# PR Doctor - state

State for `/pr-doctor`. The doctor reads this to enforce **one fix attempt per
(PR, head SHA, failure)** (SKILL.md rule 5): a PR still red on a failure already
attempted at its current head SHA is escalated, never re-fixed. Keeps the routine
from looping on a fix that did not take.

## Attempted log

One row per fix attempt. `failure` is the check + diagnosis (e.g. `codex-sync`,
`lint:dangling-ref`, `lint:example-allowlist`). `outcome` is `fixed`,
`escalated`, or `skipped-already-attempted`.

| Date | PR# | Head SHA | Failure | Outcome |
|------|-----|----------|---------|---------|
| 2026-08-24 | 249 | 9198896ef922a7e4dad1389a8c33e93670c6a16f | codex-sync | fixed |
<!-- appended by /pr-doctor; newest at the bottom -->
