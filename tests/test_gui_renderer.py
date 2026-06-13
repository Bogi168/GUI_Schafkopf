import os
import threading
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from unittest.mock import MagicMock

import pytest

from card_classes.Cards import Color
from game_classes.game_modes.Sauspiel import Sauspiel
from game_classes.game_modes.Wenz import Wenz
from player_classes.Player import Bot
from system.gui import constants as c
from system.gui.renderer import GUIRenderer
from system.gui.state import (
    DealAnimation,
    PendingRequest,
    PlayedCardEntry,
    SwapAnimation,
)
from system.gui.widgets import wrap_text
from system.Renderer import ColorChoiceKind, GameResult, YesNoKind
from system.text import (
    no_game_phrase,
    prompt_ask_for_hochzeit,
    prompt_ask_for_ramsch,
    prompt_ask_player_shoots,
)


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


def test_render_shoot_decision_announces_when_shooting(renderer, player_2):
    calls = []
    renderer._announce_choice = lambda *args, **kwargs: calls.append((args, kwargs))

    renderer.render_shoot_decision(player=player_2, shoots=True)

    assert calls == [(("Testplayer 2 shoots!",), {})]


def test_render_shoot_decision_announces_when_shooting_back(renderer, player_2):
    calls = []
    renderer._announce_choice = lambda *args, **kwargs: calls.append((args, kwargs))

    renderer.render_shoot_decision(player=player_2, shoots=True, is_shoot_back=True)

    assert calls == [(("Testplayer 2 shoots back!",), {})]


def test_render_shoot_decision_silent_when_not_shooting(renderer, player_2):
    calls = []
    renderer._announce_choice = lambda *args, **kwargs: calls.append((args, kwargs))

    renderer.render_shoot_decision(player=player_2, shoots=False)

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

    renderer.table_view.draw((0, 0))


# ---------------------------------------------------------------------------
# whose-turn indicator
# ---------------------------------------------------------------------------


def test_render_played_card_marks_bot_seat_active_then_clears(
    renderer, eichel_sau, monkeypatch
):
    # A real Bot whose name matches the seat-1 (LEFT) registration.
    bot = Bot(
        bot_name="Testplayer 2",
        renderer=MagicMock(),
        game_decision_validator=MagicMock(),
    )
    captured = []
    monkeypatch.setattr(
        "system.gui.renderer.time.sleep",
        lambda *_args: captured.append(renderer.state.active_seat),
    )

    renderer.render_played_card(player=bot, card=eichel_sau)

    # The seat is active while the bot "thinks" (during the sleep), then
    # cleared once the card lands.
    assert captured == [c.LEFT]
    assert renderer.state.active_seat is None


def test_ask_card_marks_human_seat_active(renderer, player_1, monkeypatch):
    monkeypatch.setattr(renderer, "_request", lambda **_kwargs: 0)

    renderer.ask_card(player=player_1, player_cards=[], legal_mask=[True])

    assert renderer.state.active_seat == c.BOTTOM


def test_ask_card_swap_does_not_mark_turn(renderer, player_1, monkeypatch):
    monkeypatch.setattr(renderer, "_request", lambda **_kwargs: 0)

    renderer.ask_card(player=player_1, player_cards=[], legal_mask=[True], is_swap=True)

    assert renderer.state.active_seat is None


def test_render_game_result_clears_active_seat(renderer, players):
    renderer.state.active_seat = c.LEFT

    renderer.render_game_result(
        result=GameResult(
            most_point_teams=[],
            winners=[],
            game_value=0,
            game_value_breakdown="",
            players=players,
        )
    )

    assert renderer.state.active_seat is None


def test_draw_active_seat_ring_does_not_crash(renderer):
    for seat in (c.LEFT, c.TOP, c.RIGHT, c.BOTTOM):
        renderer.state.active_seat = seat
        renderer.table_view.draw((0, 0))


# ---------------------------------------------------------------------------
# legal-card affordance on the human hand
# ---------------------------------------------------------------------------


def test_draw_human_hand_with_legal_mask_and_hover_does_not_crash(
    renderer, eichel_sau, gruen_sau, herz_sau
):
    renderer.state.human_hand = [eichel_sau, gruen_sau, herz_sau]
    renderer.state.pending = PendingRequest(kind="card", legal_mask=[True, False, True])

    base_rects = renderer.table_view._hand_card_rects(3)
    # Hover the first (legal) card.
    renderer.table_view.draw(base_rects[0].center)

    # Hit-testing exposes the base rects in card order, regardless of the
    # cosmetic hover lift.
    assert renderer.table_view.hit_test().card_rects == base_rects


