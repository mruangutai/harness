# Code review — plan c0

**FAIL.** The task graph is topological, every SC is traced, every task serves a live requirement, and normalized `files:` paths have no cross-task OVERLAP. The architecture is appropriately local: one ordered invariant registry keeps selection and ordering behind the existing checker interface; runner-owned context centralizes shared parsing; the three audits stay at the existing consolidation seam; and the two canonical writers share one post-write adapter rather than duplicating subprocess policy.

## Must fix

- **High · substance · task scope — the only code-grade gate runs before two successor tasks change Python.** T-01 traces SC-09 and runs `code-grade.py` (`plan.yaml:70,90`), but T-02 and T-03 subsequently change production and test Python (`plan.yaml:97-114,115-143`) without either successor grading the final baseline-to-HEAD range. Thus T-02 can introduce a grade-3 production function, or T-03 a grade-2 test function, and every listed task verify can still pass even though SC-09 and D-08 require *all* changed production functions to grade 4/5 and changed tests 3+. This is exactly a successor invalidating an earlier gate, even though plan-merge OVERLAP semantics report no shared literal path. **PM apply:** add SC-09 to terminal T-03's traces and append `python3 .claude/skills/harness/bin/code-grade.py --base 1b69f67f4a24c4b011cd1fa724e1bb66d4c77cb7 --head HEAD` to T-03's verify (or add an equivalent terminal task depending on T-01, T-02, and T-03). Keep T-01's local grade run if desired for task-local feedback, but do not treat it as the final SC-09 receipt.

## Coverage and proportionality

- SC-01 through SC-09 all have at least one task trace; there are no nonexistent trace targets or orphan success criteria.
- Dependencies `T-01 → T-02 → T-03` are topological and match the implementation seams.
- No task is requirement-free, and the lane remains proportionate to the operator-confirmed plan mission; no task- or mission-proportionality finding.
- No open architecture question: the exact reads vocabulary, canonical writers, and no-exemption grading posture are resolved in D-02, D-07, and D-08.
