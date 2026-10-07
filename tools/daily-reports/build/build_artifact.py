#!/usr/bin/env python3
"""
Build the Riverside PLG daily-report artifact HTML from a small JSON of query
results. All date-dependent math (run-rates, targets, projections, ROI, Net MRR
target ratio) is computed here so the daily refresh only has to supply raw
Snowflake query outputs.

Usage:
  python3 build_artifact.py --plan 2026-06-29
      -> prints the exact query windows, run-rates, and targets for that anchor
         date (run this BEFORE querying so the windows match the builder).

  python3 build_artifact.py            # reads ./report_values.json
  python3 build_artifact.py values.json out.html
      -> writes the artifact HTML.

report_values.json schema (produced by the daily refresh from query results):
{
  "anchor_date": "2026-06-29",
  "notion_url": "https://app.notion.com/p/....",
  "plg_channel_rows": [
     ["direct",1730,200,2578,48374,4651,62777,38132,4286,67216], ...
     # [channel, yest_signups, yest_trials, yest_fmrr,
     #  mtd_signups, mtd_trials, mtd_fmrr, prevmonth_signups, prevmonth_trials, prevmonth_fmrr]
     # Legacy per-channel row; still feeds the header pulse + Key Insights.
  ],
  "plg_channel_detail": [
     ["direct", 3515,480,235,7120,  5877,365,245,6935,  2128,317,160,4906,  2213,339,162,4900,  480,7120, 11493,188210,  1109,154,89,2685, 1124,173,84,2556], ...
     # 45 fields feeding the redesigned channel table (Signups / Trials / Subscriptions /
     # First MRR each with a MoM / WoW / Daily / 7d / 14d toggle, plus group-level Q3 attainment):
     #  [channel,
     #   m_su,m_tr,m_sub,m_fmrr,       # current month MTD  (Aug 1..anchor)
     #   pm_su,pm_tr,pm_sub,pm_fmrr,   # prior month same window (Jul 1..same day)   -> MoM
     #   w_su,w_tr,w_sub,w_fmrr,       # current week (Mon..anchor)
     #   pw_su,pw_tr,pw_sub,pw_fmrr,   # prior week same window                       -> WoW
     #   q_tr,q_fmrr,                  # quarter-to-date trials & first MRR (run-rate numerator)
     #   pq_tr,pq_fmrr,                # prior full quarter trials & first MRR (group target share)
     #   d_su,d_tr,d_sub,d_fmrr,       # anchor day
     #   pd_su,pd_tr,pd_sub,pd_fmrr,   # same weekday last week (anchor-7)            -> Daily
     #   r7_su,r7_tr,r7_sub,r7_fmrr,   # last 7 days (anchor-6..anchor)
     #   pr7_su,pr7_tr,pr7_sub,pr7_fmrr,   # the 7 days before (anchor-13..anchor-7)  -> 7d
     #   r14_su,r14_tr,r14_sub,r14_fmrr,   # last 14 days (anchor-13..anchor)
     #   pr14_su,pr14_tr,pr14_sub,pr14_fmrr] # the 14 days before (anchor-27..anchor-14) -> 14d
     # 45 fields since 2026-09-06 (29 before the 7d/14d views). Older 29-field rows still
     # build; the 7d/14d views then say the fields are missing instead of rendering zeros.
  ],
  "plg_totals": {"cur": {"net": 107636}, "prior": {"net": 127378}},
  "slg": {"cur": {"Agency":{"sqls":874,"pipe":181854,"won":77011}, "EU":{...}, "Enterprise":{...}},
          "prior":{"Agency":{...}, "EU":{...}, "Enterprise":{...}}},
  "spend": {"Google":1163392,"Bing":12952,"LI":28839,"FB":15511,"OpenAI":28481},
  "manual": {"growth_channels_spend":70000,"seo_spend":65000,
             "creative_partnerships_spend":120000,"slg_arr":1140000},
     # Optional invoice-board lines from spend_actuals.py: b2b_vendors_spend (2026-09-19),
     # affiliates_spend and affiliate_freelancers_spend (2026-10-04, split out of Growth
     # Channels / Creative partnerships by the board's Type column). Each renders its own line.
  "plg_intent_rows": [
     ["paid search", "podcasts", "Pro", 1530,240,18,410,  0,0,0,0,  ...], ...
     # Onboarding intent (metadata_purposes, the use-case question in signup) by channel_group and
     # plan. [channel, intent_token, plan, then the SAME 40 window fields as plg_channel_detail minus
     # its four q_/pq_ fields: m_(su,tr,sub,fmrr), pm_, w_, pw_, d_, pd_, r7_, pr7_, r14_, pr14_]
     # -> 59 fields (14 windows; r30_/pr30_ = last 30 days vs the 30 before, added 2026-09-16;
     #    r90_/pr90_ = last 90 days vs the 90 before, added 2026-10-06).
     # intent_token is the raw lower-cased answer, or 'no_answer' (null/blank) or
     # 'legacy_multi' (a comma-separated answer from the pre-Sep-2026 multi-select form). plan is
     # Pro / Grow / Webinar / Mobile Plus / Other exactly as Q4 maps product_group; it only means
     # anything on subscription rows (trials carry a plan ~14% of the time, signups ~1%), so the
     # builder sums plan away for the intent table and reads only sub/fmrr for the plan matrix.
     # The builder collapses old-form tokens into one "legacy" bucket via INTENT_TAXONOMY /
     # INTENT_LEGACY_TOKENS below, so the query stays a flat pass-through. Older rows still build:
     # no plan column -> plan "Other"; no r30_/pr30_ or r90_/pr90_ fields -> zeros, flagged on that view.
     # Optional: omit it and the Onboarding Intent card says no intent rows are in this build.
  ]
}
"""
import json, sys, os, calendar
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
TARGETS_XLS = os.path.join(HERE, "..", "targets_2026.xlsx")

MONTH_NAME = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",
              7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
SHORT_MONTH = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
WEEKDAY = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Onboarding-intent taxonomy. The single-answer use-case question shipped in signup the week of
# 2026-08-31 (answered share of signups: 0.9% the week before, 20.7% that week, ~70% since), and its
# ten raw tokens are exactly what analytics.bi.accounts_use_cases normalises (Title Case, 1:1).
# Anything else is an answer from the retired multi-select form and collapses into one "legacy"
# bucket - old accounts still surface it on their trial / subscription rows. A token that is in
# neither set keeps its own row under its raw name and is listed in the card's note, so a new
# option added to the question shows up instead of being silently swallowed by "legacy".
INTENT_TAXONOMY = {
    "podcasts": "Podcasts", "videoclips": "Video clips", "transcription": "Transcription",
    "live streaming": "Live streaming", "webinars": "Webinars", "marketingvideos": "Marketing videos",
    "internalvideos": "Internal videos", "coursevideos": "Course videos",
    "marketingcontent": "Marketing content", "internal communication": "Internal communication",
}
INTENT_LEGACY_TOKENS = {
    "legacy_multi", "video interviews", "screen recording", "voice overs", "voice over",
    "talking head video", "executive interviews", "panel discussions", "live streams",
    "video marketing", "keynote speakers", "virtual events", "virtual conferences",
    "customer testimonials",
}
INTENT_LABELS = {**INTENT_TAXONOMY, "legacy": "Legacy answer (old multi-select form)",
                 "no_answer": "No answer / not asked"}
INTENT_NFIELDS = 56   # the window fields after [channel, intent, plan]: 14 windows x (su, tr, sub, fmrr)
INTENT_NWIN = 14      # m, pm, w, pw, d, pd, r7, pr7, r14, pr14, r30, pr30, r90, pr90


PLANS = ["Pro", "Grow", "Webinar", "Mobile Plus", "Other"]   # column order of the use case x plan matrix

def intent_bucket(tok):
    """Raw metadata_purposes token -> (bucket, kind) with kind in taxonomy | no_answer | legacy | unknown."""
    tok = (tok or "").strip().lower()
    if tok in INTENT_TAXONOMY: return tok, "taxonomy"
    if tok == "no_answer": return tok, "no_answer"
    if tok in INTENT_LEGACY_TOKENS or "," in tok: return "legacy", "legacy"
    return tok, "unknown"


def collapse_rows(rows, nfields, key_fn, first_field):
    """Sum rows whose key_fn(row) agree. Rows are [key parts..., nfields numbers] with the numbers
    starting at index first_field; missing / None numbers count as 0."""
    out = {}
    for r in rows:
        key = key_fn(r)
        acc = out.setdefault(key, list(key) + [0] * nfields)
        for j in range(nfields):
            i = first_field + j
            acc[len(key) + j] += (r[i] if i < len(r) and r[i] is not None else 0)
    return list(out.values())


def collapse_intent(rows):
    """plg_intent_rows -> (plan_rows, intent_rows, legacy_tokens_seen, unknown_tokens_seen).
    plan_rows: [channel, bucket, plan, sub, fmrr x 10 windows] (23 fields) for the use case x plan
    matrix. intent_rows: [channel, bucket, 40 window fields] with plan summed away, for the intent
    table. A 42-field row from the pre-plan layout is read as plan "Other"."""
    legacy_seen, unknown = set(), set()
    # Older layouts still build: a row without the plan column (42, 50 or 58 fields) is read as plan "Other",
    # and a row without the 30d / 90d windows (43 or 51 fields) is zero-padded, which the card flags on that view.
    norm = [r[:2] + ["Other"] + r[2:] if len(r) in (42, 50, 2 + INTENT_NFIELDS) else r for r in rows]
    def key(r):
        b, kind = intent_bucket(r[1])
        if kind == "legacy": legacy_seen.add((r[1] or "").strip().lower())
        elif kind == "unknown": unknown.add(b)
        return (r[0], b, r[2] if r[2] in PLANS else "Other")
    full = collapse_rows(norm, INTENT_NFIELDS, key, 3)          # [ch, bucket, plan, 40]
    intent_rows = collapse_rows(full, INTENT_NFIELDS, lambda r: (r[0], r[1]), 3)
    plan_rows = [r[:3] + [x for w in range(INTENT_NWIN) for x in (r[3 + w * 4 + 2], r[3 + w * 4 + 3])] for r in full]
    return plan_rows, intent_rows, sorted(legacy_seen), sorted(unknown)


def day_label(d):
    """'Sat Sep 5' - weekday included because Daily compares same weekday last week."""
    return f"{WEEKDAY[d.weekday()]} {SHORT_MONTH[d.month]} {d.day}"


def d(anchor, days):
    """ISO date `days` from the anchor (negative = earlier)."""
    return (anchor + timedelta(days=days)).isoformat()


def range_label(a, b):
    """'Sep 1-5' within a month, 'Aug 31-Sep 5' across months, 'Sep 5' for a single day."""
    if a == b:
        return f"{SHORT_MONTH[a.month]} {a.day}"
    if a.month == b.month:
        return f"{SHORT_MONTH[a.month]} {a.day}-{b.day}"
    return f"{SHORT_MONTH[a.month]} {a.day}-{SHORT_MONTH[b.month]} {b.day}"

# Canonical per-channel-group quarter targets for the channel table, copied from the
# "Growth Marketing - Q3 2026 Plan" artifact (claude.ai artifact 34ed9a9f-c6c4-4da1-8270-
# d542fd13ba1e, "Channel-group targets · Q3" table): the $900K quarter first-MRR split by
# channel group, +4% MoM on a July rollover base. share = % of the quarter's first MRR as
# printed in the plan. Keys must match `channel_group` values (or the GROUPS names in the
# template: Paid / Partnerships / Affiliates).
# NEVER invent or derive channel targets (Nir, 2026-08-05): if a quarter has no entry
# here, the table renders "-" for share and attainment until the plan lands.
# NOTE: the plan's Q3 trials total (54,122) differs slightly from the workbook-derived
# company Q3 trials target (54,780 = 16,600 x1.10 x3); this table follows the plan.
CHANNEL_Q_TARGETS = {
    "2026-Q3": {
        "total": {"fmrr": 900000, "tr": 54122, "share": 100.0},
        "rows": {
            "direct":                   {"fmrr": 192900, "tr": 11483, "share": 21.4},
            "unknown":                  {"fmrr": 157300, "tr": 11390, "share": 17.5},
            "paid search brand":        {"fmrr": 123400, "tr": 6441,  "share": 13.7},
            "Paid":                     {"fmrr": 120500, "tr": 6838,  "share": 13.4},
            "organic search brand":     {"fmrr": 93800,  "tr": 5223,  "share": 10.4},
            "organic search non brand": {"fmrr": 55500,  "tr": 3823,  "share": 6.2},
            "guest":                    {"fmrr": 52400,  "tr": 2370,  "share": 5.8},
            "referral":                 {"fmrr": 32300,  "tr": 1930,  "share": 3.6},
            "integration partner":      {"fmrr": 22000,  "tr": 1382,  "share": 2.4},
            "organic llm":              {"fmrr": 16100,  "tr": 616,   "share": 1.8},
            "Affiliates":               {"fmrr": 12900,  "tr": 774,   "share": 1.4},
            "Partnerships":             {"fmrr": 8700,   "tr": 1044,  "share": 1.0},
            "organic social":           {"fmrr": 6600,   "tr": 545,   "share": 0.7},
            "other":                    {"fmrr": 3700,   "tr": 203,   "share": 0.4},
            "email marketing":          {"fmrr": 1900,   "tr": 60,    "share": 0.2},
        },
    },
}


