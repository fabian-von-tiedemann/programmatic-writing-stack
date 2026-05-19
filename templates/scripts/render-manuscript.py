#!/usr/bin/env python3
"""render-manuscript.py — strippa @[display|node-id]-markup till ren prosa.

Användning:
    ./scripts/render-manuscript.py manuskript/kapitel-01.draft.md

Producerar:
    manuskript/kapitel-01.md            (ren prosa, identisk med Apple Books-utdata)
    .cache/kapitel-01.refs.json         (lista över alla referenser + sammanfattning)

Markup-syntax:
    @[display-text|node-id]              — full ref
    @[display-text|node-id.attr.X]       — attribut-ref

Returkoder:
    0 = success
    1 = klart men varning (orefererat input)
    2 = parse-fel — ingen renderfil skrivs
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

# ---- regex --------------------------------------------------------------
# Tillåt allt utom '|' i display, allt utom ']' i node-id.
REF_RE = re.compile(r"@\[([^|\]]+)\|([^\]]+)\]")
# Hitta misslyckade kandidater (för parse-fel-rapport):
BROKEN_RE = re.compile(r"@\[[^\]]*$", re.MULTILINE)


def find_refs(text: str) -> tuple[list[dict], list[dict]]:
    """Returnera (refs, parse_errors).

    Varje ref: dict(display, node_id, attr, line, col, paragraph,
                    context_before, context_after).
    """
    refs: list[dict] = []
    parse_errors: list[dict] = []

    # Förberäkna line-starts för line/col-mappning.
    line_starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            line_starts.append(i + 1)

    def offset_to_linecol(offset: int) -> tuple[int, int]:
        # binärsök
        lo, hi = 0, len(line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if line_starts[mid] <= offset:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1, offset - line_starts[lo]

    # Paragraf-indexering: räkna paragrafgränser (\n\n) före offset
    para_breaks = [0]
    for m in re.finditer(r"\n\s*\n", text):
        para_breaks.append(m.end())

    def offset_to_para(offset: int) -> int:
        # antalet paragrafer som börjat före eller vid offset
        n = 0
        for pb in para_breaks:
            if pb <= offset:
                n += 1
            else:
                break
        return max(n, 1)

    for m in REF_RE.finditer(text):
        display = m.group(1)
        full_id = m.group(2)
        attr: str | None = None
        node_id = full_id
        if ".attr." in full_id:
            node_id, attr = full_id.split(".attr.", 1)
        line, col = offset_to_linecol(m.start())
        ctx_start = max(0, m.start() - 30)
        ctx_end = min(len(text), m.end() + 30)
        # rensa whitespace i context-snuttar
        ctx_before = text[ctx_start : m.start()].replace("\n", " ")
        ctx_after = text[m.end() : ctx_end].replace("\n", " ")
        refs.append(
            {
                "display": display,
                "node_id": node_id,
                "attr": attr,
                "line": line,
                "col": col,
                "paragraph": offset_to_para(m.start()),
                "context_before": ctx_before,
                "context_after": ctx_after,
            }
        )

    # parse-fel: leta efter '@[' som INTE matchar REF_RE
    for m in re.finditer(r"@\[", text):
        # Försök expandera till ']'
        tail = text[m.start() : m.start() + 300]
        # Om REF_RE matchar med samma start — ok
        full_match = REF_RE.match(text, m.start())
        if full_match is not None:
            continue
        # Annars: parse-fel
        snippet = tail.splitlines()[0][:120]
        line, col = offset_to_linecol(m.start())
        parse_errors.append(
            {
                "line": line,
                "col": col,
                "snippet": snippet,
                "reason": "ogiltig markup — saknar `|` eller `]`, eller har radbrytning innan `]`",
            }
        )

    return refs, parse_errors


def render(text: str) -> str:
    return REF_RE.sub(lambda m: m.group(1), text)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("input", type=Path, help="path till .draft.md-fil")
    p.add_argument(
        "--out-md",
        type=Path,
        default=None,
        help="output-path för ren .md (default: byter .draft.md → .md)",
    )
    p.add_argument(
        "--out-refs",
        type=Path,
        default=None,
        help="output-path för refs.json (default: .cache/<kapitel>.refs.json)",
    )
    p.add_argument("--verbose", "-v", action="store_true")
    args = p.parse_args(argv)

    src: Path = args.input
    if not src.exists():
        print(f"ERROR: input-fil saknas: {src}", file=sys.stderr)
        return 2

    text = src.read_text(encoding="utf-8")

    # Auto-derive out paths
    if args.out_md is None:
        if src.name.endswith(".draft.md"):
            out_md = src.with_name(src.name.replace(".draft.md", ".md"))
        else:
            out_md = src.with_suffix(".rendered.md")
    else:
        out_md = args.out_md

    cache_dir = Path(".cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    stem = src.name.replace(".draft.md", "").replace(".md", "")
    if args.out_refs is None:
        out_refs = cache_dir / f"{stem}.refs.json"
    else:
        out_refs = args.out_refs
        out_refs.parent.mkdir(parents=True, exist_ok=True)

    refs, parse_errors = find_refs(text)

    counter = Counter(r["node_id"] for r in refs)
    by_prefix: dict[str, int] = {}
    for nid, n in counter.items():
        prefix = nid.split("-", 1)[0] + "-" if "-" in nid else "other"
        by_prefix[prefix] = by_prefix.get(prefix, 0) + n

    payload = {
        "source_file": str(src),
        "rendered_file": str(out_md),
        "rendered_at": datetime.now().isoformat(timespec="seconds"),
        "references": refs,
        "summary": {
            "total_refs": len(refs),
            "unique_nodes": len(counter),
            "by_prefix": by_prefix,
            "parse_errors": parse_errors,
        },
    }

    # Skriv refs.json oavsett
    out_refs.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    if parse_errors:
        print(
            f"PARSE-FEL ({len(parse_errors)}) — render-fil EJ skriven. Se {out_refs}.",
            file=sys.stderr,
        )
        for pe in parse_errors[:5]:
            print(
                f"  rad {pe['line']}:{pe['col']}: {pe['snippet']!r}", file=sys.stderr
            )
        return 2

    rendered = render(text)
    out_md.write_text(rendered, encoding="utf-8")

    print(
        f"Rendered {len(refs)} refs, {len(counter)} unika noder, "
        f"0 errors. Output: {out_md}"
    )
    if args.verbose:
        for prefix, n in sorted(by_prefix.items()):
            print(f"  {prefix}: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
