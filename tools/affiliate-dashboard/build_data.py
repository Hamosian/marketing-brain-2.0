#!/usr/bin/env python3
"""Assemble dashboard_data.json for the Affiliate Channel Funnel dashboard.

Reads intermediate files from WORKDIR (default: current directory), produced
by the HubSpot pulls described in REFRESH.md:

  contacts.json             list of contact dicts already in output shape (Step 1)
  deals_raw.json            {deal_id: <hubspot properties dict>}          (Step 2)
  deal_sources.json         {deal_id: [source, ...]}                      (Step 3)
  contact_deal_links.json   optional, {contact_id: [{"dealstage","pipeline",
                            "stage_category","createdate"}, ...]} for every
                            cohort contact (Step 3.5) - backfills missing
                            meeting dates AND dates each deal's first meeting
  meeting_booked_lookup.json  optional, {contact_id: "YYYY-MM-DD"} meeting_booked
                            date for the same contacts, when HubSpot has it (Step 3.5)

Writes dashboard_data.json into WORKDIR and prints a sanity report. Usage:

  python3 build_data.py [WORKDIR]
"""
import json, datetime, sys, os
from collections import Counter

WORKDIR = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
PORTAL = "9154210"

# A contact is in the cohort if utm_medium/meeting_medium_cp = affiliate OR its
# source is a named partner (Step 1). Contacts caught only by the medium filter can
# have no utm_source and no meeting_source_cp at all. They are still real affiliate
# records, so they get this explicit tag instead of being discarded - otherwise
# they'd be pulled, counted in the header total and findable in search, yet invisible
# in every source-filtered tile (which contradicts tile 4's "every affiliate record").
NO_SOURCE_TAG = "affiliate (no source)"

# Source aliases: some affiliate partners are the same company under two source
# tags in HubSpot and must be merged into one on the dashboard. "landd" (L&D) and
# "boscia group" are the same partner, folded under "boscia group". "unknown" (no
# source field on a medium-only affiliate contact/deal) is folded into NO_SOURCE_TAG
# so it becomes a real, selectable chip rather than being dropped. Apply norm() to
# every source tag the moment it's derived, so chips, filtering and attribution all
# treat them consistently. The raw HubSpot value is still what Step 1's pull filters
# on (see REFRESH.md); only the emitted/displayed tag is normalized.
SOURCE_ALIASES = {"landd": "boscia group", "unknown": NO_SOURCE_TAG}


def norm(s):
    return SOURCE_ALIASES.get(s, s)


TARGET_SOURCES = {"ziffdavis", "memoryblue", "pursuit", "boscia group"}

# HubSpot pipeline id -> human label
PIPELINE_LABELS = {
    "29354026": "Pre-Opp - Agency (SMB)",
    "29152011": "Pre-Opp - Enterprise",
    "916013614": "Pre-Opp - EU Enterprise",
    "89765536": "Pre-Opp - Europe",
    "9297003": "Agency New Sales",
    "916006193": "EU Enterprise New Sale",
    "9308023": "Enterprise New Sales",
    "89892425": "Europe New Sales",
    "3711152": "Renewals",
    "33402955": "Upsell Pipeline",
    "891525221": "Account Expansion",
    "2662763": "Partnership & Channel Sales",
    "71445776": "Influencer Marketing",
}

