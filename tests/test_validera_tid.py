import copy

import pytest

from bok.cli import main
from bok.graf import Graf
from bok.tid import Datum
from bok.validera import aldersvarningar, personer_med_fodd
from helpers import TIDGRAF, skriv, skriv_tidgraf

D94 = Datum(1994, 9, 28)


@pytest.fixture
def personer(bok):
    skriv_tidgraf(bok)
    return personer_med_fodd(Graf.load(bok))


def test_personer_med_fodd(personer):
    namn = {p[0]: p for p in personer}
    assert set(namn) == {"Marléne Östlund", "Sofia Östlund", "Henrik Ek"}
    assert "Marléne" in namn["Marléne Östlund"][1] and "Marléne Östlund" in namn["Marléne Östlund"][1]


@pytest.mark.parametrize("text", ["Marléne var 49.", "Den 48-åriga Marléne steg av.", "Sofia var 21.",
                                  "Marléne och Sofia var 30.", "Hon var 12 år då.",
                                  "Klockan var 12 när Marléne kom.", "Marléne var 20 minuter sen.",
                                  "Marléne såg att det var 100 meter kvar.", "Marléne köpte 3 bullar, 7, och gick."])
def test_inga_varningar(personer, text):
    assert aldersvarningar(text + "\n", personer, D94) == []


@pytest.mark.parametrize("text, del_", [
    ("Marléne var 52 år när hon kom in.", "texten säger 52"),
    ("Marlénes syster sa att Marléne var 52.", "texten säger 52"),
    ("Hennes mamma, Marléne, 60, kom.", "texten säger 60"),
    ("Marléne, 60, öppnade dörren.", "texten säger 60"),
    ("Sofia var 25.", "19–20 år"),
    ("Hon mötte den 30-åriga Sofia.", "texten säger 30"),
    ("Marléne var född 1950.", "född 1946 enligt grafen"),
])
def test_varningar(personer, text, del_):
    ut = aldersvarningar("Rubrik\n" + text + "\n", personer, D94)
    assert len(ut) == 1 and ut[0][0] == 2 and del_ in ut[0][1]


def test_cli_varning_och_blockerande_tidsfel(bok, capsys):
    g = copy.deepcopy(TIDGRAF)
    g["events"].append({"id": "e5", "kapitel": 2, "vad": "Mötet", "datum": "1994-01-01", "narvarande": ["henrik"]})
    skriv_tidgraf(bok, g)
    skriv(bok, "bok/plot/kapitel/kapitel-02.md", "---\nkapitel: 2\ndatum: 1994-09-28\n---\n")
    skriv(bok, "manuskript/kapitel-02.md", "Marléne var 52.\n")
    assert main(["validate"]) == 1
    out = capsys.readouterr().out
    assert "BLOCKERANDE" in out and "dog 1990-05-01" in out
    assert "Ålder att kontrollera rad 1" in out and "texten säger 52" in out


def test_cli_bara_varning_ger_exitkod_0(bok, capsys):
    skriv_tidgraf(bok)
    skriv(bok, "bok/plot/kapitel/kapitel-02.md", "---\nkapitel: 2\ndatum: 1994-09-28\n---\n")
    skriv(bok, "manuskript/kapitel-02.md", "Marléne var 52.\n")
    assert main(["validate"]) == 0
    assert "Ålder att kontrollera" in capsys.readouterr().out


def test_cli_kapitel_utan_datum_kontrolleras_inte(bok, capsys):
    skriv_tidgraf(bok)
    skriv(bok, "manuskript/kapitel-05.md", "Marléne var 90.\n")
    assert main(["validate"]) == 0
    assert "Ålder att kontrollera" not in capsys.readouterr().out


def test_cli_bok_utan_datum_som_forut(bok, capsys):
    skriv(bok, "manuskript/kapitel-01.md", "Det var en gång.\n")
    assert main(["validate"]) == 0
    out = capsys.readouterr().out
    assert "Tidslinjen" not in out and "Inga anmärkningar." in out
