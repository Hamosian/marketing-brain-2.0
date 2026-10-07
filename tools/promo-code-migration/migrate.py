"""Move a coupon's active promotion codes to another coupon, one code at a time.

Uses the Backoffice Marketing Coupons API (systems/reference/backoffice-coupons-api.md).
Every command that calls the API needs --approved-by: only Jonathan Galili or Hanan Amos
may request or approve use of this API.

  python3 migrate.py plan --from 30days --to growmonthoffsep --approved-by jonathan
  python3 migrate.py dry-run --from 30days --to growmonthoffsep
  python3 migrate.py run --from 30days --to growmonthoffsep --only CANARYCODE --execute --approved-by jonathan
  python3 migrate.py run --from 30days --to growmonthoffsep --execute --approved-by jonathan
  python3 migrate.py rollback --from 30days --to growmonthoffsep --only CODE --execute --approved-by jonathan
  python3 migrate.py reconcile --from 30days --to growmonthoffsep --approved-by jonathan

`plan` reads the live source list, skips inactive codes, codes with non-default restrictions
and codes whose text is already active on the target, and orders the rest canary first, then
fewest redemptions first. Writes happen only with --execute. Every call is appended to
ledger.jsonl and per-code progress to state.json in the run directory, so a crash or Ctrl-C
resumes where it stopped. Ctrl-C finishes the current code's pair before stopping, so no
code is left switched off.
"""
import argparse, datetime, json, os, re, signal, subprocess, sys, time, uuid

BASE = "https://api.riverside.fm/backoffice/api/coupons"
KEY_FILE = os.path.expanduser("~/.config/marketing-os/backoffice.key")
APPROVERS = {"jonathan": "Jonathan Galili", "hanan": "Hanan Amos",
             "yehonatan.galili@riverside.fm": "Jonathan Galili",
             "yehonatan.galili@riverside.com": "Jonathan Galili",
             "hanan.amos@riverside.fm": "Hanan Amos", "hanan.amos@riverside.com": "Hanan Amos"}
WRITE_GAP = 6.7          # seconds between writes: under the 10-a-minute key-wide write budget
MAX_RETRIES = 4
DEFAULT_RESTRICTIONS = {"firstTimeTransaction": False, "minimumAmount": None,
                        "minimumAmountCurrency": None, "currencyOptions": []}

SRC = DST = PLAN = STATE = LEDGER = APPROVER = None
_last_write = 0.0
_stop = False


def configure(src, dst, run_dir, approver=None):
    global SRC, DST, PLAN, STATE, LEDGER, APPROVER
    SRC, DST, APPROVER = src, dst, approver
    os.makedirs(run_dir, exist_ok=True)
    PLAN, STATE, LEDGER = (os.path.join(run_dir, f) for f in ("plan.json", "state.json", "ledger.jsonl"))


def now():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def log(event):
    event = {"ts": now(), "approvedBy": APPROVER, **event}
    with open(LEDGER, "a") as f:
        f.write(json.dumps(event) + "\n")


def load(path, default):
    return json.load(open(path)) if os.path.exists(path) else default


def save(path, data):
    tmp = path + ".tmp"
    json.dump(data, open(tmp, "w"), indent=2)
    os.replace(tmp, path)


def call(method, path, body=None):
    """curl, not urllib: Cloudflare on api.riverside.fm bans Python-urllib's signature (1010).
    The key goes in on stdin (-H @-) so it never shows in the process list or the ledger."""
    if not APPROVER:
        sys.exit("refusing to call the API without --approved-by (Jonathan Galili or Hanan Amos)")
    key = (os.environ.get("MARKETING_BACKOFFICE_API_KEY") or open(KEY_FILE).read()).strip()
    args = ["curl", "-s", "--max-time", "45", "-X", method, "-w", "\n%{http_code}",
            "-H", "@-", "-H", "Accept: application/json"]
    if body is not None:
        args += ["-H", "Content-Type: application/json", "--data-binary", json.dumps(body)]
    p = subprocess.run(args + [BASE + path], input=f"X-Api-Key: {key}\n",
                       capture_output=True, text=True, start_new_session=True)
    text, _, code = p.stdout.rpartition("\n")
    code = int(code) if code.isdigit() else 0
    try:
        data = json.loads(text) if text else {}
    except ValueError:
        data = {"raw": text[:500]}
    return code, data


def list_codes(coupon):
    code, data = call("GET", f"/promotion-codes?couponId={coupon}")
    if code != 200 or not data.get("ok"):
        sys.exit(f"list {coupon} failed: HTTP {code} {data}")
    return data


