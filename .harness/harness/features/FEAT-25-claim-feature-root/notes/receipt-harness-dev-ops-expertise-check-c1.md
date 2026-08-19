# Receipt — harness-dev-ops — check-expertise sweep (FEAT-25 D-check)

## Command run
```
.claude/skills/harness/bin/check-expertise.sh .harness/expertise/
```
(from repo root `/Users/molchairuangutai/GitHub/harness`)

## Verbatim output
```
OK   .harness/expertise/harness-ai-dev.md
OK   .harness/expertise/harness-backend-dev.md
OK   .harness/expertise/harness-code-reviewer.md
OK   .harness/expertise/harness-data-engineer.md
OK   .harness/expertise/harness-dev-ops.md
OK   .harness/expertise/harness-documentor.md
OK   .harness/expertise/harness-eng-lead.md
OK   .harness/expertise/harness-orchestrator.md
OK   .harness/expertise/harness-pm.md
OK   .harness/expertise/harness-product-lead.md
OK   .harness/expertise/harness-qa.md
OK   .harness/expertise/harness-security-reviewer.md
OK   .harness/expertise/harness-ui-reviewer.md
OK   .harness/expertise/harness-validator-lead.md
OK   .harness/expertise/harness-visual-designer.md
```
exit=0

All 15 files under `.harness/expertise/` — the three squad files plus every other owner's file
swept incidentally — reported `OK`. None failed; nothing to route to a tier above.

## Per-section entry counts (requested four files)

Counted by matching `- XX-NN: ` at column 0 within each `## Section` header, as the checker does —
not by highest id number.

| File | Patterns (max 15) | Gotchas (max 15) | Outcomes (max 10) | Open (max 5) | Total lines / 150 |
|---|---|---|---|---|---|
| harness-backend-dev.md | 15 | 15 | 0 | 0 | 106 |
| harness-dev-ops.md | 9 | 12 | 0 | 0 | 30 |
| harness-data-engineer.md | 5 | 3 | 0 | 0 | 32 |
| harness-eng-lead.md | 15 | 15 | 0 | 0 | 104 |

**Caveat confirmed:** `harness-dev-ops.md`'s Patterns section does not start at P-01 — its first
entry is P-02, highest id is P-10, and the entry count (9) is one less than the highest id number
(10). Counting by highest-id-number would have overreported this section by 1.

## Tree-movement note

A concurrent `git status --porcelain` capture during this run showed
`.harness/harness/features/FEAT-25-claim-feature-root/` and
`.harness/harness/features/FEAT-27-expertise-repository-tier/` as untracked (`??`), consistent with
another spawn writing a receipt under the FEAT-25 notes/ directory concurrently, as flagged in the
dispatch. No Expertise file showed as touched by that concurrent activity — the `M` files
(`harness-backend-dev.md`, `harness-data-engineer.md`, `harness-dev-ops.md`, `harness-pm.md`) reflect
prior working-tree state, not a change made during this check. This run edited no file except this
receipt.

## Scope discipline

Read-only verification. No Expertise file was edited, no file staged, no commit made.
