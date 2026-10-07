#!/usr/bin/env python3
"""Incrementally refresh graphify-out using a direct LLM backend.

The existing graph's built_at_commit is the baseline. Only supported files
changed since that commit are re-extracted, then merged into the graph. In CI,
the OpenAI-compatible backend is GitHub Models authenticated with the ephemeral
GITHUB_TOKEN, so no repository API-key secret is required.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-dir", type=Path, default=Path("."))
    parser.add_argument("--graph", type=Path, default=Path("graphify-out/graph.json"))
    parser.add_argument("--base", help="Override graph.json built_at_commit")
    parser.add_argument("--backend", default=os.environ.get("GRAPHIFY_BACKEND", "openai"))
    parser.add_argument("--model", default=os.environ.get("GRAPHIFY_MODEL", "openai/gpt-4.1-mini"))
    parser.add_argument(
        "--semantic-mode",
        choices=("deterministic", "auto", "model"),
        default=os.environ.get("GRAPHIFY_SEMANTIC_MODE", "deterministic"),
        help="Document extraction mode (default: deterministic, no credentials)",
    )
    # GitHub Models currently caps gpt-4.1-mini request bodies at 8k tokens.
    # Leave room for Graphify's extraction system prompt and file wrappers.
    parser.add_argument("--token-budget", type=int, default=5_000)
    parser.add_argument("--max-concurrency", type=int, default=2)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


def ensure_commit(repo: Path, revision: str) -> None:
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(
            f"Graph baseline {revision!r} is not available in this checkout. "
            "Fetch full history or perform a manual full graph refresh."
        )


def changed_paths(repo: Path, base: str, head: str) -> tuple[set[str], set[str]]:
    raw = subprocess.check_output(
        ["git", "diff", "--name-status", "-z", f"{base}..{head}"], cwd=repo
    ).decode("utf-8", errors="surrogateescape")
    fields = raw.split("\0")
    if fields and fields[-1] == "":
        fields.pop()
    changed: set[str] = set()
    removed: set[str] = set()
    index = 0
    while index < len(fields):
        status = fields[index]
        index += 1
        kind = status[:1]
        if kind in {"R", "C"}:
            old_path, new_path = fields[index : index + 2]
            index += 2
            changed.add(new_path)
            if kind == "R":
                removed.add(old_path)
        else:
            path = fields[index]
            index += 1
            if kind == "D":
                removed.add(path)
            else:
                changed.add(path)
    return changed, removed


def relative_file_map(detection: dict, repo: Path) -> tuple[dict[str, str], dict[str, Path]]:
    categories: dict[str, str] = {}
    paths: dict[str, Path] = {}
    for category, entries in detection.get("files", {}).items():
        for entry in entries:
            path = Path(entry).resolve()
            try:
                relative = path.relative_to(repo).as_posix()
            except ValueError:
                continue
            categories[relative] = category
            paths[relative] = path
    return categories, paths


def combine_extractions(*results: dict) -> dict:
    merged = {
        "nodes": [],
        "edges": [],
        "hyperedges": [],
        "input_tokens": 0,
        "output_tokens": 0,
    }
    for result in results:
        merged["nodes"].extend(result.get("nodes", []))
        merged["edges"].extend(result.get("edges", []))
        merged["hyperedges"].extend(result.get("hyperedges", []))
        merged["input_tokens"] += int(result.get("input_tokens", 0) or 0)
        merged["output_tokens"] += int(result.get("output_tokens", 0) or 0)
    return merged


def normalize_source(value: str | None, repo: Path) -> str | None:
    if not value:
        return None
    path = Path(value)
    if path.is_absolute():
        try:
            return path.resolve().relative_to(repo).as_posix()
        except ValueError:
            return path.as_posix()
    relative = path.as_posix()
    return relative[2:] if relative.startswith("./") else relative


def graph_sources(raw_graph: dict, repo: Path) -> set[str]:
    sources: set[str] = set()
    for item in [*raw_graph.get("nodes", []), *raw_graph.get("links", raw_graph.get("edges", []))]:
        source = normalize_source(item.get("source_file"), repo)
        if source:
            sources.add(source)
    return sources


def source_label(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")[:8_000]
    except OSError:
        text = ""
    patterns = (
        r"(?m)^name:\s*['\"]?([^'\"\n]+)",
        r"(?m)^#\s+(.+)$",
        r"(?is)<title[^>]*>(.*?)</title>",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return " ".join(match.group(1).split())
    return " ".join(Path(path).stem.replace("_", " ").replace("-", " ").split()).title()


class HeadingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.active_tag: str | None = None
        self.buffer: list[str] = []
        self.title = ""
        self.headings: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"title", "h1", "h2", "h3"}:
            self.active_tag = tag
            self.buffer = []

    def handle_data(self, data: str) -> None:
        if self.active_tag:
            self.buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != self.active_tag:
            return
        text = " ".join("".join(self.buffer).split())
        if text:
            if tag == "title":
                self.title = text
            else:
                self.headings.append((tag, text))
        self.active_tag = None
        self.buffer = []


def structured_document_fallback(source: str, path: Path) -> dict:
    from graphify.ids import make_id

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        text = ""
    file_id = make_id(source)
    label = source_label(path)
    nodes = [
        {
            "id": file_id,
            "label": label,
            "file_type": "document",
            "source_file": source,
            "source_location": "L1",
        }
    ]
    edges: list[dict] = []
    children: list[tuple[str, str]] = []

    if path.suffix.lower() in {".html", ".htm"}:
        parser = HeadingParser()
        parser.feed(text)
        if parser.title:
            nodes[0]["label"] = parser.title
        children = parser.headings
    elif path.suffix.lower() in {".yml", ".yaml"}:
        jobs_block = False
        for line in text.splitlines():
            if re.match(r"^jobs:\s*$", line):
                jobs_block = True
                continue
            if jobs_block and line and not line.startswith(" "):
                jobs_block = False
            match = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line) if jobs_block else None
            if match:
                children.append(("job", match.group(1).replace("-", " ").title()))

    seen: set[str] = set()
    for kind, child_label in children:
        normalized = child_label.casefold()
        if normalized in seen:
            continue
        seen.add(normalized)
        child_id = make_id(source, kind, child_label)
        nodes.append(
            {
                "id": child_id,
                "label": child_label,
                "file_type": "section",
                "source_file": source,
                "source_location": None,
            }
        )
        edges.append(
            {
                "source": file_id,
                "target": child_id,
                "relation": "contains",
                "confidence": "EXTRACTED",
                "confidence_score": 1.0,
                "source_file": source,
                "source_location": None,
                "weight": 1.0,
            }
        )
    return {"nodes": nodes, "edges": edges, "hyperedges": []}


def prepare_semantic_result(result: dict, expected: set[str], paths: dict[str, Path], repo: Path) -> dict:
    if result.get("failed_chunks"):
        raise SystemExit(
            f"Semantic extraction failed for {result['failed_chunks']} chunk(s); "
            "refusing to prune the existing graph."
        )

    # A model may assign a referenced filename as source_file even though that
    # file was not in its input chunk. Keep only evidence attributed to files we
    # actually sent, then guarantee one source-backed node per input.
    cleaned = dict(result)
    cleaned["nodes"] = []
    for node in result.get("nodes", []):
        source = normalize_source(node.get("source_file"), repo)
        if source in expected:
            cleaned["nodes"].append({**node, "source_file": source})
    cleaned["edges"] = []
    for edge in result.get("edges", []):
        source = normalize_source(edge.get("source_file"), repo)
        if source in expected:
            cleaned["edges"].append({**edge, "source_file": source})

    covered = {
        source
        for node in cleaned["nodes"]
        if (source := normalize_source(node.get("source_file"), repo))
    }
    missing = sorted(expected - covered)
    if missing:
        from graphify.ids import make_id

        print(
            "Semantic extraction emitted no valid node for "
            + ", ".join(missing)
            + "; adding deterministic source stubs."
        )
        for source in missing:
            cleaned["nodes"].append(
                {
                    "id": make_id(source),
                    "label": source_label(paths[source]),
                    "file_type": "document",
                    "source_file": source,
                    "source_location": "L1",
                }
            )
    return cleaned


def deterministic_document_extraction(paths: list[Path], expected: set[str], path_map: dict[str, Path], repo: Path, extract) -> dict:
    result = extract(paths, cache_root=repo) if paths else {"nodes": [], "edges": []}
    covered = {
        source
        for node in result.get("nodes", [])
        if (source := normalize_source(node.get("source_file"), repo)) in expected
    }
    for source in sorted(expected - covered):
        fallback = structured_document_fallback(source, path_map[source])
        result.setdefault("nodes", []).extend(fallback["nodes"])
        result.setdefault("edges", []).extend(fallback["edges"])
    result.setdefault("hyperedges", [])
    result.setdefault("input_tokens", 0)
    result.setdefault("output_tokens", 0)
    return prepare_semantic_result(result, expected, path_map, repo)


def previous_community_state(raw_graph: dict) -> tuple[dict[str, int], dict[int, str]]:
    node_community: dict[str, int] = {}
    names: dict[int, Counter[str]] = {}
    for node in raw_graph.get("nodes", []):
        node_id = node.get("id")
        raw_cid = node.get("community")
        if node_id is None or raw_cid is None:
            continue
        try:
            cid = int(raw_cid)
        except (TypeError, ValueError):
            continue
        node_community[str(node_id)] = cid
        name = node.get("community_name")
        if name and not re.fullmatch(r"Community \d+", str(name)):
            names.setdefault(cid, Counter())[str(name)] += 1
    labels = {cid: counts.most_common(1)[0][0] for cid, counts in names.items() if counts}
    return node_community, labels


def fallback_community_label(graph, members: list[str], cid: int) -> str:
    candidates = []
    for node_id in members:
        data = graph.nodes[node_id]
        label = str(data.get("label") or node_id).strip()
        file_type = str(data.get("file_type") or "")
        if not label or file_type == "file" or "/" in label or "\\" in label:
            continue
        candidates.append((graph.degree(node_id), label))
    candidates.sort(key=lambda item: (-item[0], item[1].lower()))
    labels: list[str] = []
    for _, label in candidates:
        clean = " ".join(label.replace("_", " ").split())
        if clean.lower() not in {item.lower() for item in labels}:
            labels.append(clean)
        if len(labels) == 2:
            break
    if not labels:
        return f"Community {cid}"
    return " and ".join(labels)[:80]


def _frontmatter_name(path: Path) -> str | None:
    """Return the `name:` value from a markdown frontmatter block, or None."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    fm = text[3:end] if end != -1 else text
    m = re.search(r"^name:\s*(.+?)\s*$", fm, re.MULTILINE)
    return m.group(1).strip() if m else None


