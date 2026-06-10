"""Heuristics used by Bot players to decide which card to play."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from card_classes.Cards import Cards, Type

if TYPE_CHECKING:
    from card_classes.Cards import Card, Color
    from card_classes.CardPowerCalculator import CardPowerCalculator
    from player_classes.Player import Player
    from player_classes.team_knowledge import TeamKnowledge


# A trick worth at least this many points is worth spending a trump on, even
# if it's not strictly necessary to win the game.
_HIGH_VALUE_THRESHOLD = 10

# Leading a Sau is only considered "safe" (unlikely that someone is already
# void in that suit) during the first two of the eight tricks.
_EARLY_GAME_TRICKS = 6

_FULL_DECK: list[Card] = Cards().full_deck


@dataclass(frozen=True)
class CardPlayContext:
    """Everything a Bot needs to know to make an informed card decision."""

    current_trick: list[tuple[Player, Card]]
    trumps: list[Card]
    card_power_calculator: CardPowerCalculator
    played_cards_history: list[Card]
    team_knowledge: TeamKnowledge
    is_ramsch: bool
    is_tout: bool
    tricks_remaining: int


def _remaining_unseen_cards(
    own_hand: list[Card],
    played_cards_history: list[Card],
    current_trick_cards: list[Card],
) -> list[Card]:
    """Cards that aren't in ``own_hand`` and haven't been played yet -
    i.e. cards that could still be in another player's hand."""

    seen = own_hand + played_cards_history + current_trick_cards
    return [card for card in _FULL_DECK if card not in seen]


def _is_highest_remaining(
    card: Card,
    unseen_cards: list[Card],
    trumps: list[Card],
    card_power_calculator: CardPowerCalculator,
) -> bool:
    """Whether no card still possibly held by another player could beat
    ``card`` if it were played."""

    card_power = card_power_calculator.get_card_power(card)

    if card in trumps:
        return not any(
            card_power_calculator.get_card_power(unseen) > card_power
            for unseen in unseen_cards
            if unseen in trumps
        )

    if any(unseen in trumps for unseen in unseen_cards):
        return False

    return not any(
        unseen.card_color == card.card_color
        and card_power_calculator.get_card_power(unseen) > card_power
        for unseen in unseen_cards
    )


def _safe_low_card(
    cards: list[Card],
    trumps: list[Card],
    card_power_calculator: CardPowerCalculator,
) -> Card:
    """The least valuable card to part with - prefers shedding non-trumps
    and, among those, the lowest-point (then lowest-power) card."""

    non_trump = [card for card in cards if card not in trumps]
    pool = non_trump or cards
    return min(
        pool,
        key=lambda card: (
            card.card_type.points,
            card_power_calculator.get_card_power(card),
        ),
    )


def _non_trump_suit_count(cards: list[Card], color: Color, trumps: list[Card]) -> int:
    return sum(1 for card in cards if card.card_color == color and card not in trumps)


def choose_card_to_play(
    player: Player, legal_cards: list[Card], context: CardPlayContext
) -> Card:
    """Picks the card a Bot should play, given everything it knows."""

    if len(legal_cards) == 1:
        return legal_cards[0]

    if not context.current_trick:
        return _choose_lead_card(player=player, legal_cards=legal_cards, context=context)

    return _choose_follow_card(player=player, legal_cards=legal_cards, context=context)


