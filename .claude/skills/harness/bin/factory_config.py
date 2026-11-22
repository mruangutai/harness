"""Factory fleet paths, repository queries, product configuration, and board validation.

Fleet bytes and schema validation are owned by ``artifact_accessors.load_fleet``. Factory tools
use that accessor and the domain helpers in this module rather than deriving configuration from
the working directory. That matters most for factory_workspace.py and factory_land.py, which
operate a CHECKOUT OF ANOTHER REPOSITORY: run from inside it, a relative fleet.yaml path would
resolve against the target repo, not the factory's own — so FLEET_PATH here is always absolute,
never derived from the current directory.

A fleet member's own configuration — its board included — no longer lives in fleet.yaml at all.
It lives in THAT repository's own .harness/harness.json, under the github.board key, and this
module is the only reader of it too: product_config() reads it, always REMOTELY at the member's
default_branch, via factory_gh.file_at_ref, never from a checkout on disk.

ROOT RESOLUTION is delegated whole to `harness_boundary.resolve_root(_BIN_DIR)` — the one
resolver every caller in this tree now shares (FEAT-42), never a second copy standardised on
here. It reads its one override variable (see that module's own docstring for the exact name)
only, honours it when `.harness/team-config.yaml` (its MARKER) is readable underneath, and
otherwise derives the root from this file's own location, walking up out of the bin directory.
`strict=True` (the default) raises rather than returning a confident wrong answer when neither
candidate carries MARKER; see FLEET_PATH below for why that raise cannot fire in practice. A
discarded override is announced on stderr, never swapped in silence — resolve_root's own
contract, not restated here.

Importing this module has no side effects beyond resolving that root and computing FLEET_PATH:
no fleet file is read, nothing is written, and no GitHub call is made until a caller asks.
"""
import argparse
import json
import os
import sys

import artifact_accessors
import factory_cli
import factory_gh
import harness_boundary
import harness_yaml

_BIN_DIR = os.path.dirname(os.path.abspath(__file__))

# THE ONE STATION TABLE (FEAT-61 D-02). One row per station: its name, whether it has a board
# column, and its lifecycle bucket. Every other station fact in this tree is a VIEW of these rows,
# so a station cannot be half-added — a row that names no bucket is a construction error here,
# never a name that is silently in no bucket at a call site. The data structure carries the
# weight so call sites carry no conditions. Row order is contract: the board reads its columns in
# this order, and FINISHED_STATIONS keeps the `("done",) + TERMINAL_STATIONS` order every
# consumer used to concatenate by hand.
#
# Board-column axis — `abandoned` (planned, never built — DEC-203) and `rejected` (refused at
# first-run intake as wrong or superseded — FEAT-1714) are NOT board stations; they have no
# column and must stay out of MANDATED_STATIONS. harness.json's github.board.stations must equal
# list(MANDATED_STATIONS) exactly, in this order, so the declaration is a checksum against this
# table rather than a source of new names (FEAT-41 T-01).
#
# Lifecycle axis — the buckets partition the vocabulary: `not_started` (backlog), `active` (the
# four stations where work is in progress) and `finished` (done, plus the two terminal names).
# `finished` is NOT evidence that work started: abandoned can happen before execution and
# rejected happens at intake, which is why plan-merge.py keeps its own `_work_started` predicate.
STATION_ROWS = (
    # name        board column  bucket
    ("backlog",   True,         "not_started"),
    ("plan",      True,         "active"),
    ("ready",     True,         "active"),
    ("building",  True,         "active"),
    ("review",    True,         "active"),
    ("done",      True,         "finished"),
    ("abandoned", False,        "finished"),
    ("rejected",  False,        "finished"),
)

MANDATED_STATIONS = tuple(name for name, column, _ in STATION_ROWS if column)
TERMINAL_STATIONS = tuple(name for name, column, _ in STATION_ROWS if not column)
ACTIVE_STATIONS = tuple(name for name, _, bucket in STATION_ROWS if bucket == "active")
FINISHED_STATIONS = tuple(name for name, _, bucket in STATION_ROWS if bucket == "finished")

_BUCKET_OF = {name: bucket for name, _, bucket in STATION_ROWS}


