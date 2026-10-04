# Röstlabbet (bok 2.5) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modulen `rostlabb`: ett labb där författarna hittar bokens röst och form genom att välja bland genererade varianter, och mätbara ankare (`bok rost`, låsta ställen i `bok validate`) som håller rösten genom skrivloopen.

**Architecture:** Python-delen är en ny modul `src/bok/rost.py` (textanalys, profil, drift med Burrows Delta, pastisch, urval) plus små tillägg i `fron.py`, `validera.py` och `mallar.py`. Processen (labbets varv, pekningar, nya uppdrag) är Markdown i det genererade ramverket under `src/bok/data/genererat/claude/`. Modulens bokfiler ligger i `src/bok/data/moduler/rostlabb/`.

**Tech Stack:** Python 3.11+, bara standardbiblioteket (`re`, `statistics`, `argparse`, `json`), pytest via `uv run pytest`.

**Spec:** `docs/superpowers/specs/2026-10-04-rostlabbet-design.md`

## Global Constraints

- Bara standardbiblioteket i `src/bok/`; inga nya beroenden (ingen spaCy, Stanza eller liknande).
- Fel som visas för användaren är `BokFel` (eller en subklass) och ger exitkod 2 via `cli.main`; varningar ger exitkod 0.
- Allt nytt gäller bara när `rostlabb` står i `moduler` i `bok.toml`. Utan modulen fungerar `bok` som i 2.4.
- `bok rost` kräver modulen: utan den `RostFel` med texten "Modulen rostlabb är inte på i boken. Kör `bok mall rostlabb` först."
- Konstanter: meningar under 6 ord är korta, över 30 ord långa; tolerans 25 % av provbankens spann (25 % av medianen när spannet är noll); pastisch vid minst 5 gemensamma ord i följd; minsta underlag 3 provstycken och 2 kontrollvarianter.
- Svenska i all text som användaren eller Claude läser. Följ varje fils befintliga stil (skillen och rollerna säger "hon" och "henne" om författaren).
- Sökvägar i backticks i paketets Markdown (`bok/…`, `.claude/…`) måste finnas i paketet, annars fallerar `tests/test_innehall.py::test_inga_dinglande_sokvagar` (mönster med `NN`, `<…>`, `{…}` och `*` undantas).
- Ändringar i `src/bok/data/genererat/` når befintliga böcker först när versionen höjs; versionen höjs i release-steget, inte i den här planen.

## Review Focus

- Kapitel- och provbanksfiler med CRLF-radslut eller BOM: räknas som samma text som med LF (testas i Task 3).
- Provbanksfil med trasigt huvud (saknar avslutande `---`): räknas som text utan `lage`, ingen krasch, varken i `profil` eller `urval` (testas i Task 3 och Task 5).
- Låst citat med typografiska citattecken eller radbrytning mitt i, mot ett kapitel med raka citattecken eller annan radbrytning: ska passera (testas i Task 6).
- Tomt kapitel (inga ord) i `bok rost drift`: ingen division med noll, inga påhittade varningar (testas i Task 4).
- Scenkort med `lage` som ingen provbanksfil har: `urval` faller tillbaka på hela banken i stället för att returnera inget (testas i Task 5).

---

### Task 1: Tre nya klasser i `bok fron`

**Files:**
- Create: `src/bok/data/fron/rostdrag.txt`, `src/bok/data/fron/formgrepp.txt`, `src/bok/data/fron/kalla.txt`
- Modify: `src/bok/fron.py:13` (`KLASSER`)
- Modify: `src/bok/data/genererat/claude/bok/verktyg.md` (raden för `bok fron`)
- Test: `tests/test_fron.py`

**Interfaces:**
- Produces: `bok.fron.KLASSER` innehåller `"rostdrag"`, `"formgrepp"`, `"kalla"`; `STANDARD` oförändrad. `bok fron --klass rostdrag --klass kalla --klass formgrepp --antal 8 --json --spara bok/stil/labb` fungerar (används av skillen i Task 7).

- [ ] **Step 1: Write the failing test**

Lägg sist i `tests/test_fron.py`:

```python
NYA = ("rostdrag", "formgrepp", "kalla")


def test_nya_klasser_finns_men_dras_inte_som_standard():
    assert set(NYA) <= set(KLASSER)
    for slump in range(20):
        assert not {f["klass"] for f in dra(antal=8, slump=slump)["fron"]} & set(NYA)


def test_rostlabbets_dragning():
    fron = dra(antal=6, klasser=list(NYA), slump=11)["fron"]
    assert [f["klass"] for f in fron] == ["rostdrag", "formgrepp", "kalla"] * 2
```

(`test_listorna` och `test_inga_listor_utover_klasserna` täcker de nya listorna automatiskt: minst 40 frön, inga dubbletter, högst 140 tecken, ingen avslutande punkt.)

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_fron.py -v`
Expected: FAIL i `test_nya_klasser_finns_men_dras_inte_som_standard` (klasserna saknas i `KLASSER`).

- [ ] **Step 3: Write the lists and register the classes**

`src/bok/data/fron/rostdrag.txt`:

```
# Drag på meningsnivå för Röstlabbet. En rad per frö.
inga bisatser
meningar som slutar i ett substantiv
andra person: berättaren säger du
presens även om det som berättas är över
inga adjektiv framför substantiv
varje stycke är en enda mening
samma fras upprepas med en förskjutning varje gång
repliker utan anföringsverb
inga repliker, allt som sägs återges indirekt
berättaren registrerar men tolkar aldrig
korta huvudsatser som staplas utan konjunktion
långa meningar som håller andan över en hel scen
frågor som aldrig besvaras
siffror och mått i stället för känslor
berättaren rättar sig själv mitt i meningen
ett ord som återkommer i varje stycke
tiden anges med klockslag, aldrig med skymning eller gryning
bara det som syns, inget som tänks
vi-form: en grupp berättar
talspråk i berättarrösten
meningar som börjar med ett verb
inga namn, bara funktioner: chefen, systern, mannen vid fönstret
parenteser där berättaren lägger till det som inte borde sägas
slutet på varje stycke vänder på det som just sagts
kroppen före känslan: först vad händerna gör
förklaringar stryks, bara följderna står kvar
liturgiskt tonfall i vardagliga situationer
torr humor i det mest allvarliga
berättaren vet hur det slutar och säger det tidigt
listor i stället för beskrivningar
en enda lång mening per kapitel som bryter mönstret
ljud i stället för bilder
samma händelse i två tempus
inga metaforer, bara exakta ord
en metafor som bärs genom hela scenen
tystnader markerade med radbrytning
ordförråd ur ett yrke som inte är personens
berättaren tilltalar läsaren direkt en gång per kapitel
nekande satser: det som inte hände
formell svenska i intima scener
ett barns syntax i en vuxen berättare
varje replik är kortare än fem ord
meningar utan subjekt
```

`src/bok/data/fron/formgrepp.txt`:

```
# Formgrepp i bokens skala för Röstlabbet. En rad per frö.
kapitel som dokument: protokoll, brev, promemorior
omvänd kronologi
en scen berättas två gånger ur olika perspektiv
kapitlen följer en dagordning
berättaren utelämnar en sak som läsaren förstår först i slutet
varje kapitel är en enda dag
en ram: någon berättar i efterhand för någon
kapitlen växlar mellan då och nu
fotnoter som säger emot texten
fragment utan övergångar
andra person genom hela boken
en kör: en grupp som kommenterar
kapitlen blir kortare mot slutet
en bärande scen återkommer i varje akt, förändrad
boken börjar med slutet
kapitel som är förhör
brevroman
en dagbok som ljuger
en berättare som inte är med i handlingen
tidshopp på exakt samma antal år
varje kapitel har samma första mening
en person som aldrig syns men styr allt
en inventarielista som kapitel
kapitel som är ett enda samtal
parallella berättelser som möts först i sista kapitlet
en byggnad som berättare
berättaren tilltalar en död person
kapitlen är rum i ett hus
varje akt har en annan berättare
utelämnade kapitel: numreringen hoppar
klimax berättas inte, bara det före och det efter
mötesprotokoll varvat med det som sades i korridoren
boken är ett arkiv som någon går igenom
dokumentär ton med påhittat innehåll
ett kapitel i framtidsform
kapitel som är vägbeskrivningar
samma vecka berättad av fyra personer
en händelse som aldrig berättas men som alla kapitel kretsar kring
berättaren blir en annan halvvägs
en fråga per kapitel, svaret först i nästa
kapitel som är remissvar
kapitlen numreras baklänges
```

`src/bok/data/fron/kalla.txt`:

```
# Texter utanför litteraturen som ett drag kan låna form från. En rad per frö.
sjörapport
liturgi
rättegångsprotokoll
telegram
bruksanvisning
mötesprotokoll
väderrapport
recept
obduktionsprotokoll
kontaktannons
dödsannons
platsannons
förfrågningsunderlag i en offentlig upphandling
psalm
fotbollsreferat
radiotrafik mellan flygledare och pilot
inventarieförteckning
dagordning
bokföring
polisrapport
journalanteckning
schackkommentar
skiftrapport från en gruva
skolbetyg med omdömen
försäkringsärende
tidtabell
bönbok
byggbeskrivning
fågelskådares anteckningar
sms-tråd
röstmeddelande
domstolsbeslut
vetenskaplig sammanfattning
ritning
stickmönster
kartans teckenförklaring
körschema
bipacksedel
riksdagsprotokoll
skeppsdagbok
spelregler
utvecklingssamtal
pressmeddelande
```

I `src/bok/fron.py`, ändra rad 13:

```python
KLASSER = ("doman", "omvandning", "begransning", "process", "forlaga", "rostdrag", "formgrepp", "kalla")
```

I `src/bok/data/genererat/claude/bok/verktyg.md`, ändra raden för `bok fron` så att den slutar:

```
| `bok fron [--antal N] [--klass KLASS …] [--antagande TEXT …] [--slump TAL] [--spara MAPP]` | slumpade frön till ett vägval eller Röstlabbet (`--json` för skillen); klasserna är doman, omvandning, begransning, process och forlaga, och för Röstlabbet rostdrag, formgrepp och kalla |
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_fron.py tests/test_innehall.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/bok/fron.py src/bok/data/fron/ src/bok/data/genererat/claude/bok/verktyg.md tests/test_fron.py
git commit -m "feat: bok fron drar rostdrag, formgrepp och kalla till Röstlabbet"
```

---

### Task 2: Modulen `rostlabb` och scenkortets fält

**Files:**
- Create: `src/bok/data/moduler/rostlabb/bok/stil/labb/README.md`
- Create: `src/bok/data/moduler/rostlabb/bok/stil/labb/provscener.md`
- Create: `src/bok/data/moduler/rostlabb/bok/stil/provbank/README.md`
- Create: `src/bok/data/moduler/rostlabb/bok/stil/kontroll/README.md`
- Create: `src/bok/data/moduler/rostlabb/bok/stil/pekningar/README.md`
- Modify: `src/bok/mallar.py:12-20` (`BESKRIVNING`)
- Modify: `src/bok/data/bok/bok/plot/kapitel/MALL.md` (frontmatter)
- Test: `tests/test_mallar.py`, `tests/test_innehall.py`

**Interfaces:**
- Produces: `lagg_till(root, "rostlabb")` skapar filerna ovan och lägger `"rostlabb"` i `moduler`. Senare tasks använder `lagg_till(bok, "rostlabb")` i testerna för att slå på modulen. Scenkortsmallen har `vagar:` och `lage:`.

- [ ] **Step 1: Write the failing tests**

Lägg sist i `tests/test_mallar.py`:

```python
def test_lagg_till_rostlabb(bok):
    skapade = lagg_till(bok, "rostlabb")
    for rel in ("bok/stil/labb/README.md", "bok/stil/labb/provscener.md", "bok/stil/provbank/README.md",
                "bok/stil/kontroll/README.md", "bok/stil/pekningar/README.md"):
        assert rel in skapade, rel
    assert read(bok)["moduler"] == ["rostlabb"]
