"""Privata filer i ~/.config/bok: katalogen 0700, filerna 0600, skrivna hela eller inte alls."""

from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path


def katalog() -> Path:
    bas = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(bas) / "bok"


def skapa_katalog(path: Path) -> None:
    ny = not path.exists()
    os.makedirs(path, mode=0o700, exist_ok=True)
    if ny:
        os.chmod(path, 0o700)


def skriv_privat(path: Path, text: str) -> None:
    """Skriver hela filen eller inget: först till en tillfällig fil bredvid, sedan byts den in."""
    skapa_katalog(path.parent)
    fd, tillfallig = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            os.chmod(tillfallig, 0o600)
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tillfallig, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tillfallig)
        raise
