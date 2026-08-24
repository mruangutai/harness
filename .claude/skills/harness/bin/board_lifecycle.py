#!/usr/bin/env python3
"""board_lifecycle.py — creates and maintains a GitHub Projects v2 board (FEAT-33 T-04).

Usage: board_lifecycle.py <provision|audit|reconcile|retitle> [--repo <owner/name>] [--apply]

`provision` (T-04), `audit` (T-05), `reconcile` (T-06) and `retitle` (T-17) are all wired up
here — one bin, four subcommands (D-08); `retitle` shares only the repo half of the
board-resolution path (below), never the board itself, which it has no use for.

RETITLE (T-17) — the one-time backfill that renames every OLD-format task ticket
(`"T-NN — <title>"`, gh-sync.py's title before T-16) to the NEW format T-16 now writes going
forward (`"<feat> — T-NN — <title>"`, gh-sync.py:764). It touches ISSUE TITLES ONLY — never a
project or a card — so it never resolves a board at all; it resolves only the REPO NAME half of
`_resolve_board`, reusing that function and discarding the board it returns, so an unknown
`--repo` refuses (exit 2) exactly the way every other subcommand's caller error does.

Three network-call shapes, and the cost is retitle's OWN, never covered by audit's four-call
figure (that count is audit's own contract and nothing else's — see below):
  - ONE enumeration: `gh issue list --repo <repo> --state all --limit 1000 --json
    number,title,milestone`. Measured 2026-08-22 at f5f5185: 640 issues, 7 GraphQL points.
  - ONE `gh issue edit <n> --repo <repo> --title <new>` PER RENAME. Measured 2026-08-22 at
    f5f5185: 2 GraphQL points each — 188 renames on the harness board is 383 points including
    the enumeration, 7.7 percent of the 5000/hour budget.
Every cost figure this subcommand prints or writes carries the repo, the item count and the
commit it was measured at, so a stale figure is never mistaken for a live one.

Selection: a title matches `^(T-\\d+) — (.+)$` — the OLD format's own separator, not merely a
bare space, because gh-sync.py wrote the em dash even before T-16 (`f"{task['id']} — {task['title']}"`)
— captures the task id and the task's own title text UNCHANGED, so the new title this backfill
writes is byte-identical to what `cmd_open` would write today for the same task: `f"{feat} —
{tid} — {rest}"`, the SAME f-string gh-sync.py:764 builds, with `rest` the exact substring the
regex captured (never re-derived from plan.yaml or any other source).
Each selected ticket's feature id is derived from THAT TICKET'S OWN milestone title and from
NOTHING ELSE (D-20) — never from plan.yaml, never inferred. No milestone means REFUSED: printed
and counted, never renamed, never guessed. A ticket already starting with its own milestone
title followed by " — " is counted "already correct" and skipped with no write — this is what
makes a re-run idempotent with no state file: the title itself records whether the rename
happened.
`--dry-run` (the default, matching `reconcile`'s shape) previews every pending rename and the
projected point cost and performs ZERO writes; `--apply` is required to write. A truncated
enumeration (the returned count reaches the `--limit`) refuses with exit 2 rather than silently
backfilling a partial list. A `GhError` from the ENUMERATION call propagates as exit 4, caught
explicitly here exactly as `audit` and `reconcile` catch it — never left to `factory_cli.run`'s
generic trap, which would exit 2 and read as a caller/declaration error rather than a network
failure.

A `GhError` from an INDIVIDUAL RENAME call (fix cycle c1, MUST-FIX 3) is caught PER-TICKET,
mirroring `reconcile`'s own apply loop (`_apply_fix`'s caller, above) exactly rather than merely
being described as doing so: printed to stderr and counted as `failed`, and the run continues to
the next ticket rather than stopping — a `GhError` on ticket N of a 218-ticket bulk backfill must
never leave N-1 already-renamed tickets unreported behind a caller/declaration exit code, the
same "a bulk fix that stops at the first failure leaves the board half migrated" principle
`reconcile` states for its own apply loop. `--apply` exits 1 if one or more renames FAILED (a
write was attempted and did not land — a genuine partial-completion signal, distinct from
`factory_cli`'s generic "nothing to do" meaning for exit 1, exactly as `reconcile` already
overrides the generic exit-1 meaning for its own residual-findings count) and exits 0 otherwise
— including when every renamable ticket succeeds, or when the only outcomes were REFUSED-for-
no-milestone tickets, which are decided-not-attempted and never fail the run.

RECONCILE (T-06) — the write side of `audit`. It runs `_audit_findings` (the SAME detection
`audit` runs, never re-derived) and fixes exactly the classes a write CAN fix, per finding:
  - STATION: `gh_board.set_station` moves the card to the declared done station.
  - REASON: PATCHes `repos/<repo>/issues/<n>` to state=closed. An issue carrying the
    `abandoned` label gets state_reason=not_planned; every other REASON finding (by
    definition already null) gets state_reason=completed.
  - LABEL: creates the `abandoned` label directly (never through a helper — see below), then
    `gh issue edit <n> --add-label abandoned`.
  - STATUS, for every recorded status EXCEPT Done: moves the PARENT card (never the other
    way — feature.json is the authority, DEC-138, and this must never rewrite feature.json) to
    the station its status maps to. A Done-status STATUS finding is a genuine finding (D-22,
    no Done exemption in detection) but reconcile does not move a card to the done station on
    its say alone, so it is left for a human exactly like DECLARATION and WORKFLOW — the SAME
    "counts only what it can fix" principle that excludes those two, applied to one status
    value inside a class that is otherwise fixable.
DECLARATION and WORKFLOW are never attempted: the declaration is a file a human signs, and no
API can enable a workflow (D-09).

RECONCILE SHARES STATUS's SCOPING (#783's fix): it runs `_audit_findings`, the SAME detection
function `audit` calls, so a `--repo` naming anything but this checkout's own repo never
produces a STATUS finding for reconcile to attempt either -- before the fix this meant
`reconcile --apply` against a served repo could call `gh_board.set_station` on THAT repo's card
using a station computed from THIS checkout's own, unrelated feature.json. The fix lives once,
in detection, so both callers inherit it without a second check.

THE LABEL CREATE IS A DIRECT SHELL-OUT, never a helper, for two measured reasons: `gh-sync.py`
is HYPHENATED, so its own `ensure_labels` (gh-sync.py:682-696) is not an importable module
function; and the only importable one, `factory_gh.ensure_labels` (factory_gh.py:186-195),
passes `--force` with its own single `_LABEL_COLOR`, which would repaint `abandoned`
harness-purple over gh-sync.py's `b60205` on every run this module makes (D-04's
three-implementations collision, arriving here as a live defect if called). The literal
`b60205` here matches gh-sync.py's own colour for the same label. The create call reads its
binary from `GH_SYNC_GH` (gh-sync.py's own env var, D-11) rather than `FACTORY_GH` — the one
call in this module that is not routed through `factory_gh.run_gh` — and swallows its error
exactly as gh-sync.py's own `ensure_labels` does: "label already exists" is the common case.

RECONCILE'S NETWORK-CALL COST is NOT covered by AUDIT's four-call count above, which is audit's
own contract and nothing else's. `--dry-run` (the default) costs exactly the SAME four calls
audit makes — detection only, nothing more. `--apply` costs those four, PLUS one write per
fixed finding (two for LABEL: the label create and the issue edit), PLUS a second, identical
four-call detection pass afterward to compute the residual truthfully rather than assume the
writes landed.

RECONCILE'S EXIT CODES: 4 on a `GhError` from EITHER detection pass (the run could not
complete — never conflated with 0 or 1, DEC-186's inverse-of-the-mirror posture, same as
audit). Under `--dry-run`, always 0 once detection succeeds — a preview attempts nothing, so
nothing can be reported as "surviving" a fix it never tried. Under `--apply`: 0 when no
STATION, REASON, LABEL or STATUS(non-Done) finding survives the post-fix re-detection; 1 with
the full residual list otherwise. DECLARATION, WORKFLOW and STATUS(Done) residuals are always
printed in full and NEVER counted toward this exit code — counting an unfixable-by-design class
would mean reconcile could never exit 0 on a board carrying one, permanently gating T-11 and
T-12 (which require exit 0) on a finding no write of this tool's can resolve. A bulk fix that
stops at the first failure and reports 0 leaves the board silently half migrated, so a failed
write for one card is caught, printed, and the run continues to the rest; the failed card's
finding survives into the residual list and the exit code reflects that.

IDEMPOTENCE: re-running `reconcile --apply` against an already-correct board performs the
SAME detection-only four calls both passes always cost, finds nothing fixable, attempts zero
writes, and exits 0 — a no-op in effect, not merely in outcome.

AUDIT (T-05) — read-only, exits 0/1/4, never 2 or 3 (those are provision's own codes for a
caller/declaration error and the new-project race). It performs EXACTLY FOUR network calls, one
answering each bullet below, and this count is the one a later reader is told to trust — if a
future change adds a fifth call, name it here rather than silently letting this figure go stale:
  1. `factory_gh.project_field_options` — the board's Status field option names (DECLARATION).
  2. `gh issue list --repo <repo> --state closed --json number,stateReason,labels --limit 1000`
     — every closed issue's number, close reason and labels (REASON, LABEL, and feeds STATION).
  3. `gh_board.board_stations` — the targeted, cost-1 station read (STATION).
  4. `factory_gh.project_workflows` — the three named automation workflows (WORKFLOW).
STATUS (T-15, below) adds a SIXTH finding class but no fifth network call: it reads every
feature's `feature.json` off disk and reuses call 3's already-fetched station map. STATUS runs
ONLY when the audited repo is THIS checkout's own declared repo (#783's fix, below) — it
self-skips, printing one line, for any other `--repo`, since the on-disk features it reads are
never that repo's.

The six finding classes are closed (T-05/T-15 intent): DECLARATION (a declared station value the
board's Status field does not carry — via `_missing_options`, the SAME helper `provision` calls,
never re-authored), STATION (a closed board issue not at the declared done station), REASON (a
closed issue with a null close reason), LABEL (a `not_planned` issue with no `abandoned` label),
WORKFLOW (one of "Item closed", "Auto-close issue", "Pull request merged" absent or disabled),
STATUS (a feature's recorded `feature.json` status, mapped through the board's declared stations
exactly as T-13 maps it, disagreeing with its parent card's actual station — feature.json is the
authority (DEC-138's outbound posture, T-13); the card is what drifted. NO Done exemption, D-22:
a status of Done whose parent card is not at the done station is a finding whether the parent
issue is open or closed. SCOPED TO THIS CHECKOUT'S OWN REPO ONLY, #783's fix — see
`_status_findings`'s own docstring for the ruling and why).
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

PROVISION'S EXIT CODES: 0 the board is correct — either nothing needed doing, or the station
field was created/widened on an EXISTING project. 2 the declaration or the caller is unusable
and NOTHING was written (an unknown --repo, an org-owned board, a `github.repo` that is not
declared, the wrong-field-type disaster guard, the linkage guard). 3 a NEW project was created,
linked, AND its station field made to carry every declared station (fix cycle c2, SC-01 — the
field lands in the SAME run, it never waits for a second one); the operator must record the new
number in that repo's harness.json before anything else runs, and 3 is that signal — its
meaning is unchanged by c2 or c3. 4 a write was attempted and the run did not fully land: the
link failed, or the field work failed after a successful create+link. Every 4 path names the
CREATED project's number on stderr, because a retry that cannot see it re-enters the create
branch and produces a SECOND duplicate board — the exact disaster `project_resolve`'s own
docstring names.

ONCE A PROJECT EXISTS, 2 IS UNREACHABLE FROM ANY FAILURE THIS MODULE CATCHES — enforced by
exception class, not asserted (fix cycle c4). Both post-create blocks (the link, and
`_fresh_board_station_field`'s field work) catch BaseException, re-raising only SystemExit so a
deliberate exit 4 passes through. c3 stated this outcome while catching GhError alone, which was
false: `factory_gh.run_gh`'s bare `json.loads(r.stdout)` (factory_gh.py:170) raises ValueError on
an unparseable success body, and `_project_field_resolve`'s unguarded `field_obj["id"]` /
`o["name"]` (factory_gh.py:459-462) raise KeyError or TypeError — each escaped to
`factory_cli.run`'s `except BaseException` (factory_cli.py:88) and exited 2, the code that means
nothing was written, with a board already created and linked.
ONE WINDOW REMAINS, and it is named rather than papered over: `factory_gh.project_create` itself
is not wrapped, because a failure there has no created number to report. Every GhError it raises
is a genuine zero-mutation failure (the owner-id read failed, or the mutation was rejected and
returned null), so 2 is correct for those. A non-GhError inside it — a `json.loads` ValueError on
the createProjectV2 response, where gh exited 0 and the board therefore EXISTS — exits 2 while a
board exists, and no catch here could name its number. Closing it needs a read-back
(`project_resolve` by title) that this module does not do today.

A FRESH BOARD IS NOT EMPTY — MEASURED 2026-08-23 on project 7, owner mruangutai (fix cycle c3).
A brand-new Projects v2 project ALREADY carries a `Status` single-select field whose options are
Todo, In Progress and Done (plus Title, Assignees, Labels, Linked pull requests, Milestone,
Repository, Reviewers, Parent issue, Sub-issues progress, Created, Updated and Closed, all plain
ProjectV2Field). c2 asserted the opposite — that a just-created project "is empty by
construction, so `field` cannot already be taken" — and a live provision against that project
proved it false: `createProjectV2Field` returned "Name cannot have a reserved value, Name has
already been taken" and the run exited 4 with the project created and linked. So the create
branch PROBES with `_field_probe` exactly like the resolved-project path, and where the field
already exists as a single-select it is set to EXACTLY the declared stations — deleting GitHub's
Todo and In Progress. That exact replace is confined to a project the SAME run created, where no
item exists to lose a column; see `_fresh_board_station_field` and `_extend_to_union`.

THE LINKAGE GUARD (fix cycle c1, MUST-FIX 1) — read this before changing step 2.5's dispatch.
`factory_gh.project_resolve` confirms only that a project NUMBER exists under `owner` — its query
carries no repository linkage at all. Projects v2 numbers are per-OWNER, not per-repo (that is why
`linkProjectV2ToRepository` exists as a separate mutation), so a SERVED repo's own remote
harness.json can legitimately name a project that is not linked to it — including this checkout's
OWN board, under the same owner. Both field-schema mutation branches below (create the field,
extend it) are UNGUARDED against that: `project_single_select_extend`'s mutation REPLACES the
option set, so landing on the wrong board there deletes its columns. `_project_linked_repos`,
below, is the read side T-03 never built (T-03 built the write, `project_link_repository`, but no
read of the same connection) — one paginated, read-only GraphQL query over the project's own
`repositories` connection, sent through `factory_gh.run_gh` like `_field_probe`. `provision` refuses
(exit 2, zero mutations) whenever `repo_name` is absent from it, before either field-schema branch
runs.

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
import collections
import glob
import json
import os
import re
import subprocess
import sys

import factory_cli
import factory_config
import factory_gh
import gh_board

_TOOL = "board_lifecycle"
_SINGLE_SELECT = "ProjectV2SingleSelectField"

# A structured finding: `kind` is one of the six closed classes, `message` is the EXACT string
# `audit` prints (unchanged by T-06), `data` is whatever `reconcile` needs to fix it — empty for
# DECLARATION and WORKFLOW, which no write here ever touches.
Finding = collections.namedtuple("Finding", "kind message data")


def _finding(kind, message, **data):
    return Finding(kind, message, data)


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


# See the module docstring's THE LINKAGE GUARD section. `repositories` is a project's own
# connection to every repository `linkProjectV2ToRepository` has linked it to; membership there,
# never the project's mere existence under `owner`, is what makes `repo_name` the RIGHT board.
_LINKED_REPOS_QUERY = """query($owner: String!, $number: Int!, $after: String) {
  repositoryOwner(login: $owner) {
    __typename
    ... on ProjectV2Owner {
      projectV2(number: $number) {
        repositories(first: 100, after: $after) {
          nodes { nameWithOwner }
          pageInfo { hasNextPage endCursor }
        }
      }
    }
  }
}
"""

# 100 repos/page x this cap = 1000 -- the SAME truncation bound retitle's own enumeration refuses
# at (_RETITLE_LIMIT), applied here to the same "never silently trust a partial list" principle.
_LINKED_REPOS_PAGE_CAP = 10


def _project_linked_repos(owner, number):
    """Every `owner/name` string `owner`'s project `number` is linked to, read-only, via
    `_LINKED_REPOS_QUERY` paginated through `repositories(first: 100, after:)`. Mutates nothing.

    Raises `factory_gh.GhError` if the connection exceeds `_LINKED_REPOS_PAGE_CAP` pages rather
    than returning a partial list a caller could mistake for the complete linkage set -- the same
    posture retitle's own `--limit`-truncation refusal takes for its enumeration.
    """
    names = []
    after = None
    for _ in range(_LINKED_REPOS_PAGE_CAP):
        argv = ["api", "graphql", "-f", "query=" + _LINKED_REPOS_QUERY,
                "-f", "owner=" + owner, "-F", "number=" + str(number)]
        if after is not None:
            argv += ["-f", "after=" + after]
        env = factory_gh.run_gh(argv, json_out=True)
        data = env.get("data") or {}
        repo_owner = data.get("repositoryOwner") or {}
        project = repo_owner.get("projectV2") or {}
        conn = project.get("repositories") or {}
        for node in conn.get("nodes", []):
            nwo = node.get("nameWithOwner")
            if nwo:
                names.append(nwo)
        page = conn.get("pageInfo") or {}
        if not page.get("hasNextPage"):
            return names
        after = page.get("endCursor")
    raise factory_gh.GhError(
        [], None, "", "", "linked-repository list exceeds the page cap",
        f"{owner} project {number} ({_LINKED_REPOS_PAGE_CAP * 100}+ linked repos)",
        "raise _LINKED_REPOS_PAGE_CAP or confirm the linkage manually before provisioning",
    )


def _missing_options(declared_stations, board_option_names):
    """The declared values absent from the board, byte-for-byte and case-sensitive (DEC-192),
    preserving declared key order. T-05's DECLARATION finding class calls this SAME helper —
    do not re-author the comparison there; D-05 makes the exactness load-bearing and two
    implementations means a later loosening has two sites and no invariant tying them together."""
    return [v for v in declared_stations if v not in board_option_names]


def _declared_stations(board):
    return [board["stations"][k] for k in
            ("backlog", "plan", "ready", "building", "review", "done")]


# feature.json's top-level `status` values that map onto a board station, keyed to the SAME
# `board["stations"]` keys `_declared_stations` reads (T-15). `Abandoned` is deliberately absent:
# DEC-192 gives it no board column at all, so there is no key for it to map to.
_STATUS_TO_STATION_KEY = {
    "Backlog": "backlog", "Plan": "plan", "Ready": "ready",
    "Building": "building", "Review": "review", "Done": "done",
}


def _feature_dirs(root):
    """Every feature directory under the harness root, `<root>/.harness/*/features/*` — the SAME
    glob shape `check-state.sh`'s own INV-24/INV-26 invariants read, so a feature this audit sees
    is the same set those invariants see (T-15)."""
    pattern = os.path.join(root, ".harness", "*", "features", "*", "feature.json")
    return sorted(os.path.dirname(p) for p in glob.glob(pattern))


def _status_findings(root, board, stations):
    """Class 6 -- STATUS (T-15). No network call: reads each feature's `feature.json` off disk
    and reuses `stations`, the SAME station map class 2 (STATION) already fetched for this repo.

    CALLED ONLY WHEN THE AUDITED REPO IS THIS CHECKOUT'S OWN REPO (#783's fix) -- see
    `_audit_findings`'s Class 6 section for the caller-side check and why it lives there rather
    than in here.

    THE RULING (#783), stated once here because it has to be explicit rather than implied by a
    filter: `_feature_dirs` walks `<root>/.harness/*/features/*` -- ALWAYS this checkout's own
    on-disk tree, regardless of which repo `--repo` names. A served fleet repository's features
    are never there; its own `.harness/harness.json` is read REMOTELY
    (`factory_config.product_config` -> `factory_gh.file_at_ref`), never from a directory in
    this checkout, and no feature.json anywhere records a `github.repo` field to filter by
    (checked: none of this tree's feature.json files carry one). Scoping this class to
    "features whose recorded repo matches the audited one" would mean inventing a field that
    does not exist on disk. Self-skip is the honest alternative, and it is what `_audit_findings`
    does: this class runs ONLY for this checkout's own repo, and prints one line saying so for
    any other `--repo`, rather than silently comparing this checkout's features against a
    foreign board (the live defect measured on board 2 with `--repo mruangutai/kaya-ai`: 18 of
    29 findings were this checkout's own harness issues compared against kaya-ai's board).

    feature.json's `status` IS THE AUTHORITY here, never the card (T-13's outbound posture,
    DEC-138) -- a disagreement means the card drifted, not that the recorded status is wrong.

    THREE exemptions, and only three (T-15 intent):
    - status `Abandoned` -- DEC-192 gives it no board column to compare against.
    - no recorded `github.parent` -- INV-21 already reports that shape.
    - issues recorded under `factory.issues` rather than `github.issues` -- that feature's cards
      live on the PRODUCT's board, not this one (the same carve-out check-state.sh's INV-26
      already makes for the factory lane).
    There is NO Done exemption (D-22): a status of Done whose parent is not at the done station
    is a finding whether the parent issue is open or closed.
    """
    findings = []
    for feat_dir in _feature_dirs(root):
        try:
            with open(os.path.join(feat_dir, "feature.json"), encoding="utf-8") as f:
                fj = json.load(f)
        except (OSError, ValueError):
            continue
        if not isinstance(fj, dict):
            continue

        status = fj.get("status")
        station_key = _STATUS_TO_STATION_KEY.get(status)
        if station_key is None:
            # Either `Abandoned` (exemption 1) or an unrecognised/absent status -- nothing to
            # compare against either way.
            continue

        github = fj.get("github")
        github = github if isinstance(github, dict) else {}
        parent = github.get("parent")
        if not isinstance(parent, int):
            continue  # exemption 2 -- no recorded parent; INV-21's finding, not this one.

        if not github.get("issues"):
            factory_block = fj.get("factory")
            factory_block = factory_block if isinstance(factory_block, dict) else {}
            if factory_block.get("issues"):
                continue  # exemption 3 -- this feature's cards live on the PRODUCT's board.

        expected = board["stations"][station_key]
        actual = stations.get(parent)
        if actual != expected:
            findings.append(_finding(
                "STATUS",
                f"STATUS: {feat_dir} records status {status!r} (column {expected!r}) but its "
                f"parent #{parent} reads {actual!r}",
                parent=parent, expected=expected, status=status,
            ))
    return findings


def _fresh_board_station_field(created, repo_name, owner, field, declared):
    """Put the declared station field on a project THIS RUN created -- and ONLY such a project.

    THE EXACT-REPLACE CARVE-OUT (fix cycle c3). This is the one place in this module that may
    hand `project_single_select_extend` the bare `declared` list. That mutation REPLACES a
    field's option set, so passing `declared` DELETES every option not declared -- on an
    established board that is the column-deletion disaster the primitive's own docstring warns
    about and D-plan T-03 forbids, which is why the resolved-project path goes through
    `_extend_to_union` instead -- which does take `declared` (c3's comments said it took no
    option list; that was false, corrected in c4) but uses it only to compute the missing set,
    and passes the replacing mutation an inline `existing + missing` from its own read. It is safe
    HERE, and only here: `created` is `project_create`'s own return value from the same run, so
    the project holds no items and no card can lose its column. The parameter is the create
    record for that reason -- an existing-board caller has nothing to pass.

    MEASURED, not assumed (2026-08-23, project 7 on mruangutai): a brand-new Projects v2 project
    already carries a `Status` single-select field with options Todo / In Progress / Done. So all
    three shapes are reachable and each is handled: field ABSENT (a declaration whose
    `station_field` is not `Status` -- e.g. `Station`), field EXISTS as single-select (what a
    real fresh board gives you for `Status`, and where the exact replace leaves precisely the
    declared six), field EXISTS as something else (no fresh board does this today; the API is
    not promised to stay still, so it exits rather than guessing).

    Returns None on success -- the caller then exits 3, whose meaning is unchanged. Exits 4 on
    every failure, the same code and the same shape as the create+link failure paths: a project
    EXISTS and is LINKED, so "nothing mutated" (exit 2) would be false, and stderr names the
    CREATED number because a retry that cannot see it re-enters the create branch and produces a
    SECOND duplicate board.

    THAT PROMISE IS ENFORCED BY EXCEPTION CLASS, not merely stated (fix cycle c4). The catch
    below is not GhError-only: a ValueError from `run_gh`'s `json.loads` or a KeyError/TypeError
    from `_project_field_resolve`'s unguarded subscripts would otherwise reach
    `factory_cli.run`'s generic `except BaseException` and exit 2 -- the one code that asserts
    nothing was written, after a project has been created and linked. See the comment on that
    clause.

    A CONSIDERED, ACCEPTED RESIDUAL (fix cycle c4): the exact-replace confinement rests on
    `created` being a create record by SHAPE (it is subscripted for `number` and `id`), never on
    a type, so a future caller could hand-build a dict with those keys and reach the exact
    replace against an established board. Accepted rather than closed: the only other
    project-record shape in this module is `project_resolve`'s `{"id", "title"}`
    (factory_gh.py:544), which has no `number` key and so raises KeyError before any mutation --
    a real barrier, not a comment. Moving `project_create` inside this helper would close it
    fully, but that would reorder the "created project N" print which fix cycle c1's MUST-FIX 2
    established must come BEFORE anything that can still fail, and that ordering is load-bearing.
    """
    def _bail(what, detail):
        print(
            f"factory: {_TOOL}: created project {created['number']} on {owner} and linked "
            f"{repo_name}, but {what} -- {detail}; the project EXISTS and is LINKED (record "
            f"{created['number']} in {repo_name}'s harness.json now to avoid a duplicate on "
            f"retry) -- re-run provision once the failure is resolved and it will repair the "
            f"field on the recorded project",
            file=sys.stderr,
        )
        sys.exit(4)

    # The probe reads `created["number"]`, never the DECLARED `number` -- the declaration's
    # number is the one that did not resolve, which is why this branch is running at all.
    try:
        field_id, typename = _field_probe(owner, created["number"], field)
        if field_id is None:
            factory_gh.project_single_select_create(created["id"], field, declared)
            _out(f"created field {field!r} with {len(declared)} option(s): "
                 f"{', '.join(declared)}")
            return
        if typename != _SINGLE_SELECT:
            # Unreachable on a fresh board TODAY (GitHub's default `Status` is a single-select).
            # Kept because this module never converts an existing field's type -- the same
            # refusal the resolved-project path makes, at exit 4 rather than 2 because a project
            # was created here.
            _bail(f"field {field!r} already exists on it as {typename}, not a single-select",
                  "board_lifecycle never converts an existing field's type -- convert or rename "
                  "that field by hand, then re-run provision against the recorded number")
        existing = factory_gh.project_field_options(owner, created["number"], field)
        factory_gh.project_single_select_extend(created["id"], field_id, declared)
    except factory_gh.GhError as exc:
        _bail(f"failed to put field {field!r} on it", str(exc))
    except SystemExit:
        # `_bail` itself raises this from inside the try (the wrong-field-type branch above).
        # It is the intended exit 4 and must reach the interpreter unchanged -- re-wrapping it
        # would replace a precise refusal message with the generic unexpected-failure one.
        raise
    except BaseException as exc:
        # Fix cycle c4, finding 1. A GhError-only catch here was a REAL exit-code defect, not a
        # hypothetical: `factory_gh.run_gh`'s bare `json.loads(r.stdout)` (factory_gh.py:170)
        # raises ValueError on an unparseable success body, and `_project_field_resolve`'s
        # unguarded `field_obj["id"]` / `o["name"]` (factory_gh.py:459-462) raise KeyError or
        # TypeError on a shape it did not expect -- both inside this try, neither a GhError.
        # Each escaped to `factory_cli.run`'s `except BaseException` (factory_cli.py:88), which
        # exits EXIT_REFUSED = 2, and 2 means "nothing was written". A project has been created
        # and linked by the time this runs, so an operator or script reading 2 as "nothing
        # happened" retries, re-enters the create branch and gets a SECOND board. Every failure
        # here is exit 4 regardless of class; nothing is swallowed.
        _bail(f"an UNEXPECTED {type(exc).__name__} interrupted the field work for {field!r}",
              f"{exc} -- this is not a gh failure the module anticipated, so the field's state "
              f"on the new project is UNKNOWN; check it before re-running")
    removed = [o for o in existing if o not in declared]
    _out(f"field {field!r} already existed on the new project (GitHub's default) -- replaced "
         f"its options with exactly the {len(declared)} declared: {', '.join(declared)}"
         + (f"; REMOVED {len(removed)}: {', '.join(removed)}" if removed
            else "; removed nothing"))


def _extend_to_union(project_id, field_id, owner, number, field, declared):
    """Widen an EXISTING board's single-select to cover every declared station, keeping every
    option the operator already has.

    THE MUTATION ARGUMENT IS COMPUTED HERE, never passed through (fix cycle c3, restated
    correctly in c4). `declared` IS a parameter -- it has to be, it is what the union is computed
    against -- and c3's comments claimed otherwise ("takes NO option list"), which was false as
    literal code. The property that actually holds is narrower and sufficient: `declared` is
    consumed ONLY by `_missing_options` below, and the single argument
    `project_single_select_extend` ever receives from this function is the inline
    `existing + missing`, built from this function's own read. So no caller can cause a bare
    `declared` to reach that mutation through this path -- which matters because the mutation
    REPLACES a field's option set, so a bare `declared` on a live board DELETES every column the
    declaration does not name (D-plan T-03, and `project_single_select_extend`'s own docstring).
    The exact-replace behaviour exists in exactly one other place,
    `_fresh_board_station_field`, and is reachable only from a project the same run created.
    """
    existing = factory_gh.project_field_options(owner, number, field)
    missing = _missing_options(declared, existing)
    if not missing:
        _out("nothing to do")
        return
    factory_gh.project_single_select_extend(project_id, field_id, existing + missing)
    _out(f"added {len(missing)} option(s) to {field!r}: {', '.join(missing)}")


def cmd_provision(repo_arg):
    """Create or repair the declared board. Exits 0 (correct), 2 (unusable declaration/caller,
    zero mutations), 3 (a new project was created, linked and its station field made to carry
    every declared station — record the number) or 4 (a write was attempted and did not fully
    land; stderr names the created number). See the module docstring's PROVISION'S EXIT CODES
    and A FRESH BOARD IS NOT EMPTY paragraphs for the full contract.
    """
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
        # Fix cycle c1, MUST-FIX 2: the created project's number is printed BEFORE anything
        # that can still fail (the link call) -- an exit code that follows a partial mutation
        # must never read like "nothing mutated" (exit 2, this module's OWN caller/declaration
        # code), and a naive retry that saw exit 2 here would re-enter this branch and create a
        # SECOND duplicate board, the exact disaster `project_resolve`'s own docstring names.
        created = factory_gh.project_create(owner, f"{repo_name} board")
        _out(f"no project {number} on {owner} -- created project {created['number']}; record "
             f"number {created['number']} in {repo_name}'s harness.json")
        try:
            factory_gh.project_link_repository(created["id"], repo_name)
        except SystemExit:
            raise
        except BaseException as exc:
            # Fix cycle c4, finding 1, SECOND instance: this catch was GhError-only too, and
            # `project_link_repository` sends TWO `run_gh(json_out=True)` calls
            # (factory_gh.py:613, 622) whose `json.loads` raises ValueError, plus an unguarded
            # `repository["id"]`. A project already exists at this point, so the same reasoning
            # applies verbatim -- exit 2 here would claim nothing was written and a retry would
            # duplicate the board. Broadened alongside `_fresh_board_station_field`'s, because
            # leaving it would keep the module docstring's "4 is never conflated with 2" false
            # for a different line.
            if not isinstance(exc, factory_gh.GhError):
                exc = f"unexpected {type(exc).__name__}: {exc}"
            print(
                f"factory: {_TOOL}: created project {created['number']} on {owner} but "
                f"failed to link {repo_name} -- {exc}; the project EXISTS (record "
                f"{created['number']} in {repo_name}'s harness.json now to avoid a duplicate "
                f"on retry) -- link it manually (project_link_repository) or re-run once the "
                f"failure is resolved",
                file=sys.stderr,
            )
            sys.exit(4)
        _out(f"linked {repo_name} to project {created['number']}")
        # Fix cycle c2 (SC-01): the station field lands HERE, in the SAME run as the project --
        # it never waits for a second one. Every input is already in hand: `created["id"]` is
        # the new project's node id, and both `field` and `declared` come from the DECLARATION
        # (harness.json's `github.board`), never from the board number, so neither depends on
        # the operator having recorded the new number yet.
        # Fix cycle c3: this branch PROBES rather than assuming the field is absent. c2 asserted
        # here that a just-created project "is empty by construction, so `field` cannot already
        # be taken" -- MEASURED FALSE against the real API on 2026-08-23 (project 7, owner
        # mruangutai): a brand-new Projects v2 project already carries a `Status` single-select
        # with Todo / In Progress / Done, and createProjectV2Field returned "Name has already
        # been taken" (exit 4). The whole field decision lives in `_fresh_board_station_field`,
        # which is the ONLY caller of the exact-replace path -- see its docstring.
        _fresh_board_station_field(created, repo_name, owner, field, declared)
        sys.exit(3)

    project_id = resolved["id"]

    # Step 2.5, THE LINKAGE GUARD (fix cycle c1, MUST-FIX 1): `project_resolve` above confirmed
    # only that project `number` EXISTS under `owner` -- never that it is linked to `repo_name`.
    # A served repo's own harness.json can name a project under the SAME owner it has no link to
    # (including this checkout's own board), and the field-schema mutation branches below would
    # then land on the WRONG board -- `project_single_select_extend`'s mutation REPLACES the
    # option set, so a wrong union there deletes that board's columns. Refuse before either
    # branch runs, zero mutations, exactly like the field-wrong-type disaster guard above it.
    linked = _project_linked_repos(owner, number)
    if repo_name not in linked:
        factory_cli.refuse(
            _TOOL, "project is not linked to this repository",
            f"project {number} ({owner}) is not linked to {repo_name!r} -- confused-deputy "
            f"guard: a served repo's own harness.json can name a project under the same owner "
            f"it has no link to, and the field-schema write below would then land on the wrong "
            f"board",
            f"link {repo_name!r} to project {number} ({owner}) with project_link_repository, "
            f"or correct {repo_name}'s declared board number, before provisioning",
        )

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

    # Step 4: an EXISTING board's option set is only ever WIDENED, never replaced -- and that
    # is enforced structurally (fix cycle c3, restated correctly in c4), not by a comment.
    # `_extend_to_union` DOES take `declared` -- c3's comment here claimed it takes no option
    # list, which was false as literal code. What is structural is that `declared` reaches only
    # `_missing_options` inside it, and the argument it hands
    # `project_single_select_extend` is the inline `existing + missing` computed from its own
    # read -- so a bare `declared` cannot reach the replacing mutation along this path.
    _extend_to_union(project_id, field_id, owner, number, field, declared)


# The three workflows every board needs (T-05 intent, finding class 5). Matched by NAME only —
# ProjectV2Workflow exposes neither trigger nor action (D-09) — so a renamed workflow is reported
# MISSING rather than assumed present.
_REQUIRED_WORKFLOWS = ("Item closed", "Auto-close issue", "Pull request merged")

_WORKFLOW_HEADER = (
    "workflow detection matches by NAME only -- ProjectV2Workflow exposes neither trigger nor "
    "action, so a workflow the operator renamed is reported MISSING rather than assumed present"
)
_WORKFLOW_SUFFIX = "no API can enable it -- only a click in the project's web UI can"


def _audit_findings(root, board, repo_name):
    """The closed, finite finding list (T-05/T-15 intent). Read-only: no mutation, anywhere.

    Performs exactly the four network calls the module docstring's AUDIT section names, in the
    order: field options (class 1), the closed-issue list (feeds classes 2, 3 and 4), the board
    station read (class 2), the project workflows read (class 5). Class 6 (STATUS) adds no
    network call of its own -- it reuses class 2's station read -- and self-skips (one printed
    line, no findings) unless `repo_name` is this checkout's own declared repo (#783's fix; see
    `_status_findings`'s docstring for the ruling).
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
        findings.append(_finding(
            "DECLARATION",
            f"DECLARATION: station {key!r} (declared value {value!r}) is not among project "
            f"{number}'s Status options",
        ))

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
            findings.append(_finding(
                "STATION",
                f"STATION: issue #{num} reads {stations[num]!r}, expected {done_station!r}",
                issue_number=num, expected=done_station,
            ))

    # Class 3 -- REASON.
    for issue in issues:
        if issue.get("stateReason") is None:
            num = issue.get("number")
            names = {l.get("name") for l in issue.get("labels", []) if isinstance(l, dict)}
            findings.append(_finding(
                "REASON", f"REASON: issue #{num} is closed with no state_reason",
                issue_number=num, abandoned=("abandoned" in names),
            ))

    # Class 4 -- LABEL.
    for issue in issues:
        reason = (issue.get("stateReason") or "").upper()
        if reason == "NOT_PLANNED":
            names = {l.get("name") for l in issue.get("labels", []) if isinstance(l, dict)}
            if "abandoned" not in names:
                num = issue.get("number")
                findings.append(_finding(
                    "LABEL",
                    f"LABEL: issue #{num} is not_planned and carries no 'abandoned' label",
                    issue_number=num,
                ))

    # Class 5 -- WORKFLOW. Call 4/4.
    _out(_WORKFLOW_HEADER)
    workflows = factory_gh.project_workflows(owner, number)
    by_name = {w["name"]: w for w in workflows}
    for name in _REQUIRED_WORKFLOWS:
        w = by_name.get(name)
        if w is None:
            findings.append(_finding(
                "WORKFLOW", f"WORKFLOW: {name!r} is MISSING -- {_WORKFLOW_SUFFIX}"))
        elif not w.get("enabled"):
            findings.append(_finding(
                "WORKFLOW", f"WORKFLOW: {name!r} is disabled -- {_WORKFLOW_SUFFIX}"))

    # Class 6 -- STATUS. No call, EXCEPT it self-skips for any repo but this checkout's own
    # (#783's fix -- see `_status_findings`'s own docstring for the ruling and why). This
    # checkout's on-disk `.harness/*/features/*` is never a served fleet repo's feature set --
    # that repo's config is read remotely and no feature.json records a `github.repo` to filter
    # by, so scoping instead of skipping would mean inventing a field that does not exist.
    own_repo = _own_repo(root)
    if repo_name == own_repo:
        findings.extend(_status_findings(root, board, stations))
    else:
        _out(f"STATUS: skipped -- auditing {repo_name!r}, not this checkout's own repo "
             f"({own_repo!r}); this checkout's on-disk features are never that repo's")

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
        findings = _audit_findings(root, board, repo_name)
    except factory_gh.GhError as exc:
        print(f"factory: {_TOOL}: {exc}", file=sys.stderr)
        sys.exit(4)

    for f in findings:
        _out(f.message)
    _out(f"{len(findings)} finding(s)")
    if findings:
        sys.exit(1)


