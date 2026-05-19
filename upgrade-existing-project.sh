#!/usr/bin/env bash
# upgrade-existing-project.sh — icke-destruktiv uppgradering av befintligt bokprojekt
#
# Användning:
#   ./upgrade-existing-project.sh <PROJECT_DIR> [--dry-run] [--force] [--templates DIR]
#
# Exempel:
#   ./upgrade-existing-project.sh ~/projects/sekretariatet
#   ./upgrade-existing-project.sh ~/projects/sekretariatet --dry-run
#   ./upgrade-existing-project.sh ~/projects/sekretariatet --force
#
# Flaggor:
#   --dry-run         Visa vad som skulle göras utan att göra det
#   --force           Auto-ersätt SAFE-filer utan att fråga
#   --templates DIR   Override templates-path (alt. STACK_TEMPLATES_DIR env)
#
# Beteende:
#   Uppdaterar ramverks-filer (roller, hantverk, scripts, MALL-filer) UTAN
#   att skriva över författarens content (CLAUDE.md, manuskript/, learnings.md,
#   plot/koncept/stil/forlag/meta/varld-content, story-graph med content).
#
# Tre kategorier:
#   1. SAFE TO REPLACE  — hantverk, scripts, roles, docs/
#   2. DIFF + PROMPT    — process.md, canon.md, tics-katalog.md, tools.md
#   3. NEVER TOUCH      — CLAUDE.md, manuskript/, learnings.md, all bok-content
#
# Säkerhetskopia skapas i .cache/upgrade-backup-<datum>/ före varje ändring.

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
skip() { printf "%s\n" "${YELLOW}SKIP:${NC} $*"; }

usage() {
    sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'
    exit "${1:-1}"
}

# ---------- argparse ----------
DRY_RUN=0
FORCE=0
TEMPLATES_OVERRIDE=""
POSITIONAL=()

while [ "$#" -gt 0 ]; do
    case "$1" in
        -h|--help) usage 0 ;;
        --dry-run) DRY_RUN=1; shift ;;
        --force)   FORCE=1; shift ;;
        --templates)
            [ "$#" -ge 2 ] || { err "--templates kräver argument"; exit 2; }
            TEMPLATES_OVERRIDE="$2"; shift 2 ;;
        --templates=*) TEMPLATES_OVERRIDE="${1#*=}"; shift ;;
        --) shift; while [ "$#" -gt 0 ]; do POSITIONAL+=("$1"); shift; done ;;
        -*) err "Okänd flagga: $1"; usage 2 ;;
        *) POSITIONAL+=("$1"); shift ;;
    esac
done

[ "${#POSITIONAL[@]}" -ge 1 ] || { err "Saknar PROJECT_DIR"; usage 2; }
PROJECT_DIR="${POSITIONAL[0]}"
case "$PROJECT_DIR" in
    "~"|"~/"*) PROJECT_DIR="${HOME}${PROJECT_DIR#~}" ;;
esac

# ---------- validera project ----------
[ -d "$PROJECT_DIR" ]              || { err "$PROJECT_DIR finns inte eller är ej katalog"; exit 3; }
[ -d "$PROJECT_DIR/.context" ]     || { err "$PROJECT_DIR/.context saknas — inte ett writing-stack-projekt?"; exit 3; }
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"

# ---------- hitta templates/ ----------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -n "$TEMPLATES_OVERRIDE" ]; then
    TEMPLATES_DIR="$TEMPLATES_OVERRIDE"
elif [ -n "${STACK_TEMPLATES_DIR:-}" ]; then
    TEMPLATES_DIR="$STACK_TEMPLATES_DIR"
else
    TEMPLATES_DIR="$SCRIPT_DIR/templates"
fi
[ -d "$TEMPLATES_DIR" ] || { err "Templates saknas: $TEMPLATES_DIR"; exit 3; }
TEMPLATES_DIR="$(cd "$TEMPLATES_DIR" && pwd)"

# ---------- konstanter ----------
DATUM="$(date +%Y-%m-%d)"
BACKUP_DIR="$PROJECT_DIR/.cache/upgrade-backup-$DATUM"
REPORT_FILE="$PROJECT_DIR/.context/upgrade-rapport-$DATUM.md"

