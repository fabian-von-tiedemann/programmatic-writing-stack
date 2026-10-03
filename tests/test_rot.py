import pytest

from bok.rot import BokSaknas, find_root


def test_find_root_gar_uppat(tmp_path):
    (tmp_path / "bok.toml").write_text("[bok]\n")
    djup = tmp_path / "manuskript" / "x"
    djup.mkdir(parents=True)
    assert find_root(djup) == tmp_path.resolve()


def test_find_root_utan_bok(tmp_path):
    with pytest.raises(BokSaknas, match="bok init"):
        find_root(tmp_path)
