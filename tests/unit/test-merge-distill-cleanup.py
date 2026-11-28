#!/usr/bin/env python3
"""Unit tests for merge-gate.py's post-merge working-file cleanup (FEAT-2641 T-06, D-05, DEC-260):
_clean_after_merge never raises, and distill_main reports a merged distill whose cleanup failed
with exit 4, the clean command and no REFUSED line. Plain script: one ok/FAIL line per check,
exit 1 on any FAIL."""
import contextlib
import importlib.util
import io
import os
import shutil
import sys
import tempfile

from unit_support import BIN

FAILS = []
FEATURE = "FEAT-0-probe"


def check(name, ok, detail=""):
    print(f"{'ok' if ok else 'FAIL'} {name}" + ("" if ok else f" | {detail}"))
    if not ok:
        FAILS.append(name)


def load():
    spec = importlib.util.spec_from_file_location("merge_gate", os.path.join(BIN, "merge-gate.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextlib.contextmanager
def patched(obj, name, value):
    old = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, old)


def run_main(mg, evidence):
    out, err = io.StringIO(), io.StringIO()
    with patched(mg, "merge_distill", lambda root, feature, number: evidence), \
            contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = mg.distill_main(["merge-distill", "--root", "/nonexistent", "--feature", FEATURE, "--pr", "7"])
    return rc, out.getvalue(), err.getvalue()


def check_main(mg, label, evidence):
    rc, out, err = run_main(mg, evidence)
    check(f"{label}: distill_main returns 4", rc == 4, rc)
    check(f"{label}: prints MERGED, the clean command and 'do not re-run merge-distill', never REFUSED",
          f"MERGED {FEATURE} PR #7" in err and evidence["cleanup_retry"] in err
          and "do not re-run merge-distill" in err and "REFUSED" not in err + out, err)
    check(f"{label}: prints the evidence JSON", '"cleanup_error"' in out, out)


def evidence_of(result):
    removed, error, retry = result
    return {"merged": True, "feature": FEATURE, "pr": "7", "cleaned": removed,
            "cleanup_error": error, "cleanup_retry": retry}


def case_partial_oserror(mg, root):
    fdir = os.path.join(root, ".harness", "harness", "features", FEATURE)
    os.makedirs(fdir)
    gone = os.path.join(fdir, "notes")

    def clean(feature_dir, owner_root, dry_run=False, emit=print):
        emit(f"removed {gone}")
        raise OSError("disk said no")

    with patched(mg.working_files, "clean", clean), \
            patched(mg.feature_corpus, "owner_root", lambda r: r):
        result = mg._clean_after_merge(root, FEATURE)
    removed, error, retry = result
    check("OSError: removed path comes back", removed == [gone], removed)
    check("OSError: error text comes back", error is not None and "disk said no" in error, error)
    check("OSError: retry is the feature-worktree clean command",
          retry is not None and "feature-worktree.py clean" in retry and FEATURE in retry, retry)
    check_main(mg, "OSError", evidence_of(result))


def case_lookup_failures(mg, root):
    def no_dir(r, f):
        raise mg.working_files.WorkingFilesError("no feature directory probe")

    def no_owner(r):
        raise mg.feature_corpus.CorpusError("no owner probe")

    for label, obj, name, fake, needle in (
            ("WorkingFilesError", mg.working_files, "feature_directory", no_dir, "no feature directory probe"),
            ("CorpusError", mg.feature_corpus, "owner_root", no_owner, "no owner probe")):
        try:
            with patched(obj, name, fake):
                result = mg._clean_after_merge(root, FEATURE)
        except Exception as exc:  # noqa: BLE001 - the check is that nothing escapes
            check(f"{label}: _clean_after_merge does not raise", False, repr(exc))
            continue
        removed, error, retry = result
        check(f"{label}: error and retry command come back",
              removed == [] and error is not None and needle in error
              and retry is not None and "feature-worktree.py clean" in retry and FEATURE in retry, result)
        check_main(mg, label, evidence_of(result))


def main():
    mg = load()
    check("_clean_after_merge exists", hasattr(mg, "_clean_after_merge"))
    if not hasattr(mg, "_clean_after_merge"):
        return
    root = os.path.realpath(tempfile.mkdtemp(prefix="merge-distill-cleanup-"))
    try:
        case_partial_oserror(mg, root)
        case_lookup_failures(mg, root)
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
    sys.exit(1 if FAILS else 0)
