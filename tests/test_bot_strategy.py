from unittest.mock import MagicMock

from player_classes.Player import Bot
from player_classes.bot_strategy import (
    ramsch_risk,
    wants_to_double_game_value,
    wants_to_play_ramsch,
)


def _bot(player_cards):
    bot = Bot(
        bot_name="Bot 1",
        renderer=MagicMock(),
        game_decision_validator=MagicMock(),
    )
    bot.player_cards = player_cards
    return bot


def test_ramsch_risk_zero_for_trump_free_hand_without_blanc_sau_or_ten(
    eichel_seven,
    eichel_eight,
    eichel_nine,
    eichel_koenig,
    gruen_seven,
    gruen_eight,
    schellen_seven,
    schellen_eight,
):
    hand = [
        eichel_seven,
        eichel_eight,
        eichel_nine,
        eichel_koenig,
        gruen_seven,
        gruen_eight,
        schellen_seven,
        schellen_eight,
    ]

    assert ramsch_risk(hand) == 0


def test_ramsch_risk_high_for_trump_heavy_hand(
    eichel_ober,
    gruen_ober,
    herz_ober,
    schellen_ober,
    eichel_unter,
    gruen_unter,
    herz_sau,
    herz_koenig,
):
    hand = [
        eichel_ober,
        gruen_ober,
        herz_ober,
        schellen_ober,
        eichel_unter,
        gruen_unter,
        herz_sau,
        herz_koenig,
    ]

    assert ramsch_risk(hand) == 16.0


def test_ramsch_risk_counts_blanc_sau(
    eichel_sau,
    gruen_seven,
    gruen_eight,
    gruen_nine,
    gruen_koenig,
    schellen_seven,
    schellen_eight,
    schellen_nine,
):
    # Eichel Sau is the only Eichel card in hand.
    hand = [
        eichel_sau,
        gruen_seven,
        gruen_eight,
        gruen_nine,
        gruen_koenig,
        schellen_seven,
        schellen_eight,
        schellen_nine,
    ]

    assert ramsch_risk(hand) == 2.0


def test_ramsch_risk_counts_blanc_ten(
    gruen_ten,
    eichel_seven,
    eichel_eight,
    eichel_nine,
    eichel_koenig,
    schellen_seven,
    schellen_eight,
    schellen_nine,
):
    # Gruen Ten is the only Gruen card in hand.
    hand = [
        gruen_ten,
        eichel_seven,
        eichel_eight,
        eichel_nine,
        eichel_koenig,
        schellen_seven,
        schellen_eight,
        schellen_nine,
    ]

    assert ramsch_risk(hand) == 1.0


def test_wants_to_play_ramsch_true_for_low_risk_hand(
    eichel_seven,
    eichel_eight,
    eichel_nine,
    eichel_koenig,
    gruen_seven,
    gruen_eight,
    schellen_seven,
    schellen_eight,
):
    hand = [
        eichel_seven,
        eichel_eight,
        eichel_nine,
        eichel_koenig,
        gruen_seven,
        gruen_eight,
        schellen_seven,
        schellen_eight,
    ]

    assert wants_to_play_ramsch(hand) is True


def test_wants_to_play_ramsch_false_for_trump_heavy_hand(
    eichel_ober,
    gruen_ober,
    herz_ober,
    schellen_ober,
    eichel_unter,
    gruen_unter,
    herz_sau,
    herz_koenig,
):
    hand = [
        eichel_ober,
        gruen_ober,
        herz_ober,
        schellen_ober,
        eichel_unter,
        gruen_unter,
        herz_sau,
        herz_koenig,
    ]

    assert wants_to_play_ramsch(hand) is False


def test_wants_to_play_ramsch_true_for_blanc_sau_alone(
    eichel_sau,
    gruen_sau,
    gruen_ten,
    gruen_koenig,
    gruen_nine,
    schellen_sau,
    schellen_ten,
    schellen_koenig,
):
    # Eichel Sau is blanc and there are no trumps at all - a blanc Sau on
    # its own should not be enough to refuse the Ramsch.
    hand = [
        eichel_sau,
        gruen_sau,
        gruen_ten,
        gruen_koenig,
        gruen_nine,
        schellen_sau,
        schellen_ten,
        schellen_koenig,
    ]

    assert wants_to_play_ramsch(hand) is True


