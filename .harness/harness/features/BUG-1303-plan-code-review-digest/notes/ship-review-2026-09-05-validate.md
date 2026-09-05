# BUG-1303 — ship review

**Ship-ready.** All eight success criteria are met at the pinned commit, the reviewer panel closed
with no `must_fix`, and every gate this repository runs is green. One decision is yours before or
after the merge: F-02, below. Nothing is blocking.

**Feature:** BUG-1303-plan-code-review-digest · branch `feat/BUG-1303-plan-code-review-digest` ·
`review_sha` **e2c800f1** (HEAD, tree clean) · base `63404ef0`.

---

## What was wrong, and what shipped

A code reviewer dispatched during the **plan** phase could not return a digest that validated. The
validator had implemented plan-review mode for a while; the reviewer's own persona file never
documented it, so a reviewer following only the contract it was handed wrote a digest the validator
refused. The defect was in the documentation half of a contract whose two halves nobody checked
against each other.

The fix is three things. The reviewer's three contract sources now document the plan-phase form.
`DEC-216` records the general rule — **a persona's documented output block is an enforced half of the
digest contract**, not commentary — and the test suite now enforces it for **all sixteen personas**,
each with its own named pass line, with the persona set derived from the validator's own registry so
a seventeenth persona reddens the suite by name rather than shrinking a still-passing count.

`validate-digest.py` itself was deliberately not touched; the reviewed range contains no file under
`.claude/skills/harness/bin/`, which is SC-04's whole point.

## Where the phases landed

I spawned **no report round**. This briefing is assembled from artifacts already on disk:
`notes/handoff-plan.md`, `notes/handoff-build.md`, `notes/research-BUG-1303-panel-record.md`,
`notes/qa-BUG-1303-build.md`, `notes/research-BUG-1303-goalcheck-validate-c5.md`,
`notes/review-harness-{code-reviewer,qa,security-reviewer,ui-reviewer}-c4.md`, the two c5
confirmation notes, and the run digests `runs/2026-09-05-{08,13,14}-validator/digest.md`,
`runs/2026-09-05-{13,14}-product/digest.md`, `runs/2026-09-05-mf2-eng/digest.md`. The earlier
build-phase digests are represented through the two handoff notes rather than read individually.

- **Plan.** The adversarial panel ran three cycles and closed at cycle 3 with `severity_max: none`,
  both readers `ran`, eleven findings recorded in `plan.yaml`'s `panel:` key and **zero left open**.
  You signed BRIEF and plan with no overrule.
- **Build.** Four tasks, all at station `done`. QA returned FAIL on one thing only — the test-matrix
  floor, not this change's tests, which were green and proven red-capable.
- **The matrix ruling.** That FAIL was the honest one: `test_matrix.bugfix.always` demanded a `unit`
  test, and this bugfix's entire test surface is a contract guard over markdown across two trees —
  integration-shaped by construction. BUG-1128 hit the identical wall and was never ruled. The
  delegated Advisor ruled it as **DEC-217**: bugfix test kinds now follow the changed surface —
  `unit` when the diff touches runtime code, `integration` when the fix is confined to tests and
  contract docs. The main session implemented it. That closes F-01.
- **Validate.** The panel returned **FAIL** with two `must_fix`. Both were real; I re-derived each
  myself before spending the cycle on it.
  - **MF-1 (high)** — the DEC-217 index row carried hand-written tags no regeneration reproduces.
    This reddened the whole `integration` test bucket and made SC-06 literally false at the old pin.
    Regenerated: one row moved, ruling text untouched.
  - **MF-2 (med)** — the new suite retyped the literal `n_a` where SC-03 requires the value be
    derived from the validator's own constant. It now probes the validator's own plan-mode rule
    across `CODE_GRADE_VALUES` and keeps the single member that rule accepts, failing loudly if zero
    or several qualify. I confirmed independently that renaming the grade makes the derivation report
    red rather than silently defaulting.
  - The c5 confirmation pass ruled both **RESOLVED**, `matrix_ok: true`, `code_grade: pass`,
    `must_fix: []`, `severity_max: med`. The security and ui lenses were deliberately not re-run
    (recorded as carried forward with reasons, never presented as having run).

## Goal-check — 8 of 8 met

`notes/research-BUG-1303-goalcheck-validate-c5.md`, graded at `e2c800f1`, content read with
`git show` rather than from the working tree. SC-06 was PARTIAL at the superseded pin and is met at
this one. No success criterion declares `verify: uat`, so **no user acceptance test is required** —
the feature's whole surface is a test suite and three documents.

