# Code review — FEAT-53 frontend fix c2

BLUF: The five authorized frontend findings are resolved at `ffd9fb0204701cdae968ef0febc86943fb4829bd`, with no new frontend finding. The overall reviewer verdict is nevertheless FAIL because the mandatory canonical full-feature Python grade is `fail`; that inherited gate is outside this no-further-scope frontend repair and is not reopened as an authorized finding.

## Stage 1 — spec compliance

- **V-02 — resolved (T-14/T-28).** Independent query states remain separate in `client/src/routes.tsx:55-62`; the added reverse case rejects `/api/work` while asserting the settled KPI heading and Escaped Defects link remain usable (`client/src/routes.test.tsx:109-123`). The converse KPI-failure case remains at `routes.test.tsx:94-107`. The scoped route suite passed 13/13 at the pinned tip.
- **V-03 — resolved (T-14/T-28).** `fetchKpis` now declares the live top-level `{features, aggregate, trend}` contract (`client/src/api.ts:5`), both tile and panel routes consume that payload directly (`client/src/routes.tsx:55-72`), and the test fixture has the same live shape (`client/src/routes.test.tsx:7-17`). The drill test reaches the level-one Escaped Defects panel, its disclosure, and `/work/BUG-1` (`routes.test.tsx:125-149`), eliminating the former `data.kpis` fail-open/fabricated adapter.
- **V-17 — resolved (T-13).** The keyboard-only rule now uses the defined `--color-text-primary` token for a 2px solid outline, while route landing headings remain deliberately outline-free (`client/src/routes.tsx:42`). The receipt's actual-browser probe measured `focusVisible: true`, `2px solid`, `rgb(250, 250, 250)`.
- **V-18 — resolved (T-13/T-28).** `body{margin:0}`, 24px shell padding, the 831px/16px media rule, fixed table layout, and wrapping are co-located in the shell (`client/src/routes.tsx:42`). The receipt records exact browser geometry of 24px desktop and 16px narrow gutters with `scrollWidth === clientWidth` at both widths.
- **NEW-fixed-dark-document — resolved (T-13 per operator ruling).** `:root{color-scheme:dark}` and the opaque `rgb(27,27,27)` body ground implement DESIGN C-3 (`client/src/routes.tsx:42`); the receipt records those exact computed browser values.

The repair changes only the four authorized client source files, their deterministic generated bundle, and its receipt. The sole commit in `7dbb0259..ffd9fb02` is the repair. A fresh scoped Vite build succeeded and left both `src/` and `dist/` byte-identical to the pinned commit.

## Stage 2 — code quality

The live KPI contract no longer relies on a nonexistent lookup, independent request failures block only their own region, and neither rejection is silently converted into empty data. Invalid KPI numbers remain non-rendering rather than fabricating a panel (`client/src/routes.tsx:65-72`). No new substantive, form, or proportionality frontend finding was found.

Coverage limits: this pass independently ran only `src/routes.test.tsx` (13/13) and the client build; it did not repeat the receipt's CDP browser probes or any project-wide suite. Browser computed-style and geometry closure relies on pinned source inspection plus the receipt's recorded actual-browser measurements. Per the reviewer protocol, `code_grade` audits `merge-base(origin/main, ffd9fb02)..ffd9fb02`, not merely the repair diff; that canonical run reports `fail`. The dispatch forbids reopening V-09, V-10, V-11, V-16, and V-20 and allows no further scope, so this report does not recast inherited full-feature records as a new frontend finding.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "All five authorized frontend findings are resolved with no new frontend finding, but the mandatory canonical full-feature Python code grade remains fail."
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: fail
  reviewed: "7dbb025995b92a45c6a9d4035b56917a00fc7699..ffd9fb0204701cdae968ef0febc86943fb4829bd"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.harness/harness/features/FEAT-53-metrics-dashboard/notes/review-harness-code-reviewer-c2.md
```
