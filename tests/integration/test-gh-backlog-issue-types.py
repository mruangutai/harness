#!/usr/bin/env python3
"""gh-sync.py backlog must type every issue it creates with a native GitHub Issue Type,
exactly as the open route does (FEAT-55, REQ-01/REQ-04/REQ-05/REQ-06/REQ-07/REQ-08) —
against a fake `gh` answering the same `issueTypes` capability query, `--jq .node_id` and
`updateIssue` shape tests/integration/test-gh-issue-types.py's fake uses for the open route.

    ./test-gh-backlog-issue-types.py    -> exit 0 all pass, 1 otherwise

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
  I    #1542: a create URL with no positive /issues/<n> tail is a mirror SKIP.

A/B shares its run with D's first run, and C shares its run with F's first run: each pair
is the identical command on an identical fresh fixture.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

import integration_support  # noqa: F401  (puts bin/ and tests/ on sys.path before the imports below)
from check_support import Checks
from gh_sync_support import SYNC, install_gh
from harness_config_support import write_config
from offline_gh_support import assert_sentinel_unused, offline_gh_env

C = Checks()
check = C.check

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


def stage(tmp):
    """A bare feature directory plus a github.sync-enabled harness.json — cmd_backlog reads
    neither BRIEF.md, plan.yaml nor feature.json, so the fixture is only what load_config's
    root walk-up needs: the feature dir three levels under harness.json's parent."""
    feat_dir = os.path.join(tmp, ".harness", "features", "FEAT-88-backlog")
    os.makedirs(feat_dir)
    write_config(os.path.join(tmp, ".harness", "harness.json"),
                 {"github": {"sync": True, "board": None, "repo": "owner/name"}})
    return feat_dir


def run(feat_dir, tmp, env_extra=None, log="calls.log"):
    env, sentinel_log = offline_gh_env(os.path.join(tmp, "gh"), tmp)
    env["FAKE_LOG"] = os.path.join(tmp, log)
    env.update(env_extra or {})
    result = subprocess.run([SYNC, "backlog", feat_dir, *ITEMS], capture_output=True, text=True, env=env)
    assert_sentinel_unused(sentinel_log)
    return result


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


def case_i():
    """CASE I (#1542): a create URL with no positive /issues/<n> tail is an ordinary mirror SKIP:
    no traceback, no backlog receipt entry, no second create."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp, FAKE_GH_TYPES.replace(
            'echo "https://github.com/implentio/fake/issues/$n" ;;',
            'echo "https://github.com/implentio/fake/issues/" ;;'))
        feat_dir = stage(tmp)
        result = run(feat_dir, tmp, {"FAKE_TYPES": "available"})
        creates = [l for l in calls(tmp) if "issue create" in l]
        check("CASE I: a malformed create URL is a mirror SKIP, exit 0, no traceback",
              result.returncode == 0 and "gh-sync: SKIP" in result.stdout
              and "Traceback" not in result.stderr, result.stdout + result.stderr)
        check("CASE I: no backlog receipt entry is written for the unreadable create",
              not read_receipt(feat_dir), f"{read_receipt(feat_dir)}")
        check("CASE I: exactly one create was dispatched, never a second",
              len(creates) == 1, f"{creates}")


def check_a(log):
    """CASE A: per-issue type ids on the available run."""
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
    return creates


def check_b(creates):
    """CASE B: label suppression on the same run's create argv."""
    for lab in ("bug", "chore"):
        check(f"CASE B: no create argv carries --label {lab}",
              not any(f"--label {lab}" in l for l in creates), f"{creates}")
    check("CASE B: every create argv carries --label harness",
          bool(creates) and all("--label harness" in l for l in creates), f"{creates}")


def check_d_receipt(feat_dir):
    """CASE D: a successful run's receipt records number + typed true per item."""
    rec = read_receipt(feat_dir)
    check("CASE D: backlog-issues.json exists after a successful run",
          rec is not None, feat_dir)
    rec = rec or {}
    for item, number in zip(ITEMS, (41, 42, 43)):
        entry = rec.get(item, {})
        check(f"CASE D: {item!r} recorded with number {number} and typed true",
              entry.get("number") == number and entry.get("typed") is True,
              f"{item!r} -> {entry}")