# HubSpot dealstage id -> funnel bucket
STAGE_LABELS = {
    "67154602": "Action Required", "66605109": "Action Required", "1397905039": "Action Required", "166509137": "Action Required",
    "1033613941": "Meeting Booked", "1031377048": "Meeting Booked", "1397905040": "Meeting Booked", "1033614704": "Meeting Booked",
    "69180237": "Follow-Up Stage", "69198923": "Follow-Up Stage", "1397905043": "Follow-Up Stage", "166509139": "Follow-Up Stage",
    "67154607": "Promoted to Deal", "66605111": "Promoted to Deal", "1397905044": "Promoted to Deal", "166509142": "Promoted to Deal",
    "67154608": "Closed Lost", "66605113": "Closed Lost", "1397905045": "Closed Lost", "166509143": "Closed Lost",
    "66605110": "Intro Completed", "1397905041": "Intro Completed",
    "1214348650": "Demo Completed", "1397905042": "Demo Completed",
    "26497054": "S1", "1397903671": "S1", "26589195": "S1",
    "26497055": "S2", "1397903672": "S2", "26589196": "S2",
    "26497056": "S3", "1397903673": "S3", "26589197": "S3",
    "26497057": "S4", "1397903674": "S4", "26589198": "S4",
    "49153958": "S5", "1397903675": "S5", "26589199": "S5",
    "26497058": "S6", "1397903676": "S6", "26588039": "S6",
    "199756209": "S7", "1397903677": "S7", "26588040": "S7",
    "48484985": "S7",  # S8 Pending Payment folded into S7
    "26497059": "Closed won", "1397903678": "Closed won",
    "26497060": "Closed Lost", "1397903679": "Closed Lost",
    # manually inferred (absent from the truncated dealstage enum dump)
    "166590829": "S1", "166590834": "Closed won", "166590835": "Closed Lost",
    "166590832": "S2",  # Europe New Sales pipeline, open stage between S1 (829) and
                        # Closed won (834) - inferred S2 from numeric position (2026-08-30 refresh).
    "13281636": "Active Client",
    "199765128": "S1",  # Europe New Sales early open stage, inferred S1
    "1343770515": "Active Client",  # Account Expansion pipeline, open expansion stage (e.g.
                                     # Bain add'l license + webinar) - expansion revenue on an
                                     # ALREADY-ACTIVE customer, same treatment as Renewals
                                     # (13281636 above), never a fresh "S1" opportunity. A prior
                                     # fix mapped this to S1 just to silence the UNMAPPED STAGES
                                     # warning without addressing the miscategorization, which is
                                     # why it kept resurfacing - see retro 2026-08-30.
}

# Pipelines whose deals represent expansion/upsell revenue on an ALREADY-ACTIVE
# customer account, not progress through a new-business sales cycle (see
# systems/owned/hubspot.md's pipeline table). Two distinct uses below:
#  1. bucket_of() still maps any of their stages to "Active Client" (never the
#     generic "S1" default) so Step 3.5's meeting-completion inference - which
#     only cares whether a meeting demonstrably happened - keeps working.
#  2. The deals_out loop further down EXCLUDES every deal in these pipelines
#     from the dashboard entirely (tile 4, Vendor ROI, everywhere) and instead
#     flags it in the sanity report for manual verification. A deal here means
#     the account was ALREADY a customer before this affiliate touch, so - per
#     Nir, 2026-08-30 (Bain & Company Account Expansion deal) - it is not
#     evidence the affiliate channel sourced anything and must never be
#     counted, even as "Active Client". If the affiliate meeting genuinely
#     brought NEW business, that shows up as its own Pre-Opp/New-Sales deal
#     and IS counted normally - only the existing-customer expansion deal
#     itself is excluded.
EXPANSION_PIPELINES = {"891525221", "33402955"}  # Account Expansion, Upsell Pipeline

# Stages after (and including) the intro meeting - a deal can't reach any of these
# without the meeting having happened. Used to backfill meeting-completed dates
# that HubSpot's contact-level property drops once a deal moves past intro (see
# meeting_completed_effective below).
POST_INTRO_BUCKETS = {"Follow-Up Stage", "Promoted to Deal", "S1", "S2", "S3", "S4",
                      "S5", "S6", "S7", "Closed won", "Active Client"}

# Ascending sales progression, used to compute the FURTHEST stage a Closed-Lost
# deal ever reached from its dealstage history (the `hs_v2_date_entered_<id>`
# timestamps pulled per lost deal - see REFRESH.md). Terminal / non-progress
# buckets ("Closed Lost", "Promoted to Deal") are intentionally NOT ranked here:
# they never count as the "high-water mark" a deal reached before it was lost.
PEAK_ORDER = ["Action Required", "Meeting Booked", "Intro Completed", "Follow-Up Stage",
              "Demo Completed", "S1", "S2", "S3", "S4", "S5", "S6", "S7",
              "Closed won", "Active Client"]
PEAK_RANK = {b: i for i, b in enumerate(PEAK_ORDER)}


def peak_stage_from_history(hist):
    """hist = {stageId: entered_date_iso}. Return the furthest-progressed bucket
    the deal ever entered, by PEAK_ORDER, or None if none qualify."""
    best, best_rank = None, -1
    for sid in (hist or {}):
        bucket = STAGE_LABELS.get(sid)
        rank = PEAK_RANK.get(bucket, -1)
        if rank > best_rank:
            best, best_rank = bucket, rank
    return best

