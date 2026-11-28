#!/usr/bin/env python3
"""`gh-sync.py start-task`: the station writes, the guard that refuses a closed or
already-done card, the parent rule, the board preconditions, and the plan-write
failure -- plus the dangling-plan diagnosis both it and `status` must produce.

Split out of test-gh-sync.py (issue #1527). Shared fixtures live in gh_sync_support.py.

    ./test-gh-sync-start-task.py    -> exit 0 all pass, 1 otherwise
"""
import integration_support  # noqa: F401  (first: puts bin/ and tests/ on sys.path)
import contextlib
import io
import os
import sys
import tempfile

import artifact_accessors
from feature_record import schema as record_schema
import harness_yaml

from gh_sync_support import (
    FAKE_GH_SHIP, FAKE_GH_STATIONS, FAKE_GH_STATIONS_CUSTOM, FAKE_GH_STATIONS_GUARD_READ_FAILS,
    calls, check, install_gh, load_gh_sync, read_feature_json, report, run, ship_env,
    stage_depends_on, stage_ship, stage_station, write_dangling_plan_yaml, write_feature_json,
    write_plan_yaml)


# gh-sync.py's hyphen blocks a plain import; the refuse() cases below assert
# that function's own contract rather than a subcommand's output.
_ghs = load_gh_sync()

BUILDING = "--single-select-option-id OPT_BUILDING"
THREE_TASKS = [("T-01", "done"), ("T-02", "building"), ("T-03", "ready")]


def _set_build_entry(feat, value=None):
    """Rewrite FEAT's feature.json github.build_entry to VALUE; None removes the key."""
    path = os.path.join(feat, "feature.json")
    document = read_feature_json(path)
    if value is None:
        document["github"].pop("build_entry", None)
    else:
        document["github"]["build_entry"] = value
    write_feature_json(path, feature_id=document["feature_id"], github=document["github"])


def _item_edits(tmp):
    """Every `project item-edit` call the fake in TMP logged."""
    return [l for l in calls(tmp) if "project item-edit" in l]


def _wrote(edits, item, opt=BUILDING):
    """Whether one of EDITS set card ITEM (e.g. ITEM_326) with option flag OPT."""
    return any(f"--id {item}" in l and opt in l for l in edits)


def _start_t02(tmp, feat_name, script=FAKE_GH_STATIONS, guard=None, **stage_kw):
    """Stage the three-task feature (T-02 on issue 326, parent 40) and run start-task T-02.
    GUARD is (state, station) for the fake's guard read of issue 326, or None for its default.
    run() binds FACTORY_GH to tmp/gh, the fake installed here (tests/offline_gh_support.py)."""
    install_gh(tmp, script)
    feat = stage_station(tmp, feat_name, THREE_TASKS, issues={"T-01": 41, "T-02": 326},
                         parent=40, **stage_kw)
    env = None
    if guard:
        env = {"GUARD_ISSUE": "326", "GUARD_STATE": guard[0], "GUARD_STATION_NAME": guard[1]}
    return run(["start-task", feat, "T-02"], tmp, env)


def _station_writes():
    # start-task sets the sub-issue's station to Building, then the parent's (D-04) --
    # two field-sets, distinguishable by item id, never by counting calls.
    with tempfile.TemporaryDirectory() as tmp:
        r = _start_t02(tmp, "FEAT-89-start-task")
        edits = _item_edits(tmp)
        check("start-task exits 0", r.returncode == 0, r.stdout + r.stderr)
        check("start-task sets T-02's OWN issue station to Building",
              _wrote(edits, "ITEM_326"), str(edits))
        check("start-task then sets the PARENT's station to Building (distinct item id)",
              _wrote(edits, "ITEM_40"), str(edits))
        check("exactly two field-sets, one per item id",
              len(edits) == 2 and {"ITEM_326", "ITEM_40"} == {
                  next(p for p in l.split() if p.startswith("ITEM_")) for l in edits},
              str(edits))


def _refused(tmp, label, r):
    """The two checks every refused guard case shares: exit 0 and no station write at all."""
    log = calls(tmp)
    check(f"{label}: exits 0", r.returncode == 0, r.stdout + r.stderr)
    check(f"{label}: refused, no station write reaches the fake",
          not any("item-edit" in l for l in log), str(log))


