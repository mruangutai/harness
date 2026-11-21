# Handoff — FEAT-2225-member-expertise-writes, validate c1 → fix (main-session-direct segment) → validate c2 — written at 3ab9f467 + bookkeeping, seq-5

## Next

The validate panel over review_sha 130592528844321c27fbb628fdc05f6f17f86d0d returned three substance must-fixes (runs/r-20261121-6-validate-validator/digest.md). F1 and F3 cite only T-04 (main-session-direct, DEC-174); F2 cites T-01 (harness-backend-dev) and T-04 in one contract. No squad `fix` run can own F1/F3, so the main session executes ONE fix segment inside the worktree, then re-delegates the orchestrator for re-pin + `gh-sync.py status review` + ONE `validate` c2 dispatch (`run-start --regate`, rework round 1 of 2 / 90 min, 13 min spent). Station is `building` (gh-sync written at this seam).

Fix segment, in dependency order, each with its verify:

1. **F1 / T-04** — `.omp/extensions/harness-hooks.ts` (`applyCallerRefusal`, `currentMission` from the prose marker at :1005/:1253/:1325) and `.claude/skills/harness/bin/dispatch-guard.py` (`_distill_preflight` returns when `_bound_distill_run()` is None): require REGISTERED distill authority before `member-ops` runs; refuse a `HARNESS-MISSION: distill` start with no bound `distill-*` run, while preserving the orchestrator's own distill authority (validate-digest's `_require_feature_distill` derives it from the feature's registered distill run, not a lead run). Regressions: `tests/unit/omp-hooks.test.ts` (marker under a non-distill run → tool refused) and `tests/integration/test-dispatch-guard.py` (marker with no bound distill run → exit 2). Verify: `bun test tests/unit/omp-hooks.test.ts && python3 tests/integration/test-dispatch-guard.py`.
2. **F2 / T-01 + T-04** — `.claude/skills/harness/bin/expertise-merge.py` `verify-receipt` (:1462-1470, :1540-1552 compare active-op keys only) and `.claude/skills/harness/bin/validate-digest.py` (:2250-2269 trusts exit 0): verify the COMPLETE resulting destination against the authorized active history (receipted add P-01 + unreceipted deletion of G-01 must refuse at live yield and durable close), preserving ordered/superseded batches. Regression in `tests/integration/test-expertise-merge.py` and `tests/integration/test-validate-digest.py`. Verify: `python3 tests/unit/test-expertise-ops.py && python3 tests/integration/test-expertise-merge.py && python3 tests/integration/test-validate-digest.py`.
3. **F3 / T-04** — `tests/integration/test-member-expertise.py` (:162-215 calls the core CLI directly) and `tests/unit/omp-hooks.test.ts` (:1840-1984 canned receipts): representative real host→core application/receipt coverage for craft and repository add/replace/drop, keeping the all-16 configuration assertions. Verify: T-04 verify verbatim, `python3 tests/unit/test-digest-schemas.py && bun test tests/unit/omp-hooks.test.ts && python3 tests/integration/test-member-expertise.py`.

After the segment: `python3 .claude/skills/harness/bin/code-grade.py --base 594af2a8 --head HEAD` must stay rc 0 (new functions at bar); run-unit-tests unit + integration; check-plan-routes, --canonical-reader-audit, check-instruction-paths, check-state.

## Trust

- SIMPLIFY r-20261121-5-simplify-eng: all 24 below-bar T-01 functions lifted at f06b2e57, assertions 119→119 / 255→255; orchestrator re-ran code-grade (rc 0, 414 PASS) and six gates rc 0 — runs/r-20261121-5-simplify-eng/digest.md — verified-at f06b2e57
- Three SIMPLIFY readers (simplification, efficiency, altitude) returned prose receipts only; the host yield gate refused their structured returns twice each — notes/receipt-harness-{data-engineer,dev-ops,ai-dev}-r-20261121-5-simplify-eng-*.md — source (host defect, reported to xd://report_issue by the lead)
- Validate c1: matrix observed green by qa (unit 61 files/1129 PASS, integration 88 files/2922 PASS, env -u HARNESS_AGENT_TYPE) but qa's return was refused by the host yield gate, so the run closed BLOCKED; findings F1–F3 stand — runs/r-20261121-6-validate-validator/digest.md, notes/review-harness-qa-c1.md — source
- F1 premise re-read by the orchestrator at the pin: dispatch-guard.py `_distill_preflight` returns on no bound run; harness-hooks.ts:1151 gates on `currentMission` set from the marker — verified-at 13059252
- Goal-check c1: SC-01 partial, SC-03 not_met, SC-02/04/05/06 met — notes/research-FEAT-2225-member-expertise-writes-goalcheck-validate-c1.md — source
- Credentialled probe cited, not rerun — notes/probe-handoff-comprehension-2026-11-21.md — source

## Dead ends

- Wrapped `{data:{VERDICT,DIGEST,artifact}}` yields from read-only members are refused by the host gate in this session; a form-only re-prompt does not recover them. Do not spend a third re-prompt — harness defect, routed up in the orchestrator's open_questions — source
- Spelling a feature-artifact path relative, or through `$VAR`, in a bash commit line is refused by bash-write-guard; absolute paths pass — source

## Working set

- .harness/harness/features/FEAT-2225-member-expertise-writes/feature.json (review_sha 13059252; stale once the fix lands — re-pin)
- .harness/harness/features/FEAT-2225-member-expertise-writes/plan.yaml (status building)
- .harness/harness/features/FEAT-2225-member-expertise-writes/runs/r-20261121-6-validate-validator/digest.md
- notes/review-harness-code-reviewer-c1.md, notes/review-harness-security-reviewer-c1.md

## Done when

Scope: F1–F3 landed in the worktree with their regressions red-first, every verify above rc 0, then validate c2 PASS over a fresh pin
Authority: plan-task:T-01.verify
Authority: plan-task:T-04.verify
Authority: brief-perspective:.harness/harness/features/FEAT-2225-member-expertise-writes/BRIEF.md#orchestrator
