#!/usr/bin/env python3
"""Tests for factory_land.py — the last step of the journey, opening a pull request (T-07,
REQ-05).

Nothing here spawns a subprocess, touches a real repository, or makes a real gh/git call.
`factory_workspace.run_git` and `factory_gh`'s public functions are monkeypatched over a single
`Recorder`, whose ordered `.git_calls` / `.gh_calls` lists are the evidence every assertion below
is a projection of.
"""
import contextlib
import io
import json
import os
import sys
import tempfile

import yaml

import factory_cli
import factory_config as fc
import factory_gh
import factory_land as land
import factory_workspace as fw

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
ISSUE = 42
BRANCH = f"factory/issue-{ISSUE}"
ISSUE_TITLE = "widget: do the thing"
PR_URL = "https://github.com/acme/widget/pull/99"
ITEM_ID = "PVTI_item99"


def good_fleet_dict(workspace_root, default_branch=DEFAULT_BRANCH, repos=None):
    return {
        "schema": "factory-fleet/1",
        "board": {
            "owner": OWNER,
            "number": BOARD,
            "station_field": STATION_FIELD,
            "stations": {"ready": "Ready", "building": "Building", "review": "Review"},
        },
        "repos": repos if repos is not None else [
            {"name": REPO, "default_branch": default_branch},
        ],
        "workspace_root": workspace_root,
    }


def write_yaml(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)
    return path


# --------------------------------------------------------------------------
# Recorder — a single ordered call log over run_git and factory_gh's public surface.
# --------------------------------------------------------------------------

class Recorder:
    def __init__(self):
        self.git_calls = []
        self.gh_calls = []
        self.items = [
            {"id": ITEM_ID, "content": {"number": ISSUE, "title": ISSUE_TITLE}},
        ]
        self.issue_title = ISSUE_TITLE
        self.issue_state = "OPEN"
        self.preflight_raises = None
        self.pr_create_raises = None
        self.field_options = {STATION_FIELD: ["Ready", "Building", "Review"]}
        self.field_ids = {STATION_FIELD: "FIELD_1"}
        self.option_ids = {"Ready": "OPT_R", "Building": "OPT_B", "Review": "OPT_V"}

    # --- run_git stand-in ---
    def run_git(self, args, cwd):
        self.git_calls.append((tuple(args), cwd))
        return ""

    # --- factory_gh's public surface used by factory_land ---
    def preflight(self):
        self.gh_calls.append(("preflight", ()))
        if self.preflight_raises is not None:
            raise self.preflight_raises

    def issue_view(self, repo, number, fields):
        self.gh_calls.append(("issue_view", (repo, number, tuple(fields))))
        return {"title": self.issue_title, "state": self.issue_state}

    def run_gh(self, args, json_out=False):
        self.gh_calls.append(("run_gh", (tuple(args), json_out)))
        if args[:2] == ["pr", "create"]:
            if self.pr_create_raises is not None:
                raise self.pr_create_raises
            return PR_URL + "\n"
        raise AssertionError(f"test bug: unexpected run_gh args {args!r}")

    def project_items(self, owner, number, query=None, limit=500):
        self.gh_calls.append(("project_items", (owner, number, query)))
        return list(self.items)

    def issue_board_item_id(self, repo, number, board_number):
        self.gh_calls.append(("issue_board_item_id", (repo, number, board_number)))
        for it in self.items:
            if (it.get("content") or {}).get("number") == number:
                return it.get("id")
        return None

    def project_field_set(self, owner, number, item_id, field, option):
        self.gh_calls.append(("project_field_set", (owner, number, item_id, field, option)))


PATCHED_GH = (
    "preflight", "issue_view", "run_gh", "project_items", "issue_board_item_id",
    "project_field_set",
)


def patch(rec):
    saved_gh = {name: getattr(factory_gh, name) for name in PATCHED_GH}
    for name in PATCHED_GH:
        setattr(factory_gh, name, getattr(rec, name))
    saved_run_git = fw.run_git
    fw.run_git = rec.run_git
    return saved_gh, saved_run_git