# ---------------- reconcile (T-06) -- the write side of audit ----------------

# STATION, REASON and LABEL are always attempted; STATUS is attempted for every status except
# Done (see the module docstring's RECONCILE section for why). DECLARATION and WORKFLOW never
# are -- neither reaches this set.
_ALWAYS_FIXABLE_KINDS = {"STATION", "REASON", "LABEL"}

_ABANDONED_LABEL_COLOR = "b60205"  # MUST match gh-sync.py's own colour for this label (D-04).


def _fixable(finding):
    """Whether `reconcile` attempts this finding's fix, and whether it counts toward the exit
    code. STATUS is fixable for every recorded status except Done -- Done and Abandoned are
    T-15's own exemptions; Abandoned never reaches here at all (`_status_findings` never
    emits it), so only Done needs an explicit check here."""
    if finding.kind in _ALWAYS_FIXABLE_KINDS:
        return True
    if finding.kind == "STATUS":
        return finding.data.get("status") != "Done"
    return False


def _ensure_abandoned_label(repo_name):
    """Create the `abandoned` label directly via `GH_SYNC_GH`'s binary -- never
    `factory_gh.ensure_labels`, never a helper imported from gh-sync.py (see the module
    docstring's RECONCILE section for the two measured reasons). Swallows its error exactly as
    gh-sync.py's own `ensure_labels` does: "label already exists" is the common case, and the
    `issue edit --add-label` call right after this one is what surfaces a genuinely broken
    repo."""
    gh_bin = os.environ.get("GH_SYNC_GH", "gh")
    subprocess.run(
        [gh_bin, "label", "create", "abandoned", "--repo", repo_name,
         "--color", _ABANDONED_LABEL_COLOR, "--description", "created by harness gh-sync"],
        capture_output=True,
    )


