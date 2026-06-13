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

# Strength alone can be reached with two Obers and two Saus - only two
# trumps. Measured over thousands of simulated games, such Sauspiele are
# coin flips (2 trumps won 43%, 3 trumps 52%), while 4+ trumps won 62-94%.
# A hand with exactly one trump is exempt: it cannot play a Sauspiel at
# all, only offer a Hochzeit, where the trump count is fixed by rule.
_SAUSPIEL_MIN_TRUMPS = 4
_HOCHZEIT_CHOOSER_TRUMPS = 1

# Doubling the game value happens after seeing only the first half of the
# hand (4 of 8 cards) and amplifies this player's final outcome, win or
# lose. The threshold was tuned by a best-response sweep: one bot's
# threshold varied against three reference bots, measuring the varied bot's
# own EV in real play. A naive force-double-vs-not A/B overstates low
# thresholds because it doubles opponents at random, breaking the real
# correlation that opponents double exactly when they are strong (and you
# are about to lose) - doubling is a shared multiplier, so that correlation
# matters. The best response settles here.
_DOUBLE_GAME_VALUE_THRESHOLD = 5.0

# Solo viability, measured over thousands of simulated bot games: the
# chooser's trump count dominates the outcome (5 trumps won 24%, 6 trumps
# 54%, 7 trumps 87%). Six-trump solos are only profitable when the trump
# quality and side aces make up for the missing trump: Obers plus non-trump
# Saus of at least _SOLO_SIX_TRUMP_QUALITY.
_SOLO_MIN_TRUMPS = 7
_SOLO_SIX_TRUMP_QUALITY = 3

# Accepting a Hochzeit means carrying the partner team almost alone: the
# game chooser hands over their single trump and contributes points, but no
# further trump support. That needs a hand clearly stronger than a normal
# want-to-play hand (8.0) - the swap adds one trump and the chooser's card
# points still count for the team.
_HOCHZEIT_PARTNER_THRESHOLD = 10.0

# Wenz viability, measured the same way: Unter alone don't carry a Wenz
# (3 Unter with no Sau won 8% of the time) - the side suits have to win
# tricks too. At least _WENZ_MIN_UNTER Unter and a combined count of Unter
# and Saus of at least _WENZ_MIN_UNTER_PLUS_SAUS (3 Unter + 2 Saus won 61%,
# 4 Unter + 1 Sau 50%) marks the profitable region.
_WENZ_MIN_UNTER = 3
_WENZ_MIN_UNTER_PLUS_SAUS = 5

# Suit rankings used to check for "standing" side suits (every held card of
# a suit is part of an unbroken run from the Sau down, so each one wins its
# trick once trumps are drained). In Wenz the Ober is a regular suit card
# between König and Nine; in Solo the Ober and Unter are trumps.
_WENZ_SUIT_ORDER = (
    Type.SAU,
    Type.TEN,
    Type.KOENIG,
    Type.OBER,
    Type.NINE,
    Type.EIGHT,
    Type.SEVEN,
)
_SOLO_SUIT_ORDER = (
    Type.SAU,
    Type.TEN,
    Type.KOENIG,
    Type.NINE,
    Type.EIGHT,
    Type.SEVEN,
)

# The three highest Ober (trump tops a Solo Tout must own).
_TOP_OBER_COLORS = (Color.EICHEL, Color.GRUEN, Color.HERZ)

# Wenz/WenzTout: there are only 4 Unter trumps in total.
_WENZ_TRUMP_COUNT = 4

# Sauspiel/Hochzeit/Solo (non-Tout) shooting. Shooting doubles the stake and
# flips the active team, so like doubling it must be tuned by a best-response
# sweep, not a 50/50 A/B (which overstates aggression by shooting opponents
# at random instead of when they are strong). The sweep - one bot's shoot
# threshold varied against three reference bots, measuring its own EV - rises
# steeply to a flat plateau from ~11 upward (+2.2 cents at 11, vs +1.3 at 10
# and -1.3 at 9): shooting only pays on a genuinely dominant trump holding,
# e.g. 2 Obers plus 5 trump-color cards, or 3 Obers plus 2 more trumps.
_SHOOT_THRESHOLD_NORMAL = 11.0

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

# Simulated Ramsch outcomes (forcing every Ramsch offer to be accepted,
# bucketed by the player's own ramsch_risk) stay clearly profitable up to
# about risk 6.7 (+44 cents at risk 5-6, +14 at 6-7) and only fall off a
# cliff beyond it (-42 at 7-8). Since declining merely redeals for a fresh,
# break-even hand, accepting pays whenever the risk is below that crossover.
# The same "is my hand safe enough" judgement drives Ramsch shooting.
_RAMSCH_RISK_THRESHOLD = 6.5

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


