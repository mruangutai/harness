#!/usr/bin/env python3
"""gh-sync.py backlog must type every issue it creates with a native GitHub Issue Type,
exactly as the open route does (FEAT-55, REQ-01/REQ-04/REQ-05/REQ-06/REQ-07/REQ-08) —
against a fake `gh` answering the same `issueTypes` capability query, `--jq .node_id` and
`updateIssue` shape tests/integration/test-gh-issue-types.py's fake uses for the open route.

RED BY DESIGN until T-06 lands: cmd_backlog is unchanged, so it never calls the detection
query, never applies a type, never writes a per-item receipt and never refuses. Every case
below asserts the TYPED behaviour, so every case fails against today's gh-sync.py, and this
file's own exit code is non-zero until then.

    ./test-gh-backlog-issue-types.py    -> exit 0 all pass, 1 otherwise (must be 1 today)

Command under test:
    gh-sync.py backlog <featdir> "bug:a defect" "chore:a chore" "enhancement:a wish"

Cases (each is CASE <letter> in a `check()` message, grepped by this task's verify):
  A/B  available types: per-issue type ids (bug->Bug, chore->Task, enhancement->Feature)
       and label suppression, one run.
  C    absent types: today's labels unchanged, zero updateIssue, one diagnostic line, and
       NO backlog-issues.json at all (D-13 as amended — compatibility mode has no net-new
       receipt).
  D    receipt and rerun: a successful run's receipt records number + typed true per item;
       the rerun creates nothing but still queries capability exactly once (the
       lazily-called-detector trap) and prints no diagnostic.
  E    crash between create and type: a failed apply records typed exactly false per item
       (never absent, never a missing entry); a later successful rerun backfills every
       recorded number with no create/close/delete.
  F    compatibility mode is byte-identical to today (grilling Settled clause 3): the
       identical command run twice creates three MORE issues each time and never writes
       backlog-issues.json.
  G    REQ-07's refuse-before-create on this route, partial types (Task undeclared), with
       a pre-seeded "created-but-not-yet-typed" remnant so the backfill set is not empty.
  H    the discriminating case: nobug types — both items this run would CREATE have a
       declared type, so only the pre-seeded remnant's backfill need for Bug can refuse.
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

ITEMS = ["bug:a defect", "chore:a chore", "enhancement:a wish"]

# Same fake-gh fixture shape as tests/integration/test-gh-issue-types.py: logs every argv,
# answers the issueTypes capability query by FAKE_TYPES, "--jq .node_id" with a node id
# derived from the issue number, and updateIssue with success unless FAKE_TYPE_APPLY=fail.
FAKE_GH_TYPES = """#!/bin/bash
echo "$*" | tr '\n' '\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
case "$*" in
  *"issueTypes"*)
    case "$FAKE_TYPES" in
      available)
        printf '{"data":{"repository":{"issueTypes":{"nodes":[{"id":"IT_bug","name":"Bug"},{"id":"IT_feature","name":"Feature"},{"id":"IT_task","name":"Task"}]}}}}\\n'
        exit 0 ;;
      partial)
        printf '{"data":{"repository":{"issueTypes":{"nodes":[{"id":"IT_bug","name":"Bug"},{"id":"IT_feature","name":"Feature"}]}}}}\\n'
        exit 0 ;;
      nobug)
        printf '{"data":{"repository":{"issueTypes":{"nodes":[{"id":"IT_feature","name":"Feature"},{"id":"IT_task","name":"Task"}]}}}}\\n'
        exit 0 ;;
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
esac
case "$1 $2" in
  "auth status") exit 0 ;;
  "issue create")
    n=$(( $(grep -c "issue create" "$FAKE_LOG") + 40 ))
    echo "https://github.com/implentio/fake/issues/$n" ;;
