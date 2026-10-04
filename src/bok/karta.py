"""bok karta: restider och gatubilder från Google Maps med författarens egen nyckel.

Inget från Google sparas i boken. Restider visas och glöms; gatubilder hamnar i en tillfällig
mapp utanför boken (se bild.py). Nyckeln hanteras bara av google.py."""

from __future__ import annotations

import argparse
import getpass
import re
import shutil
import sys
from datetime import date, datetime, time, timedelta

from bok import bild, geo, google
from bok.google import KartaFel
from bok.graf import Graf
from bok.platser import Plats, tolka
from bok.rot import BokFel, find_root

SATT = {
    "gang": ("WALK", "till fots"),
    "cykel": ("BICYCLE", "cykel"),
    "bil": ("DRIVE", "bil"),
    "kollektivt": ("TRANSIT", "kollektivt"),
}
BAS_FALT = "routes.duration,routes.distanceMeters"
KOLL_FALT = (BAS_FALT + ",routes.legs.steps.travelMode,routes.legs.steps.staticDuration"
             ",routes.legs.steps.transitDetails")
POLY_FALT = "routes.polyline.encodedPolyline"
ATTRIBUTION = "Google Maps · beräknad {datum} · dagens vägnät och tidtabell, inte bokens tid."
BETA = ("WALK, BICYCLE, and TWO_WHEELER routes are in beta and might sometimes be missing clear sidewalks, "
        "pedestrian paths, or bicycling paths.\n"
        "Gång- och cykelvägar är i beta och kan sakna tydliga trottoarer, gångvägar eller cykelvägar.")
MAX_ANTAL = 20
STATUS_FRAN = {"location": {"latLng": {"latitude": 59.3326, "longitude": 18.0649}}}
STATUS_TILL = {"location": {"latLng": {"latitude": 59.3340, "longitude": 18.0630}}}


def _sek(v) -> int:
    if isinstance(v, str) and v.endswith("s"):
        try:
            return round(float(v[:-1]))
        except ValueError:
            return 0
    return 0


def _tid(sek: int) -> str:
    minuter = max(1, round(sek / 60)) if sek else 0
    if minuter < 60:
        return f"{minuter} min"
    return f"{minuter // 60} h {minuter % 60:02d} min"


def _langd(m) -> str:
    if not isinstance(m, (int, float)) or isinstance(m, bool):
        return ""
    return f"{m} m" if m < 1000 else f"{m / 1000:.1f} km".replace(".", ",")


def _satt_lista(text: str) -> list[str]:
    valda = [s.strip() for s in text.split(",") if s.strip()]
    okanda = [s for s in valda if s not in SATT]
    if okanda or not valda:
        raise KartaFel(f"Okänt färdsätt: {', '.join(okanda) or text}. Välj bland {', '.join(SATT)}.")
    return valda


def _kollektiv_tid(avgang: str | None, ankomst: str | None, dag: str | None, idag: date) -> dict:
    if avgang and ankomst:
        raise KartaFel("Ange antingen --avgang eller --ankomst, inte båda.")
    klocka = avgang or ankomst
    if not klocka:
        if dag:
            raise KartaFel("--dag behöver --avgang eller --ankomst.")
        return {}
    try:
        d = date.fromisoformat(dag) if dag else idag
    except ValueError:
        raise KartaFel("--dag ska vara ÅÅÅÅ-MM-DD.") from None
    if not idag - timedelta(days=7) <= d <= idag + timedelta(days=100):
        raise KartaFel("Kollektivtrafik går bara att räkna från 7 dagar bakåt till 100 dagar framåt. "
                       "Äldre tidtabeller finns inte hos Google.")
    if not re.fullmatch(r"\d{1,2}:\d{2}", klocka):
        raise KartaFel("Tiden ska vara HH:MM, till exempel 08:15.")
    try:
        t = time(*map(int, klocka.split(":")))
    except ValueError:
        raise KartaFel("Tiden ska vara HH:MM, till exempel 08:15.") from None
    stampel = datetime.combine(d, t).astimezone().isoformat()
    return {"departureTime" if avgang else "arrivalTime": stampel}