def _bucket(name):
    """The lifecycle bucket of a declared station name, or FleetError. STRICT (D-03): only an
    exact declared string is a station. `x in FINISHED_STATIONS` returned False for a typo, an
    empty status or a capitalised column name, and let corrupt station data pass as "not
    finished"; a boundary that answers a question about a name it does not know is not a
    boundary — the same posture station_column takes below."""
    bucket = _BUCKET_OF.get(name) if isinstance(name, str) else None
    if bucket is None:
        known = ", ".join(MANDATED_STATIONS + TERMINAL_STATIONS)
        raise artifact_accessors.FleetError("unknown station", repr(name), f"known stations: {known}")
    return bucket


def is_active(name):
    """True when work on the feature or task is in progress: plan, ready, building or review."""
    return _bucket(name) == "active"


def is_finished(name):
    """True when nothing executable remains: done, or a terminal name. Not evidence work began."""
    return _bucket(name) == "finished"

# FLEET_PATH's root always resolves inside the LIVE checkout under any test fixture root,
# because _BIN_DIR is this module's own on-disk location, and the live checkout always carries
# harness_boundary.MARKER — so resolve_root's strict raise cannot fire here. strict stays True
# rather than being weakened to False (FEAT-42).
FLEET_PATH = os.path.join(
    harness_boundary.resolve_root(_BIN_DIR), ".harness", "factory", "fleet.yaml"
)






def validate_board(board):
    """Normalise one schema-validated `github.board` mapping in place and return it. The shape
    rules (required fields, number form, the six ordered stations) live in the harness.json
    schema (FEAT-2297); this keeps only the domain normalisation every consumer relies on.

    `number` becomes an int — the schema admits an integer, an integer-valued float, or a
    whitespace-padded digit string. `stations` becomes a tuple, so no caller can append to the
    declaration. IDEMPOTENT: product_config memoises the document and board_for normalises that
    same mapping on every call, so a second call must accept what the first produced."""
    number = board["number"]
    board["number"] = int(number.strip() if isinstance(number, str) else number)
    board["stations"] = tuple(board["stations"])
    return board




def repo_entry(fleet, name):
    """Return the repos entry whose name equals `name` exactly. Raises FleetError naming
    `name` and listing the known names when it is absent — an unlisted repository is
    unusable, not silently accepted."""
    for entry in fleet["repos"]:
        if entry.get("name") == name:
            return entry
    known = ", ".join(e.get("name", "?") for e in fleet["repos"])
    raise artifact_accessors.FleetError(
        "repository not in fleet", name, f"known repos: {known} — add it to repos in fleet.yaml"
    )


_PRODUCT_CONFIG_PATH = ".harness/harness.json"
_product_config_memo = {}


def clear_product_config_memo():
    """Empty the product-config memo. This is its only sanctioned reset — no caller reaches into
    the dict by name. test-factory-config.py's check() calls this as its first statement so every
    test case begins with an empty memo (FEAT-24 T-02 item 6)."""
    _product_config_memo.clear()


def product_config(fleet, repo_name):
    """Return repo_name's own .harness/harness.json, parsed to a dict, read from the REMOTE at
    its default_branch — never from a checkout on disk, even when one exists at workspace_path.
    Resolves the entry through repo_entry, takes default_branch from it, and calls
    factory_gh.file_at_ref(repo_name, ".harness/harness.json", default_branch).

    Any failure — a GhError from factory_gh.file_at_ref, or text the validated harness.json
    loader refuses — raises FleetError naming the repository, the path and the ref via the
    human-readable form "<repo_name>@<default_branch>:.harness/harness.json", and carrying the
    loader's diagnosis. There is no fallback to workspace_path and no default.

    Successful results are memoised per (repo_name, ref) for the life of the process, so a tool
    calling board_for twice makes one network call. A failing read is NEVER memoised and never
    served from the memo — a failure is always a fresh, loud failure (item 5 governs the failure
    path; the memo, item 6, governs only the success path, and the two do not conflict). The memo
    is never persisted to disk; clear_product_config_memo() is its only sanctioned reset.
    """
    entry = repo_entry(fleet, repo_name)
    ref = entry["default_branch"]
    memo_key = (repo_name, ref)
    if memo_key in _product_config_memo:
        return _product_config_memo[memo_key]

    human_path = f"{repo_name}@{ref}:{_PRODUCT_CONFIG_PATH}"
    try:
        raw = factory_gh.file_at_ref(repo_name, _PRODUCT_CONFIG_PATH, ref)
    except factory_gh.GhError as e:
        raise artifact_accessors.FleetError(
            "product config unreadable", human_path,
            f"could not read {repo_name}'s {_PRODUCT_CONFIG_PATH} at {ref}: {e}",
        ) from e
    try:
        doc = artifact_accessors.load_harness_json(text=raw, context=human_path)
    except artifact_accessors.ArtifactAccessError as e:
        raise artifact_accessors.FleetError(
            "product config invalid", human_path,
            f"repair {repo_name}'s {_PRODUCT_CONFIG_PATH} at {ref}: {e}",
        ) from e

    _product_config_memo[memo_key] = doc
    return doc


