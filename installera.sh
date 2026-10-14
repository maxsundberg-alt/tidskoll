#!/bin/bash
# Tidskoll — installation och styrning (macOS). Går att köra om, inget dubbleras.
#
#   bash installera.sh bas [--kategorier]   ActivityWatch, webbläsarbevakaren, veckorapporten
#                                           och skillen tidskoll. --kategorier ersätter
#                                           ActivityWatchs kategorier med startindelningen.
#   bash installera.sh skarm [--bygg-om]    skärmdumpar var femte sekund (valfri nivå)
#   bash installera.sh blockera             blockering av sajter i alla webbläsare (valfri,
#                                           slås på separat med ~/tidskoll/bin/blockera.sh pa)
#   bash installera.sh status               vad som körs, och dagens data
#   bash installera.sh paus | fortsatt      stoppa eller starta skärmdumparna
#   bash installera.sh avinstallera         ta bort allt utom din data
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$HOME/tidskoll"
BIN="$ROOT/bin"
AGENTS="$HOME/Library/LaunchAgents"
APP="$HOME/Applications/Tidskoll.app"
# ~/.agents/skills är standardmappen (Codex, Cursor, Gemini CLI m.fl.), ~/.claude/skills är Claude Codes.
SKILL_DIRS=("$HOME/.claude/skills/tidskoll" "$HOME/.agents/skills/tidskoll")
GUI="gui/$(id -u)"

say()  { printf '%s\n' "$*"; }
ok()   { printf '  ✓ %s\n' "$*"; }
fail() { printf '  ✗ %s\n' "$*" >&2; exit 1; }

load_agent() {   # $1 = label
  local dst="$AGENTS/$1.plist"
  mkdir -p "$AGENTS"
  sed "s#__HOME__#$HOME#g" "$SRC/launchd/$1.plist" > "$dst"
  launchctl bootout "$GUI/$1" 2>/dev/null || true
  launchctl bootstrap "$GUI" "$dst"
  ok "$1 laddad"
}

