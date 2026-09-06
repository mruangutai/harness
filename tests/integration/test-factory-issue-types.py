#!/usr/bin/env python3
"""factory_decompose.py's parent and task creation must type every issue it creates with a
native GitHub Issue Type, suppress the two now-redundant chore/bug labels, refuse before any
create when a required type is undeclared (REQ-07), and never touch an adopted parent's type
or an absent-provenance remnant (FEAT-55, REQ-01/REQ-03/REQ-05/REQ-06/REQ-07/REQ-08/REQ-10) —
against a fake `gh`, installed at FACTORY_GH (never GH_SYNC_GH: see the wiring comment at
factory_gh.py:91-94 and gh_board.py:8-12 — a fake wired the other way would leave every call
this module makes going to the real `gh`), that answers the issueTypes capability query,
`--jq .node_id`, `updateIssue`, and every other call factory_decompose.py's existing surface
already makes (auth, labels, the remote harness.json contents read, project field-resolve /
item-add / item-edit, the projectItems recovery query, sub_issues, blocked_by) so a real
subprocess run of factory_decompose.py reaches step 6 (issue creation) and beyond, exactly as
test-gh-issue-types.py's FAKE_GH_TYPES fake (T-03) does for gh-sync.py.

RED BY DESIGN until T-08 lands: factory_decompose.py and factory_gh.py are unchanged, so this
run never queries issue types, never calls updateIssue, never refuses, and never prints a
"factory: issue types " diagnostic. Every case below asserts the TYPED/refusing behaviour, so
every case fails against today's factory_decompose.py, and this file's own exit code is
non-zero until then.

    ./test-factory-issue-types.py    -> exit 0 all pass, 1 otherwise (must be 1 today)

Fixture: one feature, one repository, a signed three-task plan.yaml — one bugfix task (maps
to Bug), one config task (maps to Task) and one feature-change_type task (maps to Task, D-18:
a task sub-issue is never Feature whatever its change_type spells) — plus a parent that does
not yet exist unless a case pre-seeds one.

Cases (each is CASE <letter> in a `check()` message, grepped by T-07's verify):
  A  FAKE_TYPES=available: per-issue updateIssue typing (D-18: the FEATURE task types Task,
     never Feature; only the parent types Feature, from type_for_parent).
  B  same run: chore/bug labels suppressed; harness/feature:<FEAT> still applied.
  C  FAKE_TYPES=absent: today's labels unchanged, zero updateIssue, exactly one diagnostic
     line for a run creating four issues (parent + three tasks).
  D  github.issue_types overrides {"Bug": "Story", "parent": "Story"}: the bugfix task's and
     the parent's updateIssue both carry IT_story; Task is not overridden, so the config task
     and the feature task (D-18) both still carry IT_task.
  E  FAKE_TYPES=available FAKE_TYPE_APPLY=fail, then a clean rerun: the create-time
     "created" provenance survives a failed type-apply and is promoted to True only once
     the rerun's apply succeeds.
  F  --parent 4242 (REQ-10, the adopted-parent route): never typed, recorded "adopted", and
     still "adopted" — never True, never "created" — on a later run with no --parent at all.
  G  the lazily-called-detector trap (FAKE_TYPES=absent): a rerun that creates nothing must
     still print exactly one "^factory: issue types " line.
  H  absent provenance (the legacy factory.yaml shape, no `typed` key at all) is never typed,
     this run or any later one — while the tasks that are NOT already recorded still get
     typed, proving the bound rather than a dead run.
  I  REQ-07 refuse-before-create, partial types (Task undeclared), a pre-seeded "created"
     remnant (bugfix task 701) so the backfill set is not empty: the run refuses before ANY
     create, the parent's included, and the remnant is untouched.
  J  the discriminating case (FAKE_TYPES=nobug): every issue this run WOULD create already has
     a declared type, so refusal can only come from the backfill needing the undeclared Bug
     for the pre-seeded "created" remnant (task 703).
"""
import base64
import json
import os
import re
import subprocess
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
DECOMPOSE = os.path.join(BIN_DIR, "factory_decompose.py")

REPO = "acme/widget"
FEAT = "FEAT-91-factory-types"

# The three-task fixture every case builds on: one of each role T-08's typing table cares
# about. Neither logic nor bugfix's siblings need varying change_types beyond these three —
# D-18 (task sub-issues are never Feature) is proven by the FEATURE-change_type task alone.
TASKS = [
    {"id": "T-01", "title": "fix the off-by-one in export", "change_type": "bugfix",
     "execution_mode": "team", "files": ["a.py"], "verify": "true",
     "intent": "Fix the off-by-one.", "traces": ["REQ-01"]},
    {"id": "T-02", "title": "add sync toggle to harness.json", "change_type": "config",
     "execution_mode": "team", "files": ["b.py"], "verify": "true",
     "intent": "Add the toggle.", "traces": ["REQ-01"]},
    {"id": "T-03", "title": "add CSV export button", "change_type": "feature",
     "execution_mode": "team", "files": ["c.py"], "verify": "true",
     "intent": "Add the button.", "traces": ["REQ-01"]},
]

# The FAKE_GH bash script — the same style FAKE_GH_TYPES (T-03, test-gh-issue-types.py) uses:
# no state file, everything derived from the argv/env alone, a `$FAKE_LOG` line per call so a
# case can count "issue create" calls and read back exact argv. Two sequential `case`
# statements: the first dispatches on distinctive TEXT anywhere in the joined argv (GraphQL
# query text and --jq flags never sit in a fixed argv position); the second on the exact
# first two words, for the plain gh subcommands. Every arm ends in `exit`, so nothing falls
# through unhandled into "exit 0" by accident.
FAKE_GH_SRC = r"""#!/bin/bash
echo "$*" | tr '\n' '\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
case "$*" in
  *"issueTypes(first:"*)
    case "$FAKE_TYPES" in
      available)
        printf '%s\n' '{"data":{"repository":{"issueTypes":{"nodes":[{"id":"IT_bug","name":"Bug"},{"id":"IT_feature","name":"Feature"},{"id":"IT_task","name":"Task"},{"id":"IT_story","name":"Story"}]}}}}'
        exit 0 ;;
      partial)
        printf '%s\n' '{"data":{"repository":{"issueTypes":{"nodes":[{"id":"IT_bug","name":"Bug"},{"id":"IT_feature","name":"Feature"}]}}}}'
        exit 0 ;;
      nobug)
        printf '%s\n' '{"data":{"repository":{"issueTypes":{"nodes":[{"id":"IT_feature","name":"Feature"},{"id":"IT_task","name":"Task"}]}}}}'
        exit 0 ;;
      failed)
        printf '%s\n' '{"data":{"repository":null},"errors":[{"message":"Could not resolve to a Repository"}]}'
        exit 1 ;;
      *)
        printf '%s\n' '{"data":{"repository":{"issueTypes":null}}}'
        exit 0 ;;
    esac ;;
  *"--jq .node_id"*)
    num=$(echo "$*" | grep -oE 'issues/[0-9]+' | head -1 | grep -oE '[0-9]+')
    echo "I_node$num"
    exit 0 ;;
  *"--jq .id"*)
    num=$(echo "$*" | grep -oE 'issues/[0-9]+' | head -1 | grep -oE '[0-9]+')
    echo "9000$num"
    exit 0 ;;
  *"updateIssue"*)
    if [ "$FAKE_TYPE_APPLY" = "fail" ]; then
      echo "simulated type-apply failure" >&2
      exit 1
    fi
    echo '{"data":{"updateIssue":{"issue":{"id":"I_node"}}}}'
    exit 0 ;;
  *"contents/.harness/harness.json"*)
    echo "$FAKE_HARNESS_JSON_B64"
    exit 0 ;;
  *"field(name:"*)
    printf '%s\n' '{"data":{"repositoryOwner":{"__typename":"User","projectV2":{"id":"PVT_kwFAKE","field":{"id":"FIELD_STATUS","name":"Status","options":[{"id":"OPT_BACKLOG","name":"Backlog"},{"id":"OPT_PLAN","name":"Plan"},{"id":"OPT_READY","name":"Ready"},{"id":"OPT_BUILDING","name":"Building"},{"id":"OPT_REVIEW","name":"Review"},{"id":"OPT_DONE","name":"Done"}]}}}}}'
    exit 0 ;;
  *"projectItems(first:"*)
    echo '{"data":{"repository":{"issue":{"projectItems":{"totalCount":0,"nodes":[]}}}}}'
    exit 0 ;;
  *"sub_issues -F sub_issue_id="*)
    echo '{}'
    exit 0 ;;
  *"dependencies/blocked_by"*)
    echo '{}'
    exit 0 ;;
esac
case "$1 $2" in
  "auth status")
    exit 0 ;;
  "label create")
    exit 0 ;;
  "issue create")
    n=$(( $(grep -c '^issue create' "$FAKE_LOG") + 40 ))
    echo "https://github.com/$FAKE_REPO/issues/$n"
    exit 0 ;;
  "project item-add")
    n=$(( $(grep -c '^project item-add' "$FAKE_LOG") + 1 ))
    echo "{\"id\": \"ITEM$n\"}"
    exit 0 ;;
  "project item-edit")
    exit 0 ;;
esac
exit 0
"""


