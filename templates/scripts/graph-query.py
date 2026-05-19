#!/usr/bin/env python3
"""graph-query.py — Story-graph query-lager (ADR 0002 v1).

Subcommands:
  who-knows        --char <char-id> --at <ISO-T>
  who-was-where    --location <loc-id> --at <ISO-T> [--tolerance MIN]
  thread           --name "<sökstr>" [--chronological]

Output: markdown till stdout. Inga skriv-operationer mot canon.

Beroenden: Python 3.11+, stdlib only.
"""
from __future__ import annotations

import argparse
import json
import pickle
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

# ---- Paths -----------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
GRAPH_DIR = REPO_ROOT / ".context" / "story-graph"
CACHE_DIR = REPO_ROOT / ".cache" / "graph"
CACHE_FILE = CACHE_DIR / "graph.pkl"

# Återanvänd existerande loader om möjligt
sys.path.insert(0, str(SCRIPT_DIR))
try:
    from _storygraph import load_graph  # noqa: E402
except ImportError:
    load_graph = None  # type: ignore[assignment]


# ---- Datum-parser ----------------------------------------------------------

ISO_FULL_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?$")
ISO_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")


def parse_iso(s: str | None) -> datetime | None:
    """Tolerant ISO 8601-parser. Accepterar YYYY-MM-DD och YYYY-MM-DDTHH:MM[:SS]."""
    if not s or not isinstance(s, str):
        return None
    s = s.strip()
    m = ISO_FULL_RE.match(s)
    if m:
        y, mo, d, h, mi, sec = m.groups()
        try:
            return datetime(int(y), int(mo), int(d), int(h), int(mi), int(sec or 0))
        except ValueError:
            return None
    m = ISO_DATE_RE.match(s)
    if m:
        y, mo, d = m.groups()
        try:
            return datetime(int(y), int(mo), int(d))
        except ValueError:
            return None
    return None


# ---- Graph-struktur --------------------------------------------------------

@dataclass
class Graph:
    characters: dict[str, dict[str, Any]] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)
    locations: dict[str, dict[str, Any]] = field(default_factory=dict)
    secrets: list[dict[str, Any]] = field(default_factory=list)
    documents: dict[str, dict[str, Any]] = field(default_factory=dict)
    organizations: dict[str, dict[str, Any]] = field(default_factory=dict)
    relationships: list[dict[str, Any]] = field(default_factory=list)
    threads: list[dict[str, Any]] = field(default_factory=list)  # parsed from threads.md

    def char(self, cid: str) -> dict[str, Any] | None:
        return self.characters.get(cid)

    def loc(self, lid: str) -> dict[str, Any] | None:
        return self.locations.get(lid)

    def event_by_id(self, eid: str) -> dict[str, Any] | None:
        for e in self.events:
            if e.get("id") == eid:
                return e
        return None


# ---- Load + cache ----------------------------------------------------------

def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _parse_threads_md(path: Path) -> list[dict[str, Any]]:
    """Plocka ut trådar med events ur threads.md.

    Format per tråd (efter strukturell städning 2026-05-19):
        ## Tråd X — Y
        ...
        **Events:**
        - `evt-...`
        - `evt-...`

    Stoppar events-listan vid första rad som inte börjar med ``- ``,
    inte är tom, eller börjar med ``#`` / ``**``.
    """
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    threads: list[dict[str, Any]] = []
    cur: dict[str, Any] | None = None
    in_events = False
    for line in lines:
        if line.startswith("## "):
            if cur is not None:
                threads.append(cur)
            cur = {
                "header": line[3:].strip(),
                "events": [],
                "raw_index": len(threads),
            }
            in_events = False
            continue
        if cur is None:
            continue
        if line.strip().startswith("**Events"):
            in_events = True
            continue
        if in_events:
            stripped = line.strip()
            if not stripped:
                # blank line — fortfarande inom Events-blocket
                continue
            if stripped.startswith("- "):
                # plocka ut första backtick-omslutna ID:t
                m = re.search(r"`(evt-[A-Za-z0-9_-]+)`", stripped)
                if m:
                    cur["events"].append(m.group(1))
                continue
            # rad som inte är bullet och inte tom → ny sektion
            if stripped.startswith("**") or stripped.startswith("#"):
                in_events = False
            else:
                # fortsättning av föregående bullet eller fri prosa — sluta
                in_events = False
    if cur is not None:
        threads.append(cur)
    return threads