esac
exit 0
"""


def install_gh(tmp, script=FAKE_GH_TYPES):
    gh_path = os.path.join(tmp, "gh")
    open(gh_path, "w").write(script)
    os.chmod(gh_path, 0o755)


def build_harness_json(tmp, repo, issue_types):
    g = {"sync": True, "board": None, "repo": repo}
    if issue_types:
        g["issue_types"] = issue_types
    os.makedirs(os.path.join(tmp, ".harness"), exist_ok=True)
    with open(os.path.join(tmp, ".harness", "harness.json"), "w", encoding="utf-8") as f:
        json.dump({"github": g}, f)


def stage(tmp, feat_name="FEAT-88-backlog", repo="owner/name", issue_types=None):
    """A bare feature directory plus a github.sync-enabled harness.json — cmd_backlog reads
    neither BRIEF.md, plan.yaml nor feature.json, so the fixture is only what load_config's
    root walk-up needs: the feature dir three levels under harness.json's parent."""
    feat_dir = os.path.join(tmp, ".harness", "features", feat_name)
    os.makedirs(feat_dir)
    build_harness_json(tmp, repo, issue_types)
    return feat_dir


def run(feat_dir, tmp, env_extra=None, log="calls.log", items=None):
    env = dict(os.environ)
    env["FAKE_LOG"] = os.path.join(tmp, log)
    env["GH_SYNC_GH"] = os.path.join(tmp, "gh")
    env.update(env_extra or {})
    args = ["backlog", feat_dir] + list(items if items is not None else ITEMS)
    return subprocess.run([SYNC] + args, capture_output=True, text=True, env=env)


def calls(tmp, log="calls.log"):
    p = os.path.join(tmp, log)
    return ([l.rstrip("\x01") for l in
              open(p, encoding="utf-8", errors="replace").read().splitlines()]
            if os.path.exists(p) else [])


RECEIPT_NAME = "backlog-issues.json"


def receipt_path(feat_dir):
    return os.path.join(feat_dir, RECEIPT_NAME)


def read_receipt(feat_dir):
    p = receipt_path(feat_dir)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def seed_receipt(feat_dir, entries):
    with open(receipt_path(feat_dir), "w", encoding="utf-8") as f:
        json.dump(entries, f)


def labels_of(argv_line):
    return re.findall(r"--label (\S+)", argv_line)


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
            ("bug:a defect -> Bug", "I_node41", "IT_bug"),
            ("chore:a chore -> Task", "I_node42", "IT_task"),
            ("enhancement:a wish -> Feature", "I_node43", "IT_feature"),
        ]
        for label, node, type_id in expectations:
            check(f"CASE A: {label} is typed {type_id}",
                  any(node in l and type_id in l for l in updates), f"updates={updates}")

        creates = [l for l in log if "issue create" in l]
        check("CASE A: three issue create argv reached the fake",
              len(creates) == 3, f"{creates}")
        check("CASE B: no create argv carries --label bug",
              not any("--label bug" in l for l in creates), f"{creates}")
        check("CASE B: no create argv carries --label chore",
              not any("--label chore" in l for l in creates), f"{creates}")
        check("CASE B: every create argv carries --label harness",
              bool(creates) and all("--label harness" in l for l in creates), f"{creates}")


