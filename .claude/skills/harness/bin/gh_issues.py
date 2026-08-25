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


def sub_issues_args(repo, num):
    """GET one issue's children. Read-only, and bounded to `gh-sync.py ship`'s open-child
    check (DEC-203 item 5, the sixth read-back purpose). Unlike `attach_sub_issue_args` this
    takes the issue's NUMBER, because it is the REST path segment, not a payload id."""
    return ["api", f"repos/{repo}/issues/{num}/sub_issues"]


def detach_sub_issue_args(repo, parent, child_id):
    """DETACH one child from its parent. Takes the child's internal `id`, like the attach --
    the SAME trap, and the path segment is singular `sub_issue` where the attach and the list
    are plural `sub_issues`.

    Measured live 2026-08-25 on #860/#861: after this call the parent's `sub_issues` list
    reads `[]`. `abandon` uses it so a dropped ticket stops holding its parent open."""
    return ["api", "-X", "DELETE", f"repos/{repo}/issues/{parent}/sub_issue",
            "-F", f"sub_issue_id={child_id}"]


def parent_args(repo, num):
    return ["api", f"repos/{repo}/issues/{num}/parent"]


def blocked_by_args(repo, num, blocker_id):
    return ["api", f"repos/{repo}/issues/{num}/dependencies/blocked_by",
            "-F", f"issue_id={blocker_id}"]
