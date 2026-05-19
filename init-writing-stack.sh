#!/usr/bin/env bash
# init-writing-stack.sh — Klona Programmatic Writing Stack till nytt bokprojekt
#
# Användning:
#   ./scripts/init-writing-stack.sh <TARGET_DIR> <BOK_TITEL> [GENRE]
#
# Exempel:
#   ./scripts/init-writing-stack.sh ~/projects/bok-2 "Det Tysta Året" thriller
#   ./scripts/init-writing-stack.sh /tmp/test-stack "Titel" science-fiction
#
# Flaggor:
#   --dry-run         Visa vad som skulle göras utan att göra det
#   --no-git          Skippa git init + initial commit
#   --templates DIR   Override templates-path (alt. STACK_TEMPLATES_DIR env)
#
# Beteende:
#   1. Validerar argument (TARGET_DIR ej existerande eller tom; BOK_TITEL satt)
#   2. Hittar templates/ (script-relativt eller via STACK_TEMPLATES_DIR)
#   3. Skapar TARGET_DIR och kopierar templates/. rekursivt
#   4. Ersätter placeholders: {{BOK_TITEL}}, {{GENRE}}, {{DATUM}}, {{AR}}
#   5. git init + initial commit (om inte --no-git)
#   6. Skriver välkomst-meddelande
#
# Se docs/programmatic-writing-stack-PRD.md sektion 9 för vidare onboarding.

set -euo pipefail

# ---------- färger ----------
if [ -t 1 ]; then
    RED=$'\033[0;31m'
    GREEN=$'\033[0;32m'
    YELLOW=$'\033[0;33m'
    BLUE=$'\033[0;34m'
    BOLD=$'\033[1m'
    NC=$'\033[0m'
else
    RED='' GREEN='' YELLOW='' BLUE='' BOLD='' NC=''
fi

err()  { printf "%s\n" "${RED}FEL:${NC} $*" >&2; }
warn() { printf "%s\n" "${YELLOW}VARNING:${NC} $*" >&2; }
ok()   { printf "%s\n" "${GREEN}OK:${NC} $*"; }
info() { printf "%s\n" "${BLUE}INFO:${NC} $*"; }

# ---------- usage ----------
usage() {
    sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'
    exit "${1:-1}"
}

# ---------- argparse ----------
DRY_RUN=0
NO_GIT=0
TEMPLATES_OVERRIDE=""
POSITIONAL=()

while [ "$#" -gt 0 ]; do
    case "$1" in
        -h|--help) usage 0 ;;
        --dry-run) DRY_RUN=1; shift ;;
        --no-git)  NO_GIT=1; shift ;;
        --templates)
            [ "$#" -ge 2 ] || { err "--templates kräver argument"; exit 2; }
            TEMPLATES_OVERRIDE="$2"; shift 2 ;;
        --templates=*) TEMPLATES_OVERRIDE="${1#*=}"; shift ;;
        --) shift; while [ "$#" -gt 0 ]; do POSITIONAL+=("$1"); shift; done ;;
        -*) err "Okänd flagga: $1"; usage 2 ;;
        *) POSITIONAL+=("$1"); shift ;;
    esac
done

if [ "${#POSITIONAL[@]}" -lt 2 ]; then
    err "Saknar argument."
    usage 2
fi

TARGET_DIR="${POSITIONAL[0]}"
BOK_TITEL="${POSITIONAL[1]}"
GENRE="${POSITIONAL[2]:-thriller}"

# expandera ~ manuellt (bash gör inte det när argumentet är quoted)
case "$TARGET_DIR" in
    "~"|"~/"*) TARGET_DIR="${HOME}${TARGET_DIR#~}" ;;
esac

[ -n "$BOK_TITEL" ] || { err "BOK_TITEL får inte vara tom"; exit 2; }

# ---------- hitta templates/ ----------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -n "$TEMPLATES_OVERRIDE" ]; then
    TEMPLATES_DIR="$TEMPLATES_OVERRIDE"
elif [ -n "${STACK_TEMPLATES_DIR:-}" ]; then
    TEMPLATES_DIR="$STACK_TEMPLATES_DIR"
else
    TEMPLATES_DIR="$SCRIPT_DIR/../templates"
fi

if [ ! -d "$TEMPLATES_DIR" ]; then
    err "Templates-katalogen finns inte: $TEMPLATES_DIR"
    err "Sätt STACK_TEMPLATES_DIR eller använd --templates DIR."
    exit 3
fi
TEMPLATES_DIR="$(cd "$TEMPLATES_DIR" && pwd)"

# ---------- validera target ----------
WE_CREATED_TARGET=0
if [ -e "$TARGET_DIR" ]; then
    if [ ! -d "$TARGET_DIR" ]; then
        err "$TARGET_DIR finns men är ingen katalog."
        exit 4
    fi
    if [ -n "$(ls -A "$TARGET_DIR" 2>/dev/null)" ]; then
        err "$TARGET_DIR finns och är inte tom. Avbryter (säkerhet)."
        exit 4
    fi
fi

