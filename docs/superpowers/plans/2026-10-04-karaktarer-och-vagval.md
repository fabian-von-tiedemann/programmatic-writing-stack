# bok 2.3: förlagor, karaktärsverkstad och vägval – implementationsplan

> **För agenter som exekverar:** OBLIGATORISK UNDER-SKILL: använd superpowers:subagent-driven-development (rekommenderas) eller superpowers:executing-plans för att genomföra planen uppgift för uppgift. Stegen har kryssrutor (`- [ ]`) för uppföljning.

**Mål:** Förlagor (verkliga personer som råmaterial till karaktärer), en rikare karaktärsmall med karaktärsverkstad, och en lätt idéloop för vägval med slumpade frön från verktyget.

**Arkitektur:** Tre små Python-delar: `forlagor.py` läser förlagornas huvuden och används av `bok validate` (namnskydd), `bok status` (sensitivitetsgrind) och `bok fron`. `fron.py` är ett nytt kommando som drar frön med en seedad slumpgenerator ur textlistor i paketet. Resten är ramverkstext: två nya roller, en hantverksfil, nya avsnitt i skillen och processen, ändrade roller och nya bokfiler.

**Teknik:** Python ≥ 3.11 utan beroenden, pytest, hatchling. Kör testerna med `uv run pytest -q`.

**Spec:** `docs/superpowers/specs/2026-10-04-karaktarer-och-vagval-design.md`

**Innan start:** Utvecklaren arbetar i en annan worktree. Börja först när det arbetet är mergat: `git fetch origin && git rebase origin/main` på den här grenen, och kör `uv run pytest -q` så att allt är grönt innan första uppgiften. Har filerna nedan ändrats på `main` sedan planen skrevs: läs dem igen och anpassa ersättningarna, ändra inte riktningen.

## Globala villkor

- Inga nya beroenden: `dependencies = []` i `pyproject.toml`.
- All text som författaren eller rollerna läser är svenska. Följ tonen i befintliga filer: korta meningar, "hon" om författaren, "hen" om personer i boken.
- Inga ord ur `ARVSTERMER` i `tests/test_innehall.py` i `src/bok/data/` (t.ex. "Marléne", "Visby", "Gotland"). Använd neutrala exempel.
- Genererade filer (`src/bok/data/genererat/`) får inte innehålla `{{` (utom begreppet `{{…}}`).
- Sökvägar i backticks som börjar med `bok/`, `.claude/`, `manuskript/` eller `inkorg/` måste finnas i paketet, om de inte innehåller `<`, `{` eller `*` (testet `test_inga_dinglande_sokvagar`).
- Agentfiler: frontmatter `name` = filnamnet, `description` över 40 tecken, `tools` bara ur Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch; brödtexten nämner `` `bok/roller/<roll>.local.md` ``.
- Inga nya obligatoriska fält i `bok status`. Den enda nya grinden: sensitivitetsläsning av planen när boken har förlagor.
- Fel som visas för användaren är `BokFel` och ger exitkod 2 via `bok.cli.main`.
- Versionen höjs inte i den här planen. Ändringarna skrivs under `## [Unreleased]` i `CHANGELOG.md`; releasen görs efteråt med skillen `release` (2.3.0).

## Granskningsfokus

1. **Genitiv av förlagans namn** ("Cathie Woods aktier") ska blockeras som namnet självt; detsamma för `blacklist` ("Olof Palmes"). Test i uppgift 1.
2. **Förlaga med trasigt huvud eller kvarlämnad platshållare** får aldrig krascha `bok validate`, `bok status` eller `bok fron`; `bok validate` varnar att namnet inte skyddas. Test i uppgift 1.
3. **Förlaga som också står bland kända namn** i `canon.md` (personen förekommer som sig själv) ska inte blockeras. Test i uppgift 1.
4. **`bok fron --spara` två gånger i samma varv** (processfröet i ett utvecklingsvarv) ska lägga till en ny dragning, inte skriva över den första. Test i uppgift 3.
5. **Ny bok där POV-personen har de gamla rubrikerna ifyllda men de nya orörda** ska vara klar i `bok status`: de nya rubrikerna är frivilliga. Test i uppgift 4.

---

### Uppgift 1: Förlagor och namnskydd i `bok validate`

**Filer:**
- Skapa: `src/bok/forlagor.py`
- Ändra: `src/bok/validera.py` (`blacklist_traffar`, ny `forlageskydd`, `_kor`)
- Test: `tests/test_forlagor.py`

**Gränssnitt:**
- Producerar: `bok.forlagor.forlagor(root: Path) -> list[dict]`, där varje post är `{"fil": str, "namn": str | None, "alias": list[str]}`; `fil` är relativ till `root` (`"bok/karaktarer/forlagor/cathie-wood.md"`). Hoppar över `MALL.md` och `README.md`. Saknas mappen: `[]`.
- Producerar: `bok.validera.forlageskydd(root: Path, canon_text: str) -> tuple[dict[str, str], list[str]]`: (skyddade namn → fil, filer vars namn inte gick att läsa).
- Ändrar: `bok.validera.blacklist_traffar(text, namn)` träffar även genitiv-s.

- [ ] **Steg 1: Skriv de fallerande testerna**

`tests/test_forlagor.py`:

```python
from bok.cli import main
from bok.forlagor import forlagor
from bok.validera import blacklist_traffar, forlageskydd
from helpers import skriv

FIL = "bok/karaktarer/forlagor/cathie-wood.md"
WOOD = "---\nnamn: Cathie Wood\nalias: [Catherine Wood]\nkaraktarer: [vera]\n---\n\n# Cathie Wood\n"


def test_forlagor_laser_namn_och_alias(bok):
    skriv(bok, FIL, WOOD)
    assert forlagor(bok) == [{"fil": FIL, "namn": "Cathie Wood", "alias": ["Catherine Wood"]}]


def test_mall_och_readme_ar_inte_forlagor(bok):
    skriv(bok, "bok/karaktarer/forlagor/MALL.md", "---\nnamn: {{Personens namn}}\n---\n")
    skriv(bok, "bok/karaktarer/forlagor/README.md", "# Förlagor\n")
    assert forlagor(bok) == []


def test_saknad_mapp_ger_tom_lista(tmp_path):
    assert forlagor(tmp_path) == []


def test_trasigt_huvud_och_fel_typer_kraschar_inte(bok):
    skriv(bok, "bok/karaktarer/forlagor/a.md", "---\nnamn: [trasig\n---\n")
    skriv(bok, "bok/karaktarer/forlagor/b.md", "---\nnamn: 42\nalias: Kalle Ek\n---\n")
    skriv(bok, "bok/karaktarer/forlagor/c.md", "---\nnamn: {{Personens namn}}\n---\n")
    skriv(bok, "bok/karaktarer/forlagor/d.md", "# Utan huvud\n")
    assert [(f["namn"], f["alias"]) for f in forlagor(bok)] == [
        (None, []), (None, ["Kalle Ek"]), (None, []), (None, [])]


def test_blacklist_tar_genitiv():
    assert blacklist_traffar("Hon läste Olof Palmes tal.\n", ["Olof Palme"]) == [(1, "Olof Palme")]
    assert blacklist_traffar("Olof Palmeström\n", ["Olof Palme"]) == []


def test_forlageskydd_undantar_kanda_namn(bok):
    skriv(bok, FIL, WOOD)
    skydd, utan = forlageskydd(bok, "```kanda-namn\nCathie Wood\n```\n")
    assert skydd == {"Catherine Wood": FIL}
    assert utan == []


def test_cli_forlaga_i_manus_blockerar(bok, capsys):
    skriv(bok, FIL, WOOD)
    skriv(bok, "manuskript/kapitel-01.md", "Hon hade sett Cathie Woods intervju.\n")
    assert main(["validate"]) == 1
    out = capsys.readouterr().out
    assert f"BLOCKERANDE rad 1: Cathie Wood är förlaga ({FIL}) och får inte stå i manuset." in out


def test_cli_forlaga_bland_kanda_namn_blockerar_inte(bok, capsys):
    skriv(bok, FIL, "---\nnamn: Cathie Wood\n---\n")
    skriv(bok, "bok/canon.md", "# Canon\n\n```kanda-namn\nCathie Wood\n```\n")
    skriv(bok, "manuskript/kapitel-01.md", "Hon hade sett Cathie Wood på tv.\n")
    assert main(["validate"]) == 0


def test_cli_forlaga_utan_namn_varnar(bok, capsys):
    skriv(bok, "bok/karaktarer/forlagor/x.md", "# Ingen\n")
    skriv(bok, "manuskript/kapitel-01.md", "Hon gick hem.\n")
    assert main(["validate"]) == 0
    assert "bok/karaktarer/forlagor/x.md saknar namn i huvudet; namnet skyddas inte i manuset." in capsys.readouterr().out
```

- [ ] **Steg 2: Kör testerna och se dem falla**

Kör: `uv run pytest tests/test_forlagor.py -q`
Förväntat: FAIL med `ModuleNotFoundError: No module named 'bok.forlagor'`.

- [ ] **Steg 3: Skriv `src/bok/forlagor.py`**

```python
"""Förlagor: verkliga personer som karaktärer bygger på, i bok/karaktarer/forlagor/."""

from __future__ import annotations

from pathlib import Path

from bok import frontmatter

KATALOG = ("bok", "karaktarer", "forlagor")
INTE_FORLAGOR = ("MALL.md", "README.md")


def _text(v) -> str | None:
    if isinstance(v, str) and v.strip() and not v.startswith("{{"):
        return v.strip()
    return None


def forlagor(root: Path) -> list[dict]:
    """En post per förlaga: fil, namn (None om det inte går att läsa) och alias.
    Trasiga huvuden och fel typer ger namn None, aldrig ett undantag."""
    ut = []
    for p in sorted(root.joinpath(*KATALOG).glob("*.md")):
        if p.name in INTE_FORLAGOR:
            continue
        try:
            meta, _ = frontmatter.split(p.read_text(encoding="utf-8"))
        except frontmatter.FrontmatterFel:
            meta = {}
        alias = meta.get("alias")
        alias = [alias] if isinstance(alias, str) else alias if isinstance(alias, list) else []
        ut.append({
            "fil": p.relative_to(root).as_posix(),
            "namn": _text(meta.get("namn")),
            "alias": [a for a in map(_text, alias) if a],
        })
    return ut
```

- [ ] **Steg 4: Ändra `src/bok/validera.py`**

Lägg till importen överst, efter `from bok.graf import …`:

```python
from bok.forlagor import forlagor
```

Ersätt `blacklist_traffar` (genitiv-s):

