#!/usr/bin/env python3
"""check-state over sparse and full checkouts of a synthetic owner (FEAT-1559 SC-03, SC-04,
SC-05, SC-06, SC-09).

The checker runs as a subprocess against each checkout (HARNESS_PROJECT_DIR), the way the
pre-commit gate and /harness entry run it. One wrapper runs it under a Python audit hook that
records every file it opens, so "reads only its own feature" is observed, not inferred from code.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BIN = ROOT / ".claude/skills/harness/bin"
CHECK = BIN / "check-state.py"
REPAIR = BIN / "worktree-state.py"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(BIN))
import f58_sparse_fixture as F  # noqa: E402
from isolated_bin import isolated_bin  # noqa: E402

ACTIVE = "FEAT-1-alpha"
NO_INVARIANT_RAN = "no invariant ran"

# Runs check-state.py under an audit hook and appends every opened path to OPEN_LOG.
WRAPPER = r"""
import os, runpy, sys
log, script = os.environ["OPEN_LOG"], sys.argv[1]
seen = []
def hook(event, args):
    if event == "open" and isinstance(args[0], (str, bytes)):
        p = os.fsdecode(args[0])
        seen.append(os.path.realpath(p if os.path.isabs(p) else os.path.join(os.getcwd(), p)))
sys.addaudithook(hook)
sys.argv = [script] + sys.argv[2:]
try:
    runpy.run_path(script, run_name="__main__")
finally:
    with open(log, "w") as fh:
        fh.write("\n".join(seen))
