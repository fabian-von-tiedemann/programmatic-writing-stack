import io

import pytest

from bok.cli import main
from bok.rapport import RapportFel, las_alla, spara
from helpers import skriv

RED = """---
omfang: kapitel
kapitel: 3
roll: redaktor
runda: 1
betyg: {struktur: 8, karaktar: 7, spanning: 8, kontinuitet: 9, tema: 8}
utfall: revidera
blockerande: ["Tisdag blir torsdag"]
---

## Blockerande
- ...
"""


def test_sparar_granskarrapport(bok):
    path = spara(bok, RED)
    assert path == bok / "bok/rapporter/kapitel-03/redaktor-r1.md"
    assert path.read_text().startswith("---\nomfang: kapitel")


def test_godkand_kraver_atta(bok):
    with pytest.raises(RapportFel, match="kräver minst 8"):
        spara(bok, RED.replace("utfall: revidera", "utfall: godkand"))


def test_saknad_axel(bok):
    with pytest.raises(RapportFel, match="saknar axlar: tema"):
        spara(bok, RED.replace(", tema: 8", ""))


def test_okand_roll(bok):
    with pytest.raises(RapportFel, match="roll måste vara en av"):
        spara(bok, RED.replace("roll: redaktor", "roll: nagelfaren"))


def test_granskare_kraver_runda(bok):
    with pytest.raises(RapportFel, match="runda krävs"):
        spara(bok, RED.replace("runda: 1\n", ""))


def test_saknar_frontmatter(bok):
    with pytest.raises(RapportFel, match="saknar frontmatter"):
        spara(bok, "# Bara text\n")


def test_forberedelse_numreras_automatiskt(bok):
    text = "---\nomfang: forberedelse\nroll: forfattare\nutfall: godkand\n---\nJa.\n"
    assert spara(bok, text).name == "forfattare-r1.md"
    assert spara(bok, text).name == "forfattare-r2.md"
    assert spara(bok, text).parent == bok / "bok/rapporter/forberedelse"


def test_akt(bok):
    text = "---\nomfang: akt\nakt: 1\nroll: forlaggare\nutfall: fortsatt\n---\n"
    assert spara(bok, text) == bok / "bok/rapporter/akt-1/forlaggare-r1.md"


def test_finns_redan(bok):
    spara(bok, RED)
    with pytest.raises(RapportFel, match="finns redan"):
        spara(bok, RED)
    assert spara(bok, RED, skriv_over=True).name == "redaktor-r1.md"


def test_las_alla_hoppar_over_ogiltiga(bok):
    spara(bok, RED)
    skriv(bok, "bok/rapporter/kapitel-03/trasig.md", "---\nroll: x\n---\n")
    alla = las_alla(bok)
    assert [(r["roll"], r["runda"], r["kapitel"]) for r in alla] == [("redaktor", 1, 3)]


def test_cli_stdin_med_bom_crlf_och_tomrader(bok, capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("﻿\n\n" + RED.replace("\n", "\r\n")))
    assert main(["rapport", "spara", "-"]) == 0
    assert "Sparade bok/rapporter/kapitel-03/redaktor-r1.md" in capsys.readouterr().out
    assert "\r" not in (bok / "bok/rapporter/kapitel-03/redaktor-r1.md").read_text()


def test_cli_fel_visas_som_lista(bok, capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO(RED.replace("roll: redaktor", "roll: x")))
    assert main(["rapport", "spara", "-"]) == 2
    assert "Rapporten avvisades" in capsys.readouterr().err


def test_validera_roll_lista(bok):
    with pytest.raises(RapportFel, match="roll måste vara en av"):
        spara(bok, RED.replace("roll: redaktor", "roll: [redaktor]"))


def test_validera_utfall_lista(bok):
    with pytest.raises(RapportFel, match="utfall för"):
        spara(bok, RED.replace("utfall: revidera", "utfall: [revidera]"))


def test_validera_utfall_dict(bok):
    with pytest.raises(RapportFel, match="utfall för"):
        spara(bok, RED.replace("utfall: revidera", "utfall: {a: 1}"))


def test_las_alla_hoppar_over_roll_lista(bok):
    spara(bok, RED)
    skriv(bok, "bok/rapporter/kapitel-03/ogiltigt.md", "---\nroll: [redaktor]\nomfang: kapitel\nkapitel: 3\n---\n")
    alla = las_alla(bok)
    assert [(r["roll"], r["kapitel"]) for r in alla] == [("redaktor", 3)]


def test_cli_filinteFel(bok, capsys):
    assert main(["rapport", "spara", "finns-inte.md"]) == 2
    err = capsys.readouterr().err
    assert "Hittar inte" in err or "finns-inte.md" in err


def _granska_runda(bok, runda):
    spara(bok, RED.replace("runda: 1", f"runda: {runda}"))


def test_kontinuitet_far_senaste_granskningsrundan(bok):
    _granska_runda(bok, 1)
    _granska_runda(bok, 2)
    text = "---\nomfang: kapitel\nkapitel: 3\nroll: kontinuitet\nutfall: klar\n---\n"
    assert spara(bok, text).name == "kontinuitet-r2.md"


def test_kontinuitet_omkorning_i_samma_runda_kraver_skriv_over(bok):
    _granska_runda(bok, 1)
    text = "---\nomfang: kapitel\nkapitel: 3\nroll: kontinuitet\nutfall: klar\n---\n"
    spara(bok, text)
    with pytest.raises(RapportFel, match="--skriv-over"):
        spara(bok, text)
    assert spara(bok, text, skriv_over=True).name == "kontinuitet-r1.md"


def test_kontinuitet_och_forfattare_maste_galla_senaste_rundan(bok):
    _granska_runda(bok, 1)
    for roll, utfall in (("kontinuitet", "klar"), ("forfattare", "godkand")):
        text = f"---\nomfang: kapitel\nkapitel: 3\nroll: {roll}\nrunda: 2\nutfall: {utfall}\n---\n"
        with pytest.raises(RapportFel, match="senaste granskningsrundan"):
            spara(bok, text)


def test_kontinuitet_fore_granskning_avvisas(bok):
    text = "---\nomfang: kapitel\nkapitel: 3\nroll: kontinuitet\nutfall: klar\n---\n"
    with pytest.raises(RapportFel, match="inte granskats"):
        spara(bok, text)


def _researcher(runda=None):
    rad = f"runda: {runda}\n" if runda else ""
    return f"---\nomfang: kapitel\nkapitel: 3\nroll: researcher\n{rad}utfall: godkand\n---\n"


def test_fackgranskning_fore_forsta_granskningen(bok):
    assert spara(bok, _researcher()).name == "researcher-r1.md"


def test_fackgranskning_hor_till_kommande_runda(bok):
    _granska_runda(bok, 1)
    assert spara(bok, _researcher()).name == "researcher-r2.md"
    with pytest.raises(RapportFel, match="kommande granskningsrundan"):
        spara(bok, _researcher(1))
    with pytest.raises(RapportFel, match="--skriv-over"):
        spara(bok, _researcher())
    assert spara(bok, _researcher(2), skriv_over=True).name == "researcher-r2.md"


def test_sensitivitet_vid_forberedelse(bok):
    text = "---\nomfang: forberedelse\nroll: sensitivitet\nutfall: atgarda\n---\n"
    assert spara(bok, text) == bok / "bok/rapporter/forberedelse/sensitivitet-r1.md"
