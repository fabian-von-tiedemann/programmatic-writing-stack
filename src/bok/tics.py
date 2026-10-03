"""bok tics: frekvenspass mot tics-katalogen (.claude/bok/tics-katalog.md + bok/tics-tillagg.md)."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

from bok.rot import BokFel, find_root

_BLOCK = re.compile(r"```tics\n(.*?)```", re.S)
_KAPFIL = re.compile(r"^kapitel-(\d+)\.md$")


class TicsFel(BokFel):
    pass


@dataclass(frozen=True)
class Tic:
    namn: str
    monster: re.Pattern
    tak_kapitel: int | None
    tak_bok: int | None
    kommentar: str


def _tak(text: str, kalla: str, namn: str) -> tuple[int | None, int | None]:
    kap = bok = None
    if text in ("", "-"):
        return kap, bok
    for del_ in text.split(","):
        nyckel, sep, varde = del_.strip().partition("=")
        if not sep or not varde.strip().isdigit() or nyckel.strip() not in ("kapitel", "bok"):
            raise TicsFel(f"{kalla}: taket för {namn} ska skrivas kapitel=N, bok=N eller -, fick {text!r}.")
        if nyckel.strip() == "kapitel":
            kap = int(varde)
        else:
            bok = int(varde)
    return kap, bok


def parse_katalog(text: str, kalla: str) -> list[Tic]:
    tics = []
    for block in _BLOCK.findall(text):
        for line in block.splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = [p.strip() for p in line.split(" | ")]
            if len(parts) < 2:
                raise TicsFel(f"{kalla}: raden {line!r} ska ha formen 'namn | regex | tak | kommentar'.")
            namn, regex = parts[0], parts[1]
            try:
                monster = re.compile(regex, re.IGNORECASE)
            except re.error as exc:
                raise TicsFel(f"{kalla}: ogiltigt mönster för {namn}: {exc}") from exc
            kap, bok = _tak(parts[2] if len(parts) > 2 else "", kalla, namn)
            tics.append(Tic(namn, monster, kap, bok, parts[3] if len(parts) > 3 else ""))
    return tics


def ladda_katalog(root: Path) -> list[Tic]:
    ram = root / ".claude" / "bok" / "tics-katalog.md"
    if not ram.is_file():
        raise TicsFel("Hittar inte .claude/bok/tics-katalog.md. Kör bok init.")
    tics = parse_katalog(ram.read_text(encoding="utf-8"), ".claude/bok/tics-katalog.md")
    eget = root / "bok" / "tics-tillagg.md"
    if eget.is_file():
        tics += parse_katalog(eget.read_text(encoding="utf-8"), "bok/tics-tillagg.md")
    return tics


def scan(text: str, tics: list[Tic]) -> dict[str, list[tuple[int, str, int]]]:
    rader = text.splitlines()
    ut: dict[str, list[tuple[int, str, int]]] = {}
    for t in tics:
        traffar = []
        for nr, rad in enumerate(rader, 1):
            antal = sum(1 for _ in t.monster.finditer(rad))
            if antal:
                traffar.append((nr, rad.strip(), antal))
        if traffar:
            ut[t.namn] = traffar
    return ut


def kapitelfiler(root: Path) -> list[Path]:
    katalog = root / "manuskript"
    filer = [(int(m.group(1)), p) for p in katalog.glob("kapitel-*.md") if (m := _KAPFIL.match(p.name))]
    return [p for _, p in sorted(filer)]


def _over(antal: int, tak: int | None) -> bool:
    return tak is not None and antal > tak


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("tics", help="räkna tics per kapitel och i hela boken")
    p.add_argument("filer", nargs="*", help="kapitelfiler (standard: alla i manuskript/)")
    p.add_argument("--bok", action="store_true", help="summera hela boken mot bok-taken")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=_kor)


def _kor(args: argparse.Namespace) -> int:
    root = find_root()
    tics = ladda_katalog(root)
    per_namn = {t.namn: t for t in tics}
    filer = [Path(f).resolve() for f in args.filer] or kapitelfiler(root)
    if not filer:
        print("Inga kapitel att kontrollera i manuskript/.")
        return 0
    resultat: dict[str, dict] = {}
    totalt: dict[str, int] = {}
    for fil in filer:
        rel = fil.relative_to(root).as_posix() if fil.is_relative_to(root) else str(fil)
        traffar = scan(fil.read_text(encoding="utf-8"), tics)
        resultat[rel] = {}
        for namn, rader in traffar.items():
            antal = sum(a for _, _, a in rader)
            totalt[namn] = totalt.get(namn, 0) + antal
            tak = per_namn[namn].tak_kapitel
            resultat[rel][namn] = {"antal": antal, "tak": tak, "over": _over(antal, tak),
                                   "rader": [{"rad": nr, "text": t} for nr, t, _ in rader]}
    bok = {n: {"antal": a, "tak": per_namn[n].tak_bok, "over": _over(a, per_namn[n].tak_bok)}
           for n, a in totalt.items()}
    if args.json:
        print(json.dumps({"filer": resultat, "bok": bok}, ensure_ascii=False, indent=2))
        return 0
    for rel, traffar in resultat.items():
        print(rel)
        if not traffar:
            print("  Inga träffar.")
        for namn, r in traffar.items():
            flagga = f" [ÖVER TAK {r['tak']}/kapitel]" if r["over"] else ""
            print(f"  {namn}: {r['antal']}{flagga}")
            for rad in r["rader"]:
                print(f"    rad {rad['rad']}: {rad['text']}")
        print()
    if args.bok:
        print("Hela boken")
        for namn, r in sorted(bok.items(), key=lambda x: -x[1]["antal"]):
            flagga = f" [ÖVER TAK {r['tak']}/bok]" if r["over"] else ""
            print(f"  {namn}: {r['antal']}{flagga}")
    return 0
