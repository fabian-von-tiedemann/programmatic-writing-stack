"""Google Maps Platform: nyckeln, anropen och felen.

Nyckeln och URL:er med nyckeln lämnar aldrig den här modulen. Alla anrop går genom _oppna,
och alla fel blir KartaFel med egna texter, utan URL och utan Googles råa svar (som kan citera
anropet)."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import http.client
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from bok import __version__
from bok.privat import katalog, skriv_privat
from bok.rot import BokFel

ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
STREETVIEW_URL = "https://maps.googleapis.com/maps/api/streetview"
METADATA_URL = "https://maps.googleapis.com/maps/api/streetview/metadata"
GUIDE = "https://github.com/fabian-von-tiedemann/programmatic-writing-stack/blob/main/docs/google-maps.md"
NYCKEL_ENV = "BOK_GOOGLE_MAPS_NYCKEL"
SIGNERING_ENV = "BOK_GOOGLE_MAPS_SIGNERING"
NYCKEL_FIL = "google-maps-nyckel"
SIGNERING_FIL = "google-maps-signering"
TIMEOUT = 10.0
MAX_SVAR = 20 * 1024 * 1024
ROUTES = "Routes API"
STREET_VIEW = "Street View Static API"

INGEN_NYCKEL = (f"Det finns ingen nyckel till Google Maps. Se guiden {GUIDE} "
                "och kör bok karta nyckel i din egen terminal.")
OGILTIG = "Google godkänner inte nyckeln. Kontrollera den i Google Cloud och kör bok karta nyckel igen."
EJ_AKTIVERAT = "Nyckeln får inte använda {api}. Aktivera API:et och kontrollera nyckelns begränsningar ({guide})."
TAK = "Dagens tak för {api} är nått. Försök i morgon, eller höj taket i Google Cloud."
TRASIG_SIGNERING = ("Signeringshemligheten går inte att läsa. Kopiera den igen från Google Cloud "
                    "och kör bok karta nyckel --signering.")


class KartaFel(BokFel):
    pass


class IngenBild(KartaFel):
    """Det finns ingen gatubild för panoramat."""


@dataclass
class Svar:
    status: int
    typ: str
    data: bytes


def _las_hemlighet(env: str, fil: str) -> tuple[str, str] | None:
    if varde := os.environ.get(env, "").strip():
        return varde, "miljövariabel"
    path = katalog() / fil
    if path.is_file() and (varde := path.read_text(encoding="utf-8").strip()):
        return varde, "fil"
    return None


def nyckel_kalla() -> str | None:
    hittad = _las_hemlighet(NYCKEL_ENV, NYCKEL_FIL)
    return hittad[1] if hittad else None


def nyckel() -> str:
    hittad = _las_hemlighet(NYCKEL_ENV, NYCKEL_FIL)
    if hittad is None:
        raise KartaFel(INGEN_NYCKEL)
    return hittad[0]


def signering() -> str | None:
    hittad = _las_hemlighet(SIGNERING_ENV, SIGNERING_FIL)
    return hittad[0] if hittad else None


def spara_nyckel(varde: str) -> None:
    skriv_privat(katalog() / NYCKEL_FIL, varde.strip() + "\n")


def spara_signering(varde: str) -> None:
    signera("/", varde.strip())  # avvisar en hemlighet som inte går att läsa
    skriv_privat(katalog() / SIGNERING_FIL, varde.strip() + "\n")


def ta_bort() -> list[str]:
    borta = []
    for fil in (NYCKEL_FIL, SIGNERING_FIL):
        path = katalog() / fil
        if path.exists():
            path.unlink()
            borta.append(fil)
    return borta


def signera(sokvag_och_fraga: str, hemlighet: str) -> str:
    """Googles URL-signering: HMAC-SHA1 med den URL-säkra base64-hemligheten."""
    try:
        nyckel_ = base64.b64decode(hemlighet + "=" * (-len(hemlighet) % 4), altchars=b"-_", validate=True)
    except (binascii.Error, ValueError):
        raise KartaFel(TRASIG_SIGNERING) from None
    digest = hmac.new(nyckel_, sokvag_och_fraga.encode("utf-8"), hashlib.sha1).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii")


class _IngenOmdirigering(urllib.request.HTTPRedirectHandler):
    """Följer aldrig en omdirigering: nyckeln ska bara gå till Googles egna adresser."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPPNARE = urllib.request.build_opener(_IngenOmdirigering)


