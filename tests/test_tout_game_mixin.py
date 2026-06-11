from unittest.mock import MagicMock

import pytest

from card_classes.Cards import Cards, Type, Color
from card_classes.CardPowerCalculator import SauspielCardPowerCalculator
from game_classes.RunnersCalculator import RunnersSetup
from game_classes.TeamBuilder import TeamSetup
from game_classes.game_modes.ToutGameMixin import ToutGameMixin
from game_classes.game_modes.WenzTout import WenzTout
from game_classes.game_modes.SoloTout import SoloTout
from money_handling.GameValueCalculator import (
    ToutGameValueCalculator,
    WenzToutGameValueCalculator,
    SoloToutGameValueCalculator,
)
from money_handling.WinnersSelector import (
    ToutWinnersSelector,
    WenzToutWinnersSelector,
    SoloToutWinnersSelector,
)


class FakeRunnersCalculator:
    """A fake runners_calculator "class" whose instance returns a known RunnersSetup."""

    def __init__(self, trumps):
        self.trumps = trumps
        self.count_game_runners = MagicMock(
            return_value=RunnersSetup(runners_amount=0)
        )


class FakeToutGame(ToutGameMixin):
    """Minimal concrete ToutGameMixin user for testing the mixin in isolation."""


@pytest.fixture
def tout_game(players, player_1, team_two_players_1, team_two_players_2):
    team_builder = MagicMock()
    team_builder.create_teams.return_value = TeamSetup(
        player_teams={},
        teams=[team_two_players_1, team_two_players_2],
        active_team=team_two_players_1,
    )

    game = FakeToutGame(
        cards=Cards(),
        renderer=MagicMock(),
        team_builder=team_builder,
        card_power_calculator=SauspielCardPowerCalculator(),
        card_decision_validator=MagicMock(),
        runners_calculator=FakeRunnersCalculator,
        trump_types=[Type.UNTER],
        trump_color=None,
        players=players,
        amount_game_value_doubles=0,
    )
    game.game_chooser = player_1
    game.base_price = 10
    game.alone_price = 50
    game.runners_amount = 2
    game.create_teams()
    return game


def test_play_rounds_continues_while_game_chooser_keeps_winning(
    tout_game, player_1, eichel_sau, eichel_seven
):
    for player in tout_game.players:
        player.player_cards = [eichel_sau, eichel_seven]

    round_manager = MagicMock()
    round_manager.get_round_winner.return_value = player_1

    tout_game.play_rounds(round_manager=round_manager)

    assert round_manager.play_round.call_count == 2
    assert round_manager.prepare_next_round.call_count == 2


def test_play_rounds_breaks_when_game_chooser_loses_a_trick(
    tout_game, player_1, player_2, eichel_sau, eichel_seven
):
    for player in tout_game.players:
        player.player_cards = [eichel_sau, eichel_seven]

    round_manager = MagicMock()
    round_manager.get_round_winner.return_value = player_2

    tout_game.play_rounds(round_manager=round_manager)

    round_manager.play_round.assert_called_once_with(is_first_round=True)
    round_manager.prepare_next_round.assert_not_called()


def test_get_most_point_teams_for_result_returns_empty_list(tout_game):
    assert tout_game.get_most_point_teams_for_result(winners_selector=MagicMock()) == []


def test_create_winners_selector_uses_tout_winners_selector_class(
    tout_game, player_1
):
    selector = tout_game.create_winners_selector()

    assert isinstance(selector, ToutWinnersSelector)
    assert selector.teams == tout_game.teams
    assert selector.active_team == tout_game.active_team
    assert selector.game_chooser is player_1
    assert selector.full_deck == tout_game.cards.full_deck


def test_create_game_value_calculator_uses_tout_game_value_calculator_class(
    tout_game, player_1
):
    calculator = tout_game.create_game_value_calculator(winners=[player_1])

    assert isinstance(calculator, ToutGameValueCalculator)
    assert calculator.base_price == tout_game.base_price
    assert calculator.alone_price == tout_game.alone_price
    assert calculator.runners_amount == tout_game.runners_amount


def test_wenz_tout_uses_wenz_specific_tout_classes():
    assert WenzTout.tout_winners_selector_class is WenzToutWinnersSelector
    assert WenzTout.tout_game_value_calculator_class is WenzToutGameValueCalculator


def test_solo_tout_uses_solo_specific_tout_classes():
    assert SoloTout.tout_winners_selector_class is SoloToutWinnersSelector
    assert SoloTout.tout_game_value_calculator_class is SoloToutGameValueCalculator
