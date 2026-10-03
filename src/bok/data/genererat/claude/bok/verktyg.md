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
| `bok validate manuskript/kapitel-NN.md` | förbjudna namn (exitkod 1) och namn som saknas i grafen |
| `bok tics manuskript/kapitel-NN.md` | tics per kapitel; `--bok` för hela boken |
| `bok rapport spara -` | spara en rapport från stdin; avvisar fel frontmatter |
| `bok mall <modul>` | lägg till en tillvalsmodul; utan namn listas modulerna |
| `bok annotations --sedan ÅÅÅÅ-MM-DD` | läsarnoter från Apple Böcker (macOS) |
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
