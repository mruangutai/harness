#!/usr/bin/env python3
"""BUG-1898 SC-01 (F-QA-01): a real validate-digest suite run releases no unrelated live
claim, and the suite itself goes red on a hook that releases by persona.

Two runs of the real suite:
  pinned  — one live stranger per governed persona is seeded in this checkout's registry,
            each under this run's own feature and runtime id (so concurrent runs never
            collide). The suite must pass and every stranger must stay byte-identical.
  mutant  — the suite fires a copy of the validator whose registry `release` ignores the
            runtime id: the persona-wide selector BUG-1898 removed. The suite's own
            exact-release checks must report failures. A green suite here would mean a
            persona-wide release could come back unnoticed, because the suite's fires land
            in isolated registries this wrapper cannot watch directly.
Its own file, so the suite is never run inside itself. Cleanup releases exactly the seeded
claims and removes the mutant copy.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(BIN))
import inflight_registry  # noqa: E402

SUITE = ROOT / "tests" / "integration" / "test-validate-digest.py"
FEATURE = "BUG-1898-suite-sentinel-%d" % os.getpid()
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


def rows():
    path = ROOT / inflight_registry.REGISTRY_REL
    return json.loads(path.read_text(encoding="utf-8")).get("claims", []) if path.exists() else []


def governed_personas():
    return sorted(name[:-3] for name in os.listdir(ROOT / ".omp" / "agents")
                  if name.startswith("harness-") and name.endswith(".md"))


def seed_sentinels():
    """One live claim per governed persona, each bound to this run's own runtime id."""
    claim_ids = []
    for persona in governed_personas():
        entry = inflight_registry.claim_with_receipt(
            str(ROOT), persona, "suite-sentinel", str(ROOT), feature=FEATURE,
            supervisor_pid=os.getpid())
        inflight_registry.attach_runtime_identity(
            str(ROOT), persona, FEATURE, agent_id="Suite%d.%s" % (os.getpid(), persona),
            claim_id=entry["claim_id"], parent_agent_id="Suite%d" % os.getpid())
        claim_ids.append(entry["claim_id"])
    return [row for row in rows() if row.get("claim_id") in claim_ids]


def run_suite(env=None):
    run = subprocess.run([sys.executable, str(SUITE)], cwd=ROOT, capture_output=True,
                         text=True, timeout=1800, env=env)
    return run.returncode, run.stdout + run.stderr


def pinned_run():
    sentinels = seed_sentinels()
    ids = {row["claim_id"] for row in sentinels}
    try:
        check("one live sentinel per governed persona was seeded",
              len(sentinels) == len(governed_personas()), len(sentinels))
        code, output = run_suite()
        kept = [row for row in rows() if row.get("claim_id") in ids]
        check("the pinned validate-digest suite run passed", code == 0,
              output.strip().splitlines()[-3:])
        check("every unrelated live claim is byte-identical after the suite",
              kept == sentinels,
              sorted({r["agent"] for r in sentinels} - {r["agent"] for r in kept}))
    finally:
        for claim_id in ids:
            inflight_registry.release(str(ROOT), feature=FEATURE, claim_id=claim_id)


def mutant_run():
    copy = Path(tempfile.mkdtemp(prefix="vd-persona-release-")) / "bin"
    try:
        shutil.copytree(BIN, copy, ignore=shutil.ignore_patterns("__pycache__"))
        with open(copy / "inflight_registry.py", "a", encoding="utf-8") as handle:
            handle.write(PERSONA_RELEASE)
        code, output = run_suite(dict(os.environ,
                                      VALIDATE_DIGEST_BIN=str(copy / "validate-digest.py")))
        reddened = {line[len(EXACT_RELEASE_FAIL):] for line in output.splitlines()
                    if line.startswith(EXACT_RELEASE_FAIL)}
        check("a persona-wide release reddens exactly the parent-settlement checks",
              code != 0 and reddened == PERSONA_RELEASE_REDS,
              "exit %d, reddened %s" % (code, sorted(reddened)))
    finally:
        shutil.rmtree(copy.parent, ignore_errors=True)


def main():
    pinned_run()
    mutant_run()
    print("%d failure(s)" % len(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
