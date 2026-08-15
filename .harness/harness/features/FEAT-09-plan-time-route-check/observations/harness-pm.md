# Observations — harness-pm — FEAT-09-plan-time-route-check

- 2026-08-05: the dispatch predicted ONE hazard in `check-domain.sh:26` (`payload=$(cat)` hangs on
  an argv invocation). Measured at `ae2443d` there are TWO, and the second is worse: with stdin an
  open pipe it hangs past 10s, but with stdin `/dev/null` or closed it exits **0 with empty stdout**
  — a fail-open answer indistinguishable from "clean". A brief that names a hazard names the half
  someone already noticed; probe both directions of the input, not just the predicted one.
- 2026-08-05: `run-unit-tests.sh:9-21` has a drift detector — any `test-*.py` under
  `.claude/skills/harness/bin/` that is absent from the explicit `SCRIPTS` array exits 2 and fails
  the WHOLE suite, not just that file. A task that adds a test file and defers the registration
  turns every other task's `verify:` red.
- 2026-08-05: `execution_mode:` had three spellings in the tree before this plan pinned two —
  `squad-dispatched` (FEAT-06, FEAT-07), `team` (FEAT-08), `main-session-direct` (all three). A
  field invented ad hoc by successive plans acquires synonyms before it acquires a parser.
