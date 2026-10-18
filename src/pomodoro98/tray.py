"""Optional system tray icon (requires ``pystray`` and ``Pillow``).

Every tray operation is guarded so a missing or broken tray backend can never
stop the timer.
"""

import logging
import threading

LOGGER = logging.getLogger(__name__)

try:
    import pystray
    from PIL import Image, ImageDraw

    TRAY_OK = True
except Exception:
    TRAY_OK = False

# Mode name -> (RGBA fill, label)
_MODE_STYLES = {
    "focus": ((0, 160, 0, 255), "Focus"),
    "rest": ((192, 0, 0, 255), "Rest"),
}
_STOPPED_STYLE = ((128, 128, 128, 255), "Stopped")


def _make_image(color_rgba):
    size = 24
    bg = (192, 192, 192, 255)
    dark = (128, 128, 128, 255)
    light = (255, 255, 255, 255)
    img = Image.new("RGBA", (size, size), bg)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, size - 1, size - 1], outline=dark)
    d.rectangle([1, 1, size - 2, size - 2], outline=light)
    d.rectangle([2, 2, size - 3, size - 3], outline=dark)
    d.rectangle([3, 3, size - 4, size - 4], outline=light)
    pad = 5
    d.rectangle([pad, pad, size - pad - 1, size - pad - 1], fill=(224, 224, 224, 255), outline=dark)
    d.line([pad, pad, size - pad - 1, pad], fill=light)
    d.line([pad, pad, pad, size - pad - 1], fill=light)
    inner_pad = 2
    d.rectangle(
        [pad + inner_pad, pad + inner_pad, size - pad - 1 - inner_pad, size - pad - 1 - inner_pad],
        fill=color_rgba,
    )
    return img


class TrayIcon:
    def __init__(self, name, title):
        self._name = name
        self._title = title
        self._icon = None

    def start(self):
        if not TRAY_OK:
            return
        try:
            self._icon = pystray.Icon(self._name, _make_image((0, 160, 0, 255)), self._title)
            threading.Thread(target=self._icon.run, daemon=True).start()
        except Exception:
            # If tray fails to start, keep going; app should not exit.
            LOGGER.exception("Failed to start system tray integration")
            self._icon = None

    def update(self, mode, remaining):
        """Show ``mode`` ("focus", "rest" or anything else for stopped)."""
        if not self._icon:
            return
        try:
            color, mode_text = _MODE_STYLES.get(mode, _STOPPED_STYLE)
            mm, ss = divmod(remaining, 60)
            self._icon.icon = _make_image(color)
            self._icon.title = f"{mode_text}: {mm:02d}:{ss:02d} remaining"
        except Exception:
            # Never let tray errors kill the app
            LOGGER.exception("Failed to update system tray state")

    def stop(self):
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                LOGGER.exception("Failed to stop system tray integration")
            finally:
                self._icon = None
