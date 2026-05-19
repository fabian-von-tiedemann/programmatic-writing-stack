# PRD — Programmatic Writing Stack

**Version:** 1.2
**Datum:** 2026-05-19
**Status:** Komplett plattform — 13 roller, 9 lager artefakter, Del III hantverkstekniker integrerade.
**Författare:** Fabian von Tiedemann

---

## 0. TL;DR

Ett ramverk för att skriva böcker som ett mjukvaruprojekt. Använder versionkontroll, automatiserade tester, code review, architecture decision records och refactoring — applicerat på prosa. Förvandlar enskild författare till operationsekvivalent av ett franchise-team (Tom Clancy-modellen) med behållen upphovsrätt.

**v1.2 lägger till:** komplett artefakt-arkitektur i 9 lager (~50 artefakt-templates från koncept till marknad) och Del III hantverkstekniker (A-K tekniker, I kvalitetsgrindar, J anti-mönster, L snabb-checklista) integrerade i roll-briefer och process-grindar.

**Validerat resultat:** Snitt 9.13/10 över 26 enheter (~70 000 ord) på två sessioner. Differens redaktör/verklighet sjönk från 2.1 → <0.5 över fyra rundor. Bok 2 är 5x snabbare än bok 1 efter implementation.

---

## 1. Problem Statement

### 1.1 Problemen detta ramverk löser

En enskild författare som skriver en bok på 22+ kapitel stöter på följande systemfel:

1. **Canon-drift.** Karaktärer, miljöer, vetskap driftar isär över kapitel. Anna har en iPhone i kap 2, en Pixel i kap 8. Lars är levande i kap 4, död i kap 13. Donnerska huset slår klockan i två kapitel — huset har inget tornur.

2. **Frekvens-blindhet.** AI-redaktör som läser ett kapitel ser inte att "nickade" finns 101 gånger över boken. Inte heller "luktade kaffe" x4 över bok. Mönster syns inte på enskild-fil-nivå.

3. **Self-grading-bias.** LLM-redaktör sätter höga betyg på vagheter. Faktisk validitet av "Klarhet 9.5" är ofta ~6 baserat på vad mänskliga läsare hittar. Bias mot godkännande är inbyggd i modellen.

4. **POV-läckage.** Karaktärernas tankespråk smyger in i fel POV. Anna-analytisk-urban-ton glider in i Erika-norrländska kapitel. AI-redaktör fångar sällan detta utan explicit canon-bibliotek.

5. **Spackling istället för förebyggande.** Korrigerande pass (prosa-städ, NAGELFAREN) som *säkerhetsnät* förväxlas med förebyggande disciplin. Bättre instruktioner till writer minskar antalet fel i grunden.

6. **Verktygslöshet.** "Vad visste karaktär X vid tidpunkt T?" är en omöjlig fråga utan strukturerad data. Manuell genomgång av 22 kapitel är inte hållbar för konsistens-validering.

7. **Förlorad lärdom mellan böcker.** Författaren upptäcker samma typ av fel i bok 2 som hen löste i bok 1. Inget institutionellt minne mellan projekt.

8. **Plot-arkitektur dimridd.** Skribent-agent vet inte HUR scen ska byggas — bara att den ska skrivas. Saknar scenkort, klocka, clue-economy, antagonist-tidslinje, mid-point-reversal. Resultatet blir prosa utan dramaturgisk ryggrad.

9. **Hantverkstekniker implicita.** Specificitet över generalitet, sensorisk grund, subtext > text, iceberg-principen, in-sent-out-early, free indirect discourse — dessa är kända i litteraturen men inte explicita i AI-stacken. Resultatet blir generisk AI-prosa: lila, abstrakt, exposition-tung, alla karaktärer låter likadant.

### 1.2 Vad ramverket är *inte*

- En generator av prosa. AI är verktyg, författaren är upphovsperson.
- En ersättning för läsare. Mänsklig läsare är slutvalideraren.
- Genre-specifikt. Fungerar för thriller, science fiction, fantasy, litterär roman, ungdomsbok.
- Beroende av specifik LLM. Designat för Claude men principerna är model-agnostiska.

---

## 2. Goals & Non-Goals

### 2.1 Goals

**Primära:**
- G1: Höja kapitel-kvalitet från snitt 6-7/10 till snitt 9+/10 inom en kvalitetspass-runda
- G2: Eliminera canon-drift mellan kapitel via centraliserad kunskapsgraf
- G3: Bygga institutionellt minne så bok N+1 är märkbart snabbare än bok N
- G4: Möjliggöra för enskild författare att operera som ett franchise-team
- G5: Bibehålla git-vänlighet och författarens fulla kontroll

**Sekundära:**
- G6: Reducera författarens tid på mekanisk korrektur (frekvens-tics, fakta-checks)
- G7: Generera mätbara framgångskriterier per kapitel (axel-betyg)
- G8: Producera processdokumentation som kan delas eller åter-applieras

### 2.2 Non-Goals

- NG1: Generera fullskaliga romaner från premise utan författar-input
- NG2: Ersätta traditionella förlagsroller (agent, lektör, marknadsförare) i deras helhet
- NG3: Hantera juridiska aspekter (rättigheter, upphovsmannarätt, licensiering)
- NG4: Stödja kollaborativt skrivande mellan flera mänskliga författare i realtid
- NG5: Bygga en monolitisk databas. Filer + git förblir källan.

---

## 3. Användarroller

### 3.1 Primär användare: Författaren

- **Beslutsfattare** för plot, karaktär, ton, juridik
- **Slutgranskare** av allt prosa
- **Operatör** av ramverket (initierar pass, fattar A/B/C-beslut)
- **Tekniskt komfortabel** med kommandoraden, git, markdown
- *Förkunskapskrav:* förmåga att läsa JSON, kunna köra Python-script, förstå AI-prompt-engineering grundläggande

### 3.2 Sekundära användare

- **Mänsklig redaktör/förläggare** som tar över efter ramverket producerat A-rekommendation
- **Lektör/copyeditor** som verifierar slutprodukten
- **Sensitivity-läsare** (manuell, ej AI) för specifika representationsfrågor
- **Läsare** som producerar feedback via Apple Books (kan dras in i learnings.md via script)

### 3.3 AI-subagent-roller (interna)

Se sektion 7 för fullständig specifikation.

---

## 3a. Artefakt-arkitektur (9 lager)

Ramverket arbetar med ~50 artefakter organiserade i nio lager. Varje lager har sin egen mapp under `.context/` (eller `story-graph/` när strukturerad data behövs). Lagren är inte strikt sekventiella — flera utvecklas parallellt — men de har en *övergripande* ordning: lager 1 (koncept) måste existera innan lager 4 (plot) kan låsas; lager 4 (plot) måste existera innan lager 7 (prosa) skrivs.

### Lager 1 — Koncept (`.context/koncept/`)

Bokens hela idé innan något skrivs.

- `premiss.md` — en mening / ett stycke / en sida
- `logline.md` — säljbar 20-30-ords-version + alternativa formuleringar
- `genre.md` — genre, sub-genre, närmaste släktingar
- `form.md` — enskild bok / trilogi / serie, pocket/hardcover, marknad
- `genre-kontrakt.md` — vilka löften gör boken till sin läsare
- `central-fraga.md` — prismat varje scen ska bedömas igenom
- `teman.md` — vad boken egentligen handlar om (inte plotten)
- `series-promise.md` (om serie) — vad lovar serien som helhet

### Lager 2 — Värld (`story-graph/` + `.context/varld/` + `.context/research-dossier/`)

Tidsperiod, geografi, samhällskontext, real-world references.

- `varld/tidsperiod.md` — kalendertid, realtid eller alternativ
- `story-graph/timeline.json` — master, single source of truth
- `varld/geografi.md` — alla platser, adresser, kartor
- `research-dossier/<amne>.md` — verifierade fakta + källor + kvarstående frågor + canon-kandidater
- `story-graph/locations.json`, `organizations.json` — strukturerade noder

### Lager 3 — Karaktärer (`story-graph/character-deepening/` + `relationships.json`)

Djup karaktärsdokumentation.

- `story-graph/characters.json` — strukturerade noder
- `story-graph/character-deepening/char-<id>.md` — djup profil (drivkraft, sårbarhet, quirks, principer, röst-canon, anti-mönster)
- `story-graph/relationships.json` — vem känner vem, sedan när
- `bipersons-katalog.md` — kortare profiler för icke-POV-figurer
- `.context/stil/roster/<namn>.md` — röstprofil per karaktär

### Lager 4 — Plot (`.context/plot/`)

Strukturen mellan koncept och prosa. Detta lager är där v1.2 expanderar mest.

- `through-line.md` — den dolda tråden, det egentliga mysteriet
- `bagar.md` — tematiska resor per huvudkaraktär
- `trilogi.md` (om serie) — vad gör varje bok
- `bok-N/struktur.md` — akter, vändpunkter, mid-point-reversal, klimax, slut
- `bok-N/inciting-incident.md` — ögonblicket där boken inte längre kan vara om något annat
- `bok-N/kapitelplan.md` — kapitel för kapitel
- `bok-N/scenkort/kap-NN-scen-Y.md` — POV, plats, tid, närvarande, premiss, beat, slut
- `bok-N/spanning.md` — spänningsdiagram, hot-nivå per scen
- `bok-N/clue-economy.md` — alla planterade ledtrådar med plantering / upptäckt / förstådd / red-herring-status
- `bok-N/tension-tracker.md` — hot-typ per scen (subtext, explicit, klocka, fysiskt, moraliskt)
- `bok-N/klocka.md` — tickande deadlines, när introduceras, när tickar, konsekvens
- `bok-N/informationsflode.md` — dramatisk ironi-matris (vad vet protagonist / antagonist / sidekick / läsare)
- `bok-N/antagonist-tidslinje.md` — parallell tidslinje, motpartens plan
- `bok-N/try-fail.md` — försök / resultat / lärdom / nästa försök
- `bok-N/cold-open.md` — kapitel-1-strategi
- `bok-N/two-track.md` (om relevant) — parallella spår + rytm-schema

### Lager 5 — Kontinuitet (`story-graph/` + `.context/foreshadowing/`)

