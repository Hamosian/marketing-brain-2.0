/* ==========================================================================
   00-core.js: window.MBT, the contract every other script codes against.
   Slides registry, navigation, events, per-viewer state, data blocks,
   capabilities, a11y, overview, presenter mode, follow the presenter,
   and the cover's live example. Runs first; exposes MBT synchronously.
   ========================================================================== */
(function () {
  'use strict';

  var doc = document;
  var win = window;
  var MBT = win.MBT = win.MBT || {};

  var STORE_KEY = 'mbt3';
  var MIRROR_KEYS = ['role', 'exp', 'far', 'check', 'practice', 'commit', 'ran', 'setup'];
  var hasOwn = Object.prototype.hasOwnProperty;
  function each(list, fn) { Array.prototype.forEach.call(list || [], fn); }
  function $(id) { return doc.getElementById(id); }
  function clone(v) {
    if (v === null || typeof v !== 'object') return v;
    try { return JSON.parse(JSON.stringify(v)); } catch (e) { return v; }
  }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function iso() { return new Date().toISOString(); }
  function safe(p) { try { return Promise.resolve(p).catch(function () { return null; }); } catch (e) { return Promise.resolve(null); } }
  function warn(msg, e) { try { if (win.console && console.warn) console.warn('[MBT] ' + msg, e || ''); } catch (x) { /* no console */ } }

  /* Small DOM builder: text always goes in through textContent. */
  function h(tag, attrs, kids) {
    var el = doc.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        var v = attrs[k];
        if (v === null || v === undefined || v === false) return;
        if (k === 'text') el.textContent = String(v);
        else if (k === 'class') el.className = v;
        else if (k.slice(0, 2) === 'on' && typeof v === 'function') el.addEventListener(k.slice(2), v);
        else el.setAttribute(k, v === true ? '' : String(v));
      });
    }
    (kids || []).forEach(function (c) {
      if (c === null || c === undefined || c === false) return;
      el.appendChild(typeof c === 'string' ? doc.createTextNode(c) : c);
    });
    return el;
  }

  /* ---------------------------------------------------------------- events */
  var handlers = {};
  function on(evt, fn) {
    if (typeof fn !== 'function') return function () {};
    (handlers[evt] = handlers[evt] || []).push(fn);
    return function off() {
      var list = handlers[evt] || [];
      var i = list.indexOf(fn);
      if (i >= 0) list.splice(i, 1);
    };
  }
  function emit(evt, payload) {
    (handlers[evt] || []).slice().forEach(function (fn) {
      try { fn(payload); } catch (e) { warn('a "' + evt + '" listener failed', e); }
    });
  }

  /* ----------------------------------------------------------------- state */
  var mem = {};
  var lsOk = false;
  try {
    var raw = win.localStorage.getItem(STORE_KEY);
    lsOk = true;
    if (raw) {
      var parsed = JSON.parse(raw);
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) mem = parsed;
    }
  } catch (e) { lsOk = false; }
  function persist() {
    if (!lsOk) return;
    try { win.localStorage.setItem(STORE_KEY, JSON.stringify(mem)); } catch (e) { /* storage full or blocked: memory keeps working */ }
  }
  var state = {
    get: function (key, fallback) {
      return hasOwn.call(mem, key) && mem[key] !== undefined ? clone(mem[key]) : fallback;
    },
    set: function (key, value) {
      if (JSON.stringify(mem[key]) === JSON.stringify(value)) return;
      if (value === undefined || value === null) delete mem[key];
      else mem[key] = clone(value);
      persist();
      emit('state', { key: key, value: clone(value) });
      scheduleMirror();
    },
    all: function () { return clone(mem); },
    clear: function () {
      mem = {};
      persist();
      emit('state', { key: '*', value: null });
    }
  };

  /* -------------------------------------------------------------- announce */
  var announcer = $('announcer');
  var announceT = null;
  function announce(text) {
    if (!announcer) return;
    clearTimeout(announceT);
    announcer.textContent = '';
    announceT = setTimeout(function () { announcer.textContent = String(text || ''); }, 60);
  }

  /* ------------------------------------------------------------------ data */
  function readJSON(id, fallback) {
    var el = $(id);
    if (!el) return fallback;
    try {
      var v = JSON.parse(el.textContent || '');
      return v === null || v === undefined ? fallback : v;
    } catch (e) { return fallback; }
  }
  var graph = readJSON('brainGraph', null);
  if (!graph || !Array.isArray(graph.nodes) || !Array.isArray(graph.links)) graph = { nodes: [], links: [] };
  var catalog = readJSON('skillCatalog', []);
  var cases = readJSON('routingCases', []);
  var facts = readJSON('buildFacts', {});
  var data = {
    catalog: Array.isArray(catalog) ? catalog : [],
    graph: graph,
    cases: Array.isArray(cases) ? cases : [],
    facts: facts && typeof facts === 'object' && !Array.isArray(facts) ? facts : {}
  };

  function fillFacts(root) {
    each((root || doc).querySelectorAll('[data-fact]'), function (el) {
      var v = data.facts[el.getAttribute('data-fact')];
      if (v !== undefined && v !== null && v !== '') el.textContent = String(v);
    });
  }

  /* ---------------------------------------------------------- capabilities */
  var capCache = {};
  function cap(name) {
    if (capCache[name]) return capCache[name];
    var p = new Promise(function (resolve) {
      var c = win.claude;
      if (!c || typeof c.use !== 'function') { resolve(null); return; }
      var done = false;
      var timer = setTimeout(function () { if (!done) { done = true; resolve(null); } }, 10000);
      function finish(v) { if (done) return; done = true; clearTimeout(timer); resolve(v || null); }
      try { Promise.resolve(c.use(name)).then(finish, function () { finish(null); }); }
      catch (e) { finish(null); }
    });
    capCache[name] = p;
    return p;
  }

  /* ----------------------------------------------------------------- roles */
  function role() {
    var R = MBT.ROLES || {};
    var k = state.get('role', null);
    return (k && R[k]) || R.any || null;
  }

  /* ------------------------------------------------------------------ copy */
  function flash(btn, ok) {
    if (!btn || !btn.classList) return;
    var label = btn.querySelector('[data-copy-label]');
    if (btn.__mbtOrig === undefined || btn.__mbtOrig === null) {
      btn.__mbtOrig = label ? label.textContent : btn.innerHTML;
      btn.__mbtW = btn.style.minWidth;
      btn.style.minWidth = btn.offsetWidth + 'px';
    }
    clearTimeout(btn.__mbtT);
    btn.classList.toggle('is-copied', !!ok);
    var msg = ok ? 'Copied' : 'Select and copy';
    if (label) label.textContent = msg; else btn.textContent = msg;
    btn.__mbtT = setTimeout(function () {
      btn.classList.remove('is-copied');
      if (label) label.textContent = btn.__mbtOrig; else btn.innerHTML = btn.__mbtOrig;
      btn.style.minWidth = btn.__mbtW || '';
      btn.__mbtOrig = null;
    }, 1800);
  }
  function copy(text, btn) {
    text = String(text === null || text === undefined ? '' : text);
    var short = text.length > 90 ? text.slice(0, 90) + '...' : text;
    function done(ok) {
      flash(btn, ok);
      announce(ok ? 'Copied: ' + short : 'Copy is blocked here. The text is selected: press Command C or Control C.');
      return ok;
    }
    function fallback() {
      var ta = h('textarea', { readonly: true, 'aria-hidden': 'true', tabindex: '-1' });
      ta.value = text;
      ta.style.cssText = 'position:fixed;top:0;left:0;width:1px;height:1px;opacity:0;pointer-events:none;';
      doc.body.appendChild(ta);
      var ok = false;
      try { ta.select(); ta.setSelectionRange(0, text.length); ok = doc.execCommand('copy'); } catch (e) { ok = false; }
      if (ok) ta.remove(); else setTimeout(function () { ta.remove(); }, 8000);
      if (btn && btn.focus) { try { btn.focus({ preventScroll: true }); } catch (e) { btn.focus(); } }
      return done(ok);
    }
    try {
      if (win.navigator.clipboard && win.navigator.clipboard.writeText) {
        return win.navigator.clipboard.writeText(text).then(function () { return done(true); }, fallback);
      }
    } catch (e) { /* fall through */ }
    return Promise.resolve(fallback());
  }

  /* ---------------------------------------------------------- reduced motion */
  var mq = win.matchMedia ? win.matchMedia('(prefers-reduced-motion: reduce)') : null;
  MBT.reduced = !!(mq && mq.matches);
  if (mq) {
    var onMotion = function (e) { MBT.reduced = !!e.matches; emit('motion', MBT.reduced); };
    if (mq.addEventListener) mq.addEventListener('change', onMotion);
    else if (mq.addListener) mq.addListener(onMotion);
  }

  /* -------------------------------------------------------- slides registry */
  var body = doc.body;
  var deck = $('deck');
  var slides = [];
  var byId = {};
  each(doc.querySelectorAll('#deck > section.slide[data-id]'), function (el, i) {
    var hd = el.querySelector('h1, h2');
    var s = {
      index: i,
      id: el.getAttribute('data-id'),
      title: el.getAttribute('data-title') || (hd ? hd.textContent.trim() : 'Slide ' + (i + 1)),
      part: el.getAttribute('data-part') || 'core',
      el: el
    };
    slides.push(s);
    byId[s.id] = s;
  });
  var coreList = slides.filter(function (s) { return s.part === 'core'; });
  var CORE_N = coreList.length;
  function coreNum(s) { return coreList.indexOf(s) + 1; }
  function heading(s) { return s && s.el.querySelector('h1, h2'); }

  slides.forEach(function (s) {
    var el = s.el;
    if (el.hasAttribute('aria-labelledby')) {
      el.setAttribute('data-labelledby', el.getAttribute('aria-labelledby'));
      el.removeAttribute('aria-labelledby');
    }
    el.setAttribute('role', 'group');
    el.setAttribute('aria-roledescription', 'slide');
    el.setAttribute('aria-label', (s.index + 1) + ' of ' + slides.length + ': ' + s.title);
    el.setAttribute('tabindex', '-1');
    var hd = heading(s);
    if (hd && !hd.hasAttribute('tabindex')) hd.setAttribute('tabindex', '-1');
  });

  function indexFromHash(hash) {
    var v = String(hash || '').replace(/^#/, '');
    if (!v) return -1;
    try { v = decodeURIComponent(v); } catch (e) { /* keep raw */ }
    if (byId[v]) return byId[v].index;
    var m = /^slide-(\d+)$/.exec(v);
    if (m) {
      var n = parseInt(m[1], 10) - 1;
      if (n >= 0 && n < slides.length) return n;
    }
    return -1;
  }
  function resolveTarget(t) {
    if (typeof t === 'number') return Math.floor(t);
    if (typeof t === 'string') {
      if (byId[t]) return byId[t].index;
      if (/^\d+$/.test(t)) return parseInt(t, 10);
    }
    if (t && typeof t === 'object' && typeof t.index === 'number') return t.index;
    return -1;
  }

  function setActiveDom(i) {
    slides.forEach(function (s, j) {
      var el = s.el;
      if (j === i) {
        el.hidden = false;
        el.removeAttribute('inert');
        el.inert = false;
        el.classList.add('active');
      } else {
        el.classList.remove('active');
        el.hidden = true;
        el.setAttribute('inert', '');
        el.inert = true;
      }
    });
  }

  var cur = indexFromHash(win.location.hash);
  if (cur < 0) cur = 0;
  if (slides.length) setActiveDom(cur);
  if (deck) deck.classList.add('is-ready');

  /* ------------------------------------------------------------ navigation */
  var prevBtn = $('prevBtn');
  var nextBtn = $('nextBtn');
  var dotsEl = $('dots');
  var pfill = $('pfill');
  var cnum = $('cnum');
  var ctotal = $('ctotal');
  var dots = [];
  var navDuring = false;
  var seenExtra = {};

  function current() {
    var s = slides[cur];
    return s ? { index: s.index, id: s.id, el: s.el, title: s.title, part: s.part } : { index: -1, id: null, el: null };
  }

  function focusHeading(s) {
    var hd = heading(s) || s.el;
    try { hd.focus({ preventScroll: true }); } catch (e) { hd.focus(); }
  }

  function go(target, opts) {
    opts = opts || {};
    var i = resolveTarget(target);
    if (isNaN(i) || i < 0 || i >= slides.length) return false;
    navDuring = true;
    setTimeout(function () { navDuring = false; }, 0);
    if (i === cur && !opts.force) return false;
    var from = cur;
    var fromEl = slides[from] ? slides[from].el : null;
    var active = doc.activeElement;
    /* a focused Back or Next that is about to be disabled at either end drops focus too */
    var navEdge = (active === prevBtn && i === 0) || (active === nextBtn && i === slides.length - 1);
    var lostFocus = !active || active === body || navEdge || (fromEl && fromEl.contains(active)) ||
      !!(active.closest && active.closest('dialog'));
    cur = i;
    setActiveDom(i);
    slides[i].el.scrollTop = 0;
    commit(from, opts);
    if (opts.focus === 'heading' || (lostFocus && opts.focus !== 'keep')) focusHeading(slides[i]);
    return true;
  }
  function next(opts) { return go(Math.min(cur + 1, slides.length - 1), opts); }
  function prev(opts) { return go(Math.max(cur - 1, 0), opts); }

  /* Everything that depends on the current slide, painted unconditionally. */
  function commit(from, opts) {
    opts = opts || {};
    var s = slides[cur];
    if (!s) return;
    if (s.part === 'core') {
      if (cur > state.get('far', 0)) state.set('far', cur);
    } else {
      seenExtra[cur] = true;
    }
    render();
    try { win.history.replaceState(null, '', '#' + s.id); } catch (e) { /* sandboxed frame */ }
    if (!opts.initial) announce('Slide ' + (cur + 1) + ' of ' + slides.length + ': ' + s.title);
    updateResume();
    updatePresenter();
    liveWrite();
    emit('slide', { index: s.index, id: s.id, el: s.el, from: from });
    if (s.id === 'cover') coverEnter(); else coverLeave();
    setTimeout(function () { updatePrimary(); updateScrollCue(); }, 350);
  }

  function render() {
    var s = slides[cur];
    var far = state.get('far', 0);
    body.setAttribute('data-slide', s.id);
    body.setAttribute('data-part', s.part);
    body.setAttribute('data-tone', s.el.classList.contains('tone-light') ? 'light' : 'dark');
    updatePrimary();
    updateScrollCue();
    if (s.part === 'core') {
      var n = coreNum(s);
      if (cnum) cnum.textContent = pad(n);
      if (ctotal) ctotal.textContent = ' / ' + pad(CORE_N);
      if (pfill) pfill.style.width = (CORE_N ? (n / CORE_N) * 100 : 0) + '%';
    } else {
      if (cnum) cnum.textContent = s.part === 'end' ? 'About' : 'Appendix';
      if (ctotal) ctotal.textContent = '';
      if (pfill) pfill.style.width = '100%';
    }
    if (prevBtn) prevBtn.disabled = cur === 0;
    if (nextBtn) {
      nextBtn.disabled = cur === slides.length - 1;
      var lbl = nextBtn.querySelector('.nav-label');
      var lastCore = coreList.length ? coreList[coreList.length - 1].index : -1;
      if (lbl) lbl.textContent = cur === lastCore && cur < slides.length - 1 ? 'Under the hood' : 'Next';
    }
    dots.forEach(function (d) {
      var i = +d.getAttribute('data-index');
      var sl = slides[i];
      var isCur = i === cur;
      if (isCur) d.setAttribute('aria-current', 'step'); else d.removeAttribute('aria-current');
      d.classList.toggle('seen', !isCur && (sl.part === 'core' ? i <= far : !!seenExtra[i]));
    });
  }

  /* One primary per view: when the slide shows its own filled action, Next steps back.
     Re-checked after every click, so a primary that appears later (practice feedback) counts. */
  function updatePrimary() {
    var s = slides[cur];
    if (!s) return;
    var prim = null;
    each(s.el.querySelectorAll('.btn-primary:not(.btn-sm)'), function (b) {
      if (!prim && b.offsetParent !== null && !b.closest('[hidden]')) prim = b;
    });
    body.classList.toggle('slide-has-primary', !!prim);
  }
  /* Scroll cue: fade the bottom edge while a slide has more content below. */
  function updateScrollCue() {
    var s = slides[cur];
    if (!s) return;
    var el = s.el;
    var more = el.scrollHeight - el.clientHeight - el.scrollTop > 40;
    el.classList.toggle('is-scrollable', more);
  }
  doc.addEventListener('click', function () { setTimeout(function () { updatePrimary(); updateScrollCue(); }, 0); });
  slides.forEach(function (s) {
    s.el.addEventListener('scroll', function () { if (s.index === cur) updateScrollCue(); }, { passive: true });
  });
  win.addEventListener('resize', function () { updateScrollCue(); });

  function buildDots() {
    if (!dotsEl) return;
    dotsEl.textContent = '';
    dots = [];
    var groups = [
      { label: 'Core', test: function (s) { return s.part === 'core'; } },
      { label: 'Under the hood', test: function (s) { return s.part !== 'core'; } }
    ];
    var first = true;
    groups.forEach(function (g) {
      var items = slides.filter(g.test);
      if (!items.length) return;
      if (!first) dotsEl.appendChild(h('span', { class: 'dot-sep', 'aria-hidden': 'true' }));
      first = false;
      var wrap = h('div', { class: 'dot-group', role: 'group', 'aria-label': g.label });
      items.forEach(function (s) {
        var label = s.part === 'core' ? coreNum(s) + ' of ' + CORE_N + ': ' + s.title : s.title;
        var d = h('button', {
          type: 'button',
          class: 'dot' + (s.part === 'core' ? '' : ' is-extra'),
          'data-index': s.index,
          'data-nav': String(s.index),
          'data-label': s.title,
          'aria-label': label,
          tabindex: '-1'
        });
        wrap.appendChild(d);
        dots.push(d);
      });
      dotsEl.appendChild(wrap);
    });
    dotsEl.addEventListener('keydown', function (e) {
      var i = dots.indexOf(doc.activeElement);
      if (i < 0) return;
      var j = -1;
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') j = Math.min(i + 1, dots.length - 1);
      else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') j = Math.max(i - 1, 0);
      else if (e.key === 'Home') j = 0;
      else if (e.key === 'End') j = dots.length - 1;
      if (j < 0) return;
      e.preventDefault();
      dots[j].focus();
    });
  }

  /* Dots are a pointer shortcut and stay out of the Tab order (the Overview,
     O, is the keyboard and screen reader route to any slide). Once a dot has
     focus, arrow keys, Home and End move between dots and Enter opens one. */

  /* Delegated slide navigation: data-nav="next|prev|<data-id>|<index>" (or data-go).
     A bare data-nav is a marker only. If the element's own handler already
     navigated during this click, the core does nothing. */
  doc.addEventListener('click', function (e) {
    var b = e.target && e.target.closest ? e.target.closest('[data-nav], [data-go]') : null;
    if (!b || b.disabled || b.getAttribute('aria-disabled') === 'true') return;
    var inSlide = b.closest('.slide');
    if (inSlide && !inSlide.classList.contains('active')) return;
    var v = b.getAttribute('data-go') || b.getAttribute('data-nav');
    if (b.hasAttribute('data-reset')) { e.preventDefault(); askReset(b); return; }
    if (!v || e.defaultPrevented || navDuring) return;
    if (v === 'next') next();
    else if (v === 'prev') prev();
    else go(v);
  });

  /* ------------------------------------------------------------- keyboard */
  var WIDGET = 'button, a[href], input, textarea, select, summary, [contenteditable], [role="radio"], [role="tab"], ' +
    '[role="option"], [role="slider"], [role="switch"], [role="checkbox"], [role="menuitem"], [role="listbox"], ' +
    '[role="textbox"], [role="spinbutton"], canvas[tabindex], [data-keys], [tabindex]:not([tabindex="-1"])';

  function scrollSlide(dir, amount) {
    var el = slides[cur] && slides[cur].el;
    if (!el) return false;
    var max = el.scrollHeight - el.clientHeight;
    if (max <= 4) return false;
    if (dir > 0 && el.scrollTop >= max - 2) return false;
    if (dir < 0 && el.scrollTop <= 2) return false;
    var by = amount || Math.round(el.clientHeight * 0.85);
    try { el.scrollBy({ top: dir * by, behavior: MBT.reduced ? 'auto' : 'smooth' }); } catch (e) { el.scrollTop += dir * by; }
    return true;
  }

  doc.addEventListener('keydown', function (e) {
    if (e.defaultPrevented || e.isComposing || e.ctrlKey || e.metaKey || e.altKey) return;
    var key = e.key;
    if (blanked) {
      if (key === 'b' || key === 'B' || key === 'Escape' || key === '.') { e.preventDefault(); setBlank(false); }
      return;
    }
    if (ov && ov.open) return;
    var t = e.target && e.target.nodeType === 1 ? e.target : doc.activeElement || body;
    if (t.closest('dialog, #dots, .presenter')) return;
    var chrome = !!t.closest('.topbar, .nav');
    var widget = t.closest(WIDGET);
    var surface = !widget;
    if (!surface && !chrome) return;           /* an in-slide control owns its keys */
    var shift = e.shiftKey;

    if (key === 'ArrowRight' && !shift) { e.preventDefault(); next(); return; }
    if (key === 'ArrowLeft' && !shift) { e.preventDefault(); prev(); return; }
    if (key === 'PageDown' || (key === ' ' && surface && !shift)) {
      e.preventDefault();
      if (!scrollSlide(1)) next();
      return;
    }
    if (key === 'PageUp' || (key === ' ' && surface && shift)) {
      e.preventDefault();
      if (!scrollSlide(-1)) prev();
      return;
    }
    if ((key === 'ArrowDown' || key === 'ArrowUp') && surface) {
      var slideFocused = t.closest('.slide');
      if (!slideFocused) { e.preventDefault(); scrollSlide(key === 'ArrowDown' ? 1 : -1, 72); }
      return;
    }
    if (key === 'Home' && !shift) { e.preventDefault(); go(0); return; }
    if (key === 'End' && !shift) { e.preventDefault(); go(slides.length - 1); return; }
    if (key === 'o' || key === 'O') { e.preventDefault(); openOverview(); return; }
    if (key === 'p' || key === 'P') { e.preventDefault(); setPresent(!presenting); return; }
    if ((key === 'b' || key === 'B' || key === '.') && presenting) { e.preventDefault(); setBlank(true); return; }
  });

  /* ---------------------------------------------------------------- swipe */
  function inHScroller(el) {
    while (el && el !== deck && el.nodeType === 1) {
      if (el.scrollWidth > el.clientWidth + 2) {
        var ox = win.getComputedStyle(el).overflowX;
        if (ox === 'auto' || ox === 'scroll') return true;
      }
      el = el.parentElement;
    }
    return false;
  }
  var touch = null;
  if (deck) {
    deck.addEventListener('touchstart', function (e) {
      touch = null;
      if (!e.touches || e.touches.length !== 1) return;
      var t = e.target;
      if (!t || !t.closest || t.closest('input, textarea, select, canvas, [contenteditable], [data-noswipe], dialog') || inHScroller(t)) return;
      touch = { x: e.touches[0].clientX, y: e.touches[0].clientY, at: Date.now() };
    }, { passive: true });
    deck.addEventListener('touchend', function (e) {
      if (!touch || !e.changedTouches || !e.changedTouches.length) { touch = null; return; }
      var c = e.changedTouches[0];
      var dx = c.clientX - touch.x;
      var dy = c.clientY - touch.y;
      var dt = Date.now() - touch.at;
      touch = null;
      if (dt > 900 || Math.abs(dx) < 60 || Math.abs(dx) < Math.abs(dy) * 1.6) return;
      if (dx < 0) next(); else prev();
    }, { passive: true });
    deck.addEventListener('touchcancel', function () { touch = null; }, { passive: true });
  }

  win.addEventListener('hashchange', function () {
    var i = indexFromHash(win.location.hash);
    if (i >= 0 && i !== cur) go(i);
  });

  var skip = doc.querySelector('.skip-link');
  if (skip) skip.addEventListener('click', function (e) { e.preventDefault(); focusHeading(slides[cur]); });

  /* -------------------------------------------------------------- overview */
  var ov = $('overview');
  var ovBtn = $('overviewBtn');
  var ovCells = [];
  function buildOverview() {
    if (!ov) return;
    ov.textContent = '';
    ovCells = [];
    function group(id, title, note, test) {
      var items = slides.filter(test);
      if (!items.length) return null;
      var list = h('ol', { class: 'ov-list' });
      items.forEach(function (s) {
        var num = s.part === 'core' ? pad(coreNum(s)) : '';
        var cell = h('button', { type: 'button', class: 'ov-cell', 'data-nav': s.id, 'data-index': s.index }, [
          h('span', { class: 'ov-num' + (s.part === 'core' ? '' : ' is-extra'), 'aria-hidden': 'true', text: num }),
          h('span', { class: 'ov-title', text: s.title }),
          h('span', { class: 'ov-tag' })
        ]);
        ovCells.push(cell);
        list.appendChild(h('li', null, [cell]));
      });
      return h('section', { class: 'ov-group', 'aria-labelledby': id }, [
        h('h3', { id: id, text: title }),
        h('p', { text: note }),
        list
      ]);
    }
    var closeBtn = h('button', { type: 'button', class: 'btn btn-ghost btn-sm', text: 'Close' });
    closeBtn.addEventListener('click', function () { closeOverview(true); });
    ov.appendChild(h('div', { class: 'ov-head' }, [h('h2', { id: 'overviewTitle', text: 'All slides' }), closeBtn]));
    ov.appendChild(h('div', { class: 'ov-body' }, [
      group('c-ov-core', 'Core', 'About 15 minutes, in order.', function (s) { return s.part === 'core'; }),
      group('c-ov-extra', 'Under the hood', 'Optional. Open any of these, in any order.', function (s) { return s.part !== 'core'; })
    ]));
    function keyHint(keys, text) {
      return h('span', null, keys.map(function (k) { return h('kbd', { class: 'kbd', text: k }); }).concat([text]));
    }
    ov.appendChild(h('div', { class: 'ov-foot' }, [
      h('div', { class: 'ov-keys', 'aria-label': 'Keyboard shortcuts' }, [
        keyHint(['←', '→'], 'move'),
        keyHint(['O'], 'this overview'),
        keyHint(['P'], 'presenter mode'),
        keyHint(['B'], 'blank screen while presenting')
      ]),
      h('div', { class: 'c-reset-wrap' }, [
        h('button', { type: 'button', class: 'btn btn-ghost btn-sm', 'data-nav': 'cover', 'data-reset': '1', text: 'Clear my progress' })
      ])
    ]));
    ov.addEventListener('click', function (e) {
      var cell = e.target.closest ? e.target.closest('.ov-cell') : null;
      if (cell) {
        e.preventDefault();
        var target = +cell.getAttribute('data-index');
        closeOverview(false);
        if (target === cur) focusHeading(slides[cur]); else go(target, { focus: 'heading' });
        return;
      }
      if (e.target === ov) {
        var r = ov.getBoundingClientRect();
        if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) closeOverview(true);
      }
    });
    // Keep Tab inside the dialog (native showModal lets focus reach the browser chrome).
    ov.addEventListener('keydown', function (e) {
      if (e.key !== 'Tab' || e.altKey || e.ctrlKey || e.metaKey) return;
      var f = [].slice.call(ov.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'))
        .filter(function (x) { return !x.disabled && x.offsetParent !== null; });
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1], a = document.activeElement;
      if (e.shiftKey && (a === first || a === ov)) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && a === last) { e.preventDefault(); first.focus(); }
    });
    ov.addEventListener('close', function () {
      if (ov.__restore !== false && ovBtn) { try { ovBtn.focus({ preventScroll: true }); } catch (e) { ovBtn.focus(); } }
      ov.__restore = true;
    });
  }
  function openOverview() {
    if (!ov) return;
    if (ov.open) { closeOverview(true); return; }
    var far = state.get('far', 0);
    ovCells.forEach(function (c) {
      var i = +c.getAttribute('data-index');
      var isCur = i === cur;
      if (isCur) c.setAttribute('aria-current', 'true'); else c.removeAttribute('aria-current');
      c.classList.toggle('seen', slides[i].part === 'core' ? i <= far : !!seenExtra[i]);
      c.querySelector('.ov-tag').textContent = isCur ? 'You are here' : '';
    });
    ov.__restore = true;
    try { ov.showModal(); } catch (e) { ov.setAttribute('open', ''); }
    var target = ov.querySelector('.ov-cell[aria-current="true"]') || ovCells[0];
    if (target) target.focus();
  }
  function closeOverview(restore) {
    if (!ov || !ov.open) return;
    ov.__restore = restore !== false;
    try { ov.close(); } catch (e) { ov.removeAttribute('open'); }
  }
  if (ovBtn) ovBtn.addEventListener('click', openOverview);

  /* ------------------------------------------------------------ start over */
  /* Clearing progress takes two steps: the first press asks, the second clears. */
  var RESET_FLAG = 'mbt3-cleared';
  function askReset(btn) {
    if (btn.__mbtConfirm) { startOver(); return; }
    btn.__mbtConfirm = true;
    btn.__mbtLabel = btn.textContent;
    var q = h('span', { class: 'c-reset-q', text: 'Clear your saved progress?' });
    var cancel = h('button', { type: 'button', class: 'btn btn-ghost' + (btn.classList.contains('btn-sm') ? ' btn-sm' : ''), text: 'Cancel' });
    function revert() {
      btn.__mbtConfirm = false;
      btn.textContent = btn.__mbtLabel;
      q.remove();
      cancel.remove();
    }
    cancel.addEventListener('click', function () {
      revert();
      try { btn.focus({ preventScroll: true }); } catch (e) { btn.focus(); }
      announce('Kept your progress.');
    });
    btn.textContent = 'Yes, clear it';
    btn.parentNode.insertBefore(q, btn);
    if (btn.nextSibling) btn.parentNode.insertBefore(cancel, btn.nextSibling); else btn.parentNode.appendChild(cancel);
    announce('Clear your saved progress? This removes your check score, your pick and your setup ticks. Choose Yes, clear it, or Cancel.');
  }

  var resetting = false;
  function startOver() {
    if (resetting) return;
    resetting = true;
    state.clear();
    try { win.sessionStorage.setItem(RESET_FLAG, '1'); } catch (e) { /* blocked storage: the reload still works */ }
    announce('Progress cleared. Starting over.');
    var finish = function () {
      try {
        win.history.replaceState(null, '', '#cover');
        win.location.reload();
      } catch (e) {
        resetting = false;
        go(0, { focus: 'heading' });
      }
    };
    var t = setTimeout(finish, 1500);
    mirrorNow().then(function () { clearTimeout(t); finish(); });
  }

  /* ------------------------------------------------------------- presenter */
  var presentBtn = $('presentBtn');
  var pr = $('presenter');
  var presenting = false;
  var startAt = 0;
  var timerId = null;
  var blanked = false;
  var prEls = {};
  var blankEl = h('div', { class: 'c-blank', id: 'c-blank', hidden: true }, [
    h('p', { class: 'sr-only', text: 'Screen blanked. Press B or Escape to return.' })
  ]);
  blankEl.addEventListener('click', function () { setBlank(false); });
  body.appendChild(blankEl);

  function buildPresenter() {
    if (!pr) return;
    pr.textContent = '';
    prEls.timer = h('span', { class: 'pr-timer', 'aria-label': 'Elapsed time', text: '00:00' });
    prEls.min = h('button', { type: 'button', class: 'pr-btn', 'aria-expanded': 'true', 'aria-controls': 'c-pr-body', text: 'Hide notes' });
    var reset = h('button', { type: 'button', class: 'pr-btn', 'aria-label': 'Reset timer', text: 'Reset' });
    var exit = h('button', { type: 'button', class: 'pr-btn', text: 'Exit' });
    reset.addEventListener('click', function () { startAt = Date.now(); tick(); });
    exit.addEventListener('click', function () { setPresent(false); if (presentBtn) presentBtn.focus(); });
    prEls.min.addEventListener('click', function () {
      var min = !pr.classList.contains('is-min');
      pr.classList.toggle('is-min', min);
      prEls.min.setAttribute('aria-expanded', String(!min));
      prEls.min.textContent = min ? 'Show notes' : 'Hide notes';
    });
    prEls.pos = h('p', { class: 'pr-label' });
    prEls.title = h('h3');
    prEls.notes = h('p', { class: 'pr-notes' });
    prEls.next = h('p');
    pr.appendChild(h('div', { class: 'pr-head' }, [h('span', { class: 'pr-title', text: 'Presenter' }), prEls.timer, reset, prEls.min, exit]));
    pr.appendChild(h('div', { class: 'pr-body', id: 'c-pr-body' }, [
      h('div', { class: 'pr-now' }, [prEls.pos, prEls.title, prEls.notes]),
      h('div', { class: 'pr-next' }, [h('p', { class: 'pr-label', text: 'Next' }), prEls.next]),
      h('p', { class: 'pr-hint' }, [
        h('span', null, [h('kbd', { class: 'kbd', text: 'B' }), ' blanks the screen']),
        h('span', null, [h('kbd', { class: 'kbd', text: 'P' }), ' exits']),
        h('span', { text: 'Nothing advances on its own.' })
      ])
    ]));
  }
  function tick() {
    if (!prEls.timer) return;
    var s = Math.max(0, Math.floor((Date.now() - startAt) / 1000));
    prEls.timer.textContent = pad(Math.floor(s / 60)) + ':' + pad(s % 60);
  }
  function updatePresenter() {
    if (!presenting || !prEls.title) return;
    var s = slides[cur];
    var n = slides[cur + 1];
    prEls.pos.textContent = s.part === 'core' ? 'Now: ' + pad(coreNum(s)) + ' of ' + pad(CORE_N) : (s.part === 'end' ? 'Now: the end' : 'Now: appendix');
    prEls.title.textContent = s.title;
    var notes = s.el.querySelector('aside.notes, .notes');
    prEls.notes.textContent = notes ? notes.textContent.replace(/\s+/g, ' ').trim() : 'No notes for this slide.';
    prEls.next.textContent = n ? n.title : 'That was the last slide.';
  }
  function setPresent(onOff) {
    presenting = !!onOff;
    if (presentBtn) presentBtn.setAttribute('aria-pressed', String(presenting));
    if (pr) pr.hidden = !presenting;
    body.classList.toggle('is-presenting', presenting);
    clearInterval(timerId);
    if (presenting) {
      startAt = Date.now();
      tick();
      timerId = setInterval(tick, 1000);
      updatePresenter();
      live.lastWritten = null;
      liveWrite();
      announce('Presenter mode on. Notes are in the panel. B blanks the screen.');
    } else {
      setBlank(false);
      announce('Presenter mode off.');
    }
    state.set('present', presenting);
    updateFollowPill();
  }
  function setBlank(onOff) {
    blanked = !!onOff && presenting;
    blankEl.hidden = !blanked;
    if (blanked) announce('Screen blanked. Press B or Escape to return.');
  }
  if (presentBtn) presentBtn.addEventListener('click', function () { setPresent(!presenting); });

  /* ------------------------------------------- follow the presenter (db) */
  var followPill = $('followPill');
  var live = { db: null, canEdit: false, doc: null, following: false, writeT: null, lastWritten: null, writing: false, pending: false, staleT: null };
  var FRESH_MS = 10 * 60 * 1000;
  function isFresh(d) {
    var t = d && Date.parse(d.at);
    return !!t && Date.now() - t < FRESH_MS;
  }
  function setFollowLabel() {
    if (!followPill) return;
    var lg = followPill.querySelector('.fp-long');
    var sh = followPill.querySelector('.fp-short');
    if (lg) lg.textContent = live.following ? 'Following the presenter' : 'Follow the presenter';
    if (sh) sh.textContent = live.following ? 'Following' : 'Follow';
    followPill.setAttribute('aria-pressed', String(live.following));
  }
  function updateFollowPill() {
    if (!followPill) return;
    var show = !!live.doc && !presenting && (live.following || isFresh(live.doc));
    if (!show && live.following) live.following = false;
    followPill.hidden = !show;
    setFollowLabel();
  }
  function followNow() {
    if (live.following && live.doc && !presenting && byId[live.doc.slide] && byId[live.doc.slide].index !== cur) {
      go(live.doc.slide, { focus: 'keep' });
    }
  }
  if (followPill) {
    followPill.addEventListener('click', function () {
      live.following = !live.following;
      setFollowLabel();
      announce(live.following ? 'Following the presenter.' : 'Stopped following the presenter.');
      followNow();
    });
  }
  function subscribeLive(db) {
    live.db = db;
    try {
      db.doc('live/state').onSnapshot(function (snap) {
        var d = snap && snap.exists ? snap.data() : null;
        live.doc = d && typeof d.slide === 'string' ? { slide: d.slide, at: d.at } : null;
        updateFollowPill();
        followNow();
        if (live.doc && !live.staleT) live.staleT = setInterval(updateFollowPill, 60000);
      }, function () { updateFollowPill(); });
    } catch (e) { warn('live/state subscription failed', e); }
  }
  function liveWrite() {
    if (!presenting || !live.db || !live.canEdit) return;
    clearTimeout(live.writeT);
    live.writeT = setTimeout(function () {
      var id = slides[cur] && slides[cur].id;
      if (!id || id === live.lastWritten) return;
      if (live.writing) { live.pending = true; return; }
      live.writing = true;
      safe(Promise.resolve().then(function () { return live.db.doc('live/state').set({ slide: id, at: iso() }); }).then(function () {
        live.lastWritten = id;
      }, function (e) {
        if (e && e.code === 'invalid_argument') live.canEdit = false;
      })).then(function () {
        live.writing = false;
        if (live.pending) { live.pending = false; liveWrite(); }
      });
    }, 300);
  }

  /* ------------------------------ private progress mirror (db + user) */
  var mirror = { ref: null, ready: false, last: null, writing: false, pending: false, t: null };
  function pickMirror() {
    var out = {};
    MIRROR_KEYS.forEach(function (k) { if (hasOwn.call(mem, k)) out[k] = mem[k]; });
    return out;
  }
  function scheduleMirror() {
    if (!mirror.ready || !mirror.ref) return;
    clearTimeout(mirror.t);
    mirror.t = setTimeout(mirrorNow, 1500);
  }
  function mirrorNow() {
    clearTimeout(mirror.t);
    if (!mirror.ready || !mirror.ref) return Promise.resolve();
    var st = pickMirror();
    var sig = JSON.stringify(st);
    if (sig === mirror.last) return Promise.resolve();
    if (mirror.writing) { mirror.pending = true; return Promise.resolve(); }
    mirror.writing = true;
    return safe(Promise.resolve().then(function () { return mirror.ref.set({ state: st, updatedAt: iso() }); }).then(function () {
      mirror.last = sig;
    }, function (e) {
      if (e && (e.code === 'invalid_argument' || e.code === 'not_granted' || e.code === 'revoked')) mirror.ref = null;
    })).then(function () {
      mirror.writing = false;
      if (mirror.pending) { mirror.pending = false; scheduleMirror(); }
    });
  }
  function initMirror(db, user) {
    safe(user.id && user.id()).then(function (uid) {
      if (!uid) return;
      try { mirror.ref = db.doc('data/users/' + uid + '/state'); } catch (e) { return; }
      safe(mirror.ref.get()).then(function (snap) {
        var remote = snap && snap.exists && snap.data() ? snap.data().state : null;
        if (remote && typeof remote === 'object') {
          var changed = [];
          MIRROR_KEYS.forEach(function (k) {
            if (!hasOwn.call(remote, k) || remote[k] === null || remote[k] === undefined) return;
            if (k === 'far') {
              var f = Math.max(+remote.far || 0, +mem.far || 0);
              if (f !== (+mem.far || 0)) { mem.far = f; changed.push(k); }
            } else if (!hasOwn.call(mem, k)) {
              mem[k] = remote[k];
              changed.push(k);
            }
          });
          if (changed.length) {
            persist();
            changed.forEach(function (k) { emit('state', { key: k, value: clone(mem[k]) }); });
            render();
            updateResume();
          }
          mirror.last = JSON.stringify(remote);
        }
        mirror.ready = true;
        scheduleMirror();
      });
    });
  }

  function initCaps() {
    var pDb = cap('db');
    var pUser = cap('user');
    var pSample = cap('sample');
    pDb.then(function (db) { if (db) { subscribeLive(db); liveWrite(); } });
    pUser.then(function (user) {
      if (!user || typeof user.canEdit !== 'function') return;
      safe(user.canEdit()).then(function (v) { live.canEdit = !!v; liveWrite(); });
    });
    Promise.all([pDb, pUser]).then(function (r) { if (r[0] && r[1]) initMirror(r[0], r[1]); });
    MBT.capsReady = Promise.all([pDb, pUser, pSample]).then(function (r) {
      var caps = { db: r[0], user: r[1], sample: r[2] };
      MBT.caps = caps;
      emit('caps', caps);
      return caps;
    });
  }

  /* ---------------------------------------------------- cover: resume slot */
  function updateResume() {
    var btn = $('c-resume');
    if (!btn) return;
    var far = state.get('far', 0);
    var s = slides[far];
    var show = slides[cur] && slides[cur].id === 'cover' && far > 2 && s && s.part === 'core' && far !== cur;
    btn.hidden = !show;
    if (show) {
      btn.setAttribute('data-nav', s.id);
      var t = $('c-resume-title');
      if (t) t.textContent = s.title;
    }
    if (slides[cur] && slides[cur].id === 'cover') render();
  }

  /* ------------------------------------------- cover: live terminal example */
  var term = $('c-term');
  var termTimers = [];
  var termPlayed = false;
  function termClear() { termTimers.forEach(clearTimeout); termTimers = []; }
  function termLater(fn, ms) { termTimers.push(setTimeout(fn, ms)); }
  function termSettle() {
    if (!term) return;
    termClear();
    term.classList.remove('is-typing', 'is-playing');
    each(term.querySelectorAll('.c-step'), function (s) { s.classList.add('on'); });
  }
  function termPlay() {
    if (!term) return;
    termClear();
    if (MBT.reduced) { termSettle(); return; }
    var full = term.querySelector('.c-full');
    var typed = term.querySelector('.c-typed');
    var steps = term.querySelectorAll('.c-step');
    if (!full || !typed) { termSettle(); return; }
    var text = full.textContent;
    typed.textContent = '';
    each(steps, function (s) { s.classList.remove('on'); });
    term.classList.add('is-typing', 'is-playing');
    var i = 0;
    function type() {
      typed.textContent = text.slice(0, i);
      if (i < text.length) {
        i += 1;
        termLater(type, 42 + Math.round(Math.random() * 38));
      } else {
        termLater(function () { term.classList.remove('is-typing'); reveal(0); }, 420);
      }
    }
    function reveal(k) {
      if (k >= steps.length) { termLater(function () { term.classList.remove('is-playing'); }, 450); return; }
      steps[k].classList.add('on');
      termLater(function () { reveal(k + 1); }, k === 0 ? 700 : 380);
    }
    termLater(type, 650);
  }
  function coverEnter() {
    var rp = $('c-replay');
    if (rp) rp.hidden = MBT.reduced;
    if (!termPlayed) { termPlayed = true; termPlay(); }
  }
  function coverLeave() { termSettle(); }
  var replayBtn = $('c-replay');
  if (replayBtn) replayBtn.addEventListener('click', function () { termPlay(); });
  on('motion', function (reduced) { if (reduced) termSettle(); var rp = $('c-replay'); if (rp) rp.hidden = reduced; });

  /* -------------------------------------------------------------- public */
  MBT.slides = slides.map(function (s) { return { index: s.index, id: s.id, title: s.title, part: s.part, el: s.el }; });
  MBT.go = go;
  MBT.next = function () { return next(); };
  MBT.prev = function () { return prev(); };
  MBT.current = current;
  MBT.on = on;
  MBT.emit = emit;
  MBT.state = state;
  MBT.announce = announce;
  MBT.data = data;
  MBT.cap = cap;
  MBT.role = role;
  MBT.copy = copy;
  MBT.h = h;
  MBT.refresh = function () { if (slides[cur]) render(); };
  MBT.present = function (v) { setPresent(v === undefined ? !presenting : !!v); };
  MBT.overview = openOverview;
  MBT.startOver = startOver;

  /* ---------------------------------------------------------------- boot */
  function boot() {
    if (!slides.length) return;
    buildDots();
    buildOverview();
    buildPresenter();
    fillFacts(doc);
    commit(-1, { initial: true });
    if (state.get('present', false)) setPresent(true);
    initCaps();
    var cleared = false;
    try { cleared = win.sessionStorage.getItem(RESET_FLAG) === '1'; win.sessionStorage.removeItem(RESET_FLAG); } catch (e) { cleared = false; }
    if (cleared && slides[cur]) {
      var note = $('c-cleared');
      if (note && slides[cur].id === 'cover') note.hidden = false;
      focusHeading(slides[cur]);
      setTimeout(function () { announce('Progress cleared. You are starting fresh.'); }, 300);
    }
  }
  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', boot);
  else setTimeout(boot, 0);
})();
