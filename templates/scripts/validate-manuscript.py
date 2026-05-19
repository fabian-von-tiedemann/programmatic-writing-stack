#!/usr/bin/env python3
"""validate-manuscript.py — validera refs.json mot story-graph.

Användning:
    ./scripts/validate-manuscript.py .cache/kapitel-01.refs.json

Producerar:
    .context/validator-rapporter/kapitel-01-validation.md

Regler:
    R1  Saknad nod                       ERROR
    R2  Attribut-claim-strid             WARNING
    R3  Introduktion-spårning            WARNING
    R4  Frekvens > threshold             WARNING
    R5  Verklig-person-blacklist         ERROR

Returkoder:
    0 = inga errors
    1 = errors finns (rapporten är ändå skriven)
    2 = parse-fel i refs.json
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# importera _storygraph från samma katalog
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from _storygraph import (  # noqa: E402
    build_name_index,
    has_attribute,
    load_graph,
    node_display_name,
)

DEFAULT_GRAPH_DIR = Path(".context/story-graph")
DEFAULT_BLACKLIST = Path(".context/tics-katalog.md")
DEFAULT_REPORT_DIR = Path(".context/validator-rapporter")
DEFAULT_FREQ_THRESHOLD = 8  # per kapitel (legacy fallback)

# v2: per-prefix-thresholds (R4) — POV-karaktären får särskild tröskel
DEFAULT_PER_PREFIX_THRESHOLDS = {
    "char-POV": 50,   # POV-karaktären (detekteras heuristiskt eller via frontmatter)
    "char-": 15,      # bipersoner
    "loc-": 20,
    "obj-": 10,
    "evt-": 5,
    "doc-": 5,
    "org-": 10,
    "secret-": 5,
    "other": 8,
}

# POV-detektion: en char-nod måste ha minst så här många träffar för att kvala
POV_MIN_REFS = 15

# Bestämd-form-heuristik: ändelser som indikerar bestämd form av subst
DEFINITE_SUFFIXES = ("en", "et", "an", "na", "rna", "arna", "erna", "orna")
# Egennamn i bestämd-form (proper-noun-determiner)
DEFINITE_DETERMINERS = ("den ", "det ", "de ", "denna ", "detta ")


def load_blacklist_from_tics(path: Path) -> list[str]:
    """Plocka namn från sektion 18 i tics-katalog.md."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    # plocka sektionen 18 Verkliga personer fram till nästa '## '
    m = re.search(
        r"^##\s*18\.\s*Verkliga personer.*?(?=^## )", text, re.DOTALL | re.MULTILINE
    )
    if not m:
        return []
    block = m.group(0)
    names: list[str] = []
    # rad 1: t.ex. "Åsa Hallin    — prolog r14. ..."
    for line in block.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("```"):
            continue
        # bryt vid första em-streck/streck-block
        # Mönster: "Åsa Hallin    — ..."
        nm = re.match(r"^([A-ZÅÄÖa-zåäö][\wÅÄÖåäö\-' ]{2,}?)\s+[—\-]{1,2}\s", s)
        if nm:
            names.append(nm.group(1).strip())
        else:
            # Politiker-block i ```-fence: "Magdalena Andersson, Ulf Kristersson, ..."
            if "," in s and re.match(r"^[A-ZÅÄÖ]", s):
                for part in s.split(","):
                    cand = part.strip().rstrip(".")
                    if re.match(r"^[A-ZÅÄÖ][\wÅÄÖåäö\-']+ [A-ZÅÄÖ][\wÅÄÖåäö\-']+$", cand):
                        names.append(cand)
    # dedup, behåll ordning
    seen = set()
    out = []
    for n in names:
        if n.lower() not in seen:
            seen.add(n.lower())
            out.append(n)
    return out


def build_proper_noun_set(graph: dict) -> set[str]:
    """Returnera lowercase-set över alla 'name'-värden + första-namn-split + aliases
    från char-, loc-, org-noder. Används för R3 proper-noun-filter.

    Inkluderar:
    - hela namnet ('Anna Lidman', 'Tussan', 'Carina')
    - första-namn-split ('Anna' av 'Anna Lidman')
    - aliases om fältet finns
    """
    names: set[str] = set()
    for nid, node in graph.items():
        if not (nid.startswith("char-") or nid.startswith("loc-") or nid.startswith("org-")):
            continue
        nm = node.get("name") or node.get("namn")
        if isinstance(nm, str):
            nm = nm.strip()
            if nm:
                names.add(nm.lower())
                parts = nm.split()
                if len(parts) >= 2 and parts[0][0:1].isupper():
                    names.add(parts[0].lower())
        aliases = node.get("aliases") or []
        if isinstance(aliases, list):
            for a in aliases:
                if isinstance(a, str) and a.strip():
                    names.add(a.strip().lower())
    return names


