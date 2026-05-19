# PROCESS — Förbättringsloopen per kapitel

Stående arbetsflöde för bokprojektet. Får ALDRIG hoppas över. Är skälet boken når 9+ på alla axlar.

Ramverket har **13 roller** (5 grund + 8 utökning). FAS-flödet är FAS 0 → 9 plus löpande GRAF-VAKT och separat VÄRLDSBYGGARE.

---

## FAS 0 — Plot + Research (FÖRE skrivande)

- [ ] STEG 0a: Dispatcha PLOT-ARKITEKT (`.context/roles/plot-arkitekt.md`)
  - Designar scen-skelett: öppningsbeat, mid-point, cliffhanger-vektor, kognitiv förskjutning
  - Verifierar trådar via `scripts/graph-query.py thread <id>`
  - Output: `.context/plot-outlines/kapitel-NN-outline.md`
  - Plot-arkitekten **flaggar** plot-konflikter; författaren beslutar
- [ ] STEG 0b: Dispatcha RESEARCHER (`.context/roles/researcher.md`) för uppdrag plot-arkitekten flaggar
  - Verifierad fakta + källa per uppslag
  - Skiljer canon-research (in i grafen) från writer-bakgrund (textur, stannar i dossier)
  - Output: `.context/research-dossier/<amne>.md`
  - Researcher kan också triggas **reaktivt** av redaktör/NAGELFAREN/förläggare när fakta flaggas

**STOPP** om plot-outline saknas eller research-flagor inte är besvarade.

---

## FAS 1 — Förberedelse innan writer dispatchas

- [ ] STEG 1: Grafen är COMPLETE från förra kapitlet (events, characters, locations, documents, secrets, objects)
- [ ] STEG 2: `.context/learnings.md` innehåller ALL feedback från redaktör + förläggare + läsare för förra kapitlet
- [ ] STEG 3: `.context/editor-brief.md` (om finns) uppdaterad med förläggarens senaste helhetskontroller
- [ ] STEG 4: `.context/story-graph/knowledge-matrix.md` konsulterad för POV-vetskap

**STOPP — gå INTE vidare till FAS 2 om STEG 1-4 inte är ✓.**

---

## FAS 2 — Skrivande

- [ ] STEG 5: Dispatcha WRITER-subagent
  - Läs: `CLAUDE.md` + `.context/roles/writer.md` + `.context/process.md` + `.context/canon.md` + `.context/learnings.md` + **`.context/story-graph/character-deepening/char-<POV-id>.md` + relevanta bi-person-fördjupningar** + relevanta grafnoder + alla tidigare kapitel
  - Skriv utkast till `manuskript/kapitel-NN.draft.md` (om layered markup införd) eller `manuskript/kapitel-NN.md`

---

## FAS 3 — Redaktörsloop

- [ ] STEG 6: Dispatcha REDAKTÖR-subagent (`.context/roles/redaktor.md`)
  - Rapport: `.context/redaktor-rapporter/<kapitel>-granskning-v<N>.md`
- [ ] STEG 7: Applicera fixar (själv eller via fix-agent)
- [ ] STEG 7a: **PROSA-STÄD-AGENT (BLOCKERANDE)** (`.context/roles/prosa-stad.md`)
  - Mening-för-mening, naiv-läsare-perspektiv
  - Output: `.context/prosa-stad-rapporter/<kapitel>-stadning-v<N>.md`
  - **STEG 7a får INTE hoppas över. Inget kapitel godkänns utan denna rapport.**
- [ ] STEG 7b: Applicera prosa-städ-fixar
- [ ] STEG 7b1: **DIALOG-COACH (POV-veto)** (`.context/roles/dialog-coach.md`)
  - Lyssnar BARA på dialog + POV-tankespråk
  - Verifierar mot character-deepening: talspråk, rytm, signum-quirks, förbjudna konstruktioner
  - Output: `.context/dialog-coach-rapporter/kapitel-NN-roster-vN.md`
  - **Veto på POV-axeln:** ≥3 läckage-flaggor eller ≥2 förbjudna-konstruktion-träffar → blockerar 9+
- [ ] STEG 7b2: Applicera dialog-coach-fixar
- [ ] STEG 7c: **NAGELFAREN (BLOCKERANDE för 9+)** (`.context/roles/nagelfaren.md`)
  - Adversarial meta-granskning av redaktör-rapporten
  - Minst 5 missar krävs i rapport — om inte hittade: gå tillbaka och titta
  - Output: `.context/nagelfaren-rapporter/<kapitel>-meta-v<N>.md`
  - Veto-rätt: om 5+ missar → redaktör-rapporten FÖRKASTAS, redaktör gör om