"""


def check(checkout, *args, script=CHECK, opens=None):
    env = dict(F.ENV, HARNESS_PROJECT_DIR=checkout, CLAUDE_PROJECT_DIR=checkout)
    argv = [sys.executable, str(script), *args]
    if opens is not None:
        env["OPEN_LOG"] = opens
        argv = [sys.executable, "-c", WRAPPER, str(script), *args]
    proc = subprocess.run(argv, env=env, capture_output=True, text=True, cwd=checkout)
    return proc.returncode, proc.stdout + proc.stderr


def violations(out):
    return [l.strip() for l in out.splitlines() if l.strip().startswith("VIOLATION")]


class Case(unittest.TestCase):
    def setUp(self):
        ctx = F.sparse_fixture()
        self.fx = ctx.__enter__()
        self.addCleanup(ctx.__exit__, None, None, None)

    def sparse(self, name=ACTIVE):
        wt = self.fx.add_worktree(name)
        proc = subprocess.run([sys.executable, str(REPAIR), "--repair", "--checkout", wt],
                              env=F.ENV, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return wt

    def assert_no_invariant_ran(self, out):
        self.assertNotRegex(out, r"INV-\d+")
        self.assertNotIn("all state invariants hold", out)


class SubjectAndPopulation(Case):
    def test_sparse_and_full_agree_on_the_selected_subject(self):
        clone = self.fx.clone()
        wt = self.sparse()
        _c, full = check(clone, "--feature", ACTIVE)
        _s, sparse = check(wt)

        def subject(out, prefix):
            # Prefix first, then select: a line about the checkout itself contains the feature
            # id only through its path. INV-29 judges the worktree's own existence, which a
            # plain clone does not have — a checkout-class finding, not a subject finding.
            lines = (l.replace(prefix, "<checkout>") for l in out.splitlines())
            return sorted(l for l in lines if ACTIVE in l and "INV-29" not in l)
        self.assertTrue(subject(full, clone), full)
        self.assertEqual(subject(full, clone), subject(sparse, wt))

    def test_plain_clone_keeps_the_full_audit(self):
        _code, out = check(self.fx.clone())
        for fid in ("FEAT-1-alpha", "FEAT-2-beta", "FEAT-10-kaya-app"):
            self.assertIn(fid, out)
        self.assertNotIn("LAYOUT", out)

    def test_sparse_worktree_audits_only_its_active_feature(self):
        _code, out = check(self.sparse())
        self.assertIn(ACTIVE, out)
        for other in ("FEAT-2-beta", "FEAT-10-kaya-app", "BUG-3-gamma"):
            self.assertNotIn(other, out)

    def test_a_duplicate_branch_between_two_other_landed_features_is_seen(self):
        self.fx.commit_owner({
            ".harness/harness/features/FEAT-2-beta/feature.json": F.feature_json("FEAT-2-beta", "feat/dup"),
            ".harness/kaya/features/FEAT-10-kaya-app/feature.json":
                F.feature_json("FEAT-10-kaya-app", "feat/dup"),
        }, "two features claim one branch")
        _code, out = check(self.sparse())
        self.assertIn("INV-52: branch feat/dup is claimed by 2 landed features "
                      "(FEAT-10-kaya-app, FEAT-2-beta)", out)


class OpenConfinement(Case):
    def test_reads_stay_in_the_active_feature_and_declared_owner_records(self):
        wt = self.sparse()
        log = os.path.join(self.fx.base, "opens.log")
        check(wt, opens=log)
        opened = Path(log).read_text().splitlines()
        feature_path = re.compile(r"/\.harness/[^/]+/features/([^/]+)/(.+)$")
        local, owner = [], []
        for path in opened:
            m = feature_path.search(path)
            if not m:
                continue
            (local if path.startswith(wt + os.sep) else owner).append((m.group(1), m.group(2)))
        self.assertTrue(local, "instrumentation saw no local feature read at all")
        self.assertEqual(sorted({fid for fid, _rest in local}), [ACTIVE])
        # Owner-root opens: only the record files the repo-wide predicates declare.
        self.assertTrue(owner, "instrumentation saw no owner-root record read")
        self.assertEqual(sorted({rest for _fid, rest in owner}), ["feature.json"])


class Refusals(Case):
    def test_a_missing_selected_feature_refuses_before_any_invariant(self):
        code, out = check(self.fx.clone(), "--feature", "FEAT-9-gone")
        self.assertEqual(code, 1)
        self.assertIn("names no feature directory", out)
        self.assert_no_invariant_ran(out)

    def test_a_missing_recordless_directory_refuses_with_counts(self):
        clone = self.fx.clone()
        shutil.rmtree(os.path.join(clone, ".harness/harness/features/BUG-3-gamma"))
        code, out = check(clone)
        self.assertEqual(code, 1)
        self.assertIn("reaches 3 of 4 expected feature directories — missing: harness/BUG-3-gamma",
                      out)
        self.assert_no_invariant_ran(out)

    def test_an_untracked_extra_directory_is_reported_not_gating(self):
        clone = self.fx.clone()
        F.write_files(clone, {".harness/harness/features/FEAT-77-wip/notes/n.md": "wip\n"})
        _code, out = check(clone)
        self.assertIn("HEAD does not track: harness/FEAT-77-wip (not gating)", out)
        self.assertNotIn("FEATURE SET: this checkout reaches", out)

    def test_a_structural_break_refuses_before_any_invariant(self):
        wt = self.sparse()
        # Keeps .harness (so the checkout is still a harness root) but drops the active feature.
        F.git(wt, "sparse-checkout", "set", "--cone", "src", ".harness/notes")
        code, out = check(wt)
        self.assertEqual(code, 1)
        self.assertIn("LAYOUT cone (3)", out)
        self.assertIn(f"--repair --checkout {wt}", out)
        self.assert_no_invariant_ran(out)

    def test_dirty_alone_is_reported_and_the_audit_runs(self):
        wt = self.sparse()
        F.write_files(wt, {f".harness/harness/features/{ACTIVE}/BRIEF.md": "# edited\n"})
        _code, out = check(wt)
        self.assertIn("LAYOUT dirty (8)", out)
        self.assertNotIn(NO_INVARIANT_RAN, out)
        self.assertRegex(out, r"INV-\d+|all state invariants hold|BRIEF.md is NOT approved")

    def test_dirty_with_a_structural_break_still_refuses_structurally(self):
        wt = self.sparse()
        F.write_files(wt, {f".harness/harness/features/{ACTIVE}/BRIEF.md": "# edited\n"})
        F.write_files(wt, {".harness/harness/features/FEAT-2-beta/BRIEF.md": "# BRIEF FEAT-2-beta\n"})
        code, out = check(wt)
        self.assertEqual(code, 1)
        self.assertIn("LAYOUT materialisation (7)", out)
        self.assertIn("LAYOUT dirty (8)", out)
        self.assert_no_invariant_ran(out)

    def test_an_unusable_verify_report_refuses(self):
        wt = self.sparse()
        scratch = tempfile.mkdtemp(prefix="check-state-corpus-bin-")
        self.addCleanup(shutil.rmtree, scratch, True)
        bin_copy = isolated_bin(scratch)
        Path(bin_copy, "worktree-state.py").write_text("print('not a report')\n")
        code, out = check(wt, script=Path(bin_copy, "check-state.py"))
        self.assertEqual(code, 1)
        self.assertIn("without a JSON report", out)
        self.assert_no_invariant_ran(out)

    def test_list_stays_metadata_only(self):
        wt = self.sparse()
        F.git(wt, "sparse-checkout", "set", "--cone", "src")
        code, out = check(wt, "--list")
        self.assertEqual(code, 0)
        self.assertIn("INV-52", out)
        self.assertNotIn("LAYOUT", out)


if __name__ == "__main__":
    unittest.main()
