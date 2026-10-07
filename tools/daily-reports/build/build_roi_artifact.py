#!/usr/bin/env python3
"""
Build the Riverside ROI & Growth daily artifact (v2 layout) from a small JSON of
query results. Reuses compute_params() from build_artifact.py for all the
date-dependent math (run-rates, windows, SLG targets).

Layout vs the original daily report:
  1. High-Level Summary, split into:
       - PLG: Current (MTD) + MoM + WoW (both pro-rated by elapsed window),
              rows Signups / Trials / First MRR / New Subscribers / Net MRR,
              plus a New-Subscribers breakdown (billing period + plan type).
       - SLG: unchanged (Target / Current / Projected / Attainment / QoQ).
  2. (PLG Channel Detail removed.)
  3. ROI Snapshot, split into:
       - July MTD: SLG ARR = (B2B-MRR target x12 /3) x monthly-RR; spend = actual
                   PPC (MTD) + SEO/Partnerships/Growth monthly budgets x monthly-RR.
       - Trailing 30 days: SLG ARR = full monthly (B2B-MRR target x12 /3); spend =
                   actual PPC (30d) + full SEO/Partnerships/Growth monthly budgets.
  4. (Key Insights removed.)
  5. Invoice-board actuals (added 2026-10-04): the anchor month's invoices from the Invoices and
     Payments board, split into Creative partnerships / Affiliates / Affiliate freelancers &
     platforms / B2B vendors / Growth Channels other. Optional values["invoice_spend"] is
     spend_actuals.py's JSON output pasted verbatim. Reporting only: never priced into the ROI
     above, which stays on fixed budgets so it remains a comparable series.

Usage:
  python3 build_roi_artifact.py                       # reads ./roi_report_values.json
  python3 build_roi_artifact.py values.json out.html
"""
import json, sys, os
from datetime import date, timedelta
from build_artifact import compute_params, MONTH_NAME, SHORT_MONTH


def compute_roi_params(anchor):
    """All date windows + targets the ROI refresh needs, on top of compute_params."""
    p = compute_params(anchor)                                  # week windows now live in compute_params
    roll_start = anchor - timedelta(days=29)                    # trailing 30 days, inclusive
    return {
        **p,
        "rollover_window":  [roll_start.isoformat(), anchor.isoformat()],
        "slg_b2b_target":   p["slg_tgt"]["B2B MRR"],
        "slg_arr_monthly":  p["slg_tgt"]["B2B MRR"] * 12 / 3,
    }


def build(values):
    anchor = date.fromisoformat(values["anchor_date"])
    p = compute_params(anchor)
    mrr = p["mrr"]                       # fraction of month elapsed
    slg_b2b_tgt = p["slg_tgt"]["B2B MRR"]
    # SLG ARR normally derives from the B2B-MRR target; an optional values["slg_arr_monthly"]
    # override lets a one-off run supply an actual monthly SLG ARR instead (daily flow omits it).
    slg_arr_is_actual = "slg_arr_monthly" in values
    slg_arr_monthly = values.get("slg_arr_monthly", slg_b2b_tgt * 12 / 3)   # quarterly MRR target -> monthly annualized ARR

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

    rw = values["rollover_window"]
    rw_label = f"{SHORT_MONTH[int(rw[0][5:7])]} {int(rw[0][8:10])} - {SHORT_MONTH[int(rw[1][5:7])]} {int(rw[1][8:10])}"

    data = {
        "ANCHOR": f"{p['month_name']} {anchor.day}, {anchor.year}",
        "MONTH_LABEL": p["month_name"] + f" {anchor.year}",
        "SHORT_THROUGH": f"{p['short']} {anchor.day}",
        "MRR": mrr, "QRR": p["qrr"],
        "SLG_ARR_MONTHLY": slg_arr_monthly,
        "SLG_ARR_IS_ACTUAL": slg_arr_is_actual,
        "SLG_B2B_TGT": slg_b2b_tgt,
        "PLG_HL": values["plg_hl"],
        "SUBS": values["subs_breakdown"],
        "SLG": [{"name": n, "tgt": t, "cur": c, "prior": pr, "money": m} for (n, t, c, pr, m) in slg_rows],
        "SLG_Q_LABEL": p["cur_q_label"],
        "SPEND_MTD": values["spend_mtd"],
        "SPEND_30D": values["spend_30d"],
        "PLG_30D": values["plg_30d"],
        "BUDGETS": values["budgets_monthly"],
        "ROLLOVER_LABEL": rw_label,
        "NOTION_URL": values.get("notion_url", ""),
        "INVOICE": invoice_card(values.get("invoice_spend")),
    }
    # Escape "<" so board-provided text (item names) can never close the inline <script>.
    return TEMPLATE.replace("__DATA_JSON__", json.dumps(data).replace("<", "\\u003c"))


