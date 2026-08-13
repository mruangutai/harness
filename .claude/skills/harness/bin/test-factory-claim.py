#!/usr/bin/env python3
"""Tests for factory_claim.py — the polling and claiming tool (T-05, D-05, REQ-03).

Nothing here spawns a subprocess and nothing touches a real board, repository, or this
repository's own `.harness/features/`. Every call `factory_claim` makes into `factory_gh`'s
public functions is monkeypatched over a single `Recorder`, whose ordered `.calls` list is the
evidence every assertion below is a projection of. `FEATURES_ROOT` is monkeypatched to a
temporary directory built once by this file — `build_features_root()` — holding two fixture
features: FEAT-01-demo (one unblocked task, used by every case that is not about the blocker
gate) and FEAT-02-block (several tasks with varying `depends_on`, used by the seven blocker-gate
cases, SC-22). Both are read via `factory_claim.harness_yaml`, never re-derived, so a case that
needs to prove "no plan file consulted" monkeypatches `harness_yaml.load_plan` itself.
"""
import contextlib
import io
import json
import os
import re
import sys
import tempfile

import yaml

import factory_claim as claim
import factory_cli
import factory_config as fc
import factory_gh
import harness_yaml

FAILS = 0
RAN = 0


def check(name, cond, detail=""):
    global FAILS, RAN
    RAN += 1
    if cond:
        print(f"ok    {name}")
    else:
        FAILS += 1
        print(f"FAIL  {name}" + (f"\n        {detail}" if detail else ""))


OWNER = "acme"
BOARD = 3
STATION_FIELD = "Status"
REPO = "acme/widget"
DEFAULT_BRANCH = "main"
AS_LOGIN = "agent-1"

# A second repository/board pair, used only by the per-repository-board cases (FEAT-16 T-02).
# Deliberately a DIFFERENT station_field name from REPO's board, so a case can prove a query was
# built from THIS board's own field and ready option rather than the other board's.
REPO_B = "acme/gadget"
BOARD_B = 5
STATION_FIELD_B = "StatusB"

MUTATING_NAMES = ("add_label", "assign", "project_field_set")


# --------------------------------------------------------------------------
# Recorder — a single ordered call log over every factory_gh public function T-05 calls.
# --------------------------------------------------------------------------

class Recorder:
    def __init__(self):
        self.calls = []
        self.field_options = {
            STATION_FIELD: ["Ready", "Building", "Review", "Backlog", "Done"],
        }
        # (owner, number) -> {field: [options]} — overrides field_options for that ONE board,
        # used by the per-repository-board cases to give two boards different station option
        # sets. Every case not about that keeps using the simpler field_options dict.
        self.board_field_options = {}
        self.items = []
        # (owner, number) -> [items] — overrides self.items for that ONE board's project_items
        # call, used by the per-repository-board cases so two boards can return different (or
        # empty) item lists. Every case not about that keeps using the simpler self.items list.
        self.items_by_board = {}
        self.issue_data = {}          # number -> dict
        self.create_ref_results = {}  # number -> True | False | Exception
        self.default_sha = "deadbeef"
        self.preflight_raises = None
        self.queries = []

    def mutating_calls(self):
        return [c for c in self.calls if c[0] in MUTATING_NAMES]

    def create_ref_calls(self):
        return [c for c in self.calls if c[0] == "create_ref"]

    # --- factory_gh's public surface used by factory_claim ---
    def preflight(self):
        self.calls.append(("preflight", ()))
        if self.preflight_raises is not None:
            raise self.preflight_raises

    def project_field_options(self, owner, number, field):
        self.calls.append(("project_field_options", (owner, number, field)))
        by_board = self.board_field_options.get((owner, number))
        if by_board is not None:
            return by_board.get(field, [])
        return self.field_options.get(field, [])

    def project_items(self, owner, number, query=None, limit=500):
        self.calls.append(("project_items", (owner, number, query)))
        self.queries.append(query)
        key = (owner, number)
        if key in self.items_by_board:
            return list(self.items_by_board[key])
        return list(self.items)

    def issue_board_item_id(self, repo, number, board_number):
        self.calls.append(("issue_board_item_id", (repo, number, board_number)))
        for it in self.items:
            content = it.get("content") or {}
            if content.get("number") == number and content.get("repository") == repo:
                return it.get("id")
        return None

    def issue_view(self, repo, number, fields):
        self.calls.append(("issue_view", (repo, number, tuple(fields))))
        data = self.issue_data.get(number)
        if data is None:
            raise AssertionError(f"test bug: no issue_data fixture for #{number}")
        # Honours the requested `fields` (FEAT-13 fix01) — every fixture in this file happens to
        # carry all of {number, title, state, labels, assignees}, so filtering to `fields` is a
        # no-op today (production always requests all five, T-05 D-05) and stays a no-op unless
        # a future call site narrows its own request; if `state` is ever dropped from that
        # request, `.get("state")` reads None the same way a real gh response would.
        return {k: v for k, v in data.items() if k in fields}

    def default_branch_sha(self, repo, branch):
        self.calls.append(("default_branch_sha", (repo, branch)))
        return self.default_sha

    def create_ref(self, repo, ref, sha):
        self.calls.append(("create_ref", (repo, ref, sha)))
        num = int(ref.rsplit("-", 1)[-1])
        result = self.create_ref_results.get(num, True)
        if isinstance(result, BaseException):
            raise result
        return result

    def add_label(self, repo, number, label):
        self.calls.append(("add_label", (repo, number, label)))

    def assign(self, repo, number, login):
        self.calls.append(("assign", (repo, number, login)))

    def project_field_set(self, owner, number, item_id, field, option):
        self.calls.append(("project_field_set", (owner, number, item_id, field, option)))


PATCHED = (
    "preflight", "project_field_options", "project_items", "issue_board_item_id", "issue_view",
    "default_branch_sha", "create_ref", "add_label", "assign", "project_field_set",
)


def patch_gh(rec):
    saved = {name: getattr(factory_gh, name) for name in PATCHED}
    for name in PATCHED:
        setattr(factory_gh, name, getattr(rec, name))
    return saved


def unpatch_gh(saved):
    for name, fn in saved.items():
        setattr(factory_gh, name, fn)


# --------------------------------------------------------------------------
# Fixture builders.
# --------------------------------------------------------------------------

