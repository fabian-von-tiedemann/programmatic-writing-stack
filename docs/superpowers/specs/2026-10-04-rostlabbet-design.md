# Design: `bok` 2.5 – Röstlabbet

Underlag: Soup-körningen `ideas/2026-10-04-ett-eget-sprak-och-litterar-hojd-i-bok-harnesset/` (karta, kritik och styrvarv) och samtalet med utvecklaren 2026-10-04.

## 1. Mål

`bok` ska kunna skriva på en ny nivå när en bok vill det: tillsammans med författarna söka fram ett eget uttryck, en röst och en form som inte bara härmar kända författare, och sedan hålla det genom hela boken. Alla böcker behöver inte det; det är ett val per bok.

Författarna skriver inte prosan själva. De formar idén, kommer med inspel och väljer. Rösten hittas därför genom att **välja bland genererade alternativ**, inte genom att skriva, och hålls genom **ankare som går att mäta**: godkända provstycken, ett recept, en antiröst och en profil som CLI:n räknar fram.

Lyckat är när:

- författarna känner igen sin bok i ett provstycke, och rösten inte går att härleda till en enda förebild,
- Writer håller rösten i kapitel 12 lika väl som i kapitel 1,
- `bok rost drift` deterministiskt visar när ett kapitel ligger närmare AI-genomsnittet än rösten,
- det som författarna pekat ut som levande inte slipas bort av granskningen,
- formen är ett medvetet val för boken, inte en följd av mallen.

Allt nytt ligger bakom modulen `rostlabb`. Utan den fungerar `bok` som i 2.4; stilverkstaden finns kvar.

### Utanför ramen

- Att författaren skriver grovutkast som Writer putsar, och loggar över författarens egna strykningar (Soup i-0087, i-0088, i-0092). Författarna skriver inte prosa; det här kan bli aktuellt senare.
- Egna skuggutkast per scenkort (i-0074). Kontrollvarianterna från labbet fyller den rollen.
- Ordklasstaggning eller andra språkmodeller i CLI:n (spaCy, Stanza). Allt räknas med standardbiblioteket.
- Att ta bort golvet på 8 i granskningen. Det gäller som förut, utom för låsta ställen (avsnitt 5.4).
- Integration med Soup (MCP).

## 2. Modulen `rostlabb`

`bok mall rostlabb` slår på modulen som andra tillval: den läggs i `moduler` i `bok.toml` och skapar bokfilerna nedan om de saknas. Beskrivning i `bok mall`: "Röstlabbet: sök bokens röst och form genom att välja bland varianter, och håll den med mätbara ankare."

Ramverket (skill, process, roller) installeras alltid. Avsnitten om Röstlabbet gäller bara när `rostlabb` står i `moduler`; skillen läser `bok.toml`.

Nya bokfiler från modulen:

```
bok/stil/labb/README.md         hur labbet går till, receptets form
bok/stil/labb/provscener.md     de två provscenerna (fylls i labbet)
bok/stil/provbank/README.md     godkända provstycken, ett per fil
bok/stil/kontroll/README.md     kontrollvarianter (AI-genomsnittet), ett per fil
bok/stil/pekningar/README.md    levande och döda ställen per kapitel
```

Claude föreslår modulen när författaren pratar om ett eget språk, litterär höjd eller att boken låter som AI.

## 3. Röstlabbet

Labbet ersätter stilverkstaden i böcker med modulen. Det har två sorters prov, med samma varv.

### 3.1 Två sorters prov

- **Formprov.** En skiss av första akten på en sida, i fyra radikalt olika former (protokoll, omvänd kronologi, kapitel som dokument, en berättare som utelämnar). Prövar det som bara syns i bokens skala: komposition, vad som utelämnas, hur tiden rör sig. Skrivs av `bok-plot-arkitekt`, uppdraget *formprov*.
- **Röstprov.** Två fasta provscener ur boken, 250–350 ord var: en stilla och en under tryck. Samma scener i varje generation, så att varianterna går att jämföra; en röst ska klara båda. Skrivs av `bok-writer`, uppdraget *röstprov*.

Skillen rekommenderar formen först, eftersom formen ofta bestämmer rösten, men författarna kan börja med rösten eller hoppa över formen.

### 3.2 Recept

En variant byggs från ett recept: 3–6 drag, vart och ett med en källa.

```
- Distans: berättaren registrerar, tolkar aldrig. (Ernaux)
- Upprepning i repliker som vägrar svara. (Fosse)
- Mötesprotokollets passiv när makten talar. (frö: kalla – mötesprotokoll)
```

