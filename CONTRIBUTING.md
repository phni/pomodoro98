# Contributing to Pomodoro98

Thanks for helping. This guide covers everything you need to make a change.
The project's process is defined in
[ADR 0001: SDLC conventions](docs/adr/0001-sdlc-conventions.md); this file is
the practical summary.

## 1. Find or create an issue

All planned work is tracked in Linear (project **SDLC Pomodoro98**, team key
`R3D`). External contributors can open a
[GitHub issue](https://github.com/phni/pomodoro98/issues) instead; the
maintainer will mirror it to Linear.

## 2. Set up your environment

You need Linux with Python 3.10+ and Tk (`sudo apt install python3-tk` on
Ubuntu/Debian). Then:

```bash
git clone https://github.com/phni/pomodoro98.git
cd pomodoro98
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -e '.[tray,audio,dev]'
pre-commit install
```

`pre-commit install` runs ruff and basic file checks automatically on every
commit. To build the Flatpak as well, follow "Flatpak development" in the
[README](README.md).

## 3. Make the change

1. Branch from the latest `main`, using the Linear branch name, for example
   `phanigr8/r3d-49-single-source-of-truth-for-the-version`.
2. Keep each commit to one logical change. Commit messages follow
   [Conventional Commits](https://www.conventionalcommits.org/):
   `type(scope): imperative summary`, where `type` is one of `feat`, `fix`,
   `docs`, `test`, `refactor`, `build`, `ci`, or `chore`.
3. Keep timer rules in `src/pomodoro98/timer.py` (no Tk imports) and the Tk
   window in `app.py` as a thin view. Keep Tk calls on the main thread.

## 4. Check your work

```bash
make lint-py      # ruff, syntax, and version checks (no Flatpak needed)
make test-py      # pytest suite with coverage (UI tests need a display)
make run          # run the app from the source tree
make lint         # also validates the desktop file, AppStream, and manifest
make test         # builds the Flatpak and runs sandbox checks
```

Then exercise the app by hand: Start, Pause, resume, Reset, a full focus→rest
cycle (temporarily lower `FOCUS_MINUTES`/`REST_MINUTES` in `app.py` locally),
progress colours, window title, sounds or bell, and closing the window.

## 5. Open a pull request

- Title: a Conventional Commit summary ending with the Linear key, for example
  `fix(sound): fall back to the bell when aplay fails (R3D-50)`.
- Fill in the PR template: what changed for the user, the checks you ran, and
  the platforms you tested.
- Add a line under `## [Unreleased]` in [CHANGELOG.md](CHANGELOG.md) for any
  user-visible change.
- CI (`.github/workflows/ci.yml`) runs lint, the tests on Python 3.10–3.13
  under Xvfb, and a Flatpak build with the Flathub linter on every PR.
- `main` is protected: every change needs a PR with passing CI, and the
  maintainer squash-merges it. The branch is deleted automatically after merging.

## Versioning

Releases use CalVer, `YYYY.MM.PATCH`. The version lives only in
`src/pomodoro98/__init__.py`; `make lint` checks that the newest MetaInfo
`<release>` matches it.
