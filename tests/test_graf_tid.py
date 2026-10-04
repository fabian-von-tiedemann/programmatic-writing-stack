import copy

import pytest

from bok.cli import main
from bok.graf import Graf, scenkort_om_finns
from bok.tid import Datum, tolka
from helpers import TIDGRAF, skriv, skriv_tidgraf


@pytest.fixture
def graf(bok):
    skriv_tidgraf(bok)
    return Graf.load(bok)


def test_kapitel_datum(graf):
    assert graf.kapitel_datum(2) == Datum(1994, 9, 28)
    assert graf.kapitel_datum(2, "1995") == Datum(1995)
    assert graf.kapitel_datum(2, 1995) == Datum(1995)
    assert graf.kapitel_datum(3) is None  # "våren 1995" går inte att tolka
    assert graf.kapitel_datum(9) is None


def test_alder_vid(graf):
    vid = Datum(1994, 9, 28)
    assert graf.alder_vid("marlene", vid) == "48 år (född 1946-03-14)"
    assert graf.alder_vid("sofia", vid) == "19–20 år (född 1974)"
    assert graf.alder_vid("henrik", vid) == "död 1990-05-01 (född 1950)"
    assert graf.alder_vid("utan", vid) is None
    assert graf.alder_vid("okand", vid) is None
    assert graf.alder_vid("marlene", Datum(1940)) == "inte född än (född 1946-03-14)"


def test_context_med_datum_och_rost(graf):
    out = graf.context(2, ["marlene", "sofia", "utan"], [], [], datum=Datum(1994, 9, 28),
                       rostfil="bok/stil/rost-marlene.md")
    assert "Kapitlet utspelar sig: 1994-09-28" in out
    assert "- Ålder: 48 år (född 1946-03-14)" in out
    assert "- Ålder: 19–20 år (född 1974)" in out
    utan = out.split("### Utan Datum")[1].split("###")[0]
    assert "Ålder" not in utan
    assert "## Röst" in out and "bok/stil/rost-marlene.md" in out


def test_context_utan_datum(graf):
    out = graf.context(2, ["marlene"], [], [])
    assert "Kapitlet utspelar sig" not in out and "Ålder" not in out and "## Röst" not in out


def test_tidslinje(graf):
    out = graf.tidslinje()
    rader = [r for r in out.splitlines() if r.startswith("- ")]
    assert rader == [
        "- 1989-11-09 · kapitel 1 · Anbudsöppningen · Kontoret · Marléne Östlund 43 år, Henrik Ek 38–39 år",
        "- 1994-09-28 · kapitel 2 · Estonia · Marléne Östlund 48 år, Sofia Östlund 19–20 år",
    ]
    assert "Anbudsöppningen" not in graf.tidslinje(fran=1990)
    assert "Estonia" not in graf.tidslinje(till=1990)


def test_tidslinje_tom(bok):
    assert "Inga daterade händelser" in Graf.load(bok).tidslinje()


def test_tidsfel_personer(bok):
    g = copy.deepcopy(TIDGRAF)
    g["events"].append({"id": "e5", "kapitel": 2, "vad": "Mötet", "datum": "1994-01-01", "narvarande": ["henrik"]})
    g["events"].append({"id": "e6", "kapitel": 1, "vad": "Dopet", "datum": "1970", "narvarande": ["sofia"]})
    skriv_tidgraf(bok, g)
    fel = Graf.load(bok).tidsfel([])
    assert 'Henrik Ek är med i "Mötet" (1994-01-01, kapitel 2) men dog 1990-05-01.' in fel
    assert 'Sofia Östlund är med i "Dopet" (1970, kapitel 1) men föds 1974.' in fel
    assert len(fel) == 2


def test_tidsfel_kapitelordning(graf):
    d89, d94 = Datum(1989, 11, 9), Datum(1994, 9, 28)
    fel = graf.tidsfel([(1, d94, False), (2, d89, False)])
    assert fel == ["Kapitel 2 (1989-11-09) ligger före kapitel 1 (1994-09-28). "
                   "Är det en tillbakablick? Skriv tillbakablick: true i scenkortet "
                   "– eller skriv kapitlets datum i scenkortet."]
    assert graf.tidsfel([(1, d94, False), (2, d89, True), (3, d94, False)]) == []
    assert graf.tidsfel([(1, d94, False), (2, None, False), (3, d94, False)]) == []


