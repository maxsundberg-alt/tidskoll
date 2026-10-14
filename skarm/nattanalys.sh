#!/bin/bash
# Valfri nattlig analys: en AI-agent kör "tidskoll analysera" på dagens skärmdumpar
# klockan 23:30, skriver en dagsanteckning och uppdaterar listan över återkommande
# mönster. Startas av launchd (com.tidskoll.nattanalys).
#
# Vilken agent som körs står i ~/tidskoll/nattanalys.conf, som en rad:
#   AGENT_KOMMANDO='claude -p "$UPPDRAG" --allowedTools "Bash(python3:*),Read,Write,Edit"'
# $UPPDRAG ersätts med uppdraget nedan. Agenten som installerar Tidskoll skriver in
# det kommando som kör den själv utan att fråga (headless).
#
# Kostar en körning per dag som har data. Bilderna agenten tittar på skickas till
# leverantören av modellen.
set -u
export PATH="/usr/local/bin:/opt/homebrew/bin:$HOME/.local/bin:$HOME/.claude/local:$HOME/.npm-global/bin:/usr/bin:/bin"

DAY=$(date +%F)
LOG="$HOME/tidskoll/skarm/days/$DAY/log.jsonl"
CONF="$HOME/tidskoll/nattanalys.conf"

# Ingen data idag (datorn var av eller pausad): kör inte.
[ -s "$LOG" ] || { echo "$(date) ingen data för $DAY, hoppar över"; exit 0; }
[ -f "$CONF" ] || { echo "$(date) $CONF saknas, vet inte vilken agent som ska köras"; exit 1; }

AGENT_KOMMANDO=""
# shellcheck source=/dev/null
. "$CONF"
[ -n "$AGENT_KOMMANDO" ] || { echo "$(date) AGENT_KOMMANDO är tomt i $CONF"; exit 1; }

UPPDRAG="Kör tidskoll analysera $DAY. Instruktionerna finns i skillen tidskoll, eller i ~/tidskoll/SKILL.md om skillen inte är laddad."
export UPPDRAG
cd "$HOME/tidskoll"
eval "$AGENT_KOMMANDO"
echo "$(date) analys $DAY klar, exit=$?"
