# Design: `bok` 2.3 – platser och miljöer från kartan

**Datum:** 2026-10-04
**Status:** Utkast för granskning
**Bygger på:** `docs/superpowers/specs/2026-10-03-bok-2-2-design.md`
**Underlag:** `docs/superpowers/research/2026-10-04-google-maps-platform.md` (villkor, API:er, priser)

## 1. Mål

Göra det lätt att förankra bokens miljöer i verkliga platser: hur lång tid det tar att gå, cykla, åka bil eller åka kollektivt mellan platser, och hur det ser ut på en plats eller längs en rutt. Claude tittar på gatubilder och skriver *egna* miljöbeskrivningar i bokens filer. Eftersom böckerna ofta spänner över decennier ska det alltid synas när underlaget är fotograferat och att det visar dagens värld. När glappet mot bokens tid är stort ska det gå att söka sig bakåt i arkiv.

Lyckat är när:

- "hur lång är cykelturen från lägenheten till fabriken?" får ett svar med dagens restid, tydligt märkt,
- Claude kan ta fram en miljöbeskrivning av en plats eller en rutt innan Writer skriver kapitlet,
- `bok graph context` visar både *Bokens tid* och *Idag* för kapitlets platser, och hur många år som skiljer,
- en plats som ska skildras 1978 kan få en *Bokens tid* som bygger på arkivbilder och källor,
- en författare utan teknikvana kan skaffa och lägga in en nyckel själv med guiden,
- nyckeln syns aldrig i repot, i boken, i chatten eller i felmeddelanden,
- inga bilder från Google eller arkiven sparas i boken.

Inga nya fält blir obligatoriska; befintliga böcker fungerar som förut efter `bok init`. Utan nyckel fungerar allt som förut.

### Utanför ramen

- **Places** (vad som finns längs vägen). EES-villkoren (EEA-SST §15.2) begränsar Places-data till nio uppräknade ändamål som romanresearch inte passar in i. Kan tas upp senare.
- Historiska restider. Routes kan inte räkna bakåt (kollektivt högst 7 dagar).
- Äldre Street View-bilder. API:et har inget sätt att välja datum.
- Kartbilder (Static Maps).

### Villkoren

Undersökningen i underlaget visar:

- **Restider:** att visa dem på begäran är tillåtet. Att spara dem är det inte: "No Caching", och för Routes får bara lat/lng sparas, i högst 30 dagar. `bok` sparar aldrig ett resultat från Google i en fil. Boken innehåller frågan och en egen, avrundad formulering.
- **Bilder:** sparas aldrig i boken, bara i en tillfällig mapp utanför boken som rensas.
- **Beskrivningar av bilder:** villkoren förbjuder att "create content based on Google Maps Content". Utvecklaren tolkar det som att det gäller själva materialet (spåra, digitalisera, återskapa), inte att beskriva vad man ser med egna ord. Tolkningen är osäker: villkorens eget exempel ("construct an index of tree locations within a city from Street View imagery") bygger på att tolka bilder. Därför är Street View ett eget, medvetet steg för varje användare (§6), och guiden säger det rakt ut.
- **Attribution:** "Google Maps" visas med varje restid, och för gång och cykel visas Googles obligatoriska beta-varning.

## 2. Kommandon

Ny modul `src/bok/karta.py`. Den registrerar `bok karta` och `bok bild`. Bara standardbiblioteket.

| Kommando | Gör | Sparar |
|---|---|---|
| `bok karta nyckel` | frågar efter API-nyckeln med `getpass` (syns inte). `--signering` frågar efter Street Views URL-signeringshemlighet. `--ta-bort` raderar båda | `~/.config/bok/google-maps-nyckel`, `~/.config/bok/google-maps-signering` (0600, katalogen 0700) |
| `bok karta status` | om nyckeln finns och var den kommer ifrån (fil eller miljövariabel, aldrig värdet), och om den fungerar: ett gratis metadataanrop mot Street View | inget |
| `bok karta restid <från> <till> [--satt gang,cykel,bil,kollektivt] [--avgang HH:MM] [--ankomst HH:MM] [--dag ÅÅÅÅ-MM-DD]` | restid och avstånd per färdsätt, och linjer, byten och gångsträckor för kollektivt | inget |
| `bok karta gatuvy <plats> [<till>] [--satt gang] [--antal 8] [--mellanrum 150]` | gatubilder på en plats eller längs en rutt, till en tillfällig mapp | bara den tillfälliga mappen |
| `bok karta stada` | raderar alla tillfälliga mappar från `gatuvy` och `bok bild` | — |
| `bok bild <url>` | laddar ner en bild (t.ex. ur ett arkiv) till den tillfälliga mappen så att Claude kan titta på den | bara den tillfälliga mappen |

