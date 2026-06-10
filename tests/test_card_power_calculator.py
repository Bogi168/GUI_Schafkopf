from card_classes.Cards import Card, Color, Type
from card_classes.CardPowerCalculator import (
    CardPowerCalculator,
    SauspielCardPowerCalculator,
    WenzCardPowerCalculator,
    SoloCardPowerCalculator,
    RamschCardPowerCalculator,
    HochzeitCardPowerCalculator,
)


# tests for Ramsch, Sauspiel, Solo
def test_same_color(sauspiel_trumps, eichel_eight, eichel_nine, eichel_ten, eichel_sau):
    card_power_calculator = SauspielCardPowerCalculator()

    played_cards = [eichel_eight, eichel_nine, eichel_ten, eichel_sau]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=sauspiel_trumps
        )
        == eichel_sau
    )

    played_cards = [eichel_eight, eichel_nine, eichel_ten]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=sauspiel_trumps
        )
        == eichel_ten
    )


def test_mixed_colors(
    sauspiel_trumps, eichel_sau, eichel_ten, eichel_nine, schellen_sau, schellen_seven
):
    card_power_calculator = SauspielCardPowerCalculator()

    played_cards = [schellen_seven, eichel_nine, eichel_ten, eichel_sau]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=sauspiel_trumps
        )
        == schellen_seven
    )

    played_cards = [eichel_nine, schellen_sau, schellen_seven, eichel_sau]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=sauspiel_trumps
        )
        == eichel_sau
    )


def test_lead_trump(
    sauspiel_trumps,
    herz_seven,
    herz_eight,
    eichel_ober,
    gruen_ober,
    herz_ober,
    schellen_ober,
    eichel_unter,
    gruen_unter,
    herz_unter,
    schellen_unter,
    schellen_sau,
    eichel_sau,
    herz_sau,
    herz_ten,
):
    card_power_calculator = SauspielCardPowerCalculator()

    played_cards = [herz_seven, herz_sau, gruen_unter, eichel_ober]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=sauspiel_trumps
        )
        == eichel_ober
    )

    played_cards = [herz_eight, herz_seven, schellen_sau, eichel_sau]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=sauspiel_trumps
        )
        == herz_eight
    )

    played_cards = [eichel_ober, gruen_ober, herz_ober, schellen_ober]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=sauspiel_trumps
        )
        == eichel_ober
    )

    played_cards = [gruen_ober, herz_ober, schellen_ober, eichel_unter]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=sauspiel_trumps
        )
        == gruen_ober
    )

    played_cards = [herz_ober, schellen_ober, eichel_unter, gruen_unter]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=sauspiel_trumps
        )
        == herz_ober
    )

    played_cards = [schellen_ober, eichel_unter, gruen_unter, herz_unter]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=sauspiel_trumps
        )
        == schellen_ober
    )

    played_cards = [eichel_unter, gruen_unter, herz_unter, schellen_unter]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=sauspiel_trumps
        )
        == eichel_unter
    )

    played_cards = [gruen_unter, herz_unter, schellen_unter, herz_sau]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=sauspiel_trumps
        )
        == gruen_unter
    )

    played_cards = [herz_unter, schellen_unter, herz_sau, herz_ten]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=sauspiel_trumps
        )
        == herz_unter
    )


# special rules for Wenz
def test_same_color_ober(
    wenz_trumps,
    eichel_nine,
    eichel_ober,
    eichel_ten,
    eichel_koenig,
    eichel_sau,
    gruen_eight,
    gruen_ober,
):
    card_power_calculator = WenzCardPowerCalculator()

    played_cards = [eichel_nine, eichel_ober, eichel_ten, eichel_sau]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=wenz_trumps
        )
        == eichel_sau
    )

    played_cards = [eichel_nine, eichel_ober, eichel_ten, eichel_koenig]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=wenz_trumps
        )
        == eichel_ten
    )

    played_cards = [eichel_nine, eichel_ober, gruen_eight, eichel_koenig]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=wenz_trumps
        )
        == eichel_koenig
    )

    played_cards = [eichel_nine, eichel_ober, gruen_eight, gruen_ober]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=wenz_trumps
        )
        == eichel_ober
    )


