#!/usr/bin/env python3
"""Behavioral coverage for merge-gitignore.py through its real process boundary."""
from integration_support import ROOT, BIN
import contextlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from git_support import git as isolated_git, write_files

HERE = BIN
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


def each_rule_once(content):
    lines = content.splitlines()
    return all(lines.count(rule) == 1 for rule in RULES)


@contextlib.contextmanager
def project_target():
    """A fresh temp dir holding an empty project/ directory; yields (project, project/.gitignore)."""
    with tempfile.TemporaryDirectory() as directory:
        project = Path(directory) / "project"
        project.mkdir()
        yield project, project / ".gitignore"


def case_preserves_existing_content():
    with project_target() as (project, target):
        original = b"existing-first\n# distinctive existing comment\narchive/[abc]\nexisting-last\n"
        target.write_bytes(original)
        result = run(project)
        merged = target.read_bytes()
        require(result.returncode == 0, result.stderr)
        require(merged.startswith(original), "existing .gitignore bytes or order changed")
        require(each_rule_once(merged.decode("utf-8")), "harness rules were not each added once")


def case_check_complete_is_read_only():
    with project_target() as (project, target):
        original = ("complete-existing\n" + "\n".join(RULES) + "\n").encode()
        target.write_bytes(original)
        result = run(project, check=True)
        require(result.returncode == 0, result.stderr)
        require(target.read_bytes() == original, "complete --check modified .gitignore")


def case_check_incomplete_reports_missing_and_is_read_only():
    with project_target() as (project, target):
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
    with project_target() as (project, target):
        result = run(project)
        require(result.returncode == 0, result.stderr)
        require(target.exists(), "merge did not create an absent .gitignore")
        require(each_rule_once(target.read_text(encoding="utf-8")), "absent target did not receive every rule exactly once")


def case_partial_target_retains_present_rule_and_adds_missing_once():
    with project_target() as (project, target):
        present_rule = RULES[0]
        target.write_text("unrelated-keep\n%s\n" % present_rule, encoding="utf-8")
        result = run(project)
        content = target.read_text(encoding="utf-8")
        require(result.returncode == 0, result.stderr)
        require("unrelated-keep" in content.splitlines(), "partial target lost unrelated content")
        require(each_rule_once(content), "partial target has missing or duplicate harness rules")


def case_second_merge_is_byte_identical():
    with project_target() as (project, target):
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


# --- BUG-2399: non-UI run evidence is ordinary tracked material; only runs/*/ui/ stays out ---
REPO_GITIGNORE = ROOT / ".gitignore"
NARROW_RULE = ".harness/*/features/*/runs/*/ui/**"
LOCK_RULE = ".harness/**/*.lock"
BROAD_RULES = [".harness/features/*/runs/**", ".harness/*/features/*/runs/**"]
HISTORICAL_TARGETS = (("legacy", BROAD_RULES[:1]), ("namespaced", BROAD_RULES[1:]), ("both", list(BROAD_RULES)))
RUN_EVIDENCE = [
    "digest.md", "state.yaml", ".run-identity.json", "acceptance.md",
    "qa/manifest-unit.json", "qa/manifest-integration.json", "panel-c0.md", "altitude-ruling-c1.md",
]
RUN_EXCLUDED = ["ui/shot.webp", "ui/traces/trace.zip", "state.yaml.lock"]


def git(repo, *args):
    """Isolated git (git_support ENV: no system/global config, fixed identity) that also blanks
    core.excludesFile, so a developer's XDG ignore file cannot hide or expose run files."""
    return isolated_git(repo, "-c", "core.excludesFile=", *args, timeout=30).stdout


def z_paths(repo, *args):
    return set(filter(None, git(repo, *args, "-z").split("\0")))


def git_repo(path):
    """A fresh repo on main; identity comes from ENV and no global config can turn on signing."""
    path.mkdir(parents=True)
    git(path, "init", "-q", "-b", "main")
    return path


def seed_run(repo, run_dir, names):
    files = {(Path(run_dir) / name).as_posix(): ("evidence %s\n" % name).encode() for name in names}
    write_files(repo, files)
    return list(files)


