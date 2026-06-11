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
class DealAnimation:
    """An in-flight card animation from the deck to a seat while dealing."""

    seat: int
    start_time: float
    duration: float


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
    previous_round_cards: list[PlayedCardEntry] = field(default_factory=list)
    show_previous_round: bool = False
    trick_winner_seat: int | None = None
    current_game_mode: str | None = None
    current_game_mode_chooser_seat: int | None = None
    current_game_mode_detail: str | None = None
    current_game_mode_detail_color: Color | None = None
    choice_announcement: str | None = None
    choice_announcement_detail: str | None = None
    choice_announcement_detail_color: Color | None = None
    is_farewell: bool = False
    message: str = ""
    # Per-seat "lamp" shown next to a bot's avatar while players decide
    # whether to choose the game: "pending" | "yes" | "no". Only populated
    # for bot seats, and only during the choosing process.
    game_choice_lamps: dict[int, str] = field(default_factory=dict)
    game_result: GameResult | None = None
    pending: PendingRequest | None = None
    # Card-dealing animation state, written by render_shuffle_cards /
    # render_deal_cards and read by the draw loop.
    shuffle_start_time: float | None = None
    shuffle_duration: float = 0.0
    dealing_card: DealAnimation | None = None
    # Set by GUIRenderer._run_game if the game-logic thread crashes.
    game_error: str | None = None
