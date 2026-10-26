#!/usr/bin/env python3
"""Synthesize Pomodoro98's alert sounds from scratch.

Both chimes are generated with plain sine-wave additive synthesis (bell-like
partials with exponential decay); no recordings or samples are used, so the
output is original work released under CC0-1.0. Only the standard library is
needed: ``python3 scripts/build_sounds.py``

- ``focus_end.wav``: a bright rising three-note chime (focus is over, take a break)
- ``reset_end.wav``: a calm two-note "ding-dong" (the break is over, cycle complete)
"""

import math
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOUNDS = ROOT / "src" / "pomodoro98" / "sounds"
RATE = 44100
PEAK = 0.7  # about -3 dBFS

# (frequency ratio, relative amplitude, decay multiplier) of a soft bell.
PARTIALS = ((1.0, 1.0, 1.0), (2.0, 0.35, 1.6), (3.01, 0.15, 2.4), (4.17, 0.06, 3.2))


def bell(freq, start, decay, length, out):
    """Mix one bell strike at ``start`` seconds into the ``out`` sample buffer."""
    first = int(start * RATE)
    for i in range(int(length * RATE)):
        t = i / RATE
        attack = min(1.0, t / 0.004)  # 4 ms fade-in avoids a click
        value = 0.0
        for ratio, amp, speed in PARTIALS:
            value += amp * math.exp(-t * speed / decay) * math.sin(2 * math.pi * freq * ratio * t)
        out[first + i] += attack * value


def render(notes, total):
    """Render (frequency, start, decay) notes into normalized 16-bit samples."""
    buf = [0.0] * int(total * RATE)
    for freq, start, decay in notes:
        bell(freq, start, decay, total - start, buf)
    tail = int(0.05 * RATE)  # fade the last 50 ms to silence
    for i in range(tail):
        buf[-tail + i] *= 1 - i / tail
    scale = PEAK / max(abs(v) for v in buf)
    return [round(v * scale * 32767) for v in buf]


def write(path, samples):
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(struct.pack(f"<{len(samples)}h", *samples))


C5, E5, G5, C6, E6, G6 = 523.25, 659.25, 783.99, 1046.50, 1318.51, 1567.98

FOCUS_END = [(C6, 0.00, 0.45), (E6, 0.16, 0.45), (G6, 0.32, 0.70)]
REST_END = [(E5, 0.00, 0.60), (C5, 0.38, 0.90)]


def main():
    write(SOUNDS / "focus_end.wav", render(FOCUS_END, 1.6))
    write(SOUNDS / "reset_end.wav", render(REST_END, 2.0))
    print("Sounds written to", SOUNDS.relative_to(ROOT))


if __name__ == "__main__":
    main()
