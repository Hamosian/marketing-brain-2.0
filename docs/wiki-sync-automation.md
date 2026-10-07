# Wiki + graph sync automation

The GitHub Wiki, the Graphify knowledge graph (`graphify-out/graph.json`), and the semantic search index (`graphify-out/embeddings.json`) are generated views of this repository. The `Wiki + Graph Sync` workflow keeps all three current after every pull request merge into `main`, without an Anthropic API key or Claude OAuth token.

## How it works

The workflow is `.github/workflows/doc-agent-on-merge.yml`. It can also be started manually with `workflow_dispatch`.

### Wiki

1. `wiki-build` checks out `main`, clones the wiki, and runs `scripts/sync_wiki.py`.
2. The script maps changed source files to wiki pages, rewrites repository links, regenerates navigation and catalogs, and updates the wiki's Recent Changes page.
3. The read-only job uploads a binary-safe patch.
4. `wiki-commit` applies that patch and pushes the wiki.

Wiki generation is deterministic Python. It does not call a model. Every run performs a full reconciliation, but generated banners are stable, so only pages whose source or generated navigation actually changed appear in the patch.

### Knowledge graph

1. `graph-build` installs the pinned `graphifyy` package and runs `scripts/sync_graph.py`.
2. The script reads `built_at_commit` from `graphify-out/graph.json`, finds indexed files changed since that commit, and performs deterministic AST extraction for code.
3. Graphify's deterministic Markdown extractor maps documents and headings. Repo-owned fallbacks map HTML headings and GitHub Actions workflow jobs; any other supported document receives a source-backed file node.
4. The updater merges that source structure, preserves existing community names, reclusters, and regenerates `graphify-out/graph.json` and `graphify-out/GRAPH_REPORT.md`. It does not write the stock graphify HTML viewer: that export hard-fails above 5000 nodes, and `graphify-out/graph-explorer.html` supersedes it.
5. `scripts/graph_explorer.py` rebuilds the Riverside explorer. The read-only job uploads a patch, and `graph-commit` applies and pushes only paths under `graphify-out/`.

The committed graph retains richer semantic concepts from model-assisted refreshes. Merge automation keeps changed sources structurally current without inference. A maintainer can still run `scripts/sync_graph.py --semantic-mode model` locally, or enable model mode in Actions after the organization grants GitHub Models access.

### Semantic search index

1. `embeddings-build` installs no extra package (pure standard library) and runs `scripts/sync_embeddings.py`.
2. The script chunks every indexed Markdown file (`CLAUDE.md`, `references/`, `systems/`, `docs/`, `.claude/skills/`, `.claude/agents/`) by heading, then vectorizes each chunk.
3. In CI (`EMBEDDINGS_MODE: tfidf`), vectors are deterministic TF-IDF sparse vectors - no model call, no credential, ranks chunks by weighted term overlap rather than exact string/keyword match.
4. A maintainer can run `OPENAI_API_KEY=... python3 scripts/sync_embeddings.py --mode model` locally (or with `--mode auto`, which picks model mode automatically when `OPENAI_API_KEY` is set) to get dense embeddings from an OpenAI-compatible `/embeddings` endpoint, which additionally catch paraphrase/synonym similarity that TF-IDF cosine misses.
5. `embeddings-commit` applies the patch, restricted to `graphify-out/embeddings.json` only, same as the graph's path boundary.

Query the index with:

```bash
python3 scripts/semantic_search.py "how does BD attribution work"
```

This is a full rebuild every run, like the wiki generator - the corpus is small enough that incremental re-indexing isn't worth the complexity, and TF-IDF's idf weights are corpus-global anyway.

## Authentication

No repository LLM secret is required, and the default workflow does not call a model.

- GitHub creates a short-lived `GITHUB_TOKEN` for each job.
- Build jobs grant that token `contents: read` only.
- The wiki and graph commit jobs separately receive `contents: write` and never run model inference.

GitHub Models was tested as the optional model backend, but Riverside organization policy currently returns `403` to repository Actions tokens. An organization owner can enable GitHub Models and allow a model later; that permits `models: read` with the ephemeral token, still without a stored model secret. Until then, deterministic mode is the supported CI path.

The repository's Actions settings must also allow workflows to write repository contents. If organization policy prevents `GITHUB_TOKEN` from pushing the wiki or directly updating `main`, use a GitHub App or fine-grained PAT for only the commit jobs. That is a GitHub write credential, not an LLM credential.

## Security model

- **No agent in CI.** Wiki and graph extraction are deterministic scripts with no model or tool-capable agent.
- **Source-backed output.** Every changed indexed file receives nodes attributed to that file before old data is replaced.
- **Separate writes.** Model-free jobs apply patch artifacts after the build jobs finish.
- **Path boundary.** `graph-commit` rejects any patch that touches a path outside `graphify-out/`.
- **No ambient checkout credential.** Build checkouts use `persist-credentials: false`.
- **No code from PR text.** PR titles are passed through environment variables and used only as commit-message data.

## Controls and operation

- Add `skip-wiki`, `skip-graph`, or `skip-embeddings` before merging to skip that generated view.
- Run a full reconciliation from Actions with the `Wiki + Graph Sync` workflow, or with:

```bash
gh workflow run doc-agent-on-merge.yml --repo riversidefm/marketing-brain
```

- Run the wiki generator locally against a wiki clone:

```bash
python3 scripts/sync_wiki.py --repo-dir . --wiki-dir ../marketing-brain.wiki --full
```

- Preview which graph sources would be updated without calling a model:

```bash
python3 scripts/sync_graph.py --repo-dir . --dry-run
```

- Perform a richer model-assisted refresh locally when an OpenAI-compatible backend is configured:

```bash
OPENAI_API_KEY=... OPENAI_BASE_URL=... \
  python3 scripts/sync_graph.py --repo-dir . --semantic-mode model
```

When no indexed files changed, the graph job produces no patch and no graph commit. The graph commit does not trigger another sync because the workflow listens to merged pull requests and manual dispatches, not pushes.
