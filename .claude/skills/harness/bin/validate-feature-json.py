#!/usr/bin/env python3
"""validate-feature-json.py — thin CLI over feature_schema.py (FEAT-14 D-03).

Argument parsing, printing and exit codes only — no schema logic lives here;
that is feature_schema.py's job, so check-domain.py can import the same
logic in process.

Usage:
  validate-feature-json.py [path ...]

With no arguments, sweeps every execution-state file on disk: globs
`.harness/*/features/*/feature.*` and keeps only the `.json`, `.yaml` and
`.yml` suffixes — never two literal filenames — because the corpus spans the
migration window from the old per-feature block-scalar execution-state
format to this JSON one (this schema is live before every file is
converted), and hard-coding a second filename naming the old format here
would redden a later corpus-wide sweep at the far end of the build.

Exit codes, three and distinct, because callers branch on them (T-03's CI
step, T-04's, T-07's and T-08's verify clauses all read the return code):
  0 - every file validates
  1 - at least one file failed validation, a verdict ABOUT a file
  3 - the checker could not run at all (jsonschema unimportable, or — with no
      arguments — the feature corpus could not be established), which is not a
      verdict about any file
"""
import glob
import os
import sys

BIN_DIR = os.path.dirname(os.path.abspath(__file__))
if BIN_DIR not in sys.path:
    sys.path.insert(0, BIN_DIR)

import feature_corpus
import feature_schema
import harness_boundary

KEEP_SUFFIXES = ("json", "yaml", "yml")


def discover_paths():
    """Every execution-state file the corpus holds: this checkout's own feature directories and,
    from a linked worktree, every landed one at the owner root (FEAT-1559) — a sparse worktree
    holds one directory, and validating one file is not validating the corpus. A broken layout
    or an unreadable corpus exits 3: the checker could not see what it was asked to check."""
    root = harness_boundary.resolve_root(BIN_DIR)
    refusal = feature_corpus.layout_refusal(root)
    if refusal is None:
        try:
            dirs = [e["path"] for e in feature_corpus.population(root)]
        except feature_corpus.CorpusError as exc:
            refusal = str(exc)
    if refusal is not None:
        print(f"validate-feature-json: cannot establish the feature corpus: {refusal}",
              file=sys.stderr)
        sys.exit(3)
    paths = sorted(
        p for d in dirs for p in glob.glob(os.path.join(d, "feature.*"))
        if p.rsplit(".", 1)[-1] in KEEP_SUFFIXES
    )
    # Naming the root and the count is what distinguishes a legitimate
    # zero-feature checkout from the wrong-directory defect — the same
    # reasoning check-plan-routes.py's discover_plans() states: a scan that
    # matches nothing must not look identical to a scan that ran and found a
    # clean corpus. This does not add a fourth exit code; exit stays 0.
    print(f"scanning the feature corpus at {root} "
          f"(.harness/*/features/*/feature.{{json,yaml,yml}}) — {len(paths)} file(s)",
          file=sys.stderr)
    return paths


def main(argv):
    if not feature_schema.JSONSCHEMA_AVAILABLE:
        # Checked BEFORE touching any path: exit 3 is a verdict about the
        # checker, not about any file, so it is decided before any file is
        # even looked at.
        sys.stderr.write(feature_schema.UNAVAILABLE_MESSAGE + "\n")
        sys.exit(3)

    paths = argv[1:] if len(argv) > 1 else discover_paths()

    any_problem = False
    for path in paths:
        for line in feature_schema.problems_for_file(path):
            print(line, file=sys.stderr)
            any_problem = True

    sys.exit(1 if any_problem else 0)


if __name__ == "__main__":
    main(sys.argv)
