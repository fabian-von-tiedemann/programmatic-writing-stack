"""bok validate: förbjudna namn ur canon.md och namn som inte finns i grafen."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from bok.graf import Graf, scenkort_om_finns
from bok.rot import find_root
from bok.tics import kapitelfiler, las_kapitel
from bok.tid import Datum, alder, som_text, tolka

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


_MENING = re.compile(r"[^.!?…]+[.!?…]?")
_ALDER = re.compile(
    r"(?<!\d)(\d{1,3})(?:-årig\w*|\s+år\s+gammal\w*|\s+års\s+ålder)"
    r"|\bvar\s+(\d{1,3})(?=\s+år\b|\s*[.!?…]|\s*$)"
)
_FODD = re.compile(r"\bfödd(?:\s+år)?\s+(\d{4})\b")
_KAPNR = re.compile(r"^kapitel-(\d+)\.md$")


def personer_med_fodd(graf: Graf) -> list[tuple[str, list[str], Datum, Datum | None]]:
    ut = []
    for c in graf.lista("characters"):
        fodd = tolka(c.get("fodd"))
        if fodd is None:
            continue
        namn = [n.strip() for n in [c.get("namn"), *(c.get("alias") or [])] if isinstance(n, str) and n.strip()]
        former = set(namn) | {n.split()[0] for n in namn}
        ut.append((c.get("namn") or c.get("id", "?"), sorted(former, key=len, reverse=True), fodd, tolka(c.get("dod"))))
    return ut


def aldersvarningar(text: str, personer, kapiteldatum: Datum) -> list[tuple[int, str]]:
    """Åldrar och födelseår i texten som inte stämmer med grafen. En person per mening, annars hoppas den över."""
    ut = []
    for nr, rad in enumerate(text.splitlines(), 1):
        for mening in _MENING.findall(rad):
            traffade = [p for p in personer
                        if any(re.search(rf"(?<![\wÅÄÖåäö]){re.escape(f)}s?(?![\wåäö])", mening) for f in p[1])]
            if len(traffade) != 1:
                continue
            namn, former, fodd, _ = traffade[0]
            if not any(re.search(rf"(?<![\wÅÄÖåäö]){re.escape(f)}(?![\wåäö])", mening) for f in former):
                continue  # bara nämnd i genitiv ("Sofias mamma"): åldern gäller någon annan
            lagst, hogst = alder(fodd, kapiteldatum)
            fynd = list(_ALDER.finditer(mening))
            vardena = [int(next(x for x in m.groups() if x)) for m in fynd]
            for f in former:
                for m in re.finditer(rf"(?<![\wÅÄÖåäö]){re.escape(f)},\s*(\d{{1,3}}),", mening):
                    vardena.append(int(m.group(1)))
            for varde in dict.fromkeys(vardena):
                if varde < lagst - 1 or varde > hogst + 1:
                    ut.append((nr, f"{namn} är {som_text(lagst, hogst)} vid kapitlets datum ({kapiteldatum}), "
                                   f"texten säger {varde}."))
            for m in _FODD.finditer(mening):
                if int(m.group(1)) != fodd.ar:
                    ut.append((nr, f"{namn} är född {fodd.ar} enligt grafen, texten säger {m.group(1)}."))
    return ut


def _nummer(fil: Path) -> int | None:
    m = _KAPNR.match(fil.name)
    return int(m.group(1)) if m else None


def _kapitel_i_tid(root: Path, graf: Graf) -> list[tuple[int, Datum | None, bool]]:
    nummer = {n for f in kapitelfiler(root) if (n := _nummer(f))}
    nummer |= {n for f in (root / "bok" / "plot" / "kapitel").glob("kapitel-*.md") if (n := _nummer(f))}
    nummer |= {e["kapitel"] for e in graf.lista("events")
               if isinstance(e.get("kapitel"), int) and not isinstance(e.get("kapitel"), bool) and e["kapitel"] > 0}
    ut = []
    for n in sorted(nummer):
        meta = scenkort_om_finns(root, n)
        ut.append((n, graf.kapitel_datum(n, meta.get("datum")), meta.get("tillbakablick") is True))
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
    graf = Graf.load(root)
    kanda = kanda_namn(graf, canon)
    filer = [Path(f).resolve() for f in args.filer] or kapitelfiler(root)
    if not filer:
        print("Inga kapitel att kontrollera i manuskript/.")
        return 0
    kapitel = _kapitel_i_tid(root, graf)
    datum = {n: d for n, d, _ in kapitel}
    personer = personer_med_fodd(graf)
    stopp = False
    if tidsfel := graf.tidsfel(kapitel):
        print("Tidslinjen")
        for rad in tidsfel:
            print(f"  BLOCKERANDE: {rad}")
        stopp = True
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
        varningar = []
        if (n := _nummer(fil)) and (d := datum.get(n)) is not None and personer:
            varningar = aldersvarningar(text, personer, d)
        for nr, rad in varningar:
            print(f"  Ålder att kontrollera rad {nr}: {rad}")
        if not traffar and not nya and not varningar:
            print("  Inga anmärkningar.")
    return 1 if stopp else 0
