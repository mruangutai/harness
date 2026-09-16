# BRIEF — BUG-1723-orchestrator-closeout one-command run close-out

## Problem

Closing a lead-returned run currently makes the harness orchestrator spend roughly eleven model calls on deterministic bookkeeping. The measured specimen used 448 calls, including 214 of 235 Bash calls for bookkeeping, while contexts crossed phase seams and later required retrospective succession corrections. The operator has neither a single close-out operation nor an enforced signal when one orchestrator context records runs on both sides of a phase handoff.

## Done when — by perspective

**orchestrator** — I can close a lead-returned run with one command, receive the first refusal by name when close-out cannot finish, and then separately finish `STATE.md`, the phase handoff note, and the git commit. Quarantine remains something I check when I wake.

**operator** — I can rely on the ledger to expose a retrospective succession correction when its judgement postdates the first run in the later phase. On the first plan mission after shipment, I can determine whether close-out reduced orchestrator calls and context without allowing retrospective succession.

**code maintainer** — I can maintain one validation and mutation contract for digest, run-end, plan-station, judgement, and spend operations, with focused regression evidence for close-out and phase-seam failures.

## Success criteria

- SC-01 (orchestrator): One successful `close-run` invocation validates the named run's persona digest, closes the run, applies paired optional task/station and optional judgement inputs, accepts only `n_a` for the optional code grade, and prints one close-out line containing spend. The successful case must first be demonstrated failing against the pre-change command.
  verify: automated        evidence: unit
- SC-02 (code maintainer): When a composed writer refuses, `close-run` exits nonzero, names that first failing stage, does not invoke later stages, and preserves any earlier completed write and the refusal semantics of the existing authorities. Each refusal case must first be demonstrated failing against the pre-change command.
  verify: automated        evidence: unit
- SC-03 (operator): The next available state invariant reports a succession judgement whose timestamp is later than the first run after the corresponding phase handoff, stays silent when succession is recorded no later than that run, and reports unusable chronology as unverifiable rather than silently passing it. The retrospective and unusable-chronology cases must first be demonstrated failing against the pre-change checker.
  verify: automated        evidence: integration
- SC-04 (orchestrator): At the pinned review SHA, `git show <review_sha>:.claude/skills/harness/SKILL.md`, `git show <review_sha>:.claude/skills/harness/references/build-phase.md`, and `git show <review_sha>:.claude/skills/harness/references/ledger.md` present `close-run` as the single run-close command, keep `STATE.md`, the handoff note, and the git commit as explicit separate writes, and keep quarantine at wake time; the reviewer cites each relevant file and heading.
  verify: inspection
- SC-05 (operator): For the first complete plan mission after shipment, export the orchestrator OMP JSONL, group model calls by dispatch, calculate median context from `.message.usage`, and compare succession judgement timestamps with the first run after each handoff. Pass only when every dispatch uses at most eight orchestrator model calls, median context is below 100,000 tokens, and there are zero retrospective succession judgements.
  verify: uat

## Verification gaps

None. Unit and integration suites cover the deterministic contracts; SC-05 deliberately remains a live UAT against the first post-shipment plan mission.

## Constraints

- DEC-159 supplies the per-phase orchestrator boundary and handoff model; this change enforces rather than relaxes it.
- DEC-150 blocks moving `STATE.md` authorship or history into `close-run`; `STATE.md` remains a separate current-truth write.
- DEC-174 and DEC-179 require enforcement scripts, their tests, and any currently ungranted source surface to execute in the main session.
- DEC-227 remains authoritative for run-end timestamps, token hooks, and spend derivation.
- DEC-230 remains authoritative for judgement structure and append-only recording.
- DEC-204 keeps quarantine inspection at wake time rather than adding it to close-out.
- `feature.json` gains no new fields, and the invariant does not depend on `run_uid` while issue 1708 remains unresolved.
- Approval remains pending until the main session presents this brief and plan to the user.

## Out of scope

- Shrinking repository reads performed at each orchestrator wake.
- Changing which decisions the orchestrator makes.
- Reducing dispatch count, which remains owned by issues 1725 and 1716.

## Approval

status: pending
