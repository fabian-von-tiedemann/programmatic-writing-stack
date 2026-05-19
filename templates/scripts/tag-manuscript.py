#!/usr/bin/env python3
"""tag-manuscript.py — semi-automatisk taggning av ren prosa mot story-graph.

Användning:
    ./scripts/tag-manuscript.py manuskript/kapitel-01.md

Producerar:
    manuskript/kapitel-01.draft.md          (med @[display|node-id]-taggar)
    .cache/kapitel-01.tag-suggestions.md    (rapport per match + confidence)

Algoritm:
1. Läs alla noder från grafen (characters, locations, objects, events, documents,
   organizations).
2. Hitta varje nods primärnamn ('name'/'namn') + första-namn-split + ev. aliases.
3. Sök whole-word i prosan. Skippa redan-taggade regioner.
4. Confidence:
   HIGH   = unik match per display-token, sammansatt namn ELLER egennamn med
            entydig node-koppling
   MEDIUM = display-token mappar till >1 node (auto-applicerad mot mest
            sannolika — flaggas för verifiering)
   LOW    = bestämd-form-substantiv (Skodan, kameran, kartan) — skippas;
            kräver manuell taggning
5. Attribut-referenser (@-attr-tagging) genereras EJ automatiskt.

Returkoder:
    0 = OK
    1 = inga matches hittade (klart men sannolikt fel)
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from _storygraph import build_name_index, load_graph, node_display_name  # noqa: E402

DEFAULT_GRAPH_DIR = Path(".context/story-graph")

# Ord vi aldrig taggar (för korta / ambiga)
STOPWORDS = {
    "a", "an", "av", "att", "och", "i", "på", "till", "som", "men",
    "ja", "nej", "om", "han", "hon", "den", "det", "de", "vi", "ni",
    "är", "var", "ska", "skall", "kan", "med", "för", "från",
}

# v3: Svenska vanliga ord som ALDRIG ska auto-taggas, även om de matchar
# en nods första-token-split (t.ex. "Två mejl ...", "Norra muröppning ...",
# "Stora Torget", "S:t Lars-ruinen", "Folk-och-försvar"). Dessa fångar
# partial-match-bug:en där en kort prefix-token taggas felaktigt.
# Jämförs case-insensitivt mot lowercased term.
SWEDISH_COMMON_WORDS = {
    # Siffror / räkneord
    "en", "ett", "två", "tre", "fyra", "fem", "sex", "sju", "åtta", "nio", "tio",
    "elva", "tolv", "tretton", "fjorton", "femton", "tjugo", "trettio", "fyrtio",
    "femtio", "första", "andra", "tredje", "fjärde", "femte", "sjätte", "sjunde",
    # Riktningar
    "norra", "södra", "östra", "västra", "norr", "söder", "öster", "väster",
    "övre", "nedre", "inre", "yttre",
    # Generiska adjektiv
    "stora", "stor", "stort", "lilla", "liten", "litet", "lille",
    "nya", "ny", "nytt", "gamla", "gammal", "gammalt",
    "höga", "hög", "högt", "låga", "låg", "lågt",
    "bra", "dåligt", "fina", "fin", "fint",
    # Helger / dagar
    "söndag", "måndag", "tisdag", "onsdag", "torsdag", "fredag", "lördag",
    # Vanliga substantiv som kan kollidera med org/loc-namn
    "folk", "människor", "någon", "ingen", "alla", "några",
    "hus", "huset", "gård", "gården", "torg", "torget", "gata", "gatan",
    # Förkortningar
    "s:t", "sankt", "st",
}

# v3: Minsta antal tecken för att en term ska auto-tagga som första-namn-split
# (fullnamn och alias har inget min — egennamn med 3 bokstäver är ofta valida).
MIN_FIRST_NAME_LEN = 4

# v2: generiska geo/metonymi-termer som ALDRIG auto-taggas — alltid AMBIGUOUS.
# Författaren beslutar per förekomst om termen är stad, flygplats, organisation
# eller metonymi (t.ex. "Stockholm hade sagt").
# Lämna här bara termer där metonymi-risken är central (Stockholm/Gotland) eller
# där flera plats-noder definitivt existerar (Visby, Bromma).
AMBIGUOUS_TERMS = {
    "Stockholm",
    "Visby",
    "Bromma",
    "Gotland",
}

# Bestämd-form-ändelser som vi misstänker = LOW (skip)
DEFINITE_OBJECT_SUFFIXES = ("orna", "arna", "erna", "rna", "an", "en", "et")


def is_definite_object_word(word: str) -> bool:
    """Heuristik för bestämd-form-substantiv vi inte vill auto-tagga."""
    if not word:
        return False
    if word[0].isupper():
        return False  # Egennamn-fall hanteras separat
    return word.endswith(DEFINITE_OBJECT_SUFFIXES) and len(word) > 4


def build_search_terms(
    nodes: dict[str, dict[str, Any]],
) -> dict[str, list[tuple[str, str]]]:
    """Returnerar dict { search_term: [(node_id, kind) ...] }

    kind ∈ {"full_name", "first_name", "alias"}

    v3: first-name-split görs ENDAST för char-noder. För loc/doc/org/evt
    skulle split:en producera partial-match-buggar:
      - "Norra muröppning Mellangatan" → "Norra" matchar "Norra Hansegatan"
      - "Stora Torget, Visby" → "Stora" matchar varje "Stora ..."
      - "S:t Lars-ruinen" → "S:t" matchar "S:t Hansgatan"
      - "Två mejl SGU-..." → "Två" matchar siffran "två" i prosan
      - "Folk och försvar" → "Folk" matchar svenska substantivet
    """
    terms: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for nid, node in nodes.items():
        name = node_display_name(node)
        if not name:
            continue
        name = name.strip()
        if name:
            terms[name].append((nid, "full_name"))
            parts = name.split()
            # first-name-split: endast char-noder, ord > 3 tkn, ej i blacklist
            is_char = nid.startswith("char-")
            if (
                is_char
                and len(parts) >= 2
                and parts[0][0:1].isupper()
                and len(parts[0]) >= MIN_FIRST_NAME_LEN
                and parts[0].lower() not in SWEDISH_COMMON_WORDS
            ):
                # filtrera bort beskrivande namn ("Mörk Audi Q5 — hyrbil ...")
                # och paranteser/em-streck
                if not any(c in parts[0] for c in "()—-—,"):
                    terms[parts[0]].append((nid, "first_name"))
        aliases = node.get("aliases") or []
        if isinstance(aliases, list):
            for a in aliases:
                if isinstance(a, str) and a.strip():
                    a = a.strip()
                    # alias-blacklist också: undvik aliases som är vanliga ord
                    if a.lower() in SWEDISH_COMMON_WORDS:
                        continue
                    terms[a].append((nid, "alias"))
    return terms


def make_pattern(term: str) -> re.Pattern[str]:
    """Whole-word-pattern för en search-term. Case-sensitive för egennamn."""
    # Egennamn — case-sensitive; vanliga ord — case-insensitive
    flags = 0
    if not term[0:1].isupper():
        flags |= re.IGNORECASE
    # Skydd för redan-taggade regioner: lookahead/-behind att vi INTE är inne i @[..]
    # `\bTerm\b` med svenska tecken — Python `\w` täcker åäö i UNICODE.
    escaped = re.escape(term)
    return re.compile(rf"(?<![\w])(?<!\|){escaped}(?![\w])(?!\|)", flags)


def already_tagged_spans(text: str) -> list[tuple[int, int]]:
    """Returnera [(start, end)] för redan-taggade @[...]-block."""
    spans: list[tuple[int, int]] = []
    for m in re.finditer(r"@\[[^\]]+\]", text):
        spans.append((m.start(), m.end()))
    return spans


def inside_spans(pos: int, spans: list[tuple[int, int]]) -> bool:
    for s, e in spans:
        if s <= pos < e:
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("input", type=Path, help="path till .md-fil (ren prosa)")
    p.add_argument("--graph-dir", type=Path, default=DEFAULT_GRAPH_DIR)
    p.add_argument(
        "--out-draft",
        type=Path,
        default=None,
        help="output-path för .draft.md (default: byt .md → .draft.md)",
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=None,
        help="output-path för tag-suggestions.md (default .cache/<stem>.tag-suggestions.md)",
    )
    p.add_argument("--verbose", "-v", action="store_true")
    args = p.parse_args(argv)

    if not args.input.exists():
        print(f"ERROR: input-fil saknas: {args.input}", file=sys.stderr)
        return 2

    text = args.input.read_text(encoding="utf-8")

    cache_dir = Path(".cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    stem = args.input.stem  # "kapitel-01"

    out_draft = args.out_draft or args.input.with_name(stem + ".draft.md")
    out_report = args.out_report or (cache_dir / f"{stem}.tag-suggestions.md")

    graph = load_graph(args.graph_dir)
    if args.verbose:
        print(f"Laddade {len(graph)} noder från {args.graph_dir}")

    terms = build_search_terms(graph)
    if args.verbose:
        print(f"Genererade {len(terms)} sök-termer")

    # Sortera termer: längsta först (så "Anna Lidman" matchar innan "Anna")
    sorted_terms = sorted(terms.keys(), key=len, reverse=True)

    # Hitta alla matches
    spans = already_tagged_spans(text)
    # match: (start, end, term, node_id, kind, confidence, line)
    matches: list[dict] = []

    # line-mapping
    line_starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            line_starts.append(i + 1)

    def offset_to_line(off: int) -> int:
        lo, hi = 0, len(line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if line_starts[mid] <= off:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1

    # taken-spans följer med så att längre matches får företräde
    taken: list[tuple[int, int]] = list(spans)

    for term in sorted_terms:
        if term.lower() in STOPWORDS:
            continue
        # v3: extra säkerhet — om termen (som ensam token) är ett vanligt svenskt ord,
        # skippa auto-tag oavsett vad grafen säger. Author-confirm krävs då via
        # längre multi-word-match som inkluderar termen.
        if term.lower() in SWEDISH_COMMON_WORDS:
            continue
        if len(term) < 3:
            continue
        if is_definite_object_word(term):
            # bestämd-form-objekt — skippa
            continue
        candidates = terms[term]
        # Ta unika node_ids:
        node_ids = list({nid for nid, _ in candidates})
        kinds = list({k for _, k in candidates})

        # v2: generiska/ambiga termer ska aldrig auto-taggas
        is_ambig_term = term in AMBIGUOUS_TERMS
        # Eller om någon kandidat-nod har ambiguous: true i grafen
        any_node_ambiguous = any(
            (graph.get(n, {}).get("ambiguous") is True) for n in node_ids
        )

        if is_ambig_term or any_node_ambiguous:
            confidence = "AMBIGUOUS"
            chosen_nid = sorted(node_ids)[0] if node_ids else ""
        elif len(node_ids) == 1:
            confidence = "HIGH"
            chosen_nid = node_ids[0]
        else:
            # MEDIUM — välj första (alfabetisk på node_id) men flagga
            confidence = "MEDIUM"
            chosen_nid = sorted(node_ids)[0]

        # Egennamn (kapital initial) + first_name-kind är ofta HIGH även om
        # det också finns som full_name (samma node). Men för MEDIUM över olika
        # noder håller vi MEDIUM.
        pattern = make_pattern(term)
        for m in pattern.finditer(text):
            s, e = m.start(), m.end()
            # skip om inne i redan taget span
            if any(ts <= s < te for ts, te in taken):
                continue
            matches.append(
                {
                    "start": s,
                    "end": e,
                    "term": term,
                    "node_id": chosen_nid,
                    "all_candidates": node_ids,
                    "kind": ", ".join(sorted(kinds)),
                    "confidence": confidence,
                    "line": offset_to_line(s),
                }
            )
            taken.append((s, e))

    # Sortera matches efter start
    matches.sort(key=lambda x: x["start"])

    # Producera draft genom att ersätta från slutet (så offsets inte rör sig)
    new_text = text
    skipped_low: list[dict] = []
    skipped_ambiguous: list[dict] = []
    applied: list[dict] = []

    for m in reversed(matches):
        if m["confidence"] in ("HIGH", "MEDIUM"):
            tag = f"@[{text[m['start']:m['end']]}|{m['node_id']}]"
            new_text = new_text[: m["start"]] + tag + new_text[m["end"] :]
            applied.append(m)
        elif m["confidence"] == "AMBIGUOUS":
            skipped_ambiguous.append(m)
        else:
            skipped_low.append(m)

    out_draft.write_text(new_text, encoding="utf-8")

    # Rapport
    by_conf: dict[str, list[dict]] = defaultdict(list)
    for m in applied:
        by_conf[m["confidence"]].append(m)

    lines: list[str] = []
    lines.append(f"# Tag-förslag för {stem}")
    lines.append("")
    lines.append(f"**Source:** `{args.input}`")
    lines.append(f"**Draft:** `{out_draft}`")
    lines.append("")
    lines.append("## Sammanfattning")
    lines.append(f"- {len(applied)} taggar applicerade")
    lines.append(f"  - HIGH: {len(by_conf['HIGH'])}")
    lines.append(f"  - MEDIUM: {len(by_conf['MEDIUM'])}")
    lines.append(f"- {len(skipped_ambiguous)} AMBIGUOUS (kräver författarens beslut)")
    lines.append(f"- {len(skipped_low)} skippade (LOW)")
    lines.append("")

    lines.append("## HIGH-confidence (auto-applied)")
    # Kollapsa per (term → node)
    high_collapsed: dict[tuple[str, str], list[int]] = defaultdict(list)
    for m in by_conf["HIGH"]:
        high_collapsed[(m["term"], m["node_id"])].append(m["line"])
    for (term, nid), llines in sorted(high_collapsed.items()):
        lines.append(
            f"- `{term}` → `@[{term}|{nid}]` ({len(llines)} förekomster; "
            f"första rad {min(llines)})"
        )
    lines.append("")

    lines.append("## MEDIUM-confidence (auto-applied — verifiera)")
    med_collapsed: dict[tuple[str, str], list[int]] = defaultdict(list)
    for m in by_conf["MEDIUM"]:
        med_collapsed[(m["term"], m["node_id"])].append(m["line"])
    for (term, nid), llines in sorted(med_collapsed.items()):
        sample = next(
            mm for mm in by_conf["MEDIUM"] if mm["term"] == term and mm["node_id"] == nid
        )
        alts = [c for c in sample["all_candidates"] if c != nid]
        lines.append(
            f"- `{term}` → `@[{term}|{nid}]` ({len(llines)} förekomster; "
            f"första rad {min(llines)}). Alt: {', '.join(alts) or '—'}"
        )
    lines.append("")

    lines.append("## AMBIGUOUS (författaren måste välja per förekomst)")
    lines.append(
        "Generiska geo-/metonymi-termer eller noder markerade `ambiguous: true` "
        "i grafen. Auto-tag SKIPPAS. Författaren bestämmer per förekomst om termen "
        "är t.ex. stad, flygplats eller metonymi (\"Stockholm hade sagt\")."
    )
    lines.append("")
    if skipped_ambiguous:
        # Kollapsa per term med antal förekomster + alla kandidater
        ambig_by_term: dict[str, list[dict]] = defaultdict(list)
        for m in skipped_ambiguous:
            ambig_by_term[m["term"]].append(m)
        for term, hits in sorted(ambig_by_term.items()):
            cands = sorted({c for h in hits for c in h["all_candidates"]})
            sample_lines = sorted({h["line"] for h in hits})[:6]
            cands_str = ", ".join(f"`{c}`" for c in cands) or "—"
            lines.append(
                f"- `{term}` ({len(hits)} förekomster, rad {sample_lines}). "
                f"Kandidater: {cands_str}"
            )
        lines.append("")
    else:
        lines.append("Inga.")
        lines.append("")

    lines.append("## LOW / SKIPPED (manuell genomgång)")
    lines.append(
        "Bestämd-form-substantiv (Skodan, kartan, kameran ...) "
        "auto-taggas EJ — för många false positives."
    )
    lines.append("")
    # Plocka misstänkta bestämd-form-substantiv ur prosan som referens
    # (informativt, inte autoritativt)
    suspected = sorted(
        set(
            w
            for w in re.findall(r"\b[a-zåäö]{4,}\b", text)
            if is_definite_object_word(w)
        )
    )
    if suspected:
        lines.append("Misstänkta bestämd-form-ord i texten (informativt):")
        for s in suspected[:40]:
            lines.append(f"- `{s}`")
        if len(suspected) > 40:
            lines.append(f"- ... och {len(suspected) - 40} till")
    lines.append("")

    out_report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(
        f"Tag: {len(applied)} taggar (HIGH={len(by_conf['HIGH'])}, "
        f"MEDIUM={len(by_conf['MEDIUM'])}, AMBIGUOUS={len(skipped_ambiguous)}). "
        f"Draft: {out_draft}. Rapport: {out_report}"
    )
    return 0 if applied else 1


if __name__ == "__main__":
    sys.exit(main())
