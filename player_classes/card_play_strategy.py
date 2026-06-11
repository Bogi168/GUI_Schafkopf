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
    is_active_team: bool
    is_solo_mode: bool
    call_sau: Card | None
    tricks_remaining: int
    trick_history: list[list[tuple[Player, Card]]]


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


def _avoid_call_sau_leads(
    cards: list[Card], call_sau: Card, player: Player, is_active_team: bool
) -> list[Card]:
    """Cards that don't risk exposing the call sau to a Sau-Zwang.

    The call sau holder should never volunteer the Sau itself as a lead,
    and the chooser shouldn't lead the called colour at all - either would
    force the Sau into play and let the opposing team trump it away if
    they're void.
    """

    if call_sau in player.player_cards:
        return [card for card in cards if card != call_sau]
    if is_active_team:
        return [card for card in cards if card.card_color != call_sau.card_color]
    return cards


def _call_sau_safe_to_reveal(player: Player, context: CardPlayContext) -> bool:
    """Whether the team that owns the call sau no longer needs to avoid
    leading/seeking it.

    Avoiding the call sau is mainly an early-game precaution against a
    Sau-Zwang trump-stab. It stops mattering once either:

    - the player has no trumps left themselves (so they can't be forced
      into a Sau-Zwang on a later trick anyway), or
    - the known opponents have already proven (by following a trump lead
      with non-trump cards - Trumpfzwang) that they're void of trumps and
      so can't trump the Sau away.
    """

    trumps = context.trumps
    if not any(card in trumps for card in player.player_cards):
        return True

    opponents = context.team_knowledge.opponents
    if not opponents:
        return False

    void_of_trumps: set[Player] = set()
    for trick in context.trick_history:
        if not trick or trick[0][1] not in trumps:
            continue
        for trick_player, card in trick[1:]:
            if card not in trumps:
                void_of_trumps.add(trick_player)

    return all(opponent in void_of_trumps for opponent in opponents)


def _call_sau_owner_forced_this_trick(context: CardPlayContext, lead_card: Card) -> bool:
    """Whether Sau-Zwang guarantees the call sau's holder must still play it
    on this trick - someone other than the holder led the called colour."""

    call_sau = context.call_sau
    if call_sau is None or call_sau in context.played_cards_history:
        return False

    return lead_card.card_color == call_sau.card_color and lead_card != call_sau


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

    call_sau = context.call_sau
    call_sau_in_play = (
        call_sau is not None and call_sau not in context.played_cards_history
    )
    if call_sau_in_play:
        if call_sau in player.player_cards:
            if (
                context.tricks_remaining >= _EARLY_GAME_TRICKS
                and _non_trump_suit_count(player.player_cards, call_sau.card_color, trumps)
                >= 4
            ):
                # Davonlaufen: our suit in the called colour is long enough
                # that we can lead a non-Sau card of it without giving the
                # Sau itself away - keep it hidden until it's safer to play.
                run_away_candidates = [
                    card
                    for card in legal_cards
                    if card.card_color == call_sau.card_color
                    and card not in trumps
                    and card != call_sau
                ]
                if run_away_candidates:
                    return min(
                        run_away_candidates,
                        key=lambda card: (card.card_type.points, cpc.get_card_power(card)),
                    )
        elif not context.is_active_team:
            # Seeking: lead a low card of the called colour, hoping our
            # still-unknown partner is void and can trump the Sau away.
            seek_candidates = [
                card
                for card in legal_cards
                if card.card_color == call_sau.card_color and card not in trumps
            ]
            if seek_candidates:
                return min(
                    seek_candidates,
                    key=lambda card: (card.card_type.points, cpc.get_card_power(card)),
                )

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

    if context.is_solo_mode:
        # In Wenz/Solo/WenzTout/SoloTout the chooser plays alone against the
        # other three. Whoever holds the trump majority is decided by who
        # chose the game, not by `is_active_team` - that can flip to the
        # three-player side after a successful shoot, but the cards
        # themselves don't move.
        should_pull_trumps = not context.team_knowledge.teammates
    else:
        should_pull_trumps = context.is_active_team

    if (
        should_pull_trumps
        and trump_legal
        and context.tricks_remaining >= _EARLY_GAME_TRICKS
    ):
        # As the side likely holding the trump majority, lead trumps early
        # ("Trumpf ziehen") to draw out the opponents' trumps while we're
        # still strong. Later in the game the other rules below take over.
        return max(trump_legal, key=cpc.get_card_power)

    non_trump_legal = [card for card in legal_cards if card not in trumps]
    if call_sau_in_play and not _call_sau_safe_to_reveal(player, context):
        filtered = _avoid_call_sau_leads(
            non_trump_legal, call_sau, player, context.is_active_team
        )
        if filtered:
            non_trump_legal = filtered

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

    if _call_sau_owner_forced_this_trick(context, current_trick[0][1]):
        call_sau = context.call_sau
        has_called_suit = any(
            card.card_color == call_sau.card_color and card not in trumps
            for card in player.player_cards
        )
        trump_winners = [card for card in winning_cards if card in trumps]
        if not has_called_suit and trump_winners:
            # The call sau's holder is forced to play it into this trick
            # (Sau-Zwang) - we can't follow suit, so trump in now to claim
            # those 11 points even though we can't be sure of overtaking
            # whoever else still has to act.
            return min(trump_winners, key=cpc.get_card_power)

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
            if strongest not in trumps:
                sau_of_suit = next(
                    (
                        card
                        for card in winning_cards
                        if card.card_color == strongest.card_color
                        and card.card_type == Type.SAU
                    ),
                    None,
                )
                if sau_of_suit is not None:
                    # Our teammate's non-trump card is winning, but a later
                    # opponent could still overtake it with a higher card of
                    # the same suit. Playing the Sau both secures the trick
                    # and adds the most possible points for the team.
                    return sau_of_suit
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
            # as possible - but Ober/Unter are too valuable as trumps to
            # give away just for their modest point value.
            schmier_candidates = [
                card for card in legal_cards if card.card_type not in cpc.trump_types
            ]
            if schmier_candidates:
                return max(schmier_candidates, key=lambda card: card.card_type.points)
            return _safe_low_card(legal_cards, trumps, cpc)
        # Too risky - an opponent could still overtake, don't feed points.
        return _safe_low_card(legal_cards, trumps, cpc)

    # The current winner is an opponent (or not yet known to be a teammate).
    if winning_cards:
        cheapest = min(winning_cards, key=cpc.get_card_power)
        worth_it = (
            trick_points_so_far >= _HIGH_VALUE_THRESHOLD
            or (is_last_to_act and trick_points_so_far > 0)
            or trick_points_so_far >= cheapest.card_type.points
        )
        if worth_it:
            return cheapest
        if losing_cards:
            return _safe_low_card(losing_cards, trumps, cpc)
        return cheapest

    return _safe_low_card(legal_cards, trumps, cpc)
