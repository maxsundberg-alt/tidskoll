#!/bin/bash
# Tidskoll, skärmdumpsnivån (macOS). Tar en skärmdump och loggar app, fönster
# och adress var femte sekund. Startas av launchd via Tidskoll.app (se wrapper.c:
# behörigheten att spela in skärmen kräver en riktig app).
#
# Bygger på capture-loop.sh i screenwatch-kit av Muhammad Ali (MIT-licens),
# https://github.com/tabani-png/screenwatch-kit
set -u

BASE="${TIDSKOLL_SKARM:-$HOME/tidskoll/skarm}"
MAX_TICKS="${TIDSKOLL_VARV:-0}"   # 0 = för alltid; ett tal = sluta efter så många varv (för test)
LOG_MAX_BYTES=1048576   # korta daemon.log när den passerar 1 MB, behåll slutet
LOG_KEEP_LINES=2000
INTERVAL=5
IDLE_SKIP_SECS=90       # skip capture if no keyboard/mouse input for this long
RETAIN_DAYS=30          # prune image folders older than this (notes never pruned)
WIDTH=1568              # AI vision max useful long edge — bigger is wasted
WEBP_QUALITY=35         # ~40-60KB/frame, verified legible
JPEG_QUALITY=55         # fallback when ffmpeg is unavailable

# launchd doesn't inherit your shell PATH — hitta encoders med absoluta vägar.
# Prioritet: cwebp (minst, ~40KB) → ffmpeg MED libwebp → annars sips JPEG (alltid
# på macOS, ~150-230KB). Många homebrew-ffmpeg saknar webp-encoder — vi testar det,
# litar inte på att ffmpeg finns = webp finns.
CWEBP=""
for c in "$(command -v cwebp 2>/dev/null)" /opt/homebrew/bin/cwebp /usr/local/bin/cwebp; do
  [ -n "$c" ] && [ -x "$c" ] && CWEBP="$c" && break
done
FFMPEG=""
for c in "$(command -v ffmpeg 2>/dev/null)" /opt/homebrew/bin/ffmpeg /usr/local/bin/ffmpeg; do
  [ -n "$c" ] && [ -x "$c" ] && FFMPEG="$c" && break
done
FFMPEG_WEBP=""
if [ -n "$FFMPEG" ] && "$FFMPEG" -hide_banner -encoders 2>/dev/null | grep -q webp; then
  FFMPEG_WEBP=1
fi

# Koda ner en PNG till minsta tillgängliga läsbara format. Skriver ut sökvägen
# till den skapade filen (eller inget vid fel).
encode_frame() {
  # $1 = källa-png, $2 = mål-mapp, $3 = tidsstämpel
  if [ -n "$CWEBP" ]; then
    if "$CWEBP" -quiet -q "$WEBP_QUALITY" -resize "$WIDTH" 0 "$1" -o "$2/$3.webp" 2>>"$BASE/daemon.log"; then
      printf '%s' "$2/$3.webp"; return 0
    fi
  fi
  if [ -n "$FFMPEG_WEBP" ]; then
    if "$FFMPEG" -y -loglevel error -i "$1" -vf "scale=$WIDTH:-2" -quality "$WEBP_QUALITY" "$2/$3.webp" 2>>"$BASE/daemon.log"; then
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
  # Prints: app <TAB> window_title. Only System Events here — browser
  # dictionaries are referenced in get_url so a missing browser can't
  # break compilation of this script.
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
  # $1 = frontmost app name. Separate per-browser scripts: AppleScript
  # resolves an app's dictionary at COMPILE time, so mentioning an
  # uninstalled browser is a syntax error that kills the whole script.
  case "$1" in
    "Google Chrome"|"Brave Browser"|"Arc"|"Microsoft Edge"|"Vivaldi")
      osascript -e "tell application \"$1\" to get URL of active tab of front window" 2>/dev/null ;;
    "Safari")
      osascript -e 'tell application "Safari" to get URL of front document' 2>/dev/null ;;
  esac
}

# Pauslistan: hoppa över BILDEN (app och fönster loggas ändå) när appnamnet eller
# adressen innehåller en rad i ~/tidskoll/pauslista.txt. En delsträng per rad,
# # är kommentar. Filen läses varje varv, så ändringar gäller direkt.
SENSITIVE_FILE="$HOME/tidskoll/pauslista.txt"
is_sensitive() {
  # $1=app, $2=url. Retur 0 (sant) vid träff.
  [ -f "$SENSITIVE_FILE" ] || return 1
  local pat
  while IFS= read -r pat || [ -n "$pat" ]; do
    case "$pat" in ''|'#'*) continue ;; esac
    case "$1" in *"$pat"*) return 0 ;; esac
    [ -n "${2:-}" ] && case "$2" in *"$pat"*) return 0 ;; esac
  done < "$SENSITIVE_FILE"
  return 1
}

n_ticks=0
while true; do
  if [ "$MAX_TICKS" -gt 0 ]; then
    [ "$n_ticks" -ge "$MAX_TICKS" ] && exit 0
    n_ticks=$((n_ticks + 1))
  fi
  sleep "$INTERVAL"

  idle=$(ioreg -c IOHIDSystem 2>/dev/null | awk '/HIDIdleTime/ {print int($NF/1000000000); exit}')
  if [ "${idle:-0}" -ge "$IDLE_SKIP_SECS" ]; then continue; fi

  day=$(date +%F)
  dir="$BASE/days/$day"
  mkdir -p "$dir"
  ts=$(date +%H-%M-%S)
  epoch=$(date +%s)

  meta=$(get_meta)
  app=$(printf '%s' "$meta" | cut -f1)
  win=$(printf '%s' "$meta" | cut -f2)
  url=$(get_url "$app")

  # Dedupe: unchanged app+window+url → metadata every tick, image every 6th.
  # Känslig app/url → hoppa över bilden helt (metadata loggas ändå nedan).
  state="$app|$win|$url"
  saved=0
  if { [ "$state" != "${last_state:-}" ] || [ $(( ${tick:-0} % 6 )) -eq 0 ]; } && ! is_sensitive "$app" "$url"; then
    # NOTE: never a dot-prefixed temp name — screencapture refuses hidden
    # paths with an error identical to a permissions denial.
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
    find "$BASE/days" -mindepth 1 -maxdepth 1 -type d -mtime +"$RETAIN_DAYS" \
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
