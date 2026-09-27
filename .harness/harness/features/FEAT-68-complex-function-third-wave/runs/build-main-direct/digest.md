# FEAT-68 build — main-session-direct (DEC-174)

```yaml
VERDICT: PASS
DIGEST:
  headline: "process_plan_yaml, classify, _audit_findings, layout_migration.scan and domain_check are drivers over per-rule / per-phase functions at bar 4 (from grade 1: cyc 29/29/21/21/14), every function they leave behind is at bar 4, render-brief.py is gone with its test, its two invoking sentences, its classification row and 102 derived html files, and 56 of 57 owning suites are byte-identical to the baseline at a clean checkout of the implementation pin 9ab1813e — the 57th differs by the deleted test's discovery count."
  tests_added: 0
  suite: pass
  task: T-01
  task_verify: pass
  blocked_on: none
  open_questions: []
  files_touched:
    - .claude/skills/harness/bin/check-plan-routes.py
    - .claude/skills/harness/bin/harness_boundary.py
    - .claude/skills/harness/bin/board_lifecycle.py
    - .claude/skills/harness/bin/layout_migration.py
    - .claude/skills/harness/bin/check-domain.py
    - .claude/skills/harness/bin/render-brief.py
    - .claude/skills/harness/references/briefing.md
    - .omp/commands/harness.md
    - tests/unit/test-render-brief.py
    - tests/unit/test-code-grade.py
    - tests/integration/canonical-reader-classification.json
    - tests/integration/test-gen-decisions-index.py
    - tests/integration/test-check-domain-artifact.py
    - tests/integration/test-check-domain-worktree.py
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/build-divergences.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/red-first-receipts.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/clean-pin-byte-receipts.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/amendments-build-main-direct.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-68-complex-function-third-wave/notes/clean-pin-byte-receipts.md
```

One run covers T-01: `921bbf6e` (render-brief removal: script, test, briefing.md step, harness.md
note, classification row, 102 html), `ae8a3dcc` (scan), `a0bbafcf` (_audit_findings), `c7427067`
(process_plan_yaml), `df912ae6` (classify), `85451e4f` (domain_check), `cb7d56b2` (artifact mutant
repointed), `0c15bad6` (simplify pass: S1–S3, A1, A2 applied; S4 skipped; bug895 mutant
repointed), `9ab1813e` (stale `process_plan_yaml: 1` exemption removed — the bar-4 lock caught it
on the first full unit run) — the implementation pin — then `ae0b41d7` for the receipts and this
commit for the amendment and close. Runners at the pin: unit exit 0 (41 files), integration
exit 0 (70 files, `0 failure(s)`). Evidence: `notes/clean-pin-byte-receipts.md` (56/57 owning
suites identical at a clean detached checkout of the pin after the checkout-root, mkdtemp and
unittest-timing normalisations; the 57th is D-01; grade assertion green at the pin, red in the
baseline checkout on exactly the five targets), `notes/red-first-receipts.md`,
`notes/build-divergences.md` (D-01 the one output divergence; D-02..D-09 structural; simplify
record), `notes/amendments-build-main-direct.md` (T-01 `files` re-anchored to the post-image).

Things the reviewer should weigh:
1. **Two new normalisations (mkdtemp paths, unittest wall-clock)** beside the ruled checkout-root
   one — run-to-run nondeterminism present at the base too; raw bytes retained. Operator ruling
   requested 2026-09-27 and proceeded on the recommendation.
2. **D-01 `discovered 112 → 111`** — the only byte divergence, from the deletion.
3. **`_VERDICT_HANDLERS` table** in check-domain with `_deny_verdict` as the default: the inline
   chain's fall-through, now explicit.
4. **Two source-anchor mutants repointed** (artifact: feature-checkout guards; worktree: bug895
   block) — same proofs.

Residual (briefing rows, not applied): `_harness_advertise` single-use extraction (S4 — holds the
grade); the CANNOT_VERIFY reason chain lives in two functions with a documented order (A2).