def _guard_closed_done():
    # T-07: start-task must not drive a CLOSED card, or one already at Done, backwards.
    # #642's exact shape: issue closed, card already at Done. Must refuse: no station write of any
    # kind reaches the fake (neither the sub-issue's nor the parent's), and the refusal line prints.
    with tempfile.TemporaryDirectory() as tmp:
        r = _start_t02(tmp, "FEAT-89-start-task-closed-done", guard=("CLOSED", "Done"))
        log = calls(tmp)
        check("#642 replay: exits 0 (a refusal is not a failure, D-02/DEC-146)",
              r.returncode == 0, r.stdout + r.stderr)
        check("#642 replay: no station write of any kind reaches the fake",
              not any("item-edit" in l for l in log), str(log))
        check("#642 replay: refuses, naming the issue, the task id, the current station and why",
              # `done` LOWERCASE (FEAT-41 T-02): the refusal quotes the card's current station as
              # gh_board.board_stations returned it, lowercased at the boundary. The capitalised
              # form would mean the boundary had leaked.
              "gh-sync: refusing #326" in r.stdout and "T-02" in r.stdout and "done" in r.stdout,
              r.stdout)


def _guard_open_backlog():
    # An open issue at Backlog is still moved to Building -- the guard changes nothing for the
    # case it was never meant to touch.
    with tempfile.TemporaryDirectory() as tmp:
        r = _start_t02(tmp, "FEAT-89-start-task-open-backlog", guard=("OPEN", "Backlog"))
        edits = _item_edits(tmp)
        check("open at Backlog: exits 0", r.returncode == 0, r.stdout + r.stderr)
        check("open at Backlog: still writes the sub-issue's station to Building",
              _wrote(edits, "ITEM_326"), str(edits))
        check("open at Backlog: still writes the parent's station too",
              _wrote(edits, "ITEM_40"), str(edits))


def _guard_refused_pair():
    # An OPEN issue whose card reads Done, and a CLOSED issue whose card reads Building, are each
    # refused: the card's station alone, and the issue's state alone, are each sufficient.
    for label, feat_name, guard in (
            ("open but card at Done", "FEAT-89-start-task-open-done", ("OPEN", "Done")),
            ("closed but card at Building", "FEAT-89-start-task-closed-building",
             ("CLOSED", "Building"))):
        with tempfile.TemporaryDirectory() as tmp:
            r = _start_t02(tmp, feat_name, guard=guard)
            _refused(tmp, label, r)
            check(f"{label}: refusal line printed", "gh-sync: refusing #326" in r.stdout, r.stdout)


def _guard_read_fails():
    # A board read that raises (network blip mid-guard) must NOT gate: falls through to the
    # original behaviour and still writes Building for both the sub-issue and the parent.
    with tempfile.TemporaryDirectory() as tmp:
        r = _start_t02(tmp, "FEAT-89-start-task-guard-read-fails",
                       script=FAKE_GH_STATIONS_GUARD_READ_FAILS)
        edits = _item_edits(tmp)
        check("guard read fails: exits 0 (a failed guard read is not a gate either)",
              r.returncode == 0, r.stdout + r.stderr)
        check("guard read fails: falls through and still writes the sub-issue's station",
              _wrote(edits, "ITEM_326"), str(edits))
        check("guard read fails: falls through and still writes the parent's station",
              _wrote(edits, "ITEM_40"), str(edits))
        check("guard read fails: one ERROR line printed, not a silent swallow",
              "gh-sync: ERROR" in r.stderr and "326" in r.stderr, r.stderr)


# A renamed board: the board's `building` column is spelled "Doing".
CUSTOM_STATIONS = {"backlog": "Todo", "plan": "Planned", "ready": "Queued",
                   "building": "Doing", "review": "Checking", "done": "Shipped"}