Källan är en förebild som författarna nämnt (deras texter i `bok/stil/exempel/`, som i dag) eller ett frö ur `bok fron`. Tre nya klasser i `bok fron` (avsnitt 6.1): `rostdrag` (meningsnivå: "inga bisatser", "andra person", "meningar som slutar i ett substantiv"), `formgrepp` (bokens skala: "kapitel som dokument", "omvänd kronologi", "en scen berättas två gånger") och `kalla` (texter utanför litteraturen: sjörapport, liturgi, rättegångsprotokoll, telegram, bruksanvisning, mötesprotokoll).

### 3.3 Varvet

1. **Rama in** (skillen, med författarna): förebilderna, vad boken inte får låta som, och vilka provscener (eller vilken akt för formprov). Skriv provscenerna i `bok/stil/labb/provscener.md`. Få ett ja.
2. **Generation 0.** Skillen sätter ihop fyra recept: två ur förebilderna med ett frö var, två huvudsakligen ur frön (`bok fron --klass rostdrag kalla formgrepp --antal 8 --spara bok/stil/labb`). Fyra instanser av rollen skriver parallellt, ett recept var, i egna kontexter.
3. **Kontrollvariant.** En femte instans skriver samma prov utan recept och utan `rost.md`: AI-genomsnittet. Den visas sist, märkt som kontroll. Röstprovens kontroller sparas också i `bok/stil/kontroll/`; formprovets kontroll (mallens standardform) stannar i generationsfilen, eftersom en synopsis inte ska räknas in i `bok rost drift`.
4. **Kritik.** `bok-idekritiker`, uppdraget *röstprov*, läser varianterna och sållar: pastisch (för nära en enda förebild), AI-genomsnitt (för likt kontrollen), recept som inte följts. Ingen rangordning, inga betyg.
5. **Visa och peka.** Skillen visar varianterna A–D och kontrollen. Författarna pekar i fri form: "B: 'han räknade stolarna' lever, slutet är dött. D:s rytm men inte orden." Skillen skriver pekningarna under varianten i generationsfilen.
6. **Nästa generation.** Skillen bygger fyra nya recept ur pekningarna: *korsa* (levande drag från två varianter), *mutera* (byt ett drag mot ett nytt frö), *förstärk* (driv ett levande drag längre) och *vild* (ett helt nytt frö). Ny kontrollvariant bara om provscenen bytts.
7. **Slut** när författarna säger att det är boken. Efter femte generationen frågar skillen om rösten håller på att sätta sig eller om provscenen ska bytas. Inget fast tak.

Generationerna sparas i `bok/stil/labb/gen-NN.md` (röst) och `bok/stil/labb/form-NN.md` (form): recepten med källor, texterna, kritikerns sållning och pekningarna.

### 3.4 Vad labbet lämnar efter sig

Efter författarnas ja:

- **`bok/stil/rost.md` i receptform** (avsnitt 4.1).
- **Provbanken:** de godkända provstyckena, ett per fil i `bok/stil/provbank/<id>.md` med frontmatter `lage: stilla|tryck`, `kalla: gen-03 B` och `datum`.
- **Kontrollen:** kontrollvarianterna i `bok/stil/kontroll/`.
- **Formlagen** (om formprov gjorts): rubriken `## Formlag` i `bok/koncept/form.md`: vad formen måste göra, vad den aldrig får göra, och varför den här boken ser ut så. En hypotes som får revideras vid aktgränser.
- En rad i `bok/beslut.md` med länk till generationsfilen.

## 4. Rösten under skrivandet

### 4.1 `rost.md` som recept

Med modulen har `rost.md` tre rubriker i stället för adjektiv:

- `## Recept` – dragen med källa, en rad om hur draget märks, och ett kort exempel ur ett godkänt provstycke.
- `## Antiröst` – konkreta mönster ur kontrollvarianterna och ur döda ställen, med exempel. Bokens egen anti-monster.
- `## Form` – hänvisning till formlagen i `bok/koncept/form.md`.

POV-röster (`rost-<id>.md`) fungerar som förut, ovanpå receptet.

### 4.2 Vad Writer läser

Utöver dagens lista: 2–3 stycken ur provbanken, valda deterministiskt av `bok rost urval --kapitel N` utifrån scenkortets `lage`. Writer läser aldrig hela provbanken och, som i dag, aldrig `bok/stil/exempel/`. Writer återger aldrig formuleringar ur provbanken; provstyckena visar hur det låter, inte vad som står.

### 4.3 Provbanken växer med boken

Ställen som författarna pekat ut som levande i kapitlen (avsnitt 5.4) föreslås till provbanken. Taket är 15 stycken; vid aktgränsen rensar författarna banken tillsammans med skillen.

## 5. Skrivloopen med modulen

### 5.1 Scenkortet

Två fält i `bok/plot/kapitel/MALL.md` (tomma och utan verkan utan modulen):

