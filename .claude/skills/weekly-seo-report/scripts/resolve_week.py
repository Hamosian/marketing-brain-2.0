#!/usr/bin/env python3
"""Resolve the date windows for the weekly organic report.

The window is the **last 7 complete days**, ending yesterday, compared against
the 7 days before that. Pulled on a Thursday this gives Thu-Wed against Thu-Wed,
which is the established convention for this report.

Why 7 days and not a calendar week: organic weekend traffic runs at roughly half
a weekday, so a comparison whose two windows hold different numbers of weekend
days measures the calendar rather than performance. Any multiple of 7 is safe;
anything else is not.

Search Console runs on its **own** window because Windsor lags ~3 days. Pass
--gsc-through with the feed's last clean date to get that window too.

Usage:
    python3 resolve_week.py                          # windows ending yesterday
    python3 resolve_week.py --asof 2026-09-10        # pretend today is this
    python3 resolve_week.py --gsc-through 2026-08-31 # add the GSC windows
    python3 resolve_week.py --json
"""

import json
import sys
from datetime import date, timedelta

WEEK = timedelta(days=7)


def label(start: date, end: date) -> str:
    """Inclusive human label, e.g. 'Sep 3 to 9, 2026' or 'Aug 27 to Sep 2, 2026'."""
    if start.year != end.year:
        return f"{start:%b %-d, %Y} to {end:%b %-d, %Y}"
    if start.month == end.month:
        return f"{start:%b %-d} to {end:%-d}, {end:%Y}"
    return f"{start:%b %-d} to {end:%b %-d}, {end:%Y}"


def pair(last_day: date) -> dict:
    """The 7 days ending last_day, and the 7 before that."""
    cur_start = last_day - timedelta(days=6)
    pri_end = cur_start - timedelta(days=1)
    pri_start = pri_end - timedelta(days=6)
    return {
        "current": {
            "start": cur_start.isoformat(), "end": last_day.isoformat(),
            "label": label(cur_start, last_day), "dow": f"{cur_start:%a} to {last_day:%a}",
        },
        "prior": {
            "start": pri_start.isoformat(), "end": pri_end.isoformat(),
            "label": label(pri_start, pri_end), "dow": f"{pri_start:%a} to {pri_end:%a}",
        },
        "weekend_days_each": sum(
            1 for i in range(7) if (cur_start + timedelta(days=i)).weekday() >= 5),
    }


def holidays_in(start: date, end: date) -> list:
    """Major US/UK holidays that land in the window and distort a weekday.

    Not exhaustive: it covers the movable Mondays that actually move this
    report's numbers. A hit is a prompt to check, never an automatic
    explanation. Anything else still needs a human eye.
    """
    out = []
    d = start
    while d <= end:
        if d.month == 9 and d.weekday() == 0 and d.day <= 7:
            out.append({"date": d.isoformat(), "name": "US Labor Day", "market": "US"})
        if d.month == 8 and d.weekday() == 0 and d.day >= 25:
            out.append({"date": d.isoformat(), "name": "UK summer bank holiday", "market": "UK"})
        if d.month == 5 and d.weekday() == 0 and d.day >= 25:
            out.append({"date": d.isoformat(), "name": "US Memorial Day", "market": "US"})
        if d.month == 11 and d.weekday() == 3 and 22 <= d.day <= 28:
            out.append({"date": d.isoformat(), "name": "US Thanksgiving", "market": "US"})
        d += timedelta(days=1)
    return out


def resolve(today: date, gsc_through: date | None) -> dict:
    funnel = pair(today - timedelta(days=1))
    out = {"pulled": today.isoformat(), "funnel": funnel}
    for side in ("current", "prior"):
        s = date.fromisoformat(funnel[side]["start"])
        e = date.fromisoformat(funnel[side]["end"])
        funnel[side]["holidays"] = holidays_in(s, e)
    if gsc_through:
        out["gsc"] = pair(gsc_through)
        out["gsc"]["lag_days"] = (today - gsc_through).days
    return out


def main(argv: list[str]) -> int:
    as_json = "--json" in argv
    today = date.today()
    gsc = None
    for i, a in enumerate(argv):
        if a in ("--asof", "--gsc-through"):
            if i + 1 >= len(argv):
                print(f"{a} needs a YYYY-MM-DD date", file=sys.stderr)
                return 2
            try:
                value = date.fromisoformat(argv[i + 1])
            except ValueError:
                print(f"{a} needs a YYYY-MM-DD date, got {argv[i + 1]!r}", file=sys.stderr)
                return 2
            if a == "--asof":
                today = value
            else:
                gsc = value
    out = resolve(today, gsc)

    if as_json:
        print(json.dumps(out, indent=2))
        return 0

    f = out["funnel"]
    print(f"Pulled           {out['pulled']}")
    print(f"Funnel current   {f['current']['label']}  ({f['current']['dow']})")
    print(f"Funnel prior     {f['prior']['label']}  ({f['prior']['dow']})")
    print(f"Weekend days     {f['weekend_days_each']} in each window")
    for side in ("current", "prior"):
        for h in f[side]["holidays"]:
            print(f"  HOLIDAY in {side}: {h['name']} ({h['market']}) on {h['date']}")
    if "gsc" in out:
        g = out["gsc"]
        print(f"GSC current      {g['current']['label']}  (feed lag {g['lag_days']} days)")
        print(f"GSC prior        {g['prior']['label']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
