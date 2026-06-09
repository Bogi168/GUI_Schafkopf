from __future__ import annotations
from typing import Callable, TYPE_CHECKING
from card_classes.Cards import Color, Type
from system.text import (
    error_message,
    prompt_ask_play_card_decision,
    prompt_ask_to_double_game_value,
    prompt_ask_to_choose_game,
    prompt_choose_game,
    prompt_choose_color,
    prompt_ask_player_shoots,
    show_player_cards,
    show_played_card,
    prompt_ask_player_shoots_back,
    prompt_ask_for_hochzeit,
    prompt_ask_for_ramsch,
    prompt_ask_swap_card_decision,
)
import random

if TYPE_CHECKING:
    from game_classes.Game import Game
    from system.Renderer import Renderer
    from card_classes.Cards import Card
    from input_validators.GameDecisionValidator import GameDecisionValidator


class Player:
    """An object that represents a player on the game"""

    def __init__(
        self,
        player_name: str,
        renderer: Renderer,
        game_decision_validator: GameDecisionValidator,
    ) -> None:
        """
        :param player_name: The player's name
        :type player_name: str
        :param renderer: An object to render information
        :type renderer: Renderer
        :param game_decision_validator: An object to validate the game decisions made by the player
        :type game_decision_validator: GameDecisionValidator
        """

        self.player_name: str = player_name
        self.renderer: Renderer = renderer
        self.game_decision_validator: GameDecisionValidator = game_decision_validator
        self.player_cards: list[Card] = []
        self.collected_cards: list[Card] = []
        self.money: int = 0
        self.yes_decisions: tuple[str, ...] = ("Y", "YES")
        self.no_decisions: tuple[str, ...] = ("N", "NO")
        self.string_decisions: tuple[str, ...] = self.yes_decisions + self.no_decisions
        self.quit_decisions: tuple[str, ...] = ("QUIT", "Q")

    def __repr__(self) -> str:
        return self.player_name

    @property
    def points(self) -> int:
        """Returns the total points of the player"""

        return sum(card.card_type.points for card in self.collected_cards)

    def ask_double_game_value(self) -> bool:
        """
        Asks the player whether he wants to double the game value or not
        :return: A boolean indicating whether the player wants to double the game value or not
        :rtype: bool
        """

        self.renderer.render(
            message=show_player_cards(
                player_name=self.player_name, player_cards=self.player_cards
            )
        )

        decision = self.renderer.ask_with_validation(
            prompt=prompt_ask_to_double_game_value(player_name=self.player_name),
            error_prefix=error_message,
            preprocess=lambda x: x.strip().upper(),
            validator=lambda x: x in self.string_decisions,
        )

        return decision in self.yes_decisions

    def ask_want_choose_game(self) -> bool:
        """
        Asks the player whether he wants to choose a game or not
        :return: A boolean indicating whether the player wants to choose a game or not
        :rtype: bool
        """

        decision = self.renderer.ask_with_validation(
            prompt=prompt_ask_to_choose_game(player_name=self.player_name),
            error_prefix=error_message,
            preprocess=lambda x: x.strip().upper(),
            validator=lambda x: x in self.string_decisions,
        )
        return decision in self.yes_decisions

    def ask_for_hochzeit(self) -> bool:
        """
        Asks the player whether he wants to be the partner of a Hochzeit or not
        :return: A boolean indicating whether the player wants to be the partner of a Hochzeit or not
        :rtype: bool
        """

        self.renderer.render(
            message=show_player_cards(
                player_name=self.player_name, player_cards=self.player_cards
            )
        )

        if all(
            card.card_type in [Type.OBER, Type.UNTER] or card.card_color == Color.HERZ
            for card in self.player_cards
        ):
            legal_decisions: tuple[str, ...] = self.no_decisions
        else:
            legal_decisions: tuple[str, ...] = self.string_decisions

        decision = self.renderer.ask_with_validation(
            prompt=prompt_ask_for_hochzeit(player_name=self.player_name),
            error_prefix=error_message,
            preprocess=lambda x: x.strip().upper(),
            validator=lambda x: x in legal_decisions,
        )

        return decision in self.yes_decisions

    def get_sau_color(self) -> Color:
        """
        Asks the player for a sau color
        :return: The sau color chosen by the player
        :rtype: Color
        """

        valid_color_inputs: dict[str, Color] = (
            self.game_decision_validator.get_valid_call_sau_color_inputs(
                player_cards=self.player_cards
            )
        )

        sau_color_decision = self.renderer.ask_with_validation(
            prompt=prompt_choose_color(
                player_name=self.player_name, valid_colors=valid_color_inputs
            ),
            error_prefix=error_message,
            preprocess=lambda x: x.strip(),
            validator=lambda x: x in valid_color_inputs.keys(),
        )

        sau_color = valid_color_inputs[sau_color_decision]

        return sau_color

    def get_trump_color(self) -> Color:
        """
        Asks the player for a trump color
        :return: The trump color chosen by the player
        :rtype: Color
        """

        valid_color_inputs: dict[str, Color] = (
            self.game_decision_validator.get_valid_solo_color_inputs()
        )

        trump_color_decision = self.renderer.ask_with_validation(
            prompt=prompt_choose_color(
                player_name=self.player_name, valid_colors=valid_color_inputs
            ),
            error_prefix=error_message,
            preprocess=lambda x: x.strip(),
            validator=lambda x: x in valid_color_inputs.keys(),
        )

        trump_color = valid_color_inputs[trump_color_decision]

        return trump_color

    def choose_game_mode(
        self,
        prev_game_mode: type[Game] | None,
        quitting_possible: bool = False,
    ) -> type[Game] | None:
        """
        Returns a valid game decision made by the player
        :param prev_game_mode: The previously chosen game mode by another player
        :type prev_game_mode: type[Game] | None
        :param quitting_possible: A boolean value that indicates whether quitting the game choosing process is legal
        :type quitting_possible: bool
        :return: A game_mode decision or nothing if the player decides to quit the choosing process
        :rtype: type[Game] | None
        """

        valid_game_mode_decisions = (
            self.game_decision_validator.get_valid_game_mode_decisions(
                prev_game_mode=prev_game_mode, player_cards=self.player_cards
            )
        )
        decision = self.renderer.ask_with_validation(
            prompt=prompt_choose_game(
                player_name=self.player_name,
                quitting_possible=quitting_possible,
                possible_game_mode_decisions=valid_game_mode_decisions,
            ),
            error_prefix=error_message,
            preprocess=lambda x: x.strip().upper(),
            validator=lambda x: x in valid_game_mode_decisions.keys()
            or (x in self.quit_decisions and quitting_possible),
        )
        if decision in self.quit_decisions:
            return None
        else:
            return valid_game_mode_decisions[decision]

    def ask_for_ramsch(self) -> bool:
        """
        Asks the player whether he wants to play a Ramsch or draw the cards again.
        :return: A boolean indicating whether the player wants to play a Ramsch.
        :rtype: bool
        """

        decision = self.renderer.ask_with_validation(
            prompt=prompt_ask_for_ramsch(player_name=self.player_name),
            error_prefix=error_message,
            preprocess=lambda x: x.strip().upper(),
            validator=lambda x: x in self.string_decisions,
        )

        return decision in self.yes_decisions

    def ask_shoot(self, ask_shoot_back: bool = False) -> bool:
        """
        Asks the player whether he wants to shoot or not.
        By shooting, the player doubles the game value and his team turns to the active team.
        :param ask_shoot_back: If the player is asked to shoot back, it should be set to True
        :type ask_shoot_back: bool
        :return: A boolean indicating whether the player wants to shoot or not
        :rtype: bool
        """

        self.renderer.render(
            show_player_cards(
                player_name=self.player_name, player_cards=self.player_cards
            )
        )
        if ask_shoot_back:
            prompt: str = prompt_ask_player_shoots_back(player_name=self.player_name)
        else:
            prompt: str = prompt_ask_player_shoots(player_name=self.player_name)

        decision = self.renderer.ask_with_validation(
            prompt=prompt,
            error_prefix=error_message,
            preprocess=lambda x: x.strip().upper(),
            validator=lambda x: x in self.string_decisions,
        )
        return decision in self.yes_decisions

    def is_card_decision_valid_number(self, index_decision: str) -> bool:
        """
        Checks, whether the player chose a valid card number for his next card decision
        :param index_decision: The input made by the player
        :type index_decision: str
        :return: A boolean value which indicates whether the player chose a valid card number or not
        :rtype: bool
        """
        return index_decision.isdigit() and 1 <= int(index_decision) <= len(
            self.player_cards
        )

    def get_card_swap_decision(
        self,
        move_validator: Callable[[Card], bool],
        trumps: list[Card],
        is_game_chooser: bool,
    ) -> Card:
        """
        Asks the player to make a card decision for the Hochzeit swap
        :param move_validator: A function that checks whether the decision by the player is legal
        :type move_validator: Callable[[Card], bool]
        :param trumps: A list of all the trumps
        :type trumps: list[Card]
        :param is_game_chooser: A boolean that indicates whether the player choose the game mode or not.
        :type is_game_chooser: bool
        :return: A valid card decision made by the player
        :rtype: Card
        """

        self.renderer.render(
            message=show_player_cards(
                player_name=self.player_name, player_cards=self.player_cards
            )
        )
        index_decision = self.renderer.ask_with_validation(
            prompt=prompt_ask_swap_card_decision(
                player_name=self.player_name,
                player_cards=self.player_cards,
                trumps=trumps,
                is_game_chooser=is_game_chooser,
            ),
            error_prefix=error_message,
            preprocess=lambda x: x.strip(),
            validator=lambda x: self.is_card_decision_valid_number(x)
            and move_validator(self.player_cards[int(x) - 1]),
        )

        decision: Card = self.player_cards[int(index_decision) - 1]
        self.player_cards.remove(decision)

        return decision

    def get_card_play_decision(
        self,
        move_validator: Callable[[Card], bool],
    ) -> Card:
        """
        Asks the player to make a card decision
        :param move_validator: A function that checks whether the decision by the player is legal
        :type move_validator: Callable[[Card], bool]
        :return: A valid card decision made by the player
        :rtype: Card
        """

        self.renderer.render(
            message=show_player_cards(
                player_name=self.player_name, player_cards=self.player_cards
            )
        )
        index_decision = self.renderer.ask_with_validation(
            prompt=prompt_ask_play_card_decision(
                player_name=self.player_name, player_cards=self.player_cards
            ),
            error_prefix=error_message,
            preprocess=lambda x: x.strip(),
            validator=lambda x: self.is_card_decision_valid_number(x)
            and move_validator(self.player_cards[int(x) - 1]),
        )

        decision = self.player_cards[int(index_decision) - 1]
        self.player_cards.remove(decision)

        return decision


