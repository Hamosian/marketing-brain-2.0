#!/usr/bin/env bash
# Run every gate CI runs on a pull request, locally, before you open one.
#
# Mirrors .github/workflows/team-context-lint.yml (9 gates) and
# .github/workflows/codex-sync-check.yml (1 gate). Keep it in step with those
# files - if you add a CI step, add it here in the same commit, or the local
# gate silently stops matching CI and someone eats a red PR for a mechanical
# reason.
#
# Usage:  bash scripts/preflight.sh [base-ref]      # base-ref defaults to main
# Exit 0 = nothing to fix. Runs all gates even after one fails, so you see
# every problem in one pass instead of fixing them one red run at a time.
#
# Three outcomes per gate: PASS, FAIL (fix it), and PEND - green once you commit
# and nothing to fix now. Only gate 8 can PEND; see its comment below. PEND does
# not set a non-zero exit, so branch on the exit code, not on grepping for PASS.

set -uo pipefail
BASE="${1:-main}"
FAILED=()
PENDING=()
PASSED=0

hdr()  { printf '\n\033[1m%s\033[0m\n' "$1"; }
ok()   { PASSED=$((PASSED+1)); printf '  \033[32mPASS\033[0m  %s\n' "$1"; }
bad()  { FAILED+=("$1");       printf '  \033[31mFAIL\033[0m  %s\n' "$1"; }
# PEND = not green yet, but nothing is wrong: a state that only a commit clears.
# Kept out of FAILED so a pre-commit run is not red for a mechanical reason.
pend() { PENDING+=("$1");      printf '  \033[33mPEND\033[0m  %s\n' "$1"; }

hdr "Team Context Lint"

# 1. Skills and subagents must have frontmatter that actually PARSES. Grepping
#    for `description:` is not enough - an unquoted value containing ": " or
#    " #" greps fine and then either fails to parse or silently truncates.
if python3 scripts/lint_skill_frontmatter.py >/dev/null; then
  ok "skill/subagent frontmatter parses, descriptions within 1024 chars"
else
  python3 scripts/lint_skill_frontmatter.py | sed 's/^/    /'
  bad "lint_skill_frontmatter"
fi

# 2. Referenced files must exist on this branch
if git rev-parse --verify --quiet "origin/$BASE" >/dev/null; then
  if python3 scripts/lint_references.py --changed-only "origin/$BASE"; then
    ok "referenced files resolve (vs origin/$BASE)"
  else
    bad "lint_references"
  fi
else
  bad "lint_references (no origin/$BASE - run: git fetch origin $BASE)"
fi

# 3. Subagents scoped, pinned, registered
if python3 scripts/lint_agents.py >/dev/null; then ok "lint_agents"; else
  python3 scripts/lint_agents.py; bad "lint_agents"; fi

# 4. Embedded context + output-contract blocks in sync
if python3 scripts/harmonize_agents.py --check >/dev/null; then ok "harmonize_agents --check"; else
  python3 scripts/harmonize_agents.py --check; bad "harmonize_agents --check"; fi

# 5. Routing eval suite resolves (structural failures only; overlap is a warning)
if python3 scripts/eval_routing.py --coverage >/dev/null; then ok "eval_routing --coverage"; else
  python3 scripts/eval_routing.py --coverage; bad "eval_routing --coverage"; fi

# 5b. Output-lift suite resolves, and its harness still fails loudly on a broken
#     suite. Structural only - measuring actual lift costs model calls and is a
#     deliberate local/manual step, never a PR gate.
if python3 scripts/eval_output_lift.py >/dev/null; then ok "eval_output_lift (structural)"; else
  python3 scripts/eval_output_lift.py; bad "eval_output_lift"; fi

if python3 scripts/test_eval_output_lift.py >/dev/null; then ok "test_eval_output_lift"; else
  python3 scripts/test_eval_output_lift.py; bad "test_eval_output_lift"; fi

