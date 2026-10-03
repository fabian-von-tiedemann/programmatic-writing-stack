# Design: `bok`, en skrivharness som dras in i valfritt repo

**Datum:** 2026-10-03
**Status:** Utkast för granskning
**Ersätter:** v1.2 (`init-writing-stack.sh`, `upgrade-existing-project.sh`, `templates/`)

## 1. Mål

Ett harness som man lägger in i ett nytt, tomt repo och sedan arbetar med genom att chatta i Claude Code eller Conductor. AI skriver romanen. Författaren styr, väljer och godkänner.

Det ska gå att:

1. **Komma igång direkt.** `bok init` i ett tomt repo, öppna det i Conductor, börja prata.
2. **Chatta sig fram.** Ingen tvingande ordning. Man kan börja med en karaktär, en scen, en ton eller en lös idé. Harnesset sorterar in det som sägs på rätt plats och håller reda på vad som saknas.
3. **Utveckla ton och språk fritt i början.** Skicka in exempel ("så här vill jag att det låter"), låta Claude provskriva i olika röster, välja och justera tills rösten sitter.
4. **Skriva vilken roman som helst.** Inget genrearv. Spänningsverktyg (klocka, ledtrådar, motkraft) finns som tillval.
5. **Hålla reda på boken.** Karaktärer, relationer, hemligheter, platser, händelser och historiebågar, både som plan och som det som faktiskt står i texten.
6. **Skriva en hel bok.** Processen tar slut per kapitel och kontexten räcker till sista kapitlet.

Primär användare: en förstagångsförfattare som kan Claude Code och Conductor men inte är utvecklare. Hon har bara chattat lite om sin idé.

### Utanför ramen

- Flytt av befintliga v1.2-bokrepon.
- MCP-server. Claude anropar `bok` via Bash.
- Layered markup (`render-manuscript.py`, `tag-manuscript.py`, `@[display|node-id]`).
- PyPI-publicering. Installation sker från git.
- Audiobook och marknadsföring utöver att rollerna följer med som tillval.

## 2. Arkitektur

Samma mönster som Soup: ett uv-verktyg som skriver in sig i repot.

```sh
uv tool install git+https://github.com/fabian-von-tiedemann/programmatic-writing-stack
mkdir min-bok && cd min-bok && bok init
```

Det här repot blir Python-paketet `bok`. Python 3.11+, endast standardbiblioteket. pytest som utvecklingsberoende.

### 2.1 Tre sorters filer i bokrepot

| Sort | Var | Beteende |
|---|---|---|
| **Genererat** | `.claude/skills/bok/`, `.claude/agents/bok-*.md`, `.claude/bok/` | Skrivs av `bok init`. Bär versionshuvud. Skrivs om när paketet är nyare. En fil utan huvud är användarens och lämnas orörd (med varning). |
| **Bokens** | `bok/`, `manuskript/`, `inkorg/`, `bok.toml` | Skapas om de saknas. Rörs aldrig igen av `bok init`. |
| **Delad** | `CLAUDE.md` | Ett markerat block `<!-- bok:start -->…<!-- bok:end -->` skrivs om. Allt utanför blocket är användarens. |

Versionshuvud (efter eventuell frontmatter, som Soups skill):

```
<!-- bok-version: 2.0.0 | genererad av bok; redigera inte, skrivs om vid uppgradering. Egna tillägg: bok/roller/<roll>.local.md -->
```

### 2.2 Varför inte `.context/`

Conductor lägger `.context/` i `.git/info/exclude` i varje repo det hanterar. Bokens planering i `.context/` skulle alltså aldrig commitas och försvinna när en workspace arkiveras. All bokdata flyttas därför till den synliga mappen `bok/`, och ramverket till `.claude/bok/`.

### 2.3 Kommandon

| Kommando | Gör |
|---|---|
| `bok init [mapp] [--titel T] [--no-git]` | Gör mappen till ett bokrepo. Idempotent. Samma kommando uppgraderar. Kör `git init` och första commit om mappen inte är ett repo. |
| `bok status [--json]` | Läge, vad som saknas, nästa steg. |
| `bok mall <modul>` | Lägger till en tillvalsmodul i boken (se 3.3). |
| `bok graph <fråga>` | Frågor mot story-graph (se 5). |
| `bok tics [kapitel…] [--bok]` | Frekvenspass mot tics-katalogen. |
| `bok validate [kapitel…]` | Canon-blacklist och okända namn mot `characters.json`. |
| `bok rapport spara <fil\|->` | Validerar rapportens frontmatter och sparar den på rätt plats. |
| `bok annotations` | Läsarnoter från Apple Books (macOS). |

