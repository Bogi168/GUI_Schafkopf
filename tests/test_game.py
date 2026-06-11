from unittest.mock import MagicMock, call

import pytest

from card_classes.Cards import Cards, Type, Color
from card_classes.CardPowerCalculator import SauspielCardPowerCalculator
from game_classes.Game import Game
from game_classes.RoundManager import RoundManager
from game_classes.RunnersCalculator import RunnersSetup
from game_classes.TeamBuilder import TeamSetup
from money_handling.MoneyDistributer import MoneyDistributer
from money_handling.WinnersSelector import WinnersSelector
from system.Renderer import GameResult


class FakeGame(Game):
    """Minimal concrete Game subclass for testing the abstract base class."""

    def create_game_value_calculator(self, winners):
        calc = MagicMock()
        calc.calculate_game_value.return_value = 20
        calc.game_value_breakdown.return_value = "breakdown"
        return calc


class FakeRunnersCalculator:
    """A fake runners_calculator "class" whose instance returns a known RunnersSetup."""

    last_instance = None

    def __init__(self, trumps):
        self.trumps = trumps
        self.count_game_runners = MagicMock(
            return_value=RunnersSetup(runners_amount=3)
        )
        FakeRunnersCalculator.last_instance = self


@pytest.fixture
def team_setup(team_two_players_1, team_two_players_2):
    return TeamSetup(
        player_teams={},
        teams=[team_two_players_1, team_two_players_2],
        active_team=team_two_players_1,
    )


@pytest.fixture
def fake_game(players, team_setup):
    team_builder = MagicMock()
    team_builder.create_teams.return_value = team_setup

    game = FakeGame(
        cards=Cards(),
        renderer=MagicMock(),
        team_builder=team_builder,
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=MagicMock(),
        runners_calculator=FakeRunnersCalculator,
        trump_types=[Type.OBER, Type.UNTER],
        trump_color=Color.HERZ,
        players=players,
        amount_game_value_doubles=0,
    )
    return game


# __init__


def test_init_sets_up_trumps_and_total_card_points(fake_game):
    # All Ober + Unter + Herz cards, deduplicated and sorted descending by power
    assert all(
        card.card_type in (Type.OBER, Type.UNTER) or card.card_color == Color.HERZ
        for card in fake_game.trumps
    )
    powers = [
        fake_game.card_power_calculator.get_card_power(card)
        for card in fake_game.trumps
    ]
    assert powers == sorted(powers, reverse=True)

    expected_total_points = sum(card.card_type.points for card in Cards().full_deck)
    assert fake_game.total_card_points == expected_total_points


def test_init_sets_default_state(fake_game):
    assert fake_game.player_teams == {}
    assert fake_game.teams == []
    assert fake_game.active_team is None
    assert fake_game.runners_amount == 0
    assert fake_game.round_manager is None


# gather_kwargs


def test_gather_kwargs_returns_base_dict():
    schafkopf = MagicMock()
    schafkopf.cards = "cards"
    schafkopf.renderer = "renderer"
    schafkopf.players = "players"
    schafkopf.amount_game_value_doubles = 5

    kwargs = Game.gather_kwargs(chooser=None, schafkopf=schafkopf)

    assert kwargs == dict(
        cards="cards",
        renderer="renderer",
        players="players",
        amount_game_value_doubles=5,
    )


# create_teams


def test_create_teams_sets_player_teams_active_team_and_teams(fake_game, team_setup):
    fake_game.create_teams()

    assert fake_game.player_teams == team_setup.player_teams
    assert fake_game.active_team == team_setup.active_team
    assert fake_game.teams == team_setup.teams
    fake_game.team_builder.create_teams.assert_called_once_with()


# create_round_manager


def test_create_round_manager_returns_round_manager_with_expected_attributes(
    fake_game, team_two_players_1
):
    fake_game.active_team = team_two_players_1
    fake_game.player_teams = {p: team_two_players_1 for p in fake_game.players}

    round_manager = fake_game.create_round_manager()

    assert isinstance(round_manager, RoundManager)
    assert round_manager.players == fake_game.players
    assert round_manager.player_teams == fake_game.player_teams
    assert round_manager.trumps == fake_game.trumps
    assert round_manager.card_power_calculator == fake_game.card_power_calculator
    assert (
        round_manager.card_decision_validator == fake_game.card_decision_validator
    )
    assert round_manager.active_team == fake_game.active_team
    assert round_manager.renderer == fake_game.renderer
    assert round_manager.is_tout == fake_game.is_tout


