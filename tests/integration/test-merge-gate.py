#!/usr/bin/env python3
"""Contract coverage for the Build-entry merge gate."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BIN = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
GATE = os.path.join(BIN, "merge-gate.py")
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
        json.dump({"github": {"sync": sync, "repo": repo, "board": None}}, f)
    directory = os.path.join(root, ".harness", "harness", "features", feature)
    os.makedirs(directory)
    document = {"feature_id": feature, "branch": "feature/test", "github": {}}
    if entry is not None:
        document["github"]["build_entry"] = entry
        if repo:
            document["github"]["repo"] = repo
    with open(os.path.join(directory, "feature.json"), "w") as f:
        json.dump(document, f)
    with open(os.path.join(directory, "plan.yaml"), "w") as f:
        f.write(
            "status: plan\n"
            "tasks:\n"
            "  - id: T-01\n"
            "    title: Fixture task\n"
            "    change_type: test\n"
            "    execution_mode: main-session-direct\n"
            "    files: [fixture.py]\n"
            "    status: ready\n"
            "    verify: python3 test.py\n"
            "    intent: Exercise the merge gate fixture.\n")
    subprocess.run(["git", "init", "-q", "-b", "feature/test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    subprocess.run(["git", "commit", "--allow-empty", "-qm", "fixture"], cwd=root, check=True)
    return root, directory


def gate(command, root, gh=None):
    env = dict(os.environ, HARNESS_PROJECT_DIR=root)
    if gh:
        env["GH_BIN"] = gh
    result = subprocess.run([GATE], input=json.dumps({"tool_input": {"command": command}}),
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


for provenance in (None, "elsewhere/wrong"):
    root, directory = fixture(entry="opened")
    record = os.path.join(directory, "feature.json")
    with open(record) as source:
        document = json.load(source)
    document["github"].update(parent=12)
    if provenance is None:
        document["github"].pop("repo")
    else:
        document["github"]["repo"] = provenance
    with open(record, "w") as target:
        json.dump(document, target)
    r, d, reason = gate("git merge feature/test", root)
    if provenance is None:
        check("an unbound legacy mapping is proven by the owner binding that created it",
              r.returncode == 0 and d is None, f"decision={d} reason={reason}")
    else:
        check("opened is not proof of ownership for a wrong-repository mirror",
              d == "deny" and "recover-mirror" in reason and "--previous-repo" in reason, reason)

root, directory = fixture(entry="opened", sync=False)
record = os.path.join(directory, "feature.json")
with open(record) as source:
    document = json.load(source)
document["factory"] = {"repo": "unknown/product", "issues": {"T-01": 51}}
with open(record, "w") as target:
    json.dump(document, target)
r, d, reason = gate("git merge feature/test", root)
check("owner sync-off and factory claims cannot bypass an invalid authoritative binding",
      d == "deny", f"decision={d} reason={reason} stderr={r.stderr}")

r, d, reason, _ = denial("git merge feature/test", entry="recovery-required")
check("T-05 recovery-required denies", r.returncode == 0 and d == "deny"
      and "needs its GitHub mirror recovery completed" in reason, reason)
r, d, reason, _ = denial("git merge feature/test")
check("T-05 non-era absent build_entry denies naming feature and re-run command",
      d == "deny" and "FEAT-9001-fixture-non-era" in reason and "gh-sync.py open" in reason, reason)
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
# FEAT-71: the receipt rule is uniform. An absent or recovery-required build_entry denies for
# EVERY feature id: synthetic ones, plus every feature-id-shaped string feature_schema itself
# holds as module data — read from the module, never named here, so a reintroduced per-feature
# exemption table is probed without this file naming any real feature.
sys.path.insert(0, BIN)
import re  # noqa: E402
import feature_schema  # noqa: E402
_held = set()
for _value in vars(feature_schema).values():
    _members = _value.keys() if isinstance(_value, dict) else (
        _value if isinstance(_value, (set, frozenset, list, tuple)) else ())
    _held.update(m for m in _members
                 if isinstance(m, str) and re.match(r"^(FEAT|BUG|PR)-[0-9]+", m))
allowed = []
for feature in ["BUG-9-x", "PR-9-fixture"] + sorted(_held):
    for entry in (None, "recovery-required"):
        root, _ = fixture(feature=feature, entry=entry)
        r, d, reason = gate("git merge feature/test", root)
        if d != "deny" or feature not in reason:
            allowed.append((feature, entry, d))
        shutil.rmtree(root, ignore_errors=True)
check("T-05 absent or recovery-required build_entry denies for every feature id",
      allowed == [], f"{len(allowed)} not denied, e.g. {allowed[:3]}")
root, _ = fixture()
r, d, reason = gate("gh pr merge 7", root, "/nonexistent/gh")
check("T-05 unresolvable gh falls back and denies a locally owed receipt",
      r.returncode == 0 and d == "deny" and "FEAT-9001-fixture-non-era" in reason
      and "gh-sync.py open" in reason,
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
bad_directory = os.path.join(root, ".harness", "harness", "features", "FEAT-9002-unrelated-malformed")
os.makedirs(bad_directory)
with open(os.path.join(bad_directory, "feature.json"), "w") as f:
    json.dump([], f)
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
root, directory = fixture(entry="opened")
with open(os.path.join(directory, "feature.json")) as f:
    doc = json.load(f)
doc["branch"] = "other"
with open(os.path.join(directory, "feature.json"), "w") as f:
    json.dump(doc, f)
bad_directory = os.path.join(root, ".harness", "harness", "features", "FEAT-9002-unrelated-malformed")
os.makedirs(bad_directory)
with open(os.path.join(bad_directory, "feature.json"), "w") as f:
    json.dump([], f)
r, d, reason = gate("git merge feature/test", root)
check("T-05 no-record branch ignores unrelated malformed record",
      r.returncode == 0 and d is None, f"rc={r.returncode} reason={reason!r}")
root, directory = fixture()
duplicate_id = "FEAT-9002-fixture-duplicate"
duplicate_directory = os.path.join(root, ".harness", "harness", "features", duplicate_id)
os.makedirs(duplicate_directory)
with open(os.path.join(duplicate_directory, "feature.json"), "w") as f:
    json.dump({"feature_id": duplicate_id, "branch": "feature/test",
               "github": {"build_entry": "opened"}}, f)
r, d, reason = gate("git merge feature/test", root)
_, repeated_d, repeated_reason = gate("git merge feature/test", root)
check("T-05 duplicate valid records claiming the branch deny naming both",
      r.returncode == 0 and d == repeated_d == "deny"
      and "FEAT-9001-fixture-non-era" in reason and duplicate_id in reason
      and "gh-sync.py" not in reason and reason == repeated_reason,
      f"rc={r.returncode} reason={reason!r} repeated={repeated_reason!r}")
root, directory = fixture(entry="opened")
bad_directory = os.path.join(root, ".harness", "harness", "features", "FEAT-9002-unrelated-malformed")
os.makedirs(bad_directory)
with open(os.path.join(bad_directory, "feature.json"), "w") as f:
    json.dump([], f)
r, d, reason = gate("git merge feature/test", root)
check("T-05 single owner plus unrelated malformed record still allows",
      r.returncode == 0 and d is None, f"rc={r.returncode} reason={reason!r}")
root, directory = fixture(entry="opened")
for name, content in (
    ("FEAT-9002-unreadable", None),
    ("FEAT-9003-malformed", "{"),
    ("FEAT-9004-non-object", []),
    ("FEAT-9005-different-branch", {"feature_id": "FEAT-9005-different-branch",
                                     "branch": "other", "github": {}}),
):
    noise_directory = os.path.join(root, ".harness", "harness", "features", name)
    os.makedirs(noise_directory)
    noise_file = os.path.join(noise_directory, "feature.json")
    if content is None:
        with open(noise_file, "w") as f:
            json.dump({}, f)
        os.chmod(noise_file, 0)
    else:
        with open(noise_file, "w") as f:
            if isinstance(content, str):
                f.write(content)
            else:
                json.dump(content, f)
r, d, reason = gate("git merge feature/test", root)
check("T-05 single owner ignores unreadable malformed non-object and different-branch noise",
      r.returncode == 0 and d is None, f"rc={r.returncode} reason={reason!r}")
for command, name in (
    (f"git -C {root} merge feature/test", "T-05 git -C global flag merge is still detected"),
    ("git -c core.pager=cat merge feature/test", "T-05 git -c config global flag merge is still detected"),
    (f"git --work-tree {root} merge feature/test", "T-05 git --work-tree global flag merge is still detected"),
    ("git merge --no-ff feature/test", "T-05 git --no-ff merge is still detected"),
    ("git merge --squash feature/test", "T-05 git --squash merge is still detected"),
    ("git merge -m message feature/test", "T-05 git -m merge is still detected"),
):
    root, _ = fixture()
    r, d, reason = gate(command, root)
    check(name, r.returncode == 0 and d == "deny", f"rc={r.returncode} reason={reason!r}")
for command, name in (
    ("git merge -F /tmp/message feature/test", "T-05 merge -F detached value denies"),
    ("git merge --cleanup strip feature/test", "T-05 merge --cleanup detached value denies"),
    ("git --attr-source HEAD merge --no-ff feature/test", "T-05 global --attr-source before merge is still detected"),
    ("git merge --file /tmp/message", "T-05 merge with no identifiable ref denies"),
):
    root, _ = fixture()
    r, d, reason = gate(command, root)
    check(name, r.returncode == 0 and d == "deny", f"rc={r.returncode} reason={reason!r}")
for command, name in (
    ("git merge --abort", "T-05 merge --abort on an owing branch allows"),
    ("git merge --continue", "T-05 merge --continue on an owing branch allows"),
    ("git merge --quit", "T-05 merge --quit on an owing branch allows"),
):
    root, _ = fixture()
    r, d, reason = gate(command, root)
    check(name, r.returncode == 0 and d is None, f"rc={r.returncode} reason={reason!r}")

root, _ = fixture()
raw_payload = (
    '{"tool_input":{"command":"git status"},'
    '"tool_input":{"command":"git merge feature/test"}}')
raw_env = dict(os.environ, HARNESS_PROJECT_DIR=root)
raw_result = subprocess.run(
    [GATE], input=raw_payload, text=True, capture_output=True, cwd=root, env=raw_env)
if raw_result.stdout.strip():
    check("duplicate hook-payload keys are rejected before merge policy evaluation",
          False, raw_result.stdout)

root, _ = fixture()
with open(os.path.join(root, ".harness", "harness.json"), "w") as stream:
    stream.write(
        '{"github":{"sync":false},"github":{"sync":true,"repo":"acme/widgets"}}')
r, d, reason = gate("git merge feature/test", root)
if d is not None:
    check("duplicate harness.json keys disable merge policy rather than choosing one",
          False, f"rc={r.returncode} reason={reason!r}")

root, directory = fixture()
with open(os.path.join(directory, "feature.json"), "w") as stream:
    stream.write(
        '{"feature_id":"FEAT-9001-fixture-non-era","branch":"other",'
        '"branch":"feature/test","github":{}}')
r, d, reason = gate("git merge feature/test", root)
if d is not None:
    check("duplicate feature.json keys cannot claim a merge branch",
          False, f"rc={r.returncode} reason={reason!r}")
# FEAT-65: the two "could not evaluate … receipt" broad catches are gone; an unexpected defect
# reaches hook_guard's CLOSED form — BLOCKED on stderr, exit 2, no decision JSON — so the
# denial verdict is kept while the defect is named. Process control escapes the guard.
def _feat65_fire(root, sibling, override):
    mbin = os.path.join(tempfile.mkdtemp(), "bin")
    shutil.copytree(BIN, mbin)
    with open(os.path.join(mbin, sibling), "a", encoding="utf-8") as handle:
        handle.write("\n\n" + override)
    return subprocess.run([os.path.join(mbin, "merge-gate.py")],
                          input=json.dumps({"tool_input": {"command": "git merge feature/test"}}),
                          text=True, capture_output=True, cwd=root,
                          env=dict(os.environ, HARNESS_PROJECT_DIR=root))


root, _ = fixture()
sig = "def recovery_command_for(feat_dir, feature_doc=None, bound_repo=None, *, replacement=False):\n"
r = _feat65_fire(root, "feature_schema.py", sig + "    raise RuntimeError('FEAT-65 injected')\n")
check("FEAT-65: a receipt-evaluation defect is BLOCKED by the closed guard and named",
      r.returncode == 2 and r.stdout == "" and "RuntimeError: FEAT-65 injected" in r.stderr,
      f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
r = _feat65_fire(root, "feature_schema.py", sig + "    raise KeyboardInterrupt()\n")
check("FEAT-65: KeyboardInterrupt escapes the guard",
      r.returncode != 0 and "KeyboardInterrupt" in r.stderr and "failed internally" not in r.stderr,
      f"rc={r.returncode} stderr={r.stderr[-200:]!r}")
r = _feat65_fire(root, "feature_schema.py", sig + "    raise SystemExit(7)\n")
check("FEAT-65: a deliberate SystemExit keeps its own exit code",
      r.returncode == 7 and "failed internally" not in r.stderr,
      f"rc={r.returncode} stderr={r.stderr[-200:]!r}")

print("ALL PASSED" if not fails else f"{fails} FAILED")
sys.exit(bool(fails))