# 6. No unfilled {{PLACEHOLDER}} - note the DOUBLE braces; single-brace greps
#    match nothing and give a false all-clear.
hits=$(grep -rnE '\{\{[A-Z][A-Z0-9_]*\}\}' --include='*.md' --include='*.json' . 2>/dev/null \
  | grep -v '.git/' | grep -v '_example' | grep -v '.claude/skills/setup/' \
  | grep -v '.agents/' | grep -v 'starter/' | grep -v 'graphify-out/' \
  | grep -v 'node_modules' || true)
if [ -z "$hits" ]; then ok "no unfilled {{PLACEHOLDER}}"; else
  echo "$hits" | sed 's/^/    /'; bad "unfilled placeholders"; fi

# 7. No binary/packaged files in the repo root
binf=0
for f in *.plugin *.zip *.tar.gz *.jar; do
  [ -f "$f" ] && { echo "    $f"; binf=1; }
done
[ "$binf" -eq 0 ] && ok "no binaries in repo root" || bad "binary files in repo root"

hdr "Codex Sync Check"

# 8. The Codex port under .agents/ is generated from .claude/ - regenerate and
#    diff. This is the one that bites after any skill edit, because nothing in
#    the editing flow hints that a mirror exists.
#
#    Note --check REGENERATES before comparing, so it writes to .agents/ as a
#    side effect. Two consequences: (a) on failure the regenerated port is
#    already in your working tree, but it still has to be COMMITTED - the gate
#    compares against HEAD, and `git status --porcelain` reports staged changes
#    too, so `git add` alone never clears it; (b) you cannot test this gate by
#    hand-editing a file under .agents/ - the regeneration overwrites it and the
#    gate passes. The real failure is a .claude/ edit with no regeneration,
#    which is what CI catches.
#
#    Because of (a) this gate cannot be green before the commit. It reports PEND,
#    not FAIL, once the port content matches the source - that state is expected
#    on a pre-commit run and is not something to fix. Exit codes: 0 in sync,
#    1 stale, 2 regenerated-but-uncommitted, 3 git status failed.
codex_out=$(python3 scripts/sync-codex.py --check 2>&1); codex_rc=$?
case "$codex_rc" in
  0) ok "sync-codex --check (Codex port in sync)" ;;
  2) echo "$codex_out" | sed 's/^/    /'
     pend "sync-codex --check  -> port matches source, NOT COMMITTED yet. Commit \`.agents/**\` + \`AGENTS.md\` in the SAME commit as the skill change (\`git add\` does not clear this gate)." ;;
  3) echo "$codex_out" | sed 's/^/    /'
     bad "sync-codex --check  -> \`git status\` failed, so drift could not be determined. Fix the repo state and re-run; do NOT read this as green." ;;
  *) echo "$codex_out" | sed 's/^/    /'
     bad "sync-codex --check  -> port was STALE. The regenerated port is now in your working tree - COMMIT it (\`git add -A AGENTS.md .agents && git commit\`); staging alone leaves this gate red." ;;
esac

hdr "Result"
if [ ${#FAILED[@]} -eq 0 ] && [ ${#PENDING[@]} -eq 0 ]; then
  printf '  \033[32mAll %d gates green.\033[0m Safe to open the PR.\n\n' "$PASSED"
  exit 0
fi
if [ ${#FAILED[@]} -ne 0 ]; then
  printf '  \033[31m%d gate(s) failed:\033[0m %s\n' "${#FAILED[@]}" "$(IFS=', '; echo "${FAILED[*]}")"
fi
if [ ${#PENDING[@]} -ne 0 ]; then
  printf '  \033[33m%d gate(s) pending a commit:\033[0m %s\n' "${#PENDING[@]}" "$(IFS=', '; echo "${PENDING[*]}")"
  printf '  Pending is expected before you commit - it is not a failure to fix.\n'
  printf '  It turns green once the change is committed; CI only ever sees committed state.\n'
fi
if [ ${#FAILED[@]} -ne 0 ]; then
  printf '  %d passed. Fix the above and re-run.\n\n' "$PASSED"
  exit 1
fi
printf '  %d passed, 0 failed. Commit, then re-run to confirm all green.\n\n' "$PASSED"
exit 0
