"""A pygame-based Renderer implementation.

Game logic (the background thread running Schafkopf.main) talks to this
class exclusively through the Renderer interface (render_*/ask_* methods).
Those methods only ever mutate `self.state` under `self.lock`. The pygame
event/draw loop runs on the main thread in `run()` and reads `self.state`
to draw the table, never touching game objects directly except for the
read-only `Player.money` attribute used for the live money display.
"""

from __future__ import annotations

import os
import random
import threading
import time
import traceback
from typing import TYPE_CHECKING, Any, Callable

import pygame

from card_classes.Cards import Color
from system.Renderer import ColorChoiceKind, Renderer, YesNoKind
from system.gui import constants as c
from system.gui.state import (
    CardSlideAnimation,
    DealAnimation,
    PendingRequest,
    PlayedCardEntry,
    SwapAnimation,
    TableState,
    TrickCollectAnimation,
)
from system.gui.table_view import TableView
from system.text import (
    prompt_ask_for_hochzeit,
    prompt_ask_for_ramsch,
    prompt_ask_player_shoots,
    prompt_ask_player_shoots_back,
    prompt_ask_to_choose_game,
    prompt_ask_to_double_game_value,
    tell_player_chose_game_mode,
    tell_player_doubles_game_value,
    tell_player_hochzeit_partner_decision,
    tell_player_shoots,
    tell_player_wants_to_play,
)

if TYPE_CHECKING:
    from card_classes.Cards import Card
    from game_classes.Game import Game
    from player_classes.Player import Player
    from system.Renderer import GameResult


_YES_NO_PROMPTS: dict[YesNoKind, Callable[[str], str]] = {
    YesNoKind.DOUBLE_GAME_VALUE: prompt_ask_to_double_game_value,
    YesNoKind.CHOOSE_GAME: prompt_ask_to_choose_game,
    YesNoKind.HOCHZEIT: prompt_ask_for_hochzeit,
    YesNoKind.RAMSCH: prompt_ask_for_ramsch,
    YesNoKind.SHOOT: prompt_ask_player_shoots,
    YesNoKind.SHOOT_BACK: prompt_ask_player_shoots_back,
}

_CHOICE_ANNOUNCEMENT_DELAY = 1.6
_FAREWELL_DELAY = 8.0
_SHUFFLE_DURATION = 1.0
_DEAL_CARD_DURATION = 0.12
_SWAP_CARD_DURATION = 0.9
_PLAY_SLIDE_DURATION = 0.22
_TRICK_WINNER_HIGHLIGHT = 1.0
_TRICK_COLLECT_DURATION = 0.35


