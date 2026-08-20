#!/usr/bin/env python3
"""Tests for factory_gh.py, the single seam every factory tool talks to GitHub through (D-02, D-14).

WHY: this module's whole job is deciding failure behaviour once — loud (GhError), never a
swallowed default — and routing the three DAG edge functions through gh_issues' argv builders
so FACTORY_GH cannot be silently bypassed (the T-12 stub-gh escape named in the plan). Every
case here monkeypatches subprocess.run or run_gh with an in-process recorder; nothing spawns a
real gh (run-unit-tests.sh classifies this as UNIT for exactly that reason).
"""
import base64
import contextlib
import io
import json
import os
import sys

import factory_gh as fgh
import gh_issues

# FEAT-29 T-03, amendment 4: run_gh now wraps its subprocess call with gh_cost_log.measured(),
# which (when enabled) makes TWO extra `gh api rate_limit` calls per invocation to read the
# GraphQL counter before and after. This file asserts on calls[0] in ~28 places — those extra
# calls would shift every one of them. Set BEFORE any test runs, at true module scope, so no
# recorder here ever sees a counter-read call.
os.environ["HARNESS_GH_COST_LOG"] = "0"

FAILS = 0
RAN = 0
RAISED = []  # every GhError caught below — the "every GhError" invariant is asserted once, at the end


def check(name, cond, detail=""):
    global FAILS, RAN
    RAN += 1
    if cond:
        print(f"ok    {name}")
    else:
        FAILS += 1
        print(f"FAIL  {name}" + (f"\n        {detail}" if detail else ""))


class Result:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def recorder(results):
    """Returns (fake_run, calls). fake_run replaces factory_gh.subprocess.run."""
    calls = []
    it = iter(results)

    def fake_run(argv, **kwargs):
        calls.append({"argv": argv, **kwargs})
        try:
            return next(it)
        except StopIteration:
            raise AssertionError(f"recorder ran out of results, argv={argv!r}")

    return fake_run, calls


_real_subprocess_run = fgh.subprocess.run
_real_run_gh = fgh.run_gh
_real_gh_bin = gh_issues.gh_bin


def restore():
    fgh.subprocess.run = _real_subprocess_run
    fgh.run_gh = _real_run_gh
    gh_issues.gh_bin = _real_gh_bin


def silent_stdout(fn, *a, **kw):
    """Run fn under redirect_stdout, return (result_or_exc, stdout_text)."""
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            result = fn(*a, **kw)
        return result, out.getvalue()
    except Exception as exc:
        return exc, out.getvalue()


GRAPHQL_FIELD_JSON = json.dumps({"data": {"repositoryOwner": {"__typename": "User",
    "projectV2": {"id": "PVT_kwFAKE", "field": {"id": "F1", "name": "Station",
    "options": [{"id": "O1", "name": "Ready"}, {"id": "O2", "name": "Doing"}]}}}}})

# The exit-0 organization fixture: no row in the measured table names it — no org owning a
# reachable board is reachable from this account — it is derived from the success shape above
# with __typename flipped. Named so SC-05 has a content anchor to grep for.
GRAPHQL_ORG_OK_JSON = json.dumps({"data": {"repositoryOwner": {"__typename": "Organization",
    "projectV2": {"id": "PVT_kwFAKE", "field": {"id": "F1", "name": "Station",
    "options": [{"id": "O1", "name": "Ready"}, {"id": "O2", "name": "Doing"}]}}}}})

GRAPHQL_UNKNOWN_OWNER_JSON = json.dumps({"data": {"repositoryOwner": None}})

GRAPHQL_ORG_UNREACHABLE_JSON = json.dumps({
    "data": {"repositoryOwner": {"__typename": "Organization", "projectV2": None}},
    "errors": [{"type": "NOT_FOUND"}],
})

GRAPHQL_BOARD_ABSENT_JSON = json.dumps({
    "data": {"repositoryOwner": {"__typename": "User", "projectV2": None}},
    "errors": [{"type": "NOT_FOUND"}],
})

GRAPHQL_FIELD_ABSENT_JSON = json.dumps({
    "data": {"repositoryOwner": {"__typename": "User",
              "projectV2": {"id": "PVT_kwFAKE", "field": None}}},
    "errors": [{"type": "NOT_FOUND"}],
})

GRAPHQL_FIELD_NOT_SINGLE_SELECT_JSON = json.dumps({"data": {"repositoryOwner": {
    "__typename": "User", "projectV2": {"id": "PVT_kwFAKE", "field": {}}}}})


# ---- issue_board_item_id fixtures (D-01/D-03) ----
ISSUE_ITEM_MATCH_JSON = json.dumps({"data": {"repository": {"issue": {"projectItems": {
    "totalCount": 1, "nodes": [{"id": "ITEM1", "project": {"number": 9}}]}}}}})

ISSUE_ITEM_OTHER_PROJECT_JSON = json.dumps({"data": {"repository": {"issue": {"projectItems": {
    "totalCount": 1, "nodes": [{"id": "ITEM1", "project": {"number": 4}}]}}}}})

ISSUE_ITEM_EMPTY_JSON = json.dumps({"data": {"repository": {"issue": {"projectItems": {
    "totalCount": 0, "nodes": []}}}}})

ISSUE_ITEM_ISSUE_NULL_JSON = json.dumps({"data": {"repository": {"issue": None}}})

ISSUE_ITEM_NO_ISSUE_KEY_JSON = json.dumps({"data": {"repository": {}}})

ISSUE_ITEM_NO_PROJECTITEMS_JSON = json.dumps({"data": {"repository": {"issue": {}}}})

ISSUE_ITEM_NODES_NOT_LIST_JSON = json.dumps({"data": {"repository": {"issue": {"projectItems": {
    "totalCount": 0, "nodes": "not-a-list"}}}}})

ISSUE_ITEM_NO_TOTALCOUNT_JSON = json.dumps({"data": {"repository": {"issue": {"projectItems": {
    "nodes": []}}}}})

ISSUE_ITEM_TOTALCOUNT_STRING_JSON = json.dumps({"data": {"repository": {"issue": {"projectItems": {
    "totalCount": "oops", "nodes": []}}}}})

ISSUE_ITEM_TRUNCATED_JSON = json.dumps({"data": {"repository": {"issue": {"projectItems": {
    "totalCount": 3, "nodes": [{"id": "ITEM1", "project": {"number": 9}}]}}}}})

ISSUE_ITEM_NODE_NO_ID_JSON = json.dumps({"data": {"repository": {"issue": {"projectItems": {
    "totalCount": 1, "nodes": [{"project": {"number": 9}}]}}}}})

ISSUE_ITEM_NODE_NO_PROJECT_JSON = json.dumps({"data": {"repository": {"issue": {"projectItems": {
    "totalCount": 1, "nodes": [{"id": "ITEM1"}]}}}}})

ISSUE_ITEM_NULL_REPOSITORY_JSON = json.dumps({"data": {"repository": None}})


def dispatching_fake(responses_by_prefix, default=None):
    """An argv-DISPATCHING fake for subprocess.run: matches on the argv PREFIX (e.g.
    ("project", "field-list")) rather than call ORDER, so it discriminates the shape of a value
    (which id reached --project-id) instead of merely recording that a call happened.

    subprocess.run is invoked with [gh_binary] + args (factory_gh.run_gh prepends the binary),
    so argv[0] here is the binary, not the gh subcommand — the prefix match starts at argv[1:]."""
    calls = []

    def fake_run(argv, **kwargs):
        calls.append({"argv": argv, **kwargs})
        rest = argv[1:]
        for prefix, result in responses_by_prefix.items():
            if list(rest[:len(prefix)]) == list(prefix):
                return result
        if default is not None:
            return default
        raise AssertionError(f"dispatching_fake: unhandled argv={argv!r}")

    return fake_run, calls

PROJECT_ITEMS_2 = {
    "totalCount": 2,
    "items": [
        {"content": {"number": 1, "repository": "o/r"}, "id": "i1", "labels": [],
         "repository": "https://github.com/o/r", "status": "Ready", "title": "t1"},
        {"content": {"number": 2, "repository": "o/r"}, "id": "i2", "labels": [],
         "repository": "https://github.com/o/r", "status": "Ready", "title": "t2"},
    ],
}

PROJECT_ITEMS_TRUNCATED = {
    "totalCount": 5,
    "items": [
        {"content": {"number": 1, "repository": "o/r"}, "id": "i1", "labels": [],
         "repository": "https://github.com/o/r", "status": "Ready", "title": "t1"},
    ],
}


# ---------------- run_gh: missing binary ----------------
def fake_run_missing(argv, **kwargs):
    raise FileNotFoundError("no such file: 'gh'")


