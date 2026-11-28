#!/usr/bin/env python3
"""Behavioral coverage for merge-gitignore.py through its real process boundary."""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(_anchor_bin)
SCRIPT = Path(os.environ.get("MERGE_GITIGNORE_BIN", HERE / "merge-gitignore.py")).resolve()
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
        actual_missing_rules = {
            line[len("  - "):] for line in result.stderr.splitlines() if line.startswith("  - ")
        }
        expected_missing_rules = set(RULES[1:])
        require(
            actual_missing_rules == expected_missing_rules,
            "missing-rule bullets differ: missing=%r unexpected=%r"
            % (
                sorted(expected_missing_rules - actual_missing_rules),
                sorted(actual_missing_rules - expected_missing_rules),
            ),
        )
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
        caller_target = caller / ".gitignore"
        caller_target.write_bytes(b"caller-only-rule\n")
        caller_before = caller_target.read_bytes()
        result = run(project.resolve(), cwd=caller)
        require(result.returncode == 0, result.stderr)
        require((project / ".gitignore").exists(), "explicit project root was not updated")
        require(caller_target.read_bytes() == caller_before, "caller cwd .gitignore changed")


# --- DEC-260: notes/, runs/, observations/ and .harness/notes/ are local working files ---
REPO_GITIGNORE = Path(_anchor_root) / ".gitignore"
WORKING_RULES = [
    ".harness/*/features/*/notes/",
    ".harness/*/features/*/runs/",
    ".harness/*/features/*/observations/",
    ".harness/notes/",
]
LOCK_RULE = ".harness/**/*.lock"
OBSOLETE = [
    ".harness/features/*/runs/**",
    ".harness/*/features/*/runs/**",
    ".harness/*/features/*/runs/*/ui/**",
]
FEATURE = ".harness/acme/features/FEAT-1-fixture/"
WORKING_FILES = [
    FEATURE + "notes/answers.md", FEATURE + "notes/prototypes/FEAT-1-fixture/shot.png",
    FEATURE + "runs/r-1/digest.md", FEATURE + "runs/r-1/ui/shot.webp",
    FEATURE + "observations/a.md", ".harness/notes/project.md", FEATURE + "state.yaml.lock",
]
RECORD_FILES = [FEATURE + name for name in ("plan.yaml", "feature.json", "BRIEF.md", "STATE.md")]
PREVIOUS_HEADER = (
    "# --- harness ---\n"
    "# Run UI is never committed; every other run record is retained evidence (DEC-238)\n"
    "# and is committed with its feature. Everything else under .harness/ is committed\n"
    "# on purpose — it is the record of what shipped.\n"
)


def git(repo, *args):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return subprocess.run(["git", "-C", str(repo), "-c", "core.excludesFile=", *args], env=env,
                          capture_output=True, check=True, timeout=30).stdout


def git_repo(path):
    path.mkdir(parents=True)
    git(path, "init", "-q", "-b", "main")
    for key, value in (("user.email", "t@example.invalid"), ("user.name", "T"), ("commit.gpgsign", "false")):
        git(path, "config", key, value)
    return path


def require_record_tracked_and_working_files_excluded(repo, label):
    for rel in WORKING_FILES + RECORD_FILES:
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(("content %s\n" % rel).encode())
    git(repo, "add", "--", ".harness")
    staged = set(filter(None, git(repo, "diff", "--cached", "--name-only", "-z").decode().split("\0")))
    missing = sorted(set(RECORD_FILES) - staged)
    leaked = sorted(set(WORKING_FILES) & staged)
    require(not missing, "DEC-260 %s: ordinary git add left the record untracked: %r" % (label, missing))
    require(not leaked, "DEC-260 %s: working files or locks were staged: %r" % (label, leaked))


def case_repository_rules_exclude_working_files():
    with tempfile.TemporaryDirectory() as directory:
        repo = git_repo(Path(directory) / "repo")
        (repo / ".gitignore").write_bytes(REPO_GITIGNORE.read_bytes())
        require_record_tracked_and_working_files_excluded(repo, "repository .gitignore")


def case_fresh_install_excludes_working_files():
    with tempfile.TemporaryDirectory() as directory:
        repo = git_repo(Path(directory) / "repo")
        result = run(repo)
        require(result.returncode == 0, result.stderr)
        content = (repo / ".gitignore").read_text(encoding="utf-8").splitlines()
        require(all(rule in content for rule in WORKING_RULES + [LOCK_RULE]),
                "DEC-260 fresh install lacks a working-file or lock rule: %r" % content)
        require(not any(rule in content for rule in OBSOLETE), "DEC-260 fresh install ships an obsolete run rule")
        require(not any(line.startswith("!") for line in content), "DEC-260 fresh install ships a negation")
        require_record_tracked_and_working_files_excluded(repo, "fresh snippet install")


