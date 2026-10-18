# ADR 0004: Freedesktop 26.08 runtime with tkinter built from CPython

- **Status:** Accepted
- **Date:** 2026-10-18
- **Decider:** Phani (maintainer)
- **Linear:** R3D-64
- **Supersedes:** [ADR 0002](0002-flatpak-runtime.md)

## Context

ADR 0002 chose `org.freedesktop.Platform` 25.08 and bundled Tcl/Tk 9.0.2 plus
`_tkinter` from the third-party `tkinter-standalone` project, because the
runtime ships Python without tkinter. Freedesktop 26.08 is now available and
the Flathub linter warns `runtime-update-available-to-org.freedesktop.Platform-26.08`;
Flathub expects new submissions to use the latest runtime.

26.08 ships Python 3.14.7. The newest `tkinter-standalone` commit only
supports Python 3.13 and fails to compile against 3.14 (`pycore_long.h` not
found), and the project has no 3.14 release.

## Decision

- Use `org.freedesktop.Platform` / `org.freedesktop.Sdk` **26.08**.
- Keep building pinned Tcl/Tk 9.0.2 from source, as in ADR 0002 (26.08 still
  has no Tcl/Tk).
- Replace `tkinter-standalone` with the official **CPython 3.14.7 source
  release** (pinned by SHA-256): compile `Modules/_tkinter.c` with the SDK's
  Python headers (including `internal/`) against the bundled Tcl/Tk, and copy
  `Lib/tkinter` into `/app/lib/python3.14/site-packages`.

The rest of ADR 0002 still holds: neutral Freedesktop runtime, X11 via
XWayland, PulseAudio, no filesystem, network, or extra D-Bus access.

## Consequences

**Easier**

- No dependency on a small third-party project to keep up with new Python
  releases; the source is the upstream CPython release that matches the
  runtime.
- The Flathub runtime-update warning is gone.

**Harder**

- `_tkinter` uses CPython internal headers, so its source must match the
  runtime's Python version. When the runtime updates Python (for example a
  3.14.x micro release in a 26.08 point update, or 3.15 in 27.08), bump the
  CPython source URL and hash in the manifest; `make test` fails fast if they
  drift apart.

**Alternatives considered**

- **Stay on 25.08:** rejected; it delays the upgrade until after publication
  and keeps the linter warning.
- **Wait for `tkinter-standalone` to support 3.14:** rejected; no timeline.
