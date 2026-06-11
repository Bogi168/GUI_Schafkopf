from card_classes.Cards import Color
from card_classes.CardPowerCalculator import (
    RamschCardPowerCalculator,
    SauspielCardPowerCalculator,
)
from player_classes.card_play_strategy import (
    CardPlayContext,
    _is_highest_remaining,
    _non_trump_suit_count,
    _players_void_of_trumps,
    _remaining_unseen_cards,
    _safe_low_card,
    choose_card_to_play,
)
from player_classes.team_knowledge import TeamKnowledge


class _FakePlayer:
    def __init__(self, player_cards):
        self.player_cards = player_cards


def _context(
    current_trick=(),
    trumps=(),
    cpc=None,
    history=(),
    teammates=(),
    opponents=(),
    unknown=(),
    is_ramsch=False,
    is_tout=False,
    is_active_team=False,
    is_solo_mode=False,
    call_sau=None,
    tricks_remaining=8,
    trick_history=(),
    known_trumpless=(),
):
    return CardPlayContext(
        current_trick=list(current_trick),
        trumps=list(trumps),
        card_power_calculator=cpc or SauspielCardPowerCalculator(),
        played_cards_history=list(history),
        team_knowledge=TeamKnowledge(
            teammates=list(teammates), opponents=list(opponents), unknown=list(unknown)
        ),
        is_ramsch=is_ramsch,
        is_tout=is_tout,
        is_active_team=is_active_team,
        is_solo_mode=is_solo_mode,
        call_sau=call_sau,
        tricks_remaining=tricks_remaining,
        trick_history=[list(trick) for trick in trick_history],
        known_trumpless=list(known_trumpless),
    )


# _remaining_unseen_cards


def test_remaining_unseen_cards_excludes_seen_cards(
    eichel_sau, eichel_ten, eichel_koenig, herz_sau
):
    unseen = _remaining_unseen_cards(
        own_hand=[eichel_sau],
        played_cards_history=[eichel_ten],
        current_trick_cards=[herz_sau],
    )

    assert eichel_sau not in unseen
    assert eichel_ten not in unseen
    assert herz_sau not in unseen
    assert eichel_koenig in unseen
    assert len(unseen) == 32 - 3


# _is_highest_remaining


def test_is_highest_remaining_true_for_strongest_trump(
    eichel_ober, gruen_ober, sauspiel_trumps
):
    cpc = SauspielCardPowerCalculator()

    assert _is_highest_remaining(eichel_ober, [gruen_ober], sauspiel_trumps, cpc) is True


def test_is_highest_remaining_false_when_higher_trump_unseen(
    gruen_ober, eichel_ober, sauspiel_trumps
):
    cpc = SauspielCardPowerCalculator()

    assert _is_highest_remaining(gruen_ober, [eichel_ober], sauspiel_trumps, cpc) is False


def test_is_highest_remaining_non_trump_beaten_by_unseen_trump(
    eichel_sau, gruen_unter, sauspiel_trumps
):
    cpc = SauspielCardPowerCalculator()

    assert _is_highest_remaining(eichel_sau, [gruen_unter], sauspiel_trumps, cpc) is False


def test_is_highest_remaining_non_trump_safe_with_only_lower_same_suit_unseen(
    eichel_sau, eichel_koenig, sauspiel_trumps
):
    cpc = SauspielCardPowerCalculator()

    assert _is_highest_remaining(eichel_sau, [eichel_koenig], sauspiel_trumps, cpc) is True


# _safe_low_card


def test_safe_low_card_prefers_zero_point_non_trump(
    eichel_ober, eichel_seven, gruen_koenig, sauspiel_trumps
):
    cpc = SauspielCardPowerCalculator()

    result = _safe_low_card([eichel_ober, eichel_seven, gruen_koenig], sauspiel_trumps, cpc)

    assert result == eichel_seven


