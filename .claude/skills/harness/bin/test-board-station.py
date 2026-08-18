#!/usr/bin/env python3
"""board-station.py must get these right — offline, against a fake gh (FEAT-23, T-05).

Modeled on `test-gh-board.py`, its nearest sibling: same `check()` shape (PASS + two spaces +
name on success, a line beginning FAIL on failure), and the same `write_harness_json`-style
temporary-root fixture.

**THE FAKE-BINARY TRAP, and it is not optional.** `factory_gh.run_gh` finds `gh` through the
`FACTORY_GH` environment variable; `gh-sync.py` (and this tool, `board-station.py`, deliberately
mirroring it) reads `GH_SYNC_GH`... except `board-station.py` imports `gh_board` directly and
never reads `GH_SYNC_GH` itself — but the FAKE must still be wired through BOTH variables, because
a test that injects through one alone risks a future refactor routing some call through the other
and silently reaching the REAL `gh`. EVERY case here sets BOTH `FACTORY_GH` and `GH_SYNC_GH` to
the SAME fake. No case in this file may reach the real `gh` binary or the real board.

    ./test-board-station.py    -> exit 0 all pass, 1 otherwise
"""
import json
import os
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "board-station.py")

FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS  {name}")
    else:
        print(f"FAIL  {name}{(' — ' + detail) if detail else ''}")
        FAILURES.append(name)


def write_team_config(root):
    """The manifest that proves `root` is a harness project root — the established
    root-probe convention `board-station.py` walks up looking for."""
    os.makedirs(os.path.join(root, ".harness"), exist_ok=True)
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w") as f:
        f.write("org: {}\n")


def write_harness_json(root, github):
    os.makedirs(os.path.join(root, ".harness"), exist_ok=True)
    with open(os.path.join(root, ".harness", "harness.json"), "w") as f:
        json.dump({"schema_version": 1, "github": github}, f)


# A fake `gh` that logs every invocation (one line per call, argv joined on \x01 so a
# station string containing a space cannot be mistaken for a field separator) to
# $FAKE_LOG, and answers the THREE calls `gh_board.set_station` makes in sequence:
# (1) the issue -> board-item-id GraphQL lookup, (2) the field/option resolve GraphQL
# call, (3) `project item-edit`, the actual write.
FAKE_GH_OK = """#!/bin/bash
echo "$*" | tr ' ' '\\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
case "$*" in
  *"ProjectV2SingleSelectField"*)
    printf '{"data":{"repositoryOwner":{"__typename":"User","projectV2":{"id":"PVT_PROJ","field":{"id":"FIELD_STATUS","name":"Status","options":[{"id":"OPT_PLAN","name":"Plan"},{"id":"OPT_BUILDING","name":"Building"}]}}}}}\\n'
    exit 0 ;;
  *"projectItems(first: 100)"*)
    num=$(echo "$*" | grep -oE 'number=[0-9]+' | tail -1 | grep -oE '[0-9]+')
    printf '{"data":{"repository":{"issue":{"projectItems":{"totalCount":1,"nodes":[{"id":"ITEM_%s","project":{"number":3}}]}}}}}\\n' "$num"
    exit 0 ;;
  *"project item-edit"*)
    exit 0 ;;
esac
exit 0
"""

# Same board reads, but the ISSUE-ITEM lookup call returns exit-0 with a NON-JSON body —
# `factory_gh.run_gh(json_out=True)` calls `json.loads` UNGUARDED on that response, so this
# raises a bare `ValueError`, never a `gh_board.BoardError`. This is what board-station.py's
# broad `except Exception` — documented in its module docstring's EXIT CONTRACT paragraph —
# exists to catch, and nothing else in this file exercises that branch.
FAKE_GH_NON_JSON = """#!/bin/bash
echo "$*" | tr ' ' '\\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
case "$*" in
  *"projectItems(first: 100)"*)
    echo 'not json, but a clean exit 0'
    exit 0 ;;
esac
exit 0
"""

