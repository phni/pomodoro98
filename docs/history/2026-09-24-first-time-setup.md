# First-time setup documentation

- Added fresh-machine prerequisites and ordered Ubuntu/Debian commands for
  source runs, optional Python integrations, and Flatpak development.
- Documented Tkinter verification, graphical-session requirements, Flathub
  configuration, runtime/SDK setup, and common setup failures.
- Checked Flatpak setup against the official Flathub Ubuntu instructions and
  checked documented Make targets against the repository Makefile.
- Documented the Makefile's `--disable-rofiles-fuse` workaround, which applies
  to build, rebuild, and install. The previous build log now reaches export,
  finish-cache commit, and cache pruning; packaged import verification remains
  pending, so the build-fix parent TODO remains active.
- Python syntax compilation and `git diff --check` passed. No fresh-machine
  package installation or interactive GUI tests were performed for this edit.
- Existing local Tkinter installation and Flatpak publication/manual-testing
  blockers remain recorded in `SDD/todo.md`.
