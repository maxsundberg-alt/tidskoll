#!/usr/bin/env python3
"""Veckorapport över datortiden, som en HTML-sida på den egna datorn.

Senaste sju dagarna jämfört med veckan innan: aktiv tid, tid per dag, per
kategori med underkategorier, de mest använda apparna och sajterna, och om
blockerade sajter ändå laddades. Är skärmdumpsnivån installerad kommer även
fokusmått med (långa arbetspass, appbyten per timme).

Allt räknas fram lokalt. Inget skickas någonstans.

    python3 veckorapport.py            # skriv rapporten och skriv ut sökvägen
    python3 veckorapport.py --oppna    # skriv och öppna i webbläsaren (så kör launchd den)
"""

from __future__ import annotations

import argparse
import html
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import aw  # noqa: E402

try:
    import arbetspass  # noqa: E402  (skärmdumpsnivån, valfri)
except Exception:
    arbetspass = None

OUT_DIR = Path.home() / "tidskoll" / "rapporter"
MONTHS = ["", "jan", "feb", "mar", "apr", "maj", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]
WEEKDAYS = ["mån", "tis", "ons", "tor", "fre", "lör", "sön"]
URL_PREFIXES = ("aw-watcher-tidskoll-url", "aw-watcher-web")
DEEP_FOCUS_S = 600
BLOCKLISTA = Path.home() / "tidskoll" / "blocklista.txt"
# Titeln på en flik där sajten inte gick att nå. Kontrollerat: Safari på engelska skriver
# "Failed to open page". Antaget: Chrome visar adressen som titel. Andra språk och webbläsare
# kan ha andra titlar; lägg till dem här i gemener om felsidor räknas som laddade.
FELSIDOR = {"failed to open page", ""}


def fetch(periods: list[str], categories: list[dict]) -> list[dict]:
    buckets = aw.get("/buckets/")
    rules = aw.rules(categories)
    out = [{"app": {}, "cat": {}, "dom": {}, "sidor": []} for _ in periods]
    for win, afk in aw.bucket_pairs(buckets):
        res = aw.query(aw.active_query(win, afk, rules, (
            'RETURN = {"app": merge_events_by_keys(active, ["app"]), '
            '"cat": merge_events_by_keys(cats, ["$category"])};'
        )), periods)
        for i, r in enumerate(res):
            for e in r["app"]:
                a = aw.clean(e["data"].get("app", "?"))
                out[i]["app"][a] = out[i]["app"].get(a, 0) + e["duration"]
            for e in r["cat"]:
                k = tuple(e["data"].get("$category") or ["Uncategorized"])
                out[i]["cat"][k] = out[i]["cat"].get(k, 0) + e["duration"]
    for bid in buckets:
        if not bid.startswith(URL_PREFIXES):
            continue
        try:
            res = aw.query([f'events = flood(query_bucket("{bid}"));',
                            'RETURN = merge_events_by_keys(events, ["url", "title"]);'], periods[:1])
        except Exception:
            continue
        for e in res[0]:
            d = urlparse(e["data"].get("url", "")).netloc.removeprefix("www.")
            if d:
                out[0]["dom"][d] = out[0]["dom"].get(d, 0) + e["duration"]
                out[0]["sidor"].append((d, e["data"].get("title") or "", e["duration"]))
    return out


def blocked(week: dict) -> dict | None:
    """Tid på sajter i blocklistan: hur mycket som faktiskt laddade, och hur mycket
    som bara var en flik med felsida som låg framme."""
    if not BLOCKLISTA.exists():
        return None
    lista = [r.strip() for r in BLOCKLISTA.read_text().splitlines()
             if r.strip() and not r.strip().startswith("#")]
    # Samma namn som blockera.sh lägger i /etc/hosts: raden själv plus www. och m.
    blockade = {}
    for b in lista:
        for h in (b, f"www.{b}", f"m.{b}"):
            blockade.setdefault(h, b)
    laddade: dict[str, float] = {}
    dod = 0.0
    for host, title, dur in week["sidor"]:
        traff = blockade.get(host) or blockade.get(f"www.{host}")
        if not traff:
            continue
        if title.strip().lower() in FELSIDOR or title.strip().lower().removeprefix("www.") == host:
            dod += dur
        else:
            laddade[traff] = laddade.get(traff, 0) + dur
    return {"laddade": laddade, "dod": dod}


def total(p: dict) -> float:
    return sum(p["app"].values())


def top_cats(p: dict) -> dict[str, float]:
    t: dict[str, float] = {}
    for k, s in p["cat"].items():
        n = "Okategoriserat" if k[0] == "Uncategorized" else k[0]
        t[n] = t.get(n, 0) + s
    return t