def _oppna(req: urllib.request.Request, timeout: float = TIMEOUT) -> Svar:
    """Det enda stället där anrop görs. Inget undantag med URL:en lämnar funktionen."""
    try:
        with _OPPNARE.open(req, timeout=timeout) as svar:
            return Svar(svar.status, svar.headers.get("Content-Type", ""), svar.read(MAX_SVAR))
    except urllib.error.HTTPError as exc:
        try:
            data = exc.read(MAX_SVAR)
        except (OSError, http.client.HTTPException, ValueError):
            data = b""
        typ = exc.headers.get("Content-Type", "") if exc.headers is not None else ""
        return Svar(exc.code, typ, data)
    except Exception:  # alla andra fel också: deras text kan innehålla URL:en med nyckeln
        raise KartaFel("Kunde inte nå Google Maps just nu.") from None


def _json(svar: Svar) -> dict:
    try:
        data = json.loads(svar.data.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _http_fel(status: int, api: str, data: dict) -> KartaFel:
    text = json.dumps(data)
    if "API_KEY_INVALID" in text or "API key not valid" in text:
        return KartaFel(OGILTIG)
    if status == 429 or "RESOURCE_EXHAUSTED" in text:
        return KartaFel(TAK.format(api=api))
    if status == 403 or "PERMISSION_DENIED" in text:
        return KartaFel(EJ_AKTIVERAT.format(api=api, guide=GUIDE))
    if status == 400:
        return KartaFel("Google kunde inte tolka frågan. Kontrollera adresserna och tiderna.")
    return KartaFel(f"Google Maps svarade oväntat ({status}).")


def routes(kropp: dict, falt: str) -> dict:
    req = urllib.request.Request(ROUTES_URL, data=json.dumps(kropp).encode("utf-8"), method="POST", headers={
        "X-Goog-Api-Key": nyckel(),
        "X-Goog-FieldMask": falt,
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": f"bok/{__version__}",
    })
    svar = _oppna(req)
    data = _json(svar)
    if svar.status != 200:
        raise _http_fel(svar.status, ROUTES, data)
    return data


def _gatuvy_request(bas: str, parametrar: dict[str, str]) -> urllib.request.Request:
    fraga = urllib.parse.urlencode({**parametrar, "key": nyckel()})
    if (hemlighet := signering()) is not None:
        fraga += "&signature=" + signera(urllib.parse.urlsplit(bas).path + "?" + fraga, hemlighet)
    return urllib.request.Request(f"{bas}?{fraga}", headers={"User-Agent": f"bok/{__version__}"})


def gatuvy_metadata(plats: str) -> dict:
    """Metadata för närmaste gatubild utomhus inom 50 meter. Gratis. `plats` är "lat,lng" eller en adress."""
    svar = _oppna(_gatuvy_request(METADATA_URL, {"location": plats, "source": "outdoor", "radius": "50"}))
    data = _json(svar)
    if svar.status != 200:
        raise _http_fel(svar.status, STREET_VIEW, data)
    status = data.get("status")
    if status in ("OK", "ZERO_RESULTS", "NOT_FOUND"):
        return data
    if status == "OVER_QUERY_LIMIT":
        raise KartaFel(TAK.format(api=STREET_VIEW))
    if status == "REQUEST_DENIED":
        if "invalid" in str(data.get("error_message", "")).lower():
            raise KartaFel(OGILTIG)
        raise KartaFel(EJ_AKTIVERAT.format(api=STREET_VIEW, guide=GUIDE))
    raise KartaFel("Street View svarade oväntat.")


def gatuvy_bild(pano: str, riktning: float) -> bytes:
    svar = _oppna(_gatuvy_request(STREETVIEW_URL, {
        "size": "640x640", "pano": pano, "heading": f"{riktning:.0f}", "pitch": "0", "fov": "90",
        "return_error_code": "true",
    }))
    if svar.status == 200 and svar.typ.startswith("image/"):
        return svar.data
    if svar.status == 404:
        raise IngenBild("ingen gatubild")
    if svar.status == 429:
        raise KartaFel(TAK.format(api=STREET_VIEW))
    if svar.status == 403:
        if signering() is None:
            raise KartaFel("Street View kräver signering för fler anrop. Lägg till signeringshemligheten "
                           f"med bok karta nyckel --signering (se {GUIDE}).")
        raise KartaFel("Google godkände inte signaturen. Kontrollera signeringshemligheten "
                       "och kör bok karta nyckel --signering igen.")
    raise KartaFel(f"Street View svarade oväntat ({svar.status}).")