def obsolete_targets():
    """(label, file text): each obsolete rule alone outside a block, inside a block, and all three."""
    for rule in OBSOLETE:
        yield "outside %s" % rule, "custom-first\n# my run notes\n%s\ncustom-last\n" % rule
        yield "inside %s" % rule, ("custom-first\n# my run notes\ncustom-last\n\n"
                                   "# --- harness ---\n%s\n# --- end harness ---\n" % rule)
    yield "all three", "custom-first\n# my run notes\n%s\ncustom-last\n" % "\n".join(OBSOLETE)


def case_check_reports_obsolete_and_missing_and_is_read_only():
    for label, text in obsolete_targets():
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            project.mkdir()
            target = project / ".gitignore"
            original = text.encode()
            target.write_bytes(original)
            result = run(project, check=True)
            obsolete = {line[len("  x "):] for line in result.stderr.splitlines() if line.startswith("  x ")}
            missing = {line[len("  - "):] for line in result.stderr.splitlines() if line.startswith("  - ")}
            present = {rule for rule in OBSOLETE if rule in text.splitlines()}
            require(result.returncode == 1, "DEC-260 %s: --check accepted an obsolete run rule" % label)
            require(obsolete == present, "DEC-260 %s: obsolete bullets %r, want %r" % (label, obsolete, present))
            require(set(WORKING_RULES) <= missing,
                    "DEC-260 %s: --check did not name every working-file rule missing: %r" % (label, missing))
            require(target.read_bytes() == original, "DEC-260 %s: --check modified .gitignore" % label)


def case_check_names_all_three_obsolete_and_four_missing():
    with tempfile.TemporaryDirectory() as directory:
        project = Path(directory) / "project"
        project.mkdir()
        target = project / ".gitignore"
        others = [rule for rule in RULES if rule not in WORKING_RULES]
        original = ("\n".join(["custom-first"] + others + OBSOLETE + ["custom-last"]) + "\n").encode()
        target.write_bytes(original)
        result = run(project, check=True)
        obsolete = [line[len("  x "):] for line in result.stderr.splitlines() if line.startswith("  x ")]
        missing = [line[len("  - "):] for line in result.stderr.splitlines() if line.startswith("  - ")]
        require(result.returncode == 1, "DEC-260: --check exited %d, want 1" % result.returncode)
        require(obsolete == OBSOLETE, "DEC-260: obsolete bullets %r, want %r" % (obsolete, OBSOLETE))
        require(missing == WORKING_RULES, "DEC-260: missing bullets %r, want %r" % (missing, WORKING_RULES))
        require(target.read_bytes() == original, "DEC-260: --check modified .gitignore")


def case_merge_replaces_obsolete_rules():
    for label, text in obsolete_targets():
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "project"
            project.mkdir()
            target = project / ".gitignore"
            target.write_text(text, encoding="utf-8")
            first = run(project)
            after_first = target.read_bytes()
            lines = after_first.decode("utf-8").splitlines()
            require(first.returncode == 0, first.stderr)
            require(not any(rule in lines for rule in OBSOLETE), "DEC-260 %s: obsolete run rule survived merge" % label)
            require(all(lines.count(rule) == 1 for rule in WORKING_RULES),
                    "DEC-260 %s: working-file rules not installed once each" % label)
            require(not any(line.startswith("!") for line in lines), "DEC-260 %s: merge wrote a negation" % label)
            kept = [line for line in lines if line in ("custom-first", "# my run notes", "custom-last")]
            require(kept == ["custom-first", "# my run notes", "custom-last"],
                    "DEC-260 %s: unrelated project lines lost or reordered: %r" % (label, kept))
            second = run(project)
            require(second.returncode == 0 and target.read_bytes() == after_first,
                    "DEC-260 %s: second merge was not byte-identical" % label)
            require(run(project, check=True).returncode == 0, "DEC-260 %s: --check red after migration" % label)