def _build_graph_from_disk() -> Graph:
    g = Graph()
    # characters
    p = GRAPH_DIR / "characters.json"
    if p.exists():
        data = _load_json(p)
        for c in data.get("characters", []):
            if "id" in c:
                g.characters[c["id"]] = c
    # events
    p = GRAPH_DIR / "events.json"
    if p.exists():
        data = _load_json(p)
        g.events = list(data.get("events", []))
    # locations
    p = GRAPH_DIR / "locations.json"
    if p.exists():
        data = _load_json(p)
        for loc in data.get("locations", []):
            if "id" in loc:
                g.locations[loc["id"]] = loc
    # secrets
    p = GRAPH_DIR / "secrets.json"
    if p.exists():
        data = _load_json(p)
        g.secrets = list(data.get("secrets", []))
    # documents
    p = GRAPH_DIR / "documents.json"
    if p.exists():
        data = _load_json(p)
        for d in data.get("documents", []):
            if "id" in d:
                g.documents[d["id"]] = d
    # organizations
    p = GRAPH_DIR / "organizations.json"
    if p.exists():
        data = _load_json(p)
        for o in data.get("organizations", []):
            if "id" in o:
                g.organizations[o["id"]] = o
    # relationships
    p = GRAPH_DIR / "relationships.json"
    if p.exists():
        data = _load_json(p)
        g.relationships = list(data.get("relationships", []))
    # threads
    g.threads = _parse_threads_md(GRAPH_DIR / "threads.md")
    return g


def _cache_is_fresh() -> bool:
    if not CACHE_FILE.exists():
        return False
    try:
        cache_mtime = CACHE_FILE.stat().st_mtime
    except OSError:
        return False
    for p in GRAPH_DIR.glob("*"):
        try:
            if p.stat().st_mtime > cache_mtime:
                return False
        except OSError:
            return False
    return True


def load_or_build_graph(use_cache: bool = True) -> Graph:
    if use_cache and _cache_is_fresh():
        try:
            with CACHE_FILE.open("rb") as f:
                return pickle.load(f)
        except Exception:
            pass  # cache corrupt — bygg om
    g = _build_graph_from_disk()
    if use_cache:
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            with CACHE_FILE.open("wb") as f:
                pickle.dump(g, f)
        except OSError:
            pass
    return g


# ---- Hjälpare för IDs i fri text -------------------------------------------

CHAR_ID_RE = re.compile(r"\bchar-[a-z0-9-]+")
LOC_ID_RE = re.compile(r"\bloc-[a-z0-9-]+")


def _extract_char_ids(value: Any) -> list[str]:
    """Plocka char-IDs ur sträng eller list-av-strängar (deltagare m.m.)."""
    out: list[str] = []
    if value is None:
        return out
    if isinstance(value, str):
        out.extend(CHAR_ID_RE.findall(value))
    elif isinstance(value, list):
        for v in value:
            if isinstance(v, str):
                out.extend(CHAR_ID_RE.findall(v))
            elif isinstance(v, dict):
                # struct-entries — kolla character_id
                cid = v.get("character_id")
                if isinstance(cid, str):
                    out.append(cid)
                raw = v.get("raw")
                if isinstance(raw, str):
                    out.extend(CHAR_ID_RE.findall(raw))
    return out


def _event_participants(e: dict[str, Any]) -> list[str]:
    pts = _extract_char_ids(e.get("participants"))
    pts.extend(_extract_char_ids(e.get("participants_off_screen")))
    pov = e.get("pov")
    if isinstance(pov, str):
        pts.extend(CHAR_ID_RE.findall(pov))
    return list(dict.fromkeys(pts))  # dedup, behåll ordning


