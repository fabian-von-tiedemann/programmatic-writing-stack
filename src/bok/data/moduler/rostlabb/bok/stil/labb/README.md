# Röstlabbet

Här söks bokens röst och form. Författaren skriver inte: Claude skriver varianter, författaren pekar ut vad som lever och vad som är dött, och nästa generation bygger på det.

## Två sorters prov

- **Formprov:** en skiss av första akten på en sida, i fyra olika former. Visar det som bara syns i bokens skala: hur kapitlen ser ut, vad som utelämnas, hur tiden rör sig.
- **Röstprov:** två provscener ur boken i `bok/stil/labb/provscener.md`, 250–350 ord var, en stilla och en under tryck. Samma scener i varje generation.

Varje generation har fyra varianter (A–D) med var sitt recept och en kontroll utan recept: så skriver Claude utan riktning. Kontrollen visar AI-genomsnittet, det boken inte ska låta som.

## Ett recept

3–6 drag, vart och ett med en källa: en förebild (texterna i `bok/stil/exempel/`) eller ett frö ur `bok fron`.

```
- Distans: berättaren registrerar, tolkar aldrig. (förebild)
- Upprepning i repliker som vägrar svara. (förebild)
- Mötesprotokollets passiv när makten talar. (frö: kalla – mötesprotokoll)
```

## Generationerna

En fil per generation: `gen-01.md`, `gen-02.md` … för röstprov och `form-01.md` … för formprov. Varje fil har recepten med källor, texterna, kritikerns sållning och författarens pekningar under varje variant.

## När rösten är hittad

`bok/stil/rost.md` skrivs om med tre rubriker:

```
## Recept
- Drag (källa). Hur det märks. Exempel: "…"

## Antiröst
- Mönster ur kontrollerna och de döda ställena. Exempel: "…"

## Form
Se Formlag i bok/koncept/form.md.
```

De godkända provstyckena sparas i `bok/stil/provbank/`, röstprovens kontroller i `bok/stil/kontroll/` och formlagen under `## Formlag` i `bok/koncept/form.md`.