# Fixed business order for the funnel tile (NOT alphabetical / by volume).
# "Promoted to Deal" is deliberately excluded: it's a stale marker left on the
# originating Pre-Opp record once a real Deal record is created for the same
# opportunity. That Deal gets its own bucket further down this same list (S1-S7,
# Closed won/Lost, Active Client), so counting "Promoted to Deal" too would count
# the same opportunity twice - same double-count risk the MRR rule below avoids
# for Renewals.
#
# "Intro Completed" and "Demo Completed" must stay in this list - they were
# accidentally missing before 2026-08-30, and tile 4's render4() only builds a
# row per bucket named in DATA.funnel_order; any bucket not listed here (other
# than the deliberate Promoted-to-Deal exclusion above) is silently dropped
# with no error, not "shown as zero". Bug found via Nir noticing boscia
# group's SQL count (9) didn't match its visible tile-4 total (4): 8 real
# deals across the whole snapshot (6 Intro Completed + 2 Demo Completed) were
# invisible in every tile-4 view and every source filter. Adding a new bucket
# name to STAGE_LABELS is not enough on its own - it must also be added here,
# and to FUNNEL_LABELS (and ideally ORDINAL_STAGES) in dashboard_template.html,
# or it renders as literal "undefined" text instead of a bar.
FUNNEL_ORDER = ["Closed Lost", "Action Required", "Meeting Booked", "Intro Completed",
                "Follow-Up Stage", "Demo Completed",
                "S1", "S2", "S3", "S4", "S5", "S6", "S7", "Closed won", "Active Client"]


def bucket_of(stage_id, pipeline_id, stage_category, record_type):
    """Map a deal to a funnel bucket. If the stage id is unknown, fall back to
    Won/Lost/open reasoning the same way the label map was built."""
    label = STAGE_LABELS.get(stage_id)
    if label:
        return label
    if stage_category == "Won":
        return "Closed won"
    if stage_category == "Lost":
        return "Closed Lost"
    if pipeline_id in EXPANSION_PIPELINES:
        return "Active Client"
    return "S1"


def deal_url(did):
    return f"https://app.hubspot.com/contacts/{PORTAL}/record/0-3/{did}"


def load(name):
    return json.load(open(os.path.join(WORKDIR, name)))


contacts_out = load("contacts.json")
# `email` is passed straight through to the output (shown next to the contact
# name in the click-through panel and used by the top-bar search). Guarantee the
# key exists so an older contacts.json pulled without it still builds cleanly.
for _c in contacts_out:
    _c.setdefault("email", None)


def contact_source_tag(c):
    return norm(c.get("utm_source") or c.get("meeting_source_cp") or "unknown")


deals_raw = load("deals_raw.json")        # id -> properties
deal_sources = load("deal_sources.json")  # id -> [sources]


def load_optional(name):
    path = os.path.join(WORKDIR, name)
    return json.load(open(path)) if os.path.exists(path) else {}


# {deal_id: {stageId: entered_date_iso}} for Closed-Lost deals (see REFRESH.md).
closed_lost_stage_history = load_optional("closed_lost_stage_history.json")

unknown_stages = Counter()
deals_out = []
# Existing-customer-pipeline deals excluded from every count/tile above (see
# EXPANSION_PIPELINES) - printed in the sanity report for a human to check by
# hand, never silently folded into the dashboard.
flagged_existing_customer_deals = []
for did, p in deals_raw.items():
    stage_id = p.get("dealstage")
    pipeline_id = p.get("pipeline")
    if pipeline_id in EXPANSION_PIPELINES:
        flagged_existing_customer_deals.append({
            "id": did,
            "name": p.get("dealname", "") or f"Deal {did}",
            "pipeline": PIPELINE_LABELS.get(pipeline_id, pipeline_id),
            "sources": sorted({norm(s) for s in deal_sources.get(did, [])}) or [NO_SOURCE_TAG],
            "url": deal_url(did),
        })
        continue
    if stage_id not in STAGE_LABELS:
        unknown_stages[(pipeline_id, stage_id, p.get("stage_category"))] += 1
    bucket = bucket_of(stage_id, pipeline_id, p.get("stage_category"), p.get("record_type"))
    mrr = p.get("hs_mrr")
    try:
        mrr_val = float(mrr) if mrr not in (None, "") else None
    except ValueError:
        mrr_val = None
    amount = p.get("amount")
    try:
        amount_val = float(amount) if amount not in (None, "") else None
    except ValueError:
        amount_val = None
    peak = peak_stage_from_history(closed_lost_stage_history.get(did)) if bucket == "Closed Lost" else None
    deals_out.append({
        "id": int(did),
        "name": p.get("dealname", "") or f"Deal {did}",
        "pipeline": PIPELINE_LABELS.get(pipeline_id, pipeline_id),
        "record_type": p.get("record_type"),
        "bucket": bucket,
        "stage_category": p.get("stage_category"),
        "mrr": mrr_val,
        "amount": amount_val,
        "createdate": (p.get("createdate") or "")[:10] or None,
        "closedate": (p.get("closedate") or "")[:10] or None,
        # A cohort deal with no attributed source is still an affiliate deal (its
        # cohort contact came in medium-only); tag it NO_SOURCE_TAG so it stays
        # visible under its own chip instead of being filtered out everywhere.
        "sources": sorted({norm(s) for s in deal_sources.get(did, [])}) or [NO_SOURCE_TAG],
        "peak_stage": peak,
        "url": deal_url(did),
    })

