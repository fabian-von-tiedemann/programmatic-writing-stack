# Programmatic Writing Stack

> Ett ramverk för att skriva böcker som ett mjukvaruprojekt.
> Versionkontroll, automatiserade tester, code review, architecture decision records — applicerat på prosa.

**Version:** 1.2
**Status:** Validerad mot fullskaligt thriller-projekt (26 enheter, snitt 9.13/10)
**Författare:** Fabian von Tiedemann

---

## Vad det är

13 AI-roller. 9 lager artefakter. Del III hantverkstekniker. En process-loop med kvalitetsgrindar mellan faser.

Förvandlar enskild författare till operationsekvivalent av ett franchise-team (Tom Clancy-modellen) med behållen upphovsrätt.

## Vad det inte är

- En generator av prosa — AI är verktyg, författaren är upphovsperson
- En ersättning för läsare — mänsklig läsare är slutvalideraren
- Genre-specifikt — fungerar för thriller, sci-fi, fantasy, litterär roman, ungdomsbok
- Beroende av specifik LLM — designat för Claude men model-agnostiskt i princip

---

## Snabbstart

### Initiera nytt bokprojekt

```bash
git clone <denna-repo> ~/code/programmatic-writing-stack
cd ~/code/programmatic-writing-stack
./init-writing-stack.sh ~/projects/min-nya-bok "Boktitel" thriller
cd ~/projects/min-nya-bok
```

Du har nu ett komplett ramverks-skelett med:
- 13 rolldefinitioner i `.context/roles/`
- 9 lager artefakter med templates och `MALL.md`-filer
- Hantverk-bibliotek (tekniker, kvalitetsgrindar, snabb-checklista, anti-monster)
- 7 operativa scripts (graph-query, grep-tics, layered markup, Apple Books-noter, m.fl.)
- Git initialiserat med första commit

### Uppgradera befintligt bokprojekt

När ramverket utvecklas vidare (nya roller, skärpta briefer, nya scripts) kan ett
befintligt projekt uppgraderas icke-destruktivt med `upgrade-existing-project.sh`:

```bash
cd ~/code/programmatic-writing-stack
git pull
./upgrade-existing-project.sh ~/projects/min-bok --dry-run    # förhandsgranska
./upgrade-existing-project.sh ~/projects/min-bok              # på riktigt
```

Tre kategorier av filer hanteras automatiskt:

| Kategori | Filer | Beteende |
|---|---|---|
| **SAFE** | `roles/`, `hantverk/`, `scripts/`, `docs/` | ersätts utan att fråga |
| **DIFF** | `process.md`, `canon.md`, `tics-katalog.md`, `tools.md` | visar diff, frågar `behåll/ersätt/skippa` |
| **NEVER** | `CLAUDE.md`, `manuskript/`, `learnings.md`, `koncept/`, `plot/`, `stil/`, `forlag/`, `meta/`, story-graph med content, `*-rapporter/` | rörs aldrig |

Säkerhetskopia skapas i `.cache/upgrade-backup-<datum>/` före varje ändring och en
rapport landar i `.context/upgrade-rapport-<datum>.md`. Flaggor: `--dry-run`,
`--force` (auto-ersätt SAFE), `--templates DIR`.

### Onboarding-flöde (9 steg, ~1-2h)

Se `docs/PRD.md` sektion 9 för komplett guide. Kort:

1. Fyll i `CLAUDE.md` med din boks premise + distinguishing features
2. Skriv `.context/koncept/premiss.md` + `logline.md` + `central-fraga.md`
3. Skissa POV-karaktärer i `.context/story-graph/character-deepening/`
4. Lägg ut grov plot i `.context/plot/through-line.md` + `struktur.md`
5. Dispatcha **Plot-arkitekt** (FAS 0) för scenkort kap 1
6. Dispatcha **Writer** (FAS 2) för utkast
7. FAS 3-loop: Redaktör → Prosa-städ → Dialog-coach → NAGELFAREN → fix
8. FAS 4 Förläggare när alla kapitel ≥9.0
9. FAS 5+6: lärdomar in i `learnings.md`, graf-uppdatering

---

## Arkitektur

### De 13 rollerna

| FAS | Roll | Veto-rätt |
|---|---|---|
| **0** | Plot-arkitekt | flaggar plot-konflikter |
| **0+** | Researcher | — |
| **2** | Writer | — |
| **3** | Redaktör | — |
| **3** | Prosa-städ | BLOCKERANDE |
| **3** | Dialog-coach | POV-axeln |
| **3** | NAGELFAREN | redaktör-rapport |
| **4** | Förläggare | A/B/C |
| **4** | Sensitivity-läsare | publikation |
| **Löpande** | Graf-vakt | flaggar canon |
| **Separat** | Världsbyggare | — (rådgivande) |
| **8** | Audiobook-direktör | — |
| **9** | Marknadsförare | — |

