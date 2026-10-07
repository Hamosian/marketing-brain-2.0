#!/usr/bin/env python3
"""
Deterministic HTML builder for the seo-de-report skill.

Takes a JSON data file (already-pulled, already-combined-channel numbers per
/de/ URL for two periods) and renders the same Riverside-branded, sortable,
searchable single-page report used for the Jul-vs-Jun 2026 pilot run. This
script owns layout/styling/interactivity only - it never invents numbers.
All figures come from the input JSON, which the skill's Step 1/2 (querying
Rivermind/Omni/Snowflake) is responsible for producing.

Usage:
    python3 build_report.py <input.json> <output.html> [--csv <output.csv>]

Input JSON schema:
{
  "locale": "/de/",                         # for the header copy
  "period_a_label": "July 2026",            # the newer / "current" period
  "period_b_label": "June 2026",            # the prior / comparison period
  "period_range_note": "Jul 1-31, 2026 vs Jun 1-30, 2026",
  "source_note": "Snowflake organic funnel export",
  "generated_note": "Generated Aug 6, 2026",
  "channel_note": "<the Non-Brand/Brand-classification-bug callout copy, or '' to omit>",
  "records": [
    {"url": "/de", "current": {"visits":.., "signups":.., "subs":.., "mrr":..},
               "prior":   {"visits":.., "signups":.., "subs":.., "mrr":..}},
    ...
  ]
}

grandTotal is computed by this script (sum of records) - do not pass it in;
if the source system's own total disagrees with the sum of per-URL rows,
that mismatch is a data-quality signal, surface it in Step 2, don't paper
over it here.
"""

import argparse
import base64
import csv
import html
import json
import os
import re
import sys

FONT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "InstrumentSans-subset.woff2")


def _json_for_script(obj):
    """json.dumps, then defang </script>-breakout so URLs/labels can't end the data block early."""
    s = json.dumps(obj, separators=(",", ":"), allow_nan=False)
    return s.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def pct_and_new(cur, pri):
    if pri == 0:
        if cur == 0:
            return None, False
        return None, True  # "new" - no baseline to divide by
    return (cur - pri) / pri * 100, False


def shape(data):
    recs = data["records"]
    for r in recs:
        for m in ("visits", "signups", "subs"):
            r[m + "_delta"] = r["current"][m] - r["prior"][m]
            p, isnew = pct_and_new(r["current"][m], r["prior"][m])
            r[m + "_pct"] = p
            r[m + "_new"] = isnew
        r["mrr_delta"] = round(r["current"]["mrr"] - r["prior"]["mrr"], 2)
        p, isnew = pct_and_new(r["current"]["mrr"], r["prior"]["mrr"])
        r["mrr_pct"] = p
        r["mrr_new"] = isnew
        r["current"]["mrr"] = round(r["current"]["mrr"], 2)
        r["prior"]["mrr"] = round(r["prior"]["mrr"], 2)

    recs.sort(key=lambda r: -r["current"]["visits"])

    def total(key):
        return sum(r["current"][key] for r in recs), sum(r["prior"][key] for r in recs)

    def gt_metric(key, money=False):
        cur, pri = total(key)
        if money:
            cur, pri = round(cur, 2), round(pri, 2)
        p, isnew = pct_and_new(cur, pri)
        delta = round(cur - pri, 2) if money else cur - pri
        return {"cur": cur, "pri": pri, "delta": delta, "pct": p, "new": isnew}

    grand = {
        "visits": gt_metric("visits"),
        "signups": gt_metric("signups"),
        "subs": gt_metric("subs"),
        "mrr": gt_metric("mrr", money=True),
    }

    by_delta = sorted(recs, key=lambda r: r["visits_delta"])
    decliners = [r for r in by_delta if r["visits_delta"] < 0][:7]
    growers = sorted(
        [r for r in recs if r["visits_delta"] > 0],
        key=lambda r: -r["visits_delta"],
    )[:5]
    movers = decliners + growers
    movers_out = [
        {"url": r["url"], "delta": r["visits_delta"], "cur": r["current"]["visits"], "pri": r["prior"]["visits"]}
        for r in movers
    ]
    movers_out.sort(key=lambda m: m["delta"])

    return recs, grand, movers_out


