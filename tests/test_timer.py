"""Unit tests for the Tk-independent timer state machine."""

import pytest

from pomodoro98.timer import Event, Mode, TimerModel, default_clock

FOCUS = 25 * 60
REST = 5 * 60


class FakeClock:
    def __init__(self, start=1000.0):
        self.now = start

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def timer(clock):
    return TimerModel(FOCUS, REST, clock=clock)


def test_new_timer_is_stopped_with_full_focus_time(timer):
    assert timer.mode is Mode.STOPPED
    assert not timer.running
    assert not timer.completed
    assert timer.remaining == FOCUS
    assert timer.total_seconds == FOCUS
    assert timer.progress == 0.0


def test_start_enters_focus_and_counts_down(timer, clock):
    timer.start()
    assert timer.mode is Mode.FOCUS
    assert timer.running
    clock.advance(10)
    assert timer.remaining == FOCUS - 10
    assert timer.progress == pytest.approx(10 / FOCUS)


def test_remaining_rounds_up_partial_seconds(timer, clock):
    timer.start()
    clock.advance(0.4)
    assert timer.remaining == FOCUS
    clock.advance(0.6)
    assert timer.remaining == FOCUS - 1


def test_start_while_running_is_a_no_op(timer, clock):
    timer.start()
    clock.advance(5)
    timer.start()
    assert timer.remaining == FOCUS - 5


def test_pause_keeps_remaining_time(timer, clock):
    timer.start()
    clock.advance(60)
    timer.pause()
    assert not timer.running
    assert timer.mode is Mode.FOCUS
    clock.advance(3600)
    assert timer.remaining == FOCUS - 60
    assert timer.tick() == []


def test_pause_when_not_running_is_a_no_op(timer):
    timer.pause()
    assert timer.mode is Mode.STOPPED
    assert timer.remaining == FOCUS


def test_resume_continues_from_paused_time(timer, clock):
    timer.start()
    clock.advance(60)
    timer.pause()
    clock.advance(500)
    timer.start()
    assert timer.mode is Mode.FOCUS
    clock.advance(30)
    assert timer.remaining == FOCUS - 90


def test_toggle_starts_and_pauses(timer, clock):
    timer.toggle()
    assert timer.running
    clock.advance(5)
    timer.toggle()
    assert not timer.running
    assert timer.remaining == FOCUS - 5


def test_reset_restores_fresh_focus_timer(timer, clock):
    timer.start()
    clock.advance(FOCUS)
    timer.tick()
    timer.reset()
    assert timer.mode is Mode.STOPPED
    assert not timer.running
    assert not timer.completed
    assert timer.remaining == FOCUS
    assert timer.total_seconds == FOCUS


def test_tick_before_deadline_returns_no_events(timer, clock):
    timer.start()
    clock.advance(FOCUS - 1)
    assert timer.tick() == []
    assert timer.mode is Mode.FOCUS


def test_tick_when_stopped_returns_no_events(timer):
    assert timer.tick() == []


def test_focus_end_switches_to_rest(timer, clock):
    timer.start()
    clock.advance(FOCUS)
    assert timer.tick() == [Event.FOCUS_END]
    assert timer.mode is Mode.REST
    assert timer.running
    assert timer.total_seconds == REST
    assert timer.remaining == REST
    assert timer.progress == 0.0


def test_rest_end_completes_the_cycle(timer, clock):
    timer.start()
    clock.advance(FOCUS)
    timer.tick()
    clock.advance(REST)
    assert timer.tick() == [Event.CYCLE_COMPLETE]
    assert timer.mode is Mode.STOPPED
    assert not timer.running
    assert timer.completed
    assert timer.remaining == 0
    assert timer.progress == 1.0


def test_start_after_cycle_complete_begins_new_focus(timer, clock):
    timer.start()
    clock.advance(FOCUS)
    timer.tick()
    clock.advance(REST)
    timer.tick()
    timer.start()
    assert timer.mode is Mode.FOCUS
    assert not timer.completed
    assert timer.remaining == FOCUS


def test_late_tick_does_not_drift(timer, clock):
    """A callback that fires late still reports time from the deadline."""
    timer.start()
    clock.advance(123.7)
    assert timer.remaining == FOCUS - 123


def test_suspend_through_focus_end_starts_rest_on_wake(timer, clock):
    timer.start()
    clock.advance(FOCUS + REST + 600)  # suspended past both periods
    assert timer.tick() == [Event.FOCUS_END]
    assert timer.mode is Mode.REST
    assert timer.remaining == REST
    assert timer.tick() == []


def test_paused_rest_resumes_in_rest(timer, clock):
    timer.start()
    clock.advance(FOCUS)
    timer.tick()
    clock.advance(60)
    timer.pause()
    timer.start()
    assert timer.mode is Mode.REST
    assert timer.remaining == REST - 60


def test_custom_durations():
    clock = FakeClock()
    timer = TimerModel(3, 2, clock=clock)
    timer.start()
    clock.advance(3)
    assert timer.tick() == [Event.FOCUS_END]
    clock.advance(2)
    assert timer.tick() == [Event.CYCLE_COMPLETE]


def test_default_clock_is_monotonic():
    first = default_clock()
    assert default_clock() >= first
