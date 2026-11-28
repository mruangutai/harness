#!/usr/bin/env python3
"""pinned-checkout.py — a validator's detached checkout at a pin is created under one
disposable root, removed on demand, and swept when stale (#1994).

Every case runs against a throwaway repository; nothing touches this checkout."""
from integration_support import BIN

import os  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

from check_support import Checks  # noqa: E402
from git_support import checked_git, commit_files, git_out, init_repo  # noqa: E402

TOOL = BIN / "pinned-checkout.py"
C = Checks()
check = C.check


def tool(cwd, *args):
    return subprocess.run([sys.executable, str(TOOL), *args], cwd=cwd, capture_output=True, text=True)


def key(persona="qa"):
    return ("--feature", "FEAT-9-thing", "--persona", persona)


def add(repo, run_id, sha, persona="qa"):
    return tool(repo, "add", *key(persona), "--run-id", run_id, "--sha", sha)


def remove(repo, run_id, persona="qa"):
    return tool(repo, "remove", *key(persona), "--run-id", run_id)


def make_repo(tmp):
    """The owner repository with two commits; returns (repo, first sha, second sha)."""
    repo = init_repo(Path(tmp) / "owner", "main", git=checked_git)
    commit_files(repo, {".harness/team-config.yaml": "agents: {}\n", "a.txt": "one\n"}, "one", git=checked_git)
    first = git_out(repo, "rev-parse", "HEAD")
    commit_files(repo, {"a.txt": "two\n"}, "two", git=checked_git)
    return repo, first, git_out(repo, "rev-parse", "HEAD")


def pins_root(repo):
    return (repo / ".claude" / "worktrees" / ".pins").resolve()


def add_cases(repo, first):
    added = add(repo, "validate-c1-qa", first)
    path = added.stdout.strip()
    check("add prints the checkout path and exits 0", added.returncode == 0 and bool(path), added.stderr)
    check("checkout lives under the disposable pins root", Path(path).resolve() == pins_root(repo) / "FEAT-9-thing--validate-c1-qa--qa", path)
    at_pin = git_out(path, "rev-parse", "HEAD") == first and (Path(path) / "a.txt").read_text() == "one\n"
    check("checkout is detached at exactly the pin", at_pin)
    again = add(repo, "validate-c1-qa", first)
    check("add is idempotent for the same run and pin", again.returncode == 0 and again.stdout.strip() == path, again.stderr)
    return path


def add_refusal_cases(repo, first, second, path):
    moved = add(repo, "validate-c1-qa", second)
    check("add refuses to move an existing run's checkout to another pin", moved.returncode == 2 and "different pin" in moved.stderr, moved.stderr)
    short = add(repo, "validate-c2-qa", first[:8])
    check("add refuses an abbreviated sha", short.returncode == 2 and "40-hex" in short.stderr, short.stderr)
    missing = add(repo, "validate-c3-qa", "0" * 40)
    check("add refuses a sha the repository does not have", missing.returncode == 2 and "not a commit" in missing.stderr, missing.stderr)
    other = add(repo, "validate-c1-qa", first, persona="code")
    same_run_own_tree = other.returncode == 0 and other.stdout.strip() != path
    check("a second reader on the same run id gets its own checkout", same_run_own_tree, other.stdout + other.stderr)
    dashed = tool(repo, "add", "--feature", "FEAT-9--x", "--persona", "qa", "--run-id", "r", "--sha", first)
    check("a key part containing '--' is refused (the separator)", dashed.returncode == 2, dashed.stderr)


def remove_cases(repo, path):
    removed = remove(repo, "validate-c1-qa")
    listed = git_out(repo, "worktree", "list")
    gone = not Path(path).exists() and "validate-c1-qa--qa" not in listed and "validate-c1-qa--code" in listed
    check("remove deletes this reader's checkout and worktree entry, not the other reader's", removed.returncode == 0 and gone, removed.stderr)
    check("remove of an absent run is a no-op success", remove(repo, "validate-c1-qa").returncode == 0)


def sweep_cases(repo, first):
    old = Path(add(repo, "validate-c4-qa", first).stdout.strip())
    fresh = Path(add(repo, "validate-c5-qa", first).stdout.strip())
    stale = time.time() - 2 * 86400
    os.utime(old, (stale, stale))
    swept = tool(repo, "sweep", "--older-than-hours", "24")
    only_old = not old.exists() and fresh.exists() and "validate-c4-qa" in swept.stdout and "validate-c5-qa" not in swept.stdout
    check("sweep removes only checkouts older than the window", swept.returncode == 0 and only_old, swept.stdout + swept.stderr)
    dry = tool(repo, "sweep", "--older-than-hours", "0", "--dry-run")
    check("sweep --dry-run names the checkout and leaves it", dry.returncode == 0 and fresh.exists() and "validate-c5-qa" in dry.stdout, dry.stdout)


def classify_cases(repo, path):
    """A pin is not a feature worktree: worktree_terminal.classify must not emit it as an
    unresolved record, or INV-29 turns every session's check-state red for the run's whole life.
    Runs while add_cases' pin at `path` is on disk; the check also proves that pin is listed."""
    import worktree_terminal
    pinned = "validate-c1-qa--qa" in git_out(repo, "worktree", "list") and Path(path).exists()
    records = worktree_terminal.classify(str(repo))
    pins = [r for r in records if ".pins" in r["path"]]
    check("classify skips pinned checkouts (no INV-29 unresolved record)", pinned and pins == [], str(pins))


def main():
    with tempfile.TemporaryDirectory() as tmp:
        repo, first, second = make_repo(tmp)
        path = add_cases(repo, first)
        classify_cases(repo, path)
        add_refusal_cases(repo, first, second, path)
        remove_cases(repo, path)
        sweep_cases(repo, first)
        outside = Path(tmp) / "elsewhere"
        outside.mkdir()
        nowhere = add(outside, "x", first)
        check("outside a harness checkout the tool refuses", nowhere.returncode == 2, nowhere.stderr)
    return C.report()


if __name__ == "__main__":
    sys.exit(main())
