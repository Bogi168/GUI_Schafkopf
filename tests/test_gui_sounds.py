import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from system.gui.sounds import SoundPlayer, _build_sound, _segment


@pytest.fixture(autouse=True, scope="module")
def _pygame_init():
    pygame.init()
    yield
    pygame.quit()


def test_segment_produces_expected_sample_count():
    samples = _segment(frequency=440.0, duration=0.05, sample_rate=44100, channels=2)

    assert len(samples) == int(44100 * 0.05) * 2


def test_build_sound_returns_none_when_mixer_not_initialized(monkeypatch):
    monkeypatch.setattr(pygame.mixer, "get_init", lambda: None)

    assert _build_sound([(440.0, 0.05)]) is None


def test_build_sound_returns_sound_when_mixer_initialized():
    sound = _build_sound([(440.0, 0.05)])

    assert isinstance(sound, pygame.mixer.Sound)


def test_sound_player_builds_card_and_trick_sounds():
    player = SoundPlayer()

    assert isinstance(player._card_played, pygame.mixer.Sound)
    assert isinstance(player._trick_won, pygame.mixer.Sound)


def test_sound_player_play_methods_do_not_raise():
    player = SoundPlayer()

    player.play_card_played()
    player.play_trick_won()


def test_sound_player_disabled_when_mixer_init_fails(monkeypatch):
    def _raise_pygame_error():
        raise pygame.error("no audio device")

    monkeypatch.setattr(pygame.mixer, "init", _raise_pygame_error)

    player = SoundPlayer()

    assert player._card_played is None
    assert player._trick_won is None
    player.play_card_played()
    player.play_trick_won()