Det svåraste lagret i fler-böckers-serier.

- `story-graph/knowledge-matrix.md` — continuity-tracker, vem vet vad när
- `foreshadowing/payoff-tracker.md` — frö-kapitel | frö | payoff-kapitel | payoff
- `story-graph/fact-check.md` — alla faktiska påståenden, kontrollerbara
- `story-graph/dodslista.md` — vem dör / försvinner / flyttar / dyker upp igen
- `story-graph/secrets.json` — strukturerad known_to per karaktär

### Lager 6 — Röst och stil (`.context/stil/` + `story-graph/style-guide.md` + `.context/tics-katalog.md`)

Bokens prosa-DNA.

- `story-graph/style-guide.md` — berättarröst, register, tempo, meningsstruktur
- `stil/undvik.md` — förbjudna konstruktioner (uppdateras under revision)
- `stil/motiv.md` — återkommande motiv + symboler, när planterades / återkommer
- `stil/roster/<namn>.md` + `stil/roster/<namn>-exempel.md` — per-karaktärs röstprov
- `stil/inspiration/<forfattare>.md` — style samples + analys
- `stil/platser/<plats>.md` — scene description bank (sensoriska detaljer + förändringar över tid)
- `stil/rytm.md` — meningsrytm-prov
- `stil/dialog.md` — talstreck/citattecken, attribuering, tankar
- `stil/pov-bok-N.md` — POV-strategi
- `stil/aterkommande.md` — återkommande element över serien
- `tics-katalog.md` — mekaniska grep-mönster med tak

### Lager 7 — Skrivande (`manuskript/` + `.context/prosa-anteckningar/`)

Själva prosan.

- `manuskript/kapitel-NN.md` — utkast / renderad slutprodukt
- `manuskript/kapitel-NN.draft.md` — källfil om layered markup används
- `prosa-anteckningar/kapitel-NN.md` — anteckningar till nästa version
- `manuskript/versioner/v1/`, `v2/` — tidigare utkast (eller via git)

### Lager 8 — Editorial (rapporter + `.context/forlag/`)

Feedback-cykeln.

- `redaktor-rapporter/kapitel-NN-granskning-vN.md`
- `prosa-stad-rapporter/kapitel-NN-stadning-vN.md`
- `nagelfaren-rapporter/kapitel-NN-meta-vN.md`
- `dialog-coach-rapporter/kapitel-NN-roster-vN.md`
- `forlaggar-rapporter/efter-hela-boken-<datum>.md`
- `sensitivity-rapporter/efter-<bok>-<datum>.md`
- `forlag/lektorsbrev-bok-N.md`
- `forlag/fixes-bok-N.md`
- `forlag/respons-bok-N.md`
- `forlag/revisions-tracker.md`
- `forlag/beta/<lasare>-bok-N.md`
- `forlag/sensitivity/<amne>.md`
- `forlag/manuskriptformatering.md` — branschstandard
- `forlag/baksidestext.md` — marketing copy 150-200 ord
- `forlag/loglinetest.md` — diagnostik

### Lager 9 — Meta (`.context/meta/` + `docs/adr/`)

Process och beslut.

- `meta/beslutslogg.md` — alla större beslut + motivering
- `meta/oppna-fragor.md` — vad är inte beslutat
- `meta/parkering.md` — backlog, idéer som inte fick plats
- `meta/bruttolistor/` — råa idéer från brainstorm
- `meta/canon.md` — canonical events som aldrig får retconnas
- `meta/hantverksstandarder.md` — positiva krav (ingen scen utan sensorisk detalj, etc.)
- `meta/ambition.md` — författarens interna kompass
- `docs/adr/00NN-<beslut>.md` — architecture decision records
- `learnings.md` — compounding tillgång, alla upptäckta mönster

---

## 4. Funktionella krav

### 4.1 Krav på kunskapsgrafen (canon)

- F1.1: Grafen ska bestå av maskinläsbara JSON-filer för strukturerad data (characters, events, locations, etc.) plus markdown-filer för djupare beskrivningar (character-deepening, threads, themes)
- F1.2: Alla events ska ha ISO 8601 timestamp, location_id, participant_ids[]
- F1.3: Alla secrets ska ha strukturerad `known_to[]`-array med per-karaktärs `known_since`-datum
- F1.4: Alla karaktärer som är POV eller central biperson ska ha en `character-deepening/char-X.md`-fil
- F1.5: Grafen ska vara frågebar via Python-tooling utan att kräva extern databas
- F1.6: Schema-validering ska upptäcka brott (saknade fält, broken references, ogiltiga datum)

### 4.2 Krav på rollsystemet

- F2.1: Varje roll ska ha separat brief-fil (`.context/roles/<roll>.md`)
- F2.2: Roller ska dispatchas som separata subagenter — inte samma agent som byter mindset
- F2.3: NAGELFAREN-rollen ska vara strikt adversarial — får inte godkänna en rapport utan att hitta minst 5 missar
- F2.4: Default-betyg på alla axlar är 7. 9+ kräver dokumentation av varje punkt redaktören kontrollerat
- F2.5: Prosa-städ-passet är BLOCKERANDE — inget kapitel godkänns utan rapport
- F2.6: Förläggaren har veto-rätt på A/B/C — inget kap N+1 förrän A

### 4.3 Krav på processloopen

- F3.1: Process delad i 7 sekventiella faser (se sektion 8)
- F3.2: Varje fas har tydliga `STOPP`-villkor — får inte gå vidare om föregående inte är klar
- F3.3: Mellan kapitel ska FAS 5 (lärdomar) och FAS 6 (graf-uppdatering) köras OBLIGATORISKT
- F3.4: Tasks-tracking ska visa varje fas, inte bara kapitel
- F3.5: Författar-beslut (plot, juridik) ska flaggas men aldrig appliceras autonomt av subagent

### 4.4 Krav på verktyg

- F4.1: `grep-tics.sh` ska kunna köra mekaniskt över ett eller alla manuskript-filer
- F4.2: `graph-query.py` ska stödja minst tre queries: `who-knows`, `who-was-where`, `thread`
- F4.3: Pipeline ska tolerera schema-luckor utan att krascha (logga + fortsätt)
- F4.4: Alla scripts ska producera deterministiska, diff:bara output
- F4.5: Cache-filer ska vara gitignored

### 4.5 Krav på lärdoms-systemet

- F5.1: `learnings.md` ska uppdateras efter VARJE förläggarpass och VARJE läsarinput
- F5.2: Varje lärdom ska följa formatet Mönster / Bevis / Lärdom / Regel
- F5.3: Lärdomar ska kategoriseras (fakta-fällor, tics, POV-läckage, system-fel)
- F5.4: Tics-katalogen ska uppdateras med nya frekvens-mönster när de upptäcks
- F5.5: Lärdomar ska kunna åter-användas i nästa bokprojekt (cross-bok library)

---

## 5. Tekniska krav

### 5.1 Dependencies

**Hårda dependencies:**
- Git (versionkontroll, allt diff:bart)
- Python 3.11+ (stdlib only — inga externa paket krävs)
- Bash 4+ (för shell-scripts)
- Markdown editor (Obsidian, VSCode, eller motsvarande)
- LLM med subagent-stöd (Claude Code, motsvarande)

**Mjuka dependencies (om vissa features används):**
- Apple Books (för läsarnoter-flödet) — endast om författaren använder denna feedback-kanal
- TTS-pipeline (för audiobook-produktion)

### 5.2 Performance-krav

- P1: graph-query.py ska svara inom 5 sekunder på alla queries mot graf upp till 1000 noder
- P2: grep-tics.sh ska köra över hela manuskript-katalogen inom 10 sekunder
- P3: Render-pipeline (layered markup, om använd) ska producera ren prosa inom 5 sekunder per kapitel
- P4: Validate-pipeline ska producera valideringsrapport inom 10 sekunder per kapitel

### 5.3 Förvaring och versionkontroll

- S1: Alla projekt-filer (kapitel, graf, briefer, rapporter) ska checkas in i git
- S2: Cache-filer och säkerhetskopior ska vara gitignored
- S3: Commit-meddelanden ska följa konvention: `<typ>: <vad>` (t.ex. `kap-04: kvalitetspass FAS 3`)
- S4: Co-Authored-By för AI-genererat innehåll
- S5: Inga binära filer i repo utöver bok-omslag och epub-export

### 5.4 Kompabilitet

- C1: Ramverket ska fungera på macOS, Linux. Windows via WSL.
- C2: Inga LLM-specifika syntax-beroenden i prompt-templates
- C3: Markdown-filer ska följa CommonMark + GitHub-flavored
- C4: JSON ska följa standard JSON (RFC 8259), inte JSON5 eller liknande

---

## 6. Arkitektur

### 6.1 Filstruktur (komplett)

```
project-root/
├── CLAUDE.md                          # 100-150 rader: index + huvudregler
├── README.md                          # projektets publika beskrivning
├── manuskript/                        # alla kapitel som markdown
│   ├── prolog.md
│   ├── kapitel-01.md
│   ├── kapitel-02.md
│   ├── ...
│   ├── kapitel-NN.md
│   ├── epilog.md
│   └── interludium-mellan-X-och-Y.md  # om dokument-interludier används
├── docs/
│   ├── adr/                           # architecture decision records
│   │   ├── 0001-<beslut>.md
│   │   └── 0002-<beslut>.md
│   ├── programmatic-writing-stack.html
│   └── programmatic-writing-stack-PRD.md
├── .context/
│   ├── process.md                     # FAS 1-7 flödet
│   ├── canon.md                       # fakta-fällor + verklig-person-blacklist
│   ├── tools.md                       # script-användning
│   ├── learnings.md                   # COMPOUNDING tillgång
│   ├── tics-katalog.md                # mekaniska grep-mönster
│   ├── roles/                          # 13 roller (komplett ramverk)
│   │   ├── plot-arkitekt.md
│   │   ├── researcher.md
│   │   ├── writer.md
│   │   ├── redaktor.md
│   │   ├── prosa-stad.md
│   │   ├── dialog-coach.md
│   │   ├── nagelfaren.md
│   │   ├── forlaggare.md
│   │   ├── sensitivity-lasare.md
│   │   ├── graf-vakt.md
│   │   ├── varldsbyggare.md
│   │   ├── audiobook-direktor.md
│   │   └── marknadsforare.md
│   ├── story-graph/                   # KUNSKAPSGRAFEN = bokens canon
│   │   ├── characters.json
│   │   ├── events.json
│   │   ├── locations.json
│   │   ├── secrets.json
│   │   ├── relationships.json
│   │   ├── objects.json
│   │   ├── documents.json
│   │   ├── organizations.json
│   │   ├── timeline.json
│   │   ├── knowledge-matrix.md
│   │   ├── threads.md
│   │   ├── themes.md
│   │   ├── style-guide.md
│   │   ├── consistency-checks.md
│   │   └── character-deepening/
│   │       ├── char-<id>.md
│   │       └── ...
│   ├── redaktor-rapporter/
│   ├── prosa-stad-rapporter/
│   ├── nagelfaren-rapporter/
│   ├── forlaggar-rapporter/
│   └── validator-rapporter/
├── scripts/
│   ├── books-annotations.sh           # läsarnoter från Apple Books
│   ├── grep-tics.sh                   # mekanisk frekvens-validator
│   ├── graph-query.py                 # 3 queries mot grafen
│   └── _storygraph.py                 # graf-loader (shared)
└── .gitignore                         # ignorera .cache/, *.tmp, etc.
```

