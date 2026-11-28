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

from integration_support import BIN
from harness_config_support import build_config  # noqa: E402
import f58_sparse_fixture as F  # noqa: E402
import git_support as G  # noqa: E402
import feature_corpus as fc  # noqa: E402
import layout_migration  # noqa: E402
import factory_config  # noqa: E402
import board_lifecycle  # noqa: E402

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
GITHUB_ON = json.dumps(build_config({"github": {"sync": True, "repo": "o/r", "board": None}})) + "\n"


def repair(checkout):
    proc = subprocess.run([sys.executable, str(BIN / "worktree-state.py"), "--repair",
                           "--checkout", checkout], env=G.ENV, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return checkout


def run(checkout, script, *args, payload=None, **env):
    """Run bin/<script> from inside checkout, with HARNESS_PROJECT_DIR naming it."""
    stdin = None if payload is None else json.dumps(payload)
    return subprocess.run([sys.executable, str(BIN / script), *args], input=stdin,
                          env=dict(G.ENV, HARNESS_PROJECT_DIR=checkout, **env),
                          capture_output=True, text=True, cwd=checkout)


def hook(script, checkout, payload):
    return run(checkout, script, payload=payload, GH_BIN="/nonexistent-gh")


def record(fid, branch, **extra):
    """F.feature_json for fid on branch, with extra top-level keys merged in."""
    return json.dumps({**json.loads(F.feature_json(fid, branch)), **extra}) + "\n"


def hide_owner_config(fx):
    harness = os.path.join(fx.owner, ".harness")
    os.rename(os.path.join(harness, "team-config.yaml"), os.path.join(harness, "team-config.moved"))


def drop_landed(fx, rel):
    shutil.rmtree(os.path.join(fx.owner, rel))


def materialise_other(wt):
    F.write_files(wt, {".harness/harness/features/FEAT-2-beta/BRIEF.md": "# BRIEF FEAT-2-beta\n"})


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
        self.fx = self.enterContext(F.sparse_fixture())

    def active(self):
        return repair(self.fx.add_worktree(ACTIVE))


class SyncOn(Case):
    def setUp(self):
        super().setUp()
        self.fx.commit_owner({".harness/harness.json": GITHUB_ON}, "sync on")


class CrossCheckoutReads(Case):
    """SC-02: from inside each checkout class, another landed feature is read at the owner
    root, byte for byte, and does not exist locally."""

    def assert_reads(self, checkout, other_segment, other):
        owner_dir = Path(self.fx.owner, ".harness", other_segment, "features", other)
        local_dir = Path(checkout, ".harness", other_segment, "features", other)
        self.assertFalse(local_dir.exists(), f"{other} is materialised in {checkout}")
        owner = fc.owner_root(checkout)
        self.assertEqual(owner, os.path.realpath(self.fx.owner))
        self.assertIn(other, [e["id"] for e in fc.records(owner)])
        for path in (owner_dir / "BRIEF.md", min((owner_dir / "notes").iterdir())):
            got = path.read_bytes()                           # an ordinary absolute read
            want = G.git(self.fx.owner, "show", f"HEAD:{path.relative_to(self.fx.owner)}").stdout
            self.assertEqual(got.decode(), want)

    def test_harness_feature_worktree(self):
        wt = self.active()
        self.assert_reads(wt, "harness", "FEAT-2-beta")

    def test_fleet_planning_worktree_reads_across_segments(self):
        wt = repair(self.fx.add_worktree("FEAT-10-kaya-app"))
        self.assertEqual(F.feature_dirs_on_disk(wt), ["kaya/FEAT-10-kaya-app"])
        self.assert_reads(wt, "harness", "FEAT-2-beta")

    def test_validator_pin(self):
        pin = repair(self.fx.add_pin("FEAT-2-beta"))
        self.assert_reads(pin, "kaya", "FEAT-10-kaya-app")

    def test_an_unavailable_owner_root_refuses_by_name(self):
        wt = self.active()
        hide_owner_config(self.fx)
        with self.assertRaises(fc.CorpusError) as caught:
            fc.population(wt)
        self.assertIn(os.path.realpath(self.fx.owner), str(caught.exception))

    def test_a_missing_landed_path_refuses_by_name(self):
        wt = self.active()
        drop_landed(self.fx, ".harness/harness/features/BUG-3-gamma")
        with self.assertRaises(fc.CorpusError) as caught:
            fc.population(wt)
        self.assertIn("harness/BUG-3-gamma", str(caught.exception))

    def test_a_missing_active_directory_is_missing_not_a_landed_copy(self):
        # The checkout's own feature is decided by identity, not by its directory existing: a
        # deleted active directory must not be answered from stale landed bytes (#2103 panel 6).
        # One worktree named by its directory, one only by its feat/<id> branch.
        for wt, own, other in ((self.active(), ACTIVE, "FEAT-2-beta"),
                               (repair(self.fx.add_worktree("scratch", branch="feat/FEAT-2-beta")),
                                "FEAT-2-beta", ACTIVE)):
            rel = f".harness/harness/features/{own}/BRIEF.md"
            shutil.rmtree(os.path.join(wt, os.path.dirname(rel)))
            self.assertEqual(fc.corpus_path(wt, rel), os.path.join(wt, rel))
            elsewhere = f".harness/harness/features/{other}/BRIEF.md"
            self.assertEqual(fc.corpus_path(wt, elsewhere), os.path.join(self.fx.owner, elsewhere))

    def test_an_in_progress_sibling_is_never_read(self):
        wt = self.active()
        sibling = repair(self.fx.add_worktree("FEAT-50-wip"))
        F.write_files(sibling, {".harness/harness/features/FEAT-50-wip/feature.json":
                                F.feature_json("FEAT-50-wip", "feat/FEAT-50-wip")})
        ids = [e["id"] for e in fc.population(wt)]
        self.assertNotIn("FEAT-50-wip", ids)
        self.assertIn("FEAT-2-beta", ids)


class MergeGate(SyncOn):

    def merge(self, checkout, branch):
        return hook("merge-gate.py", checkout, {
            "tool_name": "Bash", "tool_input": {"command": f"git merge {branch}"}})

    def test_a_duplicate_claim_between_two_other_landed_features_is_denied(self):
        self.fx.commit_owner({
            ".harness/harness/features/FEAT-2-beta/feature.json": F.feature_json("FEAT-2-beta", "feat/dup"),
            ".harness/kaya/features/FEAT-10-kaya-app/feature.json":
                F.feature_json("FEAT-10-kaya-app", "feat/dup"),
        }, "two claims")
        wt = self.active()
        verdict, reason = decision(self.merge(wt, "feat/dup"))
        self.assertEqual(verdict, "deny")
        self.assertIn("FEAT-10-kaya-app, FEAT-2-beta", reason)

    def test_a_single_receipted_owner_is_allowed(self):
        self.fx.commit_owner({".harness/harness/features/FEAT-2-beta/feature.json": record(
            "FEAT-2-beta", "feat/FEAT-2-beta", github={"repo": "o/r", "build_entry": "opened"})},
            "receipt")
        wt = self.active()
        # FEAT-2225: the gate must read the merge's changed paths, so the ref has to exist.
        G.git(wt, "branch", "feat/FEAT-2-beta")
        proc = self.merge(wt, "feat/FEAT-2-beta")
        self.assertEqual(decision(proc), (None, ""), proc.stdout + proc.stderr)

    def test_a_missing_landed_directory_denies(self):
        wt = self.active()
        drop_landed(self.fx, ".harness/harness/features/BUG-3-gamma")
        verdict, reason = decision(self.merge(wt, "feat/FEAT-2-beta"))
        self.assertEqual(verdict, "deny")
        self.assertIn("harness/BUG-3-gamma", reason)

    def test_a_broken_layout_denies(self):
        wt = self.active()
        materialise_other(wt)
        verdict, reason = decision(self.merge(wt, "feat/FEAT-2-beta"))
        self.assertEqual(verdict, "deny")
        self.assertIn("materialisation (7)", reason)

    def test_one_id_claimed_from_two_segments_is_two_owners_and_denies(self):
        # Same id, two segments, one branch: both records must reach the owner count, or the
        # gate sees one owner and lets an unattributable merge through.
        self.fx.commit_owner({
            ".harness/harness/features/FEAT-2-beta/feature.json": F.feature_json("FEAT-2-beta", "feat/dup"),
            ".harness/kaya/features/FEAT-2-beta/feature.json": F.feature_json("FEAT-2-beta", "feat/dup"),
        }, "one id, two segments, one branch")
        wt = self.active()
        verdict, reason = decision(self.merge(wt, "feat/dup"))
        self.assertEqual(verdict, "deny", reason)
        self.assertIn("claimed by more than one feature record (FEAT-2-beta, FEAT-2-beta)", reason)


class SegmentIdentity(Case):
    """A feature directory is `<segment>/<id>`: one id in two segments is two features, and this
    checkout's copy replaces only the landed directory with the same segment AND id (SC-04)."""

    def setUp(self):
        super().setUp()
        self.fx.commit_owner({".harness/kaya/features/FEAT-2-beta/feature.json":
                              F.feature_json("FEAT-2-beta", "feat/kaya-beta")}, "same id in kaya")

    def test_a_shared_id_is_two_entries_from_a_worktree_and_from_a_clone(self):
        for checkout in (self.active(), self.fx.clone()):
            entries = fc.population(checkout)
            keys = [(e["segment"], e["id"]) for e in entries]
            self.assertIn(("harness", "FEAT-2-beta"), keys)
            self.assertIn(("kaya", "FEAT-2-beta"), keys)
            self.assertEqual(len(keys), len(set(keys)), keys)
            self.assertEqual(len(keys), 5, keys)       # FEAT-1, FEAT-2 x2, BUG-3, FEAT-10

    def test_this_checkouts_copy_replaces_only_its_own_directory(self):
        wt = self.active()
        by_key = {(e["segment"], e["id"]): e for e in fc.population(wt)}
        self.assertEqual(by_key[("harness", ACTIVE)]["path"],
                         os.path.join(wt, ".harness/harness/features", ACTIVE))
        for key in (("harness", "FEAT-2-beta"), ("kaya", "FEAT-2-beta")):
            self.assertEqual(by_key[key]["path"],
                             os.path.join(self.fx.owner, ".harness", key[0], "features", key[1]))


class BranchCreateGate(SyncOn):

    def branch(self, checkout, name):
        return hook("branch-create-gate.py", checkout, {
            "tool_name": "Bash", "tool_input": {"command": f"git checkout -b {name}"}})

    def test_a_flow_landed_at_the_owner_and_absent_here_is_allowed(self):
        # ALLOW FIRST: a gate that denies everything passes every deny case below.
        wt = self.active()
        self.assertFalse(os.path.isdir(os.path.join(wt, ".harness/harness/features/FEAT-2-beta")))
        proc = self.branch(wt, "feat/FEAT-2-beta")
        self.assertEqual(decision(proc), (None, ""), proc.stdout + proc.stderr)
        self.assertIn("Branch maps to flow FEAT-2-beta", proc.stdout)
        proc = self.branch(wt, "feat/FEAT-10-kaya-app")
        self.assertEqual(decision(proc), (None, ""), proc.stdout)

    def test_an_unknown_flow_is_denied(self):
        wt = self.active()
        verdict, reason = decision(self.branch(wt, "feat/FEAT-404-nope"))
        self.assertEqual(verdict, "deny")
        self.assertIn("FEAT-404-nope", reason)

    def test_a_broken_layout_denies(self):
        wt = self.active()
        G.git(wt, "sparse-checkout", "set", "--cone", "src", ".harness/notes")
        verdict, reason = decision(self.branch(wt, "feat/FEAT-2-beta"))
        self.assertEqual(verdict, "deny")
        self.assertIn("cone (3)", reason)


class WriteGuards(Case):
    """A governed write INTO the main corpus is refused on both registered routes; the same
    session's write to its own feature passes. The guards decide by exit status 2 (DEC-100)."""

    def setUp(self):
        super().setUp()
        self.fx.commit_owner({".harness/team-config.yaml": MANIFEST}, "grant features")
        self.wt = self.active()
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
        self.board = {"owner": "o", "number": 9, "station_field": "Status",
                      "stations": list(factory_config.MANDATED_STATIONS)}
        github = {"repo": "o/r", "issues": {"T-01": 501}, "parent": 500}
        self.fx.commit_owner({f"{self.OTHER}/feature.json": record(
                                  "FEAT-2-beta", "feat/FEAT-2-beta", github=github),
                              f"{self.OTHER}/plan.yaml": self.PLAN,
                              ".harness/harness.json": json.dumps(build_config({"github": {
                                  "sync": True, "repo": "o/r", "board": self.board}})) + "\n"},
                             "FEAT-2-beta is building")
        self.wt = self.active()

    def messages(self, stations):
        return [f.message for f in board_lifecycle._status_findings(self.wt, self.board, stations, "o/r")]

    def test_a_landed_feature_absent_here_is_audited_against_its_cards(self):
        self.assertFalse(os.path.exists(os.path.join(self.wt, self.OTHER)))
        wrong = self.messages({500: "building", 501: "ready"})
        self.assertTrue(any("card #501" in m and "'ready'" in m for m in wrong), wrong)
        self.assertEqual(self.messages({500: "building", 501: "building"}), [])

    def test_a_broken_layout_reports_the_corpus_unreadable(self):
        materialise_other(self.wt)
        found = self.messages({500: "building", 501: "building"})
        self.assertEqual(len(found), 1, found)
        self.assertIn("feature cards cannot be audited", found[0])

    def test_one_id_active_in_two_segments_is_audited_in_both(self):
        github = {"repo": "o/r", "issues": {"T-01": 601}, "parent": 600}
        kaya = ".harness/kaya/features/FEAT-2-beta"
        self.fx.commit_owner({f"{kaya}/feature.json": record(
                                  "FEAT-2-beta", "feat/kaya-beta", github=github),
                              f"{kaya}/plan.yaml": self.PLAN}, "kaya FEAT-2-beta is building")
        wrong = self.messages({500: "building", 501: "ready", 600: "building", 601: "ready"})
        self.assertTrue(any("card #501" in m for m in wrong), wrong)
        self.assertTrue(any("card #601" in m for m in wrong), wrong)


class FactoryClaim(Case):
    """The factory claim lane reads another feature's plan and issue map in the main corpus:
    from a sparse worktree, a landed feature's plan is not 'missing' (#2103 panel, finding 1)."""

    PLAN = json.dumps({"schema": "plan/1", "feature": "FEAT-2-beta",
                       "approval": {"status": "approved"},
                       "tasks": [{"id": "T-01", "title": "task", "change_type": "feature",
                                  "execution_mode": "team", "files": ["src/app.py"],
                                  "verify": "true", "intent": "test claim",
                                  "traces": ["REQ-03"]}]}) + "\n"
    PROBE = ("import sys; sys.path.insert(0, {bin!r}); import factory_claim as c; "
             "cache = c._BlockerCache(); "
             "print(repr(c._blocker_gate(cache, 'org/harness', 'FEAT-2-beta', 'T-01'))); "
             "print(repr(cache.issue_number('org/harness', 'FEAT-2-beta', 'T-01')))")

    def test_a_landed_plan_and_issue_map_are_read_from_a_sparse_worktree(self):
        factory = {"repo": "org/harness", "issues": {"T-01": 77}}
        base = ".harness/harness/features/FEAT-2-beta"
        self.fx.commit_owner({f"{base}/plan.yaml": self.PLAN,
                              f"{base}/feature.json": record(
                                  "FEAT-2-beta", "feat/FEAT-2-beta", factory=factory)},
                             "landed plan")
        wt = self.active()
        self.assertFalse(os.path.exists(os.path.join(wt, base)))
        proc = subprocess.run([sys.executable, "-c", self.PROBE.format(bin=str(BIN))],
                              env=dict(G.ENV, HARNESS_PROJECT_DIR=wt), cwd=wt,
                              capture_output=True, text=True)
        self.assertEqual(proc.stdout.split("\n")[:2], ["None", "77"], proc.stdout + proc.stderr)


class DecisionAnchors(Case):
    """A decision anchor citing another landed feature's file is counted in the main corpus,
    which a sparse worktree does not hold (SC-02); an unreachable corpus exits 2, never 1."""

    # history.md exists only under BUG-3-gamma, so the basename has exactly one candidate.
    DOC = "Cited: `.harness/harness/features/BUG-3-gamma/notes/deep/history.md:1`.\n"

    def setUp(self):
        super().setUp()
        self.wt = self.active()
        self.assertFalse(os.path.exists(
            os.path.join(self.wt, ".harness/harness/features/BUG-3-gamma")))
        self.doc = os.path.join(self.fx.base, "DECISIONS.md")
        with open(self.doc, "w", encoding="utf-8") as fh:
            fh.write(self.DOC)

    def anchors(self):
        return run(self.wt, "check-decision-anchors.py", "--file", self.doc)

    def test_another_landed_features_file_is_counted_in_the_main_corpus(self):
        proc = self.anchors()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("examined 1 anchor(s), 0 failed", proc.stdout)

    def test_an_unreachable_main_corpus_exits_two(self):
        hide_owner_config(self.fx)
        proc = self.anchors()
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("cannot check", proc.stderr)


class Discovery(Case):
    """Repo-wide discovery from a sparse worktree sees the landed corpus, not one directory."""

    def test_validate_feature_json_scans_every_landed_record(self):
        wt = self.active()
        proc = run(wt, "validate-feature-json.py")
        self.assertIn("— 3 file(s)", proc.stderr)          # FEAT-1, FEAT-2, FEAT-10

    def test_validate_feature_json_refuses_a_broken_layout(self):
        wt = self.active()
        materialise_other(wt)
        proc = run(wt, "validate-feature-json.py")
        self.assertEqual(proc.returncode, 3, proc.stderr)
        self.assertIn("cannot establish the feature corpus", proc.stderr)

    def routes(self, checkout):
        proc = run(checkout, "check-plan-routes.py")
        return proc.returncode, proc.stdout + proc.stderr

    def test_check_plan_routes_examines_the_landed_corpus(self):
        code, out = self.routes(self.active())
        self.assertIn("examined 4 feature dir(s)", out)
        self.assertNotEqual(code, 2, out)

    def test_check_plan_routes_refuses_a_missing_landed_directory_by_name(self):
        # SC-04: one landed directory gone while the others remain must refuse by name, N of M,
        # before any plan is walked — not route-check the survivors and report a clean total.
        wt = self.active()
        drop_landed(self.fx, ".harness/harness/features/FEAT-2-beta")
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

    def test_layout_evidence_reads_this_checkouts_tree_not_its_disk(self):
        # A fresh worktree whose id has no record holds no feature directory on disk, yet
        # its tree carries every landed record: INV-27 must judge that tree (#2114).
        self.fx.commit_owner({".harness/factory/fleet.yaml":
                              "schema: factory-fleet/1\nworkspace_root: /tmp/f2114-ws\n"
                              "repos:\n  - name: o/kaya\n    default_branch: main\n",
                              ".harness/harness.json": json.dumps(build_config(
                                  {"github": {"repo": "o/harness"}})) + "\n"},
                             "declare the segments")
        wt = repair(self.fx.add_worktree("FEAT-99-new"))
        self.assertEqual(F.feature_dirs_on_disk(wt), [])
        result = layout_migration.scan(wt)
        self.assertGreater(result.feature_dirs, 0)
        self.assertEqual(result.surfaces["features"].evidence, {"migrated"})


if __name__ == "__main__":
    unittest.main()
