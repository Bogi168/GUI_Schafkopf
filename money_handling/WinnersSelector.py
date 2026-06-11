from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player_classes.Team import Team
    from player_classes.Player import Player
    from card_classes.Cards import Card


class WinnersSelector:
    """Selects the winners of a game"""

    def __init__(self, teams: list[Team], active_team: Team | None) -> None:
        """
        :param teams: list of all the teams of a game
        :type teams: list[Team]
        :param active_team: The active team of the game
        :type active_team: Team | None
        """
        self.teams: list[Team] = teams
        self.active_team: Team | None = active_team

    def get_most_points_teams(self) -> list[Team]:
        """
        :return: A list of the teams with the most points
        :rtype: list[Team]
        """
        most_point_team_points: int = max(team.points for team in self.teams)
        most_point_teams: list[Team] = [
            team for team in self.teams if team.points == most_point_team_points
        ]
        return most_point_teams

    def get_game_winners(self) -> list[Player]:
        """
        :return: A list of the winners of the game
        :rtype: list[Player]
        """
        most_point_teams: list[Team] = self.get_most_points_teams()
        if len(most_point_teams) == 1:
            winners: list[Player] = [
                player for team in most_point_teams for player in team.players
            ]
        else:
            winners: list[Player] = [
                player
                for team in most_point_teams
                if self.active_team != team
                for player in team.players
            ]
        return winners


class RamschWinnersSelector(WinnersSelector):
    def __init__(self, teams: list[Team], active_players: list[Player]) -> None:
        super().__init__(teams=teams, active_team=None)
        self.run_through_threshold: int = 91
        self.active_players: list[Player] = active_players

    def _players_not_in(self, teams: list[Team]) -> list[Player]:
        return [
            player
            for team in self.teams
            for player in team.players
            if team not in teams
        ]

    def _players_in(self, teams: list[Team]) -> list[Player]:
        return [
            player for team in self.teams for player in team.players if team in teams
        ]

    def _durchmarsch_winners(self, most_point_teams: list[Team]) -> list[Player]:
        """The lone team with the most points "ran through" (collected at
        least run_through_threshold points), reversing the usual outcome:
        that team wins instead of losing."""

        return [most_point_teams[0].players[0]]

    def _tied_losers_winners(self, most_point_teams: list[Team]) -> list[Player]:
        """Several teams are tied for the most points and all lose - unless
        every one of them shot (became active), in which case the ones that
        didn't shoot win too."""

        winners = self._players_not_in(most_point_teams)
        losers = self._players_in(most_point_teams)
        shot_losers = [loser for loser in losers if loser in self.active_players]
        spared_losers = [loser for loser in losers if loser not in self.active_players]
        if shot_losers and spared_losers:
            winners.extend(spared_losers)
        return winners

    def get_game_winners(self) -> list[Player]:
        most_point_teams: list[Team] = self.get_most_points_teams()
        if len(most_point_teams) > 1:
            return self._tied_losers_winners(most_point_teams)
        if most_point_teams[0].points >= self.run_through_threshold:
            return self._durchmarsch_winners(most_point_teams)
        return self._players_not_in(most_point_teams)


class ToutWinnersSelector(WinnersSelector):
    def __init__(
        self,
        teams: list[Team],
        active_team: Team | None,
        game_chooser: Player,
        full_deck: list[Card],
    ) -> None:
        super().__init__(teams=teams, active_team=active_team)
        self.game_chooser = game_chooser
        self.full_deck: list[Card] = full_deck

    def get_game_winners(self) -> list[Player]:
        if len(self.game_chooser.collected_cards) == len(self.full_deck):
            return [self.game_chooser]
        else:
            return [
                player
                for team in self.teams
                for player in team.players
                if player != self.game_chooser
            ]


class WenzToutWinnersSelector(ToutWinnersSelector):
    pass


class SoloToutWinnersSelector(ToutWinnersSelector):
    pass
