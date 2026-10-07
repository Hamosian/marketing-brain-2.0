#!/usr/bin/env python3
"""Minimal Markup.io API v2 client for the website page-QA flow.

    export MARKUP_API_KEY=sk_...
    python3 scripts/markup_client.py usage
    python3 scripts/markup_client.py find-markup --url <staging-url>
    python3 scripts/markup_client.py create-markup --url <staging-url> --name "<page> - QA 2026-08-23"
    python3 scripts/markup_client.py view-modes --markup-id <id>
    python3 scripts/markup_client.py create-pin --markup-id <id> \
        --page-url <staging-url> --canonical-url <prod-url> \
        --selector ".hero > :nth-child(2)" --x 0.5 --y 0.4 \
        --breakpoint desktop --message "P2 - double space in the H2"
    python3 scripts/markup_client.py list-threads --markup-id <id>
    python3 scripts/markup_client.py add-message --thread-id <id> --message "..."

Stdlib only. Two non-obvious requirements are baked in because getting them
wrong returns an opaque 500 rather than a 400 (see
.claude/skills/marketing-website-page-qa/knowledge/markup-api.md):

  * `message` must be a Quill Delta object, never a plain string.
  * `elementParents` must be present as a key, even when empty.
"""
import argparse, json, os, sys, urllib.error, urllib.request

BASE = "https://api.markup.io"
API_VERSION = "2023-02-22"
# urllib's default User-Agent is filtered by Cloudflare (error code 1010).
UA = "riverside-marketing-os/1.0"


def _key():
    k = os.environ.get("MARKUP_API_KEY", "").strip()
    if not k:
        sys.exit("MARKUP_API_KEY is not set. Never commit this key to the repo.")
    return k


