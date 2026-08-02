# FEAT-02 — STATE

## Feature
Fix VERDICT-shadowing in `.claude/skills/harness/bin/validate-digest.py`: `VERDICT:` is
matched first-match-wins, so a return that echoes the contract template before the real
return gets the echoed verdict routed. Found/reproduced in BUILD task 22 (ledger row,
`docs/harness/BUILD.md:207`).

## Mission
plan — run the plan-feature sequence, return artifacts pending user signature.

## Success criteria (binding; pm may refine wording, not weaken)
- SC-1: the echo repro is rejected or correctly routed; verified automated — repro fails post-fix.
- SC-2: all 36 existing suite cases (`bin/test-validate-digest.py`) still pass; verified automated.

## Constraints
- Files-only, stdlib-only (no PyYAML on this machine).

## Log
- seq-1: feature opened by orchestrator; plan-feature segment 1 (product-lead: pm) dispatched.
- seq-2: RECOVERY (new orchestrator). Prior dispatch interrupted; subtree ran on. Reconciled
  disk vs record: pm's plan-step artifacts exist and are sound (BRIEF.md, PLAN.md with D-01/D-02
  + T-01/T-02, notes/research-FEAT-02-verdict-shadowing.md), but run 2026-07-27-01-product
  state.yaml showed both steps pending — no checkpoints, design-pass never ran. Verified plan
  claims directly: suite exits 0, VALIDATE_DIGEST_BIN override at test-validate-digest.py:18.
  Decision: assess-not-redo; re-dispatch product-lead to resume the run.
- seq-3: run 2026-07-27-01-product complete, PASS. plan step recovered-as-assessed; design-pass
  self-scoped out (no end-user interaction, needs_prototype: false, no DESIGN.md — ruling at
  notes/mockups/design-pass-ruling.md). Cycles 2. Cost metered (approx, P-01).
- seq-4: segment 2 dispatched — eng-lead architecture review, run 2026-07-27-02-eng.
- seq-5: run 2026-07-27-02-eng complete, PASS. D-01 tail-anchor verified against all validate()
  code paths; edge cases (lowercase member verdict:, indented echoes, hook payload) hold.
  Advisories only, no must_fix: A-1 T-01 echoes must be schema-valid to go red pre-fix
  (self-correcting via T-01's RED verify gate); A-2 /tmp pre-fix binary fragility; A-3
  "worst" casing in case matchers. Artifact: runs/2026-07-27-02-eng/review-arch.md.
- seq-6: segment 3 (ui-reviewer contract check) SKIPPED per Expertise O-01 — design pass ruled
  no end-user interaction and no DESIGN.md exists; there is no contract to review.
- seq-7: plan-feature complete. BRIEF.md + PLAN.md approval sections pending; status set to
  awaiting_user. Next: user signs (one signature covers both), then build flow (T-01 → T-02).
- seq-8: ship flow (new orchestrator). Approvals confirmed on BRIEF/PLAN (2026-07-27).
- seq-9: run 2026-07-27-03-eng (build) complete, PASS, 1 cycle. T-01 red-first at 6546b1d,
  T-02 fix at d9b16e5; suite 40/40 green, pre-fix binary fails exactly the new cases.
  Orchestrator verified suite exit 0 directly. review_sha pinned d9b16e5.
- seq-10: run 2026-07-27-04-validator complete, PASS. qa gate met (bugfix matrix floor,
  pre-fix proof re-run); panel unanimous PASS at pinned SHA, severity_max low, must_fix
  empty; ui self-scoped out. F-1 (DIGEST-first returns now rejected) assessed
  non-gating, fails closed.
- seq-11: BUDGET BOUND HIT. Cost attribution ~$49 of max $40 (P-01 approximate; fable-tier
  runs ~$21 each). pm goal-check NOT dispatched per never-continue-past-a-bound. Status
  blocked; briefing at notes/ship-review-2026-07-27-04.md. Decisions for user: fund
  goal-check (~$5) or waive on qa evidence; merge sign-off; team-config ownership of
  .claude/skills/harness/bin/** (non-blocking).
