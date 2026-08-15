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
import subprocess
import sys
import tempfile

BIN_DIR = os.path.dirname(os.path.realpath(__file__))
if BIN_DIR not in sys.path:
    sys.path.insert(0, BIN_DIR)

REPO_ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.abspath(
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
        "runs": [{"id": "r1", "squad": "code", "verdict": "PASS"}],
        "max_total_runs": 10,
        "github": {
            "milestone": 1, "parent": 2, "parent_origin": "x",
            "attached": ["a"], "issues": {"T-01": 10},
        },
        "factory": {
            "repo": "r", "parent": 1, "parent_origin": "x",
            "issues": {}, "items": {}, "edges": {"parent": [], "blocked_by": {}},
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
        env = dict(os.environ)
        env["CLAUDE_PROJECT_DIR"] = tmp
        r = subprocess.run([VALIDATE_CLI], capture_output=True, text=True,
                           timeout=30, env=env)
        check("case_migrated_depth: the sweep reports ONE file, not zero",
              "1 file(s)" in r.stderr, r.stderr)
        check("case_migrated_depth: the scanning line names the migrated glob",
              ".harness/*/features/" in r.stderr, r.stderr)


def main():
    case_accepted_all_eleven_keys()
    case_accepted_only_eight_required_keys()
    case_accepted_omitting_one_optional_key()
    case_rejected_omitting_one_required_key()
    case_accepted_each_status_value()
    case_rejected_phase_is_gone()
    case_rejected_undeclared_top_level_key()
    case_rejected_undeclared_runs_item_key()
    case_rejected_undeclared_github_sub_key()
    case_rejected_prose_key_reproducing_real_rot()
    case_rejected_status_shipped()
    case_rejected_status_lowercase_done()
    case_rejected_pr_string_none()
    case_cli_clean_file_exit_0()
    case_cli_invalid_file_exit_1()
    case_cli_jsonschema_unavailable_exit_3()
    case_json_extension_rejects_yaml_content_yaml_extension_accepts_it()
    case_problems_for_text_names_real_display_path_in_every_line()
    case_problems_for_text_jsonschema_forced_unavailable()
    case_migrated_depth_discovery_scans_the_segment_layout()

    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        sys.exit(1)
    print("\nALL PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
