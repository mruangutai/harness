#!/usr/bin/env python3
"""The fixtures, fake-gh scripts and reporter shared by the test-gh-sync-*.py files.

NOT a test file and deliberately not named like one: `tests/unit/test-suite-layout.py`
requires every test-shaped file under tests/ to sit where the runner's `test-*.py` glob
finds it, so a shared module has to carry a name that glob never selects. Every fixture
below came out of the single test-gh-sync.py this family was split from (issue #1527);
none of them changed in the move.

Each importing file installs its own fake gh into its own temporary directory through
`install_gh`, so the files carry no ordering dependency on one another and the runner
pool may run them concurrently in any order (`tests/unit/test-suite-independence.py`).
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import importlib.util
import json
import os
import re
import subprocess
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
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


def add_plan_station(feat_dir, feat_name, station="building"):
    """Give an existing `stage()` fixture the plan.yaml the station now lives in (FEAT-41 T-07).

    SEPARATE FROM `stage`, DELIBERATELY. Folding this into `stage` was tried and reverted: a
    plan.yaml WINS over PLAN.md in cmd_open's discovery, so every open-lifecycle case silently
    switched to a one-task plan and asserted against three issues that were never created.
    Only the cases that exercise a STATION WRITE need a plan, and they ask for one."""
    with open(os.path.join(feat_dir, "plan.yaml"), "w", encoding="utf-8") as f:
        f.write(f"schema: plan/1\nfeature: {feat_name}\nstatus: {station}\n"
                f"tasks:\n  - id: T-01\n    title: t\n    change_type: logic\n"
                f"    execution_mode: team\n    files:\n      - a.py\n"
                f"    verify: |\n      true\n    intent: |\n      x\n    status: done\n")
    return feat_dir


def write_feature_json(path, **fields):
    """Write a minimal feature.json fixture. `feature_id` and `status` default; any keyword
    (including `github`) overrides or adds a top-level key.

    `status=None` OMITS the key entirely rather than writing a JSON null (FEAT-41 T-07). The
    distinction is the whole point of the post-migration shape: a null status is a malformed
    document that a reader may legitimately reject, while an ABSENT status is what the
    migration actually leaves on disk and what every repointed reader must handle.
    """
    doc = {"feature_id": fields.pop("feature_id", "FEAT-05-export-fix"),
           "status": fields.pop("status", "Building")}
    if doc["status"] is None:
        del doc["status"]
    doc.update(fields)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)


def nested_feature_dir(feat_name="FEAT-77-test"):
    """A fresh tempdir's feature directory nested under a realistic
    .harness/features/<feat_name>/ shape (matching `stage()`'s own convention and
    feature_json_write.FEATURE_JSON_TAIL) — required for any fixture that reaches
    save_recorded/_record_status/_record_pr now that they route through the locked,
    destination-checked feature_json_write.write_feature_json (stale-anchor-write-hazard
    cycle 2). A bare tempdir passed a feature.json worked only because those write sites
    carried no destination check at all before this feature."""
    base = tempfile.mkdtemp()
    d = os.path.join(base, ".harness", "features", feat_name)
    os.makedirs(d)
    return d


def read_plan_station(feat_dir):
    """plan.yaml's top-level station (FEAT-41 T-07) — what `read_feature_json(...)["status"]`
    used to answer before the field moved. Returns None when the plan or the key is absent, so
    a case can assert "no station recorded" as well as a value."""
    try:
        with open(os.path.join(feat_dir, "plan.yaml"), encoding="utf-8") as f:
            for line in f:
                if line.startswith("status:"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        return None
    return None


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
  *"projectItems(first: 20)"*)
    # THE BY-ISSUE GUARD READ (issue #1541), gh_board.board_stations_for. Same three
    # variables and same meanings as the whole-board branch below — only the response shape
    # differs. An alias the query did not ask about is never emitted, so a lookup for any
    # number other than GUARD_ISSUE reads as "not on the board", exactly as the whole-board
    # fake's single node made it.
    if [ -z "$GUARD_STATION_NAME" ]; then
      fv=null
    else
      fv='{"name":"'"$GUARD_STATION_NAME"'"}'
    fi
    num="${GUARD_ISSUE:-326}"
    printf '{"data":{"repository":{"i%s":{"number":%s,"projectItems":{"pageInfo":{"hasNextPage":false},"nodes":[{"project":{"number":3},"fieldValueByName":%s}]}}}}}\\n' "$num" "$num" "$fv"
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
  *"projectItems(first: 20)"*)
    echo "simulated network failure" >&2
    exit 1 ;;
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
  *"projectItems(first: 20)"*)
    if [ -z "$GUARD_STATION_NAME" ]; then
      fv=null
    else
      fv='{"name":"'"$GUARD_STATION_NAME"'"}'
    fi
    num="${GUARD_ISSUE:-326}"
    printf '{"data":{"repository":{"i%s":{"number":%s,"projectItems":{"pageInfo":{"hasNextPage":false},"nodes":[{"project":{"number":3},"fieldValueByName":%s}]}}}}}\\n' "$num" "$num" "$fv"
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


# THE ORDERED LOWERCASE DECLARATION (FEAT-41 T-01). This was a six-key MAPPING of station name
# to column name, which T-01 made a loud FleetError: the six names are FIXED, and a board's
# COLUMN names are DERIVED from them by factory_config.station_column. There is no column name to
# store here any more, so the declaration is a checksum rather than a place to choose.
FULL_STATIONS = ["backlog", "plan", "ready", "building", "review", "done"]


# T-04: the ship fixture's gh. Everything FAKE_GH_STATIONS answers, plus the three reads the
# new cmd_ship makes that no earlier subcommand did: the sub_issues GET (the open-child test),
# the closed-issue list and the project workflows list (the audit ship now schedules).
#
# Parameterised by env so one stub covers every case:
#   SHIP_STATIONS       "40=Review 41=Done 42="   the board's station map; empty value = null
#   SHIP_CHILDREN_<n>   "41 42"                   issue <n>'s children, absent = childless
#   SHIP_SUBISSUES_FAIL "40"                      that one sub_issues read exits non-zero
#   SHIP_EDIT_FAIL      "ITEM_41"                 that one card's station write fails
#   SHIP_CLOSED_JSON    a gh issue list payload   what the audit's closed-issue read returns
FAKE_GH_SHIP = """#!/bin/bash
echo "$*" | tr '\n' '\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
case "$*" in
  *"sub_issues -F sub_issue_id="*)
    echo '{}'
    exit 0 ;;
  *"/sub_issues"*)
    num=$(echo "$*" | grep -oE 'issues/[0-9]+/sub_issues' | grep -oE '[0-9]+' | head -1)
    for bad in $SHIP_SUBISSUES_FAIL; do
      if [ "$bad" = "$num" ]; then echo "sub_issues read refused" >&2; exit 1; fi
    done
    eval "kids=\\$SHIP_CHILDREN_$num"
    out="["; sep=""
    for k in $kids; do out="$out$sep{\\"number\\":$k}"; sep=","; done
    echo "$out]"
    exit 0 ;;
  *"--jq .id"*)
    num=$(echo "$*" | grep -oE 'issues/[0-9]+' | head -1 | grep -oE '[0-9]+')
    echo "9000$num"
    exit 0 ;;
  *"ProjectV2SingleSelectField"*)
    printf '{"data":{"repositoryOwner":{"__typename":"User","projectV2":{"id":"PVT_PROJ","field":{"id":"FIELD_STATUS","name":"Status","options":[{"id":"OPT_BACKLOG","name":"Backlog"},{"id":"OPT_PLAN","name":"Plan"},{"id":"OPT_READY","name":"Ready"},{"id":"OPT_BUILDING","name":"Building"},{"id":"OPT_REVIEW","name":"Review"},{"id":"OPT_DONE","name":"Done"}]}}}}}\\n'
    exit 0 ;;
  *"workflows(first: 50)"*)
    printf '{"data":{"user":{"projectV2":{"workflows":{"nodes":[{"name":"Item closed","enabled":true,"number":1},{"name":"Auto-close issue","enabled":true,"number":2},{"name":"Pull request merged","enabled":true,"number":3}]}}}}}\\n'
    exit 0 ;;
  *"projectItems(first: 20)"*)
    # THE BY-ISSUE BOARD READ (issue #1541). It answers ONLY for the aliases the query asked
    # about: a number absent from SHIP_STATIONS comes back as a null alias, which is the same
    # answer the whole-board branch below gives by omitting its node — "not on the board".
    # SHIP_BOARD_STATE still wins, so the board still REMEMBERS a write made earlier in the run.
    asked=$(echo "$*" | grep -oE 'issue\\(number: [0-9]+\\)' | grep -oE '[0-9]+')
    out=""; sep=""
    for n in $asked; do
      st=""; found=0
      for pair in $SHIP_STATIONS; do
        pn="${pair%%=*}"
        if [ "$pn" = "$n" ]; then found=1; st="${pair#*=}"; fi
      done
      if [ -n "$SHIP_BOARD_STATE" ] && [ -f "$SHIP_BOARD_STATE" ]; then
        later=$(grep -E "^$n=" "$SHIP_BOARD_STATE" | tail -1)
        if [ -n "$later" ]; then found=1; st="${later#*=}"; fi
      fi
      if [ "$found" = "1" ]; then
        if [ -z "$st" ]; then fv=null; else fv='{"name":"'"$st"'"}'; fi
        out="$out$sep\\"i$n\\":{\\"number\\":$n,\\"projectItems\\":{\\"pageInfo\\":{\\"hasNextPage\\":false},\\"nodes\\":[{\\"project\\":{\\"number\\":3},\\"fieldValueByName\\":$fv}]}}"
      else
        out="$out$sep\\"i$n\\":null"
      fi
      sep=","
    done
    printf '{"data":{"repository":{%s}}}\\n' "$out"
    exit 0 ;;
  *"items(first: 100, after:"*)
    nodes=""; sep=""
    for pair in $SHIP_STATIONS; do
      n="${pair%%=*}"; st="${pair#*=}"
      if [ -n "$SHIP_BOARD_STATE" ] && [ -f "$SHIP_BOARD_STATE" ]; then
        later=$(grep -E "^$n=" "$SHIP_BOARD_STATE" | tail -1)
        if [ -n "$later" ]; then st="${later#*=}"; fi
      fi
      if [ -z "$st" ]; then fv=null; else fv='{"name":"'"$st"'"}'; fi
      nodes="$nodes$sep{\\"content\\":{\\"number\\":$n,\\"repository\\":{\\"nameWithOwner\\":\\"implentio/fake\\"}},\\"fieldValueByName\\":$fv}"
      sep=","
    done
    printf '{"data":{"user":{"projectV2":{"items":{"totalCount":1,"pageInfo":{"hasNextPage":false,"endCursor":null},"nodes":[%s]}}}}}\\n' "$nodes"
    exit 0 ;;
  *"projectItems(first: 100)"*)
    num=$(echo "$*" | grep -oE 'number=[0-9]+' | tail -1 | grep -oE '[0-9]+')
    printf '{"data":{"repository":{"issue":{"projectItems":{"totalCount":1,"nodes":[{"id":"ITEM_%s","project":{"number":3}}]}}}}}\\n' "$num"
    exit 0 ;;
  *"project item-edit"*)
    for bad in $SHIP_EDIT_FAIL; do
      case "$*" in *"--id $bad "*|*"--id $bad") echo "item-edit refused for $bad" >&2; exit 1 ;; esac
    done
    # THE BOARD REMEMBERS. A successful write is recorded so a LATER station read in the same
    # run reports the new value. Without this the stub is a board that never changes, and the
    # audit-ordering case cannot fail against an implementation that audits before it writes.
    if [ -n "$SHIP_BOARD_STATE" ]; then
      wnum=$(echo "$*" | grep -oE -- '--id ITEM_[0-9]+' | grep -oE '[0-9]+')
      wopt=$(echo "$*" | grep -oE -- '--single-select-option-id OPT_[A-Z]+' | sed 's/.*OPT_//')
      case "$wopt" in
        BACKLOG) wst=Backlog ;; PLAN) wst=Plan ;; READY) wst=Ready ;;
        BUILDING) wst=Building ;; REVIEW) wst=Review ;; DONE) wst=Done ;; *) wst="" ;;
      esac
      if [ -n "$wnum" ] && [ -n "$wst" ]; then echo "$wnum=$wst" >> "$SHIP_BOARD_STATE"; fi
    fi
    exit 0 ;;
