import getpass
import io
import json
import re
import sys
import urllib.error
import urllib.parse
from datetime import date, timedelta
from email.message import Message

import pytest

from bok import google
from bok.cli import main
from bok.privat import katalog
from helpers import skriv_graf

NYCKEL = "AIzaTESTNYCKEL-0123456789abcdefghijk"
GANG = {"routes": [{"duration": "2280s", "distanceMeters": 2900}]}
CYKEL = {"routes": [{"duration": "840s", "distanceMeters": 3100}]}
BIL = {"routes": [{"duration": "660s", "distanceMeters": 3600}]}
KOLL = {"routes": [{"duration": "1440s", "distanceMeters": 4000, "legs": [{"steps": [
    {"travelMode": "WALK", "staticDuration": "120s"},
    {"travelMode": "WALK", "staticDuration": "60s"},
    {"travelMode": "TRANSIT", "staticDuration": "600s", "transitDetails": {
        "headsign": "Radiohuset", "stopCount": 6,
        "localizedValues": {"departureTime": {"time": {"text": "08:15"}}},
        "transitLine": {"nameShort": "4", "vehicle": {"name": {"text": "Buss"}}}}},
    {"travelMode": "WALK", "staticDuration": "30s"},
    {"travelMode": "TRANSIT", "staticDuration": "300s", "transitDetails": {
        "headsign": "Hässelby strand", "stopCount": 4,
        "transitLine": {"nameShort": "19", "vehicle": {"name": {"text": "Tunnelbana"}}}}},
]}]}]}
PLATSER = {"locations": [
    {"id": "hemmet", "namn": "Lägenheten", "adress": "Storgatan 1, Exempelstad"},
    {"id": "fabriken", "namn": "Fabriken", "lat": 59.3, "lng": 18.1},
]}


class FalskGoogle:
    """Står i för google._oppna. Routes svarar per färdsätt; Street View enligt `metadata` och `bilder`."""

    def __init__(self):
        self.anrop = []
        self.rutter = {}
        self.metadata = lambda plats: {"status": "OK", "pano_id": f"p-{plats}", "date": "2023-08",
                                       "location": {"lat": 59.3, "lng": 18.07}}
        self.bilder = {}

    def __call__(self, req, timeout=None):
        url = req.full_url
        if url.startswith(google.ROUTES_URL):
            kropp = json.loads(req.data)
            self.anrop.append(("routes", kropp, req.get_header("X-goog-fieldmask")))
            return google.Svar(200, "application/json", json.dumps(self.rutter.get(kropp["travelMode"], {})).encode())
        fraga = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
        if url.startswith(google.METADATA_URL):
            self.anrop.append(("metadata", fraga, None))
            return google.Svar(200, "application/json", json.dumps(self.metadata(fraga["location"])).encode())
        self.anrop.append(("bild", fraga, None))
        status = self.bilder.get(fraga["pano"], 200)
        return google.Svar(status, "image/jpeg" if status == 200 else "text/plain", b"\xff\xd8bild" if status == 200 else b"")


@pytest.fixture
def falsk(monkeypatch):
    monkeypatch.setenv("BOK_GOOGLE_MAPS_NYCKEL", NYCKEL)
    f = FalskGoogle()
    monkeypatch.setattr(google, "_oppna", f)
    return f


def _filer(root):
    return sorted(p.relative_to(root) for p in root.rglob("*"))


def test_restid_alla_satt(bok, falsk, capsys):
    skriv_graf(bok, PLATSER)
    falsk.rutter = {"WALK": GANG, "BICYCLE": CYKEL, "DRIVE": BIL, "TRANSIT": KOLL}
    fore = _filer(bok)
    assert main(["karta", "restid", "hemmet", "fabriken"]) == 0
    ut = capsys.readouterr().out
    assert "Lägenheten → Fabriken" in ut
    assert re.search(r"till fots\s+38 min\s+2,9 km", ut)
    assert re.search(r"cykel\s+14 min\s+3,1 km", ut)
    assert re.search(r"bil\s+11 min\s+3,6 km\s+\(utan trafik\)", ut)
    assert ("avgång 08:15: gå 3 min, buss 4 mot Radiohuset (6 hållplatser), "
            "tunnelbana 19 mot Hässelby strand (4 hållplatser)") in ut
    assert f"Google Maps · beräknad {date.today().isoformat()} · dagens vägnät och tidtabell, inte bokens tid." in ut
    assert "WALK, BICYCLE, and TWO_WHEELER routes are in beta" in ut
    assert "Gång- och cykelvägar är i beta" in ut
    assert NYCKEL not in ut
    anrop = {k["travelMode"]: (k, falt) for _, k, falt in falsk.anrop}
    assert anrop["WALK"][0]["origin"] == {"address": "Storgatan 1, Exempelstad"}
    assert anrop["WALK"][0]["destination"] == {"location": {"latLng": {"latitude": 59.3, "longitude": 18.1}}}
    assert anrop["DRIVE"][0]["routingPreference"] == "TRAFFIC_UNAWARE"
    assert all(k["languageCode"] == "sv" for k, _ in anrop.values())
    assert anrop["WALK"][1] == "routes.duration,routes.distanceMeters"
    assert "routes.legs.steps.transitDetails" in anrop["TRANSIT"][1]
    assert "departureTime" not in anrop["TRANSIT"][0]
    assert _filer(bok) == fore