**Gates, all run by me at the pin:** digest-validator suite exit 0, zero `FAIL` lines, `ALL PASSED` ·
`test-config-shape-matrix.py` 19/19 · `run-unit-tests.sh --kind integration` exit 0 over 46 files ·
index regeneration byte-identical · `check-state.sh` exit 0 · working tree clean.

**Budgets.** 5 rework cycles of 8. **17 runs of a budget of 20** — informational only, and worth a
sentence: the count is high because the plan panel ran three cycles and the validate phase ran a
find-fix-confirm loop. Each run resolved a named finding; none was a retry of an unchanged input.

## The one decision — F-02

DEC-217 introduced two predicates, `touches_runtime_code` and
`fix_confined_to_tests_and_contract_docs`. Its sibling DEC-212 documented its predicate in both QA
skill files **and** asserted that documentation with a test. DEC-217's two are documented in neither.
QA evaluates these names against a diff at gate time out of its preloaded skills; the definitions
live only in `DECISIONS.md`. The code reviewer rated this `high`; the validator lead reconciled it to
`med` because the two predicates are exact complements, so no diff can require zero test kinds — the
reachable harm is a wrongly-chosen kind, not an ungated ship. Both ratings are recorded.

I did not fix it, and no squad could have: both files resolve to `NOBODY` under the domain guard.
It is a main-session-only edit. **Ship now and take it as B-1, or rule it first** — it does not gate.

## Proposed backlog

Unstruck rows become issues on ship acceptance. Anything not listed here dies silently.

| ID | Nature | Row |
|---|---|---|
| B-1 | bug | Document DEC-217's two predicates in `harness-qa-gate/SKILL.md` and `harness-verification-rules/SKILL.md` and assert them in `test-config-shape-matrix.py`, as DEC-212's predicate already is (F-02) |
| B-2 | chore | Reconcile DEC-217's worked example with its own predicates: applied literally to this very diff, `touches_runtime_code` is TRUE via `templates/harness.json`, so the matrix asks for `unit` where the decision's prose says integration. Both kinds are present and green, so nothing is at risk — the wording is |
| B-3 | bug | `harness.json` keeps the `__bug_class__` / `match_bug_class` leg while `test_kinds` defines no such kind — a predicate that can never resolve, which DECISIONS.md:5074 already calls broken elsewhere |
| B-4 | bug | A subagent's job returns `failed (exit 1)` with "yield with null data" while its final message is a complete, valid return — and the job preview can show a superseded draft with the opposite verdict. Hit twice this run; routing on either signal would have discarded correct work or shipped a red gate |
| B-5 | bug | `check-domain.sh` guards `<run_dir>/digest.md` but not `<run_dir>/state.yaml`, and `runs/` is gitignored so a Glob of it looks empty — two leads independently overwrote an earlier run's checkpoint this run. A stray `runs/2026-09-05-01-product/send-back-criteria.md` is also undeletable: my `rm` was correctly refused as out-of-domain |
| B-6 | bug | Worktree path resolution: an agent's injected persona text came from the STALE main-checkout copy, not the worktree's fixed one — the reviewer of a fix to the reviewer's contract was loaded with the pre-fix contract. Same root as `brief-sc:`/`plan-task:` handoff authorities being unusable from a worktree |
| B-7 | chore | `bash-write-guard.sh` parses the command line textually, refusing `plan-merge.py apply --proposal -` when the proposal contains an angle bracket; `amend --value-file -` is not wired to stdin although `apply --proposal -` is |
| B-8 | chore | Dispatch text and docs template `gen-decisions-index.py --apply`; that flag does not exist (exit 2) — the bare invocation is the in-place write. Cost one send-back this run |
| B-9 | enhancement | `_reviewer_plan_mode_results` short-circuits on a derivation error and prints one FAIL line where eight assertions exist — it still gates, but a broken derivation under-reports |
| B-10 | enhancement | SC-02's two discrimination directions share a single report line; both are separately asserted, so this is diagnosability, not ever-greenness |
| B-11 | chore | `harness-qa`'s repository Expertise still says the bugfix floor "stays at unit alone" — false since DEC-217. Fix at the next distillation |

## One thing I could not verify

Test-first ordering for T-01 rests on the main session's own report: commit `cdfce3cb` bundles T-01,
T-02 and T-03, so no git artifact shows the declared red state. Carried from the build handoff
unchanged rather than quietly dropped.
