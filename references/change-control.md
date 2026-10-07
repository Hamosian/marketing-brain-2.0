# Change Control - landing a change so it actually runs

How a change to a skill, routine, or reference gets from "written" to "running in production." Written after the 2026-08-09 weekend, when three changes were authored, reviewed, and believed shipped, and only one of them was actually in effect.

Load this when you are about to edit a skill, open a PR against this repo, or document a new cadence for a scheduled routine.

## The failure this prevents

A change is not done when the file is written. It is done when **the branch that production reads** contains it. Those are different things, and the gap between them is invisible unless you go looking.

Three ways a change silently fails to land:

| Failure | What it looks like | Caught by |
|---|---|---|
| **Merged to the wrong base** | PR merges green into a feature branch, not `main` | Step 3 below |
| **Half a change** | A doc references a file that shipped on a different branch | `scripts/lint_references.py` in CI |
| **Documented, not implemented** | A skill describes a cadence, integration, or step that nothing actually executes | Step 4 below |

All three happened in one weekend. None of them produced an error.

## The five checks

Run all five before calling a change done. They take about two minutes together.

### 1. Base the branch on `main`, and keep it to one concern

`git checkout main && git pull && git checkout -b <type>/<slug>`

One concern per branch. A branch that accretes unrelated work becomes hard to review, sits open, and gets superseded rather than merged. Two of the weekend's branches carried four unrelated subsystems each.

### 2. Everything the change needs ships in the same PR

If a skill file now says "read `.claude/skills/inbound-demo-reply/pain-map.md`", the PR that adds that sentence adds the file. Never split a reference from its referent across PRs, even when the second PR is "coming right after." CI enforces this on changed files via `scripts/lint_references.py`.

Run it yourself first - but not on its own. **One command runs every gate CI runs:**

```bash
bash scripts/preflight.sh
```

Eight gates, in CI's order, all of them executed even after one fails so you see every
problem in one pass. Pass a base ref as `$1` if you are not targeting `main`.

### 3. Verify the merge landed on `main`, not somewhere else

A green merge is not proof. GitHub will happily merge a PR into whatever base it was opened against, and the notification reads identically either way.

```bash
git fetch origin && git log origin/main --oneline -5
git cat-file -e origin/main:<path/to/every/file/you/added> && echo LANDED || echo NOT ON MAIN
```

Check the **files**, not the commit. Squash and rebase merges rewrite SHAs, so `git merge-base --is-ancestor` on your local commit will say NO even when the content did land. File existence on `origin/main` is the honest test.

**File existence is the honest test only for a change that adds files.** For a change that *edits* an existing file, `git cat-file -e` returns LANDED whether or not your edit is in it - the file was already there. Grep `origin/main` for a distinctive phrase the change introduced:

```bash
git fetch origin && git show origin/main:<path> | grep -c "<phrase your change introduced>"
```

This is not hypothetical: the `cat-file -e` form above would have reported LANDED for the merge described next, because the file it edits has existed on `main` since the skill was created.

**A stacked PR whose base merges first can merge into a dead branch and still report success.** GitHub re-targets a stacked PR to `main` when its base merges, but that is a background job and it loses to a fast human. Verified 2026-09-02: #277 (base `main`) merged at 09:56:39, #278 (base `ops/ticket-hygiene-ledger-catchup-aug27-sep01`) twenty seconds later at 09:56:59. The re-target never fired, so #278 merged into a branch that was already dead and its content never reached `main`. It had to be re-opened as #279 against `main`.

`state: MERGED` is therefore not the field to read - it was true for #278, with a real merge commit, pointing at the wrong branch. Read the **base**, and confirm GitHub's own merge commit is reachable from `main`:

```bash
gh pr view <n> --json state,baseRefName,mergeCommit \
  --jq '"\(.state) base=\(.baseRefName) merge=\(.mergeCommit.oid[0:7])"'
git merge-base --is-ancestor <that merge commit> origin/main && echo ON MAIN || echo NOT ON MAIN
```

That is GitHub's merge commit, not your local one - the object the caveat above warns about is the pre-merge commit on your branch, which squash and rebase strategies discard.

**Cheapest fix is not to stack.** Stacking earns its cost only when the child genuinely cannot be reviewed without the base in front of it. When both are ready together, merge the base, let `main` settle, then open the child against `main`.

