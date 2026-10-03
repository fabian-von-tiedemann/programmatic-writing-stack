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


def _set_line(root: Path, key: str, pattern: str, line: str, expected_value=None) -> bool:
    path = _path(root)
    text = path.read_text(encoding="utf-8")
    new, n = re.subn(pattern, line, text, count=1, flags=re.M)
    if n == 0:
        # Pattern didn't match
        # Check if key already exists (maybe with different format)
        key_exists = re.search(rf'(?m)^{re.escape(key)}\s*=', text)
        if key_exists:
            # Key exists but pattern didn't match; this is an error
            raise BokTomlFel(f"Kunde inte uppdatera {key} i {path}. Ändra raden för hand och försök igen.")

        # Key not found; try to insert after [bok] header
        header_match = re.search(r'(?m)^\[bok\][^\n]*\n', text)
        if not header_match:
            raise BokTomlFel(f"{path} saknar tabellen [bok]. Rätta filen och försök igen.")
        insert_pos = header_match.end()
        new = text[:insert_pos] + line + "\n" + text[insert_pos:]

    if new == text:
        return False

    path.write_text(new, encoding="utf-8")

    # Verify the write
    try:
        bok = read(root)
        if expected_value is not None and bok.get(key) != expected_value:
            path.write_text(text, encoding="utf-8")
            raise BokTomlFel(f"Kunde inte uppdatera {key} i {path}. Ändra raden för hand och försök igen.")
    except BokTomlFel:
        # Restore original if reading failed or value mismatch
        path.write_text(text, encoding="utf-8")
        raise

    return True


def set_ramverk(root: Path, version: str) -> bool:
    if read(root).get("ramverk") == version:
        return False
    # Pattern accepts both single and double quoted strings
    pattern = r'^ramverk\s*=\s*["\'][^"\']*["\']'
    return _set_line(root, "ramverk", pattern, f'ramverk = "{version}"', expected_value=version)


def add_modul(root: Path, modul: str) -> None:
    path = _path(root)
    bok = read(root)
    moduler = list(bok.get("moduler", []))
    if modul in moduler:
        return
    # Verify moduler is actually a list
    if "moduler" in bok and not isinstance(bok["moduler"], list):
        raise BokTomlFel(f"Kunde inte uppdatera moduler i {path}. 'moduler' är inte en lista. Ändra raden för hand och försök igen.")
    moduler.append(modul)
    lista = "[" + ", ".join(f'"{m}"' for m in moduler) + "]"
    # Pattern accepts any valid list
    pattern = r'^moduler\s*=\s*\[[^\]]*\]'
    _set_line(root, "moduler", pattern, f"moduler = {lista}", expected_value=moduler)
