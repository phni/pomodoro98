"""Tk user interface for Pomodoro98.

- Start/Pause and Reset buttons (with click beep)
- Progress bar: green during focus; red when time is up and during rest
- Always-on-top window
- Title shows remaining time + mode (visible on taskbar)
- Optional system tray icon (green/red) with live-updating tooltip
- Sounds: focus_end.wav when focus ends, reset_end.wav when the cycle completes,
  and click.wav on Start/Pause/Reset if present; otherwise the Tk bell
"""

import logging
import queue
import tkinter as tk
from pathlib import Path

from pomodoro98 import APP_ID, __version__
from pomodoro98.sound import SoundPlayer
from pomodoro98.timer import Event, Mode, TimerModel
from pomodoro98.tray import TrayIcon

# ------------------------------
# Config
# ------------------------------
FOCUS_MINUTES = 25
REST_MINUTES = 5
TICK_MS = 200  # how often the view polls the timer; display changes once per second
BELL_POLL_MS = 100

APP_DIR = Path(__file__).resolve().parent
LOGGER = logging.getLogger(__name__)
APP_VERSION = __version__

# Sounds
SOUND_ENABLED = True
SOUNDS_DIR = APP_DIR / "sounds"
SOUND_FOCUS_END = SOUNDS_DIR / "focus_end.wav"
SOUND_REST_END = SOUNDS_DIR / "reset_end.wav"
SOUND_CLICK = SOUNDS_DIR / "click.wav"  # optional

# Win98 palette
WIN98_BG         = "#C0C0C0"
WIN98_DARK       = "#808080"
WIN98_LIGHT      = "#FFFFFF"
WIN98_TEXT       = "#000000"
WIN98_TITLE_BG   = "#000080"
WIN98_TITLE_TEXT = "#FFFFFF"

BAR_NORMAL = "#00A000"
BAR_ALERT  = "#C00000"

MODE_LABELS = {
    Mode.FOCUS: "Mode: Focus (Work)",
    Mode.REST: "Mode: Rest",
    Mode.STOPPED: "Mode: Stopped",
}
MODE_TITLES = {Mode.FOCUS: "Focus", Mode.REST: "Rest", Mode.STOPPED: "Stopped"}
CYCLE_COMPLETE_LABEL = "Mode: Cycle Complete (Stopped)"
EVENT_SOUNDS = {Event.FOCUS_END: SOUND_FOCUS_END, Event.CYCLE_COMPLETE: SOUND_REST_END}

# Icons
ICONS_DIR = APP_DIR / "icons"
ICON_FOCUS_FILE = ICONS_DIR / "icon.png"
ICON_REST_FILE = ICONS_DIR / "icon_rest.png"
ICON_IDLE_FILE = ICONS_DIR / "icon_idle.png"