def _renamed_board():
    # The six station names are fixed and every column is DERIVED from them
    # (factory_config.station_column, FEAT-41 T-01), so a declaration cannot rename a column; the
    # rename lives only on the BOARD. The harness derives `Building`, GitHub offers only `Doing`, and
    # the option lookup fails by name. Exit stays 0 -- a failed card write never gates (DEC-146,
    # DEC-138) -- and the harness must never CHASE the rename by writing OPT_DOING.
    with tempfile.TemporaryDirectory() as tmp:
        r = _start_t02(tmp, "FEAT-89-start-task-custom-stations", script=FAKE_GH_STATIONS_CUSTOM,
                       guard=("OPEN", "Todo"), stations=CUSTOM_STATIONS)
        edits = _item_edits(tmp)
        out = r.stdout + r.stderr
        check("renamed board: exit 0 — a failed card write still never gates",
              r.returncode == 0, f"exit {r.returncode}: {out[:200]!r}")
        check("renamed board: one loud ERROR naming the option the board does not offer",
              "option not found" in out and "Building" in out, out[:300])
        check("renamed board: the harness NEVER writes the renamed option — it derives the fixed "
              "name and stops, rather than hunting for a column that fits",
              not any("OPT_DOING" in l for l in edits), str(edits))


def _parent_follows_plan_write():
    # _apply_parent_rule reads plan.yaml from disk, never the calling subcommand. start-task
    # RECORDS the task's station in plan.yaml before it touches the board, so `start-task T-03` on
    # an all-done plan makes T-03 `building` and the parent derives building, not review. A card at
    # review here would mean the plan write silently did nothing. (The all-done -> review rule
    # itself is asserted in test-gh-board.py.)
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp, FAKE_GH_STATIONS)
        feat = stage_station(
            tmp, "FEAT-89-close-last-task",
            [("T-01", "done"), ("T-02", "done"), ("T-03", "done")],
            issues={"T-01": 41, "T-02": 42, "T-03": 43},
            parent=40,
        )
        r = run(["start-task", feat, "T-03"], tmp)
        edits = _item_edits(tmp)
        check("every task done: exits 0", r.returncode == 0, r.stdout + r.stderr)
        check("every task done, then start-task: the parent follows the PLAN WRITE to building, "
              "never the pre-command review",
              _wrote(edits, "ITEM_40") and not _wrote(edits, "ITEM_40", "OPT_REVIEW"),
              str(edits))


def _terminal_exemption():
    # A feature whose plan.yaml station is done writes NO PARENT station -- the terminal exemption
    # (D-03/D-04) of _apply_parent_rule. It covers the parent card only: start-task writes the
    # sub-issue's own station unconditionally, which the exemption never governed.
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp, FAKE_GH_STATIONS)
        feat = stage_station(
            tmp, "FEAT-89-done-exempt",
            [("T-01", "done")],
            issues={"T-01": 41},
            parent=40,
            feature_status=None, plan_station="done",
        )
        r = run(["start-task", feat, "T-01"], tmp)
        log = calls(tmp)
        check("a Done feature exits 0", r.returncode == 0, r.stdout + r.stderr)
        check("a Done feature writes NO PARENT station — the terminal exemption",
              not any("item-edit" in l and "ITEM_40" in l for l in log), str(log))


def _loud_pair():
    # THE LOUD PAIR (SC-04/D-02), one fixture per half, both required.
    # Half 1: the station write (item-edit) of one card fails -> exit 0, one ERROR line on stderr
    # naming it, and the write that follows (the parent's) still happens. start-task reads the
    # board first (its already-Done guard), and FAKE_GH_SHIP answers that read; SHIP_EDIT_FAIL
    # picks which single card's write fails.
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp, FAKE_GH_SHIP)
        feat = stage_ship(tmp, "FEAT-89-loud-item-edit-fails", {"T-01": 41, "T-02": 42},
                          parent=40)
        r = run(["start-task", feat, "T-02"], tmp,
                ship_env(tmp, "40=Building 41=Building 42=Backlog", SHIP_EDIT_FAIL="ITEM_42"))
        log = calls(tmp)
        check("loud pair (item-edit fails): process still exits 0", r.returncode == 0,
              r.stdout + r.stderr)
        check("loud pair (item-edit fails): stderr carries the gh-sync: ERROR line naming the "
              "card whose write failed",
              "gh-sync: ERROR" in r.stderr and "42" in r.stderr, r.stderr)
        check("loud pair (item-edit fails): a failed card write does not stop the write that "
              "follows it — the parent write was still attempted",
              any("item-edit" in l and "ITEM_40" in l for l in log), str(log))

    # Half 2: gh is absent entirely -> one SKIP line, exit 0, and no item-edit call is even
    # attempted -- proving the failing half alone would be satisfied by a tool that has simply
    # stopped writing anything.
    with tempfile.TemporaryDirectory() as tmp:
        feat = stage_station(
            tmp, "FEAT-89-loud-gh-absent",
            [("T-01", "done"), ("T-02", "done")],
            issues={"T-01": 41, "T-02": 42},
            parent=40,
        )
        r = run(["start-task", feat, "T-02"], tmp,
                {"FACTORY_GH": os.path.join(tmp, "no-such-gh")})
        check("loud pair (gh absent): one SKIP line, exit 0",
              r.returncode == 0 and r.stdout.count("SKIP") == 1, r.stdout + r.stderr)
        check("loud pair (gh absent): no item-edit call is even attempted",
              not calls(tmp), str(calls(tmp)))


