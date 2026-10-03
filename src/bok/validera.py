"""bok validate: förbjudna namn ur canon.md och namn som inte finns i grafen."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from bok.graf import Graf
from bok.rot import find_root
from bok.tics import kapitelfiler, las_kapitel

_NAMN = re.compile(r"(?<![\wÅÄÖåäö])([A-ZÅÄÖ][a-zåäöéü]+(?:[ -][A-ZÅÄÖ][a-zåäöéü]+)*)")
MENINGSSTART = set('.!?…:–—-"(«»') | {'“', '”', '‘', '’'}


def block(text: str, namn: str) -> list[str]:
    ut = []
    for innehall in re.findall(rf"```{re.escape(namn)}\n(.*?)```", text, re.S):
        ut += [r.strip() for r in innehall.splitlines() if r.strip() and not r.strip().startswith("#")]
    return ut


def kanda_namn(graf: Graf, canon_text: str) -> set[str]:
    kanda = set(block(canon_text, "kanda-namn"))
    for nyckel in ("characters", "locations", "organizations", "objects"):
        for x in graf.lista(nyckel):
            for n in [x.get("namn"), *(x.get("alias") or [])]:
                if isinstance(n, str) and n.strip():
                    kanda.add(n.strip())
                    kanda.update(n.split())
    return kanda


def blacklist_traffar(text: str, namn: list[str]) -> list[tuple[int, str]]:
    ut = []
    for nr, rad in enumerate(text.splitlines(), 1):
        for n in namn:
            if re.search(rf"(?<!\w){re.escape(n)}(?!\w)", rad):
                ut.append((nr, n))
    return ut


def okanda(text: str, kanda: set[str]) -> list[tuple[int, str]]:
    ut, sett = [], set()
    for nr, rad in enumerate(text.splitlines(), 1):
        if rad.lstrip().startswith("#"):
            continue
        for m in _NAMN.finditer(rad):
            fore = rad[: m.start()].rstrip()
            if not fore or fore[-1] in MENINGSSTART:
                continue
            namn = m.group(1)
            if namn in kanda or any(d in kanda for d in re.split(r"[ -]", namn)) or namn in sett:
                continue
            sett.add(namn)
            ut.append((nr, namn))
    return ut


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("validate", help="förbjudna namn och namn som saknas i grafen")
    p.add_argument("filer", nargs="*", help="kapitelfiler (standard: alla i manuskript/)")
    p.set_defaults(func=_kor)


def _kor(args: argparse.Namespace) -> int:
    root = find_root()
    canon_path = root / "bok" / "canon.md"
    canon = las_kapitel(canon_path) if canon_path.is_file() else ""
    forbjudna = block(canon, "blacklist")
    kanda = kanda_namn(Graf.load(root), canon)
    filer = [Path(f).resolve() for f in args.filer] or kapitelfiler(root)
    if not filer:
        print("Inga kapitel att kontrollera i manuskript/.")
        return 0
    stopp = False
    for fil in filer:
        text = las_kapitel(fil)
        print(fil.relative_to(root).as_posix() if fil.is_relative_to(root) else str(fil))
        traffar = blacklist_traffar(text, forbjudna)
        for nr, namn in traffar:
            print(f"  BLOCKERANDE rad {nr}: {namn} står i canon.md som förbjudet namn.")
        stopp = stopp or bool(traffar)
        if nya := okanda(text, kanda):
            lista = ", ".join(f"{n} (rad {nr})" for nr, n in nya)
            print(f"  Okända namn (lägg i grafen, eller i canon.md under kända namn): {lista}")
        if not traffar and not nya:
            print("  Inga anmärkningar.")
    return 1 if stopp else 0
