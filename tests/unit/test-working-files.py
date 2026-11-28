#!/usr/bin/env python3
"""Unit tests for bin/working_files.py (FEAT-2641 T-03, DEC-260): the project-note path
contract, target ordering, and clean's symlink and refusal rules. Plain script: one ok/FAIL line
per check, exit 1 on any FAIL."""
import json
import os
import shutil
import sys
import tempfile

from unit_support import BIN  # noqa: F401  (puts bin/ on sys.path)
import working_files as wf  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(f"{'ok' if ok else 'FAIL'} {name}" + ("" if ok else f" | {detail}"))
    if not ok:
        FAILS.append(name)


def write(path, text="x\n"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def feature(root, name="FEAT-0-probe", notes=None):
    """A .harness/harness/features/<name> directory with notes/, runs/ and observations/ files,
    and feature.json listing `notes` as project_notes when given."""
    fdir = os.path.join(root, ".harness", "harness", "features", name)
    write(os.path.join(fdir, "notes", "n.md"))
    write(os.path.join(fdir, "runs", "r", "digest.md"))
    write(os.path.join(fdir, "observations", "o.md"))
    doc = {} if notes is None else {"project_notes": notes}
    write(os.path.join(fdir, "feature.json"), json.dumps(doc))
    return fdir


def raises(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except wf.WorkingFilesError:
        return True
    return False


BAD = ["/abs.md", ".harness/notes/../x.md", ".harness/notes/a/b.md", "notes/x.md",
       ".harness/notes/..", 7]
GOOD = ".harness/notes/grilling-x-2026-01-01.md"


def test_validator(tmp):
    for value in BAD:
        check(f"validate_project_note rejects {value!r}", raises(wf.validate_project_note, value))
        fdir = os.path.join(tmp, f"v{BAD.index(value)}")
        write(os.path.join(fdir, "feature.json"), json.dumps({"project_notes": [value]}))
        check(f"project_notes rejects {value!r}", raises(wf.project_notes, fdir))
    check("validate_project_note accepts a grilling note", wf.validate_project_note(GOOD) == GOOD)
    fdir = os.path.join(tmp, "good")
    write(os.path.join(fdir, "feature.json"), json.dumps({"project_notes": [GOOD]}))
    check("project_notes returns the listed note", wf.project_notes(fdir) == [GOOD])
    nokey = os.path.join(tmp, "nokey")
    write(os.path.join(nokey, "feature.json"), "{}")
    check("project_notes: absent key gives []", wf.project_notes(nokey) == [])
    check("project_notes: absent feature.json gives []",
          wf.project_notes(os.path.join(tmp, "nothing")) == [])


def test_targets(tmp):
    owner = os.path.join(tmp, "owner")
    fdir = feature(owner, notes=[".harness/notes/b.md", ".harness/notes/a.md",
                                 ".harness/notes/missing.md"])
    write(os.path.join(owner, ".harness", "notes", "a.md"))
    write(os.path.join(owner, ".harness", "notes", "b.md"))
    shutil.rmtree(os.path.join(fdir, "runs"))
    got = wf.targets(fdir, owner)
    want = [os.path.join(fdir, "notes"), os.path.join(fdir, "observations"),
            os.path.join(owner, ".harness/notes/b.md"), os.path.join(owner, ".harness/notes/a.md")]
    check("targets: order and lexists filtering", got == want, got)


def test_dry_run(tmp):
    owner = os.path.join(tmp, "owner-dry")
    fdir = feature(owner, notes=[".harness/notes/a.md"])
    note = write(os.path.join(owner, ".harness", "notes", "a.md"))
    lines = []
    removed = wf.clean(fdir, owner, dry_run=True, emit=lines.append)
    check("dry_run removes nothing",
          removed == [] and all(os.path.exists(os.path.join(fdir, d)) for d in wf.WORKING_DIRS)
          and os.path.exists(note), removed)
    check("dry_run emits would remove per target",
          lines == [f"would remove {p}" for p in wf.targets(fdir, owner)], lines)


def test_symlinks(tmp):
    owner = os.path.join(tmp, "owner-link")
    fdir = feature(owner, notes=[".harness/notes/link.md"])
    outside = os.path.join(tmp, "outside-dir")
    kept = write(os.path.join(outside, "keep.md"))
    shutil.rmtree(os.path.join(fdir, "notes"))
    os.symlink(outside, os.path.join(fdir, "notes"))
    target_file = write(os.path.join(tmp, "outside-note.md"))
    os.makedirs(os.path.join(owner, ".harness", "notes"), exist_ok=True)
    os.symlink(target_file, os.path.join(owner, ".harness", "notes", "link.md"))
    lines = []
    wf.clean(fdir, owner, emit=lines.append)
    check("a notes symlink to an outside directory is unlinked",
          not os.path.lexists(os.path.join(fdir, "notes")), lines)
    check("the outside directory's file survives", os.path.exists(kept))
    check("a listed project-note symlink is unlinked",
          not os.path.lexists(os.path.join(owner, ".harness", "notes", "link.md")))
    check("the project-note symlink's target survives", os.path.exists(target_file))


def test_directory_note_refuses(tmp):
    owner = os.path.join(tmp, "owner-dir")
    fdir = feature(owner, notes=[".harness/notes/d.md"])
    write(os.path.join(owner, ".harness", "notes", "d.md", "unlisted.md"))
    check("a listed project note that is a directory raises",
          raises(wf.clean, fdir, owner, emit=lambda _l: None))
    check("nothing is removed, notes/ included",
          all(os.path.exists(os.path.join(fdir, d)) for d in wf.WORKING_DIRS)
          and os.path.exists(os.path.join(owner, ".harness", "notes", "d.md", "unlisted.md")))


def test_parent_symlink_refuses(tmp):
    owner = os.path.join(tmp, "owner-parent")
    fdir = feature(owner, notes=[".harness/notes/a.md"])
    outside = os.path.join(tmp, "outside-notes")
    victim = write(os.path.join(outside, "a.md"))
    os.symlink(outside, os.path.join(owner, ".harness", "notes"))
    check("an owner .harness/notes symlink raises",
          raises(wf.clean, fdir, owner, emit=lambda _l: None))
    check("nothing is removed under a symlinked notes parent",
          os.path.exists(victim)
          and all(os.path.exists(os.path.join(fdir, d)) for d in wf.WORKING_DIRS))


def test_feature_directory(tmp):
    zero = os.path.join(tmp, "fd-zero")
    os.makedirs(os.path.join(zero, ".harness", "harness", "features"))
    check("feature_directory with zero matches raises", raises(wf.feature_directory, zero, "FEAT-1"))
    two = os.path.join(tmp, "fd-two")
    for seg in ("harness", "kaya"):
        os.makedirs(os.path.join(two, ".harness", seg, "features", "FEAT-1"))
    check("feature_directory with two matches raises", raises(wf.feature_directory, two, "FEAT-1"))
    one = os.path.join(tmp, "fd-one")
    os.makedirs(os.path.join(one, ".harness", "harness", "features", "FEAT-1"))
    got = wf.feature_directory(one, "FEAT-1")
    check("feature_directory with one match returns it",
          got == os.path.join(os.path.realpath(one), ".harness", "harness", "features", "FEAT-1"), got)


def test_clean_command(tmp):
    fdir = os.path.join(tmp, "cc", ".harness", "harness", "features", "FEAT-0-probe")
    os.makedirs(fdir)
    argv = ["clean", "--repo", "harness", "--id", "FEAT-0-probe", "--yes"]
    check("clean_argv for a harness feature", wf.clean_argv(fdir) == argv, wf.clean_argv(fdir))
    check("retry_command is the feature-worktree.py clean command",
          wf.retry_command(fdir) == "python3 .claude/skills/harness/bin/feature-worktree.py "
          + " ".join(argv), wf.retry_command(fdir))


def test_owner_none(tmp):
    fdir = feature(os.path.join(tmp, "none"))
    check("targets with owner_root None lists the three directories",
          wf.targets(fdir, None) == [os.path.join(fdir, d) for d in wf.WORKING_DIRS])
    removed = wf.clean(fdir, None, emit=lambda _l: None)
    check("clean with owner_root None removes notes/, runs/ and observations/",
          removed == [os.path.join(fdir, d) for d in wf.WORKING_DIRS]
          and not any(os.path.lexists(os.path.join(fdir, d)) for d in wf.WORKING_DIRS), removed)


def main():
    tmp = tempfile.mkdtemp(prefix="working-files-test-")
    try:
        for test in (test_validator, test_targets, test_dry_run, test_symlinks,
                     test_directory_note_refuses, test_parent_symlink_refuses,
                     test_feature_directory, test_clean_command, test_owner_none):
            test(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
