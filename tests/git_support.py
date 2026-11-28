"""git_support.py — real-git fixture primitives shared by unit and integration tests.

Two ways to run git, each with its exit-code policy explicit:

    git(cwd, *args, check=True) -> CompletedProcess (text)
        Runs under ENV, the isolated environment: system and global git config disabled, a fixed
        author and committer identity, every inherited GIT_* variable dropped. check=True raises
        AssertionError naming the command on a non-zero exit; check=False never checks.
    git_out(cwd, *args) -> str
        git(cwd, *args).stdout.strip(): the same isolated environment and the same raising on a
        non-zero exit, for the reads (rev-parse, symbolic-ref, status --porcelain) a caller
        compares as a string.
    quiet_git(args, cwd) / checked_git(args, cwd)
        The `git=` callables the primitives below accept. quiet_git inherits os.environ and never
        checks the exit code (the default, the policy the integration callers were written
        against). checked_git is git(cwd, *args) above: isolated and raising, for a caller whose
        fixture must not fail silently.

Primitives, each taking `git=quiet_git`: init_repo, commit_files, commit_all, commit_feature,
add_worktree, plus feature_rel and plan_text. IDENTITY and MAINTENANCE_OFF are config pairs.

Nothing here picks a default branch, maintenance setting, file, or commit message on a caller's
behalf: `init_repo` takes the branch (None leaves git's own default), and the seed file,
feature layout, plan text, and message are all supplied by the caller or spelled at its site.

Import from a unit file:        from unit_support import ROOT   (puts tests/ on sys.path)
                                from git_support import checked_git, init_repo, commit_files
Import from an integration file: from integration_support import ROOT   (puts tests/ on sys.path)
                                 from git_support import git, git_out, checked_git, init_repo

Git isolation is the default and stays the default. ENV drops every inherited GIT_* variable and
disables system and global config; repository-local config (core.hooksPath, hooks under .git)
still applies, which is why test-worktree-state-hooks.py runs its hook cases under git() and
ENV. A file whose git must see the inherited environment, or a custom one, does not loosen ENV:
it runs git through quiet_git (inherits os.environ, never checks) or keeps its own runner when it
needs both a custom env and a loud failure -- test-hooks-install.py's _git(args, cwd, env=None)
is that case and stays local.
"""
import json
import os
import subprocess

IDENTITY = ("t@example.com", "t")
MAINTENANCE_OFF = (("maintenance.auto", "false"), ("gc.auto", "0"))


def _isolated_env():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com",
    })
    return env


ENV = _isolated_env()


def git(cwd, *args, check=True):
    """Run git in `cwd` under the isolated environment; returns the CompletedProcess."""
    proc = subprocess.run(["git", *args], cwd=cwd, env=ENV, capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} in {cwd} exited {proc.returncode}: "
                             f"{proc.stderr.strip()}")
    return proc


def git_out(cwd, *args):
    """Run git like git(cwd, *args) above and return its stdout stripped."""
    return git(cwd, *args).stdout.strip()


def quiet_git(args, cwd):
    return subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True)


def checked_git(args, cwd):
    """The loud `git=` callable: isolated environment, AssertionError on a non-zero exit."""
    return git(cwd, *args)


def init_repo(path, branch, identity=IDENTITY, config=(), git=quiet_git):
    """`git init` at `path` (created if absent) on `branch` — None omits `-b` — then the
    identity and any extra `(key, value)` config pairs, in that order."""
    os.makedirs(path, exist_ok=True)
    git(["init", "-q"] + ([] if branch is None else ["-b", branch]), path)
    email, name = identity
    for key, value in (("user.email", email), ("user.name", name)) + tuple(config):
        git(["config", key, value], path)
    return path


def commit_files(repo, files, message, git=quiet_git):
    """Write each `{relpath: text}` under `repo`, stage exactly those paths in that order, and
    land them in ONE commit."""
    for rel, text in files.items():
        abs_path = os.path.join(repo, rel)
        os.makedirs(os.path.dirname(abs_path) or repo, exist_ok=True)
        with open(abs_path, "w") as f:
            f.write(text)
    git(["add"] + list(files), repo)
    git(["commit", "-qm", message], repo)


def commit_all(repo, message, git=quiet_git):
    """Stage everything already in the working tree (`git add -A`) and commit it."""
    git(["add", "-A"], repo)
    git(["commit", "-qm", message], repo)


def feature_rel(repo_segment, feature_id, *parts):
    return os.path.join(".harness", repo_segment, "features", feature_id, *parts)


def plan_text(feature_id, station):
    return f"feature: {feature_id}\nstatus: {station}\ntasks: []\n"


def commit_feature(repo, feature_id, doc_or_raw, repo_segment, message, plan_station=None,
                   extra_files=None, git=quiet_git):
    """Commit `<feature dir>/feature.json` on the CURRENT branch — a dict is written as JSON, a
    string verbatim — plus, in the SAME commit, a sibling `plan.yaml` carrying `plan_station`
    when given and any `extra_files` (`{relpath: text}`, staged after the plan). Landing them
    together matters: readers resolve one from the other's directory at a landed ref.
    Returns the absolute feature.json path."""
    rel = feature_rel(repo_segment, feature_id, "feature.json")
    files = {rel: doc_or_raw if isinstance(doc_or_raw, str) else json.dumps(doc_or_raw)}
    if plan_station is not None:
        files[feature_rel(repo_segment, feature_id, "plan.yaml")] = plan_text(feature_id,
                                                                              plan_station)
    files.update(extra_files or {})
    commit_files(repo, files, message, git=git)
    return os.path.join(repo, rel)


def add_worktree(repo, worktree_id, repo_segment, branch, ref="HEAD", git=quiet_git):
    """A real `git worktree add -b <branch>` from `ref` at the station path
    `.claude/worktrees/<repo_segment>/<worktree_id>`; returns that path."""
    dest = os.path.join(repo, ".claude", "worktrees", repo_segment, worktree_id)
    git(["worktree", "add", "-q", "-b", branch, dest, ref], repo)
    return dest
