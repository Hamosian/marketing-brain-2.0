/* 51-practice.js: "Route five test requests" (slide "practice").
 *
 * Draws five cases from evals/routing.jsonl (MBT.data.cases): up to three from the viewer's
 * role (MBT.role().weights), the rest from the general pool. Options are the expected skill plus near misses taken from
 * MBT.route(request), so every wrong option is one the description matcher itself confuses
 * with the right answer. One item per round carries the data rule (/rivermind:ask first, or
 * the documented /data-agent exception). Saves MBT.state 'practice' = {right, total}.
 */
(function () {
  'use strict';
  var MBT = window.MBT;
  if (!MBT || typeof MBT.route !== 'function' || !MBT.routerUtil) return;
  var slide = document.querySelector('.slide[data-id="practice"]');
  if (!slide) return;
  var U = MBT.routerUtil;
  function $(id) { return document.getElementById(id); }

  var qWrap = $('r-p-q'), countEl = $('r-p-count'), reqEl = $('r-p-request'), optsEl = $('r-p-options');
  var fbEl = $('r-p-feedback'), nextBtn = $('r-p-next'), doneEl = $('r-p-done'), scoreEl = $('r-p-score');
  var compareEl = $('r-p-compare'), msgEl = $('r-p-msg'), recapEl = $('r-p-recap'), againBtn = $('r-p-again');
  var railEl = $('r-p-rail'), roleEl = $('r-p-role'), lastEl = $('r-p-last'), live = $('r-p-live');
  if (!qWrap || !optsEl || !reqEl || !fbEl || !nextBtn) return;
  var nextHome = nextBtn.parentNode;

  var ROUND = 5, OPTIONS = 4;
  var TEMPLATE = /-copytemplates$/;
  var ICON_OK = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>';
  var ICON_BAD = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true" focusable="false"><path d="M7 7l10 10M17 7 7 17"/></svg>';

  function readCases() {
    var c = MBT.data && MBT.data.cases;
    if (Array.isArray(c)) return c;
    try { return JSON.parse(document.getElementById('routingCases').textContent) || []; } catch (e) { return []; }
  }
  function role() {
    try { return typeof MBT.role === 'function' ? MBT.role() : null; } catch (e) { return null; }
  }
  function roleKey() { var r = role(); return (r && r.key) || 'any'; }
  function hash(s) {
    var h = 5381;
    for (var i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0;
    return h >>> 0;
  }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }
  function cmd(name) { return el('span', 'cmd', '/' + name); }
  function sentence(s) {
    s = String(s || '').trim();
    s = s.charAt(0).toUpperCase() + s.slice(1);
    return /[.?]$/.test(s) ? s : s + '.';
  }
  function announce(text) {
    if (!live) return;
    live.textContent = '';
    setTimeout(function () { live.textContent = text; }, 30);
  }

  // Skills that are really one person's workflow even though they are not tagged as owned:
  // vendor-meeting-quality is drafted for Nir from his inbound flow, and invoice-inbox-to-monday
  // runs on Hanan's, Nir's or Erika's own inbox. Neither is a general answer to route to.
  var SKIP = { 'vendor-meeting-quality': 1, 'invoice-inbox-to-monday': 1 };

  // Regular pool: a general skill in the catalog, a short request, and no data phrasing
  // (data phrasing is taught by the dedicated data item, so the two lessons never disagree).
  function regular(c) {
    var n = c.expect;
    return !!U.skill(n) && U.isGeneral(n) && !SKIP[n] && n !== 'good-morning' && n !== 'data-agent' &&
      !TEMPLATE.test(n) && String(c.request).length <= 120 && !U.looksData(c.request);
  }

  // Plain-language reasons, one per answer skill. The suite's own notes are written for
  // maintainers (pass names, board IDs), so the slide shows these instead.
  var WHY = {
    'access-welcome': 'Greeting people who just got repo access is a daily routine: /access-welcome finds them and sends the setup guide.',
    'agent-builder': 'Building a new skill or a recurring routine is /agent-builder. The skill that would do the work once is the near miss.',
    'are-we-really-different': 'Checking whether our claims sound like every competitor is /are-we-really-different. It tests positioning, not conversion or copy.',
    'campaign-agent': 'Planning a launch across channels is orchestration, which is /campaign-agent. Drafting the pieces comes after.',
    'candidate-brief': 'A hiring brief or scorecard with a competency chart is its own artifact: /candidate-brief, not a general deck or chart.',
    'content-agent': 'Drafting branded copy, like a newsletter or an announcement, is /content-agent.',
    'critique': 'Asking whether finished writing is good enough is a verdict, and /critique gives it. It scores and never rewrites.',
    'curious-intern': 'Being interviewed so what you know lands in the repo is /curious-intern.',
    'de-ai': 'Cleaning the AI tells out of an existing draft is /de-ai. It fixes how the text reads without changing the voice.',
    'demo-reply-fact-check': 'Checking that a product claim is true, including which plan a feature is on, is /demo-reply-fact-check. It marks each claim before it ships.',
    'gong-calls-explorer': 'Calls with deal context come from /gong-calls-explorer, which joins Gong with HubSpot.',
    'granola-recipe-builder': 'Writing a reusable meeting-notes prompt for Granola is /granola-recipe-builder.',
    'graphify': 'Mapping how the repo\'s files connect is a knowledge-graph question, which is /graphify.',
    'health-check': 'Finding stale docs and missing fields is the repo check-up, /health-check.',
    'hubspot-agent': 'Looking up contacts, companies or deals in HubSpot is /hubspot-agent.',
    'hubspot-workflow-qa': 'Reviewing a HubSpot workflow before it goes live is /hubspot-workflow-qa. It ends in a sign-off.',
    'impeccable': 'Making a built design bolder or more polished is a craft pass, which is /impeccable. Conversion and page builds are other skills.',
    'lifecycle-agent': 'Designing a nurture or win-back journey is lifecycle work, which is /lifecycle-agent.',
    'link-triage': 'Links you want read and sorted go to /link-triage. It says what each one is, then asks what to do with it.',
    'linkedin-best-practices-2026': 'LinkedIn profile and platform know-how is /linkedin-best-practices-2026.',
    'list-skills': 'A live list of every skill and how to start it is /list-skills.',
    'marketing-brain': 'A broad question that spans paid, lifecycle and the site starts at /marketing-brain, which pulls in the right skills.',
    'marketing-council': 'Debating a direction from several expert points of view is /marketing-council. It argues the options; it does not pull data.',
    'marketing-ops-automation-agent': 'When an automation such as lead routing breaks, that is /marketing-ops-automation-agent.',
    'marketing-psychology': 'The biases and mental models behind a buying decision are /marketing-psychology.',
    'marketing-website-page-qa': 'Checking a finished page on staging before launch is /marketing-website-page-qa. Building the page is a different skill.',
    'measurement-agent': 'Reporting on performance and explaining what moved is /measurement-agent.',
    'mesh-expenditure-report': 'Spend and receipts in Mesh belong to /mesh-expenditure-report.',
    'monday-agent': 'Reading or updating monday items that already exist is /monday-agent. Writing a new ticket is /pm-story.',
    'mops-backlog-review': 'Going through the backlog and on-hold groups for what to archive is /mops-backlog-review.',
    'organic-dashboard': 'The monthly organic picture, with rankings, Search Console and content cohorts, is /organic-dashboard. The weekly report covers a single week.',
    'page-build': 'Building or updating a page from a ticket, a brief or a Figma file is /page-build. Reviewing a finished page is QA.',
    'page-cro': 'Working out why a page converts badly is /page-cro.',
    'paid-acquisition-agent': 'Paid channel health, like a sudden jump in cost per acquisition, is /paid-acquisition-agent.',
    'pm-story': 'Creating one new task or ticket is /pm-story. It writes the why and the done-when for you.',
    'podcast-transcript': 'Transcribing or summarizing a podcast episode is /podcast-transcript.',
    'retro': 'Writing what a workflow taught you back into the repo is /retro.',
    'riverside-brand-guidelines': 'Brand colors and fonts are owned by /riverside-brand-guidelines.',
    'riverside-presentation': 'A branded .pptx deck is /riverside-presentation.',
    'riverside-product-knowledge': 'How a feature works and which plan it is on comes from the Help Center, through /riverside-product-knowledge.',
    'riverside-ux-patterns': 'Spacing, hierarchy and focus states are interaction patterns, which is /riverside-ux-patterns. Colors and fonts are the brand skill.',
    'seo-ai-search-agent': 'Diagnosing a drop in organic or AI-search visibility is /seo-ai-search-agent.',
    'seo-de-report': 'Per-page organic numbers for the German site are /seo-de-report.',
    'skill-audit': 'Scoring how well a skill is written is /skill-audit.',
    'skill-eval': 'Testing that requests still route to the right skill is /skill-eval.',
    'slack-agent': 'Posting a message to a Slack channel is /slack-agent.',
    'ste': 'A short internal write-up where clarity matters most goes through /ste, which writes plain technical English.',
    'team-intro': 'Getting a new teammate oriented on the repo is /team-intro.',
    'ticket-hygiene': 'Auditing tickets that already exist is the /ticket-hygiene sweep: duplicates, the wrong board, a missing brief, or Slack asks never ticketed. /pm-story only writes new ones.',
    'value-proposition-canvas': 'Customer jobs, pains, gains and fit, and the test cards that check them, are /value-proposition-canvas.',
    'video-project-intake': 'Starting a video project, or checking a brief is ready, is /video-project-intake. It knows the Creative Ops board and its template.',
    'webflow-accessibility-audit': 'An accessibility (WCAG) check on a Webflow page is /webflow-accessibility-audit.',
    'webflow-asset-audit': 'Alt text and file names across the site\'s images are /webflow-asset-audit.',
    'webflow-build-agent': 'Building a Webflow page straight from a Figma spec is /webflow-build-agent.',
    'webflow-link-checker': 'Crawling pages for broken links and redirect chains is /webflow-link-checker.',
    'webflow-locale-publish-queue': 'Queueing translated CMS items for the next publish is /webflow-locale-publish-queue. A person still does the publish.',
    'website-agent': 'Who owns riverside.com and how a change ships is /website-agent, the front door for website work.',
    'weekly-seo-report': 'One finished week of organic search is /weekly-seo-report. The monthly view is the dashboard.',
    'win-loss-pricing-analyzer': 'Why deals are lost on price is /win-loss-pricing-analyzer.',
    'rivermind:ask': 'Every number or metric question goes to /rivermind:ask first. /data-agent is the fallback when Rivermind has no coverage.',
    'data-agent': 'Writing raw SQL to explore tables is the documented case that goes straight to /data-agent.'
  };
  function isDataCase(c) { return c.expect === 'rivermind:ask' || c.expect === 'data-agent'; }

  function buildItem(c) {
    var ranked = MBT.route(c.request);
    var opts = [c.expect];
    if (c.expect === 'rivermind:ask') opts.push('data-agent');
    function add(limit, strict) {
      for (var i = 0; i < Math.min(limit, ranked.length) && opts.length < OPTIONS; i++) {
        var n = ranked[i].name;
        if (ranked[i].score <= 0) break;
        if (opts.indexOf(n) >= 0) continue;
        if (strict && (!U.isGeneral(n) || TEMPLATE.test(n))) continue;
        opts.push(n);
      }
    }
    add(6, true);   // near misses: the matcher's top six, minus the answer
    add(12, true);
    add(6, false);
    ['marketing-brain', 'content-agent', 'monday-agent'].forEach(function (n) {
      if (opts.length < 3 && opts.indexOf(n) < 0) opts.push(n);
    });
    opts.sort(function (a, b) { return hash(c.request + '|' + a) - hash(c.request + '|' + b); });
    var top = ranked[0] && ranked[0].score > 0 ? ranked[0].name : null;
    return { c: c, opts: opts, matcherTop: top, answer: null };
  }

  var seen = {}, roundNo = 0, round = null, drawnFor = null;

  function draw() {
    var all = readCases();
    var pool = all.filter(regular);
    var fresh = pool.filter(function (c) { return !seen[c.request]; });
    if (fresh.length < ROUND) { seen = {}; fresh = pool.slice(); }
    var r = role(), favored = {};
    ((r && r.weights) || []).forEach(function (n) { favored[String(n).replace(/^\//, '')] = 1; });
    var picked = [], usedSkill = {};
    function take(list, max) {
      while (picked.length < max && list.length) {
        var c = list.splice(Math.floor(Math.random() * list.length), 1)[0];
        if (usedSkill[c.expect]) continue;
        usedSkill[c.expect] = 1;
        picked.push(c);
        var at = fresh.indexOf(c);
        if (at >= 0) fresh.splice(at, 1);
      }
    }
    // up to three from the viewer's role first (one per skill), then the general pool
    var mine = fresh.filter(function (c) { return favored[c.expect]; });
    if (mine.length < 3) mine = pool.filter(function (c) { return favored[c.expect]; });
    take(mine.slice(), 3);
    take(fresh.slice(), ROUND - 1);
    for (var q = picked.length - 1; q > 0; q--) { var j = Math.floor(Math.random() * (q + 1)); var t = picked[q]; picked[q] = picked[j]; picked[j] = t; }
    var dataPool = all.filter(isDataCase);
    var want = roundNo % 2 === 0 ? 'rivermind:ask' : 'data-agent';
    var d = dataPool.filter(function (c) { return c.expect === want; })[0] || dataPool[0];
    if (d) picked.splice(Math.min(picked.length, 1 + Math.floor(Math.random() * 3)), 0, d);
    picked = picked.slice(0, ROUND);
    picked.forEach(function (c) { seen[c.request] = 1; });
    roundNo++;
    drawnFor = roleKey();
    round = { items: picked.map(buildItem), i: 0, done: false };
  }

  function untouched() {
    return !round || (!round.done && round.i === 0 && !round.items[0].answer);
  }

  function paintRail() {
    if (!railEl) return;
    var pips = railEl.children;
    for (var i = 0; i < pips.length; i++) {
      var it = round.items[i], p = pips[i];
      p.className = 'r-p-pip' +
        (it && it.answer ? (it.answer === it.c.expect ? ' is-right' : ' is-wrong') : '') +
        (!round.done && i === round.i ? ' is-current' : '');
    }
  }

  function paintSide() {
    var r = role();
    if (roleEl) {
      var on = r && r.key && r.key !== 'any' && r.label;
      roleEl.hidden = !on;
      if (on) roleEl.textContent = 'Weighted toward ' + r.label + '.';
    }
    if (lastEl) {
      var last = MBT.state && typeof MBT.state.get === 'function' ? MBT.state.get('practice', null) : null;
      var show = last && typeof last.right === 'number' && typeof last.total === 'number';
      lastEl.hidden = !show;
      if (show) lastEl.textContent = 'Your last round: ' + last.right + ' of ' + last.total + '.';
    }
  }

  function renderItem() {
    var it = round.items[round.i];
    qWrap.hidden = false;
    if (doneEl) doneEl.hidden = true;
    countEl.textContent = 'Request ' + (round.i + 1) + ' of ' + round.items.length;
    reqEl.textContent = '“' + it.c.request + '”';
    while (optsEl.firstChild) optsEl.removeChild(optsEl.firstChild);
    it.opts.forEach(function (name) {
      var b = el('button', 'r-p-opt');
      b.type = 'button';
      b.setAttribute('aria-pressed', 'false');
      b.setAttribute('data-skill', name);
      var head = el('span', 'r-p-opt-head');
      head.appendChild(cmd(name));
      var tag = U.tagFor(name);
      if (tag) { var t = el('span', 'r-tag', tag.text); t.setAttribute('data-kind', tag.kind); head.appendChild(t); }
      var mark = el('span', 'r-p-mark');
      mark.setAttribute('aria-hidden', 'true');
      head.appendChild(mark);
      b.appendChild(head);
      b.appendChild(el('span', 'r-p-opt-d', U.blurb(name, 92)));
      b.addEventListener('click', function () { answer(name); });
      optsEl.appendChild(b);
    });
    nextBtn.hidden = true;
    if (nextHome && nextBtn.parentNode !== nextHome) nextHome.appendChild(nextBtn);
    fbEl.hidden = true;
    fbEl.textContent = '';
    paintRail();
  }

  function answer(name) {
    var it = round.items[round.i];
    if (it.answer) return;
    it.answer = name;
    var right = name === it.c.expect;
    Array.prototype.forEach.call(optsEl.children, function (b) {
      var n = b.getAttribute('data-skill');
      b.setAttribute('aria-disabled', 'true');
      if (n === name) b.setAttribute('aria-pressed', 'true');
      var mark = b.querySelector('.r-p-mark');
      if (n === it.c.expect) { b.classList.add('is-right'); mark.innerHTML = ICON_OK; }
      else if (n === name) { b.classList.add('is-wrong'); mark.innerHTML = ICON_BAD; }
      else b.classList.add('is-dim');
    });

    fbEl.textContent = '';
    fbEl.className = 'r-p-feedback ' + (right ? 'is-right' : 'is-wrong');
    var verdict = el('p', 'r-p-verdict');
    verdict.appendChild(document.createTextNode(right ? 'Right. ' : 'Not this time. '));
    verdict.appendChild(cmd(it.c.expect));
    verdict.appendChild(document.createTextNode(' owns this one.'));
    fbEl.appendChild(verdict);

    var whyText = WHY[it.c.expect];
    if (whyText) {
      var why = el('p', 'r-p-why');
      why.appendChild(el('span', 'r-p-label', 'Why'));
      var wt = el('span', 'r-p-why-text');
      whyText.split(/(\/[a-z][a-z0-9:-]*[a-z0-9])/).forEach(function (part) {
        if (!part) return;
        if (/^\/[a-z]/.test(part)) wt.appendChild(cmd(part.slice(1)));
        else wt.appendChild(document.createTextNode(part));
      });
      why.appendChild(wt);
      fbEl.appendChild(why);
    }
    if (!right) {
      var picked = el('p', 'r-p-picked');
      picked.appendChild(document.createTextNode('You picked '));
      picked.appendChild(cmd(name));
      picked.appendChild(document.createTextNode(': ' + sentence(U.blurb(name, 150)).replace(/…\.$/, '…')));
      fbEl.appendChild(picked);
    }
    var m = el('p', 'r-p-matcher');
    if (it.c.expect === 'rivermind:ask') {
      m.appendChild(document.createTextNode('The description matcher cannot rank '));
      m.appendChild(cmd('rivermind:ask'));
      m.appendChild(document.createTextNode(': it lives outside this repo, which is why this rule is worth remembering.'));
    } else if (it.matcherTop) {
      m.appendChild(document.createTextNode('The description matcher from the last slide ranked '));
      m.appendChild(cmd(it.matcherTop));
      m.appendChild(document.createTextNode(it.matcherTop === it.c.expect ? ' first too.' : ' first, so it missed this one.'));
    }
    // matcher note and the Next button share the feedback's last row, right after the why
    var foot = el('div', 'r-p-fb-foot');
    if (m.childNodes.length) foot.appendChild(m);
    var last = round.i === round.items.length - 1;
    nextBtn.textContent = last ? 'See your score' : 'Next request';
    nextBtn.hidden = false;
    foot.appendChild(nextBtn);
    fbEl.appendChild(foot);

    fbEl.hidden = false;
    paintRail();
    // focus moves to the feedback, which screen readers read; no second copy in the live region
    try { fbEl.focus({ preventScroll: false }); } catch (e) { fbEl.focus(); }
  }

  function finish() {
    round.done = true;
    var right = 0, matcher = 0;
    round.items.forEach(function (it) {
      if (it.answer === it.c.expect) right++;
      if (it.matcherTop === it.c.expect) matcher++;
    });
    var total = round.items.length;
    if (MBT.state && typeof MBT.state.set === 'function') MBT.state.set('practice', { right: right, total: total });

    qWrap.hidden = true;
    doneEl.hidden = false;
    scoreEl.textContent = '';
    scoreEl.appendChild(el('span', 'r-p-score-num', String(right)));
    scoreEl.appendChild(el('span', 'r-p-score-of', ' of ' + total + ' routed'));
    compareEl.textContent = 'The description matcher got ' + matcher + ' of the same ' + total + '.';
    msgEl.textContent = '';
    if (right === total) {
      msgEl.textContent = 'All five. You read what a request is for, not just its words.';
    } else if (right >= 3) {
      msgEl.textContent = 'Solid. The misses are worth a second look: each answer below is a call the team wrote down.';
    } else {
      msgEl.appendChild(document.createTextNode('Worth another round. When you are unsure, start with '));
      msgEl.appendChild(cmd('marketing-brain'));
      msgEl.appendChild(document.createTextNode(': it routes broad asks.'));
    }
    recapEl.textContent = '';
    round.items.forEach(function (it) {
      var ok = it.answer === it.c.expect;
      var li = el('li', 'r-p-recap-row ' + (ok ? 'is-right' : 'is-wrong'));
      var ic = el('span', 'r-p-recap-ic');
      ic.innerHTML = ok ? ICON_OK : ICON_BAD;
      li.appendChild(ic);
      var q = String(it.c.request);
      var qEl = el('span', 'r-p-recap-q');
      qEl.appendChild(el('span', 'sr-only', ok ? 'Right: ' : 'Missed: '));
      qEl.appendChild(document.createTextNode(q.length > 72 ? q.slice(0, 70).replace(/\s+\S*$/, '') + '…' : q));
      li.appendChild(qEl);
      li.appendChild(cmd(it.c.expect));
      recapEl.appendChild(li);
    });
    paintRail();
    if (lastEl) lastEl.hidden = true;
    announce('You routed ' + right + ' of ' + total + '. The description matcher got ' + matcher + '.');
    try { scoreEl.focus(); } catch (e) { /* ignore */ }
  }

  nextBtn.addEventListener('click', function () {
    if (!round.items[round.i].answer) return;
    if (round.i >= round.items.length - 1) { finish(); return; }
    round.i++;
    renderItem();
    announce('Request ' + (round.i + 1) + ' of ' + round.items.length + '.');
    reqEl.focus();
  });
  if (againBtn) {
    againBtn.addEventListener('click', function () {
      draw();
      paintSide();
      renderItem();
      reqEl.focus();
    });
  }

  function refreshIfUntouched() {
    if (untouched() && drawnFor !== roleKey()) { draw(); renderItem(); }
    paintSide();
  }
  if (typeof MBT.on === 'function') {
    MBT.on('role', refreshIfUntouched);
    MBT.on('state', function (p) {
      if (p == null || p.key == null || p.key === 'role') refreshIfUntouched();
    });
    MBT.on('slide', function (e) { if (e && e.id === 'practice') refreshIfUntouched(); });
  }

  draw();
  renderItem();
  paintSide();
})();
