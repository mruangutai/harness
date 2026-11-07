#!/usr/bin/env python3
"""Unit floor for gh-sync.py's Build-entry seams (T-11, BUG-1309, DEC-217's Over clause).
Eleven cases, each aimed at a state or observable the T-02/T-03/T-04 integration blocks in
tests/integration/test-gh-sync.py cannot construct (see this task's plan.yaml intent for the
case-by-case cross-check against all five integration files). Mutation-based discrimination
proof lives outside this file (throwaway scripts, never the real gh-sync.py) and is recorded in
this task's receipt.

python3 stdlib only. BIN-dir resolution convention (tests/unit/test-handoff-done-when.py:7-10);
in-process load of the hyphenated gh-sync.py (tests/unit/test-gh-cost-log.py:291); reporting
convention (tests/unit/test-handoff-done-when.py:15-18).

    ./test-gh-sync-build-entry.py    -> exit 0 all pass, 1 otherwise
"""
import importlib.util
import io
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(BIN))

_spec = importlib.util.spec_from_file_location("_ghs_t11_build_entry", str(BIN / "gh-sync.py"))
gh_sync = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gh_sync)

failures = []


def check(name, ok, detail=""):
    print("PASS" if ok else "FAIL", name, detail if not ok else "")
    if not ok:
        failures.append(name)


def feat_dir(tmp, name):
    d = os.path.join(tmp, ".harness", "harness", "features", name)
    os.makedirs(d, exist_ok=True)
    return d


def base_doc(feature_id, github=None):
    """A schema-valid feature.json: the seven required top-level keys, `github` added only
    where the case wants one, with the closed key set {milestone, parent, attached, issues,
    source_issues, build_entry}."""
    doc = {
        "feature_id": feature_id,
        "branch": "none",
        "pr": None,
        "review_sha": "none",
        "cycles_used": 0,
        "max_total_cycles": 1,
        "runs": [],
    }
    if github is not None:
        doc["github"] = github
    return doc


