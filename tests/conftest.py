import pytest

from bok.init import init_repo


@pytest.fixture(autouse=True)
def _isolera_forslag(tmp_path, monkeypatch):
    # Inga tester får läsa ~/.config/bok eller nå en riktig mottagare.
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("BOK_FORSLAG_URL", "http://127.0.0.1:9")


@pytest.fixture
def bok(tmp_path, monkeypatch):
    root = tmp_path / "min-bok"
    init_repo(root, titel="Testbok", git=False)
    monkeypatch.chdir(root)
    return root.resolve()
