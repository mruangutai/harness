#!/usr/bin/env python3
"""FEAT-1821 T-01: ui_contract.py is the ONLY parser and policy authority for a DESIGN.md
`## Checks` table, and the ONLY gate that decides whether a Playwright evidence bundle
(`runs/<id>/ui/results.json` + WebPs) discharges it.

Every case below is a mutation of one required or prohibited condition (SC-05, SC-06,
SC-10, SC-11): the positive contract passes, and each single defect is refused with a
reason that names it. The gate recomputes the contract from DESIGN.md on every call — a
results file cannot bring its own list of checks (the "second parser" path).
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".claude" / "skills" / "harness" / "bin"))
import ui_contract as uc  # noqa: E402

FEATURE = "FEAT-53-metrics-dashboard"
RUN = "2026-09-17-30-validator"
SHA = "93785232ac32ae4fecc0a456d286e772ad15eb82"
WEBP = b"RIFF\x1a\x00\x00\x00WEBPVP8 " + b"\x00" * 14

ROWS = [
    ("C1-HEADER-GEOMETRY", "shared header geometry matches DESIGN", "shared-header",
     "automated-each-project", "desktop-1440,desktop-1920", "header height >= 72px; selector width == 180px"),
    ("SRC-TOKENS", "component source uses only theme tokens", "client-source",
     "automated-once", "desktop-1440", "no hex literal outside theme.ts"),
    ("VIS-DENSITY", "dense hierarchy and qualitative states match DESIGN", "all-routes",
     "inspection-each-project", "desktop-1440,desktop-1920", "reader compares against §Component direction"),
]
EVIDENCE = [
    ("VIS-DENSITY", "overview-default", "/", "default", "load", "desktop-1440", "overview-default.webp"),
    ("VIS-DENSITY", "overview-default", "/", "default", "load", "desktop-1920", "overview-default.webp"),
]


ZIP = b"PK\x03\x04" + b"\x00" * 26 + b"PK\x05\x06" + b"\x00" * 18


def design_text(rows=ROWS, evidence=EVIDENCE, header=None, traces=None, traces_header="| Check ID |"):
    header = header or "| Check ID | Spec title | Surface | Method | Projects | Predicate or evidence |"
    lines = ["# DESIGN", "", "## Palette", "", "prose", "", "## Checks", "", header,
             "|---|---|---|---|---|---|"]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    if traces is not None:
        lines += ["", "### Traces", "", traces_header, "|---|"] + [f"| {t} |" for t in traces]
    lines += ["", "### Inspection evidence", "",
              "| Check ID | Evidence label | Route | Fixture state | Setup | Project | Screenshot |",
              "|---|---|---|---|---|---|---|"]
    lines += ["| " + " | ".join(e) + " |" for e in evidence]
    lines += ["", "## Out of scope", "", "nothing"]
    return "\n".join(lines) + "\n"


class Workspace:
    """A throwaway repo root: feature dir, results bundle, client package, spec file."""

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.feature_dir = self.root / ".harness" / "harness" / "features" / FEATURE
        self.design = self.feature_dir / "DESIGN.md"
        self.ui_dir = self.feature_dir / "runs" / RUN / "ui"
        self.client = self.root / "client"
        self.ui_dir.mkdir(parents=True)
        self.client.mkdir(parents=True)
        self.design.write_text(design_text())
        (self.client / "package.json").write_text(json.dumps(
            {"scripts": {"test:ui": "playwright test"}, "devDependencies": {"@playwright/test": "1.55.0"}}))
        (self.client / "feat-53.e2e.spec.ts").write_text(
            "".join(f"test('{r[1]}', async () => {{}});\n" for r in ROWS))

    def rel(self, path):
        return os.path.relpath(path, self.root)

    def shot(self, name, data=WEBP):
        path = self.ui_dir / name
        path.write_bytes(data)
        return self.rel(path)

    def trace(self, name, data=ZIP):
        path = self.ui_dir / "traces" / name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(data)
        return self.rel(path)

    def results(self, mutate=None, traced=()):
        checks = []
        for cid, title, surface, method, projects, _ in ROWS:
            for project in projects.split(","):
                status = "evidence" if method.startswith("inspection") else "passed"
                shots = [{"path": self.shot(f"{cid}-{project}.webp"), "route": "/", "fixture_state": "default",
                          "interaction": "load", "evidence_label": "overview-default"}]
                record = {"check_id": cid, "spec_title": title, "method": method, "surface": surface,
                          "project": project, "status": status, "screenshots": shots, "errors": []}
                if cid in traced:
                    record["trace"] = self.trace(f"{cid}--{project}.zip")
                checks.append(record)
        applicable = {"desktop-1440": [r[0] for r in ROWS], "desktop-1920": [r[0] for r in ROWS if r[3] != "automated-once"]}
        doc = {"schema": "harness-ui-results/1", "feature": FEATURE, "run_id": RUN,
               "design": self.rel(self.design), "served_bundle_commit": SHA,
               "projects": {"desktop-1440": {"width": 1440, "height": 1100}, "desktop-1920": {"width": 1920, "height": 1100}},
               "listed_check_ids": [r[0] for r in ROWS], "applicable_check_ids": applicable,
               "observed_check_ids": [r[0] for r in ROWS], "missing_check_ids": [],
               "checks": checks, "summary": {"status": "passed", "failed": 0}}
        if mutate:
            mutate(doc)
        path = self.ui_dir / "results.json"
        path.write_text(json.dumps(doc))
        return path

    def gate(self, changed=("client/src/tiles.tsx",), **overrides):
        args = dict(design=self.design, results=self.ui_dir / "results.json", feature=FEATURE, run_id=RUN,
                    served_bundle_commit=SHA, repo_root=self.root, changed=list(changed),
                    client_package=self.client)
        args.update(overrides)
        return uc.gate(**args)


class CheckContract(unittest.TestCase):
    def manifest(self, text, **kw):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "DESIGN.md"
            p.write_text(text)
            return uc.load_manifest(p, **kw)

    def refuses(self, text, needle, **kw):
        with self.assertRaises(uc.ContractError) as ctx:
            self.manifest(text, **kw)
        self.assertIn(needle, str(ctx.exception))

    def test_complete_contract_normalizes(self):
        m = self.manifest(design_text(), require_predicates=True, require_inspection_evidence=True)
        self.assertEqual(m["schema"], "harness-ui-manifest/1")
        self.assertEqual(m["listed_check_ids"], ["C1-HEADER-GEOMETRY", "SRC-TOKENS", "VIS-DENSITY"])
        self.assertEqual(m["applicable"]["desktop-1920"], ["C1-HEADER-GEOMETRY", "VIS-DENSITY"])
        self.assertEqual(m["checks"][1]["applicable_projects"], ["desktop-1440"])
        self.assertEqual(len(m["inspection_evidence"]), 2)

    def test_missing_section(self):
        self.refuses(design_text().replace("## Checks", "## Cheques"), "no `## Checks` section")

    def test_malformed_columns(self):
        self.refuses(design_text(header="| Check ID | Title | Surface | Method | Projects | Predicate |"), "columns")
        rows = ROWS[:1] + [("KPI-R1", "overview KPI grid is 4 plus 3", "overview-kpis", "automated-each-project", "desktop-1440")]
        self.refuses(design_text(rows=rows), "5 cells, not 6")

    def test_unknown_method_and_project(self):
        rows = [ROWS[0][:3] + ("manual",) + ROWS[0][4:]]
        self.refuses(design_text(rows=rows), "unknown method")
        rows = [ROWS[0][:4] + ("mobile-390",) + ROWS[0][5:]]
        self.refuses(design_text(rows=rows), "unknown project")

    def test_once_method_takes_exactly_one_project(self):
        rows = [ROWS[1][:4] + ("desktop-1440,desktop-1920",) + ROWS[1][5:]]
        self.refuses(design_text(rows=rows), "exactly one project")

    def test_duplicate_id_and_title(self):
        self.refuses(design_text(rows=ROWS + [ROWS[0][:1] + ("other title",) + ROWS[0][2:]]), "duplicate check id")
        self.refuses(design_text(rows=ROWS + [("OTHER-ID",) + ROWS[0][1:]]), "duplicate spec title")

    def test_predicates_required_only_when_asked(self):
        rows = [ROWS[0][:5] + ("",)] + ROWS[1:]
        self.manifest(design_text(rows=rows))
        self.refuses(design_text(rows=rows), "no predicate", require_predicates=True)

    def test_inspection_evidence_required_per_project(self):
        text = design_text(evidence=EVIDENCE[:1])
        self.manifest(text)
        self.refuses(text, "desktop-1920", require_inspection_evidence=True)
        bad = [EVIDENCE[0][:4] + ("",) + EVIDENCE[0][5:], EVIDENCE[1]]
        self.refuses(design_text(evidence=bad), "incomplete", require_inspection_evidence=True)
        stray = EVIDENCE + [("C1-HEADER-GEOMETRY",) + EVIDENCE[0][1:]]
        self.refuses(design_text(evidence=stray), "not an inspection row", require_inspection_evidence=True)


    def test_traces_table_normalizes_and_rejects_invalid_rows(self):
        m = self.manifest(design_text(traces=["VIS-DENSITY", "C1-HEADER-GEOMETRY"]))
        self.assertEqual(m["traced_check_ids"], ["VIS-DENSITY", "C1-HEADER-GEOMETRY"])
        self.assertEqual(self.manifest(design_text())["traced_check_ids"], [])
        self.refuses(design_text(traces=["VIS-DENSITY"], traces_header="| Check ID | Note |"), "Traces: columns")
        self.refuses(design_text(traces=["VIS-DENSITY", "VIS-DENSITY"]), "Traces: duplicate")
        self.refuses(design_text(traces=["NOT-A-CHECK"]), "Traces: NOT-A-CHECK is not a listed check")

    def test_expected_rows_must_match_byte_for_byte(self):
        expect = ["|".join(r[:5]) for r in ROWS]
        self.manifest(design_text(), expect=expect)
        wrong_title = expect[:]
        wrong_title[0] = wrong_title[0].replace("matches DESIGN", "matches design")
        self.refuses(design_text(), "expected row", expect=wrong_title)
        wrong_projects = expect[:]
        wrong_projects[1] = wrong_projects[1].replace("desktop-1440", "desktop-1920")
        self.refuses(design_text(), "expected row", expect=wrong_projects)
        self.refuses(design_text(), "not expected", expect=expect[:2])

    def test_cli_emits_manifest_and_refuses(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "DESIGN.md"
            p.write_text(design_text())
            out = subprocess.run([sys.executable, str(uc.__file__), "check", "--design", str(p)],
                                 capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertEqual(json.loads(out.stdout)["schema"], "harness-ui-manifest/1")
            p.write_text(design_text().replace("## Checks", "## Nope"))
            out = subprocess.run([sys.executable, str(uc.__file__), "check", "--design", str(p)],
                                 capture_output=True, text=True)
            self.assertEqual(out.returncode, 1)
            self.assertIn("REFUSED", out.stderr)


class GateEvidence(unittest.TestCase):
    def setUp(self):
        self.ws = Workspace()
        self.addCleanup(self.ws.tmp.cleanup)

    def failing(self, needle, mutate=None, traced=(), **kw):
        self.ws.results(mutate, traced=traced)
        verdict = self.ws.gate(**kw)
        self.assertEqual(verdict.status, "FAIL", verdict.reasons)
        self.assertTrue(any(needle in r for r in verdict.reasons), verdict.reasons)

    def test_complete_bundle_passes(self):
        self.ws.results()
        verdict = self.ws.gate()
        self.assertEqual(verdict.status, "PASS", verdict.reasons)
        self.assertEqual(verdict.reasons, [])

    def test_results_cannot_bring_their_own_check_list(self):
        def drop(doc):
            doc["listed_check_ids"] = doc["listed_check_ids"][:2]
            doc["applicable_check_ids"] = {p: [c for c in ids if c != "VIS-DENSITY"] for p, ids in doc["applicable_check_ids"].items()}
            doc["observed_check_ids"] = doc["listed_check_ids"]
            doc["checks"] = [c for c in doc["checks"] if c["check_id"] != "VIS-DENSITY"]
        self.failing("listed_check_ids", drop)

    def test_missing_applicable_record(self):
        def drop(doc):
            doc["checks"] = [c for c in doc["checks"] if not (c["check_id"] == "C1-HEADER-GEOMETRY" and c["project"] == "desktop-1920")]
        self.failing("no record for C1-HEADER-GEOMETRY at desktop-1920", drop)

    def test_duplicate_record(self):
        self.failing("duplicate record", lambda d: d["checks"].append(dict(d["checks"][0])))

    def test_wrong_title_and_wrong_applicability(self):
        def retitle(doc):
            doc["checks"][0]["spec_title"] = "shared header geometry matches design"
        self.failing("spec_title", retitle)

        def extra_project(doc):
            once = [c for c in doc["checks"] if c["check_id"] == "SRC-TOKENS"][0]
            doc["checks"].append(dict(once, project="desktop-1920"))
        self.failing("not applicable at desktop-1920", extra_project)

    def test_screenshot_evidence_must_be_real_webp(self):
        def empty(doc):
            doc["checks"][0]["screenshots"][0]["path"] = self.ws.shot("empty.webp", b"")
        self.failing("empty", empty)

        def png(doc):
            doc["checks"][0]["screenshots"][0]["path"] = self.ws.shot("not.webp", b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
        self.failing("not WebP", png)

        def none(doc):
            doc["checks"][0]["screenshots"] = []
        self.failing("no screenshot", none)

        def outside(doc):
            stray = self.ws.root / "stray.webp"
            stray.write_bytes(WEBP)
            doc["checks"][0]["screenshots"][0]["path"] = "stray.webp"
        self.failing("outside", outside)

    def test_inspection_manifest_entries_need_their_screenshot(self):
        def relabel(doc):
            for c in doc["checks"]:
                if c["check_id"] == "VIS-DENSITY" and c["project"] == "desktop-1920":
                    c["screenshots"][0]["evidence_label"] = "something-else"
        self.failing("overview-default", relabel)

    def test_identity_and_pin(self):
        self.failing("served_bundle_commit", lambda d: d.update(served_bundle_commit="0" * 40))
        self.failing("feature", lambda d: d.update(feature="FEAT-1-other"))
        self.failing("run_id", lambda d: d.update(run_id="other-run"))
        self.failing("schema", lambda d: d.update(schema="harness-ui-results/2"))

    def test_accounting_and_status_consistency(self):
        self.failing("missing_check_ids", lambda d: d.update(missing_check_ids=["C1-HEADER-GEOMETRY"]))
        self.failing("observed_check_ids", lambda d: d.update(observed_check_ids=d["observed_check_ids"][:1]))

        def failed(doc):
            doc["checks"][0]["status"] = "failed"
            doc["checks"][0]["errors"] = ["header height 64px < 72px"]
        self.failing("header height 64px", failed)

        def hidden_failure(doc):
            doc["checks"][0]["status"] = "failed"
            doc["summary"]["status"] = "passed"
        self.failing("summary", hidden_failure)

        def inspection_cannot_pass(doc):
            [c for c in doc["checks"] if c["check_id"] == "VIS-DENSITY"][0]["status"] = "passed"
        self.failing("inspection", inspection_cannot_pass)


    def test_gate_enforces_predicates_and_inspection_evidence(self):
        # F-01: a DESIGN that keeps its rows but drops the inspection manifest, or blanks a
        # predicate, must be refused by the GATE, not only by `check --require-...`.
        self.ws.design.write_text(design_text(evidence=[]))
        self.failing("no inspection evidence entry")
        rows = [ROWS[0][:5] + ("",)] + ROWS[1:]
        self.ws.design.write_text(design_text(rows=rows))
        self.failing("no predicate")

    def test_inspection_record_with_failed_setup_is_not_evidence(self):
        def broken_setup(doc):
            rec = [c for c in doc["checks"] if c["check_id"] == "VIS-DENSITY" and c["project"] == "desktop-1440"][0]
            rec["errors"] = ["every signed inspection setup and capture must execute"]
        self.failing("inspection setup failed", broken_setup)


    def test_traced_results_require_replayable_zip_inside_run_ui(self):
        self.ws.design.write_text(design_text(traces=["C1-HEADER-GEOMETRY", "SRC-TOKENS"]))
        self.ws.results(traced=("C1-HEADER-GEOMETRY", "SRC-TOKENS"))
        verdict = self.ws.gate()
        self.assertEqual(verdict.status, "PASS", verdict.reasons)

        def rec(doc, cid="C1-HEADER-GEOMETRY", project="desktop-1920"):
            return [c for c in doc["checks"] if c["check_id"] == cid and c["project"] == project][0]

        def absent(doc):
            del rec(doc)["trace"]
        self.failing("C1-HEADER-GEOMETRY@desktop-1920: no trace", absent, traced=("C1-HEADER-GEOMETRY", "SRC-TOKENS"))

        def absolute(doc):
            rec(doc)["trace"] = str(self.ws.ui_dir / "traces" / "C1-HEADER-GEOMETRY--desktop-1920.zip")
        self.failing("C1-HEADER-GEOMETRY@desktop-1920: trace", absolute, traced=("C1-HEADER-GEOMETRY", "SRC-TOKENS"))

        def escaping(doc):
            rec(doc)["trace"] = self.ws.rel(self.ws.ui_dir) + "/traces/../../escape.zip"
        self.failing("outside", escaping, traced=("C1-HEADER-GEOMETRY", "SRC-TOKENS"))

        def outside(doc):
            stray = self.ws.root / "stray.zip"
            stray.write_bytes(ZIP)
            rec(doc)["trace"] = "stray.zip"
        self.failing("outside", outside, traced=("C1-HEADER-GEOMETRY", "SRC-TOKENS"))

        def empty(doc):
            rec(doc)["trace"] = self.ws.trace("empty.zip", b"")
        self.failing("absent or empty", empty, traced=("C1-HEADER-GEOMETRY", "SRC-TOKENS"))

        def not_zip(doc):
            rec(doc)["trace"] = self.ws.trace("not.zip", WEBP)
        self.failing("not a ZIP", not_zip, traced=("C1-HEADER-GEOMETRY", "SRC-TOKENS"))

        def wrong_record(doc):
            rec(doc, "VIS-DENSITY", "desktop-1440")["trace"] = self.ws.trace("VIS-DENSITY--desktop-1440.zip")
        self.failing("VIS-DENSITY@desktop-1440: trace attached to a check the Traces table does not list", wrong_record,
                     traced=("C1-HEADER-GEOMETRY", "SRC-TOKENS"))

    def test_to_have_screenshot_requires_pixel_baseline_opt_in(self):
        spec = self.ws.client / "feat-53.e2e.spec.ts"
        spec.write_text(spec.read_text() + "test('pixels', async ({ page }) => { await expect(page).toHaveScreenshot(); });\n")
        self.failing("toHaveScreenshot( in feat-53.e2e.spec.ts but no Checks row opts into pixel-baseline")
        rows = ROWS + [("PIX-OVERVIEW", "overview pixels match baseline", "overview", "pixel-baseline",
                        "desktop-1440,desktop-1920", "baseline committed under e2e/__screenshots__")]
        self.ws.design.write_text(design_text(rows=rows))
        spec.write_text(spec.read_text() + "test('overview pixels match baseline', async () => {});\n")

        def add_pix(doc):
            for project in ("desktop-1440", "desktop-1920"):
                doc["checks"].append({"check_id": "PIX-OVERVIEW", "spec_title": "overview pixels match baseline",
                                      "method": "pixel-baseline", "surface": "overview", "project": project,
                                      "status": "passed", "errors": [],
                                      "screenshots": [{"path": self.ws.shot(f"PIX-{project}.webp"), "route": "/",
                                                       "fixture_state": "default", "interaction": "load",
                                                       "evidence_label": "overview-default"}]})
            doc["listed_check_ids"].append("PIX-OVERVIEW")
            doc["observed_check_ids"].append("PIX-OVERVIEW")
            for project in doc["applicable_check_ids"]:
                doc["applicable_check_ids"][project].append("PIX-OVERVIEW")
        self.ws.results(add_pix)
        verdict = self.ws.gate()
        self.assertEqual(verdict.status, "PASS", verdict.reasons)

    def test_client_package_change_requires_every_spec_title(self):
        # A title is present when the source names it literally OR the bundle carries an
        # executed record under that exact title (V7-01: specs are manifest-driven —
        # `test(check.spec_title, …)` — so a literal grep alone finds nothing).
        (self.ws.client / "feat-53.e2e.spec.ts").write_text("for (const c of manifest.checks) test(c.spec_title, async () => {});\n")
        self.ws.results()
        verdict = self.ws.gate(changed=["client/src/shared/Card.tsx"])
        self.assertEqual(verdict.status, "PASS", verdict.reasons)

        def drop_src_tokens(doc):
            doc["checks"] = [c for c in doc["checks"] if c["check_id"] != "SRC-TOKENS"]
        self.failing("no spec carries the title 'component source uses only theme tokens'", drop_src_tokens,
                     changed=["client/src/shared/Card.tsx"])
        (self.ws.client / "feat-53.e2e.spec.ts").write_text("test('component source uses only theme tokens', async () => {});\n")
        self.ws.results(drop_src_tokens)
        verdict = self.ws.gate(changed=["client/src/shared/Card.tsx"])
        self.assertNotIn("no spec carries the title 'component source uses only theme tokens'", " ".join(verdict.reasons))
        self.ws.results()
        verdict = self.ws.gate(changed=[".claude/skills/harness/bin/dashboard/serve.py"])
        self.assertEqual(verdict.status, "PASS", verdict.reasons)

    def test_missing_runner_or_contract_blocks(self):
        (self.ws.client / "package.json").write_text(json.dumps({"scripts": {"test": "vitest run"}}))
        self.failing("test:ui")
        (self.ws.client / "package.json").write_text(json.dumps({"scripts": {"test:ui": "playwright test"}}))
        self.ws.design.write_text(design_text().replace("## Checks", "## Nope"))
        self.failing("no `## Checks` section")

    def test_missing_results_file(self):
        verdict = self.ws.gate()
        self.assertEqual(verdict.status, "FAIL")
        self.assertIn("results.json", verdict.reasons[0])


if __name__ == "__main__":
    unittest.main()
