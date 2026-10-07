/* 61-check.js: final check (slide "check"). Six situations not asked earlier in the deck, per-option feedback,
   pass at 5 of 6, missed items can be retried. Saves MBT.state 'check' {score, total, passed}.
   Answers stay in memory only. */
(function () {
  'use strict';
  var MBT = window.MBT || {};
  var F = window.MBTFinish;
  var slide = document.querySelector('[data-id="check"]');
  if (!slide || !F) return;

  var PASS = 5;
  var ITEMS = [
    {
      id: 'vague',
      ask: 'Paid spend is up, signups are flat, and you are not sure where to start.',
      q: 'Where do you take it?',
      answer: 'mb',
      opts: [
        { k: 'mb', label: '/marketing-brain', fb: 'A vague ask that spans paid, the site, and the funnel is what the top-level router is for. It works out which skills to pull in.' },
        { k: 'paid', label: '/paid-acquisition-agent', fb: 'It owns spend and campaign health, but that is one piece. You do not know yet whether the problem is paid, the site, or the funnel. Start at /marketing-brain and let it route.' },
        { k: 'riv', label: '/rivermind:ask', fb: 'Rivermind answers a specific data question. Here you do not know which question to ask yet, and the ask spans several systems. That is /marketing-brain.' },
        { k: 'story', label: '/pm-story', fb: 'That files a ticket for Marketing Ops or Web. Nobody knows what the work is yet. Investigate first with /marketing-brain.' }
      ]
    },
    {
      id: 'deck',
      ask: 'Brand asks you for a six-slide recap deck in the Riverside look.',
      q: 'Which skill builds it?',
      answer: 'pres',
      opts: [
        { k: 'pres', label: '/riverside-presentation', fb: 'It builds the .pptx itself, in the official Riverside layouts, colors and logo placement.' },
        { k: 'brand', label: '/riverside-brand-guidelines', fb: 'Close. That is where the brand rules live, and the deck skill already applies them. To get an actual deck, use /riverside-presentation.' },
        { k: 'content', label: '/content-agent', fb: 'It drafts the words for emails and announcements. The slides themselves come from /riverside-presentation.' },
        { k: 'imp', label: '/impeccable', fb: 'That is a design pass on a page or dashboard that is already built. A new deck is /riverside-presentation.' }
      ]
    },
    {
      id: 'banner',
      ask: 'Growth wants a banner across the top of the homepage announcing next week\'s webinar.',
      q: 'How does it get ticketed?',
      answer: 'mops',
      opts: [
        { k: 'mops', label: '/pm-story, on Marketing Ops Tasks as Messaging', fb: 'Banners, top bars and popups are served by Trendemon, so they are Marketing Ops work, even when the ask names the homepage.' },
        { k: 'web', label: '/pm-story, on Website Dev', fb: 'The right skill, the wrong board. On-site messages like banners run through Trendemon, which Marketing Ops owns. File it on Marketing Ops Tasks as Messaging.' },
        { k: 'build', label: '/page-build', fb: 'That builds or updates a Webflow page from a ticket. A banner is not a page change, and it still needs a ticket first: /pm-story on Marketing Ops Tasks.' },
        { k: 'hyg', label: '/ticket-hygiene', fb: 'That audits tickets that already exist. A new request is one ticket, written with /pm-story on Marketing Ops Tasks.' }
      ]
    },
    {
      id: 'plan',
      ask: 'A lead asks which plans include AI show notes. You have not written a reply yet, you just want the answer.',
      q: 'Where do you ask?',
      answer: 'rpk',
      opts: [
        { k: 'rpk', label: '/riverside-product-knowledge', fb: 'How a feature works and which plan it is on comes from the Help Center, and this skill reads it for you.' },
        { k: 'fact', label: '/demo-reply-fact-check', fb: 'Close. It checks the claims in a draft you have already written. For a plain question about a feature, ask /riverside-product-knowledge.' },
        { k: 'hs', label: '/hubspot-agent', fb: 'HubSpot knows what this lead has, not what each plan includes. That is /riverside-product-knowledge.' },
        { k: 'riv', label: '/rivermind:ask', fb: 'Rivermind answers data questions. What a plan includes is a product fact from the Help Center: /riverside-product-knowledge.' }
      ]
    },
    {
      id: 'dash',
      ask: 'Your channel needs a dashboard that does not exist yet.',
      q: 'Where do you ask for it?',
      answer: 'dtr',
      opts: [
        { k: 'dtr', label: '/data-team-request', fb: 'It files on the Data Team\'s own board with their request types and priority scale, and it can check the status for you later.' },
        { k: 'story', label: '/pm-story', fb: 'Close, and a common mix-up. /pm-story files tickets for Marketing Ops and Web on our boards. The Data Team has its own board, and /data-team-request knows it.' },
        { k: 'org', label: '/organic-dashboard', fb: 'That refreshes one existing dashboard, the organic analytics one for SEO. A new build from the Data Team is /data-team-request.' },
        { k: 'data', label: '/data-agent', fb: 'It queries data for you. It does not ask the Data Team to build anything. That is /data-team-request.' }
      ]
    },
    {
      id: 'write',
      ask: 'The Brain proposes updating 40 HubSpot contacts and asks you to confirm.',
      q: 'What do you do?',
      answer: 'read',
      opts: [
        { k: 'yes', label: 'Say yes. It already checked', fb: 'The pause is there so a person looks. Read what will change first, then approve it or narrow it.' },
        { k: 'read', label: 'Read what it will change, then approve or narrow it', fb: 'HubSpot, Monday, and Slack writes wait for your yes for exactly this. Check the contacts and the fields, then approve all, some, or none.' },
        { k: 'never', label: 'Cancel. Never let it write to HubSpot', fb: 'Writes with your yes are how it is meant to work. Read the plan, then approve or narrow it.' },
        { k: 'hand', label: 'Make the 40 updates by hand instead', fb: 'That throws away the time it saves. Read the plan it shows you, then approve or narrow it.' }
      ]
    }
  ];
  var BY_ID = {};
  ITEMS.forEach(function (it) { BY_ID[it.id] = it; });

  var body = document.getElementById('f-quiz-body');
  var fb = document.getElementById('f-quiz-fb');
  var actions = document.getElementById('f-quiz-actions');
  var pos = document.getElementById('f-quiz-pos');
  var pips = document.getElementById('f-pips');
  var el = F.el;

  var run = null; /* {results:{id:bool}, queue:[ids], at:int, round:int, answered:bool} */

  function shuffle(a) {
    var b = a.slice();
    for (var i = b.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = b[i]; b[i] = b[j]; b[j] = t;
    }
    return b;
  }
  function score() {
    var n = 0;
    ITEMS.forEach(function (it) { if (run && run.results[it.id] === true) n++; });
    return n;
  }
  function clear(n) { while (n && n.firstChild) n.removeChild(n.firstChild); }
  function isCmd(label) { return /^\/[a-z]/.test(label); }
  function labelNode(label) {
    /* Render any /command inside the label as a code token, the rest as text. */
    var span = el('span', { className: 'f-opt-label' });
    var parts = label.split(/(\/[a-z][a-z0-9:-]*)/);
    parts.forEach(function (p) {
      if (!p) return;
      if (/^\/[a-z]/.test(p)) span.appendChild(el('code', { className: 'f-opt-cmd', text: p }));
      else span.appendChild(document.createTextNode(p));
    });
    return span;
  }
  function textWithCmds(text) {
    var frag = document.createDocumentFragment();
    text.split(/(\/[a-z][a-z0-9:-]*)/).forEach(function (p) {
      if (!p) return;
      if (/^\/[a-z]/.test(p)) frag.appendChild(el('code', { className: 'cmd', text: p }));
      else frag.appendChild(document.createTextNode(p));
    });
    return frag;
  }

  function paintPips() {
    clear(pips);
    ITEMS.forEach(function (it, i) {
      var r = run ? run.results[it.id] : undefined;
      var cur = run && run.queue[run.at] === it.id && run.at < run.queue.length;
      var cls = 'f-pip' + (r === true ? ' is-right' : r === false ? ' is-wrong' : '') + (cur ? ' is-current' : '');
      var sr = 'Situation ' + (i + 1) + ': ' + (r === true ? 'right' : r === false ? 'missed' : cur ? 'current' : 'not answered yet');
      pips.appendChild(el('li', { className: cls }, [el('span', { className: 'sr-only', text: sr })]));
    });
  }

  function renderItem(focus) {
    var it = BY_ID[run.queue[run.at]];
    run.answered = false;
    clear(body); clear(fb); clear(actions);
    fb.className = 'f-quiz-fb';
    var idx = ITEMS.indexOf(it) + 1;
    pos.textContent = run.round > 1
      ? 'Retry ' + (run.at + 1) + ' of ' + run.queue.length + ' (situation ' + idx + ')'
      : 'Situation ' + idx + ' of ' + ITEMS.length;

    var ask = el('p', { className: 'f-q-ask', id: 'f-q-ask', tabindex: '-1' }, [textWithCmds(it.ask)]);
    var q = el('p', { className: 'f-q-q', id: 'f-q-q', text: it.q });
    var group = el('div', { className: 'f-opts', role: 'group', 'aria-labelledby': 'f-q-ask f-q-q' });
    shuffle(it.opts).forEach(function (o) {
      var b = el('button', { type: 'button', className: 'f-opt' + (isCmd(o.label) ? ' is-cmd' : ''), 'data-k': o.k }, [
        el('span', { className: 'f-opt-mark', 'aria-hidden': 'true' }),
        labelNode(o.label),
        el('span', { className: 'sr-only f-opt-sr' })
      ]);
      b.addEventListener('click', function () { answer(it, o, b); });
      group.appendChild(b);
    });
    body.appendChild(el('div', { className: 'f-q' }, [ask, q, group]));
    paintPips();
    if (focus) { try { ask.focus({ preventScroll: true }); } catch (e) { ask.focus(); } }
  }

  function answer(it, o, btn) {
    if (run.answered) return;
    run.answered = true;
    var right = o.k === it.answer;
    run.results[it.id] = right;
    var correct = null;
    it.opts.forEach(function (x) { if (x.k === it.answer) correct = x; });
    var buttons = body.querySelectorAll('.f-opt');
    for (var i = 0; i < buttons.length; i++) {
      var b = buttons[i];
      var k = b.getAttribute('data-k');
      b.setAttribute('aria-disabled', 'true');
      b.classList.add('is-locked');
      var sr = b.querySelector('.f-opt-sr');
      if (k === it.answer) { b.classList.add('is-right'); if (sr) sr.textContent = right ? ', your answer, right' : ', the right answer'; }
      if (b === btn && !right) { b.classList.add('is-wrong'); if (sr) sr.textContent = ', your answer, not this one'; }
    }
    clear(fb);
    fb.className = 'f-quiz-fb is-shown ' + (right ? 'is-right' : 'is-wrong');
    var head = el('p', { className: 'f-fb-head', tabindex: '-1' }, [
      el('span', { className: 'f-fb-icon', 'aria-hidden': 'true' }),
      right ? 'Right.' : 'Not this one.'
    ]);
    var text = el('p', { className: 'f-fb-text' }, [textWithCmds(o.fb)]);
    fb.appendChild(head);
    fb.appendChild(text);
    if (!right && correct) {
      fb.appendChild(el('p', { className: 'f-fb-best' }, [el('span', { className: 'f-fb-best-k', text: 'The move: ' }), textWithCmds(correct.label)]));
    }
    paintPips();
    clear(actions);
    var last = run.at >= run.queue.length - 1;
    var next = el('button', { type: 'button', className: 'btn btn-ghost f-next', text: last ? 'See your result' : 'Next situation' });
    next.addEventListener('click', function () {
      if (last) summary(true);
      else { run.at++; renderItem(true); }
    });
    actions.appendChild(next);
    try { head.focus({ preventScroll: true }); } catch (e) { head.focus(); }
    /* keep the next step in view without moving focus off the feedback */
    try { next.scrollIntoView({ block: 'nearest', behavior: MBT.reduced ? 'auto' : 'smooth' }); } catch (e) { /* old browsers */ }
  }

  function summary(fresh) {
    var s = run ? score() : 0;
    var passed = s >= PASS;
    if (fresh) {
      F.save('check', { score: s, total: ITEMS.length, passed: passed });
    }
    renderSummary(s, passed, run ? missed() : []);
  }
  function missed() {
    return ITEMS.filter(function (it) { return run.results[it.id] !== true; }).map(function (it) { return it.id; });
  }

  function renderSummary(s, passed, miss, fromSaved) {
    clear(body); clear(fb); clear(actions);
    fb.className = 'f-quiz-fb';
    pos.textContent = 'Result';
    if (run) run.at = run.queue.length;
    paintPips();
    var big = el('p', { className: 'f-score', tabindex: '-1' }, [
      el('span', { className: 'f-score-n', text: String(s) }),
      el('span', { className: 'f-score-of', text: ' of ' + ITEMS.length })
    ]);
    var msg;
    if (passed) {
      msg = s === ITEMS.length
        ? 'A clean pass. You know where requests go, and what to do when the Brain pushes back.'
        : 'A pass. You know where requests go. Retry the one you missed if you want the full set.';
    } else {
      msg = 'Not yet. Five is a pass. Read the notes on the ones you missed, then retry just those.';
    }
    if (fromSaved) msg = passed ? 'You passed this earlier with ' + s + ' of ' + ITEMS.length + '. Retake it any time.' : 'Last time you got ' + s + ' of ' + ITEMS.length + '. Five is a pass.';
    body.appendChild(el('div', { className: 'f-result' + (passed ? ' is-pass' : '') }, [
      el('div', { className: 'f-seal', 'aria-hidden': 'true' }, [svgSeal(passed)]),
      el('div', { className: 'f-result-copy' }, [big, el('p', { className: 'f-result-msg', text: msg })])
    ]));

    if (miss.length && !fromSaved) {
      var retry = el('button', { type: 'button', className: 'btn ' + (passed ? 'btn-ghost' : 'btn-primary') + ' f-retry', text: miss.length === 1 ? 'Retry the one you missed' : 'Retry the ' + miss.length + ' you missed' });
      retry.addEventListener('click', function () {
        run.queue = shuffle(miss); run.at = 0; run.round++;
        renderItem(true);
      });
      actions.appendChild(retry);
    }
    if (fromSaved || passed) {
      var again = el('button', { type: 'button', className: 'btn btn-ghost f-restart', text: fromSaved ? 'Retake the check' : 'Take it again' });
      again.addEventListener('click', function () { start(true); });
      actions.appendChild(again);
    }
    if (passed) {
      actions.appendChild(el('button', { type: 'button', className: 'btn btn-ghost f-nav f-to-commit', 'data-nav': 'commit', text: 'Next: pick your command' }));
    }
    F.announce(fromSaved ? msg : 'Result: ' + s + ' of ' + ITEMS.length + '. ' + (passed ? 'Pass.' : 'Not yet a pass.'));
    if (!fromSaved) { try { big.focus({ preventScroll: true }); } catch (e) { big.focus(); } }
  }

  function svgSeal(passed) {
    var ns = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('viewBox', '0 0 64 64');
    var c = document.createElementNS(ns, 'circle');
    c.setAttribute('cx', '32'); c.setAttribute('cy', '32'); c.setAttribute('r', '28');
    c.setAttribute('class', 'f-seal-ring');
    svg.appendChild(c);
    var p = document.createElementNS(ns, 'path');
    p.setAttribute('class', 'f-seal-mark');
    p.setAttribute('d', passed ? 'M20 33l8 8 16-18' : 'M22 32h20');
    svg.appendChild(p);
    return svg;
  }

  function start(focus) {
    run = { results: {}, queue: ITEMS.map(function (it) { return it.id; }), at: 0, round: 1, answered: false };
    renderItem(focus);
  }

  /* First paint: show a saved result if there is one, else the first situation. */
  var saved = F.state('check', null);
  if (saved && typeof saved.score === 'number') {
    run = null;
    renderSummary(saved.score, !!saved.passed, [], true);
  } else {
    start(false);
  }

  if (MBT.on) {
    MBT.on('state', function (p) {
      /* "Start over" in the overview clears state: reset to a fresh run. */
      if (!p || p.key !== 'check') return;
      if ((p.value === null || p.value === undefined) && !run) { start(false); return; }
      /* a saved result restored after load (private db mirror) while no answer is in progress */
      var fresh = !run || (run.round === 1 && run.at === 0 && !run.answered);
      if (p.value && typeof p.value.score === 'number' && fresh) {
        run = null;
        renderSummary(p.value.score, !!p.value.passed, [], true);
      }
    });
  }
})();
