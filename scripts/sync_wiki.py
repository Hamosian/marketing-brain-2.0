#!/usr/bin/env python3
"""Synchronize the GitHub Wiki from repository source files.

This script is intentionally deterministic and model-free. It runs against a
checked-out wiki repository and only mirrors content that already exists in the
marketing-brain repository.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


REPOSITORY_URL = "https://github.com/riversidefm/marketing-brain"

PAGE_MAP = {
    "CLAUDE.md": "How-This-Repo-Works",
    "PHILOSOPHY.md": "Philosophy",
    "docs/QUICKSTART.md": "Quickstart",
    ".claude/skills/marketing-brain/SKILL.md": "Marketing-OS",
    "systems/owned/hubspot.md": "System-HubSpot",
    "systems/owned/paid-acquisition.md": "System-Paid-Acquisition",
    "systems/owned/marketing-website.md": "System-Marketing-Website",
    "systems/owned/omni-bi.md": "System-Omni-BI",
    "systems/owned/marketing-ops-automation.md": "System-Marketing-Ops-Automation",
    "systems/owned/self-serve-lead-scoring.md": "System-Self-Serve-Lead-Scoring",
    "systems/owned/self-reported-attribution.md": "System-Self-Reported-Attribution",
    "systems/owned/marketing-brain.md": "System-Marketing-Brain",
    "systems/reference/rivermind.md": "System-Rivermind",
    "systems/reference/agent-flow.md": "System-Agent-Flow",
    "systems/reference/data-team.md": "System-Data-Team",
    "systems/reference/marketing-operating-model.md": "System-Marketing-Operating-Model",
    "references/team.md": "Reference-Team-Roster",
    "references/slack.md": "Reference-Slack",
    "references/monday_boards.md": "Reference-Monday-Boards",
    "references/other_teams.md": "Reference-Other-Teams",
    "references/agent-prompting.md": "Reference-Agent-Prompting",
    "references/granola-recipes.md": "Reference-Granola-Recipes",
    "references/growth-reporting.md": "Reference-Growth-Reporting",
    "references/messaging/README.md": "Reference-Messaging",
    "ADS-AUDIT-REPORT.md": "Paid-Ads-Audit-Report",
    "ADS-ACTION-PLAN.md": "Paid-Ads-Action-Plan",
    "ADS-QUICK-WINS.md": "Paid-Ads-Quick-Wins",
    "GOOGLE-ADS-REPORT.md": "Google-Ads-Health-Audit",
    "sql-mql-attribution/INBOUND-SQL-WITHOUT-MQL-ANALYSIS.md": "Inbound-SQL-Without-MQL-Analysis",
    "retros/2026-Q1-marketing-ops.md": "Retro-2026-Q1-Marketing-Ops",
}

PAGE_TITLES = {
    "How-This-Repo-Works": "How this repo works",
    "Marketing-OS": "Marketing OS",
    "System-HubSpot": "HubSpot",
    "System-Omni-BI": "Omni BI",
    "System-Marketing-Ops-Automation": "Marketing Ops Automation",
    "System-Self-Serve-Lead-Scoring": "Self-Serve Lead Scoring",
    "System-Self-Reported-Attribution": "Self-Reported Attribution",
    "System-Marketing-Brain": "Marketing Brain",
    "System-Rivermind": "Rivermind",
    "System-Agent-Flow": "Agent Flow",
    "System-Data-Team": "Data Team",
    "System-Marketing-Operating-Model": "Marketing Operating Model",
    "Reference-Team-Roster": "Team roster",
    "Reference-Monday-Boards": "Monday boards",
    "Reference-Other-Teams": "Other teams",
    "Reference-Agent-Prompting": "Agent prompting",
    "Reference-Granola-Recipes": "Granola recipes",
    "Reference-Growth-Reporting": "Growth reporting",
    "Reference-Messaging": "Messaging",
}

NAVIGATION = {
    "Getting started": [
        ("Quickstart", "Quickstart", "First 30 minutes, first week, first month, decision trees, common pitfalls"),
        ("How this repo works", "How-This-Repo-Works", "Progressive disclosure, the repo map, knowledge routing, task routing"),
        ("Philosophy", "Philosophy", "The five principles, anti-patterns, and what belongs where"),
    ],
    "Operating": [
        ("Marketing OS", "Marketing-OS", "The top-level router, sub-agent registry, and operating state loop"),
        ("Skills catalog", "Skills-Catalog", "All skills, trigger phrases, and when to use them"),
        ("Marketing agents", "Marketing-Agents", "Imported specialist subagents and when to use each"),
    ],
    "Systems we own": [
        ("Marketing Brain", "System-Marketing-Brain", "This repo plus the Marketing OS agent layer"),
        ("Paid Acquisition", "System-Paid-Acquisition", "Ad accounts and their reporting layers"),
        ("Marketing Website", "System-Marketing-Website", "riverside.com pages, experiments, accessibility, and localization"),
        ("HubSpot", "System-HubSpot", "CRM, Pre-Ops, deals, lifecycle, and attribution"),
        ("Omni BI", "System-Omni-BI", "BI layer on Snowflake: models, topics, and dashboards"),
        ("Marketing Ops Automation", "System-Marketing-Ops-Automation", "Lead routing, scoring, workflows, syncs, and conversion uploads"),
        ("Self-Serve Lead Scoring", "System-Self-Serve-Lead-Scoring", "PLG quality scoring and ad-platform quality signals"),
        ("Self-Reported Attribution", "System-Self-Reported-Attribution", "The merged How-did-you-hear-about-us channel"),
    ],
    "Systems we depend on": [
        ("Rivermind", "System-Rivermind", "Analytics team's self-serve data Q&A plugin on Snowflake"),
        ("Agent Flow", "System-Agent-Flow", "Local visualizer for Claude Code and Codex sessions"),
        ("Data Team", "System-Data-Team", "Business Operations data request intake and execution boards"),
        ("Marketing Operating Model", "System-Marketing-Operating-Model", "Growth cadence, measurement stack, data model, and bets"),
    ],
    "References": [
        ("Team roster", "Reference-Team-Roster", "Owners, roles, and reporting lines"),
        ("Slack", "Reference-Slack", "Channels and workspace pointers"),
        ("Monday boards", "Reference-Monday-Boards", "Boards, column keys, and label IDs"),
        ("Other teams", "Reference-Other-Teams", "Cross-functional teams and routing context"),
        ("Agent prompting", "Reference-Agent-Prompting", "Prompting conventions for agents"),
        ("Granola recipes", "Reference-Granola-Recipes", "Meeting-note automation recipes"),
        ("Growth reporting", "Reference-Growth-Reporting", "Reporting definitions and routines"),
        ("Messaging", "Reference-Messaging", "Positioning and messaging source material"),
        ("Design system", "Reference-Design-System", "Product design tokens, components, icons, and brand assets"),
    ],
    "Reports and analyses": [
        ("Paid ads audit", "Paid-Ads-Audit-Report", "Cross-platform paid ads audit"),
        ("Paid ads action plan", "Paid-Ads-Action-Plan", "Prioritized paid ads action plan"),
        ("Paid ads quick wins", "Paid-Ads-Quick-Wins", "High-impact paid ads fixes"),
        ("Google Ads health audit", "Google-Ads-Health-Audit", "Google Ads account health review"),
        ("Inbound SQL without MQL", "Inbound-SQL-Without-MQL-Analysis", "Inbound SQLs that bypassed MQL"),
        ("Q1 FY26 retro", "Retro-2026-Q1-Marketing-Ops", "Marketing Ops quarterly retrospective"),
    ],
}

SKILL_GROUPS = {
    "Entry-point and workflow skills": {
        "access-welcome", "agent-builder", "chief-of-staff", "curious-intern", "data-team-request",
        "good-morning", "granola-recipe-builder", "health-check", "hubspot-workflow-qa",
        "invoice-inbox-to-monday", "list-skills", "marketing-brain", "mops-backlog-review",
        "mops-standup", "nir-monthly-report", "nir-mql-live-report", "nir-weekly-report",
        "p1-p2-followup", "pm-story", "retro", "setup", "team-intro",
        "webflow-locale-publish-queue",
    },
    "Specialist sub-agents": {
        "campaign-agent", "content-agent", "data-agent", "hubspot-agent", "lifecycle-agent",
        "marketing-ops-automation-agent", "measurement-agent", "monday-agent",
        "paid-acquisition-agent", "seo-ai-search-agent", "slack-agent", "website-agent",
    },
    "Domain and tool skills": {
        "gong-calls-explorer", "graphify", "linkedin-best-practices-2026", "marketing-psychology",
        "page-cro", "preop-data-intelligence", "riverside-brand-guidelines",
        "riverside-presentation", "riverside-ux-patterns",
    },
    "Copy template skills": {
        "alliteration-copytemplates", "antithesis-copytemplates",
        "boring-but-works-master-copytemplates", "humor-master-copytemplates",
        "metaphor-copytemplates", "numbers-master-copytemplates",
        "personification-copytemplates", "phrase-play-master-copytemplates",
        "point-of-view-master-copytemplates",
    },
}

SKIP_PREFIXES = (
    ".github/", ".githooks/", "graphify-out/", "ads-audit-data/", "node_modules/",
    "systems/examples/", "docs/presentations/",
)


@dataclass(frozen=True)
class SyncContext:
    revision: str
    date: str
    pr_number: int | None = None
    pr_title: str = "Repository reconciliation"

    @property
    def event_label(self) -> str:
        if self.pr_number is not None:
            return f"[PR #{self.pr_number}]({REPOSITORY_URL}/pull/{self.pr_number})"
        return f"commit `{self.revision[:8]}`"


def git_head(repo: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo, text=True
    ).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-dir", type=Path, default=Path("."))
    parser.add_argument("--wiki-dir", type=Path, required=True)
    parser.add_argument("--pr-context", type=Path)
    parser.add_argument("--changed-files", type=Path)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--no-change-log", action="store_true")
    parser.add_argument("--revision")
    parser.add_argument("--date")
    return parser.parse_args()


def load_context(args: argparse.Namespace, repo: Path) -> tuple[SyncContext, list[str]]:
    revision = args.revision or git_head(repo)
    sync_date = args.date or datetime.now(UTC).date().isoformat()
    pr_number = None
    pr_title = "Repository reconciliation"
    changed: list[str] = []

    if args.pr_context:
        data = json.loads(args.pr_context.read_text(encoding="utf-8"))
        pr_number = int(data["number"])
        pr_title = " ".join(str(data.get("title") or "Merged change").split())
        merged_at = data.get("mergedAt")
        if merged_at and not args.date:
            sync_date = str(merged_at)[:10]

    if args.changed_files:
        changed = [
            line.strip() for line in args.changed_files.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    return SyncContext(revision, sync_date, pr_number, pr_title), changed


def slug_title(value: str) -> str:
    words = re.sub(r"[_-]+", " ", value).split()
    return " ".join(word.upper() if word.lower() in {"bi", "sql", "mql"} else word.capitalize() for word in words)


def derived_page(path: str) -> str | None:
    source = Path(path)
    if path.startswith(("systems/owned/", "systems/reference/")) and source.suffix == ".md":
        if len(source.parts) == 3:
            return f"System-{slug_title(source.stem).replace(' ', '-')}"
    if path.startswith("references/") and source.suffix == ".md":
        if source.name == "README.md":
            name = source.parent.name
        elif len(source.parts) == 2:
            name = source.stem
        else:
            return None
        return f"Reference-{slug_title(name).replace(' ', '-')}"
    if path.startswith("retros/") and source.suffix == ".md":
        return f"Retro-{slug_title(source.stem).replace(' ', '-')}"
    return None


def page_for_source(path: str) -> str | None:
    return PAGE_MAP.get(path) or derived_page(path)


def is_skipped(path: str) -> bool:
    return path.startswith(SKIP_PREFIXES) or path in {"systems/README.md", "references/README.md"}


def targets_for_path(path: str) -> set[str]:
    if is_skipped(path):
        return set()
    targets: set[str] = set()
    mapped = page_for_source(path)
    if mapped:
        targets.add(mapped)
    if path == "README.md":
        targets.add("Home")
    if path.startswith(".claude/skills/") and path.endswith("/SKILL.md"):
        targets.add("Skills-Catalog")
    if path.startswith(".claude/agents/marketing/") or path.startswith(".claude/agents/paid-media/"):
        targets.add("Marketing-Agents")
    if path.startswith("references/design-system/"):
        targets.add("Reference-Design-System")
    return targets


def all_targets(repo: Path) -> set[str]:
    targets = {"Home", "Skills-Catalog", "Marketing-Agents", "Reference-Design-System"}
    targets.update(source_page_map(repo).values())
    return targets


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    return text[end + 5 :] if end != -1 else text


def strip_first_h1(text: str) -> tuple[str | None, str]:
    lines = text.splitlines()
    prefix: list[str] = []
    while lines and (not lines[0].strip() or lines[0].lstrip().startswith("<!--")):
        prefix.append(lines.pop(0))
    title = None
    if lines and lines[0].startswith("# "):
        title = lines.pop(0)[2:].strip()
        while lines and not lines[0].strip():
            lines.pop(0)
    return title, "\n".join(prefix + lines).strip()


def source_page_map(repo: Path) -> dict[str, str]:
    mapping = dict(PAGE_MAP)
    for base in (repo / "systems/owned", repo / "systems/reference", repo / "references", repo / "retros"):
        if not base.exists():
            continue
        for path in base.rglob("*.md"):
            rel = path.relative_to(repo).as_posix()
            page = page_for_source(rel)
            if page:
                mapping[rel] = page
    return mapping


def normalize_repo_path(source: str, target: str) -> tuple[str, str]:
    if "#" in target:
        path_part, fragment = target.split("#", 1)
        suffix = f"#{fragment}"
    else:
        path_part, suffix = target, ""
    if path_part.startswith("/"):
        combined = Path(path_part.lstrip("/"))
    else:
        combined = Path(source).parent / path_part
    parts: list[str] = []
    for part in combined.as_posix().split("/"):
        if part == "..":
            if parts:
                parts.pop()
        elif part not in {"", "."}:
            parts.append(part)
    return "/".join(parts), suffix


def rewrite_links(markdown: str, source: str, mapping: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        label, target = match.group(1), match.group(2).strip()
        if re.match(r"^[a-z]+://", target) or target.startswith(("#", "mailto:")):
            return match.group(0)
        path, suffix = normalize_repo_path(source, target)
        if path in mapping:
            return f"[{label}]({mapping[path]}{suffix})"
        if path:
            return f"[{label}]({REPOSITORY_URL}/blob/main/{path}{suffix})"
        return match.group(0)

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace, markdown)


def write_if_changed(path: Path, content: str) -> bool:
    normalized = content.rstrip() + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == normalized:
        return False
    path.write_text(normalized, encoding="utf-8")
    return True


def page_title(page: str) -> str:
    return PAGE_TITLES.get(page, page.replace("-", " "))


def generated_banner(source: str, context: SyncContext, *, directory: bool = False) -> str:
    url_kind = "tree" if directory else "blob"
    source_url = f"{REPOSITORY_URL}/{url_kind}/main/{source.rstrip('/')}"
    return (
        f"<!-- Generated from {source} by scripts/sync_wiki.py. Source of truth is the repo. "
        "Edit the source and let automation regenerate this page; do not edit the wiki by hand. -->\n\n"
        f"> Mirrored from [`{source}`]({source_url}) in the marketing-brain repo. "
        "The repo is the source of truth."
    )


def mirror_markdown(repo: Path, wiki: Path, source: str, page: str, context: SyncContext, mapping: dict[str, str]) -> bool:
    source_path = repo / source
    target_path = wiki / f"{page}.md"
    if not source_path.exists():
        if target_path.exists():
            target_path.unlink()
            return True
        return False
    raw = strip_frontmatter(source_path.read_text(encoding="utf-8"))
    source_title, body = strip_first_h1(raw)
    title = source_title or page_title(page)
    body = rewrite_links(body, source, mapping)
    content = f"# {title}\n\n{generated_banner(source, context)}\n\n{body}"
    return write_if_changed(target_path, content)


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    lines = text[4:end].splitlines()
    data: dict[str, str] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if not re.match(r"^[A-Za-z_-]+:", line):
            index += 1
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value in {">", ">-", "|", "|-"}:
            folded: list[str] = []
            index += 1
            while index < len(lines) and (lines[index].startswith(" ") or not lines[index].strip()):
                folded.append(lines[index].strip())
                index += 1
            data[key.strip()] = " ".join(part for part in folded if part)
            continue
        if value.startswith(("\"", "'")):
            try:
                value = ast.literal_eval(value)
            except (SyntaxError, ValueError):
                value = value.strip("\"'")
        data[key.strip()] = str(value)
        index += 1
    return data


def short_description(value: str, limit: int = 220) -> str:
    clean = " ".join(value.split()).replace("|", "\\|")
    clean = re.sub(r"^Use this skill when the user asks to ", "", clean, flags=re.IGNORECASE)
    clean = re.sub(r"^Use when ", "", clean, flags=re.IGNORECASE)
    return clean[:limit] + ("..." if len(clean) > limit else "")


def trigger_phrases(description: str) -> str:
    phrases = []
    for phrase in re.findall(r'"([^"]+)"', description):
        phrase = phrase.strip()
        if phrase and len(phrase) <= 60:
            phrases.append(f'"{phrase}"')
    return ", ".join(phrases[:4]) or "n/a"


def generate_skills_catalog(repo: Path, wiki: Path, context: SyncContext) -> bool:
    rows: list[tuple[str, str, str]] = []
    for path in sorted((repo / ".claude/skills").glob("*/SKILL.md")):
        data = parse_frontmatter(path)
        name = data.get("name") or path.parent.name
        description = data.get("description", "")
        rows.append((name, trigger_phrases(description), short_description(description)))

    groups = {heading: set(names) for heading, names in SKILL_GROUPS.items()}
    assigned = set().union(*groups.values())
    extras = {name for name, _, _ in rows} - assigned
    if extras:
        groups["Other skills"] = extras

    lines = [
        "# Skills catalog",
        "",
        generated_banner(".claude/skills/", context, directory=True),
        "",
        f"The {len(rows)} skills in `.claude/skills/`. The exact set is read live by `/list-skills`, so treat that as authoritative if this page drifts.",
        "",
    ]
    by_name = {name: (trigger, description) for name, trigger, description in rows}
    for heading, names in groups.items():
        present = sorted(name for name in names if name in by_name)
        if not present:
            continue
        lines.extend([
            f"## {heading}", "", "| Skill | Trigger phrases | What it does |",
            "|-------|-----------------|--------------|",
        ])
        for name in present:
            trigger, description = by_name[name]
            lines.append(f"| `{name}` | {trigger} | {description} |")
        lines.append("")

    version_path = repo / ".claude/skills/graphify/.graphify_version"
    version = version_path.read_text(encoding="utf-8").strip() if version_path.exists() else "unknown"
    lines.extend([
        "## Vendored skill: graphify", "",
        f"`graphify` is vendored from [safishamsi/graphify](https://github.com/safishamsi/graphify). The recorded project version is `{version}`, and the CLI package is `graphifyy`.",
        "",
        "- **What it does:** turns the codebase into a persistent, queryable knowledge graph with community detection, JSON/HTML output, and an audit report.",
        "- **Trigger:** `/graphify`. Core query commands are `graphify query \"<question>\"`, `graphify path \"<A>\" \"<B>\"`, and `graphify explain \"<concept>\"`.",
        "- **Refresh:** merge-time automation performs incremental semantic extraction through GitHub Models and then rebuilds the Riverside explorer.",
    ])
    return write_if_changed(wiki / "Skills-Catalog.md", "\n".join(lines))


def generate_marketing_agents(repo: Path, wiki: Path, context: SyncContext) -> bool:
    lines = [
        "# Marketing agents", "",
        generated_banner(".claude/agents/", context, directory=True), "",
        "Riverside-aware specialist agents under `.claude/agents/`. Use them for focused execution; use `/marketing-brain` for broad or cross-system work.", "",
    ]
    for folder, heading in (("marketing", "Marketing"), ("paid-media", "Paid media")):
        agents = []
        for path in sorted((repo / ".claude/agents" / folder).glob("*.md")):
            data = parse_frontmatter(path)
            agents.append((data.get("name") or slug_title(path.stem), data.get("description", ""), path))
        lines.extend([
            f"## {heading} ({len(agents)})", "",
            "| Agent | Specialty |", "|-------|-----------|",
        ])
        for name, description, path in agents:
            rel = path.relative_to(repo).as_posix()
            lines.append(f"| [{name}]({REPOSITORY_URL}/blob/main/{rel}) | {short_description(description)} |")
        lines.append("")
    return write_if_changed(wiki / "Marketing-Agents.md", "\n".join(lines))


def generate_design_system(repo: Path, wiki: Path, context: SyncContext, mapping: dict[str, str]) -> bool:
    root = "references/design-system"
    prose = [
        ("README.md", None),
        ("brand/brand.md", "Brand"),
        ("components/components.md", "Components"),
        ("icons/icons.md", "Icons"),
    ]
    lines = ["# Riverside Design System", "", generated_banner(f"{root}/", context, directory=True), ""]
    for rel, heading in prose:
        source = f"{root}/{rel}"
        path = repo / source
        if not path.exists():
            continue
        _, body = strip_first_h1(path.read_text(encoding="utf-8"))
        body = rewrite_links(body, source, mapping)
        if heading:
            lines.extend([f"## {heading}", "", f"Source: [`{rel}`]({REPOSITORY_URL}/blob/main/{source}).", ""])
        lines.extend([body, ""])
    lines.extend([
        "## Data files", "",
        f"Machine-readable tokens, inventories, and the HTML reference remain in [{root}/]({REPOSITORY_URL}/tree/main/{root}) and are not copied into the wiki.",
    ])
    return write_if_changed(wiki / "Reference-Design-System.md", "\n".join(lines))


def navigation_entries(repo: Path) -> dict[str, list[tuple[str, str, str]]]:
    navigation = {section: list(entries) for section, entries in NAVIGATION.items()}
    known = {page for entries in navigation.values() for _, page, _ in entries}
    for source, page in sorted(source_page_map(repo).items()):
        if page in known or page in {"How-This-Repo-Works", "Philosophy", "Quickstart", "Marketing-OS"}:
            continue
        if source.startswith("systems/owned/"):
            section = "Systems we own"
        elif source.startswith("systems/reference/"):
            section = "Systems we depend on"
        elif source.startswith("references/"):
            section = "References"
        elif source.startswith("retros/") or source.endswith("REPORT.md") or "ANALYSIS" in source:
            section = "Reports and analyses"
        else:
            continue
        navigation[section].append((page_title(page), page, f"Mirrored from `{source}`"))
        known.add(page)
    return navigation


def generate_home(repo: Path, wiki: Path) -> bool:
    skill_count = len(list((repo / ".claude/skills").glob("*/SKILL.md")))
    agent_count = sum(1 for folder in ("marketing", "paid-media") for _ in (repo / ".claude/agents" / folder).glob("*.md"))
    lines = [
        "# Riverside marketing team context brain", "",
        "<!-- Generated by scripts/sync_wiki.py. Source of truth is the marketing-brain repo. -->", "",
        f"The Riverside Marketing department's knowledge base for AI, mirrored from the [marketing-brain repo]({REPOSITORY_URL}). The repo is the source of truth; this wiki is a generated, browsable view.", "",
    ]
    for section, entries in navigation_entries(repo).items():
        lines.extend([f"## {section}", ""])
        if section in {"Getting started", "Operating"}:
            lines.extend(["| Page | What it covers |", "|------|----------------|"])
            for label, page, description in entries:
                if page == "Skills-Catalog":
                    description = f"All {skill_count} skills, trigger phrases, and when to use them"
                elif page == "Marketing-Agents":
                    description = f"All {agent_count} specialist agents and when to use them"
                lines.append(f"| [{label}]({page}) | {description} |")
        elif section.startswith("Systems"):
            lines.extend(["| System | Page | In one line |", "|--------|------|-------------|"])
            for label, page, description in entries:
                lines.append(f"| {label} | [{page}]({page}) | {description} |")
        else:
            lines.extend(["| Page | What it covers |", "|------|----------------|"])
            for label, page, description in entries:
                lines.append(f"| [{label}]({page}) | {description} |")
        lines.append("")
    return write_if_changed(wiki / "Home.md", "\n".join(lines))


def generate_sidebar(repo: Path, wiki: Path) -> bool:
    lines = ["### Team context brain", "", "**[Home](Home)**", ""]
    for section, entries in navigation_entries(repo).items():
        lines.append(f"**{section}**")
        for label, page, _ in entries:
            lines.append(f"- [{label}]({page})")
        lines.append("")
    lines.extend(["**Meta**", "- [Recent changes](Recent-Changes)"])
    return write_if_changed(wiki / "_Sidebar.md", "\n".join(lines))


def update_change_log(wiki: Path, context: SyncContext, pages: list[str]) -> bool:
    if not pages:
        return False
    path = wiki / "Recent-Changes.md"
    if path.exists():
        lines = path.read_text(encoding="utf-8").splitlines()
    else:
        lines = [
            "# Recent changes", "",
            "<!-- Maintained by scripts/sync_wiki.py. Each row is one merged change that affected a mirrored page. -->", "",
            "| Date | PR | Change | Pages updated |", "|------|----|--------|---------------|",
        ]
    event = context.event_label
    escaped_title = context.pr_title.replace("|", "\\|")
    row = f"| {context.date} | {event} | {escaped_title} | {', '.join(pages)} |"
    if row in lines:
        return False
    insert_at = next((i for i, line in enumerate(lines) if re.match(r"\| 20\d\d-", line)), len(lines))
    lines.insert(insert_at, row)
    return write_if_changed(path, "\n".join(lines))


def main() -> int:
    args = parse_args()
    repo = args.repo_dir.resolve()
    wiki = args.wiki_dir.resolve()
    if not (repo / ".git").exists():
        raise SystemExit(f"Not a git repository: {repo}")
    if not (wiki / ".git").exists():
        raise SystemExit(f"Not a wiki git repository: {wiki}")
    context, changed_paths = load_context(args, repo)
    if not args.full and not changed_paths:
        print("No changed-file list supplied; nothing to synchronize.")
        return 0

    targets = all_targets(repo) if args.full else set().union(*(targets_for_path(path) for path in changed_paths))
    if not targets:
        print("No wiki-mirrored sources changed.")
        return 0

    mapping = source_page_map(repo)
    changed_pages: list[str] = []
    reverse_map = {page: source for source, page in PAGE_MAP.items()}
    special = {"Home", "Skills-Catalog", "Marketing-Agents", "Reference-Design-System"}
    for page in sorted(targets - special):
        source = reverse_map.get(page)
        if source is None:
            source = next((path for path in changed_paths if page_for_source(path) == page), None)
        if source and mirror_markdown(repo, wiki, source, page, context, mapping):
            changed_pages.append(page)

    if "Skills-Catalog" in targets and generate_skills_catalog(repo, wiki, context):
        changed_pages.append("Skills-Catalog")
    if "Marketing-Agents" in targets and generate_marketing_agents(repo, wiki, context):
        changed_pages.append("Marketing-Agents")
    if "Reference-Design-System" in targets and generate_design_system(repo, wiki, context, mapping):
        changed_pages.append("Reference-Design-System")

    # Navigation is cheap and deterministic. Regenerate it on every mirrored change
    # so skill/agent counts and newly mapped pages cannot drift.
    if generate_home(repo, wiki):
        changed_pages.append("Home")
    if generate_sidebar(repo, wiki):
        changed_pages.append("_Sidebar")

    logged_pages = sorted(dict.fromkeys(changed_pages))
    if not args.no_change_log and update_change_log(wiki, context, logged_pages):
        changed_pages.append("Recent-Changes")

    if changed_pages:
        print("Wiki pages updated: " + ", ".join(sorted(dict.fromkeys(changed_pages))))
    else:
        print("Wiki already matches the repository.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
