#!/usr/bin/env python3
"""Mutation proof for BUG-1290's per-repository resolution (SC-08, T-05).

This file does not add coverage of its own; test-factory-claim.py's BUG-1290 5a/5b/5c
cases already carry that. What it proves is that those cases actually DISCRIMINATE: that
they are green today and would go red if factory_claim stopped resolving features_root
per repository and fell back to one fixed segment for every candidate, the exact defect
BUG-1290 reported.

It runs the real suite in-process twice via `runpy.run_path`, unmutated then mutated, and
never spawns a subprocess or imports a test framework. The mutant is a proxy object
substituted for factory_claim's `factory_config` module attribute: it delegates every
name to the real module except `features_root`, whose wrapper DISCARDS the repo_name
argument it is called with and always resolves through one fixed owner-qualified fleet
name, "acme/harness" (segment "harness") — the same "one root for every candidate" shape
BUG-1290's now-deleted FEATURES_ROOT hardcode produced. The proxy resolves attributes at
call time, so it sits in front of the suite's own `factory_config.features_root`
monkeypatch rather than replacing it (measured in
notes/research-BUG-1290-factory-claim-repo-root-fix-c2.md).
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)

import contextlib
import io
import runpy
import sys

import factory_claim
import factory_config

SUITE_PATH = _anchor_os.path.join(_anchor_tests, "test-factory-claim.py")
CASES = ("5a", "5b", "5c")
FIXED_FLEET_NAME = "acme/harness"  # owner-qualified; segment is "harness".


class _MutantFactoryConfig:
    """Delegates every attribute to the real `factory_config` module except
    `features_root`, whose wrapper discards `repo_name` and resolves through one fixed
    fleet name instead — the post-change equivalent of the deleted FEATURES_ROOT
    hardcode. Attribute lookups on the real module happen at CALL time, so this sits in
    front of a suite-level monkeypatch of `factory_config.features_root` rather than
    bypassing it.

    The suite under test captures the tool's own stdout/stderr into strings it asserts
    against (`run_main`'s `out`/`err`), and `features_root` is reached from deep inside
    that captured call. Printing through `sys.stdout` here would land inside those
    captured strings and corrupt unrelated assertions (e.g. a JSON-payload parse), so
    the marker is written to the real process stream, `sys.__stdout__`, which no
    `contextlib.redirect_stdout` in this file or in the suite ever retargets."""

    def __init__(self, real_module):
        object.__setattr__(self, "_real", real_module)
        object.__setattr__(self, "_reached", False)

    def __getattr__(self, name):
        real = object.__getattribute__(self, "_real")
        if name != "features_root":
            return getattr(real, name)

        def _fixed_features_root(repo_name):
            if not object.__getattribute__(self, "_reached"):
                print("MUTANT ACTIVE", file=sys.__stdout__)
                object.__setattr__(self, "_reached", True)
            return real.features_root(FIXED_FLEET_NAME)

        return _fixed_features_root

    def reached(self):
        return object.__getattribute__(self, "_reached")


def _run_suite():
    """Runs test-factory-claim.py in-process via runpy, swallowing the SystemExit it
    raises at the end, and returns everything it printed to stdout."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            runpy.run_path(SUITE_PATH, run_name="__main__")
        except SystemExit:
            pass
    return buf.getvalue()


def _case_line(output, status, case_id):
    """The single line check() printed for `case_id` at `status` ("ok" or "FAIL"), or
    None if no such line exists — status and name are two independent fields of the
    same marker, so this looks for their exact concatenation, not either alone."""
    prefix = ("ok    " if status == "ok" else "FAIL  ") + f"BUG-1290 {case_id}:"
    for line in output.splitlines():
        if line.startswith(prefix):
            return line
    return None


def _baseline():
    output = _run_suite()
    missing = [c for c in CASES if _case_line(output, "ok", c) is None]
    if missing:
        for case_id in missing:
            print(f"BASELINE MISSING: {case_id}")
        print("BASELINE INCOMPLETE")
        return False
    print("BASELINE 3/3 ok")
    return True


def _mutate_and_run():
    real = factory_claim.factory_config
    mutant = _MutantFactoryConfig(real)
    factory_claim.factory_config = mutant
    try:
        output = _run_suite()
    finally:
        factory_claim.factory_config = real
    return output, mutant.reached()


def _mutation_proof():
    output, reached = _mutate_and_run()
    if not reached:
        print("MUTANT NEVER REACHED")
        print("MUTATION PROOF: INCOMPLETE")
        return False
    missing = []
    for case_id in CASES:
        line = _case_line(output, "FAIL", case_id)
        if line is None:
            missing.append(case_id)
        else:
            print(line)
    if missing:
        for case_id in missing:
            print(f"MUTATION MISSING: {case_id}")
        print("MUTATION PROOF: INCOMPLETE")
        return False
    print("MUTATION PROOF: 3/3 cases reddened")
    return True


def main():
    if not _baseline():
        sys.exit(1)
    sys.exit(0 if _mutation_proof() else 1)


if __name__ == "__main__":
    main()
