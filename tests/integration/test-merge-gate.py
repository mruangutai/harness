#!/usr/bin/env python3
"""Contract coverage for the Build-entry merge gate."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness_config_support import build_config  # noqa: E402

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
    config = build_config({"github": {"sync": sync, "repo": repo or "acme/widgets"}})
    config["github"]["repo"] = repo  # repo=None with sync on is a deliberate schema violation
    with open(os.path.join(root, ".harness", "harness.json"), "w") as f:
        json.dump(config, f)
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


def gate(command, root, gh=None, env_extra=None):
    env = dict(os.environ, HARNESS_PROJECT_DIR=root, **(env_extra or {}))
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


# FEAT-2337 (DEC-100): merge-gate.py is a narrow gate. This is the applicability its `merge_ref`
# decides, (command, is a guarded merge). test-omp-native-gate-runtime.py reads it as a literal and
# checks the extension's port (`narrowGateApplies`) against it, so every entry stays a plain pair.
APPLICABILITY_CORPUS = [
    ("git merge feature/test", True),
    ("git merge", True),
    ("git merge --no-ff feature/test", True),
    ("git merge -m 'release --abort' feature/test", True),
    ("git merge -F /tmp/message feature/test", True),
    ("git merge feature/test --abort", True),
    ("git -C /repo merge feature/test", True),
    ("git -c core.pager=cat merge feature/test", True),
    ("git --git-dir=/repo/.git --no-pager merge feature/test", True),
    ("git --attr-source HEAD merge feature/test", True),
    ("/usr/bin/git merge feature/test", True),
    ('git "merge" feature/test', True),
    ("cd /repo && git merge feature/test", True),
    ("echo git merge feature/test", True),
    ("gh pr merge 12 --squash", True),
    ("/opt/homebrew/bin/gh pr merge 12", True),
    ("true; gh pr merge --auto", True),
    ("bash -c 'git merge feature/test'", True),
    ('sh -c "gh pr merge 12 --squash"', True),
    ('eval "git -C /repo merge feature/test"', True),
    ("grep -rn 'git merge' docs/", True),
    ('bash -c "sh -c \'bash -c \\"git merge feature/test\\"\'"', True),
    ('git merge feature/test "unclosed', True),
    ("git merge --abort", False),
    ("git merge --continue", False),
    ("git merge --quit", False),
    ("git merge -s ours --abort", False),
    ("git -C /repo merge --abort", False),
    ("bash -c 'git merge --abort'", False),
    # Four nested `bash -c` layers: past the gate's nesting depth of three.
    ('bash -c "bash -c \\"bash -c \\\\\\"bash -c \\\\\\\\\\\\\\"git merge feature/test'
     '\\\\\\\\\\\\\\"\\\\\\"\\""', False),
    ("echo merge", False),
    ('echo "merge', False),
    ("rg merge src/", False),
    ("git status", False),
    ("git log --grep merge", False),
    ("git mergetool", False),
    ("git merge-base main HEAD", False),
    ("git -C merge status", False),
    ("gh pr view 12", False),
    ("gh pr list --search merge", False),
    ("python3 .claude/skills/harness/bin/merge-gate.py merge-distill --root R --feature F --pr 7",
     False),
]


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
check("T-05 unpinned repo with sync on is an invalid config: the merge is denied with the loader's "
      "diagnosis and the repair command",
      d == "deny" and "github.repo" in reason and "upgrade-config.py" in reason, reason)
for entry, name in (("opened", "T-05 opened allows"), ("not-applicable", "T-05 not-applicable allows"), ("recovered-terminal", "T-05 recovered-terminal allows")):
    root, _ = fixture(entry=entry)
    r, d, _ = gate("git merge feature/test", root)
    check(name, r.returncode == 0 and d is None)
root, _ = fixture(sync=False)
r, d, _ = gate("git merge feature/test", root)
check("T-05 sync false allows", r.returncode == 0 and d is None)
root, _ = fixture()
subprocess.run(["git", "branch", "other"], cwd=root, check=True)
r, d, _ = gate("git merge other", root)
check("T-05 branch matching no feature allows", r.returncode == 0 and d is None)
r, d, reason = gate("git merge no-such-ref", root)
check("FEAT-2225 unreadable git merge ref denies rather than guessing non-distill",
      d == "deny" and "could not be read" in reason, f"decision={d} reason={reason!r}")
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
# EVERY feature id: synthetic ones plus feature_id_probe_support.held_feature_ids(feature_schema).
sys.path.insert(0, BIN)
import feature_schema  # noqa: E402
from feature_id_probe_support import held_feature_ids  # noqa: E402
allowed = []
for feature in ["BUG-9-x", "PR-9-fixture"] + held_feature_ids(feature_schema):
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
r, d, reason = gate("gh pr merge 7", root, fake)
check("FEAT-2225 gh outage with no matching feature denies: changed paths unreadable",
      d == "deny" and "could not be read" in reason, f"decision={d} reason={reason!r}")
view_only_fails = os.path.join(root, "gh-view-fails")
with open(view_only_fails, "w") as f:
    f.write('#!/bin/sh\nif [ "$2" = diff ]; then echo src/ordinary.py; exit 0; fi\necho unavailable >&2\nexit 9\n')
os.chmod(view_only_fails, 0o755)
r, d, _ = gate("gh pr merge 7", root, view_only_fails)
check("T-05 gh head outage with readable ordinary diff and no matching feature allows",
      d is None and "could not verify" in r.stderr, f"decision={d} stderr={r.stderr!r}")
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
    stream.write(json.dumps(build_config())[:-1] + ',"github":{"sync":true,"repo":"acme/widgets"}}')
r, d, reason = gate("git merge feature/test", root)
check("duplicate harness.json keys deny the merge with the loader's diagnosis rather than "
      "choosing one", d == "deny" and "duplicate key" in reason, f"rc={r.returncode} reason={reason!r}")

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

# FEAT-2225 T-04: distill candidates (changed Expertise paths) merge only through the locked
# `merge-distill` executor. Fixtures: a bare origin, an owner checkout on main and a linked
# feature worktree whose Expertise change was applied by expertise-merge.py member-ops.
import harness_merge  # noqa: E402

DFEAT = "FEAT-9100-distill-fixture"
DBRANCH = f"feat/{DFEAT}"
CRAFT = ".harness/expertise/harness-backend-dev.md"
PLAN = ("status: {status}\ntasks:\n  - id: T-01\n    title: Fixture task\n    change_type: test\n"
        "    execution_mode: main-session-direct\n    files: [fixture.py]\n    status: ready\n"
        "    verify: python3 test.py\n    intent: Exercise the merge gate fixture.\n")
FAKE_GH = r'''#!/usr/bin/env python3
import fcntl, json, os, subprocess, sys
path = os.environ["FAKE_GH_STATE"]
with open(path) as f:
    state = json.load(f)
args = sys.argv[1:]


def save():
    with open(path, "w") as f:
        json.dump(state, f)


def second_view():
    hook = state.get("on_second_view")
    if hook == "advance-main":
        for cmd in (["commit", "--allow-empty", "-qm", "advance"], ["push", "-q", "origin", "main"]):
            subprocess.run(["git", "-C", state["owner"], *cmd], check=True, capture_output=True)
    if hook == "move-head":
        state["head"] = "1" * 40


def lock_held():
    fd = os.open(state["lock"], os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return False
    except OSError:
        return True
    finally:
        os.close(fd)


if args[:2] == ["pr", "view"]:
    state["views"] = state.get("views", 0) + 1
    if state["views"] == 2:
        second_view()
    save()
    meta = {"headRefOid": state["head"], "headRefName": state["branch"], "baseRefName": "main"}
    print(meta["headRefName"] if "-q" in args else json.dumps(meta))
elif args[:2] == ["pr", "diff"]:
    if state.get("diff_fails"):
        sys.exit("diff unavailable")
    print("\n".join(state["files"]))
elif args[:2] == ["pr", "merge"]:
    state.setdefault("merges", []).append({"args": args, "lock_held": lock_held()})
    save()
else:
    sys.exit(2)
'''


def git(cwd, *args):
    return subprocess.run(["git", "-C", cwd, *args], check=True, capture_output=True,
                          text=True, timeout=30).stdout.strip()


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as stream:
        stream.write(content if isinstance(content, str) else json.dumps(content))


def seed_owner(owner, entry, repo):
    github = {"build_entry": entry, "repo": repo} if entry else {}
    feature_dir = os.path.join(owner, ".harness", "harness", "features", DFEAT)
    write(os.path.join(owner, ".harness", "team-config.yaml"), "agents: {}\n")
    write(os.path.join(owner, ".harness", "harness.json"),
          build_config({"github": {"sync": True, "repo": "acme/widgets"}}))
    write(os.path.join(owner, ".gitignore"), "*.lock\n")
    write(os.path.join(feature_dir, "feature.json"),
          {"feature_id": DFEAT, "branch": DBRANCH, "github": github})
    write(os.path.join(feature_dir, "plan.yaml"), PLAN.format(status="build"))


def member_ops(wt, entry="Distill fixture entry text."):
    ops = [{"op": "add", "section": "Patterns", "target": "P-01", "entry": entry, "why": "fixture"}]
    return subprocess.run(
        [sys.executable, os.path.join(BIN, "expertise-merge.py"), "member-ops", "--root", wt,
         "--feature", DFEAT, "--persona", "harness-backend-dev", "--runtime-id", "rt-1",
         "--parent-id", "parent-1", "--tier", "craft", "--ops", "-"],
        input=json.dumps(ops), capture_output=True, text=True, timeout=60)


def commit_push(wt, message):
    git(wt, "add", "-A")
    git(wt, "commit", "-qm", message)
    git(wt, "push", "-q", "origin", DBRANCH)
    return git(wt, "rev-parse", "HEAD")


def distill_fixture(entry="opened", repo="acme/widgets", apply=True):
    base = os.path.realpath(tempfile.mkdtemp())
    origin, owner, wt = (os.path.join(base, name) for name in ("origin.git", "owner", "wt"))
    git(base, "init", "-q", "--bare", "-b", "main", origin)
    git(base, "init", "-q", "-b", "main", owner)
    for key, value in (("user.email", "t@example.invalid"), ("user.name", "T"), ("commit.gpgsign", "false")):
        git(owner, "config", key, value)
    seed_owner(owner, entry, repo)
    git(owner, "add", "-A")
    git(owner, "commit", "-qm", "base")
    git(owner, "remote", "add", "origin", origin)
    git(owner, "push", "-q", "origin", "main")
    git(owner, "worktree", "add", "-q", "-b", DBRANCH, wt)
    if apply:
        ops = member_ops(wt)
        assert ops.returncode == 0, ops.stdout + ops.stderr
    else:
        write(os.path.join(wt, "src", "ordinary.py"), "x = 1\n")
    head = commit_push(wt, "distill")
    gh = os.path.join(base, "gh")
    write(gh, FAKE_GH)
    os.chmod(gh, 0o755)
    fx = {"base": base, "owner": owner, "wt": wt, "gh": gh, "state": os.path.join(base, "gh-state.json"),
          "lock": os.path.join(owner, ".harness", "merge-distill.lock")}
    set_state(fx, head=head, branch=DBRANCH, files=[CRAFT], owner=owner, lock=fx["lock"])
    return fx


def set_state(fx, **values):
    state = {}
    if os.path.exists(fx["state"]):
        with open(fx["state"]) as stream:
            state = json.load(stream)
    state.update(values)
    write(fx["state"], state)


def gh_state(fx):
    with open(fx["state"]) as stream:
        return json.load(stream)


def distill(fx, feature=DFEAT, pr="7", env_extra=None):
    env = dict(os.environ, GH_BIN=fx["gh"], FAKE_GH_STATE=fx["state"], **(env_extra or {}))
    return subprocess.run([sys.executable, GATE, "merge-distill", "--root", fx["wt"], "--feature", feature,
                           "--pr", pr], capture_output=True, text=True, cwd=fx["owner"], env=env, timeout=60)


def refused_before_merge(name, fx, result, *needles):
    merges = gh_state(fx).get("merges", [])
    check(name, result.returncode != 0 and not merges and all(n in result.stderr for n in needles),
          f"rc={result.returncode} merges={merges} stderr={result.stderr!r}")


def blob_sha(fx, rel):
    import hashlib
    data = subprocess.run(["git", "-C", fx["wt"], "cat-file", "blob", f"HEAD:{rel}"],
                          capture_output=True, check=True, timeout=30).stdout
    return hashlib.sha256(data).hexdigest()


def json_or_empty(text):
    try:
        return json.loads(text)
    except ValueError:
        return {}


def option_value(args, flag):
    return args[args.index(flag) + 1] if flag in args else None


def check_merged_at_head(fx, r):
    merges = gh_state(fx).get("merges", [])
    merge = merges[0] if len(merges) == 1 else {"args": [], "lock_held": False}
    check("FEAT-2225 valid distill merges once, holding the owner lock, at the exact head",
          r.returncode == 0 and merge["lock_held"] and merge["args"][:3] == ["pr", "merge", "7"]
          and option_value(merge["args"], "--match-head-commit") == gh_state(fx)["head"],
          f"rc={r.returncode} merges={merges} stderr={r.stderr!r}")


def check_distill_evidence(fx, r):
    evidence = json_or_empty(r.stdout)
    first = (evidence.get("files") or [{}])[0]
    expected = {"head": gh_state(fx)["head"], "main": git(fx["owner"], "rev-parse", "main"),
                "destination": CRAFT, "sha256": blob_sha(fx, CRAFT)}
    actual = {"head": evidence.get("head"), "main": evidence.get("main"),
              "destination": first.get("destination"), "sha256": first.get("sha256")}
    check("FEAT-2225 valid distill emits head, main and committed hash evidence",
          actual == expected, f"evidence={evidence}")


def case_distill_valid():
    fx = distill_fixture()
    r = distill(fx)
    check_merged_at_head(fx, r)
    check_distill_evidence(fx, r)
    return fx


def case_distill_lock_contention():
    fx = distill_fixture()
    with harness_merge.acquire(fx["lock"]):
        r = distill(fx, env_extra={"HARNESS_LOCK_TIMEOUT_SECONDS": "0.5"})
    refused_before_merge("FEAT-2225 distill waits on the one owner-checkout lock and refuses LOCKED",
                         fx, r, "LOCKED", fx["lock"])
    check("FEAT-2225 lock refusal exits with the merge core's LOCKED code", r.returncode == 6, r.stderr)


def case_distill_changed_main_and_head():
    fx = distill_fixture()
    git(fx["owner"], "commit", "--allow-empty", "-qm", "main moved")
    git(fx["owner"], "push", "-q", "origin", "main")
    refused_before_merge("FEAT-2225 distill refuses a head that does not contain current main",
                         fx, distill(fx), "does not contain current main")
    fx = distill_fixture()
    write(os.path.join(fx["wt"], "src", "later.py"), "y = 2\n")
    git(fx["wt"], "add", "-A")
    git(fx["wt"], "commit", "-qm", "local only")
    refused_before_merge("FEAT-2225 distill refuses a worktree that is not at the PR head",
                         fx, distill(fx), "not PR head")


def case_distill_recheck():
    fx = distill_fixture()
    set_state(fx, on_second_view="advance-main")
    refused_before_merge("FEAT-2225 distill rechecks main immediately before merging",
                         fx, distill(fx), "main advanced")
    fx = distill_fixture()
    set_state(fx, on_second_view="move-head")
    refused_before_merge("FEAT-2225 distill rechecks the PR head immediately before merging",
                         fx, distill(fx), "head moved")


def case_distill_replay_invalid():
    fx = distill_fixture()
    with open(os.path.join(fx["wt"], CRAFT), "a") as stream:
        stream.write("- P-02: hand-written entry with no receipt.\n")
    set_state(fx, head=commit_push(fx["wt"], "hand edit"))
    refused_before_merge("FEAT-2225 distill refuses committed Expertise that differs from the replay",
                         fx, distill(fx), "differs from the replay")
    fx = distill_fixture()
    write(os.path.join(fx["wt"], ".harness", "harness", "expertise", "harness-qa.md"), "# harness-qa\n")
    set_state(fx, head=commit_push(fx["wt"], "unreceipted"), files=[CRAFT, ".harness/harness/expertise/harness-qa.md"])
    refused_before_merge("FEAT-2225 distill refuses when replay --check refuses (unreceipted change)",
                         fx, distill(fx), "replay --check refused", "UNRECEIPTED")


def case_distill_build_entry():
    for name, kwargs, needles in (
        ("missing", {"entry": None}, ("gh-sync.py open",)),
        ("wrong-repository", {"entry": "opened", "repo": "elsewhere/wrong"}, ("recover-mirror", "--previous-repo")),
        ("recovery-required", {"entry": "recovery-required"}, ("needs its GitHub mirror recovery completed",)),
    ):
        fx = distill_fixture(**kwargs)
        refused_before_merge(f"FEAT-2225 replay-valid distill with {name} build-entry evidence refuses "
                             f"with recovery guidance before gh merge", fx, distill(fx), DFEAT, *needles)


def case_distill_identity():
    fx = distill_fixture()
    refused_before_merge("FEAT-2225 distill refuses a feature id that does not own the PR",
                         fx, distill(fx, feature="FEAT-9101-not-the-owner"), "REFUSED")
    fx = distill_fixture(apply=False)
    set_state(fx, files=["src/ordinary.py"])
    refused_before_merge("FEAT-2225 merge-distill refuses a PR that changes no Expertise",
                         fx, distill(fx), "not a distill candidate")


def hook(fx, command, **state):
    set_state(fx, **state)
    return gate(command, fx["owner"], fx["gh"], {"FAKE_GH_STATE": fx["state"]})


def hook_denies(fx, name, command, needle, **state):
    _, d, reason = hook(fx, command, **state)
    check(name, d == "deny" and needle in reason, reason)


def hook_allows(fx, name, command, **state):
    _, d, reason = hook(fx, command, **state)
    check(name, d is None, reason)


def case_raw_distill_hook_denials(fx):
    command = "python3 .claude/skills/harness/bin/merge-gate.py merge-distill --root <feature-worktree>"
    hook_denies(fx, "FEAT-2225 raw git merge of a distill candidate is refused with the merge-distill command",
                f"git merge {DBRANCH}", f"{command} --feature {DFEAT} --pr <pr-number>")
    hook_denies(fx, "FEAT-2225 raw gh pr merge of a distill candidate is refused with the merge-distill command",
                "gh pr merge 7", f"{command} --feature {DFEAT} --pr 7")
    hook_denies(fx, "FEAT-2225 nested raw gh distill merge is refused",
                "bash -c 'gh pr merge 7 --squash'", "merge-distill")
    hook_denies(fx, "FEAT-2225 repository-tier Expertise change is a distill candidate whatever the branch name",
                "gh pr merge 7", "--feature <feature-id> --pr 7", branch="topic/plain",
                files=[".harness/harness/expertise/harness-qa.md"])
    hook_denies(fx, "FEAT-2225 unreadable gh changed-path evidence refuses", "gh pr merge 7",
                "could not be read", branch=DBRANCH, files=[CRAFT], diff_fails=True)


def case_raw_distill_hook_allows(fx):
    hook_allows(fx, "FEAT-2225 ordinary gh merge with a valid receipt still allows", "gh pr merge 7",
                branch=DBRANCH, files=["src/ordinary.py"], diff_fails=False)
    hook_allows(fx, "FEAT-2225 the merge-distill command itself is not a raw merge",
                f"{sys.executable} {GATE} merge-distill --root {fx['wt']} --feature {DFEAT} --pr 7")


def case_shipped_not_exempt():
    fx = distill_fixture()
    write(os.path.join(fx["owner"], ".harness", "harness", "features", DFEAT, "plan.yaml"),
          PLAN.format(status="done"))
    _, d, reason = hook(fx, "gh pr merge 7")
    check("FEAT-2225 a shipped feature's distill candidate is not exempt", d == "deny" and "merge-distill" in reason,
          reason)


VALID_DISTILL = case_distill_valid()
case_raw_distill_hook_denials(VALID_DISTILL)
case_raw_distill_hook_allows(VALID_DISTILL)
case_distill_lock_contention()
case_distill_changed_main_and_head()
case_distill_recheck()
case_distill_replay_invalid()
case_distill_build_entry()
case_distill_identity()
case_shipped_not_exempt()

# FEAT-2337: the corpus against merge-gate.py itself, on a HEALTHY root (it refuses every command
# on a broken one) whose checked-out branch owes its Build-entry receipt, with gh unreachable so a
# PR head falls back to that branch: every guarded merge is refused and every other command passes.
def case_applicability_corpus():
    root, _ = fixture()
    for command, guarded in APPLICABILITY_CORPUS:
        r, d, reason = gate(command, root, "/nonexistent/feat2337-gh")
        check(f"FEAT-2337 corpus: {command!r} is {'refused' if guarded else 'allowed'}",
              r.returncode == 0 and d == ("deny" if guarded else None),
              f"rc={r.returncode} decision={d} reason={reason!r} stderr={r.stderr[-300:]!r}")
    shutil.rmtree(root, ignore_errors=True)


case_applicability_corpus()

print("ALL PASSED" if not fails else f"{fails} FAILED")
sys.exit(bool(fails))
