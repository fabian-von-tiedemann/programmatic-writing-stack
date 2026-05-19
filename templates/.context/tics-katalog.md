# Tics-katalog

Mekanisk första-pass-lista. Prosa-städ-agenten kör `scripts/grep-tics.sh` mot varje kapitel innan mening-för-mening-passet. Allt som träffar markeras för review.

**Princip:** Tics är konstruktioner/ord/märkeshänvisningar som *vinner* i små doser men *förstör* om de upprepas mekaniskt. Tak per ord kalibreras vartefter manuskriptet växer. Allt över tak är aktuellt problem; allt under är förebyggande för kommande revisioner.

---

## 1. Doft-tics (variera doftbeskrivningar)

Mönster (regex): `\bluktade\b`

**Regel:** Samma doftsubstantiv max 1 gång per bok om det inte är en *medveten paralleliseringspoäng* (= flaggas för förläggare). Variera grammatiskt och lexikalt.

---

## 2. Dialog-mumlar-tics ("Mm.", "Hm.", "Tja.")

Mönster: `"Mm\."`, `"Hm\."`, `"Tja\."`

**Tak:** 4-5 i hela boken per variant. Variera med: "Ja.", tystnad, nick, eller skippa svaret helt. **Per-karaktär-rekommendation:** låt mumlanden vara karaktärs-signum, inte default.

---

## 3. Gest-tics ("nickade", "ryckte på axlarna", "log")

Mönster: `\bnickade\b`, `\bryckte på axlarna\b`, `\blog\b`

**Tak:** max 2 per kapitel, max 35-40 i hela boken per gest. Varannan ska variera: "fällde huvudet", "böjde nacken kort", "ett halvt nicka", "ett ja utan ord", "höll blicken i en sekund extra", "ingenting".

---

## 4. Räkne-tics (precision utan funktion)

Mönster: `\bräknade\b`, `(tre|fyra|fem|sex|sju|två) sekunder`

**Regel:** Räknande är *karaktärs-tic* — koppla till en specifik POV (analytisk, militär, kalibrerande). I andra POV: stryk eller omformulera. **Tak: 2 per kapitel.**

Cheat-test: är sekunderna *funktionellt nödvändiga* (puls-kalibrering, lögn-test)? Om författaren skriver "hon stod i tre sekunder" som tidsfärg = stryk.

---

## 5. "exakt" — kalibrera intentionalitet

Mönster: `\bexakt\b`

Cheat-test: stryker "exakt" ändras meningen? Om nej = stryk. Om ja = behåll (precisionsmarkör för specifik POV OK).

---

## 6. Bilmärken (variation krävs)

Mönster: `Volvo|BMW|Audi|Mercedes|Toyota|Skoda|Tesla|Kia|VW|Volkswagen|Peugeot|Hyundai`

**Princip:** Bilmodeller kan vara canon (polis, protagonist, antagonist), men bipersoner ska variera. Räkna totalt över kapitlen — om en modell nämnts 4+ gånger ska nästa biroll-bil vara annan modell.

---

## 7. Klädmärkes-tics (funktionellt eller stryk)

Mönster: `Acne|COS|Filippa K|Common Projects|Toteme|Carhartt|Aspesi|Hope|Tiger of Sweden|Stutterheim`

**Regel:** Klädmärken får finnas om de bär konkret funktion (klass-signal, karaktärs-quirk). Tre samtidiga märkesnamn i samma stycke = ut. Max 2 märken per scen.

---

## 8. Klockslag — för exakt utan motivering

Mönster (regex): `\bklockan \d`, `kl \d`, `\b\d{1,2}[.:]\d{2}\b`

Cheat-test: är klockslaget *funktionellt*? (kalibrerar tid, utredning, deadline = OK). Atmosfär-klockslag ("hon vaknade kl 06.43") = stryk eller runda.

---

## 9. Tom Clancy / militär-precision-tics

Grep-lista:
```
\b(trettiotvå|fyrtiotre|sextiosju|åttiotvå) (sekunder|minuter)
aviator
aviator-glasögon
Operation\s[A-ZÅÄÖ]
hundrafemtio gånger
\bgör det blint\b
\bmuskelminne\b
\basset\b
\bhandler\b
```

**Regel:** Larsson-svenska räknar inte decimal-sekunder. Undvik elite-team-vokabulär ("hennes celler", "asset", "handler", "the package"). Svensk thriller använder vanliga ord: utredning, källa, kontakt, dokument.

---

## 10. Aforismer i karaktärs-tankar (förbjudna)

Mönster:
```
\bär värre än\b
\bDet enda som\b
\bSanningen om\b
\bSanningen var att\b
\bFaktum är att\b
\bDet finns två sorters\b
```

