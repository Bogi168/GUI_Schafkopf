from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player_classes.Team import Team
    from player_classes.Player import Player


class GameValueCalculator(ABC):
    """An object that distributes money across multiple players."""

    def __init__(
        self,
        base_price: int,
        call_price: int,
        alone_price: int,
        player_teams: dict[Player, Team],
        active_team: Team | None,
        winners: list[Player],
        amount_game_value_doubles: int,
        runners_amount: int,
        amount_game_card_points: int,
    ) -> None:
        """
        :param base_price: base price for game value calculations
        :type base_price: int
        :param call_price: call price for game value calculations
        :type call_price: int
        :param alone_price: alone price for game value calculations
        :type alone_price: int
        :param player_teams: A dictionary which contains the players and their teams
        :type player_teams: dict[Player, Team]
        :param active_team: The active team of the game
        :type active_team: Team | None
        :param winners: The winners of the game
        :type winners: list[Player]
        :param amount_game_value_doubles: The amount of times someone decided to double the game value
        :type amount_game_value_doubles: int
        :param runners_amount: The amount of game runners
        :type runners_amount: int
        :param amount_game_card_points: The amount of points when combining all card points of a game
        :type amount_game_card_points: int
        """

        self.base_price: int = base_price
        self.call_price: int = call_price
        self.alone_price: int = alone_price
        self.player_teams: dict[Player, Team] = player_teams
        self.players: list[Player] = [player for player in player_teams.keys()]
        self.active_team: Team | None = active_team
        self.winners: list[Player] = winners
        self.amount_game_value_doubles: int = amount_game_value_doubles
        self.runners_amount: int = runners_amount
        self.schneider_threshold: int = amount_game_card_points - (
            amount_game_card_points // 4
        )  # If total amount of points is 120, then schneider threshold is at 90 (75%)
        self.black_threshold: int = amount_game_card_points

    def is_schneider(self) -> bool:
        winning_team = self.player_teams[self.winners[0]]
        return winning_team.points > self.schneider_threshold or (
            winning_team.points == self.schneider_threshold
            and self.active_team != winning_team
        )

    def is_black(self) -> bool:
        winning_team = self.player_teams[self.winners[0]]
        return winning_team.points == self.black_threshold

    def _add_runners(self, game_value: int) -> int:
        return game_value + self.runners_amount * self.base_price

    def _apply_doubles(self, game_value: int) -> int:
        for _ in range(self.amount_game_value_doubles):
            game_value *= 2
        return game_value

    def _runners_breakdown_lines(self) -> list[str]:
        if not self.runners_amount:
            return []
        return [f"{"Runners:":<11} + {self.runners_amount * self.base_price} cents"]

    def _doubles_breakdown_lines(self) -> list[str]:
        if not self.amount_game_value_doubles:
            return []
        return [f"{"Doubles:":<11} * {2 ** self.amount_game_value_doubles}"]

    def _basic_game_value_adds_breakdown(self) -> list[str]:
        """The schneider/black/runners/doubles lines added by
        basic_game_value_adds, shared by every game_value_breakdown that
        uses it."""

        lines: list[str] = []
        if self.is_schneider():
            lines.append(f"{"Schneider:":<11} + {self.base_price} cents")
        if self.is_black():
            lines.append(f"{"Black:":<11} + {self.base_price} cents")
        lines.extend(self._runners_breakdown_lines())
        lines.extend(self._doubles_breakdown_lines())
        return lines

    def basic_game_value_adds(self, game_value: int) -> int:
        """
        Adds runners, schneider and black values to the given game value if needed
        and doubles game value for the amount of times it got doubled by players.
        :param game_value: The previous game value
        :type game_value: int
        :return: The updated game value
        :rtype: int
        """

        game_value = self._add_runners(game_value)

        if self.is_schneider():
            game_value += self.base_price

        if self.is_black():
            game_value += self.base_price

        return self._apply_doubles(game_value)

    @abstractmethod
    def calculate_game_value(self) -> int:
        """
        calculates the game value for the whole game
        :return: The game value
        :rtype: int
        """
        pass

    @abstractmethod
    def game_value_breakdown(self) -> str:
        """Returns a human-readable breakdown of the game value calculation."""

        pass


