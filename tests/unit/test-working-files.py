#!/usr/bin/env python3
"""Unit tests for bin/working_files.py (FEAT-2641 T-03 and T-11, DEC-262): the project-note path
contract, target ordering, clean's symlink, containment and refusal rules, and the untracked
working-file counts both removal gates share. Plain script: one ok/FAIL line per check, exit 1 on
any FAIL."""
import json
import os
import shutil
import subprocess
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
    """A .harness/harness/features/<name> directory with notes/, runs/, observations/ and
    scratch/ files, and feature.json listing `notes` as project_notes when given."""
    fdir = os.path.join(root, ".harness", "harness", "features", name)
    write(os.path.join(fdir, "notes", "n.md"))
    write(os.path.join(fdir, "runs", "r", "digest.md"))
    write(os.path.join(fdir, "observations", "o.md"))
    write(os.path.join(fdir, "scratch", "pytest.log"))
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
            os.path.join(fdir, "scratch"),
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
    check("targets with owner_root None lists the four directories",
          wf.targets(fdir, None) == [os.path.join(fdir, d) for d in wf.WORKING_DIRS])
    removed = wf.clean(fdir, None, emit=lambda _l: None)
    check("clean with owner_root None removes notes/, runs/, observations/ and scratch/",
          removed == [os.path.join(fdir, d) for d in wf.WORKING_DIRS]
          and not any(os.path.lexists(os.path.join(fdir, d)) for d in wf.WORKING_DIRS), removed)


def test_scratch(tmp):
    """T-12 (D-13): scratch/ is a working-file class - listed after observations/ and removed."""
    fdir = os.path.join(tmp, "scratch", ".harness", "harness", "features", "FEAT-0-probe")
    write(os.path.join(fdir, "notes", "x.md"))
    write(os.path.join(fdir, "observations", "o.md"))
    write(os.path.join(fdir, "scratch", "pytest.log"))
    got = wf.targets(fdir, None)
    check("T-12: targets lists scratch/ after observations/",
          got == [os.path.join(fdir, d) for d in ("notes", "observations", "scratch")], got)
    wf.clean(fdir, None, emit=lambda _l: None)
    check("T-12: clean removes scratch/", not os.path.lexists(os.path.join(fdir, "scratch")))


def _survives(fdir):
    return all(os.path.exists(os.path.join(fdir, d)) for d in wf.WORKING_DIRS)


def _features_link(tmp, name, target):
    """<tmp>/<name>/.harness/harness/features as a symlink to target; the feature path under it."""
    os.makedirs(os.path.join(tmp, name, ".harness", "harness"))
    os.symlink(target, os.path.join(tmp, name, ".harness", "harness", "features"))
    return os.path.join(tmp, name, ".harness", "harness", "features", "FEAT-0-probe")


def test_symlinked_ancestor_refuses(tmp):
    """must_fix 1: a feature directory reached through a symlinked ancestor (its features/
    directory) refuses, and the real working files it would reach elsewhere survive."""
    victim = feature(os.path.join(tmp, "victim-anc"))
    fdir = _features_link(tmp, "owner-anc", os.path.dirname(victim))
    check("a feature directory under a symlinked features/ ancestor raises",
          raises(wf.clean, fdir, None, emit=lambda _l: None))
    check("nothing is removed through the symlinked ancestor", _survives(victim))
    check("contained() raises on the symlinked ancestor", raises(wf.contained, fdir))


def test_symlinked_feature_dir_refuses(tmp):
    """must_fix 1: a feature directory that is itself a symlink refuses; contained() reads a real
    directory as True and an absent one as False."""
    victim = feature(os.path.join(tmp, "victim-leaf"))
    features = os.path.join(tmp, "owner-leaf", ".harness", "harness", "features")
    os.makedirs(features)
    os.symlink(victim, os.path.join(features, "FEAT-0-probe"))
    check("a feature directory that is itself a symlink raises",
          raises(wf.clean, os.path.join(features, "FEAT-0-probe"), None, emit=lambda _l: None))
    check("nothing is removed through the symlinked feature directory", _survives(victim))
    check("contained() is True for a real feature directory and False for an absent one",
          wf.contained(victim) is True
          and wf.contained(os.path.join(features, "FEAT-absent")) is False)


def _swapper(features, notes_parent, victim_features, outside):
    """An emit callback that, on its first call, swaps features/ and .harness/notes for symlinks
    to victim_features and outside, keeping the originals as <name>-orig."""
    def swap(_line):
        if os.path.islink(features):
            return
        os.rename(features, features + "-orig")
        os.symlink(victim_features, features)
        os.rename(notes_parent, notes_parent + "-orig")
        os.symlink(outside, notes_parent)
    return swap


def _swap_fixture(tmp):
    """(feature dir claiming .harness/notes/a.md, owner, victim feature dir, outside a.md): every
    path the swap case reads."""
    owner = os.path.join(tmp, "owner-swap")
    fdir = feature(owner, notes=[".harness/notes/a.md"])
    write(os.path.join(owner, ".harness", "notes", "a.md"))
    victim = feature(os.path.join(tmp, "victim-swap"))
    return fdir, owner, victim, write(os.path.join(tmp, "outside-swap", "a.md"))


