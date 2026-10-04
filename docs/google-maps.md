# Restider och gatubilder med Google Maps

Den här guiden är för dig som skriver med `bok` och vill att Claude ska kunna svara på frågor som "hur lång tid tar det att cykla dit?" och titta på gatubilder för att beskriva miljöer. Funktionen är frivillig, och allt annat i `bok` fungerar utan den. Räkna med en kvart.

## Vad funktionen gör, och inte gör

- **Restider:** till fots, med cykel, bil och kollektivt, mellan bokens platser eller vilka adresser som helst.
- **Gatubilder:** Claude hämtar bilder från Google Street View på en plats eller längs en rutt, tittar på dem och skriver en beskrivning med egna ord i `bok/varld/platser/`.
- **Inget från Google sparas i boken.** Varken bilder eller restider sparas. Det som sparas är egna beskrivningar och formuleringar ("en dryg kvart på cykel"), fotodatum och när uppgifterna hämtades. Bilderna ligger i en tillfällig mapp utanför boken och rensas bort.
- **Allt visar dagens värld.** Restiderna räknas på dagens vägar och tidtabeller, och gatubilderna är från de senaste åren. Utspelar sig boken 1978 visar `bok` hur många år som skiljer, och Claude kan söka i arkiv efter hur platsen såg ut då.

## Vad det kostar

Google kräver ett betalkonto, även när du bara använder det som ingår gratis. Varje månad ingår 10 000 ruttanrop och 10 000 gatubilder, och fotodatum kostar ingenting. En bok kommer sällan i närheten av de gränserna. Är ditt konto nytt får du dessutom en provperiod (**Free trial**) med en kredit. Under provperioden dras allt från krediten och inget från ditt kort. När provperioden tar slut behöver du välja **Upgrade** för att funktionen ska fortsätta fungera, men inom gratisvolymen kostar den fortfarande ingenting. Sätt ändå ett budgetlarm och dagstak (steg 6), så att kostnaderna inte kan dra iväg.

## 1. Skapa ett projekt

