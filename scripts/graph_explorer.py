#!/usr/bin/env python3
"""Build graphify-out/graph-explorer.html - an enhanced, Riverside-branded
interactive viewer for the knowledge graph.

Why this exists
---------------
The stock viewer at graphify-out/graph.html is produced by the installed
`graphify` tool and is overwritten on every `graphify update .`. This script is a
repo-owned enhancement layer: it reads the same graphify-out/graph.json and
writes a separate graph-explorer.html, so our UI improvements survive every
graph rebuild instead of being clobbered.

It is now also the only viewer we ship. The stock graph.html is git-ignored and
CI no longer builds it, because graphify's to_html hard-fails above 5000 nodes
and this repo's graph passed that in Aug 2026. This script has no node limit.

Keep it fresh
-------------
Run after any graph rebuild:  python scripts/graph_explorer.py
CI runs it automatically in the graph-build job (doc-agent-on-merge.yml).

Zero third-party dependencies (Python stdlib only). vis-network is loaded from a
CDN with subresource integrity, matching the stock viewer.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Riverside brand theme lives in graphify-theme.json at the repo root so the
# team can tune the palette without touching this script. It is the same file
# the (planned) graphify fork reads, so both viewers stay visually consistent.
# The constants below are fallbacks used only when that file is missing.
THEME_PATH = Path(__file__).resolve().parent.parent / "graphify-theme.json"

# Qualitative palette for communities, brand purples first, all legible on the
# dark Riverside background. Cycled by community rank.
COMMUNITY_COLORS = [
    "#7C5CFF", "#9671FF", "#B43DFF", "#E961FF", "#5353FC",
    "#50C9FF", "#67FFB1", "#C2FF44", "#FF8A00", "#FFEC45",
    "#b377ff", "#27ae60", "#f2994a", "#56ccf2", "#bb6bd9", "#f25757",
    "#9bdb4d", "#48c1e0", "#ff9f7f", "#a0e2bc", "#d5c7ff", "#ffd166",
]

# File-type accent colors (used for the type chips and type filter dots).
FILE_TYPE_COLORS = {
    "code": "#50C9FF",
    "document": "#7C5CFF",
    "concept": "#67FFB1",
    "rationale": "#FFEC45",
    "image": "#E961FF",
    "": "#888888",
}

# vis-network node shape per file_type (color still encodes community). The
# shape group we use ("dot", "square", "diamond", "triangle", "hexagon") all
# draw the label below the marker, so labels stay consistent across types.
SHAPES_BY_FILE_TYPE = {
    "document": "dot",
    "concept": "hexagon",
    "code": "square",
    "rationale": "diamond",
    "image": "triangle",
}

# Dark-chrome CSS variables. graphify-theme.json overrides bg/panel/border/
# text/text_secondary/accent; the rest are derived from those at build time.
CHROME = {
    "bg": "#0F0F14",
    "panel": "#1C1C24",
    "border": "#2A2A35",
    "text": "#FFFFFF",
    "text_secondary": "#E6E6EB",
    "accent": "#7C5CFF",
}


def _hex_rgb(hexstr: str) -> tuple[int, int, int]:
    h = hexstr.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _mix(hexstr: str, toward: tuple[int, int, int], amount: float) -> str:
    r, g, b = _hex_rgb(hexstr)
    tr, tg, tb = toward
    def m(a, t):
        return round(a + (t - a) * amount)
    return f"#{m(r, tr):02x}{m(g, tg):02x}{m(b, tb):02x}"


def load_theme() -> None:
    """Merge graphify-theme.json over the module-level fallbacks (in place)."""
    if not THEME_PATH.exists():
        return
    try:
        theme = json.loads(THEME_PATH.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        print(f"[graph_explorer] could not read {THEME_PATH}: {exc}; using defaults.",
              file=sys.stderr)
        return
    if theme.get("community_colors"):
        # Keep the extra fallback hues after the branded ones so large graphs
        # with many communities never run out of distinct colors.
        branded = list(theme["community_colors"])
        COMMUNITY_COLORS[:] = branded + [c for c in COMMUNITY_COLORS if c not in branded]
    for ft, shape in (theme.get("shapes_by_file_type") or {}).items():
        SHAPES_BY_FILE_TYPE[ft] = shape
    CHROME.update({k: v for k, v in (theme.get("chrome") or {}).items() if k in CHROME})


def _chrome_css() -> str:
    """Build the dark-theme :root declaration from CHROME (with derived tokens)."""
    bg, panel, border = CHROME["bg"], CHROME["panel"], CHROME["border"]
    text, accent = CHROME["text"], CHROME["accent"]
    white = (255, 255, 255)
    ar, ag, ab = _hex_rgb(accent)
    return (
        f"  --bg: {bg}; --panel: {panel}; --panel-2: {_mix(panel, white, 0.06)}; "
        f"--line: {border};\n"
        f"  --line-2: {_mix(border, white, 0.12)}; --text: {text}; --muted: #888c99; "
        f"--muted-2: {CHROME['text_secondary']};\n"
        f"  --accent: {accent}; --accent-strong: {_mix(accent, (0, 0, 0), 0.12)}; "
        f"--accent-soft: rgba({ar},{ag},{ab},0.15);\n"
        f"  --canvas: {bg}; --label: {text}; --shadow: rgba(0,0,0,0.5);"
    )


def _links(data: dict) -> list:
    return data.get("links") or data.get("edges") or []


def build(graph_path: Path, out_path: Path) -> None:
    load_theme()
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    links = _links(data)
    hyperedges = data.get("hyperedges", [])

    if not nodes:
        print(f"[graph_explorer] {graph_path} has no nodes; nothing to build.", file=sys.stderr)
        return

    id2node = {n["id"]: n for n in nodes}

    # Degree (undirected) plus directional counts for the inspection panel.
    degree: Counter = Counter()
    out_edges: dict[str, list] = defaultdict(list)
    in_edges: dict[str, list] = defaultdict(list)
    for e in links:
        s, t = e.get("source"), e.get("target")
        if s is None or t is None:
            continue
        degree[s] += 1
        degree[t] += 1
        out_edges[s].append(e)
        in_edges[t].append(e)
    max_deg = max(degree.values(), default=1) or 1

    # Community membership and a human label per community (highest-degree member).
    comm_members: dict = defaultdict(list)
    for n in nodes:
        comm_members[n.get("community")].append(n["id"])
    comm_label: dict = {}
    for cid, members in comm_members.items():
        rep = max(members, key=lambda m: degree.get(m, 0))
        comm_label[cid] = id2node[rep].get("label", str(cid))

    # Stable, distinct colors: assign palette by community size rank.
    ranked = sorted(comm_members, key=lambda c: (-len(comm_members[c]), str(c)))
    comm_color = {c: COMMUNITY_COLORS[i % len(COMMUNITY_COLORS)] for i, c in enumerate(ranked)}

    # ---- vis nodes ----
    vis_nodes = []
    for n in nodes:
        nid = n["id"]
        cid = n.get("community")
        deg = degree.get(nid, 0)
        color = comm_color.get(cid, "#888888")
        ft = n.get("file_type", "") or ""
        shape = SHAPES_BY_FILE_TYPE.get(ft, "dot")
        # sqrt scaling keeps hubs prominent without dwarfing everything else
        size = round(8 + 26 * (deg / max_deg) ** 0.5, 1)
        # Polygon shapes read smaller than a dot at the same radius, so scale
        # them up a touch to keep the file-type silhouette legible in the graph.
        if shape != "dot":
            size = round(size * 1.35, 1)
        vis_nodes.append({
            "id": nid,
            "label": n.get("label", nid),
            "color": color,
            "size": size,
            "deg": deg,
            "shape": shape,
            "ft": ft,
            "comm": cid,
            "src": n.get("source_file", "") or "",
            "loc": n.get("source_location", "") or "",
            "meta": n.get("metadata", {}) or {},
        })

    # ---- vis edges ----
    vis_edges = []
    for i, e in enumerate(links):
        s, t = e.get("source"), e.get("target")
        if s is None or t is None or s not in id2node or t not in id2node:
            continue
        vis_edges.append({
            "id": i,
            "from": s,
            "to": t,
            "rel": e.get("relation", "") or "",
            "conf": e.get("confidence", "EXTRACTED") or "EXTRACTED",
        })

    # ---- legend / filter metadata ----
    communities = [{
        "cid": cid,
        "label": comm_label.get(cid, str(cid)),
        "color": comm_color.get(cid, "#888888"),
        "count": len(comm_members[cid]),
    } for cid in ranked]

    ft_counts = Counter(n.get("file_type", "") or "" for n in nodes)
    file_types = [{
        "type": ft or "unknown",
        "key": ft,
        "count": c,
        "color": FILE_TYPE_COLORS.get(ft, "#888888"),
        "shape": SHAPES_BY_FILE_TYPE.get(ft, "dot"),
    } for ft, c in ft_counts.most_common()]

    rel_counts = Counter(e["rel"] for e in vis_edges)
    relations = [{"rel": r or "unlabeled", "key": r, "count": c}
                 for r, c in rel_counts.most_common()]

    payload = {
        "nodes": vis_nodes,
        "edges": vis_edges,
        "communities": communities,
        "fileTypes": file_types,
        "relations": relations,
        "hyperedges": hyperedges,
        "maxDeg": max_deg,
        "stats": {
            "nodes": len(vis_nodes),
            "edges": len(vis_edges),
            "communities": len(comm_members),
            "commit": data.get("built_at_commit", ""),
        },
    }

    # Escape </ so embedded JSON can never terminate the <script> element early.
    data_json = json.dumps(payload).replace("</", "<\\/")

    page = _HTML.replace("__CHROME__", _chrome_css()).replace("__DATA__", data_json)
    out_path.write_text(page, encoding="utf-8")
    st = payload["stats"]
    print(f"[graph_explorer] wrote {out_path} "
          f"({st['nodes']} nodes, {st['edges']} edges, {st['communities']} communities)")


# ---------------------------------------------------------------------------
# The page. Data is injected as window.GRAPH via the __DATA__ token so the JS
# body needs no brace-escaping and stays readable.
# ---------------------------------------------------------------------------
_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Team context brain - knowledge graph explorer</title>
<script src="https://unpkg.com/vis-network@9.1.6/standalone/umd/vis-network.min.js"
        integrity="sha384-Ux6phic9PEHJ38YtrijhkzyJ8yQlH8i/+buBR8s3mAZOJrP1gwyvAcIYl3GWtpX1"
        crossorigin="anonymous"></script>
<style>
:root {
__CHROME__
}
body.light {
  --bg: #f2eeff; --panel: #ffffff; --panel-2: #f6f4ff; --line: #e7dfff;
  --line-2: #d5c7ff; --text: #151515; --muted: #666666; --muted-2: #444444;
  --canvas: #fafaff; --label: #1d1d1d; --shadow: rgba(94,58,195,0.15);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: var(--bg); color: var(--text);
  font-family: "Instrument Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  display: flex; flex-direction: column; height: 100vh; overflow: hidden;
  transition: background 0.2s, color 0.2s;
}
#topbar {
  display: flex; align-items: center; gap: 14px; padding: 10px 16px;
  background: var(--panel); border-bottom: 1px solid var(--line); flex-shrink: 0;
}
#topbar .brand { display: flex; align-items: center; gap: 9px; font-weight: 700; font-size: 14px; }
#topbar .brand .mark { width: 12px; height: 12px; border-radius: 3px; background: var(--accent); }
#topbar .stat { font-size: 12px; color: var(--muted); }
#topbar .spacer { flex: 1; }
.tool-btn {
  background: var(--panel-2); border: 1px solid var(--line-2); color: var(--text);
  padding: 6px 11px; border-radius: 6px; font-size: 12px; cursor: pointer;
  font-family: inherit; transition: border-color 0.15s, background 0.15s;
}
.tool-btn:hover { border-color: var(--accent); }
.tool-btn.active { background: var(--accent-soft); border-color: var(--accent); color: var(--accent); }
#main { flex: 1; display: flex; overflow: hidden; }
#graph { flex: 1; background: var(--canvas); }
#sidebar {
  width: 320px; background: var(--panel); border-left: 1px solid var(--line);
  display: flex; flex-direction: column; overflow: hidden; flex-shrink: 0;
}
.panel { border-bottom: 1px solid var(--line); }
.panel h3 {
  font-size: 11px; color: var(--muted); padding: 12px 14px 8px;
  text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600;
}
#search-wrap { padding: 12px 14px; }
#search {
  width: 100%; background: var(--bg); border: 1px solid var(--line-2); color: var(--text);
  padding: 8px 11px; border-radius: 7px; font-size: 13px; outline: none; font-family: inherit;
}
#search:focus { border-color: var(--accent); }
#search-results {
  margin-top: 6px; max-height: 220px; overflow-y: auto; display: none;
  border: 1px solid var(--line); border-radius: 7px; background: var(--bg);
}
.search-item {
  padding: 7px 10px; cursor: pointer; font-size: 12px; display: flex; gap: 8px;
  align-items: center; border-left: 3px solid transparent;
}
.search-item:hover, .search-item.kbd { background: var(--panel-2); }
.search-item .s-label { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.search-item .s-meta { color: var(--muted); font-size: 10px; flex-shrink: 0; }
#scroll { flex: 1; overflow-y: auto; }
#info-content { padding: 4px 14px 14px; font-size: 13px; color: var(--muted-2); line-height: 1.55; }
#info-content .empty { color: var(--muted); font-style: italic; }
.i-title { font-size: 15px; font-weight: 700; color: var(--text); margin-bottom: 8px; word-break: break-word; }
.i-row { display: flex; gap: 8px; margin-bottom: 5px; font-size: 12px; }
.i-row .k { color: var(--muted); min-width: 62px; }
.i-row .v { color: var(--text); word-break: break-word; }
.chip {
  display: inline-block; padding: 1px 8px; border-radius: 10px; font-size: 11px;
  font-weight: 600; color: #0a0a0a;
}
.i-actions { display: flex; gap: 6px; margin: 10px 0 4px; flex-wrap: wrap; }
.edge-group { margin-top: 10px; }
.edge-group .eg-title { font-size: 11px; color: var(--muted); margin-bottom: 4px; }
.edge-link {
  display: flex; gap: 6px; align-items: baseline; padding: 3px 7px; margin: 2px 0;
  border-radius: 5px; cursor: pointer; font-size: 12px; border-left: 3px solid var(--line-2);
}
.edge-link:hover { background: var(--panel-2); }
.edge-link .rel { color: var(--accent); font-size: 10px; flex-shrink: 0; }
.edge-link .nb { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text); }
.edge-link.inferred .rel { opacity: 0.65; font-style: italic; }
.filter-block { padding: 4px 14px 12px; }
.filter-block .fb-head {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;
}
.filter-block .fb-head .mini {
  font-size: 11px; color: var(--accent); cursor: pointer; background: none; border: none;
  font-family: inherit;
}
.slider-row { display: flex; align-items: center; gap: 10px; font-size: 12px; color: var(--muted-2); }
input[type=range] { flex: 1; accent-color: var(--accent); }
.row-item {
  display: flex; align-items: center; gap: 8px; padding: 3px 0; cursor: pointer;
  font-size: 12px; border-radius: 4px;
}
.row-item:hover { color: var(--text); }
.row-item.dimmed { opacity: 0.4; }
.row-item .dot { width: 11px; height: 11px; border-radius: 50%; flex-shrink: 0; }
.row-item .glyph { width: 14px; height: 14px; flex-shrink: 0; display: block; }
.row-item .lbl { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.row-item .cnt { color: var(--muted); font-size: 11px; }
.cb {
  appearance: none; -webkit-appearance: none; width: 14px; height: 14px;
  border: 1.5px solid var(--line-2); border-radius: 3px; background: var(--bg);
  cursor: pointer; position: relative; flex-shrink: 0;
}
.cb:checked { background: var(--accent); border-color: var(--accent); }
.cb:checked::after {
  content: ''; position: absolute; left: 3.5px; top: 1px; width: 4px; height: 7px;
  border: solid #fff; border-width: 0 2px 2px 0; transform: rotate(45deg);
}
.cb:indeterminate { background: var(--accent); border-color: var(--accent); }
.cb:indeterminate::after {
  content: ''; position: absolute; left: 2px; top: 5px; width: 8px; height: 2px;
  background: #fff; transform: none; border: none;
}
#community-list { max-height: 260px; overflow-y: auto; }
#focus-banner {
  display: none; padding: 8px 14px; background: var(--accent-soft);
  border-bottom: 1px solid var(--line); font-size: 12px; color: var(--accent);
  align-items: center; justify-content: space-between; gap: 8px;
}
#focus-banner .clear-x { cursor: pointer; text-decoration: underline; }
::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-thumb { background: var(--line-2); border-radius: 6px; }
::-webkit-scrollbar-track { background: transparent; }
</style>
</head>
<body>
<div id="topbar">
  <div class="brand"><span class="mark"></span>Team context brain</div>
  <span class="stat" id="stat-line"></span>
  <span class="spacer"></span>
  <button class="tool-btn" id="btn-fit">Fit</button>
  <button class="tool-btn" id="btn-physics">Re-layout</button>
  <button class="tool-btn" id="btn-labels">Labels: hubs</button>
  <button class="tool-btn" id="btn-theme">Light</button>
</div>
<div id="main">
  <div id="graph"></div>
  <div id="sidebar">
    <div id="search-wrap" class="panel">
      <input id="search" type="text" placeholder="Search label, file or id..." autocomplete="off">
      <div id="search-results"></div>
    </div>
    <div id="focus-banner">
      <span id="focus-text"></span>
      <span class="clear-x" id="focus-clear">Clear focus</span>
    </div>
    <div id="scroll">
      <div class="panel">
        <h3>Node info</h3>
        <div id="info-content"><span class="empty">Click a node to inspect it</span></div>
      </div>
      <div class="panel">
        <h3>Degree filter</h3>
        <div class="filter-block">
          <div class="slider-row">
            <span>min</span>
            <input type="range" id="deg-slider" min="0" value="0">
            <span id="deg-val">0</span>
          </div>
        </div>
      </div>
      <div class="panel">
        <h3>File types</h3>
        <div class="filter-block" id="filetype-list"></div>
      </div>
      <div class="panel">
        <h3>Relationships</h3>
        <div class="filter-block" id="relation-list"></div>
      </div>
      <div class="panel">
        <h3>Communities</h3>
        <div class="filter-block">
          <div class="fb-head">
            <label class="row-item" style="cursor:pointer">
              <input type="checkbox" class="cb" id="comm-all" checked>
              <span class="lbl">Select all</span>
            </label>
          </div>
          <div id="community-list"></div>
        </div>
      </div>
    </div>
  </div>
</div>

<script>window.GRAPH = __DATA__;</script>
<script>
(function () {
  const G = window.GRAPH;
  const esc = s => String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");

  // ---- lookups ----
  const byId = {};
  G.nodes.forEach(n => { byId[n.id] = n; });
  const commLabel = {}, commColor = {};
  G.communities.forEach(c => { commLabel[c.cid] = c.label; commColor[c.cid] = c.color; });
  const ftColor = {};
  G.fileTypes.forEach(f => { ftColor[f.key] = f.color; });
  // adjacency for focus mode
  const adj = {};
  G.nodes.forEach(n => { adj[n.id] = new Set(); });
  G.edges.forEach(e => { adj[e.from].add(e.to); adj[e.to].add(e.from); });

  // ---- vis datasets ----
  const HUB = Math.max(2, G.maxDeg * 0.15); // label hubs at/above this degree
  let labelMode = "hubs"; // hubs | all | none
  function labelFor(n) {
    if (labelMode === "none") return "";
    if (labelMode === "all") return n.label;
    return n.deg >= HUB ? n.label : "";
  }
  function fontColor() { return getComputedStyle(document.body).getPropertyValue("--label").trim() || "#fff"; }
  function accentColor() { return getComputedStyle(document.body).getPropertyValue("--accent").trim() || "#7C5CFF"; }
  // Small SVG glyph mirroring a node's vis-network shape, for the file-type legend.
  const SHAPE_POLY = {
    square: "1.5,1.5 12.5,1.5 12.5,12.5 1.5,12.5",
    diamond: "7,0.8 13.2,7 7,13.2 0.8,7",
    triangle: "7,1.2 13,12.5 1,12.5",
    triangleDown: "1,1.5 13,1.5 7,12.8",
    hexagon: "7,0.8 12.2,4 12.2,10 7,13.2 1.8,10 1.8,4",
    star: "7,0.8 8.6,5.2 13.2,5.2 9.4,8 10.9,12.5 7,9.7 3.1,12.5 4.6,8 0.8,5.2 5.4,5.2",
  };
  function shapeGlyph(shape, color) {
    const s = shape || "dot";
    let inner;
    if (s === "dot" || s === "ellipse") {
      inner = '<circle cx="7" cy="7" r="6" fill="' + color + '"/>';
    } else if (SHAPE_POLY[s]) {
      inner = '<polygon points="' + SHAPE_POLY[s] + '" fill="' + color + '"/>';
    } else {
      inner = '<rect x="1" y="3" width="12" height="8" rx="2" fill="' + color + '"/>';
    }
    return '<svg class="glyph" viewBox="0 0 14 14" aria-hidden="true">' + inner + '</svg>';
  }

  const nodesDS = new vis.DataSet(G.nodes.map(n => {
    const shaped = n.shape && n.shape !== "dot";
    // Shaped (non-document) nodes get a light rim so the polygon silhouette
    // reads against the same-colored fill; dots keep an invisible border.
    const border = shaped ? "rgba(255,255,255,0.9)" : n.color;
    return {
      id: n.id, label: labelFor(n), title: esc(n.label), size: n.size,
      shape: n.shape || "dot",
      borderWidth: shaped ? 2 : 1.5,
      color: { background: n.color, border: border,
               highlight: { background: "#ffffff", border: n.color } },
      font: { size: 12, color: fontColor() },
    };
  }));
  const edgesDS = new vis.DataSet(G.edges.map(e => ({
    id: e.id, from: e.from, to: e.to,
    title: esc(e.rel + " [" + e.conf + "]"),
    dashes: e.conf !== "EXTRACTED",
    width: e.conf === "EXTRACTED" ? 1.5 : 1,
    color: { opacity: e.conf === "EXTRACTED" ? 0.6 : 0.3 },
    arrows: { to: { enabled: true, scaleFactor: 0.45 } },
  })));

  const container = document.getElementById("graph");
  const network = new vis.Network(container, { nodes: nodesDS, edges: edgesDS }, {
    physics: {
      enabled: true, solver: "forceAtlas2Based",
      forceAtlas2Based: { gravitationalConstant: -60, centralGravity: 0.005,
        springLength: 120, springConstant: 0.08, damping: 0.4, avoidOverlap: 0.8 },
      stabilization: { iterations: 220, fit: true },
    },
    interaction: { hover: true, tooltipDelay: 120, hideEdgesOnDrag: true,
      navigationButtons: false, keyboard: false },
    nodes: { shape: "dot", borderWidth: 1.5 },
    edges: { smooth: { type: "continuous", roundness: 0.2 }, selectionWidth: 3 },
  });
  network.once("stabilizationIterationsDone", () => network.setOptions({ physics: { enabled: false } }));

  // ---- hyperedges (shaded regions) ----
  const hyper = G.hyperedges || [];
  network.on("afterDrawing", ctx => {
    hyper.forEach(h => {
      const ids = (h.nodes || h.members || []).filter(id => byId[id] && !hiddenNodes.has(id));
      const pos = ids.map(id => network.getPositions([id])[id]).filter(Boolean);
      if (pos.length < 2) return;
      const cx = pos.reduce((s, p) => s + p.x, 0) / pos.length;
      const cy = pos.reduce((s, p) => s + p.y, 0) / pos.length;
      const acc = accentColor();
      ctx.save();
      ctx.globalAlpha = 0.10; ctx.fillStyle = acc; ctx.strokeStyle = acc;
      ctx.lineWidth = 2; ctx.beginPath();
      const ex = pos.map(p => ({ x: cx + (p.x - cx) * 1.15, y: cy + (p.y - cy) * 1.15 }));
      ctx.moveTo(ex[0].x, ex[0].y); ex.slice(1).forEach(p => ctx.lineTo(p.x, p.y));
      ctx.closePath(); ctx.fill(); ctx.globalAlpha = 0.35; ctx.stroke();
      ctx.globalAlpha = 0.8; ctx.fillStyle = acc; ctx.font = "bold 11px sans-serif";
      ctx.textAlign = "center"; ctx.fillText(h.label || "", cx, cy - 5);
      ctx.restore();
    });
  });

  // ---- filter state ----
  const hiddenComms = new Set();
  const hiddenTypes = new Set();
  const hiddenRels = new Set();
  let minDeg = 0;
  let focusSet = null; // Set of node ids, or null when not focusing
  const hiddenNodes = new Set();

  function nodeVisible(n) {
    if (focusSet && !focusSet.has(n.id)) return false;
    if (hiddenComms.has(n.comm)) return false;
    if (hiddenTypes.has(n.ft)) return false;
    if (n.deg < minDeg) return false;
    return true;
  }
  function applyFilters() {
    hiddenNodes.clear();
    const nUpd = G.nodes.map(n => {
      const vis_ = nodeVisible(n);
      if (!vis_) hiddenNodes.add(n.id);
      return { id: n.id, hidden: !vis_ };
    });
    nodesDS.update(nUpd);
    const eUpd = G.edges.map(e => ({
      id: e.id,
      hidden: hiddenRels.has(e.rel) || hiddenNodes.has(e.from) || hiddenNodes.has(e.to),
    }));
    edgesDS.update(eUpd);
    const shown = G.nodes.length - hiddenNodes.size;
    document.getElementById("stat-line").textContent =
      shown + " / " + G.stats.nodes + " nodes  ·  " + G.stats.edges +
      " edges  ·  " + G.stats.communities + " communities";
  }

  // ---- node inspection ----
  let histBack = [];
  function showInfo(id, pushHist) {
    const n = byId[id];
    if (!n) return;
    if (pushHist && selected && selected !== id) histBack.push(selected);
    selected = id;
    const outs = G.edges.filter(e => e.from === id);
    const ins = G.edges.filter(e => e.to === id);
    const chip = '<span class="chip" style="background:' + (ftColor[n.ft] || "#888") + '">' +
      esc(n.ft || "unknown") + "</span>";
    const commChip = '<span class="chip" style="background:' + (commColor[n.comm] || "#888") + '">' +
      esc(commLabel[n.comm] || ("Community " + n.comm)) + "</span>";
    function edgeRow(e, other) {
      const nb = byId[other];
      const col = nb ? nb.color : "#888";
      return '<div class="edge-link ' + (e.conf !== "EXTRACTED" ? "inferred" : "") +
        '" style="border-left-color:' + col + '" data-goto="' + esc(other) + '">' +
        '<span class="rel">' + esc(e.rel || "rel") + '</span>' +
        '<span class="nb">' + esc(nb ? nb.label : other) + "</span></div>";
    }
    let metaRows = "";
    Object.keys(n.meta || {}).forEach(k => {
      metaRows += '<div class="i-row"><span class="k">' + esc(k) + '</span><span class="v">' +
        esc(n.meta[k]) + "</span></div>";
    });
    const el = document.getElementById("info-content");
    el.innerHTML =
      '<div class="i-title">' + esc(n.label) + "</div>" +
      '<div class="i-row"><span class="k">Type</span><span class="v">' + chip + "</span></div>" +
      '<div class="i-row"><span class="k">Community</span><span class="v">' + commChip + "</span></div>" +
      '<div class="i-row"><span class="k">Source</span><span class="v">' +
        esc(n.src || "-") + (n.loc ? " " + esc(n.loc) : "") + "</span></div>" +
      '<div class="i-row"><span class="k">Degree</span><span class="v">' + n.deg + "</span></div>" +
      metaRows +
      '<div class="i-actions">' +
        (histBack.length ? '<button class="tool-btn" id="i-back">Back</button>' : "") +
        '<button class="tool-btn" id="i-focus">Focus neighborhood</button>' +
        (focusSet ? '<button class="tool-btn" id="i-unfocus">Clear focus</button>' : "") +
      "</div>" +
      (outs.length ? '<div class="edge-group"><div class="eg-title">Outgoing (' + outs.length +
        ')</div>' + outs.map(e => edgeRow(e, e.to)).join("") + "</div>" : "") +
      (ins.length ? '<div class="edge-group"><div class="eg-title">Incoming (' + ins.length +
        ')</div>' + ins.map(e => edgeRow(e, e.from)).join("") + "</div>" : "");

    el.querySelectorAll("[data-goto]").forEach(node => {
      node.addEventListener("click", () => gotoNode(node.getAttribute("data-goto")));
    });
    const back = document.getElementById("i-back");
    if (back) back.addEventListener("click", () => {
      const prev = histBack.pop(); if (prev) { selected = null; focusNode(prev, false); }
    });
    const foc = document.getElementById("i-focus");
    if (foc) foc.addEventListener("click", () => focusNeighborhood(id));
    const unf = document.getElementById("i-unfocus");
    if (unf) unf.addEventListener("click", clearFocus);
  }
  let selected = null;
  function gotoNode(id) { focusNode(id, true); }
  function focusNode(id, pushHist) {
    if (hiddenNodes.has(id)) { // reveal if filtered out
      focusSet = null; hiddenComms.delete(byId[id].comm); hiddenTypes.delete(byId[id].ft);
      syncFilterUI(); applyFilters();
    }
    network.focus(id, { scale: 1.3, animation: { duration: 400 } });
    network.selectNodes([id]);
    showInfo(id, pushHist);
  }
  function focusNeighborhood(id) {
    focusSet = new Set([id, ...adj[id]]);
    updateFocusBanner();
    applyFilters();
    network.fit({ nodes: [...focusSet], animation: { duration: 400 } });
    showInfo(id, false);
  }
  function clearFocus() { focusSet = null; updateFocusBanner(); applyFilters(); if (selected) showInfo(selected, false); }
  function updateFocusBanner() {
    const b = document.getElementById("focus-banner");
    if (focusSet) {
      b.style.display = "flex";
      document.getElementById("focus-text").textContent =
        "Focused on " + (byId[selected] ? byId[selected].label : "node") + " + " +
        (focusSet.size - 1) + " neighbors";
    } else { b.style.display = "none"; }
  }
  document.getElementById("focus-clear").addEventListener("click", clearFocus);

  network.on("click", params => {
    if (params.nodes.length) { showInfo(params.nodes[0], true); }
    else if (!params.nodes.length) {
      document.getElementById("info-content").innerHTML =
        '<span class="empty">Click a node to inspect it</span>';
      selected = null; histBack = [];
    }
  });
  network.on("doubleClick", params => { if (params.nodes.length) focusNeighborhood(params.nodes[0]); });

  // ---- search (ranked: prefix > word-start > substring), keyboard nav ----
  const searchInput = document.getElementById("search");
  const searchResults = document.getElementById("search-results");
  let kbdIdx = -1, curMatches = [];
  function rank(n, q) {
    const l = n.label.toLowerCase();
    if (l === q) return 0;
    if (l.startsWith(q)) return 1;
    if (l.includes(" " + q) || l.includes("_" + q) || l.includes("-" + q)) return 2;
    if (l.includes(q)) return 3;
    if ((n.src || "").toLowerCase().includes(q)) return 4;
    if (String(n.id).toLowerCase().includes(q)) return 5;
    return 99;
  }
  function renderSearch() {
    searchResults.innerHTML = "";
    if (!curMatches.length) { searchResults.style.display = "none"; return; }
    searchResults.style.display = "block";
    curMatches.forEach((n, i) => {
      const el = document.createElement("div");
      el.className = "search-item" + (i === kbdIdx ? " kbd" : "");
      el.style.borderLeftColor = n.color;
      el.innerHTML = '<span class="s-label">' + esc(n.label) + "</span>" +
        '<span class="s-meta">' + esc(n.ft || "") + " · d" + n.deg + "</span>";
      el.addEventListener("click", () => { pick(n.id); });
      searchResults.appendChild(el);
    });
  }
  function pick(id) {
    gotoNode(id); searchResults.style.display = "none"; searchInput.value = ""; curMatches = []; kbdIdx = -1;
  }
  searchInput.addEventListener("input", () => {
    const q = searchInput.value.toLowerCase().trim();
    kbdIdx = -1;
    if (!q) { curMatches = []; searchResults.style.display = "none"; return; }
    curMatches = G.nodes.map(n => [rank(n, q), n]).filter(x => x[0] < 99)
      .sort((a, b) => a[0] - b[0] || b[1].deg - a[1].deg).slice(0, 40).map(x => x[1]);
    renderSearch();
  });
  searchInput.addEventListener("keydown", e => {
    if (!curMatches.length) return;
    if (e.key === "ArrowDown") { kbdIdx = Math.min(kbdIdx + 1, curMatches.length - 1); renderSearch(); e.preventDefault(); }
    else if (e.key === "ArrowUp") { kbdIdx = Math.max(kbdIdx - 1, 0); renderSearch(); e.preventDefault(); }
    else if (e.key === "Enter") { pick(curMatches[kbdIdx < 0 ? 0 : kbdIdx].id); e.preventDefault(); }
    else if (e.key === "Escape") { searchResults.style.display = "none"; }
  });
  document.addEventListener("click", e => {
    if (!searchResults.contains(e.target) && e.target !== searchInput) searchResults.style.display = "none";
  });

  // ---- filter UIs ----
  // file types
  const ftWrap = document.getElementById("filetype-list");
  G.fileTypes.forEach(f => {
    const row = document.createElement("label");
    row.className = "row-item";
    row.innerHTML = '<input type="checkbox" class="cb" checked>' +
      shapeGlyph(f.shape, f.color) +
      '<span class="lbl">' + esc(f.type) + '</span><span class="cnt">' + f.count + "</span>";
    const cb = row.querySelector("input");
    cb.addEventListener("change", () => {
      if (cb.checked) hiddenTypes.delete(f.key); else hiddenTypes.add(f.key);
      row.classList.toggle("dimmed", !cb.checked); applyFilters();
    });
    ftWrap.appendChild(row);
  });
  // relations
  const relWrap = document.getElementById("relation-list");
  G.relations.forEach(r => {
    const row = document.createElement("label");
    row.className = "row-item";
    row.innerHTML = '<input type="checkbox" class="cb" checked>' +
      '<span class="lbl">' + esc(r.rel) + '</span><span class="cnt">' + r.count + "</span>";
    const cb = row.querySelector("input");
    cb.addEventListener("change", () => {
      if (cb.checked) hiddenRels.delete(r.key); else hiddenRels.add(r.key);
      row.classList.toggle("dimmed", !cb.checked); applyFilters();
    });
    relWrap.appendChild(row);
  });
  // communities
  const commWrap = document.getElementById("community-list");
  const commAll = document.getElementById("comm-all");
  const commRows = {};
  G.communities.forEach(c => {
    const row = document.createElement("label");
    row.className = "row-item";
    row.innerHTML = '<input type="checkbox" class="cb" checked>' +
      '<span class="dot" style="background:' + c.color + '"></span>' +
      '<span class="lbl" title="' + esc(c.label) + '">' + esc(c.label) + '</span>' +
      '<span class="cnt">' + c.count + "</span>";
    const cb = row.querySelector("input");
    cb.addEventListener("change", () => {
      if (cb.checked) hiddenComms.delete(c.cid); else hiddenComms.add(c.cid);
      row.classList.toggle("dimmed", !cb.checked); syncCommAll(); applyFilters();
    });
    commRows[c.cid] = { row, cb };
    commWrap.appendChild(row);
  });
  function syncCommAll() {
    const total = G.communities.length, hid = hiddenComms.size;
    commAll.checked = hid === 0;
    commAll.indeterminate = hid > 0 && hid < total;
  }
  commAll.addEventListener("change", () => {
    const hide = !commAll.checked;
    G.communities.forEach(c => {
      if (hide) hiddenComms.add(c.cid); else hiddenComms.delete(c.cid);
      commRows[c.cid].cb.checked = !hide;
      commRows[c.cid].row.classList.toggle("dimmed", hide);
    });
    commAll.indeterminate = false; applyFilters();
  });
  function syncFilterUI() {
    Object.keys(commRows).forEach(cid => {
      const on = !hiddenComms.has(isNaN(+cid) ? cid : +cid);
      commRows[cid].cb.checked = on; commRows[cid].row.classList.toggle("dimmed", !on);
    });
    syncCommAll();
  }

  // degree slider
  const degSlider = document.getElementById("deg-slider");
  const degVal = document.getElementById("deg-val");
  degSlider.max = Math.min(G.maxDeg, 40);
  degSlider.addEventListener("input", () => {
    minDeg = +degSlider.value; degVal.textContent = degSlider.value; applyFilters();
  });

  // ---- toolbar ----
  document.getElementById("btn-fit").addEventListener("click", () => network.fit({ animation: { duration: 400 } }));
  const physBtn = document.getElementById("btn-physics");
  physBtn.addEventListener("click", () => {
    network.setOptions({ physics: { enabled: true } });
    network.once("stabilizationIterationsDone", () => network.setOptions({ physics: { enabled: false } }));
    network.stabilize(220);
  });
  const labelBtn = document.getElementById("btn-labels");
  labelBtn.addEventListener("click", () => {
    labelMode = labelMode === "hubs" ? "all" : labelMode === "all" ? "none" : "hubs";
    labelBtn.textContent = "Labels: " + labelMode;
    nodesDS.update(G.nodes.map(n => ({ id: n.id, label: labelFor(n) })));
  });
  const themeBtn = document.getElementById("btn-theme");
  themeBtn.addEventListener("click", () => {
    document.body.classList.toggle("light");
    themeBtn.textContent = document.body.classList.contains("light") ? "Dark" : "Light";
    const fc = fontColor();
    nodesDS.update(G.nodes.map(n => ({ id: n.id, font: { size: 12, color: fc } })));
  });

  // ---- init ----
  syncCommAll();
  applyFilters();
})();
</script>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--graph", default="graphify-out/graph.json", help="path to graph.json")
    ap.add_argument("--out", default="graphify-out/graph-explorer.html", help="output HTML path")
    args = ap.parse_args()
    gp = Path(args.graph)
    if not gp.exists():
        print(f"[graph_explorer] {gp} not found. Run a graphify build first.", file=sys.stderr)
        return 1
    build(gp, Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
