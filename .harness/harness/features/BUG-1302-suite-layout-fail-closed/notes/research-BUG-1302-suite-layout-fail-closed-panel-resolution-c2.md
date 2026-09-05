# Plan panel cycle 1 — resolution record — BUG-1302-suite-layout-fail-closed

**All four panel findings are resolved and transcribed; the plan is signature-ready.**
`check-plan-routes.py` exits 0 with five DEVIATION lines and zero VIOLATION lines. Task set
unchanged: T-01..T-05, every one `main-session-direct`. `approval.status: pending`, `status: plan`.
BRIEF still carries SC-01..SC-10 (10 criteria; none added, none removed).

## PANEL-1 — PF-fc35850348334fa161835c8a8d817636 — med — should-not-exist — resolved by T-05

Applied, by the **producible-state route**, not the escape hatch. The reader's and the lead's route
holds at source: `tree()` copies `run-unit-tests.sh` into the temp tree
(`tests/integration/test-run-unit-tests-layout.py:15-23`) and `run()` executes that copy (`:45-47`),
so the runner is mutable in place inside case 2. `run-unit-tests.sh` runs `set -uo pipefail` without
`-e` and performs its layout check at the `layout_out=` line (`:33`), after `cd "$_ROOT"` (`:9`), so a
`python3 tests/integration/test-integration.py` line inserted immediately before it prints
`PASS test-integration.py` on stdout and the refusal still exits 2 at `:41` with the MISCONFIGURED
line intact. Case 2's other two clauses therefore stay TRUE and only the sentinel property varies —
the narrow clause evaluates True (case 2 PASSES, misses the defect), the widened clause evaluates
False (case 2 FAILS). Exact discrimination; the clause-level fallback was not needed.

T-05's `verify:` is unchanged. Only the demonstrate-the-red paragraph was rewritten; the
record-it-in-notes sentence and its "one dated section per task" phrasing are intact.

## Red-demonstration rule applied to all five tasks — five judgements

The rule: hold every OTHER clause of the assertion TRUE and vary ONLY the property the new assertion
adds.

- **T-01 — AGREE with the lead.** Restoring the `(".", "..")` tuple raises the `".."` constant count
  from 1 to 2 and reddens only `b5 structural`. The B5 corpus check stays green because the restored
  element is unreachable behind the `".." in segments` guard — which is the point of the removal.
- **T-02 — AGREE.** Restoring the conjunct raises both AST counts to 2 and reddens `b4 structural`.
  The B4 corpus stays green (the conjunct is a tautology, so verdicts are unchanged). The `verify:`
  code_grade clause also reverts to grade 2 — a second detector of the *same* property, not a second
  property, so the demonstration is not over-determined.
- **T-03 — AGREE, and it is the exemplar.** Three demonstrations, each varying one clause of the
  three-clause condition while the others hold: the call-site fixture swap proves the branch routes,
  the phrase deletion isolates a message clause, the truthy-second-argument swap isolates the
  fail-closed clause.
- **T-04 — AGREE.** Reverting to the unguarded `read_text()` varies exactly the guarded-read
  property; the repository-wide caller check is untouched because real tracked sources are readable.
- **T-05 — DISAGREE with the plan as written (the panel is right).** Untracking the rogue falsifies
  `returncode == 2`, the MISCONFIGURED clause and the sentinel clause at once — integration case 5
  (`:125-134`) pins that state at returncode 0 with both sentinels present. Amended. **No second
  over-determined demonstration was found.**

## PANEL-2 — PF-1059ca60a52554428bd249d00f0d2fb4 — low — scope — resolved (BRIEF, no task)

**Option (a) taken:** SC-09 now names the build-time qa gate as its executor, once, after all five
tasks land and before the ship decision. Option (b) was rejected on the lead's hazard: SC-09's
named-check list spans BOTH files, T-05 declares `depends_on: []`, and a clause on T-04 could
therefore run before T-05's integration-file edit landed. Splitting the criterion across two owners
to work around that trades one ownerless half for two partial ones; SC-09 is a whole-feature
regression criterion, so one owner at the gate is the honest shape. No `depends_on` was changed and
no task was added — the plan's structure is untouched.

T-04's `verify:` was cross-checked against `plan.yaml` before this decision and matches the dispatch
string byte for byte.

## PANEL-3 — PF-1ada4741b4b00970cf6013518244f0f5 — low — should-not-exist — resolved (BRIEF, no task)

Recorded in `## Residual risk and its owner` beside the B-6 fixture-maintenance red: a legitimate
refactor changing the `any()` / `"*?["` / `".."` census reddens the suite under a misleading FAIL
name, and DEC-174 makes that red main-session-only to clear. No AST assertion was weakened; SC-02,
SC-04 and SC-06 are untouched.

## PANEL-4 — PF-00b01248362bad264b494db4f764ef99 — info — should-not-exist — resolved

The rediscovery of goal-check F-4 / Advisor R2 is transcribed rather than dropped, so a later reader
does not re-litigate D-02/D-03 as self-granted risk acceptance.

## Transcription note

`panel.transcription_rule` records that the digest writes finding 2's reader as the persona
`harness-code-reviewer`; it is transcribed as the reader id `scope` and the id was hashed over
`reader=scope`. No summary was reworded — a reworded summary would produce a different id and any
later operator ruling would read as stale.

## Open questions

- **Q1 (non-blocking):** the panel's own adequacy note stands unanswered — nobody confirmed SC-09's
  named-check list is COMPLETE at HEAD. Every anchor it lists exists; whether it omits a check worth
  protecting was assessed by no reader. Naming the qa gate as owner does not settle completeness.
