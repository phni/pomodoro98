# Changelog

All notable user-visible changes to Pomodoro98 are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Releases after 0.1.0 use calendar versioning, `YYYY.MM.PATCH`
([ADR 0001](docs/adr/0001-sdlc-conventions.md)).

## [Unreleased]

## [2026.10.2] - 2026-10-25

### Changed

- New end-of-focus and end-of-break chimes, made from scratch so they can be
  shared freely; they replace sounds of unknown origin.
- The app icon is now drawn from code, with a scalable SVG version; it looks
  the same as before.

## [2026.10.1] - 2026-10-20

### Changed

- New pixel-art tomato app icon in a Windows 98 window, used for the
  launcher, dock, and window; the idle window icon is a grey version.
- The store description no longer mentions a tray icon, which the Flatpak
  does not include.

## [2026.10.0] - 2026-10-18

### Added

- `POMODORO98_FOCUS_SECONDS` and `POMODORO98_REST_SECONDS` environment
  variables shorten the periods for quick manual testing.
- A manual release checklist in `docs/release-checklist.md`.
- Installable Python package with a `pomodoro98` command
  (`pip install -e '.[tray,audio]'`, or `python -m pomodoro98`).
- Contributor guide, security policy, and issue and pull request templates.

### Changed

- Updated the screenshot to show the current window.
- The Flatpak uses the Freedesktop 26.08 runtime (Python 3.14), with tkinter
  built from the matching CPython release, and bundles Tcl/Tk 9.0.4.
- The window is wider (about 650 px instead of 410 px), so the title and
  status text are no longer truncated.
- The window title shows only the mode, e.g. "Pomodoro98 [Focus]" or
  "Pomodoro98 [Paused]", and the focus status reads "Mode: Focus".
- The timer counts down to a fixed deadline, so it no longer drifts and keeps
  counting while the computer is suspended.
- The window, title, and tray update only when what they show has changed.
- The application name is written "Pomodoro98" everywhere.
- The Flatpak installs the app as a Python package.

### Fixed

- `make install` installs with the host `flatpak`, so Pomodoro98 appears in
  the desktop launcher.
- The Tk bell now sounds when the `aplay` fallback fails, for example when no
  audio device is available.

### Removed

- The unmaintained legacy `pomodoro98.py` script.

## 0.1.0 - 2026-08-13

Pre-CalVer release. Its history was folded into the 2026.10.0 initial import,
so it has no tag or GitHub release.

### Added

- Windows 98-styled focus (25 minutes) and rest (5 minutes) timer with Start,
  Pause, and Reset.
- Progress bar, always-on-top window, and remaining time in the window title.
- Optional system tray icon and optional `simpleaudio`/`pygame` sound backends,
  with `aplay` and Tk bell fallbacks.
- Flatpak packaging as `io.github.phni.Pomodoro98` with desktop file, MetaInfo,
  and icons.

[Unreleased]: https://github.com/phni/pomodoro98/compare/v2026.10.2...HEAD
[2026.10.2]: https://github.com/phni/pomodoro98/compare/v2026.10.1...v2026.10.2
[2026.10.1]: https://github.com/phni/pomodoro98/compare/v2026.10.0...v2026.10.1
[2026.10.0]: https://github.com/phni/pomodoro98/releases/tag/v2026.10.0