### 2.1 Platser som argument

`<plats>`, `<från>` och `<till>` är:

1. ett id i `bok/story-graph/locations.json` som har `adress` eller `lat` och `lng` (värden som författaren själv angett, inte Googles), eller
2. en fri adress ("Hornsgatan 12, Stockholm") eller `lat,lng`.

Ett id utan `adress` och koordinater ger felet "Platsen <id> har ingen adress. Lägg till adress i locations.json." Nya valfria fält i `locations.json`:

```json
{"locations": [{"id": "fabriken", "namn": "Fabriken", "adress": "Lumaparksvägen 7, Stockholm"}]}
```

eller `"lat": 59.30, "lng": 18.10`.

### 2.2 `bok karta restid`

`POST https://routes.googleapis.com/directions/v2:computeRoutes`. Nyckeln skickas i headern `X-Goog-Api-Key`, och `languageCode` är `sv`.

| `--satt` | travelMode | Field mask |
|---|---|---|
| `gang` | `WALK` | `routes.duration,routes.distanceMeters` |
| `cykel` | `BICYCLE` | samma |
| `bil` | `DRIVE`, `TRAFFIC_UNAWARE` (Essentials-pris) | samma |
| `kollektivt` | `TRANSIT` | samma plus `routes.legs.steps.transitDetails,routes.legs.steps.travelMode,routes.legs.steps.staticDuration` |

- Standard är alla fyra, ett anrop per färdsätt.
- `--avgang` och `--ankomst` gäller bara kollektivt och avser `--dag`, som är i dag om inget anges. Tiden tolkas i datorns lokala tidszon och skickas i RFC 3339. Routes tillåter högst 7 dagar bakåt och 100 dagar framåt. Ligger `--dag` utanför det stoppar `bok` med ett tydligt fel. Anges båda tiderna är det ett fel.
- Utskrift:

```
Lägenheten → Fabriken
  till fots     38 min   2,9 km
  cykel         14 min   3,1 km
  bil           11 min   3,6 km  (utan trafik)
  kollektivt    24 min   avgång 08:15: buss 4 mot Radiohuset (6 hållplatser), byte, tunnelbana 19 …

Google Maps · beräknad 2026-10-04 · dagens vägnät och tidtabell, inte bokens tid.
Gång- och cykelvägar är i beta och kan sakna tydliga trottoarer, gångvägar eller cykelvägar.
```

- Beta-varningen skrivs ut på engelska och svenska ordagrant när gång eller cykel ingår.
- Saknas en rutt för ett färdsätt ("ingen rutt hittades") skrivs det på färdsättets rad, och resten fortsätter.

### 2.3 `bok karta gatuvy`

**En plats:** metadata för platsen, sedan fyra bilder (riktning 0, 90, 180 och 270).

**En rutt** (`<plats> <till>`):
1. Hämta rutten (`--satt`, standard `gang`) med field mask `routes.polyline.encodedPolyline`.
2. Avkoda polylinen i minnet. Den sparas aldrig.
3. Välj punkter var `--mellanrum` meter (standard 150), högst `--antal` (standard 8, tak 20). Start och mål är alltid med. Om rutten räcker till fler punkter än `--antal` sprids de jämnt.
4. Blickriktning per punkt = bäring mot nästa punkt på polylinen (framåt längs rutten). Vid målet används bäringen från föregående punkt.

**Per punkt:**
1. Metadata: `GET https://maps.googleapis.com/maps/api/streetview/metadata?location=lat,lng&source=outdoor&radius=50&key=…`. Det är gratis och kostar ingen kvot.
2. `ZERO_RESULTS` eller `NOT_FOUND`: punkten hoppas över och nämns i utskriften.
3. Samma `pano_id` som föregående punkt: hoppas över.
4. Bild: `GET https://maps.googleapis.com/maps/api/streetview?size=640x640&pano=<pano_id>&heading=<h>&pitch=0&fov=90&return_error_code=true&key=…`, och `&signature=…` om en signeringshemlighet finns (HMAC-SHA1 enligt Googles beskrivning, med `hmac`, `hashlib` och `base64`).
5. Sparas som `NN.jpg` i den tillfälliga mappen.

