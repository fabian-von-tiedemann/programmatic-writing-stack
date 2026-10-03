"""bok status: var boken står och vad som är nästa steg, härlett ur filerna."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from bok import boktoml, frontmatter
from bok.graf import Graf, GrafFel, ar_oppen
from bok.rapport import GRANSKARE_AXLAR, las_alla
from bok.rot import find_root
from bok.validera import block

KONCEPT = ("bok/koncept/premiss.md", "bok/koncept/genre.md", "bok/koncept/form.md", "bok/koncept/teman.md")
PLOT = ("bok/plot/struktur.md", "bok/plot/bagar.md")
ROST = ("bok/stil/rost.md",)
KAPITELPLAN = "bok/plot/kapitelplan.md"
MAX_RUNDOR = 3
PASSERAT = 8
GRANSKARE = tuple(GRANSKARE_AXLAR)
NAMN = {"redaktor": "Redaktören", "sprakgranskare": "Språkgranskaren"}
_RAD = re.compile(r"^\|\s*(\d+)\s*\|\s*(?:akt\s*)?(\d+)\s*\|", re.M | re.I)
_KAPFIL = re.compile(r"^kapitel-(\d+)\.md$")


def ofylld(path: Path) -> bool:
    return not path.is_file() or "{{" in path.read_text(encoding="utf-8")


def _del(namn: str, filer: tuple[str, ...], root: Path) -> dict:
    saknas = [f"{Path(f).name} är inte ifylld" for f in filer if ofylld(root / f)]
    return {"namn": namn, "klar": not saknas, "saknas": saknas}


def _kapitelplan_del(root: Path) -> dict:
    klar = 1 in kapitelplan(root).values()
    return {"namn": "Kapitelplan", "klar": klar, "saknas": [] if klar else ["ingen rad för akt 1 i kapitelplan.md"]}


_REVISION = re.compile(r"^\s*- \[ \] (?:kapitel\s+(\d+)|(alla))\s*:", re.M | re.I)


def _verkliga_del(root: Path, rapporter: list[dict]) -> dict | None:
    """Sensitivitetsläsning av planen, bara när canon.md listar verkliga händelser."""
    path = root / "bok" / "canon.md"
    if not path.is_file() or not block(path.read_text(encoding="utf-8"), "verkliga-handelser"):
        return None
    s = _senaste(rapporter, omfang="forberedelse", roll="sensitivitet")
    if s and s["utfall"] == "godkand":
        return {"namn": "Verkliga händelser", "klar": True, "saknas": []}
    saknas = "sensitivitetsläsaren vill ha ändringar i planen" if s else "sensitivitetsläsning av planen saknas"
    return {"namn": "Verkliga händelser", "klar": False, "saknas": [saknas]}


def revisioner(root: Path) -> dict:
    path = root / "bok" / "revisioner.md"
    ut: dict = {"alla": 0, "kapitel": {}}
    if not path.is_file():
        return ut
    for kap, alla in _REVISION.findall(path.read_text(encoding="utf-8")):
        if alla:
            ut["alla"] += 1
        else:
            ut["kapitel"][int(kap)] = ut["kapitel"].get(int(kap), 0) + 1
    return ut


def _karaktarer(root: Path) -> dict:
    katalog = root / "bok" / "karaktarer"
    filer = sorted(p for p in katalog.glob("*.md") if p.name not in ("MALL.md", "README.md"))
    if not filer:
        return {"namn": "Karaktärer", "klar": False, "saknas": ["ingen karaktär än"]}
    # Bara POV-karaktärerna måste vara ifyllda; bikaraktärer får växa under skrivandet.
    saknas, pov = [], 0
    for p in filer:
        text = p.read_text(encoding="utf-8")
        try:
            meta, _ = frontmatter.split(text)
        except frontmatter.FrontmatterFel:
            saknas.append(f"{p.name} har ett trasigt huvud (raderna mellan --- överst)")
            continue
        if meta.get("pov") is True:
            pov += 1
            if "{{" in text:
                saknas.append(f"{p.name} är inte ifylld")
        elif meta.get("pov") is not False:
            saknas.append(f"{p.name}: ange pov: true eller false")
    if pov == 0:
        saknas.append("ingen POV-karaktär (pov: true)")
    return {"namn": "Karaktärer", "klar": not saknas, "saknas": saknas}


def kapitelplan(root: Path) -> dict[int, int]:
    path = root / KAPITELPLAN
    if not path.is_file():
        return {}
    return {int(k): int(a) for k, a in _RAD.findall(path.read_text(encoding="utf-8"))}


def _kapitelfil(katalog: Path, nr: int) -> Path | None:
    for p in katalog.glob("kapitel-*.md"):
        if (m := _KAPFIL.match(p.name)) and int(m.group(1)) == nr:
            return p
    return None


def _kapitelnummer(root: Path, plan: dict[int, int]) -> list[int]:
    nr = set(plan)
    for katalog in (root / "manuskript", root / "bok" / "plot" / "kapitel"):
        nr.update(int(m.group(1)) for p in katalog.glob("kapitel-*.md") if (m := _KAPFIL.match(p.name)))
    return sorted(nr)


def _scenkort(root: Path, nr: int) -> tuple[bool, bool, str | None, dict]:
    """(finns och är ifyllt, godkänt, fel i huvudet, huvudet)."""
    path = _kapitelfil(root / "bok" / "plot" / "kapitel", nr)
    if path is None:
        return False, False, None, {}
    text = path.read_text(encoding="utf-8")
    if "{{" in text:
        return False, False, None, {}
    try:
        meta, _ = frontmatter.split(text)
    except frontmatter.FrontmatterFel as exc:
        return False, False, str(exc).rstrip("."), {}
    return True, meta.get("godkand") is True, None, meta


def _granska_nasta(nr: int, runda: int) -> tuple[str, str]:
    return ("ska granskas" if runda == 1 else f"granskning runda {runda}",
            f"Kapitel {nr}: kör bok validate och bok tics, sedan Redaktör och Språkgranskare (runda {runda}).")


def _fack(nr: int, fack_r: dict | None, runda: int) -> tuple[str, str] | None:
    """Fackgranskningen före granskningsrunda `runda`; None när den är godkänd."""
    if fack_r is None:
        return "fackgranskning", f"Kapitel {nr}: Researcher fackgranskar kapitlet (runda {runda})."
    if fack_r["utfall"] == "atgarda":
        return "revision efter fackgranskning", (f"Kapitel {nr}: Writer reviderar efter fackgranskningen, "
                                                 f"sedan ny fackgranskning (runda {runda}).")
    return None


def _lage(nr, scenkort, plan_ok, kortfel, utkast, sammanfattning, g, senaste, forf,
          fack: bool = False, fack_r: dict | None = None) -> tuple[str, str | None]:
    if forf and forf["utfall"] == "godkand" and forf["runda"] >= g:
        if sammanfattning:
            return "klart", None
        return "kontinuitet", f"Kapitel {nr}: Kontinuitet uppdaterar grafen och skriver sammanfattningen (runda {g})."
    if kortfel:
        return "scenkortets huvud är trasigt", (f"Kapitel {nr}: huvudet i scenkortet (raderna mellan --- "
                                                f"överst) är trasigt ({kortfel}). Rätta det.")
    if not scenkort:
        return "scenkort saknas", f"Kapitel {nr}: Plot-arkitekten gör scenkortet."
    if not plan_ok:
        return "scenkortet väntar på ditt ja", f"Kapitel {nr}: scenkortet väntar på ditt ja."
    if not utkast:
        return "utkast saknas", f"Kapitel {nr}: Writer skriver utkastet."
    if g == 0:
        if fack and (steg := _fack(nr, fack_r, 1)):
            return steg
        return _granska_nasta(nr, 1)
    if forf and forf["utfall"] == "tillbaka" and forf["runda"] >= g:
        if fack and fack_r is not None:
            return _fack(nr, fack_r, g + 1) or _granska_nasta(nr, g + 1)
        mellan = "fackgranskning och granskning" if fack else "granskning"
        return "tillbaka till Writer", (f"Kapitel {nr}: Writer reviderar efter dina kommentarer, "
                                        f"sedan {mellan} runda {g + 1}.")
    if saknade := [r for r in GRANSKARE if r not in senaste]:
        return f"granskning runda {g}", f"Kapitel {nr}: {' och '.join(NAMN[r] for r in saknade)} ska granska runda {g}."
    utfall = {r["utfall"] for r in senaste.values()}
    if "eskalera" in utfall or ("revidera" in utfall and g >= MAX_RUNDOR):
        return "du bestämmer", (f"Kapitel {nr}: granskarna är inte nöjda efter runda {g}: "
                                "du bestämmer – godkänn eller skicka tillbaka.")
    if "revidera" in utfall:
        if fack and fack_r is not None:
            return _fack(nr, fack_r, g + 1) or _granska_nasta(nr, g + 1)
        mellan = "fackgranskning och granskning" if fack else "granskning"
        return "revision", (f"Kapitel {nr}: Writer reviderar efter fynden i runda {g}, "
                            f"sedan {mellan} runda {g + 1}." + _vill_ha_revision(senaste))
    if not sammanfattning:
        return "kontinuitet", f"Kapitel {nr}: Kontinuitet uppdaterar grafen och skriver sammanfattningen (runda {g})."
    return "väntar på din läsning", (f"Kapitel {nr}: läs manuskript/kapitel-{nr:02d}.md "
                                     "och godkänn eller skicka tillbaka.")


def _vill_ha_revision(senaste: dict) -> str:
    delar = []
    for roll in GRANSKARE:
        r = senaste.get(roll)
        if r and r["utfall"] == "revidera":
            lagt = [f"{a} {v}" for a, v in (r.get("betyg") or {}).items() if isinstance(v, int) and v < PASSERAT]
            delar.append(f" {NAMN[roll]}" + (f": {', '.join(lagt)}." if lagt else "."))
    return "".join(delar)


def _kapitel(root: Path, nr: int, akt: int | None, rapporter: list[dict]) -> dict:
    egna = [r for r in rapporter if r["omfang"] == "kapitel" and r.get("kapitel") == nr]
    scenkort, plan_ok, kortfel, meta = _scenkort(root, nr)
    manus = _kapitelfil(root / "manuskript", nr)
    granskning = [r for r in egna if r["roll"] in GRANSKARE]
    g = max((r["runda"] for r in granskning), default=0)
    # Sammanfattningen är aktuell när Kontinuitet har kört för senaste granskningsrundan.
    # Filtider duger inte: git checkout skriver filerna i indexordning.
    kont = max((r["runda"] for r in egna if r["roll"] == "kontinuitet"), default=0)
    aktuell = _kapitelfil(root / "bok" / "sammanfattningar", nr) is not None and kont >= g
    senaste = {r["roll"]: r for r in granskning if r["runda"] == g}
    fack_v = meta.get("fack")
    fack = bool(fack_v.strip()) if isinstance(fack_v, str) else isinstance(fack_v, list) and bool(fack_v)
    fack_r = next((r for r in egna if r["roll"] == "researcher" and r["runda"] == g + 1), None)
    forf = max((r for r in egna if r["roll"] == "forfattare"), key=lambda r: r["runda"], default=None)
    betyg: dict = {}
    for roll in GRANSKARE:
        if roll in senaste:
            betyg.update(senaste[roll].get("betyg") or {})
    lage, nasta = _lage(nr, scenkort, plan_ok, kortfel, manus is not None, aktuell, g, senaste, forf, fack, fack_r)
    return {"nr": nr, "akt": akt, "lage": lage, "runda": g, "betyg": betyg, "klart": nasta is None, "nasta": nasta}


def _senaste(rapporter: list[dict], **villkor) -> dict | None:
    valda = [r for r in rapporter if all(r.get(k) == v for k, v in villkor.items())]
    return max(valda, key=lambda r: r["runda"], default=None)


def _nasta(forb, ja, kapitel, plan, rapporter) -> str:
    for d in forb:
        if not d["klar"]:
            return f"Förberedelse: {d['namn']} – {d['saknas'][0]}."
    if not ja:
        return "Förberedelsen är klar: läs sammanfattningen av boken och ge ditt ja."
    akter: dict[int, list[int]] = {}
    for nr, akt in plan.items():
        akter.setdefault(akt, []).append(nr)
    for k in kapitel:
        if not k["klart"]:
            return k["nasta"]
        if k["akt"] is not None and k["nr"] == max(akter[k["akt"]]):
            fl = _senaste(rapporter, omfang="akt", akt=k["akt"], roll="forlaggare")
            if fl and fl["utfall"] == "atgarda":
                return f"Akt {k['akt']}: åtgärda Förläggarens fynd och låt Förläggaren läsa akten igen."
            if not fl or fl["utfall"] != "fortsatt":
                return f"Akt {k['akt']} är skriven: Förläggaren läser akten."
    if not kapitel:
        return "Kapitel 1: Plot-arkitekten gör scenkortet."
    slut = _senaste(rapporter, omfang="bok", roll="forlaggare")
    if not slut or slut["utfall"] not in ("A", "B", "C"):
        return "Alla planerade kapitel är klara. Planera fler i kapitelplanen, eller låt Förläggaren göra slutläsningen."
    if slut["utfall"] != "A":
        return (f"Förläggaren gav {slut['utfall']}: arbeta igenom åtgärderna och "
                "låt Förläggaren läsa boken igen.")
    sens = _senaste(rapporter, omfang="bok", roll="sensitivitet")
    if not sens:
        return "Boken har fått A: sensitivitetsläsningen återstår."
    if sens["utfall"] != "godkand":
        return "Åtgärda sensitivitetsläsarens fynd och låt sensitivitetsläsaren läsa boken igen."
    return "Boken är klar. Tillval: bok mall forlag, audiobook eller marknad."


def _plan_bagar(root: Path) -> list[tuple[str, int | None]]:
    path = root / "bok" / "plot" / "bagar.md"
    if ofylld(path):
        return []
    ut = []
    for sektion in re.split(r"(?m)^## ", path.read_text(encoding="utf-8"))[1:]:
        if m := re.search(r"(?m)^id:\s*(\S+)", sektion):
            s = re.search(r"(?m)^start:\s*kapitel\s*(\d+)", sektion)
            ut.append((m.group(1), int(s.group(1)) if s else None))
    return ut


def _bagar(root: Path, kapitel: list[dict]) -> dict:
    tom = {"stillastaende": [], "ej_paborjade": [], "olosta_planteringar": []}
    senast = max((k["nr"] for k in kapitel if k["klart"]), default=0)
    try:
        graf = Graf.load(root)
    except GrafFel as exc:
        return {**tom, "fel": str(exc)}
    threads = {t["id"]: t for t in graf.lista("threads") if t.get("id")}
    ej = [bid for bid, start in _plan_bagar(root)
          if start is not None and start <= senast and not (threads.get(bid) or {}).get("steg")]
    still = []
    for tid, t in threads.items():
        if not ar_oppen(t):
            continue
        steg = [s["kapitel"] for s in t.get("steg") or [] if isinstance(s, dict) and isinstance(s.get("kapitel"), int)]
        if steg and senast - max(steg) >= 3:
            still.append({"id": tid, "senast": max(steg)})
    olosta = [{"bage": tid, "vad": p.get("vad", ""), "kapitel": p.get("kapitel")}
              for tid, t in threads.items() for p in t.get("planteringar") or []
              if isinstance(p, dict) and not p.get("loses_i")]
    return {"stillastaende": still, "ej_paborjade": ej, "olosta_planteringar": olosta}


def compute(root: Path) -> dict:
    bok = boktoml.read(root)
    rapporter = las_alla(root)
    forb = [_del("Koncept", KONCEPT, root), _karaktarer(root), _del("Plot", PLOT, root),
            _del("Röst", ROST, root), _kapitelplan_del(root)]
    if verkliga := _verkliga_del(root, rapporter):
        forb.append(verkliga)
    forb_ja = _senaste(rapporter, omfang="forberedelse", roll="forfattare")
    ja = forb_ja is not None and forb_ja["utfall"] == "godkand"
    plan = kapitelplan(root)
    kapitel = [_kapitel(root, nr, plan.get(nr), rapporter) for nr in _kapitelnummer(root, plan)]
    rev = revisioner(root)
    for k in kapitel:
        k["revisioner"] = rev["kapitel"].get(k["nr"], 0)
    return {
        "titel": bok.get("titel", ""),
        "forberedelse": forb,
        "forberedelse_godkand": ja,
        "kapitel": kapitel,
        "bagar": _bagar(root, kapitel),
        "nasta": _nasta(forb, ja, kapitel, plan, rapporter),
        "revisioner_alla": rev["alla"],
    }


def render_text(s: dict) -> str:
    r = [f"# {s['titel']}", "", "Förberedelse"]
    for d in s["forberedelse"]:
        r.append(f"  {'✓' if d['klar'] else '✗'} {d['namn']}" + ("" if d["klar"] else f": {'; '.join(d['saknas'])}"))
    r.append(f"  {'✓' if s['forberedelse_godkand'] else '✗'} Ditt ja på helheten")
    if s["kapitel"]:
        r += ["", "Kapitel"]
        for k in s["kapitel"]:
            akt = f" (akt {k['akt']})" if k["akt"] else ""
            betyg = " · ".join(f"{a} {v}" for a, v in k["betyg"].items())
            rev = f"  ({k['revisioner']} öppna revisioner)" if k.get("revisioner") else ""
            r.append(f"  {k['nr']}{akt}: {k['lage']}" + (f"  [{betyg}]" if betyg else "") + rev)
    if s.get("revisioner_alla"):
        r += ["", f"Revisioner för hela boken: {s['revisioner_alla']} öppna"]
    b = s["bagar"]
    varningar = []
    if b.get("fel"):
        varningar.append(f"grafen kunde inte läsas: {b['fel']}")
    varningar += [f"{x} skulle ha börjat men har inte rört sig i texten" for x in b["ej_paborjade"]]
    varningar += [f"{x['id']} har inte rört sig sedan kapitel {x['senast']}" for x in b["stillastaende"]]
    if b["olosta_planteringar"]:
        varningar.append(f"{len(b['olosta_planteringar'])} planteringar väntar på upplösning")
    if varningar:
        r += ["", "Bågar", *(f"  ! {v}" for v in varningar)]
    r += ["", f"Nästa steg: {s['nasta']}"]
    return "\n".join(r) + "\n"


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("status", help="var boken står och vad som är nästa steg")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=_kor)


def _kor(args: argparse.Namespace) -> int:
    s = compute(find_root())
    print(json.dumps(s, ensure_ascii=False, indent=2) if args.json else render_text(s), end="" if not args.json else "\n")
    return 0
