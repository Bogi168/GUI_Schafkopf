"""Inference of how much each player knows about team membership.

In most game modes teams are public knowledge from the start. In Sauspiel,
however, only the holder of the callsau (and, once it has been played,
everybody) knows the true teams - the game chooser and the players who turn
out to be on team 2 only know who they are *not* with until the callsau is
revealed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from card_classes.Cards import Type

if TYPE_CHECKING:
    from card_classes.Cards import Card
    from player_classes.Player import Player
    from player_classes.Team import Team


@dataclass(frozen=True)
class TeamKnowledge:
    """What ``player`` currently knows about the other players' allegiance."""

    teammates: list[Player]
    opponents: list[Player]
    unknown: list[Player]


def _call_sau_revealer(
    player: Player,
    call_sau: Card,
    trick_history: list[list[tuple[Player, Card]]],
    current_trick: list[tuple[Player, Card]],
) -> Player | None:
    """Returns the player known (to ``player``) to hold/have played
    ``call_sau``, or None if its owner hasn't been revealed yet."""

    if any(card == call_sau for card in player.player_cards):
        return player

    for trick in trick_history + [current_trick]:
        for trick_player, card in trick:
            if card == call_sau:
                return trick_player

    # Davonlaufen reveals the owner just as surely as playing the Sau:
    # Sau-Zwang forces the Sau out of the owner whenever anybody else
    # leads the called colour, so a completed trick led with a non-Sau
    # card of that colour where the Sau did not fall can only have been
    # led by the owner running away. (Only completed tricks count - in
    # the trick still being played the Sau may simply not have fallen
    # yet.)
    for trick in trick_history:
        if not trick:
            continue
        leader, lead = trick[0]
        if (
            lead.card_color == call_sau.card_color
            and lead.card_type not in (Type.OBER, Type.UNTER)
            and lead != call_sau
        ):
            return leader

    return None


def infer_team_knowledge(
    player: Player,
    players: list[Player],
    player_teams: dict[Player, Team],
    game_chooser: Player | None,
    call_sau: Card | None,
    trick_history: list[list[tuple[Player, Card]]],
    current_trick: list[tuple[Player, Card]] | None = None,
) -> TeamKnowledge:
    """Determines what ``player`` knows about teammates/opponents so far."""

    others = [p for p in players if p != player]
    own_team = player_teams[player]

    if len(own_team.players) == 1:
        # Ramsch, or the lone chooser in Wenz/Solo: nobody is a teammate.
        return TeamKnowledge(teammates=[], opponents=others, unknown=[])

    if call_sau is not None and game_chooser is not None:
        revealer = _call_sau_revealer(
            player=player,
            call_sau=call_sau,
            trick_history=trick_history,
            current_trick=current_trick or [],
        )
        if revealer is None:
            if player == game_chooser:
                return TeamKnowledge(teammates=[], opponents=[], unknown=others)
            return TeamKnowledge(
                teammates=[],
                opponents=[game_chooser],
                unknown=[p for p in others if p != game_chooser],
            )

    teammates = [p for p in others if player_teams[p] is own_team]
    opponents = [p for p in others if player_teams[p] is not own_team]
    return TeamKnowledge(teammates=teammates, opponents=opponents, unknown=[])
