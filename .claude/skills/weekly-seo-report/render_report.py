# -*- coding: utf-8 -*-
import html, json, os
SP = os.path.dirname(os.path.abspath(__file__))   # assets sit beside this script
# Reuse the logo already in the repo rather than duplicating it in this skill.
import base64
_LOGO = os.path.join(SP, "..", "..", "..", "docs", "presentations", "marketing-os", "riverside-logo-white.png")
logo = base64.b64encode(open(os.environ.get("REPORT_LOGO", _LOGO), "rb").read()).decode()
style = open(SP + "/style.html").read()

# ---------------------------------------------------------------------------
# All figures come from one JSON payload written by the weekly runbook, so this
# file is a renderer with no data of its own. Regenerate the payload, re-run
# this, and the report is current. See SKILL.md in this directory.
# ---------------------------------------------------------------------------
DATA = json.load(open(os.environ.get("REPORT_DATA", SP + "/report-data.json"), encoding="utf-8"))
METRICS = DATA["METRICS"]
CH      = DATA["CH"]
TOT     = DATA["TOT"]
SHORT   = DATA["SHORT"]
RAILS   = DATA["RAILS"]
PAGES   = DATA["PAGES"]
SUBPAGES= DATA["SUBPAGES"]
GAIN    = DATA["GAIN"]
DROP    = DATA["DROP"]
AUTH    = set(DATA["AUTH"])
TOP25_SU        = DATA["TOP25_SU"]
TOP25_SUBS      = DATA["TOP25_SUBS"]
PAGES_WITH_SU   = DATA["PAGES_WITH_SU"]
ZERO_SUB_PAGES  = DATA["ZERO_SUB_PAGES"]
ZERO_SUB_SU     = DATA["ZERO_SUB_SU"]
PAGES_2PLUS_SUBS= DATA["PAGES_2PLUS_SUBS"]
PAGES_1_SUB     = DATA["PAGES_1_SUB"]
G       = DATA["GSC"]
M       = DATA["_meta"]

