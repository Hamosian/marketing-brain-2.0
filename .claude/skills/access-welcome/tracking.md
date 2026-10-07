# Access Welcome - tracking & config

State file for the `access-welcome` skill. The skill reads and rewrites this file on every run. Do not hand-edit the Processed log during a run; add to the Handle map freely.

## GitHub handle → Slack identity map

Used to resolve a new repo collaborator (a GitHub login) to the person we DM. If a new handle is **not** here, the skill tries to resolve it from `references/team.md` (by name/email) and a Slack user search; if it still cannot resolve with high confidence, it **alerts Hanan and does not guess**.

| GitHub handle | Person | Slack ID |
|---------------|--------|----------|
| `abelgrun` | Abel Grünfeld | `U01B8LQS944` |
| `johntay10` | John Tay | `U09MQ7HR0JD` |
| `jgalili-rs` | Jonathan Galili | `U06NC1VQN7R` |
| `dordruker-tech` | Dor Druker | `U09R2APCAUU` |
| `hananamos-fm` | Hanan Amos | `U0A3HCFE90S` |
| `galyanash` | Galya Nash | `U08CNRXGX2R` |
| `eyalsolnikRS` | Eyal Solnik | `U08CRJGKAE7` |
| `raznavon-source` | Raz Navon | `U0A31DAME0G` |
| `e-varangouli` | Erika Varangouli | `U06R47T4ASJ` |
| `savionron` | Savion Ron Shemesh | `U09340B5HCM` |
| `kendall-ship-it` | Kendall Breitman | `U04V1DC70PL` |
| `arikuchar` | Ari Kuchar | `U07R8V5L19N` |
| `nikoriverside` | Nir Taranto | `U07LETHMPAP` |
| `ruben503` | Ruben Aknin | `U06MVGB6KC5` |
| `sivanmazuz` | Sivan Mazuz | `U08KPU4E7PW` |
| `ortalriverside` | Ortal Hadad | `U02MPD6U6T1` |
| `amirbartikva-art` | Amir Bar-Tikva | `U0B3NM80M1N` |
| `amirhemed-creative` | Amir Hemed | `U0B098W2QJD` |
| `timseneker-source` | Tim Seneker | `U0A7HNMQATA` |
| `adiathedesigner` | Adi Alegresi | `U0AKV6J6F7B` |
| `JarredBerman` | Jarred Ilan Berman | `U0B4Z2LCJ6A` |
| `razmessing` | Raz Messing | `U08HMKEAYC8` |
| `zalinabakhisheva` | Zalina Bakhisheva | `U09B03J0P3Q` |
| `ofratoubiana` | Ofra Toubiana | `U0BUXT80R32` |
| `jonathanydov` | Jonathan Ydov | `U0C0T6TUC8Y` |

## Processed log

Any handle listed here has already been handled and will never be re-messaged. Status values: `baseline` (present before automation, not messaged), `welcomed` (DM sent), `alerted` (could not resolve, Hanan notified), `skipped` (intentionally excluded).

| GitHub handle | Status | Date |
|---------------|--------|------|
| `abelgrun` | welcomed | 2026-06-29 |
| `johntay10` | welcomed | 2026-06-29 |
| `jgalili-rs` | baseline | 2026-06-29 |
| `dordruker-tech` | baseline | 2026-06-29 |
| `hananamos-fm` | baseline | 2026-06-29 |
| `nikoriverside` | baseline | 2026-06-29 |
| `galyanash` | baseline | 2026-06-29 |
| `eyalsolnikRS` | welcomed | 2026-07-02 |
| `raznavon-source` | welcomed | 2026-07-05 |
| `e-varangouli` | welcomed | 2026-07-08 |
| `savionron` | welcomed | 2026-07-12 |
| `kendall-ship-it` | welcomed | 2026-07-12 |
| `arikuchar` | welcomed | 2026-07-14 |
| `amirbartikva-art` | welcomed | 2026-07-20 |
| `ortalriverside` | welcomed | 2026-07-20 |
| `amirhemed-creative` | welcomed | 2026-07-20 |
| `adiathedesigner` | welcomed | 2026-07-20 |
| `JarredBerman` | welcomed | 2026-07-20 |
| `razmessing` | welcomed | 2026-08-17 |
| `zalinabakhisheva` | welcomed | 2026-08-17 |
| `timseneker-source` | skipped | 2026-09-06 |
| `sivanmazuz` | welcomed | 2026-09-14 |
| `ofratoubiana` | welcomed | 2026-09-17 |
| `jonathanydov` | welcomed | 2026-09-28 |

**`timseneker-source` is skipped because Tim Seneker left Riverside (reported 2026-09-06).** He was in the handle map but had never reached this log, so if his GitHub access outlives his employment the routine would have DM'd a departed person a "welcome to the repo" message. The `skipped` row is what stops that. Keep the handle-map row too - deleting it would only send the skill back to name-resolution and land it in the same place. Same shape as `dordruker-tech`, which stays as `baseline` after his 2026-08-04 departure.

**Departure is not access revocation.** This log stops the DM; it does nothing about the GitHub collaborator seat. Removing a leaver from `riversidefm/marketing-brain` is a separate manual step for a repo admin.

## Welcome message template

Send verbatim, substituting `{FIRST_NAME}`. Slack mrkdwn. No em dashes. Footer is mandatory.

```
Hey {FIRST_NAME}! 👋 You've got access to the Marketing OS repo (`riversidefm/marketing-brain`) now. Here's how to turn it on. You don't set anything up from scratch, you just activate it. 🚀

*1. Open the repo* 📦
Easiest, nothing to install: go to Claude Code on the web (claude.ai/code), connect your GitHub account, and pick the `marketing-brain` repo. That's it.

Comfortable in a terminal instead? Copy-paste these (don't click them):
```
git clone https://github.com/riversidefm/marketing-brain.git
cd marketing-brain
```

*2. Open Claude Code in the repo folder* 🧠
`CLAUDE.md` loads automatically. That's the brain. Everything else loads on demand, so the first session is instant.

*3. Connect tools as you go* 🔌
The first time Claude touches Monday, Slack, HubSpot, or Omni, approve the connection prompt (Monday uses OAuth, no API key). One time per tool.

*Then say one of these to confirm it's live:* ✅
• `tell me about the team`, what the brain knows about us
• `what skills do you have?`, every available workflow
• `good morning`, daily brief of active work plus Slack highlights
• `run the marketing OS`, top-level operating brief

*Prefer a guided tour first?* 🎓
Take the self-guided Marketing Brain trainer (interactive, about 15 min, ends with a quick routing check and your first command): https://claude.ai/code/artifact/54f53531-5029-40bb-8cd7-d9d68943ede2

*One-time CLI install* ⚙️ (makes codebase questions faster):
uv tool install graphifyy
(No `uv`? `brew install uv` first. Verify with `graphify --version`.)

Confirmation is required before any write (HubSpot, Monday, Slack), so exploring is totally safe. Full details are in `docs/ACTIVATE.md` and `README.md`. Ping me if anything snags! 🙌

_Posted by the Marketing OS agent_
```
