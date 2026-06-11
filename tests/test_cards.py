from card_classes.Cards import Card, Cards, Color, Type


# --- Card.__post_init__ ---


def test_card_auto_generates_name_when_not_provided():
    card = Card(Color.EICHEL, Type.OBER)

    assert card.card_name == "(Eichel Ober)"


def test_card_auto_generates_name_for_another_color_and_type():
    card = Card(Color.HERZ, Type.SAU)

    assert card.card_name == "(Herz Sau)"


def test_card_preserves_explicitly_provided_name():
    card = Card(Color.EICHEL, Type.OBER, card_name="Custom Name")

    assert card.card_name == "Custom Name"


# --- Color.display_name ---


def test_color_display_names():
    assert Color.EICHEL.display_name == "Eichel"
    assert Color.GRUEN.display_name == "Grün"
    assert Color.HERZ.display_name == "Herz"
    assert Color.SCHELLEN.display_name == "Schellen"


# --- Type.display_name ---


def test_type_display_names():
    assert Type.SEVEN.display_name == "7"
    assert Type.EIGHT.display_name == "8"
    assert Type.NINE.display_name == "9"
    assert Type.UNTER.display_name == "Unter"
    assert Type.OBER.display_name == "Ober"
    assert Type.KOENIG.display_name == "König"
    assert Type.TEN.display_name == "10"
    assert Type.SAU.display_name == "Sau"


# --- Type.points ---


def test_type_points():
    assert Type.SAU.points == 11
    assert Type.TEN.points == 10
    assert Type.KOENIG.points == 4
    assert Type.OBER.points == 3
    assert Type.UNTER.points == 2
    assert Type.NINE.points == 0
    assert Type.EIGHT.points == 0
    assert Type.SEVEN.points == 0


# --- Cards.__init__ / full_deck / reset_deck ---


def test_cards_init_sets_deck_to_copy_of_full_deck():
    cards = Cards()

    assert len(cards.deck) == 32
    assert cards.deck == cards.full_deck

    # .deck must be a distinct list object from full_deck
    assert cards.deck is not cards.full_deck

    # mutating .deck must not affect a freshly accessed full_deck
    cards.deck.pop()
    assert len(cards.full_deck) == 32
    assert len(cards.deck) == 31


def test_full_deck_has_32_unique_cards_covering_all_colors_and_types():
    cards = Cards()
    full_deck = cards.full_deck

    assert len(full_deck) == 32

    pairs = [(card.card_color, card.card_type) for card in full_deck]
    assert len(set(pairs)) == 32

    colors = {card.card_color for card in full_deck}
    types = {card.card_type for card in full_deck}
    assert colors == set(Color)
    assert types == set(Type)


def test_reset_deck_restores_full_deck_after_removal():
    cards = Cards()

    # remove some cards from the deck
    cards.deck.pop()
    cards.deck.pop()
    assert len(cards.deck) == 30

    cards.reset_deck()

    assert len(cards.deck) == 32
    assert cards.deck == cards.full_deck
