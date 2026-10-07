#!/usr/bin/env python3
"""Deterministic duplicate-candidate generator for the /ticket-hygiene sweep.

Reads a JSON dump of monday items and emits the shortlist of pairs worth a model's
judgement. The point is to keep the expensive part small: the model never sees the raw
cross-product, only pairs that a cheap, reproducible signal already flagged.

Two signal families:

  url   two items carry the same Figma / brief / staging / production / HubSpot link.
        Near-conclusive on its own, so these are always emitted regardless of text score.
  text  TF-IDF cosine over `name + description` clears the threshold. Boosted when the
        two items share a requester within a short window, since the same person filing
        the same thing twice is the common real-world case.

Stdlib only, no dependencies - same constraint as scripts/graph_explorer.py.

Usage:
    python3 scripts/ticket_dedupe.py items.json
    python3 scripts/ticket_dedupe.py items.json --threshold 0.5 --max-pairs 40
    python3 scripts/ticket_dedupe.py items.json --pretty

Input: a JSON array of objects. Only `id` and `name` are required.

    [
      {
        "id": "123456",
        "board": "mops",
        "name": "fix pricing page hero copy",
        "description": "...",
        "requester": "Erika Varangouli",
        "created_at": "2026-08-01",
        "urls": ["https://figma.com/file/abc"]
      }
    ]

Output: a JSON array of candidate pairs, highest score first.

    [
      {
        "a": {"id": "1", "board": "mops", "name": "..."},
        "b": {"id": "2", "board": "web", "name": "..."},
        "score": 0.71,
        "reasons": ["text", "same-requester"],
        "shared_urls": []
      }
    ]
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from datetime import date, datetime

# Generic English stopwords plus the verbs that show up in nearly every ticket title on
# these boards. Leaving "page", "form", "report" and friends IN is deliberate - they are
# the domain nouns that actually distinguish one ticket from another.
STOPWORDS = frozenset("""
a an and are as at be been by for from has have how in into is it its of on onto or that
the their then there these this to was were what when where which who will with
add added adding also can could do does done get make making need needs new please
should some take use used using want we
""".split())

TOKEN_RE = re.compile(r"[a-z0-9]+")

# A token appearing in more than this fraction of items carries no signal; skipping it
# in the inverted index is what keeps pair generation near-linear on a 900-item board.
MAX_DOCUMENT_FREQUENCY_RATIO = 0.25

SAME_REQUESTER_WINDOW_DAYS = 14
SAME_REQUESTER_BOOST = 0.10


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens, stopwords and 1-character noise removed."""
    return [
        token
        for token in TOKEN_RE.findall(text.lower())
        if len(token) > 1 and token not in STOPWORDS
    ]


def normalize_url(raw: str) -> str:
    """Reduce a URL to the part that identifies the resource.

    Scheme, `www.`, query string, fragment and trailing slash all vary between two people
    pasting the same link, so none of them may participate in the comparison. The path is
    kept: two Figma links to the same file but different nodes should still collide, and a
    human can downgrade that to `related`.
    """
    url = raw.strip().lower()
    url = re.sub(r"^https?://", "", url)
    url = re.sub(r"^www\.", "", url)
    url = url.split("#", 1)[0].split("?", 1)[0]
    return url.rstrip("/")


def parse_date(value) -> date | None:
    if not value or not isinstance(value, str):
        return None
    text = value.strip().replace("Z", "+00:00")
    for candidate in (text, text[:10]):
        try:
            return datetime.fromisoformat(candidate).date()
        except ValueError:
            continue
    return None


def item_text(item: dict) -> str:
    return f"{item.get('name', '')} {item.get('description', '') or ''}"


def build_vectors(items: list[dict]) -> tuple[list[dict[str, float]], dict[str, int]]:
    """L2-normalized TF-IDF vectors, plus the document frequency table."""
    token_lists = [tokenize(item_text(item)) for item in items]

    document_frequency: dict[str, int] = defaultdict(int)
    for tokens in token_lists:
        for token in set(tokens):
            document_frequency[token] += 1

    total = len(items)
    vectors: list[dict[str, float]] = []
    for tokens in token_lists:
        term_frequency: dict[str, int] = defaultdict(int)
        for token in tokens:
            term_frequency[token] += 1

        vector: dict[str, float] = {}
        for token, count in term_frequency.items():
            idf = math.log((total + 1) / (document_frequency[token] + 1)) + 1.0
            vector[token] = (1.0 + math.log(count)) * idf

        norm = math.sqrt(sum(weight * weight for weight in vector.values()))
        if norm:
            vector = {token: weight / norm for token, weight in vector.items()}
        vectors.append(vector)

    return vectors, document_frequency


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    """Dot product of two already-normalized sparse vectors."""
    if len(b) < len(a):
        a, b = b, a
    return sum(weight * b.get(token, 0.0) for token, weight in a.items())


