#!/usr/bin/env bash
# Hämta highlights + noter från Apple Books för en given bok.
# Default: "Marken under marken" av Alex Krohn.
#
# Användning:
#   scripts/books-annotations.sh                      # markdown till stdout
#   scripts/books-annotations.sh --json               # JSON-array
#   scripts/books-annotations.sh --since 2026-05-18   # bara nya sen datum
#   scripts/books-annotations.sh --title "Annan bok"  # annan bok
#   scripts/books-annotations.sh --out fil.md         # skriv till fil

set -euo pipefail

ANNO_DB="$HOME/Library/Containers/com.apple.iBooksX/Data/Documents/AEAnnotation"
LIB_DB="$HOME/Library/Containers/com.apple.iBooksX/Data/Documents/BKLibrary"

ANNO_FILE=$(ls "$ANNO_DB"/AEAnnotation_*.sqlite 2>/dev/null | head -1)
LIB_FILE=$(ls "$LIB_DB"/BKLibrary-*.sqlite 2>/dev/null | head -1)

if [[ -z "$ANNO_FILE" || -z "$LIB_FILE" ]]; then
  echo "Hittar inte Apple Books-databaserna." >&2
  exit 1
fi

TITLE="Marken under marken"
FORMAT="md"
SINCE=""
OUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json) FORMAT="json"; shift ;;
    --md)   FORMAT="md"; shift ;;
    --since) SINCE="$2"; shift 2 ;;
    --title) TITLE="$2"; shift 2 ;;
    --out)  OUT="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,11p' "$0"; exit 0 ;;
    *) echo "Okänd flagga: $1" >&2; exit 1 ;;
  esac
done

# Core Data-epok = 2001-01-01 UTC. SQLite-datum = epoch + 978307200.
SINCE_CLAUSE=""
if [[ -n "$SINCE" ]]; then
  SINCE_EPOCH=$(date -j -f "%Y-%m-%d" "$SINCE" "+%s" 2>/dev/null || date -d "$SINCE" "+%s")
  SINCE_CD=$(( SINCE_EPOCH - 978307200 ))
  SINCE_CLAUSE="AND a.ZANNOTATIONCREATIONDATE >= $SINCE_CD"
fi

# Kopiera till temp för att undvika WAL-lås om Books är öppen.
# Viktigt: även -wal och -shm måste med, annars missar vi nyligen tillagda
# kommentarer som inte hunnit checkpointas till huvudfilen.
TMP=$(mktemp -d)
cp "$ANNO_FILE"      "$TMP/anno.sqlite"
cp "$ANNO_FILE-wal"  "$TMP/anno.sqlite-wal" 2>/dev/null || true
cp "$ANNO_FILE-shm"  "$TMP/anno.sqlite-shm" 2>/dev/null || true
cp "$LIB_FILE"       "$TMP/lib.sqlite"
cp "$LIB_FILE-wal"   "$TMP/lib.sqlite-wal"  2>/dev/null || true
cp "$LIB_FILE-shm"   "$TMP/lib.sqlite-shm"  2>/dev/null || true
trap "rm -rf $TMP" EXIT

# Hämta asset-id för bokens titel.
ASSET_ID=$(sqlite3 "$TMP/lib.sqlite" \
  "SELECT ZASSETID FROM ZBKLIBRARYASSET WHERE ZTITLE = '$TITLE' LIMIT 1;")

if [[ -z "$ASSET_ID" ]]; then
  echo "Hittar ingen bok med titel: $TITLE" >&2
  exit 1
fi

SQL="SELECT
  datetime(a.ZANNOTATIONCREATIONDATE + 978307200, 'unixepoch', 'localtime'),
  COALESCE(a.ZANNOTATIONSTYLE, 0),
  COALESCE(a.ZANNOTATIONSELECTEDTEXT, ''),
  COALESCE(a.ZANNOTATIONNOTE, ''),
  COALESCE(a.ZANNOTATIONLOCATION, '')
FROM ZAEANNOTATION a
WHERE a.ZANNOTATIONASSETID = '$ASSET_ID'
  AND a.ZANNOTATIONDELETED = 0
  AND (a.ZANNOTATIONSELECTEDTEXT IS NOT NULL OR a.ZANNOTATIONNOTE IS NOT NULL)
  $SINCE_CLAUSE
ORDER BY a.ZANNOTATIONCREATIONDATE ASC;"

render() {
  if [[ "$FORMAT" == "json" ]]; then
    sqlite3 "$TMP/anno.sqlite" -separator $'\t' "$SQL" | \
      python3 -c '
import sys, json
out=[]
styles={0:"underline",1:"green",2:"blue",3:"yellow",4:"pink",5:"purple"}
for line in sys.stdin:
    parts=line.rstrip("\n").split("\t")
    if len(parts)<5: continue
    date,style,sel,note,loc=parts
    out.append({"date":date,"style":styles.get(int(style),str(style)),"selected":sel,"note":note,"location":loc})
print(json.dumps(out, ensure_ascii=False, indent=2))
'
  else
    echo "# Apple Books — $TITLE"
    echo
    sqlite3 "$TMP/anno.sqlite" -separator $'\t' "$SQL" | \
      python3 -c '
import sys
styles={0:"_underline_",1:"green",2:"blue",3:"yellow",4:"pink",5:"purple"}
n=0
for line in sys.stdin:
    parts=line.rstrip("\n").split("\t")
    if len(parts)<5: continue
    n+=1
    date,style,sel,note,loc=parts
    s=styles.get(int(style),style)
    print(f"## {n}. {date} ({s})")
    if loc: print(f"_loc: {loc}_")
    print()
    if sel:
        for ln in sel.split("\n"):
            print(f"> {ln}")
        print()
    if note:
        print(f"**Not:** {note}")
        print()
print(f"---\n_Totalt: {n} kommentarer_")
'
  fi
}

if [[ -n "$OUT" ]]; then
  render > "$OUT"
  echo "Skrev till: $OUT"
else
  render
fi
