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
class SwapAnimation:
    """Two face-down cards sliding between the Hochzeit partners' seats."""

    seat_a: int
    seat_b: int
    start_time: float
    duration: float


@dataclass
class CardSlideAnimation:
    """A just-played card sliding face-up from a seat to its center slot."""

    seat: int
    card: Card
    start_time: float
    duration: float


@dataclass
class TrickCollectAnimation:
    """The finished trick's cards sweeping from the center to the winner."""

    winner_seat: int
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
    # Seat currently to act (a bot "thinking" before its card drops, or the
    # human while the play-a-card request is pending). None between turns.
    active_seat: int | None = None
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
    # Hochzeit card-swap animation, written by render_hochzeit_card_swap.
    swap_animation: SwapAnimation | None = None
    # A played card in flight from its seat to the center, written by
    # render_played_card while it slides in (before it joins center_cards).
    sliding_card: CardSlideAnimation | None = None
    # The finished trick sweeping to the winner, written by
    # render_trick_winner; while set, the center cards animate toward them.
    trick_collect: TrickCollectAnimation | None = None
    # Set by GUIRenderer._run_game if the game-logic thread crashes.
    game_error: str | None = None