### 6.2 Datalager-arkitektur

```
KÄLLA (git-versionhanterad)
├── manuskript/*.md        # prosa
├── .context/story-graph/  # canon
└── .context/roles/        # roll-briefer

       │
       ▼ (loadning vid behov)

VERKTYGSLAGER (Python, in-memory)
├── _storygraph.py         # generic loader
└── graph-query.py         # specifika queries

       │
       ▼ (output)

RAPPORT-LAGER (markdown till .context/*-rapporter/)
├── Per-kapitel granskningar
├── Validator-output
└── Metarapporter (NAGELFAREN på redaktör)

       │
       ▼ (kondenserat)

LÄRDOMS-LAGER
├── learnings.md           # compounding mönster
└── tics-katalog.md        # mekaniska checks
```

### 6.3 Process-flöde (övergripande)

```
[Författare initierar]
       │
       ▼
FAS 1: Förberedelse ──┐
       │              │ STOPP om graf eller learnings inkomplett
       ▼              │
FAS 2: Writer-agent skapar utkast
       │
       ▼
FAS 3: Redaktör → Prosa-städ → NAGELFAREN ──┐
       │                                     │ Re-run tills 9+ alla axlar
       ▼                                     │
FAS 4: Förläggare A/B/C ─────────────────────┤ Om B/C: tillbaka till FAS 3
       │
       ▼ (när A)
FAS 5: Lärdomar in i learnings.md
       │
       ▼
FAS 6: Graf-uppdatering
       │
       ▼
FAS 7: Nästa kapitel ─────► FAS 1
```

---

## 7. Roller (Agent-specs)

Varje roll har separat brief-fil i `.context/roles/`. Templates finns i appendix A.

### 7.0 Mapping mellan roller och artefaktlager

Varje roll ägar input från specifika lager och producerar output i andra. Tabellen visar primärt ägarskap — alla roller läser från flera lager.

| Roll | Lager (läser) | Lager (skriver) | Primär output |
|---|---|---|---|
| Plot-arkitekt | 1, 2, 3, 5 | 1 (refining), 4 | `koncept/`, `plot/bok-N/` (scenkort, klocka, clue-economy, antagonist-tidslinje, tension-tracker, kapitelplan) |
| Researcher | 2, källor | 2 | `research-dossier/<amne>.md`, canon-kandidater till `story-graph/` |
| Världsbyggare | 1, 2, 3, 5 | 1, 2, 9 | `world-bible.md`, `series-bible.md`, `cross-bok-continuity-N.md` |
| Writer | 1, 2, 3, 4, 5, 6 | 7 | `manuskript/kapitel-NN.md` |
| Redaktör | 4, 5, 6, 7 | 8 | `redaktor-rapporter/` (8 axlar + 12 tester + 5 helhets) |
| Prosa-städ | 7 (+ minimal canon för fakta) | 8 | `prosa-stad-rapporter/` (6 frågor/mening) |
| Dialog-coach | 3, 6, 7 | 8 | `dialog-coach-rapporter/` (POV-veto) |
| NAGELFAREN | 3, 5, 7, 8 (redaktör-rapport) | 8 | `nagelfaren-rapporter/` (min 5 missar) |
| Förläggare | hela 7, hela 8 | 8 | `forlaggar-rapporter/` (A/B/C) |
| Sensitivity-läsare | 1, 3, 7 | 8 | `sensitivity-rapporter/` (publikation-veto) |
| Graf-vakt | 5, 7 | 5 (säker auto-fix) | `graf-vakt-rapporter/`, schema-fixar |
| Audiobook-direktör | 6, 7 | 8 audio-sub | `scripts/audiobook/*.json`, `audiobook/*.md` |
| Marknadsförare | 1, 3, 7 | 8 | `marknadsforing/pitch-pack-*.md` |

### 7.1 Writer

**Syfte:** Producera kapitel-utkast som följer canon, karaktärsdjup och stilcanon.

**Triggers:** Manuellt dispatchad av författare när graf och learnings är uppdaterade efter föregående kapitel.

