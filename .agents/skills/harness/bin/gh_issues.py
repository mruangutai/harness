"""Shared GitHub Issues primitives — argv builders only (D-03, REQ-06).

THE TRAP: the sub-issue and dependency endpoints take an issue's internal `id`,
never its `number`. Passing the number silently attaches the wrong issue or 422s.
This module documents the trap once and builds the argv for it; it executes
nothing. `wayfind.py` dies exit 1 and is dry-run by default, `gh-sync.py` skips
and exits 0 on an environmental failure — two different failure semantics a
shared executor would have to pick one of, so each caller keeps its own runner.
"""
import os


def gh_bin():
    return os.environ.get("GH_SYNC_GH", "gh")


def internal_id_args(repo, num):
    return ["api", f"repos/{repo}/issues/{num}", "--jq", ".id"]


def attach_sub_issue_args(repo, parent, child_id):
    return ["api", f"repos/{repo}/issues/{parent}/sub_issues", "-F", f"sub_issue_id={child_id}"]


def parent_args(repo, num):
    return ["api", f"repos/{repo}/issues/{num}/parent"]


def blocked_by_args(repo, num, blocker_id):
    return ["api", f"repos/{repo}/issues/{num}/dependencies/blocked_by",
            "-F", f"issue_id={blocker_id}"]
