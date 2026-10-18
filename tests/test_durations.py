"""Period overrides used for quick manual test cycles."""

import pytest

from pomodoro98.app import FOCUS_SECONDS_ENV, duration_from_env


def test_default_when_unset():
    assert duration_from_env(FOCUS_SECONDS_ENV, 1500, environ={}) == 1500


def test_positive_override_is_used():
    assert duration_from_env(FOCUS_SECONDS_ENV, 1500, environ={FOCUS_SECONDS_ENV: "60"}) == 60


@pytest.mark.parametrize("value", ["0", "-5", "abc", "1.5", ""])
def test_invalid_override_falls_back(value):
    assert duration_from_env(FOCUS_SECONDS_ENV, 1500, environ={FOCUS_SECONDS_ENV: value}) == 1500
