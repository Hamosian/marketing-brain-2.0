#!/usr/bin/env python3
"""Render the two Moon at Dawn Slack messages from the funnel.sql result.

Usage:
  python3 render.py rows.json --week-start 2026-09-21 --week-end 2026-09-27 \
      --since 2026-05-28 --asof 2026-09-27 [--exclude excluded.json] [--eng eng.json]

rows.json     the query's result_set.data array, columns in funnel.sql SELECT order
excluded.json [["Creator Name","sep2026"], ...]  post keys that are not live on the board
eng.json      {"Creator Name|may2026": "8.2", ...}  engagement % from the board, when one post maps to one link
Prints message 1 (channel post), a line "=====THREAD=====", then message 2 (thread reply).
"""
import argparse, datetime, json

COLS = ("creator mth first visits visits_wk visits_prev signups signups_wk signups_prev "
        "trials trials_wk trials_prev paid paid_wk paid_prev leads leads_wk leads_prev "
        "mqls mqls_wk mqls_prev sqls sqls_wk sqls_prev won won_mrr").split()

def day(d):
    return datetime.date.fromisoformat(d).strftime("%b %-d")

def n(count, word):
    return f"{count} {word}" if count == 1 else f"{count} {word}s"

def growth(now, before):
    if before == 0:
        return "new" if now > 0 else "flat"
    pct = round((now - before) / before * 100)
    if pct == 0:
        return "flat"
    return f"{'up' if pct > 0 else 'down'} {abs(pct)}%"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rows"); ap.add_argument("--week-start", required=True); ap.add_argument("--week-end", required=True)
    ap.add_argument("--since", required=True); ap.add_argument("--asof", required=True)
    ap.add_argument("--exclude"); ap.add_argument("--eng")
    ap.add_argument("--title", default="weekly funnel", help="e.g. '12-month funnel' for a one-off")
    a = ap.parse_args()
    excluded = {tuple(k) for k in json.load(open(a.exclude))} if a.exclude else set()
    eng = json.load(open(a.eng)) if a.eng else {}
    rows = []
    for raw in json.load(open(a.rows)):
        r = dict(zip(COLS, raw))
        for c in COLS[3:]:
            r[c] = float(r[c] or 0) if c == "won_mrr" else int(r[c] or 0)
        if (r["creator"], r["mth"]) not in excluded and r["first"]:
            rows.append(r)
    tot = lambda k: sum(r[k] for r in rows)
    new_posts = sum(1 for r in rows if a.week_start <= r["first"] <= a.week_end)
    wk = lambda s: f"{tot(s + '_wk')} ({growth(tot(s + '_wk'), tot(s + '_prev'))})"

    m1 = [
        f":crescent_moon: *Moon at Dawn x Riverside: {a.title}*",
        f"_{day(a.week_start)} to {day(a.week_end)}, compared with the week before_",
        "",
        "*This week*",
        f"Posts live {new_posts} new → Visitors {wk('visits')} → Sign-ups {wk('signups')} → Trials {wk('trials')} → Paid {wk('paid')}",
        f"B2B: Leads {wk('leads')} → MQL {wk('mqls')} → SQL {wk('sqls')}",
        "",
    ]
    moved = sorted([r for r in rows if r["visits_wk"] or r["visits_prev"]], key=lambda r: -r["visits_wk"])
    if moved:
        m1.append("*This week by post*")
        for r in moved[:8]:
            extra = "".join(f" · {n(r[k + '_wk'], label)}" for k, label in
                            (("signups", "sign-up"), ("leads", "lead"), ("sqls", "SQL")) if r[k + "_wk"])
            m1.append(f"• {r['creator']} ({day(r['first'])}): {n(r['visits_wk'], 'visitor')} ({growth(r['visits_wk'], r['visits_prev'])}){extra}")
        if len(moved) > 8:
            m1.append(f"• {len(moved) - 8} more posts in the thread")
        m1.append("")
    m1 += [
        f"*Since launch ({day(a.since)})*",
        f"{len(rows)} posts → {n(tot('visits'), 'visitor')} → {n(tot('signups'), 'sign-up')} → {n(tot('trials'), 'trial')} → {tot('paid')} paid",
        f"B2B: {n(tot('leads'), 'lead')} → {tot('mqls')} MQL → {tot('sqls')} SQL → {tot('won')} won",
        "",
        "Funnel for every post in the thread :thread:",
        f"_Source: Riverside analytics, data through {day(a.asof)}_",
        "_Posted by the Marketing OS agent_",
    ]

    hdr = f"{'Post (live date)':<28}{'Eng%':>5}{'Visitors':>9}{'Sign-ups':>9}{'Trial':>6}{'Paid':>5}{'Leads':>6}{'MQL':>5}{'SQL':>5}{'Won':>5}"
    body = [hdr]
    for r in sorted(rows, key=lambda r: (-r["visits"], r["creator"])):
        name = f"{r['creator']} ({day(r['first'])})"
        body.append(f"{name:<28}{eng.get(r['creator'] + '|' + r['mth'], '-'):>5}{r['visits']:>9}{r['signups']:>9}"
                    f"{r['trials']:>6}{r['paid']:>5}{r['leads']:>6}{r['mqls']:>5}{r['sqls']:>5}{r['won']:>5}")
    body.append(f"{'Total':<28}{'':>5}{tot('visits'):>9}{tot('signups'):>9}{tot('trials'):>6}{tot('paid'):>5}"
                f"{tot('leads'):>6}{tot('mqls'):>5}{tot('sqls'):>5}{tot('won'):>5}")
    m2 = [f"*Every live post since {day(a.since)}, full funnel*", "```", *body, "```",
          "_Visitors = unique people who reached riverside.com from that post's link. "
          "Sign-ups, trials and paid are self-serve. Leads to won are B2B, from the CRM._"]
    print("\n".join(m1)); print("=====THREAD====="); print("\n".join(m2))

if __name__ == "__main__":
    main()
