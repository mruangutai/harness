#!/usr/bin/env python3
"""FEAT-2397 / issue #2194: the manual session-accessor probe's offline logic.

The probe (tests/manual/probe-omp-session-accessor.py) is a credentialled host check and never
runs here. This file imports its helpers and drives them with synthetic observation rows, so it
proves the probe's classification and acceptance logic, not the host's wiring (SC-11, not SC-10).

Two properties are held apart on purpose:

  - IDENTITY: a session is a nested task child or a flat main because of its session-file path,
    through the probe's one `is_nested` helper. `usageDefined` and the usage numbers never decide
    it, so a child with defined usage (#2194, omp >= 18.0.11) is still a child.
  - MEASUREMENT: a child's usage is accepted only as finite numbers for tokens, contextWindow and
    percent. bool, absent, null, NaN, infinities and strings are rejected.

Changing one must not move the other, and both are exercised table by table.
"""
import importlib.util
import inspect
import sys

from unit_support import ROOT
from check_support import Checks

PROBE_PATH = ROOT / "tests/manual/probe-omp-session-accessor.py"

spec = importlib.util.spec_from_file_location("probe_omp_session_accessor", PROBE_PATH)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

C = Checks()
check = C.check

ABSENT = object()
CHILD = "/tmp/s/2026-11-22T10-00-00-000Z_0a1b2c3d-4e5f/Pong.jsonl"
MAIN = "/tmp/s/2026-11-22T10-00-00-000Z_0a1b2c3d-4e5f.jsonl"
NUMBERS = {"tokens": 1234, "contextWindow": 200000, "percent": 0.617}


def row(session, path, usage=NUMBERS, usage_defined=None):
    """One probe observation. usageDefined defaults to the honest diagnostic but may lie."""
    observed = {"session": session, "probed": {"getSessionFile": path}}
    if usage is not ABSENT:
        observed["usage"] = usage
    observed["usageDefined"] = (usage is not ABSENT) if usage_defined is None else usage_defined
    return observed


def with_tokens(tokens):
    usage = dict(NUMBERS)
    if tokens is ABSENT:
        del usage["tokens"]
    else:
        usage["tokens"] = tokens
    return usage


# (label, getSessionFile value, is_nested, is_flat_main)
IDENTITY_CASES = (
    ("nested task child transcript", CHILD, True, False),
    ("flat main transcript", MAIN, False, True),
    ("empty string", "", False, False),
    ("None", None, False, False),
    ("non-string", 42, False, False),
    ("tryCall 'undefined'", "undefined", False, False),
    ("tryCall 'null'", "null", False, False),
    ("tryCall threw", "THREW: TypeError: boom", False, False),
    ("tryCall no-target", "no-target", False, False),
    ("relative nested-looking path", "s/2026-11-22T10-00-00-000Z_0a1b/Pong.jsonl", False, False),
    ("relative flat path", "s/main.jsonl", False, False),
    ("nested dir, wrong extension", "/tmp/s/2026-11-22T10-00-00-000Z_0a1b/Pong.json", False, False),
    ("flat, wrong extension", "/tmp/s/main.txt", False, False),
    ("bare .jsonl name", "/tmp/s/.jsonl", False, False),
    ("trailing slash", "/tmp/s/main.jsonl/", False, False),
)


def test_identity_table():
    for label, path, nested, flat in IDENTITY_CASES:
        got = (probe.is_nested(path), probe.is_flat_main(path))
        check(f"identity: {label}", got == (nested, flat), (path, got))


# (label, observation row, expected session_file)
SESSION_FILE_CASES = (
    ("string path", {"probed": {"getSessionFile": CHILD}}, CHILD),
    ("no probed", {}, ""),
    ("probed is null", {"probed": None}, ""),
    ("getSessionFile missing", {"probed": {}}, ""),
    ("non-string not stringified", {"probed": {"getSessionFile": 5}}, ""),
)


def test_session_file_table():
    for label, observed, expected in SESSION_FILE_CASES:
        got = probe.session_file(observed)
        check(f"session_file: {label}", got == expected, got)


# (label, tokens value, accepted)
TOKEN_CASES = (
    ("int", 1234, True),
    ("zero", 0, True),
    ("float", 12.5, True),
    ("bool True", True, False),
    ("bool False", False, False),
    ("null", None, False),
    ("absent", ABSENT, False),
    ("NaN", float("nan"), False),
    ("+inf", float("inf"), False),
    ("-inf", float("-inf"), False),
    ("numeric string", "1234", False),
    ("list", [1234], False),
)

