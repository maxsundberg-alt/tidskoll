#!/bin/bash
# Valfri nattlig analys: Claude Code kör "/tidskoll analysera" på dagens
# skärmdumpar klockan 23:30, skriver en dagsanteckning och uppdaterar listan
# över återkommande mönster. Startas av launchd (com.tidskoll.nattanalys).
#
# Kostar en Claude-körning per dag som har data. Bilderna Claude tittar på
# skickas till Anthropic.
set -u
export PATH="/usr/local/bin:/opt/homebrew/bin:$HOME/.local/bin:$HOME/.claude/local:/usr/bin:/bin"

DAY=$(date +%F)
LOG="$HOME/tidskoll/skarm/days/$DAY/log.jsonl"

# Ingen data idag (datorn var av eller pausad): kör inte.
[ -s "$LOG" ] || { echo "$(date) ingen data för $DAY, hoppar över"; exit 0; }

cd "$HOME/tidskoll"
claude -p "/tidskoll analysera $DAY" \
  --allowedTools "Bash(python3:*),Read,Write,Edit"
echo "$(date) analys $DAY klar, exit=$?"
