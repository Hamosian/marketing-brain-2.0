#!/usr/bin/env python3
"""Lint the specialist subagent layer in `.claude/agents/**`.

Enforces the invariants that `.claude/agents/README.md` claims but nothing checked before:

1. Frontmatter exists and carries `name`, `description`, `model`, and `tools`.
2. `tools:` is explicit and grants no live-system MCP tool. A subagent that inherits every
   session tool can write to HubSpot, Slack, monday, Webflow, and the ad platforms, which
   bypasses the routing layer's confirm-before-mutating gate.
3. `model:` is pinned to the execution-layer default (`sonnet`) unless the file is listed
   in MODEL_EXCEPTIONS with a reason.
4. Every non-exempt subagent carries both harmonized blocks: the Riverside context block
   and the output contract. Without the latter the routing layer has no predictable shape
   to synthesize across specialists.
5. The README registry and the files on disk agree in both directions: every `name:` on
   disk appears in the registry table, and every name in the registry resolves to a file.

Usage:
    python3 scripts/lint_agents.py

Exits 1 on any violation, emitting GitHub Actions `::error` annotations. Stdlib only.
Run from the repo root.
"""

import re
import sys
from pathlib import Path

from agent_blocks import AGENTS_DIR, BLOCKS, agent_files

README = AGENTS_DIR / "README.md"

REQUIRED_KEYS = ("name", "description", "model", "tools", "last-reviewed")

# Subagents cannot carry the repo's usual `<!-- last-reviewed: ... -->` first-line marker,
# because line 1 must be the frontmatter delimiter. They use a frontmatter key instead, so
# /health-check has something to age this layer against. The lint checks the format; the
# staleness judgement is advisory and belongs to /health-check, not to a build failure.
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Tools a specialist may hold. The layer is read-and-author only: it reasons over repo
# context and the public web, and writes files. Live system access stays in the routing
# layer (`.claude/skills/*-agent`), which gates mutations.
ALLOWED_TOOLS = {
    "Read", "Write", "Edit", "Glob", "Grep", "WebFetch", "WebSearch",
    # Bash is allowed only for subagents shipping their own scripts; see BASH_ALLOWED.
    "Bash",
}
# Bash is earned, not inherited. The paid-media set carried it from its upstream personas,
# justified by a live-API extraction workflow that no longer exists in those files -- they
# now work the snapshot /paid-acquisition-agent hands them, so the grant was revoked.
# Carousel Growth Engine keeps it because driving a browser and its publish/analytics
# scripts is its core described workflow.
BASH_ALLOWED = {
    "marketing/marketing-carousel-growth-engine.md",
}

EXPECTED_MODEL = "sonnet"

# Specialists allowed off the Sonnet execution default. These three are judgment-heavy
# rather than mechanical -- they weigh trade-offs and build a case, which is the kind of
# pass the model split reserves for the planning tier. Everything else stays on Sonnet.
MODEL_EXCEPTIONS = {
    "paid-media/paid-media-auditor.md":
        "200+ checkpoint audit; ranks and justifies findings across a whole account",
    "paid-media/paid-media-tracking-specialist.md":
        "attribution and tracking-architecture reasoning, where a wrong call is expensive and quiet",
    "paid-media/paid-media-conversion-psychologist.md":
        "diagnostic reasoning over behavioural models rather than mechanical checks",
}
ALLOWED_MODELS = {"sonnet", "opus"}

# Empty by design. The three former archive candidates were moved to
# docs/archive/agents/ (out of the .claude/agents/** discovery path), so every subagent
# that still loads is expected to meet the full bar: both harmonized blocks and a registry
# entry. Add a path here only with a reason, and prefer archiving over exempting.
HARMONIZE_EXEMPT = set()
REGISTRY_EXEMPT = set()

# Managed marker pairs come from scripts/agent_blocks.py, shared with the harmonizer, so a
# renamed marker cannot be accepted by one script and rejected by the other.


