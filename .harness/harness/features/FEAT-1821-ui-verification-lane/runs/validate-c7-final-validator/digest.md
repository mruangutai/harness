# Final c7 validation — FEAT-1821-ui-verification-lane

The immutable c7 pin is terminally blocked: the real full-client gate falsely reports eleven missing specs because it recognizes literal Playwright titles but not the manifest-driven `test(check.spec_title, ...)` registrations used by eleven signed checks. The matrix otherwise passes, and Mode B confirms the committed FEAT-53 bundle is an honest fail-closed RED record.

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: "Final c7 is blocked: the real full-client gate adds 11 false structural refusals, while all scoped suites and the 41-image RED audit otherwise pass."
  team: validate
  steps_run: 3
  cycles_used: 0
  members:
    - { step: qa, persona: harness-qa, verdict: FAIL, headline: "Matrix commands pass, but the exact c7 gate reports 11 false missing-title reasons and fail-first proof remains incomplete.", files_touched: [".harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-qa-c7.md"] }
    - { step: code, persona: harness-code-reviewer, verdict: PASS, headline: "Both review stages pass its scoped checks: dependency pins, two-stage probes, component/UI counts, and ui_contract.py grades meet the contract.", files_touched: [".harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-code-reviewer-c7.md"] }
    - { step: ui, persona: harness-ui-reviewer, verdict: PASS, headline: "Mode B inspected 41/41 WebPs and confirmed an explicit fail-closed 18 failed, 4 setup-error, 1 passed RED bundle.", files_touched: [".harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-ui-reviewer-c7.md"] }
  must_fix:
    - "1. T-01/main-session-direct: make SC-11 full-client enforcement recognize the eleven manifest-driven Playwright registrations instead of falsely refusing the complete 23-test contract."
    - "2. T-01/main-session-direct: complete the pinned fail-first record for automated SC-02..SC-06 and SC-10..SC-11; present-green commands and partial receipts do not prove each contract could fail before its fix."
  files_touched:
    - ".harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-qa-c7.md"
    - ".harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-code-reviewer-c7.md"
    - ".harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-ui-reviewer-c7.md"
  branch: none
  open_questions: []
  escalations: []
  expertise_update: []
  adequacy_notes:
    - "All three readers bound their artifacts to review pin b8f96ab8e9c8168ed8389ccf4732a958e84828fd over baseline 711ba16227eda39ddb397ed574e4ca199fbc5984."
    - "Configured unit command `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit` exited 0 with 44 named tests, including 24/24 UI-contract cases."
    - "Configured component command `npm --prefix .claude/skills/harness/bin/dashboard/client run test` exited 0 with 5 files and 27/27 tests."
    - "Configured discovery `HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=qa-c7-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list` exited 0 with exactly 23 tests in 6 files."
    - "Reporter probe `node --experimental-strip-types --test .claude/skills/harness/bin/dashboard/client/ui-reporter.probe.spec.ts` exited 0 with 7/7 two-stage cases."
    - "The real gate against FEAT-53 results and served_bundle_commit 153909c71e8ca3f02be6fcbcfe48781718953b1d exited 1 with 18 honest product failures, 4 explicit inspection-setup refusals, and 11 additional false missing-title reasons; there were no other structural categories."
    - "The code reviewer measured 28 passing grade records over 711ba162..b8f96ab8; every ui_contract.py function is grade 4 or 5. Exact @testing-library/dom@10.4.1 and @stylexjs/stylex@0.19.1 pins were confirmed."
    - "The QA/code disagreement is resolved in QA's favor: QA exercised the actual c7 changed client paths, and ui_contract.py spec_titles() reads only literal _TITLE matches while eleven real specs register as test(check.spec_title, ...). The code PASS therefore does not clear SC-11."
    - "Mode B opened all 41 WebPs: 21 desktop-1440 and 20 desktop-1920. Four inspection rows retain setup errors and are refused as evidence; the bundle does not claim a green result or false visual completeness."
    - "No formatter, linter, unrelated project-wide suite, build, production edit, test edit, governance edit, or FEAT-53 repair was performed. No rework is authorized after this terminal finding."
  severity_max: high
  matrix_ok: false
  coverage_gaps:
    - "SC-11 full-client enforcement has no discriminating case for manifest-driven Playwright title registration."
    - "Pinned fail-first proof remains incomplete for SC-02..SC-06 and SC-10..SC-11."
  findings:
    - { id: V7-01, kind: substance, severity: high, status: must_fix, reporters: "qa", task: T-01, owner: main-session-direct, summary: "The full-client gate recognizes only literal test titles and falsely reports eleven signed manifest-driven specs absent.", evidence: "review-harness-qa-c7.md exact gate output; ui_contract.py:252-259 and :379-384; dashboard client specs use test(check.spec_title, ...)." }
    - { id: V7-02, kind: form, severity: med, status: must_fix, reporters: "qa", task: T-01, owner: main-session-direct, summary: "Automated-SC fail-first receipts remain incomplete.", evidence: "review-harness-qa-c7.md fail_first audit records gaps for SC-02..SC-06 and SC-10..SC-11." }
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/runs/validate-c7-final-validator/digest.md
```
