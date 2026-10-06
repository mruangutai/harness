"""f58_sparse_fixture.py — a synthetic owner repository with real linked worktrees (FEAT-1559).

FEAT-58 D-11, carried: every corpus-layout test runs against a SYNTHETIC repository built here, a
real `git init` with a handful of feature directories, never a copy of this checkout or its `.git`
(issue #1526: a fixture that copied `.claude/worktrees` cost 239 s of a 240 s suite). The module
name is deliberate: it matches none of the runner's `test-*` shapes, so it is imported, never
collected.

The owner holds records in TWO artifact segments — `harness` and the fleet segment `kaya` — so a
test can tell "the active record's segment" from "the worktree's segment". It also tracks every
non-feature `.harness` subtree in REQUIRED_PATHS and one record-less feature directory, because a
sparse cone that strips either while git reports success is the failure class this feature exists
to stop (FEAT-58 D-08).

Git runs with the system and global config files disabled, so a developer's own hooks or aliases
cannot reach the fixture, and with `core.hooksPath` pointed at an empty directory until a test
installs hooks itself.
"""
import contextlib
import os
import shutil
import subprocess
import tempfile

# Non-feature paths every record-bearing checkout must keep. Fixture assertions import this; the
# production derivation never reads it — it derives the cone from tracked directories alone.
REQUIRED_PATHS = (
    ".agents/skills",
    ".claude/skills/harness",
    ".harness/harness/docs",
    ".harness/expertise",
    ".harness/factory",
    ".harness/domains",
    ".harness/examples",
    ".harness/notes",
)

HARNESS_FEATURES = ("FEAT-1-alpha", "FEAT-2-beta")
RECORDLESS_FEATURE = "BUG-3-gamma"          # a landed directory with no feature.json
FLEET_SEGMENT = "kaya"
FLEET_FEATURES = ("FEAT-10-kaya-app",)


def _env():
    env = dict(os.environ)
    env.update({
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com",
    })
    env.pop("GIT_DIR", None)
    env.pop("GIT_WORK_TREE", None)
    return env


ENV = _env()


def git(cwd, *args, check=True):
    """Run git in `cwd` under the isolated environment; returns the CompletedProcess."""
    proc = subprocess.run(["git", *args], cwd=cwd, env=ENV, capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} in {cwd} exited {proc.returncode}: "
                             f"{proc.stderr.strip()}")
    return proc


def feature_json(feature_id, branch):
    return ('{"feature_id": "%s", "branch": "%s", "pr": null, "review_sha": "none", '
            '"cycles_used": 0, "max_total_cycles": 5, "runs": []}\n' % (feature_id, branch))


def _owner_files():
    files = {
        "README.md": "owner\n",
        ".gitignore": ".claude/worktrees/\n.harness/**/*.lock\n.harness/*/features/*/runs/**\n",
        "src/app.py": "print('app')\n",
        ".agents/skills/demo/SKILL.md": "skill\n",
        ".claude/skills/harness/bin/tool.py": "# tool\n",
        ".harness/team-config.yaml": "teams: {}\n",
        ".harness/harness.json": "{}\n",
        ".harness/README.md": "harness readme\n",
        ".harness/harness/docs/DECISIONS.md": "# decisions\n",
        ".harness/harness/expertise/pm.md": "expertise\n",
        ".harness/expertise/shared.md": "shared\n",
        # No fleet.yaml: a fixture with a fleet declaration is a factory, and every write
        # guard then demands a valid one. The subtree itself must still be tracked.
        ".harness/factory/README.md": "factory\n",
        ".harness/domains/d.md": "domain\n",
        ".harness/examples/e.md": "example\n",
        ".harness/notes/n.md": "note\n",
        f".harness/{FLEET_SEGMENT}/expertise/k.md": "fleet expertise\n",
    }
    for fid in HARNESS_FEATURES:
        base = f".harness/harness/features/{fid}"
        files[f"{base}/feature.json"] = feature_json(fid, f"feat/{fid}")
        files[f"{base}/BRIEF.md"] = f"# BRIEF {fid}\n"
        files[f"{base}/notes/research.md"] = f"research {fid}\n"
    files[f".harness/harness/features/{RECORDLESS_FEATURE}/notes/deep/history.md"] = "history\n"
    for fid in FLEET_FEATURES:
        base = f".harness/{FLEET_SEGMENT}/features/{fid}"
        files[f"{base}/feature.json"] = feature_json(fid, f"feat/{fid}")
        files[f"{base}/BRIEF.md"] = f"# BRIEF {fid}\n"
        files[f"{base}/notes/plan.md"] = f"plan {fid}\n"
    return files


def write_files(root, files):
    for rel, text in files.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)