def is_definite_form(display: str, proper_nouns: set[str] | None = None) -> bool:
    """Heuristik: är display-texten i bestämd form / determinerad?

    v2: om display matchar ett proper-noun-name i grafen (display.lower() finns i
    proper_nouns), returneras False (egennamn räknas inte som bestämd form),
    OUTOM när display har klassisk objekt-bestämd-form-ändelse PÅ ETT MÄRKE
    (Skodan, Volvon, Hyundaien) — där behåller vi bestämd-form-signalen.
    """
    d = display.strip()
    if not d:
        return False
    dl = d.lower()
    proper_nouns = proper_nouns or set()

    # determinant ("den bilen") — alltid bestämd
    if any(dl.startswith(det) for det in DEFINITE_DETERMINERS):
        return True

    # Heuristik för bestämd form av MÄRKE: "Skodan", "Volvon", "Audin", "Hyundaien"
    # Om display med ÄNDELSEN borttagen är ett egennamn (Skoda, Volvo, ...) men
    # display SJÄLV INTE är ett egennamn i grafen → bestämd form.
    if dl not in proper_nouns:
        first = d.split()[0]
        if first[0:1].isupper() and first.endswith(("en", "et", "an", "na")):
            # Pröva strip:a ändelse (en/et/an/na) och se om resterande är proper noun
            for suf in ("en", "et", "an", "na"):
                if first.lower().endswith(suf) and len(first) > len(suf) + 2:
                    base = first[: -len(suf)].lower()
                    if base in proper_nouns:
                        return True
            # Capital first letter men ingen base-match: troligen riktigt egennamn
            return False
        if first[0:1].isupper():
            # Egennamn utan typisk bestämd-ändelse — inte bestämd
            return False

        # Gemener: klassisk bestämd-form-ändelse på subst
        return d.endswith(DEFINITE_SUFFIXES)

    # Display matchar ett proper-noun i grafen (Carina, Tussan, Lena, Tobias) →
    # alltid räknas som egennamn, INTE bestämd form
    return False


def detect_pov_from_opening(
    refs: list[dict], graph: dict, max_paragraph: int = 7
) -> tuple[str | None, str]:
    """v3: detektera POV via öppnings-stycken-frekvens + protagonist-flagga.

    Algoritm:
    1. Plocka ut alla char-refs i paragraph 1-N (öppningen)
    2. Filtrera till noder med `role: protagonist` om någon finns
       (POV-kapitel öppnar nästan alltid med protagonisten på scen, men
       bipersoner kan dominera frekvensen — Anna POV i kap 2 öppnar med
       Tuva som subjekt)
    3. Inom protagonisterna: välj den med flest träffar i öppningen
    4. Fallback: alla char-refs, flest träffar

    Returnerar (node_id, bevis-sträng) eller (None, "").
    """
    from collections import Counter

    opening_counts: Counter[str] = Counter()
    first_seen_line: dict[str, int] = {}
    for r in refs:
        if r.get("paragraph", 999) > max_paragraph:
            continue
        nid = r["node_id"]
        if not nid.startswith("char-") or nid not in graph:
            continue
        opening_counts[nid] += 1
        if nid not in first_seen_line:
            first_seen_line[nid] = r.get("line", 999)

    if not opening_counts:
        return None, ""

    # Protagonist-filter: om någon protagonist är ref:ad, välj bland dem
    protagonists_in_opening = [
        nid for nid in opening_counts
        if graph.get(nid, {}).get("role", "").lower() == "protagonist"
    ]
    if protagonists_in_opening:
        top = sorted(
            protagonists_in_opening,
            key=lambda nid: (-opening_counts[nid], first_seen_line.get(nid, 999)),
        )
        top_nid = top[0]
        line = first_seen_line.get(top_nid, "?")
        return top_nid, (
            f"protagonist i öppningen (paragraph 1-{max_paragraph}): "
            f"`{top_nid}` × {opening_counts[top_nid]}, första rad {line}"
        )

    # Fallback: alla char-refs, flest träffar
    top = sorted(
        opening_counts.items(),
        key=lambda kv: (-kv[1], first_seen_line.get(kv[0], 999)),
    )
    top_nid, top_count = top[0]
    line = first_seen_line.get(top_nid, "?")
    return top_nid, (
        f"flest char-träffar i öppningen (paragraph 1-{max_paragraph}, "
        f"ingen protagonist): `{top_nid}` × {top_count}, första rad {line}"
    )


