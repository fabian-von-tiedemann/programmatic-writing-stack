# manuskript/

Bokens kapitel bor här.

## Filer

- `prolog.md` (om relevant)
- `kapitel-01.md`, `kapitel-02.md`, ...
- `epilog.md` (om relevant)
- Mellan-kapitel: `interludium-NN-MM.md` om bokens form har dokument-mellanlägg

## Om layered markup är införd

För kapitel som använder layered markup (ADR 0001):
- `kapitel-NN.draft.md` — källan med `@[display|node-id]`-markup
- `kapitel-NN.md` — renderad output (bytewise identisk efter ren render)

Pipeline:
```bash
scripts/render-manuscript.py manuskript/kapitel-NN.draft.md
scripts/validate-manuscript.py .cache/kapitel-NN.refs.json
```

## Format (per kapitel)

- **Längd:** {{KAPITEL_LANGD}} ord (förslag thriller: 3000-3500)
- **Öppning:** om realtidsformat — `DAG DATUM HH:MM \n PLATS` i VERSALER, två rader (se `exempel-kapitel-01.md`)
- **Slut:** cliffhanger som omformar (kognitiv förskjutning), inte hot-cliff

## Disciplin

1. Inget kapitel sparas här utan att FAS 2 (writer) → FAS 3 (redaktör → prosa-städ → dialog-coach → NAGELFAREN → fix) → FAS 4 (förläggare → sensitivity) är gått.
2. Inget kapitel publiceras under 9+ på alla axlar.
3. Grafen ska vara uppdaterad efter varje kapitel (FAS 6).