fgh.subprocess.run = fake_run_missing
try:
    fgh.run_gh(["auth", "status"])
    raised, msg = False, ""
except fgh.GhError as e:
    raised, msg = True, str(e)
    RAISED.append(e)
restore()
check("run_gh: raises GhError when the binary is missing", raised)
check("run_gh: missing-binary message carries a concrete value",
      "gh" in msg.lower(), f"msg={msg!r}")


# ---------------- run_gh: non-zero exit carries stderr ----------------
# Two Results queued, not one: under a mutant that drops the rate-limit TEXT check from run_gh's
# detection guard (T-04 mutation 1), this ordinary permission-denied failure is misrouted into the
# rate_limit budget path, which makes a SECOND subprocess call (`gh api rate_limit`) to build its
# message. Unmutated code never takes that path — this call is never made and the second Result
# is simply never consumed, per `recorder`'s own contract (it raises only when it runs out). This
# is what makes the check below (`run_gh: message carries the captured stderr`) capable of
# reddening in-repo, per FEAT-29 T-04 cycle 2.
fake, calls = recorder([
    Result(1, stdout="", stderr="permission denied\nmore detail"),
    Result(1, stdout="", stderr="rate_limit query itself failed"),
])
fgh.subprocess.run = fake
try:
    fgh.run_gh(["issue", "list"])
    raised, exc = False, None
except fgh.GhError as e:
    raised, exc = True, e
    RAISED.append(e)
restore()
check("run_gh: raises GhError on non-zero exit", raised)
check("run_gh: message carries the captured stderr",
      raised and "permission denied" in str(exc), f"exc={exc}")
check("run_gh: GhError message has an em dash, no class name, no traceback",
      raised and "—" in str(exc) and "GhError" not in str(exc) and "Traceback" not in str(exc),
      f"exc={exc}")


# ---------------- run_gh: FACTORY_GH resolved at call time ----------------
os.environ["FACTORY_GH"] = "my-stub-gh"
fake, calls = recorder([Result(0, stdout="ok")])
fgh.subprocess.run = fake
try:
    fgh.run_gh(["auth", "status"])
finally:
    del os.environ["FACTORY_GH"]
    restore()
check("run_gh: FACTORY_GH set AFTER import changes the binary used",
      calls and calls[0]["argv"][0] == "my-stub-gh", f"calls={calls}")


# ---------------- run_gh: stdin is closed ----------------
fake, calls = recorder([Result(0, stdout="ok")])
fgh.subprocess.run = fake
fgh.run_gh(["auth", "status"])
restore()
check("run_gh: stdin is closed (DEVNULL)",
      calls and calls[0].get("stdin") is fgh.subprocess.DEVNULL, f"calls={calls}")


# ---------------- preflight: succeeds silently, raises with the auth-login hint ----------------
fake, calls = recorder([Result(0)])
fgh.subprocess.run = fake
result = fgh.preflight()
restore()
check("preflight: returns None on a zero exit", result is None, f"result={result!r}")
check("preflight: runs `auth status`",
      calls and calls[0]["argv"] == ["gh", "auth", "status"], f"calls={calls}")

# Two Results queued for the same reason as the non-zero-exit fixture above: under T-04
# mutation 1 this ordinary auth failure is misrouted into the rate_limit budget path, which
# makes a second subprocess call. Unmutated code never makes that call, so the spare Result is
# never consumed.
fake, calls = recorder([
    Result(1, stderr="gh: not logged in"),
    Result(1, stderr="rate_limit query itself failed"),
])
fgh.subprocess.run = fake
try:
    fgh.preflight()
    raised = False
except fgh.GhError as e:
    raised, exc = True, e
    RAISED.append(e)
restore()
check("preflight: raises GhError telling the operator to run gh auth login",
      raised and "gh auth login" in str(exc), f"exc={exc if raised else None}")


# ---------------- create_issue: parses number from URL ----------------
fake, calls = recorder([Result(0, stdout="https://github.com/o/r/issues/42\n")])
fgh.subprocess.run = fake
num = fgh.create_issue("o/r", "title", "body", ["harness", "chore"])
restore()
check("create_issue: returns the number parsed from the URL", num == 42, f"num={num!r}")
check("create_issue: passes repo verbatim",
      calls and "--repo" in calls[0]["argv"] and
      calls[0]["argv"][calls[0]["argv"].index("--repo") + 1] == "o/r", f"calls={calls}")
check("create_issue: passes every label",
      calls[0]["argv"].count("harness") == 1 and calls[0]["argv"].count("chore") == 1)


# ---------------- create_issue: unparseable output raises ----------------
fake, calls = recorder([Result(0, stdout="not a url\n")])
fgh.subprocess.run = fake
try:
    fgh.create_issue("o/r", "t", "b", [])
    raised = False
except fgh.GhError as e:
    raised = True
    RAISED.append(e)
restore()
check("create_issue: unparseable output raises GhError, never returns a default", raised)


# ---------------- ensure_labels: one call per label, raises rather than swallows ----------------
# The 3rd/4th Results are never consumed by unmutated code (the loop stops at the failing label
# "b"). Under T-04 mutation 1 the failing "b" call is misrouted into the rate_limit budget path,
# which makes an extra subprocess call and consumes the queue's NEXT item regardless of which
# label it was meant for — so that item must itself look like a (non-JSON, ordinary) gh failure,
# not a bare success, or the mutant crashes on json.loads("") instead of reddening a check.
fake, calls = recorder([
    Result(0), Result(1, stderr="already frozen"), Result(1, stderr="rate_limit query itself failed"),
])
fgh.subprocess.run = fake
try:
    fgh.ensure_labels("o/r", ["a", "b", "c"])
    raised = False
except fgh.GhError as e:
    raised = True
    RAISED.append(e)
restore()
check("ensure_labels: raises GhError instead of swallowing a non-zero exit", raised)
check("ensure_labels: stops at the failing label, does not run the remaining ones",
      len(calls) == 2, f"calls={len(calls)}")
check("ensure_labels: each call uses --force",
      all("--force" in c["argv"] for c in calls), f"calls={calls}")
check("ensure_labels: passes repo verbatim",
      all(c["argv"][c["argv"].index("--repo") + 1] == "o/r" for c in calls))


# ---------------- project_field_set: resolves ids via ONE graphql call, then edits ----------------
fake, calls = recorder([
    Result(0, stdout=GRAPHQL_FIELD_JSON), Result(0, stdout=""),
])
fgh.subprocess.run = fake
try:
    fgh.project_field_set("owner", 3, "ITEM1", "Station", "Ready")
    set_exc = None
except fgh.GhError as e:
    set_exc = e
    RAISED.append(e)
restore()
check("project_field_set: made no more and no fewer than TWO calls (graphql, then item-edit)",
      set_exc is None and len(calls) == 2, f"exc={set_exc}, calls={calls}")
if set_exc is None:
    graphql_call, edit_call = calls[0], calls[1]
    check("project_field_set: first call is gh api graphql",
          graphql_call["argv"][1:3] == ["api", "graphql"], f"argv={graphql_call['argv']}")
    check("project_field_set: second call is gh project item-edit",
          edit_call["argv"][1:3] == ["project", "item-edit"], f"argv={edit_call['argv']}")
    check("project_field_set: resolves the field id",
          "F1" in edit_call["argv"], f"argv={edit_call['argv']}")
    check("project_field_set: resolves the option id",
          "O1" in edit_call["argv"], f"argv={edit_call['argv']}")

    # THE OVER-SCOPE GUARD. Regexes, not substrings — see the intent for why a substring test
    # is not sufficient (a filtered plural connection can satisfy it while still fanning out).
    import re as _re
    qargv = graphql_call["argv"]
    q = ""
    for i, a in enumerate(qargv):
        if a == "-f" and i + 1 < len(qargv) and qargv[i + 1].startswith("query="):
            q = qargv[i + 1][len("query="):]
    check("project_field_set: query selects exactly one field by name",
          _re.search(r"field\s*\(\s*name\s*:", q) is not None, f"q={q!r}")
    check("project_field_set: query has no plural field-connection selection",
          _re.search(r"fields\s*\(", q) is None, f"q={q!r}")
    check("project_field_set: query carries no connection argument (first:/last:)",
          _re.search(r"\b(first|last)\s*:", q) is None, f"q={q!r}")

# ---------------- project_field_set: option not offered — raises, edits nothing ----------------
fake, calls = recorder([Result(0, stdout=GRAPHQL_FIELD_JSON)])
fgh.subprocess.run = fake
try:
    fgh.project_field_set("owner", 3, "ITEM1", "Station", "NotAnOption")
    raised = False
