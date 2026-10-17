# Flatpak window icon association

Date: 2026-08-13

## Problem

GNOME displayed its generic gears icon for the running application even though
the application-ID-named PNG icons were installed and valid.

## Cause

Tk used its generic default window class, so GNOME could not associate the
running window with `io.github.phni.Pomodoro98.desktop`.

## Changes

- Set Tk's base name and window class to the permanent Flatpak application ID.
- Add the matching `StartupWMClass` to the desktop entry.

This leaves the packaged icon assets unchanged and gives GNOME an explicit,
stable link between the running window and its desktop launcher.
