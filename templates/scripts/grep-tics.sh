#!/usr/bin/env bash
#
# grep-tics.sh — Mekanisk första-pass-tics-detektor för "Marken under marken"
#
# Användning:
#   ./scripts/grep-tics.sh                          # alla kapitel i manuskript/
#   ./scripts/grep-tics.sh manuskript/kapitel-01.md # en fil
#   ./scripts/grep-tics.sh manuskript/kap*.md       # glob
#
# Output: kategoriserad rapport till stdout, med radnr per träff.
# Träffar över etablerat "tak" markeras med [ÖVER TAK].
#
# Referens: .context/tics-katalog.md
#
# Designprinciper:
#  - Mekanisk första-pass — alla träffar ska reviewas, inte autofixas
#  - Per-kategori tak (canon-fixerat eller empiriskt)
#  - Kategorierna matchar tics-katalog.md numrering 1-22
#  - Inga falsk-positiva-elimineringar — bättre att flagga för mycket

set -euo pipefail

# ─────────────────────────────────────────────────────────────
# Konfiguration
# ─────────────────────────────────────────────────────────────

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"
MANUSKRIPT_DIR="${PROJECT_ROOT}/manuskript"

# Färger för terminaloutput (men inte i pipe)
if [[ -t 1 ]]; then
    RED=$'\033[0;31m'
    YELLOW=$'\033[0;33m'
    GREEN=$'\033[0;32m'
    CYAN=$'\033[0;36m'
    BOLD=$'\033[1m'
    RESET=$'\033[0m'
else
    RED=""; YELLOW=""; GREEN=""; CYAN=""; BOLD=""; RESET=""
fi

# ─────────────────────────────────────────────────────────────
# Helper: kör grep mot fil + visa kategori
# Args: $1 = kategorinamn, $2 = regex, $3 = fil, [$4 = tak per fil]
# ─────────────────────────────────────────────────────────────

grep_category() {
    local label="$1"
    local pattern="$2"
    local file="$3"
    local tak="${4:-}"

    # -E extended regex, -n line numbers, -i case-insensitive ej default
    local matches
    matches=$(grep -nE "${pattern}" "${file}" 2>/dev/null || true)

    if [[ -z "${matches}" ]]; then
        return 0
    fi

    local count
    count=$(echo "${matches}" | wc -l | tr -d ' ')

    # Tak-kontroll
    local flag=""
    if [[ -n "${tak}" ]] && (( count > tak )); then
        flag=" ${RED}[ÖVER TAK: ${count} > ${tak}]${RESET}"
    fi

    echo ""
    echo "  ${BOLD}${label}${RESET} (${count} träff${flag})"
    echo "${matches}" | sed 's/^/    /'
}

# ─────────────────────────────────────────────────────────────
# Kör alla tics-kategorier mot en fil
# ─────────────────────────────────────────────────────────────