def test_kollektivt_utan_betavarning(bok, falsk, capsys):
    falsk.rutter = {"TRANSIT": KOLL}
    assert main(["karta", "restid", "Storgatan 1, Exempelstad", "Torget 2, Exempelstad", "--satt", "kollektivt"]) == 0
    ut = capsys.readouterr().out
    assert "kollektivt" in ut and "beta" not in ut


def test_kollektivt_bara_gang(bok, falsk, capsys):
    falsk.rutter = {"TRANSIT": {"routes": [{"duration": "600s", "distanceMeters": 800, "legs": [
        {"steps": [{"travelMode": "WALK", "staticDuration": "600s"}]}]}]}}
    assert main(["karta", "restid", "Storgatan 1, Exempelstad", "Storgatan 9, Exempelstad", "--satt", "kollektivt"]) == 0
    ut = capsys.readouterr().out
    assert re.search(r"kollektivt\s+10 min\s+800 m", ut) and "avgång" not in ut


def test_ingen_rutt(bok, falsk, capsys):
    falsk.rutter = {"BICYCLE": CYKEL}
    assert main(["karta", "restid", "Storgatan 1, Exempelstad", "Ön 1, Exempelstad", "--satt", "gang,cykel"]) == 0
    ut = capsys.readouterr().out
    assert re.search(r"till fots\s+ingen rutt hittades", ut) and re.search(r"cykel\s+14 min", ut)


def test_lang_restid(bok, falsk, capsys):
    falsk.rutter = {"DRIVE": {"routes": [{"duration": "3900s", "distanceMeters": 95000}]}}
    main(["karta", "restid", "Storgatan 1, Exempelstad", "Annanstans 1, Bortby", "--satt", "bil"])
    assert re.search(r"bil\s+1 h 05 min\s+95,0 km", capsys.readouterr().out)


@pytest.mark.parametrize("flagga,falt", [("--avgang", "departureTime"), ("--ankomst", "arrivalTime")])
def test_tid_for_kollektivt(bok, falsk, flagga, falt):
    dag = (date.today() + timedelta(days=1)).isoformat()
    falsk.rutter = {"TRANSIT": KOLL}
    assert main(["karta", "restid", "A gatan 1", "B gatan 2", "--satt", "kollektivt", flagga, "08:15", "--dag", dag]) == 0
    kropp = falsk.anrop[0][1]
    assert kropp[falt].startswith(f"{dag}T08:15:00")


@pytest.mark.parametrize("extra,text", [
    (["--avgang", "08:15", "--ankomst", "09:00"], "inte båda"),
    (["--avgang", "08:15", "--dag", (date.today() - timedelta(days=8)).isoformat()], "7 dagar bakåt"),
    (["--avgang", "08:15", "--dag", (date.today() + timedelta(days=101)).isoformat()], "100 dagar framåt"),
    (["--avgang", "25:00"], "HH:MM"),
    (["--avgang", "8"], "HH:MM"),
    (["--dag", date.today().isoformat()], "--dag behöver"),
    (["--avgang", "08:15", "--dag", "igår"], "ÅÅÅÅ-MM-DD"),
    (["--satt", "flyg"], "färdsätt"),
])
def test_fel_i_fragan(bok, falsk, capsys, extra, text):
    assert main(["karta", "restid", "A gatan 1", "B gatan 2", *extra]) == 2
    assert text in capsys.readouterr().err
    assert falsk.anrop == []


