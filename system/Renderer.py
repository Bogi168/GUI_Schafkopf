from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum, auto
from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING

from system.text import (
    error_message,
    prompt_player_name,
    prompt_play_again_message,
    prompt_ask_to_double_game_value,
    prompt_ask_to_choose_game,
    prompt_ask_for_hochzeit,
    prompt_ask_for_ramsch,
    prompt_ask_player_shoots,
    prompt_ask_player_shoots_back,
    prompt_choose_game,
    prompt_choose_color,
    prompt_ask_play_card_decision,
    prompt_ask_swap_card_decision,
    show_player_cards,
    show_played_card,
    show_collector_of_cards,
    tell_chosen_game_mode,
    tell_player_wants_to_play,
    tell_player_chose_game_mode,
    tell_game_mode_announcement,
    tell_most_point_teams,
    tell_team_points,
    tell_team_players,
    tell_winners,
    tell_game_value_calculation,
    tell_player_money,
)

if TYPE_CHECKING:
    from card_classes.Cards import Card, Color
    from player_classes.Player import Player
    from player_classes.Team import Team
    from game_classes.Game import Game


class YesNoKind(Enum):
    """Identifies the context of a yes/no question asked to a player."""

    DOUBLE_GAME_VALUE = auto()
    CHOOSE_GAME = auto()
    HOCHZEIT = auto()
    RAMSCH = auto()
    SHOOT = auto()
    SHOOT_BACK = auto()


class ColorChoiceKind(Enum):
    """Identifies the context of a color choice asked to a player."""

    SAU = auto()
    TRUMP = auto()


@dataclass
class GameResult:
    """A summary of a finished game, ready to be displayed to the players."""

    most_point_teams: list[Team]
    winners: list[Player]
    game_value: int
    game_value_breakdown: str
    players: list[Player]


class Renderer(ABC):
    """An object that renders information and collects player decisions."""

    @abstractmethod
    def render(self, message: str) -> None:
        pass

    @abstractmethod
    def render_farewell(self, message: str) -> None:
        pass

    @abstractmethod
    def render_shuffle_cards(self) -> None:
        pass

    @abstractmethod
    def render_deal_cards(self, players: list[Player], cards_per_player: int) -> None:
        pass

    @abstractmethod
    def render_hand(self, player: Player, cards: list[Card]) -> None:
        pass

    @abstractmethod
    def render_played_card(self, player: Player, card: Card) -> None:
        pass

    @abstractmethod
    def render_trick_winner(self, winner: Player) -> None:
        pass

    @abstractmethod
    def render_game_result(self, result: GameResult) -> None:
        pass

    @abstractmethod
    def render_game_mode(
        self,
        game_mode_name: str | None,
        chooser: Player | None,
        detail: str | None = None,
        detail_color: Color | None = None,
    ) -> None:
        pass

    @abstractmethod
    def set_players(self, players: list[Player]) -> None:
        pass

    @abstractmethod
    def render_want_to_play_decision(self, player: Player, wants_to_play: bool) -> None:
        pass

    @abstractmethod
    def render_game_mode_decision(self, player: Player, game_mode: type[Game] | None) -> None:
        pass

    @abstractmethod
    def render_game_mode_announcement(
        self,
        game_mode_name: str,
        chooser: Player | None,
        detail: str | None = None,
        detail_color: Color | None = None,
    ) -> None:
        pass

    @abstractmethod
    def ask_player_name(self) -> str:
        pass

    @abstractmethod
    def ask_play_again(self) -> bool:
        pass

    @abstractmethod
    def ask_yes_no(self, player: Player, kind: YesNoKind, allow_yes: bool = True) -> bool:
        pass

    @abstractmethod
    def ask_game_mode(
        self,
        player: Player,
        options: dict[str, type[Game]],
        quitting_possible: bool,
    ) -> type[Game] | None:
        pass

    @abstractmethod
    def ask_color(
        self, player: Player, options: dict[str, Color], kind: ColorChoiceKind
    ) -> Color:
        pass

    @abstractmethod
    def ask_card(
        self,
        player: Player,
        player_cards: list[Card],
        legal_mask: list[bool],
        is_swap: bool = False,
    ) -> int:
        pass


