from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from game_classes.RoundManager import RoundManager
from money_handling.WinnersSelector import WinnersSelector
from player_classes.Team import Team
from card_classes.Cards import Card, Type, Color
from game_classes.RunnersCalculator import (
    RunnersCalculator,
)
from card_classes.CardPowerCalculator import CardPowerCalculator
from input_validators.CardDecisionValidator import CardDecisionValidator
from system.Renderer import GameResult

from money_handling.MoneyDistributer import MoneyDistributer

if TYPE_CHECKING:
    from player_classes.Player import Player
    from system.Renderer import Renderer
    from card_classes.Cards import Cards
    from game_classes.TeamBuilder import TeamSetup, TeamBuilder
    from game_classes.RunnersCalculator import RunnersSetup
    from money_handling.GameValueCalculator import GameValueCalculator
    from schafkopf_classes.Schafkopf import Schafkopf


class Game(ABC):
    """An object that represents the game"""

    name = "Game"
    rank = 0
    is_choosable = False
    is_tout = False

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        team_builder: TeamBuilder,
        card_power_calculator: CardPowerCalculator,
        card_decision_validator: CardDecisionValidator,
        runners_calculator: type[RunnersCalculator],
        trump_types: list[Type],
        trump_color: Color | None,
        players: list[Player],
        amount_game_value_doubles: int,
    ) -> None:
        """
        :param cards: An object which saves a full deck of cards and provides a deck to play with
        :type cards: Cards
        :param renderer: An object which renders information
        :type renderer: Renderer
        :param card_power_calculator: An object which calculates the card power
        :type card_power_calculator: CardPowerCalculator
        :param players: A list of objects which represent the players
        :type players: list[Player]
        :param amount_game_value_doubles: The amount of players who doubled the game value
        :type amount_game_value_doubles: int
        """

        self.cards: Cards = cards
        self.team_builder: TeamBuilder = team_builder
        self.card_power_calculator: CardPowerCalculator = card_power_calculator
        self.card_decision_validator: CardDecisionValidator = card_decision_validator
        self.runners_calculator: type[RunnersCalculator] = runners_calculator
        self.renderer: Renderer = renderer
        self.amount_game_value_doubles: int = amount_game_value_doubles
        self.players: list[Player] = players
        self.trump_color: Color | None = trump_color
        # Wenz/WenzTout pass trump_types=[Type.UNTER] and trump_color=None,
        # which is the only combination yielding exactly the 4 Unter as
        # trumps; bot_strategy.wants_to_shoot relies on this to detect the
        # Wenz family via len(trumps).
        self.trumps: list[Card] = [
            card
            for card in cards.full_deck
            if card.card_type in trump_types or card.card_color == trump_color
        ]
        self.trumps.sort(key=card_power_calculator.get_card_power, reverse=True)
        self.round_manager: RoundManager | None = None
        self.total_card_points: int = sum(
            card.card_type.points for card in cards.full_deck
        )
        self.player_teams: dict[Player, Team] = dict()
        self.teams: list[Team] = []
        self.active_team: Team | None = None
        self.runners_amount: int = 0

    @classmethod
    def gather_kwargs(
        cls, chooser: Player | None, schafkopf: Schafkopf
    ) -> dict[str, Any]:
        return dict(
            cards=schafkopf.cards,
            renderer=schafkopf.renderer,
            players=schafkopf.players,
            amount_game_value_doubles=schafkopf.amount_game_value_doubles,
        )

    def create_teams(self) -> None:
        """
        Creates the team objects and sets player_teams, active_team and teams of Game
        :rtype: None
        """

        teams_setup: TeamSetup = self.team_builder.create_teams()
        self.player_teams: dict[Player, Team] = teams_setup.player_teams
        self.active_team: Team = teams_setup.active_team
        self.teams: list[Team] = teams_setup.teams

    def create_round_manager(self) -> RoundManager:
        """
        Creates a round manager object.
        :return: A round manager object
        :rtype: RoundManager
        """

        return RoundManager(
            players=self.players,
            player_teams=self.player_teams,
            trumps=self.trumps,
            card_power_calculator=self.card_power_calculator,
            card_decision_validator=self.card_decision_validator,
            active_team=self.active_team,
            renderer=self.renderer,
            is_tout=self.is_tout,
        )

    def create_winners_selector(self) -> WinnersSelector:
        """
        Creates a winners selector object.
        :return: A winners selector object
        :rtype: WinnersSelector
        """

        return WinnersSelector(teams=self.teams, active_team=self.active_team)

    @abstractmethod
    def create_game_value_calculator(
        self, winners: list[Player]
    ) -> GameValueCalculator:
        pass

    def display_detail(self) -> str | None:
        """Optional extra info about the chosen game (e.g. trump or Sau color)."""

        return None

    def display_detail_color(self) -> Color | None:
        """The Color (if any) named in display_detail(), so the GUI can show
        a suit symbol instead of the color name."""

        return None

    def sort_player_hands(self) -> None:
        """
        Sorts the cards of the players according to their power in the game
        and re-renders the hands, so the new order shows the moment the
        game mode is settled rather than on each player's next turn.
        :return: None
        """

        for player in self.players:
            player.player_cards.sort(
                key=self.card_power_calculator.get_card_power, reverse=True
            )
            self.renderer.render_hand(player=player, cards=player.player_cards)

    def play_rounds(
        self, round_manager: RoundManager, game_chooser: Player | None = None
    ) -> None:
        """Plays every round, rewarding the winner of each.

        ``game_chooser`` is only set for Tout games (see
        game_modes.ToutGameMixin): there, the chooser must win every trick,
        so play stops as soon as a round is won by someone else.
        """

        for i in range(len(self.players[0].player_cards)):
            round_manager.play_round(is_first_round=(i == 0))
            round_winner: Player = round_manager.get_round_winner()
            round_manager.reward_round_winner(round_winner=round_winner)
            if game_chooser is not None and round_winner != game_chooser:
                break
            round_manager.prepare_next_round(round_winner=round_winner)

    def calculate_runners_amount(self) -> None:
        """
        Creates a RunnersCalculator object, calculates the amount of
        game runners and sets the runners_amount variable of Game.
        :rtype: None
        """
        runners_calculator: RunnersCalculator = self.runners_calculator(self.trumps)
        runners_setup: RunnersSetup = runners_calculator.count_game_runners(
            teams=self.teams
        )
        self.runners_amount: int = runners_setup.runners_amount

    def get_most_point_teams_for_result(
        self, winners_selector: WinnersSelector
    ) -> list[Team]:
        return winners_selector.get_most_points_teams()

    def handle_winners(self) -> None:
        """
        Creates an object that selects the winners.
        Creates another object after to distribute the money among the players.
        :return: None
        """

        winners_selector: WinnersSelector = self.create_winners_selector()
        winners: list[Player] = winners_selector.get_game_winners()
        most_point_teams: list[Team] = self.get_most_point_teams_for_result(
            winners_selector=winners_selector
        )
        gv_calculator: GameValueCalculator = self.create_game_value_calculator(
            winners=winners
        )
        game_value: int = gv_calculator.calculate_game_value()
        MoneyDistributer.distribute_money(
            game_value=game_value, winners=winners, players=self.players
        )
        self.renderer.render_game_result(
            result=GameResult(
                most_point_teams=most_point_teams,
                winners=winners,
                game_value=game_value,
                game_value_breakdown=gv_calculator.game_value_breakdown(),
                players=self.players,
            )
        )

    def play_game(self) -> None:
        """
        Simulates a full game.
        :return: None
        """

        self.create_teams()
        self.sort_player_hands()
        self.calculate_runners_amount()
        self.round_manager = self.create_round_manager()
        assert self.round_manager is not None
        self.play_rounds(round_manager=self.round_manager)
        self.amount_game_value_doubles += self.round_manager.amt_game_val_doubles
        self.active_team: Team = self.round_manager.active_team
        self.handle_winners()
