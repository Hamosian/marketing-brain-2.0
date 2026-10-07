/* 62-commit.js: commitment (slide "commit"), check-in on a later visit, funnel write,
   owner console. State keys: 'commit' {cmd, when, at}, 'ran' (boolean).
   Capabilities are optional: every path no-ops when MBT.cap resolves null. */
(function () {
  'use strict';
  var MBT = window.MBT || {};
  var F = window.MBTFinish;
  var slide = document.querySelector('[data-id="commit"]');
  if (!F) return;
  var el = F.el;
  var LOADED_AT = Date.now();

  var UNIVERSAL = {
    cmd: '/team-intro',
    prompt: 'tell me about the team',
    why: 'Shows what the Brain knows: the team, the systems we own, and what it can do for you. It only reads.',
    universal: true
  };

  function role() {
    try { return (MBT.role && MBT.role()) || {}; } catch (e) { return {}; }
  }
  function options() {
    var r = role();
    var list = [UNIVERSAL];
    (r.starters || []).forEach(function (s) {
      if (!s || !s.cmd || s.cmd === UNIVERSAL.cmd) return;
      list.push({ cmd: s.cmd, prompt: s.prompt || s.cmd, why: s.why || '' });
    });
    return list;
  }
  function spoken(cmd) {
    return cmd === UNIVERSAL.cmd ? '“' + UNIVERSAL.prompt + '”' : cmd;
  }
  function clear(n) { while (n && n.firstChild) n.removeChild(n.firstChild); }
  function focusQuiet(n) { if (!n) return; try { n.focus({ preventScroll: true }); } catch (e) { n.focus(); } }

  /* ================= commitment UI ================= */
  if (slide) {
    var listEl = document.getElementById('f-pick-list');
    var hintEl = document.getElementById('f-role-hint');
    var pledge = document.getElementById('f-pledge');
    var pledgeCmd = document.getElementById('f-pledge-cmd');
    var pledgeCopy = document.getElementById('f-pledge-copy');
    var goBtn = document.getElementById('f-pledge-go');
    var savedEl = document.getElementById('f-pledge-saved');
    var checkin = document.getElementById('f-checkin');
    var checkinCmd = document.getElementById('f-checkin-cmd');
    var checkinBtns = document.getElementById('f-checkin-btns');
    var checkinMsg = document.getElementById('f-checkin-msg');
    var selected = null;

    var renderPicks = function () {
      var opts = options();
      var commit = F.state('commit', null);
      var keep = selected ? selected.cmd : (commit && commit.cmd);
      selected = null;
      opts.forEach(function (o) { if (o.cmd === keep) selected = o; });
      if (!selected) selected = opts[0];
      clear(listEl);
      opts.forEach(function (o, i) {
        var id = 'f-pick-' + i;
        var input = el('input', { type: 'radio', name: 'f-pick', id: id, value: o.cmd });
        input.checked = o === selected;
        input.addEventListener('change', function () { if (input.checked) { selected = o; paintPledge(); } });
        var main = el('label', { className: 'f-pick-main', 'for': id }, [
          input,
          el('span', { className: 'f-pick-dot', 'aria-hidden': 'true' }),
          el('span', { className: 'f-pick-text' }, [
            el('span', { className: 'f-pick-top' }, [
              el('code', { className: 'cmd', text: o.cmd }),
              o.universal ? el('span', { className: 'f-pick-tag', text: 'Everyone starts here' }) : null
            ]),
            el('span', { className: 'f-pick-prompt', text: '“' + o.prompt + '”' }),
            o.why ? el('span', { className: 'f-pick-why', text: o.why }) : null
          ])
        ]);
        var copy = el('button', { type: 'button', className: 'btn btn-ghost btn-sm copy-btn f-copy f-pick-copy', 'data-f-copy': o.prompt, 'aria-label': 'Copy: ' + o.prompt, text: 'Copy' });
        listEl.appendChild(el('div', { className: 'f-pick' + (o.universal ? ' is-universal' : '') }, [main, copy]));
      });
      var r = role();
      clear(hintEl);
      if (r.key && r.key !== 'any' && r.label) {
        hintEl.appendChild(document.createTextNode('Starters for ' + r.label + '. '));
      } else {
        hintEl.appendChild(document.createTextNode('Pick your role to see starters for your work. '));
      }
      hintEl.appendChild(el('button', { type: 'button', className: 'f-linkbtn f-nav', 'data-nav': 'path', text: r.key && r.key !== 'any' ? 'Change role' : 'Pick a role' }));
      paintPledge();
    };

    var paintPledge = function () {
      if (!selected) return;
      pledgeCmd.textContent = selected.prompt;
      pledgeCopy.setAttribute('data-f-copy', selected.prompt);
      pledgeCopy.setAttribute('aria-label', 'Copy: ' + selected.prompt);
      var c = F.state('commit', null);
      var same = c && c.cmd === selected.cmd && c.when === currentWhen();
      pledge.classList.toggle('is-committed', !!same);
      goBtn.textContent = c ? (same ? 'Saved' : 'Update my pick') : 'I will do it';
    };

    var currentWhen = function () {
      var r = slide.querySelector('input[name="f-when"]:checked');
      return r ? r.value : 'This week';
    };

    var setWhen = function (w) {
      var rs = slide.querySelectorAll('input[name="f-when"]');
      for (var i = 0; i < rs.length; i++) rs[i].checked = rs[i].value === w;
    };

    slide.addEventListener('change', function (e) {
      if (e.target && e.target.name === 'f-when') paintPledge();
    });

    goBtn.addEventListener('click', function () {
      if (!selected) return;
      var when = currentWhen();
      var prev = F.state('commit', null);
      var c = { cmd: selected.cmd, when: when, at: new Date().toISOString() };
      if (prev && prev.cmd === c.cmd && prev.when === c.when) {
        savedEl.textContent = 'Already saved: ' + spoken(c.cmd) + ', ' + when.toLowerCase() + '.';
        focusQuiet(savedEl);
        return;
      }
      F.save('commit', c);
      if (!prev || prev.cmd !== c.cmd) F.save('ran', false);
      pledge.classList.remove('is-stamping');
      void pledge.offsetWidth;
      pledge.classList.add('is-stamping');
      savedEl.textContent = 'Saved. You will run ' + spoken(c.cmd) + ' ' + when.toLowerCase() + '. When you come back, this slide asks how it went.';
      paintPledge();
      paintCheckin();
      focusQuiet(savedEl);
    });

    /* ---- check-in on a later visit ---- */
    var paintCheckin = function () {
      var c = F.state('commit', null);
      var ran = F.state('ran', false) === true;
      var earlier = c && c.at && Date.parse(c.at) < LOADED_AT - 1000;
      if (!c || !earlier) { checkin.hidden = true; return; }
      checkin.hidden = false;
      checkinCmd.textContent = spoken(c.cmd);
      if (ran) {
        checkin.classList.add('is-ran');
        checkinBtns.hidden = true;
        if (!checkinMsg.textContent) checkinMsg.textContent = 'You ran it. Pick the next one below.';
      }
    };

    document.getElementById('f-checkin-yes').addEventListener('click', function () {
      F.save('ran', true);
      checkin.classList.add('is-ran');
      checkinBtns.hidden = true;
      clear(checkinMsg);
      checkinMsg.appendChild(document.createTextNode('Nice. When the Brain misses a step or gets something wrong, run '));
      checkinMsg.appendChild(el('code', { className: 'cmd', text: '/retro' }));
      checkinMsg.appendChild(document.createTextNode(' so the fix lands in the repo for everyone. Pick your next one below.'));
      focusQuiet(checkinMsg);
    });
    document.getElementById('f-checkin-no').addEventListener('click', function () {
      clear(checkinMsg);
      checkinMsg.appendChild(document.createTextNode('No problem. If setup is what stopped you, it takes a few minutes once you have access. '));
      checkinMsg.appendChild(el('button', { type: 'button', className: 'f-linkbtn f-nav', 'data-nav': 'setup', text: 'Go to setup' }));
      focusQuiet(checkinMsg);
    });

    var initial = F.state('commit', null);
    if (initial && initial.when) setWhen(initial.when);
    renderPicks();
    paintCheckin();

    if (MBT.on) {
      MBT.on('role', function () { selected = null; renderPicks(); });
      MBT.on('state', function (p) {
        if (!p) return;
        if (p.key === 'role') { selected = null; renderPicks(); }
        if ((p.key === 'commit' || p.key === 'ran') && p.value) {
          /* restored from the private mirror after load, or saved here */
          var c = F.state('commit', null);
          if (p.key === 'commit' && c && c.when) setWhen(c.when);
          renderPicks();
          paintCheckin();
        }
        if ((p.key === 'commit' || p.key === 'ran') && (p.value === null || p.value === undefined)) {
          /* state cleared by "Start over" */
          savedEl.textContent = ''; checkin.hidden = true; checkinMsg.textContent = ''; checkinBtns.hidden = false;
          checkin.classList.remove('is-ran'); selected = null; setWhen('This week'); renderPicks();
        }
      });
    }
  }

  /* ================= funnel + owner console (capabilities) ================= */
  var fun = { ref: null, lastSig: null, started: null, busy: false, again: false, off: false, timer: null };
  var FUNNEL_KEYS = { role: 1, exp: 1, far: 1, check: 1, commit: 1, ran: 1 };

  function lastCoreIndex() {
    var idx = -1;
    (MBT.slides || []).forEach(function (s) { if (s.part === 'core' && s.index > idx) idx = s.index; });
    return idx;
  }
  function snapshot() {
    var r = role();
    var chk = F.state('check', null) || {};
    var c = F.state('commit', null);
    var last = lastCoreIndex();
    var far = Number(F.state('far', 0)) || 0;
    return {
      org: r.org || 'Not sure yet',
      role: F.state('role', null) || 'any',
      exp: F.state('exp', null) || null,
      coreDone: last > 0 && far >= last,
      passed: !!chk.passed,
      committed: !!(c && c.cmd),
      cmd: c && c.cmd ? String(c.cmd) : null,
      when: c && c.when ? String(c.when) : null,
      ran: F.state('ran', false) === true
    };
  }
  function pickFields(d) {
    if (!d) return null;
    return {
      org: d.org || 'Not sure yet', role: d.role || 'any', exp: d.exp || null,
      coreDone: !!d.coreDone, passed: !!d.passed, committed: !!d.committed,
      cmd: d.cmd || null, when: d.when || null, ran: !!d.ran
    };
  }

  function sync() {
    if (!fun.ref || fun.off) return;
    if (fun.busy) { fun.again = true; return; }
    var snap = snapshot();
    var sig = JSON.stringify(snap);
    if (sig === fun.lastSig) return;
    fun.busy = true;
    var doc = {};
    Object.keys(snap).forEach(function (k) { doc[k] = snap[k]; });
    doc.started = fun.started;
    doc.updatedAt = new Date().toISOString();
    var attempt = function (retry) {
      return fun.ref.set(doc).then(function () {
        fun.lastSig = sig;
      }, function (err) {
        var code = err && err.code;
        if (code === 'unavailable' && retry) {
          return new Promise(function (res) { setTimeout(res, 800 + Math.random() * 800); }).then(function () { return attempt(false); });
        }
        if (code !== 'resource_exhausted' && code !== 'unavailable') fun.off = true;
        return null;
      });
    };
    attempt(true).then(function () {
      fun.busy = false;
      if (fun.again) { fun.again = false; sync(); }
    });
  }
  function schedule() {
    if (!fun.ref || fun.off) return;
    clearTimeout(fun.timer);
    fun.timer = setTimeout(sync, 700);
  }

  function capsReady() {
    if (!MBT.cap) return Promise.resolve([null, null]);
    return Promise.all([
      MBT.cap('db').catch(function () { return null; }),
      MBT.cap('user').catch(function () { return null; })
    ]);
  }

  capsReady().then(function (caps) {
    var db = caps[0], user = caps[1];
    if (!db || !user) return;
    Promise.resolve(user.id()).then(function (uid) {
      if (!uid) return;
      var ref;
      try { ref = db.doc('funnel/' + uid); } catch (e) { return; }
      return ref.get().then(function (snap) { return snap; }, function () { return null; }).then(function (snap) {
        var data = snap && snap.exists ? snap.data() : null;
        fun.started = (data && data.started) || new Date().toISOString();
        fun.lastSig = data ? JSON.stringify(pickFields(data)) : null;
        fun.ref = ref;
        var priv = document.getElementById('f-privacy');
        if (priv) priv.hidden = false;
        var cpriv = document.getElementById('c-privacy');
        if (cpriv) cpriv.hidden = false;
        sync();
        if (MBT.on) MBT.on('state', function (p) { if (p && FUNNEL_KEYS[p.key]) schedule(); });
      });
    }).catch(function () { /* no funnel this visit */ });

    Promise.resolve(user.isOwner()).then(function (owner) {
      if (owner && slide) owner_init(db, user);
    }).catch(function () { /* not the owner */ });
  });

  /* ---------------- owner console ---------------- */
  var STAGES = [
    ['started', 'Started'],
    ['coreDone', 'Finished core'],
    ['passed', 'Passed check'],
    ['committed', 'Committed'],
    ['ran', 'Ran it']
  ];
  var ORGS = ['Growth', 'Brand', 'Marketing', 'AI Marketing', 'Growth Initiatives', 'Not sure yet'];

  function owner_init(db, user) {
    var panel = document.getElementById('f-owner');
    if (!panel) return;
    var subscribed = false;
    var funnelDocs = [], flagDocs = [], renderSeq = 0, failed = false;

    function subscribe() {
      if (subscribed) return;
      subscribed = true;
      panel.hidden = false;
      try {
        db.collection('funnel').onSnapshot(function (snap) {
          funnelDocs = snap.docs.map(function (d) { var x = d.data() || {}; return { id: d.id, d: x }; });
          render();
        }, function () { failed = true; render(); });
        db.collection('flags').onSnapshot(function (snap) {
          flagDocs = snap.docs.map(function (d) { return d.data() || {}; });
          render();
        }, function () { /* flags optional */ });
      } catch (e) { failed = true; render(); }
    }

    function stageOf(d) {
      if (d.ran) return 4;
      if (d.committed) return 3;
      if (d.passed) return 2;
      if (d.coreDone) return 1;
      return 0;
    }
    function has(d, key) { return key === 'started' ? true : !!d[key]; }

    function render() {
      var seq = ++renderSeq;
      var stats = document.getElementById('f-owner-stats');
      var table = document.getElementById('f-owner-table');
      var people = document.getElementById('f-owner-people');
      var peopleSum = document.getElementById('f-owner-people-sum');
      var flags = document.getElementById('f-owner-flags');
      clear(stats); clear(table);
      if (failed && !funnelDocs.length) {
        stats.appendChild(el('p', { className: 'f-owner-empty', text: 'Team progress could not load right now. It will retry when you reopen the trainer.' }));
        return;
      }
      if (!funnelDocs.length) {
        stats.appendChild(el('p', { className: 'f-owner-empty', text: 'No one has opened the trainer with progress saving on yet.' }));
      }
      var total = funnelDocs.length;
      STAGES.forEach(function (st) {
        var n = funnelDocs.filter(function (x) { return has(x.d, st[0]); }).length;
        var pct = total ? Math.round((n / total) * 100) : 0;
        stats.appendChild(el('div', { className: 'f-stat' }, [
          el('span', { className: 'f-stat-n', text: String(n) }),
          el('span', { className: 'f-stat-l', text: st[1] }),
          el('span', { className: 'f-stat-bar', 'aria-hidden': 'true' }, [el('i', { style: 'width:' + pct + '%' })])
        ]));
      });

      /* by org */
      var orgs = ORGS.slice();
      funnelDocs.forEach(function (x) { var o = x.d.org || 'Not sure yet'; if (orgs.indexOf(o) < 0) orgs.push(o); });
      var tbl = el('table', { className: 'f-otable' });
      var thead = el('thead', null, [el('tr', null, [el('th', { scope: 'col', text: 'Org' })].concat(STAGES.map(function (st) { return el('th', { scope: 'col', text: st[1] }); })))]);
      var tbody = el('tbody');
      orgs.forEach(function (o) {
        var rows = funnelDocs.filter(function (x) { return (x.d.org || 'Not sure yet') === o; });
        if (!rows.length) return;
        tbody.appendChild(el('tr', null, [el('th', { scope: 'row', text: o })].concat(STAGES.map(function (st) {
          return el('td', { text: String(rows.filter(function (x) { return has(x.d, st[0]); }).length) });
        }))));
      });
      tbl.appendChild(thead); tbl.appendChild(tbody);
      if (tbody.firstChild) table.appendChild(tbl);

      /* flags */
      var items = 0, flaggers = 0;
      flagDocs.forEach(function (f) { var n = (f.items && f.items.length) || 0; items += n; if (n) flaggers++; });
      flags.textContent = items
        ? items + (items === 1 ? ' flag' : ' flags') + ' from ' + flaggers + (flaggers === 1 ? ' person' : ' people') + ' on the router and catalog. Ask Claude to read the flags collection to see them.'
        : 'No one has flagged anything as wrong yet.';

      /* people, names resolved at render time, never stored */
      peopleSum.textContent = 'People (' + total + ')';
      var sorted = funnelDocs.slice().sort(function (a, b) { return stageOf(b.d) - stageOf(a.d); });
      var ids = sorted.map(function (x) { return x.id; });
      var draw = function (ps) {
        if (seq !== renderSeq) return;
        clear(people);
        sorted.forEach(function (x) {
          var p = ps && ps[x.id];
          var name = (p && p.name) || 'Someone';
          var bits = [x.d.org || 'Not sure yet', STAGES[stageOf(x.d)][1]];
          if (x.d.cmd) bits.push(spoken(x.d.cmd) + (x.d.when ? ', ' + String(x.d.when).toLowerCase() : ''));
          people.appendChild(el('li', null, [
            el('span', { className: 'f-person', text: name }),
            el('span', { className: 'f-person-meta', text: bits.join(' · ') })
          ]));
        });
      };
      if (!ids.length) { draw({}); return; }
      Promise.resolve(user.profiles ? user.profiles(ids) : {}).then(draw, function () { draw({}); });
    }

    var cur = MBT.current ? MBT.current() : null;
    if (cur && cur.id === 'commit') subscribe();
    if (MBT.on) MBT.on('slide', function (p) { if (p && p.id === 'commit') subscribe(); });
  }
})();