def _apply_fix(finding, board, repo_name):
    """Perform the ONE write this finding calls for. Raises `gh_board.BoardError` or
    `factory_gh.GhError` on failure -- the caller catches, prints, and moves on to the next
    finding rather than stopping the whole run (a bulk fix that stops at the first error leaves
    the board half migrated with a zero exit)."""
    if finding.kind == "STATION":
        gh_board.set_station(
            board, repo_name, finding.data["issue_number"], finding.data["expected"])
    elif finding.kind == "STATUS":
        gh_board.set_station(
            board, repo_name, finding.data["parent"], finding.data["expected"])
    elif finding.kind == "REASON":
        num = finding.data["issue_number"]
        reason = "not_planned" if finding.data["abandoned"] else "completed"
        factory_gh.run_gh([
            "api", "-X", "PATCH", f"repos/{repo_name}/issues/{num}",
            "-f", "state=closed", "-f", f"state_reason={reason}",
        ])
    elif finding.kind == "LABEL":
        num = finding.data["issue_number"]
        _ensure_abandoned_label(repo_name)
        factory_gh.run_gh([
            "issue", "edit", str(num), "--repo", repo_name, "--add-label", "abandoned",
        ])


def cmd_reconcile(repo_arg, apply):
    root = factory_config.harness_root()
    repo_name, board = _resolve_board(root, repo_arg)
    if board is None:
        # D-07: an explicit `github.board: null` is a declaration, not a misconfiguration.
        _out("no board declared -- nothing to reconcile")
        return
    if not repo_name:
        factory_cli.refuse(
            _TOOL, "cannot reconcile", "github.repo is not declared",
            "pin github.repo in harness.json before reconciling",
        )

    try:
        findings = _audit_findings(root, board, repo_name)
    except factory_gh.GhError as exc:
        print(f"factory: {_TOOL}: {exc}", file=sys.stderr)
        sys.exit(4)

    if not apply:
        # --dry-run (the default): preview only, zero writes, zero risk of a half-applied
        # bulk write against the operator's live tracker. Always exits 0 once detection has
        # succeeded -- a preview attempts nothing, so nothing it lists can be reported as
        # having "survived" a fix it never tried.
        for f in findings:
            if _fixable(f):
                _out(f"DRY-RUN would fix -- {f.message}")
            else:
                _out(f"DRY-RUN cannot fix, needs a human -- {f.message}")
        fixable_n = sum(1 for f in findings if _fixable(f))
        human_n = len(findings) - fixable_n
        _out(f"{fixable_n} fixable finding(s) previewed; {human_n} finding(s) require a "
             f"human (see above) -- re-run with --apply to write")
        return

    # --apply: attempt every fixable finding's write, continuing past a single failure.
    for f in findings:
        if not _fixable(f):
            continue
        try:
            _apply_fix(f, board, repo_name)
        except (gh_board.BoardError, factory_gh.GhError) as exc:
            print(f"factory: {_TOOL}: fix failed -- {exc}", file=sys.stderr)

    # Re-run the SAME detection in this process to report the residual state truthfully,
    # rather than assume every write landed.
    try:
        residual = _audit_findings(root, board, repo_name)
    except factory_gh.GhError as exc:
        print(f"factory: {_TOOL}: {exc}", file=sys.stderr)
        sys.exit(4)

    for f in residual:
        _out(f.message)
    fixable_residual = [f for f in residual if _fixable(f)]
    human_residual = [f for f in residual if not _fixable(f)]
    _out(f"{len(fixable_residual)} fixable finding(s) remain; {len(human_residual)} "
         f"finding(s) require a human (see above)")
    if fixable_residual:
        sys.exit(1)


