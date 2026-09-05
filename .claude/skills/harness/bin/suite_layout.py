#!/usr/bin/env python3
"""Filesystem invariant for Harness's directory-driven test layout."""
import fnmatch
import os
import subprocess
from pathlib import Path

# Vocabulary for the repository-wide clause below. SOURCE_EXTENSIONS applies to
# RESTRICTED_NAME_PATTERNS only: an AGNOSTIC_NAME_PATTERNS match is test-shaped at any
# extension. Both tuples stay module-level and importable in their own right, beside
# is_test_shaped, because a later census imports the tuples without the extension filter.
RESTRICTED_NAME_PATTERNS = ("test-*", "test_*", "probe-*")
AGNOSTIC_NAME_PATTERNS = ("*_test.*", "*.test.*")
SOURCE_EXTENSIONS = (".py", ".sh", ".ts", ".tsx", ".js", ".mjs", ".cjs")

# Documented exceptions: exact relative path plus a written reason, never a glob.
# The registry polices itself in violations() below.
DOCUMENTED_EXCEPTIONS = (
    (
        ".harness/harness/features/FEAT-44-omp-context-advisory/evidence/"
        "probe-session-accessors.ts",
        "FEAT-44 evidence, the committed OMP extension that "
        "tests/manual/probe-omp-session-accessor.py loads; classified as evidence, "
        "not a test (BUG-1286 D-05).",
    ),
)


def is_test_shaped(path):
    """Return True when path's basename matches the test-shape vocabulary.

    The sole implementation of the vocabulary: the repository-wide clause and the
    registry self-policing clause in violations() both call this, and nothing else
    spells the expression inline."""
    basename = os.path.basename(path)
    if any(fnmatch.fnmatch(basename, pattern) for pattern in AGNOSTIC_NAME_PATTERNS):
        return True
    return (
        any(fnmatch.fnmatch(basename, pattern) for pattern in RESTRICTED_NAME_PATTERNS)
        and os.path.splitext(path)[1] in SOURCE_EXTENSIONS
    )


def tracked_paths(root):
    """Return a sorted tuple of POSIX-relative Git-tracked paths under root.

    Raises LookupError with a one-line reason if git is missing, exits non-zero,
    times out, or root is not the toplevel of its own Git index — the last check is
    what keeps a fixture root nested inside another checkout from being scanned
    against the outer index."""
    root = str(root)
    try:
        listed = subprocess.run(
            ["git", "ls-files", "-z"], cwd=root, text=True,
            capture_output=True, timeout=20)
    except FileNotFoundError as error:
        raise LookupError(f"git is not available: {error}") from error
    except subprocess.TimeoutExpired as error:
        raise LookupError(f"git ls-files timed out under {root}") from error
    if listed.returncode != 0:
        reason = next(iter(listed.stderr.splitlines()), "git ls-files failed")
        raise LookupError(reason)
    try:
        toplevel = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], cwd=root, text=True,
            capture_output=True, timeout=20)
    except FileNotFoundError as error:
        raise LookupError(f"git is not available: {error}") from error
    except subprocess.TimeoutExpired as error:
        raise LookupError(f"git rev-parse --show-toplevel timed out under {root}") from error
    if toplevel.returncode != 0:
        reason = next(iter(toplevel.stderr.splitlines()), "git rev-parse --show-toplevel failed")
        raise LookupError(reason)
    if os.path.realpath(toplevel.stdout.strip()) != os.path.realpath(root):
        raise LookupError(f"{root} is not the toplevel of its own Git index")
    return tuple(sorted(p for p in listed.stdout.split("\0") if p))


def _duplicate_or_malformed(rel, seen):
    """First two registry rules: reject a glob-shaped entry, then a repeat."""
    if any(ch in rel for ch in "*?["):
        return f"documented exception is not an exact path: {rel}"
    if rel in seen:
        return f"documented exception is listed twice: {rel}"
    return None


def _unnecessary_or_stale(rel, tracked):
    """Last two registry rules: reject an entry that isn't test-shaped outside
    tests/, then one no longer present in the tracked set."""
    if not is_test_shaped(rel) or rel.startswith("tests/"):
        return f"documented exception is unnecessary: {rel}"
    if tracked is not None and rel not in tracked:
        return f"documented exception is no longer tracked: {rel}"
    return None