def test_safe_low_card_picks_lowest_point_trump_when_only_trumps(
    eichel_unter, herz_ober, sauspiel_trumps
):
    cpc = SauspielCardPowerCalculator()

    result = _safe_low_card([eichel_unter, herz_ober], sauspiel_trumps, cpc)

    assert result == eichel_unter


# _non_trump_suit_count


def test_non_trump_suit_count_excludes_trumps(
    gruen_seven, gruen_koenig, gruen_unter, sauspiel_trumps
):
    cards = [gruen_seven, gruen_koenig, gruen_unter]

    assert _non_trump_suit_count(cards, Color.GRUEN, sauspiel_trumps) == 2


# choose_card_to_play - trivial case


def test_single_legal_card_is_returned_immediately(eichel_sau, sauspiel_trumps):
    player = _FakePlayer(player_cards=[eichel_sau])
    context = _context(trumps=sauspiel_trumps)

    assert choose_card_to_play(player, [eichel_sau], context) == eichel_sau


# choose_card_to_play - leading


def test_lead_ramsch_picks_lowest_point_non_trump(
    eichel_koenig, gruen_seven, herz_ober, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[eichel_koenig, gruen_seven, herz_ober])
    context = _context(trumps=sauspiel_trumps, is_ramsch=True)

    result = choose_card_to_play(
        player, [eichel_koenig, gruen_seven, herz_ober], context
    )

    assert result == gruen_seven


def test_lead_tout_chooser_plays_strongest_card(
    eichel_seven, herz_ober, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[eichel_seven, herz_ober])
    context = _context(trumps=sauspiel_trumps, is_tout=True, teammates=[])

    result = choose_card_to_play(player, [eichel_seven, herz_ober], context)

    assert result == herz_ober


def test_lead_guaranteed_trump_is_played(eichel_ober, eichel_seven, sauspiel_trumps):
    player = _FakePlayer(player_cards=[eichel_ober, eichel_seven])
    context = _context(trumps=sauspiel_trumps)

    result = choose_card_to_play(player, [eichel_ober, eichel_seven], context)

    assert result == eichel_ober


def test_lead_active_team_draws_trump_early(eichel_sau, gruen_ober, sauspiel_trumps):
    player = _FakePlayer(player_cards=[gruen_ober, eichel_sau])
    context = _context(trumps=sauspiel_trumps, is_active_team=True, tricks_remaining=8)

    result = choose_card_to_play(player, [gruen_ober, eichel_sau], context)

    assert result == gruen_ober


def test_lead_non_active_team_does_not_draw_trump_early(
    eichel_sau, gruen_ober, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[gruen_ober, eichel_sau])
    context = _context(trumps=sauspiel_trumps, is_active_team=False, tricks_remaining=8)

    result = choose_card_to_play(player, [gruen_ober, eichel_sau], context)

    assert result == eichel_sau


def test_lead_active_team_trump_draw_only_applies_early_game(
    eichel_sau, gruen_ober, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[gruen_ober, eichel_sau])
    context = _context(trumps=sauspiel_trumps, is_active_team=True, tricks_remaining=2)

    result = choose_card_to_play(player, [gruen_ober, eichel_sau], context)

    assert result == eichel_sau


def test_lead_solo_chooser_draws_trump_even_after_shoot_flips_active_team(
    eichel_sau, gruen_ober, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[gruen_ober, eichel_sau])
    context = _context(
        trumps=sauspiel_trumps,
        is_solo_mode=True,
        teammates=[],
        is_active_team=False,
        tricks_remaining=8,
    )

    result = choose_card_to_play(player, [gruen_ober, eichel_sau], context)

    assert result == gruen_ober


def test_lead_solo_defender_does_not_draw_trump_even_after_shoot_flips_active_team(
    eichel_sau, gruen_ober, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[gruen_ober, eichel_sau])
    context = _context(
        trumps=sauspiel_trumps,
        is_solo_mode=True,
        teammates=["teammate"],
        is_active_team=True,
        tricks_remaining=8,
    )

    result = choose_card_to_play(player, [gruen_ober, eichel_sau], context)

    assert result == eichel_sau


