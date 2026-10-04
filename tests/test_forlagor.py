from bok.cli import main
from bok.forlagor import forlagor
from bok.validera import blacklist_traffar, forlageskydd
from helpers import skriv

FIL = "bok/karaktarer/forlagor/cathie-wood.md"
WOOD = "---\nnamn: Cathie Wood\nalias: [Catherine Wood]\nkaraktarer: [vera]\n---\n\n# Cathie Wood\n"


def test_forlagor_laser_namn_och_alias(bok):
    skriv(bok, FIL, WOOD)
    assert forlagor(bok) == [{"fil": FIL, "namn": "Cathie Wood", "alias": ["Catherine Wood"]}]


def test_mall_och_readme_ar_inte_forlagor(bok):
    skriv(bok, "bok/karaktarer/forlagor/MALL.md", "---\nnamn: {{Personens namn}}\n---\n")
    skriv(bok, "bok/karaktarer/forlagor/README.md", "# Förlagor\n")
    assert forlagor(bok) == []


def test_saknad_mapp_ger_tom_lista(tmp_path):
    assert forlagor(tmp_path) == []


def test_trasigt_huvud_och_fel_typer_kraschar_inte(bok):
    skriv(bok, "bok/karaktarer/forlagor/a.md", "---\nnamn: [trasig\n---\n")
    skriv(bok, "bok/karaktarer/forlagor/b.md", "---\nnamn: 42\nalias: Kalle Ek\n---\n")
    skriv(bok, "bok/karaktarer/forlagor/c.md", "---\nnamn: {{Personens namn}}\n---\n")
    skriv(bok, "bok/karaktarer/forlagor/d.md", "# Utan huvud\n")
    assert [(f["namn"], f["alias"]) for f in forlagor(bok)] == [
        (None, []), (None, ["Kalle Ek"]), (None, []), (None, [])]


def test_blacklist_tar_genitiv():
    assert blacklist_traffar("Hon läste Olof Palmes tal.\n", ["Olof Palme"]) == [(1, "Olof Palme")]
    assert blacklist_traffar("Olof Palmeström\n", ["Olof Palme"]) == []


def test_forlageskydd_undantar_kanda_namn(bok):
    skriv(bok, FIL, WOOD)
    skydd, utan = forlageskydd(bok, "```kanda-namn\nCathie Wood\n```\n")
    assert skydd == {"Catherine Wood": FIL}
    assert utan == []


def test_cli_forlaga_i_manus_blockerar(bok, capsys):
    skriv(bok, FIL, WOOD)
    skriv(bok, "manuskript/kapitel-01.md", "Hon hade sett Cathie Woods intervju.\n")
    assert main(["validate"]) == 1
    out = capsys.readouterr().out
    assert f"BLOCKERANDE rad 1: Cathie Wood är förlaga ({FIL}) och får inte stå i manuset." in out


def test_cli_forlaga_bland_kanda_namn_blockerar_inte(bok, capsys):
    skriv(bok, FIL, "---\nnamn: Cathie Wood\n---\n")
    skriv(bok, "bok/canon.md", "# Canon\n\n```kanda-namn\nCathie Wood\n```\n")
    skriv(bok, "manuskript/kapitel-01.md", "Hon hade sett Cathie Wood på tv.\n")
    assert main(["validate"]) == 0


def test_cli_forlaga_utan_namn_varnar(bok, capsys):
    skriv(bok, "bok/karaktarer/forlagor/x.md", "# Ingen\n")
    skriv(bok, "manuskript/kapitel-01.md", "Hon gick hem.\n")
    assert main(["validate"]) == 0
    assert "bok/karaktarer/forlagor/x.md saknar namn i huvudet; namnet skyddas inte i manuset." in capsys.readouterr().out
