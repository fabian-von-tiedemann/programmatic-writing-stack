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
| `bok/` | planen och minnet: idén, personerna, handlingen, rösten, världen, besluten, sammanfattningar per kapitel, grafen och granskningarna | boken |
| `manuskript/` | kapitlen | boken |
| `bok.toml` | titel och inställningar | boken |
| `.claude/skills/bok/`, `.claude/agents/bok-*.md`, `.claude/bok/` | ramverket: skillen, rollerna, processen, hantverksreglerna | verktyget |
| `CLAUDE.md` | ett block mellan `<!-- bok:start -->` och `<!-- bok:end -->` som pekar Claude till skillen | verktyget äger blocket, resten är ditt |

Ramverkets filer har ett versionshuvud och skrivs om när du uppgraderar. Bokens filer skapas bara om de saknas och rörs aldrig efter det. En ramverksfil som någon har ändrat för hand (huvudet borttaget) lämnas också orörd. Egna tillägg till en roll skrivs i `bok/roller/<roll>.local.md`.

## Från idé till färdig bok

### Förberedelse

Fritt samtal i vilken ordning som helst: idén, personerna, handlingen, rösten. I **stilverkstaden** visar du texter du gillar och Claude provskriver en scen ur din bok i olika röster tills rösten sitter. En POV-person kan få en egen röst ovanpå bokens.

Innan första kapitlet skrivs ska koncept, karaktärer, plot, röst och kapitelplanen för första akten vara ifyllda. Bygger boken på verkliga händelser läses planen först av sensitivitetsläsaren. Sist får du en sammanfattning av boken på en skärm och säger ja.

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

## Rollerna

| Roll | Gör |
|---|---|
| Plot-arkitekt | struktur, bågar, scenkort; bedömer om planen håller |
| Writer | skriver och reviderar prosan |
| Redaktör | granskar struktur, karaktär, spänning, kontinuitet och tema |
| Språkgranskare | granskar prosa, dialog och röst |
| Kontinuitet | håller grafen och sammanfattningarna; flaggar motsägelser |
| Researcher | research och fackgranskning mot källor |
| Världsbyggare | världens regler, platser och historia |
| Sensitivitet | verkliga personer och händelser, representation, respekt |
| Förläggare | läser akter och hela boken som en förlagsläsare |
| Audiobook, Marknad | tillval när boken är klar |

Rollerna läser sammanfattningar och utdrag ur grafen i stället för hela manuset, så att de håller sig skarpa även i en lång bok.

## Grafen

`bok/story-graph/` är bokens minne i strukturerad form: personer (med födelse- och dödsdatum), händelser (med datum och vilka som var med), platser, hemligheter (och vem som känner till dem) och relationer. Kontinuitet uppdaterar grafen efter varje kapitel. Ur grafen räknar verktyget ut:

- `bok graph context --kapitel N`: allt en roll behöver veta inför kapitlet, med personernas ålder vid kapitlets datum,
- `bok graph vem-vet`, `var`, `bagar`, `karaktar`: vem vet vad, vem var var, hur bågarna går,
- `bok graph tidslinje`: händelserna i datumordning.

`bok validate` använder grafen för att hitta tidsfel (en person med i en händelse innan hon är född, kapitel som hoppar bakåt i tiden utan att vara en tillbakablick) och åldrar i texten som inte stämmer.

## Moduler

Vissa delar läggs bara till när boken behöver dem: `bok mall tidslinje`, `serie`, `spanning`, `graf-extra`, och när boken är klar `forlag`, `audiobook`, `marknad`. Claude föreslår dem när det passar.

## Uppdateringar

```sh
uv tool upgrade bok
bok init
```

`bok init` i en befintlig bok skriver om ramverket till den nya versionen och skapar nya bokfiler som saknas. Dina texter rörs inte. Vad som är nytt står i [CHANGELOG.md](../CHANGELOG.md).

## Förslag

Är något krångligt eller fel kan du säga det till Claude. Claude visar exakt vad som skickas, och ingenting ur boken skickas. Förslaget hamnar hos dem som bygger verktyget. `bok forslag` visar dina förslag och vad som har hänt med dem; `bok forslag av` stänger av funktionen.
