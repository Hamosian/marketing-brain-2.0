#!/usr/bin/env python3
"""Build graphify-out/embeddings.json - a semantic search index over the brain's Markdown.

Two modes, matching the deterministic/model-assisted split already used for the
knowledge graph (see docs/wiki-sync-automation.md):

  tfidf   Deterministic. No credential required. Sparse TF-IDF vectors, cosine
          similarity via dict dot-product. Always available, used by CI.
  model   Model-assisted. Calls an OpenAI-compatible /embeddings endpoint
          (OPENAI_API_KEY + optional OPENAI_BASE_URL) for dense embeddings that
          capture paraphrase/synonym similarity, not just shared terms. Run
          locally when a credential is configured.

`--mode auto` (the default) uses model mode if OPENAI_API_KEY is set, else
falls back to tfidf. Every run is a full rebuild, mirroring the wiki
generator's "always full, but stable so only real changes appear in the
patch" approach - the corpus is small enough that incremental re-indexing
would add complexity for no real savings.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "than", "so", "of",
    "to", "in", "on", "at", "for", "with", "by", "from", "as", "is", "are",
    "was", "were", "be", "been", "being", "it", "its", "this", "that", "these",
    "those", "we", "you", "your", "our", "their", "they", "he", "she", "his",
    "her", "them", "not", "no", "do", "does", "did", "can", "will", "would",
    "should", "could", "have", "has", "had", "into", "over", "out", "up",
    "down", "about", "when", "what", "which", "who", "how", "all", "any",
    "each", "more", "most", "other", "some", "such", "only", "own", "same",
    "just", "also",
}

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9\-']{1,}")
HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)$")

INDEXED_GLOBS = [
    "CLAUDE.md",
    "references/**/*.md",
    "systems/**/*.md",
    "docs/**/*.md",
    ".claude/skills/**/*.md",
    ".claude/agents/**/*.md",
]

EXCLUDE_DIR_PARTS = {"graphify-out", "starter", "node_modules", ".git"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-dir", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("graphify-out/embeddings.json"))
    parser.add_argument(
        "--mode",
        choices=("auto", "model", "tfidf"),
        default=os.environ.get("EMBEDDINGS_MODE", "auto"),
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


def discover_files(repo: Path) -> list[Path]:
    seen: set[Path] = set()
    files: list[Path] = []
    for pattern in INDEXED_GLOBS:
        for path in sorted(repo.glob(pattern)):
            if not path.is_file():
                continue
            rel = path.relative_to(repo)
            if EXCLUDE_DIR_PARTS & set(rel.parts):
                continue
            if path in seen:
                continue
            seen.add(path)
            files.append(path)
    return files


def chunk_file(repo: Path, path: Path) -> list[dict]:
    rel = str(path.relative_to(repo))
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    # A human-readable label from the path (e.g. "systems owned hubspot") so a
    # chunk stays findable by its file/system name even when the section body
    # never repeats it - a query for "preop" should still reach
    # preop-data-intelligence.md.
    stem = rel[:-3] if rel.endswith(".md") else rel
    file_label = re.sub(r"[/_\-]+", " ", stem).strip()

    chunks: list[dict] = []
    heading = "(intro)"
    anchor = ""
    doc_title = ""
    buffer: list[str] = []

    def flush() -> None:
        body = "\n".join(buffer).strip()
        if not body:
            return
        # Prepend a deterministic "situating context" breadcrumb (path label >
        # document title > section heading) to what gets indexed, so parent
        # context is part of the match signal rather than the raw section body
        # alone. This is the credential-free analogue of contextual-retrieval
        # chunking: no LLM call, so it is safe to run in CI. `index_text` is used
        # only to build the vector and is dropped before the index is written -
        # the stored schema (text_preview, vector, ...) is unchanged.
        parts: list[str] = []
        for part in (file_label, doc_title, heading):
            if part and part != "(intro)" and part not in parts:
                parts.append(part)
        context = " > ".join(parts)
        index_text = f"{context}\n{body}" if context else body
        chunks.append(
            {
                "file": rel,
                "heading": heading,
                "anchor": anchor,
                "text": body,
                "index_text": index_text,
            }
        )

    for line in lines:
        match = HEADING_RE.match(line)
        if match:
            flush()
            buffer = []
            level = len(match.group(1))
            heading = match.group(2).strip()
            anchor = re.sub(r"[^a-z0-9\- ]", "", heading.lower()).strip().replace(" ", "-")
            if level == 1 and not doc_title:
                doc_title = heading
        else:
            buffer.append(line)
    flush()
    return chunks


def tokenize(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS]


def build_tfidf(chunks: list[dict]) -> tuple[list[dict], dict[str, float]]:
    token_lists = [tokenize(c.get("index_text", c["text"])) for c in chunks]
    doc_count = len(chunks)

    df: dict[str, int] = {}
    for tokens in token_lists:
        for term in set(tokens):
            df[term] = df.get(term, 0) + 1

    idf = {term: math.log((1 + doc_count) / (1 + freq)) + 1.0 for term, freq in df.items()}

    vectors = []
    for tokens in token_lists:
        if not tokens:
            vectors.append({})
            continue
        tf: dict[str, int] = {}
        for term in tokens:
            tf[term] = tf.get(term, 0) + 1
        total = len(tokens)
        weights = {term: (count / total) * idf[term] for term, count in tf.items()}
        norm = math.sqrt(sum(w * w for w in weights.values())) or 1.0
        vectors.append({term: round(w / norm, 5) for term, w in weights.items()})

    return vectors, {term: round(value, 5) for term, value in idf.items()}


def embed_model(texts: list[str], model: str) -> list[list[float]]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY must be set to use --mode model.")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")

    vectors: list[list[float]] = []
    batch_size = 64
    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]
        payload = json.dumps({"model": model, "input": batch}).encode("utf-8")
        req = urllib.request.Request(
            f"{base_url}/embeddings",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise SystemExit(f"Embedding request failed ({exc.code}): {detail}") from exc
        vectors.extend(item["embedding"] for item in body["data"])
    return vectors


def main() -> None:
    args = parse_args()
    repo = args.repo_dir.resolve()

    files = discover_files(repo)
    chunks: list[dict] = []
    for path in files:
        chunks.extend(chunk_file(repo, path))

    mode = args.mode
    if mode == "auto":
        mode = "model" if os.environ.get("OPENAI_API_KEY") else "tfidf"

    idf: dict[str, float] = {}
    if mode == "model":
        vectors = embed_model([c.get("index_text", c["text"]) for c in chunks], args.model)
        for chunk, vector in zip(chunks, vectors, strict=True):
            chunk["vector"] = vector
    else:
        sparse_vectors, idf = build_tfidf(chunks)
        for chunk, vector in zip(chunks, sparse_vectors, strict=True):
            chunk["vector"] = vector

    for chunk in chunks:
        chunk["id"] = f"{chunk['file']}#{chunk['anchor']}" if chunk["anchor"] else chunk["file"]
        chunk["text_preview"] = chunk["text"][:280]
        del chunk["text"]
        chunk.pop("index_text", None)

    output = {
        "mode": mode,
        "model": args.model if mode == "model" else None,
        "built_at_commit": git(repo, "rev-parse", "HEAD"),
        "files_indexed": len(files),
        "chunk_count": len(chunks),
        "idf": idf,
        "chunks": chunks,
    }

    print(f"Indexed {len(files)} files into {len(chunks)} chunks (mode={mode}).")

    if args.dry_run:
        return

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
