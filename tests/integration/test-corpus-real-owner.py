#!/usr/bin/env python3
"""Read-only checks against THIS repository's real owner root (FEAT-1559 SC-12, D-16).

A synthetic fixture agrees with itself by construction, so it cannot show a defect that exists
only because the real tree disagrees with itself — 89 feature directories against 79 records was
exactly that (PL-01). These cases read the real owner root and assert, with no census literal:

  * the names the corpus audit uses equal the feature directories HEAD tracks there, record-less
    historical directories included, from the owner AND from an active worktree caller;
  * more than 70 are reached (a non-vacuity floor, never an expected count);
  * check-state gets past its corpus choke point from both callers;
  * the same equality helper REJECTS a wrong-root override and a staged missing directory, both
    built from the T-01 fixture, so the green real-owner result is not a vacuous pass.

The only tree written is one disposable validator pin of this repository at the owner's current
HEAD, made and removed through pinned-checkout.py. Nothing else — no owner file, no live
worktree — is touched. A missing host prerequisite is announced and skipped, never passed.
"""
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BIN = ROOT / ".claude/skills/harness/bin"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(BIN))
import f58_sparse_fixture as F  # noqa: E402
import feature_corpus as fc  # noqa: E402

FLOOR = 70
REFUSED = ("FEATURE SET: this checkout reaches", "no invariant ran")


def skip(case, reason):
    print(f"SKIP (host prerequisite missing): {reason}")
    case.skipTest(reason)


def tracked_feature_dirs(owner):
    """Feature directories HEAD tracks at `owner`, by an independent route: `git ls-tree` per
    segment, not feature_corpus. Record-less directories count like any other."""
    found = set()
    segments = subprocess.run(["git", "ls-tree", "-d", "--name-only", "HEAD", ".harness/"],
                              cwd=owner, capture_output=True, text=True, check=True).stdout
    for seg_path in segments.split():
        names = subprocess.run(["git", "ls-tree", "-d", "--name-only", "HEAD",
                                f"{seg_path}/features/"],
                               cwd=owner, capture_output=True, text=True).stdout
        segment = seg_path.split("/", 1)[1]
        found.update(f"{segment}/{os.path.basename(n)}" for n in names.split())
    return found


def audit_mismatch(caller, disk_owner):
    """[] when the feature directories the corpus audit at `caller` REQUIRES — the landed names
    at its owner root — equal those HEAD tracks at `disk_owner`, and the population it judges
    holds every one; otherwise why not. The one equality every subject here is held to.

    Untracked extra directories are not compared: the audit reports them, not gating (SC-04),
    and a live owner can carry one."""
    try:
        landed = {f"{segment}/{fid}" for segment, fid, _path in
                  fc.landed_dirs(fc.owner_root(caller))}
        population = {f"{e['segment']}/{e['id']}" for e in fc.population(caller)}
    except fc.CorpusError as exc:
        return [f"the audit refused: {exc}"]
    expected = tracked_feature_dirs(disk_owner)
    out = []
    if landed != expected:
        out.append(f"the audit requires names other than those tracked at {disk_owner}: "
                   f"missing {sorted(expected - landed)}, extra {sorted(landed - expected)}")
    if not landed <= population:
        out.append(f"the judged population lacks {sorted(landed - population)}")
    return out


def check_state(root):
    env = dict(os.environ, HARNESS_PROJECT_DIR=root, CLAUDE_PROJECT_DIR=root,
               GH_BIN="/nonexistent-gh")
    proc = subprocess.run([sys.executable, str(BIN / "check-state.py")], env=env, cwd=root,
                          capture_output=True, text=True)
    return proc.stdout + proc.stderr


class RealOwner(unittest.TestCase):
    def setUp(self):
        try:
            self.owner = fc.owner_root(str(ROOT))
        except fc.CorpusError as exc:
            skip(self, f"no owner root resolves from {ROOT}: {exc}")
        self.linked = os.path.realpath(str(ROOT)) != self.owner

    def callers(self):
        out = [self.owner]
        if self.linked:
            out.append(str(ROOT))
        else:
            print(f"SKIP (host prerequisite missing): {ROOT} is the owner itself, so there is no "
                  f"active-worktree caller to compare")
        return out

    def test_audited_names_equal_the_tracked_directories(self):
        expected = tracked_feature_dirs(self.owner)
        self.assertGreater(len(expected), FLOOR)
        recordless = {f"{e['segment']}/{e['id']}" for e in fc.records(self.owner)
                      if e["record"] is None}
        self.assertTrue(recordless, "no record-less historical directory: the name-set "
                                    "comparison would not be exercising one")
        self.assertLessEqual(recordless, expected)
        for caller in self.callers():
            with self.subTest(caller=caller):
                self.assertEqual(audit_mismatch(caller, self.owner), [])

    def test_check_state_passes_the_corpus_choke_point(self):
        for caller in self.callers():
            with self.subTest(caller=caller):
                out = check_state(caller)
                for refusal in REFUSED:
                    self.assertNotIn(refusal, out)
                self.assertRegex(out, r"INV-\d+|all state invariants hold")


