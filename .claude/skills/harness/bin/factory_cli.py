"""factory_cli.py — the shared factory command-line contract (D-08).

The one place the factory's stdout/stderr/exit-code grammar is implemented. Every
other factory tool with a command-line entry calls into this module rather than
formatting its own lines, so the contract is written once instead of six times.

Contract:
  - stdout carries ONLY the machine-readable payload; every diagnostic, warning and
    error goes to stderr.
  - exit 0 success (payload on stdout); exit 1 nothing to do (not an error); exit 2
    refused (invalid config, repo not in the fleet, plan unsigned, or a guard tripped
    — nothing mutated); exit 3 lost race (another agent owns the issue — nothing
    mutated).
  - a tool NEVER exits 1 for a failure. run() traps any unhandled exception so it
    exits 2 instead of falling through to Python's default exit 1, which would read
    as nothing-to-do.

Importing this module has no side effects, and it has no command-line entry of its
own. It imports no other factory module, so nothing can import it circularly.
"""
import json
import os
import sys
import traceback

EXIT_OK = 0
EXIT_NOTHING = 1
EXIT_REFUSED = 2
EXIT_RACE = 3


def body(what, value, next_step):
    """The one place the failure-line body is constructed."""
    return f"{what}: {value} — {next_step}"


def message(tool, what, value, next_step):
    """Build the one canonical stderr grammar line.

    Never call this with an exception CLASS as `value` — value is the path, the
    repository, the issue number or the option name the operator can act on.
    """
    return f"factory: {tool}: {body(what, value, next_step)}"


def fail(tool, what, value, next_step):
    print(message(tool, what, value, next_step), file=sys.stderr)


def refuse(tool, what, value, next_step):
    fail(tool, what, value, next_step)
    sys.exit(EXIT_REFUSED)


def nothing_to_do(tool, why):
    print(f"factory: {tool}: {why}", file=sys.stderr)
    sys.exit(EXIT_NOTHING)


def lost_race(tool, what, value, next_step):
    fail(tool, what, value, next_step)
    sys.exit(EXIT_RACE)


def payload(obj):
    """Write the single stdout payload. Accepts only a dict or a list."""
    if not isinstance(obj, (dict, list)):
        raise TypeError(f"payload() accepts only a dict or a list, got {type(obj).__name__}")
    print(json.dumps(obj))


def run(tool, fn, expected=()):
    """Call fn() under the entry-point trap.

    SystemExit propagates unchanged, so a deliberate sys.exit(1) stays 1 and a
    deliberate sys.exit(3) stays 3. An exception whose type is in `expected` is
    assumed to already carry a message built with message()/body() — it is printed
    verbatim, not re-wrapped. Anything else is an unexpected failure and is trapped
    so it exits 2 instead of Python's default exit 1.
    """
    try:
        fn()
    except SystemExit:
        raise
    except expected as exc:
        print(f"factory: {tool}: {exc}", file=sys.stderr)
        sys.exit(EXIT_REFUSED)
    except BaseException as exc:
        print(
            f"factory: {tool}: unexpected failure: {type(exc).__name__}: {exc} — "
            "re-run with FACTORY_DEBUG=1 for a traceback",
            file=sys.stderr,
        )
        if os.environ.get("FACTORY_DEBUG"):
            traceback.print_exc(file=sys.stderr)
        sys.exit(EXIT_REFUSED)
