#!/usr/bin/env python3
"""gh-sync.py must get these right — offline, against a fake gh.

The fake logs every invocation and returns canned JSON, so the tests assert the
EXACT outward calls (repo pinned on every one, labels derived, close-task
closes exactly one issue and leaves absorbed issues open) and the exit-code
contract: environmental problems exit 0 (the mirror never gates), caller
errors exit 1.

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
echo "$*" | tr '\n' '\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
case "$*" in
  *"sub_issues -F sub_issue_id="*)
    echo '{}'
    exit 0 ;;
  *"--jq .id"*)
    num=$(echo "$*" | grep -oE 'issues/[0-9]+' | head -1 | grep -oE '[0-9]+')
    echo "9000$num"
    exit 0 ;;
esac
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


def stage(tmp, sync=True, repo="implentio/fake", phrase="reliable csv export",
          feat_name="FEAT-05-export-fix"):
    feat = os.path.join(tmp, ".harness", "features", feat_name)
    os.makedirs(feat)
    g = {"sync": sync}
    if repo:
        g["repo"] = repo
    json.dump({"github": g}, open(os.path.join(tmp, ".harness", "harness.json"), "w"))
    h1 = f"# BRIEF — {feat_name} — {phrase}" if phrase else f"# BRIEF — {feat_name}"
    open(os.path.join(feat, "BRIEF.md"), "w").write(f"""{h1}

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
    open(os.path.join(feat, "feature.yaml"), "w").write(
        f"feature_id: {feat_name}\nstatus: in_progress\n")
    return feat


def run(args, tmp, env_extra=None):
    env = dict(os.environ)
    env["FAKE_LOG"] = os.path.join(tmp, "calls.log")
    env["GH_SYNC_GH"] = os.path.join(tmp, "gh")
    env.update(env_extra or {})
    return subprocess.run([SYNC] + args, capture_output=True, text=True, env=env)


def calls(tmp):
    p = os.path.join(tmp, "calls.log")
    # ENCODING IS EXPLICIT, and the separator above is a SINGLE BYTE. CI on Linux found
    # what macOS could not: `tr '\n' '§'` gives `tr` a TWO-byte SET2 (§ is U+00A7 =
    # 0xC2 0xA7). BSD tr copies both bytes; GNU tr truncates SET2 to SET1's length and
    # emits a lone 0xC2 — invalid UTF-8 — so this read died with
    # "can't decode byte 0xc2 in position 11: invalid continuation byte" on the runner and
    # passed on the author's machine. \001 (SOH) is one byte in every
    # implementation and cannot appear in a gh argument. NOT \034 (FS): str.splitlines()
    # treats \x1c, \x1d, \x1e and \x85 as LINE BOUNDARIES, so flattening newlines to FS
    # and then calling splitlines() re-splits them and defeats the whole point — a first
    # fix for this did exactly that and turned one green suite into seven failures. errors="replace" so a future mangling is a visible
    # test failure rather than a crash inside the harness.
    return (open(p, encoding="utf-8", errors="replace").read().splitlines()
            if os.path.exists(p) else [])


