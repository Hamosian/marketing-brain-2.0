#!/usr/bin/env python3
"""Validate the YAML frontmatter of every skill and subagent, for real.

Replaces the inline bash frontmatter gate that `.github/workflows/team-context-lint.yml`
and `scripts/preflight.sh` each carried a copy of. That gate grepped for the presence of
`name:` and `description:` and measured the description with a one-line `awk` substitution,
so it could not tell a parseable description from an unparseable one -- and it silently
shipped one: `link-triage` carried an unquoted description containing `Human-in-the-loop: `,
which YAML reads as a nested mapping. The file failed `yaml.safe_load` on main while the
gate stayed green, and the skill ran with no description at all, so nothing could route to
it by description match. Two more descriptions were being silently truncated at a `#`.

`scripts/lint_agents.py` shares the blind spot by construction -- its `parse_frontmatter`
is documented as a "minimal top-level key: value parse" that "avoids a pyyaml dep" -- so
this script covers `.claude/agents/**` as well as `.claude/skills/*/SKILL.md`.

Why not just call pyyaml: no script in this repo imports it and the lint workflow installs
nothing (no `setup-python`, no pip step), so a pyyaml import would make the gate's behaviour
depend on whatever the runner image happens to ship. This is instead a parser for the YAML
*subset* the repo actually uses.

WHAT IT CHECKS
  1. Frontmatter is present, opens with `---`, and is terminated.
  2. Every value parses unambiguously, and decodes to the string YAML would produce.
  3. No duplicate top-level keys.
  4. Skills carry `name` and `description`; `name` matches the directory; the DECODED
     description is within the router's 1024-char cap. (The old awk measured the first
     physical line, so for a `>-` block scalar it measured the literal `>-` as 2 chars and
     the cap was never enforced on those files at all.)

STRICTER THAN YAML, ON PURPOSE
These are rejected even though pyyaml accepts them, because in each case YAML's reading is
not the author's. They are the gate's whole reason to exist, so they are not "false
positives" -- the error message explains the fix in each case:
  * a plain value containing ' #'  -- parses, then silently truncates at the comment
  * a duplicate top-level key      -- parses, silently keeping only the last value
  * anchors, aliases and tags (`&a`, `*a`, `!t`)     -- valid YAML this gate won't interpret
  * keep-chomping (`|+`, `>+`)                        -- ditto; subtle, and unused here
  * a more-indented line inside a folded (`>`) block  -- ditto; YAML keeps it literally

RESIDUAL, KNOWN AND BOUNDED
Nested blocks are validated at their shallowest level only; deeper levels are opaque. One
shape slips through: a comment line inside a nested block followed by a MORE-indented line
(`  - item` / `  #c` / `    deep`) is accepted although YAML rejects it. Differential
fuzzing against pyyaml over 560,000 generated frontmatters put this at 13 cases -- 0.0023%,
every one that shape -- with zero false positives and zero value drift. No file in this
repo has a comment inside a nested frontmatter block.

VERIFYING CHANGES TO THIS FILE
    python3 scripts/lint_skill_frontmatter.py             # lint the repo
    python3 scripts/lint_skill_frontmatter.py --selftest  # 37 regression cases
    python3 scripts/lint_skill_frontmatter.py --crosscheck  # diff every decoded value
                                                            # against pyyaml, where present
`--selftest` is the guard that matters: every case in its second half is a defect that
differential fuzzing against pyyaml actually found in this file, so the suite is a record of
the ways a hand-written YAML subset parser goes wrong. Run it after any edit here. The fuzz
harness itself is not committed -- it needs pyyaml, which CI does not have.

Exits 1 on any violation, emitting GitHub Actions `::error` annotations. Stdlib only.
Run from the repo root.
"""

import glob
import re
import sys
from pathlib import Path

SKILLS_GLOB = ".claude/skills/*/SKILL.md"
AGENTS_DIR = Path(".claude/agents")
# Mirrors NOT_AGENTS in scripts/agent_blocks.py: canonical sources and docs, not subagents.
NOT_AGENTS = {"README.md", "COMPANY_CONTEXT.md", "OUTPUT_CONTRACT.md"}

# 1024 matches the cap the previous gate enforced and Anthropic's Agent Skills convention.
# Measured on the DECODED value, so a folded or quoted description is measured as the router
# actually sees it -- the old `awk` read `>-` as the whole value and measured 2 chars.
DESC_CAP = 1024

KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_.-]*):(?:[ \t]+(.*))?[ \t]*$")
BLOCK_HEADERS = {"|", "|-", "|+", ">", ">-", ">+"}
# Openers that make a plain scalar something other than a string. `"`, `'`, `[`, `{` and
# the block headers are routed away before the plain-scalar path, so they are absent here.
# `-` and `?` are conditional (see _check_plain): `-5` and `-dash` are strings, `- x` is a
# sequence entry and `? x` a complex key, and both are errors in a value position.
#   verified against pyyaml 2026-09-02: `k: - dash` and `k: ? q` raise; `k: -dash` does not.
BAD_FIRST = set("*&!%@`,")

# Plain scalars YAML resolves to null. An unquoted `description: null` is NOT a
# four-character description -- the key is empty at runtime, the same data loss as a
# comment-only value -- so these decode to "" and trip the missing-key check in main().
# Quoted forms ("null") are ordinary strings and are unaffected, since they never reach
# the plain-scalar path.
#   verified against pyyaml: null / Null / NULL / ~ / empty resolve to None; nuLL, none,
#   None, nil do not.
YAML_NULLS = {"null", "Null", "NULL", "~", ""}

# `&anchor`, `!tag` and `*alias` are valid YAML that this gate declines to interpret rather
# than claims is broken, so its message says so instead of "YAML cannot parse this".
POLICY_ONLY = set("*&!")


class FrontmatterError(Exception):
    """A frontmatter structure this parser will not silently accept."""


class Incomplete(FrontmatterError):
    """A quoted scalar that is not closed *yet* -- the reader should consume another line.

    Distinct from FrontmatterError so that a genuinely malformed scalar (an unescaped
    interior quote, say) surfaces its own message instead of being mistaken for a
    continuation and eventually reported as "never closed".
    """


def _indent(line):
    """Number of leading spaces, or None for a blank line."""
    if not line.strip():
        return None
    return len(line) - len(line.lstrip(" "))


def _check_plain(value_lines, key):
    """Raise if any physical line of a plain scalar makes YAML read something else.

    These are the ways an unquoted value stops being the string its author meant. Each rule
    below was checked against pyyaml rather than assumed; see the probes in the commit that
    added them.
    """
    for raw in value_lines:
        if not raw:
            continue
        if "\t" in raw:
            raise FrontmatterError(
                f"'{key}:' is an unquoted value containing a tab. Quote it."
            )
        if ": " in raw:
            col = raw.index(": ")
            raise FrontmatterError(
                f"'{key}:' is an unquoted value containing ': ' (at {raw[max(0, col - 25):col + 2]!r}). "
                "YAML reads that as a nested mapping and the file fails to parse, which leaves the "
                'key empty at runtime. Wrap the value in double quotes (escaping any " as \\") '
                "or use a '>-' block scalar."
            )
        if raw.rstrip().endswith(":"):
            raise FrontmatterError(
                f"'{key}:' is an unquoted value ending in ':', which YAML reads as a nested "
                "mapping. Quote it or use a '>-' block scalar."
            )
        if " #" in raw:
            raise FrontmatterError(
                f"'{key}:' is an unquoted value containing ' #'. YAML truncates the value at the "
                "comment, silently dropping the rest -- it parses, so nothing warns you. Quote it "
                "or use a '>-' block scalar."
            )
    first = value_lines[0]
    if not first:
        return
    if first[0] in POLICY_ONLY:
        raise FrontmatterError(
            f"'{key}:' opens with {first[0]!r} (a YAML anchor, alias or tag). Valid YAML, but "
            "this gate does not interpret them in frontmatter -- quote the value instead."
        )
    if first[0] in BAD_FIRST:
        raise FrontmatterError(
            f"'{key}:' is an unquoted value starting with the YAML indicator {first[0]!r}. Quote it."
        )
    # `- x` is a sequence entry and `? x` a complex mapping key; both are errors in a value
    # position. `-dash` and `-5` are ordinary scalars, so only the space form is rejected.
    if first in ("-", "?") or first[:2] in ("- ", "? "):
        raise FrontmatterError(
            f"'{key}:' is an unquoted value starting with {first[0]!r} followed by a space, which "
            f"YAML reads as {'a sequence entry' if first[0] == '-' else 'a complex mapping key'} "
            "rather than a string. Quote it."
        )