def install_gh(tmp):
    path = os.path.join(tmp, "gh")
    with open(path, "w", encoding="utf-8") as f:
        f.write(FAKE_GH_SRC)
    os.chmod(path, 0o755)
    return path


def make_root(base):
    """A temp root carrying harness_boundary's own MARKER (.harness/team-config.yaml), so
    HARNESS_PROJECT_DIR points every root-resolving module (gh_cost_log included) at a
    throwaway directory rather than falling through to the real checkout."""
    root = os.path.join(base, "root")
    os.makedirs(os.path.join(root, ".harness"), exist_ok=True)
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w", encoding="utf-8") as f:
        f.write("teams: []\n")
    return root


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def board_dict():
    return {
        "owner": "acme", "number": 9, "station_field": "Status",
        "stations": ["backlog", "plan", "ready", "building", "review", "done"],
    }


def harness_json_b64(issue_types=None):
    github = {"board": board_dict()}
    if issue_types:
        github["issue_types"] = issue_types
    return base64.b64encode(json.dumps({"github": github}).encode("utf-8")).decode("ascii")


def build_fleet(tmp):
    fleet_path = os.path.join(tmp, "fleet", "fleet.yaml")
    write_json(fleet_path, {
        "schema": "factory-fleet/1",
        "repos": [{"name": REPO, "default_branch": "main"}],
        "workspace_root": os.path.join(tmp, "workspaces"),
    })
    return fleet_path


def stage(tmp, factory=None, feat=FEAT, tasks=None):
    """A feature directory: a signed three-task plan.yaml, a BRIEF.md with Problem/Goal
    sections, and — only when `factory` is given — a pre-seeded feature.json `factory` block.
    write_factory legitimately creates feature.json fresh (its own module docstring), so a
    case starting from nothing installs no feature.json at all."""
    feat_dir = os.path.join(tmp, "feature")
    os.makedirs(feat_dir, exist_ok=True)
    write_json(os.path.join(feat_dir, "plan.yaml"), {
        "schema": "plan/1", "feature": feat,
        "approval": {"status": "approved"},
        "tasks": tasks if tasks is not None else TASKS,
    })
    with open(os.path.join(feat_dir, "BRIEF.md"), "w", encoding="utf-8") as f:
        f.write(f"# {feat} — native issue types\n\n## Problem\n\nIssues carry no type.\n\n"
                 f"## Goal\n\nType every issue the factory creates.\n")
    if factory is not None:
        write_json(os.path.join(feat_dir, "feature.json"), {"factory": factory})
    return feat_dir


