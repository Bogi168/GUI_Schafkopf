"""Small reusable UI widgets for the pygame GUI. Pure presentation - no game logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pygame

from system.gui import constants as c


@dataclass
class Button:
    """A clickable rectangular button with a text label."""

    rect: pygame.Rect
    label: str
    value: Any = None
    enabled: bool = True

    def draw(self, surface: pygame.Surface, fonts: c.Fonts, mouse_pos: tuple[int, int]) -> None:
        if not self.enabled:
            bg = c.BUTTON_DISABLED_BG
        elif self.rect.collidepoint(mouse_pos):
            bg = c.BUTTON_HOVER_BG
        else:
            bg = c.BUTTON_BG
        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, c.BLACK, self.rect, width=2, border_radius=8)
        text_surf = fonts.button.render(self.label, True, c.BUTTON_TEXT)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def is_clicked(self, pos: tuple[int, int]) -> bool:
        return self.enabled and self.rect.collidepoint(pos)


@dataclass
class TextInput:
    """A simple single-line text input box with a blinking cursor."""

    rect: pygame.Rect
    text: str = ""
    max_length: int = 20

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Updates the text on key events. Returns True if Enter was pressed with non-empty text."""

        if event.type != pygame.KEYDOWN:
            return False
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.key == pygame.K_RETURN:
            return bool(self.text.strip())
        elif event.unicode and event.unicode.isprintable() and len(self.text) < self.max_length:
            self.text += event.unicode
        return False

    def draw(self, surface: pygame.Surface, fonts: c.Fonts) -> None:
        pygame.draw.rect(surface, c.WHITE, self.rect, border_radius=4)
        pygame.draw.rect(surface, c.BLACK, self.rect, width=2, border_radius=4)
        text_surf = fonts.body.render(self.text, True, c.TEXT_DARK)
        surface.blit(
            text_surf,
            (self.rect.x + 10, self.rect.centery - text_surf.get_height() // 2),
        )
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            cursor_x = self.rect.x + 12 + text_surf.get_width()
            pygame.draw.line(
                surface,
                c.TEXT_DARK,
                (cursor_x, self.rect.y + 8),
                (cursor_x, self.rect.bottom - 8),
                2,
            )
