# research — FEAT-41 — operator rulings, cycle 5

**BLUF.** Rulings 1, 2 and 5 are applied. Ruling 3 is a confirmed no-op. Removing the
ready/Backlog exception costs **zero card moves**, not the "accepted cost" the ruling budgeted for —
but only because the same measurement uncovered two defects the exception was masking, both now
explicit work in the plan. Everything measured at worktree HEAD `8f8a6a3` against live board 3 on
2026-08-25.

## Ruling 1 — the measurement

Commands (run from the worktree root; full scripts reproduced by `T-10`'s new verify line):

```
python3 -c "import sys;sys.path.insert(0,'.claude/skills/harness/bin');import gh_board as g;
b=g.load_board('.');st=g.board_stations(b,'mruangutai/harness');print(len(st))"
```

- board 3 carries **656** cards for `mruangutai/harness`: 323 Backlog, 321 Done, 7 Plan, 4 Building,
  1 Review.
- **211** of those are task sub-issues that `plan.yaml` places (29 `plan.yaml` files, 259 tasks,
  of which 211 carry a recorded sub-issue number in `feature.json github.issues`).
- **0 of the 211 sit at Backlog.** The exception protected nothing that exists.
- Projecting every recorded task card and comparing against its live column, three ways:
  **with** the exception 16 mismatch; **without** it the *same* 16 mismatch, only their destination
  changes Backlog→Ready; **without it plus the record repair below, 0 mismatch.**

**The inherited 28 is wrong on both readings.** 29 `plan.yaml` files exist; only **7** carry a task
status the migration rewrites (55 task lines — consistent with `T-04`'s existing 55-hit anchored
grep). The `lanes:` row now carries the measured figures and names 28 as superseded.

## Two defects the measurement uncovered

1. **16 stale task statuses.** FEAT-12 (14) and FEAT-13 (2) shipped with their `plan.yaml` task
   statuses never recorded. All 16 issues are CLOSED and all 16 cards are at Done. A blind
   `pending → ready` migration would make the new single record contradict a closed issue and drag
   16 closed cards backwards. `T-04` now migrates a pending task inside a terminal feature to
   `done`, by rule rather than by name, with its own verify line.
2. **`derive_station` outranking a terminal station.** Every shipped feature has all tasks done, so
   `derive_station` returns `review` for all of them. With `project`'s parent rule as drafted
   (derive first), **22 of the 23 parent cards** project to Review while correctly sitting at Done —
   `T-10`'s pass would have moved 22 shipped parents backwards. `T-06`'s parent rule is now
   **terminal-first**, and a card at `TERMINAL_MARKER` is absent from the mapping (which clears
   FEAT-28). With both, parent mismatches drop 23 → 1.

## The one-time pass

Landed in **`T-10`**, as a specified step with its own verify line, not a footnote. Measured cost:
**0 station writes, 1 card added** (issue 223, FEAT-12's parent, genuinely absent from board 3).

**No INV-26 red window opens** between `T-04` and `T-10`, because the record repair lands in the
same task as the migration. The single expected red is FEAT-12's absent parent card, which appears
when `T-06` routes the compare through `project` and closes at `T-10`.

## Ruling 2 — the strike form

Reproduced from the two live examples, `DECISIONS.md:3228` and `:4436` (both read at `8f8a6a3`):
two parts per strike — a bold in-place sentence at the clause naming the strike, the date, DEC-188
and the amendment; plus an amendment section stating what the clause *said*, that it is struck, and
what holds instead. None of DEC-203 / DEC-191 / DEC-182 carries an amendment today, so each is
amendment 1. `D-09` reversed; `T-12` retitled and reshaped; its `verify:` and the 30-word index-row
cap warning are untouched.

## Ruling 5

Landed as **`D-12`**, a `decisions:` row — the already-supported plan-level shape. I verified a new
top-level key would *also* be safe (`harness_yaml.load_plan` validates only `tasks:`;
`check-plan-routes.py` has no top-level allowlist — both greps empty), but nothing reads such a key,
so it would be decoration, whereas a `D-NN` row is read at approval.

## Ruling 3 — no-op, re-confirmed

`grep -rn -i "glossary" BRIEF.md plan.yaml` → exit 1, zero hits. Nothing edited. Run digests and
`notes/*` untouched.

## Open

- **Q1 (non-blocking):** issue 223, FEAT-12's parent, is not on board 3 at all. `T-10` adds it. If
  the operator would rather it stay off the board, `T-10`'s hard verify needs an exemption.
- **Q2 (non-blocking):** FEAT-28 is `abandoned` with its card at **Done**. `project` now places no
  card for it, so the board keeps a Done card for an abandoned feature. Nobody has decided whether
  that card should move.
