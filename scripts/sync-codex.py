#!/usr/bin/env python3
"""Generate the Codex port (AGENTS.md + .agents/skills/) from the Claude source of truth.

The repo maintains a parallel setup so the Marketing OS also runs under OpenAI Codex.
Rather than hand-copy 77 skills (which drifts - it was 47/77 out of sync), we GENERATE
the Codex side deterministically from the Claude side:

  CLAUDE.md          --(substitution table below)-->  AGENTS.md
  .claude/skills/     --(verbatim mirror)-->           .agents/skills/

Skill bodies are copied verbatim (no Claude->Codex text swap): the Codex port is a
LOCATION mirror, not a content fork. Only AGENTS.md - the always-loaded root file -
gets Codex-specific substitutions, and only the few that are actually correct.

What is deliberately NOT mirrored: runtime state the routines write about themselves -
per-skill `data/` directories and `tracking*.md` ledgers. See STATE_* below for why.

`.codex/` (native Codex hook config, a different format from `.claude/hooks`) is NOT
generated here - it is hand-maintained Codex-native config.

Usage:
  python3 scripts/sync-codex.py          regenerate AGENTS.md + .agents/skills/ in place
  python3 scripts/sync-codex.py --check  regenerate, then exit non-zero if the port
                                         committed at HEAD is not what the source
                                         generates (.github/workflows/codex-sync-check.yml)

--check exit codes:
  0  port is in sync AND committed
  1  port was stale - regeneration rewrote it; commit the result
  2  port matches the source but is not committed yet (local pre-commit state;
     a clean CI checkout cannot produce it)
  3  `git status` itself failed, so drift could not be determined - never
     silently green, since a broken repo must not read as a clean one

The gate compares against HEAD, not the working tree, so it CANNOT pass before the
commit: `git add` leaves staged changes visible to `git status --porcelain` and does
not clear it. Expect exit 2 on any pre-commit run that touched a skill or CLAUDE.md.
"""
import fnmatch
import hashlib
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAUDE_MD = os.path.join(REPO, "CLAUDE.md")
AGENTS_MD = os.path.join(REPO, "AGENTS.md")
CLAUDE_SKILLS = os.path.join(REPO, ".claude", "skills")
AGENTS_DIR = os.path.join(REPO, ".agents")
AGENTS_SKILLS = os.path.join(REPO, ".agents", "skills")

GENERATED_HEADER = (
    "<!-- GENERATED from CLAUDE.md by scripts/sync-codex.py. DO NOT EDIT BY HAND.\n"
    "     Edit CLAUDE.md, then run `python3 scripts/sync-codex.py`. -->\n\n"
)

# Ordered, explicit substitutions applied to CLAUDE.md text to produce AGENTS.md.
# Order matters: path rewrites run before the standalone-Claude rewrite so they don't
# collide. Anything not listed here is left byte-identical - in particular the
# "no Anthropic/Claude secret needed" infra note stays, because it is a fact about the
# CI not needing an Anthropic API key, true whichever CLI you run.
SUBSTITUTIONS = [
    ("CLAUDE.md", "AGENTS.md"),          # the always-loaded root filename
    (".claude/skills", ".agents/skills"),  # Codex reads skills from .agents/skills
    (".claude/agents", ".agents/agents"),  # specialist subagent layer, mirrored path
    ("turns Claude from an isolated tool", "turns Codex from an isolated tool"),  # branding line
]


def generate_agents_md():
    with open(CLAUDE_MD, encoding="utf-8") as f:
        text = f.read()
    for old, new in SUBSTITUTIONS:
        text = text.replace(old, new)
    with open(AGENTS_MD, "w", encoding="utf-8") as f:
        f.write(GENERATED_HEADER + text)


