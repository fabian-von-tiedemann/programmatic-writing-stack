# CLAUDE.md — Stående instruktioner för *{{BOK_TITEL}}*

Läs detta först varje session. Pekare till djupare instruktioner ligger längst ner.

## Vad detta är

{{KORT_BESKRIVNING}} — *{{BOK_TITEL}}* — en {{GENRE}} som utspelar sig {{TIDSPERIOD_OCH_PLATS}}. {{LANGD_OCH_STRUKTUR}}.

**Ambition:** {{AMBITION}}. **{{KVALITETSRIBBA}} på alla axlar** är ribban.

## De distinguishing features

1. **{{DISTINGUISHING_FEATURE_1}}** — {{BESKRIVNING_1}}
2. **{{DISTINGUISHING_FEATURE_2}}** — {{BESKRIVNING_2}}
3. **{{DISTINGUISHING_FEATURE_3}}** — {{BESKRIVNING_3}}
4. **{{DISTINGUISHING_FEATURE_4}}** — {{BESKRIVNING_4}}

(Lägg till eller ta bort efter behov — minst 2, max 5.)

---

## Process — hur vi jobbar

Hela förbättringsloopen FAS 0-9 finns i **`.context/process.md`**. Läs den för:
- Varje fas + alla obligatoriska steg
- När man dispatchar respektive roll
- Hårda regler om processen (aldrig hoppa över steg, NAGELFAREN/förläggare vetoröst, etc.)

**Snabb sammanfattning av rollerna (13 totalt — komplett ramverk):**

| Roll | Fas | Brief |
|---|---|---|
| PLOT-ARKITEKT | FAS 0 | `.context/roles/plot-arkitekt.md` |
| RESEARCHER | FAS 0 + on-demand | `.context/roles/researcher.md` |
| WRITER | FAS 2 | `.context/roles/writer.md` |
| REDAKTÖR | FAS 3 | `.context/roles/redaktor.md` |
| PROSA-STÄD | FAS 3 (BLOCKERANDE) | `.context/roles/prosa-stad.md` |
| DIALOG-COACH | FAS 3 (POV-veto) | `.context/roles/dialog-coach.md` |
| NAGELFAREN | FAS 3 (veto) | `.context/roles/nagelfaren.md` |
| FÖRLÄGGARE | FAS 4 (A/B/C) | `.context/roles/forlaggare.md` |
| SENSITIVITY-LÄSARE | FAS 4 (publikation-veto) | `.context/roles/sensitivity-lasare.md` |
| GRAF-VAKT | LÖPANDE | `.context/roles/graf-vakt.md` |
| VÄRLDSBYGGARE | Före/efter bok | `.context/roles/varldsbyggare.md` |
| AUDIOBOOK-DIREKTÖR | FAS 8 | `.context/roles/audiobook-direktor.md` |
| MARKNADSFÖRARE | FAS 9 | `.context/roles/marknadsforare.md` |

NAGELFAREN är adversarial meta-granskare — granskar inte boken, granskar REDAKTÖRENS RAPPORT. Default-betyg är **7**, inte 9.

**Vetoröster:** NAGELFAREN (på redaktör-rapport), Förläggare (A/B/C), Dialog-coach (POV-axeln), Sensitivity-läsare (publikation), Prosa-städ (BLOCKERANDE för fortsatt FAS 3).

---

## POV-karaktärer

{{POV_KARAKTARER}} — fyll i namn + en mening per. T.ex.:
- **Karaktär A** — yrke, åldersgrupp, geografisk hemvist, drivkraft i en mening
- **Karaktär B** — ...

Per POV finns `.context/story-graph/character-deepening/char-<id>.md` som är writer-agentens ledstjärna.

---

## Canon — fakta-fällor + verkliga personer

Allt fakta-relaterat (geografi-fällor, fordon, tider, verkliga personer-blacklist, verkliga företag) i **`.context/canon.md`**.

**Användarens hårda no:s (anpassa till boken):**
- Logiska tabbar (geografi, transport, tider)
- Författare-på-promenad-känsla (strössla detaljer som inte tjänar något)
- Fakta-fel som varje insider ser
- Verkliga personer i fiktionen (bygg blacklist)

---

## Tools — mekaniska hjälpmedel

Alla scripts + pipeline-användning i **`.context/tools.md`**:
- `scripts/books-annotations.sh` — hämtar läsarens noter från Apple Books
- `scripts/grep-tics.sh` — frekvens-pass mot tics-katalog
- `scripts/render-manuscript.py` + `validate-manuscript.py` + `tag-manuscript.py` — layered markup-pipeline
- `scripts/graph-query.py` — query-lager mot story-graph

Validator-rapporter blir input till redaktör, prosa-städ och NAGELFAREN som mekaniskt bevis.

---

## Kunskapsgrafen är canon

`.context/story-graph/` är romanens canon. **Den ska vara levande** — uppdateras varje gång nya detaljer dyker upp eller fixas.

Filer:
- `characters.json`, `organizations.json`, `locations.json`, `events.json`
- `secrets.json`, `relationships.json`, `timeline.json`, `documents.json`
- `objects.json` (bilar, telefoner, kläder med funktion)
- `threads.md`, `knowledge-matrix.md`, `themes.md`
- `consistency-checks.md` (kvalitetsspärrar)
- `style-guide.md` (prosastilens regler)

