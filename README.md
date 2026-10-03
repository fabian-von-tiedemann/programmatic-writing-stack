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

Öppna mappen i Claude Code eller Conductor och börja prata: om en idé, en person, en scen eller hur boken ska låta. Har du redan chattat om boken: lägg chattarna i `inkorg/` och be Claude gå igenom dem.

**Med Conductor.** `bok init` gör mappen till ett git-repo (grenen `main`) med en första commit, och tillåter `bok`, `git add` och `git commit` i `.claude/settings.json` (som följer med i repot) så att Claude Code inte frågar om lov vid varje steg. Lägg sedan till bokens mapp som ett repository i Conductor. Varje workspace är en egen gren: slå ihop godkänt arbete tillbaka till main.

Uppgradera ramverket i en befintlig bok:

```sh
uv tool upgrade bok
cd min-bok && bok init
```

Bokens egna filer rörs aldrig. Ramverkets filer i `.claude/` skrivs om; dina egna inställningar i `.claude/settings.json` behålls.

## Hur det fungerar

1. **Förberedelse i fritt samtal.** Koncept, karaktärer, plot, röst och kapitelplan, i vilken ordning som helst. I **stilverkstaden** visar du texter du gillar, Claude provskriver en scen ur din bok i olika röster och du väljer.
2. **Skrivloopen per kapitel.** Scenkort (du säger ja), utkast, granskning av Redaktör och Språkgranskare, högst två revisioner, kontinuitet, och till sist din läsning.
3. **Aktgränser.** Förläggaren läser varje akt och hela boken. När boken fått A läser Sensitivitetsläsaren den.

`bok status` säger alltid var boken står och vad som är nästa steg.

## Vad som hamnar i repot

```
bok.toml          titel, genre, ramverksversion, moduler
CLAUDE.md         ett bok-block + dina egna regler
inkorg/           råmaterial
manuskript/       kapitlen
bok/              planen och minnet: koncept, karaktärer, plot, stil, värld,
                  story-graph, sammanfattningar, rapporter, canon, lärdomar
.claude/          skillen bok, elva roller och ramverket (genereras)
```

## Kommandon

| Kommando | Gör |
|---|---|
| `bok init` | gör en mapp till ett bokrepo, eller uppgradera ramverket |
| `bok status` | var boken står och nästa steg |
| `bok mall [modul]` | tillval: `spanning`, `serie`, `forlag`, `graf-extra`, `audiobook`, `marknad` |
| `bok graph …` | frågor mot story-graph: `context`, `vem-vet`, `bagar`, `karaktar`, `var` |
| `bok tics` | ord och vändningar som blivit vana |
| `bok validate` | förbjudna namn och namn som saknas i grafen |
| `bok rapport spara` | sparar granskningar och godkännanden |
| `bok annotations` | läsarnoter från Apple Böcker (macOS) |

## Roller

Plot-arkitekt, Writer, Redaktör, Språkgranskare, Kontinuitet och Förläggare i skrivloopen. Sensitivitetsläsaren när boken fått A. Researcher, Världsbyggare, Audiobook-regissör och Marknadsförare vid behov. Vill du ändra hur en roll arbetar i din bok: skriv `bok/roller/<roll>.local.md`.

## Utveckling

```sh
uv run pytest
```

Ändringar i de genererade filerna (`src/bok/data/genererat/`) når befintliga böcker först när versionen i `src/bok/__init__.py` höjs.

Design: `docs/superpowers/specs/2026-10-03-bok-cli-design.md`. Den tidigare versionen ligger i `docs/arkiv/v1.2/`.

## Filosofi

> Bra prosa är inte tekniker. Bra prosa är uppmärksamhet. Tekniker är hantverkets nedre nittio procent; de frigör uppmärksamheten till det som inte kan läras.

## Licens

Fritt att använda, anpassa och distribuera. Ingen attribuering krävs men uppskattas.
