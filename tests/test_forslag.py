import http.server
import io
import json
import os
import stat
import threading
import time

import pytest

from bok import __version__, forslag
from bok.cli import main
from helpers import skriv

UTKAST = ("---\ntyp: problem\nroll: sprakgranskare\nsammanhang: I granskningen av ett kapitel.\n---\n"
          "Det var krångligt att förstå betygen 😅\nAndra raden.\n")


class Mottagare:
    def __init__(self):
        self.mottagna = []
        self.huvuden = []
        self.status_post = 201
        self.lista = []
        self.sov = 0.0


@pytest.fixture
def mottagare(monkeypatch):
    m = Mottagare()

    class Hanterare(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _svara(self, kod, data):
            kropp = json.dumps(data).encode("utf-8")
            self.send_response(kod)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(kropp)))
            self.end_headers()
            self.wfile.write(kropp)

        def do_POST(self):
            data = json.loads(self.rfile.read(int(self.headers["Content-Length"])).decode("utf-8"))
            m.huvuden.append(dict(self.headers))
            m.mottagna.append(data)
            if m.status_post != 201:
                self._svara(m.status_post, {"fel": "Mottagaren sa nej."})
                return
            self._svara(201, {"id": f"id-{len(m.mottagna)}", "issue": 100 + len(m.mottagna)})

        def do_GET(self):
            time.sleep(m.sov)
            m.huvuden.append(dict(self.headers))
            self._svara(200, m.lista)

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Hanterare)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setenv("BOK_FORSLAG_URL", f"http://127.0.0.1:{server.server_address[1]}")
    yield m
    server.shutdown()
    server.server_close()


def skicka(monkeypatch, text=UTKAST):
    monkeypatch.setattr("sys.stdin", io.StringIO(text))
    return main(["forslag", "skicka", "-"])


def test_skickar_utkast_med_version_och_lage(bok, mottagare, monkeypatch, capsys):
    assert skicka(monkeypatch) == 0
    data = mottagare.mottagna[0]
    assert set(data) == {"typ", "text", "sammanhang", "version", "lage", "roll"}
    assert data["typ"] == "problem" and data["roll"] == "sprakgranskare"
    assert data["text"] == "Det var krångligt att förstå betygen 😅\nAndra raden."
    assert data["version"] == __version__
    assert data["lage"] == "förberedelse"
    assert "Tack!" in capsys.readouterr().out
    rad = forslag.las_lokala()[0]
    assert rad["skickat"] is True and rad["issue"] == 101


def test_nyckeln_skapas_en_gang_och_ar_privat(bok, mottagare, monkeypatch):
    skicka(monkeypatch)
    skicka(monkeypatch)
    a, b = (h["Authorization"] for h in mottagare.huvuden)
    assert a == b and a.startswith("Bearer ") and len(a) >= 7 + 32
    path = forslag.katalog() / "nyckel"
    assert stat.S_IMODE(os.stat(path).st_mode) == 0o600


def test_laget_innehaller_inga_filnamn(bok, mottagare, monkeypatch):
    skriv(bok, "bok/karaktarer/anna.md", "---\nid: anna\nnamn: {{Namn}}\npov: true\n---\n")
    skicka(monkeypatch)
    assert mottagare.mottagna[0]["lage"] == "förberedelse"


def test_utanfor_en_bok(tmp_path, mottagare, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert skicka(monkeypatch) == 0
    assert mottagare.mottagna[0]["lage"] == ""


@pytest.mark.parametrize("text, fel", [
    ("---\ntyp: klagomal\n---\nHej\n", "typ måste vara"),
    ("---\ntyp: problem\n---\n\n", "saknar text"),
    ("---\ntyp: problem\n---\n" + "a" * 4001 + "\n", "högst 4000"),
    ("---\ntyp: problem\nroll: " + "r" * 41 + "\n---\nHej\n", "roll får vara högst 40 tecken."),
])
def test_ogiltiga_utkast_stoppas_lokalt(bok, mottagare, monkeypatch, capsys, text, fel):
    assert skicka(monkeypatch, text) == 2
    assert fel in capsys.readouterr().err
    assert mottagare.mottagna == []


def test_nere_mottagare_sparar_och_igen_skickar(bok, monkeypatch, capsys):
    assert skicka(monkeypatch) == 1
    assert "sparat" in capsys.readouterr().out
    assert forslag.las_lokala()[0]["skickat"] is False


def test_igen_skickar_det_som_inte_kom_fram(bok, monkeypatch, capsys, request):
    skicka(monkeypatch)
    m = request.getfixturevalue("mottagare")
    assert main(["forslag", "skicka", "--igen"]) == 0
    assert "Skickade 1 förslag." in capsys.readouterr().out
    assert len(m.mottagna) == 1 and forslag.las_lokala()[0]["skickat"] is True


def test_avvisat_forslag_skickas_inte_igen(bok, mottagare, monkeypatch):
    mottagare.status_post = 400
    assert skicka(monkeypatch) == 1
    assert forslag.las_lokala()[0]["avvisat"] == "Mottagaren sa nej."
    main(["forslag", "skicka", "--igen"])
    assert len(mottagare.mottagna) == 1


def test_avstangt_skickar_inget(bok, mottagare, monkeypatch, capsys):
    assert main(["forslag", "av"]) == 0
    assert skicka(monkeypatch) == 2
    assert "avstängda" in capsys.readouterr().err
    assert mottagare.mottagna == []
    main(["forslag", "pa"])
    assert skicka(monkeypatch) == 0


def test_lista_visar_status_och_svar(bok, mottagare, monkeypatch, capsys):
    skicka(monkeypatch)
    mottagare.lista = [{"id": "id-1", "issue": 101, "rubrik": "x", "skapad": "2026-10-03T10:00:00Z",
                        "status": "infort", "version": "2.1.0", "svar": "Tack, nu är det enklare."}]
    capsys.readouterr()
    assert main(["forslag"]) == 0
    ut = capsys.readouterr().out
    assert "infört i 2.1.0" in ut and "Svar: Tack, nu är det enklare." in ut
    assert "Det var krångligt" in ut


def test_lista_utan_forslag(bok, capsys):
    assert main(["forslag"]) == 0
    assert "inte skickat några förslag" in capsys.readouterr().out


@pytest.mark.parametrize("fil, innehall, fel", [
    ("nyckel", "kort\n", "nyckel"),
    ("forslag.jsonl", "{inte json\n", "forslag.jsonl rad 1"),
    ("installningar.json", "[]", "installningar.json"),
])
def test_trasiga_lokala_filer(bok, mottagare, monkeypatch, capsys, fil, innehall, fel):
    path = forslag.katalog() / fil
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(innehall, encoding="utf-8")
    assert skicka(monkeypatch) == 2
    assert fel in capsys.readouterr().err
    assert path.read_text(encoding="utf-8") == innehall
