# FEAT-41 fix cycle 1 — instrument repair, at ee66ae2

All nine blocking findings APPLIED, none rejected — every premise held when I re-derived it
against the tree. D-11 landed in T-06. Task count unchanged at **13 tasks, 12 main-session-direct**
(T-12 alone `team`, `harness-documentor`); `BRIEF.md:48` now states that. `plan.yaml` `safe_load`s,
every `verify:` is a literal block, `check-plan-routes.py` exits 0, both `approval:` blocks
`pending`.

## D-11, by task and line

`plan.yaml` `decisions:` gains **D-11** (after D-10), carrying the rejected option's cost verbatim —
six edits, no new import surface, zero runtime risk — and the reason it was rejected: a lookup miss
and "nothing to check here" share a code path, so divergence is invisible *by construction*.

It lands in **T-06**, which gains `check-state.sh` and `test-check-state.py` in `files:`:

- **Sub-clause 1, the fail-open dies.** T-06's intent deletes `_st26`/`_EXPECT` (circa `:1403-1405`)
  outright, builds `rec` from the `feature.json` the loop already holds, calls `project(_pdoc, rec)`
  once per feature, and **deletes** `if _want is None: continue`. An unplaced task id and a
  `FleetError` out of `project` are both violation lines naming feature, task id and value.
- **Sub-clause 2, DEC-174 re-checked.** T-06 stays `main-session-direct`; `execution_reason` now
  names `check-state.sh` as the gate script. `check-plan-routes.py` reports T-06's DEVIATION over
  the `.claude/skills/harness/bin/**` surface, exit 0 — the lane is correct.
- **A measurement that strengthens D-11:** `check-state.sh` *already* imports `gh_board`, and an
  import failure is *already* a loud violation at circa `:1337-1349`. The new failure mode the lead
  accepted is already paid for.
- **The window is closed without softening D-11.** T-04 renames `pending` out from under
  `_EXPECT`, so T-04 gains `check-state.sh` and repoints the six literals — including the
  **inverting** guard at circa `:1440` — as *not breaking a gate it renames*, explicitly not as the
  fix. T-06 then deletes the map. No ordering leaves INV-26 blind.

## Findings I re-derived rather than inherited

- **F-09a** `check-domain.sh`: the "deliberately absent" comment is **1011-1017**; **1018 IS the
  `SHAPE_PATTERNS` tuple**; the `RE_` block is 1004-1010. T-09's `1017-1022` would have deleted the
  tuple and `has_shape_rules`.
- **F-09b** `gh-sync.py:998` is inside `_to_backlog` (def 987). `cmd_backlog` is at **1166** and
  carries **no station logic at all**.
- **F-09c** `.harness/harness.json` uses `github.board._note` (:182); the **template** uses
  `github._board_note` (:156), one level up. Two spellings — T-01 now names both.
- **F-09d** `STATUS_ORDER` is **defined at :513**, used at :604 (and :548). Both change.
- **F-03** deletable unit is **1655-1691** exactly: 1692 blank, 1693 begins the results loop.
- **F-06 count corrected.** The reader's 31 was match-count. Line-count at ee66ae2 is **26 across
  5 files** (`check-state.sh` 13, `gh-sync.py` 7, `board_lifecycle.py` 3, `check-plan-routes.py` 3,
  `worktree_terminal.py` 1). Three are stale comments; T-04 now owns two of them so SC-02 can
  reach zero without excusing comments.
- **F-05 count corrected.** Ten today; **four** survive, not one — `board-station.py:153`,
  `board_lifecycle.py:1013` and `:1016`, plus gh-sync's single policy call. T-06's verify asserts
  the count `= 4`; the old bare pipeline exited 0 at ten and at one.
- **T-13 settled by measurement.** Main checkout: **1100** lines without `--exclude-dir=worktrees`,
  **35** with it. Worktree checkout: 35 either way. Exclude added; path list untouched.

## A new policy choice D-11 forced into the open

