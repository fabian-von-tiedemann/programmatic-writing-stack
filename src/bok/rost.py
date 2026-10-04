"""bok rost: rösten i siffror. Profil ur provbanken, drift för ett kapitel och urval till Writer."""

from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path

from bok import boktoml, frontmatter
from bok.graf import scenkort
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


def _fw(text: str, ord_: list[str]) -> dict[str, float]:
    alla = ord_i(text)
    n = len(alla) or 1
    antal = {w: 0 for w in ord_}
    for w in alla:
        if w in antal:
            antal[w] += 1
    return {w: antal[w] / n for w in ord_}


def delta(text: str, rost: list[str], kontroll: list[str]) -> tuple[float, float]:
    """Burrows Delta på funktionsorden: avståndet från texten till röstens och kontrollens centroid."""
    ord_ = funktionsord()
    ref = [_fw(t, ord_) for t in rost + kontroll]
    medel = {w: statistics.fmean(v[w] for v in ref) for w in ord_}
    sd = {w: statistics.pstdev([v[w] for v in ref]) for w in ord_}
    drag = [w for w in ord_ if sd[w] > 0]
    if not drag:
        return 0.0, 0.0

    def z(v: dict[str, float]) -> dict[str, float]:
        return {w: (v[w] - medel[w]) / sd[w] for w in drag}

    def centroid(grupp: list[str]) -> dict[str, float]:
        zs = [z(_fw(t, ord_)) for t in grupp]
        return {w: statistics.fmean(x[w] for x in zs) for w in drag}

    zt = z(_fw(text, ord_))
    return tuple(statistics.fmean(abs(zt[w] - c[w]) for w in drag) for c in (centroid(rost), centroid(kontroll)))


def utanfor(kapitel: dict, prof: dict) -> list[tuple[str, float, float, float]]:
    ut = []
    for namn in MATT:
        v, s = kapitel[namn], prof["matt"][namn]
        spann = s["max"] - s["min"]
        tol = TOLERANS * (spann if spann > 0 else abs(s["median"]))
        if v < s["min"] - tol or v > s["max"] + tol:
            ut.append((namn, v, s["min"], s["max"]))
    return ut


