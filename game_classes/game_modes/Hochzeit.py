from __future__ import annotations
from typing import TYPE_CHECKING, Any

from card_classes.Cards import Color, Type
from card_classes.CardPowerCalculator import HochzeitCardPowerCalculator
from game_classes.Game import Game
from game_classes.game_modes.GameRegistry import GameRegistry
from game_classes.RunnersCalculator import RunnersCalculator
from input_validators.CardDecisionValidator import HochzeitCardDecisionValidator
from money_handling.GameValueCalculator import (
    GameValueCalculator,
    HochzeitGameValueCalculator,
)
from game_classes.TeamBuilder import HochzeitTeamBuilder
from system.custom_exceptions import GameNotPlayableError

if TYPE_CHECKING:
    from card_classes.Cards import Cards, Card
    from system.Renderer import Renderer
    from player_classes.Player import Player
    from schafkopf_classes.Schafkopf import Schafkopf


@GameRegistry.register_game
class Hochzeit(Game):

    name = "Hochzeit"
    rank = 3
    is_choosable = True

    def __init__(
        self,
        cards: Cards,
        renderer: Renderer,
        players: list[Player],
        amount_game_value_doubles: int,
        game_chooser: Player,
        partner: Player,
        base_price: int,
        alone_price: int,
    ):
        super().__init__(
            cards=cards,
            renderer=renderer,
            team_builder=HochzeitTeamBuilder(
                players=players,
                game_chooser=game_chooser,
                partner=partner,
            ),
            runners_calculator=RunnersCalculator,
            card_power_calculator=HochzeitCardPowerCalculator(),
            players=players,
            trump_types=[Type.OBER, Type.UNTER],
            trump_color=Color.HERZ,
            amount_game_value_doubles=amount_game_value_doubles,
            card_decision_validator=HochzeitCardDecisionValidator(),
        )
        self.game_chooser = game_chooser
        self.base_price = base_price
        self.alone_price = alone_price

    @classmethod
    def gather_kwargs(
        cls, chooser: Player | None, schafkopf: Schafkopf
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = super().gather_kwargs(
            chooser=chooser, schafkopf=schafkopf
        )
        assert chooser is not None
        partner: Player | None = schafkopf.get_hochzeit_partner(game_chooser=chooser)
        if partner is None:
            raise GameNotPlayableError("No partner found for Hochzeit")
        kwargs.update(
            alone_price=schafkopf.alone_price,
            partner=partner,
            game_chooser=chooser,
            base_price=schafkopf.base_price,
        )
        return kwargs

    def hochzeit_card_swap(self):
        hochzeit_players: list[Player] = self.player_teams[self.game_chooser].players
        swap_cards: list[Card] = []

        for player in hochzeit_players:
            is_game_chooser: bool = player == self.game_chooser
            decision: Card = player.get_card_swap_decision(
                move_validator=lambda d: self.card_decision_validator.is_card_swap_legal(
                    is_game_chooser=is_game_chooser, decision=d
                ),
            )
            swap_cards.append(decision)

        card_a, card_b = swap_cards
        hochzeit_players[0].player_cards.append(card_b)
        hochzeit_players[1].player_cards.append(card_a)

    def create_teams(self) -> None:
        super().create_teams()
        self.hochzeit_card_swap()

    def create_game_value_calculator(
        self, winners: list[Player]
    ) -> GameValueCalculator:
        assert self.active_team is not None
        return HochzeitGameValueCalculator(
            base_price=self.base_price,
            alone_price=self.alone_price,
            player_teams=self.player_teams,
            amount_game_value_doubles=self.amount_game_value_doubles,
            active_team=self.active_team,
            winners=winners,
            runners_amount=self.runners_amount,
            amount_game_card_points=self.total_card_points,
        )
