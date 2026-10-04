"""FEAT-70 SC-02 scratch-plan script over ONE checkout. Usage:
    python3 feat70-scratch-plans.py <checkout-root> <plan-list-file> <out.json>

<plan-list-file> names, one per line, every `.harness/harness/features/*/plan.yaml` tracked at the
implementation pin except this feature's own — discovered once, in git order, and handed to BOTH
sides so both grade the same corpus. The checkout is copied to a scratch tree (its own record
removed, `.git`/`__pycache__`/worktrees excluded) and every command runs THERE with the checkout's
own bin, so nothing is written into a clean checkout. Per plan, in document order:
  check --file <plan> --root <scratch>
  set-feature-station --station <its current top-level status>      (skipped when absent)
  set-task-station --task <id> --station <its status, or ready>      per task
  amend --show --key <tasks|decisions> --id <id> --field <f>         per string field, not id/status
record-amendments is deliberately absent (it crashes at baseline; SC-03 is its red-first proof).
Every command's argv, exit, stdout, stderr, plan bytes before/after and sha1s are recorded."""
import hashlib, json, os, shutil, subprocess, sys, importlib.util

root, plan_list, out = (os.path.abspath(a) for a in sys.argv[1:4])
BIN = os.path.join(root, ".claude", "skills", "harness", "bin")
OWN = os.path.join(".harness", "harness", "features", "FEAT-70-long-file-plan-merge-package")
plans = [l.strip() for l in open(plan_list) if l.strip()]

spec = importlib.util.spec_from_file_location("feat70_harness_yaml", os.path.join(BIN, "harness_yaml.py"))
hy = importlib.util.module_from_spec(spec); spec.loader.exec_module(hy)

scratch = os.path.join("/tmp/feat70-scratch", os.path.basename(root))
shutil.rmtree(os.path.dirname(scratch), ignore_errors=True)
shutil.copytree(root, scratch, symlinks=True, ignore=shutil.ignore_patterns(".git", "__pycache__", "worktrees"))
scratch = os.path.realpath(scratch)   # the tool prints resolved paths (/private/tmp on macOS)
shutil.rmtree(os.path.join(scratch, OWN), ignore_errors=True)
CLI = os.path.join(scratch, ".claude", "skills", "harness", "bin", "plan-merge.py")

env = dict(os.environ)
env.pop("HARNESS_AGENT_TYPE", None)
records = []
sha = lambda s: None if s is None else hashlib.sha1(s.encode("utf-8", "surrogateescape")).hexdigest()


def read(p):
    try:
        return open(p, "rb").read().decode("utf-8", "surrogateescape")
    except OSError:
        return None


def run(plan, *argv):
    path = os.path.join(scratch, plan)
    before = read(path)
    p = subprocess.run([sys.executable, CLI, *argv], cwd=scratch, capture_output=True, text=True, env=env, timeout=300)
    after = read(path)
    # Plan bytes are kept only when the command CHANGED them; otherwise the sha1 pair (equal) is the
    # record. 6,500 commands x two full plans per side was 1.2 GB of identical bytes per side.
    changed = before != after
    records.append({"plan": plan, "argv": list(argv), "exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr,
                    "plan_before": before if changed else None, "plan_after": after if changed else None,
                    "plan_changed": changed, "stdout_sha": sha(p.stdout), "stderr_sha": sha(p.stderr),
                    "before_sha": sha(before), "after_sha": sha(after)})


def string_fields(item):
    return [k for k, v in item.items() if k not in ("id", "status") and isinstance(v, str)]


for plan in plans:
    path = os.path.join(scratch, plan)
    run(plan, "check", "--file", path, "--root", scratch)
    try:
        doc = hy.load_file(path)
    except Exception as exc:  # an unloadable plan is recorded and its mutations skipped
        records.append({"plan": plan, "argv": ["<load>"], "exit": None, "stdout": "", "stderr": repr(exc),
                        "plan_before": None, "plan_after": None, "stdout_sha": None, "stderr_sha": None,
                        "before_sha": None, "after_sha": None})
        continue
    doc = doc if isinstance(doc, dict) else {}
    station = doc.get("status")
    if isinstance(station, str):
        run(plan, "set-feature-station", "--file", path, "--station", station)
    tasks = [t for t in (doc.get("tasks") or []) if isinstance(t, dict) and isinstance(t.get("id"), str)]
    for t in tasks:
        st = t.get("status") if isinstance(t.get("status"), str) else "ready"
        run(plan, "set-task-station", "--file", path, "--task", t["id"], "--station", st)
    for key in ("tasks", "decisions"):
        for item in (doc.get(key) or []):
            if not (isinstance(item, dict) and isinstance(item.get("id"), str)):
                continue
            for field in string_fields(item):
                run(plan, "amend", "--file", path, "--key", key, "--id", item["id"], "--field", field, "--show")
    print(f"{plan}: {sum(1 for r in records if r['plan'] == plan)} command(s)", flush=True)

json.dump({"scratch_root": scratch, "excludes": OWN, "plans": plans, "records": records}, open(out, "w"))
shutil.rmtree(os.path.dirname(scratch), ignore_errors=True)
print(f"{len(records)} command(s) over {len(plans)} plan(s)")