def test_lead_early_sau_is_played(eichel_sau, gruen_seven, gruen_koenig, sauspiel_trumps):
    player = _FakePlayer(player_cards=[eichel_sau, gruen_seven, gruen_koenig])
    context = _context(trumps=sauspiel_trumps, tricks_remaining=8)

    result = choose_card_to_play(player, [eichel_sau, gruen_seven], context)

    assert result == eichel_sau


def test_lead_shortest_suit_when_no_safe_sau(
    gruen_seven, gruen_koenig, schellen_eight, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[gruen_seven, gruen_koenig, schellen_eight])
    context = _context(trumps=sauspiel_trumps, tricks_remaining=2)

    result = choose_card_to_play(player, [gruen_seven, schellen_eight], context)

    assert result == schellen_eight


def test_lead_fallback_picks_lowest_point_trump(
    herz_unter, eichel_unter, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[herz_unter, eichel_unter])
    context = _context(trumps=sauspiel_trumps)

    result = choose_card_to_play(player, [herz_unter, eichel_unter], context)

    assert result == herz_unter


# choose_card_to_play - leading, call sau seeking/avoiding/running away


def test_lead_seeks_call_sau_color_when_not_active_team(
    eichel_sau, eichel_koenig, eichel_seven, gruen_unter, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[eichel_koenig, eichel_seven, gruen_unter])
    context = _context(trumps=sauspiel_trumps, is_active_team=False, call_sau=eichel_sau)

    result = choose_card_to_play(
        player, [eichel_koenig, eichel_seven, gruen_unter], context
    )

    assert result == eichel_seven


def test_lead_active_team_avoids_call_sau_color(
    eichel_sau, eichel_koenig, gruen_seven, gruen_eight, herz_seven, sauspiel_trumps
):
    player_cards = [eichel_koenig, gruen_seven, gruen_eight, herz_seven]
    player = _FakePlayer(player_cards=player_cards)
    context = _context(
        trumps=sauspiel_trumps,
        is_active_team=True,
        call_sau=eichel_sau,
        tricks_remaining=2,
    )

    result = choose_card_to_play(player, player_cards, context)

    assert result == gruen_seven


def test_lead_active_team_can_lead_call_sau_color_when_no_trumps_left(
    eichel_sau, eichel_koenig, gruen_seven, gruen_eight, sauspiel_trumps
):
    player_cards = [eichel_koenig, gruen_seven, gruen_eight]
    player = _FakePlayer(player_cards=player_cards)
    context = _context(trumps=sauspiel_trumps, is_active_team=True, call_sau=eichel_sau)

    result = choose_card_to_play(player, player_cards, context)

    # Without any trumps left, the chooser can no longer be put under
    # Sau-Zwang on a later trick - leading the called colour is legit.
    assert result == eichel_koenig


def test_lead_active_team_can_lead_call_sau_color_once_revealed(
    eichel_sau, eichel_koenig, gruen_seven, gruen_eight, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[eichel_koenig, gruen_seven, gruen_eight])
    context = _context(
        trumps=sauspiel_trumps,
        is_active_team=True,
        call_sau=eichel_sau,
        history=[eichel_sau],
    )

    result = choose_card_to_play(
        player, [eichel_koenig, gruen_seven, gruen_eight], context
    )

    assert result == eichel_koenig


def test_lead_call_sau_holder_runs_away_with_long_suit(
    eichel_sau, eichel_koenig, eichel_ten, eichel_seven, gruen_seven, sauspiel_trumps
):
    player_cards = [eichel_sau, eichel_koenig, eichel_ten, eichel_seven, gruen_seven]
    player = _FakePlayer(player_cards=player_cards)
    context = _context(
        trumps=sauspiel_trumps, is_active_team=True, call_sau=eichel_sau, tricks_remaining=8
    )

    result = choose_card_to_play(player, player_cards, context)

    # Davonlaufen: lead a non-Sau card of the called colour, keeping the
    # Sau itself hidden.
    assert result == eichel_seven


