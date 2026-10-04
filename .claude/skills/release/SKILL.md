---
name: release
description: Används i harness-repot när utvecklaren vill släppa en ny version av bok ("gör en release", "släpp 2.3", "dags för en version"). Väljer version, flyttar Unreleased i CHANGELOG, höjer versionen och tar PR:en till merge; taggen och GitHub-releasen skapas automatiskt.
---

# Release av bok

Processen och reglerna står i `docs/utveckla-och-releasa.md`. Läs den först; den här skillen är stegen i ordning.

## 1. Läget

```sh
git fetch origin
git status
git log --oneline "$(git describe --tags --abbrev=0 origin/main)"..origin/main
sed -n '/^## \[Unreleased\]/,/^## \[/p' CHANGELOG.md
```

- Arbeta på en gren från senaste `origin/main`, aldrig direkt på `main`.
- Är `[Unreleased]` tom men det finns ändringar sedan förra taggen: skriv avsnittet utifrån commits och PR:er (för användaren, kategorierna Lagt till, Ändrat, Fixat, Borttaget, Säkerhet). Citera aldrig användares förslag.
- Är allt tomt: säg att det inte finns något att släppa och sluta.

## 2. Versionen

Föreslå patch, minor eller major enligt tabellen i `docs/utveckla-och-releasa.md`, med en mening om varför. Ändras något i `src/bok/data/genererat/` måste versionen höjas, annars når ändringen inga böcker. Utvecklaren bekräftar.

## 3. Ändringarna

1. `src/bok/__init__.py`: `__version__ = "X.Y.Z"`.
2. `CHANGELOG.md`:
   - `## [Unreleased]` blir `## [X.Y.Z] — <dagens datum, ÅÅÅÅ-MM-DD>`, med ett nytt tomt `## [Unreleased]` ovanför.
   - Länkarna längst ned: `[Unreleased]: …/compare/vX.Y.Z...HEAD` och en ny rad `[X.Y.Z]: …/compare/vFÖRRA...vX.Y.Z` överst bland versionerna.
3. Kontrollera:

```sh
uv run pytest -q
python scripts/changelog.py X.Y.Z
```

Visa release-texten för utvecklaren.

## 4. PR och merge

Fråga innan du pushar och innan du mergar.

```sh
git add src/bok/__init__.py CHANGELOG.md
git commit -m "release: X.Y.Z"
git push -u origin HEAD
gh pr create --title "release: X.Y.Z" --body-file <fil med release-texten>
gh pr checks --watch
gh pr merge --merge
```

## 5. Efter merge

```sh
gh run list --workflow release.yml --limit 1
gh release view vX.Y.Z
```

Workflowen `Release` skapar taggen och releasen. Har den inte gjort det: läs körningens logg och rätta; skapa aldrig taggen för hand på en annan commit än merge-commiten.

Sedan, när det gäller:

- **Förslag som kom med:** följ steget om releaser i skillen `forslag` (etiketten `infort:X.Y.Z` och svar till användarna).
- **Mottagaren ändrad:** `cd mottagare && npx wrangler whoami && npx wrangler deploy`. Fabians privata Cloudflare-konto, aldrig Digitalists; fråga först.
- **Uppgradera lokalt:** `uv tool upgrade bok`, och berätta att användarna kör `uv tool upgrade bok` och `bok init` i sina böcker.
