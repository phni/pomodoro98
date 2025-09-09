# Pomodoro98

A retro Windows 98–styled Pomodoro clock built with Python and Tkinter.

## Features
- **Focus timer** (default 25 minutes)
- **Rest timer** (default 5 minutes)
- **Progress bar**: green during focus, red when focus ends and during rest
- **Always on top** window
- **Taskbar title** shows time remaining + mode
- **System tray icon** (optional via `pystray` + `Pillow`)
  - Green for focus
  - Red for rest
  - Tooltip shows time remaining

## Installation
```bash
cd pomodoro98
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
