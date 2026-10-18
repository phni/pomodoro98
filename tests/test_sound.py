"""Sound playback falls back gracefully when backends are missing or fail."""

import subprocess
from pathlib import Path
from unittest import mock

import pytest

import pomodoro98.sound as sound

WAV = Path(sound.__file__).with_name("sounds") / "focus_end.wav"


class ImmediateThread:
    """Stand-in for threading.Thread that runs the target on start()."""

    def __init__(self, target, **kwargs):
        self._target = target

    def start(self):
        self._target()


@pytest.fixture(autouse=True)
def no_backends(monkeypatch):
    """Start every test with no optional backend and synchronous playback."""
    monkeypatch.setattr(sound, "_SA", None)
    monkeypatch.setattr(sound, "_PYG", None)
    monkeypatch.setattr(sound.threading, "Thread", ImmediateThread)


@pytest.fixture
def aplay(monkeypatch):
    run = mock.Mock(return_value=subprocess.CompletedProcess([], 0))
    monkeypatch.setattr(sound.subprocess, "run", run)
    return run


@pytest.fixture
def player():
    on_failure = mock.Mock()
    return sound.SoundPlayer(on_failure=on_failure), on_failure


def test_aplay_success_does_not_ring_bell(player, aplay):
    p, on_failure = player
    p.play_async(WAV)
    aplay.assert_called_once()
    assert aplay.call_args.args[0][:2] == ["aplay", "-q"]
    on_failure.assert_not_called()


def test_aplay_nonzero_exit_rings_bell(player, aplay):
    aplay.return_value = subprocess.CompletedProcess([], 1)
    p, on_failure = player
    p.play_async(WAV)
    on_failure.assert_called_once()


@pytest.mark.parametrize(
    "error", [FileNotFoundError("aplay"), subprocess.TimeoutExpired("aplay", 30)]
)
def test_aplay_missing_or_hung_rings_bell(player, aplay, error):
    aplay.side_effect = error
    p, on_failure = player
    p.play_async(WAV)
    on_failure.assert_called_once()


def test_missing_file_rings_bell_without_backends(player, aplay, tmp_path):
    p, on_failure = player
    p.play_async(tmp_path / "missing.wav")
    aplay.assert_not_called()
    on_failure.assert_called_once()


def test_simpleaudio_is_preferred(monkeypatch, player, aplay):
    sa = mock.Mock()
    monkeypatch.setattr(sound, "_SA", sa)
    p, on_failure = player
    p.play_async(WAV)
    sa.WaveObject.from_wave_file.return_value.play.assert_called_once()
    aplay.assert_not_called()
    on_failure.assert_not_called()


def test_simpleaudio_failure_falls_back_to_pygame(monkeypatch, player, aplay):
    sa = mock.Mock()
    sa.WaveObject.from_wave_file.side_effect = RuntimeError("bad device")
    pyg = mock.Mock()
    pyg.mixer.get_init.return_value = False
    monkeypatch.setattr(sound, "_SA", sa)
    monkeypatch.setattr(sound, "_PYG", pyg)
    p, on_failure = player
    p.play_async(WAV)
    pyg.mixer.init.assert_called_once()
    pyg.mixer.Sound.return_value.play.assert_called_once()
    aplay.assert_not_called()
    on_failure.assert_not_called()


def test_pygame_init_failure_falls_back_to_aplay(monkeypatch, player, aplay):
    pyg = mock.Mock()
    pyg.mixer.get_init.return_value = False
    pyg.mixer.init.side_effect = RuntimeError("no audio")
    monkeypatch.setattr(sound, "_PYG", pyg)
    p, on_failure = player
    p.play_async(WAV)
    aplay.assert_called_once()
    on_failure.assert_not_called()


def test_pygame_playback_failure_falls_back_to_aplay(monkeypatch, player, aplay):
    pyg = mock.Mock()
    pyg.mixer.Sound.side_effect = RuntimeError("bad file")
    monkeypatch.setattr(sound, "_PYG", pyg)
    p, on_failure = player
    p.play_async(WAV)
    aplay.assert_called_once()
    on_failure.assert_not_called()


def test_unexpected_error_still_rings_bell(monkeypatch, player):
    p, on_failure = player
    monkeypatch.setattr(p, "_play_backend", mock.Mock(side_effect=ValueError("boom")))
    p.play_async(WAV)
    on_failure.assert_called_once()


def test_disabled_player_plays_nothing(aplay):
    on_failure = mock.Mock()
    p = sound.SoundPlayer(on_failure=on_failure, enabled=False)
    p.play_async(WAV)
    aplay.assert_not_called()
    on_failure.assert_not_called()


def test_no_playback_after_shutdown(player, aplay):
    p, on_failure = player
    p.shutdown()
    p.play_async(WAV)
    aplay.assert_not_called()
    on_failure.assert_not_called()


def test_shutdown_quits_pygame_mixer(monkeypatch, player):
    pyg = mock.Mock()
    pyg.mixer.get_init.return_value = True
    monkeypatch.setattr(sound, "_PYG", pyg)
    p, _ = player
    p.shutdown()
    pyg.mixer.quit.assert_called_once()


def test_shutdown_survives_pygame_errors(monkeypatch, player):
    pyg = mock.Mock()
    pyg.mixer.get_init.side_effect = RuntimeError("broken")
    monkeypatch.setattr(sound, "_PYG", pyg)
    p, _ = player
    p.shutdown()  # must not raise
