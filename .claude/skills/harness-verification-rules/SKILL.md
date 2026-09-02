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
`plan.yaml`, or `PLAN.md` for a feature still on the pre-DEC-182 format. From
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

## Every criterion names its mutant, and its subject (issue #979)

Nine real instances shipped past review because an assertion's subject was not the thing it
claimed to bind: prose about a mechanism, not the mechanism; a stub, not the collaborator; a
substring, not the count; a comparison that is false either way, not the operator under test. None
failed loudly — all read as passing verification while verifying nothing.

**Any criterion claiming to exclude a specific wrong implementation must name the mutant and be
provable by flipping it.** A signed criterion asserting `>=` where the code only ever exercised
`>` with a value the comparison is true either way for excludes nothing — measured live: an
under-threshold test fixture whose value made both `28614 > 200000` and `28614 >= 200000` false,
so the operator could be swapped and nothing reddened. Before signing off a criterion that names an
operator, a threshold, or an exclusion, mutate the code to the wrong alternative and confirm the
named test reddens. This is the single question in this defect class with the most teeth — ask it
of every new assertion, not only the ones that feel risky.

**Fixture provenance.** A fixture standing in for a nested or externally-produced artifact must
name what it was captured *from* — depth, shape, or mode. A fixture captured from a main-session
run is not proof of a nested-subagent path; if the plan or the code needs the nested case, demand a
fixture that says so, not one that is merely present.

**Measurement mode.** A claim about host or environment behaviour (a resolved package version, a
binary's location) is only as good as the mode it was measured under — `bun run` and `bun test`
resolved three different copies of the same package in this project's own history. If a coverage
gap or an added test depends on measuring the real host, state the mode next to the claim; do not
accept a claim measured under one execution mode as covering another.

## You supply the evidence, not the verdict on the goal

`pm` goal-checks success criteria by **collecting** evidence rather than re-testing. For every SC marked
`verify: automated`, pm needs to cite the specific test that exercises it — so your DIGEST must make that
findable.

**A passing suite is not a met SC.** If no test exercises `SC-03`, say so: the gap returns to a dev, not
to the user.

## Your DIGEST

```yaml
suite: pass|fail|n/a           # n/a ONLY if the suite could not be run at all.
                               # `suite: fail` with VERDICT: PASS is rejected — a gate that
                               # FAILED cannot have passed, and saying so honestly while
                               # claiming PASS is the same fail-open as declining to say
failures: <n>
coverage_gaps: [<area>]        # incl. any Phase 1 expectation with no test
matrix_ok: <bool>|n/a          # a BOOL. "mostly" is a contract violation.
                               # n/a ONLY if the matrix could not be evaluated;
                               # n/a with VERDICT: PASS is rejected — DEC-173.
                               # `matrix_ok: false` with VERDICT: PASS is rejected too, and
                               # the BOOLEAN spelling is the reason it needed its own gate:
                               # one keyed on the string "fail" never fires here (DEC-175)
```

**You gain neither `task` nor `task_verify`.** Those bind the five dev specialists only. Adding
either to a qa return is the schema leak SC-05 exists to catch.

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
| "The test passes, so the criterion is proven" | Passing is not exclusion. Name the mutant, flip it, confirm it reddens |
