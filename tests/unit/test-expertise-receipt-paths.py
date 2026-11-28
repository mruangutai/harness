#!/usr/bin/env python3
"""Unit tests for expertise-merge.py receipt_paths (FEAT-2641 T-06, D-04, DEC-262): receipts are
local working files read from the feature's notes with no git call and no base exclusion. Plain
script: one ok/FAIL line per check, exit 1 on any FAIL."""
import importlib.util
import os
import shutil
import sys
import tempfile

from unit_support import BIN

FAILS = []


def check(name, ok, detail=""):
    print(f"{'ok' if ok else 'FAIL'} {name}" + ("" if ok else f" | {detail}"))
    if not ok:
        FAILS.append(name)


def load():
    spec = importlib.util.spec_from_file_location("expertise_merge", os.path.join(BIN, "expertise-merge.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    em = load()
    check("receipt_paths exists", hasattr(em, "receipt_paths"))
    if not hasattr(em, "receipt_paths"):
        return
    root = tempfile.mkdtemp(prefix="receipt-paths-")
    try:
        fdir = os.path.join(root, ".harness", "harness", "features", "FEAT-0-probe")
        notes = os.path.join(fdir, "notes")
        os.makedirs(notes)
        names = ["expertise-receipt-" + "b" * 64 + ".json", "expertise-receipt-" + "a" * 64 + ".json"]
        for name in names + ["answers-run-1.md"]:
            with open(os.path.join(notes, name), "w", encoding="utf-8") as fh:
                fh.write("{}\n")
        got = em.receipt_paths(fdir)
        want = [os.path.join(notes, n) for n in sorted(names)]
        check("receipt_paths returns exactly the two receipts, sorted, as absolute paths",
              got == want and all(os.path.isabs(p) for p in got), got)
        other = os.path.join(root, ".harness", "harness", "features", "FEAT-1-empty")
        os.makedirs(other)
        check("receipt_paths is [] for an absent notes directory", em.receipt_paths(other) == [],
              em.receipt_paths(other))
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
    sys.exit(1 if FAILS else 0)
