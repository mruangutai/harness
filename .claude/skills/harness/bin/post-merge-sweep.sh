#!/usr/bin/env bash
# post-merge-sweep.sh — the entire body of the post-merge git hook (FEAT-34 T-03).
#
# Invocable directly, by its absolute path — the tracked `.claude/skills/harness/hooks/post-merge`
# shim (T-11, out of scope here) execs this script, but this script never assumes that shim ran
# it and never reads anything the shim would have set up.
#
# ARGS
#   $1          git's post-merge squash flag (0 or 1). IGNORED (D-01): post-merge is never told
#               which ref merged, and one `git pull` can land several merges, so the sweep runs
#               over every eligible worktree of the repository regardless of what $1 says.
#   --dry-run   print what the sweep would do, change nothing, exit 0. Safe in any tree — this
#               is the flag the mandated verify uses.
#
# The script NEVER exits non-zero for a skipped or declined record (a post-merge hook that fails
# makes git print an error after an otherwise successful pull) — every branch below prints and
# continues, and the process itself always exits 0.
set -u

DRY_RUN=0
for _arg in "$@"; do
  if [ "$_arg" = "--dry-run" ]; then
    DRY_RUN=1
  fi
done

BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

POST_MERGE_SWEEP_BIN_DIR="$BIN_DIR" POST_MERGE_SWEEP_DRY_RUN="$DRY_RUN" python3 - <<'PYEOF'
import os
import subprocess
import sys

BIN_DIR = os.environ["POST_MERGE_SWEEP_BIN_DIR"]
DRY_RUN = os.environ.get("POST_MERGE_SWEEP_DRY_RUN") == "1"

sys.path.insert(0, BIN_DIR)
import worktree_terminal   # noqa: E402  (D-02: the one shared eligibility predicate)
import factory_config      # noqa: E402


