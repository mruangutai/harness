# STATE

## Current

- feature: FEAT-41-one-station-vocabulary
- run: 2026-08-30-02-orchestrator. Plan revision only. NO squad was dispatched and no run row is
  added; the build is STOPPED by the operator and no task is built.
- squad: none
- status: Plan. Moved back from Ready, because the plan is under revision and its approval is
  withdrawn — a signed, buildable plan is what Ready asserts and there is not one right now.
- THE REVISION IS APPLIED AND BOTH GATES ARE GREEN. plan.yaml carries 13 tasks — T-01..T-11,
  T-14, T-15 — with T-12 and T-13 gap-noted and nothing renumbered. `check-plan-routes.py` exits
  0, "0 violation(s) across 1 plan(s)", and prints exactly one ordinary team line for the whole
  plan: `OK T-15 granted to harness-documentor`. `check-state.sh` exits 0 with zero violations.
- WHAT LANDED, all at 15394e5: T-13 struck with SC-05 and SC-12, and the post-rename basename is
  absent from both artifacts (D-01 records the reversal). T-07 names and rekeys SEAM_NOTES in the
  same edit as STATUS_ORDER and runs SC-02's own measurement. T-15 added on the documentor lane
  to AMEND — never strike — the contradicted clause in DEC-203 s6, DEC-191 and DEC-182, graded by
  SC-14. D-11 records its reversal of the grilling's Backlog line; D-09 records that the clause
  corrections came back inside the feature. PB-04 narrowed; PB-05, PB-06 and PB-07 opened.
- T-01 WAS BUILT, WAS GREEN, AND BROKE THE STATE GATE. It landed at cd4aca6 with
  test-factory-config.py at 112/112 and the `_STATION_KEYS` absence grep clean, and turning
  `github.board.stations` from a mapping into a list broke every consumer that subscripts it by
  name — `board_lifecycle._declared_stations` raises `TypeError: list indices must be integers`,
  check-state.sh tracebacks out of INV-26. Reverted by the main session at 33e716c; T-01 is back
  to `status: pending` and its code is out of the tree. The verify could not see it because it
  exercised factory_config in ISOLATION. Filed as #1033.
- THE #1033 AUDIT IS COMPLETE AND MEASURED, NOT GUESSED. FIVE tasks change the shape of a value a
  gate reads — T-01, T-02, T-04, T-06, T-07 — and each now runs a real consumer against the LIVE
  declaration plus the gate itself. The probe was proved discriminating before it was written in:
  it exits 0 on today's mapping and reds with the exact TypeError on a simulated list.
  EIGHT non-test modules read `board["stations"]` as a mapping and ZERO of them are orphaned —
  every one is named in some surviving task's `files:`, so the plan does repair them all.
  REJECTED with reasons, so the audit is falsifiable: T-03, T-08, T-09 (consumers of a shape,
  not producers), T-05, T-15 (docs), T-10 (already carries a live `gh_board.load_board('.')`
  line), T-11 (deletes test cases), T-14 (adds an invariant, changes no shape).
- T-14's SIGNED MEASUREMENT WAS FALSE AND IS CORRECTED IN PLACE, not rewritten away. It claimed
  the reported set was EMPTY at `cc00983`; the signature commit `49638bf` rewrote plan.yaml after
  that measurement, so the set was {FEAT-41 itself}. RE-WALKED AT HEAD, 40 dirs: 1 reported
  (FEAT-41), 4 silenced by the terminal scope (FEAT-26, FEAT-27, FEAT-32, FEAT-33), 19 where the
  pin resolves but the plan path is absent in it, 4 unresolvable pins, 1 with no plan, 11 current.
  The 19 are ALL terminal, so the Q6 scope silences them before the both-reads clause is reached —
  live exposure zero, which is exactly why case (inv32.d) was added to pin that clause.
- cycles: 9 of 24. This revision is one rework cycle (DEC-157 counts rework only). THE RAISE IS
  THE OPERATOR'S, granted 2026-08-30 after a three-reader prosecution panel and a reverted T-01,
  and sized on measurement rather than feel: planning alone consumed 8, twelve tasks remain to be
  hand-built under DEC-174 with a validation panel and fix loops still ahead, so 15 rework cycles
  of headroom is a tripwire for a runaway rather than a bound on normal work.
