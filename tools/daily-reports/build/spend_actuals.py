#!/usr/bin/env python3
"""Compute the daily reports' invoice-board spend lines from a raw monday response.

Usage:
  python3 spend_actuals.py <board_items.json>

<board_items.json> is the VERBATIM response of the recipe's Step 5 GraphQL query against the
Invoices and Payments - Growth Marketing board (18390740532): one month group, items with
column_values for numeric_mky9safm (Invoice Sum), multiple_person_mkz6t3jw (Payed by) and
color_mm0e2221 (Type). Save the API response unmodified - this script does the parsing so the
run never re-types amounts.

Attribution rules, applied in order per item (the human-canonical copy of these rules lives in
.claude/skills/invoice-board-spend-pulse/knowledge/config.md - change them TOGETHER):
  1. Dor-presence: any Payed by name is Dor Druker -> Growth Channels (his legacy items;
     Savion/Nir were added to them after his 2026-08-04 departure).
  2. Owner-ruled vendor exceptions (Hanan, 2026-08-26): MVF, Saasworthy -> Growth Channels
     (Dor's vendors whose Payed by moved fully off him).
  3. Payer map: every resolved payer is Savion / Dalit / Gili / Ofra -> Creative partnerships
     (Creator Marketing).
  3b. Every resolved payer is Nir -> B2B vendors, its own reported line (Nir, 2026-09-19).
     Hanan / Jonathan (Marketing Ops) stay OUT of every reported line by the same ruling.
  4. Everything else -> other (never guessed into a team). Items in "other" that look like
     Growth Channels work (an affiliate Type, Review Platforms or partnerships, or a blank/mixed
     Payed by involving a mapped payer) are FLAGGED for a human ruling, not attributed.

Rules 1-4 decide WHICH invoices count (the scope). Rule 5 then decides which LINE a counted
invoice lands on, by the board's Type column (Hanan for Nir, 2026-10-04):
  5. Type "Affiliates" -> Affiliates; Type "Affiliate (Freelance and Platforms)", "Freelance",
     "Affiliate Vendors", "Creators Freelancer / Platform Fees" or the retired "Affiliate
     Networks" -> Affiliate freelancers & platforms; Type "B2B Vendors" -> B2B vendors. Any other
     Type (or none) keeps its rule 1-3 line. Rule 5 never pulls an "other" item into a line.
     Why: since Dor left, Savion pays both Creator Marketing and Growth Channels invoices, so
     payer alone filed September's Impact, PartnerStack and Ron Davidman invoices (~$31k) under
     Creative partnerships and left Growth Channels at $0. Type is how the board's owners already
     label each invoice, so it splits them without guessing from the vendor name.

Blank Invoice Sum cells contribute nothing to any sum and are listed separately - a blank is
the absence of a fact, not $0. A numeric 0 is a populated amount.

Output: one JSON object on stdout (see keys below) and a final "SUMMARY:" line. Exits non-zero
when the input is empty, spans more than one group, or the bucket partition fails to reconcile
against the populated-amount total - callers must treat non-zero as "fall back to
manual_inputs.json", never as figures.
"""
import json
import sys

DOR = {"dor druker", "dor.druker@riverside.fm"}
CREATIVE = {
    "savion ron shemesh", "savion.ron@riverside.fm",
    "dalit cordoval", "dalit.cordoval@riverside.fm",
    "gili remen", "gili.remen@riverside.fm",
    "ofra toubiana", "ofra.toubiana@riverside.fm",
}
# B2B vendor spend Nir files himself (Ziff Davis and the like). Reported on its own line rather
# than folded into Growth Channels - Nir's ruling 2026-09-19, when the daily report was dropping
# $14,250 of September B2B vendor spend out of the ROI denominator entirely. Checked AFTER the
# Dor-presence rule, so a legacy item carrying both names still reads as Growth Channels (that is
# how the July "SWZD Ziff Davis" item is attributed, and the ruling did not reopen it).
B2B = {"nir taranto", "nir.taranto@riverside.fm"}
# Owner-ruled vendor -> Growth Channels exceptions (matched on the item-name prefix; board
# convention is "vendor short name, optionally with billing context").
GC_VENDOR_EXCEPTIONS = ("mvf", "saasworthy")
# Rule 5: Type -> line, applied only to items rules 1-3 already counted. Matched casefolded.
# "affiliate networks" was retired from the board's Type column by October 2026; kept so older
# months still split.
AFFILIATE_TYPES = {"affiliates"}
AFFILIATE_FREELANCE_TYPES = {"affiliate (freelance and platforms)", "freelance", "affiliate vendors",
                             "creators freelancer / platform fees", "affiliate networks"}
B2B_TYPES = {"b2b vendors"}
# Type labels that mark an unattributed item as Growth-Channels-suspect (flag, never attribute).
GC_SUSPECT_TYPES = AFFILIATE_TYPES | AFFILIATE_FREELANCE_TYPES | {"review platforms", "partnerships"}


