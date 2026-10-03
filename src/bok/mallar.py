"""bok mall: lägg till en tillvalsmodul i boken."""

from __future__ import annotations

import argparse
from pathlib import Path

from bok import boktoml
from bok.init import DATA
from bok.rot import BokFel, find_root

MODULER = DATA / "moduler"
BESKRIVNING = {
    "spanning": "Klocka, ledtrådar och motkraft för spänning, deckare och thriller.",
    "serie": "Löften och hemligheter som löper över flera böcker.",
    "forlag": "Manusformat, betaläsare och revisioner inför förlag.",
    "graf-extra": "Föremål, organisationer och dokument i grafen.",
    "audiobook": "Uttal, röstprofiler och inläsningsnoter.",
    "marknad": "Baksidestext, pitch och målgrupp.",
}


class MallFel(BokFel):
    pass


def lagg_till(root: Path, namn: str) -> list[str]:
    src = MODULER / namn
    if namn not in BESKRIVNING or not src.is_dir():
        raise MallFel(f"Okänd modul {namn!r}. Välj bland: {', '.join(BESKRIVNING)}.")
    skapade = []
    for path in sorted(p for p in src.rglob("*") if p.is_file()):
        rel = path.relative_to(src)
        target = root / rel
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
        skapade.append(rel.as_posix())
    boktoml.add_modul(root, namn)
    return skapade


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("mall", help="lägg till en tillvalsmodul (utan namn: lista modulerna)")
    p.add_argument("modul", nargs="?")
    p.set_defaults(func=_kor)


def _kor(args: argparse.Namespace) -> int:
    if not args.modul:
        for namn, text in BESKRIVNING.items():
            print(f"{namn:<12} {text}")
        return 0
    skapade = lagg_till(find_root(), args.modul)
    for rel in skapade:
        print(f"Skapade {rel}.")
    if not skapade:
        print(f"Modulen {args.modul} finns redan i boken.")
    return 0
