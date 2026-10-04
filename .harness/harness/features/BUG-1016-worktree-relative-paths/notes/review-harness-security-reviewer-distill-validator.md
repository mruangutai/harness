# Security distillation — authority boundaries

**PASS: one craft rule applied; no fresh security audit or suite execution.** Only the listed c1/c2/c3 security notes supplied lesson evidence; no observations or runs were consulted.

## Judgment and receipt

- **Accepted (skim 2):** success-only authority caching, authority-context partitioning, resolver/run lifetime, and authorization before cache hits. Sources: `review-harness-security-reviewer-c1.md` Scope and evidence / Limits; `review-harness-security-reviewer-c2.md` Cache isolation. Six-spawns test: changes how future cached-resolver audits distinguish cached destinations from permission. Craft: useful in unfamiliar repositories. Entry is 42 words, WHEN/DO, with no feature/task/issue identifiers.
- **Rejected (skim 1):** lexical checkout selection is not containment; approved traversal/symlink exclusions are already covered by craft O-05's structural/signed-risk disposition. A new repository recipe would age without changing future action.
- **Rejected (skim 3):** literal output assertions support inspection-only closure without adopting others' runtime counts. Identity-level evidence is already covered by O-01; separating unexecuted preconditions is covered by O-04. No duplicate entry or retrospective runtime claim.
- **Rejected (self, c1–c3):** remeasure each pinned census and sweep all changed files for secrets — duplicates O-07 and P-14.
- **Rejected (self, c1–c3):** preserve agreement between pre-policy, execution and post-policy destinations, including URI siblings — useful, but at the full Patterns cap no remaining entry is clearly weaker; P-06 already covers token-only exemptions partially. Not merged into a survivor.
- **Rejected (self, c3):** insert at a literal wrapper boundary rather than searching for a repeated substring — a narrow implementation lesson, weaker for future security reviews than existing entries.

**Applied op:** craft `Patterns/P-15`, `replace`; deliberately displaces the narrower sibling-escaping heuristic, not a merge. No repository update. Accepted totals: skim 1, self 0; rejected totals: skim 2, self 3.

**Capability:** inspected `.omp/agents/harness-security-reviewer.md:1-20` (Write/Bash present). `check-domain.py --resolve /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-security-reviewer.md` returned `harness-security-reviewer`. Feature-root resolver returned the dispatched absolute worktree root. Merge result: `REPLACED P-15`, `APPLIED`.

**Counts (Patterns / Gotchas / Outcomes / Open):** craft `15/15/10/0 → 15/15/10/0`; repository `5/9/1/0 → 5/9/1/0` (unchanged). All other entries preserved.

**Checker:** `check-expertise.py` on the sole touched Expertise file exited 0, `OK`. Existing G-01 naming DEC-100 received a repository-layer advisory; it concerns a hook-specific blocking convention, not the new cache rule. Left unchanged as unrelated curation. No other verification executed. Open questions: none.

```yaml
VERDICT: PASS
DIGEST:
  headline: One portable cache-authority rule applied; duplicates and weaker candidates rejected.
  in_scope: false
  scope_reason: Source-only feature-close distillation; no diff reviewed or security boundary freshly audited.
  severity_max: n/a
  findings: []
  must_fix: []
  threat_model: []
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-security-reviewer.md
  expertise_update:
    - op: replace
      target: P-15
      section: Patterns
      entry: "WHEN auditing a cached authority resolver DO verify only successes are cached, keys partition every authority-changing context, cache lifetime follows the resolver and run, and readiness plus per-operation authorization precede cache hits; caching a destination must never cache permission to use it."
      why: "c1/c2 cache-boundary evidence generalizes across repositories; displaces the narrower sibling-escaping heuristic at the full cap."
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/notes/review-harness-security-reviewer-distill-validator.md
```
