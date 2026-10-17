# Repository Guidelines

## SDLC Conventions

Branching, commit and PR format, merging, versioning, Linear tracking, and the
Claude Code workflow are defined in
[ADR 0001: SDLC conventions](docs/adr/0001-sdlc-conventions.md). Follow it for
every change.

## Task Workflow

Planned work lives only in Linear (project **SDLC Pomodoro98**, team key `R3D`).
Start every task from its Linear issue and reference the key in the PR title.
When an issue needs information or a material decision that is not in the
repository or the issue, ask the maintainer instead of making an unsafe
assumption. If the work reveals a follow-up, blocker, or out-of-scope change,
create a Linear issue for it (or comment on the current one) rather than
noting it in the repository. Record what changed and how it was verified in the
PR description; user-visible changes also go in `CHANGELOG.md`. Older change
notes are archived in `docs/history/`, and design decisions are recorded as
ADRs in `docs/adr/`.

## Project Structure & Module Organization

Pomodoro98 is a Python/Tkinter application packaged with `pyproject.toml` (src layout):

- `src/pomodoro98/timer.py`: `TimerModel` state machine and `Mode` enum, independent of Tk and driven by an injectable clock so it can be unit tested.
- `src/pomodoro98/app.py`: Tk window that renders `TimerModel`; `main()` is the `pomodoro98` console script.
- `src/pomodoro98/sound.py`: non-blocking sound playback with optional `simpleaudio`/`pygame`/`aplay` backends.
- `src/pomodoro98/tray.py`: optional `pystray` system tray icon.
- `src/pomodoro98/icons/` and `src/pomodoro98/sounds/`: runtime assets shipped as package data and resolved relative to the package, so the app runs from any working directory.
- `flatpak/` and `io.github.phni.Pomodoro98.yml`: Flatpak desktop file, MetaInfo, icons, and manifest.
- `docs/adr/`: architecture decision records; `docs/history/`: archived change notes.

Setup notes belong in `README.md`.

## Build, Test, and Development Commands

Create an isolated environment and install the app with its optional and development extras:

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -e '.[tray,audio,dev]'
```

Run the app with `make run` (source tree) or `pomodoro98` (installed). There is no build step for local runs. Before submitting changes, run `python3 -m compileall -q src` for a quick syntax check; `make lint` and `make test` also validate and build the Flatpak.

## Coding Style & Naming Conventions

Follow PEP 8 with four-space indentation. Use `snake_case` for functions, methods, and local variables; `UPPER_CASE` for configuration constants; and `CapWords` for classes. Private implementation helpers use a leading underscore, as in `_update_tray`. Keep Tkinter state changes on the main thread and isolate blocking audio or tray work. Keep timer rules in `timer.py` (no Tk imports), sound and tray code in their own modules, and `app.py` as a thin view. No formatter or linter is currently configured, so keep diffs focused and match nearby style.

## Testing Guidelines

No automated test suite or coverage target exists yet. Manually verify Start/Stop behavior, focus-to-rest transitions, progress colors, title updates, close handling, sound fallback, and tray state. Test graceful operation when optional dependencies or assets are unavailable. If adding tests, place them in `tests/`, use `test_*.py` names, and prefer `pytest` with timer, audio, and tray integrations mocked.

## Commit & Pull Request Guidelines

Recent history uses short, imperative, sentence-style subjects, for example `Enhance Pomodoro98 functionality...`. Keep each commit scoped to one logical change. Pull requests should describe user-visible behavior, list manual checks performed, identify affected platform(s), and link related issues. Include a screenshot or short recording for UI changes and call out new dependencies or assets explicitly.
