# Applying the operator's cycle-1 rulings — FEAT-58 — 2026-09-10

**All seven rulings are applied to `plan.yaml` and `BRIEF.md`; one write is blocked by a missing
tool verb and is recorded as a decision instead.** The plan now carries 16 tasks (T-12 deleted,
T-17 added) and 14 decisions (D-13, D-14 added). `check-plan-routes.py` on this plan: **0
violations, exit 0**, 11 informational DEVIATION lines — the DEC-174 carve-out working. Approval is
still `pending`; no `status:`, no station, no `panel:` byte was touched.

## Disposition per ruling

- **Q1 (high, PF-5945852660e0bd21e2b5aabb8cd48383) — resolved by amendment, HEAD-content
  precondition, not an edge.** T-10 and T-08 each carry `git merge-base --is-ancestor <fix-sha>
  HEAD` against the checkout's OWN HEAD, `<fix-sha>` resolved at execution time and recorded (never
  a literal). Non-carrying checkout: left FULLY MATERIALISED, row `skipped-pending-merge` with
  reason; T-08 creates such a worktree FULL and exits 0. Both intents state why a `depends_on` edge
  cannot close it (`${CLAUDE_PROJECT_DIR}` hook registration → own-branch gates → the 1-of-88 /
  EXIT=0 shape). T-09 was amended too, because the guard lives in the script T-09 writes and T-10's
  `--verify` is what grades it live: `--verify` now exits non-zero for a live worktree that does not
  carry `<fix-sha>` yet shows a feature count of 1. The RED case is T-09 case (f) and it is in
  T-10's verify as a third command, so the verify can go red on a non-carrying worktree.
- **Q2 — T-12 CUT.** `delete-items --task T-12 --reason "<operator's reason>"`, exit 0. D-05 no
  longer mandates the dispatch-guard mechanism (frame is declared by the reader's recorded output;
  the residual narrows to an API bypass, which T-13's lint targets). D-13 records the cut with the
  operator's reasoning so it is not re-proposed. Downstream references cleaned: D-11 (`T-05, T-06
  and T-12 are NOT relocated` → drops T-12), T-07's reader list (dispatch-guard row removed), T-14
  (the `harness-spec-driven` prose bullet and that file dropped from `files:`), T-01 (`corpus_read`
  caller list).
- **Q3 — `linked_worktrees` split out as T-17** with REQ-12 (corpus root read-only AND enforced),
  new SC-15, a failing-first test (`tests/integration/test-check-domain-worktree-tier.py`), and the
  measured `-0.1751 ms/checkout` carried as its cost statement. T-06 no longer carries the fix and
  points at T-17; T-17 `depends_on: [T-06]` because they share `check-domain.sh`.
- **Q4 — all four.** (a)+(b) landed in ONE `amend` of `T-04.intent`: byte-for-byte parity struck
  (exit status + verdict set instead), frame lines kept, prose call-count pin deleted; the matching
  prose pin was deleted from T-03 in its own write, and T-06 case (f) is named as the single pin.
  (c) T-05 resolves the candidate feature from the branch with ONE plain local read, calls
  `corpus_read` zero times, and keeps the duplicate-owner denial reachable through a plain-local
  fallback; case (f) asserts the read budget. (d) T-07's sweep rows attribute to the owning suite
  instead of re-executing the seven refusal cases.
  - **Send-back, same day, fixed.** Both amended `intent` fields still spelled the pin as "T-06
    case (g)" — the lettering shifted when the `linked_worktrees` case left T-06 for T-17, so the
    pin is case **(f)**. Re-amended `T-03.intent` and `T-04.intent` (one `amend` each, own
    `--show` sha256), case letter only. Every case-letter cross-reference in `tasks:`/`decisions:`
    now resolves against the referenced task's own labels: T-01→T-08 (c), T-03→T-06 (f),
    T-04→T-06 (f), T-04→T-03 (b), D-12→T-08 (c). The surviving "T-06 case (g)" at `plan.yaml:222`
    is inside `panel:`, is the orchestrator's, and is a correct record of cycle 1.
- **Q5/Q6 — no plan change needed; the gloss was hunted.** The backwards DEC-174 gloss is gone from
  `BRIEF.md` (`## Constraints`, now "BLOCKS DISPATCH — not planning, and not execution", citing the
  corrected `.harness/notes/grilling-worktree-corpus-2026-09-09.md:89-92`) and from
  `T-16.execution_reason`. One occurrence SURVIVES and could not be written: `lanes.rows[2].reason`.
- **Q7 — lane row BLOCKED, recorded as D-14.** Measured this run: `plan-merge.py apply` with the
  lanes key exits **7** (`CONFLICT: top-level key 'lanes' carries two different values`);
  `plan-merge.py amend --key lanes` exits **2** (`not amendable — expected one of: tasks,
  decisions`). Every other route is denied by the shape gate, so the ruling lives in D-14 and in
  `T-14.execution_reason`. Issue #1596. Two things therefore stay stale in `lanes:` until a verb
  reaches top-level keys: the missing `.claude/commands/**` row, and that row-2 DEC-174 gloss.

## Traceability, derived from the file (`/tmp/feat58/verify.py`, re-runnable)

12 REQ, 15 SC in `BRIEF.md`; 16 tasks, 14 decisions in `plan.yaml`. Untraced REQ: **none**.
Untraced SC: **none**. Traces to a nonexistent id: **none**. `SC-14 → T-03, T-04` (the readers that
record the frame lines it now grades); `SC-15 → T-17`; `REQ-12 → T-17`. `depends_on`: no dangling
edge, no cycle, nothing references T-12, T-12 absent. Every task carries `change_type`,
`execution_mode`, `files`, `verify`, `traces`, `intent`.

## Open for the next reader

- The panel must re-run on the amended plan (cycle 2). Its seven cycle-1 findings still carry
  `disposition: open` — transcribing dispositions is the orchestrator's/validator-lead's write, not
  pm's, and I did not touch `panel:`.
- The `lanes:` block is stale in two ways (above). Whoever ships #1596 should transcribe D-14's row
  and fix row 2's reason text.
- T-05's candidate-by-name path cannot see a SECOND record claiming the same branch when the
  candidate resolves cleanly; the plain-local fallback covers the unattributable case and case (d)
  pins it. Stated in the intent, not hidden.