esac
case "$1 $2" in
  "auth status") exit 0 ;;
  "issue list") echo "${SHIP_CLOSED_JSON:-[]}" ;;
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
                    "stations": list(stations or FULL_STATIONS)} if board else None)
    json.dump({"github": g}, open(os.path.join(tmp, ".harness", "harness.json"), "w"))


def write_plan_yaml(feat_dir, feat_name, task_statuses, source_issues=None, approval=None,
                     plan_station=None):
    """A minimal plan.yaml — every REQUIRED_TASK_FIELDS key present — carrying only the
    `status` values a test cares about. Written as JSON text: JSON is valid YAML and this
    avoids a second parser dependency in the test file itself.

    `source_issues` is OPTIONAL (T-02, FEAT-26) so every existing caller is unchanged when
    it is omitted; when given, it is written as plan.yaml's own top-level `source_issues`
    key, exactly the shape `parse_source_issues` reads.

    `approval` is OPTIONAL (T-13): a dict written verbatim as plan.yaml's top-level
    `approval:` key when given, omitted otherwise — every existing caller (none of which
    cares about approval) is unchanged.

    `plan_station` writes plan.yaml's own top-level `status:` — the feature's station, which
    FEAT-41 T-07 makes the single record of it. Omitted by default so every existing caller is
    unchanged.
    """
    # BLOCK YAML, NOT JSON (FEAT-41 T-16). This wrote `json.dump(doc, f)` on the reasoning that
    # JSON is valid YAML and it avoided a second parser dependency in this file. Both halves were
    # true and the fixture was still wrong, in a way nothing could see until a tool WROTE the
    # file rather than only reading it: plan-merge.py's verbs SPLICE TEXT under a lock, so they
    # address a task by its own `- id: T-NN` LINE. A single-line JSON document has no such line,
    # so `set-task-station` could not find any task at all and start-task refused.
    #
    # Emitted as text rather than through a dumper for the original reason — no parser dependency
    # — and it is now the same SHAPE the template produces, so a fixture exercises the write path
    # production uses instead of merely one a reader accepts.
    lines = ["schema: plan/1", f"feature: {feat_name}"]
    if plan_station is not None:
        lines.append(f"status: {plan_station}")
    if source_issues is not None:
        lines.append("source_issues: [" + ", ".join(str(n) for n in source_issues) + "]")
    if approval is not None:
        lines.append("approval:")
        for key, value in approval.items():
            lines.append(f"  {key}: {value}")
    lines.append("tasks:")
    for tid, status in task_statuses:
        lines += [
            f"  - id: {tid}",
            f"    title: {tid}",
            "    change_type: logic",
            "    execution_mode: team",
            "    files:",
            "      - dummy.py",
            "    verify: |",
            "      true",
            "    intent: |",
            "      fixture",
            f"    status: {status}",
        ]
    with open(os.path.join(feat_dir, "plan.yaml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def stage_station(tmp, feat_name, task_statuses, board=True, sync=True, repo="implentio/fake",
                   feature_status=None, plan_station="building", issues=None, parent=40,
                   milestone=7, stations=None, approval=None, source_issues=None):
    """A plan.yaml-backed feature, wired for the T-03 station-write tests: harness.json's
    github.board (optionally), a plan.yaml carrying the given task statuses, and a
    feature.json recording the given issues/parent so `load_recorded` needs no live sync.

    `approval` and `source_issues` are OPTIONAL passthroughs to `write_plan_yaml` (T-13) —
    every existing caller, which passes neither, is unchanged.

    `feature_status=None` OMITS feature.json's status key — the post-migration shape (FEAT-41
    T-07) — and `plan_station` records the station in plan.yaml instead, where T-07 makes it
    the only record. Passing both is the pre-migration shape and is what every existing
    caller still gets by default.
    """
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
- SC-01: covered by the test-gh-sync-*.py suite. verify: automated

## Approval

status: approved
""")
    write_plan_yaml(feat, feat_name, task_statuses, source_issues=source_issues,
                     approval=approval, plan_station=plan_station)
    write_feature_json(
        os.path.join(feat, "feature.json"),
        feature_id=feat_name, status=feature_status,
        github={"milestone": milestone, "parent": parent, "parent_origin": "created",
                "build_entry": "opened", "attached": list((issues or {}).keys()),
                "issues": issues or {}},
    )
    return feat


def write_dangling_plan_yaml(feat_dir, feat_name, t2_depends_on, approval=None,
                              plan_station=None):
    """A plan.yaml with exactly two complete tasks, T-01 and T-02, where T-02's `depends_on`
    names `t2_depends_on` — BUG-201 T-05's shared fixture (D-05, REQ-05). Pass "T-99" for the
    DANGLING plan (T-99 is not one of this plan's own tasks — the referential-integrity
    violation T-03 rejects at load) and "T-01" for the paired LEGAL plan. Every
    REQUIRED_TASK_FIELDS key is present for both tasks, in this file's own block-YAML house
    style (T-05 intent), never json.dump — the same reason `write_plan_yaml` moved off it
    (FEAT-41 T-16): plan-merge's verbs address a task by its own `- id: T-NN` line.
    """
    lines = ["schema: plan/1", f"feature: {feat_name}"]
    if plan_station is not None:
        lines.append(f"status: {plan_station}")
    if approval is not None:
        lines.append("approval:")
        for key, value in approval.items():
            lines.append(f"  {key}: {value}")
    lines.append("tasks:")
    for tid in ("T-01", "T-02"):
        lines += [
            f"  - id: {tid}",
            f"    title: {tid}",
            "    change_type: logic",
            "    execution_mode: team",
            "    files:",
            "      - dummy.py",
            "    verify: |",
            "      true",
            "    intent: |",
            "      fixture",
            "    status: ready",
        ]
        if tid == "T-02":
            lines.append(f"    depends_on: [{t2_depends_on}]")
    with open(os.path.join(feat_dir, "plan.yaml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def stage_depends_on(tmp, feat_name, t2_depends_on, repo="implentio/fake", board=True,
                      sync=True, issues=None, parent=40, milestone=7,
                      approval=None, plan_station="plan"):
    """The BUG-201 T-05 shared fixture (D-05, REQ-05), staged the way `stage_station` already
    stages a plan.yaml-backed feature — harness.json's github.board, feature.json recording
    `issues`, and a plan.yaml built by `write_dangling_plan_yaml` instead of `write_plan_yaml`.
    `approval` defaults to status `pending` and `plan_station` to `plan` — T-05's intent's own
    words for "otherwise legal": feature, status plan, approval status pending, two complete
    tasks.
    """
    feat = os.path.join(tmp, ".harness", "features", feat_name)
    os.makedirs(feat)
    write_harness_json_board(tmp, sync=sync, repo=repo, board=board)
    write_dangling_plan_yaml(
        feat, feat_name, t2_depends_on,
        approval=approval if approval is not None else {"status": "pending"},
        plan_station=plan_station,
    )
    write_feature_json(
        os.path.join(feat, "feature.json"),
        feature_id=feat_name, status=None,
        github={"milestone": milestone, "parent": parent, "parent_origin": "created",
                "attached": list((issues or {}).keys()), "issues": issues or {},
                "build_entry": "opened"},
    )
    return feat


def install_gh(tmp, script=FAKE_GH):
    gh_path = os.path.join(tmp, "gh")
    open(gh_path, "w").write(script)
    os.chmod(gh_path, 0o755)


# T-04's ship fixtures, defined HERE with the other helpers rather than beside the ship cases,
# because T-11 retargeted an earlier block onto them: a helper used by two sections belongs
# above both.
def stage_ship(tmp, feat_name, issues, parent=40, source_issues=None, milestone=7):
    """A ship fixture: a board-backed feature plus the SPEC.md probe and the
    team-config.yaml MARKER `harness_boundary.resolve_root()` needs, so the audit ship now
    schedules resolves THIS fixture's harness.json rather than climbing out to the real
    checkout."""
    feat = stage_station(tmp, feat_name, [(t, "done") for t in issues],
                          issues=issues, parent=parent, milestone=milestone,
                          source_issues=source_issues, feature_status="Review")
    if source_issues:
        # feature.json's github.source_issues is the MIRROR `load_recorded` reads; plan.yaml's
        # own top-level field is what `open` copies from. `stage_station` writes only the
        # plan, so the mirror is written here.
        fj = os.path.join(feat, "feature.json")
        doc = json.load(open(fj))
        doc["github"]["source_issues"] = list(source_issues)
        json.dump(doc, open(fj, "w"), indent=2)
    docs = os.path.join(tmp, ".harness", "harness", "docs")
    os.makedirs(docs, exist_ok=True)
    open(os.path.join(docs, "SPEC.md"), "w").write("# fixture probe\n")
    marker = os.path.join(tmp, ".harness", "team-config.yaml")
    if not os.path.isfile(marker):
        open(marker, "w").write("teams: []\n")
    return feat


def ship_env(tmp, stations, children=None, **extra):
    env = {"FACTORY_GH": os.path.join(tmp, "gh"),
           "HARNESS_PROJECT_DIR": tmp,
           "SHIP_STATIONS": stations,
           "SHIP_BOARD_STATE": os.path.join(tmp, "board-state")}
    for num, kids in (children or {}).items():
        env["SHIP_CHILDREN_%s" % num] = " ".join(str(k) for k in kids)
    env.update(extra)
    return env


def edits_to(log, station_opt):
    return [l for l in log if "project item-edit" in l and station_opt in l]


def moved_to_done(log):
    """The ITEM ids written to the Done option. Callers assert PER NUMBER, never as a count,
    so a run that moved the wrong three cards cannot pass."""
    out = set()
    for l in edits_to(log, "OPT_DONE"):
        m = re.search(r"--id ITEM_(\d+)", l)
        if m:
            out.add(int(m.group(1)))
    return out


# The reporter, verbatim in its output grammar -- `ok    <name>` and `FAIL  <name>` plus
# the indented detail line -- with the module-level counter replaced by a list each
# importing file reads for its own exit status.
FAILURES = []


def check(name, cond, detail=""):
    if cond:
        print(f"ok    {name}")
    else:
        FAILURES.append(name)
        print(f"FAIL  {name}\n      {detail}")


def report():
    """The summary line, then the exit status: 1 if anything failed, 0 otherwise."""
    print(f"\n{'ALL PASSED' if not FAILURES else str(len(FAILURES)) + ' FAILED'}")
    return 1 if FAILURES else 0


def load_gh_sync():
    """gh-sync.py's hyphen blocks a plain import, so the module is loaded from its path.
    Used by the cases that assert a function's own contract rather than a subcommand's."""
    spec = importlib.util.spec_from_file_location("_ghs", os.path.join(BIN_DIR, "gh-sync.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
