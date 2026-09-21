---
name: harness-systematic-debugging
description: Four-phase debugging protocol — reproduce before hypothesizing, hypothesize before touching code, confirm with evidence before fixing, and stop after three failed fixes. Loaded by the engineering specialists when working a bug.
user-invocable: false
---

# Systematic Debugging

**Evidence before fixes. A hypothesis before code changes.**

## Phase 1 — Observe

- **Reproduce it consistently** before changing anything.
- Document the exact failure: input, expected, actual.
- Does it fail the same way every time? Under what conditions does it *not* fail?
- Capture error messages, stack traces, logs, relevant state.

**Do not proceed until you can reproduce on demand.** A fix for a bug you cannot reproduce is a guess you
will not be able to verify, and you will not know whether it worked or the bug simply hid.

## Phase 2 — Hypothesize

- Form **one** specific hypothesis: *"The bug is caused by X because Y."*
- **Write it down** in your artifact, not just internally. An unstated hypothesis drifts to fit whatever
  you find next.
- State what evidence would **falsify** it, not only what would confirm it.
- **Touch no code in this phase.**

## Phase 3 — Test the hypothesis

- Gather the evidence you identified. Use logging, assertions, or read-only investigation.
- **Write a failing test that demonstrates the root cause** where possible — you need it in Phase 4 anyway,
  and it is what proves the fix worked rather than coincided.
- Confirm or falsify with evidence, not intuition.
- **Falsified? Return to Phase 2** with a new hypothesis. That is the protocol working, not a setback.

## Phase 4 — Fix

Only after Phase 3 **confirms**.

- Implement the **minimal** change addressing the confirmed root cause.
- Run the Phase 3 test — it must now pass.
- Run the full suite to confirm no regression.
- The regression test must match the bug's class: a functional bug needs a functional test, a UI bug a
  browser test. A unit test for a UI bug proves nothing about the UI.
- **Never add a guard to silence a crash.** A nil check that makes the symptom disappear is a symptom
  fix; the root cause is still there. A workaround that needs a paragraph of comment to justify it is
  the code being wrong — fix the code, not the comment.
- **Fix the pattern, not the instance.** Grep for siblings of the confirmed cause and fix every
  occurrence in the same cycle; the instance you reproduced is rarely the only one.
- **A bug that appears after restart: suspect stale persistent state before code** — config files,
  caches, lock files, serialized state. If clearing a state file restores behaviour, state validation
  is the fix.

## The three-failure cap

**After three attempted fixes that do not resolve it: stop. Do not attempt a fourth.**

Return `BLOCKED` reporting which hypotheses you tested, what evidence you gathered, and what remains
uncertain. Escalate.

Three failures means your model of the system is wrong, not that you need another attempt. The fourth
attempt is where speculative changes start accumulating and the original bug gets buried under new ones.
Two failed fixes that share one premise are evidence about the premise
(`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-craft/references/attack-the-premise.md`) —
question it before the third.

## Red flags

| Thought | Reality |
|---|---|
| "Let's just try X" | No code change without a confirmed hypothesis. Changing code to test one is not testing — use logging or read-only investigation |
| "I'll fix this and that other thing while I'm here" | One fix per cycle. Never bundle unrelated changes into a debugging fix |
| "The test is wrong, not the code" | Sometimes true — but prove it with evidence, do not assume it because the code looks right |
| "I'll add a fix and a test together" | Then the test was written to pass, not to catch the bug |
| "It's obviously the null check" | Obvious hypotheses still need Phase 3. Obvious and wrong is common |
| "I'll skip reproduction, the stack trace is clear" | A stack trace shows where it surfaced, not where it originated |
