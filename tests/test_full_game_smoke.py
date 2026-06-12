"""End-to-end smoke tests: four bots play complete hands through the real
Schafkopf orchestration (dealing, game choosing, every game mode, scoring).

These catch crashes and money-accounting bugs that unit tests of single
collaborators can miss - especially with stateful pieces like the Sauspiel
validator's Davonlaufen tracking.
"""

import random
from unittest.mock import MagicMock

import pytest

from player_classes.Player import Bot
from schafkopf_classes.Schafkopf import Schafkopf


def _all_bot_schafkopf() -> Schafkopf:
    renderer = MagicMock()
    schafkopf = Schafkopf(
        renderer=renderer, base_price=10, call_price=20, alone_price=30
    )
    schafkopf.players = [
        Bot(
            bot_name=f"Bot {i + 1}",
            renderer=renderer,
            game_decision_validator=schafkopf.game_decision_validator,
        )
        for i in range(4)
    ]
    schafkopf.starter = schafkopf.players[0]
    return schafkopf


def _play_one_hand(schafkopf: Schafkopf) -> str | None:
    """One iteration of Schafkopf.main's while-loop, without the renderer
    round-trips. Returns the name of the played game mode, or None if the
    cards were thrown together."""

    schafkopf.prepare_players()
    schafkopf.prepare_cards()
    for player in schafkopf.players:
        if player.ask_want_choose_game(
            players_who_want_to_play_count=len(schafkopf.game_choosers)
        ):
            schafkopf.game_choosers.append(player)
    game = schafkopf.players_choose_game()
    if game is None:
        return None
    game.play_game()
    return game.name


@pytest.mark.parametrize("seed", range(40))
def test_full_bot_hands_complete_and_money_stays_zero_sum(seed):
    random.seed(seed)
    schafkopf = _all_bot_schafkopf()

    for _ in range(4):
        mode = _play_one_hand(schafkopf)
        assert sum(player.money for player in schafkopf.players) == 0
        if mode is not None and "Tout" not in mode:
            # Touts stop early when the chooser loses a trick; every other
            # played game must run all eight rounds.
            for player in schafkopf.players:
                assert player.player_cards == []
        schafkopf.starter = schafkopf.get_new_starter(
            prev_starter_index=schafkopf.players.index(schafkopf.starter)
        )


def test_full_bot_hands_cover_multiple_game_modes():
    played_modes: set[str | None] = set()
    for seed in range(40):
        random.seed(seed)
        schafkopf = _all_bot_schafkopf()
        played_modes.add(_play_one_hand(schafkopf))

    assert len(played_modes - {None}) >= 2