```

Lägg sist i `tests/test_innehall.py`:

```python
def test_bokfiler_2_5():
    mall = (DATA / "bok/bok/plot/kapitel/MALL.md").read_text(encoding="utf-8")
    meta, _ = split(mall)
    assert "vagar" in meta and "lage" in meta
    labb = (DATA / "moduler/rostlabb/bok/stil/labb/README.md").read_text(encoding="utf-8")
    for fras in ("## Recept", "## Antiröst", "## Form", "Formprov", "Röstprov", "kontroll"):
        assert fras in labb, fras
    pek = (DATA / "moduler/rostlabb/bok/stil/pekningar/README.md").read_text(encoding="utf-8")
    for fras in ("## Lever", "## Dött", "## Upplåst"):
        assert fras in pek, fras
    bank = (DATA / "moduler/rostlabb/bok/stil/provbank/README.md").read_text(encoding="utf-8")
    for fras in ("lage:", "kalla:", "datum:", "15"):
        assert fras in bank, fras
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_mallar.py tests/test_innehall.py::test_bokfiler_2_5 -v`
Expected: FAIL (`Okänd modul 'rostlabb'` och saknade filer).

- [ ] **Step 3: Write the module**

I `src/bok/mallar.py`, lägg sist i `BESKRIVNING`:

```python
    "rostlabb": "Röstlabbet: sök bokens röst och form genom att välja bland varianter, och håll den med mätbara ankare.",
```

`src/bok/data/moduler/rostlabb/bok/stil/labb/README.md`:

````markdown
# Röstlabbet

Här söks bokens röst och form. Författaren skriver inte: Claude skriver varianter, författaren pekar ut vad som lever och vad som är dött, och nästa generation bygger på det.

## Två sorters prov

- **Formprov:** en skiss av första akten på en sida, i fyra olika former. Visar det som bara syns i bokens skala: hur kapitlen ser ut, vad som utelämnas, hur tiden rör sig.
- **Röstprov:** två provscener ur boken i `bok/stil/labb/provscener.md`, 250–350 ord var, en stilla och en under tryck. Samma scener i varje generation.

Varje generation har fyra varianter (A–D) med var sitt recept och en kontroll utan recept: så skriver Claude utan riktning. Kontrollen visar AI-genomsnittet, det boken inte ska låta som.

## Ett recept

3–6 drag, vart och ett med en källa: en förebild (texterna i `bok/stil/exempel/`) eller ett frö ur `bok fron`.

```
- Distans: berättaren registrerar, tolkar aldrig. (förebild)
- Upprepning i repliker som vägrar svara. (förebild)
- Mötesprotokollets passiv när makten talar. (frö: kalla – mötesprotokoll)
```

## Generationerna

En fil per generation: `gen-01.md`, `gen-02.md` … för röstprov och `form-01.md` … för formprov. Varje fil har recepten med källor, texterna, kritikerns sållning och författarens pekningar under varje variant.

## När rösten är hittad

`bok/stil/rost.md` skrivs om med tre rubriker:

```
## Recept
- Drag (källa). Hur det märks. Exempel: "…"

## Antiröst
- Mönster ur kontrollerna och de döda ställena. Exempel: "…"

## Form
Se Formlag i bok/koncept/form.md.
```

De godkända provstyckena sparas i `bok/stil/provbank/`, röstprovens kontroller i `bok/stil/kontroll/` och formlagen under `## Formlag` i `bok/koncept/form.md`.
````

`src/bok/data/moduler/rostlabb/bok/stil/labb/provscener.md`:

```markdown
# Provscener

Två scener ur boken som varje generation i Röstlabbet skriver. Samma scener hela tiden, så att varianterna går att jämföra.

## Stilla
{{En scen där inget avgörande händer: vem, var, vad som pågår. Två till fyra meningar.}}

## Under tryck
{{En scen där något står på spel: vem, var, vad som står på spel. Två till fyra meningar.}}
```

`src/bok/data/moduler/rostlabb/bok/stil/provbank/README.md`:

```markdown
# Provbanken

Godkända provstycken i bokens röst, ett per fil. Writer läser två eller tre av dem inför varje kapitel (`bok rost urval --kapitel N`), och `bok rost drift` mäter kapitlen mot dem.

Varje fil börjar med ett huvud:

    ---
    lage: stilla
    kalla: gen-03 B
    datum: 2026-10-04
    ---

- `lage`: `stilla` eller `tryck`.
- `kalla`: generation och variant, eller kapitlet ett levande ställe kom från (`kapitel-07`).
- `datum`: när stycket godkändes.

Högst 15 stycken. Vid varje aktgräns rensar författaren banken.
```

`src/bok/data/moduler/rostlabb/bok/stil/kontroll/README.md`:

```markdown
# Kontroll

Röstprovens kontrollvarianter: provscenerna skrivna utan recept och utan röst. De visar AI-genomsnittet. `bok rost drift` varnar när ett kapitel ligger närmare dem än provbanken. En fil per variant, med samma huvud som i provbanken.
```

`src/bok/data/moduler/rostlabb/bok/stil/pekningar/README.md`:

````markdown
# Pekningar

Efter första granskningen pekar författaren ut levande och döda ställen i kapitlet. En fil per kapitel: `kapitel-03.md` och så vidare.

```
## Lever
- "Han räknade stolarna två gånger innan han satte sig."

## Dött
- "Tystnaden lade sig över rummet."

## Upplåst
```

- **Lever** är låst. `bok validate` stoppar kapitlet om citatet inte längre står ordagrant i det. Granskarna får kommentera men inte kräva ändringar.
- **Dött** skriver Writer om först.
- **Upplåst**: flytta hit ett citat för att låsa upp det.

Citera ordagrant ur kapitlet, ett citat per rad.
````

I `src/bok/data/bok/bok/plot/kapitel/MALL.md`, lägg två rader efter `tillbakablick: false` (före `godkand: false`):

```
vagar:
lage:
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_mallar.py tests/test_innehall.py -v`
Expected: PASS (inklusive `test_moduler_stammer_med_beskrivningar` och `test_inga_dinglande_sokvagar`).

- [ ] **Step 5: Commit**

```bash
git add src/bok/mallar.py src/bok/data/moduler/rostlabb src/bok/data/bok/bok/plot/kapitel/MALL.md tests/test_mallar.py tests/test_innehall.py
git commit -m "feat: modulen rostlabb och fälten vagar och lage i scenkortet"
```

---

### Task 3: `bok rost profil` och textanalysen

**Files:**
- Create: `src/bok/rost.py`
- Create: `src/bok/data/rost/funktionsord.txt`, `src/bok/data/rost/pronomen.txt`
- Modify: `src/bok/cli.py:15-17` (`_moduler`)
- Test: `tests/test_rost.py`

**Interfaces:**
- Consumes: `bok.mallar.lagg_till(root, "rostlabb")` (Task 2) i testerna; `bok.tics.las_kapitel(Path) -> str`; `bok.frontmatter.split(str) -> (dict, str)`; `bok.boktoml.read(root) -> dict`.
- Produces (används av Task 4 och 5):
  - `class RostFel(BokFel)`
  - `ren_text(text: str) -> str`
  - `stycken(text: str) -> list[str]`, `dela_meningar(stycke: str) -> list[str]`, `ord_i(text: str) -> list[str]`
  - `funktionsord() -> list[str]`, `pronomen() -> set[str]`
  - `matt(text: str) -> dict[str, float]` med nycklarna i `MATT`
  - `profil(texter: list[str]) -> dict` med formen `{"antal": int, "matt": {namn: {"median": float, "min": float, "max": float}}}`
  - `krav_modul(root: Path) -> None`
  - `texter(root: Path, mapp: str) -> list[tuple[Path, dict, str]]` (fil, huvud, ren text) för `provbank`, `kontroll`, `exempel`
  - `register(sub)` med underkommandot `profil` (Task 4 och 5 lägger till `drift` och `urval` i samma `register`)

- [ ] **Step 1: Write the failing tests**

`tests/test_rost.py`:

