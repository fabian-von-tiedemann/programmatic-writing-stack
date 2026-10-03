"""bok annotations: läsarnoter och understrykningar från Apple Böcker (macOS)."""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from bok import boktoml
from bok.rot import BokFel, find_root

CONTAINER = Path.home() / "Library/Containers/com.apple.iBooksX/Data/Documents"
CORE_DATA_EPOK = 978307200  # 2001-01-01 i Unix-tid
STILAR = {0: "understrykning", 1: "grön", 2: "blå", 3: "gul", 4: "rosa", 5: "lila"}
SQL = """SELECT a.ZANNOTATIONCREATIONDATE, COALESCE(a.ZANNOTATIONSTYLE, 0),
COALESCE(a.ZANNOTATIONSELECTEDTEXT, ''), COALESCE(a.ZANNOTATIONNOTE, ''), COALESCE(a.ZANNOTATIONLOCATION, '')
FROM ZAEANNOTATION a
WHERE a.ZANNOTATIONASSETID = ? AND a.ZANNOTATIONDELETED = 0
  AND (a.ZANNOTATIONSELECTEDTEXT IS NOT NULL OR a.ZANNOTATIONNOTE IS NOT NULL)
  AND a.ZANNOTATIONCREATIONDATE >= ?
ORDER BY a.ZANNOTATIONCREATIONDATE ASC"""


class AnnotationsFel(BokFel):
    pass


def _hitta(katalog: Path, monster: str) -> Path:
    traffar = sorted(katalog.glob(monster))
    if not traffar:
        raise AnnotationsFel(f"Hittar inte Apple Böckers databas ({katalog / monster}). Har boken öppnats i Böcker?")
    return traffar[0]


def _kopiera(db: Path, till: Path) -> Path:
    """Kopiera databasen med -wal och -shm, så att nya noter som inte skrivits in än kommer med."""
    mal = till / db.name
    shutil.copy2(db, mal)
    for suffix in ("-wal", "-shm"):
        extra = db.with_name(db.name + suffix)
        if extra.exists():
            shutil.copy2(extra, till / extra.name)
    return mal


def hamta(titel: str, sedan: datetime | None = None,
          anno_db: Path | None = None, lib_db: Path | None = None) -> list[dict]:
    anno_db = anno_db or _hitta(CONTAINER / "AEAnnotation", "AEAnnotation_*.sqlite")
    lib_db = lib_db or _hitta(CONTAINER / "BKLibrary", "BKLibrary-*.sqlite")
    grans = sedan.timestamp() - CORE_DATA_EPOK if sedan else -1e18
    with tempfile.TemporaryDirectory() as tmp:
        lib = sqlite3.connect(_kopiera(lib_db, Path(tmp)))
        try:
            rad = lib.execute("SELECT ZASSETID FROM ZBKLIBRARYASSET WHERE ZTITLE = ? LIMIT 1", (titel,)).fetchone()
        finally:
            lib.close()
        if rad is None:
            raise AnnotationsFel(f"Hittar ingen bok med titeln {titel!r} i Böcker. Ange en annan med --titel.")
        anno = sqlite3.connect(_kopiera(anno_db, Path(tmp)))
        try:
            rader = anno.execute(SQL, (rad[0], grans)).fetchall()
        finally:
            anno.close()
    return [
        {"datum": datetime.fromtimestamp(d + CORE_DATA_EPOK).strftime("%Y-%m-%d %H:%M"),
         "stil": STILAR.get(int(s), str(s)), "markerat": sel, "not": note, "plats": loc}
        for d, s, sel, note, loc in rader
    ]


def render_md(titel: str, noter: list[dict]) -> str:
    r = [f"# Apple Böcker: {titel}", ""]
    for n, x in enumerate(noter, 1):
        r += [f"## {n}. {x['datum']} ({x['stil']})", ""]
        if x["plats"]:
            r += [f"_plats: {x['plats']}_", ""]
        if x["markerat"]:
            r += [*(f"> {rad}" for rad in x["markerat"].splitlines()), ""]
        if x["not"]:
            r += [f"**Not:** {x['not']}", ""]
    r.append(f"Totalt: {len(noter)} noter")
    return "\n".join(r) + "\n"


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("annotations", help="läsarnoter från Apple Böcker (macOS)")
    p.add_argument("--titel", help="bokens titel i Böcker (standard: titeln i bok.toml)")
    p.add_argument("--sedan", help="bara noter från och med datumet (ÅÅÅÅ-MM-DD)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--ut", help="skriv till fil i stället för att visa")
    p.add_argument("--anno-db", type=Path, help=argparse.SUPPRESS)
    p.add_argument("--lib-db", type=Path, help=argparse.SUPPRESS)
    p.set_defaults(func=_kor)


def _kor(args: argparse.Namespace) -> int:
    if sys.platform != "darwin" and not (args.anno_db and args.lib_db):
        raise AnnotationsFel("bok annotations fungerar bara på macOS, där Apple Böcker finns.")
    titel = args.titel or boktoml.read(find_root()).get("titel", "")
    try:
        sedan = datetime.strptime(args.sedan, "%Y-%m-%d") if args.sedan else None
    except ValueError as exc:
        raise AnnotationsFel(f"--sedan ska vara ÅÅÅÅ-MM-DD, fick {args.sedan!r}.") from exc
    noter = hamta(titel, sedan, args.anno_db, args.lib_db)
    text = json.dumps(noter, ensure_ascii=False, indent=2) + "\n" if args.json else render_md(titel, noter)
    if args.ut:
        Path(args.ut).write_text(text, encoding="utf-8")
        print(f"Skrev {len(noter)} noter till {args.ut}.")
    else:
        print(text, end="")
    return 0