def _no_board_open(tmp, feat):
    """Run open on the board-less FEAT; check it; return (feature.json, T-01 issue, T-02 issue)."""
    r = run(["open", feat], tmp)
    check("no board configured: open exits 0", r.returncode == 0, r.stdout + r.stderr)
    check("no board configured: prints the plain no-board line, not a SKIP",
          "no github.board configured" in r.stdout and "SKIP" not in r.stdout,
          r.stdout + r.stderr)
    doc = read_feature_json(os.path.join(feat, "feature.json"))
    recorded = (doc.get("github") or {}).get("issues") or {}
    t1, t2 = recorded.get("T-01"), recorded.get("T-02")
    check("no board configured: open still recorded T-02's issue — the lifecycle ran, not skipped",
          t2 is not None, str(doc))
    return doc, t1, t2


def _no_board():
    # A feature whose harness.json carries no github.board runs open and start-task unchanged,
    # exits 0, and makes no item-edit call -- the environmental precondition (D-02).
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp, FAKE_GH_STATIONS)
        feat = stage_station(
            tmp, "FEAT-89-no-board",
            [("T-01", "done"), ("T-02", "building")],
            issues={},
            board=False,
        )
        doc, t1, t2 = _no_board_open(tmp, feat)
        open(os.path.join(tmp, "calls.log"), "w").close()
        r2 = run(["start-task", feat, "T-02"], tmp)
        log = calls(tmp)
        check("no board configured: start-task exits 0", r2.returncode == 0, r2.stdout + r2.stderr)
        check("no board configured: no item-edit call is ever made",
              not any("item-edit" in l for l in log), str(log))
        check("no board configured: the issue lifecycle still ran — T-01 and T-02 are recorded",
              t1 is not None and t2 is not None, str(doc))


def _plan_write_fails():
    # FEAT-41 T-16: start-task's PLAN WRITE fails loudly and writes no card. Every other failure
    # here is best-effort because the mirror never gates (DEC-138); the plan is the TRUTH, so a
    # plan write that fails and is mirrored anyway would put a Building card against a task the
    # plan does not call building.
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp, FAKE_GH_STATIONS)
        feat = stage_station(
            tmp, "FEAT-89-plan-write-fails",
            [("T-01", "done"), ("T-02", "building")],
            issues={"T-01": 41, "T-99": 326},
            parent=40,
        )
        # The failure is provoked at the verb, not by mocking gh: T-99 IS recorded in feature.json
        # (so control reaches the plan write) but ABSENT from plan.yaml, so the real
        # plan-merge.py set-task-station exits non-zero.
        r = run(["start-task", feat, "T-99"], tmp)
        out = r.stdout + r.stderr
        edits = _item_edits(tmp)
        check("plan write fails: start-task REFUSES, exit 2 — not a best-effort carry-on",
              r.returncode == 2, f"exit {r.returncode}: {out[:300]!r}")
        check("plan write fails: the refusal names the task, the plan path and the verb that failed",
              "T-99" in out and "plan.yaml" in out and "set-task-station" in out, out[:400])
        check("plan write fails: NO card is written — the mirror never runs ahead of the truth",
              not edits, str(edits))