def fail(msg):
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def parse_amount(text):
    """None for blank; float otherwise. Tolerates $ signs and thousands separators."""
    if text is None:
        return None
    cleaned = str(text).strip().replace(",", "").replace("$", "")
    if cleaned == "":
        return None
    return float(cleaned)


def vendor_exception(name):
    n = (name or "").strip().casefold()
    for v in GC_VENDOR_EXCEPTIONS:
        if n == v or (n.startswith(v) and not n[len(v):][:1].isalnum()):
            return True
    return False


def extract_items(payload):
    """Accept the raw GraphQL response (with or without a data wrapper) or a bare item list."""
    if isinstance(payload, list):
        return payload, None
    if "data" in payload and isinstance(payload["data"], dict):
        payload = payload["data"]
    boards = payload.get("boards") or []
    if not boards:
        fail("no boards[] in input - save the query response verbatim")
    groups = boards[0].get("groups") or []
    if len(groups) != 1:
        fail(f"expected exactly one month group, got {len(groups)} - query only the anchor month")
    group = groups[0]
    page = group.get("items_page") or {}
    if page.get("cursor"):
        fail("items_page cursor is not null - page the query until it is, then re-save")
    return page.get("items") or [], group.get("title")


def main():
    if len(sys.argv) != 2:
        fail("usage: spend_actuals.py <board_items.json>")
    with open(sys.argv[1]) as f:
        payload = json.load(f)
    items, month_title = extract_items(payload)
    if not items:
        fail("zero items in the month group")

    buckets = {"creative": [], "growth": [], "affiliates": [], "affiliate_freelance": [],
               "b2b": [], "other": []}
    blanks, flagged = [], []

    for item in items:
        cols = {c.get("id"): (c.get("text") or "") for c in item.get("column_values", [])}
        name = (item.get("name") or "").strip()
        amount = parse_amount(cols.get("numeric_mky9safm"))
        payers = [p.strip().casefold() for p in cols.get("multiple_person_mkz6t3jw", "").split(",")
                  if p.strip()]
        item_type = cols.get("color_mm0e2221", "").strip().casefold()

        if any(p in DOR for p in payers):
            bucket = "growth"
        elif vendor_exception(name):
            bucket = "growth"
        elif payers and all(p in CREATIVE for p in payers):
            bucket = "creative"
        elif payers and all(p in B2B for p in payers):
            bucket = "b2b"
        else:
            bucket = "other"
            reasons = []
            if item_type in GC_SUSPECT_TYPES:
                reasons.append(f"Growth-Channels-suspect Type '{item_type}' with unruled payers")
            if not payers:
                reasons.append("blank Payed by")
            elif any(p in CREATIVE for p in payers):
                reasons.append("mixed Payed by cell includes a Creator Marketing payer")
            if reasons:
                flagged.append({"id": item.get("id"), "name": name,
                                "payed_by": cols.get("multiple_person_mkz6t3jw", ""),
                                "reason": "; ".join(reasons)})

        # Rule 5: a counted item's line comes from its Type; "other" stays out of scope.
        if bucket != "other":
            if item_type in AFFILIATE_TYPES:
                bucket = "affiliates"
            elif item_type in AFFILIATE_FREELANCE_TYPES:
                bucket = "affiliate_freelance"
            elif item_type in B2B_TYPES:
                bucket = "b2b"

        if amount is None:
            blanks.append({"id": item.get("id"), "name": name, "bucket": bucket})
        else:
            buckets[bucket].append(amount)

    sums = {k: round(sum(v), 2) for k, v in buckets.items()}
    populated_total = round(sum(sum(v) for v in buckets.values()), 2)
    counts_ok = sum(len(v) for v in buckets.values()) + len(blanks) == len(items)
    sums_ok = round(sum(sums.values()), 2) == populated_total
    if not (counts_ok and sums_ok):
        fail("bucket partition does not reconcile against the group's populated-amount total")

    result = {
        "month_title": month_title,
        "creative_partnerships_spend": sums["creative"],
        "growth_channels_spend": sums["growth"],
        "affiliates_spend": sums["affiliates"],
        "affiliate_freelancers_spend": sums["affiliate_freelance"],
        "b2b_vendors_spend": sums["b2b"],
        "other_teams_total": sums["other"],
        "populated_total": populated_total,
        "items_total": len(items),
        "item_counts": {k: len(v) for k, v in buckets.items()},
        "blank_amounts": blanks,
        "flagged": flagged,
        "reconcile": "OK",
    }
    print(json.dumps(result, indent=2))
    print(f"SUMMARY: creative={sums['creative']} growth={sums['growth']} "
          f"affiliates={sums['affiliates']} affiliate_freelance={sums['affiliate_freelance']} "
          f"b2b={sums['b2b']} other={sums['other']} items={len(items)} blanks={len(blanks)} "
          f"flagged={len(flagged)} reconcile=OK")


if __name__ == "__main__":
    main()
