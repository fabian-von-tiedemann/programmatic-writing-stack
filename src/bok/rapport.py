"""Rapporter: granskningar och godkännanden med frontmatter som bok status läser."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from bok import frontmatter, tics
from bok.rot import BokFel, find_root

GRANSKARE_AXLAR = {
    "redaktor": ("struktur", "karaktar", "spanning", "kontinuitet", "tema"),
    "sprakgranskare": ("prosa", "dialog", "rost"),
}
UTFALL = {
    "redaktor": {"godkand", "revidera", "eskalera"},
    "sprakgranskare": {"godkand", "revidera", "eskalera"},
    "plot-arkitekt": {"godkand", "revidera"},
    "kontinuitet": {"klar", "flaggor"},
    "forlaggare": {"fortsatt", "atgarda", "A", "B", "C"},
    "sensitivitet": {"godkand", "atgarda"},
    "forfattare": {"godkand", "tillbaka"},
}
OMFANG = ("kapitel", "akt", "forberedelse", "bok")
GODKAND_GRANS = 8
EFTER_GRANSKNING = ("kontinuitet", "forfattare")


class RapportFel(BokFel):
    def __init__(self, fel: list[str]):
        self.fel = fel
        super().__init__("Rapporten avvisades:\n" + "\n".join(f"- {f}" for f in fel))


def _posint(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v >= 1


def validera(meta: dict) -> list[str]:
    roll = meta.get("roll")
    if not isinstance(roll, str) or roll not in UTFALL:
        return [f"roll måste vara en av {', '.join(sorted(UTFALL))}, fick {roll!r}."]
    fel = []
    omfang = meta.get("omfang", "kapitel")
    if not isinstance(omfang, str) or omfang not in OMFANG:
        fel.append(f"omfang måste vara en av {', '.join(OMFANG)}, fick {omfang!r}.")
    if omfang == "kapitel" and not _posint(meta.get("kapitel")):
        fel.append("kapitel måste vara ett heltal ≥ 1 när omfang är kapitel.")
    if omfang == "akt" and not _posint(meta.get("akt")):
        fel.append("akt måste vara ett heltal ≥ 1 när omfang är akt.")
    utfall = meta.get("utfall")
    if not isinstance(utfall, str) or utfall not in UTFALL[roll]:
        fel.append(f"utfall för {roll} måste vara en av {', '.join(sorted(UTFALL[roll]))}, fick {utfall!r}.")
    if "runda" in meta and not _posint(meta["runda"]):
        fel.append("runda måste vara ett heltal ≥ 1.")
    if omfang == "kapitel" and (roll in GRANSKARE_AXLAR or roll == "forfattare") and "runda" not in meta:
        fel.append("runda krävs för granskningar och ditt omdöme om ett kapitel.")
    if roll in GRANSKARE_AXLAR:
        axlar = GRANSKARE_AXLAR[roll]
        betyg = meta.get("betyg")
        if not isinstance(betyg, dict):
            fel.append("betyg måste vara {" + ", ".join(f"{a}: N" for a in axlar) + "}.")
        else:
            if saknas := [a for a in axlar if a not in betyg]:
                fel.append(f"betyg saknar axlar: {', '.join(saknas)}.")
            if extra := [a for a in betyg if a not in axlar]:
                fel.append(f"betyg har okända axlar: {', '.join(extra)}.")
            for a, v in betyg.items():
                if isinstance(v, bool) or not isinstance(v, (int, float)) or not 1 <= v <= 10:
                    fel.append(f"betyg.{a} måste vara 1–10, fick {v!r}.")
            if not fel and utfall == "godkand" and min(betyg.values()) < GODKAND_GRANS:
                fel.append(f"utfall godkand kräver minst {GODKAND_GRANS} på varje axel; lägsta är "
                           f"{min(betyg.values())}. Sätt utfall revidera eller eskalera.")
    if not isinstance(meta.get("blockerande", []), list):
        fel.append("blockerande måste vara en lista.")
    return fel


def _katalog(root: Path, meta: dict) -> Path:
    base = root / "bok" / "rapporter"
    omfang = meta.get("omfang", "kapitel")
    if omfang == "kapitel":
        return base / f"kapitel-{meta['kapitel']:02d}"
    if omfang == "akt":
        return base / f"akt-{meta['akt']}"
    return base / omfang


def _nasta(katalog: Path, roll: str) -> int:
    nummer = [int(m.group(1)) for p in katalog.glob(f"{roll}-r*.md")
              if (m := re.fullmatch(rf"{re.escape(roll)}-r(\d+)\.md", p.name))]
    return max(nummer, default=0) + 1


def _runda_efter_granskning(katalog: Path, meta: dict, runda: int | None) -> int:
    """Kontinuitet och författarens omdöme gäller alltid kapitlets senaste granskningsrunda."""
    rundor = [int(m.group(1)) for roll in GRANSKARE_AXLAR for p in katalog.glob(f"{roll}-r*.md")
              if (m := re.fullmatch(rf"{roll}-r(\d+)\.md", p.name))]
    if not rundor:
        raise RapportFel([f"Kapitel {meta['kapitel']} har inte granskats än; {meta['roll']} kommer efter granskningen."])
    senaste = max(rundor)
    if runda is not None and runda != senaste:
        raise RapportFel([f"runda {runda} stämmer inte med senaste granskningsrundan för kapitel "
                          f"{meta['kapitel']}, som är {senaste}."])
    return senaste


def spara(root: Path, text: str, skriv_over: bool = False) -> Path:
    try:
        meta, body = frontmatter.split(text)
    except frontmatter.FrontmatterFel as exc:
        raise RapportFel([str(exc)]) from exc
    if not meta:
        raise RapportFel(["Rapporten saknar frontmatter (--- … ---) överst."])
    if fel := validera(meta):
        raise RapportFel(fel)
    katalog = _katalog(root, meta)
    runda = meta.get("runda")
    if meta.get("omfang", "kapitel") == "kapitel" and meta["roll"] in EFTER_GRANSKNING:
        runda = _runda_efter_granskning(katalog, meta, runda)
    katalog.mkdir(parents=True, exist_ok=True)
    runda = runda or _nasta(katalog, meta["roll"])
    path = katalog / f"{meta['roll']}-r{runda}.md"
    if path.exists() and not skriv_over:
        rad = path.relative_to(root).as_posix()
        if meta["roll"] in EFTER_GRANSKNING and meta.get("omfang", "kapitel") == "kapitel":
            raise RapportFel([f"{rad} finns redan för den här rundan. Använd --skriv-over för att ersätta den."])
        raise RapportFel([f"{rad} finns redan. Använd en ny runda, eller --skriv-over för att ersätta rapporten."])
    normal = text.lstrip("﻿").replace("\r\n", "\n").lstrip()
    path.write_text(normal if normal.endswith("\n") else normal + "\n", encoding="utf-8")
    return path


def las_alla(root: Path) -> list[dict]:
    base = root / "bok" / "rapporter"
    ut = []
    for p in sorted(base.rglob("*.md")) if base.is_dir() else []:
        if p.name == "README.md":
            continue
        try:
            meta, _ = frontmatter.split(p.read_text(encoding="utf-8"))
        except (frontmatter.FrontmatterFel, UnicodeDecodeError):
            continue
        if not meta or validera(meta):
            continue
        m = re.fullmatch(r".+-r(\d+)\.md", p.name)
        meta = dict(meta)
        meta.setdefault("omfang", "kapitel")
        meta["runda"] = meta.get("runda") or (int(m.group(1)) if m else 1)
        ut.append(meta)
    return ut


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("rapport", help="spara rapporter")
    r = p.add_subparsers(dest="rapport_kommando", metavar="<kommando>", required=True)
    s = r.add_parser("spara", help="validera och spara en rapport (fil, eller - för stdin)")
    s.add_argument("fil")
    s.add_argument("--skriv-over", action="store_true")
    p.set_defaults(func=_kor)


def _kor(args: argparse.Namespace) -> int:
    root = find_root()
    if args.fil == "-":
        text = sys.stdin.read()
    else:
        text = tics.las_kapitel(Path(args.fil))
    path = spara(root, text, args.skriv_over)
    print(f"Sparade {path.relative_to(root).as_posix()}.")
    return 0
