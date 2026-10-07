#!/usr/bin/env python3
"""Build Graphify artifacts from tracked, privacy-checked knowledge. No LLM calls."""
import argparse
from collections import Counter
import json
from pathlib import Path
import posixpath
import re
import subprocess
import tempfile
from urllib.parse import quote, unquote, urlsplit

from markdown_it import MarkdownIt

from knowledge_sources import collect_sources, load_fingerprints, validate_outputs
from publish_wiki import MARKER

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN = MarkdownIt("commonmark").enable("table")
SCOPE = ("Structural map: explicit Markdown links, exact skill references, directory membership, "
         "and local code AST extraction. No semantic LLM extraction or API calls. "
         "Missing relationships are not evidence that no relationship exists.")


def markdown_tokens(text):
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end >= 0:
            # Keep line numbers aligned with the source after removing frontmatter.
            text = "\n" * text[:end + 5].count("\n") + text[end + 5:]
    return MARKDOWN.parse(text)


def group_for(name):
    if name.startswith(".claude/skills/"):
        return "Workflow skills"
    if name.startswith(".claude/agents/"):
        return "Specialist personas"
    return {"references": "Reference guidance", "systems": "System templates", "docs": "Documentation", "scripts": "Maintenance code"}.get(name.split("/")[0], "Brain overview")


def document_graph(sources):
    nodes, edges = [], []
    parsed = {name: markdown_tokens(text) for name, text in sources.items() if name.endswith(".md")}
    skills = {Path(name).parent.name: name for name in sources if name.startswith(".claude/skills/") and name.endswith("/SKILL.md")}
    groups = sorted({group_for(name) for name in sources})
    for group in groups:
        nodes.append(dict(id="group:" + group, label=group, file_type="concept", source_file="", source_location="L1"))
    for name in sources:
        title = name
        tokens = parsed.get(name, [])
        for index, token in enumerate(tokens[:-1]):
            if token.type == "heading_open" and token.tag == "h1":
                title = tokens[index + 1].content
                break
        nodes.append(dict(id="doc:" + name, label=title, file_type="document" if name.endswith(".md") else "code", source_file=name, source_location="L1"))
        edges.append(dict(source="group:" + group_for(name), target="doc:" + name, relation="contains", confidence="EXTRACTED", source_file=name, source_location="L1"))

    seen = set()
    for name, tokens in parsed.items():
        for token in tokens:
            if token.type != "inline":
                continue
            line = f"L{token.map[0] + 1}" if token.map else "L1"
            references = []
            for child in token.children or []:
                if child.type == "link_open":
                    url = urlsplit(child.attrGet("href") or "")
                    if not url.scheme and not url.netloc and url.path:
                        path = unquote(url.path)
                        relative = posixpath.normpath(posixpath.join(posixpath.dirname(name), path))
                        if relative in sources:
                            references.append((relative, "references"))
                elif child.type == "code_inline":
                    value = child.content.strip()
                    if value in sources:
                        references.append((value, "references"))
                    if value.lstrip("/") in skills:
                        references.append((skills[value.lstrip("/")], "mentions_skill"))
            # Routing-table cells list exact skill names, often without backticks.
            names = [value.strip() for value in token.content.split(",")]
            if names and all(value in skills for value in names):
                references.extend((skills[value], "mentions_skill") for value in names)
            for target, relation in references:
                key = (name, target, relation)
                if name != target and key not in seen:
                    seen.add(key)
                    edges.append(dict(source="doc:" + name, target="doc:" + target, relation=relation, confidence="EXTRACTED", source_file=name, source_location=line))
    return {"nodes": nodes, "edges": edges}


