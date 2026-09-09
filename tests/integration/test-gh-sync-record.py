#!/usr/bin/env python3
"""What the subcommands RECORD rather than what they draw on the board: `status`'s
station transitions, `record-pr`'s PR number, and the milestone/comment bookkeeping
`ship` still does when no board is configured.

Split out of test-gh-sync.py (issue #1527); the cases, their assertions and their
subprocess invocations are unchanged. Shared fixtures live in gh_sync_support.py.

    ./test-gh-sync-record.py    -> exit 0 all pass, 1 otherwise
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import os
import re
import sys
import tempfile

from gh_sync_support import (
    FAKE_GH_STATIONS, add_plan_station, calls, check, install_gh, read_feature_json,
    read_plan_station, report, run, stage, stage_station, write_feature_json)


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
    one (the ship case, so cmd_ship's milestone/parent close has something to act on).

    `status` is written to the sibling plan.yaml as the feature's station (FEAT-41 T-07), not
    into feature.json — ship reads it from there and writes it back through the verb."""
    add_plan_station(os.path.dirname(path), feat_name, str(status).lower())
    fields = dict(
        feature_id=feat_name, branch=branch, pr=pr,
        review_sha="none", cycles_used=1, max_total_cycles=10, runs=[],
    )
    if github is not None:
        fields["github"] = github
    write_feature_json(path, **fields)