**Tillfällig mapp:**
- `tempfile.mkdtemp(prefix="bok-gatuvy-")` under systemets temp-katalog, aldrig i boken.
- Rättigheter 0700.
- Vid varje körning raderas `bok-gatuvy-*`- och `bok-bild-*`-mappar äldre än ett dygn.

**Utskrift:**

```
Gatubilder (Google Street View) i /var/folders/…/bok-gatuvy-a1b2c3/
  01.jpg  fotograferat 2023-08  mot nordost  start
  02.jpg  fotograferat 2019-06  mot öst      150 m
  –       ingen gatubild         (300 m)
  …
Fotograferat: 2019-06 – 2023-08. Hämtat 2026-10-04. Dagens värld, inte bokens tid.
Öppna i webbläsaren: https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=59.3%2C18.1&heading=45
Rensa när beskrivningen är skriven: bok karta stada
```

- Datum kan vara `ÅÅÅÅ-MM`, `ÅÅÅÅ` eller saknas ("fotodatum okänt").
- Webbläsarlänken är Googles nyckelfria Maps URL och behöver ingen nyckel.

### 2.4 `bok bild <url>`

- Bara `https`, eller `http` om det är uttryckligen angivet.
- Högst fem omdirigeringar, och bara till http(s).
- `Content-Type` måste börja med `image/` (jpeg, png, gif, webp, tiff). Annars ett fel.
- Storlekstak 15 MB, avbryts vid överskridande.
- Sparas i `tempfile.mkdtemp(prefix="bok-bild-")` och sökvägen skrivs ut.
- Ingen nyckel skickas. `User-Agent: bok/<version>`.

## 3. Nyckeln

**Var nyckeln läses ifrån:**
1. miljövariabeln `BOK_GOOGLE_MAPS_NYCKEL`,
2. annars `~/.config/bok/google-maps-nyckel`.

Signeringshemligheten läses på samma sätt: `BOK_GOOGLE_MAPS_SIGNERING`, annars `google-maps-signering`. Katalogen följer `XDG_CONFIG_HOME`, som `forslag.katalog()`.

**Skrivning:**
- Atomiskt och privat, på samma sätt som `forslag._skriv_privat`.
- `_skapa_katalog` och `_skriv_privat` flyttas till en gemensam modul, `src/bok/privat.py`, som både `forslag` och `karta` använder.

**Inmatning:**
- `bok karta nyckel` kräver en terminal (`sys.stdin.isatty()`). Annars avbryter kommandot med: "Kör bok karta nyckel i din egen terminal, inte via Claude. Se docs/google-maps.md."
- Det hindrar att nyckeln klistras in i chatten och skickas via stdin.

**Nyckeln får aldrig synas.** URL:er med `key=` skapas bara inuti `karta.py` och lämnar aldrig modulen. Konkret:
- Alla anrop går genom en funktion `_hamta(url_eller_request)`. Den fångar `urllib.error.HTTPError`, `URLError`, `TimeoutError`, `OSError` och `http.client.HTTPException` och kastar `KartaFel` (en `BokFel`) med en text utan URL, `from None`, så att ingen kedjad undantagstext bär URL:en.
  - Varför det behövs: `cli.main` skriver i dag ut `exc.filename` för `OSError`, och för en `HTTPError` är `filename` hela URL:en.
- Omdirigeringar följs aldrig mot Googles API:er (som `forslag._IngenOmdirigering`).
- `bok karta status` visar bara "nyckel: finns (fil)" eller "nyckel: finns (miljövariabel)".
- Felsvar från Google (`error_message`, `error.message`) visas inte råa. De mappas till egna meddelanden (§5), eftersom de i sällsynta fall kan citera begäran.

**Skillen:** Claude läser aldrig `~/.config/bok/google-maps-*`, kör aldrig `bok karta nyckel` och ber aldrig om nyckeln i chatten. Klistrar hon ändå in en nyckel ska Claude säga att den bör bytas ut (skapa en ny i Google Cloud och ta bort den gamla), och peka på guiden.

## 4. I boken

### 4.1 Platsfiler

Ny mapp i startfilerna: `bok/varld/platser/README.md` (skapas av `bok init` om den saknas). Den beskriver formatet:

```
# Hornsgatan

## Bokens tid
<det som är belagt eller som hon har bestämt, med källor. Tomt tills dess.>

## Idag
Källa: Google Street View
Fotograferat: 2019-06 – 2023-08
Hämtat: 2026-10-04
<beskrivningen: gatans form och lutning, husen, material, grönska, ljus, ljud man anar, avstånd, vad som rör sig>

## Rutter
- Lägenheten → fabriken, cykel: en dryg kvart (dagens vägnät, 2026-10-04)
```

- Filen heter `bok/varld/platser/<id>.md` med samma id som i `locations.json`. För en rutt utan egen plats används `<från>-<till>.md`.
- Raden `Fotograferat:` är det som `bok graph context` läser: ett eller två partiella datum, med ett tankstreck eller bindestreck mellan.
- Under `## Rutter` står bara egna, avrundade formuleringar och datumet, aldrig Googles siffror.
- Inget i filen kommer ordagrant från Google, och inga bilder eller bildlänkar till Google sparas.

### 4.2 `bok graph context --kapitel N`

För varje plats i scenkortets `platser` som har en platsfil visas, efter platsens fakta:

1. `#### Bokens tid` med innehållet, om det inte är tomt,
2. `#### Idag` med innehållet,
3. en rad om glappet, när både kapitlets datum och `Fotograferat:` finns:
   `Underlaget Idag är fotograferat 2019–2023; kapitlet utspelar sig 1978 (41–45 år tidigare). Bokens tid går före; ur Idag används bara det som gällde då.`
   - Är glappet under 3 år skrivs: `Underlaget Idag är fotograferat 2023; kapitlet utspelar sig 2024.`
   - Saknas något av datumen skrivs ingen rad.

Platsfiler för platser som inte står i scenkortet tas inte med. Det håller underlaget kort.

### 4.3 Ramverket

| Fil | Ändring |
|---|---|
| skillen `bok` | nytt avsnitt **Platser och miljöer**: restid på begäran, miljö efter scenkortets ja, arkivspåret, nyckelreglerna (§3), första gången utan nyckel → guiden. Tabellen i Fritt samtal: "hur en plats ser ut, hur lång tid det tar" → `bok/varld/platser/<id>.md` via Världsbyggaren |
| `.claude/bok/verktyg.md` | `bok karta restid`, `gatuvy`, `stada`, `status`, `bok bild` |
| `.claude/bok/story-graph.md` | `adress`, `lat`, `lng` i `locations.json`; platsfilerna i `context` |
| `.claude/bok/process.md` | miljö efter scenkortet (erbjudande, inte grind); platsens historia |
| `bok-varldsbyggare` | `tools` får `Bash` (bara för `bok`-kommandon). Nytt uppdrag **miljö** (§4.4) |
| `bok-researcher` | `tools` får `Bash` (bara för `bok bild` och `bok karta stada`). Nytt uppdrag **platsens historia** (§4.5) |
| `bok-plot-arkitekt` | I scenkortet: när personer förflyttar sig mellan platser med adress körs `bok karta restid`, och en egen formulering skrivs under Plats och tid |
| `bok-writer` | regeln om *Bokens tid* och *Idag* (§4.6) |
| `bok-redaktor` | under kontinuitet: detaljer ur *Idag* som inte kan ha funnits vid kapitlets datum är fel |
| mallar | `bok/varld/platser/README.md`; i `bok/varld/research/README.md` en rad om platsens historia |

### 4.4 Uppdraget miljö (Världsbyggaren)

1. Läs `bok/varld/platser/<id>.md` om den finns, `bok/varld/varld.md` och kapitlets datum (om det är ett kapitel).
2. Kör `bok karta gatuvy <id>` (eller `<från> <till>` för en rutt).
3. Titta på varje bild med Read.
4. Skriv eller uppdatera `## Idag` med egna ord, med raderna `Källa`, `Fotograferat` och `Hämtat` från utskriften. Beskriv det bestående först (gatans sträckning, terräng, byggnadernas ålder och material, ljuset), sedan det föränderliga (butiker, skyltar, fordon). Skriv aldrig av skyltar, namn på verksamheter eller annan text i bilderna.
5. Kör `bok karta stada`.
6. Returnera: tre rader om platsen, fotodatum, och om kapitlets datum ligger mer än tio år från fotodatum ett förslag om platsens historia.

Världsbyggaren skriver bara i `## Idag` och `## Rutter` utan att fråga. `## Bokens tid` skrivs efter hennes ja.