FAKE_GH_ATTACH_FAILS = """#!/bin/bash
echo "$*" | tr '\n' '\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
case "$*" in
  *"sub_issues -F sub_issue_id="*)
    echo "simulated network failure" >&2
    exit 1 ;;
  *"--jq .id"*)
    num=$(echo "$*" | grep -oE 'issues/[0-9]+' | head -1 | grep -oE '[0-9]+')
    echo "9000$num"
    exit 0 ;;
esac
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


def install_gh(tmp, script=FAKE_GH):
    gh_path = os.path.join(tmp, "gh")
    open(gh_path, "w").write(script)
    os.chmod(gh_path, 0o755)


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
    task_create_lines = [l for l in log if "issue create" in l and re.search(r"\bT-0\d\b", l)]
    check("3 issues created", len(task_create_lines) == 3, str(log))
    parent_create_lines = [l for l in log if "issue create" in l and not re.search(r"\bT-0\d\b", l)]
    check("parent created and recorded",
          len(parent_create_lines) == 1
          and "--repo implentio/fake" in parent_create_lines[0]
          and "--label harness" in parent_create_lines[0]
          and "--milestone" not in parent_create_lines[0],
          str(log))
    check("parent title carries the H1 phrase",
          any("FEAT-05-export-fix — reliable csv export" in l for l in parent_create_lines),
          str(parent_create_lines))
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
    check("created parent records origin created", "parent_origin: created" in fy, fy)

    attach_lines = [l for l in log if "sub_issues -F sub_issue_id=" in l]
    check("three sub-issues attached to the parent", len(attach_lines) == 3, str(attach_lines))
    check("attach uses internal id not number",
          len(attach_lines) > 0 and all(re.search(r"sub_issue_id=9000\d+", l) for l in attach_lines),
          str(attach_lines))

    check("labels ensured before any issue create",
          [l for l in log if "label create" in l]
          and log.index([l for l in log if "label create" in l][0])
              < log.index([l for l in log if "issue create" in l][0]),
          str(log[:6]))
    ms_idx = log.index([l for l in log if "milestones -f" in l or ("milestones" in l and "POST" in l)][0])
    # feature.yaml already carried the milestone before the last issue was created:
    # asserted indirectly — the recorded map exists even though save happens per-create.

    # --- idempotency: rerun creates nothing new (issues, milestones, AND attaches)
    n_before = len(calls(tmp))
    r = run(["open", feat], tmp)
    new = [l for l in calls(tmp)[n_before:]
           if "issue create" in l or "milestones" in l
           or "sub_issue_id=" in l or "--jq .id" in l]
    check("re-run open creates nothing", r.returncode == 0 and not new, str(new))

    # --- close-task closes exactly one issue; absorbed issues are cited and left open
    open(os.path.join(tmp, "calls.log"), "w").close()
    r = run(["close-task", feat, "T-01"], tmp)
    log = calls(tmp)
    closes = [l for l in log if l.startswith("issue close")]
    check("close-task closes exactly one issue", r.returncode == 0 and len(closes) == 1, str(log))
    check("absorbed #12 #14 NOT closed",
          not any(" 12 " in l + " " for l in closes) and not any(" 14 " in l + " " for l in closes), str(closes))

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

# --- empty-phrase fixture: parent title is the bare feat-id, no trailing em-dash
with tempfile.TemporaryDirectory() as tmp2:
    install_gh(tmp2)
    feat2 = stage(tmp2, phrase=None)
    json.dump({"github": {"sync": True, "repo": "implentio/fake"}},
              open(os.path.join(tmp2, ".harness", "harness.json"), "w"))
    r = run(["open", feat2], tmp2)
    log2 = calls(tmp2)
    parent_lines2 = [l for l in log2 if "issue create" in l and not re.search(r"\bT-0\d\b", l)]
    check("empty phrase titles the parent with no trailing em-dash",
          r.returncode == 0 and len(parent_lines2) == 1
          and "--title FEAT-05-export-fix " in parent_lines2[0]
          and "FEAT-05-export-fix —" not in parent_lines2[0],
          str(parent_lines2))

# --- --parent <n> adopts instead of creating
with tempfile.TemporaryDirectory() as tmp3:
    install_gh(tmp3)
    feat3 = stage(tmp3)
    json.dump({"github": {"sync": True, "repo": "implentio/fake"}},
              open(os.path.join(tmp3, ".harness", "harness.json"), "w"))
    r = run(["open", feat3, "--parent", "55"], tmp3)
    log3 = calls(tmp3)
    parent_creates3 = [l for l in log3 if "issue create" in l and not re.search(r"\bT-0\d\b", l)]
    fy3 = open(os.path.join(feat3, "feature.yaml")).read()
    check("--parent adopts",
          r.returncode == 0 and len(parent_creates3) == 0 and "parent: 55" in fy3, fy3)
    check("adopted parent records origin adopted", "parent_origin: adopted" in fy3, fy3)

# --- crash resume: recorded-but-unattached task is attached, not re-created;
#     and the pre-existing parent + its origin survive every per-task save
with tempfile.TemporaryDirectory() as tmp4:
    install_gh(tmp4)
    feat4 = stage(tmp4)
    json.dump({"github": {"sync": True, "repo": "implentio/fake"}},
              open(os.path.join(tmp4, ".harness", "harness.json"), "w"))
    open(os.path.join(feat4, "feature.yaml"), "w").write(
        "feature_id: FEAT-05-export-fix\nstatus: in_progress\n"
        "github:\n"
        "  milestone: 7\n"
        "  parent: 40\n"
        "  parent_origin: created\n"
        "  attached: []\n"
        "  issues:\n"
        "    T-01: 999\n"
    )
    r = run(["open", feat4], tmp4)
    log4 = calls(tmp4)
    check("recorded-not-attached task is attached on re-run",
          r.returncode == 0
          and not any("issue create" in l and "T-01" in l for l in log4)
          and sum(1 for l in log4 if "sub_issue_id=9000999" in l) == 1,
          str(log4))
    fy4 = open(os.path.join(feat4, "feature.yaml")).read()
    check("pre-existing parent survives per-task saves",
          "parent: 40" in fy4 and re.search(r"T-01:\s*999", fy4)
          and re.search(r"T-02:\s*4\d", fy4) and re.search(r"T-03:\s*4\d", fy4),
          fy4)
    check("parent_origin survives per-task saves", "parent_origin: created" in fy4, fy4)

# --- a phrase containing its own em-dash is taken whole, not truncated at the second one
with tempfile.TemporaryDirectory() as tmp5:
    install_gh(tmp5)
    feat5 = stage(tmp5, phrase="streaming export — v2")
    json.dump({"github": {"sync": True, "repo": "implentio/fake"}},
              open(os.path.join(tmp5, ".harness", "harness.json"), "w"))
    r = run(["open", feat5], tmp5)
    log5 = calls(tmp5)
    parent_lines5 = [l for l in log5 if "issue create" in l and not re.search(r"\bT-0\d\b", l)]
    check("phrase containing an em-dash is taken whole",
          r.returncode == 0 and len(parent_lines5) == 1
          and "FEAT-05-export-fix — streaming export — v2" in parent_lines5[0],
          str(parent_lines5))

# --- SC-12: an attach that fails for an environmental reason is a SKIP, exit 0, not a gate —
#     and the issue recorded just before the failed attach survives the crash
with tempfile.TemporaryDirectory() as tmp6:
    install_gh(tmp6, FAKE_GH_ATTACH_FAILS)
    feat6 = stage(tmp6)
    json.dump({"github": {"sync": True, "repo": "implentio/fake"}},
              open(os.path.join(tmp6, ".harness", "harness.json"), "w"))
    r = run(["open", feat6], tmp6)
    fy6 = open(os.path.join(feat6, "feature.yaml")).read()
    check("failed attach is a SKIP, exit 0, for the new subcommand too (SC-12)",
          r.returncode == 0 and "SKIP" in r.stdout, r.stdout)
    check("issue recorded before the failed attach survives the crash",
          re.search(r"T-01:\s*4\d", fy6) is not None, fy6)

# --- abandon: adopted parent stays open, subs + milestone close not_planned/closed
with tempfile.TemporaryDirectory() as tmpA:
    install_gh(tmpA)
    featA = stage(tmpA, feat_name="FEAT-06-abandon-adopted")
    json.dump({"github": {"sync": True, "repo": "implentio/fake"}},
              open(os.path.join(tmpA, ".harness", "harness.json"), "w"))
    open(os.path.join(featA, "feature.yaml"), "w").write(
        "feature_id: FEAT-06-abandon-adopted\nstatus: in_progress\n"
        "github:\n"
        "  milestone: 7\n"
        "  parent: 40\n"
        "  parent_origin: adopted\n"
        "  attached: [T-01, T-02, T-03]\n"
        "  issues:\n"
        "    T-01: 41\n"
        "    T-02: 42\n"
        "    T-03: 43\n"
    )
    reasonA = os.path.join(tmpA, "reason.txt")
    open(reasonA, "w").write("budget cut — deprioritized this quarter")
    r = run(["abandon", featA, "--reason-file", reasonA], tmpA)
    logA = calls(tmpA)
    patchedA = [l for l in logA if "api -X PATCH" in l and "issues/" in l and "state_reason=not_planned" in l]
    check("abandon closes 3 subs not_planned",
          r.returncode == 0
          and {re.search(r"issues/(\d+)", l).group(1) for l in patchedA} == {"41", "42", "43"},
          str(logA))
    check("abandon closes the milestone",
          any("milestones/7" in l and "state=closed" in l for l in logA), str(logA))
    check("abandon posts via --body-file",
          any(l.startswith("issue comment 40") and "--body-file" in l and reasonA in l for l in logA)
          and not any("budget cut" in l for l in logA),
          str(logA))
    check("abandon leaves an adopted parent open",
          not any(re.search(r"\bissues/40\b", l) for l in logA)
          and not any(l.startswith("issue close 40") for l in logA),
          str(logA))

# --- abandon: a created parent closes not_planned, via the same PATCH form as the subs
with tempfile.TemporaryDirectory() as tmpB:
    install_gh(tmpB)
    featB = stage(tmpB, feat_name="FEAT-06-abandon-created")
    json.dump({"github": {"sync": True, "repo": "implentio/fake"}},
              open(os.path.join(tmpB, ".harness", "harness.json"), "w"))
    open(os.path.join(featB, "feature.yaml"), "w").write(
        "feature_id: FEAT-06-abandon-created\nstatus: in_progress\n"
        "github:\n"
        "  milestone: 7\n"
        "  parent: 40\n"
        "  parent_origin: created\n"
        "  attached: [T-01]\n"
        "  issues:\n"
        "    T-01: 41\n"
    )
    reasonB = os.path.join(tmpB, "reason.txt")
    open(reasonB, "w").write("cutting this")
    r = run(["abandon", featB, "--reason-file", reasonB], tmpB)
    logB = calls(tmpB)
    parent40_calls = [l for l in logB if re.search(r"\bissues/40\b", l)]
    check("abandon closes a created parent not_planned",
          r.returncode == 0
          and len(parent40_calls) == 1
          and "state=closed" in parent40_calls[0] and "state_reason=not_planned" in parent40_calls[0]
          and not any(l.startswith("issue close 40") for l in logB),
          str(logB))

# --- abandon: parent recorded with no parent_origin line at all — the specified default,
#     and cmd_abandon must write no receipt so the absent line is never back-filled
with tempfile.TemporaryDirectory() as tmpC:
    install_gh(tmpC)
    featC = stage(tmpC, feat_name="FEAT-06-abandon-noorigin")
    json.dump({"github": {"sync": True, "repo": "implentio/fake"}},
              open(os.path.join(tmpC, ".harness", "harness.json"), "w"))
    open(os.path.join(featC, "feature.yaml"), "w").write(
        "feature_id: FEAT-06-abandon-noorigin\nstatus: in_progress\n"
        "github:\n"
        "  milestone: 7\n"
        "  parent: 40\n"
        "  attached: [T-01]\n"
        "  issues:\n"
        "    T-01: 41\n"
    )
    reasonC = os.path.join(tmpC, "reason.txt")
    open(reasonC, "w").write("cutting this too")
    r = run(["abandon", featC, "--reason-file", reasonC], tmpC)
    logC = calls(tmpC)
    fyC = open(os.path.join(featC, "feature.yaml")).read()
    check("abandon leaves a parent with no recorded origin open",
          r.returncode == 0
          and not any(re.search(r"\bissues/40\b", l) for l in logC)
          and not any(l.startswith("issue close 40") for l in logC)
          and "parent_origin" not in fyC,
          str(logC) + " | " + fyC)

# --- abandon: caller errors on a bad or missing --reason-file
with tempfile.TemporaryDirectory() as tmpD:
    install_gh(tmpD)
    featD = stage(tmpD, feat_name="FEAT-06-abandon-badfile")
    json.dump({"github": {"sync": True, "repo": "implentio/fake"}},
              open(os.path.join(tmpD, ".harness", "harness.json"), "w"))
    open(os.path.join(featD, "feature.yaml"), "w").write(
        "feature_id: FEAT-06-abandon-badfile\nstatus: in_progress\n"
        "github:\n"
        "  milestone: 7\n"
        "  parent: none\n"
        "  attached: []\n"
        "  issues:\n"
        "    T-01: 41\n"
    )
    r = run(["abandon", featD], tmpD)
    check("abandon without --reason-file exits 1", r.returncode == 1, r.stdout)

    open(os.path.join(tmpD, "calls.log"), "w").close()
    emptyD = os.path.join(tmpD, "empty.txt")
    open(emptyD, "w").close()
    r = run(["abandon", featD, "--reason-file", emptyD], tmpD)
    logD = [l for l in calls(tmpD) if l]  # drop the fake-gh's blank separator line
    check("abandon with an empty reason file exits 1",
          r.returncode == 1 and all(l.startswith("auth") for l in logD),
          str(logD))

    open(os.path.join(tmpD, "calls.log"), "w").close()
    notAFileD = os.path.join(tmpD, "no-such-reason.txt")
    r = run(["abandon", featD, "--reason-file", notAFileD], tmpD)
    check("abandon with a nonexistent reason path exits 1", r.returncode == 1, r.stdout)

    open(os.path.join(tmpD, "calls.log"), "w").close()
    unreadableD = os.path.join(tmpD, "unreadable.txt")
    open(unreadableD, "w").write("cannot read this")
    os.chmod(unreadableD, 0o000)
    r = run(["abandon", featD, "--reason-file", unreadableD], tmpD)
    unreadable_result = r.returncode
    os.chmod(unreadableD, 0o644)  # restore so cleanup can remove it
    if os.geteuid() == 0:
        print("skip  abandon with an unreadable reason file exits 1 (running as root — chmod 000 has no effect)")
    else:
        check("abandon with an unreadable reason file exits 1", unreadable_result == 1, str(unreadable_result))

    # FEAT-03 B-1: a BINARY reason file. UnicodeDecodeError is a ValueError, not an
    # OSError, so it escaped post_body_path's handler and surfaced as a traceback
    # rather than a clean caller error. Unlike the chmod case above this needs no
    # euid guard, so it holds as a regression test even when the suite runs as root.
    open(os.path.join(tmpD, "calls.log"), "w").close()
    binaryD = os.path.join(tmpD, "binary-reason.md")
    open(binaryD, "wb").write(b"\x80\x81\xfe\xff not utf-8")
    r = run(["abandon", featD, "--reason-file", binaryD], tmpD)
    check("abandon with a BINARY reason file exits 1, not a traceback",
          r.returncode == 1 and "Traceback" not in (r.stdout + r.stderr),
          f"rc={r.returncode} {(r.stdout + r.stderr)[:120]!r}")

# --- abandon: no recorded milestone still closes subs, and never builds milestones/None
with tempfile.TemporaryDirectory() as tmpE:
    install_gh(tmpE)
    featE = stage(tmpE, feat_name="FEAT-06-abandon-nomilestone")
    json.dump({"github": {"sync": True, "repo": "implentio/fake"}},
              open(os.path.join(tmpE, ".harness", "harness.json"), "w"))
    open(os.path.join(featE, "feature.yaml"), "w").write(
        "feature_id: FEAT-06-abandon-nomilestone\nstatus: in_progress\n"
        "github:\n"
        "  milestone: none\n"
        "  parent: none\n"
        "  attached: []\n"
        "  issues:\n"
        "    T-01: 41\n"
    )
    reasonE = os.path.join(tmpE, "reason.txt")
    open(reasonE, "w").write("no milestone was ever recorded")
    r = run(["abandon", featE, "--reason-file", reasonE], tmpE)
    logE = calls(tmpE)
    check("abandon with no recorded milestone never builds milestones/None",
          r.returncode == 0
          and not any("milestones/None" in l for l in logE)
          and any("issues/41" in l and "state_reason=not_planned" in l for l in logE),
          str(logE))

# --- abandon: sync disabled is still a SKIP, exit 0 (SC-12)
with tempfile.TemporaryDirectory() as tmpF:
    install_gh(tmpF)
    featF = stage(tmpF, feat_name="FEAT-06-abandon-skip")
    json.dump({"github": {"sync": False}}, open(os.path.join(tmpF, ".harness", "harness.json"), "w"))
    reasonF = os.path.join(tmpF, "reason.txt")
    open(reasonF, "w").write("does not matter, sync is off")
    r = run(["abandon", featF, "--reason-file", reasonF], tmpF)
    check("abandon with sync disabled -> SKIP, exit 0", r.returncode == 0 and "SKIP" in r.stdout, r.stdout)

# --- ship: a created parent closes completed, milestone patched closed AFTER the parent close
with tempfile.TemporaryDirectory() as tmpG:
    install_gh(tmpG)
    featG = stage(tmpG, feat_name="FEAT-07-ship-created")
    json.dump({"github": {"sync": True, "repo": "implentio/fake"}},
              open(os.path.join(tmpG, ".harness", "harness.json"), "w"))
    open(os.path.join(featG, "feature.yaml"), "w").write(
        "feature_id: FEAT-07-ship-created\nstatus: in_progress\n"
        "github:\n"
        "  milestone: 7\n"
        "  parent: 40\n"
        "  parent_origin: created\n"
        "  attached: [T-01]\n"
        "  issues:\n"
        "    T-01: 41\n"
    )
    r = run(["ship", featG], tmpG)
    logG = calls(tmpG)
    close40G = [l for l in logG if l.startswith("issue close 40")]
    patch40G = [l for l in logG if re.search(r"\bissues/40\b", l)]
    close_idxG = [i for i, l in enumerate(logG) if l.startswith("issue close 40")]
    ms_idxG = [i for i, l in enumerate(logG) if "milestones/7" in l and "state=closed" in l]
    check("ship closes a created parent completed",
          r.returncode == 0
          and len(close40G) == 1
          and not patch40G
          and bool(close_idxG) and bool(ms_idxG) and close_idxG[0] < ms_idxG[0],
          str(logG))

# --- ship: an adopted parent is left open; the milestone still closes regardless (labelled here)
with tempfile.TemporaryDirectory() as tmpH:
    install_gh(tmpH)
    featH = stage(tmpH, feat_name="FEAT-07-ship-adopted")
    json.dump({"github": {"sync": True, "repo": "implentio/fake"}},
              open(os.path.join(tmpH, ".harness", "harness.json"), "w"))
    open(os.path.join(featH, "feature.yaml"), "w").write(
        "feature_id: FEAT-07-ship-adopted\nstatus: in_progress\n"
        "github:\n"
        "  milestone: 7\n"
        "  parent: 40\n"
        "  parent_origin: adopted\n"
        "  attached: [T-01]\n"
        "  issues:\n"
        "    T-01: 41\n"
    )
    r = run(["ship", featH], tmpH)
    logH = calls(tmpH)
    check("ship leaves an adopted parent open",
          r.returncode == 0
          and not any(l.startswith("issue close 40") for l in logH)
          and not any(re.search(r"\bissues/40\b", l) for l in logH),
          str(logH))
    check("ship closes the milestone regardless of parent origin",
          any("milestones/7" in l and "state=closed" in l for l in logH), str(logH))

# --- ship: a parent with no recorded origin at all is left open (the specified default);
#     the milestone still closes (inline, unlabelled — the discriminating case lives above)
with tempfile.TemporaryDirectory() as tmpI:
    install_gh(tmpI)
    featI = stage(tmpI, feat_name="FEAT-07-ship-noorigin")
    json.dump({"github": {"sync": True, "repo": "implentio/fake"}},
              open(os.path.join(tmpI, ".harness", "harness.json"), "w"))
    open(os.path.join(featI, "feature.yaml"), "w").write(
        "feature_id: FEAT-07-ship-noorigin\nstatus: in_progress\n"
        "github:\n"
        "  milestone: 7\n"
        "  parent: 40\n"
        "  attached: [T-01]\n"
        "  issues:\n"
        "    T-01: 41\n"
    )
    r = run(["ship", featI], tmpI)
    logI = calls(tmpI)
    fyI = open(os.path.join(featI, "feature.yaml")).read()
    check("ship leaves a parent with no recorded origin open",
          r.returncode == 0
          and not any(l.startswith("issue close 40") for l in logI)
          and not any(re.search(r"\bissues/40\b", l) for l in logI)
          and any("milestones/7" in l and "state=closed" in l for l in logI)
          and "parent_origin" not in fyI,
          str(logI) + " | " + fyI)

# --- ship --body-file posts once, on an adopted parent, so the UNCONDITIONALITY of the
#     comment (vs. the conditional close) is what is being checked
with tempfile.TemporaryDirectory() as tmpJ:
    install_gh(tmpJ)
    featJ = stage(tmpJ, feat_name="FEAT-07-ship-bodyfile")
    json.dump({"github": {"sync": True, "repo": "implentio/fake"}},
              open(os.path.join(tmpJ, ".harness", "harness.json"), "w"))
    open(os.path.join(featJ, "feature.yaml"), "w").write(
        "feature_id: FEAT-07-ship-bodyfile\nstatus: in_progress\n"
        "github:\n"
        "  milestone: 7\n"
        "  parent: 40\n"
        "  parent_origin: adopted\n"
        "  attached: [T-01]\n"
        "  issues:\n"
        "    T-01: 41\n"
    )
    bodyJ = os.path.join(tmpJ, "body.txt")
    open(bodyJ, "w").write("ship review notes, signed")
    r = run(["ship", featJ, "--body-file", bodyJ], tmpJ)
    logJ = calls(tmpJ)
    commentsJ = [l for l in logJ if l.startswith("issue comment 40")]
    check("ship --body-file posts once",
          r.returncode == 0 and len(commentsJ) == 1
          and "--body-file" in commentsJ[0] and bodyJ in commentsJ[0],
          str(logJ))

# --- ship without --body-file posts nothing
with tempfile.TemporaryDirectory() as tmpK:
    install_gh(tmpK)
    featK = stage(tmpK, feat_name="FEAT-07-ship-nobodyfile")
    json.dump({"github": {"sync": True, "repo": "implentio/fake"}},
              open(os.path.join(tmpK, ".harness", "harness.json"), "w"))
    open(os.path.join(featK, "feature.yaml"), "w").write(
        "feature_id: FEAT-07-ship-nobodyfile\nstatus: in_progress\n"
        "github:\n"
        "  milestone: 7\n"
        "  parent: 40\n"
        "  parent_origin: adopted\n"
        "  attached: [T-01]\n"
        "  issues:\n"
        "    T-01: 41\n"
    )
    r = run(["ship", featK], tmpK)
    logK = calls(tmpK)
    check("ship without --body-file posts nothing",
          r.returncode == 0 and not any(l.startswith("issue comment") for l in logK),
          str(logK))

# --- ship with an empty --body-file exits 1, before any gh call beyond auth status
with tempfile.TemporaryDirectory() as tmpL:
    install_gh(tmpL)
    featL = stage(tmpL, feat_name="FEAT-07-ship-emptybodyfile")
    json.dump({"github": {"sync": True, "repo": "implentio/fake"}},
              open(os.path.join(tmpL, ".harness", "harness.json"), "w"))
    open(os.path.join(featL, "feature.yaml"), "w").write(
        "feature_id: FEAT-07-ship-emptybodyfile\nstatus: in_progress\n"
        "github:\n"
        "  milestone: 7\n"
        "  parent: 40\n"
        "  parent_origin: adopted\n"
        "  attached: [T-01]\n"
        "  issues:\n"
        "    T-01: 41\n"
    )
    emptyL = os.path.join(tmpL, "empty.txt")
    open(emptyL, "w").close()
    r = run(["ship", featL, "--body-file", emptyL], tmpL)
    logL = [l for l in calls(tmpL) if l]
    check("ship with an empty body file exits 1",
          r.returncode == 1 and all(l.startswith("auth") for l in logL),
          str(logL))

# ---------- T-06 Part C: load_recorded reads the github: block with a PARSER ----------
# Mandated by the plan and never written; found MISSING by the review panel (F-04) and
# confirmed by grep before being fixed here. Both cases are read-only — they call the
# function directly rather than driving a subcommand, because what is under test is the
# PARSE, not the GitHub calls.

import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "_ghs", os.path.join(os.path.dirname(os.path.abspath(__file__)), "gh-sync.py"))
_ghs = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_ghs)

# 1. A trailing `#` comment on parent: and milestone: — the issue #11 defect class, in
#    THIS file. The old regexes were `(\d+)`-anchored, so a commented value still
#    matched; a QUOTED one did not. Both shapes are asserted so the case cannot pass by
#    accident on the easy half.
_d1 = tempfile.mkdtemp()
open(os.path.join(_d1, "feature.yaml"), "w").write(
    "feature_id: F1\n"
    "github:\n"
    "  parent: 40        # the container issue, adopted\n"
    '  milestone: "7"    # quoted on purpose\n'
    "  parent_origin: adopted\n"
    "  attached: [T-01]\n"
    "  issues:\n"
    "    T-01: 41   # trailing comment here too\n"
)
_rec = _ghs.load_recorded(_d1)
check("T-06C: a trailing # comment on parent:/milestone:/issues does not lose the value",
      _rec["parent"] == 40 and _rec["milestone"] == 7
      and _rec["issues"] == {"T-01": 41} and _rec["attached"] == ["T-01"],
      str(_rec))

# 2. No github: block at all -> the all-None default, never a raise. gh-sync would
#    otherwise crash on any feature that has not been mirrored yet, which is most of
#    them.
_d2 = tempfile.mkdtemp()
open(os.path.join(_d2, "feature.yaml"), "w").write("feature_id: F2\nphase: plan\n")
_rec2 = _ghs.load_recorded(_d2)
check("T-06C: a feature.yaml with no github: block returns the default, does not raise",
      _rec2 == {"milestone": None, "parent": None, "parent_origin": None,
                "attached": [], "issues": {}},
      str(_rec2))

# ---------- review finding 2: save_recorded must not append a SECOND github: block ----------
# The old `^github:\s*$...` regex missed `github:   # comment` — this repo's own house
# style — so nothing was stripped and a second top-level key was appended. The strict
# loader then raised DuplicateKeyError and load_recorded turned it into SystemExit, so
# every later gh-sync died with "does not parse". Severe because save_recorded runs
# IMMEDIATELY AFTER an irreversible GitHub mutation (DEC-131), so the record that rule
# exists to preserve became unreadable.
_REC = {"milestone": 9, "parent": 40, "parent_origin": "created",
        "attached": ["T-01"], "issues": {"T-01": 41}}
for _label, _body in (
        ("bare", "feature_id: F1\ngithub:\n  parent: 40\nphase: ship\n"),
        ("trailing comment", "feature_id: F1\ngithub:   # the mirror\n  parent: 40\nphase: ship\n"),
        ("column-0 comment inside", "feature_id: F1\ngithub:\n  parent: 40\n# note\n  milestone: 9\nphase: ship\n"),
        ("no block at all", "feature_id: F1\nphase: ship\n")):
    _d = tempfile.mkdtemp()
    open(os.path.join(_d, "feature.yaml"), "w").write(_body)
    _ghs.save_recorded(_d, _REC)
    _txt = open(os.path.join(_d, "feature.yaml")).read()
    _n = sum(1 for l in _txt.split("\n") if l.split("#", 1)[0].rstrip() == "github:")
    try:
        _rt = _ghs.load_recorded(_d)
        _ok = _n == 1 and _rt["parent"] == 40 and _rt["milestone"] == 9
        _why = f"{_n} github: keys, round-trip {_rt}"
    except SystemExit as e:
        _ok, _why = False, f"load_recorded refused after save: {e}"
    check(f"finding 2: save_recorded round-trips a feature.yaml with a {_label}", _ok, _why)

print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