def test_wants_to_play_ramsch_false_when_blanc_sau_tips_a_trumpy_hand(
    eichel_unter,
    herz_sau,
    herz_koenig,
    gruen_seven,
    gruen_eight,
    gruen_nine,
    gruen_koenig,
    gruen_ten,
    schellen_sau,
):
    # 1 Unter + 2 Herz trumps alone is risky but still acceptable...
    moderate_trumps = [
        eichel_unter,
        herz_sau,
        herz_koenig,
        gruen_seven,
        gruen_eight,
        gruen_nine,
        gruen_koenig,
        gruen_ten,
    ]
    assert wants_to_play_ramsch(moderate_trumps) is True

    # ...but swapping the harmless Gruen Zehn for a blanc Schellen Sau
    # tips the same hand into "no".
    with_blanc_sau = [
        eichel_unter,
        herz_sau,
        herz_koenig,
        gruen_seven,
        gruen_eight,
        gruen_nine,
        gruen_koenig,
        schellen_sau,
    ]
    assert wants_to_play_ramsch(with_blanc_sau) is False


def test_wants_to_double_game_value_true_for_very_strong_half_hand(
    eichel_ober, gruen_ober, eichel_sau, gruen_sau
):
    # 2 Ober + 2 Sau = 9.0, well above the threshold - the doubling
    # decision is made after seeing only these 4 cards.
    half_hand = [eichel_ober, gruen_ober, eichel_sau, gruen_sau]

    assert wants_to_double_game_value(half_hand) is True


def test_wants_to_double_game_value_true_at_threshold(
    eichel_unter, gruen_unter, herz_unter, schellen_unter
):
    # All 4 Unter = 8.0, exactly at the threshold.
    half_hand = [eichel_unter, gruen_unter, herz_unter, schellen_unter]

    assert wants_to_double_game_value(half_hand) is True


def test_wants_to_double_game_value_false_for_decent_but_not_great_half_hand(
    eichel_ober, eichel_unter, eichel_sau, eichel_koenig
):
    # 1 Ober + 1 Unter + 1 Sau + filler = 6.5 - a fine start, but not the
    # "very very good" hand needed to risk doubling the stakes.
    half_hand = [eichel_ober, eichel_unter, eichel_sau, eichel_koenig]

    assert wants_to_double_game_value(half_hand) is False


def test_wants_to_double_game_value_false_for_average_half_hand(
    eichel_seven, eichel_eight, eichel_nine, eichel_koenig
):
    half_hand = [eichel_seven, eichel_eight, eichel_nine, eichel_koenig]

    assert wants_to_double_game_value(half_hand) is False


def test_bot_ask_double_game_value_delegates_to_wants_to_double_game_value(
    eichel_ober,
    gruen_ober,
    eichel_sau,
    gruen_sau,
    eichel_seven,
    eichel_eight,
    eichel_nine,
    eichel_koenig,
):
    strong_half_hand = [eichel_ober, gruen_ober, eichel_sau, gruen_sau]
    weak_half_hand = [eichel_seven, eichel_eight, eichel_nine, eichel_koenig]

    assert _bot(strong_half_hand).ask_double_game_value() is True
    assert _bot(weak_half_hand).ask_double_game_value() is False


def test_bot_ask_for_ramsch_delegates_to_wants_to_play_ramsch(
    eichel_seven,
    eichel_eight,
    eichel_nine,
    eichel_koenig,
    gruen_seven,
    gruen_eight,
    schellen_seven,
    schellen_eight,
    eichel_ober,
    gruen_ober,
    herz_ober,
    schellen_ober,
    eichel_unter,
    gruen_unter,
    herz_sau,
    herz_koenig,
):
    safe_hand = [
        eichel_seven,
        eichel_eight,
        eichel_nine,
        eichel_koenig,
        gruen_seven,
        gruen_eight,
        schellen_seven,
        schellen_eight,
    ]
    risky_hand = [
        eichel_ober,
        gruen_ober,
        herz_ober,
        schellen_ober,
        eichel_unter,
        gruen_unter,
        herz_sau,
        herz_koenig,
    ]

    assert _bot(safe_hand).ask_for_ramsch() is True
    assert _bot(risky_hand).ask_for_ramsch() is False
