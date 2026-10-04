import json

import pytest

from bok.cli import main
from bok.graf import GrafFel
from bok.mallar import lagg_till
from bok.rost import urval
from helpers import skriv


def scenkort(root, lage):
    rad = f"lage: {lage}\n" if lage else ""
    skriv(root, "bok/plot/kapitel/kapitel-03.md", f"---\nkapitel: 3\n{rad}godkand: true\n---\n\n# Kapitel 3\n")


def stycke(root, namn, lage, datum):
    huvud = f"lage: {lage}\n" if lage else ""
    huvud += f"datum: {datum}\n" if datum else ""
    skriv(root, f"bok/stil/provbank/{namn}.md", f"---\n{huvud}---\nText.\n")


@pytest.fixture
def labb(bok):
    lagg_till(bok, "rostlabb")
    stycke(bok, "a", "stilla", "2026-10-01")
    stycke(bok, "b", "tryck", "2026-10-03")
    stycke(bok, "c", "tryck", "2026-10-02")
    stycke(bok, "d", "tryck", None)
    stycke(bok, "e", "tryck", "2026-10-03")
    return bok


def test_valjer_lage_nyast_forst_och_namn_vid_lika(labb):
    scenkort(labb, "tryck")
    assert [p.name for p in urval(labb, 3)] == ["b.md", "e.md", "c.md"]
    assert [p.name for p in urval(labb, 3, antal=10)] == ["b.md", "e.md", "c.md", "d.md"]


def test_utan_lage_valjs_ur_hela_banken(labb):
    scenkort(labb, None)
    assert [p.name for p in urval(labb, 3, antal=2)] == ["b.md", "e.md"]


def test_lage_som_ingen_har_faller_tillbaka_pa_hela_banken(labb):
    scenkort(labb, "drom")
    assert len(urval(labb, 3, antal=5)) == 5


def test_trasigt_huvud_i_banken_kraschar_inte(labb):
    skriv(labb, "bok/stil/provbank/f.md", "---\nlage: tryck\nText utan slut på huvudet.\n")
    scenkort(labb, "tryck")
    assert "f.md" not in [p.name for p in urval(labb, 3, antal=10)]  # utan lage väljs det inte för tryck
    scenkort(labb, None)
    assert "f.md" in [p.name for p in urval(labb, 3, antal=10)]


def test_saknat_scenkort_ar_fel(labb):
    with pytest.raises(GrafFel):
        urval(labb, 3)


def test_cli_urval(labb, capsys):
    scenkort(labb, "tryck")
    assert main(["rost", "urval", "--kapitel", "3", "--antal", "2"]) == 0
    assert capsys.readouterr().out.splitlines() == ["bok/stil/provbank/b.md", "bok/stil/provbank/e.md"]
    assert main(["rost", "urval", "--kapitel", "3", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["lage"] == "tryck"
    assert main(["rost", "urval", "--kapitel", "9"]) == 2
