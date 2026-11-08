#!/usr/bin/env python3
"""What FEAT-1559 must NOT change, kept as standing tests (SC-06, SC-11, SC-12; D-13).

Three parts are collected on every run, because their post-change side is live:

  1. RETENTION. A fresh non-linked synthetic clone keeps every feature directory, `--verify` is a
     no-op there, and a pull that fires the installed post-merge hook leaves all of them in place.
  2. AUDIT FINDINGS. check-state on a fresh synthetic clone still reports every finding the
     planning-baseline checker (652e70d4) reported there. The baseline is a RECORDED literal
     (below), never re-derived from a git ref: a moving ref compares the change against itself
     (D-13). Findings are normalised to (level, invariant, features) so wording edits elsewhere
     cannot redden this; a lost finding is the regression this feature could cause, so the check
     is that the baseline is a subset of what the checker reports now.
  3. CONVERSION MANIFEST. A manifest recorded the way T-06 recorded the real one — produced here
     by converting a synthetic owner's checkouts — must be internally consistent: converted
     checkouts verified and idempotent, dirty ones skipped with unchanged bytes, code-only probes
     excluded and never counted as converted. Its LIVE half (T-06's verify) must hold too: every
     converted checkout still at its recorded HEAD verifies clean now; a checkout that is gone or
     has moved on is reported as skipped, never counted as a pass.

The one-time endpoint proofs — merge-base(review_sha, main) as pre_change_sha, the whole-feature
diff touching no other feature's directory, main-corpus byte equality — are NOT here. They are
recorded once in notes/non-regression-receipt.md (D-13: a pinned proof or a one-time one; there
is no third form).
"""
import hashlib
import json
import os
import re
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

OUTCOMES = ("converted", "skipped-dirty", "excluded")

# The planning-baseline checker (git archive 652e70d4 .claude/skills/harness/bin) run once against
# a fresh f58_sparse_fixture clone, normalised by `finding_keys`. Recorded 2026-10-05.
BASELINE_KEYS = {
    ("VIOLATION", "-", ("FEAT-1-alpha",)),
    ("VIOLATION", "-", ("FEAT-10-kaya-app",)),
    ("VIOLATION", "-", ("FEAT-2-beta",)),
    ("VIOLATION", "INV-29", ()),
    ("VIOLATION", "INV-31", ()),
    ("VIOLATION", "INV-32", ()),
    ("VIOLATION", "INV-34", ("FEAT-1-alpha",)),
    ("VIOLATION", "INV-34", ("FEAT-10-kaya-app",)),
    ("VIOLATION", "INV-34", ("FEAT-2-beta",)),
    ("VIOLATION", "INV-43", ()),
    ("note", "-", ()),
    ("note", "INV-22", ("FEAT-1-alpha",)),
    ("note", "INV-22", ("FEAT-10-kaya-app",)),
    ("note", "INV-22", ("FEAT-2-beta",)),
    ("note", "INV-42", ()),
}
FEATURE_ID = re.compile(r"\b(?:FEAT|BUG)-\d+(?:-[a-z0-9]+)*")


def finding_keys(output):
    keys = set()
    for line in output.splitlines():
        line = line.strip()
        level = line.split(" ", 1)[0]
        if level not in ("VIOLATION", "note", "warn"):
            continue
        inv = re.search(r"\bINV-\d+\b", line)
        keys.add((level, inv.group(0) if inv else "-", tuple(sorted(set(FEATURE_ID.findall(line))))))
    return keys


def verify(checkout, bin_dir=BIN):
    proc = subprocess.run([sys.executable, os.path.join(bin_dir, "worktree-state.py"), "--verify",
                           "--json", "--checkout", checkout], env=F.ENV,
                          capture_output=True, text=True)
    return proc.returncode, json.loads(proc.stdout)


ALL_FEATURES = ["harness/BUG-3-gamma", "harness/FEAT-1-alpha", "harness/FEAT-2-beta",
                "kaya/FEAT-10-kaya-app"]


