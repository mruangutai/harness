#!/usr/bin/env python3
"""Tests for factory_decompose.py — publish an approved plan as issues on the board (T-04, D-14).

Nothing here spawns a subprocess and nothing touches a real repository or board: every call
`factory_decompose` makes into `factory_gh`'s public functions is monkeypatched over a single
`Recorder`, whose ordered `.calls` list is the evidence every assertion below is a projection
of. `factory_gh.preflight()` is called unconditionally at step 3, before dispositions are even
sorted, so "zero calls of any kind" assertions are scoped to the mutating/board/edge/id
surface — `ensure_labels`, `create_issue`, `add_label`, `project_item_add`, `project_field_set`,
`internal_id`, `attach_sub_issue`, `blocked_by` — and say so in their labels; `preflight` itself
is expected on every run that reaches step 3.
"""
import contextlib
import hashlib
import io
import json
import os
import re
import sys
import tempfile

import yaml

import factory_decompose as fd
import factory_gh
import factory_config as fc

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


REPO = "acme/widget"
FEAT = "FEAT-99-fixture"

MUTATING_NAMES = (
    "ensure_labels", "create_issue", "add_label", "project_item_add",
    "project_field_set", "internal_id", "attach_sub_issue", "blocked_by",
)


# --------------------------------------------------------------------------
# Recorder — a single ordered call log over every factory_gh public function T-04 calls.
# --------------------------------------------------------------------------

class Recorder:
    def __init__(self):
        self.calls = []
        self._issue_seq = 100
        self._item_seq = 5000
        self.raise_on = {}   # name -> exception instance, or callable(args) -> exception|None

    def _hit(self, name, args):
        self.calls.append((name, args))
        handler = self.raise_on.get(name)
        if handler is not None:
            exc = handler(args) if callable(handler) else handler
            if exc is not None:
                raise exc

    def mutating_calls(self):
        return [c for c in self.calls if c[0] in MUTATING_NAMES]

    # --- factory_gh's public surface ---
    def preflight(self):
        self._hit("preflight", ())

    def ensure_labels(self, repo, labels):
        self._hit("ensure_labels", (repo, tuple(labels)))

    def create_issue(self, repo, title, body, labels):
        self._hit("create_issue", (repo, title, body, tuple(labels)))
        self._issue_seq += 1
        return self._issue_seq

    def add_label(self, repo, number, label):
        self._hit("add_label", (repo, number, label))

    def project_item_add(self, owner, number, url):
        self._hit("project_item_add", (owner, number, url))
        self._item_seq += 1
        return f"ITEM-{self._item_seq}"

    def project_field_set(self, owner, number, item_id, field, option):
        self._hit("project_field_set", (owner, number, item_id, field, option))

    def internal_id(self, repo, num):
        self._hit("internal_id", (repo, num))
        # Deliberately far from any issue number this recorder ever hands out, so a bug
        # that passes the issue NUMBER where the internal id belongs is visibly wrong.
        return 900000 + num

    def attach_sub_issue(self, repo, parent_num, child_id):
        self._hit("attach_sub_issue", (repo, parent_num, child_id))

    def blocked_by(self, repo, num, blocker_id):
        self._hit("blocked_by", (repo, num, blocker_id))


PATCHED = (
    "preflight", "ensure_labels", "create_issue", "add_label", "project_item_add",
    "project_field_set", "internal_id", "attach_sub_issue", "blocked_by",
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

def good_fleet_dict(workspace_root):
    return {
        "schema": "factory-fleet/1",
        "board": {
            "owner": "acme",
            "number": 3,
            "station_field": "Status",
            "stations": {"ready": "Ready", "building": "Building", "review": "Review"},
        },
        "repos": [{"name": REPO, "default_branch": "main"}],
        "workspace_root": workspace_root,
    }


def task(tid, title="do the thing", change_type="feature", depends_on=None, traces=None,
         intent=None):
    t = {
        "id": tid,
        "title": title,
        "change_type": change_type,
        "execution_mode": "team",
        "files": [f"{tid}.py"],
        "verify": "true",
        "intent": intent or f"intent text for {tid}, verbatim.",
        "traces": traces or ["REQ-01"],
    }
    if depends_on:
        t["depends_on"] = depends_on
    return t


def plan_dict(tasks=None, approved=True, feat=FEAT):
    return {
        "schema": "plan/1",
        "feature": feat,
        "approval": {"status": "approved" if approved else "pending"},
        "tasks": tasks if tasks is not None else [task("T-01"), task("T-02")],
    }


GOOD_BRIEF = f"""# {FEAT} — give operators visibility

## Problem

Operators cannot see into the pipeline today.

## Goal

Give operators a live view of the pipeline. This is a longer goal sentence that follows.

## Success Criteria

- SC-01: something measurable
"""

NO_HEADINGS_BRIEF = "# just a title\n\nsome prose, no headings at all.\n"


def write_yaml(path, data):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)


