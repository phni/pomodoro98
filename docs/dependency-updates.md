# Bundled dependency updates

The Flatpak bundles three things that the Freedesktop runtime does not
provide. Each one is pinned by URL and SHA-256 in
`io.github.phni.Pomodoro98.yml`, so each needs a way to stay current, mostly
for security fixes.

| Component | Pinned | How updates are found |
| --- | --- | --- |
| Tcl 9.0.x | `tcl9.0.*-src.tar.gz` | Weekly bot (below) |
| Tk 9.0.x | `tk9.0.*-src.tar.gz` | Weekly bot (below) |
| CPython source for tkinter | `Python-3.14.*.tar.xz` | Build guard (below) |

## Tcl and Tk: weekly bot

`.github/workflows/dependency-updates.yml` runs every Monday (and on demand
from the Actions tab). It uses Flathub's
[flatpak-external-data-checker](https://github.com/flathub-infra/flatpak-external-data-checker),
which reads the `x-checker-data` blocks on the Tcl and Tk sources, looks for
the newest 9.0.x release on tcl-lang.org, and opens a PR that updates the URL
and SHA-256. Treat it like any other PR: CI must pass, then run `make test`
and a quick launch before merging.

PRs opened with the default `GITHUB_TOKEN` do not start CI on their own. To
run CI on them, close and reopen the PR, or add a fine-grained personal access
token with contents and pull-request write access as the repository secret
`DEPENDENCY_BOT_TOKEN`.

The checker stays on Tcl/Tk 9.0.x. Moving to a new minor series (9.1) is a
deliberate change: update the version pattern and the library names in the
manifest together.

## CPython source: build guard

`_tkinter` is compiled against CPython's internal headers, so its source must
match the runtime's Python version exactly ([ADR 0004](adr/0004-freedesktop-26.08-runtime.md)).
This cannot be "kept current" independently; it follows the runtime.
`flatpak/check_tkinter_source.py` runs first in the `tkinter` module and stops
the build with a clear message when a runtime update changes the Python
version. Then update the module's source URL and SHA-256 to the matching
CPython release from python.org.

## Security advisories

Before each release (see [releasing.md](releasing.md)), check for open
dependency PRs and for Tcl/Tk security announcements on
[tcl-lang.org](https://www.tcl-lang.org/) and CPython security releases on
[python.org](https://www.python.org/downloads/). Runtime security fixes arrive
automatically through Freedesktop runtime updates.