Alla kommandon hittar bokroten genom att gå uppåt till närmaste `bok.toml`.

## 3. Bokens filer

### 3.1 Princip: plan i markdown, fakta i grafen

- **Plan** (vad boken ska vara): markdown som författaren och Claude formar i samtal. `bok/koncept/`, `bok/karaktarer/`, `bok/plot/`, `bok/stil/`.
- **Fakta** (vad som faktiskt står i texten): JSON i `bok/story-graph/`, uppdaterad av Kontinuitet efter varje kapitel. Det är grafen som fångar glidning mellan plan och text.
- **En källa per uppgift.** Inget står på två ställen.

### 3.2 Trädet

```
bok.toml                  titel, genre, ramverksversion, aktiva moduler
CLAUDE.md                 tunn: bok-blocket + bokens egna regler
inkorg/                   råmaterial: chattar, anteckningar, gamla utkast
manuskript/
  kapitel-01.md …
bok/
  koncept/
    premiss.md            premiss, logline, central fråga
    genre.md              genre och genrekontrakt (vad läsaren utlovas)
    form.md               längd, kapitelstruktur, kapitelrubriker, tempus, berättarperson
    teman.md
  karaktarer/
    <id>.md               önskan, rädsla, blind fläck, språklig signatur, båge, relationer
  plot/
    struktur.md           akter, inciting incident, mittpunkt, klimax, upplösning
    bagar.md              historiebågar och karaktärsbågar: start, vändning, slut, kapitel
    kapitelplan.md        en rad per kapitel: POV, funktion, vilka bågar som rör sig
    kapitel/kapitel-NN.md scenkort för kapitlet (mål, konflikt, vändpunkt per scen)
  stil/
    rost.md               bokens röst: distans, rytm, bildspråk, dialog, förbjudet
    exempel/              texter författaren gillar, med en rad om varför
    prov/                 provskrivningar från stilverkstaden
  varld/
    varld.md              tid, plats, regler för världen
    research/<ämne>.md
  story-graph/
    characters.json  locations.json  events.json
    secrets.json  relationships.json  threads.json
  sammanfattningar/
    kapitel-NN.md         ca 200 ord per färdigt kapitel
  rapporter/
    kapitel-NN/<roll>-rN.md
    bok/<roll>-<datum>.md
  roller/                 valfria <roll>.local.md som läggs ovanpå standardrollen
  canon.md                fakta-fällor och verkliga personer som inte får förekomma
  learnings.md            aktiva regler (max ca 20) + arkiv
  tics-tillagg.md         bokens egna tics utöver ramverkets katalog
  beslut.md               viktiga vägval och varför
```

Jämfört med v1.2 försvinner: `meta/`, `forlag/`, `plot/serie/`, ett tjugotal plot-mallar, `stil/pov|rytm|dialog|motiv.md` (samlas i `rost.md`), `story-graph/*.md` (themes, threads, style-guide, knowledge-matrix, consistency-checks), `timeline.json`, `objects|organizations|documents.json` (tillval), åtta rapportmappar (blir en).

### 3.3 Tillvalsmoduler (`bok mall <modul>`)

Skillen föreslår modulen när genren eller samtalet motiverar den.

| Modul | Lägger till |
|---|---|
| `spanning` | `plot/klocka.md`, `plot/ledtradar.md` (plantering och avslöjande), `plot/motkraft.md` (antagonistens tidslinje) |
| `serie` | `plot/serie.md` (löfte, kanoniska händelser, hemligheter över böcker) |
| `forlag` | `forlag/` (manusformat, betaläsare, revisioner) |
| `graf-extra` | `objects.json`, `organizations.json`, `documents.json` |
| `audiobook`, `marknad` | respektive mapp och roll |

### 3.4 Mallarna

- Platshållare skrivs alltid `{{…}}`. Exempeltext innehåller aldrig `{{`.
- Mallarna är genreneutrala och korta: rubriker plus en fråga per rubrik, inga thrillerexempel.
- JSON-filerna seedas i loaderns format, t.ex. `{"characters": []}`.
- `README.md` och filer under `exempel/` och `prov/` räknas aldrig som ofyllda.

