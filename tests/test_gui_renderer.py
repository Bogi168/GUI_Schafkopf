import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pytest

from card_classes.Cards import Color
from system.gui import constants as c
from system.gui.renderer import GUIRenderer
from system.gui.state import PlayedCardEntry
from system.Renderer import GameResult


@pytest.fixture
def renderer(players, monkeypatch) -> GUIRenderer:
    monkeypatch.setattr("system.gui.renderer.time.sleep", lambda *_args: None)
    gui_renderer = GUIRenderer()
    gui_renderer.set_players(players)
    return gui_renderer


def test_render_trick_winner_stores_previous_round_cards(
    renderer, players, eichel_sau, gruen_sau, herz_sau, schellen_sau
):
    entries = [
        PlayedCardEntry(seat=0, card=eichel_sau),
        PlayedCardEntry(seat=1, card=gruen_sau),
        PlayedCardEntry(seat=2, card=herz_sau),
        PlayedCardEntry(seat=3, card=schellen_sau),
    ]
    renderer.state.center_cards = list(entries)

    renderer.render_trick_winner(winner=players[0])

    assert renderer.state.previous_round_cards == entries
    assert renderer.state.center_cards == []


def test_render_trick_winner_overwrites_older_round(
    renderer, players, eichel_sau, gruen_sau, herz_sau, schellen_sau, eichel_ten
):
    renderer.state.previous_round_cards = [PlayedCardEntry(seat=0, card=eichel_sau)]
    new_entries = [PlayedCardEntry(seat=1, card=eichel_ten)]
    renderer.state.center_cards = list(new_entries)

    renderer.render_trick_winner(winner=players[0])

    assert renderer.state.previous_round_cards == new_entries


def test_render_game_result_resets_previous_round(renderer, players, eichel_sau):
    renderer.state.previous_round_cards = [PlayedCardEntry(seat=0, card=eichel_sau)]
    renderer.state.show_previous_round = True

    renderer.render_game_result(
        result=GameResult(
            most_point_teams=[],
            winners=[],
            game_value=0,
            game_value_breakdown="",
            players=players,
        )
    )

    assert renderer.state.previous_round_cards == []
    assert renderer.state.show_previous_round is False


def test_render_game_result_resets_game_mode_badge(renderer, players):
    renderer.state.current_game_mode = "Sauspiel"
    renderer.state.current_game_mode_chooser_seat = 0
    renderer.state.current_game_mode_detail = "Eichel Sau"
    renderer.state.current_game_mode_detail_color = Color.EICHEL

    renderer.render_game_result(
        result=GameResult(
            most_point_teams=[],
            winners=[],
            game_value=0,
            game_value_breakdown="",
            players=players,
        )
    )

    assert renderer.state.current_game_mode is None
    assert renderer.state.current_game_mode_chooser_seat is None
    assert renderer.state.current_game_mode_detail is None
    assert renderer.state.current_game_mode_detail_color is None


def test_render_game_mode_none_resets_previous_round(renderer, eichel_sau):
    renderer.state.previous_round_cards = [PlayedCardEntry(seat=0, card=eichel_sau)]
    renderer.state.show_previous_round = True

    renderer.render_game_mode(game_mode_name=None, chooser=None)

    assert renderer.state.previous_round_cards == []
    assert renderer.state.show_previous_round is False


def test_previous_round_button_toggles_and_dismisses_on_click(renderer, eichel_sau):
    renderer.state.previous_round_cards = [PlayedCardEntry(seat=0, card=eichel_sau)]
    renderer._draw((0, 0))

    button_pos = c.PREVIOUS_ROUND_BUTTON_RECT.center
    renderer._handle_click(button_pos)
    assert renderer.state.show_previous_round is True

    renderer._draw((0, 0))
    renderer._handle_click((c.WINDOW_WIDTH - 1, c.WINDOW_HEIGHT - 1))
    assert renderer.state.show_previous_round is False


def test_previous_round_button_hidden_when_no_round_played(renderer):
    renderer.state.previous_round_cards = []
    renderer._draw((0, 0))

    assert renderer._previous_round_button is None

    button_pos = c.PREVIOUS_ROUND_BUTTON_RECT.center
    renderer._handle_click(button_pos)

    assert renderer.state.show_previous_round is False


def test_draw_previous_round_does_not_crash(renderer, eichel_sau, gruen_sau):
    renderer.state.previous_round_cards = [
        PlayedCardEntry(seat=0, card=eichel_sau),
        PlayedCardEntry(seat=2, card=gruen_sau),
    ]
    renderer.state.show_previous_round = True

    renderer._draw((0, 0))


def test_render_farewell_shows_centered_announcement_and_requests_quit(renderer):
    renderer.render_farewell("\nThank you for playing!")

    assert renderer.state.choice_announcement == "Thank you for playing!"
    assert renderer._should_quit is True

    renderer._draw((0, 0))


def test_main_loop_exits_after_farewell(renderer, monkeypatch):
    monkeypatch.setattr("system.gui.renderer.pygame.event.get", lambda: [])
    monkeypatch.setattr("system.gui.renderer.pygame.display.flip", lambda: None)
    monkeypatch.setattr("system.gui.renderer.pygame.quit", lambda: None)
    renderer.clock = type("DummyClock", (), {"tick": lambda *_args: None})()
    monkeypatch.setattr(
        "system.gui.renderer.os._exit",
        lambda code: (_ for _ in ()).throw(SystemExit(code)),
    )
    renderer._should_quit = True

    with pytest.raises(SystemExit):
        renderer._main_loop()
