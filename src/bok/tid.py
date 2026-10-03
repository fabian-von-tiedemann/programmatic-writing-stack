"""Partiella datum (ÅÅÅÅ, ÅÅÅÅ-MM, ÅÅÅÅ-MM-DD) och åldrar med den precision som finns."""

from __future__ import annotations

import re
from dataclasses import dataclass

_DATUM = re.compile(r"^(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?$")


@dataclass(frozen=True)
class Datum:
    ar: int
    manad: int | None = None
    dag: int | None = None

    def tidigast(self) -> tuple[int, int, int]:
        return (self.ar, self.manad or 1, self.dag or 1)

    def senast(self) -> tuple[int, int, int]:
        return (self.ar, self.manad or 12, self.dag or 31)

    def __str__(self) -> str:
        delar = [f"{self.ar:04d}"]
        if self.manad:
            delar.append(f"{self.manad:02d}")
        if self.dag:
            delar.append(f"{self.dag:02d}")
        return "-".join(delar)


def tolka(varde) -> Datum | None:
    """Ett partiellt datum ur grafen eller ett scenkort; allt annat blir None."""
    if isinstance(varde, bool):
        return None
    if isinstance(varde, int):
        return Datum(varde) if 1000 <= varde <= 9999 else None
    if not isinstance(varde, str):
        return None
    m = _DATUM.match(varde.strip())
    if not m:
        return None
    ar = int(m.group(1))
    manad = int(m.group(2)) if m.group(2) else None
    dag = int(m.group(3)) if m.group(3) else None
    if manad is not None and not 1 <= manad <= 12:
        return None
    if dag is not None and not 1 <= dag <= 31:
        return None
    return Datum(ar, manad, dag)


def _hela_ar(fran: tuple[int, int, int], till: tuple[int, int, int]) -> int:
    return till[0] - fran[0] - ((till[1], till[2]) < (fran[1], fran[2]))


def alder(fodd: Datum, vid: Datum) -> tuple[int, int]:
    """Lägsta och högsta möjliga ålder vid `vid`."""
    return _hela_ar(fodd.senast(), vid.tidigast()), _hela_ar(fodd.tidigast(), vid.senast())


def sakert_fore(a: Datum, b: Datum) -> bool:
    """Ligger a säkert före b, oavsett hur oprecisa datumen är?"""
    return a.senast() < b.tidigast()


def som_text(lagst: int, hogst: int) -> str:
    return f"{lagst} år" if lagst == hogst else f"{lagst}–{hogst} år"