def _read_double_quoted(lines, i, rest, key):
    """Consume a (possibly multi-line) double-quoted scalar. Return (decoded, next_i)."""
    buf = rest
    start = i
    while True:
        try:
            decoded = _unescape_double(buf, key)
            return decoded, i + 1
        except Incomplete:
            i += 1
            if i >= len(lines) or _indent(lines[i]) == 0:
                raise FrontmatterError(
                    f"'{key}:' opens a double-quoted value on line {start + 1} that is never closed."
                )
            buf += "\n" + lines[i].strip()


def _unescape_double(text, key):
    """Decode one complete `"..."` scalar, or raise if it is not complete."""
    if not text.startswith('"'):
        raise Incomplete("not a double-quoted scalar")
    out = []
    i = 1
    while i < len(text):
        c = text[i]
        if c == "\\":
            if i + 1 >= len(text):
                raise Incomplete("incomplete")
            nxt = text[i + 1]
            if nxt == "\n":  # line continuation inside a quoted scalar
                i += 2
                continue
            out.append({"n": "\n", "t": "\t", '"': '"', "\\": "\\", "/": "/"}.get(nxt, nxt))
            i += 2
            continue
        if c == '"':
            if text[i + 1:].strip():
                raise FrontmatterError(
                    f"'{key}:' has trailing text after the closing quote: "
                    f"{text[i + 1:].strip()[:40]!r}. An interior \" must be escaped as \\\"."
                )
            return "".join(out)
        if c == "\n":
            out.append(" ")  # quoted scalars fold newlines to a space
            i += 1
            while i < len(text) and text[i] == " ":
                i += 1
            continue
        out.append(c)
        i += 1
    raise Incomplete("incomplete")


def _read_single_quoted(lines, i, rest, key):
    """Consume a (possibly multi-line) single-quoted scalar. Return (decoded, next_i)."""
    buf = rest
    start = i
    while True:
        body = buf[1:]
        # A lone `'` closes; `''` is a literal apostrophe.
        j, out = 0, []
        while j < len(body):
            if body[j] == "'":
                if j + 1 < len(body) and body[j + 1] == "'":
                    out.append("'")
                    j += 2
                    continue
                if body[j + 1:].strip():
                    raise FrontmatterError(
                        f"'{key}:' has trailing text after the closing quote. "
                        "An interior ' must be doubled as ''."
                    )
                return "".join(out).replace("\n", " "), i + 1
            out.append(body[j])
            j += 1
        i += 1
        if i >= len(lines) or _indent(lines[i]) == 0:
            raise FrontmatterError(
                f"'{key}:' opens a single-quoted value on line {start + 1} that is never closed."
            )
        buf += "\n" + lines[i].strip()


def _read_block(lines, i, header, key, base_len):
    """Consume a `|`/`>` block scalar body. Return (decoded, next_i).

    Implements the chomping indicators exactly, because the decoded length is what the
    1024-char cap is measured against:
      `>`/`|`  (clip)  one trailing newline, but only if the body is followed by more
                       frontmatter -- at the very end there is no line break to keep
      `>-`/`|-`(strip) no trailing newline
      `>+`/`|+`(keep)  every trailing blank line
    Verified against pyyaml: `k: >` over `a`,`b` then a key yields `'a b\n'`, `>-` yields
    `'a b'`, `>+` yields `'a b\n\n'`, `|` yields `'a\nb\n'`.
    """
    body, i, base = [], i + 1, None
    while i < len(lines):
        ind = _indent(lines[i])
        if ind is None:
            body.append(None)  # blank line; significant to both folding and chomping
            i += 1
            continue
        if ind == 0:
            break
        # The FIRST non-blank line sets the block's indent; a shallower line ENDS the block
        # rather than dedenting it. Whether that line is then legal is the outer loop's
        # business -- a comment is fine, content is not.
        #   verified: `k: >-` over '    deep' then '  #c' parses; then '  content' raises.
        if base is None:
            base = ind
        elif ind < base:
            break
        body.append(lines[i])
        i += 1

    # Keep-chomping is genuinely subtle -- pyyaml gives `k: |+` over `a` the value 'a' at
    # end-of-input but '\n' for a blank-only body -- and no file in this repo uses it. The
    # gate refuses it rather than half-implementing it.
    if header.endswith("+"):
        raise FrontmatterError(
            f"'{key}:' uses keep-chomping ('{header}'). This gate does not validate it; "
            "use '|', '|-', '>' or '>-'."
        )

    # A block scalar with no body is the empty string, not an error (pyyaml: `k: >` -> '').
    if not any(l is not None for l in body):
        return "", i

    trailing_blanks = 0
    while body and body[-1] is None:
        body.pop()
        trailing_blanks += 1

    if header[0] == "|":
        # Literal: keep every line, preserving indentation relative to the block indent.
        text = "\n".join("" if l is None else l[base:] for l in body)
    else:
        # Folded: blank lines become newlines; a MORE-indented line is kept literally and
        # is not folded into its neighbours. That last rule is the one this gate declines to
        # reproduce, because getting it subtly wrong would mis-measure the cap in silence.
        if any(l is not None and (len(l) - len(l.lstrip(" "))) > base for l in body):
            raise FrontmatterError(
                f"'{key}:' is a folded ('{header}') block scalar containing a more-indented "
                "line. YAML keeps such lines literally rather than folding them; this gate "
                "does not reproduce that rule, so use a literal ('|') block or even indentation."
            )
        paras, cur = [], []
        for l in body:
            if l is None:
                paras.append(cur)
                cur = []
            else:
                cur.append(l.strip())
        paras.append(cur)
        text = "\n".join(" ".join(p) for p in paras)

    if header.endswith("-"):
        return text, i
    # Clip: exactly one trailing newline. Every content line inside a frontmatter block is
    # newline-terminated -- including the last one, whose break sits just before the closing
    # `---` -- so a non-empty clip body always retains one.
    #   verified: 'description: >\n  a b\n' -> 'a b\n'; the same document without the final
    #   newline gives 'a b', which is why the split below must keep it.
    return text + "\n", i


