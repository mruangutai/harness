#!/usr/bin/env python3
"""Unit floor for BUG-2349: plan_merge.union's union-key head selection, in process.

An inline-empty base list (`decisions: []` / `tasks: []`) yields its head to a proposal that adds
items; a base list that has items keeps its own head. Exercised through `apply_merge`, the
module's in-process entry point, below the CLI subprocess the integration cases drive.

    PLAN_MERGE_UNION=<path to union.py>  optional: load a different union.py (red-first runs)
    ./test-plan-merge-union-head.py      -> exit 0 all pass, 1 otherwise
"""
import importlib.util
import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(BIN))

import plan_merge  # noqa: E402  the package must be importable before its union module loads
import harness_merge  # noqa: E402

_UNION = os.environ.get("PLAN_MERGE_UNION") or str(BIN / "plan_merge" / "union.py")
_spec = importlib.util.spec_from_file_location("plan_merge.union", _UNION)
union = importlib.util.module_from_spec(_spec)
sys.modules["plan_merge.union"] = union
_spec.loader.exec_module(union)

failures = []


def check(name, ok, detail=""):
    print("PASS" if ok else "FAIL", name, detail if not ok else "")
    if not ok:
        failures.append(name)


HEAD = "schema: plan/1\nfeature: FEAT-99-fixture\napproval:\n  status: pending\n"
TASK = "  - id: T-01\n    title: Task T-01\n    status: ready\n"
DECISION = "  - id: D-01\n    choice: Adopt x\n"


def merge(base_text, proposal_text):
    """(merged text, None) or (None, the refusal)."""
    try:
        return union.apply_merge(base_text.encode("utf-8"), proposal_text).out_bytes.decode(), None
    except harness_merge.MergeRefusal as refusal:
        return None, refusal


def case_inline_empty_base_takes_the_proposal_head():
    for key, item, expected in (
        ("decisions", DECISION, [{"id": "D-01", "choice": "Adopt x"}]),
        ("tasks", TASK, [{"id": "T-01", "title": "Task T-01", "status": "ready"}]),
    ):
        base = HEAD + ("tasks:\n" + TASK if key == "decisions" else "") + f"{key}: []\n"
        out, refusal = merge(base, f"{key}:\n{item}")
        check(f"{key}: [] gaining an item merges without a refusal", refusal is None,
              repr(refusal))
        check(f"{key}: [] gains the proposal's block head, not the inline []",
              out is not None and f"{key}: []" not in out and f"\n{key}:\n" in out, repr(out))
        check(f"{key}: [] merged plan reloads with the added item",
              out is not None and yaml.safe_load(out).get(key) == expected, repr(out))


def case_base_with_items_keeps_its_own_head():
    base = HEAD + "tasks:\n" + TASK + "decisions:   # base head comment\n" + DECISION
    out, refusal = merge(base, "decisions:\n  - id: D-02\n    choice: Adopt y\n")
    check("a decisions base with items merges D-02", refusal is None, repr(refusal))
    check("a decisions base with items keeps its own head line",
          out is not None and "decisions:   # base head comment\n" in out, repr(out))
    check("a decisions base with items carries D-01 then D-02",
          out is not None and [d["id"] for d in yaml.safe_load(out)["decisions"]]
          == ["D-01", "D-02"], repr(out))


for case in (case_inline_empty_base_takes_the_proposal_head,
             case_base_with_items_keeps_its_own_head):
    case()

print("FAIL test-plan-merge-union-head.py" if failures else "PASS test-plan-merge-union-head.py")
sys.exit(1 if failures else 0)
