#!/usr/bin/env python3
"""pinned-checkout.py — a validator's detached checkout at a pin is created under one
disposable root, removed on demand, and swept when stale (#1994).

Every case runs against a throwaway repository; nothing touches this checkout."""
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / ".claude" / "skills" / "harness" / "bin" / "pinned-checkout.py"
FAILURES = []


def check(name, condition, detail=""):
    print(("PASS" if condition else "FAIL") + " - " + name)
    if not condition:
        FAILURES.append(name)
        print("       " + detail[:500])


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def tool(cwd, *args):
    return subprocess.run([sys.executable, str(TOOL), *args], cwd=cwd, capture_output=True, text=True)


KEY = ("--feature", "FEAT-9-thing", "--persona")


def add(repo, run_id, sha, persona="qa"):
    return tool(repo, "add", *KEY, persona, "--run-id", run_id, "--sha", sha)


def make_repo(tmp):
    repo = Path(tmp) / "owner"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "t")
    (repo / ".harness").mkdir()
    (repo / ".harness" / "team-config.yaml").write_text("agents: {}\n")
    (repo / "a.txt").write_text("one\n")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "one")
    first = git(repo, "rev-parse", "HEAD")
    (repo / "a.txt").write_text("two\n")
    git(repo, "commit", "-q", "-am", "two")
    return repo, first


def pins_root(repo):
    return (repo / ".claude" / "worktrees" / ".pins").resolve()


def add_cases(repo, first):
    added = add(repo, "validate-c1-qa", first)
    path = added.stdout.strip()
    check("add prints the checkout path and exits 0", added.returncode == 0 and bool(path), added.stderr)
    check("checkout lives under the disposable pins root", Path(path).resolve() == pins_root(repo) / "FEAT-9-thing--validate-c1-qa--qa", path)
    at_pin = git(path, "rev-parse", "HEAD") == first and (Path(path) / "a.txt").read_text() == "one\n"
    check("checkout is detached at exactly the pin", at_pin)
    again = add(repo, "validate-c1-qa", first)
    check("add is idempotent for the same run and pin", again.returncode == 0 and again.stdout.strip() == path, again.stderr)
    return path


def add_refusal_cases(repo, first):
    moved = add(repo, "validate-c1-qa", git(repo, "rev-parse", "HEAD"))
    check("add refuses to move an existing run's checkout to another pin", moved.returncode == 2 and "different pin" in moved.stderr, moved.stderr)
    short = add(repo, "validate-c2-qa", first[:8])
    check("add refuses an abbreviated sha", short.returncode == 2 and "40-hex" in short.stderr, short.stderr)
    missing = add(repo, "validate-c3-qa", "0" * 40)
    check("add refuses a sha the repository does not have", missing.returncode == 2 and "not a commit" in missing.stderr, missing.stderr)
    other = add(repo, "validate-c1-qa", first, persona="code")
    same_run_own_tree = other.returncode == 0 and other.stdout.strip() != str(pins_root(repo) / "FEAT-9-thing--validate-c1-qa--qa")
    check("a second reader on the same run id gets its own checkout", same_run_own_tree, other.stdout + other.stderr)
    dashed = tool(repo, "add", "--feature", "FEAT-9--x", "--persona", "qa", "--run-id", "r", "--sha", first)
    check("a key part containing '--' is refused (the separator)", dashed.returncode == 2, dashed.stderr)


def remove_cases(repo, path):
    removed = tool(repo, "remove", *KEY, "qa", "--run-id", "validate-c1-qa")
    listed = git(repo, "worktree", "list")
    gone = not Path(path).exists() and "validate-c1-qa--qa" not in listed and "validate-c1-qa--code" in listed
    check("remove deletes this reader's checkout and worktree entry, not the other reader's", removed.returncode == 0 and gone, removed.stderr)
    check("remove of an absent run is a no-op success", tool(repo, "remove", *KEY, "qa", "--run-id", "validate-c1-qa").returncode == 0)


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


def classify_cases(repo, first):
    """A pin is not a feature worktree: worktree_terminal.classify must not emit it as an
    unresolved record, or INV-29 turns every session's check-state red for the run's whole life."""
    sys.path.insert(0, str(TOOL.parent))
    import worktree_terminal
    add(repo, "validate-c6-qa", first)
    records = worktree_terminal.classify(str(repo))
    pins = [r for r in records if ".pins" in r["path"]]
    check("classify skips pinned checkouts (no INV-29 unresolved record)", pins == [], str(pins))


def main():
    with tempfile.TemporaryDirectory() as tmp:
        repo, first = make_repo(tmp)
        classify_cases(repo, first)
        path = add_cases(repo, first)
        add_refusal_cases(repo, first)
        remove_cases(repo, path)
        sweep_cases(repo, first)
        outside = Path(tmp) / "elsewhere"
        outside.mkdir()
        nowhere = add(outside, "x", first)
        check("outside a harness checkout the tool refuses", nowhere.returncode == 2, nowhere.stderr)
    print(f"{len(FAILURES)} failure(s)" if FAILURES else "all checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
