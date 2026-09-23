# FEAT-64 goal-check — validate c0

Review pin: `dc71e09e0647882c63f66ab0b6d6048bc6dd2688`
Baseline: `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983`
Reader: `harness-pm`
Artifact: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-64-broad-exception-libs-tools/.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/research-FEAT-64-broad-exception-libs-tools-goalcheck-validate-c0.md`

## Perspective grades

- **operator — partial** — Carrying criteria: SC-01, SC-04. SC-04 is discharged: the pinned baseline-to-review changed-file set contains none of the eleven hook entry scripts or `.omp/extensions/harness-hooks.ts`; pinned `git grep` finds `hook_guard` only at `.claude/skills/harness/bin/harness_boundary.py:442` plus its census comment, and `tests/unit/test-harness-boundary.py:1022-1023` explicitly checks that no hook calls it. SC-01 is not fully discharged: `notes/red-first-receipts.md:7-41` records all 27 baseline/head exit and stream digests and `notes/build-divergences.md:13-31` supplies rulings, but A1 and A5 give categories/placeholders rather than the signed criterion's exact old and new bytes; B2 also changes an unplanned production file without an approved task or operator ruling.
- **code maintainer — partial** — Carrying criteria: SC-02, SC-03. SC-02 is discharged by the pinned two catches at `.claude/skills/harness/bin/harness_boundary.py:438,454`, no other scoped production catch from the canonical set, the zero/two ceilings at `.claude/skills/harness/bin/check-plan-routes.py:2192-2228`, and independent increase/reduction mutants at `tests/integration/test-check-plan-routes.py:2892-2922` with red-first receipts at `notes/red-first-receipts.md:114-131`. SC-03's implementation and red-first evidence are present, including `harness_boundary.py:430-454`, `tests/unit/test-harness-boundary.py:1004-1023`, and the boundary cases indexed throughout the pinned unit and integration tests, but its declared `evidence: unit` does not execute the tool-family assertions that live only under `tests/integration/`.
- **reader — partial** — Carrying criteria: SC-05, SC-06. SC-05 is discharged by direct baseline-to-pin inspection: retained silence rationales remain unchanged around narrowed handlers, the copied DEC-234 prologue/reciprocal comment precedes the first `run-unit-tests.py` diff at line 49, and each new explanatory block is separate and marked `FEAT-64`; `notes/build-divergences.md:33-38` inventories the moves. SC-06 has red-first and pinned implementation evidence for both removed duplicate plan parses (`notes/red-first-receipts.md:71-73,117-135`; `handoff_done_when.py:126-148`; `check-plan-routes.py:558-581`; `tests/unit/test-handoff-done-when.py:462-501`; `tests/integration/test-check-plan-routes.py:2867-2886`) and the existing loader-family mutants cover plan, feature, and harness config sources (`check-plan-routes.py:1830-1835,1914-1926`; `test-check-plan-routes.py:2597-2606,2741-2752`), but the declared `evidence: integration` omits the handoff reparse assertion in the unit suite.

## Obligation audit

- **No hook wiring:** the pinned hook-path diff is empty, and the only pinned production `hook_guard` occurrence is its definition; this satisfies the no-wiring constraint independently of the test claim.
- **Deliberate divergences:** A2-A4 and B1/B3-B7 have identifiable old/new observations and a signed-task rationale in `notes/build-divergences.md:13-31`. A1/A5 lack exact byte pairs, and B2 is not owned or ruled by the approved plan; these are findings GC-64-01 and GC-64-03.
- **Removed reparses:** the two FEAT-64 removals are each tied to a pre-change failure, a one-load pinned assertion, and consumption of the cached parsed document. The remaining gap is evidence-kind routing, not an unidentified reparse.
- **Comments:** baseline-to-pin inspection agrees with ledger §C: moved rationales are unchanged, the DEC-234 copied prologue and reciprocal comment are untouched, and new explanations are separately marked `FEAT-64`.

## Findings

### GC-64-01 — exact byte evidence is incomplete

- reader: `harness-pm`
- kind: `substance`
- severity: `high`
- failure scenario: A suite can lose or rewrite an established output line while also adding a FEAT-64 line; the recorded digest proves that some difference exists, while A1's pattern list and A5's `/T/tmpXXXX` placeholders cannot prove that the listed addition/path substitution was the only byte difference required by SC-01.
- task owner: `T-03`
- anchors: `BRIEF.md:25-27`; `plan.yaml:193-197`; `notes/red-first-receipts.md:7-41`; `notes/build-divergences.md:13-19`
- artifact path: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-64-broad-exception-libs-tools/.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/research-FEAT-64-broad-exception-libs-tools-goalcheck-validate-c0.md`

### GC-64-02 — signed evidence kinds do not cover all carrying assertions

- reader: `harness-pm`
- kind: `form`
- severity: `medium`
- failure scenario: a verifier resolving SC-03 only through the declared unit kind never executes the eight tool-family boundary assertions under `tests/integration/`; a verifier resolving SC-06 only through integration never executes handoff's one-parse assertion under `tests/unit/`, so either criterion can be reported met without all of its clauses running.
- task owner: `T-03` (terminal evidence), with assertions produced by `T-01` and `T-02`
- anchors: `BRIEF.md:31-40`; `tests/unit/test-harness-boundary.py:962-1023`; `tests/unit/test-handoff-done-when.py:462-501`; `tests/integration/test-board-station.py:253-291`; `tests/integration/test-check-plan-routes.py:2867-2886`
- artifact path: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-64-broad-exception-libs-tools/.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/research-FEAT-64-broad-exception-libs-tools-goalcheck-validate-c0.md`

### GC-64-03 — board_lifecycle production change has no approved task owner or ruling

- reader: `harness-pm`
- kind: `substance`
- severity: `medium`
- failure scenario: when `github.repo` is absent, `.claude/skills/harness/bin/board_lifecycle.py` now constructs and renders a valid `GhError` instead of the baseline constructor `TypeError`; this deliberate operator-visible change is outside the BRIEF's eighteen production files and every approved task file list, and ledger B2's “fixed in passing” is not the operator ruling required by D-03/SC-01.
- task owner: `none in approved plan` (change surfaced during T-02)
- anchors: `BRIEF.md:48-55`; `plan.yaml:73-79,141-173`; `.claude/skills/harness/bin/board_lifecycle.py` baseline-to-pin diff; `notes/build-divergences.md:21-27`; `tests/integration/test-board-lifecycle.py:759-793`
- artifact path: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-64-broad-exception-libs-tools/.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/research-FEAT-64-broad-exception-libs-tools-goalcheck-validate-c0.md`

## Dismissed and advisory items

None.

## Open questions

None.
