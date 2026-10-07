#!/usr/bin/env python3
"""Keep the shared blocks in sync across specialist subagents.

Two blocks are managed, each with a canonical source in `.claude/agents/` and a marker
pair delimiting its copy inside every Riverside-aware subagent:

| Block            | Canonical source        | Markers in subagents                              |
|------------------|-------------------------|---------------------------------------------------|
| Riverside context| RIVERSIDE_CONTEXT.md    | <!-- riverside-harmonized --> ... <!-- /... -->   |
| Output contract  | OUTPUT_CONTRACT.md      | <!-- output-contract --> ... <!-- /... -->        |

A block missing from a subagent is appended at the end of the file; a block already
present is replaced in place. Anything outside the markers is never touched -- notably
the per-agent `## How this fits Riverside Marketing` section, which is intentionally
different in every file.

Usage:
    python3 scripts/harmonize_agents.py            # rewrite embedded copies in place
    python3 scripts/harmonize_agents.py --check    # exit 1 if any copy is out of sync

Stdlib only, no dependencies. Run from the repo root.
"""

import sys

from agent_blocks import AGENTS_DIR, BLOCKS, agent_files

# Empty by design -- see HARMONIZE_EXEMPT in scripts/lint_agents.py. Retired personas live
# in docs/archive/agents/, outside this directory, rather than being exempted in place.
EXEMPT = set()


def fail(msg):
    """Abort with a message on stderr and exit 2 (a usage or setup error, not a lint failure)."""
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(2)


def load_canonical(path, canon_markers, start_marker):
    """Extract a block's canonical text from between `canon_markers` in `path`.

    Returns the text stripped of surrounding blank lines, still carrying `start_marker` as
    its first line. Exits non-zero if the file or its markers are missing.
    """
    if not path.exists():
        fail(f"{path} not found (run from the repo root)")
    text = path.read_text(encoding="utf-8")
    begin, end = canon_markers
    try:
        body = text.split(begin, 1)[1].split(end, 1)[0]
    except IndexError:
        fail(f"{path} is missing the {begin} / {end} markers")
    block = body.strip("\n")
    if start_marker not in block:
        fail(f"canonical block in {path} must itself begin with {start_marker}")
    return block


def sync_block(text, canonical, markers):
    """Return (new_text, status) where status is 'ok', 'stale', 'appended', or 'error:...'."""
    start, end = markers

    if start not in text:
        # Block absent entirely -- append it as a new trailing section.
        return text.rstrip("\n") + "\n\n" + canonical + "\n" + end + "\n", "appended"

    pre, rest = text.split(start, 1)
    if end not in rest:
        return text, f"error:found {start} but no closing {end}; add it and re-run"

    current = start + rest.split(end, 1)[0]
    post = rest.split(end, 1)[1]

    if current.strip("\n") == canonical:
        return text, "ok"
    return pre + canonical + "\n" + end + post, "stale"


def main():
    """Sync (or with --check, verify) every managed block across every subagent.

    Returns a process exit code: 0 when everything is in sync or was written successfully,
    1 when --check found drift or any file was malformed.
    """
    args = set(sys.argv[1:])
    check = "--check" in args
    if args - {"--check"}:
        fail(f"unknown argument(s): {' '.join(sorted(args - {'--check'}))}")

    blocks = [
        (b.label, load_canonical(b.canonical, b.canonical_markers, b.start), b.markers)
        for b in BLOCKS
    ]

    files = agent_files(EXEMPT)
    if not files:
        fail(f"no subagent files found under {AGENTS_DIR}")

    problems = []
    in_sync = 0
    changed_files = 0

    for path in files:
        rel = path.as_posix()
        text = original = path.read_text(encoding="utf-8")
        notes = []

        for label, canonical, markers in blocks:
            text, status = sync_block(text, canonical, markers)
            if status.startswith("error:"):
                problems.append((rel, f"{label}: {status.split(':', 1)[1]}"))
            elif status == "ok":
                in_sync += 1
            elif check:
                problems.append((rel, f"{label} block is out of sync with the canonical version"))
            else:
                notes.append(f"{label} {status}")

        if text != original and not check:
            path.write_text(text, encoding="utf-8")
            changed_files += 1
            print(f"updated {rel}  ({', '.join(notes)})")

    for rel, msg in problems:
        print(f"::error file={rel}::{msg}")

    expected = len(files) * len(blocks)
    if check:
        print(
            f"\nchecked {len(files)} subagent(s) x {len(blocks)} block(s): "
            f"{in_sync}/{expected} in sync, {len(problems)} problem(s)"
        )
        if problems:
            print("\nRun `python3 scripts/harmonize_agents.py` to fix.", file=sys.stderr)
            return 1
        return 0

    print(
        f"\nharmonized {len(files)} subagent(s) x {len(blocks)} block(s): "
        f"{changed_files} file(s) updated, {in_sync}/{expected} already in sync"
    )
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
