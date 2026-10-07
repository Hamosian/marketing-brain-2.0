/* 20-path.js: the "Pick your path" slide (data-id="path").
   Team -> function -> experience, each an accessible radiogroup (arrows move focus, Space/Enter select).
   Persists 'role' and 'exp' through MBT.state and emits MBT.emit('role', roleObj) when the role changes.
   A returning viewer sees a one-line summary with a "Change path" button instead of the full form. */
(function () {
  'use strict';
  var MBT = window.MBT = window.MBT || {};
  var root = document.querySelector('.slide[data-id="path"]');
  if (!root) return;

  var ROLES = MBT.ROLES || {};
  var TEAMS = MBT.TEAMS || [];
  var EXP = MBT.EXP || {};
  var memory = {};

  function $(id) { return document.getElementById(id); }
  function getState(k) {
    try { if (MBT.state && MBT.state.get) return MBT.state.get(k, null); } catch (e) { /* fall through */ }
    return memory.hasOwnProperty(k) ? memory[k] : null;
  }
  var writing = false;
  function setState(k, v) {
    memory[k] = v;
    writing = true;
    try { if (MBT.state && MBT.state.set) MBT.state.set(k, v); } catch (e) { /* in-memory only */ }
    writing = false;
  }
  function announce(t) { if (MBT.announce) MBT.announce(t); }
  function team(key) {
    for (var i = 0; i < TEAMS.length; i++) if (TEAMS[i].key === key) return TEAMS[i];
    return null;
  }
  function teamOfRole(roleKey) {
    for (var i = 0; i < TEAMS.length; i++) if (TEAMS[i].roles.indexOf(roleKey) !== -1) return TEAMS[i].key;
    return null;
  }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function q(s) { return '“' + s + '”'; }
  function slash(name) { return name.charAt(0) === '/' ? name : '/' + name; }

  /* ---------- accessible radiogroup ---------- */
  function RadioGroup(groupEl, onPick) {
    var self = this;
    this.el = groupEl;
    this.value = null;
    this.items = function () { return [].slice.call(groupEl.querySelectorAll('[role="radio"]')); };
    this.rove = function (target) {
      self.items().forEach(function (it) { it.tabIndex = it === target ? 0 : -1; });
    };
    this.set = function (v) {
      self.value = v;
      var items = self.items();
      var hit = null;
      items.forEach(function (it) {
        var on = it.getAttribute('data-value') === v;
        it.setAttribute('aria-checked', on ? 'true' : 'false');
        if (on) hit = it;
      });
      self.rove(hit || items[0]);
      groupEl.classList.toggle('has-value', !!hit);
    };
    this.focusChecked = function () {
      var items = self.items();
      var t = groupEl.querySelector('[aria-checked="true"]') || items[0];
      if (t) t.focus();
    };
    function pick(it, origin) {
      if (origin) {
        it.style.setProperty('--fx', origin.x + '%');
        it.style.setProperty('--fy', origin.y + '%');
      } else {
        it.style.removeProperty('--fx');
        it.style.removeProperty('--fy');
      }
      var v = it.getAttribute('data-value');
      var changed = v !== self.value;
      self.set(v);
      onPick(v, changed);
    }
    groupEl.addEventListener('keydown', function (e) {
      if (e.altKey || e.ctrlKey || e.metaKey) return;
      var it = e.target.closest && e.target.closest('[role="radio"]');
      if (!it || !groupEl.contains(it)) return;
      var items = self.items();
      var i = items.indexOf(it);
      var to = null;
      switch (e.key) {
        case 'ArrowRight': case 'ArrowDown': to = items[(i + 1) % items.length]; break;
        case 'ArrowLeft': case 'ArrowUp': to = items[(i - 1 + items.length) % items.length]; break;
        case 'Home': to = items[0]; break;
        case 'End': to = items[items.length - 1]; break;
        case ' ': case 'Spacebar': case 'Enter':
          e.preventDefault();
          if (!e.repeat) pick(it, null);
          return;
        default: return;
      }
      e.preventDefault();
      self.rove(to);
      to.focus();
    });
    groupEl.addEventListener('click', function (e) {
      var it = e.target.closest && e.target.closest('[role="radio"]');
      if (!it || !groupEl.contains(it)) return;
      var origin = null;
      if (e.clientX || e.clientY) {
        var r = it.getBoundingClientRect();
        if (r.width && r.height) {
          origin = {
            x: Math.round(Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)) * 100),
            y: Math.round(Math.max(0, Math.min(1, (e.clientY - r.top) / r.height)) * 100)
          };
        }
      }
      pick(it, origin);
    });
  }

  /* ---------- elements ---------- */
  var form = $('p-form');
  var summary = $('p-summary');
  var summaryV = $('p-summary-v');
  var changeBtn = $('p-change');
  var stepFn = $('p-step-fn');
  var stepExp = $('p-step-exp');
  var expNum = $('p-exp-num');
  var fnWrap = $('p-fn');
  var card = $('p-card');
  var cardRole = $('p-card-role');
  var route = $('p-route');
  var vExample = $('p-v-example');
  var vPractice = $('p-v-practice');
  var vFirst = $('p-v-first');
  var firstK = $('p-k-first');
  var note = $('p-card-note');
  var actions = $('p-actions');
  var skipBtn = $('p-skip');

  var sel = { team: null, role: null, exp: null };

  var teamGroup = new RadioGroup($('p-team'), function (v, changed) { chooseTeam(v, changed, true); });
  var fnGroup = new RadioGroup(fnWrap, function (v, changed) { chooseRole(v, changed, true); });
  var expGroup = new RadioGroup($('p-exp'), function (v, changed) { chooseExp(v, changed, true); });

  /* ---------- choices ---------- */
  function buildFn(t) {
    while (fnWrap.firstChild) fnWrap.removeChild(fnWrap.firstChild);
    t.roles.forEach(function (rk) {
      var r = ROLES[rk];
      if (!r) return;
      var tile = el('div', 'p-tile p-tile-fn');
      tile.setAttribute('role', 'radio');
      tile.setAttribute('aria-checked', 'false');
      tile.setAttribute('data-value', rk);
      tile.tabIndex = -1;
      tile.appendChild(el('span', 'p-tile-name', r.label));
      var first = r.starters && r.starters[0];
      if (first) tile.appendChild(el('span', 'p-tile-sub p-tile-cmd', first.cmd));
      var dot = el('span', 'p-dot');
      dot.setAttribute('aria-hidden', 'true');
      tile.appendChild(dot);
      fnWrap.appendChild(tile);
    });
    fnWrap.setAttribute('data-count', String(t.roles.length));
  }

  function chooseTeam(key, changed, user) {
    var t = team(key);
    if (!t) return;
    var prevTeam = sel.team;
    sel.team = key;
    teamGroup.set(key);
    if (t.roles.length > 1) {
      if (prevTeam !== key || !fnWrap.firstChild) buildFn(t);
      if (t.roles.indexOf(sel.role) === -1) sel.role = null;
      fnGroup.set(sel.role);
      reveal(stepFn);
      render();
      if (user) announce(t.label + ' selected. Next: what do you mostly do? ' + t.roles.length + ' options.');
    } else {
      stepFn.hidden = true;
      chooseRole(t.roles[0], sel.role !== t.roles[0], user, true);
    }
  }

  function chooseRole(key, changed, user, viaTeam) {
    if (!ROLES[key]) return;
    var was = getState('role');
    sel.role = key;
    if (!viaTeam) fnGroup.set(key);
    var expWasHidden = stepExp.hidden;
    if (user && was !== key) {
      setState('role', key);
      if (MBT.emit) MBT.emit('role', ROLES[key]);
    }
    reveal(stepExp);
    render(true);
    if (!user) return;
    if (sel.exp) { announceComplete(); if (expWasHidden) revealActions(); }
    else if (expWasHidden) announce(ROLES[key].label + ' selected. Next: how much have you used Claude?');
    else announce(ROLES[key].label + ' selected.');
  }

  function chooseExp(v, changed, user) {
    if (!EXP[v]) return;
    var wasDone = !!(sel.role && sel.exp);
    sel.exp = v;
    expGroup.set(v);
    if (user && getState('exp') !== v) setState('exp', v);
    render(changed);
    if (!user) return;
    announceComplete();
    if (!wasDone && sel.role) revealActions();
  }

  /* bring the finished card's buttons into view once, without moving focus */
  function revealActions() {
    if (actions.hidden || !actions.scrollIntoView) return;
    var r = actions.getBoundingClientRect();
    var navTop = window.innerHeight;
    var nav = document.querySelector('.nav');
    if (nav) navTop = Math.min(navTop, nav.getBoundingClientRect().top);
    if (r.bottom <= navTop - 8) return;
    try { actions.scrollIntoView({ block: 'nearest', behavior: MBT.reduced ? 'auto' : 'smooth' }); }
    catch (e) { actions.scrollIntoView(false); }
  }

  function reveal(step) {
    if (!step.hidden) return;
    step.hidden = false;
    if (!MBT.reduced) {
      step.classList.remove('p-enter');
      void step.offsetWidth;
      step.classList.add('p-enter');
    }
  }

  function exampleTitle(r) {
    var w = MBT.WORKED && MBT.WORKED[r.example];
    return (w && (w.title || w.request)) || r.exampleTitle || r.label;
  }

  function announceComplete() {
    var r = ROLES[sel.role];
    if (!r || !sel.exp) return;
    var w = r.weights || [];
    announce('Your path: ' + r.label + '. Worked example: ' + exampleTitle(r) +
      '. Practice weighted to ' + w.slice(0, 2).join(' and ') +
      '. First command: ' + r.starters[0].cmd + '.');
  }

  /* ---------- card ---------- */
  function swap(node) {
    if (MBT.reduced) return;
    node.classList.remove('p-swap');
    void node.offsetWidth;
    node.classList.add('p-swap');
  }
  function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }

  function renderFirst(r) {
    clear(vFirst);
    var s = r.starters[0];
    var box = el('div', 'p-first');
    var top = el('div', 'p-first-top');
    top.appendChild(el('code', 'cmd p-first-cmd', s.cmd));
    var copy = el('button', 'btn btn-sm copy-btn p-copy', 'Copy prompt');
    copy.type = 'button';
    copy.addEventListener('click', function () {
      if (MBT.copy) MBT.copy(s.prompt, copy);
    });
    top.appendChild(copy);
    box.appendChild(top);
    box.appendChild(el('p', 'p-first-prompt', q(s.prompt)));
    box.appendChild(el('p', 'p-first-why', s.why));
    vFirst.appendChild(box);
    clear(firstK);
    firstK.appendChild(document.createTextNode('Your first command'));
    if (r.key !== 'any') {
      firstK.appendChild(el('span', 'p-after', ', after ' + q('tell me about the team') + ' shows you are connected'));
    }
  }

  var lastRole = null;
  function render(animate) {
    var r = ROLES[sel.role];
    var t = team(sel.team);
    var multi = t && t.roles.length > 1;

    stepFn.hidden = !multi;
    stepExp.hidden = !(sel.role || sel.exp);
    if (expNum) expNum.textContent = multi ? '3' : '2';
    root.querySelector('#p-step-team').classList.toggle('is-done', !!sel.team);
    stepFn.classList.toggle('is-done', !!(multi && sel.role));
    stepExp.classList.toggle('is-done', !!sel.exp);

    var stops = route.querySelectorAll('.p-stop');
    if (r) {
      cardRole.textContent = r.org.toLowerCase() === r.label.toLowerCase() ? r.org : r.label + ' · ' + r.org;
      if (r.key !== lastRole) {
        vExample.textContent = q(exampleTitle(r));
        clear(vPractice);
        (r.weights || []).slice(0, 2).forEach(function (w) { vPractice.appendChild(el('code', 'cmd', slash(w))); });
        renderFirst(r);
        if (animate && lastRole) { swap(vExample); swap(vPractice); swap(vFirst); swap(cardRole); }
        lastRole = r.key;
      }
      for (var i = 0; i < stops.length; i++) stops[i].classList.add('is-set');
    } else {
      cardRole.textContent = t ? t.label + ': pick what you mostly do' : 'Pick a team to start';
      vExample.textContent = t ? 'Appears when you pick what you do' : 'Appears when you pick a team';
      if (lastRole !== null) {
        vPractice.textContent = 'The skills your work leans on';
        vFirst.textContent = 'One command, ready to paste';
        firstK.textContent = 'Your first command';
        lastRole = null;
      }
      for (var j = 0; j < stops.length; j++) stops[j].classList.remove('is-set');
    }
    route.classList.toggle('is-set', !!r);

    var done = !!(r && sel.exp);
    note.textContent = sel.exp && EXP[sel.exp] ? EXP[sel.exp].note : (r ? 'One more answer: how much have you used Claude?' : '');
    note.hidden = !note.textContent;
    actions.hidden = !done;
    skipBtn.hidden = !(done && sel.exp === 'fluent');
    card.classList.toggle('is-ready', done);
    root.classList.toggle('p-complete', done);
  }

  /* ---------- summary (returning viewer) ---------- */
  function summaryText() {
    var r = ROLES[sel.role];
    var t = team(sel.team);
    var parts = [];
    if (t) parts.push(t.label);
    if (r && t && t.roles.length > 1) parts.push(r.label);
    if (sel.exp && EXP[sel.exp]) parts.push(EXP[sel.exp].label);
    return parts.join(' · ');
  }
  function showSummary(on) {
    summary.hidden = !on;
    form.hidden = on;
    root.classList.toggle('p-mode-summary', on);
    changeBtn.setAttribute('aria-expanded', on ? 'false' : 'true');
    if (on) summaryV.textContent = summaryText();
  }
  changeBtn.addEventListener('click', function () {
    showSummary(false);
    if (!MBT.reduced) {
      form.classList.remove('p-enter');
      void form.offsetWidth;
      form.classList.add('p-enter');
    }
    teamGroup.focusChecked();
  });

  /* ---------- navigation buttons ----------
     Both carry data-nav; the core owns data-nav navigation. The fallback below only runs
     when the core has not handled the click (no MBT.go yet, or the slide did not change). */
  [$('p-continue'), skipBtn].forEach(function (b) {
    b.addEventListener('click', function () {
      var target = b.getAttribute('data-nav');
      setTimeout(function () {
        if (!MBT.go || !MBT.current) return;
        var cur = MBT.current();
        if (cur && cur.id === 'path') MBT.go(target);
      }, 0);
    });
  });

  /* ---------- restore ---------- */
  function validRole(k) { return k && ROLES[k] ? k : null; }
  function validExp(k) { return k && EXP[k] ? k : null; }

  function apply(roleKey, exp, collapse) {
    sel = { team: roleKey ? teamOfRole(roleKey) : null, role: roleKey, exp: exp };
    lastRole = '__';
    teamGroup.set(sel.team);
    var t = team(sel.team);
    if (t && t.roles.length > 1) { buildFn(t); fnGroup.set(roleKey); }
    else { while (fnWrap.firstChild) fnWrap.removeChild(fnWrap.firstChild); }
    expGroup.set(exp);
    render(false);
    showSummary(!!(collapse && roleKey && exp));
  }

  apply(validRole(getState('role')), validExp(getState('exp')), true);

  function resync() {
    var r = validRole(getState('role'));
    var x = validExp(getState('exp'));
    if (r === sel.role && x === sel.exp) return;
    if (r === null && x === null && sel.role === null && sel.exp === null) return;
    apply(r, x, !!(r && x));
  }
  if (MBT.on) {
    MBT.on('state', function (p) {
      if (writing || !p) return;
      if (p.key === 'role' || p.key === 'exp' || p.key == null) resync();
    });
    MBT.on('slide', function (p) {
      if (p && p.id === 'path') resync();
    });
  }
})();
