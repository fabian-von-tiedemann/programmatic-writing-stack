"""Hitta bokens rot: närmaste mapp uppåt som har en bok.toml."""

from __future__ import annotations

from pathlib import Path

MARKER = "bok.toml"


class BokFel(Exception):
    """Fel som visas för användaren som en rad, utan traceback."""


class BokSaknas(BokFel):
    pass


def find_root(start: Path | None = None) -> Path:
    here = (start or Path.cwd()).resolve()
    for mapp in (here, *here.parents):
        if (mapp / MARKER).is_file():
            return mapp
    raise BokSaknas(
        f"Hittar ingen bok.toml i {here} eller uppåt. Kör `bok init` i bokens mapp först."
    )
