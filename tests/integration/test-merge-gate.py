#!/usr/bin/env python3
"""Contract coverage for the Build-entry merge gate."""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BIN = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
GATE = os.path.join(BIN, "merge-gate.sh")
fails = 0


def check(name, condition, detail=""):
    global fails
    print(f"{'ok   ' if condition else 'FAIL '} {name}" + (f"\n      {detail}" if not condition else ""))
    fails += not condition


def fixture(feature="FEAT-9001-fixture-non-era", entry=None, repo="acme/widgets", sync=True):
    root = tempfile.mkdtemp()
    os.makedirs(os.path.join(root, ".harness"))
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w") as f:
        f.write("agents: {}\n")
    with open(os.path.join(root, ".harness", "harness.json"), "w") as f:
        json.dump({"github": {"sync": sync, "repo": repo}}, f)
    directory = os.path.join(root, ".harness", "harness", "features", feature)
    os.makedirs(directory)
    document = {"feature_id": feature, "branch": "feature/test", "github": {}}
    if entry is not None:
        document["github"]["build_entry"] = entry
    with open(os.path.join(directory, "feature.json"), "w") as f:
        json.dump(document, f)
    with open(os.path.join(directory, "plan.yaml"), "w") as f:
        f.write("status: plan\ntasks: []\n")
    subprocess.run(["git", "init", "-q", "-b", "feature/test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    subprocess.run(["git", "commit", "--allow-empty", "-qm", "fixture"], cwd=root, check=True)
    return root, directory


def gate(command, root, gh=None):
    env = dict(os.environ, HARNESS_PROJECT_DIR=root)
    if gh:
        env["GH_BIN"] = gh
    result = subprocess.run(["bash", GATE], input=json.dumps({"tool_input": {"command": command}}),
                            text=True, capture_output=True, cwd=root, env=env)
    decision = None
    reason = ""
    if result.stdout.strip():
        hook = json.loads(result.stdout)["hookSpecificOutput"]
        decision, reason = hook.get("permissionDecision"), hook.get("permissionDecisionReason", "")
    return result, decision, reason


def denial(command, **kwargs):
    root, directory = fixture(**kwargs)
    result, decision, reason = gate(command, root)
    return result, decision, reason, directory


r, d, reason, _ = denial("git merge feature/test", entry="recovery-required")
check("T-05 recovery-required denies", r.returncode == 0 and d == "deny" and "recovery-required" in reason, reason)
r, d, reason, _ = denial("git merge feature/test")
check("T-05 non-era absent build_entry denies", d == "deny" and "gh-sync.py open" in reason, reason)
r, d, reason, _ = denial("git merge feature/test", repo=None)
check("T-05 unpinned repo absent build_entry denies naming the configuration fix", d == "deny" and "NOT pinned" in reason and "open" not in reason.lower(), reason)
for entry, name in (("opened", "T-05 opened allows"), ("not-applicable", "T-05 not-applicable allows"), ("recovered-terminal", "T-05 recovered-terminal allows")):
    root, _ = fixture(entry=entry)
    r, d, _ = gate("git merge feature/test", root)
    check(name, r.returncode == 0 and d is None)
root, _ = fixture(sync=False)
r, d, _ = gate("git merge feature/test", root)
check("T-05 sync false allows", r.returncode == 0 and d is None)
root, _ = fixture()
r, d, _ = gate("git merge other", root)
check("T-05 branch matching no feature allows", r.returncode == 0 and d is None)
r, d, _ = gate("git status", root)
check("T-05 non-merge command allows", r.returncode == 0 and d is None)
root, _ = fixture()
fake_ok = os.path.join(root, "gh-ok")
with open(fake_ok, "w") as f: f.write("#!/bin/sh\necho feature/test\n")
os.chmod(fake_ok, 0o755)
r, d, _ = gate("/opt/homebrew/bin/gh pr merge 7", root, fake_ok)
check("T-05 path-prefixed gh is still detected", d == "deny")
r, d, _, _ = denial("bash -c 'git merge feature/test'")
check("T-05 bash -c wrapped merge is still detected", d == "deny")
root, _ = fixture(feature="BUG-1030-stale-anchor-write-hazard")
r, d, reason = gate("git merge feature/test", root)
check("T-05 era-exempt absent build_entry allows", d is None and "predates" in r.stderr and "open" not in r.stderr.lower(), r.stderr)
root, _ = fixture(feature="BUG-1030-stale-anchor-write-hazard", entry="recovery-required")
r, d, reason = gate("git merge feature/test", root)
check("T-05 era-exempt recovery-required allows", r.returncode == 0 and d is None
      and "predates" in r.stderr, r.stderr or reason)
root, _ = fixture()
r, d, reason = gate("gh pr merge 7", root, "/nonexistent/gh")
check("T-05 unresolvable gh falls back and denies a locally owed receipt",
      r.returncode == 0 and d == "deny" and "absent" in reason,
      f"rc={r.returncode} stderr={r.stderr!r} reason={reason!r}")
root, _ = fixture()
fake = os.path.join(root, "gh-fail")
with open(fake, "w") as f: f.write("#!/bin/sh\necho unavailable >&2\nexit 9\n")
os.chmod(fake, 0o755)
with open(os.path.join(root, ".harness", "harness", "features", "FEAT-9001-fixture-non-era", "feature.json")) as f:
    doc = json.load(f)
doc["branch"] = "other"
with open(os.path.join(root, ".harness", "harness", "features", "FEAT-9001-fixture-non-era", "feature.json"), "w") as f:
    json.dump(doc, f)
r, d, _ = gate("gh pr merge 7", root, fake)
check("T-05 gh outage with no matching feature allows", d is None and "could not verify" in r.stderr, r.stderr)
doc["branch"] = "feature/test"
with open(os.path.join(root, ".harness", "harness", "features", "FEAT-9001-fixture-non-era", "feature.json"), "w") as f:
    json.dump(doc, f)
r, d, reason = gate("gh pr merge 7", root, fake)
check("T-05 gh outage with a feature owing a receipt denies", d == "deny" and "could not verify" not in reason, reason)
root, directory = fixture()
with open(os.path.join(directory, "plan.yaml"), "w") as f:
    f.write("")
r, d, reason = gate("git merge feature/test", root)
check("T-05 empty plan fails closed", r.returncode == 0 and d == "deny"
      and "FEAT-9001-fixture-non-era" in reason, f"rc={r.returncode} reason={reason!r}")
root, directory = fixture(entry="opened")
bad_directory = os.path.join(root, ".harness", "harness", "features", "FEAT-9002-unrelated-malformed")
os.makedirs(bad_directory)
with open(os.path.join(bad_directory, "feature.json"), "w") as f:
    json.dump([], f)
r, d, reason = gate("git merge feature/test", root)
check("T-05 unrelated non-object feature record does not block healthy merge",
      r.returncode == 0 and d is None, f"rc={r.returncode} reason={reason!r}")
root, directory = fixture()
with open(os.path.join(directory, "feature.json"), "w") as f:
    json.dump([], f)
r, d, reason = gate("git merge feature/test", root)
check("T-05 unusable target record fails closed", r.returncode == 0 and d == "deny"
      and "malformed feature record" in reason, f"rc={r.returncode} reason={reason!r}")
print("ALL PASSED" if not fails else f"{fails} FAILED")
sys.exit(bool(fails))
