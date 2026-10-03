import pytest

from bok.tid import Datum, alder, sakert_fore, som_text, tolka


@pytest.mark.parametrize("varde, vantat", [
    ("1946", Datum(1946)),
    ("1946-03", Datum(1946, 3)),
    ("1946-03-14", Datum(1946, 3, 14)),
    (" 1994-09-28 ", Datum(1994, 9, 28)),
    (1994, Datum(1994)),
])
def test_tolka(varde, vantat):
    assert tolka(varde) == vantat


@pytest.mark.parametrize("varde", ["våren 1995", "1994-13-01", "1994-09-32", "94", "", None, True, 12, [1994]])
def test_tolka_ogiltigt(varde):
    assert tolka(varde) is None


def test_str():
    assert str(Datum(1946)) == "1946"
    assert str(Datum(1946, 3)) == "1946-03"
    assert str(Datum(1946, 3, 14)) == "1946-03-14"


def test_alder_exakt():
    assert alder(Datum(1946, 3, 14), Datum(1994, 9, 28)) == (48, 48)
    assert alder(Datum(1946, 3, 14), Datum(1994, 3, 13)) == (47, 47)
    assert alder(Datum(1946, 3, 14), Datum(1994, 3, 14)) == (48, 48)


def test_alder_oprecis():
    assert alder(Datum(1946), Datum(1994, 9, 28)) == (47, 48)
    assert alder(Datum(1946, 3, 14), Datum(1994)) == (47, 48)


def test_sakert_fore():
    assert sakert_fore(Datum(1989), Datum(1990, 1, 1))
    assert not sakert_fore(Datum(1990), Datum(1990, 6, 1))
    assert not sakert_fore(Datum(1990, 6, 1), Datum(1990))


def test_som_text():
    assert som_text(48, 48) == "48 år"
    assert som_text(47, 48) == "47–48 år"
