# Platser

En fil per plats som boken skildrar: `bok/varld/platser/<id>.md`, med samma id som i `bok/story-graph/locations.json`. En rutt utan egen plats får namnet `<från>-<till>.md`. Världsbyggaren skriver filerna.

~~~
# Platsens namn

## Bokens tid
Det som är belagt eller som författaren har bestämt om platsen vid bokens tid, med källor.

## Idag
Källa: Google Street View
Fotograferat: 2019-06 – 2023-08
Hämtat: 2026-10-04
Beskrivningen med egna ord: gatans form, husen, material, grönska, ljus, ljud.

## Rutter
- Platsen → en annan plats, cykel: en dryg kvart (dagens vägnät, 2026-10-04)
~~~

- *Bokens tid* går före *Idag*. Allt under *Idag* är dagens värld.
- Raden `Fotograferat:` används av `bok graph context` för att visa hur långt det är mellan bilderna och kapitlets tid.
- Här sparas inga bilder, inga avskrivna skyltar och inga siffror från Google, bara egna beskrivningar och formuleringar.