```python
import json

import pytest

from bok.cli import main
from bok.mallar import lagg_till
from bok.rost import (MATT, RostFel, dela_meningar, funktionsord, krav_modul, matt, ord_i, profil, pronomen,
                      ren_text, stycken, texter)
from helpers import skriv


def bank(root, namn, text, lage="stilla", datum="2026-10-01", mapp="provbank"):
    return skriv(root, f"bok/stil/{mapp}/{namn}.md",
                 f"---\nlage: {lage}\nkalla: gen-01 A\ndatum: {datum}\n---\n\n{text}\n")


def test_datafilerna():
    fo = funktionsord()
    assert len(fo) >= 100 and len(set(fo)) == len(fo)
    assert {"och", "att", "det", "som"} <= set(fo)
    assert {"jag", "du", "han", "hon", "hen", "vi", "de", "man"} <= pronomen()


def test_ren_text_tar_bort_huvud_rubriker_och_kommentarer():
    text = "---\nlage: stilla\n---\n# Rubrik\n\nHon gick.<!-- not -->\n\n## Under\nHan stod kvar.\n"
    assert ren_text(text) == "Hon gick.\n\nHan stod kvar."


def test_ren_text_tal_crlf_bom_och_trasigt_huvud():
    assert ren_text("﻿---\r\nlage: tryck\r\n---\r\nHon gick.\r\n") == "Hon gick."
    assert ren_text("---\nlage: tryck\nHon gick.\n") == "---\nlage: tryck\nHon gick."


def test_meningar_och_stycken():
    assert dela_meningar('Hon gick. – Kom hit, sa han. "Nej." Hon log! Vad? 3 st. och sen.') == [
        "Hon gick.", "– Kom hit, sa han.", '"Nej."', "Hon log!", "Vad? 3 st. och sen."]
    assert stycken("Ett.\nTvå.\n\n\nTre.") == ["Ett. Två.", "Tre."]
    assert ord_i("Det var Åsa-Lena, 34 år.") == ["det", "var", "åsa-lena", "år"]


def test_matt_kanda_varden():
    text = ("Hon gick hem.\n\n"                                        # 3 ord
            "Han satt kvar vid bordet; det var sent och mörkt ute.\n\n"  # 11 ord
            "– Kom nu, sa hon.\n\n"                                     # 4 ord, replik
            "Det var en lång dag: regn, vind, kyla och sedan ingenting mer än tystnad i huset.")  # 16 ord
    m = matt(text)
    assert set(m) == set(MATT)
    assert m["meningslangd_median"] == 7.5
    assert m["meningslangd_kvartilavstand"] == pytest.approx(12.25 - 3.75)
    assert m["andel_korta"] == 0.5
    assert m["andel_langa"] == 0
    assert m["styckelangd_median"] == 1
    assert m["replikandel"] == pytest.approx(4 / 34)
    assert m["komma"] == pytest.approx(3 * 1000 / 34)
    assert m["semikolon"] == pytest.approx(1000 / 34)
    assert m["kolon"] == pytest.approx(1000 / 34)
    assert m["tankstreck"] == 0
    assert m["fragetecken"] == 0
    assert m["pronomenstart"] == 0.75  # hon, han, det; inte "kom"


def test_matt_tom_text_ger_nollor():
    assert set(matt("").values()) == {0}


def test_profil():
    p = profil(["Hon gick. Han stod.", "Det var sent och mörkt ute i staden den kvällen."])
    assert p["antal"] == 2
    assert p["matt"]["meningslangd_median"] == {"median": 6.0, "min": 2, "max": 10}


def test_krav_modul(bok):
    with pytest.raises(RostFel, match="bok mall rostlabb"):
        krav_modul(bok)
    lagg_till(bok, "rostlabb")
    krav_modul(bok)


def test_texter_hoppar_over_readme_och_tal_trasigt_huvud(bok):
    lagg_till(bok, "rostlabb")
    bank(bok, "a", "Hon gick.")
    skriv(bok, "bok/stil/provbank/b.md", "---\nlage: tryck\nHan sprang.\n")
    t = texter(bok, "provbank")
    assert [p.name for p, _, _ in t] == ["a.md", "b.md"]
    assert t[0][1]["lage"] == "stilla" and t[1][1] == {}


def test_cli_profil(bok, capsys):
    lagg_till(bok, "rostlabb")
    bank(bok, "a", "Hon gick. Han stod.")
    bank(bok, "b", "Det var sent och mörkt ute i staden den kvällen.")
    assert main(["rost", "profil"]) == 0
    out = capsys.readouterr().out
    assert "2 provstycken" in out and "meningslangd_median" in out
    assert main(["rost", "profil", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["antal"] == 2


def test_cli_profil_tom_bank_och_utan_modul(bok, capsys):
    assert main(["rost", "profil"]) == 2
    lagg_till(bok, "rostlabb")
    assert main(["rost", "profil"]) == 2
    assert "tom" in capsys.readouterr().err
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_rost.py -v`
Expected: FAIL med `ModuleNotFoundError: No module named 'bok.rost'`.

- [ ] **Step 3: Write the data files and the module**

`src/bok/data/rost/funktionsord.txt` (ett ord per rad; samma ord som nedan, i den här ordningen):

```
# Svenska funktionsord för Burrows Delta i bok rost drift. Ett ord per rad, gemener.
och
i
att
det
som
en
på
är
av
för
med
till
den
har
de
inte
om
ett
han
hon
men
var
jag
sig
från
vi
så
kan
man
när
du
nu
skulle
bara
eller
efter
ut
upp
vid
hade
sin
där
sedan
också
mot
under
in
över
kommer
alla
ska
vad
vara
blir
mycket
här
dem
hur
denna
dessa
detta
någon
något
inget
ingen
många
mer
mest
själv
sitt
sina
mig
dig
oss
er
honom
henne
deras
dess
hans
hennes
min
mitt
mina
din
ditt
dina
vår
vårt
våra
än
då
ju
nog
väl
redan
ännu
aldrig
alltid
ofta
igen
bort
fram
hem
kvar
inne
ute
utan
genom
mellan
bakom
framför
bland
hos
kring
trots
enligt
medan
eftersom
fast
fastän
innan
tills
ifall
därför
alltså
dock
ändå
även
just
endast
varje
varandra
vilken
vilket
vilka
vem
varför
sådan
sådant
sådana
annan
annat
andra
samma
hela
blev
varit
vore
får
fick
måste
kunde
ville
vill
skall
går
gick
sa
säger
ser
såg
gör
gjorde
finns
fanns
ja
nej
kanske
lite
inga
några
allt
ens
hit
dit
härifrån
därifrån
```

`src/bok/data/rost/pronomen.txt`:

```
# Personliga pronomen för måttet pronomenstart i bok rost. Ett ord per rad, gemener.
jag
du
han
hon
hen
den
det
vi
ni
de
man
```

`src/bok/rost.py`:

```python
"""bok rost: rösten i siffror. Profil ur provbanken, drift för ett kapitel och urval till Writer."""

from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path

from bok import boktoml, frontmatter
from bok.init import DATA
from bok.rot import BokFel, find_root
from bok.tics import las_kapitel

ROSTDATA = DATA / "rost"
MODUL = "rostlabb"
KORT, LANG = 6, 30
TOLERANS = 0.25
NGRAM = 5
MIN_BANK, MIN_KONTROLL = 3, 2
MATT = ("meningslangd_median", "meningslangd_kvartilavstand", "andel_korta", "andel_langa",
        "styckelangd_median", "replikandel", "komma", "semikolon", "kolon", "tankstreck",
        "fragetecken", "pronomenstart")

_ORD = re.compile(r"[A-Za-zÅÄÖåäöÉéÜü]+(?:-[A-Za-zÅÄÖåäöÉéÜü]+)*")
_SLUT = re.compile(r"(?:(?<=[.!?…])|(?<=[.!?…][\"”»']))\s+(?=[\"”«»„–—]?\s*[A-ZÅÄÖÉ])")
_REPLIK = ("–", "—", '"', "”", "«", "»", "„")
_KOMMENTAR = re.compile(r"<!--.*?-->", re.S)


class RostFel(BokFel):
    pass


def _lista(namn: str) -> list[str]:
    rader = (r.strip() for r in (ROSTDATA / namn).read_text(encoding="utf-8").splitlines())
    return [r for r in rader if r and not r.startswith("#")]


def funktionsord() -> list[str]:
    return _lista("funktionsord.txt")


def pronomen() -> set[str]:
    return set(_lista("pronomen.txt"))


def ren_text(text: str) -> str:
    """Brödtexten: utan huvud, rubriker och HTML-kommentarer. Ett trasigt huvud räknas som text."""
    try:
        _, body = frontmatter.split(text)
    except frontmatter.FrontmatterFel:
        body = text.lstrip("﻿").replace("\r\n", "\n")
    body = _KOMMENTAR.sub("", body)
    rader = [r.rstrip() for r in body.splitlines() if not r.lstrip().startswith("#")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(rader)).strip()


def ord_i(text: str) -> list[str]:
    return [m.group(0).lower() for m in _ORD.finditer(text)]


def stycken(text: str) -> list[str]:
    return [" ".join(s.split()) for s in re.split(r"\n\s*\n", text) if s.strip()]


def dela_meningar(stycke: str) -> list[str]:
    return [m.strip() for m in _SLUT.split(stycke) if ord_i(m)]


def _tankstreck(st: list[str]) -> int:
    return sum(s.count("–") + s.count("—") - (1 if s.startswith(("–", "—")) else 0) for s in st)


def matt(text: str) -> dict[str, float]:
    st = stycken(text)
    meningar = [m for s in st for m in dela_meningar(s)]
    langder = [len(ord_i(m)) for m in meningar]
    if not langder:
        return {namn: 0 for namn in MATT}
    antal_ord = sum(langder)
    kvartiler = statistics.quantiles(langder, n=4, method="inclusive") if len(langder) > 1 else [langder[0]] * 3
    pron = pronomen()
    per_tusen = 1000 / antal_ord
    return {
        "meningslangd_median": statistics.median(langder),
        "meningslangd_kvartilavstand": kvartiler[2] - kvartiler[0],
        "andel_korta": sum(n < KORT for n in langder) / len(langder),
        "andel_langa": sum(n > LANG for n in langder) / len(langder),
        "styckelangd_median": statistics.median(len(dela_meningar(s)) for s in st),
        "replikandel": sum(len(ord_i(s)) for s in st if s.startswith(_REPLIK)) / antal_ord,
        "komma": text.count(",") * per_tusen,
        "semikolon": text.count(";") * per_tusen,
        "kolon": text.count(":") * per_tusen,
        "tankstreck": _tankstreck(st) * per_tusen,
        "fragetecken": text.count("?") * per_tusen,
        "pronomenstart": sum(ord_i(m)[0] in pron for m in meningar) / len(meningar),
    }


def profil(texter_: list[str]) -> dict:
    alla = [matt(t) for t in texter_]
    return {"antal": len(alla), "matt": {
        namn: {"median": statistics.median(m[namn] for m in alla),
               "min": min(m[namn] for m in alla), "max": max(m[namn] for m in alla)}
        for namn in MATT}}


def krav_modul(root: Path) -> None:
    if MODUL not in (boktoml.read(root).get("moduler") or []):
        raise RostFel("Modulen rostlabb är inte på i boken. Kör `bok mall rostlabb` först.")


def texter(root: Path, mapp: str) -> list[tuple[Path, dict, str]]:
    """Filerna i bok/stil/<mapp>/ utom README.md: (fil, huvud, ren text). Trasigt huvud ger {}."""
    katalog = root / "bok" / "stil" / mapp
    ut = []
    for path in sorted(katalog.glob("*.md")):
        if path.name == "README.md":
            continue
        text = las_kapitel(path)
        try:
            meta, _ = frontmatter.split(text)
        except frontmatter.FrontmatterFel:
            meta = {}
        ut.append((path, meta, ren_text(text)))
    return ut


def _bank(root: Path) -> list[str]:
    krav_modul(root)
    bank = [t for _, _, t in texter(root, "provbank")]
    if not bank:
        raise RostFel("Provbanken bok/stil/provbank/ är tom. Röstlabbet fyller den med godkända provstycken.")
    return bank


def _tal(x: float) -> str:
    return f"{x:.2f}".rstrip("0").rstrip(".")


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("rost", help="rösten i siffror: profil, drift och urval (modulen rostlabb)")
    r = p.add_subparsers(dest="rostdel", metavar="<del>", required=True)
    a = r.add_parser("profil", help="provbankens profil")
    a.add_argument("--json", action="store_true", help="maskinläsbart, för skillen")
    a.set_defaults(func=_kor_profil)


def _kor_profil(args: argparse.Namespace) -> int:
    p = profil(_bank(find_root()))
    if args.json:
        print(json.dumps(p, ensure_ascii=False))
        return 0
    print(f"Provbanken: {p['antal']} provstycken")
    for namn, v in p["matt"].items():
        print(f"  {namn:<30} median {_tal(v['median'])}  ({_tal(v['min'])}–{_tal(v['max'])})")
    return 0
```

