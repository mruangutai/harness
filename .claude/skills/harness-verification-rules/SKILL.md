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

**Read QA policy at the review pin (D-01, DEC-256).** `test_matrix` and `test_kinds` come from the
**reviewed repository's** own `harness.json`, in that repository's `.harness` directory, at its
review pin — never the control plane's copy, the current tree, a default branch or a planning
tree; read `change_type` from each PLAN task.

1. **Repository.** A feature whose `feature.json` binds `factory.repo` reviews that fleet
   repository's code checkout — locate it with `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/feature-worktree.py
   path --repo <owner/repo> --id <feature-id>`, its `CODE` line. An unbound Harness feature
   reviews the repository holding the feature.
2. **Commit.** `feature.json`'s `review_sha` names it; a dispatch review pin must resolve to the same
   commit in that repository.
3. **Blob.** Read that file at the commit with `git show <commit>:<path>` — never either
   checkout's current config — and record the repository, the full commit and the path in your
   artifact.

If the pin, the repository or the blob is missing or invalid, **stop and say so** with
`VERDICT: BLOCKED` and `kinds: []` — there is no fallback, and `validate-digest.py` refuses every
other QA return it cannot check against the pin. Do not invent a matrix. INV-49 only requires a
BRIEF to disclose, under `## Verification gaps`, a criterion that rests on a kind with no runner;
that disclosure never waives the kind. The
contract and its rationale: `<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness/docs/SPEC.md` §9 and
DEC-256, DEC-187 and DEC-212 in `<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness/docs/DECISIONS.md`.

You may **add** a requirement the diff clearly warrants. You may never drop below the matrix.
`validate-digest.py` applies three gates over the started tasks' `always` kinds:

1. Every kind you report is checked against its configured `status`, under every verdict.
2. An omitted `always` kind that is `unresolved`, or `active` with no `cmd`, is refused under every
   verdict — omission is never exclusion.
3. A `PASS` with `matrix_ok: true` must report every non-excluded `always` kind as `satisfied`.

An omission on an early `BLOCKED` or `FAIL` is neither a soft skip nor proof of coverage. You
evaluate the `when:` predicates yourself (DEC-212); report every applicable kind, and one that is
`unresolved` or has no `cmd` as `misconfigured` with `VERDICT: BLOCKED`.

**Presence is not satisfied by an unrelated existing test.** A new endpoint is not covered because a
different endpoint has one. Find the test exercising *this* change, or the kind is missing.

**A `config` task that changes a value's shape** (a key's container type, required-ness, or
structural nesting in a config a gate script reads) **trips `touches_config_shape` and requires
`integration`** (DEC-212) — a value tweak does not.

## Your run is recorded once, as runner receipts (DEC-255)

Running the matrix is yours; `validate-digest.py` no longer runs it again. A `PASS` with
`suite: pass` and `matrix_ok: true` is accepted only with a runner receipt for every satisfied
claimed active `unit`/`integration` kind, at your validator-lead run's
`runs/<run-id>/qa/manifest-<kind>.json`, written by DEC-255's production runner command from your
managed review-pin checkout (a fix run: the fixed tip, clean outside the feature's own
directory). An empty `kinds:` is refused, never read as "all". Each kind runs once; a receipt is
never hand-edited. A refusal names every bad receipt and the exact repair command — run it, never
route around it. The steps and who commits what:
`<HARNESS_CONTROL_PLANE_ROOT>/.omp/agents/harness-qa.md` § Runner receipts.

**Candidate versus installed.** When the diff changes a gate or hook, the copy enforcing your own
run is the installed control-plane one, not the candidate at the pin. Record the host launcher's
path, version and hash beside the candidate's source pin, prove candidate behavior only with
tests run from `review_sha`, and never claim the installed hook behaved as the candidate does.
You still produce candidate receipts for main to commit; the host is not redeployed mid-run.

## Resolve each kind to exactly one of five states

Read **two** signals, never just the exit code: what kind of failure, not merely whether it failed.
Report each as `kinds: [{ kind, state, … }]` with `state` spelled as below; `validate-digest.py`
refuses a state the pinned `harness.json` contradicts and `misconfigured` under any verdict but
`BLOCKED`. Only `status: excluded` takes a kind out of the required set; a null `cmd` alone never
does.