- `vagar:` – vad kapitlet vågar: ett formbrott, något som undanhålls, en tidsförskjutning, en moralisk obekvämhet. Plot-arkitekten föreslår två eller tre; författarna väljer eller skriver eget.
- `lage: stilla|tryck` – styr urvalet ur provbanken.

`bok status` kräver inget av fälten.

### 5.2 Mekanisk kontroll

Steg 4 kör också `bok rost drift manuskript/kapitel-NN.md`. Varningarna blockerar inget och följer med till Språkgranskaren.

### 5.3 Granskning

- **Språkgranskaren** bedömer `rost` mot receptet, antirösten och driftrapporten.
- **Redaktören** bedömer under `struktur` om kapitlet gör det `vagar` lovar.
- Båda rapporterna får två nya avsnitt i brödtexten: `## Mest levande` och `## Mest döda`, med citat och en rad om varför. Ingen ändring i frontmatter eller i `bok rapport spara`.

### 5.4 Författarna pekar

Efter runda 1, före första revisionen, och frivilligt. Skillen visar granskarnas levande och döda kandidater. Författarna säger vad som lever och vad som är dött, eller "kör" för att hoppa över.

Skillen skriver `bok/stil/pekningar/kapitel-NN.md`:

```
## Lever
- "Han räknade stolarna två gånger innan han satte sig."

## Dött
- "Tystnaden lade sig över rummet."
```

- **Lever** = låst. `bok validate manuskript/kapitel-NN.md` stoppar (BLOCKERANDE) om ett levande citat inte längre finns ordagrant i kapitlet (avsnitt 6.3). Granskarna får kommentera låsta ställen men inte kräva ändringar i dem, och golvet på 8 gäller inte för dem.
- **Dött** = det Writer skriver om först i revisionen.
- Ett låst ställe låses upp genom att författarna säger det; skillen flyttar raden till `## Upplåst`.

### 5.5 Aktgränsen

Förläggaren läser akten också mot formlagen och svarar på om formen fortfarande bär. Skillen frågar om receptet håller. Författarna kan köra en ny labbgeneration på en scen ur akten och revidera receptet och formlagen; då rensas provbanken.

## 6. CLI

### 6.1 `bok fron`

Tre nya klasser: `rostdrag`, `formgrepp`, `kalla`, i `src/bok/data/fron/<klass>.txt`, minst 40 frön var. De ingår inte i standardfördelningen; de dras bara med `--klass`.

### 6.2 `bok rost`

Ny modul `src/bok/rost.py`. Bara standardbiblioteket. Texten förbehandlas: frontmatter, rubriker och HTML-kommentarer tas bort; meningar delas på `.`, `!`, `?` och `…` följt av blanktecken och versal; repliker är stycken som börjar med `–`, `—` eller `"`.

```
bok rost profil [--json]
bok rost drift KAPITELFIL [--json]
bok rost urval --kapitel N [--antal 3] [--json]
```

**`profil`** räknar ur provbanken:

- meningslängd i ord: median, kvartilavstånd, andel meningar under 6 ord och över 30 ord,
- styckelängd i meningar: median,
- andel ord i repliker,
- skiljetecken per 1000 ord: komma, semikolon, kolon, tankstreck, frågetecken,
- andel meningar som börjar med ett pronomen (lista i paketet),
- relativ frekvens för funktionsorden i en fast svensk lista (cirka 150 ord, `src/bok/data/rost/funktionsord.txt`).

**`drift`** jämför kapitlet med provbanken (rösten) och kontrollen (AI-genomsnittet):

- **Delta.** Burrows Delta på funktionsorden: z-poäng mot medel och standardavvikelse över provbank och kontroll, medelvärdet av absoluta skillnader mot provbankens centroid och mot kontrollens. Är avståndet till kontrollen mindre än till provbanken: varning "närmare AI-genomsnittet än rösten", med båda talen.
- **Mått utanför spridningen.** Varje profilmått där kapitlet ligger utanför provbankens min–max med mer än 25 % av spannet listas med kapitlets värde och bankens spann.
- **Pastisch.** Sekvenser om minst 5 ord (gemener, utan skiljetecken) som kapitlet delar med en fil i provbanken eller i `bok/stil/exempel/` listas med källfil.
- **För lite underlag.** Färre än 3 provstycken eller färre än 2 kontrollvarianter: meddelandet säger det, och bara pastischkontrollen körs.
- Exitkod 0 med varningar; 2 vid fel (saknad fil, bok utan modulen), som andra kommandon.

**`urval`** läser scenkortets `lage` och väljer `--antal` stycken ur provbanken med samma `lage` (alla om `lage` saknas), nyaste först efter `datum`, sedan filnamn. Skriver sökvägarna.

### 6.3 `bok validate`

