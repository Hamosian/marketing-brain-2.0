---
name: gong-calls-explorer
description: Explore and analyze Gong call data with context from HubSpot - including deal info, company details, and rep performance. Use this skill whenever the user asks about Gong calls, call activity, intro calls, customer calls, who had calls this week, call volume by rep, calls by deal stage, or anything relating to recorded sales or CS conversations. Also trigger for questions like "show me calls from last week", "how many intro calls did X do", "what calls happened today", "show me calls for a specific AE/BD/CSM", or "calls by market segment". Always use this skill before querying Omni directly for Gong-related data.
---

# Gong Calls Explorer

This skill helps users explore Gong call data enriched with HubSpot context: deal stage, company, contact, and rep information.

## Available Data

The `gong_calls` topic in Omni (model: RS Snowflake, ID: `48d89fd2-ce24-44e1-bfe5-f3e30334c6dc`) contains:

**Call fields**: Conversation ID, Call Title, Started At (datetime)

**Company fields**: Company Name, Company Market (Agency / Mid Market / Enterprise), Industry, Country, Is Active Company

**Contact fields**: First Name, Last Name, Email, Persona, Seniority

**Deal fields**: Deal Name, Deal Type, Deal Status, Stage Category (Open / Won / Lost), MRR, Close Date, Is Won Deal

**Team fields**: AE Name, BD Name, CSM Name, Owner Name

---

## Workflow

### Step 1 - Ask Clarifying Questions

Before querying, ask the user a focused set of questions to scope the data. Use `AskUserQuestion` in Claude Code (`ask_user_input_v0` in a claude.ai chat) for the questions below. Ask only what's needed - don't overwhelm with every question at once. If the request already states the period and the focus, skip straight to Step 2.

**Always ask:**

1. **Time period** - What date range? (Today / This week / Last 7 days / Last 30 days / Custom)
2. **Focus area** - What do they want to see? (Call list / Call volume by rep / Calls by deal stage / Calls by market segment / Calls by industry / Custom question)

**Ask conditionally** (only if relevant to the focus area):

- **Rep filter** - If they mention a specific person or "my calls": AE Name, BD Name, CSM Name, or Owner Name
- **Market segment** - Agency / Mid Market / Enterprise / All
- **Deal type filter** - Pre-Opp / New Sales / Renewals / Upsell / All
- **Stage filter** - Open / Won / Lost / All

### Step 2 - Translate to a Natural Language Query

Convert the user's answers into a clear plain-English question. Examples:

- "Show me all calls from the last 7 days with call title, company name, AE name, deal type, and deal status"
- "Count of calls per AE this week, grouped by deal type"
- "Calls from last 30 days for Enterprise accounts, showing company, deal status, MRR, and CSM name"
- "Number of intro calls per BD rep in the last 14 days"
- "Calls this week grouped by market segment and stage category"

### Step 3 - Query Omni

Call `Omni Analytics:getData` with:
- `topicId`: `gong_calls`
- `modelId`: `48d89fd2-ce24-44e1-bfe5-f3e30334c6dc`
- `prompt`: the natural language question from Step 2

### Step 4 - Present Results

- If the result is a **list of calls**: show as a clean table (Call Title, Date, Company, Rep, Deal Status at minimum)
- If the result is **aggregated/counted data**: show a summary table. Where a chart tool exists (`visualize:show_widget` in a claude.ai chat; read `read_me` with module `chart` first), add a bar chart
- Always show the Omni workbook URL if one is returned, so the user can explore further
- Add a 1-2 sentence summary of what the data shows
- Before quoting a number, read the column headers and the `query.filters` block `getData` returns. It can silently answer with a near-match field or rewrite an absolute date range (`systems/owned/omni-bi.md`, Known Issues); a substituted field is a finding to report, not an answer

**Done when:** the answer states the period (UTC) and filters actually applied, every figure comes from the returned result, and the workbook URL is attached when Omni returned one. Never invent a call, a rep or a count; an empty result says so and names the filters that produced it.

**Output format, for example** "how many intro calls did each BD do in the last 14 days" (period and focus are both given, so Step 1 is skipped):

```
Intro calls per BD, last 14 days (UTC), from Omni gong_calls
| BD Name | Intro calls |
| <name from result> | <count from result> |
Filter used: title contains "Intro" or Deal Type contains "Pre-Opp"
Workbook: <url returned by getData>
<1-2 sentence read of the table>
```

