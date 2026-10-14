#!/bin/bash
# Tidskoll, skärmdumpar (macOS). Tar en skärmdump och loggar app, fönster
# och adress var femte sekund. Startas av launchd via Tidskoll.app (se wrapper.c:
# behörigheten att spela in skärmen kräver en riktig app).
#
# Bygger på capture-loop.sh i screenwatch-kit av Muhammad Ali (MIT-licens),
# https://github.com/tabani-png/screenwatch-kit
set -u

BASE="$HOME/tidskoll/skarm"
LOG_MAX_BYTES=1048576   # korta daemon.log när den passerar 1 MB och behåll slutet
LOG_KEEP_LINES=2000
INTERVAL=5
IDLE_SKIP_SECS=90       # ingen skärmdump om tangentbord och mus varit orörda så här länge
RETAIN_DAYS=30          # dagsmappar (bilder och logg) äldre än så raderas, anteckningarna sparas
WIDTH=1568              # bredare än så har AI-modeller ingen nytta av
WEBP_QUALITY=35         # ger 40–60 kB per bild med läsbar text
JPEG_QUALITY=55         # när cwebp saknas

# launchd ärver inte skalets PATH, så cwebp letas upp med fullständiga sökvägar.
# cwebp (installeras med Homebrew) ger runt 40 kB per bild. Saknas det används macOS
# egen sips och JPEG, som ger 150–230 kB.
CWEBP=""
for c in "$(command -v cwebp 2>/dev/null)" /opt/homebrew/bin/cwebp /usr/local/bin/cwebp; do
  [ -n "$c" ] && [ -x "$c" ] && CWEBP="$c" && break
done

# Komprimera en PNG till WebP, eller JPEG om cwebp saknas. Skriver ut sökvägen
# till den nya filen, eller ingenting om det misslyckas.
encode_frame() {
  # $1 = PNG-källfil, $2 = målmapp, $3 = tidsstämpel
  if [ -n "$CWEBP" ]; then
    if "$CWEBP" -quiet -q "$WEBP_QUALITY" -resize "$WIDTH" 0 "$1" -o "$2/$3.webp" 2>>"$BASE/daemon.log"; then
      printf '%s' "$2/$3.webp"; return 0
    fi
  fi
  if sips -s format jpeg -s formatOptions "$JPEG_QUALITY" --resampleWidth "$WIDTH" "$1" --out "$2/$3.jpg" >/dev/null 2>>"$BASE/daemon.log"; then
    printf '%s' "$2/$3.jpg"; return 0
  fi
  return 1
}

last_prune_day=""

get_meta() {
  # Skriver ut: app <TAB> fönstertitel. Bara System Events här. Webbläsarna frågas
  # i get_url, så att en webbläsare som inte är installerad inte kan stoppa skriptet.
  osascript <<'EOS' 2>>"$BASE/daemon.log"
tell application "System Events"
  set p to first application process whose frontmost is true
  set appName to name of p
  set winTitle to ""
  try
    set winTitle to name of front window of p
  end try
end tell
return appName & tab & winTitle
EOS
}

get_url() {
  # $1 = den aktiva appens namn. Ett eget anrop per webbläsare: AppleScript slår upp
  # appens ordlista redan när skriptet kompileras, så ett skript som nämner en
  # webbläsare som inte är installerad går inte att köra alls.
  case "$1" in
    "Google Chrome"|"Brave Browser"|"Arc"|"Microsoft Edge"|"Vivaldi")
      osascript -e "tell application \"$1\" to get URL of active tab of front window" 2>/dev/null ;;
    "Safari")
      osascript -e 'tell application "Safari" to get URL of front document' 2>/dev/null ;;
  esac
}

# Pauslistan: ingen bild tas när appnamnet eller adressen innehåller en rad i
# ~/tidskoll/pauslista.txt. App och fönster loggas ändå. En bit text per rad, rader
# som börjar med # räknas inte. Filen läses varje varv, så ändringar gäller direkt.
SENSITIVE_FILE="$HOME/tidskoll/pauslista.txt"
is_sensitive() {
  # $1 = app, $2 = adress. Returnerar 0 (sant) vid träff.
  [ -f "$SENSITIVE_FILE" ] || return 1
  local pat
  while IFS= read -r pat || [ -n "$pat" ]; do
    case "$pat" in ''|'#'*) continue ;; esac
    case "$1" in *"$pat"*) return 0 ;; esac
    [ -n "${2:-}" ] && case "$2" in *"$pat"*) return 0 ;; esac
  done < "$SENSITIVE_FILE"
  return 1
}

while true; do
  sleep "$INTERVAL"

  idle=$(ioreg -c IOHIDSystem 2>/dev/null | awk '/HIDIdleTime/ {print int($NF/1000000000); exit}')
  if [ "${idle:-0}" -ge "$IDLE_SKIP_SECS" ]; then continue; fi

  day=$(date +%F)
  dir="$BASE/dagar/$day"
  mkdir -p "$dir"
  ts=$(date +%H-%M-%S)
  epoch=$(date +%s)

  meta=$(get_meta)
  app=$(printf '%s' "$meta" | cut -f1)
  win=$(printf '%s' "$meta" | cut -f2)
  url=$(get_url "$app")

  # Är app, fönster och adress oförändrade loggas raden varje varv men bilden bara
  # vart sjätte. Står appen eller adressen på pauslistan tas ingen bild alls.
  state="$app|$win|$url"
  saved=0
  if { [ "$state" != "${last_state:-}" ] || [ $(( ${tick:-0} % 6 )) -eq 0 ]; } && ! is_sensitive "$app" "$url"; then
    # Aldrig ett filnamn som börjar med punkt: screencapture vägrar skriva dit, med
    # samma felmeddelande som när behörigheten saknas.
    tmp="$dir/tmp-capture.png"
    if screencapture -x -m -t png "$tmp" 2>>"$BASE/daemon.log"; then
      out="$(encode_frame "$tmp" "$dir" "$ts")"
      rm -f "$tmp"
      [ -n "$out" ] && [ -s "$out" ] && saved=1
    fi
  fi
  last_state="$state"
  tick=$(( ${tick:-0} + 1 ))

  APP="$app" WIN="$win" URL="$url" TS="$ts" EPOCH="$epoch" IMG="$saved" \
  python3 - >> "$dir/log.jsonl" <<'EOF'
import json, os
print(json.dumps({
  "t": os.environ["TS"], "epoch": int(os.environ["EPOCH"]),
  "app": os.environ["APP"], "window": os.environ["WIN"],
  "url": os.environ["URL"], "img": os.environ["IMG"] == "1",
}))
EOF

  if [ "$day" != "$last_prune_day" ]; then
    find "$BASE/dagar" -mindepth 1 -maxdepth 1 -type d -mtime +"$RETAIN_DAYS" \
      -exec rm -rf {} + 2>/dev/null
    # Korta loggen så att gamla fel inte ser ut som nya. Skriv över på plats,
    # så att öppna omdirigeringar fortsätter skriva till samma fil.
    if [ -f "$BASE/daemon.log" ] && [ "$(wc -c <"$BASE/daemon.log")" -gt "$LOG_MAX_BYTES" ]; then
      tail -n "$LOG_KEEP_LINES" "$BASE/daemon.log" >"$BASE/daemon.log.tmp" 2>/dev/null \
        && cat "$BASE/daemon.log.tmp" >"$BASE/daemon.log" \
        && rm -f "$BASE/daemon.log.tmp"
    fi
    last_prune_day="$day"
  fi
done