def _choose_lead_card(
    player: Player, legal_cards: list[Card], context: CardPlayContext
) -> Card:
    cpc = context.card_power_calculator
    trumps = context.trumps

    if context.is_ramsch:
        non_trump = [card for card in legal_cards if card not in trumps]
        pool = non_trump or legal_cards
        return min(
            pool, key=lambda card: (card.card_type.points, cpc.get_card_power(card))
        )

    if context.is_tout and not context.team_knowledge.teammates:
        # The Tout chooser has no margin for error: stay in control by
        # leading the strongest card available.
        return max(legal_cards, key=cpc.get_card_power)

    unseen = _remaining_unseen_cards(
        own_hand=player.player_cards,
        played_cards_history=context.played_cards_history,
        current_trick_cards=[],
    )

    trump_legal = [card for card in legal_cards if card in trumps]
    guaranteed_trumps = [
        card for card in trump_legal if _is_highest_remaining(card, unseen, trumps, cpc)
    ]
    if guaranteed_trumps:
        # Drain the opponents' trumps with a card nobody can beat.
        return max(guaranteed_trumps, key=cpc.get_card_power)

    non_trump_legal = [card for card in legal_cards if card not in trumps]
    if non_trump_legal:
        aces = [card for card in non_trump_legal if card.card_type == Type.SAU]
        if aces and context.tricks_remaining >= _EARLY_GAME_TRICKS:
            # Early on, a Sau is unlikely to be trumped and is the highest
            # card of its suit - lead the one from our shortest suit.
            return min(
                aces,
                key=lambda card: _non_trump_suit_count(
                    player.player_cards, card.card_color, trumps
                ),
            )

        suit_counts = {
            color: _non_trump_suit_count(player.player_cards, color, trumps)
            for color in {card.card_color for card in non_trump_legal}
        }
        shortest_suit = min(suit_counts, key=lambda color: suit_counts[color])
        candidates = [card for card in non_trump_legal if card.card_color == shortest_suit]
        return min(
            candidates,
            key=lambda card: (card.card_type.points, cpc.get_card_power(card)),
        )

    return min(
        legal_cards, key=lambda card: (card.card_type.points, cpc.get_card_power(card))
    )


def _choose_follow_card(
    player: Player, legal_cards: list[Card], context: CardPlayContext
) -> Card:
    cpc = context.card_power_calculator
    trumps = context.trumps
    current_trick = context.current_trick

    cards_so_far = [card for _, card in current_trick]
    players_so_far = [trick_player for trick_player, _ in current_trick]

    strongest = cpc.get_strongest_played_card(played_cards=cards_so_far, trumps=trumps)
    winner_player = players_so_far[cards_so_far.index(strongest)]
    trick_points_so_far = sum(card.card_type.points for card in cards_so_far)
    is_last_to_act = len(current_trick) == 3

    winning_cards = [
        card
        for card in legal_cards
        if cpc.get_strongest_played_card(played_cards=cards_so_far + [card], trumps=trumps)
        == card
    ]
    losing_cards = [card for card in legal_cards if card not in winning_cards]

    is_teammate_winning = winner_player in context.team_knowledge.teammates

    if context.is_tout:
        if is_last_to_act and is_teammate_winning:
            # The trick is already secured for our side either way - don't
            # waste a card that could matter in a future trick.
            return _safe_low_card(legal_cards, trumps, cpc)
        if winning_cards:
            return min(winning_cards, key=cpc.get_card_power)
        return _safe_low_card(legal_cards, trumps, cpc)

    if context.is_ramsch:
        if winning_cards:
            if losing_cards:
                return _safe_low_card(losing_cards, trumps, cpc)
            # Forced to take the trick - minimise the damage.
            return min(
                winning_cards,
                key=lambda card: (card.card_type.points, cpc.get_card_power(card)),
            )
        return _safe_low_card(legal_cards, trumps, cpc)

    if is_teammate_winning:
        if winning_cards:
            # The trick is already ours - no need to spend a strong card.
            return _safe_low_card(legal_cards, trumps, cpc)

        unseen = _remaining_unseen_cards(
            own_hand=player.player_cards,
            played_cards_history=context.played_cards_history,
            current_trick_cards=cards_so_far,
        )
        safe = _is_highest_remaining(strongest, unseen, trumps, cpc)
        if safe or is_last_to_act:
            # Schmieren: feed our teammate's winning trick as many points
            # as possible.
            return max(legal_cards, key=lambda card: card.card_type.points)
        # Too risky - an opponent could still overtake, don't feed points.
        return _safe_low_card(legal_cards, trumps, cpc)

    # The current winner is an opponent (or not yet known to be a teammate).
    if winning_cards:
        cheapest = min(winning_cards, key=cpc.get_card_power)
        worth_it = (
            trick_points_so_far >= _HIGH_VALUE_THRESHOLD
            or is_last_to_act
            or trick_points_so_far >= cheapest.card_type.points
        )
        if worth_it:
            return cheapest
        if losing_cards:
            return _safe_low_card(losing_cards, trumps, cpc)
        return cheapest

    return _safe_low_card(legal_cards, trumps, cpc)