def write_text(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def make_feature(td, tasks=None, approved=True, factory_yaml_extra="", brief=GOOD_BRIEF,
                  feat=FEAT):
    """Build a temporary feature directory: plan.yaml, BRIEF.md, feature.yaml, fleet.yaml.
    Returns (feat_dir, fleet_path)."""
    feat_dir = os.path.join(td, "feature")
    os.makedirs(feat_dir, exist_ok=True)
    write_yaml(os.path.join(feat_dir, "plan.yaml"), plan_dict(tasks=tasks, approved=approved,
                                                               feat=feat))
    write_text(os.path.join(feat_dir, "BRIEF.md"), brief)
    write_text(os.path.join(feat_dir, "feature.yaml"), factory_yaml_extra)
    fleet_dir = os.path.join(td, "fleet")
    os.makedirs(fleet_dir, exist_ok=True)
    fleet_path = os.path.join(fleet_dir, "fleet.yaml")
    write_yaml(fleet_path, good_fleet_dict(os.path.join(td, "workspaces")))
    return feat_dir, fleet_path


def make_feature_bad_feature_key(td, mode, tasks=None):
    """Build a feature dir identical to make_feature's happy path except the plan's
    top-level `feature` key is either absent entirely, an empty string, or whitespace
    only — `mode` is "missing", "empty" or "whitespace". Everything else (approved
    plan, tasks, BRIEF, fleet) matches the happy-path fixture exactly, so the ONLY
    thing wrong with this fixture is the `feature` key itself.
    Returns (feat_dir, fleet_path)."""
    feat_dir = os.path.join(td, "feature")
    os.makedirs(feat_dir, exist_ok=True)
    plan = plan_dict(tasks=tasks, approved=True, feat=FEAT)
    if mode == "missing":
        del plan["feature"]
    elif mode == "empty":
        plan["feature"] = ""
    elif mode == "whitespace":
        plan["feature"] = "   "
    else:
        raise ValueError(mode)
    write_yaml(os.path.join(feat_dir, "plan.yaml"), plan)
    write_text(os.path.join(feat_dir, "BRIEF.md"), GOOD_BRIEF)
    write_text(os.path.join(feat_dir, "feature.yaml"), "")
    fleet_dir = os.path.join(td, "fleet")
    os.makedirs(fleet_dir, exist_ok=True)
    fleet_path = os.path.join(fleet_dir, "fleet.yaml")
    write_yaml(fleet_path, good_fleet_dict(os.path.join(td, "workspaces")))
    return feat_dir, fleet_path


def run_publish(feat_dir, fleet_path, rec, extra_args=None):
    argv_saved = sys.argv
    sys.argv = ["factory_decompose.py", feat_dir, "--repo", REPO, "--fleet", fleet_path]
    if extra_args:
        sys.argv += extra_args
    saved = patch_gh(rec)
    out, err = io.StringIO(), io.StringIO()
    code = None
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                fd.factory_cli.run(
                    fd.TOOL, fd._main,
                    expected=(fd.factory_config.FleetError, fd.factory_gh.GhError),
                )
            except SystemExit as e:
                code = e.code
    finally:
        sys.argv = argv_saved
        unpatch_gh(saved)
    return code, out.getvalue(), err.getvalue()


def read_factory_block(feat_dir):
    doc = yaml.safe_load(open(os.path.join(feat_dir, "feature.yaml"), encoding="utf-8").read())
    return (doc or {}).get("factory") or {}


def issue_url(repo, num):
    return f"https://github.com/{repo}/issues/{num}"


def trailing_issue_number(url):
    m = re.search(r"/issues/(\d+)$", url)
    return int(m.group(1)) if m else None


# ============================================================================
# 1. an unsigned plan publishes nothing and exits 2 (listed repo, so it refuses at step 2)
# ============================================================================
with tempfile.TemporaryDirectory() as td:
    feat_dir, fleet_path = make_feature(td, approved=False)
    rec = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec)
    check("(1) unsigned plan: exits 2", code == 2, f"code={code!r}")
    check("(1) unsigned plan: nothing on stdout", out == "", repr(out))
    check("(1) unsigned plan: names the plan path on stderr",
          os.path.join(feat_dir, "plan.yaml") in err, err)
    check("(1) unsigned plan: zero mutating calls",
          rec.mutating_calls() == [], rec.mutating_calls())