def write(path, body, label):
    """One write with pacing, 429 back-off and retry on transient failures.
    Deactivate/activate are idempotent; create is replay-safe on the same requestId + body."""
    global _last_write
    for attempt in range(1, MAX_RETRIES + 1):
        wait = WRITE_GAP - (time.time() - _last_write)
        if wait > 0:
            time.sleep(wait)
        _last_write = time.time()
        code, data = call("POST", path, body)
        log({"label": label, "path": path, "body": body, "http": code, "attempt": attempt,
             "response": data})
        msg = json.dumps(data)
        if code == 429 or (code == 400 and "rate limit" in msg.lower()):
            secs = int((re.findall(r"(\d+)\s*second", msg) or [60])[0]) + 2
            print(f"      rate limited, waiting {secs}s")
            time.sleep(secs)
            continue
        if code == 0 or code >= 500:
            print(f"      HTTP {code}, retrying ({attempt}/{MAX_RETRIES})")
            time.sleep(5 * attempt)
            continue
        return code, data
    return code, data


def row_ok(data, *, pid=None, code=None, active=None, coupon=None):
    pc = data.get("promotionCode") or {}
    problems = []
    if not data.get("ok"):
        problems.append("ok!=true")
    if pid and pc.get("id") != pid:
        problems.append(f"id={pc.get('id')}")
    if code and pc.get("code") != code:
        problems.append(f"code={pc.get('code')}")
    if active is not None and pc.get("active") is not active:
        problems.append(f"active={pc.get('active')}")
    if coupon and (pc.get("coupon") or {}).get("id") != coupon:
        problems.append(f"coupon={(pc.get('coupon') or {}).get('id')}")
    if coupon and {k: v for k, v in (pc.get("restrictions") or {}).items()
                   if k != "__typename"} != DEFAULT_RESTRICTIONS:
        problems.append(f"restrictions={pc.get('restrictions')}")
    return problems


# ---------------------------------------------------------------- plan / dry-run

def cmd_plan(canary=None):
    live = list_codes(SRC)
    if live.get("truncated"):
        sys.exit(f"{SRC} list is truncated: plan would be incomplete")
    dst = list_codes(DST)
    taken = {p["code"].lower() for p in dst["promotionCodes"] if p["active"]}
    items, skipped = [], []
    for p in live["promotionCodes"]:
        r = {k: v for k, v in p["restrictions"].items() if k != "__typename"}
        if not p["active"]:
            skipped.append({"code": p["code"], "reason": f"already inactive on {SRC}"})
        elif r != DEFAULT_RESTRICTIONS:
            # The create call can carry restrictions, but none were needed when this was built,
            # so these stay put for a person to review rather than being copied untested.
            skipped.append({"code": p["code"], "reason": f"non-default restrictions {r}: needs review"})
        elif p["code"].lower() in taken:
            skipped.append({"code": p["code"], "reason": f"text already active on {DST}"})
        else:
            items.append({"code": p["code"], "oldId": p["id"], "timesRedeemed": p["timesRedeemed"],
                          "requestId": str(uuid.uuid4())})
    # Canary first, then lowest traffic first so any surprise lands on quiet codes.
    items.sort(key=lambda i: (i["timesRedeemed"], i["code"].lower()))
    if canary:
        items.sort(key=lambda i: i["code"].lower() != canary.lower())
    save(PLAN, {"built": now(), "src": SRC, "dst": DST, "items": items, "skipped": skipped})
    print(f"{PLAN}: {len(items)} to move, {len(skipped)} skipped")
    for s in skipped:
        print(f"   skip {s['code']:18} {s['reason']}")


def bodies(item):
    return ({"promotionCodeId": item["oldId"]},
            {"requestId": item["requestId"], "couponId": DST, "code": item["code"]})


def rotate_request_id(plan, item):
    """A reused requestId replays the first result for 24h, so a code that was rolled back
    needs a fresh one before it is created again."""
    old = item["requestId"]
    item["requestId"] = str(uuid.uuid4())
    save(PLAN, plan)
    log({"label": f"rotate requestId {item['code']}", "old": old, "new": item["requestId"]})


