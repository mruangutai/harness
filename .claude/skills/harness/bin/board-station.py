#!/usr/bin/env python3
"""board-station.py — the kickoff-time writer that moves ONE named issue to ONE named station
on `harness.json`'s configured board (FEAT-23, T-05).

WHY THIS EXISTS RATHER THAN A `gh-sync.py` SUBCOMMAND: `gh-sync.py`'s `main()` reads
`cmd, feat_dir = argv[0], argv[1]` and dies when `feat_dir` is not a directory, BEFORE any
subcommand dispatch, and derives the harness root by walking up from that feature directory. At
`/harness-plan` kickoff there is no feature directory yet — the write is against a wayfinding
ticket, not a feature's own parent card. So this is a new, small tool rather than a special case
bolted onto a file built entirely around one positional argument.

Usage: board-station.py <issue-number> <station>

`<issue-number>` is an issue of `harness.json`'s `github.repo` — the repository is resolved
IMPLICITLY from that field, never taken as a parameter here, so a source ticket living in a
different repository would silently move THIS repository's issue of the same number.

`<station>` is a plain string, never validated against a list (D-05): `gh_board.set_station`
passes it to `factory_gh.project_field_set`, which resolves the option BY NAME at runtime, so a
wrong value fails loudly at the board instead of silently against a stale local copy.

EVERY line this tool prints, on stdout or stderr, carries the "board-station: " prefix — the
environmental lines below included, matching `gh-sync.py`'s own universal prefix discipline.

EXIT CONTRACT: 2 is the ONLY non-zero exit, and it is reserved for a caller mistake — a missing
or extra argument, or an issue number that is not a positive integer. Every environmental
precondition (no harness root, no harness.json, no github block, sync off, no repo pinned, no
board configured) prints one plain line and exits 0 having written nothing. The board write
itself is wrapped in a broad `except Exception`: a `gh_board.BoardError` is the documented
failure, but `factory_gh.run_gh(json_out=True)` also calls `json.loads` UNGUARDED, so a
non-JSON exit-0 response raises `ValueError`, and `OSError` is unguarded too — any of these
reaching the top as a traceback would abort an operator's planning session, which the EXIT CONTRACT
paragraph above forbids. So every exception class from the write is reported as ONE line on stderr and
the process still exits 0 (D-02's mirror-write rule, applied here). `factory_gh.preflight()` is
never called — its callers exit non-zero, and this tool's callers must not.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gh_board  # noqa: E402

USAGE = (
    "usage: board-station.py <issue-number> <station> — <issue-number> is an issue of "
    "harness.json's github.repo (resolved implicitly; not a parameter)"
)


def out(line):
    print(f"board-station: {line}")


def err(line):
    print(f"board-station: {line}", file=sys.stderr)


def main(argv):
    if len(argv) != 2:
        err(USAGE)
        return 2
    issue_arg, station = argv
    # CATCH THE FAILURE, DO NOT ENUMERATE IT. int() refuses more inputs than any list
    # of predicates keeps up with: Unicode digit forms str.isdigit() accepts, and
    # anything past CPython's 4300-digit conversion cap. Two rounds of adding one more
    # predicate each shipped with one class still open. The ASCII test stays because it
    # catches a DIFFERENT failure — a Unicode digit int() happily PARSES, which would
    # move the wrong card silently rather than raise. Everything else int() rejects is
    # caught here, including edges nobody has met yet: 2 is this tool's only non-zero exit.
    try:
        issue_number = int(issue_arg)
    except ValueError:
        err(USAGE)
        return 2
    if not (issue_arg.isascii() and issue_arg.isdigit()) or issue_number <= 0:
        err(USAGE)
        return 2

    # DEPTH-AGNOSTIC ROOT, the established root-probe convention (same walk-up gh-sync.py
    # uses): the first ancestor of the CURRENT WORKING DIRECTORY holding the manifest,
    # `.harness/team-config.yaml`. No fixed-depth climb.
    _d = os.path.abspath(os.getcwd())
    while (not os.path.isfile(os.path.join(_d, ".harness", "team-config.yaml"))
           and _d != os.path.dirname(_d)):
        _d = os.path.dirname(_d)
    if not os.path.isfile(os.path.join(_d, ".harness", "team-config.yaml")):
        out("no harness root found above the current directory — nothing written")
        return 0
    root = _d

    # VARIABLE-FIRST FORM (test-check-plan-routes.py case_20's escape, exactly how
    # gh-sync.py's load_config reads harness.json at gh-sync.py:122-123): the path is
    # assembled into a variable on this line, and only the NEXT statement tests it.
    harness_json_path = os.path.join(root, ".harness", "harness.json")
    if not os.path.isfile(harness_json_path):
        out("no .harness/harness.json — nothing written")
        return 0
    try:
        with open(harness_json_path, encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, ValueError):
        out("harness.json is unreadable — nothing written")
        return 0
    if not isinstance(cfg, dict):
        out("harness.json is not a JSON mapping — nothing written")
        return 0

    github = cfg.get("github")
    if not isinstance(github, dict):
        out("no github block configured — nothing written")
        return 0
    if not github.get("sync"):
        out("github.sync is not enabled — nothing written")
        return 0
    repo = github.get("repo")
    if not repo or "/" not in str(repo):
        out("github.repo is not pinned — nothing written")
        return 0

    board = gh_board.load_board(root)
    if board is None:
        out("no github.board configured — nothing written")
        return 0

    try:
        gh_board.set_station(board, repo, issue_number, station)
    except Exception as exc:  # noqa: BLE001 — deliberate: see module docstring, D-02
        err(f"ERROR - #{issue_number} -> {station}: {exc}")
        return 0

    out(f"#{issue_number} -> {station}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
