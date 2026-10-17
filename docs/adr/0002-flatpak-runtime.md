# ADR 0002: Flatpak runtime selection

- **Status:** Accepted
- **Date:** 2026-08-13 (moved from `SDD/runtime-selection.md` on 2026-10-17)
- **Follow-up:** upgrade to Freedesktop 26.08 is tracked in R3D-64.

## Decision

Use:

```yaml
runtime: org.freedesktop.Platform
runtime-version: "25.08"
sdk: org.freedesktop.Sdk
```

This is a suitable foundation for Pomodoro98, provided the application manifest
builds and bundles Tcl, Tk, and the Python `_tkinter` extension.

## Why Freedesktop 25.08

- Pomodoro98 is a plain Python/Tk application and does not depend on GNOME or
  KDE framework APIs. The neutral Freedesktop runtime avoids adopting a larger
  desktop-specific API surface solely to run Tk.
- Flathub currently requires the latest suitable runtime at submission time,
  and its current build tutorial uses Freedesktop 25.08.
- The 25.08 runtime provides maintained Python 3.13 and the underlying Linux
  graphics, font, input, X11/XWayland, and audio stack expected by a small
  desktop application.
- The Freedesktop major branch provides ABI/API stability for its supported
  lifetime.

## Required application modules

Freedesktop SDK 25.08 explicitly removed Tcl and Tk. Its runtime Python cannot
be assumed to provide a working `tkinter` import. The manifest must therefore:

1. Build a pinned Tcl release.
2. Build a matching pinned Tk release against Tcl and the Freedesktop X11
   libraries.
3. Build a Python-version-matched `_tkinter` extension, or a complete compatible
   Python interpreter with Tk support, against those libraries.
4. Install the required Tcl/Tk script libraries and shared libraries under
   `/app`.
5. Verify `python3 -m tkinter` and launch Pomodoro98 inside the final sandbox.

The first manifest uses Tcl/Tk 9.0.2 because the maintained Python 3.13
`tkinter-standalone` source targets Tcl/Tk 9.0. Both archives have immutable
SHA-256 hashes, and the binding is pinned to an immutable Git commit.

## Display and audio implications

On Unix, Tk uses Xlib. Pomodoro98 therefore needs X11 access and runs on Wayland
desktops through XWayland; native Wayland permission alone is insufficient.
Audio output needs the Flatpak PulseAudio socket when an included backend uses
the host audio service. The initial manifest grants shared IPC as required for
X11, plus X11 and PulseAudio sockets. It does not grant filesystem, D-Bus,
device, or network access.

## Maintenance

Re-evaluate this decision whenever the Freedesktop runtime branch is upgraded.
In particular, keep Tcl/Tk and `_tkinter` aligned with the runtime Python ABI,
and remove bundled modules if a future maintained runtime supplies them.
