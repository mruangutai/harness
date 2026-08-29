#!/usr/bin/env python3
"""Anchor-rot checker for .harness/harness/docs/DECISIONS.md — no model in it.

Every citation of the form `<file>:<line>` or `<file>:<line>-<line>` in the target
document is an ANCHOR. This checker asserts exactly two things about each anchor,
and two things only:

  1. the named file exists in the tree, resolved by BASENAME against `git ls-files`
     so an anchor written relative to a subdirectory still resolves;
  2. the first line number is within that file's line count.

It deliberately does NOT store or compare snippets: existence plus range already
finds real rot at zero authoring cost, and a snippet still cannot see a line that
exists and now says something unrelated — that is the executable-claims checker's
job (a different tool), not this one's.

Usage:
    check-decision-anchors.py            check .harness/harness/docs/DECISIONS.md,
                                          resolved the same way gen-decisions-index.py
                                          resolves its default target
    check-decision-anchors.py --file P   check P instead

Exit codes: 0 no failing anchors, 1 at least one failing anchor, 2 a usage error or
an unreadable target. Never 0 on a target it could not read — an empty result and a
successful result must not look the same.
"""
import argparse
import os
import re
import subprocess
import sys

import harness_boundary

_BIN_DIR = os.path.dirname(os.path.abspath(__file__))

# Mirrors gen-decisions-index.py's own DOCS_DIR/DECISIONS_PATH constants exactly —
# the default target is the same file, resolved the same way, never a second guess.
DOCS_DIR = os.path.join(".harness", "harness", "docs")
DECISIONS_REL_PATH = os.path.join(DOCS_DIR, "DECISIONS.md")

# The anchor grammar: a backtick, a path of word characters/dots/slashes/hyphens
# ending in a known source extension, a colon, a line number, optionally a hyphen
# and a second line number, then the closing backtick.
ANCHOR_RE = re.compile(
    r"`([\w./-]+\.(?:py|sh|md|json|yaml|yml|ts|toml)):(\d+)(?:-\d+)?`"
)


def default_target():
    """The default --file value, resolved at CALL time (never at import time) so
    an explicit --file always wins and nothing here is fixed before argv is read.

    Reuses gen-decisions-index.py's own root resolution — harness_boundary.resolve_root
    from this script's directory — rather than hand-rolling a second one.
    """
    project_dir = harness_boundary.resolve_root(_BIN_DIR)
    return os.path.join(project_dir, DECISIONS_REL_PATH)


def extract_anchors(text):
    """[(raw_anchor_text, cited_path, first_line_number), ...] in document order."""
    return [
        (m.group(0), m.group(1), int(m.group(2)))
        for m in ANCHOR_RE.finditer(text)
    ]


def git_tracked_basenames():
    """basename -> [tracked path, ...], from `git ls-files` in the current tree.

    Runs in the inherited working directory deliberately: "the tree" an anchor is
    checked against is whichever repo the checker is invoked from, not a root this
    script would have to rediscover a second time.
    """
    try:
        result = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True, check=True
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"check-decision-anchors: `git ls-files` failed: {exc}", file=sys.stderr)
        sys.exit(2)
    basenames = {}
    for path in result.stdout.splitlines():
        basenames.setdefault(os.path.basename(path), []).append(path)
    return basenames


def count_lines(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f)


def check_anchor(cited_path, line, basenames):
    """None if the anchor is clean, else a short reason string naming which of the
    two checks failed."""
    candidates = basenames.get(os.path.basename(cited_path))
    if not candidates:
        return "file not found in the tree"
    for candidate in candidates:
        try:
            total = count_lines(candidate)
        except OSError:
            continue
        if line <= total:
            return None
    return "line past end of file"


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="check-decision-anchors.py",
        description="Check every `<file>:<line>` anchor in a decisions document "
        "still names a real file at an in-range line.",
    )
    parser.add_argument(
        "--file",
        default=None,
        help="document to check (default: .harness/harness/docs/DECISIONS.md, "
        "resolved via harness_boundary)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)

    if args.file is not None:
        target = args.file
    else:
        try:
            target = default_target()
        except ValueError as exc:
            print(f"check-decision-anchors: {exc}", file=sys.stderr)
            sys.exit(2)

    try:
        with open(target, encoding="utf-8") as f:
            text = f.read()
    except OSError as exc:
        print(f"check-decision-anchors: cannot read {target!r}: {exc}", file=sys.stderr)
        sys.exit(2)

    anchors = extract_anchors(text)
    basenames = git_tracked_basenames()

    failed = 0
    for raw, cited_path, line in anchors:
        reason = check_anchor(cited_path, line, basenames)
        if reason is not None:
            print(f"{raw}: {reason}")
            failed += 1

    print(f"examined {len(anchors)} anchor(s), {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