**Input:**
- CLAUDE.md
- .context/roles/writer.md
- .context/process.md
- .context/canon.md
- .context/learnings.md
- .context/story-graph/character-deepening/char-<POV-id>.md + relevanta bi-personer
- .context/story-graph/* (relevanta noder)
- Alla tidigare kapitel
- Plot-outline (från plot-arkitekt-roll om använd, annars författar-input)

**Output:**
- `manuskript/kapitel-NN.md` (utkast, 3000-3500 ord)
- Eventuell `manuskript/kapitel-NN.draft.md` om layered markup används

**Discipliner:**
- INTRODUKTIONS-DISCIPLIN: bestämd form kräver tidigare obestämd form
- GENRE-DISCIPLIN: håll genre-register, inga genretransgressioner
- REPETITIONS-DISCIPLIN: variera doft/objekt/varumärken — kolla frekvens

### 7.2 Redaktör

**Syfte:** Skarp mening-för-mening-granskning + helhetskontroller. Sätter kalibrerade axel-betyg.

**Triggers:** Efter writer producerar utkast.

**Input:** Kapitel + CLAUDE.md + redaktor.md + canon.md + learnings.md + character-deepening + grafen

**Output:** `.context/redaktor-rapporter/kapitel-NN-granskning-vN.md`

**8 axlar att betygsätta (kalibrerat default 7):**
1. Stil
2. Atmosfär
3. POV
4. Cliffhanger
5. Spänning under ytan
6. Geografi/fakta
7. Logik
8. Klarhet

**12 mening-för-mening-tester (sektion 1a):**
1. Klarhet-test
2. Zeugma-check
3. Syftnings-check (subjekt-dubblering)
4. Verb-precision
5. Preposition-stapling (max 2 i rad)
6. Telegraf-mening (utelämnat "att")
7. Entitets-introduktion (bestämd form utan föregående obestämd)
8. Fakta-mekanik (tekniska detaljer)
9. Genre-register
10. Repetitions-check
11. Författar-essä-flagga
12. Aforism-flagga

**5 helhetskontroller (sektion 1c):**
1. Frekvens-rapport över alla kapitel
2. Genre-register-stickprov
3. Verklig-person-check
4. Mekanisk konsistens (telefon/bil/klädmodeller per karaktär)
5. Etablerings-spårning

**Veto-villkor:** Om 9+ på en axel, MÅSTE redaktören lista MINST 3 saker som inte är perfekta (för att förhindra inflation).

### 7.3 Prosa-städ-agent (Naiv läsare)

**Syfte:** Fånga otydlighet som redaktör missar genom att läsa SOM EN NAIV FÖRSTAGÅNGSLÄSARE.

**Triggers:** Efter redaktör-pass. BLOCKERANDE — kapitlet kan inte gå vidare utan denna rapport.

**Input:** Kapitlet + `.context/roles/prosa-stad.md` + (minimalt annat, för att bevara naiv-perspektiv) + canon.md för fakta-fällor.

**Output:** `.context/prosa-stad-rapporter/kapitel-NN-stadning-vN.md`

**6 frågor per mening:**
1. **Fattar jag vad som står?** Är det otydligt vem som gör vad?
2. **Vad syftas det på?** Bestämd form — har entiteten introducerats för mig?
3. **Är det här nytt?** Något presenteras som självklart men är obekant — borde introduceras bättre?
4. **Är det rimligt?** Livslogik — tror jag på det?
5. **Är det här samma röst som tidigare?** Eller har språket bytt register?
6. **Stannar jag upp?** Om jag pausar för att läsa om — rött flagg.

### 7.4 NAGELFAREN (Adversarial meta-granskare)

**Syfte:** Bryta self-grading-bias genom att granska redaktörens RAPPORT, inte boken.

**Triggers:** Efter prosa-städ. Veto-rätt på redaktörens betyg.

**Input:** Kapitel + redaktörens rapport + prosa-städ-rapport + character-deepening + learnings.md

**Output:** `.context/nagelfaren-rapporter/kapitel-NN-meta-vN.md`

**Hård regel:** Måste hitta minst 5 missar. Om inte hittade: gå tillbaka och titta noggrannare. Får inte lämna in en "godkänd"-rapport utan dokumenterade missar.

**Output-format:**
1. Mappning av redaktörens betyg mot kapitlet (verkliga betyg per axel)
2. Anti-detektor-kontroll (mot 10 lärdoms-mönster)
3. Karaktärs-consistens-kontroll mot deepening
4. Minst 5 bonus-fynd (saker varken redaktör eller prosa-städ flaggade)
5. Slutbedömning: ✓ KAN ACCEPTERAS / ⚠ HAR LUCKOR / ✗ FÖRKASTAS

**Veto-mekanik:** Om NAGELFAREN hittar 5+ missar → redaktör-rapporten FÖRKASTAS och redaktören gör om.

### 7.5 Förläggare

**Syfte:** Helhets-perspektiv över hela boken. A/B/C-rekommendation.

**Triggers:** Efter alla kapitel passat FAS 3.

**Input:** ALLA kapitel + grafen + alla redaktör/NAGELFAREN-rapporter + learnings.md

**Output:** `.context/forlaggar-rapporter/efter-hela-boken-<datum>.md`

**Granskningsområden:**
1. Karaktärsbåge över hela boken
2. Plot-trådar (avslutade? lösa trådar?)
3. Frekvens-mönster över alla kapitel (kaffe, Volvo, nickade)
4. Strukturella frågor (pacing, POV-balans, distinguishing features)
5. Stilistisk koherens
6. Distinguishing features (är de levererade konsekvent?)
7. Per-kapitel A/B/C-bedömning

**Beslut:**
- **A:** Klar för publikation
- **B:** En till runda på specifika kapitel
- **C:** Strukturell omarbetning

### 7.6 Plot-arkitekt

**Syfte:** Designar bokens plot-båge **innan** writer dispatchas. Säkerställer att trådar väver ihop, att cliffhangers är oförutsägbara men i efterhand oundvikliga, att POV-fördelningen tjänar dramaturgin. Den enda rollen som arbetar FÖRE skrivande — alla andra är reaktiva.

Arbetar med dramaturgisk grammatik (setup → komplikation → mid-point → false summit → reveal → cliffhanger). Producerar scen-skelett som writer klär i kött.

**Triggers:**
- FAS 0 — innan varje kapitel
- Mellan kapitel om plot omformas (förläggar/författar-beslut)
- Vid mid-point och false summit
- Efter större fakta-uppdateringar som ändrar förutsättningar

**Input:** CLAUDE.md + canon.md + threads.md + knowledge-matrix.md + events.json + timeline.json + character-deepening + tidigare kapitel + tidigare plot-outlines

**Output:** `.context/plot-outlines/kapitel-NN-outline.md` (scen-skelett, ej prosa)

**Veto-villkor / Eskalering:** Flaggar plot-konflikter; applicerar aldrig autonomt. Eskalering till författaren vid tids-/geografi-konflikt, tråd-tappning (>4 kapitel), POV-kollaps, cliffhanger-vektor-upprepning, reveal-brott mot knowledge-matrix.

### 7.7 Researcher

**Syfte:** Verifierar fakta-claims **innan** de hamnar i texten. Producerar dossier-filer som blir canon-källa. Skiljer canon-research (in i grafen) från writer-bakgrund (textur, stannar i dossier).

**Triggers:**
- FAS 0 — general world-building före boken
- FAS 2 sub-steg — när writer behöver specifik fakta
- Reaktivt efter redaktör/NAGELFAREN/förläggare-flaggor

**Input:** Story-graph nod eller specifik fråga + canon.md + befintliga dossier

**Output:** `.context/research-dossier/<amne>.md` med format Bakgrund / Verifierade fakta + källor / Kvarstående frågor / Notiser till writer (textur) / Canon-kandidater

**Veto-villkor / Eskalering:** Flaggar, applicerar inte canon-ändringar autonomt. Eskalering vid fakta-konflikt mot canon, anakronismer i färdigt kapitel, juridiska risker, verkliga personer.

### 7.8 Graf-vakt

**Syfte:** "DBA för bokens canon." Håller story-graph synkad med texten kontinuerligt. **Inte en FAS 6-checkpoint** — en LÖPANDE roll som aktiveras efter varje pass där manuskriptet eller grafen ändras.

**Triggers:**
- Efter writer-pass (extrahera nya entiteter)
- Efter redaktör/prosa-städ/dialog-coach/NAGELFAREN/fix-pass (uppdatera ändrade)
- Efter förläggar-pass (global konsistens)
- Schemalagt eller manuellt
- Efter ny ADR om graf-schema

**Input:** Hela story-graph + senaste manuskript-ändringar + scripts/graph-query.py

**Output:** `.context/graf-vakt-rapporter/efter-<händelse>-<datum>.md`
- Säker auto-fix (saknad stub-nod, kebab-case, strukturerad known_to)
- Flagg-rapport (möjliga dubbletter, broken references, schema-drift)

**Veto-villkor / Eskalering:** Flaggar konflikter men applicerar INTE merges autonomt. Eskalering vid dubbletter, canon-konflikter som påverkar plot. NAGELFAREN-eskalering om text/graf säger olika saker likvärdigt.

### 7.9 Dialog-coach

**Syfte:** Röst-vakt. Lyssnar BARA på dialog och POV-tankespråk. Fångar POV-läckage som redaktör + prosa-städ missar.

**Triggers:** FAS 3, mellan prosa-städ (STEG 7b) och NAGELFAREN (STEG 7c). Default: alla kapitel.

**Input:** Kapitlet + ALLA character-deepening-filer + characters.json + style-guide.md + tidigare kapitel där POV-karaktären haft röst

**Output:** `.context/dialog-coach-rapporter/kapitel-NN-roster-vN.md` med POV-detektering, per-karaktärs röst-rapport, läckage-flaggor, förbjudna-konstruktion-träffar, betyg per karaktär

**Veto-villkor:** Veto på **POV-axeln specifikt**. ≥3 läckage-flaggor eller ≥2 förbjudna-konstruktion-träffar → POV-axeln BLOCKERAR 9+. NAGELFAREN måste nedjustera redaktör-betyget. Eskalering till författaren om läckage avslöjar canon-fel i deepening.

### 7.10 Sensitivity-läsare

**Syfte:** Etisk granskning av representation, makt och språk. Läser HELA boken med disciplinerat öga — pekar ut texten, inte författaren.

**Triggers:** FAS 4, **efter förläggar-pass A**, innan publikation. Kan också köras tidigare på begäran för specifik karaktär/scen. Default: en gång per bok, sent.

**Input:** Hela boken + canon.md + themes.md + characters.json + character-deepening + ev. tidigare sensitivity-rapport

**Output:** `.context/sensitivity-rapporter/efter-<bok>-<datum>.md` med representation per kategori (klass, etnicitet, kön, sexualitet, funktion, ålder), språk-fynd, makt-asymmetrier, kulturell appropriering, geografisk autenticitet, BLOCKERANDE fynd, prioriterad rekommendation-lista

**Veto-villkor:** **Veto på publikation** vid allvarlig stereotypisering, representations-svikt, otidsenligt språk, glamourisering av övergrepp, kulturell appropriering utan dignitet. Författaren beslutar **hur** fixa.

### 7.11 Världsbyggare

**Syfte:** Världs-arkitekt. Den enda rollen som tänker BORTOM enskild bok. Designar världen så den bär flera berättelser. Klassificerar entiteter som världs-canon (universellt) vs bok-canon (specifikt).

**Triggers (tre tidpunkter):**
- **Före bok 1** (fundament-pass) — designar grund-världen
- **Efter bok 1** (extraktion-pass) — extraherar världs-bibel från färdig bok
- **Före bok N+1** (continuity-pass) — cross-bok-continuity

**Input:** Hela story-graph + character-deepening + threads + themes + canon + ev. tidigare world-bible + ev. tidigare böcker

**Output:**
- `.context/world-bible.md` (live-dokument, överlever projektet)
- `.context/series-bible.md` (om serie planerad)
- `.context/cross-bok-continuity-<bok-N>.md` (per uppföljare, med KANONISERAT / TOLKNINGSBART / MEDVETET ÖPPET)

**Veto-villkor:** **Ingen veto.** Rådgivande. Föreslår världs-canon, dokumenterar mönster, flaggar inkonsistenser. Författaren beslutar.

### 7.12 Audiobook-direktör

**Syfte:** Förbereder texten för uppläsning. Markerar betoning, pauser, dialekter, uttal. Producerar uttalslexikon + karaktärsröster + regianvisningar för TTS-pipen eller skådespelar-producent.

**Triggers:** FAS 8 — efter förläggar-A. Kan också köras inkrementellt per kapitel om TTS-pipen är aktiv.

**Input:** Hela manuskriptet + canon.md + characters.json + character-deepening + locations.json + organizations.json + style-guide.md + scripts/audiobook/* (befintliga config + lexikon)

**Output:**
- `scripts/audiobook/pronunciations.json` (bygg vidare, ersätt inte)
- `scripts/audiobook/character-voices.json` (voiceProfiles per POV + central biperson)
- `.context/audiobook/karaktarsröster.md` — fördjupad per POV (inre-tanke-röst vs dialog-röst)
- `.context/audiobook/regissor-anvisningar.md` — övergripande regi (scen-typer, dokument-interludier, tidsstämpel-rubriker)
- `.context/audiobook/markup-pass-kapitel-NN.md` (per kapitel om director-overrides behövs)
- `.context/audiobook/direktor-rapport-<datum>.md` — täckning + flaggor + författar-beslut

**Veto-villkor:** **Ingen veto i manuskriptet** (applicerar inga text-fixar). Veto i audio-pipeline (kan be om re-generering). Audio-tics som påverkar ljudboksupplevelsen flaggas till författaren.

### 7.13 Marknadsförare

**Syfte:** Den absolut sista rollen. Läser boken **som någon som ska sälja den**. Hjälper boken hitta sin läsare. Mindre om text-kvalitet, mer om kommersialisering.

**Triggers:** FAS 9 — när boken är A-godkänd och redo för tryck. Kan också köras innan publikation om författaren behöver pitch-pack för agent-möten.

**Input:** Hela manuskriptet + senaste förläggar-rapport + themes + threads + characters + character-deepening + learnings

**Output:** `.context/marknadsforing/pitch-pack-marken-under-marken.md` med:
- Pitch-mening (5-10 versioner med rekommendation)
- Jämförelsetitlar (3-5 med konkret motivering)
- Målgrupp (demografi + psykografi + köpvägar + kanaler)
- Baksidestext (2 versioner, max 200 ord, inga spoilers)
- Författarpresentation (lång + kort)
- Pressmaterial (push-notis + pressrelease + talking points)
- Cover-direction (med referenser till existerande omslag)
- Genre-positionering (hylla + ström + awards)
- Författar-beslut explicit listade

**Veto-villkor:** **Ingen veto.** Förslag. Författaren och förlaget beslutar.

---

## 8. Process (FAS 0-9 + löpande GRAF-VAKT + separat VÄRLDSBYGGARE)

### 8.0 FAS 0 — Plot + Research (FÖRE skrivande)

**Steg:**
- STEG 0a: Dispatcha PLOT-ARKITEKT (se 7.6). Output: `.context/plot-outlines/kapitel-NN-outline.md`.
- STEG 0b: Dispatcha RESEARCHER (se 7.7) för flaggade uppslag. Output: `.context/research-dossier/<amne>.md`.

**STOPP** om plot-outline saknas eller research-flagor inte är besvarade.

### 8.1 FAS 1 — Förberedelse innan writer dispatchas

**Steg:**
1. STEG 1: Grafen är COMPLETE från förra kapitlet
2. STEG 2: `learnings.md` innehåller ALL feedback från redaktör + förläggare + läsare för förra kapitlet
3. STEG 3: `roles/redaktor.md` sektion 1c uppdaterad med förläggarens senaste helhetskontroller
4. STEG 4: `story-graph/knowledge-matrix.md` konsulterad för POV-vetskap

**STOPP** om STEG 1-4 inte är ✓.

### 8.2 FAS 2 — Skrivande

**Steg:**
5. STEG 5: Dispatcha WRITER-subagent (se 7.1)

### 8.3 FAS 3 — Redaktörsloop

**Steg:**
6. STEG 6: Dispatcha REDAKTÖR-subagent (se 7.2)
7. STEG 7: Applicera fixar
8. STEG 7a: PROSA-STÄD-AGENT (BLOCKERANDE — se 7.3)
9. STEG 7b: Applicera prosa-städ-fixar
10. STEG 7b1: DIALOG-COACH (POV-veto — se 7.9)
11. STEG 7b2: Applicera dialog-coach-fixar
12. STEG 7c: NAGELFAREN (BLOCKERANDE för 9+, se 7.4)
13. STEG 8: Re-dispatcha redaktör tills 9+ på ALLA axlar

### 8.4 FAS 4 — Förläggargranskning + Sensitivity

**Steg:**
14. STEG 9: Dispatcha FÖRLÄGGAR-subagent (se 7.5)
15. STEG 10: Applicera förläggar-fixar
16. STEG 11: Om förläggaren rekommenderar B/C → repetera tills A
17. STEG 11a: SENSITIVITY-LÄSARE (publikation-veto — se 7.10)
18. STEG 11b: Applicera ev. sensitivity-fixar

### 8.5 FAS 5 — Arbeta in lärdomar (OBLIGATORISKT)

**Steg:**
15. STEG 12: Skriv in ALLA nya fel/tics i `learnings.md`
16. STEG 13: Uppdatera `roles/redaktor.md` sektion 1c om förläggaren hittade systemfel
17. STEG 14: Om läsarinput finns (via books-annotations.sh): skriv in den

### 8.6 FAS 6 — Graf-uppdatering (OBLIGATORISKT INNAN NÄSTA KAPITEL)

**Steg:**
18. STEG 15: Dispatcha graf-uppdaterar-subagent eller uppdatera manuellt:
    - events.json
    - characters.json
    - locations.json
    - documents.json
    - objects.json
    - secrets.json
    - knowledge-matrix.md

**STOPP** om STEG 12-15 inte är ✓.

### 8.7 FAS 7 — Nästa kapitel

**Steg:**
19. STEG 16: Mark task complete, börja FAS 0 för nästa kapitel

### 8.8 FAS 8 — Audiobook (efter förläggar-A)

**Steg:**
20. STEG 17: Dispatcha AUDIOBOOK-DIREKTÖR (se 7.12)
21. STEG 18: Producera uttalslexikon + voiceProfiles + regianvisningar

### 8.9 FAS 9 — Marknadsföring (efter audiobook eller parallellt)

**Steg:**
22. STEG 19: Dispatcha MARKNADSFÖRARE (se 7.13)
23. STEG 20: Producera pitch-pack

### 8.10 GRAF-VAKT — LÖPANDE (efter varje pass)

Körs efter writer / redaktör / prosa-städ / dialog-coach / NAGELFAREN / fix-pass / förläggare. Se 7.8. FAS 6 är formell verifiering — graf-vakten själv körs LÖPANDE.

### 8.11 VÄRLDSBYGGARE — separat (tre tidpunkter)

Se 7.11. Körs **före bok 1** (fundament), **efter bok 1** (extraktion), **före bok N+1** (cross-bok-continuity).

### 8.12 Hårda regler om processen

1. **Aldrig hoppa över ett steg.** Om någon vill "köra snabbt" — säg nej.
2. **Aldrig dispatcha writer för kap N+1 om FAS 5+6 för kap N inte är klara.**
3. **Förläggaren är vetoröst.**
4. **NAGELFAREN är vetoröst på redaktören.**
5. **DIALOG-COACH är vetoröst på POV-axeln.**
6. **SENSITIVITY-LÄSARE är vetoröst på publikation.**
7. **PROSA-STÄD är BLOCKERANDE.**
8. **PLOT-ARKITEKT körs FÖRE writer.**
9. **GRAF-VAKT körs LÖPANDE.**
10. **Tasks-tracking ska visa varje fas, inte bara kapitel.**
11. **Grafen är canon.**
12. **PROSA-PRINCIPEN (icke-förhandlingsbar):** ingen syftningstvivel. Klarhet före allt.

### 8.13 Kvalitetsgrindar mellan faserna (Del III I.1-I.7)

Sju grindar måste passas innan processen flyttar vidare. Varje grind ställer specifika frågor; om svaret är "inte ännu" → tillbaka till föregående fas. Grindar är dokumenterade i `.context/hantverk/kvalitetsgrindar.md`.

| Grind | Var | Frågor |
|---|---|---|
| **I.1 Karaktärsgrind** | Innan FAS 0/1 (innan plot) | Kan jag namnge varje huvudkaraktärs (a) främsta önskan, (b) främsta rädsla, (c) blinda fläck, (d) språkliga signatur? |
| **I.2 Plotgrind** | Innan FAS 0 STEG 0a → FAS 1 | Kan jag besvara central-fråga utan synopsis? Vet jag inciting incident, mid-point, klimax? Vet jag varje aktes funktion? |
| **I.3 Scenkortsgrind** | Innan FAS 2 (innan writer) | Har varje scen mål, konflikt, vändpunkt? Vet jag POV, plats, närvarande, vad varje karaktär vill ut ur scenen? |
| **I.4 Stilgrind** | Innan FAS 2 | Har jag exempel-stycken som visar bokens röst? Karaktärs-röstprov? Undvik-listan? |
| **I.5 Prosagrind** | I FAS 3 (efter writer) | Kan jag stryka tre stycken utan att förlora något? Kan jag dölja attribuering i dialog och fortfarande veta vem som talar? Har varje scen sensorisk detalj? Har varje karaktär agenda? |
| **I.6 Boggrind** | Innan FAS 4 | Är alla planted clues skördade? Setups paid off? Continuity konsistent? Canonical events korrekta? |
| **I.7 Seriegrind** | Innan nästa bok | Bryter inget canonical events från bok 1-(N-1)? Avancerar tematiska bågar? Lämnar tillräckligt öppet för bok N+1? |

Grindarna körs av relevanta roller: I.1 + I.7 av världsbyggare; I.2 + I.3 av plot-arkitekt; I.4 + I.5 av redaktör/prosa-städ/dialog-coach; I.6 av förläggare. NAGELFAREN verifierar att grinden faktiskt passades, inte bara påstods.

---

## 9. Onboarding-guide — installera i nytt projekt

### 9.1 Förutsättningar

- Git-repo initierat
- Python 3.11+ installerat
- Bash tillgängligt
- LLM-klient med subagent-stöd (t.ex. Claude Code)
- Bok-idé klar (premise, huvudkaraktärer identifierade)

### 9.2 Steg 1: Skapa basstruktur

```bash
cd /path/to/your/book-project

# Skapa katalog-struktur
mkdir -p manuskript
mkdir -p docs/adr
mkdir -p .context/{roles,story-graph/character-deepening}
mkdir -p .context/{redaktor-rapporter,prosa-stad-rapporter,nagelfaren-rapporter,forlaggar-rapporter}
mkdir -p scripts

# Initiera git om det inte redan är gjort
git init
echo ".cache/" >> .gitignore
echo "*.tmp" >> .gitignore
echo "__pycache__/" >> .gitignore
```

### 9.3 Steg 2: Kopiera ramverks-filer

Från ett befintligt projekt som använder ramverket (eller från en template-repo):

**Kopiera roll-briefer (anpassa till din bok):**
```bash
cp <source>/.context/roles/*.md .context/roles/
cp <source>/.context/process.md .context/
cp <source>/.context/canon.md .context/
cp <source>/.context/tools.md .context/
cp <source>/.context/tics-katalog.md .context/
```

**Kopiera scripts:**
```bash
cp <source>/scripts/grep-tics.sh scripts/
cp <source>/scripts/graph-query.py scripts/
cp <source>/scripts/_storygraph.py scripts/
chmod +x scripts/*.sh scripts/*.py
```

### 9.4 Steg 3: Anpassa CLAUDE.md

Skapa en `CLAUDE.md` i projektroten med:

```markdown
# CLAUDE.md — Stående instruktioner för <BOK-TITEL>

## Vad detta är

[Bokens premise, genre, omfattning, ambition]

## De N distinguishing features

[Vad gör DIN bok unik]

## Process

Se `.context/process.md` för FAS 1-7-flödet.

## Roller

Se `.context/roles/` för per-roll-briefer.

## Canon

Se `.context/canon.md` för fakta-fällor + verklig-person-blacklist.

## Resurser

[Index över alla filer i .context/]
```

Använd PRD:s appendix A som template.

### 9.5 Steg 4: Initiera kunskapsgrafen

Skapa tomma JSON-filer i `.context/story-graph/`:

```bash
for f in characters events locations secrets relationships objects documents organizations timeline; do
    echo "{}" > .context/story-graph/$f.json
done

touch .context/story-graph/{knowledge-matrix,threads,themes,style-guide,consistency-checks}.md
touch .context/learnings.md
```

Fyll i basgrafens noder:
- Minst 3 POV-karaktärer i `characters.json`
- Plot-bågens viktigaste events i `events.json`
- Huvudplatser i `locations.json`

### 9.6 Steg 5: Anpassa canon.md och tics-katalog.md

`canon.md`:
- Lista verkliga personer som inte får finnas i fiktionen
- Genre-specifika fakta-fällor (för thriller: geografi; för historisk roman: tidsanakronismer)
- Hårda no:s från författaren

`tics-katalog.md`:
- Generella tics (alla genrer)
- Genre-specifika tics
- Författar-specifika tics (om du vet dina egna)

### 9.7 Steg 6: Skriv character-deepening för POV-karaktärerna

Använd templates i appendix B. Minst för POV-karaktärer — gärna även för nyckel-bipersoner.

Lägg `deepening_file`-pekare i characters.json så roller hittar dem.

### 9.8 Steg 7: Skapa ADR 0001 (om du planerar specifika designbeslut)

Exempel: layered markup, audiobook-pipeline, parallella POVs.

### 9.9 Steg 8: Testa pipeline

```bash
# Skapa ett mini-test
echo "# Kapitel 1\n\nTestmening." > manuskript/kapitel-01.md

# Kör grep-tics
./scripts/grep-tics.sh manuskript/

# Bygg minst en event-nod, försök query
./scripts/graph-query.py --help
```

### 9.10 Steg 9: Första kapitlet

Följ FAS 1 → 7 enligt process.md. För första kapitlet förvänta dig:
- Lägre snitt (6-7/10) — kalibreringen är inte uppe ännu
- Många graf-flaggor (canon växer)
- Flera lärdomar (learnings.md fylls)

Efter 2-3 kapitel ska snittet ligga 8.5-9.

---

## 10. Success Metrics

### 10.1 Per-kapitel-metrics

| Metric | Mål | Mätning |
|---|---|---|
| Snitt-betyg | ≥9.0 | Genomsnitt över 8 axlar efter FAS 3 |
| NAGELFAREN-godkännande | ✓ | Ingen veto efter 1-2 redaktörsrundor |
| Tics inom tak | ✓ | grep-tics.sh visar inga `[ÖVER TAK]` |
| Graf-uppdaterad | ✓ | Alla nya entiteter i grafen efter FAS 6 |
| Författar-beslut antal | Minimalt | Flaggade beslut bör avta över tid |

### 10.2 Boknivå-metrics

| Metric | Mål | Mätning |
|---|---|---|
| Snitt över alla kapitel | ≥9.0 | Förläggarpassets sammanställning |
| Förläggar-rek | A | Helhets-bedömning |
| Frekvens-tics inom tak | ✓ | Tics-katalog grep över hela boken |
| Canon-konsistens | 100% | Graf-validator visar inga broken refs |

### 10.3 Process-metrics

| Metric | Mål | Mätning |
|---|---|---|
| NAGELFAREN/redaktör-gap | <1.0 | Differens mellan deras betyg sjunker över rundor |
| Tid per kapitel | <2h (efter inkörning) | Inklusive alla 4 sub-pass |
| Författar-flaggor per kapitel | <3 | Beslut som måste skickas till författare |
| Lärdomar per kapitel | 2-5 | Nya mönster i learnings.md per pass |

### 10.4 Bok-till-bok-metrics

| Metric | Mål | Mätning |
|---|---|---|
| Bok 2 snitt från start | ≥8.0 (mot bok 1:s ~6) | Första-kapitlets-betyg på bok 2 |
| Bok 2 totalbetygsprocess | 5x snabbare | Tid att nå A-rek |
| Återanvändning av learnings | >70% | Procent regler från bok 1 som tillämpas |

---

## 11. Roadmap

### 11.1 v1.1 (klar, 2026-05-19) — KOMPLETT RAMVERK

Det som är implementerat och validerat:
- ✓ **13 aktiva roller** (5 grund + 8 utökning)
  - Plot-arkitekt, Researcher, Writer, Redaktör, Prosa-städ, Dialog-coach, NAGELFAREN, Förläggare, Sensitivity-läsare, Graf-vakt, Världsbyggare, Audiobook-direktör, Marknadsförare
- ✓ Kunskapsgraf med 9 fil-typer
- ✓ Layered markup-pipeline
- ✓ Query-lager v1 (3 queries)
- ✓ Process FAS 0-9 + löpande graf-vakt + separat världsbyggare
- ✓ Apple Books-integration
- ✓ Tics-katalog + grep-script
- ✓ Architecture decision records (ADR 0001, 0002)
- ✓ Audiobook-pipeline (parse → director → chunker → TTS → audio)

### 11.2 v1.2 (klar, 2026-05-19) — KOMPLETT PLATTFORM

- ✓ **9 lager artefakter** specificerade (~50 artefakt-templates)
  - Lager 1 Koncept (8 filer), 2 Värld (4 + research), 3 Karaktärer (4 + deepening), 4 Plot (16 filer inkl scenkort, klocka, clue-economy, antagonist-tidslinje), 5 Kontinuitet (5), 6 Röst/stil (11), 7 Skrivande (4), 8 Editorial (14), 9 Meta (9)
- ✓ **Hantverkstekniker (Del III) integrerade** i `.context/hantverk/`
  - `tekniker.md` A-K, `kvalitetsgrindar.md` I.1-I.7, `snabb-checklista.md` L, `anti-monster.md` J
- ✓ Mapping roll → lager (sektion 7.0)
- ✓ Kvalitetsgrindar mellan FAS-stegen (sektion 8.13)
- ✓ Alla 13 roller pekar mot relevanta hantverk-filer

### 11.3 v1.3 — Verktygsintegration

- Plot-arkitekt v2 med automatiserad outline-generering från premise
- Researcher v2 med automatiska web-queries och source-validering
- Dialog-coach integration med character-deepening pattern-matching
- Mall-projekt (template repo)
- Query-lagret v2 — relationships, place-tracking, plot-skeleton

### 11.4 v1.4 — Cross-bok

- Cross-bok learnings-bibliotek (delat mellan projekt)
- Världsbyggare v2 med multi-bok-graf
- World-bible-format utökat med tidsmaskin-support

### 11.5 v2.0 — Extern integration

- Eventuell extern publikation-integration
- Multi-författar-collaboration-stöd
- Cloud-graf med flera författare

---

## 11a. Hantverkstekniker (Del III)

Mappen `.context/hantverk/` innehåller tekniker som *inte är artefakter* utan *checklistor och agent-prompts* för meningsnivå, scennivå, kapitelnivå. Alla roller pekar mot dessa filer.

### 11a.1 Filer

- `tekniker.md` — alla tekniker A-K
  - **A. Meningsnivå** — specificitet över generalitet, verbet gör jobbet, konkret över abstrakt, sensorisk grund, meningsrytm, förbjudna hedging-ord, klichémedvetenhet
  - **B. Scennivå** — varje scen har en fråga, scene & sequel (Swain), iceberg-principen (Hemingway), in sent / out early, inga exposition-dumps, subtext > text, negativrum, sensoriska ankare
  - **C. Karaktärnivå** — karaktären ÄR plotten, varje karaktär har en agenda, distinkt språk, visa karaktär genom handling, blinda fläckar
  - **D. Tidsnivå** — tidskompression, tidsdilation, white space som tidsmarkör, tense-disciplin
  - **E. POV-nivå** — POV-disciplin, free indirect discourse, multipla POV-disciplin (ingen headhopping)
  - **F. Strukturnivå** — Tjechovs gevär, setup-payoff-balans, inga heliga scener, kapitel-cliffhangers (med variation), tre-akt fraktalt
  - **G. Genre-specifika tekniker (thriller)** — tickande klockor, plant och pay-off i tempo, two-track narratives, ticking suspicion (Hitchcock), cold open, recurring locations as anchors
  - **H. AI-prosa-fällor** — metaberättarröst, föraningar med exakta siffror, alla karaktärer låter likadant, lila prosa, exposition dumps, telegrafering av slut, "och sedan"-struktur, abstraktion när konkret är möjligt, generisk dialog, tic-repetition
  - **K. Svenska genrekonventioner** — thriller-traditionen (Larsson/Mankell/Persson/Läckberg/Lapidus/Kepler/Marklund), samhälls-detaljer, dialog-konvention (talstreck), titel-tradition

- `kvalitetsgrindar.md` — I.1-I.7 (se sektion 8.13)

- `snabb-checklista.md` — L: 17 kontroller per kapitel (~15 min)
  - Scen-fråga ställd vid öppning + besvarad vid slut
  - Sensorisk detalj som inte är visuell
  - POV konsekvent
  - Varje karaktär har en agenda
  - Subtext > text i dialog
  - Meningsrytm varierad
  - Inga adverb som modifierar svaga verb
  - Inget exposition-dump
  - Sensoriskt ankare i öppningen
  - Karaktärsdistinkt språk
  - Inga metaberättar-fraser
  - Klocka/threat synlig om relevant
  - Setups planterade noterade
  - Payoffs noterade
  - Continuity inte bruten
  - Slutet får läsaren att vilja vända blad

- `anti-monster.md` — J: åtta anti-mönster
  1. Karaktären upptäcker viktig information ensam i ett rum (drama dödad)
  2. Plötslig förvandling utan plantering (fusk)
  3. Tillfälligheter som löser plot (förbjudet — får bara skapa problem)
  4. Missförstånd-plot som löses av ett enkelt samtal
  5. Tidsglapp som ursäkt ("hon hade glömt") — lat plot
  6. Ondskan-utan-skäl (antagonister måste ha legitima motiv för sig själva)
  7. Sidekick som dör för pathos
  8. Författarens favoriter (murder your darlings)

### 11a.2 Integration i roller

| Roll | Hantverk-filer som läses |
|---|---|
| Writer | `tekniker.md` A-G, K | `anti-monster.md` |
| Redaktör | `tekniker.md` A-K, `snabb-checklista.md` L, `anti-monster.md` J, `kvalitetsgrindar.md` I.5 |
| Prosa-städ | `tekniker.md` A, B, H |
| Dialog-coach | `tekniker.md` B.5-B.6, C, E, H.3, H.9, K.3 |
| NAGELFAREN | hela `hantverk/` (verifierar att andra roller faktiskt applicerat) |
| Förläggare | `tekniker.md` F, `kvalitetsgrindar.md` I.6 |
| Plot-arkitekt | `tekniker.md` B, F, G, `kvalitetsgrindar.md` I.2, I.3 |
| Sensitivity-läsare | `tekniker.md` C, K |
| Världsbyggare | `kvalitetsgrindar.md` I.1, I.7 |

### 11a.3 Filosofisk slutpunkt (Del III.M)

> Bra prosa är inte *tekniker.* Bra prosa är *uppmärksamhet.* Det som tekniker gör är att frigöra författaren från att tänka på saker som kan bli vana. När man inte längre tänker på meningsrytm eller specificitet eller subtext, då kan man tänka på det som inte kan reduceras till teknik: människan, situationen, ögonblicket.
>
> Tekniker är hantverkets nedre nittio procent. Den övre tio är vad som inte kan läras.
>
> Men nittio procent är värt att lära.

Det är dit ramverket siktar: automatisera de nittio så att författaren får tankeutrymme för de tio.

---

## 12. Risker och mitigation

### 12.1 Tekniska risker

| Risk | Sannolikhet | Konsekvens | Mitigation |
|---|---|---|---|
| LLM-uppgradering bryter prompt-templates | Medel | Hög | Versionkontrollera roll-briefer, regression-testa vid uppgradering |
| Graf-schema driftar mellan kapitel | Medel | Hög | Schema-validator i CI; ADR för schema-ändringar |
| Subagenter går "off-script" | Låg | Medel | Tydliga briefer, default-betyg 7, NAGELFAREN-veto |
| Cache-filer commitas av misstag | Medel | Låg | .gitignore + pre-commit hook |

### 12.2 Process-risker

| Risk | Sannolikhet | Konsekvens | Mitigation |
|---|---|---|---|
| Författare hoppar över FAS 5/6 | Hög | Hög | STOPP-villkor i process.md, hårda regler |
| Self-grading-bias återkommer | Medel | Medel | NAGELFAREN-rollen, kalibreringssnitt mätt över tid |
| POV-läckage smyger igenom | Medel | Medel | Dialog-coach-roll (v1.2), character-deepening läses FÖRE skrivande |
| Canon-konflikter mellan kapitel | Låg (med graf) | Hög | Graf-validator, FAS 6 obligatorisk |

### 12.3 Strategiska risker

| Risk | Sannolikhet | Konsekvens | Mitigation |
|---|---|---|---|
| Ramverket fördröjer kreativt flöde | Medel | Hög | Minimal start (10 filer), bygg ut efter behov |
| Författare blir verktygsberoende | Låg | Medel | Verktyg är förslag, författare beslutar |
| AI-genererat innehåll blir homogent | Medel | Hög | Stark character-deepening, anti-mönster-disciplin, författar-fingeravtryck |

---

## 13. Appendix

### Appendix A: CLAUDE.md template

```markdown
# CLAUDE.md — Stående instruktioner för <BOK-TITEL>

Läs detta först varje session.

## Vad detta är

<Beskriv premisse, genre, omfattning, ambition>

## De N distinguishing features

1. <Vad gör din bok unik>
2. <...>
3. <...>

## Process

Hela förbättringsloopen FAS 1-7 finns i `.context/process.md`.

### Snabb sammanfattning av rollerna (13 totalt)

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

## Canon

Allt fakta-relaterat i `.context/canon.md`.

## Användarens hårda no:s

- <Logiska tabbar typ X>
- <Författare-på-promenad-känsla>
- <Verkliga personer i fiktion>

## Resurser — komplett index

### Process & roller
- `.context/process.md`
- `.context/roles/writer.md`
- `.context/roles/redaktor.md`
- `.context/roles/prosa-stad.md`
- `.context/roles/nagelfaren.md`
- `.context/roles/forlaggare.md`

### Canon & fakta
- `.context/canon.md`
- `.context/story-graph/`

### Tools
- `.context/tools.md`
- `.context/tics-katalog.md`
- `scripts/`

### Lärdomar & rapporter
- `.context/learnings.md`
- `.context/redaktor-rapporter/`
- `.context/prosa-stad-rapporter/`
- `.context/nagelfaren-rapporter/`
- `.context/forlaggar-rapporter/`
```

### Appendix B: character-deepening template

```markdown
# CHARACTER DEEPENING — <Namn>

> Writer läser FÖRE kapitel där karaktären är POV eller central.

## En mening
<Karaktärens själ i en mening>

## Yttre mål (i plottet)
<Vad gör karaktären i historien>

## DRIVKRAFT — det egentliga
<Det djupare. Vad vill hen som hen inte säger>

## SÅRBARHET — det mänskliga
<Vad gör hen mänsklig. Minst 3 saker>

## STYRKOR (vardagliga)
<Inte hjältemodiga. Tålmodighet, observation, intuition>

## SVAGHETER (vardagliga)
<Inte oduglig. Långsam, tvekande, missar familjehändelser>

## QUIRKS — det minnesvärda
<Specifikt. Minst 5 quirks>

## RELATIONER (som format)
<Familj, kollegor, vänner>

## GILLAR
<Vardagspreferenser>

## OGILLAR
<Det hen undviker>

## PRINCIPER (vad hen ALDRIG gör)
<Linjer. Minst 3>

## RÖST-CANON
- **Talspråk:** <Hur låter hen>
- **Tankespråk (POV):** <Hur låter inre rösten>
- **Typiska meningar:** <3-5 signatur-meningar>
- **Förbjudna konstruktioner:** <Vad hen ALDRIG skulle säga>

## TRÅD-KARTA
| Kapitel | Plot-funktion | Drivkraft-testning | Sårbarhets-exponering |
|---|---|---|---|

## SLUT-BÅGEN
<Var hamnar karaktären>

## ANTI-MÖNSTER — vad karaktären INTE är
<Vad du måste undvika>

## RISKER FÖR WRITER
<Konkreta fallgropar>
```

### Appendix C: roles/redaktor.md template (utdrag)

Se exempelfil från befintligt ramverk. Kärninnehåll:

```markdown
# REDAKTÖR

## Din roll
Världens skarpaste svenska <genre>-redaktör.

## Läs först
- CLAUDE.md
- .context/process.md
- .context/canon.md
- .context/learnings.md
- character-deepening för POV
- Kapitlet

## Output
.context/redaktor-rapporter/kapitel-NN-granskning-vN.md

## 8 axlar
Stil, Atmosfär, POV, Cliffhanger, Spänning, Geografi/fakta, Logik, Klarhet

## Default-betyg
7. 8 bra. 9 exceptionellt och kräver dokumentation. 10 finns inte.

## Sektion 1a — 12 mening-för-mening-tester
<Lista>

## Sektion 1c — 5 helhetskontroller
<Lista>

## Format för rapporten
<Mall>
```

### Appendix D: events.json schema

```json
{
  "evt-mans-funnen-smojen": {
    "id": "evt-mans-funnen-smojen",
    "name": "Måns hittas vid Smöjen",
    "timestamp": "2026-06-22T06:14:00",
    "location_id": "loc-smojen-kalkbrott",
    "participant_ids": ["char-britta-olofsson", "char-daniel-wallin"],
    "chapter": "kapitel-01",
    "secret_outcomes": [
      {"secret_id": "sec-mans-dod", "becomes_known_to": ["char-britta-olofsson"]}
    ],
    "summary": "Britta Olofsson hittar Måns flytande i kalkbrottet. Ringer polisen.",
    "pov": "char-daniel-wallin"
  }
}
```

### Appendix E: secrets.json schema (med strukturerad known_to)

```json
{
  "sec-mans-har-bevis-pa-vatten-affar": {
    "id": "sec-mans-har-bevis-pa-vatten-affar",
    "name": "Måns har dokumentation av OstseeKalk-affären",
    "category": "plot-driver",
    "known_to": [
      {
        "character_id": "char-mans",
        "known_since": "2025-12-15",
        "status": "deceased",
        "notes": "Etablerade kunskap som motiv för mord"
      },
      {
        "character_id": "char-tobias",
        "known_since": "2026-04-22",
        "status": "alive",
        "notes": "Måns informerade Tobias vid Rondo-mötet"
      },
      {
        "character_id": "char-erika",
        "known_since": "2026-06-23T19:00",
        "status": "alive",
        "notes": "Erika upptäckte via dokumentanalys"
      }
    ],
    "anar": [
      {
        "character_id": "char-daniel",
        "known_since": "2026-06-25T14:30",
        "notes": "Misstänker via Hansén-spår"
      }
    ]
  }
}
```

### Appendix F': Komplett artefakt-tabell (v1.2)

Översikt över alla ~50 artefakter. Skapas-av / konsumeras-av / när-i-processen.

| Artefakt | Lager | Skapas av | Konsumeras av | När |
|---|---|---|---|---|
| `koncept/premiss.md` | 1 | Författare | Plot-arkitekt, Writer | Innan FAS 0 |
| `koncept/logline.md` | 1 | Författare/Marknadsförare | Plot-arkitekt, Marknadsförare | FAS 0, finslipas FAS 9 |
| `koncept/genre.md` | 1 | Författare | Alla | Innan FAS 0 |
| `koncept/form.md` | 1 | Författare | Plot-arkitekt | Innan FAS 0 |
| `koncept/genre-kontrakt.md` | 1 | Plot-arkitekt | Writer, Redaktör | FAS 0 |
| `koncept/central-fraga.md` | 1 | Plot-arkitekt | Writer, Förläggare | FAS 0 |
| `koncept/teman.md` | 1 | Författare | Alla | Innan FAS 0 |
| `koncept/series-promise.md` | 1 | Världsbyggare | Plot-arkitekt | Före bok 1 |
| `varld/tidsperiod.md` | 2 | Författare/Världsbyggare | Researcher, Writer | Före FAS 0 |
| `story-graph/timeline.json` | 2 | Plot-arkitekt | Alla | FAS 0, löpande |
| `varld/geografi.md` | 2 | Researcher | Writer | FAS 0 |
| `research-dossier/<amne>.md` | 2 | Researcher | Writer, Redaktör | FAS 0 + on-demand |
| `story-graph/locations.json` | 2 | Graf-vakt/Researcher | Alla | Löpande |
| `story-graph/organizations.json` | 2 | Graf-vakt/Researcher | Alla | Löpande |
| `story-graph/characters.json` | 3 | Författare/Graf-vakt | Alla | Löpande |
| `story-graph/character-deepening/<id>.md` | 3 | Författare | Writer, Dialog-coach, NAGELFAREN | Innan POV-kapitel |
| `story-graph/relationships.json` | 3 | Graf-vakt | Plot-arkitekt, Writer | Löpande |
| `stil/roster/<namn>.md` | 3, 6 | Författare | Writer, Dialog-coach | Före prosa |
| `plot/through-line.md` | 4 | Plot-arkitekt | Förläggare, Writer | FAS 0 |
| `plot/bagar.md` | 4 | Plot-arkitekt | Writer, Förläggare | FAS 0 |
| `plot/trilogi.md` | 4 | Världsbyggare | Plot-arkitekt | Före serie |
| `plot/bok-N/struktur.md` | 4 | Plot-arkitekt | Writer, Förläggare | FAS 0 per bok |
| `plot/bok-N/inciting-incident.md` | 4 | Plot-arkitekt | Writer | FAS 0 |
| `plot/bok-N/kapitelplan.md` | 4 | Plot-arkitekt | Writer | FAS 0 |
| `plot/bok-N/scenkort/kap-NN-scen-Y.md` | 4 | Plot-arkitekt | Writer | FAS 0 omedelbart före prosa |
| `plot/bok-N/spanning.md` | 4 | Plot-arkitekt | Förläggare | FAS 0 |
| `plot/bok-N/clue-economy.md` | 4 | Plot-arkitekt | Writer, Förläggare | FAS 0, uppdateras |
| `plot/bok-N/tension-tracker.md` | 4 | Plot-arkitekt | Writer | FAS 0 |
| `plot/bok-N/klocka.md` | 4 | Plot-arkitekt | Writer | FAS 0 |
| `plot/bok-N/informationsflode.md` | 4 | Plot-arkitekt | Writer, NAGELFAREN | FAS 0, löpande |
| `plot/bok-N/antagonist-tidslinje.md` | 4 | Plot-arkitekt | Writer | FAS 0 |
| `plot/bok-N/try-fail.md` | 4 | Plot-arkitekt | Writer | FAS 0 |
| `plot/bok-N/cold-open.md` | 4 | Plot-arkitekt | Writer | FAS 0 |
| `plot/bok-N/two-track.md` | 4 | Plot-arkitekt | Writer | FAS 0 om relevant |
| `story-graph/knowledge-matrix.md` | 5 | Graf-vakt | Writer, NAGELFAREN | Löpande |
| `foreshadowing/payoff-tracker.md` | 5 | Plot-arkitekt/Förläggare | Förläggare | Löpande |
| `story-graph/fact-check.md` | 5 | Researcher/Graf-vakt | Redaktör | Löpande |
| `story-graph/dodslista.md` | 5 | Graf-vakt | Writer | Löpande |
| `story-graph/secrets.json` | 5 | Graf-vakt | Alla | Löpande |
| `story-graph/style-guide.md` | 6 | Författare | Writer, Redaktör, Dialog-coach | Före prosa |
| `stil/undvik.md` | 6 | Redaktör/Författare | Writer | Före prosa, uppdateras |
| `stil/motiv.md` | 6 | Författare | Writer, Förläggare | Löpande |
| `stil/inspiration/<forfattare>.md` | 6 | Författare | Writer | Före prosa |
| `stil/platser/<plats>.md` | 6 | Writer/Författare | Writer | Löpande |
| `stil/rytm.md` | 6 | Författare | Writer | Före prosa |
| `stil/dialog.md` | 6 | Författare | Writer, Dialog-coach | Före prosa |
| `stil/pov-bok-N.md` | 6 | Författare | Writer, Dialog-coach | Före prosa |
| `stil/aterkommande.md` | 6 | Världsbyggare | Writer | Före bok 1 |
| `tics-katalog.md` | 6 | Författare/Redaktör | grep-tics.sh, Redaktör | Löpande |
| `manuskript/kapitel-NN.md` | 7 | Writer | Alla granskande | FAS 2 |
| `prosa-anteckningar/kapitel-NN.md` | 7 | Writer | Writer (v2) | Under skrivande |
| `redaktor-rapporter/*.md` | 8 | Redaktör | NAGELFAREN, Författare | FAS 3 |
| `prosa-stad-rapporter/*.md` | 8 | Prosa-städ | Författare | FAS 3 |
| `dialog-coach-rapporter/*.md` | 8 | Dialog-coach | NAGELFAREN, Författare | FAS 3 |
| `nagelfaren-rapporter/*.md` | 8 | NAGELFAREN | Författare, Redaktör | FAS 3 |
| `forlaggar-rapporter/*.md` | 8 | Förläggare | Författare | FAS 4 |
| `sensitivity-rapporter/*.md` | 8 | Sensitivity-läsare | Författare, Förläggare | FAS 4 |
| `forlag/lektorsbrev-bok-N.md` | 8 | Extern lektör | Författare | Efter FAS 4 |
| `forlag/fixes-bok-N.md` | 8 | Redaktör | Författare | Efter lektörsbrev |
| `forlag/respons-bok-N.md` | 8 | Författare | Förlag | Efter feedback |
| `forlag/revisions-tracker.md` | 8 | Författare | Förläggare | Under revision |
| `forlag/beta/<lasare>-bok-N.md` | 8 | Beta-läsare | Författare | Efter A-rek |
| `forlag/manuskriptformatering.md` | 8 | Författare | Förlag | Före inlämning |
| `forlag/baksidestext.md` | 8 | Författare/Marknadsförare | Förlag | Tidigt + sent |
| `forlag/loglinetest.md` | 8 | Författare | Författare | Löpande diagnostik |
| `scripts/audiobook/pronunciations.json` | 8 | Audiobook-direktör | TTS-pipeline | FAS 8 |
| `scripts/audiobook/character-voices.json` | 8 | Audiobook-direktör | TTS-pipeline | FAS 8 |
| `audiobook/*.md` | 8 | Audiobook-direktör | TTS-producent | FAS 8 |
| `marknadsforing/pitch-pack-*.md` | 8 | Marknadsförare | Författare, Agent, Förlag | FAS 9 |
| `meta/beslutslogg.md` | 9 | Författare | Alla | Löpande |
| `meta/oppna-fragor.md` | 9 | Författare | Alla | Löpande |
| `meta/parkering.md` | 9 | Författare | Författare | Löpande |
| `meta/bruttolistor/` | 9 | Författare | Författare | Löpande |
| `meta/canon.md` | 9 | Världsbyggare | Alla | Löpande |
| `meta/hantverksstandarder.md` | 9 | Författare | Writer, Redaktör | Tidigt |
| `meta/ambition.md` | 9 | Författare | Författare | Tidigt, omläst |
| `docs/adr/*.md` | 9 | Författare | Alla | Vid större beslut |
| `learnings.md` | 9 | Alla roller | Alla | Löpande |
| `hantverk/tekniker.md` | n/a | Författare | Alla | Statisk referens |
| `hantverk/kvalitetsgrindar.md` | n/a | Författare | Alla | Statisk referens |
| `hantverk/snabb-checklista.md` | n/a | Författare | Writer, Redaktör | Per kapitel |
| `hantverk/anti-monster.md` | n/a | Författare | Writer, Förläggare | Statisk referens |

### Appendix F: Kvalitets-checklista

Innan ett kapitel anses klart (FAS 3 + 4):

- [ ] Writer-utkast producerat
- [ ] Redaktör-rapport skriven (8 axlar med betyg + 1a/1c-fynd)
- [ ] Redaktör-fixar applicerade
- [ ] Prosa-städ-rapport skriven (6 frågor per mening)
- [ ] Prosa-städ-fixar applicerade
- [ ] NAGELFAREN-rapport skriven (min 5 missar eller godkänd)
- [ ] NAGELFAREN-fixar applicerade (om missar)
- [ ] Redaktör-pass v2 (om NAGELFAREN-veto)
- [ ] Alla 8 axlar ≥9.0
- [ ] grep-tics visar inga `[ÖVER TAK]`
- [ ] Canon-konsistens verifierad mot grafen
- [ ] FAS 5 lärdomar in i learnings.md
- [ ] FAS 6 graf-uppdatering klar
- [ ] Författar-beslut flaggade (om några)
- [ ] Commit gjord med tydligt meddelande

---

## 14. Versionhistorik

| Version | Datum | Ändring |
|---|---|---|
| 1.0 | 2026-05-19 | Initial version, 5 roller, validerad mot *Marken under marken* |
| 1.1 | 2026-05-19 | Komplett ramverk: 13 roller, alla aktiva. FAS 0-9 + löpande graf-vakt + separat världsbyggare. Plot-arkitekt, researcher, dialog-coach, sensitivity-läsare, graf-vakt, världsbyggare, audiobook-direktör, marknadsförare tillagda. |
| 1.2 | 2026-05-19 | Komplett plattform — 9 lager artefakter, Del III hantverkstekniker integrerade, ~50 nya artefakt-templates. Sektion 3a (artefakt-arkitektur), 7.0 (roll→lager-mapping), 8.13 (kvalitetsgrindar I.1-I.7) och 11a (hantverkstekniker A-K + J + L) tillagda. Nya mappar: `koncept/`, `varld/`, `plot/`, `stil/`, `forlag/`, `meta/`, `hantverk/`, `prosa-anteckningar/`, `foreshadowing/`. |

---

## 15. Licens och användning

Detta PRD är skrivet av Fabian von Tiedemann och får användas, anpassas och distribueras fritt för icke-kommersiell såväl som kommersiell användning. Ingen attribuering krävs men uppskattas.

Idéerna och processen är inte unika — de är synteser av etablerad mjukvaru-engineering, lean methodology, agile process design, och beprövad redaktörspraxis. Innovationen ligger i att applicera dessa systematiskt på författarskap.

---

**Slut på PRD.**
