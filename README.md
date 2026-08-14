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

Run the maintained application from any working directory:

```bash
python3 /path/to/pomodoro98/pomodoro98_2.py
```

Optional sound backends are attempted in this order: `simpleaudio`, `pygame`,
the Linux `aplay` command, and the Tk system bell.

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
