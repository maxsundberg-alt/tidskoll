#!/usr/bin/env python3
"""Loggar adressen i webbläsarens aktiva flik till ActivityWatch.

ActivityWatch ser bara fönstertiteln. Den här bevakaren lägger till själva
adressen för Safari och de Chromium-baserade webbläsarna (Chrome, Arc, Brave,
Edge, Vivaldi). Firefox går inte att fråga via AppleScript; där finns
ActivityWatchs eget tillägg aw-watcher-web.

Den frågar bara webbläsaren när ActivityWatch redan säger att webbläsaren är
den aktiva appen och att du sitter vid datorn. macOS frågar en gång per webbläsare
om python3 får styra den, och det är den enda behörighet som behövs.

Körs i bakgrunden av launchd (com.tidskoll.webblasare).

    python3 webblasare.py            # kör i loop
    python3 webblasare.py --en-gang  # skriv ut vad den ser just nu, skicka inget
"""

from __future__ import annotations

import subprocess
import sys
import time
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aw  # noqa: E402

PREFIX = "aw-watcher-tidskoll-url"
POLL = 5.0
PULSE = POLL + 5.0

# Appnamn som ActivityWatch rapporterar → AppleScript som ger adressen.
# Varje webbläsare får ett eget osascript-anrop: AppleScript slår upp appens
# ordlista när skriptet kompileras, så ett skript som nämner en webbläsare som
# inte är installerad går inte ens att köra.
CHROMIUM = ("Google Chrome", "Arc", "Brave Browser", "Microsoft Edge", "Vivaldi", "Chromium")
SAFARI = ("Safari", "Safari Technology Preview")


def tab(app: str) -> tuple[str | None, str | None]:
    if app in SAFARI:
        url_s = f'tell application "{app}" to get URL of current tab of front window'
        title_s = f'tell application "{app}" to get name of current tab of front window'
    elif app in CHROMIUM:
        url_s = f'tell application "{app}" to get URL of active tab of front window'
        title_s = f'tell application "{app}" to get title of active tab of front window'
    else:
        return None, None

    def osa(script: str) -> str:
        return subprocess.run(["osascript", "-e", script], capture_output=True,
                              text=True, timeout=5).stdout.strip()
    try:
        return osa(url_s) or None, osa(title_s) or None
    except Exception:
        return None, None


def frontmost_browser() -> tuple[str | None, str | None]:
    """(webbläsarens appnamn, datornamn) om en webbläsare är aktiv och du är vid datorn."""
    buckets = aw.get("/buckets/")
    win_b = aw.newest_bucket(buckets, type_="currentwindow")
    afk_b = aw.newest_bucket(buckets, type_="afkstatus")
    if not win_b or not afk_b:
        return None, None
    win = aw.get(f"/buckets/{win_b}/events?limit=1")
    afk = aw.get(f"/buckets/{afk_b}/events?limit=1")
    if not win or not afk or afk[0]["data"].get("status") != "not-afk":
        return None, None
    app = win[0]["data"].get("app")
    if app not in SAFARI + CHROMIUM:
        return None, None
    host = win_b.split("_", 1)[1] if "_" in win_b else "okand"
    return app, host


def ensure_bucket(host: str) -> str:
    bid = f"{PREFIX}_{host}"
    try:
        aw.get(f"/buckets/{bid}")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
        aw.post(f"/buckets/{bid}", {"client": PREFIX, "type": "web.tab.current", "hostname": host})
    return bid


def heartbeat(bid: str, url: str, title: str | None, app: str):
    aw.post(f"/buckets/{bid}/heartbeat?pulsetime={PULSE}", {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "duration": 0,
        "data": {"url": url, "title": title or "", "browser": app},
    })


def wait_for_server() -> bool:
    for _ in range(60):
        try:
            aw.get("/info")
            return True
        except Exception:
            time.sleep(2)
    return False


def main() -> int:
    if "--en-gang" in sys.argv:
        app, host = frontmost_browser()
        if not app:
            print("Ingen webbläsare är aktiv just nu (eller så är du markerad som borta).")
            return 0
        url, title = tab(app)
        print(f"webbläsare: {app}\ndator: {host}\nadress: {url}\ntitel: {title}")
        return 0 if url else 1

    if not wait_for_server():
        print("ActivityWatch svarar inte på localhost:5600", file=sys.stderr)
        return 1
    known: set[str] = set()
    while True:
        try:
            app, host = frontmost_browser()
            if app:
                url, title = tab(app)
                if url and url.startswith(("http://", "https://")):
                    if host not in known:
                        ensure_bucket(host)
                        known.add(host)
                    heartbeat(f"{PREFIX}_{host}", url, title, app)
        except Exception as e:
            print(f"{datetime.now():%F %T} {e}", file=sys.stderr)
        time.sleep(POLL)


if __name__ == "__main__":
    sys.exit(main())
