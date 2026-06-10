from __future__ import annotations
from typing import TYPE_CHECKING
from unittest.mock import MagicMock
from money_handling.GameValueCalculator import (
    GameValueCalculator,
    RamschGameValueCalculator,
    SauspielGameValueCalculator,
    WenzGameValueCalculator,
    SoloGameValueCalculator,
    HochzeitGameValueCalculator,
    ToutGameValueCalculator,
    WenzToutGameValueCalculator,
    SoloToutGameValueCalculator,
)

if TYPE_CHECKING:
    from player_classes.Player import Player
    from player_classes.Team import Team

TOTAL_POINTS = 120


def make_calculator(
    cls: type[GameValueCalculator],
    player_teams: dict[Player, Team],
    winners: list[Player],
    active_team: Team | None = None,
    amount_game_value_doubles: int = 0,
    runners_amount: int = 0,
    base_price: int = 10,
    call_price: int = 20,
    alone_price: int = 50,
    amount_game_card_points: int = TOTAL_POINTS,
) -> GameValueCalculator:
    kwargs = dict(
        player_teams=player_teams,
        winners=winners,
        amount_game_value_doubles=amount_game_value_doubles,
        amount_game_card_points=amount_game_card_points,
    )
    if cls is RamschGameValueCalculator:
        kwargs["alone_price"] = alone_price
    elif cls is SauspielGameValueCalculator:
        kwargs.update(
            base_price=base_price,
            call_price=call_price,
            active_team=active_team,  # type: ignore
            runners_amount=runners_amount,
        )
    else:  # Wenz / Solo
        kwargs.update(
            base_price=base_price,
            alone_price=alone_price,
            active_team=active_team,  # type: ignore
            runners_amount=runners_amount,
        )
    return cls(**kwargs)


# basic game value adds


def test_basic_game_value_adds_no_extras(
    team_two_players_1,
    team_two_players_2,
):
    # No runners, no schneider, no black, no doubles → value unchanged
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    player_teams: dict[Player, Team] = {
        player_1: team_two_players_1,
        player_2: team_two_players_1,
        player_3: team_two_players_2,
        player_4: team_two_players_2,
    }

    team_two_players_1.points = 61
    team_two_players_2.points = 59
    calculator: GameValueCalculator = make_calculator(
        SauspielGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1, player_2],
        active_team=team_two_players_1,
    )
    assert calculator.basic_game_value_adds(game_value=20) == 20


def test_basic_game_value_adds_runners(
    team_two_players_1,
    team_two_players_2,
):
    # 3 runners with base_price=10 add 30
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    player_teams: dict[Player, Team] = {
        player_1: team_two_players_1,
        player_2: team_two_players_1,
        player_3: team_two_players_2,
        player_4: team_two_players_2,
    }

    team_two_players_1.points = 61
    team_two_players_2.points = 59
    calculator: GameValueCalculator = make_calculator(
        SoloGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1, player_2],
        active_team=team_two_players_1,
        runners_amount=3,
    )
    assert calculator.basic_game_value_adds(game_value=20) == 50


def test_basic_game_value_adds_schneider(
    team_two_players_1,
    team_two_players_2,
):
    # Winning team above schneider threshold (>90) -> adds base_price
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    player_teams: dict[Player, Team] = {
        player_1: team_two_players_1,
        player_2: team_two_players_1,
        player_3: team_two_players_2,
        player_4: team_two_players_2,
    }

    team_two_players_1.points = 91
    team_two_players_2.points = 29
    calculator: GameValueCalculator = make_calculator(
        SauspielGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1, player_2],
        active_team=team_two_players_1,
    )
    assert calculator.basic_game_value_adds(game_value=20) == 30


