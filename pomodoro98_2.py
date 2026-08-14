#!/usr/bin/env python3
"""
Pomodoro 98 — Win98-styled Pomodoro timer (hardened)

- Start/Pause and Reset buttons (with click beep)
- Progress bar: green during focus; red when time is up and during rest
- Always-on-top window
- Title shows remaining time + mode (visible on taskbar)
- Optional system tray icon (green/red) with live-updating tooltip
- Sounds:
    * focus_end.wav when focus ends (work -> rest)
    * reset_end.wav when rest ends (cycle complete)
    * click.wav on Start/Stop (optional; falls back to bell)

HARDENING:
- All sound playback done in a background thread with try/except
  so backend errors can’t kill Tk’s mainloop.
- Robust guards around tray updates.

Sound backends tried in order (non-blocking):
  simpleaudio -> pygame -> system 'aplay' -> Tk bell

Optional installs:
    pip install pystray pillow
    pip install simpleaudio   # OR
    pip install pygame

Assets:
  icons/: icon.png, icon_rest.png, icon_idle.png, icon.ico
  sounds/: focus_end.wav, reset_end.wav, click.wav (optional)
"""

import logging
import queue
import subprocess
import threading
import tkinter as tk
from pathlib import Path

# ---------- Optional deps ----------
# Tray (optional)
try:
    import pystray
    from PIL import Image, ImageDraw
    _TRAY_OK = True
except Exception:
    _TRAY_OK = False

# Sound backends (optional)
_SA = None      # simpleaudio
_PYG = None     # pygame (lazy mixer init)

try:
    import simpleaudio as _SA
except Exception:
    _SA = None

try:
    import pygame as _PYG
except Exception:
    _PYG = None

# ------------------------------
# Config
# ------------------------------
FOCUS_MINUTES = 25
REST_MINUTES = 5
TICK_MS = 1000
BELL_POLL_MS = 100

APP_DIR = Path(__file__).resolve().parent
LOGGER = logging.getLogger("pomodoro98")
APP_VERSION = "0.1.0"

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

# Icons
ICONS_DIR = APP_DIR / "icons"
ICON_FOCUS_FILE = ICONS_DIR / "icon.png"
ICON_REST_FILE = ICONS_DIR / "icon_rest.png"
ICON_IDLE_FILE = ICONS_DIR / "icon_idle.png"
ICON_ICO_FILE = ICONS_DIR / "icon.ico"


