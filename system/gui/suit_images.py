"""Loads and caches the Bavarian suit symbol images used by the GUI."""

from __future__ import annotations

import os
from functools import lru_cache

import pygame

from card_classes.Cards import Color

_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets", "suits")

_FILENAMES: dict[Color, str] = {
    Color.EICHEL: "eichel.png",
    Color.GRUEN: "gruen.png",
    Color.HERZ: "herz.png",
    Color.SCHELLEN: "schellen.png",
}

_DIM_ALPHA = 110


@lru_cache(maxsize=None)
def _load_original(color: Color) -> pygame.Surface:
    path = os.path.join(_ASSET_DIR, _FILENAMES[color])
    return pygame.image.load(path).convert_alpha()


@lru_cache(maxsize=None)
def get_suit_image(color: Color, height: int, dim: bool = False) -> pygame.Surface:
    """Returns the suit symbol for ``color`` scaled to ``height`` pixels tall,
    preserving its aspect ratio. If ``dim`` is True, the symbol is faded for
    use on disabled/illegal cards."""

    original = _load_original(color)
    width = round(original.get_width() * height / original.get_height())
    scaled = pygame.transform.smoothscale(original, (width, height))
    if dim:
        scaled = scaled.copy()
        scaled.fill((255, 255, 255, _DIM_ALPHA), special_flags=pygame.BLEND_RGBA_MULT)
    return scaled