Routing INV-26 through `project()` would newly report every *unstarted* card as mis-columned,
because the old `_EXPECT` encoded `pending -> backlog` while a `ready` task's own station is Ready.
`project()` therefore carries **one documented exception**: a task at `ready` projects to the
**backlog** station, because `gh-sync open` lands every sub-issue there and nothing moves it until
`start-task`. This preserves today's semantics exactly and avoids board-wide churn across 28
features. Stated once, in `project()`'s docstring, read by both sides. Raised as Q4.

## Open questions — see the DIGEST

Q1 D-09's record shape; Q2 the glossary; Q3 the 149 s double-run; Q4 the `ready -> backlog`
projection exception.

## Cycle 2 — T-11's line-addressed deletion (remedy: BOTH)

**Conclusion.** T-11 now orders *and* content-anchors. Ordering alone leaves absolute numbers in the
task text; anchoring alone leaves T-04/T-06 free to add cases into the very unit being deleted.

- **Mutators of `test-check-state.py`, derived from the plan's own `files:` lists:** T-02, T-04,
  T-06, T-07, T-11. The send-back named four; **T-02 (`plan.yaml` files entry) is a fifth** and was
  missing from that list. T-10 only *runs* the file (runtime disclosure), it does not edit it.
- **T-11 `depends_on: [T-01, T-02, T-04, T-06, T-07]`** — T-01 kept as the mandate premise, the
  other four are every mutator. No cycle (checked); T-13 already depends on T-11.
- **Anchors, measured at ee66ae2:** unit is the comment `# --- ONE CASE PER KEY…` through the third
  `results.append` referencing `_no_finding`; `_renamed` occurs 4× (1662, 1674, 1681, 1688) and
  `_no_finding` 4× (1666, 1677, 1684, 1691), **all inside the unit and nowhere else in the file** —
  so both names are usable as absence assertions. Deletion stops before `allok = True`.
- **The grep still discriminates.** `Icebox|Drafted|Primed|Shipped` returns 6 lines today (1663,
  1664, 1672, 1673, 1680, 1687), every one inside the unit; none of those four words survives
  elsewhere in the file, and neither T-04 nor T-06 introduces them (both write the mandated
  vocabulary). `WIP` is likewise confined to 1664/1680. Two lines added: `_renamed|_no_finding`
  absent (catches the partial-deletion `NameError`, 8 hits today) and `grep -q FEAT-41` present
  (**0 hits today**, so the positive assertion discriminates).
- **`test-board-lifecycle.py:771-798` re-anchored too** — T-02 and T-07 both edit that file, so the
  "do NOT touch" span had the same defect. Now named as the case-5g block labelled `c3 regression:`
  with fixture `existing = ["Backlog", "Icebox", "Plan", "Ready"]`.

### Sweep across all 13 tasks for the same defect class

Every task's line references were extracted and cross-checked against the file→tasks map.

- **T-11 was the only bare span used as an edit address.** Fixed.
- **One residual, fixed in place: T-07.** It cites `_STATUS_TO_STATION_KEY at :445-448` for
  *deletion* in `board_lifecycle.py`, which T-02 edits at `:438` — seven lines above — and T-02 is
  an ordered predecessor. T-07 also carries `check-plan-routes.py:418/605-618/711` beneath T-04's
  deletion of `LEGAL_TASK_STATUSES` (line 415) and `check-state.sh:1577` beneath T-06's deletion of
  `_st26`/`_EXPECT`. All of these name their identifier, so they are navigation, not addresses —
  one paragraph added to T-07 saying so and instructing re-derivation.
- **Checked and clean:** T-02 (`check-state.sh circa 1403`) and T-04 (`circa 1403-1405`) have no
  ordering between them but touch **disjoint identifiers** (`_st26` vs `_EXPECT` keys, defaults,
  the `not any(...)` guard), and both use `circa` plus the identifier. Either order works; no edge
  added. T-09's `check-domain.sh:1004-1022` has **no predecessor** touching that file and already
  says "open the file and confirm the span". T-01, T-03, T-05, T-08, T-10, T-12, T-13 address no
  line in a file a sibling mutates.