class Pomodoro98(tk.Tk):
    def __init__(self):
        super().__init__(baseName=APP_ID, className=APP_ID)
        self._closing = False
        self._bell_requests = queue.SimpleQueue()
        self._sound = SoundPlayer(on_failure=self._request_bell, enabled=SOUND_ENABLED)
        self._tray = TrayIcon("Pomodoro98", "Pomodoro98")

        self.title("Pomodoro98")
        self.configure(bg=WIN98_BG)
        self.resizable(False, False)
        self.attributes("-topmost", True)

        self._load_window_icons()

        # State
        self.timer = TimerModel(FOCUS_MINUTES * 60, REST_MINUTES * 60)
        self._after_id = None
        self._last_view = None
        self._icon_mode = None

        # UI
        self._build_ui()
        self._bell_poll_id = self.after(BELL_POLL_MS, self._process_bell_requests)

        # Tray (optional)
        self._tray.start()
        self._render()

    # ---------- Icons ----------
    def _load_window_icons(self):
        self._icon_focus_img = None
        self._icon_rest_img = None
        self._icon_idle_img = None

        try:
            if ICON_FOCUS_FILE.exists():
                self._icon_focus_img = tk.PhotoImage(file=str(ICON_FOCUS_FILE))
            if ICON_REST_FILE.exists():
                self._icon_rest_img = tk.PhotoImage(file=str(ICON_REST_FILE))
            if ICON_IDLE_FILE.exists():
                self._icon_idle_img = tk.PhotoImage(file=str(ICON_IDLE_FILE))
            if self._icon_focus_img:
                self.iconphoto(False, self._icon_focus_img)
        except Exception:
            LOGGER.exception("Failed to load application icons")

    def _set_mode_icon(self, mode):
        try:
            if mode is Mode.FOCUS and self._icon_focus_img:
                self.iconphoto(False, self._icon_focus_img)
            elif mode is Mode.REST and self._icon_rest_img:
                self.iconphoto(False, self._icon_rest_img)
            elif self._icon_idle_img:
                self.iconphoto(False, self._icon_idle_img)
        except Exception:
            LOGGER.exception("Failed to update the window icon for mode %s", mode)

    # ---------- UI ----------
    def _build_ui(self):
        outer = tk.Frame(self, bg=WIN98_BG, bd=2, relief="ridge")
        outer.grid(padx=10, pady=10)

        titlebar = tk.Frame(outer, bg=WIN98_TITLE_BG, height=22, bd=2, relief="flat")
        titlebar.grid(row=0, column=0, sticky="ew")
        titlebar.grid_columnconfigure(0, weight=1)
        title = tk.Label(titlebar, text="Pomodoro98", fg=WIN98_TITLE_TEXT, bg=WIN98_TITLE_BG,
                         anchor="w", padx=6, font=("MS Sans Serif", 9, "bold"))
        title.grid(row=0, column=0, sticky="ew")

        body = tk.Frame(outer, bg=WIN98_BG, bd=2, relief="flat")
        body.grid(row=1, column=0, padx=8, pady=8)

        clock_frame = tk.Frame(body, bg=WIN98_BG, bd=2, relief="sunken")
        clock_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=2, pady=(0,8))
        self.clock_label = tk.Label(clock_frame,
                                    text="00:00",
                                    font=("MS Sans Serif", 28, "bold"),
                                    bg=WIN98_BG, fg=WIN98_TEXT,
                                    padx=20, pady=8)
        self.clock_label.pack()

        # Progress
        prog_frame = tk.Frame(body, bg=WIN98_BG)
        prog_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,8))
        self.prog_width = 360
        self.prog_height = 22

        groove = tk.Frame(prog_frame, bg=WIN98_BG, bd=2, relief="sunken")
        groove.pack()
        self.canvas = tk.Canvas(groove, width=self.prog_width, height=self.prog_height,
                                highlightthickness=0, bg=WIN98_BG)
        self.canvas.pack()
        self.canvas.create_rectangle(1, 1, self.prog_width-1, self.prog_height-1,
                                     outline=WIN98_DARK, fill=WIN98_LIGHT, width=1, tags="bg")
        self.bar = self.canvas.create_rectangle(2, 2, 2, self.prog_height-2,
                                                outline="", fill=BAR_NORMAL, tags="bar")

        # Buttons
        btns = tk.Frame(body, bg=WIN98_BG)
        btns.grid(row=2, column=0, columnspan=2, pady=(4,0))

        self.start_btn = self._win98_button(btns, "Start", command=self.start)
        self.start_btn.grid(row=0, column=0, padx=4)
        self.reset_btn = self._win98_button(btns, "Reset", command=self.reset)
        self.reset_btn.grid(row=0, column=1, padx=4)

        # Mode label
        self.mode_label = tk.Label(body, text="Mode: Stopped",
                                   font=("MS Sans Serif", 9),
                                   bg=WIN98_BG, fg=WIN98_TEXT)
        self.mode_label.grid(row=3, column=0, columnspan=2, pady=(6,0))

    def _win98_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=WIN98_BG,
            fg=WIN98_TEXT,
            activebackground=WIN98_LIGHT,
            activeforeground=WIN98_TEXT,
            bd=2,
            relief="raised",
            padx=10,
            pady=2,
            font=("MS Sans Serif", 9),
        )

    # ---------- Logic ----------
    def start(self):
        """Start, pause, or resume (the Start/Pause button)."""
        self._play_click_async()
        self.timer.toggle()
        if self.timer.running:
            self._schedule_tick()
        else:
            self._cancel_tick()
        self._render()

    def pause(self):
        """Pause the active session without changing its remaining time."""
        self.timer.pause()
        self._cancel_tick()
        self._render()

    def reset(self):
        """Stop the current session and restore a fresh focus timer."""
        self._play_click_async()
        self._cancel_tick()
        self.timer.reset()
        self._render()

    def _tick(self):
        self._after_id = None
        for event in self.timer.tick():
            self._play_sound_async(EVENT_SOUNDS[event])
        self._render()
        if self.timer.running:
            self._schedule_tick()

    def _schedule_tick(self):
        self._cancel_tick()
        self._after_id = self.after(TICK_MS, self._tick)

    def _cancel_tick(self):
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except tk.TclError:
                LOGGER.debug("Scheduled timer callback was already cancelled")
            self._after_id = None

    # ---------- View ----------
    def _render(self):
        """Redraw only when what the user can see has changed."""
        t = self.timer
        view = (t.mode, t.running, t.completed, t.remaining)
        if view == self._last_view:
            return
        self._last_view = view
        mode, running, completed, remaining = view

        mm, ss = divmod(remaining, 60)
        self.clock_label.config(text=f"{mm:02d}:{ss:02d}")
        self.title(f"Pomodoro98 — {mm:02d}:{ss:02d} [{MODE_TITLES[mode]}]")

        bar_color = BAR_ALERT if (mode is Mode.REST or completed) else BAR_NORMAL
        self._draw_progress(t.progress, bar_color)

        if completed:
            label = CYCLE_COMPLETE_LABEL
        else:
            label = MODE_LABELS[mode]
            if not running and mode is not Mode.STOPPED:
                label += " — Paused"
        self.mode_label.config(text=label)
        self.start_btn.config(text="Pause" if running else "Start")

        if mode is not self._icon_mode:
            self._icon_mode = mode
            self._set_mode_icon(mode)
        self._tray.update(mode.value, remaining)

    def _draw_progress(self, pct, color):
        pct = max(0.0, min(1.0, pct))
        x2 = 2 + int((self.prog_width - 4) * pct)
        self.canvas.coords(self.bar, 2, 2, x2, self.prog_height - 2)
        self.canvas.itemconfig(self.bar, fill=color)

    # ---------- Sound ----------
    def _request_bell(self):
        """Queue a bell for Tk's main thread instead of calling Tk from a worker."""
        if not self._closing:
            self._bell_requests.put(None)

    def _process_bell_requests(self):
        try:
            while True:
                self._bell_requests.get_nowait()
                self.bell()
        except queue.Empty:
            pass
        except tk.TclError:
            LOGGER.debug("Tk bell is unavailable", exc_info=True)
        finally:
            if not self._closing:
                self._bell_poll_id = self.after(
                    BELL_POLL_MS, self._process_bell_requests
                )

    def _play_sound_async(self, path):
        self._sound.play_async(path)

    def _play_click_async(self):
        self._play_sound_async(SOUND_CLICK)

    def shutdown(self):
        """Cancel Tk callbacks and optional integrations before closing."""
        if self._closing:
            return
        self._closing = True
        self.timer.pause()
        for callback_id in (self._after_id, self._bell_poll_id):
            if callback_id:
                try:
                    self.after_cancel(callback_id)
                except tk.TclError:
                    LOGGER.debug("Callback was already cancelled during shutdown")
        self._after_id = None
        self._bell_poll_id = None
        self._tray.stop()
        self._sound.shutdown()
        self.destroy()


# ------------------------------
# Run
# ------------------------------
def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    app = Pomodoro98()
    app.update_idletasks()
    w = app.winfo_width()
    h = app.winfo_height()
    x = (app.winfo_screenwidth() // 2) - (w // 2)
    y = (app.winfo_screenheight() // 3) - (h // 2)
    app.geometry(f"+{x}+{y}")

    app.protocol("WM_DELETE_WINDOW", app.shutdown)
    app.mainloop()
