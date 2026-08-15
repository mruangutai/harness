# BRIEF — FEAT-07 Verify teeth, batched signature, probed environment

## Problem

Three costs recur, each measured in this repo's own logs.

**(1) The cheapest gate in the system never runs.** Every PLAN task carries a mandatory `verify:`
command (`.claude/skills/harness/templates/PLAN.md:47`) and nothing executes it — it appears in
exactly two places outside the perf doc, and `grep -n verify` over `.claude/agents/harness-eng-lead.md`
and `.claude/skills/harness-zero-micro-management/SKILL.md` returns nothing. The first thing that
catches a task-level miss is therefore the qa gate, which runs after the whole build segment, and a
miss there is a full loop-back cycle.

**(2) The user's change requests arrive one at a time at the signature gate.** FEAT-03 ran seven
serialized plan-phase runs at ~$95 and ~5h wall clock (`.harness/logs/2026-07-31.md:2` 10:15 →
`:6` 15:08). All three engineering re-verifications returned PASS with zero `must_fix` — nothing was
found; each cycle existed only because a new sign-off change request arrived separately
(`.harness/logs/2026-07-31.md:4` "User NOT ready to sign", `:5` "User approved; still not signing").

**(3) Bounded environment questions get inferred instead of measured.** One question — which copy of
a script a hook actually executes in a worktree — cost a working day and two retracted claims to the
user (`.harness/logs/2026-08-03.md:6` asserted, `:14` "my statement was firmer than the evidence",
`:23` measured and disproved the original). The probe that settled it took five minutes, and five
downstream consequences flipped when it landed.

## Goal

Give the dev's declared `verify:` real teeth in the return contract, so a task-level miss is caught at
the task rather than at the qa gate; make the main session collect all of the user's change requests
from one review pass and dispatch exactly one consolidated fix; and make a bounded runtime-environment
question something that gets probed before any claim about it is relayed to the user. Zero quality
degradation is the binding constraint — a change that trades quality for speed is out, whatever it
saves.

## Requirements

- REQ-01: A dev's return records whether its task's declared `verify:` command passed, and a return
  claiming success while recording a non-passing verify is rejected by the machinery, not by a
  reviewer's attention.
- REQ-02: No dev specialist is exempt from REQ-01. There is no persona for which "verify did not
  pass" alongside a success verdict is accepted. **Amended by the architecture review (F1): the
  exemption axis is the DISPATCH, not the persona.** A dev dispatched against a PLAN task has no
  legal way to claim success while its verify did not pass — that is REQ-01 and no persona escapes
  it. A dev dispatched for work that carries no PLAN task at all has no `verify:` command to report
  on, and needs a truthful spelling of that (REQ-10); the two cases must be told apart by their
  spelling, not by the validator guessing. Read as "no persona is exempt", REQ-02 would have made
  every non-task dev dispatch unreturnable — see `## Verification gaps`.
- REQ-03: A dev that genuinely could not run its verify — a refused or blocked task — can say so
  truthfully and have that return accepted.
- REQ-04: A dev is told which `verify:` command belongs to its task without having to find it, and a
  disagreement between what it was told and what the plan says stops the task instead of being
  resolved silently.
- REQ-05: Change requests the user raises while reviewing BRIEF/PLAN for signature are applied as one
  revision pass, not one revision per request.
- REQ-06: A bounded question about how the runtime environment resolves something is settled by
  measurement before any claim about it is relayed to the user.
- REQ-07: Every surface that documents the engineering return contract describes what the validator
  actually enforces — no site is left stating the superseded field set.
- REQ-08: A dev's verification claim leaves durable evidence in a file its reviewers already open —
  the command it ran and that command's own output, not only a self-reported verdict field.