def unpatch(saved_gh, saved_run_git):
    for name, fn in saved_gh.items():
        setattr(factory_gh, name, fn)
    fw.run_git = saved_run_git


# --------------------------------------------------------------------------
# Driver.
# --------------------------------------------------------------------------

def run_main(rec, extra_args, workspace_root=None, fleet_dict=None):
    workspace_root = workspace_root or tempfile.mkdtemp(prefix="land-ws-")
    fleet_dir = tempfile.mkdtemp(prefix="land-fleet-")
    fleet_path = write_yaml(
        os.path.join(fleet_dir, "fleet.yaml"),
        fleet_dict if fleet_dict is not None else good_fleet_dict(workspace_root),
    )
    argv_saved = sys.argv
    sys.argv = ["factory_land.py", "--fleet", fleet_path] + extra_args
    saved_gh, saved_run_git = patch(rec)
    out, err = io.StringIO(), io.StringIO()
    code = None
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                factory_cli.run(
                    "land", land._main,
                    expected=(fc.FleetError, factory_gh.GhError),
                )
            except SystemExit as e:
                code = e.code
        if code is None:
            code = 0
    finally:
        sys.argv = argv_saved
        unpatch(saved_gh, saved_run_git)
    return code, out.getvalue(), err.getvalue(), workspace_root


# ==========================================================================
# M — the "at minimum" list.
# ==========================================================================

# (M1) happy path.
rec = Recorder()
code, out, err, ws = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)])
check("(M1) exits 0", code == 0, code)
push_calls = [c for c in rec.git_calls if c[0][0] == "push"]
check("(M1) pushes exactly one branch", len(push_calls) == 1, rec.git_calls)
check("(M1) push args are --set-upstream origin <branch>",
      push_calls and push_calls[0][0] == ("push", "--set-upstream", "origin", BRANCH),
      push_calls)
expected_ws_path = fc.workspace_path(good_fleet_dict(ws), REPO)
check("(M1) push runs against workspace_path's cwd",
      push_calls and push_calls[0][1] == expected_ws_path, (push_calls, expected_ws_path))
pr_create_calls = [c for c in rec.gh_calls if c[0] == "run_gh" and c[1][0][:2] == ("pr", "create")]
check("(M1) creates exactly one pull request", len(pr_create_calls) == 1, rec.gh_calls)
pr_argv = pr_create_calls[0][1][0]
check("(M1) pr create base is the fleet's default_branch",
      "--base" in pr_argv and pr_argv[pr_argv.index("--base") + 1] == DEFAULT_BRANCH, pr_argv)
check("(M1) pr create head is the branch",
      "--head" in pr_argv and pr_argv[pr_argv.index("--head") + 1] == BRANCH, pr_argv)
check("(M1) pr create body contains closes #<n>",
      "--body" in pr_argv and f"closes #{ISSUE}" in pr_argv[pr_argv.index("--body") + 1], pr_argv)
lookup_calls = [c for c in rec.gh_calls if c[0] == "issue_board_item_id"]
check("(M1) issue_board_item_id was called EXACTLY ONCE — the targeted lookup replaces the "
      "whole-board scan (FEAT-13, D-01)", len(lookup_calls) == 1, rec.gh_calls)
check("(M1) project_items was called ZERO times",
      not any(c[0] == "project_items" for c in rec.gh_calls), rec.gh_calls)
check("(M1) issue_board_item_id's first argument is the repository string (args.repo), "
      "NOT the bare board-owner login",
      lookup_calls and lookup_calls[0][1][0] == REPO, lookup_calls)
check("(M1) issue_board_item_id's first argument is explicitly NOT the board-owner login "
      "(the mis-wire this assertion exists to catch)",
      lookup_calls and lookup_calls[0][1][0] != OWNER, lookup_calls)
check("(M1) issue_board_item_id called with (repo, issue, board_number)",
      lookup_calls and lookup_calls[0][1] == (REPO, ISSUE, BOARD), lookup_calls)
field_set_calls = [c for c in rec.gh_calls if c[0] == "project_field_set"]
check("(M1) sets the station to Review", len(field_set_calls) == 1
      and field_set_calls[0][1][4] == "Review", field_set_calls)