def test_played_trump(
    wenz_trumps, eichel_nine, eichel_ober, eichel_unter, schellen_unter, eichel_sau
):
    card_power_calculator = WenzCardPowerCalculator()

    played_cards = [schellen_unter, eichel_ober, eichel_unter, eichel_nine]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=wenz_trumps
        )
        == eichel_unter
    )

    played_cards = [eichel_sau, eichel_ober, schellen_unter, eichel_nine]
    assert (
        card_power_calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=wenz_trumps
        )
        == schellen_unter
    )


# get_stronger_card


def test_get_stronger_card_returns_the_higher_power_card(eichel_sau, eichel_ten):
    calculator = CardPowerCalculator()

    assert calculator.get_stronger_card(eichel_sau, eichel_ten) == eichel_sau
    assert calculator.get_stronger_card(eichel_ten, eichel_sau) == eichel_sau


def test_get_stronger_card_tie_keeps_first_card(eichel_sau):
    calculator = CardPowerCalculator()
    other_eichel_sau = Card(card_color=Color.EICHEL, card_type=Type.SAU)

    assert calculator.get_stronger_card(eichel_sau, other_eichel_sau) is eichel_sau
    assert (
        calculator.get_stronger_card(other_eichel_sau, eichel_sau) is other_eichel_sau
    )


# RamschCardPowerCalculator and HochzeitCardPowerCalculator are Herz-trump
# pass-throughs, identical to SauspielCardPowerCalculator


def test_ramsch_and_hochzeit_card_power_match_sauspiel(
    herz_ober, eichel_unter, herz_sau, eichel_sau, gruen_seven
):
    sauspiel = SauspielCardPowerCalculator()

    for calculator_cls in (RamschCardPowerCalculator, HochzeitCardPowerCalculator):
        calculator = calculator_cls()
        assert calculator.trump_color == Color.HERZ
        assert calculator.trump_types == [Type.OBER, Type.UNTER]
        for card in (herz_ober, eichel_unter, herz_sau, eichel_sau, gruen_seven):
            assert calculator.get_card_power(card) == sauspiel.get_card_power(card)


# SoloCardPowerCalculator: Ober/Unter are always trump, the trump color is
# chosen by the game chooser and is configurable


def _solo_trumps(trump_color: Color) -> list[Card]:
    ober_and_unter = [
        Card(color, card_type)
        for card_type in (Type.OBER, Type.UNTER)
        for color in (Color.EICHEL, Color.GRUEN, Color.HERZ, Color.SCHELLEN)
    ]
    trump_color_cards = [
        Card(trump_color, card_type)
        for card_type in (
            Type.SAU,
            Type.TEN,
            Type.KOENIG,
            Type.NINE,
            Type.EIGHT,
            Type.SEVEN,
        )
    ]
    return ober_and_unter + trump_color_cards


def test_solo_trump_color_cards_get_trump_color_power(
    schellen_sau, schellen_ten, eichel_sau
):
    calculator = SoloCardPowerCalculator(trump_color=Color.SCHELLEN)

    # plain Schellen cards are trump (the chosen trump color)
    assert calculator.get_card_power(schellen_sau) == 100 + Type.SAU.value
    assert calculator.get_card_power(schellen_ten) == 100 + Type.TEN.value
    # Eichel Sau is just a normal color card - not trump in this Solo
    assert calculator.get_card_power(eichel_sau) == 80 + Type.SAU.value


def test_solo_ober_and_unter_outrank_trump_color_cards(
    eichel_unter, schellen_ober, schellen_sau
):
    calculator = SoloCardPowerCalculator(trump_color=Color.SCHELLEN)

    # any Ober beats any Unter, both beat the trump-color Sau
    assert calculator.get_card_power(schellen_ober) > calculator.get_card_power(
        eichel_unter
    )
    assert calculator.get_card_power(eichel_unter) > calculator.get_card_power(
        schellen_sau
    )


def test_solo_get_strongest_played_card_with_schellen_trump(
    eichel_sau, herz_ober, schellen_sau, schellen_seven
):
    calculator = SoloCardPowerCalculator(trump_color=Color.SCHELLEN)
    schellen_trumps = _solo_trumps(Color.SCHELLEN)

    played_cards = [eichel_sau, herz_ober, schellen_sau, schellen_seven]
    assert (
        calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=schellen_trumps
        )
        == herz_ober
    )

    played_cards = [eichel_sau, schellen_sau, schellen_seven]
    assert (
        calculator.get_strongest_played_card(
            played_cards=played_cards, trumps=schellen_trumps
        )
        == schellen_sau
    )
