---
name: harness-verification-rules
description: Verification discipline for QA — enforce the test matrix against the diff, resolve each test kind to one of five states, audit test-first compliance, and supply the evidence the goal-check consumes. Loaded by harness-qa.
user-invocable: false
---

# Verification Rules

You write tests, run them, and **gate**. Enforced against **the diff**, never against a self-report.

## Two phases, in order — the first is anti-bias

**Phase 1 — derive expected coverage with NO source access.** Read `BRIEF.md` and the plan only —
`plan.yaml` (legacy features: `PLAN.md`). From the requirements and success criteria alone, write
down what tests *should* exist. A suite written after reading the implementation mirrors it and
cannot detect that the implementation is wrong.

**Phase 2 — read the code.** Write and run tests, enforce the matrix, report gaps against your Phase 1
list. A gap between the two is a finding, not an oversight to quietly close.

## The matrix is a floor

Read `test_matrix` and `test_kinds` from `<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness.json`; read `change_type` from each PLAN task.
If `harness.json` is absent, **stop and say so** — do not invent a matrix.

You may **add** a requirement the diff clearly warrants. You may never drop below the matrix:
`validate-digest.py` refuses a `PASS` with `matrix_ok: true` whose `kinds:` does not report every
`always` kind for the plan's tasks as `satisfied`; the `when:` kinds remain your call.

**Presence is not satisfied by an unrelated existing test.** A new endpoint is not covered because a
different endpoint has one. Find the test exercising *this* change, or the kind is missing.

**A `config` task that changes a value's shape** (a key's container type, required-ness, or
structural nesting in a config a gate script reads) **trips `touches_config_shape` and requires
`integration`** (DEC-212) — a value tweak does not.

## Resolve each kind to exactly one of five states

Read **two** signals, never just the exit code: what kind of failure, not merely whether it failed.
Report each as `kinds: [{ kind, state, … }]` with `state` spelled as below; `validate-digest.py`
refuses a state `harness.json` contradicts and `misconfigured` under any verdict but `BLOCKED`.

| `state` | Signals | Result |
|---|---|---|
| `satisfied` | a named test ran, none failed | contributes to `PASS` |
| `missing` | required, and nothing covers this change | **`FAIL`** |
| `not_applicable` | `test_kinds.<kind>.status == "excluded"` — the tooling genuinely is absent | **soft skip.** Report it; do not FAIL |
| `locally_run` | `test_kinds.<kind>.status == "locally_run"` (issue #1187) — a real `cmd` that cannot run in CI (needs a host and live credentials) | **not FAIL, not a soft skip.** If the change touched this kind's `detect` surface, require a recorded run under the feature's `notes/`; absent that note, `BLOCKED — locally-run kind '<kind>' has no recorded run` |
| `misconfigured` | `cmd` is null/absent on an active kind · no test files matched · the failure is a **load / import / collection / syntax error** rather than an assertion | **`BLOCKED`** — never `FAIL` |

⚠️ **Do not use "zero tests collected" to detect misconfiguration.** `node --test src/` reports
`tests 1 / fail 1` for a module-load error. **The failure kind is the signal.**

A genuine `FAIL` looks like a **named** test with an assertion diff. Misconfiguration looks like
`MODULE_NOT_FOUND`, `ImportError`, `No test files found`, a collection `ERROR`, or a "test" whose name is
a file path.

**Need the tree at the pin?** MUST read
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/references/review-checkout.md` before creating
it. Use only `pinned-checkout.py`, never a bare `git worktree add`; each reader gets its own
feature/run/persona-keyed pin. Do not alter the primary checkout or its dirty changes to reach it.
Copy evidence to the feature's `runs/<run-id>/` before removal; remove your pin on **every return**,
including external fleet repositories — sibling isolation and cleanup cannot rely on a fleet hook
(DEC-238, #1994).

**A pin holds only the feature it is keyed on (FEAT-1559).** Read any other feature by absolute
path under the control-plane root, by its concrete id — for example
`<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness/features/FEAT-23-ship-flow-fixes/BRIEF.md`; it is
not in the pin, and an in-progress sibling worktree is never evidence. Layout evidence is
`worktree-state.py --verify --checkout <pin>` exiting 0. A post-checkout, post-merge or post-rewrite
hook that ran quietly proves nothing: those hooks always exit 0, and `core.hooksPath` is local
configuration that a fresh clone does not carry. Structural `cone (3)`, `skip-bits (4)` and
`materialisation (7)` refuse an audit; `dirty (8)` alone is reported and does not. Pre-change
evidence names an immutable SHA, never a moving ref such as `main` or a merge-base taken later.
Layout savings are counted in files and feature directories, never as a `du` byte delta.

## Audit test-first compliance

Beyond presence: for each behavioural change in the diff, confirm a test covers it, and where git history
shows the order, confirm the test came **first**. Report violations in your artifact and
`coverage_gaps` — they never fail the gate by themselves; `validate-digest.py` refuses a `FAIL`
whose suite, matrix and failure count are all green.

**Fail-first evidence is a gate, not an audit note (FEAT-59 SC-17).** For every SC marked
`verify: automated`, your digest names the test and the evidence that it **failed before the fix** —
the path of the captured failing run, or the receipt line that records it (`1 failed before 3f2a9c1`).
Where the fix and its test landed together, the capture you cite is your own reproduction. A green suite
with no fail-first evidence is `FAIL`, not `PASS`: passing proves the tests pass today, and a test that
never failed constrains nothing.

**Perturbation proofs run in a worktree, never the main checkout (DEC-153).** Proving a test
discriminates (mutate, watch it fail, restore) is sanctioned — but the bash-write-guard denies your
in-place source edits in the main checkout by design. Run the proof in the same pinned
checkout as the lane (the managed procedure above); verify the restore with
`git status --porcelain <path>`, never a read-back.

## Absence, subject and mutant (DEC-169, issue #979)

An absence assertion is never a check on its own, and a criterion that excludes a specific wrong
implementation names its mutant, which you flip. The one canonical block — the presence pairing, the
two subject-binding questions, fixture provenance and measurement mode — is
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-code-review/SKILL.md` § Absence, subject and mutant.
MUST read it in Phase 2 before you sign off any criterion or added test.

## You supply the evidence, not the verdict on the goal

`pm` **collects**, never reruns, evidence: your digest must identify the specific test exercising
each `verify: automated` SC (DEC-73). A passing suite is not a met SC: name any uncovered SC;
the gap returns to the owning dev, not the user.

## Your DIGEST

MUST read `<HARNESS_CONTROL_PLANE_ROOT>/.omp/agents/harness-qa.md` § Output before returning;
it points to the canonical schema, including `matrix_ok`'s allowed values and verdict pairings
(DEC-237). `validate-digest.py` refuses a digest that breaks the contract and names the field,
the rejected pairing and the repair — read its message, never guess a value.
Every Phase 1 expectation with no test belongs in `coverage_gaps`. `task` and `task_verify` bind
the five dev specialists only; the validator refuses them on a qa return (SC-05).

## Red flags

| Thought | Reality |
|---|---|
| "The suite is green, so this passes" | Green proves existing tests pass. Nothing about *this* change |
| "I'll read the code first, it's faster" | Then Phase 1 is worthless. You will test what it does, not what was asked |
| "There's a test in that file already" | Does it exercise *this* behaviour? If not, missing |
| "The test passes, so the criterion is proven" | Passing is not exclusion. Name the mutant, flip it, confirm it reddens |
| "The tests were written first, I'll just say so" | Saying so is a claim. `fail_first` wants the receipt: the path or line that shows the red run |
