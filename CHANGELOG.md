# Changelog

Alla ändringar i `bok` som märks för den som använder verktyget dokumenteras här.

Formatet följer [Keep a Changelog](https://keepachangelog.com/sv/1.1.0/) och versionerna följer [semantisk versionshantering](https://semver.org/lang/sv/). Kategorierna heter Lagt till, Ändrat, Fixat, Borttaget och Säkerhet. Nya ändringar skrivs under [Unreleased] och flyttas till en version när den släpps; se `docs/utveckla-och-releasa.md`.

## [Unreleased]

## [2.5.0] — 2026-10-04

### Lagt till
- Röstlabbet (`bok mall rostlabb`): sök bokens röst och form genom att välja bland varianter i generationer, med recept av drag från förebilder och slumpade frön, en kontroll som visar AI-genomsnittet och pekningar på det som lever och det som är dött. Resultatet blir ett recept i `rost.md`, en provbank och en formlag.
- `bok rost profil`, `bok rost drift` och `bok rost urval`: röstens profil, ett kapitel mätt mot rösten och AI-genomsnittet (och pastisch), och provstycken som Writer läser inför kapitlet.
- `bok fron` har klasserna `rostdrag`, `formgrepp` och `kalla`.
- Scenkortet har fälten `vagar` (vad kapitlet vågar) och `lage` (stilla eller under tryck).

### Ändrat
- Med Röstlabbet pekar författaren ut levande och döda ställen efter första granskningen. Levande ställen är låsta: `bok validate` stoppar kapitlet om de ändrats, och granskarna får inte kräva ändringar i dem. Granskarnas rapporter har avsnitten Mest levande och Mest döda.

## [2.4.0] — 2026-10-04

### Lagt till
- Förlagor: en karaktär kan bygga på en verklig person. Researcher tar fram ett porträtt ur intervjuer och vad andra säger, med källor, i `bok/karaktarer/forlagor/`. `bok validate` stoppar kapitel där förlagans namn står, och sensitivitetsläsaren läser planen när boken har förlagor.
- Karaktärsverkstaden: personer prövas i tre korta scener under tryck. Karaktärsmallen har nya, frivilliga rubriker: förlaga, motsägelser, självbild och andras bild, det hen döljer, under tryck, vardag och öppet.
- Vägval: flera distinkta alternativ för en fråga i boken, från rollerna Vägval och Idékritiker, med slumpade frön från `bok fron`. Varven sparas i `bok/vagval/`.

### Fixat
- `bok validate` stoppar förbjudna namn också i genitiv ("Olof Palmes").

## [2.3.1] — 2026-10-04

### Fixat
- Guiden `docs/google-maps.md` följer hur Google Cloud faktiskt ser ut: projektnamn på minst 4 tecken, nyckeln som skapas automatiskt och ska begränsas, Street View som måste aktiveras för sig, budget med bara larm, provperioden och ett avsnitt om vad man gör när något inte fungerar.
- `bok karta status` och de andra kommandona säger nu om ett API inte är aktiverat i projektet eller om nyckelns begränsningar stoppar det, i stället för ett gemensamt meddelande, och hänvisar till rätt steg i guiden.
- `bok karta` kraschar inte längre på oväntade svar från Google eller på `--mellanrum nan`, och Ctrl-D eller Ctrl-C vid `bok karta nyckel` avbryter utan felutskrift.
- Avbryts `bok karta gatuvy` av ett fel efter att några bilder hämtats visas var de ligger. `bok karta stada` räknar bara mappar som faktiskt togs bort.

## [2.3.0] — 2026-10-04

### Lagt till
- Restider och miljöer från Google Maps med en egen nyckel. `bok karta restid` visar dagens restid till fots, med cykel, bil och kollektivt. `bok karta gatuvy` hämtar gatubilder på en plats eller längs en rutt, som Claude tittar på och beskriver med egna ord i `bok/varld/platser/<id>.md`. Bilder och restider sparas aldrig i boken. Guiden `docs/google-maps.md` visar hur man skaffar nyckeln och lägger in den med `bok karta nyckel`; `bok karta status` visar om den fungerar.
- Platsfiler med *Bokens tid* och *Idag*. `bok graph context` visar dem för kapitlets platser, och hur många år som skiljer gatubildernas fotodatum från kapitlets tid.
- Platsens historia: Researchern söker i öppna arkiv efter hur en plats såg ut vid bokens tid. `bok bild` hämtar en arkivbild tillfälligt så att Claude kan titta på den.
- `adress`, `lat` och `lng` för platser i grafen.

### Ändrat
- Efter ett godkänt scenkort erbjuder Claude att ta fram miljön för kapitlets platser. Plot-arkitekten tar med restider som egna formuleringar i scenkortet, och Writer och Redaktören skiljer på bokens tid och dagens värld.

## [2.2.1] — 2026-10-04

### Fixat
- `bok validate`, `bok graph karaktar` och `bok graph var` kraschar inte längre när grafens json har handredigerats med fel typ, t.ex. `alias` som text i stället för lista eller `fakta` som lista i stället för objekt. Sådana värden visas som de är eller hoppas över.

## [2.2.0] — 2026-10-03

### Lagt till
- Datum och åldrar: `fodd`, `dod` och `datum` i grafen, `datum` och `tillbakablick` i scenkortet. `bok graph context` visar åldrar; `bok validate` stoppar tidsfel och varnar för åldrar i texten som inte stämmer.
- `bok graph tidslinje` och modulen `tidslinje`.
- Respons utifrån: lektörsbrev och betaläsare blir beslut och rader i `bok/revisioner.md`; `bok status` visar öppna revisioner.
- Verkliga händelser i `canon.md`; sensitivitetsläsning av planen innan första kapitlet.
- Fackgranskning för kapitel med `fack` i scenkortet.
- En röst per POV-person (`bok/stil/rost-<id>.md`).

## [2.1.1] — 2026-10-03

### Lagt till
- Välkomst första gången: i en helt ny bok berättar Claude kort hur det går till och vad man kan börja med.
- `README.md` i bokens rot (skapas av `bok init` om den saknas): kom igång, mapparna, uppdatering och förslag, skrivet för författaren.

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

[Unreleased]: https://github.com/fabian-von-tiedemann/programmatic-writing-stack/compare/v2.5.0...HEAD
[2.5.0]: https://github.com/fabian-von-tiedemann/programmatic-writing-stack/compare/v2.4.0...v2.5.0
[2.4.0]: https://github.com/fabian-von-tiedemann/programmatic-writing-stack/compare/v2.3.1...v2.4.0
[2.3.1]: https://github.com/fabian-von-tiedemann/programmatic-writing-stack/compare/v2.3.0...v2.3.1
[2.3.0]: https://github.com/fabian-von-tiedemann/programmatic-writing-stack/compare/v2.2.1...v2.3.0
[2.2.1]: https://github.com/fabian-von-tiedemann/programmatic-writing-stack/compare/v2.2.0...v2.2.1
[2.2.0]: https://github.com/fabian-von-tiedemann/programmatic-writing-stack/compare/v2.1.1...v2.2.0
[2.1.1]: https://github.com/fabian-von-tiedemann/programmatic-writing-stack/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/fabian-von-tiedemann/programmatic-writing-stack/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/fabian-von-tiedemann/programmatic-writing-stack/compare/37fbd05...v2.0.0
[1.2]: https://github.com/fabian-von-tiedemann/programmatic-writing-stack/tree/37fbd05
[1.1]: https://github.com/fabian-von-tiedemann/programmatic-writing-stack/tree/37fbd05
[1.0]: https://github.com/fabian-von-tiedemann/programmatic-writing-stack/tree/37fbd05