def _terminal_exemption_from_plan():
    # T-07: `_feature_status` feeds exactly one comparison, the terminal exemption in
    # `_apply_parent_rule`. With no feature.json status and the reader un-repointed it returns None,
    # the exemption never fires, and start-task moves a shipped feature's parent card back.
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp, FAKE_GH_STATIONS)
        feat = stage_station(
            tmp, "FEAT-80-terminal-from-plan",
            [("T-01", "done"), ("T-02", "building")],
            issues={"T-01": 41, "T-02": 42}, parent=40,
            feature_status=None, plan_station="done",
        )
        r = run(["start-task", feat, "T-02"], tmp)
        parent_edits = [l for l in _item_edits(tmp) if "40" in l]
        check("T-07: the terminal exemption fires from plan.yaml's `done` — the parent's card is "
              "NOT rewritten on a shipped feature",
              r.returncode == 0 and not parent_edits,
              f"exit {r.returncode}; parent edits={parent_edits}")

    with tempfile.TemporaryDirectory() as tmp:
        # NEGATIVE CONTROL: same shape, a LIVE station. The exemption must NOT fire, or the case
        # above passes on a repointing that exempts every feature and stops writing parents at all.
        install_gh(tmp, FAKE_GH_STATIONS)
        feat = stage_station(
            tmp, "FEAT-81-live-from-plan",
            [("T-01", "done"), ("T-02", "building")],
            issues={"T-01": 41, "T-02": 42}, parent=40,
            feature_status=None, plan_station="building",
        )
        r = run(["start-task", feat, "T-02"], tmp)
        edits = _item_edits(tmp)
        check("T-07 NEGATIVE CONTROL: a live plan.yaml station does NOT exempt — the parent rule "
              "still runs and writes",
              r.returncode == 0 and _wrote(edits, "ITEM_40"),
              f"exit {r.returncode}; edits={edits}")


def _refuses_toward_open(label, result):
    check(label, result.returncode == 2 and "gh-sync.py open" in result.stdout, result.stdout)


def _build_entry_preflight():
    # T-04 (BUG-1309): a feature with no Build-entry receipt is refused and pointed at the
    # subcommand that would mint one -- `open` for a plan still in flight, `recover-terminal` for one
    # whose stations are already done. No feature name exempts itself.
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp, FAKE_GH_STATIONS)
        feat = stage_station(tmp, "FEAT-9001-fixture-no-receipt", [("T-01", "ready")],
                             issues={"T-01": 41})
        _set_build_entry(feat)
        _refuses_toward_open("T-04 absent receipt refuses", run(["start-task", feat, "T-01"], tmp))
        bug = stage_station(tmp, "BUG-9001-fixture-no-receipt", [("T-01", "ready")],
                            issues={"T-01": 42})
        _set_build_entry(bug)
        _refuses_toward_open("T-04 BUG-named absent receipt refuses",
                             run(["start-task", bug, "T-01"], tmp))
        _refuses_toward_open("T-12 absent receipt with a trailing slash refuses the same way",
                             run(["start-task", feat + "/", "T-01"], tmp))
        _receipt_horns(tmp, feat)


def _receipt_horns(tmp, feat):
    """FEAT (no receipt) with its stations done points at recover-terminal; a recovery-required
    receipt names the derived command."""
    write_plan_yaml(feat, "FEAT-9001-fixture-no-receipt", [("T-01", "done")])
    result = run(["start-task", feat, "T-01"], tmp)
    check("T-04 station discriminator", result.returncode == 2 and "recover-terminal" in result.stdout
          and "open" not in result.stdout.lower(), result.stdout)
    recovery = stage_station(tmp, "FEAT-9002-fixture-recovery-terminal", [("T-01", "done")],
                             issues={"T-01": 44})
    _set_build_entry(recovery, "recovery-required")
    expected_command = record_schema.recovery_command_for(recovery)
    result = run(["start-task", recovery, "T-01"], tmp)
    check("T-04 recovery-required recover-terminal horn names the derived command",
          result.returncode == 0 and expected_command == "recover-terminal"
          and expected_command in result.stderr and " --yes" in result.stderr
          and "open" not in result.stderr.lower(),
          result.stderr)


# BUG-201 (D-05, REQ-05): the two swallowing consumers' diagnosis cases (T-05).
_DANGLING_FEAT = "FEAT-201-dangling"
_LEGAL_FEAT = "FEAT-201-legal"