def test_basic_game_value_adds_schneider_threshold_active_team_loses(
    team_two_players_1,
    team_two_players_2,
):
    # Winning team == schneider threshold (90) and active_team != winning_team -> schneider bonus applies
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    player_teams: dict[Player, Team] = {
        player_1: team_two_players_1,
        player_2: team_two_players_1,
        player_3: team_two_players_2,
        player_4: team_two_players_2,
    }

    team_two_players_1.points = 90
    team_two_players_2.points = 30
    calculator: GameValueCalculator = make_calculator(
        SauspielGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1, player_2],
        active_team=team_two_players_2,  # active_team is the loser
    )
    assert calculator.basic_game_value_adds(game_value=20) == 30


def test_basic_game_value_adds_schneider_threshold_active_team_wins(
    team_two_players_1,
    team_two_players_2,
):
    # Winning team == schneider threshold (90) and active_team == winning_team -> no schneider bonus.
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    player_teams: dict[Player, Team] = {
        player_1: team_two_players_1,
        player_2: team_two_players_1,
        player_3: team_two_players_2,
        player_4: team_two_players_2,
    }

    team_two_players_1.points = 90
    team_two_players_2.points = 30
    calculator: GameValueCalculator = make_calculator(
        SauspielGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1, player_2],
        active_team=team_two_players_1,  # active_team is the winner
    )
    assert calculator.basic_game_value_adds(game_value=20) == 20


def test_basic_game_value_adds_black(
    team_two_players_1,
    team_two_players_2,
):
    # Winning team collects all 120 points → schneider + black bonus
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    player_teams: dict[Player, Team] = {
        player_1: team_two_players_1,
        player_2: team_two_players_1,
        player_3: team_two_players_2,
        player_4: team_two_players_2,
    }

    team_two_players_1.points = TOTAL_POINTS
    team_two_players_2.points = 0
    calculator: GameValueCalculator = make_calculator(
        SauspielGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1, player_2],
        active_team=team_two_players_1,
    )
    # 20 (base) + 10 (schneider) + 10 (black) = 40
    assert calculator.basic_game_value_adds(game_value=20) == 40


def test_basic_game_value_adds_doubles(
    team_two_players_1,
    team_two_players_2,
):
    # 2 doubles → value multiplied by 4
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    player_teams: dict[Player, Team] = {
        player_1: team_two_players_1,
        player_2: team_two_players_1,
        player_3: team_two_players_2,
        player_4: team_two_players_2,
    }

    team_two_players_1.points = 61
    team_two_players_2.points = 59
    calculator: GameValueCalculator = make_calculator(
        SauspielGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1, player_2],
        active_team=team_two_players_1,
        amount_game_value_doubles=2,
    )
    assert calculator.basic_game_value_adds(game_value=20) == 80


# calculate game value


def test_sauspiel_calculate_game_value_base(
    team_two_players_1,
    team_two_players_2,
):
    # Minimal Sauspiel: call_price only
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    player_teams: dict[Player, Team] = {
        player_1: team_two_players_1,
        player_2: team_two_players_1,
        player_3: team_two_players_2,
        player_4: team_two_players_2,
    }

    team_two_players_1.points = 61
    team_two_players_2.points = 59
    calculator: GameValueCalculator = make_calculator(
        SauspielGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1, player_2],
        active_team=team_two_players_1,
        call_price=20,
    )
    assert calculator.calculate_game_value() == 20


def test_sauspiel_calculate_game_value_with_runners_and_schneider(
    team_two_players_1,
    team_two_players_2,
):
    player_1: Player = team_two_players_1.players[0]
    player_2: Player = team_two_players_1.players[1]
    player_3: Player = team_two_players_2.players[0]
    player_4: Player = team_two_players_2.players[1]
    player_teams: dict[Player, Team] = {
        player_1: team_two_players_1,
        player_2: team_two_players_1,
        player_3: team_two_players_2,
        player_4: team_two_players_2,
    }

    team_two_players_1.points = 91
    team_two_players_2.points = 29
    calculator: GameValueCalculator = make_calculator(
        SauspielGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1, player_2],
        active_team=team_two_players_1,
        call_price=20,
        runners_amount=3,
    )
    # 20 (call) + 30 (3 runners) + 10 (schneider) = 60
    assert calculator.calculate_game_value() == 60


