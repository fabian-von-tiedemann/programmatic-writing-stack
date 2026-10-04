"""bok fron: slumpade frön till vägval, ur listor som följer med verktyget."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from bok.forlagor import forlagor
from bok.init import DATA
from bok.rot import BokFel, BokSaknas, find_root

FRON = DATA / "fron"
KLASSER = ("doman", "omvandning", "begransning", "process", "forlaga", "rostdrag", "formgrepp", "kalla")
STANDARD = ("doman", "omvandning", "begransning")


class FronFel(BokFel):
    pass


def lista(klass: str) -> list[str]:
    """Fröna i en av paketets listor, utan tomma rader och kommentarer."""
    path = FRON / f"{klass}.txt"
    if klass == "forlaga" or not path.is_file():
        raise FronFel(f"Det finns ingen frölista för {klass}.")
    rader = (r.strip() for r in path.read_text(encoding="utf-8").splitlines())
    return [r for r in rader if r and not r.startswith("#")]


def _forlagefron(root: Path | None) -> list[str]:
    if root is None:
        return []
    return [f"{f['namn']} ({f['fil']})" for f in forlagor(root) if f["namn"]]


def _ordning(antal: int, klasser: list[str] | None, har_forlagor: bool, rng: random.Random) -> list[str]:
    if klasser:
        return [klasser[i % len(klasser)] for i in range(antal)]
    bas = list(STANDARD) + (["forlaga"] if har_forlagor else [])
    if antal <= len(bas):
        return bas[:antal]
    return bas + [rng.choice(STANDARD) for _ in range(antal - len(bas))]


def dra(antal: int = 4, klasser: list[str] | None = None, antaganden: list[str] | None = None,
        slump: int | None = None, root: Path | None = None) -> dict:
    """Dra frön. Samma slump, klasser, antaganden och förlagor ger samma frön."""
    if antal < 1:
        raise FronFel("--antal måste vara minst 1.")
    if slump is None:
        slump = random.SystemRandom().randrange(1, 100_000)
    rng = random.Random(slump)
    forlage = _forlagefron(root)
    kvar: dict[str, list[str]] = {}
    fron = []
    for klass in _ordning(antal, klasser, bool(forlage), rng):
        if klass not in kvar:
            kvar[klass] = list(forlage) if klass == "forlaga" else lista(klass)
        if not kvar[klass]:
            if klass == "forlaga" and not forlage:
                raise FronFel("Boken har inga förlagor med namn i bok/karaktarer/forlagor/.")
            raise FronFel(f"Det finns inte fler frön i klassen {klass}.")
        text = kvar[klass].pop(rng.randrange(len(kvar[klass])))
        antagande = rng.choice(antaganden) if klass == "omvandning" and antaganden else None
        fron.append({"klass": klass, "text": text, "antagande": antagande})
    return {"slump": slump, "fron": fron}


def _rad(f: dict, fet: bool = False) -> str:
    klass = f"**{f['klass']}**" if fet else f["klass"]
    rad = f"{klass}: {f['text']}"
    return rad + (f" (antagande: {f['antagande']})" if f["antagande"] else "")


def som_text(drag: dict) -> str:
    rader = [f"Slump {drag['slump']} (samma frön igen: --slump {drag['slump']})"]
    rader += [f"{i}. {_rad(f)}" for i, f in enumerate(drag["fron"], 1)]
    return "\n".join(rader)


def spara(mapp: Path, drag: dict) -> Path:
    """Lägg dragningen sist i MAPP/fron.md; tidigare dragningar i samma varv ligger kvar."""
    mapp.mkdir(parents=True, exist_ok=True)
    path = mapp / "fron.md"
    befintlig = path.read_text(encoding="utf-8") if path.is_file() else "# Frön\n"
    delar = [f"## Slump {drag['slump']}", ""] + [f"{i}. {_rad(f, fet=True)}" for i, f in enumerate(drag["fron"], 1)]
    path.write_text(befintlig.rstrip("\n") + "\n\n" + "\n".join(delar) + "\n", encoding="utf-8")
    return path


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("fron", help="slumpade frön till ett vägval")
    p.add_argument("--antal", type=int, default=4, help="hur många frön (standard: 4)")
    p.add_argument("--klass", action="append", choices=KLASSER, help="dra bara ur den här klassen; kan upprepas")
    p.add_argument("--antagande", action="append", default=[],
                   help="ett antagande som en omvändning kan gälla; kan upprepas")
    p.add_argument("--slump", type=int, help="samma tal ger samma frön")
    p.add_argument("--spara", metavar="MAPP", help="lägg dragningen sist i MAPP/fron.md")
    p.add_argument("--json", action="store_true", help="maskinläsbart, för skillen")
    p.set_defaults(func=_kor)


def _kor(args: argparse.Namespace) -> int:
    try:
        root = find_root()
    except BokSaknas:
        root = None
    drag = dra(args.antal, args.klass, args.antagande, args.slump, root)
    if args.spara:
        mapp = Path(args.spara)
        spara(root / mapp if root and not mapp.is_absolute() else mapp, drag)
    print(json.dumps(drag, ensure_ascii=False) if args.json else som_text(drag))
    return 0
