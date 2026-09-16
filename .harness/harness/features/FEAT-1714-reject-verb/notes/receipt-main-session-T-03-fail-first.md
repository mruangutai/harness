# Fail-first receipt — FEAT-1714 T-03 (TERMINAL_STATIONS cutover, rejected station, INV-44)

The new and updated cases copied into a throwaway worktree at the parent commit (84885aba, T-02's working tree excluded) and run there. Captured 2026-09-16T06:09Z by Main.

```
== tests/integration/test-check-state-feat59.py
FAIL - case (44.a) a conforming rejected record is silent on INV-44 and on the approval gate
FAIL - case (44.b) cycles_used other than integer 0 is a VIOLATION naming cycles
FAIL - case (44.c) zero runs is a VIOLATION naming the count
FAIL - case (44.d) two runs is a VIOLATION naming the count
FAIL - case (44.e) the one run owned by a lead is a VIOLATION naming the agent
FAIL - case (44.f) no reject judgement is a VIOLATION naming the kind and remedy
FAIL - case (44.g) an approved plan under a rejected station is a VIOLATION
FAIL - case (44.h) a signed BRIEF under a rejected station is a VIOLATION
FAIL - case (44.i) a panel mapping under a rejected station is a VIOLATION
FAIL - case (44.j) every bad dimension is reported separately
== tests/integration/test-worktree-terminal.py
FAIL: FEAT-1714: plan.yaml station `rejected` -> terminal, reason naming the station
== tests/unit/test-factory-config.py
FAIL  (T-03) TERMINAL_MARKER no longer exists — TERMINAL_STATIONS is the one terminal vocabulary
FAIL  (T-02) TERMINAL_STATIONS is the ordered abandoned/rejected non-board tuple
== tests/integration/test-check-plan-routes.py
== tests/integration/test-plan-merge.py
FAIL  set-task-station's exit-4 line lists the legal stations for 'Done', rejected included
FAIL  set-task-station's exit-4 line lists the legal stations for 'icebox', rejected included
FAIL  set-task-station's exit-4 line lists the legal stations for '', rejected included
FAIL  set-task-station's exit-4 line lists the legal stations for 'abandonded', rejected included
FAIL  set-feature-station's exit-4 line lists the legal stations for 'Done', rejected included
FAIL  set-feature-station's exit-4 line lists the legal stations for 'icebox', rejected included
FAIL  set-feature-station's exit-4 line lists the legal stations for '', rejected included
FAIL  set-feature-station's exit-4 line lists the legal stations for 'abandonded', rejected included
FAIL  set-task-station ACCEPTS rejected, a terminal station
FAIL  set-feature-station ACCEPTS rejected (FEAT-1714 T-03: reject's one station write)
```

Note: the parent commit still carries TERMINAL_MARKER (T-02's worktree change is uncommitted), so test-factory-config's (T-03) hasattr check and the vocabulary pins are red for the right reason; INV-44 does not exist there at all, so 44.a is silent-by-absence (green) and every violation case is red.
