"""Drawing of the pygame table: seats, cards, modals, and the result screen.

GUIRenderer owns the Renderer interface and the request/response plumbing;
TableView only reads `state` (under the shared lock) and draws to `screen`,
mirroring the pure presentation helpers in cards.py/widgets.py. `draw()` also
records the interactive elements it drew (buttons, card rects, the previous-
round toggle) and the human-readable text input; GUIRenderer's input handlers
read these back afterwards via `hit_test()`, `text_input_value`,
`handle_text_input_event()` and `reset_text_input()`.
"""

from __future__ import annotations

import math
import threading
import time
from typing import TYPE_CHECKING, NamedTuple

import pygame

from card_classes.Cards import Color
from system.gui import constants as c
from system.gui.bot_images import get_bot_image
from system.gui.cards import draw_card_back, draw_card_face
from system.gui.suit_images import get_suit_image
from system.gui.widgets import Button, TextInput, wrap_text

if TYPE_CHECKING:
    from system.gui.state import PendingRequest, TableState


_FAREWELL_SUITS = [Color.EICHEL, Color.GRUEN, Color.HERZ, Color.SCHELLEN]


class HitTestTargets(NamedTuple):
    """The interactive elements drawn during the last `draw()` call."""

    buttons: list[Button]
    card_rects: list[pygame.Rect]
    previous_round_button: Button | None


