#!/usr/bin/env python3
"""Fetch Gmail attachments matching a Gmail search, save them to a folder, optionally extract PDF text.

Why this exists: the Gmail MCP connector reads bodies but cannot open attachments. Vendor lead
handover documents (Ziff Davis LHO PDFs), invoices and similar arrive only as attachments.

Auth, two modes, picked automatically:
  oauth  - a Google sign-in client (Desktop app) for an Internal Workspace app. Used when
           ~/.config/marketing-os/gmail-credentials.json exists. First run opens the browser once;
           the refresh token is kept in ~/.config/marketing-os/gmail-token.json (internal-app tokens
           do not expire). Scope is gmail.readonly. Setup steps: README.md.
  imap   - a Google app password in the macOS Keychain (service marketing-os-gmail). Only works
           where the Workspace admin allows app passwords; riverside.fm does not (checked 2026-09-19).
Then:
  python3 tools/gmail-attachments/fetch_attachments.py \
      --account nir.taranto@riverside.fm \
      --query 'from:charles.green@swzd.com has:attachment filename:pdf' \
      --out ~/Downloads/LHO --extract-text

Stdlib only, plus pypdf when --extract-text is used. Dedupes on Gmail Message-ID via manifest.json
in the output folder, so re-running only fetches what is new.
"""
import argparse, email, imaplib, json, os, re, subprocess, sys
from email.header import decode_header, make_header
from pathlib import Path

KEYCHAIN_SERVICE = "marketing-os-gmail"


