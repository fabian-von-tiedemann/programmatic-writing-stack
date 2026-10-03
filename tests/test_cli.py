import pytest

from bok.cli import main


def test_version(capsys):
    with pytest.raises(SystemExit):
        main(["--version"])
    assert "bok 2.0.0" in capsys.readouterr().out


def test_utan_kommando_visar_hjalp(capsys):
    assert main([]) == 0
    assert "bok" in capsys.readouterr().out