def _read_flow(lines, i, rest, key):
    """Consume a `[...]`/`{...}` flow collection as an opaque value. Return (marker, next_i)."""
    depth, buf, start = 0, rest, i
    while True:
        for c in buf:
            if c in "[{":
                depth += 1
            elif c in "]}":
                depth -= 1
        if depth == 0:
            return "<flow>", i + 1
        i += 1
        if i >= len(lines) or _indent(lines[i]) == 0:
            raise FrontmatterError(
                f"'{key}:' opens a flow collection on line {start + 1} that is never closed."
            )
        buf = lines[i]


def _skip_nested(lines, i, key, errors):
    """Consume an indented nested mapping/sequence, hazard-checking its `key: value` lines.

    The block's internal structure is deliberately opaque. An earlier version tried to
    require the shallowest level to be consistently a sequence or a mapping, but that rule
    is unsound: YAML allows a block sequence at the same indentation as the mapping key it
    belongs to, so `k:` over `  ends:` and `  - item` is valid and the rule rejected it.
    The residual is recorded in the module docstring.
    """
    i += 1
    # State for the block's SHALLOWEST level only; deeper levels stay opaque (see the
    # module docstring's "residual" note).
    top = None            # the shallowest indent in this block
    is_seq_block = None   # was the block's first entry a sequence entry?
    seq_open = False      # is a sequence currently open at `top`?
    valueless_key = False # was the last entry at `top` a `key:` with no inline value?
    deeper_since = False  # has a deeper-indented line appeared since that entry?
    bad = None
    while i < len(lines):
        ind = _indent(lines[i])
        if ind is None:
            i += 1
            continue
        if ind == 0:
            break
        raw = lines[i].lstrip(" ")
        if raw.startswith("#"):
            i += 1
            continue
        if top is not None and ind > top:
            # A deeper line is the value of the entry above it, so that entry is no longer
            # valueless -- which decides whether a later sequence entry at `top` is legal.
            #   verified: `k:` over '  ends:' / '    deep' / '  - item' raises in pyyaml.
            deeper_since = True
            i += 1
            continue
        m = KEY_RE.match(raw.lstrip("- "))
        if top is None:
            top = ind
        if ind == top:
            entry_is_seq = raw.startswith("- ") or raw == "-"
            if is_seq_block is None:
                is_seq_block = entry_is_seq
                seq_open = entry_is_seq
            elif entry_is_seq:
                # Legal as a continuation of an open sequence, or as the value of the
                # valueless key immediately above (which nothing deeper has claimed).
                #   verified: `k:` over '  ends:' then '  - item' parses;
                #             `k:` over '  version: 1.0' then '  - s' raises.
                if not (is_seq_block or seq_open or (valueless_key and not deeper_since)):
                    bad = bad or "a sequence entry after a key that already has a value"
                seq_open = True
            elif not m:
                # Inside a nested mapping every entry is a key line or a sequence entry.
                bad = bad or "a bare scalar line where a mapping key was expected"
            elif is_seq_block:
                #   verified: `k:` over '  - s' then '  version: 1.0' raises.
                bad = bad or "a mapping key after a sequence entry at the same level"
            else:
                seq_open = False
            valueless_key = bool(m) and not m.group(2) and not entry_is_seq
            deeper_since = False
        if m and m.group(2):
            try:
                _check_plain([m.group(2)], f"{key}.{m.group(1)}")
            except FrontmatterError as e:
                errors.append(str(e))
        i += 1
    if bad:
        raise FrontmatterError(
            f"'{key}:' opens a nested block containing {bad}, which YAML rejects."
        )
    return "<nested>", i


