import pytest

from bok.init import init_repo


@pytest.fixture(autouse=True)
def _isolera_forslag(tmp_path, monkeypatch):
    # Inga tester får läsa ~/.config/bok eller nå en riktig mottagare.
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("BOK_FORSLAG_URL", "http://127.0.0.1:9")


@pytest.fixture(autouse=True)
def _ingen_google(tmp_path, monkeypatch):
    # Inga tester får nå Google, använda en riktig nyckel eller lägga bilder i den riktiga temp-katalogen.
    import tempfile

    monkeypatch.delenv("BOK_GOOGLE_MAPS_NYCKEL", raising=False)
    monkeypatch.delenv("BOK_GOOGLE_MAPS_SIGNERING", raising=False)
    tmp = tmp_path / "tmp"
    tmp.mkdir()
    monkeypatch.setattr(tempfile, "tempdir", str(tmp))
    from bok import google

    def stopp(*args, **kwargs):
        raise AssertionError("ett test försökte nå Google på riktigt")

    monkeypatch.setattr(google._OPPNARE, "open", stopp)


@pytest.fixture
def bok(tmp_path, monkeypatch):
    root = tmp_path / "min-bok"
    init_repo(root, titel="Testbok", git=False)
    monkeypatch.chdir(root)
    return root.resolve()
