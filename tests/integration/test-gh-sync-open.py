#!/usr/bin/env python3
"""`gh-sync.py open` and `backlog`: the issue/milestone lifecycle, the record it
writes into feature.json, and the two subcommands that were deleted.

Split out of test-gh-sync.py (issue #1527); the cases, their assertions and their
subprocess invocations are unchanged. Shared fixtures live in gh_sync_support.py.

    ./test-gh-sync-open.py    -> exit 0 all pass, 1 otherwise
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
    FAKE_GH, FAKE_GH_ATTACH_FAILS, SYNC, calls, check, install_gh, load_gh_sync,
    nested_feature_dir, read_feature_json, report, run, stage, write_feature_json,
    write_plan_yaml)


def stage_recover(tmp, feat_name, milestone=None, parent=None, issues=None, source_issues=None):
    """A `recover-terminal` fixture (T-03, BUG-1309): `stage()`'s sync-enabled project plus
    a plan.yaml carrying `source_issues`, and feature.json's `github` block pre-seeded with
    whatever milestone/parent/issues a recovery scenario needs already recorded."""
    feat = stage(tmp, feat_name=feat_name)
    write_plan_yaml(feat, feat_name, [("T-01", "done")], source_issues=source_issues or [])
    write_feature_json(
        os.path.join(feat, "feature.json"), feature_id=feat_name,
        github={"milestone": milestone, "parent": parent, "attached": [],
                "issues": issues or {}, "source_issues": []},
    )
    return feat


def create_calls(log):
    """Log lines that CREATE something remotely: a milestone POST, or `issue create`
    (parent or task sub-issue). Scoped to the PAYLOAD, never the path alone (P-03) —
    the milestone title LOOKUP also mentions "milestones" but is a plain GET, never
    `-X POST`, and must not count as a create."""
    return [l for l in log
            if ("api -X POST" in l and "milestones" in l) or "issue create" in l]


def non_preflight_calls(log):
    """Every logged call beyond `load_config`'s own unavoidable `gh auth status`
    preflight — what a COMMAND's own logic invoked, so a dry-run or a refusal that
    never touches `gh` at all can be asserted as making none."""
    return [l for l in log if "auth status" not in l]


FAKE_GH_FAIL_FIRST = """#!/bin/bash
echo "$*" | tr '\n' '\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
case "$1 $2" in
  "auth status") exit 0 ;;
esac
echo "simulated failure" >&2
exit 1
"""

# Milestone create succeeds (the FIRST remote-mutating call cmd_open makes); every OTHER
# gh invocation fails, so the parent (or task) create right after it fails too — the
# partial-remote-write shape D-04 must block.
FAKE_GH_PARTIAL = """#!/bin/bash
echo "$*" | tr '\n' '\001' >> "$FAKE_LOG"; echo >> "$FAKE_LOG"
case "$1 $2" in
  "auth status") exit 0 ;;
  "api -X")
    case "$*" in
      *milestones\\ -f*) echo '{"number": 7}'; exit 0 ;;
    esac
    echo "simulated failure" >&2
    exit 1 ;;