def _sau_count(player_cards: list[Card]) -> int:
    return sum(1 for card in player_cards if card.card_type == Type.SAU)


def _solo_trump_count(player_cards: list[Card], trump_color: Color) -> int:
    return sum(
        1
        for card in player_cards
        if card.card_type in (Type.OBER, Type.UNTER)
        or card.card_color == trump_color
    )


def _best_solo_color(player_cards: list[Card]) -> Color:
    return best_trump_color(
        player_cards=player_cards,
        options={str(i): color for i, color in enumerate(Color, start=1)},
    )


def is_solo_worthy(player_cards: list[Card], trump_color: Color) -> bool:
    """Whether the hand is strong enough to profitably choose a Solo in
    ``trump_color`` (see _SOLO_MIN_TRUMPS / _SOLO_SIX_TRUMP_QUALITY)."""

    trump_count = _solo_trump_count(player_cards, trump_color)
    if trump_count >= _SOLO_MIN_TRUMPS:
        return True
    if trump_count != _SOLO_MIN_TRUMPS - 1:
        return False

    obers = sum(1 for card in player_cards if card.card_type == Type.OBER)
    side_saus = sum(
        1
        for card in player_cards
        if card.card_type == Type.SAU and card.card_color != trump_color
    )
    return obers + side_saus >= _SOLO_SIX_TRUMP_QUALITY


def is_wenz_worthy(player_cards: list[Card]) -> bool:
    """Whether the hand is strong enough to profitably choose a Wenz (see
    _WENZ_MIN_UNTER / _WENZ_MIN_UNTER_PLUS_SAUS)."""

    unters = _unter_count(player_cards)
    return (
        unters >= _WENZ_MIN_UNTER
        and unters + _sau_count(player_cards) >= _WENZ_MIN_UNTER_PLUS_SAUS
    )


def _suits_are_standing(
    player_cards: list[Card],
    trump_types: tuple[Type, ...],
    trump_color: Color | None,
    suit_order: tuple[Type, ...],
) -> bool:
    """Whether every non-trump suit the hand holds is an unbroken run from
    the Sau down (``suit_order``), so each card wins its trick once the
    trumps are drained."""

    for color in Color:
        if color == trump_color:
            continue
        held = sorted(
            (
                card.card_type
                for card in player_cards
                if card.card_color == color and card.card_type not in trump_types
            ),
            key=suit_order.index,
        )
        if held != list(suit_order[: len(held)]):
            return False
    return True


def is_wenz_tout_worthy(player_cards: list[Card]) -> bool:
    """Whether the hand all but wins a Wenz Tout outright.

    Holding all four Unter - or the three highest, so the outstanding
    Schellen Unter can never beat one of ours and falls under our first
    Unter lead (Trumpfzwang) - drains every trump while keeping the lead.
    If on top of that every side suit is standing, the only way to lose a
    trick is an early ruff by the lone low Unter before we get to lead.
    """

    unters = [card for card in player_cards if card.card_type == Type.UNTER]
    if len(unters) < _WENZ_MIN_UNTER:
        return False
    if len(unters) == _WENZ_MIN_UNTER and Color.SCHELLEN in {
        unter.card_color for unter in unters
    }:
        # Missing one of the three high Unter: it could overtrump us.
        return False
    return _suits_are_standing(
        player_cards,
        trump_types=(Type.UNTER,),
        trump_color=None,
        suit_order=_WENZ_SUIT_ORDER,
    )


def is_solo_tout_worthy(player_cards: list[Card], trump_color: Color) -> bool:
    """Whether the hand is near-certain to win a Solo Tout in
    ``trump_color``: at least _SOLO_MIN_TRUMPS trumps including the three
    highest Ober, and nothing but standing cards outside the trump suit."""

    if _solo_trump_count(player_cards, trump_color) < _SOLO_MIN_TRUMPS:
        return False
    for ober_color in _TOP_OBER_COLORS:
        if not any(
            card.card_type == Type.OBER and card.card_color == ober_color
            for card in player_cards
        ):
            return False
    return _suits_are_standing(
        player_cards,
        trump_types=(Type.OBER, Type.UNTER),
        trump_color=trump_color,
        suit_order=_SOLO_SUIT_ORDER,
    )


