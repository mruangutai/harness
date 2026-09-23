# FEAT-64 goal check — validate c2

## Scope and evidence basis

Verdict: **PASS** at immutable review SHA `721b690e3578fbaba2b88d93774667d94ac4d8a3` against baseline `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983`.

I inspected the complete 67-object baseline-to-pin union as Git objects: 18 production Python files, 20 test files, and 29 signed/evidence/state records. The production and test objects are byte-identical to validation-c1; the review-pin delta after c1 is evidence/state only. This permits the green c1 QA matrix (`notes/review-harness-qa-c1.md:67-73`, 42 unit files and 69 integration files) to remain evidence for the unchanged executable objects. Independently, the c2 code reviewer ran all three signed task chains from an isolated pinned tree (`notes/review-harness-code-reviewer-c2.md:22-24`). No success criterion uses UAT.

The evidence union is coherent: `notes/red-first-receipts.md` retains discriminating pre-fix failures and final results; `notes/byte-evidence.md` records all 27 baseline/final stream and exit comparisons; `notes/build-divergences.md` rules every deliberate difference; and the tracked build/validation digests preserve the build and prior-reader record.

## Prior-item regrade and current-reader disposition

- **GC-64-04 — kind: substance; status: CLOSED.** Independent object diff from `a4a3d7f8` to evidence head `220feabb` returns exactly three governed YAML additions: `plan.yaml`, `runs/validate-validator/state.yaml`, and `runs/validate-c1-validator/state.yaml`. An independent `git ls-tree` count using the corpus test's `features/*/notes/**` exclusion returns baseline `101` total / `.harness=97` and evidence head `104` total / `.harness=100` (teams remain `4`). Those values and contributors now match `notes/build-divergences.md` §A4 and `notes/byte-evidence.md:343-349`; the c1 contradiction is gone.
- **QA-64-01 — kind: form; status: CLOSED.** `git cat-file -e` succeeds for `721b690e:.harness/harness/features/FEAT-64-broad-exception-libs-tools/runs/build-main-direct/digest.md`, and `git ls-tree` returns its tracked blob. The required build digest is inspectable at the review pin.
- **QA-64-02 — kind: form; status: NON-BLOCKING FOR THE FEATURE GOAL.** The c2 QA reader correctly declined to execute commands in the mutable supplied checkout because its checked-out `HEAD` is not the review pin (`notes/review-harness-qa-c2.md:3-9`). That runner-provisioning issue does not remove the c1 QA evidence for byte-identical production/tests, and the c2 code reviewer additionally executed all signed chains from an isolated pinned tree. Recommendation: provision QA itself a clean detached pin in future cycles; no product or evidence change is warranted here.

## Perspective grades

| Perspective | Grade | Discharge |
|---|---|---|
| operator | met | The exact-output ledger and unchanged-object QA evidence discharge SC-01; pinned hook/caller inspection discharges SC-04. |
| code maintainer | met | The census, typed library/tool boundary cases, defect-escape cases, process-control cases, and mutants discharge SC-02, SC-03, and SC-07. |
| reader | met | The comment/bootstrap inspection and the single-parse route and handoff tests discharge SC-05, SC-06, and SC-08. |

## Dismissed and superseded items

- CR-64-01/GC-64-03 remains resolved: `board_lifecycle.py` is baseline-identical, ledger B2 records that fact, and defect #1897 owns the deferred constructor repair.
- GC-64-01's earlier category-only evidence gap remains superseded by per-suite raw/normalised digests, exact differing lines, and the complete divergence ledger; its narrower successor GC-64-04 is closed above.
- GC-64-02 remains resolved by the re-signed separation of library/tool and route/handoff evidence kinds in BRIEF/plan.
- The future `hook_guard` fail-open/disclosure concern is not active at this pin because the function has no caller; SC-04 expressly forbids wiring it here.
- The propagated `board_lifecycle` TypeError remains the signed exposure of #1897 rather than FEAT-64 scope, `FACTORY_GH` executable selection predates this diff and still uses list argv, and the changed line-oriented CLI output creates no rendered UI surface.

```yaml
VERDICT: PASS
DIGEST:
  headline: "All three perspectives and SC-01 through SC-08 are met at the immutable pin; GC-64-04 and QA-64-01 are closed."
  feasibility: clear
  surface: L
  flags: [exception-boundaries, evidence, validation]
  recommend: proceed
  tasks: 3
  decisions: 4
  needs_approval: false
  risk: low
  sc_status:
    - id: SC-01
      verdict: met
      method: automated
      evidence: "T-01/T-02/T-03 trace: notes/review-harness-qa-c1.md:67-73; notes/byte-evidence.md (27 stream/exit comparisons); notes/build-divergences.md A1-A5/B1-B7, with corrected A4 independently matching 104/100 and exactly three YAML additions."
    - id: SC-02
      verdict: met
      method: automated
      evidence: "T-01/T-02/T-03 trace: tests/unit/test-broad-catch-census.py:83-96 and tests/integration/test-check-plan-routes.py:2912-2922 cover zero ceilings, exactly two harness_boundary catches, increase/third-catch mutants, and clean reduction; notes/red-first-receipts.md §2 retains REDs."
    - id: SC-03
      verdict: met
      method: automated
      evidence: "T-01/T-02/T-03 trace: tests/unit/test-harness-boundary.py:1004-1023 and tests/unit/test-handoff-done-when.py:462-508 cover typed library boundaries, main-result preservation, Exception-only hook handling, process-control escape, and unexpected-defect escape."
    - id: SC-04
      verdict: met
      method: inspection
      evidence: "T-03 trace: pinned diff has no changes under .claude/hooks/** or .omp/extensions/harness-hooks.ts; full production diff and notes/review-harness-code-reviewer-c2.md:7-10 confirm hook_guard remains unwired and existing hook ceilings/verdicts remain untouched."
    - id: SC-05
      verdict: met
      method: inspection
      evidence: "T-01/T-02/T-03 trace: full pinned bin/tests patch inspection plus notes/build-divergences.md:43-48 confirms silence rationales moved byte-for-byte, FEAT-64 explanations are separate, and the run-unit-tests DEC-234 prologue/reciprocal comment are unchanged."
    - id: SC-06
      verdict: met
      method: automated
      evidence: "T-01/T-03 trace: tests/integration/test-check-plan-routes.py:2807-2960 proves one plan load for live and shipped discovery while retaining typed manifest failure behavior; notes/red-first-receipts.md §2 preserves the two-load RED."
    - id: SC-07
      verdict: met
      method: automated
      evidence: "T-02/T-03 trace: tests/integration/test-board-station.py:270-293, test-check-omp-port.py:279-304, test-post-merge-sweep.py:1041-1065, test-run-unit-tests-layout.py:142-164, test-upgrade-config.py:112-137, and test-gh-sync-ship.py:245-268 exercise the typed tool boundaries and unrelated-defect escape."
    - id: SC-08
      verdict: met
      method: automated
      evidence: "T-01/T-03 trace: tests/unit/test-handoff-done-when.py:462-501 proves one authoritative plan parse, typed indeterminate failures, and unrelated RuntimeError escape; notes/red-first-receipts.md §2 retains the duplicate-parse RED."
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/research-FEAT-64-broad-exception-libs-tools-goalcheck-validate-c2.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-64-broad-exception-libs-tools/.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/research-FEAT-64-broad-exception-libs-tools-goalcheck-validate-c2.md
```
