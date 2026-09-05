# SIMPLIFICATION angle — BUG-1303, 63404ef0..b724a0f4

**BLUF:** One low-severity finding — DECISIONS.md DEC-216 (line 6807) names a code site,
`required_by_persona` in `run_documented_contract_cases`, that the same-scope commit 8596745f
already moved before DEC-216 was written. Everything else judged (four-branch error path,
`_completeness_ok`'s six checks, `_discrimination_ok`'s two conjuncts, `PRE_FIX_REVIEWER_BLOCK`,
new docstrings/comments, the reviewer-md/SKILL.md prose) is load-bearing or a present-fact
statement. FLAG-ONLY throughout; zero edits made.

## Finding 1 — stale code-site reference in a decision record

- **File:** `.harness/harness/docs/DECISIONS.md`, line 6807 (DEC-216 body)
- **Summary:** DEC-216 says the schema-extension mirror developers must keep in sync is
  "`required_by_persona` in `run_documented_contract_cases`". After 8596745f (committed
  *before* b724a0f4, which wrote DEC-216), that mirror is `_required_contracts` — a
  separate function `run_documented_contract_cases` merely calls on the next line.
  `required_by_persona` still exists, but only as a parameter name of
  `documented_contract_results` (test-validate-digest.py:317), not as a local in
  `run_documented_contract_cases`.
- **Concrete cost:** a future engineer extending `SCHEMAS` for a persona, reading DEC-216 to
  find "that site," opens `run_documented_contract_cases` (test-validate-digest.py:475) looking
  for the per-persona `.update(...)` line and finds a four-line orchestrator instead; the real
  edit site (`_required_contracts`, line 385) is one function up, easy to find once you keep
  reading, but the decision record no longer names it correctly. This is exactly the "dead
  reference to a shape that no longer exists after a revision" case the SIMPLIFICATION angle
  is scoped to catch.
- **Exact alternative:** on DECISIONS.md:6807, replace `` `required_by_persona` in
  `run_documented_contract_cases` `` with `` `_required_contracts` (called from
  `run_documented_contract_cases`) ``.
- **Severity:** low — doc-accuracy only, one function away from correct, no behavior at stake.
- **Routing:** DECISIONS.md resolves to the documentor under check-domain (per dispatch), not
  NOBODY — this is a normal routed finding, not a lost flag-only one.

## Judgment questions answered explicitly

1. **New comments (docstrings) added in this diff — present fact or narration?** Present fact.
   Grepped the added block (test-validate-digest.py:239-495) for narrative markers (`used to`,
   `previously`, `the old`, `c22`/send-back style commit-cycle references) — zero hits. Every
   new docstring (`documented_block`, `documented_contract_gaps`, `documented_contract_results`,
   `run_documented_contract_cases`) states what the function does now, not what changed to get
   there. (The pre-existing "c22 send-back" narrative comments at lines 117-220 predate
   63404ef0 and are out of this diff's scope.)
2. **`_completeness_ok`'s `checks` tuple / `_discrimination_ok`'s conjunction — redundant or
   distinct?** Both distinct, on both counts:
   - `_completeness_ok`'s six checks correspond 1:1 to the six synthetic roster entries
     (`unmapped`, `empty`, `absent`, `unlocatable`, `outside`, `control`) and each asserts a
     different branch's message text; none is a repeat of another.
   - `_discrimination_ok`'s two conjuncts test opposite directions of one property (omission
     flagged vs. presence accepted) — dropping either leaves the "discriminates" claim
     unproven in that direction. Not redundant.
   Per the standing rule, even a genuinely duplicated assertion here would be a **backlog row**,
   never an apply — moot since none was found.
3. **`documented_contract_results`'s four-branch error path — load-bearing or ceremony?**
   Load-bearing. Each of the four branches (unmapped persona / absent source / unlocatable
   block / field gaps) produces a distinctly-worded line, and `_completeness_ok` asserts each
   by a distinct substring pulled from the synthetic run — deleting any branch's distinct
   message would silently pass `_completeness_ok`'s corresponding check as a false negative
   only if the branch collapsed into another's wording, which none do.
4. **`PRE_FIX_REVIEWER_BLOCK` — dead reference or discriminator proof?** Discriminator proof,
   not dead. It is a frozen literal of the pre-fix `## Output` block (missing `code_grade`),
   used only by `_discrimination_ok` to prove the gap-detector both flags the field's absence
   (`pre_fix_gaps == ["code_grade"]`) and accepts it once added
   (`with_code_grade` gaps `== []`). It never claims to model the *current* file (which now has
   `code_grade`) — it deliberately models the superseded shape as a regression fixture. This is
   the "anchoring semantics the original fought for" case the skill calls out as NOT complexity
   to trim.

## Restructuring precedent (8596745f) — respected, not re-litigated

Confirmed via `git show 8596745f --stat` / `git show 8596745f`: it already split one
grade-2-flagged monolith into `_skill_documented_block`/`_agent_documented_block` (extraction
by branch), `_required_contracts`, `_reviewer_plan_mode_results`, `_discrimination_ok`,
`_synthetic_contract_results`, `_contains_line`+`_completeness_ok`, and `_report_group_result`.
Each resulting helper is small, single-purpose, and independently named in tests
(`_completeness_ok`, `_discrimination_ok` by name). No second restructuring is proposed here —
that would be churn with no defect behind it.

## Reviewer-md / SKILL.md / DECISIONS-INDEX.md

`.claude/agents/harness-code-reviewer.md`, `.omp/agents/harness-code-reviewer.md`,
`.claude/skills/harness-code-review/SKILL.md`: the DEC-207 plan-phase-review rule is stated in
all three plus the inline `# reviewed: plan:...` comment. This reads as duplication but isn't:
these are genuinely independent consumers (two runtime-specific agent prompt templates + one
skill doc), and DEC-216 itself exists to catch exactly this kind of three-way drift
mechanically (`_reviewer_plan_mode_results` greps all three sources for the same tokens). No
finding — matches the standing repository pattern (O-08: no shared-constant span means the
repetition is load-bearing, not drift). DECISIONS-INDEX.md's DEC-216 summary row is an accurate
high-level restatement, not a second copy of the rule body — no finding.

## Scope confirmation

`git status --porcelain` in the worktree, run at the end of this pass:

```
 M .harness/harness/features/BUG-1303-plan-code-review-digest/feature.json
 M .harness/harness/features/BUG-1303-plan-code-review-digest/plan.yaml
?? .harness/harness/features/BUG-1303-plan-code-review-digest/notes/receipt-harness-dev-ops-simplify-efficiency.md
```

The two modified files and the sibling's receipt are not touches by this angle — `feature.json`/
`plan.yaml` reflect concurrent orchestrator/sibling activity in this shared worktree (O-06); the
untracked receipt belongs to the EFFICIENCY reader. No file in the reviewed diff was modified by
this pass.
