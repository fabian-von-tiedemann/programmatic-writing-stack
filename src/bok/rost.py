"""bok rost: rösten i siffror. Profil ur provbanken, drift för ett kapitel och urval till Writer."""

from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path

from bok import boktoml, frontmatter
from bok.init import DATA
from bok.rot import BokFel, find_root
from bok.tics import las_kapitel

ROSTDATA = DATA / "rost"
MODUL = "rostlabb"
KORT, LANG = 6, 30
TOLERANS = 0.25
NGRAM = 5
MIN_BANK, MIN_KONTROLL = 3, 2
MATT = ("meningslangd_median", "meningslangd_kvartilavstand", "andel_korta", "andel_langa",
        "styckelangd_median", "replikandel", "komma", "semikolon", "kolon", "tankstreck",
        "fragetecken", "pronomenstart")

_ORD = re.compile(r"[A-Za-zÅÄÖåäöÉéÜü]+(?:-[A-Za-zÅÄÖåäöÉéÜü]+)*")
_SLUT = re.compile(r"(?:(?<=[.!?…])|(?<=[.!?…][\"”»']))\s+(?=[\"”«»„–—]?\s*[A-ZÅÄÖÉ])")
_REPLIK = ("–", "—", '"', "”", "«", "»", "„")
_KOMMENTAR = re.compile(r"<!--.*?-->", re.S)


class RostFel(BokFel):
    pass


def _lista(namn: str) -> list[str]:
    rader = (r.strip() for r in (ROSTDATA / namn).read_text(encoding="utf-8").splitlines())
    return [r for r in rader if r and not r.startswith("#")]


def funktionsord() -> list[str]:
    return _lista("funktionsord.txt")


def pronomen() -> set[str]:
    return set(_lista("pronomen.txt"))


def ren_text(text: str) -> str:
    """Brödtexten: utan huvud, rubriker och HTML-kommentarer. Ett trasigt huvud räknas som text."""
    try:
        _, body = frontmatter.split(text)
    except frontmatter.FrontmatterFel:
        body = text.lstrip("﻿").replace("\r\n", "\n")
    body = _KOMMENTAR.sub("", body)
    rader = [r.rstrip() for r in body.splitlines() if not r.lstrip().startswith("#")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(rader)).strip()


def ord_i(text: str) -> list[str]:
    return [m.group(0).lower() for m in _ORD.finditer(text)]


def stycken(text: str) -> list[str]:
    return [" ".join(s.split()) for s in re.split(r"\n\s*\n", text) if s.strip()]


def dela_meningar(stycke: str) -> list[str]:
    return [m.strip() for m in _SLUT.split(stycke) if ord_i(m)]


def _tankstreck(st: list[str]) -> int:
    return sum(s.count("–") + s.count("—") - (1 if s.startswith(("–", "—")) else 0) for s in st)


def matt(text: str) -> dict[str, float]:
    st = stycken(text)
    meningar = [m for s in st for m in dela_meningar(s)]
    langder = [len(ord_i(m)) for m in meningar]
    if not langder:
        return {namn: 0 for namn in MATT}
    antal_ord = sum(langder)
    kvartiler = statistics.quantiles(langder, n=4, method="inclusive") if len(langder) > 1 else [langder[0]] * 3
    pron = pronomen()
    per_tusen = 1000 / antal_ord
    return {
        "meningslangd_median": statistics.median(langder),
        "meningslangd_kvartilavstand": kvartiler[2] - kvartiler[0],
        "andel_korta": sum(n < KORT for n in langder) / len(langder),
        "andel_langa": sum(n > LANG for n in langder) / len(langder),
        "styckelangd_median": statistics.median(len(dela_meningar(s)) for s in st),
        "replikandel": sum(len(ord_i(s)) for s in st if s.startswith(_REPLIK)) / antal_ord,
        "komma": text.count(",") * per_tusen,
        "semikolon": text.count(";") * per_tusen,
        "kolon": text.count(":") * per_tusen,
        "tankstreck": _tankstreck(st) * per_tusen,
        "fragetecken": text.count("?") * per_tusen,
        "pronomenstart": sum(ord_i(m)[0] in pron for m in meningar) / len(meningar),
    }


def profil(texter_: list[str]) -> dict:
    alla = [matt(t) for t in texter_]
    return {"antal": len(alla), "matt": {
        namn: {"median": statistics.median(m[namn] for m in alla),
               "min": min(m[namn] for m in alla), "max": max(m[namn] for m in alla)}
        for namn in MATT}}


def krav_modul(root: Path) -> None:
    if MODUL not in (boktoml.read(root).get("moduler") or []):
        raise RostFel("Modulen rostlabb är inte på i boken. Kör `bok mall rostlabb` först.")


def texter(root: Path, mapp: str) -> list[tuple[Path, dict, str]]:
    """Filerna i bok/stil/<mapp>/ utom README.md: (fil, huvud, ren text). Trasigt huvud ger {}."""
    katalog = root / "bok" / "stil" / mapp
    ut = []
    for path in sorted(katalog.glob("*.md")):
        if path.name == "README.md":
            continue
        text = las_kapitel(path)
        try:
            meta, _ = frontmatter.split(text)
        except frontmatter.FrontmatterFel:
            meta = {}
        ut.append((path, meta, ren_text(text)))
    return ut


def _bank(root: Path) -> list[str]:
    krav_modul(root)
    bank = [t for _, _, t in texter(root, "provbank")]
    if not bank:
        raise RostFel("Provbanken bok/stil/provbank/ är tom. Röstlabbet fyller den med godkända provstycken.")
    return bank


def _tal(x: float) -> str:
    return f"{x:.2f}".rstrip("0").rstrip(".")


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("rost", help="rösten i siffror: profil, drift och urval (modulen rostlabb)")
    r = p.add_subparsers(dest="rostdel", metavar="<del>", required=True)
    a = r.add_parser("profil", help="provbankens profil")
    a.add_argument("--json", action="store_true", help="maskinläsbart, för skillen")
    a.set_defaults(func=_kor_profil)


def _kor_profil(args: argparse.Namespace) -> int:
    p = profil(_bank(find_root()))
    if args.json:
        print(json.dumps(p, ensure_ascii=False))
        return 0
    print(f"Provbanken: {p['antal']} provstycken")
    for namn, v in p["matt"].items():
        print(f"  {namn:<30} median {_tal(v['median'])}  ({_tal(v['min'])}–{_tal(v['max'])})")
    return 0
