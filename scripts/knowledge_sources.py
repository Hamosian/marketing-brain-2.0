"""Select and check the portable corpus used by the documentation actions."""
import json
from pathlib import Path
import re
import subprocess

from privacy_check import POLICY, findings

ROOT_FILES = {"README.md", "CLAUDE.md", "PHILOSOPHY.md", "THIRD_PARTY_NOTICES.md"}
PREFIXES = (".claude/skills/", ".claude/agents/", "references/", "systems/", "docs/", "scripts/")
SUFFIXES = {".md", ".py", ".sh"}


def load_fingerprints(root):
    values = json.loads((root / POLICY).read_text())["sha256"]
    if not values or any(not re.fullmatch(r"[a-f0-9]{64}", value) for value in values):
        raise ValueError("Invalid privacy policy")
    return set(values)


def collect_sources(root, fingerprints):
    """Read tracked regular files only; never follow even an in-repo symlink."""
    root = root.resolve()
    entries = subprocess.check_output(["git", "-C", str(root), "ls-files", "--stage", "-z"])
    sources = {}
    for entry in entries.decode().split("\0"):
        if not entry:
            continue
        metadata, name = entry.split("\t", 1)
        if name not in ROOT_FILES and not (name.startswith(PREFIXES) and Path(name).suffix in SUFFIXES):
            continue
        if "private runtime path" in findings(name, b"", set()) or "private skill runtime state" in findings(name, b"", set()):
            continue
        mode, _, stage = metadata.split()
        path = root / name
        if mode not in {"100644", "100755"} or stage != "0" or path.resolve() != path:
            raise ValueError(f"Unsupported source entry: {name}")
        content = path.read_bytes()
        issues = findings(name, content, fingerprints)
        if issues:
            raise ValueError(f"Source privacy check failed: {name}: {', '.join(issues)}")
        sources[name] = content.decode("utf-8")
    if not sources:
        raise ValueError("No eligible tracked source files")
    return dict(sorted(sources.items()))


def validate_outputs(directory, fingerprints):
    """Scan generated content before upload, without making it Git-trackable."""
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise ValueError("Generated output contains a symlink")
        if not path.is_file():
            continue
        name = path.relative_to(directory).as_posix()
        issues = findings("generated/" + name, path.read_bytes(), fingerprints)
        if issues:
            raise ValueError(f"Generated privacy check failed: {name}: {', '.join(issues)}")
