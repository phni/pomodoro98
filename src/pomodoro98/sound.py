"""Non-blocking sound playback with optional backends.

Backends are tried in order: simpleaudio, pygame, then the Linux ``aplay``
command. Playback runs on a worker thread so backend errors can never block or
crash Tk's main loop. When no backend can play a file, ``on_failure`` is called
from the worker thread; the caller must marshal any Tk work back to the main
thread itself.
"""

import logging
import subprocess
import threading

LOGGER = logging.getLogger(__name__)

APLAY_TIMEOUT_S = 30

# Optional backends
_SA = None  # simpleaudio
_PYG = None  # pygame (lazy mixer init)

try:
    import simpleaudio as _SA
except Exception:
    _SA = None

try:
    import pygame as _PYG
except Exception:
    _PYG = None


class SoundPlayer:
    def __init__(self, on_failure, enabled=True):
        self._on_failure = on_failure
        self._lock = threading.Lock()
        self.enabled = enabled
        self._closed = False

    def play_async(self, path):
        """Play ``path`` in the background, falling back to ``on_failure``."""
        if not self.enabled or self._closed:
            return

        def run():
            try:
                with self._lock:
                    if path.exists() and self._play_backend(path):
                        return
                self._on_failure()
            except Exception:
                LOGGER.exception("Unexpected sound playback failure: %s", path)
                self._on_failure()

        threading.Thread(target=run, daemon=True, name="pomodoro98-audio").start()

    def shutdown(self):
        self._closed = True
        if _PYG:
            try:
                if _PYG.mixer.get_init():
                    _PYG.mixer.quit()
            except Exception:
                LOGGER.exception("Failed to shut down pygame audio")

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
        # 3) aplay (Linux). Wait for it on this worker thread so a non-zero exit
        # (no audio device, unsupported file) still falls back to the bell.
        try:
            result = subprocess.run(
                ["aplay", "-q", path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=APLAY_TIMEOUT_S,
                check=False,
            )
            if result.returncode == 0:
                return True
            LOGGER.debug("aplay exited with status %s", result.returncode)
        except (OSError, subprocess.SubprocessError):
            LOGGER.debug("aplay playback failed", exc_info=True)
        return False
