# STATE

## Current

- feature: FEAT-18-board-truth
- run: .harness/features/FEAT-18-board-truth/runs/2026-08-13-06-product/state.yaml
- squad: product
- status: review

**The validate phase is COMPLETE and the feature is stopped on one operator decision.** Panel and
goal-check both ran, in that order, at pin `6d2d61b`. Two rework cycles of ten; eight runs of twenty.
No cycle was spent on either run — both reported zero send-backs, and a first-pass FAIL that finds a
real defect is not rework (DEC-157).

**The feature's board writes are correct; the detector it exists to build is not.** Seven of the
eight live criteria are met. **SC-05 is `not_met`** — reported, not fixed and not re-scoped.
`check-state.sh:1143-1146` does `if _derived is None: continue`, which skips the **entire** feature:
the per-task card comparison (`:1166-1182`), the mirror-never-ran clause (`:1154-1159`) and the
parent check (`:1184-1194`) alike. `gh_board.py:114-118` returns `None` for a **legal** plan mixing
`done` and `pending` with nothing `building` — the ordinary window between one task closing and the
next starting, which is when a session most often opens. No typo is needed to reach it. I measured
this myself rather than relaying it: `derive_station` on `{T-01 done, T-02 pending}` returns `None`,
and every INV-26 fixture is single-task (`_inv26_fixture`, `test-check-state.py:1307`), so the
suppressing branch is unexercised and a green suite could not have caught it. Both remedy sites —
`check-state.sh` and `gh_board.py`, under `.claude/skills/harness/bin/` — are DEC-174 carve-outs.

**E-01 is the open decision and it is the operator's alone:** take the fix main-session-direct, or
ship FEAT-18 with the SC-05 gap recorded. No fix was dispatched and no repair loop was proposed.

**The rest of the panel is clean.** security PASS (the board-write surface is shell-injection-safe —
list argv, bound GraphQL variables, literal-only station values; three `info` notes, one re-ranked
to `low` for a session-entry read with no timeout). ui PASS, scoped out — no rendered surface, no
DESIGN.md; the two operator-facing surfaces were checked, not skipped. qa was **skipped by me**, with
its reason in the run's `state.yaml`: it PASSED the `test_matrix` gate at this exact pin in run
`2026-08-13-05-validator` (`matrix_ok: true`, 0 send-backs) and no source file has changed since —
`git diff --name-only 6d2d61b..HEAD` returns only this feature's own bookkeeping and notes.

**EIGHT criteria are live, not nine.** `BRIEF.md` carries `SC-01`..`SC-09`; `SC-08` is struck. The
live set is SC-01..SC-07 and SC-09. The earlier "nine" assumed an `SC-10` the BRIEF does not contain.

**Live board 3 agrees with the plan, and no criterion asked it to.** Every automated SC asserts
against a fake `gh` (`functional` has `cmd: null`, DEC-187); the rest are `inspection`. The clean
INV-26 run against the real board belongs in the ship record as an operator observation and closes
**zero** criteria.

**Do not let a reviewer "fix" the `SKILL.md` divergence.** T-06's signed `intent:` step 2 still lists
"no board configured" among the whole-invocation skips — the exact falsehood D-02's amendment
(`5c835c7`) corrected. `SKILL.md` was written against the amended D-02. The divergence is the
amendment working.

## Open Questions

- **E-01 (BLOCKING, operator only):** VL-01/SC-05's only remedy sites are `check-state.sh` and
  `gh_board.py`; `check-state.sh` is a DEC-174 carve-out, so the fix cannot be dispatched through a
  team run. Fix it main-session-direct, or ship with the gap recorded?
- **Q-SC01-GRADE (non-blocking, operator may re-grade)** — a NEW question, not the BRIEF's Q1
  below, which stays closed: SC-01 was graded on its achievable half, SC-05 on its
  full written text — two standards. SC-01's signed proof clause ("captures the field-set call")
  cannot cover its own `Done` half, because the same signature's D-03/T-03 forbid the harness from
  writing a `Done` station; the card reaches `Done` via GitHub's `Item closed` workflow. On a
  full-text reading SC-01 would be `not_met`. Surfaced rather than reconciled — correcting the clause
  is a re-signature, which is not the run's to make.
- Q1/Q3 were answered at signature (`BRIEF.md` `## Approval`); Q2 was overtaken by the 2026-08-13
  revision; Q4 by operator re-signature at `3862a64`; Q6 by operator amendment at `5c835c7`; Q8 by
  the main session, which recorded the unsourced T-02/T-04 mutation figures as a relayed claim in
  `notes/mutation-record-T-02-T-04.md` — those figures are never repeated as measured coverage. None
  is to be reopened.
- Standing constraint: **a `not_met` criterion is reported, never fixed and never re-scoped.**
  Amending `BRIEF.md` stops the run and goes to the operator. SC-08 is **struck** — eight live
  criteria — and is never counted `not_met`.