Läser `bok/stil/pekningar/kapitel-NN.md` om den finns för kapitlet och kontrollerar att varje citat under `## Lever` finns ordagrant (blanktecken normaliserade, typografiska citattecken likställda). Saknas ett: BLOCKERANDE med citatet. Trasig eller tom pekningsfil kraschar inte.

## 7. Ändringar i befintliga filer

| Fil | Ändring |
|---|---|
| `skills/bok/SKILL.md` | avsnittet Röstlabbet (varvet i 3.3) när modulen är på; tabellen i Fritt samtal pekar till labbet i stället för stilverkstaden; pekning efter runda 1; `bok rost drift` i mekanisk kontroll; fråga om receptet vid aktgräns; föreslå modulen |
| `bok/process.md` | Röstlabbet, receptet, provbanken, pekningar och låsta ställen, `vagar` och `lage`; lästabellen för de nya uppdragen |
| `bok/verktyg.md` | `bok rost`, nya klasser i `bok fron`, pekningar i `bok validate` |
| `agents/bok-writer.md` | uppdraget *röstprov*; läser `bok rost urval` med modulen; återger aldrig provbanken; skriver om döda ställen först, rör aldrig levande |
| `agents/bok-plot-arkitekt.md` | uppdraget *formprov*; föreslår `vagar` och sätter `lage` i scenkortet |
| `agents/bok-idekritiker.md` | uppdraget *röstprov* (sållar pastisch, AI-genomsnitt, recept som inte följts) |
| `agents/bok-sprakgranskare.md` | `rost` mot receptet och driftrapporten; avsnitten Mest levande och Mest döda; låsta ställen |
| `agents/bok-redaktor.md` | `vagar` under `struktur`; avsnitten Mest levande och Mest döda; låsta ställen |
| `agents/bok-forlaggare.md` | läser formlagen vid aktgräns |
| `cli.py`, ny `rost.py` | kommandot `bok rost` |
| `fron.py` | klasserna `rostdrag`, `formgrepp`, `kalla` |
| `validera.py` | låsta ställen ur pekningar |
| `mallar.py` | modulen `rostlabb` med beskrivning |
| `data/bok/bok/plot/kapitel/MALL.md` | fälten `vagar` och `lage` |
| nya paketfiler | `data/fron/rostdrag.txt`, `formgrepp.txt`, `kalla.txt`; `data/rost/funktionsord.txt`, `data/rost/pronomen.txt`; `data/moduler/rostlabb/…` (avsnitt 2) |
| `README.md`, `docs/hur-det-fungerar.md`, `CHANGELOG.md` | Röstlabbet, `bok rost`, modulen |

## 8. Test

- `bok rost profil`: kända värden på en liten provbank (meningslängd, kvartilavstånd, repliker, skiljetecken, pronomenstart); frontmatter, rubriker och kommentarer räknas inte; tom provbank ger meddelande och exitkod 2.
- `bok rost drift`: ett kapitel byggt av kontrolltexter hamnar närmare kontrollen; ett byggt av provbankstexter hamnar närmare rösten; mått utanför spridningen listas; delade 5-ordssekvenser med provbank och exempel hittas med källfil; för lite underlag ger bara pastischkontrollen; bok utan modulen ger exitkod 2.
- `bok rost urval`: väljer på `lage`, ordning efter datum och filnamn, `--antal` respekteras, saknat scenkort ger fel.
- `bok validate`: levande citat som finns passerar; ändrat citat blockerar; blanktecken och citattecken normaliseras; `## Upplåst` ignoreras; trasig pekningsfil kraschar inte.
- `bok fron`: de nya klasserna har minst 40 frön och inga dubbletter; de dras inte i standardfördelningen.
- `bok mall rostlabb`: skapar filerna utan att röra befintliga; läggs i `moduler`.
- Ramverkstexterna: nya uppdrag finns i rollerna; skillen hänvisar bara till kommandon som finns i `bok --help`.
- Manuellt: två generationer av labbet på Sekretariatet (formprov och röstprov), och ett kapitel genom loopen med pekning och `bok rost drift`.

## 9. Öppna frågor

Inga. Avvägningar som gjorts:

- Delta på en liten provbank (5–15 stycken) är brusig. Därför ger `drift` bara varningar, kräver ett minsta underlag och visar talen så att Språkgranskaren och författarna kan väga dem.
- Golvet på 8 behålls. Kritiken i Soup-körningen pekar på att det slätar ut; låsta ställen och avsnitten Mest levande och Mest döda är det första motdraget. Visar provet att det inte räcker tas golvet upp i en senare version.
- Kritikern och generatorerna är samma modell med olika kontext, som i vägvalen.
- Labbet bygger på att författarna väljer. Skillen rekommenderar ingen variant och väljer aldrig åt dem.