```python
def blacklist_traffar(text: str, namn: list[str]) -> list[tuple[int, str]]:
    ut = []
    for nr, rad in enumerate(text.splitlines(), 1):
        for n in namn:
            if re.search(rf"(?<!\w){re.escape(n)}s?(?!\w)", rad):
                ut.append((nr, n))
    return ut


def forlageskydd(root: Path, canon_text: str) -> tuple[dict[str, str], list[str]]:
    """Förlagornas namn och alias (namn → fil), utom de som står bland kända namn i canon,
    och de förlagor vars namn inte går att läsa."""
    undantag = set(block(canon_text, "kanda-namn"))
    skydd: dict[str, str] = {}
    utan: list[str] = []
    for f in forlagor(root):
        if f["namn"] is None:
            utan.append(f["fil"])
        for n in ([f["namn"]] if f["namn"] else []) + f["alias"]:
            if n not in undantag:
                skydd.setdefault(n, f["fil"])
    return skydd, utan
```

I `_kor`: efter raden `forbjudna = block(canon, "blacklist")`, lägg till

```python
    skydd, utan_namn = forlageskydd(root, canon)
```

Efter blocket `if not filer: … return 0`, före `kapitel = _kapitel_i_tid(root, graf)`, lägg till

```python
    if utan_namn:
        print("Förlagor")
        for fil in utan_namn:
            print(f"  {fil} saknar namn i huvudet; namnet skyddas inte i manuset.")
```

Ersätt i loopen över filerna raderna från `traffar = blacklist_traffar(text, forbjudna)` till och med `stopp = stopp or bool(traffar)` med

```python
        traffar = blacklist_traffar(text, forbjudna)
        for nr, namn in traffar:
            print(f"  BLOCKERANDE rad {nr}: {namn} står i canon.md som förbjudet namn.")
        forlagetraffar = blacklist_traffar(text, list(skydd))
        for nr, namn in forlagetraffar:
            print(f"  BLOCKERANDE rad {nr}: {namn} är förlaga ({skydd[namn]}) och får inte stå i manuset.")
        stopp = stopp or bool(traffar) or bool(forlagetraffar)
```

och villkoret längst ned i loopen med

```python
        if not traffar and not forlagetraffar and not nya and not varningar:
            print("  Inga anmärkningar.")
```

Uppdatera modulens docstring: `"""bok validate: förbjudna namn och förlagor ur canon.md och bok/karaktarer/forlagor/, och namn som inte finns i grafen."""`

- [ ] **Steg 5: Kör testerna**

Kör: `uv run pytest tests/test_forlagor.py tests/test_validera.py tests/test_validera_tid.py -q`
Förväntat: alla PASS.

- [ ] **Steg 6: Kör hela sviten**

Kör: `uv run pytest -q`
Förväntat: alla PASS.

- [ ] **Steg 7: Commit**

```bash
git add src/bok/forlagor.py src/bok/validera.py tests/test_forlagor.py
git commit -m "feat: bok validate stoppar förlagornas namn och förbjudna namn i genitiv"
```

---

### Uppgift 2: Sensitivitetsgrinden gäller förlagor

**Filer:**
- Ändra: `src/bok/status.py` (`_verkliga_del`, importer)
- Test: `tests/test_status.py`

**Gränssnitt:**
- Konsumerar: `bok.forlagor.forlagor(root)` från uppgift 1.
- Producerar: förberedelsedelen heter `"Verkliga personer och händelser"` när boken har minst en förlaga, annars `"Verkliga händelser"` som förut.

- [ ] **Steg 1: Skriv de fallerande testerna**

Lägg till sist i `tests/test_status.py`:

```python
def test_forlaga_kraver_sensitivitet(bok):
    fyll_forberedelse(bok)
    skriv(bok, "bok/karaktarer/forlagor/cathie-wood.md", "---\nnamn: Cathie Wood\n---\n")
    assert compute(bok)["nasta"] == (
        "Förberedelse: Verkliga personer och händelser – sensitivitetsläsning av planen saknas.")
    rapport(bok, omfang="forberedelse", roll="sensitivitet", utfall="godkand")
    assert compute(bok)["nasta"].startswith("Förberedelsen är klar")


def test_forlaga_med_trasigt_huvud_utloser_ocksa_grinden(bok):
    fyll_forberedelse(bok)
    skriv(bok, "bok/karaktarer/forlagor/x.md", "---\nnamn: [trasig\n---\n")
    assert "Verkliga personer och händelser" in [d["namn"] for d in compute(bok)["forberedelse"]]


def test_mall_readme_och_prov_utloser_ingen_grind_och_ar_inga_karaktarer(bok):
    fyll_forberedelse(bok)
    skriv(bok, "bok/karaktarer/forlagor/MALL.md", "---\nnamn: {{Namn}}\n---\n")
    skriv(bok, "bok/karaktarer/forlagor/README.md", "# Förlagor\n")
    skriv(bok, "bok/karaktarer/prov/anna/1-fel.md", "{{prov}}\n")
    s = compute(bok)
    assert [d["namn"] for d in s["forberedelse"]] == ["Koncept", "Karaktärer", "Plot", "Röst", "Kapitelplan"]
    assert s["forberedelse"][1]["klar"]
```

(`fyll_forberedelse`, `skriv`, `rapport` och `compute` är redan importerade i filen; kontrollera importraden överst och lägg till det som saknas.)

- [ ] **Steg 2: Kör testerna och se dem falla**

Kör: `uv run pytest tests/test_status.py -q -k "forlaga or prov"`
Förväntat: de två första FAIL (grinden finns inte), den tredje PASS redan.

- [ ] **Steg 3: Ändra `src/bok/status.py`**

Lägg till importen efter `from bok.graf import …`:

```python
from bok.forlagor import forlagor
```

Ersätt `_verkliga_del` med:

```python
def _verkliga_del(root: Path, rapporter: list[dict]) -> dict | None:
    """Sensitivitetsläsning av planen, när canon.md listar verkliga händelser eller boken har förlagor."""
    path = root / "bok" / "canon.md"
    handelser = path.is_file() and bool(block(path.read_text(encoding="utf-8"), "verkliga-handelser"))
    personer = bool(forlagor(root))
    if not handelser and not personer:
        return None
    namn = "Verkliga personer och händelser" if personer else "Verkliga händelser"
    s = _senaste(rapporter, omfang="forberedelse", roll="sensitivitet")
    if s and s["utfall"] == "godkand":
        return {"namn": namn, "klar": True, "saknas": []}
    saknas = "sensitivitetsläsaren vill ha ändringar i planen" if s else "sensitivitetsläsning av planen saknas"
    return {"namn": namn, "klar": False, "saknas": [saknas]}
```

- [ ] **Steg 4: Kör testerna**

Kör: `uv run pytest tests/test_status.py -q`
Förväntat: alla PASS, också `test_verkliga_handelser_kraver_sensitivitet` och `test_utan_verkliga_handelser_som_forut`.

- [ ] **Steg 5: Commit**

```bash
git add src/bok/status.py tests/test_status.py
git commit -m "feat: förlagor kräver sensitivitetsläsning av planen"
```

---

### Uppgift 3: `bok fron` och frölistorna

**Filer:**
- Skapa: `src/bok/fron.py`
- Skapa: `src/bok/data/fron/doman.txt`, `omvandning.txt`, `begransning.txt`, `process.txt`
- Ändra: `src/bok/cli.py` (`_moduler`)
- Test: `tests/test_fron.py`

**Gränssnitt:**
- Konsumerar: `bok.forlagor.forlagor(root)` från uppgift 1.
- Producerar: `bok.fron.dra(antal=4, klasser=None, antaganden=None, slump=None, root=None) -> dict` med formen `{"slump": int, "fron": [{"klass": str, "text": str, "antagande": str | None}]}`; `bok.fron.lista(klass) -> list[str]`; `bok.fron.spara(mapp: Path, drag: dict) -> Path`; `bok.fron.FronFel(BokFel)`; konstanterna `FRON`, `KLASSER`, `STANDARD`. Kommandot `bok fron [--antal N] [--klass K]… [--antagande T]… [--slump S] [--spara MAPP] [--json]`.

- [ ] **Steg 1: Skriv de fallerande testerna**

`tests/test_fron.py`:

```python
import json

import pytest

from bok.cli import main
from bok.fron import FRON, KLASSER, FronFel, dra, lista
from helpers import skriv

LISTOR = [k for k in KLASSER if k != "forlaga"]


@pytest.mark.parametrize("klass", LISTOR)
def test_listorna(klass):
    fron = lista(klass)
    assert len(fron) >= 40
    assert len(set(fron)) == len(fron)
    assert all(len(f) <= 140 and not f.endswith(".") for f in fron)


def test_inga_listor_utover_klasserna():
    assert {p.stem for p in FRON.glob("*.txt")} == set(LISTOR)


def test_samma_slump_ger_samma_fron():
    assert dra(slump=7) == dra(slump=7)
    assert dra(slump=7)["fron"] != dra(slump=8)["fron"]


def test_standardfordelning_utan_forlagor():
    klasser = [f["klass"] for f in dra(slump=1)["fron"]]
    assert klasser[:3] == ["doman", "omvandning", "begransning"]
    assert klasser[3] in ("doman", "omvandning", "begransning")


def test_forlaga_blir_fjarde_frot(bok):
    skriv(bok, "bok/karaktarer/forlagor/cathie-wood.md", "---\nnamn: Cathie Wood\n---\n")
    fron = dra(slump=1, root=bok)["fron"]
    assert fron[3] == {"klass": "forlaga",
                       "text": "Cathie Wood (bok/karaktarer/forlagor/cathie-wood.md)", "antagande": None}


def test_forlaga_utan_forlagor_ar_fel(bok):
    with pytest.raises(FronFel, match="inga förlagor"):
        dra(klasser=["forlaga"], antal=1, root=bok)


def test_omvandning_paras_med_antagande():
    antaganden = ["det sker i en scen", "hon är ensam"]
    fron = dra(klasser=["omvandning"], antal=3, antaganden=antaganden, slump=3)["fron"]
    assert all(f["antagande"] in antaganden for f in fron)
    andra = dra(klasser=["doman"], antal=2, antaganden=antaganden, slump=3)["fron"]
    assert all(f["antagande"] is None for f in andra)


def test_inga_dubbletter_i_en_dragning():
    alla = lista("process")
    fron = [f["text"] for f in dra(klasser=["process"], antal=len(alla), slump=5)["fron"]]
    assert sorted(fron) == sorted(alla)


def test_slut_pa_fron_ar_fel():
    with pytest.raises(FronFel, match="inte fler frön"):
        dra(klasser=["process"], antal=len(lista("process")) + 1, slump=5)


def test_antal_noll_ar_fel():
    with pytest.raises(FronFel, match="minst 1"):
        dra(antal=0)


def test_utan_slump_valjs_ett_tal():
    assert isinstance(dra()["slump"], int)


def test_cli_json(bok, capsys):
    assert main(["fron", "--slump", "42", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["slump"] == 42 and len(data["fron"]) == 4
    assert set(data["fron"][0]) == {"klass", "text", "antagande"}


def test_cli_text(bok, capsys):
    assert main(["fron", "--slump", "42", "--antal", "2"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("Slump 42 (samma frön igen: --slump 42)\n1. doman: ")
    assert "\n2. omvandning: " in out


def test_cli_spara_lagger_till(bok):
    mapp = bok / "bok/vagval/2026-10-04-test"
    assert main(["fron", "--slump", "1", "--spara", str(mapp)]) == 0
    assert main(["fron", "--klass", "process", "--antal", "1", "--slump", "2", "--spara", str(mapp)]) == 0
    text = (mapp / "fron.md").read_text(encoding="utf-8")
    assert text.startswith("# Frön\n\n## Slump 1\n\n1. **doman**: ")
    assert "\n## Slump 2\n\n1. **process**: " in text
    assert text.count("# Frön") == 1


def test_cli_okand_klass(bok):
    with pytest.raises(SystemExit):
        main(["fron", "--klass", "planeter"])


def test_cli_fel_blir_exitkod_2(bok, capsys):
    assert main(["fron", "--klass", "forlaga", "--antal", "1"]) == 2
    assert "inga förlagor" in capsys.readouterr().err


def test_cli_utanfor_en_bok(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["fron", "--slump", "1", "--antal", "1"]) == 0
    assert "1. doman: " in capsys.readouterr().out
```