**Regel:** Karaktärer tänker inte i aforismer. De observerar, registrerar, agerar. Aforismer är essäer som glider in i prosan.

---

## 11. Anglicism / svengelska-tics

Grep-lista:
```
\bYes\b
\bOkay\b
\bAlright\b
\bliterally\b
\babsolutely\b
\bobviously\b
\bsorry\b
\bgood\b
\bfine\b
```

**Regel:** Vid alla träffar — verifiera att det är intentionell kodväxling (karaktär som jargong, internationellt sammanhang) och inte slap.

---

## 12. Hedge-/utfyllnads-tics

Grep-lista:
```
\bför säkerhets skull\b
\bav en slump\b
\bpå något sätt\b
\bpå sätt och vis\b
\bliksom\b
\briktigt\b   (när det är fyllord, inte adverb)
\bganska\b    (samma)
\btypiskt\b
\blite\b      (när det är hedgare, inte mätbar)
```

**Regel:** Hedgeord försvagar prosan. Stryk om de inte bär funktion.

---

## 13. Andetag som tidsmått

Mönster: `\b(djupt andetag|drog efter andan|tog ett andetag|hörde sin egen andning)\b`

**Regel:** Andetag är karaktärs-tic — koppla till specifik POV (max 1-2 i hela boken per POV). Vid träff i fel POV = stryk.

---

## 14. "som om" — överanvänt liknelse-prefix

Mönster: `\bsom om (hon|han|de)\b`

**Tak: max 2 per kapitel.** Cheat-fix: byt ut tredje förekomsten mot direkt observation ("hon var trött" istället för "hon såg ut som om hon var trött").

---

## 15. Tystnad-tic

Mönster: `det blev tyst|tystnaden|tystnade`

**Tak: max 1 per kapitel.** Tystnader-som-prosa är OK men variera: "ingen sa något", "luften stannade", "han väntade", "en paus som inte bröts".

---

## 16. Författare-på-promenad-fraser (FÖRBJUDNA)

Mönster:
```
^Sanningen var att
^Faktum är att
^I efterhand
^Han skulle senare förstå
^Hon skulle senare förstå
^Det fanns en tid då
\bsom alla i [A-ZÅÄÖ]
\bdet visste han på samma sätt som\b
```

**Regel:** Författar-essäer som glider in i karaktärs-tankarna är förbjudna. Karaktären observerar, registrerar, beslutar.

---

## 17. Bestämd form utan etablering

Mönster (svår att grep:a — flaggas av validator R3): bestämd form på generella substantiv (skägget, telefonen, mappen, bilen, bandet) utan tidigare obestämd-form-introduktion.

**Regel:** Egennamn introducerar sig själva. Generella substantiv kräver introduktion. Se writer-brief W1.

---

## 18. Verkliga personer (namn-blacklist)

> Fyll på vartefter granskningar avslöjar krockar med verkliga personer i bokens miljö.

**Verifierade träffar i texten:**
```
(lista per förekomst — radnr + action)
```

**Att aldrig nämna utan extra granskning:**
```
(generell lista — politiker, opinionsbildare, branschprofiler i bokens närmiljö)
```

Verifiera vid varje namedrop: bara nämnt i atmosfär (OK) eller har fiktiv handling (EJ OK).

---

## 19. Fakta-fälla-tics

> Per fel som hittats — lägg in grep:bar regex så att samma fel inte upprepas.

```
(exempel: "JKL\b" — heter Kekst CNC sedan 2021)
```

---

## 20. Geografi-fälla-tics

> Per geografi-fel som hittats — grep:bar regex.

```
(exempel: "\bKlinte\b(?!hamn)" — Klinte ≠ Klintehamn)
```

---

## 21. POV-läckage (krocksök)

Cheat-grep efter karaktärs-signum i fel POV. Bygg listor per POV vartefter character-deepening-filerna växer:

```
# I <POV-A>-kapitel:
grep -E "<POV-B-signum>" → POV-B-läckage
grep -E "<POV-C-signum>" → POV-C-läckage
```

---

## 22. Sammansatta ord (SAOL-test)

Mönster: `[a-zåäö]+-[a-zåäö]+` följt av SAOL-uppslag.

Frekvent påhittad: `[a-zåäö]+-[a-zåäö]+-[a-zåäö]+` (treord-bindestreck — ofta tic).

---

# Användning

```bash
# Kör mot enskild fil:
./scripts/grep-tics.sh manuskript/kapitel-01.md

# Kör mot hela manuskript-katalogen:
./scripts/grep-tics.sh
```

Output: kategoriserad rapport med radnr per kategori. Allt över "tak" flaggas. Output skrivs till `.context/tics-rapport-<filnamn>.md`.

---

# Aktuella problem

> Lista här vad senaste pass hittade som över tak. Fyll på + rensa vartefter fixar appliceras.
