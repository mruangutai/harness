# STATE

## Current

- feature: FEAT-06-team-layer-inv6
- phase: build
- run: none open — segment 1 was main-session-direct and opens no run dir
- squad: none
- status: in_progress

**Segment 1 complete: 8 of 8 PASS, zero send-backs, so `cycles_used` stays 4.** T-01, T-02, T-04,
T-10, T-05, T-06, T-09, T-11 all landed. All three gates exit 0 (`run-unit-tests.sh`,
`check-docs.sh`, `check-state.sh` with zero VIOLATION lines). **Every verify was re-run
independently by the orchestrator at source** before this was written — the executor's report was
not taken on trust.

**Remaining: T-08 (documentor, `docs/**` — the one squad dispatch), then T-07 (main-session).**
T-07 depends on T-08, so the build cannot finish without the dispatch.

**SC-14 measured both ways, not asserted.** At `635ef14`: `test_matrix` lines 0, 8-line window 0
hits. Now: `test_matrix` lines 2, window 7 hits. Line budgets held with room — `SKILL.md` +14 of a
20 cap, `harness-team/SKILL.md` +12 of 14, zero deletions on either, so no reflow inflated the count.

**Three defects were caught mid-execution that would each have shipped green.** (1) T-05's widened
gate would have scanned NOTHING — Python `glob` does not descend into dotted directories, so
`glob('**/*.yaml')` from the repo root returns 0 while `os.walk('.harness')` finds 54; independently
re-measured here. Switched to `os.walk`; the corpus now reports 56 across 2 roots. (2) SC-06 was
proven to discriminate by running the new fixture against the pre-widening `scan()` at `635ef14`:
0 files, 0 findings. (3) A comment using `PLACEHOLDER_UNSET` by name broke T-01's own `== 1` verify.

**T-02's predicated sweep was vindicated three times.** The handoff named four count-bearing
comments; the orchestrator's re-grep found a fifth (`review.yaml:5`); the sweep itself created a
sixth, caught by its own closing re-grep. A sixth enumeration would have missed it.

**MF-1 closed the cheap way, as the approval block authorised** — the re-grep ran as an
execution-time check. `PLAN.md`'s approved `verify:` was not edited.

**Cost: 0.00 metered of the $100 build allowance, and that figure understates reality.** Nine of ten
tasks execute at depth-0 in the main session, which is not separable to this feature. Only the T-08
dispatch and the validate-phase spawns can be metered honestly.

**Carried into segment 3:** T-01's `wc -l == 1` conjunct must be re-run after T-07 lands a new file
in `bin/`. **`feature.yaml` is at 191 of its 200-line cap** — trim before adding validate runs.

## Open Questions

- none blocking. Issue #36 (`run-unit-tests.sh` misconfigured-error when run outside the repo root,
  pre-existing at `635ef14`, fail-closed) is filed and out of scope. The ten advisories and AQ-2
  remain backlog for the user's ship acceptance.
