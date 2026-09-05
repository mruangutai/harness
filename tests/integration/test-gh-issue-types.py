#!/usr/bin/env python3
"""gh-sync.py open must type every issue it creates with a native GitHub Issue Type
(FEAT-55, REQ-01/REQ-03/REQ-05/REQ-06/REQ-07/REQ-08/REQ-10) — against a fake `gh` that
answers the `issueTypes` capability query, `--jq .node_id` and `updateIssue` in addition
to every call `test-gh-sync.py`'s fake already answers.

RED BY DESIGN until T-04 lands: gh-sync.py is unchanged, so it never calls the
detection query, never applies a type, and never refuses. Every case below asserts the
TYPED behaviour, so every case fails against today's gh-sync.py, and this file's own
exit code is non-zero until then.

    ./test-gh-issue-types.py    -> exit 0 all pass, 1 otherwise (must be 1 today)

Cases (each is CASE <letter> in a `check()` message, grepped by T-03's verify):
  A/B  available types: per-issue type ids (D-18) and label suppression, one run.
  C/D  absent types: today's labels unchanged, zero updateIssue, one diagnostic line,
       and the same on a rerun that creates nothing.
  E    github.issue_types override, all four legal keys, one run.
  F    a pre-seeded "created" remnant does not make an empty backfill set look clean —
       Task is still missing for creation, so the run must refuse before ANY create or
       apply, and the remnant must be untouched.
  G    a failed type-apply demotes nothing: "created" stays "created"; the rerun
       backfills to True without creating, closing or deleting anything.
  H/H2 an adopted --parent is never typed, this run or any later one.
  I    a failed capability query never gates: exit 0, today's labels, one diagnostic.
  J    absent provenance (a feature.json predating this feature) is NEVER typed, not
       now and not on a later run — the fail-safe direction of D-20.
  K    the discriminating case: every issue this run WOULD CREATE has a declared type,
       so refusal can only come from the backfill needing an undeclared type.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
SYNC = os.path.join(BIN_DIR, "gh-sync.py")

# The four sub-issue tasks: one of each change_type this feature cares about, in plan
# order — bugfix maps to Bug, the other three all map to Task (D-18: a task sub-issue
# is never typed Feature, whatever its change_type spells).
TASKS = [
    ("T-01", "bugfix", "fix the off-by-one in export"),
    ("T-02", "config", "add sync toggle to harness.json"),
    ("T-03", "logic", "rewire the retry loop"),
    ("T-04", "feature", "add CSV export button"),
]

FAKE_GH_TYPES = """#!/bin/bash
echo "$*" | tr '\n' '\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
case "$*" in
  *"issueTypes"*)
    case "$FAKE_TYPES" in
      available)
        printf '{"data":{"repository":{"issueTypes":{"nodes":[{"id":"IT_bug","name":"Bug"},{"id":"IT_feature","name":"Feature"},{"id":"IT_task","name":"Task"},{"id":"IT_defect","name":"Defect"},{"id":"IT_epic","name":"Epic"},{"id":"IT_maintenance","name":"Maintenance"}]}}}}\\n'
        exit 0 ;;
      partial)
        printf '{"data":{"repository":{"issueTypes":{"nodes":[{"id":"IT_bug","name":"Bug"},{"id":"IT_feature","name":"Feature"}]}}}}\\n'
        exit 0 ;;
      nobug)
        printf '{"data":{"repository":{"issueTypes":{"nodes":[{"id":"IT_feature","name":"Feature"},{"id":"IT_task","name":"Task"}]}}}}\\n'
        exit 0 ;;
      failed)
        printf '{"data":{"repository":null},"errors":[{"message":"Could not resolve to a Repository"}]}\\n'
        exit 1 ;;
      *)
        printf '{"data":{"repository":{"issueTypes":null}}}\\n'
        exit 0 ;;
    esac ;;
  *"--jq .node_id"*)
    num=$(echo "$*" | grep -oE 'issues/[0-9]+' | head -1 | grep -oE '[0-9]+')
    echo "I_node$num"
    exit 0 ;;
  *"updateIssue"*)
    if [ "$FAKE_TYPE_APPLY" = "fail" ]; then
      echo "simulated type-apply failure" >&2
      exit 1
    fi
    echo '{"data":{"updateIssue":{"issue":{"id":"I_node"}}}}'
    exit 0 ;;
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
  "issue delete") exit 0 ;;
  "label create") exit 0 ;;
