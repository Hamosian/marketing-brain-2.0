/* 30-story.js: the trust story (slides problem, how, receipts, rule, trust).
   Build facts, the MQL prediction, the layer trace, and two checkpoints.
   Checkpoint results stay in memory only (not in MBT.state). */
(function () {
  'use strict';

  var IDS = ['problem', 'how', 'receipts', 'rule', 'trust'];
  var results = {};

  function mbt() { return window.MBT || null; }
  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function slide(id) { return document.querySelector('.slide[data-id="' + id + '"]'); }
  function focusSoon(el) {
    if (!el) return;
    setTimeout(function () { try { el.focus({ preventScroll: false }); } catch (e) { el.focus(); } }, 30);
  }
  function readJSON(id, fallback) {
    var el = document.getElementById(id);
    if (!el) return fallback;
    try { return JSON.parse(el.textContent); } catch (e) { return fallback; }
  }

  /* ---------- build facts into [data-fact] ---------- */
  function facts() {
    var M = mbt();
    if (M && M.data && M.data.facts) return M.data.facts;
    return readJSON('buildFacts', {}) || {};
  }
  function fillFacts() {
    var f = facts();
    IDS.forEach(function (id) {
      var s = slide(id);
      if (!s) return;
      $$('[data-fact]', s).forEach(function (el) {
        var v = f[el.getAttribute('data-fact')];
        if (v === undefined || v === null || v === '') return;
        if (typeof v === 'string' && v.indexOf('__') === 0) return; /* unfilled build marker */
        el.textContent = String(v);
      });
    });
  }

  /* ---------- 03 problem: prediction then reveal ---------- */
  function initProblem() {
    var s = slide('problem');
    if (!s) return;
    var opts = $$('[data-s-guess]', s);
    var reveal = $('#s-reveal', s);
    var verdict = $('#s-verdict', s);
    var again = $('[data-s-reset="guess"]', s);
    if (!opts.length || !reveal || !verdict) return;

    opts.forEach(function (btn) {
      btn.addEventListener('click', function () {
        opts.forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
        verdict.textContent = btn.getAttribute('data-s-fb') || '';
        reveal.hidden = false;
        focusSoon(verdict);
      });
    });
    if (again) {
      again.addEventListener('click', function () {
        opts.forEach(function (b) { b.setAttribute('aria-pressed', 'false'); });
        verdict.textContent = '';
        reveal.hidden = true;
        focusSoon(opts[0]);
      });
    }
  }

  /* ---------- 04 how: send a request through the layers ---------- */
  var TRACES = {
    owner: {
      files: ['references/team.md'],
      skills: [],
      text: 'The map points to the team roster. One lookup opens, references/team.md, and the answer comes back: Raz Navon, Head of Paid Acquisition. No skill needed.'
    },
    banner: {
      files: ['systems/owned/trendemon.md', 'references/monday_boards.md'],
      skills: ['pm-story'],
      text: 'The map has a rule for this: banners are Marketing Ops work, served by Trendemon, not website work. The Trendemon guide and the board IDs open, then /pm-story drafts the ticket for MOPs Tasks and checks it with you.'
    },
    deck: {
      files: [],
      skills: ['riverside-presentation', 'riverside-brand-guidelines'],
      text: 'The map says branded work always loads Brand’s guidelines first. Two skills load: /riverside-presentation builds the deck, and /riverside-brand-guidelines brings the colors and type.'
    }
  };

  function catalogNames() {
    var M = mbt();
    var cat = (M && M.data && M.data.catalog) || readJSON('skillCatalog', []) || [];
    var names = [];
    for (var i = 0; i < cat.length; i++) {
      if (cat[i] && cat[i].name) names.push(String(cat[i].name));
    }
    return names;
  }

  function initHow() {
    var s = slide('how');
    if (!s) return;
    var reqs = $$('[data-s-req]', s);
    var trace = $('#s-trace', s);
    var dotsBox = $('#s-dots', s);
    var litCount = $('#s-dots-lit', s);
    var litNames = $('#s-dots-names', s);
    var layerLook = $('[data-s-layer="look"]', s);
    var layerSkill = $('[data-s-layer="skill"]', s);
    var files = $$('[data-s-file]', s);
    if (!reqs.length) return;

    /* one dot per skill in the repo, generated from the catalog */
    var dots = {};
    if (dotsBox) {
      var names = catalogNames();
      var n = names.length || Number(facts().skills) || 0;
      var frag = document.createDocumentFragment();
      for (var i = 0; i < n; i++) {
        var d = document.createElement('span');
        d.className = 's-dot';
        if (names[i]) dots[names[i]] = d;
        frag.appendChild(d);
      }
      dotsBox.appendChild(frag);
    }

    function apply(key, announce) {
      var t = TRACES[key];
      if (!t) return;
      reqs.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-s-req') === key ? 'true' : 'false'); });
      files.forEach(function (f) { f.classList.toggle('is-lit', t.files.indexOf(f.getAttribute('data-s-file')) !== -1); });
      if (layerLook) layerLook.classList.toggle('is-lit', t.files.length > 0);
      if (layerSkill) layerSkill.classList.toggle('is-lit', t.skills.length > 0);
      Object.keys(dots).forEach(function (name) { dots[name].classList.toggle('is-lit', t.skills.indexOf(name) !== -1); });
      if (litCount) litCount.textContent = t.skills.length ? String(t.skills.length) : 'None';
      if (litNames) litNames.textContent = t.skills.length ? ': /' + t.skills.join(', /') : '';
      if (trace && announce !== false) trace.textContent = t.text;
    }

    reqs.forEach(function (b) {
      b.addEventListener('click', function () { apply(b.getAttribute('data-s-req')); });
    });
    /* initial state matches the markup; set without re-announcing */
    apply('owner', false);
  }

  /* ---------- checkpoints (rule, trust) ---------- */
  function initCheckpoint(cp) {
    var key = cp.getAttribute('data-s-cp') || 'cp';
    var opts = $$('.s-cp-opt', cp);
    var fb = $('.s-cp-fb', cp);
    var retry = $('.s-cp-retry', cp);
    if (!opts.length || !fb) return;

    function reset(focusFirst) {
      cp.classList.remove('is-answered', 'is-correct');
      opts.forEach(function (b) {
        b.disabled = false;
        b.setAttribute('aria-pressed', 'false');
        b.classList.remove('is-right', 'is-wrong');
      });
      fb.textContent = '';
      fb.className = 's-cp-fb';
      fb.hidden = true;
      if (retry) retry.hidden = true;
      if (focusFirst) focusSoon(opts[0]);
    }

    opts.forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (cp.classList.contains('is-answered')) return;
        var right = btn.getAttribute('data-s-correct') === 'true';
        opts.forEach(function (b) {
          var chosen = b === btn;
          b.setAttribute('aria-pressed', chosen ? 'true' : 'false');
          b.classList.toggle('is-right', chosen && right);
          b.classList.toggle('is-wrong', chosen && !right);
          if (!chosen) b.disabled = true;
        });
        cp.classList.add('is-answered');
        if (right) cp.classList.add('is-correct');
        fb.className = 's-cp-fb ' + (right ? 'is-right' : 'is-wrong');
        fb.textContent = btn.getAttribute('data-s-fb') || '';
        fb.hidden = false;
        if (retry) retry.hidden = right;
        results[key] = { correct: right, tries: ((results[key] && results[key].tries) || 0) + 1 };
        focusSoon(fb);
      });
    });
    if (retry) retry.addEventListener('click', function () { reset(true); });
  }

  function init() {
    fillFacts();
    initProblem();
    initHow();
    ['rule', 'trust'].forEach(function (id) {
      var s = slide(id);
      if (s) $$('[data-s-cp]', s).forEach(initCheckpoint);
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
