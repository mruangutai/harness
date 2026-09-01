#!/usr/bin/env python3
"""quarantine.py — the explicit adopt/discard CLI for orphaned canonical writes (FEAT-51 T-04).

FEAT-51's earlier tasks record when a write to a canonical artifact (plan.yaml, BRIEF.md,
feature.json, STATE.md) becomes an orphan — a compatibility-host writer whose session is no
longer live — and redirect it into a quarantine directory instead of losing it silently
(inflight_registry.orphan_write, inflight_registry.quarantine_rel). This tool is the only way
that quarantined content is ever acted on: there is no scheduler, no timer, no TTL, and no
implicit action anywhere in this file. An operator runs one of three subcommands, and only that
command's own effect happens.

  list   — enumerate quarantined files for a feature. Read-only.
  adopt  — replace the canonical artifact with a quarantined one (plan.yaml unions through
           plan-merge.py; the other three replace via harness_merge.locked_update). Leaves the
           quarantine directory in place — adoption is auditable, discard is a separate act.
  discard — remove one quarantine directory tree, and only a directory that resolves under a
            features/*/quarantine/ segment.

python3 stdlib only, plus the two in-repo modules whose rules this tool reuses rather than
restates: inflight_registry (CANONICAL_ARTIFACTS) and harness_merge (locked_update).
"""
import argparse
import datetime
import glob
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness_boundary  # noqa: E402
import harness_merge  # noqa: E402
import inflight_registry  # noqa: E402

# A discard target must resolve to a directory ONE LEVEL UNDER a features/*/quarantine/
# segment — the per-writer directory inflight_registry.quarantine_rel creates, never the
# quarantine directory itself or anything above it. Matched against the REALPATH, never the
# argument as given (same discipline as harness_merge.require_destination): a dot-dot segment
# or a symlink must not be able to walk this tool's rm -rf out of the class it owns.
_QUARANTINE_CHILD_RE = re.compile(r"(?:^|/)features/[^/]+/quarantine/[^/]+")


def _resolve_root(explicit_root):
    """`--root` wins outright; otherwise the checkout this script's own location implies
    (harness_boundary.resolve_root). Returns None when neither resolves, so a caller can
    report the failure instead of raising past its own argument parsing."""
    if explicit_root:
        return os.path.abspath(explicit_root)
    try:
        return harness_boundary.resolve_root(os.path.dirname(os.path.abspath(__file__)))
    except ValueError:
        return None


def _resolve_path(path, root):
    """A relative --file/--dir is resolved against the checkout root, never against cwd —
    the same convention `--root` exists to make possible."""
    return path if os.path.isabs(path) else os.path.join(root, path)


def _split_agent_session(dirname):
    """The inverse of inflight_registry.quarantine_rel's `f"{agent}-{session_key}"` naming.
    `session_key` is either the literal `nosession` or `session[:8]` of a caller-supplied
    session id, and both are hyphen-free in every caller in this tree, so the LAST hyphen is
    always the boundary between the two — including for agent names that are themselves
    hyphenated, e.g. `harness-backend-dev-12345678`."""
    agent, sep, session = dirname.rpartition("-")
    return (agent, session) if sep else (dirname, "")


def _canonical_target_for(quarantined_path):
    """The canonical target: the same basename directly under the feature directory, which
    sits two levels above quarantine/<agent-session>/<basename>."""
    quarantine_dir = os.path.dirname(quarantined_path)
    feature_dir = os.path.dirname(os.path.dirname(quarantine_dir))
    return os.path.join(feature_dir, os.path.basename(quarantined_path))


def cmd_list(args):
    root = _resolve_root(args.root)
    if root is None:
        print("quarantine: no checkout root and no --root was given", file=sys.stderr)
        return 1
    pattern = os.path.join(
        root, ".harness", "*", "features", args.feature, "quarantine", "*", "*"
    )
    for path in sorted(glob.glob(pattern)):
        if not os.path.isfile(path):
            continue
        agent, session = _split_agent_session(os.path.basename(os.path.dirname(path)))
        mtime = datetime.datetime.fromtimestamp(
            os.path.getmtime(path), tz=datetime.timezone.utc
        ).isoformat()
        canonical = _canonical_target_for(path)
        print(f"{path} persona={agent} session={session} mtime={mtime} canonical={canonical}")
    return 0


def cmd_adopt(args):
    root = _resolve_root(args.root)
    if root is None:
        print("quarantine: no checkout root and no --root was given", file=sys.stderr)
        return 1
    quarantined = os.path.abspath(_resolve_path(args.file, root))
    basename = os.path.basename(quarantined)
    if basename not in inflight_registry.CANONICAL_ARTIFACTS:
        legal = ", ".join(inflight_registry.CANONICAL_ARTIFACTS)
        print(
            f"REFUSED: adopt only accepts one of {legal}, not {basename!r}.",
            file=sys.stderr,
        )
        return 2

    canonical = _canonical_target_for(quarantined)

    if basename == "plan.yaml":
        # DELEGATED, NOT REIMPLEMENTED: union-by-id and the byte-identical approval
        # carry-forward are plan-merge.py's answer. Both exit codes it can raise here
        # (7 — an existing id carries a different value; 8 — the approval mappings differ)
        # are surfaced verbatim, stdout and stderr both, never swallowed or collapsed into
        # a generic message — an operator must be able to act on either outcome.
        bin_dir = os.path.dirname(os.path.abspath(__file__))
        result = subprocess.run(
            [
                sys.executable,
                os.path.join(bin_dir, "plan-merge.py"),
                "apply",
                "--file", canonical,
                "--proposal", quarantined,
            ],
            capture_output=True,
            text=True,
        )
        if result.stdout:
            sys.stdout.write(result.stdout)
        if result.stderr:
            sys.stderr.write(result.stderr)
        if result.returncode != 0:
            return result.returncode
    else:
        with open(quarantined, "rb") as fh:
            payload = fh.read()
        harness_merge.locked_update(canonical, lambda _base, payload=payload: payload)

    print(f"ADOPTED {canonical} FROM {quarantined}")
    return 0


def cmd_discard(args):
    root = _resolve_root(args.root)
    if root is None:
        print("quarantine: no checkout root and no --root was given", file=sys.stderr)
        return 1
    target = os.path.realpath(os.path.abspath(_resolve_path(args.dir, root)))
    if not _QUARANTINE_CHILD_RE.search(target):
        print(
            f"REFUSED: {args.dir} does not resolve under a features/*/quarantine/ directory.",
            file=sys.stderr,
        )
        print(f"  resolved to: {target}", file=sys.stderr)
        return 2
    shutil.rmtree(target)
    print(f"DISCARDED {args.dir}")
    return 0


def main(argv=None):
    argv = list(argv) if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(prog="quarantine.py")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="list quarantined files for a feature")
    p_list.add_argument("--feature", required=True)
    p_list.add_argument("--root")
    p_list.set_defaults(func=cmd_list)

    p_adopt = sub.add_parser("adopt", help="adopt a quarantined file onto its canonical target")
    p_adopt.add_argument("--file", required=True)
    p_adopt.add_argument("--root")
    p_adopt.set_defaults(func=cmd_adopt)

    p_discard = sub.add_parser("discard", help="discard one quarantine directory")
    p_discard.add_argument("--dir", required=True)
    p_discard.add_argument("--root")
    p_discard.set_defaults(func=cmd_discard)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
