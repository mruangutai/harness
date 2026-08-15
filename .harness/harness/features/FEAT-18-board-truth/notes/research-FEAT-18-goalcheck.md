# Goal-check — FEAT-18-board-truth — 2026-08-13-06-product

**Verdict: FAIL. Seven of the eight live criteria are met; SC-05 is not met.** The board writes ship
and are correct. The *detector* — INV-26, the half of the feature that makes drift visible without a
human looking — does not fire in the window it most needs to: a plan with a task recorded `done` and
the rest `pending`, nothing `building`. Judged at HEAD `6303683`; source is the pinned tree
`6d2d61b` (only `.harness/features/FEAT-18-board-truth/` changed since).

**Send-backs: zero.** Clean first-pass panel, `cycles_used: 0`.

## SC-05 — not met, and why the suite is green anyway

SC-05's leading sentence binds *any* feature whose plan records a task `done` while that task's card
sits in `Backlog`. Verified at source myself at HEAD:

- `check-state.sh` INV-26 does `if _derived is None: continue` — skipping the **whole** feature, the
  per-task card comparison included. That loop needs no parent verdict: `_EXPECT` maps
  `pending|building|done` to columns per task, independently.
- `gh_board.derive_station` returns `None` for a **legal** mix — one task `done`, the rest
  `pending`, nothing `building`. No illegal status is needed to reach it.
- Every INV-26 fixture is single-task: `_inv26_fixture` writes exactly one `T-01`, so `case_v`'s
  non-vacuity pair (v.1 mis-columned → violation, v.2 corrected twin → clean) proves the check on an
  **all-done** feature only. The `continue` is unexercised in the direction that suppresses a finding.

So SC-05's *proof clause* is satisfied and its *claim* is false for the between-tasks window — which
is exactly when a session starts, and is the shape of FEAT-14's failure this feature opens with.
Under the rule that a criterion is graded on its full text, that is `not_met`, not `partial`.

**What would have to be true for SC-05 to be met:** a done task's card comparison runs, and a
mis-column is reported, even when the plan derives no parent station — with a multi-task mixed
fixture binding that branch. The remedy sites (`check-state.sh`, `gh_board.py`) are DEC-174
carve-outs; the routing question is **E-01, already pending with the operator**. Nothing here
proposes or attempts a repair.

## The seven met criteria

| SC | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | met | automated / integration | `test-gh-sync.py` checks "start-task sets T-02's OWN issue station to Building" (`--id ITEM_326`, `--single-select-option-id OPT_BUILDING`) and "the sub-issue close was ATTEMPTED" / "still closes the sub-issue" |
| SC-02 | met | automated / integration | `test-gh-board.py` `derive_station` cases (building→Building, all-done→Review, mixed→None, empty→None) + "close-task sets the parent to Review" (`ITEM_40`+`OPT_REVIEW`) and "close-task on a Done feature makes no item-edit call at all" |
| SC-03 | met | automated / integration | `test-gh-sync.py` the loud pair, one fixture: "stderr carries the gh-sync: ERROR line naming issue 40" with the following call still made; "loud pair (gh absent): one SKIP line, exit 0" |
| SC-04 | met | inspection | `notes/review-harness-code-reviewer-c0.md` — `retry\|while True\|for _ in range` zero hits outside comments in `gh-sync.py`/`gh_board.py`; both `set_station` call sites single `try`/`except`, no loop |
| SC-06 | met | automated / integration | `test-check-plan-routes.py` `case_25`'s named subchecks `case_25a_status_building_is_CLEAN` and the capital-B violation naming `LEGAL_TASK_STATUSES`, plus the unargumented live-corpus run, exit 0, `0 violation(s)` |
| SC-07 | met | inspection | reviewer read T-05's diff (four keys + board-flip block gone, deny path untouched) and **ran the gate live**: `permissionDecision: "deny"`, reason names `FEAT-99-nope` |
| SC-09 | met | inspection | `gh-sync.py` `main()` dispatches exactly six subcommands (`open`, `start-task`, `close-task`, `abandon`, `ship`, `backlog`); `SKILL.md` carries six owner rows for the same six plus the literal `git checkout -b feat/…` line — completeness checked at source, T-06's verify loop exit 0 |

**SC-08 is struck** (before signature, DEC-188 shape). It gets no row and is never counted unmet.

## Two things the record should carry

1. **SC-01's proof clause overreaches its own signed design.** It says the criterion is proven by "a
   recorded fake `gh` that captures the field-set call". The harness makes **no** field-set for the
   `Done` half — D-03/T-03 mandate that `close-task` writes no sub-issue station; `grep` for a `Done`
   station value in `gh-sync.py`/`gh_board.py` returns nothing. The card reaches `Done` through
   GitHub's own `Item closed` workflow, read enabled on board 3 on 2026-08-13 and recorded in D-03's
   `because:`. The harness's whole causal contribution *is* test-asserted, so I graded it met: the
   strongest proof the signed standard permits is the proof. The contradictory clause stands in the
   signed BRIEF — reported, not edited (Q1 below).
2. **REQ coverage.** All eight REQ trace to shipped tasks (REQ-01→T-01/T-03, REQ-02→T-03,
   REQ-03→T-02/T-03, REQ-04→T-03, REQ-05→T-04, REQ-06→T-02/T-03/T-05, REQ-07/08→T-06). Nothing was
   dropped. **REQ-05 is the one delivered incompletely** — its code exists and reports correctly on
   the paths it reaches; SC-05 names the window it does not.

## Observations, banked against nothing

- The operator's clean INV-26 run against the real board 3 (six cards `Done`, parent #326 deriving
  and reading `Review`) is an operator observation for the ship record. **It closes zero criteria**:
  every automated SC here runs against a fake `gh` (`functional` `cmd: null`, DEC-187) and the rest
  are inspection. It does not convert any inspection criterion to automated.
- T-02's and T-04's mutation figures are a **relayed claim with no substantiating artifact** —
  `notes/mutation-record-T-02-T-04.md`. For those two files the record holds *suite green*, not
  *mutants killed*. VL-01 is itself a case the suite does not cover.
- `SKILL.md`'s divergence from T-06's signed `intent:` step 2 is D-02's amendment working, not a
  defect. Checked and not raised.

## Open questions

- **Q1 (non-blocking):** SC-01's proof clause ("captures the field-set call") cannot cover its own
  `Done` half, which the same signature's D-03/T-03 forbid the harness from writing. The prose
  stands in the signed BRIEF; correcting it is a re-signature, not a record fix. Reported for the
  operator, not reinterpreted here.
- **E-01 — referenced, not raised.** Whether the operator takes VL-01's fix main-session-direct or
  ships with the gap recorded is already pending with the operator from the validator run. SC-05's
  `not_met` is the same gap seen from the goal side.
