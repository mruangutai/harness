#!/usr/bin/env python3
"""tests/git_support.py's git_out: git(cwd, *args) under the isolated environment, its stdout
stripped, raising AssertionError on a non-zero exit exactly as git() does."""
import tempfile
import unittest

import unit_support  # noqa: F401  (puts tests/ on sys.path)
from git_support import git, git_out


class GitOutTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = self._tmp.name
        git(self.repo, "init", "-q", "-b", "trunk")

    def tearDown(self):
        self._tmp.cleanup()

    def test_git_out_returns_stdout_stripped(self):
        self.assertTrue(git(self.repo, "symbolic-ref", "--short", "HEAD").stdout.endswith("\n"))
        self.assertEqual(git_out(self.repo, "symbolic-ref", "--short", "HEAD"), "trunk")

    def test_git_out_raises_on_a_non_zero_exit(self):
        with self.assertRaises(AssertionError):
            git_out(self.repo, "rev-parse", "--verify", "HEAD")


if __name__ == "__main__":
    unittest.main()