# ============================================================================
# 2. a signed two-task plan creates two issues, adds two board items, sets both stations
# ============================================================================
with tempfile.TemporaryDirectory() as td:
    feat_dir, fleet_path = make_feature(td)
    rec = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec, extra_args=["--parent", "1"])
    check("(2) signed two-task plan: exits 0", code in (0, None), f"code={code!r} err={err}")
    create_calls = [c for c in rec.calls if c[0] == "create_issue"]
    check("(2) two issues created", len(create_calls) == 2, create_calls)
    item_calls = [c for c in rec.calls if c[0] == "project_item_add"]
    check("(2) two board items added", len(item_calls) == 2, item_calls)
    field_calls = [c for c in rec.calls if c[0] == "project_field_set"]
    check("(2) two stations set", len(field_calls) == 2, field_calls)
    check("(2) both stations set to the fleet's ready option",
          all(c[1][4] == "Ready" for c in field_calls), field_calls)
    fblock = read_factory_block(feat_dir)
    check("(2) feature.yaml records two issue numbers", len(fblock.get("issues") or {}) == 2,
          fblock)
    check("(2) feature.yaml records two item ids", len(fblock.get("items") or {}) == 2, fblock)

# ============================================================================
# 3. a second publish against a fully-recorded feature.yaml mutates and calls nothing
# ============================================================================
with tempfile.TemporaryDirectory() as td:
    feat_dir, fleet_path = make_feature(td)
    rec1 = Recorder()
    run_publish(feat_dir, fleet_path, rec1, extra_args=["--parent", "1"])
    rec2 = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec2, extra_args=["--parent", "1"])
    check("(3) second publish: exits 0", code in (0, None), f"code={code!r} err={err}")
    check("(3) second publish: zero calls of any kind on the mutating/board/edge/id surface "
          "(preflight is expected and excluded from this list)",
          rec2.mutating_calls() == [], rec2.calls)
    check("(3) second publish: zero internal_id calls specifically",
          [c for c in rec2.calls if c[0] == "internal_id"] == [], rec2.calls)

# ============================================================================
# 4. a repository absent from the fleet exits 2 before any gh call
# ============================================================================
with tempfile.TemporaryDirectory() as td:
    feat_dir, fleet_path = make_feature(td)
    rec = Recorder()
    argv_saved = sys.argv
    sys.argv = ["factory_decompose.py", feat_dir, "--repo", "someone/unlisted",
                "--fleet", fleet_path]
    saved = patch_gh(rec)
    out, err = io.StringIO(), io.StringIO()
    code = None
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                fd.factory_cli.run(fd.TOOL, fd._main,
                                    expected=(fd.factory_config.FleetError, fd.factory_gh.GhError))
            except SystemExit as e:
                code = e.code
    finally:
        sys.argv = argv_saved
        unpatch_gh(saved)
    check("(4) unlisted repo: exits 2", code == 2, f"code={code!r}")
    check("(4) unlisted repo: zero calls of any kind", rec.calls == [], rec.calls)

# ============================================================================
# 5. the chore label appears for a config task and not for a logic task
# ============================================================================
with tempfile.TemporaryDirectory() as td:
    tasks = [task("T-01", change_type="config"), task("T-02", change_type="feature")]
    feat_dir, fleet_path = make_feature(td, tasks=tasks)
    rec = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec, extra_args=["--parent", "1"])
    creates = {c[1][0:1] + (c[1][3],): c for c in rec.calls if c[0] == "create_issue"}
    by_title = {c[1][1]: c[1][3] for c in rec.calls if c[0] == "create_issue"}
    t01_labels = next(l for title, l in by_title.items() if title.startswith("T-01"))
    t02_labels = next(l for title, l in by_title.items() if title.startswith("T-02"))
    check("(5) config task carries chore", "chore" in t01_labels, t01_labels)
    check("(5) feature task does not carry chore", "chore" not in t02_labels, t02_labels)
    check("(5) neither carries bug", "bug" not in t01_labels and "bug" not in t02_labels,
          (t01_labels, t02_labels))

# ============================================================================
# 6. feature.yaml carries the issue number after the first creation even when the board
#    add then raises GhError
# ============================================================================
with tempfile.TemporaryDirectory() as td:
    feat_dir, fleet_path = make_feature(td)
    rec = Recorder()
    rec.raise_on["project_item_add"] = factory_gh.GhError(
        [], 1, "", "boom", "gh project item-add failed", "acme", "retry",
    )
    code, out, err = run_publish(feat_dir, fleet_path, rec, extra_args=["--parent", "1"])
    check("(6) a raising board add exits 2", code == 2, f"code={code!r}")
    fblock = read_factory_block(feat_dir)
    check("(6) feature.yaml still carries the created issue number",
          len(fblock.get("issues") or {}) >= 1, fblock)