contact_deal_links = load_optional("contact_deal_links.json")   # contact_id -> [deal link dicts]
meeting_booked_lookup = load_optional("meeting_booked_lookup.json")  # contact_id -> "YYYY-MM-DD"

# A linked deal's createdate is only trustworthy as *this contact's* meeting date
# if the deal didn't already exist before the contact did. When a deal predates
# the contact by more than a few days, the contact is almost always a later
# stakeholder added to an already-in-motion deal (an account teammate looped in
# later), not the person whose meeting created it - confirmed on real examples
# with gaps of 25 to 739 days. In that case we know a meeting happened somewhere
# in this contact's history, but not a safe date for it, so it's left un-dated
# (surfaced separately) rather than plotted on a fabricated week/month.
DEAL_PREDATES_CONTACT_GRACE_DAYS = 7

backfilled = 0
undated = 0
for c in contacts_out:
    cid = str(c["id"])
    if c.get("meeting_completed"):
        c["meeting_completed_effective"] = c["meeting_completed"]
        c["meeting_completed_inferred"] = False
        c["meeting_confirmed_undated"] = False
        continue
    links = contact_deal_links.get(cid, [])
    post_intro_links = [
        l for l in links
        if bucket_of(l.get("dealstage"), l.get("pipeline"), l.get("stage_category"), None) in POST_INTRO_BUCKETS
    ]
    if not post_intro_links:
        c["meeting_completed_effective"] = None
        c["meeting_completed_inferred"] = False
        c["meeting_confirmed_undated"] = False
        continue
    booked = meeting_booked_lookup.get(cid)
    contact_created = c.get("createdate")
    if booked:
        fallback_date = booked
    else:
        plausible_dates = []
        for l in post_intro_links:
            d = (l.get("createdate") or "")[:10]
            if not d:
                continue
            if contact_created:
                gap = (datetime.date.fromisoformat(contact_created) - datetime.date.fromisoformat(d)).days
                if gap > DEAL_PREDATES_CONTACT_GRACE_DAYS:
                    continue
            plausible_dates.append(d)
        fallback_date = min(plausible_dates) if plausible_dates else None
    c["meeting_completed_effective"] = fallback_date
    c["meeting_completed_inferred"] = bool(fallback_date)
    c["meeting_confirmed_undated"] = not fallback_date
    if fallback_date:
        backfilled += 1
    else:
        undated += 1

# ---- each deal's meeting date (feeds tile 4's Month / Quarter filter) ----
# A deal's meeting date = the earliest meeting_completed_effective among the cohort
# contacts linked to it (same date tile 2 plots). None when no linked contact has a
# date - tile 4 then leaves the deal out of any Month/Quarter view and counts it in
# the footer instead of dropping it silently.
# Guard: a contact's meeting only dates a deal if it happened no more than
# MEETING_BEFORE_DEAL_GRACE_DAYS before the deal was created - a meeting from
# before the deal existed was not that deal's meeting. Found 2026-09-24: a Ziff
# Davis staffer (Charles Green, swzd.com) sits on every Ziff pre-opp with his own
# 2026-02-20 meeting date, which would otherwise date all 67 of them to February.
MEETING_BEFORE_DEAL_GRACE_DAYS = 7
deal_created = {str(d["id"]): d["createdate"] for d in deals_out}
deal_meeting = {}
for c in contacts_out:
    eff = c.get("meeting_completed_effective")
    if not eff:
        continue
    for l in contact_deal_links.get(str(c["id"]), []):
        did = str(l.get("deal_id") or "")
        created = deal_created.get(did)
        if not created:
            continue
        if (datetime.date.fromisoformat(created) - datetime.date.fromisoformat(eff)).days > MEETING_BEFORE_DEAL_GRACE_DAYS:
            continue
        if did not in deal_meeting or eff < deal_meeting[did]:
            deal_meeting[did] = eff
