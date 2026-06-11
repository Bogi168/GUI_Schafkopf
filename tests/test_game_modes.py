import pytest
from unittest.mock import MagicMock

from card_classes.Cards import Color
from schafkopf_classes.Schafkopf import Schafkopf
from system.custom_exceptions import GameNotPlayableError

from game_classes.game_modes.Sauspiel import Sauspiel
from game_classes.game_modes.Wenz import Wenz
from game_classes.game_modes.WenzTout import WenzTout
from game_classes.game_modes.Solo import Solo
from game_classes.game_modes.SoloTout import SoloTout
from game_classes.game_modes.Hochzeit import Hochzeit
from game_classes.game_modes.Ramsch import Ramsch


@pytest.fixture
def schafkopf(players):
    schafkopf = Schafkopf(
        renderer=MagicMock(), base_price=10, call_price=20, alone_price=30
    )
    schafkopf.players = players
    schafkopf.amount_game_value_doubles = 1
    return schafkopf


def assert_base_kwargs(kwargs, schafkopf):
    assert kwargs["cards"] is schafkopf.cards
    assert kwargs["renderer"] is schafkopf.renderer
    assert kwargs["players"] is schafkopf.players
    assert kwargs["amount_game_value_doubles"] == schafkopf.amount_game_value_doubles


def test_sauspiel_gather_kwargs(schafkopf, player_1, monkeypatch):
    monkeypatch.setattr(player_1, "get_sau_color", lambda: Color.EICHEL)

    kwargs = Sauspiel.gather_kwargs(chooser=player_1, schafkopf=schafkopf)

    assert_base_kwargs(kwargs, schafkopf)
    assert kwargs["game_chooser"] is player_1
    assert kwargs["base_price"] == schafkopf.base_price
    assert kwargs["call_price"] == schafkopf.call_price
    assert kwargs["sau_color"] == Color.EICHEL
    assert set(kwargs.keys()) == {
        "cards",
        "renderer",
        "players",
        "amount_game_value_doubles",
        "game_chooser",
        "base_price",
        "call_price",
        "sau_color",
    }


def test_wenz_gather_kwargs(schafkopf, player_1):
    kwargs = Wenz.gather_kwargs(chooser=player_1, schafkopf=schafkopf)

    assert_base_kwargs(kwargs, schafkopf)
    assert kwargs["game_chooser"] is player_1
    assert kwargs["base_price"] == schafkopf.base_price
    assert kwargs["alone_price"] == schafkopf.alone_price
    assert set(kwargs.keys()) == {
        "cards",
        "renderer",
        "players",
        "amount_game_value_doubles",
        "game_chooser",
        "base_price",
        "alone_price",
    }


def test_wenz_tout_gather_kwargs_same_shape_as_wenz(schafkopf, player_1):
    wenz_kwargs = Wenz.gather_kwargs(chooser=player_1, schafkopf=schafkopf)
    wenz_tout_kwargs = WenzTout.gather_kwargs(chooser=player_1, schafkopf=schafkopf)

    assert set(wenz_tout_kwargs.keys()) == set(wenz_kwargs.keys())
    assert_base_kwargs(wenz_tout_kwargs, schafkopf)
    assert wenz_tout_kwargs["game_chooser"] is player_1
    assert wenz_tout_kwargs["base_price"] == schafkopf.base_price
    assert wenz_tout_kwargs["alone_price"] == schafkopf.alone_price


def test_solo_gather_kwargs(schafkopf, player_1, monkeypatch):
    monkeypatch.setattr(player_1, "get_trump_color", lambda: Color.HERZ)

    kwargs = Solo.gather_kwargs(chooser=player_1, schafkopf=schafkopf)

    assert_base_kwargs(kwargs, schafkopf)
    assert kwargs["game_chooser"] is player_1
    assert kwargs["base_price"] == schafkopf.base_price
    assert kwargs["alone_price"] == schafkopf.alone_price
    assert kwargs["trump_color"] == Color.HERZ
    assert set(kwargs.keys()) == {
        "cards",
        "renderer",
        "players",
        "amount_game_value_doubles",
        "game_chooser",
        "base_price",
        "alone_price",
        "trump_color",
    }


def test_solo_tout_gather_kwargs_same_shape_as_solo(schafkopf, player_1, monkeypatch):
    monkeypatch.setattr(player_1, "get_trump_color", lambda: Color.GRUEN)

    solo_kwargs = Solo.gather_kwargs(chooser=player_1, schafkopf=schafkopf)
    solo_tout_kwargs = SoloTout.gather_kwargs(chooser=player_1, schafkopf=schafkopf)

    assert set(solo_tout_kwargs.keys()) == set(solo_kwargs.keys())
    assert_base_kwargs(solo_tout_kwargs, schafkopf)
    assert solo_tout_kwargs["game_chooser"] is player_1
    assert solo_tout_kwargs["base_price"] == schafkopf.base_price
    assert solo_tout_kwargs["alone_price"] == schafkopf.alone_price
    assert solo_tout_kwargs["trump_color"] == Color.GRUEN


def test_hochzeit_gather_kwargs_with_partner(schafkopf, player_1, player_2, monkeypatch):
    monkeypatch.setattr(
        schafkopf, "get_hochzeit_partner", lambda game_chooser: player_2
    )

    kwargs = Hochzeit.gather_kwargs(chooser=player_1, schafkopf=schafkopf)

    assert_base_kwargs(kwargs, schafkopf)
    assert kwargs["alone_price"] == schafkopf.alone_price
    assert kwargs["partner"] is player_2
    assert kwargs["game_chooser"] is player_1
    assert kwargs["base_price"] == schafkopf.base_price
    assert set(kwargs.keys()) == {
        "cards",
        "renderer",
        "players",
        "amount_game_value_doubles",
        "alone_price",
        "partner",
        "game_chooser",
        "base_price",
    }


def test_hochzeit_gather_kwargs_without_partner_raises(schafkopf, player_1, monkeypatch):
    monkeypatch.setattr(schafkopf, "get_hochzeit_partner", lambda game_chooser: None)

    with pytest.raises(GameNotPlayableError):
        Hochzeit.gather_kwargs(chooser=player_1, schafkopf=schafkopf)


def test_ramsch_gather_kwargs(schafkopf):
    kwargs = Ramsch.gather_kwargs(chooser=None, schafkopf=schafkopf)

    assert_base_kwargs(kwargs, schafkopf)
    assert kwargs["alone_price"] == schafkopf.alone_price
    assert set(kwargs.keys()) == {
        "cards",
        "renderer",
        "players",
        "amount_game_value_doubles",
        "alone_price",
    }
