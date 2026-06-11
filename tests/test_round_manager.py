from unittest.mock import MagicMock

from game_classes.RoundManager import RoundManager, RamschRoundManager
from game_classes.TeamBuilder import RamschTeamBuilder
from card_classes.CardPowerCalculator import (
    SauspielCardPowerCalculator,
    RamschCardPowerCalculator,
)
from input_validators.CardDecisionValidator import (
    RegularTrumpTypeCardDecisionValidator,
    RamschCardDecisionValidator,
)
from player_classes.team_knowledge import TeamKnowledge


# lead_card


def test_lead_card_is_none_before_any_card_played(sauspiel_trumps):
    round_manager = RoundManager(
        players=[],
        player_teams={},
        trumps=sauspiel_trumps,
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=None,
        renderer=MagicMock(),
    )
    assert round_manager.lead_card is None


def test_lead_card_is_first_played_card(sauspiel_trumps, eichel_ten, eichel_sau):
    round_manager = RoundManager(
        players=[],
        player_teams={},
        trumps=sauspiel_trumps,
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=None,
        renderer=MagicMock(),
    )
    round_manager.played_cards = [eichel_ten, eichel_sau]
    assert round_manager.lead_card == eichel_ten


# handle_shooting (Klopfen)


def test_handle_shooting_active_team_is_a_no_op(team_two_players_1):
    round_manager = RoundManager(
        players=[],
        player_teams={},
        trumps=[],
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=team_two_players_1,
        renderer=MagicMock(),
    )
    player = team_two_players_1.players[0]
    player.ask_shoot = MagicMock()

    shooting_possible = round_manager.handle_shooting(
        players_team=team_two_players_1, player=player
    )

    assert shooting_possible is True
    assert round_manager.amt_game_val_doubles == 0
    player.ask_shoot.assert_not_called()


def test_handle_shooting_decline_keeps_shooting_possible(
    team_two_players_1, team_two_players_2
):
    round_manager = RoundManager(
        players=[],
        player_teams={},
        trumps=[],
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=team_two_players_1,
        renderer=MagicMock(),
    )
    player = team_two_players_2.players[0]
    player.ask_shoot = MagicMock(return_value=False)

    shooting_possible = round_manager.handle_shooting(
        players_team=team_two_players_2, player=player
    )

    assert shooting_possible is True
    assert round_manager.amt_game_val_doubles == 0
    assert round_manager.active_team == team_two_players_1


def test_handle_shooting_shot_without_shoot_back_flips_active_team(
    team_two_players_1, team_two_players_2
):
    round_manager = RoundManager(
        players=[],
        player_teams={},
        trumps=[],
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=team_two_players_1,
        renderer=MagicMock(),
    )
    shooter = team_two_players_2.players[0]
    shooter.ask_shoot = MagicMock(return_value=True)
    for prev_active_player in team_two_players_1.players:
        prev_active_player.ask_shoot = MagicMock(return_value=False)

    shooting_possible = round_manager.handle_shooting(
        players_team=team_two_players_2, player=shooter
    )

    assert shooting_possible is False
    assert round_manager.amt_game_val_doubles == 1
    assert round_manager.active_team == team_two_players_2
    for prev_active_player in team_two_players_1.players:
        prev_active_player.ask_shoot.assert_called_once_with(
            ask_shoot_back=True, trumps=[], is_tout=False, is_ramsch=False
        )


def test_handle_shooting_shoot_back_keeps_active_team_and_doubles_again(
    team_two_players_1, team_two_players_2
):
    round_manager = RoundManager(
        players=[],
        player_teams={},
        trumps=[],
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=team_two_players_1,
        renderer=MagicMock(),
    )
    shooter = team_two_players_2.players[0]
    shooter.ask_shoot = MagicMock(return_value=True)
    shoot_back_player, other_active_player = team_two_players_1.players
    shoot_back_player.ask_shoot = MagicMock(return_value=True)
    other_active_player.ask_shoot = MagicMock(return_value=True)

    shooting_possible = round_manager.handle_shooting(
        players_team=team_two_players_2, player=shooter
    )

    assert shooting_possible is False
    assert round_manager.amt_game_val_doubles == 2
    assert round_manager.active_team == team_two_players_1
    # only the first active-team player who shoots back is asked
    shoot_back_player.ask_shoot.assert_called_once_with(
        ask_shoot_back=True, trumps=[], is_tout=False, is_ramsch=False
    )
    other_active_player.ask_shoot.assert_not_called()


# play_card


