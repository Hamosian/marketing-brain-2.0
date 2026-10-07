# pr-review-router - state

State file for the `pr-review-router` skill. Holds the DM template and the Processed log. The skill reads and appends to this file; commit it back each run so idempotency survives.

## Message template

Send verbatim to the routed manager's Slack ID. Substitute only the marked fields. `{AREA}` is the manager's sub-org label (Brand / Marketing / Growth Marketing). Keep the footer as the last line.

```
Hey {FIRST_NAME} 👋 a PR just landed in your area ({AREA}) and could use your eyes 📝

*{PR_TITLE}* (#{PR_NUMBER})
Opened by {AUTHOR} · {FILE_COUNT} file(s) changed

Give it a review and *approve* or *request changes* on GitHub 👉 {PR_URL}

_Posted by the Marketing OS agent_
```

## Processed log

One row per `(PR#, manager)` pair already handled. Never re-DM a pair listed here.

| Date | PR # | Manager | Status |
|------|------|---------|--------|
| _seed_ | - | - | (no PRs processed yet) |