- [ ] STEG 8: Re-dispatcha redaktör tills 9+ på ALLA axlar (med kalibrerade betyg — se redaktor.md)

---

## FAS 4 — Förläggargranskning

- [ ] STEG 9: Dispatcha FÖRLÄGGAR-subagent (`.context/roles/forlaggare.md`)
  - Läs ALLA kapitel hittills + grafen + alla redaktör- och NAGELFAREN-rapporter
- [ ] STEG 10: Applicera förläggar-fixar
- [ ] STEG 11: Om förläggaren rekommenderar B/C → repetera fix + granskning tills A
- [ ] STEG 11a: **SENSITIVITY-LÄSARE (publikation-veto)** (`.context/roles/sensitivity-lasare.md`)
  - Granskar hela boken: representation, könade beskrivningar, klassförakt, otidsenligt språk, makt-asymmetrier, kulturell autenticitet, geografisk/lokal autenticitet
  - Output: `.context/sensitivity-rapporter/efter-<bok>-<datum>.md`
  - **Veto på publikation:** allvarlig stereotypisering / otidsenligt språk / glamourisering av övergrepp
- [ ] STEG 11b: Applicera ev. sensitivity-fixar (författaren beslutar **hur** — strykning, omskrivning, ny scen, kompletterande karaktär)

---

## FAS 5 — Arbeta in lärdomar (OBLIGATORISKT)

- [ ] STEG 12: Skriv in ALLA nya fel/tics i `.context/learnings.md` (datum, plats, fel, lärdom, regel)
- [ ] STEG 13: Uppdatera `.context/roles/redaktor.md` sektion 1c (helhetskontroller) om förläggaren hittade systemfel
- [ ] STEG 14: Om läsaren har gett feedback (via `scripts/books-annotations.sh`): skriv in den också

---

## FAS 6 — Graf-uppdatering (OBLIGATORISKT INNAN NÄSTA KAPITEL)

> **FAS 6 är där författaren formellt verifierar graf-vaktens arbete. GRAF-VAKTEN själv körs LÖPANDE** — efter varje writer/redaktör/prosa-städ/dialog-coach/NAGELFAREN/fix-pass där text eller graf har ändrats. Se `.context/roles/graf-vakt.md`.

Graf-vakten levererar två produkter per pass:
1. **Säker auto-fix** (saknad stub-nod, kebab-case-fel, strukturerad known_to)
2. **Flagg-rapport** för dubbletter, broken references, schema-drift — författaren beslutar

Rapport: `.context/graf-vakt-rapporter/efter-<händelse>-<datum>.md`

- [ ] STEG 15: Författaren verifierar att graf-vaktens senaste rapport för detta kapitel är applicerad. Vid behov dispatcha graf-vakt manuellt för slut-verifiering:
  - `events.json` — nya händelser i story-tid
  - `characters.json` — nya bipersoner, fördjupningar
  - `locations.json` — nya platser (verifierad geografi)
  - `documents.json` — nya dokument
  - `objects.json` — nya objekt (bilar, telefoner, kläder med funktion)
  - `secrets.json` — nya hemligheter, vem-vet-uppdateringar
  - `knowledge-matrix.md` — vetskaps-förändringar

**STOPP — gå INTE till FAS 1 för nästa kapitel om STEG 12-15 inte är ✓.**

---

## FAS 7 — Nästa kapitel

- [ ] STEG 16: Mark task complete, börja FAS 0 för nästa kapitel

---

## FAS 8 — Audiobook (efter förläggar-A)

- [ ] STEG 17: Dispatcha AUDIOBOOK-DIREKTÖR (`.context/roles/audiobook-direktor.md`)
  - Läser texten **genom örat**, inte ögat
  - Granskar pause-markeringar från director-modell + flaggar paragrafer
  - Cross-check mot character-deepening för voiceProfiles
  - **Ingen text-veto** — flaggar audio-tics som FÖRFATTAR-BESLUT
- [ ] STEG 18: Producera uttalslexikon + karaktärsröster
  - `scripts/audiobook/pronunciations.json` (bygg vidare, ersätt inte)
  - `scripts/audiobook/character-voices.json` (voiceProfiles per POV + central biperson)
  - `.context/audiobook/karaktarsroster.md` — fördjupad per POV
  - `.context/audiobook/regissor-anvisningar.md` — övergripande regi
  - `.context/audiobook/direktor-rapport-<datum>.md` — täckning + flaggor

