#!/usr/bin/env python3
"""gh-sync.py open must type every issue it creates with a native GitHub Issue Type
(FEAT-55, REQ-01/REQ-03/REQ-05/REQ-06/REQ-07/REQ-08/REQ-10) — against a fake `gh` that
answers the `issueTypes` capability query, `--jq .node_id` and `updateIssue` in addition
to every call `test-gh-sync.py`'s fake already answers.

Every case asserts the TYPED behaviour. The cases share nothing (each has its own temporary
directory, fake and env), so they run concurrently and their checks print in case order.

    ./test-gh-issue-types.py    -> exit 0 all pass, 1 otherwise

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
from integration_support import BIN  # noqa: E402  (puts bin/ and tests/ on sys.path)
from check_support import Checks  # noqa: E402
from gh_sync_support import FAKE_GH, calls, install_gh, write_feature_json  # noqa: E402
from harness_config_support import write_config  # noqa: E402
from offline_gh_support import assert_sentinel_unused, offline_gh_env  # noqa: E402
import contextlib
import json
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

SYNC = str(BIN / "gh-sync.py")

# The four sub-issue tasks: one of each change_type this feature cares about, in plan
# order — bugfix maps to Bug, the other three all map to Task (D-18: a task sub-issue
# is never typed Feature, whatever its change_type spells).
TASKS = [
    ("T-01", "bugfix", "fix the off-by-one in export"),
    ("T-02", "config", "add sync toggle to harness.json"),
    ("T-03", "logic", "rewire the retry loop"),
    ("T-04", "feature", "add CSV export button"),
]

# The node ids the fake hands the five issues a fresh run creates (#41 parent, #42-#45 tasks).
NODES = ["I_node41", "I_node42", "I_node43", "I_node44", "I_node45"]

# The issue-type branches this file adds in front of the shared fake's own: the `issueTypes`
# capability query (shaped by FAKE_TYPES), `--jq .node_id` and `updateIssue`.
TYPE_BRANCHES = """  *"issueTypes"*)
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
"""
_CASE_HEAD = 'case "$*" in\n'
FAKE_GH_TYPES = FAKE_GH.replace(_CASE_HEAD, _CASE_HEAD + TYPE_BRANCHES, 1)
assert TYPE_BRANCHES in FAKE_GH_TYPES, "shared FAKE_GH lost its case anchor"


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
    write_config(os.path.join(tmp, ".harness", "harness.json"), {"github": g})


def stage(tmp, feat_name="FEAT-77-types", repo="owner/name", issue_types=None,
          github=None, source_issues=None):
    """A feature directory with a BRIEF, a four-task plan.yaml (one of each change_type
    this feature cares about) and a github.sync-enabled harness.json — the fixture every
    case below builds on, optionally pre-seeded with a `github` feature.json block (its
    repo filled from harness.json)."""
    feat_dir = os.path.join(tmp, ".harness", "features", feat_name)
    os.makedirs(feat_dir)
    build_brief(feat_dir, feat_name)
    build_plan_yaml(feat_dir, feat_name, source_issues)
    build_harness_json(tmp, repo, issue_types)
    extra = {} if github is None else {"github": github}
    write_feature_json(os.path.join(feat_dir, "feature.json"), feature_id=feat_name, **extra)
    return feat_dir


@contextlib.contextmanager
def staged(**kw):
    """A fresh temporary directory with FAKE_GH_TYPES installed; yields (tmp, stage(tmp, **kw))."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp, FAKE_GH_TYPES)
        yield tmp, stage(tmp, **kw)


def run(feat_dir, tmp, env_extra=None, log="calls.log", extra_args=None):
    env, sentinel_log = offline_gh_env(os.path.join(tmp, "gh"), tmp)
    env["FAKE_LOG"] = os.path.join(tmp, log)
    env.update(env_extra or {})
    args = ["open", feat_dir] + (extra_args or [])
    result = subprocess.run([SYNC] + args, capture_output=True, text=True, env=env)
    assert_sentinel_unused(sentinel_log)
    return result


def read_feature_json(feat_dir):
    with open(os.path.join(feat_dir, "feature.json"), encoding="utf-8") as f:
        return json.load(f)


def argv(log, *needles):
    """The logged gh argv lines that contain every one of NEEDLES."""
    return [line for line in log if all(n in line for n in needles)]


def labels_of(argv_line):
    return re.findall(r"--label (\S+)", argv_line)


def nth(lst, i):
    return lst[i] if 0 <= i < len(lst) else ""


