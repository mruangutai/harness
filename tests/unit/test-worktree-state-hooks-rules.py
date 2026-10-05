#!/usr/bin/env python3
"""The three layout-repair shims, run exactly as git runs them, against stub delegates
(FEAT-1559 T-04, SC-08).

Each case installs the REAL tracked shims under an install root whose path holds spaces, with
stub `worktree-state.py` and `post-merge-sweep.py` beside them that record argv, cwd and stdin,
then runs a shim from a SEPARATE checkout, also under a path with spaces. That separation is the
point: the shim finds its implementation beside itself, but repairs the checkout git is working
in — never the install root, which in a linked worktree is often another checkout entirely.

Post hooks cannot veto a git operation, so every shim exits 0 whatever happens. What a test can
and must pin is that each failure is SAID: a missing implementation, a delegate's nonzero exit,
and a dirty-tree skip each print a line naming it.
"""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOKS = ROOT / ".claude/skills/harness/hooks"
SHIMS = ("post-checkout", "post-merge", "post-rewrite")
ARGS = {"post-checkout": ["a" * 40, "b" * 40, "1"], "post-merge": ["0"],
        "post-rewrite": ["rebase"]}
REWRITE_STDIN = "1111111111111111111111111111111111111111 2222222222222222222222222222222222222222\n"

STUB = f"""#!{sys.executable}
import json, os, sys
name = os.path.basename(__file__)
data = sys.stdin.read()
with open(os.environ["STUB_LOG"], "a") as fh:
    fh.write(json.dumps({{"name": name, "argv": sys.argv[1:], "cwd": os.getcwd(),
                          "stdin": data}}) + "\\n")
print(f"{{name}} stub output")
sys.exit(int(os.environ.get("STUB_EXIT_" + name.split(".")[0].replace("-", "_"), "0")))
"""


class Installed(unittest.TestCase):
    """An install root holding the real shims and stub delegates, and a separate checkout."""

    def setUp(self):
        base = Path(os.path.realpath(tempfile.mkdtemp(prefix="hook shims ")))
        self.addCleanup(shutil.rmtree, base, True)
        self.install = base / "install root"
        self.hooks = self.install / ".claude/skills/harness/hooks"
        self.bin = self.install / ".claude/skills/harness/bin"
        self.hooks.mkdir(parents=True)
        self.bin.mkdir(parents=True)
        for name in SHIMS:
            if (HOOKS / name).exists():
                shutil.copy2(HOOKS / name, self.hooks / name)
        for name in ("worktree-state.py", "post-merge-sweep.py"):
            (self.bin / name).write_text(STUB)
            (self.bin / name).chmod(0o755)
        self.checkout = base / "the checkout"
        self.checkout.mkdir()
        subprocess.run(["git", "init", "-q", str(self.checkout)], check=True)
        self.log = base / "stub log.jsonl"
        self.env = dict(os.environ, STUB_LOG=str(self.log), GIT_CONFIG_NOSYSTEM="1",
                        GIT_CONFIG_GLOBAL=os.devnull)

    def fire(self, name, cwd=None, **stub_exits):
        env = dict(self.env, **{f"STUB_EXIT_{k}": str(v) for k, v in stub_exits.items()})
        stdin = REWRITE_STDIN if name == "post-rewrite" else ""
        return subprocess.run([str(self.hooks / name), *ARGS[name]], cwd=cwd or self.checkout,
                              input=stdin, env=env, capture_output=True, text=True)

    def calls(self):
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text().splitlines()]


