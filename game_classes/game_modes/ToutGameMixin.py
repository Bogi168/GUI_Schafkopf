from __future__ import annotations
from typing import TYPE_CHECKING

from game_classes.Game import Game
from money_handling.GameValueCalculator import ToutGameValueCalculator
from money_handling.WinnersSelector import ToutWinnersSelector

if TYPE_CHECKING:
    from game_classes.RoundManager import RoundManager
    from money_handling.GameValueCalculator import GameValueCalculator
    from money_handling.WinnersSelector import WinnersSelector
    from player_classes.Player import Player
    from player_classes.Team import Team


class ToutGameMixin(Game):
    """Shared behaviour for Tout games (WenzTout, SoloTout).

    The game chooser must win every trick to win at all, so play stops as
    soon as someone else wins a round (see Game.play_rounds), there's no
    "most points" comparison for the result, and the value is doubled with
    no schneider/black (see ToutGameValueCalculator). Subclasses only need
    to set the *_class attributes to their mode-specific selector/calculator.
    """

    game_chooser: Player
    base_price: int
    alone_price: int

    tout_winners_selector_class: type[ToutWinnersSelector] = ToutWinnersSelector
    tout_game_value_calculator_class: type[ToutGameValueCalculator] = (
        ToutGameValueCalculator
    )

    def play_rounds(self, round_manager: RoundManager) -> None:
        super().play_rounds(
            round_manager=round_manager, game_chooser=self.game_chooser
        )

    def create_winners_selector(self) -> WinnersSelector:
        return self.tout_winners_selector_class(
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
        return self.tout_game_value_calculator_class(
            base_price=self.base_price,
            alone_price=self.alone_price,
            player_teams=self.player_teams,
            amount_game_value_doubles=self.amount_game_value_doubles,
            active_team=self.active_team,
            winners=winners,
            runners_amount=self.runners_amount,
            amount_game_card_points=self.total_card_points,
        )
