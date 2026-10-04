# Design: `bok` 2.4 – förlagor, karaktärsverkstad och vägval

**Datum:** 2026-10-04
**Status:** Utkast för granskning
**Bygger på:** `docs/superpowers/specs/2026-10-03-bok-2-2-design.md`; testet med Cathie Wood som förlaga till Marléne i Sekretariatet (`bok/varld/research/cathie-wood-personportratt.md`, `bok/karaktarer/marlene-ostlund.md`); Soups forskningssyntes (`soup/research/SYNTHESIS.md`).

## 1. Mål

Två tillägg som gör att boken inte nöjer sig med förstabästa-idén:

1. **Komplexa karaktärer.** En verklig person som har intervjuats kan bli förlaga till en fiktiv karaktär. Researcher tar fram vad personen säger om sig själv och vad andra säger, med källkritik, och boken lånar en spänning mellan egenskaper, inte en biografi. Karaktärsmallen får plats för motsägelser och beteende under tryck, och en karaktärsverkstad prövar personen i provscener, som stilverkstaden gör med rösten.
2. **Vägval.** En lätt idéloop, lånad från Soup: rama in, kartlägg det uppenbara i separat kontext, dra frön utifrån, divergera i parallella grenar, kritisera med separata kritiker, visa en karta, låt författaren välja och styra.

Lyckat är när:

- ett förlageporträtt alltid anger vem som säger vad, i vilken relation och om det är förstahand,
- förlagans namn aldrig hamnar i manuset av misstag,
- karaktärsfilen beskriver personen och inte processen; datum och godkännanden ligger i `beslut.md`,
- en POV-person har motsägelser och ett konkret beteende under tryck innan första kapitlet, bedömt av Plot-arkitekten,
- ett vägval ger 4–6 distinkta riktningar på några minuter, där det uppenbara är känt men inte styr grenarna,
- slumpen i vägvalen kommer från verktyget och går att upprepa.

Inga nya fält blir obligatoriska i `bok status`; befintliga böcker fungerar som förut efter `bok init`.

### Utanför ramen

- Författarens egna intervjuer som underlag (transkript i `inkorg/`). Porträtt bygger på offentliga källor.
- Att en verklig person förekommer som sig själv i boken. Det hanteras som i dag via `canon.md`.
- Integration med Soup (MCP). Vägvalen är självständiga i `bok`.
- Bedömning av vägvalen med betyg eller rangordning.

## 2. Förlagor

### 2.1 Filerna

`bok/karaktarer/forlagor/<slug>.md`, kopierad från `bok/karaktarer/forlagor/MALL.md`. `bok/karaktarer/forlagor/README.md` förklarar mappen. Båda är bokfiler: de skapas av `bok init` om de saknas och rörs aldrig efter det. `bok status` räknar inte filer i undermappar som karaktärer (globben är redan icke-rekursiv).

Frontmatter:

```yaml
---
namn: Cathie Wood
alias: [Catherine Wood]   # valfritt
karaktarer: [marlene-ostlund]
---
```

Rubriker i mallen:

| Rubrik | Innehåll |
|---|---|
| Uppdraget | vilken karaktär, vad författaren vill låna och varför |
| Underlaget | vad materialet består av, vad det inte ger tillgång till, vems perspektiv som saknas |
| Självbild | vad personen säger om sig själv, med källa och datum |
| Andras bild | en punkt per iakttagelse: vem, relation till personen (mentor, tidigare chef, kritiker, journalist), förstahand eller återberättat, källa och datum |
| Motsägelser och spänningar | egenskaper som drar åt olika håll, med belägg |
| Röst i intervjuer | ordval, rytm, vad personen undviker; bara korta citat |
| Spärrar | det som inte får lånas eller påstås: diagnoser, privat hälsa, brott, närstående |
| Litterär tolkning | förslag till karaktären, uttryckligen märkta som förslag och inte fakta om personen |

### 2.2 Researcher: uppdraget *porträtt*

Nytt avsnitt i `bok-researcher`:

1. Läs uppdraget (karaktären och vad som ska lånas) och karaktärsfilen.
2. Sök porträtt, reportage och intervjuer med hög trovärdighet. Prioritera texter där andra än personen själv kommer till tals.
3. Skriv förlagan enligt mallen. Varje iakttagelse attribueras; skilj på det reportern såg, det andra berättar och det personen själv har berättat för någon annan.
4. Väg perspektiven: nuvarande medarbetare, tidigare chefer och kritiker har var sina skäl.
5. Tillskriv aldrig personen diagnoser, sjukdomar eller brott, och spekulera inte om privatlivet.
6. Returnera högst tio rader: vad underlaget räcker till, den starkaste spänningen och förslag till karaktären.

### 2.3 Skydd i `bok validate`

`bok validate` läser `namn` och `alias` ur alla förlagor och behandlar dem som rader i `blacklist`: en träff i kapitlet blockerar (exitkod 1) med meddelandet "<namn> är förlaga (bok/karaktarer/forlagor/<slug>.md) och får inte stå i manuset." Ett namn som också står i `kanda-namn` i `canon.md` undantas, för boken där personen faktiskt förekommer.

Träffen gäller även genitiv ("Cathie Woods"). Samma rättelse görs för `blacklist`, som i dag missar "Olof Palmes". En förlaga vars namn inte går att läsa (trasigt huvud, platshållare kvar) ger en varning i `bok validate`: namnet skyddas inte.

### 2.4 Sensitivitet

Förlagor är levande eller verkliga personer. `bok-sensitivitet` läser `bok/karaktarer/forlagor/` i uppdraget *planen* och bedömer om karaktären blir igenkännbar som personen på ett sätt som riskerar förtal eller kränkning. Grinden "Verkliga händelser" i `bok status` utlöses också när det finns minst en förlaga (fil utöver `MALL.md` och `README.md`) och byter då namn till "Verkliga personer och händelser". Böcker utan förlagor och utan verkliga händelser påverkas inte.

### 2.5 Writer läser aldrig förlagan

Som med stilexemplen: Writer arbetar från karaktärsfilen. Förlagan läses av skillen, Researcher, Sensitivitet och, vid behov, Plot-arkitekten. Det hindrar att biografiska detaljer glider in i texten.

## 3. Karaktärsmallen

`bok/karaktarer/MALL.md` behåller dagens rubriker (Kort, Önskan, Rädsla, Blind fläck, Språklig signatur, Båge, Relationer) och får nya:

| Rubrik | Innehåll |
|---|---|
| Förlaga | länk till `forlagor/<slug>.md` och vad som lånas, formulerat som en spänning ("vänlig och omöjlig att rubba"), inte som biografi |
| Motsägelser | två eller tre egenskaper som drar åt olika håll |
| Självbild och andras bild | hur personen ser sig själv, hur omgivningen ser hen, och glappet |
| Det hen döljer | vad, för vem och varför |
| Under tryck | konkret beteende när önskan och rädsla krockar: vad hen gör, säger och undviker |
| Vardag | humor, smak, vanor, det som gör personen till mer än sin funktion i handlingen |
| Öppet | idéer som inte är beslutade |

De nya rubrikerna har en kommentar (`<!-- … -->`) som ledtråd i stället för en platshållare `{{…}}`, så att de inte blir obligatoriska för POV-personer i `bok status`. Allt ovanför **Öppet** är beslutat. Datum, "godkänt" och processanteckningar skrivs i `bok/beslut.md`, inte i karaktärsfilen.

Mallen är en bokfil och uppdateras inte i befintliga böcker. Därför beskrivs rubrikerna också i en ny ramverksfil, `.claude/bok/hantverk/karaktarer.md` (genererad, skrivs om vid uppgradering), som skillen, Plot-arkitekten och Redaktören läser. I en befintlig bok lägger skillen till de nya rubrikerna i en karaktärsfil när karaktärsverkstaden körs för den personen.

`bok status` och POV-grinden ändras inte. Plot-arkitekten bedömer i uppdraget *grind* om varje POV-person har motsägelser och ett konkret beteende under tryck, och föreslår karaktärsverkstaden när det saknas.

## 4. Karaktärsverkstaden

