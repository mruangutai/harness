#!/usr/bin/env python3
"""check-state.sh INV-26: the project board must agree with the plan.

Sliced out of tests/integration/test-check-state.py (issue #1527). Cases (v) and (w) —
the board/plan comparison and the ABANDONED terminal state — every `gh` call answered by
a stub on FACTORY_GH, never the network.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import json
import os
import subprocess
import sys
import tempfile
from check_state_support import (HARNESS_JSON_SYNC_OFF, SCRIPT, _root_env, _run_with_gh,
    _run_with_gh_streams)


_SENTINEL = object()


def _inv26_fixture(root, feat, task_status, card_status, parent_status,
                   issues=None, feature_status="Building", second_status=None,
                   second_card=None, factory=None, board_override=_SENTINEL):
    """One INV-26 fixture: harness.json with sync+repo+board, one feature with a plan,
    a feature.json recording issues, and a fake gh whose project item-list page puts
    each card wherever the caller says.

    THE FAKE IS POINTED AT WITH FACTORY_GH, the same variable factory_gh honours, so one
    fake serves both gh_board and the invariant. `gh auth status` must exit 0 through it
    or INV-26 gates out and every assertion below passes vacuously.
    """
    h = os.path.join(root, ".harness")
    fd = os.path.join(h, "harness", "features", feat)
    os.makedirs(fd, exist_ok=True)
    with open(os.path.join(h, "harness.json"), "w") as f:
        # THE FIVE STATIONS ARE REQUIRED NOW (FEAT-24 T-04/T-05). Before this feature the
        # board carried three keys and INV-26 spelled "Building"/"Done"/"Backlog" itself;
        # the names now come from the declaration, so a fixture without `stations` is not a
        # weaker fixture — it is an UNUSABLE board, and case v.13 asserts that it is
        # reported as one. `board_override` lets a case ship a deliberately broken board.
        # The ordered lowercase declaration (FEAT-41 T-01); INV-26 compares stations, not
        # columns, because gh_board.board_stations lowercases the board's answer on read.
        _board = {"owner": "org", "number": 3, "station_field": "status",
                  "stations": ["backlog", "plan", "ready", "building", "review", "done"]}
        if board_override is not _SENTINEL:
            _board = board_override
        json.dump({"github": {"sync": True, "repo": "org/repo",
                              "board": _board}}, f)
    with open(os.path.join(fd, "plan.yaml"), "w") as f:
        # THE FEATURE'S STATION IS A TOP-LEVEL KEY HERE NOW (FEAT-41 T-07), lowercased from the
        # `feature_status` argument every caller already passes. The argument keeps its name so
        # no call site changes; only the file it lands in moved.
        f.write("schema: plan/1\nfeature: %s\nstatus: %s\napproval:\n  status: approved\n"
                "tasks:\n  - id: T-01\n    title: t\n    change_type: logic\n"
                "    execution_mode: team\n    execution_agent: harness-backend-dev\n"
                "    depends_on: []\n"
                "    status: %s\n    files:\n      - a.py\n    verify: |\n      true\n"
                "    intent: |\n      x\n" % (feat, str(feature_status).lower(), task_status))
        # A SECOND TASK, so a fixture can sit BETWEEN two statuses. Every case before
        # this parameter was single-task, which is exactly why the suite stayed green
        # while a mixed plan silenced the whole invariant.
        if second_status is not None:
            f.write("  - id: T-02\n    title: t2\n    change_type: logic\n"
                    "    execution_mode: team\n    execution_agent: harness-backend-dev\n"
                    "    depends_on: []\n"
                    "    status: %s\n    files:\n      - b.py\n    verify: |\n      true\n"
                    "    intent: |\n      x\n" % second_status)
    if issues is None:
        issues = {"T-01": 41} if second_status is None else {"T-01": 41, "T-02": 42}
    _doc = {"feature_id": feat, "branch": "b", "pr": None,
            "review_sha": "abc1234",
            "cycles_used": 0, "max_total_cycles": 10, "runs": [],
            "github": {"milestone": 1, "parent": 40, "issues": issues}}
    if factory is not None:
        # A factory-lane feature: published by factory_decompose, so its issues live
        # under `factory`, in a repository fleet.yaml must declare or INV-24 fires
        # instead of the clause under test.
        _doc["factory"] = factory
        os.makedirs(os.path.join(h, "factory"), exist_ok=True)
        with open(os.path.join(h, "factory", "fleet.yaml"), "w") as f:
            f.write("schema: factory-fleet/1\nrepos:\n  - name: %s\n"
                    "workspace_root: %s\n" % (factory["repo"], root))
    with open(os.path.join(fd, "feature.json"), "w") as f:
        json.dump(_doc, f)

    items = [{"content": {"repository": "org/repo", "number": 41}, "status": card_status},
             {"content": {"repository": "org/repo", "number": 40}, "status": parent_status}]
    if second_status is not None:
        items.append({"content": {"repository": "org/repo", "number": 42},
                      "status": second_card if second_card is not None else "Backlog"})
    page = json.dumps({"totalCount": len(items), "items": items})
    # TWO SHAPES, dispatched on the subcommand. FEAT-29 T-02 replaced INV-26's
    # `gh project item-list` read with ONE targeted `gh api graphql` query
    # (factory_gh.project_item_stations). A fake serving only the item-list shape makes that
    # call raise, check-state.sh's bare except swallows it, and INV-26 goes SILENT — every
    # assertion here then passes vacuously, which is issue #588's shape inside the one
    # invariant this fixture exists to test. Six named cases went red on exactly that.
    # The item-list shape is KEPT: it costs nothing and any caller still on the old read
    # keeps working rather than failing in a second, differently-confusing way.
    gql = json.dumps({"data": {"user": {"projectV2": {"items": {
        "totalCount": len(items),
        "nodes": [{"content": {"number": it["content"]["number"],
                               "repository": {"nameWithOwner": it["content"]["repository"]}},
                   "fieldValueByName": ({"name": it["status"]}
                                        if it.get("status") is not None else None)}
                  for it in items],
        "pageInfo": {"hasNextPage": False, "endCursor": None}}}}}})
    fake = os.path.join(root, "fake-gh")
    with open(fake, "w") as f:
        f.write("#!/bin/bash\ncase \"$1 $2\" in\n"
                "  \"auth status\") exit 0 ;;\n"
                "  \"api graphql\") cat <<'GQL'\n" + gql + "\nGQL\n    exit 0 ;;\n"
                "esac\n"
                "cat <<'EOF'\n" + page + "\nEOF\n")
    os.chmod(fake, 0o755)
    return fake


def case_v():
    """INV-26 (issue #277): the board must agree with the plan.

    THE NON-VACUITY PAIR IS THE POINT. v.1 and v.2 differ in the fake page ONLY — one
    card's status and the parent's. If v.1 alone passed, it would be satisfied by an
    invariant that reports a violation for every feature it looks at, which is the same
    blindness facing the other way.
    """
    results = []

    def _lines(out):
        return [l for l in out.splitlines() if "INV-26" in l]

    # --- v.1 THE MIS-COLUMNED FIXTURE: T-01 done, its card in Backlog.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Backlog", "Review")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        # The fixture feeds the BOARD's capitalised "Backlog"; board_stations lowercases it on
        # read, so the reported value is lowercase (FEAT-41 T-02).
        ok = (any("FEAT-X" in l and "T-01" in l and "done" in l and "backlog" in l
                  for l in ls))
        results.append(("(v.1) a mis-columned card is a VIOLATION naming feature, task, "
                        "plan status and column found", ok, "\n".join(ls) or "(no INV-26 line)"))

    # --- v.2 THE CORRECTED TWIN: the SAME fixture, that one card reading Done.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Done", "Review")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        results.append(("(v.2) the corrected twin reports NOTHING", not ls,
                        "\n".join(ls)))

    # --- v.3 the terminal exemption: status Done, every card wrong, silence.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Backlog", "Backlog",
                              feature_status="Done")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        results.append(("(v.3) a feature whose status is Done is exempt even with every "
                        "card wrong", not ls, "\n".join(ls)))

    # --- v.4 the mirror-never-ran clause: a task building, sync on, empty issues map.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "building", "Building", "Building", issues={})
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        ok = any("no mirrored issues" in l for l in ls)
        results.append(("(v.4) tasks in flight with an EMPTY issues map is a violation",
                        ok, "\n".join(ls) or "(no INV-26 line)"))

    # --- v.5 CANNOT VERIFY: the recorded issue is absent from the board page.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Done", "Review",
                              issues={"T-01": 9999})
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        ok = any("CANNOT VERIFY" in l and "9999" in l and "not on the board" in l
                 for l in ls)
        results.append(("(v.5) a recorded issue absent from the board is CANNOT VERIFY, "
                        "not a clean pass", ok, "\n".join(ls) or "(no INV-26 line)"))

    # --- v.6 the parent mismatch is its own finding.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Done", "Backlog")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        ok = any("parent" in l and "#40" in l and "review" in l and "backlog" in l
                 for l in ls)
        results.append(("(v.6) the parent card disagreeing with the derivation is a "
                        "violation", ok, "\n".join(ls) or "(no INV-26 line)"))

    # --- v.7 gh absent contributes NOTHING. The environment is not the tree.
    with tempfile.TemporaryDirectory() as tmp:
        _inv26_fixture(tmp, "FEAT-X", "done", "Backlog", "Backlog")
        _c, out = _run_with_gh(tmp, os.path.join(tmp, "no-such-gh-binary"))
        ls = _lines(out)
        results.append(("(v.7) a gh binary that does not exist records NO INV-26 finding",
                        not ls, "\n".join(ls)))

    # --- v.8 THE CASE THE INVARIANT WAS BUILT FOR AND COULD NOT SEE.
    # T-01 done with its card still in Backlog, T-02 not started and correctly placed.
    # derive_station returns None for {done, ready}, and the old code skipped the whole
    # feature on None — so SC-05's own scenario went unreported in the ordinary window
    # between two tasks. The per-task comparison never needed the parent derivation.
    #
    # THE SECOND TASK'S CARD MOVED WITH ITS WORD (FEAT-41 T-06, D-11). It was `pending` with a
    # card at Backlog, which was CORRECT under the old exception; the not-started station is
    # `ready` now and its card belongs at Ready, so the fixture says Ready. Leaving it at
    # Backlog would have made this case pass for the wrong reason — on a second, unintended
    # violation rather than on T-01's.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Backlog", "Backlog",
                              second_status="ready", second_card="Ready")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        ok = any("T-01" in l and "done" in l and "backlog" in l for l in ls)
        results.append(("(v.8) a mis-columned done card is reported even when the plan "
                        "derives NO parent station", ok,
                        "\n".join(ls) or "(no INV-26 line)"))

    # --- v.9 THE NON-VACUITY TWIN FOR v.8, and the parent-silence proof in one fixture.
    # Same mixed plan, T-01's card corrected to Done. Nothing must be reported — in
    # particular NOT a parent finding, because a None derivation still has no station to
    # expect and the parent card sits in Backlog here.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Done", "Backlog",
                              second_status="ready", second_card="Ready")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        results.append(("(v.9) the corrected twin of v.8 reports NOTHING, and a None "
                        "derivation raises no parent finding", not ls, "\n".join(ls)))

    # --- v.10 a plan where NOTHING HAS STARTED still claims nothing. The silence that was
    # correct must survive the fix: no task has started, so no card can be wrong yet.
    # The word is `ready` rather than `pending` (FEAT-41 T-04) — the not-started station.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "ready", "Building", "Review",
                              second_status="ready", second_card="Done")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        results.append(("(v.10) a plan where nothing has started reports NOTHING even with "
                        "every card wrong", not ls, "\n".join(ls)))

    # --- v.11/v.12 THE LANE PAIR (issue #349's caveat). The mirror-never-ran clause read
    # only `github.issues`, so a feature published by factory_decompose — issues recorded
    # under `factory.issues`, nothing under `github.issues` — fired a FALSE violation
    # instructing the operator to mirror product work onto harness's board. The pair
    # differs in the factory block alone: v.11 must stay silent, v.12 keeps the teeth.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "building", "Building", "Building",
                              issues={},
                              factory={"repo": "org/prod", "issues": {"T-01": 7}})
        _c, out = _run_with_gh(tmp, fake)
        ls = [l for l in _lines(out) if "no mirrored issues" in l]
        results.append(("(v.11) a factory-published feature (factory.issues recorded, "
                        "github.issues empty) raises NO mirror-never-ran violation",
                        not ls, "\n".join(ls)))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "building", "Building", "Building",
                              issues={},
                              factory={"repo": "org/prod", "issues": {}})
        _c, out = _run_with_gh(tmp, fake)
        ls = [l for l in _lines(out) if "no mirrored issues" in l]
        results.append(("(v.12) the same fixture with an EMPTY factory.issues still "
                        "fires — the exemption keys on recorded issues, not the block",
                        bool(ls), "(no INV-26 line)"))

    # THE OK-LINE TEXT IS THE CONTRACT. T-05's approved verify matches these five with
    # `grep -qxF` — exact, whole line, after the `ok - ` prefix is stripped. Rewording one
    # breaks the gate silently, so the strings below are load-bearing and are not descriptions.

    # --- THE INVERSE OF THE OLD BEHAVIOUR (FEAT-24 T-05). A board present but broken used to
    # make load_board return None, which made INV-26 vacuous and left the gate GREEN. Two
    # SEPARATE properties, asserted separately because the verify wants them separately
    # visible: it is REPORTED, and the gate still COMPLETES. A crashed gate reports no
    # invariant at all, which is a worse silence than the one being fixed.
    _broken = {"owner": "org", "number": 3, "station_field": "status"}
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Backlog", "Review",
                              board_override=_broken)
        c, out, err = _run_with_gh_streams(tmp, fake)
        ls = [l for l in _lines(out) if "CANNOT RUN" in l]
        results.append(("INV-26 reports a violation when the board declaration is unusable",
                        bool(ls) and "stations" in ls[0],
                        "lines=%r" % (ls[:1],)))
        # BOTH STREAMS, and the later invariants too. An abort is not merely a traceback: it
        # is every invariant after INV-26 going unreported, so the case checks that INV-13 —
        # which lives immediately below INV-26 — still ran.
        _tb = "Traceback" in out or "Traceback" in err
        _later_ran = "INV-13" in out or not _tb
        results.append(("INV-26 completes the gate rather than aborting on an unusable board",
                        not _tb and c == 1 and _later_ran,
                        "exit=%s traceback=%s stderr_tail=%r"
                        % (c, _tb, err[-200:])))

    # --- THE NULL TWIN. Not named by the verify, and load-bearing anyway: without it the two
    # cases above are satisfied by an invariant that reports every board it sees, including the
    # one shape that is a deliberate declaration rather than a defect.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Backlog", "Review",
                              board_override=None)
        c, out = _run_with_gh(tmp, fake)
        results.append(("(v.14) an explicit null board records NOTHING — not a violation, "
                        "and no traceback",
                        not _lines(out) and "Traceback" not in out,
                        "\n".join(_lines(out)) or "(unexpected INV-26 line)"))

    # --- T-22 / D-24: THE REVIEW-PHASE WIDENING, AND THE BOUND ON IT.
    # Under D-23 a done task's sub-issue is deliberately left OPEN so it can hold its column
    # through Review. So a done task's card may read done, review OR building — but ONLY while
    # the feature's own feature.json status is Review. All four cases below exist because the
    # accept set has three members and the bound has two sides; three fixtures cannot see a
    # widening that leaked past its bound.
    #
    # THE PLAN ASKED FOR A CASE THAT CANNOT EXIST. Its wording was "the same feature at status
    # Done with the same card is still a VIOLATION". At status Done the TERMINAL EXEMPTION
    # `continue`s before the per-task comparison is ever reached (case v.3 asserts exactly that),
    # so no fixture at status Done can produce an INV-26 station finding at all. The honest test
    # of the bound is a NON-terminal status, so (v.T22b) uses Building.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Review", "Review",
                              feature_status="Review")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        results.append(("(v.T22a) at status Review, a done task's card reading Review is "
                        "ACCEPTED", not ls, "\n".join(ls)))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Building", "Review",
                              feature_status="Review")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        results.append(("(v.T22b) at status Review, a done task's card reading Building is "
                        "ACCEPTED", not ls, "\n".join(ls)))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Review", "Review",
                              feature_status="Building")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        ok = any("FEAT-X" in l and "T-01" in l and "review" in l for l in ls)
        results.append(("(v.T22c) THE BOUND: at status Building, a done task's card reading "
                        "Review is still a VIOLATION", ok,
                        "\n".join(ls) or "(no INV-26 line)"))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Backlog", "Review",
                              feature_status="Review")
        _c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        ok = any("FEAT-X" in l and "T-01" in l and "backlog" in l for l in ls)
        results.append(("(v.T22d) the widening does NOT reach Backlog: a done task's card "
                        "there is a VIOLATION even at status Review", ok,
                        "\n".join(ls) or "(no INV-26 line)"))

    # --- THE RENAMED-BOARD UNIT WAS DELETED HERE BY FEAT-41 T-11 ---------------------------
    # It declared the six columns under six DIFFERENT names and asserted INV-26 read those
    # names out of harness.json. The MANDATE removed the variability it exercised: the six
    # station names are fixed and every read lowercases them, so harness.json can only ever
    # hold those six strings and there is no rename left for a test to cover. Do not restore
    # it.
    #
    # THE RETIRED SPELLINGS ARE DESCRIBED HERE, NEVER QUOTED, and that is a rule this feature
    # learned the hard way — four times, including in the first draft of this very comment.
    # T-11's own verify greps this file for those six words and for the deleted helper's name,
    # so a comment that QUOTES what it retired is indistinguishable from the code that used
    # it, and reds the gate it was written to explain.
    #
    # IT WAS ALSO PASSING VACUOUSLY BY THE TIME IT DIED, measured rather than asserted: a
    # renamed declaration is a MAPPING, the loader refuses one, INV-26 emits CANNOT RUN, and
    # the unit's local helper filtered exactly that line out. Stop filtering CANNOT RUN and
    # all three cases go red while every case below stays green — that run is in T-11's
    # receipt. They tested the filter, not the lookup.
    #
    # The cases that DO cover the mandated vocabulary are T-04's, immediately below, and they
    # carry their own helper for the reason its comment gives.

    # --- FEAT-41 T-04: ONE CASE PER _EXPECT KEY, against the REAL declaration ------------
    # _EXPECT quantifies over three statuses, so a single fixture cannot see a key that was
    # never migrated — a `done` case is blind to a `pending` literal left behind in the `ready`
    # slot. Each key therefore gets a POSITIVE case (correctly placed card, no finding) AND a
    # NEGATIVE control (misplaced card, a finding naming the value), because a positive case
    # alone passes on a build where INV-26 reports nothing at all.
    #
    # ITS OWN HELPER, AND IT IS STRICTER THAN THE ONE IT REPLACES (FEAT-41 T-11). These cases
    # used to borrow a helper from the renamed-board unit deleted above, which filtered
    # CANNOT RUN out of the output — a filter these cases must NOT inherit. They run against
    # the REAL declaration, so CANNOT RUN here would mean the loader had rejected a legal
    # board, and filtering it would turn that into a silent pass. Measured when the unit was
    # deleted: the three renamed cases needed that filter and not one of these does.
    def _clean(out):
        return not _lines(out)

    _t04 = []

    # ready: a MIXED plan. An all-ready plan is skipped outright by the nothing-has-started
    # guard, so the ready card can only be judged beside a started one — which is also the
    # regression the guard rewrite in this task protects: were it still spelled against
    # `pending`, this fixture would stop being skipped and every all-ready feature with it.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Done", "Review",
                              second_status="ready", second_card="Ready")
        c, out = _run_with_gh(tmp, fake)
        _t04.append(("(v.T04-ready) a ready task whose card reads Ready is CLEAN",
                     _clean(out), "\n".join(_lines(out)) or "(unexpected line)"))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Done", "Review",
                              second_status="ready", second_card="Building")
        c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        _t04.append(("(v.T04-ready-neg) a ready task whose card reads Building is a VIOLATION "
                     "naming ready",
                     any("T-02" in l and "ready" in l for l in ls),
                     "\n".join(ls) or "(no INV-26 line)"))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "building", "Building", "Building")
        c, out = _run_with_gh(tmp, fake)
        _t04.append(("(v.T04-building) a building task whose card reads Building is CLEAN",
                     _clean(out), "\n".join(_lines(out)) or "(unexpected line)"))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "building", "Ready", "Building")
        c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        _t04.append(("(v.T04-building-neg) a building task whose card reads Ready is a "
                     "VIOLATION naming building",
                     any("T-01" in l and "building" in l for l in ls),
                     "\n".join(ls) or "(no INV-26 line)"))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Done", "Review")
        c, out = _run_with_gh(tmp, fake)
        _t04.append(("(v.T04-done) a done task whose card reads Done is CLEAN",
                     _clean(out), "\n".join(_lines(out)) or "(unexpected line)"))

    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "done", "Backlog", "Review")
        c, out = _run_with_gh(tmp, fake)
        ls = _lines(out)
        _t04.append(("(v.T04-done-neg) a done task whose card reads Backlog is a VIOLATION "
                     "naming done",
                     any("T-01" in l and "done" in l for l in ls),
                     "\n".join(ls) or "(no INV-26 line)"))

    # `pending` IS NOT A VALUE ANY MORE, AND A PLAN STILL CARRYING ONE IS NOW REPORTED.
    #
    # THIS CASE ASSERTED THE OPPOSITE AT T-04 AND WAS RIGHT TO, WHICH IS WHY IT IS REWRITTEN
    # RATHER THAN DELETED. At T-04 the per-task lookup had no key for `pending`, so the compare
    # SKIPPED it, and this case pinned that skip while pointing at check-plan-routes.py as the
    # thing that refuses the value at plan time. T-06 deletes that skip under D-11: it was the
    # fail-open direction, where an unrecognised station and an exempt one shared a code path.
    #
    # A vocabulary miss is the defect this whole feature exists to end, so it is the ONE case
    # that must not be silent. gh_board.project raises, and INV-26 reports it naming the value.
    # The plan-time refusal still exists and still runs first; this is the second half of the
    # pair, not a replacement for it.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "pending", "Backlog", "Review")
        c, out = _run_with_gh(tmp, fake)
        ls = [l for l in _lines(out) if "pending" in l]
        _t04.append(("(v.T06-pending) a leftover pending task IS reported by INV-26, naming the "
                     "value — the fail-open skip is gone (D-11)",
                     bool(ls), "\n".join(_lines(out)) or "(no INV-26 line at all)"))

    # THE NEGATIVE CONTROL FOR THE CASE ABOVE. Without it, "a line mentioning pending appears"
    # could be satisfied by any unrelated chatter; this proves the legal twin is silent.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "ready", "Ready", "Review")
        c, out = _run_with_gh(tmp, fake)
        _t04.append(("(v.T06-pending-neg) the same fixture at a LEGAL station reports nothing",
                     _clean(out), "\n".join(_lines(out)) or "(unexpected line)"))

    # A RECORDED SUB-ISSUE THAT project DECLINES TO PLACE IS A VIOLATION, NOT A SKIP.
    # The terminal marker names no board column (D-05), so a task carrying it is absent from
    # project's mapping — and absence used to mean "no card to check", which is precisely the
    # fail-open D-11 removes. The line names the station the plan carries so the reader can see
    # WHY nothing could be placed.
    #
    # No live feature hits this today: FEAT-19 and FEAT-28 are the only ones with tasks at the
    # terminal marker and both record zero mirrored sub-issues (measured at T-04). The case is
    # here for the one that eventually does.
    with tempfile.TemporaryDirectory() as tmp:
        fake = _inv26_fixture(tmp, "FEAT-X", "abandoned", "Backlog", "Review")
        c, out = _run_with_gh(tmp, fake)
        ls = [l for l in _lines(out) if "T-01" in l and "abandoned" in l]
        _t04.append(("(v.T06-unplaced) a recorded sub-issue project declines to place is a "
                     "VIOLATION naming the station, not a silent skip",
                     bool(ls), "\n".join(_lines(out)) or "(no INV-26 line at all)"))

    results.extend(_t04)

    allok = True
    for name, ok, detail in results:
        print(f"{'ok' if ok else 'FAIL'} - {name}")
        if not ok and detail:
            print("      " + detail.replace("\n", "\n      "))
        allok = allok and ok
    return allok


def case_w():
    """ABANDONED: the terminal state for a feature planned and never built (2026-08-14).

    THE NON-VACUITY PAIR IS THE POINT. w.1 and w.2 differ in ONE byte-range — the status
    value — and nothing else. An abandoned feature's BRIEF is never approved BY DESIGN, so
    the exemption must silence that violation; but an exemption that silenced it for every
    feature would be the same blindness facing the other way, which w.2 is here to catch.

    FEAT-19 was the first: planned, reviewed through three engineering passes, retired
    unsigned when map #336 superseded its scope. Before this, the enum had no terminal
    state for that, and every one of the 18 features on disk was Done.
    """
    results = []

    def build(status):
        tmp = tempfile.mkdtemp()
        h = os.path.join(tmp, ".harness")
        fd = os.path.join(h, "harness", "features", "FEAT-Z")
        os.makedirs(fd, exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write(HARNESS_JSON_SYNC_OFF)
        with open(os.path.join(h, "team-config.yaml"), "w") as f:
            f.write("agents: {}\n")
        json.dump({"feature_id": "FEAT-Z", "branch": "b", "pr": None,
                   "review_sha": "abc1234",
                   "cycles_used": 0, "max_total_cycles": 10, "runs": []},
                  open(os.path.join(fd, "feature.json"), "w"))
        # The abandoned skip reads plan.yaml's station now (FEAT-41 T-07), so the fixture must
        # carry one — a feature.json status is no longer read by anything.
        with open(os.path.join(fd, "plan.yaml"), "w") as f:
            f.write(f"feature: FEAT-Z\nstatus: {str(status).lower()}\ntasks: []\n")
        with open(os.path.join(fd, "BRIEF.md"), "w") as f:
            f.write("# BRIEF\n\n## Approval\n\nstatus: pending\n")
        return tmp

    def approval_lines(tmp):
        env = _root_env(tmp)
        r = subprocess.run([SCRIPT], cwd=tmp, capture_output=True, text=True, env=env)
        return [l for l in r.stdout.splitlines() if "NOT approved" in l]

    # w.1 ABANDONED: the unapproved brief must NOT be reported.
    ls = approval_lines(build("Abandoned"))
    results.append(("(w.1) an Abandoned feature's unapproved BRIEF raises NOTHING",
                    not ls, "\n".join(ls)))

    # w.2 THE TWIN: same fixture, status Plan. It MUST be reported, or w.1 proves nothing.
    ls = approval_lines(build("Plan"))
    results.append(("(w.2) the same fixture at status Plan IS reported",
                    any("FEAT-Z" in l for l in ls), "\n".join(ls) or "(no line)"))

    allok = True
    for name, ok, detail in results:
        print(f"{'ok' if ok else 'FAIL'} - {name}")
        if not ok and detail:
            print("      " + detail.replace("\n", "\n      "))
        allok = allok and ok
    return allok


def main():
    results = []
    results.append(case_v())
    results.append(case_w())
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