| `state` | Signals | Result |
|---|---|---|
| `satisfied` | a named test ran, none failed | contributes to `PASS` |
| `missing` | required, and nothing covers this change | **`FAIL`** |
| `not_applicable` | `test_kinds.<kind>.status == "excluded"` with its `excluded_because` and `signed` decision — the tooling genuinely is absent. No other status may report it | **soft skip.** Report it; do not FAIL |
| `locally_run` | `test_kinds.<kind>.status == "locally_run"` (issue #1187) — a real `cmd` that cannot run in CI (needs a host and live credentials). No other status may report it | **not FAIL, not a soft skip.** If the change touched this kind's `detect` surface, require a recorded run under the feature's `notes/`; absent that note, `BLOCKED — locally-run kind '<kind>' has no recorded run` |
| `misconfigured` | a required kind is `status: unresolved`, or `active` with a null/absent `cmd` · no test files matched · the failure is a **load / import / collection / syntax error** rather than an assertion | **`BLOCKED`** — never `FAIL`. For an unresolved or cmd-less kind, name both repairs: give it `status: active` with a runnable `cmd`, or `status: excluded` with `excluded_because` and `signed: DEC-NNN` |

⚠️ **Do not use "zero tests collected" to detect misconfiguration.** `node --test src/` reports
`tests 1 / fail 1` for a module-load error. **The failure kind is the signal.**

A genuine `FAIL` looks like a **named** test with an assertion diff. Misconfiguration looks like
`MODULE_NOT_FOUND`, `ImportError`, `No test files found`, a collection `ERROR`, or a "test" whose name is
a file path.

**Need the tree at the pin?** MUST read
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/references/review-checkout.md` before creating
it. Use only `pinned-checkout.py`; remove your pin on **every return** (DEC-238).

**A pin holds only the feature it is keyed on (FEAT-1559).** Read any other feature by absolute
path under the control-plane root, by its concrete id — for example
`<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness/features/FEAT-9-example/<file>`; it is
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
with no fail-first evidence is `FAIL`, not `PASS`, unless the trusted runtime feature's readable
BRIEF explicitly marks every SC `inspection` or `uat` in its own continuation block. Missing,
ambiguous or mismatched feature context and unknown/missing modes do not earn that exemption.
Every SC declaration must parse completely and carry exactly one `verify:` annotation whose
entire value is `inspection` or `uat`; every annotation must belong to a parsed criterion.
Noncanonical SC-bearing list items or headings, including checkbox and decorated labels,
are ambiguous and never grant a waiver; unstructured prose references remain permitted.
BRIEF must be a regular feature-local file, not a symlink borrowing another feature's criteria.
Its canonical registration must be a regular file, reside in that same
physical feature directory and belong to the selected checkout; a nested linked checkout is
still foreign. Unreadable or unresolved/nonreciprocal checkout metadata grants no
waiver, including when dispatch starts inside a linked checkout (DEC-95, DEC-208).
For automated criteria, passing today does not prove the test ever failed.

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
Every Phase 1 expectation with no test belongs in `coverage_gaps`. An adversarial or malformed-input
expectation for code where no input crosses a trust boundary is neither a coverage gap nor a
finding (`harness-tdd-enforcement` § Plausible inputs). `task` and `task_verify` bind
the five dev specialists only; the validator refuses them on a qa return (SC-05).

## Red flags

| Thought | Reality |
|---|---|
| "The suite is green, so this passes" | Green proves existing tests pass. Nothing about *this* change |
| "I'll read the code first, it's faster" | Then Phase 1 is worthless. You will test what it does, not what was asked |
| "There's a test in that file already" | Does it exercise *this* behaviour? If not, missing |
| "The test passes, so the criterion is proven" | Passing is not exclusion. Name the mutant, flip it, confirm it reddens |
| "The tests were written first, I'll just say so" | Saying so is a claim. `fail_first` wants the receipt: the path or line that shows the red run |