# create_winners_selector


def test_create_winners_selector_returns_winners_selector_with_teams_and_active_team(
    fake_game, team_setup
):
    fake_game.teams = team_setup.teams
    fake_game.active_team = team_setup.active_team

    winners_selector = fake_game.create_winners_selector()

    assert isinstance(winners_selector, WinnersSelector)
    assert winners_selector.teams == fake_game.teams
    assert winners_selector.active_team == fake_game.active_team


# display_detail / display_detail_color


def test_display_detail_defaults_to_none(fake_game):
    assert fake_game.display_detail() is None


def test_display_detail_color_defaults_to_none(fake_game):
    assert fake_game.display_detail_color() is None


# sort_player_hands


def test_sort_player_hands_sorts_each_players_cards_by_power_descending(
    fake_game, eichel_sau, eichel_seven, herz_ober, schellen_seven
):
    p1, p2, p3, p4 = fake_game.players
    p1.player_cards = [eichel_seven, herz_ober, eichel_sau]
    p2.player_cards = [schellen_seven, eichel_sau]

    fake_game.sort_player_hands()

    powers_p1 = [
        fake_game.card_power_calculator.get_card_power(c) for c in p1.player_cards
    ]
    powers_p2 = [
        fake_game.card_power_calculator.get_card_power(c) for c in p2.player_cards
    ]
    assert powers_p1 == sorted(powers_p1, reverse=True)
    assert powers_p2 == sorted(powers_p2, reverse=True)
    # herz_ober (a trump) should come first for player 1
    assert p1.player_cards[0] == herz_ober


# play_rounds


def test_play_rounds_calls_round_manager_methods_for_each_round(
    fake_game, eichel_sau, eichel_seven
):
    for player in fake_game.players:
        player.player_cards = [eichel_sau, eichel_seven]

    round_manager = MagicMock()
    round_winners = ["winner_1", "winner_2"]
    round_manager.get_round_winner.side_effect = round_winners

    fake_game.play_rounds(round_manager=round_manager)

    assert round_manager.play_round.call_count == 2
    round_manager.play_round.assert_has_calls(
        [call(is_first_round=True), call(is_first_round=False)]
    )

    assert round_manager.get_round_winner.call_count == 2

    assert round_manager.reward_round_winner.call_count == 2
    round_manager.reward_round_winner.assert_has_calls(
        [call(round_winner="winner_1"), call(round_winner="winner_2")]
    )

    assert round_manager.prepare_next_round.call_count == 2
    round_manager.prepare_next_round.assert_has_calls(
        [call(round_winner="winner_1"), call(round_winner="winner_2")]
    )


def test_play_rounds_with_one_card_runs_single_round_as_first_round(
    fake_game, eichel_sau
):
    for player in fake_game.players:
        player.player_cards = [eichel_sau]

    round_manager = MagicMock()
    round_manager.get_round_winner.return_value = "winner"

    fake_game.play_rounds(round_manager=round_manager)

    round_manager.play_round.assert_called_once_with(is_first_round=True)
    round_manager.get_round_winner.assert_called_once()
    round_manager.reward_round_winner.assert_called_once_with(round_winner="winner")
    round_manager.prepare_next_round.assert_called_once_with(round_winner="winner")


# play_rounds with game_chooser (Tout games)


def test_play_rounds_with_game_chooser_behaves_like_play_rounds_when_chooser_always_wins(
    fake_game, eichel_sau, eichel_seven, player_1
):
    for player in fake_game.players:
        player.player_cards = [eichel_sau, eichel_seven]

    round_manager = MagicMock()
    round_manager.get_round_winner.return_value = player_1

    fake_game.play_rounds(round_manager=round_manager, game_chooser=player_1)

    assert round_manager.play_round.call_count == 2
    round_manager.play_round.assert_has_calls(
        [call(is_first_round=True), call(is_first_round=False)]
    )
    assert round_manager.get_round_winner.call_count == 2
    assert round_manager.reward_round_winner.call_count == 2
    assert round_manager.prepare_next_round.call_count == 2


def test_play_rounds_with_game_chooser_breaks_when_chooser_loses_first_round(
    fake_game, eichel_sau, eichel_seven, player_1, player_2
):
    for player in fake_game.players:
        player.player_cards = [eichel_sau, eichel_seven]

    round_manager = MagicMock()
    round_manager.get_round_winner.return_value = player_2

    fake_game.play_rounds(round_manager=round_manager, game_chooser=player_1)

    round_manager.play_round.assert_called_once_with(is_first_round=True)
    round_manager.get_round_winner.assert_called_once()
    round_manager.reward_round_winner.assert_called_once_with(round_winner=player_2)
    round_manager.prepare_next_round.assert_not_called()