class SparseFixture:
    """One owner repository and the checkouts a test cut from it. `commands` records every
    creation command in order, so a failing test can print how its subject was made."""

    def __init__(self, base):
        self.base = base
        self.owner = os.path.join(base, "owner")
        self.no_hooks = os.path.join(base, "no-hooks")
        self.commands = []

    def run(self, cwd, *args, check=True):
        self.commands.append(("git", *args))
        return git(cwd, *args, check=check)

    def build(self):
        os.makedirs(self.no_hooks)
        os.makedirs(self.owner)
        self.run(self.owner, "init", "-q", "-b", "main")
        self.run(self.owner, "config", "core.hooksPath", self.no_hooks)
        write_files(self.owner, _owner_files())
        self.run(self.owner, "add", "-A")
        self.run(self.owner, "commit", "-qm", "seed")
        return self

    def worktree_path(self, name, segment="harness"):
        return os.path.join(self.owner, ".claude", "worktrees", segment, name)

    def pin_path(self, feature, run_id="run1", persona="qa"):
        return os.path.join(self.owner, ".claude", "worktrees", ".pins",
                            f"{feature}--{run_id}--{persona}")

    def add_worktree(self, name, segment="harness", branch=None, ref="HEAD"):
        """A planning worktree the way `feature-worktree.py create` cuts one: a new branch at
        `ref`, at `<owner>/.claude/worktrees/<segment>/<name>`."""
        path = self.worktree_path(name, segment)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.run(self.owner, "worktree", "add", "-q", "-b", branch or f"feat/{name}", path, ref)
        return path

    def add_pin(self, feature, run_id="run1", persona="qa", ref="HEAD"):
        """A validator pin the way `pinned-checkout.py` cuts one: detached at `ref`."""
        path = self.pin_path(feature, run_id, persona)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.run(self.owner, "worktree", "add", "-q", "--detach", path, ref)
        return path

    def add_probe(self, name):
        """An arbitrary linked worktree OUTSIDE `.claude/worktrees` — not record-bearing."""
        path = os.path.join(self.base, "probes", name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.run(self.owner, "worktree", "add", "-q", "--detach", path, "HEAD")
        return path

    def clone(self, name="clone"):
        """A plain, non-linked clone of the owner."""
        path = os.path.join(self.base, name)
        self.run(self.base, "clone", "-q", self.owner, path)
        self.run(path, "config", "core.hooksPath", self.no_hooks)
        return path

    def commit_owner(self, files, message):
        write_files(self.owner, files)
        self.run(self.owner, "add", "-A")
        self.run(self.owner, "commit", "-qm", message)


HOOK_NAMES = ("post-checkout", "post-merge", "post-rewrite")


def install_hooks(checkout, source_root):
    """Give `checkout` its own copy of `source_root`'s harness bin and layout hooks, untracked
    and git-excluded, and point its `core.hooksPath` at that copy ABSOLUTELY. Returns
    `(bin_dir, hooks_dir)`.

    The bin lands in `checkout`'s own `.claude/skills/harness/bin` (the fixture tracks one file
    there), because every script derives its root four levels above itself: the post-merge sweep
    and the creators can then only ever reach this checkout. A shim absent from `source_root` is
    not copied, so a test run before the shims exist fails on behaviour, not on a copy error."""
    harness = os.path.join(checkout, ".claude", "skills", "harness")
    bin_dir, hooks = os.path.join(harness, "bin"), os.path.join(harness, "hooks")
    shutil.copytree(os.path.join(source_root, ".claude", "skills", "harness", "bin"), bin_dir,
                    dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
    os.makedirs(hooks, exist_ok=True)
    for name in HOOK_NAMES:
        shim = os.path.join(source_root, ".claude", "skills", "harness", "hooks", name)
        if os.path.exists(shim):
            shutil.copy2(shim, hooks)
    common = git(checkout, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()
    with open(os.path.join(common, "info", "exclude"), "a") as fh:
        fh.write("/.claude/skills/\n")
    git(checkout, "config", "core.hooksPath", hooks)
    return bin_dir, hooks


@contextlib.contextmanager
def sparse_fixture():
    """Build a fresh owner under a private temporary directory and remove exactly that
    directory afterwards. Nothing outside it is created or touched."""
    base = os.path.realpath(tempfile.mkdtemp(prefix="f58-sparse-"))
    try:
        yield SparseFixture(base).build()
    finally:
        shutil.rmtree(base, ignore_errors=True)


def feature_dirs_on_disk(checkout):
    """Every `.harness/<segment>/features/<name>` directory present on disk — tracked, untracked
    or ignored alike — as sorted `<segment>/<name>` strings."""
    found = []
    harness = os.path.join(checkout, ".harness")
    if not os.path.isdir(harness):
        return found
    for segment in sorted(os.listdir(harness)):
        features = os.path.join(harness, segment, "features")
        if os.path.isdir(features):
            found.extend(f"{segment}/{name}" for name in sorted(os.listdir(features))
                         if os.path.isdir(os.path.join(features, name)))
    return found


def snapshot(checkout):
    """Bytes of every file under `checkout` (excluding nothing) plus the worktree's own git
    index and config, so a test can prove a mode changed nothing at all."""
    state = {}
    for dirpath, dirnames, filenames in os.walk(checkout):
        dirnames.sort()
        for name in sorted(filenames):
            path = os.path.join(dirpath, name)
            if os.path.islink(path):
                state[os.path.relpath(path, checkout)] = ("link", os.readlink(path))
                continue
            with open(path, "rb") as fh:
                state[os.path.relpath(path, checkout)] = fh.read()
    git_dir = git(checkout, "rev-parse", "--absolute-git-dir").stdout.strip()
    common = git(checkout, "rev-parse", "--git-common-dir").stdout.strip()
    common = common if os.path.isabs(common) else os.path.join(checkout, common)
    for label, path in (("index", os.path.join(git_dir, "index")),
                        ("config.worktree", os.path.join(git_dir, "config.worktree")),
                        ("sparse-checkout", os.path.join(git_dir, "info", "sparse-checkout")),
                        ("common-config", os.path.join(common, "config"))):
        if os.path.exists(path):
            with open(path, "rb") as fh:
                state[f"<git>/{label}"] = fh.read()
    return state
