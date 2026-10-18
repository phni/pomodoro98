# Release checklist

Run this before tagging every release. CI covers lint, unit and UI tests, the
Flatpak build, and the Flathub manifest linter; this list covers what only a
person can check: sound, the desktop shell, real time, and session types.

Copy the checklist into the release PR or Linear issue and tick it there.

## 1. Before you start

- [ ] All PRs for the release are merged and CI is green on `main`.
- [ ] `__version__` in `src/pomodoro98/__init__.py` is the new CalVer version
      (`YYYY.MM.PATCH`), and the newest `<release>` in
      `flatpak/io.github.phni.Pomodoro98.metainfo.xml` matches it with today's date.
- [ ] `CHANGELOG.md`: `[Unreleased]` is renamed to the new version and date,
      and a fresh empty `[Unreleased]` section is added.
- [ ] `make lint` passes locally (includes the version check).

## 2. Install the release build

```bash
git checkout main && git pull
make uninstall          # start clean
make install            # build and install the Flatpak for your user
```

- [ ] Pomodoro98 appears in the desktop app launcher with its icon.

For a quick cycle, launch from a terminal with short periods (1 minute focus,
30 seconds rest):

```bash
flatpak run --env=POMODORO98_FOCUS_SECONDS=60 --env=POMODORO98_REST_SECONDS=30 \
    io.github.phni.Pomodoro98
```

Use the launcher (full 25/5 minute periods) for at least one session per
release to confirm real-time behavior.

## 3. Manual checks

Do this section once in a **Wayland** session and once in an **X11** session
("Ubuntu on Xorg" on the login screen). Record the distribution and desktop.

### Timer and window

- [ ] Window opens centred, always on top, and the title reads
      `Pomodoro98 [Stopped]`; nothing in the window or title is truncated.
- [ ] **Start**: clock counts down once per second, title shows `[Focus]`,
      status shows `Mode: Focus`, button reads **Pause**, progress bar fills green.
- [ ] **Pause**: clock freezes, title shows `[Paused]`, status shows
      `Mode: Focus — Paused`. Wait 10 seconds; the time does not change.
- [ ] **Resume**: counting continues from the paused time.
- [ ] **Reset**: back to the full focus time, `[Stopped]`, empty progress bar.
- [ ] Focus end: rest starts automatically, title `[Rest]`, red progress bar.
- [ ] Rest end: status shows `Mode: Cycle Complete (Stopped)`, clock `00:00`,
      full red bar; **Start** begins a new focus session.

### Sound

- [ ] Focus end plays the focus-end sound through the speakers.
- [ ] Cycle end plays the rest-end sound.
- [ ] With audio muted or no output device, the app keeps running (the Tk bell
      may sound instead).

### Desktop integration

- [ ] The dock or taskbar shows the Pomodoro98 icon (not a generic icon)
      while the app runs.
- [ ] The window icon changes between focus, rest, and idle.
- [ ] Tray icon (source installs with `.[tray]` only; the Flatpak has no
      tray, see ADR 0003 / R3D-71):
      green in focus, red in rest, grey when stopped; tooltip shows the
      remaining time.

### Shutdown

- [ ] Closing the window during a running session quits the app immediately.
- [ ] `flatpak ps` no longer lists `io.github.phni.Pomodoro98`.

## 4. Record the result

- [ ] Note any failure as a Linear bug in **SDLC Pomodoro98** before tagging;
      do not release with an open failure unless the maintainer accepts it.
- [ ] Add "Release checklist passed on <distro>, Wayland and X11" to the
      release PR.

Tagging and publishing steps are in [the release process](releasing.md).
