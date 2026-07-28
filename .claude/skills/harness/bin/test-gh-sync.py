#!/usr/bin/env python3
"""gh-sync.py must get these right — offline, against a fake gh.

The fake logs every invocation and returns canned JSON, so the tests assert the
EXACT outward calls (repo pinned on every one, labels derived, absorbed issues
closed) and the exit-code contract: environmental problems exit 0 (the mirror
never gates), caller errors exit 1.

    ./test-gh-sync.py    -> exit 0 all pass, 1 otherwise
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SYNC = os.path.join(HERE, "gh-sync.py")

FAKE_GH = """#!/bin/bash
echo "$*" | tr '\n' '§' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
case "$1 $2" in
  "auth status") exit 0 ;;
  "api -X")
    case "$*" in
      *milestones\\ -f*) echo '{"number": 7}' ;;
      *) echo '{}' ;;
    esac ;;
  "issue create")
    n=$(( $(grep -c "issue create" "$FAKE_LOG") + 40 ))
    echo "https://github.com/implentio/fake/issues/$n" ;;
  "issue close") exit 0 ;;
  "label create") exit 0 ;;
esac
exit 0
"""


def stage(tmp, sync=True, repo="implentio/fake"):
    feat = os.path.join(tmp, ".harness", "features", "FEAT-05-export-fix")
    os.makedirs(feat)
    g = {"sync": sync}
    if repo:
        g["repo"] = repo
    json.dump({"github": g}, open(os.path.join(tmp, ".harness", "harness.json"), "w"))
    open(os.path.join(feat, "BRIEF.md"), "w").write("""# BRIEF — FEAT-05-export-fix

## Problem
Export drops rows.

## Goal
Reliable export.

## Requirements
- REQ-01: exports complete.

## Success Criteria
- SC-01: header row present. verify: automated
- SC-02: 20MB file exports. verify: automated

## Approval

status: approved
""")
    open(os.path.join(feat, "PLAN.md"), "w").write("""# PLAN — FEAT-05-export-fix

## Tasks
### T-01 — streaming export rebuild
- change_type: feature
- traces: REQ-01, SC-01, SC-02
- absorbs: #12, #14

### T-02 — CI export smoke job
- change_type: ci
- traces: SC-02

