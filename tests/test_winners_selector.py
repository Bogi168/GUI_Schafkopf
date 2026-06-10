from money_handling.WinnersSelector import (
    WinnersSelector,
    RamschWinnersSelector,
    ToutWinnersSelector,
    WenzToutWinnersSelector,
    SoloToutWinnersSelector,
)


def test_alone_most_points_teams(
    team_alone_player_1,
    team_three_players_2_3_4,
):
    teams = [team_alone_player_1, team_three_players_2_3_4]
    winners_selector = WinnersSelector(teams=teams, active_team=team_alone_player_1)

    team_three_players_2_3_4.points = 64
    team_alone_player_1.points = 25

    assert sorted(
        winners_selector.get_most_points_teams(), key=lambda x: x.team_name
    ) == sorted([team_three_players_2_3_4], key=lambda x: x.team_name)

    team_three_players_2_3_4.points = 0
    team_alone_player_1.points = 11

    assert sorted(
        winners_selector.get_most_points_teams(), key=lambda x: x.team_name
    ) == sorted([team_alone_player_1], key=lambda x: x.team_name)

    team_three_players_2_3_4.points = 60
    team_alone_player_1.points = 60

    assert sorted(
        winners_selector.get_most_points_teams(), key=lambda x: x.team_name
    ) == sorted(
        [
            team_alone_player_1,
            team_three_players_2_3_4,
        ],
        key=lambda x: x.team_name,
    )


def test_duo_most_points_teams(
    team_two_players_1,
    team_two_players_2,
):
    teams = [team_two_players_1, team_two_players_2]
    winners_selector = WinnersSelector(teams=teams, active_team=team_two_players_1)

    team_two_players_1.points = 53
    team_two_players_2.points = 35

    assert sorted(
        winners_selector.get_most_points_teams(), key=lambda x: x.team_name
    ) == sorted([team_two_players_1], key=lambda x: x.team_name)

    team_two_players_1.points = 0
    team_two_players_2.points = 11

    assert sorted(
        winners_selector.get_most_points_teams(), key=lambda x: x.team_name
    ) == sorted([team_two_players_2], key=lambda x: x.team_name)

    team_two_players_1.points = 60
    team_two_players_2.points = 60

    assert sorted(
        winners_selector.get_most_points_teams(), key=lambda x: x.team_name
    ) == sorted(
        [
            team_two_players_1,
            team_two_players_2,
        ],
        key=lambda x: x.team_name,
    )


def test_alone_get_game_winners(
    team_alone_player_1,
    team_three_players_2_3_4,
):
    teams = [team_alone_player_1, team_three_players_2_3_4]
    winners_selector = WinnersSelector(teams=teams, active_team=team_alone_player_1)

    team_three_players_2_3_4.points = 64
    team_alone_player_1.points = 24

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [player for player in team_three_players_2_3_4.players],
        key=lambda x: x.player_name,
    )

    team_three_players_2_3_4.points = 0
    team_alone_player_1.points = 11

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted([team_alone_player_1.players[0]], key=lambda x: x.player_name)

    team_three_players_2_3_4.points = 60
    team_alone_player_1.points = 60

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [player for player in team_three_players_2_3_4.players],
        key=lambda x: x.player_name,
    )


def test_duo_get_game_winners(
    team_two_players_1,
    team_two_players_2,
):
    teams = [team_two_players_1, team_two_players_2]
    winners_selector = WinnersSelector(teams=teams, active_team=team_two_players_1)

    team_two_players_1.points = 53
    team_two_players_2.points = 35

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [player for player in team_two_players_1.players], key=lambda x: x.player_name
    )

    team_two_players_1.points = 0
    team_two_players_2.points = 11

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [player for player in team_two_players_2.players], key=lambda x: x.player_name
    )

    team_two_players_1.points = 60
    team_two_players_2.points = 60

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [player for player in team_two_players_2.players], key=lambda x: x.player_name
    )


# special rules for Ramsch
def test_ramsch_one_loser(
    team_alone_player_1,
    team_alone_player_2,
    team_alone_player_3,
    team_alone_player_4,
):
    teams = [
        team_alone_player_1,
        team_alone_player_2,
        team_alone_player_3,
        team_alone_player_4,
    ]
    winners_selector = RamschWinnersSelector(
        teams=teams,
        active_players=[team_alone_player_1.players[0], team_alone_player_2.players[0]],
    )

    team_alone_player_1.points = 53
    team_alone_player_3.points = 35

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [
            player
            for team in teams
            for player in team.players
            if team != team_alone_player_1
        ],
        key=lambda x: x.player_name,
    )