except fgh.GhError as e:
    raised, exc = True, e
    RAISED.append(e)
restore()
check("project_field_set: raises GhError naming the option when it is not offered",
      raised and "NotAnOption" in str(exc), f"exc={exc if raised else None}")
check("project_field_set: option-not-offered case makes ZERO item-edit calls",
      not any(c["argv"][1:3] == ["project", "item-edit"] for c in calls), f"calls={calls}")
# D-04 freeze: the rendered next_step, byte for byte, for THIS case's own arguments.
check("project_field_set: option-not-offered message is the D-04-frozen rendered string",
      raised and "field Station on owner project 3 does not offer it" in str(exc),
      f"exc={exc if raised else None}")
check("project_field_set: option-not-offered message carries no generic subcommand fallback",
      raised and "api graphql" not in str(exc), f"exc={exc if raised else None}")


# ---------------- project_field_set: --project-id must be the node id, not the board number ----
# argv-DISPATCHING fake, dispatching on the ("api", "graphql") prefix now that there is one call
# that resolves all three ids.
fake, calls = dispatching_fake({
    ("api", "graphql"): Result(0, stdout=GRAPHQL_FIELD_JSON),
}, default=Result(0, stdout=""))
fgh.subprocess.run = fake
try:
    fgh.project_field_set("owner", 3, "ITEM1", "Station", "Ready")
    pid_exc = None
except fgh.GhError as e:
    pid_exc = e
    RAISED.append(e)
restore()
check("project_field_set (--project-id case): did not raise", pid_exc is None, f"exc={pid_exc}")
edit_calls = [c for c in calls if c["argv"][1:3] == ["project", "item-edit"]]
check("project_field_set: exactly one item-edit call was made", len(edit_calls) == 1,
      f"calls={calls}")
if edit_calls:
    argv = edit_calls[0]["argv"]
    check("project_field_set: --project-id is present in the item-edit argv",
          "--project-id" in argv, f"argv={argv}")
    if "--project-id" in argv:
        pid = argv[argv.index("--project-id") + 1]
        check("project_field_set: --project-id carries the GraphQL node id, "
              "NOT the bare board number",
              pid == "PVT_kwFAKE" and pid != "3", f"--project-id={pid!r} argv={argv}")


# ---------------- project_field_set: a NON-DIAGNOSABLE transport failure RAISES, never falls
# back ---------------------------------------------------------------------------------------
# The genuine transport/auth-failure path (D-03 step e): stdout carries no JSON at all, so the
# resolver cannot fall through to the data walk and must re-raise with a real value — never the
# generic "api graphql" subcommand fallback (D-02, never swallow).
fake, calls = dispatching_fake({
    ("api", "graphql"): Result(1, stdout="", stderr="gh: API error"),
}, default=Result(0, stdout=""))
fgh.subprocess.run = fake
try:
    fgh.project_field_set("owner", 3, "ITEM1", "Station", "Ready")
    raised, exc = False, None
except fgh.GhError as e:
    raised, exc = True, e
    RAISED.append(e)
restore()
check("project_field_set: a non-diagnosable transport failure raises GhError",
      raised and isinstance(exc, fgh.GhError), f"exc={exc!r}")
check("project_field_set: a transport failure makes ZERO item-edit calls "
      "(never falls back to the bare number)",
      not any(c["argv"][1:3] == ["project", "item-edit"] for c in calls), f"calls={calls}")
check("project_field_set: transport-failure message names owner + project number",
      raised and "owner project 3" in str(exc), f"exc={exc if raised else None}")
check("project_field_set: transport-failure message never carries the generic "
      "subcommand fallback",
      raised and "api graphql" not in str(exc), f"exc={exc if raised else None}")


# ---------------- _project_field_resolve: the newly separated diagnosis states ----------------
# unknown owner login — EXIT 0, no errors key. Different message from the org and board cases.
fake, calls = recorder([Result(0, stdout=GRAPHQL_UNKNOWN_OWNER_JSON)])
fgh.subprocess.run = fake
try:
    # "acmeuser", not "owner" (MF-1): "owner" occurs in this case's own fixed prose
    # ("project owner not found", "check the owner login"), so the naming assertion below
    # would pass regardless of the value slot. "acmeuser" occurs in no fixed prose in this
    # file. Moves together with :421 and :441.
    fgh.project_field_set("acmeuser", 3, "ITEM1", "Station", "Ready")
    raised, unknown_exc = False, None
except fgh.GhError as e:
    raised, unknown_exc = True, e
    RAISED.append(e)
restore()
check("unknown owner: raises GhError naming the owner",
      raised and "acmeuser" in str(unknown_exc), f"exc={unknown_exc if raised else None}")
check("unknown owner: makes ZERO item-edit calls",
      not any(c["argv"][1:3] == ["project", "item-edit"] for c in calls), f"calls={calls}")
check("unknown owner: message carries no generic subcommand fallback",
      raised and "api graphql" not in str(unknown_exc), f"exc={unknown_exc if raised else None}")

# organization-owned board — asserted against BOTH envelopes (exit-1 unreachable, exit-0 reachable)
for label, fixture in (("exit-1 unreachable", GRAPHQL_ORG_UNREACHABLE_JSON),
                       ("exit-0 reachable", GRAPHQL_ORG_OK_JSON)):
    status = 1 if label.startswith("exit-1") else 0
    fake, calls = recorder([Result(status, stdout=fixture,
                                    stderr="" if status == 0 else "gh: not found")])
    fgh.subprocess.run = fake
    try:
        # "acmeuser" — moves together with :400 and :441 (MF-1 remedy).
        fgh.project_field_set("acmeuser", 3, "ITEM1", "Station", "Ready")
        raised, org_exc = False, None
    except fgh.GhError as e:
        raised, org_exc = True, e
        RAISED.append(e)
    restore()
    check(f"organization ({label}): raises GhError naming the owner",
          raised and "acmeuser" in str(org_exc), f"exc={org_exc if raised else None}")
    check(f"organization ({label}): makes ZERO item-edit calls",
          not any(c["argv"][1:3] == ["project", "item-edit"] for c in calls), f"calls={calls}")
    check(f"organization ({label}): message differs from the unknown-owner message",
          raised and unknown_exc is not None and str(org_exc) != str(unknown_exc),
          f"org={org_exc}, unknown={unknown_exc}")
    check(f"organization ({label}): message carries no generic subcommand fallback",
          raised and "api graphql" not in str(org_exc), f"exc={org_exc if raised else None}")

# board number not present — EXIT 1, __typename User, projectV2 null
fake, calls = recorder([Result(1, stdout=GRAPHQL_BOARD_ABSENT_JSON, stderr="gh: not found")])
fgh.subprocess.run = fake
try:
    # "acmeuser" — not optional here even though :452 already discriminates below;
    # moving only the org case would make that inequality pass for the wrong reason
    # (differing values, not differing messages) — MF-1 trap 1.
    fgh.project_field_set("acmeuser", 3, "ITEM1", "Station", "Ready")
    raised, board_exc = False, None
except fgh.GhError as e:
    raised, board_exc = True, e
    RAISED.append(e)
restore()
check("board absent: raises GhError naming owner + project number",
      raised and "acmeuser project 3" in str(board_exc), f"exc={board_exc if raised else None}")
check("board absent: makes ZERO item-edit calls",
      not any(c["argv"][1:3] == ["project", "item-edit"] for c in calls), f"calls={calls}")
check("board absent: message differs from the organization message",
      raised and str(board_exc) != str(org_exc), f"board={board_exc}, org={org_exc}")
check("board absent: message differs from the unknown-owner message",
      raised and unknown_exc is not None and str(board_exc) != str(unknown_exc),
      f"board={board_exc}, unknown={unknown_exc}")
check("board absent: message carries no generic subcommand fallback",
      raised and "api graphql" not in str(board_exc), f"exc={board_exc if raised else None}")

# field exists but is not single-select — EXIT 0, field is {} — must catch `{} is not None`
fake, calls = recorder([Result(0, stdout=GRAPHQL_FIELD_NOT_SINGLE_SELECT_JSON)])
fgh.subprocess.run = fake
try:
    fgh.project_field_set("owner", 3, "ITEM1", "Station", "Ready")
    raised, notsingle_exc = False, None
except fgh.GhError as e:
    raised, notsingle_exc = True, e
    RAISED.append(e)
restore()
check("field not single-select (empty dict): raises the SAME field-not-found error as "
      "the field-absent case",
      raised and "field-list for owner project 3 does not offer it" in str(notsingle_exc),
      f"exc={notsingle_exc if raised else None}")
