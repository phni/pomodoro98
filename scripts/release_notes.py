#!/usr/bin/env python3
"""Print the CHANGELOG.md section for one version, for use as release notes.

Exits with an error if the version has no section or the section is empty, so
a release is never published without notes.
"""

import argparse
import re
import sys
from pathlib import Path

CHANGELOG = Path(__file__).resolve().parent.parent / "CHANGELOG.md"


def extract(text, version):
    """Return the body of the ``## [version]`` section, without its heading."""
    heading = re.compile(rf"^## \[{re.escape(version)}\][^\n]*$", re.MULTILINE)
    match = heading.search(text)
    if not match:
        return None
    rest = text[match.end() :]
    end = re.search(r"^## \[|^\[[^\]]+\]: ", rest, re.MULTILINE)
    return rest[: end.start() if end else len(rest)].strip()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("version", help="version without the v prefix, e.g. 2026.10.0")
    parser.add_argument("--changelog", type=Path, default=CHANGELOG)
    args = parser.parse_args(argv)

    notes = extract(args.changelog.read_text(), args.version)
    if not notes:
        sys.exit(f"No CHANGELOG.md section for {args.version}")
    print(notes)


if __name__ == "__main__":
    main()
