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
from bok.init import init_repo
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
        self.ra = None  # råa byte som svar i stället för JSON
        self.omdirigera = False
        self.omdirigerade = []


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

        def _omdirigering(self):
            if self.path != "/v1/forslag":
                m.omdirigerade.append(dict(self.headers))
                self._svara(201 if self.command == "POST" else 200,
                            {"id": "x", "issue": 1} if self.command == "POST" else [])
                return True
            if m.omdirigera:
                m.huvuden.append(dict(self.headers))
                self.send_response(302)
                self.send_header("Location", "/annan")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return True
            return False

        def _svara_ra(self, kod):
            self.send_response(kod)
            self.send_header("Content-Length", str(len(m.ra)))
            self.end_headers()
            self.wfile.write(m.ra)

        def do_POST(self):
            data = json.loads(self.rfile.read(int(self.headers["Content-Length"])).decode("utf-8"))
            if self._omdirigering():
                return
            if m.ra is not None:
                m.huvuden.append(dict(self.headers))
                self._svara_ra(201)
                return
            m.huvuden.append(dict(self.headers))
            m.mottagna.append(data)
            if m.status_post != 201:
                self._svara(m.status_post, {"fel": "Mottagaren sa nej."})
                return
            self._svara(201, {"id": f"id-{len(m.mottagna)}", "issue": 100 + len(m.mottagna)})

        def do_GET(self):
            time.sleep(m.sov)
            if self._omdirigering():
                return
            m.huvuden.append(dict(self.headers))
            if m.ra is not None:
                self._svara_ra(200)
                return
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


@pytest.mark.parametrize("kod", [400, 401, 403, 413])
def test_avvisat_forslag_skickas_inte_igen(bok, mottagare, monkeypatch, capsys, kod):
    mottagare.status_post = kod
    assert skicka(monkeypatch) == 1
    ut = capsys.readouterr().out
    assert "Förslaget skickades inte: Mottagaren sa nej." in ut
    assert "--igen" not in ut and "sparat men inte skickat" not in ut
    assert forslag.las_lokala()[0]["avvisat"] == "Mottagaren sa nej."
    main(["forslag", "skicka", "--igen"])
    assert len(mottagare.mottagna) == 1


@pytest.mark.parametrize("kod", [429, 500, 502])
def test_tillfalligt_fel_kan_skickas_igen(bok, mottagare, monkeypatch, capsys, kod):
    mottagare.status_post = kod
    assert skicka(monkeypatch) == 1
    ut = capsys.readouterr().out
    assert "sparat men inte skickat" in ut and "--igen" in ut
    assert "avvisat" not in forslag.las_lokala()[0]
    mottagare.status_post = 201
    assert main(["forslag", "skicka", "--igen"]) == 0
    assert forslag.las_lokala()[0]["skickat"] is True


def test_trasigt_svar_ger_ingen_krasch(bok, mottagare, monkeypatch, capsys):
    import http.client
    def trasig(*a, **kw):
        raise http.client.IncompleteRead(b"")
    monkeypatch.setattr(forslag._OPPNARE, "open", trasig)
    assert skicka(monkeypatch) == 1
    assert "Kunde inte nå mottagaren just nu." in capsys.readouterr().out
    assert forslag.las_lokala()[0]["skickat"] is False


def test_svar_som_inte_ar_utf8(bok, mottagare, monkeypatch, capsys):
    mottagare.ra = b"\xff\xfe"
    assert skicka(monkeypatch) == 1
    assert "Kunde inte nå mottagaren just nu." in capsys.readouterr().out


@pytest.mark.parametrize("ra", [b"[]", b"null", b'"text"'])
def test_ovantat_svar_pa_post(bok, mottagare, monkeypatch, capsys, ra):
    mottagare.ra = ra
    assert skicka(monkeypatch) == 1
    assert "Mottagaren svarade oväntat." in capsys.readouterr().out
    assert forslag.las_lokala()[0]["skickat"] is False


def test_ovantat_svar_pa_get(bok, mottagare, monkeypatch, capsys):
    skicka(monkeypatch)
    mottagare.ra = b'{"id": "id-1"}'
    with pytest.raises(forslag.MottagarFel, match="oväntat"):
        forslag._anrop("GET", None, timeout=5)
    capsys.readouterr()
    assert main(["forslag"]) == 0
    assert "Kunde inte hämta status" in capsys.readouterr().out


@pytest.mark.parametrize("metod", ["POST", "GET"])
def test_nyckeln_foljer_inte_med_vid_omdirigering(bok, mottagare, monkeypatch, metod):
    mottagare.omdirigera = True
    data = {"typ": "problem", "text": "x", "sammanhang": "", "version": __version__, "lage": "", "roll": ""}
    with pytest.raises(forslag.MottagarFel):
        forslag._anrop(metod, data if metod == "POST" else None, timeout=5)
    assert len(mottagare.huvuden) == 1
    assert mottagare.omdirigerade == []


def test_omdirigering_skickar_inte_forslaget(bok, mottagare, monkeypatch):
    mottagare.omdirigera = True
    assert skicka(monkeypatch) == 1
    assert mottagare.omdirigerade == []
    assert forslag.las_lokala()[0]["skickat"] is False


