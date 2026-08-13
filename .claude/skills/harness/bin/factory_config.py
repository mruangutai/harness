"""factory_config.py — the only reader of .harness/factory/fleet.yaml (SC-08).

Every other factory tool takes its repository and board from this module and never from the
working directory. That matters most for factory_workspace.py and factory_land.py, which
operate a CHECKOUT OF ANOTHER REPOSITORY: run from inside it, a relative fleet.yaml path would
resolve against the target repo, not the factory's own — so FLEET_PATH here is always absolute,
never derived from the current directory.

ROOT RESOLUTION, THREE TIERS — the same rule check-plan-routes.py's _resolve_root and
run-unit-tests.sh's header comment already standardise on, copied here rather than re-derived:
prefer CLAUDE_PROJECT_DIR when it is set AND `docs/harness/SPEC.md` is readable under it;
otherwise derive the root from this file's own location, walking up out of the bin directory.
`docs/harness/SPEC.md` is the probe, never `bin/` or a script file: no mechanism copies the skill
directory (scripts, no docs) to `$HOME/.claude/skills` any more, and the probe stays a docs path
because the derived root must be a full checkout of this repository, which a bare skills tree is
not — probing for the bin directory or for a script would re-accept that tree and read a fleet
declaration that is not this checkout's own.
A discarded CLAUDE_PROJECT_DIR is announced on stderr, never swapped in silence.

Importing this module has no side effects beyond resolving that root and computing FLEET_PATH:
no fleet file is read, nothing is written, and no GitHub call is made until a caller asks.
"""
import argparse
import json
import os
import sys

import factory_cli
import harness_yaml

_BIN_DIR = os.path.dirname(os.path.abspath(__file__))
_PROBE = os.path.join("docs", "harness", "SPEC.md")

_STATION_KEYS = ("ready", "building", "review")


def harness_root():
    """Return the absolute root of this harness checkout. See the module docstring for why."""
    derived = os.path.abspath(os.path.join(_BIN_DIR, "..", "..", "..", ".."))
    asked = os.environ.get("CLAUDE_PROJECT_DIR") or ""
    if asked and os.access(os.path.join(asked, _PROBE), os.R_OK):
        return asked
    if asked:
        print(
            f"factory_config: CLAUDE_PROJECT_DIR={asked!r} has no readable {_PROBE} — "
            f"IGNORING it and using {derived}.",
            file=sys.stderr,
        )
    return derived


FLEET_PATH = os.path.join(harness_root(), ".harness", "factory", "fleet.yaml")


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


def _validate_board(board, where, path):
    """Validate one repos entry's own board mapping (where=f"repos[{name}]"; there is no
    fleet-level board any more — FEAT-16 T-08). Raises FleetError naming the offending field,
    key names prefixed by `where`: "repos[owner/name].board", "...board.owner",
    "...board.number", "...board.station_field", "...board.stations"."""
    key_base = f"{where}.board"
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
    if not isinstance(number, int) or isinstance(number, bool):
        raise FleetError(
            "fleet key invalid", f"{key_base}.number",
            f"set it to the Projects v2 board number in {path}",
        )
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
            "set exactly ready, building and review, each a non-empty option name, "
            f"in {path}",
        )


def load_fleet(path=FLEET_PATH):
    """Load and validate a fleet declaration. Raises FleetError naming the file and the
    offending key on every one of the malformed-fleet shapes this loader rejects — including a
    leftover top-level `board` key (the board is per-repository now, FEAT-16 T-08 — an unknown
    top-level key would otherwise be accepted silently, which would recreate the very
    inherit-a-board-nobody-chose silence this feature removes) and a repos[] entry that declares
    no board of its own. Every repos entry MUST carry its own board mapping, validated by
    _validate_board."""
    data = harness_yaml.load_file(path)
    _require_mapping(data, path)

    if data.get("schema") != "factory-fleet/1":
        raise FleetError(
            "fleet schema invalid", "schema", f"set schema: factory-fleet/1 in {path}"
        )

    if "board" in data:
        raise FleetError(
            "fleet key invalid", "board",
            f"the board is per-repository now — move it under each repos entry as "
            f"repos[].board in {path}",
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
        if not entry.get("default_branch"):
            raise FleetError(
                "fleet repo entry invalid", f"repos[{name}].default_branch",
                f"set a non-empty default_branch for {name} in {path}",
            )
        if "board" not in entry:
            raise FleetError(
                "fleet key invalid", f"repos[{name}].board",
                f"give {name} its own board: {{...}} block with owner, number, "
                f"station_field and stations in {path}",
            )
        _validate_board(entry["board"], f"repos[{name}]", path)

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


def board_for(fleet, repo_name):
    """Return the repos entry's own board mapping — there is no fleet-level board any more
    (FEAT-16 T-08). Raises FleetError when the repository is not in the fleet, by delegating to
    repo_entry."""
    entry = repo_entry(fleet, repo_name)
    return entry["board"]


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
