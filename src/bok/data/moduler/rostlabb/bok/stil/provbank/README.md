# Provbanken

Godkända provstycken i bokens röst, ett per fil. Writer läser två eller tre av dem inför varje kapitel (`bok rost urval --kapitel N`), och `bok rost drift` mäter kapitlen mot dem.

Varje fil börjar med ett huvud:

    ---
    lage: stilla
    kalla: gen-03 B
    datum: 2026-10-04
    ---

- `lage`: `stilla` eller `tryck`.
- `kalla`: generation och variant, eller kapitlet ett levande ställe kom från (`kapitel-07`).
- `datum`: när stycket godkändes.

Högst 15 stycken. Vid varje aktgräns rensar författaren banken.
