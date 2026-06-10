from game_classes.RunnersCalculator import (
    RunnersCalculator,
    RamschRunnersCalculator,
    WenzRunnersCalculator,
)


# count_team_runners


def test_count_team_runners_three_in_a_row(
    sauspiel_trumps,
    team_two_players_1,
    eichel_ober,
    gruen_ober,
    herz_ober,
):
    player_1, player_2 = team_two_players_1.players
    player_1.player_cards = [eichel_ober, herz_ober]
    player_2.player_cards = [gruen_ober]

    calculator = RunnersCalculator(trumps=sauspiel_trumps)
    assert calculator.count_team_runners(team=team_two_players_1) == 3


def test_count_team_runners_stops_at_gap(
    sauspiel_trumps,
    team_two_players_1,
    team_two_players_2,
    eichel_ober,
    gruen_ober,
    schellen_ober,
):
    # Team 1 has Eichel + Grün Ober (the top two), but Herz Ober (3rd
    # strongest) belongs to Team 2 -> the run stops there
    player_1, player_2 = team_two_players_1.players
    player_3, player_4 = team_two_players_2.players
    player_1.player_cards = [eichel_ober]
    player_2.player_cards = [gruen_ober]
    player_3.player_cards = [schellen_ober]

    calculator = RunnersCalculator(trumps=sauspiel_trumps)
    assert calculator.count_team_runners(team=team_two_players_1) == 2


def test_count_team_runners_zero_without_top_trump(
    sauspiel_trumps,
    team_two_players_1,
    team_two_players_2,
    eichel_ober,
    gruen_ober,
):
    # Team 1 doesn't hold the highest trump (Eichel Ober) -> 0 runners
    player_1, player_2 = team_two_players_1.players
    player_3, player_4 = team_two_players_2.players
    player_1.player_cards = [gruen_ober]
    player_3.player_cards = [eichel_ober]

    calculator = RunnersCalculator(trumps=sauspiel_trumps)
    assert calculator.count_team_runners(team=team_two_players_1) == 0


def test_count_team_runners_all_trumps(
    sauspiel_trumps,
    team_two_players_1,
):
    player_1, player_2 = team_two_players_1.players
    player_1.player_cards = sauspiel_trumps[:7]
    player_2.player_cards = sauspiel_trumps[7:]

    calculator = RunnersCalculator(trumps=sauspiel_trumps)
    assert calculator.count_team_runners(team=team_two_players_1) == len(
        sauspiel_trumps
    )


# count_game_runners


def test_count_game_runners_meets_default_minimum(
    sauspiel_trumps,
    team_two_players_1,
    team_two_players_2,
    eichel_ober,
    gruen_ober,
    herz_ober,
):
    player_1, player_2 = team_two_players_1.players
    player_1.player_cards = [eichel_ober, gruen_ober, herz_ober]

    calculator = RunnersCalculator(trumps=sauspiel_trumps)
    runners_setup = calculator.count_game_runners(
        teams=[team_two_players_1, team_two_players_2]
    )
    assert runners_setup.runners_amount == 3


def test_count_game_runners_below_default_minimum(
    sauspiel_trumps,
    team_two_players_1,
    team_two_players_2,
    eichel_ober,
    gruen_ober,
    schellen_ober,
):
    # Team 1 only has 2 in a row (below the default minimum of 3)
    # -> no runners bonus at all, even though Team 1 has more than Team 2
    player_1, player_2 = team_two_players_1.players
    player_3, player_4 = team_two_players_2.players
    player_1.player_cards = [eichel_ober, gruen_ober]
    player_3.player_cards = [schellen_ober]

    calculator = RunnersCalculator(trumps=sauspiel_trumps)
    runners_setup = calculator.count_game_runners(
        teams=[team_two_players_1, team_two_players_2]
    )
    assert runners_setup.runners_amount == 0


# special rule for Wenz: minimum of 2 runners (instead of 3)


def test_wenz_runners_minimum_is_two(
    wenz_trumps,
    team_alone_player_1,
    team_three_players_2_3_4,
    eichel_unter,
    gruen_unter,
):
    player_1 = team_alone_player_1.players[0]
    player_1.player_cards = [eichel_unter, gruen_unter]

    calculator = WenzRunnersCalculator(trumps=wenz_trumps)
    runners_setup = calculator.count_game_runners(
        teams=[team_alone_player_1, team_three_players_2_3_4]
    )
    assert runners_setup.runners_amount == 2


def test_wenz_runners_below_minimum(
    wenz_trumps,
    team_alone_player_1,
    team_three_players_2_3_4,
    eichel_unter,
    gruen_unter,
):
    # Only 1 runner (below Wenz's minimum of 2) -> no runners bonus
    player_1 = team_alone_player_1.players[0]
    player_2 = team_three_players_2_3_4.players[0]
    player_1.player_cards = [eichel_unter]
    player_2.player_cards = [gruen_unter]

    calculator = WenzRunnersCalculator(trumps=wenz_trumps)
    runners_setup = calculator.count_game_runners(
        teams=[team_alone_player_1, team_three_players_2_3_4]
    )
    assert runners_setup.runners_amount == 0


# special rule for Ramsch: minimum of 0 runners -> count_game_runners
# always reports the first team's count (Ramsch's GameValueCalculator
# never uses this value, so it has no effect on the payout)


def test_ramsch_runners_minimum_is_zero(
    sauspiel_trumps,
    team_alone_player_1,
    team_alone_player_2,
    team_alone_player_3,
    team_alone_player_4,
    eichel_ober,
):
    player_2 = team_alone_player_2.players[0]
    player_2.player_cards = [eichel_ober]

    calculator = RamschRunnersCalculator(trumps=sauspiel_trumps)
    runners_setup = calculator.count_game_runners(
        teams=[
            team_alone_player_1,
            team_alone_player_2,
            team_alone_player_3,
            team_alone_player_4,
        ]
    )
    assert runners_setup.runners_amount == 0
