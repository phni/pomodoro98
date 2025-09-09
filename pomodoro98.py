#!/usr/bin/env python3
"""
Pomodoro 98 — Win98-styled Pomodoro timer

Features:
- Start/Stop buttons (with click beep)
- Progress bar (green during focus, red when time is up and during rest)
- Always-on-top window
- Window title shows remaining time + mode (visible on taskbar)
- Optional system tray icon (green/red) with live-updating tooltip
- Sounds:
    * focus_end.wav when focus ends (work -> rest)
    * rest_end.wav when rest ends (cycle complete)
    * click.wav on Start/Stop (optional; falls back to bell)

Audio fallback chain (in order): simpleaudio -> pygame -> system `aplay` -> Tk bell

Optional installs:
    pip install pystray pillow
    pip install simpleaudio   # OR
    pip install pygame        # (if you want to avoid compiling simpleaudio)

Project assets:
    icons/
      icon.png (focus), icon_rest.png (rest), icon_idle.png (stopped), icon.ico (Windows)
    sounds/
      focus_end.wav, rest_end.wav, click.wav (optional)
"""

import os
import shlex
import subprocess
import threading
import tkinter as tk

# ---------- Optional deps ----------
# Tray (optional)
try:
    import pystray
    from PIL import Image, ImageDraw
    _TRAY_OK = True
except Exception:
    _TRAY_OK = False

# Sound backends (all optional)
_SA = None      # simpleaudio
_PYG = None     # pygame (lazy mixer init)

try:
    import simpleaudio as _SA          # may fail to build on some systems
except Exception:
    _SA = None

try:
    import pygame as _PYG              # we'll init mixer lazily
except Exception:
    _PYG = None

# ------------------------------
# Config (tweak to taste)
# ------------------------------
FOCUS_MINUTES = 25
REST_MINUTES  = 5
TICK_MS       = 1000
UI_SCALE      = 0.66    # UI scaling factor (1.0 = normal size)

# Sounds
SOUND_ENABLED     = True
SOUNDS_DIR        = "sounds"
SOUND_FOCUS_END   = os.path.join(SOUNDS_DIR, "focus_end.wav")
SOUND_REST_END    = os.path.join(SOUNDS_DIR, "rest_end.wav")
SOUND_CLICK       = os.path.join(SOUNDS_DIR, "click.wav")   # optional

# Win98-esque palette
WIN98_BG         = "#C0C0C0"
WIN98_DARK       = "#808080"
WIN98_LIGHT      = "#FFFFFF"
WIN98_TEXT       = "#000000"
WIN98_TITLE_BG   = "#000080"
WIN98_TITLE_TEXT = "#FFFFFF"

BAR_NORMAL = "#00A000"   # green-ish for focus
BAR_ALERT  = "#C00000"   # red for overtime/rest

# Icons (optional)
ICONS_DIR       = "icons"
ICON_FOCUS_FILE = os.path.join(ICONS_DIR, "icon.png")
ICON_REST_FILE  = os.path.join(ICONS_DIR, "icon_rest.png")
ICON_IDLE_FILE  = os.path.join(ICONS_DIR, "icon_idle.png")
ICON_ICO_FILE   = os.path.join(ICONS_DIR, "icon.ico")   # Windows best


