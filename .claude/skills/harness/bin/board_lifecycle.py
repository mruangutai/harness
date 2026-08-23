#!/usr/bin/env python3
"""board_lifecycle.py — creates and maintains a GitHub Projects v2 board (FEAT-33 T-04).

Usage: board_lifecycle.py <provision|audit|reconcile> [--repo <owner/name>]

`provision` (T-04) and `audit` (T-05) are wired up here. `reconcile` (T-06) grows this same file
later — one bin, three subcommands over one board-resolution path (D-08) — so the usage line
above already names all three even though the argument parser below does not yet register
`reconcile`; registering a subcommand with nothing behind it would be exactly the placeholder
this task's zero-placeholder gate refuses.

AUDIT (T-05) — read-only, exits 0/1/4, never 2 or 3 (those are provision's own codes for a
caller/declaration error and the new-project race). It performs EXACTLY FOUR network calls, one
answering each bullet below, and this count is the one a later reader is told to trust — if a
future change adds a fifth call, name it here rather than silently letting this figure go stale:
  1. `factory_gh.project_field_options` — the board's Status field option names (DECLARATION).
  2. `gh issue list --repo <repo> --state closed --json number,stateReason,labels --limit 1000`
     — every closed issue's number, close reason and labels (REASON, LABEL, and feeds STATION).
  3. `gh_board.board_stations` — the targeted, cost-1 station read (STATION).
  4. `factory_gh.project_workflows` — the three named automation workflows (WORKFLOW).

The five finding classes are closed (T-05 intent): DECLARATION (a declared station value the
board's Status field does not carry — via `_missing_options`, the SAME helper `provision` calls,
never re-authored), STATION (a closed board issue not at the declared done station), REASON (a
closed issue with a null close reason), LABEL (a `not_planned` issue with no `abandoned` label),
WORKFLOW (one of "Item closed", "Auto-close issue", "Pull request merged" absent or disabled).
Workflow detection is by NAME only — `ProjectV2Workflow` exposes neither `trigger` nor `action`
(D-09) — so a workflow the operator renamed is reported MISSING rather than assumed present; the
report says this once, in its own header line (SC-09), and every WORKFLOW finding line also says
no API can enable it and only a click in the project's web UI can.

Failure posture is the INVERSE of gh-sync.py's mirror posture (DEC-186): this is a control-plane
tool, so a `GhError` propagates as one line on stderr and exit 4 — never exit 1, which means
"findings were found", and never a silent zero-finding report. An audit that could not run must
never be mistaken for an audit that found nothing.

BOARD RESOLUTION, one code path for both repositories (T-04 intent):
  - no --repo, or --repo naming THIS checkout's own harness.json `github.repo`: the board comes
    from `gh_board.load_board(factory_config.harness_root())`. `factory_config.harness_root()`
    is the established root helper (factory_config.py:44, already reused by factory_claim.py,
    feature-worktree.py and gh_cost_log.py) — never a hand-rolled walk-up. board-station.py made
    a THIRD walk-up for a different purpose already; this is not a fourth.
  - --repo naming a fleet member: `factory_config.board_for(fleet, repo)`, which reads that
    repository's own `.harness/harness.json` REMOTELY at its default_branch — this tool never
    checks out a served repository to provision its board.
  - --repo naming neither: exit 2, naming the repo and both sources tried.

provision is idempotent, and NEVER infers "there is no project" from a field-resolution failure
(see `factory_gh.project_resolve`'s own docstring for the disaster that produces — a duplicate
Projects v2 board on the operator's account). `factory_gh.project_resolve` is the ONLY signal
this module trusts to decide "call project_create"; every other GhError from that first read
propagates unhandled and mutates nothing.

THE FIELD-ID GAP — read this before changing step 3's dispatch. factory_gh.py exposes six
primitives for board provisioning (T-03) plus the pre-existing `project_field_options`, and NONE
of the seven returns an EXISTING field's node id or its actual GraphQL type name:
`project_field_options` (factory_gh.py:465-467) discards both, returning option NAMES only, and
`_project_field_resolve` — the one function that has them — is private, and deliberately
collapses "field absent" with "field exists but is not single-select" into one GhError
(factory_gh.py:451-457, a documented prior decision, D-04). Both `project_single_select_extend`
(needs the EXISTING field's id) and this module's own disaster guard (must tell "absent" from
"wrong type" apart so it never calls `createProjectV2Field` for a name already taken — the plan
forbids that outright) are unreachable through the seven given primitives alone. `_field_probe`
below is the minimal fix: ONE read-only GraphQL query, sent through `factory_gh.run_gh` — the
same FACTORY_GH-indirected, cost-logged, rate-limit-aware seam every primitive in factory_gh.py
itself goes through, so it is exactly as fake-testable as the rest of this module — asking only
for the field's `__typename` and node id. It mutates nothing. It is reported here, and in this
task's receipt, as a plan gap rather than folded in silently: T-04's dispatch named exactly seven
primitives as what this task calls, and none of them answers "does this field exist, and if so,
as what" — a question with no destructive answer, and one this module cannot avoid asking.
"""
import argparse
import json
import os
import sys