def _event_location_id(e: dict[str, Any]) -> str | None:
    loc = e.get("location")
    if not isinstance(loc, str):
        return None
    m = LOC_ID_RE.search(loc)
    if m:
        return m.group(0)
    return None  # ingen loc-ID, bara fri text


# ---- Subcommand: who-knows --------------------------------------------------

def cmd_who_knows(args: argparse.Namespace) -> int:
    g = load_or_build_graph(use_cache=not args.no_cache)
    char_id = args.char
    at = parse_iso(args.at)
    if at is None:
        print(f"FEL: kunde inte parsa --at '{args.at}' (förväntar ISO 8601, ex 2026-06-23T19:00)", file=sys.stderr)
        return 2

    ch = g.char(char_id)
    if ch is None:
        print(f"FEL: character_id '{char_id}' finns inte i characters.json", file=sys.stderr)
        # mjuk hjälp
        candidates = [cid for cid in g.characters if char_id.lower() in cid.lower()][:5]
        if candidates:
            print(f"Möjliga matchningar: {', '.join(candidates)}", file=sys.stderr)
        return 2

    name = ch.get("name", char_id)

    # Två kategorier: "vet säkert" och "anar"
    known_secure: list[tuple[dict[str, Any], dict[str, Any] | None]] = []
    known_suspected: list[tuple[dict[str, Any], dict[str, Any] | None]] = []
    schema_warnings: list[str] = []

    for sec in g.secrets:
        for bucket_name, bucket_key in (("secure", "known_to"), ("suspected", "anar")):
            entries = sec.get(bucket_key) or []
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    # ostrukturerat (legacy)
                    if isinstance(entry, str) and char_id in entry:
                        schema_warnings.append(
                            f"  - {sec.get('id')}.{bucket_key}: ostrukturerad entry "
                            f"'{entry[:60]}' — kan inte tidsstämpla"
                        )
                    continue
                if entry.get("character_id") != char_id:
                    continue
                ks_raw = entry.get("known_since")
                ks_dt = parse_iso(ks_raw)
                if ks_raw is None:
                    # vetskap utan datum — antar att karaktären känner till sedan story-start
                    if bucket_name == "secure":
                        known_secure.append((sec, entry))
                    else:
                        known_suspected.append((sec, entry))
                elif ks_dt is None:
                    # icke-parsbart datum
                    schema_warnings.append(
                        f"  - {sec.get('id')}: opareserbart known_since='{ks_raw}'"
                    )
                elif ks_dt <= at:
                    if bucket_name == "secure":
                        known_secure.append((sec, entry))
                    else:
                        known_suspected.append((sec, entry))
                # om ks_dt > at: ännu inte känd vid T

    # Output (markdown)
    out: list[str] = []
    out.append(f"# Vad {name} ({char_id}) vet vid {at.isoformat()}")
    out.append("")
    out.append(f"**Totalt:** {len(known_secure)} secrets säkert · {len(known_suspected)} secrets anade")
    out.append("")

    if known_secure:
        out.append("## Vet säkert (`known_to`)")
        out.append("")
        for sec, entry in sorted(known_secure, key=lambda x: x[1].get("known_since") or ""):
            sid = sec.get("id", "?")
            what = sec.get("what", "")
            short = (what[:140] + "…") if len(what) > 140 else what
            since = entry.get("known_since") or "—"
            source = entry.get("source") or ""
            src_part = f" _[{source}]_" if source else ""
            out.append(f"- **{sid}** (sedan: {since}{src_part})")
            out.append(f"  - {short}")
        out.append("")
    else:
        out.append("## Vet säkert (`known_to`)")
        out.append("")
        out.append("_Inga matches._")
        out.append("")

    if known_suspected:
        out.append("## Anar (`anar`)")
        out.append("")
        for sec, entry in sorted(known_suspected, key=lambda x: x[1].get("known_since") or ""):
            sid = sec.get("id", "?")
            what = sec.get("what", "")
            short = (what[:140] + "…") if len(what) > 140 else what
            since = entry.get("known_since") or "—"
            out.append(f"- **{sid}** (sedan: {since})")
            out.append(f"  - {short}")
        out.append("")

    if schema_warnings:
        out.append("## Schema-luckor")
        out.append("")
        for w in schema_warnings[:20]:
            out.append(w)
        if len(schema_warnings) > 20:
            out.append(f"  _(...+{len(schema_warnings)-20} fler)_")
        out.append("")

    print("\n".join(out))
    return 0


