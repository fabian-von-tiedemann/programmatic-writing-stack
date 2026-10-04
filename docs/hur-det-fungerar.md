# Hur bok fungerar

För dig som skriver med `bok`, eller som vill förstå vad som händer bakom samtalet. Installationen står i [installera.md](installera.md).

## Idén i korthet

Du pratar med Claude om din bok. Claude skriver prosan och en grupp specialiserade roller granskar den; du bestämmer. Allt som bestäms hamnar i vanliga textfiler i bokens mapp, så att boken minns sig själv mellan samtalen och går att läsa utan verktyget.

`bok` är ett litet program (ett kommandoradsverktyg) som gör tre saker:

1. **Lägger ramverket i boken.** `bok init` skriver instruktionerna som Claude följer: en skill, rollerna och processen.
2. **Håller ordning.** `bok status` räknar ut var boken står och vad nästa steg är, utifrån filerna.
3. **Kontrollerar det mekaniska.** Namn, tidslinje, åldrar, upprepade ord och vem som vet vad räknas ut av verktyget, inte av Claude.

Claude anropar kommandona själv. Du behöver aldrig skriva dem.

## Vad som finns i en bok

| Var | Vad | Vem äger det |
|---|---|---|
| `inkorg/` | ditt råmaterial: chattar, anteckningar, gamla utkast, lektörsbrev | du |
| `bok/` | planen och minnet: idén, personerna och deras förlagor, handlingen, rösten, världen, besluten, vägvalen, sammanfattningar per kapitel, grafen och granskningarna | boken |
| `manuskript/` | kapitlen | boken |
| `bok.toml` | titel och inställningar | boken |
| `.claude/skills/bok/`, `.claude/agents/bok-*.md`, `.claude/bok/` | ramverket: skillen, rollerna, processen, hantverksreglerna | verktyget |
| `CLAUDE.md` | ett block mellan `<!-- bok:start -->` och `<!-- bok:end -->` som pekar Claude till skillen | verktyget äger blocket, resten är ditt |

Ramverkets filer har ett versionshuvud och skrivs om när du uppgraderar. Bokens filer skapas bara om de saknas och rörs aldrig efter det. En ramverksfil som någon har ändrat för hand (huvudet borttaget) lämnas också orörd. Egna tillägg till en roll skrivs i `bok/roller/<roll>.local.md`.

## Från idé till färdig bok

### Förberedelse

Fritt samtal i vilken ordning som helst: idén, personerna, handlingen, rösten. I **stilverkstaden** visar du texter du gillar och Claude provskriver en scen ur din bok i olika röster tills rösten sitter. En POV-person kan få en egen röst ovanpå bokens.

I **karaktärsverkstaden** prövas en person i tre korta scener där hen sätts under tryck, tills du känner igen personen. En karaktär kan bygga på en verklig person, en **förlaga**: Researcher tar fram vad personen säger om sig själv och vad andra säger om hen, med källor, och boken lånar en spänning mellan egenskaper, aldrig en biografi. Står förlagans namn i ett kapitel stoppar `bok validate` det. Ska personen förekomma som sig själv skriver du namnet bland kända namn i `bok/canon.md`.

Innan första kapitlet skrivs ska koncept, karaktärer, plot, röst och kapitelplanen för första akten vara ifyllda. Bygger boken på verkliga händelser, eller har den förlagor, läses planen först av sensitivitetsläsaren. Sist får du en sammanfattning av boken på en skärm och säger ja.

### Skrivloopen, kapitel för kapitel

1. **Scenkort.** Plot-arkitekten planerar kapitlets scener. Du godkänner.
2. **Utkast.** Writer skriver kapitlet.
3. **Fackgranskning**, bara för kapitel med fackinnehåll: Researcher kontrollerar påståendena mot källor.
4. **Mekanisk kontroll.** `bok validate` och `bok tics` letar efter fel namn, tidsfel och språkliga tics.
5. **Granskning.** Redaktör och Språkgranskare betygsätter kapitlet 1 till 10 på var sin uppsättning axlar. Godkänt kräver minst 8 på varje axel.
6. **Revision.** Högst två varv. Är granskarna fortfarande inte nöjda bestämmer du.
7. **Kontinuitet.** Grafen och sammanfattningen uppdateras och brott mot det som är bestämt flaggas.
8. **Din läsning.** Du godkänner kapitlet eller skickar tillbaka det.

Efter varje akt läser Förläggaren hela akten. När boken är klar gör Förläggaren en slutläsning och sensitivitetsläsaren läser hela boken.

Du kan alltid fråga "var är vi?" och få svaret från `bok status`.

### Respons utifrån

Ett lektörsbrev eller betaläsarnas kommentarer läggs i `inkorg/` eller klistras in. Claude delar upp responsen i punkter och föreslår för varje punkt om du ska ta till dig, avböja eller fundera. Det du tar till dig blir rader i `bok/revisioner.md`, som Writer arbetar efter.

### Vägval

