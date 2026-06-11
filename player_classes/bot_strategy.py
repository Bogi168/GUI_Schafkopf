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

# Doubling the game value happens after seeing only the first half of the
# hand (4 of 8 cards) and raises the stakes for everyone, win or lose, for
# the entire hand. That is only worth the risk if those 4 cards alone are
# already as strong as a full 8-card hand most bots would be happy to play
# (see _WANT_TO_PLAY_THRESHOLD) - a rare sign that the completed hand will
# be very good for a Sauspiel.
_DOUBLE_GAME_VALUE_THRESHOLD = _WANT_TO_PLAY_THRESHOLD

# Hand strength needed to choose/overbid into a Wenz/Solo or a Tout.
_SOLO_THRESHOLD = 11.0
_TOUT_THRESHOLD = 16.0

# Accepting a Hochzeit means carrying the partner team almost alone: the
# game chooser hands over their single trump and contributes points, but no
# further trump support. That needs a hand clearly stronger than a normal
# want-to-play hand (8.0), though not full Solo strength (11.0) - the swap
# adds one trump and the chooser's card points still count for the team.
_HOCHZEIT_PARTNER_THRESHOLD = 10.0

# Holding this many of the four Unter makes Wenz attractive on its own, even
# if the rest of the hand wouldn't otherwise reach _SOLO_THRESHOLD.
_WENZ_MIN_UNTER = 3

# Wenz/WenzTout: there are only 4 Unter trumps in total.
_WENZ_TRUMP_COUNT = 4

# Sauspiel/Hochzeit/Solo (non-Tout) shooting: a strict trump majority (8+ of
# 14) is far too rare to be useful. "6 trumps including some of the higher
# Obers" is already a clear edge - e.g. the 2 highest Obers
# (2 * _OBER_STRENGTH = 6.0) plus 4 more trump-color cards
# (4 * _TRUMP_HERZ_STRENGTH = 4.0) reach this threshold.
_SHOOT_THRESHOLD_NORMAL = 10.0

# Game mode ranks (see game_classes/game_modes/*.py): higher outranks lower.
_SAUSPIEL_RANK = 2
_HOCHZEIT_RANK = 3
_WENZ_RANK = 4
_SOLO_RANK = 5
_WENZ_TOUT_RANK = 6
_SOLO_TOUT_RANK = 7

# Ramsch risk weights: how much each card contributes to the danger of
# ending up with the most points. Ober/Unter and Herz cards are trumps in
# Ramsch and tend to win tricks, with Ober the most dangerous. A "blanc" Sau
# or Ten - the only card of its color in hand - must be played whenever that
# color is led and, being the strongest non-trump card of its suit, often
# wins an unwanted trick.
_RAMSCH_OBER_RISK = 2.5
_RAMSCH_UNTER_RISK = 2.0
_RAMSCH_HERZ_TRUMP_RISK = 1.0
_RAMSCH_BLANC_SAU_RISK = 2.0
_RAMSCH_BLANC_TEN_RISK = 1.0

# A random 8-card hand carries about one Ober, one Unter and one and a half
# Herz trumps - around 6.0 risk - which is already too dangerous to want a
# Ramsch. Only a hand clearly safer than that average should volunteer, so
# the threshold sits below it.
_RAMSCH_RISK_THRESHOLD = 5.0

_NON_TRUMP_COLORS = (Color.EICHEL, Color.GRUEN, Color.SCHELLEN)


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


def wants_to_double_game_value(player_cards: list[Card]) -> bool:
    """Decides whether a bot doubles the game value after seeing the first
    half of its hand.

    Doubling raises the stakes for every player for the rest of the hand,
    so it is only worth the risk when the cards seen so far already look
    excellent on their own - strong enough to match a full hand the bot
    would normally be happy to play (see _DOUBLE_GAME_VALUE_THRESHOLD).
    """

    return hand_strength(player_cards) >= _DOUBLE_GAME_VALUE_THRESHOLD


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


def wants_to_partner_hochzeit(player_cards: list[Card]) -> bool:
    """Decides whether a bot accepts being the partner of a Hochzeit.

    The partner must hand over a non-trump card in the swap, so a hand of
    nothing but trumps cannot accept at all (mirroring the allow_yes rule
    for human players). Beyond that, the bot only accepts when its hand is
    strong enough to carry the team (see _HOCHZEIT_PARTNER_THRESHOLD).
    """

    has_card_to_give = any(
        card.card_type not in (Type.OBER, Type.UNTER)
        and card.card_color != Color.HERZ
        for card in player_cards
    )
    return (
        has_card_to_give
        and hand_strength(player_cards) >= _HOCHZEIT_PARTNER_THRESHOLD
    )


def best_hochzeit_swap_card(
    player_cards: list[Card], legal_cards: list[Card]
) -> Card:
    """Picks the card to hand over in the Hochzeit swap.

    The swap stays within the team, so no card points change sides - what
    matters is which card leaves this bot's hand. Shedding the weakest card
    of the shortest non-trump suit works towards a void that can later be
    trumped, while a Sau is kept whenever possible since it is the
    strongest card of its suit and a likely trick winner. For the game
    chooser, whose only legal card is their single trump, the choice is
    forced anyway.
    """

    def shed_priority(card: Card) -> tuple[bool, int, int]:
        suit_length = _non_trump_color_count(player_cards, card.card_color)
        return (card.card_type == Type.SAU, suit_length, card.card_type)

    return min(legal_cards, key=shed_priority)


