#!/usr/bin/env python3
"""Query graphify-out/embeddings.json for the chunks most similar to a question.

    python3 scripts/semantic_search.py "how does BD attribution work"
    python3 scripts/semantic_search.py --top-k 10 "webflow publish queue"

Works against whichever mode built the index (see sync_embeddings.py):
tfidf mode needs no credential; model mode re-embeds the query via the same
OpenAI-compatible endpoint used to build the index, so OPENAI_API_KEY (and
OPENAI_BASE_URL, if set at build time) must still be configured.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

from sync_embeddings import embed_model, tokenize


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--embeddings", type=Path, default=Path("graphify-out/embeddings.json"))
    parser.add_argument("--top-k", type=int, default=5)
    return parser.parse_args()


def cosine_sparse(query: dict[str, float], vector: dict[str, float]) -> float:
    shared = set(query) & set(vector)
    return sum(query[t] * vector[t] for t in shared)


def cosine_dense(query: list[float], vector: list[float]) -> float:
    dot = sum(a * b for a, b in zip(query, vector, strict=True))
    norm_q = math.sqrt(sum(a * a for a in query)) or 1.0
    norm_v = math.sqrt(sum(b * b for b in vector)) or 1.0
    return dot / (norm_q * norm_v)


def embed_query_tfidf(query: str, idf: dict[str, float]) -> dict[str, float]:
    tokens = tokenize(query)
    tf: dict[str, int] = {}
    for term in tokens:
        tf[term] = tf.get(term, 0) + 1
    total = len(tokens) or 1
    weights = {
        term: (count / total) * idf[term]
        for term, count in tf.items()
        if term in idf
    }
    norm = math.sqrt(sum(w * w for w in weights.values())) or 1.0
    return {term: w / norm for term, w in weights.items()}


def main() -> None:
    args = parse_args()
    index = json.loads(args.embeddings.read_text(encoding="utf-8"))

    mode = index["mode"]
    chunks = index["chunks"]

    if mode == "model":
        if not os.environ.get("OPENAI_API_KEY"):
            raise SystemExit(
                "This index was built in model mode; set OPENAI_API_KEY to query it, "
                "or rebuild with --mode tfidf for a credential-free index."
            )
        query_vector = embed_model([args.query], index["model"])[0]
        scored = [
            (cosine_dense(query_vector, chunk["vector"]), chunk) for chunk in chunks
        ]
    else:
        query_vector = embed_query_tfidf(args.query, index["idf"])
        scored = [
            (cosine_sparse(query_vector, chunk["vector"]), chunk) for chunk in chunks
        ]

    scored.sort(key=lambda pair: pair[0], reverse=True)

    for score, chunk in scored[: args.top_k]:
        print(f"{score:.3f}  {chunk['file']} - {chunk['heading']}")
        print(f"       {chunk['text_preview'].replace(chr(10), ' ')[:160]}")


if __name__ == "__main__":
    main()