esac
exit 0
"""


def install_gh(tmp, script=FAKE_GH_TYPES):
    gh_path = os.path.join(tmp, "gh")
    open(gh_path, "w").write(script)
    os.chmod(gh_path, 0o755)


def build_brief(feat_dir, feat_name):
    with open(os.path.join(feat_dir, "BRIEF.md"), "w", encoding="utf-8") as f:
        f.write(f"""# BRIEF — {feat_name} — issue type coverage

## Problem
Issues created by gh-sync carry only labels, never a native Issue Type.

## Goal
Type every issue gh-sync creates.

## Requirements
- REQ-01: every created issue is typed.

## Success Criteria
- SC-01: type ids match the role. verify: automated

## Approval

status: approved
""")


def build_plan_yaml(feat_dir, feat_name, source_issues=None):
    lines = ["schema: plan/1", f"feature: {feat_name}", "status: building"]
    if source_issues:
        lines.append("source_issues: [" + ", ".join(str(n) for n in source_issues) + "]")
    lines.append("tasks:")
    for tid, change_type, title in TASKS:
        lines += [
            f"  - id: {tid}",
            f"    title: {title}",
            f"    change_type: {change_type}",
            "    execution_mode: team",
            "    files:",
            "      - a.py",
            "    verify: |",
            "      true",
            "    intent: |",
            "      x",
        ]
    with open(os.path.join(feat_dir, "plan.yaml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def build_harness_json(tmp, repo, issue_types):
    g = {"sync": True, "board": None, "repo": repo}
    if issue_types:
        g["issue_types"] = issue_types
    os.makedirs(os.path.join(tmp, ".harness"), exist_ok=True)
    with open(os.path.join(tmp, ".harness", "harness.json"), "w", encoding="utf-8") as f:
        json.dump({"github": g}, f)


def build_feature_json(feat_dir, github):
    doc = {"feature_id": os.path.basename(feat_dir), "status": "Building"}
    if github is not None:
        doc["github"] = github
    with open(os.path.join(feat_dir, "feature.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f)


def stage(tmp, feat_name="FEAT-77-types", repo="owner/name", issue_types=None,
          github=None, source_issues=None):
    """A feature directory with a BRIEF, a four-task plan.yaml (one of each change_type
    this feature cares about) and a github.sync-enabled harness.json — the fixture every
    case below builds on, optionally pre-seeded with a `github` feature.json block."""
    feat_dir = os.path.join(tmp, ".harness", "features", feat_name)
    os.makedirs(feat_dir)
    build_brief(feat_dir, feat_name)
    build_plan_yaml(feat_dir, feat_name, source_issues)
    build_harness_json(tmp, repo, issue_types)
    build_feature_json(feat_dir, github)
    return feat_dir


def run(feat_dir, tmp, env_extra=None, log="calls.log", extra_args=None):
    env = dict(os.environ)
    env["FAKE_LOG"] = os.path.join(tmp, log)
    env["GH_SYNC_GH"] = os.path.join(tmp, "gh")
    env.update(env_extra or {})
    args = ["open", feat_dir] + (extra_args or [])
    return subprocess.run([SYNC] + args, capture_output=True, text=True, env=env)


def calls(tmp, log="calls.log"):
    p = os.path.join(tmp, log)
    return ([l.rstrip("\x01") for l in
              open(p, encoding="utf-8", errors="replace").read().splitlines()]
            if os.path.exists(p) else [])


def read_feature_json(feat_dir):
    with open(os.path.join(feat_dir, "feature.json"), encoding="utf-8") as f:
        return json.load(f)


def labels_of(argv_line):
    return re.findall(r"--label (\S+)", argv_line)


def nth(lst, i):
    return lst[i] if 0 <= i < len(lst) else ""


fails = 0


def check(name, cond, detail=""):
    global fails
    if cond:
        print(f"ok    {name}")
    else:
        fails += 1
        print(f"FAIL  {name}\n      {detail}")


def case_a_b():
    """CASE A / CASE B, one run, FAKE_TYPES=available."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp)
        feat_dir = stage(tmp)
        run(feat_dir, tmp, {"FAKE_TYPES": "available"})
        log = calls(tmp)
        updates = [l for l in log if "updateIssue" in l]
        expectations = [
            ("parent", "I_node41", "IT_feature"),
            ("T-01 bugfix", "I_node42", "IT_bug"),
            ("T-02 config", "I_node43", "IT_task"),
            ("T-03 logic", "I_node44", "IT_task"),
            ("T-04 feature", "I_node45", "IT_task"),
        ]
        for label, node, type_id in expectations:
            check(f"CASE A: {label} is typed {type_id}",
                  any(node in l and type_id in l for l in updates), f"updates={updates}")

        creates = [l for l in log if "issue create" in l]
        check("CASE B: no create argv carries --label bug",
              not any("--label bug" in l for l in creates), f"{creates}")
        check("CASE B: no create argv carries --label chore",
              not any("--label chore" in l for l in creates), f"{creates}")
        check("CASE B: every create argv carries --label harness",
              bool(creates) and all("--label harness" in l for l in creates), f"{creates}")
        check("CASE B: the four sub-issue creates still carry --milestone FEAT-77-types",
              len(creates) >= 5 and all("--milestone FEAT-77-types" in l for l in creates[1:5]),
              f"{creates}")


