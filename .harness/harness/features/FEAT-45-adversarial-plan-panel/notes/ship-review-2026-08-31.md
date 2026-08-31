# FEAT-45 — adversarial plan panel: ship review

**Recommendation: ship it.** Every criterion that disk can settle is met — 14 of 17. Nothing is
unmet. The remaining three cannot be settled by any agent: they need one live `/harness-plan` and
your own judgement, and the criteria say so in their own words. Shipping is what makes that run
possible.

**One thing to accept knowingly.** The fix that lets a code reviewer return from a worktree is
present and correct by inspection, but it **cannot be proven until the branch merges**, because the
hook executes `main`'s installed copy of the validator, not the branch's. That is a property of how
hooks resolve, not a defect in the work. You have already ruled this a conditional close; it is
recorded below as a required post-merge check so it cannot quietly lapse.

**How this briefing was assembled.** No report round was spawned — the leads' digests were read from
disk, per DEC-69. Sources: `runs/2026-08-29-01-brief-product/`, `2026-08-29-1-arch-eng/`,
`2026-08-29-2-plan-product/`, `2026-08-29-1-simplify-eng/`, `2026-08-29-1-uiscope-validator/`,
`2026-08-29-1-planfix-product/`, `2026-08-30-1-product/`, `2026-08-31-01-product/`,
`2026-08-31-01-eng/`, `2026-08-31-1-eng/`, `2026-08-31-1-validator/`, `2026-08-31-01-validator/`,
`2026-08-31-02-validator/`, `c3-validator/`, `simplify-eng/`, plus `notes/qa-feat45-c0.md`,
`notes/research-FEAT-45-goalcheck-final.md` and the twelve `notes/review-harness-*-c{0,1,2,3}.md`.
**One source is missing and it matters:** the cycle-0 lead digest was destroyed when the cycle-2
panel reused its run directory. Its findings survive in STATE.md and the commit record; the digest
itself does not.

## What was built

An adversarial reader panel that runs in the plan phase, before any code exists. Twelve tasks:
a new team definition, three reader prompts wired into the plan door and the orchestrator playbook,
a content-hash identity for panel findings (`panel_findings.py`), a new signature gate (INV-32 in
`check-state.sh`), and two signed decisions — DEC-206 (a lead may wrap a non-harness reader and owns
its shape but never its content) and DEC-207 (a gate may grade a specification, not a diff).

## Where each squad landed

- **Product** — wrote the BRIEF and plan, adjudicated a mid-build plan gap, and ran both goal-checks.
  The final grade is 14 met / 0 unmet / 3 deferred (`notes/research-FEAT-45-goalcheck-final.md`).
- **Engineering** — delivered five build tasks and three fix cycles. Its own SIMPLIFY pass ran all
  four angles and applied nothing, which is a real outcome and was recorded as one
  (`runs/simplify-eng/digest.md`).
- **Validation** — the QA gate passed the test matrix (`notes/qa-feat45-c0.md`), and the reviewer
  panel ran four times. It earned its keep: it found the gating defect described next.

## The finding that justified the whole exercise

The gate this feature ships **failed open on exactly the input its own signed decision names as the
risk**. `check-state.sh` defaulted a missing panel-finding severity to the empty string, which was in
no gating set — so a finding whose rating was lost would have reached your signature un-vetted, while
DEC-206, written in the same change, promised verbatim that a lost rating withholds. Caught at
cycle 0, fixed, and the fix was proven able to fail by reverting it and watching the test go red.

A second one is worth your attention because it was invisible: for one pinned commit the **test gate
was collecting zero tests**. Three registrations named files `main` had retired; the runner exited
before collecting anything. Every "suite is green" claim at that pin — mine included — was a
standalone script run, not a gate run. Fixed; discovery is now 57 registered scripts and 433 result
lines against 2 lines while dead.

## Deferred, and why — these are not failures

| Criterion | Why no agent can settle it |
|---|---|
| SC-11 | "On a live plan, the operator judges each of the three readers to have earned its spawn" |
| SC-12 | "On a live plan whose panel raises nothing at `high`, the operator reaches the signature" |
| SC-16 | "On the first live `/harness-plan` after this ships" — its own text defers it |
| F5/V1 | The executing hook resolves `main`'s validator, so the fix cannot run pre-merge |

**Required post-merge check:** the first reviewer dispatch after merge must be confirmed to land a
structured return. That single run also settles SC-11, SC-12 and SC-16.

## Proposed backlog — strike any row by ID; anything not listed dies silently

| ID | Nature | Item |
|---|---|---|
| B-2 | bug | `_hook_feature_dir` falls back silently to `owner_root` on any registry miss with no existence check. Not the cause of the observed failure, but a real hole |
| B-3 | bug | `code-grade.py` raises an unhandled `RuntimeError` on any path new in the graded diff — exits 1 with zero `RESULT: FAIL` lines, reddening a clean range and able to mask a real failure behind a crash |
| B-4 | bug | Five structured returns came back empty or null across this feature and were only recovered because leads re-measured. `validate-digest.py`'s stop hook did not stop them |
| B-5 | bug | Agents wrote feature artifacts into the **main checkout** rather than their worktree six times; three existed nowhere else. All recovered by hand |
| B-6 | bug | A lead reusing a run directory across cycles overwrote an earlier lead digest, destroying the cycle-0 record |
| B-7 | bug | INV-26 is structurally red for the whole Building phase, and both shapes are produced by the mirror's own writers |
| B-8 | chore | SC-04/05/07/13/17 declare `evidence: unit`, but their proofs live in `test-check-state.py`, which is in `INTEGRATION_SCRIPTS` — so the invocation SC-08 names never runs them. The proofs exist; the label is wrong |
| B-9 | bug | `test-validate-digest.py` passes an explicit `feature_dir` — the very parameter the F1 forgery manipulated — so the test could not fail on the defect it appeared to cover. `check_hook_feature_dir` similarly monkeypatches the lookup |
| B-10 | chore | DEC number allocation has no cross-branch check; `main` landed a DEC-205 after this branch was cut and the collision was caught by hand |
| B-11 | chore | `plan-panel.yaml` restates the validator lead's transcription contract with no drift detector. Flagged by two SIMPLIFY passes and appliable by no squad — both files resolve to NOBODY |
| B-12 | chore | 40+ of 43 `bin/test-*.py` files define their own `check()` in five incompatible shapes |
| B-13 | chore | Five pre-existing plan-phase artifacts fail the DEC-154/DEC-156 contracts. Not corrected — rewriting another run's record would falsify it |
| B-14 | bug | `check-state.sh`'s overrule attribution check has no `continue`, so a rejected unattributed overrule still emits a `disposition overruled.` line. The VIOLATION still fires |
| B-15 | chore | `M6` — `goalcheck` transcription ambiguity; fails closed and loudly on the first live run. `M7` — the withhold message states the fact but not the remedy |
| B-16 | chore | `V2` — branch-less corroboration is a documented deliberate no-op; closing it needs a non-branch identity input |

## Budget

Cycles **9 of 10** — the bound nearly bit. Four rework loops went to reviewer findings, and on your
ruling cycle 10 is preserved rather than spent re-observing code that cannot execute. Runs **16 of
20**, informational. The runs earned their place: three of them found defects that would otherwise
have shipped, and one of those was in the feature's own gate.