import factory_cli
import factory_config
import factory_gh
import gh_board

_TOOL = "board_lifecycle"
_SINGLE_SELECT = "ProjectV2SingleSelectField"


def _out(line):
    print(f"{_TOOL}: {line}")


def _own_repo(root):
    """`harness.json`'s `github.repo`, or None on any unreadable/malformed shape — mirrors
    board-station.py:134's own `github.get("repo")` read of the same key, kept as a second,
    independent read here because `gh_board.load_board` returns only the board, never the repo
    name, and this module needs both."""
    path = os.path.join(root, ".harness", "harness.json")
    try:
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(cfg, dict):
        return None
    github = cfg.get("github")
    if not isinstance(github, dict):
        return None
    repo = github.get("repo")
    return repo if isinstance(repo, str) and repo else None


def _resolve_board(root, repo_arg):
    """Return (repo_name, board_or_None) per the module docstring's BOARD RESOLUTION rule.
    board is None ONLY for an explicit `github.board: null` (D-07's declared no-board path) —
    never for an unresolved repository, which refuses instead (factory_cli.refuse, exit 2)."""
    own_repo = _own_repo(root)
    if repo_arg is None or repo_arg == own_repo:
        return (own_repo or repo_arg), gh_board.load_board(root)
    fleet = factory_config.load_fleet()
    names = [e.get("name") for e in fleet.get("repos", []) if isinstance(e, dict)]
    if repo_arg not in names:
        factory_cli.refuse(
            _TOOL, "repository not recognised", repo_arg,
            f"tried this checkout's own repo ({own_repo!r}) and the fleet at "
            f"{factory_config.FLEET_PATH} (known: {', '.join(n for n in names if n) or 'none'})",
        )
    return repo_arg, factory_config.board_for(fleet, repo_arg)


# See the module docstring's FIELD-ID GAP section. `... on ProjectV2Field`/`ProjectV2Iteration
# Field`/`ProjectV2SingleSelectField` are the three concrete members of the ProjectV2Field
# Configuration union (a union, so `id` cannot be selected on `field(name:)` directly — the same
# constraint that makes `_project_field_resolve` above use an inline fragment); `__typename` is a
# meta-field and needs no fragment, so it alone already tells "absent" (field is JSON null) from
# "exists" (field is a non-null object, always carrying __typename) apart, with no ambiguity.
_FIELD_PROBE_QUERY = """query($owner: String!, $number: Int!, $field: String!) {
  repositoryOwner(login: $owner) {
    __typename
    ... on ProjectV2Owner {
      projectV2(number: $number) {
        field(name: $field) {
          __typename
          ... on ProjectV2Field { id }
          ... on ProjectV2SingleSelectField { id }
          ... on ProjectV2IterationField { id }
        }
      }
    }
  }
}
"""


def _field_probe(owner, number, field):
    """Read-only. Returns (field_id_or_None, typename_or_None) — field_id is None only when
    `field` does not exist on the project at all; typename is None only alongside it. Raises
    GhError on anything the caller has not already ruled out via `project_resolve` — an
    unresolvable owner, an org-owned board, a project that does not exist — with the identical
    discrimination `_project_field_resolve` makes (__typename read before projectV2, D-03/D-04
    there)."""
    argv = ["api", "graphql", "-f", "query=" + _FIELD_PROBE_QUERY,
            "-f", "owner=" + owner, "-F", "number=" + str(number), "-f", "field=" + field]
    env = factory_gh.run_gh(argv, json_out=True)
    data = env.get("data") or {}
    repo_owner = data.get("repositoryOwner")
    if repo_owner is None:
        raise factory_gh.GhError(argv, None, "", "",
                                  "project owner not found", owner, "check the owner login")
    if repo_owner.get("__typename") != "User":
        raise factory_gh.GhError(argv, None, "", "",
                                  "organization-owned board not supported", owner,
                                  "run against a user-owned board")
    project = repo_owner.get("projectV2")
    if project is None:
        raise factory_gh.GhError(argv, None, "", "",
                                  "project not found", f"{owner} project {number}",
                                  "check the board number")
    field_obj = project.get("field")
    if not field_obj:
        return None, None
    return field_obj.get("id"), field_obj.get("__typename")