def case_c_d():
    """CASE C: FAKE_TYPES=absent, fresh fixture. CASE D: rerun, same directory."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp)
        feat_dir = stage(tmp)
        r1 = run(feat_dir, tmp, {"FAKE_TYPES": "absent"}, log="calls1.log")
        log1 = calls(tmp, "calls1.log")
        creates1 = [l for l in log1 if "issue create" in l]
        check("CASE C: five issues created", len(creates1) == 5, f"{creates1}")
        check("CASE C: parent labels are exactly harness",
              labels_of(nth(creates1, 0)) == ["harness"], nth(creates1, 0))
        check("CASE C: bugfix labels are exactly harness, bug",
              labels_of(nth(creates1, 1)) == ["harness", "bug"], nth(creates1, 1))
        check("CASE C: config labels are exactly harness, chore",
              labels_of(nth(creates1, 2)) == ["harness", "chore"], nth(creates1, 2))
        check("CASE C: logic labels are exactly harness",
              labels_of(nth(creates1, 3)) == ["harness"], nth(creates1, 3))
        check("CASE C: feature labels are exactly harness",
              labels_of(nth(creates1, 4)) == ["harness"], nth(creates1, 4))
        check("CASE C: zero updateIssue argv reached the fake",
              not any("updateIssue" in l for l in log1), f"{log1}")
        lines1 = re.findall(r"^gh-sync: issue types ", r1.stdout, re.M)
        check("CASE C: exactly one 'gh-sync: issue types ' line for a five-issue run",
              len(lines1) == 1, repr(r1.stdout))

        r2 = run(feat_dir, tmp, {"FAKE_TYPES": "absent"}, log="calls2.log")
        log2 = calls(tmp, "calls2.log")
        check("CASE D: zero issue create argv on the rerun (everything already recorded)",
              not any("issue create" in l for l in log2), f"{log2}")
        lines2 = re.findall(r"^gh-sync: issue types ", r2.stdout, re.M)
        check("CASE D: still exactly one 'gh-sync: issue types ' line on the rerun",
              len(lines2) == 1, repr(r2.stdout))


def case_e():
    """CASE E: FAKE_TYPES=available with a github.issue_types override on all four keys."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp)
        feat_dir = stage(tmp, issue_types={
            "Bug": "Defect", "Task": "Maintenance", "parent": "Epic",
        })
        run(feat_dir, tmp, {"FAKE_TYPES": "available"})
        log = calls(tmp)
        updates = [l for l in log if "updateIssue" in l]
        expectations = [
            ("parent -> Epic (override key parent)", "I_node41", "IT_epic"),
            ("T-01 bugfix -> Defect (override key Bug)", "I_node42", "IT_defect"),
            ("T-02 config -> Maintenance (override key Task)", "I_node43", "IT_maintenance"),
            ("T-03 logic -> Maintenance (override key Task)", "I_node44", "IT_maintenance"),
            ("T-04 feature -> Maintenance (override key Task)", "I_node45", "IT_maintenance"),
        ]
        for label, node, type_id in expectations:
            check(f"CASE E: {label}", any(node in l and type_id in l for l in updates),
                  f"updates={updates}")


