#!/usr/bin/env python3
"""board-station.py must get these right — offline, against a fake gh (FEAT-23, T-05).

Modeled on `tests/unit/test-gh-board.py`, its nearest sibling: the shared `check_support.Checks`
shape (PASS + one space + name on success, a line beginning FAIL on failure), and the same
`write_harness_json`-style temporary-root fixture.

**ONE BINARY OVERRIDE: `FACTORY_GH`.** `board-station.py` imports `gh_board`, whose every call goes
through `factory_gh`, which reads `FACTORY_GH` at call time. Every case builds its environment with
`tests/offline_gh_support.offline_gh_env`: FACTORY_GH names the fake, every inherited `GH_*`
variable is dropped, and a sentinel `gh` heads PATH. `assert_sentinel_unused` then proves no case
reached the default binary, the real board or the network.

    ./test-board-station.py    -> exit 0 all pass, 1 otherwise
"""
from integration_support import BIN
import contextlib  # noqa: E402
import os  # noqa: E402
import stat  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402

from check_support import Checks  # noqa: E402
from harness_config_support import write_config  # noqa: E402
from offline_gh_support import assert_sentinel_unused, offline_gh_env  # noqa: E402

BIN_DIR = str(BIN)
SCRIPT = os.path.join(BIN_DIR, "board-station.py")

C = Checks()
check = C.check


def write_team_config(root):
    """The manifest that proves `root` is a harness project root — the established
    root-probe convention `board-station.py` walks up looking for."""
    os.makedirs(os.path.join(root, ".harness"), exist_ok=True)
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w") as f:
        f.write("org: {}\n")


def write_harness_json(root, github):
    write_config(os.path.join(root, ".harness", "harness.json"), {"github": github})


_DEFAULT_BOARD = object()  # project() writes BOARD; board=None writes an explicit null


@contextlib.contextmanager
def project(sync=True, board=_DEFAULT_BOARD, with_board=True):
    """A temporary harness root with team-config.yaml and a github block. with_board=False
    omits the board key entirely (distinct from board=None, an explicit null)."""
    github = {"sync": sync, "repo": REPO}
    if with_board:
        github["board"] = BOARD if board is _DEFAULT_BOARD else board
    with tempfile.TemporaryDirectory() as tmp:
        write_team_config(tmp)
        write_harness_json(tmp, github)
        yield tmp


REPO = "acme/widgets"
# Board number 3 matches the project number FAKE_GH_OK reports for the issue's item.
BOARD = {"owner": "implentio", "number": 3, "station_field": "Status",
         "stations": ["backlog", "plan", "ready", "building", "review", "done"]}


# A fake `gh` that logs every invocation (one line per call, argv joined on \x01 so a
# station string containing a space cannot be mistaken for a field separator) to
# $FAKE_LOG, and answers board-station's issue-state read (#2639; $FAKE_ISSUE_STATE, default
# OPEN) and the THREE calls `gh_board.set_station` makes in sequence:
# (1) the issue -> board-item-id GraphQL lookup, (2) the field/option resolve GraphQL
# call, (3) `project item-edit`, the actual write.
LOG_LINE = """echo "$*" | tr ' ' '\\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
"""


def fake_gh(*arms):
    """A fake gh: log the argv, then answer from the given `case` arms; anything else exits 0."""
    return '#!/bin/bash\n' + LOG_LINE + 'case "$*" in\n' + ''.join(arms) + 'esac\nexit 0\n'


ISSUE_STATE_CASE = """  *"issue view"*)
    printf '{"state":"%s"}\\n' "${FAKE_ISSUE_STATE:-OPEN}"
    exit 0 ;;
"""
FAKE_GH_OK = fake_gh(ISSUE_STATE_CASE, """  *"ProjectV2SingleSelectField"*)
    printf '{"data":{"repositoryOwner":{"__typename":"User","projectV2":{"id":"PVT_PROJ","field":{"id":"FIELD_STATUS","name":"Status","options":[{"id":"OPT_PLAN","name":"Plan"},{"id":"OPT_BUILDING","name":"Building"},{"id":"OPT_DONE","name":"Done"}]}}}}}\\n'
    exit 0 ;;
  *"projectItems(first: 100)"*)
    num=$(echo "$*" | grep -oE 'number=[0-9]+' | tail -1 | grep -oE '[0-9]+')
    printf '{"data":{"repository":{"issue":{"projectItems":{"totalCount":1,"nodes":[{"id":"ITEM_%s","project":{"number":3}}]}}}}}\\n' "$num"
    exit 0 ;;
  *"project item-edit"*)
    exit 0 ;;
""")