I `src/bok/cli.py`, ändra `_moduler`:

```python
def _moduler() -> list:
    from bok import annotations, bild, forslag, fron, graf, init, karta, mallar, rapport, rost, status, tics, validera

    return [init, status, mallar, graf, tics, validera, fron, rost, rapport, annotations, forslag, karta, bild]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_rost.py -v`
Expected: PASS. Om `test_matt_kanda_varden` inte stämmer: räkna om förväntningen för hand ur meningslängderna [3, 11, 4, 16] (median 7,5; inklusiva kvartiler 3,75 och 12,25), tre kommatecken och pronomenstart i tre av fyra meningar (`det` räknas som pronomen), inte genom att ändra koden mot testet.

- [ ] **Step 5: Run the full suite**

Run: `uv run pytest -q`
Expected: PASS (`test_ramverkets_kommandon_finns` påverkas inte än).

- [ ] **Step 6: Commit**

```bash
git add src/bok/rost.py src/bok/data/rost src/bok/cli.py tests/test_rost.py
git commit -m "feat: bok rost profil räknar provbankens röst"
```

---

### Task 4: `bok rost drift`

**Files:**
- Modify: `src/bok/rost.py` (nya funktioner och underkommandot `drift` i `register`)
- Test: `tests/test_rost_drift.py`

**Interfaces:**
- Consumes: från Task 3 `ren_text`, `ord_i`, `matt`, `profil`, `funktionsord`, `krav_modul`, `texter`, `MATT`, `TOLERANS`, `NGRAM`, `MIN_BANK`, `MIN_KONTROLL`, `_tal`, `register`.
- Produces:
  - `delta(text: str, rost: list[str], kontroll: list[str]) -> tuple[float, float]` (avstånd till rösten, avstånd till kontrollen)
  - `utanfor(kapitel: dict, prof: dict) -> list[tuple[str, float, float, float]]` (namn, värde, min, max)
  - `pastisch(text: str, kallor: list[tuple[str, str]]) -> list[tuple[str, str]]` (sekvens, källa)
  - `drift(root: Path, fil: Path) -> dict` med nycklarna `fil`, `underlag` (`{"provbank": int, "kontroll": int}`), `delta` (`None` eller `{"rost": float, "kontroll": float, "narmare_kontroll": bool}`), `utanfor` (lista av `{"matt", "varde", "min", "max"}`), `pastisch` (lista av `{"text", "kalla"}`)
  - CLI: `bok rost drift FIL [--json]`, exitkod 0 med varningar

- [ ] **Step 1: Write the failing tests**

`tests/test_rost_drift.py`:

```python
import json

from bok.cli import main
from bok.mallar import lagg_till
from bok.rost import delta, drift, pastisch, profil, utanfor, matt
from helpers import skriv

ROST = [
    "Hon tog kaffet och gick ut och det regnade och det var kallt och att gå var svårt.",
    "Han satt kvar och det var tyst och hon visste att det var över och att han visste.",
    "Det var morgon och det luktade järn och hon tänkte att det fick vara så.",
]
KONTROLL = [
    "När hon kom hem hade han redan gått, som om han hade vetat när hon skulle komma.",
    "Rummet som hon hade hyrt var tomt när hon kom, som alltid när det hade regnat.",
]


def labb(root, rost=ROST, kontroll=KONTROLL):
    lagg_till(root, "rostlabb")
    for i, t in enumerate(rost):
        skriv(root, f"bok/stil/provbank/r{i}.md", f"---\nlage: stilla\n---\n{t}\n")
    for i, t in enumerate(kontroll):
        skriv(root, f"bok/stil/kontroll/k{i}.md", f"---\nlage: stilla\n---\n{t}\n")


def test_delta_riktning():
    d_rost, d_kontroll = delta(ROST[0] + " " + ROST[1], ROST, KONTROLL)
    assert d_rost < d_kontroll
    d_rost, d_kontroll = delta(" ".join(KONTROLL), ROST, KONTROLL)
    assert d_kontroll < d_rost


def test_utanfor_spridningen():
    prof = profil(["Hon gick. Han stod.", "Det var sent. Hon sov."])  # median 2 ord per mening
    lang = matt("Det var sent på kvällen när hon äntligen kom hem till det tomma huset vid vattnet.")
    namn = [u[0] for u in utanfor(lang, prof)]
    assert "meningslangd_median" in namn
    assert utanfor(matt("Hon gick. Han stod."), prof) == []


def test_utanfor_nollspann_anvander_medianen():
    prof = profil(["Hon gick. Han stod.", "Hon sov. Han åt."])  # spannet för meningslängd är noll
    assert utanfor(matt("Hon gick. Han stod."), prof) == []


def test_pastisch_slar_ihop_sekvenser_och_anger_kalla():
    kalla = "Han räknade stolarna två gånger innan han satte sig vid bordet."
    text = "Det var kväll. Han räknade stolarna två gånger innan han satte sig ner."
    assert pastisch(text, [("bok/stil/provbank/a.md", kalla)]) == [
        ("han räknade stolarna två gånger innan han satte sig", "bok/stil/provbank/a.md")]
    assert pastisch("Han räknade stolarna en gång.", [("a", kalla)]) == []


def test_drift_varnar_nar_kapitlet_ar_kontroll(bok):
    labb(bok)
    kap = skriv(bok, "manuskript/kapitel-01.md", "# Kapitel 1\n\n" + " ".join(KONTROLL) + "\n")
    d = drift(bok, kap)
    assert d["underlag"] == {"provbank": 3, "kontroll": 2}
    assert d["delta"]["narmare_kontroll"] is True


def test_drift_lugn_nar_kapitlet_ar_rosten(bok):
    labb(bok)
    kap = skriv(bok, "manuskript/kapitel-01.md", ROST[0] + " " + ROST[2] + "\n")
    assert drift(bok, kap)["delta"]["narmare_kontroll"] is False


def test_drift_pastisch_mot_exempel(bok):
    labb(bok)
    skriv(bok, "bok/stil/exempel/forebild.md", "Varför: tonen.\n\nHon stod länge vid fönstret och såg på regnet.\n")
    kap = skriv(bok, "manuskript/kapitel-01.md", "Sedan stod hon länge vid fönstret och såg på regnet igen.\n")
    kallor = [p["kalla"] for p in drift(bok, kap)["pastisch"]]
    assert kallor == ["bok/stil/exempel/forebild.md"]


def test_drift_for_lite_underlag(bok):
    labb(bok, rost=ROST[:2])
    kap = skriv(bok, "manuskript/kapitel-01.md", "Hon gick.\n")
    d = drift(bok, kap)
    assert d["delta"] is None and d["utanfor"] == []


def test_drift_tomt_kapitel(bok):
    labb(bok)
    kap = skriv(bok, "manuskript/kapitel-01.md", "# Kapitel 1\n")
    d = drift(bok, kap)
    assert d["pastisch"] == []
    assert isinstance(d["delta"]["rost"], float)


def test_cli_drift(bok, capsys):
    labb(bok)
    skriv(bok, "manuskript/kapitel-01.md", " ".join(KONTROLL) + "\n")
    assert main(["rost", "drift", "manuskript/kapitel-01.md"]) == 0
    out = capsys.readouterr().out
    assert "närmare AI-genomsnittet" in out and "3 provstycken, 2 kontrollvarianter" in out
    assert main(["rost", "drift", "manuskript/kapitel-01.md", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["delta"]["narmare_kontroll"] is True


def test_cli_drift_fel(bok, capsys):
    skriv(bok, "manuskript/kapitel-01.md", "Hon gick.\n")
    assert main(["rost", "drift", "manuskript/kapitel-01.md"]) == 2  # modulen saknas
    lagg_till(bok, "rostlabb")
    assert main(["rost", "drift", "manuskript/kapitel-09.md"]) == 2  # filen saknas
    assert main(["rost", "drift", "manuskript/kapitel-01.md"]) == 0
    assert "För lite underlag" in capsys.readouterr().out
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_rost_drift.py -v`
Expected: FAIL med `ImportError: cannot import name 'delta'`.

