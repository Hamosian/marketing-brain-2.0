#!/usr/bin/env python3
"""Check publishable files without logging private text. Does not scan Git history."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = "config/privacy-fingerprints.json"
PRIVATE_ROOTS = {"local", "reports", "exports", "outputs", "working", "graphify-out"}
REPORT_SUFFIXES = {".docx", ".pptx", ".xlsx", ".pdf", ".zip", ".gz"}
PATTERNS = {
    "private workspace document": re.compile(r"https?://docs\.google\.com/(?:document|spreadsheets|presentation)/d/[A-Za-z0-9_-]{15,}"),
    "private chat permalink": re.compile(r"https?://[^/\s]+\.slack\.com/archives/[A-Z0-9]+/p\d+"),
    "cloud access key": re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
    "GitHub token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{30,})\b"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{15,}\b"),
    "API key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}\b"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    "literal credential": re.compile(r"(?i)\b(?:api_key|api_secret|access_token|auth_token|password)\s*[:=]\s*[\"'][A-Za-z0-9+/=_-]{16,}[\"']"),
}


def tokens(text):
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.findall(r"[^\W_]+", plain)


def fingerprint(text):
    return hashlib.sha256(" ".join(tokens(text)).encode()).hexdigest()


def findings(path, content, fingerprints):
    """Return only rule names; never return matched names, account IDs, or secrets."""
    relative = Path(path)
    issues = []
    if relative.parts[0] in PRIVATE_ROOTS or path == "config/company.local.json":
        issues.append("private runtime path")
    if relative.name == ".env" or relative.name.startswith(".env.") and relative.name != ".env.example":
        issues.append("environment credentials file")
    if relative.suffix.lower() in REPORT_SUFFIXES:
        issues.append("report or archive artifact")
    if len(relative.parts) > 3 and relative.parts[:2] in {(".claude", "skills"), (".agents", "skills")}:
        if relative.parts[3] in {"data", "drafts"} or relative.name.startswith("tracking"):
            issues.append("private skill runtime state")
    try:
        text = content.decode("utf-8")
    except UnicodeError:
        issues.append("unreviewed binary content")
        return issues
    for label, pattern in PATTERNS.items():
        if pattern.search(text):
            issues.append(label)
    words = tokens(path + "\n" + text)
    for size in range(1, 6):
        if any(hashlib.sha256(" ".join(words[i:i + size]).encode()).hexdigest() in fingerprints
               for i in range(len(words) - size + 1)):
            issues.append("former-company identifier fingerprint")
            break
    return issues


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)


def scan(root=ROOT, staged=False):
    # The staged mode checks index blobs, including the index copy of the policy.
    raw_policy = git(root, "show", ":" + POLICY) if staged else (root / POLICY).read_bytes()
    policy = json.loads(raw_policy)
    fingerprints = set(policy["sha256"])
    if not fingerprints or any(not re.fullmatch(r"[a-f0-9]{64}", x) for x in fingerprints):
        raise ValueError("privacy policy is empty or malformed")
    args = ["ls-files", "-z", "--cached"]
    if not staged:
        args += ["--others", "--exclude-standard"]
    paths = sorted(set(git(root, *args).decode().rstrip("\0").split("\0")))
    failures = []
    count = 0
    for path in paths:
        if not path:
            continue
        disk = root / path
        if staged:
            mode = git(root, "ls-files", "-s", "--", path).split(b" ", 1)[0]
            if mode != b"100644" and mode != b"100755":
                failures.append((path, ["unsupported index entry"]))
                continue
            content = git(root, "show", ":" + path)
        else:
            if disk.is_symlink():
                failures.append((path, ["symlink not allowed in template"]))
                continue
            if not disk.exists():
                continue  # unstaged deletion
            content = disk.read_bytes()
        count += 1
        issues = findings(path, content, fingerprints)
        if issues:
            failures.append((path, issues))
    return count, failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="check index blobs, not working files")
    args = parser.parse_args()
    try:
        count, failures = scan(staged=args.staged)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError):
        print("Privacy check could not read the repository or policy; refusing to pass.", file=sys.stderr)
        return 2
    for path, rules in failures:
        print(f"{path}: {', '.join(rules)}")
    print(f"Privacy check: {count} files, {len(failures)} failing files.")
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