När det finns flera möjliga vägar och den första idén inte räcker kan du be om vägval. Claude ramar in frågan med dig, en roll listar det uppenbara för sig, `bok fron` drar slumpade frön ur listor som följer med verktyget, fyra roller tar ett frö var, och en kritiker sållar bort det uppenbara och det som bryter mot boken. Du får 4–6 riktningar med vad som är bra, vad som är rimligt och det starkaste skälet att avstå, men inga betyg. Du väljer och kan be om ett varv till. Varven sparas i `bok/vagval/`.

### Röstlabbet

För böcker som vill mer än ett korrekt språk: `bok mall rostlabb`. Labbet ersätter stilverkstaden. Ni skriver inte själva; ni väljer. Claude skriver fyra varianter av samma prov, var och en efter ett recept av drag som lånas från förebilder ni valt eller från slumpade frön (drag på meningsnivå, formgrepp, texter utanför litteraturen som protokoll och liturgi), och en femte utan recept som visar hur AI låter utan riktning. Ni pekar ut vad som lever och vad som är dött, och nästa generation korsar, muterar och förstärker det. Formprovet söker bokens form i en skiss av första akten; röstprovet söker rösten i två provscener.

När ni känner igen boken blir rösten ett recept i `bok/stil/rost.md`, provstyckena en provbank och formen en formlag i `bok/koncept/form.md`. Under skrivandet läser Writer några provstycken inför varje kapitel, `bok rost drift` varnar när ett kapitel ligger närmare AI-genomsnittet än rösten, och ställen ni pekat ut som levande låses så att granskningen inte slipar bort dem.

## Rollerna

| Roll | Gör |
|---|---|
| Plot-arkitekt | struktur, bågar, scenkort; bedömer om planen håller |
| Writer | skriver och reviderar prosan; tryckprov i karaktärsverkstaden |
| Redaktör | granskar struktur, karaktär, spänning, kontinuitet och tema |
| Språkgranskare | granskar prosa, dialog och röst |
| Kontinuitet | håller grafen och sammanfattningarna; flaggar motsägelser |
| Researcher | research, fackgranskning mot källor och porträtt av förlagor |
| Världsbyggare | världens regler, platser och historia |
| Sensitivitet | verkliga personer och händelser, representation, respekt |
| Förläggare | läser akter och hela boken som en förlagsläsare |
| Vägval | tar fram vägval: det uppenbara, en gren ur ett frö, en utveckling av det du valt |
| Idékritiker | sållar och grupperar vägvalen, utan betyg |
| Audiobook, Marknad | tillval när boken är klar |

Rollerna läser sammanfattningar och utdrag ur grafen i stället för hela manuset, så att de håller sig skarpa även i en lång bok.

## Grafen

`bok/story-graph/` är bokens minne i strukturerad form: personer (med födelse- och dödsdatum), händelser (med datum och vilka som var med), platser, hemligheter (och vem som känner till dem) och relationer. Kontinuitet uppdaterar grafen efter varje kapitel. Ur grafen räknar verktyget ut:

- `bok graph context --kapitel N`: allt en roll behöver veta inför kapitlet, med personernas ålder vid kapitlets datum,
- `bok graph vem-vet`, `var`, `bagar`, `karaktar`: vem vet vad, vem var var, hur bågarna går,
- `bok graph tidslinje`: händelserna i datumordning.

`bok validate` använder grafen för att hitta tidsfel (en person med i en händelse innan hon är född, kapitel som hoppar bakåt i tiden utan att vara en tillbakablick) och åldrar i texten som inte stämmer.

## Platser och miljöer

Med en egen nyckel till Google Maps ([guiden](google-maps.md)) kan Claude svara på hur lång tid det tar att gå, cykla, åka bil eller åka kollektivt mellan bokens platser, och titta på gatubilder för att beskriva hur det ser ut. Beskrivningarna hamnar i `bok/varld/platser/<id>.md` under två rubriker: *Idag* (vad gatubilderna visar, med fotodatum) och *Bokens tid* (det som är belagt eller som du har bestämt om platsen vid bokens tid). `bok graph context` visar båda för kapitlets platser, och hur många år som skiljer bilderna från kapitlets tid. När glappet är stort kan Researchern söka i arkiv efter hur platsen såg ut då.

När du har godkänt ett scenkort frågar Claude om miljön ska tas fram för platser som saknar beskrivning. Inget från Google sparas i boken: inga bilder och inga restider, bara egna formuleringar.

## Moduler

Vissa delar läggs bara till när boken behöver dem: `bok mall tidslinje`, `serie`, `spanning`, `graf-extra`, `rostlabb` (Röstlabbet), och när boken är klar `forlag`, `audiobook`, `marknad`. Claude föreslår dem när det passar.

## Uppdateringar

```sh
uv tool upgrade bok
bok init
```

`bok init` i en befintlig bok skriver om ramverket till den nya versionen och skapar nya bokfiler som saknas. Dina texter rörs inte. Vad som är nytt står i [CHANGELOG.md](../CHANGELOG.md).

## Förslag

Är något krångligt eller fel kan du säga det till Claude. Claude visar exakt vad som skickas, och ingenting ur boken skickas. Förslaget hamnar hos dem som bygger verktyget. `bok forslag` visar dina förslag och vad som har hänt med dem; `bok forslag av` stänger av funktionen.