def busday_count(start, end_exclusive):
    n, d = 0, start
    while d < end_exclusive:
        if d.weekday() < 5:
            n += 1
        d += timedelta(days=1)
    return n


def fiscal_q(d):
    """Return (qnum, q_start, q_end). Fiscal: Q1 Feb-Apr, Q2 May-Jul, Q3 Aug-Oct, Q4 Nov-Jan."""
    m = d.month
    if m in (2, 3, 4):   return 1, date(d.year, 2, 1), date(d.year, 4, 30)
    if m in (5, 6, 7):   return 2, date(d.year, 5, 1), date(d.year, 7, 31)
    if m in (8, 9, 10):  return 3, date(d.year, 8, 1), date(d.year, 10, 31)
    if m in (11, 12):    return 4, date(d.year, 11, 1), date(d.year + 1, 1, 31)
    return 4, date(d.year - 1, 11, 1), date(d.year, 1, 31)  # January


def prev_month_pop_date(yd):
    dim_y = calendar.monthrange(yd.year, yd.month)[1]
    is_last = yd.day == dim_y
    pm = yd.month - 1 if yd.month > 1 else 12
    py = yd.year if yd.month > 1 else yd.year - 1
    pdim = calendar.monthrange(py, pm)[1]
    return date(py, pm, pdim) if is_last else date(py, pm, min(yd.day, pdim))


def read_targets(anchor):
    """Replicates run_full_report.py target logic."""
    import openpyxl
    wb = openpyxl.load_workbook(TARGETS_XLS, data_only=True)
    plg = wb["PLG targets"]
    month_cols = {2:'C',3:'D',4:'E',5:'F',6:'G',7:'H',8:'I',9:'J',10:'K',11:'L',12:'M',1:'N'}
    col = month_cols[anchor.month]
    signups_raw = plg[f'{col}4'].value
    trials_raw = plg[f'{col}6'].value
    mrr_raw = plg[f'{col}11'].value
    signups_tgt = round(signups_raw)                   # row 4 is all-device signups; no factor
    trials_tgt = round(trials_raw * 1.10)              # +10% mobile-app factor
    fmrr_tgt = round(mrr_raw)
    # Net MRR has NO target (confirmed by Nir 2026-08-04). It used to be derived as
    # fmrr_tgt x (Feb net 208094 / Feb new-MRR 376476) = x0.5528, i.e. February's
    # net-to-new ratio projected onto every month - a number nobody planned. Net MRR
    # is now reported as actual + MoM only; the report renders "-" for target,
    # projection, and attainment when this is None.
    net_tgt = None

    slg = wb["SLG targets"]
    qcol = {1:'B', 2:'C', 3:'D', 4:'E'}[fiscal_q(anchor)[0]]
    def dol(v):
        if v is None: return 0
        if isinstance(v, (int, float)): return float(v)
        return float(str(v).replace('$', '').replace(',', ''))
    slg_tgt = {
        "SQLs - Agency": round((slg[f'{qcol}17'].value or 0) + (slg[f'{qcol}18'].value or 0)),
        "SQLs - EU":     round((slg[f'{qcol}19'].value or 0) + (slg[f'{qcol}20'].value or 0) + (slg[f'{qcol}21'].value or 0)),
        "SQLs - Ent":    round(slg[f'{qcol}22'].value or 0),
        "Pipe - Agency": round(dol(slg[f'{qcol}38'].value) + dol(slg[f'{qcol}39'].value)),
        "Pipe - EU":     round(dol(slg[f'{qcol}40'].value) + dol(slg[f'{qcol}41'].value) + dol(slg[f'{qcol}42'].value)),
        "Pipe - Ent":    round(dol(slg[f'{qcol}43'].value)),
        "B2B MRR":       round(dol(slg[f'{qcol}65'].value)),
    }
    wb.close()
    return signups_tgt, trials_tgt, fmrr_tgt, net_tgt, slg_tgt


def read_quarter_targets(anchor):
    """Company-wide quarter targets for the anchor's fiscal quarter - the sum of the
    three constituent months, computed with the same per-month conventions as
    read_targets (trials x1.10 mobile factor; First-MRR target = New MRR row 11).
    Used by the channel report's per-channel Q3 attainment. Returns (trials, fmrr)."""
    import openpyxl
    wb = openpyxl.load_workbook(TARGETS_XLS, data_only=True)
    plg = wb["PLG targets"]
    month_cols = {2:'C',3:'D',4:'E',5:'F',6:'G',7:'H',8:'I',9:'J',10:'K',11:'L',12:'M',1:'N'}
    qmonths = {1:[2,3,4], 2:[5,6,7], 3:[8,9,10], 4:[11,12,1]}[fiscal_q(anchor)[0]]
    q_trials = sum(round((plg[f'{month_cols[m]}6'].value or 0) * 1.10) for m in qmonths)
    q_fmrr = sum(round(plg[f'{month_cols[m]}11'].value or 0) for m in qmonths)
    wb.close()
    return q_trials, q_fmrr


def compute_params(anchor):
    dim = calendar.monthrange(anchor.year, anchor.month)[1]
    mrr = anchor.day / dim
    qnum, qs, qe = fiscal_q(anchor)
    nw_elapsed = max(1, busday_count(qs, anchor + timedelta(days=1)))
    nw_total = busday_count(qs, qe + timedelta(days=1))
    qrr = nw_elapsed / nw_total

    if qnum == 1:   prev_qs, cur_lbl, prev_lbl = date(qs.year-1,11,1), f"{qs.year}-Q1", f"{qs.year-1}-Q4"
    elif qnum == 2: prev_qs, cur_lbl, prev_lbl = date(qs.year,2,1),   f"{qs.year}-Q2", f"{qs.year}-Q1"
    elif qnum == 3: prev_qs, cur_lbl, prev_lbl = date(qs.year,5,1),   f"{qs.year}-Q3", f"{qs.year}-Q2"
    else:           prev_qs, cur_lbl, prev_lbl = date(qs.year,8,1),   f"{qs.year}-Q4", f"{qs.year}-Q3"
    # prev-quarter equivalent fiscal day (business-day aligned)
    equiv, bc = prev_qs, 0
    while bc < nw_elapsed:
        if equiv.weekday() < 5: bc += 1
        if bc < nw_elapsed: equiv += timedelta(days=1)

    month_start = date(anchor.year, anchor.month, 1)
    pop_end = prev_month_pop_date(anchor)
    pop_start = date(pop_end.year, pop_end.month, 1)
    # Week windows are period-to-date: Monday of the anchor's week through the anchor, vs the
    # same elapsed slice of the prior week (Nir, 2026-08-18 - never full week vs full week).
    # Daily is the anchor vs the same weekday last week (anchor-7 == prev_week_window[1]).
    wk_mon = anchor - timedelta(days=anchor.weekday())
    prev_wk_mon = wk_mon - timedelta(days=7)
    signups_tgt, trials_tgt, fmrr_tgt, net_tgt, slg_tgt = read_targets(anchor)
    q_trials_tgt, q_fmrr_tgt = read_quarter_targets(anchor)
    return {
        "anchor": anchor.isoformat(), "mrr": mrr, "qrr": qrr,
        "month_name": MONTH_NAME[anchor.month], "short": SHORT_MONTH[anchor.month],
        "cur_month_window": [month_start.isoformat(), anchor.isoformat()],
        "prev_month_window": [pop_start.isoformat(), pop_end.isoformat()],
        "cur_week_window":  [wk_mon.isoformat(), anchor.isoformat()],
        "prev_week_window": [prev_wk_mon.isoformat(), (anchor - timedelta(days=7)).isoformat()],
        # Rolling windows (added 2026-09-06): last 7 / 14 complete days ending at the anchor vs the
        # 7 / 14 days immediately before. Unlike WoW these ignore the calendar week, so a Saturday
        # anchor compares a full Sun-Sat span rather than six elapsed days.
        "last7_window":  [d(anchor, -6), anchor.isoformat()],
        "prev7_window":  [d(anchor, -13), d(anchor, -7)],
        "last14_window": [d(anchor, -13), anchor.isoformat()],
        "prev14_window": [d(anchor, -27), d(anchor, -14)],
        # 30d (added 2026-09-16, intent card only): the last 30 complete days vs the 30 before - the same
        # trailing-30 definition the ROI report uses for its rollover window.
        "last30_window": [d(anchor, -29), anchor.isoformat()],
        "prev30_window": [d(anchor, -59), d(anchor, -30)],
        # 90d (added 2026-10-06, intent card only, Nir's ask): the last 90 complete days vs the 90 before.
        "last90_window": [d(anchor, -89), anchor.isoformat()],
        "prev90_window": [d(anchor, -179), d(anchor, -90)],
        # Lower bound for the intent query (Q8): the earlier of the prior month's first day and the start
        # of the prior-90 window. Since 2026-10-06 that is always the prior-90 start (anchor-179).
        "intent_range_start": min(pop_start.isoformat(), d(anchor, -179)),
        # Human labels for the channel table's view caption, so each toggle says which dates
        # it is comparing ("Sep 1-5 vs Aug 1-5") instead of just "this week".
        "view_labels": {
            "mom": [range_label(month_start, anchor), range_label(pop_start, pop_end)],
            "wow": [range_label(wk_mon, anchor), range_label(prev_wk_mon, anchor - timedelta(days=7))],
            "day": [day_label(anchor), day_label(anchor - timedelta(days=7))],
            "r7":  [range_label(anchor - timedelta(days=6), anchor), range_label(anchor - timedelta(days=13), anchor - timedelta(days=7))],
            "r14": [range_label(anchor - timedelta(days=13), anchor), range_label(anchor - timedelta(days=27), anchor - timedelta(days=14))],
            "r30": [range_label(anchor - timedelta(days=29), anchor), range_label(anchor - timedelta(days=59), anchor - timedelta(days=30))],
            "r90": [range_label(anchor - timedelta(days=89), anchor), range_label(anchor - timedelta(days=179), anchor - timedelta(days=90))],
        },
        "cur_q_label": cur_lbl, "prev_q_label": prev_lbl,
        "cur_q_window": [qs.isoformat(), anchor.isoformat()],
        "prev_q_window": [prev_qs.isoformat(), equiv.isoformat()],
        # Full prior quarter (all three months) - used for the channel report's
        # per-channel Q3 target, which splits the company target by each channel's
        # share of the last complete quarter.
        "prev_q_full_window": [prev_qs.isoformat(), (qs - timedelta(days=1)).isoformat()],
        "signups_tgt": signups_tgt, "trials_tgt": trials_tgt, "fmrr_tgt": fmrr_tgt,
        "net_tgt": None if net_tgt is None else round(net_tgt),
        "q_trials_tgt": q_trials_tgt, "q_fmrr_tgt": q_fmrr_tgt,
        "cur_q_short": {1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"}[qnum],
        "slg_tgt": slg_tgt,
    }


ROI_BUDGETS_DEFAULT = {"SEO": 70000, "Creative partnerships": 150000, "Growth Channels": 80000}


def roi_budgets_monthly():
    """budgets_monthly from roi_report_values.json (the ROI report's fixed budgets), else the default."""
    try:
        with open(os.path.join(HERE, "roi_report_values.json")) as f:
            return json.load(f).get("budgets_monthly") or ROI_BUDGETS_DEFAULT
    except (OSError, ValueError):
        return ROI_BUDGETS_DEFAULT


def build(values):
    anchor = date.fromisoformat(values["anchor_date"])
    p = compute_params(anchor)
    seg = ["Agency", "EU", "Enterprise"]
    slg_rows = [
        ("SQLs - Agency", p["slg_tgt"]["SQLs - Agency"], values["slg"]["cur"]["Agency"]["sqls"], values["slg"]["prior"]["Agency"]["sqls"], False),
        ("SQLs - EU",     p["slg_tgt"]["SQLs - EU"],     values["slg"]["cur"]["EU"]["sqls"],     values["slg"]["prior"]["EU"]["sqls"],     False),
        ("SQLs - Ent",    p["slg_tgt"]["SQLs - Ent"],    values["slg"]["cur"]["Enterprise"]["sqls"], values["slg"]["prior"]["Enterprise"]["sqls"], False),
        ("Pipe - Agency", p["slg_tgt"]["Pipe - Agency"], values["slg"]["cur"]["Agency"]["pipe"], values["slg"]["prior"]["Agency"]["pipe"], True),
        ("Pipe - EU",     p["slg_tgt"]["Pipe - EU"],     values["slg"]["cur"]["EU"]["pipe"],     values["slg"]["prior"]["EU"]["pipe"],     True),
        ("Pipe - Ent",    p["slg_tgt"]["Pipe - Ent"],    values["slg"]["cur"]["Enterprise"]["pipe"], values["slg"]["prior"]["Enterprise"]["pipe"], True),
    ]
    won_cur = sum(values["slg"]["cur"][s]["won"] for s in seg)
    won_prior = sum(values["slg"]["prior"][s]["won"] for s in seg)
    slg_rows.append(("B2B MRR", p["slg_tgt"]["B2B MRR"], won_cur, won_prior, True))

    rows = values["plg_channel_rows"]
    jun_su = sum(r[4] for r in rows); jun_tr = sum(r[5] for r in rows); jun_fmrr = sum(r[6] for r in rows)
    may_su = sum(r[7] for r in rows); may_tr = sum(r[8] for r in rows); may_fmrr = sum(r[9] for r in rows)

    plan_rows, intent_rows, intent_legacy, intent_unknown = collapse_intent(values.get("plg_intent_rows", []))
    # Row length with the plan column counted (42 / 50 / 58 are the no-plan layouts): 51+ carries 30d, 59 carries 90d.
    _ilen = [len(r) + (1 if len(r) in (42, 50, 58) else 0) for r in values.get("plg_intent_rows", [])]
    intent_missing = [v for v, n in (("r30", 51), ("r90", 59)) if _ilen and min(_ilen) < n]

    data = {
        "ANCHOR": f"{p['month_name'].split()[0]} {anchor.day}, {anchor.year}",
        "MONTH_LABEL": p["month_name"] + f" {anchor.year}",
        "SHORT_THROUGH": f"{p['short']} {anchor.day}",
        "PLG_MRR": p["mrr"], "SLG_QRR": p["qrr"],
        "PLG": {
            "signups": {"cur": jun_su, "prior": may_su, "tgt": p["signups_tgt"]},
            "trials":  {"cur": jun_tr, "prior": may_tr, "tgt": p["trials_tgt"]},
            "fmrr":    {"cur": jun_fmrr, "prior": may_fmrr, "tgt": p["fmrr_tgt"]},
            "net":     {"cur": values["plg_totals"]["cur"]["net"], "prior": values["plg_totals"]["prior"]["net"], "tgt": p["net_tgt"]},
        },
        "SLG": [{"name": n, "tgt": t, "cur": c, "prior": pr, "money": m} for (n, t, c, pr, m) in slg_rows],
        "SLG_Q_LABEL": p["cur_q_label"].replace("-", " ").replace("Q", "Q"),
        "SPEND": spend_lines(values),
        # Projected full-month spend, the same figure the ROI & Growth report prints under its MTD
        # spend: full monthly budgets + PPC MTD / month run-rate. Budgets are read from that
        # report's value file so the two reports cannot drift apart.
        "PROJ_MONTH_SPEND": sum(roi_budgets_monthly().values()) + sum(values["spend"].values()) / p["mrr"],
        "NEW_FIRST_MRR_MTD": jun_fmrr,
        "SLG_ARR": values["manual"]["slg_arr"],
        # Per-line provenance for the four manual inputs, so the report can say on its face
        # whether a spend line is a real actual or a pro-rated budget. Optional: omit it and the
        # caveat banner simply does not render (older value files keep working unchanged).
        # Recognised values: "invoice_actual" (from the Invoices and Payments board - lags, because
        # invoices arrive after the spend), "budget_prorated" (monthly budget x month run-rate),
        # "actual" (a real MTD figure from a source that does not lag, e.g. card spend).
        # Mixing lagging actuals with pro-rated budgets understates total spend and inflates ROI,
        # which is exactly what the banner exists to say out loud.
        "MANUAL_BASIS": values.get("manual_basis", {}),
        "RAW": [[r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]] for r in rows],
        # Per-channel detail across all windows, for the redesigned channel table.
        # Row order matches the plg_channel_detail schema (21 fields) documented at the
        # top of this file. Falls back to [] on older value files (table renders empty).
        "CHAN": values.get("plg_channel_detail", []),
        "QRR": p["qrr"],
        "Q_LABEL": p["cur_q_short"],
        "VIEW_LABELS": p["view_labels"],
        # Canonical plan targets for the anchor's quarter, or None -> table shows "-"
        # for share/attainment (never derive a substitute).
        "CH_TGT": CHANNEL_Q_TARGETS.get(p["cur_q_label"]),
        # Onboarding intent by channel (Q8), collapsed to the taxonomy above. Optional.
        "INTENT": intent_rows, "INTENT_LABELS": INTENT_LABELS,
        "INTENT_LEGACY_SEEN": intent_legacy, "INTENT_UNKNOWN": intent_unknown,
        "INTENT_PLAN": plan_rows, "PLANS": PLANS,
        # Views whose window fields the raw Q8 rows don't carry (older query layout): the card says so instead of showing zeros.
        "INTENT_MISSING": intent_missing,
        "NOTION_URL": values.get("notion_url", ""),
    }
    return TEMPLATE.replace("__DATA_JSON__", json.dumps(data))


