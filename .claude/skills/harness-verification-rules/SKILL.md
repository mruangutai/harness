---
name: harness-verification-rules
description: Verification discipline for QA — enforce the test matrix against the diff, resolve each test kind to one of five states, audit test-first compliance, and supply the evidence the goal-check consumes. Loaded by harness-qa.
user-invocable: false
---

# Verification Rules

You write tests, run them, and **gate**. Enforced against **the diff**, never against a self-report.

There is no separate verifier downstream of you. If you do not catch it, it ships.

## Two phases, in order — the first is anti-bias

**Phase 1 — derive expected coverage with NO source access.** Read `BRIEF.md` and the plan only —
`plan.yaml` (legacy features: `PLAN.md`). From the requirements and success criteria alone, write
down what tests *should* exist.

Do this first because once you have read the implementation you will unconsciously test what the code
does rather than what was asked for — and a test suite that mirrors the implementation cannot detect that
the implementation is wrong.

**Phase 2 — read the code.** Write and run tests, enforce the matrix, report gaps against your Phase 1
list. A gap between the two is a finding, not an oversight to quietly close.

## The matrix is a floor

Read `test_matrix` and `test_kinds` from `<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness.json`; read `change_type` from each PLAN task.
If `harness.json` is absent, **stop and say so** — do not invent a matrix.

You may **add** a requirement the diff clearly warrants. You may never drop below the matrix.

**Presence is not satisfied by an unrelated existing test.** A new endpoint is not covered because a
different endpoint has one. Find the test exercising *this* change, or the kind is missing.

**A `config` task that changes a value's shape** (a key's container type, required-ness, or
structural nesting in a config a gate script reads) **trips `touches_config_shape` and requires
`integration`** (DEC-212) — a value tweak does not.

## Resolve each kind to exactly one of five states

Read **two** signals, never just the exit code: what kind of failure, not merely whether it failed.

| State | Signals | Result |
|---|---|---|
| **satisfied** | a named test ran, none failed | contributes to `PASS` |
| **missing** | required, and nothing covers this change | **`FAIL`** |
| **not applicable** | the tooling genuinely is absent (e.g. `ui` with no Playwright) | **soft skip.** Report it; do not FAIL |
| **locally-run** | `test_kinds.<kind>.status == "locally_run"` (issue #1187) — a real `cmd` that cannot run in CI (needs a host and live credentials) | **not FAIL, not a soft skip.** If the change touched this kind's `detect` surface, require a recorded run under the feature's `notes/`; absent that note, `BLOCKED — locally-run kind '<kind>' has no recorded run` |
| **misconfigured** | `cmd` is null/absent · no test files matched · the failure is a **load / import / collection / syntax error** rather than an assertion | **`BLOCKED`** — never `FAIL` |

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

**Fail-first evidence is a gate, not an audit note (FEAT-59 SC-17).** For every SC marked
`verify: automated`, your digest names the test and the evidence that it **failed before the fix** —
the path of the captured failing run, or the receipt line that records it (`1 failed before 3f2a9c1`).
Where the fix and its test landed together, reproduce the failing state in a worktree (revert the
production change, run the test, capture the output, restore) and cite that capture. A green suite
with no fail-first evidence is `FAIL`, not `PASS`: passing proves the tests pass today, and a test that
never failed constrains nothing.

**Perturbation proofs run in a worktree, never the main checkout (DEC-153).** Proving a test
discriminates (mutate, watch it fail, restore) is sanctioned — but the bash-write-guard denies your
in-place source edits in the main checkout by design. Run the proof in a disposable worktree
(`isolation: worktree`, or `git worktree add`); verify the restore with
`git status --porcelain <path>`, never a read-back.

## Absence, subject and mutant (DEC-169, issue #979)

An absence assertion is never a check on its own, and a criterion that excludes a specific wrong
implementation names its mutant, which you flip. The one canonical block — the presence pairing, the
two subject-binding questions, fixture provenance and measurement mode — is
`harness-code-review` § Absence, subject and mutant.
Read it in Phase 2 before you sign off any criterion or added test.

## You supply the evidence, not the verdict on the goal

`pm` goal-checks success criteria by **collecting** evidence rather than re-testing. For every SC marked
`verify: automated`, pm needs to cite the specific test that exercises it — so your DIGEST must make that
findable.

**A passing suite is not a met SC.** If no test exercises `SC-03`, say so: the gap returns to a dev, not
to the user.

## Your DIGEST

The documented contract is `<HARNESS_CONTROL_PLANE_ROOT>/.omp/agents/harness-qa.md § Output`; `validate-digest.py` refuses a
digest that breaks it and names the field, the rejected pairing and the repair — read its message,
never guess a value. Your fields: `suite`, `failures`, `coverage_gaps` (every Phase 1 expectation
with no test is one), `matrix_ok` (a bool), `fail_first` (one `{ sc, evidence }` per
`verify: automated` SC), plus `kinds` and `sc_evidence`. `task` and `task_verify` bind the five dev
specialists only; the validator refuses them on a qa return (SC-05).

## Red flags

| Thought | Reality |
|---|---|
| "The suite is green, so this passes" | Green proves existing tests pass. Nothing about *this* change |
| "I'll read the code first, it's faster" | Then Phase 1 is worthless. You will test what it does, not what was asked |
| "There's a test in that file already" | Does it exercise *this* behaviour? If not, missing |
| "The test passes, so the criterion is proven" | Passing is not exclusion. Name the mutant, flip it, confirm it reddens |
| "The tests were written first, I'll just say so" | Saying so is a claim. `fail_first` wants the receipt: the path or line that shows the red run |
