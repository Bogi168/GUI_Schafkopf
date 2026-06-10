import pytest

from input_validators.CardDecisionValidator import (
    RegularTrumpTypeCardDecisionValidator,
    SauspielCardDecisionValidator,
    WenzCardDecisionValidator,
    HochzeitCardDecisionValidator,
)


# general rules
def test_last_card_freedom(
    sauspiel_trumps,
    eichel_ten,
    eichel_seven,
    schellen_seven,
    eichel_ober,
    herz_seven,
):
    validator = RegularTrumpTypeCardDecisionValidator()
    lead_card = eichel_ten

    player_cards = [eichel_seven]
    assert validator.is_move_legal(
        decision=eichel_seven,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )

    player_cards = [schellen_seven]
    assert validator.is_move_legal(
        decision=schellen_seven,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )

    player_cards = [eichel_ober]
    assert validator.is_move_legal(
        decision=eichel_ober,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )

    player_cards = [herz_seven]
    assert validator.is_move_legal(
        decision=herz_seven,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )


def test_lead_freedom(
    sauspiel_trumps,
    gruen_unter,
    eichel_ten,
    herz_seven,
    eichel_ober,
    gruen_eight,
):
    validator = RegularTrumpTypeCardDecisionValidator()
    lead_card = None
    player_cards = [eichel_ten, herz_seven, eichel_ober, gruen_eight]
    assert validator.is_move_legal(
        decision=eichel_ten,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert validator.is_move_legal(
        decision=gruen_eight,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert validator.is_move_legal(
        decision=herz_seven,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert validator.is_move_legal(
        decision=eichel_ober,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )


def test_lead_color_obligation(
    sauspiel_trumps,
    eichel_ten,
    eichel_seven,
    schellen_seven,
    eichel_ober,
):
    validator = RegularTrumpTypeCardDecisionValidator()
    lead_card = eichel_ten
    player_cards = [eichel_seven, schellen_seven, eichel_ober]

    assert not validator.is_move_legal(
        decision=schellen_seven,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert not validator.is_move_legal(
        decision=eichel_ober,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert validator.is_move_legal(
        decision=eichel_seven,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )


def test_lead_color_freedom(
    sauspiel_trumps,
    gruen_unter,
    eichel_ten,
    herz_seven,
    eichel_ober,
    gruen_eight,
):
    validator = RegularTrumpTypeCardDecisionValidator()
    lead_card = gruen_eight
    player_cards = [eichel_ten, herz_seven, eichel_ober]
    assert validator.is_move_legal(
        decision=eichel_ten,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert validator.is_move_legal(
        decision=herz_seven,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert validator.is_move_legal(
        decision=eichel_ober,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )


def test_lead_trump_obligation(
    sauspiel_trumps,
    gruen_unter,
    eichel_ten,
    herz_seven,
    eichel_ober,
    gruen_eight,
):
    validator = RegularTrumpTypeCardDecisionValidator()
    lead_card = gruen_unter
    player_cards = [eichel_ten, herz_seven, eichel_ober, gruen_eight]
    assert not validator.is_move_legal(
        decision=eichel_ten,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert not validator.is_move_legal(
        decision=gruen_eight,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert validator.is_move_legal(
        decision=herz_seven,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert validator.is_move_legal(
        decision=eichel_ober,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )


def test_lead_trump_freedom(
    sauspiel_trumps,
    herz_seven,
    eichel_sau,
    eichel_ober,
    gruen_eight,
    schellen_seven,
):
    validator = RegularTrumpTypeCardDecisionValidator()
    lead_card = herz_seven
    player_cards = [schellen_seven, eichel_sau, gruen_eight]
    assert validator.is_move_legal(
        decision=eichel_sau,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert validator.is_move_legal(
        decision=gruen_eight,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert validator.is_move_legal(
        decision=schellen_seven,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )


# special Sauspiel rules
def test_sau_lead_freedom(
    sauspiel_trumps,
    eichel_sau,
    eichel_seven,
    eichel_eight,
    eichel_ten,
    eichel_ober,
    gruen_eight,
):
    validator = SauspielCardDecisionValidator(call_sau=eichel_sau)
    lead_card = None
    player_cards = [
        eichel_ten,
        eichel_seven,
        eichel_ober,
        eichel_sau,
        gruen_eight,
    ]
    assert validator.is_move_legal(
        decision=eichel_sau,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert validator.is_move_legal(
        decision=gruen_eight,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert validator.is_move_legal(
        decision=eichel_ober,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert not validator.is_move_legal(
        decision=eichel_ten,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )

    player_cards = [
        eichel_ten,
        eichel_seven,
        eichel_ober,
        eichel_sau,
        eichel_eight,
    ]

    assert validator.is_move_legal(
        decision=eichel_ten,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert validator.is_move_legal(
        decision=eichel_sau,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )


def test_sau_is_called_obligation(
    sauspiel_trumps,
    eichel_sau,
    eichel_seven,
    eichel_eight,
    eichel_nine,
    eichel_ten,
    eichel_ober,
    gruen_eight,
):
    validator = SauspielCardDecisionValidator(call_sau=eichel_sau)
    lead_card = eichel_eight
    player_cards = [
        eichel_ten,
        eichel_seven,
        eichel_ober,
        eichel_sau,
        gruen_eight,
    ]
    assert validator.is_move_legal(
        decision=eichel_sau,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert not validator.is_move_legal(
        decision=gruen_eight,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert not validator.is_move_legal(
        decision=eichel_ober,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert not validator.is_move_legal(
        decision=eichel_ten,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )

    player_cards = [
        eichel_ten,
        eichel_seven,
        eichel_ober,
        eichel_sau,
        eichel_nine,
    ]

    assert not validator.is_move_legal(
        decision=eichel_ten,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert validator.is_move_legal(
        decision=eichel_sau,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )


def test_sau_is_not_called_prohibition(
    sauspiel_trumps,
    eichel_sau,
    eichel_seven,
    eichel_eight,
    eichel_nine,
    eichel_ober,
    gruen_eight,
    schellen_seven,
):
    validator = SauspielCardDecisionValidator(call_sau=eichel_sau)
    lead_card = schellen_seven
    player_cards = [
        eichel_nine,
        eichel_seven,
        eichel_ober,
        eichel_sau,
        gruen_eight,
    ]
    assert validator.is_move_legal(
        decision=eichel_nine,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert validator.is_move_legal(
        decision=gruen_eight,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert validator.is_move_legal(
        decision=eichel_ober,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )
    assert not validator.is_move_legal(
        decision=eichel_sau,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=sauspiel_trumps,
    )


# WenzCardDecisionValidator: only the four Unter are trump, Ober are regular
# color cards


def test_wenz_lead_trump_obligation(
    wenz_trumps, eichel_unter, gruen_unter, eichel_sau, herz_ober
):
    validator = WenzCardDecisionValidator()
    lead_card = eichel_unter
    player_cards = [gruen_unter, eichel_sau, herz_ober]

    assert validator.is_move_legal(
        decision=gruen_unter,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=wenz_trumps,
    )
    assert not validator.is_move_legal(
        decision=eichel_sau,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=wenz_trumps,
    )
    assert not validator.is_move_legal(
        decision=herz_ober,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=wenz_trumps,
    )


def test_wenz_lead_trump_freedom_without_unter(
    wenz_trumps, eichel_unter, eichel_sau, herz_ober
):
    validator = WenzCardDecisionValidator()
    lead_card = eichel_unter
    player_cards = [eichel_sau, herz_ober]

    assert validator.is_move_legal(
        decision=eichel_sau,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=wenz_trumps,
    )
    assert validator.is_move_legal(
        decision=herz_ober,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=wenz_trumps,
    )


def test_wenz_ober_is_a_regular_color_card(
    wenz_trumps, eichel_koenig, eichel_ober, gruen_sau, herz_seven
):
    validator = WenzCardDecisionValidator()
    lead_card = eichel_koenig
    player_cards = [eichel_ober, gruen_sau, herz_seven]

    assert validator.is_move_legal(
        decision=eichel_ober,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=wenz_trumps,
    )
    assert not validator.is_move_legal(
        decision=gruen_sau,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=wenz_trumps,
    )
    assert not validator.is_move_legal(
        decision=herz_seven,
        lead_card=lead_card,
        player_cards=player_cards,
        trumps=wenz_trumps,
    )


def test_wenz_lead_color_freedom_when_only_trump_of_that_color_held(
    wenz_trumps, eichel_koenig, eichel_unter, gruen_sau, herz_seven
):
    validator = WenzCardDecisionValidator()
    lead_card = eichel_koenig
    player_cards = [eichel_unter, gruen_sau, herz_seven]

    # eichel_unter is trump (not a "regular" Eichel card), so no Eichel
    # color card is available -> free to play anything, including the
    # Eichel Unter
    for decision in player_cards:
        assert validator.is_move_legal(
            decision=decision,
            lead_card=lead_card,
            player_cards=player_cards,
            trumps=wenz_trumps,
        )


# HochzeitCardDecisionValidator.is_card_swap_legal: the chooser must give
# away a trump card (Ober/Unter or Herz), the partner must give away a
# non-trump card


def test_hochzeit_chooser_must_give_trump(
    eichel_ober, eichel_unter, herz_sau, eichel_sau
):
    validator = HochzeitCardDecisionValidator()

    assert validator.is_card_swap_legal(decision=eichel_ober, is_game_chooser=True)
    assert validator.is_card_swap_legal(decision=eichel_unter, is_game_chooser=True)
    assert validator.is_card_swap_legal(decision=herz_sau, is_game_chooser=True)
    assert not validator.is_card_swap_legal(decision=eichel_sau, is_game_chooser=True)


def test_hochzeit_partner_must_give_non_trump(
    eichel_ober, eichel_unter, herz_sau, eichel_sau
):
    validator = HochzeitCardDecisionValidator()

    assert validator.is_card_swap_legal(decision=eichel_sau, is_game_chooser=False)
    assert not validator.is_card_swap_legal(
        decision=eichel_ober, is_game_chooser=False
    )
    assert not validator.is_card_swap_legal(
        decision=eichel_unter, is_game_chooser=False
    )
    assert not validator.is_card_swap_legal(decision=herz_sau, is_game_chooser=False)


# the base CardDecisionValidator does not support card swaps


def test_card_swap_not_implemented_by_default(eichel_sau):
    validator = RegularTrumpTypeCardDecisionValidator()

    with pytest.raises(NotImplementedError):
        validator.is_card_swap_legal(decision=eichel_sau, is_game_chooser=True)
