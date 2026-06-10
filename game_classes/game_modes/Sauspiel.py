from __future__ import annotations
from typing import TYPE_CHECKING, Any

from game_classes.Game import Game
from card_classes.Cards import Card, Color, Type
from input_validators.CardDecisionValidator import SauspielCardDecisionValidator
from card_classes.CardPowerCalculator import SauspielCardPowerCalculator
from money_handling.GameValueCalculator import SauspielGameValueCalculator
from game_classes.TeamBuilder import SauspielTeamBuilder
from game_classes.RunnersCalculator import RunnersCalculator
from game_classes.game_modes.GameRegistry import GameRegistry

if TYPE_CHECKING:
    from player_classes.Player import Player
    from system.Renderer import Renderer
    from card_classes.Cards import Cards
    from game_classes.RoundManager import RoundManager
    from money_handling.GameValueCalculator import GameValueCalculator
    from schafkopf_classes.Schafkopf import Schafkopf


@GameRegistry.register_game
class Sauspiel(Game):
    """
    The trump types are Ober and Unter.
    The trump color is Herz
    Choosing Sauspiel is only possible if you have cards that are not trumps
    and don't have the Sau for every non-trump card color you have.
    The player who chooses the game has to choose a sau color.
    The sau color decision is only legal, if he/she doesn't own the sau of the chosen sau color
    and has at least one non-trump card of the chosen sau color.
    The game chooser and the person who owns the sau of the chosen sau color (the so called callsau) build a team.
    Until the callsau is played, nobody knows for sure, who his teammates are.
    If the first played card of a round is from the color of the callsau, the owner of the callsau has to play it.
    There are no other scenarios in which the callsau is allowed to be played,
    apart from it being the last card the player has.
    The goal is to earn the highest amount of points as a team during the game.
    The team with the most points wins the game.
    If multiple teams have the same amount of points, the team that didn't choose the game wins,
    except somebody from the other team shot and the team of the game chooser didn't shoot back
    (doubled the game value and turned active).
    """

    name = "Sauspiel"
    rank = 2
    is_choosable = True

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        sau_color: Color,
        game_chooser: Player,
        base_price: int,
        call_price: int,
        amount_game_value_doubles: int,
    ) -> None:
        """
        :param cards: An object which saves a full deck of cards and provides a deck to play with
        :type cards: Cards
        :param renderer: An object which renders information
        :type renderer: Renderer
        :param players: A list of objects which represent the players
        :type players: list[Player]
        :param sau_color: The color of the callsau
        :type sau_color: Color
        :param game_chooser: The player who choose the game
        :type game_chooser: Player
        :param base_price: base price for game value calculations
        :type base_price: int
        :param call_price: call price for game value calculations
        :type call_price: int
        :param amount_game_value_doubles: The amount of people who decided to double the game value
        :type amount_game_value_doubles: int
        """

        call_sau = Card(card_color=sau_color, card_type=Type.SAU)

        super().__init__(
            cards=cards,
            renderer=renderer,
            team_builder=SauspielTeamBuilder(
                players=players,
                call_sau=call_sau,
                game_chooser=game_chooser,
            ),
            runners_calculator=RunnersCalculator,
            card_power_calculator=SauspielCardPowerCalculator(),
            players=players,
            trump_types=[Type.OBER, Type.UNTER],
            trump_color=Color.HERZ,
            amount_game_value_doubles=amount_game_value_doubles,
            card_decision_validator=SauspielCardDecisionValidator(call_sau=call_sau),
        )
        self.game_chooser: Player = game_chooser
        self.base_price: int = base_price
        self.call_price: int = call_price
        self.call_sau: Card = call_sau

    @classmethod
    def gather_kwargs(
        cls, chooser: Player | None, schafkopf: Schafkopf
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = super().gather_kwargs(
            chooser=chooser, schafkopf=schafkopf
        )
        assert chooser is not None
        kwargs.update(
            game_chooser=chooser,
            base_price=schafkopf.base_price,
            call_price=schafkopf.call_price,
            sau_color=chooser.get_sau_color(),
        )
        return kwargs

    def create_round_manager(self) -> RoundManager:
        round_manager = super().create_round_manager()
        round_manager.game_chooser = self.game_chooser
        round_manager.call_sau = self.call_sau
        return round_manager

    def display_detail(self) -> str | None:
        return f"{self.call_sau.card_color.display_name} Sau"

    def display_detail_color(self) -> Color | None:
        return self.call_sau.card_color

    def create_game_value_calculator(
        self, winners: list[Player]
    ) -> GameValueCalculator:
        assert self.active_team is not None
        return SauspielGameValueCalculator(
            base_price=self.base_price,
            call_price=self.call_price,
            player_teams=self.player_teams,
            amount_game_value_doubles=self.amount_game_value_doubles,
            active_team=self.active_team,
            winners=winners,
            runners_amount=self.runners_amount,
            amount_game_card_points=self.total_card_points,
        )
