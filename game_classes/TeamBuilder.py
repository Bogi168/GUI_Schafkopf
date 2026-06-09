from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from dataclasses import dataclass

from player_classes.Team import Team

if TYPE_CHECKING:
    from player_classes.Player import Player
    from card_classes.Cards import Card


@dataclass
class TeamSetup:
    player_teams: dict[Player, Team]
    teams: list[Team]
    active_team: Team | None = None


class TeamBuilder(ABC):
    def __init__(self, players: list[Player]) -> None:
        self.players: list[Player] = players

    @abstractmethod
    def create_teams(self) -> TeamSetup:
        """Creates the team objects and adds them to the teams list."""
        pass


class RamschTeamBuilder(TeamBuilder):
    def create_teams(self) -> TeamSetup:
        player_teams: dict[Player, Team] = dict()
        teams: list[Team] = []
        for index in range(len(self.players)):
            team: Team = Team(team_name=f"Team {index + 1}")
            team.players.append(self.players[index])
            player_teams[self.players[index]] = team
            teams.append(team)
        return TeamSetup(player_teams=player_teams, teams=teams)


class HochzeitTeamBuilder(TeamBuilder):
    def __init__(
        self, players: list[Player], game_chooser: Player, partner: Player
    ) -> None:
        super().__init__(players=players)
        self.game_chooser: Player = game_chooser
        self.partner = partner

    def create_teams(self) -> TeamSetup:
        player_teams: dict[Player, Team] = dict()
        teams: list[Team] = []
        team_1 = Team(team_name="Team 1")
        team_1.players.append(self.game_chooser)
        team_1.players.append(self.partner)
        active_team = team_1
        team_2 = Team(team_name="Team 2")
        team_2.players = [
            player for player in self.players if player not in team_1.players
        ]
        for player in team_1.players:
            player_teams[player] = team_1
        for player in team_2.players:
            player_teams[player] = team_2
        teams.append(team_1)
        teams.append(team_2)
        return TeamSetup(
            player_teams=player_teams, active_team=active_team, teams=teams
        )


class SauspielTeamBuilder(TeamBuilder):
    def __init__(
        self, players: list[Player], game_chooser: Player, call_sau: Card
    ) -> None:
        super().__init__(players=players)
        self.game_chooser: Player = game_chooser
        self.call_sau: Card = call_sau

    def create_teams(self) -> TeamSetup:
        player_teams: dict[Player, Team] = dict()
        teams: list[Team] = []
        team_1 = Team(team_name="Team 1")
        team_1.players.append(self.game_chooser)
        for player in self.players:
            if any(card == self.call_sau for card in player.player_cards):
                team_1.players.append(player)
                break
        assert len(team_1.players) == 2
        active_team = team_1
        team_2 = Team(team_name="Team 2")
        team_2.players = [
            player for player in self.players if player not in team_1.players
        ]
        for player in team_1.players:
            player_teams[player] = team_1
        for player in team_2.players:
            player_teams[player] = team_2
        teams.append(team_1)
        teams.append(team_2)
        return TeamSetup(
            player_teams=player_teams, active_team=active_team, teams=teams
        )


class AloneTeamBuilder(TeamBuilder):
    def __init__(self, players: list[Player], game_chooser: Player) -> None:
        super().__init__(players=players)
        self.game_chooser: Player = game_chooser

    def create_teams(self) -> TeamSetup:
        player_teams: dict[Player, Team] = dict()
        teams: list[Team] = []
        team_1 = Team(team_name="Team 1")
        team_1.players.append(self.game_chooser)
        active_team = team_1
        team_2 = Team(team_name="Team 2")
        team_2.players = [
            player for player in self.players if player not in team_1.players
        ]
        for player in team_1.players:
            player_teams[player] = team_1
        for player in team_2.players:
            player_teams[player] = team_2
        teams.append(team_1)
        teams.append(team_2)
        return TeamSetup(
            player_teams=player_teams, active_team=active_team, teams=teams
        )


class WenzTeamBuilder(AloneTeamBuilder):
    pass


class SoloTeamBuilder(AloneTeamBuilder):
    pass