def test_draw_human_hand_hovering_illegal_card_does_not_crash(
    renderer, eichel_sau, gruen_sau
):
    renderer.state.human_hand = [eichel_sau, gruen_sau]
    renderer.state.pending = PendingRequest(kind="card", legal_mask=[False, True])

    base_rects = renderer.table_view._hand_card_rects(2)
    # Hovering an illegal card must not lift it or break drawing.
    renderer.table_view.draw(base_rects[0].center)

    assert renderer.table_view.hit_test().card_rects == base_rects


def test_ask_play_again_clears_no_game_message(renderer, monkeypatch):
    renderer.state.message = no_game_phrase.strip()
    monkeypatch.setattr(renderer, "_request", lambda **_kwargs: True)

    renderer.ask_play_again()

    assert renderer.state.message == ""


def test_previous_round_button_toggles_and_dismisses_on_click(renderer, eichel_sau):
    renderer.state.previous_round_cards = [PlayedCardEntry(seat=0, card=eichel_sau)]
    renderer.table_view.draw((0, 0))

    button_pos = c.PREVIOUS_ROUND_BUTTON_RECT.center
    renderer._handle_click(button_pos)
    assert renderer.state.show_previous_round is True

    renderer.table_view.draw((0, 0))
    renderer._handle_click((c.WINDOW_WIDTH - 1, c.WINDOW_HEIGHT - 1))
    assert renderer.state.show_previous_round is False


def test_previous_round_button_hidden_when_no_round_played(renderer):
    renderer.state.previous_round_cards = []
    renderer.table_view.draw((0, 0))

    assert renderer.table_view.hit_test().previous_round_button is None

    button_pos = c.PREVIOUS_ROUND_BUTTON_RECT.center
    renderer._handle_click(button_pos)

    assert renderer.state.show_previous_round is False


def test_draw_previous_round_does_not_crash(renderer, eichel_sau, gruen_sau):
    renderer.state.previous_round_cards = [
        PlayedCardEntry(seat=0, card=eichel_sau),
        PlayedCardEntry(seat=2, card=gruen_sau),
    ]
    renderer.state.show_previous_round = True

    renderer.table_view.draw((0, 0))


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

    renderer.table_view.draw((0, 0))


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

    renderer.table_view.draw((0, 0))


def test_render_farewell_shows_centered_announcement_and_requests_quit(renderer):
    renderer.render_farewell("\nThank you for playing!")

    assert renderer.state.choice_announcement == "Thank you for playing!"
    assert renderer._should_quit is True

    renderer.table_view.draw((0, 0))


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

    renderer.table_view._draw_shuffle()


def test_draw_shuffle_does_not_crash_while_active(renderer):
    renderer.state.shuffle_start_time = time.time()
    renderer.state.shuffle_duration = 1.0

    renderer.table_view._draw_shuffle()


def test_draw_dealing_card_is_noop_when_not_dealing(renderer):
    renderer.state.dealing_card = None

    renderer.table_view._draw_dealing_card()


def test_draw_dealing_card_does_not_crash_while_active(renderer):
    renderer.state.dealing_card = DealAnimation(
        seat=c.LEFT, start_time=time.time(), duration=0.12
    )

    renderer.table_view._draw_dealing_card()


def test_deal_target_returns_seat_hand_positions(renderer):
    assert renderer.table_view._deal_target(c.LEFT) == c.SEAT_HAND_CENTER[c.LEFT]
    assert renderer.table_view._deal_target(c.TOP) == c.SEAT_HAND_CENTER[c.TOP]
    assert renderer.table_view._deal_target(c.RIGHT) == c.SEAT_HAND_CENTER[c.RIGHT]

    bottom_x, bottom_y = renderer.table_view._deal_target(c.BOTTOM)
    assert bottom_x == c.WINDOW_WIDTH // 2


def test_draw_does_not_crash_during_dealing_animation(renderer):
    renderer.state.shuffle_start_time = time.time()
    renderer.state.shuffle_duration = 1.0
    renderer.state.dealing_card = DealAnimation(
        seat=c.TOP, start_time=time.time(), duration=0.12
    )
    renderer.state.hand_sizes = [2, 1, 1, 1]

    renderer.table_view.draw((0, 0))


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


