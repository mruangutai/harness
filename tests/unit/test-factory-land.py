#!/usr/bin/env python3
"""Tests for factory_land.py — the last step of the journey, opening a pull request (T-07,
REQ-05).

Nothing here spawns a subprocess, touches a real repository, or makes a real gh/git call.
`factory_workspace.run_git` and the `github` package's public functions are monkeypatched over a single
`Recorder`, whose ordered `.git_calls` / `.gh_calls` lists are the evidence every assertion below
is a projection of.
"""
from unit_support import ROOT  # noqa: F401  (puts bin/ and tests/ on sys.path)

import contextlib
import json
import sys
import tempfile
from unittest import mock

import artifact_accessors
import factory_cli
import factory_config as fc
import github.issues
import github.projects
import github.transport
import factory_land as land
import factory_workspace as fw
from check_support import Checks
from factory_support import board, board_stub, fleet, invoke, repo, split_boards, write_fleet

C = Checks()
check = C.check

# One temp root for every scenario, removed when the interpreter exits.
TMP = tempfile.TemporaryDirectory(prefix="land-")

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
LAND_ARGS = ["--repo", REPO, "--issue", str(ISSUE)]


def good_fleet_dict(workspace_root, default_branch=DEFAULT_BRANCH):
    return fleet(workspace_root,
                 [repo(REPO, default_branch, board(OWNER, BOARD, STATION_FIELD))])


OWNER_B = "other-org"
BOARD_B = 7
STATION_FIELD_B = "Stage"
REPO_B = "acme/other"


def two_repo_fleet_dict(workspace_root):
    """Two repos entries on two different board numbers, no fleet-level board — REPO on
    BOARD/OWNER/STATION_FIELD (matching good_fleet_dict's numbers/options so most existing
    assertions keep working when REPO is what a test lands against); REPO_B on a distinct
    board with distinct owner, station_field and option names, so a test can prove a call
    landed on A's board and never B's by inspecting the recorded gh call arguments alone."""
    return fleet(workspace_root, [
        repo(REPO, DEFAULT_BRANCH, board(OWNER, BOARD, STATION_FIELD)),
        repo(REPO_B, DEFAULT_BRANCH, board(OWNER_B, BOARD_B, STATION_FIELD_B)),
    ])


def calls(rec, kind):
    """The recorded gh calls of one kind, in order."""
    return [c for c in rec.gh_calls if c[0] == kind]


def pr_creates(rec):
    return [c for c in rec.gh_calls if c[0] == "run_gh" and c[1][0][:2] == ("pr", "create")]


def pushes(rec):
    return [c for c in rec.git_calls if c[0][0] == "push"]


# --------------------------------------------------------------------------
# Recorder — a single ordered call log over run_git and the github package's public surface.
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
        self.pr_create_raises = None

    # --- run_git stand-in ---
    def run_git(self, args, cwd):
        self.git_calls.append((tuple(args), cwd))
        return ""

    # --- the github package's public surface used by factory_land ---
    def preflight(self):
        self.gh_calls.append(("preflight", ()))
    def issue_view(self, repo, number, fields):
        self.gh_calls.append(("issue_view", (repo, number, tuple(fields))))
        # Honours the requested `fields` (FEAT-13 fix01) — the fixture is not the full record
        # regardless of what was asked for; dropping "state" from the caller's request drops it
        # from the returned dict too, so `.get("state")` reads None just as it would against a
        # real gh response, and a caller's own state-refusal logic goes behaviourally wrong
        # rather than only failing an argv-shape assertion.
        full = {"title": self.issue_title, "state": self.issue_state}
        return {k: v for k, v in full.items() if k in fields}

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
    (github.transport, "preflight"), (github.issues, "issue_view"), (github.transport, "run_gh"),
    (github.projects, "project_items"), (github.projects, "issue_board_item_id"),
    (github.projects, "project_field_set"),
)


# --------------------------------------------------------------------------
# Driver.
# --------------------------------------------------------------------------

