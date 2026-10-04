from bok.cli import main
from bok.validera import andrade_stallen, lasta_stallen
from helpers import skriv

PEK = ('# Pekningar\n\n## Lever\n- "Han räknade stolarna två gånger innan han satte sig."\n'
       '- “Det var  inte\nhennes sak.”\n\n## Dött\n- "Tystnaden lade sig."\n\n'
       '## Upplåst\n- "Gammalt citat som inte längre gäller."\n')


def test_lasta_stallen_laser_bara_lever(bok):
    skriv(bok, "bok/stil/pekningar/kapitel-03.md", PEK)
    assert lasta_stallen(bok, 3) == ["Han räknade stolarna två gånger innan han satte sig.",
                                     "Det var inte"]
    assert lasta_stallen(bok, 4) == []


def test_andrade_stallen_normaliserar_blanktecken_och_citattecken():
    text = "Hon tittade upp.\nHan räknade stolarna två gånger\ninnan han satte sig. ”Nej.”"
    assert andrade_stallen(text, ["Han räknade stolarna två gånger innan han satte sig.", '"Nej."']) == []
    assert andrade_stallen("Han räknade stolarna en gång.", ["Han räknade stolarna två gånger."]) == [
        "Han räknade stolarna två gånger."]


def test_validate_stoppar_andrat_last_stalle(bok, capsys):
    skriv(bok, "bok/stil/pekningar/kapitel-03.md",
          '## Lever\n- "Han räknade stolarna två gånger innan han satte sig."\n')
    skriv(bok, "manuskript/kapitel-03.md", "Han räknade stolarna en gång och satte sig.\n")
    assert main(["validate", "manuskript/kapitel-03.md"]) == 1
    assert "BLOCKERANDE" in capsys.readouterr().out
    skriv(bok, "manuskript/kapitel-03.md", "Han räknade stolarna två gånger innan han satte sig.\n")
    assert main(["validate", "manuskript/kapitel-03.md"]) == 0


def test_tom_eller_trasig_pekningsfil_kraschar_inte(bok, capsys):
    skriv(bok, "bok/stil/pekningar/kapitel-03.md", "bara text utan rubriker\n- \"inte under Lever\"\n")
    skriv(bok, "manuskript/kapitel-03.md", "Hon gick.\n")
    assert main(["validate", "manuskript/kapitel-03.md"]) == 0
    (bok / "bok/stil/pekningar/kapitel-03.md").write_bytes(b"## Lever\n- \"\xff\xfe\"\n")
    assert main(["validate", "manuskript/kapitel-03.md"]) == 0
    assert "kunde inte läsas" in capsys.readouterr().out


def test_pekningsfil_med_bom_och_rubrikvariant(bok):
    (bok / "bok/stil/pekningar").mkdir(parents=True)
    (bok / "bok/stil/pekningar/kapitel-03.md").write_text('﻿## Lever\n- "Han räknade stolarna."\n', encoding="utf-8")
    assert lasta_stallen(bok, 3) == ["Han räknade stolarna."]
    skriv(bok, "bok/stil/pekningar/kapitel-04.md", '## Lever (låst)\n- "Hon log."\n')
    assert lasta_stallen(bok, 4) == ["Hon log."]


def test_citat_i_granskarnas_format(bok):
    skriv(bok, "bok/stil/pekningar/kapitel-03.md",
          '## Lever\n- "Han räknade stolarna två gånger.": rytmen bär\n- "Hon log".\n'
          '- "Han sa "nej" och gick."\n')
    assert lasta_stallen(bok, 3) == ["Han räknade stolarna två gånger.", "Hon log", 'Han sa "nej" och gick.']
