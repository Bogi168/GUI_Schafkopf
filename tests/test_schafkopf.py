from unittest.mock import MagicMock

import pytest

from player_classes.Player import Bot, Player
from schafkopf_classes.Schafkopf import Schafkopf
from game_classes.Game import Game
from game_classes.game_modes.Sauspiel import Sauspiel
from game_classes.game_modes.Wenz import Wenz
from game_classes.game_modes.SoloTout import SoloTout
from game_classes.game_modes.Ramsch import Ramsch
from system.custom_exceptions import (
    GameNotPlayableError,
    PlayerIsNotInPlayersListError,
)
from system.text import words_of_thanks, no_game_phrase


@pytest.fixture
def schafkopf() -> Schafkopf:
    renderer = MagicMock()
    renderer.ask_yes_no.return_value = False
    # The settings step keeps whatever prices Schafkopf was built with.
    renderer.ask_prices.side_effect = (
        lambda base_price, call_price, alone_price: (base_price, call_price, alone_price)
    )
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


# ---------------------------------------------------------------------------
# sort_players
# ---------------------------------------------------------------------------


def test_sort_players_rotates_so_starter_is_first(schafkopf):
    starter, bot1, bot2, bot3 = schafkopf.players

    result = Schafkopf.sort_players(starter=bot2, players=schafkopf.players)

    assert result == [bot2, bot3, starter, bot1]


def test_sort_players_with_starter_already_first_is_unchanged(schafkopf):
    starter, bot1, bot2, bot3 = schafkopf.players

    result = Schafkopf.sort_players(starter=starter, players=schafkopf.players)

    assert result == [starter, bot1, bot2, bot3]


def test_sort_players_raises_if_starter_not_in_players(schafkopf):
    outsider = Bot(
        bot_name="Outsider",
        renderer=schafkopf.renderer,
        game_decision_validator=schafkopf.game_decision_validator,
    )

    with pytest.raises(
        PlayerIsNotInPlayersListError,
        match="The starting player is not in players list",
    ):
        Schafkopf.sort_players(starter=outsider, players=schafkopf.players)


# ---------------------------------------------------------------------------
# prepare_players
# ---------------------------------------------------------------------------


def test_prepare_players_rotates_players_and_clears_choosers(schafkopf):
    starter, bot1, bot2, bot3 = schafkopf.players
    schafkopf.starter = bot1
    schafkopf.game_choosers = [starter, bot2]

    schafkopf.prepare_players()

    assert schafkopf.players == [bot1, bot2, bot3, starter]
    assert schafkopf.game_choosers == []


# ---------------------------------------------------------------------------
# get_hochzeit_partner
# ---------------------------------------------------------------------------


def test_get_hochzeit_partner_first_candidate_says_yes(schafkopf, monkeypatch):
    starter, bot1, bot2, bot3 = schafkopf.players

    monkeypatch.setattr(bot1, "ask_for_hochzeit", lambda: True)
    monkeypatch.setattr(bot2, "ask_for_hochzeit", lambda: False)
    monkeypatch.setattr(bot3, "ask_for_hochzeit", lambda: False)

    result = schafkopf.get_hochzeit_partner(game_chooser=starter)

    assert result is bot1


def test_get_hochzeit_partner_nobody_says_yes(schafkopf, monkeypatch):
    starter, bot1, bot2, bot3 = schafkopf.players

    monkeypatch.setattr(bot1, "ask_for_hochzeit", lambda: False)
    monkeypatch.setattr(bot2, "ask_for_hochzeit", lambda: False)
    monkeypatch.setattr(bot3, "ask_for_hochzeit", lambda: False)

    result = schafkopf.get_hochzeit_partner(game_chooser=starter)

    assert result is None