check("field not single-select: makes ZERO item-edit calls",
      not any(c["argv"][1:3] == ["project", "item-edit"] for c in calls), f"calls={calls}")
check("field not single-select: message carries no generic subcommand fallback",
      raised and "api graphql" not in str(notsingle_exc), f"exc={notsingle_exc if raised else None}")


# ---------------- issue_view / add_label / assign: pass repo verbatim ----------------
fake, calls = recorder([Result(0, stdout="{}")])
fgh.subprocess.run = fake
fgh.issue_view("o/r", 9, ["title", "state"])
restore()
check("issue_view: passes repo verbatim and comma-joins fields",
      "o/r" in calls[0]["argv"] and "title,state" in calls[0]["argv"], f"calls={calls}")

fake, calls = recorder([Result(0)])
fgh.subprocess.run = fake
fgh.add_label("o/r", 9, "harness")
restore()
check("add_label: passes repo verbatim", "o/r" in calls[0]["argv"], f"calls={calls}")

fake, calls = recorder([Result(0)])
fgh.subprocess.run = fake
fgh.assign("o/r", 9, "mruangutai")
restore()
check("assign: passes repo and login verbatim",
      "o/r" in calls[0]["argv"] and "mruangutai" in calls[0]["argv"], f"calls={calls}")

fake, calls = recorder([Result(0, stdout='{"id":"PVTI_1"}')])
fgh.subprocess.run = fake
item_id = fgh.project_item_add("owner", 3, "https://github.com/o/r/issues/9")
restore()
check("project_item_add: returns the item id", item_id == "PVTI_1", f"item_id={item_id!r}")
check("project_item_add: passes owner verbatim", "owner" in calls[0]["argv"], f"calls={calls}")


# ---------------- create_ref: True on success, False on the measured conflict, raise otherwise --
fake, calls = recorder([Result(0)])
fgh.subprocess.run = fake
ok = fgh.create_ref("o/r", "refs/heads/factory/issue-1", "abc123")
restore()
check("create_ref: returns True on a zero exit", ok is True, f"ok={ok!r}")

fake, calls = recorder([Result(
    1,
    stdout='{"message":"Reference already exists","status":"422"}',
    stderr="gh: Reference already exists (HTTP 422)",
)])
fgh.subprocess.run = fake
ok = fgh.create_ref("o/r", "refs/heads/factory/issue-1", "abc123")
restore()
check("create_ref: returns False WITHOUT raising on the measured conflict", ok is False,
      f"ok={ok!r}")

fake, calls = recorder([Result(1, stdout="", stderr="gh: authentication required")])
fgh.subprocess.run = fake
try:
    fgh.create_ref("o/r", "refs/heads/factory/issue-1", "abc123")
    raised = False
except fgh.GhError as e:
    raised = True
    RAISED.append(e)
restore()
check("create_ref: raises GhError on a failure carrying neither token (auth failure)", raised)

fake, calls = recorder([Result(
    1,
    stdout='{"message":"Invalid request","status":"422"}',
    stderr="gh: Invalid request (HTTP 422)",
)])
fgh.subprocess.run = fake
try:
    fgh.create_ref("o/r", "refs/heads/factory/issue-1", "badsha")
    raised = False
except fgh.GhError as e:
    raised = True
    RAISED.append(e)
restore()
check("create_ref: a 422 WITHOUT 'already exists' raises rather than reporting a lost race",
      raised)


# ---------------- project_items: truncation guard, query passthrough ----------------
fake, calls = recorder([Result(0, stdout=json.dumps(PROJECT_ITEMS_2))])
fgh.subprocess.run = fake
items = fgh.project_items("o", 3)
restore()
check("project_items: returns the items list", len(items) == 2, f"items={items}")
check("project_items: omits --query when none is given", "--query" not in calls[0]["argv"])

fake, calls = recorder([Result(0, stdout=json.dumps(PROJECT_ITEMS_2))])
fgh.subprocess.run = fake
items = fgh.project_items("o", 3, query="is:open")
restore()
check("project_items: passes the query string verbatim when given",
      "--query" in calls[0]["argv"] and
      calls[0]["argv"][calls[0]["argv"].index("--query") + 1] == "is:open", f"calls={calls}")

fake, calls = recorder([Result(0, stdout=json.dumps(PROJECT_ITEMS_TRUNCATED))])
fgh.subprocess.run = fake
try:
    fgh.project_items("o", 3)
    raised = False
except fgh.GhError as e:
    raised, exc = True, e
    RAISED.append(e)
restore()
check("project_items: raises GhError when totalCount exceeds the returned items",
      raised and "5" in str(exc) and "1" in str(exc), f"exc={exc if raised else None}")

fake, calls = recorder([Result(0, stdout=json.dumps({"items": []}))])
fgh.subprocess.run = fake
try:
    fgh.project_items("o", 3)
    raised = False
except fgh.GhError as e:
    raised = True
    RAISED.append(e)
restore()
check("project_items: a missing totalCount raises rather than defaulting to 0", raised)


# ---------------- project_item_stations: the low-cost targeted board read (T-01, FEAT-29) -----
def _station_page(total, has_next, end_cursor, nodes):
    return json.dumps({"data": {"user": {"projectV2": {"items": {
        "totalCount": total,
        "pageInfo": {"hasNextPage": has_next, "endCursor": end_cursor},
        "nodes": nodes,
    }}}}})


STATION_NODE_READY = {
    "content": {"number": 5, "repository": {"nameWithOwner": "o/r"}},
    "fieldValueByName": {"name": "Ready"},
}
# A second STATIONED (non-null) node — deliberately never null — so the "stationed item maps"
# and "truncation" fixtures below stay unaffected by a mutation that drops null-station nodes;
# only STATION_PRESENCE_JSON below exercises a null fieldValueByName, keeping that mutation's
# blast radius isolated to the one check it is meant to prove (P-04 isolation).
STATION_NODE_DOING = {
    "content": {"number": 6, "repository": {"nameWithOwner": "o/r"}},
    "fieldValueByName": {"name": "Doing"},
}
STATION_NODE_NULL_FV = {
    "content": {"number": 6, "repository": {"nameWithOwner": "o/r"}},
    "fieldValueByName": None,
}
STATION_SINGLE_PAGE_JSON = _station_page(2, False, None, [STATION_NODE_READY, STATION_NODE_DOING])

# ---- single-page: a stationed item maps to its station string ----
# Wrapped (P-04): a mutation that drops the null-station node (test below) makes the
# single-page accumulated count fall short of totalCount, tripping the truncation guard — an
# uncaught raise here would crash the whole suite rather than reddening just its own check.
fake, calls = recorder([Result(0, stdout=STATION_SINGLE_PAGE_JSON)])
fgh.subprocess.run = fake
try:
    station_items = fgh.project_item_stations("owner", 3, "Station")
    station_single_exc = None
except Exception as e:
    station_items = None
    station_single_exc = e
    if isinstance(e, fgh.GhError):
        RAISED.append(e)
restore()
check("project_item_stations: made exactly ONE gh api graphql call",
      len(calls) == 1, f"calls={calls}")
check("project_item_stations: a stationed item maps to its station string",
      station_single_exc is None and station_items[0]["station"] == "Ready",
      f"items={station_items} exc={station_single_exc}")
check("project_item_stations: a stationed item's content carries the issue number and repo",
      station_single_exc is None and station_items[0]["content"] == {"number": 5, "repository": "o/r"},
      f"items={station_items} exc={station_single_exc}")

# ---- null fieldValueByName maps to station None and is PRESENT (not dropped) ----
# A SEPARATE fixture with totalCount deliberately set to 1 (not the real 2): this isolates a
# drop-on-None mutation from the truncation guard above (P-04 isolation) — under the real,
# correct behaviour totalCount=1 <= items_out=2 never trips truncation; under a mutation that
# drops the null-station node, items_out=1 <= totalCount=1 ALSO never trips truncation, so a
# drop is caught ONLY by this presence check, not smothered by an unrelated raise.
STATION_PRESENCE_JSON = _station_page(1, False, None, [STATION_NODE_READY, STATION_NODE_NULL_FV])
fake, calls = recorder([Result(0, stdout=STATION_PRESENCE_JSON)])
fgh.subprocess.run = fake
try:
    station_presence_items = fgh.project_item_stations("owner", 3, "Station")
    station_presence_exc = None
except Exception as e:
    station_presence_items = None
    station_presence_exc = e
    if isinstance(e, fgh.GhError):
        RAISED.append(e)
restore()
check("project_item_stations: a null fieldValueByName item maps to station None "
      "and is present in the output",
      station_presence_exc is None and len(station_presence_items) == 2
      and station_presence_items[1]["station"] is None,
      f"items={station_presence_items} exc={station_presence_exc}")

