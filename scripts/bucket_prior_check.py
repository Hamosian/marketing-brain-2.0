#!/usr/bin/env python3
"""Re-validate the Type -> Bucket? priors that /ticket-hygiene relies on.

The skill auto-populates Bucket? on the MOPs board (6257866754) only for three Types,
because the board's own labelling does not support inferring it more widely. Those priors
were measured on 2026-08-23 and will drift as the board grows. This script re-measures them
so the claim in .claude/skills/ticket-hygiene/knowledge/config.md stays auditable.

Input: JSON from a monday query of the MOPs board, e.g.

  query { boards(ids: ["6257866754"]) { items_page(limit: 400) { items {
    name column_values(ids: ["status_11","color_mkzspv3r"]) { id text } } } } }

Usage:  python3 scripts/bucket_prior_check.py items.json [--threshold 70]
Exit 1 if any shipped prior falls below the threshold - that means the config is stale.
"""
import json, re, sys, collections

SHIPPED = {"Reporting/Dashboard": 2, "Biz Process": 5, "Messaging": 3}
THRESHOLD = 70.0


def load(path):
    raw = json.load(open(path))
    items = raw["boards"][0]["items_page"]["items"]
    out = []
    for it in items:
        cv = {c["id"]: (c.get("text") or "") for c in it.get("column_values", [])}
        typ, buck = cv.get("status_11", ""), cv.get("color_mkzspv3r", "")
        if not buck:
            continue
        m = re.match(r"Bucket (\d)", buck)
        if m:
            out.append((typ, int(m.group(1))))
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    thr = THRESHOLD
    if "--threshold" in sys.argv:
        thr = float(sys.argv[sys.argv.index("--threshold") + 1])
    data = load(args[0])
    if not data:
        print("no labelled items found")
        return 2

    by_type = collections.defaultdict(collections.Counter)
    for typ, buck in data:
        by_type[typ][buck] += 1

    print(f"{len(data)} labelled items\n")
    print("shipped priors:")
    failed = []
    covered = correct = 0
    for typ, expect in SHIPPED.items():
        c = by_type.get(typ)
        if not c:
            print(f"  {typ:22} MISSING from sample")
            failed.append(typ)
            continue
        n = sum(c.values())
        hit = c[expect]
        pct = 100.0 * hit / n
        covered += n
        correct += hit
        flag = "" if pct >= thr else "  <-- BELOW THRESHOLD"
        print(f"  {typ:22} -> B{expect}  n={n:3}  {pct:5.1f}%{flag}")
        if pct < thr:
            failed.append(typ)
    if covered:
        print(f"\n  coverage {covered}/{len(data)} = {100.0*covered/len(data):.0f}% "
              f"of the board, precision {100.0*correct/covered:.1f}%")

    baseline_hit = sum(c.most_common(1)[0][1] for c in by_type.values())
    print(f"\nbaseline for comparison - every Type mapped to its modal Bucket: "
          f"{100.0*baseline_hit/len(data):.1f}% "
          f"(was 59.7% on 2026-08-23; this is why the envelope is narrow)")

    print("\nfull Type -> Bucket distribution:")
    for typ in sorted(by_type, key=lambda t: -sum(by_type[t].values())):
        c = by_type[typ]
        n = sum(c.values())
        dist = " ".join(f"B{b}:{k}" for b, k in sorted(c.items()))
        print(f"  {typ:22} n={n:3}  {dist}")

    if failed:
        print(f"\nFAIL: {', '.join(failed)} no longer meet the {thr:.0f}% bar. "
              f"Update the envelope table in .claude/skills/ticket-hygiene/knowledge/config.md.")
        return 1
    print(f"\nOK: all shipped priors still at or above {thr:.0f}%.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
