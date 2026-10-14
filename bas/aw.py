"""Delad kod för att prata med ActivityWatch (localhost:5600).

Används av dag.py, veckorapport.py, kategorier.py och webblasare.py.
Bara standardbiblioteket, så allt går att köra med macOS egen python3.
"""

from __future__ import annotations

import json
import urllib.request

AW_BASE = "http://localhost:5600/api/0"
TIMEOUT = 30


def get(path: str):
    with urllib.request.urlopen(f"{AW_BASE}{path}", timeout=TIMEOUT) as r:
        return json.load(r)


def post(path: str, data):
    req = urllib.request.Request(
        f"{AW_BASE}{path}", data=json.dumps(data, ensure_ascii=False).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        body = r.read()
        return json.loads(body) if body else None


def query(lines: list[str], timeperiods: list[str]):
    return post("/query/", {"query": lines, "timeperiods": timeperiods})


def bucket_pairs(buckets: dict) -> list[tuple[str, str]]:
    """Alla (fönster, afk)-par, ett per datornamn.

    ActivityWatch lägger datornamnet sist i bucket-id:t (`aw-watcher-window_<namn>`).
    Byter datorn namn, till exempel när den byter nätverk, skapas en ny bucket.
    En vecka kan därför ligga i två buckets. Paren överlappar inte i tid, så
    ingenting räknas dubbelt när de summeras.
    """
    wins = {bid.split("_", 1)[1]: bid for bid, b in buckets.items()
            if b.get("type") == "currentwindow" and "_" in bid}
    afks = {bid.split("_", 1)[1]: bid for bid, b in buckets.items()
            if b.get("type") == "afkstatus" and "_" in bid}
    pairs = [(wins[h], afks[h]) for h in wins if h in afks]
    if not pairs:
        raise RuntimeError("Hittar ingen fönster- eller närvarodata från ActivityWatch. Är appen igång?")
    return pairs


def newest_bucket(buckets: dict, *, type_: str | None = None, prefix: str | None = None) -> str | None:
    """Senast uppdaterade bucket av en viss typ eller med ett visst prefix."""
    cands = [(bid, b) for bid, b in buckets.items()
             if (type_ is None or b.get("type") == type_)
             and (prefix is None or bid.startswith(prefix))]
    if not cands:
        return None
    cands.sort(key=lambda kv: kv[1].get("last_updated") or "", reverse=True)
    return cands[0][0]


def active_categories() -> list[dict]:
    """Kategorierna som ActivityWatch faktiskt använder just nu.

    Webbgränssnittet räknar fram dem ur `category_sets` och `active_set_ids`.
    `classes` är en äldre kopia som kan vara inaktuell, så den används bara
    om det inte finns några uppsättningar.
    """
    settings = get("/settings")
    sets = settings.get("category_sets") or []
    active = settings.get("active_set_ids") or ["default"]
    for sid in active:
        for s in sets:
            if s.get("id") == sid and s.get("categories"):
                return s["categories"]
    return settings.get("classes") or []


def rules(categories: list[dict]) -> list:
    return [[c["name"], c["rule"]] for c in categories]


def active_query(win: str, afk: str, rules_: list, extra: str) -> list[str]:
    """De inledande frågeraderna, som ger aktiv tid: fönsterhändelser när du inte är borta."""
    return [
        f'afk = flood(query_bucket("{afk}"));',
        f'win = flood(query_bucket("{win}"));',
        'active = filter_period_intersect(win, filter_keyvals(afk, "status", ["not-afk"]));',
        'active = exclude_keyvals(active, "app", ["loginwindow"]);',
        f"cats = categorize(active, {json.dumps(rules_, ensure_ascii=False)});",
        extra,
    ]


def clean(s) -> str:
    """Ta bort osynliga riktningstecken som vissa appnamn bär (t.ex. WhatsApp)."""
    return str(s).translate({0x200e: None, 0x200f: None, 0x200b: None}).strip() or "?"


def fmt_dur(seconds: float) -> str:
    if seconds >= 3600:
        return f"{seconds / 3600:.1f}".replace(".", ",") + " h"
    return f"{round(seconds / 60)} min"
