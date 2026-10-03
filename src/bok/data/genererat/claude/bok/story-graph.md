# Story-graph

Grafen är bokens minne: det som faktiskt står i texten. Planen (vad boken ska bli) ligger i `bok/koncept/`, `bok/karaktarer/`, `bok/plot/` och `bok/stil/`. Kontinuitet uppdaterar grafen efter varje kapitel. Alla id:n är korta, gemena och utan mellanslag.

Kapitelnummer är bokens tidsaxel. "Från kapitel 3" betyder att något gäller från och med kapitel 3.

## characters.json

```json
{"characters": [
  {"id": "anna", "namn": "Anna Berg", "alias": ["Annie"],
   "fodd": "1946-03-14", "fakta": {"yrke": "veterinär"}, "forsta_kapitel": 1}
]}
```

`fodd` och `dod` är partiella datum: `ÅÅÅÅ`, `ÅÅÅÅ-MM` eller `ÅÅÅÅ-MM-DD`. Åldrar räknas ut av `bok`; skriv aldrig ålder i `fakta`.

Bara fakta som etablerats i texten. Önskan, rädsla och båge står i `bok/karaktarer/<id>.md`.

## locations.json

```json
{"locations": [{"id": "garden", "namn": "Gården", "fakta": {"läge": "vid sjön"}}]}
```

## events.json

```json
{"events": [
  {"id": "e-012", "kapitel": 4, "vad": "Erik visar testamentet",
   "plats": "garden", "narvarande": ["anna", "erik"], "tid": "en söndag i mars",
   "datum": "1994-09-28"}
]}
```

`datum` är ett partiellt datum; `tid` är fritext för nyanser.

## secrets.json

```json
{"secrets": [
  {"id": "s-arvet", "vad": "Gården är redan såld", "sanning": "Erik sålde den i hemlighet",
   "vet": [{"karaktar": "erik", "fran_kapitel": 1}, {"karaktar": "anna", "fran_kapitel": 9}]}
]}
```

`vet` är vem som känner till hemligheten och från vilket kapitel. Det är så rollerna håller reda på att ingen vet mer än de kan.

## relationships.json

```json
{"relationships": [
  {"fran": "anna", "till": "erik", "typ": "syskon",
   "forandringar": [{"kapitel": 9, "typ": "syskon i öppen konflikt"}]}
]}
```

## threads.json

```json
{"threads": [
  {"id": "t-arvet", "namn": "Arvet", "typ": "intrig", "status": "oppen",
   "steg": [{"kapitel": 1, "vad": "Anna kommer hem"}, {"kapitel": 4, "vad": "Testamentet"}],
   "planteringar": [{"vad": "Nyckeln i ladan", "kapitel": 2, "loses_i": null}]}
]}
```

Bågarnas faktiska rörelse. Planen för bågen står i `bok/plot/bagar.md` med samma `id`. `typ` är `intrig`, `karaktar` eller `tema`. `status` är `oppen` eller `stangd`, skrivet exakt så (utan å och ö). En plantering är något som läsaren ska minnas och som måste lösas (`loses_i` = kapitlet där det sker).

## Datum och åldrar

Scenkortet kan ha `datum` (när kapitlet utspelar sig) och `tillbakablick: true` (kapitlet ligger före det förra i tid). Saknar scenkortet datum används den tidigaste daterade händelsen i kapitlet.

`bok graph context` visar kapitlets datum och varje persons ålder. `bok validate` stoppar händelser där någon är med före sin födelse eller efter sin död, och kapitel som går bakåt i tid utan `tillbakablick: true`. Åldrar i texten som inte stämmer visas som varningar.

## Tillval

`bok mall graf-extra` lägger till `objects.json`, `organizations.json` och `documents.json` med samma form (`{"objects": [{"id", "namn", "fakta"}]}`).

## Frågor

| Kommando | Svar |
|---|---|
| `bok graph context --kapitel N` | underlag för kapitel N enligt scenkortet: personerna, deras relationer och vad de vet, platserna, bågarna och förra kapitlet |
| `bok graph vem-vet <hemlighet> [--kapitel N]` | vilka som känner till en hemlighet (vid slutet av kapitel N) |
| `bok graph bagar [--oppna]` | bågarna med senaste kapitel och olösta planteringar |
| `bok graph karaktar <id>` | fakta, relationer och kapitel där personen förekommer |
| `bok graph var <plats> [--kapitel N]` | händelser på en plats |
| `bok graph tidslinje [--fran ÅR] [--till ÅR]` | daterade händelser i tidsordning med kapitel, plats och åldrar |
