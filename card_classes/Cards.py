from enum import Enum, IntEnum
from dataclasses import dataclass


class Color(Enum):
    """The color of the card"""

    SCHELLEN = 4
    HERZ = 3
    GRUEN = 2
    EICHEL = 1

    @property
    def display_name(self) -> str:
        names = {
            Color.EICHEL: "Eichel",
            Color.GRUEN: "Grün",
            Color.HERZ: "Herz",
            Color.SCHELLEN: "Schellen",
        }
        return names[self]


class Type(IntEnum):
    """The type of the card"""

    SEVEN = 1
    EIGHT = 2
    NINE = 3
    KOENIG = 6  # In Game mode Wenz Ober is equivalent to a 5, Geier makes Unters a 4
    TEN = 7
    SAU = 8
    UNTER = 9
    OBER = 10

    @property
    def display_name(self) -> str:
        names = {
            Type.SEVEN: "7",
            Type.EIGHT: "8",
            Type.NINE: "9",
            Type.UNTER: "Unter",
            Type.OBER: "Ober",
            Type.KOENIG: "König",
            Type.TEN: "10",
            Type.SAU: "Sau",
        }
        return names[self]

    @property
    def points(self) -> int:
        points = {
            Type.SEVEN: 0,
            Type.EIGHT: 0,
            Type.NINE: 0,
            Type.UNTER: 2,
            Type.OBER: 3,
            Type.KOENIG: 4,
            Type.TEN: 10,
            Type.SAU: 11,
        }
        return points[self]


@dataclass
class Card:
    """
    A card object that represents a card with a certain color, type and name
    :param card_color: The color of the card
    :type card_color: Color
    :param card_type: The type of the card
    :type card_type: Type
    :param card_name: The name of the card
    :type card_name: str
    """

    card_color: Color
    card_type: Type
    card_name: str | None = None

    def __post_init__(self) -> None:
        if self.card_name is None:
            self.card_name: str = (
                f"({self.card_color.display_name} {self.card_type.display_name})"
            )


class Cards:
    """
    A cards object which saves a full deck of cards and provides a deck to play with
    """

    def __init__(self) -> None:
        self.deck: list[Card] = self.full_deck.copy()

    @property
    def full_deck(self) -> list[Card]:
        return [
            Card(card_color=card_color, card_type=card_type)
            for card_type in Type
            for card_color in Color
        ]

    def reset_deck(self) -> None:
        """deck is reset to the original full deck."""
        self.deck = self.full_deck.copy()