---

## FAS 9 — Marknadsföring (efter audiobook eller parallellt)

- [ ] STEG 19: Dispatcha MARKNADSFÖRARE (`.context/roles/marknadsforare.md`)
  - Läser boken **som någon som ska sälja den**
  - **Ingen veto** — bara förslag, författaren + förlaget beslutar
- [ ] STEG 20: Producera pitch-pack
  - `.context/marknadsforing/pitch-pack-<bok>.md`
  - Pitch-mening (5-10 versioner), jämförelsetitlar, målgrupp, baksidestext (2 versioner), författarpresentation (lång + kort), pressmaterial (push + release + talking points), cover-direction, genre-positionering

---

## VÄRLDSBYGGARE — körs separat (tre tidpunkter)

`.context/roles/varldsbyggare.md`

Världsbyggaren är **enda rollen** som tänker bortom enskild bok. Körs:

- **Före bok 1** (fundament-pass) — designar grund-världen, skapar `.context/world-bible.md` v1
- **Efter bok 1** (extraktion-pass) — extraherar världs-bibel + ev. series-bible från färdig bok
- **Före bok N+1** (continuity-pass) — `.context/cross-bok-continuity-<bok-N>.md` med KANONISERAT / TOLKNINGSBART / MEDVETET ÖPPET

**Ingen veto** — rådgivande. Författaren beslutar vad som är serie-canon vs bok-specifikt.

---

## Hårda regler om processen

1. **Aldrig hoppa över ett steg.** Om någon vill att jag ska "köra snabbt" — säg nej.
2. **Aldrig dispatcha writer för kap N+1 om FAS 5+6 för kap N inte är klara.** Writer-agenten läser learnings + graf — om de är gamla skriver hen blint.
3. **Förläggaren är vetoröst.** Inget kap N+1 förrän förläggaren har rekommenderat A.
4. **NAGELFAREN är vetoröst på redaktören.** Inget redaktör-9+ godtas utan NAGELFAREN-godkännande.
5. **DIALOG-COACH är vetoröst på POV-axeln.** Inget 9+ på POV utan godkännande där.
6. **SENSITIVITY-LÄSARE är vetoröst på publikation.** Allvarliga representations-fel måste adresseras innan tryck.
7. **PROSA-STÄD är BLOCKERANDE.** Inget kapitel godkänns utan rapport.
8. **PLOT-ARKITEKT körs FÖRE writer.** Förebyggande > spackling.
9. **GRAF-VAKT körs LÖPANDE.** Efter varje pass som ändrar text eller graf.
10. **Tasks-tracking** ska visa varje fas, inte bara "Kap N — skriv".
11. **Grafen är canon.** Alla roller läser grafen som sanningsreferens.
12. **PROSA-PRINCIPEN (icke-förhandlingsbar):** ingen syftningstvivel. Varje mening ska vara lätt att förstå vid första läsning. Klarhet före allt.

---

## Grafens roll

Kunskapsgrafen är inte ett bilag-dokument — det är **bokens canon**. Alla roller använder den:

- **WRITER** läser grafen INNAN hen skriver. Konsekvent med karaktärsprofiler, etablerade hemligheter, knowledge-matrix.
- **REDAKTÖR** korsreferar VARJE kapitel mot grafen.
- **FÖRLÄGGARE** kollar HELA boken mot grafen. Repetitioner, kunskaps-progression över alla kapitel, timeline.

Om grafen är inaktuell: flagga i rapporten under separat sektion "GRAF MÅSTE UPPDATERAS". Då dispatchar huvudsessionen en graf-uppdaterar-agent FÖRE nästa kapitel.

---

## Mekaniska hjälpmedel (när tillämpligt)

Före redaktör-passet:
- `scripts/grep-tics.sh manuskript/kapitel-NN.md` — fångar frekvens-tics

Layered markup (om kapitlet är taggat `.draft.md`):
- `scripts/render-manuscript.py manuskript/kapitel-NN.draft.md` — producerar ren `.md` + refs.json
- `scripts/validate-manuscript.py .cache/kapitel-NN.refs.json` — etablering + frekvens + attribut-strider
- Validator-rapport blir input till redaktör, prosa-städ och NAGELFAREN

Story-graph query:
- `scripts/graph-query.py thread <id>` — verifiera tråden över alla kapitel
- `scripts/graph-query.py character <id>` — vetskap + relationer + scener

Se `.context/tools.md` för detaljer.