# spend_actuals.py output key, its item_counts bucket, and the card label, in render order.
INVOICE_LINES = [("creative_partnerships_spend", "creative", "Creative partnerships"),
                 ("affiliates_spend", "affiliates", "Affiliates"),
                 ("affiliate_freelancers_spend", "affiliate_freelance", "Affiliate freelancers & platforms"),
                 ("b2b_vendors_spend", "b2b", "B2B vendors"),
                 ("growth_channels_spend", "growth", "Other Growth Channels")]


def invoice_card(inv):
    """The Invoice-board actuals card's data, or None (the card then says why it is empty).
    Lines missing from an older spend_actuals.py output are left out, never shown as $0."""
    if not inv or inv.get("reconcile") != "OK":
        return None
    # item_counts holds only invoices with an amount; add the blank-amount ones so a line with an
    # invoice still awaiting its amount does not read "0 invoices".
    counts = dict(inv.get("item_counts") or {})
    for b in inv.get("blank_amounts") or []:
        if b.get("bucket") in counts:
            counts[b["bucket"]] += 1
    # Output from before the 2026-10-04 Type split groups by payer only, so affiliate invoices sit
    # inside Creative partnerships and Growth Channels is the whole channel. Label it that way.
    split = all(inv.get(k) is not None for k in ("affiliates_spend", "affiliate_freelancers_spend"))
    legacy_labels = {"creative": "Creative partnerships (by payer)", "growth": "Growth Channels"}
    lines = [{"label": label if split else legacy_labels.get(bucket, label),
              "v": inv[key], "n": counts.get(bucket)}
             for key, bucket, label in INVOICE_LINES if inv.get(key) is not None]
    return {"month_title": inv.get("month_title"), "lines": lines, "split": split,
            "total": round(sum(l["v"] for l in lines), 2),
            "blank_n": len(inv.get("blank_amounts") or []),
            "flagged": [f.get("name") for f in (inv.get("flagged") or [])]}