### 4. If the change describes behaviour, verify the thing that performs it exists

This is the check that has no automation and needs a human every time. Documentation of a behaviour is not the behaviour.

- **New or changed cadence?** List the actual schedule and confirm it matches. **There are two schedulers and they are separate lists** - `mcp__scheduled-tasks__list_scheduled_tasks` covers only *local* tasks on one machine, while cloud routines live behind `RemoteTrigger {action: "list"}`. Checking one and concluding "not scheduled" is a false negative; checking the local list for a cloud routine will always come back empty. A skill saying "runs twice daily" with one cron in the relevant list is a documentation-only change. See the cloud-routine section below.
- **New column, field, or tag?** Confirm something writes it, and that a real row now carries a value. A column that only ever holds one value is a signal that half the mechanism is missing.
- **New skill invoked by another skill?** Confirm the callee exists on the same branch and that the caller actually invokes it, not just mentions it.
- **New downstream consumer?** Confirm it reads the new thing.

### 5. Say what you verified, not what you changed

In the PR description and in any report to a stakeholder, state the verification, not the intent. "Added the evening run" is a claim about a file. "Two crons now listed, 09:00 and 17:00, next runs 08-11" is a claim about production. Only the second one is checkable.

## The eight PR gates, and why running three of them is not enough

Two workflows fire on every `pull_request`. `scripts/preflight.sh` runs all eight locally.

| # | Gate | Workflow |
|---|---|---|
| 1 | `scripts/lint_skill_frontmatter.py` - frontmatter **parses**; `description` under **1024 chars** | team-context-lint |
| 2 | `scripts/lint_references.py --changed-only origin/<base>` | team-context-lint |
| 3 | `scripts/lint_agents.py` | team-context-lint |
| 4 | `scripts/harmonize_agents.py --check` | team-context-lint |
| 5 | `scripts/eval_routing.py --coverage` | team-context-lint |
| 6 | No unfilled `{{ PLACEHOLDER }}` tokens (doubled braces, UPPER_SNAKE, **no space**) | team-context-lint |
| 7 | No binary/packaged files in the repo root | team-context-lint |
| 8 | `scripts/sync-codex.py --check` | **codex-sync-check** |

**Gate 8 is the one that catches people, including agents.** Every skill under
`.claude/skills/` has a generated mirror under `.agents/skills/`, and **`CLAUDE.md` itself
generates `AGENTS.md`** - so editing the always-loaded map trips this gate just as a skill
edit does. Verified 2026-08-23: an edit to CLAUDE.md alone failed gate 8. Nothing in the editing flow hints the mirror exists, so any skill edit that
does not re-run the generator lands a red PR for an entirely mechanical reason. Verified
2026-08-23 on PR #246: three edited skill files, `lint` green, `codex-sync` red.

Three details worth knowing before you debug it:

- `--check` **regenerates before comparing**, so it writes to `.agents/` as a side effect.
  On failure the fix is *already applied* in your working tree - but it still has to be
  **committed**.
- **`git add` does not clear this gate. Only a commit does.** The check reads
  `git status --porcelain AGENTS.md .agents`, which reports staged changes too - after
  `git add -A` the port shows as `M ` (staged, worktree clean) and the gate stays red.
  Committing is the only thing that empties it. Confirmed empirically 2026-09-15, after the
  old preflight hint (`just: git add -A`) sent a reader into a loop. **So the gate cannot be
  green before the commit:** a pre-commit preflight run always flags it when you touched a
  skill or `CLAUDE.md`. That is expected, not a failure to chase.
- For the same reason you cannot test the gate by hand-editing a file under `.agents/`;
  regeneration overwrites your edit and the gate passes. The real failure is a `.claude/`
  edit with no regeneration.

`--check` separates those two cases, because "port is stale" and "port is correct but not
committed yet" look identical to `git status` alone. It digests the generated paths either
side of the regeneration: if regenerating *changed* them, the committed port was genuinely
stale; if it changed nothing, the port already matched its source and only the commit is
missing.

| `--check` exit | Meaning | preflight |
|---|---|---|
| 0 | Port in sync **and committed** | `PASS` |
| 1 | Port was **stale** - regeneration rewrote it; commit the result | `FAIL` |
| 2 | Port matches source, **not committed yet** | `PEND` |
| 3 | `git status` failed - drift could not be determined | `FAIL` |