---

## Reading actual transcripts (Snowflake, not Omni)

**The Omni `gong_calls` topic carries metadata only. It has no transcript text.** For "what did they actually say" work (qualification analysis, win-loss verbatims, objection mining), go to Snowflake via `sql_exec_tool`. Discovered 2026-09-15 while analysing 31 vendor-booked intro calls.

| Table | Use |
|---|---|
| `ANALYTICS.TRF.INT_GONG__CALLS` | `TRANSCRIPT_TEXT` (speaker-labelled plain text, the one you want), plus `CONVERSATION_ID`, `CALL_TITLE`, `STARTED_AT`, `CALL_URL` |
| `ANALYTICS.STG.STG_GONG__CALLS` | `SPOTLIGHT_BRIEF` (Gong's own AI call summary), `SPOTLIGHT_OUTCOME`, `SPOTLIGHT_NEXT_STEPS`, `BROWSER_DURATION_SEC`, keyed on `CONVERSATION_KEY` |
| `ANALYTICS.STG.STG_GONG__CONVERSATION_PARTICIPANTS` | `SPEAKER_EMAIL`, `SPEAKER_NAME`, `AFFILIATION` (`company` / `non_company`). **This is how you find calls for a person or a company, and how you find every call a given SDR or vendor rep joined.** |
| `ANALYTICS.ENT.BRIDGE__GONG_CALL__CONTACTS` / `__DEALS` / `__COMPANIES` | Join `CONVERSATION_ID` to HubSpot ids |

Two joins worth knowing: `INT_GONG__CALLS` keys on `CONVERSATION_ID`, while the `STG_GONG__*` tables key on `CONVERSATION_KEY`. `STG_GONG__CALLS` carries both, so join through it.

### Always read SPOTLIGHT_BRIEF first

`SPOTLIGHT_BRIEF` is a two-to-three sentence AI summary of the call, already written. Pulling it for 40 calls costs a fraction of one transcript. Use it to triage which calls deserve a full read, and only then pull `TRANSCRIPT_TEXT`.

### Transcripts overflow the tool result limit

A single transcript is 15-80KB. Three or more in one query exceeds the result cap and lands in a spill file. The pattern that works:

1. Query `SPOTLIGHT_BRIEF` across the whole set to scope it.
2. Pull `TRANSCRIPT_TEXT` in batches of **three conversation ids at a time**.
3. Write each transcript to its own file in the scratchpad directory, named `<date>_<title>_<conversation_id>.txt`, with the Gong URL (`https://app.gong.io/call?id=<CONVERSATION_ID>`) in a header line.
4. Write a per-call analysis rubric to a file next to them, then fan out to subagents, roughly eight transcripts each, each writing its output to a file and returning it.

Never pull a dozen transcripts into the main context. It will not fit and the spill files are single-line JSON that `Read` cannot chunk.

### `sql_exec_tool` needs a fully qualified table name

The Snowflake MCP has no default namespace. `SELECT ... FROM information_schema.tables` fails with "You must specify the database to use". Prefix everything with the database: `ANALYTICS.STG.STG_GONG__CALLS`, `ANALYTICS.information_schema.columns`. `SHOW DATABASES` works unqualified and is the fastest way to confirm what you can reach.

---

## What this skill does not own

This skill reads and lists calls. It does not own:

- **Why deals are won or lost on price**, coded across calls and deals: `/win-loss-pricing-analyzer`.
- **Scoring a vendor-booked (Ziff) meeting brief or labelling its outcome**: `/vendor-meeting-quality`.
- **Intro meetings as a funnel KPI** (meetings booked or completed, SQLs, BD credit): those are Pre-Op records, defined in `/preop-data-intelligence`; aggregate figures for a report go to `/rivermind:ask` first, per CLAUDE.md.
- **Other Omni topics and raw Snowflake work** outside Gong: `/data-agent`.

## Design Notes

- Never guess at filter values; ask for any the request does not state
- When asking about a specific rep, search across AE Name, BD Name, CSM Name, and Owner Name
- "Intro calls" = calls with "Intro" in the title or Deal Type containing "Pre-Opp"
- Dates in the data are in UTC; mention this if precision matters
- If results are empty, suggest broadening the time range or removing filters