for d in deals_out:
    d["meeting_date"] = deal_meeting.get(str(d["id"]))

all_sources = set(TARGET_SOURCES)
for c in contacts_out:
    all_sources.add(contact_source_tag(c))
for d in deals_out:
    all_sources.update(d["sources"])
all_sources.discard("unknown")

# ---- per-vendor ROI (feeds the Vendor ROI section) ----
# Costs = cumulative PAID invoices per vendor from the Invoices & Payments board
# (Dor's board), pulled separately into vendor_costs.json (optional). Everything
# else is derived from this snapshot:
#   SQLs      = completed meetings (tile-2 definition), attributed by contact tag
#   S1s       = records that REACHED S1 or beyond (furthest stage), by deal source
#   customers = closed-won deals, by deal source
#   ARR       = closed-won MRR x 12, by deal source
#   ROI       = ARR / cost (a multiple)
# "Promoted to Deal" pre-opps are excluded from S1s for the same
# double-count reason the funnel excludes them (the resulting Deal is counted).
S1_PLUS = {"S1", "S2", "S3", "S4", "S5", "S6", "S7", "Closed won", "Active Client"}
vendor_costs = load_optional("vendor_costs.json")   # {tag: {"paid","all","invoices"}}

# Manual cost corrections that win over the board pull. The Invoices board's
# "Payment Done" checkbox is under-maintained for some vendors, so the pulled
# `paid` sum can understate real spend. Confirmed override: Pursuit was actually
# paid $30,000 (two invoices) though only one is checked paid on the board
# (Nir, 2026-08-10). Keep this file the single place such corrections live.
vendor_cost_overrides = load_optional("vendor_costs_overrides.json")  # {tag: {"paid": X}}
for _tag, _ov in vendor_cost_overrides.items():
    vendor_costs.setdefault(_tag, {})
    vendor_costs[_tag].update(_ov)


def furthest_bucket(d):
    if d["bucket"] == "Closed Lost":
        return d.get("peak_stage")          # may be None
    return d["bucket"]


roi_tags = set(all_sources) | set(vendor_costs.keys())
roi_tags.discard("unknown")
vendor_roi = []
for tag in roi_tags:
    completed = [c for c in contacts_out
                 if c.get("meeting_completed_effective") and contact_source_tag(c) == tag]
    sqls = len(completed)
    # A deal is per-account, not per-contact (see Bain & Company, 2026-08-30: two
    # separate boscia-sourced contacts, Dan Simon and Nicholas Callanta, both
    # completed their own meeting but share the one Bain Pre-Opp deal record) - so
    # "how many companies actually had a meeting" is a different, equally real
    # number from "how many people did". Contacts missing a company property each
    # count as their own distinct company rather than being merged into one bucket
    # or dropped.
    companies = len({c.get("company") or f"__contact_{c['id']}" for c in completed})
    s1s = customers = 0
    arr = 0.0
    for d in deals_out:
        if tag not in d["sources"]:
            continue
        if d["bucket"] != "Promoted to Deal" and furthest_bucket(d) in S1_PLUS:
            s1s += 1
        if d["bucket"] == "Closed won":
            customers += 1
            if d["mrr"] is not None:
                arr += d["mrr"] * 12
    cost = None
    if tag in vendor_costs and vendor_costs[tag].get("paid") is not None:
        cost = round(float(vendor_costs[tag]["paid"]), 2)
    vendor_roi.append({
        "source": tag,
        "cost": cost,
        "sqls": sqls,
        "companies": companies,
        "cost_per_sql": round(cost / sqls, 2) if (cost is not None and sqls) else None,
        "s1s": s1s,
        "customers": customers,
        "arr": round(arr, 2),
        "roi": round(arr / cost, 2) if (cost and cost > 0) else None,
    })
