#!/usr/bin/env python3
"""Gate the dashboard's three rendered chart assertions through Vitest JSON."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLIENT = ROOT / ".claude/skills/harness/bin/dashboard/client"
CARRIER = CLIENT / ".vitest/json/output.json"
REMEDY = "npm ci --prefix .claude/skills/harness/bin/dashboard/client"
REQUIRED_LABELS = (
    "grading panel mounts the Shape A histogram",
    "trend panel mounts the Shape B time series",
    "merged PR panel mounts the Shape B weekly line",
)
VITEST_CACHE = CLIENT / "node_modules/.vite/vitest"


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def assertion_statuses(report, label):
    return [
        result.get("status")
        for suite in report.get("testResults", [])
        for result in suite.get("assertionResults", [])
        if label in result.get("fullName", "")
    ]


def environment_error():
    missing = [tool for tool in ("node", "npm") if shutil.which(tool) is None]
    if missing:
        return f"missing {', '.join(missing)}; run {REMEDY}"
    if not (CLIENT / "node_modules").is_dir():
        return f"missing client node_modules; run {REMEDY}"
    return None


def load_report():
    completed = subprocess.run(
        ["npm", "--prefix", str(CLIENT), "run", "--silent", "test", "--",
         "--reporter=json", "--outputFile=.vitest/json/output.json"],
        cwd=ROOT, text=True, capture_output=True)
    if completed.returncode:
        print(completed.stdout, end="")
        print(completed.stderr, end="", file=sys.stderr)
        fail(f"Vitest exited {completed.returncode}")
        return None
    if not CARRIER.is_file():
        fail("Vitest did not write JSON carrier; run " + REMEDY)
        return None
    try:
        return json.loads(CARRIER.read_text())
    except (OSError, json.JSONDecodeError) as error:
        fail(f"malformed Vitest JSON carrier: {error}")
        return None


def grade_report(report):
    statuses = {label: assertion_statuses(report, label) for label in REQUIRED_LABELS}
    for label, found in statuses.items():
        if not found:
            return fail(f"missing assertion: {label}")
        if "passed" not in found:
            if any(status in ("skipped", "pending", "todo") for status in found):
                return fail(f"skipped assertion: {label}")
            return fail(f"failing assertion: {label} (statuses: {', '.join(found)})")
    for label in REQUIRED_LABELS:
        print(f"passed: {label}")
    return 0


def main():
    try:
        CARRIER.unlink(missing_ok=True)
        if error := environment_error():
            return fail(error)
        report = load_report()
        return 1 if report is None else grade_report(report)
    finally:
        shutil.rmtree(CARRIER.parent.parent, ignore_errors=True)
        shutil.rmtree(VITEST_CACHE, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
