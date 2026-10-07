---
name: gsc-freshness-check
description: Daily read-only watchdog that catches Search Console and Snowflake data going stale before a report is built on it. Checks the newest available GSC date via the Windsor.ai searchconsole connector plus Snowflake, and DMs Erika a short action list only when something is stale. Silent when fresh. Built after the Aug-Sep 2026 outage, where GSC died on 14 August and nobody noticed for three weeks. Runs daily as a cloud routine, or on demand. Trigger with "gsc freshness check", "is our search data fresh", "check gsc freshness", "is search console still flowing", "why is gsc data missing", "data freshness check", or "/gsc-freshness-check".
---

# GSC freshness check

A daily watchdog on the two data sources every SEO report stands on. It answers one question: **is Search Console still flowing, and if not, whose problem is it.**

**Read-only.** It never writes to Search Console, Snowflake or Windsor. The only side effect is one Slack DM, and only when something is stale.

**Done when:** both sources were read, each has a newest date quoted from its own query result, and exactly one of two things happened: a DM went out because at least one source is stale, or nothing was sent because both are fresh. A run that could not read a source counts as stale (guardrail 4), never as done-and-silent.

## What this skill does not do

- **Build or send the SEO report.** That is `/weekly-seo-report` (weekly) and `/organic-dashboard` (monthly). This skill only tells them whether their inputs can be trusted.
- **Fix the connector.** It names who fixes what and stops. Re-authorising Windsor or re-granting the property is a person's click.
- **Monitor Ahrefs, rankings or backlinks.** Search Console and the warehouse only.

## Why this exists

Search Console data stopped flowing on **14 August 2026**. Nobody noticed until **10 September**, and the person who noticed misdated it to 1 September. Three weekly reports went out with a stale or empty search half.

The weekly report already had a freshness gate. It did not surface. That is the failure this skill fixes: not the vendor, the silence.

**The original diagnosis was wrong, and that is why this skill now reads one GSC route.** Both Windsor and Ahrefs went dark on 14 August, and the skill concluded from the coincidence that the Google property authorisation had lapsed. On **15 September 2026** that was disproved: Windsor was serving complete daily data through 12 September, and an export taken straight from the Search Console UI for 1 Aug - 12 Sep matched Windsor **exactly** - all 43 days, clicks and impressions, zero difference, 274,139 / 14,273,628 either way. Google never stopped. Only the Ahrefs feed did, and it is still dark.

Two routes were kept so that "both dark" could indict the property. In practice the one time it fired, that inference was false and it pointed the owner at the wrong system. A permanently dark route also means a daily stale alert that is always wrong, which is how a watchdog gets muted. The cross-check is now Windsor against Snowflake - two genuinely independent systems, both of which have to be working for a report to be right.

## Scope

Target **5 to 8 lines** in the DM. Dates and one action list. No charts, no history, no narrative.

**Silent when green.** Do not DM "all fresh". A watchdog that pings daily with good news gets muted, and then it is worth nothing on the day it matters.

## Config

Property, connectors, project IDs, thresholds and recipients live in `knowledge/config.md`. Read it first.

## What it checks

Run both. Never stop at the first failure - which sources are stale *together* is the diagnostic.

| Check | Source | Stale when |
|-------|--------|-----------|
| GSC | Windsor.ai `searchconsole` connector | newest date < today − 4 |
| Warehouse | Snowflake `marketing_rollover` | newest date < today − 2 |

**Never read GSC from Ahrefs.** Its GSC endpoints have been dark since 14 August 2026 and returning an empty series is not evidence about Google. Windsor is the single source for Search Console across every skill in this repo. Ahrefs stays in use for Rank Tracker, Site Explorer and backlinks - this rule is about Search Console only.

