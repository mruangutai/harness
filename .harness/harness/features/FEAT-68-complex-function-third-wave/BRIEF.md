# BRIEF — FEAT-68 complex function third wave

## Problem

Five grade-1 orchestration functions in the Harness control plane remain harder to review and change safely than their behavior warrants: `process_plan_yaml`, `classify`, `_audit_findings`, `scan`, and `domain_check`. Their ordered rules and phases need explicit structure without changing any observable contract. The unused `render-brief.py` path also leaves a dead markdown-to-HTML implementation, its test and classification/reference residue, and 102 tracked feature-history HTML derivatives that can drift from the markdown record.

## Done when — by perspective

**operator** — I can rely on byte-identical exit status, stdout, and stderr from every owning executable suite at the immutable implementation pin versus baseline `e655f14a56a14bf1777cae55a19195c9af10505d`, after normalizing raw checkout-root output lines, with every old/new/ruling divergence recorded. The dead renderer and all prescribed residue are absent, both test kinds pass, and an exercised validate flow produces the briefing markdown without an `.html` sibling.

**code maintainer** — I find every function remaining in the five target production files at code grade 4 or better except functions at exactly grade 2. The five named drivers are decomposed only through the settled small rule/phase helpers, existing comments remain byte-for-byte with their rules, and any new factual comment cites FEAT-68. The implementation pin contains no other production-code changes.

## Success criteria

- SC-01 (code maintainer): At the immutable implementation pin, the repository code-grade analyzer reports every function in `.claude/skills/harness/bin/check-plan-routes.py`, `harness_boundary.py`, `board_lifecycle.py`, `layout_migration.py`, and `check-domain.py` at grade 4 or better except exact grade 2; the five named target functions are present in that result. A committed red-first receipt records the same plan-inline assertion failing against baseline before production changes.
  verify: automated
  evidence: unit
- SC-02 (operator): Every named owning executable suite is run in clean detached baseline and pin checkouts under `.claude/worktrees/harness/`; exit status, stdout, and stderr bytes match after raw checkout-root output lines are normalized up front while raw bytes and hashes are preserved. A completed old/new/ruling ledger accounts for every divergence without treating root normalization as a divergence.
  verify: automated
  evidence: integration
  fail-first: the baseline-versus-pin byte comparison is this criterion's fail-first equivalent; byte identity has no pre-fix red form under the preserved FEAT-66/FEAT-67 operator ruling.
- SC-03 (code maintainer): Review of the immutable pin finds only the settled rule/phase decomposition in the five target production files plus deletion of `render-brief.py`; ordered short-circuits, finding order, accumulation, formatting, and raw-versus-normalized comparisons are preserved. Existing comments travel byte-for-byte with their rules and new factual comments cite FEAT-68. The renderer test, exact briefing sentence, canonical-reader row, all 102 tracked feature-history HTML derivatives, and only the named test comment mention are removed or reworded as prescribed.
  verify: inspection
- SC-04 (operator): The red-first, clean detached-pin, and divergence/comparison receipts are committed only after the immutable implementation pin exists; each names the base and pin SHAs, exact commands, exit status, hashes, comparison result, and the completed old/new/ruling ledger where applicable. No receipt claims to exist inside the pin it evaluates.
  verify: inspection
- SC-05 (operator): At the pin, neither `render-brief` nor `md_to_html` remains outside notes, logs, decision records, and feature-history records; both repository test kinds pass; and an actual validate run emits the briefing markdown with no `.html` sibling. The deleted renderer and its deleted unit test are not treated as owning-suite byte-identity subjects.
  verify: automated
  evidence: integration

## Verification gaps

- none; unit and integration test kinds are active, and the pinned review plus post-pin receipts supply the required inspection and chronology evidence.

## Constraints

- Preserve the FEAT-66/FEAT-67 proof rulings: compare baseline with the immutable implementation pin, normalize only raw checkout-root output lines up front, preserve raw evidence and hashes, and ledger every real divergence.
- Refactor `process_plan_yaml` as a small driver over per-task rule evaluation, `classify` as ordered boundary short-circuit phases, `_audit_findings` as a per-issue rule evaluator, and `scan` and `domain_check` as small phase drivers. Preserve existing order and output exactly.
- Delete `.claude/skills/harness/bin/render-brief.py`, `tests/unit/test-render-brief.py`, the exact renderer sentence in `briefing.md`, the canonical-reader classification row, and all 102 tracked `.harness/harness/features/*/notes/*.html` derivatives. Reword only the renderer comment mention in `test-gen-decisions-index.py`.
- Run implementation and proof collection main-session-direct. The plan has exactly one `cross_module` task, every success criterion traces to it, source issues remain empty, and approval remains pending.
- Do not add a permanent grade lock, behavior, verb, schema, compatibility path, or replacement HTML renderer.

## Out of scope

- The nine CLI dispatchers and nine lighter grade-1 functions identified during grilling.
- `check-skill-refs.scan`, which is not present on the pinned baseline.
- Any behavior change, new permanent code-grade gate, verb, schema, or compatibility alias.
- GitHub issue #1928 or any unrelated cleanup.

## Approval

status: pending