def _dangling_load():
    with tempfile.TemporaryDirectory() as tmp:
        dangling_dir = os.path.join(tmp, ".harness", "features", _DANGLING_FEAT)
        os.makedirs(dangling_dir)
        write_dangling_plan_yaml(dangling_dir, _DANGLING_FEAT, "T-99",
                                 approval={"status": "pending"}, plan_station="plan")
        legal_dir = os.path.join(tmp, ".harness", "features", _LEGAL_FEAT)
        os.makedirs(legal_dir)
        write_dangling_plan_yaml(legal_dir, _LEGAL_FEAT, "T-01",
                                 approval={"status": "pending"}, plan_station="plan")
        try:
            artifact_accessors.load_plan(os.path.join(dangling_dir, "plan.yaml"))
            check("(D0) load_plan RAISES on the dangling fixture (T-02 depends_on T-99, absent)",
                  False, "load_plan returned instead of raising")
        except harness_yaml.PlanSchemaError as exc:
            check("(D0) load_plan RAISES on the dangling fixture (T-02 depends_on T-99, absent)",
                  "T-02" in str(exc) and "T-99" in str(exc), str(exc))
        try:
            legal_doc = artifact_accessors.load_plan(os.path.join(legal_dir, "plan.yaml"))
            check("(D0) load_plan RETURNS on the paired legal fixture (T-02 depends_on T-01, "
                  "present)", isinstance(legal_doc, dict), legal_doc)
        except Exception as exc:
            check("(D0) load_plan RETURNS on the paired legal fixture (T-02 depends_on T-01, "
                  "present)", False, repr(exc))


def _dangling_start_task():
    # (d) _projected_for REFUSES: start-task over the dangling fixture, board configured -- exit
    # EXACTLY 2, one stderr line naming BOTH T-02 and T-99, no Traceback. Never status Ready here:
    # its approval guard refuses at exit 2 on its own, so it cannot discriminate a fix that leaves
    # _projected_for still returning {}.
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp, FAKE_GH_STATIONS)
        feat = stage_depends_on(tmp, "FEAT-201-d", "T-99", issues={"T-02": 5501}, parent=40)
        r = run(["start-task", feat, "T-02"], tmp)
        both = r.stdout + r.stderr
        check("(d) start-task over the dangling fixture: exit status EXACTLY 2",
              r.returncode == 2, both)
        check("(d) exactly one stderr line names BOTH T-02 and T-99",
              sum(1 for l in r.stderr.splitlines() if "T-02" in l and "T-99" in l) == 1,
              r.stderr)
        check("(d) no Traceback anywhere in the output", "Traceback" not in both, both)

    # (e) The paired allow for (d): the same invocation over the legal fixture exits 0 and writes
    # T-02's OWN sub-issue card to Building.
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp, FAKE_GH_STATIONS)
        feat = stage_depends_on(tmp, "FEAT-201-e", "T-01", issues={"T-01": 5601, "T-02": 5602},
                                parent=40)
        r = run(["start-task", feat, "T-02"], tmp)
        edits = _item_edits(tmp)
        check("(e) start-task over the legal fixture: exits 0, exactly as today",
              r.returncode == 0, r.stdout + r.stderr)
        check("(e) start-task sets T-02's OWN issue station to Building, exactly as today",
              _wrote(edits, "ITEM_5602"), str(edits))


def _dangling_status():
    # (f) _status_plan_doc DIAGNOSES WITHOUT GATING. `status <dangling> Ready`: the ready guard
    # refuses at exit 2 with "station ready refused" because approval.status is "pending". The new
    # diagnostic line must be ADDITIVE to that pair -- never a replacement, never a second exit code.
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp, FAKE_GH_STATIONS)
        feat = stage_depends_on(tmp, "FEAT-201-f", "T-99", issues={"T-02": 5701}, parent=40)
        r = run(["status", feat, "ready"], tmp)
        both = r.stdout + r.stderr
        check("(f) status Ready over the dangling fixture: exit status UNCHANGED from today (2)",
              r.returncode == 2, both)
        check("(f) the existing refusal line is UNCHANGED from today (captured pair, additive)",
              "station ready refused" in both, both)
        check("(f) stderr ALSO carries a line naming BOTH T-02 and T-99, additive to the above",
              any("T-02" in l and "T-99" in l for l in r.stderr.splitlines()), r.stderr)