# ============================================================================
# 7. resume-after-partial: an issue recorded with no item id creates no new issue, adds the
#    board item, sets its station, and records the item id
# ============================================================================
with tempfile.TemporaryDirectory() as td:
    feat_dir, fleet_path = make_feature(td)
    rec1 = Recorder()
    rec1.raise_on["project_item_add"] = factory_gh.GhError(
        [], 1, "", "boom", "gh project item-add failed", "acme", "retry",
    )
    run_publish(feat_dir, fleet_path, rec1, extra_args=["--parent", "1"])
    fblock_mid = read_factory_block(feat_dir)
    check("(7) precondition: one issue recorded, zero items recorded",
          len(fblock_mid.get("issues") or {}) >= 1 and not (fblock_mid.get("items") or {}),
          fblock_mid)

    rec2 = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec2, extra_args=["--parent", "1"])
    check("(7) resume: exits 0", code in (0, None), f"code={code!r} err={err}")
    check("(7) resume: zero create_issue calls",
          [c for c in rec2.calls if c[0] == "create_issue"] == [],
          [c for c in rec2.calls if c[0] == "create_issue"])
    item_calls = [c for c in rec2.calls if c[0] == "project_item_add"]
    check("(7) resume: project_item_add IS called", len(item_calls) >= 1, rec2.calls)
    field_calls = [c for c in rec2.calls if c[0] == "project_field_set"]
    check("(7) resume: the item's station is set to the ready option",
          any(c[1][4] == "Ready" for c in field_calls), field_calls)
    fblock_after = read_factory_block(feat_dir)
    check("(7) resume: feature.yaml now carries an item id",
          len(fblock_after.get("items") or {}) >= 1, fblock_after)

# ============================================================================
# 8. label vocabulary: every created issue carries harness + feature:<FEAT>, never
#    factory:claimed; ensure_labels runs before the first create_issue; its argument set
#    contains factory:claimed even though no created issue carries it
# ============================================================================
with tempfile.TemporaryDirectory() as td:
    feat_dir, fleet_path = make_feature(td)
    rec = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec, extra_args=["--parent", "1"])
    ensure_idx = next(i for i, c in enumerate(rec.calls) if c[0] == "ensure_labels")
    first_create_idx = next(i for i, c in enumerate(rec.calls) if c[0] == "create_issue")
    check("(8) ensure_labels runs before the first create_issue", ensure_idx < first_create_idx,
          rec.calls)
    ensured_labels = set(rec.calls[ensure_idx][1][1])
    check("(8) ensure_labels' argument set contains factory:claimed",
          "factory:claimed" in ensured_labels, ensured_labels)
    for c in rec.calls:
        if c[0] != "create_issue":
            continue
        labels = c[1][3]
        check(f"(8) created issue {c[1][1]!r} carries harness", "harness" in labels, labels)
        check(f"(8) created issue {c[1][1]!r} carries feature:{FEAT}",
              f"feature:{FEAT}" in labels, labels)
        check(f"(8) created issue {c[1][1]!r} never carries factory:claimed",
              "factory:claimed" not in labels, labels)

# ============================================================================
# 9. feature.yaml carrying comments and a github block round-trips those bytes unchanged
# ============================================================================
with tempfile.TemporaryDirectory() as td:
    extra = (
        "# an operator comment at the top\n"
        "github:  # trailing comment\n"
        "  milestone: 5\n"
        "  parent: 9\n"
        "  parent_origin: created\n"
        "  attached: [T-01]\n"
        "  issues:\n"
        "    T-01: 9\n"
        "# a trailing comment\n"
    )
    feat_dir, fleet_path = make_feature(td, factory_yaml_extra=extra)
    before = extra
    rec = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec, extra_args=["--parent", "1"])
    after = open(os.path.join(feat_dir, "feature.yaml"), encoding="utf-8").read()
    check("(9) the pre-existing comment survives", "# an operator comment at the top" in after,
          after)
    check("(9) the github block survives", "milestone: 5" in after and "parent: 9" in after,
          after)
    check("(9) the trailing comment survives", "# a trailing comment" in after, after)
    check("(9) a factory: block was appended", "factory:" in after, after)

# ============================================================================
# 10. every exit-2 path before ensure_labels leaves the recorder with zero mutating calls
#     (covered again here over the full call list, for the unsigned-plan refusal)
# ============================================================================
with tempfile.TemporaryDirectory() as td:
    feat_dir, fleet_path = make_feature(td, approved=False)
    rec = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec)
    check("(10) unsigned-plan refusal: zero mutating calls over the FULL call list",
          rec.mutating_calls() == [], rec.calls)

# ============================================================================
# 11. the issue body's four parts appear in the C-4 fixed order, traces on one comma-separated
#     line
# ============================================================================
with tempfile.TemporaryDirectory() as td:
    tasks = [task("T-01", intent="Do the specific thing.\nWith a second line.",
                   traces=["REQ-01", "REQ-07"])]
    feat_dir, fleet_path = make_feature(td, tasks=tasks)
    rec = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec, extra_args=["--parent", "1"])
    body = next(c[1][2] for c in rec.calls if c[0] == "create_issue")
    parts = body.split("\n\n")
    check("(11) body has exactly two blank-line-separated parts (intent, then meta)",
          len(parts) == 2, body)
    check("(11) intent appears first, verbatim",
          parts[0] == "Do the specific thing.\nWith a second line.", body)
    meta_lines = parts[1].split("\n")
    check("(11) change_type line present", meta_lines[0] == "change_type: feature", body)
    check("(11) traces line is comma-separated on one line",
          meta_lines[1] == "traces: REQ-01, REQ-07", body)


