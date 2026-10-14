#!/usr/bin/env python3
"""Sammanfatta en dags skärmlogg (~/tidskoll/skarm/dagar/<datum>/log.jsonl) som JSON.

Slår ihop femsekundersraderna till arbetspass (samma app, fönster och adress i följd),
räknar appbyten och perioder med täta byten, och väljer ut de 10 till 30 bilder som är
värda att titta på. Då behöver analysen aldrig läsa hela loggen eller öppna alla bilder.

    python3 arbetspass.py                # idag
    python3 arbetspass.py 2026-10-08     # valfritt datum

Skriver alltid giltig JSON, med tomma listor om det inte finns någon data.

Bygger på analysmetoden i screenwatch-kit av Muhammad Ali (MIT-licens).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime

BASE = os.path.expanduser("~/tidskoll/skarm")
SEKUNDER_PER_RAD = 5
GLAPP_S = 15             # mer än tre missade rader i följd betyder att du var borta: nytt pass
MAX_BILDER = 30
LANGSTA_PASS = 8
TATA_FONSTER = 24        # rader, ungefär två minuter
TATA_GRANS = 6           # fler än sex appbyten på två minuter räknas som täta byten
# Varje sorts bild har en egen kvot, så att en rörig dag med många pass inte tränger
# undan bilderna från perioderna med täta byten. Summan får vara större än MAX_BILDER;
# taket gäller efter att dubbletter tagits bort.
KVOT_TATA = 12
KVOT_OVERGANGAR = 12
KVOT_LANGSTA = 6


def _bildfil(dagmapp: str, t: str) -> str | None:
    for ext in (".webp", ".jpg"):
        if os.path.exists(os.path.join(dagmapp, t + ext)):
            return t + ext
    return None


def build(datum: str) -> dict:
    dagmapp = os.path.join(BASE, "dagar", datum)
    logg = os.path.join(dagmapp, "log.jsonl")
    if not os.path.exists(logg):
        return {"datum": datum, "notering": "ingen logg för datumet", "antal_rader": 0,
                "antal_bilder": 0, "appbyten": 0, "tata_byten": [], "appar": [],
                "antal_pass": 0, "pass": [], "bilder_att_titta_pa": []}

    rader = []
    with open(logg) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rader.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    # Ett pass fortsätter bara om raderna följer direkt på varandra i tid. Loopen loggar
    # inget när du är borta, så ett glapp betyder paus. Utan den regeln blir en app som
    # står öppen över lunchen ett falskt pass på 90 minuter som tar över urvalet.
    pass_: list[dict] = []
    for r in rader:
        nyckel = (r.get("app", ""), r.get("window", ""), r.get("url", ""))
        ep = r.get("epoch", 0)
        bild = _bildfil(dagmapp, r["t"]) if r.get("img") else None
        sista = pass_[-1] if pass_ else None
        if sista and sista["_nyckel"] == nyckel and ep - sista["slut_epoch"] <= GLAPP_S:
            sista["slut"] = r["t"]
            sista["slut_epoch"] = ep
            if bild:
                sista["_bilder"].append(bild)
        else:
            pass_.append({"_nyckel": nyckel, "app": nyckel[0], "fonster": nyckel[1],
                          "url": nyckel[2], "start": r["t"], "slut": r["t"],
                          "start_epoch": ep, "slut_epoch": ep,
                          "_bilder": [bild] if bild else []})
    for p in pass_:
        p["sekunder"] = max(SEKUNDER_PER_RAD, p["slut_epoch"] - p["start_epoch"] + SEKUNDER_PER_RAD)

    app_sek: dict[str, int] = {}
    for r in rader:
        a = r.get("app", "?")
        app_sek[a] = app_sek.get(a, 0) + SEKUNDER_PER_RAD
    appar = [{"app": a, "sekunder": s}
             for a, s in sorted(app_sek.items(), key=lambda kv: kv[1], reverse=True)]

    # Appbyten, och perioder med täta byten (glidande fönster)
    appnamn = [r.get("app", "") for r in rader]
    appbyten = sum(1 for i in range(1, len(appnamn)) if appnamn[i] != appnamn[i - 1])
    tata = []
    i = 0
    while i < len(rader):
        f = rader[i:i + TATA_FONSTER]
        fa = [r.get("app", "") for r in f]
        byten = sum(1 for j in range(1, len(fa)) if fa[j] != fa[j - 1])
        if byten > TATA_GRANS:
            tata.append({"start": f[0]["t"], "slut": f[-1]["t"], "appbyten": byten})
            i += TATA_FONSTER
        else:
            i += 1

    # Urval av bilder, tre sorter.
    # a) Täta byten: första och mittersta bilden i varje period, så att varje period
    #    kommer med och inte bara den första.
    tata_bilder = []
    for t in tata:
        bilder = [_bildfil(dagmapp, r["t"]) for r in rader
                  if r.get("img") and t["start"] <= r["t"] <= t["slut"] and _bildfil(dagmapp, r["t"])]
        if bilder:
            tata_bilder.append(bilder[0])
            if len(bilder) > 2:
                tata_bilder.append(bilder[len(bilder) // 2])
    # b) Övergångar: första bilden i varje pass
    overgangar = [p["_bilder"][0] for p in pass_ if p["_bilder"]]
    # c) Mittersta bilden i de längsta passen
    langsta = [p["_bilder"][len(p["_bilder"]) // 2]
               for p in sorted(pass_, key=lambda x: x["sekunder"], reverse=True)[:LANGSTA_PASS]
               if p["_bilder"]]

    # Täta byten tas först. Det är där kopiera och klistra in och onödiga byten syns,
    # och det är det analysen främst letar efter.
    urval: list[str] = []
    sett: set[str] = set()

    def _ta(kandidater, kvot):
        n = 0
        for b in kandidater:
            if n >= kvot or len(urval) >= MAX_BILDER:
                break
            if b not in sett:
                sett.add(b)
                urval.append(b)
                n += 1

    _ta(tata_bilder, KVOT_TATA)
    _ta(overgangar, KVOT_OVERGANGAR)
    _ta(langsta, KVOT_LANGSTA)
    _ta(tata_bilder + overgangar + langsta, MAX_BILDER)   # fyll upp eventuella lediga platser

    antal_bilder = sum(1 for r in rader if r.get("img") and _bildfil(dagmapp, r["t"]))
    rena_pass = [{k: v for k, v in p.items() if not k.startswith("_")} | {"bilder": len(p["_bilder"])}
                 for p in pass_]

    return {
        "datum": datum,
        "dagmapp": dagmapp,
        "antal_rader": len(rader),
        "antal_bilder": antal_bilder,
        "appbyten": appbyten,
        "tata_byten": tata,
        "appar": appar,
        "antal_pass": len(pass_),
        "pass": rena_pass,
        "bilder_att_titta_pa": urval,
    }


def main() -> int:
    datum = sys.argv[1] if len(sys.argv) > 1 else datetime.now().astimezone().strftime("%Y-%m-%d")
    print(json.dumps(build(datum), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
