import pytest

from bok.frontmatter import FrontmatterFel, split


def test_utan_frontmatter():
    assert split("# Hej\n") == ({}, "# Hej\n")


def test_skalarer():
    meta, body = split("---\nkapitel: 3\nroll: redaktor\npov: true\nx: 7.5\n---\nText\n")
    assert meta == {"kapitel": 3, "roll": "redaktor", "pov": True, "x": 7.5}
    assert body == "Text\n"


def test_lista_och_dict():
    meta, _ = split(
        '---\nkaraktarer: [anna, erik]\nbetyg: {struktur: 8, tema: 7}\n'
        "blockerande: [\"Kap 3: tisdag\", 'a, b']\n---\n"
    )
    assert meta["karaktarer"] == ["anna", "erik"]
    assert meta["betyg"] == {"struktur": 8, "tema": 7}
    assert meta["blockerande"] == ["Kap 3: tisdag", "a, b"]


def test_tom_lista_och_tomt_varde():
    assert split("---\nx: []\ny:\n---\n")[0] == {"x": [], "y": None}


def test_platshallare_lamnas_som_text():
    meta, _ = split("---\npov: {{true eller false}}\nkaraktarer: [{{id}}, {{id}}]\n---\n")
    assert meta["pov"] == "{{true eller false}}"
    assert meta["karaktarer"] == ["{{id}}", "{{id}}"]


def test_saknar_avslutning():
    with pytest.raises(FrontmatterFel, match="avslutande"):
        split("---\nx: 1\n")


def test_trasig_rad():
    with pytest.raises(FrontmatterFel, match="Rad 1"):
        split("---\nbara text\n---\n")


def test_bom_crlf_och_tomrader_fore():
    meta, body = split("﻿\n\n---\r\nx: 1\r\n---\r\nText\r\n")
    assert meta == {"x": 1}
    assert body == "Text\n"


def test_frontmatter_utan_body():
    assert split("---\nx: 1\n---") == ({"x": 1}, "")


def test_nan_inf_underscores_stay_text():
    """Special values nan, inf and numbers with underscores should stay as text."""
    meta, _ = split("---\nid: nan\nvalue: inf\nnegative: -inf\nlarge: 1_000\n---\n")
    assert meta["id"] == "nan"
    assert meta["value"] == "inf"
    assert meta["negative"] == "-inf"
    assert meta["large"] == "1_000"