- REQ-09: For the `dev` and `qa` personas, a return reporting one of its own gates as having FAILED
  while claiming success is rejected by the machinery. Reporting a gate as "did not run" is already
  rejected; reporting it as "ran and failed" must be too. **Scoped to `dev` and `qa` deliberately** —
  `dev-ops` is excluded by the user's ruling (D-03), and the consequence is recorded as residue under
  `## Verification gaps` rather than smuggled in here. A REQ this feature does not deliver in full is
  a REQ that cannot be honestly marked covered at the goal-check.
- REQ-10: A dev specialist dispatched for work that carries no PLAN task — an architecture review, an
  Expertise distillation, a debug or research pass, any lead-issued investigation — can return
  success truthfully. Its answer to "did your task's verify pass?" is distinguishable in an audit
  from both "it passed" and "I refused the task". **Raised by the architecture review, not by the
  user. The shape it takes was the user's call and the user has now made it (D-07): a declared
  `task: T-NN|none` field, with `task_verify` binding only when `task` names a real task. The
  requirement is unchanged by that ruling — it is an outcome, and it survived the swap.**
- REQ-11: The validator's own guidance for a missing gated field does not name a value that the
  validator will then reject. A rejection message that routes the agent to a second rejection is a
  loop, and under the `stop_hook_active` passthrough the second round-trip is not re-validated at all.

## Constraints

- **Zero quality degradation is binding** (the user's ruling, not an inference). No criterion is
  weakened, no gate loosened, to save a cycle.
- **DEC-174 carve-out.** `validate-digest.py` is the harness's own enforcement layer: changes to it
  are made directly — ordinary edits, tests run explicitly, a human reading the diff — never
  dispatched through a team run whose gates are the thing being changed. This binds the widened fail
  gate too — it is the same file.
- **The probe rule must not land in `harness-handoff`.** Its lines are paid by all 16 agents at every
  spawn. It lands in `.claude/commands/harness.md` and `.claude/skills/harness/SKILL.md` only — the
  two tiers that relay claims to the user and the two that over-claimed.
- **`dev-ops`'s existing `suite: n/a` + `PASS` carve-out (DEC-173, `validate-digest.py:66`) is not
  touched.** It is correct: `test_matrix` maps config/scaffolding/docs to `[]`. Only `task_verify` is
  made non-exempt **for dev-ops**. The user's ruling extends this: `dev-ops` gains no `suite` entry in
  the new fail gate either, so `suite: fail` + `PASS` also stays accepted for it — recorded as residue
  under `## Verification gaps`, not fixed. `dev` and `qa` are separately in scope (see Behaviour change).
- **No escape hatch for an urgent, independent change request at the signature gate — deliberately.**
  Grilling recorded that nobody has hit that case, so its shape cannot be stated sharply enough to
  write. The rule ships without one; the cost the user accepted is reviewing to exhaustion before the
  first fix goes out.
- **Out of scope by the user's ruling:** issues #20 (plan-time route resolution as a general
  mechanism), #21 (qa phase 1 concurrent with the build), and perf-doc row 10 (counting and budgeting
  runs). Consequence accepted and recorded: after this feature there is still no instrumented way to
  say which lever paid.
- Files-only; PyYAML is required (DEC-171 am.1). No new dependency.

## Behaviour change — returns that pass today start being rejected

This feature does not only ADD a field. It tightens a gate every squad already passes through, so it
is stated here, where the signature is taken, rather than inside a task body.

**TWO new REQUIRED fields, not one.** Under D-07 as the user ruled it, every `dev` and `dev-ops`
return must carry `task:` as well as `task_verify:` — a return omitting `task` is rejected whatever
else it says. That is the widest part of this feature's blast radius and it is stated here rather
than inside T-01: after this lands, no `dev` or `dev-ops` return written to today's contract
validates until its dispatch and its author know about both fields. `task_verify` is then required
only when `task` names a real `T-NN`; `task: none` switches that obligation off (SC-17b) and makes
`task_verify: pass|fail` a rejected contradiction (D-08).