def check_d_rerun(r2, log2):
    """CASE D: the rerun creates nothing but still queries capability exactly once (the
    lazily-called-detector trap) and prints no diagnostic."""
    check("CASE D: zero issue create argv on the rerun (everything already recorded)",
          not any("issue create" in l for l in log2), f"{log2}")
    query_lines = [l for l in log2 if "issueTypes" in l]
    check("CASE D: exactly one argv containing issueTypes on the zero-create rerun",
          len(query_lines) == 1, f"{log2}")
    diag_lines = re.findall(r"^gh-sync: issue types ", r2.stdout, re.M)
    check("CASE D: zero 'gh-sync: issue types ' lines on the zero-create rerun",
          len(diag_lines) == 0, repr(r2.stdout))


def case_a_b_d():
    """CASE A / CASE B on one FAKE_TYPES=available run; CASE D reads that same run's receipt,
    then reruns the identical command."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp, FAKE_GH_TYPES)
        feat_dir = stage(tmp)
        run(feat_dir, tmp, {"FAKE_TYPES": "available"}, log="calls1.log")
        check_b(check_a(calls(tmp, "calls1.log")))
        check_d_receipt(feat_dir)
        r2 = run(feat_dir, tmp, {"FAKE_TYPES": "available"}, log="calls2.log")
        check_d_rerun(r2, calls(tmp, "calls2.log"))


def check_c(r, log, feat_dir):
    """CASE C: FAKE_TYPES=absent, fresh fixture - today's labels, no updateIssue, one
    diagnostic line, and no backlog-issues.json at all."""
    creates = [l for l in log if "issue create" in l]
    check("CASE C: three issues created", len(creates) == 3, f"{creates}")
    wants = (["harness", "bug"], ["harness", "chore"], ["harness"])
    for i, (item, want) in enumerate(zip(ITEMS, wants)):
        check(f"CASE C: {item.split(':')[0]} item labels are exactly {', '.join(want)}",
              i < len(creates) and labels_of(creates[i]) == want, creates)
    check("CASE C: zero updateIssue argv reached the fake",
          not any("updateIssue" in l for l in log), f"{log}")
    lines = re.findall(r"^gh-sync: issue types ", r.stdout, re.M)
    check("CASE C: exactly one 'gh-sync: issue types ' line for a three-issue run",
          len(lines) == 1, repr(r.stdout))
    check("CASE C: no backlog-issues.json is written in compatibility mode",
          not os.path.exists(receipt_path(feat_dir)), feat_dir)


def check_f(r2, log2, feat_dir):
    """CASE F: compatibility mode is byte-identical to today - the identical command run a
    second time creates three MORE issues and never writes backlog-issues.json."""
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


def case_c_f():
    """CASE C's absent run is CASE F's first run; F reruns the identical command."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp, FAKE_GH_TYPES)
        feat_dir = stage(tmp)
        r = run(feat_dir, tmp, {"FAKE_TYPES": "absent"}, log="calls1.log")
        check_c(r, calls(tmp, "calls1.log"), feat_dir)
        r2 = run(feat_dir, tmp, {"FAKE_TYPES": "absent"}, log="calls2.log")
        check_f(r2, calls(tmp, "calls2.log"), feat_dir)


def check_e_failed_apply(rec1):
    """CASE E: a failed apply records typed exactly false per item (never absent)."""
    for item in ITEMS:
        entry = rec1.get(item)
        check(f"CASE E: {item!r} has a receipt entry after a failed type-apply",
              entry is not None, f"{rec1}")
        check(f"CASE E: {item!r}'s typed value is exactly false (not absent)",
              entry is not None and entry.get("typed") is False, f"{item!r} -> {entry}")