Nytt avsnitt i skillen, efter Stilverkstaden. Körs när hon pratar om en person som känns platt, pekar ut en förlaga, eller när Plot-arkitekten föreslår det.

1. **Förlaga (valfritt).** Pekar hon ut en verklig person: starta `bok-researcher` med uppdraget *porträtt* och visa resultatet.
2. **Kärna.** Föreslå personkärnan som en spänning mellan egenskaper, utifrån förlagan och samtalet. Här föreslås vägval ("tre sätt att låna förlagan", se avsnitt 5).
3. **Tryckprov.** Starta `bok-writer` med uppdraget *tryckprov*: tre scener på cirka 200 ord var, utanför bokens handling, där personen (a) har fel inför andra, (b) blir ombedd om något hen inte vill ge, (c) har en vanlig dag. Spara dem i `bok/karaktarer/prov/<id>/`. Writer läser karaktärsfilen, rösten och `.claude/bok/hantverk/karaktarer.md`, aldrig förlagan.
4. **Läsning.** Hon säger vad som stämmer, vad som skaver och vad läsaren ska känna för personen. Skriv om en scen åt gången tills hon känner igen personen.
5. **In i filen.** Skriv in det valda under rätt rubriker i karaktärsfilen och en rad i `bok/beslut.md`.

Provscenerna är underlag, inte manus. De får inte kopieras in i kapitlen.

## 5. Vägval

### 5.1 När

- När hon ber om det ("ge mig vägval för …", "fler idéer", "jag vet inte hur hon ska …").
- Skillen **föreslår** det, men startar det aldrig själv, vid: premissen, karaktärskärnan i verkstaden, bågarnas vändpunkter (inciting incident, mittpunkt, klimax) och scenkort där Plot-arkitekten anger flera möjliga vägar eller fastnar.

Ett varv kostar ett tiotal agentanrop och tar några minuter. Skillen säger det när den föreslår vägval.

### 5.2 Varvet

1. **Rama in** (skillen, med henne, högst tre frågor). Skriv `ram.md`:
   - frågan, funktionellt ("hur korsar Marléne gränsen första gången?"), inte som en lösning,
   - det som måste hålla, hämtat ur premiss, canon, karaktärsfiler och bågar (visas, inte frågas),
   - vad som gör ett vägval bra för henne,
   - 3–5 tysta antaganden om lösningen ("det sker i en scen", "hon gör det ensam"),
   - relevanta tidigare varv: skillen söker i `bok/vagval/` (Grep) och nämner det som rör frågan.

   Visa ramen och få hennes ja innan varvet startar.
2. **Det uppenbara.** `bok-vagval` med uppdraget *uppenbart*, i egen kontext: 8–10 vägval som de flesta skulle komma på. Sparas i `uppenbart.md`. Visas aldrig för grenarna.
3. **Frön.** `bok fron --antal 4 --antagande "…" … --spara bok/vagval/<mapp>` (avsnitt 5.4).
4. **Grenar.** Fyra `bok-vagval` med uppdraget *gren*, parallellt, ett frö var och färsk kontext. Var och en får `ram.md` och sitt frö, säger ut kopplingen mellan frö och fråga ("vad i en bikupa motsvarar …, och varför") och ger 2–3 vägval. Varje vägval: en rubrik, en mening, hur det ser ut i en scen, vad det ändrar i planen. Skillen numrerar dem `v1`, `v2`, … och samlar dem i `ideer.md` med fröet som ursprung.
5. **Kritik.** `bok-idekritiker` i egen kontext läser `ram.md`, `uppenbart.md` och `ideer.md`:
   - sållar bort vägval som i sak är något på `uppenbart.md`, och anger vilket,
   - sållar bort vägval som bryter mot det som måste hålla (godkänt/underkänt, inget betyg),
   - skriver tre separata anteckningar per kvarvarande vägval: **värde** (vad som är bra, vad det öppnar), **rimlighet** (mot karaktärerna, canon och premissen) och **djävulens advokat** (det starkaste skälet att avstå),
   - grupperar dem i 4–6 riktningar med namn och kärna.

   Ingen sammanvägning och ingen rangordning. Skriver `karta.md`.
