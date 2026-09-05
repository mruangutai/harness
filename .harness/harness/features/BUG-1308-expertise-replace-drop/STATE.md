# STATE

## Current

- feature: BUG-1308-expertise-replace-drop
- run: .harness/harness/features/BUG-1308-expertise-replace-drop/runs/2026-09-05-renumber-dec218-product/digest.md
- squad: product
- status: in_progress

Build phase: THREE OF FOUR tasks done and committed, T-04 outstanding and blocked on the operator.
Returned at the operator's explicit instruction rather than holding an idle orchestrator open.
Build is INCOMPLETE — no `review_sha` pinned, qa gate and simplify not yet run. Cycles used 5 of 8.

T-01 (30b47d2b) added the `ops` subcommand: `resolve_ops` is a pure function keyed on the stable
(section, id) pair, never on an index, so a replace never moves an entry and multi-op results are
order-independent. T-03 (e44e2199, main-session-direct under DEC-174) realigned the distillation
contract. T-02 (4929479f) added case11..case20. DEC-216 -> DEC-218 renumber applied, verified,
operator-signed and committed at cb6b2875 (BUG-1303 keeps 216 and 217; DEC-215 was the highest entry
on every branch when both features were planned, so the collision was invisible to either plan); the
operator waived a new plan panel for it as a pure identifier substitution.

HANDOFF (build -> T-04 remainder, written at cb6b2875). Recorded here, not in
`notes/handoff-build.md`, because that file's shape gate cannot currently be satisfied by this
feature — see the first Open Question. This is the documented disk-only successor path.

NEXT. Dispatch `harness-product-lead` -> `harness-documentor` for T-04 (plan.yaml, station `ready`,
the only unexecuted task); inputs are plan.yaml T-04 `intent:` (three edits, ONE commit) and BRIEF.md
SC-10. TWO preconditions the main session controls must BOTH hold first: BUG-1303 merged (hotfix
#1348 was in flight for a Git auto-maintenance fixture teardown race), and release of the serialized
decision-doc boundary plus a rebase onto landed main. RECHECK the decision number before the
documentor writes — DEC-218 is the operator's ruling but is contingent on what BUG-1303 lands; if it
moved, that is a pm amendment, not an execution-time fix, because the number is pinned in T-04's
verify and in SC-10. After T-04: qa test-matrix gate, then SIMPLIFY, then pin `review_sha` LAST — an
apply commit after the pin invalidates the panel's verdict.

TRUST. unit 58/0, integration 119/0, anchor test exit 0 — all re-run by the orchestrator at
cb6b2875, not relayed. REQ-07 (apply path unchanged) holds mechanically: the expertise-merge.py diff
removes ZERO lines across four pure-addition hunks
(`git show 30b47d2b -- .claude/skills/harness/bin/expertise-merge.py`). `check-instruction-paths.py`
scope excludes `.harness/harness/docs/` (`:46-56`), so T-04 needs no path anchoring. UNVERIFIED: the
post-amendment re-signature — the main session reported SIGNED/APPLIED with no diff because the
fields were already identical, and the orchestrator can neither write nor re-run `sign-approval`;
confirm before treating the signature as fresh.

DEAD ENDS. Do NOT re-anchor T-02 case17's harvest onto the SKILL.md prose sentence — the normalised
file carries ~14 competing pipe-separated runs from markdown tables, so only the `op:` key is
unambiguous (verified at 48e001a1). Do NOT renumber plan.yaml:246 to DEC-218: its finding id is a
hash over the reader plus that text, and the operator explicitly approved keeping it as history. Do
NOT split T-04's three edits across commits to work around the boundary; the operator refused that
option by name. Do NOT try to restore `runs/2026-09-05-01-product/state.yaml` — never tracked.

WORKING SET. `plan.yaml` (T-04 at :765-841) · this `STATE.md` · `.harness/harness/docs/SPEC.md`
(section 5.3 begins :904) · `.harness/harness/docs/DECISIONS.md` (DEC-215 is the last entry; copy its
shape) · `.harness/harness/docs/DECISIONS-INDEX.md` (row shape at :215).

## Open Questions

- **Harness defect, BLOCKING the build handoff note.** `notes/handoff-build.md` cannot be written:
  no legal `## Done when` authority both resolves AND binds for a feature whose directory exists only
  in a worktree. All three failure modes measured: (1) `plan-task:` and `brief-sc:` resolve
  `feature_dir` against the PROJECT ROOT (`handoff_done_when.py:116,131`) and the main checkout has
  no `.harness/harness/features/BUG-1308-.../`, so both are unresolvable — the guard strips the
  `.claude/worktrees/<segment>/` prefix; (2) `finding:` requires `F-\d+` or `PF-\d+` (`FINDING_RE`,
  `:14`) but this repo's panel finding ids are hex, e.g. `PF-f4d258f365f54f04d9cc976baf0ad981`; (3)
  `approval:` is the only resolvable type and BOTH approvals now read `approved`, so the block binds
  nothing and is refused — correctly, by its own rule. The gate behaves as designed; the defect is
  that the design leaves a worktree-only feature with signed approvals no legal pointer at all. The
  predecessor's `handoff-plan.md` passed only because the approval still read `pending` then.
  Suggested fix: resolve `plan-task:`/`brief-sc:` against the feature-tree root rather than the
  control-plane root (DEC-214's two-anchor rule), and widen `FINDING_RE` to the hex ids
  `panel_findings.py` actually mints.
- Record loss, low impact, NOT recoverable: during the renumber run pm overwrote
  `runs/2026-09-05-01-product/state.yaml`, the plan-phase product run's 394B checkpoint, before
  noticing the directory was occupied. `check-domain.sh` guards `digest.md` but not `state.yaml`. The
  file now falsely attributes an `amend-dec218` step to the plan run. It cannot be restored:
  `.gitignore:7` (`.harness/*/features/*/runs/**`) means it was never tracked. The canonical record
  survives — that run's 6143-byte `digest.md` is intact and feature.json's `runs[]` is unchanged. The
  orchestrator attempted removal and `bash-write-guard.sh` correctly BLOCKED it as outside its
  domain; escalated rather than evaded. Two implied defects: `state.yaml` is unguarded where
  `digest.md` is guarded, and nothing stops an agent writing into an occupied run directory.
- Harness defect, non-blocking — now seen FOUR times (plan panel c1, plan panel c2, the c2 revision
  dispatch, the T-02 build run): a subagent returns host status `failed (exit 1)` while emitting a
  well-formed digest and a complete artifact. In the T-02 case it cost a second qa spawn purely to
  distinguish a real green from a crashed one.
- Harness defect, non-blocking: `check-state.sh` INV-32 (`:533`) requires a `goalcheck` entry in
  `panel.readers`, but `plan-panel.yaml` defines only `should-not-exist` and `scope` — the goal-check
  runs in the PRODUCT segment, so the honest record fails the invariant until someone measures it.
- Process observation, non-blocking: the T-02 re-run spawn ran the project-wide unit suite despite an
  explicit instruction to run only the four named acceptance commands. It found a genuine defect, so
  the outcome was good, but the instruction was not followed.
