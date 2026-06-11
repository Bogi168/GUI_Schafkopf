import os
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pytest

from card_classes.Cards import Color
from system.gui import constants as c
from system.gui.renderer import GUIRenderer
from system.gui.state import DealAnimation, PlayedCardEntry
from system.Renderer import GameResult
from system.text import no_game_phrase


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


def test_render_game_mode_none_shows_pending_lamps_for_bots(renderer):
    renderer.render_game_mode(game_mode_name=None, chooser=None)

    assert renderer.state.game_choice_lamps == {
        c.LEFT: "pending",
        c.TOP: "pending",
        c.RIGHT: "pending",
    }


def test_render_want_to_play_decision_sets_lamp_color(renderer, player_2, player_3):
    renderer.render_game_mode(game_mode_name=None, chooser=None)

    renderer.render_want_to_play_decision(player=player_2, wants_to_play=True)
    renderer.render_want_to_play_decision(player=player_3, wants_to_play=False)

    assert renderer.state.game_choice_lamps[c.LEFT] == "yes"
    assert renderer.state.game_choice_lamps[c.TOP] == "no"


def test_render_want_to_play_decision_ignores_human_seat(renderer, player_1):
    renderer.render_game_mode(game_mode_name=None, chooser=None)

    renderer.render_want_to_play_decision(player=player_1, wants_to_play=True)

    assert c.BOTTOM not in renderer.state.game_choice_lamps


def test_render_double_game_value_decision_announces_when_doubling(renderer, player_2):
    calls = []
    renderer._announce_choice = lambda *args, **kwargs: calls.append((args, kwargs))

    renderer.render_double_game_value_decision(player=player_2, doubles=True)

    assert calls == [(("Testplayer 2 doubles the game value!",), {})]


def test_render_double_game_value_decision_silent_when_not_doubling(renderer, player_2):
    calls = []
    renderer._announce_choice = lambda *args, **kwargs: calls.append((args, kwargs))

    renderer.render_double_game_value_decision(player=player_2, doubles=False)

    assert calls == []


def test_render_game_mode_with_game_hides_lamps(renderer):
    renderer.render_game_mode(game_mode_name=None, chooser=None)

    renderer.render_game_mode(game_mode_name="Sauspiel", chooser=None)

    assert renderer.state.game_choice_lamps == {}


def test_render_no_game_message_hides_lamps(renderer):
    renderer.render_game_mode(game_mode_name=None, chooser=None)

    renderer.render(message=no_game_phrase)

    assert renderer.state.game_choice_lamps == {}


def test_draw_bot_seat_with_lamp_does_not_crash(renderer):
    renderer.render_game_mode(game_mode_name=None, chooser=None)

    renderer._draw((0, 0))


def test_ask_play_again_clears_no_game_message(renderer, monkeypatch):
    renderer.state.message = no_game_phrase.strip()
    monkeypatch.setattr(renderer, "_request", lambda **_kwargs: True)

    renderer.ask_play_again()

    assert renderer.state.message == ""


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


def test_draw_result_panel_highlights_winning_team_and_players(
    renderer, players, player_1, player_2, team_two_players_1, team_two_players_2
):
    team_two_players_1.points = 64
    team_two_players_2.points = 56
    renderer.render_game_result(
        result=GameResult(
            most_point_teams=[team_two_players_1],
            winners=[player_1, player_2],
            game_value=20,
            game_value_breakdown="\nCall price:  20 cents\nSchneider:   + 10 cents",
            players=players,
        )
    )

    renderer._draw((0, 0))


def test_draw_result_panel_handles_no_winners(renderer, players):
    renderer.render_game_result(
        result=GameResult(
            most_point_teams=[],
            winners=[],
            game_value=0,
            game_value_breakdown="",
            players=players,
        )
    )

    renderer._draw((0, 0))


def test_render_farewell_shows_centered_announcement_and_requests_quit(renderer):
    renderer.render_farewell("\nThank you for playing!")

    assert renderer.state.choice_announcement == "Thank you for playing!"
    assert renderer._should_quit is True

    renderer._draw((0, 0))


def test_render_shuffle_cards_resets_hands_and_clears_afterwards(renderer, eichel_sau):
    renderer.state.hand_sizes = [3, 4, 5, 6]
    renderer.state.human_hand = [eichel_sau]

    renderer.render_shuffle_cards()

    assert renderer.state.hand_sizes == [0, 0, 0, 0]
    assert renderer.state.human_hand == []
    assert renderer.state.shuffle_start_time is None


def test_render_deal_cards_increments_hand_sizes_for_each_player(renderer, players):
    renderer.render_deal_cards(players=players, cards_per_player=4)

    assert renderer.state.hand_sizes == [4, 4, 4, 4]
    assert renderer.state.dealing_card is None


def test_render_deal_cards_reveals_human_cards_face_up_immediately(
    renderer, player_1, players, eichel_sau, gruen_sau, herz_sau, schellen_sau
):
    player_1.player_cards = [eichel_sau, gruen_sau, herz_sau, schellen_sau]

    renderer.render_deal_cards(players=players, cards_per_player=4)

    assert renderer.state.human_hand == player_1.player_cards
    assert renderer.state.hand_sizes[c.BOTTOM] == 4


def test_render_deal_cards_inserts_new_cards_in_sorted_order(
    renderer, player_1, players, eichel_sau, gruen_sau, herz_sau, schellen_sau
):
    # Cards already revealed from a previous deal phase.
    renderer.state.human_hand = [eichel_sau, gruen_sau]
    renderer.state.hand_sizes[c.BOTTOM] = 2
    # The freshly re-sorted full hand interleaves the two new cards.
    player_1.player_cards = [herz_sau, eichel_sau, schellen_sau, gruen_sau]

    renderer.render_deal_cards(players=players, cards_per_player=2)

    assert renderer.state.human_hand == player_1.player_cards
    assert renderer.state.hand_sizes[c.BOTTOM] == 4


def test_draw_shuffle_is_noop_when_not_shuffling(renderer):
    renderer.state.shuffle_start_time = None

    renderer._draw_shuffle()


def test_draw_shuffle_does_not_crash_while_active(renderer):
    renderer.state.shuffle_start_time = time.time()
    renderer.state.shuffle_duration = 1.0

    renderer._draw_shuffle()


def test_draw_dealing_card_is_noop_when_not_dealing(renderer):
    renderer.state.dealing_card = None

    renderer._draw_dealing_card()


def test_draw_dealing_card_does_not_crash_while_active(renderer):
    renderer.state.dealing_card = DealAnimation(
        seat=c.LEFT, start_time=time.time(), duration=0.12
    )

    renderer._draw_dealing_card()


def test_deal_target_returns_seat_hand_positions(renderer):
    assert renderer._deal_target(c.LEFT) == c.SEAT_HAND_CENTER[c.LEFT]
    assert renderer._deal_target(c.TOP) == c.SEAT_HAND_CENTER[c.TOP]
    assert renderer._deal_target(c.RIGHT) == c.SEAT_HAND_CENTER[c.RIGHT]

    bottom_x, bottom_y = renderer._deal_target(c.BOTTOM)
    assert bottom_x == c.WINDOW_WIDTH // 2


def test_draw_does_not_crash_during_dealing_animation(renderer):
    renderer.state.shuffle_start_time = time.time()
    renderer.state.shuffle_duration = 1.0
    renderer.state.dealing_card = DealAnimation(
        seat=c.TOP, start_time=time.time(), duration=0.12
    )
    renderer.state.hand_sizes = [2, 1, 1, 1]

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
