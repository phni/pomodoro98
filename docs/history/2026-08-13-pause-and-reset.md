# Pause and reset controls

Date: 2026-08-13

## Changes

- Turn the Start control into a Start/Pause toggle.
- Show `Pause` while the timer is running and restore `Start` while paused.
- Preserve the active focus/rest mode and remaining time while paused.
- Schedule the first tick one second after starting or resuming so resuming does
  not immediately subtract a second from the preserved value.
- Add a paused state indicator to the mode label.
- Rename Stop to Reset and retain its behavior of restoring a fresh focus timer.
- Return the actual Tk button from the shared button factory so its label can be
  updated at runtime.
- Restore the Start label when a cycle completes or the timer is reset.
- Return to the stopped state after a completed cycle so pressing Start begins a
  new focus session instead of retrying a zero-second rest timer.

## Verification

- `python3 -m py_compile pomodoro98.py pomodoro98_2.py`

The control transitions still require manual verification on a graphical
desktop.
