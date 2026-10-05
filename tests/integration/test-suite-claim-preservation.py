#!/usr/bin/env python3
"""BUG-1898 SC-01 (F-QA-01): the validate-digest suite goes red on a hook that releases by
persona.

The suite fires a copy of the validator whose registry `release` ignores the runtime id: the
persona-wide selector BUG-1898 removed. The suite's own exact-release checks must report
failures. A green suite here would mean a persona-wide release could come back unnoticed,
because the suite's fires land in isolated registries this wrapper cannot watch directly.

The other half of SC-01 (a real full suite run leaves every unrelated live claim
byte-identical) runs inside test-validate-digest.py's own full run, so the suite is not paid
for twice. Its own file, so the suite is never run inside itself. Cleanup removes the mutant
copy.
"""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"

SUITE = ROOT / "tests" / "integration" / "test-validate-digest.py"
# The mutant pass reads only the [bug1898] lines, so it runs only that group.
EXACT_RELEASE_GROUP = "run_bug1898_exact_release_cases"
EXACT_RELEASE_FAIL = "FAIL  [bug1898] "
# The two checks a persona-wide release must redden: two orchestrators share the persona and
# feature, so a release that ignores the runtime id matches both, refuses, and the settled
# parent keeps its claim. Any other [bug1898] red would be a different fault.
PERSONA_RELEASE_REDS = {
    "after the child settles the identical yield passes",
    "and releases only the parent",
}
PERSONA_RELEASE = '''

_bug1898_exact_release = release


def release(root, agent=None, feature=None, claim_id=None, agent_id=None, job_id=None):
    """Mutant: the pre-BUG-1898 persona selector; the runtime id is ignored."""
    return _bug1898_exact_release(root, agent=agent, feature=feature, claim_id=claim_id,
                                  job_id=job_id)
'''
failures = []


def check(name, condition, detail=""):
    print(("PASS" if condition else "FAIL"), name, detail if not condition else "")
    if not condition:
        failures.append(name)


def run_suite(env=None, *args):
    run = subprocess.run([sys.executable, str(SUITE), *args], cwd=ROOT, capture_output=True,
                         text=True, timeout=1800, env=env)
    return run.returncode, run.stdout + run.stderr


def mutant_run():
    copy = Path(tempfile.mkdtemp(prefix="vd-persona-release-")) / "bin"
    try:
        shutil.copytree(BIN, copy, ignore=shutil.ignore_patterns("__pycache__"))
        with open(copy / "inflight_registry.py", "a", encoding="utf-8") as handle:
            handle.write(PERSONA_RELEASE)
        code, output = run_suite(dict(os.environ,
                                      VALIDATE_DIGEST_BIN=str(copy / "validate-digest.py")),
                                 "--only", EXACT_RELEASE_GROUP)
        reddened = {line[len(EXACT_RELEASE_FAIL):] for line in output.splitlines()
                    if line.startswith(EXACT_RELEASE_FAIL)}
        check("a persona-wide release reddens exactly the parent-settlement checks",
              code != 0 and reddened == PERSONA_RELEASE_REDS,
              "exit %d, reddened %s" % (code, sorted(reddened)))
    finally:
        shutil.rmtree(copy.parent, ignore_errors=True)


def main():
    mutant_run()
    print("%d failure(s)" % len(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