# ---- Subcommand: who-was-where ---------------------------------------------

def cmd_who_was_where(args: argparse.Namespace) -> int:
    g = load_or_build_graph(use_cache=not args.no_cache)
    loc_id = args.location
    at = parse_iso(args.at)
    if at is None:
        print(f"FEL: kunde inte parsa --at '{args.at}' (förväntar ISO 8601)", file=sys.stderr)
        return 2

    tol = timedelta(minutes=args.tolerance)
    low = at - tol
    high = at + tol

    loc = g.loc(loc_id)
    if loc is None:
        # OK att fortsätta — kanske används som fritext-ID
        candidates = [lid for lid in g.locations if loc_id.lower() in lid.lower()][:5]
        print(
            f"VARNING: location_id '{loc_id}' finns inte i locations.json — "
            f"söker ändå i events.location.",
            file=sys.stderr,
        )
        if candidates:
            print(f"Möjliga matchningar: {', '.join(candidates)}", file=sys.stderr)

    matches: list[tuple[dict[str, Any], datetime]] = []
    for e in g.events:
        eloc = _event_location_id(e)
        # Direkt loc-ID match
        loc_match = (eloc == loc_id)
        # Fallback: substring i fri location-string
        if not loc_match:
            raw_loc = e.get("location")
            if isinstance(raw_loc, str) and loc and isinstance(loc.get("name"), str):
                if loc["name"].lower() in raw_loc.lower():
                    loc_match = True
        if not loc_match:
            continue
        edt = parse_iso(e.get("date"))
        if edt is None:
            continue
        # Om event saknar tid (bara datum), jämför dag-omslutande
        if "T" not in (e.get("date") or ""):
            # day-level event — match om vid-tiden är samma dag
            if edt.date() == at.date():
                matches.append((e, edt))
            continue
        if low <= edt <= high:
            matches.append((e, edt))

    matches.sort(key=lambda x: x[1])

    out: list[str] = []
    loc_name = (loc or {}).get("name", loc_id)
    out.append(f"# Events i {loc_name} ({loc_id}) vid {at.isoformat()} ± {args.tolerance}min")
    out.append("")
    if not matches:
        out.append("_Inga matches._")
        print("\n".join(out))
        return 0

    out.append(f"**Antal events:** {len(matches)}")
    out.append("")
    out.append("| Tid | Event-ID | Kapitel | Deltagare | Sammanfattning |")
    out.append("|---|---|---|---|---|")
    for e, edt in matches:
        eid = e.get("id", "?")
        chap = e.get("chapter", "—")
        pts = _event_participants(e)
        pts_str = ", ".join(pts[:6]) + ("…" if len(pts) > 6 else "")
        what = (e.get("what") or "").replace("\n", " ").replace("|", "\\|")
        if len(what) > 80:
            what = what[:80] + "…"
        out.append(f"| {edt.isoformat()} | `{eid}` | {chap} | {pts_str or '—'} | {what} |")

    print("\n".join(out))
    return 0


# ---- Subcommand: thread ----------------------------------------------------