A failing `git status` prints nothing to stdout, so treating its return code as
irrelevant would make a broken repo look like a clean tree and pass the gate. It exits 3
instead - a drift gate must never go green because it could not measure drift.

Exit 2 needs a dirty working tree, so a clean CI checkout can never produce it - CI still
only ever sees 0 or 1, and any non-zero fails the job. `PEND` is amber in preflight and does
not count as a failed gate, so a pre-commit run is not red for a mechanical reason; the
summary still calls it out, because committing the skill *without* the port is exactly the
mistake gate 8 exists to catch. Commit `.agents/**` and `AGENTS.md` in the **same commit**
as the change that caused them.

**Gate 6 is easy to fake-check.** The pattern is a *doubled* brace around an UPPER_SNAKE
token with no space after the braces. A single-brace grep (`{UPPER_SNAKE}`) matches nothing
in this repo and returns a confident all-clear, which is worse than not checking.

Gate 6 also fires on documentation *about* the pattern - writing a literal example trips it.
CI's regex requires the uppercase letter immediately after the braces, so write the spaced
form (`{{ LIKE_THIS }}`) when you need to quote it. Lowercase spaced tokens are exempt by
design, so HubSpot personalization syntax passes.

When you add a CI step, add it to `scripts/preflight.sh` in the same commit. A local gate
that has quietly stopped matching CI is how this failure mode comes back.

### Gate 1 parses the frontmatter; it used to grep it.

Until 2026-09-02 gate 1 was inline bash that checked `name:` and `description:` were
*present* and measured the description with a one-line `awk` substitution. Three skills
shipped broken past it, all on `main`:

- `link-triage` - an unquoted description containing `Human-in-the-loop:` plus a space.
  YAML reads a colon followed by a space as a nested mapping, so the file raised
  `mapping values are not allowed here` and the skill ran with **no description at all** -
  nothing could route to it by description match, and the harness fell back to the H1.
- `webflow-accessibility-audit` and `webflow-link-checker` - unquoted descriptions naming a
  Slack channel, which puts a `#` just after a space. These *parse*, and then YAML silently
  truncates the value at the `#`, dropping 186 and 165 characters of trigger phrases. A
  parse-exception sweep cannot see this one; only comparing the decoded value to the
  authored text can.

Two lessons worth keeping. **A gate that greps for a key cannot tell you the key's value
survives parsing** - presence and correctness are different checks. And the old `awk`
measured the first physical line, so for the 18 skills using a `>-` block scalar it
measured the literal `>-` as a 2-char description: the 1024 cap was not being enforced on
them at all. The replacement decodes the value first, then measures.

`scripts/lint_agents.py` still carries the same blind spot in its own `parse_frontmatter`
(documented there as a "minimal top-level `key: value` parse" that "avoids a pyyaml dep"),
which is why gate 1 now covers `.claude/agents/**` too rather than skills alone.

**Stdlib only, deliberately.** No script in this repo imports pyyaml and the lint workflow
installs nothing, so a pyyaml import would make the gate depend on whatever the runner
image ships. `scripts/lint_skill_frontmatter.py` is a parser for the YAML subset the repo
actually uses.

**If you edit that file, run `--selftest` (37 cases) before pushing.** A hand-written YAML
subset parser is exactly the kind of code that looks right and is quietly wrong, so it was
differentially fuzzed against pyyaml -- 560,000 generated frontmatters, comparing both the
accept/reject verdict and every decoded string. The first run found eight defects in it,
including four that would have *blocked valid PRs*: flow sequences (`tools: [Read, Write]`)
rejected as malformed, an unsound "a nested block cannot mix sequence entries with mapping
keys" rule (YAML allows a sequence at its parent key's indent), an empty block-scalar body
treated as an error, and a comment line inside a block scalar read as content. Every one of
those is now a case in `--selftest`, which is why that suite is the guard rather than a
formality. Final measurement: 0 false positives, 0 value drift, 13 false negatives (0.0023%),
all one shape -- a comment inside a nested block followed by a more-indented line.

**A fuzzer only finds what its generator can emit.** Ours never produced a value *starting*
with `#`, and that was the one defect it missed: `description: #routing text` is null in
YAML, and the parser was reading it as a 14-character description, so a skill could have
carried no runtime description and still passed. Code review caught it where 400,000
samples had not. If you extend the parser, extend the generator's value list too.