# Runtime state the routines write about themselves, excluded from the mirror.
#
# Why: mirroring state makes every routine commit a CI failure for everyone else. A
# cloud routine that appends to its own ledger (say `/invoice-inbox-to-monday` writing
# tracking.md) lands on main without running this script, so the mirror is instantly
# stale and `--check` red-lights every PR branched past that commit until someone
# resyncs by hand. That happened on 8bea6c7 and blocked PR #238. It is not rare: 20
# state files under .claude/skills took ~95 commits in the 60 days to 2026-08-23.
#
# Why deleting the existing copies loses nothing: mirror_skills() rmtree's and rewrites
# the whole tree, so any state a Codex-side run wrote into .agents was destroyed on the
# next sync anyway. These files were never readable-back state shared between the two
# ports - they were a write-only snapshot of the Claude side. Each port keeps its own
# state under its own tree, which is what the relative paths in the skill bodies
# ("data/ledger.md") already imply.
#
# Content that is NOT state and stays mirrored: knowledge/, and assets/ apart from the
# one generated artifact named below.
#
# Why `dashboard.html` is on this list even though it lives under assets/: it carries
# per-run state, so mirroring it guarantees drift. Be precise about what the file is,
# because it is a hybrid and the obvious description is wrong: it is NOT pure build
# output. `growth-marketing-team-tasks/scripts/build_dashboard.py` does a read-modify-
# write - `HTML.read_text()` is the first thing main() does - so the file is a
# hand-maintained HTML shell whose `TASKS` / `READING` / `FOCUS_ORDER` blocks get re-baked
# from that skill's `data/*.md` ledgers. The shell is real content; the baked blocks and
# the timestamp are state.
#
# The state half is what forces the exclusion: every non---check run re-stamps
# `REFRESHED_AT` unconditionally, so the file changes on every routine firing whether or
# not any task data moved. That makes it a guaranteed drift generator, and it was the sole
# content of both manual repair commits, 0e8c973 (2026-08-28) and 42850d6 (2026-09-07, on
# PR #302), across 28 commits in the 60 days to 2026-09-07. Excluded 2026-09-07.
#
# What the port gives up, stated plainly: the Codex side loses the shell too, so a
# Codex-side `build_dashboard.py` would fail at that first `read_text()`. That regresses
# nothing, because the same run already could not work - this script has not mirrored the
# `data/*.md` ledgers it parses since #239. Standing up the dashboard under Codex means
# seeding both the ledgers and a shell in that tree, which is exactly what "each port keeps
# its own state under its own tree" means above.
#
# The other asset in the repo, seo-de-report's font, is a real static asset and stays.
#
# On the `assets/dashboard.html` reference that `knowledge/dashboard-spec.md` makes: it now
# points at a path absent from the mirror. That is the port's existing, deliberate shape,
# not new breakage - 13 mirrored files already reference excluded state paths, this skill's
# own mirrored SKILL.md among them (`data/focus-order.md`, `data/reading-list.md`). Those
# paths resolve per-port at runtime. `scripts/lint_references.py` scans only `.claude/**`,
# so none of them is linted; if SCAN_GLOBS is ever widened to `.agents/**`, the whole class
# needs an exemption together rather than this one file being special-cased.
STATE_DIR_NAMES = {"data"}
STATE_FILE_GLOBS = ("tracking.md", "tracking-*.md", "dashboard.html")


def _ignore_state(dirpath, names):
    """copytree ignore callback: drop per-skill state dirs and tracking ledgers.

    A `data/` directory is state only at the skill root (`<skill>/data/`), which is
    where every routine keeps its ledgers. A `data/` nested deeper is shipped content
    and is mirrored: the vendored impeccable skill carries its Google Fonts
    fingerprint index at `impeccable/scripts/data/`, and dropping it would leave the
    Codex port with a launcher that cannot find its own index (docs/impeccable.md).
    """
    dropped = set()
    at_skill_root = os.path.dirname(os.path.abspath(dirpath)) == os.path.abspath(CLAUDE_SKILLS)
    for name in names:
        full = os.path.join(dirpath, name)
        if os.path.isdir(full) and name in STATE_DIR_NAMES and at_skill_root:
            dropped.add(name)
        elif any(fnmatch.fnmatch(name, pat) for pat in STATE_FILE_GLOBS):
            dropped.add(name)
    return dropped


def mirror_skills():
    # Exact mirror of skill *content*: .agents/skills becomes a copy of .claude/skills
    # minus the runtime state above. Removing the old tree first guarantees deletions
    # propagate (no orphan skills).
    if os.path.isdir(AGENTS_SKILLS):
        shutil.rmtree(AGENTS_SKILLS)
    shutil.copytree(CLAUDE_SKILLS, AGENTS_SKILLS, ignore=_ignore_state)


# --check exit codes. 0 and 1 are the CI contract and must not move; 2 is a
# local-only state that a clean CI checkout cannot reach (see check_state).
EXIT_STALE = 1
EXIT_UNCOMMITTED = 2
EXIT_GIT_ERROR = 3


