#!/usr/bin/env python3
"""Tests for feature_schema.py and validate-feature-json.py (FEAT-14 T-01).

Plain assert, python3, stdlib only, shaped after test-check-plan-routes.py's
check()/main()-returns-0/1 convention. Every fixture is a tempfile — nothing
here reads, writes or depends on any real file under .harness/*/features/*/.

jsonschema must be importable for these tests to mean anything: they prove
the schema's SHAPE, not merely that the module imports.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

BIN_DIR = os.path.dirname(os.path.realpath(__file__))
if BIN_DIR not in sys.path:
    sys.path.insert(0, BIN_DIR)

REPO_ROOT = (os.environ.get("HARNESS_PROJECT_DIR") or os.environ.get("CLAUDE_PROJECT_DIR")) or os.path.abspath(
    os.path.join(BIN_DIR, "..", "..", "..", "..")
)


VALIDATE_CLI = os.path.join(BIN_DIR, "validate-feature-json.py")

import feature_schema  # noqa: E402  (after sys.path fixup, house convention)

failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name} {detail}")
        failures.append(name)


def swept(stderr):
    """The file COUNT from the sweep's scanning line, as an int, or None.

    Exists because `"1 file(s)" in stderr` is not a count test, it is a substring
    test, and `"41 file(s)"` contains `"1 file(s)"`. That broke in BOTH directions,
    and the silent direction is the dangerous one:

    - the two POSITIVE checks -- "the sweep reports ONE file" -- passed whenever the
      sweep wrongly scanned the real checkout, because any count ending in 1
      satisfied the substring. They could not detect the redirect they exist to
      catch.
    - the NEGATIVE check fired falsely for the same reason, with nothing wrong.

    MEASURED 2026-08-30: the first worktree to hold 41 features turned the whole
    unit suite red while the behaviour under test was correct, and the two
    fail-open positives had been passing for the wrong reason since FEAT-42.
    Any count ending in 1 -- 1, 11, 21, 31, 41 -- reproduces it.

    RAISES rather than returning None (cycle-1 panel, M2). Unmatched output is not
    evidence that the count differs from one, but `None != 1` is true, so garbled or
    absent output PASSED the negative check. "I could not measure" must be a loud
    failure, not a silent success.

    NOTE THE REMAINING LIMIT, measured: parsing the integer does not by itself make
    a call site bind. A site asserting `== 1` against a fixture whose real count is
    1 still passes under a parser that only ever yields the last digit. That is why
    case_migrated_depth also asserts a MULTI-DIGIT count below.
    """
    m = re.search(r"(\d+) file\(s\)", stderr or "")
    if m is None:
        raise AssertionError(
            "no 'N file(s)' scanning line in stderr — nothing to measure, which is a "
            "failure to observe rather than a measurement: %r" % (stderr,))
    return int(m.group(1))


def full_doc(status="Building"):
    """All eleven keys, a realistic value for each."""
    return {
        "feature_id": "FEAT-99-x",
        "branch": "feat/99",
        "pr": 42,
        "status": status,
        "review_sha": "deadbeef",
        "cycles_used": 1,
        "max_total_cycles": 8,
        # `agent` added by FEAT-31 T-15: full_doc means "a realistic VALID document",
        # and a run entry written today must name its agent (SC-07). Without it these
        # cases would fail on the positional rule rather than on the eleven-key shape
        # they exist to test. The rule's own cases below drive the missing case
        # deliberately.
        "runs": [{"id": "r1", "squad": "code", "verdict": "PASS", "agent": "harness-qa"}],
        "max_total_runs": 10,
        "github": {
            "milestone": 1, "parent": 2,             "attached": ["a"], "issues": {"T-01": 10},
        },
        "factory": {
            "repo": "r", "parent": 1,             "issues": {}, "items": {}, "edges": {"parent": [], "blocked_by": {}},
        },
    }


def required_doc(status="Building"):
    """Only the eight required keys."""
    return {
        "feature_id": "FEAT-99-x",
        "branch": "feat/99",
        "pr": None,
        "status": status,
        "review_sha": "none",
        "cycles_used": 0,
        "max_total_cycles": 8,
        "runs": [],
    }


def clean(doc, display="sample.json"):
    return feature_schema.problems_for_text(json.dumps(doc), display)


def write_file(tmpdir, name, text):
    path = os.path.join(tmpdir, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def write_json(tmpdir, name, doc):
    return write_file(tmpdir, name, json.dumps(doc, indent=2))


REQUIRED_KEYS = (
    "feature_id", "branch", "pr", "status", "review_sha",
    "cycles_used", "max_total_cycles", "runs",
)
OPTIONAL_KEYS = ("max_total_runs", "github", "factory")
STATUS_VALUES = ("Backlog", "Plan", "Ready", "Building", "Review", "Done")

# Spelled out independently rather than imported from feature_schema — importing
# feature_schema._REDIRECT and asserting it appears in feature_schema's own output
# would be tautological. This is the literal sentence T-01's intent gives, verbatim.
REDIRECT_SENTENCE = (
    "This file holds execution state only. An operator ruling goes in that feature's "
    "plan.yaml under approval.rulings; run narrative, findings and corrections go in "
    "that run's digest; current state and open questions go in STATE.md; "
    "measurements, research and receipts go in notes/."
)


def case_accepted_all_eleven_keys():
    problems = clean(full_doc())
    check("accepted_all_eleven_keys", problems == [], problems)


def case_accepted_only_eight_required_keys():
    problems = clean(required_doc())
    check("accepted_only_eight_required_keys", problems == [], problems)


def case_accepted_omitting_one_optional_key():
    for key in OPTIONAL_KEYS:
        doc = full_doc()
        del doc[key]
        problems = clean(doc)
        check(f"accepted_omitting_optional_{key}", problems == [], problems)


def case_rejected_omitting_one_required_key():
    for key in REQUIRED_KEYS:
        doc = required_doc()
        del doc[key]
        problems = clean(doc)
        # The quoted form, matching feature_schema's f"missing required key {key!r}"
        # rendering — a bare substring match cannot tell "names the right key" from
        # "names some key that happens to contain this key's letters".
        named = any(f"'{key}'" in p for p in problems)
        check(f"rejected_omitting_required_{key}", problems != [] and named, problems)


def case_accepted_each_status_value():
    for status in STATUS_VALUES:
        problems = clean(required_doc(status=status))
        check(f"accepted_status_{status}", problems == [], problems)


def case_rejected_phase_is_gone():
    doc = required_doc()
    doc["phase"] = "ship"
    problems = clean(doc)
    named = any("'phase'" in p for p in problems)
    check("rejected_phase_undeclared", problems != [] and named, problems)


def case_rejected_undeclared_top_level_key():
    doc = full_doc()
    doc["invented_key"] = "x"
    problems = clean(doc)
    named = any("'invented_key'" in p for p in problems)
    redirected = any(REDIRECT_SENTENCE in p for p in problems)
    check("rejected_undeclared_top_level_key", problems != [] and named and redirected, problems)


def case_rejected_undeclared_runs_item_key():
    doc = full_doc()
    doc["runs"] = [{"id": "r1", "squad": "code", "verdict": "PASS", "cost_usd": 1.5}]
    problems = clean(doc)
    named = any("'cost_usd'" in p for p in problems)
    redirected = any(REDIRECT_SENTENCE in p for p in problems)
    check("rejected_undeclared_runs_item_key", problems != [] and named and redirected, problems)


def case_accepted_runs_item_code_grade_n_a():
    """BUG-1080: the plan-phase panel run DEC-207 legalises must be schema-VALID, or the
    exemption INV-6 grants cannot be written through the locked writer at all."""
    doc = full_doc()
    doc["runs"] = [{"id": "r1", "squad": "validator", "verdict": "PASS",
                    "agent": "harness-validator-lead", "code_grade": "n_a"}]
    problems = clean(doc)
    check("accepted_runs_item_code_grade_n_a", problems == [], problems)


def case_rejected_runs_item_code_grade_other_value():
    """The enum is CLOSED, and it agrees with check-state.sh's exact-match test: a
    document must never be schema-invalid and gate-exempt at once, in either direction.
    `graded` is rejected here and fires INV-6 there.

    The entry carries `agent` on purpose. Cycle 1's panel caught the first cut of this
    case passing VACUOUSLY: with `agent` omitted, the FEAT-31 positional rule raised a
    problem of its own, so the assertion stayed green with the enum deleted entirely.
    The value must be the ONLY defect, and the problem must NAME the key.
    """
    doc = full_doc()
    doc["runs"] = [{"id": "r1", "squad": "validator", "verdict": "PASS",
                    "agent": "harness-validator-lead", "code_grade": "graded"}]
    problems = clean(doc)
    named = any("code_grade" in p for p in problems)
    check("rejected_runs_item_code_grade_other_value",
          problems != [] and named, problems)


def case_rejected_runs_item_code_grade_case_variant():
    """`N_A` is the exact divergence the panel asked about (Q2): it must fail BOTH layers,
    since check-state.sh no longer case-folds. Non-vacuous for the same reason as above."""
    doc = full_doc()
    doc["runs"] = [{"id": "r1", "squad": "validator", "verdict": "PASS",
                    "agent": "harness-validator-lead", "code_grade": "N_A"}]
    problems = clean(doc)
    named = any("code_grade" in p for p in problems)
    check("rejected_runs_item_code_grade_case_variant",
          problems != [] and named, problems)


def case_rejected_undeclared_github_sub_key():
    doc = full_doc()
    doc["github"]["closed"] = True
    problems = clean(doc)
    named = any("'closed'" in p for p in problems)
    redirected = any(REDIRECT_SENTENCE in p for p in problems)
    check("rejected_undeclared_github_sub_key", problems != [] and named and redirected, problems)


def case_rejected_prose_key_reproducing_real_rot():
    doc = full_doc()
    doc["runs"] = [{"id": "r1", "squad": "code", "verdict": "PASS", "3 must_fix at med": "x"}]
    problems = clean(doc)
    named = any("3 must_fix at med" in p for p in problems)
    check("rejected_prose_key_runs_item", problems != [] and named, problems)


def case_rejected_status_shipped():
    doc = required_doc()
    doc["status"] = "shipped"
    problems = clean(doc)
    check("rejected_status_shipped", problems != [], problems)


def case_rejected_status_lowercase_done():
    doc = required_doc()
    doc["status"] = "done"
    problems = clean(doc)
    check("rejected_status_lowercase_done", problems != [], problems)


def case_rejected_pr_string_none():
    doc = required_doc()
    doc["pr"] = "none"
    problems = clean(doc)
    check("rejected_pr_string_none", problems != [], problems)


def case_cli_clean_file_exit_0():
    # Invoked via the shebang/exec bit directly — sys.executable is deliberately
    # NOT prepended here, unlike the other CLI cases, because CI's step and
    # T-04's verify both call this file as `.../validate-feature-json.py <path>`,
    # never as `python3 .../validate-feature-json.py <path>`.
    with tempfile.TemporaryDirectory() as td:
        path = write_json(td, "sample.json", full_doc())
        r = subprocess.run([VALIDATE_CLI, path], capture_output=True, text=True, timeout=30)
    check("cli_clean_file_exit_exactly_0", r.returncode == 0,
          f"exit={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")


def case_cli_invalid_file_exit_1():
    with tempfile.TemporaryDirectory() as td:
        doc = required_doc()
        del doc["branch"]
        path = write_json(td, "sample.json", doc)
        r = subprocess.run([VALIDATE_CLI, path], capture_output=True, text=True, timeout=30)
    check("cli_invalid_file_exit_exactly_1", r.returncode == 1,
          f"exit={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("cli_invalid_file_stderr_names_branch", "'branch'" in r.stderr, r.stderr)


def case_cli_jsonschema_unavailable_exit_3():
    with tempfile.TemporaryDirectory() as shadow_dir:
        write_file(shadow_dir, "jsonschema.py",
                   "raise ImportError('shadowed for FEAT-14 T-01 test')\n")
        env = dict(os.environ)
        env["PYTHONPATH"] = shadow_dir + os.pathsep + env.get("PYTHONPATH", "")
        with tempfile.TemporaryDirectory() as td:
            path = write_json(td, "sample.json", required_doc())
            r = subprocess.run(
                [sys.executable, VALIDATE_CLI, path],
                capture_output=True, text=True, env=env, timeout=30,
            )
    check("cli_jsonschema_unavailable_exit_exactly_3", r.returncode == 3,
          f"exit={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
    check("cli_jsonschema_unavailable_not_0_or_1", r.returncode not in (0, 1),
          f"exit={r.returncode}")
    check("cli_jsonschema_unavailable_stderr_names_required", "REQUIRED" in r.stderr,
          r.stderr)


def case_json_extension_rejects_yaml_content_yaml_extension_accepts_it():
    # Content that is valid YAML (block-style, unquoted keys) but NOT valid
    # JSON, and — importantly — is a COMPLETE valid document once parsed, so
    # the .yaml sibling actually validates clean rather than merely parsing.
    yaml_text = (
        "feature_id: FEAT-99-x\n"
        "branch: feat/99\n"
        "pr: null\n"
        "status: Building\n"
        "review_sha: none\n"
        "cycles_used: 0\n"
        "max_total_cycles: 8\n"
        "runs: []\n"
    )
    with tempfile.TemporaryDirectory() as td:
        json_path = write_file(td, "sample.json", yaml_text)
        yaml_path = write_file(td, "sample.yaml", yaml_text)

        json_problems = feature_schema.problems_for_file(json_path)
        yaml_problems = feature_schema.problems_for_file(yaml_path)

    named = any("JSON" in p or "json" in p for p in json_problems)
    check("json_extension_rejects_yaml_content", json_problems != [] and named,
          json_problems)
    check("yaml_extension_accepts_same_content", yaml_problems == [], yaml_problems)


def case_problems_for_text_names_real_display_path_in_every_line():
    display = ".harness/features/FEAT-99-x/feature.json"
    doc = required_doc()
    del doc["branch"]
    del doc["status"]
    problems = feature_schema.problems_for_text(json.dumps(doc), display)
    check("problems_for_text_at_least_two_problems", len(problems) >= 2, problems)
    check("problems_for_text_display_path_in_every_line",
          problems != [] and all(display in p for p in problems), problems)


def case_problems_for_text_jsonschema_forced_unavailable():
    original = feature_schema.JSONSCHEMA_AVAILABLE
    try:
        feature_schema.JSONSCHEMA_AVAILABLE = False
        problems = feature_schema.problems_for_text(json.dumps(full_doc()), "sample.json")
    finally:
        feature_schema.JSONSCHEMA_AVAILABLE = original
    check("forced_unavailable_returns_non_empty", problems != [], problems)
    check("forced_unavailable_single_line", len(problems) == 1, problems)
    check("forced_unavailable_names_required", "REQUIRED" in problems[0], problems)
    check("forced_unavailable_names_install_command",
          "pip install jsonschema" in problems[0], problems)


def case_migrated_depth_discovery_scans_the_segment_layout():
    """The no-argument sweep must examine a feature.json one segment deep - the CI
    backstop's only proof it still examines anything, since zero matches and a
    correct empty tree print the same exit code."""
    with tempfile.TemporaryDirectory() as tmp:
        fd = os.path.join(tmp, ".harness", "repoA", "features", "FEAT-77-x")
        os.makedirs(fd)
        with open(os.path.join(fd, "feature.json"), "w", encoding="utf-8") as f:
            json.dump(full_doc(), f)
        os.makedirs(os.path.join(tmp, ".harness"), exist_ok=True)
        open(os.path.join(tmp, ".harness", "team-config.yaml"), "w",
             encoding="utf-8").write("")
        env = dict(os.environ)
        env.pop("CLAUDE_PROJECT_DIR", None)
        env["HARNESS_PROJECT_DIR"] = tmp
        r = subprocess.run([VALIDATE_CLI], capture_output=True, text=True,
                           timeout=30, env=env)
        check("case_migrated_depth: the sweep reports ONE file, not zero",
              swept(r.stderr) == 1, r.stderr)
        check("case_migrated_depth: the scanning line names the migrated glob",
              ".harness/*/features/" in r.stderr, r.stderr)

        # MULTI-DIGIT ON PURPOSE (cycle-1 M2). The `== 1` assertion above passes
        # under a parser that only ever yields the last digit, because the fixture's
        # real count IS 1. Twelve cannot be reached by a last-digit or substring
        # break: "12 file(s)" yields 2 under such a mutant, and 2 != 12 reddens.
        for n in range(11):
            extra = os.path.join(tmp, ".harness", "repoA", "features", "FEAT-8%d-y" % n)
            os.makedirs(extra)
            with open(os.path.join(extra, "feature.json"), "w", encoding="utf-8") as f:
                json.dump(full_doc(), f)
        r12 = subprocess.run([VALIDATE_CLI], capture_output=True, text=True,
                             timeout=30, env=env)
        check("case_migrated_depth: a TWELVE-file sweep is counted as twelve, not two",
              swept(r12.stderr) == 12, r12.stderr)


def case_root_resolves_through_harness_boundary_not_the_retired_variable():
    """FEAT-42 T-05: discover_paths() resolves its root via
    harness_boundary.resolve_root, never the retired CLAUDE_PROJECT_DIR chain.

    CLAUDE_PROJECT_DIR alone must NOT redirect the sweep — this file's own docstring
    promises nothing here depends on any real file under .harness/*/features/*/, and
    the retired chain would have silently broken that promise by sweeping the real
    checkout instead of the tmp fixture whenever HARNESS_PROJECT_DIR was unset."""
    with tempfile.TemporaryDirectory() as tmp:
        fd = os.path.join(tmp, ".harness", "repoA", "features", "FEAT-77-x")
        os.makedirs(fd)
        with open(os.path.join(fd, "feature.json"), "w", encoding="utf-8") as f:
            json.dump(full_doc(), f)
        env = dict(os.environ)
        env.pop("HARNESS_PROJECT_DIR", None)
        env["CLAUDE_PROJECT_DIR"] = tmp
        r = subprocess.run([VALIDATE_CLI], capture_output=True, text=True,
                            timeout=30, env=env)
        # BIND THE PROPERTY, NOT A COUNT COINCIDENCE (cycle-1 M2). The property is
        # "the sweep did not take tmp as its root". Asserting `count != 1` inferred
        # that from a number, and was sensitive only because this repo happened to
        # hold 41 feature.json files — at 42, a last-digit mutant yields 2, `2 != 1`
        # holds, and the assertion goes vacuous with nothing announcing it. The
        # scanning line names its root, so test that directly: it is exact, and it
        # does not decay as the repository grows.
        check("case_root_resolves: CLAUDE_PROJECT_DIR alone does not redirect the sweep "
              "(scans the real repo root, not the tmp fixture with its single file)",
              swept(r.stderr) != 1 and tmp not in r.stderr, r.stderr)

        env2 = dict(os.environ)
        env2.pop("CLAUDE_PROJECT_DIR", None)
        env2["HARNESS_PROJECT_DIR"] = tmp
        os.makedirs(os.path.join(tmp, ".harness"), exist_ok=True)
        open(os.path.join(tmp, ".harness", "team-config.yaml"), "w",
             encoding="utf-8").write("")
        r2 = subprocess.run([VALIDATE_CLI], capture_output=True, text=True,
                             timeout=30, env=env2)
        check("case_root_resolves: HARNESS_PROJECT_DIR + team-config.yaml IS honoured",
              swept(r2.stderr) == 1 and tmp in r2.stderr, r2.stderr)


# ---------------------------------------------------------------------------
# FEAT-26 T-01 — github.source_issues, mirrored from plan.yaml's top-level
# source_issues by gh-sync.py open, read by gh-sync.py's `closes` renderer.
# Absent or empty is legal (D-08): no `required` change, no
# `additionalProperties` change at any level.
# ---------------------------------------------------------------------------


def case_accepted_source_issues_list_of_integers():
    doc = full_doc()
    doc["github"]["source_issues"] = [492, 501]
    problems = clean(doc)
    check("accepted_source_issues_list_of_integers", problems == [], problems)


def case_rejected_source_issues_non_integer():
    doc = full_doc()
    doc["github"]["source_issues"] = [492.5]
    problems = clean(doc)
    check("rejected_source_issues_non_integer", problems != [], problems)


def case_rejected_source_issues_quoted_number():
    doc = full_doc()
    doc["github"]["source_issues"] = ["492"]
    problems = clean(doc)
    check("rejected_source_issues_quoted_number", problems != [], problems)


def case_rejected_undeclared_sibling_of_source_issues():
    doc = full_doc()
    doc["github"]["source_issues"] = [492]
    doc["github"]["source_issue"] = 492
    problems = clean(doc)
    named = any("'source_issue'" in p for p in problems)
    check("rejected_undeclared_sibling_of_source_issues", problems != [] and named, problems)


def case_accepted_github_block_without_source_issues():
    doc = full_doc()
    doc["github"].pop("source_issues", None)
    problems = clean(doc)
    check("accepted_github_block_without_source_issues", problems == [], problems)


# ---------------------------------------------------------------------------
# SC-07's positional agent rule (FEAT-31 T-15). Read D-23.
#
# The two halves are in tension: a NEW entry omitting `agent` must be refused, and
# every feature.json already on disk must still validate. These cases assert BOTH,
# and the boundary case is the one that proves the rule bites at the right index.
# ---------------------------------------------------------------------------

# A feature name that is NOT in the frozen map, so its exempt count is 0 and its very
# first entry is required to carry the field. Asserted rather than assumed, because a
# name that turned out to be IN the map would make case A pass for the wrong reason.
T15_UNKNOWN_FEATURE = "FEAT-99-not-in-the-frozen-map"
# One that IS, read from the map itself so the fixture cannot drift from the source.
T15_KNOWN_FEATURE = "FEAT-10-software-factory"


def _t15_display(feature, root="/tmp/x"):
    return f"{root}/.harness/harness/features/{feature}/feature.json"


def _t15_doc(entries):
    d = full_doc()
    d["runs"] = entries
    return json.dumps(d)


def case_t15_refused_when_absent_from_map():
    """CASE A, REFUSED. A feature absent from the frozen map has exempt count 0, so
    its index-0 entry must carry `agent`. The TEXT is asserted, not merely the count:
    an unrelated problem would otherwise satisfy this case."""
    check("t15_unknown_feature_really_is_absent_from_the_map",
          T15_UNKNOWN_FEATURE not in feature_schema.RUNS_AGENT_EXEMPT,
          f"{T15_UNKNOWN_FEATURE} is in the map, so case A would prove nothing")
    probs = feature_schema.problems_for_text(
        _t15_doc([{"id": "r1", "squad": "code", "verdict": "PASS"}]),
        _t15_display(T15_UNKNOWN_FEATURE))
    hit = [p for p in probs if "runs[0]" in p and "'agent'" in p]
    check("t15_a_entry_without_agent_is_refused_and_names_index_and_key",
          len(hit) == 1, f"{probs}")


def case_t15_existing_entries_still_validate():
    """CASE B, THE OTHER HALF. A feature IN the map, with exactly exempt_count entries
    and none carrying `agent`, returns the EMPTY LIST — not merely something falsy.
    This is the half a schema `required` would have broken."""
    n = feature_schema.RUNS_AGENT_EXEMPT[T15_KNOWN_FEATURE]
    entries = [{"id": f"r{i}", "squad": "code", "verdict": "PASS"} for i in range(n)]
    probs = feature_schema.problems_for_text(_t15_doc(entries),
                                             _t15_display(T15_KNOWN_FEATURE))
    check("t15_b_all_legacy_entries_validate_with_no_agent",
          probs == [], f"{n} exempt entries produced {probs}")


def case_t15_boundary():
    """CASE C, THE BOUNDARY. exempt_count legacy entries plus ONE more, so the new
    entry's index EQUALS exempt_count. Exactly one problem, naming that index. This is
    what proves the rule bites at the boundary and not one entry late."""
    n = feature_schema.RUNS_AGENT_EXEMPT[T15_KNOWN_FEATURE]
    entries = [{"id": f"r{i}", "squad": "code", "verdict": "PASS"} for i in range(n + 1)]
    probs = feature_schema.problems_for_text(_t15_doc(entries),
                                             _t15_display(T15_KNOWN_FEATURE))
    check("t15_c_the_rule_bites_at_index_equal_to_the_exempt_count",
          len(probs) == 1 and f"runs[{n}]" in probs[0], f"n={n} {probs}")


def case_t15_accepted_with_the_field():
    """CASE D, ACCEPTED — and the check is on a VALUE, not on key presence. The same
    append carrying a non-empty agent validates; the same append carrying the EMPTY
    STRING is refused."""
    n = feature_schema.RUNS_AGENT_EXEMPT[T15_KNOWN_FEATURE]
    legacy = [{"id": f"r{i}", "squad": "code", "verdict": "PASS"} for i in range(n)]

    ok_doc = _t15_doc(legacy + [{"id": "new", "squad": "eng", "verdict": "PASS",
                                 "agent": "harness-backend-dev"}])
    check("t15_d_a_new_entry_naming_its_agent_validates",
          feature_schema.problems_for_text(ok_doc, _t15_display(T15_KNOWN_FEATURE)) == [],
          "a populated agent was still refused")

    empty_doc = _t15_doc(legacy + [{"id": "new", "squad": "eng", "verdict": "PASS",
                                    "agent": ""}])
    probs = feature_schema.problems_for_text(empty_doc, _t15_display(T15_KNOWN_FEATURE))
    check("t15_d_an_empty_agent_string_is_refused_so_the_check_is_on_the_value",
          len(probs) == 1 and f"runs[{n}]" in probs[0], f"{probs}")


def case_t15_red():
    """CASE E, RED PROOF. An exit status is never the proof (D-08). Copy
    feature_schema.py with the positional rule's call site removed, assert the text
    DIFFERS before running anything, and compare COUNTS on case A's fixture: original
    at least 1, mutant 0. Equal counts are INCONCLUSIVE and exit non-zero.

    THE MUTANT NEEDS THE ORIGINAL'S SCHEMA_PATH, and finding that out is the point.
    The first version of this proof reasoned that a tmpdir copy was safe because
    feature_schema imports only json, os and jsonschema, none of them relative. True
    of the IMPORTS and false of the module: SCHEMA_PATH is derived from
    os.path.dirname(os.path.abspath(__file__)), so the copy looked for
    feature-schema.json beside itself and raised FileNotFoundError. That is the third
    time on this feature that a mutant died for a reason unrelated to its mutation --
    FEAT-30's Q3, the behind-gate proof, and this. Overriding SCHEMA_PATH does not
    weaken the comparison, it is what makes it fair: both sides now validate against
    the identical schema, so the ONLY difference between them is the removed rule."""
    src_path = os.path.join(BIN_DIR, "feature_schema.py")
    src = open(src_path).read()
    needle = "    problems.extend(_runs_agent_problems(doc, display))\n"
    if needle not in src:
        check("t15_e_red_proof", False, "the rule's call site was not found")
        return
    mutant_text = src.replace(needle, "")
    if mutant_text == src:
        check("t15_e_red_proof", False, "INCONCLUSIVE — the mutation did not change the source")
        return

    import importlib.util
    with tempfile.TemporaryDirectory() as tmp:
        mpath = os.path.join(tmp, "mutant_feature_schema.py")
        with open(mpath, "w") as f:
            f.write(mutant_text)
        spec = importlib.util.spec_from_file_location("mutant_feature_schema", mpath)
        mutant = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mutant)
        mutant.SCHEMA_PATH = feature_schema.SCHEMA_PATH

        doc = _t15_doc([{"id": "r1", "squad": "code", "verdict": "PASS"}])
        display = _t15_display(T15_UNKNOWN_FEATURE)
        n_real = len(feature_schema.problems_for_text(doc, display))
        n_mut = len(mutant.problems_for_text(doc, display))
    check("t15_e_the_positional_rule_is_load_bearing",
          n_real >= 1 and n_mut == 0,
          f"INCONCLUSIVE — original {n_real}, mutant {n_mut}")
    print(f"     (red proof counts: original {n_real}, mutant {n_mut})")

def _tree_with_schema(root, extra_github_key=None):
    """A checkout-shaped tree with its OWN feature-schema.json under
    .agents/skills/harness/bin/, optionally declaring one extra key under `github`."""
    binp = os.path.join(root, ".claude", "skills", "harness", "bin")
    os.makedirs(binp, exist_ok=True)
    sch = json.loads(open(feature_schema.SCHEMA_PATH, encoding="utf-8").read())
    if extra_github_key:
        sch["properties"]["github"]["properties"][extra_github_key] = {
            "type": "array", "items": {"type": "integer"}}
    with open(os.path.join(binp, "feature-schema.json"), "w") as f:
        json.dump(sch, f)
    feat = os.path.join(root, ".harness", "harness", "features", "FEAT-T49")
    os.makedirs(feat, exist_ok=True)
    return os.path.join(feat, "feature.json")


def case_749_schema_comes_from_the_written_tree():
    """(#749) THE SCHEMA MUST COME FROM THE TREE THE FILE LIVES IN, NOT FROM THIS MODULE.

    MEASURED LIVE 2026-08-23 during FEAT-26's ship. `check-domain.sh --post` refused a
    legitimate write -- `undeclared key 'source_issues' at /github' -- because the key WAS
    declared in the worktree's own feature-schema.json and was NOT in main's, and the hook
    imports this module from CLAUDE_PROJECT_DIR, the main checkout.

    THE GENERAL SHAPE: a feature that ADDS a schema key cannot write data using that key
    until it merges, and cannot demonstrate the key working before it merges. The schema and
    the data land in one commit; the guard read them from two trees.

    `github` carries additionalProperties: false (DEC-191), so any new key under it hits
    this. FEAT-26 survived only because --post reports AFTER the write lands; a --pre route
    on the same rule blocks it outright."""
    with tempfile.TemporaryDirectory() as tmp:
        target = _tree_with_schema(tmp, extra_github_key="source_issues")
        doc = full_doc()
        doc["github"]["source_issues"] = [492]
        text = json.dumps(doc)
        probs = feature_schema.problems_for_text(text, "feature.json", for_path=target)
        check("case_749a: a key declared in the WRITTEN tree's schema is accepted",
              probs == [], repr(probs[:2]))


def case_749_guard_still_rejects_a_truly_undeclared_key():
    """(#749) GUARD -- the fix must not become "trust whatever tree you are in".

    Same tree, its schema NOT extended. An undeclared key must still be refused, or the
    fix degrades into no schema check at all for any worktree."""
    with tempfile.TemporaryDirectory() as tmp:
        target = _tree_with_schema(tmp)          # no extra key declared
        doc = full_doc()
        doc["github"]["invented_key"] = [1]
        probs = feature_schema.problems_for_text(json.dumps(doc), "feature.json",
                                                 for_path=target)
        check("case_749b: an UNDECLARED key is still rejected against the written tree",
              any("invented_key" in p for p in probs), repr(probs[:2]))


def case_749_falls_back_when_no_tree_schema_exists():
    """(#749) A path with no checkout schema above it falls back to this module's own, so
    every existing caller -- none of which passes for_path -- is unaffected.

    THE PROBE KEY IS SYNTHETIC ON PURPOSE. This case first used `source_issues`, the very
    key FEAT-26 adds -- green on main, and RED the moment FEAT-26 merged its schema change,
    because the module's own schema then declared it. Caught by the suite in FEAT-26's
    worktree before the merge. A fixture keyed on something under change grades the change,
    not the behaviour. `never_declared_anywhere` is declared by no schema in any tree."""
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, "feature.json")
        doc = full_doc()
        doc["github"]["never_declared_anywhere"] = [492]
        probs = feature_schema.problems_for_text(json.dumps(doc), "feature.json",
                                                 for_path=target)
        check("case_749c: with no tree schema, the module's own schema still governs",
              any("never_declared_anywhere" in p for p in probs), repr(probs[:2]))


def main():
    case_accepted_all_eleven_keys()
    case_accepted_only_eight_required_keys()
    case_accepted_omitting_one_optional_key()
    case_rejected_omitting_one_required_key()
    case_accepted_each_status_value()
    case_rejected_phase_is_gone()
    case_rejected_undeclared_top_level_key()
    case_rejected_undeclared_runs_item_key()
    case_accepted_runs_item_code_grade_n_a()
    case_rejected_runs_item_code_grade_other_value()
    case_rejected_runs_item_code_grade_case_variant()
    case_rejected_undeclared_github_sub_key()
    case_rejected_prose_key_reproducing_real_rot()
    case_rejected_status_shipped()
    case_rejected_status_lowercase_done()
    case_rejected_pr_string_none()
    case_cli_clean_file_exit_0()
    case_749_schema_comes_from_the_written_tree()
    case_749_guard_still_rejects_a_truly_undeclared_key()
    case_749_falls_back_when_no_tree_schema_exists()
    case_cli_invalid_file_exit_1()
    case_cli_jsonschema_unavailable_exit_3()
    case_json_extension_rejects_yaml_content_yaml_extension_accepts_it()
    case_problems_for_text_names_real_display_path_in_every_line()
    case_problems_for_text_jsonschema_forced_unavailable()
    case_migrated_depth_discovery_scans_the_segment_layout()
    case_root_resolves_through_harness_boundary_not_the_retired_variable()

    # FEAT-26 T-01 — github.source_issues
    case_accepted_source_issues_list_of_integers()
    case_rejected_source_issues_non_integer()
    case_rejected_source_issues_quoted_number()
    case_rejected_undeclared_sibling_of_source_issues()
    case_accepted_github_block_without_source_issues()

    # FEAT-31 T-15 — SC-07's positional agent rule.
    case_t15_refused_when_absent_from_map()
    case_t15_existing_entries_still_validate()
    case_t15_boundary()
    case_t15_accepted_with_the_field()
    case_t15_red()

    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        sys.exit(1)
    print("\nALL PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
