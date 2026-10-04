# Din bok

Den här mappen är din bok. Du skriver den tillsammans med Claude: Claude skriver prosan, du bestämmer.

## Kom igång

Öppna mappen i Conductor eller Claude Code och skriv till exempel:

- **"Hej, jag vill skriva en bok."** Claude berättar hur det går till.
- **"Gå igenom inkorgen."** Om du har lagt chattar, anteckningar eller gamla utkast i `inkorg/`.
- **"Jag vill jobba med tonen."** Stilverkstaden: du visar texter du gillar, Claude provskriver en scen ur din bok i olika röster och du väljer.
- **"Var är vi?"** Var boken står och vad som är nästa steg. Fungerar när som helst.

Du kan börja var som helst: med en idé, en person, en scen eller ett slut. Claude sorterar in det du säger och föreslår formuleringar som du säger ja eller nej till.

Du godkänner planen innan något skrivs, varje kapitels scenkort innan kapitlet skrivs, och varje kapitel när det är klart.

## Mapparna

| Mapp | Innehåll |
|---|---|
| `inkorg/` | ditt råmaterial: chattar, anteckningar, utkast |
| `bok/` | planen och minnet: idén, personerna, handlingen, rösten, världen, vad som hänt i varje kapitel och granskningarna |
| `manuskript/` | kapitlen |
| `.claude/` | själva verktyget; det skrivs om när verktyget uppdateras, så ändra inget där |

Du behöver inte öppna filerna själv, Claude håller ordning på dem. Men allt går att läsa.

## Platser och miljöer

Med en egen nyckel till Google Maps kan Claude ta fram restider mellan bokens platser och titta på gatubilder för att beskriva miljöer. Guiden finns i verktygets repo: https://github.com/fabian-von-tiedemann/programmatic-writing-stack/blob/main/docs/google-maps.md. Inga bilder sparas i boken.

## Uppdatera verktyget

Kör i Terminal, i den här mappen:

```sh
uv tool upgrade bok
bok init
```

Dina egna filer rörs aldrig.

## Förslag

Är något i verktyget krångligt eller fel: säg det till Claude. Du får se exakt vad som skickas till dem som bygger verktyget, och ingenting ur boken skickas.

- `bok forslag` visar dina förslag och vad som hänt med dem.
- `bok forslag av` stänger av förslag helt.