def _resolve_repo_root():
    """The repository root, derived from THIS SCRIPT's OWN on-disk location — never from the
    caller's cwd. BIN_DIR (set by the bash wrapper's
    `cd "$(dirname "${BASH_SOURCE[0]}")" && pwd`) is always `<root>/.claude/skills/harness/bin`,
    the same four path segments the T-11 shim (`.claude/skills/harness/hooks/post-merge`) already
    walks up from its own location — so walking BIN_DIR up those same four segments recovers
    `<root>` exactly, regardless of what directory the sweep happens to be invoked from.

    MEASURED DEFECT this replaces: the previous implementation ran
    `git worktree list --porcelain` with `cwd=os.getcwd()`, which discarded the root the T-11
    shim derived from `$0` and substituted the CALLER's cwd instead — invoked from outside the
    repository entirely, that command failed and the sweep did nothing, actively defeating T-11's
    own $0-based resolution. Deriving root from BIN_DIR instead means the caller's cwd — inside
    the repository, inside a linked worktree, or entirely outside any git repository — can never
    change what this resolves to.

    None only if BIN_DIR's own directory math points somewhere that does not exist as a
    directory at all — a broken installation, never a property of the caller's cwd. The caller
    treats that as nothing to sweep, never as an error that should abort the hook."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(BIN_DIR))))
    return root if os.path.isdir(root) else None


def _resolve_main_checkout_root(root):
    """The repository's MAIN checkout root — porcelain index 0, run with `cwd=root` (the
    BIN_DIR-derived root from `_resolve_repo_root()`, NEVER `os.getcwd()`). `root` answers "where
    do the bin scripts live" and can itself BE a linked worktree (a relative core.hooksPath
    resolves per-worktree — harness-init SKILL.md:73/:78 — so each worktree gets its own hooks
    dir and its own copy of this script). This function answers a SEPARATE question — "which
    checkout holds the feature directory that actually landed" — and the two must never be fused
    into one value again (the measured defect this replaces: a linked worktree's OWN, possibly
    divergent, copy of `.harness/<repo>/features/<FEAT>/` could exist and get shipped instead of
    the landed one — FEAT-35's `Review / pr:null` vs `Done / pr:812` divergence).

    `root` is always a valid checkout of the repository (main or linked) — INV-25's own
    precedent (check-state.sh:1138-1143, `worktree_terminal.classify`'s docstring): the first
    porcelain entry is always the main checkout, even queried from inside a linked worktree, and
    a repository with no linked worktrees returns itself. Running `git worktree list` with
    `cwd=root` therefore stays exactly as cwd-independent as `_resolve_repo_root()` itself —
    never `os.getcwd()`, which would reintroduce the original defect this module's docstring
    already warns about.

    None only if the subprocess cannot be run, times out, exits non-zero, or produces no
    parseable `worktree <path>` line at all — the caller treats that as nothing to sweep, the
    same "never abort the hook" contract `_resolve_repo_root()` follows."""
    try:
        proc = subprocess.run(["git", "worktree", "list", "--porcelain"], cwd=root,
                               capture_output=True, text=True, timeout=10)
    except Exception:
        return None
    if proc.returncode != 0 or not proc.stdout:
        return None
    for line in proc.stdout.splitlines():
        if line.startswith("worktree "):
            return line[len("worktree "):].strip()
    return None


def _repo_arg_for_segment(segment):
    """feature-worktree.py's --repo value for a worktree's bare repo segment: the literal
    "harness", or the fleet.yaml entry whose name's trailing segment matches. None if neither
    resolves.

    Re-derived here rather than imported: worktree_terminal.py's module docstring names its
    public surface as CLASSES and classify(root) only ("Everything else here is implementation
    detail that stays private") — its own private helper of the same name is not for import."""
    if segment == "harness":
        return "harness"
    try:
        fleet = factory_config.load_fleet()
    except Exception:
        return None
    for entry in fleet.get("repos", []):
        name = entry.get("name")
        if name and name.split("/", 1)[-1] == segment:
            return name
    return None


def _print_proc_output(proc):
    for stream in (proc.stdout, proc.stderr):
        if stream:
            sys.stdout.write(stream if stream.endswith("\n") else stream + "\n")


def _handle_record(rec, main_checkout_root, cwd_real):
    path = rec["path"]

    if rec["klass"] == "unresolved":
        print(f"post-merge-sweep: SKIP {path} — unresolved: {rec['reason']}")
        return
    if rec["klass"] != "terminal":
        # exempt_absent: never landed under this name at all — nothing to act on, nothing to
        # report either; classify() already omitted every non-terminal, non-exempt status.
        return

    # SELF-EXCLUSION, REQ-08. `git worktree remove` exits 0 from inside the tree it deletes
    # (check-state.sh:1173 already carries a comment about this same mechanical fact), so an
    # unguarded sweep would delete its own working directory mid-run. Compared by realpath, not
    # by string equality of the raw path, in case of a symlinked WORKTREES_SEGMENT ancestor.
    path_real = os.path.realpath(path)
    if cwd_real == path_real or cwd_real.startswith(path_real + os.sep):
        print(f"post-merge-sweep: SKIP {path} — the sweep declined to act on this record "
              f"because it is running inside it")
        return

    feature_id = rec["feature_id"]
    repo_segment = rec["repo"]
    wt_id = os.path.basename(path.rstrip(os.sep))

    repo_arg = _repo_arg_for_segment(repo_segment)
    if repo_arg is None:
        print(f"post-merge-sweep: SKIP {path} — could not resolve --repo for segment "
              f"{repo_segment!r}")
        return

    # The feature dir ON THE LOCAL DEFAULT BRANCH: a real filesystem directory under
    # `main_checkout_root` — resolved SEPARATELY from the BIN_DIR-derived root that locates the
    # bin scripts (see `_resolve_main_checkout_root`'s docstring for why the two must never be
    # fused) — never origin/<default_branch> (that ref is only as fresh as the last fetch, which
    # reproduces the same hole one level out).
    feat_dir = os.path.join(main_checkout_root, ".harness", repo_segment, "features", feature_id)
    if not os.path.isdir(feat_dir):
        print(f"post-merge-sweep: SKIP {path} — landed feature dir not found at {feat_dir} "
              f"on the local default branch")
        return

    if DRY_RUN:
        print(f"post-merge-sweep: DRY-RUN would ship {feature_id} then remove {wt_id} ({path})")
        return

    # ORDER, D-04: ship FIRST, remove only if that recorded the terminal status.
    ship = subprocess.run(
        ["python3", os.path.join(BIN_DIR, "gh-sync.py"), "ship", feat_dir],
        capture_output=True, text=True,
    )
    _print_proc_output(ship)

    # THE POSITIVE-SIGNAL GATE. gh-sync.py exits 0 on its own SKIP() branches (github.sync not
    # enabled, github.repo unpinned, gh missing/unauthenticated, no recorded milestone) WITHOUT
    # writing anything — an unconditional "exited 0 -> remove" would delete the checkout that is
    # the only remaining evidence the status was never recorded. skip() always prints the exact
    # line "gh-sync: SKIP — <reason>" before it exits, so that string's ABSENCE from the
    # combined stdout+stderr, together with exit 0, is what this gate treats as positive
    # evidence the write actually ran — never the exit code by itself.
    combined = (ship.stdout or "") + (ship.stderr or "")
    if ship.returncode != 0:
        print(f"post-merge-sweep: SKIP removal of {path} — gh-sync ship exited "
              f"{ship.returncode}")
        return
    if "gh-sync: SKIP" in combined:
        print(f"post-merge-sweep: SKIP removal of {path} — gh-sync ship reported SKIP, "
              f"which is not proof the terminal status was recorded")
        return

    # NO FORCE FLAG. feature-worktree.py remove already declines a dirty tree at exit 4 and an
    # unlanded artifact at exit 5; those refusals print and the sweep moves to the next record.
    remove = subprocess.run(
        ["python3", os.path.join(BIN_DIR, "feature-worktree.py"), "remove",
         "--repo", repo_arg, "--id", wt_id],
        capture_output=True, text=True,
    )
    _print_proc_output(remove)
    if remove.returncode != 0:
        print(f"post-merge-sweep: removal declined for {path} (exit {remove.returncode}) — "
              f"the standing checkout is the evidence")
    else:
        print(f"post-merge-sweep: removed {path}")


def main():
    root = _resolve_repo_root()
    if root is None:
        print("post-merge-sweep: could not resolve the repository root from this script's own "
              "on-disk location — nothing to sweep")
        return 0
    print(f"post-merge-sweep: resolved repository root: {root}")

    # `root` (above) answers "where do the bin scripts live" — BIN_DIR-derived, and can itself BE
    # a linked worktree. `main_checkout_root` answers a SEPARATE question — "which checkout holds
    # the feature directory that actually landed" — resolved from `git worktree list`'s porcelain
    # index 0, run with cwd=root (never os.getcwd()). classify() still receives `root`: its own
    # contract already handles `root` being a linked worktree correctly (skips it at index 0,
    # classifies it as a genuine record otherwise) — only feat_dir resolution needed splitting
    # out. See `_resolve_main_checkout_root`'s docstring for the full rationale.
    main_checkout_root = _resolve_main_checkout_root(root)
    if main_checkout_root is None:
        print("post-merge-sweep: could not resolve the main checkout root via `git worktree "
              "list` — nothing to sweep")
        return 0
    print(f"post-merge-sweep: resolved main checkout root: {main_checkout_root}")

    records = worktree_terminal.classify(root)
    cwd_real = os.path.realpath(os.getcwd())

    for rec in records:
        try:
            _handle_record(rec, main_checkout_root, cwd_real)
        except Exception as e:
            print(f"post-merge-sweep: ERROR handling {rec.get('path')}: {e}")
    return 0


try:
    _code = main()
except Exception as e:
    print(f"post-merge-sweep: ERROR: {e}")
    _code = 0
sys.exit(_code)
PYEOF