def test_ramsch_one_winner(
    team_alone_player_1,
    team_alone_player_2,
    team_alone_player_3,
    team_alone_player_4,
):
    teams = [
        team_alone_player_1,
        team_alone_player_2,
        team_alone_player_3,
        team_alone_player_4,
    ]
    winners_selector = RamschWinnersSelector(
        teams=teams,
        active_players=[team_alone_player_1.players[0], team_alone_player_2.players[0]],
    )

    team_alone_player_1.points = 91
    team_alone_player_2.points = 0
    team_alone_player_3.points = 0
    team_alone_player_4.points = 0

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted([team_alone_player_1.players[0]], key=lambda x: x.player_name)


def test_ramsch_two_most_point_teams(
    team_alone_player_1,
    team_alone_player_2,
    team_alone_player_3,
    team_alone_player_4,
):
    teams = [
        team_alone_player_1,
        team_alone_player_2,
        team_alone_player_3,
        team_alone_player_4,
    ]
    winners_selector = RamschWinnersSelector(
        teams=teams,
        active_players=[team_alone_player_1.players[0], team_alone_player_2.players[0]],
    )

    team_alone_player_1.points = 32
    team_alone_player_2.points = 32
    team_alone_player_3.points = 20
    team_alone_player_4.points = 4

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [
            player
            for team in teams
            for player in team.players
            if team != team_alone_player_1 and team != team_alone_player_2
        ],
        key=lambda x: x.player_name,
    )

    winners_selector = RamschWinnersSelector(
        teams=teams,
        active_players=[team_alone_player_3.players[0], team_alone_player_4.players[0]],
    )

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [
            player
            for team in teams
            for player in team.players
            if team != team_alone_player_1 and team != team_alone_player_2
        ],
        key=lambda x: x.player_name,
    )

    winners_selector = RamschWinnersSelector(
        teams=teams,
        active_players=[team_alone_player_1.players[0], team_alone_player_4.players[0]],
    )

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [
            player
            for team in teams
            for player in team.players
            if team != team_alone_player_1
        ],
        key=lambda x: x.player_name,
    )

    winners_selector = RamschWinnersSelector(
        teams=teams,
        active_players=[],
    )

    team_alone_player_1.points = 32
    team_alone_player_2.points = 32
    team_alone_player_3.points = 32
    team_alone_player_4.points = 0

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [player for player in team_alone_player_4.players],
        key=lambda x: x.player_name,
    )

    winners_selector = RamschWinnersSelector(
        teams=teams,
        active_players=[team_alone_player_1.players[0], team_alone_player_4.players[0]],
    )

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(
        [
            player
            for team in teams
            for player in team.players
            if team != team_alone_player_1
        ],
        key=lambda x: x.player_name,
    )


# Tout family: all-or-nothing - the game chooser only wins by taking every
# trick, otherwise the whole opposing side wins


def test_tout_game_chooser_wins_by_taking_every_trick(
    team_alone_player_1, team_three_players_2_3_4, all_cards
):
    teams = [team_alone_player_1, team_three_players_2_3_4]
    game_chooser = team_alone_player_1.players[0]
    game_chooser.collected_cards = list(all_cards)

    winners_selector = ToutWinnersSelector(
        teams=teams,
        active_team=team_alone_player_1,
        game_chooser=game_chooser,
        full_deck=all_cards,
    )

    assert winners_selector.get_game_winners() == [game_chooser]


def test_tout_opposing_side_wins_if_chooser_misses_a_single_trick(
    team_alone_player_1, team_three_players_2_3_4, all_cards
):
    teams = [team_alone_player_1, team_three_players_2_3_4]
    game_chooser = team_alone_player_1.players[0]
    # missing the very last card -> not a clean sweep
    game_chooser.collected_cards = list(all_cards[:-1])

    winners_selector = ToutWinnersSelector(
        teams=teams,
        active_team=team_alone_player_1,
        game_chooser=game_chooser,
        full_deck=all_cards,
    )

    assert sorted(
        winners_selector.get_game_winners(), key=lambda x: x.player_name
    ) == sorted(team_three_players_2_3_4.players, key=lambda x: x.player_name)


def test_wenz_tout_and_solo_tout_match_tout_winners(
    team_alone_player_1, team_three_players_2_3_4, all_cards
):
    teams = [team_alone_player_1, team_three_players_2_3_4]
    game_chooser = team_alone_player_1.players[0]
    game_chooser.collected_cards = list(all_cards)

    for cls in (
        ToutWinnersSelector,
        WenzToutWinnersSelector,
        SoloToutWinnersSelector,
    ):
        winners_selector = cls(
            teams=teams,
            active_team=team_alone_player_1,
            game_chooser=game_chooser,
            full_deck=all_cards,
        )
        assert winners_selector.get_game_winners() == [game_chooser]