# ---- two-page response is fully accumulated; the second page's items appear ----
STATION_PAGE1_JSON = _station_page(3, True, "CURSOR1", [
    {"content": {"number": 1, "repository": {"nameWithOwner": "o/r"}},
     "fieldValueByName": {"name": "Doing"}},
])
STATION_PAGE2_JSON = _station_page(3, False, None, [
    {"content": {"number": 2, "repository": {"nameWithOwner": "o/r"}},
     "fieldValueByName": {"name": "Doing"}},
    {"content": {"number": 3, "repository": {"nameWithOwner": "o/r"}},
     "fieldValueByName": {"name": "Doing"}},
])
fake, calls = recorder([Result(0, stdout=STATION_PAGE1_JSON), Result(0, stdout=STATION_PAGE2_JSON)])
fgh.subprocess.run = fake
# Wrapped (P-04): a mutation that stops pagination after page 1 leaves items_out (1) short of
# totalCount (3), which trips the truncation guard tested separately below — an unguarded call
# here would let that raise crash the whole suite instead of reddening just these checks.
try:
    two_page_items = fgh.project_item_stations("owner", 3, "Station")
    two_page_exc = None
except Exception as e:
    two_page_items = None
    two_page_exc = e
    if isinstance(e, fgh.GhError):
        RAISED.append(e)
restore()
check("project_item_stations: two-page response makes exactly TWO calls",
      len(calls) == 2, f"calls={calls}")
check("project_item_stations: the second call carries the first page's endCursor",
      len(calls) == 2 and "cursor=CURSOR1" in calls[1]["argv"], f"calls={calls}")
check("project_item_stations: two-page response is fully accumulated (3 items)",
      two_page_exc is None and len(two_page_items) == 3,
      f"items={two_page_items} exc={two_page_exc}")
check("project_item_stations: the second page's items appear in the output",
      two_page_exc is None and {i["content"]["number"] for i in two_page_items} == {1, 2, 3},
      f"items={two_page_items} exc={two_page_exc}")

# ---- accumulated count below totalCount raises GhError ----
STATION_TRUNCATED_JSON = _station_page(5, False, None, [STATION_NODE_READY, STATION_NODE_DOING])
fake, calls = recorder([Result(0, stdout=STATION_TRUNCATED_JSON)])
fgh.subprocess.run = fake
try:
    fgh.project_item_stations("owner", 3, "Station")
    station_trunc_raised, station_trunc_exc = False, None
except Exception as e:
    station_trunc_raised = True
    station_trunc_exc = e
    if isinstance(e, fgh.GhError):
        RAISED.append(e)
restore()
check("project_item_stations: accumulated count below totalCount raises GhError",
      station_trunc_raised and isinstance(station_trunc_exc, fgh.GhError),
      f"exc={station_trunc_exc!r}")
check("project_item_stations: truncation message names both totals",
      station_trunc_raised and "5" in str(station_trunc_exc) and "2" in str(station_trunc_exc),
      f"exc={station_trunc_exc}")

# ---- missing totalCount on the first page raises GhError ----
STATION_NO_TOTAL_JSON = json.dumps({"data": {"user": {"projectV2": {"items": {
    "pageInfo": {"hasNextPage": False, "endCursor": None},
    "nodes": [STATION_NODE_READY],
}}}}})
fake, calls = recorder([Result(0, stdout=STATION_NO_TOTAL_JSON)])
fgh.subprocess.run = fake
try:
    fgh.project_item_stations("owner", 3, "Station")
    station_notot_raised, station_notot_exc = False, None
except Exception as e:
    station_notot_raised = True
    station_notot_exc = e
    if isinstance(e, fgh.GhError):
        RAISED.append(e)
restore()
check("project_item_stations: a response missing totalCount raises GhError, "
      "never defaults it to 0",
      station_notot_raised and isinstance(station_notot_exc, fgh.GhError),
      f"exc={station_notot_exc!r}")

# ---- a null user (e.g. an organization-owned board) raises GhError, never an empty list ----
STATION_NULL_USER_JSON = json.dumps({"data": {"user": None}})
fake, calls = recorder([Result(0, stdout=STATION_NULL_USER_JSON)])
fgh.subprocess.run = fake
try:
    fgh.project_item_stations("acmeorg", 3, "Station")
    station_nouser_raised, station_nouser_exc = False, None
except Exception as e:
    station_nouser_raised = True
    station_nouser_exc = e
    if isinstance(e, fgh.GhError):
        RAISED.append(e)
restore()
check("project_item_stations: a null user (organization-owned board) raises GhError, "
      "never returns an empty list",
      station_nouser_raised and isinstance(station_nouser_exc, fgh.GhError),
      f"exc={station_nouser_exc!r}")

# ---- argv shape and query selection guard: -F for owner/number/field/cursor, -f for query,
# and the selection stays narrow (no widened fieldValues connection) ----
fake, calls = recorder([Result(0, stdout=STATION_SINGLE_PAGE_JSON)])
fgh.subprocess.run = fake
try:
    fgh.project_item_stations("owner", 3, "Station")
except Exception as _e:
    if isinstance(_e, fgh.GhError):
        RAISED.append(_e)
restore()
_sargv = calls[0]["argv"]
check("project_item_stations: argv passes owner/number/field/cursor as -F and query as -f",
      _sargv[1:3] == ["api", "graphql"]
      and "-F" in _sargv and "owner=owner" in _sargv and "number=3" in _sargv
      and "field=Station" in _sargv and "cursor=null" in _sargv,
      f"argv={_sargv}")
_squery = ""
for _i, _a in enumerate(_sargv):
    if _a == "-f" and _i + 1 < len(_sargv) and _sargv[_i + 1].startswith("query="):
        _squery = _sargv[_i + 1][len("query="):]
import re as _re_station
check("project_item_stations: query has no widened plural fieldValues connection",
      _re_station.search(r"fieldValues\s*\(", _squery) is None, f"q={_squery!r}")


# ---------------- issue_board_item_id: one targeted call, no whole-board scan (D-01) ----------
# THE DISCRIMINATION IS THE POINT (D-03): absence (issue.issue null, or a recognised nodes list
# with no match) returns None; only an unrecognised or truncated shape raises.

fake, calls = recorder([Result(0, stdout=ISSUE_ITEM_MATCH_JSON)])
fgh.subprocess.run = fake
match_id = fgh.issue_board_item_id("acme/widget", 42, 9)
restore()
check("issue_board_item_id: made exactly ONE call",
      len(calls) == 1, f"calls={calls}")
check("issue_board_item_id: that one call is gh api graphql",
      calls and calls[0]["argv"][1:3] == ["api", "graphql"], f"calls={calls}")
check("issue_board_item_id: ZERO calls hit project item-list",
      not any(c["argv"][1:3] == ["project", "item-list"] for c in calls), f"calls={calls}")
argv0 = calls[0]["argv"] if calls else []
check("issue_board_item_id: argv carries the issue number",
      "number=42" in argv0, f"argv={argv0}")
check("issue_board_item_id: argv carries both repository halves",
      "owner=acme" in argv0 and "name=widget" in argv0, f"argv={argv0}")
check("issue_board_item_id: returns the matching node's id when project.number == board_number",
      match_id == "ITEM1", f"match_id={match_id!r}")

# FIX 1 (FEAT-13 fix01): pin _ISSUE_ITEM_QUERY's issue(...) selection to carry EXACTLY the
# argument `number` — no `state`, `states`, `filterBy` or any other issue-state scoping. This is
# a STRUCTURAL check (the argument-name list inside `issue( ... )`), not a keyword blacklist and
# not an equality check on the whole query text, so it reddens under any state-scoping argument
# regardless of spelling and survives a pure whitespace/reformat of the query.
import re as _re_query
_issue_sel = _re_query.search(r"issue\s*\(([^)]*)\)", fgh._ISSUE_ITEM_QUERY)
_issue_arg_names = []
if _issue_sel:
    for _part in _issue_sel.group(1).split(","):
        _part = _part.strip()
        if _part:
            _issue_arg_names.append(_part.split(":")[0].strip())
check("issue_board_item_id: _ISSUE_ITEM_QUERY's issue(...) selection takes exactly the "
      "argument {number} — no state/filter argument of any spelling",
      _issue_arg_names == ["number"],
      f"arg_names={_issue_arg_names!r} query={fgh._ISSUE_ITEM_QUERY!r}")

fake, calls = recorder([Result(0, stdout=ISSUE_ITEM_OTHER_PROJECT_JSON)])
fgh.subprocess.run = fake
try:
    other_result = fgh.issue_board_item_id("acme/widget", 42, 9)
    other_raised = False
