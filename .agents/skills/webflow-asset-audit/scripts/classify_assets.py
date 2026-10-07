#!/usr/bin/env python3
"""Classify a Webflow asset-library page dump for alt-text and naming issues.

Why this exists: `data_assets_tool > list_assets` returns ~110-130KB per 100-asset
page, which blows the context budget if read directly (riverside.com had 5,642
assets / 57 pages as of 2026-07-27). Only this script's *output* costs tokens.

Usage:
    python3 classify_assets.py [--out findings.ndjson] <page-dump.json> [more...]

Each input is the raw tool result saved by the MCP client (an object with
.result.assets[], or a bare list of assets). Prints per-file counts, pattern
prevalence, and the rename-vs-URL divergence check, then a machine-readable
JSON summary on the last line.

Pass --out to write one NDJSON record per flagged asset (asset id, display name,
original altText, contentType, issues). The workflow needs those IDs to preview
images, get wording approved, and issue updates - so use --out for any run that
will actually fix something, and slice the file with jq rather than reading it
whole.

Stdlib only. Read-only: this never writes to Webflow.
"""

import json
import re
import sys
import urllib.parse
from collections import Counter

# Patterns observed in riverside.com's actual library (2026-07-27 audit).
# NOTE: upstream webflow-skills looks for IMG_/DSC_/screenshot/untitled in
# display names - those scored ZERO here. Figma export artifacts and versioning
# suffixes are the real signal. Keep this list evidence-based: re-run the audit
# before adding a pattern on intuition.
NAME_PATTERNS = {
    "figma-frame": re.compile(r"\bFrame[\s_-]*\d", re.I),
    "figma-group": re.compile(r"\bGroup[\s_-]*\d", re.I),
    "figma-primitive": re.compile(r"\b(Rectangle|Vector|Ellipse|Button Text|Union|Subtract)\b", re.I),
    "versioned-copy": re.compile(r"\(\d+\)"),
    "meaningless-short": re.compile(r"^[a-z0-9]{2,7}\.(webp|png|avif|svg|jpe?g)$", re.I),
    "camera-original": re.compile(r"\b(IMG|DSC|DSCF|DCIM)[\s_-]*\d", re.I),
    "screenshot": re.compile(r"screen[\s_-]*shot|screenshot|capture", re.I),
    "untitled-generic": re.compile(r"\b(untitled|asset|image|photo)\b[\s_-]*\(?\d*\)?\.", re.I),
    "double-space": re.compile(r"  +"),
    "has-space": re.compile(r" "),
    "has-uppercase": re.compile(r"[A-Z]"),
    "has-underscore": re.compile(r"_"),
}

REDUNDANT_ALT = re.compile(r"^\s*(image|picture|photo|graphic|icon|screenshot)\s+(of|showing|that)\b", re.I)
# A filename masquerading as alt text: extension, or internal build-label shape.
ALT_LOOKS_LIKE_FILENAME = re.compile(
    r"\.(webp|png|avif|svg|jpe?g|mp4)\s*$|^[\w\s-]*_\d{4}_\d{2}|\b(desktop|mobile)\s*$", re.I
)


def load_assets(path):
    with open(path) as fh:
        data = json.load(fh)
    if isinstance(data, list):
        return data
    if "result" in data:
        return data["result"].get("assets", [])
    return data.get("assets", [])


def url_filename(asset):
    """The filename a crawler actually sees, minus Webflow's 24-hex prefix."""
    tail = urllib.parse.unquote(asset.get("hostedUrl", "")).rsplit("/", 1)[-1]
    if "_" in tail[:26]:
        return tail.split("_", 1)[1]
    return tail


def classify(assets):
    out = {
        "n": len(assets),
        "alt_missing": 0,
        "alt_set": 0,
        "alt_redundant_framing": 0,
        "alt_looks_like_filename": 0,
        "alt_very_short": 0,
        "patterns": Counter(),
        "renamed_url_diverged": 0,
        "alt_lengths": [],
        "flagged": [],
    }
    by_size = Counter()

    for a in assets:
        name = a.get("displayName") or ""
        # Normalize before classifying: a whitespace-only altText is missing alt,
        # not "set". Without the collapse, "      " (>=10 chars) evades both the
        # empty check and the too-short check and reads as healthy.
        alt = a.get("altText")
        alt = re.sub(r"\s+", " ", alt).strip() if isinstance(alt, str) else alt
        issues = []

        if not alt:
            out["alt_missing"] += 1
            issues.append("missing-alt")
        else:
            out["alt_set"] += 1
            out["alt_lengths"].append(len(alt))
            if REDUNDANT_ALT.search(alt):
                out["alt_redundant_framing"] += 1
                issues.append("redundant-alt-framing")
            if ALT_LOOKS_LIKE_FILENAME.search(alt):
                out["alt_looks_like_filename"] += 1
                issues.append("alt-is-a-filename")
            if len(alt) < 10:
                out["alt_very_short"] += 1
                issues.append("alt-too-short")

        for label, rx in NAME_PATTERNS.items():
            if rx.search(name):
                out["patterns"][label] += 1
                # Only the substantive naming problems are per-asset findings;
                # space/uppercase/underscore are near-universal here and would
                # drown the report if flagged individually.
                if label not in ("has-space", "has-uppercase", "has-underscore"):
                    issues.append(label)

        if name and url_filename(a) != name:
            out["renamed_url_diverged"] += 1

        size = a.get("size")
        if size:
            by_size[size] += 1

        if issues:
            out["flagged"].append({
                "id": a.get("id"),
                "name": name,
                # The ORIGINAL value, not the normalized one - this is what a revert
                # would restore, so it has to round-trip exactly.
                "original_alt": a.get("altText"),
                "content_type": a.get("contentType"),
                "issues": sorted(set(issues)),
            })

    # Report clusters and the assets inside them, not a combinatorial pair count:
    # "5 assets across 2 size clusters" is what a human triaging duplicates needs,
    # whereas 3 same-size assets are 3 "pairs" but only 1 thing to look at.
    out["duplicate_clusters"] = sum(1 for c in by_size.values() if c > 1)
    out["duplicate_cluster_assets"] = sum(c for c in by_size.values() if c > 1)
    return out