def _parse_agent_registry(readme: Path) -> list[tuple[list[str], list[str]]]:
    """Parse the ownership table in .claude/agents/README.md.

    Returns rows of (router_slugs, specialist_display_names) from the
    "which skill-agent owns which specialists" table. Skips narrative rows.
    """
    text = readme.read_text(encoding="utf-8")
    parts = text.split("## Registry: which skill-agent owns which specialists", 1)
    if len(parts) < 2:
        return []
    body = parts[1].split("\n## ", 1)[0]
    rows: list[tuple[list[str], list[str]]] = []
    for line in body.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0].startswith("---") or cells[0].startswith("Skill-agent"):
            continue
        routers = re.findall(r"`/([^`]+)`", cells[0])           # /paid-acquisition-agent
        specialists = re.findall(r"`([^`]+)`", cells[1])         # display names
        if routers and specialists:
            rows.append((routers, specialists))
    return rows


def inject_delegates_to_edges(graph, repo: Path) -> int:
    """Add deterministic `delegates_to` edges from each skill-agent (router) to the
    specialist subagents it invokes, per the registry in .claude/agents/README.md.

    Routing is structured data that scripts/lint_agents.py already validates in both
    directions, so these are EXTRACTED (confidence 1.0) edges from a source of truth
    rather than model inference. Regenerated in full each run (idempotent): every
    existing delegates_to edge is dropped first so renames/removals leave no stragglers.
    """
    readme = repo / ".claude/agents/README.md"
    if not readme.exists():
        return 0

    def _line(data: dict) -> int:
        loc = data.get("source_location")
        if isinstance(loc, str) and loc.startswith("L") and loc[1:].isdigit():
            return int(loc[1:])
        return 10 ** 9

    # representative node per source file = its lowest-line node (the file root / H1)
    rep: dict[str, str] = {}
    for nid, data in graph.nodes(data=True):
        src = (data.get("source_file") or "").replace("./", "")
        if not src:
            continue
        if src not in rep or _line(data) < _line(graph.nodes[rep[src]]):
            rep[src] = nid

    # specialist display name -> agent file (relative posix), from on-disk frontmatter
    name_to_src: dict[str, str] = {}
    for p in (repo / ".claude/agents").rglob("*.md"):
        nm = _frontmatter_name(p)
        if nm:
            name_to_src[nm] = p.relative_to(repo).as_posix()

    # rebuild from scratch: drop stale delegates_to edges first
    stale = [(u, v) for u, v, d in graph.edges(data=True) if d.get("relation") == "delegates_to"]
    graph.remove_edges_from(stale)

    added = 0
    for routers, specialists in _parse_agent_registry(readme):
        for slug in routers:
            src_node = rep.get(f".claude/skills/{slug}/SKILL.md")
            if src_node is None:
                continue
            for disp in specialists:
                agent_src = name_to_src.get(disp)
                tgt_node = rep.get(agent_src) if agent_src else None
                # skip unresolved endpoints and never clobber a pre-existing edge
                if tgt_node is None or src_node == tgt_node or graph.has_edge(src_node, tgt_node):
                    continue
                graph.add_edge(
                    src_node,
                    tgt_node,
                    relation="delegates_to",
                    confidence="EXTRACTED",
                    confidence_score=1.0,
                    weight=1.0,
                    source_file=".claude/agents/README.md",
                    source_location=None,
                )
                added += 1
    return added