except fgh.GhError as e:
    other_raised, other_result = True, None
    RAISED.append(e)
restore()
check("issue_board_item_id: an item on a DIFFERENT project number returns None, does not raise",
      not other_raised and other_result is None, f"raised={other_raised} result={other_result!r}")

fake, calls = recorder([Result(0, stdout=ISSUE_ITEM_EMPTY_JSON)])
fgh.subprocess.run = fake
try:
    empty_result = fgh.issue_board_item_id("acme/widget", 42, 9)
    empty_raised = False
except fgh.GhError as e:
    empty_raised, empty_result = True, None
    RAISED.append(e)
restore()
check("issue_board_item_id: empty nodes list with totalCount 0 returns None, does not raise",
      not empty_raised and empty_result is None, f"raised={empty_raised} result={empty_result!r}")

fake, calls = recorder([Result(0, stdout=ISSUE_ITEM_ISSUE_NULL_JSON)])
fgh.subprocess.run = fake
try:
    null_issue_result = fgh.issue_board_item_id("acme/widget", 42, 9)
    null_issue_raised = False
except fgh.GhError as e:
    null_issue_raised, null_issue_result = True, None
    RAISED.append(e)
restore()
check("issue_board_item_id: repository.issue explicitly null returns None, does not raise",
      not null_issue_raised and null_issue_result is None,
      f"raised={null_issue_raised} result={null_issue_result!r}")

# ABSENT "issue" key is a DIFFERENT case from explicit null above — absence is an unrecognised
# shape and raises; only an explicit null is a real "issue does not exist" answer.
fake, calls = recorder([Result(0, stdout=ISSUE_ITEM_NO_ISSUE_KEY_JSON)])
fgh.subprocess.run = fake
try:
    fgh.issue_board_item_id("acme/widget", 42, 9)
    no_issue_key_raised = False
except fgh.GhError as e:
    no_issue_key_raised = True
    RAISED.append(e)
restore()
check("issue_board_item_id: repository dict with NO 'issue' key at all RAISES "
      "(distinct from the explicit-null case above)", no_issue_key_raised)

fake, calls = recorder([Result(0, stdout=ISSUE_ITEM_NO_PROJECTITEMS_JSON)])
fgh.subprocess.run = fake
try:
    fgh.issue_board_item_id("acme/widget", 42, 9)
    no_pi_raised = False
except fgh.GhError as e:
    no_pi_raised = True
    RAISED.append(e)
restore()
check("issue_board_item_id: issue with no 'projectItems' key RAISES", no_pi_raised)

fake, calls = recorder([Result(0, stdout=ISSUE_ITEM_NODES_NOT_LIST_JSON)])
fgh.subprocess.run = fake
try:
    fgh.issue_board_item_id("acme/widget", 42, 9)
    nodes_raised = False
except fgh.GhError as e:
    nodes_raised = True
    RAISED.append(e)
restore()
check("issue_board_item_id: projectItems.nodes not a list RAISES", nodes_raised)

fake, calls = recorder([Result(0, stdout=ISSUE_ITEM_NO_TOTALCOUNT_JSON)])
fgh.subprocess.run = fake
try:
    fgh.issue_board_item_id("acme/widget", 42, 9)
    no_total_raised = False
except fgh.GhError as e:
    no_total_raised = True
    RAISED.append(e)
restore()
check("issue_board_item_id: projectItems with no 'totalCount' key RAISES "
      "(never defaults to 0)", no_total_raised)

fake, calls = recorder([Result(0, stdout=ISSUE_ITEM_TOTALCOUNT_STRING_JSON)])
fgh.subprocess.run = fake
try:
    fgh.issue_board_item_id("acme/widget", 42, 9)
    total_str_raised, total_str_type = False, None
except Exception as e:
    total_str_raised, total_str_type = True, type(e)
    if isinstance(e, fgh.GhError):
        RAISED.append(e)
restore()
check("issue_board_item_id: a string totalCount raises GhError, NOT a bare TypeError",
      total_str_raised and total_str_type is fgh.GhError, f"type={total_str_type}")

fake, calls = recorder([Result(0, stdout=ISSUE_ITEM_TRUNCATED_JSON)])
fgh.subprocess.run = fake
try:
    fgh.issue_board_item_id("acme/widget", 42, 9)
    trunc_raised, trunc_exc = False, None
except fgh.GhError as e:
    trunc_raised, trunc_exc = True, e
    RAISED.append(e)
restore()
check("issue_board_item_id: totalCount 3 with one node RAISES", trunc_raised)
check("issue_board_item_id: truncation message names the totals",
      trunc_raised and "3" in str(trunc_exc) and "1" in str(trunc_exc),
      f"exc={trunc_exc if trunc_raised else None}")

fake, calls = recorder([Result(0, stdout=ISSUE_ITEM_NODE_NO_ID_JSON)])
fgh.subprocess.run = fake
try:
    fgh.issue_board_item_id("acme/widget", 42, 9)
    no_id_raised = False
except fgh.GhError as e:
    no_id_raised = True
    RAISED.append(e)
restore()
check("issue_board_item_id: a node missing 'id' RAISES", no_id_raised)

fake, calls = recorder([Result(0, stdout=ISSUE_ITEM_NODE_NO_PROJECT_JSON)])
fgh.subprocess.run = fake
try:
    fgh.issue_board_item_id("acme/widget", 42, 9)
    no_project_raised = False
except fgh.GhError as e:
    no_project_raised = True
    RAISED.append(e)
restore()
check("issue_board_item_id: a node missing 'project' RAISES", no_project_raised)

fake, calls = recorder([Result(0, stdout=ISSUE_ITEM_NULL_REPOSITORY_JSON)])
fgh.subprocess.run = fake
try:
    fgh.issue_board_item_id("acme/widget", 42, 9)
    null_repo_raised, null_repo_exc = False, None
except fgh.GhError as e:
    null_repo_raised, null_repo_exc = True, e
    RAISED.append(e)
restore()
check("issue_board_item_id: a null repository RAISES, naming the repository, "
      "not the generic graphql-call-failed text",
      null_repo_raised and "acme/widget" in str(null_repo_exc)
      and "gh graphql call failed" not in str(null_repo_exc),
      f"exc={null_repo_exc if null_repo_raised else None}")

# a non-diagnosable transport failure (no JSON on stdout at all) still raises GhError, naming
# the repo and issue number — mirrors _project_field_resolve's partial-failure recovery shape.
fake, calls = recorder([Result(1, stdout="", stderr="gh: API error")])
fgh.subprocess.run = fake
try:
    fgh.issue_board_item_id("acme/widget", 42, 9)
    transport_raised, transport_exc = False, None
except fgh.GhError as e:
    transport_raised, transport_exc = True, e
    RAISED.append(e)
restore()
check("issue_board_item_id: a non-diagnosable transport failure raises GhError",
      transport_raised, f"exc={transport_exc}")
check("issue_board_item_id: transport-failure message names the repo and issue number",
      transport_raised and "acme/widget" in str(transport_exc) and "42" in str(transport_exc),
      f"exc={transport_exc if transport_raised else None}")

# a malformed repository string (no exactly-two-part split) raises before any call is made.
fake, calls = recorder([])
fgh.subprocess.run = fake
try:
    fgh.issue_board_item_id("not-a-valid-repo", 1, 9)
    malformed_raised = False
except fgh.GhError as e:
    malformed_raised = True
    RAISED.append(e)
restore()
check("issue_board_item_id: a malformed repository string raises before any call",
      malformed_raised and calls == [], f"calls={calls}")
check("issue_board_item_id: malformed-repository message names the repository",
      malformed_raised and "not-a-valid-repo" in str(RAISED[-1]), f"exc={RAISED[-1]}")


# ---------------- project_field_options ----------------
fake, calls = recorder([Result(0, stdout=GRAPHQL_FIELD_JSON)])
fgh.subprocess.run = fake
try:
    opts = fgh.project_field_options("owner", 3, "Station")
except fgh.GhError as e:
    opts = None
    RAISED.append(e)
restore()
check("project_field_options: returns the option names",
      opts == ["Ready", "Doing"], f"opts={opts!r}")

fake, calls = recorder([Result(1, stdout=GRAPHQL_FIELD_ABSENT_JSON, stderr="gh: not found")])
fgh.subprocess.run = fake
try:
    fgh.project_field_options("owner", 3, "NoSuchField")
    raised = False
except fgh.GhError as e:
    raised, exc = True, e
    RAISED.append(e)
restore()
check("project_field_options: raises GhError naming the absent field",
      raised and "NoSuchField" in str(exc), f"exc={exc if raised else None}")
