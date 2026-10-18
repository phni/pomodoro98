#!/usr/bin/env python3
"""Fail the Flatpak build if the CPython source for tkinter mismatches the runtime.

_tkinter is compiled with CPython's internal headers, so the source release
must match the runtime's Python exactly (ADR 0004). Run from the extracted
CPython source directory.
"""

import re
import sys
from pathlib import Path

source = re.search(
    r'#define\s+PY_VERSION\s+"([^"]+)"', Path("Include/patchlevel.h").read_text()
).group(1)
runtime = sys.version.split()[0]
if source != runtime:
    sys.exit(
        f"Runtime Python is {runtime} but tkinter is built from CPython {source}. "
        "Update the tkinter module source in io.github.phni.Pomodoro98.yml (ADR 0004)."
    )
print(f"tkinter source matches runtime Python {runtime}")