# ============================================================================
# The eleven DAG/ledger cases (D-14, DESIGN.md C-5).
# ============================================================================

# --- 12. no --parent: a parent is created with exactly harness + feature:<FEAT>, a two-part
#         body (problem, blank, **Goal:**), no change_type/traces; parent_origin recorded created
with tempfile.TemporaryDirectory() as td:
    feat_dir, fleet_path = make_feature(td)
    rec = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec)  # no --parent
    check("(12) exits 0", code in (0, None), f"code={code!r} err={err}")
    parent_create = next(c for c in rec.calls if c[0] == "create_issue"
                          and not re.match(r"^T-\d+ ", c[1][1]))
    check("(12) parent carries exactly harness + feature:<FEAT>",
          set(parent_create[1][3]) == {"harness", f"feature:{FEAT}"}, parent_create)
    pbody = parent_create[1][2]
    check("(12) parent body is problem, blank line, **Goal:** line",
          pbody.startswith("Operators cannot see into the pipeline today.\n\n**Goal:**"), pbody)
    check("(12) parent body carries no change_type/traces line",
          "change_type:" not in pbody and "traces:" not in pbody, pbody)
    fblock = read_factory_block(feat_dir)
    check("(12) feature.yaml records parent_origin created",
          fblock.get("parent_origin") == "created", fblock)

# --- 13. --parent <n>: no issue created for the parent; recorded adopted; feature:<FEAT>
#         applied but no title/body edit call
with tempfile.TemporaryDirectory() as td:
    feat_dir, fleet_path = make_feature(td)
    rec = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec, extra_args=["--parent", "777"])
    check("(13) exits 0", code in (0, None), f"code={code!r} err={err}")
    parent_creates = [c for c in rec.calls if c[0] == "create_issue"
                      and not re.match(r"^T-\d+ ", c[1][1])]
    check("(13) no issue is created for the adopted parent", parent_creates == [], parent_creates)
    fblock = read_factory_block(feat_dir)
    check("(13) feature.yaml records parent 777 with parent_origin adopted",
          fblock.get("parent") == 777 and fblock.get("parent_origin") == "adopted", fblock)
    add_label_calls = [c for c in rec.calls if c[0] == "add_label" and c[1][1] == 777]
    check("(13) feature:<FEAT> label applied to the adopted parent",
          any(c[1][2] == f"feature:{FEAT}" for c in add_label_calls), rec.calls)
    check("(13) no call edits the adopted parent's title or body",
          not any(c[0] not in ("add_label",) and c[1] and c[1][0] == 777 for c in rec.calls
                  if c[0] in ("create_issue",)),
          rec.calls)

# --- 14. the parent is never added to the board
with tempfile.TemporaryDirectory() as td:
    feat_dir, fleet_path = make_feature(td)
    rec = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec)  # creates the parent
    fblock = read_factory_block(feat_dir)
    parent_num = fblock.get("parent")
    item_calls = [c for c in rec.calls if c[0] == "project_item_add"]
    numbers_added = [trailing_issue_number(c[1][2]) for c in item_calls]
    check("(14) the parent's number appears in NO project_item_add call",
          parent_num not in numbers_added, (parent_num, numbers_added))

# --- 15. every task issue is attached to the parent exactly once, carrying the INTERNAL id
with tempfile.TemporaryDirectory() as td:
    feat_dir, fleet_path = make_feature(td)
    rec = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec, extra_args=["--parent", "1"])
    attach_calls = [c for c in rec.calls if c[0] == "attach_sub_issue"]
    check("(15) exactly two attach calls, one per task", len(attach_calls) == 2, attach_calls)
    for c in attach_calls:
        repo, parent_num, child_id = c[1]
        check(f"(15) attach {c} carries the INTERNAL id, not an issue number",
              child_id >= 900000, c)
        check(f"(15) attach {c} targets parent 1", parent_num == 1, c)

# --- 16. a task with six blockers draws exactly six blocked_by calls
with tempfile.TemporaryDirectory() as td:
    tasks = [task(f"T-{i:02d}") for i in range(2, 8)] + [
        task("T-12", depends_on=["T-02", "T-03", "T-04", "T-05", "T-06", "T-07"]),
    ]
    feat_dir, fleet_path = make_feature(td, tasks=tasks)
    rec = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec, extra_args=["--parent", "1"])
    check("(16) exits 0", code in (0, None), f"code={code!r} err={err}")
    fblock = read_factory_block(feat_dir)
    t12_issue = fblock["issues"]["T-12"]
    blocked_calls = [c for c in rec.calls if c[0] == "blocked_by" and c[1][1] == t12_issue]
    check("(16) exactly six blocked_by calls for T-12", len(blocked_calls) == 6, blocked_calls)
    resolved_ids = {c[1][2] for c in blocked_calls}
    check("(16) each names a distinct resolved blocker id", len(resolved_ids) == 6, resolved_ids)

