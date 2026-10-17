#!/usr/bin/env python3
"""Fail if the package version and the newest MetaInfo release disagree.

``pomodoro98.__version__`` is the single source of truth for the version;
``pyproject.toml`` reads it, and the Flatpak MetaInfo must list it as the
newest ``<release>``.
"""

import ast
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INIT = ROOT / "src" / "pomodoro98" / "__init__.py"
METAINFO = ROOT / "flatpak" / "io.github.phni.Pomodoro98.metainfo.xml"


def package_version():
    for node in ast.parse(INIT.read_text()).body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "__version__" for t in node.targets
        ):
            return ast.literal_eval(node.value)
    sys.exit(f"__version__ not found in {INIT}")


def metainfo_version():
    release = ET.parse(METAINFO).find("./releases/release")
    if release is None:
        sys.exit(f"No <release> in {METAINFO}")
    return release.get("version")


def main():
    pkg, meta = package_version(), metainfo_version()
    if pkg != meta:
        sys.exit(f"Version mismatch: __version__ is {pkg}, newest MetaInfo release is {meta}")
    print(f"Version check passed: {pkg}")


if __name__ == "__main__":
    main()