# ---------- kategori-klassificering ----------
# Returnerar: SAFE | DIFF | NEVER
# $1 = relativ path från projekt-root (t.ex. ".context/roles/writer.md")
classify() {
    local rel="$1"

    # NEVER TOUCH — författarens content
    case "$rel" in
        CLAUDE.md) echo NEVER; return ;;
        manuskript/*) echo NEVER; return ;;
        .context/learnings.md) echo NEVER; return ;;
        .context/koncept/*.md|\
        .context/plot/*.md|.context/plot/*/*.md|\
        .context/stil/*.md|.context/stil/*/*.md|\
        .context/forlag/*.md|.context/forlag/*/*.md|\
        .context/meta/*.md|.context/meta/*/*.md|\
        .context/varld/*.md)
            # README.md i dessa kataloger är ramverks-content
            case "$rel" in
                */README.md) echo SAFE; return ;;
                *) echo NEVER; return ;;
            esac ;;
        .context/*-rapporter/*) echo NEVER; return ;;
        .context/audiobook/*|.context/marknadsforing/*|.context/prosa-anteckningar/*|\
        .context/research-dossier/*)
            case "$rel" in
                */README.md) echo SAFE; return ;;
                *) echo NEVER; return ;;
            esac ;;
        .context/story-graph/character-deepening/MALL.md|\
        .context/story-graph/character-deepening/README.md)
            echo SAFE; return ;;
        .context/story-graph/character-deepening/*)
            echo NEVER; return ;;
        .context/story-graph/*.json)
            # JSON: om target innehåller content (mer än {} eller []), NEVER
            local full="$PROJECT_DIR/$rel"
            if [ -f "$full" ]; then
                local content
                content="$(tr -d '[:space:]' < "$full")"
                if [ "$content" = "{}" ] || [ "$content" = "[]" ] || [ -z "$content" ]; then
                    echo SAFE; return
                else
                    echo NEVER; return
                fi
            else
                echo SAFE; return
            fi ;;
    esac

    # DIFF + PROMPT — ramverks-content med möjlig lokal anpassning
    case "$rel" in
        .context/process.md|.context/canon.md|.context/tics-katalog.md|.context/tools.md|.context/README.md)
            echo DIFF; return ;;
    esac

    # SAFE — ramverks-filer
    case "$rel" in
        .context/hantverk/*|\
        .context/roles/*|\
        .context/story-graph/style-guide.md|\
        .context/story-graph/consistency-checks.md|\
        .context/story-graph/knowledge-matrix.md|\
        .context/story-graph/themes.md|\
        .context/story-graph/threads.md|\
        scripts/*|\
        docs/*|\
        README.md|\
        .gitignore)
            echo SAFE; return ;;
    esac

    # Default: DIFF (säkert)
    echo DIFF
}

# ---------- helpers ----------
backup_file() {
    local rel="$1" full="$PROJECT_DIR/$1"
    [ -f "$full" ] || return 0
    if [ "$DRY_RUN" -eq 1 ]; then return 0; fi
    mkdir -p "$BACKUP_DIR/$(dirname "$rel")"
    cp "$full" "$BACKUP_DIR/$rel"
}

files_equal() {
    cmp -s "$1" "$2"
}

# ---------- collect ändringar ----------
declare -a UPGRADED=()
declare -a NEW_FILES=()
declare -a KEPT_DIFF=()
declare -a SKIPPED_NEVER=()
declare -a UNCHANGED=()
declare -a PROMPTED_REPLACED=()

# ---------- summary banner ----------
cat <<EOF
${BOLD}Programmatic Writing Stack — upgrade${NC}
  PROJECT    : $PROJECT_DIR
  TEMPLATES  : $TEMPLATES_DIR
  DATUM      : $DATUM
  DRY-RUN    : $([ "$DRY_RUN" -eq 1 ] && echo "ja" || echo "nej")
  FORCE      : $([ "$FORCE" -eq 1 ] && echo "ja (auto-ersätt SAFE)" || echo "nej")
  BACKUP     : $BACKUP_DIR

EOF

# ---------- skapa backup-dir ----------
if [ "$DRY_RUN" -eq 0 ]; then
    mkdir -p "$BACKUP_DIR"
fi

# ---------- iterera templates ----------
while IFS= read -r -d '' -u 4 src; do
    rel="${src#$TEMPLATES_DIR/}"
    target="$PROJECT_DIR/$rel"
    cat="$(classify "$rel")"

    if [ ! -e "$target" ]; then
        # Ny fil — lägg till om inte NEVER
        if [ "$cat" = "NEVER" ]; then
            SKIPPED_NEVER+=("$rel (ny, NEVER-kategori)")
            continue
        fi
        if [ "$DRY_RUN" -eq 1 ]; then
            info "NY: $rel"
        else
            mkdir -p "$(dirname "$target")"
            cp "$src" "$target"
            ok "NY: $rel"
        fi
        NEW_FILES+=("$rel")
        continue
    fi

    # Target finns
    if files_equal "$src" "$target"; then
        UNCHANGED+=("$rel")
        continue
    fi

    case "$cat" in
        NEVER)
            skip "$rel (NEVER TOUCH — författarens content)"
            SKIPPED_NEVER+=("$rel")
            ;;
        SAFE)
            if [ "$DRY_RUN" -eq 1 ]; then
                info "SAFE-replace: $rel"
            else
                backup_file "$rel"
                cp "$src" "$target"
                ok "Uppdaterade SAFE: $rel"
            fi
            UPGRADED+=("$rel")
            ;;
        DIFF)
            if [ "$DRY_RUN" -eq 1 ]; then
                info "DIFF-prompt: $rel (skulle fråga)"
                KEPT_DIFF+=("$rel (dry-run)")
                continue
            fi
            echo
            warn "DIFF i $rel — målet är editerat (eller äldre version)"
            echo "  Templates : $src"
            echo "  Target    : $target"
            # visa kort diff (max 40 rader)
            diff -u "$target" "$src" | head -n 40 || true
            echo
            if [ "$FORCE" -eq 1 ]; then
                # även med --force vågar vi inte tysta override DIFF-filer
                warn "  --force ignoreras för DIFF-kategori (säkerhet). Default = behåll."
                KEPT_DIFF+=("$rel")
                continue
            fi
            printf "  [b]ehåll / [e]rsätt / [s]kippa? (default: b): "
            answer=""
            # Försök läsa från tty; fall tillbaka på stdin om tty inte finns
            set +e
            if exec 3</dev/tty 2>/dev/null; then
                read -r answer <&3
                exec 3<&- 2>/dev/null
            else
                read -r answer
            fi
            set -e
            : "${answer:=b}"
            answer_lc="$(printf '%s' "${answer:-b}" | tr '[:upper:]' '[:lower:]')"
            case "$answer_lc" in
                e|ersätt|ersatt|replace)
                    backup_file "$rel"
                    cp "$src" "$target"
                    ok "Ersatte (efter prompt): $rel"
                    PROMPTED_REPLACED+=("$rel")
                    ;;
                *)
                    skip "Behöll $rel"
                    KEPT_DIFF+=("$rel")
                    ;;
            esac
            ;;
    esac
done 4< <(find "$TEMPLATES_DIR" -type f \
    ! -path '*/.git/*' \
    ! -name '.DS_Store' \
    -print0)

# ---------- städa tom backup ----------
if [ "$DRY_RUN" -eq 0 ] && [ -d "$BACKUP_DIR" ] && [ -z "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]; then
    rmdir "$BACKUP_DIR"
fi

# ---------- rapport ----------
write_report() {
    local f="$1"
    {
        echo "# Upgrade-rapport — $DATUM"
        echo
        echo "**Projekt:** \`$PROJECT_DIR\`"
        echo "**Templates:** \`$TEMPLATES_DIR\`"
        echo "**Dry-run:** $([ "$DRY_RUN" -eq 1 ] && echo "ja" || echo "nej")"
        echo "**Backup:** \`$BACKUP_DIR\`"
        echo
        echo "## Sammanfattning"
        echo
        echo "| Kategori | Antal |"
        echo "|---|---|"
        echo "| Uppdaterade (SAFE) | ${#UPGRADED[@]} |"
        echo "| Nya filer tillagda | ${#NEW_FILES[@]} |"
        echo "| Ersatta efter prompt (DIFF) | ${#PROMPTED_REPLACED[@]} |"
        echo "| Behållna (DIFF, ej ersatta) | ${#KEPT_DIFF[@]} |"
        echo "| Skippade (NEVER TOUCH) | ${#SKIPPED_NEVER[@]} |"
        echo "| Oförändrade (identisk) | ${#UNCHANGED[@]} |"
        echo
        for label in "Uppdaterade SAFE:UPGRADED" "Nya filer:NEW_FILES" "Ersatta efter prompt:PROMPTED_REPLACED" "Behållna (DIFF):KEPT_DIFF" "Skippade NEVER:SKIPPED_NEVER"; do
            name="${label%%:*}"
            var="${label##*:}"
            arr=()
            eval "if [ \"\${#${var}[@]}\" -gt 0 ]; then arr=(\"\${${var}[@]}\"); fi"
            if [ "${#arr[@]}" -gt 0 ]; then
                echo "## $name"
                echo
                for item in "${arr[@]}"; do
                    echo "- \`$item\`"
                done
                echo
            fi
        done
        if [ "${#KEPT_DIFF[@]}" -gt 0 ]; then
            echo "## Nästa steg"
            echo
            echo "DIFF-filer behölls. Om du vill merge:a in nya ändringar manuellt:"
            echo "\`\`\`bash"
            for f in "${KEPT_DIFF[@]}"; do
                echo "diff -u $PROJECT_DIR/$f $TEMPLATES_DIR/$f"
            done
            echo "\`\`\`"
        fi
    } > "$f"
}

if [ "$DRY_RUN" -eq 0 ]; then
    mkdir -p "$(dirname "$REPORT_FILE")"
    write_report "$REPORT_FILE"
fi

# ---------- slutsammanfattning ----------
echo
echo "${BOLD}Slutrapport${NC}"
echo "  Uppdaterade (SAFE)        : ${#UPGRADED[@]}"
echo "  Nya filer                 : ${#NEW_FILES[@]}"
echo "  Ersatta efter prompt      : ${#PROMPTED_REPLACED[@]}"
echo "  Behållna (DIFF)           : ${#KEPT_DIFF[@]}"
echo "  Skippade (NEVER TOUCH)    : ${#SKIPPED_NEVER[@]}"
echo "  Oförändrade               : ${#UNCHANGED[@]}"
echo

if [ "$DRY_RUN" -eq 1 ]; then
    info "Dry-run — inga ändringar gjorda. Kör utan --dry-run för riktig uppgradering."
else
    ok "Klar. Rapport: $REPORT_FILE"
    if [ -d "$BACKUP_DIR" ]; then
        ok "Backup:  $BACKUP_DIR"
    fi
fi
