# BRIEF — FEAT-66 complex function drivers

## Problem

The maintainers of three enforcement-layer rule evaluators must change hundreds of lines of intertwined branching to alter one rule, while the existing grade ratchet tolerates their legacy grade-1 drivers. That concentration makes review and safe extension expensive even though each body already consists of ordered, independently explainable rules.

## Done when — by perspective

**operator** — I can rely on all existing enforcement outcomes and output bytes from the three evaluators remaining unchanged, with any divergence explicitly enumerated and ruled, and on reproducible evidence from the exact implementation pin rather than the working tree.

**code maintainer** — I can change or review one rule without traversing a grade-1 monolith: each of the three named functions is a small driver over ordered per-rule functions, and every function produced or retained by this refactor meets the production code-grade bar except the grader's grade-2 exception. The comments that explain each rule remain byte-for-byte with that rule.

## Success criteria

- SC-01 (code maintainer): At the implementation pin, `shape_problems`, `validate`, and `apply_merge`, plus every per-rule or per-phase function extracted from them, grade 4 or better under `code_grade.grade_source`, except a function graded exactly 2; the committed red-first receipt demonstrates this grade assertion failing against the pre-refactor source.
  verify: automated
  evidence: unit
- SC-02 (operator): From a clean checkout of the exact implementation pin, each named owning suite has the same exit status, stdout bytes, and stderr bytes as its pre-refactor baseline except divergences whose exact old bytes, new bytes, affected case, and operator ruling are recorded; an unledgered difference fails verification.
  verify: automated
  evidence: integration
- SC-03 (code maintainer): At the pinned review SHA, the only production changes are the decomposition of `check-domain.shape_problems`, `validate-digest.validate`, and `plan-merge.apply_merge`; rule order is preserved, and every load-bearing comment moved with its rule byte-for-byte rather than being rewritten or dropped.
  verify: inspection
- SC-04 (operator): The pinned review SHA contains the red-first receipt, clean-checkout implementation-pin receipt, and divergence ledger, all committed after the implementation pin; they name the exact baseline and implementation pins, commands, checkout identity, exit statuses, and stdout/stderr byte evidence without claiming to exist inside the earlier pin.
  verify: inspection

## Verification gaps

- none; the unit and integration kinds that cover the named grader and owning suites both have active runners.

## Constraints

- DEC-174 SUPPLIES direct execution: all three production functions and their owning proof are enforcement-layer work, so T-01 is `main-session-direct` and has no developer dispatch.
- DEC-225 SUPPLIES the patch lane: this intake has one task, no panel, no goal-check, and a BRIEF no longer than 120 lines.
- The established `code_grade` ratchet remains the only grade lock; add no second checker or lock.
- Preserve rule and output order. Read each function's shared context once, then apply its existing rule families without introducing a shared record type across the three files.
- Change no behavior. Any observed output divergence requires an exact old/new ledger entry and an explicit operator ruling before it can be accepted.
- Move each existing load-bearing comment byte-for-byte with the rule it explains.
- The red-first and clean-checkout receipts and divergence ledger are committed after the implementation pin they grade.

## Out of scope

- The 12 grade-1 CLI dispatchers (`main`, `_main`, and `cmd_*` in gh-sync, factory_*, board-station, feature-record, feature-worktree, upgrade-config, and wayfind): argparse fan-out is a different shape and is not forced into the rule-table pattern.
- The other 16 grade-1 rule evaluators (`approval_guard`, `hook_mode`, `parse_digest`, `check-omp-port.check`, `md_to_html`, and the rest): they are the mechanical second wave after this pattern survives review.
- Any behavior change in the three production files, or any new lock, verb, or schema.
- #1928 and the digest wire format: that remains separate; this work only makes `validate` cheaper to change later.

## Approval

status: approved
approved-by: molchairuangutai
date: 2026-09-26
