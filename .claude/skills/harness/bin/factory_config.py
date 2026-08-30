"""factory_config.py — the only reader of .harness/factory/fleet.yaml (SC-08), and the only reader
of a fleet member's own product configuration (FEAT-24 T-02).

Every other factory tool takes its repository and board from this module and never from the
working directory. That matters most for factory_workspace.py and factory_land.py, which
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

import factory_cli
import factory_gh
import harness_boundary
import harness_yaml

_BIN_DIR = os.path.dirname(os.path.abspath(__file__))

_STATION_KEYS = ("backlog", "plan", "ready", "building", "review", "done")

# FLEET_PATH's root always resolves inside the LIVE checkout under any test fixture root,
# because _BIN_DIR is this module's own on-disk location, and the live checkout always carries
# harness_boundary.MARKER — so resolve_root's strict raise cannot fire here. strict stays True
# rather than being weakened to False (FEAT-42).
FLEET_PATH = os.path.join(
    harness_boundary.resolve_root(_BIN_DIR), ".harness", "factory", "fleet.yaml"
)


class FleetError(Exception):
    """str() is always built with factory_cli.body(what, value, next_step) — never by hand —
    because factory_cli.run prints str(exc) verbatim behind "factory: {tool}: ". `value` is
    always a path, a key name or a repository name the operator can act on, never a class name.
    """

    def __init__(self, what, value, next_step):
        super().__init__(factory_cli.body(what, value, next_step))


def _require_mapping(data, path):
    if not isinstance(data, dict):
        raise FleetError(
            "fleet file invalid", path, "the file must parse to a YAML mapping"
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
        raise FleetError(
            "fleet key invalid", key_base, f"set {key_base}: {{...}} as a mapping in {path}"
        )
    if not board.get("owner"):
        raise FleetError(
            "fleet key invalid", f"{key_base}.owner",
            f"set it to the GitHub owner or org in {path}",
        )
    number = board.get("number")
    if isinstance(number, bool):
        raise FleetError(
            "fleet key invalid", f"{key_base}.number",
            f"set it to the Projects v2 board number in {path}",
        )
    elif isinstance(number, int):
        coerced = number
    elif isinstance(number, str) and number.strip().isdigit():
        coerced = int(number.strip())
    else:
        raise FleetError(
            "fleet key invalid", f"{key_base}.number",
            f"set it to the Projects v2 board number in {path}",
        )
    board["number"] = coerced
    if not board.get("station_field"):
        raise FleetError(
            "fleet key invalid", f"{key_base}.station_field",
            f"set it to the Projects v2 field name that carries the station in {path}",
        )
    stations = board.get("stations")
    if (
        not isinstance(stations, dict)
        or set(stations.keys()) != set(_STATION_KEYS)
        or not all(stations.get(k) for k in _STATION_KEYS)
    ):
        raise FleetError(
            "fleet key invalid", f"{key_base}.stations",
            "set exactly backlog, plan, ready, building, review and done, each a non-empty "
            f"option name, in {path}",
        )
    return board


def load_fleet(path=FLEET_PATH):
    """Load and validate a fleet declaration. Raises FleetError naming the file and the
    offending key on every one of the malformed-fleet shapes this loader rejects — including a
    leftover top-level `board` key (the board is per-repository now, FEAT-16 T-08 — an unknown
    top-level key would otherwise be accepted silently, which would recreate the very
    inherit-a-board-nobody-chose silence this feature removes) and, after FEAT-24 T-02, a
    repos[] entry that carries a `board` key of its own — the board no longer lives in fleet.yaml
    at all; it lives in that repository's own .harness/harness.json under github.board, read
    remotely by product_config()/board_for() below."""
    data = harness_yaml.load_file(path)
    _require_mapping(data, path)

    if data.get("schema") != "factory-fleet/1":
        raise FleetError(
            "fleet schema invalid", "schema", f"set schema: factory-fleet/1 in {path}"
        )

    if "board" in data:
        raise FleetError(
            "fleet key invalid", "board",
            f"a whole-fleet board key is no longer read from here — each repository declares "
            f"its own board remotely, in its own .harness/harness.json under github.board; "
            f"remove board from {path}",
        )

    repos = data.get("repos")
    if not isinstance(repos, list) or not repos:
        raise FleetError(
            "fleet key invalid", "repos", f"set a non-empty list of repo entries in {path}"
        )
    for entry in repos:
        name = entry.get("name") if isinstance(entry, dict) else None
        if not isinstance(name, str) or "/" not in name:
            raise FleetError(
                "fleet repo entry invalid", "repos[].name",
                f"each repo needs a name containing a slash (owner/repo) in {path}",
            )
        # default_branch is NOT removed and NOT moved: factory_workspace reads it to CREATE the
        # checkout, so it cannot live inside a file that only exists once the checkout exists.
        if not entry.get("default_branch"):
            raise FleetError(
                "fleet repo entry invalid", f"repos[{name}].default_branch",
                f"set a non-empty default_branch for {name} in {path}",
            )
        if "board" in entry:
            raise FleetError(
                "fleet key invalid", f"repos[{name}].board",
                f"the board is no longer declared in fleet.yaml — {name} declares its own board "
                f"remotely, in its own .harness/harness.json under github.board. Remove "
                f"repos[{name}].board from {path}",
            )

    workspace_root = data.get("workspace_root")
    if not isinstance(workspace_root, str) or not os.path.isabs(workspace_root):
        raise FleetError(
            "fleet key invalid", "workspace_root",
            f"set it to an absolute path in {path}",
        )
    # A FILESYSTEM ROOT PASSES `isabs` AND INVERTS THE WRITE GUARD (review panel,
    # 2026-08-11). `check-domain.sh` refuses any path under `workspace_root` that
    # belongs to no declared repository. With `workspace_root: "/"` every path on the
    # machine is under it, so that branch becomes a catch-all: `/tmp/scratch.py` flips
    # from no-verdict to BLOCKED, inverting REQ-05 and the scratch-path behaviour
    # DEC-189 preserves deliberately. Verified by live probe before this check existed.
    #
    # Rejected here rather than in the guard because this is a malformed DECLARATION,
    # and `load_fleet` is the one place fleet shape is enforced — a check in the hook
    # would leave every other reader accepting the value.
    #
    # It fails CLOSED, never toward a wrongful permit, which is why it is a low finding
    # and not a high one. It is still wrong: a guard that refuses `/tmp` teaches agents
    # that the guard is broken, and DEC-151 records what an agent does next.
    if os.path.dirname(os.path.normpath(workspace_root)) == os.path.normpath(workspace_root):
        raise FleetError(
            "fleet key invalid", "workspace_root",
            f"it is a filesystem root ({workspace_root!r}) in {path} — every path on "
            f"the machine would resolve inside the factory workspace, so the write "
            f"guard would refuse scratch paths it must ignore. Set it to a real "
            f"directory that holds the checkouts.",
        )

    return data


def repo_entry(fleet, name):
    """Return the repos entry whose name equals `name` exactly. Raises FleetError naming
    `name` and listing the known names when it is absent — an unlisted repository is
    unusable, not silently accepted."""
    for entry in fleet["repos"]:
        if entry.get("name") == name:
            return entry
    known = ", ".join(e.get("name", "?") for e in fleet["repos"])
    raise FleetError(
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
        raise FleetError(
            "product config unreadable", human_path,
            f"could not read {repo_name}'s {_PRODUCT_CONFIG_PATH} at {ref}: {e}",
        ) from e
    try:
        doc = json.loads(raw)
    except (ValueError, TypeError) as e:
        raise FleetError(
            "product config invalid", human_path,
            f"{repo_name}'s {_PRODUCT_CONFIG_PATH} at {ref} does not parse as JSON",
        ) from e
    if not isinstance(doc, dict):
        raise FleetError(
            "product config invalid", human_path,
            f"{repo_name}'s {_PRODUCT_CONFIG_PATH} at {ref} must parse to a JSON mapping",
        )

    _product_config_memo[memo_key] = doc
    return doc


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
        raise FleetError(
            "product config missing board", where,
            f"declare {where} in {path}",
        )
    return validate_board(board, where, path)


def board_station(fleet, repo_name, key):
    """Return board_for(fleet, repo_name)["stations"][key]; raises FleetError on an unknown
    key, listing the known station keys."""
    stations = board_for(fleet, repo_name)["stations"]
    if key not in stations:
        known = ", ".join(stations.keys())
        raise FleetError("unknown station", key, f"known stations: {known}")
    return stations[key]


def workspace_path(fleet, repo_name):
    """Return the absolute checkout path: workspace_root joined with the repository name
    AFTER the owner. This is the one place that derivation exists — factory_workspace.py and
    factory_land.py both call it rather than restating the rule."""
    name = repo_name.split("/", 1)[-1]
    return os.path.join(fleet["workspace_root"], name)


def _main():
    parser = argparse.ArgumentParser(prog="factory_config")
    parser.add_argument("--fleet", default=None, help="path to fleet.yaml (default: FLEET_PATH)")
    parser.add_argument("--show", action="store_true", help="print the resolved fleet as JSON")
    args = parser.parse_args()

    fleet = load_fleet(args.fleet) if args.fleet else load_fleet()

    if args.show:
        payload = {"repos": fleet["repos"]}
        factory_cli.payload(payload)


if __name__ == "__main__":
    factory_cli.run("config", _main, expected=(FleetError,))