class Pomodoro98(tk.Tk):
    def __init__(self):
        super().__init__()
        # define tray_icon early so attribute always exists
        self.tray_icon = None
        self._closing = False
        self._bell_requests = queue.SimpleQueue()
        self._sound_lock = threading.Lock()

        self.title("Pomodoro 98")
        self.configure(bg=WIN98_BG)
        self.resizable(False, False)
        self.attributes("-topmost", True)

        self._load_window_icons()

        # State
        self.mode = "stopped"  # 'focus', 'rest', 'stopped'
        self.total_seconds = FOCUS_MINUTES * 60
        self.remaining = self.total_seconds
        self._running = False
        self._after_id = None

        # UI
        self._build_ui()
        self._update_clock_text(self.remaining)
        self._draw_progress(0.0, BAR_NORMAL)
        self._set_mode_icon()
        self._bell_poll_id = self.after(BELL_POLL_MS, self._process_bell_requests)

        # Tray (optional)
        if _TRAY_OK:
            self._start_tray_icon()
            self._update_tray()

    # ---------- Icons ----------
    def _load_window_icons(self):
        self._icon_focus_img = None
        self._icon_rest_img = None
        self._icon_idle_img = None

        if ICON_ICO_FILE.exists():
            try:
                self.iconbitmap(str(ICON_ICO_FILE))
            except Exception:
                LOGGER.exception("Failed to load window icon: %s", ICON_ICO_FILE)

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

    def _set_mode_icon(self):
        try:
            if self.mode == "focus" and self._icon_focus_img:
                self.iconphoto(False, self._icon_focus_img)
            elif self.mode == "rest" and self._icon_rest_img:
                self.iconphoto(False, self._icon_rest_img)
            elif self._icon_idle_img:
                self.iconphoto(False, self._icon_idle_img)
        except Exception:
            LOGGER.exception("Failed to update the window icon for mode %s", self.mode)

    # ---------- UI ----------
    def _build_ui(self):
        outer = tk.Frame(self, bg=WIN98_BG, bd=2, relief="ridge")
        outer.grid(padx=10, pady=10)

        titlebar = tk.Frame(outer, bg=WIN98_TITLE_BG, height=22, bd=2, relief="flat")
        titlebar.grid(row=0, column=0, sticky="ew")
        titlebar.grid_columnconfigure(0, weight=1)
        title = tk.Label(titlebar, text="Pomodoro 98", fg=WIN98_TITLE_TEXT, bg=WIN98_TITLE_BG,
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
        self._play_click_async()

        if self._running:
            self.pause()
            return

        if self.mode == "stopped":
            self._switch_mode("focus")
        self._running = True
        self.start_btn.config(text="Pause")
        self._set_mode_label()
        self._after_id = self.after(TICK_MS, self._tick)

    def pause(self):
        """Pause the active session without changing its remaining time."""
        if not self._running:
            return

        self._running = False
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except tk.TclError:
                LOGGER.debug("Scheduled timer callback was already cancelled")
            self._after_id = None
        self.start_btn.config(text="Start")
        self._set_mode_label(paused=True)
        self._update_tray()

    def reset(self):
        """Stop the current session and restore a fresh focus timer."""
        self._play_click_async()
        self._running = False
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except tk.TclError:
                LOGGER.debug("Scheduled timer callback was already cancelled")
            self._after_id = None
        self.mode = "stopped"
        self.start_btn.config(text="Start")
        self.mode_label.config(text="Mode: Stopped")
        self.total_seconds = FOCUS_MINUTES * 60
        self.remaining = self.total_seconds
        self._update_clock_text(self.remaining)
        self._draw_progress(0.0, BAR_NORMAL)
        self._set_mode_icon()
        self._update_tray()

    def _set_mode_label(self, paused=False):
        if self.mode == "focus":
            text = "Mode: Focus (Work)"
        elif self.mode == "rest":
            text = "Mode: Rest"
        else:
            text = "Mode: Stopped"
        if paused and self.mode != "stopped":
            text += " — Paused"
        self.mode_label.config(text=text)

    def _switch_mode(self, new_mode):
        self.mode = new_mode
        if new_mode == "focus":
            self.total_seconds = FOCUS_MINUTES * 60
            self.remaining = self.total_seconds
            self._draw_progress(0.0, BAR_NORMAL)
        elif new_mode == "rest":
            self.total_seconds = REST_MINUTES * 60
            self.remaining = self.total_seconds
            self._draw_progress(0.0, BAR_ALERT)

        self._set_mode_label()
        self._update_clock_text(self.remaining)
        self._set_mode_icon()
        self._update_tray()

    def _tick(self):
        if not self._running:
            return

        if self.remaining > 0:
            self.remaining -= 1
            self._update_clock_text(self.remaining)
            elapsed = self.total_seconds - self.remaining
            pct = elapsed / max(1, self.total_seconds)
            bar_color = BAR_ALERT if self.mode == "rest" else BAR_NORMAL
            self._draw_progress(pct, bar_color)
            self._after_id = self.after(TICK_MS, self._tick)
        else:
            # time up for current mode
            self._update_clock_text(0)
            self._draw_progress(1.0, BAR_ALERT)

            if self.mode == "focus":
                # play in background; never block or crash UI
                self._play_event_async("focus_end")
                self._switch_mode("rest")
                self._after_id = self.after(TICK_MS, self._tick)
            elif self.mode == "rest":
                self._play_event_async("rest_end")
                self._running = False
                self.mode = "stopped"
                self.start_btn.config(text="Start")
                self.mode_label.config(text="Mode: Cycle Complete (Stopped)")
                self._set_mode_icon()
                self._update_tray()

    # ---------- Helpers ----------
    def _update_clock_text(self, seconds):
        mm = seconds // 60
        ss = seconds % 60
        self.clock_label.config(text=f"{mm:02d}:{ss:02d}")
        mode_text = "Focus" if self.mode == "focus" else ("Rest" if self.mode == "rest" else "Stopped")
        self.title(f"Pomodoro 98 — {mm:02d}:{ss:02d} [{mode_text}]")
        self._update_tray()

    def _draw_progress(self, pct, color):
        pct = max(0.0, min(1.0, pct))
        x2 = 2 + int((self.prog_width - 4) * pct)
        self.canvas.coords(self.bar, 2, 2, x2, self.prog_height - 2)
        self.canvas.itemconfig(self.bar, fill=color)

    # ---------- Sound (threaded) ----------
    def _ensure_pygame(self):
        if _PYG:
            try:
                if not _PYG.mixer.get_init():
                    _PYG.mixer.init()
                return True
            except Exception:
                return False
        return False

    def _play_backend(self, path):
        path = str(path)
        # 1) simpleaudio
        if _SA:
            try:
                wave = _SA.WaveObject.from_wave_file(path)
                wave.play()  # non-blocking
                return True
            except Exception:
                LOGGER.debug("simpleaudio playback failed", exc_info=True)
        # 2) pygame
        if self._ensure_pygame():
            try:
                snd = _PYG.mixer.Sound(path)
                snd.play()
                return True
            except Exception:
                LOGGER.debug("pygame playback failed", exc_info=True)
        # 3) aplay (Linux)
        try:
            subprocess.Popen(
                ["aplay", "-q", path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except (OSError, subprocess.SubprocessError):
            LOGGER.debug("aplay playback failed", exc_info=True)
        return False

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
        if not SOUND_ENABLED or self._closing:
            return

        def run():
            try:
                with self._sound_lock:
                    if path.exists() and self._play_backend(path):
                        return
                self._request_bell()
            except Exception:
                LOGGER.exception("Unexpected sound playback failure: %s", path)
                self._request_bell()

        threading.Thread(target=run, daemon=True, name="pomodoro98-audio").start()

    def _play_click_async(self):
        self._play_sound_async(SOUND_CLICK)

    def _play_event_async(self, which):
        path = SOUND_FOCUS_END if which == "focus_end" else SOUND_REST_END
        self._play_sound_async(path)

    # ---------- System Tray (optional) ----------
    def _make_tray_image(self, color_rgba):
        if not _TRAY_OK:
            return None
        size = 24
        bg = (192, 192, 192, 255)
        dark = (128, 128, 128, 255)
        light = (255, 255, 255, 255)
        img = Image.new("RGBA", (size, size), bg)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, size-1, size-1], outline=dark)
        d.rectangle([1, 1, size-2, size-2], outline=light)
        d.rectangle([2, 2, size-3, size-3], outline=dark)
        d.rectangle([3, 3, size-4, size-4], outline=light)
        pad = 5
        d.rectangle([pad, pad, size-pad-1, size-pad-1], fill=(224,224,224,255), outline=dark)
        d.line([pad, pad, size-pad-1, pad], fill=light)
        d.line([pad, pad, pad, size-pad-1], fill=light)
        inner_pad = 2
        d.rectangle([pad+inner_pad, pad+inner_pad, size-pad-1-inner_pad, size-pad-1-inner_pad],
                    fill=color_rgba)
        return img

    def _start_tray_icon(self):
        try:
            img = self._make_tray_image((0, 160, 0, 255))
            self.tray_icon = pystray.Icon("Pomodoro98", img, "Pomodoro 98")
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception:
            # If tray fails to start, keep going; app should not exit.
            LOGGER.exception("Failed to start system tray integration")
            self.tray_icon = None

    def _update_tray(self):
        if not _TRAY_OK:
            return
        tray = getattr(self, "tray_icon", None)
        if not tray:
            return
        try:
            if self.mode == "rest":
                color = (192, 0, 0, 255); mode_text = "Rest"
            elif self.mode == "focus":
                color = (0, 160, 0, 255); mode_text = "Focus"
            else:
                color = (128, 128, 128, 255); mode_text = "Stopped"

            mm = self.remaining // 60
            ss = self.remaining % 60
            tray.icon = self._make_tray_image(color)
            tray.title = f"{mode_text}: {mm:02d}:{ss:02d} remaining"
        except Exception:
            # Never let tray errors kill the app
            LOGGER.exception("Failed to update system tray state")

    def _shutdown_tray(self):
        tray = getattr(self, "tray_icon", None)
        if tray:
            try:
                tray.stop()
            except Exception:
                LOGGER.exception("Failed to stop system tray integration")
            finally:
                self.tray_icon = None

    def shutdown(self):
        """Cancel Tk callbacks and optional integrations before closing."""
        if self._closing:
            return
        self._closing = True
        self._running = False
        for callback_id in (self._after_id, self._bell_poll_id):
            if callback_id:
                try:
                    self.after_cancel(callback_id)
                except tk.TclError:
                    LOGGER.debug("Callback was already cancelled during shutdown")
        self._after_id = None
        self._bell_poll_id = None
        self._shutdown_tray()
        if _PYG:
            try:
                if _PYG.mixer.get_init():
                    _PYG.mixer.quit()
            except Exception:
                LOGGER.exception("Failed to shut down pygame audio")
        self.destroy()


# ------------------------------
# Run
# ------------------------------
if __name__ == "__main__":
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

    def on_close():
        # Only on window X; Stop button never closes the app
        app.shutdown()

    app.protocol("WM_DELETE_WINDOW", on_close)
    app.mainloop()