class Bot(Player):
    def __init__(
        self,
        bot_name: str,
        renderer: Renderer,
        game_decision_validator: GameDecisionValidator,
    ):
        super().__init__(
            player_name=bot_name,
            renderer=renderer,
            game_decision_validator=game_decision_validator,
        )

    def ask_double_game_value(self) -> bool:
        return False

    def ask_want_choose_game(self) -> bool:
        return True

    def choose_game_mode(
        self,
        prev_game_mode: type[Game] | None,
        quitting_possible: bool = False,
    ) -> type[Game] | None:
        if quitting_possible:
            return None
        valid = self.game_decision_validator.get_valid_game_mode_decisions(
            prev_game_mode=prev_game_mode, player_cards=self.player_cards
        )
        return random.choice(list(valid.values()))

    def get_sau_color(self) -> Color:
        valid = self.game_decision_validator.get_valid_call_sau_color_inputs(
            player_cards=self.player_cards
        )
        return random.choice(list(valid.values()))

    def get_trump_color(self) -> Color:
        valid = self.game_decision_validator.get_valid_solo_color_inputs()
        return random.choice(list(valid.values()))

    def ask_for_hochzeit(self) -> bool:
        return False

    def ask_for_ramsch(self) -> bool:
        return False

    def get_card_play_decision(
        self,
        move_validator: Callable[[Card], bool],
    ) -> Card:
        legal_cards = [card for card in self.player_cards if move_validator(card)]
        decision = random.choice(legal_cards)

        self.renderer.render(
            message=show_played_card(player_name=self.player_name, decision=decision)
        )
        self.player_cards.remove(decision)

        return decision

    def ask_shoot(self, ask_shoot_back: bool = False) -> bool:
        return False