def test_swap_after_validation(tmp):
    """must_fix 1: a features/ ancestor and a .harness/notes parent swapped for symlinks after
    clean has validated them do not redirect deletion: removal stays in the validated
    directories."""
    fdir, owner, victim, outside_note = _swap_fixture(tmp)
    features, notes_parent = os.path.dirname(fdir), os.path.join(owner, ".harness", "notes")
    swap = _swapper(features, notes_parent, os.path.dirname(victim), os.path.dirname(outside_note))
    try:
        wf.clean(fdir, owner, emit=swap)
    except (OSError, wf.WorkingFilesError) as exc:
        check("clean after a mid-run swap completes", False, repr(exc))
    check("a features/ ancestor swapped mid-clean does not redirect rmtree", _survives(victim))
    check("the validated feature directory's working files are the ones removed",
          not any(os.path.lexists(os.path.join(features + "-orig", "FEAT-0-probe", d))
                  for d in wf.WORKING_DIRS))
    check("a .harness/notes parent swapped mid-clean does not redirect unlink",
          os.path.exists(outside_note)
          and not os.path.lexists(os.path.join(notes_parent + "-orig", "a.md")))


def test_claims_dir(tmp):
    """must_fix 4: project-note claims come from claims_dir (the record that authorised the
    cleanup), not from the deletion copy's own, possibly stale, ledger."""
    owner = os.path.join(tmp, "owner-claims")
    stale = feature(os.path.join(owner, "wt"), notes=[".harness/notes/stale.md"])
    landed = feature(owner, notes=[".harness/notes/landed.md"])
    landed_note = write(os.path.join(owner, ".harness", "notes", "landed.md"))
    stale_note = write(os.path.join(owner, ".harness", "notes", "stale.md"))
    check("targets reads claims from claims_dir",
          wf.targets(stale, owner, claims_dir=landed)[-1:] == [landed_note],
          wf.targets(stale, owner, claims_dir=landed))
    wf.clean(stale, owner, emit=lambda _l: None, claims_dir=landed)
    check("clean removes the note the landed record claims and keeps the stale claim",
          not os.path.exists(landed_note) and os.path.exists(stale_note))


def _git(cwd, *args):
    subprocess.run(["git", "-C", cwd, "-c", "user.email=t@example.com", "-c", "user.name=T"]
                   + list(args), check=True, capture_output=True)


def test_untracked_counts(tmp):
    """T-11: one counting rule for GATE 2b and bash-write-guard."""
    repo = os.path.join(tmp, "counts")
    os.makedirs(repo)
    _git(repo, "init", "-q")
    rel = os.path.join(".harness", "harness", "features", "FEAT-0-probe")
    write(os.path.join(repo, rel, "observations", "tracked.md"))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "tracked observation")
    check("untracked_counts with no untracked working files is {}",
          wf.untracked_counts(repo, rel) == {}, wf.untracked_counts(repo, rel))
    write(os.path.join(repo, rel, "notes", "a.md"))
    write(os.path.join(repo, rel, "notes", "b.md"))
    write(os.path.join(repo, rel, "runs", "r", "digest.md"))
    got = wf.untracked_counts(repo, rel)
    check("untracked_counts counts untracked notes/ and runs/, never the tracked file",
          got == {"notes": 2, "runs": 1} and list(got) == ["notes", "runs"], got)
    write(os.path.join(repo, rel, "scratch", "pytest.log"))
    write(os.path.join(repo, rel, "scratch", "run.log"))
    got = wf.untracked_counts(repo, rel)
    check("T-12: untracked_counts counts two untracked scratch/ files",
          got.get("scratch") == 2, got)
    check("untracked_counts raises on a failing git",
          raises(wf.untracked_counts, os.path.join(tmp, "not-a-repo"), rel))


def test_untracked_undecodable_name(tmp):
    """T-11 fix c2 MF-1: a working-file name that is not valid UTF-8 is counted, never a
    UnicodeDecodeError: the one counting rule GATE 2b and bash-write-guard share. A `git` earlier
    on PATH adds the name to the real ls-files output, since APFS will not create it."""
    repo = os.path.join(tmp, "undecodable")
    os.makedirs(repo)
    _git(repo, "init", "-q")
    rel = ".harness/harness/features/FEAT-0-probe"
    write(os.path.join(repo, rel, "notes", "a.md"))
    bindir = os.path.join(tmp, "undecodable-bin")
    write(os.path.join(bindir, "git"),
          f'#!/bin/sh\n"{shutil.which("git")}" "$@"\nrc=$?\n'
          f'case " $* " in *" ls-files "*) printf \'{rel}/notes/\\377.md\\0\' ;; esac\nexit $rc\n')
    os.chmod(os.path.join(bindir, "git"), 0o755)
    saved = os.environ["PATH"]
    os.environ["PATH"] = bindir + os.pathsep + saved
    try:
        got = wf.untracked_counts(repo, rel)
    except UnicodeDecodeError as exc:
        got = f"UnicodeDecodeError: {exc}"
    finally:
        os.environ["PATH"] = saved
    check("untracked_counts counts a non-UTF-8 working-file name: notes 2",
          got == {"notes": 2}, got)


def main():
    tmp = tempfile.mkdtemp(prefix="working-files-test-")
    try:
        for test in (test_validator, test_targets, test_dry_run, test_symlinks,
                     test_directory_note_refuses, test_parent_symlink_refuses,
                     test_feature_directory, test_clean_command, test_owner_none,
                     test_scratch, test_symlinked_ancestor_refuses, test_symlinked_feature_dir_refuses,
                     test_swap_after_validation, test_claims_dir, test_untracked_counts,
                     test_untracked_undecodable_name):
            try:
                test(tmp)
            except Exception as exc:  # one broken case reports and the rest still run
                check(f"{test.__name__} ran", False, repr(exc))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
