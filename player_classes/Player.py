from __future__ import annotations
from typing import Callable, TYPE_CHECKING
from card_classes.Cards import Color, Type
from system.Renderer import YesNoKind, ColorChoiceKind
from player_classes.bot_strategy import (
    best_hochzeit_swap_card,
    best_sau_color,
    best_trump_color,
    choose_preferred_game_mode,
    wants_to_double_game_value,
    wants_to_partner_hochzeit,
    wants_to_play,
    wants_to_play_ramsch,
    wants_to_shoot,
)
from player_classes.card_play_strategy import choose_card_to_play
import random

if TYPE_CHECKING:
    from game_classes.Game import Game
    from system.Renderer import Renderer
    from card_classes.Cards import Card
    from input_validators.GameDecisionValidator import GameDecisionValidator
    from player_classes.card_play_strategy import CardPlayContext


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

    def __repr__(self) -> str:
        return self.player_name

    @property
    def points(self) -> int:
        """Returns the total points of the player"""

        return sum(card.card_type.points for card in self.collected_cards)

    @property
    def is_bot(self) -> bool:
        """Returns whether the player is controlled by the computer"""

        return False

    def ask_double_game_value(self) -> bool:
        """
        Asks the player whether he wants to double the game value or not
        :return: A boolean indicating whether the player wants to double the game value or not
        :rtype: bool
        """

        self.renderer.render_hand(player=self, cards=self.player_cards)
        return self.renderer.ask_yes_no(player=self, kind=YesNoKind.DOUBLE_GAME_VALUE)

    def ask_want_choose_game(self, players_who_want_to_play_count: int) -> bool:
        """
        Asks the player whether he wants to choose a game or not
        :param players_who_want_to_play_count: The number of players asked before this one who already want to play
        :type players_who_want_to_play_count: int
        :return: A boolean indicating whether the player wants to choose a game or not
        :rtype: bool
        """

        return self.renderer.ask_yes_no(player=self, kind=YesNoKind.CHOOSE_GAME)

    def ask_for_hochzeit(self) -> bool:
        """
        Asks the player whether he wants to be the partner of a Hochzeit or not
        :return: A boolean indicating whether the player wants to be the partner of a Hochzeit or not
        :rtype: bool
        """

        self.renderer.render_hand(player=self, cards=self.player_cards)

        allow_yes: bool = not all(
            card.card_type in [Type.OBER, Type.UNTER] or card.card_color == Color.HERZ
            for card in self.player_cards
        )

        return self.renderer.ask_yes_no(
            player=self, kind=YesNoKind.HOCHZEIT, allow_yes=allow_yes
        )

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

        return self.renderer.ask_color(
            player=self, options=valid_color_inputs, kind=ColorChoiceKind.SAU
        )

    def get_trump_color(self) -> Color:
        """
        Asks the player for a trump color
        :return: The trump color chosen by the player
        :rtype: Color
        """

        valid_color_inputs: dict[str, Color] = (
            self.game_decision_validator.get_valid_solo_color_inputs()
        )

        return self.renderer.ask_color(
            player=self, options=valid_color_inputs, kind=ColorChoiceKind.TRUMP
        )

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
        return self.renderer.ask_game_mode(
            player=self,
            options=valid_game_mode_decisions,
            quitting_possible=quitting_possible,
        )

    def ask_for_ramsch(self) -> bool:
        """
        Asks the player whether he wants to play a Ramsch or draw the cards again.
        :return: A boolean indicating whether the player wants to play a Ramsch.
        :rtype: bool
        """

        return self.renderer.ask_yes_no(player=self, kind=YesNoKind.RAMSCH)

    def ask_shoot(
        self,
        ask_shoot_back: bool = False,
        trumps: list[Card] | None = None,
        is_tout: bool = False,
        is_ramsch: bool = False,
    ) -> bool:
        """
        Asks the player whether he wants to shoot or not.
        By shooting, the player doubles the game value and his team turns to the active team.
        :param ask_shoot_back: If the player is asked to shoot back, it should be set to True
        :type ask_shoot_back: bool
        :param trumps: The trumps of the current game mode, used by Bots to judge their hand.
            Ignored by human players.
        :type trumps: list[Card] | None
        :param is_tout: Whether the current game mode is a Tout, used by Bots to judge their
            hand. Ignored by human players.
        :type is_tout: bool
        :param is_ramsch: Whether the current round is a Ramsch, used by Bots to judge their
            hand. Ignored by human players.
        :type is_ramsch: bool
        :return: A boolean indicating whether the player wants to shoot or not
        :rtype: bool
        """

        self.renderer.render_hand(player=self, cards=self.player_cards)
        kind = YesNoKind.SHOOT_BACK if ask_shoot_back else YesNoKind.SHOOT
        return self.renderer.ask_yes_no(player=self, kind=kind)

    def get_card_swap_decision(
        self,
        move_validator: Callable[[Card], bool],
    ) -> Card:
        """
        Asks the player to make a card decision for the Hochzeit swap
        :param move_validator: A function that checks whether the decision by the player is legal
        :type move_validator: Callable[[Card], bool]
        :return: A valid card decision made by the player
        :rtype: Card
        """

        self.renderer.render_hand(player=self, cards=self.player_cards)
        legal_mask = [move_validator(card) for card in self.player_cards]
        index_decision = self.renderer.ask_card(
            player=self,
            player_cards=self.player_cards,
            legal_mask=legal_mask,
            is_swap=True,
        )
        return self.player_cards.pop(index_decision)

    def get_card_play_decision(
        self,
        move_validator: Callable[[Card], bool],
        context: CardPlayContext | None = None,
    ) -> Card:
        """
        Asks the player to make a card decision
        :param move_validator: A function that checks whether the decision by the player is legal
        :type move_validator: Callable[[Card], bool]
        :param context: Information about the game state, used by Bots to make
            informed decisions. Ignored by human players.
        :type context: CardPlayContext | None
        :return: A valid card decision made by the player
        :rtype: Card
        """

        self.renderer.render_hand(player=self, cards=self.player_cards)
        legal_mask = [move_validator(card) for card in self.player_cards]
        index_decision = self.renderer.ask_card(
            player=self, player_cards=self.player_cards, legal_mask=legal_mask
        )
        return self.player_cards.pop(index_decision)


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

    @property
    def is_bot(self) -> bool:
        return True

    def ask_double_game_value(self) -> bool:
        return wants_to_double_game_value(player_cards=self.player_cards)

    def ask_want_choose_game(self, players_who_want_to_play_count: int) -> bool:
        validator = self.game_decision_validator
        return wants_to_play(
            player_cards=self.player_cards,
            players_who_want_to_play_count=players_who_want_to_play_count,
            baseline_mode_playable=(
                validator.is_sauspiel_playable(player_cards=self.player_cards)
                or validator.is_hochzeit_playable(player_cards=self.player_cards)
            ),
        )

    def choose_game_mode(
        self,
        prev_game_mode: type[Game] | None,
        quitting_possible: bool = False,
    ) -> type[Game] | None:
        valid = self.game_decision_validator.get_valid_game_mode_decisions(
            prev_game_mode=prev_game_mode, player_cards=self.player_cards
        )
        return choose_preferred_game_mode(
            player_cards=self.player_cards,
            options=valid,
            can_pass=quitting_possible,
        )

    def get_sau_color(self) -> Color:
        valid = self.game_decision_validator.get_valid_call_sau_color_inputs(
            player_cards=self.player_cards
        )
        return best_sau_color(player_cards=self.player_cards, options=valid)

    def get_trump_color(self) -> Color:
        valid = self.game_decision_validator.get_valid_solo_color_inputs()
        return best_trump_color(player_cards=self.player_cards, options=valid)

    def ask_for_hochzeit(self) -> bool:
        return wants_to_partner_hochzeit(player_cards=self.player_cards)

    def ask_for_ramsch(self) -> bool:
        return wants_to_play_ramsch(player_cards=self.player_cards)

    def get_card_swap_decision(
        self,
        move_validator: Callable[[Card], bool],
    ) -> Card:
        legal_cards = [card for card in self.player_cards if move_validator(card)]
        decision = best_hochzeit_swap_card(
            player_cards=self.player_cards, legal_cards=legal_cards
        )
        self.player_cards.remove(decision)
        return decision

    def get_card_play_decision(
        self,
        move_validator: Callable[[Card], bool],
        context: CardPlayContext | None = None,
    ) -> Card:
        legal_cards = [card for card in self.player_cards if move_validator(card)]
        if context is None:
            decision = random.choice(legal_cards)
        else:
            decision = choose_card_to_play(
                player=self, legal_cards=legal_cards, context=context
            )
        self.player_cards.remove(decision)
        return decision

    def ask_shoot(
        self,
        ask_shoot_back: bool = False,
        trumps: list[Card] | None = None,
        is_tout: bool = False,
        is_ramsch: bool = False,
    ) -> bool:
        return wants_to_shoot(
            player_cards=self.player_cards,
            trumps=trumps or [],
            is_tout=is_tout,
            is_ramsch=is_ramsch,
        )