The gate is deliberately stricter than YAML in five places, each because YAML's reading is
not the author's: a space-then-`#` truncation, duplicate keys, anchors/aliases/tags,
keep-chomping
(`|+`), and a more-indented line inside a folded block. The error message names the fix.

### All eight gates are structural. None of them is behavioural.

Every gate above checks the *shape* of a file: frontmatter present, references resolve,
mirrors regenerated, no placeholders. None checks whether an agent obeyed a rule the repo
already states in prose. So the rules that get broken most often are exactly the ones no gate
covers - a bare URL on the last line of a Slack message (which Slack absorbs into the link and
404s), drafting a message without showing it first, calling the monday API directly instead of
`/pm-story`, skipping the Codex port. Each of those is written down somewhere as a soft rule,
and each has been broken after being written down.

**A correction that recurs should become a check that fails loudly, not a reminder the agent
can forget.** When a standing memory or a soft `CLAUDE.md` rule gets violated twice, that is
the signal to promote it: write the behavioural assertion into `scripts/preflight.sh` (or into
the skill's own steps as a hard stop) rather than restating it in prose a third time. Prose
scales with how much context the agent is holding; a failing check does not.

Worth an explicit pass: read the standing memories and the soft rules in `CLAUDE.md`, pick the
ones with a real failure history, and turn the highest-value few into checks. Filed from the
Lauren Tan agent workshop, 2026-08-29.

## CI enforcement of check 2 (live)

Check 2 is now automated. `scripts/lint_references.py` runs in CI via the `Referenced files must exist on this branch` step in `.github/workflows/team-context-lint.yml`, which blocks a PR when it references a file that is not present on the branch. This is the guard that would have caught the pain-map slip: a file referenced from `main` while it still sat on a feature branch. Applied to `main` via PR #192 on 2026-08-10.

To run the same check locally before opening a PR:

```bash
python3 scripts/lint_references.py --changed-only main
```

## Cloud routines have their own way of not running

A cloud routine (created via `/schedule` → `RemoteTrigger`) spawns an isolated cloud session with its own git checkout. That isolation is the point, and it is also seven new ways for a change to be "written but not running." The first four were verified 2026-08-11 while scheduling `/ticket-hygiene`; 5 and 6 came out of watching that same routine run for three weeks.

### 1. The routine checks out the default branch, not your branch

This is the big one, and it is check 3 wearing a different hat. A routine pointed at `https://github.com/riversidefm/marketing-brain` clones **`main`**. A skill that only exists on a feature branch does not exist as far as the routine is concerned - it will start, fail to find the skill file, and either abort or improvise. Registering a routine for an unmerged skill produces a scheduled job that is guaranteed to fail on its first fire.

```bash
git ls-tree -r origin/main --name-only | grep "<your skill dir>"
```

Empty output means the routine has nothing to run. **Merge first, then register** - or register disabled and enable after the merge.

### 2. Hand-writing `allowed_tools` silently removes `Skill`

Omit `allowed_tools` and the routine gets `preset:default`, which includes `Skill`, `Task`, `Bash`, `Read`/`Write`/`Edit`, `WebFetch`, and the rest. Specify it by hand and you get **exactly** what you listed. A plausible-looking `["Bash","Read","Write","Edit","Glob","Grep"]` omits `Skill`, which breaks any routine whose entire job is to invoke a skill - and it breaks it quietly, because the session still starts and still does *something*. Prefer omitting the field unless you have a specific reason to narrow it.

### 3. The connector list shown at setup time can be stale

`/schedule` may report "No MCP connectors found" while the create call in fact attaches the account's full connector set (16 of them, including `monday_com`, `Slack`, `HubSpot`, `Google_Drive`). **Read the connectors back off the created routine** rather than trusting the pre-flight note - and do not redesign a routine around a missing connector, or disable it as unusable, before checking the response body.

### 4. Cron is UTC-only, so local-time schedules drift with DST

`cron_expression` has no timezone. `0 6 * * *` is 09:00 Asia/Jerusalem during IDT (UTC+3) and 08:00 during IST (UTC+2). Every routine expressed in local time silently shifts by an hour at each DST boundary - end of October and end of March. Record the intended *local* time next to the cron in the skill doc, so the drift is a one-field fix rather than a mystery. Minimum interval is 1 hour; sub-hourly crons are rejected.

### 5. A session with no passable connector grants creates a routine with none - silently

Check 3 above covers a *stale display* (the setup UI undersells what actually got attached). The opposite failure is real too, and it does not show up as a UI quirk - it shows up as a warning on the `create_trigger` response itself: **"this trigger stores no MCP connectors, so the sessions it fires will run without connector (`mcp__<server>__*`) tools."** Confirmed 2026-08-18 building `/raz-ops`'s weekly digest: `create_trigger`, called from a shared Claude Code Remote repo session, cannot pass through connectors the calling session doesn't itself hold as passable grants - even when that session clearly has live `mcp__Slack__*` (or other) tools available to it directly, if those came from a project-configured MCP server rather than a personal claude.ai OAuth connector. `update_trigger` cannot add connectors after the fact either - there is no repair path once the routine exists.

The tool tells you outright when this happens; do not skip past the warning text. If a routine needs a connector and this warning fires, **do not deploy it anyway** - it will look created and then fail on every real firing. Either create it from a session that does hold the connector as a passable grant, or have the routine's owner create it themselves at https://claude.ai/code/routines, where their own session's connector grants are available to attach.

### 6. `session_context` silently drops fields it does not support - including `effort`

Verified 2026-09-01 against `trig_01C4YkvKC8sux2oM5uZ4TAVi`: sending
`{"model": "claude-opus-5", "effort": "high", ...}` inside `job_config.ccr.session_context`
returns **HTTP 200 with no error**, and the stored config comes back as
`{allowed_tools, model, sources}` - the `effort` key is simply gone. Not rejected, not
warned about. A routine can therefore be "configured" for an effort level it never runs at,
and nothing anywhere will say so.

Two consequences:

- **The usual first cost lever is unavailable here.** For Messages API code, the move before
  changing models is the same model at lower effort. A cloud routine cannot do that. Its
  tunable surface is `model`, `sources`, `allowed_tools`, `environment_id`, the cron, and the
  prompt - nothing else. If a routine is doing too much or too little thinking, **the prompt
  is the only lever**.
- **Never trust an `update` that returns 200.** Read the returned `job_config` and confirm the
  field you set is present. Silence is not confirmation. This is the same lesson as the
  board-relation write in `references/monday_boards.md`, from the opposite direction: there
  the API reported `null` on a write that succeeded; here it reports success on a write that
  was discarded. In both cases the only honest check is a read-back.

### 7. A routine that watches its own PR will re-arm until someone merges

Between 2026-08-24 and 2026-09-01, `/ticket-hygiene` INTAKE armed roughly **eighteen** self
check-ins via `send_later` - up to **eight on a single PR** (#254 fired at 07:24, 08:25,
09:27, 10:29, 11:31, 12:33, 13:36, 14:41), six on #260. Each firing is a full cloud session
that wakes, reads notifications, finds that a review bot edited its own comment in place,
changes nothing, and re-arms.

**Nothing in the routine prompt asked for this.** The agent self-arms because nothing bounds
it, and the condition it picks - "keep checking until the PR merges" - is unbounded when
merging is a human queue. That is the trap: the stopping condition sounds definite and is
not under the agent's control.

- Any routine that opens a PR needs an explicit follow-up bound in its **prompt**: check
  once, at most one re-arm, and treat "green with no open review threads" as done regardless
  of merge state.
- Spent check-ins persist as trigger objects (`ended_reason: run_once_fired`, disabled).
  They are inert but they crowd `RemoteTrigger {action: "list"}` - 19 of the first 20
  triggers returned were spent check-ins, which buries the real routines. Worse, one was
  found still `enabled` with a future `next_run_at`, pointed at a PR that had already merged.
- **Triggers cannot be deleted through the API.** Disable a stale one with
  `RemoteTrigger {action: "update", body: {"enabled": false}}`; deletion is manual at
  https://claude.ai/code/routines.

### Local routines have the opposite problem: they read your working tree

A cloud routine clones `main` and cannot see your branch. A **local** scheduled task reads the checkout it runs in, so it sees whatever branch you happen to be standing on, including uncommitted edits. Neither the routine nor the skill it loads checks that file against `main`.

That turns any unmerged branch into a silent downgrade of every local routine. Verified 2026-09-02: an over-revert on an unrelated feature branch left `.claude/skills/inbound-demo-reply/SKILL.md` **27 lines behind `main`**, and the evening run read the degraded file for hours. Missing rules included the `Outcome` column (so 17 log rows shipped unscoreable) and "Paste the anchor WHOLE", the rule written that same day to stop exactly the claim the run then shipped to a lead.

Before a local routine run that matters, confirm the skill it reads matches `main`:

```bash
git diff --stat origin/main -- .claude/skills/<skill>/
```

Non-empty output means the routine is not running the team's rules. Either merge, or stash and run from `main`. Two habits make this rarer: **keep feature branches short-lived**, and **never `git add -A` on a branch scoped to one concern** - the sweep pulls in unrelated files, and the corrective revert is what over-reverts. Both commits in the 2026-09-02 case were well intentioned.

### Another session can be writing into the same checkout, and onto your branch

Two agent sessions open on the same repo share one working tree and one `HEAD`. The second
one commits to whatever branch the first is standing on. Verified 2026-09-07: a concurrent
session committed an unrelated skill change onto a feature branch mid-task, and that commit
would have ridden into the PR - failing CI on its own dangling references, and putting two
unrelated concerns in front of one reviewer.

It also modifies files under you. `git status` showing a skill as dirty does not mean you
touched it, and `git add -A` is how someone else's half-finished work ships under your name.

What actually works:

- **Check authorship before staging.** `git diff <path>` on every dirty file you did not
  edit. Stage by explicit path, never `-A`.
- **Never `git stash` to get unblocked.** It moves the other session's uncommitted work, and
  it can write during the window.
- **Run the gates in a detached worktree at your own commit**
  (`git worktree add --detach <tmp> HEAD`), not in the shared checkout. The shared tree's
  dirty files make `sync-codex --check` report drift that is not in what you are shipping,
  and you cannot tell a real failure from someone else's.
- **If a foreign commit is already on your branch,** branch it first so it cannot be lost,
  then rebase yours onto `main` with `git rebase --onto origin/main <foreign-sha>`. Never
  drop it - it may be the only reference to that work.

### Read a gate's exit status, not its output

`bash scripts/preflight.sh | grep -c FAIL` and then acting on the grep is how a push happens
on a red gate: `grep` succeeds when it *finds* the failure, so an `&&` chain after it runs
exactly when it should not. Branch on the count being zero, or on preflight's own exit code.
Caught 2026-09-07 after a force-push went out on a failing `lint_references`.

### Also worth knowing

- Routines cannot be deleted through the API. Direct people to https://claude.ai/code/routines.
- `next_run_at` includes several minutes of jitter - a `0 6` cron reports `06:08`. That is normal, not a misconfiguration.
- A routine that writes to shared state unattended should carry its precondition check *in the prompt*: verify the systems it needs are reachable and **abort without writing** if they are not. A half-run writer is worse than a skipped run.
- **The `<!-- last-reviewed -->` header is the most common merge conflict in `systems/**`.** Every PR that touches a system doc edits line 1, so two same-day PRs on one doc always collide there. When you add an entry, **demote the previous `last-reviewed` line to `prior:`** rather than overwriting it. When you resolve the conflict, keep both entries, newest first, and restore any `prior:` line the other side dropped. Neither side's entry is ever the one to delete. Hit on PR #388 (2026-09-23), where the other branch had replaced the 2026-09-17 entry instead of demoting it.

## Where changes live

| Change type | Home | Gate |
|---|---|---|
| Skill behaviour, new rule | `.claude/skills/<name>/SKILL.md` | PR + CI lint |
| Generated data (pain maps, ledgers) | The skill's own directory | PR; regenerate, never hand-patch |
| Cadence / schedule | The scheduled task, AND the skill doc | Both, or neither is true |
| Team convention | `CLAUDE.md` or `references/` | PR |
| User preference | Memory | n/a |

## Standing rule for agents working in this repo

When you finish a change, do not report it as shipped until check 3 and check 4 pass. If you cannot run them (no push access, no scheduler access), say explicitly that the change is written but unverified, and name which check is outstanding. "Written but not landed" is a useful status. "Done" when it means "written" is not.
