import http.client
import http.server
import io
import json
import os
import stat
import threading
import urllib.error
import urllib.parse
import urllib.request
from email.message import Message

import pytest

from bok import google
from bok.privat import katalog

NYCKEL = "AIzaTESTNYCKEL-0123456789abcdefghijk"


@pytest.fixture
def nyckel(monkeypatch):
    monkeypatch.setenv("BOK_GOOGLE_MAPS_NYCKEL", NYCKEL)


def _svar(status, data, typ="application/json"):
    return google.Svar(status, typ, data if isinstance(data, bytes) else json.dumps(data).encode())


def test_miljovariabeln_gar_fore_filen(monkeypatch):
    google.spara_nyckel("fil-nyckel-0123456789abcdef")
    assert google.nyckel() == "fil-nyckel-0123456789abcdef"
    assert google.nyckel_kalla() == "fil"
    monkeypatch.setenv("BOK_GOOGLE_MAPS_NYCKEL", NYCKEL)
    assert google.nyckel() == NYCKEL
    assert google.nyckel_kalla() == "miljövariabel"


def test_nyckelfilen_ar_privat_och_kan_tas_bort():
    google.spara_nyckel(NYCKEL)
    google.spara_signering("vNIXE0xscrmjlyV-12Nj_BvUPaw=")
    path = katalog() / "google-maps-nyckel"
    assert stat.S_IMODE(os.stat(path).st_mode) == 0o600
    assert stat.S_IMODE(os.stat(path.parent).st_mode) == 0o700
    assert google.signering() == "vNIXE0xscrmjlyV-12Nj_BvUPaw="
    assert google.ta_bort() == ["google-maps-nyckel", "google-maps-signering"]
    assert google.nyckel_kalla() is None and google.signering() is None


def test_ingen_nyckel():
    with pytest.raises(google.KartaFel, match="bok karta nyckel"):
        google.nyckel()


def test_signering_enligt_googles_exempel():
    assert google.signera("/maps/api/geocode/json?address=New+York&client=clientID",
                          "vNIXE0xscrmjlyV-12Nj_BvUPaw=") == "chaRF2hTJKOScPr-RQCEhZbSzIE="


def test_trasig_signeringshemlighet():
    with pytest.raises(google.KartaFel, match="Signeringshemligheten"):
        google.signera("/x", "inte base64!!")
    with pytest.raises(google.KartaFel, match="Signeringshemligheten"):
        google.spara_signering("inte base64!!")


def test_routes_anropet(nyckel, monkeypatch):
    sett = {}

    def oppna(req, timeout=google.TIMEOUT):
        sett.update(url=req.full_url, nyckel=req.get_header("X-goog-api-key"),
                    falt=req.get_header("X-goog-fieldmask"), kropp=json.loads(req.data), metod=req.get_method())
        return _svar(200, {"routes": []})

    monkeypatch.setattr(google, "_oppna", oppna)
    assert google.routes({"travelMode": "WALK"}, "routes.duration") == {"routes": []}
    assert sett == {"url": google.ROUTES_URL, "nyckel": NYCKEL, "falt": "routes.duration",
                    "kropp": {"travelMode": "WALK"}, "metod": "POST"}


@pytest.mark.parametrize("status,data,text", [
    (400, {"error": {"status": "INVALID_ARGUMENT", "details": [{"reason": "API_KEY_INVALID"}]}}, "godkänner inte nyckeln"),
    (403, {"error": {"status": "PERMISSION_DENIED", "details": [{"reason": "SERVICE_DISABLED"}]}}, "får inte använda Routes API"),
    (429, {"error": {"status": "RESOURCE_EXHAUSTED"}}, "Dagens tak för Routes API"),
    (400, {"error": {"status": "INVALID_ARGUMENT", "message": f"bad {NYCKEL}"}}, "kunde inte tolka"),
    (500, b"<html>", "oväntat"),
])
def test_routes_fel(nyckel, monkeypatch, status, data, text):
    monkeypatch.setattr(google, "_oppna", lambda req, timeout=google.TIMEOUT: _svar(status, data))
    with pytest.raises(google.KartaFel, match=text) as info:
        google.routes({}, "routes.duration")
    assert NYCKEL not in str(info.value)


@pytest.mark.parametrize("svar,text", [
    ({"status": "REQUEST_DENIED", "error_message": "The provided API key is invalid."}, "godkänner inte nyckeln"),
    ({"status": "REQUEST_DENIED", "error_message": "This API project is not authorized to use this API."},
     "får inte använda Street View Static API"),
    ({"status": "OVER_QUERY_LIMIT"}, "Dagens tak för Street View Static API"),
    ({"status": "UNKNOWN_ERROR"}, "oväntat"),
])
def test_metadata_fel(nyckel, monkeypatch, svar, text):
    monkeypatch.setattr(google, "_oppna", lambda req, timeout=google.TIMEOUT: _svar(200, svar))
    with pytest.raises(google.KartaFel, match=text):
        google.gatuvy_metadata("59.3,18.0")