def _read_plain(lines, i, rest, key):
    """Consume a plain (unquoted) scalar, folding its indented continuation lines.

    A blank line inside one folds to a newline, and a comment line ENDS the scalar -- both
    verified against pyyaml (`k: a` over `  #c` yields just 'a').
    """
    chunk, j, pending = [rest], i + 1, 0
    while j < len(lines):
        ind = _indent(lines[j])
        if ind is None:
            pending += 1
            j += 1
            continue
        if ind == 0 or lines[j].lstrip().startswith("#"):
            break
        chunk.extend([None] * pending)
        pending = 0
        chunk.append(lines[j].strip())
        j += 1
    _check_plain([c for c in chunk if c is not None], key)
    folded, para = [], []
    for c in chunk:
        if c is None:
            folded.append(" ".join(para))
            para = []
        else:
            para.append(c)
    folded.append(" ".join(para))
    value = "\n".join(folded)
    return ("" if value in YAML_NULLS else value), j


def parse_frontmatter(text):
    """Strictly parse the frontmatter block. Return (mapping, errors).

    `mapping` holds decoded top-level scalars (nested blocks appear as the marker
    `"<nested>"`). `errors` lists every problem found; a non-empty list means the file
    must not ship, and an empty list means real YAML will read the mapping as intended.
    """
    errors = []
    if not text.startswith("---\n"):
        return {}, ["Missing YAML frontmatter (the file must start with ---)"]
    parts = text[4:].split("\n---", 1)
    if len(parts) < 2:
        return {}, ["Frontmatter is never terminated (no closing --- line)"]

    lines = parts[0].split("\n")
    # `seen` tracks every key encountered, including ones whose value failed to parse, so a
    # duplicate is still reported when the first occurrence errored.
    out, seen, i = {}, set(), 0
    while i < len(lines):
        line = lines[i]
        ind = _indent(line)
        if ind is None or line.lstrip().startswith("#"):
            i += 1
            continue
        if ind > 0:
            errors.append(
                f"Unexpected indented line {i + 1} at the top level: {line.strip()[:60]!r}"
            )
            i += 1
            continue
        m = KEY_RE.match(line)
        if not m:
            errors.append(
                f"Line {i + 1} is not a 'key: value' line and this gate will not guess at it: "
                f"{line.strip()[:60]!r}"
            )
            i += 1
            continue

        key, rest = m.group(1), (m.group(2) or "").strip()
        if key in seen:
            errors.append(
                f"Duplicate top-level key '{key}:' -- YAML keeps the last one and silently "
                "drops the earlier value."
            )
        try:
            if rest == "" or rest.startswith("#"):
                # `key:` with nothing after it, or nothing but a COMMENT -- YAML discards
                # the comment, so `description: #routing text` is a null description, not a
                # 14-character one. Routing it here rather than rejecting it outright
                # reproduces YAML exactly: the peek below skips comment lines, so
                # `k: #c` over `  hello` is 'hello' while `k: #c` alone is empty (and the
                # empty description is then reported by the missing-key check in main()).
                #   verified: `description: #c` -> None; over `  hello there` -> 'hello there'. What follows decides the shape: a nested
                # mapping/sequence, or an INDENTED SCALAR, which YAML folds into the value
                # (`k:` over `  hello` is {'k': 'hello'}, not a nested block). Treating the
                # scalar case as opaque was hiding malformed ones from the gate.
                j = i + 1
                while j < len(lines) and (
                    _indent(lines[j]) is None or lines[j].lstrip().startswith("#")
                ):
                    j += 1
                if j >= len(lines) or _indent(lines[j]) == 0:
                    value, i = "", i + 1
                else:
                    head = lines[j].lstrip(" ")
                    if head.startswith("- ") or head == "-" or KEY_RE.match(head):
                        value, i = _skip_nested(lines, i, key, errors)
                    elif head.startswith('"'):
                        value, i = _read_double_quoted(lines, j, head, key)
                    elif head.startswith("'"):
                        value, i = _read_single_quoted(lines, j, head, key)
                    else:
                        value, i = _read_plain(lines, j, head, key)
            elif rest in BLOCK_HEADERS:
                value, i = _read_block(lines, i, rest, key, 0)
            elif rest.startswith('"'):
                value, i = _read_double_quoted(lines, i, rest, key)
            elif rest.startswith("'"):
                value, i = _read_single_quoted(lines, i, rest, key)
            elif rest[0] in "[{":
                # A flow collection is valid YAML and is a list/mapping, not a string. The
                # gate keeps it opaque; a key that must be a string (`description`) then
                # fails the string check in main() rather than being mis-measured here.
                value, i = _read_flow(lines, i, rest, key)
            else:
                value, i = _read_plain(lines, i, rest, key)
        except FrontmatterError as e:
            errors.append(str(e))
            seen.add(key)
            i += 1
            continue
        out[key] = value
        seen.add(key)
    return out, errors


