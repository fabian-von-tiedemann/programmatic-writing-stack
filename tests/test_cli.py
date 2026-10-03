import pytest

from bok import status
from bok.cli import main


def test_version(capsys):
    with pytest.raises(SystemExit):
        main(["--version"])
    assert "bok 2.0.0" in capsys.readouterr().out


def test_utan_kommando_visar_hjalp(capsys):
    assert main([]) == 0
    assert "bok" in capsys.readouterr().out


def test_filfel_blir_en_rad(bok, monkeypatch, capsys):
    def trasig(root):
        raise PermissionError(13, "Permission denied", "bok/plot/kapitelplan.md")

    monkeypatch.setattr(status, "compute", trasig)
    assert main(["status"]) == 2
    err = capsys.readouterr().err
    assert err == "bok: kunde inte läsa eller skriva bok/plot/kapitelplan.md: Permission denied\n"


def test_fil_som_inte_ar_utf8_blir_en_rad(bok, monkeypatch, capsys):
    def trasig(root):
        b"\xff".decode("utf-8")

    monkeypatch.setattr(status, "compute", trasig)
    assert main(["status"]) == 2
    err = capsys.readouterr().err
    assert err.startswith("bok: en fil är inte sparad som UTF-8") and err.count("\n") == 1


def test_avbrutet_ror_ar_tyst(bok, monkeypatch, capsys):
    def ror(root):
        raise BrokenPipeError(32, "Broken pipe")

    monkeypatch.setattr(status, "compute", ror)
    assert main(["status"]) == 1
    assert capsys.readouterr().err == ""
