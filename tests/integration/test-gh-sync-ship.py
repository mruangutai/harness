#!/usr/bin/env python3
"""`gh-sync.py ship` against a board: the done-station writes, the open-child hold, the
audit, and the terminal-station commit.

Split out of test-gh-sync.py (issue #1527); the cases, their assertions and their
subprocess invocations are unchanged. Shared fixtures live in gh_sync_support.py.

    ./test-gh-sync-ship.py    -> exit 0 all pass, 1 otherwise
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import json
import os
import re
import subprocess
import sys
import tempfile

from gh_sync_support import (
    FAKE_GH_SHIP, FAKE_GH_STATIONS, HERE, SYNC, calls, check, edits_to, install_gh,
    moved_to_done, read_feature_json, read_plan_station, report, run, ship_env, stage_ship)


def main():
    # =============================================================================================
    # T-04 — ship writes the DONE STATION, closes nothing, and waits for open children.
    # =============================================================================================

    # --- every recorded card reaches Done, and NOTHING is closed --------------------------------
    with tempfile.TemporaryDirectory() as tmpS1:
        install_gh(tmpS1, FAKE_GH_SHIP)
        featS1 = stage_ship(tmpS1, "FEAT-40-ship-all", {"T-01": 41, "T-02": 42},
                             parent=40, source_issues=[50])
        r = run(["ship", featS1], tmpS1,
                ship_env(tmpS1, "40=Review 41=Review 42=Review 50=Review",
                         children={40: [41, 42, 50], 50: []}))
        logS1 = calls(tmpS1)
        doneS1 = moved_to_done(logS1)
        check("ship: exits 0", r.returncode == 0, r.stdout + r.stderr)
        for numS1 in (41, 42, 50, 40):
            check("ship: card #%d reaches the done station" % numS1,
                  numS1 in doneS1, "done=%s stdout=%r" % (sorted(doneS1), r.stdout))
        check("ship: closes NO issue - no `issue close` argv anywhere in the run",
              not any(l.startswith("issue close") for l in logS1), str(logS1))
        check("ship: closes NO issue - no state=closed PATCH against an ISSUE (the milestone "
              "PATCH is a milestone, not a card)",
              not any("state=closed" in l and re.search(r"\bissues/\d+\b", l) for l in logS1),
              str(logS1))
        check("ship: the milestone is still PATCHed closed",
              any("milestones/7" in l and "state=closed" in l for l in logS1), str(logS1))
        check("ship: prints the all-clear line when nothing was held and nothing failed",
              "gh-sync: every recorded card is at done" in r.stdout, repr(r.stdout))
        check("ship: prints NO HELD summary line when nothing was held",
              "gh-sync: HELD" not in r.stdout, repr(r.stdout))
        check("ship: prints NO FAILED line when nothing failed",
              "gh-sync: FAILED" not in r.stdout, repr(r.stdout))
        check("ship: no line contains 'gh-sync: SKIP' - post-merge-sweep.sh's worktree gate greps "
              "that literal and a healthy run must not trip it",
              "gh-sync: SKIP" not in (r.stdout + r.stderr), repr(r.stdout + r.stderr))
        check("ship: records the terminal status",
              read_plan_station(featS1) == "done",
              read_feature_json(os.path.join(featS1, "feature.json")))

    # --- D-10: a task sub-issue is moved WITHOUT any child check --------------------------------
    with tempfile.TemporaryDirectory() as tmpS2:
        install_gh(tmpS2, FAKE_GH_SHIP)
        featS2 = stage_ship(tmpS2, "FEAT-40-ship-depth1", {"T-01": 41}, parent=40)
        # #41 is given a child that is NOT at Done. If ship tested the sub-issue group, #41 would
        # be held; it must not be.
        r = run(["ship", featS2], tmpS2,
                ship_env(tmpS2, "40=Review 41=Review 99=Backlog",
                         children={40: [41], 41: [99]}))
        logS2 = calls(tmpS2)
        check("ship D-10: a task sub-issue reaches Done regardless of what sub_issues would say "
              "about it",
              41 in moved_to_done(logS2), "done=%s" % sorted(moved_to_done(logS2)))
        check("ship D-10: ship makes NO sub_issues read for a task sub-issue - the depth-1 "
              "exemption is a saved call, not just a skipped branch",
              not any("issues/41/sub_issues" in l for l in logS2), str(logS2))

    # --- the open-child test holds a parent, and names ONE child ---------------------------------
    with tempfile.TemporaryDirectory() as tmpS3:
        install_gh(tmpS3, FAKE_GH_SHIP)
        featS3 = stage_ship(tmpS3, "FEAT-40-ship-held", {"T-01": 41}, parent=40)
        r = run(["ship", featS3], tmpS3,
                ship_env(tmpS3, "40=Review 41=Review 77=Review 78=Review",
                         children={40: [78, 77, 41]}))
        logS3 = calls(tmpS3)
        heldS3 = [l for l in r.stdout.splitlines() if l.startswith("gh-sync: HELD — ")]
        check("ship HELD: the parent is NOT moved to Done",
              40 not in moved_to_done(logS3), "done=%s" % sorted(moved_to_done(logS3)))
        check("ship HELD: exactly ONE held line, naming the LOWEST-numbered open child",
              len(heldS3) == 1 and "#40 waiting on open child #77" in heldS3[0],
              "%r stdout=%r" % (heldS3, r.stdout))
        check("ship HELD: the parenthetical distinguishes a stationed child from a missing one",
              bool(heldS3) and "(not at done)" in heldS3[0], repr(heldS3))
        check("ship HELD: the summary line lists the held card and its child",
              "gh-sync: HELD 1 of 2 — #40 (child #77)" in r.stdout, repr(r.stdout))
        check("ship HELD: a run with holds and no failures prints NO FAILED line",
              "gh-sync: FAILED" not in r.stdout, repr(r.stdout))
        check("ship HELD: exit status is still 0 - a hold is a healthy outcome",
              r.returncode == 0, r.stdout + r.stderr)

    # --- a child absent from the board is OPEN, and says so differently --------------------------
    with tempfile.TemporaryDirectory() as tmpS4:
        install_gh(tmpS4, FAKE_GH_SHIP)
        featS4 = stage_ship(tmpS4, "FEAT-40-ship-offboard", {"T-01": 41}, parent=40)
        r = run(["ship", featS4], tmpS4,
                ship_env(tmpS4, "40=Review 41=Review", children={40: [41, 88]}))
        check("ship HELD: a child that is not on the board at all counts as OPEN, with its own "
              "parenthetical",
              "#40 waiting on open child #88 (not on the board)" in r.stdout, repr(r.stdout))

    # --- a child present with a NULL station is OPEN too -----------------------------------------
    with tempfile.TemporaryDirectory() as tmpS5:
        install_gh(tmpS5, FAKE_GH_SHIP)
        featS5 = stage_ship(tmpS5, "FEAT-40-ship-nullstation", {"T-01": 41}, parent=40)
        r = run(["ship", featS5], tmpS5,
                ship_env(tmpS5, "40=Review 41=Review 89=", children={40: [41, 89]}))
        check("ship HELD: a child on the board with NO station set counts as OPEN, reported as "
              "not at Done rather than not on the board",
              "#40 waiting on open child #89 (not at done)" in r.stdout, repr(r.stdout))

    # --- THE ORDERING: children are written before the parent is evaluated -----------------------
    with tempfile.TemporaryDirectory() as tmpS6:
        install_gh(tmpS6, FAKE_GH_SHIP)
        featS6 = stage_ship(tmpS6, "FEAT-40-ship-ordering", {"T-01": 41, "T-02": 42}, parent=40)
        # Both children start at Review. A single-pass implementation reads them as open and holds
        # the parent; writing the children FIRST is what lets the parent land in the same run.
        r = run(["ship", featS6], tmpS6,
                ship_env(tmpS6, "40=Review 41=Review 42=Review", children={40: [41, 42]}))
        doneS6 = moved_to_done(calls(tmpS6))
        check("ship ORDERING: a parent whose only open children are cards THIS RUN lands reaches "
              "Done in that same run",
              40 in doneS6 and "gh-sync: HELD" not in r.stdout,
              "done=%s stdout=%r" % (sorted(doneS6), r.stdout))

    # --- THE REFRESH SCOPE: a source that is itself a child of the parent -------------------------
    with tempfile.TemporaryDirectory() as tmpS7:
        install_gh(tmpS7, FAKE_GH_SHIP)
        featS7 = stage_ship(tmpS7, "FEAT-40-ship-refresh", {"T-01": 41}, parent=40,
                             source_issues=[50])
        # #50 is a source AND a child of #40. It is written during step 5's own pass, not step 4's.
        # An implementation that refreshes the station map only after the sub-issue writes still
        # reads #50 as open and wrongly holds the parent.
        r = run(["ship", featS7], tmpS7,
                ship_env(tmpS7, "40=Review 41=Review 50=Review",
                         children={40: [41, 50], 50: []}))
        doneS7 = moved_to_done(calls(tmpS7))
        check("ship REFRESH: a source_issues entry that is itself a child of the parent, moved in "
              "step 5's own pass, still lets the parent land in the same run",
              50 in doneS7 and 40 in doneS7 and "gh-sync: HELD" not in r.stdout,
              "done=%s stdout=%r" % (sorted(doneS7), r.stdout))

    # --- an UNREADABLE child set is never treated as childless ------------------------------------
    with tempfile.TemporaryDirectory() as tmpS8:
        install_gh(tmpS8, FAKE_GH_SHIP)
        featS8 = stage_ship(tmpS8, "FEAT-40-ship-unknown", {"T-01": 41}, parent=40)
        r = run(["ship", featS8], tmpS8,
                ship_env(tmpS8, "40=Review 41=Review", children={40: [41]},
                         SHIP_SUBISSUES_FAIL="40"))
        check("ship UNKNOWN: a sub_issues read that fails leaves the card UNMOVED - unknown is "
              "never childless",
              40 not in moved_to_done(calls(tmpS8)),
              "done=%s" % sorted(moved_to_done(calls(tmpS8))))
        check("ship UNKNOWN: it prints one stderr line naming the issue",
              "#40" in r.stderr and "child list unreadable" in r.stderr, repr(r.stderr))
        # THE REPORT IS THE POINT, not the exit code. An earlier cut printed the stderr line and
        # continued WITHOUT recording the miss, so the run ended with no `FAILED` line at all --
        # and post-merge-sweep.sh gates worktree removal on exactly three things: a non-zero exit,
        # `SKIP`, and `FAILED`. A card that silently missed done therefore had its evidence swept
        # away with the tree. An unreadable child list is a card that did not reach done, which is
        # what `FAILED` means, so it is reported like every other one.
        check("ship UNKNOWN: the miss is REPORTED on the FAILED line, so the sweep keeps the tree",
              "gh-sync: FAILED" in r.stdout and "#40" in r.stdout.split("gh-sync: FAILED")[1],
              repr(r.stdout))
        check("ship UNKNOWN: exit status is still 0", r.returncode == 0, r.stdout + r.stderr)

    # --- a BoardError on one card does not stop the rest, and IS reported -------------------------
    with tempfile.TemporaryDirectory() as tmpS9:
        install_gh(tmpS9, FAKE_GH_SHIP)
        featS9 = stage_ship(tmpS9, "FEAT-40-ship-failed", {"T-01": 41, "T-02": 42}, parent=40)
        # #41's write fails. It is deliberately NOT one of #40's children: if it were, the parent
        # would ALSO be held on it, and the run would print both lines for one cause -- which would
        # make "FAILED never covers a held card" untestable rather than true.
        r = run(["ship", featS9], tmpS9,
                ship_env(tmpS9, "40=Review 41=Review 42=Review", children={40: [42]},
                         SHIP_EDIT_FAIL="ITEM_41"))
        doneS9 = moved_to_done(calls(tmpS9))
        check("ship FAILED: one card's failure does not stop the remaining child writes",
              42 in doneS9, "done=%s" % sorted(doneS9))
        check("ship FAILED: the summary names exactly the card whose write failed",
              "gh-sync: FAILED 1 of 3 — #41 did not reach Done" in r.stdout, repr(r.stdout))
        check("ship FAILED: the FAILED line never covers a held card - this run held nothing",
              "gh-sync: HELD" not in r.stdout, repr(r.stdout))
        check("ship FAILED: exit status is still 0 - best-effort per card (DEC-146)",
              r.returncode == 0, r.stdout + r.stderr)
        check("ship FAILED: no line carries 'gh-sync: SKIP'",
              "gh-sync: SKIP" not in (r.stdout + r.stderr), repr(r.stdout + r.stderr))

    # --- the audit runs, AFTER the writes ----------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmpSA:
        install_gh(tmpSA, FAKE_GH_SHIP)
        featSA = stage_ship(tmpSA, "FEAT-40-ship-audit", {"T-01": 41}, parent=40)
        # #90 is CLOSED and its card reads Review - exactly the state a close made outside the
        # harness leaves behind, and the only thing that detects it.
        closedSA = json.dumps([{"number": 90, "stateReason": "COMPLETED", "labels": []},
                                {"number": 41, "stateReason": "COMPLETED", "labels": []}])
        r = run(["ship", featSA], tmpSA,
                ship_env(tmpSA, "40=Review 41=Review 90=Review", children={40: [41]},
                         SHIP_CLOSED_JSON=closedSA))
        auditSA = [l for l in r.stdout.splitlines() if l.startswith("gh-sync: audit — ")]
        check("ship AUDIT: it runs, and every finding is printed under ship's own prefix",
              any("STATION" in l and "#90" in l for l in auditSA),
              "%r stdout=%r" % (auditSA, r.stdout))
        check("ship AUDIT ORDERING: a card THIS RUN moved to Done produces no STATION finding - "
              "the audit runs after the writes, not before",
              not any("#41" in l for l in auditSA), repr(auditSA))
        check("ship AUDIT: a summary line counts the findings",
              any(re.search(r"audit — \d+ finding\(s\)", l) for l in auditSA), repr(auditSA))
        check("ship AUDIT: no audit line carries 'gh-sync: SKIP' or 'gh-sync: FAILED'",
              not any("gh-sync: SKIP" in l or "gh-sync: FAILED" in l for l in auditSA),
              repr(auditSA))

    # --- an audit that cannot run does not take the ship down ---------------------------------------
    with tempfile.TemporaryDirectory() as tmpSB:
        install_gh(tmpSB, FAKE_GH_SHIP)
        featSB = stage_ship(tmpSB, "FEAT-40-ship-audit-fails", {"T-01": 41}, parent=40)
        r = run(["ship", featSB], tmpSB,
                ship_env(tmpSB, "40=Review 41=Review", children={40: [41]},
                         SHIP_CLOSED_JSON="not json at all"))
        check("ship AUDIT: an audit that cannot run leaves the exit status 0",
              r.returncode == 0, r.stdout + r.stderr)
        check("ship AUDIT: it prints one stderr line saying the audit could not run",
              "the board audit could not run" in r.stderr, repr(r.stderr))
        check("ship AUDIT: the cards were still written and the status still recorded",
              41 in moved_to_done(calls(tmpSB))
              and read_plan_station(featSB) == "done",
              r.stdout)

    # --- REGRESSION GUARD, REQ-10: status Review still moves the parent and every sub-issue -------
    with tempfile.TemporaryDirectory() as tmpSC:
        install_gh(tmpSC, FAKE_GH_SHIP)
        featSC = stage_ship(tmpSC, "FEAT-40-ship-review-guard", {"T-01": 41, "T-02": 42}, parent=40)
        r = run(["status", featSC, "review"], tmpSC,
                ship_env(tmpSC, "40=Backlog 41=Backlog 42=Backlog"))
        reviewSC = set()
        for l in edits_to(calls(tmpSC), "OPT_REVIEW"):
            m = re.search(r"--id ITEM_(\d+)", l)
            if m:
                reviewSC.add(int(m.group(1)))
        for numSC in (40, 41, 42):
            check("REQ-10 guard: status Review still writes the review station for #%d" % numSC,
                  numSC in reviewSC, "review=%s stdout=%r" % (sorted(reviewSC), r.stdout))

    # --- REGRESSION GUARD, SC-12 second clause: BEHAVIOURAL, then a secondary grep ------------------
    for subSD, argsSD in (("status Ready", ["status", "@", "ready"]),
                           ("start-task", ["start-task", "@", "T-01"]),
                           ("abandon", ["abandon", "@", "--reason-file", "@REASON"])):
        with tempfile.TemporaryDirectory() as tmpSE:
            install_gh(tmpSE, FAKE_GH_SHIP)
            featSE = stage_ship(tmpSE, "FEAT-40-only-writer", {"T-01": 41}, parent=40)
            reasonSE = os.path.join(tmpSE, "reason.txt")
            open(reasonSE, "w").write("fixture reason")
            argvSE = [featSE if a == "@" else (reasonSE if a == "@REASON" else a) for a in argsSD]
            run(argvSE, tmpSE, ship_env(tmpSE, "40=Backlog 41=Backlog"))
            check("SC-12: `%s` writes NO done station - ship is the only writer" % subSD,
                  not edits_to(calls(tmpSE), "OPT_DONE"), str(calls(tmpSE)))

    # SECONDARY ONLY. A grep dies to a rename and cannot see a value passed through a local, so it
    # must never be the only evidence - the behavioural cases above are the real assertion.
    #
    # THE PATTERN CHANGED SHAPE, NOT INTENT (FEAT-41 T-16). It matched `done = board["stations"]["done"]`
    # back when a station name was looked up in the board declaration. T-02 deleted that indexing —
    # the declaration carries no column names to look up — so the binding is now the lowercase station
    # itself. What must stay unique is unchanged: the one BINDING a station write is made from.
    _srcSD = open(SYNC).read()

    # The value is also READ in `cmd_start_task`'s guard, which compares a card's current station
    # against it and refuses -- a read, never a write. What must be unique is the BINDING that a
    # station write is made from.
    _doneRefsSD = [ln.strip() for ln in _srcSD.splitlines()
                   if ln.strip() == 'done = "done"']

    check("SC-12 (secondary): exactly one place BINDS the done station for writing, and it is "
          "cmd_ship's own local",
          len(_doneRefsSD) == 1, repr(_doneRefsSD))

    # ==========================================================================================
    # FEAT-41 T-10: the two ship defects.
    # ==========================================================================================

    # ---- DEFECT ONE: the terminal station write is COMMITTED ---------------------------------
    # It used to be left in the working tree, so the default branch read a non-terminal station
    # while the board read the done column — the INV-26 violation check-state.sh reported against
    # FEAT-40 and issue 842. This asserts the file is CLEAN AGAINST HEAD after a successful ship,
    # which is the property the violation's absence actually depends on.
    with tempfile.TemporaryDirectory() as tmpC:
        install_gh(tmpC, FAKE_GH_STATIONS)
        featC = stage_ship(tmpC, "FEAT-50-commit-station", {"T-01": 41}, parent=40, milestone=7)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmpC, capture_output=True)
        subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=tmpC,
                       capture_output=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=tmpC, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=tmpC, capture_output=True)
        subprocess.run(["git", "commit", "-qm", "fixture"], cwd=tmpC, capture_output=True)
        rC = run(["ship", featC], tmpC, ship_env(tmpC, "40=Review 41=Review"))
        planC = os.path.join(featC, "plan.yaml")
        dirtyC = subprocess.run(["git", "status", "--porcelain", "--", planC], cwd=tmpC,
                                capture_output=True, text=True).stdout.strip()
        check("T-10 defect one: after a successful ship the station file is CLEAN against HEAD",
              rC.returncode == 0 and dirtyC == "",
              f"exit {rC.returncode}; dirty={dirtyC!r}; out={rC.stdout[-500:]!r}")
        check("T-10 defect one: ship names the commit it made",
              "station done committed as" in rC.stdout, f"out={rC.stdout[-500:]!r}")
        logC = subprocess.run(["git", "log", "-1", "--format=%s"], cwd=tmpC,
                              capture_output=True, text=True).stdout.strip()
        check("T-10 defect one: the commit subject names the feature and the station",
              logC == "FEAT-50-commit-station: station done at ship", f"subject={logC!r}")
        # ONLY THAT ONE FILE. A ship that swept in whatever the operator had staged would be a
        # worse surprise than the uncommitted station this fixes.
        filesC = subprocess.run(["git", "show", "--name-only", "--format=", "HEAD"], cwd=tmpC,
                                capture_output=True, text=True).stdout.split()
        check("T-10 defect one: the commit carries EXACTLY ONE file, the plan",
              len(filesC) == 1 and filesC[0].endswith("plan.yaml"), f"files={filesC}")

    # BUG-1114: THE SAME SHIP WITH A **RELATIVE** FEATURE DIR MUST ALSO COMMIT.
    #
    # The case above passes an ABSOLUTE feat_dir, because `stage_ship` builds one from a
    # TemporaryDirectory. That is why this bug shipped invisibly: `_commit_terminal_station` sets
    # `git -C <feature dir>` and then passes the pathspec AS GIVEN, so a RELATIVE dir makes git resolve
    # the pathspec against `-C` and produce a doubled path that does not exist. `git status` prints a
    # warning to stderr, stdout reads EMPTY, and the function concludes the file is clean:
    #
    #     gh-sync: station already committed — ... plan.yaml is clean against HEAD
    #
    # It then returns WITHOUT committing, at exit 0. Measured on FEAT-41's real ship: relative left
    # plan.yaml dirty and reported success; absolute committed as b3e943ca.
    #
    # `run()` sets no cwd, so this case drives the subprocess directly with cwd=tmp — that is the whole
    # point, since the defect only exists when the pathspec is resolved somewhere other than the repo
    # root. Same fixture, same assertions, one changed argument.
    with tempfile.TemporaryDirectory() as tmpR:
        install_gh(tmpR, FAKE_GH_STATIONS)
        featR = stage_ship(tmpR, "FEAT-52-relative-dir", {"T-01": 41}, parent=40, milestone=7)
        for _cmd in (["git", "init", "-q", "-b", "main"],
                     ["git", "config", "user.email", "t@example.com"],
                     ["git", "config", "user.name", "t"],
                     ["git", "add", "-A"], ["git", "commit", "-qm", "fixture"]):
            subprocess.run(_cmd, cwd=tmpR, capture_output=True)
        _envR = dict(os.environ)
        _envR["FAKE_LOG"] = os.path.join(tmpR, "calls.log")
        _envR["GH_SYNC_GH"] = os.path.join(tmpR, "gh")
        _envR.update(ship_env(tmpR, "40=Review 41=Review"))
        _relR = os.path.relpath(featR, tmpR)
        rR = subprocess.run([SYNC, "ship", _relR], cwd=tmpR, capture_output=True, text=True,
                            env=_envR)
        planR = os.path.join(featR, "plan.yaml")
        dirtyR = subprocess.run(["git", "status", "--porcelain", "--", planR], cwd=tmpR,
                                capture_output=True, text=True).stdout.strip()
        check("BUG-1114: a ship given a RELATIVE feature dir still COMMITS the station",
              rR.returncode == 0 and dirtyR == "",
              f"exit {rR.returncode}; dirty={dirtyR!r}; out={rR.stdout[-600:]!r}")
        check("BUG-1114: and it does not claim the station was already committed when it was not",
              "already committed" not in rR.stdout and "station done committed as" in rR.stdout,
              f"out={rR.stdout[-600:]!r}")
        logR = subprocess.run(["git", "log", "-1", "--format=%s"], cwd=tmpR,
                              capture_output=True, text=True).stdout.strip()
        check("BUG-1114: the commit subject is the same one the absolute path produces",
              logR == "FEAT-52-relative-dir: station done at ship", f"subject={logR!r}")

    # THE DISCRIMINATOR FOR "ONLY ONE FILE": an unrelated dirty file must survive the ship
    # uncommitted. Without this the case above passes against a `git commit -a`.
    with tempfile.TemporaryDirectory() as tmpD:
        install_gh(tmpD, FAKE_GH_STATIONS)
        featD = stage_ship(tmpD, "FEAT-51-only-one", {"T-01": 41}, parent=40, milestone=7)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmpD, capture_output=True)
        subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=tmpD,
                       capture_output=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=tmpD, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=tmpD, capture_output=True)
        subprocess.run(["git", "commit", "-qm", "fixture"], cwd=tmpD, capture_output=True)
        bystander = os.path.join(tmpD, "BYSTANDER.md")
        open(bystander, "w").write("edited by the operator, never staged by ship\n")
        subprocess.run(["git", "add", bystander], cwd=tmpD, capture_output=True)
        rD = run(["ship", featD], tmpD, ship_env(tmpD, "40=Review 41=Review"))
        stillD = subprocess.run(["git", "status", "--porcelain", "--", bystander], cwd=tmpD,
                                capture_output=True, text=True).stdout.strip()
        check("T-10 defect one DISCRIMINATOR: an unrelated STAGED file is NOT swept into the "
              "station commit — it is still uncommitted afterwards",
              rD.returncode == 0 and stillD != "",
              f"exit {rD.returncode}; bystander status={stillD!r}")

    # IDEMPOTENT. ship runs again and finds nothing to commit; that is not a failure and it says so.
    with tempfile.TemporaryDirectory() as tmpE:
        install_gh(tmpE, FAKE_GH_STATIONS)
        featE = stage_ship(tmpE, "FEAT-52-twice", {"T-01": 41}, parent=40, milestone=7)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmpE, capture_output=True)
        subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=tmpE,
                       capture_output=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=tmpE, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=tmpE, capture_output=True)
        subprocess.run(["git", "commit", "-qm", "fixture"], cwd=tmpE, capture_output=True)
        run(["ship", featE], tmpE, ship_env(tmpE, "40=Review 41=Review"))
        rE2 = run(["ship", featE], tmpE, ship_env(tmpE, "40=Review 41=Review"))
        check("T-10 defect one: a SECOND ship commits nothing and says the file is already clean",
              rE2.returncode == 0 and "already committed" in rE2.stdout,
              f"exit {rE2.returncode}; out={rE2.stdout[-400:]!r}")

    # ---- DEFECT TWO: ship REFUSES a feature dir inside a worktree ----------------------------
    with tempfile.TemporaryDirectory() as tmpW:
        install_gh(tmpW, FAKE_GH_STATIONS)
        # The owner checkout, with the worktrees segment underneath it, is what makes
        # harness_boundary.worktree_owner able to name the main-checkout path.
        owner = os.path.join(tmpW, "owner")
        os.makedirs(owner)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=owner, capture_output=True)
        wt_root = os.path.join(owner, ".claude", "worktrees", "harness", "FEAT-53-in-a-worktree")
        os.makedirs(wt_root)
        featW = stage_ship(wt_root, "FEAT-53-in-a-worktree", {"T-01": 41}, parent=40, milestone=7)
        rW = run(["ship", featW], tmpW, ship_env(wt_root, "40=Review 41=Review",
                                                  FACTORY_GH=os.path.join(tmpW, "gh")))
        check("T-10 defect two: ship REFUSES a feature dir inside a worktree, exit 1",
              rW.returncode == 1, f"exit {rW.returncode}; out={(rW.stdout + rW.stderr)[-500:]!r}")
        outW = rW.stdout + rW.stderr
        # THE REASON COMES FIRST. A refusal that says only what to use instead is
        # indistinguishable from a stuck gate, and an agent reading it as one retries elsewhere.
        check("T-10 defect two: the refusal STATES THE REASON — the worktree is about to be "
              "deleted, so the station would not survive",
              "about to be deleted" in outW and "would not survive" in outW,
              f"out={outW[-500:]!r}")
        check("T-10 defect two: the refusal names the equivalent path in the MAIN CHECKOUT",
              "main checkout" in outW, f"out={outW[-500:]!r}")
        # A REFUSAL, NOT A SKIP. skip() exits 0 and post-merge-sweep.sh reads a SKIP as
        # "nothing went wrong" — it would delete the worktree, taking the station with it.
        check("T-10 defect two: it is a REFUSAL and not a SKIP — the sweep must not read this as "
              "permission to delete",
              "gh-sync: SKIP" not in outW, f"out={outW[-500:]!r}")

    # ---- THE SWEEP'S POSITIVE-SIGNAL GATE IS UNCHANGED --------------------------------------
    # post-merge-sweep.sh gates worktree removal on the ABSENCE of `gh-sync: SKIP` and
    # `gh-sync: FAILED` from ship's combined output. The commit added by defect one must never
    # emit either word on a failure path, or a trivial bookkeeping miss would silently cancel a
    # worktree removal — a different subsystem entirely.
    with tempfile.TemporaryDirectory() as tmpS:
        install_gh(tmpS, FAKE_GH_STATIONS)
        featS = stage_ship(tmpS, "FEAT-54-no-milestone", {"T-01": 41}, parent=40, milestone=None)
        rS = run(["ship", featS], tmpS, ship_env(tmpS, "40=Review 41=Review"))
        check("T-10: ship still reports SKIP with its exact positive-signal wording when there is "
              "no recorded milestone",
              rS.returncode == 0 and "gh-sync: SKIP" in (rS.stdout + rS.stderr),
              f"exit {rS.returncode}; out={(rS.stdout + rS.stderr)[-400:]!r}")

    # NO GIT REPOSITORY AT ALL: the commit cannot succeed, and the sweep's two signal words must
    # still be absent from the output so the failure stays confined to this one line.
    with tempfile.TemporaryDirectory() as tmpN:
        install_gh(tmpN, FAKE_GH_STATIONS)
        featN = stage_ship(tmpN, "FEAT-55-no-git", {"T-01": 41}, parent=40, milestone=7)
        rN = run(["ship", featN], tmpN, ship_env(tmpN, "40=Review 41=Review"))
        bothN = rN.stdout + rN.stderr
        check("T-10: with NO git repository the station commit fails LOUDLY but does not change "
              "the exit status",
              rN.returncode == 0 and "WARNING" in bothN, f"exit {rN.returncode}; out={bothN[-600:]!r}")
        check("T-10: and that failure line contains NEITHER sweep signal word, so an uncommitted "
              "station cannot cancel a worktree removal",
              "gh-sync: SKIP" not in bothN and "gh-sync: FAILED" not in bothN,
              f"out={bothN[-600:]!r}")

    # ---------------------------------------------------------------------------------------------
    # FEAT-41 F-01: A STATION WRITE THAT NEVER REACHED DISK MUST BE VISIBLE TO THE SWEEP.
    #
    # Found by the validation panel, not by this suite, and the gap IS the finding: no case here
    # drove either failure branch of `_record_station`, so nothing measured what post-merge-sweep.sh
    # would then do. The sweep gates worktree REMOVAL on the ABSENCE of two literals from ship's
    # combined output. A station that was never recorded anywhere is exactly the case where the
    # standing worktree is the only surviving evidence -- so that failure line must carry one of
    # those literals, or the sweep deletes the tree and takes the only record with it. Irreversible.
    #
    # THE LITERALS ARE READ OUT OF THE SWEEP, NEVER RETYPED. This is a contract between two files,
    # and a test holding its own copy of the string keeps passing while the real gate drifts away.
    #
    # THE ASYMMETRY WITH `_commit_terminal_station` IS DELIBERATE, and it is asserted immediately
    # above (T-10): an UNCOMMITTED station is a recoverable bookkeeping miss and must NOT cancel a
    # removal. Written-nowhere and written-but-uncommitted are different failures whose correct
    # answers are opposite. Do not "fix" the two into agreement.
    # ---------------------------------------------------------------------------------------------
    _GATE_LITERALS = re.findall(r'if "([^"]+)" in combined:',
                                open(os.path.join(HERE, "post-merge-sweep.sh")).read())

    check("F-01 fixture: the sweep's gate literals are discoverable in post-merge-sweep.sh, so this "
          "case cannot pass by asserting against a string nothing actually reads",
          len(_GATE_LITERALS) >= 2, repr(_GATE_LITERALS))

    for _labelF, _breakF in (("absent plan.yaml", "unlink"),
                             ("set-feature-station exits non-zero", "garble")):
        with tempfile.TemporaryDirectory() as tmpF:
            install_gh(tmpF, FAKE_GH_STATIONS)
            featF = stage_ship(tmpF, "FEAT-98-station-write-fails", {"T-01": 41}, parent=40)
            planF = os.path.join(featF, "plan.yaml")
            if _breakF == "unlink":
                os.remove(planF)
            else:
                # A LIST WHERE A MAPPING BELONGS. plan-merge.py validates the parsed result before
                # replacing the file, so this drives the non-zero-exit branch rather than the
                # absent-file one -- two different prints, both of which the sweep must see.
                open(planF, "w").write("- not a mapping\n")
            rF = run(["ship", featF], tmpF, ship_env(tmpF, "40=Review 41=Review"))
            bothF = rF.stdout + rF.stderr
            check(f"F-01 ({_labelF}): ship says the station was not recorded",
                  "not recorded" in bothF, f"exit {rF.returncode}; out={bothF[-700:]!r}")
            check(f"F-01 ({_labelF}): and that line carries a literal post-merge-sweep.sh gates on, "
                  f"so the sweep keeps the worktree holding the only record of the station",
                  any(lit in bothF for lit in _GATE_LITERALS),
                  f"gates={_GATE_LITERALS} out={bothF[-700:]!r}")
    return report()


if __name__ == "__main__":
    sys.exit(main())