PAGE_TEMPLATE = r"""<title>__TITLE__</title>
<style>
  @font-face {
    font-family: 'Instrument Sans';
    font-style: normal;
    font-weight: 400 700;
    font-display: swap;
    src: url(data:font/woff2;base64,__FONT_B64__) format('woff2-variations'), url(data:font/woff2;base64,__FONT_B64__) format('woff2');
  }

  :root {
    --bg: #0F0F14; --surface: #1A1A22; --surface-2: #202029; --border: #2A2A35;
    --text: #FFFFFF; --text-2: #E6E6EB; --muted: #94919f;
    --accent: #7C5CFF; --accent-hover: #8F73FF; --accent-soft: rgba(124, 92, 255, 0.14);
    --neg: #FF6B6B; --neg-soft: rgba(255, 107, 107, 0.12);
    --pos: #4ADE80; --pos-soft: rgba(74, 222, 128, 0.12);
    color-scheme: dark;
  }
  :root[data-theme="light"] {
    --bg: #FFFFFF; --surface: #FFFFFF; --surface-2: #F7F5FF; --border: #E6E6EB;
    --text: #0F0F14; --text-2: #3A3A45; --muted: #6B6876;
    --accent: #7C5CFF; --accent-hover: #6A47F5; --accent-soft: #EDE8FF;
    --neg: #D9364B; --neg-soft: #FDEBEC; --pos: #1B9C5C; --pos-soft: #E8F8EF;
    color-scheme: light;
  }
  @media (prefers-color-scheme: light) {
    :root:not([data-theme="dark"]) {
      --bg: #FFFFFF; --surface: #FFFFFF; --surface-2: #F7F5FF; --border: #E6E6EB;
      --text: #0F0F14; --text-2: #3A3A45; --muted: #6B6876;
      --accent: #7C5CFF; --accent-hover: #6A47F5; --accent-soft: #EDE8FF;
      --neg: #D9364B; --neg-soft: #FDEBEC; --pos: #1B9C5C; --pos-soft: #E8F8EF;
      color-scheme: light;
    }
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--bg); color: var(--text);
    font-family: 'Instrument Sans', -apple-system, 'Segoe UI', Arial, sans-serif;
    -webkit-font-smoothing: antialiased; overflow-x: hidden; }
  body { display: flex; justify-content: center; padding: 40px 20px 64px; }
  .page { width: 100%; max-width: 1180px; display: flex; flex-direction: column; gap: 32px; }
  .wordmark { display: inline-flex; align-items: center; gap: 8px; font-weight: 700; font-size: 15px; letter-spacing: -0.01em; }
  .wordmark .dot { color: var(--accent); }
  .eyebrow { font-size: 12px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--accent); }
  header.top { display: flex; flex-direction: column; gap: 16px; padding-bottom: 24px; border-bottom: 1px solid var(--border); }
  .top-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; flex-wrap: wrap; }
  h1 { margin: 6px 0 0; font-size: clamp(24px, 3.4vw, 34px); font-weight: 700; letter-spacing: -0.02em; text-wrap: balance; }
  .subtitle { margin: 6px 0 0; font-size: 15px; color: var(--text-2); max-width: 62ch; line-height: 1.5; }
  .meta-list { display: flex; flex-direction: column; gap: 4px; font-size: 12.5px; color: var(--muted); text-align: right; white-space: nowrap; }
  .callout { display: flex; gap: 12px; padding: 16px 18px; background: var(--surface); border: 1px solid var(--border);
    border-left: 3px solid var(--accent); border-radius: 12px; font-size: 13.5px; line-height: 1.55; color: var(--text-2); }
  .callout strong { color: var(--text); font-weight: 600; }
  .callout-icon { flex-shrink: 0; width: 20px; height: 20px; margin-top: 1px; }
  .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
  .kpi { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 18px 20px;
    display: flex; flex-direction: column; gap: 10px; }
  .kpi-label { font-size: 12.5px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }
  .kpi-value { font-size: 30px; font-weight: 700; letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }
  .kpi-compare { font-size: 12.5px; color: var(--muted); font-variant-numeric: tabular-nums; }
  .chip { display: inline-flex; align-items: center; gap: 4px; padding: 3px 9px; border-radius: 999px;
    font-size: 12.5px; font-weight: 600; font-variant-numeric: tabular-nums; width: fit-content; }
  .chip.neg { color: var(--neg); background: var(--neg-soft); }
  .chip.pos { color: var(--pos); background: var(--pos-soft); }
  .chip.flat { color: var(--muted); background: var(--surface-2); }
  .panel { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 22px 24px 20px; }
  .panel-head { display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; gap: 8px; margin-bottom: 18px; }
  .panel-title { font-size: 15px; font-weight: 600; }
  .panel-note { font-size: 12.5px; color: var(--muted); }
  .chart-legend { display: flex; gap: 16px; font-size: 12px; color: var(--muted); margin-bottom: 4px; }
  .chart-legend span { display: inline-flex; align-items: center; gap: 6px; }
  .swatch { width: 10px; height: 10px; border-radius: 3px; display: inline-block; }
  .bar-row { display: grid; grid-template-columns: 210px 1fr 64px; align-items: center; gap: 12px; padding: 6px 0; }
  .bar-url { font-size: 12.5px; color: var(--text-2); font-family: ui-monospace, 'SF Mono', Menlo, Consolas, monospace;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .bar-track { position: relative; height: 18px; background: var(--surface-2); border-radius: 4px; }
  .bar-zero { position: absolute; top: -3px; bottom: -3px; width: 1px; background: var(--border); }
  .bar-fill { position: absolute; top: 2px; bottom: 2px; border-radius: 4px; }
  .bar-fill.neg { background: var(--neg); } .bar-fill.pos { background: var(--pos); }
  .bar-delta { font-size: 12.5px; font-weight: 600; font-variant-numeric: tabular-nums; text-align: right; }
  .bar-delta.neg { color: var(--neg); } .bar-delta.pos { color: var(--pos); }
  .table-controls { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 14px; }
  .search-wrap { position: relative; width: 280px; max-width: 100%; }
  .search-wrap svg { position: absolute; left: 11px; top: 50%; transform: translateY(-50%); color: var(--muted); }
  #search { width: 100%; padding: 9px 12px 9px 34px; background: var(--surface-2); border: 1px solid var(--border);
    border-radius: 9px; color: var(--text); font-family: inherit; font-size: 13.5px; outline: none; transition: border-color 150ms ease; }
  #search::placeholder { color: var(--muted); }
  #search:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
  .result-count { font-size: 12.5px; color: var(--muted); font-variant-numeric: tabular-nums; }
  .table-scroll { overflow-x: auto; border: 1px solid var(--border); border-radius: 14px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; min-width: 760px; }
  thead th { position: sticky; top: 0; background: var(--surface-2); color: var(--muted); font-weight: 600; font-size: 11.5px;
    text-transform: uppercase; letter-spacing: 0.04em; text-align: right; padding: 11px 14px; border-bottom: 1px solid var(--border);
    cursor: pointer; user-select: none; white-space: nowrap; }
  thead th:first-child { text-align: left; }
  thead th:focus-visible { outline: 2px solid var(--accent); outline-offset: -2px; }
  thead th .arrow { margin-left: 4px; opacity: 0.5; font-size: 10px; }
  thead th.sorted { color: var(--accent); } thead th.sorted .arrow { opacity: 1; }
  tbody td { padding: 9px 14px; text-align: right; font-variant-numeric: tabular-nums; border-bottom: 1px solid var(--border); white-space: nowrap; }
  tbody td:first-child { text-align: left; font-family: ui-monospace, 'SF Mono', Menlo, Consolas, monospace; font-size: 12.5px;
    color: var(--text-2); white-space: normal; word-break: break-all; min-width: 220px; }
  tbody tr:hover td { background: var(--surface-2); }
  tbody tr:last-child td { border-bottom: none; }
  td.delta-cell.neg { color: var(--neg); } td.delta-cell.pos { color: var(--pos); } td.delta-cell.flat { color: var(--muted); }
  tfoot td { padding: 12px 14px; text-align: right; font-weight: 700; font-variant-numeric: tabular-nums; background: var(--surface-2);
    border-top: 2px solid var(--border); }
  tfoot td:first-child { text-align: left; }
  tfoot td.delta-cell.neg { color: var(--neg); } tfoot td.delta-cell.pos { color: var(--pos); }
  .empty-state { text-align: center; padding: 40px 20px; color: var(--muted); font-size: 13.5px; }
  footer { margin-top: 8px; padding-top: 20px; border-top: 1px solid var(--border); display: flex; flex-direction: column;
    gap: 10px; font-size: 12px; color: var(--muted); line-height: 1.6; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { color: var(--accent-hover); text-decoration: underline; }
  a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 2px; }
  @media (max-width: 860px) {
    .kpi-grid { grid-template-columns: repeat(2, 1fr); } .top-row { flex-direction: column; } .meta-list { text-align: left; }
    .bar-row { grid-template-columns: 120px 1fr 56px; } .bar-url { font-size: 11px; }
  }
  @media (max-width: 520px) { .kpi-grid { grid-template-columns: 1fr; } }
  @media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }
</style>

<div class="page">
  <header class="top">
    <div class="top-row">
      <div>
        <div class="wordmark">Riverside<span class="dot">.</span></div>
        <div class="eyebrow" style="margin-top:10px;">SEO &amp; AI Search &middot; Growth Marketing</div>
        <h1>__H1__</h1>
        <p class="subtitle">__SUBTITLE__</p>
      </div>
      <div class="meta-list">
        <span>Source: __SOURCE_NOTE__</span>
        <span>Period: __PERIOD_RANGE_NOTE__</span>
        <span>__GENERATED_NOTE__</span>
      </div>
    </div>
  </header>

  __CALLOUT_BLOCK__

  <div class="kpi-grid" id="kpi-grid"></div>

  <div class="panel">
    <div class="panel-head">
      <div class="panel-title">Where the visit change concentrates</div>
      <div class="panel-note">Top movers by visit change, __PERIOD_A_LABEL__ vs __PERIOD_B_LABEL__</div>
    </div>
    <div class="chart-legend">
      <span><i class="swatch" style="background:var(--neg)"></i>Fewer visits in __PERIOD_A_SHORT__</span>
      <span><i class="swatch" style="background:var(--pos)"></i>More visits in __PERIOD_A_SHORT__</span>
    </div>
    <div id="bar-chart"></div>
  </div>

  <div class="panel">
    <div class="panel-head">
      <div class="panel-title">All __URL_COUNT__ URLs</div>
      <div class="panel-note">Click a column header to sort</div>
    </div>
    <div class="table-controls">
      <div class="search-wrap">
        <svg width="14" height="14" viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="9" cy="9" r="6.5" stroke="currentColor" stroke-width="1.5"/><path d="M18 18l-4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
        <input id="search" type="text" placeholder="Filter by URL&hellip;" aria-label="Filter by URL">
      </div>
      <div class="result-count" id="result-count"></div>
    </div>
    <div class="table-scroll">
      <table id="data-table">
        <thead>
          <tr>
            <th data-key="url" data-type="str" tabindex="0" style="text-align:left">URL</th>
            <th data-key="current.visits" data-type="num" tabindex="0">Visits __PERIOD_A_SHORT__</th>
            <th data-key="visits_delta" data-type="num" tabindex="0">&Delta; vs __PERIOD_B_SHORT__</th>
            <th data-key="current.signups" data-type="num" tabindex="0">Sign-ups __PERIOD_A_SHORT__</th>
            <th data-key="signups_delta" data-type="num" tabindex="0">&Delta; vs __PERIOD_B_SHORT__</th>
            <th data-key="current.subs" data-type="num" tabindex="0">Subs __PERIOD_A_SHORT__</th>
            <th data-key="subs_delta" data-type="num" tabindex="0">&Delta; vs __PERIOD_B_SHORT__</th>
            <th data-key="current.mrr" data-type="num" tabindex="0">First MRR __PERIOD_A_SHORT__</th>
            <th data-key="mrr_delta" data-type="num" tabindex="0">&Delta; vs __PERIOD_B_SHORT__</th>
          </tr>
        </thead>
        <tbody id="table-body"></tbody>
        <tfoot id="table-foot"></tfoot>
      </table>
    </div>
  </div>

  <footer>
    <div>__FOOTER_NOTE__</div>
    <div style="padding-top:10px;border-top:1px solid var(--border);">This report was compiled with AI assistance (Claude, Riverside Marketing OS) from __SOURCE_NOTE__. Figures reflect the source data as of the generation date above; verify before using in an external or board-level context. &mdash; <em>Diligence, not disclaimer.</em></div>
  </footer>
</div>

<script id="records-data" type="application/json">__RECORDS_JSON__</script>
<script id="grand-data" type="application/json">__GRAND_JSON__</script>
<script id="movers-data" type="application/json">__MOVERS_JSON__</script>

<script>
(function () {
  const records = JSON.parse(document.getElementById('records-data').textContent);
  const grand = JSON.parse(document.getElementById('grand-data').textContent);
  const movers = JSON.parse(document.getElementById('movers-data').textContent);

  const ESC_MAP = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'};
  function esc(s) { return String(s).replace(/[&<>"']/g, c => ESC_MAP[c]); }

  const fmtInt = n => n.toLocaleString('en-US');
  const fmtMoney = n => '$' + n.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0});
  const fmtMoneyPrecise = n => '$' + n.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});

  function chip(delta, pct, isNew) {
    const cls = delta > 0 ? 'pos' : (delta < 0 ? 'neg' : 'flat');
    const arrow = delta > 0 ? '&#9650;' : (delta < 0 ? '&#9660;' : '&#8212;');
    let pctStr;
    if (isNew) pctStr = 'new';
    else if (pct === null) pctStr = '&mdash;';
    else pctStr = (pct > 0 ? '+' : '') + pct.toFixed(0) + '%';
    return '<span class="chip ' + cls + '">' + arrow + ' ' + pctStr + '</span>';
  }

  const kpiDefs = [
    {key: 'visits', label: 'Visits', fmt: fmtInt},
    {key: 'signups', label: 'Sign-ups', fmt: fmtInt},
    {key: 'subs', label: 'Subscriptions', fmt: fmtInt},
    {key: 'mrr', label: 'First MRR', fmt: fmtMoney},
  ];
  const kpiGrid = document.getElementById('kpi-grid');
  kpiGrid.innerHTML = kpiDefs.map(d => {
    const g = grand[d.key];
    return '<div class="kpi">' +
      '<div class="kpi-label">' + d.label + '</div>' +
      '<div class="kpi-value">' + d.fmt(g.cur) + '</div>' +
      '<div class="kpi-compare">vs ' + d.fmt(g.pri) + ' in __PERIOD_B_SHORT__</div>' +
      chip(g.delta, g.pct, g.new) +
      '</div>';
  }).join('');

  const maxAbs = Math.max(1, ...movers.map(m => Math.abs(m.delta)));
  const barChart = document.getElementById('bar-chart');
  barChart.innerHTML = movers.map(m => {
    const isNeg = m.delta < 0;
    const widthPct = (Math.abs(m.delta) / maxAbs) * 50;
    const left = isNeg ? (50 - widthPct) : 50;
    const sign = isNeg ? '' : '+';
    return '<div class="bar-row">' +
      '<div class="bar-url" title="' + esc(m.url) + '">' + esc(m.url) + '</div>' +
      '<div class="bar-track"><div class="bar-zero" style="left:50%"></div>' +
        '<div class="bar-fill ' + (isNeg ? 'neg' : 'pos') + '" style="left:' + left + '%;width:' + widthPct + '%"></div>' +
      '</div>' +
      '<div class="bar-delta ' + (isNeg ? 'neg' : 'pos') + '">' + sign + m.delta + '</div>' +
    '</div>';
  }).join('');

  function get(obj, path) { return path.split('.').reduce((o, k) => (o == null ? o : o[k]), obj); }

  function deltaCell(delta, pct, money, isNew) {
    const cls = delta > 0 ? 'pos' : (delta < 0 ? 'neg' : 'flat');
    const arrow = delta > 0 ? '&#9650;' : (delta < 0 ? '&#9660;' : '&#8212;');
    const val = money ? fmtMoneyPrecise(delta) : fmtInt(delta);
    let pctStr = '';
    if (isNew) pctStr = ' (new)';
    else if (pct !== null) pctStr = ' (' + (pct > 0 ? '+' : '') + pct.toFixed(0) + '%)';
    return '<td class="delta-cell ' + cls + '">' + arrow + ' ' + val + pctStr + '</td>';
  }

  function renderRows(rows) {
    const tbody = document.getElementById('table-body');
    if (rows.length === 0) {
      tbody.innerHTML = '<tr><td colspan="9"><div class="empty-state">No URLs match that filter.</div></td></tr>';
      return;
    }
    tbody.innerHTML = rows.map(r => (
      '<tr>' +
      '<td>' + esc(r.url) + '</td>' +
      '<td title="__PERIOD_B_SHORT__: ' + fmtInt(r.prior.visits) + '">' + fmtInt(r.current.visits) + '</td>' +
      deltaCell(r.visits_delta, r.visits_pct, false, r.visits_new) +
      '<td title="__PERIOD_B_SHORT__: ' + fmtInt(r.prior.signups) + '">' + fmtInt(r.current.signups) + '</td>' +
      deltaCell(r.signups_delta, r.signups_pct, false, r.signups_new) +
      '<td title="__PERIOD_B_SHORT__: ' + fmtInt(r.prior.subs) + '">' + fmtInt(r.current.subs) + '</td>' +
      deltaCell(r.subs_delta, r.subs_pct, false, r.subs_new) +
      '<td title="__PERIOD_B_SHORT__: ' + fmtMoneyPrecise(r.prior.mrr) + '">' + fmtMoneyPrecise(r.current.mrr) + '</td>' +
      deltaCell(r.mrr_delta, r.mrr_pct, true, r.mrr_new) +
      '</tr>'
    )).join('');
  }

  function renderFoot() {
    const tfoot = document.getElementById('table-foot');
    tfoot.innerHTML = '<tr>' +
      '<td>All __URL_COUNT__ URLs (total)</td>' +
      '<td title="__PERIOD_B_SHORT__: ' + fmtInt(grand.visits.pri) + '">' + fmtInt(grand.visits.cur) + '</td>' +
      deltaCell(grand.visits.delta, grand.visits.pct, false, grand.visits.new) +
      '<td title="__PERIOD_B_SHORT__: ' + fmtInt(grand.signups.pri) + '">' + fmtInt(grand.signups.cur) + '</td>' +
      deltaCell(grand.signups.delta, grand.signups.pct, false, grand.signups.new) +
      '<td title="__PERIOD_B_SHORT__: ' + fmtInt(grand.subs.pri) + '">' + fmtInt(grand.subs.cur) + '</td>' +
      deltaCell(grand.subs.delta, grand.subs.pct, false, grand.subs.new) +
      '<td title="__PERIOD_B_SHORT__: ' + fmtMoneyPrecise(grand.mrr.pri) + '">' + fmtMoneyPrecise(grand.mrr.cur) + '</td>' +
      deltaCell(grand.mrr.delta, grand.mrr.pct, true, grand.mrr.new) +
      '</tr>';
  }

  let sortKey = 'current.visits';
  let sortDir = -1;
  let query = '';

  function applyAndRender() {
    let rows = records;
    if (query) {
      const q = query.toLowerCase();
      rows = rows.filter(r => r.url.toLowerCase().includes(q));
    }
    rows = rows.slice().sort((a, b) => {
      const av = get(a, sortKey), bv = get(b, sortKey);
      if (typeof av === 'string') return sortDir * av.localeCompare(bv);
      return sortDir * ((av ?? -Infinity) - (bv ?? -Infinity));
    });
    renderRows(rows);
    document.getElementById('result-count').textContent = rows.length + ' of ' + records.length + ' URLs';
  }

  document.querySelectorAll('thead th').forEach(th => {
    function activate() {
      const key = th.getAttribute('data-key');
      if (sortKey === key) sortDir *= -1;
      else { sortKey = key; sortDir = th.getAttribute('data-type') === 'str' ? 1 : -1; }
      document.querySelectorAll('thead th').forEach(t => t.classList.remove('sorted'));
      th.classList.add('sorted');
      th.querySelector('.arrow')?.remove();
      const arrow = document.createElement('span');
      arrow.className = 'arrow';
      arrow.textContent = sortDir === 1 ? '▲' : '▼';
      th.appendChild(arrow);
      applyAndRender();
    }
    th.addEventListener('click', activate);
    th.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); activate(); } });
  });

  document.getElementById('search').addEventListener('input', e => { query = e.target.value; applyAndRender(); });

  renderFoot();
  applyAndRender();
})();
</script>
"""


