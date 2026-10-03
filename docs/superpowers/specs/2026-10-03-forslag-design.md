# Design: förslag från användarna (feedbackloop för `bok`)

**Datum:** 2026-10-03
**Status:** Utkast för granskning
**Bygger på:** `docs/superpowers/specs/2026-10-03-bok-cli-design.md`

## 1. Mål

En feedbackloop från riktiga användare: den som skriver med `bok` ska enkelt kunna skicka förslag på hur harnesset kan bli bättre, förslagen ska nå utvecklaren, förbättringarna ska komma ut i nya versioner, och användaren ska se vad som hände med hennes förslag.

Lyckat är när:

- ett förslag går från användaren till utvecklarens inkorg på under en minut, utan konto,
- ingen text ur någon bok, inga namn och inga filinnehåll lämnar användarens dator,
- utvecklaren kan låta Claude gruppera förslagen och göra en PR,
- användaren ser "infört i 2.1.0" efter `uv tool upgrade bok` och `bok init`.

### Utanför ramen

- Dialog i båda riktningar (följdfrågor som användaren svarar på). En `Svar:`-kommentar till användaren räcker i den här versionen.
- Webbgränssnitt för förslag.
- Analys av användning (telemetri). Inget skickas utan att användaren sagt ja till just det förslaget.

## 2. Arkitektur

```
användare                         mottagare (Cloudflare Worker)          utvecklare
──────────                        ─────────────────────────────          ──────────
skillen bok fångar förslaget  →   POST /v1/forslag                  →   issue i privata
bok forslag skicka -              validera, takbegränsa, D1             repot bok-forslag
                                                                         │
bok forslag (status)          ←   GET /v1/forslag                   ←   etiketter + Svar:
bok init (efter uppgradering)                                            │
                                                                     skillen forslag i
                                                                     harness-repot → PR → release
```

Tre delar, var för sig testbara:

1. **Klient** i paketet `bok`: `src/bok/forslag.py` och skillens text.
2. **Mottagare**: Cloudflare Worker i TypeScript i `mottagare/`, med D1.
3. **Underhållsskill**: `.claude/skills/forslag/SKILL.md` i harness-repot.

## 3. Klienten (användarens sida)

### 3.1 Fånga i samtalet

Skillen `bok` lyssnar efter kommentarer om verktyget, inte om boken: "det här var krångligt", "varför frågar den hela tiden", "jag önskar att…", eller att hon kör fast eller rättar Claude om samma sak upprepade gånger. Då erbjuder den en gång, utan att tjata: "Vill du skicka det som förslag till dem som bygger verktyget?" Hon kan också själv säga "skicka ett förslag".

När en regel i bokens `bok/learnings.md` gäller skrivande i allmänhet och inte bara den här boken, erbjuder skillen att skicka den som förslag av typen `lardom`.

### 3.2 Visa innan något skickas

Skillen skriver ett utkast och visar exakt vad som går iväg:

| Fält | Innehåll |
|---|---|
| `typ` | `forbattring`, `problem`, `fraga` eller `lardom` |
| `text` | hennes ord, ordagrant (max 4000 tecken) |
| `sammanhang` | Claudes beskrivning av situationen, t.ex. "i stilverkstaden, steg 3, efter tredje provskrivningen" (max 2000 tecken). Ingen boktext, inga namn, inga filinnehåll. |
| `version` | `bok`-versionen (läggs till automatiskt) |
| `lage` | raden från `bok status`, t.ex. "kapitel 3: granskning runda 2" (automatiskt) |
| `roll` | vilken roll det gällde, om någon (automatiskt eller från skillen) |

Inget skickas utan hennes ja.

### 3.3 Kommandon

| Kommando | Gör |
|---|---|
| `bok forslag skicka -` | läser utkastet (frontmatter `typ`, `roll`, `sammanhang`; brödtext = hennes ord) från stdin, lägger till version och läge, sparar lokalt, skickar |
| `bok forslag` | listar hennes förslag med status: mottaget, planerat, infört i X, avböjt, och eventuellt svar |
| `bok forslag skicka --igen` | skickar de sparade förslag som inte kom fram |
| `bok forslag av` / `bok forslag pa` | stänger av eller på erbjudanden och all nätkontakt |

