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
from system.gui.bot_images import get_bot_image
from system.gui.cards import draw_card_back, draw_card_face
from system.gui.state import PendingRequest, PlayedCardEntry, TableState
from system.gui.suit_images import get_suit_image
from system.gui.widgets import Button, TextInput
from system.text import (
    prompt_ask_for_hochzeit,
    prompt_ask_for_ramsch,
    prompt_ask_player_shoots,
    prompt_ask_player_shoots_back,
    prompt_ask_to_choose_game,
    prompt_ask_to_double_game_value,
    tell_player_chose_game_mode,
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
_FAREWELL_DELAY = 5.0

_FAREWELL_SUITS = [Color.EICHEL, Color.GRUEN, Color.HERZ, Color.SCHELLEN]


class GUIRenderer(Renderer):
    """Renders the table with pygame and collects input from the human player."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((c.WINDOW_WIDTH, c.WINDOW_HEIGHT))
        pygame.display.set_caption("Schafkopf")
        self.clock = pygame.time.Clock()
        self.fonts = c.Fonts()

        self.lock = threading.RLock()
        self.state = TableState()

        self._seat_index: dict[str, int] = {}

        self._input_event = threading.Event()
        self._input_result: Any = None
        self._game_error: str | None = None

        self._current_buttons: list[Button] = []
        self._current_card_rects: list[pygame.Rect] = []
        self._previous_round_button: Button | None = None
        self._text_input = TextInput(rect=pygame.Rect(0, 0, 1, 1))
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
                self._game_error = "The game crashed - see the console for details."
            self._input_event.set()

    def _main_loop(self) -> None:
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(mouse_pos)
                elif event.type == pygame.KEYDOWN:
                    self._handle_key(event)
            self._draw(mouse_pos)
            pygame.display.flip()
            self.clock.tick(c.FPS)
            with self.lock:
                if self._should_quit:
                    running = False
        pygame.quit()
        os._exit(0)

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
                self._seat_index[p.player_name] = i
                self.state.seat_names[i] = p.player_name
                self.state.seat_players[i] = p

    def _ensure_seat(self, player: Player) -> int:
        """Returns the fixed seat index for a player (set up by set_players)."""

        return self._seat_index[player.player_name]

    # ------------------------------------------------------------------
    # Renderer interface - render_* (called from the game thread)
    # ------------------------------------------------------------------
    def render(self, message: str) -> None:
        message = message.strip()
        with self.lock:
            self.state.message = message
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

    def render_hand(self, player: Player, cards: list[Card]) -> None:
        seat = self._ensure_seat(player)
        with self.lock:
            self.state.hand_sizes[seat] = len(cards)
            if seat == c.BOTTOM:
                self.state.human_hand = list(cards)

    def render_played_card(self, player: Player, card: Card) -> None:
        seat = self._ensure_seat(player)
        if player.is_bot:
            time.sleep(random.uniform(0.5, 1.0))
        with self.lock:
            self.state.center_cards.append(PlayedCardEntry(seat=seat, card=card))
            self.state.hand_sizes[seat] = max(0, self.state.hand_sizes[seat] - 1)
            if seat == c.BOTTOM and card in self.state.human_hand:
                self.state.human_hand.remove(card)

    def render_trick_winner(self, winner: Player) -> None:
        seat = self._ensure_seat(winner)
        with self.lock:
            self.state.trick_winner_seat = seat
        time.sleep(1.0)
        with self.lock:
            self.state.previous_round_cards = list(self.state.center_cards)
            self.state.center_cards.clear()
            self.state.trick_winner_seat = None

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

    def render_game_result(self, result: GameResult) -> None:
        with self.lock:
            self.state.game_result = result
            self.state.center_cards.clear()
            self.state.trick_winner_seat = None
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
        self._announce_choice(
            tell_player_wants_to_play(
                player_name=player.player_name, wants_to_play=wants_to_play
            )
        )

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

    def ask_play_again(self) -> bool:
        result: bool = self._request(
            kind="play_again",
            options=[("Play again", True), ("Quit", False)],
        )
        with self.lock:
            self.state.game_result = None
            self.state.message = ""
        return result

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
            self._text_input.text = ""
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
        if self._previous_round_button is not None and self._previous_round_button.is_clicked(pos):
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
            for index, rect in enumerate(self._current_card_rects):
                if rect.collidepoint(pos) and pending.legal_mask[index]:
                    self._submit(index)
                    return
            return

        if pending.kind == "player_name":
            for button in self._current_buttons:
                if button.is_clicked(pos):
                    name = self._text_input.text.strip().capitalize()
                    if name:
                        self._submit(name)
                    return
            return

        for button in self._current_buttons:
            if button.is_clicked(pos):
                self._submit(button.value)
                return

    def _handle_key(self, event: pygame.event.Event) -> None:
        with self.lock:
            pending = self.state.pending

        if pending is None:
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
            if self._text_input.handle_event(event):
                name = self._text_input.text.strip().capitalize()
                if name:
                    self._submit(name)

    # ------------------------------------------------------------------
    # drawing (main thread)
    # ------------------------------------------------------------------
    def _draw(self, mouse_pos: tuple[int, int]) -> None:
        self._current_buttons = []
        self._current_card_rects = []
        with self.lock:
            self.screen.fill(c.TABLE_GREEN)
            pygame.draw.rect(
                self.screen,
                c.TABLE_GREEN_DARK,
                pygame.Rect(20, 20, c.WINDOW_WIDTH - 40, c.WINDOW_HEIGHT - 40),
                width=4,
                border_radius=30,
            )

            self._draw_bot_seat(c.LEFT, mouse_pos)
            self._draw_bot_seat(c.TOP, mouse_pos)
            self._draw_bot_seat(c.RIGHT, mouse_pos)
            self._draw_human_seat()
            self._draw_center()
            self._draw_game_mode_badge()

            if self.state.choice_announcement:
                if self.state.is_farewell:
                    self._draw_farewell()
                else:
                    self._draw_choice_announcement()
            if self.state.message:
                self._draw_message()
            if self.state.game_result is not None:
                self._draw_result_panel()
            if self.state.pending is not None:
                self._draw_pending(mouse_pos)
            if self.state.show_previous_round:
                self._draw_previous_round()
            self._draw_previous_round_button(mouse_pos)
            if self._game_error:
                self._draw_error()

    def _draw_bot_seat(self, seat: int, mouse_pos: tuple[int, int]) -> None:
        avatar_pos = c.SEAT_AVATAR_POS[seat]
        name_pos = c.SEAT_NAME_POS[seat]
        name = self.state.seat_names[seat]

        avatar_rect = pygame.Rect(0, 0, c.AVATAR_SIZE, c.AVATAR_SIZE)
        avatar_rect.center = avatar_pos

        if self.state.trick_winner_seat == seat:
            pygame.draw.rect(self.screen, c.HIGHLIGHT, avatar_rect.inflate(8, 8), width=4, border_radius=8)

        image = get_bot_image(name, c.AVATAR_SIZE)
        if image is not None:
            self.screen.blit(image, avatar_rect)

        label = name or "..."
        player = self.state.seat_players[seat]
        if player is not None:
            label = f"{name} ({player.money}¢)"
        name_surf = self.fonts.name.render(label, True, c.TEXT_LIGHT)
        self.screen.blit(name_surf, name_surf.get_rect(center=name_pos))

        # hidden hand, shown as fanned card backs
        amount = self.state.hand_sizes[seat]
        center_x, center_y = c.SEAT_HAND_CENTER[seat]
        width, height = c.BACK_CARD_SIZE
        spacing = 24
        if c.SEAT_HAND_ORIENTATION[seat] == c.HORIZONTAL:
            total_width = spacing * (amount - 1) + width if amount else 0
            start_x = center_x - total_width // 2
            for i in range(amount):
                rect = pygame.Rect(start_x + i * spacing, center_y - height // 2, width, height)
                draw_card_back(self.screen, rect)
        else:
            total_height = spacing * (amount - 1) + height if amount else 0
            start_y = center_y - total_height // 2
            for i in range(amount):
                rect = pygame.Rect(center_x - width // 2, start_y + i * spacing, width, height)
                draw_card_back(self.screen, rect)

    def _draw_human_seat(self) -> None:
        name = self.state.seat_names[c.BOTTOM] or "You"
        player = self.state.seat_players[c.BOTTOM]
        label = name if player is None else f"{name} ({player.money}¢)"
        name_pos = c.SEAT_NAME_POS[c.BOTTOM]
        name_surf = self.fonts.name.render(label, True, c.TEXT_LIGHT)
        if self.state.trick_winner_seat == c.BOTTOM:
            highlight_rect = name_surf.get_rect(center=name_pos).inflate(24, 12)
            pygame.draw.rect(self.screen, c.HIGHLIGHT, highlight_rect, border_radius=8)
        self.screen.blit(name_surf, name_surf.get_rect(center=name_pos))

        cards = self.state.human_hand
        rects = self._hand_card_rects(len(cards))
        pending = self.state.pending
        legal_mask = pending.legal_mask if pending and pending.kind == "card" else None
        for index, (card, rect) in enumerate(zip(cards, rects)):
            dim = legal_mask is not None and not legal_mask[index]
            draw_card_face(self.screen, rect, card, self.fonts, dim=dim)
        if legal_mask is not None:
            self._current_card_rects = rects

    def _draw_center(self) -> None:
        for entry in self.state.center_cards:
            rect = self._center_card_rect(entry.seat)
            draw_card_face(self.screen, rect, entry.card, self.fonts)

    def _draw_game_mode_badge(self) -> None:
        game_mode = self.state.current_game_mode
        if game_mode is None:
            return

        chooser_seat = self.state.current_game_mode_chooser_seat
        if chooser_seat is not None:
            chooser_name = self.state.seat_names[chooser_seat] or "?"
            text = f"{game_mode} - {chooser_name}"
        else:
            text = game_mode

        detail = self.state.current_game_mode_detail
        detail_color = self.state.current_game_mode_detail_color

        suffix = None
        if detail is not None and detail_color is not None:
            color_name = detail_color.display_name
            if detail.startswith(color_name):
                suffix = detail[len(color_name):].strip()

        if detail is not None and suffix is None:
            text += f" ({detail})"
            detail_color = None

        pieces: list[pygame.Surface] = [self.fonts.body.render(text, True, c.TEXT_LIGHT)]
        if detail_color is not None:
            pieces.append(self.fonts.body.render(" (", True, c.TEXT_LIGHT))
            pieces.append(get_suit_image(detail_color, height=20))
            pieces.append(self.fonts.body.render(f" {suffix})", True, c.TEXT_LIGHT))

        total_width = sum(piece.get_width() for piece in pieces)
        height = max(piece.get_height() for piece in pieces)
        rect = pygame.Rect(36, 36, total_width, height)
        bg = pygame.Surface(rect.inflate(20, 12).size, pygame.SRCALPHA)
        bg.fill((0, 0, 0, 140))
        self.screen.blit(bg, rect.inflate(20, 12).topleft)

        x = rect.x
        for piece in pieces:
            self.screen.blit(piece, (x, rect.centery - piece.get_height() // 2))
            x += piece.get_width()

    def _draw_choice_announcement(self) -> None:
        text = self.state.choice_announcement
        assert text is not None
        detail = self.state.choice_announcement_detail
        detail_color = self.state.choice_announcement_detail_color
        font = self.fonts.announcement

        pieces: list[pygame.Surface] = [font.render(text, True, c.TEXT_LIGHT)]
        if detail is not None:
            suffix = None
            if detail_color is not None and detail.startswith(detail_color.display_name):
                suffix = detail[len(detail_color.display_name):].strip()

            if suffix is not None:
                assert detail_color is not None
                pieces.append(font.render(" (", True, c.TEXT_LIGHT))
                pieces.append(get_suit_image(detail_color, height=font.get_height()))
                pieces.append(font.render(f" {suffix})", True, c.TEXT_LIGHT))
            else:
                pieces.append(font.render(f" ({detail})", True, c.TEXT_LIGHT))

        total_width = sum(piece.get_width() for piece in pieces)
        height = max(piece.get_height() for piece in pieces)
        rect = pygame.Rect(0, 0, total_width, height)
        rect.center = (c.WINDOW_WIDTH // 2, c.WINDOW_HEIGHT // 2)
        bg_rect = rect.inflate(60, 36)
        bg = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg.fill((0, 0, 0, 170))
        self.screen.blit(bg, bg_rect.topleft)

        x = rect.x
        for piece in pieces:
            self.screen.blit(piece, (x, rect.centery - piece.get_height() // 2))
            x += piece.get_width()

    def _draw_farewell(self) -> None:
        text = self.state.choice_announcement
        assert text is not None

        overlay = pygame.Surface((c.WINDOW_WIDTH, c.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*c.OVERLAY_COLOR, c.OVERLAY_ALPHA))
        self.screen.blit(overlay, (0, 0))

        title_surf = self.fonts.announcement.render(text, True, c.TEXT_DARK)
        subtitle_surf = self.fonts.heading.render("See you next time!", True, c.TEXT_DIM)
        suit_imgs = [get_suit_image(color, height=40) for color in _FAREWELL_SUITS]
        suit_spacing = 24
        suits_width = sum(img.get_width() for img in suit_imgs) + suit_spacing * (len(suit_imgs) - 1)

        content_width = max(title_surf.get_width(), subtitle_surf.get_width(), suits_width)
        content_height = (
            suit_imgs[0].get_height()
            + 28
            + title_surf.get_height()
            + 14
            + subtitle_surf.get_height()
        )

        panel_rect = pygame.Rect(0, 0, content_width + 100, content_height + 70)
        panel_rect.center = (c.WINDOW_WIDTH // 2, c.WINDOW_HEIGHT // 2)
        pygame.draw.rect(self.screen, c.PANEL_BG, panel_rect, border_radius=24)
        pygame.draw.rect(self.screen, c.HIGHLIGHT, panel_rect, width=5, border_radius=24)

        x = panel_rect.centerx - suits_width // 2
        y = panel_rect.top + 30
        for img in suit_imgs:
            self.screen.blit(img, (x, y))
            x += img.get_width() + suit_spacing
        y += suit_imgs[0].get_height() + 28

        self.screen.blit(title_surf, title_surf.get_rect(midtop=(panel_rect.centerx, y)))
        y += title_surf.get_height() + 14

        self.screen.blit(subtitle_surf, subtitle_surf.get_rect(midtop=(panel_rect.centerx, y)))

    def _draw_message(self) -> None:
        surf = self.fonts.body.render(self.state.message, True, c.TEXT_LIGHT)
        rect = surf.get_rect(midtop=(c.WINDOW_WIDTH // 2, 8))
        bg = pygame.Surface(rect.inflate(24, 12).size, pygame.SRCALPHA)
        bg.fill((0, 0, 0, 140))
        self.screen.blit(bg, rect.inflate(24, 12).topleft)
        self.screen.blit(surf, rect)

    def _draw_error(self) -> None:
        surf = self.fonts.body.render(f"Error: {self._game_error}", True, (255, 90, 90))
        rect = surf.get_rect(midbottom=(c.WINDOW_WIDTH // 2, c.WINDOW_HEIGHT - 8))
        self.screen.blit(surf, rect)

    def _draw_previous_round(self) -> None:
        overlay = pygame.Surface((c.WINDOW_WIDTH, c.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*c.OVERLAY_COLOR, 130))
        self.screen.blit(overlay, (0, 0))

        label_surf = self.fonts.heading.render(
            "Last round - click anywhere to close", True, c.TEXT_LIGHT
        )
        label_rect = label_surf.get_rect(midtop=(c.WINDOW_WIDTH // 2, 8))
        bg = pygame.Surface(label_rect.inflate(24, 12).size, pygame.SRCALPHA)
        bg.fill((0, 0, 0, 140))
        self.screen.blit(bg, label_rect.inflate(24, 12).topleft)
        self.screen.blit(label_surf, label_rect)

        for entry in self.state.previous_round_cards:
            rect = self._center_card_rect(entry.seat)
            draw_card_face(self.screen, rect, entry.card, self.fonts)

    def _draw_previous_round_button(self, mouse_pos: tuple[int, int]) -> None:
        if not self.state.previous_round_cards:
            self._previous_round_button = None
            return

        label = "Hide last round" if self.state.show_previous_round else "Show last round"
        button = Button(
            rect=c.PREVIOUS_ROUND_BUTTON_RECT,
            label=label,
        )
        button.draw(self.screen, self.fonts, mouse_pos)
        self._previous_round_button = button

    # ------------------------------------------------------------------
    # modal dialogs
    # ------------------------------------------------------------------
    def _draw_pending(self, mouse_pos: tuple[int, int]) -> None:
        pending = self.state.pending
        assert pending is not None

        if pending.kind == "card":
            banner = self.fonts.heading.render(pending.title, True, c.TEXT_LIGHT)
            rect = banner.get_rect(midtop=(c.WINDOW_WIDTH // 2, 8))
            bg = pygame.Surface(rect.inflate(24, 12).size, pygame.SRCALPHA)
            bg.fill((0, 0, 0, 140))
            self.screen.blit(bg, rect.inflate(24, 12).topleft)
            self.screen.blit(banner, rect)
            return

        if pending.kind == "play_again":
            self._draw_play_again_buttons(mouse_pos)
            return

        overlay = pygame.Surface((c.WINDOW_WIDTH, c.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*c.OVERLAY_COLOR, c.OVERLAY_ALPHA))
        self.screen.blit(overlay, (0, 0))

        if pending.kind == "player_name":
            self._draw_player_name_panel()
        else:
            self._draw_choice_panel(pending, mouse_pos)

    def _draw_choice_panel(self, pending: PendingRequest, mouse_pos: tuple[int, int]) -> None:
        amount = len(pending.options)
        btn_w, btn_h, gap = 200, 50, 16
        cols = min(amount, 3) or 1
        rows = (amount + cols - 1) // cols

        btn_panel_w = cols * (btn_w + gap) + gap
        text_max_width = max(360, btn_panel_w) - 40
        title_lines = self._wrap_text(pending.title, self.fonts.heading, text_max_width)
        text_w = max(self.fonts.heading.size(line)[0] for line in title_lines)

        panel_w = max(360, btn_panel_w, text_w + 40)
        panel_h = 60 + len(title_lines) * 32 + rows * (btn_h + gap) + gap
        panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
        panel_rect.center = (c.WINDOW_WIDTH // 2, c.WINDOW_HEIGHT // 2)
        pygame.draw.rect(self.screen, c.PANEL_BG, panel_rect, border_radius=12)
        pygame.draw.rect(self.screen, c.PANEL_BORDER, panel_rect, width=2, border_radius=12)

        y = panel_rect.top + 30
        for line in title_lines:
            surf = self.fonts.heading.render(line, True, c.TEXT_DARK)
            self.screen.blit(surf, surf.get_rect(midtop=(panel_rect.centerx, y)))
            y += 32

        y += 8
        grid_w = cols * (btn_w + gap) - gap
        start_x = panel_rect.centerx - grid_w // 2
        for index, (label, value) in enumerate(pending.options):
            col = index % cols
            row = index // cols
            rect = pygame.Rect(start_x + col * (btn_w + gap), y + row * (btn_h + gap), btn_w, btn_h)
            image = get_suit_image(value, height=btn_h - 16) if pending.kind == "color" else None
            button = Button(rect=rect, label=label, value=value, image=image)
            button.draw(self.screen, self.fonts, mouse_pos)
            self._current_buttons.append(button)

    def _draw_player_name_panel(self) -> None:
        panel_rect = pygame.Rect(0, 0, 460, 200)
        panel_rect.center = (c.WINDOW_WIDTH // 2, c.WINDOW_HEIGHT // 2)
        pygame.draw.rect(self.screen, c.PANEL_BG, panel_rect, border_radius=12)
        pygame.draw.rect(self.screen, c.PANEL_BORDER, panel_rect, width=2, border_radius=12)

        title_surf = self.fonts.heading.render("Welcome! Enter your name:", True, c.TEXT_DARK)
        self.screen.blit(
            title_surf, title_surf.get_rect(midtop=(panel_rect.centerx, panel_rect.top + 24))
        )

        self._text_input.rect = pygame.Rect(0, 0, 300, 44)
        self._text_input.rect.center = (panel_rect.centerx, panel_rect.centery + 5)
        self._text_input.draw(self.screen, self.fonts)

        ok_rect = pygame.Rect(0, 0, 120, 40)
        ok_rect.midtop = (panel_rect.centerx, panel_rect.bottom - 56)
        ok_button = Button(rect=ok_rect, label="OK", enabled=bool(self._text_input.text.strip()))
        ok_button.draw(self.screen, self.fonts, pygame.mouse.get_pos())
        self._current_buttons.append(ok_button)

    def _draw_play_again_buttons(self, mouse_pos: tuple[int, int]) -> None:
        pending = self.state.pending
        assert pending is not None
        panel_rect = self._result_panel_rect()
        btn_w, btn_h, gap = 160, 46, 24
        total_w = len(pending.options) * btn_w + (len(pending.options) - 1) * gap
        start_x = panel_rect.centerx - total_w // 2
        y = panel_rect.bottom - btn_h - 20
        for index, (label, value) in enumerate(pending.options):
            rect = pygame.Rect(start_x + index * (btn_w + gap), y, btn_w, btn_h)
            button = Button(rect=rect, label=label, value=value)
            button.draw(self.screen, self.fonts, mouse_pos)
            self._current_buttons.append(button)

    # ------------------------------------------------------------------
    # game result screen
    # ------------------------------------------------------------------
    @staticmethod
    def _result_panel_rect() -> pygame.Rect:
        rect = pygame.Rect(0, 0, 640, 560)
        rect.center = (c.WINDOW_WIDTH // 2, c.WINDOW_HEIGHT // 2)
        return rect

    def _draw_result_panel(self) -> None:
        result = self.state.game_result
        assert result is not None

        overlay = pygame.Surface((c.WINDOW_WIDTH, c.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*c.OVERLAY_COLOR, c.OVERLAY_ALPHA))
        self.screen.blit(overlay, (0, 0))

        panel_rect = self._result_panel_rect()
        pygame.draw.rect(self.screen, c.PANEL_BG, panel_rect, border_radius=14)
        pygame.draw.rect(self.screen, c.PANEL_BORDER, panel_rect, width=2, border_radius=14)

        x = panel_rect.left + 30
        y = panel_rect.top + 20

        title_surf = self.fonts.title.render("Game Result", True, c.TEXT_DARK)
        self.screen.blit(title_surf, title_surf.get_rect(midtop=(panel_rect.centerx, y)))
        y += 50

        for team in result.most_point_teams:
            player_names = ", ".join(player.player_name for player in team.players)
            line = f"{team.team_name}: {team.points} points ({player_names})"
            self.screen.blit(self.fonts.body.render(line, True, c.TEXT_DARK), (x, y))
            y += 26

        y += 6
        if len(result.winners) == 1:
            winners_line = f"Winner: {result.winners[0].player_name}"
        else:
            winners_line = "Winners: " + ", ".join(p.player_name for p in result.winners)
        self.screen.blit(self.fonts.heading.render(winners_line, True, c.TEXT_DARK), (x, y))
        y += 36

        for line in result.game_value_breakdown.split("\n"):
            line = line.strip()
            if line:
                self.screen.blit(self.fonts.body.render(line, True, c.TEXT_DARK), (x, y))
                y += 24

        y += 6
        value_surf = self.fonts.heading.render(
            f"Game value: {result.game_value} cents", True, c.TEXT_DARK
        )
        self.screen.blit(value_surf, (x, y))
        y += 44

        pygame.draw.rect(self.screen, c.PANEL_BORDER, pygame.Rect(x, y, panel_rect.width - 60, 2))
        y += 16

        for player in result.players:
            line = f"{player.player_name}: {player.money} cents"
            self.screen.blit(self.fonts.body.render(line, True, c.TEXT_DARK), (x, y))
            y += 26

    # ------------------------------------------------------------------
    # layout helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _hand_card_rects(amount: int) -> list[pygame.Rect]:
        if amount == 0:
            return []
        width, height = c.HAND_CARD_SIZE
        spacing = min(width + 10, (c.WINDOW_WIDTH - 80) // amount)
        total_width = spacing * (amount - 1) + width
        start_x = (c.WINDOW_WIDTH - total_width) // 2
        y = c.WINDOW_HEIGHT - height - 20
        return [pygame.Rect(start_x + i * spacing, y, width, height) for i in range(amount)]

    @staticmethod
    def _center_card_rect(seat: int) -> pygame.Rect:
        width, height = c.CENTER_CARD_SIZE
        cx, cy = c.CENTER
        dx, dy = c.CENTER_CARD_OFFSETS[seat]
        return pygame.Rect(cx + dx - width // 2, cy + dy - height // 2, width, height)

    @staticmethod
    def _wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        words = text.split(" ")
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines or [""]