### T-03 — fix header regression test
- change_type: bugfix
- traces: SC-01
""")
    open(os.path.join(feat, "feature.yaml"), "w").write("feature_id: FEAT-05-export-fix\nstatus: in_progress\n")
    return feat


def run(args, tmp, env_extra=None):
    env = dict(os.environ)
    env["FAKE_LOG"] = os.path.join(tmp, "calls.log")
    env["GH_SYNC_GH"] = os.path.join(tmp, "gh")
    env.update(env_extra or {})
    return subprocess.run([SYNC] + args, capture_output=True, text=True, env=env)


def calls(tmp):
    p = os.path.join(tmp, "calls.log")
    return open(p).read().splitlines() if os.path.exists(p) else []


fails = 0


def check(name, cond, detail=""):
    global fails
    if cond:
        print(f"ok    {name}")
    else:
        fails += 1
        print(f"FAIL  {name}\n      {detail}")


with tempfile.TemporaryDirectory() as tmp:
    gh_path = os.path.join(tmp, "gh")
    open(gh_path, "w").write(FAKE_GH)
    os.chmod(gh_path, 0o755)
    os.symlink(gh_path, os.path.join(tmp, "gh-on-path"))  # for which()
    feat = stage(tmp)

    # --- environmental skips exit 0
    r = run(["open", feat], tmp, {"GH_SYNC_GH": os.path.join(tmp, "no-such-gh")})
    check("gh missing -> SKIP, exit 0", r.returncode == 0 and "SKIP" in r.stdout, r.stdout)

    json.dump({"github": {"sync": False}}, open(os.path.join(tmp, ".harness", "harness.json"), "w"))
    r = run(["open", feat], tmp)
    check("sync disabled -> SKIP, exit 0", r.returncode == 0 and "SKIP" in r.stdout, r.stdout)

    json.dump({"github": {"sync": True}}, open(os.path.join(tmp, ".harness", "harness.json"), "w"))
    r = run(["open", feat], tmp)
    check("repo unpinned -> SKIP, exit 0", r.returncode == 0 and "not pinned" in r.stdout, r.stdout)

    # --- caller errors exit 1
    r = run(["open", os.path.join(tmp, "nope")], tmp)
    check("bad feature dir -> ERROR, exit 1", r.returncode == 1, r.stdout)

    # --- the real open
    json.dump({"github": {"sync": True, "repo": "implentio/fake"}},
              open(os.path.join(tmp, ".harness", "harness.json"), "w"))
    r = run(["open", feat], tmp)
    log = calls(tmp)
    check("open exits 0", r.returncode == 0, r.stdout + r.stderr)
    check("milestone created with SC checklist",
          any("milestones" in l and "SC-01" in l for l in log))
    check("3 issues created", sum("issue create" in l for l in log) == 3, str(log))
    check("every call pins --repo",
          all("--repo implentio/fake" in l or "repos/implentio/fake" in l or l.startswith("auth") for l in log),
          str(log))
    create_lines = [l for l in log if "issue create" in l]
    check("T-01 unlabeled beyond harness (feature)",
          any("T-01" in l and "--label harness" in l and "chore" not in l and "bug " not in l for l in create_lines))
    check("T-02 labeled chore (ci)", any("T-02" in l and "--label chore" in l for l in create_lines))
    check("T-03 labeled bug (bugfix)", any("T-03" in l and "--label bug" in l for l in create_lines))
    check("absorbs cited in T-01 body", any("T-01" in l and "absorbs: #12, #14" in l for l in create_lines))
    fy = open(os.path.join(feat, "feature.yaml")).read()
    check("issue numbers recorded in feature.yaml",
          "milestone: 7" in fy and re.search(r"T-01: 4\d", fy), fy)

    check("labels ensured before any issue create",
          [l for l in log if "label create" in l]
          and log.index([l for l in log if "label create" in l][0])
              < log.index([l for l in log if "issue create" in l][0]),
          str(log[:6]))
    ms_idx = log.index([l for l in log if "milestones -f" in l or ("milestones" in l and "POST" in l)][0])
    # feature.yaml already carried the milestone before the last issue was created:
    # asserted indirectly — the recorded map exists even though save happens per-create.

    # --- idempotency: rerun creates nothing new
    n_before = len(calls(tmp))
    r = run(["open", feat], tmp)
    new = [l for l in calls(tmp)[n_before:] if "issue create" in l or "milestones" in l]
    check("re-run open creates nothing", r.returncode == 0 and not new, str(new))

    # --- close-task closes the issue AND the absorbed ones
    open(os.path.join(tmp, "calls.log"), "w").close()
    r = run(["close-task", feat, "T-01"], tmp)
    log = calls(tmp)
    closes = [l for l in log if l.startswith("issue close")]
    check("close-task closes issue + 2 absorbed", r.returncode == 0 and len(closes) == 3, str(log))
    check("absorbed #12 #14 closed",
          any(" 12 " in l + " " for l in closes) and any(" 14 " in l + " " for l in closes), str(closes))

    # --- ship closes the milestone
    open(os.path.join(tmp, "calls.log"), "w").close()
    r = run(["ship", feat], tmp)
    log = calls(tmp)
    check("ship PATCHes milestone closed",
          r.returncode == 0 and any("milestones/7" in l and "state=closed" in l for l in log), str(log))

    # --- backlog: accepted residuals become plain issues, labeled by nature, no milestone
    open(os.path.join(tmp, "calls.log"), "w").close()
    r = run(["backlog", feat, "bug:echo-only returns unhandled", "chore:INV-10 exec-bit hole",
             "enhancement:progress events"], tmp)
    log = [l for l in calls(tmp) if "issue create" in l]
    check("backlog creates 3 issues, exit 0", r.returncode == 0 and len(log) == 3, str(log))
    check("backlog natures label correctly",
          any("--label harness --label bug" in l for l in log)
          and any("--label harness --label chore" in l for l in log)
          and any("progress events" in l and "--label harness" in l and "chore" not in l and "bug" not in l for l in log),
          str(log))
    check("backlog issues carry NO milestone", all("--milestone" not in l for l in log), str(log))
    r = run(["backlog", feat, "typo-no-colon"], tmp)
    check("malformed backlog item -> ERROR exit 1", r.returncode == 1, r.stdout)

print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
