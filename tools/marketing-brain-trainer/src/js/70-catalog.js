/* 70-catalog.js: appendix interactions for slides 14, 15, 17 and 18.
   14 appendix: pick a request, see which context layers it opens.
   15 catalog:  every skill, searchable, filterable by area, copyable.
   17 upkeep:   step through one change, lane by lane.
   18 slack:    the confirm-before-send demo.
   The graph (slide 16) lives in 71-graph.js. */
(function () {
  'use strict';

  var MBT = window.MBT || {};
  var ELL = '…';
  // long dashes (built from char codes so no dash escape sits in the source)
  var DASHES = new RegExp('\\s*[' + String.fromCharCode(8211, 8212) + ']\\s*', 'g');

  function $(id) { return document.getElementById(id); }
  function readJSON(id) {
    try { var el = $(id); return el ? JSON.parse(el.textContent) : null; } catch (e) { return null; }
  }
  function data(key, elId) {
    var d = MBT.data && MBT.data[key];
    return d || readJSON(elId);
  }
  function facts() { return data('facts', 'buildFacts') || {}; }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function announce(t) { if (typeof MBT.announce === 'function') MBT.announce(t); }
  function plural(n, one, many) { return n + ' ' + (n === 1 ? one : many); }

  function copyText(text, btn) {
    if (typeof MBT.copy === 'function') { MBT.copy(text, btn); return; }
    var done = function () {
      var old = btn.textContent;
      btn.textContent = 'Copied';
      setTimeout(function () { btn.textContent = old; }, 1400);
    };
    try {
      navigator.clipboard.writeText(text).then(done, function () {});
    } catch (e) { /* no clipboard: nothing to do */ }
  }

  /* One shared helper for "This looks wrong" (router and catalog write the
     same flags/<id> doc). Reuse the router's if it defined one first. */
  if (typeof MBT.flag !== 'function' && typeof MBT.cap === 'function') {
    MBT.flag = function (where, text) {
      return Promise.all([MBT.cap('db'), MBT.cap('user')]).then(function (r) {
        var db = r[0], user = r[1];
        if (!db || !user) throw new Error('unavailable');
        return user.id().then(function (uid) {
          if (!uid) throw new Error('unavailable');
          var ref = db.doc('flags/' + uid);
          return ref.get().then(function (snap) {
            var d = snap && snap.exists ? (snap.data() || {}) : {};
            return Array.isArray(d.items) ? d.items.slice() : [];
          }, function () { return []; }).then(function (items) {
            items.push({ where: String(where).slice(0, 120), text: String(text).slice(0, 500), at: new Date().toISOString() });
            if (items.length > 20) items = items.slice(items.length - 20);
            return ref.set({ items: items });
          });
        });
      });
    };
  }

  /* ------------------------------------------------------------------ */
  /* 14 appendix: what a request opens                                   */
  /* ------------------------------------------------------------------ */
  (function appendix() {
    var slide = document.querySelector('.slide[data-id="appendix"]');
    if (!slide) return;
    var sum = $('a-stack-sum');
    var reqBtns = slide.querySelectorAll('.a-req');
    var layers = {};
    Array.prototype.forEach.call(slide.querySelectorAll('.a-layer'), function (li) {
      layers[li.getAttribute('data-a-layer')] = li;
    });
    var DEFAULT_STATE = {
      references: 'On demand', systems: 'On demand', skills: 'When a request calls for one'
    };

    // Curated examples. Each file is shown only if the skill file really links to it.
    var REQS = {
      task: {
        skill: 'pm-story',
        refs: ['references/monday_boards.md'],
        systems: ['systems/owned/marketing-website.md'],
        say: 'the task-writing skill, the board map, and the website system doc'
      },
      seo: {
        skill: 'weekly-seo-report',
        refs: [],
        systems: ['systems/owned/seo-organic-dashboard.md'],
        say: 'the weekly SEO report skill and the SEO dashboard system doc'
      },
      claim: {
        skill: 'demo-reply-fact-check',
        refs: ['references/product/help-center-reference.md'],
        systems: [],
        say: 'the fact-check skill and the product help-center reference'
      }
    };

    function linked(skill, path) {
      var g = data('graph', 'brainGraph');
      if (!g || !g.links) return true;
      for (var i = 0; i < g.links.length; i++) {
        if (g.links[i].s === skill && g.links[i].t === path) return true;
      }
      return false;
    }
    function shortName(p) { return p.replace(/^(references|systems)\//, '').replace(/^owned\//, ''); }

    function setLayer(key, files) {
      var li = layers[key];
      if (!li) return;
      var old = li.querySelector('.a-layer-files');
      if (old) old.parentNode.removeChild(old);
      var state = li.querySelector('.a-layer-state');
      li.classList.remove('is-on', 'is-skip');
      if (files === null) { state.textContent = DEFAULT_STATE[key]; return; }
      if (!files.length) { li.classList.add('is-skip'); state.textContent = 'Not needed'; return; }
      li.classList.add('is-on');
      state.textContent = 'Opened';
      var ul = document.createElement('ul');
      ul.className = 'a-layer-files';
      ul.setAttribute('aria-label', 'Files opened');
      files.forEach(function (f) {
        var item = document.createElement('li');
        item.textContent = f;
        ul.appendChild(item);
      });
      li.appendChild(ul);
    }

    function show(key) {
      Array.prototype.forEach.call(reqBtns, function (b) {
        b.setAttribute('aria-pressed', String(b.getAttribute('data-a-req') === key));
      });
      if (!key) {
        setLayer('references', null); setLayer('systems', null); setLayer('skills', null);
        sum.textContent = 'Right now only the map is open. Pick a request.';
        return;
      }
      var r = REQS[key];
      var refs = r.refs.filter(function (p) { return linked(r.skill, p); }).map(shortName);
      var sys = r.systems.filter(function (p) { return linked(r.skill, p); }).map(shortName);
      setLayer('references', refs);
      setLayer('systems', sys);
      setLayer('skills', [r.skill + '/SKILL.md']);
      var total = Number(facts().skills) || 0;
      var rest = total > 1 ? ' The other ' + (total - 1) + ' skills stay closed.' : '';
      sum.innerHTML = 'Opened: the map, plus ' + esc(r.say) + '.' + esc(rest);
    }

    Array.prototype.forEach.call(reqBtns, function (b) {
      b.addEventListener('click', function () {
        var key = b.getAttribute('data-a-req');
        show(b.getAttribute('aria-pressed') === 'true' ? null : key);
      });
    });
  })();

  /* ------------------------------------------------------------------ */
  /* 15 catalog                                                          */
  /* ------------------------------------------------------------------ */
  (function catalog() {
    var slide = document.querySelector('.slide[data-id="catalog"]');
    if (!slide) return;
    var list = data('catalog', 'skillCatalog') || [];
    var ul = $('a-cat-ul'), input = $('a-cat-q'), countEl = $('a-cat-count'), live = $('a-cat-live');
    var empty = $('a-cat-empty'), filters = $('a-cat-filters'), numEl = $('a-cat-n');
    var scroller = $('a-cat-scroll');

    var total = Number(facts().skills) || list.length;
    numEl.textContent = String(total);

    // Areas: explicit names win, then name patterns, then "Other".
    var AREAS = [
      { key: 'start', label: 'Start here', names: ['marketing-brain', 'marketing-os', 'list-skills', 'team-intro', 'setup'] },
      { key: 'ops', label: 'Ops and CRM', re: /^(hubspot-|mops-|invoice-)/,
        names: ['lifecycle-agent', 'marketing-ops-automation-agent', 'monday-agent', 'pm-story', 'ticket-hygiene', 'launch-webinar', 'slack-agent', 'good-morning', 'p1-p2-followup', 'data-team-request'] },
      { key: 'data', label: 'Data', re: /^(data-agent$|measurement-|gong-|win-loss|mesh-|preop-)/, names: ['vendor-meeting-quality'] },
      { key: 'web', label: 'Website and SEO', re: /^(webflow-|page-|seo-|website-|marketing-website-|organic-|weekly-seo|gsc-)/ },
      { key: 'writing', label: 'Writing', names: ['content-agent', 'nik-voice', 'de-ai', 'critique', 'ste', 'linkedin-best-practices-2026', 'podcast-transcript', 'script-doctor'] },
      { key: 'copy', label: 'Copy templates', re: /copytemplates$/ },
      { key: 'brand', label: 'Brand and design', re: /^riverside-(brand|ux|presentation)/, names: ['impeccable', 'video-project-intake', 'human-review'] },
      { key: 'strategy', label: 'Strategy and sales',
        names: ['marketing-psychology', 'value-proposition-canvas', 'are-we-really-different', 'marketing-council', 'campaign-agent', 'paid-acquisition-agent', 'riverside-product-knowledge', 'demo-reply-fact-check', 'inbound-demo-reply', 'candidate-brief'] },
      { key: 'briefs', label: 'Leader briefs', re: /^nir-/, names: ['chief-of-staff', 'hanan-chief-of-staff', 'growth-marketing-team-tasks', 'raz-ops', 'weekly-1-1s'] },
      { key: 'upkeep', label: 'Upkeep', re: /^(skill-|pr-)/,
        names: ['agent-builder', 'health-check', 'retro', 'curious-intern', 'access-welcome', 'graphify', 'link-triage', 'granola-recipe-builder'] }
    ];
    var OTHER = { key: 'other', label: 'Other' };
    function areaOf(name) {
      var i;
      for (i = 0; i < AREAS.length; i++) if (AREAS[i].names && AREAS[i].names.indexOf(name) > -1) return AREAS[i];
      for (i = 0; i < AREAS.length; i++) if (AREAS[i].re && AREAS[i].re.test(name)) return AREAS[i];
      return OTHER;
    }

    // Person-owned skills (SPEC). MBT.OWNERS from the router wins when present.
    var OWNERS_FALLBACK = {
      'chief-of-staff': 'Nir', 'hanan-chief-of-staff': 'Hanan', 'nir-weekly-report': 'Nir',
      'nir-monthly-report': 'Nir', 'nir-mql-live-report': 'Nir', 'inbound-demo-reply': 'Nir',
      'invoice-board-spend-pulse': 'Nir', 'growth-marketing-team-tasks': 'Nir', 'nik-voice': 'Nir',
      'raz-ops': 'Raz Navon', 'weekly-1-1s': 'Raz Navon', 'p1-p2-followup': 'Hanan',
      'mops-standup': 'Hanan and Jonathan'
    };
    function ownerOf(name) {
      var o = (window.MBT && window.MBT.OWNERS) || OWNERS_FALLBACK;
      return o[name] || '';
    }

    // Trim a frontmatter description to its first plain statement. A few skills
    // describe themselves only by trigger phrases; those get a plain line
    // paraphrased from their own description.
    var PLAIN = {
      'good-morning': 'A daily brief of active monday work, team updates, Slack activity, open risks, and recommended actions.',
      'list-skills': 'An overview of every team skill and how to trigger it, read live from the skills directory.',
      'team-intro': 'Tells you what the Brain knows about you, the team, your projects, and your systems.',
      'setup': 'The interactive wizard that fills a new team context\u2019s template placeholders with real team data.',
      'pm-story': 'Writes, updates, or creates a product story, task, or ticket. The way in for monday tasks, never the board directly.',
      'impeccable': 'Designs, audits, critiques, and polishes a frontend interface: websites, landing pages, dashboards, product UI.'
    };
    function trimDesc(name, d) {
      if (PLAIN[name]) return PLAIN[name];
      var s = String(d || '').replace(DASHES, ', ').replace(/\s+/g, ' ').trim();
      s = s.replace(/^(?:Use this skill|Use)\s+(?:when|whenever)\s+/i, 'When ');
      s = s.replace(/^(?:Use this skill|Use)\s+(?:for|to)\s+/i, 'For ');
      var cut = s.search(/\s(?:Trigger(?:ed)?\b|Triggers\b|Also (?:use|trigger)\b|Use (?:this skill |this |it )?(?:when|whenever|for|any time)\b|ALWAYS\b|Invoke this|NOT\b|Runs\b)/);
      if (cut > 40) s = s.slice(0, cut);
      var dot = s.search(/[.?]\s+[A-Z(]/);
      if (dot > 40) s = s.slice(0, dot + 1);
      s = s.replace(/[\s,;:(-]+$/, '');
      if (s.length > 170) {
        s = s.slice(0, 170);
        s = s.slice(0, s.lastIndexOf(' ')).replace(/[\s,;:(-]+$/, '') + ELL;
      } else if (!/[.?)…]$/.test(s)) {
        s += '.';
      }
      return s;
    }

    var skills = list.map(function (s) {
      var a = areaOf(s.name);
      return { name: s.name, desc: trimDesc(s.name, s.description), full: String(s.description || '').toLowerCase(), area: a };
    }).sort(function (a, b) { return a.name < b.name ? -1 : a.name > b.name ? 1 : 0; });

    var area = 'all';

    // Area filter: chips on wide screens, a select on phones (CSS shows one).
    var counts = {};
    skills.forEach(function (s) { counts[s.area.key] = (counts[s.area.key] || 0) + 1; });
    var areaList = [{ key: 'all', label: 'All' }].concat(AREAS, [OTHER]).filter(function (a) {
      return a.key === 'all' || counts[a.key];
    });
    filters.innerHTML = areaList.map(function (a) {
      var n = a.key === 'all' ? skills.length : counts[a.key];
      return '<button type="button" class="a-fchip" data-area="' + a.key + '" aria-pressed="' + (a.key === 'all') + '">' +
        esc(a.label) + ' <span class="a-fchip-n">' + n + '</span></button>';
    }).join('');
    var selWrap = document.createElement('div');
    selWrap.className = 'a-cat-selwrap';
    selWrap.innerHTML = '<label for="a-cat-sel" class="a-label">Area</label><select id="a-cat-sel" class="a-cat-sel">' +
      areaList.map(function (a) {
        var n = a.key === 'all' ? skills.length : counts[a.key];
        return '<option value="' + a.key + '">' + esc(a.label) + ' (' + n + ')</option>';
      }).join('') + '</select>';
    filters.parentNode.appendChild(selWrap);
    var sel = $('a-cat-sel');

    function setArea(key) {
      area = key;
      Array.prototype.forEach.call(filters.querySelectorAll('.a-fchip'), function (b) {
        b.setAttribute('aria-pressed', String(b.getAttribute('data-area') === key));
      });
      if (sel.value !== key) sel.value = key;
      render(true);
    }
    filters.addEventListener('click', function (e) {
      var b = e.target.closest('.a-fchip');
      if (b) setArea(b.getAttribute('data-area'));
    });
    sel.addEventListener('change', function () { setArea(sel.value); });

    function tokens(q) {
      return q.toLowerCase().replace(/[^a-z0-9 -]/g, ' ').split(/\s+/).filter(function (t) { return t.length > 0; });
    }
    function mark(text, toks) {
      var out = esc(text);
      if (!toks.length) return out;
      var re = new RegExp('(' + toks.map(function (t) {
        return esc(t).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      }).join('|') + ')', 'gi');
      // only mark inside text, never inside an entity
      return out.split(/(&[a-z#0-9]+;)/i).map(function (part) {
        return /^&[a-z#0-9]+;$/i.test(part) ? part : part.replace(re, '<mark>$1</mark>');
      }).join('');
    }
    function score(s, toks, needAll) {
      var sc = 0, hits = 0;
      for (var i = 0; i < toks.length; i++) {
        var t = toks[i], got = false;
        if (s.name.indexOf(t) === 0) { sc += 6; got = true; } else if (s.name.indexOf(t) > -1) { sc += 4; got = true; }
        var at = s.full.indexOf(t), occ = 0;
        while (at > -1 && occ < 3) { occ++; at = s.full.indexOf(t, at + t.length); }
        if (occ) { sc += occ; got = true; }
        if (got) hits++;
        else if (needAll) return 0;
      }
      return hits ? sc + hits * 2 : 0;
    }

    var liveTimer = 0;
    function render(fromFilter) {
      var q = input.value.trim();
      var toks = tokens(q);
      var pool = skills.filter(function (s) { return area === 'all' || s.area.key === area; });
      var shown = pool, partial = false;
      if (toks.length) {
        var scored = pool.map(function (s) { return { s: s, v: score(s, toks, true) }; }).filter(function (x) { return x.v > 0; });
        if (!scored.length) {
          scored = pool.map(function (s) { return { s: s, v: score(s, toks, false) }; }).filter(function (x) { return x.v > 0; });
          partial = scored.length > 0;
        }
        scored.sort(function (a, b) { return b.v - a.v || (a.s.name < b.s.name ? -1 : 1); });
        shown = scored.map(function (x) { return x.s; });
      }
      ul.innerHTML = shown.map(function (s) {
        var own = ownerOf(s.name);
        return '<li class="a-row">' +
          '<div class="a-row-main"><span class="cmd">/' + mark(s.name, toks) + '</span>' +
          '<span class="a-dom">' + esc(s.area.label) + '</span>' +
          (own ? '<span class="a-own">For ' + esc(own) + '</span>' : '') + '</div>' +
          '<p class="a-desc">' + mark(s.desc, toks) + '</p>' +
          '<button type="button" class="btn btn-ghost btn-sm copy-btn a-copy" data-cmd="/' + esc(s.name) + '" aria-label="Copy /' + esc(s.name) + '">Copy</button>' +
          '</li>';
      }).join('');
      empty.hidden = shown.length > 0;
      var where = area === 'all' ? '' : ' in ' + areaList.filter(function (a) { return a.key === area; })[0].label;
      var msg;
      if (!toks.length) msg = area === 'all' ? plural(total, 'skill', 'skills') + ', A to Z' : plural(shown.length, 'skill', 'skills') + where;
      else if (partial) msg = 'No skill matches every word' + where + '. Showing ' + plural(shown.length, 'partial match', 'partial matches') + '.';
      else msg = plural(shown.length, 'skill matches', 'skills match') + ' “' + q + '”' + where;
      if (!shown.length) msg = 'No skill matches' + (q ? ' “' + q + '”' : '') + where + '.';
      countEl.textContent = msg;
      clearTimeout(liveTimer);
      liveTimer = setTimeout(function () { live.textContent = msg; }, fromFilter ? 50 : 450);
      scroller.scrollTop = 0;
    }

    input.addEventListener('input', function () { render(false); });
    ul.addEventListener('click', function (e) {
      var b = e.target.closest('.a-copy');
      if (b) copyText(b.getAttribute('data-cmd'), b);
    });
    render(true);
    live.textContent = '';

    // Owners may be defined by a later-loading script: refresh once on first visit.
    var refreshed = false;
    if (typeof MBT.on === 'function') {
      MBT.on('slide', function (p) {
        if (!refreshed && p && p.id === 'catalog') { refreshed = true; render(true); live.textContent = ''; }
      });
    }

    // "This looks wrong": only when a shared store and a viewer id exist.
    var flagWrap = $('a-cat-flag'), openBtn = $('a-cat-flag-open'), form = $('a-cat-flag-form');
    var ta = $('a-cat-flag-text'), sendBtn = $('a-cat-flag-send'), cancelBtn = $('a-cat-flag-cancel'), flagMsg = $('a-cat-flag-msg');
    function closeForm(focusBack) {
      form.hidden = true;
      openBtn.setAttribute('aria-expanded', 'false');
      if (focusBack) openBtn.focus();
    }
    openBtn.addEventListener('click', function () {
      var open = form.hidden;
      form.hidden = !open;
      openBtn.setAttribute('aria-expanded', String(open));
      if (open) { flagMsg.textContent = ''; ta.focus(); }
    });
    cancelBtn.addEventListener('click', function () { closeForm(true); });
    sendBtn.addEventListener('click', function () {
      var text = ta.value.trim();
      if (!text) { flagMsg.textContent = 'Write a few words first.'; ta.focus(); return; }
      if (typeof MBT.flag !== 'function') { flagMsg.textContent = 'Sending is not available here.'; return; }
      sendBtn.disabled = true;
      var q = input.value.trim();
      MBT.flag('catalog' + (q ? ' (search: ' + q.slice(0, 60) + ')' : ''), text).then(function () {
        ta.value = '';
        closeForm(true);
        flagMsg.textContent = 'Thanks. The trainer’s owner will see it.';
      }, function () {
        flagMsg.textContent = 'That did not send. Try again in a moment.';
      }).then(function () { sendBtn.disabled = false; });
    });
    if (typeof MBT.cap === 'function') {
      Promise.all([MBT.cap('db'), MBT.cap('user')]).then(function (r) {
        if (!r[0] || !r[1]) return null;
        return r[1].id();
      }).then(function (uid) {
        if (uid) flagWrap.hidden = false;
      }).catch(function () {});
    }
  })();

  /* ------------------------------------------------------------------ */
  /* 17 upkeep: step through one change                                  */
  /* ------------------------------------------------------------------ */
  (function upkeep() {
    var slide = document.querySelector('.slide[data-id="upkeep"]');
    if (!slide) return;
    var n = Number(facts().routingN);
    if (n) $('a-up-n').textContent = String(n);
    var btn = $('a-up-play'), label = $('a-up-play-l'), stepEl = $('a-up-step');
    var lanesWrap = slide.querySelector('.a-up-lanes');
    var STEPS = [
      { lane: 'pr', text: 'Step 1 of 3: a pull request changes a skill. The routing check scores it before anyone merges.' },
      { lane: 'merge', text: 'Step 2 of 3: it merges to main. The wiki, the graph, and the doc search rebuild on their own.' },
      { lane: 'people', text: 'Step 3 of 3: someone learns something. /retro turns it into an edit, and the loop starts again.' }
    ];
    var at = -1;
    function paint() {
      Array.prototype.forEach.call(slide.querySelectorAll('.a-up-lane'), function (l) {
        l.classList.toggle('is-lit', at > -1 && at < STEPS.length && l.getAttribute('data-a-lane') === STEPS[at].lane);
      });
      lanesWrap.classList.toggle('is-playing', at > -1 && at < STEPS.length);
      if (at === -1) { label.textContent = 'Walk through one change'; stepEl.textContent = ''; return; }
      stepEl.textContent = STEPS[at].text;
      label.textContent = at === STEPS.length - 1 ? 'Start over' : 'Next step';
    }
    btn.addEventListener('click', function () {
      at = at >= STEPS.length - 1 ? -1 : at + 1;
      paint();
    });
  })();

  /* ------------------------------------------------------------------ */
  /* 18 slack: nothing goes out until you say yes                        */
  /* ------------------------------------------------------------------ */
  (function slack() {
    var slide = document.querySelector('.slide[data-id="slack"]');
    if (!slide) return;
    var yes = $('a-sl-yes'), no = $('a-sl-no'), reset = $('a-sl-reset');
    var sent = $('a-sl-sent'), result = $('a-sl-result'), draft = $('a-sl-draft');
    function finish(didSend) {
      sent.hidden = !didSend;
      draft.classList.add('is-done');
      yes.hidden = true; no.hidden = true; reset.hidden = false;
      result.textContent = didSend
        ? 'Sent, because you said yes. It is now the newest post in the feed, signed like the rest.'
        : 'Held. Nothing was sent, and nothing will be until you say yes.';
      reset.focus();
    }
    yes.addEventListener('click', function () { finish(true); });
    no.addEventListener('click', function () { finish(false); });
    reset.addEventListener('click', function () {
      sent.hidden = true;
      draft.classList.remove('is-done');
      yes.hidden = false; no.hidden = false; reset.hidden = true;
      result.textContent = '';
      yes.focus();
    });
  })();
})();