# Invoice-board lines split out by the board's Type column (spend_actuals.py rule 5), in render
# order. Optional so older value files still build; an absent key contributes nothing rather than
# rendering $0 as a fact.
SPLIT_LINES = [("affiliates_spend", "Affiliates"),
               ("affiliate_freelancers_spend", "Affiliate freelancers & platforms"),
               ("b2b_vendors_spend", "B2B vendors")]


def spend_lines(values):
    """PPC by platform, then the manual / invoice-board lines. Once the affiliate split is present,
    the Growth Channels line holds only what is left after it (review platforms and the like), so it
    is labelled that way instead of reading as the whole of Growth Channels."""
    m = values["manual"]
    split = any(m.get(k) is not None for k in ("affiliates_spend", "affiliate_freelancers_spend"))
    out = {**values["spend"],
           ("Other Growth Channels" if split else "Growth Channels"): m["growth_channels_spend"],
           "SEO": m["seo_spend"],
           "Creative partnerships": m["creative_partnerships_spend"]}
    for key, label in SPLIT_LINES:
        if m.get(key) is not None:
            out[label] = m[key]
    return out


TEMPLATE = r"""<title>Riverside Daily Report</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  :root{
    --bg:#0F0F14; --card:#1C1C24; --line:#2A2A35; --line-soft:rgba(42,42,53,.5);
    --ink:#FFFFFF; --muted:#E6E6EB; --dim:#9A9AA6; --faint:#5B5B66;
    --accent:#7C5CFF; --accent-soft:rgba(124,92,255,.08);
    --great:#00C875; --ok:#579BFC; --attention:#FDAB3D; --critical:#FF3B30;
  }
  body{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
    background:var(--bg); color:var(--ink); min-height:100vh; line-height:1.45; -webkit-font-smoothing:antialiased;}
  .container{max-width:1160px;margin:0 auto;padding:32px 24px 48px}
  .header{display:flex;justify-content:space-between;align-items:flex-start;gap:24px;
    border-bottom:1px solid var(--line);padding-bottom:20px;margin-bottom:26px;flex-wrap:wrap}
  .header h1{font-size:22px;font-weight:700;letter-spacing:-.02em}
  .header h1 span{color:var(--accent)}
  .header .date{font-size:13px;color:var(--muted);margin-top:5px}
  .header .meta{text-align:right;font-size:12px;color:var(--dim);line-height:1.7}
  .header .meta b{color:var(--muted);font-weight:600}
  .section-title{font-size:12px;font-weight:600;color:var(--accent);margin-bottom:12px;text-transform:uppercase;letter-spacing:.06em}
  .card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px;margin-bottom:22px}
  .tbl-wrap{overflow-x:auto}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th{background:var(--bg);color:var(--muted);font-weight:600;font-size:11px;text-transform:uppercase;
    letter-spacing:.04em;padding:9px 10px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap}
  th:first-child{text-align:left}
  td{padding:8px 10px;text-align:right;border-bottom:1px solid var(--line-soft);font-variant-numeric:tabular-nums}
  td:first-child{text-align:left;font-weight:500;color:var(--muted)}
  tbody tr:hover{background:var(--accent-soft)}
  .group-label td{background:var(--bg);font-weight:700;font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);padding:7px 10px}
  .total td{font-weight:700;border-top:2px solid var(--accent);background:var(--accent-soft);color:var(--ink)}
  tr.total.lead td{border-top:none;border-bottom:2px solid var(--accent)}
  .total td:first-child{color:var(--ink)}
  .muted-note{font-size:11px;color:var(--faint);margin-top:10px}
  /* Spend-basis caveat. Renders only when a spend line is an invoices-filed actual rather than a
     pro-rated budget: those lag, so MTD spend is understated and ROI is not comparable. */
  .spend-caveat{display:none;background:rgba(253,171,61,.10);border:1px solid var(--attention);
    border-left:3px solid var(--attention);border-radius:8px;padding:11px 14px;margin-bottom:14px;
    font-size:12.5px;color:var(--muted);line-height:1.6}
  .spend-caveat.on{display:block}
  .spend-caveat b{color:var(--attention)}
  .pos{color:var(--great)} .neg{color:var(--critical)} .flat{color:var(--dim)}
  .pill{display:inline-block;padding:2px 9px;border-radius:9999px;font-size:11px;font-weight:600;color:#0b0b10;white-space:nowrap}
  .pill.great{background:var(--great)} .pill.ok{background:var(--ok);color:#fff}
  .pill.attention{background:var(--attention)} .pill.critical{background:var(--critical);color:#fff}
  .pill.lowvol{background:transparent;color:var(--faint);border:1px solid var(--line)}
  .na{color:var(--faint)}
  #tbl th{cursor:pointer;user-select:none}
  #tbl th:hover{color:var(--accent)}
  #tbl th .arr{color:var(--accent);font-size:9px;margin-left:3px}
  #tbl td .pp{font-size:11px;font-weight:600;margin-left:6px;white-space:nowrap}
  #tbl td .mv{font-variant-numeric:tabular-nums}
  #tbl td .share{color:#b3a1ff;font-size:11.5px;font-weight:600;margin-left:6px;white-space:nowrap}
  #tbl td .share .slash{color:var(--faint);margin:0 3px;font-weight:400}
  #tbl td .share .act.up{color:var(--great)} #tbl td .share .act.down{color:var(--critical)}
  #tbl td .share .act.dim{color:var(--dim)} #tbl td .share .act.na{color:var(--faint)}
  #tbl .caret{display:inline-block;width:15px;color:var(--accent);font-size:11px;font-weight:700}
  #tbl .exp-hint{display:inline-block;margin-left:9px;font-size:10.5px;font-weight:600;color:var(--accent);
    background:var(--accent-soft);border:1px solid rgba(124,92,255,.38);border-radius:999px;padding:1px 9px;
    letter-spacing:.02em;vertical-align:1px}
  #tbl tr.grp td{cursor:pointer}
  #tbl tr.grp:hover td{background:var(--accent-soft)}
  #tbl tr.grp:hover .exp-hint{background:var(--accent);color:#fff;border-color:var(--accent)}
  #tbl tr.grp td:first-child{font-weight:700;color:var(--ink)}
  #tbl tr.sub td{border-bottom-color:rgba(42,42,53,.3)}
  #tbl tr.sub td:first-child{padding-left:34px;font-weight:400;color:var(--dim)}
  /* the two Q3-attainment columns read as one fixed block, tinted + separated */
  #tbl th.attcol,#tbl td.attcol{background:rgba(124,92,255,.06)}
  #tbl th.attcol.sep,#tbl td.attcol.sep{border-left:1px solid var(--line)}
  #tbl th .fixed-tag{display:block;font-size:9px;font-weight:600;color:var(--accent);letter-spacing:.03em;margin-top:2px;text-transform:none}
  /* Onboarding-intent card: three breakdown tables sharing one channel filter / view / share base.
     A metric cell is two lines - count with its period change, then share with its change in pp. */
  .bd th{cursor:pointer;user-select:none} .bd th:hover{color:var(--accent)}
  .bd th .arr{color:var(--accent);font-size:9px;margin-left:3px}
  .bd td .mv{font-variant-numeric:tabular-nums}
  .bd td .l1{white-space:nowrap} .bd td .l2{font-size:11px;margin-top:1px;white-space:nowrap}
  /* two-line cells carry the prior value, so these tables scroll inside the card rather than crush the columns */
  #itbl{min-width:1320px} #ptbl{min-width:980px}
  .bd td .sh{color:#b3a1ff;font-weight:600}
  .bd td .pp{font-size:11px;font-weight:600;margin-left:5px;white-space:nowrap}
  .bd td .dl{font-size:11.5px;font-weight:600;margin-left:8px;white-space:nowrap}
  .bd td .dl.pos{color:var(--great)} .bd td .dl.neg{color:var(--critical)} .bd td .dl.flat{color:var(--dim)} .bd td .dl.na{color:var(--faint)}
  .bd td .was{font-size:10.5px;color:var(--faint);margin-left:6px;white-space:nowrap}
  .bd td .l2 .sh{margin-right:0}
  .thinpill{display:inline-block;font-size:9.5px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--attention);
    border:1px solid var(--attention);border-radius:999px;padding:0 7px;margin-left:8px;vertical-align:1px}
  .bd tr.cov td{background:var(--bg);color:var(--dim);font-size:12px}
  .bd tr.cov td:first-child{color:var(--muted);font-weight:600}
  .bd tr.cov td .mv{color:var(--muted);font-weight:600}
  .bd tr.cov td .thin{color:var(--attention);font-size:10px;font-weight:700;margin-left:6px;letter-spacing:.03em}
  .bd tr.dimrow td{color:var(--faint)} .bd tr.dimrow td:first-child{color:var(--dim);font-weight:400}
  .bd tr.dimrow td .sh{color:var(--faint)}
  .bd th.conv,.bd td.conv{background:rgba(124,92,255,.06)}
  .bd th.sep,.bd td.sep{border-left:1px solid var(--line)}
  .bd th .conv-tag{display:block;font-size:9px;font-weight:600;color:var(--accent);letter-spacing:.03em;margin-top:2px;text-transform:none}
  .bd tfoot td .l2 .sh{color:var(--muted)}
  .subhead{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:11px;font-weight:700;
    color:var(--muted);text-transform:uppercase;letter-spacing:.05em;margin:22px 0 8px;padding-top:16px;border-top:1px solid var(--line)}
  .subhead .sub{display:block;font-weight:400;text-transform:none;letter-spacing:0;color:var(--dim);margin-top:2px}
  .toggle.sm button{padding:4px 10px;font-size:11px}
  .sel{background:var(--bg);border:1px solid var(--line);border-radius:8px;color:var(--ink);font:inherit;font-size:13px;padding:8px 32px 8px 12px;max-width:100%;
    appearance:none;-webkit-appearance:none;background-image:linear-gradient(45deg,transparent 50%,var(--dim) 50%),linear-gradient(135deg,var(--dim) 50%,transparent 50%);
    background-position:calc(100% - 17px) 55%,calc(100% - 12px) 55%;background-size:5px 5px,5px 5px;background-repeat:no-repeat;cursor:pointer}
  .sel:focus{outline:2px solid var(--accent);outline-offset:1px;border-color:transparent}
  .view-cap{font-size:11.5px;color:var(--dim);margin:-4px 0 12px;line-height:1.5}
  .view-cap b{color:var(--muted);font-weight:600}
  .view-cap .lock{color:var(--accent)}
  .view-cap .warn{color:var(--critical);font-weight:600}
  .toggle{display:inline-flex;background:var(--bg);border:1px solid var(--line);border-radius:9px;padding:3px}
  .toggle button{background:transparent;border:none;color:var(--dim);font:inherit;font-size:12px;font-weight:600;
    padding:6px 13px;border-radius:6px;cursor:pointer;letter-spacing:.02em}
  .toggle button.active{background:var(--accent);color:#fff}
  .toggle button:hover:not(.active){color:var(--ink)}
  .tbl-head{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:14px;flex-wrap:wrap}
  .tbl-head .controls{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
  .search{background:var(--bg);border:1px solid var(--line);border-radius:8px;color:var(--ink);font:inherit;font-size:13px;padding:8px 12px;width:230px;max-width:100%}
  .search::placeholder{color:var(--faint)}
  .search:focus{outline:2px solid var(--accent);outline-offset:1px;border-color:transparent}
  .snap-kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:16px}
  .snap-kpi{background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:16px 18px;border-top:3px solid var(--accent)}
  .snap-kpi .label{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--dim);font-weight:600}
  .snap-kpi .big{font-size:21px;font-weight:700;letter-spacing:-.02em;margin-top:5px;font-variant-numeric:tabular-nums}
  .snap-kpi .sub{font-size:12px;color:var(--dim);margin-top:5px}
  .snap-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
  .spend-cell{background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:10px 12px}
  .spend-cell .k{font-size:11px;color:var(--dim);text-transform:uppercase;letter-spacing:.03em}
  .spend-cell .v{font-size:15px;font-weight:600;margin-top:3px;font-variant-numeric:tabular-nums}
  .insights{display:grid;grid-template-columns:1fr 1fr;gap:12px}
  .insight{background:var(--accent-soft);border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:8px;padding:13px 15px}
  .insight h3{font-size:11px;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:.03em;margin-bottom:5px}
  .insight p{font-size:13px;color:var(--muted)}
  .insight .diag{font-size:12px;color:var(--dim);margin-top:6px}
  .footer{font-size:11px;color:var(--faint);line-height:1.7;border-top:1px solid var(--line);padding-top:18px}
  .footer a{color:var(--accent);text-decoration:none}
  .footer a:hover{text-decoration:underline}
  @media (max-width:760px){
    .snap-kpis{grid-template-columns:repeat(2,1fr)}
    .snap-grid{grid-template-columns:1fr 1fr}
    .insights{grid-template-columns:1fr}
    .header .meta{text-align:left}
    table{min-width:0} #tbl{min-width:860px} #itbl{min-width:1320px} #ptbl{min-width:980px}
  }
</style>
<div class="container">
  <header class="header">
    <div><h1><span>Riverside</span> Daily Report</h1><div class="date" id="hdr-date"></div></div>
    <div class="meta" id="hdr-meta"></div>
  </header>
  <div class="card">
    <div class="section-title">High-Level Summary</div>
    <div class="tbl-wrap"><table id="hl"><thead><tr>
      <th>Metric</th><th>Target</th><th>Current</th><th>Projected</th><th>Attainment</th><th>PoP</th>
    </tr></thead><tbody id="hl-body"></tbody></table></div>
    <div class="muted-note" id="hl-note"></div>
  </div>
  <div class="card">
    <div class="tbl-head">
      <div class="section-title" style="margin:0" id="chan-title">PLG Channel Detail</div>
      <div class="controls">
        <div class="toggle" id="view-toggle" role="tablist" aria-label="Period-over-period view">
          <button type="button" data-v="mom" class="active" role="tab" aria-selected="true">MoM (MTD)</button>
          <button type="button" data-v="wow" role="tab" aria-selected="false">WoW</button>
          <button type="button" data-v="day" role="tab" aria-selected="false">Daily</button>
          <button type="button" data-v="r7" role="tab" aria-selected="false">7d</button>
          <button type="button" data-v="r14" role="tab" aria-selected="false">14d</button>
        </div>
        <input class="search" id="search" type="text" placeholder="Filter channels…" aria-label="Filter channels">
      </div>
    </div>
    <div class="view-cap" id="view-cap"></div>
    <div class="tbl-wrap"><table id="tbl"><thead><tr>
      <th data-k="channel" data-t="s">Channel</th>
      <th data-k="su">Signups</th><th data-k="tr">Trials</th>
      <th data-k="sub">Subscriptions</th><th data-k="fmrr">First MRR</th>
      <th data-k="attTr" data-fixed="1" class="attcol sep">Trials → Q3</th>
      <th data-k="attFmrr" data-fixed="1" class="attcol">First MRR → Q3</th>
    </tr></thead><tbody id="tbody"></tbody><tfoot id="tfoot"></tfoot></table></div>
    <div class="muted-note" id="chan-note"></div>
  </div>
  <div class="card">
    <div class="section-title" id="snap-title">Monthly Snapshot</div>
    <div class="spend-caveat" id="spend-caveat"></div>
    <div class="snap-kpis" id="snap-kpis"></div>
    <div style="font-size:11px;color:var(--dim);text-transform:uppercase;letter-spacing:.04em;margin:4px 0 8px">Spend by channel</div>
    <div class="snap-grid" id="snap-spend"></div>
    <div class="muted-note" id="snap-note"></div>
  </div>
  <div class="card">
    <div class="tbl-head">
      <div class="section-title" style="margin:0" id="int-title">Onboarding Intent</div>
      <div class="controls">
        <select class="sel" id="int-chan" aria-label="Filter by channel"></select>
        <div class="toggle" id="int-view" role="tablist" aria-label="Period-over-period view">
          <button type="button" data-v="mom" class="active" role="tab" aria-selected="true">MoM (MTD)</button>
          <button type="button" data-v="wow" role="tab" aria-selected="false">WoW</button>
          <button type="button" data-v="day" role="tab" aria-selected="false">Daily</button>
          <button type="button" data-v="r7" role="tab" aria-selected="false">7d</button>
          <button type="button" data-v="r14" role="tab" aria-selected="false">14d</button>
          <button type="button" data-v="r30" role="tab" aria-selected="false">30d</button>
          <button type="button" data-v="r90" role="tab" aria-selected="false">90d</button>
        </div>
        <div class="toggle" id="int-base" role="tablist" aria-label="Share base">
          <button type="button" data-b="ans" class="active" role="tab" aria-selected="true">% of answered</button>
          <button type="button" data-b="all" role="tab" aria-selected="false">% of all signups</button>
        </div>
      </div>
    </div>
    <div class="view-cap" id="int-cap"></div>
    <div class="tbl-wrap"><table id="itbl" class="bd"><thead><tr>
      <th data-k="name" data-t="s">Use case (signup question)</th>
      <th data-k="su">Signups<span class="conv-tag">count · Δ · was / share · Δ% · was</span></th><th data-k="tr">Trials<span class="conv-tag">count · Δ · was / share · Δ% · was</span></th>
      <th data-k="sub">Subscriptions<span class="conv-tag">count · Δ · was / share · Δ% · was</span></th><th data-k="fmrr">First MRR<span class="conv-tag">$ · Δ · was / share · Δ% · was</span></th>
      <th data-k="c_tr" class="conv sep">Signup → Trial<span class="conv-tag">ratio · Δ% · was</span></th>
      <th data-k="c_sub" class="conv">Trial → Sub<span class="conv-tag">ratio · Δ% · was</span></th>
      <th data-k="c_asp" class="conv">First MRR / sub<span class="conv-tag">average · Δ · was</span></th>
    </tr></thead><tbody id="ibody"></tbody><tfoot id="ifoot"></tfoot></table></div>
    <div class="subhead"><div>Subscriptions by use case × plan<span class="sub" id="plan-cap"></span></div>
      <div class="toggle sm" id="int-pm" role="tablist" aria-label="Plan matrix metric">
        <button type="button" data-m="sub" class="active" role="tab" aria-selected="true">New subs</button>
        <button type="button" data-m="fmrr" role="tab" aria-selected="false">First MRR</button>
      </div></div>
    <div class="tbl-wrap"><table id="ptbl" class="bd"><thead id="phead"></thead><tbody id="pbody"></tbody><tfoot id="pfoot"></tfoot></table></div>
    <div class="muted-note" id="int-note"></div>
  </div>
  <div class="card"><div class="section-title">Key Insights</div><div class="insights" id="insights"></div></div>
  <div class="footer" id="footer"></div>
</div>
<script>
const DATA = __DATA_JSON__;
const ANCHOR=DATA.ANCHOR, PLG_MRR=DATA.PLG_MRR, SLG_QRR=DATA.SLG_QRR, PLG=DATA.PLG, SLG=DATA.SLG,
      SPEND=DATA.SPEND, NEW_FIRST_MRR_MTD=DATA.NEW_FIRST_MRR_MTD, PLG_ARR=NEW_FIRST_MRR_MTD*12,
      SLG_ARR=DATA.SLG_ARR, RAW=DATA.RAW, NOTION_URL=DATA.NOTION_URL,
      CHAN=DATA.CHAN, QRR=DATA.QRR, CH_TGT=DATA.CH_TGT, Q_LABEL=DATA.Q_LABEL,
      MANUAL_BASIS=DATA.MANUAL_BASIS||{};
const nf=n=>Math.round(n).toLocaleString("en-US");
const money=n=>"$"+Math.round(n).toLocaleString("en-US");
const pct1=n=>(n>=0?"+":"")+Math.round(n*100)+"%";
const pop=(c,p)=>p?(c-p)/p:null;
const popCell=m=>{ if(m===null) return '<span class="na">-</span>';
  const c=Math.abs(m)<0.005?"flat":(m>0?"pos":"neg"); const a=Math.abs(m)<0.005?"→ ":(m>0?"↑ ":"↓ ");
  return '<span class="'+c+'">'+a+pct1(m)+'</span>'; };
function attBadge(a){ if(a===null) return '<span class="na">-</span>';
  let c=a>=1.0?"great":a>=0.75?"ok":a>=0.50?"attention":"critical";
  return '<span class="pill '+c+'">'+Math.round(a*100)+'%</span>'; }
const yToday={ys:0,yt:0,yf:0}; RAW.forEach(r=>{yToday.ys+=r[1];yToday.yt+=r[2];yToday.yf+=r[3];});
document.getElementById("hdr-date").textContent="Latest complete day: "+ANCHOR+"  ·  "+DATA.MONTH_LABEL+" MTD through "+DATA.SHORT_THROUGH;
document.getElementById("hdr-meta").innerHTML=
  "Monthly RR: <b>"+(PLG_MRR*100).toFixed(1)+"%</b> · Quarterly RR: <b>"+(SLG_QRR*100).toFixed(1)+"%</b><br>"+
  "Yesterday: <b>"+nf(yToday.ys)+"</b> signups · <b>"+nf(yToday.yt)+"</b> trials · <b>"+money(yToday.yf)+"</b> FMRR";
document.getElementById("chan-title").textContent="PLG Channel Detail - "+DATA.MONTH_LABEL;
document.getElementById("snap-title").textContent="Monthly Snapshot - "+DATA.MONTH_LABEL+" (MTD through "+DATA.SHORT_THROUGH+")";
document.getElementById("hl-note").innerHTML="PLG = month-to-date vs same window last month; projection = current ÷ monthly run-rate. SLG = "+DATA.SLG_Q_LABEL+" to date vs prior quarter same fiscal day; projection = current ÷ quarterly run-rate. Inbound SQLs only.";
function hlRow(name,o,rr,money_){ const proj=o.cur/rr, att=o.tgt?proj/o.tgt:null, fmt=money_?money:nf;
  return '<tr><td>'+name+'</td><td>'+(o.tgt?fmt(o.tgt):'<span class="na">-</span>')+'</td><td>'+fmt(o.cur)+
    '</td><td>'+fmt(proj)+'</td><td>'+attBadge(att)+'</td><td>'+popCell(pop(o.cur,o.prior))+'</td></tr>'; }
let hl='<tr class="group-label"><td colspan="6">PLG (Product-Led Growth) - MoM</td></tr>';
hl+=hlRow("Signups",PLG.signups,PLG_MRR,false); hl+=hlRow("Trials",PLG.trials,PLG_MRR,false);
hl+=hlRow("First MRR",PLG.fmrr,PLG_MRR,true); hl+=hlRow("Net MRR",PLG.net,PLG_MRR,true);
hl+='<tr class="group-label"><td colspan="6">SLG (Sales-Led Growth) - '+DATA.SLG_Q_LABEL+' · QoQ · Inbound</td></tr>';
SLG.forEach(s=>{ hl+=hlRow(s.name,{cur:s.cur,prior:s.prior,tgt:s.tgt},SLG_QRR,s.money); });
document.getElementById("hl-body").innerHTML=hl;
// ---- Channel detail: Daily/WoW/MoM toggle, channel groups with expansion, plan-based Q3 attainment ----
// CHAN row fields: 0 channel, 1-4 m_(su,tr,sub,fmrr), 5-8 pm_*, 9-12 w_*, 13-16 pw_*,
// 17 q_tr, 18 q_fmrr, 19 pq_tr, 20 pq_fmrr, 21-24 d_*, 25-28 pd_*, 29-32 r7_*, 33-36 pr7_*,
// 37-40 r14_*, 41-44 pr14_*
// Channel groups. Group names must match CHANNEL_Q_TARGETS keys - targets exist at the
// group level only, so attainment renders on group rows and standalone channels, never
// on sub-channels inside a group.
const GROUPS={
  // "paid search brand" is deliberately NOT in Paid - it has its own separate target
  // in the Q3 plan (Nir, 2026-08-05) and stays a standalone row with its own attainment.
  "Paid":["paid search","paid video","paid llms","paid social"],
  "Partnerships":["creator","partnerships"],
  "Affiliates":["affiliate","review_sites"]};
const IDX={su:{mom:[1,5],wow:[9,13],day:[21,25],r7:[29,33],r14:[37,41]}, tr:{mom:[2,6],wow:[10,14],day:[22,26],r7:[30,34],r14:[38,42]},
           sub:{mom:[3,7],wow:[11,15],day:[23,27],r7:[31,35],r14:[39,43]}, fmrr:{mom:[4,8],wow:[12,16],day:[24,28],r7:[32,36],r14:[40,44]}};
// Row length each view needs; a shorter row means the value file predates that view.
const VIEW_MINLEN={mom:9,wow:17,day:29,r7:37,r14:45};
function mkItem(name,rs,isGroup){
  const s=i=>rs.reduce((a,r)=>a+(r[i]||0),0);
  const o={ch:name,isGroup:!!isGroup,open:false,subs:[],qTr:s(17),qFmrr:s(18)};
  for(const k in IDX){o[k]={};for(const v in IDX[k])o[k][v]={c:s(IDX[k][v][0]),p:s(IDX[k][v][1])};}
  return o;}
// Targets come ONLY from the quarter plan (CH_TGT). A channel with no plan row - and every
// sub-channel - shows "-" for share and attainment; nothing is derived as a substitute.
function attain(o){ const t=CH_TGT&&CH_TGT.rows[o.ch];
  o.tgt=t||null;
  o.attTr=t&&t.tr?(o.qTr/QRR)/t.tr:null;
  o.attFmrr=t&&t.fmrr?(o.qFmrr/QRR)/t.fmrr:null; }
const byName={}; CHAN.forEach(r=>byName[r[0]]=r);
const grouped=new Set(Object.values(GROUPS).flat());
const topItems=[];
Object.entries(GROUPS).forEach(([g,members])=>{
  const rs=members.filter(m=>byName[m]).map(m=>byName[m]); if(!rs.length)return;
  const it=mkItem(g,rs,true); attain(it);
  it.subs=rs.map(r=>mkItem(r[0],[r],false));   // subs: no plan target -> attain() left unset -> "-"
  topItems.push(it); });
CHAN.filter(r=>!grouped.has(r[0])).forEach(r=>{const it=mkItem(r[0],[r],false); attain(it); topItems.push(it);});
const sumQtr=CHAN.reduce((a,r)=>a+r[17],0), sumQfmrr=CHAN.reduce((a,r)=>a+r[18],0);
const totAttTr=CH_TGT?(sumQtr/QRR)/CH_TGT.total.tr:null, totAttFmrr=CH_TGT?(sumQfmrr/QRR)/CH_TGT.total.fmrr:null;
let view="mom", sortK="fmrr", sortDir=-1;
const ppSpan=pp=>{ if(pp===null) return ' <span class="pp na">(-)</span>';
  const c=Math.abs(pp)<0.005?"flat":(pp>0?"pos":"neg"), a=Math.abs(pp)<0.005?"→":(pp>0?"↑":"↓");
  return ' <span class="pp '+c+'">('+a+pct1(pp)+')</span>'; };
const metricCell=(m,fmt)=>{ const o=m[view];
  return '<span class="mv">'+fmt(o.c)+'</span>'+((o.p||o.c)?ppSpan(pop(o.c,o.p)):''); };
// share = plan / actual. Plan is the channel's planned share of the quarter's first MRR, exactly
// as in the plan doc; actual is its share of First MRR in the active view's window (so it follows
// the toggle). Actual reads green at or above plan, red below; rows with no plan show "-" for plan.
let viewTotF=0;
const nameCell=it=>{ const act=viewTotF?it.fmrr[view].c/viewTotF*100:null, plan=it.tgt?it.tgt.share:null;
  const actCls=act===null?'na':plan===null?'dim':act>=plan?'up':'down';
  const tip='Plan '+(plan===null?'-':plan+'%')+' / actual '+(act===null?'-':act.toFixed(1)+'%')+' of '+DATA.VIEW_LABELS[view][0]+' First MRR';
  const sh=' <span class="share" title="'+tip+'">('+(plan===null?'<span class="na">-</span>':plan+'%')+
    '<span class="slash">/</span><span class="act '+actCls+'">'+(act===null?'-':act.toFixed(1)+'%')+'</span>)</span>';
  if(it.isGroup) return '<span class="caret">'+(it.open?"▾":"▸")+'</span>'+it.ch+sh+
    '<span class="exp-hint">'+(it.open?'▾ hide':'▸ '+it.subs.length+' channels')+'</span>';
  return '<span class="caret"></span>'+it.ch+sh; };
const rowHtml=(it,cls)=>'<tr'+(cls?' class="'+cls+'"':'')+(it.isGroup?' data-g="'+it.ch+'"':'')+'>'+
  '<td>'+nameCell(it)+'</td>'+
  '<td>'+metricCell(it.su,nf)+'</td>'+'<td>'+metricCell(it.tr,nf)+'</td>'+
  '<td>'+metricCell(it.sub,nf)+'</td>'+'<td>'+metricCell(it.fmrr,money)+'</td>'+
  '<td class="attcol sep">'+attBadge(it.attTr===undefined?null:it.attTr)+'</td>'+
  '<td class="attcol">'+attBadge(it.attFmrr===undefined?null:it.attFmrr)+'</td></tr>';
const sortVal=(r,k)=>{ if(k==="channel") return r.ch;
  if(k==="attTr") return r.attTr==null?-1e18:r.attTr;
  if(k==="attFmrr") return r.attFmrr==null?-1e18:r.attFmrr;
  return r[k][view].c; };
function render(){ const q=document.getElementById("search").value.trim().toLowerCase();
  viewTotF=topItems.reduce((a,r)=>a+r.fmrr[view].c,0);   // denominator for the actual share, this view
  let list=topItems.filter(it=>it.ch.toLowerCase().includes(q)||it.subs.some(s=>s.ch.toLowerCase().includes(q)));
  list.sort((a,b)=>{ let x=sortVal(a,sortK),y=sortVal(b,sortK);
    if(typeof x==="string"){x=x.toLowerCase();y=y.toLowerCase();return x<y?-sortDir:x>y?sortDir:0;} return (x-y)*sortDir; });
  document.getElementById("tbody").innerHTML=list.map(it=>{
    const showSubs=it.isGroup&&(it.open||(q&&it.subs.some(s=>s.ch.toLowerCase().includes(q))));
    return rowHtml(it,it.isGroup?"grp":"")+
      (showSubs?it.subs.slice().sort((a,b)=>(sortVal(b,sortK==="channel"?"fmrr":sortK)-(sortVal(a,sortK==="channel"?"fmrr":sortK)))).map(s=>rowHtml(s,"sub")).join(""):"");
  }).join("");
  const T=topItems.reduce((a,r)=>{["su","tr","sub","fmrr"].forEach(k=>{a[k]=(a[k]||0)+r[k][view].c;a["p"+k]=(a["p"+k]||0)+r[k][view].p;});return a;},{});
  const totCell=(cur,prev,fmt)=>'<span class="mv">'+fmt(cur)+'</span>'+(pop(cur,prev)===null?'':ppSpan(pop(cur,prev)));
  // Total row leads the table (Nir, 2026-09-16); it stays put through sorting because render() prepends it.
  const totalRow='<tr class="total lead"><td>TOTAL - '+CHAN.length+' channels</td>'+
    '<td>'+totCell(T.su,T.psu,nf)+'</td>'+'<td>'+totCell(T.tr,T.ptr,nf)+'</td>'+
    '<td>'+totCell(T.sub,T.psub,nf)+'</td>'+'<td>'+totCell(T.fmrr,T.pfmrr,money)+'</td>'+
    '<td class="attcol sep">'+attBadge(totAttTr)+'</td>'+'<td class="attcol">'+attBadge(totAttFmrr)+'</td></tr>';
  document.getElementById("tbody").insertAdjacentHTML("afterbegin", totalRow);
  document.getElementById("tfoot").innerHTML='';
  document.querySelectorAll("#tbl th").forEach(th=>{ const base=th.dataset.base||(th.dataset.base=th.textContent.replace(/[▲▼]/g,"").trim());
    const arr=th.dataset.k===sortK?' <span class="arr">'+(sortDir<0?"▼":"▲")+'</span>':"";
    const tag=th.dataset.fixed?'<span class="fixed-tag">fixed · run-rate vs plan</span>':"";
    th.innerHTML=base+arr+tag; });
  const VL=DATA.VIEW_LABELS[view], vname={mom:"MoM",wow:"WoW",day:"Daily",r7:"7d",r14:"14d"}[view];
  // Each view reads a fixed slice of the row; a value file built before that view existed would
  // otherwise render it as all zeros and look like a broken toggle. Say so instead.
  const missing=CHAN.some(r=>r.length<VIEW_MINLEN[view]);
  const how={mom:' (same days last month)',wow:' (same elapsed days)',day:' (same weekday last week)',
             r7:' (last 7 days vs the 7 before)',r14:' (last 14 days vs the 14 before)'}[view];
  document.getElementById("view-cap").innerHTML=
    'Showing <b>'+vname+'</b>: <b>'+VL[0]+'</b> vs '+VL[1]+how+
    ' · <span class="lock">🔒</span> <b>→ '+Q_LABEL+'</b> columns fixed: QTD run-rate vs plan'+
    (missing?' · <span class="warn">'+vname+' fields missing from this build - values show 0</span>':''); }
document.getElementById("tbody").addEventListener("click",e=>{
  const tr=e.target.closest("tr[data-g]"); if(!tr)return;
  const it=topItems.find(x=>x.ch===tr.dataset.g); if(it){it.open=!it.open; render();} });
document.querySelectorAll("#tbl th").forEach(th=>th.addEventListener("click",()=>{ const k=th.dataset.k;
  if(k===sortK)sortDir*=-1; else{sortK=k;sortDir=(th.dataset.t==="s")?1:-1;} render(); }));
document.querySelectorAll("#view-toggle button").forEach(b=>b.addEventListener("click",()=>{
  view=b.dataset.v;
  document.querySelectorAll("#view-toggle button").forEach(x=>{const on=x===b;x.classList.toggle("active",on);x.setAttribute("aria-selected",on);});
  render(); }));
document.getElementById("search").addEventListener("input",render);
document.getElementById("chan-note").innerHTML=
  "Click a bold group row (▸) to expand its sub-channels; click any column header to sort. The toggle switches the four metric columns between MoM, WoW, Daily, 7d and 14d; the caption above the table names the exact dates each view compares. Parenthetical is the period-over-period change. "+
  (CH_TGT?
    "<b>(plan% / actual%)</b> next to each name: plan is the channel's planned share of the quarter's First MRR; actual is its share of First MRR in the view you have selected, green at or above plan, red below. <b>"+Q_LABEL+" attainment</b> = run-rate-projected quarter total ÷ the channel's "+Q_LABEL+
    " plan target - both from the <a href=\"https://claude.ai/code/artifact/34ed9a9f-c6c4-4da1-8270-d542fd13ba1e\" style=\"color:var(--accent)\">Growth Marketing Q3 2026 Plan</a> ($900K quarter, +4% MoM on a July rollover base). "+
    "Targets exist at the channel-group level only - sub-channels and unplanned channels (product share, webinar_guest) show - for plan and attainment; their actual share still renders. "+
    "Quarterly run-rate is only "+(QRR*100).toFixed(1)+"% this early in "+Q_LABEL+", so attainment swings hard now and settles as the quarter fills in."
   :"No channel-target plan is loaded for this quarter, so share and "+Q_LABEL+" attainment show - (targets are never derived from history; add the quarter to CHANNEL_Q_TARGETS in build_artifact.py once the plan is set).");
render();
const totalSpend=Object.values(SPEND).reduce((a,b)=>a+b,0), totalARR=PLG_ARR+SLG_ARR, roi=(totalARR-totalSpend)/totalSpend;
document.getElementById("snap-kpis").innerHTML=[
  {l:"Total Spend",v:money(totalSpend),s:"platform + invoice-board lines + SEO<br>MTD actual · <b>"+money(DATA.PROJ_MONTH_SPEND)+"</b> projected full month"},
  {l:"PLG ARR",v:money(PLG_ARR),s:"New First MRR MTD × 12"},
  {l:"SLG ARR",v:money(SLG_ARR),s:"manual input"},
  {l:"Total ARR",v:money(totalARR),s:"PLG + SLG"},
  {l:"ROI",v:(roi*100).toFixed(1)+"%",s:"(ARR − Spend) ÷ Spend"},
].map(k=>'<div class="snap-kpi"><div class="label">'+k.l+'</div><div class="big">'+k.v+'</div><div class="sub">'+k.s+'</div></div>').join("");
document.getElementById("snap-spend").innerHTML=Object.entries(SPEND).map(([k,v])=>
  '<div class="spend-cell"><div class="k">'+k+'</div><div class="v">'+money(v)+'</div></div>').join("");
document.getElementById("snap-note").innerHTML="Platform spend is raw daily_cost_in_usd by channel (MTD). PLG ARR = New First MRR MTD ("+money(NEW_FIRST_MRR_MTD)+") × 12. Growth Channels, Creative partnerships, Affiliates, Affiliate freelancers &amp; platforms and B2B vendors are Invoices and Payments board actuals computed at build (manual_inputs.json when the board is unreachable): the board's Type column splits affiliate and B2B vendor invoices onto their own lines, whoever paid them. SEO and SLG ARR are manual inputs (manual_inputs.json).";
// Spend-basis caveat. Fires when any manual line is an invoices-filed actual: those lag the spend
// they represent, so MTD total spend is understated and the ROI above reads high. Naming the lines
// beats a generic disclaimer - the reader can see which figures to distrust and by roughly how much.
const BASIS_LABEL={growth_channels_spend:("Other Growth Channels" in SPEND)?"Other Growth Channels":"Growth Channels",seo_spend:"SEO",
                   creative_partnerships_spend:"Creative partnerships",slg_arr:"SLG ARR",
                   affiliates_spend:"Affiliates",affiliate_freelancers_spend:"Affiliate freelancers &amp; platforms",
                   b2b_vendors_spend:"B2B vendors"};
const andList=a=>a.length<2?a.join(""):a.slice(0,-1).join(", ")+" and "+a[a.length-1];
const lagging=Object.keys(MANUAL_BASIS).filter(k=>MANUAL_BASIS[k]==="invoice_actual").map(k=>BASIS_LABEL[k]||k);
const prorated=Object.keys(MANUAL_BASIS).filter(k=>MANUAL_BASIS[k]==="budget_prorated").map(k=>BASIS_LABEL[k]||k);
if(lagging.length){
  const el=document.getElementById("spend-caveat");
  el.className="spend-caveat on";
  el.innerHTML="<b>⚠ Mixed spend basis - read ROI with care.</b> "+
    "<b>"+andList(lagging)+"</b> "+(lagging.length>1?"are":"is")+" taken from the Invoices and Payments board, "+
    "which records invoices <i>filed</i> rather than spend <i>accrued</i>. Invoices arrive after the spend, so these "+
    "lines understate the month-to-date figure"+
    (prorated.length?", while <b>"+andList(prorated)+"</b> "+(prorated.length>1?"remain":"remains")+" a monthly budget pro-rated by the run-rate":"")+
    ". Total Spend is therefore understated and the <b>ROI above is inflated and not comparable</b> "+
    "to prior runs or to the ROI &amp; Growth report, which prices every line off the fixed monthly budgets. "+
    "Use this panel for the channel mix, not for a spend or ROI number you intend to quote.";
}
// ---- Onboarding intent + declared source: who signs up for what, by channel, same five views as the channel table ----
// INTENT rows (collapsed): 0 channel, 1 bucket, then the window fields: 2-5 m_(su,tr,sub,fmrr), 6-9 pm_, 10-13 w_, 14-17 pw_,
// 18-21 d_, 22-25 pd_, 26-29 r7_, 30-33 pr7_, 34-37 r14_, 38-41 pr14_ (the channel-table layout minus its q_/pq_ fields).
// INTENT_PLAN rows: 0 channel, 1 intent, 2 plan, then (sub,fmrr) pairs for the same fourteen windows (WIN_ORDER): 3-4 m_ ... 29-30 pr90_.
const INTENT=DATA.INTENT||[], ILBL=DATA.INTENT_LABELS||{}, IPLAN=DATA.INTENT_PLAN||[], PLANS=DATA.PLANS||["Pro","Grow","Webinar","Mobile Plus","Other"];
const WIN_ORDER=["m","pm","w","pw","d","pd","r7","pr7","r14","pr14","r30","pr30","r90","pr90"], VIEWPAIR={mom:["m","pm"],wow:["w","pw"],day:["d","pd"],r7:["r7","pr7"],r14:["r14","pr14"],r30:["r30","pr30"],r90:["r90","pr90"]};
const mkIdx=(base,width,mi)=>{const o={};for(const v in VIEWPAIR){const [c,p]=VIEWPAIR[v];o[v]=[base+WIN_ORDER.indexOf(c)*width+mi,base+WIN_ORDER.indexOf(p)*width+mi];}return o;};
const IIDX={su:mkIdx(2,4,0),tr:mkIdx(2,4,1),sub:mkIdx(2,4,2),fmrr:mkIdx(2,4,3)};
const PIDX={sub:mkIdx(3,2,0),fmrr:mkIdx(3,2,1)};
// Gates. A change against a prior window with thin intent coverage (the question is new - week of Aug 31 - so MoM and
// 14d/30d priors are mostly "no answer" until October) is still SHOWN, but dimmed and capped at >999%, so the reader
// sees direction without mistaking a coverage ramp for a trend (Nir, 2026-09-16: hiding it read as "no change").
// A ratio needs enough volume in its denominator to mean anything at all.
const I_MIN_COV=0.20, I_MIN_N=100, I_MIN_SU=50, I_MIN_TR=20, I_MIN_SUB=5, I_MIN_ROWP=20;
const M4=["su","tr","sub","fmrr"], FMT={su:nf,tr:nf,sub:nf,fmrr:money};
let iview="mom", ibase="ans", ichan="__all", ipm="sub";
const isort={k:"su",dir:-1};
const ichanSel=document.getElementById("int-chan");
const ichans=[...new Set(INTENT.map(r=>r[0]))].sort();
ichanSel.innerHTML='<option value="__all">All channels</option>'+
  Object.keys(GROUPS).filter(g=>GROUPS[g].some(c=>ichans.includes(c))).map(g=>'<option value="__g:'+g+'">'+g+' (group)</option>').join("")+
  ichans.map(c=>'<option value="'+c+'">'+c+'</option>').join("");
const iLabel=k=>ILBL[k]||k;
const chanLabel=()=>ichan==="__all"?"all channels":ichan.startsWith("__g:")?ichan.slice(4)+" group":ichan;
const chanFilter=rows=>{ if(ichan==="__all") return rows;
  if(ichan.startsWith("__g:")){ const m=new Set(GROUPS[ichan.slice(4)]||[]); return rows.filter(r=>m.has(r[0])); }
  return rows.filter(r=>r[0]===ichan); };
function aggRows(rows,IDX){ const by={};
  rows.forEach(r=>{ const o=by[r[1]]||(by[r[1]]={key:r[1]});
    for(const m in IDX){ o[m]=o[m]||{}; for(const v in IDX[m]){ const [ci,pi]=IDX[m][v]; const t=o[m][v]||(o[m][v]={c:0,p:0}); t.c+=r[ci]||0; t.p+=r[pi]||0; } } });
  return Object.values(by); }
// Change is always shown as the absolute difference with the prior value beside it ("▲ +13,621 · was 5"),
// never as a growth percentage: against a prior of 5 answers a growth % is a meaningless five-digit number,
// while "+13,621, was 5" says exactly what happened (Nir, 2026-09-16, third pass on this card).
const NA=' <span class="dl na">-</span>';
const sgn=(d,fmt)=>(d>0?"+":d<0?"−":"±")+fmt(Math.abs(d));
const arrow=d=>Math.abs(d)<1e-9?"":d>0?"▲ ":"▼ ";
const cls3=d=>Math.abs(d)<1e-9?"flat":d>0?"pos":"neg";
const dAbs=(c,p,fmt)=>' <span class="dl '+cls3(c-p)+'">'+arrow(c-p)+sgn(c-p,fmt)+'</span> <span class="was">was '+fmt(p)+'</span>';
// Relative change of a share or ratio, per Nir 2026-09-16 - not percentage points. At most one decimal, and
// from +1,000% up it becomes a multiple ("▲ ×75 · was 0.2%"): "+7,425%" read as seven-point-four with three
// decimals, which is the opposite of what it meant.
const relPct=m=>{ const v=Math.abs(m)*100; if(m>0&&v>=1000){ const x=m+1; return "×"+(x<10?x.toFixed(1):String(Math.round(x))); }
  return (m>0?"+":m<0?"−":"±")+(v>=100?String(Math.round(v)):v.toFixed(1))+"%"; };
const dPP=(c,p,ok=true,nPrior=null)=>{
  // Prior predates the question (thin coverage): a computed change would compare against a few hundred test-flow
  // answers, so show the prior share and how many answers it rests on, and no arrow (Nir, 2026-09-16: "there wasn't a x75").
  if(!ok) return ' <span class="was">was '+(p*100).toFixed(1)+'%'+(nPrior!==null?' of '+nf(nPrior):'')+'</span>';
  if(!p) return c?' <span class="dl pos">new</span> <span class="was">was 0.0%</span>':''; const m=(c-p)/p;
  return ' <span class="dl '+cls3(m)+'">'+arrow(m)+relPct(m)+'</span> <span class="was">was '+(p*100).toFixed(1)+'%</span>'; };
const dpp=(d)=>' <span class="dl '+cls3(d)+'">'+arrow(d)+(d>0?"+":d<0?"−":"±")+Math.abs(d).toFixed(1)+'pp</span>';
const dpct=(c,p)=>dAbs(c,p,nf);
const two=(l1,l2)=>'<div class="l1">'+l1+'</div>'+(l2?'<div class="l2">'+l2+'</div>':'');
// One breakdown table (intent or declared source): coverage row, one row per answer, no-answer row, total row,
// plus three same-window ratio columns. Every count carries its period change; every share its change in pp.
function renderBreakdown(cfg){
  const items=aggRows(chanFilter(cfg.rows),IIDX), answered=items.filter(o=>o.key!=="no_answer"), noans=items.find(o=>o.key==="no_answer");
  const tot={}, totAns={};
  M4.forEach(m=>{ tot[m]={c:0,p:0}; totAns[m]={c:0,p:0};
    items.forEach(o=>{tot[m].c+=o[m][iview].c;tot[m].p+=o[m][iview].p;});
    answered.forEach(o=>{totAns[m].c+=o[m][iview].c;totAns[m].p+=o[m][iview].p;}); });
  const base=ibase==="ans"?totAns:tot;
  const priorOk=m=>tot[m].p>0&&totAns[m].p/tot[m].p>=I_MIN_COV&&totAns[m].p>=I_MIN_N;
  const cell=(o,m,isNoAns)=>{ const v=o[m][iview], den=isNoAns?tot[m]:base[m], ok=isNoAns||priorOk(m);
    const sc=den.c?v.c/den.c:null, sp=den.p?v.p/den.p:null;
    const l1='<span class="mv">'+FMT[m](v.c)+'</span>'+dAbs(v.c,v.p,FMT[m]);
    const l2=sc===null?'':'<span class="sh">'+(sc*100).toFixed(1)+'%</span>'+(sp!==null?dPP(sc,sp,ok,den.p):'');
    return two(l1,l2); };
  // A ratio's change is only shown when the prior window clears BOTH the volume floor and the coverage gate on
  // the denominator metric - a prior window with 5 answered signups and 120 old-form trials reads as a 2400% ratio.
  const rate=(a,b,minB,ok)=>{ const c=b.c>=minB?a.c/b.c:null, p=b.p>=minB?a.p/b.p:null;
    return c===null?'<span class="na">-</span>':two('<span class="mv">'+(c*100).toFixed(1)+'%</span>', p!==null?dPP(c,p,ok,ok?null:b.p).trim():'<span class="was">no prior above the volume floor</span>'); };
  const asp=(f,sub,ok)=>{ const c=sub.c>=I_MIN_SUB?f.c/sub.c:null, p=sub.p>=I_MIN_SUB?f.p/sub.p:null;
    return c===null?'<span class="na">-</span>':two('<span class="mv">'+money(c)+'</span>', p!==null?(ok?dAbs(c,p,money).trim():'<span class="was">was '+money(p)+' on '+nf(sub.p)+' subs</span>'):'<span class="was">no prior above the volume floor</span>'); };
  const convCells=(o,isTotal)=>'<td class="conv sep">'+rate(o.tr[iview],o.su[iview],I_MIN_SU,isTotal||priorOk("su"))+'</td><td class="conv">'+rate(o.sub[iview],o.tr[iview],I_MIN_TR,isTotal||priorOk("tr"))+'</td><td class="conv">'+asp(o.fmrr[iview],o.sub[iview],isTotal||priorOk("sub"))+'</td>';
  const sv=o=>{ const k=cfg.sort.k; if(k==="name") return cfg.label(o.key).toLowerCase();
    if(k==="c_tr") return o.su[iview].c>=I_MIN_SU?o.tr[iview].c/o.su[iview].c:-1;
    if(k==="c_sub") return o.tr[iview].c>=I_MIN_TR?o.sub[iview].c/o.tr[iview].c:-1;
    if(k==="c_asp") return o.sub[iview].c>=I_MIN_SUB?o.fmrr[iview].c/o.sub[iview].c:-1;
    return o[k][iview].c; };
  const list=answered.slice().sort((a,b)=>{ const x=sv(a),y=sv(b); if(typeof x==="string") return x<y?-cfg.sort.dir:x>y?cfg.sort.dir:0; return (x-y)*cfg.sort.dir; });
  const covCell=m=>{ const c=tot[m].c?totAns[m].c/tot[m].c:null, p=tot[m].p?totAns[m].p/tot[m].p:null;
    return two((c===null?'<span class="na">-</span>':'<span class="mv">'+(c*100).toFixed(1)+'%</span> <span class="was">'+FMT[m](totAns[m].c)+' of '+FMT[m](tot[m].c)+'</span>'),
               (p===null?'':'<span class="was">was '+(p*100).toFixed(1)+'% · '+FMT[m](totAns[m].p)+' of '+FMT[m](tot[m].p)+'</span>')); };
  const anyThin=M4.some(m=>!priorOk(m));
  let html='<tr class="cov"><td>Answered the question'+(anyThin?' <span class="thinpill" title="the prior window has under '+(I_MIN_COV*100)+'% answered or fewer than '+I_MIN_N+' answers on at least one metric - the question was still rolling out, so most of a change is people starting to answer">thin prior</span>':'')+'</td>'+M4.map(m=>'<td>'+covCell(m)+'</td>').join("")+'<td class="conv sep" colspan="3"><span class="na">ratios are within each row</span></td></tr>';
  if(!cfg.rows.length) html+='<tr><td colspan="8" class="na">No rows in this build ('+cfg.missing+' missing from report_values.json).</td></tr>';
  else if((DATA.INTENT_MISSING||[]).includes(iview)) html+='<tr><td colspan="8" class="warn">'+({r30:"30d",r90:"90d"})[iview]+' fields missing from this build - this view shows zeros until the next refresh runs the current Q8.</td></tr>';
  html+=list.map(o=>'<tr'+(cfg.dim.includes(o.key)?' class="dimrow"':'')+'><td>'+cfg.label(o.key)+'</td>'+M4.map(m=>'<td>'+cell(o,m,false)+'</td>').join("")+convCells(o,false)+'</tr>').join("");
  if(noans) html+='<tr class="dimrow"><td>'+cfg.label("no_answer")+'</td>'+M4.map(m=>'<td>'+cell(noans,m,true)+'</td>').join("")+'<td class="conv sep" colspan="3"></td></tr>';
  document.getElementById(cfg.body).innerHTML=html;
  const T={key:"__tot"}; M4.forEach(m=>T[m]={[iview]:tot[m]});
  document.getElementById(cfg.foot).innerHTML='<tr class="total"><td>TOTAL - '+chanLabel()+'</td>'+M4.map(m=>'<td>'+two('<span class="mv">'+FMT[m](tot[m].c)+'</span>'+dAbs(tot[m].c,tot[m].p,FMT[m]))+'</td>').join("")+convCells(T,true)+'</tr>';
  document.querySelectorAll("#"+cfg.table+" th").forEach(th=>{ const b=th.dataset.base||(th.dataset.base=th.innerHTML);
    th.innerHTML=b+(th.dataset.k===cfg.sort.k?' <span class="arr">'+(cfg.sort.dir<0?"▼":"▲")+'</span>':""); });
  return {tot,totAns,priorOk};
}
// Use case x plan matrix on new subscriptions (or their First MRR): count with period change, then the plan's
// share of that use case's row with its change in pp. Trials carry a plan on only ~14% of rows, so subs only.
function renderPlan(){
  const [ci,pi]=PIDX[ipm][iview], fmt=FMT[ipm], by={}, tot={}, all={c:0,p:0}; PLANS.forEach(p=>tot[p]={c:0,p:0});
  chanFilter(IPLAN).forEach(r=>{ const o=by[r[1]]||(by[r[1]]={_row:{c:0,p:0}}); const pl=PLANS.includes(r[2])?r[2]:"Other";
    const t=o[pl]||(o[pl]={c:0,p:0}); const c=r[ci]||0, p=r[pi]||0; t.c+=c; t.p+=p; o._row.c+=c; o._row.p+=p; tot[pl].c+=c; tot[pl].p+=p; all.c+=c; all.p+=p; });
  const keys=Object.keys(by).filter(k=>k!=="no_answer").sort((a,b)=>by[b]._row.c-by[a]._row.c); if(by.no_answer) keys.push("no_answer");
  // Coverage gate for this metric: answered share of the prior window's subs (or their First MRR).
  const ansP=all.p-((by.no_answer||{})._row||{p:0}).p, okP=all.p>0&&ansP/all.p>=I_MIN_COV&&ansP>=(ipm==="sub"?I_MIN_N:1);
  document.getElementById("phead").innerHTML='<tr><th>Use case</th>'+PLANS.map(p=>'<th>'+p+'</th>').join("")+'<th class="sep">Row total</th></tr>';
  const cell=(t,row,ok)=>{ t=t||{c:0,p:0}; const sc=row.c?t.c/row.c:null, sp=row.p?t.p/row.p:null;
    return two('<span class="mv">'+fmt(t.c)+'</span>'+((t.c||t.p)?dAbs(t.c,t.p,fmt):''), sc===null?'':'<span class="sh">'+(sc*100).toFixed(0)+'%</span>'+(sp!==null?dPP(sc,sp,ok,ok?null:row.p):'')); };
  document.getElementById("pbody").innerHTML=keys.length?keys.map(k=>{ const ok=k==="no_answer"||okP;
      return '<tr'+(k==="legacy"||k==="no_answer"?' class="dimrow"':'')+'><td>'+iLabel(k)+'</td>'+
      PLANS.map(p=>'<td>'+cell(by[k][p],by[k]._row,ok)+'</td>').join("")+'<td class="sep">'+two('<span class="mv">'+fmt(by[k]._row.c)+'</span>'+dAbs(by[k]._row.c,by[k]._row.p,fmt))+'</td></tr>'; }).join("")
    :'<tr><td colspan="7" class="na">No plan rows in this build (plg_intent_rows missing from report_values.json).</td></tr>';
  document.getElementById("pfoot").innerHTML='<tr class="total"><td>TOTAL - '+chanLabel()+'</td>'+PLANS.map(p=>'<td>'+two('<span class="mv">'+fmt(tot[p].c)+'</span>'+dAbs(tot[p].c,tot[p].p,fmt),'<span class="sh">'+(all.c?(tot[p].c/all.c*100).toFixed(0):"0")+'%</span>'+(all.p?dPP(all.c?tot[p].c/all.c:0,tot[p].p/all.p):''))+'</td>').join("")+
    '<td class="sep">'+two('<span class="mv">'+fmt(all.c)+'</span>'+dAbs(all.c,all.p,fmt))+'</td></tr>';
  document.getElementById("plan-cap").innerHTML=(ipm==="sub"?"New subscriptions":"First MRR of new subscriptions")+" · "+DATA.VIEW_LABELS[iview][0]+" vs "+DATA.VIEW_LABELS[iview][1]+" · each cell: count with its absolute change and the prior, then the plan's share of that use case's row with its % change from the prior period"+
    (okP?"":' · <span class="thinpill">thin prior</span> the prior window predates the question: row shares show the prior share and its sample size, no computed change');
}
function iRenderAll(){
  const a=renderBreakdown({rows:INTENT,label:iLabel,body:"ibody",foot:"ifoot",table:"itbl",sort:isort,dim:["legacy"],missing:"plg_intent_rows",rowlen:2+WIN_ORDER.length*4});
  renderPlan();
  const VL=DATA.VIEW_LABELS[iview], vname={mom:"MoM",wow:"WoW",day:"Daily",r7:"7d",r14:"14d",r30:"30d",r90:"90d"}[iview];
  const how={mom:' (same days last month)',wow:' (same elapsed days)',day:' (same weekday last week)',r7:' (last 7 days vs the 7 before)',r14:' (last 14 days vs the 14 before)',r30:' (last 30 days vs the 30 before)',r90:' (last 90 days vs the 90 before)'}[iview];
  const thin=M4.filter(m=>!a.priorOk(m)).length;
  document.getElementById("int-cap").innerHTML='Showing <b>'+vname+'</b>: <b>'+VL[0]+'</b> vs '+VL[1]+how+' · channel: <b>'+chanLabel()+'</b>'+
    ' · share of: <b>'+(ibase==="ans"?"answered respondents":"all signups, incl. no answer")+'</b>'+
    '<br>Each cell, line 1: <b>count</b>, its absolute change, the prior value. Line 2: <b>share</b>, its % change from the prior period, the prior share.'+
    (thin?'<br><span class="thinpill">thin prior</span> <b>The prior window predates the question</b> (live in signup since Aug 31, 2026): only <b>'+nf(a.totAns.su.p)+'</b> of '+nf(a.tot.su.p)+' signups in '+DATA.VIEW_LABELS[iview][1]+' answered it. Share changes on this view compare against that small early sample; a share of all signups mostly measures how many were asked. WoW and 7d have a like-for-like prior.':'');
}
document.getElementById("int-title").textContent="Onboarding Intent - "+DATA.MONTH_LABEL;
[["itbl",isort]].forEach(([id,st])=>document.querySelectorAll("#"+id+" th").forEach(th=>th.addEventListener("click",()=>{ const k=th.dataset.k; if(!k) return;
  if(k===st.k) st.dir*=-1; else { st.k=k; st.dir=(th.dataset.t==="s")?1:-1; } iRenderAll(); })));
const bindToggle=(id,attr,set)=>document.querySelectorAll("#"+id+" button").forEach(b=>b.addEventListener("click",()=>{ set(b.dataset[attr]);
  document.querySelectorAll("#"+id+" button").forEach(x=>{const on=x===b;x.classList.toggle("active",on);x.setAttribute("aria-selected",on);}); iRenderAll(); }));
bindToggle("int-view","v",v=>iview=v); bindToggle("int-base","b",v=>ibase=v); bindToggle("int-pm","m",v=>ipm=v);
ichanSel.addEventListener("change",()=>{ ichan=ichanSel.value; iRenderAll(); });
document.getElementById("int-note").innerHTML=
  "Use case = the single answer to the \"what will you use Riverside for\" question in signup (<code>metadata_purposes</code> in analytics.bi.marketing_rollover). "+
  "Trial and subscription rows carry the account's answer from its signup, so their coverage lags signups by the time it takes to convert. "+
  "The use-case question shipped in this form the week of Aug 31, 2026, so month-over-month and 14-day priors are mostly \"no answer\" until October; changes are absolute (count now minus count in the prior window, with the prior shown), never growth percentages, so a prior of 5 answers reads as \"+13,621 · was 5\" rather than a five-digit percent. 30d = the last 30 complete days vs the 30 before, the ROI report's trailing definition. 90d = the last 90 complete days vs the 90 before. "+
  "Share is of answered respondents by default - the mix of what people say they want - because a share of all signups moves with how many were asked (0.3% in August, ~70% now) rather than with intent; flip to % of all signups for the raw mix. "+
  "Share and ratio changes are relative (% from the prior period), with the prior value beside them. Ratios are same-window (trials this window ÷ signups this window), not cohort conversion, and show only above "+I_MIN_SU+" signups / "+I_MIN_TR+" trials / "+I_MIN_SUB+" subs. "+
  "The channel filter uses the same channel_group values and Paid / Partnerships / Affiliates groups as the channel table and applies to both tables. Click a column header to sort."+
  (DATA.INTENT_LEGACY_SEEN&&DATA.INTENT_LEGACY_SEEN.length?" <b>Legacy bucket</b> collapses answers from the retired multi-select form: "+DATA.INTENT_LEGACY_SEEN.map(t=>t==="legacy_multi"?"any comma-separated answer":t).join(", ")+".":"")+
  (DATA.INTENT_UNKNOWN&&DATA.INTENT_UNKNOWN.length?' <span class="warn"><b>Unrecognised intent tokens</b> kept as their own rows (add them to INTENT_TAXONOMY or INTENT_LEGACY_TOKENS in build_artifact.py): '+DATA.INTENT_UNKNOWN.join(", ")+'.</span>':"");
iRenderAll();
const netPop=pop(PLG.net.cur,PLG.net.prior),trialsPop=pop(PLG.trials.cur,PLG.trials.prior),fmrrPop=pop(PLG.fmrr.cur,PLG.fmrr.prior),suPop=pop(PLG.signups.cur,PLG.signups.prior);
const slgWon=SLG[SLG.length-1];
const byFmrrAtt=topItems.filter(r=>r.attFmrr!==null).slice().sort((a,b)=>b.attFmrr-a.attFmrr);
const topAtt=byFmrrAtt[0]||{ch:"-",attFmrr:null};
const byTrMom=topItems.slice().sort((a,b)=>b.tr.mom.c-a.tr.mom.c);
const topTr=byTrMom[0]||{ch:"-",tr:{mom:{c:0,p:0}}};
const insights=[
  {h:"Net MRR is the soft spot",b:"Net MRR MTD <b>"+money(PLG.net.cur)+"</b>"+(PLG.net.tgt?" tracks to <b>"+((PLG.net.cur/PLG_MRR)/PLG.net.tgt*100).toFixed(0)+"%</b> of target and":" (no target set)")+" <b>"+pct1(netPop)+"</b> MoM. Signups <b>"+pct1(suPop)+"</b> and trials <b>"+pct1(trialsPop)+"</b>; First MRR <b>"+pct1(fmrrPop)+"</b>.",d:"→ Watch reduction/churn MRR cohorts - volume held, monetization slipped."},
  {h:"Channel "+Q_LABEL+" attainment",b:"Leading First-MRR "+Q_LABEL+" attainment: <b>"+topAtt.ch+"</b> ("+(topAtt.attFmrr!==null?(topAtt.attFmrr*100).toFixed(0)+"%":"-")+" of its run-rate target). Top channel by MTD trials: <b>"+topTr.ch+"</b> ("+pct1(pop(topTr.tr.mom.c,topTr.tr.mom.p))+" MoM).",d:"→ Sort by either "+Q_LABEL+"-attain column, or toggle WoW for the latest week. Attainment is run-rate this early."},
  {h:"SLG QoQ",b:"B2B won MRR <b>"+pct1(pop(slgWon.cur,slgWon.prior))+"</b> QoQ, tracking to <b>"+((slgWon.cur/SLG_QRR)/slgWon.tgt*100).toFixed(0)+"%</b> of the quarter target.",d:"→ See the High-Level Summary for per-segment SQL and pipeline attainment."},
  {h:"Spend efficiency",b:"MTD ROI is <b>"+(roi*100).toFixed(1)+"%</b> - "+money(totalARR)+" ARR on "+money(totalSpend)+" spend. Google is "+(SPEND.Google/totalSpend*100).toFixed(0)+"% of spend.",d:"→ Heavy Google concentration; check marginal ROAS before scaling."},
];
(function(){ if(!INTENT.length) return;   // intent card: top use case, biggest WoW share move, best signup->trial ratio (all channels)
  const items=aggRows(INTENT,IIDX).filter(o=>o.key!=="no_answer"&&o.key!=="legacy"); if(!items.length) return;
  const totM=items.reduce((a,o)=>a+o.su.mom.c,0), top=items.slice().sort((a,b)=>b.su.mom.c-a.su.mom.c)[0];
  const totW=items.reduce((a,o)=>a+o.su.wow.c,0), totPW=items.reduce((a,o)=>a+o.su.wow.p,0);
  let mover=null; if(totW&&totPW>=I_MIN_N) items.forEach(o=>{ const d=(o.su.wow.c/totW-o.su.wow.p/totPW)*100; if(!mover||Math.abs(d)>Math.abs(mover.d)) mover={o,d}; });
  const conv=items.filter(o=>o.su.mom.c>=I_MIN_SU).map(o=>({o,r:o.tr.mom.c/o.su.mom.c})).sort((a,b)=>b.r-a.r)[0];
  insights.push({h:"Onboarding intent",
    b:"Top use case MTD: <b>"+iLabel(top.key)+"</b>, "+(totM?(top.su.mom.c/totM*100).toFixed(0):0)+"% of answered signups."+
      (mover?" Biggest WoW share move: <b>"+iLabel(mover.o.key)+"</b> "+(mover.d>=0?"+":"")+mover.d.toFixed(1)+"pp.":"")+
      (conv?" Best signup → trial ratio: <b>"+iLabel(conv.o.key)+"</b> at "+(conv.r*100).toFixed(0)+"%.":""),
    d:"→ Filter the Onboarding Intent card by channel to see whether paid is buying the use cases that convert."}); })();
document.getElementById("insights").innerHTML=insights.map(i=>'<div class="insight"><h3>'+i.h+'</h3><p>'+i.b+'</p><p class="diag">'+i.d+'</p></div>').join("");
document.getElementById("footer").innerHTML="Generated "+new Date().toISOString().slice(0,10)+" · Riverside Marketing Analytics · via RiverMind /ask → Snowflake.<br>"+
  "PLG: analytics.bi.marketing_rollover (intent = metadata_purposes, plan = product_group) · SLG: analytics.bi.sales_rollover (inbound) · Spend: analytics.bi.daily_campaign_signup_attribution · Invoice-board spend lines: monday invoices board 18390740532 · Targets: targets_2026.xlsx · Manual/fallback: manual_inputs.json.<br>"+
  "Target/projection/attainment/Net-MRR math mirrors run_full_report.py. SLG & Net MRR are Snowflake-direct (not Omni semantic layer)."+
  (NOTION_URL?'<br>Registered in Notion: <a href="'+NOTION_URL+'">artifact record</a>.':"");
</script>"""


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--plan":
        import pprint
        pprint.pprint(compute_params(date.fromisoformat(sys.argv[2])))
    else:
        vp = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "report_values.json")
        outp = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "plg_daily_snapshot.html")
        with open(vp) as f:
            values = json.load(f)
        html = build(values)
        with open(outp, "w") as f:
            f.write(html)
        print(f"Wrote {outp} ({len(html)} bytes) for anchor {values['anchor_date']}")