**Konventioner:**
- IDs: `kebab-case` med typ-prefix (`char-<namn>`, `loc-<plats>`, `evt-<händelse>`, `obj-<objekt>`, `org-<organisation>`)
- Datum: ISO 8601 (`YYYY-MM-DDTHH:MM`)
- Alltid namnet — aldrig "den lilla gränden" eller "den gamla mannen"

Detaljerad uppdaterings-disciplin: se `.context/process.md` FAS 6.

---

## Manuskript

`manuskript/` innehåller alla kapitel:
- `prolog.md`, `kapitel-NN.md`
- Om layered markup införd för ett kapitel: `kapitel-NN.draft.md` är källan, `kapitel-NN.md` är renderad output

Kapitelmål: {{KAPITEL_LANGD}} ord per kapitel (förslag: 3000-3500 för thriller, 2500-3000 för litterär).

---

## Användarens preferenser

- Vill ha **{{AMBITION}}**
- Vill ha **{{KANSLA}}** (t.ex. "maktspels-känsla a la House of Cards")
- Vill ha **något nytt** (distinguishing features ovan)
- Vill **inte att det blir pang på** — atmosfär krävs
- Vill att **redaktören är nagelfaren** — ingen detalj får slarvas
- Vill att **grafen uppdateras kontinuerligt**
- Vill att **redaktör + NAGELFAREN är hårda** — default-betyg 7, 9+ kräver dokumentation

---

## Slutpunkt

- Aldrig publicera ett kapitel som inte är godkänt på 9+ av alla axlar
- Aldrig stanna upp på 7/10. **9+ eller mer arbete.**
- **Förbättringsloopen är aldrig stängd.** Varje läsarreaktion gör boken bättre.
- **Learnings.md är hjärtat.** Varje upptäckt fel sparas permanent som mönster — så framtida kapitel undviker det.

---

## Den verkliga hemligheten

> Bra prosa är inte tekniker. Bra prosa är uppmärksamhet.
>
> Det som tekniker gör är att frigöra författaren från att tänka på saker som kan bli vana. När man inte längre tänker på meningsrytm eller specifikitet eller subtext, då kan man tänka på det som inte kan reduceras till teknik: människan, situationen, ögonblicket.
>
> Tekniker är hantverkets nedre nittio procent. Den övre tio är vad som inte kan läras. Men nittio procent är värt att lära.

Hantverket finns dokumenterat i `.context/hantverk/`:
- `tekniker.md` — A-K, central referens för alla roller
- `kvalitetsgrindar.md` — I.1-I.7, grindar mellan faser
- `snabb-checklista.md` — L, 17 punkter per kapitel
- `anti-monster.md` — J.1-J.8, saker att aldrig göra

---

## Resurser — komplett index

### Process & roller
- `.context/process.md` — FAS 0-9 flödet, hårda regler
- `.context/roles/plot-arkitekt.md`
- `.context/roles/researcher.md`
- `.context/roles/writer.md`
- `.context/roles/redaktor.md`
- `.context/roles/prosa-stad.md`
- `.context/roles/dialog-coach.md`
- `.context/roles/nagelfaren.md`
- `.context/roles/forlaggare.md`
- `.context/roles/sensitivity-lasare.md`
- `.context/roles/graf-vakt.md`
- `.context/roles/varldsbyggare.md`
- `.context/roles/audiobook-direktor.md`
- `.context/roles/marknadsforare.md`

### Canon & fakta
- `.context/canon.md` — fakta-fällor, blacklist
- `.context/story-graph/` — bokens canon
- `.context/story-graph/style-guide.md` — prosastil
- `.context/story-graph/consistency-checks.md` — geografi-spärrar

### Tools & mekanik
- `.context/tools.md` — scripts + pipeline
- `.context/tics-katalog.md` — frekvens-tak per ord
- `scripts/` — alla körbara hjälpmedel
- `docs/adr/` — arkitektur-beslut

### Lärdomar & rapporter
- `.context/learnings.md` — alla upptäckta mönster, permanent
- `.context/redaktor-rapporter/` — per-kapitel granskningar
- `.context/prosa-stad-rapporter/` — naiv-läsare-pass
- `.context/nagelfaren-rapporter/` — meta-granskning av redaktör
- `.context/forlaggar-rapporter/` — helhetspass
- `.context/validator-rapporter/` — mekanisk validering (om pipeline införd)

### Lager 1-7 artefakter
- `.context/koncept/` — Lager 1 (premiss, logline, genre, form, kontrakt, central-fråga, teman)
- `.context/varld/` — Lager 2 (tidsperiod, kontext)
- `.context/story-graph/` — Lager 3 (karaktärer + canon)
- `.context/plot/` — Lager 4 (struktur, bågar, kapitelplan, scenkort)
- `.context/research-dossier/` — Lager 5 (verifierad fakta)
- `.context/stil/` — Lager 6 (POV, dialog, motiv, rytm, inspiration)
- `.context/forlag/` — Lager 7 (respons, beta, formatering, loglinetest)
- `.context/meta/` — beslutslogg, öppna frågor, ambition, hantverksstandarder
