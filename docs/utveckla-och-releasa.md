# Utveckla och releasa bok

För den som bygger `bok`. Hur verktyget fungerar för den som skriver står i [hur-det-fungerar.md](hur-det-fungerar.md).

## Arkitekturen

| Del | Var | Vad |
|---|---|---|
| Python-paketet | `src/bok/` | kommandoradsverktyget. Bara standardbiblioteket, Python 3.11 eller senare. Versionen står i `src/bok/__init__.py` och läses av hatchling. |
| Ramverket | `src/bok/data/genererat/` | skillen, rollerna och `.claude/bok/` (process, story-graph, verktyg, hantverk). Skrivs till böckerna med versionshuvud. |
| Bokens startfiler | `src/bok/data/bok/` | mallar för `bok/`, `manuskript/`, `inkorg/` och bokens `README.md`. Skapas bara om de saknas. |
| CLAUDE.md-blocket | `src/bok/data/claude-block.md`, `claude-md.md` | blocket mellan `bok:start` och `bok:end`. |
| Moduler | `src/bok/data/moduler/` | tillval som `bok mall <namn>` lägger till. |
| Mottagaren | `mottagare/` | Cloudflare Worker (TypeScript, D1) som tar emot förslag och skapar issues i det privata repot `fabian-von-tiedemann/bok-forslag`. |
| Underhållsskills | `.claude/skills/forslag/`, `.claude/skills/release/` | gå igenom förslag; göra en release. |
| Design | `docs/superpowers/specs/`, `docs/superpowers/plans/` | specar och planer per version. |

Moduler i `src/bok/` i korthet: `cli` (kommandona), `init` och `genererat` (skriva ramverket), `status` (var boken står), `graf` och `tid` (grafen, datum, åldrar), `validera` och `tics` (kontroller), `rapport` (rapporter och rundor), `mallar` (moduler), `forslag` (skicka förslag), `annotations` (Apple Böcker), `privat` (privata filer i `~/.config/bok`), `karta` (restider och gatubilder), `google` (nyckeln och anropen till Google Maps; det enda stället som ser nyckeln), `geo` (rutternas geometri), `platser` (platsargument och platsfiler), `bild` (tillfälliga bilder och `bok bild`).

### Viktigt att veta

- **Ramverket når böckerna bara när versionen höjs.** `bok init` skriver om en genererad fil bara om paketets version är nyare än filens huvud. En ändring i `src/bok/data/genererat/` utan versionshöjning når ingen.
- **Bokens filer är bokens.** Ändringar i `src/bok/data/bok/` gäller bara nya böcker. Behöver befintliga böcker något nytt, skapa en ny fil som saknas, eller låt skillen föreslå ändringen.
- **Google Maps-nyckeln lämnar aldrig `google.py`.** URL:er med nyckeln skapas och används bara där, och alla fel blir egna meddelanden utan URL. Testerna når aldrig Google (`tests/conftest.py`). Inget från Google får sparas i boken.
- **Inget arv.** Mallar, roller och exempel ska vara genreneutrala och fria från tidigare böcker; `tests/test_innehall.py` vaktar det.

## Tester

```sh
uv run pytest            # Python
cd mottagare && npm test # mottagaren
```

CI (`.github/workflows/tester.yml`) kör pytest på Ubuntu och macOS, installerar verktyget och skapar en testbok, och testar mottagaren. `tests/test_changelog.py` kräver att CHANGELOG har `[Unreleased]` överst, ett avsnitt för versionen i `__init__.py` och en länk för varje version.

## Changelog

`CHANGELOG.md` följer [Keep a Changelog](https://keepachangelog.com/sv/1.1.0/).

- Skriv under `## [Unreleased]` i samma PR som ändringen.
- Kategorier: **Lagt till**, **Ändrat**, **Fixat**, **Borttaget**, **Säkerhet**.
- Skriv för den som använder verktyget: vad som märks, inte hur koden ändrats.
- Citera aldrig användares förslag. Hänvisa till `bok-forslag#N` om det behövs.

## Versioner

[Semantisk versionshantering](https://semver.org/lang/sv/), räknat från bokens perspektiv:

| Höj | När |
|---|---|
| **patch** (2.2.0 → 2.2.1) | buggfixar och förtydliganden i ramverket som inte ändrar processen |
| **minor** (2.2 → 2.3) | nya kommandon, roller, moduler, fält eller steg i processen; befintliga böcker fungerar som förut efter `bok init` |
| **major** (2 → 3) | befintliga böcker måste ändras för att fungera, t.ex. flyttade filer eller fält som byter betydelse |

## Releaseprocessen

Kort: höj versionen, flytta Unreleased till versionen, gör en PR, merga. Taggen och GitHub-releasen skapas automatiskt. Skillen `release` gör stegen åt dig ("gör en release").

1. **Kontrollera läget.** På en gren från senaste `main`, med allt som ska med mergat eller på grenen. `uv run pytest` är grönt.
2. **Välj version** enligt tabellen ovan.
3. **Höj versionen** i `src/bok/__init__.py`.
4. **Uppdatera CHANGELOG.md:**
   - byt `## [Unreleased]` till `## [X.Y.Z] — ÅÅÅÅ-MM-DD` och lägg ett nytt tomt `## [Unreleased]` ovanför,
   - längst ned: ändra `[Unreleased]`-länken till `compare/vX.Y.Z...HEAD` och lägg till `[X.Y.Z]: …/compare/vFÖRRA...vX.Y.Z`.
5. **Kontrollera:** `uv run pytest` och `python scripts/changelog.py X.Y.Z` (skriver ut release-texten).
6. **Commit och PR:** `release: X.Y.Z`. Vänta på grön CI och merga.
7. **Automatiskt:** `.github/workflows/release.yml` körs på `main`. Saknas taggen `vX.Y.Z` skapar den taggen på merge-commiten och en GitHub-release med avsnittet ur CHANGELOG. Finns taggen händer inget, så vanliga merges utan versionshöjning gör ingen release.
8. **Kontrollera releasen:** `gh release view vX.Y.Z`.
9. **Förslag som kom med:** märk dem `infort:X.Y.Z` i `bok-forslag` och svara användarna (skillen `forslag` beskriver hur). Det är så `bok forslag` visar att ett förslag är infört.
10. **Mottagaren**, bara om `mottagare/` ändrats: `cd mottagare && npx wrangler deploy`. Den deployas på Fabians privata Cloudflare-konto (`account_id` i `wrangler.jsonc`), aldrig Digitalists. Kör `npx wrangler whoami` först. Nya migrationer körs med `npx wrangler d1 migrations apply bok-forslag --remote`.

### Användarnas uppdatering

```sh
uv tool upgrade bok
bok init
```

Den som vill ha en viss version installerar taggen:

```sh
uv tool install --force git+https://github.com/fabian-von-tiedemann/programmatic-writing-stack@vX.Y.Z
```

### Om något går fel

- **Releasen skapades inte:** titta på körningen under Actions → Release. Vanligast är att CHANGELOG saknar avsnittet; då stoppas redan PR:en av testerna. Kör om jobbet efter rättningen.
- **Fel i en släppt version:** släpp en ny patchversion. Flytta eller ta inte bort taggar som någon kan ha installerat.
