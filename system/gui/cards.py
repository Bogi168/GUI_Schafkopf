"""Drawing helpers for individual cards. Pure presentation - no game logic."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from system.gui import constants as c

if TYPE_CHECKING:
    from card_classes.Cards import Card


def draw_card_face(
    surface: pygame.Surface,
    rect: pygame.Rect,
    card: Card,
    fonts: c.Fonts,
    dim: bool = False,
) -> None:
    """Draws the face of a card showing its color and type."""

    bg = c.CARD_BG_DIM if dim else c.CARD_BG
    pygame.draw.rect(surface, bg, rect, border_radius=10)
    pygame.draw.rect(surface, c.CARD_BORDER, rect, width=2, border_radius=10)

    bar_color = c.TEXT_DIM if dim else c.SUIT_COLORS[card.card_color]
    bar_rect = pygame.Rect(rect.x + 3, rect.y + 3, rect.width - 6, 12)
    pygame.draw.rect(surface, bar_color, bar_rect, border_radius=6)

    text_color = c.TEXT_DIM if dim else c.TEXT_DARK

    type_surf = fonts.card_type.render(card.card_type.display_name, True, text_color)
    color_surf = fonts.card_color.render(card.card_color.display_name, True, text_color)

    surface.blit(type_surf, type_surf.get_rect(center=(rect.centerx, rect.centery - 6)))
    surface.blit(color_surf, color_surf.get_rect(center=(rect.centerx, rect.centery + 20)))


def draw_card_back(surface: pygame.Surface, rect: pygame.Rect) -> None:
    """Draws the back of a card (used for the bots' hidden hands)."""

    pygame.draw.rect(surface, c.CARD_BACK_BG, rect, border_radius=10)
    pygame.draw.rect(surface, c.CARD_BORDER, rect, width=2, border_radius=10)

    cx, cy = rect.center
    half_w, half_h = rect.width // 2 - 10, rect.height // 2 - 14
    if half_w > 0 and half_h > 0:
        pygame.draw.polygon(
            surface,
            c.CARD_BACK_PATTERN,
            [
                (cx, cy - half_h),
                (cx + half_w, cy),
                (cx, cy + half_h),
                (cx - half_w, cy),
            ],
            width=3,
        )
