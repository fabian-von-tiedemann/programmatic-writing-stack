import json

import pytest

from bok.cli import main
from bok.init import DATA
from bok.tics import TicsFel, parse_katalog, scan
from helpers import skriv


def test_katalogen_i_paketet_gar_att_lasa():
    text = (DATA / "genererat/claude/bok/tics-katalog.md").read_text()
    tics = parse_katalog(text, "katalog")
    assert len(tics) >= 15
    assert {t.namn for t in tics} >= {"nickade", "som om", "plötsligt"}


def test_parse_tak():
    tics = parse_katalog("```tics\na | \\ba\\b | kapitel=2, bok=5 | k\nb | \\bb\\b | -\n```\n", "x")
    assert (tics[0].tak_kapitel, tics[0].tak_bok, tics[0].kommentar) == (2, 5, "k")
    assert (tics[1].tak_kapitel, tics[1].tak_bok) == (None, None)


def test_ogiltigt_monster():
    with pytest.raises(TicsFel, match="ogiltigt mönster för a"):
        parse_katalog("```tics\na | ( | - | x\n```\n", "x")


def test_rad_utan_separator():
    with pytest.raises(TicsFel, match="namn \\| regex"):
        parse_katalog("```tics\nbara text\n```\n", "x")


def test_scan_raknar_forekomster():
    tics = parse_katalog("```tics\nnickade | \\bnickade\\b | kapitel=2 | x\n```\n", "x")
    out = scan("Hon nickade. Han nickade.\nDe nickade inte.\n", tics)
    assert out["nickade"] == [(1, "Hon nickade. Han nickade.", 2), (2, "De nickade inte.", 1)]


def test_skiftlage_ignoreras():
    tics = parse_katalog("```tics\nplötsligt | \\bplötsligt\\b | - | x\n```\n", "x")
    assert "plötsligt" in scan("Plötsligt small det.\n", tics)


def test_cli_over_tak(bok, capsys):
    skriv(bok, "manuskript/kapitel-01.md", "Hon nickade. Han nickade. De nickade.\n")
    assert main(["tics"]) == 0
    out = capsys.readouterr().out
    assert "manuskript/kapitel-01.md" in out
    assert "nickade: 3 [ÖVER TAK 2/kapitel]" in out


def test_cli_bokens_egna_tics(bok, capsys):
    skriv(bok, "bok/tics-tillagg.md", "```tics\nkaffe | \\bkaffe\\b | kapitel=1 | Hon dricker för mycket kaffe.\n```\n")
    skriv(bok, "manuskript/kapitel-01.md", "Kaffe. Mer kaffe.\n")
    main(["tics"])
    assert "kaffe: 2 [ÖVER TAK 1/kapitel]" in capsys.readouterr().out


def test_cli_hela_boken(bok, capsys):
    for n in range(1, 4):
        skriv(bok, f"manuskript/kapitel-{n:02d}.md", "Plötsligt. Plötsligt. Plötsligt. Plötsligt.\n")
    main(["tics", "--bok"])
    out = capsys.readouterr().out
    assert "Hela boken" in out and "plötsligt: 12 [ÖVER TAK 10/bok]" in out


def test_cli_json(bok, capsys):
    skriv(bok, "manuskript/kapitel-01.md", "Hon nickade.\n")
    main(["tics", "--json"])
    data = json.loads(capsys.readouterr().out)
    assert data["filer"]["manuskript/kapitel-01.md"]["nickade"]["antal"] == 1


def test_cli_utan_kapitel(bok, capsys):
    assert main(["tics"]) == 0
    assert "Inga kapitel" in capsys.readouterr().out
