/* 50-router.js: the live router (slide "router") and the shared routing core.
 *
 * MBT.route(text) is a straight port of scripts/eval_routing.py: TF-IDF cosine between the
 * request and each skill's name + description, with the tokenizer and stopwords of
 * scripts/sync_embeddings.py. The validator replays evals/routing.jsonl through it, so the
 * ranking itself must stay a faithful port. Every UI heuristic (data rule, owner tags,
 * low-signal fallback) lives in the display layer below, never in MBT.route.
 *
 * Also exports MBT.OWNERS (person-owned skills), MBT.flag(where, text) (the shared
 * "This looks wrong" writer, flags/<user id>) and MBT.routerUtil (helpers 51-practice.js reuses).
 */
(function () {
  'use strict';
  var MBT = window.MBT || (window.MBT = {});

  /* ---------- routing core (port of scripts/eval_routing.py) ---------- */
  var STOP = ('a about all also an and any are as at be been being but by can could did do does down each for from had has have he her his how if in into is it its just more most no not of on only or other our out over own same she should so some such than that the their them then these they this those to up was we were what when which who will with would you your').split(' ');
  var STOPSET = {};
  STOP.forEach(function (w) { STOPSET[w] = 1; });
  var TOKEN_RE = /[a-z0-9][a-z0-9\-']{1,}/g;

  function tokenize(text) {
    var m = String(text || '').toLowerCase().match(TOKEN_RE) || [];
    return m.filter(function (t) { return !STOPSET[t]; });
  }

  function buildIndex(catalog) {
    var lists = catalog.map(function (s) { return tokenize(s.name + ' ' + s.description); });
    var N = lists.length || 1, df = {};
    lists.forEach(function (toks) {
      var seen = {};
      toks.forEach(function (t) { if (!seen[t]) { seen[t] = 1; df[t] = (df[t] || 0) + 1; } });
    });
    var idf = {};
    Object.keys(df).forEach(function (t) { idf[t] = Math.log(N / df[t]) + 1.0; });
    var vecs = lists.map(function (toks) {
      var tf = {};
      toks.forEach(function (t) { tf[t] = (tf[t] || 0) + 1; });
      var len = toks.length || 1, w = {}, norm = 0;
      Object.keys(tf).forEach(function (t) { w[t] = (tf[t] / len) * idf[t]; norm += w[t] * w[t]; });
      norm = Math.sqrt(norm) || 1;
      Object.keys(w).forEach(function (t) { w[t] /= norm; });
      return w;
    });
    return { catalog: catalog, idf: idf, vecs: vecs };
  }

  function rank(index, request) {
    var toks = tokenize(request).filter(function (t) { return index.idf[t] !== undefined; });
    var tf = {};
    toks.forEach(function (t) { tf[t] = (tf[t] || 0) + 1; });
    var len = toks.length || 1, q = {}, norm = 0;
    Object.keys(tf).forEach(function (t) { q[t] = (tf[t] / len) * index.idf[t]; norm += q[t] * q[t]; });
    norm = Math.sqrt(norm) || 1;
    Object.keys(q).forEach(function (t) { q[t] /= norm; });
    var out = index.vecs.map(function (v, i) {
      var s = 0;
      for (var t in q) { if (v[t] !== undefined) s += q[t] * v[t]; }
      return { name: index.catalog[i].name, score: s };
    });
    out.sort(function (a, b) {
      return b.score - a.score || (a.name < b.name ? -1 : a.name > b.name ? 1 : 0);
    });
    return out;
  }

  function readJSON(id, fallback) {
    try {
      var el = document.getElementById(id);
      return el ? JSON.parse(el.textContent) : fallback;
    } catch (e) { return fallback; }
  }
  function catalog() {
    var c = MBT.data && MBT.data.catalog;
    return Array.isArray(c) ? c : readJSON('skillCatalog', []);
  }
  function facts() {
    return (MBT.data && MBT.data.facts) || readJSON('buildFacts', {});
  }

  var INDEX = null, BYNAME = null;
  function index() {
    if (!INDEX) INDEX = buildIndex(catalog());
    return INDEX;
  }
  function skill(name) {
    if (!BYNAME) {
      BYNAME = {};
      catalog().forEach(function (s) { BYNAME[s.name] = s; });
    }
    return BYNAME[name] || null;
  }

  MBT.route = function (text) { return rank(index(), text); };

  /* ---------- who a skill is for (display layer only) ---------- */
  // Built for one named person (SPEC.md, checked against each SKILL.md description).
  MBT.OWNERS = {
    'chief-of-staff': 'Nir',
    'hanan-chief-of-staff': 'Hanan',
    'nir-weekly-report': 'Nir',
    'nir-monthly-report': 'Nir',
    'nir-mql-live-report': 'Nir',
    'inbound-demo-reply': 'Nir',
    'invoice-board-spend-pulse': 'Nir',
    'growth-marketing-team-tasks': 'Nir',
    'nik-voice': 'Nir',
    'raz-ops': 'Raz Navon',
    'weekly-1-1s': 'Raz Navon',
    'p1-p2-followup': 'Hanan',
    'mops-standup': 'Hanan and Jonathan'
  };

  function tagFor(name) {
    if (MBT.OWNERS[name]) return { text: 'Built for ' + MBT.OWNERS[name], kind: 'owner' };
    if (name === 'good-morning') return { text: 'For MOPs and Growth leads', kind: 'scope' };
    if (name === 'marketing-os') return { text: 'Old name of /marketing-brain', kind: 'scope' };
    if (/-copytemplates$/.test(name)) return { text: 'Headline template', kind: 'scope' };
    return null;
  }
  // Skills a general viewer should not be handed as "copy this and run it".
  function isGeneral(name) {
    return !MBT.OWNERS[name] && name !== 'marketing-os';
  }

  // Short lines for skills whose descriptions open with trigger phrases instead of a job.
  var BLURB = {
    'pm-story': 'Creates or documents one monday task or ticket, with Why, What, Done When and Open Questions.',
    'good-morning': 'Daily brief of active monday work, team updates, Slack activity and open risks.',
    'list-skills': 'Shows every team skill and how to trigger it.',
    'team-intro': 'Tells you what it knows about the team, its projects and its systems.',
    'agent-builder': 'Builds or deploys a new agent, skill or cloud routine, lint-clean.',
    'impeccable': 'Design pass on a built interface: shape, audit, critique, polish, layout, type.',
    'curious-intern': 'Interviews you to fill gaps in the knowledge base.',
    'health-check': 'Checks the team context for stale docs, missing fields and template drift.',
    'retro': 'Captures what a finished workflow taught you back into the repo.',
    'granola-recipe-builder': 'Creates or improves a Granola recipe, a reusable prompt for meeting notes.',
    'marketing-psychology': 'Applies psychology, mental models and behavioral science to marketing.',
    'graphify': 'Builds and queries the repo’s knowledge graph.',
    'setup': 'Sets up a new team context for the first time.',
    'raz-ops': 'Raz Navon’s own routines, monday tasks and standing preferences.',
    'weekly-1-1s': 'Raz Navon’s prep for his weekly 1:1s with Jarred and with Nir.',
    'link-triage': 'Reads pasted links, classifies each one, then asks what to do with it.',
    'marketing-brain': 'Top-level router for broad or cross-system marketing work.',
    'marketing-os': 'Old name of /marketing-brain, kept so older references still work.',
    'rivermind:ask': 'The analytics team’s validated data layer. First stop for every data question.'
  };

  function trim(s, max) {
    if (s.length <= max) return s;
    s = s.slice(0, max);
    var k = s.lastIndexOf(' ');
    if (k > max * 0.6) s = s.slice(0, k);
    return s.replace(/[\s,;:.(\-]+$/, '') + '…';
  }
  function blurb(name, max) {
    max = max || 140;
    if (BLURB[name]) return trim(BLURB[name], max);
    var sk = skill(name);
    var s = String(sk ? sk.description : '').replace(/\s+/g, ' ').trim();
    s = s.replace(/^(ALWAYS use this skill\s*[-:,]?\s*|Use this skill (whenever|when|for|to)\s+|Use (this )?(skill )?(when|for)\s+|Specialist sub-agent for\s+|Specialized sub-agent for\s+|Automation skill that\s+)/i, '');
    s = s.replace(/^(the user|someone)\s+(wants to\s+)?/i, '');
    var m = s.match(/^(.+?[.?])\s+(?=[A-Z"'(“])/);
    if (m) s = m[1];
    s = trim(s, max);
    return s.charAt(0).toUpperCase() + s.slice(1);
  }

  // Data or metric phrasing (CLAUDE.md: every data question goes to /rivermind:ask first).
  var DATA_RE = /\b(how many|number|rates?|mqls?|sqls?|conversions?|trends?|metrics?|counts?|revenue|sign-?ups?|what counts as|cac)\b/i;
  function looksData(text) { return DATA_RE.test(String(text || '')); }

  function sharedWords(text, name) {
    var idx = index(), sk = skill(name);
    if (!sk) return [];
    var mine = {};
    tokenize(sk.name + ' ' + sk.description).forEach(function (t) { mine[t] = 1; });
    var seen = {}, out = [];
    tokenize(text).forEach(function (t) {
      if (mine[t] && idx.idf[t] !== undefined && !seen[t]) { seen[t] = 1; out.push(t); }
    });
    out.sort(function (a, b) { return idx.idf[b] - idx.idf[a]; });
    return out.slice(0, 4);
  }
  // Words that carry no task on their own ("help me", "fix this", "make it better").
  // Used only to decide the low-signal fallback; the ranking still sees every word.
  var FILLER = {};
  ('me my mine us help please need want wanted thing things something anything stuff make get got let lets let\'s ' +
   'can could would like just hey hi hello thanks thank ok okay better good fix new know tell really quick quickly ' +
   'look see give show work done go try maybe way ask asked').split(' ').forEach(function (w) { FILLER[w] = 1; });
  function vocabHits(text, content) {
    var idf = index().idf;
    return tokenize(text).filter(function (t) { return idf[t] !== undefined && !(content && FILLER[t]); }).length;
  }

  function copyText(text, btn) {
    if (typeof MBT.copy === 'function') { MBT.copy(text, btn); return; }
    try { if (navigator.clipboard) navigator.clipboard.writeText(text); } catch (e) { /* no clipboard */ }
  }

  /* ---------- MBT.flag: "This looks wrong" -> flags/<user id> {items:[{where,text,at}]} ---------- */
  var flagChain = Promise.resolve(false);
  if (typeof MBT.flag !== 'function') {
    MBT.flag = function (where, text) {
      var job = flagChain.then(function () {
        if (typeof MBT.cap !== 'function') return false;
        return Promise.all([MBT.cap('db'), MBT.cap('user')]).then(function (caps) {
          var db = caps[0], user = caps[1];
          if (!db || !user || typeof user.id !== 'function') return false;
          return Promise.resolve(user.id()).then(function (id) {
            if (!id) return false;
            var ref = db.doc('flags/' + id);
            return ref.get().then(function (snap) {
              var body = snap && snap.exists ? snap.data() : null;
              var items = body && Array.isArray(body.items) ? body.items.slice() : [];
              items.push({ where: String(where).slice(0, 40), text: String(text).slice(0, 500), at: new Date().toISOString() });
              if (items.length > 20) items = items.slice(items.length - 20);
              return ref.set({ items: items }).then(function () { return true; });
            });
          });
        });
      }).catch(function () { return false; });
      flagChain = job;
      return job;
    };
  }

  MBT.routerUtil = {
    tokenize: tokenize,
    skill: skill,
    blurb: blurb,
    tagFor: tagFor,
    isGeneral: isGeneral,
    looksData: looksData,
    sharedWords: sharedWords
  };

  /* ---------- the router slide ---------- */
  var slide = document.querySelector('.slide[data-id="router"]');
  if (!slide) return;
  function $(id) { return document.getElementById(id); }

  var input = $('r-input'), clearBtn = $('r-clear'), chipsEl = $('r-chips'), stage = $('r-stage');
  var dataBox = $('r-data'), dataCopy = $('r-data-copy'), lowBox = $('r-low'), lowText = $('r-low-text'), lowCopy = $('r-low-copy');
  var listLabel = $('r-list-label'), rows = Array.prototype.slice.call(slide.querySelectorAll('.r-row'));
  var live = $('r-live'), flagBtn = $('r-flag'), flagNote = $('r-flag-note');
  var askWrap = $('r-ask-wrap'), askBtn = $('r-ask'), askOut = $('r-ask-out');
  if (!input || !stage) return;

  // caption facts come from the build, never hardcoded
  var f = facts();
  Array.prototype.forEach.call(slide.querySelectorAll('[data-r-fact]'), function (el) {
    var v = f[el.getAttribute('data-r-fact')];
    if (v !== undefined && v !== null) el.textContent = String(v);
  });

  // role-aware examples; every one checked against MBT.route so the demo tells the truth
  var CHIPS = {
    any: ['tell me about the team', 'what skills do you have', 'how many signups did we get last week', 'make this draft sound less like AI wrote it'],
    seo: ['build the monthly organic search dashboard', 'is our search console data stale', 'how are we showing up in AI search answers', 'how many organic signups did we get last month'],
    paid: ['audit our paid campaigns for wasted spend', 'diagnose why this landing page is not converting', 'what was our CAC by channel last quarter'],
    creator: ['get a transcript of this podcast episode', 'critique this creator script before we film', 'draft the newsletter copy for the feature launch'],
    mops: ['open a ticket for a broken form on the pricing page', 'find slack requests that never became tickets', 'review this hubspot workflow before it goes live', 'lead routing broke, new leads are not getting assigned'],
    sdr: ['what plan is async recording on', 'check the product claims in this reply before I send it', 'look up this company\'s contacts and deals in HubSpot'],
    'brand-design': ['build a Riverside deck for the QBR', 'which brand colors and fonts should this use', 'this hero design is bland, make it bolder'],
    'brand-video': ['start a new video project from Raz’s brief', 'check this video brief has every required field', 'tighten the story in this ad script'],
    pmm: ['do we sound different from our competitors', 'map the customer jobs, pains and gains for this persona', 'check the claims in this launch copy', 'draft the newsletter copy for the feature launch'],
    content: ['how should we structure LinkedIn posts for reach', 'strip the AI tells from this draft', 'draft the newsletter copy for the feature launch'],
    ai: ['build a new skill for our team', 'audit how well this skill is written', 'check that the skill descriptions still route correctly'],
    initiatives: ['debate this pricing change from a few expert angles', 'plan a cross-channel campaign for the launch', 'what is our trial to paid conversion trend']
  };

  function roleKey() {
    try { var r = typeof MBT.role === 'function' ? MBT.role() : null; return (r && r.key) || 'any'; } catch (e) { return 'any'; }
  }
  function renderChips() {
    if (!chipsEl) return;
    var list = CHIPS[roleKey()] || CHIPS.any;
    while (chipsEl.firstChild) chipsEl.removeChild(chipsEl.firstChild);
    list.forEach(function (text) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'chip r-chip';
      b.textContent = text;
      b.addEventListener('click', function () {
        input.value = text;
        syncClear();
        run(true);
        // on a stacked (phone) layout the result sits below the chips: bring it into view
        if (window.matchMedia && window.matchMedia('(max-width: 960px)').matches && stage.scrollIntoView) {
          try { stage.scrollIntoView({ block: 'nearest', behavior: MBT.reduced ? 'auto' : 'smooth' }); } catch (e) { stage.scrollIntoView(false); }
        }
      });
      chipsEl.appendChild(b);
    });
    if (!current && rows.length) idle();
  }
  renderChips();
  if (typeof MBT.on === 'function') {
    MBT.on('role', renderChips);
    MBT.on('state', function (p) {
      if (p == null || p.key == null || p.key === 'role') renderChips();
    });
  }

  var current = null; // {text, ranked, state, data}
  var debounce = null, speak = null, askSeq = 0, sampleNS = null;

  function setCmd(el, name) { el.textContent = '/' + name; }

  function show(el, on) { if (el) el.hidden = !on; }

  function paintRows(text, top3, copyAt, weak) {
    var best = top3[0] ? top3[0].score : 0;
    rows.forEach(function (row, i) {
      var r = top3[i];
      var nameEl = row.querySelector('.r-name'), tagEl = row.querySelector('.r-tag'), fill = row.querySelector('.r-bar-fill');
      var bl = row.querySelector('.r-blurb'), words = row.querySelector('.r-words'), cp = row.querySelector('.r-copy');
      if (!r || r.score <= 0) {
        row.hidden = true;
        return;
      }
      row.hidden = false;
      setCmd(nameEl, r.name);
      var tag = tagFor(r.name);
      tagEl.hidden = !tag;
      if (tag) { tagEl.textContent = tag.text; tagEl.setAttribute('data-kind', tag.kind); }
      row.classList.toggle('is-owned', !!MBT.OWNERS[r.name]);
      fill.style.width = Math.max(4, Math.round((r.score / (best || 1)) * 100)) + '%';
      bl.textContent = blurb(r.name, 150);
      var sw = sharedWords(text, r.name);
      words.textContent = '';
      if (sw.length) {
        var lab = document.createElement('span');
        lab.className = 'r-words-label';
        lab.textContent = 'Shared words';
        words.appendChild(lab);
        sw.forEach(function (w) {
          var s = document.createElement('span');
          s.className = 'r-word';
          s.textContent = w;
          words.appendChild(s);
        });
      }
      words.hidden = !sw.length;
      cp.hidden = i !== copyAt;
      cp.setAttribute('aria-label', 'Copy /' + r.name + ' with your request');
      cp.setAttribute('data-copy', '/' + r.name + ' ' + text);
    });
    stage.classList.toggle('is-weak', !!weak);
  }

  function idle() {
    current = null;
    stage.setAttribute('data-state', 'idle');
    stage.classList.remove('is-data');
    show(dataBox, false);
    show(lowBox, false);
    // resting state: the first example's real matches, faded, so it reads as empty, not loading
    var ex = (CHIPS[roleKey()] || CHIPS.any)[0];
    paintRows(ex, MBT.route(ex).slice(0, 3), -1, false);
    if (listLabel) listLabel.textContent = 'For example: \u201c' + ex + '\u201d';
    stage.classList.remove('is-weak');
    hideAsk();
    syncAskVisibility();
  }

  function run(now) {
    clearTimeout(debounce);
    if (!now) { debounce = setTimeout(function () { run(true); }, 150); return; }
    var text = input.value.replace(/\s+/g, ' ').trim();
    clearTimeout(speak);
    if (flagNote) flagNote.textContent = '';
    if (text.length < 3) { idle(); return; }
    var ranked = MBT.route(text);
    var top3 = ranked.slice(0, 3);
    var best = top3[0] ? top3[0].score : 0;
    var rawHits = vocabHits(text, false), hits = vocabHits(text, true);
    var data = looksData(text) || (top3[0] && top3[0].name === 'data-agent' && best > 0);
    var low = !data && (hits === 0 || best < 0.09 || (hits <= 1 && best < 0.3) || (hits <= 2 && best < 0.15));
    var copyAt = -1;
    for (var i = 0; i < top3.length; i++) { if (top3[i].score > 0 && isGeneral(top3[i].name)) { copyAt = i; break; } }
    var allOwned = !low && !data && copyAt < 0;
    var state = data ? 'data' : (low || allOwned) ? 'low' : 'result';
    if (data || state === 'low') copyAt = -1;

    if (current && current.text !== text) hideAsk();
    current = { text: text, ranked: ranked, state: state, data: data };
    stage.setAttribute('data-state', state);
    stage.classList.toggle('is-data', !!data);

    show(dataBox, data);
    if (data && dataCopy) dataCopy.setAttribute('data-copy', '/rivermind:ask ' + text);

    show(lowBox, state === 'low');
    if (state === 'low') {
      if (lowText) {
        lowText.textContent = '';
        lowText.appendChild(document.createTextNode(allOwned
          ? 'The closest matches are built for one person’s workflow. Start with '
          : 'No clear match. Start with '));
        var mb = document.createElement('span');
        mb.className = 'cmd';
        mb.textContent = '/marketing-brain';
        lowText.appendChild(mb);
        lowText.appendChild(document.createTextNode(', it routes broad asks.'));
      }
      if (lowCopy) lowCopy.setAttribute('data-copy', '/marketing-brain ' + text);
    }

    if (listLabel) {
      listLabel.textContent = rawHits === 0 ? 'No skill description shares these words'
        : state === 'low' ? 'Closest, but weak'
        : data ? 'Words that matched (not where to start)'
        : 'Closest matches';
    }
    paintRows(text, rawHits === 0 ? [] : top3, copyAt, state === 'low');
    syncAskVisibility();

    speak = setTimeout(function () { announce(summary()); }, 500);
  }

  function summary() {
    if (!current) return '';
    var r = current.ranked, names = r.slice(0, 3).filter(function (x) { return x.score > 0; }).map(function (x) { return '/' + x.name; });
    if (current.state === 'data') {
      return 'Data question. Go to /rivermind:ask first, with /data-agent as the fallback.' + (names.length ? ' Closest skill by description: ' + names[0] + '.' : '');
    }
    if (current.state === 'low') return 'No clear match. Start with /marketing-brain.';
    var top = r[0].name, own = MBT.OWNERS[top];
    return 'Closest match ' + names[0] + (own ? ', built for ' + own : '') + (names.length > 1 ? '. Then ' + names.slice(1).join(' and ') + '.' : '.');
  }
  function announce(text) {
    if (!text) return;
    if (live) { live.textContent = ''; setTimeout(function () { live.textContent = text; }, 30); }
  }

  function syncClear() { if (clearBtn) clearBtn.hidden = !input.value; }

  input.addEventListener('input', function () { syncClear(); run(false); });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && input.value) { e.preventDefault(); e.stopPropagation(); input.value = ''; syncClear(); run(true); }
    if (e.key === 'Enter') { e.preventDefault(); run(true); }
  });
  if (clearBtn) {
    clearBtn.addEventListener('click', function () {
      input.value = '';
      syncClear();
      run(true);
      input.focus();
    });
  }

  // one delegated listener for every copy button on the stage
  stage.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('[data-copy]') : null;
    if (b && stage.contains(b)) copyText(b.getAttribute('data-copy'), b);
  });

  /* ---------- "This looks wrong" ---------- */
  if (flagBtn) {
    // Only offer the flag where it can be saved (db + a signed-in viewer), like the catalog's flag form.
    var flagLine = flagBtn.parentNode;
    if (flagLine) flagLine.hidden = true;
    if (typeof MBT.cap === 'function') {
      Promise.all([MBT.cap('db'), MBT.cap('user')]).then(function (c) {
        var user = c[1];
        if (!c[0] || !user || typeof user.id !== 'function') return null;
        return Promise.resolve(user.id());
      }).then(function (id) { if (id && flagLine) flagLine.hidden = false; }, function () { /* stays hidden */ });
    }
    flagBtn.addEventListener('click', function () {
      if (!current) {
        flagNote.textContent = 'Type a request first, then flag the result.';
        return;
      }
      var top = current.ranked.slice(0, 3).map(function (x) { return x.name; }).join(', ');
      var payload = '"' + current.text + '" -> ' + (current.state === 'data' ? '[data rule] ' : current.state === 'low' ? '[no clear match] ' : '') + top;
      flagNote.textContent = 'Sending…';
      MBT.flag('router', payload).then(function (saved) {
        flagNote.textContent = saved
          ? 'Thanks. The trainer’s owner will see this request and its matches.'
          : 'Flagging is not available here. Tell Hanan in Slack.';
      });
    });
  }

  /* ---------- optional: Ask Claude to route this (sample capability) ---------- */
  function hideAsk() {
    askSeq++;
    if (askOut) { askOut.hidden = true; askOut.textContent = ''; }
    if (askBtn) { askBtn.disabled = false; askBtn.removeAttribute('aria-busy'); }
  }
  function syncAskVisibility() {
    if (askWrap) askWrap.hidden = !(sampleNS && current);
  }
  if (typeof MBT.cap === 'function' && askWrap) {
    Promise.resolve(MBT.cap('sample')).then(function (s) {
      sampleNS = s || null;
      syncAskVisibility();
    }, function () { sampleNS = null; });
  }

  var DASHES = new RegExp('\\s*[' + String.fromCharCode(8212, 8211) + ']\\s*', 'g');
  function clean(s) { return String(s || '').replace(DASHES, ', ').trim(); }

  function askPrompt(text) {
    var lines = catalog().map(function (s) { return '- ' + s.name + ': ' + trim(String(s.description).replace(/\s+/g, ' '), 240); });
    var owned = Object.keys(MBT.OWNERS).join(', ');
    return 'You route requests to the skills of Riverside’s Marketing Brain, a shared Claude Code repo for the Marketing department.\n' +
      'Rules:\n' +
      '1. Data and metric questions (counts, rates, trends, definitions such as "what counts as an MQL") go to rivermind:ask first. data-agent is only the fallback when Rivermind lacks coverage or the task needs ad-hoc SQL.\n' +
      '2. Person-owned skills are not general tools; do not pick them for a general request: ' + owned + '.\n' +
      '3. When no single skill fits, or the request spans several systems, pick marketing-brain, which routes broad asks.\n\n' +
      'Skills (name: description):\n' + lines.join('\n') + '\n- rivermind:ask: the analytics team’s validated data layer, first stop for every data question.\n\n' +
      'Request: ' + JSON.stringify(text) + '\n\n' +
      'Reply with JSON only, no prose: {"skill": "<skill name>", "why": "<one plain sentence, under 25 words>", "runnerUp": "<skill name>"}';
  }

  function renderAsk(ans) {
    askOut.textContent = '';
    var skillName = String((ans && ans.skill) || '').replace(/^\//, '').trim();
    if (!skillName) { askOut.textContent = 'Claude did not name a skill this time.'; return; }
    var head = document.createElement('p');
    head.className = 'r-ask-head';
    var lab = document.createElement('span');
    lab.className = 'r-ask-label';
    lab.textContent = 'Claude’s pick';
    var cmd = document.createElement('span');
    cmd.className = 'cmd';
    cmd.textContent = '/' + skillName;
    head.appendChild(lab);
    head.appendChild(cmd);
    var tag = tagFor(skillName);
    if (tag) {
      var t = document.createElement('span');
      t.className = 'r-tag';
      t.setAttribute('data-kind', tag.kind);
      t.textContent = tag.text;
      head.appendChild(t);
    }
    askOut.appendChild(head);
    if (ans.why) {
      var why = document.createElement('p');
      why.className = 'r-ask-why';
      why.textContent = clean(ans.why);
      askOut.appendChild(why);
    }
    var ru = String(ans.runnerUp || '').replace(/^\//, '').trim();
    if (ru && ru !== skillName) {
      var r = document.createElement('p');
      r.className = 'r-ask-ru';
      r.textContent = 'Runner-up: /' + ru;
      askOut.appendChild(r);
    }
    if (!skill(skillName) && skillName !== 'rivermind:ask') {
      var warn = document.createElement('p');
      warn.className = 'r-ask-ru';
      warn.textContent = 'That name is not in this repo’s skill list, so treat it with care.';
      askOut.appendChild(warn);
    }
  }

  if (askBtn) {
    askBtn.addEventListener('click', function () {
      if (!sampleNS || !current || typeof sampleNS.json !== 'function') return;
      var seq = ++askSeq, text = current.text;
      askBtn.disabled = true;
      askBtn.setAttribute('aria-busy', 'true');
      askOut.hidden = false;
      askOut.textContent = 'Asking Claude…';
      var done = function () { askBtn.disabled = false; askBtn.removeAttribute('aria-busy'); };
      Promise.resolve().then(function () {
        return sampleNS.json(askPrompt(text), { modelTier: 'quick' });
      }).then(function (ans) {
        if (seq !== askSeq) return;
        done();
        renderAsk(ans || {});
        announce('Claude picked ' + (ans && ans.skill ? '/' + String(ans.skill).replace(/^\//, '') : 'nothing') + '.');
      }, function (err) {
        if (seq !== askSeq) return;
        done();
        var code = err && err.code;
        if (code === 'not_granted') {
          sampleNS = null;
          askOut.hidden = true;
          syncAskVisibility();
          return;
        }
        askOut.textContent = code === 'rate_limited'
          ? 'Claude is getting a lot of requests from this page. Try again in a minute.'
          : code === 'cancelled' ? '' : 'Claude could not answer this time.';
      });
    });
  }

  idle();
})();