# ---------------------------------------------------------------------------
# ask_* methods
# ---------------------------------------------------------------------------


def test_ask_player_name_requests_name(renderer, monkeypatch):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return "Daniel"

    monkeypatch.setattr(renderer, "_request", fake_request)

    result = renderer.ask_player_name()

    assert result == "Daniel"
    assert captured == {"kind": "player_name", "title": "Enter your name"}


def test_ask_yes_no_allow_yes_offers_both_options(renderer, player_2, monkeypatch):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return True

    monkeypatch.setattr(renderer, "_request", fake_request)

    result = renderer.ask_yes_no(player=player_2, kind=YesNoKind.SHOOT)

    assert result is True
    assert captured["kind"] == "yes_no"
    assert captured["player_name"] == player_2.player_name
    assert captured["title"] == prompt_ask_player_shoots(player_2.player_name)
    assert captured["options"] == [("Yes", True), ("No", False)]


def test_ask_yes_no_disallow_yes_offers_only_no(renderer, player_2, monkeypatch):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return False

    monkeypatch.setattr(renderer, "_request", fake_request)

    result = renderer.ask_yes_no(
        player=player_2, kind=YesNoKind.HOCHZEIT, allow_yes=False
    )

    assert result is False
    assert captured["title"] == prompt_ask_for_hochzeit(player_2.player_name)
    assert captured["options"] == [("No", False)]


def test_ask_game_mode_without_quitting_lists_options_only(
    renderer, player_2, monkeypatch
):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return Sauspiel

    monkeypatch.setattr(renderer, "_request", fake_request)

    options = {"1": Sauspiel, "2": Wenz}
    result = renderer.ask_game_mode(player=player_2, options=options, quitting_possible=False)

    assert result is Sauspiel
    assert captured["kind"] == "game_mode"
    assert captured["player_name"] == player_2.player_name
    assert captured["title"] == f"{player_2.player_name}: Which game do you want to choose?"
    assert captured["options"] == [("Sauspiel", Sauspiel), ("Wenz", Wenz)]


def test_ask_game_mode_with_quitting_appends_skip_option(renderer, player_2, monkeypatch):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return None

    monkeypatch.setattr(renderer, "_request", fake_request)

    options = {"1": Sauspiel}
    result = renderer.ask_game_mode(player=player_2, options=options, quitting_possible=True)

    assert result is None
    assert captured["options"] == [("Sauspiel", Sauspiel), ("Skip", None)]


def test_ask_color_sau_kind_uses_sau_wording(renderer, player_2, monkeypatch):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return Color.EICHEL

    monkeypatch.setattr(renderer, "_request", fake_request)

    options = {"1": Color.EICHEL, "2": Color.GRUEN}
    result = renderer.ask_color(player=player_2, options=options, kind=ColorChoiceKind.SAU)

    assert result == Color.EICHEL
    assert captured["kind"] == "color"
    assert captured["title"] == f"{player_2.player_name}: Which Sau color do you want to play?"
    assert captured["options"] == [("Eichel", Color.EICHEL), ("Grün", Color.GRUEN)]


def test_ask_color_trump_kind_uses_trump_wording(renderer, player_2, monkeypatch):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return Color.HERZ

    monkeypatch.setattr(renderer, "_request", fake_request)

    options = {"1": Color.HERZ}
    result = renderer.ask_color(player=player_2, options=options, kind=ColorChoiceKind.TRUMP)

    assert result == Color.HERZ
    assert captured["title"] == f"{player_2.player_name}: Which trump color do you want to play?"


def test_ask_card_to_play_uses_play_title_and_copies_legal_mask(renderer, player_2, monkeypatch):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return 0

    monkeypatch.setattr(renderer, "_request", fake_request)

    legal_mask = [True, False, True]
    result = renderer.ask_card(player=player_2, player_cards=[], legal_mask=legal_mask)

    assert result == 0
    assert captured["kind"] == "card"
    assert captured["title"] == "Choose a card to play"
    assert captured["legal_mask"] == legal_mask
    assert captured["legal_mask"] is not legal_mask
    assert captured["is_swap"] is False


def test_ask_card_to_swap_uses_swap_title(renderer, player_2, monkeypatch):
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return 1

    monkeypatch.setattr(renderer, "_request", fake_request)

    result = renderer.ask_card(
        player=player_2, player_cards=[], legal_mask=[True], is_swap=True
    )

    assert result == 1
    assert captured["title"] == "Choose a card to swap"
    assert captured["is_swap"] is True


