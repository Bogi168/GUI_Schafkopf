from __future__ import annotations
from typing import TYPE_CHECKING, Any

from card_classes.CardPowerCalculator import RamschCardPowerCalculator
from game_classes.Game import Game
from card_classes.Cards import Color, Type
from game_classes.RoundManager import RamschRoundManager
from game_classes.RunnersCalculator import RamschRunnersCalculator
from input_validators.CardDecisionValidator import RamschCardDecisionValidator
from money_handling.GameValueCalculator import RamschGameValueCalculator
from money_handling.WinnersSelector import RamschWinnersSelector
from game_classes.TeamBuilder import RamschTeamBuilder
from game_classes.game_modes.GameRegistry import GameRegistry

if TYPE_CHECKING:
    from player_classes.Player import Player
    from system.Renderer import Renderer
    from card_classes.Cards import Cards
    from money_handling.WinnersSelector import WinnersSelector
    from game_classes.RoundManager import RoundManager
    from money_handling.GameValueCalculator import GameValueCalculator
    from schafkopf_classes.Schafkopf import Schafkopf


@GameRegistry.register_game
class Ramsch(Game):
    """
    The trump types are Ober and Unter.
    The trump color is Herz
    There are no real teams, everybody plays alone.
    The goal is to earn the least amount of points during the game.
    The player with the most points loses the game.
    If multiple players have the same amount of points, all of them lose,
    expect one or more of them shot (doubled the game value and turned active).
    If the player with the most points has 91 points or more, he is the winner of the game.
    """

    name = "Ramsch"
    rank = 1
    is_choosable = False

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        alone_price: int,
        amount_game_value_doubles: int,
    ) -> None:
        """
        :param cards: An object which saves a full deck of cards and provides a deck to play with
        :type cards: Cards
        :param renderer: An object which renders information
        :type renderer: Renderer
        :param players: A list of objects which represent the players
        :type players: list[Player]
        :param alone_price: alone price for game value calculations
        :type alone_price: int
        :param amount_game_value_doubles: The amount of people who decided to double the game value
        :type amount_game_value_doubles: int
        """

        super().__init__(
            cards=cards,
            renderer=renderer,
            team_builder=RamschTeamBuilder(players=players),
            runners_calculator=RamschRunnersCalculator,
            card_power_calculator=RamschCardPowerCalculator(),
            players=players,
            trump_types=[Type.OBER, Type.UNTER],
            trump_color=Color.HERZ,
            amount_game_value_doubles=amount_game_value_doubles,
            card_decision_validator=RamschCardDecisionValidator(),
        )
        self.alone_price: int = alone_price
        self.active_players: list[Player] = []

    @classmethod
    def gather_kwargs(
        cls, chooser: Player | None, schafkopf: Schafkopf
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = super().gather_kwargs(
            chooser=chooser, schafkopf=schafkopf
        )
        kwargs.update(alone_price=schafkopf.alone_price)
        return kwargs

    def create_round_manager(self) -> RoundManager:
        return RamschRoundManager(
            players=self.players,
            player_teams=self.player_teams,
            trumps=self.trumps,
            card_power_calculator=self.card_power_calculator,
            card_decision_validator=self.card_decision_validator,
            game_renderer=self.game_renderer,
        )

    def create_winners_selector(self) -> WinnersSelector:
        assert isinstance(self.round_manager, RamschRoundManager)
        self.active_players: list[Player] = self.round_manager.active_players
        return RamschWinnersSelector(
            teams=self.teams, active_players=self.active_players
        )

    def create_game_value_calculator(
        self, winners: list[Player]
    ) -> GameValueCalculator:
        return RamschGameValueCalculator(
            alone_price=self.alone_price,
            player_teams=self.player_teams,
            amount_game_value_doubles=self.amount_game_value_doubles,
            winners=winners,
            amount_game_card_points=self.total_card_points,
        )