def keychain_password(account: str) -> str:
    r = subprocess.run(["security", "find-generic-password", "-a", account, "-s", KEYCHAIN_SERVICE, "-w"],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        sys.exit(f"No Keychain entry for account={account} service={KEYCHAIN_SERVICE}.\n"
                 f"Run once in Terminal:  security add-generic-password -a {account} -s {KEYCHAIN_SERVICE} -w")
    return r.stdout.strip()


def safe(s: str, n: int = 120) -> str:
    s = str(make_header(decode_header(s or ""))) if s else ""
    s = re.sub(r"[\\/:*?\"<>|\r\n]+", " ", s).strip()
    return s[:n] or "untitled"


def extract_pdf_text(pdf_path: Path) -> str:
    from pypdf import PdfReader  # imported lazily so the fetch works without it
    reader = PdfReader(str(pdf_path))
    return "\n".join((p.extract_text() or "") for p in reader.pages)


CONFIG_DIR = Path(os.path.expanduser("~/.config/marketing-os"))
CREDENTIALS = CONFIG_DIR / "gmail-credentials.json"
TOKEN = CONFIG_DIR / "gmail-token.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def gmail_service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS), SCOPES)
            creds = flow.run_local_server(port=0, prompt="consent")
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        TOKEN.write_text(creds.to_json()); os.chmod(TOKEN, 0o600)
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def fetch_oauth(a, out: Path, manifest: dict) -> tuple:
    import base64
    svc = gmail_service()
    ids, page = [], None
    while True:
        resp = svc.users().messages().list(userId="me", q=a.query, maxResults=min(500, a.limit - len(ids)),
                                           pageToken=page).execute()
        ids += [m["id"] for m in resp.get("messages", [])]
        page = resp.get("nextPageToken")
        if not page or len(ids) >= a.limit:
            break
    print(f"{len(ids)} messages match: {a.query}")
    saved = skipped = 0
    for mid in ids:
        if mid in manifest:
            skipped += 1; continue
        msg = svc.users().messages().get(userId="me", id=mid, format="full").execute()
        hdr = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}
        subject = safe(hdr.get("subject", ""))
        files = []
        stack = [msg.get("payload", {})]
        while stack:
            part = stack.pop()
            stack += part.get("parts", []) or []
            fn = part.get("filename")
            att = part.get("body", {}).get("attachmentId")
            if not fn or not att:
                continue
            fn = safe(fn)
            if a.ext and not fn.lower().endswith(a.ext.lower()):
                continue
            data = svc.users().messages().attachments().get(userId="me", messageId=mid, id=att).execute()["data"]
            payload = base64.urlsafe_b64decode(data)
            target = out / fn
            i = 2
            while target.exists() and target.read_bytes() != payload:
                target = out / f"{target.stem} ({i}){target.suffix}"; i += 1
            target.write_bytes(payload)
            files.append(target.name)
            if a.extract_text and target.suffix.lower() == ".pdf":
                try:
                    target.with_suffix(".txt").write_text(extract_pdf_text(target))
                except Exception as e:
                    print(f"  text extraction failed for {target.name}: {e}")
        if files:
            saved += 1
            manifest[mid] = {"gmail_id": mid, "date": hdr.get("date", ""), "subject": subject,
                             "from": hdr.get("from", ""), "files": files}
            print(f"  saved {len(files)} file(s) from: {subject}")
    return saved, skipped


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--account", required=True, help="Gmail address (Keychain account name)")
    ap.add_argument("--query", required=True, help="Gmail search, same syntax as the Gmail search box")
    ap.add_argument("--out", required=True, help="output folder")
    ap.add_argument("--ext", default=".pdf", help="only save attachments with this extension (default .pdf; '' for all)")
    ap.add_argument("--extract-text", action="store_true", help="write a .txt next to every saved PDF")
    ap.add_argument("--mailbox", default='"[Gmail]/All Mail"')
    ap.add_argument("--limit", type=int, default=500)
    ap.add_argument("--auth", choices=["auto", "oauth", "imap"], default="auto",
                    help="auto = oauth when the client JSON exists, else imap (default)")
    a = ap.parse_args()

    out = Path(os.path.expanduser(a.out)); out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    if a.auth == "oauth" or (a.auth == "auto" and CREDENTIALS.exists()):
        if not CREDENTIALS.exists():
            sys.exit(f"OAuth mode needs {CREDENTIALS} (the Desktop-app client JSON from Google Cloud). See README.md.")
        saved, skipped = fetch_oauth(a, out, manifest)
        manifest_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
        print(f"done: {saved} new message(s) saved, {skipped} already in manifest, folder {out}")
        return 0

    pw = keychain_password(a.account)
    M = imaplib.IMAP4_SSL("imap.gmail.com")
    try:
        M.login(a.account, pw)
    except imaplib.IMAP4.error as e:
        sys.exit(f"IMAP login failed: {e}\nIf the app password is right, IMAP may be disabled for the account or "
                 f"app passwords blocked by the Workspace admin; the OAuth route in README.md is the fallback.")
    typ, _ = M.select(a.mailbox, readonly=True)
    if typ != "OK":
        sys.exit(f"could not open mailbox {a.mailbox}")
    typ, data = M.uid("SEARCH", None, "X-GM-RAW", f'"{a.query}"')
    uids = data[0].split() if typ == "OK" and data and data[0] else []
    uids = uids[-a.limit:]
    print(f"{len(uids)} messages match: {a.query}")

    saved, skipped = 0, 0
    for uid in uids:
        typ, msgdata = M.uid("FETCH", uid, "(RFC822)")
        if typ != "OK" or not msgdata or msgdata[0] is None:
            continue
        msg = email.message_from_bytes(msgdata[0][1])
        mid = (msg.get("Message-ID") or f"uid-{uid.decode()}").strip()
        if mid in manifest:
            skipped += 1
            continue
        subject = safe(msg.get("Subject"))
        date = msg.get("Date", "")
        files = []
        for part in msg.walk():
            if part.get_content_disposition() not in ("attachment", "inline"):
                continue
            fn = part.get_filename()
            if not fn:
                continue
            fn = safe(fn)
            if a.ext and not fn.lower().endswith(a.ext.lower()):
                continue
            payload = part.get_payload(decode=True)
            if not payload:
                continue
            target = out / fn
            i = 2
            while target.exists() and target.read_bytes() != payload:
                target = out / f"{target.stem} ({i}){target.suffix}"; i += 1
            target.write_bytes(payload)
            files.append(target.name)
            if a.extract_text and target.suffix.lower() == ".pdf":
                try:
                    target.with_suffix(".txt").write_text(extract_pdf_text(target))
                except Exception as e:  # keep going; the PDF itself is saved
                    print(f"  text extraction failed for {target.name}: {e}")
        if files:
            saved += 1
            manifest[mid] = {"uid": uid.decode(), "date": date, "subject": subject,
                             "from": msg.get("From", ""), "files": files}
            print(f"  saved {len(files)} file(s) from: {subject}")
    manifest_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
    M.logout()
    print(f"done: {saved} new message(s) saved, {skipped} already in manifest, folder {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