def case_c():
    """CASE C: FAKE_TYPES=absent, fresh fixture — today's labels, no updateIssue, one
    diagnostic line, and no backlog-issues.json at all."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp)
        feat_dir = stage(tmp)
        r = run(feat_dir, tmp, {"FAKE_TYPES": "absent"})
        log = calls(tmp)
        creates = [l for l in log if "issue create" in l]
        check("CASE C: three issues created", len(creates) == 3, f"{creates}")
        check("CASE C: bug item labels are exactly harness, bug",
              labels_of(creates[0]) == ["harness", "bug"] if creates else False, creates)
        check("CASE C: chore item labels are exactly harness, chore",
              labels_of(creates[1]) == ["harness", "chore"] if len(creates) > 1 else False,
              creates)
        check("CASE C: enhancement item labels are exactly harness",
              labels_of(creates[2]) == ["harness"] if len(creates) > 2 else False, creates)
        check("CASE C: zero updateIssue argv reached the fake",
              not any("updateIssue" in l for l in log), f"{log}")
        lines = re.findall(r"^gh-sync: issue types ", r.stdout, re.M)
        check("CASE C: exactly one 'gh-sync: issue types ' line for a three-issue run",
              len(lines) == 1, repr(r.stdout))
        check("CASE C: no backlog-issues.json is written in compatibility mode",
              not os.path.exists(receipt_path(feat_dir)), feat_dir)


def case_d():
    """CASE D: receipt after a successful available run, then a rerun that creates
    nothing but still queries capability exactly once and prints no diagnostic."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp)
        feat_dir = stage(tmp)
        run(feat_dir, tmp, {"FAKE_TYPES": "available"}, log="calls1.log")
        rec = read_receipt(feat_dir)
        check("CASE D: backlog-issues.json exists after a successful run",
              rec is not None, feat_dir)
        rec = rec or {}
        expected_numbers = {"bug:a defect": 41, "chore:a chore": 42,
                             "enhancement:a wish": 43}
        for item, number in expected_numbers.items():
            entry = rec.get(item, {})
            check(f"CASE D: {item!r} recorded with number {number} and typed true",
                  entry.get("number") == number and entry.get("typed") is True,
                  f"{item!r} -> {entry}")

        r2 = run(feat_dir, tmp, {"FAKE_TYPES": "available"}, log="calls2.log")
        log2 = calls(tmp, "calls2.log")
        check("CASE D: zero issue create argv on the rerun (everything already recorded)",
              not any("issue create" in l for l in log2), f"{log2}")
        query_lines = [l for l in log2 if "issueTypes" in l]
        check("CASE D: exactly one argv containing issueTypes on the zero-create rerun",
              len(query_lines) == 1, f"{log2}")
        diag_lines = re.findall(r"^gh-sync: issue types ", r2.stdout, re.M)
        check("CASE D: zero 'gh-sync: issue types ' lines on the zero-create rerun",
              len(diag_lines) == 0, repr(r2.stdout))


def case_e():
    """CASE E: FAKE_TYPE_APPLY=fail records typed exactly false per item (not absent, not
    missing); a later successful rerun backfills every recorded number, with no
    create/close/delete."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp)
        feat_dir = stage(tmp)
        run(feat_dir, tmp, {"FAKE_TYPES": "available", "FAKE_TYPE_APPLY": "fail"},
            log="calls1.log")
        rec1 = read_receipt(feat_dir) or {}
        for item in ITEMS:
            entry = rec1.get(item)
            check(f"CASE E: {item!r} has a receipt entry after a failed type-apply",
                  entry is not None, f"{rec1}")
            check(f"CASE E: {item!r}'s typed value is exactly false (not absent)",
                  entry is not None and entry.get("typed") is False, f"{item!r} -> {entry}")

        run(feat_dir, tmp, {"FAKE_TYPES": "available"}, log="calls2.log")
        log2 = calls(tmp, "calls2.log")
        check("CASE E: the rerun makes no issue create argv",
              not any("issue create" in l for l in log2), f"{log2}")
        check("CASE E: the rerun makes no issue close argv",
              not any("issue close" in l for l in log2), f"{log2}")
        check("CASE E: the rerun makes no issue delete argv",
              not any("issue delete" in l for l in log2), f"{log2}")
        numbers = {rec1.get(item, {}).get("number") for item in ITEMS}
        for number in numbers:
            node = f"I_node{number}" if number is not None else "I_node__missing__"
            check(f"CASE E: the rerun updateIssue's the recorded node id for number {number}",
                  any("updateIssue" in l and node in l for l in log2), f"{log2}")
        rec2 = read_receipt(feat_dir) or {}
        for item in ITEMS:
            check(f"CASE E: {item!r}'s typed value is promoted to True after the backfill",
                  rec2.get(item, {}).get("typed") is True, f"{rec2}")


def case_f():
    """CASE F: compatibility mode is byte-identical to today — the identical command run
    twice creates three MORE issues each time and never writes backlog-issues.json."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp)
        feat_dir = stage(tmp)
        run(feat_dir, tmp, {"FAKE_TYPES": "absent"}, log="calls1.log")
        r2 = run(feat_dir, tmp, {"FAKE_TYPES": "absent"}, log="calls2.log")
        log2 = calls(tmp, "calls2.log")
        creates2 = [l for l in log2 if "issue create" in l]
        check("CASE F: the second run makes three MORE issue create argv",
              len(creates2) == 3, f"{creates2}")
        check("CASE F: no backlog-issues.json exists after either run",
              not os.path.exists(receipt_path(feat_dir)), feat_dir)
        check("CASE F: no stdout line names a skipped recorded item",
              "skip" not in r2.stdout.lower(), repr(r2.stdout))
        diag_lines = re.findall(r"^gh-sync: issue types ", r2.stdout, re.M)
        check("CASE F: the second invocation still prints exactly one diagnostic line",
              len(diag_lines) == 1, repr(r2.stdout))


