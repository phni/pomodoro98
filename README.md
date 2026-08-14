# Pomodoro98

A retro Windows 98–styled Pomodoro clock built with Python and Tkinter.

The production entry point is `pomodoro98_2.py`. The older `pomodoro98.py`
script is retained for historical comparison and does not receive new features.

## Features

- **Focus timer** (default 25 minutes)
- **Rest timer** (default 5 minutes)
- **Pause and resume** without losing the remaining time
- **Reset** to a fresh focus session
- **Progress bar**: green during focus, red when focus ends and during rest
- **Always on top** window
- **Taskbar title** shows time remaining + mode
- **System tray icon** (optional via `pystray` + `Pillow`)
  - Green for focus
  - Red for rest
  - Tooltip shows time remaining

## Installation

Pomodoro98 is intended for Linux desktops with Python 3 and Tk installed. It is
developed on Wayland and should also work on X11. System-tray availability
depends on the desktop environment. Audio and tray integrations degrade
gracefully when their optional dependencies are unavailable.

```bash
git clone https://github.com/phni/pomodoro98.git
cd pomodoro98
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
python3 -m pip install -r requirements.txt
```

The core application uses only Python and Tk. To enable the optional system tray
and additional audio backends, install:

```bash
python3 -m pip install -r requirements-optional.txt
```

Run the maintained application from any working directory:

```bash
python3 /path/to/pomodoro98/pomodoro98_2.py
```

Optional sound backends are attempted in this order: `simpleaudio`, `pygame`,
the Linux `aplay` command, and the Tk system bell.

## Flatpak development

The repository provides a Makefile so each development machine uses the same
Flatpak Builder workflow. First install the build prerequisites:

```bash
make setup-flatpak
```

The host must already have Flatpak and the Flathub remote configured. Then use:

```bash
make build         # build using cached dependency modules
make rebuild       # rebuild every module without the cache
make lint          # metadata and source validation
make test          # non-interactive sandbox checks
make install       # install for the current user
make run-flatpak   # run the installed package
make uninstall     # remove the user-local package
```

Run `make help` for the complete command list. Build output and Builder caches
are local to the repository and ignored by Git.

## Screenshot

![Pomodoro98 application window](docs/screenshots/pomodoro98.png)

Pomodoro98 running a focus session on Linux.

## Maintainer

Maintained by [phni](https://github.com/phni).

Report bugs and request features through the
[GitHub issue tracker](https://github.com/phni/pomodoro98/issues).

## Version

Current development version: `0.1.0`.

## License

Pomodoro98 is available under the [MIT License](LICENSE). Its SPDX identifier
is `MIT`.
