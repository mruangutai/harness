#!/usr/bin/env python3
"""Tests for wayfind.py's root resolution (FEAT-42 T-02).

`cfg()` used to resolve the harness root through `root()`'s bare-`.harness`-DIRECTORY
probe, which is exactly the $HOME/.harness fail-open recorded by measurement at
check-plan-routes.py:489-495: a directory merely NAMED `.harness`, holding no
`team-config.yaml`, satisfied it and won over the real root. `wayfind_directory_probe`
below is that fail-open, reproduced in a disposable tmp tree rather than against $HOME
itself so the case is deterministic and never depends on this machine's real home
directory.

Idiom matches its siblings: check_support's `check(name, cond, detail)`, plain
`case_N_...` functions, and a `main` that exits 1 on any failure. Runnable directly with `python3`, no pytest.

FEAT-2452 T-04 adds the GitHub transport cases. Every one of them runs inside `offline`,
which applies tests/offline_gh_support.offline_gh_env through patch.dict(os.environ,
clear=True): ONE FACTORY_GH fake answers every migrated read and write, a gh sentinel sits
first on PATH, and a sentinel hit is a FAIL, so no default-binary dispatch can reach GitHub.
"""
import unit_support  # noqa: F401  (puts bin/ and tests/ on sys.path; must precede repo imports)
import contextlib
import io
import json
import os
import sys
import tempfile
from unittest import mock

from check_support import Checks
from harness_config_support import write_config
from offline_gh_support import assert_sentinel_unused, offline_gh_env
import wayfind as wf
import factory_gh
import gh_issues as ghi

REPO = "acme/widget"

# The one FACTORY_GH fake. It logs {argv, stdin} per call, then answers with the first rule
# whose `match` is a substring of the joined argv (status/stdout/stderr); no match exits 0.
FAKE_GH = """#!{python}
import json, os, sys
argv = sys.argv[1:]
stdin = sys.stdin.buffer.read().decode("utf-8")
with open(os.environ["WAYFIND_FAKE_LOG"], "a", encoding="utf-8") as h:
    h.write(json.dumps({{"argv": argv, "stdin": stdin}}) + "\\n")
with open(os.environ["WAYFIND_FAKE_SPEC"], encoding="utf-8") as h:
    rules = json.load(h)
joined = " ".join(argv)
for rule in rules:
    if rule["match"] in joined:
        sys.stdout.write(rule.get("stdout", ""))
        sys.stderr.write(rule.get("stderr", ""))
        sys.exit(rule.get("status", 0))
"""

C = Checks()
check = C.check


class Fake:
    """The fake's call log, read back as a list of {argv, stdin} dicts."""

    def __init__(self, log):
        self.log = log

    def calls(self):
        if not os.path.exists(self.log):
            return []
        with open(self.log, encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]

    def argvs(self):
        return [" ".join(call["argv"]) for call in self.calls()]


@contextlib.contextmanager
def offline(name, rules, launchable=True):
    """Confine one case: FACTORY_GH is the fake (or a missing path when not launchable), the
    environment is cleared to offline_gh_env's, and a sentinel hit FAILs `<name>_offline`."""
    with tempfile.TemporaryDirectory(prefix="wayfind-gh-", ignore_cleanup_errors=True) as tmp:
        fake = os.path.join(tmp, "fake-gh")
        if launchable:
            _write(fake, FAKE_GH.format(python=sys.executable))
            os.chmod(fake, 0o755)
        env, sentinel_log = offline_gh_env(fake if launchable else fake + "-missing", tmp)
        env["WAYFIND_FAKE_LOG"] = os.path.join(tmp, "calls.jsonl")
        env["WAYFIND_FAKE_SPEC"] = os.path.join(tmp, "spec.json")
        _write(env["WAYFIND_FAKE_SPEC"], json.dumps(rules))
        with mock.patch.dict(os.environ, env, clear=True):
            yield Fake(env["WAYFIND_FAKE_LOG"])
        _check_offline(name, sentinel_log)


