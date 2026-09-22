# Answers — FEAT-1821 ship close-out — 2026-09-22

## Operator decision: SHIP, merged into feat/FEAT-53 at bdd9afae
Traces reviewed by the operator ("looks good"). Merge target feat/FEAT-53 per the 2026-09-17 grilling ruling (main has no dashboard client). Product, eng and validator distillation PASS; expertise ops applied.

## gh-sync ship deferred
`gh-sync.py ship` refuses any feature directory that resolves inside a worktree ("about to be deleted"); FEAT-1821's directory exists only on feat/FEAT-53 until FEAT-53 itself lands on main. Ruling: run `python3 .claude/skills/harness/bin/gh-sync.py ship .harness/harness/features/FEAT-1821-ui-verification-lane` from the main checkout immediately after FEAT-53's PR merges. Until then milestone #81 stays open and INV-30/INV-28 report it — a known, dated exception, not a defect.

## Backlog (from the briefing, unstruck)
- B-1 bug: scratch ui bundles land under the TARGET feature's runs/ and governed authors cannot clean them (Main intervened 6+ times).
- B-2 chore: post-approval amendments discoverable beside the BRIEF clauses they supersede.
- B-3 chore: distill runs must not consume rework cycles (ceiling raised 12→15 only to keep the ledger consistent).
- B-4 bug: a subagent spawn that dies before its first turn releases the dispatch-guard claim; the retry inherits an empty registry (Main recreated the claim by hand).
- B-5 chore: gh-sync ship cannot close a feature whose ruled merge target is a stacked branch.
- B-6 chore: feature-worktree.py `behind` fires only at the door; a multi-day build drifted 58 commits and the stale validate-digest hook produced false distill rejections.
- B-7 chore: the briefing's `npx playwright show-trace <relative path>` line is only correct inside the worktree with the package on PATH; docs to carry the absolute-path form.
Two INV-43 retrospective-seam findings (handoff-validate seq-29, handoff-build seq-31) are honest late-handoff record and stay as recorded.
