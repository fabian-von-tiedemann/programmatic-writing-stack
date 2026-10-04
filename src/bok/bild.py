"""Tillfälliga bilder utanför boken (gatubilder och arkivbilder), och bok bild.

Bilderna hamnar i systemets temp-katalog, aldrig i boken. Mappar äldre än ett dygn rensas
automatiskt, och bok karta stada rensar allt."""

from __future__ import annotations

import argparse
import http.client
import shutil
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from bok import __version__
from bok.rot import BokFel

PREFIX = ("bok-gatuvy-", "bok-bild-")
MAX_ALDER = 24 * 3600
MAX_STORLEK = 15 * 1024 * 1024
TYPER = {"image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif", "image/webp": ".webp", "image/tiff": ".tif"}
FEL = "Bara bilder (jpeg, png, gif, webp, tiff) via http eller https, högst 15 MB."


class BildFel(BokFel):
    pass


def _mappar() -> list[Path]:
    bas = Path(tempfile.gettempdir())
    try:
        return [p for p in bas.iterdir() if p.is_dir() and p.name.startswith(PREFIX)]
    except OSError:
        return []


def rensa_gamla() -> None:
    gransen = time.time() - MAX_ALDER
    for mapp in _mappar():
        try:
            if mapp.stat().st_mtime < gransen:
                shutil.rmtree(mapp, ignore_errors=True)
        except OSError:
            pass


def ny_mapp(prefix: str) -> Path:
    rensa_gamla()
    return Path(tempfile.mkdtemp(prefix=prefix))  # mkdtemp skapar mappen med 0700


def stada() -> int:
    borta = 0
    for mapp in _mappar():
        shutil.rmtree(mapp, ignore_errors=True)
        borta += not mapp.exists()
    return borta


class _Omdirigering(urllib.request.HTTPRedirectHandler):
    max_redirections = 5

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlsplit(newurl).scheme not in ("http", "https"):
            fp.close()
            raise BildFel(FEL)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_OPPNARE = urllib.request.build_opener(_Omdirigering)


def hamta(url: str) -> Path:
    if urllib.parse.urlsplit(url).scheme not in ("http", "https"):
        raise BildFel(FEL)
    req = urllib.request.Request(url, headers={"User-Agent": f"bok/{__version__}"})
    try:
        with _OPPNARE.open(req, timeout=20) as svar:
            typ = svar.headers.get_content_type()
            if typ not in TYPER:
                raise BildFel(FEL)
            data = svar.read(MAX_STORLEK + 1)
    except BildFel:
        raise
    except urllib.error.HTTPError as exc:
        raise BildFel(f"Bilden kunde inte hämtas (svar {exc.code}).") from None
    except (urllib.error.URLError, TimeoutError, OSError, http.client.HTTPException, ValueError):
        raise BildFel("Bilden kunde inte hämtas.") from None
    if len(data) > MAX_STORLEK:
        raise BildFel(FEL)
    path = ny_mapp("bok-bild-") / ("bild" + TYPER[typ])
    path.write_bytes(data)
    return path


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("bild", help="ladda ner en bild (till exempel ur ett arkiv) till en tillfällig mapp utanför boken")
    p.add_argument("url")
    p.set_defaults(func=_kor)


def _kor(args: argparse.Namespace) -> int:
    path = hamta(args.url)
    print(f"Bilden ligger i {path}")
    print("Den sparas inte i boken. Rensa med bok karta stada när du har tittat.")
    return 0