def repo_board(owner=OWNER, number=BOARD, station_field=STATION_FIELD,
               ready="Ready", building="Building", review="Review"):
    """One repos[] entry's own `board:` block (FEAT-16 T-01/T-02) — the per-repo shape, never a
    fleet-level fallback."""
    return {
        "owner": owner,
        "number": number,
        "station_field": station_field,
        "stations": {"ready": ready, "building": building, "review": review},
    }


def repo_dict(name, default_branch=DEFAULT_BRANCH, board=None):
    return {"name": name, "default_branch": default_branch, "board": board or repo_board()}


def good_fleet_dict(workspace_root, repos=None):
    return {
        "schema": "factory-fleet/1",
        "repos": repos if repos is not None else [repo_dict(REPO)],
        "workspace_root": workspace_root,
    }


def two_repo_fleet(workspace_root, board_b_number=BOARD_B, station_field_b=STATION_FIELD_B,
                    ready_b="ReadyB", building_b="BuildingB", review_b="ReviewB"):
    """REPO on board BOARD (owner OWNER), REPO_B on a DIFFERENT board — the per-repository-board
    cases (FEAT-16 T-02)."""
    return good_fleet_dict(workspace_root, repos=[
        repo_dict(REPO),
        repo_dict(REPO_B, board=repo_board(
            number=board_b_number, station_field=station_field_b,
            ready=ready_b, building=building_b, review=review_b,
        )),
    ])


def same_board_two_repo_fleet(workspace_root):
    """REPO and REPO_B declare the SAME board number — the de-duplication case."""
    return good_fleet_dict(workspace_root, repos=[
        repo_dict(REPO),
        repo_dict(REPO_B, board=repo_board()),
    ])


def write_yaml(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)
    return path


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return path


def board_item(item_id, num, repo_owner_name, repo_url=None, title=None):
    """The REAL measured shape (T-05's intent): `repository` holds the URL form of the SAME
    repository `content.repository` holds in owner/name form. The fleet lists repositories in
    owner/name form, so an implementation reading the wrong key (`repository`) matches nothing
    and every candidate is silently discarded — this fixture is what catches that."""
    return {
        "id": item_id,
        "content": {"number": num, "repository": repo_owner_name, "title": title or f"stub {num}"},
        "repository": repo_url or f"https://github.com/{repo_owner_name}",
        "title": title or f"stub {num}",
    }


def issue_data(number, title, state="OPEN", labels=None, assignees=None):
    return {
        "number": number,
        "title": title,
        "state": state,
        "labels": [{"name": l} for l in (labels or [])],
        "assignees": [{"login": a} for a in (assignees or [])],
    }


def task_dict(tid, depends_on=None, title="do the thing"):
    t = {
        "id": tid,
        "title": title,
        "change_type": "feature",
        "execution_mode": "team",
        "files": [f"{tid}.py"],
        "verify": "true",
        "intent": f"intent text for {tid}, verbatim.",
        "traces": ["REQ-03"],
    }
    if depends_on:
        t["depends_on"] = depends_on
    return t


def plan_dict(feat, tasks):
    return {
        "schema": "plan/1",
        "feature": feat,
        "approval": {"status": "approved"},
        "tasks": tasks,
    }


def build_features_root():
    """One shared fixture tree, built once. FEAT-01-demo carries a single unblocked task and
    backs every case that is not about the blocker gate. FEAT-02-block backs the seven SC-22
    cases: T-05 (single blocker), T-06 (three blockers, MIXED), T-09 (clear), T-10 (unresolvable
    blocker naming T-99, which feature.json never maps)."""
    root = tempfile.mkdtemp(prefix="claim-features-")

    demo = os.path.join(root, "FEAT-01-demo")
    write_yaml(os.path.join(demo, "plan.yaml"),
               plan_dict("FEAT-01-demo", [task_dict("T-01")]))
    # An eleven-key feature.json fixture, read end to end by issue_number below — not just a
    # bare `factory` key — so this case doubles as T-05's (FEAT-14) required eleven-key case.
    write_json(os.path.join(demo, "feature.json"), {
        "feature_id": "FEAT-01-demo",
        "branch": "none",
        "pr": None,
        "status": "Building",
        "review_sha": "none",
        "cycles_used": 0,
        "max_total_cycles": 10,
        "max_total_runs": 20,
        "runs": [],
        "github": {"milestone": None, "parent": None, "parent_origin": None,
                   "attached": [], "issues": {}},
        "factory": {"issues": {"T-01": 501}},
    })

    block = os.path.join(root, "FEAT-02-block")
    write_yaml(os.path.join(block, "plan.yaml"), plan_dict("FEAT-02-block", [
        task_dict("T-05", depends_on=["T-02"]),
        task_dict("T-06", depends_on=["T-02", "T-03", "T-04"]),
        task_dict("T-09"),
        task_dict("T-10", depends_on=["T-99"]),
    ]))
    write_json(os.path.join(block, "feature.json"), {
        "factory": {"issues": {"T-02": 601, "T-03": 602, "T-04": 603}},
    })

    return root


FEATURES_ROOT = build_features_root()


# --------------------------------------------------------------------------
# Driver.
# --------------------------------------------------------------------------

def run_main(rec, extra_args, workspace_root=None, fleet_dict=None):
    workspace_root = workspace_root or tempfile.mkdtemp(prefix="claim-ws-")
    fleet_dir = tempfile.mkdtemp(prefix="claim-fleet-")
    fleet_path = write_yaml(
        os.path.join(fleet_dir, "fleet.yaml"),
        fleet_dict if fleet_dict is not None else good_fleet_dict(workspace_root),
    )
    argv_saved = sys.argv
    sys.argv = ["factory_claim.py", "--fleet", fleet_path] + extra_args
    saved_gh = patch_gh(rec)
    saved_features_root = claim.FEATURES_ROOT
    claim.FEATURES_ROOT = FEATURES_ROOT
    out, err = io.StringIO(), io.StringIO()
    code = None
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                factory_cli.run(
                    "claim", claim._main,
                    expected=(fc.FleetError, factory_gh.GhError),
                )
            except SystemExit as e:
                code = e.code
        if code is None:
            code = 0
    finally:
        sys.argv = argv_saved
        unpatch_gh(saved_gh)
        claim.FEATURES_ROOT = saved_features_root
    return code, out.getvalue(), err.getvalue()


