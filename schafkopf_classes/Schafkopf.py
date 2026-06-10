from __future__ import annotations
import random
from typing import Any

from system.Renderer import Renderer
from card_classes.Cards import Cards
from player_classes.Player import Player, Bot
from game_classes.Game import Game
from game_classes.game_modes.Hochzeit import Hochzeit
from game_classes.game_modes.Sauspiel import Sauspiel
from game_classes.game_modes.Wenz import Wenz
from game_classes.game_modes.Solo import Solo
from game_classes.game_modes.Ramsch import Ramsch
from game_classes.game_modes.SoloTout import SoloTout
from game_classes.game_modes.WenzTout import WenzTout
from input_validators.GameDecisionValidator import GameDecisionValidator
from card_classes.CardPowerCalculator import SauspielCardPowerCalculator
from game_classes.game_modes.GameRegistry import GameRegistry
from system.custom_exceptions import (
    GameNotPlayableError,
    PlayerIsNotInPlayersListError,
)
from system.text import (
    words_of_thanks,
    no_game_phrase,
)


class Schafkopf:
    def __init__(
        self, renderer: Renderer, base_price: int, call_price: int, alone_price: int
    ) -> None:

        self.cards = Cards()
        self.renderer = renderer
        self.base_price = base_price
        self.call_price = call_price
        self.alone_price = alone_price

        self.players: list[Player] = []
        self.starter: Player | None = None
        self.game_choosers: list[Player] = []
        self.amount_game_value_doubles = 0

        self.implemented_games: list[dict[str, Any]] = (
            GameRegistry.get_game_mapping().copy()
        )
        self.choosable_game_rank_mapping: dict[type[Game], int] = {
            class_dict["class"]: class_dict["rank"]
            for class_dict in self.implemented_games
            if class_dict["is_choosable"]
        }
        self.game_decision_validator: GameDecisionValidator = GameDecisionValidator(
            choosable_game_rank_mapping=self.choosable_game_rank_mapping,
        )

    def _create_players(self) -> list[Player]:
        players: list[Player] = []

        player_name = self.renderer.ask_player_name()
        players.append(
            Player(
                player_name=player_name,
                renderer=self.renderer,
                game_decision_validator=self.game_decision_validator,
            )
        )
        for i in range(3):
            players.append(
                Bot(
                    bot_name=f"Bot {i + 1}",
                    renderer=self.renderer,
                    game_decision_validator=self.game_decision_validator,
                )
            )

        return players

    @staticmethod
    def sort_players(starter: Player, players: list[Player]) -> list[Player]:
        if starter not in players:
            raise PlayerIsNotInPlayersListError(
                "The starting player is not in players list"
            )
        starter_index = players.index(starter)
        players = players[starter_index:] + players[:starter_index]
        return players

    def deal_cards(self, cards_amount_per_player: int) -> None:
        random.shuffle(self.cards.deck)
        for player in self.players:
            player.player_cards.extend(self.cards.deck[-cards_amount_per_player:])
            del self.cards.deck[-cards_amount_per_player:]

    def prepare_cards(self) -> None:
        for player in self.players:
            player.player_cards.clear()
            player.collected_cards.clear()
        self.cards.reset_deck()
        cards_per_dealing_round = len(self.cards.deck) // 2
        cards_per_player_per_dealing_round = cards_per_dealing_round // len(
            self.players
        )
        self.deal_cards(cards_amount_per_player=cards_per_player_per_dealing_round)
        self.sort_player_hands()
        self.amount_game_value_doubles = 0
        for player in self.players:
            if player.ask_double_game_value():
                self.amount_game_value_doubles += 1
        self.deal_cards(cards_amount_per_player=cards_per_player_per_dealing_round)
        self.sort_player_hands()

    def prepare_players(self):
        assert self.starter is not None
        self.players = self.sort_players(starter=self.starter, players=self.players)
        self.game_choosers.clear()

    # sort cards for a Sauspiel -> easier to make game decisions
    def sort_player_hands(self) -> None:
        card_power_calculator = SauspielCardPowerCalculator()
        for player in self.players:
            player.player_cards.sort(
                key=card_power_calculator.get_card_power, reverse=True
            )

    def get_hochzeit_partner(self, game_chooser: Player) -> Player | None:
        temp_players: list[Player] = self.sort_players(
            starter=game_chooser, players=self.players
        )[1:]
        for player in temp_players:
            decision: bool = player.ask_for_hochzeit()
            if decision:
                return player
        return None

    def get_game(self, game_mode: type[Game], chooser: Player | None) -> Game | None:
        try:
            return game_mode(**game_mode.gather_kwargs(chooser=chooser, schafkopf=self))
        except GameNotPlayableError:
            return None

    def players_choose_game(self) -> Game | None:
        game_mode: type[Game] | None = None
        game_chooser: Player | None = None
        if not self.game_choosers:
            play_ramsch: bool = self.players[-1].ask_for_ramsch()
            if play_ramsch:
                return self.get_game(game_mode=Ramsch, chooser=game_chooser)
            else:
                return None
        else:
            for player in self.game_choosers:
                if game_mode is None:
                    decision: type[Game] | None = player.choose_game_mode(
                        prev_game_mode=game_mode,
                    )
                    self.renderer.render_game_mode_decision(
                        player=player, game_mode=decision
                    )
                    game_mode = decision
                    game_chooser = player

                elif (
                    self.choosable_game_rank_mapping[game_mode]
                    > self.choosable_game_rank_mapping[Sauspiel]
                ):
                    decision = player.choose_game_mode(
                        prev_game_mode=game_mode,
                        quitting_possible=True,
                    )
                    self.renderer.render_game_mode_decision(
                        player=player, game_mode=decision
                    )
                    if decision is None:
                        continue
                    else:
                        game_mode = decision
                        game_chooser = player

                else:
                    decision = player.choose_game_mode(
                        prev_game_mode=game_mode,
                        quitting_possible=False,
                    )
                    self.renderer.render_game_mode_decision(
                        player=player, game_mode=decision
                    )
                    game_mode = decision
                    game_chooser = player

                if game_mode is SoloTout:
                    break

        assert game_mode is not None
        return self.get_game(game_mode=game_mode, chooser=game_chooser)

    def get_new_starter(
        self, prev_starter_index: int
    ) -> Player:  # players list rotates each round
        if self.players[prev_starter_index] == self.players[-1]:
            return self.players[0]
        else:
            return self.players[prev_starter_index + 1]

    def main(self) -> None:
        self.players = self._create_players()
        self.renderer.set_players(self.players)
        self.starter: Player = random.choice(self.players)
        while True:
            self.prepare_players()
            self.prepare_cards()
            self.renderer.render_game_mode(game_mode_name=None, chooser=None)
            for player in self.players:
                self.renderer.render_hand(player=player, cards=player.player_cards)
                wants_to_play = player.ask_want_choose_game(
                    players_who_want_to_play_count=len(self.game_choosers)
                )
                self.renderer.render_want_to_play_decision(
                    player=player, wants_to_play=wants_to_play
                )
                if wants_to_play:
                    self.game_choosers.append(player)
            game: Game | None = self.players_choose_game()
            if game is not None:
                self.renderer.render_game_mode(
                    game_mode_name=game.name,
                    chooser=getattr(game, "game_chooser", None),
                    detail=game.display_detail(),
                    detail_color=game.display_detail_color(),
                )
                self.renderer.render_game_mode_announcement(
                    game_mode_name=game.name,
                    chooser=getattr(game, "game_chooser", None),
                    detail=game.display_detail(),
                    detail_color=game.display_detail_color(),
                )
                game.play_game()
            else:
                self.renderer.render(message=no_game_phrase)
            assert self.starter is not None
            self.starter = self.get_new_starter(
                prev_starter_index=self.players.index(self.starter)
            )
            if not self.renderer.ask_play_again():
                break

        self.renderer.render_farewell(message=words_of_thanks)