class Pomodoro98(tk.Tk):
    def __init__(self):
        super().__init__()

        # ---- define tray_icon EARLY to avoid AttributeError ----
        self.tray_icon = None

        self.title("Pomodoro 98")
        self.configure(bg=WIN98_BG)
        self.resizable(False, False)

        # Always on top
        self.attributes("-topmost", True)

        # Try to set a taskbar/window icon
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

        # System tray (optional)
        if _TRAY_OK:
            self._start_tray_icon()
            self._update_tray()

    # ---------- Icons ----------
    def _load_window_icons(self):
        self._icon_focus_img = None
        self._icon_rest_img = None
        self._icon_idle_img = None

        if os.path.exists(ICON_ICO_FILE):
            try:
                self.iconbitmap(ICON_ICO_FILE)
            except Exception:
                pass

        try:
            if os.path.exists(ICON_FOCUS_FILE):
                self._icon_focus_img = tk.PhotoImage(file=ICON_FOCUS_FILE)
            if os.path.exists(ICON_REST_FILE):
                self._icon_rest_img = tk.PhotoImage(file=ICON_REST_FILE)
            if os.path.exists(ICON_IDLE_FILE):
                self._icon_idle_img = tk.PhotoImage(file=ICON_IDLE_FILE)
            if self._icon_focus_img:
                self.iconphoto(False, self._icon_focus_img)
        except Exception as e:
            print("Icon load failed:", e)

    def _set_mode_icon(self):
        try:
            if self.mode == "focus" and self._icon_focus_img:
                self.iconphoto(False, self._icon_focus_img)
            elif self.mode == "rest" and self._icon_rest_img:
                self.iconphoto(False, self._icon_rest_img)
            elif self._icon_idle_img:
                self.iconphoto(False, self._icon_idle_img)
        except Exception as e:
            print("Icon swap failed:", e)

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

        prog_frame = tk.Frame(body, bg=WIN98_BG)
        prog_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,8))
        self.prog_width = 360 * UI_SCALE
        self.prog_height = 22 * UI_SCALE

        groove = tk.Frame(prog_frame, bg=WIN98_BG, bd=2, relief="sunken")
        groove.pack()
        self.canvas = tk.Canvas(groove, width=self.prog_width, height=self.prog_height,
                                highlightthickness=0, bg=WIN98_BG)
        self.canvas.pack()
        self.canvas.create_rectangle(1, 1, self.prog_width-1, self.prog_height-1,
                                     outline=WIN98_DARK, fill=WIN98_LIGHT, width=1, tags="bg")
        self.bar = self.canvas.create_rectangle(2, 2, 2, self.prog_height-2,
                                                outline="", fill=BAR_NORMAL, tags="bar")

        btns = tk.Frame(body, bg=WIN98_BG)
        btns.grid(row=2, column=0, columnspan=2, pady=(4,0))

        self.start_btn = self._win98_button(btns, "Start", command=self.start)
        self.start_btn.grid(row=0, column=0, padx=4)
        self.stop_btn  = self._win98_button(btns, "Stop", command=self.stop)
        self.stop_btn.grid(row=0, column=1, padx=4)

        self.mode_label = tk.Label(body, text="Mode: Stopped",
                                   font=("MS Sans Serif", 9),
                                   bg=WIN98_BG, fg=WIN98_TEXT)
        self.mode_label.grid(row=3, column=0, columnspan=2, pady=(6,0))

    def _win98_button(self, parent, text, command):
        f = tk.Frame(parent, bg=WIN98_BG, bd=1, relief="raised")
        b = tk.Button(f, text=text, command=command,
                      bg=WIN98_BG, fg=WIN98_TEXT,
                      activebackground=WIN98_LIGHT, activeforeground=WIN98_TEXT,
                      bd=0, padx=10, pady=2,
                      font=("MS Sans Serif", 9))
        b.pack()
        return f

    # ---------- Logic ----------
    def start(self):
        # 🔔 click beep or click.wav
        self._play_click()

        if not self._running:
            if self.mode == "stopped":
                self._switch_mode("focus")
            self._running = True
            self._tick()

    def stop(self):
        # 🔔 click beep or click.wav
        self._play_click()

        self._running = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
        self.mode = "stopped"
        self.mode_label.config(text="Mode: Stopped")
        self.total_seconds = FOCUS_MINUTES * 60
        self.remaining = self.total_seconds
        self._update_clock_text(self.remaining)
        self._draw_progress(0.0, BAR_NORMAL)
        self._set_mode_icon()
        self._update_tray()

    def _switch_mode(self, new_mode):
        self.mode = new_mode
        if new_mode == "focus":
            self.total_seconds = FOCUS_MINUTES * 60
            self.remaining = self.total_seconds
            self.mode_label.config(text="Mode: Focus (Work)")
            self._draw_progress(0.0, BAR_NORMAL)
        elif new_mode == "rest":
            self.total_seconds = REST_MINUTES * 60
            self.remaining = self.total_seconds
            self.mode_label.config(text="Mode: Rest")
            self._draw_progress(0.0, BAR_ALERT)

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
                self._play_event_sound("focus_end")   # 🔊 Focus ended
                self._switch_mode("rest")
                self._after_id = self.after(TICK_MS, self._tick)
            elif self.mode == "rest":
                self._play_event_sound("rest_end")    # 🔊 Rest ended
                self._running = False
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

    # ---------- Sound helpers ----------
    def _ensure_pygame(self):
        """Lazy-init pygame mixer the first time we need it."""
        if _PYG:
            try:
                if not _PYG.mixer.get_init():
                    _PYG.mixer.init()
                return True
            except Exception:
                return False
        return False

    def _play_backend(self, path):
        """Try simpleaudio, then pygame, then aplay. Return True if started."""
        # 1) simpleaudio
        if _SA:
            try:
                wave = _SA.WaveObject.from_wave_file(path)
                wave.play()  # non-blocking
                return True
            except Exception:
                pass
        # 2) pygame
        if self._ensure_pygame():
            try:
                snd = _PYG.mixer.Sound(path)
                snd.play()
                return True
            except Exception:
                pass
        # 3) aplay (Linux)
        try:
            subprocess.Popen(
                shlex.split(f"aplay -q {shlex.quote(path)}"),
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return True
        except Exception:
            pass
        return False

    def _play_click(self):
        """Play click.wav if it exists, else fall back to bell()."""
        if not SOUND_ENABLED:
            return
        played = False
        if os.path.exists(SOUND_CLICK):
            played = self._play_backend(SOUND_CLICK)
        if not played:
            try:
                self.bell()
            except Exception:
                pass

    def _play_event_sound(self, which):
        """Play focus_end/rest_end, else bell()."""
        if not SOUND_ENABLED:
            return
        path = SOUND_FOCUS_END if which == "focus_end" else SOUND_REST_END
        played = False
        if os.path.exists(path):
            played = self._play_backend(path)
        if not played:
            try:
                self.bell()
            except Exception:
                pass

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
        img = self._make_tray_image((0, 160, 0, 255))   # green focus default
        self.tray_icon = pystray.Icon("Pomodoro98", img, "Pomodoro 98")
        t = threading.Thread(target=self.tray_icon.run, daemon=True)
        t.start()

    def _update_tray(self):
        # robust guard: use getattr to avoid AttributeError during early init
        if not _TRAY_OK:
            return
        tray = getattr(self, "tray_icon", None)
        if not tray:
            return

        if self.mode == "rest":
            color = (192, 0, 0, 255); mode_text = "Rest"
        elif self.mode == "focus":
            color = (0, 160, 0, 255); mode_text = "Focus"
        else:
            color = (128, 128, 128, 255); mode_text = "Stopped"

        mm = self.remaining // 60
        ss = self.remaining % 60
        title = f"{mode_text}: {mm:02d}:{ss:02d} remaining"
        try:
            tray.icon = self._make_tray_image(color)
            tray.title = title
        except Exception:
            pass

    def _shutdown_tray(self):
        if _TRAY_OK:
            tray = getattr(self, "tray_icon", None)
            if tray:
                try:
                    tray.stop()
                except Exception:
                    pass


# ------------------------------
# Run
# ------------------------------
if __name__ == "__main__":
    app = Pomodoro98()
    app.update_idletasks()
    w = app.winfo_width()
    h = app.winfo_height()
    x = (app.winfo_screenwidth() // 2) - (w // 2)
    y = (app.winfo_screenheight() // 3) - (h // 2)
    app.geometry(f"+{x}+{y}")

    def on_close():
        app._shutdown_tray()
        app.destroy()
    app.protocol("WM_DELETE_WINDOW", on_close)
    app.mainloop()