### De 9 lagren av artefakter

```
.context/
├── koncept/          # Lager 1 — premiss, logline, genre, central fråga
├── varld/            # Lager 2 — tidsperiod + research-dossier
├── story-graph/      # Lager 3+5 — characters, events, secrets, etc.
├── plot/             # Lager 4 — through-line, scenkort, clue-economy
├── stil/             # Lager 6 — motiv, rytm, dialog, POV
├── prosa-anteckningar/  # Lager 7
├── forlag/           # Lager 8 — respons, beta, manuskriptformatering
├── meta/             # Lager 9 — beslutslogg, ambition, hantverksstandarder
└── hantverk/         # Del III — tekniker, kvalitetsgrindar, anti-monster
```

### Kvalitetsgrindar mellan faser

| Grind | Mellan | Ägare |
|---|---|---|
| I.1 Karaktärsgrind | Före FAS 0 | Plot-arkitekt |
| I.2 Plotgrind | Före kapitelplan | Plot-arkitekt |
| I.3 Scenkortsgrind | Före FAS 2 | Plot-arkitekt → Writer |
| I.4 Stilgrind | Före FAS 2 | Writer |
| I.5 Prosagrind | FAS 3 | Redaktör |
| I.6 Boggrind | Före FAS 4 | Förläggare |
| I.7 Seriegrind | Före nästa bok | Världsbyggare |

---

## Förutsättningar

**Hårda dependencies:**
- Git
- Python 3.11+ (stdlib only — inga externa paket)
- Bash 4+ (för shell-scripts)
- LLM med subagent-stöd (Claude Code, motsvarande)

**Mjuka dependencies:**
- Apple Books (för läsarnoter-flödet) — endast om författaren använder denna feedback
- TTS-pipeline (för audiobook-produktion)

**Kompatibilitet:** macOS, Linux. Windows via WSL.

---

## Dokumentation

- **`docs/PRD.md`** — komplett operativ spec (~1500 rader). Onboarding-guide i sektion 9.
- **`docs/stack.html`** — visuell guide för läsning, delning, reflektion. Öppna i webbläsare.
- **`templates/`** — master-katalog som klonas till nya bokprojekt.

---

## Validerat resultat

Ramverket är validerat mot ett fullskaligt thriller-projekt:
- 26 enheter (prolog + 22 kap + epilog + 2 interludier)
- ~70 000 ord
- Snitt 9.13/10 över alla axlar efter FAS 3-pass
- Differens redaktör/verklighet sjönk från 2.1 → <0.5 över fyra rundor
- 673 noder i kunskapsgrafen
- ~50 commits över två sessioner

Bok 2 förväntas vara 5x snabbare än bok 1 efter implementation.

---

## Filosofi-anchor

> Bra prosa är inte tekniker. Bra prosa är uppmärksamhet.
>
> Det som tekniker gör är att frigöra författaren från att tänka på saker som kan bli vana. När man inte längre tänker på meningsrytm eller specifikitet eller subtext, då kan man tänka på det som inte kan reduceras till teknik: människan, situationen, ögonblicket.
>
> Tekniker är hantverkets nedre nittio procent. Den övre tio är vad som inte kan läras. Men nittio procent är värt att lära.

Hantverket finns i `templates/.context/hantverk/`.

---

## Licens

Fritt att använda, anpassa och distribuera för icke-kommersiell såväl som kommersiell användning. Ingen attribuering krävs men uppskattas.

Idéerna och processen är synteser av etablerad mjukvaru-engineering, lean methodology, agile process design, och beprövad redaktörspraxis. Innovationen ligger i att applicera dessa systematiskt på författarskap.

---

## Bidra

Detta ramverk växer med användning. Om du upptäcker nya mönster, fixar buggar i scripts, eller skriver roll-briefer som är skarpare än default — skicka en PR.

Speciellt välkommet:
- Genre-anpassningar (fantasy-specifika tics, sci-fi-research-mönster, etc.)
- Nya queries i `graph-query.py`
- Förbättrade `tag-manuscript.py`-heuristiker
- Integration med fler TTS-pipelines för audiobook-direktören
- Lärdomar från egna bokprojekt (cross-bok learnings-bibliotek)

---

**Senaste uppdatering:** 2026-05-19 (v1.2)
