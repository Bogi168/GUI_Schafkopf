from input_validators.CardDecisionValidator import (
    RegularTrumpTypeCardDecisionValidator,
    SauspielCardDecisionValidator,
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