**Re-derived at `4091b36` by running each case through `validate-digest.py`, not by reading the
code.** Four persona/field combinations report a gate as having FAILED alongside `VERDICT: PASS` and
are ACCEPTED today — `digest ok`, exit 0. Cause: the `GATE_FIELDS` consultation
(`validate-digest.py:481`) is nested inside the `field in NULLABLE and val in PLACEHOLDER_UNSET`
branch (`:477`), so it can only ever see the placeholder value `n/a`. DEC-173 gave "did not run" a
spelling and gated it; "ran and failed" was never gated at all.

| Persona | Field + value, with `VERDICT: PASS` | Today | After this feature |
|---|---|---|---|
| `dev` | `suite: fail` | accepted, exit 0 | **REJECTED** |
| `qa` | `suite: fail` | accepted, exit 0 | **REJECTED** |
| `qa` | `matrix_ok: false` | accepted, exit 0 | **REJECTED** |
| `dev-ops` | `suite: fail` | accepted, exit 0 | **accepted — unchanged, see Verification gaps** |

Three of the four are closed here (REQ-09). The fourth is left open by the user's ruling that
`dev-ops` gains no `suite` entry in either gate structure, and is recorded as residue rather than
fixed. This is a deliberate tightening, not a regression: a return that says its own gate failed and
claims success anyway is the fail-open the validator exists to prevent.

## Success Criteria

- SC-01: A dev-persona digest that declares `task: T-NN` and omits `task_verify` is rejected by
  `validate-digest.py`, and one carrying `task: T-NN` + `task_verify: pass` with `VERDICT: PASS` is
  accepted. **The `task: T-NN` precondition is load-bearing under D-07, not decoration:** the
  requirement is conditional, so with `task: none` the same omission is ACCEPTED (SC-17b). Written
  without the precondition this criterion would assert something the validator no longer does.
  verify: automated        evidence: unit
- SC-02: For a dev persona **declaring `task: T-NN`**, BOTH `task_verify: fail` + `VERDICT: PASS` and
  `task_verify: n/a` + `VERDICT: PASS` are rejected. (The `n/a` half comes from the existing
  `GATE_FIELDS` mechanism; the `fail` half does not — measured at `4091b36`, `GATE_FIELDS` never sees
  a real `fail` value, which is why a second gate structure is built. Since the Behaviour-change
  ruling that structure covers `suite` too, so it is one shared fail gate, not a `task_verify`-only
  one — see PLAN D-01.) The precondition is stated because after D-07 BOTH gates bind only on a
  task-carrying return; what happens on the `task: none` branch is a separate ruling (D-08) and is
  SC-17c's, not this criterion's.
  verify: automated        evidence: unit
- SC-03: The same two rejections hold for `harness-dev-ops` declaring `task: T-NN`. A dev-ops return
  with `task_verify: n/a` or `fail` alongside `VERDICT: PASS` is rejected — this is the no-carve-out
  ruling, proven. Same precondition, same reason as SC-02.
  verify: automated        evidence: unit
- SC-04: `dev-ops`'s pre-existing carve-out is intact: a dev-ops digest with `suite: n/a`,
  `task: T-NN`, `task_verify: pass` and `VERDICT: PASS` is still accepted. **This is a REGRESSION
  clause, not a change detector** — it passes at `4091b36` and must keep passing. It never
  discriminated and does not start to; the widened fail gate is a separate structure from the `n/a`
  gate this clause guards, so SC-04 alone does not show that widening left `dev-ops` alone. SC-15 is
  the case that does. It gains `task: T-NN` only because that field is now required of the schema.
  verify: automated        evidence: unit
- SC-05: **`task` AND `task_verify` are required of exactly the `dev` and `dev-ops` schemas.** A
  `harness-qa`, reviewer, documentor, lead or orchestrator digest carrying NEITHER field is still
  accepted. Two fields, one criterion, deliberately: `task` is new under D-07 and nothing else proves
  it did not leak into the personas that must not carry it — the same leak SC-05 already existed to
  catch, one field over, and a leak nobody would notice because an extra required field only ever
  makes returns FAIL. **LABELLED per its own honesty rule:** the qa half is green at `4091b36` too
  (measured: a qa digest with neither field returns `digest ok`, exit 0), so it is a REGRESSION guard,
  not a change detector. What makes it go red is `task` or `task_verify` appearing in a persona schema
  it does not belong to — which is exactly the drift it exists to catch.
  verify: automated        evidence: unit
