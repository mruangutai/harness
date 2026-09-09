#!/usr/bin/env python3
"""`gh-sync.py abandon`: what it closes, what it labels, what it detaches, where the
cards land, and the terminal station it records.

Split out of test-gh-sync.py (issue #1527); the cases, their assertions and their
subprocess invocations are unchanged. Shared fixtures live in gh_sync_support.py.

    ./test-gh-sync-abandon.py    -> exit 0 all pass, 1 otherwise
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
import sys
import tempfile

from gh_sync_support import (
    FAKE_GH, FAKE_GH_SHIP, FAKE_GH_STATIONS, add_plan_station, calls, check, edits_to,
    install_gh, read_feature_json, read_plan_station, report, run, ship_env, stage, stage_ship,
    stage_station, write_feature_json)


def main():
    # `issue edit ... --add-label` fails, and NOTHING ELSE does. The one write in `abandon` that is
    # purely cosmetic is the one made to fail, because that is the whole shape of the defect: a
    # cosmetic failure used to abort the run through `gh()`'s `skip()`, taking the backlog write,
    # the rest of the batch and the status write down with it.
    FAKE_GH_STATIONS_LABEL_FAILS = FAKE_GH_STATIONS.replace(
        'case "$1 $2" in',
        'case "$*" in\n'
        '  *"--add-label"*) echo "label service unavailable" >&2; exit 1 ;;\n'
        'esac\n'
        'case "$1 $2" in',
        1,
    )

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
        r = run(["abandon", featA, "--reason-file", reasonA, "--yes"], tmpA)
        logA = calls(tmpA)
        patchedA = [l for l in logA if "api -X PATCH" in l and "issues/" in l and "state_reason=not_planned" in l]
        check("abandon closes 3 subs not_planned",
              r.returncode == 0
              and {re.search(r"issues/(\d+)", l).group(1) for l in patchedA}
                  == {"41", "42", "43", "40"},
              str(logA))
        check("abandon closes the milestone",
              any("milestones/7" in l and "state=closed" in l for l in logA), str(logA))
        check("abandon posts via --body-file",
              any(l.startswith("issue comment 40") and "--body-file" in l and reasonA in l for l in logA)
              and not any("budget cut" in l for l in logA),
              str(logA))
        # REVERSED BY T-05. This read "abandon leaves an adopted parent open". Under DEC-203 the
        # parent closes whatever its history: the operator's --yes is what replaces the origin
        # gate, and it is a better guard because a human read the list first.
        check("abandon closes an ADOPTED parent not_planned — origin decides nothing now",
              any(re.search(r"\bissues/40\b", l) and "state_reason=not_planned" in l
                  for l in logA),
              str(logA))
        # T-08: each recorded sub-issue gets its OWN assertion — a fixture where one issue is
        # missed must still fail, so no count-only check over the three lines below.
        check("abandon labels sub-issue #41 abandoned",
              any(l.startswith("issue edit 41") and "--repo implentio/fake" in l
                  and "--add-label abandoned" in l for l in logA),
              str(logA))
        check("abandon labels sub-issue #42 abandoned",
              any(l.startswith("issue edit 42") and "--repo implentio/fake" in l
                  and "--add-label abandoned" in l for l in logA),
              str(logA))
        check("abandon labels sub-issue #43 abandoned",
              any(l.startswith("issue edit 43") and "--repo implentio/fake" in l
                  and "--add-label abandoned" in l for l in logA),
              str(logA))
        # REVERSED BY T-05, with the clause above. An adopted parent now closes, so it is
        # labelled like every other issue this run closed.
        check("abandon labels the adopted parent it closed",
              any(l.startswith("issue edit 40") and "--add-label abandoned" in l for l in logA),
              str(logA))
        check("ensure_labels sends colour b60205 for the abandoned label",
              any(l.startswith("label create abandoned") and "--color b60205" in l for l in logA),
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
        r = run(["abandon", featB, "--reason-file", reasonB, "--yes"], tmpB)
        logB = calls(tmpB)
        # NARROWED: `issues/40` now also matches the DETACH call
        # (api -X DELETE repos/.../issues/40/sub_issue), so a bare substring filter counts two.
        # The assertion is about the CLOSE, so it selects the close.
        parent40_calls = [l for l in logB if re.search(r"\bissues/40 ", l) and "state=closed" in l]
        check("abandon closes the parent not_planned, exactly once",
              r.returncode == 0
              and len(parent40_calls) == 1
              and "state_reason=not_planned" in parent40_calls[0]
              and not any(l.startswith("issue close 40") for l in logB),
              str(logB))
        # T-08: the sub-issue and the created parent each get their own assertion.
        check("abandon labels sub-issue #41 abandoned",
              any(l.startswith("issue edit 41") and "--repo implentio/fake" in l
                  and "--add-label abandoned" in l for l in logB),
              str(logB))
        check("abandon labels a created parent that closes",
              any(l.startswith("issue edit 40") and "--repo implentio/fake" in l
                  and "--add-label abandoned" in l for l in logB),
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
        r = run(["abandon", featC, "--reason-file", reasonC, "--yes"], tmpC)
        logC = calls(tmpC)
        docC = read_feature_json(os.path.join(featC, "feature.json"))
        ghC = docC.get("github") or {}
        # REVERSED BY T-05. This read "abandon leaves a parent with no recorded origin open" —
        # the default that left #728 open with all thirteen of its children finished, because both
        # of the two most recent features recorded their parent by hand and the key read null.
        check("abandon closes a parent that carries no origin at all — the leave-open default is "
              "gone, and the key is still absent from the saved block",
              r.returncode == 0
              and any(re.search(r"\bissues/40\b", l) and "state_reason=not_planned" in l
                      for l in logC)
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
        add_plan_station(featE, "FEAT-06-abandon-nomilestone")
        write_feature_json(
            os.path.join(featE, "feature.json"),
            feature_id="FEAT-06-abandon-nomilestone",
            status="Review",
            github={"milestone": None, "parent": None, "attached": [], "issues": {"T-01": 41}},
        )
        reasonE = os.path.join(tmpE, "reason.txt")
        open(reasonE, "w").write("no milestone was ever recorded")
        r = run(["abandon", featE, "--reason-file", reasonE, "--yes"], tmpE)
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
        check("abandon with no milestone but WITH issues still records the terminal station",
              read_plan_station(featE) == "abandoned", read_plan_station(featE))

    # --- abandon: sync disabled is still a SKIP, exit 0 (SC-12)
    with tempfile.TemporaryDirectory() as tmpF:
        install_gh(tmpF)
        featF = stage(tmpF, feat_name="FEAT-06-abandon-skip")
        json.dump({"github": {"sync": False}}, open(os.path.join(tmpF, ".harness", "harness.json"), "w"))
        reasonF = os.path.join(tmpF, "reason.txt")
        open(reasonF, "w").write("does not matter, sync is off")
        r = run(["abandon", featF, "--reason-file", reasonF, "--yes"], tmpF)
        check("abandon with sync disabled -> SKIP, exit 0", r.returncode == 0 and "SKIP" in r.stdout, r.stdout)

    # ---- T-01 (FEAT-23): ship and abandon record feature.json's own terminal status ---------
    # The fixture is SCHEMA-VALID AND FULLY POPULATED — all eight feature-schema.json required
    # keys plus a github block — so the key-survival case below quantifies over the real key
    # set instead of passing vacuously against a two-key fixture.
    def _full_fixture(path, feat_name, status, issue_num):
        """A schema-complete feature.json PLUS the sibling plan.yaml that now records the station
        (FEAT-41 T-07). Both, because ship and abandon WRITE the station through
        `plan-merge.py set-feature-station`, which needs a plan on disk to write to — a fixture with
        only a feature.json makes those paths print "absent" and record nothing, which is a
        different case from the one every caller here means."""
        with open(os.path.join(os.path.dirname(path), "plan.yaml"), "w", encoding="utf-8") as f:
            f.write(f"schema: plan/1\nfeature: {feat_name}\nstatus: {str(status).lower()}\n"
                    f"tasks:\n  - id: T-01\n    title: t\n    change_type: logic\n"
                    f"    execution_mode: team\n    files:\n      - a.py\n"
                    f"    verify: |\n      true\n    intent: |\n      x\n    status: done\n")
        write_feature_json(
            path,
            feature_id=feat_name,
            branch=f"feat/{feat_name}",
            pr=None,
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
        check("ship records plan.yaml station done",
              r.returncode == 0 and read_plan_station(featS) == "done",
              f"rc={r.returncode} station={read_plan_station(featS)!r}")

    # --- abandon records feature.json status Abandoned
    with tempfile.TemporaryDirectory() as tmpT:
        install_gh(tmpT)
        featT = stage(tmpT, feat_name="FEAT-23-abandon-status")
        fjT = os.path.join(featT, "feature.json")
        _full_fixture(fjT, "FEAT-23-abandon-status", "Review", 900142)
        reasonT = os.path.join(tmpT, "reason.txt")
        open(reasonT, "w").write("cutting scope")
        r = run(["abandon", featT, "--reason-file", reasonT, "--yes"], tmpT)
        check("abandon records plan.yaml station abandoned",
              r.returncode == 0 and read_plan_station(featT) == "abandoned",
              f"rc={r.returncode} station={read_plan_station(featT)!r}")

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
        r = run(["abandon", featV, "--reason-file", reasonV, "--yes"], tmpV)
        after_docV = read_feature_json(fjV)
        other_keys_V = [k for k in before_docV if k != "status"]
        check("abandon leaves every other top-level key unchanged",
              r.returncode == 0
              and all(after_docV.get(k) == before_docV.get(k) for k in other_keys_V)
              and set(after_docV.keys()) == set(before_docV.keys()),
              f"before={before_docV} after={after_docV}")

    # =============================================================================================
    # T-05 — abandon REPORTS AND ASKS, and the parent's origin is no longer recorded anywhere.
    # =============================================================================================

    def _abandon_fixture(tmp, name="FEAT-40-abandon", parent=40, issues=None, milestone=7):
        install_gh(tmp, FAKE_GH)
        feat = stage(tmp, feat_name=name)
        add_plan_station(feat, name, "review")
        write_feature_json(
            os.path.join(feat, "feature.json"), feature_id=name,
            github={"milestone": milestone, "parent": parent,
                    "attached": list((issues or {"T-01": 41, "T-02": 42}).keys()),
                    "issues": issues or {"T-01": 41, "T-02": 42}},
        )
        reason = os.path.join(tmp, "reason.txt")
        open(reason, "w").write("the operator's signed reason")
        return feat, reason

    # --- without --yes: it makes NO write at all ---------------------------------------------------
    with tempfile.TemporaryDirectory() as tmpA1:
        featA1, reasonA1 = _abandon_fixture(tmpA1)
        r = run(["abandon", featA1, "--reason-file", reasonA1], tmpA1)
        logA1 = calls(tmpA1)
        wouldA1 = [l for l in r.stdout.splitlines() if l.startswith("gh-sync: would ")]
        check("abandon dry run: exits 0", r.returncode == 0, r.stdout + r.stderr)
        # `load_config` runs `gh auth status` as a precondition before ANY subcommand, so the log
        # is not expected to be empty. The discriminating assertion is that no WRITE was attempted
        # -- an empty-log assertion would also pass if the fixture were broken.
        _writesA1 = [l for l in logA1
                     if "state=closed" in l or l.startswith("issue edit ")
                     or l.startswith("issue comment ") or l.startswith("issue close ")
                     or l.startswith("label create ")]
        check("abandon dry run: makes ZERO writes - no close, no label, no comment",
              _writesA1 == [], str(logA1))
        check("abandon dry run: one would-line per recorded sub-issue",
              sum(1 for l in wouldA1 if "issue #41" in l) == 1
              and sum(1 for l in wouldA1 if "issue #42" in l) == 1,
              repr(wouldA1))
        check("abandon dry run: the sub-issue line names all four acts — detach, close, label, "
              "and the return to the backlog — so the dry run and the real run diff by eye",
              all(w in next(l for l in wouldA1 if "issue #41" in l)
                  for w in ("detach", "parent #40", "not_planned", "abandoned", "backlog")),
              repr(wouldA1))
        check("abandon dry run: the parent line says it returns to the backlog too",
              any("parent #40" in l and "backlog" in l and "not_planned" in l for l in wouldA1),
              repr(wouldA1))
        check("abandon dry run: one would-line for the milestone",
              sum(1 for l in wouldA1 if "close milestone #7" in l) == 1, repr(wouldA1))
        check("abandon dry run: the parent is LABELLED as the parent, never as one more number - "
              "it now closes unconditionally, so a column of numbers would hide the epic",
              any("close parent #40" in l for l in wouldA1), repr(wouldA1))
        check("abandon dry run: it says what the operator must do next",
              "re-run with --yes" in r.stdout, repr(r.stdout))
        check("abandon dry run: does NOT record the status",
              read_plan_station(featA1) != "abandoned",
              read_feature_json(os.path.join(featA1, "feature.json")))

    # --- with --yes: it closes exactly what the dry run listed, in that order ------------------------
    with tempfile.TemporaryDirectory() as tmpA2:
        featA2, reasonA2 = _abandon_fixture(tmpA2)
        dry = run(["abandon", featA2, "--reason-file", reasonA2], tmpA2)
        dry_numbers = [int(m.group(1)) for m in
                        (re.search(r"#(\d+)", l) for l in dry.stdout.splitlines()
                         if l.startswith("gh-sync: would "))
                        if m]

    with tempfile.TemporaryDirectory() as tmpA3:
        featA3, reasonA3 = _abandon_fixture(tmpA3)
        r = run(["abandon", featA3, "--reason-file", reasonA3, "--yes"], tmpA3)
        logA3 = calls(tmpA3)
        real_numbers = []
        for l in logA3:
            m = re.search(r"issues/(\d+) -f state=closed", l) or \
                re.search(r"milestones/(\d+) -f state=closed", l) or \
                re.search(r"^issue comment (\d+) ", l)
            if m:
                real_numbers.append(int(m.group(1)))
        check("abandon --yes: the numbers it actually closes, in order, equal the numbers the dry "
              "run listed - ONE renderer, so the operator confirms the list that executes",
              real_numbers == dry_numbers,
              "dry=%s real=%s log=%s" % (dry_numbers, real_numbers, logA3))
        check("abandon --yes: every sub-issue is closed not_planned",
              all(any("issues/%d" % n in l and "state_reason=not_planned" in l for l in logA3)
                  for n in (41, 42)), str(logA3))
        check("abandon --yes: the PARENT is closed not_planned whatever its history - the "
              "confirmation replaces the old origin gate",
              any("issues/40" in l and "state_reason=not_planned" in l for l in logA3), str(logA3))
        check("abandon --yes: everything it closed is labelled abandoned, parent included",
              all(any(l.startswith("issue edit %d " % n) and "abandoned" in l for l in logA3)
                  for n in (41, 42, 40)), str(logA3))
        check("abandon --yes: the milestone is closed",
              any("milestones/7" in l and "state=closed" in l for l in logA3), str(logA3))
        check("abandon --yes: records the terminal station in plan.yaml",
              read_plan_station(featA3) == "abandoned", read_plan_station(featA3))

    # --- --yes BEFORE the directory behaves identically to --yes after it ----------------------------
    # Without the name-search strip in main(), `abandon --yes <dir>` reads --yes as the feature
    # directory and dies "--yes is not a directory" -- at exactly the moment the operator is being
    # careful about a destructive command.
    with tempfile.TemporaryDirectory() as tmpA4:
        featA4, reasonA4 = _abandon_fixture(tmpA4)
        r = run(["abandon", "--yes", featA4, "--reason-file", reasonA4], tmpA4)
        docA4 = read_feature_json(os.path.join(featA4, "feature.json"))
        stationA4 = read_plan_station(featA4)
        check("abandon --yes BEFORE the directory: does not die with 'is not a directory'",
              "is not a directory" not in (r.stdout + r.stderr), r.stdout + r.stderr)
        check("abandon --yes BEFORE the directory: behaves identically - status recorded, parent "
              "closed",
              r.returncode == 0 and stationA4 == "abandoned"
              and any("issues/40" in l and "state_reason=not_planned" in l for l in calls(tmpA4)),
              "rc=%s station=%s" % (r.returncode, stationA4))

    # --- --yes on any other subcommand is a CALLER ERROR ----------------------------------------------
    with tempfile.TemporaryDirectory() as tmpA5:
        featA5, _reasonA5 = _abandon_fixture(tmpA5, name="FEAT-40-yes-on-ship")
        r = run(["ship", featA5, "--yes"], tmpA5)
        check("--yes on ship exits 1 with a caller-error message naming the subcommand - a flag "
              "that silently does nothing teaches the operator it is harmless everywhere",
              r.returncode == 1 and "--yes" in (r.stdout + r.stderr)
              and "abandon" in (r.stdout + r.stderr), "rc=%s %r" % (r.returncode, r.stderr))
        check("--yes on ship makes no gh call at all", calls(tmpA5) == [], str(calls(tmpA5)))

    # --- a github block still carrying the old origin key is read, and never written back --------------
    with tempfile.TemporaryDirectory() as tmpA6:
        install_gh(tmpA6, FAKE_GH)
        featA6 = stage(tmpA6, feat_name="FEAT-40-legacy-key")
        fjA6 = os.path.join(featA6, "feature.json")
        # Written by hand, bypassing write_feature_json, because the schema no longer allows the
        # key: this is what every feature on disk looked like before this task.
        json.dump({"feature_id": "FEAT-40-legacy-key", "branch": None, "pr": None,
                   "status": "Review", "review_sha": None, "cycles_used": 0,
                   "max_total_cycles": 10, "runs": [],
                   "github": {"milestone": 7, "parent": 40, "parent_origin": "adopted",
                              "attached": ["T-01"], "issues": {"T-01": 41}}},
                  open(fjA6, "w"), indent=2)
        reasonA6 = os.path.join(tmpA6, "reason.txt")
        open(reasonA6, "w").write("legacy reason")
        r = run(["abandon", featA6, "--reason-file", reasonA6, "--yes"], tmpA6)
        ghA6 = (read_feature_json(fjA6).get("github") or {})
        check("legacy origin key: abandon reads the block without crashing",
              r.returncode == 0, r.stdout + r.stderr)
        check("legacy origin key: the parent closes anyway - the key is read but decides nothing",
              any("issues/40" in l and "state_reason=not_planned" in l for l in calls(tmpA6)),
              str(calls(tmpA6)))

    # --- abandon with a BOARD: detach, close, label, and back to the BACKLOG ------------------------
    # The operator's correction of 2026-08-25. Measured the same day on probe #860: closing an issue
    # moves its card to the done station at t+0s, not_planned included. So before this, every
    # abandoned ticket landed at Done and the board could not tell dropped work from shipped work.
    with tempfile.TemporaryDirectory() as tmpAB:
        install_gh(tmpAB, FAKE_GH_SHIP)
        featAB = stage_ship(tmpAB, "FEAT-40-abandon-backlog", {"T-01": 41, "T-02": 42}, parent=40)
        reasonAB = os.path.join(tmpAB, "reason.txt")
        open(reasonAB, "w").write("dropped")
        r = run(["abandon", featAB, "--reason-file", reasonAB, "--yes"], tmpAB,
                ship_env(tmpAB, "40=Review 41=Review 42=Review"))
        logAB = calls(tmpAB)
        backlogAB = set()
        for l in edits_to(logAB, "OPT_BACKLOG"):
            m = re.search(r"--id ITEM_(\d+)", l)
            if m:
                backlogAB.add(int(m.group(1)))
        check("abandon: exits 0 with a board configured", r.returncode == 0, r.stdout + r.stderr)
        for numAB in (41, 42, 40):
            check("abandon: card #%d is returned to the BACKLOG station, not left at Done" % numAB,
                  numAB in backlogAB, "backlog=%s stdout=%r" % (sorted(backlogAB), r.stdout))
        check("abandon: NO card is written to the done station",
              not edits_to(logAB, "OPT_DONE"), str(logAB))

        # THE ORDER IS THE WHOLE POINT. A backlog write made BEFORE the close is overwritten by
        # GitHub's own workflow, silently. Measured on #860: a write AFTER the close sticks.
        close41 = next(i for i, l in enumerate(logAB)
                       if "issues/41 " in l and "state=closed" in l)
        backlog41 = next(i for i, l in enumerate(logAB)
                         if "item-edit" in l and "ITEM_41" in l and "OPT_BACKLOG" in l)
        check("abandon: the backlog write comes AFTER the close — a write before it would be "
              "overwritten by GitHub's Item-closed workflow",
              backlog41 > close41, "close=%d backlog=%d log=%s" % (close41, backlog41, logAB))

        # DETACH. Under DEC-203 a ticket is open while its card is not at Done, so an abandoned
        # ticket at the backlog reads as OPEN — and ship refuses to move a parent with an open
        # child. Left attached, one abandoned child holds its parent forever, and the Bash gate
        # refuses a hand close, so there is no way out.
        for numAB in (41, 42):
            check("abandon: sub-issue #%d is DETACHED from parent #40, so it cannot hold the "
                  "parent open" % numAB,
                  any("DELETE" in l and "issues/40/sub_issue" in l
                      and "sub_issue_id=9000%d" % numAB in l for l in logAB), str(logAB))
        detach41 = next(i for i, l in enumerate(logAB)
                        if "DELETE" in l and "sub_issue_id=900041" in l)
        check("abandon: the detach comes BEFORE the close — a detach is a write on the parent, "
              "and doing it first means a failed close cannot leave a half-detached child",
              detach41 < close41, "detach=%d close=%d" % (detach41, close41))

        check("abandon: everything it closed still carries the abandoned label",
              all(any(l.startswith("issue edit %d " % n) and "abandoned" in l for l in logAB)
                  for n in (41, 42, 40)), str(logAB))
        check("abandon: still records status Abandoned",
              read_plan_station(featAB) == "abandoned",
              read_feature_json(os.path.join(featAB, "feature.json")))

    # --- a detach that FAILS does not stop the close ------------------------------------------------
    # Best-effort, like every other write here. An attached-but-closed ticket is a worse outcome
    # than a detached one, and far better than not closing it at all.
    with tempfile.TemporaryDirectory() as tmpAC:
        install_gh(tmpAC, FAKE_GH_SHIP)
        featAC = stage_ship(tmpAC, "FEAT-40-detach-fails", {"T-01": 41}, parent=40)
        reasonAC = os.path.join(tmpAC, "reason.txt")
        open(reasonAC, "w").write("dropped")
        r = run(["abandon", featAC, "--reason-file", reasonAC, "--yes"], tmpAC,
                ship_env(tmpAC, "40=Review 41=Review", SHIP_SUBISSUES_FAIL="40"))
        logAC = calls(tmpAC)
        check("abandon: exits 0 even when a detach cannot be made",
              r.returncode == 0, r.stdout + r.stderr)
        check("abandon: the close still runs when the detach fails",
              any("issues/41 " in l and "state=closed" in l for l in logAC), str(logAC))

    # ---------- ABANDON PUTS THE CARD BACK IN THE BACKLOG, AND NOTHING COSMETIC CAN STOP IT ------
    # The operator's ruling: an abandoned ticket is NOT done work. It closes `not_planned`, keeps
    # the `abandoned` label, detaches from its parent, and its card returns to the BACKLOG station.
    # Probe #860 measured why the order is forced: a close moves the card to the done station at
    # t+0s, so the backlog write must come AFTER the close or GitHub overwrites it.

    with tempfile.TemporaryDirectory() as tmpAB:
        install_gh(tmpAB, FAKE_GH_STATIONS)
        featAB = stage_station(tmpAB, "FEAT-40-abandon-backlog",
                               [("T-01", "pending")], issues={"T-01": 41}, parent=40)
        reasonAB = os.path.join(tmpAB, "reason.txt")
        open(reasonAB, "w").write("dropped")
        rAB = run(["abandon", featAB, "--reason-file", reasonAB, "--yes"], tmpAB,
                  {"FACTORY_GH": os.path.join(tmpAB, "gh")})
        logAB = calls(tmpAB)
        editsAB = [l for l in logAB if "project item-edit" in l]
        check("abandon exits 0", rAB.returncode == 0, rAB.stdout + rAB.stderr)
        check("abandon writes BACKLOG for the sub-issue's card, never the done station",
              any("--id ITEM_41" in l and "--single-select-option-id OPT_BACKLOG" in l
                  for l in editsAB)
              and not any("--id ITEM_41" in l and "OPT_DONE" in l for l in editsAB),
              str(editsAB))
        check("abandon writes BACKLOG for the parent's card too",
              any("--id ITEM_40" in l and "--single-select-option-id OPT_BACKLOG" in l
                  for l in editsAB),
              str(editsAB))
        # ORDERING, asserted by position in the ONE call log rather than by counting: the close
        # must land before the backlog write, or GitHub's own workflow overwrites it.
        _close41 = next((i for i, l in enumerate(logAB)
                         if "api -X PATCH" in l and "issues/41" in l and "not_planned" in l), None)
        _back41 = next((i for i, l in enumerate(logAB)
                        if "project item-edit" in l and "--id ITEM_41" in l
                        and "OPT_BACKLOG" in l), None)
        check("the close precedes the backlog write, because a close moves the card to done at "
              "t+0s and a write made before it would be silently overwritten",
              _close41 is not None and _back41 is not None and _close41 < _back41,
              f"close={_close41} backlog={_back41}")

    with tempfile.TemporaryDirectory() as tmpAC:
        install_gh(tmpAC, FAKE_GH_STATIONS_LABEL_FAILS)
        featAC = stage_station(tmpAC, "FEAT-40-abandon-label-fails",
                               [("T-01", "pending"), ("T-02", "pending")],
                               issues={"T-01": 41, "T-02": 42}, parent=40)
        reasonAC = os.path.join(tmpAC, "reason.txt")
        open(reasonAC, "w").write("dropped")
        rAC = run(["abandon", featAC, "--reason-file", reasonAC, "--yes"], tmpAC,
                  {"FACTORY_GH": os.path.join(tmpAC, "gh")})
        logAC = calls(tmpAC)
        editsAC = [l for l in logAC if "project item-edit" in l]
        patchedAC = {re.search(r"issues/(\d+)", l).group(1) for l in logAC
                     if "api -X PATCH" in l and "issues/" in l and "not_planned" in l}
        check("a failing --add-label does not abort the run — no SKIP, exit 0",
              rAC.returncode == 0 and "gh-sync: SKIP" not in rAC.stdout,
              f"rc={rAC.returncode} stdout={rAC.stdout!r}")
        check("a failing --add-label on the FIRST issue still leaves every later issue closed",
              {"41", "42", "40"} <= patchedAC, sorted(patchedAC))
        check("a failing --add-label still leaves the card in the BACKLOG, never at done — the "
              "cosmetic write cannot cost the state correction",
              any("--id ITEM_41" in l and "OPT_BACKLOG" in l for l in editsAC)
              and not any("OPT_DONE" in l for l in editsAC),
              str(editsAC))
        check("the label failure is REPORTED on stderr, naming the issue",
              "#41" in rAC.stderr and "not labelled" in rAC.stderr, repr(rAC.stderr))
        check("_record_status still runs — feature.json reaches Abandoned",
              read_plan_station(featAC) == "abandoned",
              open(os.path.join(featAC, "feature.json")).read())
    return report()


if __name__ == "__main__":
    sys.exit(main())