def cmd_dry_run():
    plan = load(PLAN, None) or sys.exit("run `plan` first")
    for n, item in enumerate(plan["items"], 1):
        d, c = bodies(item)
        print(f"{n:>3}. {item['code']:18} (redeemed {item['timesRedeemed']})")
        print(f"      POST /promotion-codes/deactivate {json.dumps(d)}")
        print(f"      POST /promotion-codes/create     {json.dumps(c)}")
    print(f"\n{len(plan['items'])} codes, {2 * len(plan['items'])} writes, "
          f"about {2 * len(plan['items']) * WRITE_GAP / 60:.0f} min at one write per {WRITE_GAP}s")


# ---------------------------------------------------------------- run / rollback

def select(plan, only):
    items = plan["items"]
    if only:
        wanted = {c.lower() for c in only.split(",")}
        items = [i for i in items if i["code"].lower() in wanted]
        if len(items) != len(wanted):
            sys.exit(f"--only names codes not in the plan: {only}")
    return items


def halt(msg):
    print(f"\nHALTED: {msg}")
    log({"label": "halt", "message": msg})
    sys.exit(1)


def cmd_run(only, execute):
    plan = load(PLAN, None) or sys.exit("run `plan` first")
    state = load(STATE, {})
    todo = [i for i in select(plan, only) if state.get(i["code"], {}).get("stage") != "created"]
    if not execute:
        sys.exit(f"{len(todo)} codes would run. Add --execute to write.")

    # Fresh read right before writing: each old code must still be active with the same text.
    live = {p["id"]: p for p in list_codes(SRC)["promotionCodes"]}
    for i in todo:
        p = live.get(i["oldId"])
        stage = state.get(i["code"], {}).get("stage")
        if not p or p["code"] != i["code"] or (not p["active"] and stage != "deactivated"):
            halt(f"{i['code']} no longer matches the plan (live row: {p})")

    def on_sigint(*_):
        global _stop
        _stop = True
        print("\n   Ctrl-C: finishing this code, then stopping")
    signal.signal(signal.SIGINT, on_sigint)

    for n, item in enumerate(todo, 1):
        if _stop:
            halt("stopped by Ctrl-C between codes (nothing left switched off)")
        code, old = item["code"], item["oldId"]
        d_body, c_body = bodies(item)
        st = state.setdefault(code, {})
        print(f"[{n}/{len(todo)}] {code}")

        if st.get("stage") != "deactivated":
            http, data = write("/promotion-codes/deactivate", d_body, f"deactivate {code}")
            bad = [f"HTTP {http}"] if http != 200 else row_ok(data, pid=old, code=code, active=False)
            if bad:
                ahttp, adata = write("/promotion-codes/activate", d_body, f"ensure-on {code}")
                on = ahttp == 200 and not row_ok(adata, pid=old, active=True)
                halt(f"deactivate {code} failed ({', '.join(bad)}); old code "
                     f"{'confirmed active' if on else 'state UNKNOWN, check it now'}")
            st.update(stage="deactivated", deactivatedAt=now())
            save(STATE, state)
            print("      old code off")

        http, data = write("/promotion-codes/create", c_body, f"create {code}")
        bad = [f"HTTP {http}"] if http != 200 else row_ok(data, code=code, active=True, coupon=DST)
        if bad:
            # Reactivate first. Stripe refuses it if the new code took the text, so success
            # proves the create did not land; a refusal means go and look at the target list.
            print(f"      create failed ({', '.join(bad)}): reactivating old code")
            ahttp, adata = write("/promotion-codes/activate", d_body, f"reactivate {code}")
            if ahttp == 200 and not row_ok(adata, pid=old, active=True):
                st.update(stage="rolled_back", error=bad)
                save(STATE, state)
                rotate_request_id(plan, item)
                halt(f"{code}: create failed, old code reactivated (customers unaffected)")
            try:
                landed = [p for p in list_codes(DST)["promotionCodes"]
                          if p["code"].lower() == code.lower() and p["active"]]
            except SystemExit:
                landed = []
            if landed:
                st.update(stage="created", newId=landed[0]["id"], createdAt=now(), note="found on list")
                save(STATE, state)
                halt(f"create {code} returned {bad} but the code is live on {DST}; review, then resume")
            st.update(stage="DEAD", error=bad)
            save(STATE, state)
            halt(f"{code} IS SWITCHED OFF: create failed and the old code would not reactivate "
                 f"(HTTP {ahttp} {adata})")
        st.update(stage="created", newId=data["promotionCode"]["id"], createdAt=now())
        save(STATE, state)
        print(f"      live on {DST} as {st['newId']}")
    print(f"\nDone: {len(todo)} codes moved.")


