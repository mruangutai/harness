#!/usr/bin/env python3
"""Tests for cost-report.py's --into splice (B-4).

WHY: the rule docs used to say `cost-report.py --yaml >> <run_dir>/state.yaml`. A lead
sets `cost: pending_orchestrator` as its placeholder, so appending produced a SECOND
top-level `cost:` key — silently shadowed by the last occurrence in every YAML parser,
and rejected by INV-16 (DEC-156). The FEAT-02 audit found `cost:` twice in 12 of 15
state files. `--into` replaces instead, so the footgun is gone rather than documented.

The first version of splice_cost emitted the block once per occurrence, so a file with
two cost: keys came out with two — while printing that it had collapsed them. Hence the
`duplicates` cases: the invariant under test is EXACTLY ONE cost: key afterwards, always.
"""
import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get("COST_REPORT_BIN") or os.path.join(HERE, "cost-report.py")
spec = importlib.util.spec_from_file_location("cost_report", SRC)
cr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cr)

BLOCK = ["cost:", "  currency: usd", "  total: 12.5", "  by_agent:",
         "    - { agent: harness-qa, usd: 12.5 }"]

# (name, source state.yaml, sibling keys that must survive)
CASES = [
    ("a lead's placeholder is REPLACED, not appended",
     "run_id: r1\nstatus: complete\ncost: pending_orchestrator\nverdict: PASS\n",
     ["run_id: r1", "status: complete", "verdict: PASS"]),
    ("no cost key at all — appended once",
     "run_id: r2\nstatus: complete\n",
     ["run_id: r2", "status: complete"]),
    ("an already-written full block is replaced whole",
     "run_id: r3\ncost:\n  currency: usd\n  total: 1.0\n  by_agent:\n"
     "    - { agent: stale }\nverdict: PASS\n",
     ["run_id: r3", "verdict: PASS"]),
    ("two cost keys collapse to ONE",
     "run_id: r4\ncost: pending_orchestrator\nstatus: complete\ncost:\n  total: 9\n",
     ["run_id: r4", "status: complete"]),
    ("a trailing duplicate placeholder also collapses",
     "run_id: r5\ncost:\n  total: 1\ncost: pending_orchestrator\n",
     ["run_id: r5"]),
]


def main():
    fails = 0
    for name, src, survivors in CASES:
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "state.yaml")
            open(p, "w").write(src)
            rc = cr.splice_cost(p, BLOCK)
            got = open(p).read()
            keys = [l for l in got.splitlines() if l.startswith("cost:")]
            problems = []
            if rc != 0:
                problems.append(f"returned {rc}, expected 0")
            if len(keys) != 1:
                problems.append(f"{len(keys)} top-level cost: keys, expected exactly 1")
            if "  total: 12.5" not in got:
                problems.append("the new block's total is absent")
            if "total: 9" in got or "total: 1.0" in got or "agent: stale" in got:
                problems.append("a stale cost value survived the replace")
            for s in survivors:
                if s not in got:
                    problems.append(f"sibling key lost: {s!r}")
            if problems:
                fails += 1
                print(f"FAIL  {name}")
                for pr in problems:
                    print(f"        {pr}")
                print("      got:\n" + "\n".join("        " + l for l in got.splitlines()))
            else:
                print(f"ok    {name}")

    # A missing file is an error, not a silent no-op: the orchestrator would otherwise
    # believe it had metered a run it never touched.
    rc = cr.splice_cost(os.path.join(tempfile.gettempdir(), "no-such-state-file.yaml"), BLOCK)
    if rc == 0:
        print("FAIL  a missing state file must be an error, got 0")
        fails += 1
    else:
        print("ok    a missing state file is an error")

    total = len(CASES) + 1
    print(f"\n{total - fails}/{total} cases passed.")
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
