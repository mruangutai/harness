# Handoff — FEAT-54-handoff-done-when, plan → build — written 2026-09-02, seq-3

## Next

Start the build with T-01 when the operator requests it. `BRIEF.md` and `plan.yaml` were both signed
by Mike Ruangutai on 2026-09-02. Goal-check c3 passed, the panel ran all three readers with nothing
high, critical or unrated, and every finding is dispositioned. T-01 is `main-session-direct` under
DEC-174; follow the task's test-first sequence and its `verify` block exactly.

## Trust

- Rulings landed: T-06 case (g) is a fixture-corpus case naming no real path, SC-04 is
  `verify: inspection` with its evidence home pinned, T-09 states `exclude: .claude/worktrees/**` in
  intent AND verify, D-10's `because` carries the grammar-stability clause and the Q3 confirmation —
  verified by parsing plan.yaml/BRIEF.md back from disk after each run.
- Rejections honoured: SC-14, T-03(h), T-06(h), D-04, T-09's probe scope, T-12, SC-09, D-01, D-03 are
  unchanged — verified by reading each back and by the c3 panel's independent leave-list check.
- `plan.yaml` `panel:` reads cycle 3, `last_run: 2026-09-02-c3-validator`, three readers `ran`, nine
  findings, and NO disposition says "no operator ruling exists" — verified by parsing the key.
- 12 tasks T-01..T-12, decisions D-01..D-08 + D-10, `status: plan`; both approval blocks are signed
  by Mike Ruangutai on 2026-09-02 — verified from `plan.yaml` and `BRIEF.md`.
- `check-plan-routes.py`: 0 violations across 6 plans; the DEVIATION lines are the declared DEC-174
  carve-outs — verified-at working tree during cycle 3.
- No `approval.rulings` entry is required: no high, critical or unrated finding remains open. The
  separate missing-writer defect is tracked by issue #1157.
- cycles_used 9 of 10, runs 16 of 20 — one cycle left; raising the budget is the operator's call.
- UNVERIFIED: whether SC-04's review-time run will actually be performed and recorded at review. It
  is an instruction to a future reviewer, not a gate, and the panel said plainly it cannot judge it.

## Dead ends

- Do not `Edit`, `Write` or redirect into `plan.yaml`: one writer, `plan-merge.py`. `apply` is
  add-only (exit 7 on a changed value); `amend --show` then `--expect-sha256` changes a field;
  `set-panel` replaces the panel whole, so anything that must survive goes in the value file —
  verified this run by using each.
- Do not add an `approval.rulings` entry for this plan: no blocking finding is being accepted as risk.
  Issue #1157 tracks the missing writer for a future plan that genuinely needs an override.
- Do not re-open the four ruled findings. Two were accepted and implemented, two were rejected by the
  operator; a reader re-deriving one of them is producing noise the operator already priced.
- Do not pass relative paths or shell variables to a write command: `bash-write-guard` resolves
  relative paths against the MAIN checkout and refuses any unexpanded `$var` target.
- Do not let a dispatch omit its run-dir slug: two contexts have already collided on one on this
  feature. Name the slug in the dispatch.

## Working set

- .harness/harness/features/FEAT-54-handoff-done-when/plan.yaml
- .harness/harness/features/FEAT-54-handoff-done-when/BRIEF.md
- .harness/harness/features/FEAT-54-handoff-done-when/notes/signature-inputs-c3.md
- .harness/harness/features/FEAT-54-handoff-done-when/notes/research-FEAT-54-goalcheck-plan-c3.md
- .harness/harness/features/FEAT-54-handoff-done-when/runs/2026-09-02-c3-validator/digest.md