def _targets():
    """Every skill and subagent file this gate covers."""
    files = [Path(p) for p in sorted(glob.glob(SKILLS_GLOB))]
    if AGENTS_DIR.is_dir():
        files += sorted(
            p for p in AGENTS_DIR.rglob("*.md") if p.name not in NOT_AGENTS
        )
    return files


def selftest():
    """Regression suite: every rule below was verified against pyyaml, and every case in the
    second half is a defect a differential fuzz against pyyaml actually found in this file.

    Cases are (label, frontmatter, expectation), where expectation is either `False` (the
    gate must reject) or a dict of decoded values the gate must produce exactly. Decoded
    values matter as much as the verdict, because the 1024-char cap is measured on them.
    """
    OK = {}
    cases = [
        # ---- the bugs this gate was written for ----
        ("the link-triage bug: unquoted ': '",
         '---\nname: x\ndescription: Reads links. Human-in-the-loop: nothing writes.\n---\n', False),
        ("the fix: double-quoted with escaped quotes",
         '---\nname: x\ndescription: "A. Human-in-the-loop: b. Say \\"hi\\"."\n---\n',
         {"description": 'A. Human-in-the-loop: b. Say "hi".'}),
        ("the other fix: folded block scalar",
         '---\nname: x\ndescription: >-\n  Reads links. Human-in-the-loop: nothing\n  writes.\n---\n',
         {"description": "Reads links. Human-in-the-loop: nothing writes."}),
        ("the webflow bug: ' #' truncates silently",
         '---\nname: x\ndescription: See #website-accessibility work\n---\n', False),
        ("unquoted trailing colon",
         '---\nname: x\ndescription: Trigger on:\n---\n', False),
        ("bare colon and a URL are fine",
         '---\nname: x\ndescription: Ratio 3:1 and http://a.b work\n---\n',
         {"description": "Ratio 3:1 and http://a.b work"}),
        ("duplicate key",
         '---\nname: x\ndescription: a\ndescription: b\n---\n', False),
        ("duplicate key even when the first one errored",
         '---\nname: x\ndescription: bad: v\ndescription: b\n---\n', False),
        ("unterminated quote",
         '---\nname: x\ndescription: "oops\n---\n', False),
        ("no frontmatter", '# just a heading\n', False),

        # ---- defects found by differential fuzzing against pyyaml ----
        ("flow sequence is valid YAML, not an error",
         '---\nname: x\ndescription: d\ntools: [Read, Write]\n---\n', OK),
        ("flow mapping is valid YAML, not an error",
         '---\nname: x\ndescription: d\nmeta: {a: 1}\n---\n', OK),
        ("'- x' in a value position is a sequence entry, so rejected",
         '---\nname: x\ndescription: - dash\n---\n', False),
        ("'-dash' and '-5' are ordinary scalars",
         '---\nname: x\ndescription: -dash\n---\n', {"description": "-dash"}),
        ("'?q' is an ordinary scalar; '? q' is a complex key",
         '---\nname: x\ndescription: ?q\n---\n', {"description": "?q"}),
        ("'? q' rejected", '---\nname: x\ndescription: ? q\n---\n', False),
        # An empty block body decodes to '' rather than raising; the empty description is
        # then reported by main()'s missing-key check, not by the parser.
        ("an empty block scalar body is '', not an error",
         '---\nname: x\ndescription: >\nmeta: 1\n---\n', {"description": ""}),
        ("keep-chomping is refused rather than half-implemented",
         '---\nname: x\ndescription: |+\n  a\n---\n', False),
        ("clip adds one newline when a line follows the body",
         '---\nname: x\ndescription: |\n  a\n  b\nmeta: 1\n---\n',
         {"description": "a\nb\n"}),
        ("clip retains its newline even as the final entry",
         '---\nname: x\ndescription: >\n  a\n  b\n---\n', {"description": "a b\n"}),
        ("strip never adds a newline",
         '---\nname: x\ndescription: >-\n  a\n  b\nmeta: 1\n---\n', {"description": "a b"}),
        ("a blank line in a folded block is a newline, not a space",
         '---\nname: x\ndescription: >-\n  a\n\n  b\n---\n', {"description": "a\nb"}),
        ("a more-indented line in a folded block is refused",
         '---\nname: x\ndescription: >-\n  a\n    deep\n  b\n---\n', False),
        ("a block scalar's FIRST line sets the indent",
         '---\nname: x\ndescription: |-\n    deep\n  shallow\n---\n', False),
        ("a shallower COMMENT ends the block instead of breaking it",
         '---\nname: x\ndescription: >-\n    deep\n  #c\nmeta: 1\n---\n',
         {"description": "deep"}),
        ("a comment line ends a plain scalar",
         '---\nname: x\ndescription: a\n  #c\n---\n', {"description": "a"}),
        ("a blank line folds a plain scalar to a newline",
         '---\nname: x\ndescription: a\n\n  b\n---\n', {"description": "a\nb"}),
        # Decodes to '' exactly as YAML yields null; main()'s missing-key check is what
        # rejects the file, which is why the expectation here is a value, not False.
        ("an unquoted 'null' is null, not the text 'null'",
         '---\nname: x\ndescription: null\n---\n', {"description": ""}),
        ("'~' is null too",
         '---\nname: x\ndescription: ~\n---\n', {"description": ""}),
        ("a QUOTED \"null\" is an ordinary string",
         '---\nname: x\ndescription: "null"\n---\n', {"description": "null"}),
        ("'nuLL' is not a null token",
         '---\nname: x\ndescription: nuLL\n---\n', {"description": "nuLL"}),
        ("a comment-only value is null, not the comment text",
         '---\nname: x\ndescription: #routing text\n---\n', {"description": ""}),
        ("a comment before an indented scalar is discarded, not prepended",
         '---\nname: x\ndescription: #c\n  hello there\n---\n',
         {"description": "hello there"}),
        ("'key:' over an indented scalar is a scalar, not a nested block",
         '---\nname: x\ndescription:\n  hello there\n---\n', {"description": "hello there"}),
        ("nested mapping is allowed",
         '---\nname: x\ndescription: d\nmetadata:\n  version: 1.1.0\n---\n', OK),
        ("a hazard inside a nested mapping is still caught",
         '---\nname: x\ndescription: d\nmetadata:\n  note: a: b\n---\n', False),
        ("a sequence at a VALUELESS key's indent is legal",
         '---\nname: x\ndescription: d\nmetadata:\n  ends:\n  - item\n  - item\n---\n', OK),
        ("a sequence after a key that HAS a value is not",
         '---\nname: x\ndescription: d\nmetadata:\n  version: 1.0\n  - s\n---\n', False),
        ("a mapping key after a sequence entry is not",
         '---\nname: x\ndescription: d\nmetadata:\n  - s\n  version: 1.0\n---\n', False),
        ("a bare scalar where a mapping key belongs is not",
         '---\nname: x\ndescription: d\nmetadata:\n  version: 1.0\n  bare text\n---\n', False),
        ("a deeper value means a later sequence entry is illegal",
         '---\nname: x\ndescription: d\nmetadata:\n  ends:\n    deep\n  - item\n---\n', False),
        ("two-level nested sequences of mappings are fine",
         '---\nname: x\ndescription: d\nservices:\n  - name: A\n    url: https://a.b\n'
         '  - name: B\n    url: https://b.c\n---\n', OK),
        ("name must match its directory (checked in main, not here)",
         '---\nname: x\ndescription: d\n---\n', OK),
    ]
    bad = 0
    for label, text, expect in cases:
        fm, errs = parse_frontmatter(text)
        if expect is False:
            if errs:
                print(f"  ok   {label}")
            else:
                print(f"  FAIL {label}: expected rejection, got {fm!r}")
                bad += 1
            continue
        if errs:
            print(f"  FAIL {label}: expected acceptance, got {errs[0][:80]}")
            bad += 1
            continue
        wrong = {k: (fm.get(k), v) for k, v in expect.items() if fm.get(k) != v}
        if wrong:
            print(f"  FAIL {label}: decoded {wrong!r}")
            bad += 1
        else:
            print(f"  ok   {label}")
    print(f"\nselftest: {len(cases)} case(s), {bad} failure(s)")
    return 1 if bad else 0