def test_play_card_appends_decision_and_renders_it(player_1, eichel_sau, eichel_ten):
    player_1.player_cards = [eichel_ten, eichel_sau]
    player_1.get_card_play_decision = MagicMock(return_value=eichel_ten)
    renderer = MagicMock()

    round_manager = RoundManager(
        players=[player_1],
        player_teams={},
        trumps=[],
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=None,
        renderer=renderer,
    )

    round_manager.play_card(player=player_1)

    assert round_manager.played_cards == [eichel_ten]
    renderer.render_played_card.assert_called_once_with(player=player_1, card=eichel_ten)
    # human players don't get a CardPlayContext - they use the renderer
    assert player_1.get_card_play_decision.call_args.kwargs["context"] is None


def test_play_card_passes_context_for_bot_players(
    player_1, team_alone_player_1, eichel_sau, eichel_ten, sauspiel_trumps
):
    bot = MagicMock()
    bot.is_bot = True
    bot.player_cards = [eichel_ten, eichel_sau]
    bot.get_card_play_decision = MagicMock(return_value=eichel_ten)
    renderer = MagicMock()

    round_manager = RoundManager(
        players=[bot],
        player_teams={bot: team_alone_player_1},
        trumps=sauspiel_trumps,
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=None,
        renderer=renderer,
    )

    round_manager.play_card(player=bot)

    context = bot.get_card_play_decision.call_args.kwargs["context"]
    assert context is not None
    assert context.trumps == sauspiel_trumps
    assert context.tricks_remaining == len(bot.player_cards)
    assert context.team_knowledge == TeamKnowledge(teammates=[], opponents=[], unknown=[])
    assert context.is_active_team is False
    assert context.call_sau is None


def test_play_card_context_marks_active_team(
    team_alone_player_1, eichel_sau, eichel_ten, sauspiel_trumps
):
    bot = MagicMock()
    bot.is_bot = True
    bot.player_cards = [eichel_ten, eichel_sau]
    bot.get_card_play_decision = MagicMock(return_value=eichel_ten)

    round_manager = RoundManager(
        players=[bot],
        player_teams={bot: team_alone_player_1},
        trumps=sauspiel_trumps,
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=team_alone_player_1,
        renderer=MagicMock(),
    )

    round_manager.play_card(player=bot)

    context = bot.get_card_play_decision.call_args.kwargs["context"]
    assert context.is_active_team is True


def test_play_card_context_includes_call_sau(
    team_alone_player_1, eichel_sau, eichel_ten, sauspiel_trumps
):
    bot = MagicMock()
    bot.is_bot = True
    bot.player_cards = [eichel_ten, eichel_sau]
    bot.get_card_play_decision = MagicMock(return_value=eichel_ten)

    round_manager = RoundManager(
        players=[bot],
        player_teams={bot: team_alone_player_1},
        trumps=sauspiel_trumps,
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=team_alone_player_1,
        renderer=MagicMock(),
    )
    round_manager.call_sau = eichel_sau

    round_manager.play_card(player=bot)

    context = bot.get_card_play_decision.call_args.kwargs["context"]
    assert context.call_sau == eichel_sau


def test_play_card_context_includes_known_trumpless(
    team_alone_player_1, eichel_sau, eichel_ten, sauspiel_trumps
):
    bot = MagicMock()
    bot.is_bot = True
    bot.player_cards = [eichel_ten, eichel_sau]
    bot.get_card_play_decision = MagicMock(return_value=eichel_ten)

    round_manager = RoundManager(
        players=[bot],
        player_teams={bot: team_alone_player_1},
        trumps=sauspiel_trumps,
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=team_alone_player_1,
        renderer=MagicMock(),
    )
    round_manager.known_trumpless = ["chooser"]

    round_manager.play_card(player=bot)

    context = bot.get_card_play_decision.call_args.kwargs["context"]
    assert context.known_trumpless == ["chooser"]


def test_play_card_context_marks_solo_mode_for_one_vs_three_teams(
    team_alone_player_1, team_three_players_2_3_4, eichel_sau, eichel_ten, sauspiel_trumps
):
    bot = MagicMock()
    bot.is_bot = True
    bot.player_cards = [eichel_ten, eichel_sau]
    bot.get_card_play_decision = MagicMock(return_value=eichel_ten)

    round_manager = RoundManager(
        players=[bot],
        player_teams={bot: team_alone_player_1, "other": team_three_players_2_3_4},
        trumps=sauspiel_trumps,
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=team_alone_player_1,
        renderer=MagicMock(),
    )

    round_manager.play_card(player=bot)

    context = bot.get_card_play_decision.call_args.kwargs["context"]
    assert context.is_solo_mode is True


