# UAT — BUG-20261006-fleet-planning-recovery — SC-08
status: passed
branch: main (recovered Kaya record landed as 30c06581, #2189)
review_sha: d5f87d9e8fab2908bd1c5cada104454ace9e91fa
accepted_by: operator (mruangutai), 2026-11-21 — "i accept"

## Setup
Main checkout `~/GitHub/harness` at origin/main, with `K=.harness/kaya/features/FEAT-01-kaya-platform`. Every step is read-only.

The main session ran the commands at the operator's request ("run U-01 to U-07 for me") and showed the outputs. The operator inspected them and accepted.

## Steps

- U-01 (SC-08): `jq` the factory and github bindings in `$K/feature.json`.
  expect: factory.repo and github.repo are mruangutai/kaya; milestone 1, parent 16, T-01…T-10 → #17…#26, source [14], recovery complete.
  result: as expected.

- U-02 (SC-08): read `.github.history`, milestone 100 and #2116–#2126 in mruangutai/harness.
  expect: one archived mruangutai/harness mapping (milestone 100, parent 2116, tasks 2117–2126), and none of those numbers in the live mirror.
  result: as expected. Milestone 100 is closed (0 open, 10 closed). #2116–#2126 are CLOSED NOT_PLANNED, with none updated after 2026-10-11.

- U-03 (SC-08): `gh issue view 14 --repo mruangutai/harness`.
  expect: untouched by the repair.
  result: CLOSED, last updated 2026-09-09, before the repair. No milestone; label `harness` only.

- U-04 (SC-08): hash the authorization note and read the evidence references.
  expect: the note is inside the Kaya feature and the references point at it.
  result: sha256 `a6ec5e09…`. Runs 2, 3 and 6 and the archived mapping all reference `notes/research-fleet-planning-recovery-authorization.md` inside the Kaya feature.

- U-05 (SC-08): `jq` the runs; hash the simplify digest.
  expect: two FAILs with evidenced 0 and 1 cycles; the simplify run BLOCKED and refused; its digest byte-identical.
  result:
  - 2026-10-05-2 is FAIL, 0 cycles, with operator-history evidence.
  - 2026-10-05-6 is FAIL, 1 cycle, with operator-history evidence.
  - 2026-10-05-3 is BLOCKED with an operator-history refusal.
  - Feature total cycles_used is 1.
  - The digest sha256 is `d0e28f4d…`, the same as the T-03 capture.

- U-06 (SC-08): read the live Kaya mirror and project 9.
  expect: the mirror is in mruangutai/kaya and its cards are at Ready.
  result: milestone #1 is open with 10 issues. Parent #16 is OPEN with sub-issues #17–#26, all OPEN. Project 9 shows #14 and #16–#26 at Ready.

- U-07 (SC-08): `check-state.py --feature FEAT-01-kaya-platform`, plus the plan task statuses.
  expect: exit 0 with no bypasses; no Kaya implementation started.
  result:
  - Exit 0.
  - The plan station and all 10 tasks are `ready`. The last run is 2026-10-05-8-simplify-product, PASS.
  - The first attempt exited 1 on an unrelated repo-wide INV-29: a leftover FEAT-2206 worktree. That worktree was removed by its own session, and the re-run exited 0.
