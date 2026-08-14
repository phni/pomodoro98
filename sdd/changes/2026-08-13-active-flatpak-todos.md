# Active Flatpak TODOs

Date: 2026-08-13

## Completed items

### Working-directory-independent assets

- Verified `pomodoro98_2.py` derives its asset directories from the resolved
  location of the installed script.
- Verified the focus sound, rest-completion sound, and focus icon resolve when
  the process working directory is outside the repository.
- Marked the corresponding `SDD/todo.md` item complete. The implementation was
  originally recorded in `2026-08-13-production-hardening.md`.

### Installed application launcher

- Added `flatpak/pomodoro98`, a POSIX shell launcher intended for installation
  at `/app/bin/pomodoro98`.
- The launcher replaces itself with Python 3 running
  `/app/lib/pomodoro98/pomodoro98_2.py` and forwards all command-line arguments.
- Marked the corresponding `SDD/todo.md` item complete.

## Verification

- `python3 -m py_compile pomodoro98.py pomodoro98_2.py`
- Asset resolution assertions executed from `/tmp`.
- `sh -n flatpak/pomodoro98`
