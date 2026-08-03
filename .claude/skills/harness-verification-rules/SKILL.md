---
name: harness-verification-rules
description: Verification discipline for QA — enforce the test matrix against the diff, resolve each test kind to one of four states, audit test-first compliance, and supply the evidence the goal-check consumes. Loaded by harness-qa.
user-invocable: false
---

# Verification Rules

You write tests, run them, and **gate**. Enforced against **the diff**, never against a self-report.

There is no separate verifier downstream of you. If you do not catch it, it ships.

## Two phases, in order — the first is anti-bias

**Phase 1 — derive expected coverage with NO source access.** Read `BRIEF.md` and `PLAN.md` only. From
the requirements and success criteria alone, write down what tests *should* exist.

Do this first because once you have read the implementation you will unconsciously test what the code
does rather than what was asked for — and a test suite that mirrors the implementation cannot detect that
the implementation is wrong.

**Phase 2 — read the code.** Write and run tests, enforce the matrix, report gaps against your Phase 1
list. A gap between the two is a finding, not an oversight to quietly close.

## The matrix is a floor

Read `test_matrix` and `test_kinds` from `.harness/harness.json`; read `change_type` from each PLAN task.
If `harness.json` is absent, **stop and say so** — do not invent a matrix.

You may **add** a requirement the diff clearly warrants. You may never drop below the matrix.

**Presence is not satisfied by an unrelated existing test.** A new endpoint is not covered because a
different endpoint has one. Find the test exercising *this* change, or the kind is missing.

## Resolve each kind to exactly one of four states

Read **two** signals, never just the exit code: what kind of failure, not merely whether it failed.

| State | Signals | Result |
|---|---|---|
| **satisfied** | a named test ran, none failed | contributes to `PASS` |
| **missing** | required, and nothing covers this change | **`FAIL`** |
| **not applicable** | the tooling genuinely is absent (e.g. `ui` with no Playwright) | **soft skip.** Report it; do not FAIL |
| **misconfigured** | `cmd` is null/absent · no test files matched · the failure is a **load / import / collection / syntax error** rather than an assertion | **`BLOCKED`** — never `FAIL` |

**An absence assertion is never a check on its own (DEC-169).** For every "X is gone" assertion,
name the presence assertion beside it — `sed -d` satisfies an absence-grep completely and can delete
the thing that had to stay. Demonstrated live: SC-13's grep passed on a variant that removed two
load-bearing rows.

⚠️ **Do not use "zero tests collected" to detect misconfiguration.** `node --test src/` reports
`tests 1 / fail 1` for a module-load error. **The failure kind is the signal.**

A genuine `FAIL` looks like a **named** test with an assertion diff. Misconfiguration looks like
`MODULE_NOT_FOUND`, `ImportError`, `No test files found`, a collection `ERROR`, or a "test" whose name is
a file path.

Blocking legitimate non-web work on a missing browser is a bug. Passing a hard gate because its command
was broken is worse than halting.

## Audit test-first compliance

Beyond presence: for each behavioural change in the diff, confirm a test covers it, and where git history
shows the order, confirm the test came **first**. Report violations as findings — they do not by
themselves fail the gate.

**Perturbation proofs run in a worktree, never the main checkout (DEC-153).** Proving a test
discriminates (mutate, watch it fail, restore) is sanctioned — but the bash-write-guard denies your
in-place source edits in the main checkout by design. Run the proof in a disposable worktree
(`isolation: worktree`, or `git worktree add`); verify the restore with
`git status --porcelain <path>`, never a read-back.

## You supply the evidence, not the verdict on the goal

`pm` goal-checks success criteria by **collecting** evidence rather than re-testing. For every SC marked
`verify: automated`, pm needs to cite the specific test that exercises it — so your DIGEST must make that
findable.

**A passing suite is not a met SC.** If no test exercises `SC-03`, say so: the gap returns to a dev, not
to the user.

## Your DIGEST

```yaml
suite: pass|fail|n/a           # n/a ONLY if the suite could not be run at all
failures: <n>
coverage_gaps: [<area>]        # incl. any Phase 1 expectation with no test
matrix_ok: <bool>|n/a          # a BOOL. "mostly" is a contract violation.
                               # n/a ONLY if the matrix could not be evaluated;
                               # n/a with VERDICT: PASS is rejected — DEC-173
```

## Red flags

| Thought | Reality |
|---|---|
| "The suite is green, so this passes" | Green proves existing tests pass. Nothing about *this* change |
| "I'll read the code first, it's faster" | Then Phase 1 is worthless. You will test what it does, not what was asked |
| "Non-zero exit means the tests failed" | Check the failure kind. A load error is `BLOCKED`, not `FAIL` |
| "Playwright is missing, so ui fails" | Absent tooling is a soft skip |
| "The command errors, I'll skip that kind" | That is `BLOCKED`, loudly |
| "Small change, the matrix is overkill" | The matrix is a floor. Size is not a change type |
| "There's a test in that file already" | Does it exercise *this* behaviour? If not, missing |
