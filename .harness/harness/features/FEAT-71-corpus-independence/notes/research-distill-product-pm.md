# PM cold distillation — FEAT-71

**PASS: C1 accepted; C2 and C3 rejected as covered.** Applied only craft expertise in the assigned worktree. No diff review, product verification, T-01 execution, builds, tests, linters or formatters. No observations logs or other product-member evidence were assumed.

## Candidate dispositions

All source paths below are relative to this feature directory.

- **C1 — accept.** `notes/research-patch-intake.md:20` specified standalone clone identity but omitted inherited root-selection environment and clone-local setup. `notes/ship-review-fix-c1-validator.md:60-62` records three verify amendments for hook configuration and required main-ref targets; `:71-73` records environment contamination. This supports a craft planning rule about complete execution context, distinct from G-16's worktree-lifetime override. Added G-20 by displacing G-12, the weaker, narrow YAML-scalar syntax reminder; no survivor was expanded or merged. Neither the host hook defect nor repository-specific setup recipes become Expertise.
- **C2 — reject.** My own goal-check, `notes/research-FEAT-71-corpus-independence-goalcheck-validate-c0.md:22`, distinguishes committed deletion evidence from a pinned receipt binding edited/untracked local bytes to paths, sizes and hashes. G-17 already requires a recorded hash manifest where Git status cannot discriminate; G-15 requires the produced evidence at the review ref. The combined rules adequately cover this application; a deletion-specific restatement does not warrant displacing another entry. This is not credited as a lead discovery.
- **C3 — reject.** `notes/omp-session-accessor-live-2026-11-07.md:9-25` records identical baseline/feature failures, independently observed nested/flat accessor paths, and a stale subagent-identification premise; `notes/ship-review-fix-c1-validator.md:40-43` summarizes that distinction. P-14 already requires baseline comparison, O-06 requires reaching the actual measured branch, and G-18 separates runtime identity from source provenance. Apply those rules to distinguish classifier failure from accessor behavior; no additional entry, probe repair or Harness-defect lesson is warranted. Identical failures alone are not positive accessor proof; the raw session observations supply that evidence.

## Exact applied expertise_update

Target: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-71-corpus-independence/.harness/expertise/harness-pm.md`

```json
[
  {"op":"drop","target":"G-12","section":"Gotchas","why":"Displace the narrower YAML scalar syntax reminder at the full section cap; standalone execution-context planning addresses a distinct, repeatedly evidenced acceptance failure."},
  {"op":"add","target":"G-20","section":"Gotchas","entry":"WHEN authoring a standalone verify DO specify inherited environment isolation, clone-local configuration and required ref targets alongside commit identity before dispatch; a fresh clone neither sanitizes the parent environment nor preserves local Git setup, so correct checkout identity alone cannot establish the intended execution context.","why":"C1: ship-review-fix-c1-validator.md:60-62,71-73 records three clone-setup amendments and inherited root-selection contamination omitted by research-patch-intake.md:20; G-16 only covers worktree lifetime."}
]
```

Control-plane `expertise-merge.py ops --file <target> --ops -` exited 0: `DROPPED G-12`, `ADDED G-20`, `APPLIED <target>`. No main-checkout expertise or repository-tier expertise was changed.

| Touched expertise file | Patterns before → after | Gotchas before → after | Outcomes before → after | Open before → after |
|---|---|---|---|---|
| Worktree `.harness/expertise/harness-pm.md` | 15 → 15 | 15 → 15 | 10 → 10 | 0 → 0 |

## Required validation evidence

From the assigned feature worktree, ran exactly `python3 .claude/skills/harness/bin/check-expertise.py .harness/expertise/`. **Exit 0.** Complete output:

```text
OK   .harness/expertise/harness-ai-dev.md
OK   .harness/expertise/harness-backend-dev.md
OK   .harness/expertise/harness-code-reviewer.md
OK   .harness/expertise/harness-data-engineer.md
OK   .harness/expertise/harness-dev-ops.md
OK   .harness/expertise/harness-documentor.md
OK   .harness/expertise/harness-eng-lead.md
OK   .harness/expertise/harness-frontend-dev.md
OK   .harness/expertise/harness-orchestrator.md
OK   .harness/expertise/harness-pm.md
OK   .harness/expertise/harness-product-lead.md
OK   .harness/expertise/harness-qa.md
OK   .harness/expertise/harness-security-reviewer.md
ADVISORY .harness/expertise/harness-security-reviewer.md:19: G-01 names 'DEC-100' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-ui-reviewer.md
OK   .harness/expertise/harness-validator-lead.md
OK   .harness/expertise/harness-visual-designer.md
```

No violations; the unrelated security-reviewer advisory is not a blocker and was left unchanged. Open questions: none.
