from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from game_classes.Game import Game


class GameRegistry:
    _game_modes: list[type[Game]] = []

    @classmethod
    def register_game(cls, game_class: type[Game]) -> type[Game]:
        if game_class not in cls._game_modes:
            cls._game_modes.append(game_class)
        return game_class

    @classmethod
    def get_game_mapping(cls) -> list[dict[str, Any]]:
        return [
            {
                "name": game_mode.name,
                "rank": game_mode.rank,
                "is_choosable": game_mode.is_choosable,
                "class": game_mode,
            }
            for game_mode in cls._game_modes
        ]

    @classmethod
    def all_games(cls) -> list[type[Game]]:
        return cls._game_modes.copy()
