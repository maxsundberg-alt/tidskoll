#!/usr/bin/env python3
"""Sammanfatta en dags skärmlogg (~/tidskoll/skarm/days/<datum>/log.jsonl) som JSON.

Det visuella lagrets navigering: kollapsar 5s-tickar till aktivitetsblock
(samma app+fönster+url i följd), räknar kontext-växlingar och churn-bursts, och
väljer ut de 10–30 frames som är värda att faktiskt titta på (block-övergångar,
längsta block, churn) — så analysen aldrig läser rå JSONL i kontext och aldrig
öppnar alla bilder.

    python3 block.py                # idag
    python3 block.py 2026-10-08     # valfritt datum

Skriver alltid giltig JSON (tomma listor om ingen data/frames finns än).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime

BASE = os.environ.get("TIDSKOLL_SKARM", os.path.expanduser("~/tidskoll/skarm"))
TICK_INTERVAL = 5
GAP_SPLIT_S = 15            # >3 tick-luckor mellan tickar = idle/avbrott → nytt block
MAX_FRAMES = 30
LONGEST_BLOCKS = 8
CHURN_WINDOW_TICKS = 24     # ~2 min vid 5s-tick
CHURN_THRESHOLD = 6         # >6 app-växlingar i fönstret = churn-burst
# Reserverade kvoter i frame-urvalet så att inget slag (särskilt churn) kan
# nollas ut av antalet block en stökig dag. Summan får överstiga MAX_FRAMES —
# capen appliceras efter dedupe.
CHURN_QUOTA = 12
TRANSITION_QUOTA = 12
LONGEST_QUOTA = 6


def _frame_file(day_dir: str, ts: str) -> str | None:
    for ext in (".webp", ".jpg"):
        if os.path.exists(os.path.join(day_dir, ts + ext)):
            return ts + ext
    return None


def build(date_str: str) -> dict:
    day_dir = os.path.join(BASE, "days", date_str)
    log_path = os.path.join(day_dir, "log.jsonl")
    if not os.path.exists(log_path):
        return {"date": date_str, "note": "ingen log.jsonl för datumet",
                "blocks": [], "by_app": [], "switches": 0, "churn_bursts": [],
                "frames_to_view": [], "frame_count_total": 0}

    ticks = []
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ticks.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    # Blocken: kollapsa samma app+fönster+url i följd. Fortsätt ETT block bara om
    # tickarna är konsekutiva i tid — annars (idle >90s loggas aldrig, så ett gap i
    # epoch = idle/avbrott) startas nytt block även vid samma app. Utan detta blir en
    # app som ligger öppen över lunch ett falskt 90-min-block som dominerar urvalet.
    blocks = []
    for tk in ticks:
        key = (tk.get("app", ""), tk.get("window", ""), tk.get("url", ""))
        ep = tk.get("epoch", 0)
        prev = blocks[-1] if blocks else None
        contiguous = prev is not None and prev["_key"] == key and \
            (ep - prev["end_epoch"]) <= GAP_SPLIT_S
        if contiguous:
            prev["end_t"] = tk["t"]
            prev["end_epoch"] = ep
            prev["n_ticks"] += 1
            f = _frame_file(day_dir, tk["t"]) if tk.get("img") else None
            if f:
                prev["_frames"].append(f)
        else:
            f = _frame_file(day_dir, tk["t"]) if tk.get("img") else None
            blocks.append({
                "_key": key, "app": key[0], "window": key[1], "url": key[2],
                "start_t": tk["t"], "end_t": tk["t"],
                "start_epoch": ep, "end_epoch": ep,
                "n_ticks": 1, "_frames": [f] if f else [],
            })
    # Blocken är nu tidskontinuerliga, så väggtiden är aktiv tid.
    for b in blocks:
        b["dur_s"] = max(TICK_INTERVAL, b["end_epoch"] - b["start_epoch"] + TICK_INTERVAL)

    # Per-app totaler (tick-baserat, 5s/tick)
    app_secs: dict[str, int] = {}
    for tk in ticks:
        app_secs[tk.get("app", "?")] = app_secs.get(tk.get("app", "?"), 0) + 5
    by_app = [{"app": a, "seconds": s}
              for a, s in sorted(app_secs.items(), key=lambda kv: kv[1], reverse=True)]

    # Kontext-växlingar + churn-bursts (glidande fönster över app-byten)
    apps = [tk.get("app", "") for tk in ticks]
    switches = sum(1 for i in range(1, len(apps)) if apps[i] != apps[i - 1])
    churn = []
    i = 0
    while i < len(ticks):
        w = ticks[i:i + CHURN_WINDOW_TICKS]
        wa = [t.get("app", "") for t in w]
        chg = sum(1 for j in range(1, len(wa)) if wa[j] != wa[j - 1])
        if chg > CHURN_THRESHOLD:
            churn.append({"start_t": w[0]["t"], "end_t": w[-1]["t"], "switches": chg})
            i += CHURN_WINDOW_TICKS      # hoppa förbi burst-fönstret
        else:
            i += 1

    # Urval av frames att titta på — tre slag, var för sig, sen kvoterat.
    # a) churn-frames: sampla PER burst (första + mitten) så varje burst
    #    representeras — annars fyller en tidig burst hela churn-kvoten och en
    #    burst sent på dagen blir osamplad.
    churn_ranges = [(c["start_t"], c["end_t"]) for c in churn]
    churn_frames = []
    for s, e in churn_ranges:
        burst = [_frame_file(day_dir, tk["t"]) for tk in ticks
                 if tk.get("img") and s <= tk["t"] <= e and _frame_file(day_dir, tk["t"])]
        if burst:
            churn_frames.append(burst[0])
            if len(burst) > 2:
                churn_frames.append(burst[len(burst) // 2])
    # b) block-övergångar (första framen i varje block)
    transition_frames = [b["_frames"][0] for b in blocks if b["_frames"]]
    # c) mitt-frame i de längsta blocken
    longest_frames = [
        b["_frames"][len(b["_frames"]) // 2]
        for b in sorted(blocks, key=lambda x: x["dur_s"], reverse=True)[:LONGEST_BLOCKS]
        if b["_frames"]
    ]

    # Reserverade kvoter — churn tas FÖRST så en stökig dag med >30 block aldrig kan
    # tränga ut just copy-paste/kontext-växlings-framesen (skillens kärnsyfte).
    frames_to_view: list[str] = []
    seen: set[str] = set()

    def _take(cands, quota):
        n = 0
        for f in cands:
            if n >= quota or len(frames_to_view) >= MAX_FRAMES:
                break
            if f not in seen:
                seen.add(f)
                frames_to_view.append(f)
                n += 1

    _take(churn_frames, CHURN_QUOTA)
    _take(transition_frames, TRANSITION_QUOTA)
    _take(longest_frames, LONGEST_QUOTA)
    # Fyll ev. kvarvarande slots upp till MAX_FRAMES (churn > övergångar > längsta)
    _take(churn_frames + transition_frames + longest_frames, MAX_FRAMES)

    total_frames = sum(1 for tk in ticks if tk.get("img") and _frame_file(day_dir, tk["t"]))

    # Rensa interna fält
    clean_blocks = [{k: v for k, v in b.items() if not k.startswith("_")} | {"frames": len(b["_frames"])}
                    for b in blocks]

    return {
        "date": date_str,
        "day_dir": day_dir,
        "tick_count": len(ticks),
        "frame_count_total": total_frames,
        "switches": switches,
        "churn_bursts": churn,
        "by_app": by_app,
        "block_count": len(blocks),
        "blocks": clean_blocks,
        "frames_to_view": frames_to_view,
    }


def main() -> int:
    date_str = sys.argv[1] if len(sys.argv) > 1 else datetime.now().astimezone().strftime("%Y-%m-%d")
    print(json.dumps(build(date_str), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
