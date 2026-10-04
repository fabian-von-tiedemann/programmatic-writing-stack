"""Förlagor: verkliga personer som karaktärer bygger på, i bok/karaktarer/forlagor/."""

from __future__ import annotations

from pathlib import Path

from bok import frontmatter

KATALOG = ("bok", "karaktarer", "forlagor")
INTE_FORLAGOR = ("MALL.md", "README.md")


def _text(v) -> str | None:
    if isinstance(v, str) and v.strip() and not v.startswith("{{"):
        return v.strip()
    return None


def forlagor(root: Path) -> list[dict]:
    """En post per förlaga: fil, namn (None om det inte går att läsa) och alias.
    Trasiga huvuden och fel typer ger namn None, aldrig ett undantag."""
    ut = []
    for p in sorted(root.joinpath(*KATALOG).glob("*.md")):
        if p.name in INTE_FORLAGOR:
            continue
        try:
            meta, _ = frontmatter.split(p.read_text(encoding="utf-8"))
        except frontmatter.FrontmatterFel:
            meta = {}
        alias = meta.get("alias")
        alias = [alias] if isinstance(alias, str) else alias if isinstance(alias, list) else []
        ut.append({
            "fil": p.relative_to(root).as_posix(),
            "namn": _text(meta.get("namn")),
            "alias": [a for a in map(_text, alias) if a],
        })
    return ut