def case_a_b(check):
    """CASE A / CASE B, one run, FAKE_TYPES=available."""
    with staged() as (tmp, feat_dir):
        run(feat_dir, tmp, {"FAKE_TYPES": "available"})
        log = calls(tmp, strip=True)
        updates = argv(log, "updateIssue")
        expectations = [
            ("parent", "IT_feature"),
            ("T-01 bugfix", "IT_bug"),
            ("T-02 config", "IT_task"),
            ("T-03 logic", "IT_task"),
            ("T-04 feature", "IT_task"),
        ]
        for (label, type_id), node in zip(expectations, NODES):
            check(f"CASE A: {label} is typed {type_id}",
                  argv(updates, node, type_id), f"updates={updates}")

        creates = argv(log, "issue create")
        check("CASE B: no create argv carries --label bug",
              not argv(creates, "--label bug"), f"{creates}")
        check("CASE B: no create argv carries --label chore",
              not argv(creates, "--label chore"), f"{creates}")
        check("CASE B: every create argv carries --label harness",
              bool(creates) and all("--label harness" in l for l in creates), f"{creates}")
        check("CASE B: the four sub-issue creates still carry --milestone FEAT-77-types",
              len(creates) >= 5 and all("--milestone FEAT-77-types" in l for l in creates[1:5]),
              f"{creates}")


def case_c_d(check):
    """CASE C: FAKE_TYPES=absent, fresh fixture. CASE D: rerun, same directory."""
    with staged() as (tmp, feat_dir):
        r1 = run(feat_dir, tmp, {"FAKE_TYPES": "absent"}, log="calls1.log")
        log1 = calls(tmp, "calls1.log", strip=True)
        creates1 = argv(log1, "issue create")
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
              not argv(log1, "updateIssue"), f"{log1}")
        lines1 = re.findall(r"^gh-sync: issue types ", r1.stdout, re.M)
        check("CASE C: exactly one 'gh-sync: issue types ' line for a five-issue run",
              len(lines1) == 1, repr(r1.stdout))

        r2 = run(feat_dir, tmp, {"FAKE_TYPES": "absent"}, log="calls2.log")
        log2 = calls(tmp, "calls2.log", strip=True)
        check("CASE D: zero issue create argv on the rerun (everything already recorded)",
              not argv(log2, "issue create"), f"{log2}")
        lines2 = re.findall(r"^gh-sync: issue types ", r2.stdout, re.M)
        check("CASE D: still exactly one 'gh-sync: issue types ' line on the rerun",
              len(lines2) == 1, repr(r2.stdout))


def case_e(check):
    """CASE E: FAKE_TYPES=available with a github.issue_types override on all four keys."""
    with staged(issue_types={"Bug": "Defect", "Task": "Maintenance", "parent": "Epic"}) as (
            tmp, feat_dir):
        run(feat_dir, tmp, {"FAKE_TYPES": "available"})
        updates = argv(calls(tmp, strip=True), "updateIssue")
        expectations = [
            ("parent -> Epic (override key parent)", "IT_epic"),
            ("T-01 bugfix -> Defect (override key Bug)", "IT_defect"),
            ("T-02 config -> Maintenance (override key Task)", "IT_maintenance"),
            ("T-03 logic -> Maintenance (override key Task)", "IT_maintenance"),
            ("T-04 feature -> Maintenance (override key Task)", "IT_maintenance"),
        ]
        for (label, type_id), node in zip(expectations, NODES):
            check(f"CASE E: {label}", argv(updates, node, type_id), f"updates={updates}")


def case_f(check):
    """CASE F: FAKE_TYPES=partial (Task undeclared), one already-recorded 'created'
    remnant (bugfix #501) so the backfill set is not empty — the run must still refuse
    on Task, before any create and before any apply, and the remnant must be untouched."""
    with staged(github={
        "milestone": None, "parent": None, "attached": [], "source_issues": [],
        "issues": {"T-01": 501}, "typed": {"T-01": "created"},
    }) as (tmp, feat_dir):
        r = run(feat_dir, tmp, {"FAKE_TYPES": "partial"})
        log = calls(tmp, strip=True)
        both = r.stdout + r.stderr
        check("CASE F: the run refuses (non-zero exit)", r.returncode != 0,
              f"exit={r.returncode} out={both}")
        check("CASE F: zero issue create argv reached the fake",
              not argv(log, "issue create"), f"{log}")
        check("CASE F: zero updateIssue argv reached the fake",
              not argv(log, "updateIssue"), f"{log}")
        check("CASE F: zero updateIssue argv carries a node id derived from the remnant 501",
              not argv(log, "updateIssue", "I_node501"), f"{log}")
        check("CASE F: the refusal names both Task and github.issue_types",
              "Task" in both and "github.issue_types" in both, both)
        rec = read_feature_json(feat_dir).get("github", {})
        check("CASE F: the remnant's issue number is unchanged (501)",
              rec.get("issues", {}).get("T-01") == 501, f"{rec}")
        check("CASE F: the remnant's provenance is still exactly 'created'",
              rec.get("typed", {}).get("T-01") == "created", f"{rec}")