def test_lead_call_sau_holder_does_not_run_away_with_short_suit(
    eichel_sau, gruen_seven, gruen_eight, herz_seven, sauspiel_trumps
):
    player_cards = [eichel_sau, gruen_seven, gruen_eight, herz_seven]
    player = _FakePlayer(player_cards=player_cards)
    context = _context(
        trumps=sauspiel_trumps, is_active_team=True, call_sau=eichel_sau, tricks_remaining=2
    )

    result = choose_card_to_play(player, player_cards, context)

    assert result == gruen_seven


def test_lead_call_sau_holder_can_play_call_sau_when_no_trumps_left(
    eichel_sau, gruen_seven, gruen_eight, sauspiel_trumps
):
    player_cards = [eichel_sau, gruen_seven, gruen_eight]
    player = _FakePlayer(player_cards=player_cards)
    context = _context(
        trumps=sauspiel_trumps, is_active_team=True, call_sau=eichel_sau, tricks_remaining=8
    )

    result = choose_card_to_play(player, player_cards, context)

    # Without any trumps left, the holder can no longer be put under
    # Sau-Zwang on a later trick - playing the call sau now is legit.
    assert result == eichel_sau


def test_lead_call_sau_holder_can_play_call_sau_when_opponents_void_of_trumps(
    eichel_sau,
    gruen_seven,
    gruen_eight,
    herz_seven,
    herz_ober,
    schellen_seven,
    schellen_eight,
    schellen_nine,
    sauspiel_trumps,
    player_1,
    player_2,
    player_3,
    player_4,
):
    player_cards = [eichel_sau, gruen_seven, gruen_eight, herz_seven]
    player = _FakePlayer(player_cards=player_cards)
    # player_2 led a trump and both opponents (player_3, player_4) followed
    # with non-trump cards - Trumpfzwang proves they're void of trumps.
    trick_history = [
        [
            (player_2, herz_ober),
            (player_3, schellen_seven),
            (player_4, schellen_eight),
            (player_1, schellen_nine),
        ]
    ]
    context = _context(
        trumps=sauspiel_trumps,
        is_active_team=True,
        call_sau=eichel_sau,
        tricks_remaining=2,
        opponents=[player_3, player_4],
        trick_history=trick_history,
    )

    result = choose_card_to_play(player, player_cards, context)

    assert result == eichel_sau


def test_lead_call_sau_holder_avoids_when_only_one_opponent_void_of_trumps(
    eichel_sau,
    gruen_seven,
    gruen_eight,
    herz_seven,
    herz_ober,
    herz_unter,
    schellen_seven,
    schellen_nine,
    sauspiel_trumps,
    player_1,
    player_2,
    player_3,
    player_4,
):
    player_cards = [eichel_sau, gruen_seven, gruen_eight, herz_seven]
    player = _FakePlayer(player_cards=player_cards)
    # player_4 followed the trump lead with a trump itself, so only
    # player_3 is proven void - not enough to relax the avoidance.
    trick_history = [
        [
            (player_2, herz_ober),
            (player_3, schellen_seven),
            (player_4, herz_unter),
            (player_1, schellen_nine),
        ]
    ]
    context = _context(
        trumps=sauspiel_trumps,
        is_active_team=True,
        call_sau=eichel_sau,
        tricks_remaining=2,
        opponents=[player_3, player_4],
        trick_history=trick_history,
    )

    result = choose_card_to_play(player, player_cards, context)

    assert result == gruen_seven


def test_lead_call_sau_holder_does_not_run_away_late_game(
    eichel_sau, eichel_koenig, eichel_ten, eichel_seven, gruen_seven, sauspiel_trumps
):
    player_cards = [eichel_sau, eichel_koenig, eichel_ten, eichel_seven, gruen_seven]
    player = _FakePlayer(player_cards=player_cards)
    context = _context(
        trumps=sauspiel_trumps, is_active_team=True, call_sau=eichel_sau, tricks_remaining=2
    )

    result = choose_card_to_play(player, player_cards, context)

    assert result == gruen_seven