payload = json.loads(out)
check("(M1) payload url is the created pull request url", payload.get("url") == PR_URL.strip(),
      payload)
check("(M1) payload carries repo, issue, branch", payload.get("repo") == REPO
      and payload.get("issue") == ISSUE and payload.get("branch") == BRANCH, payload)

# (M1-json) the happy path's whole stdout stream is exactly one JSON object.
rec = Recorder()
code, out, err, ws = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)])
try:
    json.loads(out)
    parsed_ok = True
except Exception:
    parsed_ok = False
check("(M1-json) stdout is a single json.loads-able stream", parsed_ok, out)

# (M2) a pull request already open for the head is NOT a failure.
rec = Recorder()
rec.pr_create_raises = factory_gh.GhError(
    ["pr", "create"], 1, "",
    f'a pull request for branch "{BRANCH}" into branch "{DEFAULT_BRANCH}" already exists:\n'
    f"{PR_URL}",
    "gh pr create failed", REPO, "n/a",
)
code, out, err, ws = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)])
check("(M2) still exits 0", code == 0, code)
field_set_calls = [c for c in rec.gh_calls if c[0] == "project_field_set"]
check("(M2) still sets the station", len(field_set_calls) == 1, rec.gh_calls)
payload = json.loads(out)
check("(M2) payload carries the existing pr's url", payload.get("url") == PR_URL, payload)
check("(M2) stderr mentions the url", PR_URL in err, err)

# (M2b) a GhError from pr create that is NOT the already-open shape stays fatal (test-factory-
# decompose.py's case (21) precedent: an unrelated GhError must not be swallowed as "already
# open", and the station must not advance on a pull request that was never created).
rec = Recorder()
rec.pr_create_raises = factory_gh.GhError(
    ["pr", "create"], 1, "", "authentication failed, run gh auth login",
    "gh pr create failed", REPO, "run gh auth login",
)
code, out, err, ws = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)])
check("(M2b) a non-already-open GhError stays fatal: exits 2", code == 2, code)
field_set_calls = [c for c in rec.gh_calls if c[0] == "project_field_set"]
check("(M2b) the station is never set on an unopened pull request", field_set_calls == [],
      rec.gh_calls)
check("(M2b) stdout empty", out == "", out)

# (M2c) the board carries no item for the issue: the miss BLOCKS rather than sailing through.
# The push has already happened by this point (point of no return), matching the intent's
# recovery note that every step from the push onward is safe to re-run.
rec = Recorder()
rec.items = []
code, out, err, ws = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)])
check("(M2c) a missing board item exits 2, not 0 or 1 (fail-closed on the miss)", code == 2, code)
field_set_calls = [c for c in rec.gh_calls if c[0] == "project_field_set"]
check("(M2c) the station is never set when no item was found", field_set_calls == [],
      rec.gh_calls)
check("(M2c) stdout empty", out == "", out)
check("(M2c) the pull request WAS already created before the miss was discovered",
      any(c[0] == "run_gh" and c[1][0][:2] == ("pr", "create") for c in rec.gh_calls),
      rec.gh_calls)

# (M3) an issue number whose branch would equal the default branch exits 2, zero calls.
rec = Recorder()
weird_default = f"factory/issue-{ISSUE}"
fleet_dict = good_fleet_dict(tempfile.mkdtemp(prefix="land-ws-"), default_branch=weird_default)
code, out, err, ws = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)], fleet_dict=fleet_dict)
check("(M3) exits 2", code == 2, code)
check("(M3) zero git calls", rec.git_calls == [], rec.git_calls)
check("(M3) zero gh calls", rec.gh_calls == [], rec.gh_calls)
check("(M3) stdout empty", out == "", out)
check("(M3) stderr names the branch", weird_default in err, err)

# (M4) a repository absent from the fleet exits 2, zero calls.
rec = Recorder()
code, out, err, ws = run_main(rec, ["--repo", "acme/other", "--issue", str(ISSUE)])
check("(M4) exits 2", code == 2, code)
check("(M4) zero git calls", rec.git_calls == [], rec.git_calls)
check("(M4) zero gh calls", rec.gh_calls == [], rec.gh_calls)
check("(M4) stdout empty", out == "", out)
check("(M4) stderr names the repository", "acme/other" in err, err)

