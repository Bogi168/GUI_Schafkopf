from unittest.mock import MagicMock

from card_classes.Cards import Color, Type
from input_validators.GameDecisionValidator import GameDecisionValidator
from player_classes.Player import Bot
from player_classes.bot_strategy import (
    best_hochzeit_swap_card,
    best_trump_color,
    ramsch_risk,
    wants_to_double_game_value,
    wants_to_partner_hochzeit,
    wants_to_play,
    wants_to_play_ramsch,
    wants_to_shoot,
)


def _is_trump(card):
    return card.card_type in (Type.OBER, Type.UNTER) or card.card_color == Color.HERZ


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


def test_wants_to_shoot_true_with_majority_of_trumps(sauspiel_trumps):
    # All 4 Ober + all 4 Unter = 8 of the 14 Sauspiel trumps - far above the
    # "6 trumps with some higher Obers" bar.
    hand = sauspiel_trumps[:8]

    assert wants_to_shoot(hand, sauspiel_trumps) is True


def test_wants_to_shoot_true_at_normal_threshold(
    eichel_ober,
    gruen_ober,
    herz_sau,
    herz_ten,
    herz_koenig,
    herz_nine,
    eichel_seven,
    gruen_seven,
    sauspiel_trumps,
):
    # 2 Ober (6.0) + 4 Herz trumps (4.0) = 10.0 - exactly "6 trumps with
    # some of the higher Obers".
    hand = [
        eichel_ober,
        gruen_ober,
        herz_sau,
        herz_ten,
        herz_koenig,
        herz_nine,
        eichel_seven,
        gruen_seven,
    ]

    assert wants_to_shoot(hand, sauspiel_trumps) is True


def test_wants_to_shoot_false_below_normal_threshold(
    eichel_ober,
    eichel_unter,
    herz_sau,
    herz_ten,
    herz_koenig,
    herz_nine,
    eichel_seven,
    gruen_seven,
    sauspiel_trumps,
):
    # 1 Ober (3.0) + 1 Unter (2.0) + 4 Herz trumps (4.0) = 9.0 - just below
    # the threshold.
    hand = [
        eichel_ober,
        eichel_unter,
        herz_sau,
        herz_ten,
        herz_koenig,
        herz_nine,
        eichel_seven,
        gruen_seven,
    ]

    assert wants_to_shoot(hand, sauspiel_trumps) is False


def test_wants_to_shoot_true_with_majority_of_wenz_trumps(
    wenz_trumps,
    eichel_unter,
    gruen_unter,
    herz_unter,
    eichel_sau,
    gruen_sau,
    schellen_sau,
    eichel_koenig,
    gruen_koenig,
):
    # 3 of the 4 Unter - the chooser can hold at most 1.
    hand = [
        eichel_unter,
        gruen_unter,
        herz_unter,
        eichel_sau,
        gruen_sau,
        schellen_sau,
        eichel_koenig,
        gruen_koenig,
    ]

    assert wants_to_shoot(hand, wenz_trumps) is True


def test_wants_to_shoot_false_with_half_of_wenz_trumps(
    wenz_trumps,
    eichel_unter,
    gruen_unter,
    eichel_sau,
    gruen_sau,
    schellen_sau,
    eichel_koenig,
    gruen_koenig,
    schellen_koenig,
):
    # Only 2 of the 4 Unter - no guaranteed majority.
    hand = [
        eichel_unter,
        gruen_unter,
        eichel_sau,
        gruen_sau,
        schellen_sau,
        eichel_koenig,
        gruen_koenig,
        schellen_koenig,
    ]

    assert wants_to_shoot(hand, wenz_trumps) is False


def test_wants_to_shoot_false_without_trumps(sauspiel_trumps):
    # An empty trumps list means the game mode is unknown - shooting
    # cannot be judged without it.
    hand = sauspiel_trumps[:8]

    assert wants_to_shoot(hand, []) is False


