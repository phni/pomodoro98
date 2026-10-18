# Initial Flatpak manifest

Date: 2026-08-13

## Changes

- Add `io.github.phni.Pomodoro98.yml` using Freedesktop Platform/SDK 25.08.
- Bundle Tcl/Tk 9.0.2 from SHA-256-pinned upstream archives.
- Build the Python 3.13 `_tkinter` extension from immutable
  `tkinter-standalone` commit `8e78e38ef0cceb44a3a0062e1c314a4ff3f981db`.
- Install the launcher, maintained script, assets, license, desktop file,
  MetaInfo, and hicolor icons into their expected `/app` locations.
- Grant shared IPC as required by X11, plus X11 and PulseAudio sockets. Tk on
  Unix uses X11, including through XWayland; the app has no filesystem, device,
  bus, or network permissions.
- Exclude optional tray/audio Python packages from the initial build. The app
  remains functional through its guarded optional imports and Tk bell fallback.

## Pending sub-actions

- Manually exercise the complete timer cycle and controls in the installed app.
- Test on native X11 and a Wayland desktop through XWayland where available.
- Decide whether optional tray integration should be included in the Flatpak.

## Verification completed

- Installed `org.flatpak.Builder` 1.4.9 from Flathub.
- Completed a clean Freedesktop 25.08 build with pinned-source downloads.
- AppStream composition and desktop exports completed successfully.
- Installed the app as a local user Flatpak and launched it successfully.
- Confirmed packaged Tcl 9.0.2 and Tk 9.0.2 initialize inside the installed app.
- Confirmed the app imports and launches with `pystray`, Pillow, simpleaudio,
  and pygame absent.
- Confirmed exported icons use the required hicolor directory layout.
- Confirmed installed permissions contain only shared IPC, X11, and PulseAudio.
- Ran the official Flathub manifest linter and addressed its requirement for
  shared IPC with X11. AppStream URL validation remains pending until the
  screenshot commit is pushed to GitHub.
