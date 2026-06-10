from __future__ import annotations
import pytest
from typing import TYPE_CHECKING
from unittest.mock import MagicMock
from money_handling.MoneyDistributer import MoneyDistributer
from player_classes.Player import Player
from system.custom_exceptions import MoneyDistributionNotPossibleError

if TYPE_CHECKING:
    from player_classes.Player import Player

TOTAL_POINTS = 120


@pytest.fixture
def distributer() -> MoneyDistributer:
    return MoneyDistributer()


def test_distribute_money_one_winner(
    team_alone_player_1,
    team_three_players_2_3_4,
    distributer,
):
    player_1 = team_alone_player_1.players[0]
    player_2 = team_three_players_2_3_4.players[0]
    player_3 = team_three_players_2_3_4.players[1]
    player_4 = team_three_players_2_3_4.players[2]
    players: list[Player] = [player_1, player_2, player_3, player_4]
    winners: list[Player] = [player_1]

    game_value: int = 10
    distributer.distribute_money(
        game_value=game_value, winners=winners, players=players
    )

    assert player_1.money == 3 * game_value
    assert player_2.money == -game_value
    assert player_3.money == -game_value
    assert player_4.money == -game_value


def test_distribute_money_two_winners(
    team_two_players_1, team_two_players_2, distributer
):
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    players: list[Player] = [player_1, player_2, player_3, player_4]
    winners: list[Player] = [player_1, player_2]

    game_value: int = 10
    distributer.distribute_money(
        game_value=game_value, winners=winners, players=players
    )

    assert player_1.money == game_value
    assert player_2.money == game_value
    assert player_3.money == -game_value
    assert player_4.money == -game_value


def test_distribute_money_three_winners(
    team_alone_player_1, team_three_players_2_3_4, distributer
):
    player_1: Player = team_alone_player_1.players[0]
    player_2: Player = team_three_players_2_3_4.players[0]
    player_3: Player = team_three_players_2_3_4.players[1]
    player_4: Player = team_three_players_2_3_4.players[2]
    players: list[Player] = [player_1, player_2, player_3, player_4]
    winners: list[Player] = [player_2, player_3, player_4]

    game_value: int = 10
    distributer.distribute_money(
        game_value=game_value, winners=winners, players=players
    )

    assert player_1.money == -3 * game_value
    assert player_2.money == game_value
    assert player_3.money == game_value
    assert player_4.money == game_value


def test_distribute_money_no_winners_is_a_no_op(
    team_alone_player_1, team_three_players_2_3_4, distributer
):
    players: list[Player] = [team_alone_player_1.players[0]] + list(
        team_three_players_2_3_4.players
    )

    distributer.distribute_money(game_value=10, winners=[], players=players)

    for player in players:
        assert player.money == 0


def test_distribute_money_everyone_wins_is_a_no_op(
    team_alone_player_1, team_three_players_2_3_4, distributer
):
    players: list[Player] = [team_alone_player_1.players[0]] + list(
        team_three_players_2_3_4.players
    )

    distributer.distribute_money(game_value=10, winners=players, players=players)

    for player in players:
        assert player.money == 0


def test_distribute_money_uneven_split_raises(distributer):
    players: list[Player] = [
        Player(
            player_name=f"Testplayer {i}",
            renderer=MagicMock(),
            game_decision_validator=MagicMock(),
        )
        for i in range(1, 6)
    ]
    winners: list[Player] = players[:2]

    with pytest.raises(MoneyDistributionNotPossibleError):
        distributer.distribute_money(game_value=10, winners=winners, players=players)
