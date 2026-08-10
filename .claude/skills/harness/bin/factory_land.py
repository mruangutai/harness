"""factory_land.py — the last step of the journey, opening a pull request (T-07, REQ-05).

It opens a pull request and stops. The operator merges; the factory never does, in this
increment. The module contains no call to `gh pr merge`, no call to `gh api` against a merge
endpoint, and no `git push` whose refspec is the default branch.

POINT OF NO RETURN: the fleet load and the default-branch guard exit 2 with zero calls of any
kind. The point of no return is the successful push — everything from there on is idempotent on
a re-run (the push is a no-op, `gh pr create` adopts an existing pull request, and the field set
is a write of the same value), so the recovery from any later failure is to re-run the same
command.

Every git operation runs through factory_workspace.run_git(args, cwd) — never a second git-binary
resolution — and every GitHub operation runs through factory_gh's public surface, including the
generic factory_gh.run_gh for `gh pr create`, which factory_gh does not wrap with a dedicated
helper. Neither module's own resolution is re-derived here.
"""
import argparse
import re
import sys

import factory_cli
import factory_config
import factory_gh
import factory_workspace

TOOL = "land"


def _find_item_id(owner, board_number, number):
    """The board item id for `number`, or None when the board carries no such item."""
    items = factory_gh.project_items(owner, board_number, query="is:open")
    for it in items:
        if (it.get("content") or {}).get("number") == number:
            return it.get("id")
    return None


def _main():
    parser = argparse.ArgumentParser(prog="factory_land")
    parser.add_argument("--repo", required=True, help="owner/name")
    parser.add_argument("--issue", required=True, type=int)
    parser.add_argument("--fleet", default=None, help="path to fleet.yaml (default: FLEET_PATH)")
    args = parser.parse_args()

    fleet = factory_config.load_fleet(args.fleet) if args.fleet else factory_config.load_fleet()
    entry = factory_config.repo_entry(fleet, args.repo)
    default_branch = entry["default_branch"]

    # 2. THE DEFAULT-BRANCH GUARD — first thing checked after the fleet loads, before any call.
    branch = f"factory/issue-{args.issue}"
    if branch == default_branch:
        factory_cli.refuse(
            TOOL, "branch equals the default branch", branch,
            "the factory never pushes the default branch",
        )

    # 3. THE POINT OF NO RETURN — push the branch from the same checkout T-06 uses.
    path = factory_config.workspace_path(fleet, args.repo)
    factory_workspace.run_git(["push", "--set-upstream", "origin", branch], path)

    # 4. preflight, then create the pull request. A pull request already open for this head is
    # NOT a failure — it is adopted so the retry path stays usable.
    factory_gh.preflight()

    title = factory_gh.issue_view(args.repo, args.issue, ["title"]).get("title")
    body = f"closes #{args.issue}"
    pr_args = [
        "pr", "create", "--repo", args.repo, "--base", default_branch,
        "--head", branch, "--title", title, "--body", body,
    ]
    try:
        out = factory_gh.run_gh(pr_args)
        url = out.strip()
    except factory_gh.GhError as e:
        combined = f"{e.stdout or ''}\n{e.stderr or ''}"
        m = re.search(r"https?://\S+", combined) if "already exists" in combined.lower() else None
        if m is None:
            raise
        url = m.group(0)
        print(
            f"factory: {TOOL}: pull request for {branch} already open — {url}",
            file=sys.stderr,
        )

    # 5. move the issue's board item to the review station.
    owner = fleet["board"]["owner"]
    board_number = fleet["board"]["number"]
    station_field = fleet["board"]["station_field"]
    review_option = fleet["board"]["stations"]["review"]

    item_id = _find_item_id(owner, board_number, args.issue)
    if item_id is None:
        raise factory_gh.GhError(
            [], None, "", "",
            "issue not found on the board", args.issue,
            f"board {owner}/{board_number}",
        )
    factory_gh.project_field_set(owner, board_number, item_id, station_field, review_option)

    # 6. the single stdout payload.
    factory_cli.payload({"repo": args.repo, "issue": args.issue, "branch": branch, "url": url})


if __name__ == "__main__":
    factory_cli.run(TOOL, _main, expected=(factory_config.FleetError, factory_gh.GhError))
