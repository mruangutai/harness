# BRIEF — BUG-2241 Rerunnable verify ids

## Problem

A signed verify recipe can create durable state using a literal single-use id, leaving validation unable to rerun it. BUG-2171 hit this when its smoke run was already closed; the missing authoring rule in harness-spec-driven lets that failure recur.

## Done when — by perspective

**operator** — I can rely on the verify guidance to require recipes that remain rerunnable when they create named records.

**pm (author)** — I can tell what id to use for a state-creating verify step without researching a past incident or guessing whether a literal id is acceptable.

**code maintainer** — I inherit one concise rule in the existing verify guidance, with content-specific evidence and no detector or unrelated recipe change.

## Success criteria

- SC-01 (operator): The verify literal-block section of .agents/skills/harness-spec-driven/SKILL.md requires a step creating durable state (run, issue, branch or other named record) to derive a fresh id at execution (timestamp or run counter) or receive one as a parameter, and calls a literal single-use id a defect because validation cannot rerun it. QA demonstrates the T-01 complete-rule content assertion failing against baseline 594af2a8123771da1a5290942400f4f8a064656f and passing against review_sha, reading git show <review_sha>:.claude/skills/harness-spec-driven/SKILL.md rather than an uncommitted file.
  verify: automated evidence: unit
- SC-02 (pm): Reading git show <review_sha>:.claude/skills/harness-spec-driven/SKILL.md, the reviewer can find one self-contained normative paragraph in the existing verify section that states both permitted id sources and the validation-rerun reason; its guidance applies to durable state generally, not just BUG-2171 smoke runs.
  verify: inspection
- SC-03 (code maintainer): The pinned source diff changes only .agents/skills/harness-spec-driven/SKILL.md (tracked as .claude/skills/harness-spec-driven/SKILL.md), adding only the specified 44-word rule and leaving existing guidance intact. The reviewer reads git show <review_sha>:.claude/skills/harness-spec-driven/SKILL.md and the pinned base-to-review diff; the author records actual skill-word delta and check-skill-weight.py output at that pin.
  verify: inspection

## Verification gaps

- The docs matrix requires no test kinds. Unit is active with a runnable cmd; SC-01 uses T-01's supplemental unit-level content assertion, not an unrelated suite result. The registered unit runner does not discover this inline assertion: QA must execute and cite it explicitly, including red-first evidence.
- Content assertions and SC-02 inspection prove the rule is present and usable, not that every future author obeys it. Mechanical detection of literal ids is excluded. No runtime behavior, live smoke rerun, UI, service API, or model-comprehension outcome is claimed; null/unresolved component, ui, typecheck and excluded functional/eval runners carry none of these SCs. No UAT is required.

## Constraints

- DEC-225 SUPPLIES the patch intake: at most 120 BRIEF lines and exactly T-01; no readers, panel or goal-check run. Both artifacts remain pending until the operator signs through the main session (DEC-120).
- DEC-158 move 1 BLOCKS history/procedure growth: one rule, one-clause why, DEC pointer. Add the 44-word paragraph in the existing verify literal-block section; no new section or supporting file.
- check-skill-weight.py SUPPLIES preload measurement. Baseline at 594af2a8123771da1a5290942400f4f8a064656f: skill 1137 words, pm 5001, universal 1476; projected +44 gives skill 1181 and pm 5045. Record actual words added because harness-spec-driven is PM-preloaded. Configured advisory budgets: agent 5500, universal 1900; do not change them.
- DEC-182 SUPPLIES plan/1, controlled plan-merge writes, a literal verify block and the 50-machine-line task cap. change_type docs is configured with an empty required-test floor and fits this text-only rule; the content assertion remains mandatory.
- DEC-179 BLOCKS inventing a team grant: check-domain --resolve returns NOBODY for this skill; SPEC section 6 reserves rule-skill editing to the human. This conflicts with the requested team route; only an explicitly disclosed main-session-direct route can use existing authority. Do not assign documentor or broaden grants to conceal it.
- PRODUCT is /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2241-smoke-run-id. AGENTS.md maps guidance to .harness/harness/docs/SPEC.md and DECISIONS.md; docs/spec.md, docs/decisions.md and docs/architecture.md are absent. These are read-input findings, not permission to create documents.

## Out of scope

- A mechanical gate detecting literal ids in verify blocks (could be a later enhancement).
- BUG-2171's already-shipped recipe (its smoke is single-use by operator ruling).

## Approval

status: pending
approved-by:
date:
