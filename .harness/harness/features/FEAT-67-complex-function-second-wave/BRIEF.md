# BRIEF — FEAT-67 complex function second wave

## Problem

Operators and code maintainers must audit or change three grade-1 enforcement functions whose independently ordered rules or parsing phases are intertwined in large bodies. The concentration makes narrow changes expensive and error-prone even though the observable contracts and decomposition shapes are already settled.

## Done when — by perspective

**operator** — I can rely on every existing enforcement outcome, error order, exit status, stdout byte, and stderr byte from the three target functions remaining unchanged, with any divergence explicitly enumerated and ruled from reproducible evidence at the immutable implementation pin.

**code maintainer** — I can review or change one rule or parsing phase without traversing a grade-1 monolith: each target is a small driver over its settled decomposition shape, every function introduced or retained by that decomposition meets the production code-grade bar except the grader's exact-grade-2 exception, and each explanatory comment remains byte-for-byte with its rule.

## Success criteria

- SC-01 (code maintainer): At the implementation pin, `approval_guard`, `check`, and `parse_digest`, plus every function introduced or retained by their decompositions, grade 4 or better under `code_grade.grade_source`, except a function graded exactly 2; the committed red-first receipt demonstrates the same inline grade assertion failing against base `00c7219e` before production changes.
  verify: automated
  evidence: unit
- SC-02 (operator): From a clean detached checkout of the immutable implementation pin under `.claude/worktrees/harness/`, every named owning suite has the same exit status, stdout bytes, and stderr bytes as base `00c7219e` after the ruled checkout-root normalization; any other difference fails unless the divergence ledger records its exact old bytes, new bytes, affected case, and operator ruling in completed built form.
  verify: automated
  evidence: integration
  fail-first: the baseline-versus-pin byte comparison is this criterion's fail-first equivalent; byte identity has no pre-fix red form (operator ruling 2026-09-26, FEAT-66 validate c0 MF-05).
- SC-03 (code maintainer): At the pinned review SHA, the only production changes are the decomposition of `check-domain.approval_guard`, `check-omp-port.check`, and `validate-digest.parse_digest` into their settled distinct shapes; existing explanatory comments move byte-for-byte with their rules, new factual comments cite FEAT-67, and no other production code changes.
  verify: inspection
- SC-04 (operator): The pinned review SHA contains the red-first receipt, clean implementation-pin byte receipt, and divergence ledger, all committed after the implementation pin; they identify base `00c7219e`, the immutable pin, clean checkout, commands, exit statuses, stdout and stderr byte evidence, and grade records without claiming the receipts exist inside the earlier pin.
  verify: inspection

## Verification gaps

- none; the unit and integration kinds covering the code-grade assertion and named owning suites both have active runners.

## Constraints

- DEC-174 SUPPLIES direct execution: the three enforcement-layer targets and their owning proof remain one `main-session-direct` task with no developer dispatch.
- DEC-225 SUPPLIES the patch lane: this intake has one task, no panel, no goal-check, and a BRIEF no longer than 120 lines.
- Base all red-first and byte-comparison proof on `00c7219e`; perform pin proof in a clean detached checkout under `.claude/worktrees/harness/`.
- Normalize each checkout's raw absolute-root output lines before comparison, while retaining the raw bytes in the receipt; this normalization is not a divergence.
- The existing `code_grade` ratchet remains the only lock. SC-01 uses the plan's inline grade assertion and no permanent second grade-lock file.
- SC-02's baseline-versus-pin byte comparison is its fail-first equivalent. Set `change_type: cross_module` so both active test kinds remain required.
- Preserve the three distinct settled decompositions, all short circuits, accumulation and output order, cursor semantics, and raw-versus-normalized distinctions. Do not introduce a shared mutable context bag.
- Change no behavior. Record each actual divergence only in completed built form with exact old bytes, new bytes, affected case, and operator ruling; reject every unledgered difference.
- Move existing explanatory comments byte-for-byte with their rules. Any new factual comment cites FEAT-67.
- Commit the red-first receipt, clean implementation-pin byte receipt, and divergence ledger only after the implementation pin, explicitly without claiming they exist inside that pin.

## Out of scope

- The nine grade-1 CLI dispatchers; their argparse fan-out is a different shape.
- The seven other grade-1 evaluators: `md_to_html`, `process_plan_yaml`, `classify`, `check-skill-refs.scan`, `layout_migration.scan`, `_audit_findings`, and `domain_check`.
- `validate-digest.hook_mode`; it is a dispatcher beside the target parser.
- Any behavior change in the three production files.
- Any new lock, verb, or schema.
- #1928; the digest wire-format work remains parked.

## Approval

status: pending
approved-by:
date:
