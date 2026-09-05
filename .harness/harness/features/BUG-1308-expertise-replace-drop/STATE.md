# STATE

## Current

- feature: BUG-1308-expertise-replace-drop
- run: .harness/harness/features/BUG-1308-expertise-replace-drop/runs/2026-09-05-renumber-dec218-product/digest.md
- squad: product
- status: awaiting_user

Build phase, three of four tasks DONE and committed. T-01 (30b47d2b) added the `ops` subcommand —
`resolve_ops` is a pure function keyed on the stable (section, id) pair, never on an index, so a
replace never moves an entry and multi-op results are order-independent. Verified on disk: the diff
to expertise-merge.py removes ZERO lines across four pure-addition hunks, which is REQ-07 (apply
path unchanged) proved mechanically rather than asserted. T-03 (e44e2199, main-session-direct under
DEC-174) realigned the distillation contract. T-02 (4929479f) added case11..case20; 119 integration
checks pass / 0 fail, and only the authorised file was touched, so case18's no-production-bypass
rule holds.

Two defects were found by measurement and routed back to the main session, both in its exclusive
T-03 lane, both fixed: (1) T-03's first draft moved the ops vocabulary out of the yaml example's
`op:` key into prose, which would have made T-02 case17's mechanical harvest fail loudly — the
normalised file carries ~14 other pipe-separated runs from markdown tables, so the `op:` key is the
only unambiguous anchor; restored at 48e001a1. (2) T-03's bash block carried a bare relative path,
the single repo-wide violation of the instruction-path anchor rule; fixed at 018fba56. Anchor test
now exit 0 across all rows.

BLOCKING THE OPERATOR: BUG-1308's decision is renumbered DEC-216 -> DEC-218 on the operator's
binding ruling, because BUG-1303 keeps DEC-216 and DEC-217. DEC-215 was the highest entry on the
worktree branch, on local main and on origin/main when both features were planned, so the collision
was invisible to either plan. The amendment is applied and verified — nine live references plus a
new D-16 recording the renumber, T-04's verify moved all four of its 216s, BRIEF SC-10 moved, and
the literal ruling string `replace and drop through the ops subcommand` is untouched. The cycle-1
panel finding at plan.yaml:246 deliberately RETAINS "DEC-216" as transcribed history: it is the
validator lead's own text under `panel.transcription_rule` and its finding id is a hash over that
text, so editing it would break the id and falsify the record. **plan.yaml still reads
`approval.status: approved` against amended content — only the main session can re-sign, and that
signature is what the feature is now waiting on.**

T-04 (documentor — SPEC 5.3, DEC-218, DECISIONS-INDEX) remains parked on TWO gates: the operator's
re-signature of the amended plan, and the serialized decision-doc write boundary, which the main
session is holding shut until BUG-1303's PR merges (a rebase onto updated main is to follow).
Checked and settled so the documentor need not: check-instruction-paths.py's scope does NOT include
.harness/harness/docs/, so T-04's invocation text needs no anchoring.

Remaining after T-04: qa test-matrix gate, simplify (before the pin), then pin review_sha.
Cycles used 5 of 8. Worktree: .claude/worktrees/harness/BUG-1308-expertise-replace-drop.

Cycle accounting note: the DEC-218 renumber consumed a product run but is NOT counted as a cycle.
DEC-157 defines rework as a FAIL routed back, an unmet-SC re-dispatch, or a lead-reported send-back;
this was an operator-mandated amendment forced by an external feature's numbering, none of the
three, and the lead reported cycles 0. The two T-03 fixes ARE counted, because each was a defect
routed back for repair.

Log:
- 2026-09-05: plan opened; feature.json and STATE.md instantiated; station -> plan.
- 2026-09-05: BRIEF + plan drafted (PASS).
- 2026-09-05: goal-check c0 FAIL, 3 must_fix + 3 advisory; routed back — cycle 1.
- 2026-09-05: plan repaired; goal-check c1 PASS, all six closed.
- 2026-09-05: plan panel c1 FAIL, severity_max high, 7 findings; Advisor answered A1/A2/A3; panel
  transcribed, D-14 records the rulings; returned to the operator for signature.
- 2026-09-05: operator ruled REVISE not overrule; consolidated revision applied — cycle 2.
- 2026-09-05: goal-check c2 PASS (R1-R4 all met); plan panel c2 PASS, severity_max med, no gating
  finding, cycle-1 HIGH confirmed closed.
- 2026-09-05: cycle-2 meds closed and both cycles' dispositions recorded — cycle 3; INV-32's third
  reader recorded; goal-check c3 PASS; three intent imprecisions closed.
- 2026-09-05: plan SIGNED (approved). Station -> building.
- 2026-09-05: T-01 eng segment PASS, no send-backs; verified on disk and committed 30b47d2b.
- 2026-09-05: T-03 executed by the main session (DEC-174); vocabulary anchor regression found by
  measurement and routed back — cycle 4; restored 48e001a1.
- 2026-09-05: T-02 validator segment delivered green but returned ESCALATE on an instruction-path
  violation in T-03's file; T-02 committed 4929479f; anchor fix routed back — cycle 5; fixed
  018fba56 and re-verified (anchor exit 0, integration 119/0).
- 2026-09-05: DEC numbering collision with BUG-1303 detected BEFORE dispatching T-04; operator ruled
  BUG-1308 becomes DEC-218; pm amendment applied and verified; awaiting operator re-signature.

## Open Questions

- Awaiting the operator: re-signature of the amended plan. `approval.status` still reads `approved`
  from the pre-amendment signature; the mapping is main-session-only, so neither the orchestrator
  nor pm can reset or re-sign it.
- Record loss, low impact, NOT recoverable: during the renumber run, pm overwrote
  `runs/2026-09-05-01-product/state.yaml` — the plan-phase product run's 394B checkpoint — before
  noticing the directory was occupied. `check-domain.sh` guards `digest.md` but not `state.yaml`.
  The file now falsely attributes an `amend-dec218` step to the plan run. It cannot be restored:
  `.gitignore:7` (`.harness/*/features/*/runs/**`) means it was never tracked. The canonical record
  survives — that run's 6143-byte `digest.md` is intact and feature.json's `runs[]` entry is
  unchanged. The orchestrator attempted removal of the corrupted file and `bash-write-guard.sh`
  correctly BLOCKED it as outside its domain; escalating rather than evading. Two harness defects
  are implied: `state.yaml` is unguarded where `digest.md` is guarded, and nothing stops an agent
  writing into an occupied run directory.
- Harness defect, non-blocking, for the harness owner — now seen FOUR times (plan panel c1, plan
  panel c2, the c2 revision dispatch, and the T-02 build run): a subagent returns host status
  `failed (exit 1)` while emitting a well-formed digest and a complete artifact. In the T-02 case it
  cost a second qa spawn purely to distinguish a real green from a crashed one. A valid return that
  exits 1 is indistinguishable from a real failure to the tier above.
- Harness defect, non-blocking: `check-state.sh` INV-32 (`:533`) requires a `goalcheck` entry in
  `panel.readers`, but `plan-panel.yaml` defines only `should-not-exist` and `scope` — the goal-check
  runs in the PRODUCT segment. Nothing in the team file or the playbook tells the recorder to add the
  third entry, so the honest record fails the invariant until someone measures it. Recorded there as
  `ran`, persona harness-pm, because it did run.
- Process observation, non-blocking: the T-02 re-run spawn ran the project-wide unit suite despite an
  explicit instruction to run only the four named acceptance commands. It found a genuine defect, so
  the outcome was good, but the instruction was not followed.