### 4.5 Uppdraget platsens historia (Researchern)

När glappet är mer än tio år, eller när hon ber om det:

1. Läs platsfilen, `bok/varld/varld.md` och vilken tid som ska skildras.
2. Sök i öppna källor: DigitaltMuseum, Stockholmskällan och andra stadsmuseers bildarkiv, Alvin, Wikimedia Commons, Lantmäteriets historiska flygfoton, gamla kartor och tidtabeller, tidningar.kb.se, lokalhistoriska skrifter.
3. Titta på relevanta bilder med `bok bild <url>` och Read. Kör `bok karta stada` efteråt.
4. Skriv `bok/varld/research/plats-<id>.md`: frågan, vad källorna visar för den tiden, med länk, datering och licens per källa, vad som är säkert, troligt och okänt, och ett förslag till `## Bokens tid`.
5. Returnera förslaget. Skillen visar det för henne, och vid ja skriver Världsbyggaren in det under `## Bokens tid`.

Arkivbilder sparas aldrig i boken, bara länkar och egna beskrivningar.

### 4.6 Regeln för Writer

- *Bokens tid* går före *Idag*.
- Ur *Idag* används bara det som rimligen gällde vid kapitlets datum: gatans sträckning, terräng, äldre byggnader, ljus och väder. Butiker, skyltar, fordon, gatumöbler och teknik används inte, utom när kapitlet utspelar sig inom några år från fotodatum.
- Restider står som formuleringar i platsfilen eller scenkortet. Räkna aldrig om dem.

## 5. Fel

Alla fel i `karta.py` är `KartaFel(BokFel)` och ger exitkod 2 via `cli.main`. Inga URL:er och inga råa svar från Google visas.

| Situation | Meddelande |
|---|---|
| ingen nyckel | Det finns ingen nyckel till Google Maps. Se docs/google-maps.md och kör bok karta nyckel i din egen terminal. |
| 400 eller 403 med `API_KEY_INVALID` | Google godkänner inte nyckeln. Kontrollera den i Google Cloud och kör bok karta nyckel igen. |
| 403 eller `REQUEST_DENIED`, API ej aktiverat eller nyckeln begränsad | Nyckeln får inte använda <Routes API / Street View Static API>. Aktivera API:et och kontrollera nyckelns begränsningar (docs/google-maps.md). |
| 429 eller `OVER_QUERY_LIMIT` | Dagens tak för <API> är nått. Försök i morgon, eller höj taket i Google Cloud. |
| osignerat anrop nekas (403 på bild, metadata OK) | Street View kräver signering för fler anrop. Lägg till signeringshemligheten med bok karta nyckel --signering. |
| ingen rutt | på färdsättets rad: ingen rutt hittades |
| ingen gatubild | på punktens rad: ingen gatubild |
| nätet nere eller timeout (10 s) | Kunde inte nå Google Maps just nu. |
| platsen saknar adress | Platsen <id> har ingen adress. Lägg till adress i locations.json. |
| okänt id (ett argument utan mellanslag, siffror och kommatecken tolkas som id) | Platsen <id> finns inte i locations.json. Skriv en adress i stället, eller lägg till platsen. |
| `bok bild`: fel schema, inte bild, för stor | Bara bilder via https, högst 15 MB. |

## 6. Guiden `docs/google-maps.md`

Skriven för en författare utan teknikvana, i samma ton som `installera.md`:

1. **Vad det här är.**
   - `bok` kan visa restider och låta Claude titta på gatubilder och beskriva miljöer.
   - Det som sparas i boken är beskrivningar med egna ord, frågor och fotodatum, aldrig bilder eller Googles restider.
   - Allt är dagens värld.
2. **Vad det kostar.**
   - Ett Google Cloud-konto med betalning krävs.
   - Varje månad ingår 10 000 ruttanrop och 10 000 gatubilder, och fotodatum är gratis. En bok kommer sällan i närheten.
   - Sätt ett budgetlarm och ett dagstak ändå (steg 5).
3. **Skapa projektet:** konto, nytt projekt, betalning (Billing), med skärmens rubriker.
4. **Aktivera Routes API och skapa nyckeln:**
   - APIs & Services → Library → Routes API → Enable.
   - Credentials → Create credentials → API key.
   - Begränsa nyckeln: API restrictions → bara de API:er som används.
