# Process

Så skrivs en bok med `bok`. Skillen `bok` leder arbetet och startar rollerna. Den här filen är regelboken som skillen och rollerna följer.

## Grundprinciper

1. **AI skriver, författaren bestämmer.** Inget passerar en grind utan hennes ja.
2. **Plan i markdown, fakta i grafen.** Planen ligger i `bok/koncept/`, `bok/karaktarer/`, `bok/plot/` och `bok/stil/`. Det som faktiskt står i texten ligger i `bok/story-graph/` (se `.claude/bok/story-graph.md`).
3. **En källa per uppgift.** Skriv aldrig samma sak på två ställen; hänvisa.
4. **Ingen roll läser hela manuset.** Underlaget är sammanfattningar, föregående kapitel och `bok graph context`.
5. **`bok status` avgör var boken står.** Skillen kör den först varje gång.

## Förberedelse

Fritt samtal, i vilken ordning som helst. För att börja skriva kapitel 1 krävs:

| Del | Filer | Klar när |
|---|---|---|
| Koncept | `bok/koncept/premiss.md`, `bok/koncept/genre.md`, `bok/koncept/form.md`, `bok/koncept/teman.md` | inga `{{…}}` kvar |
| Karaktärer (grind I.1) | `bok/karaktarer/<id>.md` | varje fil anger `pov: true` eller `false`; minst en har `pov: true`; varje POV-karaktär är helt ifylld, med önskan, rädsla, blind fläck och språklig signatur |
| Plot (grind I.2) | `bok/plot/struktur.md`, `bok/plot/bagar.md` | central fråga, inciting incident, mittpunkt, klimax och varje akts funktion |
| Röst | `bok/stil/rost.md` | ifylld och godkänd i stilverkstaden |
| Kapitelplan | `bok/plot/kapitelplan.md` | åtminstone första akten |
| Verkliga händelser | blocket `verkliga-handelser` i `bok/canon.md` | bara om blocket har rader: rapport `omfang: forberedelse`, `roll: sensitivitet`, `utfall: godkand` |
| Hennes ja | rapport med `omfang: forberedelse`, `roll: forfattare`, `utfall: godkand` | efter en sammanfattning av boken på en skärm |

`bok status` ser bara om filerna är ifyllda. Om innehållet håller bedömer `bok-plot-arkitekt` (uppdrag *grind*).

## Skrivloopen per kapitel

1. **Scenkort.** `bok-plot-arkitekt` skriver `bok/plot/kapitel/kapitel-NN.md` från `bok/plot/kapitel/MALL.md`. Grind I.3: varje scen har mål, konflikt och vändpunkt, och det är klart vem som är med och vad var och en vill. Författaren godkänner; skillen sätter `godkand: true` i scenkortet.
2. **Utkast.** `bok-writer` skriver `manuskript/kapitel-NN.md`.
3. **Fackgranskning** (bara när scenkortet har `fack`). `bok-researcher` kontrollerar kapitlets fackpåståenden mot källor och returnerar en rapport (`roll: researcher`, `runda` = kommande granskningsrunda). Vid `atgarda` reviderar Writer och fackgranskningen görs om innan granskningen. Efter en revision från granskarna görs en ny fackgranskning före nästa runda.
4. **Mekanisk kontroll.** `bok validate manuskript/kapitel-NN.md` och `bok tics manuskript/kapitel-NN.md`. Blockerande namn rättas innan granskning.
5. **Granskning, runda R.** `bok-redaktor` och `bok-sprakgranskare` parallellt. De returnerar rapporter som skillen sparar med `bok rapport spara -`.
6. **Revision.** Har någon `utfall: revidera` reviderar `bok-writer` efter fynden, och sedan följer granskning runda R+1. Granskarna får högst två revisioner: runda 3 är deras sista granskning. Är de inte nöjda efter runda 3, eller säger någon `eskalera`, visar skillen fynden och författaren bestämmer. Skickar författaren tillbaka kapitlet efter det (steg 8) blir det en ny runda.
7. **Kontinuitet.** `bok-kontinuitet` uppdaterar `bok/story-graph/`, skriver `bok/sammanfattningar/kapitel-NN.md` och flaggar brott mot canon. Skillen ger rollen kapitel N och runda R (den senaste granskningsrundan). Rollen returnerar en rapport (`runda: R`, `utfall: klar` eller `flaggor`) som skillen sparar; sammanfattningen räknas som aktuell först när den rapporten finns. Körs Kontinuitet igen för ett reviderat kapitel ersätter den kapitlets uppgifter i grafen. Vid `flaggor` visar skillen dem för författaren innan hon läser kapitlet.
8. **Författarens läsning.** Hon godkänner (`roll: forfattare`, `utfall: godkand`, `runda: R`) eller skickar tillbaka med kommentarer (`utfall: tillbaka`). Tillbaka betyder revision och en ny granskningsrunda.

### Aktgränser

När sista kapitlet i en akt (kolumnen Akt i kapitelplanen) är klart läser `bok-forlaggare` akten och svarar `fortsatt` eller `atgarda` (rapport med `omfang: akt` och `akt: N`). Vid `atgarda` åtgärdas fynden och Förläggaren läser igen.

### När alla kapitel är klara

