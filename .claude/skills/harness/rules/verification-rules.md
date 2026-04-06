# Harness: Verification Rules

## Authority

This file is injected via agent_skills into gsd-verifier. These rules augment GSD's built-in verification -- do NOT duplicate checks GSD already performs.

## Harness-Specific Verification

After GSD's standard verification completes, additionally verify:

### 1. TDD Compliance Check

For implementation plans: confirm test files exist for every new production file created or substantially modified in this plan.

- Identify all new production files listed in the plan's SUMMARY.md key_files.created
- For each production file, verify a corresponding test file exists (same directory or `tests/` sibling, matching filename pattern)
- If a production file has no corresponding test file, flag it: `HARNESS-FAIL: No test file for [path]`
- Plans with type matching `tdd_exempt_plan_types` in harness.json (config, docs, scaffolding) skip this check

### 2. Spec Traceability Check

Every plan task must trace to a CONTEXT.md decision or REQUIREMENTS.md requirement.

- Read the phase CONTEXT.md decisions section
- For each task completed in this plan, verify at least one CONTEXT.md decision ID (D-NN) or REQUIREMENTS.md requirement ID (REQ-NN) is referenced in the plan or SUMMARY.md
- If a task has no traceable decision or requirement, flag it: `HARNESS-FAIL: Task [name] has no CONTEXT.md or REQUIREMENTS.md traceability`

### 3. Gate Completion Check

For implementation plans (plan type "execute"): verify the code review gate was triggered before verification.

- Check SUMMARY.md for evidence that harness-code-reviewer was spawned (reviewer findings, Stage 1/Stage 2 results, or explicit gate-skipped notation)
- If no evidence exists and the plan type is "execute", flag it: `HARNESS-FAIL: Code review gate (harness-code-reviewer) was not triggered for this implementation plan`
- Plans with type matching `tdd_exempt_plan_types` skip this check

## What NOT to Duplicate

GSD's verifier already checks: must_haves truths/artifacts/key_links, plan success criteria, file existence, automated test commands. Do NOT re-check these.
