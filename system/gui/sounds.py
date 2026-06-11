"""Calm, understated sound effects for the pygame GUI.

Sounds are short sine tones synthesized at runtime (no audio assets), kept
quiet and brief so they read as a background detail rather than an alert.
If the mixer can't be initialized (e.g. no audio device available),
playback is silently disabled.
"""

from __future__ import annotations

import array
import math

import pygame

_VOLUME = 0.12
_ATTACK = 0.005
_DECAY_RATE = 5.0


def _segment(frequency: float, duration: float, sample_rate: int, channels: int) -> array.array:
    amplitude = int(32767 * _VOLUME)
    n_samples = int(sample_rate * duration)
    samples = array.array("h")
    for i in range(n_samples):
        t = i / sample_rate
        envelope = math.exp(-_DECAY_RATE * t / duration)
        if t < _ATTACK:
            envelope *= t / _ATTACK
        value = int(amplitude * envelope * math.sin(2 * math.pi * frequency * t))
        samples.extend([value] * channels)
    return samples


def _build_sound(segments: list[tuple[float, float]]) -> pygame.mixer.Sound | None:
    init = pygame.mixer.get_init()
    if init is None:
        return None
    sample_rate, sample_size, channels = init
    if abs(sample_size) != 16:
        return None
    samples = array.array("h")
    for frequency, duration in segments:
        samples.extend(_segment(frequency, duration, sample_rate, channels))
    return pygame.mixer.Sound(buffer=samples)


class SoundPlayer:
    """Plays short, quiet sound effects - or does nothing if audio is unavailable."""

    def __init__(self) -> None:
        self._card_played: pygame.mixer.Sound | None = None
        self._trick_won: pygame.mixer.Sound | None = None
        try:
            pygame.mixer.init()
        except pygame.error:
            return
        self._card_played = _build_sound([(294.0, 0.06)])
        self._trick_won = _build_sound([(523.25, 0.16), (659.25, 0.22)])

    def play_card_played(self) -> None:
        self._play(self._card_played)

    def play_trick_won(self) -> None:
        self._play(self._trick_won)

    @staticmethod
    def _play(sound: pygame.mixer.Sound | None) -> None:
        if sound is not None:
            sound.play()