def render(data):
    recs, grand, movers = shape(data)
    # Build every default from raw (unescaped) input, then escape each field
    # exactly once at the end -- escaping a default composed from
    # already-escaped fields would double-escape it. Only channel_note is a
    # documented raw-HTML exception (see its own comment below).
    raw_locale = data.get("locale", "/de/")
    raw_period_a = data["period_a_label"]
    raw_period_b = data["period_b_label"]
    raw_period_a_short = data.get("period_a_short", raw_period_a)
    raw_period_b_short = data.get("period_b_short", raw_period_b)
    raw_source_note = data.get("source_note", "Snowflake organic funnel export")
    raw_period_range_note = data.get("period_range_note", f"{raw_period_a} vs {raw_period_b}")
    raw_generated_note = data.get("generated_note", "")
    raw_footer_note = data.get("footer_note") or (
        f"All {raw_locale} URLs with organic search visits in {raw_period_a} or {raw_period_b}, "
        f"{len(recs)} total. Figures are visits, sign-ups, paid subscriptions, and first-month MRR "
        f"attributed to organic search sessions on that URL. Source: {raw_source_note}."
    )

    locale = html.escape(raw_locale)
    period_a = html.escape(raw_period_a)
    period_b = html.escape(raw_period_b)
    period_a_short = html.escape(raw_period_a_short)
    period_b_short = html.escape(raw_period_b_short)
    source_note = html.escape(raw_source_note)
    period_range_note = html.escape(raw_period_range_note)
    generated_note = html.escape(raw_generated_note)
    footer_note = html.escape(raw_footer_note)

    with open(FONT_PATH, "rb") as fh:
        font_b64 = base64.b64encode(fh.read()).decode("ascii")

    default_channel_note = (
        '<div class="callout">'
        '<svg class="callout-icon" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
        '<circle cx="10" cy="10" r="8.5" stroke="currentColor" stroke-width="1.4" style="color:var(--accent)"/>'
        '<path d="M10 9v4.2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" style="color:var(--accent)"/>'
        '<circle cx="10" cy="6.6" r="0.9" fill="currentColor" style="color:var(--accent)"/></svg>'
        '<div><strong>Why one channel, not Non-Brand / Brand split:</strong> the Non-Brand vs. Brand '
        'classification is unreliable for localized pages, so splitting it out here would misstate the mix. '
        'This view reports organic search (Non-Brand + Brand + LLM) as one combined channel per URL. '
        'Flagged for the Data Team as a classification bug to fix at the source.</div></div>'
    )
    channel_note = data.get("channel_note", default_channel_note)
    callout_block = channel_note if channel_note else ""

    subs = {
        "__TITLE__": f"{locale} Organic Search: {period_a_short} vs {period_b_short}",
        "__H1__": f"{locale.strip('/').upper() if locale.strip('/') else locale} organic search: {period_a} vs {period_b}",
        "__SUBTITLE__": (
            f"All {len(recs)} <code>{locale}</code> URLs that received organic search traffic, compared "
            f"{period_a} vs {period_b}. Non-Brand, Brand, and LLM referral traffic are reported as a single "
            f"combined channel here."
        ),
        "__SOURCE_NOTE__": source_note,
        "__PERIOD_RANGE_NOTE__": period_range_note,
        "__GENERATED_NOTE__": generated_note,
        "__CALLOUT_BLOCK__": callout_block,
        "__PERIOD_A_LABEL__": period_a,
        "__PERIOD_B_LABEL__": period_b,
        "__PERIOD_A_SHORT__": period_a_short,
        "__PERIOD_B_SHORT__": period_b_short,
        "__URL_COUNT__": str(len(recs)),
        "__FOOTER_NOTE__": footer_note,
        "__RECORDS_JSON__": _json_for_script(recs),
        "__GRAND_JSON__": _json_for_script(grand),
        "__MOVERS_JSON__": _json_for_script(movers),
        "__FONT_B64__": font_b64,
    }
    # Single-pass substitution against the original template -- sequential
    # .replace() calls would let marker-shaped text inside one substituted
    # value (e.g. a URL that literally contains "__GRAND_JSON__") get
    # corrupted by a later replacement.
    marker_re = re.compile("|".join(re.escape(k) for k in subs))
    page_html = marker_re.sub(lambda m: subs[m.group(0)], PAGE_TEMPLATE)
    return page_html, recs, grand