# ---------------------------------------------------------------------------
# _request / _submit threading round trip
# ---------------------------------------------------------------------------


def test_request_submit_round_trip_unblocks_ask_yes_no(renderer, player_2):
    result_holder: dict = {}

    def ask():
        result_holder["value"] = renderer.ask_yes_no(player=player_2, kind=YesNoKind.RAMSCH)

    thread = threading.Thread(target=ask)
    thread.start()

    deadline = time.time() + 2
    while renderer.state.pending is None and time.time() < deadline:
        time.sleep(0.01)

    assert renderer.state.pending is not None
    assert renderer.state.pending.kind == "yes_no"
    assert renderer.state.pending.title == prompt_ask_for_ramsch(player_2.player_name)

    renderer._submit(True)
    thread.join(timeout=2)

    assert not thread.is_alive()
    assert result_holder["value"] is True
    assert renderer.state.pending is None


# ---------------------------------------------------------------------------
# wrap_text
# ---------------------------------------------------------------------------


def test_wrap_text_returns_single_line_when_it_fits(renderer):
    lines = wrap_text("Short text", renderer.fonts.heading, 400)

    assert lines == ["Short text"]


def test_wrap_text_wraps_long_text_into_multiple_lines(renderer):
    text = "one two three four five six seven eight"
    max_width = renderer.fonts.heading.size("one two three")[0]

    lines = wrap_text(text, renderer.fonts.heading, max_width)

    assert len(lines) > 1
    assert " ".join(lines) == text
    for line in lines:
        assert renderer.fonts.heading.size(line)[0] <= max_width


def test_wrap_text_empty_string_returns_single_empty_line(renderer):
    lines = wrap_text("", renderer.fonts.heading, 100)

    assert lines == [""]


def test_render_hochzeit_partner_search_shows_pending_lamps_for_bot_candidates(
    renderer, players
):
    # players[0] is the human chooser; the three bots are the candidates.
    renderer.render_hochzeit_partner_search(candidates=players[1:])

    assert renderer.state.game_choice_lamps == {
        c.LEFT: "pending",
        c.TOP: "pending",
        c.RIGHT: "pending",
    }


def test_render_hochzeit_partner_search_excludes_the_bot_chooser(renderer, players):
    # players[1] (seat LEFT) chose the Hochzeit - only the other three are
    # candidates, including the human, who gets no lamp.
    candidates = [players[2], players[3], players[0]]

    renderer.render_hochzeit_partner_search(candidates=candidates)

    assert renderer.state.game_choice_lamps == {c.TOP: "pending", c.RIGHT: "pending"}


def test_render_hochzeit_partner_decision_sets_lamp_and_announces(
    renderer, players, player_2
):
    renderer.render_hochzeit_partner_search(candidates=players[1:])
    calls = []
    renderer._announce_choice = lambda *args, **kwargs: calls.append((args, kwargs))

    renderer.render_hochzeit_partner_decision(player=players[1], accepts=False)
    renderer.render_hochzeit_partner_decision(player=players[2], accepts=True)

    assert renderer.state.game_choice_lamps[c.LEFT] == "no"
    assert renderer.state.game_choice_lamps[c.TOP] == "yes"
    assert calls == [
        (("Testplayer 2 does not want to partner the Hochzeit.",), {}),
        (("Testplayer 3 partners the Hochzeit!",), {}),
    ]


def test_render_hochzeit_card_swap_animates_between_the_partner_seats(
    renderer, players, monkeypatch
):
    snapshots = []
    monkeypatch.setattr(
        "system.gui.renderer.time.sleep",
        lambda *_args: snapshots.append(renderer.state.swap_animation),
    )

    renderer.render_hochzeit_card_swap(chooser=players[0], partner=players[2])

    assert len(snapshots) == 1
    assert snapshots[0] is not None
    assert snapshots[0].seat_a == c.BOTTOM
    assert snapshots[0].seat_b == c.TOP
    assert renderer.state.swap_animation is None


def test_draw_swap_animation_does_not_crash_while_active(renderer):
    renderer.state.swap_animation = SwapAnimation(
        seat_a=c.BOTTOM, seat_b=c.TOP, start_time=time.time(), duration=0.9
    )

    renderer.table_view.draw(mouse_pos=(0, 0))