esac
echo "simulated failure" >&2
exit 1
"""


def main():
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
        # T-16: the task title carries its own feature id, prefixed with the same em dash
        # the parent title already uses at :746 — the exact argv sent, not just a substring
        # or a count, per the harness-dev-ops rule against count-only assertions.
        t01_argv = [l for l in task_create_lines if "T-01" in l]
        check("T-01 issue create carries the exact title "
              "\"FEAT-05-export-fix — T-01 — streaming export rebuild\" (T-16)",
              len(t01_argv) == 1
              and "--title FEAT-05-export-fix — T-01 — streaming export rebuild" in t01_argv[0],
              str(t01_argv))
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
        check("every call pins the pinned repo - --repo/repos flag, auth, or an api graphql "
              "line carrying the exact owner=implentio and name=fake GraphQL values",
              all("--repo implentio/fake" in l or "repos/implentio/fake" in l or l.startswith("auth")
                  or (l.startswith("api graphql") and "owner=implentio" in l and "name=fake" in l)
                  for l in log),
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
        check("created parent records its NUMBER and no origin key at all (DEC-203 item 4)",
              isinstance(gh.get("parent"), int) and "parent_origin" not in gh, doc)

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

        # --- T-11: the subcommand is GONE. It closed an issue while writing no station, so it
        #     could produce the exact state this feature exists to prevent -- an issue CLOSED with
        #     its card away from the done station. T-07's Bash gate would NOT have stopped it:
        #     gh-sync.py reaches gh through subprocess, which a PreToolUse Bash hook never sees.
        #     Deleting it is what stops it. The three assertions that stood here were about
        #     close-task itself and have no surviving subject.
        open(os.path.join(tmp, "calls.log"), "w").close()
        r = run(["close-task", feat, "T-01"], tmp)
        check("close-task is not a subcommand any more",
              r.returncode != 0 and "close-task" in (r.stdout + r.stderr)
              and "unknown command" in (r.stdout + r.stderr),
              "rc=%s out=%r err=%r" % (r.returncode, r.stdout, r.stderr))

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
        check("an ADOPTED parent records its number and no origin key either — where a parent "
              "came from is not recorded on either path",
              gh3.get("parent") == 55 and "parent_origin" not in gh3, doc3)

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
        # THE LEGACY KEY IS TOLERATED, NOT PRESERVED. This fixture's feature.json was written
        # with the key still in its github block (see the write_feature_json call above), which is
        # what every feature on disk looked like before this task. load_recorded must read it
        # without crashing, and save_recorded must not write it back.
        check("a github block written with the old origin key is read without crashing, and the "
              "key is not written back",
              gh4.get("parent") == 40 and "parent_origin" not in gh4, doc4)

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

    # --- an abandoned plan task is historical record, not work to mirror as an open child.
    with tempfile.TemporaryDirectory() as tmp6b:
        install_gh(tmp6b)
        feat6b = stage(tmp6b, feat_name="FEAT-48-abandoned-open")
        write_plan_yaml(feat6b, "FEAT-48-abandoned-open",
                        [("T-01", "ready"), ("T-07", "abandoned")],
                        approval={"status": "approved"}, plan_station="ready")
        r = run(["open", feat6b], tmp6b)
        task_creates = [line for line in calls(tmp6b)
                        if "issue create" in line and re.search(r"\bT-0\d\b", line)]
        recorded = (read_feature_json(os.path.join(feat6b, "feature.json")).get("github") or {})
        check("open skips an abandoned task instead of creating a permanent child",
              r.returncode == 0
              and any("T-01" in line for line in task_creates)
              and not any("T-07" in line for line in task_creates)
              and set((recorded.get("issues") or {}).keys()) == {"T-01"},
              f"rc={r.returncode} calls={task_creates!r} github={recorded!r}")

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

    _ghs = load_gh_sync()

    # 1. A populated github: block, including a QUOTED milestone number — _opt_int must still
    #    coerce it. This is row 3 of the fix1 spec's table: "file present with a github
    #    mapping -> load it, as today".
    _d1 = nested_feature_dir("FEAT-t06c-1")

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
    _d2 = nested_feature_dir("FEAT-t06c-2")

    json.dump({"feature_id": "F2"}, open(os.path.join(_d2, "feature.json"), "w"))

    _rec2 = _ghs.load_recorded(_d2)

    check("T-06C: a feature.json with no github: block returns the default, does not raise",
          _rec2 == {"milestone": None, "parent": None,
                    "attached": [], "issues": {}, "source_issues": [], "build_entry": None},
          str(_rec2))

    # ---------- fix1 Part B: three states must stay distinct, plus the fourth the operator's
    # table did not enumerate. Collapse row 1 (legitimate first sync) into row 2 (error) and
    # the first sync of every new feature is blocked forever; collapse row 2 into row 1 and
    # the zero-byte-truncation bug (the defect this whole fix cycle exists for) is rebuilt.
    # Every SystemExit case is asserted on the message too, not just "it raised" — a
    # SystemExit from an unrelated crash would satisfy a bare pytest.raises just as well.

    # Row 1a: file ABSENT entirely -> default rec, never a raise (already covered by cmd_open's
    # happy path via stage(), asserted again here directly against load_recorded).
    _dabsent = nested_feature_dir("FEAT-fix1b-absent")

    _recAbsent = _ghs.load_recorded(_dabsent)

    check("fix1 B row1a: absent feature.json returns the default rec, does not raise",
          _recAbsent == {"milestone": None, "parent": None,
                         "attached": [], "issues": {}, "source_issues": [], "build_entry": None},
          str(_recAbsent))

    # Row 1b: file present, a dict, but NO github: key -> default rec (already _d2 above,
    # named here again for the fix1 spec's own enumeration).
    check("fix1 B row1b: dict present with no github key returns the default rec",
          _rec2 == {"milestone": None, "parent": None,
                    "attached": [], "issues": {}, "source_issues": [], "build_entry": None},
          str(_rec2))

    # Row 2: file present but a genuine ZERO-BYTE truncation -- the exact artifact
    # save_recorded's pre-fix `open(p, "w")` guaranteed at open. THIS is the live truncation
    # fixture the dispatch requires: a 0-byte record file must ERROR, not load as empty.
    _dzero = nested_feature_dir("FEAT-fix1b-zero")

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
        _dnm = nested_feature_dir(f"FEAT-fix1b-nonmap-{_label}")
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
        _dgh = nested_feature_dir(f"FEAT-fix1b-row4-{_label}")
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
    _datomic = nested_feature_dir("FEAT-fix1a-atomic")

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
    # feature.json.lock is harness_merge's own sibling lock file (DEC-199/D-02): deliberately
    # never removed once created -- flock has no stale state, so it costs nothing left behind
    # (see harness_merge.py's module docstring). It is not the artifact this check protects
    # against; a REAL leak here would be a stray json.dump/mkstemp tempfile from a write that
    # crashed partway, which is what "no leftover temp file" actually means.
    _leftover = [f for f in os.listdir(_datomic) if f not in ("feature.json", "feature.json.lock")]

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
              "github": {"milestone": 1, "parent": 2, "attached": [],
                         "issues": {}}}),
            ("other keys present",
             {"feature_id": "F1", "status": "Building", "review_sha": "abc1234",
              "cycles_used": 3})):
        _d = nested_feature_dir(f"FEAT-finding2-{_label.replace(' ', '-')}")
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

    # ---------- T-02 (FEAT-26): source_issues mirrored from plan.yaml into feature.json,
    # threaded through save_recorded's fixed key set so no later save erases it ------------

    # --- open records source_issues from the plan.yaml the feature actually carries
    with tempfile.TemporaryDirectory() as tmpX1:
        install_gh(tmpX1)
        featX1 = stage(tmpX1, feat_name="FEAT-26-source-issues")
        write_plan_yaml(featX1, "FEAT-26-source-issues",
                         [("T-01", "pending"), ("T-02", "pending"), ("T-03", "ready")],
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
                         [("T-01", "pending"), ("T-02", "pending"), ("T-03", "ready")],
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
    _dabsentT02 = nested_feature_dir("FEAT-t02-absent")

    _recAbsentT02 = {"milestone": None, "parent": None, "attached": [],
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

    # ---------- T-04 (FEAT-26): closes emits the pull-request-body closing keywords derived
    # --- T-06: the `closes` subcommand is DELETED ------------------------------------------------
    # It rendered one closing-keyword line per source ticket for the operator to paste into a pull
    # request body, so that
    # GitHub's merge would close the source tickets. Under DEC-203 `ship` lands those cards at the
    # done station instead, and GitHub's Auto-close issue workflow closes them -- so the rendering
    # had one job and no longer has it. There is deliberately NO deprecation shim: a shim that
    # still prints the lines would let the old route keep working while the new one is untested.

    # BUILT, NEVER SPELLED. T-06's verify greps this whole directory for the literal, so a test
    # that spelled it would fail the clause it exists to prove.
    _CLOSES_LITERAL = "Closes" + " #"

    # The fixture is `stage`, not a bare directory. The OLD `closes` was dispatched BEFORE the root
    # climb and `load_config`, so a directory with no harness.json still reached it. Now that the
    # subcommand is gone, the same fixture would exit at `load_config`'s SKIP and never reach the
    # dispatch -- and the test would pass for the wrong reason, proving nothing about `closes`.
    with tempfile.TemporaryDirectory() as tmpC1:
        install_gh(tmpC1)
        featC1 = stage(tmpC1, feat_name="FEAT-40-closes-gone")
        r = run(["closes", featC1], tmpC1)
        check("the closes subcommand exits non-zero and is named as unknown",
              r.returncode != 0 and "closes" in (r.stdout + r.stderr)
              and "unknown command" in (r.stdout + r.stderr),
              "rc=%s out=%r err=%r" % (r.returncode, r.stdout, r.stderr))
        check("the closes subcommand renders NO Closes line — not even a deprecation notice "
              "carrying one",
              _CLOSES_LITERAL not in (r.stdout + r.stderr), repr(r.stdout + r.stderr))

    # No function anywhere in gh-sync.py emits that line any more.
    check("no function in gh-sync.py emits a closing-keyword line",
          _CLOSES_LITERAL not in open(SYNC).read(), "the literal survives in gh-sync.py")

    # --- source_issues itself STAYS: only the rendering went ---------------------------------------
    # `cmd_open` still mirrors plan.yaml's own top-level list into feature.json, and T-04's ship
    # is what moves those cards. Deleting the renderer must not have taken the record with it.
    with tempfile.TemporaryDirectory() as tmpC5:
        install_gh(tmpC5)
        featC5 = stage(tmpC5, feat_name="FEAT-40-sources-survive")
        write_plan_yaml(featC5, "FEAT-40-sources-survive", [("T-01", "pending")],
                         source_issues=[305, 101, 220])
        r = run(["open", featC5], tmpC5)
        ghC5 = (read_feature_json(os.path.join(featC5, "feature.json")).get("github") or {})
        check("cmd_open still mirrors plan.yaml's source_issues into feature.json, in order",
              ghC5.get("source_issues") == [305, 101, 220],
              "rc=%s github=%s" % (r.returncode, ghC5))

    # ---------- T-02: gh-sync.py open records the Build-entry outcome ----------
    # D-04: a run failing AFTER any remote create records NOTHING (field absent). D-09:
    # github.sync true with github.repo unpinned records NOTHING via the explicit _NO_RECORD
    # sentinel; not-applicable belongs to the sync-not-enabled skip alone.
    with tempfile.TemporaryDirectory() as tmpT2a:
        install_gh(tmpT2a, FAKE_GH)
        featT2a = stage(tmpT2a, feat_name="FEAT-70-t02-opened")
        rT2a = run(["open", featT2a], tmpT2a)
        docT2a = read_feature_json(os.path.join(featT2a, "feature.json"))
        ghT2a = docT2a.get("github") or {}
        check("T-02 open records opened",
              rT2a.returncode == 0 and ghT2a.get("build_entry") == "opened",
              f"rc={rT2a.returncode} github={ghT2a!r} out={rT2a.stdout!r}")

    with tempfile.TemporaryDirectory() as tmpT2b:
        install_gh(tmpT2b, FAKE_GH)
        featT2b = stage(tmpT2b, sync=False, feat_name="FEAT-70-t02-syncfalse")
        rT2b = run(["open", featT2b], tmpT2b)
        docT2b = read_feature_json(os.path.join(featT2b, "feature.json"))
        ghT2b = docT2b.get("github") or {}
        check("T-02 sync false records not-applicable",
              rT2b.returncode == 0 and ghT2b.get("build_entry") == "not-applicable"
              and not calls(tmpT2b),
              f"rc={rT2b.returncode} github={ghT2b!r} calls={calls(tmpT2b)!r}")

    with tempfile.TemporaryDirectory() as tmpT2c:
        install_gh(tmpT2c, FAKE_GH)
        featT2c = stage(tmpT2c, repo=None, feat_name="FEAT-70-t02-unpinned")
        rT2c = run(["open", featT2c], tmpT2c)
        docT2c = read_feature_json(os.path.join(featT2c, "feature.json"))
        ghT2c = docT2c.get("github") or {}
        check("T-02 unpinned repo records nothing",
              rT2c.returncode == 0 and "build_entry" not in ghT2c,
              f"rc={rT2c.returncode} github={ghT2c!r}")

    with tempfile.TemporaryDirectory() as tmpT2d:
        install_gh(tmpT2d, FAKE_GH_FAIL_FIRST)
        featT2d = stage(tmpT2d, feat_name="FEAT-70-t02-firstfail")
        rT2d = run(["open", featT2d], tmpT2d)
        docT2d = read_feature_json(os.path.join(featT2d, "feature.json"))
        ghT2d = docT2d.get("github") or {}
        check("T-02 first-call failure records recovery-required",
              rT2d.returncode == 0 and ghT2d.get("build_entry") == "recovery-required",
              f"rc={rT2d.returncode} github={ghT2d!r} out={rT2d.stdout!r}")

    with tempfile.TemporaryDirectory() as tmpT2e:
        install_gh(tmpT2e, FAKE_GH_PARTIAL)
        featT2e = stage(tmpT2e, feat_name="FEAT-70-t02-partial")
        rT2e = run(["open", featT2e], tmpT2e)
        docT2e = read_feature_json(os.path.join(featT2e, "feature.json"))
        ghT2e = docT2e.get("github") or {}
        check("T-02 partial remote write records nothing",
              rT2e.returncode == 0 and "build_entry" not in ghT2e
              and ghT2e.get("milestone") == 7,
              f"rc={rT2e.returncode} github={ghT2e!r} out={rT2e.stdout!r}")

    with tempfile.TemporaryDirectory() as tmpT2f:
        install_gh(tmpT2f, FAKE_GH)
        featT2f = stage(tmpT2f, feat_name="FEAT-70-t02-secondopen")
        run(["open", featT2f], tmpT2f)
        n_before_f = len(calls(tmpT2f))
        rT2f = run(["open", featT2f], tmpT2f)
        new_f = calls(tmpT2f)[n_before_f:]
        docT2f = read_feature_json(os.path.join(featT2f, "feature.json"))
        ghT2f = docT2f.get("github") or {}
        check("T-02 second open stays opened",
              rT2f.returncode == 0 and ghT2f.get("build_entry") == "opened"
              and not any("issue create" in l or "milestones" in l for l in new_f),
              f"github={ghT2f!r} new_calls={new_f!r}")

    with tempfile.TemporaryDirectory() as tmpT2g:
        install_gh(tmpT2g, FAKE_GH_FAIL_FIRST)
        featT2g = stage(tmpT2g, feat_name="FEAT-70-t02-nodowngrade")
        write_feature_json(
            os.path.join(featT2g, "feature.json"),
            feature_id="FEAT-70-t02-nodowngrade",
            github={"milestone": None, "parent": None, "attached": [], "issues": {},
                    "build_entry": "opened"},
        )
        rT2g = run(["open", featT2g], tmpT2g)
        docT2g = read_feature_json(os.path.join(featT2g, "feature.json"))
        ghT2g = docT2g.get("github") or {}
        check("T-02 opened never downgrades",
              rT2g.returncode == 0 and ghT2g.get("build_entry") == "opened",
              f"rc={rT2g.returncode} github={ghT2g!r} out={rT2g.stdout!r}")

    with tempfile.TemporaryDirectory() as tmpT2h:
        install_gh(tmpT2h, FAKE_GH)
        featT2h = stage(tmpT2h, feat_name="FEAT-70-t02-contracterror")
        os.remove(os.path.join(featT2h, "BRIEF.md"))
        rT2h = run(["open", featT2h], tmpT2h)
        docT2h = read_feature_json(os.path.join(featT2h, "feature.json"))
        ghT2h = docT2h.get("github", {})
        check("T-02 contract error records nothing",
              rT2h.returncode == 1 and "build_entry" not in ghT2h,
              f"rc={rT2h.returncode} github={ghT2h!r} out={rT2h.stdout!r}")

    # ---------- T-03 (BUG-1309): gh-sync.py recover-terminal ----------
    # The remedy every refusal this bug's OTHER tasks point at, for a feature that predates the
    # Build-entry receipt. FEAT-55, this bug's own subject, records milestone 52, parent 1289
    # and twelve task sub-issues 1391-1402 with NO build_entry (measured fact) -- the fixture
    # below reproduces exactly that shape.
    #
    # `recover-terminal` is the OPEN lifecycle run late: it creates the milestone and the parent
    # issue, mirrors source_issues and writes the same feature.json record cmd_open writes, so
    # its cases live beside cmd_open's. The ONE recover-terminal case that does not is the `ship`
    # signpost, which lives with the no-board ship bookkeeping in test-gh-sync-record.py.

    _FEAT55_ISSUES = {f"T-{i:02d}": 1390 + i for i in range(1, 13)}

    with tempfile.TemporaryDirectory() as tmpR1:
        install_gh(tmpR1)
        featR1 = stage_recover(tmpR1, "FEAT-70-t03-dry", source_issues=[501])
        fj_path_R1 = os.path.join(featR1, "feature.json")
        before_R1 = open(fj_path_R1, "rb").read()
        rR1 = run(["recover-terminal", featR1], tmpR1)
        after_R1 = open(fj_path_R1, "rb").read()
        check("T-03 report and ask writes nothing",
              rR1.returncode == 0 and "would" in rR1.stdout
              and not non_preflight_calls(calls(tmpR1)) and before_R1 == after_R1,
              f"rc={rR1.returncode} out={rR1.stdout!r} calls={calls(tmpR1)!r}")

    with tempfile.TemporaryDirectory() as tmpR2:
        install_gh(tmpR2)
        featR2 = stage_recover(tmpR2, "FEAT-70-t03-create", source_issues=[401, 402])
        rR2 = run(["recover-terminal", featR2, "--yes"], tmpR2)
        docR2 = read_feature_json(os.path.join(featR2, "feature.json"))
        ghR2 = docR2.get("github") or {}
        logR2 = calls(tmpR2)
        check("T-03 recover-terminal creates milestone and parent only",
              rR2.returncode == 0
              and ghR2.get("milestone") is not None and ghR2.get("parent") is not None
              and ghR2.get("issues") == {} and ghR2.get("source_issues") == [401, 402]
              and ghR2.get("build_entry") == "recovered-terminal"
              and len([l for l in logR2 if "issue create" in l]) == 1,
              f"rc={rR2.returncode} github={ghR2!r} calls={logR2!r}")

    with tempfile.TemporaryDirectory() as tmpR3:
        install_gh(tmpR3)
        featR3 = stage_recover(tmpR3, "FEAT-70-t03-feat55", milestone=52, parent=1289,
                               issues=dict(_FEAT55_ISSUES), source_issues=[1289])

        rR3 = run(["recover-terminal", featR3, "--yes"], tmpR3)
        docR3 = read_feature_json(os.path.join(featR3, "feature.json"))
        ghR3 = docR3.get("github") or {}
        check("T-03 FEAT-55 shape adopts and creates nothing",
              rR3.returncode == 0 and ghR3.get("build_entry") == "recovered-terminal"
              and ghR3.get("issues") == _FEAT55_ISSUES
              and len(create_calls(calls(tmpR3))) == 0,
              f"rc={rR3.returncode} github={ghR3!r} calls={calls(tmpR3)!r}")

        n_before_R4 = len(calls(tmpR3))
        rR4 = run(["recover-terminal", featR3, "--yes"], tmpR3)
        logR4 = calls(tmpR3)[n_before_R4:]
        docR4 = read_feature_json(os.path.join(featR3, "feature.json"))
        ghR4 = docR4.get("github") or {}
        check("T-03 second run is idempotent",
              rR4.returncode == 0 and ghR4.get("issues") == _FEAT55_ISSUES
              and len(create_calls(logR4)) == 0,
              f"rc={rR4.returncode} github={ghR4!r} calls={logR4!r}")

        fj_path_R5 = os.path.join(featR3, "feature.json")
        before_R5 = open(fj_path_R5, "rb").read()
        n_before_R5 = len(calls(tmpR3))
        rR5 = run(["recover-terminal", featR3, "--parent", "999", "--yes"], tmpR3)
        logR5 = calls(tmpR3)[n_before_R5:]
        after_R5 = open(fj_path_R5, "rb").read()
        both_R5 = rR5.stdout + rR5.stderr
        check("T-03 parent contract error refuses",
              rR5.returncode == 2 and "999" in both_R5 and "1289" in both_R5
              and before_R5 == after_R5 and not non_preflight_calls(logR5),
              f"rc={rR5.returncode} out={both_R5!r} calls={logR5!r}")

    with tempfile.TemporaryDirectory() as tmpR6:
        install_gh(tmpR6, FAKE_GH_FAIL_FIRST)
        featR6 = stage_recover(tmpR6, "FEAT-70-t03-ghfail")
        rR6 = run(["recover-terminal", featR6, "--yes"], tmpR6)
        docR6 = read_feature_json(os.path.join(featR6, "feature.json"))
        ghR6 = docR6.get("github") or {}
        check("T-03 gh failure records nothing",
              rR6.returncode == 0 and "build_entry" not in ghR6
              and "gh-sync: SKIP" in rR6.stdout,
              f"rc={rR6.returncode} github={ghR6!r} out={rR6.stdout!r}")

    return report()


if __name__ == "__main__":
    sys.exit(main())
