"""The tray icon never breaks the app when pystray is missing or fails."""

from unittest import mock

import pytest

import pomodoro98.tray as tray


class ImmediateThread:
    def __init__(self, target, **kwargs):
        self._target = target

    def start(self):
        self._target()


@pytest.fixture
def fake_pystray(monkeypatch):
    """Pretend pystray and Pillow are installed."""
    pystray = mock.Mock()
    monkeypatch.setattr(tray, "TRAY_OK", True)
    monkeypatch.setattr(tray, "pystray", pystray, raising=False)
    monkeypatch.setattr(tray, "_make_image", lambda color: ("image", color))
    monkeypatch.setattr(tray.threading, "Thread", ImmediateThread)
    return pystray


def test_without_pystray_every_call_is_a_no_op(monkeypatch):
    monkeypatch.setattr(tray, "TRAY_OK", False)
    icon = tray.TrayIcon("Pomodoro98", "Pomodoro98")
    icon.start()
    icon.update("focus", 1500)
    icon.stop()
    assert icon._icon is None


def test_start_runs_the_icon(fake_pystray):
    icon = tray.TrayIcon("Pomodoro98", "Pomodoro98")
    icon.start()
    fake_pystray.Icon.assert_called_once()
    fake_pystray.Icon.return_value.run.assert_called_once()


@pytest.mark.parametrize(
    ("mode", "color", "title"),
    [
        ("focus", (0, 160, 0, 255), "Focus: 24:59 remaining"),
        ("rest", (192, 0, 0, 255), "Rest: 24:59 remaining"),
        ("stopped", (128, 128, 128, 255), "Stopped: 24:59 remaining"),
    ],
)
def test_update_shows_mode_and_time(fake_pystray, mode, color, title):
    icon = tray.TrayIcon("Pomodoro98", "Pomodoro98")
    icon.start()
    icon.update(mode, 1499)
    native = fake_pystray.Icon.return_value
    assert native.icon == ("image", color)
    assert native.title == title


def test_start_failure_leaves_tray_disabled(fake_pystray):
    fake_pystray.Icon.side_effect = RuntimeError("no StatusNotifier host")
    icon = tray.TrayIcon("Pomodoro98", "Pomodoro98")
    icon.start()  # must not raise
    assert icon._icon is None
    icon.update("focus", 60)  # no-op, must not raise


def test_update_failure_is_swallowed(fake_pystray, monkeypatch):
    icon = tray.TrayIcon("Pomodoro98", "Pomodoro98")
    icon.start()
    monkeypatch.setattr(tray, "_make_image", mock.Mock(side_effect=OSError("render")))
    icon.update("rest", 60)  # must not raise


def test_stop_clears_icon_even_when_backend_fails(fake_pystray):
    fake_pystray.Icon.return_value.stop.side_effect = RuntimeError("already gone")
    icon = tray.TrayIcon("Pomodoro98", "Pomodoro98")
    icon.start()
    icon.stop()  # must not raise
    assert icon._icon is None


def test_make_image_draws_a_24px_icon(monkeypatch):
    image_module = pytest.importorskip("PIL.Image")
    draw_module = pytest.importorskip("PIL.ImageDraw")
    monkeypatch.setattr(tray, "Image", image_module, raising=False)
    monkeypatch.setattr(tray, "ImageDraw", draw_module, raising=False)
    image = tray._make_image((0, 160, 0, 255))
    assert image.size == (24, 24)
    assert image.getpixel((12, 12)) == (0, 160, 0, 255)
