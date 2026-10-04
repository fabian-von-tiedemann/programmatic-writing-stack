import pytest

from bok.boktoml import read
from bok.cli import main
from bok.init import DATA
from bok.mallar import BESKRIVNING, MallFel, lagg_till
from helpers import skriv


def test_moduler_stammer_med_beskrivningar():
    mappar = {p.name for p in (DATA / "moduler").iterdir() if p.is_dir()}
    assert mappar == set(BESKRIVNING)


def test_lagg_till_spanning(bok):
    skapade = lagg_till(bok, "spanning")
    assert "bok/plot/klocka.md" in skapade
    assert (bok / "bok/plot/ledtradar.md").is_file()
    assert read(bok)["moduler"] == ["spanning"]


def test_befintliga_filer_skrivs_inte_over(bok):
    skriv(bok, "bok/plot/klocka.md", "min klocka\n")
    lagg_till(bok, "spanning")
    assert (bok / "bok/plot/klocka.md").read_text() == "min klocka\n"
    assert lagg_till(bok, "spanning") == []


def test_okand_modul(bok):
    with pytest.raises(MallFel, match="spanning"):
        lagg_till(bok, "romantik")


def test_cli_listar(bok, capsys):
    assert main(["mall"]) == 0
    out = capsys.readouterr().out
    assert "spanning" in out and "serie" in out


def test_cli_lagger_till(bok, capsys):
    assert main(["mall", "serie"]) == 0
    assert "bok/plot/serie.md" in capsys.readouterr().out


def test_lagg_till_rostlabb(bok):
    skapade = lagg_till(bok, "rostlabb")
    for rel in ("bok/stil/labb/README.md", "bok/stil/labb/provscener.md", "bok/stil/provbank/README.md",
                "bok/stil/kontroll/README.md", "bok/stil/pekningar/README.md"):
        assert rel in skapade, rel
    assert read(bok)["moduler"] == ["rostlabb"]
