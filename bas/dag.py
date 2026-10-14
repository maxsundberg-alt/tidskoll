#!/usr/bin/env python3
"""En dags aktiva tid ur ActivityWatch, som JSON.

Tid per app, per kategori (med underkategorier) och per webbadress. Bara tid
när du satt vid datorn räknas. Används av skillen tidskoll för att svara på
frågor om en dag, och av skärmdumpsanalysen som grund för tiden.

    python3 dag.py                # idag
    python3 dag.py 2026-10-08     # valfritt datum
    python3 dag.py igår

Skriver alltid giltig JSON. Svarar inte ActivityWatch kommer ett "fel"-fält.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aw  # noqa: E402

TOP = 15
URL_PREFIXES = ("aw-watcher-tidskoll-url", "aw-watcher-web")


def day_period(date_str: str) -> str:
    start = datetime.strptime(date_str, "%Y-%m-%d").astimezone()
    now = datetime.now().astimezone()
    end = min(start + timedelta(days=1), now)
    return f"{start.isoformat()}/{end.isoformat()}"


def build(date_str: str) -> dict:
    tp = day_period(date_str)
    buckets = aw.get("/buckets/")
    rules = aw.rules(aw.active_categories())

    apps: dict[str, float] = {}
    cats: dict[tuple, float] = {}
    for win, afk in aw.bucket_pairs(buckets):
        res = aw.query(aw.active_query(win, afk, rules, (
            'RETURN = {"app": merge_events_by_keys(active, ["app"]), '
            '"cat": merge_events_by_keys(cats, ["$category"])};'
        )), [tp])[0]
        for e in res["app"]:
            a = aw.clean(e["data"].get("app", "?"))
            apps[a] = apps.get(a, 0) + e["duration"]
        for e in res["cat"]:
            k = tuple(e["data"].get("$category") or ["Uncategorized"])
            cats[k] = cats.get(k, 0) + e["duration"]

    top: dict[str, float] = {}
    subs: dict[str, dict[str, float]] = {}
    for k, s in cats.items():
        name = "Okategoriserat" if k[0] == "Uncategorized" else k[0]
        top[name] = top.get(name, 0) + s
        if len(k) >= 2:
            subs.setdefault(name, {})[k[1]] = subs.get(name, {}).get(k[1], 0) + s

    urls: dict[str, float] = {}
    domains: dict[str, float] = {}
    for bid in buckets:
        if not bid.startswith(URL_PREFIXES):
            continue
        try:
            res = aw.query([f'events = flood(query_bucket("{bid}"));',
                            'RETURN = merge_events_by_keys(events, ["url"]);'], [tp])[0]
        except Exception:
            continue
        for e in res:
            u = e["data"].get("url", "?")
            urls[u] = urls.get(u, 0) + e["duration"]
            d = urlparse(u).netloc.removeprefix("www.") or u
            domains[d] = domains.get(d, 0) + e["duration"]

    def ranked(d: dict, key: str, n: int = TOP):
        return [{key: k, "sekunder": round(v)}
                for k, v in sorted(d.items(), key=lambda kv: kv[1], reverse=True)[:n]]

    return {
        "datum": date_str,
        "aktiv_tid_sekunder": round(sum(apps.values())),
        "appar": ranked(apps, "app"),
        "kategorier": [
            {"kategori": n, "sekunder": round(s),
             "under": ranked(subs.get(n, {}), "namn", 99)}
            for n, s in sorted(top.items(), key=lambda kv: kv[1], reverse=True)
        ],
        "domaner": ranked(domains, "doman"),
        "adresser": ranked(urls, "url"),
    }


def main() -> int:
    arg = sys.argv[1] if len(sys.argv) > 1 else "idag"
    today = datetime.now().astimezone()
    date_str = {"idag": today, "igår": today - timedelta(days=1),
                "igar": today - timedelta(days=1)}.get(arg)
    date_str = date_str.strftime("%Y-%m-%d") if date_str else arg
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print(json.dumps({"datum": arg, "fel": "Okänt datum. Ange idag, igår eller ÅÅÅÅ-MM-DD."},
                         ensure_ascii=False))
        return 0
    try:
        out = build(date_str)
    except Exception as e:
        out = {"datum": date_str, "fel": f"ActivityWatch svarar inte: {e}"}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