- SC-06: A refused or blocked task can be reported honestly — a return declaring `task: T-NN` with
  `task_verify: n/a` and `VERDICT: BLOCKED` (and with `VERDICT: FAIL`) is accepted for both `dev` and
  `dev-ops`. **`task: T-NN` is the correct branch and was checked rather than assumed:** REQ-03 is
  about a task that EXISTED and whose verify did not run, so the honest-refusal shape must be proven
  on a task-carrying return. Proving it with `task: none` would test the `task: none` branch instead and
  leave REQ-03 unproven — the wrong-branch defect the conditional makes possible.
  verify: automated        evidence: unit
- SC-07: No surface describing the engineering or dev-ops DIGEST still lists the superseded field set.
  Each of `.claude/skills/harness-digest-dev/SKILL.md`, `.claude/agents/harness-dev-ops.md`,
  `docs/harness/SPEC.md` §8.1 (BOTH the eng-devs bullet and the dev-ops bullet) and
  `.claude/skills/harness-tdd-enforcement/SKILL.md` names `task_verify` with its full enum AND the
  `task: T-NN|none` field D-07 settles, together with the rule that binds them: `task_verify` is
  required only when `task` names a real task, and `fail` or `n/a` alongside `VERDICT: PASS` is
  rejected. A surface naming one field without the other documents a schema that does not exist.
  verify: inspection
- SC-08: The lead's delegation rule requires the dispatch prompt to carry the task id AND the task's
  `verify:` command verbatim; the dev's return contract requires cross-checking that command against
  `PLAN.md` and returning `BLOCKED` on mismatch.
  verify: inspection
- SC-09: `.claude/commands/harness.md` §2 states that all of the user's change requests from one
  review pass are collected and dispatched as exactly one consolidated fix, and names the cost the
  user accepted (reviewing to exhaustion before the first fix goes out).
  verify: inspection
- SC-10: `.claude/commands/harness.md` and `.claude/skills/harness/SKILL.md` each state that a bounded
  runtime-environment question is probed before any claim about it is relayed to the user, and
  `.claude/skills/harness-handoff/SKILL.md` does not carry the rule. (The absence half is a guard
  paired with the two presence checks per DEC-169, not evidence on its own.)
  verify: inspection
- SC-11: The validator change and its fixtures ship in ONE commit — there is no commit on the feature
  branch at which `run-unit-tests.sh` fails because `validate-digest.py` and
  `test-validate-digest.py` disagree about the field set.
  verify: inspection
- SC-12: Three DECISIONS.md entries exist (the gated `task_verify` field, the signature-gate batching
  rule, the probe rule), each with its `DECISIONS-INDEX.md` row, and the index is the generator's
  output rather than a hand edit — re-running `bin/gen-decisions-index.py` leaves the file unchanged.
  **Plus the reporting half, folded in after the architecture review noted the end-state hash alone
  does not discriminate:** T-09's receipt records the precondition diff's exit code, and where that
  exit code was 1, names the pre-existing drift it necessarily absorbed. Regenerating rewrites every
  anchor row, so "do not absorb the drift" is not achievable — only "do not absorb it SILENTLY" is,
  and this is the clause that checks the difference. Where the precondition exited 0 the receipt says
  so and there is nothing to name.
  verify: inspection
- SC-13: A `dev` digest carrying `suite: fail` alongside `VERDICT: PASS` is rejected. (Measured at
  `4091b36`: accepted, `digest ok`, exit 0 — so this criterion discriminates.)
  verify: automated        evidence: unit
