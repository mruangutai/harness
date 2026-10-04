# PASS — delimiter-collision lesson retained within the existing cap

One craft replacement applied; no repository expertise changed. No review, diff, build, test, lint, formatter or mutant execution occurred.

## Candidate judgments
- **Accepted / skim (2):** `review-harness-code-reviewer-c2.md`, Stage 1 R2, and `review-harness-code-reviewer-c3.md`, R2 disposition: searching for normalized payload text can select its surrounding delimiter. Six-spawns test: changes how I inspect any wrapper-preserving rewrite, not just paths. Retained as craft G-04 (43 words); quote-only payloads and literal output checks discriminate the collision.
- **Rejected / skim (1):** c1 R1 / c2 R1 closure: compare the exact classification predicate, then resolve an approved specification mismatch. Existing O-08 already captures remedy direction; no incremental durable rule.
- **Rejected / skim (3):** c3 canonical-range Stage 2 after Stage 1: mandatory review protocol already states this; do not duplicate it in capped expertise.
- **Rejected / self-derived:** c3 original/revised input convergence: idempotent transformation is useful but this record contributes no new review action beyond existing protocol and craft guidance.
- **Rejected / self-derived:** plan-c1 shared effective-input seam: sound reuse of existing interfaces, not evidence for a distinct new rule. The one-run seven-tool shape is not a transferable recipe.

Sources were only the four assigned prior notes (plan-c1, c1, c2, c3); no observations log or runs/ source used. Source transformations are historical inspection evidence, not newly executed probes.

## Mutation receipt
- Capability definition: `/Users/molchairuangutai/GitHub/harness/.omp/agents/harness-code-reviewer.md:4-10,35-42` grants Write/Bash and own Expertise. `check-domain.py --resolve /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-code-reviewer.md` actually resolved **harness-code-reviewer** before mutation.
- Feature-root resolver returned the dispatched absolute worktree root.
- Applied via `expertise-merge.py ops --ops -`: **replace**, target **G-04**, section **Gotchas**, file `/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-code-reviewer.md`.
- Entry: WHEN rewriting a normalized substring inside preserved wrappers DO derive its insertion offset from the parsed boundaries, not a first-occurrence search; check payloads made entirely of delimiter characters and assert literal output, because the payload can match its own opening wrapper.
- Why: displaces the narrower sibling-test-order warning at the full Gotchas cap; P-01 still requires checking coverage claims against actual invocations/assertions. No new rule was merged into a survivor; all other entries preserved by the locked merge tool.
- Actual pre-apply counts → post-apply counts: Patterns **15→15**, Gotchas **15→15**, Outcomes **10→10**, Open **0→0**. Merge output: `REPLACED G-04`, `APPLIED` at the target file.
- Required scoped checker: `check-expertise.py` returned **OK**, exit **0**, for the sole touched expertise file. No scratch files created. Open questions: none.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Retained delimiter-boundary rewrite lesson by replacing a weaker capped gotcha; scoped checker passes."
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: n_a
  reviewed: none
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-code-reviewer.md
  expertise_update:
    - op: replace
      target: G-04
      section: Gotchas
      entry: "WHEN rewriting a normalized substring inside preserved wrappers DO derive its insertion offset from the parsed boundaries, not a first-occurrence search; check payloads made entirely of delimiter characters and assert literal output, because the payload can match its own opening wrapper."
      why: "c2 R2 and c3 closure expose a general delimiter-collision defect; displaces the narrower sibling-test-order warning, whose claim-versus-invocation check remains covered by P-01."
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/notes/review-harness-code-reviewer-distill-validator.md
```
