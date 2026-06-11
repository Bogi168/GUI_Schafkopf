from __future__ import annotations

from game_classes.game_modes.GameRegistry import GameRegistry
from game_classes.game_modes.Solo import Solo
from game_classes.game_modes.ToutGameMixin import ToutGameMixin
from money_handling.GameValueCalculator import SoloToutGameValueCalculator
from money_handling.WinnersSelector import SoloToutWinnersSelector


@GameRegistry.register_game
class SoloTout(ToutGameMixin, Solo):
    name = "Solo Tout"
    rank = 7
    is_choosable = True
    is_tout = True

    tout_winners_selector_class = SoloToutWinnersSelector
    tout_game_value_calculator_class = SoloToutGameValueCalculator