def call(method, path, body=None, params=None):
    url = BASE + path
    if params:
        from urllib.parse import urlencode
        url += "?" + urlencode({k: v for k, v in params.items() if v is not None})
    req = urllib.request.Request(
        url, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": "Bearer " + _key(),
                 "Markup-API-Version": API_VERSION,
                 "Content-Type": "application/json",
                 "User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            err = json.loads(raw)["error"]
        except Exception:
            err = raw[:300]
        sys.exit(f"{method} {path} -> HTTP {e.code}: {json.dumps(err)}")


def delta(text):
    """Markup expects a Quill Delta. A trailing newline matches the UI's own shape."""
    return {"ops": [{"insert": text if text.endswith("\n") else text + "\n"}]}


def view_mode_id(markup_id, breakpoint_):
    modes = call("GET", f"/api/v2/markups/{markup_id}/view-modes")["data"]["projectViewModes"]
    for m in modes:
        if m["category"] == breakpoint_:
            return m["id"]
    sys.exit(f"no view mode for '{breakpoint_}'; have {[m['category'] for m in modes]}")


def cmd_usage(a):
    print(json.dumps(call("GET", "/api/v2/markups/usage")["data"], indent=1))


def _norm(u):
    """Compare page URLs loosely: ignore scheme, trailing slash and query string."""
    u = (u or "").split("?")[0].split("#")[0].rstrip("/").lower()
    return u.split("://", 1)[-1]


def cmd_find_markup(a):
    # GET /api/v2/markups returns at most ~99 markups, newest activity first, and reports
    # hasMore/nextCursor - but no query parameter or header we tried advances the cursor
    # (see knowledge/markup-api.md). So this only searches the most recently active markups.
    d = call("GET", "/api/v2/markups", params={"limit": 100})["data"]
    rows = d.get("data", [])
    found = [{k: m.get(k) for k in ("id", "name", "url", "createdAt")}
             for m in rows if _norm(m.get("url")) == _norm(a.url)]
    print(json.dumps(found, indent=1))
    if not found and d.get("hasMore"):
        print(f"NOTE: searched only the {len(rows)} most recently active markups; older ones are "
              "not reachable through the API. If the ticket's MarkUp column already holds an invite "
              "link, ask a person which markup it is before creating a new one.", file=sys.stderr)


def cmd_create_markup(a):
    d = call("POST", "/api/v2/markups/url",
             {"url": a.url, "name": a.name, **({"workspaceId": a.workspace_id} if a.workspace_id else {})})
    d = d.get("data", d)
    print(json.dumps({"id": d["id"], "markupUrl": d["markupUrl"], "name": d.get("name")}, indent=1))
    # markupUrl opens for Markup members and anonymous visitors; a signed-in non-member sees
    # "this markup is private" and needs a Markup invite (see knowledge/markup-api.md).


def cmd_view_modes(a):
    modes = call("GET", f"/api/v2/markups/{a.markup_id}/view-modes")["data"]["projectViewModes"]
    print(json.dumps([{k: m[k] for k in ("category", "id", "width", "height")} for m in modes], indent=1))


def cmd_create_pin(a):
    body = {
        "isImageThread": False,
        "projectId": a.markup_id,
        "url": a.page_url,
        "canonicalUrl": a.canonical_url or a.page_url,
        "viewModeId": a.view_mode_id or view_mode_id(a.markup_id, a.breakpoint),
        "offsetXPercentage": a.x, "offsetYPercentage": a.y,
        "viewportXPercentage": a.viewport_x if a.viewport_x is not None else a.x,
        "viewportYPercentage": a.viewport_y if a.viewport_y is not None else a.y,
        "elements": [{"elementPath": a.selector, "offsetXPercentage": a.x, "offsetYPercentage": a.y}],
        "elementParents": [],          # key must exist; empty is accepted
        "message": delta(a.message),   # must be a Delta, not a string
        "browserContext": {"browserName": "Chrome", "browserVersion": "151.0.0.0",
                           "os": "macOS", "osVersion": "10.15.7", "platform": "desktop",
                           "screenWidth": a.screen_width, "screenHeight": a.screen_height,
                           "viewportWidth": a.viewport_width, "viewportHeight": a.viewport_height},
    }
    d = call("POST", "/api/v2/threads", body).get("data", {})
    print(json.dumps({"threadId": d.get("id"), "number": d.get("number")}, indent=1))


def cmd_list_threads(a):
    d = call("GET", "/api/v2/threads", params={"markupId": a.markup_id, "limit": a.limit})["data"]
    out = []
    for t in d.get("threads", d.get("data", [])):
        msgs = t.get("messages") or []
        first = msgs[0] if msgs else {}
        out.append({"threadId": t.get("id"), "number": t.get("number"),
                    "resolved": t.get("resolved"),
                    "author": (first.get("user") or {}).get("name") or (t.get("user") or {}).get("name"),
                    "message": (first.get("message") if isinstance(first.get("message"), str)
                                else json.dumps(first.get("message"))or "")[:160],
                    "replies": max(0, len(msgs) - 1)})
    print(json.dumps(out, indent=1))


def cmd_add_message(a):
    d = call("POST", f"/api/v2/threads/{a.thread_id}/messages", {"content": a.message}).get("data", {})
    print(json.dumps({"messageId": d.get("id")}, indent=1))


def main():
    p = argparse.ArgumentParser(description="Markup.io API v2 client (page QA)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("usage").set_defaults(fn=cmd_usage)

    s = sub.add_parser("find-markup"); s.set_defaults(fn=cmd_find_markup)
    s.add_argument("--url", required=True, help="page URL the markup was created from")

    s = sub.add_parser("create-markup"); s.set_defaults(fn=cmd_create_markup)
    s.add_argument("--url", required=True); s.add_argument("--name", required=True)
    s.add_argument("--workspace-id")

    s = sub.add_parser("view-modes"); s.set_defaults(fn=cmd_view_modes)
    s.add_argument("--markup-id", required=True)

    s = sub.add_parser("create-pin"); s.set_defaults(fn=cmd_create_pin)
    s.add_argument("--markup-id", required=True)
    s.add_argument("--page-url", required=True)
    s.add_argument("--canonical-url")
    s.add_argument("--selector", required=True, help="CSS selector chain for the pinned element")
    s.add_argument("--x", type=float, required=True, help="0-1 fraction across the element")
    s.add_argument("--y", type=float, required=True, help="0-1 fraction down the element")
    s.add_argument("--viewport-x", type=float); s.add_argument("--viewport-y", type=float)
    s.add_argument("--breakpoint", default="desktop", choices=["desktop", "tablet", "mobile"])
    s.add_argument("--view-mode-id")
    s.add_argument("--message", required=True)
    s.add_argument("--screen-width", type=int, default=1920)
    s.add_argument("--screen-height", type=int, default=1080)
    s.add_argument("--viewport-width", type=int, default=1280)
    s.add_argument("--viewport-height", type=int, default=900)

    s = sub.add_parser("list-threads"); s.set_defaults(fn=cmd_list_threads)
    s.add_argument("--markup-id", required=True); s.add_argument("--limit", type=int, default=50)

    s = sub.add_parser("add-message"); s.set_defaults(fn=cmd_add_message)
    s.add_argument("--thread-id", required=True); s.add_argument("--message", required=True)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
