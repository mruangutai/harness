# UI distillation — PASS

One craft rule accepted from skim; no new UI review or suite executed. Only the four assigned prior review notes supplied lesson evidence.

- **Accepted (skim 2):** c3's “adapter user-visible behavior is not a visual interface” and explicitly not-applicable dimensions become craft Gotchas G-15. Six-spawns test: prevents policy-only changes being mistaken for visual scope and prevents false visual all-clears. Unlike existing G-02 (batch/CLI reporting), this rule addresses adapter scope classification and the distinction between inapplicability and observed passes.
- **Rejected (skim 1):** c2/c3 complete census and absent DESIGN object are already covered by craft P-01/P-02, O-01/O-03/O-05; another entry changes no future action.
- **Rejected (self-derived):** plan-c1 adapter-only scope needs no prototype: follows P-01/P-03 and the accepted rule, not an independent lesson. c1–c3 routing adapter correctness to code/security/QA duplicates O-02.
- **Displaced:** former G-15 mistyped-pin recovery is narrower and less broadly useful than preventing incorrect UI applicability/verification claims. No survivor merged or expanded.
- **Authority:** `check-domain.py --resolve /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-ui-reviewer.md` returned `harness-ui-reviewer`; feature-root resolution matched the supplied worktree.
- **Counts (Patterns/Gotchas/Outcomes/Open):** craft `15/15/10/0 → 15/15/10/0`; repository `4/0/0/0 → 4/0/0/0` (unchanged, no repository ops).
- **Application:** `expertise-merge.py ops` reported `REPLACED G-15` and `APPLIED`; `check-expertise.py` reported `OK` on the sole touched Expertise file. No other verification executed. Accepted entries: skim 1, self 0; unapplied ops 0. Open questions: none.

Evidence pointers (same notes directory): `review-harness-ui-reviewer-plan-c1.md`, `review-harness-ui-reviewer-c1.md`, `review-harness-ui-reviewer-c2.md`, `review-harness-ui-reviewer-c3.md`.

```yaml
VERDICT: PASS
DIGEST:
  headline: "One craft applicability rule applied; census/routing duplicates rejected."
  mode: B
  in_scope: false
  severity_max: n/a
  findings: []
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: []
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-ui-reviewer.md
  expertise_update:
    - op: replace
      target: G-15
      section: Gotchas
      entry: "WHEN a diff changes non-rendering tool behavior DO distinguish user-visible policy outcomes from visual UI; report accessibility, theme, focus, and layout as not applicable when no visual surface exists, not as visually passed."
      why: "Skim c3 passes six-spawns test; broader applicability protection displaces narrower mistyped-pin recovery at cap."
      file: /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-ui-reviewer.md
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/notes/review-harness-ui-reviewer-distill-validator.md
```