def write_csv(recs, grand, path, period_a_short, period_b_short):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "URL",
            f"Visits ({period_a_short})", f"Visits ({period_b_short})", "Visits Δ", "Visits Δ%",
            f"Sign-ups ({period_a_short})", f"Sign-ups ({period_b_short})", "Sign-ups Δ", "Sign-ups Δ%",
            f"Subscriptions ({period_a_short})", f"Subscriptions ({period_b_short})", "Subscriptions Δ", "Subscriptions Δ%",
            f"First MRR $ ({period_a_short})", f"First MRR $ ({period_b_short})", "First MRR Δ", "First MRR Δ%",
        ])

        def pctstr(p, isnew):
            if isnew:
                return "new"
            if p is None:
                return ""
            return f"{p:+.1f}%"

        for r in recs:
            row = [r["url"]]
            for m in ("visits", "signups", "subs"):
                row += [r["current"][m], r["prior"][m], r[m + "_delta"], pctstr(r[m + "_pct"], r[m + "_new"])]
            row += [r["current"]["mrr"], r["prior"]["mrr"], r["mrr_delta"], pctstr(r["mrr_pct"], r["mrr_new"])]
            w.writerow(row)

        row = ["ALL URLs TOTAL"]
        for m in ("visits", "signups", "subs"):
            g = grand[m]
            row += [g["cur"], g["pri"], g["delta"], pctstr(g["pct"], g["new"])]
        g = grand["mrr"]
        row += [g["cur"], g["pri"], g["delta"], pctstr(g["pct"], g["new"])]
        w.writerow(row)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_json")
    ap.add_argument("output_html")
    ap.add_argument("--csv", dest="csv_path", default=None)
    args = ap.parse_args()

    with open(args.input_json) as f:
        data = json.load(f)

    page_html, recs, grand = render(data)
    with open(args.output_html, "w") as f:
        f.write(page_html)
    print(f"wrote {args.output_html} ({len(page_html)} bytes, {len(recs)} URLs)")

    if args.csv_path:
        write_csv(recs, grand, args.csv_path, data.get("period_a_short", data["period_a_label"]), data.get("period_b_short", data["period_b_label"]))
        print(f"wrote {args.csv_path}")


if __name__ == "__main__":
    main()
