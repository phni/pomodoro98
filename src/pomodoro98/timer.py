"""Pomodoro timer state machine, independent of Tk.

The timer counts down to a deadline on a monotonic clock instead of
decrementing once per UI callback, so late or skipped callbacks never make it
drift. On Linux the default clock is ``CLOCK_BOOTTIME``, which keeps counting
while the machine is suspended: a focus session that ends during suspend is
over when the machine wakes, and the rest period starts from that moment.
"""

import enum
import math
import time


class Mode(str, enum.Enum):
    STOPPED = "stopped"
    FOCUS = "focus"
    REST = "rest"


class Event(enum.Enum):
    FOCUS_END = "focus_end"
    CYCLE_COMPLETE = "cycle_complete"


def default_clock():
    if hasattr(time, "CLOCK_BOOTTIME"):
        return time.clock_gettime(time.CLOCK_BOOTTIME)
    return time.monotonic()


class TimerModel:
    """One focus period followed by one rest period, then stop."""

    def __init__(self, focus_seconds, rest_seconds, clock=default_clock):
        self.focus_seconds = focus_seconds
        self.rest_seconds = rest_seconds
        self._clock = clock
        self.reset()

    # ---------- Commands ----------
    def start(self):
        """Start a fresh cycle when stopped, or resume a paused one."""
        if self.running:
            return
        if self.mode is Mode.STOPPED:
            self._enter(Mode.FOCUS)
        self.running = True
        self._deadline = self._clock() + self._remaining

    def pause(self):
        """Pause without losing the remaining time."""
        if not self.running:
            return
        self._remaining = max(0.0, self._deadline - self._clock())
        self._deadline = None
        self.running = False

    def toggle(self):
        if self.running:
            self.pause()
        else:
            self.start()

    def reset(self):
        """Stop and restore a fresh focus timer."""
        self.mode = Mode.STOPPED
        self.running = False
        self.completed = False
        self.total_seconds = self.focus_seconds
        self._remaining = float(self.focus_seconds)
        self._deadline = None

    def tick(self):
        """Advance the state machine; return the events that just happened."""
        if not self.running or self._clock() < self._deadline:
            return []
        if self.mode is Mode.FOCUS:
            self._enter(Mode.REST)
            self._deadline = self._clock() + self._remaining
            return [Event.FOCUS_END]
        self.mode = Mode.STOPPED
        self.running = False
        self.completed = True
        self._remaining = 0.0
        self._deadline = None
        return [Event.CYCLE_COMPLETE]

    # ---------- Queries ----------
    @property
    def remaining(self):
        """Whole seconds left, rounded up so 24:59.5 still shows 25:00."""
        seconds = max(0.0, self._deadline - self._clock()) if self.running else self._remaining
        return min(self.total_seconds, math.ceil(seconds))

    @property
    def progress(self):
        """Fraction of the current period elapsed, in whole seconds."""
        if self.completed:
            return 1.0
        return (self.total_seconds - self.remaining) / max(1, self.total_seconds)

    # ---------- Internals ----------
    def _enter(self, mode):
        self.mode = mode
        self.completed = False
        self.total_seconds = self.focus_seconds if mode is Mode.FOCUS else self.rest_seconds
        self._remaining = float(self.total_seconds)
