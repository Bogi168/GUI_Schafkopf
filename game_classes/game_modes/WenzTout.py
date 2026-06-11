from __future__ import annotations

from game_classes.game_modes.ToutGameMixin import ToutGameMixin
from game_classes.game_modes.Wenz import Wenz
from money_handling.GameValueCalculator import WenzToutGameValueCalculator
from game_classes.game_modes.GameRegistry import GameRegistry
from money_handling.WinnersSelector import WenzToutWinnersSelector


@GameRegistry.register_game
class WenzTout(ToutGameMixin, Wenz):
    name = "Wenz Tout"
    rank = 6
    is_choosable = True
    is_tout = True

    tout_winners_selector_class = WenzToutWinnersSelector
    tout_game_value_calculator_class = WenzToutGameValueCalculator
