# QA gate — FEAT-2037 T-01, cycle 0 (gate-only, receipts graded, nothing run)

## BLUF
Matrix floor met: T-01 is `change_type: docs`, `.harness/harness.json` `test_matrix.docs.always == []`, so no required kind exists and `matrix_ok: true`. The T-01 static/unit/integration receipts are green (integration only after a preserved first FAIL, see below). The feature has **no `verify: automated` SC** (SC-01..03 `uat`, SC-04 `inspection`), so fail-first evidence has nothing to apply to (SC-17 vacuous). The digest validator (`validate-digest.py:1506-1512`) rejects `PASS + matrix_ok:true + fail_first:[]` with no carve-out for zero automated SCs; I will not fabricate fail-first evidence, so the verdict is ESCALATE (harness contract gap), not PASS and not FAIL (no gate failed).

## Phase 1 (source-blind, BRIEF + plan only)
Expected coverage from SC text alone: SC-01/02/03 need observed-conduct UAT (27 assertions: U-01 6, U-02 12, U-03 2, U-04 7 — counted in `notes/uat-product-document-guidance-c0.md`); SC-04 needs independent inspection at `review_sha`; structural checks are supplemental. No automated test is expected by BRIEF (DEC-70).

## Matrix / kinds (configured, reported honestly)
- `docs.always = []` → no required kind. Configured kinds: unit active (`run-unit-tests.py --kind unit`), integration active, functional/eval excluded (DEC-187), component/ui/typecheck unresolved null, locally_run probes (omp_session_accessor, handoff_comprehension, issue_types_live, inflight_claim_lifecycle_live, digest_object_contract_live) — none required for docs.
- Supplemental receipts (`notes/verification-main-c0.md`, `notes/receipt-main-session-T-01-c0.md`), read not rerun:
  - check-skill-weight + check-skill-refs + check-instruction-paths: exit 0; 55,847 words/16 roles, refs ok 73 files, 68 instruction files 0 violations; no budget NOTE.
  - unit: exit 0, 46 files (artifact://101). Earlier initial-tree unit run FAILED on test-check-skill-refs.py bare product-doc refs (artifact://94); corrected by `<product-checkout>` notation, no checker change.
  - integration: initial tree PASS 73 files (artifact://95); updated tree first run **FAIL** exit 1, only test-check-plan-routes.py, 6 failures, stale owner manifest (artifact://102); after separately operator-authorized owner `git merge --ff-only origin/main` (652e70d4→f35d3a72) re-run **PASS** exit 0, 73 files (artifact://107). Failure history retained; the green was produced by the owner's own rerun, not asserted here (O-01).
  - Caveat: run-unit-tests PASS lines are per-script, not case counts (repo G-04). These runs are not required kinds and not proof of any behavioural SC.
- Matrix kinds array is therefore `[]` of required kinds; the digest's `kinds` carries unit/integration as supplemental `satisfied` entries.

## SC evidence
- SC-01, SC-02, SC-03: operator-only UAT, **NOT RUN** (all 27 assertions `result: NOT RUN YET`, status draft, review_sha unpinned). No test evidence; not claimed.
- SC-04: pending independent reviewer inspection at `review_sha`. My grep (not a review) sees product guidance present in all four paths (harness-principles SKILL.md:17-24, harness-spec-driven SKILL.md:48-51, harness-zero-micro-management SKILL.md:29-32, SPEC.md:1122-1131). Not a sign-off.
- `sc_evidence` in digest: `[]` — no automated SC.

## fail_first
`[]`. No `verify: automated` SC exists, so SC-17 has nothing to apply to. Not evidence of a missing red run.

## Coverage gaps (reported, not must-fix, no kind invented)
1. No runner covers the four Markdown playbook edits' behavior; conduct is only graded by the pending UAT.
2. SC-01..03 UAT NOT RUN (27 assertions); operator alone records passed.
3. SC-04 independent review at `review_sha` pending; no `review_sha` pinned.
4. Updated-skill delivery to governed subagents unproven (live preflight evidence pending).

## Open questions
- OQ-1 (harness contract, non-blocking for feature): `validate-digest.py:1506-1512` has no path for a QA PASS on a feature with zero `verify: automated` SCs (`fail_first: []` + `matrix_ok: true` is refused; `matrix_ok: n/a` with PASS is refused). Needs a ruling: carve-out for zero automated SCs, or orchestrator accepts this ESCALATE as the gate result.

## Principles applied
None cited (no craft leaf read this run).
