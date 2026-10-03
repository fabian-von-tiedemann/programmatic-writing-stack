import pytest

from bok.boktoml import BokTomlFel, add_modul, read, render_new, set_ramverk


def test_render_och_read(tmp_path):
    (tmp_path / "bok.toml").write_text(render_new('Hösten på "Ön"', "2.0.0"), encoding="utf-8")
    bok = read(tmp_path)
    assert bok["titel"] == 'Hösten på "Ön"'
    assert bok["ramverk"] == "2.0.0"
    assert bok["moduler"] == []


def test_ogiltig_toml(tmp_path):
    (tmp_path / "bok.toml").write_text("[bok\n")
    with pytest.raises(BokTomlFel, match="inte giltig TOML"):
        read(tmp_path)


def test_saknar_tabell(tmp_path):
    (tmp_path / "bok.toml").write_text('titel = "x"\n')
    with pytest.raises(BokTomlFel, match="saknar tabellen"):
        read(tmp_path)


def test_set_ramverk(tmp_path):
    (tmp_path / "bok.toml").write_text(render_new("X", "1.0.0"))
    assert set_ramverk(tmp_path, "2.0.0") is True
    assert read(tmp_path)["ramverk"] == "2.0.0"
    assert set_ramverk(tmp_path, "2.0.0") is False


def test_add_modul(tmp_path):
    (tmp_path / "bok.toml").write_text(render_new("X", "2.0.0"))
    add_modul(tmp_path, "spanning")
    add_modul(tmp_path, "spanning")
    add_modul(tmp_path, "serie")
    assert read(tmp_path)["moduler"] == ["spanning", "serie"]


def test_set_ramverk_single_quotes(tmp_path):
    """Single-quoted ramverk should be updated without creating duplicates."""
    (tmp_path / "bok.toml").write_text(
        "[bok]\ntitel = \"X\"\ngenre = \"\"\nramverk = '1.0.0'\nmoduler = []\n"
    )
    assert set_ramverk(tmp_path, "2.0.0") is True
    # Verify no duplicate keys and correct value
    bok = read(tmp_path)
    assert bok["ramverk"] == "2.0.0"


def test_set_ramverk_with_comment(tmp_path):
    """[bok] header with trailing comment should be recognized."""
    (tmp_path / "bok.toml").write_text(
        "[bok]  # Book configuration\ntitel = \"X\"\ngenre = \"\"\nramverk = \"1.0.0\"\nmoduler = []\n"
    )
    assert set_ramverk(tmp_path, "2.0.0") is True
    assert read(tmp_path)["ramverk"] == "2.0.0"


def test_add_modul_with_comment_header(tmp_path):
    """add_modul should insert moduler key even with [bok] header comment."""
    (tmp_path / "bok.toml").write_text(
        "[bok]  # Book configuration\ntitel = \"X\"\ngenre = \"\"\nramverk = \"1.0.0\"\n"
    )
    add_modul(tmp_path, "spanning")
    assert read(tmp_path)["moduler"] == ["spanning"]


def test_add_modul_malformed_existing_raises(tmp_path):
    """add_modul should raise BokTomlFel if moduler is malformed (string instead of list)."""
    (tmp_path / "bok.toml").write_text(
        "[bok]\ntitel = \"X\"\ngenre = \"\"\nramverk = \"1.0.0\"\nmoduler = \"spanning\"\n"
    )
    with pytest.raises(BokTomlFel, match="Kunde inte uppdatera"):
        add_modul(tmp_path, "serie")
    # File should be unchanged
    text = (tmp_path / "bok.toml").read_text(encoding="utf-8")
    assert 'moduler = "spanning"' in text


def test_titel_genre_preserved(tmp_path):
    """Other keys should be preserved when updating ramverk."""
    (tmp_path / "bok.toml").write_text(
        '[bok]\ntitel = "Mitt verk"\ngenre = "roman"\nramverk = "1.0.0"\nmoduler = []\n'
    )
    set_ramverk(tmp_path, "2.0.0")
    bok = read(tmp_path)
    assert bok["titel"] == "Mitt verk"
    assert bok["genre"] == "roman"
    assert bok["ramverk"] == "2.0.0"
