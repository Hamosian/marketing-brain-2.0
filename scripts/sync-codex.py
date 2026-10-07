#!/usr/bin/env python3
"""Generate Codex context from the canonical source; --check never writes files."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
HEADER = "<!-- GENERATED from CLAUDE.md by scripts/sync-codex.py. -->\n\n"


def runtime_path(relative, kind):
    parts = relative.parts
    return kind == "skills" and len(parts) > 1 and (
        parts[1] in {"data", "drafts"}
        or relative.name.startswith("tracking")
        or relative.name == "dashboard.html"
    )


def expected_files(root):
    text = (root / "CLAUDE.md").read_text()
    for old, new in (("CLAUDE.md", "AGENTS.md"), (".claude/skills", ".agents/skills"), (".claude/agents", ".agents/agents")):
        text = text.replace(old, new)
    expected = {Path("AGENTS.md"): (HEADER + text).encode()}
    for kind in ("skills", "agents"):
        source = root / ".claude" / kind
        if not source.is_dir():
            raise ValueError(f"missing canonical {kind} directory")
        for path in source.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            relative = path.relative_to(source)
            if not runtime_path(relative, kind):
                expected[Path(".agents") / kind / relative] = path.read_bytes()
    return expected


def synchronize(root=ROOT, check=False):
    expected = expected_files(root)
    actual = {Path("AGENTS.md")} if (root / "AGENTS.md").is_file() else set()
    for kind in ("skills", "agents"):
        directory = root / ".agents" / kind
        for path in directory.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and not runtime_path(path.relative_to(directory), kind):
                actual.add(path.relative_to(root))
    changed = [path for path, content in expected.items() if not (root / path).is_file() or (root / path).read_bytes() != content]
    removed = actual - expected.keys()
    if not check:
        for path in removed:
            (root / path).unlink()
        for path in changed:
            destination = root / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(expected[path])
    return sorted(set(changed) | removed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        changes = synchronize(check=args.check)
    except (OSError, ValueError) as error:
        print(f"Codex sync failed: {error}", file=sys.stderr)
        return 2
    if args.check and changes:
        print("Codex mirror drift. Run python3 scripts/sync-codex.py")
        for path in changes:
            print(path)
        return 1
    print(f"Codex mirror {'checked' if args.check else 'updated'}: {len(changes)} changed paths.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
