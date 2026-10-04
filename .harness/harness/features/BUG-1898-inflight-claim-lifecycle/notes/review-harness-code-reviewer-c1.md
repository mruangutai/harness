# Code review — BUG-1898 — c1

**BLUF.** Spec compliance passes and prior F-01 is resolved: the pinned validator strict-reads both the run's own claim and exact children before any write, refuses an unreadable registry for a dispatching parent's non-BLOCKED return at exit 2, releases nothing and preserves the unreadable bytes, while a leaf proceeds without writing. Code quality fails only because the changed production function `_registry_errand` grades 3 below the required grade-4 bar.

## Scope and evidence

- Reviewed canonical range `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e` and focused fix range `84c3a6cbe74c7c27337d4372a68be60fca834118..81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e`; no `[harness:human]` commits occur in scope.
- The only tracked dirt is the Harness-owned `feature.json`; pinned source and tests were read from `81dbd81d…`. `notes/cancelled-c1/**` was ignored.
- Per assignment, QA owns execution of T-03's exact verify command; this review used pinned code/test evidence and independently ran only `code-grade.py`.

## Stage 1 — spec compliance: PASS

- **F-01 disposed as resolved.** `_registry_errand` reads `live_claims(... agent_id=agent_id)` and then `_held_children(...)` inside one pre-write `try` (`validate-digest.py:2323-2329`). Either strict read raising `UnreadableRegistry`/`OSError` routes to `_unreadable_registry`; a lead/orchestrator non-BLOCKED return is refused at exit 2, while BLOCKED is allowed (`:2290-2303`). No release is reached on this path. A leaf is allowed through without a release attempt, so unreadable bytes remain untouched.
- The pinned integration case (`tests/integration/test-validate-digest.py:5850-5877`) distinguishes parent PASS refusal, BLOCKED escape, leaf passage, and exact byte preservation. Its subject is the real hook subprocess and its concrete mutant is the prior catch-and-pass behavior, which makes the parent PASS assertion fail.
- SC-06 is satisfied by the exact parent/child gate and targeted recovery commands (`validate-digest.py:2265-2287`), plus strict unreadable handling above. SC-08 inspection passes: DEC-204 at `DECISIONS.md:6383-6438` states run-start exact-id claiming, `pi.events` lifecycle settlement, exact/idempotent release, shared feature root, and held-child refusal, matching the pinned implementation. **DEC-204 is current truth.** SC-07 remains a pending operator-only live OMP merge gate, not a panel failure.
- No scope creep, omission, or decision mismatch found in the canonical diff.

## Stage 2 — code quality: FAIL

### F-02 — high · substance · T-03

`validate-digest.py:2306` — `_registry_errand` grades **3** for production (`cyclomatic 9`, `cognitive 9`, `ABC 20.2`; required bar 4). The function coordinates identity refusal, root resolution, two strict ownership reads, child refusal, own-claim absence, release, and release failure in one control surface. A future change to an unreadable or absent-claim branch can be placed after the release path and turn the intended pre-write refusal into a write-before-refusal regression—the exact lifecycle failure class this function guards. The mechanical gate classifies a below-bar production function as high; split the pre-write ownership decision from the release errand so the ordering invariant is structurally explicit.

No other substantive quality defect or focused-fix regression was found. The full grade run reports 121 passing changed functions and this one failing function; no grade-2 records.

## Principles applied

- **Model the Domain:** exact ownership, dispatch capability, unreadable state, child hold, and release are separate lifecycle states; F-02 reflects their concentration in one branching function.
- **Delete First:** the canonical diff retains no persona fallback, bulk cleanup, bare-name binding, or compatibility release path beside the exact-id lifecycle.

## Handoff

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Spec compliance passes with F-01 closed and DEC-204 current; code quality still fails on unchanged F-02."
  severity_max: high
  findings:
    - kind: substance
      scope: task
      severity: high
      reader: code-reviewer
      summary: "F-02 — validate-digest.py:2306: _registry_errand grades 3 below the production grade-4 bar."
      why: "The function concentrates pre-write ownership decisions and release behavior, allowing a future branch-order change to create a write-before-refusal lifecycle regression."
  must_fix:
    - "F-02 — split the pre-write ownership decision from the release errand so the ordering invariant is structurally explicit."
  code_grade: fail
  reviewed: "a4d72e7fc91d0cf7a568d9e2a5225465a422170e..81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e"
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/review-harness-code-reviewer-c1.md
```