def pastisch(text: str, kallor: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Sekvenser om minst NGRAM ord som texten delar med en källa, sammanslagna och med källan."""
    ord_ = ord_i(text)
    ut = []
    for namn, kalltext in kallor:
        k = ord_i(kalltext)
        gram = {tuple(k[i:i + NGRAM]) for i in range(len(k) - NGRAM + 1)}
        tackt = [False] * len(ord_)
        for i in range(len(ord_) - NGRAM + 1):
            if tuple(ord_[i:i + NGRAM]) in gram:
                tackt[i:i + NGRAM] = [True] * NGRAM
        i = 0
        while i < len(ord_):
            if not tackt[i]:
                i += 1
                continue
            j = i
            while j < len(ord_) and tackt[j]:
                j += 1
            ut.append((" ".join(ord_[i:j]), namn))
            i = j
    return ut


def drift(root: Path, fil: Path) -> dict:
    krav_modul(root)
    text = ren_text(las_kapitel(fil))
    bank, kontroll = texter(root, "provbank"), texter(root, "kontroll")
    kallor = [(p.relative_to(root).as_posix(), t) for p, _, t in bank + texter(root, "exempel")]
    ut = {
        "fil": fil.relative_to(root).as_posix() if fil.is_relative_to(root) else str(fil),
        "underlag": {"provbank": len(bank), "kontroll": len(kontroll)},
        "delta": None,
        "utanfor": [],
        "pastisch": [{"text": s, "kalla": k} for s, k in pastisch(text, kallor)],
    }
    if len(bank) >= MIN_BANK and len(kontroll) >= MIN_KONTROLL:
        d_rost, d_kontroll = delta(text, [t for *_, t in bank], [t for *_, t in kontroll])
        ut["delta"] = {"rost": round(d_rost, 3), "kontroll": round(d_kontroll, 3),
                       "narmare_kontroll": d_kontroll < d_rost}
        ut["utanfor"] = [{"matt": n, "varde": v, "min": lo, "max": hi}
                         for n, v, lo, hi in utanfor(matt(text), profil([t for *_, t in bank]))]
    return ut


def som_text_drift(d: dict) -> str:
    u = d["underlag"]
    rader = [d["fil"], f"  Underlag: {u['provbank']} provstycken, {u['kontroll']} kontrollvarianter."]
    if d["delta"] is None:
        rader.append(f"  För lite underlag för rösten (minst {MIN_BANK} provstycken och {MIN_KONTROLL} "
                     "kontrollvarianter); bara pastischkontrollen körs.")
    elif d["delta"]["narmare_kontroll"]:
        rader.append(f"  VARNING: närmare AI-genomsnittet än rösten (delta rösten {d['delta']['rost']}, "
                     f"kontrollen {d['delta']['kontroll']}).")
    for x in d["utanfor"]:
        rader.append(f"  Utanför röstens spridning: {x['matt']} {_tal(x['varde'])} "
                     f"(provbanken {_tal(x['min'])}–{_tal(x['max'])}).")
    for x in d["pastisch"]:
        rader.append(f"  Pastisch: \"{x['text']}\" ({x['kalla']}).")
    if len(rader) == 2 and d["delta"] is not None:
        rader.append(f"  Inga anmärkningar (delta rösten {d['delta']['rost']}, kontrollen {d['delta']['kontroll']}).")
    return "\n".join(rader)


def urval(root: Path, kapitel: int, antal: int = 3) -> list[Path]:
    """Stycken ur provbanken med scenkortets lage, nyaste först (datum), sedan filnamn.
    Saknar scenkortet lage, eller har inget stycke det, väljs ur hela banken."""
    krav_modul(root)
    lage = scenkort(root, kapitel).get("lage")
    bank = texter(root, "provbank")
    if lage:
        bank = [b for b in bank if b[1].get("lage") == lage] or bank
    bank.sort(key=lambda b: b[0].name)
    bank.sort(key=lambda b: str(b[1].get("datum") or ""), reverse=True)
    return [p for p, _, _ in bank[:antal]]


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("rost", help="rösten i siffror: profil, drift och urval (modulen rostlabb)")
    r = p.add_subparsers(dest="rostdel", metavar="<del>", required=True)
    a = r.add_parser("profil", help="provbankens profil")
    a.add_argument("--json", action="store_true", help="maskinläsbart, för skillen")
    a.set_defaults(func=_kor_profil)
    b = r.add_parser("drift", help="ett kapitel mot rösten och AI-genomsnittet, och pastisch")
    b.add_argument("fil", help="kapitelfilen, till exempel manuskript/kapitel-03.md")
    b.add_argument("--json", action="store_true", help="maskinläsbart, för skillen")
    b.set_defaults(func=_kor_drift)
    c = r.add_parser("urval", help="stycken ur provbanken som Writer läser inför kapitlet")
    c.add_argument("--kapitel", type=int, required=True)
    c.add_argument("--antal", type=int, default=3)
    c.add_argument("--json", action="store_true", help="maskinläsbart, för skillen")
    c.set_defaults(func=_kor_urval)


def _kor_profil(args: argparse.Namespace) -> int:
    p = profil(_bank(find_root()))
    if args.json:
        print(json.dumps(p, ensure_ascii=False))
        return 0
    print(f"Provbanken: {p['antal']} provstycken")
    for namn, v in p["matt"].items():
        print(f"  {namn:<30} median {_tal(v['median'])}  ({_tal(v['min'])}–{_tal(v['max'])})")
    return 0


def _kor_drift(args: argparse.Namespace) -> int:
    root = find_root()
    d = drift(root, Path(args.fil).resolve())
    print(json.dumps(d, ensure_ascii=False) if args.json else som_text_drift(d))
    return 0


def _kor_urval(args: argparse.Namespace) -> int:
    root = find_root()
    valda = [p.relative_to(root).as_posix() for p in urval(root, args.kapitel, args.antal)]
    if args.json:
        lage = scenkort(root, args.kapitel).get("lage")
        print(json.dumps({"kapitel": args.kapitel, "lage": lage, "stycken": valda}, ensure_ascii=False))
    else:
        print("\n".join(valda))
    return 0
