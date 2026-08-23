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
    # board is an EXPLICIT null (FEAT-24 D-07): an absent board key now raises FleetError
    # from gh_board.load_board, and this fixture is about the OPEN lifecycle, not boards.
    g = {"sync": sync, "board": None}
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
    write_feature_json(os.path.join(feat, "feature.json"), feature_id=feat_name)
    return feat


def write_feature_json(path, **fields):
    """Write a minimal feature.json fixture. `feature_id` and `status` default; any keyword
    (including `github`) overrides or adds a top-level key."""
    doc = {"feature_id": fields.pop("feature_id", "FEAT-05-export-fix"),
           "status": fields.pop("status", "Building")}
    doc.update(fields)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)


def read_feature_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


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


FAKE_GH_STATIONS = """#!/bin/bash
echo "$*" | tr '\n' '\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
case "$*" in
  *"sub_issues -F sub_issue_id="*)
    echo '{}'
    exit 0 ;;
  *"--jq .id"*)
    num=$(echo "$*" | grep -oE 'issues/[0-9]+' | head -1 | grep -oE '[0-9]+')
    echo "9000$num"
    exit 0 ;;
  *"ProjectV2SingleSelectField"*)
    printf '{"data":{"repositoryOwner":{"__typename":"User","projectV2":{"id":"PVT_PROJ","field":{"id":"FIELD_STATUS","name":"Status","options":[{"id":"OPT_BACKLOG","name":"Backlog"},{"id":"OPT_PLAN","name":"Plan"},{"id":"OPT_READY","name":"Ready"},{"id":"OPT_BUILDING","name":"Building"},{"id":"OPT_REVIEW","name":"Review"},{"id":"OPT_DONE","name":"Done"}]}}}}}\\n'
    exit 0 ;;
  *"items(first: 100, after:"*)
    # T-07's guard read (gh_board.board_stations). GUARD_ISSUE/GUARD_STATION_NAME/GUARD_STATE
    # default to empty when unset — an unset GUARD_STATION_NAME reports no station (null),
    # never "Done", and an unset GUARD_STATE reports open (not "CLOSED"), so a case that
    # sets none of them (the pre-existing start-task fixture) exercises the guard's happy
    # path without changing its own assertions.
    if [ -z "$GUARD_STATION_NAME" ]; then
      fv=null
    else
      fv='{"name":"'"$GUARD_STATION_NAME"'"}'
    fi
    num="${GUARD_ISSUE:-326}"
    printf '{"data":{"user":{"projectV2":{"items":{"totalCount":1,"pageInfo":{"hasNextPage":false,"endCursor":null},"nodes":[{"content":{"number":%s,"repository":{"nameWithOwner":"implentio/fake"}},"fieldValueByName":%s}]}}}}}\\n' "$num" "$fv"
    exit 0 ;;
  *"projectItems(first: 100)"*)
    num=$(echo "$*" | grep -oE 'number=[0-9]+' | tail -1 | grep -oE '[0-9]+')
    printf '{"data":{"repository":{"issue":{"projectItems":{"totalCount":1,"nodes":[{"id":"ITEM_%s","project":{"number":3}}]}}}}}\\n' "$num"
    exit 0 ;;
  *"project item-edit"*)
    exit 0 ;;
esac
case "$1 $2" in
  "auth status") exit 0 ;;
  "issue view")
    printf '{"state":"%s"}\\n' "${GUARD_STATE:-OPEN}"
    exit 0 ;;
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

# Same as FAKE_GH_STATIONS, except the guard's board read (`items(first: 100, after:`) fails —
# proves a gh/network failure DURING THE GUARD ITSELF must not gate: the guard read is caught,
# printed, and start-task falls through to its ORIGINAL behaviour (still writes the station).
FAKE_GH_STATIONS_GUARD_READ_FAILS = """#!/bin/bash
echo "$*" | tr '\n' '\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
case "$*" in
  *"sub_issues -F sub_issue_id="*)
    echo '{}'
    exit 0 ;;
  *"--jq .id"*)
    num=$(echo "$*" | grep -oE 'issues/[0-9]+' | head -1 | grep -oE '[0-9]+')
    echo "9000$num"
    exit 0 ;;
  *"ProjectV2SingleSelectField"*)
    printf '{"data":{"repositoryOwner":{"__typename":"User","projectV2":{"id":"PVT_PROJ","field":{"id":"FIELD_STATUS","name":"Status","options":[{"id":"OPT_BACKLOG","name":"Backlog"},{"id":"OPT_PLAN","name":"Plan"},{"id":"OPT_READY","name":"Ready"},{"id":"OPT_BUILDING","name":"Building"},{"id":"OPT_REVIEW","name":"Review"},{"id":"OPT_DONE","name":"Done"}]}}}}}\\n'
    exit 0 ;;
  *"items(first: 100, after:"*)
    echo "simulated network failure" >&2
    exit 1 ;;
  *"projectItems(first: 100)"*)
    num=$(echo "$*" | grep -oE 'number=[0-9]+' | tail -1 | grep -oE '[0-9]+')
    printf '{"data":{"repository":{"issue":{"projectItems":{"totalCount":1,"nodes":[{"id":"ITEM_%s","project":{"number":3}}]}}}}}\\n' "$num"
    exit 0 ;;
  *"project item-edit"*)
    exit 0 ;;
esac
case "$1 $2" in
  "auth status") exit 0 ;;
  "issue view")
    printf '{"state":"%s"}\\n' "${GUARD_STATE:-OPEN}"
    exit 0 ;;
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

# Custom station spellings (T-07's de-hardcoding requirement): the field's "Building" OPTION
# is renamed to "Doing"/OPT_DOING, so a re-hardcoding of the literal string "Building" at the
# call site would select an option this board does not offer and the write would fail (or, if
# selected by an unguarded literal string comparison, silently write the wrong option).
FAKE_GH_STATIONS_CUSTOM = """#!/bin/bash
echo "$*" | tr '\n' '\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
case "$*" in
  *"sub_issues -F sub_issue_id="*)
    echo '{}'
    exit 0 ;;
  *"--jq .id"*)
    num=$(echo "$*" | grep -oE 'issues/[0-9]+' | head -1 | grep -oE '[0-9]+')
    echo "9000$num"
    exit 0 ;;
  *"ProjectV2SingleSelectField"*)
    printf '{"data":{"repositoryOwner":{"__typename":"User","projectV2":{"id":"PVT_PROJ","field":{"id":"FIELD_STATUS","name":"Status","options":[{"id":"OPT_TODO","name":"Todo"},{"id":"OPT_PLANNED","name":"Planned"},{"id":"OPT_QUEUED","name":"Queued"},{"id":"OPT_DOING","name":"Doing"},{"id":"OPT_CHECKING","name":"Checking"},{"id":"OPT_SHIPPED","name":"Shipped"}]}}}}}\\n'
    exit 0 ;;
  *"items(first: 100, after:"*)
    if [ -z "$GUARD_STATION_NAME" ]; then
      fv=null
    else
      fv='{"name":"'"$GUARD_STATION_NAME"'"}'
    fi
    num="${GUARD_ISSUE:-326}"
    printf '{"data":{"user":{"projectV2":{"items":{"totalCount":1,"pageInfo":{"hasNextPage":false,"endCursor":null},"nodes":[{"content":{"number":%s,"repository":{"nameWithOwner":"implentio/fake"}},"fieldValueByName":%s}]}}}}}\\n' "$num" "$fv"
    exit 0 ;;
  *"projectItems(first: 100)"*)
    num=$(echo "$*" | grep -oE 'number=[0-9]+' | tail -1 | grep -oE '[0-9]+')
    printf '{"data":{"repository":{"issue":{"projectItems":{"totalCount":1,"nodes":[{"id":"ITEM_%s","project":{"number":3}}]}}}}}\\n' "$num"
    exit 0 ;;
  *"project item-edit"*)
    exit 0 ;;
esac
case "$1 $2" in
  "auth status") exit 0 ;;
  "issue view")
    printf '{"state":"%s"}\\n' "${GUARD_STATE:-OPEN}"
    exit 0 ;;
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

# Same board reads/writes, but `project item-edit` — the actual station write — fails while
# every other gh call (including a subsequent `issue close`) still succeeds. This is what pins
# D-02's loud-but-non-terminal rule: one stderr ERROR line, and everything after it still runs.
FAKE_GH_STATIONS_ITEM_EDIT_FAILS = """#!/bin/bash
echo "$*" | tr '\n' '\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
case "$*" in
  *"sub_issues -F sub_issue_id="*)
    echo '{}'
    exit 0 ;;
  *"--jq .id"*)
    num=$(echo "$*" | grep -oE 'issues/[0-9]+' | head -1 | grep -oE '[0-9]+')
    echo "9000$num"
    exit 0 ;;
  *"ProjectV2SingleSelectField"*)
    printf '{"data":{"repositoryOwner":{"__typename":"User","projectV2":{"id":"PVT_PROJ","field":{"id":"FIELD_STATUS","name":"Status","options":[{"id":"OPT_BACKLOG","name":"Backlog"},{"id":"OPT_PLAN","name":"Plan"},{"id":"OPT_READY","name":"Ready"},{"id":"OPT_BUILDING","name":"Building"},{"id":"OPT_REVIEW","name":"Review"},{"id":"OPT_DONE","name":"Done"}]}}}}}\\n'
    exit 0 ;;
  *"projectItems(first: 100)"*)
    num=$(echo "$*" | grep -oE 'number=[0-9]+' | tail -1 | grep -oE '[0-9]+')
    printf '{"data":{"repository":{"issue":{"projectItems":{"totalCount":1,"nodes":[{"id":"ITEM_%s","project":{"number":3}}]}}}}}\\n' "$num"
    exit 0 ;;
  *"project item-edit"*)
    echo "simulated item-edit failure" >&2
    exit 1 ;;
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

# Same board reads/writes, station write succeeds, but `issue close` fails — this is the
# fixture that pins the ORDERING in close-task: the parent write must already have happened
# by the time this failure is hit.
FAKE_GH_STATIONS_CLOSE_FAILS = """#!/bin/bash
echo "$*" | tr '\n' '\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
case "$*" in
  *"sub_issues -F sub_issue_id="*)
    echo '{}'
    exit 0 ;;
  *"--jq .id"*)
    num=$(echo "$*" | grep -oE 'issues/[0-9]+' | head -1 | grep -oE '[0-9]+')
    echo "9000$num"
    exit 0 ;;
  *"ProjectV2SingleSelectField"*)
    printf '{"data":{"repositoryOwner":{"__typename":"User","projectV2":{"id":"PVT_PROJ","field":{"id":"FIELD_STATUS","name":"Status","options":[{"id":"OPT_BACKLOG","name":"Backlog"},{"id":"OPT_PLAN","name":"Plan"},{"id":"OPT_READY","name":"Ready"},{"id":"OPT_BUILDING","name":"Building"},{"id":"OPT_REVIEW","name":"Review"},{"id":"OPT_DONE","name":"Done"}]}}}}}\\n'
    exit 0 ;;
  *"projectItems(first: 100)"*)
    num=$(echo "$*" | grep -oE 'number=[0-9]+' | tail -1 | grep -oE '[0-9]+')
    printf '{"data":{"repository":{"issue":{"projectItems":{"totalCount":1,"nodes":[{"id":"ITEM_%s","project":{"number":3}}]}}}}}\\n' "$num"
    exit 0 ;;
  *"project item-edit"*)
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
  "issue close")
    echo "simulated close failure" >&2
    exit 1 ;;
  "label create") exit 0 ;;
esac
exit 0
"""


FULL_STATIONS = {"backlog": "Backlog", "plan": "Plan", "ready": "Ready", "building": "Building",
                  "review": "Review", "done": "Done"}


def write_harness_json_board(tmp, sync=True, repo="implentio/fake", board=True, stations=None):
    """harness.json's github block, carrying T-02's `board` sub-mapping when `board` is True,
    or an EXPLICIT null (FEAT-24 D-07 — the one non-error "no board" shape) when `board` is
    False. An absent `board` key is a different, REJECTED shape (FleetError) and is not what
    this helper's `board=False` means; nothing in this file drives that shape through here.

    `stations` OPTIONAL (T-07): defaults to FULL_STATIONS, but a caller proving the guard's
    write is de-hardcoded (rather than re-hardcoded to the literal "Building") passes a
    six-key map whose `building` value is something else entirely."""
    g = {"sync": sync}
    if repo:
        g["repo"] = repo
    g["board"] = ({"owner": "mruangutai", "number": 3, "station_field": "Status",
                    "stations": dict(stations or FULL_STATIONS)} if board else None)
    json.dump({"github": g}, open(os.path.join(tmp, ".harness", "harness.json"), "w"))


def write_plan_yaml(feat_dir, feat_name, task_statuses, source_issues=None):
    """A minimal plan.yaml — every REQUIRED_TASK_FIELDS key present — carrying only the
    `status` values a test cares about. Written as JSON text: JSON is valid YAML and this
    avoids a second parser dependency in the test file itself.

    `source_issues` is OPTIONAL (T-02, FEAT-26) so every existing caller is unchanged when
    it is omitted; when given, it is written as plan.yaml's own top-level `source_issues`
    key, exactly the shape `parse_source_issues` reads."""
    doc = {
        "schema": "plan/1",
        "feature": feat_name,
        "tasks": [
            {"id": tid, "title": tid, "change_type": "logic", "execution_mode": "team",
             "files": ["dummy.py"], "verify": "true", "intent": "fixture", "status": status}
            for tid, status in task_statuses
        ],
    }
    if source_issues is not None:
        doc["source_issues"] = source_issues
    with open(os.path.join(feat_dir, "plan.yaml"), "w", encoding="utf-8") as f:
        json.dump(doc, f)


