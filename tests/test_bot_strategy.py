from unittest.mock import MagicMock

from player_classes.Player import Bot
from player_classes.bot_strategy import ramsch_risk, wants_to_play_ramsch


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
    herz_ober,
    eichel_unter,
    herz_sau,
    schellen_sau,
    eichel_koenig,
    eichel_nine,
    gruen_seven,
    gruen_eight,
    schellen_seven,
):
    # 1 Ober + 1 Unter + 1 Herz trump alone is risky but still acceptable...
    moderate_trumps = [
        herz_ober,
        eichel_unter,
        herz_sau,
        schellen_seven,
        eichel_koenig,
        eichel_nine,
        gruen_seven,
        gruen_eight,
    ]
    assert wants_to_play_ramsch(moderate_trumps) is True

    # ...but swapping the harmless blanc Schellen Sieben for a blanc
    # Schellen Sau tips the same hand into "no".
    with_blanc_sau = [
        herz_ober,
        eichel_unter,
        herz_sau,
        schellen_sau,
        eichel_koenig,
        eichel_nine,
        gruen_seven,
        gruen_eight,
    ]
    assert wants_to_play_ramsch(with_blanc_sau) is False


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
