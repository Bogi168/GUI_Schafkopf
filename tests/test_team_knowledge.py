from player_classes.team_knowledge import TeamKnowledge, infer_team_knowledge


def test_alone_team_has_no_teammates(
    players,
    player_1,
    player_2,
    player_3,
    player_4,
    team_alone_player_1,
    team_alone_player_2,
    team_alone_player_3,
    team_alone_player_4,
):
    player_teams = {
        player_1: team_alone_player_1,
        player_2: team_alone_player_2,
        player_3: team_alone_player_3,
        player_4: team_alone_player_4,
    }

    knowledge = infer_team_knowledge(
        player=player_1,
        players=players,
        player_teams=player_teams,
        game_chooser=None,
        call_sau=None,
        trick_history=[],
    )

    assert knowledge == TeamKnowledge(
        teammates=[], opponents=[player_2, player_3, player_4], unknown=[]
    )


def test_public_teams_outside_sauspiel(
    players,
    player_1,
    player_2,
    player_3,
    player_4,
    team_alone_player_1,
    team_three_players_2_3_4,
):
    player_teams = {
        player_1: team_alone_player_1,
        player_2: team_three_players_2_3_4,
        player_3: team_three_players_2_3_4,
        player_4: team_three_players_2_3_4,
    }

    knowledge = infer_team_knowledge(
        player=player_2,
        players=players,
        player_teams=player_teams,
        game_chooser=None,
        call_sau=None,
        trick_history=[],
    )

    assert knowledge == TeamKnowledge(
        teammates=[player_3, player_4], opponents=[player_1], unknown=[]
    )


def test_callsau_holder_knows_teammate_from_start(
    players,
    player_1,
    player_2,
    player_3,
    player_4,
    team_two_players_1,
    team_two_players_2,
    eichel_sau,
    herz_ten,
):
    player_teams = {
        player_1: team_two_players_1,
        player_2: team_two_players_1,
        player_3: team_two_players_2,
        player_4: team_two_players_2,
    }
    player_2.player_cards = [eichel_sau, herz_ten]

    knowledge = infer_team_knowledge(
        player=player_2,
        players=players,
        player_teams=player_teams,
        game_chooser=player_1,
        call_sau=eichel_sau,
        trick_history=[],
    )

    assert knowledge == TeamKnowledge(
        teammates=[player_1], opponents=[player_3, player_4], unknown=[]
    )


def test_chooser_does_not_know_teammate_before_callsau_revealed(
    players,
    player_1,
    player_2,
    player_3,
    player_4,
    team_two_players_1,
    team_two_players_2,
    eichel_sau,
    herz_ten,
):
    player_teams = {
        player_1: team_two_players_1,
        player_2: team_two_players_1,
        player_3: team_two_players_2,
        player_4: team_two_players_2,
    }
    player_1.player_cards = [herz_ten]
    player_2.player_cards = [eichel_sau]

    knowledge = infer_team_knowledge(
        player=player_1,
        players=players,
        player_teams=player_teams,
        game_chooser=player_1,
        call_sau=eichel_sau,
        trick_history=[],
    )

    assert knowledge == TeamKnowledge(
        teammates=[], opponents=[], unknown=[player_2, player_3, player_4]
    )


def test_chooser_learns_teammate_once_callsau_played(
    players,
    player_1,
    player_2,
    player_3,
    player_4,
    team_two_players_1,
    team_two_players_2,
    eichel_sau,
    herz_ten,
    gruen_sau,
):
    player_teams = {
        player_1: team_two_players_1,
        player_2: team_two_players_1,
        player_3: team_two_players_2,
        player_4: team_two_players_2,
    }
    player_1.player_cards = [herz_ten]
    player_2.player_cards = []
    trick_history = [[(player_3, gruen_sau), (player_2, eichel_sau), (player_4, herz_ten)]]

    knowledge = infer_team_knowledge(
        player=player_1,
        players=players,
        player_teams=player_teams,
        game_chooser=player_1,
        call_sau=eichel_sau,
        trick_history=trick_history,
    )

    assert knowledge == TeamKnowledge(
        teammates=[player_2], opponents=[player_3, player_4], unknown=[]
    )


def test_team_two_player_only_knows_chooser_is_an_opponent_before_reveal(
    players,
    player_1,
    player_2,
    player_3,
    player_4,
    team_two_players_1,
    team_two_players_2,
    eichel_sau,
    herz_ten,
):
    player_teams = {
        player_1: team_two_players_1,
        player_2: team_two_players_1,
        player_3: team_two_players_2,
        player_4: team_two_players_2,
    }
    player_2.player_cards = [eichel_sau]
    player_3.player_cards = [herz_ten]

    knowledge = infer_team_knowledge(
        player=player_3,
        players=players,
        player_teams=player_teams,
        game_chooser=player_1,
        call_sau=eichel_sau,
        trick_history=[],
    )

    assert knowledge == TeamKnowledge(
        teammates=[], opponents=[player_1], unknown=[player_2, player_4]
    )


def test_team_two_player_learns_true_teams_once_callsau_played(
    players,
    player_1,
    player_2,
    player_3,
    player_4,
    team_two_players_1,
    team_two_players_2,
    eichel_sau,
    herz_ten,
    gruen_sau,
):
    player_teams = {
        player_1: team_two_players_1,
        player_2: team_two_players_1,
        player_3: team_two_players_2,
        player_4: team_two_players_2,
    }
    player_2.player_cards = []
    player_3.player_cards = [herz_ten]
    trick_history = [[(player_3, gruen_sau), (player_2, eichel_sau), (player_4, herz_ten)]]

    knowledge = infer_team_knowledge(
        player=player_3,
        players=players,
        player_teams=player_teams,
        game_chooser=player_1,
        call_sau=eichel_sau,
        trick_history=trick_history,
    )

    assert knowledge == TeamKnowledge(
        teammates=[player_4], opponents=[player_1, player_2], unknown=[]
    )