def export_knowledge(sources, output, repository, revision, fingerprints, working_tree_dirty=False):
    from graphify.analyze import god_nodes, suggest_questions, surprising_connections
    from graphify.build import build_from_json
    from graphify.cluster import cluster, score_all
    from graphify.export import to_html, to_json
    from graphify.extract import extract
    from graphify.report import generate
    from graphify.wiki import to_wiki

    if output.exists():
        raise ValueError("Output directory already exists; choose a fresh directory")
    extraction = document_graph(sources)
    with tempfile.TemporaryDirectory(prefix="brain-corpus-") as directory:
        snapshot = Path(directory).resolve()
        code_paths = []
        for name, content in sources.items():
            if Path(name).suffix not in {".py", ".sh"}:
                continue
            path = snapshot / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            code_paths.append(path)
        if code_paths:
            ast = extract(code_paths, root=snapshot, cache_root=snapshot, parallel=False)
            extraction["nodes"].extend(ast["nodes"])
            extraction["edges"].extend(ast["edges"])
            for node in ast["nodes"]:
                source = node.get("source_file")
                if source in sources:
                    extraction["edges"].append(dict(source="doc:" + source, target=node["id"], relation="declares", confidence="EXTRACTED", source_file=source, source_location=node.get("source_location") or "L1"))
        graph = build_from_json(extraction, root=snapshot)

    if not graph.number_of_nodes():
        raise ValueError("Graphify produced an empty graph")
    communities = cluster(graph)
    cohesion = score_all(graph, communities)
    labels = {}
    for cid, members in communities.items():
        categories = Counter(group_for(graph.nodes[node].get("source_file", "")) for node in members)
        labels[cid] = f"{categories.most_common(1)[0][0]} {cid + 1}"
    hubs = god_nodes(graph)
    output.mkdir(parents=True)
    if not to_json(graph, communities, str(output / "graph.json"), built_at_commit=revision, community_labels=labels):
        raise ValueError("Graph JSON export failed")
    if not to_html(graph, communities, str(output / "graph.html"), community_labels=labels, node_limit=5000):
        raise ValueError("Graph HTML export failed")
    detection = {"total_files": len(sources), "total_words": sum(len(text.split()) for text in sources.values())}
    report = generate(graph, communities, cohesion, labels, hubs, surprising_connections(graph, communities), detection, {"input": 0, "output": 0}, repository, suggested_questions=suggest_questions(graph, communities, labels), built_at_commit=revision)
    (output / "GRAPH_REPORT.md").write_text(f"> {SCOPE}\n\n" + report)

    with tempfile.TemporaryDirectory(prefix="brain-articles-") as directory:
        articles = Path(directory)
        to_wiki(graph, communities, articles, community_labels=labels, cohesion=cohesion, god_nodes_data=hubs)
        mapping = {path.name: "Brain-Article-" + path.name for path in articles.glob("*.md")}
        mapping["index.md"] = "Brain-Home.md"
        wiki = output / "wiki"
        wiki.mkdir()
        wiki_url = f"https://github.com/{repository}/wiki/"
        source_url = f"https://github.com/{repository}/blob/{revision}/"
        for path in sorted(articles.glob("*.md")):
            content = path.read_text()
            for old, new in mapping.items():
                content = content.replace("](" + old + ")", "](" + wiki_url + quote(Path(new).stem, safe="") + ")")
            # Add clickable source references without copying the underlying documents.
            cited = sorted({child.content for token in MARKDOWN.parse(content) for child in token.children or [] if child.type == "code_inline" and child.content in sources})
            if cited:
                content += "\n\n## Source Links\n\n" + "\n".join(f"- [{name}]({source_url}{quote(name, safe='/')})" for name in cited)
            if path.name == "index.md":
                content = "# Marketing Brain Wiki\n\n" + SCOPE + "\n\n" + f"[Start here]({source_url}README.md) | [Company setup]({source_url}docs/NEW-COMPANY-SETUP.md)\n\n" + content
            (wiki / mapping[path.name]).write_text(MARKER + "\n\n" + f"Source revision: `{revision}`\n\n" + content + "\n")
    info = dict(repository=repository, revision=revision, working_tree_dirty=working_tree_dirty, mode="structural-no-llm", files=len(sources), nodes=graph.number_of_nodes(), edges=graph.number_of_edges(), communities=len(communities), input_tokens=0, output_tokens=0, scope=SCOPE)
    (output / "build-info.json").write_text(json.dumps(info, indent=2) + "\n")
    validate_outputs(output, fingerprints)
    print(json.dumps(info, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "graphify-out" / "ci")
    parser.add_argument("--repository", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repository):
        raise ValueError("Invalid repository name")
    fingerprints = load_fingerprints(ROOT)
    sources = collect_sources(ROOT, fingerprints)
    revision = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"]).decode().strip()
    dirty = bool(subprocess.check_output(["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=no"]))
    export_knowledge(sources, args.output.resolve(), args.repository, revision, fingerprints, working_tree_dirty=dirty)


if __name__ == "__main__":
    main()
