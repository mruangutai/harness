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
fake, calls = recorder([Result(1, stdout="", stderr="permission denied\nmore detail")])
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

fake, calls = recorder([Result(1, stderr="gh: not logged in")])
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
fake, calls = recorder([Result(0), Result(1, stderr="already frozen"), Result(0)])
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
      and any("ref=main" in a for a in calls[0]["argv"]), f"calls={calls}")

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
