#!/usr/bin/env python3
"""Unit floor for BUG-2582 T-01: `apply` / `add-tasks` convert a station-only record into a plan.

A station-only record (`station_only: true`, `tasks: []`) is what check-state INV-34 tells the
operator to write through `plan-merge.py apply`. Before BUG-2582 no verb could take it to a
task-bearing plan: the loader refuses the marker beside tasks, and nothing dropped it. The writer
now converts; the loader's pair stays as it was.

    PLAN_MERGE_UNION=<path to union.py>  optional: load a different union.py (red-first runs)
    CHECK_STATE_REV=<git revision>        optional: run that revision's check-state.py
    ./test-plan-merge-station-convert.py  -> exit 0 all pass, 1 otherwise
"""
import contextlib
import io
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

import yaml

from unit_support import ROOT, BIN, load_script

import plan_merge  # noqa: E402,F401  the package must be importable before its union module loads
import harness_merge  # noqa: E402
import harness_yaml  # noqa: E402
from harness_config_support import write_config  # noqa: E402

_UNION = os.environ.get("PLAN_MERGE_UNION") or str(BIN / "plan_merge" / "union.py")
union = load_script("union.py", path=_UNION, module_name="plan_merge.union", register=True)

CHECKER_RELATIVE = Path(".claude/skills/harness/bin/check-state.py")
DRAFTED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

BASE = ("schema: plan/1\n"
        "feature: BUG-99-fixture\n"
        "status: plan\n"
        "station_only: true\n"
        "tasks: []\n")

PROPOSAL = ("schema: plan/1\n"
            "feature: BUG-99-fixture\n"
            "status: plan\n"
            "tasks:\n"
            "  - id: T-01\n"
            "    title: fixture task\n"
            "    change_type: bugfix\n"
            "    execution_mode: main-session-direct\n"
            "    execution_reason: fixture\n"
            "    files: [x.py]\n"
            "    verify: 'true'\n"
            "    intent: fixture\n")

failures = []


def report(name, ok, detail=""):
    if ok:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name}: {detail}")
        failures.append(name)


def run_case(name, body):
    """Run one case; any refusal or exception is that case's FAIL, never a crash of the file."""
    try:
        ok, detail = body()
    except harness_merge.MergeRefusal as refusal:
        ok, detail = False, f"MergeRefusal code {refusal.code}: " + " ".join(refusal.lines)
    except Exception as exc:  # noqa: BLE001  a base-tree red must still print its line
        ok, detail = False, f"{type(exc).__name__}: {exc}"
    report(name, ok, detail)


def merge(base_text, proposal_text, verb="apply"):
    return union.apply_merge(base_text.encode("utf-8"), proposal_text, verb)


def refused_with(base_text, proposal_text, code):
    """(ok, detail): the merge raises MergeRefusal with `code`."""
    try:
        merge(base_text, proposal_text)
    except harness_merge.MergeRefusal as refusal:
        return refusal.code == code, f"refused with code {refusal.code}, want {code}"
    return False, f"merged without a refusal, want code {code}"


def receipt_lines(result):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        union._print_apply_receipt(result)
    return out.getvalue().splitlines()


def converted_case(verb):
    def body():
        result = merge(BASE, PROPOSAL, verb)
        doc = harness_yaml.load_str(result.out_bytes.decode("utf-8"), "<converted>")
        harness_yaml.validate_plan_doc(doc, "<converted>")
        lines = receipt_lines(result)
        problems = []
        if "station_only" in doc:
            problems.append("station_only still present")
        if [t.get("id") for t in doc.get("tasks") or []] != ["T-01"]:
            problems.append(f"tasks {doc.get('tasks')!r}")
        if doc.get("approval") != {"status": "pending"}:
            problems.append(f"approval {doc.get('approval')!r}")
        if not (isinstance(doc.get("drafted_at"), str) and DRAFTED_RE.match(doc["drafted_at"])):
            problems.append(f"drafted_at {doc.get('drafted_at')!r}")
        if doc.get("status") != "plan":
            problems.append(f"status {doc.get('status')!r}")
        if result.reset is not False:
            problems.append(f"reset {result.reset!r}")
        if not any(line.startswith("CONVERTED") for line in lines):
            problems.append(f"no CONVERTED receipt line in {lines!r}")
        if any(line.startswith("APPROVAL-RESET") for line in lines):
            problems.append("an APPROVAL-RESET receipt line")
        return not problems, "; ".join(problems)
    return body