def case_bug2399_merge_corrects_shipped_rationale_only():
    with tempfile.TemporaryDirectory() as directory:
        project = Path(directory) / "project"
        project.mkdir()
        target = project / ".gitignore"
        legacy_block = (
            "# --- harness ---\n"
            "# Run dirs are ephemeral; a dirty tree halts a team with BLOCKED, so these\n"
            "# must be ignored or the harness deadlocks itself. Everything else under\n"
            "# .harness/ is committed on purpose — it is the record of what shipped.\n"
            ".harness/features/*/runs/**\n"
            "# --- end harness ---\n"
        )
        target.write_text("# project: build dirs are ephemeral\nbuild/\n\n" + legacy_block, encoding="utf-8")
        result = run(project)
        content = target.read_text(encoding="utf-8")
        require(result.returncode == 0, result.stderr)
        require("Run dirs are ephemeral" not in content and "deadlocks itself" not in content,
                "BUG-2399: the shipped false run rationale survived merge:\n%s" % content)
        require(content.startswith("# project: build dirs are ephemeral\nbuild/\n"),
                "BUG-2399: project prose was rewritten:\n%s" % content)


def case_previous_header_rationale_removed():
    with tempfile.TemporaryDirectory() as directory:
        project = Path(directory) / "project"
        project.mkdir()
        target = project / ".gitignore"
        project_lines = "# project: Run UI is never committed; mine is\nbuild/\n\n"
        block = (PREVIOUS_HEADER + ".harness/*/features/*/runs/*/ui/**\n.harness/**/*.lock\nmy-project-rule\n"
                 "# --- end harness ---\n")
        target.write_text(project_lines + block, encoding="utf-8")
        result = run(project)
        content = target.read_text(encoding="utf-8")
        lines = content.splitlines()
        require(result.returncode == 0, result.stderr)
        stale = [line for line in PREVIOUS_HEADER.splitlines()[1:] if line in lines]
        require(not stale, "DEC-260: previous HEADER rationale survived merge: %r" % stale)
        require(content.startswith(project_lines), "DEC-260: project prose was rewritten:\n%s" % content)
        require("my-project-rule" in lines and LOCK_RULE in lines, "DEC-260: project line inside block lost:\n%s" % content)
        require(all(lines.count(rule) == 1 for rule in WORKING_RULES), "DEC-260: working-file rules not added once")


def case_bug2399_line_endings_preserved():
    with tempfile.TemporaryDirectory() as directory:
        project = Path(directory) / "project"
        project.mkdir()
        target = project / ".gitignore"
        target.write_bytes(b"crlf-first\r\n.harness/*/features/*/runs/**\r\ncrlf-last\r\n")
        result = run(project)
        merged = target.read_bytes()
        require(result.returncode == 0, result.stderr)
        require(merged.startswith(b"crlf-first\r\ncrlf-last\r\n"),
                "BUG-2399: CRLF project lines changed or broad rule kept: %r" % merged[:80])
        target.write_bytes(b"no-newline-first\n.harness/features/*/runs/**\nno-newline-last")
        result = run(project)
        merged = target.read_bytes()
        require(result.returncode == 0, result.stderr)
        require(merged.startswith(b"no-newline-first\nno-newline-last\n"),
                "BUG-2399: unterminated last line not preserved before appended rules: %r" % merged[:80])
        require(all(rule.encode() + b"\n" in merged for rule in WORKING_RULES),
                "DEC-260: working-file rules missing after unterminated input")


CASES = [
    ("preserves_existing_content", case_preserves_existing_content),
    ("check_complete_is_read_only", case_check_complete_is_read_only),
    ("check_incomplete_reports_missing_and_is_read_only", case_check_incomplete_reports_missing_and_is_read_only),
    ("absent_target_receives_each_rule_once", case_absent_target_receives_each_rule_once),
    ("partial_target_retains_present_rule_and_adds_missing_once", case_partial_target_retains_present_rule_and_adds_missing_once),
    ("second_merge_is_byte_identical", case_second_merge_is_byte_identical),
    ("explicit_project_root_ignores_caller_cwd", case_explicit_project_root_ignores_caller_cwd),
    ("repository_rules_exclude_working_files", case_repository_rules_exclude_working_files),
    ("fresh_install_excludes_working_files", case_fresh_install_excludes_working_files),
    ("check_reports_obsolete_and_missing_and_is_read_only", case_check_reports_obsolete_and_missing_and_is_read_only),
    ("check_names_all_three_obsolete_and_four_missing", case_check_names_all_three_obsolete_and_four_missing),
    ("merge_replaces_obsolete_rules", case_merge_replaces_obsolete_rules),
    ("bug2399_merge_corrects_shipped_rationale_only", case_bug2399_merge_corrects_shipped_rationale_only),
    ("previous_header_rationale_removed", case_previous_header_rationale_removed),
    ("bug2399_line_endings_preserved", case_bug2399_line_endings_preserved),
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