def cmd_rollback(only, execute):
    plan = load(PLAN, None) or sys.exit("no plan")
    state = load(STATE, {})
    items = [i for i in select(plan, only) if state.get(i["code"], {}).get("newId")]
    if not execute:
        sys.exit(f"{len(items)} codes would roll back. Add --execute to write.")
    for item in items:
        st = state[item["code"]]
        print(f"rollback {item['code']}")
        http, data = write("/promotion-codes/deactivate", {"promotionCodeId": st["newId"]},
                           f"rollback-deactivate-new {item['code']}")
        if http != 200 or row_ok(data, pid=st["newId"], active=False):
            halt(f"could not switch off new {item['code']}: HTTP {http} {data}")
        http, data = write("/promotion-codes/activate", {"promotionCodeId": item["oldId"]},
                           f"rollback-reactivate-old {item['code']}")
        if http != 200 or row_ok(data, pid=item["oldId"], active=True):
            halt(f"new {item['code']} is off but old would not reactivate: HTTP {http} {data}")
        st.update(stage="rolled_back", rolledBackAt=now())
        save(STATE, state)
        rotate_request_id(plan, item)


# ---------------------------------------------------------------- reconcile

def cmd_reconcile():
    plan = load(PLAN, None) or sys.exit("no plan")
    state = load(STATE, {})
    src = {p["id"]: p for p in list_codes(SRC)["promotionCodes"]}
    dst_list = list_codes(DST)
    dst = {p["code"].lower(): p for p in dst_list["promotionCodes"]}
    moved = ok = 0
    for i in plan["items"]:
        st = state.get(i["code"], {})
        if st.get("stage") != "created":
            continue
        moved += 1
        old, new = src.get(i["oldId"]), dst.get(i["code"].lower())
        issues = []
        if not old or old["active"]:
            issues.append("old still active")
        if new is None:
            issues.append("new not on list" + (" (list truncated: check ledger)" if dst_list.get("truncated") else ""))
        elif not new["active"] or new["id"] != st["newId"]:
            issues.append(f"new row mismatch {new['id']} active={new['active']}")
        if issues:
            print(f"   {i['code']:18} {'; '.join(issues)}")
        else:
            ok += 1
    pending = [i["code"] for i in plan["items"] if state.get(i["code"], {}).get("stage") != "created"]
    print(f"moved {moved}, verified {ok}, pending {len(pending)}"
          + (f": {', '.join(pending[:10])}{' ...' if len(pending) > 10 else ''}" if pending else ""))
    skipped = {s["code"] for s in plan["skipped"]}
    changed = [p["code"] for p in src.values() if p["code"] in skipped and p["active"]]
    print(f"skipped codes now active on {SRC}: {changed or 'none'}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["plan", "dry-run", "run", "rollback", "reconcile"])
    ap.add_argument("--from", dest="src", required=True, help="source coupon id")
    ap.add_argument("--to", dest="dst", required=True, help="target coupon id")
    ap.add_argument("--run-dir", help="where plan/state/ledger live "
                    "(default ~/promo-migrations/<from>-to-<to>)")
    ap.add_argument("--approved-by", help="jonathan or hanan (or their email): required for any API call")
    ap.add_argument("--only", help="comma-separated codes (run/rollback)")
    ap.add_argument("--canary", help="code to put first in the plan")
    ap.add_argument("--execute", action="store_true", help="actually write (run/rollback)")
    a = ap.parse_args(argv)
    approver = APPROVERS.get((a.approved_by or "").strip().lower())
    if a.command != "dry-run" and not approver:
        sys.exit("--approved-by must be jonathan or hanan (Jonathan Galili or Hanan Amos): "
                 "marketing-brain processes may use this API only on their request or approval")
    run_dir = a.run_dir or os.path.expanduser(f"~/promo-migrations/{a.src}-to-{a.dst}")
    configure(a.src, a.dst, run_dir, approver)
    plan = load(PLAN, None)
    if plan and a.command != "plan" and (plan["src"], plan["dst"]) != (a.src, a.dst):
        sys.exit(f"plan in {run_dir} is for {plan['src']} -> {plan['dst']}, not {a.src} -> {a.dst}")
    {"plan": lambda: cmd_plan(a.canary), "dry-run": cmd_dry_run, "reconcile": cmd_reconcile,
     "run": lambda: cmd_run(a.only, a.execute),
     "rollback": lambda: cmd_rollback(a.only, a.execute)}[a.command]()


if __name__ == "__main__":
    main()