class TableView:
    """Draws the table for the current `TableState` onto `screen`."""

    def __init__(
        self,
        screen: pygame.Surface,
        fonts: c.Fonts,
        state: TableState,
        lock: threading.RLock,
    ) -> None:
        self.screen = screen
        self.fonts = fonts
        self.state = state
        self.lock = lock

        self._current_buttons: list[Button] = []
        self._current_card_rects: list[pygame.Rect] = []
        self._previous_round_button: Button | None = None
        self._text_input = TextInput(rect=pygame.Rect(0, 0, 1, 1))

    def hit_test(self) -> HitTestTargets:
        """Returns the interactive elements drawn during the last `draw()` call."""

        return HitTestTargets(
            buttons=self._current_buttons,
            card_rects=self._current_card_rects,
            previous_round_button=self._previous_round_button,
        )

    @staticmethod
    def _turn_pulse_color() -> tuple[int, int, int]:
        """A cyan that pulses over time for the whose-turn ring."""

        t = 0.5 + 0.5 * math.sin(time.time() * 4.5)
        return tuple(
            int(lo + (hi - lo) * t)
            for lo, hi in zip(c.TURN_HIGHLIGHT_DIM, c.TURN_HIGHLIGHT)
        )

    @property
    def text_input_value(self) -> str:
        return self._text_input.text.strip().capitalize()

    def reset_text_input(self) -> None:
        self._text_input.text = ""

    def handle_text_input_event(self, event: pygame.event.Event) -> bool:
        """Updates the text input on key events. Returns True if Enter was pressed with non-empty text."""

        return self._text_input.handle_event(event)

    def draw(self, mouse_pos: tuple[int, int]) -> None:
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
            self._draw_human_seat(mouse_pos)
            self._draw_center()
            self._draw_card_slide()
            self._draw_shuffle()
            self._draw_dealing_card()
            self._draw_swap_animation()
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
            if self.state.game_error:
                self._draw_error(self.state.game_error)

    def _draw_bot_seat(self, seat: int, mouse_pos: tuple[int, int]) -> None:
        avatar_pos = c.SEAT_AVATAR_POS[seat]
        name_pos = c.SEAT_NAME_POS[seat]
        name = self.state.seat_names[seat]

        avatar_rect = pygame.Rect(0, 0, c.AVATAR_SIZE, c.AVATAR_SIZE)
        avatar_rect.center = avatar_pos

        if self.state.trick_winner_seat == seat:
            pygame.draw.rect(self.screen, c.HIGHLIGHT, avatar_rect.inflate(8, 8), width=4, border_radius=8)
        elif self.state.active_seat == seat:
            pygame.draw.rect(
                self.screen,
                self._turn_pulse_color(),
                avatar_rect.inflate(12, 12),
                width=4,
                border_radius=10,
            )

        image = get_bot_image(name, c.AVATAR_SIZE)
        if image is not None:
            self.screen.blit(image, avatar_rect)

        lamp_state = self.state.game_choice_lamps.get(seat)
        if lamp_state is not None:
            lamp_color = {
                "pending": c.LAMP_BLUE,
                "yes": c.LAMP_GREEN,
                "no": c.LAMP_RED,
            }[lamp_state]
            lamp_center = (avatar_rect.right - c.LAMP_RADIUS, avatar_rect.top + c.LAMP_RADIUS)
            pygame.draw.circle(self.screen, lamp_color, lamp_center, c.LAMP_RADIUS)
            pygame.draw.circle(self.screen, c.BLACK, lamp_center, c.LAMP_RADIUS, width=2)

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

    def _draw_human_seat(self, mouse_pos: tuple[int, int]) -> None:
        name = self.state.seat_names[c.BOTTOM] or "You"
        player = self.state.seat_players[c.BOTTOM]
        label = name if player is None else f"{name} ({player.money}¢)"
        name_pos = c.SEAT_NAME_POS[c.BOTTOM]
        name_surf = self.fonts.name.render(label, True, c.TEXT_LIGHT)
        if self.state.trick_winner_seat == c.BOTTOM:
            highlight_rect = name_surf.get_rect(center=name_pos).inflate(24, 12)
            pygame.draw.rect(self.screen, c.HIGHLIGHT, highlight_rect, border_radius=8)
        elif self.state.active_seat == c.BOTTOM:
            highlight_rect = name_surf.get_rect(center=name_pos).inflate(24, 12)
            pygame.draw.rect(
                self.screen, self._turn_pulse_color(), highlight_rect, width=3, border_radius=8
            )
        self.screen.blit(name_surf, name_surf.get_rect(center=name_pos))

        cards = self.state.human_hand
        rects = self._hand_card_rects(len(cards))
        pending = self.state.pending
        legal_mask = pending.legal_mask if pending and pending.kind == "card" else None

        # While it is the human's turn, the card under the mouse (if legal)
        # lifts up to signal it is the one that will be played.
        hovered = None
        if legal_mask is not None:
            for index, rect in enumerate(rects):
                if legal_mask[index] and rect.collidepoint(mouse_pos):
                    hovered = index

        for index, (card, rect) in enumerate(zip(cards, rects)):
            legal = legal_mask is not None and legal_mask[index]
            dim = legal_mask is not None and not legal_mask[index]
            draw_rect = rect.move(0, -c.HAND_HOVER_LIFT) if index == hovered else rect
            draw_card_face(self.screen, draw_rect, card, self.fonts, dim=dim)
            if legal:
                # Gold outline marks every playable card; thicker when hovered.
                pygame.draw.rect(
                    self.screen,
                    c.LEGAL_CARD_HIGHLIGHT,
                    draw_rect.inflate(6, 6),
                    width=4 if index == hovered else 2,
                    border_radius=12,
                )

        if legal_mask is not None:
            # Hit-testing stays on the base rects: while a card is hovered the
            # cursor is within its base rect, so clicks register even though
            # the card is drawn lifted.
            self._current_card_rects = rects

    def _draw_center(self) -> None:
        collect = self.state.trick_collect
        target = None
        eased = 0.0
        if collect is not None:
            progress = min(1.0, (time.time() - collect.start_time) / collect.duration)
            eased = progress * progress  # accelerate as the cards sweep away
            target = self._deal_target(collect.winner_seat)
        for entry in self.state.center_cards:
            rect = self._center_card_rect(entry.seat)
            if target is not None:
                rect = rect.move(
                    int((target[0] - rect.centerx) * eased),
                    int((target[1] - rect.centery) * eased),
                )
            draw_card_face(self.screen, rect, entry.card, self.fonts)

    def _draw_shuffle(self) -> None:
        start_time = self.state.shuffle_start_time
        if start_time is None:
            return
        elapsed = time.time() - start_time
        progress = min(1.0, elapsed / self.state.shuffle_duration)
        amplitude = (1 - progress) * 36
        width, height = c.BACK_CARD_SIZE
        cx, cy = c.CENTER
        num_cards = 8
        for i in range(num_cards):
            phase = i / num_cards
            offset_x = math.sin(elapsed * 6 + phase * math.tau) * amplitude
            rect = pygame.Rect(0, 0, width, height)
            rect.center = (cx + offset_x, cy + i * 2 - num_cards)
            draw_card_back(self.screen, rect)

    def _draw_dealing_card(self) -> None:
        dealing = self.state.dealing_card
        if dealing is None:
            return
        progress = min(1.0, (time.time() - dealing.start_time) / dealing.duration)
        eased = 1 - (1 - progress) ** 2
        start_x, start_y = c.CENTER
        end_x, end_y = self._deal_target(dealing.seat)
        width, height = c.BACK_CARD_SIZE
        rect = pygame.Rect(0, 0, width, height)
        rect.center = (
            start_x + (end_x - start_x) * eased,
            start_y + (end_y - start_y) * eased,
        )
        draw_card_back(self.screen, rect)

    @staticmethod
    def _deal_target(seat: int) -> tuple[int, int]:
        if seat == c.BOTTOM:
            _, height = c.HAND_CARD_SIZE
            return (c.WINDOW_WIDTH // 2, c.WINDOW_HEIGHT - height // 2 - 20)
        return c.SEAT_HAND_CENTER[seat]

    def _draw_card_slide(self) -> None:
        slide = self.state.sliding_card
        if slide is None:
            return
        progress = min(1.0, (time.time() - slide.start_time) / slide.duration)
        eased = 1 - (1 - progress) ** 2
        start_x, start_y = self._deal_target(slide.seat)
        end_x, end_y = self._center_card_rect(slide.seat).center
        width, height = c.CENTER_CARD_SIZE
        rect = pygame.Rect(0, 0, width, height)
        rect.center = (
            start_x + (end_x - start_x) * eased,
            start_y + (end_y - start_y) * eased,
        )
        draw_card_face(self.screen, rect, slide.card, self.fonts)

    def _draw_swap_animation(self) -> None:
        swap = self.state.swap_animation
        if swap is None:
            return
        progress = min(1.0, (time.time() - swap.start_time) / swap.duration)
        eased = 1 - (1 - progress) ** 2
        pos_a = self._deal_target(swap.seat_a)
        pos_b = self._deal_target(swap.seat_b)
        width, height = c.BACK_CARD_SIZE
        # Two face-down cards pass each other between the partners' hands.
        for (start_x, start_y), (end_x, end_y) in ((pos_a, pos_b), (pos_b, pos_a)):
            rect = pygame.Rect(0, 0, width, height)
            rect.center = (
                start_x + (end_x - start_x) * eased,
                start_y + (end_y - start_y) * eased,
            )
            draw_card_back(self.screen, rect)

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

    def _draw_error(self, game_error: str) -> None:
        surf = self.fonts.body.render(f"Error: {game_error}", True, (255, 90, 90))
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
        title_lines = wrap_text(pending.title, self.fonts.heading, text_max_width)
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
        rect = pygame.Rect(0, 0, 640, 700)
        rect.center = (c.WINDOW_WIDTH // 2, c.WINDOW_HEIGHT // 2)
        return rect

    @staticmethod
    def _star_points(
        center: tuple[float, float], outer_radius: float, inner_radius: float
    ) -> list[tuple[float, float]]:
        points: list[tuple[float, float]] = []
        for i in range(10):
            angle = -math.pi / 2 + i * math.pi / 5
            radius = outer_radius if i % 2 == 0 else inner_radius
            points.append(
                (center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle))
            )
        return points

    def _draw_result_panel(self) -> None:
        result = self.state.game_result
        assert result is not None

        overlay = pygame.Surface((c.WINDOW_WIDTH, c.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*c.OVERLAY_COLOR, c.OVERLAY_ALPHA))
        self.screen.blit(overlay, (0, 0))

        panel_rect = self._result_panel_rect()
        pygame.draw.rect(self.screen, c.PANEL_BG, panel_rect, border_radius=14)
        pygame.draw.rect(self.screen, c.PANEL_BORDER, panel_rect, width=2, border_radius=14)

        content_x = panel_rect.left + 30
        content_width = panel_rect.width - 60
        y = panel_rect.top + 22

        title_surf = self.fonts.title.render("Game Result", True, c.TEXT_DARK)
        self.screen.blit(title_surf, title_surf.get_rect(midtop=(panel_rect.centerx, y)))
        y += title_surf.get_height() + 8
        pygame.draw.line(
            self.screen, c.HIGHLIGHT, (content_x, y), (content_x + content_width, y), 3
        )
        y += 14

        winners = set(result.winners)

        for team in result.most_point_teams:
            is_winning_team = any(player in winners for player in team.players)
            pill_bg = c.RESULT_WIN_BG if is_winning_team else c.RESULT_NEUTRAL_BG
            player_names = ", ".join(player.player_name for player in team.players)
            line = f"{team.team_name}: {team.points} points ({player_names})"
            text_surf = self.fonts.body.render(line, True, c.TEXT_DARK)
            pill_rect = pygame.Rect(content_x, y, content_width, text_surf.get_height() + 10)
            pygame.draw.rect(self.screen, pill_bg, pill_rect, border_radius=8)
            self.screen.blit(text_surf, text_surf.get_rect(center=pill_rect.center))
            y += pill_rect.height + 6

        y += 8

        if result.winners:
            if len(result.winners) == 1:
                winners_line = f"Winner: {result.winners[0].player_name}"
            else:
                winners_line = "Winners: " + ", ".join(p.player_name for p in result.winners)
            text_surf = self.fonts.heading.render(winners_line, True, c.TEXT_DARK)
            badge_rect = pygame.Rect(0, 0, text_surf.get_width() + 120, text_surf.get_height() + 18)
            badge_rect.centerx = panel_rect.centerx
            badge_rect.top = y
            pygame.draw.rect(
                self.screen, c.RESULT_WINNER_BG, badge_rect, border_radius=badge_rect.height // 2
            )
            pygame.draw.rect(
                self.screen, c.HIGHLIGHT, badge_rect, width=2, border_radius=badge_rect.height // 2
            )
            self.screen.blit(text_surf, text_surf.get_rect(center=badge_rect.center))
            for star_x in (badge_rect.left + 20, badge_rect.right - 20):
                pygame.draw.polygon(
                    self.screen, c.HIGHLIGHT, self._star_points((star_x, badge_rect.centery), 10, 4.5)
                )
            y += badge_rect.height + 16
        else:
            text_surf = self.fonts.heading.render("No winner this round", True, c.TEXT_DIM)
            self.screen.blit(text_surf, text_surf.get_rect(midtop=(panel_rect.centerx, y)))
            y += text_surf.get_height() + 16

        breakdown_lines = [
            line.strip() for line in result.game_value_breakdown.split("\n") if line.strip()
        ]
        if breakdown_lines:
            line_height = 24
            box_rect = pygame.Rect(content_x, y, content_width, len(breakdown_lines) * line_height + 16)
            pygame.draw.rect(self.screen, c.RESULT_NEUTRAL_BG, box_rect, border_radius=8)
            line_y = box_rect.top + 8
            for line in breakdown_lines:
                self.screen.blit(self.fonts.body.render(line, True, c.TEXT_DIM), (box_rect.left + 16, line_y))
                line_y += line_height
            y += box_rect.height + 16

        value_surf = self.fonts.heading.render(
            f"Game value: {result.game_value} cents", True, c.BUTTON_TEXT
        )
        badge_rect = pygame.Rect(0, 0, value_surf.get_width() + 48, value_surf.get_height() + 20)
        badge_rect.centerx = panel_rect.centerx
        badge_rect.top = y
        pygame.draw.rect(self.screen, c.BUTTON_BG, badge_rect, border_radius=badge_rect.height // 2)
        self.screen.blit(value_surf, value_surf.get_rect(center=badge_rect.center))
        y += badge_rect.height + 18

        pygame.draw.line(
            self.screen, c.PANEL_BORDER, (content_x, y), (content_x + content_width, y), 1
        )
        y += 14

        money_changes = bool(result.winners) and len(result.winners) != len(result.players)
        row_height = 32
        for index, player in enumerate(result.players):
            row_rect = pygame.Rect(content_x, y, content_width, row_height)
            if index % 2 == 1:
                pygame.draw.rect(self.screen, c.RESULT_ROW_ALT_BG, row_rect, border_radius=6)
            if money_changes:
                dot_color = c.LAMP_GREEN if player in winners else c.LAMP_RED
            else:
                dot_color = c.CARD_BG_DIM
            pygame.draw.circle(self.screen, dot_color, (row_rect.left + 14, row_rect.centery), 6)
            name_surf = self.fonts.body.render(player.player_name, True, c.TEXT_DARK)
            self.screen.blit(name_surf, name_surf.get_rect(midleft=(row_rect.left + 30, row_rect.centery)))
            money_surf = self.fonts.body.render(f"{player.money} cents", True, c.TEXT_DARK)
            self.screen.blit(money_surf, money_surf.get_rect(midright=(row_rect.right - 10, row_rect.centery)))
            y += row_height + 4

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
