# ADR 0003: No system tray in the first Flatpak release

- **Status:** Accepted
- **Date:** 2026-10-18
- **Decider:** Phani (maintainer)
- **Linear:** decided in R3D-67; follow-up work is R3D-71

## Context

Pomodoro98 can show an optional system tray icon (green in focus, red in rest,
grey when stopped, with the remaining time as a tooltip) through `pystray` and
`Pillow`. It works when the app runs from source with the `tray` extra. The
Flatpak does not bundle these libraries, so the app silently skips the tray
there (`TRAY_OK` is false), and the sandbox requests no tray permission.

Shipping the tray in the Flatpak would require:

- bundling and hash-pinning `pystray`, `Pillow`, PyGObject, and
  `libayatana-appindicator` as extra manifest modules that must be kept up to
  date;
- an extra sandbox permission, `--talk-name=org.kde.StatusNotifierWatcher`,
  which must be justified in the Flathub review;
- testing on several desktops, because tray support varies: Ubuntu GNOME has it
  through the AppIndicator extension, stock GNOME has none, and KDE Plasma has
  it natively.

Meanwhile the window already shows the state without a tray: it stays on top,
and its title reads `Pomodoro98 [Focus]`, `[Rest]`, `[Paused]`, or `[Stopped]`.

## Decision

The first Flatpak and Flathub release ships **without** tray support. The
Flatpak keeps its current minimal permissions (X11, shared IPC, PulseAudio).
The tray code stays in the app, so source installs with `.[tray]` keep the
icon, and the Flatpak keeps degrading gracefully without it.

Tray support in the Flatpak is planned for a later release (R3D-71). When it
ships, this ADR becomes Superseded.

## Consequences

**Easier**

- Smaller build with fewer bundled modules to track for security updates.
- No extra sandbox permission, so the Flathub review is simpler.
- No per-desktop tray behavior to test before the first release.

**Harder**

- Flatpak users cannot see the timer at a glance from the top bar; they rely
  on the always-on-top window and its title.
- Source and Flatpak installs behave differently until R3D-71 lands.

**Alternatives considered**

- **Ship the tray now:** rejected for the first release because of the extra
  modules, permission, and testing it adds before publication.
- **Remove the tray code entirely:** rejected; it already works for source
  installs and is covered by tests, and R3D-71 will reuse it.