# ==========================================================================
# M — the "at minimum" list.
# ==========================================================================

# M1. empty ready column exits 1.
rec = Recorder()
rec.items = []
code, out, err = run_main(rec, ["--as", AS_LOGIN])
check("(M1) empty ready column exits 1", code == 1, code)
check("(M1) stdout is empty", out == "", out)

# M2. an item in a repo absent from the fleet is not a candidate.
rec = Recorder()
rec.items = [board_item("i1", 900, "acme/other")]
code, out, err = run_main(rec, ["--as", AS_LOGIN])
check("(M2) repo not in fleet exits 1 (no candidate)", code == 1, code)
check("(M2) issue_view never called for it", not any(c[0] == "issue_view" for c in rec.calls),
      rec.calls)

# M3/M6/M7/M8. happy path — real board-item shape, station set once, JSON branch, feature key,
# harness-only label claims with feature null, project_items called with a real query.
rec = Recorder()
rec.items = [board_item("i1", 42, REPO, repo_url=f"https://github.com/{REPO}")]
rec.issue_data[42] = issue_data(42, "T-01 do the thing", labels=["harness", "feature:FEAT-01-demo"])
code, out, err = run_main(rec, ["--as", AS_LOGIN])
check("(M3/M6) happy path exits 0", code == 0, code)
payload = json.loads(out) if out else None
check("(M3/M6) stdout parses as one JSON payload", payload is not None, out)
check("(M6) branch is factory/issue-42", payload and payload.get("branch") == "factory/issue-42",
      payload)
check("(M6) station set to Building exactly once",
      len([c for c in rec.calls if c[0] == "project_field_set"]) == 1
      and rec.calls[[c[0] for c in rec.calls].index("project_field_set")][1][4] == "Building",
      rec.calls)
check("(M7) feature key equals label value with prefix stripped",
      payload and payload.get("feature") == "FEAT-01-demo", payload)
check("(M8) project_items called with a query naming the ready option",
      rec.queries and rec.queries[0] and "Ready" in rec.queries[0], rec.queries)

rec2 = Recorder()
rec2.items = [board_item("i1", 43, REPO)]
rec2.issue_data[43] = issue_data(43, "some mirrored issue", labels=["harness"])
code, out, err = run_main(rec2, ["--as", AS_LOGIN])
check("(M7) harness-only issue claims normally, exit 0", code == 0, code)
payload2 = json.loads(out)
check("(M7) feature is null for an issue with no feature: label", payload2.get("feature") is None,
      payload2)

# M4. lowest issue number wins among three claimable candidates.
rec = Recorder()
rec.items = [
    board_item("i3", 103, REPO), board_item("i1", 101, REPO), board_item("i2", 102, REPO),
]
for n in (101, 102, 103):
    rec.issue_data[n] = issue_data(n, f"issue {n}", labels=["harness"])
code, out, err = run_main(rec, ["--as", AS_LOGIN])
check("(M4) lowest issue number wins", json.loads(out).get("issue") == 101, out)

# M5. a station option name missing from the recorder's field options exits 2, BEFORE any
# board read.
rec = Recorder()
rec.field_options[STATION_FIELD] = ["Ready", "Backlog", "Done"]  # no Building, no Review
rec.items = [board_item("i1", 900, REPO)]
code, out, err = run_main(rec, ["--as", AS_LOGIN])
check("(M5) missing station option exits 2", code == 2, code)
check("(M5) no board read happened", not any(c[0] == "project_items" for c in rec.calls),
      rec.calls)
check("(M5) stderr names the missing option, the field and the fleet file",
      "Building" in err and STATION_FIELD in err and "fleet.yaml" in err, err)


# ==========================================================================
# C-3 — the stream-split contract.
# ==========================================================================

# C1. empty-column path: stdout empty, "no work available" on stderr, exit 1.
rec = Recorder()
rec.items = []
code, out, err = run_main(rec, ["--as", AS_LOGIN])
check("(C1) exit 1", code == 1, code)
check("(C1) stdout is EMPTY", out == "", out)
check("(C1) stderr carries 'no work available'", "no work available" in err, err)

# C2. happy path: stdout parses as JSON in a single json.loads of the whole stream.
rec = Recorder()
rec.items = [board_item("i1", 42, REPO)]
rec.issue_data[42] = issue_data(42, "T-01 do the thing", labels=["harness"])
code, out, err = run_main(rec, ["--as", AS_LOGIN])
try:
    json.loads(out)
    parsed_ok = True
except Exception:
    parsed_ok = False
check("(C2) whole stdout parses as one JSON object", parsed_ok, out)
check("(C2) exit 0", code == 0, code)
# FIX 2 (FEAT-13 fix01): issue_view is invoked with "state" among the requested fields —
# without it the OPEN-state check always reads None, `!= "OPEN"` is always true, and the tool
# refuses EVERY issue (total outage of claim).
c2_issue_view_calls = [c for c in rec.calls if c[0] == "issue_view"]
check("(C2) issue_view's requested fields include \"state\"",
      c2_issue_view_calls and "state" in c2_issue_view_calls[0][1][2], c2_issue_view_calls)

# C3. a monkeypatched preflight raising GhError exits 2, not 1, stdout empty, one stderr line.
rec = Recorder()
rec.preflight_raises = factory_gh.GhError(
    ["auth", "status"], 1, "", "", "gh auth status failed", "gh", "run `gh auth login`",
)
code, out, err = run_main(rec, ["--as", AS_LOGIN])
check("(C3) exit 2, not 1", code == 2, code)
check("(C3) stdout empty", out == "", out)
lines = [l for l in err.splitlines() if l.strip()]
check("(C3) exactly one stderr line", len(lines) == 1, err)
check("(C3) stderr names a concrete value", "gh" in lines[0], err)


# ==========================================================================
# R — REQ-03.
# ==========================================================================

# R1. create_ref True on the first candidate: payload+exit0; label, assign, field-set all
# happen AFTER create_ref, in that relative order.
rec = Recorder()
rec.items = [board_item("i1", 55, REPO)]
rec.issue_data[55] = issue_data(55, "T-01 do the thing", labels=["harness"])
code, out, err = run_main(rec, ["--as", AS_LOGIN])
names = [c[0] for c in rec.calls]
create_idx = names.index("create_ref")
check("(R1) exit 0 with payload", code == 0 and json.loads(out).get("issue") == 55, (code, out))
check("(R1) label/assign/field_set all happen AFTER create_ref",
      all(names.index(n) > create_idx for n in ("add_label", "assign", "project_field_set")),
      names)

