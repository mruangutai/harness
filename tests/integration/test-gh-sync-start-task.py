#!/usr/bin/env python3
"""`gh-sync.py start-task`: the station writes, the guard that refuses a closed or
already-done card, the parent rule, the board preconditions, and the plan-write
failure -- plus the dangling-plan diagnosis both it and `status` must produce.

Split out of test-gh-sync.py (issue #1527); the cases, their assertions and their
subprocess invocations are unchanged. Shared fixtures live in gh_sync_support.py.

    ./test-gh-sync-start-task.py    -> exit 0 all pass, 1 otherwise
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import contextlib
import io
import json
import os
import sys
import tempfile

import feature_schema
import harness_yaml

from gh_sync_support import (
    FAKE_GH_SHIP, FAKE_GH_STATIONS, FAKE_GH_STATIONS_CUSTOM, FAKE_GH_STATIONS_GUARD_READ_FAILS,
    calls, check, install_gh, load_gh_sync, read_feature_json, report, run, ship_env,
    stage_depends_on, stage_ship, stage_station, write_dangling_plan_yaml, write_feature_json,
    write_plan_yaml)


# gh-sync.py's hyphen blocks a plain import; the refuse() cases below assert
# that function's own contract rather than a subcommand's output.
_ghs = load_gh_sync()


def _without_build_entry(feat):
    path = os.path.join(feat, "feature.json")
    document = read_feature_json(path)
    document["github"].pop("build_entry", None)
    write_feature_json(path, feature_id=document["feature_id"], github=document["github"])


def main():
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
            [("T-01", "done"), ("T-02", "building"), ("T-03", "ready")],
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
            [("T-01", "done"), ("T-02", "building"), ("T-03", "ready")],
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
              # `done` LOWERCASE (FEAT-41 T-02): the refusal quotes the card's current station as
              # gh_board.board_stations returned it, and that read is lowercased at the boundary.
              # The capitalised form would mean the boundary had leaked.
              "gh-sync: refusing #326" in r.stdout and "T-02" in r.stdout and "done" in r.stdout,
              r.stdout)

    # --- an open issue at Backlog is still moved to Building — the guard changes nothing for the
    #     case it was never meant to touch.
    with tempfile.TemporaryDirectory() as tmpN3:
        install_gh(tmpN3, FAKE_GH_STATIONS)
        featN3 = stage_station(
            tmpN3, "FEAT-09-start-task-open-backlog",
            [("T-01", "done"), ("T-02", "building"), ("T-03", "ready")],
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
            [("T-01", "done"), ("T-02", "building"), ("T-03", "ready")],
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
            [("T-01", "done"), ("T-02", "building"), ("T-03", "ready")],
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
            [("T-01", "done"), ("T-02", "building"), ("T-03", "ready")],
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
            [("T-01", "done"), ("T-02", "building"), ("T-03", "ready")],
            issues={"T-01": 41, "T-02": 326},
            parent=40,
            stations=CUSTOM_STATIONS,
        )
        r = run(["start-task", featN7, "T-02"], tmpN7,
                {"FACTORY_GH": os.path.join(tmpN7, "gh"),
                 "GUARD_ISSUE": "326", "GUARD_STATE": "OPEN", "GUARD_STATION_NAME": "Todo"})
        logN7 = calls(tmpN7)
        editsN7 = [l for l in logN7 if "project item-edit" in l]
        # INVERTED, NOT PATCHED (FEAT-41 T-16). This case proved a board could RENAME its columns —
        # declare `building: "Doing"` — and that the tool would select the declared option rather
        # than a hardcoded OPT_BUILDING. That capability is GONE BY DESIGN: T-01 fixes the six names
        # and DERIVES every column from them through factory_config.station_column, so a renamed
        # declaration is no longer a supported configuration but a loud FleetError.
        #
        # The case is kept and turned around rather than deleted, because its SPIRIT is still the
        # thing that matters: the tool must never silently write the wrong option. Before, that meant
        # "read the declaration instead of a literal". Now it means "refuse a declaration that tries
        # to choose". Deleting it would leave nothing asserting either.
        # WHERE THE REFUSAL LANDS, MEASURED RATHER THAN ASSUMED. My first attempt at this inversion
        # asserted a validation refusal with a non-zero exit. Wrong mechanism: the declaration is a
        # LIST of the six fixed names now, so it is perfectly VALID — there is no longer anywhere in
        # it to express a rename. The rename lives only on the BOARD, and the harness meets it at the
        # write: station_column derives `Building`, GitHub offers only `Doing`, and the option lookup
        # fails by name.
        #
        # Exit stays 0 and that is the point — a failed card write has never gated this tool
        # (DEC-146, DEC-138). What must hold is that the harness does not CHASE the rename.
        _outN7 = r.stdout + r.stderr
        check("renamed board: exit 0 — a failed card write still never gates",
              r.returncode == 0, f"exit {r.returncode}: {_outN7[:200]!r}")
        check("renamed board: one loud ERROR naming the option the board does not offer",
              "option not found" in _outN7 and "Building" in _outN7, _outN7[:300])
        check("renamed board: the harness NEVER writes the renamed option — it derives the fixed "
              "name and stops, rather than hunting for a column that fits",
              not any("OPT_DOING" in l for l in editsN7), str(editsN7))

    # --- the parent reaches Review when every task is done. RETARGETED to start-task by T-11.
    #     The derivation is CALLER-INDEPENDENT BY CONSTRUCTION -- _apply_parent_rule's own
    #     docstring says it reads plan.yaml from disk and never infers the transition from which
    #     subcommand called it -- so start-task exercises the same property close-task did.
    #     The two ORDERING assertions that stood here are deleted, not retargeted: they ordered
    #     the parent write against a sub-issue close that no longer exists.
    with tempfile.TemporaryDirectory() as tmpO:
        install_gh(tmpO, FAKE_GH_STATIONS)
        featO = stage_station(
            tmpO, "FEAT-09-close-last-task",
            [("T-01", "done"), ("T-02", "done"), ("T-03", "done")],
            issues={"T-01": 41, "T-02": 42, "T-03": 43},
            parent=40,
        )
        r = run(["start-task", featO, "T-03"], tmpO, {"FACTORY_GH": os.path.join(tmpO, "gh")})
        logO = calls(tmpO)
        editsO = [l for l in logO if "project item-edit" in l]
        check("every task done: exits 0", r.returncode == 0, r.stdout + r.stderr)
        # THE PREMISE NO LONGER SURVIVES THE COMMAND (FEAT-41 T-16, consequence of T-06).
        # start-task now RECORDS the task's station in plan.yaml before it touches the board, so
        # `start-task T-03` on an all-done plan makes T-03 `building` — and the parent therefore
        # derives building, not review. "Every task done AND T-03 just started" is a contradiction.
        #
        # NOT WEAKENED: the all-done -> review rule is asserted directly, on project, in
        # test-gh-board.py. What this case can uniquely still prove is stronger than what it proved
        # before — that start-task's PLAN WRITE really happened and is the input the placement is
        # computed from. A card at review here would mean the plan write silently did nothing.
        check("every task done, then start-task: the parent follows the PLAN WRITE to building, "
              "never the pre-command review",
              any("--id ITEM_40" in l and "--single-select-option-id OPT_BUILDING" in l
                  for l in editsO)
              and not any("--id ITEM_40" in l and "OPT_REVIEW" in l for l in editsO),
              str(editsO))

    # --- a feature whose feature.json status is Done writes NO station at all -- the terminal
    #     exemption (D-03/D-04). RETARGETED to start-task by T-11; the exemption is a property of
    #     _apply_parent_rule, which reads feature.json, not of whichever subcommand called it.
    #     The third assertion, that the sub-issue still closes, went with the command.
    with tempfile.TemporaryDirectory() as tmpP:
        install_gh(tmpP, FAKE_GH_STATIONS)
        featP = stage_station(
            tmpP, "FEAT-09-done-exempt",
            [("T-01", "done")],
            issues={"T-01": 41},
            parent=40,
            feature_status=None, plan_station="done",
        )
        r = run(["start-task", featP, "T-01"], tmpP, {"FACTORY_GH": os.path.join(tmpP, "gh")})
        logP = calls(tmpP)
        check("a Done feature exits 0", r.returncode == 0, r.stdout + r.stderr)
        # NARROWED FROM "no item-edit at all". The terminal exemption is _apply_parent_rule's,
        # and it covers the PARENT card. The deleted subcommand wrote no station for its own
        # sub-issue, so "none at all" happened to be true through it; start-task writes the
        # sub-issue's own station unconditionally, which the exemption never governed. Asserting
        # the wider claim through the new caller would assert something that was never the rule.
        check("a Done feature writes NO PARENT station — the terminal exemption",
              not any("item-edit" in l and "ITEM_40" in l for l in logP), str(logP))

    # --- THE LOUD PAIR (SC-04/D-02), one fixture per half, both required —
    #     half 1: gh works but the station write (item-edit) fails -> exit 0, one ERROR line on
    #     stderr naming the issue, AND the call that follows (the sub-issue close) still happens.
    # THE FIXTURE CHANGED WITH THE CALLER. The deleted subcommand made no board READ, so a stub
    # that only answered item-edit was enough for it. start-task reads the board first (its
    # already-Done guard), so the stub has to answer that query too, and FAKE_GH_SHIP is the one
    # that does. SHIP_EDIT_FAIL picks which single card's write fails.
    with tempfile.TemporaryDirectory() as tmpQ1:
        install_gh(tmpQ1, FAKE_GH_SHIP)
        featQ1 = stage_ship(tmpQ1, "FEAT-09-loud-item-edit-fails", {"T-01": 41, "T-02": 42},
                             parent=40)
        r = run(["start-task", featQ1, "T-02"], tmpQ1,
                ship_env(tmpQ1, "40=Building 41=Building 42=Backlog", SHIP_EDIT_FAIL="ITEM_42"))
        logQ1 = calls(tmpQ1)
        check("loud pair (item-edit fails): process still exits 0", r.returncode == 0,
              r.stdout + r.stderr)
        check("loud pair (item-edit fails): stderr carries the gh-sync: ERROR line naming the "
              "card whose write failed",
              "gh-sync: ERROR" in r.stderr and "42" in r.stderr, r.stderr)
        # RETARGETED by T-11, and the PROPERTY is unchanged: one failed write must not stop the
        # call that follows it. It used to be asserted against the sub-issue close; the surviving
        # sequence is the sub-issue's own station write followed by the parent's, so the parent
        # write must still be attempted after the sub-issue's fails.
        check("loud pair (item-edit fails): a failed card write does not stop the write that "
              "follows it — the parent write was still attempted",
              any("item-edit" in l and "ITEM_40" in l for l in logQ1), str(logQ1))

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
        r = run(["start-task", featQ2, "T-02"], tmpQ2,
                {"GH_SYNC_GH": os.path.join(tmpQ2, "no-such-gh"),
                 "FACTORY_GH": os.path.join(tmpQ2, "no-such-gh")})
        check("loud pair (gh absent): one SKIP line, exit 0",
              r.returncode == 0 and r.stdout.count("SKIP") == 1, r.stdout + r.stderr)
        check("loud pair (gh absent): no item-edit call is even attempted",
              not calls(tmpQ2), str(calls(tmpQ2)))

    # --- a feature whose harness.json carries no github.board runs open and start-task unchanged,
    #     exits 0, and makes no item-edit call — the environmental precondition (D-02).
    #     RETARGETED from close-task by T-11: the precondition is a property of the environment,
    #     not of the subcommand that meets it.
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
        open(os.path.join(tmpR, "calls.log"), "w").close()
        r2 = run(["start-task", featR, "T-02"], tmpR, {"FACTORY_GH": os.path.join(tmpR, "gh")})
        logR = calls(tmpR)
        check("no board configured: start-task exits 0", r2.returncode == 0, r2.stdout + r2.stderr)
        check("no board configured: no item-edit call is ever made",
              not any("item-edit" in l for l in logR), str(logR))
        # The lifecycle-ran proof, retargeted: it used to be that close-task really closed T-01's
        # issue. start-task's own recorded evidence is the plan.yaml status it requires and the
        # exit 0 above; assert it did not silently no-op by requiring the recorded issue exists.
        check("no board configured: the issue lifecycle still ran — T-01 and T-02 are recorded",
              t1R is not None and t2R is not None, str(docR))

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

    # =============================================================================================
    # FEAT-41 T-16 — start-task's PLAN WRITE fails loudly, and writes no card when it does.
    # The case T-06 introduced the behaviour for and could not land, because this suite was red.
    # =============================================================================================
    # WHY LOUD RATHER THAN BEST-EFFORT. Every other failure in this file is best-effort: a card that
    # will not move prints one line and the command carries on, because the mirror never gates
    # (DEC-138). The PLAN write is the exception, and the asymmetry is the point — the plan is the
    # TRUTH and the board is the mirror. A board write that fails leaves the truth intact; a PLAN
    # write that fails and is then mirrored anyway puts a Building card against a task the plan does
    # not call building, which is the two-words-two-meanings drift this whole feature exists to end.
    with tempfile.TemporaryDirectory() as tmpPW:
        install_gh(tmpPW, FAKE_GH_STATIONS)
        featPW = stage_station(
            tmpPW, "FEAT-09-plan-write-fails",
            [("T-01", "done"), ("T-02", "building")],
            issues={"T-01": 41, "T-99": 326},
            parent=40,
        )
        # THE FAILURE IS PROVOKED AT THE VERB, not by mocking gh: T-99 IS recorded in feature.json —
        # so the "no recorded issue" skip does not fire and control reaches the plan write — but it is
        # ABSENT from plan.yaml, so plan-merge.py set-task-station exits non-zero. A real refusal from
        # the real tool rather than a simulated one.
        #
        # That combination is also a realistic drift: the mirror's record carrying a task the plan
        # does not. Before T-06 this command would happily have moved that card.
        r = run(["start-task", featPW, "T-99"], tmpPW, {"FACTORY_GH": os.path.join(tmpPW, "gh")})
        outPW = r.stdout + r.stderr
        editsPW = [l for l in calls(tmpPW) if "project item-edit" in l]
        check("plan write fails: start-task REFUSES, exit 2 — not a best-effort carry-on",
              r.returncode == 2, f"exit {r.returncode}: {outPW[:300]!r}")
        check("plan write fails: the refusal names the task, the plan path and the verb that failed",
              "T-99" in outPW and "plan.yaml" in outPW and "set-task-station" in outPW, outPW[:400])
        check("plan write fails: NO card is written — the mirror never runs ahead of the truth",
              not editsPW, str(editsPW))

    # ---- T-07: the terminal exemption reads its station from plan.yaml -----------------------
    #
    # `_feature_status` feeds EXACTLY one comparison — the terminal exemption in
    # `_apply_parent_rule` — so this is the case that proves the repointing. With the status key
    # gone and the reader un-repointed, `_feature_status` returns None, the exemption never fires,
    # and start-task writes the parent's card to the plan-derived station on a SHIPPED feature.
    # That is the fail-open direction and it is a WRITE: the mirror moves a done parent back.

    with tempfile.TemporaryDirectory() as tmpT7:
        install_gh(tmpT7, FAKE_GH_STATIONS)
        # Post-migration shape: NO feature.json status, station `done` in plan.yaml.
        featT7 = stage_station(
            tmpT7, "FEAT-80-terminal-from-plan",
            [("T-01", "done"), ("T-02", "building")],
            issues={"T-01": 41, "T-02": 42}, parent=40,
            feature_status=None, plan_station="done",
        )
        r = run(["start-task", featT7, "T-02"], tmpT7, {"FACTORY_GH": os.path.join(tmpT7, "gh")})
        parent_editsT7 = [l for l in calls(tmpT7) if "project item-edit" in l and "40" in l]
        check("T-07: the terminal exemption fires from plan.yaml's `done` — the parent's card is "
              "NOT rewritten on a shipped feature",
              r.returncode == 0 and not parent_editsT7,
              f"exit {r.returncode}; parent edits={parent_editsT7}")

    with tempfile.TemporaryDirectory() as tmpT7b:
        # NEGATIVE CONTROL: same shape, a LIVE station. The exemption must NOT fire, or the case
        # above passes on a repointing that exempts every feature and stops writing parents at all.
        install_gh(tmpT7b, FAKE_GH_STATIONS)
        featT7b = stage_station(
            tmpT7b, "FEAT-81-live-from-plan",
            [("T-01", "done"), ("T-02", "building")],
            issues={"T-01": 41, "T-02": 42}, parent=40,
            feature_status=None, plan_station="building",
        )
        r = run(["start-task", featT7b, "T-02"], tmpT7b, {"FACTORY_GH": os.path.join(tmpT7b, "gh")})
        parent_editsT7b = [l for l in calls(tmpT7b) if "project item-edit" in l]
        check("T-07 NEGATIVE CONTROL: a live plan.yaml station does NOT exempt — the parent rule "
              "still runs and writes",
              r.returncode == 0 and parent_editsT7b,
              f"exit {r.returncode}; edits={parent_editsT7b}")

    # ---------- T-04 (BUG-1309): start-task's Build-entry preflight ----------
    # A feature with no receipt is refused and pointed at the subcommand that would mint one —
    # `open` for a plan still in flight, `recover-terminal` for one whose stations are already
    # done — unless its name is in the era-exempt set, which continues with a warning.
    with tempfile.TemporaryDirectory() as tmpT04:
        install_gh(tmpT04, FAKE_GH_STATIONS)
        feat = stage_station(tmpT04, "FEAT-9001-fixture-non-era", [("T-01", "ready")],
                             issues={"T-01": 41})
        _without_build_entry(feat)
        result = run(["start-task", feat, "T-01"], tmpT04, {"FACTORY_GH": os.path.join(tmpT04, "gh")})
        check("T-04 non-era absent refuses", result.returncode == 2 and "gh-sync.py open" in result.stdout,
              result.stdout)
        bug = stage_station(tmpT04, "BUG-9001-fixture-non-era", [("T-01", "ready")],
                            issues={"T-01": 42})
        _without_build_entry(bug)
        result = run(["start-task", bug, "T-01"], tmpT04, {"FACTORY_GH": os.path.join(tmpT04, "gh")})
        check("T-04 BUG-named non-era absent refuses", result.returncode == 2 and "gh-sync.py open" in result.stdout,
              result.stdout)
        write_plan_yaml(feat, "FEAT-9001-fixture-non-era", [("T-01", "done")])
        result = run(["start-task", feat, "T-01"], tmpT04, {"FACTORY_GH": os.path.join(tmpT04, "gh")})
        check("T-04 station discriminator", result.returncode == 2 and "recover-terminal" in result.stdout
              and "open" not in result.stdout.lower(), result.stdout)
        recovery = stage_station(tmpT04, "FEAT-9002-fixture-recovery-terminal", [("T-01", "done")],
                                 issues={"T-01": 44})
        recovery_document = read_feature_json(os.path.join(recovery, "feature.json"))
        recovery_document["github"]["build_entry"] = "recovery-required"
        write_feature_json(os.path.join(recovery, "feature.json"),
                           feature_id=recovery_document["feature_id"],
                           github=recovery_document["github"])
        expected_command = feature_schema.recovery_command_for(recovery)
        result = run(["start-task", recovery, "T-01"], tmpT04,
                     {"FACTORY_GH": os.path.join(tmpT04, "gh")})
        check("T-04 recovery-required non-era recover-terminal horn names the derived command",
              result.returncode == 0 and expected_command == "recover-terminal"
              and expected_command in result.stderr and " --yes" in result.stderr
              and "open" not in result.stderr.lower(),
              result.stderr)
        era = stage_station(tmpT04, "BUG-1030-stale-anchor-write-hazard", [("T-01", "ready")],
                            issues={"T-01": 43})
        _without_build_entry(era)
        result = run(["start-task", era, "T-01"], tmpT04, {"FACTORY_GH": os.path.join(tmpT04, "gh")})
        check("T-04 era-exempt continues", result.returncode == 0 and "predates" in result.stderr, result.stderr)
        result = run(["start-task", era + "/", "T-01"], tmpT04,
                     {"FACTORY_GH": os.path.join(tmpT04, "gh")})
        check("T-12 era-exempt trailing slash continues", result.returncode == 0
              and "predates" in result.stderr, result.stderr)
        document = read_feature_json(os.path.join(era, "feature.json"))
        document["github"]["build_entry"] = "recovery-required"
        write_feature_json(os.path.join(era, "feature.json"), feature_id=document["feature_id"], github=document["github"])
        result = run(["start-task", era, "T-01"], tmpT04, {"FACTORY_GH": os.path.join(tmpT04, "gh")})
        check("T-04 era recovery-required does not claim a refusal", result.returncode == 0
              and "is not refused" in result.stderr and "open" not in result.stderr.lower(), result.stderr)

    # =============================================================================================
    # BUG-201 (D-05, REQ-05): the two swallowing consumers' failing diagnosis cases (T-05).
    # T-06 (a separate, later dispatch) fixes _projected_for and _status_plan_doc's swallowed
    # cause; until then case (d) below is RED.
    # =============================================================================================

    _DANGLING_FEAT = "FEAT-201-dangling"

    _LEGAL_FEAT = "FEAT-201-legal"

    with tempfile.TemporaryDirectory() as tmpD0:
        _dangling_dir = os.path.join(tmpD0, ".harness", "features", _DANGLING_FEAT)
        os.makedirs(_dangling_dir)
        write_dangling_plan_yaml(_dangling_dir, _DANGLING_FEAT, "T-99",
                                  approval={"status": "pending"}, plan_station="plan")
        _legal_dir = os.path.join(tmpD0, ".harness", "features", _LEGAL_FEAT)
        os.makedirs(_legal_dir)
        write_dangling_plan_yaml(_legal_dir, _LEGAL_FEAT, "T-01",
                                  approval={"status": "pending"}, plan_station="plan")
        try:
            harness_yaml.load_plan(os.path.join(_dangling_dir, "plan.yaml"))
            check("(D0) load_plan RAISES on the dangling fixture (T-02 depends_on T-99, absent)",
                  False, "load_plan returned instead of raising")
        except harness_yaml.PlanSchemaError as exc:
            check("(D0) load_plan RAISES on the dangling fixture (T-02 depends_on T-99, absent)",
                  "T-02" in str(exc) and "T-99" in str(exc), str(exc))
        try:
            _legal_doc0 = harness_yaml.load_plan(os.path.join(_legal_dir, "plan.yaml"))
            check("(D0) load_plan RETURNS on the paired legal fixture (T-02 depends_on T-01, "
                  "present)", isinstance(_legal_doc0, dict), _legal_doc0)
        except Exception as exc:
            check("(D0) load_plan RETURNS on the paired legal fixture (T-02 depends_on T-01, "
                  "present)", False, repr(exc))

    # (d) _projected_for REFUSES. start-task over the dangling fixture, a board configured, the
    # shape this file's own start-task cases already stage through stage_station — exit status
    # EXACTLY 2, one stderr line naming BOTH T-02 and T-99, no "Traceback" anywhere in the output.
    # NEVER status Ready here (T-05 intent): status Ready's approval guard refuses at exit 2 on its
    # own, so it cannot discriminate a fix that leaves _projected_for still returning {}.
    with tempfile.TemporaryDirectory() as tmpDd:
        install_gh(tmpDd, FAKE_GH_STATIONS)
        featDd = stage_depends_on(tmpDd, "FEAT-201-d", "T-99", issues={"T-02": 5501}, parent=40)
        rDd = run(["start-task", featDd, "T-02"], tmpDd, {"FACTORY_GH": os.path.join(tmpDd, "gh")})
        bothDd = rDd.stdout + rDd.stderr
        linesDd = [l for l in bothDd.splitlines() if l.strip()]
        check("(d) start-task over the dangling fixture: exit status EXACTLY 2",
              rDd.returncode == 2, bothDd)
        check("(d) exactly one stderr line names BOTH T-02 and T-99",
              sum(1 for l in rDd.stderr.splitlines() if "T-02" in l and "T-99" in l) == 1,
              rDd.stderr)
        check("(d) no Traceback anywhere in the output", "Traceback" not in bothDd, bothDd)

    # (e) THE PAIRED ALLOW for (d): the same start-task invocation over the legal fixture behaves
    # as it does today — mirrors this file's own plain start-task success case (featN): exits 0
    # and writes T-02's OWN sub-issue card to Building.
    with tempfile.TemporaryDirectory() as tmpDe:
        install_gh(tmpDe, FAKE_GH_STATIONS)
        featDe = stage_depends_on(tmpDe, "FEAT-201-e", "T-01", issues={"T-01": 5601, "T-02": 5602},
                                   parent=40)
        rDe = run(["start-task", featDe, "T-02"], tmpDe, {"FACTORY_GH": os.path.join(tmpDe, "gh")})
        editsDe = [l for l in calls(tmpDe) if "project item-edit" in l]
        check("(e) start-task over the legal fixture: exits 0, exactly as today",
              rDe.returncode == 0, rDe.stdout + rDe.stderr)
        check("(e) start-task sets T-02's OWN issue station to Building, exactly as today",
              any("--id ITEM_5602" in l and "--single-select-option-id OPT_BUILDING" in l
                  for l in editsDe),
              str(editsDe))

    # (f) _status_plan_doc DIAGNOSES WITHOUT GATING. `status <dangling> Ready` — today the ready
    # guard refuses at exit 2 with "station ready refused" because approval reads as absent
    # (approval.status is "pending", never "approved"). That pair is captured here FIRST, then the
    # new diagnostic line must be ADDITIVE to it — never a replacement, never a second exit code.
    with tempfile.TemporaryDirectory() as tmpDf:
        install_gh(tmpDf, FAKE_GH_STATIONS)
        featDf = stage_depends_on(tmpDf, "FEAT-201-f", "T-99", issues={"T-02": 5701}, parent=40)
        rDf = run(["status", featDf, "ready"], tmpDf, {"FACTORY_GH": os.path.join(tmpDf, "gh")})
        bothDf = rDf.stdout + rDf.stderr
        check("(f) status Ready over the dangling fixture: exit status UNCHANGED from today (2)",
              rDf.returncode == 2, bothDf)
        check("(f) the existing refusal line is UNCHANGED from today (captured pair, additive)",
              "station ready refused" in bothDf, bothDf)
        check("(f) stderr ALSO carries a line naming BOTH T-02 and T-99, additive to the above",
              any("T-02" in l and "T-99" in l for l in rDf.stderr.splitlines()), rDf.stderr)

    # (g) THE PAIRED ALLOW for (f): the same guarded transition (status Ready) over the legal
    # fixture, approval APPROVED, proceeds exactly as this file's own featSt2 case asserts — exits
    # 0 and writes every recorded sub-issue's card to Ready.
    with tempfile.TemporaryDirectory() as tmpDg:
        install_gh(tmpDg, FAKE_GH_STATIONS)
        featDg = stage_depends_on(tmpDg, "FEAT-201-g", "T-01", issues={"T-01": 5801, "T-02": 5802},
                                   parent=40, approval={"status": "approved"})
        rDg = run(["status", featDg, "ready"], tmpDg, {"FACTORY_GH": os.path.join(tmpDg, "gh")})
        editsDg = [l for l in calls(tmpDg) if "project item-edit" in l]
        idsDg = {next(p for p in l.split() if p.startswith("ITEM_")) for l in editsDg}
        check("(g) status Ready over the legal fixture: exits 0, exactly as today",
              rDg.returncode == 0, rDg.stdout + rDg.stderr)
        check("(g) status Ready over the legal fixture: both recorded sub-issues moved to Ready",
              idsDg == {"ITEM_5801", "ITEM_5802"}
              and all("OPT_READY" in l for l in editsDg),
              str(editsDg))

    # ---------------------------------------------------------------------------------------------
    # BUG-201 SIMPLIFY fold-in: refuse() grows an optional runtime-selected `stream` (default
    # unchanged — stdout), and _projected_for's inline "print to stderr, then sys.exit(2)" for a
    # plan that fails to load is replaced by refuse(msg, stream=sys.stderr). This section asserts
    # refuse()'s own contract directly (unit-level, via the already-imported _ghs module) so the
    # altitude fold-in cannot silently flip which stream either call writes to.
    # ---------------------------------------------------------------------------------------------

    def _call_refuse(msg, **kwargs):
        """Invoke _ghs.refuse and report what happened without ever letting an unexpected raise
        (a TypeError from an as-yet-unsupported kwarg, say) abort the rest of this suite (P-04)."""
        try:
            _ghs.refuse(msg, **kwargs)
            return ("returned", None)
        except SystemExit as exc:
            return ("exit", exc.code)
        except TypeError as exc:
            return ("typeerror", str(exc))

    _ro, _re = io.StringIO(), io.StringIO()

    with contextlib.redirect_stdout(_ro), contextlib.redirect_stderr(_re):
        _outcome_default = _call_refuse("default stream unchanged")

    check("refuse() default: still exits 2, unaffected by the new parameter",
          _outcome_default == ("exit", 2), _outcome_default)

    check("refuse() default: message on stdout, exactly as before",
          "gh-sync: REFUSED — default stream unchanged" in _ro.getvalue(), _ro.getvalue())

    check("refuse() default: nothing written to stderr",
          _re.getvalue() == "", _re.getvalue())

    _rso, _rse = io.StringIO(), io.StringIO()

    with contextlib.redirect_stdout(_rso), contextlib.redirect_stderr(_rse):
        _outcome_stream = _call_refuse("stderr routed", stream=sys.stderr)

    check("refuse(stream=sys.stderr): exits 2",
          _outcome_stream == ("exit", 2), _outcome_stream)

    check("refuse(stream=sys.stderr): message on stderr, not stdout",
          "gh-sync: REFUSED — stderr routed" in _rse.getvalue() and _rso.getvalue() == "",
          (_rso.getvalue(), _rse.getvalue()))
    return report()


if __name__ == "__main__":
    sys.exit(main())
