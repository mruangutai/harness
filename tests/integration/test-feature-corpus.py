#!/usr/bin/env python3
"""Reads and gates over the main corpus from sparse checkouts (FEAT-1559 SC-02, SC-04, SC-05).

Every subject is a real worktree or pin of the synthetic owner in f58_sparse_fixture, converged
with worktree-state.py --repair first, so it holds its own feature directory and no other. The
gates run as subprocesses through their registered entrypoints with a hook payload on stdin. A
gate's decision is read from its printed permissionDecision, never from its exit status: both
gates exit 0 on a deny (FEAT-58 D-17).
"""
import json
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

ACTIVE = "FEAT-1-alpha"
MANIFEST = """schema_version: 1
teams:
  - name: build
    members:
      - name: harness-documentor
        domain:
          - { path: .harness/*/features/**, upsert: true }
          - { path: ".", read: true }
"""
GITHUB_ON = '{"github": {"sync": true, "repo": "o/r"}}\n'


def repair(checkout):
    proc = subprocess.run([sys.executable, str(BIN / "worktree-state.py"), "--repair",
                           "--checkout", checkout], env=F.ENV, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return checkout


def hook(script, checkout, payload, extra_env=None):
    env = dict(F.ENV, HARNESS_PROJECT_DIR=checkout, CLAUDE_PROJECT_DIR=checkout,
               GH_BIN="/nonexistent-gh", **(extra_env or {}))
    return subprocess.run([sys.executable, str(BIN / script)], input=json.dumps(payload),
                          env=env, capture_output=True, text=True, cwd=checkout)


def decision(proc):
    """The permissionDecision a gate printed, or None when it printed none (an allow)."""
    for line in proc.stdout.splitlines():
        try:
            doc = json.loads(line)
        except json.JSONDecodeError:
            continue
        out = (doc.get("hookSpecificOutput") or {}) if isinstance(doc, dict) else {}
        if "permissionDecision" in out:
            return out["permissionDecision"], out.get("permissionDecisionReason", "")
    return None, ""


class Case(unittest.TestCase):
    def setUp(self):
        ctx = F.sparse_fixture()
        self.fx = ctx.__enter__()
        self.addCleanup(ctx.__exit__, None, None, None)


class CrossCheckoutReads(Case):
    """SC-02: from inside each checkout class, another landed feature is read at the owner
    root, byte for byte, and does not exist locally."""

    def assert_reads(self, checkout, other_segment, other):
        owner_dir = Path(self.fx.owner, ".harness", other_segment, "features", other)
        local_dir = Path(checkout, ".harness", other_segment, "features", other)
        self.assertFalse(local_dir.exists(), f"{other} is materialised in {checkout}")
        owner = fc.owner_root(checkout)
        self.assertEqual(owner, os.path.realpath(self.fx.owner))
        landed = {e["id"]: e for e in fc.records(owner)}
        self.assertIn(other, landed)
        for rel in ("BRIEF.md", sorted(os.listdir(owner_dir / "notes"))[0]):
            path = owner_dir / rel if rel == "BRIEF.md" else owner_dir / "notes" / rel
            with open(path, "rb") as fh:                      # an ordinary absolute read
                got = fh.read()
            want = F.git(self.fx.owner, "show", f"HEAD:{path.relative_to(self.fx.owner)}").stdout
            self.assertEqual(got.decode(), want)

    def test_harness_feature_worktree(self):
        wt = repair(self.fx.add_worktree(ACTIVE))
        self.assert_reads(wt, "harness", "FEAT-2-beta")

    def test_fleet_planning_worktree_reads_across_segments(self):
        wt = repair(self.fx.add_worktree("FEAT-10-kaya-app"))
        self.assertEqual(F.feature_dirs_on_disk(wt), ["kaya/FEAT-10-kaya-app"])
        self.assert_reads(wt, "harness", "FEAT-2-beta")

    def test_validator_pin(self):
        pin = repair(self.fx.add_pin("FEAT-2-beta"))
        self.assert_reads(pin, "kaya", "FEAT-10-kaya-app")

    def test_an_unavailable_owner_root_refuses_by_name(self):
        wt = repair(self.fx.add_worktree(ACTIVE))
        os.rename(os.path.join(self.fx.owner, ".harness", "team-config.yaml"),
                  os.path.join(self.fx.owner, ".harness", "team-config.moved"))
        with self.assertRaises(fc.CorpusError) as caught:
            fc.population(wt)
        self.assertIn(os.path.realpath(self.fx.owner), str(caught.exception))

    def test_a_missing_landed_path_refuses_by_name(self):
        wt = repair(self.fx.add_worktree(ACTIVE))
        shutil.rmtree(os.path.join(self.fx.owner, ".harness/harness/features/BUG-3-gamma"))
        with self.assertRaises(fc.CorpusError) as caught:
            fc.population(wt)
        self.assertIn("harness/BUG-3-gamma", str(caught.exception))

    def test_an_in_progress_sibling_is_never_read(self):
        wt = repair(self.fx.add_worktree(ACTIVE))
        sibling = repair(self.fx.add_worktree("FEAT-50-wip"))
        F.write_files(sibling, {".harness/harness/features/FEAT-50-wip/feature.json":
                                F.feature_json("FEAT-50-wip", "feat/FEAT-50-wip")})
        ids = [e["id"] for e in fc.population(wt)]
        self.assertNotIn("FEAT-50-wip", ids)
        self.assertIn("FEAT-2-beta", ids)


class MergeGate(Case):
    def setUp(self):
        super().setUp()
        self.fx.commit_owner({".harness/harness.json": GITHUB_ON}, "sync on")

    def merge(self, checkout, branch):
        return hook("merge-gate.py", checkout, {
            "tool_name": "Bash", "tool_input": {"command": f"git merge {branch}"}})

    def test_a_duplicate_claim_between_two_other_landed_features_is_denied(self):
        self.fx.commit_owner({
            ".harness/harness/features/FEAT-2-beta/feature.json": F.feature_json("FEAT-2-beta", "feat/dup"),
            ".harness/kaya/features/FEAT-10-kaya-app/feature.json":
                F.feature_json("FEAT-10-kaya-app", "feat/dup"),
        }, "two claims")
        wt = repair(self.fx.add_worktree(ACTIVE))
        verdict, reason = decision(self.merge(wt, "feat/dup"))
        self.assertEqual(verdict, "deny")
        self.assertIn("FEAT-10-kaya-app, FEAT-2-beta", reason)

    def test_a_single_receipted_owner_is_allowed(self):
        doc = json.loads(F.feature_json("FEAT-2-beta", "feat/FEAT-2-beta"))
        doc["github"] = {"build_entry": "opened"}
        self.fx.commit_owner({".harness/harness/features/FEAT-2-beta/feature.json":
                              json.dumps(doc) + "\n"}, "receipt")
        wt = repair(self.fx.add_worktree(ACTIVE))
        proc = self.merge(wt, "feat/FEAT-2-beta")
        self.assertEqual(decision(proc), (None, ""), proc.stdout + proc.stderr)

    def test_a_missing_landed_directory_denies(self):
        wt = repair(self.fx.add_worktree(ACTIVE))
        shutil.rmtree(os.path.join(self.fx.owner, ".harness/harness/features/BUG-3-gamma"))
        verdict, reason = decision(self.merge(wt, "feat/FEAT-2-beta"))
        self.assertEqual(verdict, "deny")
        self.assertIn("harness/BUG-3-gamma", reason)

    def test_a_broken_layout_denies(self):
        wt = repair(self.fx.add_worktree(ACTIVE))
        F.write_files(wt, {".harness/harness/features/FEAT-2-beta/BRIEF.md": "# BRIEF FEAT-2-beta\n"})
        verdict, reason = decision(self.merge(wt, "feat/FEAT-2-beta"))
        self.assertEqual(verdict, "deny")
        self.assertIn("materialisation (7)", reason)


class BranchCreateGate(Case):
    def setUp(self):
        super().setUp()
        self.fx.commit_owner({".harness/harness.json": GITHUB_ON}, "sync on")

    def branch(self, checkout, name):
        return hook("branch-create-gate.py", checkout, {
            "tool_name": "Bash", "tool_input": {"command": f"git checkout -b {name}"}})

    def test_a_flow_landed_at_the_owner_and_absent_here_is_allowed(self):
        # ALLOW FIRST: a gate that denies everything passes every deny case below.
        wt = repair(self.fx.add_worktree(ACTIVE))
        self.assertFalse(os.path.isdir(os.path.join(wt, ".harness/harness/features/FEAT-2-beta")))
        proc = self.branch(wt, "feat/FEAT-2-beta")
        self.assertEqual(decision(proc), (None, ""), proc.stdout + proc.stderr)
        self.assertIn("Branch maps to flow FEAT-2-beta", proc.stdout)
        proc = self.branch(wt, "feat/FEAT-10-kaya-app")
        self.assertEqual(decision(proc), (None, ""), proc.stdout)

    def test_an_unknown_flow_is_denied(self):
        wt = repair(self.fx.add_worktree(ACTIVE))
        verdict, reason = decision(self.branch(wt, "feat/FEAT-404-nope"))
        self.assertEqual(verdict, "deny")
        self.assertIn("FEAT-404-nope", reason)

    def test_a_broken_layout_denies(self):
        wt = repair(self.fx.add_worktree(ACTIVE))
        F.git(wt, "sparse-checkout", "set", "--cone", "src", ".harness/notes")
        verdict, reason = decision(self.branch(wt, "feat/FEAT-2-beta"))
        self.assertEqual(verdict, "deny")
        self.assertIn("cone (3)", reason)


class WriteGuards(Case):
    """A governed write INTO the main corpus is refused on both registered routes; the same
    session's write to its own feature passes. The guards decide by exit status 2 (DEC-100)."""

    def setUp(self):
        super().setUp()
        self.fx.commit_owner({".harness/team-config.yaml": MANIFEST}, "grant features")
        self.wt = repair(self.fx.add_worktree(ACTIVE))
        self.target = os.path.join(self.fx.owner, ".harness/harness/features/FEAT-2-beta/BRIEF.md")
        self.own = os.path.join(self.wt, f".harness/harness/features/{ACTIVE}/notes/n.md")

    def write(self, path):
        return hook("check-domain.py", self.wt, {
            "agent_type": "harness-documentor", "tool_name": "Write",
            "tool_input": {"file_path": path, "content": "x"}})

    def bash(self, path):
        return hook("bash-write-guard.py", self.wt, {
            "agent_type": "harness-documentor", "tool_name": "Bash",
            "tool_input": {"command": f"echo x > {path}"}})

    def test_write_route(self):
        own = self.write(self.own)
        self.assertEqual(own.returncode, 0, own.stderr)
        into = self.write(self.target)
        self.assertEqual(into.returncode, 2, into.stderr)

    def test_bash_route(self):
        own = self.bash(self.own)
        self.assertEqual(own.returncode, 0, own.stderr)
        into = self.bash(self.target)
        self.assertEqual(into.returncode, 2, into.stderr)


class BoardStatus(Case):
    """The board audit judges the landed corpus from a sparse worktree (SC-04): a landed feature
    with an active plan is compared against its cards even though this checkout does not hold it,
    and a broken layout reports the corpus unreadable instead of auditing a smaller set."""

    OTHER = ".harness/harness/features/FEAT-2-beta"
    # A schema-valid plan: an invalid one reads as "no plan", which projects no card at all.
    PLAN = ("status: building\ntasks:\n  - id: T-01\n    title: fixture task\n"
            "    change_type: bugfix\n    execution_mode: team\n    files: [fixture.py]\n"
            "    verify: python3 test.py\n    intent: fixture\n    status: building\n")

    def setUp(self):
        super().setUp()
        import board_lifecycle
        self.bl = board_lifecycle
        record = json.loads(F.feature_json("FEAT-2-beta", "feat/FEAT-2-beta"))
        record["github"] = {"issues": {"T-01": 501}, "parent": 500}
        self.fx.commit_owner({f"{self.OTHER}/feature.json": json.dumps(record) + "\n",
                              f"{self.OTHER}/plan.yaml": self.PLAN}, "FEAT-2-beta is building")
        self.wt = repair(self.fx.add_worktree(ACTIVE))

    def messages(self, stations):
        return [f.message for f in self.bl._status_findings(self.wt, None, stations)]

    def test_a_landed_feature_absent_here_is_audited_against_its_cards(self):
        self.assertFalse(os.path.exists(os.path.join(self.wt, self.OTHER)))
        wrong = self.messages({500: "building", 501: "ready"})
        self.assertTrue(any("card #501" in m and "'ready'" in m for m in wrong), wrong)
        self.assertEqual(self.messages({500: "building", 501: "building"}), [])

    def test_a_broken_layout_reports_the_corpus_unreadable(self):
        F.write_files(self.wt, {f"{self.OTHER}/BRIEF.md": "# BRIEF FEAT-2-beta\n"})
        found = self.messages({500: "building", 501: "building"})
        self.assertEqual(len(found), 1, found)
        self.assertIn("feature cards cannot be audited", found[0])


class DecisionAnchors(Case):
    """A decision anchor citing another landed feature's file is counted in the main corpus,
    which a sparse worktree does not hold (SC-02); an unreachable corpus exits 2, never 1."""

    # history.md exists only under BUG-3-gamma, so the basename has exactly one candidate.
    DOC = "Cited: `.harness/harness/features/BUG-3-gamma/notes/deep/history.md:1`.\n"

    def anchors(self):
        wt = repair(self.fx.add_worktree(ACTIVE))
        self.assertFalse(os.path.exists(os.path.join(wt, ".harness/harness/features/BUG-3-gamma")))
        doc = os.path.join(self.fx.base, "DECISIONS.md")
        with open(doc, "w", encoding="utf-8") as fh:
            fh.write(self.DOC)
        return lambda: subprocess.run(
            [sys.executable, str(BIN / "check-decision-anchors.py"), "--file", doc],
            env=dict(F.ENV, HARNESS_PROJECT_DIR=wt), capture_output=True, text=True, cwd=wt)

    def test_another_landed_features_file_is_counted_in_the_main_corpus(self):
        proc = self.anchors()()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("examined 1 anchor(s), 0 failed", proc.stdout)

    def test_an_unreachable_main_corpus_exits_two(self):
        run = self.anchors()
        os.rename(os.path.join(self.fx.owner, ".harness", "team-config.yaml"),
                  os.path.join(self.fx.owner, ".harness", "team-config.moved"))
        proc = run()
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("cannot check", proc.stderr)


class Discovery(Case):
    """Repo-wide discovery from a sparse worktree sees the landed corpus, not one directory."""

    def test_validate_feature_json_scans_every_landed_record(self):
        wt = repair(self.fx.add_worktree(ACTIVE))
        proc = subprocess.run([sys.executable, str(BIN / "validate-feature-json.py")],
                              env=dict(F.ENV, HARNESS_PROJECT_DIR=wt), capture_output=True,
                              text=True, cwd=wt)
        self.assertIn("— 3 file(s)", proc.stderr)          # FEAT-1, FEAT-2, FEAT-10

    def test_validate_feature_json_refuses_a_broken_layout(self):
        wt = repair(self.fx.add_worktree(ACTIVE))
        F.write_files(wt, {".harness/harness/features/FEAT-2-beta/BRIEF.md": "# BRIEF FEAT-2-beta\n"})
        proc = subprocess.run([sys.executable, str(BIN / "validate-feature-json.py")],
                              env=dict(F.ENV, HARNESS_PROJECT_DIR=wt), capture_output=True,
                              text=True, cwd=wt)
        self.assertEqual(proc.returncode, 3, proc.stderr)
        self.assertIn("cannot establish the feature corpus", proc.stderr)

    def routes(self, checkout):
        proc = subprocess.run([sys.executable, str(BIN / "check-plan-routes.py")],
                              env=dict(F.ENV, HARNESS_PROJECT_DIR=checkout), capture_output=True,
                              text=True, cwd=checkout)
        return proc.returncode, proc.stdout + proc.stderr

    def test_check_plan_routes_examines_the_landed_corpus(self):
        code, out = self.routes(repair(self.fx.add_worktree(ACTIVE)))
        self.assertIn("examined 4 feature dir(s)", out)
        self.assertNotEqual(code, 2, out)

    def test_check_plan_routes_refuses_a_missing_landed_directory_by_name(self):
        # SC-04: one landed directory gone while the others remain must refuse by name, N of M,
        # before any plan is walked — not route-check the survivors and report a clean total.
        wt = repair(self.fx.add_worktree(ACTIVE))
        shutil.rmtree(os.path.join(self.fx.owner, ".harness/harness/features/FEAT-2-beta"))
        code, out = self.routes(wt)
        self.assertEqual(code, 2, out)
        self.assertIn("reaches 3 of 4 tracked feature directories; missing: harness/FEAT-2-beta",
                      out)
        self.assertNotIn("examined", out)

    def test_check_plan_routes_refuses_a_missing_directory_in_a_full_clone(self):
        clone = self.fx.clone()
        shutil.rmtree(os.path.join(clone, ".harness/kaya/features/FEAT-10-kaya-app"))
        code, out = self.routes(clone)
        self.assertEqual(code, 2, out)
        self.assertIn("missing: kaya/FEAT-10-kaya-app", out)


if __name__ == "__main__":
    unittest.main()