def test_wenz_calculate_game_value_base(
    team_alone_player_1,
    team_three_players_2_3_4,
):
    # Minimal Wenz: alone_price only
    player_1: Player = team_alone_player_1.players[0]
    player_2: Player = team_three_players_2_3_4.players[0]
    player_3: Player = team_three_players_2_3_4.players[1]
    player_4: Player = team_three_players_2_3_4.players[2]
    player_teams: dict[Player, Team] = {
        player_1: team_alone_player_1,
        player_2: team_three_players_2_3_4,
        player_3: team_three_players_2_3_4,
        player_4: team_three_players_2_3_4,
    }

    team_alone_player_1.points = 61
    team_three_players_2_3_4.points = 59
    calculator: GameValueCalculator = make_calculator(
        WenzGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1],
        active_team=team_alone_player_1,
        alone_price=50,
    )
    assert calculator.calculate_game_value() == 50


def test_solo_calculate_game_value_with_doubles(
    team_alone_player_1,
    team_three_players_2_3_4,
):
    player_1: Player = team_alone_player_1.players[0]
    player_2: Player = team_three_players_2_3_4.players[0]
    player_3: Player = team_three_players_2_3_4.players[1]
    player_4: Player = team_three_players_2_3_4.players[2]
    player_teams: dict[Player, Team] = {
        player_1: team_alone_player_1,
        player_2: team_three_players_2_3_4,
        player_3: team_three_players_2_3_4,
        player_4: team_three_players_2_3_4,
    }

    team_alone_player_1.points = 61
    team_three_players_2_3_4.points = 59
    calculator: GameValueCalculator = make_calculator(
        SoloGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1],
        active_team=team_alone_player_1,
        alone_price=50,
        amount_game_value_doubles=1,
    )
    assert calculator.calculate_game_value() == 100


def test_ramsch_calculate_game_value_base(
    team_alone_player_1,
    team_alone_player_2,
    team_alone_player_3,
    team_alone_player_4,
):
    player_1: Player = team_alone_player_1.players[0]
    player_2: Player = team_alone_player_2.players[0]
    player_3: Player = team_alone_player_3.players[0]
    player_4: Player = team_alone_player_4.players[0]
    player_teams: dict[Player, Team] = {
        player_1: team_alone_player_1,
        player_2: team_alone_player_2,
        player_3: team_alone_player_3,
        player_4: team_alone_player_4,
    }

    # All the players collected cards -> no virgins
    player_2.collected_cards = [MagicMock()]
    player_1.collected_cards = [MagicMock()]
    player_3.collected_cards = [MagicMock()]
    player_4.collected_cards = [MagicMock()]

    calculator: GameValueCalculator = make_calculator(
        RamschGameValueCalculator,
        player_teams=player_teams,
        winners=[player_2, player_3, player_4],
        alone_price=20,
    )
    assert calculator.calculate_game_value() == 20


def test_ramsch_calculate_game_value_one_virgin(
    team_alone_player_1,
    team_alone_player_2,
    team_alone_player_3,
    team_alone_player_4,
):
    # 1 player collected no cards → 1 extra double → alone_price * 2
    player_1: Player = team_alone_player_1.players[0]
    player_2: Player = team_alone_player_2.players[0]
    player_3: Player = team_alone_player_3.players[0]
    player_4: Player = team_alone_player_4.players[0]
    player_teams: dict[Player, Team] = {
        player_1: team_alone_player_1,
        player_2: team_alone_player_2,
        player_3: team_alone_player_3,
        player_4: team_alone_player_4,
    }

    player_2.collected_cards = []
    player_1.collected_cards = [MagicMock()]
    player_3.collected_cards = [MagicMock()]
    player_4.collected_cards = [MagicMock()]
    calculator: GameValueCalculator = make_calculator(
        RamschGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1, player_3, player_4],
        alone_price=20,
    )
    assert calculator.calculate_game_value() == 40


