"""Heuristics used by Bot players to make game-choosing decisions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from card_classes.Cards import Color, Type

if TYPE_CHECKING:
    from card_classes.Cards import Card
    from game_classes.Game import Game


# Approximate strength contributions of card types for a "normal" game
# (Ober/Unter + Herz trump). An average 8-card hand scores ~7-8 points.
_OBER_STRENGTH = 3.0
_UNTER_STRENGTH = 2.0
_TRUMP_HERZ_STRENGTH = 1.0
_SAU_STRENGTH = 1.5

# Minimum hand strength to volunteer with a hand that is at best
# Sauspiel/Hochzeit material (see wants_to_play).
_WANT_TO_PLAY_THRESHOLD = 8.0

# Hand strength needed to choose/overbid into a Wenz/Solo or a Tout.
_SOLO_THRESHOLD = 11.0
_TOUT_THRESHOLD = 16.0

# Holding this many of the four Unter makes Wenz attractive on its own, even
# if the rest of the hand wouldn't otherwise reach _SOLO_THRESHOLD.
_WENZ_MIN_UNTER = 3

# Game mode ranks (see game_classes/game_modes/*.py): higher outranks lower.
_SAUSPIEL_RANK = 2
_HOCHZEIT_RANK = 3
_WENZ_RANK = 4
_SOLO_RANK = 5
_WENZ_TOUT_RANK = 6
_SOLO_TOUT_RANK = 7


def _unter_count(player_cards: list[Card]) -> int:
    return sum(1 for card in player_cards if card.card_type == Type.UNTER)


def hand_strength(player_cards: list[Card]) -> float:
    """A rough measure of how strong a hand is for a 'normal' trump suit
    (Ober + Unter + Herz), used to decide whether a bot wants to play."""

    score = 0.0
    for card in player_cards:
        if card.card_type == Type.OBER:
            score += _OBER_STRENGTH
        elif card.card_type == Type.UNTER:
            score += _UNTER_STRENGTH
        elif card.card_color == Color.HERZ:
            score += _TRUMP_HERZ_STRENGTH
        elif card.card_type == Type.SAU:
            score += _SAU_STRENGTH
    return score


def wants_to_play(player_cards: list[Card], players_who_want_to_play_count: int) -> bool:
    """Decides whether a bot wants to enter the game-choosing process.

    A hand strong enough for Wenz/Solo (or better) is always worth offering:
    such a mode either still outranks whatever the earlier choosers landed
    on, or this bot can simply pass once it's its turn (see
    choose_preferred_game_mode). A hand that is at best Sauspiel/Hochzeit
    material is only worth offering if this bot is the first chooser - any
    later chooser whose preferred mode is still Sauspiel would be forced to
    overbid into an unsuited Wenz/Solo instead.
    """

    strength = hand_strength(player_cards)
    if strength >= _SOLO_THRESHOLD or _unter_count(player_cards) >= _WENZ_MIN_UNTER:
        return True

    if players_who_want_to_play_count > 0:
        return False

    return strength >= _WANT_TO_PLAY_THRESHOLD


def choose_preferred_game_mode(
    player_cards: list[Card],
    options: dict[str, type[Game]],
    can_pass: bool,
) -> type[Game] | None:
    """Picks the legal game mode that best matches the hand's strength.

    Hochzeit and Sauspiel are the baseline. A hand strong enough for
    _SOLO_THRESHOLD (or holding at least _WENZ_MIN_UNTER Unter) is steered
    towards Wenz or Solo, whichever fits the hand better, and a hand strong
    enough for _TOUT_THRESHOLD goes for the matching Tout. If none of the
    preferred modes are among the legal ``options`` (e.g. because they don't
    outrank a previous offer), the bot passes if allowed, otherwise falls
    back to the lowest-ranked legal mode.
    """

    candidates_by_rank = {mode.rank: mode for mode in options.values()}
    if not candidates_by_rank:
        return None

    strength = hand_strength(player_cards)
    wenz_favored = _unter_count(player_cards) >= _WENZ_MIN_UNTER

    if wenz_favored:
        family_rank, family_tout_rank = _WENZ_RANK, _WENZ_TOUT_RANK
        other_rank, other_tout_rank = _SOLO_RANK, _SOLO_TOUT_RANK
    else:
        family_rank, family_tout_rank = _SOLO_RANK, _SOLO_TOUT_RANK
        other_rank, other_tout_rank = _WENZ_RANK, _WENZ_TOUT_RANK

    if strength >= _TOUT_THRESHOLD:
        preference_order = [
            family_tout_rank,
            other_tout_rank,
            family_rank,
            other_rank,
            _HOCHZEIT_RANK,
            _SAUSPIEL_RANK,
        ]
    elif strength >= _SOLO_THRESHOLD or wenz_favored:
        preference_order = [family_rank, other_rank, _HOCHZEIT_RANK, _SAUSPIEL_RANK]
    else:
        preference_order = [_HOCHZEIT_RANK, _SAUSPIEL_RANK]

    for rank in preference_order:
        mode = candidates_by_rank.get(rank)
        if mode is not None:
            return mode

    if can_pass:
        return None
    return min(candidates_by_rank.values(), key=lambda mode: mode.rank)


def _non_trump_color_count(player_cards: list[Card], color: Color) -> int:
    return sum(
        1
        for card in player_cards
        if card.card_color == color and card.card_type not in (Type.OBER, Type.UNTER)
    )


def best_trump_color(player_cards: list[Card], options: dict[str, Color]) -> Color:
    """Picks the color the bot holds the most non-Ober/Unter cards of,
    maximising the bot's own trump count for a Solo."""

    return max(
        options.values(), key=lambda color: _non_trump_color_count(player_cards, color)
    )


def best_sau_color(player_cards: list[Card], options: dict[str, Color]) -> Color:
    """Picks the shortest suit to call, so the bot is unlikely to have to
    lead it before the callsau owner reveals themselves."""

    return min(
        options.values(), key=lambda color: _non_trump_color_count(player_cards, color)
    )