def case_keeps_base_approval_and_stamp():
    base = BASE.replace("feature: BUG-99-fixture\n",
                        "feature: BUG-99-fixture\napproval:\n  status: pending\n"
                        "drafted_at: '2026-11-20T00:00:00Z'\n")
    out = merge(base, PROPOSAL).out_bytes.decode("utf-8")
    doc = harness_yaml.load_str(out, "<converted>")
    problems = []
    approvals = [line for line in out.splitlines() if line.startswith("approval:")]
    stamps = [line for line in out.splitlines() if line.startswith("drafted_at:")]
    if len(approvals) != 1 or len(stamps) != 1:
        problems.append(f"{len(approvals)} approval and {len(stamps)} drafted_at keys")
    if doc.get("approval") != {"status": "pending"}:
        problems.append(f"approval {doc.get('approval')!r}")
    if doc.get("drafted_at") != "2026-11-20T00:00:00Z":
        problems.append(f"drafted_at {doc.get('drafted_at')!r}")
    if "station_only" in doc:
        problems.append("station_only still present")
    return not problems, "; ".join(problems)


def case_marker_in_proposal_refused():
    proposal = PROPOSAL.replace("status: plan\n", "status: plan\nstation_only: true\n", 1)
    return refused_with(BASE, proposal, 5)


def finished_case(station):
    def body():
        # Both sides carry the finished station: a proposal at `status: plan` would stop at the
        # plain-key CONFLICT (7) and never reach the conversion this case pins.
        return refused_with(BASE.replace("status: plan\n", f"status: {station}\n"),
                            PROPOSAL.replace("status: plan\n", f"status: {station}\n"), 5)
    return body


def case_empty_proposal_stays_station_only():
    proposal = "schema: plan/1\nfeature: BUG-99-fixture\nstatus: plan\ntasks: []\n"
    doc = harness_yaml.load_str(merge(BASE, proposal).out_bytes.decode("utf-8"), "<merged>")
    problems = []
    if doc.get("station_only") is not True:
        problems.append(f"station_only {doc.get('station_only')!r}")
    if "approval" in doc:
        problems.append("approval key added")
    if "drafted_at" in doc:
        problems.append("drafted_at key added")
    return not problems, "; ".join(problems)


def schema_refuses(doc):
    try:
        harness_yaml.validate_plan_doc(doc, "<fixture>")
    except harness_yaml.PlanSchemaError:
        return True
    return False


def case_loader_pair_unchanged():
    unmarked = yaml.safe_load(BASE.replace("station_only: true\n", ""))
    marked_with_tasks = yaml.safe_load(BASE)
    marked_with_tasks["tasks"] = yaml.safe_load(PROPOSAL)["tasks"]
    problems = []
    if not schema_refuses(unmarked):
        problems.append("an empty plan without the marker loads")
    if not schema_refuses(marked_with_tasks):
        problems.append("the marker beside tasks loads")
    return not problems, "; ".join(problems)


def materialize_checker(directory):
    revision = os.environ.get("CHECK_STATE_REV")
    if not revision:
        return ROOT / CHECKER_RELATIVE
    archive = Path(directory) / "checker.tar"
    # The whole skill directory, not just bin/: the checker reads its sibling schemas/ at startup,
    # and an archive of bin/ alone dies on harness.json before INV-34 runs.
    subprocess.run(
        ["git", "archive", "--format=tar", f"--output={archive}", revision,
         str(CHECKER_RELATIVE.parent.parent)],
        cwd=ROOT, check=True,
    )
    extracted = Path(directory) / "revision"
    extracted.mkdir()
    with tarfile.open(archive) as bundle:
        bundle.extractall(extracted, filter="data")
    return extracted / CHECKER_RELATIVE


def case_inv34_remedy_line():
    with tempfile.TemporaryDirectory() as checker_dir, tempfile.TemporaryDirectory() as fixture:
        checker = materialize_checker(checker_dir)
        root = Path(fixture)
        feature = root / ".harness/harness/features/FEAT-TEST"
        feature.mkdir(parents=True)
        (root / ".harness/team-config.yaml").write_text("agents: {}\n")
        write_config(root / ".harness/harness.json")
        (feature / "feature.json").write_text("{}\n")
        env = dict(os.environ, HARNESS_PROJECT_DIR=str(root))
        run = subprocess.run([sys.executable, str(checker)], cwd=root, env=env, text=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = run.stdout
    if "station_only: true" not in out or "FIRST CHECK WHETHER A REAL PLAN WAS DELETED" not in out:
        return False, "remedy absent"
    if "converts this record into the plan" not in out:
        return False, "remedy present, conversion sentence absent"
    return True, ""


def main():
    run_case("bug2582-convert-apply", converted_case("apply"))
    run_case("bug2582-convert-add-tasks", converted_case("add-tasks"))
    run_case("bug2582-convert-keeps-base-approval-and-stamp", case_keeps_base_approval_and_stamp)
    run_case("bug2582-marker-in-proposal-refused", case_marker_in_proposal_refused)
    for station in ("done", "abandoned", "rejected"):
        run_case(f"bug2582-finished-{station}", finished_case(station))
    run_case("bug2582-empty-proposal-stays-station-only", case_empty_proposal_stays_station_only)
    run_case("bug2582-loader-pair-unchanged", case_loader_pair_unchanged)
    run_case("bug2582-inv34-remedy-line", case_inv34_remedy_line)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
