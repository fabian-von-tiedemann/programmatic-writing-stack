import pytest

from bok.platser import Plats, PlatsFel, avsnitt, fotoar, glapp, platsfil, tolka, underlag
from bok.tid import Datum
from helpers import skriv

LOK = [
    {"id": "fabriken", "namn": "Fabriken", "adress": "Storgatan 1, Exempelstad"},
    {"id": "torget", "namn": "Torget", "lat": 59.3, "lng": 18.07, "adress": "Torget, Exempelstad"},
    {"id": "skogen", "namn": "Skogen"},
    {"id": "trasig", "namn": "Trasig", "lat": "59", "lng": True},
]

TEXT = ("# Hornsgatan\n\n## Bokens tid\nKullersten och spårvagn.\n\n## Idag\nKälla: Google Street View\n"
        "Fotograferat: 2019-06 – 2023-08\nHämtat: 2026-10-04\nAsfalt och cykelbana.\n\n## Rutter\n- x\n")


def test_id_med_adress():
    p = tolka("fabriken", LOK)
    assert p == Plats("Fabriken", adress="Storgatan 1, Exempelstad")
    assert p.routes() == {"address": "Storgatan 1, Exempelstad"}
    assert p.streetview() == "Storgatan 1, Exempelstad"


def test_id_med_koordinater_gar_fore_adress():
    p = tolka("torget", LOK)
    assert p.routes() == {"location": {"latLng": {"latitude": 59.3, "longitude": 18.07}}}
    assert p.streetview() == "59.3,18.07"


@pytest.mark.parametrize("pid", ["skogen", "trasig"])
def test_id_utan_adress(pid):
    with pytest.raises(PlatsFel, match=f"{pid} har ingen adress"):
        tolka(pid, LOK)


def test_okant_id_och_ortnamn():
    with pytest.raises(PlatsFel, match="finns inte i locations.json"):
        tolka("slussen", LOK)
    assert tolka("Slussen", LOK).routes() == {"address": "Slussen"}
    assert tolka("Slussen, Stockholm", []).streetview() == "Slussen, Stockholm"
    assert tolka("Hornsgatan 12", LOK).namn == "Hornsgatan 12"


def test_koordinater_som_text():
    assert tolka(" 59.3, 18.07 ", []).streetview() == "59.3,18.07"
    with pytest.raises(PlatsFel, match="utanför"):
        tolka("99.0,18", [])


def test_avsnitt():
    assert avsnitt(TEXT, "Bokens tid") == "Kullersten och spårvagn."
    assert avsnitt(TEXT, "Idag").endswith("Asfalt och cykelbana.")
    assert avsnitt(TEXT, "Saknas") == ""


@pytest.mark.parametrize("text,ar", [
    ("Fotograferat: 2019-06 – 2023-08", (2019, 2023)),
    ("Fotograferat: 2019-2023", (2019, 2023)),
    ("Fotograferat: 2023 - 2019", (2019, 2023)),
    ("Fotograferat: 2021", (2021, 2021)),
    ("Fotograferat: 2021-05.", (2021, 2021)),
    ("Fotograferat: okänt", None),
    ("Ingen rad", None),
])
def test_fotoar(text, ar):
    assert fotoar(text) == ar


def test_glapp():
    assert glapp((2019, 2023), Datum(1978)) == (
        "Underlaget Idag är fotograferat 2019–2023; kapitlet utspelar sig 1978 (41–45 år tidigare). "
        "Bokens tid går före; ur Idag används bara det som gällde då.")
    assert glapp((2023, 2023), Datum(2024)) == "Underlaget Idag är fotograferat 2023; kapitlet utspelar sig 2024."
    assert glapp((2020, 2020), Datum(2040, 5)) == (
        "Underlaget Idag är fotograferat 2020; kapitlet utspelar sig 2040 (20 år senare). "
        "Bokens tid går före; ur Idag används bara det som gällde då.")


def test_underlag():
    rader = underlag(TEXT, Datum(1978))
    assert rader[:3] == ["#### Bokens tid", "Kullersten och spårvagn.", "#### Idag"]
    assert rader[3].startswith("Källa: Google Street View") and rader[3].endswith("cykelbana.")
    assert rader[4].startswith("Underlaget Idag är fotograferat 2019–2023")
    assert len(underlag(TEXT, None)) == 4
    assert underlag(None, Datum(1978)) == []
    assert underlag("# Tom\n\n## Bokens tid\n\n## Idag\n", Datum(1978)) == []


def test_platsfil(bok):
    assert platsfil(bok, "hornsgatan") is None
    skriv(bok, "bok/varld/platser/hornsgatan.md", TEXT)
    assert platsfil(bok, "hornsgatan") == TEXT
    assert platsfil(bok, "../koncept/premiss") is None