def product_config_report(fleet):
    """Return a reachability report: one entry per repository in fleet["repos"], IN DECLARATION
    ORDER, each {"repo": name, "ref": entry default_branch, "path": _PRODUCT_CONFIG_PATH,
    "ok": bool, "detail": str}. Calls product_config(fleet, name) for each and catches ONLY
    FleetError — success sets ok True and detail "", a caught FleetError sets ok False and
    detail str(exc). Any other exception propagates, because a report that swallows an
    unexpected bug would report every member unreachable for the wrong reason.

    Makes no other call, and does not clear or consult the process memo itself —
    product_config already never memoises a failure.

    The "ok" count in the returned entries is meaningful only READ BESIDE the declared count
    (len(fleet["repos"])): a report over an empty repos list is vacuously all-ok."""
    report = []
    for entry in fleet["repos"]:
        name = entry["name"]
        ref = entry["default_branch"]
        try:
            product_config(fleet, name)
            ok, detail = True, ""
        except artifact_accessors.FleetError as e:
            ok, detail = False, str(e)
        report.append(
            {"repo": name, "ref": ref, "path": _PRODUCT_CONFIG_PATH, "ok": ok, "detail": detail}
        )
    return report


def board_for(fleet, repo_name):
    """Return repo_name's own board mapping, read from its validated product configuration
    (product_config above) at github.board and normalised by validate_board. The schema defaults
    an absent board to null, but for a fleet member a board is REQUIRED — a repository the
    factory serves with no board is a misconfiguration — so null raises FleetError."""
    entry = repo_entry(fleet, repo_name)
    board = product_config(fleet, repo_name)["github"]["board"]
    if board is None:
        raise artifact_accessors.FleetError(
            "product config missing board", "github.board",
            f"declare github.board in {repo_name}@{entry['default_branch']}:{_PRODUCT_CONFIG_PATH}",
        )
    return validate_board(board)


def station_names(board):
    """Return the validated declaration's six station names, as a tuple of lowercase names.

    The accessor every other module uses instead of reaching into board["stations"] itself, so a
    later change to the declaration's container shape lands here and nowhere else. Before FEAT-41
    T-01 eight non-test modules subscripted board["stations"] directly, and turning that mapping
    into a list took check-state.py down (issue #1033)."""
    return tuple(board["stations"])


def station_column(name):
    """Return the board's exact column name for one lowercase station.

    THE ONLY PLACE IN THE TREE A CAPITALISED STATION NAME IS PRODUCED. Every value written to the
    board's station field comes through here, and .capitalize() reproduces all six declared names
    exactly — Backlog, Plan, Ready, Building, Review, Done — which is why the declaration may not
    rename them.

    Raises FleetError on anything outside the six, and that INCLUDES an already-capitalised name
    and every TERMINAL_STATIONS name. Refusing a capitalised column name is deliberate: a caller holding one
    and passing it back in would otherwise have `.capitalize()` return it unchanged and silently
    work, and a case boundary that accepts its own output is not a boundary.

    The refused spellings are deliberately NOT quoted in this docstring: SC-02 greps non-test
    source for quoted station literals, and prose naming a rejected value is indistinguishable
    to that grep from code depending on it."""
    if name not in MANDATED_STATIONS:
        known = ", ".join(MANDATED_STATIONS)
        raise artifact_accessors.FleetError("unknown station", name, f"known stations: {known}")
    return name.capitalize()


def board_station(fleet, repo_name, key):
    """Return the board column name for `key` on repo_name's board; raises FleetError on a key
    the repo's declaration does not carry, listing the known station names.

    Name and signature are unchanged, but the RETURN is now derived rather than looked up: the
    declaration no longer carries column names for it to read (FEAT-41 T-01)."""
    if key not in station_names(board_for(fleet, repo_name)):
        known = ", ".join(MANDATED_STATIONS)
        raise artifact_accessors.FleetError("unknown station", key, f"known stations: {known}")
    return station_column(key)