def run_main(rec, extra_args=LAND_ARGS, fleet_dict=None):
    workspace_root = tempfile.mkdtemp(prefix="land-ws-", dir=TMP.name)
    raw_fleet = fleet_dict if fleet_dict is not None else good_fleet_dict(workspace_root)
    clean_fleet, boards_by_repo = split_boards(raw_fleet)
    fleet_path = write_fleet(tempfile.mkdtemp(prefix="land-fleet-", dir=TMP.name), clean_fleet)
    # The board is resolved through factory_config.product_config, never from fleet.yaml
    # (T-02/T-03) — this tool is in-process (no subprocess), so the module-level function itself
    # is monkeypatched rather than faking a `gh` call.
    with contextlib.ExitStack() as stack:
        for module, name in PATCHED_GH:
            stack.enter_context(mock.patch.object(module, name, getattr(rec, name)))
        stack.enter_context(mock.patch.object(fw, "run_git", rec.run_git))
        stack.enter_context(mock.patch.object(fc, "product_config", board_stub(boards_by_repo)))
        result = invoke(
            lambda: factory_cli.run(
                "land", land._main,
                expected=(artifact_accessors.FleetError, github.transport.GhError),
            ),
            argv=["factory_land.py", "--fleet", fleet_path] + list(extra_args),
        )
    return result.code or 0, result.out, result.err, workspace_root


# ==========================================================================
# M — the "at minimum" list.
# ==========================================================================

# (M1) happy path.
rec = Recorder()
code, out, err, ws = run_main(rec)
check("(M1) exits 0", code == 0, code)
push_calls = pushes(rec)
check("(M1) pushes exactly one branch", len(push_calls) == 1, rec.git_calls)
check("(M1) push args are --set-upstream origin <branch>",
      push_calls and push_calls[0][0] == ("push", "--set-upstream", "origin", BRANCH),
      push_calls)
expected_ws_path = fc.workspace_path(good_fleet_dict(ws), REPO)
check("(M1) push runs against workspace_path's cwd",
      push_calls and push_calls[0][1] == expected_ws_path, (push_calls, expected_ws_path))
pr_create_calls = pr_creates(rec)
check("(M1) creates exactly one pull request", len(pr_create_calls) == 1, rec.gh_calls)
pr_argv = pr_create_calls[0][1][0]
check("(M1) pr create base is the fleet's default_branch",
      "--base" in pr_argv and pr_argv[pr_argv.index("--base") + 1] == DEFAULT_BRANCH, pr_argv)
check("(M1) pr create head is the branch",
      "--head" in pr_argv and pr_argv[pr_argv.index("--head") + 1] == BRANCH, pr_argv)
check("(M1) pr create body contains closes #<n>",
      "--body" in pr_argv and f"closes #{ISSUE}" in pr_argv[pr_argv.index("--body") + 1], pr_argv)
lookup_calls = calls(rec, "issue_board_item_id")
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
field_set_calls = calls(rec, "project_field_set")
check("(M1) sets the station to Review", len(field_set_calls) == 1
      and field_set_calls[0][1][4] == "Review", field_set_calls)
# FIX 2 (FEAT-13 fix01): issue_view is invoked with "state" among the requested fields — without
# it the closed-issue refusal (M7 below) always reads None and NEVER refuses (total outage).
issue_view_calls = calls(rec, "issue_view")
check("(M1) issue_view's requested fields include \"state\"",
      issue_view_calls and "state" in issue_view_calls[0][1][2], issue_view_calls)
payload = json.loads(out)
check("(M1) payload url is the created pull request url", payload.get("url") == PR_URL.strip(),
      payload)
check("(M1) payload carries repo, issue, branch", payload.get("repo") == REPO
      and payload.get("issue") == ISSUE and payload.get("branch") == BRANCH, payload)

# The M1 run is the happy path; M1-json, M5, M6 and C1 read their evidence from it too.
happy_rec, happy_code, happy_out = rec, code, out

# (M1-json) the happy path's whole stdout stream is exactly one JSON object.
try:
    json.loads(out)
    parsed_ok = True
except Exception:
    parsed_ok = False
check("(M1-json) stdout is a single json.loads-able stream", parsed_ok, out)