def test_wants_to_shoot_ramsch_true_for_low_risk_hand(
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

    assert wants_to_shoot(hand, [], is_ramsch=True) is True


def test_wants_to_shoot_ramsch_false_for_trump_heavy_hand(
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

    assert wants_to_shoot(hand, [], is_ramsch=True) is False


def test_wants_to_shoot_tout_false_when_higher_trumps_can_block_every_trick(
    herz_ober, schellen_ober, sauspiel_trumps
):
    # Herz Ober and Schellen Ober rank below Eichel Ober and Gruen Ober - if
    # the game chooser plays those two Ober in the first two rounds, neither
    # held trump can ever win a trick.
    hand = [herz_ober, schellen_ober]

    assert wants_to_shoot(hand, sauspiel_trumps, is_tout=True) is False


def test_wants_to_shoot_tout_true_with_an_extra_trump_to_outlast_higher_ones(
    herz_ober, schellen_ober, eichel_unter, sauspiel_trumps
):
    # The chooser can only play Eichel Ober and Gruen Ober once each - in
    # one of those two rounds this hand can play its third trump and keep
    # an Ober for a guaranteed trick win.
    hand = [herz_ober, schellen_ober, eichel_unter]

    assert wants_to_shoot(hand, sauspiel_trumps, is_tout=True) is True


def test_wants_to_shoot_tout_false_without_any_trumps_held(eichel_sau, sauspiel_trumps):
    hand = [eichel_sau]

    assert wants_to_shoot(hand, sauspiel_trumps, is_tout=True) is False


def test_wants_to_shoot_wenz_tout_true_holding_strongest_unter_alone(
    eichel_unter, wenz_trumps
):
    # Eichel Unter is the strongest of the 4 trumps - no other trump can
    # ever beat it.
    hand = [eichel_unter]

    assert wants_to_shoot(hand, wenz_trumps, is_tout=True) is True


def test_wants_to_shoot_wenz_tout_false_holding_only_lower_trumps(
    herz_unter, schellen_unter, wenz_trumps
):
    # Herz Unter and Schellen Unter rank below Eichel Unter and Gruen Unter -
    # if the game chooser plays those two first, neither held trump can ever
    # win a trick.
    hand = [herz_unter, schellen_unter]

    assert wants_to_shoot(hand, wenz_trumps, is_tout=True) is False


def test_wants_to_shoot_wenz_tout_true_with_three_lower_trumps(
    gruen_unter, herz_unter, schellen_unter, wenz_trumps
):
    # Holding 3 of the 4 trumps guarantees a trick even if the chooser
    # holds the strongest one.
    hand = [gruen_unter, herz_unter, schellen_unter]

    assert wants_to_shoot(hand, wenz_trumps, is_tout=True) is True


def test_bot_ask_shoot_delegates_to_wants_to_shoot(
    eichel_ober,
    gruen_ober,
    eichel_unter,
    herz_sau,
    herz_ten,
    herz_koenig,
    herz_nine,
    eichel_seven,
    gruen_seven,
    sauspiel_trumps,
):
    strong_hand = [
        eichel_ober,
        gruen_ober,
        herz_sau,
        herz_ten,
        herz_koenig,
        herz_nine,
        eichel_seven,
        gruen_seven,
    ]
    weak_hand = [
        eichel_ober,
        eichel_unter,
        herz_sau,
        herz_ten,
        herz_koenig,
        herz_nine,
        eichel_seven,
        gruen_seven,
    ]

    assert _bot(strong_hand).ask_shoot(trumps=sauspiel_trumps) is True
    assert _bot(weak_hand).ask_shoot(trumps=sauspiel_trumps) is False


def test_bot_ask_shoot_without_trumps_defaults_to_false(sauspiel_trumps):
    assert _bot(sauspiel_trumps[:8]).ask_shoot() is False


def test_bot_ask_shoot_tout_delegates_to_can_guarantee_a_trick(
    herz_ober, schellen_ober, eichel_unter, sauspiel_trumps
):
    no_extra_trump = _bot([herz_ober, schellen_ober])
    with_extra_trump = _bot([herz_ober, schellen_ober, eichel_unter])

    assert no_extra_trump.ask_shoot(trumps=sauspiel_trumps, is_tout=True) is False
    assert with_extra_trump.ask_shoot(trumps=sauspiel_trumps, is_tout=True) is True


def test_bot_ask_shoot_ramsch_delegates_to_wants_to_play_ramsch(
    eichel_seven,
    eichel_eight,
    eichel_nine,
    eichel_koenig,
    gruen_seven,
    gruen_eight,
    schellen_seven,
    schellen_eight,
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

    assert _bot(safe_hand).ask_shoot(is_ramsch=True) is True


def test_wants_to_partner_hochzeit_true_for_strong_hand(
    eichel_ober,
    gruen_ober,
    herz_ober,
    eichel_unter,
    eichel_seven,
    eichel_eight,
    gruen_seven,
    gruen_eight,
):
    # 3 Ober + 1 Unter = 11.0, well above the partner threshold, with
    # plenty of non-trump cards to hand over in the swap.
    hand = [
        eichel_ober,
        gruen_ober,
        herz_ober,
        eichel_unter,
        eichel_seven,
        eichel_eight,
        gruen_seven,
        gruen_eight,
    ]

    assert wants_to_partner_hochzeit(hand) is True


def test_wants_to_partner_hochzeit_true_at_threshold(
    eichel_ober,
    gruen_ober,
    eichel_unter,
    gruen_unter,
    eichel_seven,
    eichel_eight,
    gruen_seven,
    gruen_eight,
):
    # 2 Ober + 2 Unter = 10.0, exactly at the partner threshold.
    hand = [
        eichel_ober,
        gruen_ober,
        eichel_unter,
        gruen_unter,
        eichel_seven,
        eichel_eight,
        gruen_seven,
        gruen_eight,
    ]

    assert wants_to_partner_hochzeit(hand) is True


def test_wants_to_partner_hochzeit_false_for_decent_but_not_strong_hand(
    eichel_ober,
    eichel_unter,
    herz_sau,
    herz_ten,
    herz_koenig,
    herz_nine,
    eichel_seven,
    gruen_seven,
):
    # 1 Ober + 1 Unter + 4 Herz trumps = 9.0 - a fine Sauspiel hand, but
    # not strong enough to carry a Hochzeit team almost alone.
    hand = [
        eichel_ober,
        eichel_unter,
        herz_sau,
        herz_ten,
        herz_koenig,
        herz_nine,
        eichel_seven,
        gruen_seven,
    ]

    assert wants_to_partner_hochzeit(hand) is False


def test_wants_to_partner_hochzeit_false_for_all_trump_hand(
    eichel_ober,
    gruen_ober,
    herz_ober,
    schellen_ober,
    eichel_unter,
    gruen_unter,
    herz_unter,
    schellen_unter,
):
    # Strength 20.0, but every card is a trump - there is no legal card to
    # hand over in the swap, so accepting is impossible (mirrors the
    # allow_yes rule for human players).
    hand = [
        eichel_ober,
        gruen_ober,
        herz_ober,
        schellen_ober,
        eichel_unter,
        gruen_unter,
        herz_unter,
        schellen_unter,
    ]

    assert wants_to_partner_hochzeit(hand) is False


def test_best_hochzeit_swap_card_sheds_blanc_card_to_create_a_void(
    eichel_ober,
    eichel_unter,
    herz_sau,
    gruen_seven,
    schellen_seven,
    schellen_eight,
):
    # Gruen Seven is the only Gruen card - shedding it voids the suit.
    hand = [
        eichel_ober,
        eichel_unter,
        herz_sau,
        gruen_seven,
        schellen_seven,
        schellen_eight,
    ]
    legal_cards = [card for card in hand if not _is_trump(card)]

    assert best_hochzeit_swap_card(hand, legal_cards) is gruen_seven


def test_best_hochzeit_swap_card_keeps_a_blanc_sau(
    eichel_ober,
    eichel_unter,
    herz_sau,
    gruen_sau,
    schellen_seven,
    schellen_eight,
):
    # Gruen Sau is blanc, but a Sau is a likely trick winner - the bot
    # sheds from the longer Schellen suit instead.
    hand = [
        eichel_ober,
        eichel_unter,
        herz_sau,
        gruen_sau,
        schellen_seven,
        schellen_eight,
    ]
    legal_cards = [card for card in hand if not _is_trump(card)]

    assert best_hochzeit_swap_card(hand, legal_cards) is schellen_seven


def test_best_hochzeit_swap_card_sheds_weakest_card_of_suit(
    eichel_ober,
    schellen_koenig,
    schellen_ten,
    schellen_seven,
):
    hand = [eichel_ober, schellen_koenig, schellen_ten, schellen_seven]
    legal_cards = [schellen_koenig, schellen_ten, schellen_seven]

    assert best_hochzeit_swap_card(hand, legal_cards) is schellen_seven


def test_best_hochzeit_swap_card_returns_forced_choice(
    herz_koenig, gruen_sau, eichel_seven
):
    # The game chooser's only legal card is their single trump; a Sau is
    # shed when it is the only legal card.
    hand = [herz_koenig, gruen_sau, eichel_seven]

    assert best_hochzeit_swap_card(hand, [herz_koenig]) is herz_koenig
    assert best_hochzeit_swap_card(hand, [gruen_sau]) is gruen_sau


def test_bot_ask_for_hochzeit_delegates_to_wants_to_partner_hochzeit(
    eichel_ober,
    gruen_ober,
    herz_ober,
    eichel_unter,
    eichel_seven,
    eichel_eight,
    gruen_seven,
    gruen_eight,
    herz_sau,
    herz_ten,
    herz_koenig,
    herz_nine,
):
    strong_hand = [
        eichel_ober,
        gruen_ober,
        herz_ober,
        eichel_unter,
        eichel_seven,
        eichel_eight,
        gruen_seven,
        gruen_eight,
    ]
    weak_hand = [
        eichel_ober,
        eichel_unter,
        herz_sau,
        herz_ten,
        herz_koenig,
        herz_nine,
        eichel_seven,
        gruen_seven,
    ]

    assert _bot(strong_hand).ask_for_hochzeit() is True
    assert _bot(weak_hand).ask_for_hochzeit() is False


def test_bot_get_card_swap_decision_uses_best_hochzeit_swap_card(
    eichel_ober,
    eichel_unter,
    herz_sau,
    gruen_seven,
    schellen_seven,
    schellen_eight,
):
    bot = _bot(
        [
            eichel_ober,
            eichel_unter,
            herz_sau,
            gruen_seven,
            schellen_seven,
            schellen_eight,
        ]
    )

    decision = bot.get_card_swap_decision(
        move_validator=lambda card: not _is_trump(card)
    )

    assert decision is gruen_seven
    assert gruen_seven not in bot.player_cards


# wants_to_play: baseline mode playability


def test_wants_to_play_false_when_no_baseline_mode_playable(
    eichel_sau,
    gruen_sau,
    schellen_sau,
    eichel_ober,
    herz_ten,
    herz_seven,
    eichel_seven,
    gruen_seven,
):
    # Three Saus and an Ober: comfortably above the want-to-play threshold,
    # but every callable color's Sau is in hand and three trumps rule out
    # a Hochzeit - volunteering would force an unsuited Wenz/Solo.
    hand = [
        eichel_sau,
        gruen_sau,
        schellen_sau,
        eichel_ober,
        herz_ten,
        herz_seven,
        eichel_seven,
        gruen_seven,
    ]

    assert (
        wants_to_play(
            hand, players_who_want_to_play_count=0, baseline_mode_playable=False
        )
        is False
    )
    assert (
        wants_to_play(
            hand, players_who_want_to_play_count=0, baseline_mode_playable=True
        )
        is True
    )


def test_wants_to_play_solo_hand_ignores_baseline_playability(
    eichel_ober, gruen_ober, herz_ober, herz_sau, herz_ten
):
    # A hand at Solo strength is worth volunteering even if neither
    # Sauspiel nor Hochzeit would be legal.
    hand = [eichel_ober, gruen_ober, herz_ober, herz_sau, herz_ten]

    assert (
        wants_to_play(
            hand, players_who_want_to_play_count=0, baseline_mode_playable=False
        )
        is True
    )


def test_bot_ask_want_choose_game_vetoes_hand_without_legal_baseline_mode(
    eichel_sau,
    gruen_sau,
    schellen_sau,
    schellen_seven,
    eichel_ober,
    herz_ten,
    herz_seven,
    eichel_seven,
    gruen_seven,
):
    bot = Bot(
        bot_name="Bot 1",
        renderer=MagicMock(),
        game_decision_validator=GameDecisionValidator(choosable_game_rank_mapping={}),
    )

    # All three Saus in hand: no callable color, three trumps: no Hochzeit.
    bot.player_cards = [
        eichel_sau,
        gruen_sau,
        schellen_sau,
        eichel_ober,
        herz_ten,
        herz_seven,
        eichel_seven,
        gruen_seven,
    ]
    assert bot.ask_want_choose_game(players_who_want_to_play_count=0) is False

    # Swapping the Schellen Sau for the Seven makes Schellen callable.
    bot.player_cards = [
        eichel_sau,
        gruen_sau,
        schellen_seven,
        eichel_ober,
        herz_ten,
        herz_seven,
        eichel_seven,
        gruen_seven,
    ]
    assert bot.ask_want_choose_game(players_who_want_to_play_count=0) is True


# best_trump_color


def test_best_trump_color_picks_longest_color(
    eichel_seven, eichel_eight, eichel_nine, schellen_sau, schellen_ten
):
    cards = [eichel_seven, eichel_eight, eichel_nine, schellen_sau, schellen_ten]
    options = {
        "1": Color.EICHEL,
        "2": Color.GRUEN,
        "3": Color.HERZ,
        "4": Color.SCHELLEN,
    }

    assert best_trump_color(player_cards=cards, options=options) == Color.EICHEL


def test_best_trump_color_breaks_ties_with_higher_points(
    eichel_seven, eichel_eight, schellen_sau, schellen_ten
):
    cards = [eichel_seven, eichel_eight, schellen_sau, schellen_ten]
    options = {
        "1": Color.EICHEL,
        "2": Color.GRUEN,
        "3": Color.HERZ,
        "4": Color.SCHELLEN,
    }

    # Eichel and Schellen are equally long, but the Schellen Sau and Ten
    # become near-unbeatable trumps - pick Schellen.
    assert best_trump_color(player_cards=cards, options=options) == Color.SCHELLEN