5. **Tak och larm:** Quotas → dagstak per API (förslag: 200 ruttanrop och 200 gatubilder per dag). Billing → Budgets & alerts.
6. **Street View, ett eget val.**
   - Googles villkor förbjuder att "skapa innehåll från Google Maps-innehåll" och att spara deras material.
   - `bok` sparar aldrig bilderna och låter Claude skriva egna beskrivningar. Utvecklaren tolkar det som tillåtet, men Google kan se det annorlunda, och det är ditt konto.
   - Vill du använda det: aktivera Street View Static API och lägg till det i nyckelns API restrictions.
   - Får du fel om signering: Credentials → URL signing secret, och sedan `bok karta nyckel --signering`.
7. **Lägg in nyckeln:**
   - Öppna Terminal (inte Claude) i vilken mapp som helst och kör `bok karta nyckel`. Klistra in nyckeln; den syns inte.
   - Kör `bok karta status`.
   - Klistra aldrig in nyckeln i chatten. Har det hänt: skapa en ny nyckel och ta bort den gamla.
8. **Använda det:** några exempel på vad man kan säga till Claude.
9. **Ta bort:** `bok karta nyckel --ta-bort`, och stäng av API:erna eller projektet i Google Cloud.

Länkar till guiden finns i `docs/installera.md`, i ett nytt avsnitt "Platser och miljöer" i `docs/hur-det-fungerar.md` och i bokens `README.md` (startfilen; gäller nya böcker). Skillen pekar dit när nyckel saknas.

## 7. Tester

pytest, inga riktiga anrop. `karta._oppna` (som tar en `urllib.request.Request` och returnerar status, headers och bytes) byts ut i testerna.

- **Nyckeln läcker aldrig:**
  - kör `restid`, `gatuvy` och `status` mot en falsk `_oppna` som kastar `HTTPError` (med URL:en med nyckeln som `filename`), `URLError`, `TimeoutError` och omdirigering,
  - kör via `cli.main` och kontrollera att nyckeln inte finns i stdout eller stderr,
  - samma när Google svarar med ett felmeddelande som innehåller nyckeln.
- **Nyckelfilen:** läses från miljövariabeln först, filen skrivs 0600 i en katalog med 0700, `--ta-bort` raderar, och `nyckel` utan terminal avbryter.
- **Signering:** känt testfall för HMAC-SHA1 med URL-säker base64.
- **Polyline:** avkodning mot Googles dokumenterade exempel. Punkter var M meter, tak och spridning. Bäring framåt och vid målet.
- **Routes-anropen:** rätt travelMode, field mask, `languageCode`, `departureTime`/`arrivalTime` för kollektivt, fel utanför 7 dagar bakåt och 100 dagar framåt, fel när både `--avgang` och `--ankomst` anges.
- **Utskriften:** attribution, beta-varningen bara när gång eller cykel ingår, "ingen rutt" per rad, kollektivtrafikens steg.
- **Gatuvy:** metadata före bild, `ZERO_RESULTS` hoppas över, samma `pano_id` hoppas över, datumformat (`ÅÅÅÅ-MM`, `ÅÅÅÅ`, saknas), sammanfattning av fotodatum, mappen ligger utanför boken med 0700, gamla mappar rensas, `stada` raderar.
- **`bok bild`:** fel schema, fel typ, för stor, omdirigering till annat schema.
- **Platser:** id med `adress`, id med `lat`/`lng`, id utan någondera, okänt id, fri adress.
- **`graph context`:** platsfil med båda delarna, glapp i år, kort glapp, inga datum, ingen platsfil, platsfil för plats som inte står i scenkortet.
- **`test_innehall`:** de nya mallarna och rollerna är genreneutrala. Rollerna nämner aldrig nyckelfilen som något de får läsa.
- **CI** gör inga nätanrop till Google.

## 8. Version och dokumentation

- **2.3.0 (minor):** nya kommandon, nya uppdrag för rollerna, nya valfria fält och en ny startfil. `bok init` uppgraderar ramverket i befintliga böcker och skapar `bok/varld/platser/README.md` om den saknas.
- **`CHANGELOG.md`** under Lagt till: restider, gatubilder och miljöbeskrivningar, platsens historia, `bok bild`, guiden.
- **`docs/utveckla-och-releasa.md`:** `karta` och `privat` i modullistan.
- **`docs/hur-det-fungerar.md`:** avsnittet "Platser och miljöer".