def test_play_card_context_does_not_mark_solo_mode_for_two_vs_two_teams(
    team_two_players_1, team_two_players_2, eichel_sau, eichel_ten, sauspiel_trumps
):
    bot = MagicMock()
    bot.is_bot = True
    bot.player_cards = [eichel_ten, eichel_sau]
    bot.get_card_play_decision = MagicMock(return_value=eichel_ten)

    round_manager = RoundManager(
        players=[bot],
        player_teams={bot: team_two_players_1, "other": team_two_players_2},
        trumps=sauspiel_trumps,
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=team_two_players_1,
        renderer=MagicMock(),
    )

    round_manager.play_card(player=bot)

    context = bot.get_card_play_decision.call_args.kwargs["context"]
    assert context.is_solo_mode is False


# get_round_winner / reward_round_winner


def test_get_round_winner_picks_strongest_card(
    sauspiel_trumps, players, eichel_sau, eichel_ten, eichel_koenig, eichel_seven
):
    round_manager = RoundManager(
        players=players,
        player_teams={},
        trumps=sauspiel_trumps,
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=None,
        renderer=MagicMock(),
    )
    round_manager.played_cards = [eichel_ten, eichel_koenig, eichel_sau, eichel_seven]

    assert round_manager.get_round_winner() == players[2]


def test_reward_round_winner_collects_cards_and_renders(
    player_1, eichel_sau, eichel_ten
):
    renderer = MagicMock()
    round_manager = RoundManager(
        players=[player_1],
        player_teams={},
        trumps=[],
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=None,
        renderer=renderer,
    )
    round_manager.played_cards = [eichel_sau, eichel_ten]

    round_manager.reward_round_winner(round_winner=player_1)

    assert player_1.collected_cards == [eichel_sau, eichel_ten]
    renderer.render_trick_winner.assert_called_once_with(winner=player_1)


# sort_players / prepare_next_round


def test_sort_players_rotates_to_starter(players, player_3):
    round_manager = RoundManager(
        players=players.copy(),
        player_teams={},
        trumps=[],
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=None,
        renderer=MagicMock(),
    )

    round_manager.sort_players(starter=player_3)

    assert round_manager.players == [players[2], players[3], players[0], players[1]]


def test_prepare_next_round_sorts_players_and_clears_played_cards(
    players, player_2, eichel_sau
):
    round_manager = RoundManager(
        players=players.copy(),
        player_teams={},
        trumps=[],
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=None,
        renderer=MagicMock(),
    )
    round_manager.played_cards = [eichel_sau]

    round_manager.prepare_next_round(round_winner=player_2)

    assert round_manager.players[0] == player_2
    assert round_manager.played_cards == []


# current_trick / trick_history


def test_current_trick_pairs_players_with_played_cards(players, eichel_sau, eichel_ten):
    round_manager = RoundManager(
        players=players,
        player_teams={},
        trumps=[],
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=None,
        renderer=MagicMock(),
    )
    round_manager.played_cards = [eichel_sau, eichel_ten]

    assert round_manager.current_trick == [
        (players[0], eichel_sau),
        (players[1], eichel_ten),
    ]


def test_prepare_next_round_appends_current_trick_to_history(
    players, player_2, eichel_sau, eichel_ten
):
    round_manager = RoundManager(
        players=players.copy(),
        player_teams={},
        trumps=[],
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=None,
        renderer=MagicMock(),
    )
    round_manager.played_cards = [eichel_sau, eichel_ten]
    expected_trick = round_manager.current_trick

    round_manager.prepare_next_round(round_winner=player_2)

    assert round_manager.trick_history == [expected_trick]


# play_round - shooting is only possible in the first round, and only once


def _set_up_round(
    sauspiel_trumps,
    team_two_players_1,
    team_two_players_2,
    cards,
):
    players = team_two_players_1.players + team_two_players_2.players
    for player, card in zip(players, cards):
        player.get_card_play_decision = MagicMock(return_value=card)
    player_teams = {
        player: team_two_players_1 for player in team_two_players_1.players
    }
    player_teams.update(
        {player: team_two_players_2 for player in team_two_players_2.players}
    )
    return RoundManager(
        players=players,
        player_teams=player_teams,
        trumps=sauspiel_trumps,
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=RegularTrumpTypeCardDecisionValidator(),
        active_team=team_two_players_1,
        renderer=MagicMock(),
    )


def test_play_round_first_round_no_shots_keeps_active_team(
    sauspiel_trumps,
    team_two_players_1,
    team_two_players_2,
    eichel_sau,
    eichel_ten,
    eichel_koenig,
    eichel_nine,
):
    round_manager = _set_up_round(
        sauspiel_trumps,
        team_two_players_1,
        team_two_players_2,
        [eichel_sau, eichel_ten, eichel_koenig, eichel_nine],
    )
    for player in round_manager.players:
        player.ask_shoot = MagicMock(return_value=False)

    round_manager.play_round(is_first_round=True)

    # the active team is never asked - handle_shooting is a no-op for them
    for player in team_two_players_1.players:
        player.ask_shoot.assert_not_called()
    # everyone else is asked once, since nobody shoots
    for player in team_two_players_2.players:
        player.ask_shoot.assert_called_once_with(
            trumps=sauspiel_trumps, is_tout=False, is_ramsch=False
        )
    assert round_manager.amt_game_val_doubles == 0
    assert round_manager.active_team == team_two_players_1
    assert round_manager.played_cards == [
        eichel_sau,
        eichel_ten,
        eichel_koenig,
        eichel_nine,
    ]