# The board write's item-id lookup finds no matching project on the item -> BoardError,
# a documented, ordinary board failure.
FAKE_GH_NOT_ON_BOARD = """#!/bin/bash
echo "$*" | tr ' ' '\\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
case "$*" in
  *"projectItems(first: 100)"*)
    printf '{"data":{"repository":{"issue":{"projectItems":{"totalCount":0,"nodes":[]}}}}}\\n'
    exit 0 ;;
esac
exit 0
"""


def install_gh(tmp, script):
    path = os.path.join(tmp, "fake-gh")
    with open(path, "w") as f:
        f.write(script)
    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
    return path


def run(tmp, args, gh_script=FAKE_GH_OK, cwd=None):
    """Fork the real script — the discipline this module's docstring pins. Returns
    (CompletedProcess, log_lines) — `log_lines` empty when no `gh` call was ever logged
    (the fake writes nothing until it is actually invoked)."""
    gh_path = install_gh(tmp, gh_script)
    log_path = os.path.join(tmp, "calls.log")
    env = dict(os.environ)
    env["FACTORY_GH"] = gh_path
    env["GH_SYNC_GH"] = gh_path
    env["FAKE_LOG"] = log_path
    r = subprocess.run(
        [sys.executable, SCRIPT] + args,
        capture_output=True, text=True, env=env, cwd=cwd or tmp,
    )
    lines = []
    if os.path.isfile(log_path):
        with open(log_path) as f:
            lines = [l for l in f.read().splitlines() if l]
    return r, lines


# ---------------- case 1: the station-write case ----------------

