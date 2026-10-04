# FEAT-68 — amendment 2 (DEC-174 main-session-direct): T-01 files to the touched set

Recorded with `plan-merge.py record-amendments` after validate c5 PASS, because CI's route gate (check-plan-routes, DEC-182) refused the merge: 162 machine-field lines against a budget of 50.

```yaml
VERDICT: PASS
DIGEST:
  amendments:
  - task: T-01
    field: files
    was:
    - .claude/skills/harness/bin/check-plan-routes.py#process_plan_yaml
    - .claude/skills/harness/bin/harness_boundary.py#classify
    - .claude/skills/harness/bin/board_lifecycle.py#_audit_findings
    - .claude/skills/harness/bin/layout_migration.py#scan
    - .claude/skills/harness/bin/check-domain.py#domain_check
    - &id001
      path: .claude/skills/harness/references/briefing.md
      quote: is the record; no rendered view is produced (FEAT-68).
    - &id002
      path: tests/integration/canonical-reader-classification.json
      quote: '".claude/skills/harness/bin/run-unit-tests.py",'
    - &id003
      path: tests/integration/test-gen-decisions-index.py
      quote: '# mechanism the other hyphenated-module tests use.'
    - &id004
      path: tests/unit/test-code-grade.py
      quote: '#!/usr/bin/env python3'
    - path: tests/unit/test-no-distribution.py
      quote: '#!/usr/bin/env python3'
    - path: tests/unit/test-factory-claim.py
      quote: '#!/usr/bin/env python3'
    - path: tests/unit/test-factory-config.py
      quote: '#!/usr/bin/env python3'
    - path: tests/unit/test-gh-cost-log.py
      quote: '#!/usr/bin/env python3'
    - path: tests/unit/test-suite-independence.py
      quote: '#!/usr/bin/env python3'
    - path: tests/unit/test-harness-boundary.py
      quote: '#!/usr/bin/env python3'
    - path: tests/unit/test-gh-board.py
      quote: '#!/usr/bin/env python3'
    - path: tests/unit/test-config-shape-matrix.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/check_state_support.py
      quote: '"""Fixture vocabulary shared by the test-check-state-*.py files.'
    - path: tests/integration/check_domain_support.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/test-anchor-directions.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/test-board-lifecycle.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/test-check-domain.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/test-check-domain-approval.py
      quote: '#!/usr/bin/env python3'
    - &id005
      path: tests/integration/test-check-domain-artifact.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/test-check-domain-claims.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/test-check-domain-grant.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/test-check-domain-post.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/test-check-domain-worktree-parity.py
      quote: '#!/usr/bin/env python3'
    - &id006
      path: tests/integration/test-check-domain-worktree.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/test-bash-write-guard.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/test-check-plan-routes.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/test-feature-worktree.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/test-harness-yaml.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/test-check-state-plans.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/test-validate-feature-json.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/test-check-state-entry.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/test-gh-sync-ship.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/test-factory-integration.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/test-layout-migration.py
      quote: '#!/usr/bin/env python3'
    - path: tests/integration/test-check-state-worktrees.py
      quote: '#!/usr/bin/env python3'
    - .harness/harness/features/BUG-1081-code-grade-enforcement/notes/ship-review-BUG-1081.html
    - .harness/harness/features/BUG-1286-test-tree-enforcement/notes/ship-review-2026-09-05-ship-final.html
    - .harness/harness/features/BUG-1286-test-tree-enforcement/notes/ship-review-2026-09-05-ship.html
    - .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/ship-review-2026-09-05-13-ship.html
    - .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/ship-review-2026-09-06-07-ship.html
    - .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/ship-review-2026-09-06-13-ship.html
    - .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/ship-review-2026-09-06-19-ship.html
    - .harness/harness/features/BUG-1302-suite-layout-fail-closed/notes/ship-review-2026-09-05-validate.html
    - .harness/harness/features/BUG-1303-plan-code-review-digest/notes/ship-review-2026-09-05-validate.html
    - .harness/harness/features/BUG-1304-worktree-relative-path-guard/notes/ship-review-2026-09-05-validate-final.html
    - .harness/harness/features/BUG-1305-run-state-clobber/notes/ship-review-2026-09-05-final.html
    - .harness/harness/features/BUG-1305-run-state-clobber/notes/ship-review-2026-09-05-validate-c2.html
    - .harness/harness/features/BUG-1308-expertise-replace-drop/notes/ship-review-2026-09-05-resume.html
    - .harness/harness/features/BUG-1309-mirror-build-entry/notes/ship-review-2026-09-08-resume.html
    - .harness/harness/features/BUG-1309-mirror-build-entry/notes/ship-review-2026-09-09-shipdecision.html
    - .harness/harness/features/BUG-148-gate-record-correction/notes/ship-review-2026-09-07-03-ship.html
    - .harness/harness/features/BUG-1480-handoff-note-checkout-root/notes/ship-review-2026-09-08-01-ship.html
    - .harness/harness/features/BUG-1563-inv35-multiline-quoted-scalar/notes/ship-review-validate-validator-final.html
    - .harness/harness/features/BUG-1699-lifecycle-cards/notes/ship-review-2026-09-16-05-simplify-eng.html
    - .harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/ship-review-validate-c6-validator.html
    - .harness/harness/features/BUG-201-depends-on-integrity/notes/ship-review-2026-09-07-ship.html
    - .harness/harness/features/BUG-285-canonical-reader/notes/ship-review-2026-09-14-t03-eng.html
    - .harness/harness/features/BUG-285-canonical-reader/notes/ship-review-2026-09-15-fix-c1-validator.html
    - .harness/harness/features/BUG-285-canonical-reader/notes/ship-review-2026-09-15-t03-eng.html
    - .harness/harness/features/BUG-285-canonical-reader/notes/ship-review-2026-09-15-t03-final-eng.html
    - .harness/harness/features/BUG-440-digest-verdict-reconciliation/notes/ship-review-plan-BUG-440.html
    - .harness/harness/features/FEAT-03-subissue-mirror/notes/ship-review-2026-07-31-16.html
    - .harness/harness/features/FEAT-04-decisions-index/notes/ship-review-2026-08-02-15-product.html
    - .harness/harness/features/FEAT-06-team-layer-inv6/notes/ship-review-FEAT-06.html
    - .harness/harness/features/FEAT-10-software-factory/notes/ship-review-build-2026-08-09.html
    - .harness/harness/features/FEAT-10-software-factory/notes/ship-review-ship-2026-08-09.html
    - .harness/harness/features/FEAT-104-strict-digest-schema/notes/ship-review-plan-signature-c1.html
    - .harness/harness/features/FEAT-104-strict-digest-schema/notes/ship-review-plan-signature-c2.html
    - .harness/harness/features/FEAT-104-strict-digest-schema/notes/ship-review-plan-signature-c3.html
    - .harness/harness/features/FEAT-104-strict-digest-schema/notes/ship-review-plan-signature-c4.html
    - .harness/harness/features/FEAT-104-strict-digest-schema/notes/ship-review-ship-c11.html
    - .harness/harness/features/FEAT-11-graphql-field-resolve/notes/ship-review-close.html
    - .harness/harness/features/FEAT-12-end-copy-distribution/notes/ship-review-2026-08-10-ship.html
    - .harness/harness/features/FEAT-13-single-issue-board-lookup/notes/ship-review-5e81612.html
    - .harness/harness/features/FEAT-14-feature-json-schema/notes/ship-review-2026-08-12-validate.html
    - .harness/harness/features/FEAT-20-migration-detector/notes/ship-review-2026-08-14.html
    - .harness/harness/features/FEAT-21-features-layout-migration/notes/ship-review-2026-08-15.html
    - .harness/harness/features/FEAT-22-docs-layout-migration/notes/ship-review-2026-08-16.html
    - .harness/harness/features/FEAT-23-ship-flow-fixes/notes/ship-review-2026-08-17-13.html
    - .harness/harness/features/FEAT-24-config-responsibility-split/notes/ship-review-2026-08-18-ship-01.html
    - .harness/harness/features/FEAT-24-config-responsibility-split/notes/ship-review-2026-08-19-ship-02.html
    - .harness/harness/features/FEAT-25-claim-feature-root/notes/ship-review-2026-08-19-ship.html
    - .harness/harness/features/FEAT-27-expertise-repository-tier/notes/ship-review-2026-08-19.html
    - .harness/harness/features/FEAT-29-graphql-budget/notes/ship-review-2026-08-19-01.html
    - .harness/harness/features/FEAT-29-graphql-budget/notes/ship-review-2026-08-19-02.html
    - .harness/harness/features/FEAT-29-graphql-budget/notes/ship-review-2026-08-19-03.html
    - .harness/harness/features/FEAT-29-graphql-budget/notes/ship-review-2026-08-20-final.html
    - .harness/harness/features/FEAT-30-worktree-per-feature/notes/ship-review-2026-08-20-01-build-eng.html
    - .harness/harness/features/FEAT-30-worktree-per-feature/notes/ship-review-2026-08-21-04-validator.html
    - .harness/harness/features/FEAT-31-orchestrator-context-watch/notes/ship-review-fix1.html
    - .harness/harness/features/FEAT-31-orchestrator-context-watch/notes/ship-review-ship1.html
    - .harness/harness/features/FEAT-32-concurrent-write-merge/notes/ship-review-2026-08-22-build-gate.html
    - .harness/harness/features/FEAT-34-worktree-act3-enforced/notes/ship-review-2026-08-24-validate.html
    - .harness/harness/features/FEAT-35-orchestrator-stop-and-wake/notes/ship-review-2026-08-24-validate.html
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/ship-review-c1.html
    - .harness/harness/features/FEAT-37-lead-stop-and-wake/notes/ship-review-2026-08-26-02-product.html
    - .harness/harness/features/FEAT-37-lead-stop-and-wake/notes/ship-review-2026-08-27-01.html
    - .harness/harness/features/FEAT-37-lead-stop-and-wake/notes/ship-review-2026-08-27-02.html
    - .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/ship-review-2026-08-29-16.html
    - .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/ship-review-2026-08-29-18.html
    - .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/ship-review-2026-08-30-fold-ship.html
    - .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/ship-review-2026-08-30-ship-close.html
    - .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/ship-review-2026-08-30-ship.html
    - .harness/harness/features/FEAT-41-one-station-vocabulary/notes/ship-review-2026-08-29-01.html
    - .harness/harness/features/FEAT-41-one-station-vocabulary/notes/ship-review-2026-08-30-01.html
    - .harness/harness/features/FEAT-42-one-root-resolver/notes/ship-review-2026-08-26-2-plan-product.html
    - .harness/harness/features/FEAT-42-one-root-resolver/notes/ship-review-2026-08-26-3-plan-product.html
    - .harness/harness/features/FEAT-42-one-root-resolver/notes/ship-review-2026-08-27-plan.html
    - .harness/harness/features/FEAT-42-one-root-resolver/notes/ship-review-2026-08-27-validate.html
    - .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-c27.html
    - .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-c28.html
    - .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-c29.html
    - .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-final.html
    - .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-ship-gate.html
    - .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-t06-eng.html
    - .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-validate-final-c24.html
    - .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-validate-final-c25.html
    - .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-validate-final-c26.html
    - .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-validate-final-panel-validator.html
    - .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-validate-fix-c13-simplify-eng.html
    - .harness/harness/features/FEAT-45-adversarial-plan-panel/notes/ship-review-2026-08-31.html
    - .harness/harness/features/FEAT-48-parallel-safe-suite/notes/ship-review-2026-09-02-c9.html
    - .harness/harness/features/FEAT-50-run-artifact-integrity/notes/ship-review-2026-09-01-ship.html
    - .harness/harness/features/FEAT-51-claude-code-lifecycle-safety/notes/ship-review-build-validate.html
    - .harness/harness/features/FEAT-51-claude-code-lifecycle-safety/notes/ship-review-plan-signature-c9.html
    - .harness/harness/features/FEAT-54-handoff-done-when/notes/ship-review-2026-09-02-t05t09-eng.html
    - .harness/harness/features/FEAT-54-handoff-done-when/notes/ship-review-2026-09-03-review-c6-validator.html
    - .harness/harness/features/FEAT-54-handoff-done-when/notes/ship-review-2026-09-04-ship.html
    - .harness/harness/features/FEAT-55-issue-types-created-work/notes/ship-review-2026-09-05-01-eng.html
    - .harness/harness/features/FEAT-55-issue-types-created-work/notes/ship-review-2026-09-05-02-eng.html
    - .harness/harness/features/FEAT-56-central-onboarding-model/notes/ship-review-2026-09-08-ship.html
    - .harness/harness/features/FEAT-56-central-onboarding-model/notes/ship-review-2026-09-09-ship.html
    - .harness/harness/features/FEAT-61-control-plane-consolidation/notes/ship-review-docs-product.html
    - .harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/ship-review-validate-c2-qa-validator.html
    - .harness/harness/features/FEAT-65-broad-exception-hooks/notes/ship-review-validate-c2-validator.html
    - .harness/harness/features/FEAT-66-complex-function-drivers/notes/ship-review-validate-c1-validator.html
    - .harness/harness/features/FEAT-67-complex-function-second-wave/notes/ship-review-validate-validator.html
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/red-first-receipts.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/clean-pin-byte-receipts.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/build-divergences.md
    - &id007
      path: .omp/commands/harness.md
      quote: '| `briefing: <path>` |'
    now:
    - .claude/skills/harness/bin/check-plan-routes.py#process_plan_yaml
    - .claude/skills/harness/bin/harness_boundary.py#classify
    - .claude/skills/harness/bin/board_lifecycle.py#_audit_findings
    - .claude/skills/harness/bin/layout_migration.py#scan
    - .claude/skills/harness/bin/check-domain.py#domain_check
    - *id001
    - *id002
    - *id003
    - *id004
    - *id005
    - *id006
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/red-first-receipts.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/clean-pin-byte-receipts.md
    - .harness/harness/features/FEAT-68-complex-function-third-wave/notes/build-divergences.md
    - *id007
    reason: 'DEC-182 budget (CI route gate, 162 > 50): the 102 deleted html anchors
      and the 30 untouched owning suites leave files; the deletion is asserted by
      verify, the suites are proof inputs named in the receipts.'
```