# (M2) a pull request already open for the head is NOT a failure.
rec = Recorder()
rec.pr_create_raises = github.transport.GhError(
    ["pr", "create"], 1, "",
    f'a pull request for branch "{BRANCH}" into branch "{DEFAULT_BRANCH}" already exists:\n'
    f"{PR_URL}",
    "gh pr create failed", REPO, "n/a",
)
code, out, err, ws = run_main(rec)
check("(M2) still exits 0", code == 0, code)
field_set_calls = calls(rec, "project_field_set")
check("(M2) still sets the station", len(field_set_calls) == 1, rec.gh_calls)
payload = json.loads(out)
check("(M2) payload carries the existing pr's url", payload.get("url") == PR_URL, payload)
check("(M2) stderr mentions the url", PR_URL in err, err)

# (M2b) a GhError from pr create that is NOT the already-open shape stays fatal (test-factory-
# decompose.py's case (21) precedent: an unrelated GhError must not be swallowed as "already
# open", and the station must not advance on a pull request that was never created).
rec = Recorder()
rec.pr_create_raises = github.transport.GhError(
    ["pr", "create"], 1, "", "authentication failed, run gh auth login",
    "gh pr create failed", REPO, "run gh auth login",
)
code, out, err, ws = run_main(rec)
check("(M2b) a non-already-open GhError stays fatal: exits 2", code == 2, code)
field_set_calls = calls(rec, "project_field_set")
check("(M2b) the station is never set on an unopened pull request", field_set_calls == [],
      rec.gh_calls)
check("(M2b) stdout empty", out == "", out)

# (M2c) the board carries no item for the issue: the miss BLOCKS rather than sailing through.
# The push has already happened by this point (point of no return), matching the intent's
# recovery note that every step from the push onward is safe to re-run.
rec = Recorder()
rec.items = []
code, out, err, ws = run_main(rec)
check("(M2c) a missing board item exits 2, not 0 or 1 (fail-closed on the miss)", code == 2, code)
field_set_calls = calls(rec, "project_field_set")
check("(M2c) the station is never set when no item was found", field_set_calls == [],
      rec.gh_calls)
check("(M2c) stdout empty", out == "", out)
check("(M2c) the pull request WAS already created before the miss was discovered",
      any(c[0] == "run_gh" and c[1][0][:2] == ("pr", "create") for c in rec.gh_calls),
      rec.gh_calls)

# (M3) an issue number whose branch would equal the default branch exits 2, zero calls.
rec = Recorder()
weird_default = f"factory/issue-{ISSUE}"
fleet_dict = good_fleet_dict(tempfile.mkdtemp(prefix="land-ws-", dir=TMP.name),
                            default_branch=weird_default)
code, out, err, ws = run_main(rec, fleet_dict=fleet_dict)
check("(M3) exits 2", code == 2, code)
check("(M3) zero git calls", rec.git_calls == [], rec.git_calls)
check("(M3) zero gh calls", rec.gh_calls == [], rec.gh_calls)
check("(M3) stdout empty", out == "", out)
check("(M3) stderr names the branch", weird_default in err, err)
guard_code, guard_out, guard_err = code, out, err

# (M4) a repository absent from the fleet exits 2, zero calls.
rec = Recorder()
code, out, err, ws = run_main(rec, ["--repo", "acme/other", "--issue", str(ISSUE)])
check("(M4) exits 2", code == 2, code)
check("(M4) zero git calls", rec.git_calls == [], rec.git_calls)
check("(M4) zero gh calls", rec.gh_calls == [], rec.gh_calls)
check("(M4) stdout empty", out == "", out)
check("(M4) stderr names the repository", "acme/other" in err, err)

# (M5) the recorded git argument lists contain no push of the default branch (anti-vacuum).
rec = happy_rec
check("(M5) at least one git call was recorded (anti-vacuum)", len(rec.git_calls) > 0,
      rec.git_calls)
default_branch_pushes = [
    c for c in rec.git_calls
    if c[0][0] == "push" and DEFAULT_BRANCH in c[0]
]
check("(M5) no recorded git call pushes the default branch", default_branch_pushes == [],
      rec.git_calls)