- [ ] **Steg 2: Kör testerna och se dem falla**

Kör: `uv run pytest tests/test_fron.py -q`
Förväntat: FAIL med `ModuleNotFoundError: No module named 'bok.fron'`.

- [ ] **Steg 3: Skriv frölistorna**

Skriv de fyra filerna exakt så här (en rad per frö, kommentarer med `#`, ingen punkt sist på raderna).

`src/bok/data/fron/doman.txt`:

```text
# Avlägsna domäner och fenomen. Grenen frågar: vad i det här motsvarar frågan, och varför?
En bikupa som byter drottning
Tidvattnet i en trång vik
Ett schackparti som slutar i remi
Svampnätverket under en skog
Ett auktionsrum de sista sekunderna
Fågelsträck som byter riktning
En fyrvaktares nattrutin
Restaureringen av en gammal oljemålning
Ett vulkanutbrott som ingen förutsåg
Immunförsvaret som angriper den egna kroppen
En kör där en röst sjunger falskt
Ett sjökort med en ö som inte finns
Isen som lägger sig på en sjö
En räntehöjning i en centralbank
Brobyggare som spänner över en ravin
En jazzimprovisation som tappar takten
Myrstackens arbetsfördelning
Kontrollrummet i ett kraftverk vid ett larm
Ett vittnesförhör som går fel
Barnlekar med hemliga regler
En flyttfågel som kommer tillbaka för tidigt
En operation där kirurgen ändrar plan
Ett lotteri som ingen vann
Stjärnbilder som bara syns från ett ställe
En ruin som återanvänds som stall
Parasiter som styr sin värd
Ett väderomslag i fjällen
En fotbollsmatch i förlängning
Ett kloster med tystnadslöfte
En smugglarrutt över en gräns
Korallrev som bleknar
Tågtidtabellen under en strejk
En trollkarls vilseledning
Arkeologer som gräver i fel lager
Ett bröllop där någon invänder
En dikt som översätts till ett språk utan rim
Ett kasino där huset alltid vinner
Laxens vandring uppströms
En pianostämmare i ett tomt hus
Ett datavirus som sover i åratal
En gruva som vattenfylls
Fjärilseffekten i en väderprognos
Gamla brev som hittas i en vägg
En lavin som utlöses av ett ljud
Ett postkontor där breven aldrig kommer fram
Kartritare vid en okänd kust
En brandmans beslut i ett rökfyllt rum
Kristaller som växer i en grotta
En gerillaodling på en parkeringsplats
Tvillingar som byter plats
En tolk som medvetet översätter fel
Det sista exemplaret av en art
En hängbro som svajar i takt med stegen
En armé som stannar för vintern
Dominobrickor som faller åt fel håll
Ekot i en tom katedral
En provsmakare vid ett hov
Ett vattenverk under torka
Nattbussens sista tur
Mögel som sprider sig bakom tapeten
En dirigent som tappar taktpinnen
Planeter som drar i varandra
Ett kassavalv med tidslås
En fågelholk som tas över av en annan art
Skeppsbrutna på en ö
Ett pussel med en bit för mycket
Ett nattpass på en akutmottagning
En skådespelare som glömmer repliken
En myr som dikas ut
En kurir som inte vet vad hen bär
Ekolodet över ett djuphav
Ett bygdemöte där allt avgörs
En korsning där trafikljusen slocknat
En vargflock som byter ledare
En pokerrunda där alla bluffar
En häxprocess i en liten by
En väderkvarn i vindstilla
Ett museum efter stängning
Brandmän som släcker med motbrand
En arvstvist om en sommarstuga
```

`src/bok/data/fron/omvandning.txt`:

```text
# Operatorer som vänder på ett antagande. Grenen tillämpar operatorn på antagandet som dras med den.
Gör tvärtom
Låt det redan ha hänt när boken börjar
Låt det aldrig hända, och visa vad som händer i stället
Ta bort huvudpersonen ur det
Låt fel person göra det
Låt det ske offentligt i stället för i hemlighet
Låt det ske i hemlighet i stället för offentligt
Flytta det till en helt vardaglig plats
Låt det ta tjugo år i stället för en dag
Låt det ske på en sekund
Gör det komiskt
Låt den som drabbas vara den som driver det
Låt det vara ett misstag, inte ett val
Låt det vara ett val, inte ett misstag
Låt någon annan få äran
Låt någon annan få skulden
Överdriv det tills det blir absurt
Krymp det tills det nästan inte märks
Låt motståndaren vilja samma sak
Låt hjälpen vara det som skadar
Låt den svagaste ha makten
Berätta det baklänges
Låt det hända två gånger, med olika utfall
Låt alla redan veta, utom läsaren
Låt läsaren veta, men ingen i boken
Låt det kosta mer än det ger
Låt det lyckas, och gör framgången till problemet
Låt det misslyckas, och gör misslyckandet till en öppning
Byt plats på orsak och verkan
Låt det ske i ett brev, ett protokoll eller ett formulär
Låt ett barn se det
Låt en främling avgöra det
Gör det lagligt men fel
Gör det olagligt men rätt
Låt kärlek vara motivet
Låt tristess vara motivet
Låt pengar vara oviktiga
Låt det hända någon annan först
Låt det upprepa något som hänt en förälder
Låt den som borde protestera hålla med
Låt det vara oåterkalleligt
Låt det gå att ångra, och låt någon låta bli
Lägg det mitt i en fest
Lägg det i tystnad
Låt platsen vara den som bestämmer
Låt en regel tvinga fram det
Låt en lögn vara sann
Låt sanningen vara det som ingen tror på
Låt den goda och den onda byta roller för en dag
Låt det börja som en tjänst
```

`src/bok/data/fron/begransning.txt`:

```text
# Udda villkor för hur vägvalet ska gestaltas.
Utan dialog
Inom en timme
Sett av ett barn
Sett av någon som inte förstår språket
I ett enda rum
Utan att någon höjer rösten
Medan det regnar hela tiden
Bara med det som syns på ett foto
Under en måltid
I en kö
Där ingen säger vad de menar
Där huvudpersonen bara lyssnar
I ett telefonsamtal
Genom ett sms som skickas till fel person
Med ett husdjur som vittne
Under en begravning
På en arbetsplatsfest
Utan att huvudpersonen är där
I tre meningar
Med ett föremål som byter ägare
Där någon ljuger av omtanke
Under ett strömavbrott
I en bil som står still
På ett sjukhus
Under en flytt
Med en främling som avgör
Där det enda ljudet är en klocka
I ett protokoll från ett möte
Med en felstavning som avslöjar något
Där vädret är det enda som rör sig
Med två personer som pratar om något annat
Under en semester som går fel
Där någon sover
I ett väntrum
Utan att någon rör vid varandra
Där någon äter ensam
Där ett barn ställer en fråga
Under en storstädning
I ett mejl med fel mottagare
Med ett löfte som hålls alltför exakt
Där någon vinner något
Där en dörr inte går att stänga
Med en lukt som ingen nämner
Där någon måste vara artig
I en hiss
Där allt sker på en gång
Under ett firande
Med något som går sönder
Där någon räknar pengar
Vid ett bord som är dukat för en till
Där någon ber om ursäkt för fel sak
På en plats huvudpersonen aldrig varit
Med en gammal vän som inte känner igen hen
Där någon låtsas sova
Under en bilfärd i mörker
Med en lista som någon har skrivit
Där någon sjunger
På en loppis
Med en nyckel som passar fel lås
Där någon har bråttom och någon inte
Under ett läkarbesök
I ett trapphus
Där en granne hör allt
I sista minuten
Med ett djur som gör något oväntat
Där någon städar efter någon annan
I en kyrka utan gudstjänst
Där någon får ett pris
```

`src/bok/data/fron/process.txt`:

```text
# Hur man arbetar när ett varv har fastnat. Dras bara med --klass process.
Börja i slutet och arbeta bakåt
Skriv den sämsta idén först och leta efter det som är bra i den
Ta bort det som alla idéer hittills har gemensamt
Fråga vad den minst viktiga personen vill
Gör den minsta tänkbara versionen
Gör den största tänkbara versionen
Byt genre för en stund
Låt en bifigur bära vägvalet
Fråga vad läsaren fruktar ska hända, och låt något värre eller bättre hända
Leta efter det som skulle vara pinsamt att skriva
Beskriv vägvalet för ett barn
Låt slutet vara bestämt och fråga bara hur
Kombinera de två idéer som passar sämst ihop
Ge den idé som ratades först en chans till
Fråga vad som händer dagen efter
Fråga vad som hände dagen före
Läs premissen som om den gällde någon annan
Leta efter ett föremål som kan bära vägvalet
Fråga vem som tjänar på det
Fråga vem som förlorar mest
Gör det tystare
Gör det högljuddare
Ta bort en person ur scenen
Lägg till en person som inte borde vara där
Låt det som skulle sägas förbli osagt
Säg rakt ut det som ingen säger
Byt tid på dygnet
Byt årstid
Gör det till ett mönster som upprepas
Bryt ett mönster som boken har etablerat
Fråga vad huvudpersonen ljuger för sig själv om
Gör idén konkret: vad syns, vad hörs, vad luktar det
Skriv rubriken innan idén
Välj den idé som skrämmer författaren mest
Fråga vad som är billigast för handlingen
Fråga vad som öppnar flest dörrar senare i boken
Låt två vägval ske samtidigt
Gör följden viktigare än händelsen
Fråga vad som gör personen begriplig utan att ursäkta det hen gör
Gå ut ur huvudpersonens huvud och se det utifrån
```

- [ ] **Steg 4: Skriv `src/bok/fron.py`**

