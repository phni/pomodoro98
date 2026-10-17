<!-- Title: Conventional Commit summary ending with the Linear key,
     e.g. "fix(sound): fall back to the bell when aplay fails (R3D-50)" -->

Linear: R3D-

## What changes for the user

Before:

After:

## How

<!-- A short explanation of the approach, if it is not obvious from the diff. -->

## Checks

- [ ] `make lint-py`
- [ ] `make lint` and `make test` (Flatpak), if packaging or runtime behavior changed
- [ ] Manual run: Start / Pause / Reset, focus→rest, progress colours, title, sound or bell, close
- [ ] `CHANGELOG.md` updated under `[Unreleased]` (user-visible changes only)

Platforms tested: <!-- e.g. Ubuntu 26.04, GNOME Wayland -->

<!-- For UI changes, attach a screenshot or short recording.
     Call out any new dependency or asset. -->
