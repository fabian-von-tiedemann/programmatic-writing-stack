# templates/ — master-katalog för Programmatic Writing Stack v1.2

Detta är **master-katalogen** som `scripts/init-writing-stack.sh` klonar till nya bokprojekt. Allt här är RENT och generiskt — ingen bok-specifik canon. Placeholder-fält (`{{BOK_TITEL}}`, `{{GENRE}}`, etc.) ersätts av init-scriptet eller manuellt.

## Vad ingår

- **CLAUDE.md** — stående instruktioner för hela projektet (med placeholders)
- **.gitignore.template** — typisk .gitignore för ett bokprojekt
- **manuskript/** — exempelkapitel + README
- **docs/** — PRD + HTML-deliverable + ADR-praxis
- **.context/** — hela ramverket (process, canon, tools, roller, hantverk, story-graph, koncept/plot/stil/meta/forlag/varld)
- **scripts/** — alla körbara verktyg (books-annotations, grep-tics, render/validate/tag-manuscript, graph-query)

## Användning

```bash
# Manuellt (utan init-script):
cp -R templates/ ../min-nya-bok/
cd ../min-nya-bok/
mv .gitignore.template .gitignore
git init

# Eller via init-script (när det finns):
scripts/init-writing-stack.sh ../min-nya-bok/
```

Efter klonen:
1. Fyll i `CLAUDE.md` (ersätt `{{PLACEHOLDERS}}`)
2. Börja på Lager 1 (`.context/koncept/`) innan något annat
3. Följ FAS 0-9 i `.context/process.md`

## Filer per typ

| Typ | Innehåll |
|---|---|
| **Kopior** | docs/PRD, docs/HTML, .context/hantverk/*, scripts/* |
| **Generiska** | CLAUDE.md, process.md, canon.md, tools.md, tics-katalog.md, alla roller |
| **MALL-versioner** | koncept/, plot/, stil/, forlag/, meta/, varld/, research-dossier/ |
| **Tomma + struktur** | story-graph/*.json (`{}`), story-graph/*.md (rubrik) |
| **.gitkeep** | alla rapport-kataloger |

## Versioning

Master-katalogen följer ramverkets version. Senaste:
- **v1.2** — 13 roller, full Programmatic Writing Stack (Lager 1-7), Del III-tekniker integrerade

Ändringar i master propageras inte automatiskt till befintliga bokprojekt. Varje bok är en oberoende klon.