def run_decompose(root, feat_dir, fleet_path, gh_path, log_path, harness_b64,
                   fake_types=None, fake_type_apply=None, extra_args=None):
    env = dict(os.environ)
    env["HARNESS_PROJECT_DIR"] = root
    env["FACTORY_GH"] = gh_path
    env["FAKE_LOG"] = log_path
    env["FAKE_REPO"] = REPO
    env["FAKE_HARNESS_JSON_B64"] = harness_b64
    if fake_types is not None:
        env["FAKE_TYPES"] = fake_types
    else:
        env.pop("FAKE_TYPES", None)
    if fake_type_apply is not None:
        env["FAKE_TYPE_APPLY"] = fake_type_apply
    else:
        env.pop("FAKE_TYPE_APPLY", None)
    args = [feat_dir, "--repo", REPO, "--fleet", fleet_path] + (extra_args or [])
    return subprocess.run(
        [sys.executable, DECOMPOSE] + args,
        env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=20,
    )


def read_log(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", errors="replace") as f:
        # Every logged line carries one trailing "\x01" — the fake's own trailing newline
        # (echo's own terminator), converted by the same tr that folds embedded body
        # newlines into "\x01" so one gh call is always one log line. Strip it so a
        # trailing label token (e.g. "bug") is never seen as "bug\x01".
        return [l.rstrip("\x01") for l in f.read().splitlines() if l]


def read_factory(feat_dir):
    path = os.path.join(feat_dir, "feature.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    return doc.get("factory") or {}


def diag_lines(result):
    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    return [l for l in combined.splitlines() if re.match(r"^factory: issue types ", l)]


fails = 0


def check(name, cond, detail=""):
    global fails
    if cond:
        print(f"ok    {name}")
    else:
        fails += 1
        print(f"FAIL  {name}\n      {detail}")


def case_a_b():
    with tempfile.TemporaryDirectory() as td:
        root = make_root(td)
        gh = install_gh(td)
        fleet_path = build_fleet(td)
        feat_dir = stage(td)
        log = os.path.join(td, "run.log")
        r = run_decompose(root, feat_dir, fleet_path, gh, log, harness_json_b64(),
                           fake_types="available")
        check("CASE A: decompose exits 0 so step 6 is reached",
              r.returncode == 0, f"code={r.returncode} stderr={r.stderr!r}")
        fac = read_factory(feat_dir)
        issues = fac.get("issues", {})
        loglines = read_log(log)
        updates = [l for l in loglines if "updateIssue" in l]
        expectations = [
            ("the parent", fac.get("parent"), "IT_feature"),
            ("T-01 (bugfix)", issues.get("T-01"), "IT_bug"),
            ("T-02 (config)", issues.get("T-02"), "IT_task"),
            ("T-03 (feature change_type — D-18, never IT_feature)", issues.get("T-03"),
             "IT_task"),
        ]
        for label, num, type_id in expectations:
            node = f"I_node{num}"
            check(f"CASE A: {label} is typed {type_id} via an updateIssue argv carrying "
                  f"{node}",
                  num is not None and any(node in l and type_id in l for l in updates),
                  f"num={num} updates={updates}")

        creates = [l for l in loglines if l.startswith("issue create")]
        check("CASE B: no create argv carries --label bug",
              not any("--label bug" in l for l in creates), creates)
        check("CASE B: no create argv carries --label chore",
              not any("--label chore" in l for l in creates), creates)
        check("CASE B: every create argv still carries --label harness",
              bool(creates) and all("--label harness" in l for l in creates), creates)
        check(f"CASE B: every create argv still carries --label feature:{FEAT}",
              bool(creates) and all(f"--label feature:{FEAT}" in l for l in creates), creates)
        check("CASE B: factory:claimed is applied exactly where it is today (nowhere on a "
              "created issue)",
              not any("--label factory:claimed" in l for l in creates), creates)


def case_c():
    with tempfile.TemporaryDirectory() as td:
        root = make_root(td)
        gh = install_gh(td)
        fleet_path = build_fleet(td)
        feat_dir = stage(td)
        log = os.path.join(td, "run.log")
        r = run_decompose(root, feat_dir, fleet_path, gh, log, harness_json_b64(),
                           fake_types="absent")
        check("CASE C: decompose exits 0", r.returncode == 0,
              f"code={r.returncode} stderr={r.stderr!r}")
        loglines = read_log(log)
        creates = [l for l in loglines if l.startswith("issue create")]
        check("CASE C: four issues created (parent + three tasks)", len(creates) == 4,
              creates)
        t01_labels = re.findall(r"--label (\S+)", next((l for l in creates
                                                          if "T-01" in l), ""))
        t02_labels = re.findall(r"--label (\S+)", next((l for l in creates
                                                          if "T-02" in l), ""))
        check("CASE C: labels unchanged — bugfix task still carries bug",
              "bug" in t01_labels, t01_labels)
        check("CASE C: labels unchanged — config task still carries chore",
              "chore" in t02_labels, t02_labels)
        updates = [l for l in loglines if "updateIssue" in l]
        check("CASE C: zero updateIssue argv when types are absent", updates == [], updates)
        lines = diag_lines(r)
        check("CASE C: exactly one '^factory: issue types ' diagnostic line for a run "
              "creating four issues",
              len(lines) == 1, f"stdout={r.stdout!r} stderr={r.stderr!r}")


def case_d():
    with tempfile.TemporaryDirectory() as td:
        root = make_root(td)
        gh = install_gh(td)
        fleet_path = build_fleet(td)
        feat_dir = stage(td)
        log = os.path.join(td, "run.log")
        b64 = harness_json_b64(issue_types={"Bug": "Story", "parent": "Story"})
        r = run_decompose(root, feat_dir, fleet_path, gh, log, b64, fake_types="available")
        check("CASE D: decompose exits 0", r.returncode == 0,
              f"code={r.returncode} stderr={r.stderr!r}")
        fac = read_factory(feat_dir)
        issues = fac.get("issues", {})
        updates = [l for l in read_log(log) if "updateIssue" in l]

        def typed(num, type_id):
            node = f"I_node{num}"
            return num is not None and any(node in l and type_id in l for l in updates)

        check("CASE D: github.issue_types Bug->Story types the bugfix task's updateIssue "
              "IT_story", typed(issues.get("T-01"), "IT_story"),
              f"issues={issues} updates={updates}")
        check("CASE D: github.issue_types parent->Story types the parent's updateIssue "
              "IT_story", typed(fac.get("parent"), "IT_story"),
              f"parent={fac.get('parent')} updates={updates}")
        check("CASE D: Task is not overridden — the config task still types IT_task",
              typed(issues.get("T-02"), "IT_task"), f"issues={issues} updates={updates}")
        check("CASE D: Task is not overridden — the feature task (D-18) still types IT_task",
              typed(issues.get("T-03"), "IT_task"), f"issues={issues} updates={updates}")


def case_e():
    with tempfile.TemporaryDirectory() as td:
        root = make_root(td)
        gh = install_gh(td)
        fleet_path = build_fleet(td)
        feat_dir = stage(td)
        b64 = harness_json_b64()
        log1 = os.path.join(td, "run1.log")
        run_decompose(root, feat_dir, fleet_path, gh, log1, b64,
                      fake_types="available", fake_type_apply="fail")
        fac1 = read_factory(feat_dir)
        t01_num = fac1.get("issues", {}).get("T-01")
        check("CASE E: after the first run the bugfix task's issue number is recorded",
              t01_num is not None, fac1)
        typed1 = fac1.get("typed", {})
        check("CASE E: the number and the create-time provenance are written as the string "
              "'created' (not True, not absent) after a failed type-apply",
              typed1.get("T-01") == "created", f"typed={typed1!r}")

        log2 = os.path.join(td, "run2.log")
        run_decompose(root, feat_dir, fleet_path, gh, log2, b64, fake_types="available")
        loglines2 = read_log(log2)
        creates2 = [l for l in loglines2 if l.startswith("issue create")]
        check("CASE E: the rerun makes no second issue-create argv for that task",
              creates2 == [], creates2)
        updates2 = [l for l in loglines2 if "updateIssue" in l]
        node = f"I_node{t01_num}"
        check("CASE E: the rerun makes an updateIssue call for the recorded number",
              t01_num is not None and any(node in l for l in updates2), updates2)
        fac2 = read_factory(feat_dir)
        typed2 = fac2.get("typed", {})
        check("CASE E: the flag is promoted to True only after the rerun's apply succeeds",
              typed2.get("T-01") is True, f"typed={typed2!r}")


def case_f():
    with tempfile.TemporaryDirectory() as td:
        root = make_root(td)
        gh = install_gh(td)
        fleet_path = build_fleet(td)
        feat_dir = stage(td)
        b64 = harness_json_b64()
        log1 = os.path.join(td, "run1.log")
        run_decompose(root, feat_dir, fleet_path, gh, log1, b64, fake_types="available",
                      extra_args=["--parent", "4242"])
        fac1 = read_factory(feat_dir)
        check("CASE F: the parent is recorded as 4242 (adopted, not created)",
              fac1.get("parent") == 4242, fac1)
        updates1 = [l for l in read_log(log1) if "updateIssue" in l]
        check("CASE F: zero updateIssue argv carries the node id derived from 4242",
              not any("I_node4242" in l for l in updates1), updates1)
        typed1 = fac1.get("typed", {})
        check("CASE F: factory.yaml's typed mapping records the parent as the string "
              "'adopted'", typed1.get("parent") == "adopted", f"typed={typed1!r}")

        log2 = os.path.join(td, "run2.log")
        run_decompose(root, feat_dir, fleet_path, gh, log2, b64, fake_types="available")
        fac2 = read_factory(feat_dir)
        check("CASE F: rerun without --parent leaves the parent recorded as 4242 (not "
              "typed by us)", fac2.get("parent") == 4242, fac2)
        updates2 = [l for l in read_log(log2) if "updateIssue" in l]
        check("CASE F: rerun still makes zero updateIssue argv for node id 4242",
              not any("I_node4242" in l for l in updates2), updates2)
        typed2 = fac2.get("typed", {})
        check("CASE F: rerun marker is still 'adopted' — never True and never 'created'",
              typed2.get("parent") == "adopted", f"typed={typed2!r}")


def case_g():
    with tempfile.TemporaryDirectory() as td:
        root = make_root(td)
        gh = install_gh(td)
        fleet_path = build_fleet(td)
        feat_dir = stage(td)
        b64 = harness_json_b64()
        log1 = os.path.join(td, "run1.log")
        r1 = run_decompose(root, feat_dir, fleet_path, gh, log1, b64, fake_types="absent")
        check("CASE G: the first run exits 0", r1.returncode == 0,
              f"code={r1.returncode} stderr={r1.stderr!r}")

        log2 = os.path.join(td, "run2.log")
        r2 = run_decompose(root, feat_dir, fleet_path, gh, log2, b64, fake_types="absent")
        creates2 = [l for l in read_log(log2) if l.startswith("issue create")]
        check("CASE G: the rerun makes zero 'issue create' argv (everything already "
              "recorded)", creates2 == [], creates2)
        lines2 = diag_lines(r2)
        check("CASE G: the lazily-called-detector trap — the rerun's combined stdout+stderr "
              "still contains exactly one '^factory: issue types ' line, even though it "
              "created nothing", len(lines2) == 1, f"stdout={r2.stdout!r} stderr={r2.stderr!r}")


def case_h():
    with tempfile.TemporaryDirectory() as td:
        root = make_root(td)
        gh = install_gh(td)
        fleet_path = build_fleet(td)
        # The legacy shape: a parent and one task issue already recorded, full disposition
        # (item + edge already drawn), and — the point of the case — NO `typed` key at all,
        # the shape of every factory.yaml written before this feature ships.
        legacy = {
            "repo": REPO, "parent": 555, "issues": {"T-01": 556},
            "items": {"T-01": "ITEM_LEGACY"},
            "edges": {"parent": ["T-01"], "blocked_by": {"T-01": []}},
        }
        feat_dir = stage(td, factory=legacy)
        b64 = harness_json_b64()
        log1 = os.path.join(td, "run1.log")
        r1 = run_decompose(root, feat_dir, fleet_path, gh, log1, b64, fake_types="available")
        check("CASE H: the first run exits 0", r1.returncode == 0,
              f"code={r1.returncode} stderr={r1.stderr!r}")
        updates1 = [l for l in read_log(log1) if "updateIssue" in l]
        check("CASE H: zero updateIssue argv carries the node id derived from the recorded "
              "parent 555", not any("I_node555" in l for l in updates1), updates1)
        check("CASE H: zero updateIssue argv carries the node id derived from the recorded "
              "task issue 556", not any("I_node556" in l for l in updates1), updates1)
        fac1 = read_factory(feat_dir)
        typed1 = fac1.get("typed", {})
        check("CASE H: absent provenance is never typed — no typed entry for the parent "
              "afterwards", "parent" not in typed1, typed1)
        check("CASE H: absent provenance is never typed — no typed entry for the already-"
              "recorded task afterwards", "T-01" not in typed1, typed1)

        log2 = os.path.join(td, "run2.log")
        r2 = run_decompose(root, feat_dir, fleet_path, gh, log2, b64, fake_types="available")
        check("CASE H: the rerun still exits 0", r2.returncode == 0,
              f"code={r2.returncode} stderr={r2.stderr!r}")
        fac2 = read_factory(feat_dir)
        typed2 = fac2.get("typed", {})
        check("CASE H: rerun still leaves the parent untyped — absent provenance is unknown "
              "provenance on any later run too", "parent" not in typed2, typed2)
        check("CASE H: rerun still leaves the already-recorded task untyped",
              "T-01" not in typed2, typed2)
        new_nums = [fac2.get("issues", {}).get(tid) for tid in ("T-02", "T-03")]
        updates2 = [l for l in read_log(log2) if "updateIssue" in l]
        check("CASE H: the tasks that are NOT recorded (T-02, T-03) still get typed, "
              "proving the bound rather than a dead run",
              all(n is not None for n in new_nums)
              and all(any(f"I_node{n}" in l for l in updates2) for n in new_nums),
              f"issues={new_nums} updates={updates2}")


def case_i():
    with tempfile.TemporaryDirectory() as td:
        root = make_root(td)
        gh = install_gh(td)
        fleet_path = build_fleet(td)
        # A "created" remnant for the bugfix task, no item recorded (partial disposition) —
        # a legitimate member of the required-types set a correct backfill-aware
        # implementation would compute, and its type (Bug) IS declared by the partial fake.
        # The config and feature tasks are still "new" and both resolve to Task, which the
        # partial fake does NOT declare — the run must refuse before any create.
        remnant = {"repo": REPO, "issues": {"T-01": 701}, "typed": {"T-01": "created"}}
        feat_dir = stage(td, factory=remnant)
        b64 = harness_json_b64()
        log = os.path.join(td, "run.log")
        r = run_decompose(root, feat_dir, fleet_path, gh, log, b64, fake_types="partial")
        check("CASE I: REQ-07's refuse-before-create — the run exits non-zero",
              r.returncode != 0, f"code={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
        loglines = read_log(log)
        creates = [l for l in loglines if l.startswith("issue create")]
        check("CASE I: zero argv containing 'issue create' reached the fake — the parent's "
              "create included, since the refusal precedes every create", creates == [],
              creates)
        updates = [l for l in loglines if "updateIssue" in l]
        check("CASE I: zero argv containing updateIssue reached the fake", updates == [],
              updates)
        check("CASE I: specifically, zero updateIssue argv carries the node id derived from "
              "701", not any("I_node701" in l for l in updates), updates)
        combined = (r.stdout or "") + "\n" + (r.stderr or "")
        check("CASE I: the combined stdout+stderr names both 'Task' and 'github.issue_types'",
              "Task" in combined and "github.issue_types" in combined, combined)
        fac_after = read_factory(feat_dir)
        check("CASE I: factory.yaml afterwards records no parent number",
              fac_after.get("parent") is None, fac_after)
        check("CASE I: factory.yaml afterwards records no task issue number other than the "
              "seeded remnant", fac_after.get("issues", {}) == {"T-01": 701}, fac_after)
        typed_after = fac_after.get("typed", {})
        check("CASE I: the remnant is unchanged — T-01's recorded number is still 701 and "
              "its typed value is still exactly 'created', not True, not absent, not "
              "rewritten",
              fac_after.get("issues", {}).get("T-01") == 701
              and typed_after.get("T-01") == "created",
              f"issues={fac_after.get('issues')} typed={typed_after!r}")


def case_j():
    with tempfile.TemporaryDirectory() as td:
        root = make_root(td)
        gh = install_gh(td)
        fleet_path = build_fleet(td)
        # A FULL "created" remnant for the bugfix task (issue, item and edges all already
        # recorded) so this run creates nothing for it — FAKE_TYPES=nobug means every issue
        # this run WOULD create (the parent, needing Feature; the config and feature tasks,
        # both needing Task, D-18) already has a declared type, so the refusal can only come
        # from the backfill needing the undeclared Bug for the remnant.
        remnant = {
            "repo": REPO, "issues": {"T-01": 703}, "items": {"T-01": "ITEM_703"},
            "edges": {"parent": ["T-01"], "blocked_by": {"T-01": []}},
            "typed": {"T-01": "created"},
        }
        feat_dir = stage(td, factory=remnant)
        b64 = harness_json_b64()
        log = os.path.join(td, "run.log")
        r = run_decompose(root, feat_dir, fleet_path, gh, log, b64, fake_types="nobug")
        check("CASE J: the backfill is the sole source of a missing type — the run exits "
              "non-zero", r.returncode != 0,
              f"code={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
        loglines = read_log(log)
        creates = [l for l in loglines if l.startswith("issue create")]
        check("CASE J: zero argv containing 'issue create' reached the fake — the parent's "
              "create included", creates == [], creates)
        updates = [l for l in loglines if "updateIssue" in l]
        check("CASE J: zero argv containing updateIssue reached the fake", updates == [],
              updates)
        check("CASE J: specifically, zero updateIssue argv carries the node id derived from "
              "703", not any("I_node703" in l for l in updates), updates)
        combined = (r.stdout or "") + "\n" + (r.stderr or "")
        check("CASE J: the combined stdout+stderr names both 'Bug' and 'github.issue_types'",
              "Bug" in combined and "github.issue_types" in combined, combined)
        fac_after = read_factory(feat_dir)
        check("CASE J: factory.yaml afterwards records no parent number",
              fac_after.get("parent") is None, fac_after)
        check("CASE J: factory.yaml afterwards records no task issue number other than the "
              "seeded remnant", fac_after.get("issues", {}) == {"T-01": 703}, fac_after)
        typed_after = fac_after.get("typed", {})
        check("CASE J: the remnant is unchanged — 703 is still recorded and its typed value "
              "is still exactly 'created', not True, not absent, not rewritten",
              fac_after.get("issues", {}).get("T-01") == 703
              and typed_after.get("T-01") == "created",
              f"issues={fac_after.get('issues')} typed={typed_after!r}")


case_a_b()
case_c()
case_d()
case_e()
case_f()
case_g()
case_h()
case_i()
case_j()

print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
