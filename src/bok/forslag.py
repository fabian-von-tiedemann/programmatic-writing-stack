"""Förslag till dem som bygger bok.

Skillen skriver ett utkast, användaren säger ja, och förslaget skickas med en anonym
nyckel till mottagaren. Allt sparas också lokalt, så att inget går förlorat."""

from __future__ import annotations

import argparse
import contextlib
import http.client
import json
import os
import secrets
import sys
import tempfile
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

from bok import __version__, frontmatter
from bok.rot import BokFel, find_root

# Mottagaren (mottagare/) på Fabians privata Cloudflare-konto. BOK_FORSLAG_URL ersätter den i tester.
STANDARD_URL = "https://bok-forslag.lindvide.workers.dev"
TYPER = ("forbattring", "problem", "fraga", "lardom")
MAX_TEXT = 4000
MAX_SAMMANHANG = 2000
MAX_ROLL = 40
MAX_LAGE = 200
STATUSTEXT = {"mottaget": "mottaget", "planerat": "planerat", "infort": "infört i {version}", "avbojt": "avböjt"}
# Svar som betyder att just det här förslaget aldrig kommer att tas emot; skickas inte igen.
SLUTGILTIGA = (400, 401, 403, 413)


class ForslagFel(BokFel):
    pass


class MottagarFel(ForslagFel):
    def __init__(self, kod: int | None, text: str):
        self.kod = kod
        super().__init__(text)


def katalog() -> Path:
    bas = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(bas) / "bok"


def _url() -> str:
    return os.environ.get("BOK_FORSLAG_URL", STANDARD_URL).rstrip("/") + "/v1/forslag"


def _skapa_katalog(path: Path) -> None:
    ny = not path.exists()
    os.makedirs(path, mode=0o700, exist_ok=True)
    if ny:
        os.chmod(path, 0o700)


def _skriv_privat(path: Path, text: str) -> None:
    """Skriver hela filen eller inget: först till en tillfällig fil bredvid, sedan byts den in."""
    _skapa_katalog(path.parent)
    fd, tillfallig = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            os.chmod(tillfallig, 0o600)
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tillfallig, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tillfallig)
        raise