# keep rows that have any signal; sort by ARR then cost then SQLs
vendor_roi = [r for r in vendor_roi
              if r["cost"] or r["sqls"] or r["s1s"] or r["customers"] or r["arr"]]
vendor_roi.sort(key=lambda r: (-(r["arr"] or 0), -(r["cost"] or 0), -r["sqls"]))

today = datetime.date.today()
window_start = today - datetime.timedelta(days=182)  # rolling last 6 months

out = {
    "generated_note": f"Snapshot pulled {today.isoformat()} from HubSpot (portal {PORTAL}). "
                      "Cohort = CONTACT.utm_source/meeting_source_cp IN (ziffdavis, memoryblue, landd, "
                      "pursuit, boscia group) OR meeting_medium_cp = affiliate OR utm_medium = affiliate.",
    "today": today.isoformat(),
    # Shown in the header chip so two publishes of the same snapshot are telling
    # apart at a glance (a stale tab, a second copy of the artifact, a rebuild).
    "built_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    "window_start": window_start.isoformat(),
    "target_sources": sorted(TARGET_SOURCES),
    "all_sources": sorted(all_sources),
    "funnel_order": FUNNEL_ORDER,
    "contacts": contacts_out,
    "deals": deals_out,
    "vendor_roi": vendor_roi,
    "vendor_costs_present": bool(vendor_costs),
}
json.dump(out, open(os.path.join(WORKDIR, "dashboard_data.json"), "w"), indent=None)

# ---- sanity report ----
print("today:", out["today"], "| window_start:", out["window_start"])
print("contacts:", len(contacts_out), "| deals:", len(deals_out))
print("all_sources:", out["all_sources"])
if unknown_stages:
    print("!! UNMAPPED STAGES (pipeline, stage, category) - reason them into a bucket and add to STAGE_LABELS:")
    for k, v in unknown_stages.items():
        print("   ", k, "x", v)
else:
    print("all stages mapped cleanly")
print("bucket counts:", dict(Counter(d["bucket"] for d in deals_out)))
cw = [d for d in deals_out if d["bucket"] == "Closed won" and d["mrr"] is not None]
print("closed-won MRR deals:", len(cw), "| total MRR: $%.2f" % sum(d["mrr"] for d in cw))
print("Follow-Up open deals:", sum(1 for d in deals_out if d["bucket"] == "Follow-Up Stage"))
_cl = [d for d in deals_out if d["bucket"] == "Closed Lost"]
print("Closed-Lost deals:", len(_cl), "| with peak stage:", sum(1 for d in _cl if d["peak_stage"]))
print("Closed-Lost peak breakdown:", dict(Counter(d["peak_stage"] for d in _cl)))
print("contacts with company:", sum(1 for c in contacts_out if c.get("company")))
print("vendor_costs present:", bool(vendor_costs), "| ROI rows:", len(vendor_roi))
for r in vendor_roi:
    print(f"   {r['source']:<14} cost={r['cost']} sqls={r['sqls']} companies={r['companies']} "
          f"cost/sql={r['cost_per_sql']} s1s={r['s1s']} customers={r['customers']} arr={r['arr']} roi={r['roi']}")
print("meeting_completed backfilled from deal stage/meeting_booked (dated):", backfilled)
print("meeting confirmed via deal stage but no safe date to plot (undated):", undated)
_t4 = [d for d in deals_out if d["bucket"] != "Promoted to Deal"]
print("tile-4 records with a meeting date:", sum(1 for d in _t4 if d["meeting_date"]), "of", len(_t4))
_wide = sorted(((len(v), k) for k, v in contact_deal_links.items() if len(v) > 10), reverse=True)
if _wide:
    print("contacts linked to >10 deals (likely vendor/internal staff; the date guard keeps them from dating unrelated deals):",
          ", ".join(f"{k} x{n}" for n, k in _wide))
if flagged_existing_customer_deals:
    print(f"!! {len(flagged_existing_customer_deals)} EXISTING-CUSTOMER PIPELINE DEAL(S) EXCLUDED "
          "from the dashboard (Account Expansion / Upsell Pipeline) - verify by hand, never add "
          "these to the report:")
    for fd in flagged_existing_customer_deals:
        print(f"    {fd['name']} [{fd['pipeline']}] sources={fd['sources']} {fd['url']}")
