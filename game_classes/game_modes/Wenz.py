from __future__ import annotations
from typing import TYPE_CHECKING, Any

from card_classes.CardPowerCalculator import WenzCardPowerCalculator
from game_classes.Game import Game
from card_classes.Cards import Type
from game_classes.RunnersCalculator import WenzRunnersCalculator
from input_validators.CardDecisionValidator import WenzCardDecisionValidator
from money_handling.GameValueCalculator import WenzGameValueCalculator
from game_classes.TeamBuilder import WenzTeamBuilder
from game_classes.game_modes.GameRegistry import GameRegistry

if TYPE_CHECKING:
    from player_classes.Player import Player
    from system.Renderer import Renderer
    from card_classes.Cards import Cards
    from money_handling.GameValueCalculator import GameValueCalculator
    from schafkopf_classes.Schafkopf import Schafkopf


@GameRegistry.register_game
class Wenz(Game):
    """
    The only trump type is Unter.
    There are no trump colors.
    The game chooser has to play alone.
    The rest of the players build a team.
    The goal is to earn the highest amount of points as a team during the game.
    The team with the most points wins the game.
    If the game chooser and the rest have the same amount of points, the game chooser loses,
    except somebody from the other team shot and game chooser didn't shoot back
    (doubled the game value and turned active).
    """

    name = "Wenz"
    rank = 4
    is_choosable = True

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        game_chooser: Player,
        base_price: int,
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
        :param game_chooser: The player who choose the game
        :type game_chooser: Player
        :param base_price: base price for game value calculations
        :type base_price: int
        :param alone_price: alone price for game value calculations
        :type alone_price: int
        :param amount_game_value_doubles: The amount of people who decided to double the game value
        :type amount_game_value_doubles: int
        """

        super().__init__(
            cards=cards,
            renderer=renderer,
            team_builder=WenzTeamBuilder(players=players, game_chooser=game_chooser),
            runners_calculator=WenzRunnersCalculator,
            card_power_calculator=WenzCardPowerCalculator(),
            players=players,
            trump_types=[Type.UNTER],
            trump_color=None,
            amount_game_value_doubles=amount_game_value_doubles,
            card_decision_validator=WenzCardDecisionValidator(),
        )
        self.game_chooser: Player = game_chooser
        self.alone_price: int = alone_price
        self.base_price: int = base_price

    @classmethod
    def gather_kwargs(
        cls, chooser: Player | None, schafkopf: Schafkopf
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = super().gather_kwargs(
            chooser=chooser, schafkopf=schafkopf
        )
        kwargs.update(
            game_chooser=chooser,
            base_price=schafkopf.base_price,
            alone_price=schafkopf.alone_price,
        )
        return kwargs

    def create_game_value_calculator(
        self, winners: list[Player]
    ) -> GameValueCalculator:
        assert self.active_team is not None
        return WenzGameValueCalculator(
            base_price=self.base_price,
            alone_price=self.alone_price,
            player_teams=self.player_teams,
            amount_game_value_doubles=self.amount_game_value_doubles,
            active_team=self.active_team,
            winners=winners,
            runners_amount=self.runners_amount,
            amount_game_card_points=self.total_card_points,
        )