def _entry_finding(rel, seen, tracked):
    """One entry's finding, if any. seen.add(rel) only happens once the entry
    has passed the malformed/duplicate rules, exactly as the single loop did."""
    finding = _duplicate_or_malformed(rel, seen)
    if finding is not None:
        return finding
    seen.add(rel)
    return _unnecessary_or_stale(rel, tracked)


def _registry_findings(tracked):
    """Registry self-policing over DOCUMENTED_EXCEPTIONS, sorted by entry path.

    Runs whether or not the index is available; only the last check needs it."""
    findings = []
    seen = set()
    for rel, _reason in sorted(DOCUMENTED_EXCEPTIONS, key=lambda entry: entry[0]):
        finding = _entry_finding(rel, seen, tracked)
        if finding is not None:
            findings.append(finding)
    return findings


def _unit_integration_findings(unit, integration):
    """Both suites are non-empty and share no test file name."""
    unit_tests = {p.name for p in unit.glob("test-*.py")}
    integration_tests = {p.name for p in integration.glob("test-*.py")}
    out = []
    if not unit_tests:
        out.append(f"{unit} contains no test-*.py")
    if not integration_tests:
        out.append(f"{integration} contains no test-*.py")
    for name in sorted(unit_tests & integration_tests):
        out.append(f"{name} appears in both {unit} and {integration}")
    return out


def _runner_selection_findings(tests_root, unit, integration):
    """Every test-shaped file under tests/ actually lives where the runner's
    own test-*.py glob under unit/ or integration/ will find it."""
    test_shapes = ("test-*.py", "test_*.py", "*_test.py")
    shaped_tests = {
        path
        for pattern in test_shapes
        for path in tests_root.rglob(pattern)
    }
    out = []
    for path in sorted(shaped_tests):
        if path.parent not in (unit, integration) or not path.match("test-*.py"):
            out.append(f"test file is not selected by the runner: {path}")
    return out


def _bin_planted(bin_dir):
    """Test-shaped files planted directly under bin/, sorted and deduplicated."""
    planted = []
    for pattern in ("test-*.py", "*.test.*", "probe-*"):
        planted.extend(bin_dir.glob(pattern))
    return sorted(set(planted))


def _bin_planted_findings(planted):
    return [f"test-shaped file remains under bin: {path}" for path in planted]


def _is_untracked_exclusion(rel, planted_rel, exception_paths):
    """True when rel is out of scope for the outside-tests rule: already
    under tests/, a bin-planted file, or a documented registry exception."""
    return (
        rel.startswith("tests/")
        or rel in planted_rel
        or rel in exception_paths
    )


def _tracked_outside_tests_findings(root, tracked, planted):
    exception_paths = {entry[0] for entry in DOCUMENTED_EXCEPTIONS}
    planted_rel = {p.relative_to(root).as_posix() for p in planted}
    return [
        f"tracked test-shaped file outside tests/: {rel}"
        for rel in sorted(tracked)
        if not _is_untracked_exclusion(rel, planted_rel, exception_paths)
        and is_test_shaped(rel)
    ]


def _tracked_scan(root, planted):
    """Every Git-tracked test-shaped file lives under tests/. Only runs once
    this checkout owns suite_layout.py itself: the Git-toplevel precondition
    lives inside tracked_paths() (D-03) and always resolves before the
    self-ownership test below, so a fixture root nested inside another
    checkout fails toplevel there and never reaches this function's own
    branch. Returns (findings, tracked) so the caller can still feed tracked
    -- possibly the real tuple, possibly None -- on to the registry."""
    if not os.path.exists(os.path.join(root, ".git")):
        return [], None
    try:
        tracked = tracked_paths(root)
    except LookupError as error:
        return [f"cannot enumerate tracked files under {root}: {error}"], None
    if ".claude/skills/harness/bin/suite_layout.py" not in tracked:
        return [], tracked
    return _tracked_outside_tests_findings(root, tracked, planted), tracked


def violations(root):
    root = Path(root)
    unit = root / "tests" / "unit"
    integration = root / "tests" / "integration"
    bin_dir = root / ".claude" / "skills" / "harness" / "bin"
    out = []
    out.extend(_unit_integration_findings(unit, integration))
    out.extend(_runner_selection_findings(root / "tests", unit, integration))
    planted = _bin_planted(bin_dir)
    out.extend(_bin_planted_findings(planted))
    scan_findings, tracked = _tracked_scan(root, planted)
    out.extend(scan_findings)
    out.extend(_registry_findings(tracked))
    return out
