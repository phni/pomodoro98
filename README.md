# Pomodoro98

A retro Windows 98–styled Pomodoro clock built with Python and Tkinter.

The application entry point is `pomodoro98_2.py`.

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

## First-time setup and prerequisites

Cloning or pulling this repository does not install system dependencies. Follow
these steps once on each new machine. Use the local setup to run the Python app;
follow the Flatpak setup below when you want to build and install a package.

Pomodoro98 is intended for Linux desktops with Python 3 and Tk installed. It is
developed on Wayland and should also work on X11. System-tray availability
depends on the desktop environment. Audio and tray integrations degrade
gracefully when their optional dependencies are unavailable.

### Run locally (Ubuntu/Debian)

Install Git, Make, Python, Tkinter, and virtual environment support:

```bash
sudo apt update
sudo apt install git make python3 python3-tk python3-venv
```

Clone the repository, or enter your existing checkout if you already have it:

```bash
git clone https://github.com/phni/pomodoro98.git
cd pomodoro98
```

Verify that Tkinter opens a test window, close it, then start the app:

```bash
python3 -m tkinter
make run
```

Run these commands in a graphical desktop session. No build step or pip packages
are needed for the core app. On other Linux distributions, install the equivalent
packages using your distribution's package manager.

### Optional tray and audio support

From the repository directory, create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

The core application uses only Python and Tk, so `requirements.txt` intentionally
contains no package entries. Tkinter is supplied by your Python installation or
operating system, not pip. To enable the optional system tray and additional
audio backends, install:

```bash
python3 -m pip install -r requirements-optional.txt
make run
```

Activate `venv` again in each new terminal when you want these optional packages.

Run the maintained application from any working directory:

```bash
python3 /path/to/pomodoro98/pomodoro98_2.py
```

From the repository directory, you can also use `make run`. If it reports
`No module named tkinter`, install the OS Tkinter package above. Installing the
pip requirements does not install Tkinter.

Optional sound backends are attempted in this order: `simpleaudio`, `pygame`,
the Linux `aplay` command, and the Tk system bell.

## Flatpak development

### First-time Flatpak setup (Ubuntu/Debian)

Install the host tools and configure the Flathub remote:

```bash
sudo apt update
sudo apt install git make python3 flatpak appstream desktop-file-utils
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
```

For other distributions, follow the [Flathub setup instructions](https://flathub.org/en/setup).
Restart your desktop session after first installing Flatpak if needed for desktop
menu integration. System-wide setup may ask for administrator authentication.

From the repository directory, install Builder and the Freedesktop 25.08 runtime
and SDK, then build and run:

```bash
make setup-flatpak
make build
make install
make run-flatpak
```

The first setup/build needs internet access and downloads the runtime, SDK, and
source dependencies. The package bundles its own Tcl/Tk and Tkinter; host
`python3-tk` is needed for `make run`, not for the Flatpak application.

### Everyday Flatpak commands

After setup, run these commands from the repository directory:

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

The Makefile disables Flatpak Builder's `rofiles-fuse` cache mounts so builds
also work on hosts where those mounts fail. Build caching remains enabled for
`make build`; `make rebuild` disables cache lookups.

### Troubleshooting a fresh machine

| Error | Action |
| --- | --- |
| `No module named tkinter` with `make run` | Install `python3-tk`, then check `python3 -m tkinter` with the same Python environment. |
| `make: command not found` | Install the `make` OS package. |
| Flatpak is missing or the Flathub remote is missing | Complete the first-time Flatpak setup above. |
| Builder, runtime, or SDK is not installed | Run `make setup-flatpak` before `make build`. |
| `Failure spawning rofiles-fuse` | Use the updated Makefile, which passes `--disable-rofiles-fuse` for builds and installs. |
| `no display name` or cannot connect to the display | Run the app from a graphical desktop session. |

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
