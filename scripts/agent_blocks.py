#!/usr/bin/env python3
"""Single source of truth for the specialist-subagent managed blocks.

`scripts/harmonize_agents.py` writes these blocks into every subagent and
`scripts/lint_agents.py` asserts they are present. Both used to hard-code the marker
strings and rely on a "keep in step with..." comment to stay aligned, which is the exact
drift this directory's tooling exists to prevent: rename a marker in one script and the
other silently accepts a block its counterpart rejects. Import from here instead.

Convention for a canonical source file: the delimited region **opens** with the in-agent
`start` marker and omits `end`, which the harmonizer writes itself.

Paths here are relative to the repo root, so both scripts must be run from there.
"""

from pathlib import Path
from typing import NamedTuple

AGENTS_DIR = Path(".claude/agents")

# Files under AGENTS_DIR that are canonical sources or docs, never subagents.
NOT_AGENTS = {"README.md", "RIVERSIDE_CONTEXT.md", "OUTPUT_CONTRACT.md"}


class ManagedBlock(NamedTuple):
    """One harmonized block: where its canonical text lives and how it is delimited."""

    label: str
    canonical: Path
    canonical_markers: tuple
    start: str
    end: str

    @property
    def markers(self):
        """The (start, end) pair delimiting this block inside a subagent."""
        return (self.start, self.end)


BLOCKS = [
    ManagedBlock(
        label="riverside context",
        canonical=AGENTS_DIR / "RIVERSIDE_CONTEXT.md",
        canonical_markers=("<!-- embedded-block:start -->", "<!-- embedded-block:end -->"),
        start="<!-- riverside-harmonized -->",
        end="<!-- /riverside-harmonized -->",
    ),
    ManagedBlock(
        label="output contract",
        canonical=AGENTS_DIR / "OUTPUT_CONTRACT.md",
        canonical_markers=("<!-- output-contract:start -->", "<!-- output-contract:end -->"),
        start="<!-- output-contract -->",
        end="<!-- /output-contract -->",
    ),
]


def agent_files(exempt=frozenset()):
    """Every subagent file under AGENTS_DIR, excluding canonical sources and `exempt`.

    `exempt` holds AGENTS_DIR-relative posix paths.
    """
    return sorted(
        p
        for p in AGENTS_DIR.rglob("*.md")
        if p.name not in NOT_AGENTS
        and p.relative_to(AGENTS_DIR).as_posix() not in exempt
    )