def test_ramsch_calculate_game_value_two_virgins(
    team_alone_player_1,
    team_alone_player_2,
    team_alone_player_3,
    team_alone_player_4,
):
    # 2 virgins → 2 extra doubles → alone_price * 4
    player_1: Player = team_alone_player_1.players[0]
    player_2: Player = team_alone_player_2.players[0]
    player_3: Player = team_alone_player_3.players[0]
    player_4: Player = team_alone_player_4.players[0]
    player_teams: dict[Player, Team] = {
        player_1: team_alone_player_1,
        player_2: team_alone_player_2,
        player_3: team_alone_player_3,
        player_4: team_alone_player_4,
    }

    player_2.collected_cards = []
    player_3.collected_cards = []
    player_1.collected_cards = [MagicMock()]
    player_4.collected_cards = [MagicMock()]
    calculator: GameValueCalculator = make_calculator(
        RamschGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1, player_4],
        alone_price=20,
    )
    assert calculator.calculate_game_value() == 80


def test_ramsch_calculate_game_value_existing_doubles_combined_with_virgin(
    team_alone_player_1,
    team_alone_player_2,
    team_alone_player_3,
    team_alone_player_4,
):
    # 1 pre-existing double + 1 virgin → 2 doubles total → alone_price * 4
    player_1: Player = team_alone_player_1.players[0]
    player_2: Player = team_alone_player_2.players[0]
    player_3: Player = team_alone_player_3.players[0]
    player_4: Player = team_alone_player_4.players[0]
    player_teams: dict[Player, Team] = {
        player_1: team_alone_player_1,
        player_2: team_alone_player_2,
        player_3: team_alone_player_3,
        player_4: team_alone_player_4,
    }

    player_2.collected_cards = []
    player_1.collected_cards = [MagicMock()]
    player_3.collected_cards = [MagicMock()]
    player_4.collected_cards = [MagicMock()]
    calculator: GameValueCalculator = make_calculator(
        RamschGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1, player_3, player_4],
        alone_price=20,
        amount_game_value_doubles=1,
    )
    assert calculator.calculate_game_value() == 80


# Tout family: no schneider/black bonus, but the whole game value (including
# runners and doubles) is doubled


def test_tout_calculate_game_value_ignores_schneider_and_black(
    team_alone_player_1, team_three_players_2_3_4
):
    player_1: Player = team_alone_player_1.players[0]
    player_2, player_3, player_4 = team_three_players_2_3_4.players
    player_teams: dict[Player, Team] = {
        player_1: team_alone_player_1,
        player_2: team_three_players_2_3_4,
        player_3: team_three_players_2_3_4,
        player_4: team_three_players_2_3_4,
    }

    team_alone_player_1.points = TOTAL_POINTS
    team_three_players_2_3_4.points = 0
    calculator: GameValueCalculator = make_calculator(
        ToutGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1],
        active_team=team_alone_player_1,
        alone_price=50,
    )
    # (50 + 0) * 2 = 100, despite winning black (schneider/black don't apply)
    assert calculator.calculate_game_value() == 100


def test_tout_calculate_game_value_with_runners_and_doubles(
    team_alone_player_1, team_three_players_2_3_4
):
    player_1: Player = team_alone_player_1.players[0]
    player_2, player_3, player_4 = team_three_players_2_3_4.players
    player_teams: dict[Player, Team] = {
        player_1: team_alone_player_1,
        player_2: team_three_players_2_3_4,
        player_3: team_three_players_2_3_4,
        player_4: team_three_players_2_3_4,
    }

    team_alone_player_1.points = TOTAL_POINTS
    team_three_players_2_3_4.points = 0
    calculator: GameValueCalculator = make_calculator(
        ToutGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1],
        active_team=team_alone_player_1,
        alone_price=50,
        base_price=10,
        runners_amount=3,
        amount_game_value_doubles=1,
    )
    # ((50 + 30) * 2) * 2 = 320
    assert calculator.calculate_game_value() == 320


