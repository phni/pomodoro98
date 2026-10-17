# Security Policy

## Supported versions

Only the latest release of Pomodoro98 receives security fixes.

## Reporting a vulnerability

Please do not open a public issue for security problems. Report them privately
through GitHub's
[private vulnerability reporting](https://github.com/phni/pomodoro98/security/advisories/new)
for this repository.

Include what you found, how to reproduce it, and the version or commit you
tested. You can expect an acknowledgement within a week. Fixes are released
as a new version and noted in [CHANGELOG.md](CHANGELOG.md).

## Scope

Pomodoro98 is an offline desktop app. The Flatpak requests only X11, shared IPC,
and PulseAudio access, with no network or filesystem permissions. The Flatpak
bundles Tcl/Tk and a `_tkinter` build; vulnerabilities in those components are
in scope when they affect the packaged app.