```python
"""bok fron: slumpade frön till vägval, ur listor som följer med verktyget."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from bok.forlagor import forlagor
from bok.init import DATA
from bok.rot import BokFel, BokSaknas, find_root

FRON = DATA / "fron"
KLASSER = ("doman", "omvandning", "begransning", "process", "forlaga")
STANDARD = ("doman", "omvandning", "begransning")


class FronFel(BokFel):
    pass


def lista(klass: str) -> list[str]:
    """Fröna i en av paketets listor, utan tomma rader och kommentarer."""
    path = FRON / f"{klass}.txt"
    if klass == "forlaga" or not path.is_file():
        raise FronFel(f"Det finns ingen frölista för {klass}.")
    rader = (r.strip() for r in path.read_text(encoding="utf-8").splitlines())
    return [r for r in rader if r and not r.startswith("#")]


def _forlagefron(root: Path | None) -> list[str]:
    if root is None:
        return []
    return [f"{f['namn']} ({f['fil']})" for f in forlagor(root) if f["namn"]]


def _ordning(antal: int, klasser: list[str] | None, har_forlagor: bool, rng: random.Random) -> list[str]:
    if klasser:
        return [klasser[i % len(klasser)] for i in range(antal)]
    bas = list(STANDARD) + (["forlaga"] if har_forlagor else [])
    if antal <= len(bas):
        return bas[:antal]
    return bas + [rng.choice(STANDARD) for _ in range(antal - len(bas))]


def dra(antal: int = 4, klasser: list[str] | None = None, antaganden: list[str] | None = None,
        slump: int | None = None, root: Path | None = None) -> dict:
    """Dra frön. Samma slump, klasser, antaganden och förlagor ger samma frön."""
    if antal < 1:
        raise FronFel("--antal måste vara minst 1.")
    if slump is None:
        slump = random.SystemRandom().randrange(1, 100_000)
    rng = random.Random(slump)
    forlage = _forlagefron(root)
    kvar: dict[str, list[str]] = {}
    fron = []
    for klass in _ordning(antal, klasser, bool(forlage), rng):
        if klass not in kvar:
            kvar[klass] = list(forlage) if klass == "forlaga" else lista(klass)
        if not kvar[klass]:
            if klass == "forlaga" and not forlage:
                raise FronFel("Boken har inga förlagor med namn i bok/karaktarer/forlagor/.")
            raise FronFel(f"Det finns inte fler frön i klassen {klass}.")
        text = kvar[klass].pop(rng.randrange(len(kvar[klass])))
        antagande = rng.choice(antaganden) if klass == "omvandning" and antaganden else None
        fron.append({"klass": klass, "text": text, "antagande": antagande})
    return {"slump": slump, "fron": fron}


def _rad(f: dict, fet: bool = False) -> str:
    klass = f"**{f['klass']}**" if fet else f["klass"]
    rad = f"{klass}: {f['text']}"
    return rad + (f" (antagande: {f['antagande']})" if f["antagande"] else "")


def som_text(drag: dict) -> str:
    rader = [f"Slump {drag['slump']} (samma frön igen: --slump {drag['slump']})"]
    rader += [f"{i}. {_rad(f)}" for i, f in enumerate(drag["fron"], 1)]
    return "\n".join(rader)


def spara(mapp: Path, drag: dict) -> Path:
    """Lägg dragningen sist i MAPP/fron.md; tidigare dragningar i samma varv ligger kvar."""
    mapp.mkdir(parents=True, exist_ok=True)
    path = mapp / "fron.md"
    befintlig = path.read_text(encoding="utf-8") if path.is_file() else "# Frön\n"
    delar = [f"## Slump {drag['slump']}", ""] + [f"{i}. {_rad(f, fet=True)}" for i, f in enumerate(drag["fron"], 1)]
    path.write_text(befintlig.rstrip("\n") + "\n\n" + "\n".join(delar) + "\n", encoding="utf-8")
    return path


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("fron", help="slumpade frön till ett vägval")
    p.add_argument("--antal", type=int, default=4, help="hur många frön (standard: 4)")
    p.add_argument("--klass", action="append", choices=KLASSER, help="dra bara ur den här klassen; kan upprepas")
    p.add_argument("--antagande", action="append", default=[],
                   help="ett antagande som en omvändning kan gälla; kan upprepas")
    p.add_argument("--slump", type=int, help="samma tal ger samma frön")
    p.add_argument("--spara", metavar="MAPP", help="lägg dragningen sist i MAPP/fron.md")
    p.add_argument("--json", action="store_true", help="maskinläsbart, för skillen")
    p.set_defaults(func=_kor)


def _kor(args: argparse.Namespace) -> int:
    try:
        root = find_root()
    except BokSaknas:
        root = None
    drag = dra(args.antal, args.klass, args.antagande, args.slump, root)
    if args.spara:
        spara(Path(args.spara), drag)
    print(json.dumps(drag, ensure_ascii=False) if args.json else som_text(drag))
    return 0
```

- [ ] **Steg 5: Registrera kommandot i `src/bok/cli.py`**

Ersätt `_moduler`:

```python
def _moduler() -> list:
    from bok import annotations, forslag, fron, graf, init, mallar, rapport, status, tics, validera

    return [init, status, mallar, graf, tics, validera, fron, rapport, annotations, forslag]
```

- [ ] **Steg 6: Kör testerna**

Kör: `uv run pytest tests/test_fron.py tests/test_cli.py -q`
Förväntat: alla PASS.

- [ ] **Steg 7: Kontrollera att listorna följer med i paketet**

Kör: `uv build --wheel -o /tmp/bok-wheel && unzip -l /tmp/bok-wheel/bok-*.whl | grep fron/`
Förväntat: de fyra `.txt`-filerna under `bok/data/fron/`. Saknas de: lägg till `[tool.hatch.build.targets.wheel.force-include]` med `"src/bok/data/fron" = "bok/data/fron"` i `pyproject.toml` och bygg igen.

- [ ] **Steg 8: Commit**

```bash
git add src/bok/fron.py src/bok/data/fron src/bok/cli.py tests/test_fron.py
git commit -m "feat: bok fron drar slumpade frön till vägval"
```

---

### Uppgift 4: Bokens nya filer och den rikare karaktärsmallen

**Filer:**
- Ändra: `src/bok/data/bok/bok/karaktarer/MALL.md`, `src/bok/data/bok/bok/karaktarer/README.md`, `src/bok/data/bok/README.md`
- Skapa: `src/bok/data/bok/bok/karaktarer/forlagor/README.md`, `src/bok/data/bok/bok/karaktarer/forlagor/MALL.md`, `src/bok/data/bok/bok/karaktarer/prov/README.md`, `src/bok/data/bok/bok/vagval/README.md`
- Test: `tests/test_innehall.py`, `tests/test_status.py`, `tests/test_init.py`

**Gränssnitt:**
- Producerar: sökvägarna `bok/karaktarer/forlagor/`, `bok/karaktarer/forlagor/MALL.md`, `bok/karaktarer/prov/` och `bok/vagval/` finns i paketet, så att senare uppgifter får nämna dem i backticks.
- Producerar: rubrikerna `## Förlaga`, `## Motsägelser`, `## Självbild och andras bild`, `## Det hen döljer`, `## Under tryck`, `## Vardag`, `## Öppet` i karaktärsmallen.

- [ ] **Steg 1: Skriv de fallerande testerna**

Sist i `tests/test_innehall.py`:

```python
NYA_RUBRIKER = ("## Förlaga", "## Motsägelser", "## Självbild och andras bild", "## Det hen döljer",
                "## Under tryck", "## Vardag", "## Öppet")


def test_bokfiler_2_3():
    mall = (DATA / "bok/bok/karaktarer/MALL.md").read_text(encoding="utf-8")
    for rubrik in NYA_RUBRIKER:
        assert rubrik in mall, rubrik
    assert "{{" not in mall.split("## Förlaga", 1)[1], "de nya rubrikerna ska vara frivilliga"
    meta, _ = split((DATA / "bok/bok/karaktarer/forlagor/MALL.md").read_text(encoding="utf-8"))
    assert {"namn", "alias", "karaktarer"} <= set(meta)
    for rel in ("bok/bok/karaktarer/forlagor/README.md", "bok/bok/karaktarer/prov/README.md",
                "bok/bok/vagval/README.md"):
        assert (DATA / rel).is_file(), rel
    las_mig = (DATA / "bok/README.md").read_text(encoding="utf-8")
    assert "karaktärsverkstaden" in las_mig.lower() and "vägval" in las_mig.lower()
```

Sist i `tests/test_status.py` (lägg till `import re` överst om den saknas):

```python
def test_nya_rubriker_i_karaktarsmallen_ar_frivilliga(bok):
    fyll_forberedelse(bok)
    mall = (bok / "bok/karaktarer/MALL.md").read_text(encoding="utf-8")
    fylld = re.sub(r"\{\{[^}]*\}\}", "ifyllt", mall).replace("pov: ifyllt", "pov: true")
    skriv(bok, "bok/karaktarer/anna.md", fylld)
    assert compute(bok)["forberedelse"][1] == {"namn": "Karaktärer", "klar": True, "saknas": []}
```

Sist i `tests/test_init.py`:

```python
NYA_BOKFILER = ("bok/karaktarer/forlagor/README.md", "bok/karaktarer/forlagor/MALL.md",
                "bok/karaktarer/prov/README.md", "bok/vagval/README.md")


def test_uppgradering_skapar_nya_bokfiler_men_ror_inte_mallen(tmp_path):
    root = tmp_path / "bok"
    init_repo(root, titel="T", git=False)
    for rel in NYA_BOKFILER:
        (root / rel).unlink()
    (root / "bok/karaktarer/MALL.md").write_text("gammal mall\n", encoding="utf-8")
    init_repo(root, git=False)
    for rel in NYA_BOKFILER:
        assert (root / rel).is_file(), rel
    assert (root / "bok/karaktarer/MALL.md").read_text(encoding="utf-8") == "gammal mall\n"
```

- [ ] **Steg 2: Kör testerna och se dem falla**

Kör: `uv run pytest tests/test_innehall.py::test_bokfiler_2_3 tests/test_init.py::test_uppgradering_skapar_nya_bokfiler_men_ror_inte_mallen -q`
Förväntat: FAIL (rubrikerna och filerna saknas). `test_nya_rubriker_i_karaktarsmallen_ar_frivilliga` passerar redan med dagens mall; den skyddar mot att de nya rubrikerna får platshållare.

- [ ] **Steg 3: Skriv om `src/bok/data/bok/bok/karaktarer/MALL.md`**

````markdown
---
id: {{kort-id, t.ex. anna}}
namn: {{Fullständigt namn}}
pov: {{true om kapitel berättas genom personen, annars false}}
---

# {{Namn}}

## Kort
{{Vem är personen, i två meningar?}}

## Önskan
{{Vad vill personen mest av allt, medvetet?}}

## Rädsla
{{Vad är personen mest rädd för?}}

## Blind fläck
{{Vad ser personen inte hos sig själv, som läsaren kan se?}}

## Språklig signatur
{{Hur pratar och tänker personen? Ordval, rytm, vad personen aldrig skulle säga.}}

## Båge
{{Var börjar personen, vad tvingar fram en förändring, var slutar hen?}}

## Relationer
{{De viktigaste relationerna och vad som står på spel i dem.}}

