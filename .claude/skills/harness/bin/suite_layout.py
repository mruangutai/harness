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


def _registry_findings(tracked):
    """Registry self-policing over DOCUMENTED_EXCEPTIONS, sorted by entry path.

    Runs whether or not the index is available; only the last check needs it."""
    findings = []
    seen = set()
    for rel, _reason in sorted(DOCUMENTED_EXCEPTIONS, key=lambda entry: entry[0]):
        if any(ch in rel for ch in "*?["):
            findings.append(f"documented exception is not an exact path: {rel}")
            continue
        if rel in seen:
            findings.append(f"documented exception is listed twice: {rel}")
            continue
        seen.add(rel)
        if not is_test_shaped(rel) or rel.startswith("tests/"):
            findings.append(f"documented exception is unnecessary: {rel}")
            continue
        if tracked is not None and rel not in tracked:
            findings.append(f"documented exception is no longer tracked: {rel}")
    return findings


def violations(root):
    root = Path(root)
    unit = root / "tests" / "unit"
    integration = root / "tests" / "integration"
    bin_dir = root / ".claude" / "skills" / "harness" / "bin"
    unit_tests = {p.name for p in unit.glob("test-*.py")}
    integration_tests = {p.name for p in integration.glob("test-*.py")}
    out = []
    if not unit_tests:
        out.append(f"{unit} contains no test-*.py")
    if not integration_tests:
        out.append(f"{integration} contains no test-*.py")
    for name in sorted(unit_tests & integration_tests):
        out.append(f"{name} appears in both {unit} and {integration}")
    test_shapes = ("test-*.py", "test_*.py", "*_test.py")
    shaped_tests = {
        path
        for pattern in test_shapes
        for path in (root / "tests").rglob(pattern)
    }
    for path in sorted(shaped_tests):
        if path.parent not in (unit, integration) or not path.match("test-*.py"):
            out.append(f"test file is not selected by the runner: {path}")
    planted = []
    for pattern in ("test-*.py", "*.test.*", "probe-*"):
        planted.extend(bin_dir.glob(pattern))
    for path in sorted(set(planted)):
        out.append(f"test-shaped file remains under bin: {path}")
    tracked = None
    if os.path.exists(os.path.join(root, ".git")):
        try:
            tracked = tracked_paths(root)
        except LookupError as error:
            out.append(f"cannot enumerate tracked files under {root}: {error}")
        else:
            if ".claude/skills/harness/bin/suite_layout.py" in tracked:
                planted_rel = {p.relative_to(root).as_posix() for p in set(planted)}
                exception_paths = {entry[0] for entry in DOCUMENTED_EXCEPTIONS}
                for rel in sorted(tracked):
                    if rel.startswith("tests/"):
                        continue
                    if rel in planted_rel:
                        continue
                    if rel in exception_paths:
                        continue
                    if not is_test_shaped(rel):
                        continue
                    out.append(f"tracked test-shaped file outside tests/: {rel}")
    out.extend(_registry_findings(tracked))
    return out
