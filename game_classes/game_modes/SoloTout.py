from __future__ import annotations
from typing import TYPE_CHECKING

from game_classes.game_modes.GameRegistry import GameRegistry
from game_classes.game_modes.Solo import Solo
from money_handling.GameValueCalculator import SoloToutGameValueCalculator
from money_handling.WinnersSelector import SoloToutWinnersSelector

if TYPE_CHECKING:
    from money_handling.GameValueCalculator import GameValueCalculator
    from player_classes.Player import Player
    from player_classes.Team import Team
    from money_handling.WinnersSelector import WinnersSelector
    from game_classes.RoundManager import RoundManager


@GameRegistry.register_game
class SoloTout(Solo):
    name = "Solo Tout"
    rank = 7
    is_choosable = True

    game_chooser: Player
    base_price: int
    alone_price: int

    def play_rounds(self, round_manager: RoundManager) -> None:
        self.tout_play_rounds(
            game_chooser=self.game_chooser, round_manager=round_manager
        )

    def create_winners_selector(self) -> WinnersSelector:
        return SoloToutWinnersSelector(
            teams=self.teams,
            active_team=self.active_team,
            game_chooser=self.game_chooser,
            full_deck=self.cards.full_deck.copy(),
        )

    def get_most_point_teams_for_result(
        self, winners_selector: WinnersSelector
    ) -> list[Team]:
        return []

    def create_game_value_calculator(
        self, winners: list[Player]
    ) -> GameValueCalculator:
        assert self.active_team is not None
        return SoloToutGameValueCalculator(
            base_price=self.base_price,
            alone_price=self.alone_price,
            player_teams=self.player_teams,
            amount_game_value_doubles=self.amount_game_value_doubles,
            active_team=self.active_team,
            winners=winners,
            runners_amount=self.runners_amount,
            amount_game_card_points=self.total_card_points,
        )