# (M5) the recorded git argument lists contain no push of the default branch (anti-vacuum).
rec = Recorder()
code, out, err, ws = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)])
check("(M5) at least one git call was recorded (anti-vacuum)", len(rec.git_calls) > 0,
      rec.git_calls)
default_branch_pushes = [
    c for c in rec.git_calls
    if c[0][0] == "push" and DEFAULT_BRANCH in c[0]
]
check("(M5) no recorded git call pushes the default branch", default_branch_pushes == [],
      rec.git_calls)

# (M6) the recorded gh argument lists contain no merge subcommand (anti-vacuum).
rec = Recorder()
code, out, err, ws = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)])
check("(M6) at least one gh call was recorded (anti-vacuum)", len(rec.gh_calls) > 0, rec.gh_calls)
merge_calls = [
    c for c in rec.gh_calls
    if c[0] == "run_gh" and "merge" in c[1][0]
]
check("(M6) no recorded gh call contains a merge subcommand", merge_calls == [], rec.gh_calls)

# (M7) SC-07: a CLOSED issue fails at the SAME point in the sequence as today's is:open-filter
# miss — AFTER the branch push and AFTER the pull-request create — and the station is never
# set. Today this was a side effect of the is:open filter on the board read; now it is an
# explicit check on the widened issue_view(["title", "state"]) read (REQ-04, D-04).
rec = Recorder()
rec.issue_state = "CLOSED"
code, out, err, ws = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)])
check("(M7) a closed issue exits 2 (refused), not 0", code == 2, code)
check("(M7) stdout empty", out == "", out)
check("(M7) stderr names the issue", str(ISSUE) in err, err)
push_calls = [c for c in rec.git_calls if c[0][0] == "push"]
check("(M7) the push already happened before the closed-issue refusal", len(push_calls) == 1,
      rec.git_calls)
pr_create_calls = [c for c in rec.gh_calls if c[0] == "run_gh" and c[1][0][:2] == ("pr", "create")]
check("(M7) the pull request WAS already created before the closed-issue refusal",
      len(pr_create_calls) == 1, rec.gh_calls)
field_set_calls = [c for c in rec.gh_calls if c[0] == "project_field_set"]
check("(M7) the station is never set on a closed issue (field_set_calls == [])",
      field_set_calls == [], rec.gh_calls)

# ==========================================================================
# C-3 contract — three cases, captured with redirect_stdout/redirect_stderr.
# ==========================================================================

# (C1) happy path's stdout parses as JSON in a single json.loads of the whole stream.
rec = Recorder()
code, out, err, ws = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)])
check("(C1) code is 0", code == 0, code)
try:
    obj = json.loads(out)
    ok = isinstance(obj, dict)
except Exception:
    ok = False
check("(C1) whole stdout stream is one JSON object", ok, out)

# (C2) the default-branch guard writes nothing to stdout and one stderr line naming the branch.
rec = Recorder()
fleet_dict = good_fleet_dict(tempfile.mkdtemp(prefix="land-ws-"), default_branch=weird_default)
code, out, err, ws = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)], fleet_dict=fleet_dict)
check("(C2) exit 2", code == 2, code)
check("(C2) stdout empty", out == "", out)
err_lines = [l for l in err.splitlines() if l.strip()]
check("(C2) exactly one stderr line", len(err_lines) == 1, err)
check("(C2) that line names the branch", err_lines and weird_default in err_lines[0], err)

# (C3) a monkeypatched pr-create raising a plain ValueError makes the entry point exit 2, not 1.
rec = Recorder()
rec.pr_create_raises = ValueError("boom")
code, out, err, ws = run_main(rec, ["--repo", REPO, "--issue", str(ISSUE)])
check("(C3) exits 2, not 1", code == 2, code)
check("(C3) stdout empty", out == "", out)

print(f"\n{RAN - FAILS}/{RAN} checks passed." if FAILS == 0 else f"\n{FAILS} of {RAN} FAILING.")
sys.exit(1 if FAILS else 0)