def main():
    args = sys.argv[1:]
    out_path = None
    if "--out" in args:
        i = args.index("--out")
        if i + 1 >= len(args):
            print("error: --out requires a path", file=sys.stderr)
            return 2
        out_path = args[i + 1]
        args = args[:i] + args[i + 2:]

    paths = args
    if not paths:
        print(__doc__)
        return 1

    totals = Counter()
    all_lengths = []
    all_flagged = []
    pattern_totals = Counter()

    for path in paths:
        assets = load_assets(path)
        r = classify(assets)
        print(f"\n=== {path.rsplit('/', 1)[-1]} (n={r['n']}) ===")
        print(f"  alt missing/empty : {r['alt_missing']}  ({pct(r['alt_missing'], r['n'])})")
        print(f"  alt set           : {r['alt_set']}")
        print(f"    ...redundant framing : {r['alt_redundant_framing']}")
        print(f"    ...looks like a filename : {r['alt_looks_like_filename']}")
        print(f"    ...under 10 chars    : {r['alt_very_short']}")
        print(f"  renamed (URL keeps original name) : {r['renamed_url_diverged']}")
        print(f"  duplicate candidates : {r['duplicate_cluster_assets']} assets "
              f"across {r['duplicate_clusters']} same-size cluster(s)")
        print("  name patterns:")
        for label, c in r["patterns"].most_common():
            print(f"    {label:22} {c}")

        for k in ("n", "alt_missing", "alt_set", "alt_redundant_framing",
                  "alt_looks_like_filename", "alt_very_short", "renamed_url_diverged"):
            totals[k] += r[k]
        pattern_totals.update(r["patterns"])
        all_lengths += r["alt_lengths"]
        all_flagged += r["flagged"]

    if all_lengths:
        all_lengths.sort()
        mid = all_lengths[len(all_lengths) // 2]
        over = sum(1 for x in all_lengths if x > 125)
        print(f"\n=== alt length (set only, n={len(all_lengths)}) ===")
        print(f"  min={all_lengths[0]} median={mid} max={all_lengths[-1]}")
        print(f"  over 125 chars: {over} ({pct(over, len(all_lengths))}) "
              " - length alone is NOT a defect; check for padding, not char count")

    print(f"\n=== TOTAL across {len(paths)} page(s) ===")
    for k, v in totals.items():
        print(f"  {k:32} {v}")
    print(f"  flagged assets (any issue)       {len(all_flagged)}")

    # Per-asset findings are the point of the run - the workflow needs asset IDs to
    # preview, get wording approved, and update. Counts alone would force a return to
    # the raw page dumps, which are exactly what does not fit in context.
    if out_path:
        with open(out_path, "w") as fh:
            for f in all_flagged:
                fh.write(json.dumps(f) + "\n")
        print(f"\nFindings written: {out_path} ({len(all_flagged)} assets, NDJSON)")
        print("  Read it, or slice it - e.g. only the missing-alt ones:")
        print(f"  jq -c 'select(.issues | index(\"missing-alt\"))' {out_path} | head -20")
    else:
        print("\nNo findings file written (pass --out <path.ndjson> to emit per-asset "
              "records with IDs - required for the preview/approve/update steps).")
        # Still surface a few so a run without --out is not a dead end.
        for i, f in enumerate(all_flagged[:5], 1):
            print(f"  [{i}] {f['name']} - {', '.join(f['issues'])}")
        if len(all_flagged) > 5:
            print(f"  ... and {len(all_flagged) - 5} more")

    print("\nJSON_SUMMARY " + json.dumps({
        "totals": dict(totals),
        "patterns": dict(pattern_totals),
        "flagged_count": len(all_flagged),
        "findings_file": out_path,
    }))
    return 0


def pct(part, whole):
    return f"{round(part * 100 / whole)}%" if whole else "n/a"


if __name__ == "__main__":
    sys.exit(main())