def _check_offline(name, sentinel_log):
    try:
        assert_sentinel_unused(sentinel_log)
    except AssertionError as error:
        check(f"{name}_offline", False, str(error))


def outcome(fn, *args):
    """Call fn(*args) capturing stdout+stderr: ("value", result, text), ("exit", code, text)
    or ("raise", exception, text). Old wayfind code dies (SystemExit) where typed code raises."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            return "value", fn(*args), buf.getvalue()
    except SystemExit as error:
        return "exit", error.code, buf.getvalue()
    except Exception as error:  # noqa: BLE001 — the kind of failure is what the case asserts
        return "raise", error, buf.getvalue()


def is_gh_error(result):
    return result[0] == "raise" and isinstance(result[1], factory_gh.GhError)


def run_cli(*argv):
    """wayfind's CLI entry (cli) with cfg() pinned to REPO; returns ("exit"/"value", code, text)."""
    with mock.patch.object(wf, "cfg", return_value=REPO), \
            mock.patch.object(sys, "argv", ["wayfind.py", *argv]):
        return outcome(wf.cli)


def _write(path, content=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def _run_cfg_from(start_dir):
    """chdir to `start_dir`, call wf.cfg(), and report what happened.

    Returns (repo_or_none, exit_code_or_none, stderr_text). The two env spellings this
    feature deletes are cleared for the duration so a real HARNESS_PROJECT_DIR or
    CLAUDE_PROJECT_DIR set on the runner's own machine cannot mask the probe under test
    — the walk is supposed to start from cwd alone. patch.dict and chdir restore env and
    cwd on exit so one case cannot corrupt the next.
    """
    stderr_buf = io.StringIO()
    with mock.patch.dict(os.environ), contextlib.chdir(start_dir):
        for k in ("HARNESS_PROJECT_DIR", "CLAUDE_PROJECT_DIR"):
            os.environ.pop(k, None)
        try:
            with contextlib.redirect_stderr(stderr_buf):
                repo = wf.cfg()
            return repo, None, stderr_buf.getvalue()
        except SystemExit as se:
            return None, se.code, stderr_buf.getvalue()


# ============================== Case 1 ==============================
# the $HOME/.harness fail-open: a bare `.harness` directory with no team-config.yaml
# sits between the start point and the real, MARKER-carrying root. cfg() must resolve
# against the real root, never the decoy.

def case_1_wayfind_directory_probe():
    with tempfile.TemporaryDirectory(prefix="f42-wayfind-real-", ignore_cleanup_errors=True) as tmp:
        _write(os.path.join(tmp, ".harness", "team-config.yaml"), "# marker\n")
        write_config(os.path.join(tmp, ".harness", "harness.json"),
                     {"github": {"sync": True, "repo": "acme/real-root"}})

        # The decoy: a directory NAMED .harness directly under `decoy_child`, holding
        # NO team-config.yaml — the bare-directory probe this case exists to defeat.
        decoy_child = os.path.join(tmp, "decoy_child")
        os.makedirs(os.path.join(decoy_child, ".harness"), exist_ok=True)

        start = os.path.join(decoy_child, "nested", "start")
        os.makedirs(start, exist_ok=True)

        repo, exit_code, stderr_text = _run_cfg_from(start)

        check(
            "case_1_wayfind_directory_probe_resolves_real_root",
            repo == "acme/real-root",
            f"expected cfg() to resolve the real, MARKER-carrying root and return its "
            f"github.repo ('acme/real-root'); got repo={repo!r} exit_code={exit_code!r} "
            f"stderr={stderr_text!r}",
        )


# ============================== Case 2 ==============================
# no MARKER anywhere above the start point — cfg() must die with a non-zero exit,
# never fail open by resolving something else.

def case_2_wayfind_no_marker_dies():
    with tempfile.TemporaryDirectory(prefix="f42-wayfind-none-", ignore_cleanup_errors=True) as tmp:
        start = os.path.join(tmp, "a", "b", "c")
        os.makedirs(start, exist_ok=True)
        # deliberately NO .harness/team-config.yaml anywhere under `tmp`

        repo, exit_code, stderr_text = _run_cfg_from(start)

        check(
            "case_2_wayfind_no_marker_dies_nonzero",
            repo is None and isinstance(exit_code, int) and exit_code != 0,
            f"expected cfg() to die with a non-zero exit when no MARKER exists above "
            f"the start point; got repo={repo!r} exit_code={exit_code!r} "
            f"stderr={stderr_text!r}",
        )


# ============================== T-04: migrated paths ==============================
# One FACTORY_GH fake answers every read and write; the sentinel proves no other binary ran.

def case_3_strict_json_read_on_factory_gh():
    rules = [{"match": "api repos/acme/widget/issues/5", "stdout": '{"number": 5, "id": 905}'}]
    with offline("case_3_strict_json_read", rules) as fake:
        got = outcome(wf.gh_json, ["api", f"repos/{REPO}/issues/5"])
        argvs = fake.argvs()
    check("case_3_strict_json_read_value", got[:2] == ("value", {"number": 5, "id": 905}), repr(got))
    check("case_3_strict_json_read_one_fake_call", argvs == [f"api repos/{REPO}/issues/5"], repr(argvs))


def case_4_do_dry_run_and_apply():
    cmd = ["issue", "close", "5", "-R", REPO]
    with offline("case_4_do", [{"match": "issue close", "stdout": "closed #5\n"}]) as fake:
        dry = outcome(wf.do, [cmd], False)
        dry_calls = fake.argvs()
        wet = outcome(wf.do, [cmd], True)
        wet_calls = fake.argvs()
    check("case_4_do_dry_run_launches_nothing", dry_calls == [], repr(dry_calls))
    check("case_4_do_dry_run_prints_plan",
          "would run: gh issue close 5" in dry[2] and "DRY RUN" in dry[2], repr(dry))
    check("case_4_do_apply_runs_on_fake", wet_calls == [" ".join(cmd)] and "closed #5" in wet[2],
          f"{wet_calls!r} {wet!r}")


GIST_BODY = "## Destination\n\nship it  \n\n## Decisions so far\n\n- old ✓\n\n## Notes\nα\r\n"


def case_5_gist_stdin_byte_exact():
    rules = [{"match": "issue view 7", "stdout": json.dumps({"body": GIST_BODY})}]
    with offline("case_5_gist", rules) as fake:
        dry = outcome(wf.append_gist, REPO, 7, "- [#9 t] — new", False)
        dry_calls = fake.argvs()
        wet = outcome(wf.append_gist, REPO, 7, "- [#9 t] — new", True)
        calls = fake.calls()
    want = "## Destination\n\nship it  \n\n## Decisions so far\n\n- old ✓\n- [#9 t] — new\n\n## Notes\nα\r\n"
    check("case_5_gist_dry_run_reads_only", dry[0] == "value" and dry_calls == [f"issue view 7 -R {REPO} --json body"],
          f"{dry!r} {dry_calls!r}")
    edit = calls[-1] if calls else {}
    check("case_5_gist_edit_argv", edit.get("argv") == ["issue", "edit", "7", "-R", REPO, "--body-file", "-"],
          f"{wet!r} {calls!r}")
    check("case_5_gist_stdin_byte_exact", edit.get("stdin") == want, repr(edit.get("stdin")))


# ============================== T-04: fail-closed reads ==============================
# gh exits 1 for EVERY HTTP error, so absence is only a completed nonzero process whose stderr
# carries gh's explicit "(HTTP 404)" marker. Everything else must raise GhError.

BLOCKED_BY = f"api repos/{REPO}/issues/11/dependencies/blocked_by"
PARENT = f"api repos/{REPO}/issues/11/parent"
READ_FAILURES = {
    "401": {"status": 1, "stderr": "gh: Bad credentials (HTTP 401)\n"},
    "403": {"status": 1, "stderr": "gh: Resource not accessible by integration (HTTP 403)\n"},
    "500": {"status": 1, "stderr": "gh: Server Error (HTTP 500)\n"},
    "network": {"status": 1, "stderr": "error connecting to api.github.com\n"},
    "exit1_no_marker": {"status": 1, "stderr": "something went wrong\n"},
    "misleading_404": {"status": 1, "stderr": "gh: issue 404 is locked (HTTP 410)\nHTTP 4040\n"},
    "status0_malformed_with_404": {"status": 0, "stdout": "<html>", "stderr": "gh: Not Found (HTTP 404)\n"},
}
NOT_FOUND = {"status": 1, "stderr": "gh: Not Found (HTTP 404)\n"}  # the one confirmed-absence answer
READERS = {"blockers": (wf.blockers, BLOCKED_BY), "parent": (wf.parent_of, PARENT)}
RESOLVE_11 = ("resolve", "11", "--body", "done", "--gist", "g", "--apply")


def case_6_reads_fail_closed():
    for reader, (fn, match) in READERS.items():
        for label, rule in READ_FAILURES.items():
            name = f"case_6_{reader}_{label}"
            with offline(name, [dict(rule, match=match)]):
                got = outcome(fn, REPO, 11)
            check(f"{name}_raises_gh_error", is_gh_error(got), repr(got))
        name = f"case_6_{reader}_launch_failure"
        with offline(name, [], launchable=False):
            got = outcome(fn, REPO, 11)
        check(f"{name}_raises_gh_error", is_gh_error(got) and got[1].status is None, repr(got))


def case_7_genuine_404_is_absence():
    for reader, want in (("blockers", []), ("parent", None)):
        fn, match = READERS[reader]
        with offline(f"case_7_{reader}", [dict(NOT_FOUND, match=match)]) as fake:
            got = outcome(fn, REPO, 11)
            argvs = fake.argvs()
        check(f"case_7_{reader}_404_is_absence", got[:2] == ("value", want) and len(argvs) == 1,
              f"{got!r} {argvs!r}")


def case_8_valid_reads():
    rules = [{"match": BLOCKED_BY, "stdout": '[{"number": 3, "state": "open"}]'},
             {"match": PARENT, "stdout": '{"number": 2}'}]
    with offline("case_8_valid_reads", rules):
        got_b = outcome(wf.blockers, REPO, 11)
        got_p = outcome(wf.parent_of, REPO, 11)
    check("case_8_blockers_value", got_b[:2] == ("value", [{"number": 3, "state": "open"}]), repr(got_b))
    check("case_8_parent_value", got_p[:2] == ("value", 2), repr(got_p))


def case_9_invalid_json_raises():
    for label, text in (("garbage", "not json"), ("duplicate", '{"a": 1, "a": 2}'),
                        ("nonfinite", '{"a": NaN}')):
        with offline(f"case_9_{label}", [{"match": "api", "stdout": text}]):
            got = outcome(wf.gh_json, ["api", f"repos/{REPO}/issues/5"])
        check(f"case_9_{label}_raises_gh_error", is_gh_error(got), repr(got))


OPEN_11 = '[{"number": 11, "state": "open"}]'


def case_10_frontier_no_eligibility_on_failed_read():
    got, argvs = _frontier("case_10_frontier", OPEN_11, READ_FAILURES["401"], json.dumps(VIEW_11))
    check("case_10_frontier_exit_1", got[:2] == ("exit", 1), repr(got))
    check("case_10_frontier_prints_no_ticket", "#11" not in got[2] and "eligible?" not in got[2], repr(got))
    check("case_10_frontier_diagnostic", got[2].startswith("wayfind: ") and "Traceback" not in got[2]
          and "HTTP 401" in got[2], repr(got))
    check("case_10_frontier_stops_reading", not any("issue view 11" in a for a in argvs), repr(argvs))


def case_11_resolve_no_writes_after_parent_uncertainty():
    rules = [dict(READ_FAILURES["500"], match=PARENT)]
    with offline("case_11_resolve", rules) as fake:
        got = run_cli(*RESOLVE_11)
        argvs = fake.argvs()
    check("case_11_resolve_exit_1", got[:2] == ("exit", 1), repr(got))
    check("case_11_resolve_names_the_failure", "no parent map" not in got[2] and "HTTP 500" in got[2], repr(got))
    check("case_11_resolve_no_writes", argvs == [PARENT], repr(argvs))
    with offline("case_11_resolve_404", [dict(NOT_FOUND, match=PARENT)]):
        got = run_cli(*RESOLVE_11)
    check("case_11_resolve_404_means_no_parent", got[:2] == ("exit", 1) and "no parent map" in got[2], repr(got))


# H2 (c1): a SUCCESSFUL payload the reader cannot use is never absence. Only the confirmed 404
# above means "no blockers" / "no parent"; null, {} and wrong types raise GhError.
UNUSABLE_BLOCKERS = {"null": "null", "object": "{}", "string": '"none"', "number": "0",
                     "bool": "false", "non_object_item": '[3]', "null_item": "[null]"}
UNUSABLE_PARENTS = {"null": "null", "empty_object": "{}", "number_false": '{"number": false}',
                    "number_true": '{"number": true}', "number_zero": '{"number": 0}',
                    "number_negative": '{"number": -2}', "number_string": '{"number": "2"}',
                    "number_float": '{"number": 2.0}', "number_null": '{"number": null}',
                    "list": '[{"number": 2}]'}


def case_8b_unusable_success_payloads_raise():
    for reader, table in (("blockers", UNUSABLE_BLOCKERS), ("parent", UNUSABLE_PARENTS)):
        fn, match = READERS[reader]
        for label, text in table.items():
            name = f"case_8b_{reader}_{label}"
            with offline(name, [{"match": match, "stdout": text}]):
                got = outcome(fn, REPO, 11)
            check(f"{name}_raises_gh_error", is_gh_error(got), repr(got))


def case_10b_frontier_no_eligibility_on_unusable_blockers():
    for label in ("null", "object"):
        name = f"case_10b_frontier_{label}"
        got, argvs = _frontier(name, OPEN_11, UNUSABLE_BLOCKERS[label], json.dumps(VIEW_11))
        check(f"{name}_exit_1", got[:2] == ("exit", 1), repr(got))
        check(f"{name}_prints_no_ticket", "eligible?" not in got[2] and "Traceback" not in got[2], repr(got))
        check(f"{name}_stops_reading", not any("issue view 11" in a for a in argvs), repr(argvs))


def case_11b_resolve_no_writes_on_unusable_parent():
    for label in ("empty_object", "number_false", "number_zero", "number_string", "null"):
        name = f"case_11b_resolve_{label}"
        with offline(name, [{"match": PARENT, "stdout": UNUSABLE_PARENTS[label]}]) as fake:
            got = run_cli(*RESOLVE_11)
            argvs = fake.argvs()
        check(f"{name}_exit_1", got[:2] == ("exit", 1), repr(got))
        check(f"{name}_not_absence", "no parent map" not in got[2] and got[2].startswith("wayfind: "),
              repr(got))
        check(f"{name}_no_writes", argvs == [PARENT], repr(argvs))


# M1 (c2): every field frontier and resolve DECIDE on is validated, not only the container.
# A blocker or sub-issue state must be a string whose lowercase is open or closed; a sub-issue
# needs a positive integer number; the frontier's ticket view needs its own number, a string
# title, an assignees list and a list of named labels (the round's research/HITL split).
STATELESS_BLOCKERS = {"item_no_state": "[{}]", "state_unknown": '[{"state": "unknown"}]',
                      "state_int": '[{"state": 1}]', "state_null": '[{"state": null}]',
                      "state_empty": '[{"state": ""}]', "state_list": '[{"state": ["open"]}]',
                      "second_item_stateless": '[{"state": "closed"}, {"number": 4}]'}
VIEW_11 = {"number": 11, "title": "eligible?", "assignees": [], "labels": []}


def _without(field, **extra):
    view = {k: v for k, v in VIEW_11.items() if k != field}
    view.update(extra)
    return json.dumps(view)


UNUSABLE_SUBS = {"null": "null", "object": "{}", "non_object_item": "[11]",
                 "no_state": '[{"number": 11}]', "state_unknown": '[{"number": 11, "state": "unknown"}]',
                 "state_int": '[{"number": 11, "state": 1}]', "no_number": '[{"state": "open"}]',
                 "number_string": '[{"number": "11", "state": "open"}]',
                 "number_bool": '[{"number": true, "state": "open"}]',
                 "number_zero": '[{"number": 0, "state": "open"}]'}
UNUSABLE_VIEWS = {"view_null": "null", "view_list": "[]",
                  "assignees_missing": _without("assignees"),
                  "assignees_null": _without("assignees", assignees=None),
                  "assignees_string": _without("assignees", assignees="octocat"),
                  "assignees_object": _without("assignees", assignees={"login": "octocat"}),
                  "labels_missing": _without("labels"),
                  "labels_string": _without("labels", labels="wayfinder:research"),
                  "labels_non_object_item": _without("labels", labels=["wayfinder:research"]),
                  "labels_nameless_item": _without("labels", labels=[{}]),
                  "labels_name_int": _without("labels", labels=[{"name": 7}]),
                  "title_missing": _without("title"), "title_null": _without("title", title=None),
                  "number_missing": _without("number"), "number_other": _without("number", number=12),
                  "number_string": _without("number", number="11"),
                  "number_bool": _without("number", number=True)}
SUBS_11 = f"repos/{REPO}/issues/3/sub_issues"


def _frontier(name, subs, blocked, view):
    """run `frontier 3` with sub-issues `subs`, #11's blockers `blocked`, #11's view `view`."""
    rules = [{"match": SUBS_11, "stdout": subs},
             dict(blocked, match=BLOCKED_BY) if isinstance(blocked, dict) else {"match": BLOCKED_BY, "stdout": blocked},
             {"match": "issue view 11", "stdout": view}]
    with offline(name, rules) as fake:
        return run_cli("frontier", "3"), fake.argvs()


def _check_refused(name, got):
    check(f"{name}_exit_1", got[:2] == ("exit", 1), repr(got))
    check(f"{name}_prints_no_ticket", "eligible?" not in got[2] and "(frontier empty)" not in got[2],
          repr(got))
    check(f"{name}_typed_diagnostic", got[2].startswith("wayfind: ") and "unusable payload" in got[2]
          and "Traceback" not in got[2], repr(got))


def case_8c_blocker_state_must_be_open_or_closed():
    for label, text in STATELESS_BLOCKERS.items():
        name = f"case_8c_blockers_{label}"
        with offline(name, [{"match": BLOCKED_BY, "stdout": text}]):
            got = outcome(wf.blockers, REPO, 11)
        check(f"{name}_raises_gh_error", is_gh_error(got), repr(got))
    for label, payload in (("valid", [{"number": 3, "state": "OPEN"}, {"number": 4, "state": "closed"}]),
                           ("empty", [])):
        with offline(f"case_8c_blockers_{label}", [{"match": BLOCKED_BY, "stdout": json.dumps(payload)}]):
            got = outcome(wf.blockers, REPO, 11)
        check(f"case_8c_blockers_{'open_closed_any_case_valid' if payload else 'empty_list_valid'}",
              got[:2] == ("value", payload), repr(got))


def case_10c_frontier_refuses_unusable_decision_fields():
    subs, view = '[{"number": 11, "state": "open"}]', json.dumps(VIEW_11)
    for label, text in STATELESS_BLOCKERS.items():
        name = f"case_10c_frontier_blockers_{label}"
        got, argvs = _frontier(name, subs, text, view)
        _check_refused(name, got)
        check(f"{name}_stops_reading", not any("issue view 11" in a for a in argvs), repr(argvs))
    for label, text in UNUSABLE_SUBS.items():
        name = f"case_10c_frontier_subs_{label}"
        got, argvs = _frontier(name, text, "[]", view)
        _check_refused(name, got)
        check(f"{name}_stops_reading", argvs == [f"api {SUBS_11} --paginate"], repr(argvs))
    for label, text in UNUSABLE_VIEWS.items():
        name = f"case_10c_frontier_{label}"
        _check_refused(name, _frontier(name, subs, "[]", text)[0])


def case_10d_frontier_valid_decisions_unchanged():
    """The controls: valid open/closed states in any case, the empty list, a confirmed 404 and a
    claimed or blocked ticket keep their meaning."""
    research = json.dumps(dict(VIEW_11, labels=[{"name": "wayfinder:research", "color": "1d76db"}]))
    for label, subs, blocked, view, want in (
            ("closed_blockers", '[{"number": 11, "state": "OPEN"}]', '[{"state": "CLOSED"}, {"state": "closed"}]',
             research, "#11\tresearch\teligible?"),
            ("empty_blockers", '[{"number": 11, "state": "open"}]', "[]", json.dumps(VIEW_11), "#11\t?\teligible?"),
            ("blockers_404", '[{"number": 11, "state": "open"}]', NOT_FOUND, json.dumps(VIEW_11), "#11\t?\teligible?"),
            ("open_blocker", '[{"number": 11, "state": "open"}]', '[{"state": "Open"}]', json.dumps(VIEW_11),
             "(frontier empty)"),
            ("claimed", '[{"number": 11, "state": "open"}]', "[]",
             json.dumps(dict(VIEW_11, assignees=[{"login": "octocat"}])), "(frontier empty)"),
            ("closed_ticket", '[{"number": 11, "state": "closed"}]', "[]", json.dumps(VIEW_11), "(frontier empty)"),
            ("no_subs", "[]", "[]", json.dumps(VIEW_11), "(frontier empty)")):
        name = f"case_10d_frontier_{label}"
        got, _ = _frontier(name, subs, blocked, view)
        check(f"{name}_exit_0", got[:2] == ("value", 0) and got[2].strip() == want, repr(got))


MAP_VIEW = "issue view 2"


def case_11c_resolve_refuses_unusable_title_and_body():
    """resolve's title read precedes the writes, so an unusable title means no writes; the map
    body read follows them (documented), so an unusable body means no edit and a typed exit 1,
    never 'no section' or a traceback."""
    head = [{"match": PARENT, "stdout": '{"number": 2}'}]
    for label, text in (("null", "null"), ("list", "[]"), ("missing", "{}"), ("title_null", '{"title": null}'),
                        ("title_int", '{"title": 5}')):
        name = f"case_11c_resolve_title_{label}"
        with offline(name, head + [{"match": "issue view 11", "stdout": text}]) as fake:
            got = run_cli(*RESOLVE_11)
            argvs = fake.argvs()
        check(f"{name}_exit_1_typed", got[:2] == ("exit", 1) and "unusable payload" in got[2]
              and "Traceback" not in got[2], repr(got))
        check(f"{name}_no_writes", argvs == [PARENT, f"issue view 11 -R {REPO} --json title"], repr(argvs))
    for label, text in (("null", "null"), ("missing", "{}"), ("body_null", '{"body": null}'),
                        ("body_int", '{"body": 5}')):
        name = f"case_11c_gist_body_{label}"
        with offline(name, [{"match": MAP_VIEW, "stdout": text}]) as fake:
            got = outcome(wf.append_gist, REPO, 2, "- line", True)
            argvs = fake.argvs()
        check(f"{name}_raises_gh_error", is_gh_error(got), repr(got))
        check(f"{name}_no_edit", argvs == [f"{MAP_VIEW} -R {REPO} --json body"], repr(argvs))


ALL_LABELS = json.dumps([{"name": n} for n in wf.LABELS])
CREATE = "issue create"


def _ticket_rules(create_stdout):
    return [{"match": "label list", "stdout": ALL_LABELS},
            {"match": CREATE, "stdout": create_stdout},
            {"match": f"api repos/{REPO}/issues/42 --jq .id", "stdout": "9001\n"},
            {"match": f"repos/{REPO}/issues/3/sub_issues", "stdout": "{}"}]


def _ticket_cli(name, create_stdout, *flags):
    with offline(name, _ticket_rules(create_stdout)) as fake:
        got = run_cli("ticket", "3", "task", "T", *flags)
        return got, fake.argvs()


def case_12_ticket_create_url():
    got, argvs = _ticket_cli("case_12_ticket", f"https://github.com/{REPO}/issues/42\n", "--apply")
    attach = f"api repos/{REPO}/issues/3/sub_issues -F sub_issue_id=9001"
    check("case_12_ticket_attached", got[:2] == ("value", 0) and argvs[-1:] == [attach]
          and "ticket #42 [task] attached to map #3" in got[2], f"{got!r} {argvs!r}")


def case_12b_ticket_malformed_url():
    got, argvs = _ticket_cli("case_12_ticket_bad_url", "created!\n", "--apply")
    check("case_12_ticket_bad_url_exit_1", got[:2] == ("exit", 1) and got[2].startswith("wayfind: ")
          and "Traceback" not in got[2], repr(got))
    check("case_12_ticket_bad_url_stops", not any("--jq .id" in a or "sub_issues" in a for a in argvs), repr(argvs))


def case_12c_ticket_dry_run():
    got, argvs = _ticket_cli("case_12_ticket_dry", "unused")
    check("case_12_ticket_dry_run_no_mutation", got[:2] == ("value", 0) and argvs == [
        f"label list -R {REPO} --limit 200 --json name"], f"{got!r} {argvs!r}")


def case_13_gh_bin_deleted():
    check("case_13_gh_issues_has_no_gh_bin", not hasattr(ghi, "gh_bin"))
    with open(wf.__file__, encoding="utf-8") as handle:
        source = handle.read()
    retired = "GH_SYNC" + "_GH"  # assembled so this test file is not itself a site
    check("case_13_wayfind_has_no_subprocess", "subprocess" not in source and retired not in source)


def main():
    case_1_wayfind_directory_probe()
    case_2_wayfind_no_marker_dies()
    case_3_strict_json_read_on_factory_gh()
    case_4_do_dry_run_and_apply()
    case_5_gist_stdin_byte_exact()
    case_6_reads_fail_closed()
    case_7_genuine_404_is_absence()
    case_8_valid_reads()
    case_9_invalid_json_raises()
    case_10_frontier_no_eligibility_on_failed_read()
    case_11_resolve_no_writes_after_parent_uncertainty()
    case_8b_unusable_success_payloads_raise()
    case_10b_frontier_no_eligibility_on_unusable_blockers()
    case_11b_resolve_no_writes_on_unusable_parent()
    case_8c_blocker_state_must_be_open_or_closed()
    case_10c_frontier_refuses_unusable_decision_fields()
    case_10d_frontier_valid_decisions_unchanged()
    case_11c_resolve_refuses_unusable_title_and_body()
    case_12_ticket_create_url()
    case_12b_ticket_malformed_url()
    case_12c_ticket_dry_run()
    case_13_gh_bin_deleted()
    return C.report()


if __name__ == "__main__":
    sys.exit(main())