- SC-14: A `harness-qa` digest is rejected when it carries `VERDICT: PASS` with EITHER `suite: fail`
  OR `matrix_ok: false`. Both are accepted at `4091b36`, and `matrix_ok` is the project's only
  blocking gate (`harness.json` `gates.qa_gate: blocking`).
  verify: automated        evidence: unit
- SC-15: The `dev-ops` residue is PINNED, not left implicit: a `dev-ops` digest with `suite: fail` and
  `VERDICT: PASS` is still ACCEPTED after the widening, and a named fixture asserts it. The fixture is
  the guard that goes red if a later edit tidies `dev-ops` into symmetry with `dev` — the exact drift
  D-03 predicts. It pins the user's ruling, not a claim that the acceptance is correct.
  verify: automated        evidence: unit
- SC-16: The requirement that a dev's verification receipt carry the task's `verify:` command AND that
  command's verbatim output is stated on exactly one surface, and that surface is preloaded by all
  five dev specialists (the four eng specialists plus `harness-dev-ops`). The "no inline second copy
  in any agent file" half is a SCOPE GUARD, not evidence: `receipt` and `verbatim` both measure 0
  across those files at `4091b36`, so an absence-grep on them was already empty and proves nothing on
  its own. It is paired with the presence check per DEC-169, exactly as SC-10's `harness-handoff`
  clause is. The clause is scoped to returns declaring `task: T-NN`: a return declaring `task: none`
  has no `verify:` command to record, and a clause demanding one would be a second instance of the F1
  defect one surface over.
  verify: inspection
- SC-17: **`task` is a real, constrained, REQUIRED field, and the conditional it governs binds in
  both directions.** Four cases, one criterion, because an acceptance clause with no rejection
  partner is the vacuous shape this feature exists to remove:
  (a) `dev` `task: T-NN` + `task_verify` OMITTED + `VERDICT: PASS` -> REJECTED — the requirement binds;
  (b) `dev` and `dev-ops` `task: none` + `task_verify` OMITTED + `VERDICT: PASS` -> ACCEPTED — it does
      not bind, and this is how a dispatch carrying no PLAN task returns success truthfully (REQ-10);
  (c) `dev` `task: none` + `task_verify: fail` + `VERDICT: PASS` -> REJECTED — the contradiction gate,
      D-08. Declaring no task and then reporting that the task's command failed cannot both be true;
  (d) `task: bogus` -> REJECTED, and `task` OMITTED entirely -> REJECTED.
  Measured at `4091b36`, every one of the four returns `digest ok`, exit 0 today. So (a), (c) and (d)
  DISCRIMINATE and (b) does not — (b) is green because `task` is in no schema yet and an unknown key
  is ignored, and it is labelled the regression half rather than sold as a detector. **(d) is the
  load-bearing half:** it is what shows `task` is a constrained field rather than a free string, and
  without it `task` would be precisely the "unknown key ignored" shape that made the superseded
  SC-17's acceptance half vacuous.
  verify: automated        evidence: unit
