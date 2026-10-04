import json

import pytest

from bok.cli import main
from bok.mallar import lagg_till
from bok.rost import RostFel, dela_meningar, drift, matt, profil, stycken, urval
from helpers import skriv


def test_repliker_pa_egna_rader_ar_egna_stycken():
    tat = "Hon kom hem.\n– Var har du varit?\n– Ute."
    luft = "Hon kom hem.\n\n– Var har du varit?\n\n– Ute."
    assert stycken(tat) == stycken(luft)
    assert matt(tat) == matt(luft)


def test_scenbrytningar_ar_inga_stycken():
    assert stycken("Hon gick.\n\n* * *\n\nHan stod.\n\n---\n\nSlut.") == ["Hon gick.", "Han stod.", "Slut."]


def test_meningsdelning_forkortningar_siffror_och_parentes():
    assert dela_meningar("Hon tog t.ex. Anna med sig. Sedan gick de.") == [
        "Hon tog t.ex. Anna med sig.", "Sedan gick de."]
    assert dela_meningar("Det var sent. 1984 dog han.") == ["Det var sent.", "1984 dog han."]
    assert dela_meningar("Hon log (utan att veta varför.) Han gick.") == [
        "Hon log (utan att veta varför.)", "Han gick."]


def test_profil_har_funktionsordens_frekvenser():
    p = profil(["Hon och han och det.", "Det var hon som gick."])
    assert p["funktionsord"]["och"] == pytest.approx((2 / 5 + 0) / 2)
    assert "katt" not in p["funktionsord"]


def test_cli_profil_visar_vanligaste_funktionsorden(bok, capsys):
    lagg_till(bok, "rostlabb")
    skriv(bok, "bok/stil/provbank/a.md", "Hon och han och det.\n")
    assert main(["rost", "profil"]) == 0
    assert "Vanligaste funktionsorden: och" in capsys.readouterr().out


@pytest.fixture
def labb(bok):
    lagg_till(bok, "rostlabb")
    skriv(bok, "bok/plot/kapitel/kapitel-03.md", "---\nkapitel: 3\nlage: Stilla\ngodkand: true\n---\n# K\n")
    for namn, lage, datum in (("a", "stilla", "2026-9-4"), ("b", "stilla", "2026-10-01"), ("c", "tryck", "2026-12-01")):
        skriv(bok, f"bok/stil/provbank/{namn}.md", f"---\nlage: {lage}\ndatum: {datum}\n---\nText.\n")
    return bok


def test_urval_lage_utan_skiftlage_och_datum_som_datum(labb):
    assert [p.name for p in urval(labb, 3)] == ["b.md", "a.md"]


def test_urval_antal_maste_vara_minst_ett(labb):
    with pytest.raises(RostFel, match="--antal"):
        urval(labb, 3, antal=0)
    assert main(["rost", "urval", "--kapitel", "3", "--antal", "-1"]) == 2


def test_drift_json_ar_avrundad(bok, capsys):
    lagg_till(bok, "rostlabb")
    for i, t in enumerate(["Hon gick. Han stod.", "Det var sent.", "Hon sov."]):
        skriv(bok, f"bok/stil/provbank/r{i}.md", t + "\n")
    for i, t in enumerate(["När hon kom hem hade han gått, som alltid.", "Rummet var tomt, som när det regnat."]):
        skriv(bok, f"bok/stil/kontroll/k{i}.md", t + "\n")
    skriv(bok, "manuskript/kapitel-01.md", "Det var en lång kväll, och hon satt kvar, länge, vid bordet i köket.\n")
    assert main(["rost", "drift", "manuskript/kapitel-01.md", "--json"]) == 0
    utanfor = json.loads(capsys.readouterr().out)["utanfor"]
    assert any(x["varde"] != int(x["varde"]) for x in utanfor)
    for x in utanfor:
        for nyckel in ("varde", "min", "max"):
            assert x[nyckel] == round(x[nyckel], 3)