def _las(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ForslagFel(f"{path} går inte att läsa. Rätta eller ta bort filen.") from exc


def nyckel() -> str:
    path = katalog() / "nyckel"
    if path.exists():
        varde = _las(path).strip()
        if len(varde) < 32:
            raise ForslagFel(f"{path} är trasig. Ta bort filen så skapas en ny nyckel "
                             "(dina tidigare förslag syns då inte längre i bok forslag).")
        return varde
    varde = secrets.token_urlsafe(32)
    _skriv_privat(path, varde + "\n")
    return varde


def installningar() -> dict:
    path = katalog() / "installningar.json"
    if not path.exists():
        return {"forslag": "pa", "senast_sedda": {}}
    try:
        data = json.loads(_las(path))
    except json.JSONDecodeError as exc:
        raise ForslagFel(f"{path} går inte att läsa. Rätta eller ta bort filen.") from exc
    if not isinstance(data, dict):
        raise ForslagFel(f"{path} går inte att läsa. Rätta eller ta bort filen.")
    data.setdefault("forslag", "pa")
    data.setdefault("senast_sedda", {})
    return data


def spara_installningar(data: dict) -> None:
    _skriv_privat(katalog() / "installningar.json", json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def ar_pa() -> bool:
    return installningar().get("forslag") != "av"


def las_lokala() -> list[dict]:
    path = katalog() / "forslag.jsonl"
    if not path.exists():
        return []
    rader = []
    for nr, rad in enumerate(_las(path).splitlines(), 1):
        if not rad.strip():
            continue
        try:
            rader.append(json.loads(rad))
        except json.JSONDecodeError as exc:
            raise ForslagFel(f"{path} rad {nr} är trasig. Rätta eller ta bort raden.") from exc
    return rader


def _spara_lokala(rader: list[dict]) -> None:
    _skriv_privat(katalog() / "forslag.jsonl", "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rader))


def tolka_utkast(text: str) -> dict:
    meta, body = frontmatter.split(text)
    typ = meta.get("typ")
    if typ not in TYPER:
        raise ForslagFel(f"typ måste vara en av {', '.join(TYPER)}.")
    ord_ = body.strip()
    if not ord_:
        raise ForslagFel("Förslaget saknar text (hennes ord under raderna ---).")
    if len(ord_) > MAX_TEXT:
        raise ForslagFel(f"Förslaget får vara högst {MAX_TEXT} tecken.")
    sammanhang = str(meta.get("sammanhang") or "").strip()
    if len(sammanhang) > MAX_SAMMANHANG:
        raise ForslagFel(f"Sammanhanget får vara högst {MAX_SAMMANHANG} tecken.")
    roll = str(meta.get("roll") or "").strip()
    if len(roll) > MAX_ROLL:
        raise ForslagFel(f"roll får vara högst {MAX_ROLL} tecken.")
    return {"typ": typ, "text": ord_, "sammanhang": sammanhang, "roll": roll}


def _lage() -> str:
    """Grovt läge utan filnamn eller namn ur boken."""
    from bok.status import compute

    try:
        s = compute(find_root())
    except (BokFel, OSError, UnicodeDecodeError):
        return ""
    if not s["forberedelse_godkand"] or not all(d["klar"] for d in s["forberedelse"]):
        return "förberedelse"
    for k in s["kapitel"]:
        if not k["klart"]:
            return f"kapitel {k['nr']}: {k['lage']}"[:MAX_LAGE]
    return "alla kapitel klara"


class _IngenOmdirigering(urllib.request.HTTPRedirectHandler):
    """Följer aldrig en omdirigering: nyckeln ska bara gå till mottagarens egen adress."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        fp.close()
        raise MottagarFel(None, "Mottagaren svarade oväntat.")


_OPPNARE = urllib.request.build_opener(_IngenOmdirigering)


def _anrop(metod: str, data: dict | None, timeout: float):
    kropp = json.dumps(data, ensure_ascii=False).encode("utf-8") if data is not None else None
    req = urllib.request.Request(_url(), data=kropp, method=metod, headers={
        "Authorization": f"Bearer {nyckel()}",
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": f"bok/{__version__}",
    })
    try:
        with _OPPNARE.open(req, timeout=timeout) as svar:
            resultat = json.loads(svar.read().decode("utf-8") or "null")
    except urllib.error.HTTPError as exc:
        try:
            fel = json.loads(exc.read().decode("utf-8")).get("fel", "")
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            fel = ""
        raise MottagarFel(exc.code, fel or f"Mottagaren svarade {exc.code}.") from exc
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, UnicodeDecodeError,
            http.client.HTTPException) as exc:
        raise MottagarFel(None, "Kunde inte nå mottagaren just nu.") from exc
    if not isinstance(resultat, dict if metod == "POST" else list):
        raise MottagarFel(None, "Mottagaren svarade oväntat.")
    return resultat


def _skicka_rad(rad: dict) -> None:
    data = {k: rad[k] for k in ("typ", "text", "sammanhang", "version", "lage", "roll")}
    try:
        svar = _anrop("POST", data, timeout=10)
    except MottagarFel as exc:
        if exc.kod in SLUTGILTIGA:
            rad["avvisat"] = str(exc)
        raise
    rad.update(skickat=True, id=svar.get("id"), issue=svar.get("issue"))


def _kontrollera_pa() -> None:
    if not ar_pa():
        raise ForslagFel("Förslag är avstängda. Slå på dem med bok forslag pa.")


def skicka_utkast(text: str) -> dict:
    _kontrollera_pa()
    falt = tolka_utkast(text)
    rader = las_lokala()
    rad = {"lokalt_id": uuid.uuid4().hex, "tid": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           **falt, "version": __version__, "lage": _lage(), "skickat": False, "id": None, "issue": None}
    rader.append(rad)
    _spara_lokala(rader)
    try:
        _skicka_rad(rad)
    finally:
        _spara_lokala(rader)
    return rad


def skicka_igen() -> tuple[int, list[str]]:
    _kontrollera_pa()
    rader = las_lokala()
    skickade, fel = 0, []
    try:
        for rad in rader:
            if rad.get("skickat") or rad.get("avvisat"):
                continue
            try:
                _skicka_rad(rad)
                skickade += 1
            except MottagarFel as exc:
                fel.append(str(exc))
                if exc.kod in (None, 429):  # nätet nere eller för många: försök inte med resten nu
                    break
    finally:
        _spara_lokala(rader)
    return skickade, fel


def lista() -> tuple[list[dict], bool]:
    """Användarens förslag med status. Andra värdet: om status gick att hämta."""
    lokala = las_lokala()
    status: dict = {}
    ok = True
    if lokala and ar_pa() and any(r.get("skickat") for r in lokala):
        try:
            status = {s["id"]: s for s in _anrop("GET", None, timeout=10)}
        except (MottagarFel, KeyError, TypeError):
            ok = False
    ut = []
    for rad in lokala:
        s = status.get(rad.get("id"))
        if rad.get("avvisat"):
            text = f"avvisat: {rad['avvisat']}"
        elif not rad.get("skickat"):
            text = "inte skickat än"
        elif s and s.get("status") in STATUSTEXT:
            text = STATUSTEXT[s["status"]].format(version=s.get("version") or "")
        else:
            text = "skickat"
        ut.append({"datum": rad.get("tid", "")[:10], "rubrik": rad["text"].splitlines()[0][:60],
                   "status": text, "svar": (s or {}).get("svar")})
    return ut, ok


def nyheter(timeout: float = 3.0) -> list[str]:
    """Rader om förslag som blivit införda sedan förra gången. Tyst vid alla fel."""
    try:
        if not ar_pa():
            return []
        lokala = {r.get("id"): r for r in las_lokala() if r.get("skickat")}
        if not lokala:
            return []
        aktuella = {s["id"]: s for s in _anrop("GET", None, timeout=timeout)}
        inst = installningar()
        sedda = inst["senast_sedda"]
        nya = [i for i, s in aktuella.items() if s.get("status") == "infort" and sedda.get(i) != "infort"]
        # Okänd status (till exempel "okand" när issuet inte gick att läsa) ändrar inget: annars
        # skulle ett infört förslag meddelas igen när det väl går att läsa.
        nya_sedda = {}
        for i, s in aktuella.items():
            varde = s.get("status") if s.get("status") in STATUSTEXT else sedda.get(i)
            if varde is not None:
                nya_sedda[i] = varde
        inst["senast_sedda"] = nya_sedda
        spara_installningar(inst)
    except (BokFel, OSError, ValueError, KeyError, TypeError, AttributeError, http.client.HTTPException):
        return []
    if not nya:
        return []
    forsta = "Ett av dina förslag finns" if len(nya) == 1 else f"{len(nya)} av dina förslag finns"
    rader = [f"{forsta} med i den här versionen:"]
    rader += [f"  – {lokala[i]['text'].splitlines()[0][:60]}" for i in nya if i in lokala]
    return rader


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("forslag", help="förslag till dem som bygger bok: skicka och se status")
    f = p.add_subparsers(dest="forslag_kommando", metavar="<kommando>")
    s = f.add_parser("skicka", help="skicka ett förslag (fil, eller - för stdin)")
    s.add_argument("fil", nargs="?")
    s.add_argument("--igen", action="store_true", help="skicka de förslag som inte kom fram")
    f.add_parser("av", help="stäng av förslag och all nätkontakt")
    f.add_parser("pa", help="slå på förslag igen")
    f.add_parser("installning", help="se om förslag är påslagna eller avstängda")
    p.set_defaults(func=_kor)


def _kor(args: argparse.Namespace) -> int:
    kommando = args.forslag_kommando
    if kommando in ("av", "pa"):
        inst = installningar()
        inst["forslag"] = kommando
        spara_installningar(inst)
        print("Förslag är avstängda: inga erbjudanden och ingen nätkontakt." if kommando == "av"
              else "Förslag är påslagna.")
        return 0
    if kommando == "installning":
        print(installningar().get("forslag", "pa"))
        return 0
    if kommando == "skicka":
        return _kor_skicka(args)
    rader, ok = lista()
    if not ar_pa():
        print("Förslag är avstängda. Slå på dem med bok forslag pa.")
    if not rader:
        print("Du har inte skickat några förslag än.")
        return 0
    if not ok:
        print("Kunde inte hämta status just nu; visar det som finns sparat.")
    for nr, rad in enumerate(rader, 1):
        print(f"{nr}. {rad['datum']}  {rad['rubrik']}  [{rad['status']}]")
        if rad["svar"]:
            print(f"   Svar: {rad['svar']}")
    return 0


def _kor_skicka(args: argparse.Namespace) -> int:
    from bok.tics import las_kapitel

    if args.igen:
        skickade, fel = skicka_igen()
        print(f"Skickade {skickade} förslag.")
        for rad in fel:
            print(f"  {rad}")
        return 1 if fel else 0
    if not args.fil:
        raise ForslagFel("Ange en fil, eller - för att läsa förslaget från stdin.")
    text = sys.stdin.read() if args.fil == "-" else las_kapitel(Path(args.fil))
    try:
        rad = skicka_utkast(text)
    except MottagarFel as exc:
        if exc.kod in SLUTGILTIGA:
            print(f"Förslaget skickades inte: {exc}")
        else:
            print(f"Förslaget är sparat men inte skickat: {exc} Försök igen med bok forslag skicka --igen.")
        return 1
    print(f"Tack! Förslaget är skickat (nummer {rad['issue']}). Med bok forslag ser du vad som händer med det.")
    return 0
