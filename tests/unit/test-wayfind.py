#!/usr/bin/env python3
"""Tests for wayfind.py's root resolution (FEAT-42 T-02).

`cfg()` used to resolve the harness root through `root()`'s bare-`.harness`-DIRECTORY
probe, which is exactly the $HOME/.harness fail-open recorded by measurement at
check-plan-routes.py:489-495: a directory merely NAMED `.harness`, holding no
`team-config.yaml`, satisfied it and won over the real root. `wayfind_directory_probe`
below is that fail-open, reproduced in a disposable tmp tree rather than against $HOME
itself so the case is deterministic and never depends on this machine's real home
directory.

Idiom matches its siblings (see test-no-distribution.py): a module-level `failures`
list, `check(name, cond, detail)`, plain `case_N_...` functions, and a `main` that
exits 1 on any failure. Runnable directly with `python3`, no pytest.

FEAT-2452 T-04 adds the GitHub transport cases. Every one of them runs inside `offline`,
which applies tests/offline_gh_support.offline_gh_env through patch.dict(os.environ,
clear=True): ONE FACTORY_GH fake answers every migrated read and write, a gh sentinel sits
first on PATH, and a sentinel hit is a FAIL, so no default-binary dispatch can reach GitHub.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_os.path.dirname(_anchor_tests))
from harness_config_support import write_config  # noqa: E402
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
from unittest import mock

from offline_gh_support import assert_sentinel_unused, offline_gh_env  # noqa: E402

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
sys.path.insert(0, HERE)
import wayfind as wf  # noqa: E402  (path insert must precede this import)
import factory_gh  # noqa: E402
import gh_issues as ghi  # noqa: E402

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

failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name} {detail}")
        failures.append(name)


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
    tmp = tempfile.mkdtemp(prefix="wayfind-gh-")
    try:
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
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


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
    — the walk is supposed to start from cwd alone. Restores both cwd and env in a
    `finally` so one case cannot corrupt the next.
    """
    prev_cwd = os.getcwd()
    prev_env = {k: os.environ.get(k) for k in ("HARNESS_PROJECT_DIR", "CLAUDE_PROJECT_DIR")}
    for k in prev_env:
        os.environ.pop(k, None)
    stderr_buf = io.StringIO()
    try:
        os.chdir(start_dir)
        try:
            with contextlib.redirect_stderr(stderr_buf):
                repo = wf.cfg()
            return repo, None, stderr_buf.getvalue()
        except SystemExit as se:
            return None, se.code, stderr_buf.getvalue()
    finally:
        os.chdir(prev_cwd)
        for k, v in prev_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


# ============================== Case 1 ==============================
# the $HOME/.harness fail-open: a bare `.harness` directory with no team-config.yaml
# sits between the start point and the real, MARKER-carrying root. cfg() must resolve
# against the real root, never the decoy.

def case_1_wayfind_directory_probe():
    tmp = tempfile.mkdtemp(prefix="f42-wayfind-real-")
    try:
        real_root = tmp
        _write(os.path.join(real_root, ".harness", "team-config.yaml"), "# marker\n")
        write_config(os.path.join(real_root, ".harness", "harness.json"),
                     {"github": {"sync": True, "repo": "acme/real-root"}})

        # The decoy: a directory NAMED .harness directly under `decoy_child`, holding
        # NO team-config.yaml — the bare-directory probe this case exists to defeat.
        decoy_child = os.path.join(real_root, "decoy_child")
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
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ============================== Case 2 ==============================
# no MARKER anywhere above the start point — cfg() must die with a non-zero exit,
# never fail open by resolving something else.

def case_2_wayfind_no_marker_dies():
    tmp = tempfile.mkdtemp(prefix="f42-wayfind-none-")
    try:
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
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


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
READERS = {"blockers": (wf.blockers, BLOCKED_BY), "parent": (wf.parent_of, PARENT)}


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
    rule = {"status": 1, "stderr": "gh: Not Found (HTTP 404)\n"}
    for reader, (fn, match), want in (("blockers", READERS["blockers"], []),
                                      ("parent", READERS["parent"], None)):
        with offline(f"case_7_{reader}", [dict(rule, match=match)]) as fake:
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


FRONTIER_RULES = [{"match": f"repos/{REPO}/issues/3/sub_issues", "stdout": '[{"number": 11, "state": "open"}]'},
                  dict(READ_FAILURES["401"], match=BLOCKED_BY),
                  {"match": "issue view 11", "stdout": '{"number": 11, "title": "eligible?", "assignees": [], "labels": []}'}]


def case_10_frontier_no_eligibility_on_failed_read():
    with offline("case_10_frontier", FRONTIER_RULES) as fake:
        got = run_cli("frontier", "3")
        argvs = fake.argvs()
    check("case_10_frontier_exit_1", got[:2] == ("exit", 1), repr(got))
    check("case_10_frontier_prints_no_ticket", "#11" not in got[2] and "eligible?" not in got[2], repr(got))
    check("case_10_frontier_diagnostic", got[2].startswith("wayfind: ") and "Traceback" not in got[2]
          and "HTTP 401" in got[2], repr(got))
    check("case_10_frontier_stops_reading", not any("issue view 11" in a for a in argvs), repr(argvs))


def case_11_resolve_no_writes_after_parent_uncertainty():
    rules = [dict(READ_FAILURES["500"], match=PARENT)]
    with offline("case_11_resolve", rules) as fake:
        got = run_cli("resolve", "11", "--body", "done", "--gist", "g", "--apply")
        argvs = fake.argvs()
    check("case_11_resolve_exit_1", got[:2] == ("exit", 1), repr(got))
    check("case_11_resolve_names_the_failure", "no parent map" not in got[2] and "HTTP 500" in got[2], repr(got))
    check("case_11_resolve_no_writes", argvs == [PARENT], repr(argvs))
    with offline("case_11_resolve_404", [{"match": PARENT, "status": 1, "stderr": "gh: Not Found (HTTP 404)\n"}]):
        got = run_cli("resolve", "11", "--body", "done", "--gist", "g", "--apply")
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
        rules = [FRONTIER_RULES[0], {"match": BLOCKED_BY, "stdout": UNUSABLE_BLOCKERS[label]},
                 FRONTIER_RULES[2]]
        name = f"case_10b_frontier_{label}"
        with offline(name, rules) as fake:
            got = run_cli("frontier", "3")
            argvs = fake.argvs()
        check(f"{name}_exit_1", got[:2] == ("exit", 1), repr(got))
        check(f"{name}_prints_no_ticket", "eligible?" not in got[2] and "Traceback" not in got[2], repr(got))
        check(f"{name}_stops_reading", not any("issue view 11" in a for a in argvs), repr(argvs))


def case_11b_resolve_no_writes_on_unusable_parent():
    for label in ("empty_object", "number_false", "number_zero", "number_string", "null"):
        name = f"case_11b_resolve_{label}"
        with offline(name, [{"match": PARENT, "stdout": UNUSABLE_PARENTS[label]}]) as fake:
            got = run_cli("resolve", "11", "--body", "done", "--gist", "g", "--apply")
            argvs = fake.argvs()
        check(f"{name}_exit_1", got[:2] == ("exit", 1), repr(got))
        check(f"{name}_not_absence", "no parent map" not in got[2] and got[2].startswith("wayfind: "),
              repr(got))
        check(f"{name}_no_writes", argvs == [PARENT], repr(argvs))


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
    case_12_ticket_create_url()
    case_12b_ticket_malformed_url()
    case_12c_ticket_dry_run()
    case_13_gh_bin_deleted()

    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        return 1
    print("\nALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
