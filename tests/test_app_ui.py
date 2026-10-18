"""Smoke tests that drive the real Tk window.

They need a display. CI runs them under ``xvfb-run``; elsewhere they are
skipped when no display is available.
"""

import tkinter as tk

import pytest

import pomodoro98.app as app_module
from pomodoro98.timer import TimerModel

FOCUS = 60
REST = 30


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def played(monkeypatch):
    """Record sounds instead of playing them."""
    calls = []
    monkeypatch.setattr(app_module.SoundPlayer, "play_async", lambda self, path: calls.append(path))
    return calls


@pytest.fixture
def app(monkeypatch, clock, played):
    monkeypatch.setattr(app_module.TrayIcon, "start", lambda self: None)
    try:
        window = app_module.Pomodoro98()
    except tk.TclError as exc:
        pytest.skip(f"no display available: {exc}")
    window.withdraw()
    window.timer = TimerModel(FOCUS, REST, clock=clock)
    window._last_view = None
    window._render()
    yield window
    if not window._closing:
        window.shutdown()


def advance(app, clock, seconds):
    clock.now += seconds
    app._tick()
    app.update_idletasks()


def status(app):
    return app.title(), app.mode_label.cget("text"), app.start_btn.cget("text")


def clock_text(app):
    return app.clock_label.cget("text")


def test_initial_window(app):
    assert status(app) == ("Pomodoro98 [Stopped]", "Mode: Stopped", "Start")
    assert clock_text(app) == "01:00"


def test_start_pause_resume_reset(app, clock, played):
    app.start_btn.invoke()
    assert status(app) == ("Pomodoro98 [Focus]", "Mode: Focus", "Pause")

    advance(app, clock, 15)
    assert clock_text(app) == "00:45"

    app.start_btn.invoke()
    assert status(app) == ("Pomodoro98 [Paused]", "Mode: Focus — Paused", "Start")
    clock.now += 100
    app.update_idletasks()
    assert clock_text(app) == "00:45"

    app.start_btn.invoke()
    assert status(app) == ("Pomodoro98 [Focus]", "Mode: Focus", "Pause")

    app.reset_btn.invoke()
    assert status(app) == ("Pomodoro98 [Stopped]", "Mode: Stopped", "Start")
    assert clock_text(app) == "01:00"
    assert played == [app_module.SOUND_CLICK] * 4


def test_full_cycle(app, clock, played):
    app.start_btn.invoke()
    advance(app, clock, FOCUS)
    assert status(app) == ("Pomodoro98 [Rest]", "Mode: Rest", "Pause")
    assert clock_text(app) == "00:30"
    assert played[-1] == app_module.SOUND_FOCUS_END

    advance(app, clock, REST)
    assert status(app) == ("Pomodoro98 [Stopped]", "Mode: Cycle Complete (Stopped)", "Start")
    assert clock_text(app) == "00:00"
    assert played[-1] == app_module.SOUND_REST_END

    app.start_btn.invoke()
    assert status(app) == ("Pomodoro98 [Focus]", "Mode: Focus", "Pause")
    assert clock_text(app) == "01:00"


def test_progress_bar_tracks_elapsed_time(app, clock):
    def bar():
        x1, _, x2, _ = app.canvas.coords(app.bar)
        return (x2 - x1) / (app.prog_width - 4), app.canvas.itemcget(app.bar, "fill")

    assert bar() == (0.0, app_module.BAR_NORMAL)
    app.start_btn.invoke()
    advance(app, clock, FOCUS / 2)
    width, color = bar()
    assert width == pytest.approx(0.5, abs=0.01)
    assert color == app_module.BAR_NORMAL

    advance(app, clock, FOCUS / 2)
    assert bar()[1] == app_module.BAR_ALERT


def test_window_fits_longest_status(app):
    app.mode_label.config(text=app_module.CYCLE_COMPLETE_LABEL)
    app.update_idletasks()
    assert app.mode_label.winfo_reqwidth() < app.prog_width


def test_close_shuts_down_cleanly(app):
    app.start_btn.invoke()
    app.shutdown()
    assert app._closing
    assert not app.timer.running
    with pytest.raises(tk.TclError):
        app.winfo_exists()