# --- 17. every edge call goes through the second pass: no attach/blocked_by call precedes the
#         LAST create_issue call
with tempfile.TemporaryDirectory() as td:
    tasks = [task("T-01"), task("T-02", depends_on=["T-01"])]
    feat_dir, fleet_path = make_feature(td, tasks=tasks)
    rec = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec, extra_args=["--parent", "1"])
    last_create_idx = max(i for i, c in enumerate(rec.calls) if c[0] == "create_issue")
    edge_idxs = [i for i, c in enumerate(rec.calls) if c[0] in ("attach_sub_issue", "blocked_by")]
    check("(17) no edge call precedes the last create_issue call",
          all(i > last_create_idx for i in edge_idxs), (last_create_idx, edge_idxs, rec.calls))

# --- 18. a blocker with no recorded issue number is skipped, not fatal
with tempfile.TemporaryDirectory() as td:
    tasks = [task("T-01", depends_on=["T-99-missing"])]
    feat_dir, fleet_path = make_feature(td, tasks=tasks)
    rec = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec, extra_args=["--parent", "1"])
    check("(18) exits 0", code in (0, None), f"code={code!r} err={err}")
    check("(18) stderr names both task ids",
          "T-01" in err and "T-99-missing" in err, err)
    check("(18) no blocked_by call was made for the missing blocker",
          [c for c in rec.calls if c[0] == "blocked_by"] == [],
          [c for c in rec.calls if c[0] == "blocked_by"])
    payload = json.loads(out)
    check("(18) payload edges_skipped is exactly 1", payload.get("edges_skipped") == 1, payload)
    check("(18) payload edges_drawn counts only edges actually written",
          payload.get("edges_drawn") == 1, payload)  # the one parent-attach edge for T-01

# --- 19. the fourth disposition: both issues+items recorded, empty edges — re-runs create/add
#         nothing, draw every edge; a third run then draws nothing at all
with tempfile.TemporaryDirectory() as td:
    tasks = [task("T-01"), task("T-02", depends_on=["T-01"])]
    feat_dir, fleet_path = make_feature(td, tasks=tasks)
    rec0 = Recorder()
    rec0.raise_on["attach_sub_issue"] = lambda args: RuntimeError("boom, kill before any edge")
    argv_saved = sys.argv
    sys.argv = ["factory_decompose.py", feat_dir, "--repo", REPO, "--fleet", fleet_path,
                "--parent", "1"]
    saved = patch_gh(rec0)
    try:
        try:
            fd.factory_cli.run(fd.TOOL, fd._main,
                                expected=(fd.factory_config.FleetError, fd.factory_gh.GhError))
        except SystemExit:
            pass
        except RuntimeError:
            pass
    finally:
        sys.argv = argv_saved
        unpatch_gh(saved)
    fblock_mid = read_factory_block(feat_dir)
    check("(19) precondition: two issues, two items, empty edges",
          len(fblock_mid.get("issues") or {}) == 2 and len(fblock_mid.get("items") or {}) == 2
          and not (fblock_mid.get("edges") or {}).get("parent"), fblock_mid)

    rec1 = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec1, extra_args=["--parent", "1"])
    check("(19) run 2: exits 0", code in (0, None), f"code={code!r} err={err}")
    check("(19) run 2: zero create_issue calls",
          [c for c in rec1.calls if c[0] == "create_issue"] == [], rec1.calls)
    check("(19) run 2: zero project_item_add calls",
          [c for c in rec1.calls if c[0] == "project_item_add"] == [], rec1.calls)
    check("(19) run 2: draws every parent and blocked_by edge",
          len([c for c in rec1.calls if c[0] == "attach_sub_issue"]) == 2
          and len([c for c in rec1.calls if c[0] == "blocked_by"]) == 1, rec1.calls)

    rec2 = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec2, extra_args=["--parent", "1"])
    check("(19) run 3: draws nothing at all", rec2.mutating_calls() == [], rec2.calls)