# choose_card_to_play - following, teammate currently winning


def test_follow_does_not_overtake_winning_teammate(
    herz_ober, eichel_ober, eichel_seven, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[eichel_ober, eichel_seven])
    context = _context(
        current_trick=[("teammate", herz_ober)],
        trumps=sauspiel_trumps,
        teammates=["teammate"],
    )

    result = choose_card_to_play(player, [eichel_ober, eichel_seven], context)

    assert result == eichel_seven


def test_follow_overtaking_teammates_trump_uses_smallest_sufficient_trump(
    schellen_unter, herz_unter, eichel_ober, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[herz_unter, eichel_ober])
    context = _context(
        current_trick=[("teammate", schellen_unter)],
        trumps=sauspiel_trumps,
        teammates=["teammate"],
    )

    result = choose_card_to_play(player, [herz_unter, eichel_ober], context)

    # Teammate's trump already wins the trick. Forced to follow with a
    # trump, the smallest one that's still stronger than the teammate's
    # card (Herz Unter) is the first trump above Schellen Unter - playing
    # the strongest trump in hand (Eichel Ober) here wouldn't be ideal.
    assert result == herz_unter


def test_follow_extends_teammates_non_trump_lead_with_sau(
    gruen_koenig, gruen_sau, gruen_seven, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[gruen_sau, gruen_seven])
    context = _context(
        current_trick=[("teammate", gruen_koenig)],
        trumps=sauspiel_trumps,
        teammates=["teammate"],
    )

    result = choose_card_to_play(player, [gruen_sau, gruen_seven], context)

    # Teammate's König already wins the trick, but a later opponent could
    # still overtake it with the Gruen Zehn. Playing the Sau locks in the
    # trick for the team and adds 11 points instead of 0.
    assert result == gruen_sau


def test_follow_schmiers_teammate_when_safe(
    eichel_ober, herz_sau, gruen_seven, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[herz_sau, gruen_seven])
    context = _context(
        current_trick=[("teammate", eichel_ober)],
        trumps=sauspiel_trumps,
        teammates=["teammate"],
    )

    result = choose_card_to_play(player, [herz_sau, gruen_seven], context)

    assert result == herz_sau


def test_follow_holds_back_when_schmiering_is_risky(
    gruen_ober, herz_sau, gruen_seven, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[herz_sau, gruen_seven])
    # Both opponents still have to act and could hold a higher trump.
    context = _context(
        current_trick=[("teammate", gruen_ober)],
        trumps=sauspiel_trumps,
        teammates=["teammate"],
        opponents=["opp1", "opp2"],
    )

    result = choose_card_to_play(player, [herz_sau, gruen_seven], context)

    assert result == gruen_seven


def test_follow_schmiers_when_last_to_act_even_if_risky(
    eichel_seven, schellen_eight, gruen_ober, herz_sau, gruen_seven, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[herz_sau, gruen_seven])
    context = _context(
        current_trick=[
            ("opp1", eichel_seven),
            ("opp2", schellen_eight),
            ("teammate", gruen_ober),
        ],
        trumps=sauspiel_trumps,
        teammates=["teammate"],
    )

    result = choose_card_to_play(player, [herz_sau, gruen_seven], context)

    assert result == herz_sau


def test_follow_schmier_skips_unter_in_favour_of_lower_value_non_trump(
    eichel_ober, schellen_unter, gruen_seven, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[schellen_unter, gruen_seven])
    context = _context(
        current_trick=[("teammate", eichel_ober)],
        trumps=sauspiel_trumps,
        teammates=["teammate"],
    )

    result = choose_card_to_play(player, [schellen_unter, gruen_seven], context)

    # Eichel Ober is unbeatable, so schmieren is safe - but Schellen Unter
    # is too valuable a trump to give away for its 2 points, even though
    # it's worth more than the 0-point Gruen Sieben.
    assert result == gruen_seven