class GUIRenderer(Renderer):
    """Renders the table with pygame and collects input from the human player."""

    def __init__(self) -> None:
        pygame.init()
        # The real OS window can be freely resized or made fullscreen; the
        # table is always drawn onto a fixed-size logical canvas and then
        # scaled to fit, so the whole absolute layout stays valid at any size.
        self._window = pygame.display.set_mode(
            (c.WINDOW_WIDTH, c.WINDOW_HEIGHT), pygame.RESIZABLE
        )
        self.canvas = pygame.Surface((c.WINDOW_WIDTH, c.WINDOW_HEIGHT))
        pygame.display.set_caption("Schafkopf")
        self.clock = pygame.time.Clock()
        self.fonts = c.Fonts()

        # Maps window coordinates to canvas coordinates (set each frame by
        # _present); identity until the first present.
        self._canvas_scale = 1.0
        self._canvas_offset = (0, 0)
        self._fullscreen = False
        self._windowed_size = (c.WINDOW_WIDTH, c.WINDOW_HEIGHT)

        self.lock = threading.RLock()
        self.state = TableState()
        self.table_view = TableView(
            screen=self.canvas, fonts=self.fonts, state=self.state, lock=self.lock
        )

        self._seat_index: dict[int, int] = {}

        self._input_event = threading.Event()
        self._input_result: Any = None

        self._should_quit = False

    # ------------------------------------------------------------------
    # entry point
    # ------------------------------------------------------------------
    def run(self, target: Callable[[], None]) -> None:
        """Starts the game logic in a background thread and runs the GUI loop."""

        thread = threading.Thread(target=self._run_game, args=(target,), daemon=True)
        thread.start()
        self._main_loop()

    def _run_game(self, target: Callable[[], None]) -> None:
        try:
            target()
        except BaseException:
            traceback.print_exc()
            with self.lock:
                self.state.game_error = "The game crashed - see the console for details."
            self._input_event.set()

    def _main_loop(self) -> None:
        running = True
        while running:
            mouse_pos = self._to_canvas(pygame.mouse.get_pos())
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(mouse_pos)
                elif event.type == pygame.VIDEORESIZE and not self._fullscreen:
                    self._window = pygame.display.set_mode(
                        (event.w, event.h), pygame.RESIZABLE
                    )
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self._toggle_fullscreen()
                    else:
                        self._handle_key(event)
            self.table_view.draw(mouse_pos)
            self._present()
            self.clock.tick(c.FPS)
            with self.lock:
                if self._should_quit:
                    running = False
        pygame.quit()
        os._exit(0)

    def _present(self) -> None:
        """Scales the logical canvas to fit the window (aspect-preserved,
        letterboxed) and shows it. Records the scale/offset so mouse input
        can be mapped back to canvas coordinates."""

        win_w, win_h = self._window.get_size()
        scale = min(win_w / c.WINDOW_WIDTH, win_h / c.WINDOW_HEIGHT)
        draw_w = max(1, int(c.WINDOW_WIDTH * scale))
        draw_h = max(1, int(c.WINDOW_HEIGHT * scale))
        offset = ((win_w - draw_w) // 2, (win_h - draw_h) // 2)
        self._canvas_scale = scale
        self._canvas_offset = offset

        self._window.fill(c.BLACK)
        self._window.blit(pygame.transform.smoothscale(self.canvas, (draw_w, draw_h)), offset)
        pygame.display.flip()

    def _to_canvas(self, pos: tuple[int, int]) -> tuple[int, int]:
        """Maps a window-space position to canvas-space."""

        if self._canvas_scale <= 0:
            return pos
        x = (pos[0] - self._canvas_offset[0]) / self._canvas_scale
        y = (pos[1] - self._canvas_offset[1]) / self._canvas_scale
        return (int(x), int(y))

    def _toggle_fullscreen(self) -> None:
        self._fullscreen = not self._fullscreen
        if self._fullscreen:
            self._windowed_size = self._window.get_size()
            self._window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self._window = pygame.display.set_mode(self._windowed_size, pygame.RESIZABLE)

    # ------------------------------------------------------------------
    # seat assignment
    # ------------------------------------------------------------------
    def set_players(self, players: list[Player]) -> None:
        """Fixes the seating for the whole game (0=bottom/human, 1=left,
        2=top, 3=right), preserving the players' turn order so that the
        next player to act always sits next to the player who just acted.
        """

        human_idx = next(i for i, p in enumerate(players) if not p.is_bot)
        ordered = players[human_idx:] + players[:human_idx]
        with self.lock:
            for i, p in enumerate(ordered):
                self._seat_index[id(p)] = i
                self.state.seat_names[i] = p.player_name
                self.state.seat_players[i] = p

    def _ensure_seat(self, player: Player) -> int:
        """Returns the fixed seat index for a player (set up by set_players)."""

        return self._seat_index[id(player)]

    # ------------------------------------------------------------------
    # Renderer interface - render_* (called from the game thread)
    # ------------------------------------------------------------------
    def render(self, message: str) -> None:
        message = message.strip()
        with self.lock:
            self.state.message = message
            if message:
                # Schafkopf.main() reports "no game was selected" this way -
                # the game-choosing process is over, hide its lamps.
                self.state.game_choice_lamps = {}
        if message:
            time.sleep(0.6)

    def render_farewell(self, message: str) -> None:
        with self.lock:
            self.state.choice_announcement = message.strip()
            self.state.choice_announcement_detail = None
            self.state.choice_announcement_detail_color = None
            self.state.is_farewell = True
        time.sleep(_FAREWELL_DELAY)
        with self.lock:
            self._should_quit = True

    def render_shuffle_cards(self) -> None:
        with self.lock:
            self.state.hand_sizes = [0, 0, 0, 0]
            self.state.human_hand = []
            self.state.shuffle_start_time = time.time()
            self.state.shuffle_duration = _SHUFFLE_DURATION
        time.sleep(_SHUFFLE_DURATION)
        with self.lock:
            self.state.shuffle_start_time = None

    def render_deal_cards(self, players: list[Player], cards_per_player: int) -> None:
        for player in players:
            seat = self._ensure_seat(player)
            for _ in range(cards_per_player):
                with self.lock:
                    self.state.dealing_card = DealAnimation(
                        seat=seat, start_time=time.time(), duration=_DEAL_CARD_DURATION
                    )
                time.sleep(_DEAL_CARD_DURATION)
                with self.lock:
                    self.state.hand_sizes[seat] += 1
                    self.state.dealing_card = None
                    if seat == c.BOTTOM:
                        self._reveal_next_human_card(player)

    def _reveal_next_human_card(self, player: Player) -> None:
        """Reveals the next not-yet-shown card of the human's hand face up,
        keeping the already-revealed cards in their final sorted order.
        """

        for card in player.player_cards:
            if card not in self.state.human_hand:
                self.state.human_hand.append(card)
                break
        self.state.human_hand.sort(key=player.player_cards.index)

    def render_hand(self, player: Player, cards: list[Card]) -> None:
        seat = self._ensure_seat(player)
        with self.lock:
            self.state.hand_sizes[seat] = len(cards)
            if seat == c.BOTTOM:
                self.state.human_hand = list(cards)

    def render_played_card(self, player: Player, card: Card) -> None:
        seat = self._ensure_seat(player)
        if player.is_bot:
            # Mark the bot as the one to act while it "thinks", so the table
            # shows whose turn it is before the card drops.
            with self.lock:
                self.state.active_seat = seat
            time.sleep(random.uniform(0.5, 1.0))
        with self.lock:
            # The card leaves the hand now and slides toward the center; it
            # joins center_cards only once the slide finishes.
            self.state.hand_sizes[seat] = max(0, self.state.hand_sizes[seat] - 1)
            if seat == c.BOTTOM and card in self.state.human_hand:
                self.state.human_hand.remove(card)
            self.state.active_seat = None
            self.state.sliding_card = CardSlideAnimation(
                seat=seat, card=card, start_time=time.time(), duration=_PLAY_SLIDE_DURATION
            )
        time.sleep(_PLAY_SLIDE_DURATION)
        with self.lock:
            self.state.center_cards.append(PlayedCardEntry(seat=seat, card=card))
            self.state.sliding_card = None

    def render_trick_winner(self, winner: Player) -> None:
        seat = self._ensure_seat(winner)
        with self.lock:
            self.state.trick_winner_seat = seat
        time.sleep(_TRICK_WINNER_HIGHLIGHT)
        # Sweep the trick's cards into the winner's pile before clearing.
        with self.lock:
            self.state.trick_collect = TrickCollectAnimation(
                winner_seat=seat,
                start_time=time.time(),
                duration=_TRICK_COLLECT_DURATION,
            )
        time.sleep(_TRICK_COLLECT_DURATION)
        with self.lock:
            self.state.previous_round_cards = list(self.state.center_cards)
            self.state.center_cards.clear()
            self.state.trick_winner_seat = None
            self.state.trick_collect = None

    def render_game_mode(
        self,
        game_mode_name: str | None,
        chooser: Player | None,
        detail: str | None = None,
        detail_color: Color | None = None,
    ) -> None:
        seat = self._ensure_seat(chooser) if chooser is not None else None
        with self.lock:
            self.state.current_game_mode = game_mode_name
            self.state.current_game_mode_chooser_seat = seat
            self.state.current_game_mode_detail = detail
            self.state.current_game_mode_detail_color = detail_color
            if game_mode_name is None and chooser is None:
                # Schafkopf.main() signals the start of a new hand this way -
                # the previous hand's last round is no longer relevant.
                self.state.previous_round_cards = []
                self.state.show_previous_round = False
                # A new game-choosing process starts: show a "pending" lamp
                # next to each bot's avatar.
                self.state.game_choice_lamps = {
                    seat: "pending" for seat in (c.LEFT, c.TOP, c.RIGHT)
                }
            else:
                # A game was chosen - the choosing process is over, hide
                # the lamps immediately.
                self.state.game_choice_lamps = {}

    def render_game_result(self, result: GameResult) -> None:
        with self.lock:
            self.state.game_result = result
            self.state.center_cards.clear()
            self.state.trick_winner_seat = None
            self.state.active_seat = None
            self.state.trick_collect = None
            self.state.message = ""
            # The hand is over - the "show last round" button must not offer
            # this hand's last trick while the player is asked to play again.
            self.state.previous_round_cards = []
            self.state.show_previous_round = False
            # Likewise, the top-left game mode badge must not keep showing
            # this hand's game while the player is asked to play again.
            self.state.current_game_mode = None
            self.state.current_game_mode_chooser_seat = None
            self.state.current_game_mode_detail = None
            self.state.current_game_mode_detail_color = None

    def render_want_to_play_decision(self, player: Player, wants_to_play: bool) -> None:
        seat = self._ensure_seat(player)
        with self.lock:
            if seat in self.state.game_choice_lamps:
                self.state.game_choice_lamps[seat] = "yes" if wants_to_play else "no"
        self._announce_choice(
            tell_player_wants_to_play(
                player_name=player.player_name, wants_to_play=wants_to_play
            )
        )

    def render_double_game_value_decision(self, player: Player, doubles: bool) -> None:
        if doubles:
            self._announce_choice(
                tell_player_doubles_game_value(player_name=player.player_name)
            )

    def render_shoot_decision(
        self, player: Player, shoots: bool, is_shoot_back: bool = False
    ) -> None:
        if shoots:
            self._announce_choice(
                tell_player_shoots(
                    player_name=player.player_name, is_shoot_back=is_shoot_back
                )
            )

    def render_hochzeit_partner_search(self, candidates: list[Player]) -> None:
        # Partner selection is a fresh decision round: show a blue
        # "pending" lamp next to every bot still to be asked.
        candidate_seats = {self._ensure_seat(player) for player in candidates}
        with self.lock:
            self.state.game_choice_lamps = {
                seat: "pending"
                for seat in (c.LEFT, c.TOP, c.RIGHT)
                if seat in candidate_seats
            }

    def render_hochzeit_partner_decision(self, player: Player, accepts: bool) -> None:
        seat = self._ensure_seat(player)
        with self.lock:
            if seat in self.state.game_choice_lamps:
                self.state.game_choice_lamps[seat] = "yes" if accepts else "no"
        self._announce_choice(
            tell_player_hochzeit_partner_decision(
                player_name=player.player_name, accepts=accepts
            )
        )

    def render_hochzeit_card_swap(self, chooser: Player, partner: Player) -> None:
        seat_a = self._ensure_seat(chooser)
        seat_b = self._ensure_seat(partner)
        with self.lock:
            self.state.swap_animation = SwapAnimation(
                seat_a=seat_a,
                seat_b=seat_b,
                start_time=time.time(),
                duration=_SWAP_CARD_DURATION,
            )
        time.sleep(_SWAP_CARD_DURATION)
        with self.lock:
            self.state.swap_animation = None

    def render_game_mode_decision(self, player: Player, game_mode: type[Game] | None) -> None:
        self._announce_choice(
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
        if chooser is not None:
            message = f"{chooser.player_name} chooses {game_mode_name}"
        else:
            message = f"{game_mode_name} is being played"
        self._announce_choice(message, detail=detail, detail_color=detail_color)

    def _announce_choice(
        self, message: str, detail: str | None = None, detail_color: Color | None = None
    ) -> None:
        with self.lock:
            self.state.choice_announcement = message
            self.state.choice_announcement_detail = detail
            self.state.choice_announcement_detail_color = detail_color
        time.sleep(_CHOICE_ANNOUNCEMENT_DELAY)
        with self.lock:
            self.state.choice_announcement = None
            self.state.choice_announcement_detail = None
            self.state.choice_announcement_detail_color = None

    # ------------------------------------------------------------------
    # Renderer interface - ask_* (called from the game thread, blocking)
    # ------------------------------------------------------------------
    def ask_player_name(self) -> str:
        return self._request(kind="player_name", title="Enter your name")

    def ask_prices(
        self, base_price: int, call_price: int, alone_price: int
    ) -> tuple[int, int, int]:
        with self.lock:
            self.state.settings_prices = {
                "Base": base_price,
                "Call": call_price,
                "Alone": alone_price,
            }
        prices: dict[str, int] = self._request(
            kind="prices", title="Set the stakes (cents)"
        )
        with self.lock:
            self.state.settings_prices = None
        return (prices["Base"], prices["Call"], prices["Alone"])

    def ask_play_again(self) -> bool:
        result = self._request(
            kind="play_again",
            options=[("Play again", "again"), ("New match", "new"), ("Quit", "quit")],
        )
        if result == "new":
            # Reset everyone's balance for a fresh match.
            with self.lock:
                for player in self.state.seat_players:
                    if player is not None:
                        player.money = 0
        with self.lock:
            self.state.game_result = None
            self.state.message = ""
        return result in ("again", "new")

    def ask_yes_no(self, player: Player, kind: YesNoKind, allow_yes: bool = True) -> bool:
        prompt = _YES_NO_PROMPTS[kind](player.player_name)
        options: list[tuple[str, Any]] = []
        if allow_yes:
            options.append(("Yes", True))
        options.append(("No", False))
        return self._request(
            kind="yes_no", player_name=player.player_name, title=prompt, options=options
        )

    def ask_game_mode(
        self,
        player: Player,
        options: dict[str, type[Game]],
        quitting_possible: bool,
    ) -> type[Game] | None:
        btn_options: list[tuple[str, Any]] = [
            (game_mode.name, game_mode) for game_mode in options.values()
        ]
        if quitting_possible:
            btn_options.append(("Skip", None))
        title = f"{player.player_name}: Which game do you want to choose?"
        return self._request(
            kind="game_mode",
            player_name=player.player_name,
            title=title,
            options=btn_options,
        )

    def ask_color(
        self, player: Player, options: dict[str, Color], kind: ColorChoiceKind
    ) -> Color:
        btn_options: list[tuple[str, Any]] = [
            (color.display_name, color) for color in options.values()
        ]
        what = "Sau" if kind == ColorChoiceKind.SAU else "trump"
        title = f"{player.player_name}: Which {what} color do you want to play?"
        return self._request(
            kind="color",
            player_name=player.player_name,
            title=title,
            options=btn_options,
        )

    def ask_card(
        self,
        player: Player,
        player_cards: list[Card],
        legal_mask: list[bool],
        is_swap: bool = False,
    ) -> int:
        title = "Choose a card to swap" if is_swap else "Choose a card to play"
        if not is_swap:
            # Playing a card is the human's turn - light up their seat too.
            with self.lock:
                self.state.active_seat = c.BOTTOM
        return self._request(
            kind="card",
            player_name=player.player_name,
            title=title,
            legal_mask=list(legal_mask),
            is_swap=is_swap,
        )

    # ------------------------------------------------------------------
    # blocking request/response plumbing
    # ------------------------------------------------------------------
    def _request(self, kind: str, **kwargs: Any) -> Any:
        request = PendingRequest(kind=kind, **kwargs)
        self._input_event.clear()
        if kind == "player_name":
            self.table_view.reset_text_input()
        with self.lock:
            self.state.pending = request
        self._input_event.wait()
        return self._input_result

    def _submit(self, value: Any) -> None:
        with self.lock:
            self.state.pending = None
        self._input_result = value
        self._input_event.set()

    # ------------------------------------------------------------------
    # input handling (main thread)
    # ------------------------------------------------------------------
    def _handle_click(self, pos: tuple[int, int]) -> None:
        hit_test = self.table_view.hit_test()

        # The in-game menu, when open, captures all clicks.
        with self.lock:
            menu_open = self.state.menu_open
        if menu_open:
            for button in hit_test.menu_buttons:
                if button.is_clicked(pos):
                    if button.value == "quit":
                        with self.lock:
                            self._should_quit = True
                    with self.lock:
                        self.state.menu_open = False
                    return
            return
        if hit_test.menu_button is not None and hit_test.menu_button.is_clicked(pos):
            with self.lock:
                self.state.menu_open = True
            return

        previous_round_button = hit_test.previous_round_button
        if previous_round_button is not None and previous_round_button.is_clicked(pos):
            with self.lock:
                self.state.show_previous_round = not self.state.show_previous_round
            return

        with self.lock:
            show_previous_round = self.state.show_previous_round
            pending = self.state.pending

        if show_previous_round:
            with self.lock:
                self.state.show_previous_round = False
            return

        if pending is None:
            return

        if pending.kind == "card":
            for index, rect in enumerate(hit_test.card_rects):
                if rect.collidepoint(pos) and pending.legal_mask[index]:
                    self._submit(index)
                    return
            return

        if pending.kind == "player_name":
            for button in hit_test.buttons:
                if button.is_clicked(pos):
                    name = self.table_view.text_input_value
                    if name:
                        self._submit(name)
                    return
            return

        if pending.kind == "prices":
            self._handle_prices_click(pos, hit_test.buttons)
            return

        for button in hit_test.buttons:
            if button.is_clicked(pos):
                self._submit(button.value)
                return

    def _handle_prices_click(self, pos: tuple[int, int], buttons: list) -> None:
        for button in buttons:
            if not button.is_clicked(pos):
                continue
            if button.value == "start_game":
                with self.lock:
                    prices = dict(self.state.settings_prices or {})
                self._submit(prices)
            else:
                _, key, delta = button.value
                with self.lock:
                    if self.state.settings_prices is not None:
                        current = self.state.settings_prices[key]
                        self.state.settings_prices[key] = max(
                            c.STAKE_MIN, min(c.STAKE_MAX, current + delta)
                        )
            return

    def _handle_key(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE:
            with self.lock:
                self.state.menu_open = not self.state.menu_open
            return

        with self.lock:
            menu_open = self.state.menu_open
            pending = self.state.pending

        if menu_open or pending is None:
            return

        if pending.kind == "card":
            if pygame.K_1 <= event.key <= pygame.K_9:
                index = event.key - pygame.K_1
                if (
                    pending.legal_mask is not None
                    and index < len(pending.legal_mask)
                    and pending.legal_mask[index]
                ):
                    self._submit(index)
            return

        if pending.kind == "player_name":
            if self.table_view.handle_text_input_event(event):
                name = self.table_view.text_input_value
                if name:
                    self._submit(name)