def test_privata_filer_och_katalog(bok, mottagare, monkeypatch):
    skicka(monkeypatch)
    main(["forslag", "av"])
    kat = forslag.katalog()
    assert stat.S_IMODE(os.stat(kat).st_mode) == 0o700
    for namn in ("nyckel", "forslag.jsonl", "installningar.json"):
        assert stat.S_IMODE(os.stat(kat / namn).st_mode) == 0o600
    assert sorted(p.name for p in kat.iterdir()) == ["forslag.jsonl", "installningar.json", "nyckel"]


def test_avbruten_skrivning_lamnar_gamla_filen(bok, monkeypatch):
    path = forslag.katalog() / "installningar.json"
    forslag.spara_installningar({"forslag": "pa", "senast_sedda": {}})
    fore = path.read_text(encoding="utf-8")
    def fel(fd):
        raise OSError("disken är full")
    monkeypatch.setattr(forslag.os, "fsync", fel)
    with pytest.raises(OSError):
        forslag.spara_installningar({"forslag": "av", "senast_sedda": {}})
    assert path.read_text(encoding="utf-8") == fore
    assert [p.name for p in forslag.katalog().iterdir()] == ["installningar.json"]


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


@pytest.mark.parametrize("status", ["okand", "nagot-nytt"])
def test_lista_visar_okand_status_som_skickat(bok, mottagare, monkeypatch, capsys, status):
    skicka(monkeypatch)
    mottagare.lista = [{"id": "id-1", "issue": 101, "rubrik": "", "skapad": "2026-10-03T10:00:00Z",
                        "status": status, "version": None, "svar": None}]
    capsys.readouterr()
    assert main(["forslag"]) == 0
    assert "[skickat]" in capsys.readouterr().out


def test_avstangt_ror_inte_natet_i_lista_och_nyheter(bok, mottagare, monkeypatch, capsys):
    skicka(monkeypatch)
    mottagare.lista = [{"id": "id-1", "issue": 101, "status": "infort", "version": "2.1.0", "svar": None}]
    main(["forslag", "av"])
    mottagare.huvuden.clear()
    rader, ok = forslag.lista()
    assert rader and ok
    assert main(["forslag"]) == 0
    assert forslag.nyheter() == []
    assert mottagare.huvuden == []


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


def test_nyheter_en_gang(bok, mottagare, monkeypatch):
    skicka(monkeypatch)
    mottagare.lista = [{"id": "id-1", "issue": 101, "status": "infort", "version": "2.1.0", "svar": None}]
    rader = forslag.nyheter()
    assert rader[0] == "Ett av dina förslag finns med i den här versionen:"
    assert "Det var krångligt" in rader[1]
    assert forslag.nyheter() == []


def test_okand_status_upprepar_inte_nyheten(bok, mottagare, monkeypatch):
    skicka(monkeypatch)
    infort = {"id": "id-1", "issue": 101, "status": "infort", "version": "2.1.0", "svar": None}
    mottagare.lista = [infort]
    assert forslag.nyheter()
    mottagare.lista = [{**infort, "status": "okand", "version": None}]
    assert forslag.nyheter() == []
    assert forslag.installningar()["senast_sedda"]["id-1"] == "infort"
    mottagare.lista = [infort]
    assert forslag.nyheter() == []


def test_nyheter_utan_forslag_gor_inget_anrop(bok, mottagare):
    assert forslag.nyheter() == []
    assert mottagare.huvuden == []


def test_nyheter_ar_tyst_och_snabb_nar_mottagaren_droger(bok, mottagare, monkeypatch):
    skicka(monkeypatch)
    mottagare.sov = 2.0
    start = time.monotonic()
    assert forslag.nyheter(timeout=0.5) == []
    assert time.monotonic() - start < 1.5


def test_init_efter_uppgradering_visar_nyheter(bok, mottagare, monkeypatch):
    skicka(monkeypatch)
    mottagare.lista = [{"id": "id-1", "issue": 101, "status": "infort", "version": "2.1.0", "svar": None}]
    path = bok / ".claude/skills/bok/SKILL.md"
    path.write_text(path.read_text().replace(f"bok-version: {__version__}", "bok-version: 1.9.0"))
    actions = init_repo(bok, git=False)
    assert "Ett av dina förslag finns med i den här versionen:" in actions


def test_init_utan_uppgradering_ror_inte_natet(bok, mottagare, monkeypatch):
    skicka(monkeypatch)
    antal = len(mottagare.huvuden)
    init_repo(bok, git=False)
    assert len(mottagare.huvuden) == antal


def test_installning_pa_som_standard(bok, mottagare, capsys):
    assert main(["forslag", "installning"]) == 0
    assert capsys.readouterr().out.strip() == "pa"
    assert mottagare.huvuden == []
    path = forslag.katalog() / "nyckel"
    assert not path.exists()


def test_installning_efter_av(bok, mottagare, monkeypatch, capsys):
    assert main(["forslag", "av"]) == 0
    capsys.readouterr()
    assert main(["forslag", "installning"]) == 0
    assert capsys.readouterr().out.strip() == "av"
    assert mottagare.huvuden == []
    path = forslag.katalog() / "nyckel"
    assert not path.exists()


def test_nyheter_tyst_vid_http_exception(bok, monkeypatch):
    import http.client
    skicka(monkeypatch)
    monkeypatch.setattr("bok.forslag._anrop", lambda *a, **kw: (_ for _ in ()).throw(http.client.IncompleteRead(b"")))
    assert forslag.nyheter() == []
