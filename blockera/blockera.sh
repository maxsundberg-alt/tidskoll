#!/bin/bash
# Tidskoll, blockering. Blockerar sajterna i ~/tidskoll/blocklista.txt i alla
# webbläsare på datorn, genom att peka dem mot 0.0.0.0 i /etc/hosts. Sajten går
# inte att öppna, oavsett webbläsare, inkognitoläge eller app som hämtar från den.
#
#   bash blockera.sh pa              slå på blockeringen
#   bash blockera.sh av              stäng av blockeringen
#   bash blockera.sh lyft <domän>    öppna en sajt tillfälligt, resten förblir blockerade
#   bash blockera.sh ater <domän>    blockera den igen
#   bash blockera.sh status          visa läget
#
# Att skriva till /etc/hosts kräver datorns lösenord. Det skrivs i macOS egen
# ruta, så varken skriptet eller agenten ser det.
set -euo pipefail

ROOT="$HOME/tidskoll"
LISTA="$ROOT/blocklista.txt"
UNDANTAG="$ROOT/blockera-undantag.txt"
HOSTS=/etc/hosts
START="# === TIDSKOLL-BLOCK START ==="
END="# === TIDSKOLL-BLOCK SLUT ==="

rader() { [ -f "$1" ] && grep -vE '^[[:space:]]*(#.*)?$' "$1" | tr -d ' \t' || true; }

domaner() {  # listan plus www. och m. för varje rad, utan dubbletter
  rader "$LISTA" | while IFS= read -r d; do
    printf '%s\n' "$d"
    case "$d" in www.*|m.*) ;; *) printf 'www.%s\nm.%s\n' "$d" "$d" ;; esac
  done | sort -u
}

lyft_() {  # sant om domänen, eller en domän den ligger under, är tillfälligt öppnad
  local d="$1" e
  while IFS= read -r e; do
    [ -z "$e" ] && continue
    [ "$d" = "$e" ] && return 0
    case "$d" in *."$e") return 0 ;; esac
  done < <(rader "$UNDANTAG")
  return 1
}

utan_block() {
  awk -v s="$START" -v e="$END" '$0==s{skip=1;next} $0==e{skip=0;next} !skip{print}' "$HOSTS"
}

block() {
  echo "$START"
  domaner | while IFS= read -r d; do lyft_ "$d" || printf '0.0.0.0 %s\n' "$d"; done
  echo "$END"
}

skriv() {  # nytt innehåll för /etc/hosts på stdin
  local tmp; tmp="$(mktemp "${TMPDIR:-/tmp}/tidskoll-hosts.XXXXXX")"
  cat > "$tmp"
  # Byt filen i ett steg (mv), så att inget program läser en halvskriven fil.
  # Originalet sparas en gång som /etc/hosts.tidskoll-original.
  osascript - "$tmp" <<'OSA' >/dev/null
on run argv
  set src to quoted form of (item 1 of argv)
  do shell script "[ -f /etc/hosts.tidskoll-original ] || cp /etc/hosts /etc/hosts.tidskoll-original; t=$(mktemp /etc/.hosts.tidskoll.XXXXXX) && cat " & src & " > \"$t\" && chown root:wheel \"$t\" && chmod 644 \"$t\" && mv -f \"$t\" /etc/hosts && dscacheutil -flushcache; killall -HUP mDNSResponder 2>/dev/null; true" with prompt "Tidskoll vill uppdatera listan över blockerade sajter." with administrator privileges
end run
OSA
  rm -f "$tmp"
}

antal() { grep -c '^0\.0\.0\.0 ' <(awk -v s="$START" -v e="$END" '$0==s{on=1;next} $0==e{on=0} on' "$HOSTS") || true; }
pa_nu() { grep -qxF "$START" "$HOSTS" 2>/dev/null; }

case "${1:-status}" in
  pa)
    [ -s "$LISTA" ] || { echo "Blocklistan saknas eller är tom: $LISTA"; exit 1; }
    { utan_block; block; } | skriv
    echo "✓ Blockeringen är på. $(antal) adresser är blockerade."
    echo "  Flikar som redan var öppna kan fortsätta fungera en stund. Avsluta webbläsaren (Cmd+Q) om något fortfarande syns."
    ;;
  av)
    utan_block | skriv
    echo "✓ Blockeringen är avstängd."
    ;;
  lyft)
    [ $# -ge 2 ] || { echo "Ange en domän: bash $0 lyft youtube.com"; exit 1; }
    mkdir -p "$ROOT"; touch "$UNDANTAG"
    grep -qxF "$2" "$UNDANTAG" || echo "$2" >> "$UNDANTAG"
    pa_nu && { utan_block; block; } | skriv
    echo "✓ $2 är tillfälligt öppen. Blockera den igen med: bash $0 ater $2"
    ;;
  ater)
    [ $# -ge 2 ] || { echo "Ange en domän: bash $0 ater youtube.com"; exit 1; }
    if [ -f "$UNDANTAG" ]; then
      grep -vxF "$2" "$UNDANTAG" > "$UNDANTAG.tmp" || true
      mv "$UNDANTAG.tmp" "$UNDANTAG"
    fi
    pa_nu && { utan_block; block; } | skriv
    echo "✓ $2 är blockerad igen."
    ;;
  status)
    if pa_nu; then echo "Blockeringen: på ($(antal) adresser)"; else echo "Blockeringen: av"; fi
    if [ -n "$(rader "$UNDANTAG")" ]; then echo "Tillfälligt öppna:"; rader "$UNDANTAG" | sed 's/^/  /'; fi
    ;;
  *) sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
