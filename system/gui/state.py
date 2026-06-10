"""Shared mutable state describing what the GUI should currently display.

Instances are written by the game thread (via GUIRenderer's render_*/ask_*
methods) and read by the pygame main loop. All access must go through
GUIRenderer.lock.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from card_classes.Cards import Card, Color
    from player_classes.Player import Player
    from system.Renderer import GameResult


@dataclass
class PlayedCardEntry:
    """A card that one of the players has played in the current trick."""

    seat: int
    card: Card


@dataclass
class PendingRequest:
    """A blocking request for input from the human player."""

    kind: str
    player_name: str = ""
    title: str = ""
    options: list[tuple[str, Any]] = field(default_factory=list)
    legal_mask: list[bool] | None = None
    is_swap: bool = False


@dataclass
class TableState:
    """The full state of the table as the GUI should render it."""

    seat_names: list[str] = field(default_factory=lambda: ["", "", "", ""])
    seat_players: list[Player | None] = field(default_factory=lambda: [None, None, None, None])
    hand_sizes: list[int] = field(default_factory=lambda: [0, 0, 0, 0])
    human_hand: list[Card] = field(default_factory=list)
    center_cards: list[PlayedCardEntry] = field(default_factory=list)
    trick_winner_seat: int | None = None
    current_game_mode: str | None = None
    current_game_mode_chooser_seat: int | None = None
    current_game_mode_detail: str | None = None
    current_game_mode_detail_color: Color | None = None
    choice_announcement: str | None = None
    message: str = ""
    game_result: GameResult | None = None
    pending: PendingRequest | None = None
