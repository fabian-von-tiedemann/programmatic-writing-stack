import json

import pytest

from bok.cli import main
from bok.mallar import lagg_till
from bok.rost import (MATT, RostFel, dela_meningar, funktionsord, krav_modul, matt, ord_i, profil, pronomen,
                      ren_text, stycken, texter)
from helpers import skriv


def bank(root, namn, text, lage="stilla", datum="2026-10-01", mapp="provbank"):
    return skriv(root, f"bok/stil/{mapp}/{namn}.md",
                 f"---\nlage: {lage}\nkalla: gen-01 A\ndatum: {datum}\n---\n\n{text}\n")


def test_datafilerna():
    fo = funktionsord()
    assert len(fo) >= 100 and len(set(fo)) == len(fo)
    assert {"och", "att", "det", "som"} <= set(fo)
    assert {"jag", "du", "han", "hon", "hen", "vi", "de", "man"} <= pronomen()


def test_ren_text_tar_bort_huvud_rubriker_och_kommentarer():
    text = "---\nlage: stilla\n---\n# Rubrik\n\nHon gick.<!-- not -->\n\n## Under\nHan stod kvar.\n"
    assert ren_text(text) == "Hon gick.\n\nHan stod kvar."


def test_ren_text_tal_crlf_bom_och_trasigt_huvud():
    assert ren_text("﻿---\r\nlage: tryck\r\n---\r\nHon gick.\r\n") == "Hon gick."
    assert ren_text("---\nlage: tryck\nHon gick.\n") == "---\nlage: tryck\nHon gick."


def test_meningar_och_stycken():
    assert dela_meningar('Hon gick. – Kom hit, sa han. "Nej." Hon log! Vad? 3 st. och sen.') == [
        "Hon gick.", "– Kom hit, sa han.", '"Nej."', "Hon log!", "Vad? 3 st. och sen."]
    assert stycken("Ett.\nTvå.\n\n\nTre.") == ["Ett. Två.", "Tre."]
    assert ord_i("Det var Åsa-Lena, 34 år.") == ["det", "var", "åsa-lena", "år"]


def test_matt_kanda_varden():
    text = ("Hon gick hem.\n\n"                                        # 3 ord
            "Han satt kvar vid bordet; det var sent och mörkt ute.\n\n"  # 11 ord
            "– Kom nu, sa hon.\n\n"                                     # 4 ord, replik
            "Det var en lång dag: regn, vind, kyla och sedan ingenting mer än tystnad i huset.")  # 16 ord
    m = matt(text)
    assert set(m) == set(MATT)
    assert m["meningslangd_median"] == 7.5
    assert m["meningslangd_kvartilavstand"] == pytest.approx(12.25 - 3.75)
    assert m["andel_korta"] == 0.5
    assert m["andel_langa"] == 0
    assert m["styckelangd_median"] == 1
    assert m["replikandel"] == pytest.approx(4 / 34)
    assert m["komma"] == pytest.approx(3 * 1000 / 34)
    assert m["semikolon"] == pytest.approx(1000 / 34)
    assert m["kolon"] == pytest.approx(1000 / 34)
    assert m["tankstreck"] == 0
    assert m["fragetecken"] == 0
    assert m["pronomenstart"] == 0.75  # hon, han, det; inte "kom"


def test_matt_tom_text_ger_nollor():
    assert set(matt("").values()) == {0}


def test_profil():
    p = profil(["Hon gick. Han stod.", "Det var sent och mörkt ute i staden den kvällen."])
    assert p["antal"] == 2
    assert p["matt"]["meningslangd_median"] == {"median": 6.0, "min": 2, "max": 10}


def test_krav_modul(bok):
    with pytest.raises(RostFel, match="bok mall rostlabb"):
        krav_modul(bok)
    lagg_till(bok, "rostlabb")
    krav_modul(bok)


def test_texter_hoppar_over_readme_och_tal_trasigt_huvud(bok):
    lagg_till(bok, "rostlabb")
    bank(bok, "a", "Hon gick.")
    skriv(bok, "bok/stil/provbank/b.md", "---\nlage: tryck\nHan sprang.\n")
    t = texter(bok, "provbank")
    assert [p.name for p, _, _ in t] == ["a.md", "b.md"]
    assert t[0][1]["lage"] == "stilla" and t[1][1] == {}


def test_cli_profil(bok, capsys):
    lagg_till(bok, "rostlabb")
    bank(bok, "a", "Hon gick. Han stod.")
    bank(bok, "b", "Det var sent och mörkt ute i staden den kvällen.")
    assert main(["rost", "profil"]) == 0
    out = capsys.readouterr().out
    assert "2 provstycken" in out and "meningslangd_median" in out
    assert main(["rost", "profil", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["antal"] == 2


def test_cli_profil_tom_bank_och_utan_modul(bok, capsys):
    assert main(["rost", "profil"]) == 2
    lagg_till(bok, "rostlabb")
    assert main(["rost", "profil"]) == 2
    assert "tom" in capsys.readouterr().err
