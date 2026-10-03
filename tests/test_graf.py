import json

import pytest

from bok.cli import main
from bok.graf import Graf, GrafFel
from helpers import skriv, skriv_graf


@pytest.fixture
def graf(bok):
    skriv_graf(bok)
    return Graf.load(bok)


def test_vem_vet(graf):
    alla = graf.vem_vet("s-arvet")
    assert "Erik Berg (från kapitel 1)" in alla and "Anna Berg (från kapitel 3)" in alla
    vid2 = graf.vem_vet("s-arvet", kapitel=2)
    assert "Erik Berg" in vid2 and "Anna Berg" not in vid2


def test_okant_id_ger_forslag(graf):
    with pytest.raises(GrafFel, match="Menade du: s-arvet"):
        graf.vem_vet("s-arve")


def test_karaktar(graf):
    out = graf.karaktar("anna")
    assert "veterinär" in out
    assert "Erik Berg: syskon i konflikt" in out
    assert "1, 2" in out
    assert "Gården är redan såld" in out


def test_var(graf):
    out = graf.var("garden", kapitel=2)
    assert "testamentet" in out and "kommer hem" not in out


def test_bagar(graf):
    out = graf.bagar()
    assert "Senast i kapitel 2." in out
    assert "Olöst plantering (kapitel 1): Nyckeln i ladan" in out
    assert "Gammal" in out
    assert "Gammal" not in graf.bagar(oppna=True)


def test_context_visar_laget_fore_kapitlet(graf):
    out = graf.context(3, ["anna", "erik", "ny"], ["garden"], ["t-arvet", "t-planerad"])
    assert "Relation till Erik Berg: syskon\n" in out
    assert "syskon i konflikt" not in out
    anna = out.split("### Anna Berg")[1].split("###")[0]
    assert "Vet:" not in anna
    erik = out.split("### Erik Berg")[1].split("###")[0]
    assert "Vet: Gården är redan såld" in erik
    assert "Ny i kapitlet" in out
    assert "t-planerad" in out and "inte påbörjats" in out
    assert "## Förra kapitlet" in out and "testamentet" in out


def test_trasig_json(bok):
    skriv(bok, "bok/story-graph/events.json", "{")
    with pytest.raises(GrafFel, match="events.json rad 1"):
        Graf.load(bok)


def test_fel_form(bok):
    skriv(bok, "bok/story-graph/events.json", "[]")
    with pytest.raises(GrafFel, match="ska ha formen"):
        Graf.load(bok)


def test_tom_graf_fungerar(bok):
    assert "Inga bågar" in Graf.load(bok).bagar()


def test_cli_context_utan_scenkort(bok, capsys):
    assert main(["graph", "context", "--kapitel", "3"]) == 2
    assert "Scenkortet" in capsys.readouterr().err


def test_cli_context_med_ofyllt_scenkort(bok, capsys):
    mall = (bok / "bok/plot/kapitel/MALL.md").read_text()
    skriv(bok, "bok/plot/kapitel/kapitel-03.md", mall)
    assert main(["graph", "context", "--kapitel", "3"]) == 2
    assert "inte ifyllt" in capsys.readouterr().err


def test_cli_context(bok, capsys):
    skriv_graf(bok)
    skriv(bok, "bok/plot/kapitel/kapitel-03.md",
          "---\nkapitel: 3\npov: anna\nkaraktarer: [anna, erik]\nplatser: [garden]\n"
          "bagar: [t-arvet]\ngodkand: true\n---\n\n# Kapitel 3\n")
    assert main(["graph", "context", "--kapitel", "3"]) == 0
    assert "# Underlag för kapitel 3" in capsys.readouterr().out


def test_cli_vem_vet(bok, capsys):
    skriv_graf(bok)
    assert main(["graph", "vem-vet", "s-arvet", "--kapitel", "2"]) == 0
    assert "Erik Berg" in capsys.readouterr().out


def _graf_med_trad(bok, trad):
    skriv_graf(bok)
    skriv(bok, "bok/story-graph/threads.json", json.dumps({"threads": [trad]}, ensure_ascii=False))
    return Graf.load(bok)


def test_context_visar_plantering_som_var_oppen_da(bok):
    g = _graf_med_trad(bok, {
        "id": "t-x", "namn": "X", "typ": "intrig", "status": "oppen", "steg": [],
        "planteringar": [{"vad": "Nyckeln", "kapitel": 1, "loses_i": 5}],
    })
    assert "Olöst plantering (kapitel 1): Nyckeln" in g.context(3, [], [], ["t-x"])
    assert "Nyckeln" not in g.context(6, [], [], ["t-x"])
    assert "Olöst plantering" not in g.bagar()


def test_kapitelfalt_som_inte_ar_heltal_kraschar_inte(bok):
    skriv_graf(bok)
    skriv(bok, "bok/story-graph/events.json", json.dumps({"events": [
        {"id": "e1", "kapitel": "3", "vad": "A", "plats": "garden", "narvarande": ["anna"]},
        {"id": "e2", "kapitel": None, "vad": "B", "plats": "garden", "narvarande": ["anna"]},
        {"id": "e3", "kapitel": 1, "vad": "C", "plats": "garden", "narvarande": ["anna"]},
    ]}))
    skriv(bok, "bok/story-graph/threads.json", json.dumps({"threads": [
        {"id": "t-y", "namn": "Y", "typ": "intrig", "status": "oppen",
         "steg": [{"kapitel": "3", "vad": "a"}, {"kapitel": None, "vad": "b"}, {"kapitel": 2, "vad": "c"}],
         "planteringar": [{"vad": "P", "kapitel": "1", "loses_i": "4"}]},
    ]}))
    skriv(bok, "bok/story-graph/secrets.json", json.dumps({"secrets": [
        {"id": "s", "vad": "S", "vet": [{"karaktar": "anna", "fran_kapitel": None}, {"karaktar": "erik", "fran_kapitel": "2"}]},
    ]}))
    skriv(bok, "bok/story-graph/relationships.json", json.dumps({"relationships": [
        {"fran": "anna", "till": "erik", "typ": "syskon",
         "forandringar": [{"kapitel": None, "typ": "a"}, {"kapitel": "2", "typ": "b"}]},
    ]}))
    g = Graf.load(bok)
    g.context(3, ["anna", "erik"], ["garden"], ["t-y"])
    g.bagar()
    g.karaktar("anna")
    g.var("garden")
    g.vem_vet("s", kapitel=2)
