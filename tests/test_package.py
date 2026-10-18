"""Package-level checks: metadata, entry points, and shipped assets."""

import importlib
import xml.etree.ElementTree as ET
from pathlib import Path

import pomodoro98

ROOT = Path(__file__).resolve().parent.parent
METAINFO = ROOT / "flatpak" / "io.github.phni.Pomodoro98.metainfo.xml"


def test_version_matches_newest_metainfo_release():
    release = ET.parse(METAINFO).find("./releases/release")
    assert release.get("version") == pomodoro98.__version__


def test_console_entry_point_is_importable():
    app = importlib.import_module("pomodoro98.app")
    assert callable(app.main)


def test_assets_ship_with_the_package():
    app = importlib.import_module("pomodoro98.app")
    for path in (
        app.SOUND_FOCUS_END,
        app.SOUND_REST_END,
        app.ICON_FOCUS_FILE,
        app.ICON_REST_FILE,
        app.ICON_IDLE_FILE,
    ):
        assert path.is_file(), path
