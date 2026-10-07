#!/usr/bin/env python3
"""
Validate a skill or subagent before you open a PR.

Mirrors the repo CI lint (.github/workflows/team-context-lint.yml) AND the
Agent Skills framework frontmatter rules, so failures show up here instead of
on the PR. stdlib only, no dependencies.

Usage:
    python3 validate_skill.py <path>

    <path> may be:
      - a skill directory            (.claude/skills/agent-builder)
      - a SKILL.md file              (.claude/skills/agent-builder/SKILL.md)
      - a subagent markdown file     (.claude/agents/marketing/foo.md)
      - omitted -> current directory

Exit code 0 = all hard checks pass. Non-zero = at least one FAIL.
Lines prefixed WARN are advisory (progressive-disclosure / quality hints) and
never fail the build.
"""

import os
import re
import sys

RESERVED = ("anthropic", "claude")
NAME_RE = re.compile(r"^[a-z0-9-]+$")
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")
XML_TAG_RE = re.compile(r"<[^>]+>")
BINARY_GLOBS = (".zip", ".plugin", ".tar.gz", ".jar")
# A frontmatter value that is only a YAML block-scalar header -- "|", ">", with
# any chomping/indentation modifier ("|-", "|+", "|2", ">8") and an optional
# trailing comment ("| # note") -- has its real value on the indented lines
# that follow. parse_frontmatter reads that body: folded (">") joins lines with
# spaces, literal ("|") keeps line breaks. A header with no indented body
# resolves to "" so the required-field checks still fire. The CI lint
# (team-context-lint.yml) greps only for "^description:", so block-scalar
# frontmatter passes CI; this parser must accept it too or it false-FAILs
# skills the CI accepts (e.g. webflow-locale-publish-queue).
BLOCK_SCALAR_RE = re.compile(r"^([|>])[0-9+-]*(\s+#.*)?$")

fails = 0
warns = 0


def fail(msg):
    global fails
    fails += 1
    print(f"FAIL  {msg}")


def warn(msg):
    global warns
    warns += 1
    print(f"WARN  {msg}")


def ok(msg):
    print(f"PASS  {msg}")


def resolve_target(path):
    """Return (frontmatter_file, skill_dir_or_none)."""
    if os.path.isdir(path):
        skill_md = os.path.join(path, "SKILL.md")
        if os.path.isfile(skill_md):
            return skill_md, path
        fail(f"{path} is a directory but has no SKILL.md")
        return None, path
    if os.path.isfile(path):
        # a bare .md (SKILL.md or a subagent persona file)
        parent = os.path.dirname(path)
        return path, (parent if os.path.basename(path) == "SKILL.md" else None)
    fail(f"path not found: {path}")
    return None, None