def write_feature_json(d, doc):
    with open(os.path.join(d, "feature.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)


def read_feature_json(d):
    with open(os.path.join(d, "feature.json"), encoding="utf-8") as f:
        return json.load(f)


class _Captured:
    """Swap stdout/stderr for the duration of a call, and catch SystemExit."""

    def __enter__(self):
        self._out, self._err = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
        self.exit_code = None
        self.raised = False
        return self

    def __exit__(self, exc_type, exc, tb):
        self.out = sys.stdout.getvalue()
        self.err = sys.stderr.getvalue()
        sys.stdout, sys.stderr = self._out, self._err
        if exc_type is SystemExit:
            self.raised = True
            self.exit_code = exc.code
            return True
        return False


# ---------------------------------------------------------------------------
# Read and write side (T-02).

# BE-11: load_recorded normalizes an out-of-enum build_entry, "reopened", to None.
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9101-fixture")
    write_feature_json(d, base_doc("FEAT-9101-fixture", github={
        "milestone": None, "parent": None, "attached": [], "issues": {},
        "source_issues": [], "build_entry": "reopened"}))
    rec = gh_sync.load_recorded(d)
    check("BE-11 load_recorded normalizes an out-of-enum build_entry to None",
          rec.get("build_entry") is None, repr(rec.get("build_entry")))

# BE-12: save_recorded of that record DROPS the key entirely — no build_entry in the written
# feature.json, asserted as key absence, never as a falsy value.
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9102-fixture")
    write_feature_json(d, base_doc("FEAT-9102-fixture", github={
        "milestone": None, "parent": None, "attached": [], "issues": {},
        "source_issues": [], "build_entry": "reopened"}))
    rec = gh_sync.load_recorded(d)
    gh_sync.save_recorded(d, rec)
    written = read_feature_json(d)
    check("BE-12 save_recorded of a normalized record drops the build_entry key",
          "build_entry" not in written.get("github", {}), repr(written.get("github")))

# BE-14: record_build_entry upgrades a recorded recovery-required to opened.
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9103-fixture")
    write_feature_json(d, base_doc("FEAT-9103-fixture", github={
        "milestone": None, "parent": None, "attached": [], "issues": {},
        "source_issues": [], "build_entry": "recovery-required"}))
    gh_sync.record_build_entry(d, "opened")
    rec2 = gh_sync.load_recorded(d)
    check("BE-14 record_build_entry upgrades a recorded recovery-required to opened",
          rec2.get("build_entry") == "opened", repr(rec2.get("build_entry")))

# A legacy unbound opened mapping (no github.repo) is the owner's own generation: an
# environmental skip on rerun must not downgrade it; a bound feature's absence is not.
for factory, expected in ((None, "opened"), ({"repo": "org/product"}, "recovery-required")):
    with tempfile.TemporaryDirectory() as tmp:
        d = feat_dir(tmp, "FEAT-9105-fixture-legacy")
        doc = base_doc("FEAT-9105-fixture-legacy", github={
            "milestone": 3, "parent": 7, "attached": [], "issues": {},
            "source_issues": [], "build_entry": "opened"})
        if factory:
            doc["factory"] = factory
        write_feature_json(d, doc)
        gh_sync._BUILD_ENTRY["repo"] = "acme/widgets"
        try:
            gh_sync.record_build_entry(d, "recovery-required")
        finally:
            gh_sync._BUILD_ENTRY.pop("repo", None)
        got = gh_sync.load_recorded(d).get("build_entry")
        check(f"legacy opened receipt, factory={factory}: rerun skip leaves {expected}",
              got == expected, repr(got))

# BE-19: skip() armed but feature.json does not exist — records nothing and creates no file.
with tempfile.TemporaryDirectory() as tmp:
    d = feat_dir(tmp, "FEAT-9104-fixture-absent")
    gh_sync._BUILD_ENTRY["feat_dir"] = d
    gh_sync._BUILD_ENTRY["remote_written"] = False
    with _Captured() as cap:
        gh_sync.skip("test message")
    gh_sync._BUILD_ENTRY["feat_dir"] = None
    gh_sync._BUILD_ENTRY["remote_written"] = False
    exists = os.path.isfile(os.path.join(d, "feature.json"))
    check("BE-19 skip armed with feature.json absent records nothing and creates no file",
          cap.raised and cap.exit_code == 0 and not exists,
          f"raised={cap.raised} exit={cap.exit_code} exists={exists}")

# ---------------------------------------------------------------------------
# Build-entry preflight (T-04), uniform since FEAT-71: no feature id is exempt.

# A Build start with NO receipt is refused, and a recovery-required one proceeds with the
# merge-refused notice, for EVERY feature id: synthetic ones, plus every feature-id-shaped
# string feature_schema itself holds as module data — read from the module, never named here,
# so a reintroduced per-feature exemption table is probed without this file naming any real
# feature.
import re  # noqa: E402
import feature_schema  # noqa: E402
_held = set()
for _value in vars(feature_schema).values():
    _members = _value.keys() if isinstance(_value, dict) else (
        _value if isinstance(_value, (set, frozenset, list, tuple)) else ())
    _held.update(m for m in _members
                 if isinstance(m, str) and re.match(r"^(FEAT|BUG|PR)-[0-9]+", m))
not_refused, not_noticed = [], []
with tempfile.TemporaryDirectory() as tmp:
    for name in ["FEAT-9106-fixture", "BUG-9-x"] + sorted(_held):
        d = feat_dir(tmp, name)
        write_feature_json(d, base_doc(name, {}))
        with _Captured() as cap:
            gh_sync._build_entry_preflight(d, {"build_entry": None})
        if not (cap.raised and cap.exit_code == 2 and "no recorded build entry" in cap.out):
            not_refused.append((name, cap.exit_code))
        with _Captured() as cap:
            gh_sync._build_entry_preflight(d + "/", {"build_entry": "recovery-required"})
        if cap.raised or "the MERGE is refused until explicit recovery" not in cap.err:
            not_noticed.append(name)
check("BE-31 an absent receipt refuses the Build start for every feature id",
      not_refused == [], f"{len(not_refused)} not refused, e.g. {not_refused[:3]}")
check("BE-32 recovery-required warns that the merge is refused, for every feature id",
      not_noticed == [], f"{len(not_noticed)} exempt, e.g. {not_noticed[:3]}")

# ---------------------------------------------------------------------------
# recover-terminal (T-03).

# BE-25: _recover_terminal_conflict is None when --parent (a STRING, as main() passes it)
# matches the recorded parent via the int() coercion.
got = gh_sync._recover_terminal_conflict({"parent": 1289}, "1289")
check("BE-25 a matching string --parent against the recorded parent is no conflict",
      got is None, repr(got))

# BE-27: conflict is None when --parent is absent, and None when no parent is recorded.
r1 = gh_sync._recover_terminal_conflict({"parent": 1289}, None)
r2 = gh_sync._recover_terminal_conflict({"parent": None}, "5")
check("BE-27 conflict is None with no --parent given, and None with no parent recorded",
      r1 is None and r2 is None, f"r1={r1!r} r2={r2!r}")

# BE-28: milestone and parent both recorded — creates == [] and both adoption lines present.
creates, adoptions = gh_sync._recover_terminal_report({"milestone": 7, "parent": 40}, None)
check("BE-28 milestone and parent recorded yields no creates and both adoption lines",
      creates == []
      and "gh-sync: adopting recorded milestone 7" in adoptions
      and "gh-sync: adopting recorded parent #40" in adoptions,
      f"creates={creates!r} adoptions={adoptions!r}")

# BE-29: neither recorded — creates is exactly the two-line list.
creates, adoptions = gh_sync._recover_terminal_report({"milestone": None, "parent": None}, None)
check("BE-29 neither milestone nor parent recorded yields the exact two-line creates list",
      creates == ["create the milestone", "create the parent"], repr(creates))

# BE-30: a milestone recorded and --parent 9 given — creates is exactly the one adoption line,
# and across all four adoption states no returned line ever mentions a task or a sub-issue.
creates, _ = gh_sync._recover_terminal_report({"milestone": 7, "parent": None}, "9")
no_mentions = True
for rec, parent_arg in (
    ({"milestone": None, "parent": None}, None),
    ({"milestone": 7, "parent": None}, None),
    ({"milestone": None, "parent": 40}, None),
    ({"milestone": 7, "parent": 40}, None),
):
    c, a = gh_sync._recover_terminal_report(rec, parent_arg)
    for line in c + a:
        if "task" in line.lower() or "sub-issue" in line.lower():
            no_mentions = False
check("BE-30 milestone recorded plus --parent 9 given adopts by number, and no adoption "
      "state ever mentions a task or a sub-issue",
      creates == ["adopt parent #9 (given via --parent)"] and no_mentions,
      f"creates={creates!r} no_mentions={no_mentions}")

# A signed plan can acquire a ledgered amendment without rewriting its original hashes.
# Recovery must recognize that approval, but neither an unrelated amendment nor a missing
# original signature may bless changed task text.
with tempfile.TemporaryDirectory() as tmp:
    from plan_merge.approval import signed_task_hashes

    d = feat_dir(tmp, "FEAT-9110-fixture")
    plan = {"approval": {"status": "approved"}, "tasks": [
        {"id": "T-01", "title": "Recovery approval", "change_type": "cross_module",
         "execution_mode": "main-session-direct", "files": ["original.py"],
         "intent": "fix", "verify": "unit"}]}
    doc = base_doc("FEAT-9110-fixture")
    doc["signed_task_hashes"] = signed_task_hashes(plan)
    plan["tasks"][0]["files"].append("approved-regression.py")
    Path(d, "plan.yaml").write_text(json.dumps(plan), encoding="utf-8")
    for label, judgements, accepted in (
        ("ledgered amendment", [{"kind": "amendment", "decision": "T-01.files"}], True),
        ("unrelated amendment", [{"kind": "amendment", "decision": "T-02.files"}], False),
        ("unledgered edit", [], False),
    ):
        doc["judgements"] = judgements
        try:
            gh_sync._replacement_plan(d, doc)
            allowed = True
        except ValueError:
            allowed = False
        check(f"mirror replacement approval: {label}", allowed == accepted)
    doc["signed_task_hashes"] = {}
    doc["judgements"] = [{"kind": "amendment", "decision": "T-01.files"}]
    try:
        gh_sync._replacement_plan(d, doc)
        allowed = True
    except ValueError:
        allowed = False
    check("mirror replacement refuses missing original task signatures", not allowed)

sys.exit(1 if failures else 0)