def test_follow_schmier_falls_back_to_safe_low_card_when_only_trumps_legal(
    eichel_ober, schellen_unter, herz_unter, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[schellen_unter, herz_unter])
    context = _context(
        current_trick=[("teammate", eichel_ober)],
        trumps=sauspiel_trumps,
        teammates=["teammate"],
    )

    result = choose_card_to_play(player, [schellen_unter, herz_unter], context)

    # Both legal cards are Unter - no non-trump-type card to schmier with,
    # so fall back to the cheapest trump.
    assert result == schellen_unter


def test_follow_trumps_in_when_call_sau_owner_will_be_forced(
    eichel_sau, eichel_seven, schellen_unter, gruen_seven, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[schellen_unter, gruen_seven])
    context = _context(
        current_trick=[("teammate", eichel_seven)],
        trumps=sauspiel_trumps,
        call_sau=eichel_sau,
    )

    result = choose_card_to_play(player, [schellen_unter, gruen_seven], context)

    # Our team mate led a low Eichel, seeking the call sau. We're void of
    # Eichel ourselves but hold a trump - the call sau's holder is now
    # forced (Sau-Zwang) to play it into this trick, so trump in to claim
    # those 11 points instead of ducking with junk from another suit.
    assert result == schellen_unter


# choose_card_to_play - following, opponent (or unknown) currently winning


def test_follow_takes_high_value_trick_cheaply(
    herz_sau, herz_unter, gruen_seven, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[herz_unter, gruen_seven])
    context = _context(current_trick=[("opponent", herz_sau)], trumps=sauspiel_trumps)

    result = choose_card_to_play(player, [herz_unter, gruen_seven], context)

    assert result == herz_unter


def test_follow_skips_low_value_trick_when_a_losing_card_is_available(
    gruen_eight, gruen_ober, gruen_seven, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[gruen_ober, gruen_seven])
    context = _context(current_trick=[("opponent", gruen_eight)], trumps=sauspiel_trumps)

    result = choose_card_to_play(player, [gruen_ober, gruen_seven], context)

    assert result == gruen_seven


def test_follow_forced_to_win_low_value_trick_plays_cheapest_winner(
    gruen_eight, gruen_ober, eichel_ober, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[gruen_ober, eichel_ober])
    context = _context(current_trick=[("opponent", gruen_eight)], trumps=sauspiel_trumps)

    result = choose_card_to_play(player, [gruen_ober, eichel_ober], context)

    assert result == gruen_ober


def test_follow_dumps_junk_when_cannot_win(
    eichel_ober, herz_sau, gruen_seven, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[herz_sau, gruen_seven])
    context = _context(current_trick=[("opponent", eichel_ober)], trumps=sauspiel_trumps)

    result = choose_card_to_play(player, [herz_sau, gruen_seven], context)

    assert result == gruen_seven


def test_follow_last_to_act_does_not_spend_points_on_worthless_trick(
    gruen_seven, gruen_eight, gruen_nine, gruen_ober, schellen_seven, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[gruen_ober, schellen_seven])
    context = _context(
        current_trick=[
            ("opp1", gruen_seven),
            ("opp2", gruen_eight),
            ("opp3", gruen_nine),
        ],
        trumps=sauspiel_trumps,
    )

    result = choose_card_to_play(player, [gruen_ober, schellen_seven], context)

    # Every card on the table is worth 0 points, so there's no must to win
    # it with the Gruen Ober - keep the trump and let the opponent have the
    # worthless trick.
    assert result == schellen_seven