def case_g(check):
    """CASE G: FAKE_TYPE_APPLY=fail on the first run demotes nothing; the rerun
    backfills to True without creating, closing or deleting anything."""
    with staged() as (tmp, feat_dir):
        run(feat_dir, tmp, {"FAKE_TYPES": "available", "FAKE_TYPE_APPLY": "fail"},
            log="calls1.log")
        rec1 = read_feature_json(feat_dir).get("github", {})
        check("CASE G: T-01's typed value is 'created' after a failed type-apply",
              rec1.get("typed", {}).get("T-01") == "created", f"{rec1}")
        check("CASE G: T-01's typed value is not True after a failed type-apply",
              rec1.get("typed", {}).get("T-01") is not True, f"{rec1}")

        run(feat_dir, tmp, {"FAKE_TYPES": "available"}, log="calls2.log")
        log2 = calls(tmp, "calls2.log", strip=True)
        number = rec1.get("issues", {}).get("T-01")
        node = f"I_node{number}" if number is not None else "I_node__missing__"
        check("CASE G: the rerun creates no issue for the already-recorded T-01",
              not argv(log2, "issue create", "T-01"), f"{log2}")
        check("CASE G: the rerun contains no issue delete argv anywhere",
              not argv(log2, "issue delete"), f"{log2}")
        check("CASE G: the rerun contains no issue close argv anywhere",
              not argv(log2, "issue close"), f"{log2}")
        check("CASE G: the rerun's log carries an updateIssue call for T-01's recorded node id",
              argv(log2, "updateIssue", node), f"{log2}")
        rec2 = read_feature_json(feat_dir).get("github", {})
        check("CASE G: T-01's typed value is promoted to True after the backfill",
              rec2.get("typed", {}).get("T-01") is True, f"{rec2}")


def case_h_h2(check):
    """CASE H: --parent 4242 is adopted, never typed, and its provenance reads
    'adopted'. CASE H2: a rerun without --parent must skip it forever, not once."""
    with staged(source_issues=[100, 200]) as (tmp, feat_dir):
        run(feat_dir, tmp, {"FAKE_TYPES": "available"}, log="calls1.log",
            extra_args=["--parent", "4242"])
        log1 = calls(tmp, "calls1.log", strip=True)
        check("CASE H: no updateIssue argv carries a node id derived from adopted parent 4242",
              not argv(log1, "updateIssue", "I_node4242"), f"{log1}")
        for n in (100, 200):
            check(f"CASE H: no updateIssue argv carries a node id derived from source_issues #{n}",
                  not argv(log1, "updateIssue", f"I_node{n}"), f"{log1}")
        rec1 = read_feature_json(feat_dir).get("github", {})
        check("CASE H: the parent's typed provenance is recorded as 'adopted'",
              rec1.get("typed", {}).get("parent") == "adopted", f"{rec1}")

        run(feat_dir, tmp, {"FAKE_TYPES": "available"}, log="calls2.log")
        log2 = calls(tmp, "calls2.log", strip=True)
        check("CASE H2: the rerun without --parent still emits zero updateIssue for 4242",
              not argv(log2, "updateIssue", "I_node4242"), f"{log2}")
        rec2 = read_feature_json(feat_dir).get("github", {})
        check("CASE H2: the parent's typed provenance stays exactly 'adopted' across the rerun",
              rec2.get("typed", {}).get("parent") == "adopted", f"{rec2}")


def case_i(check):
    """CASE I: FAKE_TYPES=failed never gates — exit 0, today's labels, one diagnostic."""
    with staged() as (tmp, feat_dir):
        r = run(feat_dir, tmp, {"FAKE_TYPES": "failed"})
        creates = argv(calls(tmp, strip=True), "issue create")
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


