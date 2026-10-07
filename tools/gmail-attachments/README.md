# Gmail attachments fetcher

Pulls attachments matching a Gmail search to a local folder, with optional PDF-to-text. Exists because the Gmail connector reads message bodies but cannot open attachments, and vendor handover documents, invoices and similar arrive only as attachments.

## One-time setup: Google sign-in client (about five minutes, done by the mailbox owner)

riverside.fm blocks app passwords (checked 2026-09-19), so the durable route is a Google Cloud OAuth client for an **Internal** app. Internal-app refresh tokens do not expire, so this is set up once.

1. https://console.cloud.google.com/projectcreate : name it `Marketing OS`, Create. (If this page says you cannot create projects, stop; the admin has to create it or grant the role.)
2. https://console.cloud.google.com/apis/library/gmail.googleapis.com : make sure the `Marketing OS` project is selected at the top, click Enable.
3. https://console.cloud.google.com/auth/overview : Get started. App name `Marketing OS`, your email as support email, Audience **Internal**, your email as contact, Create.
4. https://console.cloud.google.com/auth/clients : Create client, type **Desktop app**, name `Marketing OS`, Create, then **Download JSON**.
5. Move the downloaded file to `~/.config/marketing-os/gmail-credentials.json`:

```bash
mkdir -p ~/.config/marketing-os && mv ~/Downloads/client_secret_*.json ~/.config/marketing-os/gmail-credentials.json
```

6. The first run opens a browser tab asking you to allow `Marketing OS` read-only access to Gmail. Click Allow. The token is saved to `~/.config/marketing-os/gmail-token.json` (mode 600) and reused from then on.

The client JSON identifies the app, it is not a mailbox credential; the token file is what grants access, and it lives only on this Mac. Revoke at https://myaccount.google.com/permissions if the Mac changes hands.

**IMAP + app password** (`--auth imap`, Keychain service `marketing-os-gmail`) remains in the script for accounts where the admin allows app passwords.

## Use

```bash
python3 tools/gmail-attachments/fetch_attachments.py \
  --account nir.taranto@riverside.fm \
  --query 'from:charles.green@swzd.com has:attachment filename:pdf' \
  --out ~/Downloads/LHO --extract-text
```

- `--query` takes exactly what you would type in the Gmail search box.
- `--out` gets the files plus `manifest.json` (Message-ID, date, subject, saved files). Re-runs fetch only new messages.
- `--extract-text` writes a `.txt` beside every PDF (needs `pypdf`, present on Nir's Mac).
- `--ext ''` saves every attachment type, not just PDFs.

## Who calls it

- `vendor-meeting-quality`: an LHO that arrives attachment-only is fetched with this tool and scored from the `.txt`, instead of being flagged `brief missing`.
- `invoice-inbox-to-monday` can use it for invoice PDFs the connector cannot read.

Safety: read-only IMAP (`readonly=True`), nothing is moved, labelled or deleted. The app password grants full mailbox access, so it lives only in the Keychain of this Mac; revoke it at the same Google page if the Mac changes hands.