6. **Karta.** Skillen visar riktningarna: namn, kärna, varje vägvals id, rubrik och mening, och kort de tre anteckningarna. Sist en rad om det uppenbara, eftersom det uppenbara också får vinna.
7. **Välj och styr.** Hon väljer 1–3 vägval och säger åt vilket håll ("mörkare", "kombinera v3 och v7", "billigare för handlingen"). `bok-vagval` med uppdraget *utveckla* kombinerar, förenklar eller ändrar en aspekt och ger 2–4 nya vägval, markerade "utvecklar v3". Kritikern läser dem. Fastnar ett varv kan skillen dra ett processfrö (`bok fron --klass process --antal 1`). Högst två utvecklingsvarv; sedan bestämmer hon.
8. **Beslut.** Det valda skrivs in där det hör hemma (karaktärsfil, bågar, struktur, scenkort) efter hennes ja, och `val.md` och en rad i `bok/beslut.md` får länk till varvets mapp. Väljer hon inget sparas varvet ändå.

Hon väljer alltid. Skillen rekommenderar inte ett vägval före kartan och väljer aldrig åt henne.

### 5.3 Filer

`bok/vagval/<ÅÅÅÅ-MM-DD>-<slug>/` med `ram.md`, `uppenbart.md`, `fron.md`, `ideer.md`, `karta.md` och `val.md`. `bok/vagval/README.md` (bokfil) förklarar mappen. Mapparna är bokens idébank och raderas aldrig av verktyget; vägval som inte valdes kan väckas i ett senare varv.

### 5.4 `bok fron`

```
bok fron [--antal N] [--klass KLASS ...] [--antagande TEXT ...] [--slump TAL] [--spara MAPP] [--json]
```

- Drar frön med en seedad slumpgenerator (`random.Random(slump)`) ur listor i paketet, `src/bok/data/fron/<klass>.txt`, en rad per frö, kommentarer med `#`.
- Klasser: `doman` (avlägsna domäner och fenomen), `omvandning` (operatorer som vänder, tar bort, överdriver, flyttar i tid), `begransning` (udda villkor: "utan dialog", "inom en timme", "sett av ett barn"), `process` (hur man arbetar när det fastnar; dras inte som standard) och `forlaga` (bokens egna förlagor, ur `bok/karaktarer/forlagor/`; bara om några finns).
- Standard för `--antal 4` utan `--klass`: en `doman`, en `omvandning`, en `begransning` och en fjärde ur dessa tre, eller `forlaga` om boken har förlagor.
- En `omvandning` paras med ett av `--antagande`, valt av samma slumpgenerator. Utan antaganden skrivs operatorn ensam.
- `--slump` utelämnat: ett tal väljs och skrivs ut, så att dragningen går att upprepa.
- `--spara MAPP` skriver `MAPP/fron.md` med slumptalet, klasserna och fröna. Mappen skapas om den saknas.
- `--json` för skillen: `{"slump": 4711, "fron": [{"klass": "doman", "text": "…", "antagande": null}, …]}`.
- Samma frö dras inte två gånger i ett anrop. Tar fröna slut, eller begärs `forlaga` i en bok utan förlagor: felmeddelande och exitkod 2, som andra fel i `bok`. Okänd klass avvisas av kommandoraden.
- Fungerar även utanför en bok; då finns ingen `forlaga`.

Listorna skrivs för `bok` på svenska, minst 40 rader per klass (cirka 80 för `doman`, 70 för `begransning`, 50 för `omvandning`, 40 för `process`). Inga texter från Oblique Strategies eller andra skyddade kortlekar.

### 5.5 Rollerna

- **`bok-vagval`**: uppdragen *uppenbart*, *gren* och *utveckla*. Läser bara det uppdraget anger (`ram.md`, fröet, de valda vägvalen). Läser aldrig `uppenbart.md` i uppdragen *gren* och *utveckla*. Skriver konkret: varje vägval ska gå att se som en scen.
- **`bok-idekritiker`**: uppdraget *kritik*. Håller de tre anteckningarna isär, ger inga betyg och dödar inte ett vägval för att det är ovanligt; värdeanteckningen skrivs först.

