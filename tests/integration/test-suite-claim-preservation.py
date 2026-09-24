#!/usr/bin/env python3
"""BUG-1898 SC-01 (F-QA-01): one real validate-digest suite run leaves an unrelated live claim
byte-identical.

The suite fires the SubagentStop hook hundreds of times from this checkout. Before BUG-1898 a
return that named no exact identity was released by persona, so a suite run released a live
stranger holding the same persona. This seeds such a stranger — a live harness-qa claim bound
to its own runtime id, under a feature no case uses — in this checkout's own registry, runs
the suite, and requires the row unchanged. Its own file, so the suite is never run inside
itself. Cleanup releases exactly the seeded claim and nothing else.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".claude" / "skills" / "harness" / "bin"))
import inflight_registry  # noqa: E402

SUITE = ROOT / "tests" / "integration" / "test-validate-digest.py"
SENTINEL_FEATURE = "BUG-1898-suite-sentinel"
SENTINEL_ID = "Suite.Sentinel"
failures = []


def check(name, condition, detail=""):
    print(("PASS" if condition else "FAIL"), name, detail if not condition else "")
    if not condition:
        failures.append(name)


def rows():
    path = ROOT / inflight_registry.REGISTRY_REL
    return json.loads(path.read_text(encoding="utf-8")).get("claims", []) if path.exists() else []


def seed_sentinel():
    entry = inflight_registry.claim_with_receipt(
        str(ROOT), "harness-qa", "suite-sentinel", str(ROOT), feature=SENTINEL_FEATURE,
        supervisor_pid=os.getpid())
    inflight_registry.attach_runtime_identity(
        str(ROOT), "harness-qa", SENTINEL_FEATURE, agent_id=SENTINEL_ID,
        claim_id=entry["claim_id"], parent_agent_id="Suite")
    return next(row for row in rows() if row.get("claim_id") == entry["claim_id"])


def main():
    sentinel = seed_sentinel()
    try:
        run = subprocess.run([sys.executable, str(SUITE)], cwd=ROOT, capture_output=True,
                             text=True, timeout=1800)
        kept = [row for row in rows() if row.get("claim_id") == sentinel["claim_id"]]
        tail = (run.stdout + run.stderr).strip().splitlines()[-3:]
        check("the validate-digest suite run passed", run.returncode == 0, tail)
        check("the unrelated live claim is byte-identical after the suite", kept == [sentinel],
              kept)
    finally:
        inflight_registry.release(str(ROOT), feature=SENTINEL_FEATURE,
                                  claim_id=sentinel["claim_id"])
    print("%d failure(s)" % len(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