## Förlaga
<!-- Bygger personen på en verklig person: länk till förlagan i bok/karaktarer/forlagor/ och vilken spänning som lånas, till exempel "vänlig och omöjlig att rubba". Ingen biografi. -->

## Motsägelser
<!-- Två eller tre egenskaper som drar åt olika håll. -->

## Självbild och andras bild
<!-- Hur personen ser sig själv, hur omgivningen ser hen, och glappet mellan dem. -->

## Det hen döljer
<!-- Vad, för vem och varför. -->

## Under tryck
<!-- Vad personen gör, säger och undviker när önskan och rädsla krockar. Beteende, inte egenskaper. -->

## Vardag
<!-- Humor, smak, vanor: det som gör personen till mer än sin funktion i handlingen. -->

## Öppet
<!-- Idéer om personen som inte är beslutade. Allt ovanför den här rubriken är beslutat. -->
````

- [ ] **Steg 4: Lägg till i `src/bok/data/bok/bok/karaktarer/README.md`**

Lägg sist i filen (behåll allt som står där, också meningen om `fodd`):

```markdown

Rubrikerna från Förlaga och nedåt är frivilliga men gör personen levande: motsägelser, självbild och andras bild, det hen döljer, beteende under tryck och vardag. Allt ovanför Öppet är beslutat. Datum och godkännanden skrivs i `bok/beslut.md`, inte här.

`forlagor/` har verkliga personer som en karaktär bygger på, och `prov/` karaktärsverkstadens provscener. Ingen av dem räknas som karaktärer.
```

- [ ] **Steg 5: Skapa `src/bok/data/bok/bok/karaktarer/forlagor/README.md`**

```markdown
# Förlagor

Verkliga personer som en karaktär bygger på. En fil per person, `<kort-namn>.md`, kopierad från `MALL.md`. Researcher skriver dem med uppdraget porträtt, ur offentliga intervjuer och porträtt.

Det som lånas är en spänning mellan egenskaper, aldrig en biografi. Writer läser inte filerna här; vad karaktären lånar står i `bok/karaktarer/<id>.md`.

`bok validate` stoppar kapitel där en förlagas namn eller alias står. Ska personen förekomma i boken som sig själv: skriv namnet under kända namn i `bok/canon.md`. Finns det förlagor läser sensitivitetsläsaren planen innan första kapitlet.
```

- [ ] **Steg 6: Skapa `src/bok/data/bok/bok/karaktarer/forlagor/MALL.md`**

```markdown
---
namn: {{Personens namn, som det skrivs}}
alias: []
karaktarer: [{{id för karaktären som lånar}}]
---

# {{Namn}}: förlaga

Underlag för en karaktär, inte fakta i boken och inte en bedömning av personen.

## Uppdraget
{{Vilken karaktär, vad författaren vill låna och varför.}}

## Underlaget
{{Vad materialet består av, vad det inte ger tillgång till och vems perspektiv som saknas.}}

## Självbild
{{Vad personen säger om sig själv. En punkt per uppgift, med källa och datum.}}

## Andras bild
{{En punkt per iakttagelse: vem, relation till personen, förstahand eller återberättat, källa och datum.}}

## Motsägelser och spänningar
{{Egenskaper som drar åt olika håll, med belägg.}}

## Röst i intervjuer
{{Ordval, rytm och vad personen undviker. Bara korta citat.}}

## Spärrar
{{Det som inte får lånas eller påstås: diagnoser, privat hälsa, brott, närstående.}}

## Litterär tolkning
{{Förslag till karaktären. Förslag, inte fakta om personen.}}
```

- [ ] **Steg 7: Skapa `src/bok/data/bok/bok/karaktarer/prov/README.md`**

```markdown
# Provscener

Karaktärsverkstadens tryckprov: korta scener utanför bokens handling där en person sätts under tryck. En mapp per person, `<id>/`. Underlag, inte manus: inget härifrån kopieras in i kapitlen.
```

- [ ] **Steg 8: Skapa `src/bok/data/bok/bok/vagval/README.md`**

```markdown
# Vägval

Bokens idébank. Ett varv per mapp, `ÅÅÅÅ-MM-DD-<kort-namn>/`:

| Fil | Innehåll |
|---|---|
| `ram.md` | frågan, det som måste hålla, vad som gör ett vägval bra, antagandena |
| `uppenbart.md` | det som de flesta skulle komma på |
| `fron.md` | fröna, med slumptalet så att dragningen går att upprepa |
| `ideer.md` | vägvalen, numrerade `v1`, `v2` … med fröet som ursprung |
| `karta.md` | riktningarna och kritikerns anteckningar |
| `val.md` | vad du valde och vart det tog vägen |

Vägval som inte valdes ligger kvar och kan väckas i ett senare varv.
```

- [ ] **Steg 9: Lägg till i `src/bok/data/bok/README.md`**

Lägg till två punkter i listan under "Kom igång", efter punkten om tonen:

```markdown
- **"Den här personen känns platt."** Karaktärsverkstaden: Claude provskriver korta scener där personen sätts under tryck, och du säger vad som stämmer. Du kan också peka ut en verklig person som förlaga; då tas ett porträtt fram ur intervjuer och ur vad andra säger om personen.
- **"Ge mig vägval."** När du inte vet hur något ska gå: flera roller tar fram alternativ från olika håll, och du väljer.
```

- [ ] **Steg 10: Kör testerna**

Kör: `uv run pytest -q`
Förväntat: alla PASS.

- [ ] **Steg 11: Commit**

```bash
git add src/bok/data/bok tests/test_innehall.py tests/test_status.py tests/test_init.py
git commit -m "feat: karaktärsmallen får motsägelser, under tryck och förlaga; mappar för förlagor, prov och vägval"
```

---

### Uppgift 5: Hantverket för karaktärer, skillen, processen och verktygen

**Filer:**
- Skapa: `src/bok/data/genererat/claude/bok/hantverk/karaktarer.md`
- Ändra: `src/bok/data/genererat/claude/skills/bok/SKILL.md`, `src/bok/data/genererat/claude/bok/process.md`, `src/bok/data/genererat/claude/bok/verktyg.md`
- Test: `tests/test_innehall.py`

**Gränssnitt:**
- Konsumerar: `bok fron` (uppgift 3), sökvägarna från uppgift 4.
- Producerar: `.claude/bok/hantverk/karaktarer.md` (som rollerna i uppgift 6 och 7 hänvisar till); skillen nämner `bok-vagval` och `bok-idekritiker`, så att `test_skillen` passerar när rollerna läggs till i uppgift 6.

- [ ] **Steg 1: Skriv de fallerande testerna**

Sist i `tests/test_innehall.py`:

```python
def test_skillen_2_3():
    text = _las("skills/bok/SKILL.md")
    for fras in ("## Karaktärsverkstaden", "## Vägval", "uppdraget **porträtt**", "uppdraget **tryckprov**",
                 "bok fron --json", "bok-vagval", "bok-idekritiker", "Välj aldrig åt henne",
                 "`.claude/bok/hantverk/karaktarer.md`", "Ge aldrig `bok-writer` en förlaga"):
        assert fras in text, fras


def test_process_verktyg_och_hantverk_2_3():
    process = _las("bok/process.md")
    for fras in ("## Karaktärer och förlagor", "## Vägval", "Writer läser aldrig förlagor",
                 "Verkliga händelser och personer", "| Vägval |", "| Idékritiker |"):
        assert fras in process, fras
    verktyg = _las("bok/verktyg.md")
    assert "`bok fron" in verktyg and "förlagornas namn" in verktyg
    hantverk = _las("bok/hantverk/karaktarer.md")
    for fras in ("## Förlagor", "## Tryckprov", "Under tryck", "Öppet", "`bok/beslut.md`"):
        assert fras in hantverk, fras


def test_ramverkets_kommandon_finns():
    from bok.cli import build_parser

    sub = next(a for a in build_parser()._actions if isinstance(a, argparse._SubParsersAction))
    text = "".join(_las(r) for r in ("skills/bok/SKILL.md", "bok/process.md", "bok/verktyg.md"))
    for kommando in set(re.findall(r"`bok ([a-z]+)", text)):
        assert kommando in sub.choices, kommando
```

Lägg till `import argparse` överst i `tests/test_innehall.py`.

- [ ] **Steg 2: Kör testerna och se dem falla**

Kör: `uv run pytest tests/test_innehall.py -q -k "2_3 or kommandon"`
Förväntat: `test_skillen_2_3` och `test_process_verktyg_och_hantverk_2_3` FAIL; `test_ramverkets_kommandon_finns` PASS (bok fron finns redan).

- [ ] **Steg 3: Skapa `src/bok/data/genererat/claude/bok/hantverk/karaktarer.md`**

```markdown
# Karaktärer

Hur en person i boken blir mer än sin funktion i handlingen. Skillen, Writer, Plot-arkitekten och Redaktören utgår från den här filen.

## Rubrikerna i karaktärsfilen

| Rubrik | Vad som står där |
|---|---|
| Kort, Önskan, Rädsla, Blind fläck, Språklig signatur, Båge, Relationer | grunden; måste vara ifylld för POV-personer innan första kapitlet |
| Förlaga | vilken verklig person personen bygger på och vilken spänning som lånas, aldrig en biografi |
| Motsägelser | två eller tre egenskaper som drar åt olika håll |
| Självbild och andras bild | hur personen ser sig själv, hur omgivningen ser hen, och glappet |
| Det hen döljer | vad, för vem och varför |
| Under tryck | vad personen gör, säger och undviker när önskan och rädsla krockar |
| Vardag | humor, smak, vanor |
| Öppet | idéer om personen som inte är beslutade |

Allt ovanför Öppet är beslutat. Datum, godkännanden och hur något kom fram skrivs i `bok/beslut.md`, inte i karaktärsfilen. En rubrik där bara kommentaren står kvar är inte ifylld än. Saknas rubrikerna i en äldre bok: lägg till dem när karaktärsverkstaden körs för personen.

## Komplexitet

- **Motsägelser som finns samtidigt.** Vänligheten är inte en mask som faller; den finns kvar medan personen gör andra illa. Två sanna saker samtidigt, inte en avslöjad sanning.
- **Beteende, inte egenskaper.** "Hon är envis" går inte att skriva. "Hon lyssnar färdigt, nickar och gör sedan som hon hade tänkt" går att skriva.
- **Glappet mellan självbild och andras bild** är där läsaren kommer före personen.
- **Under tryck** visar vem personen är. Önskan och rädsla som krockar ger ett val, och valet ger scenen.
- **Vardagen** gör personen igenkännbar: vad hen skrattar åt, vad hen gör en vanlig tisdag.
- **Moraliska val är val.** Förklara aldrig en handling med en diagnos, en uppväxt eller en egenskap så att personen slipper ansvar.

## Förlagor