def crosscheck():
    """Diff this parser against pyyaml over every target. Local use; CI has no pyyaml."""
    try:
        import yaml
    except ImportError:
        print("crosscheck: pyyaml not installed here; skipping", file=sys.stderr)
        return 0
    # Deliberately NOT the split parse_frontmatter uses: requiring `---` alone on its line
    # means a shared bug in the split cannot make both sides agree and hide itself.
    split = re.compile(r"\A---[ \t]*\n(.*?\n)---[ \t]*(?:\n|\Z)", re.S)
    bad = 0
    for path in _targets():
        text = path.read_text(encoding="utf-8")
        mine, errs = parse_frontmatter(text)
        m = split.match(text)
        try:
            theirs = yaml.safe_load(m.group(1)) if m else None
            yaml_ok = isinstance(theirs, dict)
        except Exception:
            theirs, yaml_ok = None, False
        if bool(errs) == (not yaml_ok):
            pass  # verdicts agree
        else:
            print(f"::error file={path}::verdict disagreement "
                  f"(this parser ok={not errs}, pyyaml ok={yaml_ok}): {errs[:1]}")
            bad += 1
            continue
        if yaml_ok:
            for k, v in mine.items():
                if v in ("<nested>", "<flow>"):
                    continue
                other = theirs.get(k)
                if other is None:
                    # Do NOT skip this case. A key that pyyaml reads as null while this
                    # parser reports text is the `description: #comment` bug, and an
                    # isinstance(str) guard here would step straight over it.
                    if v:
                        print(f"::error file={path}::'{k}' is null in YAML but this parser "
                              f"decoded {v[:60]!r}")
                        bad += 1
                    continue
                if not isinstance(other, str):
                    continue
                if other != v:
                    print(f"::error file={path}::decoded '{k}' differs from pyyaml\n"
                          f"  mine  : {v[:90]!r}\n  pyyaml: {other[:90]!r}")
                    bad += 1
    print(f"\ncrosscheck: {len(_targets())} file(s), {bad} disagreement(s)")
    return 1 if bad else 0


