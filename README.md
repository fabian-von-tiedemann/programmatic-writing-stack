# bok

> Ett skrivharness för romaner i Claude Code. Dra in det i ett tomt repo, och chatta dig fram till en bok.

AI skriver prosan. Du bestämmer: idén, personerna, rösten och varje kapitel. Harnesset håller ordning på resten: karaktärer, hemligheter, bågar, kontinuitet, granskning och vad som är nästa steg.

## Kom igång

```sh
uv tool install git+https://github.com/fabian-von-tiedemann/programmatic-writing-stack
mkdir min-bok && cd min-bok
bok init --titel "Arbetstitel"
```

Du behöver Python 3.11 eller senare; uv hämtar det åt dig om det saknas.

Första gången på en ny dator: följ [docs/installera.md](docs/installera.md) steg för steg (git, uv, bok, din bok och en säkerhetskopia).

Öppna mappen i Claude Code eller Conductor och börja prata: om en idé, en person, en scen eller hur boken ska låta. Har du redan chattat om boken: lägg chattarna i `inkorg/` och be Claude gå igenom dem.

**Med Conductor.** `bok init` gör mappen till ett git-repo (grenen `main`) med en första commit, och tillåter `bok`, `git add` och `git commit` i `.claude/settings.json` (som följer med i repot) så att Claude Code inte frågar om lov vid varje steg. Lägg sedan till bokens mapp som ett repository i Conductor. Varje workspace är en egen gren: slå ihop godkänt arbete tillbaka till main.

Uppgradera ramverket i en befintlig bok:

```sh
uv tool upgrade bok
cd min-bok && bok init
```

Bokens egna filer rörs aldrig. Ramverkets filer i `.claude/` skrivs om; dina egna inställningar i `.claude/settings.json` behålls.

## Hur det fungerar

1. **Förberedelse i fritt samtal.** Koncept, karaktärer, plot, röst och kapitelplan, i vilken ordning som helst. I **stilverkstaden** visar du texter du gillar, Claude provskriver en scen ur din bok i olika röster och du väljer. I **karaktärsverkstaden** prövas en person i korta scener under tryck, gärna med en verklig person som förlaga. Vid vägskäl ger **vägval** flera distinkta alternativ i stället för det första som dyker upp. Vill boken mer än ett hantverksmässigt språk söker **Röstlabbet** (`bok mall rostlabb`) bokens röst och form genom att ni väljer bland varianter, och håller den med mätbara ankare.
2. **Skrivloopen per kapitel.** Scenkort (du säger ja), utkast, granskning av Redaktör och Språkgranskare, högst två revisioner, kontinuitet, och till sist din läsning.
3. **Aktgränser.** Förläggaren läser varje akt och hela boken. När boken fått A läser Sensitivitetsläsaren den.

Med en egen nyckel till Google Maps tar Claude fram restider mellan bokens platser och tittar på gatubilder för att beskriva miljöerna ([guiden](docs/google-maps.md)). Inga bilder sparas i boken.

`bok status` säger alltid var boken står och vad som är nästa steg. Hela genomgången: [docs/hur-det-fungerar.md](docs/hur-det-fungerar.md).

## Vad som hamnar i repot

```
bok.toml          titel, genre, ramverksversion, moduler
CLAUDE.md         ett bok-block + dina egna regler
inkorg/           råmaterial
manuskript/       kapitlen
bok/              planen och minnet: koncept, karaktärer, plot, stil, värld,
                  story-graph, sammanfattningar, rapporter, canon, lärdomar
.claude/          skillen bok, tretton roller och ramverket (genereras)
```

## Kommandon

| Kommando | Gör |
|---|---|
| `bok init` | gör en mapp till ett bokrepo, eller uppgradera ramverket |
| `bok status` | var boken står och nästa steg |
| `bok mall [modul]` | tillval: `spanning`, `serie`, `forlag`, `graf-extra`, `audiobook`, `marknad`, `tidslinje`, `rostlabb` |
| `bok graph …` | frågor mot story-graph: `context`, `vem-vet`, `bagar`, `karaktar`, `var`, `tidslinje` |
| `bok tics` | ord och vändningar som blivit vana |
| `bok rost` | röstens profil, ett kapitels drift mot rösten och AI-genomsnittet, och provstycken till Writer (modulen rostlabb) |
| `bok validate` | förbjudna namn och förlagor, tidslinjen och namn/åldrar att kontrollera |
| `bok fron` | slumpade frön till vägval och Röstlabbet |
| `bok rapport spara` | sparar granskningar och godkännanden |
| `bok annotations` | läsarnoter från Apple Böcker (macOS) |
| `bok karta …` | restider och gatubilder från Google Maps med egen nyckel: `nyckel`, `status`, `restid`, `gatuvy`, `stada` |
| `bok bild` | hämtar en arkivbild tillfälligt, utanför boken, så att Claude kan titta på den |
| `bok forslag` | skicka förslag till dem som bygger verktyget och se vad som hänt med dem |

## Förslag

Märker du något som kunde vara bättre, säg det till Claude i samtalet ("det här var krångligt", "jag önskar att…"). Du får se exakt vad som skickas och säga ja eller nej. Ingen text ur din bok skickas, och du behöver inget konto.

- `bok forslag` visar dina förslag och vad som hänt med dem.
- `bok forslag av` stänger av förslag och all nätkontakt.
- `bok forslag installning` visar om förslag är på eller av.

## Roller

Plot-arkitekt, Writer, Redaktör, Språkgranskare, Kontinuitet och Förläggare i skrivloopen. Sensitivitetsläsaren när boken fått A. Vägval och Idékritiker när du vill ha flera vägar att välja mellan. Researcher, Världsbyggare, Audiobook-regissör och Marknadsförare vid behov. Vill du ändra hur en roll arbetar i din bok: skriv `bok/roller/<roll>.local.md`.

## Utveckling

```sh
uv run pytest
```

Ändringar i de genererade filerna (`src/bok/data/genererat/`) når befintliga böcker först när versionen i `src/bok/__init__.py` höjs.

- [Hur bok fungerar](docs/hur-det-fungerar.md): för den som skriver, eller vill förstå.
- [Utveckla och releasa](docs/utveckla-och-releasa.md): arkitektur, tester, changelog och releaseprocessen. Skillen `release` gör stegen ("gör en release").
- [CHANGELOG](CHANGELOG.md): vad som ändrats i varje version.

Design: `docs/superpowers/specs/2026-10-03-bok-cli-design.md`. Den tidigare versionen ligger i `docs/arkiv/v1.2/`.

## Filosofi

Det mesta i att skriva en bok går att lära ut: en scen behöver en konflikt, personerna ska vilja något, ingen ska förklara det läsaren redan förstått, och ingen får veta något hen inte kan veta. Det är hantverk, och det sköter verktyget: rollerna, granskningen och kontrollerna.

Det som gör en bok till din går inte att lära ut på samma sätt: vad berättelsen lägger märke till, vad den väljer att utelämna och hur den låter. Därför bestämmer du, och därför finns verkstäderna och Röstlabbet. Ju mindre tid du lägger på hantverket, desto mer uppmärksamhet har du kvar till det.

## Licens

[MIT No Attribution](LICENSE) (MIT-0): fritt att använda, ändra och sprida, även kommersiellt, utan krav på att nämna var det kommer ifrån. Det uppskattas ändå. Inga garantier.
