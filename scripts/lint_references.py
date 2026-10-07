#!/usr/bin/env python3
"""Fail a PR when a skill, agent, or doc points at a file that isn't in the repo.

This exists because of a real incident. `inbound-demo-reply/SKILL.md` was merged to
main carrying six references to `pain-map.md`, a file that only ever lived on a
feature branch. Every run from main would have followed an instruction to read a
file that wasn't there. Nothing caught it: the frontmatter lint only checks
frontmatter, and the routing eval only checks descriptions.

The rule this enforces: if a tracked file tells a reader to open something, that
something must exist on the same branch.

Scope is deliberately narrow to keep false positives near zero:
  - Only backticked tokens ending in a known file extension are treated as paths.
  - A token with a slash resolves from the repo root, then from the referring
    file's own directory.
  - A bare filename resolves from the referring file's own directory only.
  - Tokens with globs, angle-bracket placeholders, or URLs are skipped.
  - ALLOWLIST below carries the handful of references that are optional by design.

The repo carries a pre-existing backlog of dangling references (208 at the time
this was written), so a repo-wide block would fail every PR and get switched off
within a week. Instead:

  * `--changed-only <base-ref>` blocks on references introduced or touched by THIS
    PR. That is what CI gates on, and it is what makes the process airtight going
    forward.
  * A bare run scans everything and reports the whole backlog for cleanup. It is
    advisory, not a gate.

Usage:
    python3 scripts/lint_references.py                      # full scan, advisory
    python3 scripts/lint_references.py --changed-only main  # gate, blocks on new
Exit 0 clean, 1 on any missing reference in scope.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCAN_GLOBS = [
    ".claude/skills",
    ".claude/agents",
    "references",
    "systems",
    "docs",
]
SCAN_ROOT_FILES = ["CLAUDE.md", "PHILOSOPHY.md"]

# Directories mirrored verbatim from an upstream project. Their docs name files the
# tool creates at runtime (`DESIGN.md`, `.impeccable/config.json`, `report.json`), so
# they are dangling by design, and editing them is pointless because the next update
# overwrites the directory. Each entry names its doc so the exception stays explained.
VENDORED_DIRS = {
    # Impeccable design skill; update procedure and rationale in docs/impeccable.md.
    os.path.join(".claude", "skills", "impeccable"),
}

EXTENSIONS = (".md", ".py", ".json", ".xlsx", ".csv", ".html", ".yml", ".yaml", ".jsonl", ".sql")

# References that are optional by design. Each needs a reason: an entry without
# one is how this file rots into a suppression dump.
ALLOWLIST = {
    # inbound-demo-reply explicitly guards this one: "IF it exists ... Never block a
    # run on this file being missing."
    "references/product-details.md",
    "product-details.md",
    # Written at runtime by the skill on first use, not committed.
    "volume-baseline.json",
    # Local-only working file, deliberately gitignored (contains prospect PII).
    "outreach-log.xlsx",
    # Hand-built preview shell for the daily-report build folder; git-ignored with
    # the rest of tools/daily-reports/build/. The doc that names it says so.
    "tools/daily-reports/build/preview_wrapper.html",
    # Dated draft bodies the evening run writes locally before presenting;
    # gitignored (contains prospect PII). The token is an illustrative date
    # placeholder (YYYY-MM-DD), not a committed file.
    "drafts/YYYY-MM-DD-evening.md",
    # Illustrative path examples in graphify/extraction-spec.md that teach the
    # node-ID format (path + symbol -> id, e.g. src/auth/session.py + ValidateToken
    # -> auth_session_validatetoken). Not references to real repo files.
    "src/auth/session.py",
    "lib/utils/helpers.py",
    "tests/test_foo.py",
    "setup.py",
    # Claude Code's per-person settings file: git-ignored by design, so it never
    # exists on a branch. The vendored impeccable hooks reference names it.
    ".claude/settings.local.json",
    # Written by `/impeccable init` and `/impeccable hooks` at runtime, never shipped
    # with the vendored skill. Docs that explain the skill have to name them; rationale
    # in docs/impeccable.md.
    "PRODUCT.md",
    "DESIGN.md",
    ".impeccable/config.json",
    ".impeccable/config.local.json",
    # The user's own product context file. The copytemplates skills search the
    # user's folders for it at run time and create it on first use; it is never
    # committed here.
    "context_copytemplates.md",
    "context_copytemplates_acme.md",
    # Working files the carousel specialist writes in its own run workspace
    # (marketing-carousel-growth-engine.md), not files in this repo.
    "learnings.json",
    "./carousel-data/learnings.json",
    "analysis.json",
    "post-info.json",
    "slide-prompts.json",
    "generate_image.py",
    # Scratch files graphify writes into graphify-out/ during a run; the skill
    # docs name them so the steps can read them back. Never committed.
    ".graphify_detect.json",
    ".graphify_labels.json",
    ".graphify_semantic_new.json",
    "graphify-out/.graphify_analysis.json",
    "graphify-out/.graphify_chunk_NN.json",
    "graphify-out/.graphify_detect.json",
    "graphify-out/.graphify_semantic.json",
    "graphify-out/.graphify_transcripts.json",
    # Files in the upstream agent-flow repo (a local clone), which the
    # systems/reference/agent-flow*.md docs describe. Not files in this repo.
    "pnpm-workspace.yaml",
    "tsconfig.json",
    "web/tsconfig.json",
    # File-type names in prose ("instructions (`.md`)", "the `.patch.md` notes"),
    # not references to one file.
    ".md",
    ".py",
    ".patch.md",
}

TOKEN_RE = re.compile(r"`([^`\n]+?)`")
# A token with whitespace is a shell command or prose, not a path. Globs, angle
# placeholders, URLs and shell metachars are likewise not checkable paths.
SKIP_SUBSTRINGS = ("*", "<", ">", "http://", "https://", "{", "}", "$", "|", " ", "\t")
# Generic self-references that name a file type rather than a specific file.
SKIP_EXACT = {"SKILL.md", "CLAUDE.md", "README.md"}


def skill_root(path):
    """Nearest enclosing .claude/skills/<name>/ directory, if any.

    A skill's own docs reference siblings relative to the skill root
    (`assets/dashboard.html` from `knowledge/dashboard-spec.md`), not relative to
    the referring file.
    """
    parts = os.path.abspath(path).split(os.sep)
    for i in range(len(parts) - 1, 1, -1):
        if parts[i - 2 : i] == [".claude", "skills"]:
            return os.sep.join(parts[: i + 1])
    return None


def iter_files():
    for rel in SCAN_ROOT_FILES:
        p = os.path.join(ROOT, rel)
        if os.path.isfile(p):
            yield p
    for base in SCAN_GLOBS:
        for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, base)):
            dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "plugin-skills")]
            if os.path.relpath(dirpath, ROOT) in VENDORED_DIRS:
                dirnames[:] = []
                continue
            for fn in filenames:
                if fn.endswith(".md"):
                    yield os.path.join(dirpath, fn)


def candidate_paths(text):
    for m in TOKEN_RE.finditer(text):
        tok = m.group(1).strip()
        if not tok or tok in SKIP_EXACT or any(s in tok for s in SKIP_SUBSTRINGS):
            continue
        if not tok.lower().endswith(EXTENSIONS):
            continue
        if tok.startswith(("/", "~")):  # absolute host paths are not repo refs
            continue
        yield tok, text[: m.start()].count("\n") + 1


def changed_files(base_ref):
    """Markdown files added or modified relative to the merge base."""
    try:
        base = subprocess.check_output(
            ["git", "merge-base", "HEAD", base_ref], cwd=ROOT, text=True
        ).strip()
        out = subprocess.check_output(
            ["git", "diff", "--name-only", "--diff-filter=AM", base, "HEAD"],
            cwd=ROOT,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        print(f"lint_references: could not diff against {base_ref}: {exc}", file=sys.stderr)
        sys.exit(2)
    return {
        os.path.join(ROOT, line.strip())
        for line in out.splitlines()
        if line.strip().endswith(".md")
    }


def main():
    scope = None
    if "--changed-only" in sys.argv:
        i = sys.argv.index("--changed-only")
        if i + 1 >= len(sys.argv):
            print("lint_references: --changed-only needs a base ref", file=sys.stderr)
            return 2
        scope = changed_files(sys.argv[i + 1])
        if not scope:
            print("lint_references: no markdown changed in this PR, nothing to check.")
            return 0

    missing = []
    for path in iter_files():
        if scope is not None and os.path.abspath(path) not in {os.path.abspath(p) for p in scope}:
            continue
        rel_file = os.path.relpath(path, ROOT)
        try:
            text = open(path, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        own_dir = os.path.dirname(path)
        for tok, line in candidate_paths(text):
            if tok in ALLOWLIST or os.path.basename(tok) in ALLOWLIST:
                continue
            bases = [ROOT, own_dir]
            sroot = skill_root(path)
            if sroot:
                bases.append(sroot)
            if any(os.path.exists(os.path.join(b, tok)) for b in bases):
                continue
            missing.append((rel_file, line, tok))

    for rel_file, line, tok in missing:
        print(
            f"::error file={rel_file},line={line}::References `{tok}`, which does not "
            f"exist on this branch. Land the file in the same PR, or remove the reference."
        )

    if missing:
        where = "in the files this PR touches" if scope is not None else "repo-wide"
        print(f"\n{len(missing)} dangling reference(s) {where}.", file=sys.stderr)
        if scope is not None:
            print(
                "Land the missing file in this PR, or drop the reference. "
                "A merged instruction to read a file that isn't there is a broken run.",
                file=sys.stderr,
            )
        return 1
    print("lint_references: OK, every referenced file resolves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
