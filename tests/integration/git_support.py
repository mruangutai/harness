"""git_support.py — real-git fixture primitives shared by integration tests.

Every primitive runs git through a caller-chosen `git(args, cwd)` callable. The default,
`quiet_git`, captures output and never checks the exit code — the policy every migrated caller
had before. A caller that runs git loudly (test-hooks-install.py's `_git`) passes its own.

Nothing here picks a default branch, maintenance setting, file, or commit message on a caller's
behalf: `init_repo` takes the branch (None leaves git's own default), and the seed file,
feature layout, plan text, and message are all supplied by the caller or spelled at its site.
"""
import json
import os
import subprocess

IDENTITY = ("t@example.com", "t")
MAINTENANCE_OFF = (("maintenance.auto", "false"), ("gc.auto", "0"))


def quiet_git(args, cwd):
    return subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True)


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