class RamschGameValueCalculator(GameValueCalculator):

    def __init__(
        self,
        alone_price: int,
        player_teams: dict[Player, Team],
        amount_game_value_doubles: int,
        winners: list[Player],
        amount_game_card_points: int,
    ) -> None:
        super().__init__(
            base_price=0,
            call_price=0,
            alone_price=alone_price,
            player_teams=player_teams,
            active_team=None,
            amount_game_value_doubles=amount_game_value_doubles,
            winners=winners,
            runners_amount=0,
            amount_game_card_points=amount_game_card_points,
        )

    def count_virgins(self) -> int:
        """
        :return: The amount of players who didn't collect any cards during the game
        :rtype: int
        """

        virgins_count = 0
        for player in self.players:
            if not player.collected_cards:
                virgins_count += 1
        return virgins_count

    def calculate_game_value(self) -> int:
        game_value = self.alone_price

        for _ in range(self.count_virgins()):
            game_value *= 2

        for _ in range(self.amount_game_value_doubles):
            game_value *= 2
        return game_value

    def game_value_breakdown(self) -> str:
        lines: list[str] = [f"\n{"Alone price:":<11} {self.alone_price} cents"]
        if self.amount_game_value_doubles:
            lines.append(f"{"Doubles:":<11} * {2 ** self.amount_game_value_doubles}")
        virgins_amount: int = self.count_virgins()
        if virgins_amount:
            lines.append(f"{"Virgins:":<11} * {2 ** virgins_amount}")
        return "\n".join(lines)


class SauspielGameValueCalculator(GameValueCalculator):

    def __init__(
        self,
        base_price: int,
        call_price: int,
        player_teams: dict[Player, Team],
        amount_game_value_doubles: int,
        active_team: Team,
        winners: list[Player],
        runners_amount: int,
        amount_game_card_points: int,
    ) -> None:
        super().__init__(
            base_price=base_price,
            call_price=call_price,
            alone_price=0,
            player_teams=player_teams,
            amount_game_value_doubles=amount_game_value_doubles,
            active_team=active_team,
            winners=winners,
            runners_amount=runners_amount,
            amount_game_card_points=amount_game_card_points,
        )

    def calculate_game_value(self) -> int:
        game_value: int = 0
        game_value += self.call_price
        game_value: int = self.basic_game_value_adds(game_value=game_value)
        return game_value

    def game_value_breakdown(self) -> str:
        lines: list[str] = [f"\n{"Call price:":<11} {self.call_price} cents"]
        lines.extend(self._basic_game_value_adds_breakdown())
        return "\n".join(lines)


class AloneGameValueCalculator(GameValueCalculator):
    def __init__(
        self,
        base_price: int,
        alone_price: int,
        player_teams: dict[Player, Team],
        amount_game_value_doubles: int,
        active_team: Team,
        winners: list[Player],
        runners_amount: int,
        amount_game_card_points: int,
    ) -> None:
        super().__init__(
            base_price=base_price,
            call_price=0,
            alone_price=alone_price,
            player_teams=player_teams,
            active_team=active_team,
            amount_game_value_doubles=amount_game_value_doubles,
            winners=winners,
            runners_amount=runners_amount,
            amount_game_card_points=amount_game_card_points,
        )

    def calculate_game_value(self) -> int:
        game_value = 0
        game_value += self.alone_price
        game_value = self.basic_game_value_adds(game_value=game_value)
        return game_value

    def game_value_breakdown(self) -> str:
        lines: list[str] = [f"\n{"Alone price:":<11} {self.alone_price} cents"]
        lines.extend(self._basic_game_value_adds_breakdown())
        return "\n".join(lines)


class HochzeitGameValueCalculator(AloneGameValueCalculator):
    pass


class WenzGameValueCalculator(AloneGameValueCalculator):
    pass


class SoloGameValueCalculator(AloneGameValueCalculator):
    pass


class ToutGameValueCalculator(AloneGameValueCalculator):
    def __init__(
        self,
        base_price: int,
        alone_price: int,
        player_teams: dict[Player, Team],
        amount_game_value_doubles: int,
        active_team: Team,
        winners: list[Player],
        runners_amount: int,
        amount_game_card_points: int,
    ) -> None:
        super().__init__(
            base_price=base_price,
            alone_price=alone_price,
            player_teams=player_teams,
            amount_game_value_doubles=amount_game_value_doubles,
            active_team=active_team,
            winners=winners,
            runners_amount=runners_amount,
            amount_game_card_points=amount_game_card_points,
        )

    def basic_game_value_adds(self, game_value: int) -> int:
        # Tout doesn't have schneider or black, but the game value is doubled
        game_value = self._add_runners(game_value)
        game_value = self._apply_doubles(game_value)
        return game_value * 2

    def game_value_breakdown(self) -> str:
        lines: list[str] = [f"\n{"Alone price:":<11} {self.alone_price} cents"]
        lines.extend(self._runners_breakdown_lines())
        lines.extend(self._doubles_breakdown_lines())
        lines.append(f"{"Tout:":<11} * 2")
        return "\n".join(lines)


class WenzToutGameValueCalculator(ToutGameValueCalculator):
    pass


class SoloToutGameValueCalculator(ToutGameValueCalculator):
    pass