## 4. Arbetssätt: skillen

`.claude/skills/bok/SKILL.md` är tunn. Den kör alltid `bok status --json` först och svarar på svenska.

### 4.1 Fritt samtal är grundläget

Hon kan börja var som helst. Skillen:

1. **Lyssnar och sorterar.** Det hon säger om en person hamnar i `karaktarer/`, om en känsla i `teman.md`, om hur det ska låta i `stil/`. Skillen föreslår var det ska sparas ("Det låter som premissen, ska jag skriva in det?") och sparar efter ja.
2. **Föreslår, frågar inte tomt.** När något saknas föreslår Claude ett konkret svar hon kan godkänna, ändra eller kasta.
3. **Visar läget när hon vill.** "Var är vi?" ger `bok status` i klartext: vad som finns, vad som saknas för att börja skriva.
4. **Läser inkorgen.** Ligger det material i `inkorg/` erbjuder skillen att göra utkast till alla lager därifrån och fråga bara om luckorna.
5. **Committar** efter varje godkänd ändring, med ett meddelande på svenska.

Ordningen koncept → karaktärer → plot → stil är ett förslag, inte ett krav.

### 4.2 Stilverkstaden

Rösten är det som gör boken till hennes. Skillen har ett eget läge för den, som kan köras när som helst och hur många gånger som helst:

1. **Exempel in.** Hon klistrar in eller lägger texter i `bok/stil/exempel/` (egna eller andras) med en rad om vad hon gillar.
2. **Analys.** Claude beskriver vad som gör texterna till vad de är: meningslängd, distans till karaktären, bildspråk, tempo, dialogens form, vad som lämnas osagt.
3. **Provskrivning.** Claude skriver samma korta scen ur boken i 2–3 röster som drar åt olika håll och sparar dem i `bok/stil/prov/`.
4. **Val och justering.** Hon väljer, blandar, säger vad som skaver. Claude skriver om.
5. **Röstbeskrivning.** Det som valts skrivs in i `bok/stil/rost.md`. Writer och Språkgranskare utgår från den filen, aldrig direkt från exemplen.

Andras texter används för att förstå kvaliteter. Writer återger aldrig formuleringar ur dem. Utdrag hålls korta.

### 4.3 Grind innan första kapitlet

Det enda som blockerar är skrivandet av kapitel 1. Innan dess krävs:

- **I.1 Karaktärer:** varje POV-karaktär har önskan, rädsla, blind fläck och språklig signatur.
- **I.2 Plot:** central fråga, inciting incident, mittpunkt, klimax och varje akts funktion.
- **Röst:** `rost.md` ifylld och godkänd.
- **Kapitelplan** för åtminstone första akten.
- **Hennes ja** på en sammanfattning av boken på en skärm.

`bok status` visar vilka delar som saknas. Plot-arkitekten bedömer om innehållet håller.

### 4.4 Skrivloopen per kapitel

```
1. Plot-arkitekt: scenkort        → hon godkänner planen
2. Writer: utkast
3. bok validate + bok tics
4. Redaktör + Språkgranskare      (parallellt, returnerar rapporter)
5. Writer: revision efter fynd    (max 2 rundor)
6. Kontinuitet: graf, bågar, sammanfattning
7. Hon läser                      → godkänner eller skickar tillbaka med kommentarer
```

- **Godkänt** är minst 8 på varje axel. Når kapitlet inte dit efter två revisionsrundor visar skillen fynden och hon bestämmer.
- **Vid aktgränser** läser Förläggaren hela akten (via sammanfattningar och nyckelkapitel) och säger *fortsätt* eller *åtgärda*. Hon godkänner.
- **Efter sista kapitlet:** Förläggarens slutbetyg A/B/C och sensitivitetsläsning. Därefter tillvalen.
- Skillen läser aldrig prosan själv i onödan. Writer returnerar en sammanfattning på högst tio rader och en lista över nya personer, platser och händelser.

### 4.5 Lärdomar

Mönster som återkommer i rapporterna föreslås som regler i `learnings.md` ("Aktiva regler", max ca 20). Hon godkänner. Äldre regler flyttas till arkivet. Rollspecifika regler hamnar i `bok/roller/<roll>.local.md`, aldrig i de genererade filerna.