# (label, usage value, accepted): contextWindow, percent and the object itself
USAGE_CASES = (
    ("all finite", NUMBERS, True),
    ("usage null", None, False),
    ("usage absent", ABSENT, False),
    ("usage a string", "{\"tokens\": 1}", False),
    ("contextWindow string", {**NUMBERS, "contextWindow": "200000"}, False),
    ("contextWindow absent", {"tokens": 1, "percent": 0.1}, False),
    ("percent NaN", {**NUMBERS, "percent": float("nan")}, False),
    ("percent bool", {**NUMBERS, "percent": True}, False),
)


def test_measurement_tables():
    for label, tokens, accepted in TOKEN_CASES:
        numbers = probe.usage_numbers(row("c", CHILD, with_tokens(tokens)))
        check(f"measurement: tokens {label}", (numbers is not None) == accepted, numbers)
    for label, usage, accepted in USAGE_CASES:
        numbers = probe.usage_numbers(row("c", CHILD, usage))
        check(f"measurement: {label}", (numbers is not None) == accepted, numbers)
    numbers = probe.usage_numbers(row("c", CHILD))
    check("measurement: the actual numbers are returned unchanged", numbers == NUMBERS, numbers)


def test_tokens_never_reclassify():
    """Every token value, and a lying usageDefined, leaves identity exactly where the path put it."""
    for label, tokens, _ in TOKEN_CASES:
        for defined in (True, False):
            child = row("c", CHILD, with_tokens(tokens), usage_defined=defined)
            main = row("m", MAIN, with_tokens(tokens), usage_defined=defined)
            got = (probe.is_nested(probe.session_file(child)), probe.is_flat_main(probe.session_file(main)))
            check(f"independence: tokens {label}, usageDefined={defined}", got == (True, True), got)


# (label, rows, expected outcome of case3..case6)
SCENARIOS = (
    ("#2194: nested numeric child + flat numeric main",
     [row("c", CHILD), row("m", MAIN)], (True, True, True, True)),
    ("usageDefined lies on both rows; identity holds",
     [row("c", CHILD, usage_defined=False), row("m", MAIN, usage_defined=False)], (True, True, True, True)),
    ("child usage undefined",
     [row("c", CHILD, ABSENT), row("m", MAIN)], (True, False, True, False)),
    ("child tokens NaN",
     [row("c", CHILD, with_tokens(float("nan"))), row("m", MAIN)], (True, False, True, False)),
    ("child tokens bool",
     [row("c", CHILD, with_tokens(True)), row("m", MAIN)], (True, False, True, False)),
    ("main missing is a failure, not optional",
     [row("c", CHILD)], (True, True, False, False)),
    ("child missing",
     [row("m", MAIN)], (False, False, True, False)),
    ("child path malformed",
     [row("c", "undefined"), row("m", MAIN)], (False, False, True, False)),
    ("child reported a flat path",
     [row("c", "/tmp/s/child.jsonl"), row("m", MAIN)], (False, False, True, False)),
    ("child and main share one session id",
     [row("x", CHILD), row("x", MAIN)], (True, True, True, False)),
    ("no observations",
     [], (False, False, False, False)),
)


def outcome(rows):
    return tuple(ok for _, ok, _ in probe.observation_checks(rows))


def test_scenarios():
    for label, rows, expected in SCENARIOS:
        got = outcome(rows)
        check(f"scenario: {label}", got == expected, got)
    names = [name.split(":")[0] for name, _, _ in probe.observation_checks([])]
    check("scenario: the checks are case3..case6 in order", names == ["case3", "case4", "case5", "case6"], names)


def test_one_pattern_no_usage_identity():
    source = inspect.getsource(probe)
    check("structure: the probe compiles exactly one session-file pattern",
          source.count("re.compile(") == 1, source.count("re.compile("))
    check("structure: the nested pattern is the module-level constant is_nested uses",
          "NESTED_SESSION_FILE" in inspect.getsource(probe.is_nested))
    for helper in (probe.observation_checks, probe.is_nested, probe.is_flat_main):
        check(f"structure: {helper.__name__} never reads usageDefined",
              "usageDefined" not in inspect.getsource(helper))


def main():
    test_identity_table()
    test_session_file_table()
    test_measurement_tables()
    test_tokens_never_reclassify()
    test_scenarios()
    test_one_pattern_no_usage_identity()
    return C.report()


if __name__ == "__main__":
    sys.exit(main())