Båda är genererade ramverksfiler med versionshuvud och kan kompletteras med `bok/roller/<roll>.local.md`.

## 6. Ändringar i befintliga filer

| Fil | Ändring |
|---|---|
| `skills/bok/SKILL.md` | tabellen i Fritt samtal: "en verklig person som förlaga" → karaktärsverkstaden, "flera möjliga vägar" → vägval; nya avsnitt Karaktärsverkstaden och Vägval; i Innan första kapitlet nämns förlagor i sensitivitetsgrinden |
| `bok/process.md` | förlagor, karaktärsverkstaden och vägval; Writer läser aldrig förlagor; lästabellen för de nya uppdragen |
| `bok/verktyg.md` | `bok fron`; att `bok validate` stoppar förlagornas namn |
| `agents/bok-researcher.md` | uppdraget *porträtt* |
| `agents/bok-writer.md` | uppdraget *tryckprov*; läser aldrig `bok/karaktarer/forlagor/` |
| `agents/bok-plot-arkitekt.md` | grinden bedömer motsägelser och under tryck för POV-personer; föreslår vägval vid scenkort med flera möjliga vägar |
| `agents/bok-sensitivitet.md` | uppdraget *planen* läser förlagorna |
| `agents/bok-redaktor.md` | läser `.claude/bok/hantverk/karaktarer.md` för axeln `karaktar` |
| `status.py` | grinden utlöses också av förlagor och heter då "Verkliga personer och händelser" |
| `validera.py` | förlagornas `namn` och `alias` som blacklist, utom de som står i `kanda-namn` |
| `cli.py`, ny `fron.py` | kommandot `bok fron` |
| `data/bok/bok/karaktarer/MALL.md` | nya rubriker |
| nya bokfiler | `karaktarer/forlagor/README.md`, `karaktarer/forlagor/MALL.md`, `karaktarer/prov/README.md`, `vagval/README.md` |
| nya ramverksfiler | `agents/bok-vagval.md`, `agents/bok-idekritiker.md`, `bok/hantverk/karaktarer.md` |
| `docs/hur-det-fungerar.md`, `README.md` (bokens) | förlagor, karaktärsverkstaden, vägval |
| `CHANGELOG.md` | under [Unreleased]; släpps som 2.4.0 |

## 7. Test

- `bok fron`: samma `--slump` ger samma frön; standardfördelningen över klasser; `omvandning` paras med ett antagande; `forlaga` dras bara när förlagor finns och läser `namn`; inga dubbletter; okänd klass avvisas och slut på frön ger exitkod 2; `--spara` lägger till i en befintlig `fron.md`; `--spara` skriver `fron.md`; `--json` har rätt form; varje lista i paketet har minst 40 frön och inga dubbletter.
- `bok validate`: förlagans `namn` och `alias` blockerar; namn i `kanda-namn` undantas; `MALL.md` och `README.md` i `forlagor/` läses inte som förlagor; trasig frontmatter i en förlaga kraschar inte.
- `bok status`: förlagor utlöser grinden med det nya namnet; utan förlagor och utan verkliga händelser syns ingen grind; filer i `karaktarer/forlagor/` och `karaktarer/prov/` räknas inte som karaktärer.
- `bok init`: nya bokfiler skapas i en befintlig bok utan att röra befintliga; nya ramverksfiler skrivs med versionshuvud.
- Ramverkstexterna: de nya rollerna har giltig frontmatter (namn, beskrivning, verktyg); skillen hänvisar bara till kommandon som finns i `bok --help`.
- Manuellt: ett vägvalsvarv och en karaktärsverkstad i en provbok, med Sekretariatets Marléne som fall.

## 8. Öppna frågor

Inga. Avvägningar som gjorts:

- POV-grinden i `bok status` ändras inte; komplexiteten bedöms av Plot-arkitekten. Annars skulle befintliga böcker blockeras vid uppgradering.
- Förlagor utlöser sensitivitetsgrinden. Det är en ny grind för böcker med förlagor, men inte för befintliga böcker utan.
- Kritikern använder samma modell som generatorerna men egen kontext. Soups råd om olika modellfamiljer går inte att följa inom Claude Code utan extra installation.
