import tkinter as tk
import time

# ------------------------------
# Config (change these if you like)
# ------------------------------
FOCUS_MINUTES = 25       # default focus length
REST_MINUTES  = 5        # default rest length
TICK_MS = 1000           # update rate (ms)
UI_SCALE = 0.5       # UI scaling factor (1.0 = normal size)

# Win98-esque palette
WIN98_BG         = "#C0C0C0"
WIN98_DARK       = "#808080"
WIN98_LIGHT      = "#FFFFFF"
WIN98_TEXT       = "#000000"
WIN98_TITLE_BG   = "#000080"
WIN98_TITLE_TEXT = "#FFFFFF"

BAR_NORMAL = "#00A000"   # green-ish for focus
BAR_ALERT  = "#C00000"   # red for overtime/rest

# ------------------------------
# App
# ------------------------------
class Pomodoro98(tk.Tk):
    def __init__(self):
        super().__init__()
        # Apply global UI scaling
        self.tk.call('tk', 'scaling', UI_SCALE)

        self.title("Pomodoro 98")
        self.configure(bg=WIN98_BG)
        self.resizable(False, False)

        # Always on top
        self.attributes("-topmost", True)
        
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

    # ---------- UI ----------
    def _build_ui(self):
        # Outer frame with 3D ridge like Win98 dialog
        outer = tk.Frame(self, bg=WIN98_BG, bd=2, relief="ridge")
        outer.grid(padx=10, pady=10)

        # Fake title bar
        titlebar = tk.Frame(outer, bg=WIN98_TITLE_BG, height=22, bd=2, relief="flat")
        titlebar.grid(row=0, column=0, sticky="ew")
        titlebar.grid_columnconfigure(0, weight=1)
        title = tk.Label(titlebar, text="Pomodoro 98", fg=WIN98_TITLE_TEXT, bg=WIN98_TITLE_BG,
                         anchor="w", padx=6, font=("MS Sans Serif", 9, "bold"))
        title.grid(row=0, column=0, sticky="ew")

        # Body frame with classic 3D sunken groups
        body = tk.Frame(outer, bg=WIN98_BG, bd=2, relief="flat")
        body.grid(row=1, column=0, padx=8, pady=8)

        # Clock panel (rectangular "digital" display)
        clock_frame = tk.Frame(body, bg=WIN98_BG, bd=2, relief="sunken")
        clock_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=2, pady=(0,8))
        self.clock_label = tk.Label(clock_frame,
                                    text="00:00",
                                    font=("MS Sans Serif", 28, "bold"),
                                    bg=WIN98_BG, fg=WIN98_TEXT,
                                    padx=20, pady=8)
        self.clock_label.pack()

        # Progress bar (custom canvas to control exact colors)
        prog_frame = tk.Frame(body, bg=WIN98_BG)
        prog_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,8))
        self.prog_width = int(360 * UI_SCALE)
        self.prog_height = int(20 * UI_SCALE)

        # 3D groove border
        groove = tk.Frame(prog_frame, bg=WIN98_BG, bd=2, relief="sunken")
        groove.pack()
        self.canvas = tk.Canvas(groove, width=self.prog_width, height=self.prog_height,
                                highlightthickness=0, bg=WIN98_BG)
        self.canvas.pack()
        # Background box to mimic Win98 loading bar
        self.canvas.create_rectangle(1, 1, self.prog_width-1, self.prog_height-1,
                                     outline=WIN98_DARK, fill=WIN98_LIGHT, width=1, tags="bg")
        self.bar = self.canvas.create_rectangle(2, 2, 2, self.prog_height-2,
                                                outline="", fill=BAR_NORMAL, tags="bar")

        # Buttons
        btns = tk.Frame(body, bg=WIN98_BG)
        btns.grid(row=2, column=0, columnspan=2, pady=(4,0))

        self.start_btn = self._win98_button(btns, "Start", command=self.start)
        self.start_btn.grid(row=0, column=0, padx=4)
        self.stop_btn  = self._win98_button(btns, "Stop", command=self.stop)
        self.stop_btn.grid(row=0, column=1, padx=4)

        # Mode label
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
        if not self._running:
            if self.mode == "stopped":
                self._switch_mode("focus")
            self._running = True
            self._tick()

    def stop(self):
        self._running = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
        self.mode = "stopped"
        self.mode_label.config(text="Mode: Stopped")
        # Reset to a fresh focus session
        self.total_seconds = FOCUS_MINUTES * 60
        self.remaining = self.total_seconds
        self._update_clock_text(self.remaining)
        self._draw_progress(0.0, BAR_NORMAL)

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
            # Whole rest uses red bar
            self._draw_progress(0.0, BAR_ALERT)

        self._update_clock_text(self.remaining)

    def _tick(self):
        # Called every TICK_MS while running
        if not self._running:
            return

        if self.remaining > 0:
            self.remaining -= 1
            self._update_clock_text(self.remaining)

            # progress percent increases from 0 -> 1 during each mode
            elapsed = self.total_seconds - self.remaining
            pct = elapsed / max(1, self.total_seconds)

            # Color logic:
            # - focus: green until time hits 0 (handled below)
            # - rest: red the whole time
            bar_color = BAR_ALERT if self.mode == "rest" else BAR_NORMAL
            self._draw_progress(pct, bar_color)

            self._after_id = self.after(TICK_MS, self._tick)
        else:
            # Time's up for current mode
            self._update_clock_text(0)
            # Turn the progress bar red immediately at end of focus
            self._draw_progress(1.0, BAR_ALERT)

            if self.mode == "focus":
                # Auto-switch to rest
                self._switch_mode("rest")
                self._after_id = self.after(TICK_MS, self._tick)
            elif self.mode == "rest":
                # End of cycle: stop running but keep red bar (time up)
                self._running = False
                self.mode_label.config(text="Mode: Cycle Complete (Stopped)")

    # ---------- Helpers ----------
    def _update_clock_text(self, seconds):
        mm = seconds // 60
        ss = seconds % 60
        self.clock_label.config(text=f"{mm:02d}:{ss:02d}")
        #self.title(f"Pomodoro 98 — {mm:02d}:{ss:02d} [{ 'Focus' if self.mode=='focus' else ('Rest' if self.mode=='rest' else 'Stopped') }]")

    def _draw_progress(self, pct, color):
        # Clamp
        pct = max(0.0, min(1.0, pct))
        x2 = 2 + int((self.prog_width - 4) * pct)  # inside stroke
        # Update bar
        self.canvas.coords(self.bar, 2, 2, x2, self.prog_height - 2)
        self.canvas.itemconfig(self.bar, fill=color)

# ------------------------------
# Run
# ------------------------------
if __name__ == "__main__":
    app = Pomodoro98()
    # Center the window a bit
    app.update_idletasks()
    w = app.winfo_width()
    h = app.winfo_height()
    x = (app.winfo_screenwidth() // 2) - (w // 2)
    y = (app.winfo_screenheight() // 3) - (h // 2)
    app.geometry(f"+{x}+{y}")
    app.mainloop()