def test_follow_last_to_act_takes_worthless_trick_with_a_zero_point_card(
    gruen_seven, gruen_eight, gruen_nine, schellen_seven, schellen_eight, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[gruen_nine, schellen_eight])
    context = _context(
        current_trick=[
            ("opp1", gruen_seven),
            ("opp2", gruen_eight),
            ("opp3", schellen_seven),
        ],
        trumps=sauspiel_trumps,
    )

    result = choose_card_to_play(player, [gruen_nine, schellen_eight], context)

    # Taking a worthless trick with another worthless card is also fine.
    assert result == gruen_nine


# choose_card_to_play - Ramsch following


def test_follow_ramsch_ducks_when_possible(
    gruen_eight, gruen_ober, gruen_seven, sauspiel_trumps
):
    cpc = RamschCardPowerCalculator()
    player = _FakePlayer(player_cards=[gruen_ober, gruen_seven])
    context = _context(
        current_trick=[("p", gruen_eight)], trumps=sauspiel_trumps, cpc=cpc, is_ramsch=True
    )

    result = choose_card_to_play(player, [gruen_ober, gruen_seven], context)

    assert result == gruen_seven


def test_follow_ramsch_forced_win_minimises_points(
    gruen_eight, gruen_ober, eichel_ober, sauspiel_trumps
):
    cpc = RamschCardPowerCalculator()
    player = _FakePlayer(player_cards=[gruen_ober, eichel_ober])
    context = _context(
        current_trick=[("p", gruen_eight)], trumps=sauspiel_trumps, cpc=cpc, is_ramsch=True
    )

    result = choose_card_to_play(player, [gruen_ober, eichel_ober], context)

    assert result == gruen_ober


# choose_card_to_play - Tout following


def test_follow_tout_must_win_with_cheapest_card(
    gruen_eight, gruen_ober, gruen_seven, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[gruen_ober, gruen_seven])
    context = _context(
        current_trick=[("opponent", gruen_eight)], trumps=sauspiel_trumps, is_tout=True
    )

    result = choose_card_to_play(player, [gruen_ober, gruen_seven], context)

    assert result == gruen_ober


def test_follow_tout_does_not_waste_card_when_teammate_already_secured_trick(
    eichel_seven, schellen_eight, eichel_ober, herz_sau, gruen_seven, sauspiel_trumps
):
    player = _FakePlayer(player_cards=[herz_sau, gruen_seven])
    context = _context(
        current_trick=[
            ("opp1", eichel_seven),
            ("opp2", schellen_eight),
            ("teammate", eichel_ober),
        ],
        trumps=sauspiel_trumps,
        is_tout=True,
        teammates=["teammate"],
    )

    result = choose_card_to_play(player, [herz_sau, gruen_seven], context)

    assert result == gruen_seven


# _players_void_of_trumps


def test_players_void_of_trumps_combines_known_and_trumpfzwang(
    herz_ober, herz_unter, schellen_seven, sauspiel_trumps
):
    # "defender" failed to follow a trump lead (Trumpfzwang), "chooser" is
    # known trumpless from the start (Hochzeit swap); "follower" followed
    # with a trump and proves nothing.
    trick_history = [
        [
            ("leader", herz_ober),
            ("defender", schellen_seven),
            ("follower", herz_unter),
        ]
    ]
    context = _context(
        trumps=sauspiel_trumps,
        trick_history=trick_history,
        known_trumpless=("chooser",),
    )

    assert _players_void_of_trumps(context) == {"chooser", "defender"}


def test_players_void_of_trumps_ignores_non_trump_leads(
    eichel_ten, schellen_seven, sauspiel_trumps
):
    # Not following a non-trump lead proves nothing about trumps.
    trick_history = [[("leader", eichel_ten), ("other", schellen_seven)]]
    context = _context(trumps=sauspiel_trumps, trick_history=trick_history)

    assert _players_void_of_trumps(context) == set()


# Hochzeit: the chooser is publicly trumpless (known_trumpless)


