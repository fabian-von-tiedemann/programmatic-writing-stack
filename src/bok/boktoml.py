"""bok.toml i bokens rot: titel, genre, ramverksversion och aktiva moduler."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from bok.rot import BokFel


class BokTomlFel(BokFel):
    pass


def _path(root: Path) -> Path:
    return root / "bok.toml"


def read(root: Path) -> dict:
    path = _path(root)
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise BokTomlFel(f"{path} är inte giltig TOML ({exc}). Rätta filen och försök igen.") from exc
    bok = data.get("bok")
    if not isinstance(bok, dict):
        raise BokTomlFel(f"{path} saknar tabellen [bok]. Rätta filen och försök igen.")
    return bok


def render_new(titel: str, version: str) -> str:
    t = titel.replace("\\", "\\\\").replace('"', '\\"')
    return f'[bok]\ntitel = "{t}"\ngenre = ""\nramverk = "{version}"\nmoduler = []\n'


def _set_line(root: Path, key: str, pattern: str, line: str) -> bool:
    path = _path(root)
    text = path.read_text(encoding="utf-8")
    new, n = re.subn(pattern, line, text, count=1, flags=re.M)
    if n == 0:
        new = text.replace("[bok]\n", f"[bok]\n{line}\n", 1)
    if new == text:
        return False
    path.write_text(new, encoding="utf-8")
    return True


def set_ramverk(root: Path, version: str) -> bool:
    if read(root).get("ramverk") == version:
        return False
    return _set_line(root, "ramverk", r'^ramverk\s*=\s*"[^"]*"', f'ramverk = "{version}"')


def add_modul(root: Path, modul: str) -> None:
    moduler = list(read(root).get("moduler", []))
    if modul in moduler:
        return
    moduler.append(modul)
    lista = "[" + ", ".join(f'"{m}"' for m in moduler) + "]"
    _set_line(root, "moduler", r"^moduler\s*=\s*\[[^\]]*\]", f"moduler = {lista}")
