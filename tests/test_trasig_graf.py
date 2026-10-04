"""Handredigerad json med fel typer får inte krascha något kommando."""

import pytest

from bok.cli import main
from helpers import fyll_forberedelse, skriv, skriv_graf

TRASIG = {
    "characters": [
        {"id": "anna", "namn": ["Anna"], "alias": "Annie", "fakta": ["veterinär"], "fodd": "1980"},
        {"id": "erik", "namn": 42, "alias": [7, None], "fakta": "38 år", "fodd": 1946, "dod": ["x"]},
        "inte ett objekt",
    ],
    "locations": [{"id": "garden", "namn": {"sv": "Gården"}, "alias": 3, "fakta": [1, 2]}],
    "events": [
        {"id": "e1", "kapitel": "1", "vad": ["kommer hem"], "plats": ["garden"], "narvarande": "anna",
         "datum": 1994},
        {"id": "e2", "kapitel": 2, "vad": None, "plats": "garden", "narvarande": ["anna", 5], "datum": "1994-13"},
        None,
    ],
    "secrets": [
        {"id": "s1", "vad": 3, "vet": "anna"},
        {"id": "s2", "vad": "x", "vet": [{"karaktar": ["anna"], "fran_kapitel": "1"}, "erik"]},
    ],
    "relationships": [
        {"fran": ["anna"], "till": "erik", "typ": 1, "forandringar": "ingen"},
        {"fran": "anna", "till": "erik", "typ": "syskon", "forandringar": [{"kapitel": "3", "typ": ["x"]}]},
    ],
    "threads": [
        {"id": "t1", "namn": ["Arvet"], "status": 1, "steg": "kapitel 1",
         "planteringar": {"vad": "Nyckeln"}, "start": "1"},
        {"id": "t2", "namn": "Arvet 2", "steg": [{"kapitel": "2", "vad": ["x"]}, 3],
         "planteringar": [{"vad": ["x"], "kapitel": "1"}, "nyckeln"]},
    ],
}

KOMMANDON = [
    ["status"],
    ["validate"],
    ["graph", "context", "--kapitel", "1"],
    ["graph", "context", "--kapitel", "2"],
    ["graph", "bagar"],
    ["graph", "karaktar", "anna"],
    ["graph", "karaktar", "erik"],
    ["graph", "var", "garden"],
    ["graph", "vem-vet", "s1"],
    ["graph", "vem-vet", "s2"],
    ["graph", "tidslinje"],
]


@pytest.fixture
def trasig(bok):
    fyll_forberedelse(bok)
    skriv_graf(bok, TRASIG)
    skriv(bok, "bok/plot/kapitel/kapitel-01.md", "---\nkapitel: 1\npov: anna\ndatum: 1994\ngodkand: true\n---\n\n# 1\n")
    skriv(bok, "manuskript/kapitel-01.md", "# Kapitel 1\n\nAnna var 14 när Erik kom hem till Gården.\n")
    return bok


@pytest.mark.parametrize("argv", KOMMANDON, ids=" ".join)
def test_kraschar_inte(trasig, argv, capsys):
    assert main(argv) in (0, 1, 2)
    assert "Traceback" not in capsys.readouterr().err


def test_fakta_som_lista_eller_text_visas(trasig, capsys):
    main(["graph", "karaktar", "anna"])
    assert "- veterinär" in capsys.readouterr().out
    main(["graph", "karaktar", "erik"])
    out = capsys.readouterr().out
    assert "- 38 år" in out and "# erik (erik)" in out


def test_alias_som_text_raknas_som_namn():
    from bok.graf import namnformer
    assert namnformer({"namn": "Anna Berg", "alias": "Annie"}) == ["Anna Berg", "Annie"]
    assert namnformer({"namn": ["Anna"], "alias": [7, " Annie "]}) == ["Annie"]