def detect_pov(
    freq: dict,
    graph: dict,
    refs: list[dict] | None = None,
    frontmatter_pov: str | None = None,
) -> tuple[str | None, str]:
    """Returnera (node_id, bevis) för kapitlets POV-karaktär.

    v3-heuristik (i prioritetsordning):
    1) CLI/frontmatter override → använd det
    2) Första char-ref i paragraph 1-2 → sannolik POV
    3) Backup: char-nod med flest träffar OM >= POV_MIN_REFS
    """
    if frontmatter_pov and frontmatter_pov in graph:
        return frontmatter_pov, f"explicit override (--pov {frontmatter_pov})"

    # v3: första-meningen-detektion
    if refs:
        opening_pov, evidence = detect_pov_from_opening(refs, graph)
        if opening_pov:
            return opening_pov, evidence

    # Backup: char med flest träffar
    char_freqs = [
        (nid, c) for nid, c in freq.items()
        if nid.startswith("char-") and nid in graph
    ]
    if not char_freqs:
        return None, ""
    char_freqs.sort(key=lambda x: -x[1])
    top_nid, top_count = char_freqs[0]
    if top_count >= POV_MIN_REFS:
        return top_nid, f"backup-heuristik: flest char-träffar ({top_count})"
    return None, ""


def threshold_for(nid: str, pov_nid: str | None, thresholds: dict) -> int:
    """Returnera frekvens-tröskel för en given node-id."""
    if pov_nid and nid == pov_nid:
        return thresholds.get("char-POV", DEFAULT_FREQ_THRESHOLD)
    for prefix in ("char-", "loc-", "obj-", "evt-", "doc-", "org-", "secret-"):
        if nid.startswith(prefix):
            return thresholds.get(prefix, DEFAULT_FREQ_THRESHOLD)
    return thresholds.get("other", DEFAULT_FREQ_THRESHOLD)


