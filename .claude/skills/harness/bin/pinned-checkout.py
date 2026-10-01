#!/usr/bin/env python3
"""pinned-checkout.py — a validator's disposable detached checkout at one pin (#1994).

A reader that must judge the exact `review_sha` checks it out here, never with a bare
`git worktree add --detach` into a path nobody sweeps. Every checkout lives under ONE root,
`<owner>/.claude/worktrees/.pins/<feature>--<run-id>--<persona>/`. One reader's checkout is
its own: a validator-lead starts qa, code, security, ui and pm on the same run id at once, and
run ids repeat across features, so the key is all three. `sweep` finds what a dead run left.

  add    --feature F --run-id R --persona P --sha S   print the checkout path (idempotent for the same pin)
  remove --feature F --run-id R --persona P          delete the checkout and its worktree registration
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
    return os.path.join(owner_root, harness_boundary.WORKTREES_SEGMENT, harness_boundary.PINS_SEGMENT)


def _valid_segment(value):
    return bool(value) and "/" not in value and "--" not in value and value not in (".", "..")


def _pin_name(args):
    """None when a key part is unusable, else the one directory name for this reader's checkout."""
    parts = (args.feature, args.run_id, args.persona)
    if not all(_valid_segment(part) for part in parts):
        return None
    return "--".join(parts)


def _is_own_worktree(dest):
    top = _git(dest, "rev-parse", "--show-toplevel")
    return top.returncode == 0 and os.path.realpath(top.stdout.strip()) == os.path.realpath(dest)


def _pin_refusal(owner_root, args):
    """The reason `add` cannot proceed, or None."""
    if _pin_name(args) is None:
        return "--feature, --run-id and --persona must each be one path segment without '--'"
    sha = args.sha.strip().lower()
    if len(sha) != SHA_LEN or any(c not in "0123456789abcdef" for c in sha):
        return f"sha {args.sha!r} must be the full 40-hex commit id, never abbreviated"
    if _git(owner_root, "cat-file", "-e", f"{sha}^{{commit}}").returncode != 0:
        return f"{sha} is not a commit in this repository"
    return None


def _existing_pin_refusal(dest, sha):
    if not _is_own_worktree(dest):
        return f"{dest} exists but is not a checkout of its own; remove it first"
    head = _git(dest, "rev-parse", "HEAD").stdout.strip()
    if head == sha:
        return None
    return f"{dest} already holds {head[:12]} — a different pin; remove it first"


def cmd_add(owner_root, args):
    refusal = _pin_refusal(owner_root, args)
    if refusal:
        return _refuse(refusal)
    sha = args.sha.strip().lower()
    dest = os.path.join(_pins_root(owner_root), _pin_name(args))
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
    name = _pin_name(args)
    if name is None:
        return _refuse("--feature, --run-id and --persona must each be one path segment without '--'")
    dest = os.path.join(_pins_root(owner_root), name)
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
    failed = 0
    for name, dest in _stale_pins(pins, time.time() - args.older_than_hours * 3600):
        if args.dry_run:
            print(f"would remove {name}")
        elif _remove_one(owner_root, dest):
            print(f"removed {name}")
        else:
            failed += 1
            print(f"could not remove {name}", file=sys.stderr)
    return 1 if failed else 0


def _build_parser():
    parser = argparse.ArgumentParser(prog="pinned-checkout.py")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_add = sub.add_parser("add")
    p_remove = sub.add_parser("remove")
    for sub_parser in (p_add, p_remove):
        sub_parser.add_argument("--feature", required=True)
        sub_parser.add_argument("--run-id", required=True)
        sub_parser.add_argument("--persona", required=True)
    p_add.add_argument("--sha", required=True)
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