- runs: 15 of 45, unchanged — no lead ran, so no run row is added. `max_total_runs` is
  informational (INV-22) and was raised only so the tripwire stays meaningful instead of
  permanently tripped.
- review_sha: 49638bf -> 15394e5, the revision commit. Re-pinned because the plan bytes moved;
  byte-verified with `git show 15394e5:<path>` against the working copy for both artifacts.
- next: THE OPERATOR RE-SIGNS. Approval is `pending` in plan.yaml and BRIEF.md and neither is
  mine to sign (DEC-120). Scope is whole per the 2026-08-30 ruling — all twelve surviving tasks
  stay, the vocabulary migration is not deferred, #845 and #867 both close here, and the T-14
  fast path stays forbidden. After signature the build resumes in the signed order, and T-01 and
  T-02 land in ONE commit because T-01's consumer smoke cannot pass without T-02's repoint.
- briefing: none this run. The dispatch asked for a short delta, not a CEO briefing; the standing
  one is notes/ship-review-2026-08-30-01.md and its task dispositions are now stale for T-13.

## Open Questions

- Q1: SUPERSEDED 2026-08-30. The 2026-08-29 ruling removed the decision-record task; the
  recording is back inside the feature as T-15, because DEC-188 already settled the form.
- Q2: RESOLVED 2026-08-30. The form is AMENDMENT, not an in-place strike — DEC-188 at
  DECISIONS.md:5945-5947 reserves striking for a flat contradiction and requires the operator's
  word first. All three of these are narrowings.
- Q4: RESOLVED by events, 2026-08-29. The INV-26 FEAT-40 violation is gone — FEAT-40 shipped.
- Q6: RESOLVED and APPLIED. INV-32 is scoped to non-terminal stations. Shipped history is not
  repaired.
- Q7: RESOLVED and APPLIED, folded into the same edit site as Q6.
- Q8: HARNESS DEFECT, unchanged and not re-triggered — nothing allocates run-dir slugs. The
  2026-08-29 collision stands recorded in runs/2026-08-29-01-product/OVERWRITTEN.md (rule 15).
- Q9: unchanged. The stale-pin task traces REQ-07 and pm calls the stretch knowingly.
- Q10: RECONFIRMED BY MEASUREMENT and now load-bearing. This machine's grep IGNORES `--exclude`
  and `--include`: SC-02's grep form returns 427 lines here where the python form returns 27 and
  reproduces the BRIEF's per-file split exactly. Every absence check in this plan that relies on
  an exclude is suspect for the same reason. Filed as #959.
- Q11: non-blocking HARNESS DEFECT, unchanged. The shell substitutes phantom pathnames for an
  unmatched glob member, so `grep -rn PAT dir/*/f.yaml ; test $? -eq 1` is unusable harness-wide.
- Q12: RESOLVED 2026-08-30. The `.harness/harness/docs/**` lanes row is LIVE, now via T-15, and
  BRIEF.md's lane paragraph is corrected: twelve tasks main-session-direct, one on the team lane.
- Q13: RESOLVED 2026-08-30. SC-02's own measurement is in T-07's `verify:` — the last task that
  removes a capitalised literal, so it can go green there. It was briefly on T-01, where it could
  never pass, and briefly on T-13, where striking the task would have deleted it silently.
- Q14: NEW, and it outranks the vocabulary work it was serving. A task whose `verify:` exercises
  its own module in isolation can be green while the project's state gate is face-down (#1033).
  Five tasks here are hardened, but nothing MECHANICAL requires a shape-changing task to carry a
  consumer test — the next plan gets this wrong the same way unless the qa gate learns the rule.
- Q15: NEW, non-blocking, carried as PB-07. Striking SC-05 removed the only criterion-level
  assertion that the plan.yaml write denial states the REASON and not merely the verb. The
  requirement now rests on T-09's verify and its intent prose, neither of which is a criterion.
- Q16: NEW, for the operator to file — I cannot reach `xd://report_issue`. My dispatch named
  HEAD as `92d279c` when it was `63b2382`, three commits later. Second occurrence of the pattern.
