# Releasing Pomodoro98

This is the step-by-step process for cutting a release. The conventions behind
it are in [ADR 0001](adr/0001-sdlc-conventions.md); the manual tests are in the
[release checklist](release-checklist.md).

## Version numbers

Releases use calendar versioning, `YYYY.MM.PATCH`, with no leading zero in the
month:

| Situation | Next version |
| --- | --- |
| First release in October 2026 | `2026.10.0` |
| Another release later in October 2026 | `2026.10.1` |
| First release in November 2026 | `2026.11.0` |

The version lives only in `src/pomodoro98/__init__.py` (`__version__`). Git tags
add a `v` prefix: version `2026.10.0` is tag `v2026.10.0`. Git history starts at
the 2026.10.0 release; the earlier 0.1.0 has no tag (see `CHANGELOG.md`).

## 1. Prepare the release PR

Create a Linear issue for the release (for example "Ship 2026.11.0") and a
branch from the latest `main`. In one PR:

1. Set `__version__` in `src/pomodoro98/__init__.py` to the new version.
2. Add a `<release>` as the **first** entry in
   `flatpak/io.github.phni.Pomodoro98.metainfo.xml`, with today's date, a
   `details` URL pointing at the GitHub release, and a short user-facing
   description (a `<p>` plus a few `<li>` items; Flathub shows this text).
3. In `CHANGELOG.md`, add a `## [YYYY.MM.PATCH] - YYYY-MM-DD` heading directly
   under `## [Unreleased]` so the unreleased entries move into the release,
   leave `[Unreleased]` empty, and update the comparison links at the bottom.
4. Run `make lint` (includes `scripts/check_version.py`, which fails if the
   package version and the newest MetaInfo release differ), `make test-py`,
   and `make lint-repo`.
5. Run the [release checklist](release-checklist.md) on the built Flatpak,
   on Wayland and X11.

Title the PR `chore(release): YYYY.MM.PATCH (R3D-NN)` and record the checklist
result in its description.

## 2. Merge

The maintainer squash-merges the PR once CI is green. `main` now carries the
release commit.

## 3. Tag

Only the maintainer pushes release tags, or Claude with the maintainer's
explicit approval for that tag:

```bash
git checkout main && git pull
git tag -a vYYYY.MM.PATCH -m "Pomodoro98 YYYY.MM.PATCH"
git push origin vYYYY.MM.PATCH
```

Tags are never moved or reused. If a release is broken, fix it and release the
next `PATCH` version.

## 4. Publish the GitHub release

Pushing the tag runs the release workflow (`.github/workflows/release.yml`,
added by R3D-61). It checks that the tag, `__version__`, and the MetaInfo
release all match, builds the Python wheel and sdist plus a `.flatpak` bundle,
and publishes a GitHub release whose notes are the version's `CHANGELOG.md`
section. Check that the release page shows the notes and three assets.

Without the workflow, publish by hand:

```bash
python3 -m build
gh release create vYYYY.MM.PATCH dist/* --title "Pomodoro98 YYYY.MM.PATCH" \
    --notes "<the version's CHANGELOG section>"
```

## 5. Update Flathub

After the app is on Flathub (R3D-63), open a PR in
`flathub/io.github.phni.Pomodoro98` that changes the `pomodoro98` module's
`tag` and `commit` to the new release. Comment `bot, build`, test the build,
and merge it once green. Flathub publishes it within a few hours.

## 6. After the release

- Close the release issue in Linear and confirm the release PR's issues are
  Done.
- Check the bundled dependencies: Tcl/Tk and the CPython source used to build
  tkinter must stay current and match the runtime's Python (R3D-68,
  [ADR 0004](adr/0004-freedesktop-26.08-runtime.md)). Merge any open
  dependency-update PRs before the next release.