- SC-18: **No rejection message for a MISSING required field names a value that a second validation
  pass would then reject, and the hints for the two new fields are JOINTLY followable.** Three
  clauses:
  (a) a `dev` digest declaring `task: T-NN`, omitting `task_verify` and omitting no other nullable
      field, is rejected, and its message for that field names the field's real allowed values
      (`pass`, `fail`) instead of the placeholder spelling `none`. It must state that what is
      rejected is a placeholder ALONGSIDE `VERDICT: PASS`, not that placeholders are disallowed: the
      same guidance is emitted for a missing `suite`, and `suite: n/a` with `VERDICT: BLOCKED` is
      legal (SC-06/REQ-03);
  (b) a `dev` digest omitting `task` is rejected and its message names a task id and `none` — not
      `[]`. `task` is neither NULLABLE nor a gate field, so without its own hint branch it inherits
      the list wording, which is a rejectable value for it;
  (c) **JOINT FOLLOWABILITY — the clause the redirect made necessary.** A `dev` digest omitting BOTH
      fields, repaired by following BOTH emitted hints literally, validates. Under a conditional
      requirement two individually correct hints can be jointly contradictory — (b) offers `none`
      while (a) demands a value — and a repair that is rejected a second time ships UNVALIDATED
      through the pre-existing `stop_hook_active` passthrough (`validate-digest.py:691-692`). That is
      REQ-11's own defect class re-created by REQ-11's fix, one field over.
  Measured at `4091b36`: all three digests return `digest ok`, exit 0, so all three clauses
  discriminate. **This criterion was CHANGED by the redirect and RE-VERIFIED, not carried over.** The
  superseded SC-18 claimed the hint fix "holds under EITHER D-07 option, because the message is built
  from the schema". Under a conditional requirement that claim is false: with `task: none` the
  missing-`task_verify` path does not fire at all, and clauses (b) and (c) did not exist.
  verify: automated        evidence: unit

## Verification gaps

- **`functional`, `integration`, `component`, `ui`, `eval` and `typecheck` all have `cmd: null` in
  `.harness/harness.json`** — no runner. No SC here rests on any of them. `unit` is the only kind with
  a runner, and its `detect` glob includes `.claude/skills/harness/bin/test-*.py`, which is exactly the
  surface SC-01..SC-06, SC-13..SC-15, SC-17 and SC-18 are proven on — eleven criteria, all of them
  landing on `test-validate-digest.py`. SC-17 and SC-18 belong in this list rather than the next one:
  their fixtures are T-01 step (11) cases (g2)-(j2) — re-checked against the redirected task body
  rather than carried over, since the redirect renamed and added cases. They were missing from this
  enumeration when they were added, which is the stale-cross-reference defect this feature exists to
  remove, so the cross-reference is re-derived on every revision that touches T-01. Together
  with the `inspection` list below, every one of SC-01..SC-18 appears in exactly one of the two.
- **Markdown rule surfaces have no runner at all.** Every change to `.claude/skills/**/SKILL.md`,
  `.claude/commands/harness.md`, `.claude/agents/*.md` and `docs/harness/*.md` is carried by
  `verify: inspection` (SC-07..SC-12, SC-16). Nothing mechanical discriminates a well-written rule from a
  present-but-inert one on those surfaces.
- **#18 and #22 cannot be shown to have CHANGED BEHAVIOUR by this feature.** SC-09 and SC-10 prove the
  rule is present and says what it must say. Whether the main session actually batches, and actually
  probes, is only observable on the next feature that reaches a signature gate or hits a bounded
  environment question. No mechanical check available today discriminates the two, and inventing one
  would be the vacuous-criterion defect this feature exists to reduce.
- **Nothing here proves the dev RAN the command. The gap NARROWED; it did not close.** `task_verify`
  is self-reported, and the receipt clause (REQ-08) is self-reported too — a dev can fabricate a
  command's output as easily as it can write `task_verify: pass`. What changed is the cost and the
  visibility of doing so: skipping used to be an omission that left no trace anywhere, then a false
  scalar field, and now a fabricated command-plus-output block sitting in
  `.harness/features/<FEAT>/notes/receipt-<agent>-<runid>.md`, a file qa, the code reviewer and the
  user already open. That is **evidence of skipping in a place someone looks**, which is strictly
  weaker than mechanical ungameability and must not be described as achieving it. The rejected
  alternative — the lead re-runs the command itself — is structurally impossible: leads hold no
  `Bash`. No mechanical check can close the remainder, so it is stated here rather than planned.