## 5. Story-graph och historiebågar

Grafen är harnessets minne. Den uppdateras av Kontinuitet efter varje godkänt utkast.

| Fil | Innehåll |
|---|---|
| `characters.json` | etablerade fakta: namn, ålder, utseende, yrke, var de bor, första förekomst |
| `relationships.json` | vem till vem, typ, hur det förändras och i vilket kapitel |
| `locations.json` | platser med fakta som etablerats |
| `events.json` | händelser: kapitel, tid i berättelsen, plats, närvarande |
| `secrets.json` | hemlighet, sann version, `known_to` med från vilket kapitel |
| `threads.json` | bågar som faktiskt rör sig: id, typ (intrig/karaktär/tema), status (öppen/stängd), händelser per kapitel, planteringar och om de har lösts |

`bok graph` ger frågorna rollerna behöver:

| Fråga | Svar |
|---|---|
| `context --kapitel N` | allt kapitel N behöver: karaktärer i kapitlet, deras relationer och vad POV vet, öppna bågar som berörs, platser |
| `vem-vet <hemlighet> [--kapitel N]` | vilka som känner till något vid en tidpunkt |
| `bagar [--oppna]` | bågarna med status och senaste kapitel; öppna planteringar utan upplösning |
| `karaktar <id>` | fakta, relationer och kapitel där personen förekommer |
| `var <plats> [--kapitel N]` | händelser på en plats |

Grafen laddas direkt från JSON. Ingen pickle-cache.

`bok status` jämför `plot/bagar.md` (plan) med `threads.json` (utfall) och flaggar bågar som inte rört sig på länge eller som planerats men aldrig påbörjats.

## 6. Roller

Rollerna genereras som Claude Code-subagenter i `.claude/agents/bok-<roll>.md`. Varje agent läser `bok/roller/<roll>.local.md` om den finns.

### 6.1 Kärnan

| Roll | Gör | Verktyg |
|---|---|---|
| **Plot-arkitekt** | struktur, bågar, kapitelplan, scenkort; bedömer grind I.1, I.2 och scenkort | läs, skriv i `bok/plot/` och `bok/karaktarer/` |
| **Writer** | utkast och revision efter en fynd-lista | läs, skriv i `manuskript/` |
| **Redaktör** | struktur, karaktär, spänning, kontinuitet, tema; med ett eget adversarialt avsnitt ("vad har jag missat, vilket betyg är för snällt") | läs, `bok` |
| **Språkgranskare** | prosa, dialog, röst mot `rost.md`; läser som en naiv läsare | läs, `bok` |
| **Kontinuitet** | uppdaterar grafen och `threads.json`, skriver sammanfattningen, flaggar canon-brott | läs, skriv i `bok/story-graph/` och `bok/sammanfattningar/` |
| **Förläggare** | akten och hela boken: håller löftet i genrekontraktet, tempo över tid | läs, `bok` |

Granskarna (Redaktör, Språkgranskare, Förläggare) har inget skrivverktyg. De returnerar sin rapport och skillen sparar den med `bok rapport spara`.

### 6.2 Vid behov och senare

Researcher (webbsök), Världsbyggare (värld och serie), Sensitivitetsläsare (en gång, sent), Audiobook-regissör och Marknadsförare (moduler).

### 6.3 Vad rollerna läser

Ingen roll läser hela manuset. Writer läser: scenkortet, `rost.md`, karaktärsfilerna för kapitlets personer, `bok graph context --kapitel N`, föregående kapitel i sin helhet, alla tidigare sammanfattningar, aktiva regler i `learnings.md` och `canon.md`.

### 6.4 Betyg och rapporter

En skala, definierad en gång i `.claude/bok/process.md`: 7 är kompetent och publicerbart, 8 är bra, 9 är ovanligt bra och kräver motivering. Axlarna är fasta:

- Redaktör: `struktur`, `karaktar`, `spanning`, `kontinuitet`, `tema`
- Språkgranskare: `prosa`, `dialog`, `rost`

Frontmatter i varje rapport, validerad av `bok rapport spara`:

```yaml
kapitel: 3
roll: redaktor
runda: 1
datum: 2026-10-03
betyg: {struktur: 8, karaktar: 7, spanning: 8, kontinuitet: 9, tema: 8}
utfall: godkand | revidera | eskalera
blockerande: ["Kap 3 säger tisdag, kap 2 slutade på torsdag"]
```

## 7. `bok status`

Läser filerna, sparar inget eget tillstånd.

- **Förberedelse:** koncept, karaktärer, plot, röst och kapitelplan, med ✓ eller vad som saknas. Ofylld betyder att `{{` finns kvar, eller tom JSON-lista.
- **Per kapitel:** scenkort, utkast, granskat (senaste betyg per axel), revisionsrunda, godkänt.
- **Bågar:** öppna, stillastående, olösta planteringar.
- **Nästa steg:** en rad, t.ex. *"Kapitel 4: Språkgranskaren vill ha revision (dialog 6)."*
- `--json` ger samma sak till skillen.

## 8. Ramverkets innehåll (`.claude/bok/`)

- `process.md`: loopen i 4.4, grindarna, betygsskalan, vem som läser vad.
- `hantverk/`: tekniker, anti-mönster och en kapitelchecklista. Genreneutralt. Spänningstekniker flyttas till modulen `spanning`.
- `tics-katalog.md`: generella tics, genreneutrala. Bokens egna i `bok/tics-tillagg.md`.
- `verktyg.md`: kommandona i 2.3 med exempel.

## 9. Inget arv från tidigare böcker

Allt innehåll skrivs om eller rensas så att inget pekar på *Marken under marken* eller någon annan bok: inga orter, personer, organisationer, titlar eller författarpreferenser. Det gäller rollbriefer, hantverk, tics-katalog, mallar, exempelkapitel, scripts (t.ex. hårdkodade politiker och PR-byråer i `grep-tics.sh`, `TITLE` i `books-annotations.sh`) och dokumentation.

Ett test söker igenom allt paketinnehåll efter en lista med kända arvstermer och efter thriller-standarder i neutrala filer, och fallerar vid träff.

`docs/PRD.md`, `docs/stack.html` och `templates/docs/` flyttas till `docs/arkiv/v1.2/`. README skrivs om för v2.

## 10. Felhantering

- `bok init` i en mapp med en fil utan versionshuvud där ramverket vill skriva: lämnar filen och skriver en varning.
- `bok init` med ogiltig `bok.toml`: avbryter innan något skrivs.
- Kommandon utanför en bok: tydligt fel som föreslår `bok init`.
- `bok rapport spara` med fel frontmatter: avvisar med exakt vad som är fel, så att skillen kan rätta och försöka igen.
- `bok annotations` på annat än macOS: tydligt fel.
- Trasig JSON i grafen: felet pekar på fil och rad.

## 11. Tester

pytest, CI på ubuntu och macOS med Python 3.11. Ersätter `test-init.yml`.

- `init`: tom mapp, mapp utan git, repo med befintlig `CLAUDE.md`, två körningar i rad utan ändring, uppgradering av äldre genererad fil, fil utan huvud lämnas, bokens filer skrivs aldrig över.
- `status`: testböcker i varje läge: tom, halv förberedelse, redo för kapitel 1, kapitel i revision, akt klar.
- `graph`: varje fråga mot en liten testbok, inklusive bågar och `context`.
- `tics`, `validate`, `rapport spara`: träffar, missar, felaktig frontmatter.
- Agentfilerna: giltig frontmatter, versionshuvud efter frontmatter.
- Arvstestet i 9.
- Manuellt: ett nytt repo, riktigt chattmaterial i `inkorg/`, stilverkstad med egna exempel, hela vägen till ett godkänt kapitel 1.

## 12. Ordning för implementationen

1. Paketskelett, `bok.toml`, rothittning, versionshuvud, `bok init`.
2. Bokens träd och mallar, rensade och genreneutrala. Modulerna.
3. Grafen och `bok graph`, `tics`, `validate`, `rapport spara`, `annotations`.
4. `bok status`.
5. Ramverket: `process.md`, hantverk, tics-katalog, de sex kärnrollerna plus tillvalsrollerna som agenter.
6. Skillen: fritt samtal, inkorg, stilverkstad, grind, skrivloop.
7. README, arkivering av v1.2, CI, borttagning av gamla scripts.
8. Manuell genomkörning från tomt repo till kapitel 1.