def require_records_tracked_and_ui_excluded(repo, label):
    run_dir = ".harness/acme/features/FEAT-1-fixture/runs/r-1"
    evidence = seed_run(repo, run_dir, RUN_EVIDENCE)
    excluded = seed_run(repo, run_dir, RUN_EXCLUDED)
    git(repo, "add", "--", ".harness")
    staged = z_paths(repo, "diff", "--cached", "--name-only")
    missing = sorted(set(evidence) - staged)
    leaked = sorted(set(excluded) & staged)
    require(not missing, "BUG-2399 %s: ordinary git add left run evidence untracked: %r" % (label, missing))
    require(not leaked, "BUG-2399 %s: run UI or lock files were staged: %r" % (label, leaked))


def case_bug2399_repository_rules_track_run_records():
    with tempfile.TemporaryDirectory() as directory:
        repo = git_repo(Path(directory) / "repo")
        (repo / ".gitignore").write_bytes(REPO_GITIGNORE.read_bytes())
        require_records_tracked_and_ui_excluded(repo, "repository .gitignore")


def case_bug2399_fresh_install_tracks_run_records():
    with tempfile.TemporaryDirectory() as directory:
        repo = git_repo(Path(directory) / "repo")
        result = run(repo)
        require(result.returncode == 0, result.stderr)
        content = (repo / ".gitignore").read_text(encoding="utf-8").splitlines()
        require(NARROW_RULE in content and LOCK_RULE in content,
                "BUG-2399 fresh install lacks the run-UI or lock rule: %r" % content)
        require(not any(line.startswith("!") for line in content), "BUG-2399 fresh install ships a negation")
        require_records_tracked_and_ui_excluded(repo, "fresh snippet install")


def case_bug2399_check_reports_obsolete_broad_rules():
    for label, broad in HISTORICAL_TARGETS:
        with project_target() as (project, target):
            lines = ["custom-first"] + RULES + [NARROW_RULE, LOCK_RULE] + broad + ["custom-last"]
            original = ("\n".join(lines) + "\n").encode()
            target.write_bytes(original)
            result = run(project, check=True)
            require(result.returncode == 1, "BUG-2399 %s: --check accepted an obsolete broad run rule" % label)
            require(all(rule in result.stderr for rule in broad),
                    "BUG-2399 %s: --check did not name the obsolete rule: %r" % (label, result.stderr))
            require(target.read_bytes() == original, "BUG-2399 %s: --check modified .gitignore" % label)


def require_broad_rules_migrated(lines, label):
    """The merged lines drop every broad run rule, install the narrow UI rule once, write no
    negation, and keep the project's own lines in order."""
    require(not any(rule in lines for rule in BROAD_RULES), "BUG-2399 %s: broad run rule survived merge" % label)
    require(lines.count(NARROW_RULE) == 1, "BUG-2399 %s: narrow UI rule not installed once" % label)
    require(not any(line.startswith("!") for line in lines), "BUG-2399 %s: merge wrote a negation" % label)
    kept = [line for line in lines if line in ("custom-first", "# my run notes are ephemeral", "custom-last")]
    require(kept == ["custom-first", "# my run notes are ephemeral", "custom-last"],
            "BUG-2399 %s: unrelated project lines lost or reordered: %r" % (label, kept))


def case_bug2399_merge_replaces_broad_rules():
    for label, broad in HISTORICAL_TARGETS:
        with project_target() as (project, target):
            target.write_text("custom-first\n# my run notes are ephemeral\n%s\ncustom-last\n" % "\n".join(broad),
                              encoding="utf-8")
            first = run(project)
            after_first = target.read_bytes()
            require(first.returncode == 0, first.stderr)
            require_broad_rules_migrated(after_first.decode("utf-8").splitlines(), label)
            second = run(project)
            require(second.returncode == 0 and target.read_bytes() == after_first,
                    "BUG-2399 %s: second merge was not byte-identical" % label)
            require(run(project, check=True).returncode == 0, "BUG-2399 %s: --check red after migration" % label)


def case_bug2399_merge_corrects_shipped_rationale_only():
    with project_target() as (project, target):
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


