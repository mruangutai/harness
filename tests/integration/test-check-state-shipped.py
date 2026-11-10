#!/usr/bin/env python3
"""check-state checks nothing for a shipped feature (FEAT-2206 SC-02, SC-03, SC-04).

The checker runs as a subprocess against plain clones, sparse worktrees and main checkouts of a
synthetic owner repository (the FEAT-1559 fixture), the way /harness entry and the pre-commit
gate run it. One wrapper runs it under a Python audit hook so "a shipped record is not read" is
observed. A fake `gh` (FACTORY_GH) records every call so "no milestone query" is observed too.

CHECK_STATE_BIN points every case at another check-state.py (a baseline export) so the same
assertions can be shown failing against the code before the change.

    ./test-check-state-shipped.py                         synthetic fixtures (unittest)
    ./test-check-state-shipped.py --real-corpus OWNER     every shipped record OWNER's HEAD tracks
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
CHECK = Path(os.environ.get("CHECK_STATE_BIN") or BIN / "check-state.py")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(BIN))
import f58_sparse_fixture as F  # noqa: E402

ACTIVE = "FEAT-1-alpha"              # landed by the fixture; no plan.yaml, so never shipped
SHIPPED = "FEAT-5-shipped"
SHIPPED_TOO = "FEAT-6-shipped-too"
NOTE = "{fid} has shipped; nothing is checked for shipped features."

# Every shipped fixture is broken in ways the per-feature checks would report: a plan the strict
# loader refuses, an unsigned BRIEF, a run whose directory is absent.
STRICT_INVALID_DONE = "schema: plan/1\nfeature: {fid}\nstatus: done\ntasks: 7\n"
STRICT_VALID_DONE = "schema: plan/1\nfeature: {fid}\nstation_only: true\nstatus: done\ntasks: []\n"
BUILDING = "schema: plan/1\nfeature: {fid}\nstation_only: true\nstatus: building\ntasks: []\n"
FLEET = ("schema: factory-fleet/1\nrepos:\n  - name: acme/widget\n    default_branch: main\n"
         "workspace_root: /tmp/acme-factories\n")
COMPARISON_ONLY = ("INV-24", "INV-29", "INV-52")

FAKE_GH = """#!/bin/sh
printf '%s\\n' "$*" >> "{log}"
exit 0
"""


def check(checkout, *args, opens=None, env_extra=None):
    env = dict(F.ENV, HARNESS_PROJECT_DIR=checkout, CLAUDE_PROJECT_DIR=checkout)
    env.pop("HARNESS_AGENT_TYPE", None)
    env.update(env_extra or {})
    argv = [sys.executable, str(CHECK), *args]
    if opens is not None:
        env["OPEN_LOG"] = opens
        argv = [sys.executable, "-c", F.OPEN_TRACE_WRAPPER, str(CHECK), *args]
    proc = subprocess.run(argv, env=env, capture_output=True, text=True, cwd=checkout)
    return proc.returncode, proc.stdout + proc.stderr


def feature_files(fid, plan, doc=None, brief=None):
    base = f".harness/harness/features/{fid}"
    record = {"feature_id": fid, "branch": f"feat/{fid}", "pr": None, "review_sha": "none",
              "cycles_used": 0, "max_total_cycles": 5,
              "runs": [{"id": "r1", "squad": "product", "agent": "harness-product-lead",
                        "verdict": "PASS"}]}
    record.update(doc or {})
    return {f"{base}/plan.yaml": plan.replace("{fid}", fid),
            f"{base}/BRIEF.md": brief or f"# BRIEF {fid}\n",
            f"{base}/STATE.md": "# STATE\n",
            f"{base}/feature.json": json.dumps(record) + "\n"}


def naming(out, fid):
    """Finding lines that name `fid`, excluding the three comparison invariants."""
    return [l for l in out.splitlines()
            if fid in l and not any(inv in l for inv in COMPARISON_ONLY)]


def opened_under(log, checkout, fid):
    base = os.path.realpath(checkout) + f"/.harness/harness/features/{fid}/"
    return sorted({p[len(base):] for p in Path(log).read_text().splitlines()
                   if p.startswith(base)})


class Case(unittest.TestCase):
    def setUp(self):
        ctx = F.sparse_fixture()
        self.fx = ctx.__enter__()
        self.addCleanup(ctx.__exit__, None, None, None)

    def commit(self, files, message="fixture"):
        self.fx.commit_owner(files, message)

    def sparse(self, name):
        wt = self.fx.add_worktree(name)
        proc = subprocess.run([sys.executable, str(BIN / "worktree-state.py"), "--repair",
                               "--checkout", wt], env=F.ENV, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return wt


class ShippedSubjects(Case):
    def setUp(self):
        super().setUp()
        self.commit({**feature_files(SHIPPED, STRICT_INVALID_DONE),
                     **feature_files("FEAT-7-building", BUILDING)}, "shipped and building")

    def test_a_full_audit_names_no_shipped_feature(self):
        _code, out = check(self.fx.clone())
        self.assertEqual(naming(out, SHIPPED), [], out)
        self.assertTrue(naming(out, "FEAT-7-building"),
                        "control: the same broken files on a building feature are reported\n" + out)

    def test_a_changed_audit_names_no_shipped_feature(self):
        clone = self.fx.clone()
        F.write_files(clone, {f".harness/harness/features/{SHIPPED}/BRIEF.md": "# edited\n",
                              f".harness/harness/features/{SHIPPED}/plan.yaml":
                                  STRICT_INVALID_DONE.replace("{fid}", SHIPPED) + "# edited\n"})
        _code, out = check(clone, "--changed")
        self.assertEqual(naming(out, SHIPPED), [], out)

    def test_selecting_a_shipped_feature_prints_one_note_and_exits_clean(self):
        code, out = check(self.fx.clone(), "--feature", SHIPPED)
        self.assertEqual(code, 0, out)
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        self.assertEqual(lines, ["note       " + NOTE.format(fid=SHIPPED)], out)

    def test_a_missing_selected_feature_still_refuses(self):
        code, out = check(self.fx.clone(), "--feature", "FEAT-9-gone")
        self.assertEqual(code, 1)
        self.assertIn("names no feature directory", out)

    def test_an_unreadable_status_keeps_every_check(self):
        nested = "schema: plan/1\nfeature: FEAT-8-nested\nmeta:\n  status: done\ntasks: []\n"
        self.commit(feature_files("FEAT-8-nested", nested), "status not at top level")
        _code, out = check(self.fx.clone())
        self.assertTrue(naming(out, "FEAT-8-nested"), out)

    def test_a_duplicate_status_key_keeps_every_check(self):
        # `done` followed by a second status key whose value is no plain token: ambiguous, so
        # audited in full and never answered with the shipped note.
        dup = "schema: plan/1\nfeature: FEAT-8-dup\nstatus: done\nstatus: [building]\ntasks: 7\n"
        self.commit(feature_files("FEAT-8-dup", dup), "two status keys")
        clone = self.fx.clone()
        _code, out = check(clone)
        self.assertTrue(naming(out, "FEAT-8-dup"), out)
        _code, selected = check(clone, "--feature", "FEAT-8-dup")
        self.assertNotIn(NOTE.format(fid="FEAT-8-dup"), selected)
        self.assertTrue(naming(selected, "FEAT-8-dup"), selected)

    def test_a_shipped_directory_is_read_only_for_status_and_comparison(self):
        clone = self.fx.clone()
        os.makedirs(os.path.join(clone, f".harness/harness/features/{SHIPPED}/runs/r9"))
        Path(clone, f".harness/harness/features/{SHIPPED}/runs/r9/state.yaml").write_text("x: [\n")
        log = os.path.join(self.fx.base, "opens.log")
        check(clone, opens=log)
        opened = opened_under(log, clone, SHIPPED)
        self.assertTrue(opened, "instrumentation saw no read of the shipped directory at all")
        self.assertTrue(set(opened) <= {"plan.yaml", "feature.json"}, opened)
        self.assertIn("BRIEF.md", opened_under(log, clone, "FEAT-7-building"))


class ComparisonsKeepShippedRecords(Case):
    def setUp(self):
        super().setUp()
        self.commit({".harness/factory/fleet.yaml": FLEET}, "fleet")

    def claim(self, fid, plan, factory):
        return feature_files(fid, plan, {"factory": factory})

    def test_inv24_sees_a_collision_between_a_shipped_and_an_active_claim(self):
        self.commit({**self.claim(SHIPPED, STRICT_INVALID_DONE,
                                  {"repo": "acme/widget", "issues": {"T-01": 11}}),
                     **self.claim("FEAT-7-building", BUILDING,
                                  {"repo": "acme/widget", "issues": {"T-01": 11}})})
        for checkout in (self.fx.clone(), self.sparse("FEAT-7-building")):
            _code, out = check(checkout)
            hits = [l for l in out.splitlines() if "INV-24" in l and SHIPPED in l
                    and "FEAT-7-building" in l]
            self.assertEqual(len(hits), 1, out)

    def test_inv24_sees_a_collision_between_two_shipped_claims(self):
        self.commit({**self.claim(SHIPPED, STRICT_INVALID_DONE,
                                  {"repo": "acme/widget", "parent": 21}),
                     **self.claim(SHIPPED_TOO, STRICT_INVALID_DONE,
                                  {"repo": "acme/widget", "issues": {"T-02": 21}})})
        _code, out = check(self.fx.clone())
        hits = [l for l in out.splitlines() if "INV-24" in l and SHIPPED in l and SHIPPED_TOO in l]
        self.assertEqual(len(hits), 1, out)

    def test_inv24_does_not_grade_a_shipped_claim_itself(self):
        # An undeclared repository, a non-container `issues` and a number repeated within one
        # block: each is graded on an active record, none on a shipped one.
        self.commit({**self.claim(SHIPPED, STRICT_INVALID_DONE, {"repo": "acme/nope", "issues": 42}),
                     **self.claim(SHIPPED_TOO, STRICT_INVALID_DONE,
                                  {"repo": "acme/widget", "issues": {"T-01": 5, "T-02": 5}}),
                     **self.claim("FEAT-7-building", BUILDING,
                                  {"repo": "acme/nope", "issues": {"T-01": 9}})})
        _code, out = check(self.fx.clone())
        inv24 = [l for l in out.splitlines() if "INV-24" in l]
        self.assertFalse([l for l in inv24 if SHIPPED in l or SHIPPED_TOO in l], out)
        self.assertTrue([l for l in inv24 if "FEAT-7-building" in l and "acme/nope" in l],
                        "control: an undeclared repository on a building feature is graded\n" + out)

    def test_inv24_skips_unusable_shipped_numbers_and_keeps_usable_ones(self):
        # A Unicode digit int() refuses and a word, beside one usable number another feature
        # also claims: no crash, the usable collision reported, the unusable values ungraded.
        # The strict loader refuses this shipped record, so its claims arrive through the
        # lenient comparison re-read.
        self.commit({**self.claim(SHIPPED, STRICT_INVALID_DONE,
                                  {"repo": "acme/widget", "parent": "²",
                                   "issues": {"T-01": "x", "T-02": 11}}),
                     **self.claim("FEAT-7-building", BUILDING,
                                  {"repo": "acme/widget", "issues": {"T-01": 11}})})
        _code, out = check(self.fx.clone())
        self.assertNotIn("Traceback", out)
        inv24 = [l for l in out.splitlines() if "INV-24" in l]
        self.assertEqual(len([l for l in inv24 if SHIPPED in l and "FEAT-7-building" in l]), 1, out)
        self.assertFalse([l for l in inv24 if SHIPPED in l and "FEAT-7-building" not in l], out)

    def test_inv24_skips_an_oversized_shipped_number_and_keeps_usable_ones(self):
        # More digits than int()'s string-conversion limit: isdigit() says yes, int() refuses.
        self.commit({**self.claim(SHIPPED, STRICT_INVALID_DONE,
                                  {"repo": "acme/widget", "parent": "1" * 4301,
                                   "issues": {"T-02": 11}}),
                     **self.claim("FEAT-7-building", BUILDING,
                                  {"repo": "acme/widget", "issues": {"T-01": 11}})})
        _code, out = check(self.fx.clone())
        self.assertNotIn("Traceback", out)
        inv24 = [l for l in out.splitlines() if "INV-24" in l]
        self.assertEqual(len([l for l in inv24 if SHIPPED in l and "FEAT-7-building" in l]), 1, out)

    def test_inv24_still_reads_a_unicode_digit_on_active_claims(self):
        # "٣" (Arabic-Indic three) is a number int() reads: two active claims on it collide,
        # exactly as before this feature, and neither is graded as malformed.
        self.commit({**self.claim("FEAT-7-building", BUILDING,
                                  {"repo": "acme/widget", "issues": {"T-01": "٣"}}),
                     **self.claim("FEAT-8-building", BUILDING,
                                  {"repo": "acme/widget", "issues": {"T-01": 3}})})
        _code, out = check(self.fx.clone())
        inv24 = [l for l in out.splitlines() if "INV-24" in l]
        self.assertEqual(len([l for l in inv24 if "FEAT-7-building" in l and "FEAT-8-building" in l
                              and "issue 3" in l]), 1, out)
        self.assertFalse([l for l in inv24 if "not an integer" in l], out)

    def test_inv52_sees_two_shipped_features_on_one_branch(self):
        self.commit({**feature_files(SHIPPED, STRICT_INVALID_DONE, {"branch": "feat/dup"}),
                     **feature_files(SHIPPED_TOO, STRICT_INVALID_DONE, {"branch": "feat/dup"})})
        _code, out = check(self.fx.clone())
        self.assertIn(f"INV-52: branch feat/dup is claimed by 2 landed features "
                      f"({SHIPPED}, {SHIPPED_TOO})", out)

    def test_inv52_keeps_the_branch_of_a_shipped_record_the_strict_loader_refuses(self):
        # A malformed parent makes the shipped record strict-invalid; it is never graded, so its
        # branch must still be compared or a later feature could reuse it unnoticed. Full clone
        # and the active feature's sparse worktree both read the main corpus.
        self.commit({**feature_files(SHIPPED, STRICT_INVALID_DONE,
                                     {"branch": "feat/dup", "github": {"parent": "²"}}),
                     **feature_files("FEAT-7-building", BUILDING, {"branch": "feat/dup"})})
        for checkout in (self.fx.clone(), self.sparse("FEAT-7-building")):
            _code, out = check(checkout)
            self.assertIn(f"INV-52: branch feat/dup is claimed by 2 landed features "
                          f"({SHIPPED}, FEAT-7-building)", out)
            self.assertFalse([l for l in out.splitlines()
                              if SHIPPED in l and "does not parse" in l], out)

    def test_inv29_sees_a_standing_worktree_of_a_shipped_feature(self):
        self.commit(feature_files(SHIPPED, STRICT_VALID_DONE))
        wt = self.fx.add_worktree(SHIPPED)
        _code, out = check(self.fx.owner)
        hits = [l for l in out.splitlines() if "INV-29" in l and wt in l]
        self.assertEqual(len(hits), 1, out)


class RetiredMirrorChecks(Case):
    def test_inv28_and_inv30_are_retired(self):
        code, out = check(self.fx.clone(), "--list")
        self.assertEqual(code, 0, out)
        for inv in ("INV-28", "INV-30"):
            rows = [l for l in out.splitlines() if re.match(rf"\s*{inv}\b", l)]
            self.assertTrue(rows and all("retired" in l.lower() for l in rows), out)

    def test_selecting_a_retired_number_runs_nothing(self):
        clone = self.fx.clone()
        _ref_code, reference = check(clone, "--only", "INV-9")
        for inv in ("INV-28", "INV-30"):
            code, out = check(clone, "--only", inv)
            self.assertEqual(code, 0, out)
            self.assertEqual(out.replace(inv, "INV-N").splitlines()[0].split(" — ")[0],
                             reference.replace("INV-9", "INV-N").splitlines()[0].split(" — ")[0],
                             "a retired selection reads exactly as INV-9's does\n" + out)
            self.assertFalse([l for l in out.splitlines()
                              if l.strip().startswith(("VIOLATION", "note")) and inv in l], out)

    def test_no_milestone_or_pull_request_check_runs_for_a_shipped_feature(self):
        self.commit({".harness/harness.json": json.dumps(
                        {"github": {"sync": True, "repo": "acme/widget", "board": None}}) + "\n",
                     **feature_files(SHIPPED, STRICT_VALID_DONE,
                                     {"github": {"milestone": 3, "repo": "acme/widget"}})})
        gh_log = os.path.join(self.fx.base, "gh.log")
        fake = os.path.join(self.fx.base, "gh")
        Path(fake).write_text(FAKE_GH.format(log=gh_log))
        os.chmod(fake, 0o755)
        _code, out = check(self.fx.clone(), env_extra={"FACTORY_GH": fake})
        calls = Path(gh_log).read_text() if os.path.exists(gh_log) else ""
        self.assertNotIn("milestones", calls)
        self.assertNotRegex(out, r"INV-(28|30)[ :]", out)


def _export_corpus(owner, export):
    """OWNER's committed .harness tree, extracted to `export`: the real records, no git."""
    os.makedirs(export)
    archive = subprocess.run(["git", "-C", owner, "archive", "HEAD", ".harness"],
                             capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", export], input=archive, check=True)


def _shipped_ids(owner, export):
    """Every landed id whose exported plan reads `done` under the production classifier."""
    import feature_corpus
    from check_state.ctx import lenient_station
    landed = feature_corpus.landed_dirs(owner)
    shipped = sorted(fid for seg, fid, _path in landed
                     if lenient_station(os.path.join(export, ".harness", seg, "features", fid)) == "done")
    print(f"real corpus {owner}: {len(landed)} landed, {len(shipped)} shipped: {', '.join(shipped)}")
    return shipped


def _shipped_record_failures(export, full_out, log, fid):
    """The labels of every shipped-record claim `fid` breaks; each claim is printed."""
    named = naming(full_out, fid)
    opened = set(opened_under(log, export, fid))
    code, selected = check(export, "--feature", fid)
    lines = [l.strip() for l in selected.splitlines() if l.strip()]
    claims = ((not named, f"{fid} named by the full audit: {named}"),
              (opened <= {"plan.yaml", "feature.json"},
               f"{fid} opened beyond status/comparison: {sorted(opened)}"),
              (code == 0 and lines == ["note       " + NOTE.format(fid=fid)],
               f"{fid} --feature: exit {code}, {lines}"))
    for ok, label in claims:
        print(("PASS  " if ok else "FAIL  ") + (fid if ok else label))
    return [label for ok, label in claims if not ok]


def real_corpus(owner):
    """Every lenient `done` record OWNER's HEAD tracks: never an audit subject, and selecting it
    prints exactly one shipped note. Runs THIS checkout's checker over an export of OWNER's
    committed .harness tree, so the subject is the real records and the code is the candidate."""
    with tempfile.TemporaryDirectory() as tmp:
        export = os.path.join(tmp, "corpus")
        _export_corpus(owner, export)
        shipped = _shipped_ids(owner, export)
        failures = [] if shipped else ["no shipped record found — the check would be vacuous"]
        log = os.path.join(tmp, "opens.log")
        _code, out = check(export, opens=log)
        for fid in shipped:
            failures += _shipped_record_failures(export, out, log, fid)
    print(f"\n{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--real-corpus":
        sys.exit(real_corpus(sys.argv[2]))
    unittest.main()