def check_e_backfill(rec1, log2, rec2):
    """CASE E: the successful rerun backfills every recorded number, no create/close/delete."""
    for verb in ("create", "close", "delete"):
        check(f"CASE E: the rerun makes no issue {verb} argv",
              not any(f"issue {verb}" in l for l in log2), f"{log2}")
    for item in ITEMS:
        number = rec1.get(item, {}).get("number")
        check(f"CASE E: the rerun updateIssue's the recorded node id for number {number}",
              any("updateIssue" in l and f"I_node{number}" in l for l in log2), f"{log2}")
    for item in ITEMS:
        check(f"CASE E: {item!r}'s typed value is promoted to True after the backfill",
              rec2.get(item, {}).get("typed") is True, f"{rec2}")


def case_e():
    """CASE E: crash between create and type (FAKE_TYPE_APPLY=fail), then a successful rerun."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp, FAKE_GH_TYPES)
        feat_dir = stage(tmp)
        run(feat_dir, tmp, {"FAKE_TYPES": "available", "FAKE_TYPE_APPLY": "fail"},
            log="calls1.log")
        rec1 = read_receipt(feat_dir) or {}
        check_e_failed_apply(rec1)
        run(feat_dir, tmp, {"FAKE_TYPES": "available"}, log="calls2.log")
        check_e_backfill(rec1, calls(tmp, "calls2.log"), read_receipt(feat_dir) or {})


def check_refusal_untouched(case, log, remnant, rec):
    """CASE G / CASE H: nothing created or applied, and the seeded remnant left as it was."""
    check(f"CASE {case}: zero issue create argv reached the fake",
          not any("issue create" in l for l in log), f"{log}")
    check(f"CASE {case}: zero updateIssue argv reached the fake",
          not any("updateIssue" in l for l in log), f"{log}")
    check(f"CASE {case}: zero updateIssue argv carries a node id derived from remnant {remnant}",
          not any("updateIssue" in l and f"I_node{remnant}" in l for l in log), f"{log}")
    check(f"CASE {case}: the seeded remnant is unchanged - number still {remnant}",
          rec.get("bug:a defect", {}).get("number") == remnant, f"{rec}")
    check(f"CASE {case}: the seeded remnant is unchanged - typed still exactly false",
          rec.get("bug:a defect", {}).get("typed") is False, f"{rec}")
    check(f"CASE {case}: no entry was recorded for the chore item",
          "chore:a chore" not in rec, f"{rec}")
    check(f"CASE {case}: no entry was recorded for the enhancement item",
          "enhancement:a wish" not in rec, f"{rec}")


def refusal_case(case, fake_types, remnant, missing, refuse_note=""):
    """CASE G / CASE H: a pre-seeded created-but-not-yet-typed remnant (bug:a defect,
    #<remnant>, typed false) and FAKE_TYPES=<fake_types> leaving <missing> undeclared; the run
    must refuse before ANY create or apply, leaving the remnant untouched."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp, FAKE_GH_TYPES)
        feat_dir = stage(tmp)
        seed_receipt(feat_dir, {"bug:a defect": {"number": remnant, "typed": False}})
        r = run(feat_dir, tmp, {"FAKE_TYPES": fake_types})
        both = r.stdout + r.stderr
        check(f"CASE {case}: the run refuses (non-zero exit){refuse_note}", r.returncode != 0,
              f"exit={r.returncode} out={both}")
        check(f"CASE {case}: the refusal names both {missing} and github.issue_types",
              missing in both and "github.issue_types" in both, both)
        check_refusal_untouched(case, calls(tmp), remnant, read_receipt(feat_dir) or {})


case_a_b_d()
case_c_f()
case_e()
# CASE G: partial types (Task undeclared). The chore item still resolves to Task, so the
# creation-side check refuses; the remnant makes the backfill set non-empty.
refusal_case("G", "partial", 601, "Task")
# CASE H: nobug types. Both items this run would CREATE resolve to declared types
# (chore->Task, enhancement->Feature), so only the remnant's backfill need for the
# undeclared Bug can refuse.
refusal_case("H", "nobug", 602, "Bug", " though nothing to be CREATED needs Bug")
case_i()

sys.exit(C.report())