def main(argv):
    """Lint every skill and subagent. Returns a process exit code."""
    if "--selftest" in argv:
        return selftest()

    errors = []

    def err(path, msg):
        errors.append(f"::error file={path}::{msg}")

    files = _targets()
    if not files:
        print("error: no skills found (run from the repo root)", file=sys.stderr)
        return 2

    for path in files:
        rel = path.as_posix()
        fm, problems = parse_frontmatter(path.read_text(encoding="utf-8"))
        for p in problems:
            err(rel, p)
        if problems:
            continue

        is_skill = rel.startswith(".claude/skills/")
        for key in ("name", "description"):
            if not fm.get(key):
                err(rel, f"Missing '{key}:' in frontmatter")

        if is_skill and fm.get("name"):
            expected = path.parent.name
            if fm["name"] != expected:
                err(rel, f"name: is '{fm['name']}' but the directory is '{expected}'; "
                         "routing resolves by directory, so they must match.")

        desc = fm.get("description") or ""
        if desc in ("<nested>", "<flow>"):
            err(rel, "description: must be a string, not a "
                     f"{'nested block' if desc == '<nested>' else 'flow collection'}. "
                     "The router reads it as text.")
        elif len(desc) > DESC_CAP:
            err(rel, f"description is {len(desc)} chars (max {DESC_CAP}) - trim it; "
                     "the router only reads the description.")

    for line in errors:
        print(line)
    print(f"\nlint_skill_frontmatter: {len(files)} file(s) checked, {len(errors)} problem(s)")

    if "--crosscheck" in argv:
        return crosscheck() or (1 if errors else 0)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