class GitStatusError(RuntimeError):
    """`git status` did not run. Never treat this as a clean tree."""


def port_status():
    """Porcelain status of the generated paths. Non-empty = differs from HEAD.

    NOTE this reports STAGED changes too (`M ` = staged, worktree clean), so
    `git add` does not empty it. Only a commit does.

    A failing `git status` prints nothing to stdout and exits non-zero, so
    ignoring its return code would make empty stdout indistinguishable from a
    clean tree - the gate would pass on a broken repo, which is the one outcome
    a drift gate must never produce. Raise instead.
    """
    result = subprocess.run(
        ["git", "-C", REPO, "status", "--porcelain", "AGENTS.md", ".agents"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise GitStatusError(
            f"git status exited {result.returncode}: {result.stderr.strip()}"
        )
    return result.stdout.strip()


def port_digest():
    """Order-independent content digest of the generated paths.

    Covers the generated content only - the same STATE_* exclusions the mirror
    applies - so the digest tracks what the generator manages and nothing else.

    Answers the one question git cannot: did *this* regeneration rewrite the
    port, or was the working tree already correct? git compares against HEAD, so
    on its own it cannot separate "port is stale" from "port is right but not
    committed yet" - the two look identical, which is what sent readers in a
    loop following an `add -A` hint that can never clear the gate.
    """
    h = hashlib.sha256()
    paths = []
    if os.path.isfile(AGENTS_MD):
        paths.append(AGENTS_MD)
    for root, dirs, files in os.walk(AGENTS_DIR):
        # Skip exactly what mirror_skills() skips. Runtime state a routine wrote
        # about itself is not generated content: regeneration deletes it, so
        # digesting it would make the port look rewritten when only state moved,
        # and report a transient "stale" on a port that is in fact correct.
        dropped = _ignore_state(root, dirs + files)
        dirs[:] = sorted(d for d in dirs if d not in dropped)
        paths.extend(os.path.join(root, f) for f in files if f not in dropped)
    for path in sorted(paths):
        with open(path, "rb") as fh:
            body = fh.read()
        h.update(os.path.relpath(path, REPO).encode("utf-8"))
        h.update(b"\0")
        h.update(body)
        h.update(b"\0")
    return h.hexdigest()


def check_state(before, after):
    """Classify the port after regeneration. Call with digests taken either side.

    "in-sync"     - committed port matches the source. The only green state.
    "stale"       - regeneration rewrote the port, so what was committed did not
                    match the source. The real failure, and the only one a clean
                    CI checkout can produce.
    "uncommitted" - regeneration changed nothing (the port already matched the
                    source) but the paths still differ from HEAD. Expected when
                    running before the commit; unreachable from a clean checkout.
    """
    if not port_status():
        return "in-sync"
    return "uncommitted" if before == after else "stale"


def main():
    check = "--check" in sys.argv
    # Must be sampled BEFORE regenerating - it is the only record of what the
    # port looked like on the way in.
    before = port_digest() if check else None
    generate_agents_md()
    mirror_skills()
    n_skills = len(next(os.walk(CLAUDE_SKILLS))[1])
    print(f"generated AGENTS.md and mirrored {n_skills} skills into .agents/skills/")
    if not check:
        return

    try:
        state = check_state(before, port_digest())
    except GitStatusError as exc:
        print(f"\nERROR: cannot read the port's git status, so drift is unknowable.\n{exc}")
        sys.exit(EXIT_GIT_ERROR)
    if state == "in-sync":
        print("Codex port is in sync.")
        return

    diff = port_status()
    if state == "stale":
        print("\nERROR: Codex port was OUT OF SYNC with the Claude source.")
        print("The regenerated port is now in your working tree. COMMIT it -")
        print("staging is not enough - alongside the change that caused it:\n")
        print("    git add -A AGENTS.md .agents && git commit\n")
        print(diff)
        sys.exit(EXIT_STALE)

    print("\nPENDING: Codex port matches the Claude source, but is NOT COMMITTED.")
    print("This gate compares against HEAD, so it cannot pass until you commit.")
    print("`git add` does not clear it - staged changes still show here.")
    print("Commit the port in the SAME commit as the change that caused it:\n")
    print("    git commit\n")
    print(diff)
    sys.exit(EXIT_UNCOMMITTED)


if __name__ == "__main__":
    main()
