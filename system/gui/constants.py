"""Layout constants, colors and fonts for the pygame GUI.

Pure presentation data - no game logic lives here.
"""

from __future__ import annotations

import pygame

from card_classes.Cards import Color

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 30

# Seat indices: 0 = bottom (human), 1 = left, 2 = top, 3 = right
BOTTOM, LEFT, TOP, RIGHT = 0, 1, 2, 3

CENTER = (600, 380)

# Card sizes (width, height)
HAND_CARD_SIZE = (90, 130)
CENTER_CARD_SIZE = (74, 108)
BACK_CARD_SIZE = (60, 86)

# Offsets of played cards relative to CENTER, keyed by seat
CENTER_CARD_OFFSETS = {
    BOTTOM: (0, 85),
    LEFT: (-95, 0),
    TOP: (0, -85),
    RIGHT: (95, 0),
}

# Avatar positions and name label positions for the bot seats
AVATAR_RADIUS = 35
SEAT_AVATAR_POS = {
    LEFT: (90, 200),
    TOP: (600, 60),
    RIGHT: (1110, 200),
}
SEAT_NAME_POS = {
    BOTTOM: (600, 595),
    LEFT: (90, 245),
    TOP: (600, 105),
    RIGHT: (1110, 245),
}
SEAT_HAND_CENTER = {
    LEFT: (90, 400),
    TOP: (600, 165),
    RIGHT: (1110, 400),
}

# Hand-of-cards layout direction per seat. Left/right bots fan their hidden
# cards vertically so the fan stays on-screen near the table edges; the top
# bot fans horizontally like the human player.
HORIZONTAL = "horizontal"
VERTICAL = "vertical"
SEAT_HAND_ORIENTATION = {
    LEFT: VERTICAL,
    TOP: HORIZONTAL,
    RIGHT: VERTICAL,
}

# Colors
TABLE_GREEN = (21, 88, 54)
TABLE_GREEN_DARK = (15, 68, 42)
CARD_BG = (250, 247, 234)
CARD_BG_DIM = (165, 165, 155)
CARD_BORDER = (30, 30, 30)
CARD_BACK_BG = (32, 58, 110)
CARD_BACK_PATTERN = (76, 110, 180)
TEXT_DARK = (25, 25, 25)
TEXT_DIM = (110, 110, 100)
TEXT_LIGHT = (245, 245, 245)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT = (255, 215, 0)
AVATAR_COLORS = {
    LEFT: (70, 130, 180),
    TOP: (180, 90, 70),
    RIGHT: (90, 150, 90),
}
OVERLAY_COLOR = (0, 0, 0)
OVERLAY_ALPHA = 170
PANEL_BG = (250, 250, 248)
PANEL_BORDER = (40, 40, 40)
BUTTON_BG = (60, 120, 170)
BUTTON_HOVER_BG = (94, 158, 209)
BUTTON_DISABLED_BG = (150, 150, 150)
BUTTON_TEXT = (255, 255, 255)

SUIT_COLORS: dict[Color, tuple[int, int, int]] = {
    Color.EICHEL: (139, 94, 46),
    Color.GRUEN: (43, 130, 70),
    Color.HERZ: (190, 50, 50),
    Color.SCHELLEN: (205, 155, 30),
}


class Fonts:
    """Holds the fonts used by the GUI. Must be created after pygame.font.init()."""

    def __init__(self) -> None:
        self.title = pygame.font.SysFont("arial", 34, bold=True)
        self.heading = pygame.font.SysFont("arial", 24, bold=True)
        self.body = pygame.font.SysFont("arial", 20)
        self.small = pygame.font.SysFont("arial", 15)
        self.card_type = pygame.font.SysFont("arial", 18, bold=True)
        self.card_color = pygame.font.SysFont("arial", 13)
        self.button = pygame.font.SysFont("arial", 19, bold=True)
        self.name = pygame.font.SysFont("arial", 19, bold=True)
