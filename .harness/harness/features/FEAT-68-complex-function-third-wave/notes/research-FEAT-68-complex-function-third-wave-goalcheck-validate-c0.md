# Goal-check — FEAT-68 T-01

**BLUF:** FAIL at review SHA `009b249b850abd7c40eb541e1ebfbf215ac2c52f`. SC-01 and SC-03 are met, but the signed operator proof is not: SC-02 uses two unapproved normalizations and a non-detached baseline-suite capture, SC-04 names a superseded implementation pin, and SC-05 remains partial until the required post-panel markdown-only validate output is created.

Scope checked: canonical range `e655f14a56a14bf1777cae55a19195c9af10505d..009b249b850abd7c40eb541e1ebfbf215ac2c52f`, amended T-01 files, and build-digest `files_touched`. The range contains 132 paths: the five Python targets, deleted renderer and renderer test, reference/classification/command/test-anchor edits, feature evidence, and exactly 102 deleted feature-history HTML derivatives.

## Done when — by perspective

- operator — **fail** — carrying SC-02 is not met because the comparison exceeds the signed root-only normalization and does not use detached-baseline suite output; carrying SC-04 is not met because the receipts disagree on the immutable pin; carrying SC-05 is partial pending the correctly sequenced markdown-only validate output. Direct evidence: `notes/clean-pin-byte-receipts.md:3-15,74-77,117-136`, `notes/red-first-receipts.md:3-13`, `notes/build-divergences.md:3-22`, and `notes/review-harness-code-reviewer-c0.md:7-24`.
- code maintainer — **pass** — carrying SC-01 is met by the discriminating baseline/current grade assertion, and carrying SC-03 is met by the pinned five-driver decomposition and complete removal/scope inspection. Direct evidence: `notes/review-harness-qa-c0.md:18-23`, `notes/review-harness-code-reviewer-c0.md:15,28-32`, and pinned source ranges `check-plan-routes.py:378-526`, `harness_boundary.py:849-1030`, `board_lifecycle.py:807-929`, `layout_migration.py:225-296`, `check-domain.py:855-1056`.

## Success criteria

- **SC-01 — met (automated).** QA reran the exact inline assertion: review SHA passed; detached baseline failed on exactly the five named targets, each grade 1 (`notes/review-harness-qa-c0.md:16,20,47-56`). The code reviewer independently reports all 34 selected current records at grade 4 or 5 (`notes/review-harness-code-reviewer-c0.md:26-28`).
- **SC-02 — not_met (automated evidence does not satisfy the signed outcome).** The receipt compares after checkout-root, `mkdtemp`, and unittest-time substitutions, although the approved criterion permits only checkout-root normalization (`notes/clean-pin-byte-receipts.md:11-15`; `notes/build-divergences.md:3-15`). It also says the baseline suite bytes came from the feature worktree, not the detached baseline checkout (`notes/clean-pin-byte-receipts.md:6-9`). D-01 `discovered 112 -> 111` is correctly isolated and ruled as the deleted test's expected consequence (`notes/build-divergences.md:17-22`), but that does not cure the proof mismatch.
- **SC-03 — met (inspection).** The complete pinned diff changes production Python only in the five named targets and deletes `render-brief.py`; the drivers preserve the ordered rule/phase shapes, `_VERDICT_HANDLERS` defaults unknown outcomes to exiting `_deny_verdict`, and the two source-anchor mutants are repointed to `_allow_verdict` and `_no_base_verdict`. The renderer test, briefing/reference/classification/command residue, named test comment, and exactly 102 HTML derivatives are removed; no other production Python is changed. Inspection pointers: `notes/review-harness-code-reviewer-c0.md:15,30-32`, `notes/build-divergences.md:24-53`, and the source ranges cited above.
- **SC-04 — not_met (inspection).** Git chronology places the three receipt files in `ae0b41d7`, after final implementation pin `9ab1813e`, so post-pin commit ordering is correct. However `red-first-receipts.md:3` identifies superseded `0c15bad6` as the implementation pin, while `clean-pin-byte-receipts.md:5` identifies `9ab1813e86067ca4a21a84f49364cf4f453055b4`; the former predates the required stale grade-exemption removal. The committed receipts therefore do not consistently name the actual immutable pin required by SC-04 (`notes/review-harness-code-reviewer-c0.md:17-22`).
- **SC-05 — partial (automated clauses pass; sequenced validate-output clause pending).** QA independently confirmed both matrix kinds green (unit: 41 files; integration: 70 files, 0 failures), baseline HTML count 102, remaining HTML count 0, and no renderer residue outside allowed historical locations (`notes/review-harness-qa-c0.md:9-16,20-24`). After a clean panel, the orchestrator must create `notes/ship-review-validate-validator.md` through the actual validate flow and verify that `notes/ship-review-validate-validator.html` does not exist. Its required pre-fan-in absence is sequencing, not a `must_fix` defect.

## Findings

### GC-01 — unapproved output normalizations

- kind: specification mismatch
- reader: harness-pm
- severity: high
- binding: T-01 / SC-02
- concrete failure scenario: a pin-only change to a diagnostic temporary path or unittest timing text is erased before comparison and reported identical, although every non-root byte difference must be ledgered under the signed criterion.

### GC-02 — baseline suites were not captured in the detached baseline checkout

- kind: evidence integrity
- reader: harness-pm
- severity: high
- binding: T-01 / SC-02
- concrete failure scenario: uncommitted feature-worktree state can influence baseline suite output, so the recorded comparison is not the reproducible clean-detached baseline-versus-pin experiment the operator approved.

### GC-03 — receipt names a superseded implementation pin

- kind: record contradiction
- reader: harness-pm
- severity: med
- binding: T-01 / SC-04
- concrete failure scenario: an auditor follows `0c15bad6` from the red-first receipt and evaluates a tree that still contains the stale grade-1 exemption, while the final immutable implementation pin is `9ab1813e`.

DEC-174 reserves any corrective work to the main session; this goal-check makes no fixes.
