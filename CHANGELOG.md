# CHANGELOG

Alla större ändringar i Programmatic Writing Stack dokumenteras här. Följer [Keep a Changelog](https://keepachangelog.com/)-formatet.

## [2.1.0] — 2026-10-03

### Lagt till
- Förslag från användarna: skillen fångar förslag om verktyget i samtalet, `bok forslag` skickar dem och visar deras status, och `bok init` berättar vilka som införts.
- Mottagare för förslagen (`mottagare/`, Cloudflare Worker) och en underhållsskill som gör förslag till ändringar och releaser.

## [2.0.0] — 2026-10-03

**Ramverket blir verktyget `bok`, som dras in i valfritt repo.**

### Lagt till
- `bok init` (installera och uppgradera), `bok status`, `bok mall`, `bok graph`, `bok tics`, `bok validate`, `bok rapport spara`, `bok annotations`.
- Skillen `bok`: fritt samtal, inkorg, stilverkstad, grind före första kapitlet och skrivloop.
- Bågar i grafen (`threads.json`) och kontroll av plan mot utfall.
- Tillvalsmoduler: spänning, serie, förlag, graf-extra, audiobook, marknad.

### Ändrat
- Bokens filer ligger i `bok/` i stället för `.context/` (som Conductor git-ignorerar).
- Tretton roller blir sex i skrivloopen och fem vid behov, som Claude Code-subagenter.
- Skrivloopen tar slut: godkänt vid minst 8 på varje axel, högst två revisioner, sedan bestämmer författaren.
- Rollerna läser sammanfattningar och `bok graph context` i stället för hela manuset.
- Mallar och hantverk är genreneutrala och rensade från tidigare böcker.

### Borttaget
- `init-writing-stack.sh`, `upgrade-existing-project.sh`, `templates/`, shell-scripten och layered markup (`render`, `tag`).
- v1.2-dokumentationen är flyttad till `docs/arkiv/v1.2/`.

## [1.2] — 2026-05-19

**Komplett plattform — 13 roller, 9 lager artefakter, Del III hantverkstekniker integrerade.**

### Lagt till
- 8 nya roller med separata briefer:
  - Plot-arkitekt (FAS 0)
  - Researcher (FAS 0+ on-demand)
  - Dialog-coach (FAS 3, POV-veto)
  - Sensitivity-läsare (FAS 4, publikations-veto)
  - Graf-vakt (LÖPANDE)
  - Världsbyggare (separat, för uppföljare)
  - Audiobook-direktör (FAS 8)
  - Marknadsförare (FAS 9)
- 9 lager artefakter med ~50 templates:
  - Lager 1 Koncept (premiss, logline, genre, form, genre-kontrakt, central-fraga, teman)
  - Lager 4 Plot (through-line, scenkort, clue-economy, klocka, tension-tracker, m.fl.)
  - Lager 6 Stil (motiv, rytm, dialog, POV, inspiration, platser)
  - Lager 8 Editorial-utbyggnad (respons, revisions-tracker, manuskriptformatering, beta)
  - Lager 9 Meta (beslutslogg, ambition, hantverksstandarder, parkering)
- Hantverk-bibliotek (`.context/hantverk/`):
  - `tekniker.md` — Del III A-K
  - `kvalitetsgrindar.md` — Del III I.1-I.7
  - `snabb-checklista.md` — Del III L (17 punkter per kapitel)
  - `anti-monster.md` — Del III J.1-J.8
- `scripts/init-writing-stack.sh` — initierar nytt bokprojekt från templates
- Kvalitetsgrindar (I.1-I.7) integrerade i process.md mellan faser
- FAS 0 (Plot + Research), FAS 8 (Audiobook), FAS 9 (Marknadsföring) tillagda

### Ändrat
- CLAUDE.md från monolitisk till slim index (~150 rader)
- Per-roll separata briefer ersätter sammanslagen `editor-brief.md`
- Default-betyg 7 (inte 9) som standard för alla axlar
- Story-graph: secrets.json med strukturerad `known_to[]`-array

### Borttaget
- (inget — alla ändringar är additiva)

## [1.1] — 2026-05-19 (tidigare på dagen)

**Komplett ramverk: 13 aktiva roller.**

### Lagt till
- ADR 0001 — layered markup-pipeline + validator
- ADR 0002 — story-graph query-lager
- `scripts/graph-query.py` med 3 queries: `who-knows`, `who-was-where`, `thread`
- `scripts/render-manuscript.py`, `validate-manuscript.py`, `tag-manuscript.py`
- NAGELFAREN-rolldefinition (adversarial meta-granskning)
- Tics-katalog + `grep-tics.sh`

### Ändrat
- Roll-namn standardiserade
- Process-flöde utökat från FAS 1-7 till FAS 0-9

## [1.0] — 2026-05-18

**Initial version, validerad mot *Marken under marken*.**

### Lagt till
- 5 grundroller: Writer, Redaktör, Prosa-städ, NAGELFAREN, Förläggare
- `.context/process.md` med FAS 1-7
- `.context/canon.md` + `.context/learnings.md`
- Story-graph-arkitektur (characters, events, locations, secrets, relationships)
- `scripts/books-annotations.sh` för läsarnoter
- Grundläggande PRD och HTML-guide

### Validerat
- 26 enheter (prolog + 22 kap + epilog + 2 interludier)
- ~70 000 ord
- Snitt 9.13/10 efter FAS 3-pass
- NAGELFAREN-kalibrering: differens redaktör/verklighet sjönk 2.1 → <0.5

---

**Planerade kommande versioner:**

## [1.3] — Planerad

- Cross-bok learnings-bibliotek (lärdomar som ärvs mellan bokprojekt)
- World-bible-format för flerboks-serier
- Automatisk plot-skeleton-query (`graph-query.py plot-skeleton --thread X`)

## [1.4] — Planerad

- Web-baserad onboarding-wizard
- Validation-CI för bokprojekt (GitHub Actions-template)
- Cross-projekt scripts (sync-improvements between bokprojekt)

## [2.0] — Långsiktigt

- Multi-författar-stöd (kollaborativt skrivande)
- Internationalisering (engelsk/tysk översättning av briefer)
- Integration med Scrivener/Obsidian som export-mål