def cmd_thread(args: argparse.Namespace) -> int:
    g = load_or_build_graph(use_cache=not args.no_cache)
    needle = (args.name or "").lower().strip()
    if not needle:
        print("FEL: --name krävs", file=sys.stderr)
        return 2

    candidates = [t for t in g.threads if needle in t["header"].lower()]
    if not candidates:
        print(f"# Inga trådar matchar '{args.name}'")
        print("")
        print("Tillgängliga trådar:")
        for t in g.threads:
            print(f"- {t['header']}  ({len(t['events'])} events)")
        return 0

    out: list[str] = []
    for t in candidates:
        header = t["header"]
        evt_ids = t["events"]
        # Slå upp + sortera kronologiskt
        rows: list[tuple[datetime | None, str, dict[str, Any] | None]] = []
        missing: list[str] = []
        for eid in evt_ids:
            ev = g.event_by_id(eid)
            if ev is None:
                missing.append(eid)
                rows.append((None, eid, None))
                continue
            edt = parse_iso(ev.get("date"))
            rows.append((edt, eid, ev))
        if args.chronological:
            rows.sort(key=lambda r: r[0] or datetime.max)

        out.append(f"# Tråd: {header}")
        out.append("")
        out.append(f"**Antal events:** {len(evt_ids)}"
                   + (f"  ·  **saknas i events.json:** {len(missing)}" if missing else ""))
        out.append("")
        if missing:
            out.append("## Saknade events (refererade i threads.md men ej i events.json)")
            out.append("")
            for m in missing[:15]:
                out.append(f"- `{m}`")
            if len(missing) > 15:
                out.append(f"  _(...+{len(missing)-15} fler)_")
            out.append("")

        out.append("## Kronologi" if args.chronological else "## Events (i threads.md-ordning)")
        out.append("")
        out.append("| Tid | Event-ID | Kapitel | POV | Deltagare | Sammanfattning |")
        out.append("|---|---|---|---|---|---|")
        for edt, eid, ev in rows:
            if ev is None:
                out.append(f"| _saknas_ | `{eid}` | — | — | — | _(ej i events.json)_ |")
                continue
            t_str = edt.isoformat() if edt else (ev.get("date") or "—")
            chap = ev.get("chapter", "—")
            pov = ev.get("pov") or "—"
            pts = _event_participants(ev)
            pts_str = ", ".join(pts[:5]) + ("…" if len(pts) > 5 else "")
            what = (ev.get("what") or "").replace("\n", " ").replace("|", "\\|")
            if len(what) > 80:
                what = what[:80] + "…"
            out.append(f"| {t_str} | `{eid}` | {chap} | {pov} | {pts_str or '—'} | {what} |")
        out.append("")

    print("\n".join(out))
    return 0


# ---- CLI -------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="graph-query.py",
        description="Story-graph query-lager (ADR 0002).",
    )
    p.add_argument("--no-cache", action="store_true",
                   help="Bygg in-memory-graf från disk även om cache är fräsch.")
    sub = p.add_subparsers(dest="cmd", required=True)

    pk = sub.add_parser("who-knows", help="Vilka secrets X känner till vid T.")
    pk.add_argument("--char", required=True, help="character_id, ex: char-anna-lidman")
    pk.add_argument("--at", required=True, help="ISO 8601-tid, ex: 2026-06-23T19:00")
    pk.set_defaults(func=cmd_who_knows)

    pw = sub.add_parser("who-was-where", help="Vilka events skedde i L vid T.")
    pw.add_argument("--location", required=True, help="location_id, ex: loc-visby-stad")
    pw.add_argument("--at", required=True, help="ISO 8601-tid")
    pw.add_argument("--tolerance", type=int, default=30,
                    help="Tolerans i minuter (default 30)")
    pw.set_defaults(func=cmd_who_was_where)

    pt = sub.add_parser("thread", help="Visa tråd från threads.md.")
    pt.add_argument("--name", required=True,
                    help="Sökstr (case-insensitive substring mot Tråd-rubrik)")
    pt.add_argument("--chronological", action="store_true",
                    help="Sortera events i tidsordning (annars i threads.md-ordning)")
    pt.set_defaults(func=cmd_thread)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    t0 = time.perf_counter()
    rc = args.func(args)
    elapsed = time.perf_counter() - t0
    if rc == 0:
        print(f"\n<!-- graph-query.py · {elapsed*1000:.0f} ms -->")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