def case_bug2399_line_endings_preserved():
    with project_target() as (project, target):
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
        require(NARROW_RULE.encode() + b"\n" in merged, "BUG-2399: narrow rule missing after unterminated input")


def seed_fleet_checkout(repo):
    """A fleet checkout on the old broad rules, holding historical evidence the rules hide."""
    (repo / ".gitignore").write_text("scratch-dir/\n%s\n%s\n" % tuple(BROAD_RULES), encoding="utf-8")
    (repo / "README.md").write_text("fleet\n", encoding="utf-8")
    git(repo, "add", "--", ".gitignore", "README.md")
    git(repo, "commit", "-qm", "base")
    fleet = ".harness/acme/features/FEAT-7-fleet/runs/"
    evidence = (seed_run(repo, fleet + "r 1", ["digest.md", "qa/manifest-unit.json"])
                + seed_run(repo, fleet + "r-2", ["panel-c0[*].md", "state.yaml"])
                + seed_run(repo, ".harness/features/FEAT-3-legacy/runs/r-3", ["digest.md"]))
    excluded = seed_run(repo, fleet + "r-2", ["ui/shot.webp", "digest.md.lock"]) + ["unrelated.txt"]
    (repo / "unrelated.txt").write_text("not evidence\n", encoding="utf-8")
    return evidence, excluded


def stage_reviewed_evidence(repo):
    """Checklist steps 4-5: review the exposed run files, stage them by literal path."""
    visible = z_paths(repo, "ls-files", "--others", "--exclude-standard")
    reviewed = sorted(path for path in visible if "/runs/" in path and "/ui/" not in path)
    git(repo, "--literal-pathspecs", "add", "--", ".gitignore", *reviewed)
    return reviewed, z_paths(repo, "diff", "--cached", "--name-only")


def require_operator_commit(repo, evidence, excluded, before):
    """Checklist step 6: the separate operator commit tracks exactly the reviewed evidence."""
    git(repo, "commit", "-qm", "operator: track historical run evidence")
    now = z_paths(repo, "ls-files")
    require(set(evidence) <= now and not set(excluded) & now,
            "BUG-2399 checklist: evidence untracked, or UI, lock or unrelated file tracked")
    require(all((repo / path).read_bytes() == data for path, data in before.items()),
            "BUG-2399 checklist: reviewed evidence bytes changed")


def case_bug2399_operator_checklist_commands_compose():
    """The checkout-upgrade checklist's command sequence, run as an operator would on a fleet checkout."""
    with tempfile.TemporaryDirectory() as directory:
        repo = git_repo(Path(directory) / "fleet")
        evidence, excluded = seed_fleet_checkout(repo)
        base_head = git(repo, "rev-parse", "HEAD")
        before = {path: (repo / path).read_bytes() for path in evidence}
        merged = run(repo)
        require(merged.returncode == 0, merged.stderr)
        reviewed, staged = stage_reviewed_evidence(repo)
        require(reviewed == sorted(evidence),
                "BUG-2399 checklist: narrowed rule did not expose exactly the historical evidence: %r" % reviewed)
        require(staged == set(evidence) | {".gitignore"}, "BUG-2399 checklist: staged set differs: %r" % sorted(staged))
        require(git(repo, "rev-parse", "HEAD") == base_head, "BUG-2399 checklist: merge or staging committed")
        require_operator_commit(repo, evidence, excluded, before)


CASES = [
    case_preserves_existing_content,
    case_check_complete_is_read_only,
    case_check_incomplete_reports_missing_and_is_read_only,
    case_absent_target_receives_each_rule_once,
    case_partial_target_retains_present_rule_and_adds_missing_once,
    case_second_merge_is_byte_identical,
    case_explicit_project_root_ignores_caller_cwd,
    case_bug2399_repository_rules_track_run_records,
    case_bug2399_fresh_install_tracks_run_records,
    case_bug2399_check_reports_obsolete_broad_rules,
    case_bug2399_merge_replaces_broad_rules,
    case_bug2399_merge_corrects_shipped_rationale_only,
    case_bug2399_line_endings_preserved,
    case_bug2399_operator_checklist_commands_compose,
]


def main():
    failures = 0
    for case in CASES:
        name = case.__name__[len("case_"):]
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