def test_scenkort_om_finns(bok):
    assert scenkort_om_finns(bok, 4) == {}
    skriv(bok, "bok/plot/kapitel/kapitel-04.md", (bok / "bok/plot/kapitel/MALL.md").read_text())
    assert scenkort_om_finns(bok, 4) == {}
    skriv(bok, "bok/plot/kapitel/kapitel-04.md", "---\nkapitel: 4\ndatum: 1994-09-28\n---\n")
    assert tolka(scenkort_om_finns(bok, 4)["datum"]) == Datum(1994, 9, 28)


def test_cli_tidslinje(bok, capsys):
    skriv_tidgraf(bok)
    assert main(["graph", "tidslinje", "--fran", "1990"]) == 0
    out = capsys.readouterr().out
    assert "Estonia" in out and "Anbudsöppningen" not in out


def test_cli_context_med_datum_och_rostfil(bok, capsys):
    skriv_tidgraf(bok)
    skriv(bok, "bok/plot/kapitel/kapitel-02.md",
          "---\nkapitel: 2\npov: marlene\nkaraktarer: [marlene]\nplatser: []\nbagar: []\n"
          "datum: 1994-09-28\ngodkand: true\n---\n")
    skriv(bok, "bok/stil/rost-marlene.md", "# Marlénes röst\n")
    assert main(["graph", "context", "--kapitel", "2"]) == 0
    out = capsys.readouterr().out
    assert "Kapitlet utspelar sig: 1994-09-28" in out
    assert "- Ålder: 48 år (född 1946-03-14)" in out
    assert "bok/stil/rost-marlene.md" in out


def test_trasiga_listvarden_kraschar_inte(bok, capsys):
    g = copy.deepcopy(TIDGRAF)
    g["events"].append({"id": "e9", "kapitel": 2, "vad": 42, "datum": "1994-10-01", "plats": "kontoret",
                        "narvarande": 5})
    g["events"].append({"id": "e10", "kapitel": 2, "vad": ["a"], "datum": "1994-10-02",
                        "narvarande": ["marlene", 7, None]})
    g["secrets"].append({"id": "s1", "vad": "Hemlig", "vet": 5})
    skriv_tidgraf(bok, g)
    graf = Graf.load(bok)
    assert "42" in graf.tidslinje()
    assert graf.tidsfel([(1, Datum(1989), False), (2, Datum(1994), False)]) == []
    assert "Underlag för kapitel 3" in graf.context(3, ["marlene"], [], [])
    assert "Marléne" in graf.karaktar("marlene")
    assert "Kontoret" in graf.var("kontoret")
    assert "Hemlig" in graf.vem_vet("s1")
    skriv(bok, "manuskript/kapitel-01.md", "Text.\n")
    assert main(["validate"]) == 0


PLATSFIL = ("# Kontoret\n\n## Bokens tid\nLysrör och linoleum.\n\n## Idag\nKälla: Google Street View\n"
            "Fotograferat: 2019-06 – 2023-08\nHämtat: 2026-10-04\nGlas och betong.\n\n## Rutter\n")


def test_context_med_platsfil(graf):
    text = graf.context(1, [], ["kontoret"], [], datum=Datum(1989, 11, 9), platsfiler={"kontoret": PLATSFIL})
    avsnitt = text.split("## Platser", 1)[1].split("## Bågar", 1)[0]
    assert avsnitt.index("#### Bokens tid") < avsnitt.index("Lysrör") < avsnitt.index("#### Idag") < avsnitt.index("Glas")
    assert "fotograferat 2019–2023; kapitlet utspelar sig 1989 (30–34 år tidigare)" in avsnitt


def test_context_platsfil_utan_datum_och_ny_plats(graf):
    text = graf.context(1, [], ["kontoret", "torget"], [], platsfiler={"torget": PLATSFIL})
    assert "Underlaget Idag" not in text
    assert "Ny i kapitlet (finns inte i grafen än).\n#### Bokens tid" in text


def test_cli_context_laser_platsfiler(bok, capsys):
    skriv_tidgraf(bok)
    skriv(bok, "bok/varld/platser/kontoret.md", PLATSFIL)
    skriv(bok, "bok/varld/platser/annan.md", PLATSFIL.replace("Lysrör", "Annat"))
    skriv(bok, "bok/plot/kapitel/kapitel-01.md",
          "---\nkapitel: 1\npov: marlene\nkaraktarer: [marlene]\nplatser: [kontoret]\nbagar: []\n---\n\n# Kapitel 1\n")
    assert main(["graph", "context", "--kapitel", "1"]) == 0
    ut = capsys.readouterr().out
    assert "Lysrör" in ut and "Annat" not in ut and "(30–34 år tidigare)" in ut