def subcats(p: dict, name: str) -> list[tuple[str, float]]:
    return sorted(((k[1], s) for k, s in p["cat"].items() if len(k) >= 2 and k[0] == name),
                  key=lambda x: x[1], reverse=True)


def focus(days: list[str]) -> dict | None:
    if arbetspass is None:
        return None
    durs, switches, ticks, n = [], 0, 0, 0
    for d in days:
        try:
            b = arbetspass.build(d)
        except Exception:
            continue
        if not b.get("antal_rader"):
            continue
        n += 1
        ticks += b["antal_rader"]
        switches += b.get("appbyten", 0)
        durs += [x["sekunder"] for x in b.get("pass", [])]
    if not n:
        return None
    hours = ticks * arbetspass.SEKUNDER_PER_RAD / 3600
    deep = [s for s in durs if s >= DEEP_FOCUS_S]
    durs.sort()
    return {"dagar": n, "djup_antal": len(deep), "djup_s": sum(deep),
            "median_min": durs[len(durs) // 2] / 60 if durs else 0,
            "vaxlingar_h": switches / hours if hours else 0}


def trend(curr: float, prev: float, suffix: str = "") -> str:
    if prev < 600 or curr < 600:     # under 10 min åt något håll är brus, inte trend
        return ""
    diff = (curr - prev) / prev
    if abs(diff) < 0.05:
        return '<span class="t">samma som förra veckan</span>'
    arrow = "↑" if diff > 0 else "↓"
    return f'<span class="t">{arrow} {abs(round(diff * 100))} %{suffix}</span>'


def esc(s) -> str:
    return html.escape(str(s))


def render(week, prev, days, start, end, colors, fw, bl=None) -> str:
    tot, ptot = total(week), total(prev)
    cats = sorted(top_cats(week).items(), key=lambda kv: kv[1], reverse=True)
    pcats = top_cats(prev)
    day_tot = [(d, total(p)) for d, p in days]
    peak = max((s for _, s in day_tot), default=0) or 1

    rows = []
    for name, s in cats:
        pct = 100 * s / tot if tot else 0
        sub = " · ".join(f"{esc(n)} {aw.fmt_dur(x)}" for n, x in subcats(week, name)[:4] if x >= 60)
        rows.append(
            f'<div class="row"><div class="lbl"><b>{esc(name)}</b>'
            f'<span>{aw.fmt_dur(s)} {trend(s, pcats.get(name, 0))}</span></div>'
            f'<div class="bar"><i style="width:{pct:.1f}%;background:{colors.get(name, "var(--muted)")}"></i></div>'
            + (f'<div class="sub">{sub}</div>' if sub else "") + "</div>")

    dayhtml = "".join(
        f'<div class="day"><div class="col"><i style="height:{100 * s / peak:.0f}%"></i></div>'
        f'<b>{WEEKDAYS[d.weekday()]}</b><span>{aw.fmt_dur(s)}</span></div>' for d, s in day_tot)

    def toplist(d: dict, n=8):
        items = sorted(d.items(), key=lambda kv: kv[1], reverse=True)[:n]
        return "".join(f"<li><span>{esc(k)}</span><b>{aw.fmt_dur(v)}</b></li>" for k, v in items) \
            or "<li><span>Ingen data</span></li>"

    fokus = ""
    if fw:
        part = f" ({fw['dagar']} av 7 dagar)" if fw["dagar"] < 7 else ""
        m = fw["median_min"]
        median = f"{round(m * 60)} s" if m < 1 else f"{m:.1f} min".replace(".", ",")
        fokus = (
            f'<section><h2>Fokus{part}</h2><div class="kpis">'
            f'<div><b>{fw["djup_antal"]}</b><span>pass på 10 min eller mer i samma fönster, '
            f'{aw.fmt_dur(fw["djup_s"])} totalt</span></div>'
            f'<div><b>{fw["vaxlingar_h"]:.0f}</b><span>appbyten per aktiv timme</span></div>'
            f'<div><b>{median}</b><span>mediantid i samma fönster innan du byter</span></div>'
            '</div></section>')

    blockering_html = ""
    if bl is not None:
        tot_l = sum(bl["laddade"].values())
        if tot_l >= 60:
            intro = (f"{aw.fmt_dur(tot_l)} på blockerade sajter som ändå laddades. Antingen var "
                     "blockeringen avstängd, sajten tillfälligt öppnad, eller så kringgår något "
                     "blockeringen (oftast Privat reläservice i Safari).")
        else:
            intro = "Ingen blockerad sajt laddades den här veckan."
        dod = (f'<div class="sub">{aw.fmt_dur(bl["dod"])} var blockerade sajter som bara visade en felsida.</div>'
               if bl["dod"] >= 60 else "")
        blockering_html = (f'<section><h2>Blockerade sajter</h2><div>{intro}</div>{dod}'
                      + (f'<ul style="margin-top:10px">{toplist(bl["laddade"])}</ul>' if tot_l >= 60 else "")
                      + "</section>")

    span = f"{start.day} {MONTHS[start.month]}–{end.day} {MONTHS[end.month]}"
    return f"""<!doctype html><html lang="sv"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tidskoll {span}</title><style>
:root{{--bg:#fafaf8;--fg:#1c1c1a;--muted:#8a8a85;--line:#e6e6e1;--card:#fff;--acc:#2e8b57}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151514;--fg:#ecece8;--muted:#8d8d88;--line:#2c2c2a;--card:#1d1d1b}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,system-ui,sans-serif}}
main{{max-width:760px;margin:0 auto;padding:40px 16px 80px}}h1{{font-size:28px;margin:0 0 4px}}
h2{{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin:0 0 14px}}
section{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px;margin-top:18px}}
.big{{font-size:44px;font-weight:700;letter-spacing:-.02em}}.big small{{font-size:16px;font-weight:400;color:var(--muted);margin-left:8px}}
.t{{color:var(--muted);font-size:13px;margin-left:6px}}
.row{{margin:12px 0}}.lbl{{display:flex;justify-content:space-between;gap:12px}}.lbl span{{color:var(--muted)}}
.bar{{height:8px;background:var(--line);border-radius:4px;margin-top:5px;overflow:hidden}}.bar i{{display:block;height:100%;border-radius:4px}}
.sub{{font-size:13px;color:var(--muted);margin-top:4px}}
.days{{display:grid;grid-template-columns:repeat(7,1fr);gap:8px;text-align:center}}
.col{{height:110px;display:flex;align-items:flex-end;background:var(--line);border-radius:6px;overflow:hidden}}
.col i{{display:block;width:100%;background:var(--acc)}}.day b{{display:block;margin-top:6px;font-size:13px}}.day span{{font-size:12px;color:var(--muted)}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}.two section{{margin-top:0}}
ul{{list-style:none;margin:0;padding:0}}li{{display:flex;justify-content:space-between;gap:10px;padding:5px 0;border-bottom:1px solid var(--line)}}
li span{{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}li b{{font-weight:500;white-space:nowrap}}
.kpis{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}.kpis b{{display:block;font-size:28px}}.kpis span{{font-size:13px;color:var(--muted)}}
footer{{margin-top:24px;font-size:12px;color:var(--muted)}}
@media (max-width:600px){{.two,.kpis{{grid-template-columns:1fr}}.two section{{margin-top:18px}}}}
</style></head><body><main>
<h1>Din vecka vid datorn</h1><div style="color:var(--muted)">{span}</div>
<section><div class="big">{aw.fmt_dur(tot)}<small>aktiv tid, i snitt {aw.fmt_dur(tot / 7)} per dag</small></div>
<div>{trend(tot, ptot, " mot förra veckan") or '<span class="t">ingen jämförelse med förra veckan än</span>'}</div></section>
<section><h2>Per dag</h2><div class="days">{dayhtml}</div></section>
<section><h2>Kategorier</h2>{''.join(rows) or 'Ingen data'}</section>
{fokus}
{blockering_html}
<div class="two" style="margin-top:18px"><section><h2>Appar</h2><ul>{toplist(week["app"])}</ul></section>
<section><h2>Sajter</h2><ul>{toplist(week["dom"])}</ul></section></div>
<footer>Sammanställd på din dator från ActivityWatch {datetime.now():%Y-%m-%d %H:%M}. Bara tid då du satt vid datorn är med.</footer>
</main></body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--oppna", action="store_true", help="öppna rapporten i webbläsaren")
    args = ap.parse_args()

    now = datetime.now().astimezone()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start = today - timedelta(days=6)
    pstart = start - timedelta(days=7)
    day_starts = [start + timedelta(days=k) for k in range(7)]
    periods = [f"{start.isoformat()}/{now.isoformat()}",
               f"{pstart.isoformat()}/{(pstart + (now - start)).isoformat()}",
               *[f"{d.isoformat()}/{min(d + timedelta(days=1), now).isoformat()}" for d in day_starts]]

    try:
        categories = aw.active_categories()
        res = fetch(periods, categories)
    except Exception as e:
        print(f"ActivityWatch svarar inte: {e}", file=sys.stderr)
        return 1
    colors = {c["name"][0]: c.get("data", {}).get("color") for c in categories if len(c["name"]) == 1}
    fw = focus([d.strftime("%Y-%m-%d") for d in day_starts])

    page = render(res[0], res[1], list(zip(day_starts, res[2:])), start, now, colors, fw, blocked(res[0]))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"vecka-{now:%Y-%m-%d}.html"
    out.write_text(page)
    print(out)
    if args.oppna:
        subprocess.run(["open", str(out)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
