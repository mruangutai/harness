#!/usr/bin/env python3
"""pinned-checkout.py — a validator's disposable detached checkout at one pin (#1994).

A reader that must judge the exact `review_sha` checks it out here, never with a bare
`git worktree add --detach` into a path nobody sweeps. Every checkout lives under ONE root,
`<owner>/.claude/worktrees/.pins/<run-id>/`, so `remove` needs only the run id and `sweep`
can find what a dead run left behind.

  add    --run-id R --sha S     print the checkout path (idempotent for the same pin)
  remove --run-id R             delete the checkout and its worktree registration
  sweep  [--older-than-hours H] [--dry-run]   remove checkouts untouched for H hours (default 24)

The checkout carries no node_modules, no build and no evidence of its own; the reader installs
and builds inside it and removes it on return. Exit 2 is refusal; the reason is on stderr.
"""
import argparse
import os
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness_boundary  # noqa: E402

PINS_SEGMENT = ".pins"
SHA_LEN = 40


def _refuse(message):
    sys.stderr.write(f"pinned-checkout: {message}\n")
    return 2


def _git(owner_root, *args):
    return subprocess.run(["git", *args], cwd=owner_root, capture_output=True, text=True)


def _owner_root():
    root = harness_boundary.root_above(os.getcwd())
    if root is None:
        return None
    common = _git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if common.returncode != 0:
        return None
    # A linked worktree's owner is the checkout that holds the common git dir.
    return os.path.dirname(common.stdout.strip())


def _pins_root(owner_root):
    return os.path.join(owner_root, harness_boundary.WORKTREES_SEGMENT, PINS_SEGMENT)


def _valid_run_id(run_id):
    return bool(run_id) and "/" not in run_id and run_id not in (".", "..")


def _pin_refusal(owner_root, args):
    """The reason `add` cannot proceed, or None."""
    if not _valid_run_id(args.run_id):
        return f"run id {args.run_id!r} must be one path segment"
    sha = args.sha.strip().lower()
    if len(sha) != SHA_LEN or any(c not in "0123456789abcdef" for c in sha):
        return f"sha {args.sha!r} must be the full 40-hex commit id, never abbreviated"
    if _git(owner_root, "cat-file", "-e", f"{sha}^{{commit}}").returncode != 0:
        return f"{sha} is not a commit in this repository"
    return None


def _existing_pin_refusal(dest, sha):
    head = _git(dest, "rev-parse", "HEAD").stdout.strip()
    if head == sha:
        return None
    return f"{dest} already holds {head[:12]} — a different pin; remove it first"


def cmd_add(owner_root, args):
    refusal = _pin_refusal(owner_root, args)
    if refusal:
        return _refuse(refusal)
    sha = args.sha.strip().lower()
    dest = os.path.join(_pins_root(owner_root), args.run_id)
    if os.path.isdir(dest):
        refusal = _existing_pin_refusal(dest, sha)
        if refusal:
            return _refuse(refusal)
        print(dest)
        return 0
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    added = _git(owner_root, "worktree", "add", "--detach", "--quiet", dest, sha)
    if added.returncode != 0:
        return _refuse(f"git worktree add failed: {added.stderr.strip()}")
    print(dest)
    return 0


def _remove_one(owner_root, dest):
    removed = _git(owner_root, "worktree", "remove", "--force", dest)
    if os.path.isdir(dest):
        shutil.rmtree(dest, ignore_errors=True)
    _git(owner_root, "worktree", "prune")
    return removed.returncode == 0 or not os.path.exists(dest)


def cmd_remove(owner_root, args):
    if not _valid_run_id(args.run_id):
        return _refuse(f"run id {args.run_id!r} must be one path segment")
    dest = os.path.join(_pins_root(owner_root), args.run_id)
    if not os.path.exists(dest):
        return 0
    return 0 if _remove_one(owner_root, dest) else _refuse(f"could not remove {dest}")


def _stale_pins(pins, cutoff):
    for name in sorted(os.listdir(pins)):
        dest = os.path.join(pins, name)
        if os.path.isdir(dest) and os.stat(dest).st_mtime <= cutoff:
            yield name, dest


def cmd_sweep(owner_root, args):
    pins = _pins_root(owner_root)
    if not os.path.isdir(pins):
        return 0
    verb = "would remove" if args.dry_run else "removed"
    for name, dest in _stale_pins(pins, time.time() - args.older_than_hours * 3600):
        print(f"{verb} {name}")
        if not args.dry_run:
            _remove_one(owner_root, dest)
    return 0


def _build_parser():
    parser = argparse.ArgumentParser(prog="pinned-checkout.py")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_add = sub.add_parser("add")
    p_add.add_argument("--run-id", required=True)
    p_add.add_argument("--sha", required=True)
    p_remove = sub.add_parser("remove")
    p_remove.add_argument("--run-id", required=True)
    p_sweep = sub.add_parser("sweep")
    p_sweep.add_argument("--older-than-hours", type=float, default=24.0)
    p_sweep.add_argument("--dry-run", action="store_true")
    return parser


def main(argv=None):
    args = _build_parser().parse_args(argv)
    owner_root = _owner_root()
    if owner_root is None:
        return _refuse("not inside a harness checkout (no .harness/team-config.yaml above cwd)")
    return {"add": cmd_add, "remove": cmd_remove, "sweep": cmd_sweep}[args.cmd](owner_root, args)


if __name__ == "__main__":
    sys.exit(main())