# calculate_runners_amount


def test_calculate_runners_amount_sets_runners_amount_from_runners_setup(
    fake_game, team_setup
):
    fake_game.teams = team_setup.teams

    fake_game.calculate_runners_amount()

    assert fake_game.runners_amount == 3
    FakeRunnersCalculator.last_instance.count_game_runners.assert_called_once_with(
        teams=fake_game.teams
    )


# get_most_point_teams_for_result


def test_get_most_point_teams_for_result_delegates_to_winners_selector(fake_game):
    winners_selector = MagicMock()
    winners_selector.get_most_points_teams.return_value = ["team_x"]

    result = fake_game.get_most_point_teams_for_result(
        winners_selector=winners_selector
    )

    assert result == ["team_x"]
    winners_selector.get_most_points_teams.assert_called_once_with()


# handle_winners


def test_handle_winners_renders_game_result_with_expected_fields(
    fake_game, team_two_players_1, team_two_players_2
):
    fake_game.teams = [team_two_players_1, team_two_players_2]
    fake_game.active_team = team_two_players_1
    team_two_players_1.points = 70
    team_two_players_2.points = 50

    fake_game.handle_winners()

    fake_game.renderer.render_game_result.assert_called_once()
    _, kwargs = fake_game.renderer.render_game_result.call_args
    result: GameResult = kwargs["result"]

    assert result.most_point_teams == [team_two_players_1]
    assert result.winners == team_two_players_1.players
    assert result.game_value == 20
    assert result.game_value_breakdown == "breakdown"
    assert result.players == fake_game.players


def test_handle_winners_distributes_money(
    fake_game, team_two_players_1, team_two_players_2, monkeypatch
):
    fake_game.teams = [team_two_players_1, team_two_players_2]
    fake_game.active_team = team_two_players_1
    team_two_players_1.points = 70
    team_two_players_2.points = 50

    distribute_mock = MagicMock()
    monkeypatch.setattr(MoneyDistributer, "distribute_money", distribute_mock)

    fake_game.handle_winners()

    distribute_mock.assert_called_once_with(
        game_value=20,
        winners=team_two_players_1.players,
        players=fake_game.players,
    )


# play_game


def test_play_game_calls_pipeline_steps_in_order(fake_game):
    manager = MagicMock(name="manager")

    fake_game.create_teams = MagicMock(name="create_teams")
    fake_game.sort_player_hands = MagicMock(name="sort_player_hands")
    fake_game.calculate_runners_amount = MagicMock(name="calculate_runners_amount")
    fake_game.create_round_manager = MagicMock(
        name="create_round_manager", return_value=manager
    )
    fake_game.play_rounds = MagicMock(name="play_rounds")
    fake_game.handle_winners = MagicMock(name="handle_winners")

    manager.amt_game_val_doubles = 2
    manager.active_team = "the_active_team"

    fake_game.amount_game_value_doubles = 1

    parent_mock = MagicMock()
    parent_mock.attach_mock(fake_game.create_teams, "create_teams")
    parent_mock.attach_mock(fake_game.sort_player_hands, "sort_player_hands")
    parent_mock.attach_mock(
        fake_game.calculate_runners_amount, "calculate_runners_amount"
    )
    parent_mock.attach_mock(fake_game.create_round_manager, "create_round_manager")
    parent_mock.attach_mock(fake_game.play_rounds, "play_rounds")
    parent_mock.attach_mock(fake_game.handle_winners, "handle_winners")

    fake_game.play_game()

    fake_game.create_teams.assert_called_once_with()
    fake_game.sort_player_hands.assert_called_once_with()
    fake_game.calculate_runners_amount.assert_called_once_with()
    fake_game.create_round_manager.assert_called_once_with()
    fake_game.play_rounds.assert_called_once_with(round_manager=manager)
    fake_game.handle_winners.assert_called_once_with()

    assert parent_mock.mock_calls == [
        call.create_teams(),
        call.sort_player_hands(),
        call.calculate_runners_amount(),
        call.create_round_manager(),
        call.play_rounds(round_manager=manager),
        call.handle_winners(),
    ]

    assert fake_game.round_manager is manager
    assert fake_game.amount_game_value_doubles == 1 + 2
    assert fake_game.active_team == "the_active_team"