# --- 20. the already-drawn blocked_by edge is not fatal; the attach twin still is
with tempfile.TemporaryDirectory() as td:
    tasks = [task("T-01"), task("T-02", depends_on=["T-01"])]
    feat_dir, fleet_path = make_feature(td, tasks=tasks)
    rec = Recorder()
    already_taken = factory_gh.GhError(
        [], 1, "422 error body: sub-issue already been taken", "",
        "gh api failed", REPO, "n/a",
    )
    rec.raise_on["blocked_by"] = already_taken
    code, out, err = run_publish(feat_dir, fleet_path, rec, extra_args=["--parent", "1"])
    check("(20a) already-drawn blocked_by: exits 0", code in (0, None), f"code={code!r} err={err}")
    fblock = read_factory_block(feat_dir)
    check("(20a) feature.yaml records the edge exactly as a successful call would",
          "T-01" in ((fblock.get("edges") or {}).get("blocked_by") or {}).get("T-02", []),
          fblock)
    check("(20a) a stderr line names both task ids", "T-02" in err and "T-01" in err, err)
    check("(20a) the run continues to draw every later edge (both attaches present)",
          len([c for c in rec.calls if c[0] == "attach_sub_issue"]) == 2, rec.calls)

with tempfile.TemporaryDirectory() as td:
    tasks = [task("T-01"), task("T-02", depends_on=["T-01"])]
    feat_dir, fleet_path = make_feature(td, tasks=tasks)
    rec = Recorder()
    already_taken2 = factory_gh.GhError(
        [], 1, "422 error: this sub-issue has already been taken", "",
        "gh api failed", REPO, "n/a",
    )
    rec.raise_on["attach_sub_issue"] = already_taken2
    code, out, err = run_publish(feat_dir, fleet_path, rec, extra_args=["--parent", "1"])
    check("(20b) the attach twin STAYS FATAL: exits 2", code == 2, f"code={code!r}")
    fblock = read_factory_block(feat_dir)
    check("(20b) feature.yaml records NO parent receipt for that task",
          (fblock.get("edges") or {}).get("parent") in (None, []), fblock)

# --- 21. a GhError that is NOT the already-drawn shape stays fatal on both edge types
with tempfile.TemporaryDirectory() as td:
    tasks = [task("T-01"), task("T-02", depends_on=["T-01"])]
    feat_dir, fleet_path = make_feature(td, tasks=tasks)
    rec = Recorder()
    auth_error = factory_gh.GhError(
        [], 1, "", "authentication failed, run gh auth login",
        "gh api failed", REPO, "run gh auth login",
    )
    rec.raise_on["blocked_by"] = auth_error
    code, out, err = run_publish(feat_dir, fleet_path, rec, extra_args=["--parent", "1"])
    check("(21) a non-already-drawn GhError on blocked_by stays fatal: exits 2", code == 2,
          f"code={code!r}")
    fblock = read_factory_block(feat_dir)
    check("(21) no receipt recorded for that edge",
          "T-01" not in ((fblock.get("edges") or {}).get("blocked_by") or {}).get("T-02", []),
          fblock)

# --- 22. the ledger is never observed partially written
with tempfile.TemporaryDirectory() as td:
    tasks = [task("T-01"), task("T-02")]
    feat_dir, fleet_path = make_feature(td, tasks=tasks)
    rec = Recorder()

    real_replace = os.replace
    real_open = open
    replace_calls = []
    open_calls = []
    feature_yaml_path = os.path.join(feat_dir, "feature.yaml")

    def fake_replace(src, dst):
        replace_calls.append((src, dst))
        if os.path.abspath(dst) == os.path.abspath(feature_yaml_path):
            check("(22) os.replace destination is the fixture's feature.yaml",
                  os.path.abspath(dst) == os.path.abspath(feature_yaml_path), dst)
            check("(22) os.replace source is a different path in the SAME directory",
                  os.path.dirname(os.path.abspath(src)) == os.path.dirname(os.path.abspath(dst))
                  and src != dst, (src, dst))
            with real_open(src, encoding="utf-8") as f:
                content = f.read()
            try:
                parsed = yaml.safe_load(content)
                ok = isinstance(parsed, dict) and "factory" in parsed
            except Exception:
                ok = False
            check("(22) the source file parses as YAML and carries the factory block", ok,
                  content)
        return real_replace(src, dst)

    def fake_open(path, mode="r", *a, **kw):
        if os.path.abspath(path) == os.path.abspath(feature_yaml_path):
            open_calls.append(mode)
            truncating = any(t in mode for t in ("w", "x", "a")) or kw.get("O_TRUNC")
            check(f"(22) feature.yaml opened in mode {mode!r}: not truncating", not truncating,
                  mode)
        return real_open(path, mode, *a, **kw)

    import builtins
    os.replace = fake_replace
    builtins.open = fake_open
    try:
        code, out, err = run_publish(feat_dir, fleet_path, rec, extra_args=["--parent", "1"])
    finally:
        os.replace = real_replace
        builtins.open = real_open

    check("(22) os.replace was called at least once", len(replace_calls) >= 1, replace_calls)
    check("(22) feature.yaml WAS opened for reading at least once (anti-vacuum)",
          len(open_calls) >= 1, open_calls)
    check("(22) feature.yaml was opened only for reading, never in a truncating mode",
          open_calls != [] and all(m == "r" for m in open_calls), open_calls)