def test_get_hochzeit_partner_second_candidate_says_yes_stops_early(
    schafkopf, monkeypatch
):
    starter, bot1, bot2, bot3 = schafkopf.players

    bot1_mock = MagicMock(return_value=False)
    bot2_mock = MagicMock(return_value=True)
    bot3_mock = MagicMock(return_value=False)
    monkeypatch.setattr(bot1, "ask_for_hochzeit", bot1_mock)
    monkeypatch.setattr(bot2, "ask_for_hochzeit", bot2_mock)
    monkeypatch.setattr(bot3, "ask_for_hochzeit", bot3_mock)

    result = schafkopf.get_hochzeit_partner(game_chooser=starter)

    assert result is bot2
    assert bot1_mock.call_count == 1
    assert bot2_mock.call_count == 1
    assert bot3_mock.call_count == 0


# ---------------------------------------------------------------------------
# get_game
# ---------------------------------------------------------------------------


def test_get_game_returns_game_instance_on_success(schafkopf):
    schafkopf.prepare_cards()

    game = schafkopf.get_game(game_mode=Ramsch, chooser=None)

    assert isinstance(game, Ramsch)


def test_get_game_returns_none_when_gather_kwargs_raises(schafkopf, monkeypatch):
    monkeypatch.setattr(
        Ramsch,
        "gather_kwargs",
        classmethod(
            lambda cls, chooser, schafkopf: (_ for _ in ()).throw(
                GameNotPlayableError("not playable")
            )
        ),
    )

    game = schafkopf.get_game(game_mode=Ramsch, chooser=None)

    assert game is None


# ---------------------------------------------------------------------------
# get_new_starter
# ---------------------------------------------------------------------------


def test_get_new_starter_returns_next_player(schafkopf):
    starter, bot1, bot2, bot3 = schafkopf.players

    result = schafkopf.get_new_starter(prev_starter_index=0)

    assert result is bot1


def test_get_new_starter_wraps_around_when_prev_was_last(schafkopf):
    starter, bot1, bot2, bot3 = schafkopf.players

    result = schafkopf.get_new_starter(prev_starter_index=3)

    assert result is starter


# ---------------------------------------------------------------------------
# players_choose_game
# ---------------------------------------------------------------------------


def test_players_choose_game_no_choosers_plays_ramsch_when_accepted(
    schafkopf, monkeypatch
):
    starter, bot1, bot2, bot3 = schafkopf.players
    schafkopf.game_choosers = []

    monkeypatch.setattr(bot3, "ask_for_ramsch", lambda: True)
    sentinel_game = MagicMock()
    get_game_mock = MagicMock(return_value=sentinel_game)
    monkeypatch.setattr(schafkopf, "get_game", get_game_mock)

    result = schafkopf.players_choose_game()

    assert result is sentinel_game
    get_game_mock.assert_called_once_with(game_mode=Ramsch, chooser=None)


def test_players_choose_game_no_choosers_returns_none_when_declined(
    schafkopf, monkeypatch
):
    starter, bot1, bot2, bot3 = schafkopf.players
    schafkopf.game_choosers = []

    monkeypatch.setattr(bot3, "ask_for_ramsch", lambda: False)
    get_game_mock = MagicMock()
    monkeypatch.setattr(schafkopf, "get_game", get_game_mock)

    result = schafkopf.players_choose_game()

    assert result is None
    get_game_mock.assert_not_called()


def test_players_choose_game_single_chooser_picks_sauspiel(schafkopf, monkeypatch):
    starter, bot1, bot2, bot3 = schafkopf.players
    schafkopf.game_choosers = [bot1]

    monkeypatch.setattr(
        bot1, "choose_game_mode", lambda **kwargs: Sauspiel
    )
    sentinel_game = MagicMock()
    get_game_mock = MagicMock(return_value=sentinel_game)
    monkeypatch.setattr(schafkopf, "get_game", get_game_mock)

    result = schafkopf.players_choose_game()

    assert result is sentinel_game
    get_game_mock.assert_called_once_with(game_mode=Sauspiel, chooser=bot1)