def case_f():
    """CASE F: FAKE_TYPES=partial (Task undeclared), one already-recorded 'created'
    remnant (bugfix #501) so the backfill set is not empty — the run must still refuse
    on Task, before any create and before any apply, and the remnant must be untouched."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp)
        feat_dir = stage(tmp, github={
            "milestone": None, "parent": None, "attached": [], "source_issues": [],
            "issues": {"T-01": 501}, "typed": {"T-01": "created"},
        })
        r = run(feat_dir, tmp, {"FAKE_TYPES": "partial"})
        log = calls(tmp)
        both = r.stdout + r.stderr
        check("CASE F: the run refuses (non-zero exit)", r.returncode != 0,
              f"exit={r.returncode} out={both}")
        check("CASE F: zero issue create argv reached the fake",
              not any("issue create" in l for l in log), f"{log}")
        check("CASE F: zero updateIssue argv reached the fake",
              not any("updateIssue" in l for l in log), f"{log}")
        check("CASE F: zero updateIssue argv carries a node id derived from the remnant 501",
              not any("updateIssue" in l and "I_node501" in l for l in log), f"{log}")
        check("CASE F: the refusal names both Task and github.issue_types",
              "Task" in both and "github.issue_types" in both, both)
        rec = read_feature_json(feat_dir).get("github", {})
        check("CASE F: the remnant's issue number is unchanged (501)",
              rec.get("issues", {}).get("T-01") == 501, f"{rec}")
        check("CASE F: the remnant's provenance is still exactly 'created'",
              rec.get("typed", {}).get("T-01") == "created", f"{rec}")


def case_g():
    """CASE G: FAKE_TYPE_APPLY=fail on the first run demotes nothing; the rerun
    backfills to True without creating, closing or deleting anything."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp)
        feat_dir = stage(tmp)
        run(feat_dir, tmp, {"FAKE_TYPES": "available", "FAKE_TYPE_APPLY": "fail"},
            log="calls1.log")
        rec1 = read_feature_json(feat_dir).get("github", {})
        check("CASE G: T-01's typed value is 'created' after a failed type-apply",
              rec1.get("typed", {}).get("T-01") == "created", f"{rec1}")
        check("CASE G: T-01's typed value is not True after a failed type-apply",
              rec1.get("typed", {}).get("T-01") is not True, f"{rec1}")

        run(feat_dir, tmp, {"FAKE_TYPES": "available"}, log="calls2.log")
        log2 = calls(tmp, "calls2.log")
        number = rec1.get("issues", {}).get("T-01")
        node = f"I_node{number}" if number is not None else "I_node__missing__"
        check("CASE G: the rerun creates no issue for the already-recorded T-01",
              not any("issue create" in l and "T-01" in l for l in log2), f"{log2}")
        check("CASE G: the rerun contains no issue delete argv anywhere",
              not any("issue delete" in l for l in log2), f"{log2}")
        check("CASE G: the rerun contains no issue close argv anywhere",
              not any("issue close" in l for l in log2), f"{log2}")
        check("CASE G: the rerun's log carries an updateIssue call for T-01's recorded node id",
              any("updateIssue" in l and node in l for l in log2), f"{log2}")
        rec2 = read_feature_json(feat_dir).get("github", {})
        check("CASE G: T-01's typed value is promoted to True after the backfill",
              rec2.get("typed", {}).get("T-01") is True, f"{rec2}")