def parse_frontmatter(text):
    """Minimal top-level `key: value` parse. Enough for these files; avoids a pyyaml dep."""
    if not text.startswith("---\n"):
        return None
    body = text[4:].split("\n---", 1)
    if len(body) < 2:
        return None
    out = {}
    for line in body[0].splitlines():
        if not line or line.startswith((" ", "\t", "-", "#")):
            continue  # skip nested keys (e.g. `services:` entries) and comments
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def main():
    """Check every subagent against the layer's invariants.

    Returns a process exit code: 0 when clean, 1 when any violation was found, 2 on a setup
    error such as a missing agents directory.
    """
    errors = []

    def err(path, msg):
        """Record one GitHub-Actions-annotated violation against `path`."""
        errors.append(f"::error file={path}::{msg}")

    if not AGENTS_DIR.is_dir():
        print(f"error: {AGENTS_DIR} not found (run from the repo root)", file=sys.stderr)
        return 2

    files = agent_files()
    if not files:
        print(f"error: no subagents found under {AGENTS_DIR}", file=sys.stderr)
        return 2

    names_on_disk = {}

    for path in files:
        rel_repo = path.as_posix()
        rel = path.relative_to(AGENTS_DIR).as_posix()
        text = path.read_text(encoding="utf-8")

        fm = parse_frontmatter(text)
        if fm is None:
            err(rel_repo, "Missing or malformed YAML frontmatter (must start with ---)")
            continue

        for key in REQUIRED_KEYS:
            if not fm.get(key):
                err(rel_repo, f"Missing '{key}:' in frontmatter")

        # --- tools ---
        raw = fm.get("tools", "")
        if raw:
            granted = {t.strip() for t in raw.split(",") if t.strip()}
            disallowed = sorted(granted - ALLOWED_TOOLS)
            if disallowed:
                err(
                    rel_repo,
                    "tools: grants non-specialist tool(s) "
                    f"{', '.join(disallowed)}. Specialists are read-and-author only; "
                    "live system access belongs to the routing layer.",
                )
            if "Bash" in granted and rel not in BASH_ALLOWED:
                err(
                    rel_repo,
                    "tools: grants Bash but this subagent ships no scripts. "
                    "Add it to BASH_ALLOWED in scripts/lint_agents.py with a reason, or drop Bash.",
                )

        # --- review date ---
        reviewed = fm.get("last-reviewed", "")
        if reviewed and not DATE_RE.match(reviewed):
            err(
                rel_repo,
                f"last-reviewed: '{reviewed}' is not a YYYY-MM-DD date. "
                "/health-check ages this layer off that field.",
            )

        # --- model ---
        model = fm.get("model", "")
        if model and model != EXPECTED_MODEL:
            if rel not in MODEL_EXCEPTIONS:
                err(
                    rel_repo,
                    f"model: is '{model}', expected '{EXPECTED_MODEL}' (execution-layer default). "
                    "Add it to MODEL_EXCEPTIONS in scripts/lint_agents.py with a reason to override.",
                )
            elif model not in ALLOWED_MODELS:
                err(
                    rel_repo,
                    f"model: '{model}' is not one of {sorted(ALLOWED_MODELS)}. "
                    "An escalation still has to name a real tier.",
                )

        # --- harmonization markers ---
        if rel not in HARMONIZE_EXEMPT:
            for block in BLOCKS:
                label, start, end = block.label, block.start, block.end
                if start not in text:
                    err(
                        rel_repo,
                        f"Missing the {label} block ({start}). "
                        "Run scripts/harmonize_agents.py to insert it.",
                    )
                elif end not in text:
                    err(
                        rel_repo,
                        f"{label} block has no closing {end} marker "
                        "(run scripts/harmonize_agents.py)",
                    )

        if fm.get("name"):
            if fm["name"] in names_on_disk:
                err(rel_repo, f"Duplicate agent name '{fm['name']}' (also in {names_on_disk[fm['name']]})")
            else:
                names_on_disk[fm["name"]] = rel

    # --- registry round-trip ---
    if not README.exists():
        err(README.as_posix(), "Missing README.md (holds the specialist registry)")
    else:
        readme = README.read_text(encoding="utf-8")
        # Strip fenced code blocks first: their ``` runs would mis-pair the inline-code
        # regex below and silently swallow the registry table.
        prose = re.sub(r"^```.*?^```", "", readme, flags=re.S | re.M)
        registry = set(re.findall(r"`([^`\n]+)`", prose))
        for name, rel in sorted(names_on_disk.items()):
            if rel in REGISTRY_EXEMPT:
                continue
            if name not in registry:
                err(
                    README.as_posix(),
                    f"Subagent '{name}' ({rel}) is not listed in the registry table. "
                    "Routing is by display name, so an unlisted subagent is unreachable.",
                )
        # Reverse direction: names claimed by the registry tables must exist on disk.
        rows = re.findall(r"^\|\s*`?/?[\w-]+`?\s*\|(.+)\|\s*$", prose, re.M)
        claimed = {n for row in rows for n in re.findall(r"`([^`/\n][^`\n]*)`", row)}
        for name in sorted(claimed - set(names_on_disk)):
            if name.startswith(("model:", ".claude", "scripts/")) or "/" in name:
                continue  # config snippets and paths, not agent names
            err(
                README.as_posix(),
                f"Registry references subagent '{name}' but no file on disk declares that name:",
            )

    for line in errors:
        print(line)

    print(
        f"\nlint_agents: {len(files)} subagent(s) checked, "
        f"{len(names_on_disk)} named, {len(errors)} problem(s)"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
