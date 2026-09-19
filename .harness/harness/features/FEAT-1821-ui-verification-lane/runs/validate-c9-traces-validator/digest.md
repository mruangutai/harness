# Signed replayable-evidence amendment validation — c9

T-14 through T-18 are blocked at immutable pin `c5fab95615c035e97109f90bd4aa91fc2e4b78a5`: the committed bundle and all eight replay traces are complete and honestly RED, but two independent readers proved that T-14 accepts a corrupt non-ZIP trace when its first four bytes are `PK\x03\x04`.

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: "Amendment blocked: T-14 accepts a PK-prefix non-ZIP as replayable despite a structurally complete 22-RED/1-green committed bundle."
  team: validate
  steps_run: 3
  cycles_used: 0
  members:
    - { step: qa, persona: harness-qa, verdict: FAIL, headline: "Pinned bundle gate has only 18 predicate and 4 inspection-setup REDs, but the PK-prefix non-ZIP mutant passes T-14.", files_touched: [".harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-qa-c9.md"] }
    - { step: ui, persona: harness-ui-reviewer, verdict: PASS, headline: "All eight ZIPs were opened with Playwright Trace Viewer and carry distinct judged-step citations; all 41 WebPs were reviewed.", files_touched: [".harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-ui-reviewer-c9.md"] }
    - { step: code, persona: harness-code-reviewer, verdict: FAIL, headline: "Spec compliance fails because ui_contract.py validates only ZIP local-header magic, not a readable ZIP archive.", files_touched: [".harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-code-reviewer-c9.md"] }
  must_fix:
    - "T-14 / main-session-direct: make trace ZIP validation reject a file that starts PK\\x03\\x04 but is not a valid ZIP archive, and add the discriminating PK-prefix/non-ZIP mutant to tests/unit/test-ui-verification-contract.py."
  files_touched:
    - ".harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-qa-c9.md"
    - ".harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-ui-reviewer-c9.md"
    - ".harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-code-reviewer-c9.md"
  branch: none
  open_questions: []
  escalations: []
  expertise_update: []
  adequacy_notes:
    - "All readers bound their conclusions to c5fab95615c035e97109f90bd4aa91fc2e4b78a5; code review covered only 102cd2d7..c5fab95615c035e97109f90bd4aa91fc2e4b78a5 and preserved c7/c8 conclusions."
    - "QA's isolated-pin changed-client command was `python3 .claude/skills/harness/bin/ui_contract.py gate --design .harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md --results .harness/harness/features/FEAT-53-metrics-dashboard/runs/FEAT-1821-initial-red/ui/results.json --feature FEAT-53-metrics-dashboard --run-id FEAT-1821-initial-red --served-bundle-commit e94bc953d13e97c0443f1875f63884bf075143ee --repo-root . --client-package .claude/skills/harness/bin/dashboard/client --changed .claude/skills/harness/bin/dashboard/client/src/tiles.tsx`; exit 1 contained exactly 18 product-predicate failures and four inspection-setup failures, with zero structural, trace, title, provenance, screenshot, or accounting reasons."
    - "Scoped verification: T-14 exact verify passed 27/27 tests plus receipt and ignore probes; T-15 exact DESIGN/manifest/no-hardcode command passed; T-16 reporter probes passed 15/15; T-17 policy test passed 50 clause/mutant assertions. SC-04's named fail-first and live mutant refuse `toHaveScreenshot(` without any pixel-baseline Checks row and the positive case passes only after explicit opt-in."
    - "Pinned T-18 accounting is complete: 23 unique applicable records, statuses 18 failed + 4 evidence + 1 passed, 41 unique non-empty valid WebPs, exactly eight non-empty valid trace ZIPs, no missing ids, and served_bundle_commit e94bc953d13e97c0443f1875f63884bf075143ee."
    - "UI replay citations: C3-KEYBOARD desktop-1440 and desktop-1920 each judged `all C3 keyboard clauses execute before reporting product divergence`; TBL-DESKTOP desktop-1440 and desktop-1920 each judged `/kpi/7?window=all&repo=all: charts are hidden and adjacent tables expose identical non-colour values`; VIS-PROTOTYPE desktop-1440 and desktop-1920 each judged `every signed inspection setup and capture must execute`; A11Y-AXE desktop-1440 and desktop-1920 each judged `A11Y-AXE: every gap treatment exposes visible count or specific reason text`. The UI artifact records each distinct path, filmstrip, DOM snapshot, and assertion context."
    - "The deduplicated high finding is corroborated independently: `.claude/skills/harness/bin/ui_contract.py:261-265` returns true on the four-byte prefix alone, while `zipfile.is_zipfile` returns false for the same fabricated artifact; the existing non-ZIP test at `tests/unit/test-ui-verification-contract.py:357-359` uses WebP bytes and misses this mutant."
    - "An initial concurrent signed-lane replay dirtied the assigned worktree's cross-feature results.json and hit the shared port; that environmental output was excluded from every pin conclusion. The orchestrator was notified that the main-session-direct owner must restore the working evidence from the immutable pin before remediation."
  severity_max: high
  matrix_ok: false
  coverage_gaps:
    - "T-14 lacks a PK-local-header-prefix/non-ZIP mutant, so its current unit suite cannot distinguish signature bytes from a structurally valid replayable ZIP."
  findings:
    - { id: V9-01, kind: substance, severity: high, status: must_fix, reporters: "qa,code-reviewer", task: T-14, owner: main-session-direct, summary: "Trace validation accepts a corrupt non-ZIP beginning PK\\x03\\x04.", evidence: "ui_contract.py:261-265 and both readers' exact-pin probe: contract_accepts=True, zipfile_accepts=False." }
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/runs/validate-c9-traces-validator/digest.md
```