# R2. EXHAUSTION — route one: create_ref False for all three. Route two: pre-filter rejects
# all three (closed, already-labelled, already-assigned). Both exit 1, payload-free stdout,
# zero mutating calls; stderr says "no claimable work" not "no work available"; route1 vs
# route2 stderr differ; route1 names each candidate + ref-already-exists.
rec1 = Recorder()
rec1.items = [board_item("i1", 71, REPO), board_item("i2", 72, REPO), board_item("i3", 73, REPO)]
for n in (71, 72, 73):
    rec1.issue_data[n] = issue_data(n, f"issue {n}", labels=["harness"])
    rec1.create_ref_results[n] = False
code1, out1, err1 = run_main(rec1, ["--as", AS_LOGIN])
check("(R2 route1) exit 1", code1 == 1, code1)
check("(R2 route1) stdout empty", out1 == "", out1)
check("(R2 route1) zero mutating calls", rec1.mutating_calls() == [], rec1.mutating_calls())
check("(R2 route1) 'no claimable work' present, 'no work available' absent",
      "no claimable work" in err1 and "no work available" not in err1, err1)
check("(R2 route1) names all three issue numbers with ref-already-exists",
      all(f"{n}" in err1 for n in (71, 72, 73)) and err1.count("already exists") == 3, err1)

rec2 = Recorder()
rec2.items = [board_item("i1", 81, REPO), board_item("i2", 82, REPO), board_item("i3", 83, REPO)]
rec2.issue_data[81] = issue_data(81, "issue 81", state="CLOSED", labels=["harness"])
rec2.issue_data[82] = issue_data(82, "issue 82", labels=["harness", "factory:claimed"])
rec2.issue_data[83] = issue_data(83, "issue 83", labels=["harness"], assignees=["someone-else"])
code2, out2, err2 = run_main(rec2, ["--as", AS_LOGIN])
check("(R2 route2) exit 1", code2 == 1, code2)
check("(R2 route2) stdout empty", out2 == "", out2)
check("(R2 route2) zero mutating calls", rec2.mutating_calls() == [], rec2.mutating_calls())
check("(R2 route2) no create_ref attempted at all", rec2.create_ref_calls() == [],
      rec2.create_ref_calls())
check("(R2 route2) 'no claimable work' present, 'no work available' absent",
      "no claimable work" in err2 and "no work available" not in err2, err2)
check("(R2) route1 and route2 stderr are NOT equal", err1 != err2, (err1, err2))

# R3. the lowest-numbered candidate unclaimable, once per reason (four), still claims the next
# and exits 0.
def r3_case(label, low_issue_data, low_ref_false=False):
    rec = Recorder()
    rec.items = [board_item("i1", 91, REPO), board_item("i2", 92, REPO)]
    rec.issue_data[91] = low_issue_data
    rec.issue_data[92] = issue_data(92, "T-01 do the thing", labels=["harness"])
    if low_ref_false:
        rec.create_ref_results[91] = False
    code, out, err = run_main(rec, ["--as", AS_LOGIN])
    check(f"(R3 {label}) exits 0 and claims #92", code == 0 and json.loads(out).get("issue") == 92,
          (code, out))

r3_case("closed", issue_data(91, "issue 91", state="CLOSED", labels=["harness"]))
r3_case("already-labelled", issue_data(91, "issue 91", labels=["harness", "factory:claimed"]))
r3_case("already-assigned", issue_data(91, "issue 91", labels=["harness"], assignees=["other"]))
r3_case("ref-refused", issue_data(91, "issue 91", labels=["harness"]), low_ref_false=True)

# R4. --issue: create_ref False on an issue assigned to a DIFFERENT login exits 3, zero
# mutations. --issue on self-owned (factory:claimed + assignees include --as) exits 0,
# re-emits WITHOUT calling create_ref. Same issue in poll mode is skipped, not re-emitted.
rec = Recorder()
rec.items = [board_item("i1", 61, REPO)]
rec.issue_data[61] = issue_data(61, "T-01 do the thing", labels=["harness"])
rec.create_ref_results[61] = False
code, out, err = run_main(rec, ["--as", AS_LOGIN, "--issue", "61"])
check("(R4) --issue lost race exits 3", code == 3, code)
check("(R4) zero mutating calls", rec.mutating_calls() == [], rec.mutating_calls())
r4_lookup = [c for c in rec.calls if c[0] == "issue_board_item_id"]
check("(R4) --issue resolves via issue_board_item_id EXACTLY ONCE, zero project_items calls",
      len(r4_lookup) == 1 and not any(c[0] == "project_items" for c in rec.calls), rec.calls)
check("(R4) issue_board_item_id called with the fleet repo entry's own name, then args.issue, "
      "then the board number",
      r4_lookup and r4_lookup[0][1] == (REPO, 61, BOARD), r4_lookup)

rec = Recorder()
rec.items = [board_item("i1", 62, REPO)]
rec.issue_data[62] = issue_data(
    62, "T-01 do the thing", labels=["harness", "factory:claimed"], assignees=[AS_LOGIN],
)
code, out, err = run_main(rec, ["--as", AS_LOGIN, "--issue", "62"])
check("(R4) --issue self-owned re-entry exits 0", code == 0, code)
check("(R4) self-owned re-entry payload", json.loads(out).get("issue") == 62, out)
check("(R4) self-owned re-entry never calls create_ref",
      not any(c[0] == "create_ref" for c in rec.calls), rec.calls)
check("(R4) self-owned re-entry resolves via issue_board_item_id, zero project_items calls",
      any(c[0] == "issue_board_item_id" for c in rec.calls)
      and not any(c[0] == "project_items" for c in rec.calls), rec.calls)

rec = Recorder()
rec.items = [board_item("i1", 62, REPO)]
rec.issue_data[62] = issue_data(
    62, "T-01 do the thing", labels=["harness", "factory:claimed"], assignees=[AS_LOGIN],
)
code, out, err = run_main(rec, ["--as", AS_LOGIN])  # poll mode, no --issue
check("(R4) same issue in POLL mode is skipped (exit 1), not re-emitted", code == 1, code)