def _kollektivt(rutt: dict) -> str:
    """Linjer och gångsträckor i ordning: "avgång 08:15: gå 3 min, buss 4 mot X (6 hållplatser), …"."""
    delar: list[str] = []
    avgang = None
    gang = 0

    def ga() -> None:
        nonlocal gang
        if gang >= 60:
            delar.append(f"gå {round(gang / 60)} min")
        gang = 0

    for leg in rutt.get("legs") or []:
        for steg in (leg.get("steps") or []) if isinstance(leg, dict) else []:
            if not isinstance(steg, dict):
                continue
            detaljer = steg.get("transitDetails")
            if steg.get("travelMode") == "TRANSIT" and isinstance(detaljer, dict):
                ga()
                linje = detaljer.get("transitLine") or {}
                fordon = str(((linje.get("vehicle") or {}).get("name") or {}).get("text") or "linje").lower()
                text = f"{fordon} {linje.get('nameShort') or linje.get('name') or ''}".strip()
                if detaljer.get("headsign"):
                    text += f" mot {detaljer['headsign']}"
                if isinstance(detaljer.get("stopCount"), int):
                    text += f" ({detaljer['stopCount']} hållplatser)"
                if avgang is None:
                    lokalt = detaljer.get("localizedValues") or {}
                    avgang = ((lokalt.get("departureTime") or {}).get("time") or {}).get("text")
                delar.append(text)
            else:
                gang += _sek(steg.get("staticDuration"))
    ga()
    if all(d.startswith("gå ") for d in delar):
        return ""
    return (f"avgång {avgang}: " if avgang else "") + ", ".join(delar)


def _forsta_rutt(data: dict) -> dict | None:
    rutter = data.get("routes")
    if isinstance(rutter, list) and rutter and isinstance(rutter[0], dict):
        return rutter[0]
    return None


def _restid(fran: Plats, till: Plats, satt: list[str], tider: dict) -> int:
    print(f"{fran.namn} → {till.namn}")
    for s in satt:
        lage, etikett = SATT[s]
        kropp = {"origin": fran.routes(), "destination": till.routes(), "travelMode": lage, "languageCode": "sv"}
        if lage == "DRIVE":
            kropp["routingPreference"] = "TRAFFIC_UNAWARE"
        if lage == "TRANSIT":
            kropp.update(tider)
        rutt = _forsta_rutt(google.routes(kropp, KOLL_FALT if lage == "TRANSIT" else BAS_FALT))
        if rutt is None:
            print(f"  {etikett:<12}ingen rutt hittades")
            continue
        rad = f"  {etikett:<12}{_tid(_sek(rutt.get('duration'))):>8}  {_langd(rutt.get('distanceMeters'))}".rstrip()
        if lage == "DRIVE":
            rad += "  (utan trafik)"
        if lage == "TRANSIT" and (beskrivning := _kollektivt(rutt)):
            rad += f"  {beskrivning}"
        print(rad)
    print()
    print(ATTRIBUTION.format(datum=date.today().isoformat()))
    if {"gang", "cykel"} & set(satt):
        print(BETA)
    return 0


def _kor_nyckel(args: argparse.Namespace) -> int:
    if args.ta_bort:
        borta = google.ta_bort()
        print("Nyckeln är borttagen." if borta else "Det fanns ingen sparad nyckel.")
        if google.nyckel_kalla() == "miljövariabel":
            print("BOK_GOOGLE_MAPS_NYCKEL är fortfarande satt i din terminal; ta bort den där.")
        return 0
    if not sys.stdin.isatty():
        raise KartaFel(f"Kör bok karta nyckel i din egen terminal, inte via Claude. Se guiden {google.GUIDE}")
    if args.signering:
        varde = getpass.getpass("Klistra in URL-signeringshemligheten (syns inte): ").strip()
        google.spara_signering(varde)
        print("Signeringshemligheten är sparad.")
        return 0
    varde = getpass.getpass("Klistra in nyckeln till Google Maps (syns inte): ").strip()
    if len(varde) < 20 or any(c.isspace() for c in varde):
        raise KartaFel("Det där ser inte ut som en nyckel. Kopiera den igen från Google Cloud.")
    google.spara_nyckel(varde)
    print("Nyckeln är sparad. Kontrollera den med bok karta status.")
    return 0