def case_h_h2():
    """CASE H: --parent 4242 is adopted, never typed, and its provenance reads
    'adopted'. CASE H2: a rerun without --parent must skip it forever, not once."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp)
        feat_dir = stage(tmp, source_issues=[100, 200])
        run(feat_dir, tmp, {"FAKE_TYPES": "available"}, log="calls1.log",
            extra_args=["--parent", "4242"])
        log1 = calls(tmp, "calls1.log")
        check("CASE H: no updateIssue argv carries a node id derived from adopted parent 4242",
              not any("updateIssue" in l and "I_node4242" in l for l in log1), f"{log1}")
        for n in (100, 200):
            check(f"CASE H: no updateIssue argv carries a node id derived from source_issues #{n}",
                  not any("updateIssue" in l and f"I_node{n}" in l for l in log1), f"{log1}")
        rec1 = read_feature_json(feat_dir).get("github", {})
        check("CASE H: the parent's typed provenance is recorded as 'adopted'",
              rec1.get("typed", {}).get("parent") == "adopted", f"{rec1}")

        run(feat_dir, tmp, {"FAKE_TYPES": "available"}, log="calls2.log")
        log2 = calls(tmp, "calls2.log")
        check("CASE H2: the rerun without --parent still emits zero updateIssue for 4242",
              not any("updateIssue" in l and "I_node4242" in l for l in log2), f"{log2}")
        rec2 = read_feature_json(feat_dir).get("github", {})
        check("CASE H2: the parent's typed provenance stays exactly 'adopted' across the rerun",
              rec2.get("typed", {}).get("parent") == "adopted", f"{rec2}")


def case_i():
    """CASE I: FAKE_TYPES=failed never gates — exit 0, today's labels, one diagnostic."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp)
        feat_dir = stage(tmp)
        r = run(feat_dir, tmp, {"FAKE_TYPES": "failed"})
        log = calls(tmp)
        creates = [l for l in log if "issue create" in l]
        check("CASE I: the run still exits 0 when type detection fails",
              r.returncode == 0, f"exit={r.returncode} stderr={r.stderr}")
        check("CASE I: issues are still created (five, today's labels)",
              len(creates) == 5, f"{creates}")
        check("CASE I: bugfix create still carries --label bug",
              "--label bug" in nth(creates, 1), nth(creates, 1))
        check("CASE I: config create still carries --label chore",
              "--label chore" in nth(creates, 2), nth(creates, 2))
        lines = re.findall(r"^gh-sync: issue types ", r.stdout, re.M)
        check("CASE I: exactly one 'gh-sync: issue types ' line is printed",
              len(lines) == 1, repr(r.stdout))


