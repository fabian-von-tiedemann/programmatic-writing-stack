import pytest

from bok.init import init_repo


@pytest.fixture
def bok(tmp_path, monkeypatch):
    root = tmp_path / "min-bok"
    init_repo(root, titel="Testbok", git=False)
    monkeypatch.chdir(root)
    return root.resolve()
