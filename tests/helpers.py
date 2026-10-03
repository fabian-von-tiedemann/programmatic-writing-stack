import json
from pathlib import Path


def skriv(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


GRAF = {
    "characters": [
        {"id": "anna", "namn": "Anna Berg", "alias": ["Annie"],
         "fakta": {"ålder": "34", "yrke": "veterinär"}},
        {"id": "erik", "namn": "Erik Berg", "fakta": {"ålder": "38"}},
    ],
    "locations": [{"id": "garden", "namn": "Gården", "fakta": {"läge": "vid sjön"}}],
    "events": [
        {"id": "e1", "kapitel": 1, "vad": "Anna kommer hem till gården",
         "plats": "garden", "narvarande": ["anna"]},
        {"id": "e2", "kapitel": 2, "vad": "Erik visar testamentet",
         "plats": "garden", "narvarande": ["anna", "erik"]},
    ],
    "secrets": [
        {"id": "s-arvet", "vad": "Gården är redan såld", "sanning": "Erik sålde den",
         "vet": [{"karaktar": "erik", "fran_kapitel": 1}, {"karaktar": "anna", "fran_kapitel": 3}]},
    ],
    "relationships": [
        {"fran": "anna", "till": "erik", "typ": "syskon",
         "forandringar": [{"kapitel": 3, "typ": "syskon i konflikt"}]},
    ],
    "threads": [
        {"id": "t-arvet", "namn": "Arvet", "typ": "intrig", "status": "oppen",
         "steg": [{"kapitel": 1, "vad": "Anna kommer hem"}, {"kapitel": 2, "vad": "Testamentet"}],
         "planteringar": [{"vad": "Nyckeln i ladan", "kapitel": 1, "loses_i": None}]},
        {"id": "t-gammal", "namn": "Gammal", "typ": "tema", "status": "stangd", "steg": []},
    ],
}


def skriv_graf(root, graf=GRAF):
    for nyckel, lista in graf.items():
        skriv(root, f"bok/story-graph/{nyckel}.json", json.dumps({nyckel: lista}, ensure_ascii=False))


def fyll_forberedelse(root):
    for rel in ["bok/koncept/premiss.md", "bok/koncept/genre.md", "bok/koncept/form.md",
                "bok/koncept/teman.md", "bok/plot/struktur.md", "bok/plot/bagar.md", "bok/stil/rost.md"]:
        skriv(root, rel, f"# {rel}\n\nIfylld.\n")
    skriv(root, "bok/karaktarer/anna.md", "---\nid: anna\nnamn: Anna Berg\npov: true\n---\n\n# Anna\n")
    skriv(root, "bok/plot/kapitelplan.md",
          "# Kapitelplan\n\n| Kapitel | Akt | POV | Funktion | Bågar |\n|---|---|---|---|---|\n"
          "| 1 | 1 | anna | Start | t-arvet |\n| 2 | 1 | anna | Fördjupning | t-arvet |\n"
          "| 3 | 2 | anna | Vändning | t-arvet |\n")


def rapport(root, body="", **meta):
    from bok.rapport import spara

    rader = []
    for k, v in meta.items():
        if isinstance(v, dict):
            v = "{" + ", ".join(f"{a}: {b}" for a, b in v.items()) + "}"
        rader.append(f"{k}: {v}")
    return spara(root, "---\n" + "\n".join(rader) + "\n---\n" + body)


BRA_RED = {"struktur": 8, "karaktar": 8, "spanning": 8, "kontinuitet": 8, "tema": 8}
BRA_SPRAK = {"prosa": 8, "dialog": 8, "rost": 8}
