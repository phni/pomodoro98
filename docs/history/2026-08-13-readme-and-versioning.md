# README and initial versioning

Date: 2026-08-13

## Changes

- Identify `pomodoro98_2.py` as the maintained production entry point and retain
  `pomodoro98.py` for historical comparison.
- Expand the README with cloning, environment setup, run instructions, Linux
  desktop support expectations, optional integration behavior, a screenshot
  section, maintainer contact, issue tracker, license, and version.
- Use the public GitHub identity `phni` for maintainer contact.
- Establish `0.1.0` in the repository-root `VERSION` file and as `APP_VERSION`
  in the maintained application.
- Confirm and document the shipped event sounds as `focus_end.wav` and
  `reset_end.wav`.

## Release completion

- Captured the application window on Linux at
  `docs/screenshots/pomodoro98.png` and linked it from the README.
- Prepared the release contents for the annotated `v0.1.0` Git tag.

## Verification

- `python3 -m py_compile pomodoro98.py pomodoro98_2.py`
- `sh -n flatpak/pomodoro98`
- Start/Pause/Resume/Reset state-transition harness.
- Manual inspection of the captured 436×310 PNG screenshot.
