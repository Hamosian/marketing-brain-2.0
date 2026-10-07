# Coach log

Memory for the **Sharpen** section of the Sunday chief-of-staff brief. Method:
`../knowledge/ai-coach.md`.

One row per finding. Read this file before rendering Sharpen, and update it on
every Sunday run.

**Rules:** a `declined` finding never comes back. A `raised` finding escalates on
its second appearance (note it is the second ask) and becomes a build-or-drop
decision on its third - it never simply re-lists. `acted` is set when the thing
shipped, not when Nir agreed to it. A habit repeats at most twice before it is
logged `not-landed` and replaced.

| date | type | finding | evidence | status |
|------|------|---------|----------|--------|
| 2026-09-07 | promote | Positioning drift had no owner - sameness checks against competitor copy were done ad hoc or not at all | Kieran Flanagan's "Are We Really Different?" pattern, raised via `/link-triage` 2026-09-07 | acted - `/are-we-really-different` shipped 2026-09-07 |
| 2026-10-04 | unused-skill | A vendor SQL count Haim asked for was answered from memory ("17 or less") and promised for next week; `/hubspot-agent` answers it in one query | C0BBMP80H36 2026-10-01 16:49-16:59; row 5 of the 2026-10-04 brief | raised |
| 2026-10-04 | stale-context | `references/growth-reporting.md` pointed the report read at a Monday board and the Drive Monthly folder; reports actually arrive in Slack DMs | Nir 2026-10-04: "monthly reports are shared on slack"; August monthlies found in DMs 3-10 Sep | acted 2026-10-04: reference and the Friday-chase source of truth now say Slack first |
| 2026-10-04 | capability | Articles Nir emails himself never reach the capture loop; only the Slack self-DM is scanned | Gmail 1a104fe8645c46a4, Kieran Flanagan "Creative Context OS" forwarded 2026-10-04 03:38 from his personal address; the Slack self-DM has had no article since 2026-08-02 | acted - Nir set preferences rule 21 on 2026-10-04: self-emailed articles are auto-triaged |
| 2026-10-04 | habit | Drop article links in the Slack self-DM instead of forwarding the email | week of 2026-10-04 | superseded - email captures handled by rule 21 instead |

Types: `promote` (work by hand that should be a skill), `stale-context` (an
intelligence file reality has moved past), `unused-skill` (a registered skill
that covered work done manually), `capability` (an available capability that fits
how Nir works), `habit` (the week's one behavior change).
