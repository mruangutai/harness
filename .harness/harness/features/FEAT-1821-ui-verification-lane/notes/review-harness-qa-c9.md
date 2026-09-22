# QA gate — c9 replayable-traces amendment

**BLUF: FAIL at immutable pin `c5fab95615c035e97109f90bd4aa91fc2e4b78a5`.** The committed T-18 bundle itself is structurally complete and its changed-client gate produces only the allowed 18 predicate REDs plus four inspection-setup REDs. However, T-14 accepts a non-ZIP file that merely starts `PK\x03\x04`; therefore malformed replay traces can pass the stated non-ZIP refusal contract.

## Pin and scoped proof

Before validation, the assigned worktree returned `c5fab95615c035e97109f90bd4aa91fc2e4b78a5` from `git rev-parse HEAD` and `git cat-file -e c5fab95615c035e97109f90bd4aa91fc2e4b78a5^{commit}` passed. To avoid reader-dirtied evidence, all pin-sensitive bundle validation below ran in isolated detached worktree `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/qa-c9-pin-c5` at that exact SHA.

Phase 1 (BRIEF and approved plan only) expects parser/pixel-opt-in, trace validity, reporter, Mode-B trace-replay, pair/title/accounting, and complete intentional-RED evidence. Matrix aggregate: T-14/T-17 logic requires unit; T-16/T-18 frontend requires unit, component, and ui. Executed signed scoped proof:

- T-14 exact parser/receipt/ignore command: PASS; 27/27 tests.
- T-15 exact DESIGN/manifest/hardcode command: PASS; ordered traces are `C3-KEYBOARD,TBL-DESKTOP,VIS-PROTOTYPE,A11Y-AXE`.
- T-16 exact probe command: PASS; 15/15 TAP tests.
- T-17 exact policy command: PASS; 50 policy/mutant assertions.
- T-18 stored signed receipt records its required lane command as nonzero with 22 RED / 1 green; immutable results accounting independently confirms the recorded state below. No UI lane was rerun during corrected immutable validation.

## Immutable bundle and gate

The pin object `results.json` declares `harness-ui-results/1`, feature `FEAT-53-metrics-dashboard`, run `FEAT-1821-initial-red`, served bundle `e94bc953d13e97c0443f1875f63884bf075143ee`; it has 23 unique applicable/observed pairs out of 23, no missing ids, 41 unique referenced WebPs, eight unique trace paths, and statuses `passed=1`, `failed=18`, `evidence=4` (22 RED / 1 green). Every referenced WebP exists, is non-empty, and has `RIFF....WEBP` magic; all eight prescribed traces exist, are non-empty, and `zipfile.is_zipfile` accepts them.

In the isolated pin tree, the required real gate command was:

```sh
python3 .claude/skills/harness/bin/ui_contract.py gate --design .harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md --results .harness/harness/features/FEAT-53-metrics-dashboard/runs/FEAT-1821-initial-red/ui/results.json --feature FEAT-53-metrics-dashboard --run-id FEAT-1821-initial-red --served-bundle-commit e94bc953d13e97c0443f1875f63884bf075143ee --repo-root . --client-package .claude/skills/harness/bin/dashboard/client --changed .claude/skills/harness/bin/dashboard/client/src/tiles.tsx
```

It exited `1` with exactly the committed 18 product-predicate reasons and four `inspection setup failed` reasons (`VIS-DENSITY` and `VIS-PROTOTYPE` for both projects). It emitted **zero** structural, trace-contract, title, provenance, screenshot, accounting, or still-only grading reasons.

## Finding

- **kind:** substance; **severity:** high; **task:** T-14; **owner:** main-session-direct. **Failure scenario:** a trace field points to a non-empty file beginning `PK\x03\x04` but containing no ZIP archive. `_is_zip` returns true and the gate accepts that trace, so a reviewer later cannot replay it despite T-14 requiring rejection of non-ZIP traces. **Evidence:** `ui_contract.py:261-265` checks only the four-byte prefix; isolated executable probe printed `contract_accepts=True zipfile_accepts=False`. The only named non-ZIP unit mutant writes WebP bytes (`test-ui-verification-contract.py:357-359`), so it does not discriminate the PK-prefix mutant.

## Fail-first audit

- SC-01: `receipt-harness-frontend-dev-T-03-c0.md:5` records pre-lane `Missing script: test:ui`.
- SC-02: `receipt-main-direct-T-14-c0.md:7-11,25` records trace-contract red pre-fix.
- SC-03: `receipt-main-direct-T-18-c0.md:3-5` records the intentional RED bundle.
- SC-04: `receipt-main-direct-T-14-c0.md:7-11,22-23` records the named `toHaveScreenshot(` mutant red and explicit pixel-baseline opt-in green.
- SC-05: `receipt-main-direct-T-14-c0.md:7,24` records Traces-table red cases.
- SC-06: `receipt-main-direct-T-14-c0.md:9,25` records replayable-results red cases.
- SC-10: `receipt-main-direct-T-01-c8.md:14-23` records runner/contract mutations red.
- SC-11: `receipt-main-direct-T-01-c8.md:15-23` records client complete-title mutation red.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "The immutable T-18 bundle and changed-client gate are clean apart from allowed REDs, but T-14 accepts a PK-prefix non-ZIP trace."
  suite: fail
  failures: 1
  matrix_ok: false
  kinds:
    - { kind: unit, state: fail, cmd: "python3 tests/unit/test-ui-verification-contract.py", named_tests: 27 }
    - { kind: component, state: satisfied, cmd: "node --experimental-strip-types --test .claude/skills/harness/bin/dashboard/client/ui-reporter.probe.spec.ts", named_tests: 15 }
    - { kind: ui, state: satisfied, cmd: "ui_contract.py gate ... --changed .claude/skills/harness/bin/dashboard/client/src/tiles.tsx", named_tests: 23 }
  coverage_gaps: ["T-14 has no PK-prefix/non-ZIP mutant; trace validity is only a magic-prefix check."]
  sc_evidence:
    - { id: SC-04, test: "tests/unit/test-ui-verification-contract.py:366-389" }
    - { id: SC-05, test: "tests/unit/test-ui-verification-contract.py:182-205" }
    - { id: SC-06, test: "tests/unit/test-ui-verification-contract.py:326-364" }
    - { id: SC-08, test: "tests/unit/test-ui-reviewer-policy.py" }
  fail_first:
    - { sc: SC-01, evidence: "notes/receipt-harness-frontend-dev-T-03-c0.md:5" }
    - { sc: SC-02, evidence: "notes/receipt-main-direct-T-14-c0.md:7-11" }
    - { sc: SC-03, evidence: "notes/receipt-main-direct-T-18-c0.md:3-5" }
    - { sc: SC-04, evidence: "notes/receipt-main-direct-T-14-c0.md:7-11,22-23" }
    - { sc: SC-05, evidence: "notes/receipt-main-direct-T-14-c0.md:7,24" }
    - { sc: SC-06, evidence: "notes/receipt-main-direct-T-14-c0.md:9,25" }
    - { sc: SC-10, evidence: "notes/receipt-main-direct-T-01-c8.md:14-23" }
    - { sc: SC-11, evidence: "notes/receipt-main-direct-T-01-c8.md:15-23" }
  findings:
    - { kind: substance, severity: high, task: T-14, owner: main-session-direct, scenario: "PK-prefix non-ZIP trace passes gate.", evidence: "ui_contract.py:261-265; isolated probe" }
  open_questions: []
  files_touched: [".harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-qa-c9.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-qa-c9.md
```
