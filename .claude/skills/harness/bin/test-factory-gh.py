#!/usr/bin/env python3
"""Tests for factory_gh.py, the single seam every factory tool talks to GitHub through (D-02, D-14).

WHY: this module's whole job is deciding failure behaviour once — loud (GhError), never a
swallowed default — and routing the three DAG edge functions through gh_issues' argv builders
so FACTORY_GH cannot be silently bypassed (the T-12 stub-gh escape named in the plan). Every
case here monkeypatches subprocess.run or run_gh with an in-process recorder; nothing spawns a
real gh (run-unit-tests.sh classifies this as UNIT for exactly that reason).
"""
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


FIELD_LIST_JSON = json.dumps({
    "fields": [
        {"id": "F1", "name": "Station", "options": [
            {"id": "O1", "name": "Ready"},
            {"id": "O2", "name": "Doing"},
        ]}
    ]
})

PROJECT_VIEW_JSON = json.dumps({"id": "PVT_kwFAKE", "number": 3, "title": "board"})


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


# ---------------- project_field_set: resolves ids before editing ----------------
fake, calls = recorder([
    Result(0, stdout=FIELD_LIST_JSON), Result(0, stdout=PROJECT_VIEW_JSON), Result(0, stdout=""),
])
fgh.subprocess.run = fake
fgh.project_field_set("owner", 3, "ITEM1", "Station", "Ready")
restore()
check("project_field_set: reads field-list, then project-view, then item-edit",
      len(calls) == 3, f"calls={calls}")
check("project_field_set: resolves the field id",
      "F1" in calls[2]["argv"], f"argv={calls[2]['argv']}")
check("project_field_set: resolves the option id",
      "O1" in calls[2]["argv"], f"argv={calls[2]['argv']}")

fake, calls = recorder([Result(0, stdout=FIELD_LIST_JSON)])
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


# ---------------- project_field_set: --project-id must be the node id, not the board number ----
# argv-DISPATCHING fake, not a positional list: a positional 3-result list would let a
# field-list-then-item-edit-only implementation (the bug) consume the project-view result as its
# field-list call and die on "project field not found" instead — a red that proves nothing about
# --project-id. Dispatching on argv prefix means the buggy code (which never calls
# ["project","view"] at all) still runs to completion, so the failure is a clean VALUE mismatch.
fake, calls = dispatching_fake({
    ("project", "field-list"): Result(0, stdout=FIELD_LIST_JSON),
    ("project", "view"): Result(0, stdout=PROJECT_VIEW_JSON),
}, default=Result(0, stdout=""))
fgh.subprocess.run = fake
fgh.project_field_set("owner", 3, "ITEM1", "Station", "Ready")
restore()
edit_calls = [c for c in calls if c["argv"][1:3] == ["project", "item-edit"]]
check("project_field_set: exactly one item-edit call was made", len(edit_calls) == 1,
      f"calls={calls}")
if edit_calls:
    argv = edit_calls[0]["argv"]
    check("project_field_set: --project-id is present in the item-edit argv",
          "--project-id" in argv, f"argv={argv}")
    if "--project-id" in argv:
        pid = argv[argv.index("--project-id") + 1]
        check("project_field_set: --project-id carries the id from `project view`, "
              "NOT the bare board number",
              pid == "PVT_kwFAKE" and pid != "3", f"--project-id={pid!r} argv={argv}")


# ---------------- project_field_set: a failed `project view` RAISES, never falls back ----------
# The miss case: if the id lookup fails, this must not silently reuse str(number) as
# --project-id (that would resurrect the bug under a different trigger — D-02, never swallow).
fake, calls = dispatching_fake({
    ("project", "field-list"): Result(0, stdout=FIELD_LIST_JSON),
    ("project", "view"): Result(1, stderr="gh: project not found"),
}, default=Result(0, stdout=""))
fgh.subprocess.run = fake
try:
    fgh.project_field_set("owner", 3, "ITEM1", "Station", "Ready")
    raised, exc = False, None
except fgh.GhError as e:
    raised, exc = True, e
    RAISED.append(e)
restore()
check("project_field_set: a failed `project view` raises GhError",
      raised, f"exc={exc if raised else None}")
check("project_field_set: a failed `project view` makes ZERO item-edit calls "
      "(never falls back to the bare number)",
      not any(c["argv"][1:3] == ["project", "item-edit"] for c in calls), f"calls={calls}")


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


# ---------------- project_field_options ----------------
fake, calls = recorder([Result(0, stdout=FIELD_LIST_JSON)])
fgh.subprocess.run = fake
opts = fgh.project_field_options("owner", 3, "Station")
restore()
check("project_field_options: returns the option names",
      opts == ["Ready", "Doing"], f"opts={opts!r}")

fake, calls = recorder([Result(0, stdout=FIELD_LIST_JSON)])
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


# ---------------- default_branch_sha ----------------
fake, calls = recorder([Result(0, stdout="deadbeef\n")])
fgh.subprocess.run = fake
sha = fgh.default_branch_sha("o/r", "main")
restore()
check("default_branch_sha: returns the sha", sha == "deadbeef", f"sha={sha!r}")
check("default_branch_sha: hits the ref/heads path",
      any("git/ref/heads/main" in a for a in calls[0]["argv"]), f"calls={calls}")


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
    [Result(0, stdout=FIELD_LIST_JSON)], fgh.project_field_options, "owner", 3, "Station",
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
    [Result(0, stdout=FIELD_LIST_JSON), Result(0, stdout=PROJECT_VIEW_JSON), Result(0, stdout="")],
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
