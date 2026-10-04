"""Läser ett versionsavsnitt ur CHANGELOG.md (Keep a Changelog).

Används av releaseflödet: `python scripts/changelog.py 2.2.1` skriver ut avsnittet för
2.2.1, som blir texten i GitHub-releasen. Avslutas med kod 1 om avsnittet saknas.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def avsnitt(text: str, version: str) -> str | None:
    """Innehållet under `## [version]`, fram till nästa versionsrubrik eller länklistan."""
    rubrik = re.search(rf"(?m)^## \[{re.escape(version)}\][^\n]*\n", text)
    if rubrik is None:
        return None
    rest = text[rubrik.end():]
    slut = re.search(r"(?m)^## \[|^\[[^\]]+\]: ", rest)
    return (rest[: slut.start()] if slut else rest).strip()


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Användning: python scripts/changelog.py <version>", file=sys.stderr)
        return 2
    text = (Path(__file__).resolve().parents[1] / "CHANGELOG.md").read_text(encoding="utf-8")
    innehall = avsnitt(text, argv[1])
    if not innehall:
        print(f"CHANGELOG.md saknar avsnittet [{argv[1]}].", file=sys.stderr)
        return 1
    print(innehall)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
