# Genomkörning: Från tomt repo till godkänt kapitel 1

Protokoll för att testa bok-CLI från initialisering till slutlösning av kapitel 1.

## Förberedelse

Installera verktyget och skapa en test-instans:

```bash
uv tool install --force .
mkdir -p ~/bok-test && cd ~/bok-test && bok init --titel "Provbok"
```

Lägg ett riktigt chattmaterial om en bokidé i `inkorg/` (exporterad chatt eller anteckningar från Claude, eller anteckningar du gjorde själv). Inkludera även en eller två textexempel med en önskad ton i samma katalog.

Öppna `~/bok-test` i Claude Code och följ stegen nedan i ordning. Anteckna för varje punkt vad som fungerade, vilka problem du stötte på, och hur du åtgärdade dem.

## Genomkörning

| Punkt | Vad som ska hända | Fungerade? | Problem | Åtgärd |
|-------|-------------------|------------|---------|--------|
| 1 | Säg "Hej, jag vill skriva en bok." Skillen ska köra `bok status`, berätta vad som finns och föreslå inkorgen. | | | |
| 2 | Säg "Gå igenom inkorgen." Utkast till koncept, karaktärer och plot; en sammanfattning; luckor en i taget, med förslag. | | | |
| 3 | Säg "Jag vill jobba med tonen." Stilverkstaden: exempel, analys, två eller tre provtexter i `bok/stil/prov/`, val, `bok/stil/rost.md`. | | | |
| 4 | Säg "Var är vi?" Status i klartext utan jargong. | | | |
| 5 | Fyll det som saknas tills förberedelsen är klar. Plot-arkitektens grind, sammanfattningen på en skärm, ja. | | | |
| 6 | Säg "Nästa steg" upprepat: scenkort (ja), utkast, granskning (två rapporter i `bok/rapporter/kapitel-01/`), eventuell revision, kontinuitet (grafen och `bok/sammanfattningar/kapitel-01.md` uppdaterade), läsning, godkänt. | | | |
| 7 | Efter godkänt kapitel 1: `bok status` ska nu föreslå scenkort för kapitel 2. | | | |
| 8 | `git log` ska visa en commit per godkänt steg. | | | |

## Efteråt

Efter genomkörningen och när du dokumenterat eventuella problem:

1. Åtgärda alla problem som hittades i skillarnas eller agenternas genererade text. Redigera i `src/bok/data/genererat/…`.

2. Höj versionen till `2.0.1` i `src/bok/__init__.py`. Detta gör att `bok init` uppgraderar befintliga böcker när de nästa gång initias.

3. Kör testerna för att verifiera att ändringar inte bryter något:
   ```bash
   uv run pytest -q
   ```

4. Åtgärda eventuella testfel och repetera från steg 3 tills alla test passar.
