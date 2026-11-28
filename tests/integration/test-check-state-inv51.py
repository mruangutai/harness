#!/usr/bin/env python3
"""INV-51 (#1996): a feature at station abandoned carries no runs/ evidence.

`gh-sync.py abandon --yes` removes runs/ in the same act as recording the station; this invariant
is the backstop for an abandonment recorded any other way (a hand edit of plan.yaml, an older
abandon). Three cases on a throwaway tree: abandoned with runs/ is a VIOLATION naming the feature
and the run ids; abandoned without runs/ is silent; a live feature with runs/ is silent."""
import integration_support  # noqa: F401  sys.path seam: bin/ and tests/
import json
import os
import sys
import tempfile

from check_state_support import run  # noqa: E402
from check_support import Checks  # noqa: E402
from harness_config_support import write_config  # noqa: E402

C = Checks()
check = C.check

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
    return [l for l in run(root)[1].splitlines() if "INV-51" in l]


def tree(tmp):
    write_config(os.path.join(tmp, ".harness", "harness.json"), {"github": {"sync": False}})
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
    return C.report()


if __name__ == "__main__":
    sys.exit(main())