def test_restid_utan_nyckel(bok, capsys):
    assert main(["karta", "restid", "A gatan 1", "B gatan 2"]) == 2
    assert "bok karta nyckel" in capsys.readouterr().err


def test_okant_id(bok, falsk, capsys):
    skriv_graf(bok, PLATSER)
    assert main(["karta", "restid", "hemmet", "slussen"]) == 2
    assert "finns inte i locations.json" in capsys.readouterr().err


def test_restid_utanfor_en_bok(tmp_path, falsk, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    falsk.rutter = {"WALK": GANG}
    assert main(["karta", "restid", "A gatan 1", "B gatan 2", "--satt", "gang"]) == 0


def test_nyckeln_lacker_inte_via_cli(bok, monkeypatch, capsys):
    monkeypatch.setenv("BOK_GOOGLE_MAPS_NYCKEL", NYCKEL)

    class Kastar:
        def open(self, req, timeout=None):
            raise urllib.error.HTTPError(req.full_url, 403, req.full_url, Message(),
                                         io.BytesIO(f'{{"error": {{"message": "{NYCKEL}"}}}}'.encode()))

    monkeypatch.setattr(google, "_OPPNARE", Kastar())
    for argv in (["karta", "restid", "A gatan 1", "B gatan 2"], ["karta", "status"],
                 ["karta", "gatuvy", "A gatan 1"]):
        main(argv)
        fangat = capsys.readouterr()
        assert NYCKEL not in fangat.out + fangat.err


class _Terminal(io.StringIO):
    def isatty(self):
        return True


def test_nyckel_kraver_terminal(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(NYCKEL + "\n"))
    assert main(["karta", "nyckel"]) == 2
    assert "egen terminal" in capsys.readouterr().err
    assert not (katalog() / "google-maps-nyckel").exists()


def test_nyckel_sparas(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", _Terminal())
    monkeypatch.setattr(getpass, "getpass", lambda prompt="": NYCKEL)
    assert main(["karta", "nyckel"]) == 0
    assert (katalog() / "google-maps-nyckel").read_text(encoding="utf-8") == NYCKEL + "\n"
    assert NYCKEL not in capsys.readouterr().out


@pytest.mark.parametrize("varde", ["kort", "AIza med mellanslag 0123456789"])
def test_nyckel_avvisar(monkeypatch, capsys, varde):
    monkeypatch.setattr(sys, "stdin", _Terminal())
    monkeypatch.setattr(getpass, "getpass", lambda prompt="": varde)
    assert main(["karta", "nyckel"]) == 2
    assert not (katalog() / "google-maps-nyckel").exists()


def test_signering_sparas_och_avvisas(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", _Terminal())
    monkeypatch.setattr(getpass, "getpass", lambda prompt="": "vNIXE0xscrmjlyV-12Nj_BvUPaw=")
    assert main(["karta", "nyckel", "--signering"]) == 0
    assert (katalog() / "google-maps-signering").exists()
    monkeypatch.setattr(getpass, "getpass", lambda prompt="": "inte base64!!")
    assert main(["karta", "nyckel", "--signering"]) == 2


def test_ta_bort(monkeypatch, capsys):
    google.spara_nyckel(NYCKEL)
    assert main(["karta", "nyckel", "--ta-bort"]) == 0
    assert "borttagen" in capsys.readouterr().out
    assert not (katalog() / "google-maps-nyckel").exists()
    monkeypatch.setenv("BOK_GOOGLE_MAPS_NYCKEL", NYCKEL)
    assert main(["karta", "nyckel", "--ta-bort"]) == 0
    assert "BOK_GOOGLE_MAPS_NYCKEL" in capsys.readouterr().out


def test_status_utan_nyckel(capsys):
    assert main(["karta", "status"]) == 1
    assert "Det finns ingen nyckel" in capsys.readouterr().out


def test_status_med_nyckel(falsk, capsys):
    falsk.rutter = {"WALK": GANG}
    assert main(["karta", "status"]) == 0
    ut = capsys.readouterr().out
    assert "Nyckel: finns (miljövariabel)." in ut
    assert "Routes API: fungerar." in ut and "Street View Static API: fungerar." in ut
    assert NYCKEL not in ut


def test_status_street_view_inte_aktiverat(falsk, capsys):
    falsk.metadata = lambda plats: {"status": "REQUEST_DENIED", "error_message": "This API project is not authorized"}
    assert main(["karta", "status"]) == 0
    ut = capsys.readouterr().out
    assert "får inte använda Street View Static API" in ut and "frivilligt" in ut