`bok forslag skicka` kräver ingen bok (fungerar även utanför ett bokrepo; då utan `lage`).

### 3.4 Lokal lagring och identitet

Allt ligger per användare, inte per bok, i `~/.config/bok/` (eller `$XDG_CONFIG_HOME/bok/`):

- `nyckel` – en slumpad nyckel (32 byte, urlsafe base64) som skapas första gången. Den är användarens anonyma identitet mot mottagaren.
- `forslag.jsonl` – en rad per förslag: lokalt id, tid, fälten, `skickat` (bool), mottagarens id och issuenummer.
- `installningar.json` – `{"forslag": "pa" | "av", "senast_sedda": {...}}` för stängd loop.

Filerna skapas med rättigheter `0600`.

### 3.5 Stängd loop

Efter en uppgradering (när `bok init` skriver om genererade filer) hämtar `bok init` status för användarens förslag med 3 sekunders timeout och skriver t.ex. "2 av dina förslag finns med i den här versionen." om något har ändrats till infört sedan förra gången. Misslyckas anropet sägs inget.

### 3.6 Nät

Endast standardbiblioteket (`urllib.request`, `json`). Adressen är en konstant i paketet och kan ändras med `BOK_FORSLAG_URL`. Fel blir en svensk rad (`BokFel`); förslaget ligger då kvar som oskickat.

## 4. Mottagaren

Cloudflare Worker i TypeScript i `mottagare/`, D1-databas, deployas med `wrangler`.

### 4.1 Konto

**Mottagaren ligger på utvecklarens privata Cloudflare-konto**, inte Digitalists. `account_id` skrivs fast i `mottagare/wrangler.jsonc`. Före varje deploy, skapande av D1 eller hemligheter körs `wrangler whoami`, och kontot bekräftas.

### 4.2 Anrop

Båda kräver `Authorization: Bearer <nyckel>` (minst 32 tecken).

**`POST /v1/forslag`** med JSON `{typ, text, sammanhang, version, lage, roll}`:

1. Validera: kända fält, `typ` i den tillåtna mängden, längdgränser, högst 16 kB, `version` som `\d+\.\d+\.\d+`.
2. Takbegränsa med Cloudflares rate limiting: 5 förslag per timme per nyckel, 30 per dygn per IP (räknas i D1 på en HMAC av datum och IP med hemligheten `IP_SALT`; IP:n sparas aldrig). Svar 429 med svensk text.
3. Är nyckeln spärrad (D1) → 403.
4. Skapa issue i `bok-forslag`: rubrik = första raden av `text` (max 70 tecken), brödtext med fälten under rubriker, etiketterna `forslag`, `typ:<typ>` (versionen står i brödtexten; en etikett per version skulle låta klienten skapa hur många etiketter som helst).
5. Spara i D1: `forslag(id, nyckel_hash, issue, skapad)`. `nyckel_hash` = SHA-256 av nyckeln. Ingen IP sparas. Nyckeln och hashen syns aldrig i issuet.
6. Svara `201 {id, issue}`.

**`GET /v1/forslag`**: hämta användarens issues (via D1 → ett enda GraphQL-anrop till GitHub; takbegränsat per nyckel och per IP) och svara med en lista `{id, issue, rubrik, skapad, status, version, svar}`:

| I GitHub | `status` |
|---|---|
| öppet issue utan statusetikett | `mottaget` |
| `status:planerad` | `planerat` |
| etikett `infort:<version>` | `infort` (med `version`) |
| stängt med `status:avbojd` | `avbojt` |
| issuet går inte att läsa (till exempel borttaget) | `okand` (klienten visar "skickat") |

`svar` = den senaste kommentaren som börjar med `Svar:` (utan prefixet).

### 4.3 Hemligheter och data