def case_j():
    """CASE J: absent provenance is never typed — the legacy feature.json shape, no
    github.typed key at all, and the fail-safe direction stays true across a rerun."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp)
        feat_dir = stage(tmp, github={
            "milestone": None, "parent": 9001, "attached": ["T-01"],
            "issues": {"T-01": 9002}, "source_issues": [],
        })
        r1 = run(feat_dir, tmp, {"FAKE_TYPES": "available"}, log="calls1.log")
        log1 = calls(tmp, "calls1.log")
        check("CASE J: zero updateIssue argv carries a node id derived from legacy parent 9001",
              not any("updateIssue" in l and "I_node9001" in l for l in log1), f"{log1}")
        check("CASE J: zero updateIssue argv carries a node id derived from legacy T-01 9002",
              not any("updateIssue" in l and "I_node9002" in l for l in log1), f"{log1}")
        rec1 = read_feature_json(feat_dir).get("github", {})
        check("CASE J: github.typed has no entry for 'parent' after the first run",
              "parent" not in rec1.get("typed", {}), f"{rec1}")
        check("CASE J: github.typed has no entry for T-01 after the first run",
              "T-01" not in rec1.get("typed", {}), f"{rec1}")
        check("CASE J: the first run still exits 0", r1.returncode == 0,
              f"exit={r1.returncode} stderr={r1.stderr}")
        creates1 = [l for l in log1 if "issue create" in l]
        check("CASE J: the first run still creates the three tasks that are not recorded",
              len(creates1) == 3, f"{creates1}")

        r2 = run(feat_dir, tmp, {"FAKE_TYPES": "available"}, log="calls2.log")
        log2 = calls(tmp, "calls2.log")
        check("CASE J: zero updateIssue for 9001 on the rerun too",
              not any("updateIssue" in l and "I_node9001" in l for l in log2), f"{log2}")
        check("CASE J: zero updateIssue for 9002 on the rerun too",
              not any("updateIssue" in l and "I_node9002" in l for l in log2), f"{log2}")
        rec2 = read_feature_json(feat_dir).get("github", {})
        check("CASE J: github.typed still has no entry for 'parent' after the rerun",
              "parent" not in rec2.get("typed", {}), f"{rec2}")
        check("CASE J: github.typed still has no entry for T-01 after the rerun",
              "T-01" not in rec2.get("typed", {}), f"{rec2}")
        check("CASE J: the rerun still exits 0", r2.returncode == 0,
              f"exit={r2.returncode} stderr={r2.stderr}")


def case_k():
    """CASE K: FAKE_TYPES=nobug. Every issue this run WOULD CREATE has a declared
    type (parent -> Feature, every task -> Task); only the already-recorded 'created'
    remnant (bugfix #502) needs the undeclared Bug, so refusal can only come from the
    backfill's required set, never from the creation-side check alone."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp)
        feat_dir = stage(tmp, github={
            "milestone": None, "parent": None, "attached": [], "source_issues": [],
            "issues": {"T-01": 502}, "typed": {"T-01": "created"},
        })
        r = run(feat_dir, tmp, {"FAKE_TYPES": "nobug"})
        log = calls(tmp)
        both = r.stdout + r.stderr
        check("CASE K: the run refuses (non-zero exit) though nothing to be CREATED needs Bug",
              r.returncode != 0, f"exit={r.returncode} out={both}")
        check("CASE K: zero issue create argv reached the fake",
              not any("issue create" in l for l in log), f"{log}")
        check("CASE K: zero updateIssue argv reached the fake",
              not any("updateIssue" in l for l in log), f"{log}")
        check("CASE K: zero updateIssue argv carries a node id derived from the remnant 502",
              not any("updateIssue" in l and "I_node502" in l for l in log), f"{log}")
        check("CASE K: the refusal names both Bug and github.issue_types",
              "Bug" in both and "github.issue_types" in both, both)
        rec = read_feature_json(feat_dir).get("github", {})
        check("CASE K: the remnant's issue number is unchanged (502)",
              rec.get("issues", {}).get("T-01") == 502, f"{rec}")
        check("CASE K: the remnant's provenance is still exactly 'created'",
              rec.get("typed", {}).get("T-01") == "created", f"{rec}")


case_a_b()
case_c_d()
case_e()
case_f()
case_g()
case_h_h2()
case_i()
case_j()
case_k()

print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
