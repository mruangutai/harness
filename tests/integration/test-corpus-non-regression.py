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
  3. CONVERSION MANIFEST. When T-06's notes/conversion-manifest.json exists, its records must be
     internally consistent: converted checkouts verified and idempotent, dirty ones skipped with
     unchanged bytes, code-only probes excluded and never counted as converted.

`--conversion-manifest PATH` adds the LIVE half (T-06's verify): every converted checkout still at
its recorded HEAD must verify clean now. Read-only; a checkout that is gone or has moved on is an
announced skip, not a pass.

The one-time endpoint proofs — merge-base(review_sha, main) as pre_change_sha, the whole-feature
diff touching no other feature's directory, main-corpus byte equality — are NOT here. They are
recorded once in notes/non-regression-receipt.md (D-13: a pinned proof or a one-time one; there
is no third form).
"""
import json
import os
import re
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

MANIFEST_REL = ".harness/harness/features/FEAT-1559-corpus-outside-worktree/notes/conversion-manifest.json"
LIVE_MANIFEST = None          # set from --conversion-manifest

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
OUTCOMES = ("converted", "skipped-dirty", "excluded")


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


class ConversionManifest(unittest.TestCase):
    def manifest(self):
        path = LIVE_MANIFEST or fc.corpus_path(str(ROOT), MANIFEST_REL)
        if not os.path.isfile(path):
            print(f"SKIP: no conversion manifest at {path} (T-06 has not run)")
            self.skipTest("no conversion manifest yet")
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)

    def test_the_manifest_is_internally_consistent(self):
        self.assertEqual(manifest_findings(self.manifest()), [])

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

    def test_converted_checkouts_still_verify_clean(self):
        if LIVE_MANIFEST is None:
            print("SKIP: live manifest validation runs only with --conversion-manifest PATH")
            self.skipTest("no --conversion-manifest")
        for entry in self.manifest()["checkouts"]:
            if entry["outcome"] != "converted":
                continue
            with self.subTest(entry["path"]):
                path = entry["path"]
                if not os.path.isdir(path):
                    print(f"SKIP: {path} no longer exists")
                    continue
                head = F.git(path, "rev-parse", "HEAD", check=False).stdout.strip()
                if head != entry["head"]:
                    print(f"SKIP: {path} moved from {entry['head'][:12]} to {head[:12]}")
                    continue
                code, doc = verify(path)
                self.assertEqual(code, 0, doc.get("findings"))
                self.assertEqual(doc["active_feature"], entry["active_feature"])


if __name__ == "__main__":
    argv = sys.argv[:1]
    rest = sys.argv[1:]
    while rest:
        arg = rest.pop(0)
        if arg == "--conversion-manifest" and rest:
            LIVE_MANIFEST = os.path.abspath(rest.pop(0))
        else:
            argv.append(arg)
    unittest.main(argv=argv)
