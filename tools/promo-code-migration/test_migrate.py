"""Mock-API tests for migrate.py. No network, no key: `python3 test_migrate.py`.

FakeAPI enforces the two Stripe rules the tool leans on: code text is unique among active
codes (case-insensitive), and a reused requestId replays the first result.
"""
import contextlib, copy, importlib.util, io, itertools, json, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_R = {"firstTimeTransaction": False, "minimumAmount": None,
             "minimumAmountCurrency": None, "currencyOptions": []}
CODES = ["FORUM", "ACE", "BEN"]


class FakeAPI:
    def __init__(self, faults=None):
        self.codes, self.idem, self.calls = {}, {}, []
        self.n = itertools.count(1)
        self.faults = faults or {}          # (endpoint, code) -> responses returned first
        for c in CODES:
            self.add(c, "src", True)
        self.add("ALREADYMOVED", "dst", True)
        self.add("OLDOFF", "src", False)

    def add(self, code, coupon, active):
        pid = f"promo_{next(self.n)}"
        self.codes[pid] = {"id": pid, "code": code, "active": active, "coupon": {"id": coupon},
                           "restrictions": dict(DEFAULT_R), "timesRedeemed": 0}
        return pid

    def text_active(self, code):
        return any(r["active"] and r["code"].lower() == code.lower() for r in self.codes.values())

    def rows(self, code):
        return sorted((r["coupon"]["id"], r["active"]) for r in self.codes.values() if r["code"] == code)

    def __call__(self, method, path, body=None):
        self.calls.append((method, path, copy.deepcopy(body)))
        endpoint = path.split("?")[0].rsplit("/", 1)[-1]
        name = (body or {}).get("code") or (self.codes.get((body or {}).get("promotionCodeId"), {}).get("code"))
        if self.faults.get((endpoint, name)):
            return self.faults[(endpoint, name)].pop(0)
        if method == "GET":
            cid = path.split("couponId=")[1]
            return 200, {"ok": True, "truncated": False, "promotionCodes":
                         [copy.deepcopy(r) for r in self.codes.values() if r["coupon"]["id"] == cid]}
        r = self.codes.get((body or {}).get("promotionCodeId"))
        if endpoint == "deactivate":
            r["active"] = False
            return 200, {"ok": True, "promotionCode": copy.deepcopy(r)}
        if endpoint == "activate":
            if not r["active"] and self.text_active(r["code"]):
                return 400, {"ok": False, "error": "code already active elsewhere"}
            r["active"] = True
            return 200, {"ok": True, "promotionCode": copy.deepcopy(r)}
        if endpoint == "create":
            if body["requestId"] in self.idem:
                return self.idem[body["requestId"]]
            if self.text_active(body["code"]):
                res = (400, {"ok": False, "error": "code already taken"})
            else:
                pid = self.add(body["code"], body["couponId"], True)
                res = (200, {"ok": True, "promotionCode": copy.deepcopy(self.codes[pid])})
            self.idem[body["requestId"]] = res
            return res


