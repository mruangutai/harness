# FEAT-53 — plan panel cycle 3 transcribed into `plan.yaml` `panel:` — 2026-09-02

**Done, and clean.** `panel:` now records `cycle: 3`, `last_run: 2026-09-02-02-validator`, both
readers `ran` with resolved personas, and **18 findings** — the 13 from cycles 1 and 2 all carried
forward, plus the 5 cycle-3 findings at `disposition: open`. `approval:` is byte-unchanged, no key
outside `panel:` moved, and the comment-line count is **191 before, 191 after**. One dispatch-asserted
disposition was NOT written because its source does not support it (see Open question Q1).

## How it was written

One `set-panel --value-file` call against the **main checkout's** binary
(`/Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py`; the worktree's
vendored copy predates the verb). Never `apply` — `apply` splices comment lines that no verb removes
(backlog row B-12). The 13 carried findings were not retyped: `/tmp/feat53_panel_c3.py` loads the
live `panel.findings`, mutates only `disposition`/`resolved_by`/`note` on the five rows a source
moves, appends the five new ones, and asserts round-trip equality of `cycle`/`severity`/`reader`/
`summary` for every pre-existing id before the value file is accepted. It reported `drift: []`.

## Carried forward — 13 ids, none dropped, in file order

`PF-328f8f3cf2485de796e819decb0475aa` (resolved), `PF-6aa9faae67525aae35fe81805ee2e677` (overruled),
`PF-7408d83abbae66d18e98f0a349f00dbb` (resolved), `PF-04c95fd65a8f1eb7b575bfee58d2b71b` (overruled),
`PF-3713534d84c8a79f7c478fb122760829` (overruled), `PF-55e28a6ee5221c9d78c8d4eb9a06dd60` (overruled),
`PF-d2fc95637db2222cfbec65f41fef202e` (overruled), `PF-ce8b018f5719dde6716225552ee32559` (overruled),
`PF-45518258bbae0f20d051abf3a4970419` (**open → resolved**, `resolved_by: T-16`),
`PF-3b85f18809cf5c4ad01b9008e1eace1c` (**open → resolved**, `resolved_by: D-22`),
`PF-0f3f4101447923844b00515e7312ce0e` (**open → backlog**, B-12),
`PF-aa9c41f6ef1f6c977d02645dc095d2d5` (**open → backlog**, B-13),
`PF-ed0712ea279a7c0ba45f4acb3ce97f6e` (**open → backlog**, B-14).

The 8 cycle-1 rows (2 `resolved`, 6 `overruled`) are untouched — no hunk falls in them.

## Each disposition move, re-verified at its source

- **`PF-45518258` → resolved / T-16.** Operator ruled FIX at `notes/answers-2026-09-01-plan-signature-c2.md:3-7`.
  `plan.yaml` T-16 `depends_on` now reads `[T-12, T-15, T-21]` (re-read at final state, `:976-979`).
  Both cycle-3 readers confirm closure; `scope` by a 22/22 acyclic graph check
  (`runs/2026-09-02-02-validator/digest.md:11,20`).
- **`PF-3b85f188` → resolved / D-22, with residue named.** Ruling Q3 FIX B-11
  (`answers-…-c2.md:17-24`) closes it for its **two named paths only**; the cycle-3 panel finds the
  same shape at a third, `.harness/metrics/trend.jsonl`, raised as V-1 (`digest.md:13,22,29`). The
  `note` says exactly that — resolved for the two, residue carried as V-1. Not closed outright.
- **B-12/13/14 → backlog.** Operator: "ACCEPT B-12, B-13, B-14 as backlog, labeled Dashboard"
  (`answers-…-c2.md:26`). The id→row mapping was re-checked against the briefing table
  (`ship-review-2026-09-01-plan-c2.md:97,98,99`) and holds: stale spliced comments = B-12, SC-17
  evidence kind = B-13, T-12 CI timing = B-14.

## The cycle-time-origin finding — deliberately NOT written

The lead's dispatch asked for a move to `resolved` / `D-14` on the assumption a panel finding carries
the cycle-time origin. **None does.** All 13 summaries were read; none concerns the BRIEF-approval
origin. `notes/research-FEAT-53-goalcheck-plan-c3.md:73-75` states it directly: "`B-6` needed no plan
edit: no live-YAML row for it exists" — it lives in `ship-review-2026-09-01-plan.md:125` and
`STATE.md:28-30`. No finding was invented and no unrelated id repurposed. Raised as Q1.

## Verification

1. `harness_yaml.load_plan` over the final file succeeds: `cycle: 3`,
   `last_run: 2026-09-02-02-validator`, **readers 2**, **findings 18**, cycle-3 ids `V-1..V-5` all
   `disposition: open`.
2. `git diff -U0` hunk headers, all inside `panel:` (which starts at line 1506 and is the last
   top-level key; file is 1689 lines):
   `@@ -1507,2 +1507,2 @@` · `@@ -1510,0 +1511 @@` · `@@ -1512,0 +1514 @@` · `@@ -1598 +1600,5 @@` ·
   `@@ -1608 +1614,6 @@` · `@@ -1618 +1629,3 @@` · `@@ -1627 +1640,3 @@` · `@@ -1635,0 +1651,38 @@`.
   59 insertions, 6 deletions, one file. `approval:` occupies lines 6-9 — no hunk reaches it.
3. Comment lines, `grep -c '^[[:space:]]*#'`: **191 → 191**.

## Open question

- **Q1 (non-blocking):** the dispatch's instruction 4 asserts a panel finding carrying the cycle-time
  origin, to be resolved by `D-14`. Source does not support it — confirmed at
  `notes/research-FEAT-53-goalcheck-plan-c3.md:73`. Nothing written. If the lead wants B-6's strike
  recorded in `plan.yaml`, it needs a new finding id computed from a real reader summary, or it stays
  where it already is: the cycle-1 review record and `STATE.md`.