class ConsoleRenderer(Renderer):
    _yes_decisions: tuple[str, ...] = ("Y", "YES")
    _no_decisions: tuple[str, ...] = ("N", "NO")
    _quit_decisions: tuple[str, ...] = ("Q", "QUIT")

    _yes_no_prompts: dict[YesNoKind, Callable[[str], str]] = {
        YesNoKind.DOUBLE_GAME_VALUE: prompt_ask_to_double_game_value,
        YesNoKind.CHOOSE_GAME: prompt_ask_to_choose_game,
        YesNoKind.HOCHZEIT: prompt_ask_for_hochzeit,
        YesNoKind.RAMSCH: prompt_ask_for_ramsch,
        YesNoKind.SHOOT: prompt_ask_player_shoots,
        YesNoKind.SHOOT_BACK: prompt_ask_player_shoots_back,
    }

    @staticmethod
    def _ask(
        prompt: str,
        preprocess: Callable[[str], str],
        validator: Callable[[str], bool],
    ) -> str:
        raw_input = input(prompt)
        processed_input = preprocess(raw_input)
        while not validator(processed_input):
            raw_input = input(f"{error_message} {prompt}")
            processed_input = preprocess(raw_input)
        return processed_input

    def render(self, message: str) -> None:
        print(message)

    def render_farewell(self, message: str) -> None:
        print(message.strip())

    def render_shuffle_cards(self) -> None:
        pass

    def render_deal_cards(self, players: list[Player], cards_per_player: int) -> None:
        pass

    def render_hand(self, player: Player, cards: list[Card]) -> None:
        print(show_player_cards(player_name=player.player_name, player_cards=cards))

    def render_played_card(self, player: Player, card: Card) -> None:
        print(show_played_card(player_name=player.player_name, decision=card))

    def render_trick_winner(self, winner: Player) -> None:
        print(
            show_collector_of_cards(
                player_name=winner.player_name, collected_cards=winner.collected_cards
            )
        )

    def render_game_mode(
        self,
        game_mode_name: str | None,
        chooser: Player | None,
        detail: str | None = None,
        detail_color: Color | None = None,
    ) -> None:
        if game_mode_name is not None:
            print(
                tell_chosen_game_mode(
                    game_name=game_mode_name,
                    chooser_name=chooser.player_name if chooser is not None else None,
                    detail=detail,
                )
            )

    def set_players(self, players: list[Player]) -> None:
        pass

    def render_want_to_play_decision(self, player: Player, wants_to_play: bool) -> None:
        print(
            tell_player_wants_to_play(
                player_name=player.player_name, wants_to_play=wants_to_play
            )
        )

    def render_game_mode_decision(self, player: Player, game_mode: type[Game] | None) -> None:
        print(
            tell_player_chose_game_mode(
                player_name=player.player_name, game_mode=game_mode
            )
        )

    def render_game_mode_announcement(
        self,
        game_mode_name: str,
        chooser: Player | None,
        detail: str | None = None,
        detail_color: Color | None = None,
    ) -> None:
        print(
            tell_game_mode_announcement(
                game_mode_name=game_mode_name,
                chooser_name=chooser.player_name if chooser is not None else None,
                detail=detail,
            )
        )

    def render_game_result(self, result: GameResult) -> None:
        if result.most_point_teams:
            print(tell_most_point_teams(most_point_teams=result.most_point_teams))
            for team in result.most_point_teams:
                print(tell_team_points(team_name=team.team_name, points=team.points))
                print(tell_team_players(team_name=team.team_name, players=team.players))
        print(tell_winners(winners=result.winners))
        print(
            tell_game_value_calculation(
                breakdown=result.game_value_breakdown, game_value=result.game_value
            )
        )
        for player in result.players:
            print(tell_player_money(player_name=player.player_name, money=player.money))

    def ask_player_name(self) -> str:
        return self._ask(
            prompt=prompt_player_name,
            preprocess=lambda x: x.strip().capitalize(),
            validator=lambda x: x != "",
        )

    def ask_play_again(self) -> bool:
        decision = self._ask(
            prompt=prompt_play_again_message,
            preprocess=lambda x: x.strip().upper(),
            validator=lambda x: x in self._yes_decisions + self._no_decisions,
        )
        return decision in self._yes_decisions

    def ask_yes_no(self, player: Player, kind: YesNoKind, allow_yes: bool = True) -> bool:
        legal_decisions = (
            self._yes_decisions + self._no_decisions if allow_yes else self._no_decisions
        )
        decision = self._ask(
            prompt=self._yes_no_prompts[kind](player.player_name),
            preprocess=lambda x: x.strip().upper(),
            validator=lambda x: x in legal_decisions,
        )
        return decision in self._yes_decisions

    def ask_game_mode(
        self,
        player: Player,
        options: dict[str, type[Game]],
        quitting_possible: bool,
    ) -> type[Game] | None:
        decision = self._ask(
            prompt=prompt_choose_game(
                player_name=player.player_name,
                quitting_possible=quitting_possible,
                possible_game_mode_decisions=options,
            ),
            preprocess=lambda x: x.strip().upper(),
            validator=lambda x: x in options.keys()
            or (x in self._quit_decisions and quitting_possible),
        )
        if decision in self._quit_decisions:
            return None
        return options[decision]

    def ask_color(
        self, player: Player, options: dict[str, Color], kind: ColorChoiceKind
    ) -> Color:
        decision = self._ask(
            prompt=prompt_choose_color(player_name=player.player_name, valid_colors=options),
            preprocess=lambda x: x.strip(),
            validator=lambda x: x in options,
        )
        return options[decision]

    def ask_card(
        self,
        player: Player,
        player_cards: list[Card],
        legal_mask: list[bool],
        is_swap: bool = False,
    ) -> int:
        if is_swap:
            prompt = prompt_ask_swap_card_decision(
                player_name=player.player_name, legal_mask=legal_mask
            )
        else:
            prompt = prompt_ask_play_card_decision(
                player_name=player.player_name, player_cards=player_cards
            )

        def is_valid(decision: str) -> bool:
            return (
                decision.isdigit()
                and 1 <= int(decision) <= len(player_cards)
                and legal_mask[int(decision) - 1]
            )

        decision = self._ask(prompt=prompt, preprocess=lambda x: x.strip(), validator=is_valid)
        return int(decision) - 1