- **`dev-ops` `suite: fail` + `VERDICT: PASS` stays ACCEPTED, and that is an unfixed instance of the
  very defect class this feature closes.** Re-measured at `4091b36`, not inferred: that digest returns
  `digest ok`, exit 0, and it still does after this feature, because the user ruled that `dev-ops`
  gains no `suite` entry in either gate structure (D-03). The ruling is right about `suite: n/a` —
  `test_matrix` maps config/scaffolding/docs to `[]` (DEC-100), so "no tests apply" is honest. It says
  nothing about `suite: fail`, which means tests ran and FAILED, and there is no reading of DEC-100 on
  which that earns a PASS. SC-15 pins the acceptance as a fixture so the residue is visible and any
  future change to it is deliberate. Closing it is a candidate for the backlog, not for this feature.
- **`task: none` IS STILL A SELF-DECLARED BYPASS. The redirect bought a cross-checkable string; it
  did NOT buy a proof, and it must not be written up as having closed the gap.** This is the price of
  D-07 as the user ruled it, stated here at the signature rather than inside a task body.
  **What remains unchecked, precisely:** nothing in `validate-digest.py` reads the dispatch that
  produced the return. The validator therefore cannot know whether a dispatch carried a PLAN task, so
  `task: none` is accepted on the return's word on EVERY dev and dev-ops return, not only on genuine
  non-task ones. A dev that writes `task: none` on a task-carrying dispatch passes the gate. It is
  caught only if a human or a later pass runs the cross-check, and nothing schedules that.
  **What the ruling does buy, and it is real but bounded:** T-05 requires the dispatch prompt to
  carry the task's `T-NN` id verbatim, and the return now declares a field in the same vocabulary. So
  the audit is a STRING EQUALITY between two durable artifacts — the dispatch text in the run record
  and `task:` in the return — rather than a presence question with nothing on the other side.
  `grep -rn 'task: none' .harness/features/*/runs/` lists every return that claimed no task, and each
  one can be compared against whether its own dispatch carried a `T-NN`; a false `task: none` is then
  contradicted BY AN ARTIFACT rather than by nothing. The rejected `no-task` spelling had no
  counterpart on the dispatch side at all, so no comparison existed to run. **That asymmetry is the
  entire content of the ruling, and it is an audit trail, not a gate.**
  Two further residues, stated rather than left implicit: the cross-check is manual and unscheduled,
  and `task: none` still obliges no receipt (REQ-08's command-and-output clause is scoped to
  task-carrying returns, SC-16), so a false `task: none` remains cheaper to write than a false
  `pass`. What changed is that it is now cheaper to CATCH.
- **The hint fix (REQ-11) narrows a loop; it does not close the `stop_hook_active` passthrough, and
  this feature did not open that passthrough.** Verified at source: `validate-digest.py:691-692` is
  `if d.get("stop_hook_active"): return 0`, so a re-prompted return is not re-validated. That
  passthrough is PRE-EXISTING and deliberate — its reasoning is at `:663-664` and it is BUILD task
  22's, not this feature's. What this feature would otherwise have created is a hint that routes an
  agent into it: after T-01 `task_verify` sits in both `NULLABLE` and the gate tables, and `:468`
  hints `none` for a missing NULLABLE field while `none` is a member of
  `harness_yaml.PLACEHOLDER_UNSET` (`harness_yaml.py:302`, measured `("none","null","n/a")`). Omit
  the field, get rejected at exit 2, follow the hint, resubmit `task_verify: none` + `PASS` — and the
  passthrough returns 0. REQ-11 stops the hint pointing there. It leaves the passthrough exactly as
  it found it, so any OTHER route into a second round-trip still ships unvalidated. Closing the
  passthrough is a backlog candidate and is out of scope here.
  **The redirect WIDENED this hazard and the widening is answered, not absorbed.** A conditional
  requirement creates a second way in that a single field could not: two hints that are each
  individually correct and jointly contradictory. Omit both new fields, and the `task` hint offers
  `none` while the `task_verify` hint demands a real value — follow both literally and the repair is
  rejected a second time, through the same passthrough. SC-18(c) is the clause that checks the two
  hints are jointly followable, and it exists only because of the redirect. The residue is unchanged:
  the passthrough itself is still open and still out of scope.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-08-04
