from unittest.mock import MagicMock

import pytest

from player_classes.Player import Bot, Player
from schafkopf_classes.Schafkopf import Schafkopf


@pytest.fixture
def schafkopf() -> Schafkopf:
    renderer = MagicMock()
    renderer.ask_yes_no.return_value = False
    game = Schafkopf(renderer=renderer, base_price=10, call_price=20, alone_price=30)
    game.players = [
        Player(
            player_name="Starter",
            renderer=renderer,
            game_decision_validator=game.game_decision_validator,
        ),
        Bot(
            bot_name="Bot 1",
            renderer=renderer,
            game_decision_validator=game.game_decision_validator,
        ),
        Bot(
            bot_name="Bot 2",
            renderer=renderer,
            game_decision_validator=game.game_decision_validator,
        ),
        Bot(
            bot_name="Bot 3",
            renderer=renderer,
            game_decision_validator=game.game_decision_validator,
        ),
    ]
    return game


def test_prepare_cards_deals_eight_cards_per_player(schafkopf):
    schafkopf.prepare_cards()

    for player in schafkopf.players:
        assert len(player.player_cards) == 8


def test_prepare_cards_announces_double_game_value_decisions(schafkopf, monkeypatch):
    renderer = schafkopf.renderer
    starter, bot1, bot2, bot3 = schafkopf.players

    monkeypatch.setattr(bot1, "ask_double_game_value", lambda: True)
    monkeypatch.setattr(bot2, "ask_double_game_value", lambda: False)
    monkeypatch.setattr(bot3, "ask_double_game_value", lambda: False)

    schafkopf.prepare_cards()

    decisions = {
        call.kwargs["player"]: call.kwargs["doubles"]
        for call in renderer.render_double_game_value_decision.call_args_list
    }
    assert decisions == {starter: False, bot1: True, bot2: False, bot3: False}
    assert schafkopf.amount_game_value_doubles == 1


def test_prepare_cards_animates_shuffle_then_two_deals_in_turn_order(schafkopf):
    renderer = schafkopf.renderer
    players_in_turn_order = list(schafkopf.players)

    schafkopf.prepare_cards()

    assert renderer.render_shuffle_cards.call_count == 1
    assert renderer.render_deal_cards.call_count == 2
    for deal_call in renderer.render_deal_cards.call_args_list:
        assert deal_call.kwargs["players"] == players_in_turn_order
        assert deal_call.kwargs["cards_per_player"] == 4

    method_names = [method_call[0] for method_call in renderer.method_calls]
    assert method_names.index("render_shuffle_cards") < method_names.index(
        "render_deal_cards"
    )
