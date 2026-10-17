# Flatpak runtime selection

Date: 2026-08-13

## Changes

- Select `org.freedesktop.Platform` and `org.freedesktop.Sdk` version `25.08` as
  the neutral, maintained Flatpak foundation.
- Document the selection and its tradeoffs in `SDD/runtime-selection.md`.
- Record that Freedesktop 25.08 removed Tcl/Tk, so the application manifest must
  bundle Tcl, Tk, and a runtime-Python-compatible `_tkinter` binding.
- Add manifest sub-actions for bundling those components and proving Tkinter
  starts inside the finished sandbox.
- Document that Unix Tk uses X11 and therefore runs through XWayland on Wayland
  desktops.

## Verification basis

- Current Flatpak build documentation uses Freedesktop 25.08.
- The Freedesktop 25.08 release notes explicitly list Tcl and Tk as removed.
- Current Freedesktop releases retain Python 3.13 and maintained desktop/audio
  foundations.
- Python documentation confirms Tkinter requires Tcl/Tk and uses Xlib on Unix.