- En förlaga är en verklig person vars offentliga porträtt ger råmaterial. Det som lånas är en spänning mellan egenskaper, aldrig en biografi, händelser ur personens liv eller detaljer som gör hen igenkännbar.
- Förlagan ligger i `bok/karaktarer/forlagor/`. Karaktärsfilen säger under Förlaga vad som lånas. Writer läser bara karaktärsfilen.
- Tillskriv aldrig förlagan diagnoser, sjukdomar eller brott. Ska karaktären ha en diagnos är det ett eget beslut som researchas för sig, med förstahandsberättelser, och diagnosen får inte bli en förklaring till det personen gör.

## Tryckprov

Tre scener på cirka 200 ord, utanför bokens handling:

1. Personen har fel inför andra.
2. Någon ber om något som personen inte vill ge.
3. En vanlig dag.

Scenerna visar beteende, inte egenskaper, och följer bokens röst. De är underlag och kopieras aldrig in i kapitlen.
```

- [ ] **Steg 4: Ändra skillen `src/bok/data/genererat/claude/skills/bok/SKILL.md`**

4a. I tabellen under "Fritt samtal", ersätt raden

```
  | en person | `bok/karaktarer/<id>.md` (kopiera `bok/karaktarer/MALL.md`) |
```

med

```
  | en person | `bok/karaktarer/<id>.md` (kopiera `bok/karaktarer/MALL.md`; rubrikerna förklaras i `.claude/bok/hantverk/karaktarer.md`) |
  | en verklig person som en karaktär ska bygga på | Karaktärsverkstaden nedan, med en förlaga |
  | en person som känns platt, "hur skulle hon reagera?" | Karaktärsverkstaden nedan |
  | flera möjliga vägar, "jag vet inte hur det ska gå" | föreslå Vägval nedan |
```

4b. Lägg till två avsnitt direkt före `## Innan första kapitlet`:

````markdown
## Karaktärsverkstaden
En person blir levande när hen gör något under tryck. Kör verkstaden när hon pekar ut en verklig person som förlaga, när en person känns platt, eller när `bok-plot-arkitekt` föreslår det. Rubrikerna och reglerna står i `.claude/bok/hantverk/karaktarer.md`.

1. **Förlaga** (när hon pekar ut en verklig person). Starta `bok-researcher` med uppdraget **porträtt**: personen, karaktären och vad hon vill låna. Visa vad underlaget räcker till och den starkaste spänningen. Förlagan sparas i `bok/karaktarer/forlagor/`.
2. **Kärna.** Föreslå personens kärna som en spänning mellan egenskaper ("omtänksam och allt svårare att rubba"), utifrån förlagan och det hon berättat. Är hon osäker: föreslå vägval ("tre olika sätt att låna förlagan").
3. **Tryckprov.** Starta `bok-writer` med uppdraget **tryckprov** för personen. Visa de tre scenerna.
4. **Läsning.** Låt henne säga vad som stämmer, vad som skaver och vad läsaren ska känna för personen. Skriv om en scen i taget med `bok-writer` tills hon känner igen personen.
5. **In i filen.** Skriv in det valda under rätt rubriker i `bok/karaktarer/<id>.md`; saknas de nya rubrikerna, lägg till dem. Idéer som inte är beslutade hamnar under Öppet. Skriv en rad med datum i `bok/beslut.md`.

Provscenerna är underlag. Kopiera aldrig in dem i kapitlen.

## Vägval
För frågor där det finns flera möjliga vägar och den första idén inte räcker. Kör när hon ber om det ("ge mig vägval", "fler idéer", "jag vet inte hur hon ska …"). Föreslå det, men starta det aldrig utan hennes ja, vid premissen, en persons kärna, bågarnas vändpunkter (inciting incident, mittpunkt, klimax) och när `bok-plot-arkitekt` ser flera möjliga vägar i ett scenkort. Säg att ett varv tar några minuter.

1. **Ram.** Formulera frågan som ett problem, inte en lösning ("hur korsar hon gränsen första gången?"). Hämta det som måste hålla ur premissen, `bok/canon.md`, karaktärsfilerna och `bok/plot/bagar.md`, och visa det i stället för att fråga. Fråga vad som gör ett vägval bra för henne. Lista 3–5 tysta antaganden om lösningen ("det sker i en scen", "hon gör det ensam"). Sök i `bok/vagval/` efter tidigare varv om samma sak och nämn dem. Visa ramen och få hennes ja. Skriv den i `bok/vagval/<ÅÅÅÅ-MM-DD>-<kort-namn>/ram.md`.
2. **Det uppenbara.** Starta `bok-vagval` med uppdraget **uppenbart** och ramen. Spara svaret i `uppenbart.md` i varvets mapp. Ge det aldrig till grenarna.
3. **Frön.** Kör `bok fron --json --spara bok/vagval/<mapp>` med ett `--antagande "…"` per antagande i ramen.
4. **Grenar.** Starta fyra `bok-vagval` parallellt med uppdraget **gren**; var och en får ramen och ett frö. Numrera vägvalen `v1`, `v2` … i den ordning de kommer och spara dem i `ideer.md` med fröet som ursprung.
5. **Kritik.** Starta `bok-idekritiker` med varvets mapp. Spara svaret i `karta.md`.
6. **Karta.** Visa riktningarna: namn och kärna, och under varje riktning vägvalens id, rubrik och mening, med värde, rimlighet och djävulens advokat i korthet. Visa sist det uppenbara på en rad: det får också vinna. Rekommendera inget.
7. **Välj och styr.** Hon väljer ett till tre vägval och säger åt vilket håll. Starta `bok-vagval` med uppdraget **utveckla** och sedan `bok-idekritiker` igen, och visa kartan. Har varvet fastnat: dra ett processfrö med `bok fron --klass process --antal 1 --spara bok/vagval/<mapp>` och ge det till `bok-vagval`. Högst två utvecklingsvarv; sedan bestämmer hon.
8. **Beslut.** Skriv in det hon väljer där det hör hemma, efter hennes ja. Skriv i `val.md` vad hon valde och vart det tog vägen, och en rad i `bok/beslut.md` med länk till varvets mapp. Väljer hon inget: skriv det i `val.md`.

Hon väljer alltid. Välj aldrig åt henne.
````

4c. Under "Innan första kapitlet", ersätt meningen

```
**Verkliga händelser.** Säger `bok status` att verkliga händelser behöver granskas (`Förberedelse: Verkliga händelser – …`): starta `bok-sensitivitet` för planen (uppdraget planen) och spara rapporten med `bok rapport spara -`.
```

med

```
**Verkliga personer och händelser.** Säger `bok status` att verkliga händelser behöver granskas, eller verkliga personer när boken har förlagor (`Förberedelse: Verkliga …`): starta `bok-sensitivitet` för planen (uppdraget planen) och spara rapporten med `bok rapport spara -`.
```

(Resten av stycket, från "Vid `atgarda`", står kvar.)

4d. Lägg till sist i listan under `## Gör inte`:

```
- Ge aldrig `bok-writer` en förlaga. Writer arbetar från karaktärsfilen.
```

- [ ] **Steg 5: Ändra `src/bok/data/genererat/claude/bok/process.md`**

5a. I förberedelsetabellen, ersätt raden som börjar `| Verkliga händelser |` med

```
| Verkliga händelser och personer | blocket `verkliga-handelser` i `bok/canon.md`, förlagor i `bok/karaktarer/forlagor/` | bara om blocket har rader eller boken har förlagor: rapport `omfang: forberedelse`, `roll: sensitivitet`, `utfall: godkand` |
```

5b. Ersätt meningen `` `bok status` ser bara om filerna är ifyllda. Om innehållet håller bedömer `bok-plot-arkitekt` (uppdrag *grind*).`` med

```
`bok status` ser bara om filerna är ifyllda. Om innehållet håller bedömer `bok-plot-arkitekt` (uppdrag *grind*), också om POV-personerna har motsägelser och ett konkret beteende under tryck (se `.claude/bok/hantverk/karaktarer.md`).
```

5c. I tabellen "Vad rollerna läser": lägg till `, aldrig `bok/karaktarer/forlagor/`` sist i Writer-raden, och lägg till två rader sist i tabellen:

```
| Vägval | det uppdraget anger: varvets `ram.md`, fröet eller de valda vägvalen; aldrig `uppenbart.md` som gren |
| Idékritiker | varvets `ram.md`, `uppenbart.md` och `ideer.md` |
```

5d. Lägg till två avsnitt direkt efter avsnittet `## Tid`:

```markdown
## Karaktärer och förlagor

Karaktärsfilens rubriker står i `.claude/bok/hantverk/karaktarer.md`. Allt ovanför Öppet är beslutat; datum och godkännanden skrivs i `bok/beslut.md`.

En förlaga är en verklig person som en karaktär bygger på, i `bok/karaktarer/forlagor/`. `bok-researcher` skriver den med uppdraget *porträtt*. Writer läser aldrig förlagor. `bok validate` stoppar kapitel där en förlagas namn eller alias står, utom namn som står bland kända namn i `bok/canon.md`. Finns det förlagor läser `bok-sensitivitet` planen innan första kapitlet.

Karaktärsverkstaden prövar en person i tre korta scener utanför handlingen (`bok-writer`, uppdraget *tryckprov*), sparade i `bok/karaktarer/prov/`.

## Vägval

Ett vägvalsvarv ger 4–6 distinkta riktningar för en fråga där den första idén inte räcker. Skillen ramar in frågan med författaren, `bok-vagval` listar det uppenbara i egen kontext, `bok fron` drar frön, fyra `bok-vagval` tar ett frö var, och `bok-idekritiker` sållar och grupperar. Grenarna ser aldrig det uppenbara. Kritikern ger inga betyg och rekommenderar inget; författaren väljer. Varvet sparas i `bok/vagval/`.
```

- [ ] **Steg 6: Ändra `src/bok/data/genererat/claude/bok/verktyg.md`**

Ersätt raden som börjar `` | `bok validate manuskript/kapitel-NN.md` | `` med

```
| `bok validate manuskript/kapitel-NN.md` | förbjudna namn, förlagornas namn och tidsfel i grafen stoppar (exitkod 1); namn som saknas i grafen och åldrar som inte stämmer är varningar |
```

och lägg till direkt efter den:

```
| `bok fron [--antal N] [--klass KLASS] [--antagande TEXT] [--slump TAL] [--spara MAPP]` | slumpade frön till ett vägval (`--json` för skillen); klasserna är doman, omvandning, begransning, process och forlaga |
```

- [ ] **Steg 7: Kör testerna**

Kör: `uv run pytest -q`
Förväntat: alla PASS. Faller `test_inga_dinglande_sokvagar`: en sökväg i backticks finns inte i paketet; rätta stavningen eller lägg `<…>` runt variabeldelen.

- [ ] **Steg 8: Commit**

```bash
git add src/bok/data/genererat tests/test_innehall.py
git commit -m "feat: karaktärsverkstad och vägval i skillen och processen"
```

---

### Uppgift 6: Rollerna Vägval och Idékritiker