# R5. create_ref RAISING GhError exits 2, never 3, and the loop stops rather than skipping.
rec = Recorder()
rec.items = [board_item("i1", 65, REPO), board_item("i2", 66, REPO)]
rec.issue_data[65] = issue_data(65, "issue 65", labels=["harness"])
rec.issue_data[66] = issue_data(66, "issue 66", labels=["harness"])
rec.create_ref_results[65] = factory_gh.GhError(
    ["api"], 1, "", "", "gh api failed", REPO, "check auth",
)
code, out, err = run_main(rec, ["--as", AS_LOGIN])
check("(R5) exits 2, not 3", code == 2, code)
check("(R5) loop stopped — #66 was never reached (issue_view called once)",
      len([c for c in rec.calls if c[0] == "issue_view"]) == 1, rec.calls)


# ==========================================================================
# R6. SC-06 — the closed-issue refusal (D-05). Once the is:open board filter is gone, a closed
# issue reaches the candidate loop; without an explicit check, an issue this agent already owns
# would satisfy the self-ownership branch at 5a and be emitted as claimable, finished work. The
# refusal sits BEFORE 5a, so both an unowned and a self-owned closed issue are refused —
# asserted separately, since only the self-owned case exercises the ordering this decision
# depends on.
# ==========================================================================

# R6a. --issue on a closed issue this agent does NOT own: refused, zero mutating calls, zero
# create_ref calls.
rec = Recorder()
rec.items = [board_item("i1", 95, REPO)]
rec.issue_data[95] = issue_data(95, "issue 95", state="CLOSED", labels=["harness"])
code, out, err = run_main(rec, ["--as", AS_LOGIN, "--issue", "95"])
check("(R6a) --issue on a closed, unowned issue exits 2 (refused)", code == 2, code)
check("(R6a) zero mutating calls", rec.mutating_calls() == [], rec.mutating_calls())
check("(R6a) zero create_ref calls", rec.create_ref_calls() == [], rec.create_ref_calls())
check("(R6a) stdout empty", out == "", out)
check("(R6a) stderr names the issue", "95" in err, err)

# R6b. --issue on a closed issue this agent ALREADY owns (factory:claimed + assignees include
# --as) — the self-ownership branch would otherwise emit it. Still refused, not re-emitted.
rec = Recorder()
rec.items = [board_item("i1", 96, REPO)]
rec.issue_data[96] = issue_data(
    96, "issue 96", state="CLOSED", labels=["harness", "factory:claimed"], assignees=[AS_LOGIN],
)
code, out, err = run_main(rec, ["--as", AS_LOGIN, "--issue", "96"])
check("(R6b) --issue on a closed, self-owned issue exits 2 (refused), NOT re-emitted at exit 0",
      code == 2, code)
check("(R6b) zero mutating calls", rec.mutating_calls() == [], rec.mutating_calls())
check("(R6b) zero create_ref calls", rec.create_ref_calls() == [], rec.create_ref_calls())
check("(R6b) stdout empty", out == "", out)

# R7. --issue on an issue the board holds under no fleet repo the lookup matches: refused
# (D-02's accepted behaviour delta — exit 2, not the old exit-1 nothing_to_do), zero mutations.
rec = Recorder()
rec.items = []   # issue_board_item_id finds nothing for any fleet repo
code, out, err = run_main(rec, ["--as", AS_LOGIN, "--issue", "97"])
check("(R7) --issue found on no fleet repo exits 2 (refused)", code == 2, code)
check("(R7) zero mutating calls", rec.mutating_calls() == [], rec.mutating_calls())
check("(R7) stderr names the issue", "97" in err, err)

# R8. SC-09 — the poll path (no --issue) is UNCHANGED: still calls project_items exactly once
# with the station-and-open query string.
rec = Recorder()
rec.items = [board_item("i1", 98, REPO)]
rec.issue_data[98] = issue_data(98, "issue 98", labels=["harness"])
code, out, err = run_main(rec, ["--as", AS_LOGIN])
poll_calls = [c for c in rec.calls if c[0] == "project_items"]
check("(R8) poll mode calls project_items EXACTLY ONCE", len(poll_calls) == 1, rec.calls)
check("(R8) poll query names the ready station and is:open, unchanged",
      poll_calls and poll_calls[0][1][2] == f'{STATION_FIELD}:"Ready" is:open', poll_calls)
check("(R8) poll mode never calls issue_board_item_id",
      not any(c[0] == "issue_board_item_id" for c in rec.calls), rec.calls)


# ==========================================================================
# B — the blocker gate (SC-22), using FEAT-02-block.
# ==========================================================================

def blocked_issue_view(labels_extra=None):
    return issue_data(700, "T-05 do the thing", labels=["harness", "feature:FEAT-02-block"] + (labels_extra or []))


# B1. SKIP AND CONTINUE — the blocked lowest-numbered candidate plus a clear higher one.
rec = Recorder()
rec.items = [board_item("i1", 700, REPO), board_item("i2", 720, REPO)]
rec.issue_data[700] = blocked_issue_view()
rec.issue_data[720] = issue_data(720, "T-09 do the thing", labels=["harness", "feature:FEAT-02-block"])
rec.issue_data[601] = issue_data(601, "T-02", state="OPEN")
code, out, err = run_main(rec, ["--as", AS_LOGIN])
check("(B1) exits 0", code == 0, code)
check("(B1) create_ref called EXACTLY ONCE, with the CLEAR candidate (#720)",
      rec.create_ref_calls() == [("create_ref", (REPO, "refs/heads/factory/issue-720", "deadbeef"))],
      rec.create_ref_calls())
check("(B1) blocked candidate's skip reason on stderr, distinct from labelled/assigned reasons",
      "700" in err and "T-02" in err and "already carries factory:claimed" not in err
      and "already assigned" not in err, err)

# B2. EVERY CANDIDATE BLOCKED.
rec = Recorder()
rec.items = [board_item("i1", 700, REPO)]
rec.issue_data[700] = blocked_issue_view()
rec.issue_data[601] = issue_data(601, "T-02", state="OPEN")
code, out, err = run_main(rec, ["--as", AS_LOGIN])
check("(B2) exits 1", code == 1, code)
check("(B2) zero mutating calls, including create_ref",
      rec.mutating_calls() == [] and rec.create_ref_calls() == [],
      (rec.mutating_calls(), rec.create_ref_calls()))
