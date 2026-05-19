# TOOLS — Scripts + pipeline-användning

Mekaniska hjälpmedel som kompletterar AI-rollerna. Kör dessa i förbättringsloopen där de gör störst nytta.

---

## 1. Apple Books-noter — `scripts/books-annotations.sh`

Hämtar läsarens highlights + noter från Apple Books (mobilen + desktop synkar via iCloud).

```bash
scripts/books-annotations.sh                              # markdown till stdout
scripts/books-annotations.sh --since 2026-05-18           # bara nya sen datum
scripts/books-annotations.sh --out .context/feedback/lasning-<datum>.md
scripts/books-annotations.sh --json                       # för pipeline
scripts/books-annotations.sh --title "Annan bok"          # annan bok
```

Hanterar WAL/SHM (kritiskt — utan WAL saknas senaste synkade noterna). Datum är Core Data-epok (2001-01-01) → läsbar lokal tid.

**När kör jag den:** Efter varje läsesession användaren genomför. Mata in i `.context/learnings.md` om något nytt mönster.

---

## 2. Tics-katalog + grep — `scripts/grep-tics.sh`

Mekaniskt första-pass över manuskript. Fångar frekvens-fel (samma doft x4, samma bilmodell x5, samma gest x101) som AI-redaktören missar.

```bash
scripts/grep-tics.sh                                       # alla kapitel
scripts/grep-tics.sh manuskript/kapitel-05.md              # ett kapitel
scripts/grep-tics.sh manuskript/kapitel-0[3-9].md          # range
```

Kategorier definieras i `.context/tics-katalog.md`. Output: färgkodad rapport med radnr + `[ÖVER TAK]`-flagga.

**När kör jag den:**
- Före redaktör-passet (mekanisk första-pass)
- Efter writer-utkast
- Efter mekanisk städning (för verifiering)

---

## 3. Layered markup-pipeline (ADR 0001)

Inline `@[display|node-id]`-markup i `.draft.md`-filer + render/validate-pipeline. Mekanisk sanningsspegel mot story-graph.

### Workflow

```bash
# 1. Tag:a befintligt kapitel (semi-auto)
scripts/tag-manuscript.py manuskript/kapitel-NN.md
# → manuskript/kapitel-NN.draft.md
# → .cache/kapitel-NN.tag-suggestions.md

# 2. Render (.draft.md → ren .md + refs.json)
scripts/render-manuscript.py manuskript/kapitel-NN.draft.md
# → manuskript/kapitel-NN.md (BYTEWISE identisk efter ren render)
# → .cache/kapitel-NN.refs.json

# 3. Validera
scripts/validate-manuscript.py .cache/kapitel-NN.refs.json
# → .context/validator-rapporter/kapitel-NN-validation.md
```

### Validator-regler

| ID | Regel | Severity |
|---|---|---|
| R1 | Saknad nod (node_id finns inte i graf) | ERROR |
| R2 | Attribut-claim strider mot graf | WARNING |
| R3 | Bestämd form vid first-ref utan introduktion | WARNING |
| R4 | Frekvens över threshold (per-typ thresholds) | WARNING |
| R5 | Verklig person (blacklist-match) | ERROR |

### Per-typ frekvens-thresholds (R4)

- `char-` POV: 50 per kapitel (auto-detection)
- `char-` biroll: 15 per kapitel
- `loc-`: 20 per kapitel
- `obj-`: 10 per kapitel
- `evt-`: 5 per kapitel
- `doc-`: 5 per kapitel

Override via CLI: `--freq-threshold-POV N`, etc.

### Tag-confidence

| Confidence | Beskrivning | Auto-applied? |
|---|---|---|
| HIGH | Unik term → unik node, egennamn | Ja |
| MEDIUM | Match i graf, ev. flera kandidater | Ja (alfabetiskt först) |
| LOW | Ambiguös term, generisk geo | Ja (skippas) |
| AMBIGUOUS | Generisk term som plats-stadnamn | Nej — manuell genomgång |

**När kör jag pipelinen:**
- För nya kapitel: writer skriver i `.draft.md`, pipeline renderar + validerar före redaktör
- För gamla kapitel: retroaktiv taggning via `tag-manuscript.py`, sedan pipeline
- Validator-rapport ges till redaktör, prosa-städ, NAGELFAREN som mekaniskt bevis

### Bygga upp grafen för markup-stöd

Lägg till geo-noder + org-noder löpande när texten kräver. Se `.context/story-graph/locations.json` + `.context/story-graph/organizations.json`.

---

## 4. Story-graph query — `scripts/graph-query.py` (ADR 0002)

Nivå 2 query-lager mot kunskapsgrafen. Hjälper plot-arkitekt, redaktör, NAGELFAREN, förläggare att fråga grafen utan att läsa varje JSON-fil manuellt.

```bash
scripts/graph-query.py character <id>     # vetskap + relationer + scener
scripts/graph-query.py thread <id>        # trådens båge över kapitel
scripts/graph-query.py event <id>         # händelse + deltagare + plats + tid
scripts/graph-query.py secret <id>        # vem vet vad när
scripts/graph-query.py timeline           # alla events kronologiskt
```

---

## 5. Övriga scripts

- `scripts/audiobook/` — TTS-pipeline för ljudbok. Aktiveras i FAS 8.

---

## Filgrupper i .context/

### Auto-genererade rapporter
- `.context/redaktor-rapporter/<kap>-granskning-v<N>.md`
- `.context/prosa-stad-rapporter/<kap>-stadning-v<N>.md`
- `.context/dialog-coach-rapporter/<kap>-roster-v<N>.md`
- `.context/nagelfaren-rapporter/<kap>-meta-v<N>.md`
- `.context/forlaggar-rapporter/efter-kapitel-NN.md`
- `.context/sensitivity-rapporter/efter-<bok>-<datum>.md`
- `.context/graf-vakt-rapporter/efter-<händelse>-<datum>.md`
- `.context/validator-rapporter/kapitel-NN-validation.md`

### Permanent referens (uppdateras)
- `.context/learnings.md` — alla lärdomar
- `.context/canon.md` — fakta-fällor + blacklist
- `.context/tics-katalog.md` — frekvens-tak per ord
- `.context/roles/` — alla rolldefinitioner
- `.context/hantverk/` — Del III-tekniker
- `.context/process.md` — FAS-flödet
- `.context/story-graph/` — bokens canon

### Cache (gitignored)
- `.cache/kapitel-NN.refs.json`
- `.cache/kapitel-NN.tag-suggestions.md`
- `.cache/kapitel-NN.original.md` (säkerhetskopior före render)