**Filer:**
- Skapa: `src/bok/data/genererat/claude/agents/bok-vagval.md`, `src/bok/data/genererat/claude/agents/bok-idekritiker.md`
- Test: `tests/test_innehall.py` (`ROLLER` och nytt test)

**Gränssnitt:**
- Konsumerar: skillens avsnitt Vägval (uppgift 5) som anropar uppdragen *uppenbart*, *gren*, *utveckla* och *kritik*.
- Producerar: kartans format (`## Strukna`, `## Riktning: …`, `### vN Rubrik` med `**Värde:**`, `**Rimlighet:**`, `**Djävulens advokat:**`).

- [ ] **Steg 1: Skriv de fallerande testerna**

I `tests/test_innehall.py`, ersätt `ROLLER` med

```python
ROLLER = {"plot-arkitekt", "writer", "redaktor", "sprakgranskare", "kontinuitet", "forlaggare",
          "researcher", "varldsbyggare", "sensitivitet", "audiobook", "marknad", "vagval", "idekritiker"}
```

och lägg till sist:

```python
def test_vagvalsrollerna():
    vagval = _las("agents/bok-vagval.md")
    for fras in ("## Uppdrag: uppenbart", "## Uppdrag: gren", "## Uppdrag: utveckla",
                 "Läs aldrig `uppenbart.md`", "utvecklar v3"):
        assert fras in vagval, fras
    kritik = _las("agents/bok-idekritiker.md")
    for fras in ("## Uppdrag: kritik", "**Värde:**", "**Rimlighet:**", "**Djävulens advokat:**",
                 "## Strukna", "Inga betyg"):
        assert fras in kritik, fras
    for text in (vagval, kritik):
        meta, _ = split(text)
        assert not {v.strip() for v in meta["tools"].split(",")} & {"Write", "Edit", "Bash"}
```

- [ ] **Steg 2: Kör testerna och se dem falla**

Kör: `uv run pytest tests/test_innehall.py -q -k "roller or vagvalsrollerna"`
Förväntat: `test_alla_roller_finns` och `test_vagvalsrollerna` FAIL.

- [ ] **Steg 3: Skapa `src/bok/data/genererat/claude/agents/bok-vagval.md`**

````markdown
---
name: bok-vagval
description: Tar fram vägval för en fråga i boken: det uppenbara, en gren ur ett frö, eller en utveckling av vägval som författaren valt. Används i vägvalsvarvet, flera parallellt med varsitt frö.
tools: Read, Glob, Grep
model: inherit
---

# Vägval

Du tar fram konkreta vägval för en fråga i boken. Du skriver inga filer; skillen sparar det du returnerar.

## Läs först
1. `bok/roller/vagval.local.md` om den finns. Den går före allt nedan.
2. Det uppdraget ger dig, och de filer i `bok/` som ramen hänvisar till. Inget annat ur varvets mapp.

## Uppdrag: uppenbart
Du får ramen. Lista de 8–10 vägval som de flesta författare och läsare skulle komma på först. Var ärlig; här är det uppenbara rätt svar. Returnera en numrerad lista, en rad per vägval.

## Uppdrag: gren
Du får ramen och ett frö. Läs aldrig `uppenbart.md`.
1. Säg först kopplingen: vad i fröet motsvarar något i frågan, och varför. Två eller tre meningar. Är fröet en omvändning med ett antagande: vänd just det antagandet. Är fröet en förlaga: läs förlagan och låna en spänning, aldrig en händelse ur personens liv.
2. Ge 2–3 vägval som växer ur kopplingen. De ska skilja sig från varandra.
3. Håll dig inom det som måste hålla i ramen. Fröet styr vinkeln, inte reglerna.

Varje vägval i den här formen:

```
### Rubrik
En mening om vad som händer.
**Scenen:** hur det ser ut när det skrivs: plats, vem, vad som syns och hörs.
**I planen:** vad det ändrar eller kräver av personerna, bågarna och kommande kapitel.
```

## Uppdrag: utveckla
Du får ramen, de valda vägvalen och författarens riktning ("mörkare", "kombinera v3 och v7"). Läs aldrig `uppenbart.md`. Kombinera, förenkla eller ändra en aspekt. Ge 2–4 nya vägval i samma form, och skriv på raden under rubriken vilket vägval det utvecklar, till exempel "utvecklar v3". Har du fått ett processfrö: arbeta som det säger.

## Regler
- Konkret före abstrakt: varje vägval ska gå att se som en scen.
- Ingen rangordning, inga betyg, ingen rekommendation.
- Vägval som rör en förlaga följer spärrarna i förlagan.

## Det du returnerar
Bara listan eller vägvalen, utan inledning.
````

- [ ] **Steg 4: Skapa `src/bok/data/genererat/claude/agents/bok-idekritiker.md`**

````markdown
---
name: bok-idekritiker
description: Kritiserar vägvalen i ett vägvalsvarv: sållar bort det uppenbara och det som bryter mot boken, skriver värde, rimlighet och djävulens advokat per vägval och grupperar dem i riktningar. Används efter grenarna och efter varje utvecklingsvarv.
tools: Read, Glob, Grep
model: inherit
---

# Idékritiker

Du hjälper författaren att se vägvalen klart. Du väljer inte åt henne.

## Läs först
1. `bok/roller/idekritiker.local.md` om den finns. Den går före allt nedan.
2. Varvets `ram.md`, `uppenbart.md` och `ideer.md`, och de filer i `bok/` som ramen hänvisar till.

## Uppdrag: kritik
1. **Det uppenbara.** Stryk vägval som i sak är något på `uppenbart.md`, även med andra ord. Ange vilket.
2. **Det som måste hålla.** Stryk vägval som bryter mot det som måste hålla i ramen. Ange vad de bryter mot.
3. **Tre anteckningar per vägval som är kvar**, var för sig och i den här ordningen:
   - **Värde:** vad som är bra och vad det öppnar för boken. Skriv den först och på allvar; ett ovanligt vägval stryks inte för att det är ovanligt.
   - **Rimlighet:** håller det mot personerna, canon och premissen? Vad skulle behöva vara sant?
   - **Djävulens advokat:** det starkaste skälet att avstå.
4. **Riktningar.** Gruppera vägvalen i 4–6 riktningar som skiljer sig i sak, inte bara i ton. Varje riktning får ett namn och en mening om kärnan.

Efter ett utvecklingsvarv: gör samma sak med de nya vägvalen och lägg dem i befintliga eller nya riktningar.

## Regler
- Inga betyg, ingen rangordning, ingen sammanvägning, ingen rekommendation.
- Kombinationer ska fungera i boken, inte bara vara fyndiga.

## Det du returnerar
Kartan, i den här formen:

```
## Strukna
- v4: samma som uppenbart nr 2
- v9: bryter mot …

## Riktning: Namn
Kärnan i en mening.

### v3 Rubrik
**Värde:** …
**Rimlighet:** …
**Djävulens advokat:** …
```
````

- [ ] **Steg 5: Kör testerna**

Kör: `uv run pytest -q`
Förväntat: alla PASS, också `test_agentfil[bok-vagval]`, `test_agentfil[bok-idekritiker]` och `test_skillen`.

- [ ] **Steg 6: Commit**

```bash
git add src/bok/data/genererat/claude/agents/bok-vagval.md src/bok/data/genererat/claude/agents/bok-idekritiker.md tests/test_innehall.py
git commit -m "feat: rollerna Vägval och Idékritiker"
```

---

### Uppgift 7: Researcher, Writer, Plot-arkitekt, Sensitivitet och Redaktör

**Filer:**
- Ändra: `src/bok/data/genererat/claude/agents/bok-researcher.md`, `bok-writer.md`, `bok-plot-arkitekt.md`, `bok-sensitivitet.md`, `bok-redaktor.md`
- Test: `tests/test_innehall.py`

**Gränssnitt:**
- Konsumerar: `bok/karaktarer/forlagor/MALL.md` (uppgift 4), `.claude/bok/hantverk/karaktarer.md` (uppgift 5), uppdragsnamnen *porträtt* och *tryckprov* som skillen använder (uppgift 5).

- [ ] **Steg 1: Skriv det fallerande testet**

Sist i `tests/test_innehall.py`:

```python
def test_roller_2_3():
    res = _las("agents/bok-researcher.md")
    for fras in ("## Uppdrag: porträtt", "`bok/karaktarer/forlagor/MALL.md`", "förstahand eller återberättat",
                 "diagnoser"):
        assert fras in res, fras
    writer = _las("agents/bok-writer.md")
    assert "## Uppdrag: tryckprov" in writer and "Läs inte `bok/karaktarer/forlagor/`" in writer
    plot = _las("agents/bok-plot-arkitekt.md")
    assert "under tryck" in plot and "vägval" in plot
    sens = _las("agents/bok-sensitivitet.md")
    assert "`bok/karaktarer/forlagor/`" in sens and "igenkännbar" in sens
    red = _las("agents/bok-redaktor.md")
    assert "`.claude/bok/hantverk/karaktarer.md`" in red and "under tryck" in red
```

- [ ] **Steg 2: Kör testet och se det falla**

Kör: `uv run pytest tests/test_innehall.py::test_roller_2_3 -q`
Förväntat: FAIL på första frasen.

- [ ] **Steg 3: Researcher**

Lägg till sist i `bok-researcher.md`:

```markdown

## Uppdrag: porträtt
Du får en verklig person, karaktären som ska bygga på personen och vad författaren vill låna.
1. Läs karaktärsfilen i `bok/karaktarer/` och `.claude/bok/hantverk/karaktarer.md`.
2. Sök porträtt, reportage och intervjuer med hög trovärdighet. Prioritera texter där andra än personen själv kommer till tals: kollegor, tidigare chefer, kritiker, journalister som har träffat personen.
3. Kopiera `bok/karaktarer/forlagor/MALL.md` till `bok/karaktarer/forlagor/<kort-namn>.md` och fyll i den. Varje iakttagelse får vem som säger det, relationen till personen, förstahand eller återberättat, källa och datum. Skilj på det reportern såg, det andra berättar och det personen själv har berättat för någon annan.
4. Väg perspektiven: nuvarande medarbetare, tidigare chefer och kritiker har var sina skäl.
5. Tillskriv aldrig personen diagnoser, sjukdomar eller brott, och spekulera inte om privatlivet eller närstående. Skriv vad underlaget inte ger tillgång till.
6. Under Litterär tolkning: förslag till karaktären, formulerade som spänningar mellan egenskaper. Skriv inte i karaktärsfilen.

Returnera högst tio rader: vad underlaget räcker till, den starkaste spänningen och förslag till karaktären.
```

- [ ] **Steg 4: Writer**

I `bok-writer.md`, ersätt raden `Läs inte `bok/stil/exempel/`. Återge aldrig formuleringar ur andras texter.` med

```
Läs inte `bok/stil/exempel/`. Återge aldrig formuleringar ur andras texter.
Läs inte `bok/karaktarer/forlagor/`. Vad en person lånar av en förlaga står i karaktärsfilen.
```

och lägg till direkt före `## Innan du lämnar`:

```markdown
## Uppdrag: tryckprov
Karaktärsverkstaden. Du får en person (`id`) och skriver inget i manuset.
1. Läs `bok/karaktarer/<id>.md`, `bok/stil/rost.md` (och `bok/stil/rost-<id>.md` om den finns), `bok/koncept/premiss.md` och `.claude/bok/hantverk/karaktarer.md`.
2. Skriv tre scener på cirka 200 ord var, utanför bokens handling: personen har fel inför andra; någon ber om något som personen inte vill ge; en vanlig dag. Visa beteende, inte egenskaper.
3. Spara dem som `1-fel.md`, `2-nej.md` och `3-vardag.md` i `bok/karaktarer/prov/<id>/`. Skriver du om en scen: skriv över filen.

Returnera högst sex rader: vad varje scen prövar och vad du är osäker på hos personen.
```

- [ ] **Steg 5: Plot-arkitekt**

I `bok-plot-arkitekt.md`, ersätt punkten som börjar `- I.1: kan du för varje POV-karaktär` med

```
- I.1: kan du för varje POV-karaktär säga önskan, rädsla, blind fläck och språklig signatur, så att de driver handling? Är de olika varandra? Har de motsägelser och ett konkret beteende under tryck (se `.claude/bok/hantverk/karaktarer.md`)? Saknas det: föreslå karaktärsverkstaden under Förslag.
```

och lägg till sist i avsnittet `## Uppdrag: scenkort`:

```
Ser du flera möjliga vägar för en scen och ingen är självklar: skriv scenkortet med den du tror mest på, och säg i ditt svar vilka vägar du såg och att vägval kan vara värt det.
```

- [ ] **Steg 6: Sensitivitet**

I `bok-sensitivitet.md`, under `## Uppdrag: planen`, ersätt punkt 1 och 2 med

```
1. Läs `bok/koncept/`, `bok/karaktarer/`, `bok/plot/struktur.md`, `bok/plot/bagar.md`, `bok/plot/kapitelplan.md`, `bok/plot/tidslinje.md` (om den finns), blocket `verkliga-handelser` i `bok/canon.md` och alla förlagor i `bok/karaktarer/forlagor/`.
2. Bedöm: levande personer, risk för förtal, respekt för offer och anhöriga, fakta om händelserna. För förlagor: blir karaktären igenkännbar som den verkliga personen på ett sätt som kan läsas som påståenden om hen? Lånar boken spänningar eller biografi? Tillskrivs personen något som förlagans spärrar utesluter?
```

(Rapportformatet under punkterna står kvar. Orden `tidslinje.md` och `kapitelplan.md` måste finnas kvar; `test_slutgranskningens_rattningar` kontrollerar dem.)

- [ ] **Steg 7: Redaktör**

I `bok-redaktor.md`, ersätt punkt 5 under `## Läs först` med

```
5. `bok/koncept/premiss.md`, `bok/koncept/genre.md`, `bok/koncept/teman.md`, `bok/plot/bagar.md`, `bok/canon.md`, karaktärsfilerna för kapitlets personer och `.claude/bok/hantverk/karaktarer.md`.
```

och punkten `- **karaktar:** …` med

```
- **karaktar:** handlar personerna utifrån sin önskan, rädsla och blinda fläck, och beter de sig som karaktärsfilen säger under tryck? Får motsägelserna finnas samtidigt? Håller POV?
```

- [ ] **Steg 8: Kör testerna**

Kör: `uv run pytest -q`
Förväntat: alla PASS.

- [ ] **Steg 9: Commit**

```bash
git add src/bok/data/genererat/claude/agents tests/test_innehall.py
git commit -m "feat: porträtt, tryckprov och komplexa karaktärer i rollerna"
```

---

### Uppgift 8: Dokumentation och changelog

**Filer:**
- Ändra: `docs/hur-det-fungerar.md`, `README.md`, `CHANGELOG.md`
- Test: `tests/test_changelog.py`, `tests/test_innehall.py::test_readme_utan_arv` (befintliga)

- [ ] **Steg 1: `docs/hur-det-fungerar.md`**

1a. I tabellen "Vad som finns i en bok", ersätt `` | `bok/` | planen och minnet: idén, personerna, handlingen, rösten, världen, besluten, sammanfattningar per kapitel, grafen och granskningarna | boken | `` med

```
| `bok/` | planen och minnet: idén, personerna och deras förlagor, handlingen, rösten, världen, besluten, vägvalen, sammanfattningar per kapitel, grafen och granskningarna | boken |
```

1b. Under `### Förberedelse`, lägg till ett stycke efter stycket om stilverkstaden:

```markdown
I **karaktärsverkstaden** prövas en person i tre korta scener där hen sätts under tryck, tills du känner igen personen. En karaktär kan bygga på en verklig person, en **förlaga**: Researcher tar fram vad personen säger om sig själv och vad andra säger om hen, med källor, och boken lånar en spänning mellan egenskaper, aldrig en biografi. Står förlagans namn i ett kapitel stoppar `bok validate` det.
```

och ersätt `Bygger boken på verkliga händelser läses planen först av sensitivitetsläsaren.` med `Bygger boken på verkliga händelser, eller har den förlagor, läses planen först av sensitivitetsläsaren.`

1c. Lägg till ett avsnitt direkt före `## Rollerna`:

```markdown
### Vägval

När det finns flera möjliga vägar och den första idén inte räcker kan du be om vägval. Claude ramar in frågan med dig, en roll listar det uppenbara för sig, `bok fron` drar slumpade frön ur listor som följer med verktyget, fyra roller tar ett frö var, och en kritiker sållar bort det uppenbara och det som bryter mot boken. Du får 4–6 riktningar med vad som är bra, vad som är rimligt och det starkaste skälet att avstå, men inga betyg. Du väljer och kan be om ett varv till. Varven sparas i `bok/vagval/`.
```

1d. I tabellen under `## Rollerna`: ersätt Writer-raden med `| Writer | skriver och reviderar prosan; tryckprov i karaktärsverkstaden |`, Researcher-raden med `| Researcher | research, fackgranskning mot källor och porträtt av förlagor |`, och lägg till före raden `| Audiobook, Marknad | … |`:

```
| Vägval | tar fram vägval: det uppenbara, en gren ur ett frö, en utveckling av det du valt |
| Idékritiker | sållar och grupperar vägvalen, utan betyg |
```

- [ ] **Steg 2: `README.md` i repots rot**

2a. Lägg till sist i punkt 1 under "Hur det fungerar" (efter "…och du väljer."): ` I **karaktärsverkstaden** prövas en person i korta scener under tryck, gärna med en verklig person som förlaga. Vid vägskäl ger **vägval** flera distinkta alternativ i stället för det första som dyker upp.`

2b. I tabellen under "Kommandon", ersätt validate-raden och lägg till en rad efter den:

```
| `bok validate` | förbjudna namn och förlagor, tidslinjen och namn/åldrar att kontrollera |
| `bok fron` | slumpade frön till vägval |
```

2c. Under "Roller", ersätt `Researcher, Världsbyggare, Audiobook-regissör och Marknadsförare vid behov.` med `Vägval och Idékritiker när du vill ha flera vägar att välja mellan. Researcher, Världsbyggare, Audiobook-regissör och Marknadsförare vid behov.`

- [ ] **Steg 3: `CHANGELOG.md`**

Under `## [Unreleased]`:

```markdown
### Lagt till
- Förlagor: en karaktär kan bygga på en verklig person. Researcher tar fram ett porträtt ur intervjuer och vad andra säger, med källor, i `bok/karaktarer/forlagor/`. `bok validate` stoppar kapitel där förlagans namn står, och sensitivitetsläsaren läser planen när boken har förlagor.
- Karaktärsverkstaden: personer prövas i tre korta scener under tryck. Karaktärsmallen har nya, frivilliga rubriker: förlaga, motsägelser, självbild och andras bild, det hen döljer, under tryck, vardag och öppet.
- Vägval: flera distinkta alternativ för en fråga i boken, från rollerna Vägval och Idékritiker, med slumpade frön från `bok fron`. Varven sparas i `bok/vagval/`.

### Fixat
- `bok validate` stoppar förbjudna namn också i genitiv ("Olof Palmes").
```

- [ ] **Steg 4: Kör testerna**

Kör: `uv run pytest -q`
Förväntat: alla PASS.

- [ ] **Steg 5: Commit**

```bash
git add docs/hur-det-fungerar.md README.md CHANGELOG.md
git commit -m "docs: förlagor, karaktärsverkstad och vägval"
```

---

### Uppgift 9: Prova i en riktig bok

Inga kodändringar; det här är kontrollen att flödet fungerar för en författare. Rapportera vad som hände, också det som skavde.

- [ ] **Steg 1: Installera grenens version och skapa en provbok**

```bash
uv tool install --force --from . bok
mkdir -p /tmp/provbok && cd /tmp/provbok && bok init --titel "Provbok" --no-git
```

Förväntat: utskriften listar bland annat `.claude/agents/bok-vagval.md`, `.claude/agents/bok-idekritiker.md` och `.claude/bok/hantverk/karaktarer.md`, och `bok/karaktarer/forlagor/`, `bok/karaktarer/prov/` och `bok/vagval/` finns.

- [ ] **Steg 2: Mekaniken**

```bash
cd /tmp/provbok
printf -- "---\nnamn: Cathie Wood\nalias: [Catherine Wood]\nkaraktarer: [vera]\n---\n" > bok/karaktarer/forlagor/cathie-wood.md
mkdir -p manuskript && printf "Hon läste Cathie Woods brev.\n" > manuskript/kapitel-01.md
bok validate; echo "exit $?"
bok status
bok fron --antagande "det sker i en scen" --antagande "hon gör det ensam"
bok fron --slump 4711 --json --spara bok/vagval/2026-10-04-prov && bok fron --klass process --antal 1 --spara bok/vagval/2026-10-04-prov && cat bok/vagval/2026-10-04-prov/fron.md
```

Förväntat: `bok validate` ger BLOCKERANDE för Cathie Wood och exit 1; `bok status` visar "Verkliga personer och händelser"; fröna har fyra rader där den fjärde är förlagan; `fron.md` har två dragningar.

- [ ] **Steg 3: Ett vägvalsvarv och en karaktärsverkstad i Claude Code**

Öppna en kopia av Sekretariatet (aldrig originalet), kör `bok init` där med grenens version och be Claude: "Ge mig vägval för hur Marléne korsar gränsen första gången." och sedan "Kör karaktärsverkstaden för Marléne." Kontrollera:
- ramen visas och väntar på ja innan något startar,
- grenarna får inte `uppenbart.md` (läs agentanropen),
- kartan har 4–6 riktningar, inga betyg och ingen rekommendation,
- tryckproven hamnar i `bok/karaktarer/prov/marlene-ostlund/` och Writer läser inte förlagan.

- [ ] **Steg 4: Rapportera**

Skriv kort till utvecklaren: vad som fungerade, vad som skavde, och förslag på ändringar. Inga commits i Sekretariatet.