check("(B2) 'no claimable work' present, 'no work available' absent",
      "no claimable work" in err and "no work available" not in err, err)

# B3. ALL BLOCKERS CLOSED — the same fixture, blocker now closed: the candidate IS claimed.
rec = Recorder()
rec.items = [board_item("i1", 700, REPO)]
rec.issue_data[700] = blocked_issue_view()
rec.issue_data[601] = issue_data(601, "T-02", state="CLOSED")
code, out, err = run_main(rec, ["--as", AS_LOGIN])
check("(B3) all blockers closed: candidate IS claimed",
      code == 0 and rec.create_ref_calls() == [
          ("create_ref", (REPO, "refs/heads/factory/issue-700", "deadbeef")),
      ],
      (code, rec.create_ref_calls()))

# B4. MIXED BLOCKER SET — T-06 (issue 701) depends on T-02(closed), T-03(closed), T-04(open).
rec = Recorder()
rec.items = [board_item("i1", 701, REPO), board_item("i2", 721, REPO)]
rec.issue_data[701] = issue_data(701, "T-06 do the thing", labels=["harness", "feature:FEAT-02-block"])
rec.issue_data[721] = issue_data(721, "T-09 do the thing", labels=["harness", "feature:FEAT-02-block"])
rec.issue_data[601] = issue_data(601, "T-02", state="CLOSED")
rec.issue_data[602] = issue_data(602, "T-03", state="CLOSED")
rec.issue_data[603] = issue_data(603, "T-04", state="OPEN")
code, out, err = run_main(rec, ["--as", AS_LOGIN])
check("(B4) mixed: skipped, create_ref called once with the clear candidate (#721)",
      code == 0 and rec.create_ref_calls() == [
          ("create_ref", (REPO, "refs/heads/factory/issue-721", "deadbeef")),
      ],
      (code, rec.create_ref_calls()))
check("(B4) stderr names the LAST (open) blocker: T-04 / #603", "T-04" in err and "603" in err,
      err)

rec = Recorder()
rec.items = [board_item("i1", 701, REPO), board_item("i2", 721, REPO)]
rec.issue_data[701] = issue_data(701, "T-06 do the thing", labels=["harness", "feature:FEAT-02-block"])
rec.issue_data[721] = issue_data(721, "T-09 do the thing", labels=["harness", "feature:FEAT-02-block"])
rec.issue_data[601] = issue_data(601, "T-02", state="CLOSED")
rec.issue_data[602] = issue_data(602, "T-03", state="CLOSED")
rec.issue_data[603] = issue_data(603, "T-04", state="CLOSED")
code, out, err = run_main(rec, ["--as", AS_LOGIN])
check("(B4) same fixture, last blocker closed too: candidate IS now claimed",
      code == 0 and json.loads(out).get("issue") == 701, (code, out))

# B5. UNRESOLVABLE BLOCKER — T-10 (issue 710) depends on T-99, absent from the issue map.
rec = Recorder()
rec.items = [board_item("i1", 710, REPO), board_item("i2", 722, REPO)]
rec.issue_data[710] = issue_data(710, "T-10 do the thing", labels=["harness", "feature:FEAT-02-block"])
rec.issue_data[722] = issue_data(722, "T-09 do the thing", labels=["harness", "feature:FEAT-02-block"])
code, out, err = run_main(rec, ["--as", AS_LOGIN])
check("(B5) unresolvable blocker: skipped, not claimed",
      code == 0 and rec.create_ref_calls() == [
          ("create_ref", (REPO, "refs/heads/factory/issue-722", "deadbeef")),
      ],
      (code, rec.create_ref_calls()))
check("(B5) distinct stderr reason naming T-99", "T-99" in err, err)

# B5-bis. EDGE (i) — the feature: label resolves but the title names no plan task the plan
# contains (DESIGN.md C-2 amendment, T-05 intent). Not one of the seven enumerated blocker-gate
# cases, but the intent names edge (i) explicitly and the lead's receipt requires its reason be
# evidenced as distinct — a tool that returns "clear" when the task lookup misses would claim
# #711 here and fail this case.
rec = Recorder()
rec.items = [board_item("i1", 711, REPO), board_item("i2", 723, REPO)]
rec.issue_data[711] = issue_data(
    711, "T-77 a title whose task the plan does not contain",
    labels=["harness", "feature:FEAT-02-block"],
)
rec.issue_data[723] = issue_data(723, "T-09 do the thing", labels=["harness", "feature:FEAT-02-block"])
code, out, err = run_main(rec, ["--as", AS_LOGIN])
check("(B5-bis) edge (i): lost task identity is BLOCKED, not claimed",
      code == 0 and rec.create_ref_calls() == [
          ("create_ref", (REPO, "refs/heads/factory/issue-723", "deadbeef")),
      ],
      (code, rec.create_ref_calls()))
check("(B5-bis) edge (i) reason distinct from open-blocker and unresolvable-blocker reasons",
      "no matching plan task" in err and "still open" not in err
      and "unresolvable blocker" not in err, err)

# B6. FEATURE NULL IS UNGATED — no plan file consulted for it.
load_plan_calls = []
real_load_plan = harness_yaml.load_plan


def recording_load_plan(path):
    load_plan_calls.append(path)
    return real_load_plan(path)


harness_yaml.load_plan = recording_load_plan
try:
    rec = Recorder()
    rec.items = [board_item("i1", 730, REPO)]
    rec.issue_data[730] = issue_data(730, "some mirrored issue", labels=["harness"])
    code, out, err = run_main(rec, ["--as", AS_LOGIN])
finally:
    harness_yaml.load_plan = real_load_plan
check("(B6) feature: null claims normally", code == 0 and json.loads(out).get("feature") is None,
      (code, out))
check("(B6) no plan file was consulted for it", load_plan_calls == [], load_plan_calls)

# B7. --ISSUE ON A BLOCKED ISSUE — not owned: exit 2, zero mutations, no create_ref, stderr
# names the blocking T-NN. Owned (self-ownership): exit 0, re-emits the payload.
rec = Recorder()
rec.items = [board_item("i1", 700, REPO)]
rec.issue_data[700] = blocked_issue_view()
rec.issue_data[601] = issue_data(601, "T-02", state="OPEN")
code, out, err = run_main(rec, ["--as", AS_LOGIN, "--issue", "700"])
check("(B7) fresh --issue on a blocked issue exits 2 (never 3, never 0)", code == 2, code)
check("(B7) zero mutating calls and no create_ref", rec.mutating_calls() == []
      and rec.create_ref_calls() == [], (rec.mutating_calls(), rec.create_ref_calls()))
