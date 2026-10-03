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
| Karaktärer (grind I.1) | `bok/karaktarer/<id>.md` | minst en har `pov: true`; varje POV-karaktär har önskan, rädsla, blind fläck och språklig signatur |
| Plot (grind I.2) | `bok/plot/struktur.md`, `bok/plot/bagar.md` | central fråga, inciting incident, mittpunkt, klimax och varje akts funktion |
| Röst | `bok/stil/rost.md` | ifylld och godkänd i stilverkstaden |
| Kapitelplan | `bok/plot/kapitelplan.md` | åtminstone första akten |
| Hennes ja | rapport med `omfang: forberedelse`, `roll: forfattare`, `utfall: godkand` | efter en sammanfattning av boken på en skärm |

`bok status` ser bara om filerna är ifyllda. Om innehållet håller bedömer `bok-plot-arkitekt` (uppdrag *grind*).

## Skrivloopen per kapitel

1. **Scenkort.** `bok-plot-arkitekt` skriver `bok/plot/kapitel/kapitel-NN.md` från `bok/plot/kapitel/MALL.md`. Grind I.3: varje scen har mål, konflikt och vändpunkt, och det är klart vem som är med och vad var och en vill. Författaren godkänner; skillen sätter `godkand: true` i scenkortet.
2. **Utkast.** `bok-writer` skriver `manuskript/kapitel-NN.md`.
3. **Mekanisk kontroll.** `bok validate manuskript/kapitel-NN.md` och `bok tics manuskript/kapitel-NN.md`. Blockerande namn rättas innan granskning.
4. **Granskning, runda R.** `bok-redaktor` och `bok-sprakgranskare` parallellt. De returnerar rapporter som skillen sparar med `bok rapport spara -`.
5. **Revision.** Har någon `utfall: revidera` reviderar `bok-writer` efter fynden, och sedan följer granskning runda R+1. Granskarna får högst två revisioner: runda 3 är deras sista granskning. Är de inte nöjda efter runda 3, eller säger någon `eskalera`, visar skillen fynden och författaren bestämmer. Skickar författaren tillbaka kapitlet efter det (steg 7) blir det en ny runda.
6. **Kontinuitet.** `bok-kontinuitet` uppdaterar `bok/story-graph/`, skriver `bok/sammanfattningar/kapitel-NN.md` och flaggar brott mot canon. Rollen returnerar en rapport (`utfall: klar` eller `flaggor`) som skillen sparar. Vid `flaggor` visar skillen dem för författaren innan hon läser kapitlet.
7. **Författarens läsning.** Hon godkänner (`roll: forfattare`, `utfall: godkand`, `runda: R`) eller skickar tillbaka med kommentarer (`utfall: tillbaka`). Tillbaka betyder revision och en ny granskningsrunda.

### Aktgränser

När sista kapitlet i en akt (kolumnen Akt i kapitelplanen) är klart läser `bok-forlaggare` akten och svarar `fortsatt` eller `atgarda` (rapport med `omfang: akt` och `akt: N`). Vid `atgarda` åtgärdas fynden och Förläggaren läser igen.

### När alla kapitel är klara

`bok-forlaggare` gör slutläsningen (`omfang: bok`, utfall `A`, `B` eller `C`). `bok-sensitivitet` läser en gång. Därefter tillval: `bok mall forlag`, `bok mall audiobook`, `bok mall marknad`.

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
| `sensitivitet` | `bok` eller `kapitel` | `godkand`, `atgarda` |
| `forfattare` | `forberedelse` eller `kapitel` | `godkand`, `tillbaka` |

`runda` krävs för granskningar och för författarens omdöme om ett kapitel; i övrigt numreras rapporterna automatiskt.

Brödtexten i en granskning har tre avsnitt: `## Blockerande` (citat, problem, konkret förslag), `## Övrigt` och `## Det som fungerar` (sådant Writer inte får ändra vid revision).

## Vad rollerna läser

| Roll | Läser |
|---|---|
| Writer | scenkortet, `bok/stil/rost.md`, `bok/koncept/form.md`, kapitlets karaktärsfiler, `bok graph context`, föregående kapitel i sin helhet, alla sammanfattningar, aktiva regler i `bok/learnings.md`, `bok/canon.md`, `.claude/bok/hantverk/` |
| Redaktör | kapitlet, scenkortet, `bok graph context`, sammanfattningarna, premiss, genre, bågar, canon, kapitlets karaktärsfiler, `.claude/bok/hantverk/` |
| Språkgranskare | kapitlet, `bok/stil/rost.md`, kapitlets karaktärsfiler (språklig signatur), `bok tics`, hantverket |
| Kontinuitet | kapitlet, scenkortet, hela grafen, `bok/canon.md` |
| Förläggare | alla sammanfattningar, premiss, genre, struktur, bågar, kapitelplan, `bok graph bagar`, aktens första och sista kapitel |

Varje roll läser först `bok/roller/<roll>.local.md` om den finns. Den går före allt annat.

## Lärdomar

När samma fynd återkommer i två kapitel föreslår skillen en regel. Efter författarens ja skrivs den under Aktiva regler i `bok/learnings.md` (högst ungefär tjugo). Regler som blivit vana flyttas till Arkiv. Regler för en enskild roll hamnar i `bok/roller/<roll>.local.md`.

## Commits

Skillen committar efter varje godkänt steg med ett kort svenskt meddelande, till exempel `kapitel 3: utkast` eller `stil: rösten godkänd`. Den pushar aldrig utan att författaren ber om det.