# ---------- cleanup ----------
cleanup_on_error() {
    local rc=$?
    if [ "$rc" -ne 0 ] && [ "$WE_CREATED_TARGET" -eq 1 ] && [ -d "$TARGET_DIR" ]; then
        warn "Städar upp $TARGET_DIR (skapad av detta script, exit=$rc)"
        rm -rf "$TARGET_DIR"
    fi
}
trap cleanup_on_error EXIT

# ---------- macOS vs Linux sed ----------
sed_inplace() {
    if [ "$(uname)" = "Darwin" ]; then
        sed -i '' "$@"
    else
        sed -i "$@"
    fi
}

# ---------- datum ----------
DATUM="$(date +%Y-%m-%d)"
AR="$(date +%Y)"

# ---------- summary ----------
cat <<EOF
${BOLD}Programmatic Writing Stack — init${NC}
  TARGET_DIR : $TARGET_DIR
  BOK_TITEL  : $BOK_TITEL
  GENRE      : $GENRE
  DATUM      : $DATUM
  TEMPLATES  : $TEMPLATES_DIR
  GIT        : $([ "$NO_GIT" -eq 1 ] && echo "nej (--no-git)" || echo "ja")
  DRY-RUN    : $([ "$DRY_RUN" -eq 1 ] && echo "ja" || echo "nej")

EOF

if [ "$DRY_RUN" -eq 1 ]; then
    info "Dry-run: skulle skapa $TARGET_DIR, kopiera templates/, ersätta placeholders, $([ "$NO_GIT" -eq 1 ] && echo 'skippa git' || echo 'köra git init + commit')."
    trap - EXIT
    exit 0
fi

# ---------- skapa target ----------
if [ ! -d "$TARGET_DIR" ]; then
    mkdir -p "$TARGET_DIR"
    WE_CREATED_TARGET=1
    ok "Skapade $TARGET_DIR"
fi

# ---------- kopiera templates ----------
# cp -r templates/. target/ — kopierar innehåll inkl dotfiles, behåller struktur
cp -R "$TEMPLATES_DIR/." "$TARGET_DIR/"
ok "Kopierade templates/ till $TARGET_DIR"

# ---------- ersätt placeholders ----------
# escapa BOK_TITEL för sed (& och / och \)
escape_sed() {
    printf '%s' "$1" | sed -e 's/[\/&]/\\&/g'
}
BOK_TITEL_ESC="$(escape_sed "$BOK_TITEL")"
GENRE_ESC="$(escape_sed "$GENRE")"

# alla textfiler (md, json, sh, py, txt, gitignore) — undvik binärer
PLACEHOLDER_COUNT=0
while IFS= read -r -d '' f; do
    if grep -lE '\{\{BOK_TITEL\}\}|\{\{GENRE\}\}|\{\{DATUM\}\}|\{\{AR\}\}' "$f" >/dev/null 2>&1; then
        sed_inplace \
            -e "s/{{BOK_TITEL}}/$BOK_TITEL_ESC/g" \
            -e "s/{{GENRE}}/$GENRE_ESC/g" \
            -e "s/{{DATUM}}/$DATUM/g" \
            -e "s/{{AR}}/$AR/g" \
            "$f"
        PLACEHOLDER_COUNT=$((PLACEHOLDER_COUNT + 1))
    fi
done < <(find "$TARGET_DIR" -type f \( -name '*.md' -o -name '*.json' -o -name '*.sh' -o -name '*.py' -o -name '*.txt' -o -name '.gitignore' -o -name '*.yaml' -o -name '*.yml' -o -name '*.toml' \) -print0)
ok "Ersatte placeholders i $PLACEHOLDER_COUNT fil(er)"

# ---------- .gitignore fallback ----------
if [ ! -f "$TARGET_DIR/.gitignore" ]; then
    cat > "$TARGET_DIR/.gitignore" <<'GITIGNORE'
.cache/
*.tmp
__pycache__/
*.pyc
.DS_Store
.venv/
node_modules/
GITIGNORE
    ok "Skapade .gitignore (fallback — saknades i templates/)"
fi

# ---------- git ----------
if [ "$NO_GIT" -eq 0 ]; then
    (
        cd "$TARGET_DIR"
        if [ -d .git ]; then
            warn "Git-repo finns redan i target — hoppar över git init"
        else
            git init -q
            ok "Initierade git"
        fi
        git add .
        if git diff --cached --quiet; then
            warn "Inget att committa"
        else
            git commit -q -m "init: Programmatic Writing Stack v1.2 för '${BOK_TITEL}'"
            ok "Initial commit skapad"
        fi
    )
fi

# ---------- success — disarm cleanup ----------
trap - EXIT

# ---------- välkomst ----------
cat <<EOF

${GREEN}${BOLD}Klart!${NC} cd $TARGET_DIR och börja med:

  1. Fyll i ${BOLD}CLAUDE.md${NC} (premise, distinguishing features, ambition)
  2. Skriv ${BOLD}premiss + logline + central-fråga${NC} i .context/
  3. Skissa ${BOLD}karaktärer${NC} i .context/story-graph/characters.json
     (minst 3 POV-karaktärer + huvud-antagonist)
  4. Dispatcha ${BOLD}Plot-arkitekten${NC} (FAS 0) — se .context/roles/

Läs vidare: ${BLUE}docs/programmatic-writing-stack-PRD.md${NC} sektion 9 (Onboarding-guide)

EOF
