from card_classes.CardPowerCalculator import (
    SauspielCardPowerCalculator,
    WenzCardPowerCalculator,
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
