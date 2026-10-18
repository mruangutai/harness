# Briefing — BUG-20261006-fleet-planning-recovery — pending plan ready for operator review

**Where it stands.** The five-task repair plan and BRIEF are complete and `pending`, with the four-angle simplify findings folded in by pm through one freshly registered product run (`2026-10-06-3-plan-product`, squad `product`, agent `harness-product-lead`). The lead's return was accepted by the host hook and its digest validates (`validate-digest.py harness-product-lead … → digest ok`). This disproves the earlier inference that every lead return in this worktree would be refused: run 2 was refused because it was registered as squad `eng` where this checkout's `digest_destination` requires `engineering` for harness-eng-lead; the run-2 BLOCKED/refused record is untouched. No signature, approval write, implementation, test/build/lint, commit, gh-sync call, GitHub or Kaya write occurred.

Assembled from: `runs/2026-10-06-3-plan-product/{digest.md,panel-c2.md,state.yaml}`, `notes/research-…-apply-plan.md` §Fold-in 2026-10-06-3, `notes/research-…-goalcheck-plan.md` (refreshed, single canonical), `notes/review-harness-code-reviewer-plan-c2.md`, `notes/ship-review-2026-10-06-2-simplify-eng.md` (S-table), `notes/main-session-plan-review.md`.

## Exact proofs (this cycle, orchestrator-run)

- `plan-merge.py check --file <plan.yaml> --root <worktree>`: `OK T-01 33 · T-02 7 · T-03 1 · T-04 1 · T-05 1 — CHECK: 5 task(s), 43 anchor(s) resolved, 0 failure(s)` (was 42; +1 is the S-7 index-generator content anchor on T-02).
- `plan-merge.py record-panel --cycle 2 --digest runs/2026-10-06-3-plan-product/digest.md`: exit 0, 5 PF ids CARRIED; `panel.readers`: scope ran · should-not-exist skipped (DEC-228: proportionality/form never buy a re-read) · design skipped (self-scoped out at c1, non-UI) · goalcheck ran.
- `feature-record.py propose-rework`: `{"rounds": 2, "minutes": 90}` (5 tasks / 3 per round, floor 2, cap 10; 45 min/round).
- `feature-record.py close-run … --verdict PASS --cycles-used 0 --code-grade n_a`: CLOSED; spend 3 runs / 70 min / 324,671 tokens; rework 0/0.
- `check-state.py --feature …` (worktree copy): exit 1 — INV-1 (BRIEF pending, expected), INV-7 (`cycles_used=0` with 1 FAIL run: the honest zero-send-back roll-up, the defect this feature repairs), DEC-156 (run-2 refused digest, preserved by design), INV-37 (no build_entry; remedy is `gh-sync.py open`, suspended for this feature). INV-46 cleared on close. Commit withheld; no bypass requested.

## What changed in the pending text

- **SC-02 (only changed SC):** interrupted remote creation with no durable number is refused and requires explicit operator-evidenced reconciliation; ambiguous/partial evidence refuses; no automatic read-back.
- **D-02** reworded to incremental confirmed-receipt saves + uncertain-create refusal + explicit `--adopt-receipt <role>=<n>` under target-local authorized evidence. Markers, scan, adopt-match, retry, poll, title-search removed from T-01/T-05; the "new DEC-203 read purpose" removed from T-02 and BRIEF Constraints. Known-mapping idempotence (repeat completion = durable no-op; same recovery ID resume without duplicates) preserved.
- **PF-2157d88… (med, proportionality/task):** resolved by T-01 via the panel's own alternative; its historical summary text is preserved as finding identity (set-panel disposition only). **PF-05621f… (low, form, c2 scope reader):** `factory_config.load_fleet` → existing `artifact_accessors.load_fleet`; resolved in-run.
- Fold-ins applied: S-1 single `resolve_binding` home; S-2 fixture sets both `FACTORY_GH` and `GH_SYNC_GH` with one shared contents handler so SC-01's no-Harness-mutation assertion is real; S-3 one `evidence_ref` `$def` + one resolver/verifier (set-rework/raise-cycles untouched); S-4 recovery/gate text via `recovery_command_for`; S-5 one `receipt_allows_merge` predicate replacing three literals; S-7 index-drift check on T-02 verify; S-8 no stored third cycle count; S-9 typed `refusal` object alone; S-10 `history[].previous` by `$ref`; S-11 full matrix once at pinned review_sha after T-02, before T-03. S-12 kept as unmeasured-ceiling caveat; S-6/S-13 remain build notes, no new tasks/SCs.
- Task count 5 (unchanged), all `execution_agent: main-session-direct`. D-01/D-03/D-04 and SC-01/SC-03..SC-08 substance unchanged.

## Cycles — honest count

`cycles_used` 0/10. Run 3 had zero genuine send-backs (scope reader PASS with one low form fix, applied same run). Run 1 FAIL (zero-send-back roll-up) and run 2 BLOCKED (refused return) are preserved exactly; neither is counted.

## Unresolved substantive tradeoff for signature

1. **Forward fleet-wide evidence duty** (SC-03; PF-aa1a… info, disclosed in BRIEF Constraints): every future `run-end` with new/changed per-run attribution — including a newly attributed zero — must carry authentic digest evidence. Not yet operator-approved; sign consciously or overrule `--overrule PF-aa1abfeee616fde328cd7f12af5ec561:<reason>`.

The removed marker read-back is NOT a signature question: the conservative default is applied and visible; the operator may reinstate only by re-planning.

## Residual backlog (strike by ID)

| ID | Nature | Row |
|---|---|---|
| B-1 | chore | feature-schema.json `$defs.timestamp`/`$defs.sha256` for new fields (S-6) |
| B-2 | enhancement | `close-run` derives the cycle count from the validated digest, drop `--cycles-used` (S-13) |
| B-3 | bug | A run registered with a squad name outside `digest_destination.LEAD_SQUADS` (`eng` vs `engineering`) is accepted by `run-start` but refused at the lead's return (#2110); `run-start` should refuse the mismatch up front |

## Next operator actions

`sign-approval --rework rounds=2,minutes=90 --decision <path>` (optionally `--overrule PF-aa1a…`), then separate recovery authorization, then build. Decide whether to commit the uncommitted planning artifacts under the four honest findings.
