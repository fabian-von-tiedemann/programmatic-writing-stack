import os
import stat

from bok import privat


def test_katalog_foljer_xdg(tmp_path):
    assert privat.katalog() == tmp_path / "config" / "bok"


def test_skriv_privat(tmp_path):
    path = privat.katalog() / "hemlis"
    privat.skriv_privat(path, "abc\n")
    assert path.read_text(encoding="utf-8") == "abc\n"
    assert stat.S_IMODE(os.stat(path).st_mode) == 0o600
    assert stat.S_IMODE(os.stat(path.parent).st_mode) == 0o700
    privat.skriv_privat(path, "def\n")
    assert path.read_text(encoding="utf-8") == "def\n"
    assert [p.name for p in path.parent.iterdir()] == ["hemlis"]