# Same board reads, but the ISSUE-ITEM lookup call returns exit-0 with a NON-JSON body —
# `factory_gh.run_gh(json_out=True)` calls `json.loads` UNGUARDED on that response, so this
# raises a bare `ValueError`, never a `gh_board.BoardError`. This is what board-station.py's
# broad `except Exception` — documented in its module docstring's EXIT CONTRACT paragraph —
# exists to catch, and nothing else in this file exercises that branch.
FAKE_GH_NON_JSON = fake_gh(ISSUE_STATE_CASE, """  *"projectItems(first: 100)"*)
    echo 'not json, but a clean exit 0'
    exit 0 ;;
""")

# The issue has no item on the project, so set_station adds it (#2181). Here the add itself
# fails with a nonzero gh exit, which is BoardError: a documented, ordinary board failure.
FAKE_GH_NOT_ON_BOARD_ADD_FAILS = fake_gh(ISSUE_STATE_CASE, """  *"projectItems(first: 100)"*)
    printf '{"data":{"repository":{"issue":{"projectItems":{"totalCount":0,"nodes":[]}}}}}\\n'
    exit 0 ;;
  *"project item-add"*)
    echo "simulated item-add failure" >&2
    exit 1 ;;
""")

# The issue-state read itself fails (#2639): the card must stay where it is.
FAKE_GH_STATE_FAILS = fake_gh("""  *"issue view"*)
    echo "simulated issue view failure" >&2
    exit 1 ;;
""")


def install_gh(tmp, script):
    path = os.path.join(tmp, "fake-gh")
    with open(path, "w") as f:
        f.write(script)
    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
    return path


def run(tmp, args, gh_script=FAKE_GH_OK, cwd=None, extra_env=None, entry=SCRIPT):
    """Fork the real script — the discipline this module's docstring pins. Returns
    (CompletedProcess, log_lines) — `log_lines` empty when no `gh` call was ever logged
    (the fake writes nothing until it is actually invoked)."""
    gh_path = install_gh(tmp, gh_script)
    log_path = os.path.join(tmp, "calls.log")
    env, sentinel_log = offline_gh_env(gh_path, tmp)
    env["FAKE_LOG"] = log_path
    env.update(extra_env or {})
    if os.path.exists(log_path):  # one run's calls only, when a case reuses its tmp
        os.remove(log_path)
    r = subprocess.run(
        [sys.executable, entry] + args,
        capture_output=True, text=True, env=env, cwd=cwd or tmp,
    )
    _check_offline(sentinel_log)
    lines = []
    if os.path.isfile(log_path):
        with open(log_path) as f:
            lines = [l for l in f.read().splitlines() if l]
    return r, lines


def _check_offline(sentinel_log):
    """Record a FAIL when the default-binary sentinel ran; silent otherwise."""
    try:
        assert_sentinel_unused(sentinel_log)
    except AssertionError as exc:
        check("no case dispatches the default gh binary", False, str(exc))


# ---------------- case 1: the station-write case ----------------