# ---------------- retitle (T-17) -- the one-time task-ticket title backfill ----------------

# The OLD format's own separator (gh-sync.py's title before T-16: `f"{task['id']} — {task['title']}"`)
# -- captures the task id and the task's own title text verbatim, so `_retitled_title` below
# reproduces `cmd_open`'s new f-string byte for byte from that captured text.
_OLD_TASK_TITLE_RE = re.compile(r"^(T-\d+) — (.+)$")

_RETITLE_LIMIT = 1000


def _retitled_title(feat, tid, rest):
    """The SAME f-string gh-sync.py:764 builds for a freshly-opened task issue -- byte for
    byte, so a backfilled title and a freshly-`open`ed one can never disagree."""
    return f"{feat} — {tid} — {rest}"


def cmd_retitle(repo_arg, apply):
    root = factory_config.harness_root()
    # retitle has no use for a board -- it renames issue titles, never a card -- so only the
    # repo-name half of `_resolve_board` is reused; the board it returns is discarded. An
    # unrecognised --repo still refuses (exit 2) through that same call.
    repo_name, _board = _resolve_board(root, repo_arg)
    if not repo_name:
        factory_cli.refuse(
            _TOOL, "cannot retitle", "github.repo is not declared",
            "pin github.repo in harness.json before retitling",
        )

    try:
        issues = factory_gh.run_gh(
            ["issue", "list", "--repo", repo_name, "--state", "all",
             "--limit", str(_RETITLE_LIMIT), "--json", "number,title,milestone"],
            json_out=True,
        )
    except factory_gh.GhError as exc:
        print(f"factory: {_TOOL}: {exc}", file=sys.stderr)
        sys.exit(4)

    if len(issues) >= _RETITLE_LIMIT:
        factory_cli.refuse(
            _TOOL, "issue enumeration may be truncated",
            f"{len(issues)} issues returned for --limit {_RETITLE_LIMIT}",
            "raise the limit or paginate before trusting this backfill",
        )

    to_rename = []
    already_correct = 0
    refused = 0
    for issue in issues:
        title = issue.get("title") or ""
        m = _OLD_TASK_TITLE_RE.match(title)
        if not m:
            continue  # not a task-shaped title at all -- a parent, a milestone, or unrelated.
        tid, rest = m.group(1), m.group(2)

        milestone = issue.get("milestone")
        feat = milestone.get("title") if isinstance(milestone, dict) else None
        if not feat:
            refused += 1
            _out(f"REFUSED: issue #{issue.get('number')} {title!r} carries no milestone -- "
                 f"cannot derive its feature id (D-20)")
            continue

        if title.startswith(f"{feat} — "):
            already_correct += 1  # idempotent skip -- the title itself records the rename.
            continue

        to_rename.append((issue.get("number"), title, _retitled_title(feat, tid, rest)))

    if not apply:
        for num, old, new in to_rename:
            _out(f"DRY-RUN would rename #{num}: {old!r} -> {new!r}")
        _out(f"renamed: 0; already correct: {already_correct}; refused: {refused}; "
             f"{len(to_rename)} to rename; projected cost {2 * len(to_rename)} GraphQL points "
             f"(2 points per rename, measured 2026-08-22 at f5f5185)")
        return

    # MUST-FIX 3: each rename is caught PER-TICKET, mirroring `reconcile`'s own apply loop
    # (`cmd_reconcile`'s `for f in findings: ... except (gh_board.BoardError,
    # factory_gh.GhError)`) -- a failed write for one ticket is printed and counted, and the
    # run continues to the rest, rather than a `GhError` propagating past this loop into
    # `factory_cli.run`'s generic trap, which would exit 2 and leave every already-renamed
    # ticket unreported behind a caller/declaration exit code on a run that partially succeeded.
    renamed = 0
    failed = 0
    for num, old, new in to_rename:
        try:
            factory_gh.run_gh(["issue", "edit", str(num), "--repo", repo_name, "--title", new])
        except factory_gh.GhError as exc:
            failed += 1
            print(f"factory: {_TOOL}: rename failed for #{num} -- {exc}", file=sys.stderr)
            continue
        renamed += 1
        _out(f"renamed #{num}: {old!r} -> {new!r}")

    _out(f"renamed: {renamed}; already correct: {already_correct}; refused: {refused}; "
         f"failed: {failed}; points spent (approx): {2 * renamed}")
    if failed:
        sys.exit(1)


def _main():
    parser = argparse.ArgumentParser(
        prog="board_lifecycle.py",
        description="board_lifecycle.py <provision|audit|reconcile|retitle> [--repo <owner/name>]",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_provision = sub.add_parser("provision")
    p_provision.add_argument("--repo", default=None)
    p_audit = sub.add_parser("audit")
    p_audit.add_argument("--repo", default=None)
    p_reconcile = sub.add_parser("reconcile")
    p_reconcile.add_argument("--repo", default=None)
    p_reconcile.add_argument("--apply", action="store_true")
    p_retitle = sub.add_parser("retitle")
    p_retitle.add_argument("--repo", default=None)
    p_retitle.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.cmd == "provision":
        cmd_provision(args.repo)
    elif args.cmd == "audit":
        cmd_audit(args.repo)
    elif args.cmd == "reconcile":
        cmd_reconcile(args.repo, args.apply)
    elif args.cmd == "retitle":
        cmd_retitle(args.repo, args.apply)


if __name__ == "__main__":
    factory_cli.run(_TOOL, _main, expected=(factory_gh.GhError, factory_config.FleetError))