def test_wenz_tout_and_solo_tout_match_tout_formula(
    team_alone_player_1, team_three_players_2_3_4
):
    player_1: Player = team_alone_player_1.players[0]
    player_2, player_3, player_4 = team_three_players_2_3_4.players
    player_teams: dict[Player, Team] = {
        player_1: team_alone_player_1,
        player_2: team_three_players_2_3_4,
        player_3: team_three_players_2_3_4,
        player_4: team_three_players_2_3_4,
    }

    team_alone_player_1.points = TOTAL_POINTS
    team_three_players_2_3_4.points = 0

    values = {
        cls.__name__: make_calculator(
            cls,
            player_teams=player_teams,
            winners=[player_1],
            active_team=team_alone_player_1,
            alone_price=50,
        ).calculate_game_value()
        for cls in (
            ToutGameValueCalculator,
            WenzToutGameValueCalculator,
            SoloToutGameValueCalculator,
        )
    }
    assert set(values.values()) == {100}


# HochzeitGameValueCalculator is a plain AloneGameValueCalculator (2v2 teams)


def test_hochzeit_calculate_game_value_matches_alone_formula(
    team_two_players_1, team_two_players_2
):
    player_1, player_2 = team_two_players_1.players
    player_3, player_4 = team_two_players_2.players
    player_teams: dict[Player, Team] = {
        player_1: team_two_players_1,
        player_2: team_two_players_1,
        player_3: team_two_players_2,
        player_4: team_two_players_2,
    }

    team_two_players_1.points = 91
    team_two_players_2.points = 29
    calculator: GameValueCalculator = make_calculator(
        HochzeitGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1, player_2],
        active_team=team_two_players_1,
        alone_price=50,
        runners_amount=3,
    )
    # 50 (alone) + 30 (3 runners) + 10 (schneider) = 90
    assert calculator.calculate_game_value() == 90


# game_value_breakdown


def test_sauspiel_game_value_breakdown_includes_all_extras(
    team_two_players_1, team_two_players_2
):
    player_1, player_2 = team_two_players_1.players
    player_3, player_4 = team_two_players_2.players
    player_teams: dict[Player, Team] = {
        player_1: team_two_players_1,
        player_2: team_two_players_1,
        player_3: team_two_players_2,
        player_4: team_two_players_2,
    }

    team_two_players_1.points = TOTAL_POINTS
    team_two_players_2.points = 0
    calculator: GameValueCalculator = make_calculator(
        SauspielGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1, player_2],
        active_team=team_two_players_1,
        call_price=20,
        runners_amount=3,
        amount_game_value_doubles=1,
    )
    breakdown = calculator.game_value_breakdown()

    assert "Call price:" in breakdown and "20 cents" in breakdown
    assert "Schneider:" in breakdown and "+ 10 cents" in breakdown
    assert "Black:" in breakdown
    assert "Runners:" in breakdown and "+ 30 cents" in breakdown
    assert "Doubles:" in breakdown and "* 2" in breakdown


def test_alone_game_value_breakdown_without_extras(
    team_alone_player_1, team_three_players_2_3_4
):
    player_1: Player = team_alone_player_1.players[0]
    player_2, player_3, player_4 = team_three_players_2_3_4.players
    player_teams: dict[Player, Team] = {
        player_1: team_alone_player_1,
        player_2: team_three_players_2_3_4,
        player_3: team_three_players_2_3_4,
        player_4: team_three_players_2_3_4,
    }

    team_alone_player_1.points = 61
    team_three_players_2_3_4.points = 59
    calculator: GameValueCalculator = make_calculator(
        SoloGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1],
        active_team=team_alone_player_1,
        alone_price=50,
    )
    breakdown = calculator.game_value_breakdown()

    assert "Alone price:" in breakdown and "50 cents" in breakdown
    assert "Schneider:" not in breakdown
    assert "Black:" not in breakdown
    assert "Runners:" not in breakdown
    assert "Doubles:" not in breakdown