with project() as tmp:
    r, log = run(tmp, ["326", "plan"])
    check("board-station moves the named issue to the named station",
          r.returncode == 0 and "board-station: #326 -> plan" in r.stdout,
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

# ---------------- case 2: an explicit null board ----------------

with project(board=None) as tmp:
    r, log = run(tmp, ["326", "plan"])
    check("an explicitly null board still exits 0 having written nothing",
          r.returncode == 0 and not log and r.stdout.startswith("board-station: "),
          f"rc={r.returncode} stdout={r.stdout!r} log={log}")

# ---------------- case 3: BoardError on stderr ----------------

with project() as tmp:
    r, log = run(tmp, ["327", "ready"], gh_script=FAKE_GH_NOT_ON_BOARD_ADD_FAILS)
    check("board-station reports a failed item-add as a BoardError on stderr naming issue and "
          "station, and exits 0",
          r.returncode == 0
          and r.stderr.startswith("board-station: ERROR - ")
          and "327" in r.stderr and "ready" in r.stderr
          and any("item-add" in line for line in log),
          f"rc={r.returncode} stderr={r.stderr!r} log={log}")

# ---------------- case 4: usage ----------------

with project(with_board=False) as tmp:
    r, log = run(tmp, ["326"])
    r2, _ = run(tmp, ["326", "plan", "extra"])
    r3, _ = run(tmp, ["not-a-number", "plan"])
    # "not-a-number" cannot catch this class: it fails isdigit() first. Superscript
    # two passes isdigit() and int() refuses it.
    r4, _ = run(tmp, ["\u00b2", "plan"])
    # THE SECOND CLASS, and the worse one. int() RETURNS 2 for Arabic-Indic two, so the
    # pre-fix gate did not crash here — it moved issue 2's card. A silent write to the
    # wrong target. Drop isascii() and the traceback case above still passes; only this
    # one fails.
    r5, _ = run(tmp, ["\u0662", "plan"])
    # THE CLASS PREDICATES CANNOT REACH. All ASCII digits, so both string tests pass;
    # int() then refuses it on CPython's 4300-digit conversion cap. This case exists to
    # pin the try/except, not the predicates — it is why the parse is caught rather
    # than enumerated.
    r6, _ = run(tmp, ["9" * 4301, "plan"])
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
    r, log = run(outer, ["326", "plan"], cwd=no_root)
    check("board-station outside a harness root writes nothing and exits 0",
          r.returncode == 0 and not log and r.stdout.startswith("board-station: "),
          f"rc={r.returncode} stdout={r.stdout!r} log={log}")

# ---------------- case 6: github.sync false ----------------

with project(sync=False) as tmp:
    r, log = run(tmp, ["326", "plan"])
    check("board-station with github.sync false writes nothing and exits 0",
          r.returncode == 0 and not log and r.stdout.startswith("board-station: "),
          f"rc={r.returncode} stdout={r.stdout!r} log={log}")

# ---------------- case 7: a non-JSON gh body from set_station ----------------
# FEAT-64: this used to be titled "non-BoardError exception" and pinned the broad catch. The
# shape is a gh body that does not decode; run_gh raises factory_gh.GhError for it (T-01), which
# is the typed class main catches beside gh_board.BoardError. Same exit 0, same ERROR line.

with project() as tmp:
    r, log = run(tmp, ["326", "plan"], gh_script=FAKE_GH_NON_JSON)
    check("board-station exits 0 when set_station's gh returns a body that does not decode (GhError)",
          r.returncode == 0
          and r.stderr.startswith("board-station: ERROR - ")
          and "326" in r.stderr and "plan" in r.stderr,
          f"rc={r.returncode} stderr={r.stderr!r}")

# ---------------- case 7b (FEAT-64): an unrelated defect inside the write ESCAPES ----------
# The module docstring's D-02 ruling covers board failures, not programming defects: a
# RuntimeError raised inside set_station is neither BoardError nor GhError and must surface
# as itself (non-zero, traceback) rather than as `ERROR - … exit 0`.
with project() as tmp:
    shim = os.path.join(tmp, "shim.py")
    with open(shim, "w") as f:
        f.write("import sys, runpy\n"
                f"sys.path.insert(0, {BIN_DIR!r})\n"
                "import gh_board\n"
                "def boom(*a, **k): raise RuntimeError('unrelated defect')\n"
                "gh_board.set_station = boom\n"
                "sys.argv = ['board-station.py'] + sys.argv[1:]\n"
                f"runpy.run_path({SCRIPT!r}, run_name='__main__')\n")
    r, _ = run(tmp, ["326", "plan"], entry=shim, extra_env={"HARNESS_PROJECT_DIR": tmp})
    check("FEAT-64: an unrelated RuntimeError inside set_station escapes (non-zero, not ERROR/exit 0)",
          r.returncode != 0 and "RuntimeError" in r.stderr and not r.stderr.startswith("board-station: ERROR - "),
          f"rc={r.returncode} stderr={r.stderr[-300:]!r}")

# ---------------- case 8: the station is validated against the six (FEAT-41 T-02) ----------
# D-05 used to let ANY string through to the board. It is now refused here, and these cases pin
# both halves of that: what is refused, and — critically — that the refusal does NOT displace the
# environmental exit-0 no-ops that come before it.

with project() as tmp:
    # A CAPITALISED STATION IS REFUSED. This is the likeliest live mistake — the operator reads
    # "Plan" off the board and types it back — and before FEAT-41 T-02 it was passed through to
    # GitHub, where it happened to work, which is exactly how a case boundary erodes.
    r, log = run(tmp, ["326", "Plan"])
    check("board-station refuses a CAPITALISED station, exit 2, nothing written",
          r.returncode == 2 and not log and "is not a station" in r.stderr,
          f"rc={r.returncode} stderr={r.stderr!r} log={log}")
    check("board-station's refusal NAMES all six stations so the operator can act on it",
          all(st in r.stderr
              for st in ("backlog", "plan", "ready", "building", "review", "done")),
          r.stderr)
    # `abandoned` is the trap the mandate exists to close: it is a legal feature.json status but
    # NOT a station, and it names no board column.
    r, log = run(tmp, ["326", "abandoned"])
    check("board-station refuses 'abandoned' — a real status, but not a station",
          r.returncode == 2 and not log and "is not a station" in r.stderr,
          f"rc={r.returncode} stderr={r.stderr!r} log={log}")

with project(sync=False) as tmp:
    # ORDERING, PINNED: sync is off, so this exits 0 having written nothing EVEN THOUGH the
    # station is also invalid. A refusal is owed only when a write was about to happen; moving the
    # validation up to argument-parse time breaks this and it is the reason the check sits after
    # the board load.
    r, log = run(tmp, ["326", "Plan"])
    check("an invalid station does NOT override the sync-off exit-0 no-op",
          r.returncode == 0 and not log and "nothing written" in r.stdout,
          f"rc={r.returncode} stdout={r.stdout!r} log={log}")

# ---------------- case 9: a closed issue's card stays at done (#2639) ----------------
# The FEAT-2516 intake looped board-station over nine backlog issues, one already closed by an
# unrelated PR, and pulled that closed card from Done back to Plan, where it sat unnoticed.

with project() as tmp:
    r, log = run(tmp, ["2519", "plan"], extra_env={"FAKE_ISSUE_STATE": "CLOSED"})
    check("#2639: a CLOSED issue named for 'plan' is refused with exit 2 and its card is not moved",
          r.returncode == 2
          and not any("item-edit" in l or "projectItems" in l for l in log)
          and "#2519" in r.stderr and "closed" in r.stderr and "'done'" in r.stderr,
          f"rc={r.returncode} stderr={r.stderr!r} log={log}")
    r, log = run(tmp, ["2519", "done"], extra_env={"FAKE_ISSUE_STATE": "CLOSED"})
    check("#2639: a CLOSED issue may still be moved to 'done'",
          r.returncode == 0 and "board-station: #2519 -> done" in r.stdout
          and sum("item-edit" in l for l in log) == 1,
          f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r} log={log}")
    r, log = run(tmp, ["326", "plan"], extra_env={"FAKE_ISSUE_STATE": "OPEN"})
    check("#2639: an OPEN issue still moves to 'plan'",
          r.returncode == 0 and sum("item-edit" in l for l in log) == 1,
          f"rc={r.returncode} stderr={r.stderr!r} log={log}")

with project() as tmp:
    r, log = run(tmp, ["326", "plan"], gh_script=FAKE_GH_STATE_FAILS)
    check("#2639: an unreadable issue state writes nothing and reports ERROR on stderr, exit 0 (D-02)",
          r.returncode == 0
          and r.stderr.startswith("board-station: ERROR - ")
          and "326" in r.stderr and "plan" in r.stderr
          and not any("item-edit" in l or "projectItems" in l for l in log),
          f"rc={r.returncode} stderr={r.stderr!r} log={log}")

sys.exit(C.report())