def case_j(check):
    """CASE J: absent provenance is never typed — the legacy feature.json shape, no
    github.typed key at all, and the fail-safe direction stays true across a rerun."""
    with staged(github={
        "milestone": None, "parent": 9001, "attached": ["T-01"],
        "issues": {"T-01": 9002}, "source_issues": [],
    }) as (tmp, feat_dir):
        r1 = run(feat_dir, tmp, {"FAKE_TYPES": "available"}, log="calls1.log")
        log1 = calls(tmp, "calls1.log", strip=True)
        check("CASE J: zero updateIssue argv carries a node id derived from legacy parent 9001",
              not argv(log1, "updateIssue", "I_node9001"), f"{log1}")
        check("CASE J: zero updateIssue argv carries a node id derived from legacy T-01 9002",
              not argv(log1, "updateIssue", "I_node9002"), f"{log1}")
        rec1 = read_feature_json(feat_dir).get("github", {})
        check("CASE J: github.typed has no entry for 'parent' after the first run",
              "parent" not in rec1.get("typed", {}), f"{rec1}")
        check("CASE J: github.typed has no entry for T-01 after the first run",
              "T-01" not in rec1.get("typed", {}), f"{rec1}")
        check("CASE J: the first run still exits 0", r1.returncode == 0,
              f"exit={r1.returncode} stderr={r1.stderr}")
        creates1 = argv(log1, "issue create")
        check("CASE J: the first run still creates the three tasks that are not recorded",
              len(creates1) == 3, f"{creates1}")

        r2 = run(feat_dir, tmp, {"FAKE_TYPES": "available"}, log="calls2.log")
        log2 = calls(tmp, "calls2.log", strip=True)
        check("CASE J: zero updateIssue for 9001 on the rerun too",
              not argv(log2, "updateIssue", "I_node9001"), f"{log2}")
        check("CASE J: zero updateIssue for 9002 on the rerun too",
              not argv(log2, "updateIssue", "I_node9002"), f"{log2}")
        rec2 = read_feature_json(feat_dir).get("github", {})
        check("CASE J: github.typed still has no entry for 'parent' after the rerun",
              "parent" not in rec2.get("typed", {}), f"{rec2}")
        check("CASE J: github.typed still has no entry for T-01 after the rerun",
              "T-01" not in rec2.get("typed", {}), f"{rec2}")
        check("CASE J: the rerun still exits 0", r2.returncode == 0,
              f"exit={r2.returncode} stderr={r2.stderr}")


def case_k(check):
    """CASE K: FAKE_TYPES=nobug. Every issue this run WOULD CREATE has a declared
    type (parent -> Feature, every task -> Task); only the already-recorded 'created'
    remnant (bugfix #502) needs the undeclared Bug, so refusal can only come from the
    backfill's required set, never from the creation-side check alone."""
    with staged(github={
        "milestone": None, "parent": None, "attached": [], "source_issues": [],
        "issues": {"T-01": 502}, "typed": {"T-01": "created"},
    }) as (tmp, feat_dir):
        r = run(feat_dir, tmp, {"FAKE_TYPES": "nobug"})
        log = calls(tmp, strip=True)
        both = r.stdout + r.stderr
        check("CASE K: the run refuses (non-zero exit) though nothing to be CREATED needs Bug",
              r.returncode != 0, f"exit={r.returncode} out={both}")
        check("CASE K: zero issue create argv reached the fake",
              not argv(log, "issue create"), f"{log}")
        check("CASE K: zero updateIssue argv reached the fake",
              not argv(log, "updateIssue"), f"{log}")
        check("CASE K: zero updateIssue argv carries a node id derived from the remnant 502",
              not argv(log, "updateIssue", "I_node502"), f"{log}")
        check("CASE K: the refusal names both Bug and github.issue_types",
              "Bug" in both and "github.issue_types" in both, both)
        rec = read_feature_json(feat_dir).get("github", {})
        check("CASE K: the remnant's issue number is unchanged (502)",
              rec.get("issues", {}).get("T-01") == 502, f"{rec}")
        check("CASE K: the remnant's provenance is still exactly 'created'",
              rec.get("typed", {}).get("T-01") == "created", f"{rec}")


CASES = [case_a_b, case_c_d, case_e, case_f, case_g, case_h_h2, case_i, case_j, case_k]


def recorded(case):
    """Run CASE, returning its (name, cond, detail) checks in the order it made them."""
    results = []
    case(lambda name, cond, detail="": results.append((name, cond, detail)))
    return results


def main():
    C = Checks()
    with ThreadPoolExecutor(max_workers=len(CASES)) as pool:
        futures = [pool.submit(recorded, case) for case in CASES]
        for future in futures:
            for name, cond, detail in future.result():
                C.check(name, cond, detail)
    return C.report()


if __name__ == "__main__":
    sys.exit(main())
