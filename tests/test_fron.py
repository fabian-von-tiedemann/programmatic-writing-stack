import json

import pytest

from bok.cli import main
from bok.fron import FRON, KLASSER, FronFel, dra, lista
from helpers import skriv

LISTOR = [k for k in KLASSER if k != "forlaga"]


@pytest.mark.parametrize("klass", LISTOR)
def test_listorna(klass):
    fron = lista(klass)
    assert len(fron) >= 40
    assert len(set(fron)) == len(fron)
    assert all(len(f) <= 140 and not f.endswith(".") for f in fron)


def test_inga_listor_utover_klasserna():
    assert {p.stem for p in FRON.glob("*.txt")} == set(LISTOR)


def test_samma_slump_ger_samma_fron():
    assert dra(slump=7) == dra(slump=7)
    assert dra(slump=7)["fron"] != dra(slump=8)["fron"]


def test_standardfordelning_utan_forlagor():
    klasser = [f["klass"] for f in dra(slump=1)["fron"]]
    assert klasser[:3] == ["doman", "omvandning", "begransning"]
    assert klasser[3] in ("doman", "omvandning", "begransning")


def test_forlaga_blir_fjarde_frot(bok):
    skriv(bok, "bok/karaktarer/forlagor/cathie-wood.md", "---\nnamn: Cathie Wood\n---\n")
    fron = dra(slump=1, root=bok)["fron"]
    assert fron[3] == {"klass": "forlaga",
                       "text": "Cathie Wood (bok/karaktarer/forlagor/cathie-wood.md)", "antagande": None}


def test_forlaga_utan_forlagor_ar_fel(bok):
    with pytest.raises(FronFel, match="inga förlagor"):
        dra(klasser=["forlaga"], antal=1, root=bok)


def test_omvandning_paras_med_antagande():
    antaganden = ["det sker i en scen", "hon är ensam"]
    fron = dra(klasser=["omvandning"], antal=3, antaganden=antaganden, slump=3)["fron"]
    assert all(f["antagande"] in antaganden for f in fron)
    andra = dra(klasser=["doman"], antal=2, antaganden=antaganden, slump=3)["fron"]
    assert all(f["antagande"] is None for f in andra)


def test_inga_dubbletter_i_en_dragning():
    alla = lista("process")
    fron = [f["text"] for f in dra(klasser=["process"], antal=len(alla), slump=5)["fron"]]
    assert sorted(fron) == sorted(alla)


def test_slut_pa_fron_ar_fel():
    with pytest.raises(FronFel, match="inte fler frön"):
        dra(klasser=["process"], antal=len(lista("process")) + 1, slump=5)


def test_antal_noll_ar_fel():
    with pytest.raises(FronFel, match="minst 1"):
        dra(antal=0)


def test_utan_slump_valjs_ett_tal():
    assert isinstance(dra()["slump"], int)


def test_cli_json(bok, capsys):
    assert main(["fron", "--slump", "42", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["slump"] == 42 and len(data["fron"]) == 4
    assert set(data["fron"][0]) == {"klass", "text", "antagande"}


def test_cli_text(bok, capsys):
    assert main(["fron", "--slump", "42", "--antal", "2"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("Slump 42 (samma frön igen: --slump 42)\n1. doman: ")
    assert "\n2. omvandning: " in out


def test_cli_spara_lagger_till(bok):
    mapp = bok / "bok/vagval/2026-10-04-test"
    assert main(["fron", "--slump", "1", "--spara", str(mapp)]) == 0
    assert main(["fron", "--klass", "process", "--antal", "1", "--slump", "2", "--spara", str(mapp)]) == 0
    text = (mapp / "fron.md").read_text(encoding="utf-8")
    assert text.startswith("# Frön\n\n## Slump 1\n\n1. **doman**: ")
    assert "\n## Slump 2\n\n1. **process**: " in text
    assert text.count("# Frön") == 1


def test_cli_spara_relativt_ligger_under_bokens_rot(bok, monkeypatch):
    (bok / "manuskript").mkdir(exist_ok=True)
    monkeypatch.chdir(bok / "manuskript")
    assert main(["fron", "--slump", "1", "--spara", "bok/vagval/x"]) == 0
    assert (bok / "bok/vagval/x/fron.md").is_file()
    assert not (bok / "manuskript/bok").exists()


def test_cli_okand_klass(bok):
    with pytest.raises(SystemExit):
        main(["fron", "--klass", "planeter"])


def test_cli_fel_blir_exitkod_2(bok, capsys):
    assert main(["fron", "--klass", "forlaga", "--antal", "1"]) == 2
    assert "inga förlagor" in capsys.readouterr().err


def test_cli_utanfor_en_bok(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["fron", "--slump", "1", "--antal", "1"]) == 0
    assert "1. doman: " in capsys.readouterr().out


NYA = ("rostdrag", "formgrepp", "kalla")


def test_nya_klasser_finns_men_dras_inte_som_standard():
    assert set(NYA) <= set(KLASSER)
    for slump in range(20):
        assert not {f["klass"] for f in dra(antal=8, slump=slump)["fron"]} & set(NYA)


def test_rostlabbets_dragning():
    fron = dra(antal=6, klasser=list(NYA), slump=11)["fron"]
    assert [f["klass"] for f in fron] == ["rostdrag", "formgrepp", "kalla"] * 2