with tempfile.TemporaryDirectory() as tmp:
    write_team_config(tmp)
    write_harness_json(tmp, {"sync": True, "repo": "mruangutai/harness",
                              "board": {"owner": "mruangutai", "number": 3,
                                        "station_field": "Status"}})
    r, log = run(tmp, ["326", "Plan"])
    check("board-station moves the named issue to the named station",
          r.returncode == 0 and "board-station: #326 -> Plan" in r.stdout,
          f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    # THE FAKE RECORDS THE INVOCATION IT RECEIVED — asserting only the exit code would pass
    # on a tool that writes nothing at all. argv[1:3] (P-14): argv[0] is always the `gh`
    # binary itself, so a [0:2]-anchored check can never match.
    edit_calls = [l for l in log if "project\x01item-edit" in l]
    check("the field-set invocation actually carries the issue number and the station",
          len(edit_calls) == 1
          and "OPT_PLAN" in edit_calls[0]
          and "ITEM_326" in edit_calls[0],
          repr(edit_calls))

# ---------------- case 2: no board configured ----------------

with tempfile.TemporaryDirectory() as tmp:
    write_team_config(tmp)
    write_harness_json(tmp, {"sync": True, "repo": "mruangutai/harness"})
    r, log = run(tmp, ["326", "Plan"])
    check("board-station with no board configured writes nothing and exits 0",
          r.returncode == 0 and not log and r.stdout.startswith("board-station: "),
          f"rc={r.returncode} stdout={r.stdout!r} log={log}")

# ---------------- case 3: BoardError on stderr ----------------

with tempfile.TemporaryDirectory() as tmp:
    write_team_config(tmp)
    write_harness_json(tmp, {"sync": True, "repo": "mruangutai/harness",
                              "board": {"owner": "mruangutai", "number": 3,
                                        "station_field": "Status"}})
    r, log = run(tmp, ["327", "Ready"], gh_script=FAKE_GH_NOT_ON_BOARD)
    check("board-station reports a BoardError on stderr naming issue and station and exits 0",
          r.returncode == 0
          and r.stderr.startswith("board-station: ERROR - ")
          and "327" in r.stderr and "Ready" in r.stderr,
          f"rc={r.returncode} stderr={r.stderr!r}")

# ---------------- case 4: usage ----------------

with tempfile.TemporaryDirectory() as tmp:
    write_team_config(tmp)
    write_harness_json(tmp, {"sync": True, "repo": "mruangutai/harness"})
    r, log = run(tmp, ["326"])
    r2, _ = run(tmp, ["326", "Plan", "extra"])
    r3, _ = run(tmp, ["not-a-number", "Plan"])
    # "not-a-number" cannot catch this class: it fails isdigit() first. Superscript
    # two passes isdigit() and int() refuses it.
    r4, _ = run(tmp, ["\u00b2", "Plan"])
    # THE SECOND CLASS, and the worse one. int() RETURNS 2 for Arabic-Indic two, so the
    # pre-fix gate did not crash here — it moved issue 2's card. A silent write to the
    # wrong target. Drop isascii() and the traceback case above still passes; only this
    # one fails.
    r5, _ = run(tmp, ["\u0662", "Plan"])
    # THE CLASS PREDICATES CANNOT REACH. All ASCII digits, so both string tests pass;
    # int() then refuses it on CPython's 4300-digit conversion cap. This case exists to
    # pin the try/except, not the predicates — it is why the parse is caught rather
    # than enumerated.
    r6, _ = run(tmp, ["9" * 4301, "Plan"])
    check("board-station rejects a missing argument with exit 2",
          r.returncode == 2 and r2.returncode == 2 and r3.returncode == 2
          and r.stderr.startswith("board-station: "),
          f"rc1={r.returncode} rc2={r2.returncode} rc3={r3.returncode} stderr={r.stderr!r}")
    check("board-station rejects a UNICODE-digit argument with exit 2, not a traceback",
          r4.returncode == 2, f"rc4={r4.returncode} (1 means int() raised)")
    check("board-station rejects a Unicode digit int() ACCEPTS, so no card moves silently",
          r5.returncode == 2, f"rc5={r5.returncode} (0 means it moved issue 2's card)")
    check("board-station rejects an over-cap digit string with exit 2, not a traceback",
          r6.returncode == 2, f"rc6={r6.returncode} (1 means int() raised uncaught)")

# ---------------- case 5: outside a harness root ----------------

with tempfile.TemporaryDirectory() as outer:
    no_root = os.path.join(outer, "not_a_project")
    os.makedirs(no_root)
    r, log = run(outer, ["326", "Plan"], cwd=no_root)
    check("board-station outside a harness root writes nothing and exits 0",
          r.returncode == 0 and not log and r.stdout.startswith("board-station: "),
          f"rc={r.returncode} stdout={r.stdout!r} log={log}")

# ---------------- case 6: github.sync false ----------------

with tempfile.TemporaryDirectory() as tmp:
    write_team_config(tmp)
    write_harness_json(tmp, {"sync": False, "repo": "mruangutai/harness",
                              "board": {"owner": "mruangutai", "number": 3,
                                        "station_field": "Status"}})
    r, log = run(tmp, ["326", "Plan"])
    check("board-station with github.sync false writes nothing and exits 0",
          r.returncode == 0 and not log and r.stdout.startswith("board-station: "),
          f"rc={r.returncode} stdout={r.stdout!r} log={log}")

# ---------------- case 7: non-BoardError exception from set_station ----------------

with tempfile.TemporaryDirectory() as tmp:
    write_team_config(tmp)
    write_harness_json(tmp, {"sync": True, "repo": "mruangutai/harness",
                              "board": {"owner": "mruangutai", "number": 3,
                                        "station_field": "Status"}})
    r, log = run(tmp, ["326", "Plan"], gh_script=FAKE_GH_NON_JSON)
    check("board-station exits 0 when set_station raises a non-BoardError exception",
          r.returncode == 0
          and r.stderr.startswith("board-station: ERROR - ")
          and "326" in r.stderr and "Plan" in r.stderr,
          f"rc={r.returncode} stderr={r.stderr!r}")

print()
if FAILURES:
    print(f"{len(FAILURES)} FAIL")
    sys.exit(1)
print("all pass")