class Retention(unittest.TestCase):
    def setUp(self):
        ctx = F.sparse_fixture()
        self.fx = ctx.__enter__()
        self.addCleanup(ctx.__exit__, None, None, None)

    def test_a_fresh_clone_keeps_the_full_corpus_and_verify_is_a_no_op(self):
        clone = self.fx.clone()
        self.assertEqual(F.feature_dirs_on_disk(clone), ALL_FEATURES)
        code, doc = verify(clone)
        self.assertEqual((code, doc["checkout_class"], doc["findings"]), (0, "plain-clone", []))
        self.assertTrue(doc["noop"], "verify on a plain clone gave no no-op reason")

    def test_a_hooked_pull_keeps_the_full_corpus(self):
        clone = self.fx.clone()
        bin_dir, _hooks = F.install_hooks(clone, ROOT)
        self.fx.commit_owner({".harness/harness/features/FEAT-2-beta/BRIEF.md": "# v2\n",
                              "newtop/file.txt": "new\n"}, "main moves")
        F.git(clone, "pull", "-q", "--no-rebase", "origin", "main")
        self.assertEqual(F.feature_dirs_on_disk(clone), ALL_FEATURES)
        self.assertEqual(F.git(clone, "sparse-checkout", "list", check=False).returncode, 128,
                         "the plain clone gained a sparse-checkout")
        self.assertEqual(verify(clone, bin_dir)[0], 0)


class AuditFindings(unittest.TestCase):
    def test_a_fresh_clone_still_reports_every_baseline_finding(self):
        with F.sparse_fixture() as fx:
            clone = fx.clone()
            env = dict(F.ENV, HARNESS_PROJECT_DIR=clone, CLAUDE_PROJECT_DIR=clone)
            proc = subprocess.run([sys.executable, str(BIN / "check-state.py")], env=env,
                                  cwd=clone, capture_output=True, text=True)
        now = finding_keys(proc.stdout + proc.stderr)
        self.assertEqual(sorted(BASELINE_KEYS - now), [], proc.stdout + proc.stderr)


def _converted_findings(where, entry):
    """A converted checkout: an active feature, three zero exits, an idempotent second repair,
    and exactly the expected directories."""
    bad = []
    exits = entry.get("exits", {})
    if not entry.get("active_feature"):
        bad.append(f"{where}: converted with no active feature")
    if [exits.get(k) for k in ("repair", "verify", "repair_again")] != [0, 0, 0]:
        bad.append(f"{where}: converted but exits are {exits}")
    if entry.get("after", {}).get("digest") != entry.get("after_repair_again", {}).get("digest"):
        bad.append(f"{where}: the second repair changed bytes (not idempotent)")
    exact = entry.get("observed_dirs") == entry.get("expected_dirs")
    if not exact or entry.get("missing") or entry.get("unexpected"):
        bad.append(f"{where}: converted but observed directories differ from expected")
    return bad


def _dirty_findings(where, entry):
    """A dirty skip: repair refused with 8, no byte changed, and a reason given."""
    bad = []
    repair = entry.get("exits", {}).get("repair")
    if repair != 8:
        bad.append(f"{where}: skipped as dirty but repair exited {repair}")
    if entry.get("before", {}).get("digest") != entry.get("after", {}).get("digest"):
        bad.append(f"{where}: skipped as dirty but its bytes changed")
    if not entry.get("reason"):
        bad.append(f"{where}: skipped with no reason")
    return bad


def _excluded_findings(where, entry):
    return [] if entry.get("reason") else [f"{where}: excluded with no reason"]


OUTCOME_CHECKS = {"converted": _converted_findings, "skipped-dirty": _dirty_findings,
                  "excluded": _excluded_findings}


def _entry_findings(entry):
    where, outcome = entry.get("path", "?"), entry.get("outcome")
    if outcome not in OUTCOMES:
        return [f"{where}: outcome {outcome!r} is not one of {OUTCOMES}"]
    return OUTCOME_CHECKS[outcome](where, entry)