def closest_id(missing: str, all_ids: list[str], n: int = 3) -> list[str]:
    return difflib.get_close_matches(missing, all_ids, n=n, cutoff=0.6)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("refs_json", type=Path, help="refs.json från render-steget")
    p.add_argument(
        "--graph-dir", type=Path, default=DEFAULT_GRAPH_DIR, help="story-graph-katalog"
    )
    p.add_argument(
        "--blacklist",
        type=Path,
        default=DEFAULT_BLACKLIST,
        help="path till tics-katalog (eller egen blacklist)",
    )
    p.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    p.add_argument(
        "--freq-threshold",
        type=int,
        default=DEFAULT_FREQ_THRESHOLD,
        help=f"legacy global tröskel (default {DEFAULT_FREQ_THRESHOLD})",
    )
    p.add_argument("--freq-threshold-pov", type=int, default=None,
                   help="tröskel för POV-karaktär (default 50)")
    p.add_argument("--freq-threshold-char", type=int, default=None,
                   help="tröskel för biroll-karaktärer (default 15)")
    p.add_argument("--freq-threshold-loc", type=int, default=None,
                   help="tröskel för platser (default 20)")
    p.add_argument("--freq-threshold-obj", type=int, default=None,
                   help="tröskel för objekt (default 10)")
    p.add_argument("--freq-threshold-evt", type=int, default=None,
                   help="tröskel för events (default 5)")
    p.add_argument("--freq-threshold-doc", type=int, default=None,
                   help="tröskel för dokument (default 5)")
    p.add_argument("--pov", type=str, default=None,
                   help="explicit POV-nod-id (override auto-detection)")
    p.add_argument("--verbose", "-v", action="store_true")
    args = p.parse_args(argv)

    # Bygg tröskel-config
    thresholds = dict(DEFAULT_PER_PREFIX_THRESHOLDS)
    if args.freq_threshold_pov is not None:
        thresholds["char-POV"] = args.freq_threshold_pov
    if args.freq_threshold_char is not None:
        thresholds["char-"] = args.freq_threshold_char
    if args.freq_threshold_loc is not None:
        thresholds["loc-"] = args.freq_threshold_loc
    if args.freq_threshold_obj is not None:
        thresholds["obj-"] = args.freq_threshold_obj
    if args.freq_threshold_evt is not None:
        thresholds["evt-"] = args.freq_threshold_evt
    if args.freq_threshold_doc is not None:
        thresholds["doc-"] = args.freq_threshold_doc

    if not args.refs_json.exists():
        print(f"ERROR: refs-fil saknas: {args.refs_json}", file=sys.stderr)
        return 2

    with args.refs_json.open(encoding="utf-8") as fh:
        refs_doc = json.load(fh)

    parse_errors = refs_doc.get("summary", {}).get("parse_errors", []) or []
    refs = refs_doc.get("references", []) or []
    source_file = refs_doc.get("source_file", "(okänt)")

    graph = load_graph(args.graph_dir)
    name_idx = build_name_index(graph)
    proper_nouns = build_proper_noun_set(graph)
    blacklist = load_blacklist_from_tics(args.blacklist)
    blacklist_l = {n.lower(): n for n in blacklist}

    errors: list[dict] = []
    warnings: list[dict] = []
    freq = Counter(r["node_id"] for r in refs)

    all_ids = list(graph.keys())

    # Spåra första-introduktion: första gången en node-id ses i kapitlet
    first_seen: dict[str, int] = {}
    # vi sorterar refs efter (line, col)
    refs_sorted = sorted(refs, key=lambda r: (r["line"], r["col"]))
    for r in refs_sorted:
        nid = r["node_id"]
        first_seen.setdefault(nid, refs_sorted.index(r))

    # R1: Saknad nod
    for r in refs:
        if r["node_id"] not in graph:
            sugg = closest_id(r["node_id"], all_ids)
            errors.append(
                {
                    "rule": "R1",
                    "title": "Saknad nod",
                    "ref": r,
                    "detail": f"node `{r['node_id']}` finns inte i grafen. "
                    f"Liknande IDs: {', '.join(sugg) if sugg else '(inga)'}",
                }
            )

    # R2: Attribut-claim-strid
    for r in refs:
        if r["attr"] and r["node_id"] in graph:
            node = graph[r["node_id"]]
            present = has_attribute(node, r["attr"])
            if present is False:
                warnings.append(
                    {
                        "rule": "R2",
                        "title": "Attribut-claim-strid",
                        "ref": r,
                        "detail": (
                            f"attribut `{r['attr']}` saknas/är false på node "
                            f"`{r['node_id']}`."
                        ),
                    }
                )
            elif present is None:
                # Heuristisk WARNING med lägre intensitet
                warnings.append(
                    {
                        "rule": "R2?",
                        "title": "Attribut-claim okänt",
                        "ref": r,
                        "detail": (
                            f"attribut `{r['attr']}` kunde inte verifieras på "
                            f"node `{r['node_id']}` (schemat saknar exakt fält). "
                            f"Manuell koll rekommenderas."
                        ),
                    }
                )

    # R3: Introduktion-spårning (v2: med proper-noun-filter)
    seen_in_chapter: set[str] = set()
    for r in refs_sorted:
        nid = r["node_id"]
        is_first = nid not in seen_in_chapter
        seen_in_chapter.add(nid)
        if is_first and is_definite_form(r["display"], proper_nouns):
            warnings.append(
                {
                    "rule": "R3",
                    "title": "Introduktion utan föregående ref",
                    "ref": r,
                    "detail": (
                        f"första referens till `{nid}` i filen är `{r['display']}` "
                        f"— bestämd form / determinerad utan etablering."
                    ),
                }
            )

    # R4: Frekvens (v3: per-prefix-thresholds + POV-detection via öppningssats)
    pov_nid, pov_evidence = detect_pov(
        dict(freq), graph, refs=refs, frontmatter_pov=args.pov
    )
    for nid, count in freq.items():
        thr = threshold_for(nid, pov_nid, thresholds)
        if count > thr:
            sample_ref = next(r for r in refs if r["node_id"] == nid)
            pov_marker = " (POV)" if nid == pov_nid else ""
            warnings.append(
                {
                    "rule": "R4",
                    "title": "Frekvens",
                    "ref": sample_ref,
                    "detail": (
                        f"node `{nid}`{pov_marker} refereras {count} ggr "
                        f"(threshold {thr}). Verifiera att alla är motiverade."
                    ),
                }
            )

    # R5: Verklig-person-blacklist
    for r in refs:
        d = r["display"].strip()
        if d.lower() in blacklist_l:
            errors.append(
                {
                    "rule": "R5",
                    "title": "Verklig person",
                    "ref": r,
                    "detail": (
                        f"display-text `{d}` matchar verklig-person-blacklist "
                        f"({blacklist_l[d.lower()]}). Byt namn eller verifiera."
                    ),
                }
            )

    # ---- Skriv rapport -----------------------------------------------------
    args.report_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(refs_doc.get("rendered_file", source_file)).stem
    if stem.endswith(".draft"):
        stem = stem[: -len(".draft")]
    report_path = args.report_dir / f"{stem}-validation.md"

    lines: list[str] = []
    lines.append(f"# Validator-rapport: {stem}")
    lines.append("")
    lines.append(f"**Genererad:** {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"**Källa:** `{source_file}`")
    lines.append(f"**Refs.json:** `{args.refs_json}`")
    lines.append("")
    lines.append("## Sammanfattning")
    lines.append(f"- {len(refs)} referenser totalt")
    lines.append(f"- {len(freq)} unika noder")
    lines.append(f"- {len(errors)} ERRORS")
    lines.append(f"- {len(warnings)} WARNINGS")
    if parse_errors:
        lines.append(f"- {len(parse_errors)} PARSE-FEL i refs.json")
    lines.append("")

    if parse_errors:
        lines.append("## Parse-fel från render-steget")
        for pe in parse_errors:
            lines.append(
                f"- rad {pe['line']}:{pe['col']}: `{pe['snippet']}` — {pe['reason']}"
            )
        lines.append("")

    if errors:
        lines.append("## Errors")
        for i, e in enumerate(errors, 1):
            r = e["ref"]
            lines.append(f"### E{i}. [{e['rule']}] {e['title']}")
            lines.append(
                f"- **Rad {r['line']}:{r['col']}** · `@[{r['display']}|{r['node_id']}"
                + (f".attr.{r['attr']}" if r['attr'] else "")
                + "]`"
            )
            lines.append(f"  - {e['detail']}")
            if r.get("context_before") or r.get("context_after"):
                cb = (r.get("context_before") or "").strip()
                ca = (r.get("context_after") or "").strip()
                lines.append(f"  > …{cb} **{r['display']}**{(' ' + ca) if ca else ''}…")
        lines.append("")
    else:
        lines.append("## Errors")
        lines.append("Inga.")
        lines.append("")

    if warnings:
        # Gruppera per regel
        per_rule: dict[str, list[dict]] = defaultdict(list)
        for w in warnings:
            per_rule[w["rule"]].append(w)
        lines.append("## Warnings")
        if pov_nid:
            pov_name = node_display_name(graph[pov_nid]) or pov_nid
            lines.append(f"*Detekterad POV: `{pov_nid}` ({pov_name}) — {pov_evidence}*")
            lines.append("")
        wi = 0
        for rule in sorted(per_rule.keys()):
            for w in per_rule[rule]:
                wi += 1
                r = w["ref"]
                lines.append(f"### W{wi}. [{w['rule']}] {w['title']}")
                lines.append(
                    f"- **Rad {r['line']}:{r['col']}** · `@[{r['display']}|{r['node_id']}"
                    + (f".attr.{r['attr']}" if r['attr'] else "")
                    + "]`"
                )
                lines.append(f"  - {w['detail']}")
                # v2: kontext-citering — visa context_before + display (bold) + context_after
                if r.get("context_before") or r.get("context_after"):
                    cb = (r.get("context_before") or "").strip()
                    ca = (r.get("context_after") or "").strip()
                    disp = r["display"]
                    # blockquote
                    lines.append(f"  > …{cb} **{disp}**{(' ' + ca) if ca else ''}…")
        lines.append("")
    else:
        lines.append("## Warnings")
        lines.append("Inga.")
        lines.append("")

    # Frekvenstabell
    lines.append("## Frekvenstabell")
    if pov_nid:
        pov_name = node_display_name(graph[pov_nid]) or pov_nid
        lines.append(
            f"*POV: `{pov_nid}` ({pov_name}) — tröskel {thresholds.get('char-POV')} "
            f"— bevis: {pov_evidence}*"
        )
    lines.append("")
    lines.append("| Node ID | Antal | Namn | Tröskel | Status |")
    lines.append("|---|---:|---|---:|---|")
    for nid, n in sorted(freq.items(), key=lambda x: -x[1]):
        node = graph.get(nid)
        name = node_display_name(node) if node else "—"
        thr = threshold_for(nid, pov_nid, thresholds) if nid in graph else "—"
        status = "OK"
        if nid not in graph:
            status = "SAKNAD"
        elif isinstance(thr, int) and n > thr:
            status = f"ÖVER tröskel"
        lines.append(f"| `{nid}` | {n} | {name or '—'} | {thr} | {status} |")
    lines.append("")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # stdout
    print(
        f"Validator: {len(errors)} errors, {len(warnings)} warnings. "
        f"Rapport: {report_path}"
    )

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