def parse_frontmatter(md_file):
    """Return (frontmatter_dict, all_lines, has_fence).

    has_fence is True when the file opens with a '---' fence. It stays True even
    for an empty fence ('---' immediately followed by '---') so the caller still
    runs the required-field checks instead of silently passing.
    """
    with open(md_file, "r", encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    has_fence = bool(lines) and lines[0].strip() == "---"
    if not has_fence:
        fail(f"{md_file}: must start with '---' (YAML frontmatter). CI lint requires this.")
        return {}, lines, False

    fm = {}
    closed = False
    i = 1
    while i < len(lines):
        if lines[i].strip() == "---":
            closed = True
            break
        m = re.match(r"^([A-Za-z_][\w-]*):\s?(.*)$", lines[i])
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        header = BLOCK_SCALAR_RE.match(val)
        if header:
            # Block scalar: the value is the indented lines that follow, up to
            # the closing fence or the next non-indented line (the next key).
            block = []
            j = i + 1
            while j < len(lines):
                line = lines[j]
                if line.strip() == "---":
                    break
                if not line.strip():
                    block.append("")
                    j += 1
                    continue
                if not line[0] in (" ", "\t"):
                    break
                block.append(line.strip())
                j += 1
            while block and not block[-1]:
                block.pop()
            if header.group(1) == ">":
                # Folded: line breaks become spaces, blank lines become newlines.
                paras, cur = [], []
                for b in block:
                    if b:
                        cur.append(b)
                    else:
                        paras.append(" ".join(cur))
                        cur = []
                if cur:
                    paras.append(" ".join(cur))
                val = "\n".join(paras)
            else:
                # Literal: line breaks are preserved.
                val = "\n".join(block)
            fm[key] = val
            i = j
            continue
        fm[key] = val
        i += 1
    if not closed:
        fail(f"{md_file}: frontmatter opened with '---' but never closed.")
    return fm, lines, has_fence


def check_name(fm, md_file):
    name = fm.get("name", "")
    if not name:
        fail(f"{md_file}: missing 'name:' in frontmatter (CI lint requires it).")
        return
    before = fails
    if len(name) > 64:
        fail(f"name '{name}' exceeds 64 characters ({len(name)}).")
    if not NAME_RE.match(name):
        fail(f"name '{name}' must contain only lowercase letters, numbers, and hyphens.")
    low = name.lower()
    for word in RESERVED:
        if word in low:
            fail(f"name '{name}' contains reserved word '{word}'.")
    if XML_TAG_RE.search(name):
        fail(f"name '{name}' contains an XML-like tag.")
    if fails == before:
        ok(f"name '{name}'")


def check_description(fm, md_file):
    desc = fm.get("description", "")
    if not desc:
        fail(f"{md_file}: missing or empty 'description:' (CI lint requires it).")
        return
    if len(desc) > 1024:
        fail(f"description exceeds 1024 characters ({len(desc)}). Trim it.")
    if XML_TAG_RE.search(desc):
        fail("description contains an XML-like tag (< >). Remove it.")
    # Quality heuristic: a good description says WHAT and WHEN (trigger).
    low = desc.lower()
    if not any(k in low for k in ("use ", "trigger", "when ", "whenever")):
        warn("description should say WHEN to use the skill (e.g. 'Use when...', "
             "trigger phrases). That text is what Claude matches requests against.")
    ok(f"description ({len(desc)} chars)")


def check_placeholders(skill_dir, md_file):
    # Scan the same file set as the CI lint (team-context-lint.yml): *.md and
    # *.json only. Matching that include set keeps this a faithful mirror -- a
    # local PASS predicts a CI PASS. (Widening to .py/.sh would diverge from CI
    # and would also match this validator's own regex literal and log strings,
    # producing false positives on itself.)
    targets = []
    if skill_dir:
        for root, _dirs, files in os.walk(skill_dir):
            for f in files:
                if f.endswith((".md", ".json")):
                    targets.append(os.path.join(root, f))
    else:
        targets = [md_file]
    hits = []
    for t in targets:
        with open(t, "r", encoding="utf-8", errors="ignore") as fh:
            for n, line in enumerate(fh, 1):
                if PLACEHOLDER_RE.search(line):
                    hits.append(f"{t}:{n}: {line.strip()[:80]}")
    if hits:
        for h in hits:
            fail(f"unfilled {{{{PLACEHOLDER}}}}: {h}")
    else:
        ok("no unfilled {{PLACEHOLDER}} markers")


def check_binaries(skill_dir):
    if not skill_dir:
        return
    bad = []
    for root, _dirs, files in os.walk(skill_dir):
        for f in files:
            if any(f.endswith(g) for g in BINARY_GLOBS):
                bad.append(os.path.join(root, f))
    if bad:
        for b in bad:
            fail(f"binary/packaged file in skill ({b}) - use pointers, not copies.")
    else:
        ok("no binary/packaged files bundled")


def check_progressive_disclosure(lines, md_file):
    # Framework guideline: SKILL.md body should stay under ~5k tokens.
    # Rough proxy: ~1 token ~= 0.75 words, so ~5k tokens ~= ~3800 words.
    body = "\n".join(lines)
    words = len(body.split())
    if words > 3800:
        warn(f"{md_file} body is ~{words} words (>~5k tokens). Move heavy reference "
             f"content into knowledge/ files and link to them (progressive disclosure).")
    else:
        ok(f"body size ~{words} words (within progressive-disclosure budget)")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    md_file, skill_dir = resolve_target(path)
    if not md_file:
        print("\nRESULT: FAIL")
        sys.exit(1)

    print(f"Validating: {md_file}")
    if skill_dir:
        print(f"Skill dir:  {skill_dir}")
    print("-" * 60)

    fm, lines, has_fence = parse_frontmatter(md_file)
    if has_fence:
        # Run the required-field checks whenever a fence exists, even if it is
        # empty -- an empty fence must FAIL (missing name/description), not pass.
        check_name(fm, md_file)
        check_description(fm, md_file)
    check_placeholders(skill_dir, md_file)
    check_binaries(skill_dir)
    check_progressive_disclosure(lines, md_file)

    print("-" * 60)
    if fails:
        print(f"RESULT: FAIL ({fails} error(s), {warns} warning(s))")
        sys.exit(1)
    print(f"RESULT: PASS ({warns} warning(s))")
    sys.exit(0)


if __name__ == "__main__":
    main()
