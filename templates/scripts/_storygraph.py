"""Gemensam laddare av story-graph-noder.

Returnerar en flat dict { node_id: node_dict } samt en "display-name index"
{ display_str.lower(): [node_ids...] } för fuzzy-matchning.

Hanterar två schema-varianter:
- characters/locations/events/documents/secrets/organizations: top-level key med list
- objects: top-level dict { id: {id, namn, ...} }
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

GRAPH_FILES = {
    "characters.json": "characters",
    "locations.json": "locations",
    "events.json": "events",
    "documents.json": "documents",
    "secrets.json": "secrets",
    "organizations.json": "organizations",
    "objects.json": None,  # dict-style
}


def load_graph(graph_dir: Path) -> dict[str, dict[str, Any]]:
    """Returnera flat { node_id: node } dict över alla noder."""
    nodes: dict[str, dict[str, Any]] = {}
    for filename, list_key in GRAPH_FILES.items():
        path = graph_dir / filename
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        if list_key is None:
            # objects.json — dict of {id: node}
            for nid, node in data.items():
                if nid.startswith("_") or nid.startswith("$"):
                    continue
                if isinstance(node, dict):
                    nodes[nid] = node
        else:
            items = data.get(list_key, [])
            for node in items:
                if isinstance(node, dict) and "id" in node:
                    nodes[node["id"]] = node
    return nodes


def node_display_name(node: dict[str, Any]) -> str | None:
    """Returnera primärt namn för noden ('name' eller 'namn')."""
    return node.get("name") or node.get("namn")


def build_name_index(
    nodes: dict[str, dict[str, Any]],
) -> dict[str, list[str]]:
    """Bygg lowercase display-name → [node_ids]-index.

    Inkluderar:
    - hela namnet ('Anna Lidman')
    - första namnet ('Anna') om hela namnet har mellanslag
    - aliases om fältet finns (saknas idag, men framtidssäkrat)
    """
    idx: dict[str, list[str]] = {}
    for nid, node in nodes.items():
        name = node_display_name(node)
        if not name:
            continue
        keys = {name.strip()}
        # första-namn split: bara om uppenbart "Förnamn Efternamn"
        parts = name.split()
        if len(parts) >= 2 and parts[0][0:1].isupper():
            keys.add(parts[0])
        aliases = node.get("aliases") or []
        if isinstance(aliases, list):
            keys.update(a for a in aliases if isinstance(a, str))
        for k in keys:
            kl = k.lower()
            idx.setdefault(kl, []).append(nid)
    return idx


def has_attribute(node: dict[str, Any], attr: str) -> bool | None:
    """Pragmatisk attribut-koll. Returnerar True/False/None (None = okänt).

    Pratar mot characters.json-schemat som är rikt men inkonsekvent:
    - direkta fält ("hair", "physical", "speech", ...)
    - om 'attr' finns på noden — kolla där först
    - annars: titta i hela noden för en nyckel som matchar attr
    - annars: söka i strängvärden efter ordet (heuristik, returnerar None om osäkert)
    """
    if "attr" in node and isinstance(node["attr"], dict):
        if attr in node["attr"]:
            val = node["attr"][attr]
            if isinstance(val, bool):
                return val
            return val is not None and val is not False
    # Exakt-fält
    if attr in node:
        val = node[attr]
        if isinstance(val, bool):
            return val
        return val is not None and val is not False
    # Sök i fysiska/wardrobe/speech-strängar (heuristik)
    haystack_parts: list[str] = []
    for key in ("physical", "wardrobe", "speech", "small_details", "description", "beskrivning"):
        v = node.get(key)
        if isinstance(v, str):
            haystack_parts.append(v.lower())
        elif isinstance(v, dict):
            haystack_parts.extend(str(x).lower() for x in v.values())
        elif isinstance(v, list):
            haystack_parts.extend(str(x).lower() for x in v)
    if not haystack_parts:
        return None
    haystack = " ".join(haystack_parts)
    if attr.lower() in haystack:
        return True
    return None  # vi vet inte