# D-04 freeze: the rendered next_step, byte for byte, for THIS case's own arguments.
check("project_field_options: absent-field message is the D-04-frozen rendered string",
      raised and "field-list for owner project 3 does not offer it" in str(exc),
      f"exc={exc if raised else None}")
check("project_field_options: absent-field message carries no generic subcommand fallback",
      raised and "api graphql" not in str(exc), f"exc={exc if raised else None}")


# ---------------- default_branch_sha ----------------
fake, calls = recorder([Result(0, stdout="deadbeef\n")])
fgh.subprocess.run = fake
sha = fgh.default_branch_sha("o/r", "main")
restore()
check("default_branch_sha: returns the sha", sha == "deadbeef", f"sha={sha!r}")
check("default_branch_sha: hits the ref/heads path",
      any("git/ref/heads/main" in a for a in calls[0]["argv"]), f"calls={calls}")


# ---------------- file_at_ref ----------------
fake, calls = recorder([Result(0, stdout=base64.b64encode(b"hello world").decode() + "\n")])
fgh.subprocess.run = fake
text = fgh.file_at_ref("o/r", "path/to/file.txt", "main")
restore()
check("file_at_ref: returns the decoded file body", text == "hello world", f"text={text!r}")

fake, calls = recorder([Result(0, stdout=base64.b64encode(b"x").decode())])
fgh.subprocess.run = fake
fgh.file_at_ref("o/r", "path/to/file.txt", "main")
restore()
check("file_at_ref: hits the contents path with the ref",
      any("repos/o/r/contents/path/to/file.txt" in a for a in calls[0]["argv"])
      and any("ref=main" in a for a in calls[0]["argv"])
      and any("repos/o/r/contents/path/to/file.txt" in a and "?ref=main" in a
              for a in calls[0]["argv"])
      and "-f" not in calls[0]["argv"], f"calls={calls}")

fake, calls = recorder([Result(1, stdout="", stderr="404 Not Found")])
fgh.subprocess.run = fake
try:
    fgh.file_at_ref("o/r", "missing/file.txt", "release-branch")
    raised, exc = False, None
except fgh.GhError as e:
    raised, exc = True, e
    RAISED.append(e)
restore()
check("file_at_ref: a missing file raises GhError naming repo, path and ref",
      raised
      and "o/r" in str(exc)
      and "missing/file.txt" in str(exc)
      and "release-branch" in str(exc),
      f"exc={exc}")

fake, calls = recorder([Result(0, stdout="not-valid-base64!!!")])
fgh.subprocess.run = fake
try:
    fgh.file_at_ref("o/r", "path/x", "main")
    raised, exc = False, None
except fgh.GhError as e:
    raised, exc = True, e
    RAISED.append(e)
restore()
check("file_at_ref: undecodable content raises rather than returning empty", raised, f"exc={exc}")

# "aGV!sbG8=" reduces to 8 base64-alphabet chars (8 % 4 == 0), so it never trips a padding
# error — it can only be caught by validate=True rejecting the embedded "!". A padding-error
# fixture (like "not-valid-base64!!!" above) cannot see the validate flag at all.
fake, calls = recorder([Result(0, stdout="aGV!sbG8=")])
fgh.subprocess.run = fake
try:
    fgh.file_at_ref("o/r", "path/lax", "main")
    raised, exc = False, None
except fgh.GhError as e:
    raised, exc = True, e
    RAISED.append(e)
restore()
check("file_at_ref: non-alphabet character in otherwise valid-length base64 raises", raised, f"exc={exc}")

# GitHub's real contents endpoint line-wraps base64 at 60 chars (embedded newlines, not just a
# trailing one) — a fake that returns unwrapped base64 can never catch a decoder that chokes on
# that wrapping.
_wrap_text = b"the quick brown fox jumps over the lazy dog " * 5
_wrap_enc = base64.b64encode(_wrap_text).decode()
_wrap_body = "\n".join(_wrap_enc[i:i + 60] for i in range(0, len(_wrap_enc), 60)) + "\n"
fake, calls = recorder([Result(0, stdout=_wrap_body)])
fgh.subprocess.run = fake
try:
    wrapped_text = fgh.file_at_ref("o/r", "path/to/wrapped.txt", "main")
except fgh.GhError as e:
    wrapped_text = None
    _wrap_exc = e
else:
    _wrap_exc = None
restore()
check("file_at_ref: decodes GitHub's line-wrapped base64 content",
      wrapped_text == _wrap_text.decode(),
      f"wrapped_text={wrapped_text!r} exc={_wrap_exc}")

fake, calls = recorder([Result(0, stdout="null")])
fgh.subprocess.run = fake
try:
    fgh.file_at_ref("o/r", "adir", "main")
    raised, exc = False, None
except fgh.GhError as e:
    raised, exc = True, e
    RAISED.append(e)
restore()
check("file_at_ref: an absent content field raises rather than defaulting", raised, f"exc={exc}")


# ---------------- delete_ref ----------------
fake, calls = recorder([Result(0)])
fgh.subprocess.run = fake
fgh.delete_ref("o/r", "refs/heads/factory/issue-1")
restore()
check("delete_ref: hits the DELETE endpoint for the ref name",
      any("git/refs/heads/factory/issue-1" in a for a in calls[0]["argv"]), f"calls={calls}")


# ---------------- internal_id: the trap, in the only form a test can see it ----------------
fake, calls = recorder([Result(0, stdout="998877\n")])
fgh.subprocess.run = fake
val = fgh.internal_id("o/r", 7)
restore()
check("internal_id: returns an int parsed from the output",
      val == 998877 and isinstance(val, int), f"val={val!r}")
check("internal_id: the recorded argv's first element is never 'issue' (never issue view)",
      calls[0]["argv"][0] != "issue", f"argv={calls[0]['argv']}")
check("internal_id: hits the REST path repos/<owner/name>/issues/<n> with --jq .id",
      "repos/o/r/issues/7" in calls[0]["argv"] and "--jq" in calls[0]["argv"], f"calls={calls}")


# ---------------- attach_sub_issue / blocked_by: two endpoints, never collapsed ----------------
fake, calls = recorder([Result(0)])
fgh.subprocess.run = fake
fgh.attach_sub_issue("o/r", 5, 999)
restore()
check("attach_sub_issue: argv path ends in /sub_issues",
      any(a.endswith("/sub_issues") for a in calls[0]["argv"]), f"calls={calls}")

fake, calls = recorder([Result(0)])
fgh.subprocess.run = fake
fgh.blocked_by("o/r", 5, 1000)
restore()
check("blocked_by: argv path ends in /dependencies/blocked_by",
      any(a.endswith("/dependencies/blocked_by") for a in calls[0]["argv"]), f"calls={calls}")


# ---------------- all three edge functions go through run_gh, never gh_issues.gh_bin ----------------
edge_calls = []


def fake_run_gh(args, json_out=False):
    edge_calls.append(args)
    return "1"


def gh_bin_boom():
    raise AssertionError("gh_issues.gh_bin() must never be called — it escapes FACTORY_GH")


fgh.run_gh = fake_run_gh
gh_issues.gh_bin = gh_bin_boom
try:
    fgh.internal_id("o/r", 1)
    fgh.attach_sub_issue("o/r", 1, 2)
    fgh.blocked_by("o/r", 1, 2)
    escaped = False
except AssertionError:
    escaped = True
restore()
check("edge functions: all three route through run_gh and never reach gh_issues.gh_bin",
      not escaped and len(edge_calls) == 3, f"edge_calls={edge_calls}, escaped={escaped}")


# ---------------- no helper writes to stdout ----------------
def with_recorder(results, fn, *a, **kw):
    fake, calls = recorder(results)
    fgh.subprocess.run = fake
    try:
        result, out = silent_stdout(fn, *a, **kw)
    finally:
        restore()
    return result, out, calls


_, out, _ = with_recorder([Result(0, stdout="ok")], fgh.run_gh, ["auth", "status"])
check("run_gh: writes nothing to stdout on success", out == "", f"out={out!r}")

_, out, _ = with_recorder(
    [Result(0, stdout="https://github.com/o/r/issues/1\n")],
    fgh.create_issue, "o/r", "t", "b", [],
)
check("create_issue: writes nothing to stdout", out == "", f"out={out!r}")

_, out, _ = with_recorder([Result(0), Result(0)], fgh.ensure_labels, "o/r", ["a", "b"])
check("ensure_labels: writes nothing to stdout", out == "", f"out={out!r}")

_, out, _ = with_recorder(
    [Result(0, stdout=json.dumps(PROJECT_ITEMS_2))], fgh.project_items, "o", 3,
)
check("project_items: writes nothing to stdout", out == "", f"out={out!r}")