class TheEqualityRejectsMutants(unittest.TestCase):
    """The helper the real owner passes must fail a wrong root and a missing directory."""

    def setUp(self):
        ctx = F.sparse_fixture()
        self.fx = ctx.__enter__()
        self.addCleanup(ctx.__exit__, None, None, None)

    def test_a_correct_fixture_passes(self):
        self.assertEqual(audit_mismatch(self.fx.owner, self.fx.owner), [])

    def test_a_wrong_root_override_is_rejected(self):
        other = self.fx.clone("elsewhere")
        F.git(other, "rm", "-rq", ".harness/kaya")
        F.git(other, "commit", "-qm", "a different corpus")
        self.assertTrue(audit_mismatch(other, self.fx.owner))

    def test_a_staged_missing_directory_is_rejected(self):
        clone = self.fx.clone()
        shutil.rmtree(os.path.join(clone, ".harness/harness/features/BUG-3-gamma"))
        found = audit_mismatch(clone, clone)
        self.assertTrue(found)
        self.assertIn("harness/BUG-3-gamma", found[0])


class DisposablePin(unittest.TestCase):
    """One real pin of this repository at the owner's current HEAD: dirty is reported and the
    audit runs; a structural break refuses before any invariant."""

    def setUp(self):
        try:
            self.owner = fc.owner_root(str(ROOT))
        except fc.CorpusError as exc:
            skip(self, f"no owner root resolves from {ROOT}: {exc}")
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.owner,
                              capture_output=True, text=True)
        if head.returncode != 0:
            skip(self, f"owner HEAD does not resolve at {self.owner}")
        self.sha = head.stdout.strip()
        landed = [e for e in fc.records(self.owner) if e["document"] is not None]
        if len(landed) < 2:
            skip(self, "the owner has fewer than two landed feature records")
        self.active, self.other = landed[0], landed[-1]
        self.key = ["--feature", self.active["id"], "--run-id", f"f1559-{os.getpid()}",
                    "--persona", "probe"]
        proc = self.pins("add", "--sha", self.sha)
        if proc.returncode != 0:
            skip(self, f"pinned-checkout.py add failed: {proc.stderr.strip()}")
        self.addCleanup(self.pins, "remove")
        self.pin = proc.stdout.strip().splitlines()[-1]
        print(f"probe pin {self.pin} at {self.sha} (owner {self.owner})")
        repaired = subprocess.run([sys.executable, str(BIN / "worktree-state.py"), "--repair",
                                   "--checkout", self.pin], capture_output=True, text=True)
        self.assertEqual(repaired.returncode, 0, repaired.stdout + repaired.stderr)

    def pins(self, verb, *extra):
        return subprocess.run([sys.executable, str(BIN / "pinned-checkout.py"), verb, *self.key,
                               *extra], cwd=self.owner, capture_output=True, text=True)

    def rel(self, entry, name):
        return os.path.join(".harness", entry["segment"], "features", entry["id"], name)

    def test_dirty_is_reported_and_a_structural_break_refuses(self):
        self.assertEqual(os.path.basename(self.pin),
                         f"{self.active['id']}--f1559-{os.getpid()}--probe")
        with open(os.path.join(self.pin, self.rel(self.active, "feature.json")), "a") as fh:
            fh.write("\n")
        out = check_state(self.pin)
        self.assertIn("LAYOUT dirty (8)", out)
        for refusal in REFUSED:
            self.assertNotIn(refusal, out)

        other = self.rel(self.other, "feature.json")
        target = os.path.join(self.pin, other)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        shutil.copyfile(os.path.join(self.owner, other), target)   # byte-identical: class B
        out = check_state(self.pin)
        self.assertIn("LAYOUT materialisation (7)", out)
        self.assertIn("no invariant ran", out)


if __name__ == "__main__":
    unittest.main()