# (M6) the recorded gh argument lists contain no merge subcommand (anti-vacuum).
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
code, out, err, ws = run_main(rec)
check("(M7) a closed issue exits 2 (refused), not 0", code == 2, code)
check("(M7) stdout empty", out == "", out)
check("(M7) stderr names the issue", str(ISSUE) in err, err)
push_calls = pushes(rec)
check("(M7) the push already happened before the closed-issue refusal", len(push_calls) == 1,
      rec.git_calls)
pr_create_calls = pr_creates(rec)
check("(M7) the pull request WAS already created before the closed-issue refusal",
      len(pr_create_calls) == 1, rec.gh_calls)
field_set_calls = calls(rec, "project_field_set")
check("(M7) the station is never set on a closed issue (field_set_calls == [])",
      field_set_calls == [], rec.gh_calls)

# ==========================================================================
# C-3 contract — three cases, captured with redirect_stdout/redirect_stderr.
# ==========================================================================

# (C1) happy path's stdout parses as JSON in a single json.loads of the whole stream.
check("(C1) code is 0", happy_code == 0, happy_code)
try:
    obj = json.loads(happy_out)
    ok = isinstance(obj, dict)
except Exception:
    ok = False
check("(C1) whole stdout stream is one JSON object", ok, happy_out)

# (C2) the default-branch guard writes nothing to stdout and one stderr line naming the branch.
# Same scenario as M3, so it reads M3's run.
check("(C2) exit 2", guard_code == 2, guard_code)
check("(C2) stdout empty", guard_out == "", guard_out)
err_lines = [line for line in guard_err.splitlines() if line.strip()]
check("(C2) exactly one stderr line", len(err_lines) == 1, guard_err)
check("(C2) that line names the branch", err_lines and weird_default in err_lines[0], guard_err)

# (C3) a monkeypatched pr-create raising a plain ValueError makes the entry point exit 2, not 1.
rec = Recorder()
rec.pr_create_raises = ValueError("boom")
code, out, err, ws = run_main(rec)
check("(C3) exits 2, not 1", code == 2, code)
check("(C3) stdout empty", out == "", out)

# ==========================================================================
# T-04 — per-repository board (FEAT-16). Two repos entries on two different board numbers;
# landing --repo A must read and write only A's board, never B's.
# ==========================================================================

# (T04-1) landing repo_a sets the station on A's board with A's review option name, and issues
# no call against B's board.
rec = Recorder()
fleet_dict = two_repo_fleet_dict(tempfile.mkdtemp(prefix="land-ws-", dir=TMP.name))
code, out, err, ws = run_main(rec, fleet_dict=fleet_dict)
check("(T04-1) exits 0", code == 0, code)
lookup_calls = calls(rec, "issue_board_item_id")
check("(T04-1) issue_board_item_id called with A's (repo, issue, board_number)",
      lookup_calls and lookup_calls[0][1] == (REPO, ISSUE, BOARD), lookup_calls)
field_set_calls = calls(rec, "project_field_set")
check("(T04-1) project_field_set called exactly once", len(field_set_calls) == 1,
      rec.gh_calls)
check("(T04-1) project_field_set carries A's owner, board number, station_field and "
      "Review option name",
      field_set_calls
      and field_set_calls[0][1] == (OWNER, BOARD, ITEM_ID, STATION_FIELD, "Review"),
      field_set_calls)
# "Other-Review" IS GONE from the markers: FEAT-41 T-01 removed per-repo column names, so
# both boards now declare the same six stations and a column name can no longer distinguish
# them. The three that remain — board number, owner, station_field — still differ per repo,
# which is what keeps this pair of checks discriminating.
b_markers = (BOARD_B, OWNER_B, STATION_FIELD_B)
check("(T04-1) issue_board_item_id's call carries none of B's board markers",
      lookup_calls and not any(m in lookup_calls[0][1] for m in b_markers), lookup_calls)
check("(T04-1) project_field_set's call carries none of B's board markers",
      field_set_calls and not any(m in field_set_calls[0][1] for m in b_markers),
      field_set_calls)
check("(T04-1) no gh call of any kind was recorded against B's board number",
      not any(c[0] in ("issue_board_item_id", "project_field_set", "project_items")
              and BOARD_B in c[1] for c in rec.gh_calls),
      rec.gh_calls)

sys.exit(C.report())