_, out, _ = with_recorder(
    [Result(0, stdout=GRAPHQL_FIELD_JSON)], fgh.project_field_options, "owner", 3, "Station",
)
check("project_field_options: writes nothing to stdout", out == "", f"out={out!r}")

_, out, _ = with_recorder([Result(0, stdout="55\n")], fgh.internal_id, "o/r", 3)
check("internal_id: writes nothing to stdout", out == "", f"out={out!r}")

_, out, _ = with_recorder([Result(0)], fgh.attach_sub_issue, "o/r", 5, 999)
check("attach_sub_issue: writes nothing to stdout", out == "", f"out={out!r}")

_, out, _ = with_recorder([Result(0)], fgh.blocked_by, "o/r", 5, 999)
check("blocked_by: writes nothing to stdout", out == "", f"out={out!r}")

_, out, _ = with_recorder([Result(0)], fgh.create_ref, "o/r", "refs/heads/x", "sha")
check("create_ref: writes nothing to stdout on success", out == "", f"out={out!r}")

_, out, _ = with_recorder(
    [Result(1, stdout='{"status":"422"}', stderr="gh: Reference already exists (HTTP 422)")],
    fgh.create_ref, "o/r", "refs/heads/x", "sha",
)
check("create_ref: writes nothing to stdout on the measured conflict", out == "", f"out={out!r}")

_, out, _ = with_recorder(
    [Result(0, stdout=GRAPHQL_FIELD_JSON), Result(0, stdout="")],
    fgh.project_field_set, "owner", 3, "ITEM1", "Station", "Ready",
)
check("project_field_set: writes nothing to stdout", out == "", f"out={out!r}")

_, out, _ = with_recorder(
    [Result(0, stdout="{}")], fgh.issue_view, "o/r", 9, ["title"],
)
check("issue_view: writes nothing to stdout", out == "", f"out={out!r}")

_, out, _ = with_recorder([Result(0)], fgh.add_label, "o/r", 9, "harness")
check("add_label: writes nothing to stdout", out == "", f"out={out!r}")

_, out, _ = with_recorder([Result(0)], fgh.assign, "o/r", 9, "mruangutai")
check("assign: writes nothing to stdout", out == "", f"out={out!r}")

_, out, _ = with_recorder(
    [Result(0, stdout='{"id":"PVTI_1"}')],
    fgh.project_item_add, "owner", 3, "https://github.com/o/r/issues/9",
)
check("project_item_add: writes nothing to stdout", out == "", f"out={out!r}")

_, out, _ = with_recorder([Result(0, stdout="deadbeef\n")], fgh.default_branch_sha, "o/r", "main")
check("default_branch_sha: writes nothing to stdout", out == "", f"out={out!r}")

_, out, _ = with_recorder([Result(0)], fgh.delete_ref, "o/r", "refs/heads/factory/issue-1")
check("delete_ref: writes nothing to stdout", out == "", f"out={out!r}")


# ---------------- run_gh: rate-limit failure names the GraphQL budget (T-04, FEAT-29) ----------
import datetime as _dt

_RESET_EPOCH = 1755600000
_RESET_ISO = _dt.datetime.fromtimestamp(_RESET_EPOCH, tz=_dt.timezone.utc).isoformat().replace(
    "+00:00", "Z")
_RATE_LIMIT_JSON = json.dumps({
    "resources": {
        "graphql": {"limit": 5000, "used": 5000, "remaining": 0, "reset": _RESET_EPOCH},
        "core": {"limit": 5000, "used": 42, "remaining": 4958, "reset": _RESET_EPOCH},
    }
})

fake, calls = recorder([
    Result(1, stdout="", stderr="API rate limit exceeded for installation ID 123."),
    Result(0, stdout=_RATE_LIMIT_JSON),
])
fgh.subprocess.run = fake
try:
    fgh.run_gh(["api", "graphql", "-f", "query=whatever"])
    exc = None
except Exception as e:
    exc = e
    if isinstance(e, fgh.GhError):
        RAISED.append(e)
restore()
msg = str(exc) if exc is not None else ""
check("run_gh: rate-limit failure raises GhError", isinstance(exc, fgh.GhError), f"exc={exc!r}")
check("run_gh: budget message names GraphQL", "GraphQL" in msg, f"msg={msg!r}")
check("run_gh: budget message carries used and limit points",
      "5000" in msg, f"msg={msg!r}")
check("run_gh: budget message carries the reset UTC ISO 8601 timestamp",
      _RESET_ISO in msg, f"msg={msg!r} expected={_RESET_ISO!r}")
check("run_gh: budget remedy names REST's own usage",
      "42" in msg, f"msg={msg!r}")
check("run_gh: original gh stderr is preserved as detail",
      exc is not None and "API rate limit exceeded" in (exc.stderr or ""), f"exc={exc!r}")
check("run_gh: queried rate_limit exactly once, after the failing call",
      len(calls) == 2 and calls[1]["argv"][-2:] == ["api", "rate_limit"], f"calls={calls}")


# ---------------- run_gh: an unrelated exit-1 does NOT produce the budget message -----------------
# The discriminator (plan T-04): detection must be on message TEXT, never exit code alone. A
# second Result is queued for the same reason as the non-zero-exit and preflight fixtures above
# (FEAT-29 T-04 cycle 3): under a mutant that widens _RATE_LIMIT_MARKERS to also match this
# fixture's own text, this call is misrouted into the rate_limit budget path, which makes a
# SECOND subprocess call (`gh api rate_limit`) to build its message. Unmutated code never takes
# that path — this call is never made and the second Result is simply never consumed, per
# `recorder`'s own contract (it raises only when it runs out). It is a SUCCESS (exit 0, the same
# `_RATE_LIMIT_JSON` fixture the real rate-limit test above uses), not another failure — only a
# successful budget read produces the "GraphQL budget exhausted" headline this check watches for;
# a second failure would route to the other, "could not be read", message instead and never
# exercise the discriminator's own text.
fake, calls = recorder([
    Result(1, stdout="", stderr="could not resolve to a Repository with the name 'o/nope'"),
    Result(0, stdout=_RATE_LIMIT_JSON),
])
fgh.subprocess.run = fake
try:
    fgh.run_gh(["issue", "view", "1", "--repo", "o/nope"])
    exc2 = None
except Exception as e:
    exc2 = e
    if isinstance(e, fgh.GhError):
        RAISED.append(e)
restore()
msg2 = str(exc2) if exc2 is not None else ""
check("run_gh: unrelated exit-1 raises a plain GhError, not a budget error",
      isinstance(exc2, fgh.GhError), f"exc={exc2!r}")
check("run_gh: unrelated failure never contains the GraphQL budget headline",
      "GraphQL budget exhausted" not in msg2, f"msg={msg2!r}")
check("run_gh: unrelated failure message preserves the original gh text",
      "could not resolve to a Repository" in msg2, f"msg={msg2!r}")


# ---------------- run_gh: rate-limit failure whose own budget read fails ---------------------------
fake, calls = recorder([
    Result(1, stdout="", stderr="was submitted too quickly"),
    Result(1, stdout="", stderr="gh: not logged in"),
])
fgh.subprocess.run = fake
try:
    fgh.run_gh(["api", "graphql", "-f", "query=whatever"])
    exc3 = None
except Exception as e:
    exc3 = e
    if isinstance(e, fgh.GhError):
        RAISED.append(e)
restore()
msg3 = str(exc3) if exc3 is not None else ""
check("run_gh: a rate-limit failure whose budget read also fails still raises GhError",
      isinstance(exc3, fgh.GhError), f"exc={exc3!r}")
check("run_gh: budget-read failure names its own message, not the original rate-limit text",
      "the budget could not be read" in msg3, f"msg={msg3!r}")
check("run_gh: budget-read failure preserves the original rate-limit stderr as detail",
      exc3 is not None and "was submitted too quickly" in (exc3.stderr or ""), f"exc={exc3!r}")


# ---------------- every GhError raised above: em dash, concrete value, no class name/traceback --
check("GhError invariant: at least one case was collected", len(RAISED) >= 10, f"n={len(RAISED)}")
for exc in RAISED:
    m = str(exc)
    _, _, rest = m.partition(": ")
    value, _, _ = rest.partition(" — ")
    check(f"GhError invariant holds for {m[:60]!r}",
          "—" in m and "GhError" not in m and "Traceback" not in m and value.strip() != "",
          f"msg={m!r}")


print(f"\n{RAN - FAILS}/{RAN} checks passed." if FAILS == 0 else f"\n{FAILS} of {RAN} FAILING.")
sys.exit(1 if FAILS else 0)