def stage_station(tmp, feat_name, task_statuses, board=True, sync=True, repo="implentio/fake",
                   feature_status="Building", issues=None, parent=40, milestone=7, stations=None):
    """A plan.yaml-backed feature, wired for the T-03 station-write tests: harness.json's
    github.board (optionally), a plan.yaml carrying the given task statuses, and a
    feature.json recording the given issues/parent so `load_recorded` needs no live sync."""
    feat = os.path.join(tmp, ".harness", "features", feat_name)
    os.makedirs(feat)
    write_harness_json_board(tmp, sync=sync, repo=repo, board=board, stations=stations)
    open(os.path.join(feat, "BRIEF.md"), "w").write(f"""# BRIEF — {feat_name} — station fixture

## Problem
Station fixture.

## Goal
Station fixture.

## Requirements
- REQ-01: station writes route correctly.

## Success Criteria
- SC-01: covered by test-gh-sync.py. verify: automated

## Approval

status: approved
""")
    write_plan_yaml(feat, feat_name, task_statuses)
    write_feature_json(
        os.path.join(feat, "feature.json"),
        feature_id=feat_name, status=feature_status,
        github={"milestone": milestone, "parent": parent, "parent_origin": "created",
                "attached": list((issues or {}).keys()), "issues": issues or {}},
    )
    return feat


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
    json.dump({"github": {"sync": True, "repo": "implentio/fake", "board": None}},
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
    doc = read_feature_json(os.path.join(feat, "feature.json"))
    gh = doc.get("github") or {}
    check("issue numbers recorded in feature.json",
          gh.get("milestone") == 7
          and re.match(r"^4\d$", str((gh.get("issues") or {}).get("T-01"))), doc)
    check("created parent records origin created", gh.get("parent_origin") == "created", doc)

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
    # feature.json already carried the milestone before the last issue was created:
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
    r = run(["open", feat3, "--parent", "55"], tmp3)
    log3 = calls(tmp3)
    parent_creates3 = [l for l in log3 if "issue create" in l and not re.search(r"\bT-0\d\b", l)]
    doc3 = read_feature_json(os.path.join(feat3, "feature.json"))
    gh3 = doc3.get("github") or {}
    check("--parent adopts",
          r.returncode == 0 and len(parent_creates3) == 0 and gh3.get("parent") == 55, doc3)
    check("adopted parent records origin adopted", gh3.get("parent_origin") == "adopted", doc3)

# --- crash resume: recorded-but-unattached task is attached, not re-created;
#     and the pre-existing parent + its origin survive every per-task save
with tempfile.TemporaryDirectory() as tmp4:
    install_gh(tmp4)
    feat4 = stage(tmp4)
    write_feature_json(
        os.path.join(feat4, "feature.json"),
        feature_id="FEAT-05-export-fix",
        github={"milestone": 7, "parent": 40, "parent_origin": "created", "attached": [],
                "issues": {"T-01": 999}},
    )
    r = run(["open", feat4], tmp4)
    log4 = calls(tmp4)
    check("recorded-not-attached task is attached on re-run",
          r.returncode == 0
          and not any("issue create" in l and "T-01" in l for l in log4)
          and sum(1 for l in log4 if "sub_issue_id=9000999" in l) == 1,
          str(log4))
    doc4 = read_feature_json(os.path.join(feat4, "feature.json"))
    gh4 = doc4.get("github") or {}
    issues4 = gh4.get("issues") or {}
    check("pre-existing parent survives per-task saves",
          gh4.get("parent") == 40 and issues4.get("T-01") == 999
          and re.match(r"^4\d$", str(issues4.get("T-02")))
          and re.match(r"^4\d$", str(issues4.get("T-03"))),
          doc4)
    check("parent_origin survives per-task saves", gh4.get("parent_origin") == "created", doc4)

# --- a phrase containing its own em-dash is taken whole, not truncated at the second one
with tempfile.TemporaryDirectory() as tmp5:
    install_gh(tmp5)
    feat5 = stage(tmp5, phrase="streaming export — v2")
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
    r = run(["open", feat6], tmp6)
    doc6 = read_feature_json(os.path.join(feat6, "feature.json"))
    gh6 = doc6.get("github") or {}
    check("failed attach is a SKIP, exit 0, for the new subcommand too (SC-12)",
          r.returncode == 0 and "SKIP" in r.stdout, r.stdout)
    check("issue recorded before the failed attach survives the crash",
          re.match(r"^4\d$", str((gh6.get("issues") or {}).get("T-01"))) is not None, doc6)

# --- abandon: adopted parent stays open, subs + milestone close not_planned/closed
with tempfile.TemporaryDirectory() as tmpA:
    install_gh(tmpA)
    featA = stage(tmpA, feat_name="FEAT-06-abandon-adopted")
    write_feature_json(
        os.path.join(featA, "feature.json"),
        feature_id="FEAT-06-abandon-adopted",
        github={"milestone": 7, "parent": 40, "parent_origin": "adopted",
                "attached": ["T-01", "T-02", "T-03"],
                "issues": {"T-01": 41, "T-02": 42, "T-03": 43}},
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
    write_feature_json(
        os.path.join(featB, "feature.json"),
        feature_id="FEAT-06-abandon-created",
        github={"milestone": 7, "parent": 40, "parent_origin": "created",
                "attached": ["T-01"], "issues": {"T-01": 41}},
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
#     and cmd_abandon must not back-fill the absent parent_origin line (it now writes a
#     top-level status field, T-01/FEAT-23, but the github block's parent_origin stays absent)
with tempfile.TemporaryDirectory() as tmpC:
    install_gh(tmpC)
    featC = stage(tmpC, feat_name="FEAT-06-abandon-noorigin")
    write_feature_json(
        os.path.join(featC, "feature.json"),
        feature_id="FEAT-06-abandon-noorigin",
        github={"milestone": 7, "parent": 40, "attached": ["T-01"], "issues": {"T-01": 41}},
    )
    reasonC = os.path.join(tmpC, "reason.txt")
    open(reasonC, "w").write("cutting this too")
    r = run(["abandon", featC, "--reason-file", reasonC], tmpC)
    logC = calls(tmpC)
    docC = read_feature_json(os.path.join(featC, "feature.json"))
    ghC = docC.get("github") or {}
    check("abandon leaves a parent with no recorded origin open",
          r.returncode == 0
          and not any(re.search(r"\bissues/40\b", l) for l in logC)
          and not any(l.startswith("issue close 40") for l in logC)
          and "parent_origin" not in ghC,
          str(logC) + " | " + str(docC))

# --- abandon: caller errors on a bad or missing --reason-file
with tempfile.TemporaryDirectory() as tmpD:
    install_gh(tmpD)
    featD = stage(tmpD, feat_name="FEAT-06-abandon-badfile")
    write_feature_json(
        os.path.join(featD, "feature.json"),
        feature_id="FEAT-06-abandon-badfile",
        github={"milestone": 7, "parent": None, "attached": [], "issues": {"T-01": 41}},
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
    write_feature_json(
        os.path.join(featE, "feature.json"),
        feature_id="FEAT-06-abandon-nomilestone",
        status="Review",
        github={"milestone": None, "parent": None, "attached": [], "issues": {"T-01": 41}},
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
    # T-01/FEAT-23: the exact conjunction the write must not be re-gated on — no milestone
    # (which alone would `skip()` if abandon had no issues) but WITH issues recorded, so
    # cmd_abandon's real early exit (milestone is None AND no issues) does not fire, and a
    # milestone-only guard on the status write would wrongly skip it here.
    docE = read_feature_json(os.path.join(featE, "feature.json"))
    check("abandon with no milestone but WITH issues still records status Abandoned",
          docE.get("status") == "Abandoned", docE)

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
    write_feature_json(
        os.path.join(featG, "feature.json"),
        feature_id="FEAT-07-ship-created",
        github={"milestone": 7, "parent": 40, "parent_origin": "created",
                "attached": ["T-01"], "issues": {"T-01": 41}},
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
    write_feature_json(
        os.path.join(featH, "feature.json"),
        feature_id="FEAT-07-ship-adopted",
        github={"milestone": 7, "parent": 40, "parent_origin": "adopted",
                "attached": ["T-01"], "issues": {"T-01": 41}},
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
    write_feature_json(
        os.path.join(featI, "feature.json"),
        feature_id="FEAT-07-ship-noorigin",
        github={"milestone": 7, "parent": 40, "attached": ["T-01"], "issues": {"T-01": 41}},
    )
    r = run(["ship", featI], tmpI)
    logI = calls(tmpI)
    docI = read_feature_json(os.path.join(featI, "feature.json"))
    ghI = docI.get("github") or {}
    check("ship leaves a parent with no recorded origin open",
          r.returncode == 0
          and not any(l.startswith("issue close 40") for l in logI)
          and not any(re.search(r"\bissues/40\b", l) for l in logI)
          and any("milestones/7" in l and "state=closed" in l for l in logI)
          and "parent_origin" not in ghI,
          str(logI) + " | " + str(docI))

# --- ship --body-file posts once, on an adopted parent, so the UNCONDITIONALITY of the
#     comment (vs. the conditional close) is what is being checked
with tempfile.TemporaryDirectory() as tmpJ:
    install_gh(tmpJ)
    featJ = stage(tmpJ, feat_name="FEAT-07-ship-bodyfile")
    write_feature_json(
        os.path.join(featJ, "feature.json"),
        feature_id="FEAT-07-ship-bodyfile",
        github={"milestone": 7, "parent": 40, "parent_origin": "adopted",
                "attached": ["T-01"], "issues": {"T-01": 41}},
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
    write_feature_json(
        os.path.join(featK, "feature.json"),
        feature_id="FEAT-07-ship-nobodyfile",
        github={"milestone": 7, "parent": 40, "parent_origin": "adopted",
                "attached": ["T-01"], "issues": {"T-01": 41}},
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
    write_feature_json(
        os.path.join(featL, "feature.json"),
        feature_id="FEAT-07-ship-emptybodyfile",
        github={"milestone": 7, "parent": 40, "parent_origin": "adopted",
                "attached": ["T-01"], "issues": {"T-01": 41}},
    )
    emptyL = os.path.join(tmpL, "empty.txt")
    open(emptyL, "w").close()
    r = run(["ship", featL, "--body-file", emptyL], tmpL)
    logL = [l for l in calls(tmpL) if l]
    check("ship with an empty body file exits 1",
          r.returncode == 1 and all(l.startswith("auth") for l in logL),
          str(logL))

# --- T-05 (FEAT-14): `open` against a genuine eleven-key feature.json, end to end through the
#     real subcommand (not a direct save_recorded call) — every key outside `github` survives
with tempfile.TemporaryDirectory() as tmpM:
    install_gh(tmpM)
    featM = stage(tmpM, feat_name="FEAT-08-eleven-key")
    write_feature_json(
        os.path.join(featM, "feature.json"),
        feature_id="FEAT-08-eleven-key",
        branch="feat/08-eleven-key",
        pr=None,
        status="Plan",
        review_sha="none",
        cycles_used=0,
        max_total_cycles=10,
        max_total_runs=20,
        runs=[],
    )
    r = run(["open", featM], tmpM)
    docM = read_feature_json(os.path.join(featM, "feature.json"))
    check("(eleven-key) open exits 0", r.returncode == 0, r.stdout + r.stderr)
    check("(eleven-key) every non-github key survives untouched",
          docM.get("branch") == "feat/08-eleven-key" and docM.get("pr") is None
          and docM.get("status") == "Plan" and docM.get("review_sha") == "none"
          and docM.get("cycles_used") == 0 and docM.get("max_total_cycles") == 10
          and docM.get("max_total_runs") == 20 and docM.get("runs") == [],
          docM)
    check("(eleven-key) a github block was written", "github" in docM, docM)

# ---------- T-06 Part C: load_recorded reads the github: block with a PARSER ----------
# Mandated by the plan and never written; found MISSING by the review panel (F-04) and
# confirmed by grep before being fixed here. Both cases are read-only — they call the
# function directly rather than driving a subcommand, because what is under test is the
# PARSE, not the GitHub calls.
#
# FEAT-14 fix1 (B-5) converged feature.json's reader on json.load, so the two fixtures
# below now carry JSON, not YAML-with-comments — JSON has no comments, so the old
# comment-tolerance assertion is retired by design, not lost as a regression. What still
# means something (a QUOTED "7" milestone routing through _opt_int) is kept.

import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "_ghs", os.path.join(os.path.dirname(os.path.abspath(__file__)), "gh-sync.py"))
_ghs = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_ghs)

# 1. A populated github: block, including a QUOTED milestone number — _opt_int must still
#    coerce it. This is row 3 of the fix1 spec's table: "file present with a github
#    mapping -> load it, as today".
_d1 = tempfile.mkdtemp()
json.dump({
    "feature_id": "F1",
    "github": {
        "parent": 40,
        "milestone": "7",
        "parent_origin": "adopted",
        "attached": ["T-01"],
        "issues": {"T-01": 41},
    },
}, open(os.path.join(_d1, "feature.json"), "w"))
_rec = _ghs.load_recorded(_d1)
check("T-06C: a populated github: block loads, quoted milestone coerced by _opt_int",
      _rec["parent"] == 40 and _rec["milestone"] == 7
      and _rec["issues"] == {"T-01": 41} and _rec["attached"] == ["T-01"],
      str(_rec))

# 2. No github: block at all -> the all-None default, never a raise. gh-sync would
#    otherwise crash on any feature that has not been mirrored yet, which is most of
#    them. This is row 1 of the fix1 spec's table: file present, no github key -> a
#    legitimate first sync.
_d2 = tempfile.mkdtemp()
json.dump({"feature_id": "F2"}, open(os.path.join(_d2, "feature.json"), "w"))
_rec2 = _ghs.load_recorded(_d2)
check("T-06C: a feature.json with no github: block returns the default, does not raise",
      _rec2 == {"milestone": None, "parent": None, "parent_origin": None,
                "attached": [], "issues": {}, "source_issues": []},
      str(_rec2))

# ---------- fix1 Part B: three states must stay distinct, plus the fourth the operator's
# table did not enumerate. Collapse row 1 (legitimate first sync) into row 2 (error) and
# the first sync of every new feature is blocked forever; collapse row 2 into row 1 and
# the zero-byte-truncation bug (the defect this whole fix cycle exists for) is rebuilt.
# Every SystemExit case is asserted on the message too, not just "it raised" — a
# SystemExit from an unrelated crash would satisfy a bare pytest.raises just as well.

# Row 1a: file ABSENT entirely -> default rec, never a raise (already covered by cmd_open's
# happy path via stage(), asserted again here directly against load_recorded).
_dabsent = tempfile.mkdtemp()
_recAbsent = _ghs.load_recorded(_dabsent)
check("fix1 B row1a: absent feature.json returns the default rec, does not raise",
      _recAbsent == {"milestone": None, "parent": None, "parent_origin": None,
                     "attached": [], "issues": {}, "source_issues": []},
      str(_recAbsent))

# Row 1b: file present, a dict, but NO github: key -> default rec (already _d2 above,
# named here again for the fix1 spec's own enumeration).
check("fix1 B row1b: dict present with no github key returns the default rec",
      _rec2 == {"milestone": None, "parent": None, "parent_origin": None,
                "attached": [], "issues": {}, "source_issues": []},
      str(_rec2))

# Row 2: file present but a genuine ZERO-BYTE truncation -- the exact artifact
# save_recorded's pre-fix `open(p, "w")` guaranteed at open. THIS is the live truncation
# fixture the dispatch requires: a 0-byte record file must ERROR, not load as empty.
_dzero = tempfile.mkdtemp()
open(os.path.join(_dzero, "feature.json"), "w").close()
check("fix1 B row2: 0 bytes on disk",
      os.path.getsize(os.path.join(_dzero, "feature.json")) == 0, "fixture setup")
try:
    _ghs.load_recorded(_dzero)
    check("fix1 B row2: a 0-byte feature.json raises SystemExit, never loads as empty",
          False, "load_recorded returned instead of raising")
except SystemExit as e:
    check("fix1 B row2: a 0-byte feature.json raises SystemExit, never loads as empty",
          "does not parse" in str(e) or "cannot be known" in str(e), str(e))

# Row 2 (non-mapping document): a JSON document that parses fine but is not a mapping —
# a bare list or a bare scalar. Same bug shape as the zero-byte case: `.get` would not
# exist on either, so a naive fix could still fail OPEN by returning the default rec.
for _label, _body in (("a_list", "[1, 2]\n"), ("a_scalar", '"just a string"\n')):
    _dnm = tempfile.mkdtemp()
    open(os.path.join(_dnm, "feature.json"), "w").write(_body)
    try:
        _ghs.load_recorded(_dnm)
        check(f"fix1 B row2 ({_label}): a non-mapping document raises SystemExit", False,
              "load_recorded returned instead of raising")
    except SystemExit as e:
        check(f"fix1 B row2 ({_label}): a non-mapping document raises SystemExit",
              "does not parse" in str(e) or "cannot be known" in str(e)
              or "not a mapping" in str(e) or "mapping" in str(e),
              str(e))

# Row 4 (the operator's table does NOT enumerate this one): doc IS a dict, `github` IS
# present, but is not itself a mapping (a string or a list). Treated as row 2 — loud
# error — because the whole point is refusing to sync when what is mirrored cannot be
# known. Pre-fix this silently returned the default rec at gh-sync.py:274-276.
for _label, _github_val in (("a_string", "not-a-mapping"), ("a_list", ["T-01", 41])):
    _dgh = tempfile.mkdtemp()
    json.dump({"feature_id": "F-row4", "github": _github_val},
              open(os.path.join(_dgh, "feature.json"), "w"))
    try:
        _ghs.load_recorded(_dgh)
        check(f"fix1 B row4 (github={_label}): a non-mapping github: value raises "
              f"SystemExit", False, "load_recorded returned instead of raising")
    except SystemExit as e:
        check(f"fix1 B row4 (github={_label}): a non-mapping github: value raises "
              f"SystemExit", len(str(e)) > 0, str(e))

# ---------- fix1 Part A: save_recorded must be ATOMIC — feature.json is never observable
# in a partial or empty state. Proven by forcing json.dump to fail PARTWAY through the
# write, with a real pre-existing file on disk: a truncating `open(p, "w")` has already
# destroyed the original bytes by the time json.dump raises; os.replace has not.
_datomic = tempfile.mkdtemp()
_atomic_path = os.path.join(_datomic, "feature.json")
_original_doc = {"feature_id": "F-atomic", "status": "Building"}
json.dump(_original_doc, open(_atomic_path, "w"))
with open(_atomic_path, "rb") as _f:
    _original_bytes = _f.read()

# A set() is not JSON-serializable — json.dump raises TypeError partway through encoding
# the `github` value, after any truncating open() would already have destroyed the file.
_bad_rec = {"milestone": 9, "parent": 40, "parent_origin": "created",
            "attached": ["T-01"], "issues": {"T-01": {1, 2, 3}}, "source_issues": []}
try:
    _ghs.save_recorded(_datomic, _bad_rec)
except (TypeError, Exception):
    pass
with open(_atomic_path, "rb") as _f:
    _after_bytes = _f.read()
check("fix1 A: a failed save_recorded leaves feature.json byte-identical, never truncated",
      _after_bytes == _original_bytes,
      f"before={_original_bytes!r} after={_after_bytes!r}")
# No temp file left behind either — the except BaseException cleanup path.
_leftover = [f for f in os.listdir(_datomic) if f != "feature.json"]
check("fix1 A: no leftover temp file after a failed save_recorded", _leftover == [],
      str(_leftover))

# ---------- review finding 2: save_recorded is a JSON read-modify-write, so a duplicate
# github: block is structurally impossible (a dict has one "github" key by construction) —
# what matters now is that every key OUTSIDE github round-trips unchanged (T-05, FEAT-14). ----
_REC = {"milestone": 9, "parent": 40, "parent_origin": "created",
        "attached": ["T-01"], "issues": {"T-01": 41}, "source_issues": []}
for _label, _doc in (
        ("no github block yet", {"feature_id": "F1", "status": "Building"}),
        ("an existing github block",
         {"feature_id": "F1", "status": "Building",
          "github": {"milestone": 1, "parent": 2, "parent_origin": None, "attached": [],
                     "issues": {}}}),
        ("other keys present",
         {"feature_id": "F1", "status": "Building", "review_sha": "abc1234",
          "cycles_used": 3})):
    _d = tempfile.mkdtemp()
    with open(os.path.join(_d, "feature.json"), "w", encoding="utf-8") as f:
        json.dump(_doc, f)
    _ghs.save_recorded(_d, _REC)
    with open(os.path.join(_d, "feature.json"), encoding="utf-8") as f:
        _after = json.load(f)
    _n = sum(1 for k in _after if k == "github")
    _ok = (_n == 1 and _after["github"]["parent"] == 40 and _after["github"]["milestone"] == 9
           and _after.get("feature_id") == "F1" and _after.get("status") == "Building")
    check(f"finding 2: save_recorded round-trips a feature.json with {_label}", _ok,
          f"{_n} github keys, result {_after}")

# ---------- T-03: gh-sync station writes ----------
# BOTH GH_SYNC_GH and FACTORY_GH point at the same fake in every case below — gh_board's
# calls go through factory_gh, which reads FACTORY_GH, not GH_SYNC_GH (the fake-binary trap
# documented at the top of gh_board.py).

# --- start-task sets the sub-issue's station to Building, then the parent's (D-04) —
#     two field-sets, distinguishable by item id, never by counting calls.
with tempfile.TemporaryDirectory() as tmpN:
    install_gh(tmpN, FAKE_GH_STATIONS)
    featN = stage_station(
        tmpN, "FEAT-09-start-task",
        [("T-01", "done"), ("T-02", "building"), ("T-03", "pending")],
        issues={"T-01": 41, "T-02": 326},
        parent=40,
    )
    r = run(["start-task", featN, "T-02"], tmpN, {"FACTORY_GH": os.path.join(tmpN, "gh")})
    logN = calls(tmpN)
    edits = [l for l in logN if "project item-edit" in l]
    check("start-task exits 0", r.returncode == 0, r.stdout + r.stderr)
    check("start-task sets T-02's OWN issue station to Building",
          any("--id ITEM_326" in l and "--single-select-option-id OPT_BUILDING" in l
              for l in edits),
          str(edits))
    check("start-task then sets the PARENT's station to Building (distinct item id)",
          any("--id ITEM_40" in l and "--single-select-option-id OPT_BUILDING" in l
              for l in edits),
          str(edits))
    check("exactly two field-sets, one per item id",
          len(edits) == 2 and {"ITEM_326", "ITEM_40"} == {
              next(p for p in l.split() if p.startswith("ITEM_")) for l in edits},
          str(edits))

# ---------- T-07: start-task must not drive a CLOSED card, or one already at Done, backwards
# ----------

# --- REGRESSION, #642's exact shape: issue closed, card already at Done, start-task invoked
#     anyway. Must refuse: no station write of any kind reaches the fake (neither the
#     sub-issue's nor the parent's), and exactly the refusal line prints. Proven RED against
#     the pre-fix code separately (see the T-07 receipt) — this fixture is what reproduced it.
with tempfile.TemporaryDirectory() as tmpN2:
    install_gh(tmpN2, FAKE_GH_STATIONS)
    featN2 = stage_station(
        tmpN2, "FEAT-09-start-task-closed-done",
        [("T-01", "done"), ("T-02", "building"), ("T-03", "pending")],
        issues={"T-01": 41, "T-02": 326},
        parent=40,
    )
    r = run(["start-task", featN2, "T-02"], tmpN2,
            {"FACTORY_GH": os.path.join(tmpN2, "gh"),
             "GUARD_ISSUE": "326", "GUARD_STATE": "CLOSED", "GUARD_STATION_NAME": "Done"})
    logN2 = calls(tmpN2)
    check("#642 replay: exits 0 (a refusal is not a failure, D-02/DEC-146)",
          r.returncode == 0, r.stdout + r.stderr)
    check("#642 replay: no station write of any kind reaches the fake",
          not any("item-edit" in l for l in logN2), str(logN2))
    check("#642 replay: refuses, naming the issue, the task id, the current station and why",
          "gh-sync: refusing #326" in r.stdout and "T-02" in r.stdout and "Done" in r.stdout,
          r.stdout)

# --- an open issue at Backlog is still moved to Building — the guard changes nothing for the
#     case it was never meant to touch.
with tempfile.TemporaryDirectory() as tmpN3:
    install_gh(tmpN3, FAKE_GH_STATIONS)
    featN3 = stage_station(
        tmpN3, "FEAT-09-start-task-open-backlog",
        [("T-01", "done"), ("T-02", "building"), ("T-03", "pending")],
        issues={"T-01": 41, "T-02": 326},
        parent=40,
    )
    r = run(["start-task", featN3, "T-02"], tmpN3,
            {"FACTORY_GH": os.path.join(tmpN3, "gh"),
             "GUARD_ISSUE": "326", "GUARD_STATE": "OPEN", "GUARD_STATION_NAME": "Backlog"})
    logN3 = calls(tmpN3)
    editsN3 = [l for l in logN3 if "project item-edit" in l]
    check("open at Backlog: exits 0", r.returncode == 0, r.stdout + r.stderr)
    check("open at Backlog: still writes the sub-issue's station to Building",
          any("--id ITEM_326" in l and "--single-select-option-id OPT_BUILDING" in l
              for l in editsN3),
          str(editsN3))
    check("open at Backlog: still writes the parent's station too",
          any("--id ITEM_40" in l and "--single-select-option-id OPT_BUILDING" in l
              for l in editsN3),
          str(editsN3))

# --- an OPEN issue whose card already reads Done is refused — the card's current station
#     alone is sufficient, independent of the issue's open/closed state.
with tempfile.TemporaryDirectory() as tmpN4:
    install_gh(tmpN4, FAKE_GH_STATIONS)
    featN4 = stage_station(
        tmpN4, "FEAT-09-start-task-open-done",
        [("T-01", "done"), ("T-02", "building"), ("T-03", "pending")],
        issues={"T-01": 41, "T-02": 326},
        parent=40,
    )
    r = run(["start-task", featN4, "T-02"], tmpN4,
            {"FACTORY_GH": os.path.join(tmpN4, "gh"),
             "GUARD_ISSUE": "326", "GUARD_STATE": "OPEN", "GUARD_STATION_NAME": "Done"})
    logN4 = calls(tmpN4)
    check("open but card at Done: exits 0", r.returncode == 0, r.stdout + r.stderr)
    check("open but card at Done: refused, no station write reaches the fake",
          not any("item-edit" in l for l in logN4), str(logN4))
    check("open but card at Done: refusal line printed",
          "gh-sync: refusing #326" in r.stdout, r.stdout)

# --- a CLOSED issue whose card reads Building (not yet Done) is STILL refused — the issue's
#     state alone is sufficient, independent of the card's current station.
with tempfile.TemporaryDirectory() as tmpN5:
    install_gh(tmpN5, FAKE_GH_STATIONS)
    featN5 = stage_station(
        tmpN5, "FEAT-09-start-task-closed-building",
        [("T-01", "done"), ("T-02", "building"), ("T-03", "pending")],
        issues={"T-01": 41, "T-02": 326},
        parent=40,
    )
    r = run(["start-task", featN5, "T-02"], tmpN5,
            {"FACTORY_GH": os.path.join(tmpN5, "gh"),
             "GUARD_ISSUE": "326", "GUARD_STATE": "CLOSED", "GUARD_STATION_NAME": "Building"})
    logN5 = calls(tmpN5)
    check("closed but card at Building: exits 0", r.returncode == 0, r.stdout + r.stderr)
    check("closed but card at Building: refused, no station write reaches the fake",
          not any("item-edit" in l for l in logN5), str(logN5))
    check("closed but card at Building: refusal line printed",
          "gh-sync: refusing #326" in r.stdout, r.stdout)

# --- a board read that raises (network blip mid-guard) must NOT gate: falls through to the
#     original behaviour and still writes Building for both the sub-issue and the parent.
with tempfile.TemporaryDirectory() as tmpN6:
    install_gh(tmpN6, FAKE_GH_STATIONS_GUARD_READ_FAILS)
    featN6 = stage_station(
        tmpN6, "FEAT-09-start-task-guard-read-fails",
        [("T-01", "done"), ("T-02", "building"), ("T-03", "pending")],
        issues={"T-01": 41, "T-02": 326},
        parent=40,
    )
    r = run(["start-task", featN6, "T-02"], tmpN6, {"FACTORY_GH": os.path.join(tmpN6, "gh")})
    logN6 = calls(tmpN6)
    editsN6 = [l for l in logN6 if "project item-edit" in l]
    check("guard read fails: exits 0 (a failed guard read is not a gate either)",
          r.returncode == 0, r.stdout + r.stderr)
    check("guard read fails: falls through and still writes the sub-issue's station",
          any("--id ITEM_326" in l and "--single-select-option-id OPT_BUILDING" in l
              for l in editsN6),
          str(editsN6))
    check("guard read fails: falls through and still writes the parent's station",
          any("--id ITEM_40" in l and "--single-select-option-id OPT_BUILDING" in l
              for l in editsN6),
          str(editsN6))
    check("guard read fails: one ERROR line printed, not a silent swallow",
          "gh-sync: ERROR" in r.stderr and "326" in r.stderr, r.stderr)

# --- DE-HARDCODING: the board's `building` station is spelled "Doing", not "Building". A
#     re-hardcoded literal "Building" at the call site would select the wrong option (or
#     none at all); the write must select OPT_DOING, and the printed line must say "Doing".
CUSTOM_STATIONS = {"backlog": "Todo", "plan": "Planned", "ready": "Queued",
                    "building": "Doing", "review": "Checking", "done": "Shipped"}
with tempfile.TemporaryDirectory() as tmpN7:
    install_gh(tmpN7, FAKE_GH_STATIONS_CUSTOM)
    featN7 = stage_station(
        tmpN7, "FEAT-09-start-task-custom-stations",
        [("T-01", "done"), ("T-02", "building"), ("T-03", "pending")],
        issues={"T-01": 41, "T-02": 326},
        parent=40,
        stations=CUSTOM_STATIONS,
    )
    r = run(["start-task", featN7, "T-02"], tmpN7,
            {"FACTORY_GH": os.path.join(tmpN7, "gh"),
             "GUARD_ISSUE": "326", "GUARD_STATE": "OPEN", "GUARD_STATION_NAME": "Todo"})
    logN7 = calls(tmpN7)
    editsN7 = [l for l in logN7 if "project item-edit" in l]
    check("custom stations: exits 0", r.returncode == 0, r.stdout + r.stderr)
    check("custom stations: sets the sub-issue's station to the DECLARED building option "
          "(OPT_DOING), not the hardcoded literal OPT_BUILDING",
          any("--id ITEM_326" in l and "--single-select-option-id OPT_DOING" in l
              for l in editsN7)
          and not any("OPT_BUILDING" in l for l in editsN7),
          str(editsN7))
    check("custom stations: prints the declared name (\"Doing\"), never the literal \"Building\"",
          "-> Doing" in r.stdout and "-> Building" not in r.stdout,
          r.stdout)

# --- close-task on the last outstanding task sets the parent to Review and attempts the
#     sub-issue close — and the parent write happens even when the close FAILS, which pins
#     the ordering (parent write BEFORE the close) required by step 4.
with tempfile.TemporaryDirectory() as tmpO:
    install_gh(tmpO, FAKE_GH_STATIONS_CLOSE_FAILS)
    featO = stage_station(
        tmpO, "FEAT-09-close-last-task",
        [("T-01", "done"), ("T-02", "done"), ("T-03", "done")],
        issues={"T-01": 41, "T-02": 42, "T-03": 43},
        parent=40,
    )
    r = run(["close-task", featO, "T-03"], tmpO, {"FACTORY_GH": os.path.join(tmpO, "gh")})
    logO = calls(tmpO)
    editsO = [l for l in logO if "project item-edit" in l]
    check("close-task on the last task exits 0 even though the close fails (SKIP, not a gate)",
          r.returncode == 0, r.stdout + r.stderr)
    check("close-task sets the parent to Review",
          any("--id ITEM_40" in l and "--single-select-option-id OPT_REVIEW" in l
              for l in editsO),
          str(editsO))
    check("the sub-issue close was ATTEMPTED (and is the thing that failed)",
          any(l.startswith("issue close 43") for l in logO), str(logO))
    _parent_edit_idx = next((i for i, l in enumerate(logO) if "--id ITEM_40" in l), None)
    _close_idx = next((i for i, l in enumerate(logO) if l.startswith("issue close 43")), None)
    check("the parent write is ORDERED BEFORE the close in the log",
          _parent_edit_idx is not None and _close_idx is not None
          and _parent_edit_idx < _close_idx,
          str(logO))

# --- close-task on a feature whose feature.json status is Done writes NO station at all —
#     the terminal exemption (D-03/D-04) — even though the sub-issue itself still closes.
with tempfile.TemporaryDirectory() as tmpP:
    install_gh(tmpP, FAKE_GH_STATIONS)
    featP = stage_station(
        tmpP, "FEAT-09-done-exempt",
        [("T-01", "done")],
        issues={"T-01": 41},
        parent=40,
        feature_status="Done",
    )
    r = run(["close-task", featP, "T-01"], tmpP, {"FACTORY_GH": os.path.join(tmpP, "gh")})
    logP = calls(tmpP)
    check("close-task on a Done feature exits 0", r.returncode == 0, r.stdout + r.stderr)
    check("close-task on a Done feature makes no item-edit call at all",
          not any("item-edit" in l for l in logP), str(logP))
    check("close-task on a Done feature still closes the sub-issue",
          any(l.startswith("issue close 41") for l in logP), str(logP))

# --- THE LOUD PAIR (SC-04/D-02), one fixture per half, both required —
#     half 1: gh works but the station write (item-edit) fails -> exit 0, one ERROR line on
#     stderr naming the issue, AND the call that follows (the sub-issue close) still happens.
with tempfile.TemporaryDirectory() as tmpQ1:
    install_gh(tmpQ1, FAKE_GH_STATIONS_ITEM_EDIT_FAILS)
    featQ1 = stage_station(
        tmpQ1, "FEAT-09-loud-item-edit-fails",
        [("T-01", "done"), ("T-02", "done")],
        issues={"T-01": 41, "T-02": 42},
        parent=40,
    )
    r = run(["close-task", featQ1, "T-02"], tmpQ1, {"FACTORY_GH": os.path.join(tmpQ1, "gh")})
    logQ1 = calls(tmpQ1)
    check("loud pair (item-edit fails): process still exits 0", r.returncode == 0,
          r.stdout + r.stderr)
    check("loud pair (item-edit fails): stderr carries the gh-sync: ERROR line naming issue 40",
          "gh-sync: ERROR" in r.stderr and "40" in r.stderr, r.stderr)
    check("loud pair (item-edit fails): the issue call that follows it still happened",
          any(l.startswith("issue close 42") for l in logQ1), str(logQ1))

#     half 2: gh is absent from PATH entirely -> one SKIP line, exit 0, and no item-edit call
#     is even attempted — proving the failing half alone would be satisfied by a tool that
#     has simply stopped writing anything.
with tempfile.TemporaryDirectory() as tmpQ2:
    featQ2 = stage_station(
        tmpQ2, "FEAT-09-loud-gh-absent",
        [("T-01", "done"), ("T-02", "done")],
        issues={"T-01": 41, "T-02": 42},
        parent=40,
    )
    r = run(["close-task", featQ2, "T-02"], tmpQ2,
            {"GH_SYNC_GH": os.path.join(tmpQ2, "no-such-gh"),
             "FACTORY_GH": os.path.join(tmpQ2, "no-such-gh")})
    check("loud pair (gh absent): one SKIP line, exit 0",
          r.returncode == 0 and r.stdout.count("SKIP") == 1, r.stdout + r.stderr)
    check("loud pair (gh absent): no item-edit call is even attempted",
          not calls(tmpQ2), str(calls(tmpQ2)))

# --- a feature whose harness.json carries no github.board runs open and close-task
#     unchanged, exits 0, and makes no item-edit call — the environmental precondition (D-02).
with tempfile.TemporaryDirectory() as tmpR:
    install_gh(tmpR, FAKE_GH_STATIONS)
    featR = stage_station(
        tmpR, "FEAT-09-no-board",
        [("T-01", "done"), ("T-02", "building")],
        issues={},
        board=False,
    )
    r = run(["open", featR], tmpR, {"FACTORY_GH": os.path.join(tmpR, "gh")})
    check("no board configured: open exits 0", r.returncode == 0, r.stdout + r.stderr)
    check("no board configured: prints the plain no-board line, not a SKIP",
          "no github.board configured" in r.stdout and "SKIP" not in r.stdout,
          r.stdout + r.stderr)
    docR = read_feature_json(os.path.join(featR, "feature.json"))
    ghR = docR.get("github") or {}
    t1R = (ghR.get("issues") or {}).get("T-01")
    t2R = (ghR.get("issues") or {}).get("T-02")
    check("no board configured: open still recorded T-02's issue — the lifecycle ran, not skipped",
          t2R is not None, str(docR))
    r2 = run(["close-task", featR, "T-01"], tmpR, {"FACTORY_GH": os.path.join(tmpR, "gh")})
    logR = calls(tmpR)
    check("no board configured: close-task exits 0", r2.returncode == 0, r2.stdout + r2.stderr)
    check("no board configured: no item-edit call is ever made",
          not any("item-edit" in l for l in logR), str(logR))
    check("no board configured: close-task actually closed T-01's issue — the lifecycle ran",
          t1R is not None and any(l.startswith(f"issue close {t1R}") for l in logR), str(logR))

# --- an UNUSABLE board config (github.board missing station_field) is a LOUD failure of the
#     WHOLE invocation — exit 2, the offending key on stderr — not an environmental
#     precondition and not a skipped station write (FEAT-24 T-04, Part B item 4).
with tempfile.TemporaryDirectory() as tmpW:
    install_gh(tmpW, FAKE_GH_STATIONS)
    featW = stage_station(
        tmpW, "FEAT-24-unusable-board",
        [("T-01", "done")],
        issues={},
    )
    json.dump(
        {"github": {"sync": True, "repo": "implentio/fake",
                     "board": {"owner": "mruangutai", "number": 3}}},
        open(os.path.join(tmpW, ".harness", "harness.json"), "w"),
    )
    r = run(["open", featW], tmpW, {"FACTORY_GH": os.path.join(tmpW, "gh")})
    check("an unusable board config is a loud failure, not a skipped station write",
          r.returncode == 2 and "station_field" in r.stderr and "station_field" not in r.stdout,
          f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")

# ---- FEAT-21 T-10: the root walk-up is depth-agnostic ----------------------------
# migrated_depth: a feature dir one segment deeper than the old arithmetic assumed.
# The fixed three-level climb would resolve <tmp>/.harness and find no harness.json
# (SKIP "not onboarded"); the walk-up must find <tmp> and proceed past that skip.
with tempfile.TemporaryDirectory() as tmpM:
    featM = os.path.join(tmpM, ".harness", "repoA", "features", "FEAT-77-migrated")
    os.makedirs(featM)
    with open(os.path.join(tmpM, ".harness", "team-config.yaml"), "w") as f:
        f.write("agents: {}\n")
    with open(os.path.join(tmpM, ".harness", "harness.json"), "w") as f:
        json.dump({"github": {"sync": False, "repo": None}}, f)
    rM = run(["open", featM], tmpM)
    check("migrated_depth: a segment-deep feature dir resolves the root rather than skipping",
          "project not onboarded" not in (rM.stdout + rM.stderr), rM.stdout + rM.stderr)

# not_onboarded: NO harness.json anywhere above the feature dir — the fallback branch
# must still reach skip() with the message gh-sync.py prints today (taken from source).
with tempfile.TemporaryDirectory() as tmpN:
    featN = os.path.join(tmpN, ".harness", "features", "FEAT-78-bare")
    os.makedirs(featN)
    rN = run(["open", featN], tmpN)
    check("not_onboarded: no harness.json above -> the fallback reaches skip() at exit 0",
          rN.returncode == 0
          and "no .harness/harness.json — project not onboarded" in (rN.stdout + rN.stderr),
          rN.stdout + rN.stderr)

# ---- T-01 (FEAT-23): ship and abandon record feature.json's own terminal status ---------
# The fixture is SCHEMA-VALID AND FULLY POPULATED — all eight feature-schema.json required
# keys plus a github block — so the key-survival case below quantifies over the real key
# set instead of passing vacuously against a two-key fixture.
def _full_fixture(path, feat_name, status, issue_num):
    write_feature_json(
        path,
        feature_id=feat_name,
        branch=f"feat/{feat_name}",
        pr=None,
        status=status,
        review_sha="none",
        cycles_used=1,
        max_total_cycles=10,
        runs=[],
        github={"milestone": 7, "parent": 41, "parent_origin": "created",
                "attached": ["T-01"], "issues": {"T-01": issue_num}},
    )

# --- ship records feature.json status Done
with tempfile.TemporaryDirectory() as tmpS:
    install_gh(tmpS)
    featS = stage(tmpS, feat_name="FEAT-23-ship-status")
    fjS = os.path.join(featS, "feature.json")
    _full_fixture(fjS, "FEAT-23-ship-status", "Review", 900141)
    r = run(["ship", featS], tmpS)
    docS = read_feature_json(fjS)
    check("ship records feature.json status Done",
          r.returncode == 0 and docS.get("status") == "Done",
          f"rc={r.returncode} status={docS.get('status')!r}")

# --- abandon records feature.json status Abandoned
with tempfile.TemporaryDirectory() as tmpT:
    install_gh(tmpT)
    featT = stage(tmpT, feat_name="FEAT-23-abandon-status")
    fjT = os.path.join(featT, "feature.json")
    _full_fixture(fjT, "FEAT-23-abandon-status", "Review", 900142)
    reasonT = os.path.join(tmpT, "reason.txt")
    open(reasonT, "w").write("cutting scope")
    r = run(["abandon", featT, "--reason-file", reasonT], tmpT)
    docT = read_feature_json(fjT)
    check("abandon records feature.json status Abandoned",
          r.returncode == 0 and docT.get("status") == "Abandoned",
          f"rc={r.returncode} status={docT.get('status')!r}")

# --- every other top-level key present before ship/abandon ran is unchanged afterward —
#     over the FULLY POPULATED fixture, so the claim quantifies over the real key set
with tempfile.TemporaryDirectory() as tmpU:
    install_gh(tmpU)
    featU = stage(tmpU, feat_name="FEAT-23-ship-keys")
    fjU = os.path.join(featU, "feature.json")
    _full_fixture(fjU, "FEAT-23-ship-keys", "Review", 900143)
    before_docU = read_feature_json(fjU)
    r = run(["ship", featU], tmpU)
    after_docU = read_feature_json(fjU)
    other_keys_U = [k for k in before_docU if k != "status"]
    check("ship leaves every other top-level key unchanged",
          r.returncode == 0
          and all(after_docU.get(k) == before_docU.get(k) for k in other_keys_U)
          and set(after_docU.keys()) == set(before_docU.keys()),
          f"before={before_docU} after={after_docU}")

with tempfile.TemporaryDirectory() as tmpV:
    install_gh(tmpV)
    featV = stage(tmpV, feat_name="FEAT-23-abandon-keys")
    fjV = os.path.join(featV, "feature.json")
    _full_fixture(fjV, "FEAT-23-abandon-keys", "Review", 900144)
    before_docV = read_feature_json(fjV)
    reasonV = os.path.join(tmpV, "reason.txt")
    open(reasonV, "w").write("cutting scope")
    r = run(["abandon", featV, "--reason-file", reasonV], tmpV)
    after_docV = read_feature_json(fjV)
    other_keys_V = [k for k in before_docV if k != "status"]
    check("abandon leaves every other top-level key unchanged",
          r.returncode == 0
          and all(after_docV.get(k) == before_docV.get(k) for k in other_keys_V)
          and set(after_docV.keys()) == set(before_docV.keys()),
          f"before={before_docV} after={after_docV}")

# ---------- T-02 (FEAT-26): source_issues mirrored from plan.yaml into feature.json,
# threaded through save_recorded's fixed key set so no later save erases it ------------

# --- open records source_issues from the plan.yaml the feature actually carries
with tempfile.TemporaryDirectory() as tmpX1:
    install_gh(tmpX1)
    featX1 = stage(tmpX1, feat_name="FEAT-26-source-issues")
    write_plan_yaml(featX1, "FEAT-26-source-issues",
                     [("T-01", "pending"), ("T-02", "pending"), ("T-03", "pending")],
                     source_issues=[101, 102])
    r = run(["open", featX1], tmpX1)
    docX1 = read_feature_json(os.path.join(featX1, "feature.json"))
    ghX1 = docX1.get("github") or {}
    check("open records source_issues from plan.yaml",
          r.returncode == 0 and ghX1.get("source_issues") == [101, 102],
          f"rc={r.returncode} github={ghX1}")

# --- source_issues must not be erased by any of the LATER save_recorded calls a full
#     `open` run makes after it is set (T-02's whole point). Three tasks -> three issue
#     creates, so this fixture drives 9 total save_recorded calls: 1 after the milestone
#     create, 1 after the parent create, 3 after each issue create, 3 after each attach,
#     and 1 unconditional final save at the end of cmd_open — more than one happens AFTER
#     rec["source_issues"] is set (which is before the milestone save, the first of the 9).
with tempfile.TemporaryDirectory() as tmpX2:
    install_gh(tmpX2)
    featX2 = stage(tmpX2, feat_name="FEAT-26-source-issues-survive")
    write_plan_yaml(featX2, "FEAT-26-source-issues-survive",
                     [("T-01", "pending"), ("T-02", "pending"), ("T-03", "pending")],
                     source_issues=[201, 202, 203])
    r = run(["open", featX2], tmpX2)
    logX2 = calls(tmpX2)
    task_create_linesX2 = [l for l in logX2 if "issue create" in l and re.search(r"\bT-0\d\b", l)]
    docX2 = read_feature_json(os.path.join(featX2, "feature.json"))
    ghX2 = docX2.get("github") or {}
    check("source_issues survives every save during a full open run",
          r.returncode == 0
          and len(task_create_linesX2) == 3   # 3 issue creates -> 3 of the 9 total saves
          and ghX2.get("source_issues") == [201, 202, 203],
          f"rc={r.returncode} task_creates={len(task_create_linesX2)} github={ghX2}")

# --- a feature with no plan.yaml (PLAN.md-only, stage()'s default) records source_issues
#     as an empty list rather than failing or omitting the key
with tempfile.TemporaryDirectory() as tmpX3:
    install_gh(tmpX3)
    featX3 = stage(tmpX3, feat_name="FEAT-26-no-source-issues")
    r = run(["open", featX3], tmpX3)
    docX3 = read_feature_json(os.path.join(featX3, "feature.json"))
    ghX3 = docX3.get("github") or {}
    check("open on a plan with no source_issues records none and still succeeds",
          r.returncode == 0 and ghX3.get("source_issues") == [],
          f"rc={r.returncode} github={ghX3}")

# --- save_recorded refuses, loudly, when feature.json is absent — the orchestrator
#     instantiates it from templates/feature.json on the first cycle; a fresh document
#     written here would be missing feature-schema.json's eight required keys
_dabsentT02 = tempfile.mkdtemp()
_recAbsentT02 = {"milestone": None, "parent": None, "parent_origin": None, "attached": [],
                 "issues": {}, "source_issues": []}
try:
    _ghs.save_recorded(_dabsentT02, _recAbsentT02)
    check("save_recorded refuses when feature.json is absent", False,
          "save_recorded returned instead of raising SystemExit")
except SystemExit as e:
    _msgT02 = str(e)
    check("save_recorded refuses when feature.json is absent",
          "feature.json" in _msgT02
          and os.path.join(_dabsentT02, "feature.json") in _msgT02
          and "absent" in _msgT02,
          _msgT02)

# ---------- T-03 (FEAT-26): record-pr derives and records the PR number from the recorded
# branch, and cmd_ship threads it in ahead of the terminal status write ------------------

FAKE_GH_PR_LIST = """#!/bin/bash
echo "$*" | tr '\n' '\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
case "$*" in
  *"pr list"*)
    echo "$PR_LIST_JSON"
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


def _pr_fixture(path, feat_name, branch, pr, status="Review", github=None):
    """A minimal, schema-shaped feature.json carrying `branch` and `pr` (T-03, FEAT-26) —
    the two fields record-pr reads and writes. `github` is added only when a case needs
    one (the ship case, so cmd_ship's milestone/parent close has something to act on)."""
    fields = dict(
        feature_id=feat_name, branch=branch, pr=pr, status=status,
        review_sha="none", cycles_used=1, max_total_cycles=10, runs=[],
    )
    if github is not None:
        fields["github"] = github
    write_feature_json(path, **fields)


# --- record-pr writes the number when the branch has exactly one merged PR
with tempfile.TemporaryDirectory() as tmpPR1:
    install_gh(tmpPR1, FAKE_GH_PR_LIST)
    featPR1 = stage(tmpPR1, feat_name="FEAT-26-pr-one")
    fjPR1 = os.path.join(featPR1, "feature.json")
    _pr_fixture(fjPR1, "FEAT-26-pr-one", "feat/pr-one", None)
    r = run(["record-pr", featPR1], tmpPR1, {"PR_LIST_JSON": '[{"number": 501}]'})
    docPR1 = read_feature_json(fjPR1)
    logPR1 = calls(tmpPR1)
    check("record-pr writes the number when the branch has exactly one merged PR",
          r.returncode == 0 and docPR1.get("pr") == 501
          and any("pr list" in l and "--head feat/pr-one" in l and "--state merged" in l
                  for l in logPR1),
          f"rc={r.returncode} pr={docPR1.get('pr')} log={logPR1}")

# --- record-pr leaves pr null when the branch has no merged PR
with tempfile.TemporaryDirectory() as tmpPR2:
    install_gh(tmpPR2, FAKE_GH_PR_LIST)
    featPR2 = stage(tmpPR2, feat_name="FEAT-26-pr-zero")
    fjPR2 = os.path.join(featPR2, "feature.json")
    _pr_fixture(fjPR2, "FEAT-26-pr-zero", "feat/pr-zero", None)
    r = run(["record-pr", featPR2], tmpPR2, {"PR_LIST_JSON": "[]"})
    docPR2 = read_feature_json(fjPR2)
    check("record-pr leaves pr null when the branch has no merged PR",
          r.returncode == 0 and docPR2.get("pr") is None,
          f"rc={r.returncode} pr={docPR2.get('pr')}")

# --- record-pr leaves pr null when the branch has two merged PRs — the exactly-one rule,
#     not first-match (feat/harness-native-foundation carries 15 and 4)
with tempfile.TemporaryDirectory() as tmpPR3:
    install_gh(tmpPR3, FAKE_GH_PR_LIST)
    featPR3 = stage(tmpPR3, feat_name="FEAT-26-pr-two")
    fjPR3 = os.path.join(featPR3, "feature.json")
    _pr_fixture(fjPR3, "FEAT-26-pr-two", "feat/harness-native-foundation", None)
    r = run(["record-pr", featPR3], tmpPR3,
            {"PR_LIST_JSON": '[{"number": 15}, {"number": 4}]'})
    docPR3 = read_feature_json(fjPR3)
    check("record-pr leaves pr null when the branch has two merged PRs",
          r.returncode == 0 and docPR3.get("pr") is None,
          f"rc={r.returncode} pr={docPR3.get('pr')}")

# --- record-pr never overwrites a pr that is already an integer — the fake gh returns a
#     DIFFERENT number than the one on disk, so a fixture that would pass by coincidence
#     cannot, and no gh pr list call is even made (the check fires before the query).
with tempfile.TemporaryDirectory() as tmpPR4:
    install_gh(tmpPR4, FAKE_GH_PR_LIST)
    featPR4 = stage(tmpPR4, feat_name="FEAT-26-pr-recorded")
    fjPR4 = os.path.join(featPR4, "feature.json")
    _pr_fixture(fjPR4, "FEAT-26-pr-recorded", "feat/pr-recorded", 314)
    r = run(["record-pr", featPR4], tmpPR4, {"PR_LIST_JSON": '[{"number": 999}]'})
    docPR4 = read_feature_json(fjPR4)
    logPR4 = calls(tmpPR4)
    check("record-pr never overwrites a pr that is already an integer",
          r.returncode == 0 and docPR4.get("pr") == 314
          and not any("pr list" in l for l in logPR4),
          f"rc={r.returncode} pr={docPR4.get('pr')} log={logPR4}")

# --- record-pr --pr writes the number given without querying
with tempfile.TemporaryDirectory() as tmpPR5:
    install_gh(tmpPR5, FAKE_GH_PR_LIST)
    featPR5 = stage(tmpPR5, feat_name="FEAT-26-pr-explicit")
    fjPR5 = os.path.join(featPR5, "feature.json")
    _pr_fixture(fjPR5, "FEAT-26-pr-explicit", "feat/pr-explicit", None)
    r = run(["record-pr", featPR5, "--pr", "88"], tmpPR5,
            {"PR_LIST_JSON": '[{"number": 999}]'})
    docPR5 = read_feature_json(fjPR5)
    logPR5 = calls(tmpPR5)
    check("record-pr --pr writes the number given without querying",
          r.returncode == 0 and docPR5.get("pr") == 88
          and not any("pr list" in l for l in logPR5),
          f"rc={r.returncode} pr={docPR5.get('pr')} log={logPR5}")

# --- ship records the pr and then the status
with tempfile.TemporaryDirectory() as tmpPR6:
    install_gh(tmpPR6, FAKE_GH_PR_LIST)
    featPR6 = stage(tmpPR6, feat_name="FEAT-26-pr-ship")
    fjPR6 = os.path.join(featPR6, "feature.json")
    _pr_fixture(fjPR6, "FEAT-26-pr-ship", "feat/pr-ship", None, status="Review",
                github={"milestone": 7, "parent": 40, "parent_origin": "created",
                        "attached": ["T-01"], "issues": {"T-01": 41}})
    r = run(["ship", featPR6], tmpPR6, {"PR_LIST_JSON": '[{"number": 55}]'})
    docPR6 = read_feature_json(fjPR6)
    check("ship records the pr and then the status",
          r.returncode == 0 and docPR6.get("pr") == 55 and docPR6.get("status") == "Done",
          f"rc={r.returncode} pr={docPR6.get('pr')} status={docPR6.get('status')!r}")

# --- record-pr exits 0 on every branch case (one, zero, and two merged PRs together)
with tempfile.TemporaryDirectory() as tmpPR7:
    install_gh(tmpPR7, FAKE_GH_PR_LIST)
    rcs = []
    for i, pr_list_json in enumerate(('[{"number": 71}]', "[]", '[{"number": 8}, {"number": 9}]')):
        featPR7 = stage(tmpPR7, feat_name=f"FEAT-26-pr-exit0-{i}")
        fjPR7 = os.path.join(featPR7, "feature.json")
        _pr_fixture(fjPR7, f"FEAT-26-pr-exit0-{i}", f"feat/pr-exit0-{i}", None)
        r = run(["record-pr", featPR7], tmpPR7, {"PR_LIST_JSON": pr_list_json})
        rcs.append(r.returncode)
    check("record-pr exits 0 on every branch case", rcs == [0, 0, 0], str(rcs))

# --- MF-1: --pr with a non-numeric value is a caller error at the parse boundary, never
#     an uncaught ValueError traceback (T-03's own contract: never die inside _record_pr,
#     but main()'s flag parse is allowed to reject a caller mistake loudly)
with tempfile.TemporaryDirectory() as tmpPR8:
    install_gh(tmpPR8, FAKE_GH_PR_LIST)
    featPR8 = stage(tmpPR8, feat_name="FEAT-26-pr-non-numeric")
    fjPR8 = os.path.join(featPR8, "feature.json")
    _pr_fixture(fjPR8, "FEAT-26-pr-non-numeric", "feat/pr-non-numeric", None)
    r = run(["record-pr", featPR8, "--pr", "abc"], tmpPR8)
    check("record-pr --pr abc exits non-zero with no traceback",
          r.returncode != 0
          and "Traceback (most recent call last)" not in (r.stdout + r.stderr)
          and "--pr" in (r.stdout + r.stderr),
          f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")

# ---------- T-04 (FEAT-26): closes emits the pull-request-body closing keywords derived
# from the recorded source tickets, and nothing else ----------------------------------


def _closes_fixture(tmp, feat_name, github=None):
    """A bare feature dir carrying only feature.json — closes needs no BRIEF/PLAN/board
    config at all (it makes no GitHub call), so stage()'s full scaffold is not used."""
    feat = os.path.join(tmp, ".harness", "features", feat_name)
    os.makedirs(feat)
    fields = dict(feature_id=feat_name, status="Building")
    if github is not None:
        fields["github"] = github
    write_feature_json(os.path.join(feat, "feature.json"), **fields)
    return feat


# --- closes emits one line per recorded source issue in order — deliberately NOT
#     ascending on disk, so a sort would be caught
with tempfile.TemporaryDirectory() as tmpC1:
    install_gh(tmpC1)
    featC1 = _closes_fixture(tmpC1, "FEAT-26-closes-order",
                              github={"source_issues": [305, 101, 220]})
    r = run(["closes", featC1], tmpC1)
    check("closes emits one line per recorded source issue in order",
          r.returncode == 0 and r.stdout == "Closes #305\nCloses #101\nCloses #220\n",
          f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")

# --- closes emits nothing at exit 0 when source_issues is empty
with tempfile.TemporaryDirectory() as tmpC2:
    install_gh(tmpC2)
    featC2 = _closes_fixture(tmpC2, "FEAT-26-closes-empty",
                              github={"source_issues": []})
    r = run(["closes", featC2], tmpC2)
    check("closes emits nothing at exit 0 when source_issues is empty",
          r.returncode == 0 and r.stdout == "",
          f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")

# --- closes emits nothing at exit 0 when source_issues is absent (no github: block at
#     all — the legitimate first-sync shape load_recorded returns a default for)
with tempfile.TemporaryDirectory() as tmpC3:
    install_gh(tmpC3)
    featC3 = _closes_fixture(tmpC3, "FEAT-26-closes-absent", github=None)
    r = run(["closes", featC3], tmpC3)
    check("closes emits nothing at exit 0 when source_issues is absent",
          r.returncode == 0 and r.stdout == "",
          f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")

# --- closes makes no gh call at all — asserted against the fake gh's own call log, not
#     merely against the exit code, even though a real (working) gh is on PATH for it to
#     call
with tempfile.TemporaryDirectory() as tmpC4:
    install_gh(tmpC4)
    featC4 = _closes_fixture(tmpC4, "FEAT-26-closes-no-gh",
                              github={"source_issues": [9]})
    r = run(["closes", featC4], tmpC4)
    logC4 = calls(tmpC4)
    check("closes makes no gh call at all",
          r.returncode == 0 and r.stdout == "Closes #9\n" and logC4 == [],
          f"rc={r.returncode} stdout={r.stdout!r} log={logC4}")

print(f"\n{'ALL PASSED' if not fails else str(fails) + ' FAILED'}")
sys.exit(1 if fails else 0)