TEMPLATE = r"""<title>Riverside Daily Report</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  :root{
    --bg:#0F0F14; --card:#1C1C24; --line:#2A2A35; --line-soft:rgba(42,42,53,.5);
    --ink:#FFFFFF; --muted:#EDEDF2; --dim:#BDBDC9; --faint:#8B8B98;
    --accent:#9B80FF; --accent-soft:rgba(124,92,255,.10);
    --great:#00C875; --ok:#579BFC; --attention:#FDAB3D; --critical:#FF3B30;
  }
  body{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
    background:var(--bg); color:var(--ink); min-height:100vh; line-height:1.45; -webkit-font-smoothing:antialiased;}
  .container{max-width:1160px;margin:0 auto;padding:32px 24px 48px}
  .header{display:flex;justify-content:space-between;align-items:flex-start;gap:24px;
    border-bottom:1px solid var(--line);padding-bottom:20px;margin-bottom:26px;flex-wrap:wrap}
  .header h1{font-size:22px;font-weight:700;letter-spacing:-.02em}
  .header h1 span{color:var(--accent)}
  .header .date{font-size:14px;color:var(--muted);margin-top:6px}
  .header .meta{text-align:right;font-size:13px;color:var(--dim);line-height:1.75}
  .header .meta b{color:var(--muted);font-weight:600}
  .section-title{font-size:13px;font-weight:600;color:var(--accent);margin-bottom:12px;text-transform:uppercase;letter-spacing:.06em}
  .sub-title{font-size:13px;font-weight:700;color:var(--ink);margin:22px 0 10px;text-transform:uppercase;letter-spacing:.05em;display:flex;align-items:center;gap:8px}
  .sub-title:first-of-type{margin-top:6px}
  .sub-title .tag{font-size:11px;font-weight:600;color:var(--dim);background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:2px 8px;text-transform:none;letter-spacing:0}
  .card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:22px 24px;margin-bottom:22px}
  .tbl-wrap{overflow-x:auto}
  table{width:100%;border-collapse:collapse;font-size:14px}
  th{background:var(--bg);color:var(--dim);font-weight:600;font-size:12px;text-transform:uppercase;
    letter-spacing:.04em;padding:10px 11px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap}
  th:first-child{text-align:left}
  td{padding:9px 11px;text-align:right;border-bottom:1px solid var(--line-soft);font-variant-numeric:tabular-nums}
  td:first-child{text-align:left;font-weight:500;color:var(--ink)}
  tbody tr:hover{background:var(--accent-soft)}
  .total td{font-weight:700;border-top:2px solid var(--accent);background:var(--accent-soft);color:var(--ink)}
  .muted-note{font-size:12.5px;color:var(--dim);margin-top:12px;line-height:1.65}
  .pos{color:var(--great)} .neg{color:var(--critical)} .flat{color:var(--dim)}
  .pill{display:inline-block;padding:2px 9px;border-radius:9999px;font-size:11px;font-weight:600;color:#0b0b10;white-space:nowrap}
  .pill.great{background:var(--great)} .pill.ok{background:var(--ok);color:#fff}
  .pill.attention{background:var(--attention)} .pill.critical{background:var(--critical);color:#fff}
  .na{color:var(--faint)}
  .break{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px}
  .break-box{background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:16px 18px}
  .break-box .bh{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--dim);font-weight:600;margin-bottom:8px}
  .break-row{display:grid;grid-template-columns:1fr repeat(4,minmax(46px,auto));gap:9px;align-items:baseline;padding:6px 0;font-size:13.5px;border-bottom:1px solid var(--line-soft)}
  .break-row:last-child{border-bottom:none}
  .break-row.head{font-size:10px;color:var(--faint);text-transform:uppercase;letter-spacing:.02em;font-weight:600;padding-bottom:5px;line-height:1.25}
  .break-row .lbl{color:var(--ink);font-weight:500}
  .break-row .c{text-align:right;font-variant-numeric:tabular-nums}
  .break-row .c.amt{font-weight:600}
  .snap-kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:2px 0 16px}
  .snap-kpi{background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:16px 17px;border-top:3px solid var(--accent)}
  .snap-kpi.roi-great{border-top-color:var(--great)}
  .snap-kpi.roi-attention{border-top-color:var(--attention)}
  .snap-kpi.roi-critical{border-top-color:var(--critical)}
  .snap-kpi .label{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--dim);font-weight:600}
  .snap-kpi .big{font-size:22px;font-weight:700;letter-spacing:-.02em;margin-top:5px;font-variant-numeric:tabular-nums}
  .snap-kpi.roi-great .big{color:var(--great)}
  .snap-kpi.roi-attention .big{color:var(--attention)}
  .snap-kpi.roi-critical .big{color:var(--critical)}
  .snap-kpi .sub{font-size:12px;color:var(--dim);margin-top:5px;line-height:1.5}
  .snap-kpi .sub b{color:var(--muted)}
  .snap-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
  .spend-cell{background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:11px 13px}
  .spend-cell.calc{border-style:dashed;border-color:var(--accent)}
  .spend-cell .k{font-size:12px;color:var(--dim);text-transform:uppercase;letter-spacing:.03em}
  .spend-cell .v{font-size:16px;font-weight:600;margin-top:3px;font-variant-numeric:tabular-nums}
  .spend-cell .n{font-size:11px;color:var(--faint);margin-top:2px}
  .spend-lbl{font-size:12px;color:var(--dim);text-transform:uppercase;letter-spacing:.04em;margin:4px 0 8px}
  .footer{font-size:12px;color:var(--faint);line-height:1.7;border-top:1px solid var(--line);padding-top:18px}
  .footer a{color:var(--accent);text-decoration:none}
  .footer a:hover{text-decoration:underline}
  @media (max-width:760px){
    .snap-kpis{grid-template-columns:repeat(2,1fr)}
    .snap-grid{grid-template-columns:1fr 1fr}
    .break{grid-template-columns:1fr}
    .header .meta{text-align:left}
  }
</style>
<div class="container">
  <header class="header">
    <div><h1><span>Riverside</span> Daily Report</h1><div class="date" id="hdr-date"></div></div>
    <div class="meta" id="hdr-meta"></div>
  </header>

  <div class="card">
    <div class="section-title">High-Level Summary</div>

    <div class="sub-title">PLG - Product-Led Growth <span class="tag">MTD · MoM & WoW pro-rated</span></div>
    <div class="tbl-wrap"><table><thead><tr>
      <th>Metric</th><th>Current (MTD)</th><th>MoM</th><th>WoW</th>
    </tr></thead><tbody id="plg-body"></tbody></table></div>

    <div class="break">
      <div class="break-box"><div class="bh">New Subscribers - by billing period</div><div id="brk-billing"></div></div>
      <div class="break-box"><div class="bh">New Subscribers - by plan</div><div id="brk-plan"></div></div>
    </div>

    <div class="sub-title" style="margin-top:26px">SLG - Sales-Led Growth <span class="tag" id="slg-tag"></span></div>
    <div class="tbl-wrap"><table><thead><tr>
      <th>Metric</th><th>Target</th><th>Current</th><th>Projected</th><th>Attainment</th><th>QoQ</th>
    </tr></thead><tbody id="slg-body"></tbody></table></div>
    <div class="muted-note" id="hl-note"></div>
  </div>

  <div class="card">
    <div class="section-title">ROI Snapshot</div>

    <div class="sub-title" id="mtd-title"></div>
    <div class="snap-kpis" id="mtd-kpis"></div>
    <div class="spend-lbl">Spend detail</div>
    <div class="snap-grid" id="mtd-spend"></div>

    <div class="sub-title" id="roll-title" style="margin-top:28px"></div>
    <div class="snap-kpis" id="roll-kpis"></div>
    <div class="spend-lbl">Spend detail</div>
    <div class="snap-grid" id="roll-spend"></div>

    <div class="muted-note" id="snap-note"></div>
  </div>

  <div class="card">
    <div class="section-title" id="inv-title">Invoice-board actuals</div>
    <div class="snap-grid" id="inv-spend"></div>
    <div class="muted-note" id="inv-note"></div>
  </div>

  <div class="footer" id="footer"></div>
</div>
<script>
const DATA = __DATA_JSON__;
const MRR=DATA.MRR, QRR=DATA.QRR;
const nf=n=>Math.round(n).toLocaleString("en-US");
const money=n=>"$"+Math.round(n).toLocaleString("en-US");
const pct1=n=>(n>=0?"+":"")+(n*100).toFixed(1)+"%";
const pop=(c,p)=>p?(c-p)/p:null;
const popCell=m=>{ if(m===null) return '<span class="na">-</span>';
  const c=Math.abs(m)<0.005?"flat":(m>0?"pos":"neg"); const a=Math.abs(m)<0.005?"→ ":(m>0?"↑ ":"↓ ");
  return '<span class="'+c+'">'+a+pct1(m)+'</span>'; };
const ppCell=d=>{ const c=Math.abs(d)<0.05?"flat":(d>0?"pos":"neg"); const a=Math.abs(d)<0.05?"→ ":(d>0?"↑ ":"↓ ");
  return '<span class="'+c+'">'+a+(d>=0?"+":"")+d.toFixed(1)+"pp</span>"; };
function attBadge(a){ if(a===null) return '<span class="na">-</span>';
  let c=a>=1.0?"great":a>=0.75?"ok":a>=0.50?"attention":"critical";
  return '<span class="pill '+c+'">'+(a*100).toFixed(1)+'%</span>'; }

document.getElementById("hdr-date").textContent="Latest complete day: "+DATA.ANCHOR+"  ·  "+DATA.MONTH_LABEL+" MTD through "+DATA.SHORT_THROUGH;
document.getElementById("hdr-meta").innerHTML=
  "Monthly RR: <b>"+(MRR*100).toFixed(1)+"%</b> · Quarterly RR: <b>"+(QRR*100).toFixed(1)+"%</b><br>"+
  "SLG monthly ARR basis: <b>"+money(DATA.SLG_ARR_MONTHLY)+"</b>";

// ---- PLG high-level: Current (MTD) + MoM + WoW ----
const PLG=DATA.PLG_HL;
const plgRows=[
  ["Signups","signups",false],["Trials","trials",false],["First MRR","first_mrr",true],
  ["New Subscribers","new_subs",false],["Net MRR","net_mrr",true],
];
document.getElementById("plg-body").innerHTML=plgRows.map(([label,key,isMoney])=>{
  const o=PLG[key], fmt=isMoney?money:nf;
  const mom=pop(o.cur_m,o.prev_m), wow=pop(o.cur_w,o.prev_w);
  return '<tr><td>'+label+'</td><td>'+fmt(o.cur_m)+'</td><td>'+popCell(mom)+'</td><td>'+popCell(wow)+'</td></tr>';
}).join("");

// ---- New-subscribers breakdown: Subs · % of total · MoM subs · MoM % of total ----
function brk(list){ const cur=list.reduce((a,[,v])=>a+v,0), prev=list.reduce((a,[,,pv])=>a+pv,0);
  const head='<div class="break-row head"><span class="lbl">Segment</span><span class="c">Subs</span>'+
    '<span class="c">% of<br>total</span><span class="c">MoM<br>subs</span><span class="c">MoM<br>% total</span></div>';
  return head+list.map(([k,v,pv])=>{
    const shC=cur?v/cur*100:0, shP=prev?pv/prev*100:0;
    return '<div class="break-row"><span class="lbl">'+k+'</span>'+
      '<span class="c amt">'+nf(v)+'</span>'+
      '<span class="c amt">'+shC.toFixed(1)+'%</span>'+
      '<span class="c">'+popCell(pop(v,pv))+'</span>'+
      '<span class="c">'+ppCell(shC-shP)+'</span></div>';
  }).join(""); }
document.getElementById("brk-billing").innerHTML=brk(DATA.SUBS.billing);
document.getElementById("brk-plan").innerHTML=brk(DATA.SUBS.plan);

// ---- SLG: unchanged Target / Current / Projected / Attainment / QoQ ----
const SLG=DATA.SLG, qlbl=DATA.SLG_Q_LABEL.replace("-"," ");
document.getElementById("slg-tag").textContent=qlbl+" QTD · QoQ · Inbound";
document.getElementById("slg-body").innerHTML=SLG.map(s=>{
  const fmt=s.money?money:nf, proj=s.cur/QRR, att=s.tgt?proj/s.tgt:null;
  return '<tr><td>'+s.name+'</td><td>'+(s.tgt?fmt(s.tgt):'<span class="na">-</span>')+'</td><td>'+fmt(s.cur)+
    '</td><td>'+fmt(proj)+'</td><td>'+attBadge(att)+'</td><td>'+popCell(pop(s.cur,s.prior))+'</td></tr>';
}).join("");
document.getElementById("hl-note").innerHTML=
  "PLG - <b>MoM</b> compares "+DATA.MONTH_LABEL+" MTD to the same day-window of the prior month; "+
  "<b>WoW</b> compares the latest complete week to the prior complete week (both pro-rated by elapsed window). "+
  "New-subscriber breakdown uses the same MTD window through "+DATA.SHORT_THROUGH+" (data through yesterday) vs the same days last month; "+
  "<b>MoM subs</b> is the count change vs the same days last month; <b>MoM % total</b> is the change in that segment's share of total, in percentage points. &nbsp; SLG - "+qlbl+" to date vs prior quarter same fiscal day; "+
  "projected = current ÷ quarterly run-rate. Inbound SQLs only.";

// ---- ROI Snapshot ----
const BUD=DATA.BUDGETS, SLG_ARR_M=DATA.SLG_ARR_MONTHLY, SLG_ARR_ACTUAL=DATA.SLG_ARR_IS_ACTUAL;
const budTotal=Object.values(BUD).reduce((a,b)=>a+b,0);
// ROI vs 300% target: <250 red, 250-299 yellow, >=300 green
function roiClass(roiPct){ return roiPct>=300?"roi-great":roiPct>=250?"roi-attention":"roi-critical"; }
function roiKpis(elId,spend,plgArr,slgArr,plgSub,spendSub){
  const totalARR=plgArr+slgArr, roi=(totalARR-spend)/spend, roiPct=roi*100;
  document.getElementById(elId).innerHTML=[
    {l:"Total Spend",v:money(spend),s:spendSub},
    {l:"PLG ARR",v:money(plgArr),s:plgSub},
    {l:"SLG ARR",v:money(slgArr),s:SLG_ARR_ACTUAL?"actual monthly SLG ARR (input)":("B2B-MRR target ×12 ÷3"+(elId==="mtd-kpis"?" × RR":""))},
    {l:"Total ARR",v:money(totalARR),s:"PLG + SLG"},
    {l:"ROI",v:roiPct.toFixed(1)+"%",s:"(ARR − Spend) ÷ Spend · target 300%",cls:roiClass(roiPct)},
  ].map(k=>'<div class="snap-kpi'+(k.cls?" "+k.cls:"")+'"><div class="label">'+k.l+'</div><div class="big">'+k.v+'</div><div class="sub">'+k.s+'</div></div>').join("");
}
function spendGrid(elId,ppc,budgets,budgetNote){
  let cells=Object.entries(ppc).map(([k,v])=>'<div class="spend-cell"><div class="k">'+k+'</div><div class="v">'+money(v)+'</div><div class="n">PPC · actual</div></div>');
  cells=cells.concat(Object.entries(budgets).map(([k,v])=>'<div class="spend-cell calc"><div class="k">'+k+'</div><div class="v">'+money(v)+'</div><div class="n">'+budgetNote+'</div></div>'));
  document.getElementById(elId).innerHTML=cells.join("");
}

// --- MTD section (pro-rated by monthly RR) ---
document.getElementById("mtd-title").innerHTML=DATA.MONTH_LABEL+' <span class="tag">MTD through '+DATA.SHORT_THROUGH+'</span>';
const ppcMtd=Object.values(DATA.SPEND_MTD).reduce((a,b)=>a+b,0);
const budMtd={}; Object.entries(BUD).forEach(([k,v])=>budMtd[k]=v*MRR);
const spendMtd=ppcMtd+Object.values(budMtd).reduce((a,b)=>a+b,0);
// projected full-month spend: full monthly budgets + PPC projected to full month (PPC MTD ÷ RR)
const projMonthSpend=budTotal+ppcMtd/MRR;
const plgArrMtd=PLG.first_mrr.cur_m*12, slgArrMtd=SLG_ARR_M*MRR;
roiKpis("mtd-kpis",spendMtd,plgArrMtd,slgArrMtd,"First MRR MTD ("+money(PLG.first_mrr.cur_m)+") × 12",
  "MTD actual · <b>"+money(projMonthSpend)+"</b> projected full month");
spendGrid("mtd-spend",DATA.SPEND_MTD,budMtd,"budget × "+(MRR*100).toFixed(1)+"% RR");

// --- Trailing 30-day rollover (full monthly budgets) ---
document.getElementById("roll-title").innerHTML='Trailing 30 days <span class="tag">'+DATA.ROLLOVER_LABEL+'</span>';
const ppc30=Object.values(DATA.SPEND_30D).reduce((a,b)=>a+b,0);
const spend30=ppc30+budTotal;
const plgArr30=DATA.PLG_30D.first_mrr*12, slgArr30=SLG_ARR_M;
roiKpis("roll-kpis",spend30,plgArr30,slgArr30,"First MRR 30d ("+money(DATA.PLG_30D.first_mrr)+") × 12",
  "PPC 30d actual + full monthly budgets");
spendGrid("roll-spend",DATA.SPEND_30D,BUD,"full monthly budget");

document.getElementById("snap-note").innerHTML=
  "<b>MTD</b>: PPC is actual month-to-date spend; SEO / Creative partnerships / Growth Channels are monthly budgets pro-rated by the "+(MRR*100).toFixed(1)+"% monthly run-rate; "+
  (SLG_ARR_ACTUAL
    ? "SLG ARR = actual monthly SLG ARR input ("+money(SLG_ARR_M)+") × RR; "
    : "SLG ARR = (B2B-MRR target "+money(DATA.SLG_B2B_TGT)+" ×12 ÷3 = "+money(SLG_ARR_M)+" monthly ARR) × RR; ")+
  "PLG ARR = First MRR MTD × 12.<br>"+
  "<b>Trailing 30 days</b> ("+DATA.ROLLOVER_LABEL+"): PPC is actual trailing-30-day spend; SEO / partnerships / growth are full monthly budgets; "+
  "SLG ARR = full monthly "+money(SLG_ARR_M)+(SLG_ARR_ACTUAL?" (actual input)":"")+"; PLG ARR = trailing-30-day First MRR × 12.<br>"+
  // Every non-PPC line here is priced off the fixed monthly budgets, on purpose. The channel report
  // reads its three spend lines from manual_inputs.json instead, so when those hold invoices-filed
  // actuals the two reports print different ROI for the same day. Say which one is which rather than
  // leaving the reader to discover the gap and distrust both.
  "<b>Basis:</b> every non-PPC line above is a fixed monthly budget, so this ROI stays comparable "+
  "across runs. The PLG channel-detail report prices the same three lines from <code>manual_inputs.json</code>; "+
  "whenever those carry invoices-filed actuals (which lag the spend) its Total Spend runs lower and its "+
  "ROI higher than the figure here. <b>This report is the comparable ROI series.</b>";

// ---- Invoice-board actuals ----  Reporting only: the ROI above stays on fixed budgets.
(function(){
  const I=DATA.INVOICE, grid=document.getElementById("inv-spend"), note=document.getElementById("inv-note");
  if(!I||!I.lines.length){ grid.innerHTML=""; note.innerHTML='<span class="na">No invoice-board figures in this build (invoice_spend missing from roi_report_values.json, or it did not reconcile).</span>'; return; }
  document.getElementById("inv-title").textContent="Invoice-board actuals - "+I.month_title;
  const cnt=n=>(n===null||n===undefined)?"invoices filed":nf(n)+(n===1?" invoice":" invoices");
  const esc=s=>String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  grid.innerHTML=I.lines.map(l=>'<div class="spend-cell"><div class="k">'+l.label+'</div><div class="v">'+money(l.v)+'</div><div class="n">'+cnt(l.n)+'</div></div>').join("")+
    '<div class="spend-cell calc"><div class="k">Total</div><div class="v">'+money(I.total)+'</div><div class="n">sum of the lines</div></div>';
  const parts=["Invoices filed on the Invoices and Payments board for "+I.month_title+". "+
    (I.split?"The board's Type column puts affiliate and B2B vendor invoices on their own lines, whoever paid them; "
            :"These figures predate the Type split and are grouped by who paid, so affiliate invoices paid by Creator Marketing sit inside Creative partnerships; ")+
    "Marketing Ops invoices are out of scope. "+
    "<b>Not part of the ROI above</b>, which prices these channels off fixed monthly budgets. Invoices arrive after the spend, so these figures lag it."];
  if(I.blank_n) parts.push(I.blank_n+(I.blank_n===1?" invoice has":" invoices have")+" no amount entered yet, so a line may understate.");
  if(I.flagged.length) parts.push(I.flagged.length+(I.flagged.length===1?" item needs":" items need")+" a team ruling and is not counted: "+I.flagged.map(esc).join(", ")+".");
  note.innerHTML=parts.join(" ");
})();

document.getElementById("footer").innerHTML="Generated "+new Date().toISOString().slice(0,10)+" · Riverside Marketing Analytics · via RiverMind /ask → Snowflake.<br>"+
  "PLG: analytics.bi.marketing_rollover · SLG: analytics.bi.sales_rollover (inbound) · Spend: analytics.bi.daily_campaign_signup_attribution · Targets: targets_2026.xlsx · Budgets: SEO/partnerships/growth monthly budgets · Invoice-board actuals: monday board 18390740532.<br>"+
  "SLG & Net MRR are Snowflake-direct (not Omni semantic layer)."+
  (DATA.NOTION_URL?'<br>Registered in Notion: <a href="'+DATA.NOTION_URL+'">artifact record</a>.':"");
</script>"""


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--plan":
        import pprint
        pprint.pprint(compute_roi_params(date.fromisoformat(sys.argv[2])))
        sys.exit(0)
    HERE = os.path.dirname(os.path.abspath(__file__))
    vp = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "roi_report_values.json")
    outp = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "roi_daily_snapshot.html")
    with open(vp) as f:
        values = json.load(f)
    html = build(values)
    with open(outp, "w") as f:
        f.write(html)
    print(f"Wrote {outp} ({len(html)} bytes) for anchor {values['anchor_date']}")