def main():
    # --- ship: a created parent closes completed, milestone patched closed AFTER the parent close
    with tempfile.TemporaryDirectory() as tmpG:
        install_gh(tmpG)
        featG = stage(tmpG, feat_name="FEAT-07-ship-created")
        add_plan_station(featG, "FEAT-07-ship-created", "review")
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
        # T-04 REVERSES BOTH ASSERTIONS THAT STOOD HERE. They read "ship closes a created parent
        # completed" and "ship's parent close carries an explicit --reason completed (T-08)".
        # `ship` now closes NOTHING (DEC-203 item 2): it writes the done station and GitHub's own
        # Auto-close issue workflow does the closing. `parent_origin` is gone with them -- this
        # fixture still records it only because T-05 is what deletes the field.
        #
        # THIS FIXTURE HAS NO BOARD (`stage`, not `stage_station`), so it is also the no-board
        # path: no card can be moved, and the issue lifecycle must still run to completion.
        docG = read_feature_json(os.path.join(featG, "feature.json"))
        check("ship closes NO issue, whatever the recorded parent_origin (DEC-203)",
              r.returncode == 0 and not close40G and not patch40G, str(logG))
        check("ship with no board configured says so, in one line",
              "no board configured" in r.stdout, repr(r.stdout))
        check("ship with no board configured STILL closes the milestone -- the issue lifecycle "
              "runs to completion",
              bool(ms_idxG), str(logG))
        check("ship with no board configured STILL records the terminal station",
              read_plan_station(featG) == "done", read_plan_station(featG))

    # --- ship on a feature carrying NO Build-entry receipt: the no-board skip must NAME the
    #     remedy (T-03, BUG-1309). This is the one recover-terminal case that runs no
    #     recover-terminal: it manipulates nothing and asserts ship's own no-board wording,
    #     so it belongs with ship's no-board bookkeeping rather than beside cmd_open's cases.
    with tempfile.TemporaryDirectory() as tmpR7:
        install_gh(tmpR7)
        featR7 = stage(tmpR7, feat_name="FEAT-70-t03-ship-points")
        rR7 = run(["ship", featR7], tmpR7)
        check("T-03 ship names recover-terminal",
              rR7.returncode == 0 and "gh-sync: SKIP" in rR7.stdout
              and "recover-terminal" in rR7.stdout,
              f"rc={rR7.returncode} out={rR7.stdout!r}")

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

    # ---------- T-13: gh-sync.py status <feature-dir> <Status> ----------
    # Couples recording feature.json's phase status to the station writes that event implies.
    # Every case sets BOTH FACTORY_GH and GH_SYNC_GH (D-11) — gh_board's calls go through
    # factory_gh, which reads FACTORY_GH, not GH_SYNC_GH.

    # --- an unknown Status value is refused, exit 2, before anything is recorded or written.
    with tempfile.TemporaryDirectory() as tmpSt1:
        install_gh(tmpSt1, FAKE_GH_STATIONS)
        featSt1 = stage_station(
            tmpSt1, "FEAT-33-status-unknown",
            [("T-01", "done")],
            issues={"T-01": 326},
            feature_status=None, plan_station="building",
        )
        r = run(["status", featSt1, "Banana"], tmpSt1, {"FACTORY_GH": os.path.join(tmpSt1, "gh")})
        check("status: an unknown value is refused with exit 2",
              r.returncode == 2, r.stdout + r.stderr)
        check("status: the refusal names the offending value",
              "Banana" in (r.stdout + r.stderr), r.stdout + r.stderr)
        check("status: an unknown value writes no station of any kind",
              not any("item-edit" in l for l in calls(tmpSt1)), str(calls(tmpSt1)))
        check("status: an unknown value leaves plan.yaml's station unrecorded",
              read_plan_station(featSt1) == "building",
              read_feature_json(os.path.join(featSt1, "feature.json")))

    # --- status Ready on a signed plan moves every recorded T-NN sub-issue to the declared
    #     ready station and touches the parent NOWHERE (D-18) — assert the EXACT SET, never a
    #     count: a count of three is satisfied by two sub-issues plus the parent.
    with tempfile.TemporaryDirectory() as tmpSt2:
        install_gh(tmpSt2, FAKE_GH_STATIONS)
        featSt2 = stage_station(
            tmpSt2, "FEAT-33-status-ready",
            [("T-01", "done"), ("T-02", "building"), ("T-03", "ready")],
            issues={"T-01": 41, "T-02": 42, "T-03": 43},
            parent=40,
            approval={"status": "approved"},
        )
        r = run(["status", featSt2, "ready"], tmpSt2, {"FACTORY_GH": os.path.join(tmpSt2, "gh")})
        logSt2 = calls(tmpSt2)
        editsSt2 = [l for l in logSt2 if "project item-edit" in l]
        ids_written = {next(p for p in l.split() if p.startswith("ITEM_")) for l in editsSt2}
        check("status Ready: exits 0", r.returncode == 0, r.stdout + r.stderr)
        check("status Ready: writes exactly the three sub-issues, never the parent",
              ids_written == {"ITEM_41", "ITEM_42", "ITEM_43"}, str(editsSt2))
        # EACH CARD CARRIES ITS OWN TASK'S WORD (FEAT-41 T-06, D-11). This asserted that every write
        # selected OPT_READY, because the transition used to write one station to every sub-issue.
        # The plan here is deliberately MIXED — done, building, ready — and under D-11 a card whose
        # task says building must READ building; writing `ready` over it is precisely the
        # two-words-two-meanings disagreement this feature deletes.
        #
        # WHY THIS DIFFERS FROM THE Review TRANSITION, which DOES still write one station to every
        # card: Review has an operator ruling behind it (D-23) and an INV-26 widening that exists to
        # tolerate the resulting disagreement. Ready has neither, so there is nothing to justify
        # overwriting a task's own word here.
        _want_by_item = {"ITEM_41": "OPT_DONE", "ITEM_42": "OPT_BUILDING", "ITEM_43": "OPT_READY"}
        _got_by_item = {next(p for p in l.split() if p.startswith("ITEM_")):
                        l.split("--single-select-option-id ")[1].split()[0].strip("\x01")
                        for l in editsSt2}
        check("status Ready: each sub-issue card gets ITS OWN task's station, not one blanket value",
              _got_by_item == _want_by_item, f"got {_got_by_item}, want {_want_by_item}")
        check("status Ready: feature.json status recorded as Ready",
              read_plan_station(featSt2) == "ready",
              read_feature_json(os.path.join(featSt2, "feature.json")))

    # --- status Review moves the PARENT and every recorded T-NN sub-issue, and only those.
    with tempfile.TemporaryDirectory() as tmpSt3:
        install_gh(tmpSt3, FAKE_GH_STATIONS)
        featSt3 = stage_station(
            tmpSt3, "FEAT-33-status-review",
            [("T-01", "done"), ("T-02", "done")],
            issues={"T-01": 41, "T-02": 42},
            parent=40,
        )
        r = run(["status", featSt3, "review"], tmpSt3, {"FACTORY_GH": os.path.join(tmpSt3, "gh")})
        logSt3 = calls(tmpSt3)
        editsSt3 = [l for l in logSt3 if "project item-edit" in l]
        ids_written3 = {next(p for p in l.split() if p.startswith("ITEM_")) for l in editsSt3}
        check("status Review: exits 0", r.returncode == 0, r.stdout + r.stderr)
        check("status Review: writes exactly the parent plus every sub-issue",
              ids_written3 == {"ITEM_40", "ITEM_41", "ITEM_42"}, str(editsSt3))
        check("status Review: every write selects the declared Review option",
              all("--single-select-option-id OPT_REVIEW" in l for l in editsSt3), str(editsSt3))

    # --- status Review treats abandoned as finished, while still refusing unfinished work.
    with tempfile.TemporaryDirectory() as tmpSt3b:
        install_gh(tmpSt3b, FAKE_GH_STATIONS)
        featSt3b = stage_station(
            tmpSt3b, "FEAT-48-status-review-abandoned",
            [("T-01", "done"), ("T-07", "abandoned")],
            issues={"T-01": 41},
            parent=40,
        )
        r = run(["status", featSt3b, "review"], tmpSt3b,
                {"FACTORY_GH": os.path.join(tmpSt3b, "gh")})
        check("status Review accepts done plus abandoned tasks as finished",
              r.returncode == 0 and read_plan_station(featSt3b) == "review",
              r.stdout + r.stderr)

    # --- status Plan, Done and Abandoned each write NO station at all — the harness never
    #     writes those three columns (Plan is board-station.py's, Done is `ship`'s alone -- ship
    #     is the only writer of the done station -- and Abandoned has no column at all,
    #     D-03/DEC-203).
    for _st3_status in ("plan", "done", "abandoned"):
        with tempfile.TemporaryDirectory() as tmpSt4:
            install_gh(tmpSt4, FAKE_GH_STATIONS)
            featSt4 = stage_station(
                tmpSt4, f"FEAT-33-status-{_st3_status}",
                [("T-01", "done")],
                issues={"T-01": 41},
                parent=40,
            )
            r = run(["status", featSt4, _st3_status], tmpSt4,
                    {"FACTORY_GH": os.path.join(tmpSt4, "gh")})
            logSt4 = calls(tmpSt4)
            check(f"status {_st3_status}: exits 0", r.returncode == 0, r.stdout + r.stderr)
            check(f"status {_st3_status}: writes NO station at all",
                  not any("item-edit" in l for l in logSt4), str(logSt4))
            check(f"status {_st3_status}: plan.yaml station recorded",
                  read_plan_station(featSt4) == _st3_status,
                  read_plan_station(featSt4))

    # --- SC-14's fixture: status Ready on a feature with ZERO recorded sub-issues writes
    #     nothing and prints one line — proves there is no fallback to the parent.
    with tempfile.TemporaryDirectory() as tmpSt5:
        install_gh(tmpSt5, FAKE_GH_STATIONS)
        featSt5 = stage_station(
            tmpSt5, "FEAT-33-status-ready-zero-subissues",
            [("T-01", "pending")],
            issues={},
            parent=40,
            approval={"status": "approved"},
        )
        r = run(["status", featSt5, "ready"], tmpSt5, {"FACTORY_GH": os.path.join(tmpSt5, "gh")})
        logSt5 = calls(tmpSt5)
        check("status Ready, zero sub-issues: exits 0", r.returncode == 0, r.stdout + r.stderr)
        check("status Ready, zero sub-issues: no set_station call at all — no parent fallback",
              not any("item-edit" in l for l in logSt5), str(logSt5))
        check("status Ready, zero sub-issues: prints one line saying there is nothing to move",
              "no sub-issues recorded" in r.stdout, r.stdout)

    # --- refusal: status Ready with an UNSIGNED plan (no approval.status: approved) is
    #     refused, exit 2, and nothing is recorded or written.
    with tempfile.TemporaryDirectory() as tmpSt6:
        install_gh(tmpSt6, FAKE_GH_STATIONS)
        featSt6 = stage_station(
            tmpSt6, "FEAT-33-status-ready-unsigned",
            [("T-01", "pending")],
            issues={"T-01": 41},
            parent=40,
            feature_status=None, plan_station="plan",
            approval=None,
        )
        r = run(["status", featSt6, "ready"], tmpSt6, {"FACTORY_GH": os.path.join(tmpSt6, "gh")})
        check("status Ready, unsigned plan: refused with exit 2",
              r.returncode == 2, r.stdout + r.stderr)
        check("status Ready, unsigned plan: names the value ready in the refusal",
              "ready" in (r.stdout + r.stderr), r.stdout + r.stderr)
        check("status Ready, unsigned plan: no station write reaches the fake",
              not any("item-edit" in l for l in calls(tmpSt6)), str(calls(tmpSt6)))
        check("status ready, unsigned plan: plan.yaml station is NOT recorded as ready",
              read_plan_station(featSt6) == "plan",
              read_feature_json(os.path.join(featSt6, "feature.json")))

    # --- refusal: status Review while a task is not yet done is refused, exit 2, and nothing
    #     is recorded or written.
    with tempfile.TemporaryDirectory() as tmpSt7:
        install_gh(tmpSt7, FAKE_GH_STATIONS)
        featSt7 = stage_station(
            tmpSt7, "FEAT-33-status-review-unfinished",
            [("T-01", "done"), ("T-02", "building")],
            issues={"T-01": 41, "T-02": 42},
            parent=40,
            feature_status=None, plan_station="building",
        )
        r = run(["status", featSt7, "review"], tmpSt7, {"FACTORY_GH": os.path.join(tmpSt7, "gh")})
        check("status Review, unfinished tasks: refused with exit 2",
              r.returncode == 2, r.stdout + r.stderr)
        check("status Review, unfinished tasks: names the value review in the refusal",
              "review" in (r.stdout + r.stderr), r.stdout + r.stderr)
        check("status Review, unfinished tasks: no station write reaches the fake",
              not any("item-edit" in l for l in calls(tmpSt7)), str(calls(tmpSt7)))
        check("status Review, unfinished tasks: feature.json status is NOT recorded as Review",
              read_plan_station(featSt7) == "building",
              read_feature_json(os.path.join(featSt7, "feature.json")))

    # --- one sub-issue's set_station raising must not stop the remaining sub-issues from
    #     being written, exit 0, one stderr line, and feature.json's status still recorded.
    #     Custom fake: item-edit fails ONLY for ITEM_41; ITEM_42 and ITEM_43 still succeed.
    FAKE_GH_STATIONS_FIRST_ITEM_FAILS = FAKE_GH_STATIONS.replace(
        '  *"project item-edit"*)\n    exit 0 ;;',
        '  *"project item-edit"*"--id ITEM_41 "*)\n'
        '    echo "simulated item-edit failure for ITEM_41" >&2\n'
        '    exit 1 ;;\n'
        '  *"project item-edit"*)\n    exit 0 ;;',
    )

    assert 'ITEM_41' in FAKE_GH_STATIONS_FIRST_ITEM_FAILS and (
        FAKE_GH_STATIONS_FIRST_ITEM_FAILS != FAKE_GH_STATIONS), "fixture patch did not apply"

    with tempfile.TemporaryDirectory() as tmpSt8:
        install_gh(tmpSt8, FAKE_GH_STATIONS_FIRST_ITEM_FAILS)
        featSt8 = stage_station(
            tmpSt8, "FEAT-33-status-ready-one-fails",
            [("T-01", "done"), ("T-02", "done"), ("T-03", "done")],
            issues={"T-01": 41, "T-02": 42, "T-03": 43},
            parent=40,
            approval={"status": "approved"},
        )
        r = run(["status", featSt8, "ready"], tmpSt8, {"FACTORY_GH": os.path.join(tmpSt8, "gh")})
        logSt8 = calls(tmpSt8)
        editsSt8 = [l for l in logSt8 if "project item-edit" in l]
        ids8 = {next(p for p in l.split() if p.startswith("ITEM_")) for l in editsSt8}
        check("status Ready, one write raises: process still exits 0", r.returncode == 0,
              r.stdout + r.stderr)
        check("status Ready, one write raises: ITEM_41's write was attempted (and is what failed)",
              "ITEM_41" in ids8, str(editsSt8))
        check("status Ready, one write raises: the REMAINING sub-issues were still written",
              {"ITEM_42", "ITEM_43"}.issubset(ids8), str(editsSt8))
        check("status Ready, one write raises: one stderr ERROR line naming the issue",
              "gh-sync: ERROR" in r.stderr and "41" in r.stderr, r.stderr)
        check("status Ready, one write raises: feature.json status still recorded as Ready",
              read_plan_station(featSt8) == "ready",
              read_feature_json(os.path.join(featSt8, "feature.json")))

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
        check("ship records the pr in feature.json and the station in plan.yaml",
              r.returncode == 0 and docPR6.get("pr") == 55
              and read_plan_station(featPR6) == "done",
              f"rc={r.returncode} pr={docPR6.get('pr')} "
              f"station={read_plan_station(featPR6)!r}")

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
    return report()


if __name__ == "__main__":
    sys.exit(main())
