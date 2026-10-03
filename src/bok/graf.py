"""Story-graph: bokens fakta i bok/story-graph/*.json och frågorna rollerna ställer.
Schemat beskrivs i .claude/bok/story-graph.md."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from bok import frontmatter
from bok.rot import BokFel, find_root
from bok.tid import Datum, alder, sakert_fore, som_text, tolka

LISTOR = (
    "characters", "locations", "events", "secrets", "relationships", "threads",
    "objects", "organizations", "documents",
)


class GrafFel(BokFel):
    pass


def _kap(x) -> int:
    """Kapitelnummer ur json; allt som inte är ett heltal räknas som 0."""
    return x if isinstance(x, int) and not isinstance(x, bool) else 0


def ar_oppen(t: dict) -> bool:
    """Är bågen öppen? Status `oppen` (eller `öppen`, oavsett versaler); saknas status räknas den som öppen."""
    status = t.get("status") or "oppen"
    return isinstance(status, str) and status.strip().casefold() in ("oppen", "öppen")


def _ordning(e: dict) -> tuple:
    return (_kap(e.get("kapitel")), str(e.get("id", "")))


def relation_vid(rel: dict, kapitel: int | None) -> str:
    """Relationens typ när kapitel `kapitel` börjar (None: senaste)."""
    typ = rel.get("typ", "")
    for f in sorted(
        (f for f in rel.get("forandringar") or [] if isinstance(f, dict)),
        key=lambda f: _kap(f.get("kapitel")),
    ):
        if kapitel is None or _kap(f.get("kapitel")) < kapitel:
            typ = f.get("typ", typ)
    return typ


def _olosta(t: dict) -> list[dict]:
    """Planteringar som aldrig lösts."""
    return [p for p in t.get("planteringar") or [] if isinstance(p, dict) and not p.get("loses_i")]


def _oppna_vid(t: dict, kapitel: int) -> list[dict]:
    """Planteringar som var öppna när kapitel `kapitel` började."""
    return [
        p for p in t.get("planteringar") or []
        if isinstance(p, dict) and _kap(p.get("kapitel")) < kapitel
        and (not _kap(p.get("loses_i")) or _kap(p.get("loses_i")) >= kapitel)
    ]


def _steg(t: dict) -> list[dict]:
    return sorted((s for s in t.get("steg") or [] if isinstance(s, dict)), key=lambda s: _kap(s.get("kapitel")))


@dataclass
class Graf:
    data: dict[str, list[dict]]

    @classmethod
    def load(cls, root: Path) -> "Graf":
        katalog = root / "bok" / "story-graph"
        data: dict[str, list[dict]] = {}
        for nyckel in LISTOR:
            path = katalog / f"{nyckel}.json"
            if not path.exists():
                data[nyckel] = []
                continue
            rel = path.relative_to(root).as_posix()
            try:
                obj = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise GrafFel(f"{rel} rad {exc.lineno}, kolumn {exc.colno}: {exc.msg}") from exc
            items = obj.get(nyckel) if isinstance(obj, dict) else None
            if not isinstance(items, list):
                raise GrafFel(f'{rel} ska ha formen {{"{nyckel}": [ ... ]}}.')
            data[nyckel] = [x for x in items if isinstance(x, dict)]
        return cls(data)

    def lista(self, nyckel: str) -> list[dict]:
        return self.data.get(nyckel, [])

    def _finns(self, nyckel: str, id_: str) -> dict | None:
        return next((x for x in self.lista(nyckel) if x.get("id") == id_), None)

    def hitta(self, nyckel: str, id_: str) -> dict:
        if (x := self._finns(nyckel, id_)) is not None:
            return x
        ids = [str(x["id"]) for x in self.lista(nyckel) if x.get("id")]
        nara = [i for i in ids if id_.lower() in i.lower() or i.lower() in id_.lower()][:5]
        if nara:
            tips = f" Menade du: {', '.join(nara)}?"
        elif ids:
            tips = f" Finns: {', '.join(ids[:10])}."
        else:
            tips = " Listan är tom."
        raise GrafFel(f"Hittar inget med id {id_!r} i {nyckel}.json.{tips}")

    def namn(self, id_: str) -> str:
        for nyckel in ("characters", "locations", "objects", "organizations"):
            if (x := self._finns(nyckel, id_)) is not None:
                return x.get("namn") or id_
        return id_

    def kapitel_datum(self, kapitel: int, fran_scenkort=None) -> Datum | None:
        """Scenkortets datum, annars det tidigaste daterade händelsen i kapitlet."""
        if (d := tolka(fran_scenkort)) is not None:
            return d
        datum = [d for e in self.lista("events")
                 if _kap(e.get("kapitel")) == kapitel and (d := tolka(e.get("datum"))) is not None]
        return min(datum, key=Datum.tidigast) if datum else None

    def alder_vid(self, cid: str, vid: Datum) -> str | None:
        c = self._finns("characters", cid)
        if c is None or (fodd := tolka(c.get("fodd"))) is None:
            return None
        dod = tolka(c.get("dod"))
        if dod is not None and sakert_fore(dod, vid):
            return f"död {dod} (född {fodd})"
        lagst, hogst = alder(fodd, vid)
        if hogst < 0:
            return f"inte född än (född {fodd})"
        return f"{som_text(max(lagst, 0), hogst)} (född {fodd})"

    def tidslinje(self, fran: int | None = None, till: int | None = None) -> str:
        rader = []
        for e in self.lista("events"):
            d = tolka(e.get("datum"))
            if d is None or (fran is not None and d.ar < fran) or (till is not None and d.ar > till):
                continue
            rader.append((d, e))
        rader.sort(key=lambda x: (x[0].tidigast(), _kap(x[1].get("kapitel"))))
        r = ["# Tidslinje", ""]
        if not rader:
            r.append("Inga daterade händelser i grafen än.")
        for d, e in rader:
            folk = []
            for cid in e.get("narvarande") or []:
                if not isinstance(cid, str):
                    continue
                a = self.alder_vid(cid, d)
                folk.append(f"{self.namn(cid)} {a.split(' (')[0]}" if a else self.namn(cid))
            delar = [str(d), f"kapitel {e.get('kapitel', '?')}", e.get("vad", "")]
            if isinstance(e.get("plats"), str):
                delar.append(self.namn(e["plats"]))
            if folk:
                delar.append(", ".join(folk))
            r.append("- " + " · ".join(x for x in delar if x))
        return "\n".join(r) + "\n"

    def tidsfel(self, kapitel: list[tuple[int, Datum | None, bool]]) -> list[str]:
        """Tidsfel i grafen. `kapitel`: (nummer, datum, tillbakablick) i kapitelordning."""
        fel = []
        for e in sorted(self.lista("events"), key=_ordning):
            d = tolka(e.get("datum"))
            if d is None:
                continue
            for cid in e.get("narvarande") or []:
                c = self._finns("characters", cid) if isinstance(cid, str) else None
                if c is None:
                    continue
                fodd, dod = tolka(c.get("fodd")), tolka(c.get("dod"))
                var = f'"{e.get("vad") or e.get("id", "")}" ({d}, kapitel {e.get("kapitel", "?")})'
                if fodd is not None and sakert_fore(d, fodd):
                    fel.append(f"{c.get('namn', cid)} är med i {var} men föds {fodd}.")
                if dod is not None and sakert_fore(dod, d):
                    fel.append(f"{c.get('namn', cid)} är med i {var} men dog {dod}.")
        forra: tuple[int, Datum] | None = None
        for nr, d, tillbaka in kapitel:
            if d is None:
                continue
            if forra is not None and not tillbaka and sakert_fore(d, forra[1]):
                fel.append(f"Kapitel {nr} ({d}) ligger före kapitel {forra[0]} ({forra[1]}). "
                           "Är det en tillbakablick? Skriv tillbakablick: true i scenkortet.")
            if not tillbaka:
                forra = (nr, d)
        return fel

    def _relationer(self, id_: str) -> list[tuple[str, dict]]:
        ut = []
        for x in self.lista("relationships"):
            if id_ in (x.get("fran"), x.get("till")):
                annan = x.get("till") if x.get("fran") == id_ else x.get("fran")
                ut.append((annan, x))
        return ut

    def vem_vet(self, hemlighet: str, kapitel: int | None = None) -> str:
        s = self.hitta("secrets", hemlighet)
        r = [f"# Vem vet: {s.get('vad', hemlighet)}", ""]
        if s.get("sanning"):
            r += [f"Sanning: {s['sanning']}", ""]
        vet = sorted((v for v in s.get("vet") or [] if isinstance(v, dict)),
                     key=lambda v: _kap(v.get("fran_kapitel")))
        if kapitel is not None:
            vet = [v for v in vet if _kap(v.get("fran_kapitel")) <= kapitel]
        if not vet:
            r.append("Ingen vet." if kapitel is None else f"Ingen vet vid kapitel {kapitel}.")
        for v in vet:
            r.append(f"- {self.namn(v.get('karaktar', '?'))} (från kapitel {v.get('fran_kapitel', '?')})")
        return "\n".join(r) + "\n"

    def karaktar(self, id_: str) -> str:
        c = self.hitta("characters", id_)
        r = [f"# {c.get('namn', id_)} ({id_})", ""]
        if fakta := c.get("fakta") or {}:
            r += ["## Fakta", *(f"- {k}: {v}" for k, v in fakta.items()), ""]
        if rel := self._relationer(id_):
            r += ["## Relationer", *(f"- {self.namn(a)}: {relation_vid(x, None)}" for a, x in rel), ""]
        kap = sorted({_kap(e.get("kapitel")) for e in self.lista("events")
                      if id_ in (e.get("narvarande") or [])} - {0})
        if kap:
            r += ["## Förekommer i kapitel", ", ".join(map(str, kap)), ""]
        vet = [s for s in self.lista("secrets")
               if any(isinstance(v, dict) and v.get("karaktar") == id_ for v in s.get("vet") or [])]
        if vet:
            r += ["## Vet", *(f"- {s.get('vad', s.get('id'))}" for s in vet), ""]
        return "\n".join(r)

    def var(self, plats: str, kapitel: int | None = None) -> str:
        p = self.hitta("locations", plats)
        r = [f"# {p.get('namn', plats)}", ""]
        if fakta := p.get("fakta") or {}:
            r += [*(f"- {k}: {v}" for k, v in fakta.items()), ""]
        ev = [e for e in self.lista("events")
              if e.get("plats") == plats and (kapitel is None or e.get("kapitel") == kapitel)]
        r.append("## Händelser")
        if not ev:
            r.append("Inga.")
        for e in sorted(ev, key=_ordning):
            vilka = ", ".join(self.namn(n) for n in e.get("narvarande") or [])
            r.append(f"- Kapitel {e.get('kapitel', '?')}: {e.get('vad', '')} ({vilka})")
        return "\n".join(r) + "\n"

    def bagar(self, oppna: bool = False) -> str:
        tr = [t for t in self.lista("threads") if not oppna or ar_oppen(t)]
        r = ["# Bågar", ""]
        if not tr:
            r.append("Inga bågar i threads.json än.")
        for t in tr:
            steg = _steg(t)
            r.append(f"## {t.get('namn', t.get('id'))} ({t.get('id')}, {t.get('typ', '?')}, {t.get('status', 'oppen')})")
            r.append(f"Senast i kapitel {steg[-1].get('kapitel')}." if steg else "Inte påbörjad i texten.")
            r += [f"- Kapitel {s.get('kapitel', '?')}: {s.get('vad', '')}" for s in steg]
            r += [f"- Olöst plantering (kapitel {p.get('kapitel', '?')}): {p.get('vad', '')}" for p in _olosta(t)]
            r.append("")
        return "\n".join(r)

    def context(self, kapitel: int, karaktarer: list[str], platser: list[str], bagar: list[str],
                datum: Datum | None = None, rostfil: str | None = None) -> str:
        r = [f"# Underlag för kapitel {kapitel}", ""]
        if datum is not None:
            r += [f"Kapitlet utspelar sig: {datum}", ""]
        r += ["## Personer", ""]
        for cid in karaktarer:
            c = self._finns("characters", cid)
            if c is None:
                r += [f"### {cid}", "Ny i kapitlet (finns inte i grafen än).", ""]
                continue
            r.append(f"### {c.get('namn', cid)} ({cid})")
            r += [f"- {k}: {v}" for k, v in (c.get("fakta") or {}).items()]
            if datum is not None and (a := self.alder_vid(cid, datum)):
                r.append(f"- Ålder: {a}")
            r += [f"- Relation till {self.namn(a)}: {relation_vid(x, kapitel)}" for a, x in self._relationer(cid)]
            for s in self.lista("secrets"):
                for v in s.get("vet") or []:
                    if isinstance(v, dict) and v.get("karaktar") == cid and _kap(v.get("fran_kapitel")) < kapitel:
                        r.append(f"- Vet: {s.get('vad', s.get('id'))}")
            tidigare = [e for e in self.lista("events") if cid in (e.get("narvarande") or [])
                        and 0 < _kap(e.get("kapitel")) < kapitel]
            r += [f"- Senast (kapitel {e['kapitel']}): {e.get('vad', '')}" for e in sorted(tidigare, key=_ordning)[-3:]]
            r.append("")
        if platser:
            r += ["## Platser", ""]
            for pid in platser:
                p = self._finns("locations", pid)
                if p is None:
                    r += [f"### {pid}", "Ny i kapitlet (finns inte i grafen än).", ""]
                    continue
                r.append(f"### {p.get('namn', pid)} ({pid})")
                r += [f"- {k}: {v}" for k, v in (p.get("fakta") or {}).items()]
                r.append("")
        valda = bagar or [t.get("id") for t in self.lista("threads") if ar_oppen(t)]
        r += ["## Bågar", ""]
        for tid in valda:
            t = self._finns("threads", tid)
            if t is None:
                r += [f"### {tid}", "Planerad båge som inte påbörjats i texten än.", ""]
                continue
            r.append(f"### {t.get('namn', tid)} ({tid})")
            r += [f"- Kapitel {s.get('kapitel')}: {s.get('vad', '')}" for s in _steg(t) if _kap(s.get("kapitel")) < kapitel]
            r += [f"- Olöst plantering (kapitel {p.get('kapitel')}): {p.get('vad', '')}" for p in _oppna_vid(t, kapitel)]
            r.append("")
        if rostfil:
            r += ["## Röst", "", f"POV-personen har en egen röstfil: {rostfil}. Den går före bok/stil/rost.md.", ""]
        r += ["## Förra kapitlet", ""]
        forra = [e for e in self.lista("events") if e.get("kapitel") == kapitel - 1]
        r += [f"- {e.get('vad', '')}" for e in sorted(forra, key=_ordning)] or ["Inga händelser i grafen."]
        return "\n".join(r) + "\n"


def scenkort(root: Path, kapitel: int) -> dict:
    katalog = root / "bok" / "plot" / "kapitel"
    path = next((p for p in katalog.glob("kapitel-*.md")
                 if p.stem.split("-", 1)[1].isdigit() and int(p.stem.split("-", 1)[1]) == kapitel), None)
    if path is None:
        raise GrafFel(f"Scenkortet bok/plot/kapitel/kapitel-{kapitel:02d}.md saknas. Plot-arkitekten gör det först.")
    text = path.read_text(encoding="utf-8")
    if "{{" in text:
        raise GrafFel(f"Scenkortet {path.name} är inte ifyllt än.")
    meta, _ = frontmatter.split(text)
    return meta


def scenkort_om_finns(root: Path, kapitel: int) -> dict:
    """Scenkortets huvud, eller {} om scenkortet saknas, inte är ifyllt eller är trasigt."""
    try:
        return scenkort(root, kapitel)
    except BokFel:
        return {}


def _ids(meta: dict, nyckel: str) -> list[str]:
    v = meta.get(nyckel) or []
    return [x for x in v if isinstance(x, str)] if isinstance(v, list) else []


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("graph", help="frågor mot story-graph")
    g = p.add_subparsers(dest="fraga", metavar="<fråga>", required=True)
    c = g.add_parser("context", help="underlag för ett kapitel enligt scenkortet")
    c.add_argument("--kapitel", type=int, required=True)
    v = g.add_parser("vem-vet", help="vilka som känner till en hemlighet")
    v.add_argument("hemlighet")
    v.add_argument("--kapitel", type=int)
    b = g.add_parser("bagar", help="bågarnas läge")
    b.add_argument("--oppna", action="store_true")
    k = g.add_parser("karaktar", help="en person i grafen")
    k.add_argument("id")
    w = g.add_parser("var", help="händelser på en plats")
    w.add_argument("plats")
    w.add_argument("--kapitel", type=int)
    t = g.add_parser("tidslinje", help="daterade händelser i tidsordning, med åldrar")
    t.add_argument("--fran", type=int)
    t.add_argument("--till", type=int)
    p.set_defaults(func=_kor)


def _kor(args: argparse.Namespace) -> int:
    root = find_root()
    if args.fraga == "context":
        meta = scenkort(root, args.kapitel)
        graf = Graf.load(root)
        pov = meta.get("pov")
        rost = root / "bok" / "stil" / f"rost-{pov}.md" if isinstance(pov, str) else None
        print(graf.context(args.kapitel, _ids(meta, "karaktarer"), _ids(meta, "platser"), _ids(meta, "bagar"),
                           datum=graf.kapitel_datum(args.kapitel, meta.get("datum")),
                           rostfil=rost.relative_to(root).as_posix() if rost and rost.is_file() else None))
        return 0
    graf = Graf.load(root)
    if args.fraga == "tidslinje":
        print(graf.tidslinje(args.fran, args.till))
    elif args.fraga == "vem-vet":
        print(graf.vem_vet(args.hemlighet, args.kapitel))
    elif args.fraga == "bagar":
        print(graf.bagar(args.oppna))
    elif args.fraga == "karaktar":
        print(graf.karaktar(args.id))
    else:
        print(graf.var(args.plats, args.kapitel))
    return 0
