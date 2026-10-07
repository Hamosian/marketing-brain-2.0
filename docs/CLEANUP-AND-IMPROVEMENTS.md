# Cleanup and Improvements

## Implemented

- Removed employee rosters, 1:1 notes, task ledgers, customer and attribution exports,
  advertising results, financial targets, and historical reports.
- Removed branded decks, logos, rendered training pages, dashboards, and graph indexes
  that embedded old context.
- Retired company-specific API tools, hard-coded account workflows, scheduled jobs,
  deployment hooks, and automatic publishing.
- Preserved general marketing methods and specialist personas; replaced operating
  workflows with company-neutral contracts.
- Added one blank company configuration schema and ignored private local context.
- Added privacy checks for known identifiers, private document links, common token
  formats, runtime data paths, and binary report artifacts.
- Kept a single canonical skill tree with a generated, checked Codex mirror.
- Added synthetic tests and a shared local/CI preflight.

## Recommended Next

| Priority | Improvement | Benefit |
| --- | --- | --- |
| First | Populate the new company's audience, positioning, and product evidence | Removes guesswork from content and strategy |
| First | Define the metric dictionary and assign owners | Prevents conflicting funnel reports |
| First | Connect and verify one system at a time | Makes account and permission problems easy to isolate |
| Next | Add dry-run adapters for the actual CRM, task system, and analytics stack | Restores automation without hard-coded accounts |
| Next | Build synthetic end-to-end tests for the three most-used workflows | Measures task quality beyond structural checks |
| Next | Track source, owner, and review date for durable knowledge | Makes stale assumptions visible |
| Later | Rebuild training pages and graphs from approved neutral inputs | Restores navigation without embedding private records |
| Later | Review third-party licenses before external redistribution | Preserves upstream authorship and licensing obligations |

## Limits

The scanner detects known patterns; it cannot prove arbitrary text contains no
personal or proprietary information. New context still needs human review.
No live company integrations or production campaigns were exercised during cleanup.

Earlier commits retain the original imported files. Local copies and external
deployments are outside this repository's current-file cleanup.