def main() -> int:
    args = parse_args()
    repo = args.repo_dir.resolve()
    graph_path = args.graph if args.graph.is_absolute() else repo / args.graph
    if not graph_path.exists():
        raise SystemExit(f"Existing graph not found: {graph_path}")

    raw_graph = json.loads(graph_path.read_text(encoding="utf-8"))
    base = args.base or raw_graph.get("built_at_commit")
    if not base:
        raise SystemExit("graph.json has no built_at_commit; pass --base explicitly.")
    ensure_commit(repo, base)
    head = git(repo, "rev-parse", "HEAD")
    changed, removed = changed_paths(repo, base, head)

    # Delay graphify imports until after argument/baseline checks. This keeps
    # --dry-run useful in environments that have not installed graphify yet.
    from graphify.detect import detect

    detection = detect(repo)
    categories, detected_paths = relative_file_map(detection, repo)
    existing_sources = graph_sources(raw_graph, repo)
    supported_changed = sorted(path for path in changed if path in categories)
    removed_indexed = removed & existing_sources
    became_unindexed = (changed & existing_sources) - set(categories)
    # build_merge replaces every source present in the new extraction itself.
    # prune_sources is only for files that have no replacement.
    prune_sources = sorted(removed_indexed | became_unindexed)

    if not supported_changed and not removed_indexed and not became_unindexed:
        print(f"Graph is current at {head[:8]}; no indexed files changed.")
        return 0

    by_category = Counter(categories[path] for path in supported_changed)
    print(
        f"Graph update {base[:8]}..{head[:8]}: {len(supported_changed)} indexed change(s), "
        f"{len(removed_indexed)} indexed deletion(s); categories={dict(sorted(by_category.items()))}"
    )
    if args.dry_run:
        for path in supported_changed:
            print(f"  {categories[path]}: {path}")
        for path in sorted(removed_indexed | became_unindexed):
            print(f"  deleted: {path}")
        return 0

    from graphify.analyze import god_nodes, suggest_questions, surprising_connections
    from graphify.build import build_merge
    from graphify.cluster import cluster, remap_communities_to_previous, score_all
    from graphify.export import to_json
    from graphify.extract import extract
    from graphify.report import generate

    code_paths = [detected_paths[path] for path in supported_changed if categories[path] == "code"]
    semantic_rel = {
        path for path in supported_changed if categories[path] in {"document", "paper", "image"}
    }
    semantic_paths = [detected_paths[path] for path in sorted(semantic_rel)]

    ast_result = extract(code_paths, cache_root=repo) if code_paths else {"nodes": [], "edges": []}
    if semantic_paths and args.semantic_mode == "deterministic":
        semantic_result = deterministic_document_extraction(
            semantic_paths, semantic_rel, detected_paths, repo, extract
        )
    elif semantic_paths:
        from graphify.llm import extract_corpus_parallel

        semantic_result = extract_corpus_parallel(
            semantic_paths,
            backend=args.backend,
            api_key=os.environ.get("OPENAI_API_KEY") if args.backend == "openai" else None,
            model=args.model,
            root=repo,
            token_budget=args.token_budget,
            max_concurrency=args.max_concurrency,
        )
        if semantic_result.get("failed_chunks") and args.semantic_mode == "auto":
            print("Model extraction failed; falling back to deterministic document structure.")
            semantic_result = deterministic_document_extraction(
                semantic_paths, semantic_rel, detected_paths, repo, extract
            )
        else:
            semantic_result = prepare_semantic_result(semantic_result, semantic_rel, detected_paths, repo)
    else:
        semantic_result = {"nodes": [], "edges": [], "hyperedges": []}

    extraction = combine_extractions(ast_result, semantic_result)
    directed = bool(raw_graph.get("directed", False))
    graph = build_merge(
        [extraction],
        graph_path=str(graph_path),
        prune_sources=prune_sources or None,
        directed=directed,
        root=repo,
    )

    # Deterministic routing layer: inject `delegates_to` edges from the agent registry
    # (a source of truth CI validates), so the graph models which skill-agent invokes
    # which specialist - a relationship the LLM extractor cannot resolve across files.
    # Runs on the full merged graph before clustering, so the edges shape communities too.
    delegated = inject_delegates_to_edges(graph, repo)
    if delegated:
        print(f"Injected {delegated} delegates_to edge(s) from the agent registry.")

    previous_membership, previous_labels = previous_community_state(raw_graph)
    communities = cluster(graph)
    if previous_membership:
        communities = remap_communities_to_previous(communities, previous_membership)
    labels = {
        cid: previous_labels.get(cid) or fallback_community_label(graph, members, cid)
        for cid, members in communities.items()
    }
    cohesion = score_all(graph, communities)
    gods = god_nodes(graph)
    surprises = surprising_connections(graph, communities)
    questions = suggest_questions(graph, communities, labels)
    token_cost = {
        "input": extraction.get("input_tokens", 0),
        "output": extraction.get("output_tokens", 0),
    }

    report = generate(
        graph,
        communities,
        cohesion,
        labels,
        gods,
        surprises,
        detection,
        token_cost,
        ".",
        suggested_questions=questions,
        built_at_commit=head,
    )
    to_json(
        graph,
        communities,
        str(graph_path),
        force=True,
        built_at_commit=head,
        community_labels=labels,
    )
    (graph_path.parent / "GRAPH_REPORT.md").write_text(report.rstrip() + "\n", encoding="utf-8")
    # No stock graph.html. graphify's to_html hard-raises above GRAPHIFY_VIZ_NODE_LIMIT
    # (5000 by default) and this repo's graph passed that in Aug 2026, which failed the
    # merge-time graph-build job on every merge and froze graph.json and the embeddings
    # index behind it. The stock viewer was redundant anyway: scripts/graph_explorer.py
    # builds graph-explorer.html from the same graph.json, has no node limit, and is the
    # viewer CLAUDE.md points the team at. Raising the cap would only keep committing a
    # 5 MB generated file nobody opens, and would break again at the next threshold.
    print(
        f"Graph refreshed: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges, "
        f"{len(communities)} communities; semantic tokens={token_cost['input']}/{token_cost['output']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
