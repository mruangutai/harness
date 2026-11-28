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

`<station>` is one of the six MANDATED station names, lowercase, and is validated against
`factory_config.MANDATED_STATIONS` before any board call (FEAT-41 T-02, reversing D-05). The
board's COLUMN is then derived from it by `factory_config.station_column` inside
`github.board.set_station` — the one place a capitalised station name is produced — and the option is
still resolved BY NAME at the board, so a board missing that column still fails loudly there.
What changed is that a station outside the six is now this tool's own refusal, naming the six,
rather than a value passed through to GitHub.

EVERY line this tool prints, on stdout or stderr, carries the "board-station: " prefix — the
environmental lines below included, matching `gh-sync.py`'s own universal prefix discipline.

EXIT CONTRACT, scoped to what code can hold: 2 means EITHER a caller mistake — a missing or
extra argument, an issue number that is not a positive integer, or a CLOSED issue named for any
station other than `done` (#2639: a closed issue's card belongs at done) — OR an unusable board
declaration (FEAT-24 T-04): `github.board` absent, present but not a mapping, or malformed in
any field `factory_config.validate_board` checks. Both are refusals a human must fix, so they
share one exit code and one stream: for the board case, one line on stderr, `str(exc)`
verbatim, already carrying the offending key and the next step. An issue whose state cannot be
read is a board failure, reported like the write's own (D-02 below) and written nowhere.
Outside that scope the interpreter still owns the exit: a closed stdout ends in 120 at
shutdown flush, which no guard in this file can prevent and none pretends to. The remaining
environmental preconditions — no harness root, no harness.json, no github block, sync off, no
repo pinned, or `github.board`
declared as an EXPLICIT null — still print one plain line and exit 0 having written nothing;
an explicit null is a project's own declaration that it has no board, never the same state as
a misconfiguration. The board write itself is wrapped in a broad `except Exception`: a
`github.board.BoardError` is the documented failure, but `github.transport.run_gh(json_out=True)` also
calls `json.loads` UNGUARDED, so a non-JSON exit-0 response raises `ValueError`, and `OSError`
is unguarded too — any of these reaching the top as a traceback would abort an operator's
planning session, which the EXIT CONTRACT paragraph above forbids. So every exception class
from the write is reported as ONE line on stderr and the process still exits 0 (D-02's
mirror-write rule, applied here — this is a STATION WRITE failure, not an unusable
declaration, and the two exit differently on purpose).

FEAT-64 supersedes the "broad `except Exception`" sentence above: `github.transport.run_gh` now
converts its own `OSError` and non-JSON exit-0 bodies into `github.transport.GhError`, so the
write's whole failure surface is `github.board.BoardError` + `github.transport.GhError`, and that is
what `main` catches. The ONE-line-on-stderr, exit-0 outcome for those is unchanged; an
exception of any other class is a programming defect and propagates as itself. `github.transport.preflight()` is never
called — its callers exit non-zero, and this tool's callers must not.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import artifact_accessors  # noqa: E402
import factory_config  # noqa: E402
import github.issues  # noqa: E402
import github.transport  # noqa: E402
import github.board  # noqa: E402

USAGE = (
    "usage: board-station.py <issue-number> <station> — <issue-number> is an issue of "
    "harness.json's github.repo (resolved implicitly; not a parameter)"
)


def out(line):
    print(f"board-station: {line}")


def err(line):
    print(f"board-station: {line}", file=sys.stderr)


def _issue_number(issue_arg):
    """The positive ASCII issue number `issue_arg` names, or None."""
    # CATCH THE FAILURE, DO NOT ENUMERATE IT. int() refuses more inputs than any list
    # of predicates keeps up with: Unicode digit forms str.isdigit() accepts, and
    # anything past CPython's 4300-digit conversion cap. Two rounds of adding one more
    # predicate each shipped with one class still open. The ASCII test stays because it
    # catches a DIFFERENT failure — a Unicode digit int() happily PARSES, which would
    # move the wrong card silently rather than raise. Everything else int() rejects is
    # caught here, including edges nobody has met yet: for a command-line argument, 2 is
    # this tool's only non-zero exit.
    #
    # THE TWO CONJUNCTS READ DIFFERENT VARIABLES AND MUST KEEP DOING SO. isascii() and
    # isdigit() read the ORIGINAL STRING; only the positivity test reads the parsed
    # number. Merge them onto the parsed value — the tidier-looking form — and a
    # Unicode digit int() accepts sails through, moving the wrong card at exit 0. That
    # variant was built and measured; the Arabic-Indic case below is what pins this.
    try:
        issue_number = int(issue_arg)
    except ValueError:
        return None
    if not (issue_arg.isascii() and issue_arg.isdigit()) or issue_number <= 0:
        return None
    return issue_number


def _harness_root():
    """The harness root above the working directory, or None."""
    # DEPTH-AGNOSTIC ROOT, the established root-probe convention (same walk-up gh-sync.py
    # uses): the first ancestor of the CURRENT WORKING DIRECTORY holding the manifest,
    # `.harness/team-config.yaml`. No fixed-depth climb.
    _d = os.path.abspath(os.getcwd())
    while (not os.path.isfile(os.path.join(_d, ".harness", "team-config.yaml"))
           and _d != os.path.dirname(_d)):
        _d = os.path.dirname(_d)
    if not os.path.isfile(os.path.join(_d, ".harness", "team-config.yaml")):
        return None
    return _d


def _github(root):
    """(the github block, None), or (None, exit code) once the outcome is already reported."""
    # VARIABLE-FIRST FORM (test-check-plan-routes.py case_20's escape): the path is assembled
    # into a variable on this line, and only the NEXT statement reads it. A missing or invalid
    # config is refused with its diagnosis (FEAT-2297) — never "nothing written".
    harness_json_path = os.path.join(root, ".harness", "harness.json")
    try:
        gh_config = artifact_accessors.load_harness_json(harness_json_path)["github"]
    except artifact_accessors.ArtifactAccessError as exc:
        err(f"harness.json could not be read — nothing written: {exc}")
        return None, 2
    if not gh_config["sync"]:
        out("github.sync is not enabled — nothing written")
        return None, 0
    return gh_config, None


def _board(root):
    """(the board declaration, None), or (None, exit code) once the outcome is reported."""
    try:
        board = github.board.load_board(root)
    except artifact_accessors.FleetError as exc:
        # An unusable board declaration is a caller-mistake-class refusal (D-01, D-07),
        # not an environmental precondition — str(exc) is printed VERBATIM, not composed,
        # because it already carries the offending key and the next step from
        # factory_cli.body(what, value, next_step).
        err(str(exc))
        return None, 2
    if board is None:
        out("no github.board configured — nothing written")
        return None, 0
    return board, None


def _station_refusal(board, station):
    """Exit 2, reported, for a station outside the board's declaration; else None."""
    # VALIDATED AGAINST THE BOARD'S OWN DECLARATION, IMMEDIATELY BEFORE THE WRITE (FEAT-41 T-02,
    # reversing D-05). D-05's reasoning was that resolving the option BY NAME at the board makes
    # a wrong value fail loudly there rather than silently against a stale local copy. That still
    # holds for the board's COLUMNS, but the station vocabulary is no longer a local copy of
    # anything — it is mandated in one place — and set_station now derives the column through
    # factory_config.station_column, which raises FleetError on an unknown station. Refusing here
    # turns that into this tool's own exit-2 refusal, naming the six.
    #
    # CALLED AFTER THE ENVIRONMENTAL NO-OPS, NOT AT ARGUMENT-PARSE TIME, AND THE ORDER IS
    # LOAD-BEARING: every environmental no-op — no harness root, sync off, no board — exits 0
    # having written nothing (a missing or invalid harness.json is a refusal, FEAT-2297), and that
    # contract must not become an exit 2 just because the station argument was also wrong. A
    # refusal is only owed when a write was actually about to happen.
    if station not in factory_config.station_names(board):
        err(f"{station!r} is not a station — expected one of: "
            + ", ".join(factory_config.station_names(board)))
        return 2
    return None


def _closed_refusal(repo, issue_number, station):
    """An exit code, reported, when the card must not move because of the issue's state;
    else None."""
    # A CLOSED ISSUE'S CARD BELONGS AT DONE (#2639). The FEAT-2516 intake looped this tool over
    # nine backlog issues, one already closed by an unrelated PR, and pulled that closed card
    # from Done back to Plan, where it sat until a later ship audit flagged it. A closed issue
    # named for any other station is a caller mistake: exit 2, nothing written, so a loop sees
    # it. Moving a closed issue TO done stays allowed. An unreadable state is a board failure
    # like the write's own (D-02): one ERROR line, exit 0, and the card stays where it was.
    try:
        state = github.issues.issue_view(repo, issue_number, ["state"]).get("state")
    except github.transport.GhError as exc:
        err(f"ERROR - #{issue_number} -> {station}: the issue's state could not be read, so "
            f"nothing was written: {exc}")
        return 0
    if state == "CLOSED" and station != "done":
        err(f"#{issue_number} is closed, so its card belongs at 'done'; refusing to move it to "
            f"{station!r} — nothing written")
        return 2
    return None


def _refusal(board, repo, issue_number, station):
    """The station check, then the issue-state check: the first exit code owed, else None."""
    code = _station_refusal(board, station)
    return code if code is not None else _closed_refusal(repo, issue_number, station)


def _write(board, repo, issue_number, station):
    try:
        github.board.set_station(board, repo, issue_number, station)
    except (github.board.BoardError, github.transport.GhError) as exc:  # see module docstring, D-02
        err(f"ERROR - #{issue_number} -> {station}: {exc}")
        return 0
    out(f"#{issue_number} -> {station}")
    return 0


def main(argv):
    if len(argv) != 2:
        err(USAGE)
        return 2
    issue_arg, station = argv
    issue_number = _issue_number(issue_arg)
    if issue_number is None:
        err(USAGE)
        return 2
    root = _harness_root()
    if root is None:
        out("no harness root found above the current directory — nothing written")
        return 0
    gh_config, code = _github(root)
    if gh_config is None:
        return code
    board, code = _board(root)
    if board is None:
        return code
    code = _refusal(board, gh_config["repo"], issue_number, station)
    if code is not None:
        return code
    return _write(board, gh_config["repo"], issue_number, station)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