- [ ] **Step 3: Implement drift**

Lägg till i `src/bok/rost.py`, före `register`:

```python
def _fw(text: str, ord_: list[str]) -> dict[str, float]:
    alla = ord_i(text)
    n = len(alla) or 1
    antal = {w: 0 for w in ord_}
    for w in alla:
        if w in antal:
            antal[w] += 1
    return {w: antal[w] / n for w in ord_}


def delta(text: str, rost: list[str], kontroll: list[str]) -> tuple[float, float]:
    """Burrows Delta på funktionsorden: avståndet från texten till röstens och kontrollens centroid."""
    ord_ = funktionsord()
    ref = [_fw(t, ord_) for t in rost + kontroll]
    medel = {w: statistics.fmean(v[w] for v in ref) for w in ord_}
    sd = {w: statistics.pstdev([v[w] for v in ref]) for w in ord_}
    drag = [w for w in ord_ if sd[w] > 0]
    if not drag:
        return 0.0, 0.0

    def z(v: dict[str, float]) -> dict[str, float]:
        return {w: (v[w] - medel[w]) / sd[w] for w in drag}

    def centroid(grupp: list[str]) -> dict[str, float]:
        zs = [z(_fw(t, ord_)) for t in grupp]
        return {w: statistics.fmean(x[w] for x in zs) for w in drag}

    zt = z(_fw(text, ord_))
    return tuple(statistics.fmean(abs(zt[w] - c[w]) for w in drag) for c in (centroid(rost), centroid(kontroll)))


def utanfor(kapitel: dict, prof: dict) -> list[tuple[str, float, float, float]]:
    ut = []
    for namn in MATT:
        v, s = kapitel[namn], prof["matt"][namn]
        spann = s["max"] - s["min"]
        tol = TOLERANS * (spann if spann > 0 else abs(s["median"]))
        if v < s["min"] - tol or v > s["max"] + tol:
            ut.append((namn, v, s["min"], s["max"]))
    return ut


def pastisch(text: str, kallor: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Sekvenser om minst NGRAM ord som texten delar med en källa, sammanslagna och med källan."""
    ord_ = ord_i(text)
    ut = []
    for namn, kalltext in kallor:
        k = ord_i(kalltext)
        gram = {tuple(k[i:i + NGRAM]) for i in range(len(k) - NGRAM + 1)}
        tackt = [False] * len(ord_)
        for i in range(len(ord_) - NGRAM + 1):
            if tuple(ord_[i:i + NGRAM]) in gram:
                tackt[i:i + NGRAM] = [True] * NGRAM
        i = 0
        while i < len(ord_):
            if not tackt[i]:
                i += 1
                continue
            j = i
            while j < len(ord_) and tackt[j]:
                j += 1
            ut.append((" ".join(ord_[i:j]), namn))
            i = j
    return ut


def drift(root: Path, fil: Path) -> dict:
    krav_modul(root)
    text = ren_text(las_kapitel(fil))
    bank, kontroll = texter(root, "provbank"), texter(root, "kontroll")
    kallor = [(p.relative_to(root).as_posix(), t) for p, _, t in bank + texter(root, "exempel")]
    ut = {
        "fil": fil.relative_to(root).as_posix() if fil.is_relative_to(root) else str(fil),
        "underlag": {"provbank": len(bank), "kontroll": len(kontroll)},
        "delta": None,
        "utanfor": [],
        "pastisch": [{"text": s, "kalla": k} for s, k in pastisch(text, kallor)],
    }
    if len(bank) >= MIN_BANK and len(kontroll) >= MIN_KONTROLL:
        d_rost, d_kontroll = delta(text, [t for *_, t in bank], [t for *_, t in kontroll])
        ut["delta"] = {"rost": round(d_rost, 3), "kontroll": round(d_kontroll, 3),
                       "narmare_kontroll": d_kontroll < d_rost}
        ut["utanfor"] = [{"matt": n, "varde": v, "min": lo, "max": hi}
                         for n, v, lo, hi in utanfor(matt(text), profil([t for *_, t in bank]))]
    return ut


def som_text_drift(d: dict) -> str:
    u = d["underlag"]
    rader = [d["fil"], f"  Underlag: {u['provbank']} provstycken, {u['kontroll']} kontrollvarianter."]
    if d["delta"] is None:
        rader.append(f"  För lite underlag för rösten (minst {MIN_BANK} provstycken och {MIN_KONTROLL} "
                     "kontrollvarianter); bara pastischkontrollen körs.")
    elif d["delta"]["narmare_kontroll"]:
        rader.append(f"  VARNING: närmare AI-genomsnittet än rösten (delta rösten {d['delta']['rost']}, "
                     f"kontrollen {d['delta']['kontroll']}).")
    for x in d["utanfor"]:
        rader.append(f"  Utanför röstens spridning: {x['matt']} {_tal(x['varde'])} "
                     f"(provbanken {_tal(x['min'])}–{_tal(x['max'])}).")
    for x in d["pastisch"]:
        rader.append(f"  Pastisch: \"{x['text']}\" ({x['kalla']}).")
    if len(rader) == 2 and d["delta"] is not None:
        rader.append(f"  Inga anmärkningar (delta rösten {d['delta']['rost']}, kontrollen {d['delta']['kontroll']}).")
    return "\n".join(rader)
```

Lägg till i `register`, efter `profil`:

```python
    b = r.add_parser("drift", help="ett kapitel mot rösten och AI-genomsnittet, och pastisch")
    b.add_argument("fil", help="kapitelfilen, till exempel manuskript/kapitel-03.md")
    b.add_argument("--json", action="store_true", help="maskinläsbart, för skillen")
    b.set_defaults(func=_kor_drift)
```

Och sist i filen:

```python
def _kor_drift(args: argparse.Namespace) -> int:
    root = find_root()
    d = drift(root, Path(args.fil).resolve())
    print(json.dumps(d, ensure_ascii=False) if args.json else som_text_drift(d))
    return 0
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_rost.py tests/test_rost_drift.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/bok/rost.py tests/test_rost_drift.py
git commit -m "feat: bok rost drift mäter kapitlet mot rösten och AI-genomsnittet"
```

---

### Task 5: `bok rost urval`

**Files:**
- Modify: `src/bok/rost.py` (funktionen `urval` och underkommandot)
- Test: `tests/test_rost_urval.py`

**Interfaces:**
- Consumes: `krav_modul`, `texter` (Task 3); `bok.graf.scenkort(root, kapitel) -> dict` (kastar `GrafFel`, en `BokFel`, när scenkortet saknas eller inte är ifyllt).
- Produces: `urval(root: Path, kapitel: int, antal: int = 3) -> list[Path]`; CLI `bok rost urval --kapitel N [--antal 3] [--json]` som skriver en sökväg per rad, relativ till bokens rot (med `--json`: `{"kapitel": N, "lage": str|None, "stycken": [sökvägar]}`).

- [ ] **Step 1: Write the failing tests**

`tests/test_rost_urval.py`:

```python
import json

import pytest

from bok.cli import main
from bok.graf import GrafFel
from bok.mallar import lagg_till
from bok.rost import urval
from helpers import skriv


def scenkort(root, lage):
    rad = f"lage: {lage}\n" if lage else ""
    skriv(root, "bok/plot/kapitel/kapitel-03.md", f"---\nkapitel: 3\n{rad}godkand: true\n---\n\n# Kapitel 3\n")


def stycke(root, namn, lage, datum):
    huvud = f"lage: {lage}\n" if lage else ""
    huvud += f"datum: {datum}\n" if datum else ""
    skriv(root, f"bok/stil/provbank/{namn}.md", f"---\n{huvud}---\nText.\n")


@pytest.fixture
def labb(bok):
    lagg_till(bok, "rostlabb")
    stycke(bok, "a", "stilla", "2026-10-01")
    stycke(bok, "b", "tryck", "2026-10-03")
    stycke(bok, "c", "tryck", "2026-10-02")
    stycke(bok, "d", "tryck", None)
    stycke(bok, "e", "tryck", "2026-10-03")
    return bok


def test_valjer_lage_nyast_forst_och_namn_vid_lika(labb):
    scenkort(labb, "tryck")
    assert [p.name for p in urval(labb, 3)] == ["b.md", "e.md", "c.md"]
    assert [p.name for p in urval(labb, 3, antal=10)] == ["b.md", "e.md", "c.md", "d.md"]


def test_utan_lage_valjs_ur_hela_banken(labb):
    scenkort(labb, None)
    assert [p.name for p in urval(labb, 3, antal=2)] == ["b.md", "e.md"]


def test_lage_som_ingen_har_faller_tillbaka_pa_hela_banken(labb):
    scenkort(labb, "drom")
    assert len(urval(labb, 3, antal=5)) == 5


def test_trasigt_huvud_i_banken_kraschar_inte(labb):
    skriv(labb, "bok/stil/provbank/f.md", "---\nlage: tryck\nText utan slut på huvudet.\n")
    scenkort(labb, "tryck")
    assert "f.md" not in [p.name for p in urval(labb, 3, antal=10)]  # utan lage väljs det inte för tryck
    scenkort(labb, None)
    assert "f.md" in [p.name for p in urval(labb, 3, antal=10)]


def test_saknat_scenkort_ar_fel(labb):
    with pytest.raises(GrafFel):
        urval(labb, 3)


def test_cli_urval(labb, capsys):
    scenkort(labb, "tryck")
    assert main(["rost", "urval", "--kapitel", "3", "--antal", "2"]) == 0
    assert capsys.readouterr().out.splitlines() == ["bok/stil/provbank/b.md", "bok/stil/provbank/e.md"]
    assert main(["rost", "urval", "--kapitel", "3", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["lage"] == "tryck"
    assert main(["rost", "urval", "--kapitel", "9"]) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_rost_urval.py -v`