def ramsch_risk(player_cards: list[Card]) -> float:
    """Estimates how likely a hand is to end up with the most points in a
    Ramsch.

    Trumps (Ober, Unter and Herz) raise the risk since they tend to win
    tricks, with Ober the most dangerous. A "blanc" Sau or Ten - the only
    card of its color in hand - also raises the risk, since it must be
    played whenever that color is led and, being the strongest non-trump
    card of its suit, often wins an unwanted trick.
    """

    risk = 0.0
    for card in player_cards:
        if card.card_type == Type.OBER:
            risk += _RAMSCH_OBER_RISK
        elif card.card_type == Type.UNTER:
            risk += _RAMSCH_UNTER_RISK
        elif card.card_color == Color.HERZ:
            risk += _RAMSCH_HERZ_TRUMP_RISK

    for color in _NON_TRUMP_COLORS:
        cards_of_color = [card for card in player_cards if card.card_color == color]
        if len(cards_of_color) == 1:
            blanc_type = cards_of_color[0].card_type
            if blanc_type == Type.SAU:
                risk += _RAMSCH_BLANC_SAU_RISK
            elif blanc_type == Type.TEN:
                risk += _RAMSCH_BLANC_TEN_RISK

    return risk


def wants_to_play_ramsch(player_cards: list[Card]) -> bool:
    """Decides whether a bot wants to play a Ramsch when nobody else chose
    a game.

    The bot agrees to play when its hand looks unlikely to accumulate the
    most points (see ramsch_risk); a riskier hand makes it prefer to redraw
    instead. Many trumps or blanc Saus/Tens make a Ramsch less attractive,
    but neither rules it out on its own - only a hand combining several of
    these risk factors crosses the threshold.
    """

    return ramsch_risk(player_cards) <= _RAMSCH_RISK_THRESHOLD


def trump_strength(player_cards: list[Card], trumps: list[Card]) -> float:
    """Generalizes hand_strength to any trump suit.

    ``trumps`` is the power-sorted list of all trumps in the current game
    mode (see Game.__init__): positions 0-3 are the 4 Ober, 4-7 the 4
    Unter, and the rest the trump-color cards. Weighting each held trump
    by its position mirrors hand_strength's Ober/Unter/Herz-trump weights
    for any trump color. A blanc Sau of a non-trump color still counts as
    _SAU_STRENGTH, just like in hand_strength.
    """

    score = 0.0
    for card in player_cards:
        if card in trumps:
            index = trumps.index(card)
            if index < 4:
                score += _OBER_STRENGTH
            elif index < 8:
                score += _UNTER_STRENGTH
            else:
                score += _TRUMP_HERZ_STRENGTH
        elif card.card_type == Type.SAU:
            score += _SAU_STRENGTH
    return score


def _can_guarantee_a_trick(player_cards: list[Card], trumps: list[Card]) -> bool:
    """In a Tout, decides whether the player can force a trick win no
    matter how the game chooser plays.

    The game chooser can play one trump per round. Every trump ranked
    above the player's strongest held trump can be used this way to "use
    up" a round without the player ever getting to play their strongest
    trump - so the player needs more held trumps than there are trumps
    ranked above their strongest one to guarantee winning a trick once
    those higher trumps are exhausted.
    """

    held_ranks = [rank for rank, trump in enumerate(trumps) if trump in player_cards]
    if not held_ranks:
        return False
    return len(held_ranks) > min(held_ranks)


def wants_to_shoot(
    player_cards: list[Card],
    trumps: list[Card],
    is_tout: bool = False,
    is_ramsch: bool = False,
) -> bool:
    """Decides whether a bot shoots (or shoots back), doubling the game
    value and turning its own team into the active team for the rest of
    the hand.

    Shooting is a high-risk bet: it doubles the stakes for everyone, win
    or lose. The bar for it depends on the game mode:

    - Ramsch has no active team to challenge - shooting only signals that
      this hand is safe enough that the bot would have volunteered for a
      Ramsch itself (see wants_to_play_ramsch).
    - In a Tout, the game chooser must win every trick, so a bot that can
      force at least one trick win on its own (see _can_guarantee_a_trick)
      guarantees the chooser loses and should always shoot.
    - In Wenz, a strict majority of the 4 Unter (3 or more) means no other
      player - including the chooser - can hold more, which is
      "incredibly good" on its own.
    - In Sauspiel/Hochzeit/Solo, a strict trump majority is far too rare to
      be useful; instead a hand around "6 trumps including some of the
      higher Obers" (see _SHOOT_THRESHOLD_NORMAL) is a clear enough edge.
    """

    if is_ramsch:
        return wants_to_play_ramsch(player_cards)

    if not trumps:
        return False

    if is_tout:
        return _can_guarantee_a_trick(player_cards, trumps)

    # Only Wenz/WenzTout build a trumps list this short (see Game.__init__);
    # every other mode has 14 trumps.
    if len(trumps) <= _WENZ_TRUMP_COUNT:
        trump_count = sum(1 for card in player_cards if card in trumps)
        return trump_count > len(trumps) / 2

    return trump_strength(player_cards, trumps) >= _SHOOT_THRESHOLD_NORMAL
