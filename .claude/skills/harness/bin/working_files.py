"""working_files.py — the one owner of a feature's local working files and of the project-note
path contract (FEAT-2641 D-05, DEC-260).

A feature's notes/, runs/ and observations/ directories, and the .harness/notes/ files its
feature.json `project_notes` list claims, are local working files: ignored, never committed, and
removed once the feature reaches a terminal station. Every cleaning caller - feature-worktree.py
clean and GATE 2b, gh-sync.py abandon, reject and skip-distill, plan-merge.py
set-feature-station and merge-gate.py merge-distill - goes through this module, so each deletes
the same bounded set and tells the operator the same retry command.

Cleanup never follows a symlink: a symlinked working directory or project note is unlinked, and
nothing under a symlinked or relocated .harness/notes parent is touched.
"""
import os
import re
import shutil
import subprocess
import sys

_BIN = os.path.dirname(os.path.abspath(__file__))
if _BIN not in sys.path:
    sys.path.insert(0, _BIN)

from feature_record import read as record_read  # noqa: E402

WORKING_DIRS = ("notes", "runs", "observations")
PROJECT_NOTE_RE = re.compile(r"^\.harness/notes/(?!\.\.?$)[^/]+$")
_FEATURE_PATH_RE = re.compile(r"(?:^|/)\.harness/([^/]+)/features/([^/]+)$")


class WorkingFilesError(Exception):
    """A working-file lookup or cleanup refused; nothing it guards was removed."""


def validate_project_note(value):
    """`value` when it is a `.harness/notes/<name>` path; WorkingFilesError otherwise. The one
    Python validator of the contract schemas/feature.json repeats as a pattern."""
    if isinstance(value, str) and PROJECT_NOTE_RE.match(value):
        return value
    raise WorkingFilesError(f"project note must be .harness/notes/<name>, got {value!r}")


def feature_directory(root, feature):
    """The one existing, non-symlinked `.harness/<segment>/features/<feature>` under
    realpath(root); WorkingFilesError naming the count otherwise."""
    real_root = os.path.realpath(root)
    harness_dir = os.path.join(real_root, ".harness")
    try:
        segments = sorted(os.listdir(harness_dir))
    except OSError:
        segments = []
    found = [p for p in (os.path.join(harness_dir, s, "features", feature) for s in segments
                         if os.path.isdir(os.path.join(harness_dir, s)))
             if os.path.isdir(p) and os.path.realpath(p) == p]
    if len(found) != 1:
        raise WorkingFilesError(f"feature {feature} has {len(found)} feature directories under "
                                f"{harness_dir}; exactly one is required")
    return found[0]


def project_notes(feature_dir):
    """The validated `project_notes` list of feature_dir/feature.json; [] when the file or the
    key is absent."""
    try:
        doc = record_read.load_feature_json(os.path.join(feature_dir, "feature.json"))
    except record_read.FeatureJsonError as exc:
        raise WorkingFilesError(str(exc)) from exc
    if doc is None or "project_notes" not in doc:
        return []
    notes = doc["project_notes"]
    if not isinstance(notes, list):
        raise WorkingFilesError(f"project_notes must be a list, got {notes!r}")
    return [validate_project_note(note) for note in notes]


def _candidates(feature_dir, owner_root):
    dirs = [os.path.join(feature_dir, d) for d in WORKING_DIRS]
    notes = project_notes(feature_dir)
    return dirs, [os.path.join(owner_root, note) for note in notes]


def targets(feature_dir, owner_root):
    """Absolute paths that exist (lexists): notes/, runs/, observations/, then each listed
    project note under owner_root in list order. owner_root is unread when none is listed."""
    dirs, notes = _candidates(feature_dir, owner_root)
    return [p for p in dirs + notes if os.path.lexists(p)]


def _refuse_unsafe_notes(owner_root, notes):
    parent = os.path.join(owner_root, ".harness", "notes")
    expected = os.path.join(os.path.realpath(owner_root), ".harness", "notes")
    if os.path.islink(parent) or os.path.realpath(parent) != expected:
        raise WorkingFilesError(f"{parent} is a symlink or resolves outside {owner_root}; "
                                f"nothing was removed")
    for path in notes:
        if os.path.isdir(path) and not os.path.islink(path):
            raise WorkingFilesError(f"listed project note {path} is a directory; nothing was removed")


def clean(feature_dir, owner_root, dry_run=False, emit=print):
    """Remove the feature's working files, refusing before any removal on an unsafe project-note
    layout. Emits one line per target and returns the removed paths; an OSError propagates
    after the removals already emitted."""
    dirs, notes = _candidates(feature_dir, owner_root)
    if notes:
        _refuse_unsafe_notes(owner_root, notes)
    removed = []
    for path in [p for p in dirs + notes if os.path.lexists(p)]:
        if dry_run:
            emit(f"would remove {path}")
            continue
        if path in dirs and not os.path.islink(path):
            shutil.rmtree(path)
        else:
            os.unlink(path)
        removed.append(path)
        emit(f"removed {path}")
    return removed


def untracked(checkout, feature_rel):
    """Untracked paths (ignored ones included, tracked ones never) under feature_rel's working
    directories in checkout."""
    argv = ["git", "-C", checkout, "ls-files", "-z", "--others", "--"]
    argv += [f"{feature_rel}/{d}" for d in WORKING_DIRS]
    try:
        r = subprocess.run(argv, capture_output=True, text=True)
    except OSError as exc:
        raise WorkingFilesError(f"git ls-files could not run in {checkout}: {exc}") from exc
    if r.returncode != 0:
        raise WorkingFilesError(f"git ls-files failed in {checkout}: {r.stderr.strip()}")
    return [p for p in r.stdout.split("\0") if p]


def clean_argv(feature_dir):
    """feature-worktree.py's argv that cleans this feature directory."""
    match = _FEATURE_PATH_RE.search(os.path.normpath(feature_dir).replace(os.sep, "/"))
    if not match:
        raise WorkingFilesError(f"{feature_dir} is not a .harness/<segment>/features/<id> directory")
    segment, feature = match.groups()
    import worktree_terminal
    repo = worktree_terminal.repo_arg_for_segment(segment) or segment
    return ["clean", "--repo", repo, "--id", feature, "--yes"]


def retry_command(feature_dir):
    """The operator command that cleans this feature directory."""
    return "python3 .claude/skills/harness/bin/feature-worktree.py " + " ".join(clean_argv(feature_dir))