check("(B7) stderr names the blocking T-02", "T-02" in err, err)

rec = Recorder()
rec.items = [board_item("i1", 700, REPO)]
rec.issue_data[700] = blocked_issue_view(labels_extra=["factory:claimed"])
rec.issue_data[700]["assignees"] = [{"login": AS_LOGIN}]
rec.issue_data[601] = issue_data(601, "T-02", state="OPEN")
code, out, err = run_main(rec, ["--as", AS_LOGIN, "--issue", "700"])
check("(B7) --issue on an issue this agent already owns exits 0, gate never blocks re-entry",
      code == 0 and json.loads(out).get("issue") == 700, (code, out))


# ==========================================================================
# X — SC-13(b) resting condition: "no two of those reasons read alike", asserted directly
# rather than by reading factory_claim.py:277,281,286,302,315. IN-PROCESS, NO subprocess.
#
# THE SET PROVED DISTINCT (named explicitly, per the dispatch): all SEVEN emittable skip-reason
# phrases — the five print sites at :277, :281, :286, :302, :315, where :302's text comes from
# `_blocker_reason_text`'s THREE branches (edge_i, unresolvable, open/blocked-by), each counted
# separately. Five print sites, seven phrases.
#
# THE TRAP: the phrases are inline f-strings carrying the issue number (and, for the blocked-by
# branch, a SECOND embedded number, the blocker's). A pairwise comparison of the raw lines would
# pass no matter what the reasons say, because they always differ by issue number alone. The
# normalisation below strips EVERY `#\d+` and EVERY `issue-\d+` occurrence, not just a leading
# one, so two reasons that differ only by which issue number they carry collapse onto the same
# normalised text and are caught as a collision.
# ==========================================================================

def _normalize_reason(text):
    text = re.sub(r"#\d+", "#N", text)
    text = re.sub(r"issue-\d+", "issue-N", text)
    return text


def sc13b_fixture():
    """One poll where every one of the seven skip reasons fires exactly once, and nothing is
    claimable, so the loop runs to exhaustion and every skip line is emitted."""
    rec = Recorder()
    rec.items = [
        board_item("i1", 901, REPO),  # not open
        board_item("i2", 902, REPO),  # already carries factory:claimed
        board_item("i3", 903, REPO),  # already assigned
        board_item("i4", 904, REPO),  # ref already exists (create_ref False)
        board_item("i5", 905, REPO),  # blocker gate: edge (i), lost task identity
        board_item("i6", 906, REPO),  # blocker gate: unresolvable blocker (T-99)
        board_item("i7", 907, REPO),  # blocker gate: open blocker (T-02, still open)
    ]
    rec.issue_data[901] = issue_data(901, "issue 901", state="CLOSED", labels=["harness"])
    rec.issue_data[902] = issue_data(902, "issue 902", labels=["harness", "factory:claimed"])
    rec.issue_data[903] = issue_data(903, "issue 903", labels=["harness"], assignees=["other"])
    rec.issue_data[904] = issue_data(904, "issue 904", labels=["harness"])
    rec.create_ref_results[904] = False
    rec.issue_data[905] = issue_data(
        905, "T-77 a title whose task the plan does not contain",
        labels=["harness", "feature:FEAT-02-block"],
    )
    rec.issue_data[906] = issue_data(
        906, "T-10 do the thing", labels=["harness", "feature:FEAT-02-block"],
    )
    rec.issue_data[907] = issue_data(
        907, "T-05 do the thing", labels=["harness", "feature:FEAT-02-block"],
    )
    rec.issue_data[601] = issue_data(601, "T-02", state="OPEN")  # T-05's blocker, still open
    return rec


rec = sc13b_fixture()
code, out, err = run_main(rec, ["--as", AS_LOGIN])
check("(X) sc13b fixture: exits 1, nothing claimable", code == 1, code)
check("(X) sc13b fixture: stdout empty", out == "", out)
check("(X) sc13b fixture: zero mutating calls", rec.mutating_calls() == [], rec.mutating_calls())

matches = re.findall(r"skip #(\d+) — (.+)", err)
check("(X) sc13b fixture: exactly seven skip lines fired (fixture didn't silently short-circuit)",
      len(matches) == 7, (len(matches), err))
check("(X) sc13b fixture: the seven skip lines are for exactly issues 901..907",
      {n for n, _ in matches} == {str(n) for n in range(901, 908)}, matches)

reasons = [r for _, r in matches]
normalized = [_normalize_reason(r) for r in reasons]
check(
    "(X) SC-13(b): all seven skip reasons are pairwise distinct after normalising every "
    "embedded issue number, not just a leading one",
    len(set(normalized)) == len(reasons),
    list(zip(reasons, normalized)),
)

# Bonus, not required by the dispatch: normalising T-NN task ids too should not change the
# verdict — the three blocker-gate phrases differ in wording, not merely in which task id they
# name. If this ever goes red it is real signal (two blocker phrases share every word except the
# task id) and should be reported, not silently dropped.
normalized_with_task = [re.sub(r"T-\d+", "T-N", n) for n in normalized]
check(
    "(X) SC-13(b) bonus: still pairwise distinct after ALSO normalising T-NN task ids",
    len(set(normalized_with_task)) == len(reasons),
    list(zip(reasons, normalized_with_task)),
)


# ==========================================================================
# P — per-repository board (FEAT-16 T-02). Everything board-shaped is scoped to one repository
# at a time; these cases prove the scoping actually reaches the gh calls, not just that the tool
# still runs.
# ==========================================================================

# P1. a two-repo fleet on two different board numbers issues its poll query against BOTH boards,
# each with its own station_field and ready option name.
rec = Recorder()
ws = tempfile.mkdtemp(prefix="claim-ws-p1-")
fleet = two_repo_fleet(ws)
rec.board_field_options[(OWNER, BOARD_B)] = {STATION_FIELD_B: ["ReadyB", "BuildingB", "ReviewB"]}
rec.items_by_board[(OWNER, BOARD)] = []
rec.items_by_board[(OWNER, BOARD_B)] = []
code, out, err = run_main(rec, ["--as", AS_LOGIN], fleet_dict=fleet)
poll_calls = [c for c in rec.calls if c[0] == "project_items"]
check("(P1) poll mode queries both boards, not just one",
      {(c[1][0], c[1][1]) for c in poll_calls} == {(OWNER, BOARD), (OWNER, BOARD_B)}, poll_calls)