def wants_to_play(
    player_cards: list[Card],
    players_who_want_to_play_count: int,
    baseline_mode_playable: bool = True,
) -> bool:
    """Decides whether a bot wants to enter the game-choosing process.

    A hand worth a Wenz/Solo (or a Tout) is always worth offering: such a
    mode either still outranks whatever the earlier choosers landed on, or
    this bot can simply pass once it's its turn (see
    choose_preferred_game_mode). A hand that is at best Sauspiel/Hochzeit
    material is only worth offering if this bot is the first chooser - any
    later chooser whose preferred mode is still Sauspiel would be forced to
    overbid into an unsuited Wenz/Solo instead - and only if one of those
    baseline modes is actually legal for this hand
    (``baseline_mode_playable``): the first volunteer can never pass, so a
    hand with no callable sau and the wrong trump count for Hochzeit would
    likewise end up forced into an unsuited Wenz/Solo.
    """

    best_color = _best_solo_color(player_cards)
    if (
        is_wenz_worthy(player_cards)
        or is_solo_worthy(player_cards, best_color)
        or is_wenz_tout_worthy(player_cards)
        or is_solo_tout_worthy(player_cards, best_color)
    ):
        return True

    if players_who_want_to_play_count > 0:
        return False

    trumps = _solo_trump_count(player_cards, Color.HERZ)
    return (
        baseline_mode_playable
        and hand_strength(player_cards) >= _WANT_TO_PLAY_THRESHOLD
        and (
            trumps >= _SAUSPIEL_MIN_TRUMPS
            or trumps == _HOCHZEIT_CHOOSER_TRUMPS
        )
    )


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
    """Picks the legal game mode that best matches the hand.

    Hochzeit and Sauspiel are the baseline. A hand passing is_wenz_worthy /
    is_solo_worthy is steered towards that alone game, and a hand passing
    the much stricter Tout checks goes for the matching Tout first. If none
    of the preferred modes are among the legal ``options`` (e.g. because
    they don't outrank a previous offer), the bot passes if allowed,
    otherwise falls back to the lowest-ranked legal mode.
    """

    candidates_by_rank = {mode.rank: mode for mode in options.values()}
    if not candidates_by_rank:
        return None

    best_color = _best_solo_color(player_cards)
    wenz_favored = _unter_count(player_cards) >= _WENZ_MIN_UNTER

    if wenz_favored:
        family_rank, family_tout_rank = _WENZ_RANK, _WENZ_TOUT_RANK
        other_rank, other_tout_rank = _SOLO_RANK, _SOLO_TOUT_RANK
    else:
        family_rank, family_tout_rank = _SOLO_RANK, _SOLO_TOUT_RANK
        other_rank, other_tout_rank = _WENZ_RANK, _WENZ_TOUT_RANK

    preference_order: list[int] = []
    if is_wenz_tout_worthy(player_cards):
        # A guaranteed Wenz Tout beats the merely near-certain Solo Tout.
        preference_order.append(_WENZ_TOUT_RANK)
    if is_solo_tout_worthy(player_cards, best_color):
        preference_order.append(_SOLO_TOUT_RANK)
    # Solo wins more often than Wenz at their respective viability
    # boundaries (87% with 7 trumps vs 61% with 3 Unter + 2 Saus), so it
    # comes first when the hand supports both.
    if is_solo_worthy(player_cards, best_color):
        preference_order.append(_SOLO_RANK)
    if is_wenz_worthy(player_cards):
        preference_order.append(_WENZ_RANK)
    preference_order += [_HOCHZEIT_RANK, _SAUSPIEL_RANK]

    for rank in preference_order:
        mode = candidates_by_rank.get(rank)
        if mode is not None:
            return mode

    if can_pass:
        return None

    # Forced to overbid with a hand that wanted none of the legal modes:
    # pick the least-bad option. Wenz and Solo cost the same to lose
    # (alone_price), so prefer whichever family fits the hand - a Solo in
    # the bot's best color unless the hand is Unter-heavy - over blindly
    # taking the lowest rank (which would always be Wenz).
    for rank in (family_rank, other_rank, family_tout_rank, other_tout_rank):
        mode = candidates_by_rank.get(rank)
        if mode is not None:
            return mode
    return min(candidates_by_rank.values(), key=lambda mode: mode.rank)


def _non_trump_color_count(player_cards: list[Card], color: Color) -> int:
    return sum(
        1
        for card in player_cards
        if card.card_color == color and card.card_type not in (Type.OBER, Type.UNTER)
    )


def best_trump_color(player_cards: list[Card], options: dict[str, Color]) -> Color:
    """Picks the color the bot holds the most non-Ober/Unter cards of,
    maximising the bot's own trump count for a Solo. Equally long colors
    are split by the points held in them: a Sau or Ten of the trump color
    becomes a near-unbeatable trump, while small cards add little."""

    def trump_color_value(color: Color) -> tuple[int, int]:
        held = [
            card
            for card in player_cards
            if card.card_color == color
            and card.card_type not in (Type.OBER, Type.UNTER)
        ]
        return (len(held), sum(card.card_type.points for card in held))

    return max(options.values(), key=trump_color_value)


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