def _kor_status() -> int:
    kalla = google.nyckel_kalla()
    if kalla is None:
        print(google.INGEN_NYCKEL)
        return 1
    print(f"Nyckel: finns ({kalla}).")
    print("Signering: finns." if google.signering() else "Signering: ingen (behövs bara om Street View kräver det).")
    routes_ok = True
    try:
        google.routes({"origin": STATUS_FRAN, "destination": STATUS_TILL, "travelMode": "WALK"}, "routes.duration")
        print(f"{google.ROUTES}: fungerar.")
    except KartaFel as exc:
        routes_ok = False
        print(f"{google.ROUTES}: {exc}")
    try:
        google.gatuvy_metadata("59.3326,18.0649")
        print(f"{google.STREET_VIEW}: fungerar.")
    except KartaFel as exc:
        print(f"{google.STREET_VIEW}: {exc} (Street View är frivilligt; se steg 6 i guiden.)")
    return 0 if routes_ok else 1


def _platser_i_boken() -> list[dict]:
    try:
        root = find_root()
    except BokFel:
        return []
    return Graf.load(root).lista("locations")


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("karta", help="restider och gatubilder från Google Maps (kräver en egen nyckel)")
    k = p.add_subparsers(dest="karta_kommando", metavar="<kommando>", required=True)
    n = k.add_parser("nyckel", help="lägg in nyckeln till Google Maps (kör i din egen terminal)")
    n.add_argument("--signering", action="store_true", help="lägg in Street Views URL-signeringshemlighet")
    n.add_argument("--ta-bort", action="store_true", help="ta bort nyckeln och signeringshemligheten")
    k.add_parser("status", help="om nyckeln finns och fungerar")
    r = k.add_parser("restid", help="restid och avstånd i dag mellan två platser")
    r.add_argument("fran", metavar="från")
    r.add_argument("till")
    r.add_argument("--satt", default="gang,cykel,bil,kollektivt", help="gang, cykel, bil, kollektivt (kommaseparerat)")
    r.add_argument("--avgang", metavar="HH:MM", help="avgångstid för kollektivt")
    r.add_argument("--ankomst", metavar="HH:MM", help="ankomsttid för kollektivt")
    r.add_argument("--dag", metavar="ÅÅÅÅ-MM-DD", help="dag för kollektivt (standard: i dag)")
    g = k.add_parser("gatuvy", help="gatubilder på en plats eller längs en rutt, till en tillfällig mapp")
    g.add_argument("plats")
    g.add_argument("till", nargs="?")
    g.add_argument("--satt", default="gang", choices=list(SATT))
    g.add_argument("--antal", type=int, default=8)
    g.add_argument("--mellanrum", type=float, default=150.0)
    k.add_parser("stada", help="rensa tillfälliga gatubilder och arkivbilder")
    p.set_defaults(func=_kor)


def _kor(args: argparse.Namespace) -> int:
    kommando = args.karta_kommando
    if kommando == "nyckel":
        return _kor_nyckel(args)
    if kommando == "status":
        return _kor_status()
    if kommando == "stada":
        antal = bild.stada()
        print(f"Rensade {antal} tillfällig mapp." if antal == 1 else f"Rensade {antal} tillfälliga mappar.")
        return 0
    if kommando == "restid":
        satt = _satt_lista(args.satt)
        tider = _kollektiv_tid(args.avgang, args.ankomst, args.dag, date.today())
        platser = _platser_i_boken()
        fran, till = tolka(args.fran, platser), tolka(args.till, platser)
        google.nyckel()
        return _restid(fran, till, satt, tider)
    platser = _platser_i_boken()
    fran = tolka(args.plats, platser)
    till = tolka(args.till, platser) if args.till else None
    return _gatuvy(fran, till, args.satt, args.antal, args.mellanrum)


def _fotodatum(datum: list[str]) -> str:
    unika = sorted(set(datum))
    if not unika:
        return "okänt"
    return unika[0] if len(unika) == 1 else f"{unika[0]} – {unika[-1]}"


