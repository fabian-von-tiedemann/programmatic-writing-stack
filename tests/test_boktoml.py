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