- `GITHUB_TOKEN`: finkornig token som bara får läsa och skriva issues i `bok-forslag`. Sätts med `wrangler secret put`.
- `IP_SALT`: slumpad hemlighet för taket per IP och dag. Sätts med `wrangler secret put`.
- D1-tabeller: `forslag(id TEXT PK, nyckel_hash TEXT, issue INTEGER, skapad TEXT)`, `sparr(nyckel_hash TEXT PK, skal TEXT)`, `ip_dag(ip_hash TEXT PK, dag TEXT, antal INTEGER)`.
- Loggar innehåller inga förslagstexter. Vid fel loggas bara felets namn och GitHubs statuskod.

### 4.4 Engångssteg för utvecklaren

Planen skriver ut stegen; inget av dem görs utan utvecklarens ja:

1. Skapa privata repot `fabian-von-tiedemann/bok-forslag` med etiketterna ovan.
2. Skapa token med rätt behörighet.
3. `wrangler whoami` → bekräfta privat konto → `wrangler d1 create`, migrera, `wrangler secret put GITHUB_TOKEN`, `wrangler secret put IP_SALT`, `wrangler deploy`.
4. Lägg in den riktiga adressen som konstant i `bok` och höj versionen.

## 5. Från förslag till förbättring

Underhållsskill i harness-repot: `.claude/skills/forslag/SKILL.md` (committas; för utvecklaren).

"Gå igenom förslagen":

1. Hämta öppna issues i `bok-forslag` med `gh issue list`.
2. Gruppera efter tema och efter del av harnesset (skillen, en roll, `bok status`, mallar, stilverkstad, hantverk) och räkna hur många användare som tagit upp samma sak.
3. Föreslå per grupp: göra nu, senare eller avböja, med motivering. Utvecklaren bestämmer.
4. Göra nu → etiketten `status:planerad`, ändring med tester på en gren, PR som refererar `bok-forslag#N`, versionshöjning (annars får användarna inte ändringen via `bok init`). Avböja → `status:avbojd`, stäng, skriv ett vänligt `Svar:`. Senare → lämna.
5. Vid release: förslagen i versionen får `infort:<version>` och stängs; CHANGELOG får avsnittet "Från användarna".

`lardom`-förslag prövas mot `.claude/bok/hantverk/` och kan föras in där.

**Integritet:** harness-repot är publikt. Användarnas ord citeras aldrig i PR:er, commits eller CHANGELOG; sammanfatta med egna ord och referera med nummer.

## 6. Felhantering

| Situation | Beteende |
|---|---|
| Inget nät, timeout, 5xx | förslaget sparas som oskickat; svensk rad; `bok forslag skicka --igen` |
| 429 | svensk rad om att vänta; sparas som oskickat |
| 400 | visar mottagarens felmeddelande; förslaget sparas inte som skickat |
| 403 (spärrad) | svensk rad; sparas lokalt |
| `bok forslag av` | inga erbjudanden, inga anrop, `bok forslag skicka` säger att det är avstängt |
| Trasig lokal fil | svensk rad som pekar på filen; inget skrivs över |

## 7. Tester

- **Klient (pytest):** utkast från stdin (frontmatter + brödtext), validering av typ och längd, lokal lagring och rättigheter, nyckel skapas en gång, avstängning, `--igen`, statuslistning och stängd loop i `bok init` mot en lokal testserver (`http.server` i en tråd), timeout utan utskrift.
- **Mottagare (vitest med Cloudflares testmiljö för Workers):** validering, takbegränsning, spärr, issue-skapande och statusmappning med mockade GitHub-anrop, att nyckel och IP aldrig hamnar i issue eller D1 i klartext.
- **Skill:** innehållstest att skillen `bok` har avsnittet om förslag och kommandona, och att underhållsskillen nämner integritetsregeln.

## 8. Ordning för implementationen

1. Klient: lagring, nyckel, `bok forslag skicka -`, `bok forslag`, `--igen`, `av`/`pa`, mot testserver.
2. Skillen `bok`: fånga, visa, skicka; lärdomar som förslag; stängd loop i `bok init`.
3. Mottagaren: Worker, D1-schema, validering, takbegränsning, GitHub-anrop, tester.
4. Underhållsskillen `forslag`.
5. Engångssteg (med utvecklarens ja), riktig adress i `bok`, versionshöjning, README.
