"""Loads and caches the bot avatar images used by the GUI."""

from __future__ import annotations

import os
from functools import lru_cache

import pygame

_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets", "bot_icons")

_FILENAMES: dict[str, str] = {
    "Bot 1": "Bot1.png",
    "Bot 2": "Bot2.png",
    "Bot 3": "Bot3.png",
}


@lru_cache(maxsize=None)
def _load_original(bot_name: str) -> pygame.Surface | None:
    filename = _FILENAMES.get(bot_name)
    if filename is None:
        return None
    path = os.path.join(_ASSET_DIR, filename)
    return pygame.image.load(path).convert_alpha()


@lru_cache(maxsize=None)
def get_bot_image(bot_name: str, size: int) -> pygame.Surface | None:
    """Returns the avatar image for ``bot_name`` scaled to a ``size`` x
    ``size`` square, or None if no image is configured for that name."""

    original = _load_original(bot_name)
    if original is None:
        return None
    return pygame.transform.smoothscale(original, (size, size))
