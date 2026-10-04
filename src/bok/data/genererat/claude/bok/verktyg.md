# Verktyg

Kommandon som rollerna och skillen kör. Alla fungerar var som helst i bokens mapp.

| Kommando | Gör |
|---|---|
| `bok status` | var boken står, vad som saknas och nästa steg (`--json` för skillen) |
| `bok graph context --kapitel N` | underlaget för ett kapitel enligt scenkortet |
| `bok graph vem-vet <hemlighet> --kapitel N` | vem som känner till något vid slutet av kapitel N |
| `bok graph bagar --oppna` | öppna bågar och olösta planteringar |
| `bok graph karaktar <id>` | en person i grafen |
| `bok graph var <plats>` | händelser på en plats |
| `bok graph tidslinje [--fran ÅR] [--till ÅR]` | daterade händelser i tidsordning, med åldrar |
| `bok validate manuskript/kapitel-NN.md` | förbjudna namn, förlagornas namn, låsta ställen ur pekningarna och tidsfel i grafen stoppar (exitkod 1); namn som saknas i grafen och åldrar som inte stämmer är varningar |
| `bok fron [--antal N] [--klass KLASS …] [--antagande TEXT …] [--slump TAL] [--spara MAPP]` | slumpade frön till ett vägval eller Röstlabbet (`--json` för skillen); klasserna är doman, omvandning, begransning, process och forlaga, och för Röstlabbet rostdrag, formgrepp och kalla |
| `bok tics manuskript/kapitel-NN.md` | tics per kapitel; `--bok` för hela boken |
| `bok rost profil` | provbankens profil: meningslängd, repliker, skiljetecken, pronomenstart (modulen `rostlabb`) |
| `bok rost drift manuskript/kapitel-NN.md` | kapitlet mot rösten (provbanken) och AI-genomsnittet (kontrollen) med Burrows Delta, mått utanför röstens spridning och pastisch; varningar, stoppar inget |
| `bok rost urval --kapitel N` | provstycken som Writer läser inför kapitlet, efter scenkortets `lage` |
| `bok rapport spara -` | spara en rapport från stdin; avvisar fel frontmatter |
| `bok mall <modul>` | lägg till en tillvalsmodul; utan namn listas modulerna |
| `bok annotations --sedan ÅÅÅÅ-MM-DD` | läsarnoter från Apple Böcker (macOS) |
| `bok karta status` | om nyckeln till Google Maps finns och fungerar (visar aldrig nyckeln) |
| `bok karta restid <från> <till>` | restid och avstånd i dag till fots, med cykel, bil och kollektivt (`--satt`, `--avgang 08:15`, `--ankomst 08:15`, `--dag ÅÅÅÅ-MM-DD`). Sparas aldrig |
| `bok karta gatuvy <plats> [<till>]` | gatubilder på en plats eller längs en rutt, till en tillfällig mapp utanför boken (`--antal`, `--mellanrum`, `--satt`) |
| `bok karta stada` | rensa de tillfälliga bilderna |
| `bok bild <url>` | ladda ner en arkivbild till en tillfällig mapp för att titta på den |
| `bok init` | uppgradera ramverket efter `uv tool upgrade bok` |

Spara en rapport från en roll:

```sh
bok rapport spara - <<'RAPPORT'
---
omfang: kapitel
kapitel: 3
roll: redaktor
runda: 1
betyg: {struktur: 8, karaktar: 8, spanning: 7, kontinuitet: 9, tema: 8}
utfall: revidera
blockerande: []
---

## Blockerande
…
RAPPORT
```
