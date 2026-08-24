#!/usr/bin/env python3
"""Behavioral coverage for merge-gitignore.sh through its real process boundary."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = Path(os.environ.get("MERGE_GITIGNORE_BIN", HERE / "merge-gitignore.sh")).resolve()
SNIPPET = HERE.parent / "templates" / "gitignore.snippet"
RULES = [
    line
    for line in SNIPPET.read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.lstrip().startswith("#")
]


def run(project, *, check=False, cwd=None):
    command = [str(SCRIPT), str(project)]
    if check:
        command.append("--check")
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def rule_counts(content):
    lines = content.splitlines()
    return {rule: lines.count(rule) for rule in RULES}


def case_preserves_existing_content():
    with tempfile.TemporaryDirectory() as directory:
        project = Path(directory) / "project"
        project.mkdir()
        target = project / ".gitignore"
        original = b"existing-first\n# distinctive existing comment\narchive/[abc]\nexisting-last\n"
        target.write_bytes(original)
        result = run(project)
        merged = target.read_bytes()
        require(result.returncode == 0, result.stderr)
        require(merged.startswith(original), "existing .gitignore bytes or order changed")
        require(all(count == 1 for count in rule_counts(merged.decode("utf-8")).values()), "harness rules were not each added once")


def case_check_complete_is_read_only():
    with tempfile.TemporaryDirectory() as directory:
        project = Path(directory) / "project"
        project.mkdir()
        target = project / ".gitignore"
        original = ("complete-existing\n" + "\n".join(RULES) + "\n").encode()
        target.write_bytes(original)
        result = run(project, check=True)
        require(result.returncode == 0, result.stderr)
        require(target.read_bytes() == original, "complete --check modified .gitignore")


def case_check_incomplete_reports_missing_and_is_read_only():
    with tempfile.TemporaryDirectory() as directory:
        project = Path(directory) / "project"
        project.mkdir()
        target = project / ".gitignore"
        original = ("incomplete-existing\n" + RULES[0] + "\n").encode()
        target.write_bytes(original)
        result = run(project, check=True)
        require(result.returncode == 1, "incomplete --check did not exit 1")
        for rule in RULES[1:]:
            require(rule in result.stderr, "missing rule absent from --check output: %s" % rule)
        require(target.read_bytes() == original, "incomplete --check modified .gitignore")


def case_absent_target_receives_each_rule_once():
    with tempfile.TemporaryDirectory() as directory:
        project = Path(directory) / "project"
        project.mkdir()
        target = project / ".gitignore"
        result = run(project)
        require(result.returncode == 0, result.stderr)
        require(target.exists(), "merge did not create an absent .gitignore")
        require(all(count == 1 for count in rule_counts(target.read_text(encoding="utf-8")).values()), "absent target did not receive every rule exactly once")


def case_partial_target_retains_present_rule_and_adds_missing_once():
    with tempfile.TemporaryDirectory() as directory:
        project = Path(directory) / "project"
        project.mkdir()
        target = project / ".gitignore"
        present_rule = RULES[0]
        target.write_text("unrelated-keep\n%s\n" % present_rule, encoding="utf-8")
        result = run(project)
        content = target.read_text(encoding="utf-8")
        require(result.returncode == 0, result.stderr)
        require("unrelated-keep" in content.splitlines(), "partial target lost unrelated content")
        require(all(count == 1 for count in rule_counts(content).values()), "partial target has missing or duplicate harness rules")


def case_second_merge_is_byte_identical():
    with tempfile.TemporaryDirectory() as directory:
        project = Path(directory) / "project"
        project.mkdir()
        target = project / ".gitignore"
        first = run(project)
        after_first = target.read_bytes()
        second = run(project)
        require(first.returncode == 0 and second.returncode == 0, first.stderr + second.stderr)
        require(target.read_bytes() == after_first, "second merge changed complete .gitignore bytes")


def case_explicit_project_root_ignores_caller_cwd():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        project = root / "project"
        caller = root / "unrelated-caller"
        project.mkdir()
        caller.mkdir()
        result = run(project.resolve(), cwd=caller)
        require(result.returncode == 0, result.stderr)
        require((project / ".gitignore").exists(), "explicit project root was not updated")
        require(not (caller / ".gitignore").exists(), "caller cwd unexpectedly gained .gitignore")


CASES = [
    ("preserves_existing_content", case_preserves_existing_content),
    ("check_complete_is_read_only", case_check_complete_is_read_only),
    ("check_incomplete_reports_missing_and_is_read_only", case_check_incomplete_reports_missing_and_is_read_only),
    ("absent_target_receives_each_rule_once", case_absent_target_receives_each_rule_once),
    ("partial_target_retains_present_rule_and_adds_missing_once", case_partial_target_retains_present_rule_and_adds_missing_once),
    ("second_merge_is_byte_identical", case_second_merge_is_byte_identical),
    ("explicit_project_root_ignores_caller_cwd", case_explicit_project_root_ignores_caller_cwd),
]


def main():
    failures = 0
    for name, case in CASES:
        try:
            case()
        except (AssertionError, OSError, subprocess.SubprocessError) as error:
            failures += 1
            print("FAIL %s: %s" % (name, error))
        else:
            print("PASS %s" % name)
    print("%d passed; %d failed" % (len(CASES) - failures, failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