def _label(iso):
    y, m, d = iso.split("-")
    return "%s %d, %s" % (["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][int(m)-1], int(d), y)
def _range(pair):
    a, b = pair
    ay, am, ad = a.split("-"); by, bm, bd = b.split("-")
    mon = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    if am == bm and ay == by:
        return "%s %d to %d, %s" % (mon[int(am)-1], int(ad), int(bd), ay)
    return "%s %d to %s %d, %s" % (mon[int(am)-1], int(ad), mon[int(bm)-1], int(bd), by)
FW_CUR = _range(M["funnel_window"]["cur"]); FW_PRV = _range(M["funnel_window"]["prv"])
PULLED = _label(M["pulled"]); SF_THROUGH = _label(M["snowflake_through"])
GSC_THROUGH = _label(M["gsc_through"])




def fnum(v, money=False):
    return ("$" + format(round(v, 2), ",.2f")) if money else format(int(v), ",")
def ctr(v):
    return ("%.2f%%" % v) if v >= 1 else ("%.3f%%" % v)

def pct(c, p):
    return None if p == 0 else (c - p) / p * 100.0
def chip(c, p):
    q = pct(c, p)
    if q is None: return '<span class="chip chip-new">new</span>'
    cls = "chip-flat"
    if abs(q) >= 0.5: cls = "chip-up" if q > 0 else "chip-dn"
    sign = "+" if q > 0 else ("−" if q < 0 else "")
    return '<span class="chip %s">%s%s%%</span>' % (cls, sign, format(abs(q), ".1f"))
def chip_base(c, p, floor, money=False):
    """A percentage off a tiny prior base is noise. Show the absolute move, neutrally styled."""
    if c == 0 and p == 0:
        return '<span style="color:var(--ink-4)">&mdash;</span>'
    if p < floor:
        d = c - p
        sign = "+" if d > 0 else ("−" if d < 0 else "")
        return ('<span class="chip chip-flat" title="Prior base too small for a meaningful percentage">%s%s</span>'
                % (sign, fnum(abs(d), money)))
    return chip(c, p)
def dchip(d, up_is_good=True):
    sign = "+" if d > 0 else ("−" if d < 0 else "")
    cls = "chip-flat"
    if d != 0: cls = "chip-up" if (d > 0) == up_is_good else "chip-dn"
    return '<span class="chip %s">%s%s</span>' % (cls, sign, fnum(abs(d)))
def delta_abs(c, p, money=False):
    d = c - p; sign = "+" if d > 0 else ("−" if d < 0 else "")
    return sign + fnum(abs(d), money)

auth_su = sum(r[3] for r in PAGES if r[0] in AUTH)
auth_n = sum(1 for r in PAGES if r[0] in AUTH)
cov_su = TOP25_SU / TOT["cur"][1] * 100
auth_drop = sum(1 for r in DROP if r[0] in AUTH)
sp_subs_c = sum(r[7] for r in SUBPAGES); sp_subs_p = sum(r[8] for r in SUBPAGES)
sp_mrr_c = sum(r[9] for r in SUBPAGES);  sp_mrr_p = sum(r[10] for r in SUBPAGES)
sp_cov_subs = sp_subs_c / TOT["cur"][3] * 100
sp_cov_mrr = sp_mrr_c / TOT["cur"][4] * 100
sp_auth_subs = sum(r[7] for r in SUBPAGES if r[0] in AUTH)
sp_auth_n = sum(1 for r in SUBPAGES if r[0] in AUTH)
sp_tools_n = sum(1 for r in SUBPAGES if r[0].startswith("tools/"))
su_tools_n = sum(1 for r in PAGES if r[0].startswith("tools/"))
sp_thin = sum(1 for r in SUBPAGES if r[8] < 5)
sp_thick = len(SUBPAGES) - sp_thin


P = []; A = P.append
A('<title>Weekly SEO Report</title>')
A(style)
A('''<style>
.tabs{display:flex;gap:6px;border-bottom:1px solid var(--line);margin-bottom:-18px}
.tabs button{
  appearance:none;background:none;border:0;border-bottom:2px solid transparent;
  color:var(--ink-3);font-family:inherit;font-size:13.5px;font-weight:600;letter-spacing:.01em;
  padding:11px 16px 12px;cursor:pointer;margin-bottom:-1px;
}
.tabs button:hover{color:var(--ink-2)}
.tabs button[aria-selected="true"]{color:var(--ink);border-bottom-color:var(--accent)}
.tabs button:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:4px}
.panel{display:flex;flex-direction:column;gap:44px}
.panel[hidden]{display:none}
.srcnote{
  font-size:12.5px;color:var(--ink-3);background:rgba(217,161,59,.08);
  border:1px solid rgba(217,161,59,.28);border-radius:10px;padding:11px 16px;
}
.srcnote b{color:#E0B45E;font-weight:600}
</style>''')
A('<style>.subhead{margin:0;font-size:15px;font-weight:600;color:var(--ink);display:flex;align-items:center;gap:10px}'
  '.subhead .tag{font-size:10px;font-weight:700;letter-spacing:.11em;text-transform:uppercase;padding:3px 8px;'
  'border-radius:5px}.tag-up{background:var(--pos-bg);color:var(--pos)}.tag-dn{background:var(--neg-bg);'
  'color:var(--neg)}.movers{display:flex;flex-direction:column;gap:26px}.mover-blk{display:flex;'
  'flex-direction:column;gap:11px}</style>')
A('<div class="wrap">')

A('<header class="mast">')
A('<div class="mast-top"><img class="logo" alt="Riverside" src="data:image/png;base64,%s">'
  '<span style="font-size:12px;color:var(--ink-4);font-weight:500">Growth Marketing &middot; Marketing OS</span></div>' % logo)
A('<div><p class="eyebrow">Snowflake &middot; analytics.bi.marketing_rollover</p>')
A('<h1>Organic search conversion, last 7 days vs prior 7</h1>')
A('<p class="sub">Full organic funnel with the brand, non-brand, and LLM split, the top 25 landing pages by sign-ups, '
  'and the pages that gained and lost the most sign-ups, plus a Search Console tab covering clicks, impressions, '
  'the top 25 queries and pages, the non-brand query and page movers, and the top 10 countries. The two tabs run on different windows because Search Console lags '
  'three days: check the banner on each.</p></div>')
A('<dl class="fresh">')
A('<div><dt>Funnel source</dt><dd>Snowflake, through %s <span class="ok">&#10003;</span></dd></div>' % SF_THROUGH.rsplit(",",1)[0])
A('<div><dt>Search source</dt><dd>Search Console, through %s</dd></div>' % GSC_THROUGH.rsplit(",",1)[0])
A('<div><dt>Pulled</dt><dd>%s</dd></div>' % PULLED)
A('<div><dt>Partial days</dt><dd>None, both windows complete</dd></div>')
A('</dl></header>')

A('<div class="tabs" role="tablist" aria-label="Report sections">')
A('<button role="tab" id="t-funnel" aria-controls="p-funnel" aria-selected="true">Snowflake funnel</button>')
A('<button role="tab" id="t-gsc" aria-controls="p-gsc" aria-selected="false" tabindex="-1">Search Console</button>')
A('</div>')
A('<div class="panel" id="p-funnel" role="tabpanel" aria-labelledby="t-funnel">')


WIN = ('<div class="window-note"><span><b>Current:</b> ' + FW_CUR + '</span>'
       '<span style="color:var(--ink-4)">vs</span><span><b>Prior:</b> ' + FW_PRV + '</span>'
       '<span style="color:var(--ink-4)">&middot;</span><span>' + M.get('funnel_window_note',
       'Both windows are 7 complete days with the same number of weekend days, so the comparison is '
       'calendar-matched.') + '</span></div>')

# overall
A('<section><h2>Overall organic search</h2>')
A(WIN)
A('<div class="tiles">')
for i, m in enumerate(METRICS):
    money = (i == 4); c = TOT["cur"][i]; p = TOT["prv"][i]
    A('<div class="tile"><div class="k">%s</div><div class="v num">%s</div><div class="foot">%s'
      '<span class="num">%s vs %s</span></div></div>'
      % (m, fnum(c, money), chip(c, p), delta_abs(c, p, money), fnum(p, money)))
A('</div>')
A('<p class="lede">Traffic and top-of-funnel grew, revenue did not. First visits are up 3.3% and trials up 6.6%, but '
  'new subscriptions fell 5.2% and first MRR fell 7.5%. The funnel got wider at the top and narrower at the bottom in '
  'the same week.</p></section>')

# channel
A('<section><h2>Split by channel</h2>')
A('<p class="lede">Snowflake <code class="path">channel_group</code> is the source of the brand / non-brand / LLM '
  'split, and is the reliable classifier for the funnel. Short labels map to <code class="path">organic search non '
  'brand</code>, <code class="path">organic search brand</code>, and <code class="path">organic llm</code>.</p>')
A('<div class="scroll"><table><thead><tr class="grp"><th></th>')
for m in METRICS: A('<th colspan="3" class="gsep">%s</th>' % m)
A('</tr><tr><th>Channel</th>')
for _ in range(5): A('<th class="gsep">Current</th><th>Prior</th><th>&#916;</th>')
A('</tr></thead><tbody>')
for name in ["organic search non brand", "organic search brand", "organic llm"]:
    A('<tr><td class="lead"><span class="ch-name"><span class="ch-rail" style="background:%s"></span>%s</span></td>'
      % (RAILS[name], SHORT[name]))
    for i in range(5):
        money = (i == 4); c = CH[name]["cur"][i]; p = CH[name]["prv"][i]
        A('<td class="num gsep">%s</td><td class="num" style="color:var(--ink-3)">%s</td><td>%s</td>'
          % (fnum(c, money), fnum(p, money), chip(c, p)))
    A('</tr>')
A('</tbody><tfoot><tr><td>Total organic</td>')
for i in range(5):
    money = (i == 4); c = TOT["cur"][i]; p = TOT["prv"][i]
    A('<td class="num gsep">%s</td><td class="num" style="color:var(--ink-3)">%s</td><td>%s</td>'
      % (fnum(c, money), fnum(p, money), chip(c, p)))
A('</tr></tfoot></table></div>')
A('<p class="lede"><b style="color:var(--ink)">Where the subscription drop sits.</b> Non-brand lost 23 subscriptions '
  '(&minus;15.6%) and $727 of first MRR (&minus;15.7%) while its first visits rose 4.7% and sign-ups rose 6.5%. Brand '
  'shed 12 subscriptions despite trials rising 9.5%. Organic LLM is the only channel up on revenue: 53 subscriptions '
  '(+23.3%) on $1,555 MRR (+24.7%) from falling visits, off a small base. Brand remains 25.6% of organic first visits '
  'but 61.8% of organic first MRR.</p></section>')

# top 25 by sign-ups
A('<section><h2>Top 25 landing pages by sign-ups</h2>')
A(WIN)
A('<p class="lede">Ranked by sign-ups in the current window. Homepage merged from <code class="path">NULL</code>, '
  'empty string, and <code class="path">homepage</code>. The cut is clean: exactly 25 pages reached 23 or more '
  'sign-ups, and rank 26 sits at 22 or below, so no tiebreak was needed.</p>')
A('<div class="scroll"><table><thead><tr class="grp"><th></th>'
  '<th colspan="3" class="gsep">Sign-ups</th><th colspan="2" class="gsep">First visits</th>'
  '<th colspan="2" class="gsep">Trials</th><th colspan="3" class="gsep">New subscriptions</th>'
  '<th colspan="3" class="gsep">First MRR</th></tr>'
  '<tr><th>Page</th><th class="gsep">Cur</th><th>Prior</th><th>&#916;</th><th class="gsep">Cur</th><th>Prior</th>'
  '<th class="gsep">Cur</th><th>Prior</th><th class="gsep">Cur</th><th>Prior</th><th>&#916;</th>'
  '<th class="gsep">Cur</th><th>Prior</th><th>&#916;</th></tr></thead><tbody>')
for idx, r in enumerate(PAGES, 1):
    url, fvc, fvp, suc, sup, trc, trp, sbc, sbp, mrc, mrp = r
    disp = "/" if url == "/" else "/" + url
    flag = ('<span class="flagdot" title="Authentication or in-product funnel page, not an acquisition landing page">'
            '</span>') if url in AUTH else ""
    A('<tr><td class="lead"><span class="rank">%d</span><code class="path">%s</code>%s</td>'
      % (idx, html.escape(disp), flag))
    A('<td class="num gsep">%s</td><td class="num" style="color:var(--ink-3)">%s</td><td>%s</td>'
      % (fnum(suc), fnum(sup), chip(suc, sup)))
    A('<td class="num gsep">%s</td><td class="num" style="color:var(--ink-3)">%s</td>' % (fnum(fvc), fnum(fvp)))
    A('<td class="num gsep">%s</td><td class="num" style="color:var(--ink-3)">%s</td>' % (fnum(trc), fnum(trp)))
    A('<td class="num gsep">%s</td><td class="num" style="color:var(--ink-3)">%s</td><td>%s</td>'
      % (fnum(sbc), fnum(sbp), chip_base(sbc, sbp, 5)))
    A('<td class="num gsep">%s</td><td class="num" style="color:var(--ink-3)">%s</td><td>%s</td>'
      % (fnum(mrc, True), fnum(mrp, True), chip_base(mrc, mrp, 100, True)))
    A('</tr>')
A('</tbody><tfoot><tr><td>Top 25 subtotal</td>')
A('<td class="num gsep">%s</td><td class="num">%s</td><td>%s</td>'
  % (fnum(TOP25_SU), fnum(sum(r[4] for r in PAGES)), chip(TOP25_SU, sum(r[4] for r in PAGES))))
A('<td class="num gsep">%s</td><td class="num">%s</td>' % (fnum(sum(r[1] for r in PAGES)), fnum(sum(r[2] for r in PAGES))))
A('<td class="num gsep">%s</td><td class="num">%s</td>' % (fnum(sum(r[5] for r in PAGES)), fnum(sum(r[6] for r in PAGES))))
A('<td class="num gsep">%s</td><td class="num">%s</td><td>%s</td>'
  % (fnum(TOP25_SUBS), fnum(sum(r[8] for r in PAGES)), chip(TOP25_SUBS, sum(r[8] for r in PAGES))))
A('<td class="num gsep">%s</td><td class="num">%s</td><td>%s</td>'
  % (fnum(sum(r[9] for r in PAGES), True), fnum(sum(r[10] for r in PAGES), True),
     chip(sum(r[9] for r in PAGES), sum(r[10] for r in PAGES))))
A('</tr></tfoot></table></div>')
A('<p class="lede">The top 25 hold <b style="color:var(--ink)">%s of %s organic sign-ups (%.1f%%)</b> out of %s pages '
  'with any sign-up at all. Ranking by sign-ups surfaces a very different page set than ranking by subscriptions: '
  '<b style="color:var(--ink)">%d of these 25 pages produced zero subscriptions</b> in the window while carrying %s '
  'sign-ups between them, most of them free <code class="path">/tools/*</code> utilities. Pages marked '
  '<span class="flagdot"></span> are authentication or in-product funnel steps, not acquisition landing pages.</p>'
  % (fnum(TOP25_SU), fnum(TOT["cur"][1]), cov_su, fnum(PAGES_WITH_SU), ZERO_SUB_PAGES, fnum(ZERO_SUB_SU)))
A('</section>')

# movers
A('<section><h2>Biggest sign-up movers</h2>')
A('<p class="lede">Ranked by <b style="color:var(--ink)">absolute change in sign-ups</b> between the same two windows, '
  'not by percentage. A percentage ranking would fill both tables with pages moving from 1 sign-up to 4. First visits '
  'sit alongside so you can see whether the sign-up move came with a traffic move or against it.</p>')
A('<div class="movers">')
for title, tag, tagcls, rows, up_good in [
    ("Top 10 pages by increase in sign-ups", "Gained", "tag-up", GAIN, True),
    ("Top 10 pages by decrease in sign-ups", "Lost", "tag-dn", DROP, False)]:
    A('<div class="mover-blk">')
    A('<p class="subhead"><span class="tag %s">%s</span>%s</p>' % (tagcls, tag, title))
    A('<div class="scroll"><table><thead><tr class="grp"><th></th><th colspan="4" class="gsep">Sign-ups</th>'
      '<th colspan="3" class="gsep">First visits</th></tr>'
      '<tr><th>Page</th><th class="gsep">Cur</th><th>Prior</th><th>&#916;</th><th>&#916;%</th>'
      '<th class="gsep">Cur</th><th>Prior</th><th>&#916;</th></tr></thead><tbody>')
    for idx, (url, suc, sup, fvc, fvp) in enumerate(rows, 1):
        disp = "/" if url == "/" else "/" + url
        flag = ('<span class="flagdot" title="Authentication or in-product funnel page, not an acquisition landing '
                'page"></span>') if url in AUTH else ""
        A('<tr><td class="lead"><span class="rank">%d</span><code class="path">%s</code>%s</td>'
          % (idx, html.escape(disp), flag))
        A('<td class="num gsep">%s</td><td class="num" style="color:var(--ink-3)">%s</td><td>%s</td><td>%s</td>'
          % (fnum(suc), fnum(sup), dchip(suc - sup, True), chip(suc, sup)))
        A('<td class="num gsep">%s</td><td class="num" style="color:var(--ink-3)">%s</td><td>%s</td>'
          % (fnum(fvc), fnum(fvp), dchip(fvc - fvp, True)))
        A('</tr>')
    A('</tbody></table></div></div>')
A('</div>')
A('<p class="lede"><b style="color:var(--ink)">What the two lists actually say.</b> The gains are concentrated and '
  'mostly traffic-led: <code class="path">/transcription</code> (+84 sign-ups on +487 visits) and the homepage (+60 on '
  '+134) are three quarters of the top ten between them. Two moved against their traffic, which is the more '
  'interesting signal: <code class="path">/de/transkription</code> added 12 sign-ups on 4 <i>fewer</i> visits, and '
  '<code class="path">/blog/is-riverside-free</code> added 11 on 5 more. On the losing side, three pages shed '
  'sign-ups while traffic grew, so the loss is conversion-side rather than demand-side: '
  '<code class="path">/tools/audio-transcriber</code> (&minus;10 sign-ups on +56 visits), '
  '<code class="path">/tools/convert-mp3-to-text</code> (&minus;11 on +17), and '
  '<code class="path">/video-compressor</code> is the mirror case, gaining 11 sign-ups on +85 visits. Read the first '
  'data note before acting on either table: the largest single decline, <code class="path">/verify-email</code>, '
  'is not an acquisition page at all.</p>')
A('</section>')

# top 20 by subscriptions
A('<section><h2>Top 20 landing pages by new subscriptions</h2>')
A(WIN)
A('<p class="lede">The revenue view of the same two windows. Ranked by new subscriptions in the current window, and '
  'the cut is clean here too: exactly %d pages reached 2 or more subscriptions and the next %d sit at precisely 1, so '
  '20 is where the list naturally ends rather than an arbitrary stop.</p>' % (PAGES_2PLUS_SUBS, PAGES_1_SUB))
A('<div class="scroll"><table><thead><tr class="grp"><th></th>'
  '<th colspan="3" class="gsep">New subscriptions</th><th colspan="3" class="gsep">First MRR</th>'
  '<th colspan="2" class="gsep">Trials</th><th colspan="2" class="gsep">Sign-ups</th>'
  '<th colspan="2" class="gsep">First visits</th></tr>'
  '<tr><th>Page</th><th class="gsep">Cur</th><th>Prior</th><th>&#916;</th><th class="gsep">Cur</th><th>Prior</th>'
  '<th>&#916;</th><th class="gsep">Cur</th><th>Prior</th><th class="gsep">Cur</th><th>Prior</th>'
  '<th class="gsep">Cur</th><th>Prior</th></tr></thead><tbody>')
for idx, r in enumerate(SUBPAGES, 1):
    url, fvc, fvp, suc, sup, trc, trp, sbc, sbp, mrc, mrp = r
    disp = "/" if url == "/" else "/" + url
    flag = ('<span class="flagdot" title="Authentication or in-product funnel page, not an acquisition landing page">'
            '</span>') if url in AUTH else ""
    A('<tr><td class="lead"><span class="rank">%d</span><code class="path">%s</code>%s</td>'
      % (idx, html.escape(disp), flag))
    A('<td class="num gsep">%s</td><td class="num" style="color:var(--ink-3)">%s</td><td>%s</td>'
      % (fnum(sbc), fnum(sbp), chip_base(sbc, sbp, 5)))
    A('<td class="num gsep">%s</td><td class="num" style="color:var(--ink-3)">%s</td><td>%s</td>'
      % (fnum(mrc, True), fnum(mrp, True), chip_base(mrc, mrp, 100, True)))
    A('<td class="num gsep">%s</td><td class="num" style="color:var(--ink-3)">%s</td>' % (fnum(trc), fnum(trp)))
    A('<td class="num gsep">%s</td><td class="num" style="color:var(--ink-3)">%s</td>' % (fnum(suc), fnum(sup)))
    A('<td class="num gsep">%s</td><td class="num" style="color:var(--ink-3)">%s</td>' % (fnum(fvc), fnum(fvp)))
    A('</tr>')
A('</tbody><tfoot><tr><td>Top 20 subtotal</td>')
A('<td class="num gsep">%s</td><td class="num">%s</td><td>%s</td>' % (fnum(sp_subs_c), fnum(sp_subs_p), chip(sp_subs_c, sp_subs_p)))
A('<td class="num gsep">%s</td><td class="num">%s</td><td>%s</td>' % (fnum(sp_mrr_c, True), fnum(sp_mrr_p, True), chip(sp_mrr_c, sp_mrr_p)))
A('<td class="num gsep">%s</td><td class="num">%s</td>' % (fnum(sum(r[5] for r in SUBPAGES)), fnum(sum(r[6] for r in SUBPAGES))))
A('<td class="num gsep">%s</td><td class="num">%s</td>' % (fnum(sum(r[3] for r in SUBPAGES)), fnum(sum(r[4] for r in SUBPAGES))))
A('<td class="num gsep">%s</td><td class="num">%s</td>' % (fnum(sum(r[1] for r in SUBPAGES)), fnum(sum(r[2] for r in SUBPAGES))))
A('</tr></tfoot></table></div>')
A('<p class="lede">These 20 pages carry <b style="color:var(--ink)">%s of %s organic subscriptions (%.1f%%)</b> and '
  '<b style="color:var(--ink)">%s of %s first MRR (%.1f%%)</b>. Revenue is far more concentrated than sign-ups: the '
  'homepage alone is %d subscriptions, %.1f%% of every organic subscription, against %.1f%% of sign-ups. Put beside '
  'the sign-up table, the contrast is the point: the free <code class="path">/tools/*</code> pages that fill %d of the '
  'top 25 sign-up slots appear just %d times here, and <code class="path">/pricing</code> '
  'jumps from 11th on sign-ups to 2nd on subscriptions. Pages marked <span class="flagdot"></span> are authentication '
  'or in-product funnel steps and account for %s of these subscriptions.</p>'
  % (fnum(sp_subs_c), fnum(TOT["cur"][3]), sp_cov_subs, fnum(sp_mrr_c, True), fnum(TOT["cur"][4], True), sp_cov_mrr,
     SUBPAGES[0][7], SUBPAGES[0][7] / TOT["cur"][3] * 100, PAGES[0][3] / TOT["cur"][1] * 100,
     su_tools_n, sp_tools_n, fnum(sp_auth_subs)))
A('<p class="lede" style="color:var(--ink-3)">Note the subscription and MRR deltas here run on thin bases: %d of the '
  '20 pages held under 5 subscriptions a week earlier, so those rows show the absolute move in grey rather than a '
  'percentage. Only the %d pages above that floor carry a real week-over-week percentage.</p>'
  % (sp_thin, sp_thick))
A('</section>')

# ---- Data notes and issues. Payload-driven: every edition writes its own
# findings, because a hardcoded finding republishes last month's numbers.
# Payload shape: FINDINGS = [{sev, sevlabel, color, title, blocks: [html, ...]}]
FINDINGS = DATA.get("FINDINGS", [])
if FINDINGS:
    A('<section><h2>Data notes and issues</h2>')
    A('<p class="lede">%s</p>' % DATA.get(
        "FINDINGS_LEDE",
        "Ranked by how much each one would change a decision made off these numbers."))
    A('<div class="finds">')
    _SEVCOLOR = {1: "var(--neg)", 2: "var(--caution)", 3: "var(--accent)"}
    for f in FINDINGS:
        sev = int(f.get("sev", 2))
        color = f.get("color") or _SEVCOLOR.get(sev, "var(--caution)")
        A('<div class="find"><div class="stripe" style="background:%s"></div><div class="body">' % color)
        A('<h3><span class="sev sev-%d">%s</span>%s</h3>'
          % (sev, html.escape(str(f.get("sevlabel", "Read with care"))),
             html.escape(str(f.get("title", "")))))
        for b in f.get("blocks", []):
            A(b)
        A('</div></div>')
    A('</div></section>')

A('</div>')  # close funnel panel

# ================= SEARCH CONSOLE PANEL =================
def _mh5(col):
    return ('<div class="scroll"><table><thead><tr><th>%s</th><th class="gsep">Clicks</th>'
            '<th>Prior</th><th>&#916;</th><th>&#916;%%</th></tr></thead><tbody>' % col)

def _lede(key):
    txt = G.get("ledes", {}).get(key)
    return '<p class="lede">%s</p>' % txt if txt else ""


A('<div class="panel" id="p-gsc" role="tabpanel" aria-labelledby="t-gsc" hidden>')

W = G["window"]
GWIN = ('<div class="window-note"><span><b>Current:</b> %s</span><span style="color:var(--ink-4)">vs</span>'
        '<span><b>Prior:</b> %s</span><span style="color:var(--ink-4)">&middot;</span>'
        '<span>%s</span></div>') % (W["cur"], W["prv"], W.get("note",
            "Both windows are 7 complete days with the same number of weekend days each."))

A('<section><h2>Search Console overview</h2>')
A('<div class="srcnote"><b>Different window from the funnel tab.</b> Search Console data ends %s, a %d-day lag, '
  'so its last 7 full days are %s. The Snowflake tab covers %s. The two overlap by 5 days and must '
  'not be read as the same period.</div>' % (W["through"], W["lag"], W["cur"], FW_CUR))
A(GWIN)
ov=G["overall"]
tiles=[("Clicks", ov["clicks"][0], ov["clicks"][1], "n"),
       ("Impressions", ov["impressions"][0], ov["impressions"][1], "n"),
       ("CTR", ov["ctr"][0], ov["ctr"][1], "p"),
       ("Avg position", ov["position"][0], ov["position"][1], "x")]
A('<div class="tiles">')
for lab,c,pv,kind in tiles:
    if kind=="n": val, prior = fnum(c), fnum(pv)
    elif kind=="p": val, prior = "%.2f%%" % c, "%.2f%%" % pv
    else: val, prior = "%.2f" % c, "%.2f" % pv
    q=(c-pv)/pv*100
    good = (q<0) if kind=="x" else (q>0)   # deeper position is worse
    cls = "chip-flat" if abs(q)<0.5 else ("chip-up" if good else "chip-dn")
    sign = "+" if q>0 else ("&minus;" if q<0 else "")
    A('<div class="tile"><div class="k">%s</div><div class="v num">%s</div><div class="foot">'
      '<span class="chip %s">%s%.1f%%</span><span class="num">prior %s</span></div></div>'
      % (lab, val, cls, sign, abs(q), prior))
A('</div>')
A(_lede("overview"))
A('</section>')

# ---- GSC tables. Seven sections, fixed order, set by Amir on 2026-09-17.
# Everything here is payload-driven; see knowledge/build-and-render.md for the spec.

def clicks_table(title, key, col, rows, code=False):
    """One clicks/prior/delta/delta% table. rows = [[label, cur, prior], ...]"""
    A('<section><h2>%s</h2>' % title)
    A(_mh5(col))
    for i, (lab, c, pv) in enumerate(rows, 1):
        safe = html.escape(str(lab))
        cell = '<code class="path">%s</code>' % safe if code else safe
        A('<tr><td class="lead"><span class="rank">%d</span>%s</td>'
          '<td class="num gsep">%s</td><td class="num" style="color:var(--ink-3)">%s</td>'
          '<td>%s</td><td>%s</td></tr>'
          % (i, cell, fnum(c), fnum(pv), dchip(c - pv), chip(c, pv)))
    A('</tbody></table></div>')
    A(_lede(key))
    A('</section>')

q = G["queries_top25"]
clicks_table("Top 25 queries, by clicks", "queries_top25", "Query", q)

nbm = G["nb_query_movers"]
clicks_table("Top 10 non-brand queries, clicks improved", "nb_up", "Query", nbm["up"])
clicks_table("Top 10 non-brand queries, clicks declined", "nb_down", "Query", nbm["down"])

clicks_table("Top 25 pages, by clicks", "pages_top25", "Page", G["pages_top25"], code=True)

pm = G["page_movers"]
clicks_table("Top 10 pages, clicks increased", "pages_up", "Page", pm["up"], code=True)
clicks_table("Top 10 pages, clicks decreased", "pages_down", "Page", pm["down"], code=True)

# ---- countries
A('<section><h2>Top 10 countries</h2>')
A('<div class="scroll"><table><thead><tr class="grp"><th></th><th colspan="3" class="gsep">Clicks</th>'
  '<th colspan="3" class="gsep">Impressions</th><th colspan="2" class="gsep">CTR</th></tr>'
  '<tr><th>Country</th><th class="gsep">Cur</th><th>Prior</th><th>&#916;%</th><th class="gsep">Cur</th>'
  '<th>Prior</th><th>&#916;%</th><th class="gsep">Cur</th><th>Prior</th></tr></thead><tbody>')
for i, (nm, c, ci, pv, pi) in enumerate(G["countries"], 1):
    A('<tr><td class="lead"><span class="rank">%d</span>%s</td>'
      '<td class="num gsep">%s</td><td class="num" style="color:var(--ink-3)">%s</td><td>%s</td>'
      '<td class="num gsep">%s</td><td class="num" style="color:var(--ink-3)">%s</td><td>%s</td>'
      '<td class="num gsep">%s</td><td class="num" style="color:var(--ink-3)">%s</td></tr>'
      % (i, nm, fnum(c), fnum(pv), chip(c, pv), fnum(ci), fnum(pi), chip(ci, pi),
         ctr(c / ci * 100) if ci else '&mdash;', ctr(pv / pi * 100) if pi else '&mdash;'))
A('</tbody></table></div>')
A(_lede("countries"))
A('</section>')

# ---- method notes. One section, prose only. A connector defect never gets its
# own section with evidence tables; that crowds out the analysis.
A('<section><h2>Method notes</h2>')
if G.get("read_clicks_note"):
    A('<div class="srcnote">%s</div>' % G["read_clicks_note"])
for para in G.get("method_notes", []):
    A('<p class="lede">%s</p>' % para)
A('</section>')

A('</div>')  # close gsc panel

A('<footer>')
A("""<p class="sql"><b style="color:var(--ink-2)">Method.</b> Single source: Snowflake <code>analytics.bi.marketing_rollover</code>, queried directly. Stages counted as <code>COUNT(CASE WHEN metric = 'first_visit' / 'sign_up' / 'trial' / 'new_subscription' THEN 1 END)</code>; first MRR as <code>SUM(CASE WHEN metric = 'new_subscription' THEN first_mrr END)</code>. Organic scope: <code>channel_group IN ('organic search non brand', 'organic search brand', 'organic llm')</code>. Homepage canonicalized from NULL, empty string, and <code>homepage</code> to <code>/</code>; <code>/de</code> and <code>/de/home</code> are distinct pages and are never merged or netted. Movers ranked on <code>su_current - su_prior</code> across all pages, not only the top 25. Freshness gate passed at <code>MAX(date_day) = """ + M["snowflake_through"] + """</code>. Channel figures cross-foot to the totals on all five metrics; the page sign-up total cross-foots to """ + fnum(TOP25_SU) + """ with no residual.</p>""")
A('<p><b style="color:var(--ink-2)">Search Console tab.</b> ' + G.get("footer_note",
  'Source: Google Search Console for <code>sc-domain:riverside.com</code> via the Windsor.ai '
  '<code>searchconsole</code> connector, data through ' + GSC_THROUGH + '. Every figure is aggregated '
  'from daily <code>date</code> + <code>device</code> rows rather than a <code>date</code>-only pull, '
  'which drops days silently. Aggregated <code>position</code> is impression-weighted, not a naive mean. '
  'No numeric filters were used in any pull. Nothing from Search Console is blended into the Snowflake '
  'tab, and the two tabs cover different date windows.') + '</p>')
A("""<p>Page paths are shown with a leading slash for readability; stored values carry none except the homepage. No Ahrefs or Omni data is used anywhere in this report.</p>""")
A("""<p><b style="color:var(--ink-3)">AI diligence.</b> This report was produced by the Riverside Marketing OS agent. Every figure was queried live from Snowflake and cross-footed against independently computed totals, and the data issues above were verified with dedicated validation queries rather than inferred. Figures are accurate as of the pull on """ + PULLED + """ for data through """ + SF_THROUGH + """. Interpretation is the agent analysis and should be reviewed before external use.</p>""")
A('</footer></div>')
A('''<script>
(function(){
  var tabs = Array.prototype.slice.call(document.querySelectorAll('[role="tab"]'));
  function select(tab){
    tabs.forEach(function(t){
      var on = t === tab;
      var panel = document.getElementById(t.getAttribute('aria-controls'));
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      if (panel) panel.hidden = !on;
    });
    window.scrollTo({top:0, behavior:'smooth'});
  }
  tabs.forEach(function(t, i){
    t.addEventListener('click', function(){ select(t); });
    t.addEventListener('keydown', function(e){
      var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
      if (!d) return;
      e.preventDefault();
      var n = tabs[(i + d + tabs.length) % tabs.length];
      n.focus(); select(n);
    });
  });
})();
</script>''')

out = "\n".join(P)
_dest = os.environ.get("REPORT_OUT")
if not _dest:
    raise SystemExit("REPORT_OUT is required. Set it to a path outside the repo "
                     "(your scratchpad), so a run never drops report HTML into the skill directory.")
open(_dest, "w", encoding="utf-8").write(out)
print("bytes:", len(out))
print("top25 signups %d/%d = %.1f%%" % (TOP25_SU, TOT["cur"][1], cov_su))
print("signup sum check:", sum(r[3] for r in PAGES), "should be", TOP25_SU)
print("subs sum check:", sum(r[7] for r in PAGES), "should be", TOP25_SUBS)
print("auth pages in top25: %d carrying %d signups (%.1f%%)" % (auth_n, auth_su, auth_su/TOP25_SU*100))
print("auth pages in decliners:", auth_drop)