def _header_findings(doc):
    """The manifest's own fields: present, a known schema, full SHAs."""
    bad = [f"manifest lacks {key}" for key in
           ("schema", "owner", "owner_head", "pre_change_sha", "review_sha", "checkouts")
           if key not in doc]
    if doc.get("schema") != "feat-1559-conversion/1":
        bad.append(f"unknown schema {doc.get('schema')!r}")
    bad += [f"{sha_key} is not a full 40-hex SHA"
            for sha_key in ("owner_head", "pre_change_sha", "review_sha")
            if not re.fullmatch(r"[0-9a-f]{40}", str(doc.get(sha_key, "")))]
    return bad


def manifest_findings(doc):
    """Every internal inconsistency in a conversion manifest, as sentences; [] when sound."""
    bad = _header_findings(doc)
    paths = [c.get("path") for c in doc.get("checkouts", [])]
    if len(paths) != len(set(paths)):
        bad.append("a checkout path is listed twice")
    for entry in doc.get("checkouts", []):
        bad += _entry_findings(entry)
    return bad


def _digest(checkout):
    digest = hashlib.sha256()
    for key, value in sorted(F.snapshot(checkout).items()):
        digest.update(repr((key, value)).encode())
    return digest.hexdigest()


def _repair(checkout):
    return subprocess.run([sys.executable, str(BIN / "worktree-state.py"), "--repair",
                           "--checkout", checkout], env=F.ENV, capture_output=True,
                          text=True).returncode


def build_manifest(fx):
    """Convert a synthetic owner's checkouts the way T-06 converted the real ones and return the
    manifest it records: one planning worktree converted, one with uncommitted work skipped as
    dirty, one code-only probe excluded. Every exit and digest is observed, never written in."""
    head = F.git(fx.owner, "rev-parse", "HEAD").stdout.strip()
    active, busy = F.HARNESS_FEATURES
    path = fx.add_worktree(active)
    converted = {"path": path, "outcome": "converted", "active_feature": active, "head": head,
                 "expected_dirs": [f"harness/{active}"]}
    repair = _repair(path)
    converted["after"] = {"digest": _digest(path)}
    verify_exit, _report = verify(path)
    repair_again = _repair(path)
    converted["after_repair_again"] = {"digest": _digest(path)}
    converted["exits"] = {"repair": repair, "verify": verify_exit, "repair_again": repair_again}
    converted["observed_dirs"] = F.feature_dirs_on_disk(path)
    converted["missing"], converted["unexpected"] = fc.compare_names(
        converted["expected_dirs"], converted["observed_dirs"])

    path = fx.add_worktree(busy)
    with open(os.path.join(path, ".harness", "harness", "features", busy, "BRIEF.md"), "a") as fh:
        fh.write("an uncommitted edit\n")
    before = _digest(path)
    dirty = {"path": path, "outcome": "skipped-dirty", "reason": "C: uncommitted work",
             "exits": {"repair": _repair(path)}, "before": {"digest": before},
             "after": {"digest": _digest(path)}}

    excluded = {"path": fx.add_probe("code-only"), "outcome": "excluded",
                "reason": "code-only probe outside .claude/worktrees"}
    return {"schema": "feat-1559-conversion/1", "owner": fx.owner, "owner_head": head,
            "pre_change_sha": head, "review_sha": head, "checkouts": [converted, dirty, excluded]}


def live_findings(doc):
    """`(findings, skipped)` for the LIVE half (T-06's verify): every converted checkout still at
    its recorded HEAD must verify clean now, on its recorded active feature. Read-only; a
    checkout that is gone or has moved on is reported in `skipped`, never counted as a pass."""
    bad, skipped = [], []
    for entry in doc.get("checkouts", []):
        if entry.get("outcome") != "converted":
            continue
        path = entry["path"]
        if not os.path.isdir(path):
            skipped.append(f"{path} no longer exists")
            continue
        head = F.git(path, "rev-parse", "HEAD", check=False).stdout.strip()
        if head != entry.get("head"):
            skipped.append(f"{path} moved from {str(entry.get('head'))[:12]} to {head[:12]}")
            continue
        code, report = verify(path)
        if code != 0:
            bad.append(f"{path}: verify exited {code}: {report.get('findings')}")
        elif report.get("active_feature") != entry.get("active_feature"):
            bad.append(f"{path}: active feature {report.get('active_feature')!r}, recorded "
                       f"{entry.get('active_feature')!r}")
    return bad, skipped


