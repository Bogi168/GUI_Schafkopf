from __future__ import annotations
from typing import TYPE_CHECKING

from card_classes.Cards import Color, Type
from game_classes.game_modes.Hochzeit import Hochzeit
from game_classes.game_modes.Sauspiel import Sauspiel

if TYPE_CHECKING:
    from game_classes.Game import Game
    from card_classes.Cards import Card


class GameDecisionValidator:
    """
    An object that checks whether the game decision by a player is legal or not
    """

    def __init__(
        self,
        choosable_game_rank_mapping: dict[type[Game], int],
    ) -> None:
        """
        :param choosable_game_rank_mapping: A dictionary of all the implemented games with their ranks
        :type choosable_game_rank_mapping: dict[type[Game], int]
        :rtype: None
        """

        self.choosable_game_rank_mapping: dict[type[Game], int] = (
            choosable_game_rank_mapping
        )
        self.sau_color_mapping: dict[str, Color] = {
            "1": Color.EICHEL,
            "2": Color.GRUEN,
            "3": Color.SCHELLEN,
        }
        self.solo_trump_color_mapping: dict[str, Color] = {
            "1": Color.EICHEL,
            "2": Color.GRUEN,
            "3": Color.HERZ,
            "4": Color.SCHELLEN,
        }

    @staticmethod
    def is_hochzeit_playable(player_cards: list[Card]) -> bool:
        trump_types: list[Type] = [Type.OBER, Type.UNTER]
        trump_color: Color = Color.HERZ
        player_trumps: list[Card] = [
            card
            for card in player_cards
            if card.card_color == trump_color or card.card_type in trump_types
        ]
        return len(player_trumps) == 1

    @staticmethod
    def is_player_owns_sau(player_cards: list[Card], sau_color: Color) -> bool:
        """
        Checks whether a player owns the sau of a given color.
        :param player_cards: The player's cards
        :type player_cards: list[Card]
        :param sau_color: The color of the sau for which the player's cards should be checked
        :type sau_color: Color
        :return: A boolean value indicating whether the player owns the sau
        :rtype: bool
        """

        return any(
            (card.card_type == Type.SAU and card.card_color == sau_color)
            for card in player_cards
        )

    @staticmethod
    def count_color_cards(
        player_cards: list[Card], color: Color, trump_types: list[Type]
    ) -> int:
        """
        Counts the amount of cards of a given color that a player has,
        ignoring cards of the color that are from the trump type.
        :param player_cards: The player's cards
        :type player_cards: list[Card]
        :param color: The color for which the number of cards should be counted
        :type color: Color
        :param trump_types: A list of the trump types of the game
        :type trump_types: list[Type]
        :return: The amount of cards the player has of the given color
        :rtype: int
        """

        return sum(
            1
            for card in player_cards
            if card.card_color == color and card.card_type not in trump_types
        )

    def is_sauspiel_playable(self, player_cards: list[Card]) -> bool:
        """
        Checks whether the player is able to choose sauspiel as a game mode.
        Choosing Sauspiel is only possible if you have cards that are not trumps
        and don't have the Sau for every non-trump card color you have.
        :param player_cards: The player's cards
        :type player_cards: list[Card]
        :return: A boolean value indicating whether the player is able to choose sauspiel as a game mode
        :rtype: bool
        """

        colors = [color for color in self.sau_color_mapping.values()]
        callable_color_cards = 0

        for card_color in colors:
            if self.is_player_owns_sau(sau_color=card_color, player_cards=player_cards):
                continue

            callable_color_cards += self.count_color_cards(
                player_cards=player_cards,
                color=card_color,
                trump_types=[Type.OBER, Type.UNTER],
            )

            if callable_color_cards != 0:
                return True

        return False

    def get_available_game_modes(
        self,
        playable_games: list[type[Game]],
        prev_game: type[Game] | None,
        player_cards: list[Card],
    ) -> list[type[Game]]:
        """
        Returns a list of choosable game modes for a player.
        :param playable_games: A list of all the implemented game modes
        :type playable_games: list[type[Game]]
        :param prev_game: The game mode, chosen by a previous player
        :type prev_game: type[Game] | None
        :param player_cards: The player's cards
        :type player_cards: list[Card]
        """

        if prev_game is None:
            prev_game_rank = 0
        else:
            prev_game_rank = self.choosable_game_rank_mapping[prev_game]

        available_game_modes: list[type[Game]] = playable_games.copy()

        if Hochzeit in available_game_modes and not self.is_hochzeit_playable(
            player_cards=player_cards
        ):
            available_game_modes.remove(Hochzeit)

        if Sauspiel in available_game_modes and not self.is_sauspiel_playable(
            player_cards=player_cards
        ):
            available_game_modes.remove(Sauspiel)

        if prev_game_rank != 0:
            available_game_modes: list[type[Game]] = [
                game
                for game in available_game_modes
                if self.choosable_game_rank_mapping[game] > prev_game_rank
            ]

        available_game_modes.sort(key=lambda x: self.choosable_game_rank_mapping[x])
        return available_game_modes

    def get_valid_game_mode_decisions(
        self, prev_game_mode: type[Game] | None, player_cards: list[Card]
    ) -> dict[str, type[Game]]:
        """
        Returns a dictionary of valid inputs for a game decision to make by a player.
        :param prev_game_mode: The game mode, chosen by a previous player
        :type prev_game_mode: type[Game] | None
        :param player_cards: The player's cards
        :type player_cards: list[Card]
        :return: dictionary of valid inputs for a game decision to make by a player
        """

        available_game_modes: list[type[Game]] = self.get_available_game_modes(
            playable_games=[game for game in self.choosable_game_rank_mapping.keys()],
            prev_game=prev_game_mode,
            player_cards=player_cards,
        )
        valid_inputs: dict[str, type[Game]] = {
            str(index): game_mode
            for index, game_mode in enumerate(available_game_modes, start=1)
        }
        return valid_inputs

    def get_valid_call_sau_colors(self, player_cards: list[Card]) -> list[Color]:
        """
        Returns a list of valid colors for a player to choose a color for the call sau.
        :param player_cards: The player's cards
        :type player_cards: list[Card]
        :return: list of valid colors for a player to choose a color for the call sau
        :rtype: list[Color]
        """

        sau_colors: list[Color] = [color for color in self.sau_color_mapping.values()]
        playable_colors: list[Color] = sau_colors.copy()

        for color in sau_colors:
            player_has_sau = self.is_player_owns_sau(
                player_cards=player_cards, sau_color=color
            )
            color_count = self.count_color_cards(
                player_cards=player_cards,
                color=color,
                trump_types=[Type.OBER, Type.UNTER],
            )
            if color_count == 0 or player_has_sau:
                playable_colors.remove(color)

        return playable_colors

    def get_valid_call_sau_color_inputs(
        self, player_cards: list[Card]
    ) -> dict[str, Color]:
        """
        Returns a dictionary of legal inputs by a player for his sau color decision.
        :param player_cards: The player's cards
        :type player_cards: list[Card]
        """

        available_colors: list[Color] = self.get_valid_call_sau_colors(
            player_cards=player_cards
        )
        valid_inputs = {
            str(index): color for index, color in enumerate(available_colors, start=1)
        }
        return valid_inputs

    def get_valid_solo_color_inputs(self) -> dict[str, Color]:
        valid_inputs: dict[str, Color] = {
            str(key): color
            for key, color in enumerate(self.solo_trump_color_mapping.values(), start=1)
        }
        return valid_inputs
