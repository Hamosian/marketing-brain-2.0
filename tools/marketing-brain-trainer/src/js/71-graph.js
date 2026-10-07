/* 71-graph.js: slide 16, "The real wiring".
   Renders MBT.data.graph (skills plus the reference and system docs they
   link to) as an SVG force layout. The layout is computed once, the first
   time the slide is shown, synchronously, then it stops: no animation loop.
   Hover, tap, or arrow keys highlight a node and its neighbours; a list view
   carries the same information for screen readers and small screens. */
(function () {
  'use strict';

  var MBT = window.MBT || {};
  var slide = document.querySelector('.slide[data-id="graph"]');
  if (!slide) return;

  function $(id) { return document.getElementById(id); }
  function readJSON(id) {
    try { var el = $(id); return el ? JSON.parse(el.textContent) : null; } catch (e) { return null; }
  }
  function data(key, elId) { var d = MBT.data && MBT.data[key]; return d || readJSON(elId); }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  var W = 1000, H = 600;
  var svg = $('a-g-svg'), stage = $('a-g-stage'), insp = $('a-g-insp-body'), hubsEl = $('a-g-hubs');
  var cap = $('a-g-cap'), loading = $('a-g-loading');
  var btnGraph = $('a-g-v-graph'), btnList = $('a-g-v-list');
  var viewGraph = $('a-g-view-graph'), viewList = $('a-g-view-list'), listEl = $('a-g-list');

  /* ---------------- model ---------------- */
  var raw = data('graph', 'brainGraph') || { nodes: [], links: [] };
  var nodes = (raw.nodes || []).map(function (n, i) {
    return { id: n.id, kind: n.kind, i: i, out: [], inn: [], deg: 0, x: 0, y: 0, r: 4, links: [] };
  });
  var byId = {};
  nodes.forEach(function (n) { byId[n.id] = n; });
  var links = (raw.links || []).filter(function (l) { return byId[l.s] && byId[l.t]; }).map(function (l, j) {
    var s = byId[l.s], t = byId[l.t];
    s.out.push(t); t.inn.push(s); s.deg++; t.deg++;
    s.links.push(j); t.links.push(j);
    return { s: s, t: t };
  });
  var order = nodes.slice().sort(function (a, b) { return b.deg - a.deg || (a.id < b.id ? -1 : 1); });
  var nSkills = nodes.filter(function (n) { return n.kind === 'skill'; }).length;
  var nDocs = nodes.length - nSkills;

  function label(n) {
    if (n.kind === 'skill') return n.id;
    var parts = n.id.split('/');
    return parts[parts.length - 1];
  }
  function fullName(n) { return n.kind === 'skill' ? '/' + n.id : n.id; }
  function kindName(n) { return n.kind === 'skill' ? 'Skill' : n.kind === 'system' ? 'System doc' : 'Reference doc'; }
  function linkWord(k) { return k === 1 ? '1 link' : k + ' links'; }

  /* ---------------- caption, summary, hubs (cheap, at parse time) ---------------- */
  var f = data('facts', 'buildFacts') || {};
  var fs = Number(f.graphSkills) || nSkills, fd = Number(f.graphDocs) || nDocs, fl = Number(f.graphLinks) || links.length;
  cap.textContent = 'Generated at build time from what the skill files actually link to: ' + fs + ' skills, ' + fd +
    ' docs, ' + fl + ' links. The full repo graph (graphify) has about 10,600 nodes and rebuilds on every merge.';
  var top3 = order.slice(0, 3).map(function (n) { return fullName(n) + ' (' + linkWord(n.deg) + ')'; }).join(', ');
  svg.setAttribute('aria-label', 'Link graph of ' + fs + ' skills and ' + fd + ' shared docs, joined by ' + fl +
    ' links. Most connected: ' + top3 + '. Choose Show as a list for every node and its links.');

  var HUBS = order.slice(0, 5);
  hubsEl.innerHTML = HUBS.map(function (n) {
    return '<button type="button" class="a-g-hub" aria-pressed="false" data-i="' + n.i + '">' + esc(label(n)) +
      ' <span aria-hidden="true">' + n.deg + '</span><span class="sr-only">, ' + linkWord(n.deg) + '</span></button>';
  }).join('');

  /* ---------------- layout (computed once) ---------------- */
  function computeLayout() {
    var n = nodes.length;
    if (!n) return;
    var i, j, a, b, dx, dy, l, w, d2, d;
    // hubs start in the middle of a phyllotaxis spiral, like d3-force
    order.forEach(function (p, idx) {
      var rad = 10 * Math.sqrt(0.5 + idx), ang = idx * Math.PI * (3 - Math.sqrt(5));
      p.x = rad * Math.cos(ang); p.y = rad * Math.sin(ang);
      p.vx = 0; p.vy = 0;
      p.r = p.deg ? 3.6 + Math.sqrt(p.deg) * 2.4 : 3.4;
    });
    var TICKS = 320, alpha = 1, decay = 1 - Math.pow(0.001, 1 / TICKS);
    var CHARGE = -46, MAX2 = 320 * 320;
    for (var tick = 0; tick < TICKS; tick++) {
      alpha += (0 - alpha) * decay;
      // springs: pull linked nodes toward a rest length, softer on hubs
      for (j = 0; j < links.length; j++) {
        a = links[j].s; b = links[j].t;
        dx = b.x + b.vx - a.x - a.vx; dy = b.y + b.vy - a.y - a.vy;
        l = Math.sqrt(dx * dx + dy * dy) || 0.01;
        var rest = 30 + a.r + b.r;
        var str = 1 / Math.min(a.deg, b.deg);
        var bias = a.deg / (a.deg + b.deg);
        l = (l - rest) / l * alpha * str;
        dx *= l; dy *= l;
        b.vx -= dx * bias; b.vy -= dy * bias;
        a.vx += dx * (1 - bias); a.vy += dy * (1 - bias);
      }
      // charge: every pair repels within a cut-off radius
      for (i = 0; i < n; i++) {
        a = nodes[i];
        for (j = i + 1; j < n; j++) {
          b = nodes[j];
          dx = b.x - a.x; dy = b.y - a.y;
          l = dx * dx + dy * dy;
          if (l > MAX2) continue;
          if (l < 1) l = 1;
          w = CHARGE * alpha / l;
          a.vx += dx * w; a.vy += dy * w;
          b.vx -= dx * w; b.vy -= dy * w;
        }
      }
      // gentle pull to the centre, flatter vertically for a landscape stage
      for (i = 0; i < n; i++) {
        a = nodes[i];
        a.vx -= a.x * 0.045 * alpha;
        a.vy -= a.y * 0.075 * alpha;
        a.vx *= 0.6; a.vy *= 0.6;
        a.x += a.vx; a.y += a.vy;
      }
    }
    // fit into the viewBox, leaving room for labels
    var minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    nodes.forEach(function (p) {
      if (p.x < minX) minX = p.x; if (p.x > maxX) maxX = p.x;
      if (p.y < minY) minY = p.y; if (p.y > maxY) maxY = p.y;
    });
    var padX = 40, padY = 30;
    var sx = (W - padX * 2) / Math.max(1, maxX - minX), sy = (H - padY * 2) / Math.max(1, maxY - minY);
    var s = Math.min(sx, sy * 1.8), sY = Math.min(sy, sx * 1.35);
    var cx = (minX + maxX) / 2, cy = (minY + maxY) / 2;
    nodes.forEach(function (p) {
      p.x = W / 2 + (p.x - cx) * s;
      p.y = H / 2 + (p.y - cy) * sY;
    });
    // remove overlaps
    for (var pass = 0; pass < 24; pass++) {
      var moved = false;
      for (i = 0; i < n; i++) {
        a = nodes[i];
        for (j = i + 1; j < n; j++) {
          b = nodes[j];
          dx = b.x - a.x; dy = b.y - a.y;
          var min = a.r + b.r + 3;
          d2 = dx * dx + dy * dy;
          if (d2 < min * min) {
            d = Math.sqrt(d2) || 0.01;
            var push = (min - d) / 2;
            dx = dx / d; dy = dy / d;
            a.x -= dx * push; a.y -= dy * push;
            b.x += dx * push; b.y += dy * push;
            moved = true;
          }
        }
      }
      if (!moved) break;
    }
    nodes.forEach(function (p) {
      p.x = Math.max(p.r + 6, Math.min(W - p.r - 6, p.x));
      p.y = Math.max(p.r + 6, Math.min(H - p.r - 6, p.y));
    });
  }

  /* ---------------- render ---------------- */
  var nodeEls = [], labelEls = [], linkEls = [], rendered = false;

  function shape(p) {
    var cls = 'a-gn a-gn-' + (p.kind === 'skill' ? 'skill' : p.kind === 'system' ? 'sys' : 'ref') + (p.deg ? '' : ' a-gn-iso');
    var x = p.x.toFixed(1), y = p.y.toFixed(1);
    if (p.kind === 'skill') return '<circle class="' + cls + '" cx="' + x + '" cy="' + y + '" r="' + p.r.toFixed(1) + '"/>';
    if (p.kind === 'system') {
      var q = p.r * 1.25;
      return '<path class="' + cls + '" d="M' + x + ' ' + (p.y - q).toFixed(1) + 'L' + (p.x + q).toFixed(1) + ' ' + y +
        'L' + x + ' ' + (p.y + q).toFixed(1) + 'L' + (p.x - q).toFixed(1) + ' ' + y + 'Z"/>';
    }
    var h = p.r * 0.92;
    return '<rect class="' + cls + '" x="' + (p.x - h).toFixed(1) + '" y="' + (p.y - h).toFixed(1) + '" width="' + (h * 2).toFixed(1) +
      '" height="' + (h * 2).toFixed(1) + '" rx="2"/>';
  }

  function textFor(p) {
    var right = p.x < W - 190;
    var x = right ? p.x + p.r + 6 : p.x - p.r - 6;
    return '<text class="a-gt" x="' + x.toFixed(1) + '" y="' + (p.y + 5).toFixed(1) + '"' +
      (right ? '' : ' text-anchor="end"') + '>' + esc(label(p)) + '</text>';
  }

  function render() {
    if (rendered) return;
    rendered = true;
    computeLayout();
    var html = '<g class="a-g-links">';
    links.forEach(function (l) {
      html += '<line class="a-gl-link" x1="' + l.s.x.toFixed(1) + '" y1="' + l.s.y.toFixed(1) + '" x2="' + l.t.x.toFixed(1) + '" y2="' + l.t.y.toFixed(1) + '"/>';
    });
    html += '</g><g class="a-g-nodes">';
    nodes.forEach(function (p) { html += shape(p); });
    html += '</g><g class="a-g-labels">';
    nodes.forEach(function (p) { html += textFor(p); });
    html += '</g>';
    svg.innerHTML = html;
    linkEls = Array.prototype.slice.call(svg.querySelectorAll('.a-gl-link'));
    nodeEls = Array.prototype.slice.call(svg.querySelectorAll('.a-gn'));
    labelEls = Array.prototype.slice.call(svg.querySelectorAll('.a-gt'));
    // resting labels: the most connected nodes whose labels do not collide
    var boxes = [], shown = 0;
    for (var o = 0; o < order.length && shown < 11 && o < 24; o++) {
      var p = order[o];
      var wdt = label(p).length * 8.4 + 4, right = p.x < W - 190;
      var bx = right ? p.x + p.r + 6 : p.x - p.r - 6 - wdt, by = p.y - 11;
      var clash = boxes.some(function (b) { return bx < b[0] + b[2] && bx + wdt > b[0] && by < b[1] + b[3] && by + 16 > b[1]; });
      if (clash) continue;
      boxes.push([bx, by, wdt, 16]);
      labelEls[p.i].classList.add('is-rest');
      shown++;
    }
    loading.hidden = true;
  }

  /* ---------------- highlight ---------------- */
  var hot = [], current = -1, pinned = -1, kbIndex = -1;

  function clearHot() {
    for (var h = 0; h < hot.length; h++) hot[h].classList.remove('is-hot', 'is-me');
    hot = [];
    svg.classList.remove('a-g-svg-focus');
  }

  function listHTML(arr, max) {
    var sorted = arr.slice().sort(function (a, b) { return b.deg - a.deg || (a.id < b.id ? -1 : 1); });
    var out = sorted.slice(0, max).map(function (n) { return '<li>' + esc(label(n)) + '</li>'; });
    if (sorted.length > max) out.push('<li class="a-more">and ' + (sorted.length - max) + ' more</li>');
    return '<ul class="a-g-insp-list">' + out.join('') + '</ul>';
  }

  function describe(p) {
    var h = '<p class="a-g-insp-name">' + esc(fullName(p)) + '</p>' +
      '<p class="a-g-insp-meta">' + kindName(p) + ', ' + linkWord(p.deg) + '</p>';
    if (p.out.length) h += '<p class="a-g-insp-h">Points to (' + p.out.length + ')</p>' + listHTML(p.out, 14);
    if (p.inn.length) h += '<p class="a-g-insp-h">Pointed to by (' + p.inn.length + ')</p>' + listHTML(p.inn, 14);
    if (!p.deg) h += '<p class="a-g-insp-note">This skill file links to no other skill or shared doc.</p>';
    else if (p.kind !== 'skill' && p.inn.length > 2) h += '<p class="a-g-insp-note">One shared doc, many readers: these skills point to it instead of keeping their own copy.</p>';
    return h;
  }

  function hint() {
    return '<p class="a-g-insp-hint">Point at any node, or focus the graph and use the arrow keys.</p>';
  }

  function syncHubs() {
    Array.prototype.forEach.call(hubsEl.querySelectorAll('.a-g-hub'), function (b) {
      b.setAttribute('aria-pressed', String(Number(b.getAttribute('data-i')) === pinned));
    });
  }

  function focusNode(i) {
    if (i === current) return;
    current = i;
    clearHot();
    if (i < 0) { insp.innerHTML = hint(); return; }
    var p = nodes[i];
    if (rendered) {
      svg.classList.add('a-g-svg-focus');
      var add = function (el, me) { if (!el) return; el.classList.add('is-hot'); if (me) el.classList.add('is-me'); hot.push(el); };
      add(nodeEls[i], true); add(labelEls[i], true);
      var nb = p.out.concat(p.inn).sort(function (x, y) { return y.deg - x.deg; });
      nb.forEach(function (q, k) { add(nodeEls[q.i]); if (k < 10) add(labelEls[q.i]); });
      p.links.forEach(function (j) { add(linkEls[j]); });
    }
    insp.innerHTML = describe(p);
  }

  function pin(i) {
    pinned = i;
    syncHubs();
    focusNode(i);
  }

  /* pointer: nearest node within a finger-sized radius */
  function nearest(evt) {
    var m = svg.getScreenCTM();
    if (!m) return -1;
    var pt = svg.createSVGPoint();
    pt.x = evt.clientX; pt.y = evt.clientY;
    var sp = pt.matrixTransform(m.inverse());
    var scale = Math.abs(m.a) || 1;
    var best = -1, bestD = Infinity;
    for (var i = 0; i < nodes.length; i++) {
      var p = nodes[i], dx = p.x - sp.x, dy = p.y - sp.y, d = dx * dx + dy * dy;
      var lim = Math.max(p.r + 7, 18 / scale);
      if (d < lim * lim && d < bestD) { best = i; bestD = d; }
    }
    return best;
  }
  svg.addEventListener('pointermove', function (e) {
    if (!rendered || e.pointerType === 'touch') return;
    insp.setAttribute('aria-live', 'off');
    var i = nearest(e);
    focusNode(i > -1 ? i : pinned);
    svg.style.cursor = i > -1 ? 'pointer' : '';
  });
  svg.addEventListener('pointerleave', function () {
    if (!rendered) return;
    focusNode(pinned);
  });
  svg.addEventListener('click', function (e) {
    if (!rendered) return;
    insp.setAttribute('aria-live', 'off');
    var i = nearest(e);
    pin(i === pinned ? -1 : i);
    kbIndex = i > -1 ? order.indexOf(nodes[i]) : -1;
  });

  /* keyboard on the stage: step through nodes, most connected first */
  stage.addEventListener('keydown', function (e) {
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    var k = e.key, next = null;
    if (k === 'ArrowRight' || k === 'ArrowDown') next = kbIndex < 0 ? 0 : Math.min(order.length - 1, kbIndex + 1);
    else if (k === 'ArrowLeft' || k === 'ArrowUp') next = kbIndex < 0 ? 0 : Math.max(0, kbIndex - 1);
    else if (k === 'Home') next = 0;
    else if (k === 'End') next = order.length - 1;
    else if (k === 'Escape') {
      if (pinned < 0 && current < 0) return;
      e.preventDefault(); e.stopPropagation();
      kbIndex = -1; pin(-1);
      return;
    } else if (k === ' ' || k === 'Enter') { e.preventDefault(); e.stopPropagation(); return; }
    else return;
    e.preventDefault(); e.stopPropagation();
    if (!order.length) return;
    kbIndex = next;
    insp.setAttribute('aria-live', 'polite');
    pin(order[kbIndex].i);
  });

  hubsEl.addEventListener('click', function (e) {
    var b = e.target.closest('.a-g-hub');
    if (!b) return;
    var i = Number(b.getAttribute('data-i'));
    insp.setAttribute('aria-live', 'polite');
    kbIndex = pinned === i ? -1 : order.indexOf(nodes[i]);
    pin(pinned === i ? -1 : i);
  });

  /* ---------------- list view ---------------- */
  var listBuilt = false;
  function names(arr) {
    return arr.slice().sort(function (a, b) { return a.id < b.id ? -1 : 1; }).map(function (n) { return esc(fullName(n)); }).join(', ');
  }
  function buildList() {
    if (listBuilt) return;
    listBuilt = true;
    var groups = [['skill', 'Skills'], ['reference', 'Reference docs'], ['system', 'System docs']];
    listEl.innerHTML = groups.map(function (g) {
      var items = order.filter(function (n) { return n.kind === g[0]; });
      if (!items.length) return '';
      return '<h3>' + g[1] + ' (' + items.length + ')</h3><ul>' + items.map(function (n) {
        var h = '<li><span class="a-gli-name">' + esc(fullName(n)) + '</span><span class="a-gli-n">' + linkWord(n.deg) + '</span>';
        if (n.out.length) h += '<p><b>Points to:</b> ' + names(n.out) + '</p>';
        if (n.inn.length) h += '<p><b>Pointed to by:</b> ' + names(n.inn) + '</p>';
        if (!n.deg) h += '<p>No links to other skills or shared docs.</p>';
        return h + '</li>';
      }).join('') + '</ul>';
    }).join('');
  }

  var view = window.innerWidth < 640 ? 'list' : 'graph';
  function setView(v) {
    view = v;
    btnGraph.setAttribute('aria-pressed', String(v === 'graph'));
    btnList.setAttribute('aria-pressed', String(v === 'list'));
    viewGraph.hidden = v !== 'graph';
    viewList.hidden = v !== 'list';
    if (v === 'list') buildList(); else if (isActive()) render();
  }
  btnGraph.addEventListener('click', function () { setView('graph'); });
  btnList.addEventListener('click', function () { setView('list'); });

  function isActive() { return slide.classList.contains('active') && !slide.hidden; }
  function ensure() { if (view === 'graph') render(); else buildList(); }

  setView(view);
  if (typeof MBT.on === 'function') {
    MBT.on('slide', function (p) { if (p && p.id === 'graph') ensure(); });
  }
  if (typeof MBT.current === 'function') {
    try { var c = MBT.current(); if (c && c.id === 'graph') ensure(); } catch (e) { /* core not ready */ }
  }
  if (isActive()) ensure();
  if (typeof MBT.on !== 'function') {
    window.addEventListener('load', function () { ensure(); });
  }
})();
