# Graphify and Wiki Actions

## What Runs

| Action | Trigger | Result |
| --- | --- | --- |
| Graphify Knowledge Graph | Manual run, or called by Wiki Sync | Interactive HTML, graph JSON, report, wiki Markdown, and build metadata |
| Wiki Sync | Relevant pushes to `main`, pull requests, or manual run | Builds the graph; publishes generated wiki pages only from `main` when configured |

Pull requests only build and validate. They never receive the wiki credential and
never publish. No schedules, AI API calls, marketing integrations, or public GitHub
Pages deployments are enabled by these actions.

Both workflows keep their default GitHub token read-only. Third-party actions are
pinned to commits; Graphify and the Markdown parser are pinned in
`scripts/requirements-knowledge.txt`.

## Graph Scope

The build reads tracked canonical Markdown under `.claude/`, `references/`,
`systems/`, and `docs/`, root overview documents, and maintenance scripts. It maps:

- Explicit Markdown links to other selected files.
- Exact skill references and the routing table.
- Directory membership.
- Code symbols and relationships from Graphify's local AST extractor.

This is a structural graph, not a semantic reading of every paragraph. Graphify
labels code relationships with its extraction confidence; documentation edges
represent explicit references, not invented connections. Community names use
source categories, not an LLM. Token usage is zero.

Private profiles, ignored or untracked files, skill runtime data, Git history,
and duplicate Codex mirrors are not inputs. Symlinks are rejected. Sources and
generated outputs must pass the existing privacy policy before artifact upload.
These checks catch known patterns, not every possible confidential fact; review
new shared documents before committing them.

## Open the Results

In **Actions**, open a completed **Wiki Sync** or **Graphify Knowledge Graph** run
and download **marketing-brain-knowledge**. Open `<artifact>/graph.html` to explore
the graph, or read `GRAPH_REPORT.md`. The `wiki/` directory contains the generated
pages and `<artifact>/build-info.json` records the source commit and graph counts.
The stock viewer loads its pinned visualization library from a CDN, so viewing
the HTML requires an internet connection; the JSON and report work offline.

Artifacts follow repository access controls and expire after 14 days. Generate a
fresh copy with **Run workflow**. Do not make the repository public to expose the
graph. Generated files remain ignored locally and are never auto-committed to
the source branch.

## Enable GitHub Wiki Publishing

1. A repository administrator enables **Settings > General > Features > Wikis**.
   Private-repository wikis require an eligible GitHub plan; keep this repo private.
2. Create the first page through the **Wiki** tab. GitHub must initialize the
   separate wiki Git repository before the action can clone it.
3. Create a dedicated GitHub credential able to push to this repository's wiki.
   A classic PAT with `repo` scope from a collaborator with write access is the
   standard wiki-compatible option. That scope is broad: use a dedicated account
   where possible, set an expiration, and follow your organization's token policy.
4. Store it as the repository Actions secret **WIKI_TOKEN** under
   **Settings > Secrets and variables > Actions**. Never paste it into this repo,
   a workflow file, an issue, or a chat. Do not reuse a former employer's token.
5. Run **Wiki Sync** on `main` and open **Marketing Brain** in the wiki sidebar.

The workflow deliberately does not assume its built-in `GITHUB_TOKEN` can push to
the separate wiki repository. Disabled wikis or a missing secret produce an explicit
**Wiki not published** summary while still providing the downloadable artifact.
An invalid credential or an uninitialized wiki fails the publication step visibly.

Only `Brain-*.md` pages carrying the generated ownership marker are managed.
Hand-written pages, including `<wiki>/Home.md`, are preserved. `<wiki>/_Sidebar.md`
gets a small managed navigation block. A name collision with a manual page stops publication.
Older builds cannot replace a newer `main` revision, and pushes never force-rewrite
wiki history. Edits to generated pages are replaced on the next run; put manual
notes in separate pages.

GitHub references: [Wiki setup](https://docs.github.com/en/communities/documenting-your-project-with-wikis/adding-or-editing-wiki-pages),
[wiki availability](https://docs.github.com/en/communities/documenting-your-project-with-wikis/about-wikis),
and [workflow token permissions](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token).
Graph engine: [Graphify](https://github.com/Graphify-Labs/graphify).

## Local Verification

Use a virtual environment and a fresh ignored output directory:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements-knowledge.txt
bash scripts/preflight.sh
.venv/bin/python -m unittest discover -s tests/knowledge -v
.venv/bin/python scripts/build_knowledge.py --repository Hamosian/marketing-brain-2.0 --output graphify-out/local-check
```

The build refuses to overwrite an existing output directory. Use a different
directory for the next local run. Only tracked files are selected, so stage new
documentation first when checking it locally. A local build can include working
changes; use the clean CI build when citing an exact source revision.