def _vyer_langs(fran: Plats, till: Plats, satt: str, antal: int, mellanrum: float) -> list[tuple[dict, float, str]]:
    kropp = {"origin": fran.routes(), "destination": till.routes(), "travelMode": SATT[satt][0]}
    rutt = _forsta_rutt(google.routes(kropp, POLY_FALT))
    poly = ((rutt or {}).get("polyline") or {}).get("encodedPolyline")
    if not isinstance(poly, str) or not poly:
        raise KartaFel(f"Ingen rutt hittades mellan {fran.namn} och {till.namn}.")
    try:
        linje = geo.avkoda_polyline(poly)  # bara i minnet
    except ValueError:
        raise KartaFel("Google svarade med en trasig rutt.") from None
    punkter = geo.punkter_langs(linje, mellanrum, antal)
    vyer = []
    for nr, (punkt, meter, riktning) in enumerate(punkter):
        etikett = "start" if nr == 0 else "mål" if nr == len(punkter) - 1 else f"{round(meter)} m"
        vyer.append((google.gatuvy_metadata(f"{punkt[0]:.6f},{punkt[1]:.6f}"), riktning, etikett))
    return vyer


def _gatuvy(fran: Plats, till: Plats | None, satt: str, antal: int, mellanrum: float) -> int:
    if not 1 <= antal <= MAX_ANTAL:
        raise KartaFel(f"--antal ska vara mellan 1 och {MAX_ANTAL}.")
    if mellanrum < 10:
        raise KartaFel("--mellanrum ska vara minst 10 meter.")
    if till is None:
        meta = google.gatuvy_metadata(fran.streetview())
        if meta.get("status") != "OK":
            raise KartaFel(f"Det finns ingen gatubild inom 50 meter från {fran.namn}.")
        vyer = [(meta, float(riktning), "") for riktning in (0, 90, 180, 270)]
        rubrik = f"runt {fran.namn}"
    else:
        vyer = _vyer_langs(fran, till, satt, antal, mellanrum)
        rubrik = f"längs {fran.namn} → {till.namn}"
    mapp = bild.ny_mapp("bok-gatuvy-")
    rader: list[str] = []
    datum: list[str] = []
    forsta = None
    forra_pano = None
    try:
        for meta, riktning, etikett in vyer:
            pano = meta.get("pano_id") if meta.get("status") == "OK" else None
            if till is not None and pano and pano == forra_pano:
                continue
            if not isinstance(pano, str) or not pano:
                rader.append(f"  –       ingen gatubild           {etikett}".rstrip())
                continue
            forra_pano = pano
            try:
                data = google.gatuvy_bild(pano, riktning)
            except google.IngenBild:
                rader.append(f"  –       ingen gatubild           {etikett}".rstrip())
                continue
            fil = f"{sum(1 for _ in mapp.iterdir()) + 1:02d}.jpg"
            (mapp / fil).write_bytes(data)
            d = meta.get("date") if isinstance(meta.get("date"), str) else None
            if d:
                datum.append(d)
            if forsta is None:
                forsta = (meta, riktning)
            rader.append(f"  {fil}  fotograferat {d or 'okänt':<8}  mot {geo.vaderstreck(riktning):<9} {etikett}".rstrip())
    except BaseException:
        if forsta is None:
            shutil.rmtree(mapp, ignore_errors=True)
        raise
    if forsta is None:
        shutil.rmtree(mapp, ignore_errors=True)
        print("Inga gatubilder hittades.")
        return 0
    print(f"Gatubilder (Google Street View) {rubrik} i {mapp}/")
    print("\n".join(rader))
    print(f"Fotograferat: {_fotodatum(datum)}. Hämtat {date.today().isoformat()}. Dagens värld, inte bokens tid.")
    plats = forsta[0].get("location") or {}
    lat, lng = plats.get("lat"), plats.get("lng")
    if isinstance(lat, (int, float)) and isinstance(lng, (int, float)):
        print(f"Öppna i webbläsaren: https://www.google.com/maps/@?api=1&map_action=pano"
              f"&viewpoint={lat}%2C{lng}&heading={round(forsta[1])}")
    print("Rensa när beskrivningen är skriven: bok karta stada")
    return 0
