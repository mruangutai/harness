"""working_files.py — the one owner of a feature's local working files and of the project-note
path contract (FEAT-2641 D-05, DEC-262).

A feature's notes/, runs/, observations/ and scratch/ directories (scratch/ holds raw
verification output, DEC-261), and the .harness/notes/ files its feature.json `project_notes`
list claims, are local working files: ignored, never committed, and removed once the feature
reaches a terminal station. Every cleaning caller - feature-worktree.py
clean and GATE 2b, gh-sync.py abandon, reject and skip-distill, plan-merge.py
set-feature-station and merge-gate.py merge-distill - goes through this module, so each deletes
the same bounded set and tells the operator the same retry command.

Cleanup never follows a symlink and stays physically inside the feature (DEC-262): a symlinked
working directory or project note is unlinked; a feature directory that is a symlink or sits
under one below its checkout, and a symlinked .harness/notes parent, refuse before anything is
removed; and every removal runs through the directory handles opened while validating, so a
parent swapped for a symlink afterwards cannot redirect it.
"""
import contextlib
import os
import re
import shutil
import stat
import subprocess
import sys

_BIN = os.path.dirname(os.path.abspath(__file__))
if _BIN not in sys.path:
    sys.path.insert(0, _BIN)

from feature_record import read as record_read  # noqa: E402

WORKING_DIRS = ("notes", "runs", "observations", "scratch")
PROJECT_NOTE_RE = re.compile(r"^\.harness/notes/(?!\.\.?$)[^/]+$")
_FEATURE_PATH_RE = re.compile(r"(?:^|/)\.harness/([^/]+)/features/([^/]+)$")
# <checkout>/.harness/[<segment>/]features/<id>: the flat layout plan-merge.py accepts included.
_LAYOUT_RE = re.compile(r"^(.*)/\.harness/((?:[^/]+/)?features/[^/]+)$")
_DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY


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


def _candidates(feature_dir, owner_root, claims_dir):
    dirs = [os.path.join(feature_dir, d) for d in WORKING_DIRS]
    notes = project_notes(feature_dir if claims_dir is None else claims_dir)
    return dirs, [os.path.join(owner_root, note) for note in notes]


def targets(feature_dir, owner_root, claims_dir=None):
    """Absolute paths that exist (lexists): notes/, runs/, observations/, scratch/, then each
    project note claims_dir (feature_dir when None) lists, under owner_root in list order.
    owner_root is unread when none is listed."""
    dirs, notes = _candidates(feature_dir, owner_root, claims_dir)
    return [p for p in dirs + notes if os.path.lexists(p)]


def _open_below(base, names):
    """A directory fd on base/<names...>. base itself may be reached through a symlink (a checkout
    may live under one); no name below it is followed. FileNotFoundError when an entry is absent;
    another OSError when one is a symlink or not a directory."""
    fd = os.open(base, _DIR_FLAGS)
    try:
        for name in names:
            child = os.open(name, _DIR_FLAGS | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
    except OSError:
        os.close(fd)
        raise
    return fd


def _pin(held, base, names, label):
    """_open_below's fd, closed when `held` (an ExitStack) unwinds; None when absent."""
    try:
        fd = _open_below(base, names)
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise WorkingFilesError(f"{label} is a symlink, sits under one, or is not a directory "
                                f"({exc.strerror}); nothing was removed") from exc
    held.callback(os.close, fd)
    return fd


def _pin_feature(held, feature_dir):
    """The pinned fd of feature_dir, opened from its checkout through .harness, the segment,
    features and the feature directory, none of them followed; None when absent."""
    match = _LAYOUT_RE.match(os.path.abspath(feature_dir).replace(os.sep, "/"))
    if not match:
        raise WorkingFilesError(f"{feature_dir} is not a .harness/<segment>/features/<id> "
                                f"directory; nothing was removed")
    names = [".harness"] + match.group(2).split("/")
    return _pin(held, match.group(1) or "/", names, feature_dir)


def contained(feature_dir):
    """True when feature_dir is a real directory reached from its checkout through real
    directories only; False when it is absent; WorkingFilesError when it or an ancestor below its
    checkout is a symlink or not a directory."""
    with contextlib.ExitStack() as held:
        return _pin_feature(held, feature_dir) is not None


def _present(dir_fd, parent, names):
    """(dir_fd, name, path, is_dir) for each name that exists in the pinned directory dir_fd,
    read without following a symlink."""
    found = []
    for name in names:
        try:
            mode = os.stat(name, dir_fd=dir_fd, follow_symlinks=False).st_mode
        except FileNotFoundError:
            continue
        found.append((dir_fd, name, os.path.join(parent, name), stat.S_ISDIR(mode)))
    return found


def _working_entries(held, feature_dir):
    fd = _pin_feature(held, feature_dir)
    return [] if fd is None else _present(fd, feature_dir, WORKING_DIRS)


def _note_entries(held, owner_root, notes):
    """The listed project notes present under the pinned owner .harness/notes; a listed note
    that is a real directory refuses."""
    if not notes:
        return []
    parent = os.path.join(owner_root, ".harness", "notes")
    fd = _pin(held, owner_root, (".harness", "notes"), parent)
    found = [] if fd is None else _present(fd, parent, [os.path.basename(n) for n in notes])
    for _fd, _name, path, is_dir in found:
        if is_dir:
            raise WorkingFilesError(f"listed project note {path} is a directory; nothing was removed")
    return found


def _remove_all(doomed, dry_run, emit):
    removed = []
    for dir_fd, name, path, is_dir in doomed:
        if dry_run:
            emit(f"would remove {path}")
            continue
        if is_dir:
            shutil.rmtree(name, dir_fd=dir_fd)
        else:
            os.unlink(name, dir_fd=dir_fd)
        removed.append(path)
        emit(f"removed {path}")
    return removed


def clean(feature_dir, owner_root, dry_run=False, emit=print, claims_dir=None):
    """Remove the feature's working files and the project notes claims_dir (feature_dir when
    None: the record that authorised the cleanup) lists, refusing before any removal on an
    uncontained feature directory or an unsafe project-note layout. Emits one line per target and
    returns the removed paths; an OSError propagates after the removals already emitted."""
    claims = feature_dir if claims_dir is None else claims_dir
    contained(claims)
    with contextlib.ExitStack() as held:
        doomed = (_working_entries(held, feature_dir)
                  + _note_entries(held, owner_root, project_notes(claims)))
        return _remove_all(doomed, dry_run, emit)


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


def untracked_counts(checkout, feature_rel):
    """{working dir: untracked file count} under feature_rel in checkout, nonzero counts only, in
    WORKING_DIRS order - the one counting rule feature-worktree.py GATE 2b and bash-write-guard.py
    share. Raises WorkingFilesError exactly when untracked does."""
    paths = untracked(checkout, feature_rel)
    counts = {d: sum(1 for p in paths if p.startswith(f"{feature_rel}/{d}/")) for d in WORKING_DIRS}
    return {d: n for d, n in counts.items() if n}


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