check("(P1) board A's query is built from board A's own field and ready option",
      any(c[1] == (OWNER, BOARD, f'{STATION_FIELD}:"Ready" is:open') for c in poll_calls),
      poll_calls)
check("(P1) board B's query is built from board B's own field and ready option, not board A's",
      any(c[1] == (OWNER, BOARD_B, f'{STATION_FIELD_B}:"ReadyB" is:open') for c in poll_calls),
      poll_calls)

# P2. a candidate found on repository A is claimed using A's board number, and B's board is
# never addressed by the winner-only bookkeeping (project_field_set).
rec = Recorder()
ws = tempfile.mkdtemp(prefix="claim-ws-p2-")
fleet = two_repo_fleet(ws)
rec.board_field_options[(OWNER, BOARD_B)] = {STATION_FIELD_B: ["ReadyB", "BuildingB", "ReviewB"]}
rec.items_by_board[(OWNER, BOARD)] = [board_item("iA", 200, REPO)]
rec.items_by_board[(OWNER, BOARD_B)] = []
rec.issue_data[200] = issue_data(200, "issue 200", labels=["harness"])
code, out, err = run_main(rec, ["--as", AS_LOGIN], fleet_dict=fleet)
check("(P2) claims #200 on repository A, exit 0",
      code == 0 and json.loads(out).get("issue") == 200, (code, out))
field_set_calls = [c for c in rec.calls if c[0] == "project_field_set"]
check("(P2) exactly one project_field_set call, addressed to A's board and never B's",
      field_set_calls == [("project_field_set", (OWNER, BOARD, "iA", STATION_FIELD, "Building"))],
      field_set_calls)

# P3. station validation failing for repository B still names B's board number in the refusal —
# repository A's board validates cleanly.
rec = Recorder()
ws = tempfile.mkdtemp(prefix="claim-ws-p3-")
fleet = two_repo_fleet(ws)
rec.board_field_options[(OWNER, BOARD)] = {STATION_FIELD: ["Ready", "Building", "Review"]}
rec.board_field_options[(OWNER, BOARD_B)] = {STATION_FIELD_B: ["ReadyB", "BuildingB"]}  # no ReviewB
code, out, err = run_main(rec, ["--as", AS_LOGIN], fleet_dict=fleet)
check("(P3) exits 2 (refused)", code == 2, code)
check("(P3) refusal names board B's board number", f"{OWNER} project {BOARD_B}" in err, err)
check("(P3) refusal does NOT name board A's board number", f"{OWNER} project {BOARD}" not in err,
      err)

# P4. --repo filters the served set to one repository, so only that repository's board is read
# at all — never the other fleet member's.
rec = Recorder()
ws = tempfile.mkdtemp(prefix="claim-ws-p4-")
fleet = two_repo_fleet(ws)
rec.items_by_board[(OWNER, BOARD)] = []
code, out, err = run_main(rec, ["--as", AS_LOGIN, "--repo", REPO], fleet_dict=fleet)
check("(P4) --repo REPO exits 1, no work on that repo's board", code == 1, code)
board_reads = [c for c in rec.calls if c[0] in ("project_field_options", "project_items")]
check("(P4) --repo filters the served set: every board read names A's board, none names B's",
      board_reads != [] and all(c[1][0] == OWNER and c[1][1] == BOARD for c in board_reads),
      board_reads)

# P5. two fleet entries declaring the SAME board number produce exactly one candidate per issue —
# the claimed issue gets exactly one project_field_set call despite the duplicate.
rec = Recorder()
ws = tempfile.mkdtemp(prefix="claim-ws-p5-")
fleet = same_board_two_repo_fleet(ws)
rec.items = [board_item("i1", 300, REPO)]
rec.issue_data[300] = issue_data(300, "issue 300", labels=["harness"])
code, out, err = run_main(rec, ["--as", AS_LOGIN], fleet_dict=fleet)
check("(P5) claims #300 exactly once, exit 0",
      code == 0 and json.loads(out).get("issue") == 300, (code, out))
p5_poll_calls = [c for c in rec.calls if c[0] == "project_items"]
check("(P5) both fleet entries query the shared board (two project_items calls recorded)",
      len(p5_poll_calls) == 2, p5_poll_calls)
p5_issue_view_calls = [c for c in rec.calls if c[0] == "issue_view"]
check("(P5) issue_view runs exactly once for #300 — the duplicate never entered the candidate loop",
      len(p5_issue_view_calls) == 1, p5_issue_view_calls)
p5_field_set_calls = [c for c in rec.calls if c[0] == "project_field_set"]
check("(P5) exactly one project_field_set call despite the duplicate", len(p5_field_set_calls) == 1,
      p5_field_set_calls)

# P6. SC-13's SOLE EVIDENCE — a two-repository fleet on two different board numbers, --repo
# names the one whose ready station returns NO items: stdout stays empty, stderr carries
# "no work available", exit code is 1 (EXIT_NOTHING). The mutant this guards against is a
# per-repository loop that treats an empty repository as a "continue" and falls off the end of
# the served set into a normal exit 0 — silence where a report belongs.
rec = Recorder()
ws = tempfile.mkdtemp(prefix="claim-ws-p6-")
fleet = two_repo_fleet(ws)
rec.board_field_options[(OWNER, BOARD_B)] = {STATION_FIELD_B: ["ReadyB", "BuildingB", "ReviewB"]}
rec.items_by_board[(OWNER, BOARD_B)] = []
code, out, err = run_main(rec, ["--as", AS_LOGIN, "--repo", REPO_B], fleet_dict=fleet)
check("(P6) SC-13: --repo on the sole served repository's empty ready station: stdout is empty",
      out == "", out)
check("(P6) SC-13: stderr carries 'no work available'", "no work available" in err, err)
check("(P6) SC-13: exit code is EXIT_NOTHING (1), not a silent 0",
      code == factory_cli.EXIT_NOTHING, code)


print(f"\n{RAN - FAILS}/{RAN} checks passed." if FAILS == 0 else f"\n{FAILS} of {RAN} FAILING.")
sys.exit(1 if FAILS else 0)
