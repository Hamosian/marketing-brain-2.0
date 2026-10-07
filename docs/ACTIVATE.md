# Activate the marketing brain

The marketing brain is this repo. It turns Claude into an operating partner for Riverside Growth that already knows our systems, boards, channels, and workflows. New teammates do not set anything up from scratch, you just turn it on.

## Three steps

1. **Get the repo.** Clone it locally, or open it in Claude Code on the web.
   ```bash
   git clone <repo-url>
   cd <repo-folder>
   ```
2. **Open Claude Code in the repo folder.** `CLAUDE.md` loads automatically. That is the brain. Everything else loads on demand when a task needs it, so the first session is instant.
3. **Connect tools as you go.** The first time Claude touches Monday, Slack, HubSpot, or Omni, approve the connection prompt (Monday uses OAuth, no API key needed). You only do this once per tool.

## First thing to say

Pick one to confirm it is live:

- `tell me about the team` runs `team-intro`, shows what the brain knows about us
- `what skills do you have?` lists every available workflow
- `good morning` daily brief: active Monday work, Slack highlights, what needs attention
- `run the marketing OS` top-level operating brief: priorities, risks, owners, actions

If those respond with real team context, the brain is active.

## Install the graphify CLI (one-time)

The repo ships a `graphify` skill (`.claude/skills/graphify/`) and knowledge-graph hooks. The skill calls a local `graphify` command, so each teammate installs the CLI once. Without it, Claude's graphify-first hooks point at a command you do not have.

```bash
uv tool install graphifyy     # recommended (isolates the package, puts it on PATH)
# or: pipx install graphifyy
```

If you do not have `uv`: `curl -LsSf https://astral.sh/uv/install.sh | sh` (or `brew install uv`). Avoid plain `pip install` on Mac/Windows, it causes PATH and module-resolution issues. Verify with `graphify --version`.

What it gives you: when `graphify-out/graph.json` exists, Claude runs `graphify query "<question>"` to orient on the codebase before grepping or reading files, so answers about how the brain is wired together are faster and more accurate. Source and full docs: https://github.com/safishamsi/graphify

## Activate Agent Flow (optional)

Agent Flow is a separate local tool that draws your Claude Code session as a live graph, so you can watch tool calls, subagent spawns, and branching as they happen. It is optional, runs entirely on your machine, and nothing in the marketing brain depends on it. Full setup, what it changes on your machine, and gotchas live in `systems/reference/agent-flow.md`.

**First time only.** Follow the Setup section in that doc: install pnpm (`npm install -g pnpm`), clone to `~/agent-flow`, then `node scripts/setup.js`. This installs a Claude Code hook and is a one-time step. Back up `~/.claude/settings.json` first.

**Run it (watch every session under your home folder):**
```bash
cd ~/agent-flow
node scripts/.dev-relay.js "$HOME" &
NEXT_PUBLIC_DEMO=0 NEXT_PUBLIC_RELAY_PORT=3001 pnpm run dev:web &
```
Then open `http://localhost:3000`. For the simpler path that only watches `~/agent-flow`, use `cd ~/agent-flow && pnpm run dev`.

**Riverside theme (optional).** `cd ~/agent-flow && git checkout riverside-theme`, then run as above.

**Stop it.** `pkill -f 'dev-relay.js'; pkill -f 'next dev'`

If you do not see your session, the relay workspace does not cover your session's directory. That is the one thing to remember.

## Notes

- You do not run `/setup`. That skill is only for standing up a brand new team context. This one already exists.
- Confirmation is required before any write (HubSpot, Monday, Slack), so exploring is safe.
- New here? Read `README.md` for the skill list and `docs/QUICKSTART.md` for the full adoption playbook.