def _ready_legal():
    # (g) The paired allow for (f): approved Ready writes the complete active projection.
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp, FAKE_GH_STATIONS)
        feat = stage_depends_on(tmp, "FEAT-201-g", "T-01", issues={"T-01": 5801, "T-02": 5802},
                                parent=40, approval={"status": "approved"})
        r = run(["status", feat, "ready"], tmp)
        edits = _item_edits(tmp)
        ids = {next(p for p in l.split() if p.startswith("ITEM_")) for l in edits}
        check("(g) status Ready over the legal fixture: exits 0",
              r.returncode == 0, r.stdout + r.stderr)
        check("(g) status Ready over the legal fixture: parent and task cards move to Ready",
              ids == {"ITEM_40", "ITEM_5801", "ITEM_5802"}
              and all("OPT_READY" in l for l in edits),
              str(edits))


def _vocabulary_miss():
    # (h) FEAT-61 T-02 (D-03): a landed top-level station OUTSIDE THE VOCABULARY keeps gh-sync's
    # one posture for a vocabulary miss -- exit 2, one line naming the value, never a traceback --
    # and the task's own card, written before the parent rule, still lands.
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp, FAKE_GH_STATIONS)
        feat = stage_station(
            tmp, "FEAT-201-h",
            [("T-01", "done"), ("T-02", "building")],
            issues={"T-01": 41, "T-02": 326}, parent=40,
            feature_status=None, plan_station="Building",
        )
        r = run(["start-task", feat, "T-02"], tmp)
        both = r.stdout + r.stderr
        edits = _item_edits(tmp)
        check("(h) start-task over a top-level station outside the vocabulary: exit 2, names "
              "the value, no traceback",
              r.returncode == 2 and "'Building'" in both and "Traceback" not in both,
              both)
        check("(h) the task's OWN card was written before the parent rule refused",
              _wrote(edits, "ITEM_326", "OPT_BUILDING")
              and not any("--id ITEM_40" in l for l in edits),
              str(edits))


def _call_refuse(msg, to_stderr=False):
    """Invoke _ghs.refuse with stdout and stderr captured; return (outcome, stdout, stderr).
    TO_STDERR passes stream=sys.stderr, read inside the capture so it names the captured stream.
    An unexpected raise (a TypeError from an unsupported kwarg, say) is reported, never allowed
    to abort the rest of this suite (P-04)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            _ghs.refuse(msg, **({"stream": sys.stderr} if to_stderr else {}))
            outcome = ("returned", None)
        except SystemExit as exc:
            outcome = ("exit", exc.code)
        except TypeError as exc:
            outcome = ("typeerror", str(exc))
    return outcome, out.getvalue(), err.getvalue()


def _refuse_contract():
    # refuse() takes an optional `stream` (default stdout); _projected_for routes its plan-load
    # refusal through refuse(msg, stream=sys.stderr). Asserted directly so neither call can
    # silently flip which stream it writes to.
    outcome, out, err = _call_refuse("default stream unchanged")
    check("refuse() default: still exits 2, unaffected by the new parameter",
          outcome == ("exit", 2), outcome)
    check("refuse() default: message on stdout, exactly as before",
          "gh-sync: REFUSED — default stream unchanged" in out, out)
    check("refuse() default: nothing written to stderr", err == "", err)

    outcome, out, err = _call_refuse("stderr routed", to_stderr=True)
    check("refuse(stream=sys.stderr): exits 2", outcome == ("exit", 2), outcome)
    check("refuse(stream=sys.stderr): message on stderr, not stdout",
          "gh-sync: REFUSED — stderr routed" in err and out == "", (out, err))


def main():
    _station_writes()
    _guard_closed_done()
    _guard_open_backlog()
    _guard_refused_pair()
    _guard_read_fails()
    _renamed_board()
    _parent_follows_plan_write()
    _terminal_exemption()
    _loud_pair()
    _no_board()
    _plan_write_fails()
    _terminal_exemption_from_plan()
    _build_entry_preflight()
    _dangling_load()
    _dangling_start_task()
    _dangling_status()
    _ready_legal()
    _vocabulary_miss()
    _refuse_contract()
    return report()


if __name__ == "__main__":
    sys.exit(main())
