/* 60-setup.js: setup checklist (slide "setup"), shared finish helpers.
   Owns ids prefixed f-setup-. Persists MBT.state 'setup' {access, open, connect, verify}. */
(function () {
  'use strict';
  var MBT = window.MBT || {};

  /* Shared helpers for the finish area (61-check.js and 62-commit.js reuse them). */
  var F = window.MBTFinish = window.MBTFinish || {};

  F.state = function (key, fallback) {
    try { return MBT.state && MBT.state.get ? MBT.state.get(key, fallback) : fallback; } catch (e) { return fallback; }
  };
  F.save = function (key, value) {
    try { if (MBT.state && MBT.state.set) MBT.state.set(key, value); } catch (e) { /* in-memory only */ }
  };
  F.announce = function (text) {
    try { if (MBT.announce) MBT.announce(text); } catch (e) { /* no announcer */ }
  };
  F.copy = function (text, btn) {
    if (MBT.copy) { MBT.copy(text, btn); return; }
    var done = function () {
      if (!btn) return;
      var was = btn.textContent;
      btn.textContent = 'Copied';
      setTimeout(function () { btn.textContent = was; }, 1600);
      F.announce('Copied');
    };
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () { F.selectCopy(text); done(); });
        return;
      }
    } catch (e) { /* fall through */ }
    F.selectCopy(text); done();
  };
  F.selectCopy = function (text) {
    try {
      var ta = document.createElement('textarea');
      ta.value = text; ta.setAttribute('readonly', '');
      ta.style.position = 'fixed'; ta.style.opacity = '0'; ta.style.left = '-9999px';
      document.body.appendChild(ta); ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    } catch (e) { /* nothing more to try */ }
  };
  /* Navigate for a data-nav button. The core may already handle [data-nav];
     go only if it did not, so a double handler never double-moves. */
  F.nav = function (target) {
    setTimeout(function () {
      try {
        var cur = MBT.current ? MBT.current() : null;
        if (MBT.go && (!cur || cur.id !== target)) MBT.go(target);
      } catch (e) { /* core not ready */ }
    }, 0);
  };
  F.el = function (tag, attrs, kids) {
    var n = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        var v = attrs[k];
        if (v === null || v === undefined || v === false) return;
        if (k === 'text') n.textContent = v;
        else if (k === 'className') n.className = v;
        else n.setAttribute(k, v === true ? '' : String(v));
      });
    }
    (kids || []).forEach(function (c) {
      if (c === null || c === undefined) return;
      n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    });
    return n;
  };

  /* Copy buttons across all three finish slides (delegated, one listener). */
  document.addEventListener('click', function (e) {
    var b = e.target && e.target.closest ? e.target.closest('[data-f-copy]') : null;
    if (!b) return;
    e.preventDefault();
    F.copy(b.getAttribute('data-f-copy'), b);
  });
  document.addEventListener('click', function (e) {
    var b = e.target && e.target.closest ? e.target.closest('.f-nav[data-nav]') : null;
    if (!b) return;
    F.nav(b.getAttribute('data-nav'));
  });

  /* ---------- setup checklist ---------- */
  var slide = document.querySelector('[data-id="setup"]');
  if (!slide) return;
  var KEYS = ['access', 'open', 'connect', 'verify'];
  var boxes = {};
  KEYS.forEach(function (k) { boxes[k] = document.getElementById('f-setup-' + k); });
  var countEl = document.getElementById('f-setup-count');
  var doneEl = document.getElementById('f-setup-done');
  var lblEl = document.getElementById('f-setup-lbl');
  var bars = slide.querySelectorAll('.f-meter-bar i');

  function read() {
    var s = F.state('setup', null);
    var out = {};
    KEYS.forEach(function (k) { out[k] = !!(s && s[k]); });
    return out;
  }

  function paint(s) {
    var n = 0;
    KEYS.forEach(function (k, i) {
      var on = !!s[k];
      if (on) n++;
      if (boxes[k]) boxes[k].checked = on;
      var li = slide.querySelector('[data-step="' + k + '"]');
      if (li) li.classList.toggle('is-done', on);
    });
    for (var i = 0; i < bars.length; i++) bars[i].classList.toggle('on', i < n);
    if (countEl) countEl.textContent = String(n);
    if (lblEl) lblEl.textContent = n === KEYS.length ? 'All four done' : n ? (KEYS.length - n) + ' to go' : 'Tick each step as you go';
    if (doneEl) doneEl.hidden = n < KEYS.length;
    slide.classList.toggle('f-all-done', n === KEYS.length);
    return n;
  }

  KEYS.forEach(function (k) {
    var box = boxes[k];
    if (!box) return;
    box.addEventListener('change', function () {
      var s = read();
      s[k] = box.checked;
      F.save('setup', s);
      var n = paint(s);
      F.announce(n === KEYS.length ? 'All four setup steps done. You are set up.' : n + ' of 4 setup steps done');
    });
  });

  /* the two doors: a two-tab switch (arrow keys move, Home/End jump) */
  var tabs = [].slice.call(slide.querySelectorAll('.f-door-tab'));
  function selectTab(tab, focus) {
    tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      var panel = document.getElementById(t.getAttribute('aria-controls'));
      if (panel) panel.hidden = !on;
    });
    if (focus) tab.focus();
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { selectTab(t, false); });
    t.addEventListener('keydown', function (e) {
      var j = null;
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') j = (i + 1) % tabs.length;
      else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') j = (i - 1 + tabs.length) % tabs.length;
      else if (e.key === 'Home') j = 0;
      else if (e.key === 'End') j = tabs.length - 1;
      if (j === null) return;
      e.preventDefault();
      e.stopPropagation();
      selectTab(tabs[j], true);
    });
  });

  paint(read());
  if (MBT.on) {
    MBT.on('state', function (p) { if (p && p.key === 'setup') paint(read()); });
    MBT.on('slide', function (p) { if (p && p.id === 'setup') paint(read()); });
  }
})();
