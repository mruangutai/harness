# Systematic Debugging

This file is injected via `agent_skills` into gsd-debugger. Follow ALL rules below. Evidence before fixes. Hypothesis before code changes.

## The 4-Phase Protocol

### Phase 1: Observe

- Reproduce the bug consistently before any code change
- Document the exact failure: input, expected output, actual output
- Check: does it fail the same way every time? Under what conditions?
- Capture: error messages, stack traces, log output, relevant state

Do NOT proceed to Phase 2 until you can reproduce the bug on demand.

### Phase 2: Hypothesize

- Form ONE specific hypothesis: "The bug is caused by X because Y"
- Write the hypothesis down (in the session, not just internally)
- Identify what evidence would confirm or falsify this hypothesis
- Do NOT touch any code during this phase

### Phase 3: Test

- Gather the evidence identified in Phase 2
- Write a failing test that proves the hypothesis IF possible
- Confirm or falsify the hypothesis with evidence, not intuition
- If hypothesis is falsified, return to Phase 2 with a new hypothesis

### Phase 4: Fix

- ONLY after Phase 3 confirms the hypothesis
- Implement the minimal change that fixes the confirmed root cause
- Run the test from Phase 3 to confirm it now passes
- Run the full test suite to confirm no regression

## 3-Failure Cap

If you have attempted 3 fixes and the bug is not resolved: STOP. Do not attempt a 4th fix. Report to the user: which hypotheses were tested, what evidence was gathered, and what remains uncertain. Request human intervention.

This cap is separate from GSD's `node_repair_budget` (which handles plan-level retries). The 3-failure cap applies within a single debugging session.

## Forbidden Patterns

- "Let's just try X" — No fix attempts without a confirmed hypothesis
- "It might be Y, let me change it and see" — Changing code to test a hypothesis is not testing; use logging, assertions, or read-only investigation
- "I'll fix this and the other thing while I'm here" — One fix per cycle. Do not bundle unrelated changes.