def url_index(items: list[dict]) -> dict[str, list[int]]:
    index: dict[str, list[int]] = defaultdict(list)
    for position, item in enumerate(items):
        raw_urls = item.get("urls") or []
        if isinstance(raw_urls, str):
            raw_urls = [raw_urls]
        for raw in raw_urls:
            if not raw:
                continue
            normalized = normalize_url(str(raw))
            if normalized and position not in index[normalized]:
                index[normalized].append(position)
    return index


def candidate_positions(
    items: list[dict],
    vectors: list[dict[str, float]],
    document_frequency: dict[str, int],
) -> set[tuple[int, int]]:
    """Pairs sharing at least one reasonably rare token. Cheap pre-filter for the cosine."""
    cutoff = max(2, int(len(items) * MAX_DOCUMENT_FREQUENCY_RATIO))
    postings: dict[str, list[int]] = defaultdict(list)
    for position, vector in enumerate(vectors):
        for token in vector:
            if document_frequency[token] <= cutoff:
                postings[token].append(position)

    pairs: set[tuple[int, int]] = set()
    for positions in postings.values():
        # A token shared by a huge number of items is not the discriminator we hoped for.
        if len(positions) > 40:
            continue
        for i, left in enumerate(positions):
            for right in positions[i + 1:]:
                pairs.add((left, right) if left < right else (right, left))
    return pairs


def summarize(item: dict) -> dict:
    return {
        "id": item.get("id"),
        "board": item.get("board"),
        "name": item.get("name"),
    }


def find_candidates(items: list[dict], threshold: float, max_pairs: int) -> list[dict]:
    if len(items) < 2:
        return []

    vectors, document_frequency = build_vectors(items)
    urls = url_index(items)

    shared_by_pair: dict[tuple[int, int], list[str]] = defaultdict(list)
    for normalized, positions in urls.items():
        if len(positions) < 2:
            continue
        for i, left in enumerate(positions):
            for right in positions[i + 1:]:
                key = (left, right) if left < right else (right, left)
                shared_by_pair[key].append(normalized)

    pairs = candidate_positions(items, vectors, document_frequency)
    pairs.update(shared_by_pair)

    results = []
    for left, right in pairs:
        a, b = items[left], items[right]
        score = cosine(vectors[left], vectors[right])
        reasons = []

        shared_urls = sorted(shared_by_pair.get((left, right), []))
        if shared_urls:
            reasons.append("url")

        requester_a = (a.get("requester") or "").strip().lower()
        requester_b = (b.get("requester") or "").strip().lower()
        if requester_a and requester_a == requester_b:
            date_a, date_b = parse_date(a.get("created_at")), parse_date(b.get("created_at"))
            within_window = (
                date_a is None
                or date_b is None
                or abs((date_a - date_b).days) <= SAME_REQUESTER_WINDOW_DAYS
            )
            if within_window:
                score += SAME_REQUESTER_BOOST
                reasons.append("same-requester")

        if score >= threshold:
            reasons.insert(0, "text")
        elif not shared_urls:
            continue

        results.append(
            {
                "a": summarize(a),
                "b": summarize(b),
                "score": round(min(score, 1.0), 3),
                "reasons": reasons,
                "shared_urls": shared_urls,
            }
        )

    # URL matches outrank text matches at equal score - they are the stronger evidence.
    results.sort(key=lambda pair: (("url" in pair["reasons"]), pair["score"]), reverse=True)
    return results[:max_pairs]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit duplicate-candidate ticket pairs for the /ticket-hygiene sweep."
    )
    parser.add_argument("items", help="path to a JSON array of items ('-' for stdin)")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.45,
        help="TF-IDF cosine above which a text pair is a candidate (default: 0.45)",
    )
    parser.add_argument(
        "--max-pairs",
        type=int,
        default=60,
        help="cap on emitted pairs, highest score first (default: 60)",
    )
    parser.add_argument("--pretty", action="store_true", help="indent the JSON output")
    args = parser.parse_args()

    try:
        raw = sys.stdin.read() if args.items == "-" else open(args.items, encoding="utf-8").read()
        items = json.loads(raw)
    except (OSError, json.JSONDecodeError) as error:
        print(f"error: could not read items: {error}", file=sys.stderr)
        return 1

    if not isinstance(items, list):
        print("error: input must be a JSON array of item objects", file=sys.stderr)
        return 1

    usable = [item for item in items if isinstance(item, dict) and item.get("name")]
    skipped = len(items) - len(usable)
    if skipped:
        print(f"note: skipped {skipped} item(s) with no name", file=sys.stderr)

    candidates = find_candidates(usable, args.threshold, args.max_pairs)
    print(json.dumps(candidates, indent=2 if args.pretty else None, ensure_ascii=False))
    print(
        f"note: {len(candidates)} candidate pair(s) from {len(usable)} item(s)",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
