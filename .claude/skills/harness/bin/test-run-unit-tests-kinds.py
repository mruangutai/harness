#!/usr/bin/env python3
"""Integration tests for run-unit-tests.sh's kind cross-check (FEAT-31 T-12).

INTEGRATION because every case drives run-unit-tests.sh as a SUBPROCESS through its
--check-kinds mode. That mode exists for exactly this: the cases cost milliseconds instead
of driving the ~15s suite.

WHAT IS BEING TESTED, and why the exit status is never the proof. The check answers one
question: do the two bash arrays in run-unit-tests.sh and test_kinds.integration.detect in
harness.json AGREE? A non-zero exit cannot tell a detected mismatch from a crash, so every
red case asserts on a KIND-DRIFT line that NAMES the offending file (D-08).

Every fixture is a literal written under tempfile.mkdtemp() and removed in a finally block.
Nothing is checked in.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

BIN_DIR = os.path.dirname(os.path.realpath(__file__))
RUNNER = os.path.join(BIN_DIR, "run-unit-tests.sh")
REPO_ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.abspath(
    os.path.join(BIN_DIR, "..", "..", "..", ".."))
REAL_CONFIG = os.path.join(REPO_ROOT, ".harness", "harness.json")

PREFIX = ".claude/skills/harness/bin/"
REMOVE_ME = PREFIX + "test-check-state.py"      # in INTEGRATION_SCRIPTS, long in detect
APPEND_ME = PREFIX + "test-render-brief.py"     # a UNIT_SCRIPTS member

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))


def run_check_kinds(config_path=None):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=REPO_ROOT)
    if config_path is not None:
        env["HARNESS_JSON"] = config_path
    else:
        env.pop("HARNESS_JSON", None)
    return subprocess.run(["bash", RUNNER, "--check-kinds"], capture_output=True,
                          text=True, env=env, cwd=REPO_ROOT)


def drift_lines(r):
    """KIND-DRIFT lines across BOTH streams. Both, deliberately: which stream carries them
    is an implementation detail, and a test that watched only one would go green if they
    moved."""
    return [l for l in (r.stdout + r.stderr).splitlines() if "KIND-DRIFT" in l]


def _mutant_config(tmp, transform):
    with open(REAL_CONFIG, encoding="utf-8") as f:
        doc = json.load(f)
    original = doc["test_kinds"]["integration"]["detect"]
    doc["test_kinds"]["integration"]["detect"] = transform(original)
    path = os.path.join(tmp, "harness-mutant.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
    return path, original, doc["test_kinds"]["integration"]["detect"]


def case_1_green_on_the_real_tree():
    """GREEN ON THE REAL TREE. Exit 0 and EXACTLY ZERO KIND-DRIFT lines. The count is
    recorded because case 2 compares against it — "more than before" is the claim, and it
    needs a measured before."""
    r = run_check_kinds()
    n = len(drift_lines(r))
    check("case 1: --check-kinds on the real tree exits 0", r.returncode == 0,
          f"exit {r.returncode}: {(r.stdout + r.stderr).strip()[:240]}")
    check("case 1: and reports EXACTLY zero KIND-DRIFT lines", n == 0, f"{n} line(s)")
    # --check-kinds must run NO test. Asserted here as well as in case 5 because a mode
    # that quietly ran the suite would make every case below slow and still green.
    ran = [l for l in r.stdout.splitlines() if l.startswith(("PASS", "FAIL"))]
    check("case 1: --check-kinds ran no test", ran == [], f"{ran[:3]}")
    return n


def case_2_red_with_the_name(baseline):
    """RED, WITH THE MISMATCH NAMED. One explicit path removed from integration.detect.

    THE MUTATION IS ASSERTED APPLIED BEFORE ANYTHING RUNS. A mutation that silently failed
    to apply reports a surviving mutant that never existed, and the count comparison below
    would then be measuring two identical trees."""
    tmp = tempfile.mkdtemp()
    try:
        path, original, mutated = _mutant_config(
            tmp, lambda d: "|".join(p for p in d.split("|") if p != REMOVE_ME))
        check("case 2: the mutation changed the detect string", mutated != original,
              "detect is unchanged, so nothing was mutated")
        check("case 2: the removed path is present in the ORIGINAL", REMOVE_ME in original,
              f"{REMOVE_ME} was never in detect, so this case would prove nothing")
        check("case 2: and absent from the MUTANT", REMOVE_ME not in mutated,
              "the path survived the removal")

        r = run_check_kinds(path)
        lines = drift_lines(r)
        named = [l for l in lines if "test-check-state.py" in l]
        if r.returncode != 0 and not named:
            print("     INCONCLUSIVE — non-zero exit with no KIND-DRIFT line naming the file")
            print("     stdout:", r.stdout.strip()[:400])
            print("     stderr:", r.stderr.strip()[:400])
        check("case 2: a KIND-DRIFT line NAMES test-check-state.py", len(named) == 1,
              f"{lines}")
        check("case 2: exactly one KIND-DRIFT line, strictly more than case 1's baseline",
              len(lines) == 1 and len(lines) > baseline,
              f"{len(lines)} line(s) vs baseline {baseline}")
        check("case 2: the message says INTEGRATION_SCRIPTS, the direction of this drift",
              bool(named) and "INTEGRATION_SCRIPTS but absent" in named[0],
              f"{named}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def case_3_the_other_direction():
    """THE OTHER DIRECTION. A UNIT_SCRIPTS member APPENDED to integration.detect. This case
    is why the rule is stated both ways: a check that only looked for missing entries would
    pass case 2 and never notice a unit file claimed as integration."""
    tmp = tempfile.mkdtemp()
    try:
        path, original, mutated = _mutant_config(tmp, lambda d: d + "|" + APPEND_ME)
        check("case 3: the mutation changed the detect string", mutated != original)
        check("case 3: the appended path was absent from the ORIGINAL",
              APPEND_ME not in original,
              f"{APPEND_ME} was already in detect, so this case would prove nothing")
        check("case 3: and is present in the MUTANT", APPEND_ME in mutated)

        r = run_check_kinds(path)
        lines = drift_lines(r)
        named = [l for l in lines if "test-render-brief.py" in l]
        check("case 3: a KIND-DRIFT line NAMES test-render-brief.py", len(named) == 1,
              f"{lines}")
        check("case 3: the message says UNIT_SCRIPTS, the opposite direction",
              bool(named) and "UNIT_SCRIPTS but present" in named[0], f"{named}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def case_4_unreadable_config_is_loud():
    """THE UNREADABLE CONFIG IS LOUD, NEVER A SKIP. tests.yml runs this script as a required
    step, so a silent skip here is a green suite that verified nothing."""
    tmp = tempfile.mkdtemp()
    try:
        missing = os.path.join(tmp, "does-not-exist.json")
        r = run_check_kinds(missing)
        lines = drift_lines(r)
        check("case 4: a missing config produces a KIND-DRIFT line naming the path",
              any(missing in l for l in lines), f"{lines}")
        check("case 4: and a non-zero exit", r.returncode != 0, f"exit {r.returncode}")

        junk = os.path.join(tmp, "junk.json")
        with open(junk, "w") as f:
            f.write("not json at all\n")
        r2 = run_check_kinds(junk)
        lines2 = drift_lines(r2)
        check("case 4: an unparseable config produces a KIND-DRIFT line naming the path",
              any(junk in l for l in lines2), f"{lines2}")
        check("case 4: and a non-zero exit", r2.returncode != 0, f"exit {r2.returncode}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def case_5_parser_did_not_regress():
    """THE ARGUMENT PARSER DID NOT REGRESS. --check-kinds was added by extending a parser
    that previously rejected everything except --kind; an extension that accidentally
    started accepting anything would make --kind's own validation dead."""
    env = dict(os.environ, CLAUDE_PROJECT_DIR=REPO_ROOT)
    env.pop("HARNESS_JSON", None)
    r = subprocess.run(["bash", RUNNER, "--kind", "nonsense"], capture_output=True,
                       text=True, env=env, cwd=REPO_ROOT)
    check("case 5: --kind nonsense still exits 2", r.returncode == 2, f"exit {r.returncode}")
    check("case 5: and the message names the legal kinds",
          all(k in r.stderr for k in ("unit", "integration", "all")), r.stderr.strip()[:200])

    r2 = subprocess.run(["bash", RUNNER, "--not-a-flag"], capture_output=True, text=True,
                        env=env, cwd=REPO_ROOT)
    check("case 5: an unknown flag still exits 2 with the usage line",
          r2.returncode == 2 and "usage:" in r2.stderr,
          f"exit {r2.returncode}: {r2.stderr.strip()[:200]}")
    check("case 5: the usage line advertises --check-kinds",
          "--check-kinds" in r2.stderr, r2.stderr.strip()[:200])

    r3 = run_check_kinds()
    ran = [l for l in r3.stdout.splitlines() if re.match(r"^(PASS|FAIL)\b", l)]
    check("case 5: --check-kinds runs no test, so no PASS or FAIL line appears",
          ran == [], f"{ran[:3]}")


def main():
    baseline = case_1_green_on_the_real_tree()
    case_2_red_with_the_name(baseline)
    case_3_the_other_direction()
    case_4_unreadable_config_is_loud()
    case_5_parser_did_not_regress()

    failed = 0
    for name, ok, detail in RESULTS:
        if ok:
            print(f"ok    {name}")
        else:
            failed += 1
            print(f"FAIL  {name}")
            if detail:
                print(f"      | {detail}")
    print(f"{len(RESULTS) - failed} of {len(RESULTS)} cases passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
