# GNOME menu discovery

Date: 2026-08-13

## Investigation

- Confirmed `io.github.phni.Pomodoro98` is installed for the current user.
- Confirmed its exported desktop file exists and passes
  `desktop-file-validate`.
- Confirmed the GNOME Wayland session's `XDG_DATA_DIRS` contains the
  user-local Flatpak export directory.

## Action

- Refreshed the user-local desktop application database with
  `update-desktop-database` so GNOME can rediscover the launcher.
