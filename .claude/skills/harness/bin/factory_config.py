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

# THE MANDATE the declaration is checked against, not a second vocabulary. harness.json's
# github.board.stations must equal list(MANDATED_STATIONS) exactly, in this order, so this tuple
# is the only place the six names are spelled and the declaration is a checksum against it rather
# than a source of new names (FEAT-41 T-01).
MANDATED_STATIONS = ("backlog", "plan", "ready", "building", "review", "done")

# NOT A SEVENTH STATION. `abandoned` names no board column, never reaches the board, and is
# absent from MANDATED_STATIONS for that reason — station_column raises on it. It lives in this
# module because plan-merge.py, check-plan-routes.py and check-domain.py each need the terminal
# marker and each already imports factory_config; every one of those sites imports THIS NAME
# rather than respelling the literal.
TERMINAL_MARKER = "abandoned"

# FLEET_PATH's root always resolves inside the LIVE checkout under any test fixture root,
# because _BIN_DIR is this module's own on-disk location, and the live checkout always carries
# harness_boundary.MARKER — so resolve_root's strict raise cannot fire here. strict stays True
# rather than being weakened to False (FEAT-42).
FLEET_PATH = os.path.join(
    harness_boundary.resolve_root(_BIN_DIR), ".harness", "factory", "fleet.yaml"
)






def validate_board(board, where, path):
    """Validate one board mapping and return it. This is the ONLY board validator in the tree
    (FEAT-24 T-02) — gh_board.load_board imports and calls this function directly rather than
    keeping a second copy of these rules.

    `where` is the FULL key prefix under which `board` was found, supplied entirely by the
    caller — never appended to here. board_for below passes "github.board" (a fleet member's own
    .harness/harness.json carries its board at that key); there is no fleet-level caller any
    more. Every message below names the key as f"{where}.<field>", so a caller passing
    "github.board" produces messages like "github.board.owner" — never "github.board.board.owner",
    which is not a key that exists in any file.

    Raises FleetError naming the offending field: `where` itself (not a mapping), "<where>.owner",
    "<where>.number", "<where>.station_field", "<where>.stations".

    `number` accepts an int, or a string whose stripped form is entirely digits — that string is
    coerced to an int. A bool, a float and a non-digit string are all rejected. On success this
    function MUTATES board["number"] to the coerced int, so a caller reading `board["number"]`
    after this call always sees a normalised int, and RETURNS the validated `board` mapping —
    callers consume the return value; this function does not raise-only.
    """
    key_base = where
    if not isinstance(board, dict):
        raise artifact_accessors.FleetError(
            "fleet key invalid", key_base, f"set {key_base}: {{...}} as a mapping in {path}"
        )
    if not board.get("owner"):
        raise artifact_accessors.FleetError(
            "fleet key invalid", f"{key_base}.owner",
            f"set it to the GitHub owner or org in {path}",
        )
    number = board.get("number")
    if isinstance(number, bool):
        raise artifact_accessors.FleetError(
            "fleet key invalid", f"{key_base}.number",
            f"set it to the Projects v2 board number in {path}",
        )
    elif isinstance(number, int):
        coerced = number
    elif isinstance(number, str) and number.strip().isdigit():
        coerced = int(number.strip())
    else:
        raise artifact_accessors.FleetError(
            "fleet key invalid", f"{key_base}.number",
            f"set it to the Projects v2 board number in {path}",
        )
    board["number"] = coerced
    if not board.get("station_field"):
        raise artifact_accessors.FleetError(
            "fleet key invalid", f"{key_base}.station_field",
            f"set it to the Projects v2 field name that carries the station in {path}",
        )
    # THE DECLARATION IS AN ORDERED LOWERCASE SEQUENCE, CHECKED FOR EQUALITY, NOT MEMBERSHIP
    # (FEAT-41 T-01). A mapping is the pre-FEAT-41 shape and is refused here rather than
    # tolerated, because a tolerated mapping is how two vocabularies survived in one tree. The
    # comparison is on the ORDER too: the order is the workflow, so a rotation is refused.
    #
    # A TUPLE IS ACCEPTED ALONGSIDE A LIST BECAUSE THIS FUNCTION MUST BE IDEMPOTENT. It mutates
    # board["stations"] to a tuple below, product_config MEMOISES the document it returns, and
    # board_for re-validates that same memoised mapping on every call — so a second board_for
    # revalidates a board this function already normalised. Accepting only `list` made the SECOND
    # call raise on a board the FIRST call had just approved. No parsed JSON or YAML file can
    # produce a tuple, so this widens nothing an operator can write.
    stations = board.get("stations")
    if (
        not isinstance(stations, (list, tuple))
        or list(stations) != list(MANDATED_STATIONS)
    ):
        raise artifact_accessors.FleetError(
            "fleet key invalid", f"{key_base}.stations",
            "set it to the ordered list "
            f"{list(MANDATED_STATIONS)} in {path} — these six names are FIXED and may not be "
            "renamed, reordered or extended; the board's column names are derived from them, so "
            "extra columns you add to the board are untouched by the harness",
        )
    # The returned board carries stations as a TUPLE, so no caller can append to the validated
    # declaration and every consumer reads the same immutable six.
    board["stations"] = tuple(stations)
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

    Any failure — a GhError from factory_gh.file_at_ref, a JSON parse failure, or a document that
    does not parse to a mapping — raises FleetError naming the repository, the path and the ref,
    via the human-readable form "<repo_name>@<default_branch>:.harness/harness.json". There is no
    fallback to workspace_path and no default.

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
            f"{repo_name}'s {_PRODUCT_CONFIG_PATH} at {ref} does not parse as JSON",
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
    """Return repo_name's own board mapping, read from its product configuration
    (product_config above) at the key github.board, validated by validate_board. Raises
    FleetError when the github block or the board key is absent — for a fleet member a board is
    REQUIRED, and an explicit null is an error too, because a repository the factory serves with
    no board is a misconfiguration, not a declaration — and raises whatever validate_board raises
    when the board mapping itself is malformed."""
    entry = repo_entry(fleet, repo_name)
    default_branch = entry["default_branch"]
    where = "github.board"
    path = f"{repo_name}@{default_branch}:{_PRODUCT_CONFIG_PATH}"

    doc = product_config(fleet, repo_name)
    github = doc.get("github")
    board = github.get("board") if isinstance(github, dict) else None
    if board is None:
        raise artifact_accessors.FleetError(
            "product config missing board", where,
            f"declare {where} in {path}",
        )
    return validate_board(board, where, path)


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
    and TERMINAL_MARKER. Refusing a capitalised column name is deliberate: a caller holding one
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