def test_tout_game_value_breakdown_has_no_schneider_or_black(
    team_alone_player_1, team_three_players_2_3_4
):
    player_1: Player = team_alone_player_1.players[0]
    player_2, player_3, player_4 = team_three_players_2_3_4.players
    player_teams: dict[Player, Team] = {
        player_1: team_alone_player_1,
        player_2: team_three_players_2_3_4,
        player_3: team_three_players_2_3_4,
        player_4: team_three_players_2_3_4,
    }

    team_alone_player_1.points = TOTAL_POINTS
    team_three_players_2_3_4.points = 0
    calculator: GameValueCalculator = make_calculator(
        ToutGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1],
        active_team=team_alone_player_1,
        alone_price=50,
        base_price=10,
        runners_amount=3,
    )
    breakdown = calculator.game_value_breakdown()

    assert "Alone price:" in breakdown and "50 cents" in breakdown
    assert "Runners:" in breakdown and "+ 30 cents" in breakdown
    assert "Schneider:" not in breakdown
    assert "Black:" not in breakdown
    assert "Tout:" in breakdown and "* 2" in breakdown


def test_ramsch_game_value_breakdown_with_doubles_and_virgin(
    team_alone_player_1,
    team_alone_player_2,
    team_alone_player_3,
    team_alone_player_4,
):
    player_1: Player = team_alone_player_1.players[0]
    player_2: Player = team_alone_player_2.players[0]
    player_3: Player = team_alone_player_3.players[0]
    player_4: Player = team_alone_player_4.players[0]
    player_teams: dict[Player, Team] = {
        player_1: team_alone_player_1,
        player_2: team_alone_player_2,
        player_3: team_alone_player_3,
        player_4: team_alone_player_4,
    }

    player_2.collected_cards = []
    player_1.collected_cards = [MagicMock()]
    player_3.collected_cards = [MagicMock()]
    player_4.collected_cards = [MagicMock()]
    calculator: GameValueCalculator = make_calculator(
        RamschGameValueCalculator,
        player_teams=player_teams,
        winners=[player_1, player_3, player_4],
        alone_price=20,
        amount_game_value_doubles=1,
    )
    breakdown = calculator.game_value_breakdown()

    assert "Alone price:" in breakdown and "20 cents" in breakdown
    assert "Doubles:" in breakdown and "* 2" in breakdown
    assert "Virgins:" in breakdown and "* 2" in breakdown


def test_ramsch_game_value_breakdown_without_extras(
    team_alone_player_1,
    team_alone_player_2,
    team_alone_player_3,
    team_alone_player_4,
):
    player_1: Player = team_alone_player_1.players[0]
    player_2: Player = team_alone_player_2.players[0]
    player_3: Player = team_alone_player_3.players[0]
    player_4: Player = team_alone_player_4.players[0]
    player_teams: dict[Player, Team] = {
        player_1: team_alone_player_1,
        player_2: team_alone_player_2,
        player_3: team_alone_player_3,
        player_4: team_alone_player_4,
    }

    player_2.collected_cards = [MagicMock()]
    player_1.collected_cards = [MagicMock()]
    player_3.collected_cards = [MagicMock()]
    player_4.collected_cards = [MagicMock()]
    calculator: GameValueCalculator = make_calculator(
        RamschGameValueCalculator,
        player_teams=player_teams,
        winners=[player_2, player_3, player_4],
        alone_price=20,
    )
    breakdown = calculator.game_value_breakdown()

    assert "Alone price:" in breakdown and "20 cents" in breakdown
    assert "Doubles:" not in breakdown
    assert "Virgins:" not in breakdown