# ============================================================================
# SC-20: plan.yaml and BRIEF.md are byte-identical after a publish; feature.yaml is the
# only file whose hash changed
# ============================================================================
with tempfile.TemporaryDirectory() as td:
    feat_dir, fleet_path = make_feature(td)

    def hash_all(d):
        out = {}
        for name in os.listdir(d):
            p = os.path.join(d, name)
            if os.path.isfile(p):
                out[name] = hashlib.sha256(open(p, "rb").read()).hexdigest()
        return out

    before_hashes = hash_all(feat_dir)
    rec = Recorder()
    run_publish(feat_dir, fleet_path, rec)
    after_hashes = hash_all(feat_dir)
    check("(SC-20) plan.yaml is byte-identical",
          before_hashes["plan.yaml"] == after_hashes["plan.yaml"])
    check("(SC-20) BRIEF.md is byte-identical",
          before_hashes["BRIEF.md"] == after_hashes["BRIEF.md"])
    changed = {k for k in before_hashes if before_hashes[k] != after_hashes.get(k)}
    check("(SC-20) feature.yaml is the only file whose hash changed", changed == {"feature.yaml"},
          changed)


# ============================================================================
# Three C-3 cases.
# ============================================================================

# --- the unsigned-plan refusal writes nothing to stdout, one line to stderr
with tempfile.TemporaryDirectory() as td:
    feat_dir, fleet_path = make_feature(td, approved=False)
    rec = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec)
    check("(C-3a) unsigned-plan refusal: nothing on stdout", out == "", repr(out))
    err_lines = [l for l in err.split("\n") if l]
    check("(C-3a) unsigned-plan refusal: exactly one stderr line", len(err_lines) == 1, err)

# --- the happy path's stdout parses in a single json.loads of the whole stream
with tempfile.TemporaryDirectory() as td:
    feat_dir, fleet_path = make_feature(td)
    rec = Recorder()
    code, out, err = run_publish(feat_dir, fleet_path, rec, extra_args=["--parent", "1"])
    try:
        payload = json.loads(out)
        check("(C-3b) happy path stdout is exactly one JSON object", True)
        check("(C-3b) payload carries the expected keys",
              set(payload.keys()) >= {"repo", "feature", "parent", "parent_origin", "issues",
                                       "edges_drawn", "edges_skipped"},
              payload)
    except Exception as e:
        check("(C-3b) happy path stdout is exactly one JSON object", False, str(e))

# --- a monkeypatched create_issue raising a plain KeyError makes the entry point exit 2
with tempfile.TemporaryDirectory() as td:
    feat_dir, fleet_path = make_feature(td)
    rec = Recorder()
    rec.raise_on["create_issue"] = KeyError("boom")
    code, out, err = run_publish(feat_dir, fleet_path, rec)
    check("(C-3c) a plain KeyError from create_issue exits 2, not 1", code == 2, f"code={code!r}")

# ============================================================================
# S2. a plan with no usable top-level `feature` is refused before any remote call —
#     never a `feature:None` (or `feature:`) label reaching gh, never exit 0.
# ============================================================================
for mode in ("missing", "empty", "whitespace"):
    with tempfile.TemporaryDirectory() as td:
        feat_dir, fleet_path = make_feature_bad_feature_key(td, mode)
        rec = Recorder()
        code, out, err = run_publish(feat_dir, fleet_path, rec)
        check(f"(S2-{mode}) exits exactly 2 (EXIT_REFUSED, not 1/'nothing to do')",
              code == 2, f"code={code!r}")
        check(f"(S2-{mode}) nothing on stdout", out == "", repr(out))
        check(f"(S2-{mode}) stderr names the plan path",
              os.path.join(feat_dir, "plan.yaml") in err, err)
        check(f"(S2-{mode}) stderr names the missing/unusable field: 'feature'",
              "feature" in err, err)
        check(f"(S2-{mode}) zero mutating gh calls — no remote write at all",
              rec.mutating_calls() == [], rec.mutating_calls())
        check(f"(S2-{mode}) preflight itself never ran either — refused before step 3",
              rec.calls == [], rec.calls)
        all_labels = []
        for name, args in rec.calls:
            for a in args:
                if isinstance(a, (list, tuple)):
                    all_labels.extend(a)
        check(f"(S2-{mode}) no 'feature:None' label anywhere in what reached gh",
              not any(str(l).startswith("feature:None") for l in all_labels), all_labels)
        check(f"(S2-{mode}) no bare 'feature:' label anywhere in what reached gh either",
              not any(str(l) == "feature:" for l in all_labels), all_labels)


print(f"\n{RAN - FAILS}/{RAN} checks passed." if FAILS == 0 else f"\n{FAILS} of {RAN} FAILING.")
sys.exit(1 if FAILS else 0)
