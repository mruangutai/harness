# STATE

## Current

- feature: FEAT-14-feature-json-schema
- run: revision2-product — PASS, zero send-backs
- squad: product
- status: awaiting_user — BRIEF.md and plan.yaml are SIGNED (`approved`, operator, 2026-08-11);
  revision 2 applied corrections INSIDE that signature and did not re-open it

**The plan phase is complete. Five runs, `cycles_used: 3`, unchanged by this revision.** DEC-157's
test is mechanical — a FAIL routed back, an unmet-SC re-dispatch, or a lead-reported send-back — and
an operator correction is none of the three. The lead reported `cycles_used: 0`. Seven cycles remain.
Shape, verified by me with `safe_load` at `a29ad06` rather than taken from the digest: **12 tasks, 13
decisions, 18 success criteria**, 9 requirements, an **ELEVEN**-key schema with 8 required.

### What revision 2 changed

**Ruling 1 is WITHDRAWN — FEAT-15 migrates to `Done`, not `Plan`.** The withdrawn ruling reasoned
from a stale file. Measured at `a29ad06`: FEAT-15's `feature.yaml` says `awaiting_user / plan`, but
its `plan.yaml` reads `approval: approved`, **PR #263 is MERGED and issue #239 is CLOSED**. It
shipped. The old "0 INV-17 violations at `Plan`" dry-run measured a stale value being conveniently
early, not correctness, and no longer appears anywhere.

**T-04's RULE was amended, not just its row** — a corrected row would have been outlived by a stale
rule, because T-04 places features by that rule against a build-time glob. The old `phase` key is now
explicitly **not authoritative** when the feature's `plan.yaml` reads `approval: approved` and its PR
is merged; the approval block is read instead.

**INV-17 gains a plan-keyed exemption, and it is T-12's, not a new task.** `check-state.sh` and
`test-check-state.py` were already in T-12's `files:` and already lane-resolved `main-session-direct`
in the signed `lanes:` block, so a sibling task would have re-opened lane resolution for nothing.

The predicate is **three conjoined conditions**: (1) a `plan.yaml` exists — a `PLAN.md` never
qualifies; (2) its `tasks:` list is present and non-empty; (3) **every** task carries
`execution_mode: main-session-direct`. Anything else → **not exempt**, and it **fails closed** on a
read or parse error, citing SC-16's already-signed "a checker that cannot run DENIES".

**Condition 2 excludes nobody in today's corpus, and the plan says so honestly** rather than
crediting it with work it does not do — every `plan.yaml` on disk has a non-empty `tasks:` list.
**Condition 1 is what excludes FEAT-01 through FEAT-05**: FEAT-01 has no plan file, the other four
carry a `PLAN.md`. Condition 2 guards the degenerate input — a stub, a mistyped `tasks:` key —
because "every task is main-session-direct" over an empty list is **vacuously true**. A recorded
deliberate false negative: FEAT-06 and FEAT-07 are all-main-session-direct but on `PLAN.md`, so
condition 1 keeps them non-exempt and still owing notes. Both already hold every note their status
demands, so the safe direction costs nothing.

**Two mechanisms now coexist and the plan says why they differ in kind** — T-12's own sentence
forbidding "new inference inside a carve-out gate" was reversed by the operator, explicitly rather
than silently. The literal FEAT-01/FEAT-02 set survives because the plan-keyed rule cannot reach
those two by construction; a literal list is the only thing that can.

**The exemption is REPORTED, never silent** — one line per feature, not one per suppressed note —
and it goes through `warn`, deliberately avoiding the string `VIOLATION`: T-08's baseline comparison
greps for it, so a violation-shaped note would fail T-08 for the wrong reason. INV-22 is the precedent.

**T-08's hardcoded `FEAT-01/FEAT-02` exemption assertion is gone**, replaced by a set computed from
the plans (`plan.yaml:1286`) plus a never-evaluated-predicate assertion (`:1287`). As it stood, T-08
would have passed green while INV-17 raised three violations on FEAT-15.

**T-12's dry-run was re-derived** and now asserts zero violations **plus exactly one exemption note
line** for FEAT-15. Zero violations and no note line is declared a FAILURE — the exemption never
evaluated. Its "do not widen the exemption set to make it quiet" warning survives verbatim.

