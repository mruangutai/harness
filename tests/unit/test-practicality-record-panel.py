#!/usr/bin/env python3
"""Unit floor for FEAT-2622 T-02: record-panel requires and carries exposure on every new row.

`plan-merge.py record-panel` is the only writer of a plan's panel findings, so it is where a plan-
level discounted finding is caught: a fan-in finding without exposure, or a contrived, no-worse,
non-adversary one above med, is refused (exit 5). A legal exposure lands on the new row as given,
and a base row without it keeps its bytes (D-05).

Imports nothing that is absent at the feature's base, so the red-first run there reaches every
check and prints its FAIL line.

    ./test-practicality-record-panel.py   -> exit 0 all pass, 1 otherwise
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(BIN))
sys.path.insert(0, str(ROOT / "tests"))

import panel_findings  # noqa: E402
import yaml  # noqa: E402
from check_support import Checks  # noqa: E402

CLI = str(BIN / "plan-merge.py")
ENV = {k: v for k, v in os.environ.items()
       if k not in ("CLAUDE_PROJECT_DIR", "HARNESS_PROJECT_DIR", "HARNESS_AGENT_TYPE")}
C = Checks()
PROPOSAL = ("schema: plan/1\nfeature: FEAT-99-fixture\ntasks:\n- id: T-01\n  title: t\n"
            "  change_type: logic\n  execution_mode: main-session-direct\n  files:\n  - a.py\n"
            "  verify: 'true'\n  intent: do it\n")
READERS = [{"reader": "scope", "status": "ran", "persona": "harness-code-reviewer",
            "reason": "none"}]
SUMMARY = "T-01 names no verify for its second file"
PLAUSIBLE = {"trigger": "plausible", "vs_today": "regression", "control": "chance"}
DISCOUNTED = {"trigger": "contrived", "vs_today": "no_worse", "control": "user"}


def run(*argv):
    return subprocess.run([sys.executable, CLI, *map(str, argv)], capture_output=True, text=True,
                          env=ENV)


def finding(severity, exposure):
    item = {"kind": "substance", "severity": severity, "reader": "scope", "summary": SUMMARY}
    if exposure is not None:
        item["exposure"] = exposure
    return item


def fan_in(path, findings):
    block = {"VERDICT": "PASS",
             "DIGEST": {"headline": "panel ran", "readers": READERS, "findings": findings,
                        "open_questions": []},
             "artifact": "runs/c1-product/panel-c1.md"}
    path.write_text("# Plan panel fan-in, fixture\n\n```yaml\n"
                    + yaml.safe_dump(block, sort_keys=False) + "```\n", encoding="utf-8")


def with_plan(body):
    """Run body(root, plan) over a fresh plan.yaml written by plan-merge.py apply."""
    def wrapped():
        with tempfile.TemporaryDirectory(prefix="practicality-record-panel-") as tmp:
            root = Path(tmp)
            plan = root / ".harness" / "harness" / "features" / "FEAT-99-fixture" / "plan.yaml"
            plan.parent.mkdir(parents=True)
            proposal = root / "proposal.yaml"
            proposal.write_text(PROPOSAL, encoding="utf-8")
            applied = run("apply", "--file", plan, "--proposal", proposal)
            if applied.returncode != 0:
                return False, f"apply exit={applied.returncode} {applied.stderr.strip()}"
            return body(root, plan)
    return wrapped


def record(root, plan, findings):
    digest = root / "panel-c1.md"
    fan_in(digest, findings)
    result = run("record-panel", "--file", plan, "--digest", digest, "--cycle", "1")
    rows = (yaml.safe_load(plan.read_text(encoding="utf-8")).get("panel") or {}).get("findings")
    return result, rows or []


def refused_case(severity, exposure, needle):
    @with_plan
    def body(root, plan):
        result, _rows = record(root, plan, [finding(severity, exposure)])
        return (result.returncode == 5 and needle in result.stderr,
                f"exit={result.returncode} {result.stderr.strip()}")
    return body


def carried_case(severity, exposure):
    @with_plan
    def body(root, plan):
        result, rows = record(root, plan, [finding(severity, exposure)])
        ok = (result.returncode == 0 and len(rows) == 1 and rows[0].get("exposure") == exposure
              and rows[0].get("disposition") == "open")
        return ok, f"exit={result.returncode} rows={rows!r} {result.stderr.strip()}"
    return body


@with_plan
def legacy_row_kept(root, plan):
    legacy = {"id": panel_findings.finding_id("scope", SUMMARY), "severity": "med",
              "reader": "scope", "kind": "substance", "summary": SUMMARY, "disposition": "open"}
    value = root / "panel.yaml"
    value.write_text(yaml.safe_dump({"last_run": "2026-11-27-01-plan-product", "cycle": 0,
                                     "readers": READERS, "findings": [legacy]}, sort_keys=False),
                     encoding="utf-8")
    seeded = run("set-panel", "--file", plan, "--value-file", value)
    if seeded.returncode != 0:
        return False, f"set-panel exit={seeded.returncode} {seeded.stderr.strip()}"
    before = plan.read_text(encoding="utf-8")
    block = re.search(r"(?m)^ *- id: " + legacy["id"] + r"\n(?: {3,}.*\n)*", before)
    result, rows = record(root, plan, [finding("med", PLAUSIBLE)])
    after = plan.read_text(encoding="utf-8")
    ok = (result.returncode == 0 and block is not None and block.group(0) in after
          and len(rows) == 1 and "exposure" not in rows[0]
          and panel_findings.shape_faults(rows[0]) == [])
    return ok, f"exit={result.returncode} rows={rows!r} {result.stderr.strip()}"


CASES = (
    ("record-panel-missing-exposure-refused", refused_case("med", None, "exposure")),
    ("record-panel-discounted-high-refused", refused_case("high", DISCOUNTED, "practicality rule")),
    ("record-panel-exposure-carried", carried_case("med", PLAUSIBLE)),
    ("record-panel-adversary-high-carried",
     carried_case("high", {**DISCOUNTED, "control": "adversary"})),
    ("record-panel-unrated-exposure-carried", carried_case("high", "unrated")),
    ("record-panel-legacy-row-kept", legacy_row_kept),
)

for name, case in CASES:
    try:
        passed, detail = case()
    except Exception as exc:  # noqa: BLE001  a base-tree red must still print its line
        passed, detail = False, f"{type(exc).__name__}: {exc}"
    C.check(name, passed, detail)

sys.exit(C.report())
