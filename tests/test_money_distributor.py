from __future__ import annotations
import pytest
from typing import TYPE_CHECKING
from money_handling.MoneyDistributer import MoneyDistributer

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