**SC-18 now asserts seven test cases, up from four** — its own wording says so. Its case (c) keeps
the exemption keyed on declared modes rather than on absence, and covers **two** degenerate shapes: a
`Done` feature whose plan carries no `execution_mode` key at all, and one whose `tasks:` list is
empty or absent. Both must RAISE. No case rests on `check-state.sh` exiting 0. SC-08 and SC-17 were
updated in the same pass; T-11's item 5, which restated SC-17's arithmetic, was corrected unrequested.

**SC-17's arithmetic moved: `Done` is seven features, and the expected checked plan count is 10, not
11.** Cross-checked two ways — 16 plan files minus the six `Done` features that have one (FEAT-01 has
none), and today's 12 minus FEAT-10 and FEAT-15.

### The operator's own premise, corrected

The correction memo says *"FEAT-17 is already planned as main-session-direct and will be the second."*
**Measured at `a29ad06`, that is wrong.** FEAT-17's `plan.yaml` has seven tasks; T-01..T-06 are
`main-session-direct` but **T-07 is `execution_mode: team`** (`harness-documentor`, line 773). FEAT-17
is not all-main-session-direct, correctly still owes handoff notes, and the strict ALL predicate gives
the right answer for it. **The exemption stands on FEAT-15 alone** — which lands three violations on
day one without it. The predicate was NOT weakened to reach FEAT-17. Also measured: FEAT-15 is the
only all-main-session-direct feature in the corpus (FEAT-16 is 10 of 11 `team`); FEAT-01, 02, 15, 16
and 17 hold zero handoff notes.

### Unchanged, and re-verified rather than assumed

`check-plan-routes.py` reports **0 violations across 12 plans** and `check-state.sh` names FEAT-14 in
**no** violation line — I ran both myself after pm returned. The approval block is byte-identical, no
lane moved, twelve tasks before and after with the same ids and `files:`. The eleven-key schema, the
board's six values, T-11 and T-12 as the gate-rebuild tasks, and `handoff-validate.md`-at-`Done` with
no second mechanism all stand.

**THE BUILD DOES NOT START AT SIGNATURE.** The precondition is **FEAT-16 and FEAT-17**, both
`in_progress` at `a29ad06` and both writing `feature.yaml` live. The migration runs only once both
have returned for signature, and no feature may cross from signature into build during it. It has no
owner inside the plan: only the main session holds the cross-flow view.

## Open Questions

- Q1 CLOSED by the operator's correction of 2026-08-11. FEAT-15 migrates to `Done`. The withdrawn
  ruling's premise — "its plan is `approval: pending`" — was false at `a29ad06`.
- Q2 non-blocking: `validate-digest.py:182`'s orchestrator digest enum stays OUT of scope (D-13). It
  carries `blocked` while the six board columns have no `Blocked`, so collapsing it either invents a
  column or deletes a token `SubagentStop` routes on. Confirm the boundary.
- Q3 non-blocking, new: BRIEF.md SC-08 carries the clause "the format change neither silently
  disabled a check nor invented a violation" **twice** — spliced mid-sentence and again at the close.
  Every assertion is present and true; the splice only makes the criterion's scope read ambiguously.
  Fix is deleting the first instance. Not sent back: a lead round-trip costs more than the deletion.
- Q4 non-blocking, new: T-12's exemption note line pins three tokens — `exempt`, the feature name,
  `handoff` — because T-08's verify greps for them. Deliberate coupling between a carve-out gate's
  output wording and another task's assertion; it rots silently if either side is reworded. T-08's
  verify also sits at 48 of DEC-182's 50 machine-field lines, so the next editor must fold, not append.
- Q5 non-blocking: T-04/T-08 `files:` are the glob plus one literal lane anchor, not 17 literals.
  Enumerating all 17 measures 54 machine-field lines against DEC-182's 50 cap, so
  `check-plan-routes.py` rejects the enumeration. The 14-path original was exactly 50, at cap.
- Still open from the original pass, relayed and not re-litigated: the
  `.harness/team-config.yaml:15-16` harness defect — it claims check-domain exits 0 on a payload with
  no `agent_type`, which is FALSE at HEAD. Not FEAT-14's to fix.
