# SERIE — CANONICAL EVENTS

> Vad är fast canon över serien? Händelser, datum, karaktärs-handlingar som inte får ändras retroaktivt.

## Princip

> Serie-canon är immutable. Vill man ändra något — skriv ny ADR. Återkommande karaktärer drar med sig historia mellan böckerna.

## Per bok — canon-events

### Bok 1

| Event ID | Beskrivning | Datum | Plats | Synlig i bok | Karaktärer involverade |
|---|---|---|---|---|---|
| evt-<id> | {{...}} | YYYY-MM-DD | loc-<id> | Bok 1 kap-NN | char-<id>, char-<id> |
| ... | ... | ... | ... | ... | ... |

### Bok 2

(samma struktur)

### Bok N

(samma struktur)

## Pre-serie canon

> Händelser INNAN bok 1 som påverkar karaktärerna.

- {{evt-id — datum, beskrivning, vem minns}}
- ...

## Karaktärs-canon

> Per återkommande karaktär — vad är fast?

- **char-<id>:** ålder vid bok 1, yrke, civilstånd, viktiga relationer, viktiga händelser
- ...

## Disciplin

1. Inget i en senare bok får motsäga canon-events.
2. Om något måste ändras: skapa ADR + uppdatera detta dokument.
3. VÄRLDSBYGGARE-rollen verifierar mellan böckerna.

---

**Senast uppdaterad:** {{datum}}
**Status:** Levande (uppdateras per bok)
