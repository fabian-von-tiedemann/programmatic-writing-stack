"""Ramverkets genererade filer. De bär ett versionshuvud och skrivs om när paketet
är nyare. En fil utan huvud har ändrats för hand och lämnas orörd."""

from __future__ import annotations

import re
from pathlib import Path

HEADER = (
    "<!-- bok-version: {version} | genererad av bok; redigera inte, skrivs om vid "
    "uppgradering. Egna tillägg: bok/roller/<roll>.local.md -->"
)
_VERSION = re.compile(r"<!-- bok-version: (\S+) ")


def _key(version: str) -> tuple[int, ...]:
    return tuple(int(x) for x in re.findall(r"\d+", version)[:3])


def render(content: str, version: str) -> str:
    header = HEADER.format(version=version)
    if content.startswith("---\n"):
        end = content.index("\n---\n", 4) + 5  # frontmatter måste stå först
        return content[:end] + header + "\n" + content[end:]
    return header + "\n" + content


def version_of(text: str) -> str | None:
    match = _VERSION.search(text)
    return match.group(1) if match else None


def write_generated(root: Path, rel: Path, content: str, version: str) -> str | None:
    """Skriv eller uppgradera en genererad fil. Returnerar en rad till användaren,
    eller None om inget behövde göras."""
    target = root / rel
    namn = rel.as_posix()
    rendered = render(content, version)
    if target.exists():
        current = version_of(target.read_text(encoding="utf-8"))
        if current is None:
            return f"VARNING: {namn} saknar versionshuvud (ändrad för hand) och lämnas orörd."
        if _key(current) >= _key(version):
            return None
        target.write_text(rendered, encoding="utf-8")
        return f"Uppgraderade {namn} ({current} → {version})."
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered, encoding="utf-8")
    return f"Skapade {namn}."