def _missing_options(declared_stations, board_option_names):
    """The declared values absent from the board, byte-for-byte and case-sensitive (DEC-192),
    preserving declared key order. T-05's DECLARATION finding class calls this SAME helper —
    do not re-author the comparison there; D-05 makes the exactness load-bearing and two
    implementations means a later loosening has two sites and no invariant tying them together."""
    return [v for v in declared_stations if v not in board_option_names]


def _declared_stations(board):
    return [board["stations"][k] for k in
            ("backlog", "plan", "ready", "building", "review", "done")]


def cmd_provision(repo_arg):
    root = factory_config.harness_root()
    repo_name, board = _resolve_board(root, repo_arg)
    if board is None:
        # D-07: an explicit `github.board: null` is a declaration, not a misconfiguration.
        _out("no board declared -- nothing to do")
        return

    owner, number, field = board["owner"], board["number"], board["station_field"]
    declared = _declared_stations(board)

    # Step 2: the ONLY signal this module trusts to decide "create a project". Any other
    # GhError from this call (owner unresolvable, org-owned board) propagates unhandled and
    # mutates nothing.
    resolved = factory_gh.project_resolve(owner, number)
    if resolved is None:
        if not repo_name:
            factory_cli.refuse(
                _TOOL, "cannot link the new project", "github.repo is not declared",
                "pin github.repo in harness.json before provisioning",
            )
        created = factory_gh.project_create(owner, f"{repo_name} board")
        factory_gh.project_link_repository(created["id"], repo_name)
        _out(f"no project {number} on {owner} -- created project {created['number']} and "
             f"linked {repo_name}; record number {created['number']} in {repo_name}'s "
             f"harness.json")
        sys.exit(3)

    project_id = resolved["id"]

    # Step 3: discriminate "field absent" from "field exists but is not single-select" via
    # _field_probe, never via a message substring on factory_gh's collapsed GhError (see the
    # module docstring's FIELD-ID GAP section for why the given primitives alone cannot do this).
    field_id, typename = _field_probe(owner, number, field)

    if field_id is None:
        factory_gh.project_single_select_create(project_id, field, declared)
        _out(f"created field {field!r} with {len(declared)} option(s): {', '.join(declared)}")
        return

    if typename != _SINGLE_SELECT:
        factory_cli.refuse(
            _TOOL, "field is not single-select", f"{field} ({typename})",
            "convert it manually -- board_lifecycle never converts an existing field's type",
        )

    # Step 4: compute the union via the ONE shared helper, then send existing options first
    # (preserved) followed only by the additions -- project_single_select_extend's mutation
    # REPLACES the option set, so sending anything less deletes a column (D-plan T-03).
    existing = factory_gh.project_field_options(owner, number, field)
    missing = _missing_options(declared, existing)
    if not missing:
        _out("nothing to do")
        return
    factory_gh.project_single_select_extend(project_id, field_id, existing + missing)
    _out(f"added {len(missing)} option(s) to {field!r}: {', '.join(missing)}")


# The three workflows every board needs (T-05 intent, finding class 5). Matched by NAME only —
# ProjectV2Workflow exposes neither trigger nor action (D-09) — so a renamed workflow is reported
# MISSING rather than assumed present.
_REQUIRED_WORKFLOWS = ("Item closed", "Auto-close issue", "Pull request merged")

_WORKFLOW_HEADER = (
    "workflow detection matches by NAME only -- ProjectV2Workflow exposes neither trigger nor "
    "action, so a workflow the operator renamed is reported MISSING rather than assumed present"
)
_WORKFLOW_SUFFIX = "no API can enable it -- only a click in the project's web UI can"