class ManifestRules(unittest.TestCase):
    """The consistency rules themselves, on a hand-built manifest."""

    def test_a_planted_inconsistency_is_caught(self):
        sha = "a" * 40
        good = {"path": "/x", "outcome": "converted", "active_feature": "FEAT-1-a",
                "exits": {"repair": 0, "verify": 0, "repair_again": 0},
                "after": {"digest": "d1"}, "after_repair_again": {"digest": "d1"},
                "expected_dirs": ["harness/FEAT-1-a"], "observed_dirs": ["harness/FEAT-1-a"],
                "missing": [], "unexpected": []}
        dirty = {"path": "/y", "outcome": "skipped-dirty", "reason": "C: real edit",
                 "exits": {"repair": 8}, "before": {"digest": "d2"}, "after": {"digest": "d2"}}
        doc = {"schema": "feat-1559-conversion/1", "owner": "/o", "owner_head": sha,
               "pre_change_sha": sha, "review_sha": sha, "checkouts": [good, dirty]}
        self.assertEqual(manifest_findings(doc), [])
        for mutate, expect in (
                (lambda d: d["checkouts"][0]["after_repair_again"].update(digest="d9"), "idempotent"),
                (lambda d: d["checkouts"][1]["after"].update(digest="d9"), "bytes changed"),
                (lambda d: d["checkouts"][0]["exits"].update(verify=7), "exits"),
                (lambda d: d["checkouts"][0].update(outcome="done"), "outcome"),
                (lambda d: d.update(review_sha="abc"), "40-hex")):
            broken = json.loads(json.dumps(doc))
            mutate(broken)
            self.assertTrue(any(expect in f for f in manifest_findings(broken)), expect)


class ConversionManifest(unittest.TestCase):
    """Runs on a manifest this test produces from a synthetic owner (FEAT-71): never on a prior
    feature's notes, and never skipped."""

    def setUp(self):
        ctx = F.sparse_fixture()
        self.fx = ctx.__enter__()
        self.addCleanup(ctx.__exit__, None, None, None)
        self.doc = build_manifest(self.fx)

    def test_the_manifest_is_internally_consistent(self):
        self.assertEqual([c["outcome"] for c in self.doc["checkouts"]], list(OUTCOMES))
        self.assertEqual(manifest_findings(self.doc), [])

    def test_converted_checkouts_still_verify_clean(self):
        self.assertEqual(live_findings(self.doc), ([], []))

    def test_a_live_regression_is_caught_and_a_moved_checkout_is_not_a_pass(self):
        wrong = json.loads(json.dumps(self.doc))
        wrong["checkouts"][0]["active_feature"] = F.HARNESS_FEATURES[1]
        self.assertTrue(live_findings(wrong)[0])

        moved = json.loads(json.dumps(self.doc))
        moved["checkouts"][0]["head"] = "0" * 40
        self.assertEqual(len(live_findings(moved)[1]), 1)

        converted = self.doc["checkouts"][0]["path"]
        other = os.path.join(".harness", "harness", "features", F.HARNESS_FEATURES[1],
                             "feature.json")
        os.makedirs(os.path.dirname(os.path.join(converted, other)), exist_ok=True)
        shutil.copyfile(os.path.join(self.fx.owner, other), os.path.join(converted, other))
        bad, skipped = live_findings(self.doc)
        self.assertEqual(skipped, [])
        self.assertTrue(bad and "verify exited" in bad[0], bad)


if __name__ == "__main__":
    unittest.main()
