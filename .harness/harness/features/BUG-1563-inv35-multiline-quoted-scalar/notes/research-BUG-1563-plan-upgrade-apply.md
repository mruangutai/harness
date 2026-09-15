# BUG-1563 plan-upgrade panel application

## Conclusion

Panel cycle 1 is canonically recorded in `plan.yaml`. No BRIEF or task amendment was warranted: the only finding is task-scoped, informational proportionality residue, and the panel concluded there is no smaller honest task under the operator's no-waiver instruction and DEC-217 hard matrix.

## Finding disposition

- The scope reader passed with no findings.
- The should-not-exist reader identified that T-02 and SC-03 repeat the three integration-proven outcomes under the active unit kind. This residue remains open at its original `info` severity, `proportionality` kind, and `task` scope because removing any of the two quoted cases or the unquoted positive control would leave the hard matrix coverage incomplete.
- The design reader passed because the amendment introduces no user-facing surface and needs neither DESIGN.md nor a prototype.

## Preserved boundaries

- T-01 remains `done`; its behavior, files, verification command, intent, traces, and `main-session-direct` routing were not amended.
- T-02 remains the single-file matrix closure for `tests/unit/test-check-state-inv35.py`, depends on T-01, and remains `main-session-direct` under DEC-174/179.
- Approval remains `pending`.
- No implementation or test file was edited during panel application.

## Evidence

- `plan-merge.py record-panel ... --cycle 1` added `PF-7e6d83071485b8469399e400d5517723` and recorded all three reader statuses from `runs/plan-upgrade-product/panel-c1.md`.
- The required scoped `plan-merge.py check` resolved 2 tasks and 3 anchors with 0 failures.
- Post-record inspection of `plan.yaml` confirms panel cycle 1, the unmodified task boundaries and stations, and pending approval.