def test_metadata_ok_och_tomt(nyckel, monkeypatch):
    sett = []

    def oppna(req, timeout=google.TIMEOUT):
        sett.append(dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(req.full_url).query)))
        return _svar(200, {"status": "ZERO_RESULTS"} if len(sett) > 1 else {"status": "OK", "pano_id": "p1"})

    monkeypatch.setattr(google, "_oppna", oppna)
    assert google.gatuvy_metadata("Storgatan 1, Exempelstad")["pano_id"] == "p1"
    assert google.gatuvy_metadata("59.3,18.0")["status"] == "ZERO_RESULTS"
    assert sett[0] == {"location": "Storgatan 1, Exempelstad", "source": "outdoor", "radius": "50", "key": NYCKEL}


def test_bild_och_signatur(nyckel, monkeypatch):
    monkeypatch.setenv("BOK_GOOGLE_MAPS_SIGNERING", "vNIXE0xscrmjlyV-12Nj_BvUPaw=")
    sett = {}

    def oppna(req, timeout=google.TIMEOUT):
        sett["url"] = req.full_url
        return _svar(200, b"\xff\xd8", typ="image/jpeg")

    monkeypatch.setattr(google, "_oppna", oppna)
    assert google.gatuvy_bild("p1", 89.6) == b"\xff\xd8"
    delar = urllib.parse.urlsplit(sett["url"])
    fraga, signatur = delar.query.rsplit("&signature=", 1)
    assert signatur == google.signera(delar.path + "?" + fraga, "vNIXE0xscrmjlyV-12Nj_BvUPaw=")
    assert dict(urllib.parse.parse_qsl(fraga)) == {"size": "640x640", "pano": "p1", "heading": "90", "pitch": "0",
                                                    "fov": "90", "return_error_code": "true", "key": NYCKEL}


@pytest.mark.parametrize("status,signering,fel,text", [
    (404, None, google.IngenBild, "ingen gatubild"),
    (429, None, google.KartaFel, "Dagens tak"),
    (403, None, google.KartaFel, "bok karta nyckel --signering"),
    (403, "vNIXE0xscrmjlyV-12Nj_BvUPaw=", google.KartaFel, "godkände inte signaturen"),
    (200, None, google.KartaFel, "oväntat"),  # 200 men inte en bild
])
def test_bild_fel(nyckel, monkeypatch, status, signering, fel, text):
    if signering:
        monkeypatch.setenv("BOK_GOOGLE_MAPS_SIGNERING", signering)
    monkeypatch.setattr(google, "_oppna", lambda req, timeout=google.TIMEOUT: _svar(status, b"x", typ="text/plain"))
    with pytest.raises(fel, match=text):
        google.gatuvy_bild("p1", 0)


class _Kastar:
    def __init__(self, fel):
        self.fel = fel

    def open(self, req, timeout=None):
        raise self.fel(req)


def _http_fel(req):
    kropp = json.dumps({"error": {"message": f"key {NYCKEL} denied", "status": "PERMISSION_DENIED"}}).encode()
    return urllib.error.HTTPError(req.full_url, 403, f"nekad {req.full_url}", Message(), io.BytesIO(kropp))


@pytest.mark.parametrize("fel", [
    _http_fel,
    lambda req: urllib.error.URLError(f"kunde inte nå {req.full_url}"),
    lambda req: TimeoutError(req.full_url),
    lambda req: http.client.RemoteDisconnected(req.full_url),
    lambda req: ValueError(req.full_url),
    lambda req: TypeError(req.full_url),
    lambda req: LookupError(req.full_url),
], ids=["http", "url", "timeout", "frankopplad", "valueerror", "typeerror", "lookuperror"])
def test_nyckeln_lacker_aldrig(nyckel, monkeypatch, fel):
    monkeypatch.setattr(google, "_OPPNARE", _Kastar(fel))
    for anrop in (lambda: google.gatuvy_metadata("59.3,18.0"), lambda: google.gatuvy_bild("p1", 0),
                  lambda: google.routes({"travelMode": "WALK"}, "routes.duration")):
        with pytest.raises(google.KartaFel) as info:
            anrop()
        assert NYCKEL not in str(info.value)
        assert info.value.__cause__ is None
        assert info.value.__context__ is None or info.value.__suppress_context__


def test_omdirigering_foljs_inte(nyckel, monkeypatch):
    mottagna = []

    class Hanterare(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            mottagna.append(self.path.split("?")[0])
            self.send_response(302)
            self.send_header("Location", "/annan")
            self.send_header("Content-Length", "0")
            self.end_headers()

    server = http.server.HTTPServer(("127.0.0.1", 0), Hanterare)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        monkeypatch.setattr(google, "_OPPNARE", urllib.request.build_opener(google._IngenOmdirigering))
        monkeypatch.setattr(google, "METADATA_URL", f"http://127.0.0.1:{server.server_port}/meta")
        with pytest.raises(google.KartaFel) as info:
            google.gatuvy_metadata("59.3,18.0")
        assert NYCKEL not in str(info.value)
        assert mottagna == ["/meta"]
    finally:
        server.shutdown()