**The date pull must carry a dimension.** Ask Windsor for `["date","search_type","clicks","impressions"]` filtered to `search_type = web`, never `["date","clicks","impressions"]` alone. A date-only pull returns collapsed buckets or a silently empty result, so a healthy property can read as no data at all - the exact false alarm this skill must not raise. Safeguard #13 in [`../organic-dashboard/knowledge/safeguards-and-gotchas.md`](../organic-dashboard/knowledge/safeguards-and-gotchas.md).

**GSC has a natural 2-day lag.** A newest date of today − 2 or today − 3 is healthy, not a warning. The threshold is 4 days for that reason, and it matches the gate already in `/weekly-seo-report`. Do not tighten it without changing both.

Resolve "today" in **Europe/London** (the owner's timezone), explicitly, not in UTC and not in the host's local zone.

## Reading the result

The pattern across the two checks names the owner. This table is the whole point of the skill - it exists so nobody has to re-derive the diagnosis under time pressure.

| Pattern | What it means | Who fixes it |
|---------|---------------|--------------|
| **GSC stale, Snowflake fresh** | The Windsor connection or the property grant. Snowflake being fine rules out a general auth sweep | Re-auth Windsor first - it is the common case and the cheap check. If that does not restore it, check Search Console, Settings, Users and permissions, confirm the connecting account is still listed, re-grant |
| **GSC fresh, Snowflake stale** | Warehouse pipeline | Data team |
| **Both stale** | Usually an auth sweep or an account deprovisioned across connectors | Property owner first, then the data team |

**Do not infer the owner from one dark source.** The 2026 outage was misdiagnosed exactly that way. Before naming the property as the cause, confirm the data is genuinely absent at Google - open the Search Console UI for the same dates. If the UI has the data, the property is fine and the problem is the connector. Say which of the two you checked.

## Guardrails

1. **Never widen the window and never silently fall back.** If a source is stale, report it stale. Quietly shifting to an older window is exactly how three weeks passed in 2026.
2. **Report the dates, never a verdict alone.** "GSC through 14 Aug, 28 days stale" is a fact. "Search data looks off" is not. Every date in the DM is quoted from the source's own query result, never estimated from the outage history above.
3. **No self check-ins.** Publish the DM and stop. There is nothing here to wait for - the check either ran or it failed.
4. **A failed connector is itself a finding.** If Windsor will not authorise, that is a stale source, not a skipped check. Report it as such and name the re-auth as the action. Never report a source as fresh because it could not be read.
5. **Read-only.** One Slack DM, nothing else.

## Output: the DM

Write it with `/ste`. Plain language, no tool names in the action list, no error strings. Each line is one thing the reader clicks or does, in order, with one line on what it unlocks. This follows the standing rule in `CLAUDE.md` - a failure is never a dead end, it becomes an action list.

Example DM (GSC stale, Snowflake fresh; the other two patterns keep this shape and swap the diagnosis line and the action list from the table above):

```
Search data is stale.

Search Console: last data 14 Aug, 28 days behind.
Snowflake: last data 10 Sep, healthy - so this is the search connection, not a general outage.

What unblocks it:
1. Re-authorise the Windsor.ai data connection. This is the usual cause and the quickest thing to rule out.
2. If that does not bring it back, open Search Console, Settings, Users and permissions. Confirm the account we connect with is still listed. Re-grant if it is gone.
3. The gap fills itself after that - Google keeps the history.

Until this is fixed the search half of the weekly report is manual.

_Posted by the Marketing OS agent_
```

## Cadence

| | |
|---|---|
| Runs | Daily, weekday mornings |
| Recipient | Erika Varangouli (see config) |
| On green | Silent |

**Deploying the routine.** This needs the Windsor.ai, Snowflake and Slack connectors. Per `references/change-control.md`, a `create_trigger` call from a repo session cannot pass through connectors held via a project-configured MCP server, and `update_trigger` cannot repair it afterwards. If the create response warns that the trigger stores no connectors, **do not deploy it** - it will look created and fail silently on every firing, which is the same class of failure this skill exists to catch. Have the owner create it at https://claude.ai/code/routines, where their own grants attach.