def case_g():
    """CASE G: partial types (Task undeclared) with a pre-seeded created-but-not-yet-typed
    remnant (bug:a defect, #601, typed false) so the backfill set is not empty. The chore
    item still resolves to Task, which is not declared, so the run must refuse before ANY
    create or apply, leaving the remnant untouched."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp)
        feat_dir = stage(tmp)
        seed_receipt(feat_dir, {"bug:a defect": {"number": 601, "typed": False}})
        r = run(feat_dir, tmp, {"FAKE_TYPES": "partial"})
        log = calls(tmp)
        both = r.stdout + r.stderr
        check("CASE G: the run refuses (non-zero exit)", r.returncode != 0,
              f"exit={r.returncode} out={both}")
        check("CASE G: zero issue create argv reached the fake",
              not any("issue create" in l for l in log), f"{log}")
        check("CASE G: zero updateIssue argv reached the fake",
              not any("updateIssue" in l for l in log), f"{log}")
        check("CASE G: zero updateIssue argv carries a node id derived from remnant 601",
              not any("updateIssue" in l and "I_node601" in l for l in log), f"{log}")
        check("CASE G: the refusal names both Task and github.issue_types",
              "Task" in both and "github.issue_types" in both, both)
        rec = read_receipt(feat_dir) or {}
        check("CASE G: the seeded remnant is unchanged - number still 601",
              rec.get("bug:a defect", {}).get("number") == 601, f"{rec}")
        check("CASE G: the seeded remnant is unchanged - typed still exactly false",
              rec.get("bug:a defect", {}).get("typed") is False, f"{rec}")
        check("CASE G: no entry was recorded for the chore item",
              "chore:a chore" not in rec, f"{rec}")
        check("CASE G: no entry was recorded for the enhancement item",
              "enhancement:a wish" not in rec, f"{rec}")


def case_h():
    """CASE H: FAKE_TYPES=nobug. Both items this run would CREATE resolve to declared
    types (chore->Task, enhancement->Feature), so the creation-side check alone refuses
    nothing; only the pre-seeded remnant's backfill need for the undeclared Bug can
    refuse."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp)
        feat_dir = stage(tmp)
        seed_receipt(feat_dir, {"bug:a defect": {"number": 602, "typed": False}})
        r = run(feat_dir, tmp, {"FAKE_TYPES": "nobug"})
        log = calls(tmp)
        both = r.stdout + r.stderr
        check("CASE H: the run refuses (non-zero exit) though nothing to be CREATED needs Bug",
              r.returncode != 0, f"exit={r.returncode} out={both}")
        check("CASE H: the refusal names both Bug and github.issue_types",
              "Bug" in both and "github.issue_types" in both, both)
        check("CASE H: zero issue create argv reached the fake",
              not any("issue create" in l for l in log), f"{log}")
        check("CASE H: zero updateIssue argv reached the fake",
              not any("updateIssue" in l for l in log), f"{log}")
        check("CASE H: zero updateIssue argv carries a node id derived from remnant 602",
              not any("updateIssue" in l and "I_node602" in l for l in log), f"{log}")
        rec = read_receipt(feat_dir) or {}
        check("CASE H: the seeded remnant is unchanged - number still 602",
              rec.get("bug:a defect", {}).get("number") == 602, f"{rec}")
        check("CASE H: the seeded remnant is unchanged - typed still exactly false",
              rec.get("bug:a defect", {}).get("typed") is False, f"{rec}")
        check("CASE H: no entry was recorded for the chore item",
              "chore:a chore" not in rec, f"{rec}")
        check("CASE H: no entry was recorded for the enhancement item",
              "enhancement:a wish" not in rec, f"{rec}")


case_a_b()
case_c()
case_d()
case_e()
case_f()
case_g()
case_h()

print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
