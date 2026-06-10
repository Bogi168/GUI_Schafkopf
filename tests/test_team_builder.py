from game_classes.TeamBuilder import (
    RamschTeamBuilder,
    HochzeitTeamBuilder,
    SauspielTeamBuilder,
    AloneTeamBuilder,
    WenzTeamBuilder,
    SoloTeamBuilder,
)


def test_ramsch_team_builder_creates_four_solo_teams(players):
    team_setup = RamschTeamBuilder(players=players).create_teams()

    assert len(team_setup.teams) == 4
    for player, team in zip(players, team_setup.teams):
        assert team.players == [player]
        assert team_setup.player_teams[player] == team
    assert team_setup.active_team is None


def test_hochzeit_team_builder_pairs_chooser_with_partner(
    players, player_1, player_3
):
    team_setup = HochzeitTeamBuilder(
        players=players, game_chooser=player_1, partner=player_3
    ).create_teams()

    team_1, team_2 = team_setup.teams
    assert team_1.players == [player_1, player_3]
    assert sorted(team_2.players, key=lambda p: p.player_name) == sorted(
        [p for p in players if p not in (player_1, player_3)],
        key=lambda p: p.player_name,
    )
    assert team_setup.active_team == team_1
    assert team_setup.player_teams[player_1] == team_1
    assert team_setup.player_teams[player_3] == team_1
    for p in team_2.players:
        assert team_setup.player_teams[p] == team_2


def test_sauspiel_team_builder_finds_call_sau_owner(
    players, player_1, player_3, eichel_sau
):
    # The call sau is held by player_3, who isn't the game chooser
    player_3.player_cards = [eichel_sau]

    team_setup = SauspielTeamBuilder(
        players=players, game_chooser=player_1, call_sau=eichel_sau
    ).create_teams()

    team_1, team_2 = team_setup.teams
    assert team_1.players == [player_1, player_3]
    assert team_setup.active_team == team_1
    assert sorted(team_2.players, key=lambda p: p.player_name) == sorted(
        [p for p in players if p not in (player_1, player_3)],
        key=lambda p: p.player_name,
    )
    for p in team_1.players:
        assert team_setup.player_teams[p] == team_1
    for p in team_2.players:
        assert team_setup.player_teams[p] == team_2


def test_alone_team_builder_puts_chooser_alone(players, player_2):
    team_setup = AloneTeamBuilder(
        players=players, game_chooser=player_2
    ).create_teams()

    team_1, team_2 = team_setup.teams
    assert team_1.players == [player_2]
    assert team_setup.active_team == team_1
    assert sorted(team_2.players, key=lambda p: p.player_name) == sorted(
        [p for p in players if p != player_2],
        key=lambda p: p.player_name,
    )
    assert team_setup.player_teams[player_2] == team_1
    for p in team_2.players:
        assert team_setup.player_teams[p] == team_2


def test_wenz_and_solo_team_builders_behave_like_alone_team_builder(players, player_4):
    for builder_cls in (WenzTeamBuilder, SoloTeamBuilder):
        team_setup = builder_cls(
            players=players, game_chooser=player_4
        ).create_teams()
        team_1, team_2 = team_setup.teams
        assert team_1.players == [player_4]
        assert team_setup.active_team == team_1
        assert len(team_2.players) == 3
