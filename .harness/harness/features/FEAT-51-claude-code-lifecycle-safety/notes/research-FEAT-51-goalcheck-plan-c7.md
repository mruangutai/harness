# Goal-check — FEAT-51 — amended plan (cycle 7, post F-1 ruling)

**Does this amended plan deliver the operator's stated intent? Yes.** Graded against the operator's
own words in `.harness/notes/grilling-claude-code-lifecycle-safety-2026-09-01.md`, not against the
BRIEF: every settled behaviour in the grilling has a task that builds it and a criterion that grades
it, no REQ has a leg no task covers, and the `discard` removal takes nothing the operator asked for.
Twelve criteria are `not_met` because nothing is built yet — the expected plan-phase answer.

## Grades — SC-01..SC-11, SC-13

`SC-12` was withdrawn this cycle (D-18; the gap at that number is deliberate) and is not graded.

| SC | Verdict | Evidence |
|---|---|---|
| SC-01 | not_met | Unbuilt. `T-01` builds the third `hook_mode()` answer and the six exact-label cases in `test-validate-digest.py`; its `verify:` greps two of those labels then runs the suite. |
| SC-02 | not_met | Unbuilt. Same `T-01`; the three escape assertions are three of the six mandated labels (no-live-child, omitted-child, member-persona), each its own case per P-04. |
| SC-03 | not_met | Unbuilt. `T-01`'s "leaves the parent claim live" label plus its `STEP ONE` release change; the intent mandates reading the claim off disk via `claims()`, not from the exit code. |
| SC-04 | not_met | Unbuilt. `T-03` at the `check-domain.sh` Write gate over `T-02`'s `orphan_write` predicate; the third assertion (orphan `plan.yaml` keeps the FEAT-41 route-denial text) is D-11's deferral. |
| SC-05 | not_met | Unbuilt. `T-03` — the `notes/` and quarantine-path allows beside the refused `BRIEF.md` write. |
| SC-06 | not_met | Unbuilt. `T-04` ships `quarantine.py`; its intent mandates the 14-task/1-task adoption case through `plan-merge.py` union, `discard` removing one directory, and `list` proven inert by sha256, with "no scheduler, no timer, no TTL". |
| SC-07 | not_met | Unbuilt. `T-02` carries the `runtime != omp` condition; the `--kind integration` / `--kind unit` and `blocking: true` legs land with `T-04`'s registration. |
| SC-08 | not_met | Unbuilt, and `inspection` by a reviewer at `review_sha`. `T-05` writes the four clauses into both playbooks with `test-orchestrator-playbook.py` / `test-lead-stop-and-wake.py` cases. |
| SC-09 | not_met | Unbuilt. `T-06` writes the entry and the hand-written index ruling half; `T-08` is the assertion that makes an omitted Bash half red. See the `DEC-209` section below — the plan self-heals and the guard fails safe. |
| SC-10 | not_met | `uat` — only the operator can move this, from the main checkout after merge (BRIEF `## Verification gaps`). The conduct it grades is `T-05`'s. |
| SC-11 | not_met | Unbuilt. `T-07` adds the second rule to `plan-sign-gate.sh` / `.py`; its intent carries the three refusals, the own-claim-live and `runtime: omp` exit-0 controls, and the `PLAN_SIGN_GATE_BIN` red proof. |
| SC-13 | not_met | Unbuilt. `T-10` adds two fail-open cases plus a negative control to **each** of `test-check-domain.py` and `test-plan-sign-gate.py`; graded at the reviewed sha per G-15. |

No criterion is `cannot_verify`: each names the task that will grade it.

## Does removing `discard` coverage leave operator intent undelivered?

**No — not as the grilling states it.** Tested rather than assumed:

- **The grilling's own words.** Destination: "children may finish analysis but cannot race a
  replacement writer; a resumed parent explicitly adopts or discards the result" (`:5`). Settled:
  "feature-artifact writes are quarantined until a resumed parent explicitly adopts the result"
  (`:9`). Out of scope: "letting an orphan write canonical feature artifacts and repairing the race
  afterward" (`:22`). Every clause is about **writes to canonical artifacts** and about the resumed
  parent's act being **explicit**. Nothing asks that the quarantine store be tamper-proof against
  deletion, and `:16` grants engineering "the narrowest host-compatible quarantine … that satisfies
  the settled behavior".
- **REQ legs.** `REQ-01..REQ-07` are byte-frozen and every one is traced: REQ-01 → T-05; REQ-02 →
  T-01, T-06; REQ-03 → T-03, T-05, T-10; REQ-04 → T-02, T-03, T-07, T-08, T-10; REQ-05 → T-04, T-06,
  T-07, T-08; REQ-06 → T-01, T-05; REQ-07 → T-02, T-06. No orphan leg.
