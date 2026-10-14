#!/usr/bin/env python3
"""Visa, exportera och tillämpa kategorierna i ActivityWatch.

    python3 kategorier.py visa [--dagar 7]     tid per kategori + största okategoriserade tiden
    python3 kategorier.py visa --fil FIL.json  samma sak, men med filens regler (provkörning, ändrar inget)
    python3 kategorier.py exportera            skriv ut kategorierna som ActivityWatch använder nu (JSON)
    python3 kategorier.py tillampa FIL.json    ersätt kategorierna i ActivityWatch med filens

Arbetsgången när en regel ska läggas till: exportera till ~/tidskoll/kategorier.json,
redigera filen, provkör med visa --fil, och tillämpa när resultatet ser rätt ut.

Så väljer ActivityWatch kategori: regexen söks mot både appnamnet och fönstertiteln.
Den djupaste kategorin vinner. Vid lika djup vinner den som står sist i listan.

Två fällor, eftersom ActivityWatch kör Rusts regexmotor, som skiljer sig från Pythons:
  - Skriv aldrig `\\|` för ett bokstavligt lodstreck. Det blir ett "eller" och
    matchar allt. Välj en annan del av titeln.
  - `\\b` beter sig inte som väntat. Använd mellanslag eller ^ och $ som ankare.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aw  # noqa: E402

BACKUP_DIR = Path.home() / "tidskoll" / "kategorier-backup"


def period(days: int) -> str:
    now = datetime.now().astimezone()
    start = (now - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return f"{start.isoformat()}/{now.isoformat()}"


def visa(days: int, fil: str | None = None) -> int:
    cats = json.loads(Path(fil).read_text()) if fil else aw.active_categories()
    rules = aw.rules(cats)
    tp = period(days)
    buckets = aw.get("/buckets/")

    by_cat: dict[tuple, float] = {}
    unknown: dict[tuple, float] = {}
    for win, afk in aw.bucket_pairs(buckets):
        res = aw.query(aw.active_query(win, afk, rules, (
            'unk = filter_keyvals(cats, "$category", [["Uncategorized"], ["Webbläsning (okategoriserad)"]]);'
            'RETURN = {"cat": merge_events_by_keys(cats, ["$category"]), '
            '"unk": merge_events_by_keys(unk, ["app", "title"])};'
        )), [tp])[0]
        for e in res["cat"]:
            k = tuple(e["data"].get("$category") or ["Uncategorized"])
            by_cat[k] = by_cat.get(k, 0) + e["duration"]
        for e in res["unk"]:
            k = (aw.clean(e["data"].get("app", "?")), e["data"].get("title", ""))
            unknown[k] = unknown.get(k, 0) + e["duration"]

    total = sum(by_cat.values())
    print(f"Aktiv tid de senaste {days} dagarna: {aw.fmt_dur(total)}  ({len(cats)} kategorier)\n")
    for k, s in sorted(by_cat.items(), key=lambda kv: kv[1], reverse=True):
        name = "Okategoriserat" if k == ("Uncategorized",) else " > ".join(k)
        pct = f"{100 * s / total:.0f} %" if total else ""
        print(f"  {aw.fmt_dur(s):>8} {pct:>5}  {name}")

    print("\nMest tid utan riktig kategori (kandidater för nya regler):")
    rows = sorted(unknown.items(), key=lambda kv: kv[1], reverse=True)[:20]
    if not rows:
        print("  (inget, allt är kategoriserat)")
    for (app, title), s in rows:
        print(f"  {aw.fmt_dur(s):>8}  [{app}] {title[:70]}")
    return 0


def exportera() -> int:
    print(json.dumps(aw.active_categories(), ensure_ascii=False, indent=2))
    return 0


def tillampa(path: str) -> int:
    cats = json.loads(Path(path).read_text())
    for c in cats:
        if not isinstance(c.get("name"), list) or "rule" not in c:
            print(f"Ogiltig kategori: {c}", file=sys.stderr)
            return 1
        c.setdefault("data", {})

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup = BACKUP_DIR / f"{time.strftime('%Y-%m-%d_%H%M%S')}.json"
    backup.write_text(json.dumps(aw.get("/settings"), ensure_ascii=False, indent=2))

    # Webbgränssnittet läser category_sets + active_set_ids. classes skrivs också,
    # eftersom äldre versioner av ActivityWatch bara läser den.
    aw.post("/settings/category_sets", [{"id": "default", "categories": cats}])
    aw.post("/settings/active_set_ids", ["default"])
    aw.post("/settings/classes", cats)

    back = aw.active_categories()
    if [c["name"] for c in back] != [c["name"] for c in cats]:
        print("Kategorierna sparades, men det som läses tillbaka stämmer inte. Kontrollera i ActivityWatch.",
              file=sys.stderr)
        return 1
    print(f"{len(cats)} kategorier tillämpade. Förra uppsättningen sparad i {backup}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    v = sub.add_parser("visa")
    v.add_argument("--dagar", type=int, default=7)
    v.add_argument("--fil", help="provkör reglerna i en fil i stället för de aktiva")
    sub.add_parser("exportera")
    t = sub.add_parser("tillampa")
    t.add_argument("fil")
    args = ap.parse_args()
    if args.cmd == "exportera":
        return exportera()
    if args.cmd == "tillampa":
        return tillampa(args.fil)
    return visa(getattr(args, "dagar", 7), getattr(args, "fil", None))


if __name__ == "__main__":
    sys.exit(main())
