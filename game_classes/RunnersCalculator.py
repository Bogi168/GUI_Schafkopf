from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from card_classes.Cards import Card
    from player_classes.Team import Team


@dataclass
class RunnersSetup:
    runners_amount: int


class RunnersCalculator:
    def __init__(self, trumps: list[Card], minimum_runners: int = 3) -> None:
        self.trumps: list[Card] = trumps
        self.minimum_runners: int = minimum_runners

    def count_team_runners(self, team: Team) -> int:
        """
        Counts the amount of runners a team has.
        :param team: The team object
        :type team: Team
        :return: The amount of runners the given team has
        :rtype: int
        """

        runners_count: int = 0
        for trump in self.trumps:
            if any(
                card == trump for player in team.players for card in player.player_cards
            ):
                runners_count += 1
            else:
                return runners_count
        return runners_count

    def count_game_runners(self, teams: list[Team]) -> RunnersSetup:
        """
        Counts the amount of runners for each team and returns the game runners count.
        :param teams: A list of all the team objects
        :type teams: list[Team]
        :return: The amount of runners the game has
        :rtype: int
        """

        for team in teams:
            runners_count: int = self.count_team_runners(team=team)
            if runners_count >= self.minimum_runners:
                return RunnersSetup(runners_amount=runners_count)
        return RunnersSetup(runners_amount=0)


class RamschRunnersCalculator(RunnersCalculator):
    def __init__(self, trumps: list[Card]) -> None:
        super().__init__(trumps=trumps, minimum_runners=0)


class WenzRunnersCalculator(RunnersCalculator):
    def __init__(self, trumps: list[Card]) -> None:
        super().__init__(trumps=trumps, minimum_runners=2)