- **REQ-04's remedy is still whole.** Its subject is "writes to canonical feature artifacts", and
  D-05 fixes canonical as exactly `plan.yaml`, `BRIEF.md`, `feature.json`, `STATE.md` directly under
  the feature directory. A quarantine directory is not one of them, so `discard` was never inside
  REQ-04's scope; T-02/T-03/T-07/T-10 cover it end to end on both routes.
- **REQ-05's "discard is an explicit act, never a default and never a timeout"** is delivered by
  construction, not by enforcement: `T-04` mandates a CLI with no scheduler and no TTL, and SC-06
  grades that nothing happens without the command being run. What is *not* delivered is enforcement
  stopping a **different** actor from achieving discard's effect by other means.

**The one residual, and it is a recommendation, not a decision.** D-05's own reason says quarantine
exists because "quarantining them would destroy the completed analysis the operator wants
recoverable". Recoverability now rests on nothing enforcing it: `bash-write-guard.sh:259` exempts
`harness-dev-ops` outright, `:504-505` routes `rm` through `classify`, and `:784-790` prints a notice
and **continues** on the `shared` verdict that D-06's `.harness/*/features/*/quarantine/**` glob
produces. The ruling records this honestly (D-18, and the BRIEF `## Verification gaps` bullet) rather
than claiming a protection the tree lacks, which is the correct disposition of a property the
grilling never requested. **Recommend** the operator confirm that the backlog referral for generic
quarantine-directory deletion enforcement is the intended landing place; if he wants the
recoverability leg *proven* in this feature rather than deferred, that is a scope addition only he
can make.

## Did the BRIEF drift from the grilling?

**No material drift.** Goal `:26-28` is the grilling destination near-verbatim; REQ-01 matches "the
parent does not poll at all" (`:11`); REQ-02/REQ-06 match the suspension row (`:10`); REQ-03 matches
"the host wakes the same parent"; REQ-04/REQ-05 match `:9` plus the destination's "adopts or
discards"; REQ-07 matches the OMP out-of-scope bullet (`:20`); `source_issues: [280, 551]` and the
`#628` exclusion match `:12` and `:21`. Two benign extensions, neither a scope change: REQ-06 adds
"or after adoption" where the grilling says only "when the child finishes", and the BRIEF `## Problem`
carries measurements from issue #551's comments that the grilling's verified-facts block does not
contain — framing, not requirement.

## The two prior-step open questions, factored in

- **`DEC-209` is taken on main at `0bc57c88`** by *"Mechanical code-grade state is computed by the
  digest gate…"*. `BRIEF.md` contains **zero** `DEC-209` tokens (re-verified: `grep -c` = 0), so
  SC-09 names no number and is unaffected. `T-06`'s intent carries the next-free-number fallback and
  `T-08`'s `QUARANTINE_DEC` comment mandates that the constant moves with it. **The guard fails
  safe, verified at source:** the shipped DEC-209 region contains none of `check-domain.sh`,
  `plan-sign-gate.sh`, `quarantine.py adopt`, `plan-merge.py` (all `grep -c` = 0 over
  `git show 0bc57c88:…DECISIONS.md`), so a stale constant makes T-08 red, never falsely green.
  SC-09 is therefore graded `not_met` for being unbuilt only. The 21 `DEC-209` tokens in
  `plan.yaml`'s decisions block read stale and affect **no** SC — see Q1.
- **`T-06`'s third conjunct `grep -q 'DEC-209' DECISIONS-INDEX.md` is non-discriminating** (the token
  is already in the committed index) and would also stay green if T-06 took DEC-210. It weakens no
  SC's evidence: the discrimination for SC-09 lives in the two awk conjuncts, which slice the
  **last** `## DEC-` region and are proven red on the current tree and on the `check-domain.sh`-only
  defect entry, and in T-08's per-clause assertions. Worth noting for the panel: **no** conjunct of
  T-06 grades SC-09's "index row names the compatibility host in the hand-written ruling half" —
  that clause rests on inspection at review, not on the suite.

## Open questions

- **Q1 (non-blocking, routing):** the 21 stale `dec: DEC-209` pointers in `plan.yaml` have no owner
  with a route. `T-06`'s intent instructs the documentor to "use it consistently … in every `dec:`
  pointer in this plan's decisions block", but `T-06.files` names only the two decision documents,
  and `plan.yaml`'s only write route is `plan-merge.py` (harness-pm / main session). Either strike
  that clause from T-06's intent or place the repoint as a pm step.