def segment_of(repo_name):
    """Return the fleet repository name after the owner — the part of an owner-qualified
    `owner/repo` name after the first slash. This is the one home of that rule; every caller
    (factory_claim.py, feature-worktree.py:resolve_repo, workspace_path below) calls it rather
    than restating the split."""
    return repo_name.split("/", 1)[-1]


def features_root(repo_name):
    """Return the absolute path to repo_name's own `.harness/<segment>/features` directory,
    where segment is repo_name's own fleet segment (segment_of). The local is load-bearing, not
    style (A-01): layout_migration's reader rows match this join only when the segment is bound
    to a paren-free local before it, never when segment_of(repo_name) is inlined into the call."""
    seg = segment_of(repo_name)
    return os.path.join(harness_boundary.resolve_root(_BIN_DIR), ".harness", seg, "features")


def workspace_path(fleet, repo_name):
    """Return the absolute checkout path: workspace_root joined with the repository name after
    the owner. segment_of is the one place that derivation exists — factory_workspace.py and
    factory_land.py both call this function rather than restating the rule."""
    name = segment_of(repo_name)
    return os.path.join(fleet["workspace_root"], name)


def _check_product_configs(fleet, repo_name):
    """Handle --check-product-configs: optionally narrow `fleet` to one member (resolved
    through repo_entry, so an undeclared --repo name raises FleetError and is refused by the
    existing run() trap), build the reachability report, write the ONE stdout payload
    (factory_cli.payload's own contract — a second payload would break the C-3 stream contract),
    fail-log every unreachable member, and exit EXIT_REFUSED (2, never 1 — factory_cli reserves
    exit 1 for nothing-to-do) when any member is unreachable or the report came up short of the
    declared count."""
    if repo_name:
        entry = repo_entry(fleet, repo_name)
        fleet = dict(fleet, repos=[entry])
    report = product_config_report(fleet)
    ok_count = sum(1 for m in report if m["ok"])
    unreachable_count = len(report) - ok_count
    factory_cli.payload({
        "declared": len(fleet["repos"]),
        "ok": ok_count,
        "unreachable": unreachable_count,
        "members": report,
    })
    for m in report:
        if not m["ok"]:
            # Print the FleetError's own canonical line directly rather than routing back
            # through factory_cli.fail: m["detail"] is already str(FleetError), itself built by
            # factory_cli.body("what: value — next_step"), and its `value` is the SAME
            # repo@ref:path triple factory_cli.fail's own `value` argument would repeat. Two
            # near-synonymous reasons ("unreachable" here, "unreadable" in the FleetError) naming
            # the same triple twice was V-7; this keeps the "factory: {tool}: " prefix and the
            # canonical body grammar with the triple named exactly once.
            print(f"factory: config: {m['detail']}", file=sys.stderr)
    if unreachable_count or len(report) != len(fleet["repos"]):
        sys.exit(factory_cli.EXIT_REFUSED)


def _main():
    parser = argparse.ArgumentParser(prog="factory_config")
    parser.add_argument("--fleet", default=None, help="path to fleet.yaml (default: FLEET_PATH)")
    parser.add_argument("--show", action="store_true", help="print the resolved fleet as JSON")
    # This makes a network read (product_config_report -> product_config -> file_at_ref, once
    # per declared repo). check-state.py runs at every /harness door and before every commit and
    # deliberately makes no network call, so nothing about this flag is wired into it — the same
    # precedent as the board-audit reachability cost, ruled once-at-onboarding rather than on
    # every run.
    parser.add_argument(
        "--check-product-configs", action="store_true",
        help="read every fleet member's own harness.json at its default_branch",
    )
    parser.add_argument(
        "--repo", default=None,
        help="restrict --check-product-configs to one fleet member (owner/name)",
    )
    args = parser.parse_args()

    fleet = artifact_accessors.load_fleet(args.fleet) if args.fleet else artifact_accessors.load_fleet(FLEET_PATH)

    # --check-product-configs and --show are independent flags, but when both are given
    # --check-product-configs wins and --show is not printed: factory_cli.payload writes the
    # ONE stdout payload the C-3 stream contract allows, and two payloads would break it.
    if args.check_product_configs:
        _check_product_configs(fleet, args.repo)
        return

    if args.show:
        payload = {"repos": fleet["repos"]}
        factory_cli.payload(payload)


if __name__ == "__main__":
    factory_cli.run("config", _main, expected=(artifact_accessors.FleetError,))