def test_follow_schmiers_when_only_trumpless_chooser_still_to_act(
    eichel_sau, eichel_koenig, schellen_ten, schellen_seven, sauspiel_trumps
):
    # Hochzeit defender: my teammate's Eichel Sau is winning and the only
    # player still to act is the chooser, who everyone knows holds no
    # trumps - the trick cannot be lost, so feed it the Ten.
    player = _FakePlayer(player_cards=[schellen_ten, schellen_seven])
    context = _context(
        current_trick=[("teammate", eichel_sau), ("partner", eichel_koenig)],
        trumps=sauspiel_trumps,
        teammates=["teammate"],
        opponents=["partner", "chooser"],
        known_trumpless=("chooser",),
    )

    result = choose_card_to_play(player, [schellen_ten, schellen_seven], context)

    assert result == schellen_ten


def test_follow_holds_back_when_player_still_to_act_may_hold_trumps(
    eichel_sau, eichel_koenig, schellen_ten, schellen_seven, sauspiel_trumps
):
    # Same trick, but without the trumpless knowledge the chooser could
    # still trump the Sau away - don't feed points.
    player = _FakePlayer(player_cards=[schellen_ten, schellen_seven])
    context = _context(
        current_trick=[("teammate", eichel_sau), ("partner", eichel_koenig)],
        trumps=sauspiel_trumps,
        teammates=["teammate"],
        opponents=["partner", "chooser"],
    )

    result = choose_card_to_play(player, [schellen_ten, schellen_seven], context)

    assert result == schellen_seven


def test_lead_cashes_sure_winner_when_all_threats_trumpless(
    gruen_sau, gruen_seven, schellen_nine, herz_ober, eichel_koenig, sauspiel_trumps
):
    # Hochzeit defender: the chooser is publicly trumpless and the partner
    # was proven void of trumps by Trumpfzwang - nothing can trump the
    # Gruen Sau anymore, so cash it.
    player = _FakePlayer(player_cards=[gruen_sau, gruen_seven, schellen_nine])
    trick_history = [[("teammate", herz_ober), ("partner", eichel_koenig)]]
    context = _context(
        trumps=sauspiel_trumps,
        teammates=["teammate"],
        opponents=["partner", "chooser"],
        known_trumpless=("chooser",),
        trick_history=trick_history,
        tricks_remaining=3,
    )

    result = choose_card_to_play(
        player, [gruen_sau, gruen_seven, schellen_nine], context
    )

    assert result == gruen_sau


def test_lead_keeps_sau_back_when_a_threat_may_still_hold_trumps(
    gruen_sau, gruen_seven, schellen_nine, sauspiel_trumps
):
    # Without proof that both opponents are out of trumps, the late-game
    # Sau lead is too risky - fall back to a low card from the shortest
    # suit.
    player = _FakePlayer(player_cards=[gruen_sau, gruen_seven, schellen_nine])
    context = _context(
        trumps=sauspiel_trumps,
        teammates=["teammate"],
        opponents=["partner", "chooser"],
        known_trumpless=("chooser",),
        tricks_remaining=3,
    )

    result = choose_card_to_play(
        player, [gruen_sau, gruen_seven, schellen_nine], context
    )

    assert result == schellen_nine


def test_lead_claims_trick_with_trump_when_threats_trumpless(
    herz_ober, herz_seven, schellen_nine, gruen_ober, eichel_koenig, sauspiel_trumps
):
    # All threats proven trumpless: every trump is a sure winner, so claim
    # the trick with the most valuable one instead of leading the losing
    # Schellen Nine.
    player = _FakePlayer(player_cards=[herz_ober, herz_seven, schellen_nine])
    trick_history = [[("teammate", gruen_ober), ("partner", eichel_koenig)]]
    context = _context(
        trumps=sauspiel_trumps,
        teammates=["teammate"],
        opponents=["partner", "chooser"],
        known_trumpless=("chooser",),
        trick_history=trick_history,
        tricks_remaining=3,
    )

    result = choose_card_to_play(
        player, [herz_ober, herz_seven, schellen_nine], context
    )

    assert result == herz_ober
