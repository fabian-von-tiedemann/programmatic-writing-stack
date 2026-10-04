import http.server
import os
import stat
import tempfile
import threading
import time
from pathlib import Path

import pytest

from bok import bild
from bok.cli import main

JPEG = b"\xff\xd8\xff\xe0" + b"0" * 100


@pytest.fixture
def server():
    class Hanterare(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            if self.path == "/bild.jpg":
                self._svara(200, "image/jpeg", JPEG)
            elif self.path == "/sida":
                self._svara(200, "text/html; charset=utf-8", b"<html></html>")
            elif self.path == "/till-fil":
                self._flytta("file:///etc/passwd")
            elif self.path == "/till-bild":
                self._flytta("/bild.jpg")
            else:
                self._svara(404, "text/plain", b"")

        def _svara(self, kod, typ, kropp):
            self.send_response(kod)
            self.send_header("Content-Type", typ)
            self.send_header("Content-Length", str(len(kropp)))
            self.end_headers()
            self.wfile.write(kropp)

        def _flytta(self, dit):
            self.send_response(302)
            self.send_header("Location", dit)
            self.send_header("Content-Length", "0")
            self.end_headers()

    s = http.server.HTTPServer(("127.0.0.1", 0), Hanterare)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{s.server_port}"
    s.shutdown()


def test_ny_mapp_ligger_i_temp_och_ar_privat(bok):
    mapp = bild.ny_mapp("bok-gatuvy-")
    assert mapp.parent == Path(tempfile.gettempdir())
    assert mapp.name.startswith("bok-gatuvy-")
    assert stat.S_IMODE(os.stat(mapp).st_mode) == 0o700
    assert not mapp.resolve().is_relative_to(bok)


def test_rensa_gamla_och_stada():
    gammal = bild.ny_mapp("bok-bild-")
    ny = bild.ny_mapp("bok-gatuvy-")
    annan = Path(tempfile.gettempdir()) / "annat-program"
    annan.mkdir()
    for p in (gammal, annan):
        os.utime(p, (time.time() - 2 * 86400, time.time() - 2 * 86400))
    bild.rensa_gamla()
    assert not gammal.exists() and ny.exists() and annan.exists()
    assert bild.stada() == 1
    assert not ny.exists() and annan.exists()


def test_hamta_bild(server):
    path = bild.hamta(server + "/bild.jpg")
    assert path.read_bytes() == JPEG and path.suffix == ".jpg"
    assert path.parent.name.startswith("bok-bild-")


def test_hamta_via_omdirigering(server):
    assert bild.hamta(server + "/till-bild").read_bytes() == JPEG


@pytest.mark.parametrize("sokvag", ["/sida", "/till-fil", "/saknas"])
def test_hamta_avvisar(server, sokvag):
    with pytest.raises(bild.BildFel):
        bild.hamta(server + sokvag)
    assert not list(Path(tempfile.gettempdir()).glob("bok-bild-*"))


def test_hamta_for_stor(server, monkeypatch):
    monkeypatch.setattr(bild, "MAX_STORLEK", 10)
    with pytest.raises(bild.BildFel, match="15 MB"):
        bild.hamta(server + "/bild.jpg")


@pytest.mark.parametrize("url", ["ftp://example.com/a.jpg", "file:///etc/passwd", "bild.jpg"])
def test_fel_schema(url):
    with pytest.raises(bild.BildFel, match="http eller https"):
        bild.hamta(url)


def test_cli(server, capsys):
    assert main(["bild", server + "/bild.jpg"]) == 0
    ut = capsys.readouterr().out
    assert "bok-bild-" in ut and "bok karta stada" in ut
