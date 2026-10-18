# Production hardening: initial pass

Date: 2026-08-13

## Scope

This pass establishes `pomodoro98_2.py` as the production-hardening target. The
original `pomodoro98.py` remains unchanged.

## Changes

- Resolve icon and sound assets relative to `pomodoro98_2.py`, allowing the app
  to launch from a working directory other than the repository root.
- Correct the rest-completion sound path to the shipped `sounds/reset_end.wav`.
- Keep all Tk calls on the main thread. Audio workers now place fallback bell
  requests in a thread-safe queue that the Tk event loop polls.
- Serialize audio backend access to prevent concurrent mixer initialization and
  overlapping backend setup from multiple button presses.
- Replace shell-style `aplay` command construction with an explicit argument
  list.
- Add standard-library logging for icon, audio, tray, and shutdown failures
  instead of silently discarding operational errors.
- Add an idempotent `shutdown()` path that cancels timer and bell-poll callbacks,
  stops the tray icon, closes the pygame mixer, and destroys the window.
- Name audio worker threads to make diagnostics easier.

## Verification

- `python3 -m py_compile pomodoro98.py pomodoro98_2.py`

GUI behavior still requires manual verification on a system with a graphical
display, as the repository has no automated UI test suite.
