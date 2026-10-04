"""Platser i boken: från id eller adress till kartan, och platsfilerna i bok/varld/platser/."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from bok.rot import BokFel
from bok.tid import Datum

_KOORD = re.compile(r"^\s*(-?\d{1,3}(?:\.\d+)?)\s*,\s*(-?\d{1,3}(?:\.\d+)?)\s*$")
_ID = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
_FOTO = re.compile(r"^Fotograferat:\s*(\d{4})(?:-\d{2}(?!\d))?(?:\s*[–-]\s*(\d{4})(?:-\d{2}(?!\d))?)?", re.M)


class PlatsFel(BokFel):
    pass


@dataclass(frozen=True)
class Plats:
    namn: str
    adress: str | None = None
    lat: float | None = None
    lng: float | None = None

    def routes(self) -> dict:
        if self.lat is not None and self.lng is not None:
            return {"location": {"latLng": {"latitude": self.lat, "longitude": self.lng}}}
        return {"address": self.adress}

    def streetview(self) -> str:
        if self.lat is not None and self.lng is not None:
            return f"{self.lat},{self.lng}"
        return self.adress or ""


def _tal(v) -> float | None:
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def _koordinater(lat: float, lng: float, namn: str) -> Plats:
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        raise PlatsFel(f"Koordinaterna för {namn} ligger utanför kartan.")
    return Plats(namn, lat=lat, lng=lng)


def tolka(arg: str, platser: list[dict]) -> Plats:
    """Ett id i locations.json, koordinater "lat,lng" eller en fri adress."""
    for p in platser:
        if p.get("id") == arg:
            namn = p.get("namn") if isinstance(p.get("namn"), str) and p["namn"].strip() else arg
            lat, lng = _tal(p.get("lat")), _tal(p.get("lng"))
            if lat is not None and lng is not None:
                return _koordinater(lat, lng, namn)
            adress = p.get("adress")
            if isinstance(adress, str) and adress.strip():
                return Plats(namn, adress=adress.strip())
            raise PlatsFel(f"Platsen {arg} har ingen adress. Lägg till adress i locations.json.")
    if m := _KOORD.match(arg):
        return _koordinater(float(m.group(1)), float(m.group(2)), arg.strip())
    if _ID.match(arg):
        raise PlatsFel(f"Platsen {arg} finns inte i locations.json. Lägg till den, eller skriv en adress "
                       '(till exempel "Slussen, Stockholm").')
    return Plats(arg.strip(), adress=arg.strip())


def platsfil(root: Path, pid: str) -> str | None:
    if not _ID.match(pid):
        return None
    path = root / "bok" / "varld" / "platser" / f"{pid}.md"
    return path.read_text(encoding="utf-8") if path.is_file() else None


def avsnitt(text: str, rubrik: str) -> str:
    m = re.search(rf"^## {re.escape(rubrik)}[ \t]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


def fotoar(text: str) -> tuple[int, int] | None:
    m = _FOTO.search(text)
    if not m:
        return None
    ar = [int(m.group(1))] + ([int(m.group(2))] if m.group(2) else [])
    return min(ar), max(ar)


def glapp(foto: tuple[int, int], kapitel: Datum) -> str:
    forsta, sista = foto
    ar = kapitel.ar
    bas = (f"Underlaget Idag är fotograferat {forsta if forsta == sista else f'{forsta}–{sista}'}; "
           f"kapitlet utspelar sig {ar}")
    if forsta - 3 < ar < sista + 3:
        return bas + "."
    if ar < forsta:
        n1, n2, riktning = forsta - ar, sista - ar, "tidigare"
    else:
        n1, n2, riktning = ar - sista, ar - forsta, "senare"
    antal = str(n1) if n1 == n2 else f"{n1}–{n2}"
    return f"{bas} ({antal} år {riktning}). Bokens tid går före; ur Idag används bara det som gällde då."


def underlag(text: str | None, datum: Datum | None) -> list[str]:
    """Rader till bok graph context: Bokens tid, Idag och glappet mellan dem."""
    if not text:
        return []
    rader = []
    if bokens_tid := avsnitt(text, "Bokens tid"):
        rader += ["#### Bokens tid", bokens_tid]
    if idag := avsnitt(text, "Idag"):
        rader += ["#### Idag", idag]
        if datum is not None and (foto := fotoar(idag)) is not None:
            rader.append(glapp(foto, datum))
    return rader
