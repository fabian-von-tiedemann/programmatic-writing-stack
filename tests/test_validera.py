from bok.cli import main
from bok.graf import Graf
from bok.validera import blacklist_traffar, block, kanda_namn, okanda
from helpers import skriv, skriv_graf

CANON = "# Canon\n\n```blacklist\nOlof Palme\n```\n\n```kanda-namn\nStockholm\n```\n"


def test_block():
    assert block(CANON, "blacklist") == ["Olof Palme"]
    assert block(CANON, "kanda-namn") == ["Stockholm"]


def test_blacklist():
    text = "Hon tänkte på Olof Palme.\nInget här.\n"
    assert blacklist_traffar(text, ["Olof Palme"]) == [(1, "Olof Palme")]


def test_kanda_namn_tar_med_fornamn_och_alias(bok):
    skriv_graf(bok)
    kanda = kanda_namn(Graf.load(bok), CANON)
    assert {"Anna Berg", "Anna", "Annie", "Gården", "Stockholm"} <= kanda


def test_okanda_hoppar_over_meningsstart_och_kanda():
    text = "Hon mötte Märta i hallen. Sedan kom Anna.\n– Hej, sa Gustav.\n# Rubrik Med Versal\n"
    ut = okanda(text, {"Anna"})
    assert ut == [(1, "Märta"), (2, "Gustav")]


def test_okanda_med_straight_quotes():
    # Straight double quotes should also work as sentence starters
    text = '"Nej", sa Märta till Gustav.\n'
    ut = okanda(text, {"Märta"})
    assert ut == [(1, "Gustav")]


def test_okanda_sentence_start_after_straight_quote_and_period():
    # After straight quote and period, the word is at sentence start
    text = '"Nej." Märta log.\n'
    ut = okanda(text, set())
    assert ut == []


def test_okanda_med_curly_quotes():
    # Swedish dialogue with curly quotes
    text = '“Nej”, sa Märta till Gustav.\n'
    ut = okanda(text, {"Märta"})
    assert ut == [(1, "Gustav")]


def test_okanda_sentence_start_after_curly_quote_and_period():
    # After curly quote and period, the word is at sentence start
    text = '“Nej.” Märta log.\n'
    ut = okanda(text, set())
    assert ut == []


def test_cli_blacklist_ger_exitkod_1(bok, capsys):
    skriv(bok, "bok/canon.md", CANON)
    skriv(bok, "manuskript/kapitel-01.md", "Hon läste om Olof Palme.\n")
    assert main(["validate"]) == 1
    assert "BLOCKERANDE rad 1: Olof Palme" in capsys.readouterr().out


def test_cli_okanda_namn_ar_bara_information(bok, capsys):
    skriv_graf(bok)
    skriv(bok, "manuskript/kapitel-01.md", "Hon mötte Märta och Erik.\n")
    assert main(["validate"]) == 0
    out = capsys.readouterr().out
    assert "Märta (rad 1)" in out and "Erik (" not in out


def test_cli_missing_file_returns_2(bok):
    assert main(["validate", "manuskript/finns-inte.md"]) == 2
