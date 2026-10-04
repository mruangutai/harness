#!/usr/bin/env python3
"""INV-51 (#1996): a feature at station abandoned carries no runs/ evidence.

`gh-sync.py abandon --yes` removes runs/ in the same act as recording the station; this invariant
is the backstop for an abandonment recorded any other way (a hand edit of plan.yaml, an older
abandon). Three cases on a throwaway tree: abandoned with runs/ is a VIOLATION naming the feature
and the run ids; abandoned without runs/ is silent; a live feature with runs/ is silent."""
import os as _anchor_os, sys as _anchor_sys
_anchor_sys.path.insert(0, _anchor_os.path.dirname(_anchor_os.path.abspath(__file__)))

import json
import os
import subprocess
import sys
import tempfile

from check_state_support import SCRIPT, _root_env

FAILS = []

PLAN = """schema: plan/1
feature: {feat}
status: {station}
approval:
  status: approved
tasks:
  - id: T-01
    title: t
    change_type: test
    execution_mode: main-session-direct
    files: [a.py]
    verify: true
    intent: x
"""


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name)
    if not ok:
        FAILS.append(name)
        print("     " + detail[:500])


def feature(root, feat, station, run_ids):
    d = os.path.join(root, ".harness", "harness", "features", feat)
    os.makedirs(d)
    with open(os.path.join(d, "plan.yaml"), "w") as f:
        f.write(PLAN.format(feat=feat, station=station))
    with open(os.path.join(d, "BRIEF.md"), "w") as f:
        f.write(f"# {feat}\n\n## Approval\n\nstatus: approved\n")
    with open(os.path.join(d, "feature.json"), "w") as f:
        json.dump({"feature_id": feat, "branch": "none", "pr": None, "review_sha": "none",
                   "cycles_used": 0, "max_total_cycles": 10, "runs": [], "mission": "ship",
                   "judgements": [{"at": "2026-01-01T00:00:00+00:00", "by": "harness-pm", "kind": "mission", "decision": "ship", "reason": "r"}]}, f)
    for run_id in run_ids:
        os.makedirs(os.path.join(d, "runs", run_id, "ui", "evidence"))
        with open(os.path.join(d, "runs", run_id, "ui", "evidence", "a.webp"), "wb") as f:
            f.write(b"RIFF")


def inv51_lines(root):
    r = subprocess.run([sys.executable, SCRIPT], cwd=root, capture_output=True, text=True, env=_root_env(root))
    return [l for l in r.stdout.splitlines() if "INV-51" in l]


def tree(tmp):
    os.makedirs(os.path.join(tmp, ".harness"))
    with open(os.path.join(tmp, ".harness", "team-config.yaml"), "w") as f:
        f.write("agents: {}\n")
    with open(os.path.join(tmp, ".harness", "harness.json"), "w") as f:
        f.write('{"github": {"sync": false, "repo": null}}\n')
    feature(tmp, "FEAT-1-dropped", "abandoned", ["validate-c1-validator", "fix-c2-eng"])
    feature(tmp, "FEAT-2-clean", "abandoned", [])
    feature(tmp, "FEAT-3-live", "review", ["validate-c1-validator"])


def assert_findings(lines):
    hit = [l for l in lines if "FEAT-1-dropped" in l]
    names_runs = bool(hit) and "validate-c1-validator" in hit[0] and "fix-c2-eng" in hit[0]
    check("abandoned feature with runs/ is one INV-51 VIOLATION naming the feature", len(hit) == 1 and "VIOLATION" in hit[0], "\n".join(lines))
    check("the finding names the run ids it would prune", names_runs, "\n".join(hit))
    check("abandoned feature without runs/ is silent", not any("FEAT-2-clean" in l for l in lines), "\n".join(lines))
    check("a live feature with runs/ is silent", not any("FEAT-3-live" in l for l in lines), "\n".join(lines))


def main():
    with tempfile.TemporaryDirectory() as tmp:
        tree(tmp)
        assert_findings(inv51_lines(tmp))
    print(f"{len(FAILS)} failure(s)" if FAILS else "all checks passed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