def _audit_findings(board, repo_name):
    """The closed, finite finding list (T-05 intent). Read-only: no mutation, anywhere.

    Performs exactly the four network calls the module docstring's AUDIT section names, in the
    order: field options (class 1), the closed-issue list (feeds classes 2, 3 and 4), the board
    station read (class 2), the project workflows read (class 5).
    """
    owner, number, field = board["owner"], board["number"], board["station_field"]
    done_station = board["stations"]["done"]
    findings = []

    # Class 1 -- DECLARATION. Call 1/4.
    declared = _declared_stations(board)
    options = factory_gh.project_field_options(owner, number, field)
    value_to_key = {v: k for k, v in board["stations"].items()}
    for value in _missing_options(declared, options):
        key = value_to_key.get(value, "?")
        findings.append(
            f"DECLARATION: station {key!r} (declared value {value!r}) is not among project "
            f"{number}'s Status options"
        )

    # The closed-issue read feeding classes 2, 3 and 4. Call 2/4.
    issues = factory_gh.run_gh(
        ["issue", "list", "--repo", repo_name, "--state", "closed",
         "--json", "number,stateReason,labels", "--limit", "1000"],
        json_out=True,
    )

    # Class 2 -- STATION. Call 3/4.
    stations = gh_board.board_stations(board, repo_name)
    for issue in issues:
        num = issue.get("number")
        if num in stations and stations[num] != done_station:
            findings.append(
                f"STATION: issue #{num} reads {stations[num]!r}, expected {done_station!r}"
            )

    # Class 3 -- REASON.
    for issue in issues:
        if issue.get("stateReason") is None:
            findings.append(f"REASON: issue #{issue.get('number')} is closed with no state_reason")

    # Class 4 -- LABEL.
    for issue in issues:
        reason = (issue.get("stateReason") or "").upper()
        if reason == "NOT_PLANNED":
            names = {l.get("name") for l in issue.get("labels", []) if isinstance(l, dict)}
            if "abandoned" not in names:
                findings.append(
                    f"LABEL: issue #{issue.get('number')} is not_planned and carries no "
                    f"'abandoned' label"
                )

    # Class 5 -- WORKFLOW. Call 4/4.
    _out(_WORKFLOW_HEADER)
    workflows = factory_gh.project_workflows(owner, number)
    by_name = {w["name"]: w for w in workflows}
    for name in _REQUIRED_WORKFLOWS:
        w = by_name.get(name)
        if w is None:
            findings.append(f"WORKFLOW: {name!r} is MISSING -- {_WORKFLOW_SUFFIX}")
        elif not w.get("enabled"):
            findings.append(f"WORKFLOW: {name!r} is disabled -- {_WORKFLOW_SUFFIX}")

    return findings


def cmd_audit(repo_arg):
    root = factory_config.harness_root()
    repo_name, board = _resolve_board(root, repo_arg)
    if board is None:
        # D-07: an explicit `github.board: null` is a declaration, not a misconfiguration.
        _out("no board declared -- nothing to audit")
        return
    if not repo_name:
        factory_cli.refuse(
            _TOOL, "cannot audit", "github.repo is not declared",
            "pin github.repo in harness.json before auditing",
        )

    # DEC-186's inverse-of-the-mirror posture: a GhError here means the audit COULD NOT RUN, and
    # must never read like "ran and found nothing" (exit 0) or "ran and found something" (exit
    # 1) -- it gets its own exit code, 4, caught here rather than left to factory_cli.run's
    # generic expected-exception trap (which would exit 2, provision's own caller-error code).
    try:
        findings = _audit_findings(board, repo_name)
    except factory_gh.GhError as exc:
        print(f"factory: {_TOOL}: {exc}", file=sys.stderr)
        sys.exit(4)

    for f in findings:
        _out(f)
    _out(f"{len(findings)} finding(s)")
    if findings:
        sys.exit(1)


def _main():
    parser = argparse.ArgumentParser(
        prog="board_lifecycle.py",
        description="board_lifecycle.py <provision|audit|reconcile> [--repo <owner/name>]",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_provision = sub.add_parser("provision")
    p_provision.add_argument("--repo", default=None)
    p_audit = sub.add_parser("audit")
    p_audit.add_argument("--repo", default=None)
    args = parser.parse_args()
    if args.cmd == "provision":
        cmd_provision(args.repo)
    elif args.cmd == "audit":
        cmd_audit(args.repo)


if __name__ == "__main__":
    factory_cli.run(_TOOL, _main, expected=(factory_gh.GhError, factory_config.FleetError))