def fresh(faults=None):
    spec = importlib.util.spec_from_file_location("migrate", os.path.join(HERE, "migrate.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.time.sleep = lambda s: None
    m.configure("src", "dst", tempfile.mkdtemp(), "Test Approver")
    api = FakeAPI(faults)
    m.call = api
    quietly(m.cmd_plan, "FORUM")
    return m, api


def quietly(fn, *a):
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            fn(*a)
            return "completed"
        except SystemExit as e:
            return f"exit {e.code}"


def stages(m):
    s = json.load(open(m.STATE)) if os.path.exists(m.STATE) else {}
    return {c: s.get(c, {}).get("stage") for c in CODES}


MOVED = [("dst", True), ("src", False)]
UNTOUCHED = [("src", True)]
results = []


def check(name, cond):
    results.append((name, cond))
    print(f"{'PASS' if cond else 'FAIL'}  {name}")


# plan
m, api = fresh()
plan = json.load(open(m.PLAN))
check("plan: canary first, inactive codes skipped",
      [i["code"] for i in plan["items"]][0] == "FORUM" and len(plan["items"]) == 3
      and {s["code"] for s in plan["skipped"]} == {"OLDOFF"})
api.add("Dup", "src", True)       # impossible in Stripe; exercises the defensive skip
api.add("DUP", "dst", True)
quietly(m.cmd_plan, "FORUM")
check("plan: text already active on target is skipped, not planned",
      "Dup" in {s["code"] for s in json.load(open(m.PLAN))["skipped"]})

# happy path + reconcile
out = quietly(m.cmd_run, None, True)
check("run: all codes moved", out == "completed" and all(api.rows(c) == MOVED for c in CODES))
check("run: no write without --execute", quietly(fresh()[0].cmd_run, None, False).startswith("exit"))

# canary only
m, api = fresh()
quietly(m.cmd_run, "FORUM", True)
check("canary: only FORUM moved", api.rows("FORUM") == MOVED and api.rows("ACE") == UNTOUCHED)

# 429 then success
m, api = fresh({("create", "ACE"): [(429, {"ok": False, "error": "retry in 12 seconds"})]})
check("429 on create: waits and completes", quietly(m.cmd_run, None, True) == "completed"
      and api.rows("ACE") == MOVED)

# create timed out but landed: retry replays, no duplicate
m, api = fresh()
real, fired = api.__call__, []
def lossy(method, path, body=None):
    r = real(method, path, body)
    if path.endswith("/create") and body["code"] == "ACE" and not fired:
        fired.append(1)
        return 0, {}
    return r
m.call = lossy
check("lost create response: replayed, exactly one new code", quietly(m.cmd_run, None, True) == "completed"
      and api.rows("ACE") == MOVED)

# create fails for good: old reactivated, requestId rotated, rerun works
m, api = fresh({("create", "ACE"): [(400, {"ok": False, "error": "invalid"})]})
rid = [i for i in json.load(open(m.PLAN))["items"] if i["code"] == "ACE"][0]["requestId"]
first = quietly(m.cmd_run, None, True)
mid = api.rows("ACE")
rid2 = [i for i in json.load(open(m.PLAN))["items"] if i["code"] == "ACE"][0]["requestId"]
second = quietly(m.cmd_run, None, True)
check("create 400: halts with old code back on", first == "exit 1" and mid == UNTOUCHED)
check("create 400: requestId rotated, rerun completes", rid != rid2 and second == "completed"
      and api.rows("ACE") == MOVED)

# deactivate fails for good: code confirmed on, nothing else touched
m, api = fresh({("deactivate", "ACE"): [(500, {"ok": False})] * 4})
check("deactivate 5xx exhausted: halts, code still active",
      quietly(m.cmd_run, None, True) == "exit 1" and api.rows("ACE") == UNTOUCHED
      and api.rows("BEN") == UNTOUCHED)

# create and reactivate both fail: reported DEAD
m, api = fresh({("create", "ACE"): [(500, {"ok": False})] * 4,
                ("activate", "ACE"): [(500, {"ok": False})] * 4})
quietly(m.cmd_run, None, True)
check("create + reactivate fail: stage DEAD, run stops", stages(m)["ACE"] == "DEAD"
      and api.rows("BEN") == UNTOUCHED)

# resume after crash between the two writes
m, api = fresh()
ace = [i for i in json.load(open(m.PLAN))["items"] if i["code"] == "ACE"][0]
api.codes[ace["oldId"]]["active"] = False
json.dump({"ACE": {"stage": "deactivated"}}, open(m.STATE, "w"))
check("resume mid-pair: creates without re-deactivating",
      quietly(m.cmd_run, None, True) == "completed" and api.rows("ACE") == MOVED)

# live drift between plan and run: zero writes
m, api = fresh()
ben = [i for i in json.load(open(m.PLAN))["items"] if i["code"] == "BEN"][0]
api.codes[ben["oldId"]]["active"] = False
out = quietly(m.cmd_run, None, True)
check("drift before run: halts before any write",
      out == "exit 1" and not any(meth == "POST" for meth, _, _ in api.calls))

# rollback then rerun: a real create, not a replay of the dead id
m, api = fresh()
quietly(m.cmd_run, None, True)
quietly(m.cmd_rollback, "ACE", True)
after_rb = api.rows("ACE")
quietly(m.cmd_run, "ACE", True)
check("rollback: old back on, new off", after_rb == [("dst", False), ("src", True)])
check("rerun after rollback: fresh create is live",
      api.rows("ACE") == [("dst", False), ("dst", True), ("src", False)])

# approval gate
spec = importlib.util.spec_from_file_location("migrate_gate", os.path.join(HERE, "migrate.py"))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
g.call = lambda *a, **k: sys.exit("network call attempted")
tmp = tempfile.mkdtemp()
with contextlib.redirect_stderr(io.StringIO()):
    no_flag = quietly(g.main, ["plan", "--from", "src", "--to", "dst", "--run-dir", tmp])
    wrong = quietly(g.main, ["plan", "--from", "src", "--to", "dst", "--run-dir", tmp,
                             "--approved-by", "someone@riverside.fm"])
check("gate: API commands refuse without an approved requester",
      "--approved-by" in no_flag and "--approved-by" in wrong)
spec2 = importlib.util.spec_from_file_location("migrate_raw", os.path.join(HERE, "migrate.py"))
raw = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(raw)
raw.configure("src", "dst", tempfile.mkdtemp(), None)
check("gate: call() itself refuses with no approver", "approved-by" in quietly(raw.call, "GET", "/catalog"))
m2, _ = fresh()
quietly(m2.cmd_run, "FORUM", True)
first_write = json.loads(open(m2.LEDGER).readline())
check("ledger: every call records the approver", first_write.get("approvedBy") == "Test Approver")

failed = [n for n, ok in results if not ok]
print(f"\n{len(results) - len(failed)}/{len(results)} passed")
sys.exit(1 if failed else 0)