def test_players_choose_game_second_chooser_overrides_with_higher_rank(
    schafkopf, monkeypatch
):
    starter, bot1, bot2, bot3 = schafkopf.players
    schafkopf.game_choosers = [bot1, bot2]

    bot1_mock = MagicMock(return_value=Sauspiel)
    bot2_mock = MagicMock(return_value=Wenz)
    monkeypatch.setattr(bot1, "choose_game_mode", bot1_mock)
    monkeypatch.setattr(bot2, "choose_game_mode", bot2_mock)

    sentinel_game = MagicMock()
    get_game_mock = MagicMock(return_value=sentinel_game)
    monkeypatch.setattr(schafkopf, "get_game", get_game_mock)

    result = schafkopf.players_choose_game()

    assert result is sentinel_game
    get_game_mock.assert_called_once_with(game_mode=Wenz, chooser=bot2)

    # First chooser cannot quit since there is no previous pick yet.
    bot1_kwargs = bot1_mock.call_args.kwargs
    assert bot1_kwargs["prev_game_mode"] is None
    assert bot1_kwargs["quitting_possible"] is False

    # Second chooser cannot quit since the current pick (Sauspiel) is not
    # ranked above Sauspiel, so quitting_possible=False.
    bot2_kwargs = bot2_mock.call_args.kwargs
    assert bot2_kwargs["prev_game_mode"] is Sauspiel
    assert bot2_kwargs["quitting_possible"] is False


def test_players_choose_game_second_chooser_passes_keeps_previous(
    schafkopf, monkeypatch
):
    starter, bot1, bot2, bot3 = schafkopf.players
    schafkopf.game_choosers = [bot1, bot2]

    bot1_mock = MagicMock(return_value=Wenz)
    bot2_mock = MagicMock(return_value=None)
    monkeypatch.setattr(bot1, "choose_game_mode", bot1_mock)
    monkeypatch.setattr(bot2, "choose_game_mode", bot2_mock)

    sentinel_game = MagicMock()
    get_game_mock = MagicMock(return_value=sentinel_game)
    monkeypatch.setattr(schafkopf, "get_game", get_game_mock)

    result = schafkopf.players_choose_game()

    assert result is sentinel_game
    get_game_mock.assert_called_once_with(game_mode=Wenz, chooser=bot1)

    # Second chooser may quit since the current pick (Wenz) outranks
    # Sauspiel; passing keeps the first chooser's pick as game_chooser.
    bot2_kwargs = bot2_mock.call_args.kwargs
    assert bot2_kwargs["prev_game_mode"] is Wenz
    assert bot2_kwargs["quitting_possible"] is True


def test_players_choose_game_solo_tout_breaks_loop_immediately(schafkopf, monkeypatch):
    starter, bot1, bot2, bot3 = schafkopf.players
    schafkopf.game_choosers = [bot1, bot2, bot3]

    bot1_mock = MagicMock(return_value=SoloTout)
    bot2_mock = MagicMock(return_value=Sauspiel)
    bot3_mock = MagicMock(return_value=Sauspiel)
    monkeypatch.setattr(bot1, "choose_game_mode", bot1_mock)
    monkeypatch.setattr(bot2, "choose_game_mode", bot2_mock)
    monkeypatch.setattr(bot3, "choose_game_mode", bot3_mock)

    sentinel_game = MagicMock()
    get_game_mock = MagicMock(return_value=sentinel_game)
    monkeypatch.setattr(schafkopf, "get_game", get_game_mock)

    result = schafkopf.players_choose_game()

    assert result is sentinel_game
    get_game_mock.assert_called_once_with(game_mode=SoloTout, chooser=bot1)
    bot1_mock.assert_called_once()
    bot2_mock.assert_not_called()
    bot3_mock.assert_not_called()


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def test_main_single_iteration_with_no_game(schafkopf, monkeypatch):
    renderer = schafkopf.renderer
    renderer.ask_play_again.return_value = False
    starter = schafkopf.players[0]

    monkeypatch.setattr(schafkopf, "_create_players", lambda: schafkopf.players)
    monkeypatch.setattr(schafkopf, "prepare_players", lambda: None)
    monkeypatch.setattr(schafkopf, "prepare_cards", lambda: None)
    players_choose_game_mock = MagicMock(return_value=None)
    monkeypatch.setattr(schafkopf, "players_choose_game", players_choose_game_mock)
    monkeypatch.setattr(schafkopf, "get_new_starter", lambda prev_starter_index: starter)

    # ask_want_choose_game is called for every player; default to not wanting to play.
    for player in schafkopf.players:
        monkeypatch.setattr(player, "ask_want_choose_game", lambda **kwargs: False)

    schafkopf.main()

    players_choose_game_mock.assert_called_once()
    renderer.render.assert_any_call(message=no_game_phrase)
    renderer.render_farewell.assert_called_once_with(message=words_of_thanks)