1. Gå till [console.cloud.google.com](https://console.cloud.google.com) och logga in med ditt Google-konto.
2. Öppna projektlistan högst upp och välj **New project**. Projektnamnet måste vara minst 4 tecken långt, till exempel `bok-karta`. Låt *Parent resource* stå som det är och klicka på **Create**.
3. Välj det nya projektet i projektlistan högst upp. Allt nedan gäller det projektet.

## 2. Betalning

Öppna menyn ☰, välj **Billing** och koppla ett betalkonto till projektet. Lägg till ett kort om du inte redan har ett.

## 3. Aktivera Routes API

1. Öppna menyn ☰, välj **APIs & Services** och sedan **Library**. Sök efter **Routes API** och klicka på **Enable**.
2. Google skapar då ofta en nyckel automatiskt, *Maps Platform API Key*, och frågar om du vill skydda den (*Protect your API key*). Klicka på **Maybe later**. Alternativen där (webbplatser, IP-adresser, appar) passar inte för ett program på din egen dator. Begränsningen som spelar roll gör du i nästa steg.

Skapades ingen nyckel: välj **APIs & Services**, sedan **Credentials**, **Create credentials** och **API key**.

## 4. Begränsa nyckeln

1. Välj **APIs & Services** och sedan **Credentials**. Klicka på nyckelns namn under **API Keys**.
2. En ny nyckel får ofta använda alla Maps-API:er, och då står det till exempel *32 APIs* under **Select API restrictions**. Öppna listan, avmarkera alla och kryssa bara i **Routes API**, samt **Street View Static API** om du gör steg 5. Klicka på **OK**.
3. Låt **Application restrictions** stå på **None**.
4. Klicka på **Save** längst ner. Det kan ta upp till fem minuter innan ändringen gäller.

Visa aldrig nyckeln för någon och klistra aldrig in den i chatten.

## 5. Street View, ett eget val

Googles villkor förbjuder att spara deras material och att "skapa innehåll från Google Maps-innehåll". `bok` sparar aldrig bilderna och låter Claude skriva egna beskrivningar av det som syns. Vi tolkar det som tillåtet, men Google kan se annorlunda på saken, och det är ditt konto som används. Läs gärna villkoren själv: [Google Maps Platform Terms of Service](https://cloud.google.com/maps-platform/terms).

Om du vill använda gatubilderna:

1. Välj **APIs & Services** och sedan **Library**. Sök efter **Street View Static API** och klicka på **Enable**. Det här steget behövs även om API:et redan syns i nyckelns lista, eftersom den listan visar alla Maps-API:er och inte bara de aktiverade. Står det **Manage** i stället för **Enable** är API:et redan aktiverat.
2. Kontrollera att **Street View Static API** finns med under nyckelns **API restrictions** (steg 4).

Utan Street View fungerar restiderna, men inte gatubilderna.

## 6. Larm och dagstak

1. **Budgetlarm:** öppna menyn ☰ och välj **Billing**, sedan **Budgets & alerts** och **Create budget**.
   - *Define:* välj **Alerts only** och ge budgeten ett namn. Alternativet *Spend cap enforcement* är en förhandsversion som bara gäller vissa tjänster.
   - *Scope:* under *Projects* väljer du bara ditt projekt.
   - *Amount:* välj *Specified amount*, till exempel 50 kronor.
   - *Actions:* behåll larmnivåerna (50, 90 och 100 procent) och *Email alerts to billing admins and users*. Klicka på **Finish**.

   Ett budgetlarm skickar bara e-post. Det stoppar ingenting.
2. **Dagstak:** det här är själva stoppet. Välj **APIs & Services**, sedan **Routes API** och fliken **Quotas & System Limits**. Sätt taket för anrop per dag till till exempel 200. Gör samma sak för Street View Static API.

## 7. Lägg in nyckeln

1. Gå till **APIs & Services** och sedan **Credentials**. Klicka på nyckeln och sedan på **Show key**, och kopiera nyckeln.
2. Öppna **Terminal** (inte Claude) och skriv:

   ```sh
   bok karta nyckel
   ```

   Klistra in nyckeln och tryck på retur. Nyckeln syns inte när du klistrar in den.
3. Kontrollera att den fungerar:

   ```sh
   bok karta status
   ```

   Det ska stå att Routes API fungerar, och Street View Static API om du gjorde steg 5.

Nyckeln sparas i din hemkatalog (`~/.config/bok/`), utanför boken, så att den aldrig hamnar i bokens repo.

**Har du råkat klistra in nyckeln i chatten?** Skapa en ny nyckel, ta bort den gamla under **Credentials** och kör `bok karta nyckel` igen.

## 8. Använda det

Prata med Claude som vanligt:

- "Hur lång tid tar det att gå från lägenheten till skolan?"
- "Hur ser det ut på gatan där fabriken ligger? Skriv in det i platsen."
- "Ta fram miljön för platserna i kapitel 4."
- "Hur såg torget ut på sjuttiotalet?"

Platserna behöver en adress. Claude frågar efter den och skriver in den i grafen.

## Om något inte fungerar

`bok karta status` säger vad som är fel:

- **"… är inte aktiverat i projektet"**: API:et är avstängt. Gör steg 3 eller steg 5 och klicka på **Enable**.
- **"Nyckelns begränsningar tillåter inte …"**: lägg till API:et under nyckelns **API restrictions** (steg 4) och vänta några minuter.
- **"Google godkänner inte nyckeln"**: nyckeln är felkopierad eller borttagen. Kör `bok karta nyckel` igen.
- **"Dagens tak … är nått"**: dagstaket från steg 6 är nått. Vänta till i morgon, eller höj taket.
- **"Street View kräver signering"**: välj **Google Maps Platform** och sedan **Credentials** och **URL signing secret**. Kopiera hemligheten och kör `bok karta nyckel --signering`.

## Ta bort

```sh
bok karta nyckel --ta-bort
```

Stäng sedan av API:erna eller hela projektet i Google Cloud.