scan_file() {
    local file="$1"
    local filename
    filename=$(basename "${file}")

    echo ""
    echo "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo "${CYAN}${BOLD} ${filename}${RESET}"
    echo "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

    # ── 1. Doft-tics (variation krävs) ──
    grep_category "1. Doft-tics" \
        '\bluktade\b' "${file}"

    # ── 2. "Mm." dialog-tic (tak ~5 i hela boken, ~1 per kapitel) ──
    grep_category "2. Mm. dialog-tic [tak 1/kap]" \
        '"Mm\."' "${file}" 1

    # ── 3. "nickade" (BLOCKERANDE — tak ~2/kap) ──
    grep_category "3. nickade [tak 2/kap]" \
        '\bnickade\b' "${file}" 2

    # ── 4. "räknade" (Anna-signum — tak 2-3/Anna-kap) ──
    grep_category "4. räknade [Anna-signum, kontrollera POV]" \
        '\bräknade\b' "${file}" 3

    # ── 5. "tre/fyra/fem sekunder" (sekund-räkning — tak 2/kap) ──
    grep_category "5. sekund-räkning [tak 2/kap]" \
        '\b(två|tre|fyra|fem|sex|sju|åtta|nio|tio) sekunder\b' "${file}" 2

    # ── 6. "exakt" (kalibrera intentionalitet) ──
    grep_category "6. exakt [verifiera intentionalitet]" \
        '\bexakt\b' "${file}"

    # ── 7. Bilmärken (Volvo = polis-canon — variera övriga) ──
    grep_category "7. Volvo (canon för polis — variera turistbilar)" \
        'Volvo (XC60|XC90|V90|V70|XC40|XC70|S60|S80)' "${file}"

    grep_category "7b. Andra bilmärken" \
        '\b(BMW|Audi|Tesla|Mercedes|Skoda|Toyota|Hyundai|Kia|Saab)\b' "${file}"

    # ── 8. Klädmärkes-tics (funktionellt eller stryk) ──
    grep_category "8. Klädmärken" \
        '\b(Acne|Common Projects|Filippa K|COS|Toteme|Carhartt|Aspesi|Hope|Tiger of Sweden|Norse Projects|Stutterheim)\b' "${file}"

    # ── 9. Klockslag (verifiera funktion) ──
    grep_category "9. Klockslag [verifiera funktion]" \
        '\b(klockan |kl\.? )[0-9]{1,2}([.:][0-9]{2})?\b' "${file}"

    # ── 10. Tom Clancy / militär-precision ──
    grep_category "10. Militär-precision-tics" \
        '\b(trettiotvå|fyrtiotre|sextiosju|åttiotvå|hundrafemtio) (sekunder|minuter|gånger)|aviator|Operation [A-ZÅÄÖ]|\bRondo\b|gör det blint' "${file}"

    # ── 11. Aforismer i karaktärs-tankar ──
    grep_category "11. Aforism-i-tanke [FÖRBJUDET]" \
        '\bär värre än\b|\bDet enda som\b|\bSanningen om\b|\bSanningen var att\b|\bFaktum är att\b' "${file}"

    # ── 12. Anglicism / svengelska ──
    grep_category "12. Anglicism" \
        '"(Yes|Okay|Alright|Sorry)\b|\b(literally|absolutely|obviously)\b' "${file}"

    # ── 13. Aforism-/utfyllnads-tics ──
    grep_category "13. Utfyllnad" \
        '\bför säkerhets skull\b|\bav en slump\b|\bpå något sätt\b|\bpå sätt och vis\b|\bliksom\b' "${file}"

    # ── 14. Andetag som tidsmått (Daniel-exklusiv) ──
    grep_category "14. Andetag-tidsmått [Daniel-exklusiv]" \
        '\b(djupt andetag|drog efter andan|tog ett andetag|hörde sin egen andning)\b' "${file}" 1

    # ── 15. "som om" — överanvänt liknelse-prefix ──
    grep_category "15. som om [tak 2/kap]" \
        '\bsom om\b' "${file}" 2

    # ── 16. Tystnad-tic ──
    grep_category "16. Tystnad-tic [tak 1/kap]" \
        '\b(det blev tyst|tystnaden|tystnade)\b' "${file}" 1

    # ── 17. Författar-essä-fraser ──
    grep_category "17. Författar-essä [FÖRBJUDET]" \
        '^Sanningen var att|^Faktum är att|^I efterhand|^Han skulle senare förstå|^Det fanns en tid då|\bdet visste han på samma sätt som\b' "${file}"

    # ── 18. Verkliga personer (namn-blacklist) ──
    grep_category "18. Verkliga politiker/profiler [BLOCKERANDE]" \
        '\b(Åsa Hallin|Magdalena Andersson|Ulf Kristersson|Nooshi Dadgostar|Ebba Busch|Jimmie Åkesson|Annie Lööf|Märta Stenevi|Romina Pourmokhtari|Daniel Helldén|Meit Fohlin|Ali Esbati|Tobias Baudin|Johan Pehrson|Muharrem Demirok|Jonas Sjöstedt|Sverker Olofsson)\b' "${file}"

    grep_category "18b. PR-byråer (verkliga — verifiera kontext)" \
        '\b(JKL|Kekst CNC|Westander|Springtime|Diplomat Communications|Gullers|Hallvarsson|Prime Weber Shandwick|H&H Group|Kreab|Reform Society)\b' "${file}"

    # ── 19. Fakta-fälla-tics ──
    grep_category "19. Fakta-fällor [BLOCKERANDE]" \
        'Stockholmsskyltar|JKL\b|SGU.*Villavägen|Tetrao.*Birger Jarls|Reddit' "${file}"

    # ── 20. Geografi-fälla-tics (Gotland) ──
    grep_category "20. Geografi-fällor [BLOCKERANDE]" \
        '\bKlinte\b[^h]|Eskelhem.*sydost|Stora Karlsö.*slumpvis|Hamnkaféet.*juni|Smöjen.*Klintehamn|Hejdeby.*18 km|BMW.*polis' "${file}"

    # ── 21. POV-läckage: signum i fel kapitel ──
    # Detta är heuristik — vi måste veta vilket kapitel som har vilken POV
    # Riktlinje: writern dispatcheras med POV-spec, men flagga signum-cross-over
    grep_category "21. POV-signum (verifiera mot kapitel-POV)" \
        '\b(bakhuvud|hörde sin egen andning|mage-vet|halsband|nyckelben|hårfäste|Carhartt-byxor)\b' "${file}"

    # ── 22. Tre-ords-bindestreck (ofta påhittade kompositum) ──
    grep_category "22. Tre-ord-bindestreck [SAOL-verifiera]" \
        '[a-zåäöA-ZÅÄÖ]+-[a-zåäöA-ZÅÄÖ]+-[a-zåäöA-ZÅÄÖ]+' "${file}"
}

# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

# Argument-hantering
if [[ $# -eq 0 ]]; then
    # Inga args: kör alla kapitel + prolog + epilog
    FILES=( "${MANUSKRIPT_DIR}/prolog.md" "${MANUSKRIPT_DIR}"/kapitel-*.md "${MANUSKRIPT_DIR}/epilog.md" )
else
    FILES=( "$@" )
fi

echo "${BOLD}${GREEN}=================================================${RESET}"
echo "${BOLD}${GREEN} TICS-RAPPORT — Marken under marken${RESET}"
echo "${BOLD}${GREEN} $(date '+%Y-%m-%d %H:%M')${RESET}"
echo "${BOLD}${GREEN} Filer: ${#FILES[@]}${RESET}"
echo "${BOLD}${GREEN}=================================================${RESET}"

for file in "${FILES[@]}"; do
    if [[ ! -f "${file}" ]]; then
        echo "${RED}SKIPP: ${file} finns inte${RESET}" >&2
        continue
    fi
    scan_file "${file}"
done

echo ""
echo "${BOLD}${GREEN}=================================================${RESET}"
echo "${BOLD}${GREEN} Klart. Granska alla [ÖVER TAK]-träffar manuellt.${RESET}"
echo "${BOLD}${GREEN} Se .context/tics-katalog.md för regler.${RESET}"
echo "${BOLD}${GREEN}=================================================${RESET}"