class Shims(Installed):
    def test_every_shim_is_tracked_executable(self):
        for name in SHIMS:
            with self.subTest(name):
                listed = subprocess.run(["git", "ls-files", "-s", f".claude/skills/harness/hooks/{name}"],
                                        cwd=ROOT, capture_output=True, text=True).stdout
                self.assertTrue(listed.startswith("100755 "), f"{name}: {listed!r}")
                self.assertTrue(os.access(HOOKS / name, os.X_OK))

    def test_repair_runs_on_gits_checkout_not_the_install_root(self):
        for name in SHIMS:
            with self.subTest(name):
                self.log.unlink(missing_ok=True)
                proc = self.fire(name)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                repair = [c for c in self.calls() if c["name"] == "worktree-state.py"]
                self.assertEqual(len(repair), 1, self.calls())
                self.assertEqual(repair[0]["argv"], ["--repair", "--checkout", str(self.checkout)])

    def test_repair_does_not_consume_hook_stdin(self):
        proc = self.fire("post-rewrite")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(self.calls()[0]["stdin"], "")

    def test_a_successful_repair_prints_nothing(self):
        for name in ("post-checkout", "post-rewrite"):
            with self.subTest(name):
                proc = self.fire(name)
                self.assertEqual((proc.stdout, proc.stderr), ("", ""))

    def test_a_missing_implementation_is_reported_and_exits_0(self):
        (self.bin / "worktree-state.py").unlink()
        for name in SHIMS:
            with self.subTest(name):
                proc = self.fire(name)
                self.assertEqual(proc.returncode, 0)
                self.assertIn(f"{self.bin / 'worktree-state.py'} is missing or not executable",
                              proc.stderr)
                self.assertIn("no layout repair ran", proc.stderr)

    def test_a_failing_repair_is_attributed_and_exits_0(self):
        for name in SHIMS:
            with self.subTest(name):
                proc = self.fire(name, worktree_state=2)
                self.assertEqual(proc.returncode, 0)
                self.assertIn("worktree-state.py stub output", proc.stderr)
                self.assertIn(f"worktree-state.py --repair exited 2 in {self.checkout}", proc.stderr)
                self.assertIn("NOT converged", proc.stderr)

    def test_a_dirty_skip_is_reported_and_exits_0(self):
        for name in SHIMS:
            with self.subTest(name):
                proc = self.fire(name, worktree_state=8)
                self.assertEqual(proc.returncode, 0)
                self.assertIn(f"layout repair SKIPPED in {self.checkout}", proc.stderr)

    def test_outside_a_working_tree_nothing_is_repaired(self):
        outside = Path(tempfile.mkdtemp(prefix="not a checkout "))
        self.addCleanup(shutil.rmtree, outside, True)
        for name in SHIMS:
            with self.subTest(name):
                proc = self.fire(name, cwd=outside)
                self.assertEqual(proc.returncode, 0)
                self.assertIn("not inside a working tree", proc.stderr)
        # post-merge's sweep still runs there; repair, which needs a checkout, never does.
        self.assertEqual([c for c in self.calls() if c["name"] == "worktree-state.py"], [])


class PostMergeSweep(Installed):
    """post-merge keeps its terminal sweep: after repair, with git's argv, whatever repair did."""

    def sweep_calls(self):
        return [c for c in self.calls() if c["name"] == "post-merge-sweep.py"]

    def test_the_sweep_runs_after_repair_with_gits_argv(self):
        proc = self.fire("post-merge")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual([c["name"] for c in self.calls()],
                         ["worktree-state.py", "post-merge-sweep.py"])
        self.assertEqual(self.sweep_calls()[0]["argv"], ["0"])
        self.assertIn("post-merge-sweep.py stub output", proc.stdout)

    def test_the_sweep_still_runs_when_repair_fails_or_is_missing(self):
        proc = self.fire("post-merge", worktree_state=2)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(len(self.sweep_calls()), 1)
        self.log.unlink()
        (self.bin / "worktree-state.py").unlink()
        self.fire("post-merge")
        self.assertEqual(len(self.sweep_calls()), 1)

    def test_a_failing_sweep_is_attributed_and_exits_0(self):
        proc = self.fire("post-merge", post_merge_sweep=3)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("post-merge-sweep.py exited 3", proc.stderr)

    def test_a_missing_sweep_is_reported_and_exits_0(self):
        (self.bin / "post-merge-sweep.py").unlink()
        proc = self.fire("post-merge")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("no worktree sweep ran", proc.stdout + proc.stderr)
        self.assertEqual(len([c for c in self.calls() if c["name"] == "worktree-state.py"]), 1)


if __name__ == "__main__":
    unittest.main()