def test_main_single_iteration_with_game_plays_it(schafkopf, monkeypatch):
    renderer = schafkopf.renderer
    renderer.ask_play_again.return_value = False
    starter = schafkopf.players[0]

    monkeypatch.setattr(schafkopf, "_create_players", lambda: schafkopf.players)
    monkeypatch.setattr(schafkopf, "prepare_players", lambda: None)
    monkeypatch.setattr(schafkopf, "prepare_cards", lambda: None)

    mock_game = MagicMock(spec=Game)
    mock_game.name = "Sauspiel"
    mock_game.game_chooser = starter
    mock_game.display_detail.return_value = None
    mock_game.display_detail_color.return_value = None

    players_choose_game_mock = MagicMock(return_value=mock_game)
    monkeypatch.setattr(schafkopf, "players_choose_game", players_choose_game_mock)
    monkeypatch.setattr(schafkopf, "get_new_starter", lambda prev_starter_index: starter)

    for player in schafkopf.players:
        monkeypatch.setattr(player, "ask_want_choose_game", lambda **kwargs: False)

    schafkopf.main()

    players_choose_game_mock.assert_called_once()
    mock_game.play_game.assert_called_once()
    renderer.render_game_mode.assert_any_call(
        game_mode_name="Sauspiel",
        chooser=starter,
        detail=None,
        detail_color=None,
    )
    renderer.render_game_mode_announcement.assert_called_once_with(
        game_mode_name="Sauspiel",
        chooser=starter,
        detail=None,
        detail_color=None,
    )
    renderer.render_farewell.assert_called_once_with(message=words_of_thanks)


def test_main_applies_prices_from_renderer(schafkopf, monkeypatch):
    renderer = schafkopf.renderer
    renderer.ask_play_again.return_value = False
    renderer.ask_prices.side_effect = None
    renderer.ask_prices.return_value = (7, 14, 21)
    starter = schafkopf.players[0]

    monkeypatch.setattr(schafkopf, "_create_players", lambda: schafkopf.players)
    monkeypatch.setattr(schafkopf, "prepare_players", lambda: None)
    monkeypatch.setattr(schafkopf, "prepare_cards", lambda: None)
    monkeypatch.setattr(schafkopf, "players_choose_game", lambda: None)
    monkeypatch.setattr(schafkopf, "get_new_starter", lambda prev_starter_index: starter)
    for player in schafkopf.players:
        monkeypatch.setattr(player, "ask_want_choose_game", lambda **kwargs: False)

    schafkopf.main()

    assert (schafkopf.base_price, schafkopf.call_price, schafkopf.alone_price) == (7, 14, 21)


def test_get_hochzeit_partner_renders_search_and_decisions(schafkopf, monkeypatch):
    starter, bot1, bot2, bot3 = schafkopf.players

    monkeypatch.setattr(bot1, "ask_for_hochzeit", lambda: False)
    monkeypatch.setattr(bot2, "ask_for_hochzeit", lambda: True)
    monkeypatch.setattr(bot3, "ask_for_hochzeit", lambda: False)

    schafkopf.get_hochzeit_partner(game_chooser=starter)

    schafkopf.renderer.render_hochzeit_partner_search.assert_called_once_with(
        candidates=[bot1, bot2, bot3]
    )
    decision_calls = schafkopf.renderer.render_hochzeit_partner_decision.call_args_list
    # bot3 is never asked - bot2 already accepted.
    assert [(call.kwargs["player"], call.kwargs["accepts"]) for call in decision_calls] == [
        (bot1, False),
        (bot2, True),
    ]
