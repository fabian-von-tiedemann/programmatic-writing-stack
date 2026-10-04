# Restider och gatubilder med Google Maps

För dig som skriver med `bok` och vill att Claude ska kunna svara på "hur lång tid tar det att cykla dit?" och titta på gatubilder för att beskriva miljöer. Det är frivilligt; allt annat i `bok` fungerar utan.

## Vad det gör, och inte gör

- **Restider:** till fots, med cykel, bil och kollektivt, mellan bokens platser eller vilka adresser som helst.
- **Gatubilder:** Claude hämtar bilder från Google Street View på en plats eller längs en rutt, tittar på dem och skriver en beskrivning med egna ord i `bok/varld/platser/`.
- **Inget från Google sparas i boken.** Inga bilder, inga restider. Det som sparas är egna beskrivningar och formuleringar ("en dryg kvart på cykel"), fotodatum och när det hämtades. Bilderna ligger i en tillfällig mapp utanför boken och rensas.
- **Allt är dagens värld.** Restiderna räknas på dagens vägar och tidtabeller, och gatubilderna är från de senaste åren. Utspelar sig boken 1978 visar `bok` hur många år som skiljer, och Claude kan söka i arkiv efter hur platsen såg ut då.

## Vad det kostar

Du behöver ett eget konto hos Google Cloud med betalning. Varje månad ingår 10 000 ruttanrop och 10 000 gatubilder, och fotodatum är gratis. En bok kommer sällan i närheten. Sätt ändå ett tak och ett budgetlarm (steg 4), så att inget kan dra iväg.

## 1. Skapa ett projekt

1. Gå till [console.cloud.google.com](https://console.cloud.google.com) och logga in med ditt Google-konto.
2. Välj projektlistan högst upp → **New project**. Kalla det till exempel `bok`. **Create**.
3. Meny → **Billing** → koppla ett betalkonto till projektet (lägg till ett kort om du inte har ett).

## 2. Aktivera Routes API

1. Meny → **APIs & Services** → **Library**.
2. Sök **Routes API** → **Enable**.

## 3. Skapa nyckeln och begränsa den

1. **APIs & Services** → **Credentials** → **Create credentials** → **API key**. Kopiera nyckeln; du behöver den i steg 6. Visa den aldrig för någon och klistra aldrig in den i chatten.
2. Klicka på nyckeln. Under **API restrictions**: välj **Restrict key** och kryssa i **Routes API** (och **Street View Static API** om du gör steg 5). **Save**.

## 4. Tak och larm

1. **APIs & Services** → **Routes API** → **Quotas**: sätt taket per dag till till exempel 200. Gör samma sak för Street View Static API om du aktiverar det.
2. Meny → **Billing** → **Budgets & alerts** → **Create budget**: till exempel 10 kronor, med larm till din e-post.

## 5. Street View, ett eget val

Googles villkor förbjuder att spara deras material och att "skapa innehåll från Google Maps-innehåll". `bok` sparar aldrig bilderna och låter Claude skriva egna beskrivningar av det som syns. Vi tolkar det som tillåtet, men Google kan se annorlunda på det, och det är ditt konto som används. Läs gärna villkoren själv: [Google Maps Platform Terms of Service](https://cloud.google.com/maps-platform/terms).

Vill du använda gatubilderna:

1. **APIs & Services** → **Library** → **Street View Static API** → **Enable**.
2. Lägg till det under nyckelns **API restrictions** (steg 3).

Utan det fungerar restiderna, men inte gatubilderna.

Får du senare felet att Street View kräver signering: **Google Maps Platform** → **Credentials** → **URL signing secret**, kopiera hemligheten och kör `bok karta nyckel --signering` (steg 6).

## 6. Lägg in nyckeln

Öppna **Terminal** (inte Claude) och skriv:

```sh
bok karta nyckel
```

Klistra in nyckeln och tryck på retur. Den syns inte när du klistrar in den. Kontrollera sedan:

```sh
bok karta status
```

Det ska stå att Routes API fungerar, och Street View Static API om du gjorde steg 5. Nyckeln sparas i din hemkatalog (`~/.config/bok/`), utanför boken, så att den aldrig hamnar i bokens repo.

**Har du råkat klistra in nyckeln i chatten?** Skapa en ny nyckel (steg 3), ta bort den gamla under **Credentials**, och kör `bok karta nyckel` igen.

## 7. Använda det

Prata med Claude som vanligt:

- "Hur lång tid tar det att gå från lägenheten till skolan?"
- "Hur ser det ut på gatan där fabriken ligger? Skriv in det i platsen."
- "Ta fram miljön för platserna i kapitel 4."
- "Hur såg torget ut på sjuttiotalet?"

Platserna behöver en adress. Claude frågar efter den och skriver in den i grafen.

## Ta bort

```sh
bok karta nyckel --ta-bort
```

Stäng sedan av API:erna eller hela projektet i Google Cloud.