aw_up() { curl -sf --max-time 3 http://localhost:5600/api/0/info >/dev/null; }

need_mac() { [ "$(uname)" = "Darwin" ] || fail "Tidskoll fungerar bara på macOS."; }

cmd_bas() {
  need_mac
  say "▸ Tidskoll, grundnivån"

  # 1. ActivityWatch
  if [ ! -d /Applications/ActivityWatch.app ]; then
    if command -v brew >/dev/null; then
      brew install --cask activitywatch
    else
      fail "ActivityWatch saknas och Homebrew finns inte. Ladda ner från https://activitywatch.net/downloads/ och kör sedan om."
    fi
  fi
  ok "ActivityWatch finns i /Applications"
  if ! aw_up; then
    open -a ActivityWatch
    for _ in $(seq 1 60); do aw_up && break; sleep 2; done
  fi
  aw_up || fail "ActivityWatch startade inte. Öppna appen själv och godkänn den om macOS frågar."
  ok "ActivityWatch svarar på localhost:5600"
  # Starta vid inloggning
  osascript -e 'tell application "System Events" to if not (exists login item "ActivityWatch") then make login item at end with properties {path:"/Applications/ActivityWatch.app", hidden:true}' >/dev/null
  ok "ActivityWatch startar vid inloggning"

  # 2. Skript
  mkdir -p "$BIN" "$ROOT/logg" "$ROOT/rapporter"
  cp "$SRC"/bas/*.py "$SRC/skarm/block.py" "$BIN/"
  [ -f "$ROOT/kategorier.json" ] || cp "$SRC/bas/kategorier.json" "$ROOT/kategorier.json"
  ok "skript i $BIN"

  if [ "${1:-}" = "--kategorier" ]; then
    /usr/bin/python3 "$BIN/kategorier.py" tillampa "$ROOT/kategorier.json"
  fi

  # 3. Bakgrundsjobb
  load_agent com.tidskoll.webblasare
  load_agent com.tidskoll.veckorapport

  # 4. Skillen
  for d in "${SKILL_DIRS[@]}"; do
    mkdir -p "$d" && cp "$SRC/skill/tidskoll/SKILL.md" "$d/SKILL.md"
  done
  # Samma instruktioner som vanlig fil, för agenter som inte läser skills.
  cp "$SRC/skill/tidskoll/SKILL.md" "$ROOT/SKILL.md"
  ok "skillen tidskoll i ~/.claude/skills och ~/.agents/skills, och som ~/tidskoll/SKILL.md"

  say ""
  say "Klart. Webbläsarna frågar om lov första gången de används (\"python3 vill styra Safari\"): svara OK."
}

cmd_skarm() {
  need_mac
  say "▸ Tidskoll, skärmdumpar"
  xcode-select -p >/dev/null 2>&1 || fail "Xcode Command Line Tools saknas. Kör: xcode-select --install"
  if ! command -v cwebp >/dev/null && [ ! -x /opt/homebrew/bin/cwebp ] && [ ! -x /usr/local/bin/cwebp ]; then
    if command -v brew >/dev/null; then brew install webp; else say "  (cwebp saknas, bilderna sparas som JPEG och blir ungefär tre gånger större)"; fi
  fi

  mkdir -p "$BIN" "$ROOT/skarm/days" "$ROOT/anteckningar" "$ROOT/logg"
  touch "$ROOT/skarm/daemon.log"
  [ -f "$ROOT/observationer.md" ] || printf '# Återkommande mönster\n\n' > "$ROOT/observationer.md"
  [ -f "$ROOT/pauslista.txt" ] || cp "$SRC/skarm/pauslista.txt" "$ROOT/pauslista.txt"
  cp "$SRC/skarm/capture-loop.sh" "$SRC/skarm/block.py" "$BIN/"
  chmod +x "$BIN/capture-loop.sh"
  ok "skärmdumpsloopen i $BIN, pauslistan i $ROOT/pauslista.txt"

  # Bygg och signera appen bara om den saknas. En ny signatur gör behörigheten ogiltig.
  local sig
  sig="$(codesign -dv "$APP" 2>&1 || true)"
  if [ -x "$APP/Contents/MacOS/tidskoll" ] && [[ "$sig" == *"Identifier=com.tidskoll.skarm"* ]] && [ "${1:-}" != "--bygg-om" ]; then
    ok "Tidskoll.app finns redan (bygger inte om, så behörigheten ligger kvar)"
  else
    mkdir -p "$APP/Contents/MacOS"
    cp "$SRC/skarm/Info.plist" "$APP/Contents/Info.plist"
    cc -o "$APP/Contents/MacOS/tidskoll" "$SRC/skarm/wrapper.c"
    codesign -s - --force --identifier com.tidskoll.skarm "$APP"
    ok "Tidskoll.app byggd och signerad i ~/Applications"
  fi

  load_agent com.tidskoll.skarm
  say ""
  say "Nästa steg, görs i Systeminställningar:"
  say "  Integritet och säkerhet → Skärm- och systemljudinspelning → + → Cmd+Shift+G → ~/Applications → Tidskoll.app"
  say "  Samma sak under Hjälpmedel."
  say "  Starta sedan om: bash installera.sh fortsatt"
}

cmd_blockera() {
  need_mac
  mkdir -p "$BIN"
  cp "$SRC/blockera/blockera.sh" "$BIN/" && chmod +x "$BIN/blockera.sh"
  [ -f "$ROOT/blocklista.txt" ] || cp "$SRC/blockera/blocklista.txt" "$ROOT/blocklista.txt"
  ok "blockera.sh i $BIN, listan i $ROOT/blocklista.txt"
  say "Blocket är inte påslaget än. Gå igenom listan och slå sedan på: bash $BIN/blockera.sh pa"
}

agent_state() {
  local out
  out="$(launchctl print "$GUI/$1" 2>/dev/null)" || { printf 'inte installerad'; return; }
  if [[ "$out" == *"state = running"* ]]; then printf 'kör'; else printf 'laddad, väntar'; fi
}

cmd_status() {
  local day; day="$(date +%F)"
  if aw_up; then say "ActivityWatch:       kör"; else say "ActivityWatch:       svarar inte"; fi
  for l in webblasare veckorapport skarm; do
    printf '%-20s %s\n' "$l:" "$(agent_state com.tidskoll.$l)"
  done
  if [ -d "$ROOT/skarm/days/$day" ]; then
    local n; n=$(find "$ROOT/skarm/days/$day" -name '*.webp' -o -name '*.jpg' | wc -l | tr -d ' ')
    say "Skärmdumpar idag:    $n ($(du -sh "$ROOT/skarm/days/$day" | cut -f1))"
    say "Senaste loggrad:     $(tail -1 "$ROOT/skarm/days/$day/log.jsonl" 2>/dev/null | cut -c1-120)"
  fi
  [ -x "$BIN/blockera.sh" ] && printf '%-20s %s\n' "blockering:" "$(bash "$BIN/blockera.sh" status | head -1 | cut -d' ' -f2-)"
  if [ -s "$ROOT/skarm/daemon.log" ]; then say "Senaste fel:"; tail -3 "$ROOT/skarm/daemon.log" | sed 's/^/  /'; fi
}

cmd_paus()     { launchctl bootout "$GUI/com.tidskoll.skarm" 2>/dev/null && ok "skärmdumparna pausade" || say "redan pausade"; }
cmd_fortsatt() {
  [ -f "$AGENTS/com.tidskoll.skarm.plist" ] || fail "skärmdumpsnivån är inte installerad"
  launchctl bootout "$GUI/com.tidskoll.skarm" 2>/dev/null || true
  launchctl bootstrap "$GUI" "$AGENTS/com.tidskoll.skarm.plist"
  ok "skärmdumparna igång"
}

cmd_avinstallera() {
  if grep -qxF "# === TIDSKOLL-BLOCK START ===" /etc/hosts 2>/dev/null && [ -x "$BIN/blockera.sh" ]; then
    say "Tar bort sajtblocket (macOS frågar efter lösenordet)…"
    bash "$BIN/blockera.sh" av
  fi
  for l in webblasare veckorapport skarm; do
    launchctl bootout "$GUI/com.tidskoll.$l" 2>/dev/null || true
    rm -f "$AGENTS/com.tidskoll.$l.plist"
  done
  rm -rf "$APP" "${SKILL_DIRS[@]}" "$BIN" "$ROOT/SKILL.md"
  ok "bakgrundsjobb, Tidskoll.app, skillen och skripten borttagna"
  say "Kvar: din data i $ROOT och ActivityWatch själv."
  say "  Ta bort datan:        rm -rf $ROOT"
  say "  Ta bort ActivityWatch: brew uninstall --cask activitywatch (eller släng appen)"
}

case "${1:-}" in
  bas)          shift; cmd_bas "$@" ;;
  skarm)        shift; cmd_skarm "$@" ;;
  blockera)     cmd_blockera ;;
  status)       cmd_status ;;
  paus)         cmd_paus ;;
  fortsatt)     cmd_fortsatt ;;
  avinstallera) cmd_avinstallera ;;
  *) sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