Expected: FAIL med `ImportError: cannot import name 'urval'`.

- [ ] **Step 3: Implement urval**

Lägg till importen överst i `src/bok/rost.py`:

```python
from bok.graf import scenkort
```

Lägg till före `register`:

```python
def urval(root: Path, kapitel: int, antal: int = 3) -> list[Path]:
    """Stycken ur provbanken med scenkortets lage, nyaste först (datum), sedan filnamn.
    Saknar scenkortet lage, eller har inget stycke det, väljs ur hela banken."""
    krav_modul(root)
    lage = scenkort(root, kapitel).get("lage")
    bank = texter(root, "provbank")
    if lage:
        bank = [b for b in bank if b[1].get("lage") == lage] or bank
    bank.sort(key=lambda b: b[0].name)
    bank.sort(key=lambda b: str(b[1].get("datum") or ""), reverse=True)
    return [p for p, _, _ in bank[:antal]]
```

Lägg till i `register`, efter `drift`:

```python
    c = r.add_parser("urval", help="stycken ur provbanken som Writer läser inför kapitlet")
    c.add_argument("--kapitel", type=int, required=True)
    c.add_argument("--antal", type=int, default=3)
    c.add_argument("--json", action="store_true", help="maskinläsbart, för skillen")
    c.set_defaults(func=_kor_urval)
```

Och sist i filen:

```python
def _kor_urval(args: argparse.Namespace) -> int:
    root = find_root()
    valda = [p.relative_to(root).as_posix() for p in urval(root, args.kapitel, args.antal)]
    if args.json:
        lage = scenkort(root, args.kapitel).get("lage")
        print(json.dumps({"kapitel": args.kapitel, "lage": lage, "stycken": valda}, ensure_ascii=False))
    else:
        print("\n".join(valda))
    return 0
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_rost.py tests/test_rost_drift.py tests/test_rost_urval.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/bok/rost.py tests/test_rost_urval.py
git commit -m "feat: bok rost urval väljer provstycken till Writer efter scenkortets läge"
```

---

### Task 6: Låsta ställen i `bok validate`

**Files:**
- Modify: `src/bok/validera.py` (nya funktioner och kontrollen i `_kor`)
- Test: `tests/test_validera_pekningar.py`

**Interfaces:**
- Consumes: `bok.tics.las_kapitel`, `validera._nummer`, `bok.rot.BokFel`.
- Produces: `lasta_stallen(root: Path, kapitel: int) -> list[str]` (normaliserade citat under `## Lever`), `andrade_stallen(text: str, citat: list[str]) -> list[str]`; `bok validate` skriver `BLOCKERANDE` och returnerar 1 när ett låst citat saknas.

- [ ] **Step 1: Write the failing tests**

`tests/test_validera_pekningar.py`:

```python
from bok.cli import main
from bok.validera import andrade_stallen, lasta_stallen
from helpers import skriv

PEK = ('# Pekningar\n\n## Lever\n- "Han räknade stolarna två gånger innan han satte sig."\n'
       '- “Det var  inte\nhennes sak.”\n\n## Dött\n- "Tystnaden lade sig."\n\n'
       '## Upplåst\n- "Gammalt citat som inte längre gäller."\n')


def test_lasta_stallen_laser_bara_lever(bok):
    skriv(bok, "bok/stil/pekningar/kapitel-03.md", PEK)
    assert lasta_stallen(bok, 3) == ["Han räknade stolarna två gånger innan han satte sig.",
                                     "Det var inte"]
    assert lasta_stallen(bok, 4) == []


def test_andrade_stallen_normaliserar_blanktecken_och_citattecken():
    text = "Hon tittade upp.\nHan räknade stolarna två gånger\ninnan han satte sig. ”Nej.”"
    assert andrade_stallen(text, ["Han räknade stolarna två gånger innan han satte sig.", '"Nej."']) == []
    assert andrade_stallen("Han räknade stolarna en gång.", ["Han räknade stolarna två gånger."]) == [
        "Han räknade stolarna två gånger."]


def test_validate_stoppar_andrat_last_stalle(bok, capsys):
    skriv(bok, "bok/stil/pekningar/kapitel-03.md",
          '## Lever\n- "Han räknade stolarna två gånger innan han satte sig."\n')
    skriv(bok, "manuskript/kapitel-03.md", "Han räknade stolarna en gång och satte sig.\n")
    assert main(["validate", "manuskript/kapitel-03.md"]) == 1
    assert "BLOCKERANDE" in capsys.readouterr().out
    skriv(bok, "manuskript/kapitel-03.md", "Han räknade stolarna två gånger innan han satte sig.\n")
    assert main(["validate", "manuskript/kapitel-03.md"]) == 0


def test_tom_eller_trasig_pekningsfil_kraschar_inte(bok, capsys):
    skriv(bok, "bok/stil/pekningar/kapitel-03.md", "bara text utan rubriker\n- \"inte under Lever\"\n")
    skriv(bok, "manuskript/kapitel-03.md", "Hon gick.\n")
    assert main(["validate", "manuskript/kapitel-03.md"]) == 0
    (bok / "bok/stil/pekningar/kapitel-03.md").write_bytes(b"## Lever\n- \"\xff\xfe\"\n")
    assert main(["validate", "manuskript/kapitel-03.md"]) == 0
    assert "kunde inte läsas" in capsys.readouterr().out
```

Obs: det andra citatet i `PEK` står på två rader; bara första raden hör till listpunkten, så det normaliserade citatet blir `Det var inte` (citattecknet stängs aldrig på raden och tas därför inte bort). Testet låser det beteendet: ett citat ska stå på en rad.

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_validera_pekningar.py -v`
Expected: FAIL med `ImportError: cannot import name 'andrade_stallen'`.

- [ ] **Step 3: Implement**

I `src/bok/validera.py`, ändra importraden för `bok.rot`:

```python
from bok.rot import BokFel, find_root
```

Lägg till efter `_nummer`:

```python
_CITATTECKEN = str.maketrans({"“": '"', "”": '"', "„": '"', "«": '"', "»": '"', "’": "'", "‘": "'"})


def _norm(s: str) -> str:
    return " ".join(s.translate(_CITATTECKEN).split())


def lasta_stallen(root: Path, kapitel: int) -> list[str]:
    """Citaten under ## Lever i bok/stil/pekningar/kapitel-NN.md, normaliserade. Inga om filen saknas."""
    katalog = root / "bok" / "stil" / "pekningar"
    path = next((p for p in sorted(katalog.glob("kapitel-*.md")) if _nummer(p) == kapitel), None)
    if path is None:
        return []
    ut, i_lever = [], False
    for rad in las_kapitel(path).splitlines():
        if rad.startswith("## "):
            i_lever = rad[3:].strip().lower() == "lever"
            continue
        if i_lever and rad.lstrip().startswith("- "):
            citat = _norm(rad.lstrip()[2:])
            if len(citat) >= 2 and citat[0] == citat[-1] == '"':
                citat = citat[1:-1].strip()
            elif citat.startswith('"'):
                citat = citat[1:].strip()
            if citat:
                ut.append(citat)
    return ut


def andrade_stallen(text: str, citat: list[str]) -> list[str]:
    """Låsta citat som inte längre står ordagrant i texten (blanktecken och citattecken normaliserade)."""
    ren = _norm(text)
    return [c for c in citat if _norm(c) not in ren]
```

I `_kor`, ersätt raden `stopp = stopp or bool(traffar) or bool(forlagetraffar)` med:

```python
        andrade = []
        if (n := _nummer(fil)):
            try:
                andrade = andrade_stallen(text, lasta_stallen(root, n))
            except BokFel as exc:
                print(f"  Pekningarna för kapitlet kunde inte läsas: {exc}")
        for citat in andrade:
            print(f'  BLOCKERANDE: låst ställe står inte längre ordagrant i kapitlet '
                  f'(bok/stil/pekningar/): "{citat}"')
        stopp = stopp or bool(traffar) or bool(forlagetraffar) or bool(andrade)
```

Och ändra villkoret för "Inga anmärkningar." till:

```python
        if not traffar and not forlagetraffar and not andrade and not nya and not varningar:
```

(Den befintliga raden `if (n := _nummer(fil)) and (d := datum.get(n)) is not None and personer:` längre ned fungerar som förut.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_validera_pekningar.py tests/test_validera.py tests/test_validera_tid.py -v`
Expected: PASS. `test_andrade_stallen…` passerar eftersom `”Nej.”` normaliseras till `"Nej."`.

- [ ] **Step 5: Commit**

```bash
git add src/bok/validera.py tests/test_validera_pekningar.py
git commit -m "feat: bok validate stoppar kapitel där ett låst ställe har ändrats"
```

---

### Task 7: Ramverket – skill, process, verktyg och roller

**Files:**
- Modify: `src/bok/data/genererat/claude/skills/bok/SKILL.md`
- Modify: `src/bok/data/genererat/claude/bok/process.md`
- Modify: `src/bok/data/genererat/claude/bok/verktyg.md`
- Modify: `src/bok/data/genererat/claude/agents/bok-writer.md`, `bok-plot-arkitekt.md`, `bok-idekritiker.md`, `bok-sprakgranskare.md`, `bok-redaktor.md`, `bok-forlaggare.md`
- Test: `tests/test_innehall.py`

**Interfaces:**
- Consumes: kommandona från Task 1, 3–6 (`bok fron --klass rostdrag …`, `bok rost profil|drift|urval`, `bok validate`) och filerna från Task 2.
- Produces: texterna som Claude följer i en bok med modulen.

- [ ] **Step 1: Write the failing test**

Lägg sist i `tests/test_innehall.py`:

```python
def test_ramverket_2_5():
    skill = _las("skills/bok/SKILL.md")
    assert "## Röstlabbet" in skill
    labb = skill.split("## Röstlabbet", 1)[1].split("\n## ", 1)[0]
    for fras in ("`rostlabb`", "uppdraget **formprov**", "uppdraget **röstprov**", "bok fron --klass rostdrag",
                 "kontroll", "korsa", "mutera", "förstärk", "vild", "bok/stil/provbank/", "bok/stil/kontroll/",
                 "## Formlag", "bok/stil/pekningar/kapitel-NN.md", "## Upplåst", "Välj aldrig åt"):
        assert fras in labb, fras
    assert "bok mall rostlabb" in skill.split("## Fritt samtal", 1)[1].split("\n## ", 1)[0]
    rader = {r.split("|")[1].strip(): r for r in skill.splitlines() if r.startswith("| ")}
    assert "bok rost drift" in rader["Granskning"]
    assert "Pekning" in rader["Revision"]
    assert "receptet" in rader["Aktgräns"]

    process = _las("bok/process.md")
    for fras in ("## Röstlabbet", "`vagar`", "`lage`", "bok rost urval", "bok rost drift", "Mest levande",
                 "| Writer (röstprov) |", "| Plot-arkitekt (formprov) |", "| Idékritiker (röstprov) |"):
        assert fras in process, fras
    assert "bok rost" in _las("bok/verktyg.md")

    writer = _las("agents/bok-writer.md")
    for fras in ("## Uppdrag: röstprov", "bok rost urval --kapitel N", "Dött", "Lever"):
        assert fras in writer, fras
    plot = _las("agents/bok-plot-arkitekt.md")
    assert "## Uppdrag: formprov" in plot and "`vagar`" in plot and "`lage`" in plot
    kritik = _las("agents/bok-idekritiker.md")
    for fras in ("## Uppdrag: röstprov", "**Pastisch:**", "**AI-genomsnitt:**", "**Receptet:**", "**Eget:**"):
        assert fras in kritik, fras
    for roll in ("sprakgranskare", "redaktor"):
        text = _las(f"agents/bok-{roll}.md")
        assert "## Mest levande" in text and "## Mest döda" in text, roll
        assert "bok/stil/pekningar/kapitel-NN.md" in text, roll
    assert "bok rost drift" in _las("agents/bok-sprakgranskare.md")
    assert "`vagar`" in _las("agents/bok-redaktor.md")
    assert "## Formlag" in _las("agents/bok-forlaggare.md")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_innehall.py::test_ramverket_2_5 -v`
Expected: FAIL på `## Röstlabbet`.

- [ ] **Step 3: SKILL.md**

a) I tabellen under `## Fritt samtal`, ersätt raden

```
  | hur det ska låta, texter hon gillar | Stilverkstaden nedan |
```

med

```
  | hur det ska låta, texter hon gillar | Stilverkstaden nedan, eller Röstlabbet om `rostlabb` står i `moduler` i `bok.toml` |
```

b) I punkten **Genren styr tillvalen.**, lägg till sist i punkten:

```
 Pratar hon om ett eget språk, litterär höjd eller att texten låter som AI: föreslå `bok mall rostlabb` (Röstlabbet).
```

c) Lägg ett nytt avsnitt direkt före `## Karaktärsverkstaden`:

```markdown
## Röstlabbet
Bara när `rostlabb` står i `moduler` i `bok.toml`; då ersätter labbet stilverkstaden. Rösten och formen hittas genom att författaren väljer bland varianter, inte genom att skriva. Välj aldrig åt henne och rekommendera ingen variant. Hur filerna ser ut står i `bok/stil/labb/README.md`.

**Två sorters prov.** Formprov: en skiss av första akten på en sida (`bok-plot-arkitekt`, uppdraget **formprov**). Röstprov: provscenerna i `bok/stil/labb/provscener.md`, 250–350 ord var, en stilla och en under tryck (`bok-writer`, uppdraget **röstprov**). Föreslå formen först, eftersom formen ofta bestämmer rösten; hon kan börja med rösten eller hoppa över formen.

1. **Rama in.** Fråga efter förebilder (texterna sparas i `bok/stil/exempel/` som i stilverkstaden) och vad boken inte får låta som. Skriv provscenerna och få hennes ja.
2. **Frön.** Kör `bok fron --klass rostdrag --klass kalla --klass formgrepp --antal 8 --json --spara bok/stil/labb`.
3. **Recept.** Fyra recept med 3–6 drag var, varje drag med sin källa (en förebild eller ett frö): två utgår från förebilderna med ett frö var, två huvudsakligen från frön. Formprov bygger på `formgrepp`, röstprov på `rostdrag` och `kalla`.
4. **Varianter.** Starta fyra instanser parallellt, ett recept var (A–D), och en femte utan recept: kontrollen. Kontrollen får bara provet och premissen, aldrig `bok/stil/rost.md`.
5. **Kritik.** Starta `bok-idekritiker` med uppdraget **röstprov** och generationsfilen.
6. **Visa och peka.** Visa A–D och sist kontrollen, märkt som kontroll. Låt henne peka fritt: vad lever, vad är dött. Skriv recepten, texterna, kritiken och pekningarna i `bok/stil/labb/gen-NN.md` (röst) eller `bok/stil/labb/form-NN.md` (form).
7. **Nästa generation.** Fyra nya recept ur pekningarna: korsa (levande drag från två varianter), mutera (byt ett drag mot ett nytt frö), förstärk (driv ett levande drag längre) och vild (ett helt nytt frö). Ny kontroll bara när provet byts. Efter femte generationen: fråga om rösten håller på att sätta sig eller om provscenen ska bytas.
8. **Klart** när hon säger att det är boken. Efter hennes ja:
   - skriv om `bok/stil/rost.md` med rubrikerna `## Recept`, `## Antiröst` och `## Form`,
   - spara de godkända provstyckena i `bok/stil/provbank/` och röstprovens kontroller i `bok/stil/kontroll/`, en fil per stycke med `lage`, `kalla` och `datum` i huvudet,
   - skriv formlagen under `## Formlag` i `bok/koncept/form.md` om formprov gjorts: vad formen måste göra, vad den aldrig får göra och varför,
   - skriv en rad i `bok/beslut.md` med länk till generationsfilen.

**Pekning.** Före första revisionen av ett kapitel: visa granskarnas avsnitt Mest levande och Mest döda och fråga vad som lever och vad som är dött. Säger hon "kör": gå vidare. Annars skriv `bok/stil/pekningar/kapitel-NN.md` med `## Lever` och `## Dött`, ett citat per rad (`- "…"`), ordagrant ur kapitlet. Det som lever är låst: `bok validate` stoppar om det ändrats. Vill hon låsa upp något: flytta raden till `## Upplåst`. Ge pekningsfilen till `bok-writer` med fynden. Föreslå levande ställen till provbanken (högst 15 stycken).

**Aktgränsen.** Fråga om receptet håller. Vill hon revidera: kör en generation på en scen ur akten, skriv om receptet och formlagen efter hennes ja, och rensa provbanken tillsammans med henne.
```

d) I tabellen under `## Skriva kapitel`:
- Raden **Granskning**: lägg till efter första meningen: `Med modulen \`rostlabb\`: kör också \`bok rost drift\` på kapitlet och ge varningarna till \`bok-sprakgranskare\`.`
- Raden **Revision**: lägg till sist: `Med modulen \`rostlabb\`, före första revisionen: Pekning (se Röstlabbet).`
- Raden **Aktgräns**: lägg till sist: `Med modulen \`rostlabb\`: fråga om receptet håller (se Röstlabbet).`

- [ ] **Step 4: process.md och verktyg.md**

I `bok/process.md`, tabellen under `## Förberedelse`, ändra cellen för Röst till `ifylld och godkänd i stilverkstaden eller Röstlabbet`.

I tabellen under `## Vad rollerna läser`, lägg till tre rader sist:

```
| Writer (röstprov) | provet ur `bok/stil/labb/provscener.md`, receptet och premissen; kontrollen bara provet och premissen; aldrig `bok/stil/exempel/` |
| Plot-arkitekt (formprov) | receptet, premissen, `bok/plot/struktur.md` och kapitelplanen om den finns |
| Idékritiker (röstprov) | generationsfilen och `bok/stil/exempel/` |
```

och lägg till sist i Writer-raden: `; med modulen \`rostlabb\` också styckena ur \`bok rost urval --kapitel N\` och \`bok/stil/pekningar/kapitel-NN.md\``.

Lägg ett nytt avsnitt efter `## Vägval`:

```markdown
## Röstlabbet

Modulen `rostlabb` (`bok mall rostlabb`). Labbet ersätter stilverkstaden: formprov (`bok-plot-arkitekt`, uppdrag *formprov*) och röstprov (`bok-writer`, uppdrag *röstprov*) i generationer med fyra recept och en kontroll utan recept, kritik från `bok-idekritiker` (uppdrag *röstprov*) och författarens pekningar. Resultatet är `bok/stil/rost.md` i receptform, provbanken `bok/stil/provbank/`, kontrollerna `bok/stil/kontroll/` och formlagen i `bok/koncept/form.md`.

I skrivloopen, med modulen:

- scenkortet har `vagar` (vad kapitlet vågar) och `lage` (`stilla` eller `tryck`),
- Writer läser stycken ur provbanken enligt `bok rost urval --kapitel N`,
- steg 4 kör också `bok rost drift manuskript/kapitel-NN.md`; varningarna stoppar inget och går till Språkgranskaren,
- granskarnas rapporter har avsnitten Mest levande och Mest döda,
- före första revisionen pekar författaren ut levande och döda ställen i `bok/stil/pekningar/kapitel-NN.md`; det som lever är låst, `bok validate` stoppar om det ändrats, och granskarna får inte kräva ändringar i det eller sätta under 8 på grund av det,
- vid aktgränsen läser Förläggaren mot formlagen, och receptet får revideras.
```

I `bok/verktyg.md`, lägg till efter raden för `bok tics`:

```
| `bok rost profil` | provbankens profil: meningslängd, repliker, skiljetecken, pronomenstart (modulen `rostlabb`) |
| `bok rost drift manuskript/kapitel-NN.md` | kapitlet mot rösten (provbanken) och AI-genomsnittet (kontrollen) med Burrows Delta, mått utanför röstens spridning och pastisch; varningar, stoppar inget |
| `bok rost urval --kapitel N` | provstycken som Writer läser inför kapitlet, efter scenkortets `lage` |
```

och ändra raden för `bok validate` så att den börjar `förbjudna namn, förlagornas namn, låsta ställen ur pekningarna och tidsfel i grafen stoppar (exitkod 1)`.

- [ ] **Step 5: Rollerna**

`agents/bok-writer.md`:
- Under `## Läs först, i den här ordningen`, lägg till sist: `10. Med modulen \`rostlabb\`: kör \`bok rost urval --kapitel N\` och läs styckena. De visar hur boken låter; återge aldrig formuleringar ur dem.`
- Under `## Revidera`, lägg till sist: `- Finns \`bok/stil/pekningar/kapitel-NN.md\`: skriv om det som står under Dött först. Det som står under Lever får inte ändras med ett tecken.`
- Lägg ett nytt avsnitt före `## Innan du lämnar`:

```markdown
## Uppdrag: röstprov
Röstlabbet. Du får ett prov ur `bok/stil/labb/provscener.md` och ett recept, eller inget recept (kontrollen). Du skriver inget i manuset och kör inte `bok validate` eller `bok tics`. I det här uppdraget läser du bara `bok/roller/writer.local.md`, provet och `bok/koncept/premiss.md`. Läs aldrig `bok/stil/exempel/` eller `bok/stil/rost.md`.
1. Skriv provscenen, 250–350 ord, så att varje drag i receptet märks. Utan recept: skriv den som du själv skulle skriva den.
2. Returnera texten och en rad per drag om var det syns. Spara ingenting; skillen sparar varianterna.
```

`agents/bok-plot-arkitekt.md`:
- Under `## Uppdrag: scenkort`, lägg till ett stycke sist: `Med modulen \`rostlabb\`: fyll i \`vagar\` med det du tror mest på (ett formbrott, något som undanhålls, en tidsförskjutning eller en moralisk obekvämhet) och föreslå två alternativ i ditt svar. Sätt \`lage\` till \`stilla\` eller \`tryck\` efter kapitlets tyngdpunkt.`
- Lägg ett nytt avsnitt före `## Regler`:

```markdown
## Uppdrag: formprov
Röstlabbet. Du får ett recept med formgrepp, eller inget recept (kontrollen). Läs `bok/koncept/premiss.md`, `bok/plot/struktur.md` och `bok/plot/kapitelplan.md` om den finns. Skriv en skiss av första akten på högst en sida så att formen syns: hur kapitlen ser ut, vad som utelämnas, hur tiden rör sig. Utan recept: den form du själv skulle välja. Returnera skissen; spara ingenting.
```

`agents/bok-idekritiker.md`, nytt avsnitt före `## Regler`:

````markdown
## Uppdrag: röstprov
Röstlabbet. Läs generationsfilen du får och förebildernas texter i `bok/stil/exempel/`. Gå igenom varianterna A–D var för sig:
- **Pastisch:** för nära en enda förebild. Citera det som är lånat.
- **AI-genomsnitt:** för likt kontrollen. Citera.
- **Receptet:** drag som inte märks i texten.
- **Eget:** det varianten gör som ingen annan gör.

Inga betyg och ingen rangordning. Returnera en rubrik per variant:

```
### A
**Pastisch:** …
**AI-genomsnitt:** …
**Receptet:** …
**Eget:** …
```
````

`agents/bok-sprakgranskare.md`:
- Under `## Läs först`, lägg till sist: `5. Med modulen \`rostlabb\`: rapporten från \`bok rost drift\` som skillen ger dig, och \`bok/stil/pekningar/kapitel-NN.md\` om den finns.`
- Under `## Bedöm`, lägg till sist i punkten **rost**: ` Med \`rostlabb\`: följer kapitlet receptet och undviker antirösten i \`bok/stil/rost.md\`? Att kapitlet ligger närmare AI-genomsnittet än rösten är ett fynd att citera, inte ett betyg i sig.`
- Lägg till efter `## Bedöm`-listan: `Ställen under Lever i \`bok/stil/pekningar/kapitel-NN.md\` är låsta: kommentera dem gärna, men kräv inga ändringar i dem och sätt inget betyg under 8 på grund av dem.`
- I rapportblocket under `## Rapport`, lägg till sist i blocket (efter `## Det som fungerar` och dess punkt):

```
## Mest levande
- "citat": varför

## Mest döda
- "citat": varför
```

`agents/bok-redaktor.md`:
- Under `## Bedöm`, lägg till sist i punkten **struktur**: ` Har scenkortet \`vagar\`: gör kapitlet det det lovar?`
- Samma mening om låsta ställen som för Språkgranskaren, efter raden `Använd …anti-monster.md…`.
- Samma två avsnitt `## Mest levande` och `## Mest döda` sist i rapportblocket.

`agents/bok-forlaggare.md`:
- Under `## Läs först`, lägg till sist: `6. Med modulen \`rostlabb\`: rubriken \`## Formlag\` i \`bok/koncept/form.md\`.`
- Under `## Bedöm`, lägg till sist: `- Med en formlag: bär formen fortfarande stoffet, eller följs den bara? Säg om formlagen behöver skrivas om.`

- [ ] **Step 6: Run tests to verify they pass**

Run: `uv run pytest tests/test_innehall.py -v`
Expected: PASS, inklusive `test_ramverket_2_5`, `test_ramverkets_kommandon_finns` (`bok rost` finns nu) och `test_inga_dinglande_sokvagar`.

- [ ] **Step 7: Run the full suite**

Run: `uv run pytest -q`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add src/bok/data/genererat tests/test_innehall.py
git commit -m "feat: Röstlabbet i skillen, processen och rollerna"
```

---

### Task 8: Dokumentation och changelog

**Files:**
- Modify: `README.md`, `docs/hur-det-fungerar.md`, `docs/utveckla-och-releasa.md`, `CHANGELOG.md`

**Interfaces:**
- Consumes: allt ovan.
- Produces: texter för den som skriver och den som bygger.

- [ ] **Step 1: README.md**

- Under `## Hur det fungerar`, punkt 1, lägg till sist: ` Vill boken mer än ett hantverksmässigt språk söker **Röstlabbet** (\`bok mall rostlabb\`) bokens röst och form genom att ni väljer bland varianter, och håller den med mätbara ankare.`
- I tabellen `## Kommandon`: lägg `rostlabb` sist i listan för `bok mall [modul]`, och en rad efter `bok tics`: `| \`bok rost\` | röstens profil, ett kapitels drift mot rösten och AI-genomsnittet, och provstycken till Writer (modulen rostlabb) |`

- [ ] **Step 2: docs/hur-det-fungerar.md**

Lägg ett avsnitt efter `### Vägval` (före `## Rollerna`):

```markdown
### Röstlabbet

För böcker som vill mer än ett korrekt språk: `bok mall rostlabb`. Labbet ersätter stilverkstaden. Ni skriver inte själva; ni väljer. Claude skriver fyra varianter av samma prov, var och en efter ett recept av drag som lånas från förebilder ni valt eller från slumpade frön (drag på meningsnivå, formgrepp, texter utanför litteraturen som protokoll och liturgi), och en femte utan recept som visar hur AI låter utan riktning. Ni pekar ut vad som lever och vad som är dött, och nästa generation korsar, muterar och förstärker det. Formprovet söker bokens form i en skiss av första akten; röstprovet söker rösten i två provscener.

När ni känner igen boken blir rösten ett recept i `bok/stil/rost.md`, provstyckena en provbank och formen en formlag i `bok/koncept/form.md`. Under skrivandet läser Writer några provstycken inför varje kapitel, `bok rost drift` varnar när ett kapitel ligger närmare AI-genomsnittet än rösten, och ställen ni pekat ut som levande låses så att granskningen inte slipar bort dem.
```

- [ ] **Step 3: docs/utveckla-och-releasa.md**

I stycket "Moduler i `src/bok/` i korthet", lägg till efter `validera` och `tics`: `, \`rost\` (Röstlabbets mått: profil, drift och urval)`, och `fron` om det saknas i listan.

- [ ] **Step 4: CHANGELOG.md**

Under `## [Unreleased]`:

```markdown
### Lagt till
- Röstlabbet (`bok mall rostlabb`): sök bokens röst och form genom att välja bland varianter i generationer, med recept av drag från förebilder och slumpade frön, en kontroll som visar AI-genomsnittet och pekningar på det som lever och det som är dött. Resultatet blir ett recept i `rost.md`, en provbank och en formlag.
- `bok rost profil`, `bok rost drift` och `bok rost urval`: röstens profil, ett kapitel mätt mot rösten och AI-genomsnittet (och pastisch), och provstycken som Writer läser inför kapitlet.
- `bok fron` har klasserna `rostdrag`, `formgrepp` och `kalla`.
- Scenkortet har fälten `vagar` (vad kapitlet vågar) och `lage` (stilla eller under tryck).

### Ändrat
- Med Röstlabbet pekar författaren ut levande och döda ställen efter första granskningen. Levande ställen är låsta: `bok validate` stoppar kapitlet om de ändrats, och granskarna får inte kräva ändringar i dem. Granskarnas rapporter har avsnitten Mest levande och Mest döda.
```

- [ ] **Step 5: Run the full suite**

Run: `uv run pytest -q`
Expected: PASS (inklusive `test_changelog.py` och `test_readme_utan_arv`).

- [ ] **Step 6: Commit**

```bash
git add README.md docs/hur-det-fungerar.md docs/utveckla-och-releasa.md CHANGELOG.md
git commit -m "docs: Röstlabbet i README, hur det fungerar och changelog"
```

---

## Efter planen

Manuellt prov (spec avsnitt 8), inte en del av den automatiska sviten: i en provbok med modulen påslagen, kör två generationer av labbet (formprov och röstprov) och ett kapitel genom loopen med pekning och `bok rost drift`. Releasen (versionshöjning till 2.5.0) görs med skillen `release`.
