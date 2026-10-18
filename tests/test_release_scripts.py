"""Release tooling: version/tag checks and CHANGELOG release notes."""

import importlib.util
from pathlib import Path

import pytest

import pomodoro98

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check_version = load("check_version")
release_notes = load("release_notes")

CHANGELOG = """# Changelog

## [Unreleased]

## [2026.11.0] - 2026-11-02

### Fixed

- Something.

## [2026.10.0] - 2026-10-18

### Added

- First thing.

[Unreleased]: https://example.invalid/compare/v2026.11.0...HEAD
[2026.11.0]: https://example.invalid/compare/v2026.10.0...v2026.11.0
"""


def test_matching_tag_passes(capsys):
    check_version.main(["--tag", f"v{pomodoro98.__version__}"])
    assert "Version check passed" in capsys.readouterr().out


def test_without_tag_checks_package_and_metainfo():
    check_version.main([])


@pytest.mark.parametrize("tag", ["v0.0.1", pomodoro98.__version__, "release"])
def test_wrong_tag_fails(tag):
    with pytest.raises(SystemExit, match="tag is"):
        check_version.main(["--tag", tag])


def test_extracts_middle_section():
    assert release_notes.extract(CHANGELOG, "2026.11.0") == "### Fixed\n\n- Something."


def test_extracts_last_section_before_links():
    assert release_notes.extract(CHANGELOG, "2026.10.0") == "### Added\n\n- First thing."


def test_version_dots_are_literal():
    assert release_notes.extract(CHANGELOG, "2026x10x0") is None


def test_empty_or_missing_section_fails(tmp_path):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(CHANGELOG)
    with pytest.raises(SystemExit, match="No CHANGELOG.md section"):
        release_notes.main(["Unreleased", "--changelog", str(changelog)])
    with pytest.raises(SystemExit, match="No CHANGELOG.md section"):
        release_notes.main(["1999.1.0", "--changelog", str(changelog)])


def test_real_changelog_has_notes_for_current_version(capsys):
    release_notes.main([pomodoro98.__version__])
    assert capsys.readouterr().out.strip()
