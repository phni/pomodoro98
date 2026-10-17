# Repository Guidelines

## SDLC Conventions

Branching, commit and PR format, merging, versioning, Linear tracking, and the
Claude Code workflow are defined in
[ADR 0001: SDLC conventions](docs/adr/0001-sdlc-conventions.md). Follow it for
every change.

## SDD TODO Workflow

At the start of each task, inspect `SDD/todo.md`. Treat every line marked with
`[+]` as an active instruction and take action on it as part of the current
work. When an active item requires information or a material decision that is
not available in the repository, ask the user for that input instead of making
an unsafe assumption. Leave `[ ]` items untouched unless the user requests
them. After completing an active item, change its marker from `[+]` to `[x]` and
record the implementation under `sdd/changes/`. Whenever work reveals a
pending action, blocker, or incomplete portion of a TODO, add it immediately to
`SDD/todo.md` as an indented checklist sub-action beneath its parent item. Mark
the parent complete only after all required sub-actions are complete.

## Project Structure & Module Organization

Pomodoro98 is a small, script-based Python/Tkinter application; it is not packaged as a module. `pomodoro98_2.py` is the only entry point.

Runtime assets live in `icons/` (`icon.png`, `icon_idle.png`, and `icon_rest.png`) and `sounds/` (`focus_end.wav` and `reset_end.wav`). Paths are relative to the repository root, so run the application from that directory. Dependencies are listed in `requirements.txt`; setup notes belong in `README.md`.

## Build, Test, and Development Commands

Create an isolated environment and install optional tray/audio support:

```bash
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements-optional.txt
```

Run the app with `python pomodoro98_2.py`. There is no build step. Before submitting changes, run `python -m py_compile pomodoro98_2.py` for a quick syntax check.

## Coding Style & Naming Conventions

Follow PEP 8 with four-space indentation. Use `snake_case` for functions, methods, and local variables; `UPPER_CASE` for configuration constants; and `CapWords` for classes. Private implementation helpers use a leading underscore, as in `_update_tray`. Keep Tkinter state changes on the main thread and isolate blocking audio or tray work. Preserve the existing grouping of configuration, UI, timer logic, sound, and tray methods. No formatter or linter is currently configured, so keep diffs focused and match nearby style.

## Testing Guidelines

No automated test suite or coverage target exists yet. Manually verify Start/Stop behavior, focus-to-rest transitions, progress colors, title updates, close handling, sound fallback, and tray state. Test graceful operation when optional dependencies or assets are unavailable. If adding tests, place them in `tests/`, use `test_*.py` names, and prefer `pytest` with timer, audio, and tray integrations mocked.

## Commit & Pull Request Guidelines

Recent history uses short, imperative, sentence-style subjects, for example `Enhance Pomodoro98 functionality...`. Keep each commit scoped to one logical change. Pull requests should describe user-visible behavior, list manual checks performed, identify affected platform(s), and link related issues. Include a screenshot or short recording for UI changes and call out new dependencies or assets explicitly.
