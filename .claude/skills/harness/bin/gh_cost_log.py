"""gh_cost_log.py — records every gh invocation made through factory_gh.run_gh and gh-sync.py's
gh wrapper, together with the GraphQL points it cost (FEAT-29 T-03).

EVERY COST FIGURE BELOW CARRIES ITS THREE CONDITIONS — the board, that board's item count, and
the commit it was measured at. A figure without them cannot be re-derived and therefore cannot
be shown to be wrong, which is how a 31-point figure survived nine days and had an exclusion
decision built on it (.harness/notes/grilling-graphql-cost-2026-08-10.md).

WHY: check-state.sh's INV-26 read burned 506 GraphQL points -- board 3, 486 items, commit
`e1bcdc1`, 2026-08-19 -- before T-01/T-02 made it cheap
(.harness/harness/features/FEAT-29-graphql-budget/notes/measurement-before.md). This module is
the record that would have made that burn visible as it happened instead of after the fact.

THE COVERAGE IS PARTIAL. See COVERAGE_NOTICE below — it is written into every log file this
module creates, not only into this docstring, because a comment is not in the artifact the
reader opens.

OPT-IN, DEFAULT OFF (approval amendment 5, 2026-08-19). Set HARNESS_GH_COST_LOG=1 to record.
Unset, or set to anything other than "1", records nothing. This recorder is blind to gh invoked
directly from Bash — where the ~360-point burn it was built to explain actually lived — and after
T-01/T-02 the operation it CAN see costs 5 points (board 3, 473 items, commit `8c2c24d`,
2026-08-20) instead of 506 (board 3, 486 items, commit `e1bcdc1`), so always-on bought little.

Reading the counter is `gh api rate_limit --jq .resources.graphql.used` and NOTHING else — that
exact call was measured taking three consecutive reads with graphql.used unchanged at 1057 each
time, proving it costs zero GraphQL points itself (REST, not GraphQL).

record() and measured() never raise. A broken counter read, a broken log directory, or a
disabled logger must never be able to break the gh call it is only supposed to be watching.
"""
import contextlib
import datetime
import json
import os
import subprocess

import harness_boundary

_BIN_DIR = os.path.dirname(os.path.abspath(__file__))

# The exact call this module issues to read the counter — nothing else. Also the recursion
# guard: measured() must never wrap this call with another measurement, or reading the counter
# would require reading the counter, forever.
_COUNTER_ARGV = ["api", "rate_limit", "--jq", ".resources.graphql.used"]

_MAX_ARG_LEN = 80
_VALUE_FLAGS = ("-f", "-F")

COVERAGE_NOTICE = (
    "This log records only gh invocations made through factory_gh.run_gh and gh-sync.py's own "
    "gh wrapper; a gh command typed directly into Bash by the main session or by any agent is "
    "INVISIBLE to it, so this file is not a complete account of GraphQL spend."
)


def _enabled():
    """OPT-IN, default OFF (FEAT-29 T-03, approval amendment 5, 2026-08-19). The recorder is
    blind to gh invoked directly from Bash, which is where the ~360-point burn it was built for
    actually lived, and after T-01/T-02 the operation it CAN see costs 5 points (board 3, 473
    items, `8c2c24d`) instead of 506 (board 3, 486 items, `e1bcdc1`) —
    two rate_limit forks per wrapped call now buy very little by default. Runs only under an
    explicit HARNESS_GH_COST_LOG=1."""
    return os.environ.get("HARNESS_GH_COST_LOG", "0") == "1"


def is_counter_call(argv):
    """True for the exact call this module's own counter read issues."""
    return list(argv) == _COUNTER_ARGV


def _counter_binary():
    # Same env var factory_gh.run_gh resolves its binary from, read independently here rather
    # than by importing factory_gh — factory_gh imports THIS module to wire measured() around
    # its own subprocess call, so importing it back here would be circular.
    return os.environ.get("FACTORY_GH", "gh")


def _read_counter():
    """Read the GraphQL counter. Returns an int, or None on ANY failure. Never raises — the
    counter must never be able to break the gh call it is watching."""
    try:
        r = subprocess.run(
            [_counter_binary()] + list(_COUNTER_ARGV),
            capture_output=True, text=True, stdin=subprocess.DEVNULL,
        )
        if r.returncode != 0:
            return None
        return int(r.stdout.strip())
    except Exception:
        return None


def _truncate(value):
    if isinstance(value, str) and len(value) > _MAX_ARG_LEN:
        return value[:_MAX_ARG_LEN] + "..."
    return value


def _sanitize_argv(argv):
    """Return argv with any value following -f/-F longer than 80 chars truncated, so a query
    body does not bloat the recorded line."""
    out = []
    prev = None
    for a in argv:
        out.append(_truncate(a) if prev in _VALUE_FLAGS else a)
        prev = a
    return out


def _log_path():
    """Resolved INSIDE record(), never cached at import — harness_boundary.resolve_root() reads
    its override at CALL time, so caching this at import would freeze whatever the environment
    happened to hold then. The override is named once, in that module's own docstring, and is
    deliberately not spelled again here: the invariant that keeps the retired name gone counts
    it in every tracked source file."""
    root = harness_boundary.resolve_root(_BIN_DIR)
    day = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    return os.path.join(root, ".harness", "logs", f"gh-cost-{day}.jsonl")


def record(argv, graphql_before, graphql_after, returncode):
    """Append ONE line of JSON to today's gh-cost log. A failed invocation (non-zero
    returncode) IS recorded, with its real cost — skipping it would hide the exact incident
    shape this module exists to explain. Never raises."""
    if not _enabled():
        return
    try:
        cost = None
        if isinstance(graphql_before, int) and isinstance(graphql_after, int):
            cost = graphql_after - graphql_before
        line = {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
            "argv": _sanitize_argv(list(argv)),
            "before": graphql_before,
            "after": graphql_after,
            "cost": cost,
            "rc": returncode,
        }
        path = _log_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        is_new = not os.path.exists(path)
        with open(path, "a", encoding="utf-8") as f:
            if is_new:
                f.write(json.dumps({"coverage": COVERAGE_NOTICE}) + "\n")
            f.write(json.dumps(line) + "\n")
    except Exception:
        # The counter, and this log, must never be able to break a harness command.
        return


class _Measurement:
    """Handed to the caller by measured() so it can report the real invocation's returncode
    before the context manager's finally block records it."""

    __slots__ = ("argv", "returncode")

    def __init__(self, argv):
        self.argv = argv
        self.returncode = None


@contextlib.contextmanager
def measured(argv):
    """Wrap a gh invocation: reads the GraphQL counter before and after, and calls record()
    with the caller-reported returncode. The caller sets `.returncode` on the yielded object
    once the real call has completed. Never wraps the counter's own rate_limit call — that is
    the explicit argv guard against recursion."""
    argv = list(argv)
    m = _Measurement(argv)
    if not _enabled() or is_counter_call(argv):
        yield m
        return
    before = _read_counter()
    try:
        yield m
    finally:
        after = _read_counter()
        rc = m.returncode if m.returncode is not None else -1
        record(argv, before, after, rc)
