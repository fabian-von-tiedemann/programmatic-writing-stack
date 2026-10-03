# Installera bok på en ny dator

En guide för den som ska skriva med `bok` på en Mac. Allt görs en gång; sedan räcker det att öppna boken i Conductor eller Claude Code och prata.

## 1. Program du behöver

- **Claude Code** och/eller **Conductor**, inloggade på ditt konto.
- **Terminal** (finns i Program → Verktygsprogram).

## 2. Git

Skriv i Terminal:

```sh
git --version
```

Om macOS frågar om att installera *Command Line Tools*: säg ja och vänta tills det är klart. Berätta sedan för git vem du är (det syns i bokens historik):

```sh
git config --global user.name "Ditt Namn"
git config --global user.email "din@epost.se"
```

## 3. uv

`uv` installerar `bok` och hämtar själv den Python-version som behövs.

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

(Har du Homebrew går det också med `brew install uv`.) Stäng Terminal och öppna den igen.

## 4. bok

```sh
uv tool install git+https://github.com/fabian-von-tiedemann/programmatic-writing-stack
uv tool update-shell
```

Stäng Terminal, öppna den igen och kontrollera:

```sh
bok --version
```

## 5. Din bok

Skapa en mapp för boken och gör den till ett bokrepo:

```sh
mkdir -p ~/Böcker/min-bok
cd ~/Böcker/min-bok
bok init --titel "Arbetstitel"
```

Titeln kan ändras när som helst.

**Har du redan chattat om boken?** Lägg chattarna och anteckningarna i mappen `inkorg/` i boken.

## 6. Säkerhetskopia (rekommenderas)

Lägg boken i ett **privat** repo på GitHub, så att inget går förlorat om datorn går sönder. Det kräver ett GitHub-konto och verktyget `gh` (`brew install gh`, sedan `gh auth login`):

```sh
cd ~/Böcker/min-bok
gh repo create min-bok --private --source . --push
```

Använd **aldrig** ett publikt repo för en bok.

## 7. Börja skriva

- **Conductor:** lägg till `~/Böcker/min-bok` som repository. Varje workspace är en egen gren; slå ihop godkänt arbete tillbaka till `main`.
- **Claude Code:** öppna mappen och starta Claude Code där.

Säg till exempel "Hej, jag vill skriva en bok" eller "gå igenom inkorgen". Claude vet var boken står (`bok status`) och föreslår nästa steg.

## Uppdatera

När det kommit en ny version av `bok`:

```sh
uv tool upgrade bok
cd ~/Böcker/min-bok
bok init
```

Dina egna filer i boken rörs aldrig; ramverkets filer uppdateras. Har något av dina förslag förts in i den nya versionen säger `bok init` det.

## Om något krånglar

- **"bok: command not found":** kör `uv tool update-shell` och öppna en ny Terminal.
- **Claude frågar om lov för varje kommando:** kör `bok init` i bokens mapp igen; den tillåter `bok`, `git add` och `git commit`.
- **Något i verktyget är krångligt eller fel:** säg det till Claude i samtalet. Du får se exakt vad som skickas som förslag, och inget ur boken skickas. `bok forslag` visar vad som hänt med dina förslag, och `bok forslag av` stänger av förslag helt.