def test_play_round_not_first_round_never_asks_to_shoot(
    sauspiel_trumps,
    team_two_players_1,
    team_two_players_2,
    eichel_sau,
    eichel_ten,
    eichel_koenig,
    eichel_nine,
):
    round_manager = _set_up_round(
        sauspiel_trumps,
        team_two_players_1,
        team_two_players_2,
        [eichel_sau, eichel_ten, eichel_koenig, eichel_nine],
    )
    for player in round_manager.players:
        player.ask_shoot = MagicMock(return_value=True)

    round_manager.play_round(is_first_round=False)

    for player in round_manager.players:
        player.ask_shoot.assert_not_called()
    assert round_manager.amt_game_val_doubles == 0


def test_play_round_shooting_stops_after_first_shot(
    sauspiel_trumps,
    team_two_players_1,
    team_two_players_2,
    eichel_sau,
    eichel_ten,
    eichel_koenig,
    eichel_nine,
):
    round_manager = _set_up_round(
        sauspiel_trumps,
        team_two_players_1,
        team_two_players_2,
        [eichel_sau, eichel_ten, eichel_koenig, eichel_nine],
    )
    active_1, active_2 = team_two_players_1.players
    shooter, last_player = team_two_players_2.players
    active_1.ask_shoot = MagicMock(return_value=False)
    active_2.ask_shoot = MagicMock(return_value=False)
    shooter.ask_shoot = MagicMock(return_value=True)
    last_player.ask_shoot = MagicMock(return_value=False)

    round_manager.play_round(is_first_round=True)

    # active team players are only consulted for the shoot-back
    active_1.ask_shoot.assert_called_once_with(
        ask_shoot_back=True, trumps=sauspiel_trumps, is_tout=False, is_ramsch=False
    )
    active_2.ask_shoot.assert_called_once_with(
        ask_shoot_back=True, trumps=sauspiel_trumps, is_tout=False, is_ramsch=False
    )
    shooter.ask_shoot.assert_called_once_with(
        trumps=sauspiel_trumps, is_tout=False, is_ramsch=False
    )
    # shooting is settled after the first shot -> last_player is never asked
    last_player.ask_shoot.assert_not_called()

    assert round_manager.active_team == team_two_players_2
    assert round_manager.amt_game_val_doubles == 1
    assert round_manager.played_cards == [
        eichel_sau,
        eichel_ten,
        eichel_koenig,
        eichel_nine,
    ]


# Ramsch: shooting stays possible for every player and there is no active team


def test_ramsch_handle_shooting_tracks_active_players(player_1, player_2):
    round_manager = RamschRoundManager(
        players=[player_1, player_2],
        player_teams={},
        trumps=[],
        card_power_calculator=RamschCardPowerCalculator(),
        card_decision_validator=RamschCardDecisionValidator(),
        renderer=MagicMock(),
    )
    player_1.ask_shoot = MagicMock(return_value=True)
    player_2.ask_shoot = MagicMock(return_value=False)

    assert (
        round_manager.handle_shooting(players_team=MagicMock(), player=player_1)
        is True
    )
    assert (
        round_manager.handle_shooting(players_team=MagicMock(), player=player_2)
        is True
    )

    assert round_manager.active_players == [player_1]
    assert round_manager.amt_game_val_doubles == 1
    assert round_manager.active_team is None


def test_ramsch_play_round_asks_every_player_to_shoot(
    sauspiel_trumps,
    players,
    eichel_sau,
    eichel_ten,
    eichel_koenig,
    eichel_nine,
):
    cards = [eichel_sau, eichel_ten, eichel_koenig, eichel_nine]
    for player, card in zip(players, cards):
        player.get_card_play_decision = MagicMock(return_value=card)
        player.ask_shoot = MagicMock(return_value=True)

    player_teams = RamschTeamBuilder(players=players).create_teams().player_teams

    round_manager = RamschRoundManager(
        players=players,
        player_teams=player_teams,
        trumps=sauspiel_trumps,
        card_power_calculator=RamschCardPowerCalculator(),
        card_decision_validator=RamschCardDecisionValidator(),
        renderer=MagicMock(),
    )

    round_manager.play_round(is_first_round=True)

    for player in players:
        player.ask_shoot.assert_called_once_with(is_ramsch=True)
    assert round_manager.active_players == players
    assert round_manager.amt_game_val_doubles == 4
