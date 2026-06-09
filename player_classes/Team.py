from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from player_classes.Player import Player


@dataclass
class Team:
    """
    An object with a team name and a list of players,
    which dynamically calculates the total points of the team
    :param team_name: The name of the team
    :type team_name: str
    :param players: The list of players
    :type players: list[Player]
    """

    team_name: str
    players: list[Player] = field(default_factory=list)

    @property
    def points(self) -> int:
        """returns the total points of the team"""
        return sum(player.points for player in self.players)