`bok-forlaggare` gör slutläsningen (`omfang: bok`, utfall `A`, `B` eller `C`). Vid `B` eller `C` arbetas åtgärderna igenom och Förläggaren läser boken igen. Efter `A` läser `bok-sensitivitet` hela boken (`omfang: bok`); vid `atgarda` åtgärdas fynden och sensitivitetsläsaren läser igen. Därefter är boken klar, och tillvalen återstår: `bok mall forlag`, `bok mall audiobook`, `bok mall marknad`.

## Betyg

En skala för alla roller:

| Betyg | Betyder |
|---|---|
| 10 | Det bästa du läst i genren. Nästan aldrig. |
| 9 | Ovanligt bra. Kräver motivering med citat. |
| 8 | Bra. Godkänt. |
| 7 | Kompetent och publicerbart, men utan lyft. Ett normalt första utkast. |
| 6 | Fungerar men har tydliga brister. |
| 5 eller lägre | Måste skrivas om. |

Godkänt är minst 8 på varje axel. Var ärlig: 7 är inget misslyckande.

| Roll | Axlar |
|---|---|
| Redaktör | `struktur`, `karaktar`, `spanning`, `kontinuitet`, `tema` |
| Språkgranskare | `prosa`, `dialog`, `rost` |

`spanning` betyder dragkraft, lusten att läsa vidare, oavsett genre.

## Rapporter

Alla rapporter börjar med frontmatter. `bok rapport spara` avvisar rapporter med fel och säger exakt vad som är fel.

```
---
omfang: kapitel
kapitel: 3
roll: redaktor
runda: 1
betyg: {struktur: 8, karaktar: 7, spanning: 8, kontinuitet: 9, tema: 8}
utfall: revidera
blockerande: ["Kapitel 2 slutade på torsdag, kapitel 3 börjar på tisdag"]
---
```

| Roll | `omfang` | `utfall` |
|---|---|---|
| `redaktor`, `sprakgranskare` | `kapitel` | `godkand`, `revidera`, `eskalera` |
| `plot-arkitekt` | `forberedelse` eller `kapitel` | `godkand`, `revidera` |
| `kontinuitet` | `kapitel` | `klar`, `flaggor` |
| `forlaggare` | `akt` eller `bok` | `fortsatt`, `atgarda` (akt); `A`, `B`, `C` (bok) |
| `sensitivitet` | `forberedelse`, `bok` eller `kapitel` | `godkand`, `atgarda` |
| `researcher` | `kapitel` | `godkand`, `atgarda` |
| `forfattare` | `forberedelse` eller `kapitel` | `godkand`, `tillbaka` |

`runda` krävs för granskningar och för författarens omdöme om ett kapitel. Kontinuitet anger den granskningsrunda rapporten gäller. I övrigt numreras rapporterna automatiskt. För `researcher` gäller `runda` = kommande granskningsrunda; en ny fackgranskning i samma runda ersätter den förra (`--skriv-over`).

Brödtexten i en granskning har tre avsnitt: `## Blockerande` (citat, problem, konkret förslag), `## Övrigt` och `## Det som fungerar` (sådant Writer inte får ändra vid revision).

## Vad rollerna läser

| Roll | Läser |
|---|---|
| Writer | scenkortet, `bok/stil/rost.md`, `bok/stil/rost-<pov>.md` om den finns (går före `bok/stil/rost.md`), öppna rader i `bok/revisioner.md`, `bok/koncept/form.md`, kapitlets karaktärsfiler, `bok graph context`, föregående kapitel i sin helhet, alla sammanfattningar, aktiva regler i `bok/learnings.md`, `bok/canon.md`, `.claude/bok/hantverk/` |
| Redaktör | kapitlet, scenkortet, `bok graph context`, sammanfattningarna, premiss, genre, teman, bågar, canon, kapitlets karaktärsfiler, `.claude/bok/hantverk/` |
| Språkgranskare | kapitlet, `bok/stil/rost.md`, `bok/stil/rost-<pov>.md`, kapitlets karaktärsfiler (språklig signatur), `bok tics`, hantverket |
| Kontinuitet | kapitlet, scenkortet, hela grafen, `bok/canon.md` |
| Förläggare | alla sammanfattningar, premiss, genre, struktur, bågar, kapitelplan, `bok graph bagar`, aktens första och sista kapitel |

Varje roll läser först `bok/roller/<roll>.local.md` om den finns. Den går före allt annat.

## Revisioner

Respons utifrån (lektör, betaläsare, förlag) blir beslut i `bok/beslut.md` och rader i `bok/revisioner.md`: `- [ ] Kapitel N: …` eller `- [ ] Alla: …`. Writer läser kapitlets öppna rader och raderna för `Alla`. Kontinuitet kryssar av det som är gjort (`- [x]`). `bok status` visar antalet öppna; de blockerar inget.

## Tid

Personer har `fodd` (och `dod`), händelser och scenkort har `datum`. Ingen roll räknar ålder själv: `bok graph context` gör det. `bok validate` stoppar tidsfel i grafen och varnar för åldrar i texten som inte stämmer.

## Lärdomar

När samma fynd återkommer i två kapitel föreslår skillen en regel. Efter författarens ja skrivs den under Aktiva regler i `bok/learnings.md` (högst ungefär tjugo). Regler som blivit vana flyttas till Arkiv. Regler för en enskild roll hamnar i `bok/roller/<roll>.local.md`.

## Commits

Skillen committar efter varje godkänt steg med ett kort svenskt meddelande, till exempel `kapitel 3: utkast` eller `stil: rösten godkänd`. Den pushar aldrig utan att författaren ber om det.
