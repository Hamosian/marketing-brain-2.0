#!/usr/bin/env python3
"""Find and download a podcast episode's MP3 from an open RSS feed.

Usage:
  fetch_from_feed.py <feed_url> <title_fragment> <out_path.mp3>
  fetch_from_feed.py <feed_url> --list          # list recent episode titles

The feed_url can be an RSS URL or an "id<digits>" Apple Podcasts id (it will be
resolved to the feed via the free iTunes Lookup API). Matching is case-insensitive
substring, then a loose token-overlap fallback. Prints the matched title, the MP3
URL, and the episode duration, and downloads the MP3 (undRM'd) to out_path.
"""
import re
import sys
import json
import urllib.request
import xml.etree.ElementTree as ET


def http_get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 podcast-transcript"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read() if binary else r.read().decode("utf-8", "replace")


def resolve_feed(feed_or_id):
    m = re.fullmatch(r"id?(\d{6,})", feed_or_id.strip())
    if m:
        data = json.loads(http_get(f"https://itunes.apple.com/lookup?id={m.group(1)}&entity=podcast"))
        return data["results"][0]["feedUrl"]
    return feed_or_id


def episodes(feed_url):
    root = ET.fromstring(http_get(feed_url))
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        enc = item.find("enclosure")
        url = enc.get("url") if enc is not None else None
        dur = item.findtext("{http://www.itunes.com/dtds/podcast-1.0.dtd}duration") or "?"
        yield title, url, dur


def best_match(items, fragment):
    frag = fragment.lower().strip()
    for t, u, d in items:
        if frag in t.lower():
            return t, u, d
    # token-overlap fallback
    fset = set(re.findall(r"\w+", frag))
    best, score = None, 0
    for t, u, d in items:
        tset = set(re.findall(r"\w+", t.lower()))
        s = len(fset & tset)
        if s > score:
            best, score = (t, u, d), s
    return best if score >= max(2, len(fset) // 3) else None


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    feed = resolve_feed(sys.argv[1])
    items = list(episodes(feed))

    if sys.argv[2] == "--list":
        print(f"Feed: {feed}\n{len(items)} episodes (most recent first):")
        for t, _, d in items[:25]:
            print(f"  [{d}] {t[:80]}")
        return

    out = sys.argv[3] if len(sys.argv) > 3 else "episode.mp3"
    match = best_match(items, sys.argv[2])
    if not match:
        print("NO MATCH. Recent titles:")
        for t, _, _ in items[:15]:
            print("  -", t[:80])
        sys.exit(1)

    title, url, dur = match
    if not url:
        print(f"Matched '{title}' but it has no MP3 enclosure.")
        sys.exit(1)
    print(f"MATCH: {title}\nMP3:   {url}\nDUR:   {dur}\nsaving -> {out}")
    urllib.request.urlretrieve(url, out)
    print("downloaded", out)


if __name__ == "__main__":
    main()
