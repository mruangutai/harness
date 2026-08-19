# Layer-0 batch B — FEAT-29 — SUPERSEDED 13:45, two new blocking items ahead of T-07

**BLUF.** All nine tasks are now written and T-03 landed green on unit. **But the branch is RED on
`--kind integration`, and I bisected the cause to T-01/T-02 rather than accepting the report that it
was pre-existing.** Six named INV-26 checks fail. Both new blocking items are layer-0 and both must
clear before T-07 runs.

Order is now: **(A) the INV-26 fixture · (B) the stray log file · (C) T-07 · (D) T-09.**

---

## A. BLOCKING — six INV-26 checks are red, and it is issue #588's exact shape

`--kind integration` fails six named checks in `test-check-state.py`, each with the same trailer:
**`(no INV-26 line)`**. INV-26 goes *silent* precisely where it must speak — v.1 mis-columned card,
v.4 empty issues map, v.5 recorded issue absent from the board, v.6 parent disagreeing with the
derivation, v.8 mis-columned done card, v.12 empty `factory.issues`.

**The eng squad reported these as pre-existing. That was true in its frame and false in yours,** so I
bisected in a throwaway worktree rather than relaying it:

| Commit | Contains | `test-check-state.py` |
|---|---|---|
| `bee6234` | batch A only, no code | **0 FAIL** |
| `9fd11d7` | T-01, T-02, T-04 | **6 FAIL** |
| `29c3e9d` | + T-03 | 6 FAIL |

The member measured *its own* baseline at `d610822`, which already contained T-01/T-02 — so
"unchanged from baseline" was honest and the frame was wrong. T-03 added nothing.

**Diagnosis, and production is NOT at fault.** The fixture's fake `gh` is documented in its own
docstring as *"a fake gh whose `project item-list` page puts each card wherever the caller says"*
(`test-check-state.py:1315-1322`). T-02 replaced that call with `gh api graphql`. The fake does not
answer it, `project_item_stations` raises, and `check-state.sh`'s `except Exception: _stations = None`
swallows it — so INV-26 records nothing. The live path is fine: my direct read returned all **486**
board-3 cards with correct `Backlog`/`Done` stations for **5 points**. **The fixture is stale, not the
code.**

**Why this is yours and not my squad's.** `test-check-state.py` is the test file of `check-state.sh`,
and am.4 puts the enforcement layer's test files inside the DEC-174 carve-out. `--resolve` says
`harness-backend-dev, harness-dev-ops` — but that is the write axis, and the execution carve-out is
the separate one that is mechanized nowhere.

**Why nothing caught it.** T-02 is `change_type: logic`, which the matrix maps to `unit` alone, and
`test-check-state.py` lives in `INTEGRATION_SCRIPTS`. T-02's `verify:` was structurally incapable of
seeing this. That is a finding about the matrix, not about the member.

**This is also the strongest possible argument for your positive control** — same silent-failure
shape, one layer down. It is worth noting the control would *not* have caught this one: it exercises
the real board, where the code works. Fixture and control catch different things and you need both.

## B. BLOCKING — an untracked log file is in the tree, written by the existing suite

`.harness/logs/gh-cost-2026-08-19.jsonl` is untracked right now. **I did not stage it.** T-03's plan
signs `HARNESS_GH_COST_LOG` default-ON, and `factory_config.harness_root()` falls back to the real
checkout when `CLAUDE_PROJECT_DIR` is unset — so `test-board-station.py`, `test-gh-board.py` and
`test-gh-sync.py`, none of them in T-03's `files:`, now write a real log on every suite run.
Reproduced twice by the member; `bash-write-guard` then correctly refused to let it clean up after
itself. `--resolve` on that path is `NOBODY`.

Four routes were identified and none is the squad's to take: export `CLAUDE_PROJECT_DIR` before suite
runs · gitignore the pattern · set `HARNESS_GH_COST_LOG=0` inside `run-unit-tests.sh` (am.4 granted
that file for the registration edit only) · tighten `factory_config.py`'s fallback (harness-wide).
This is the plan-digest's old Q4 and my B-8, now live.

## C then D — T-07, then T-09, unchanged

Both still yours, both still gated on **A** clearing — a red INV-26 fixture means the invariant under
measurement is not provably intact. The rewritten T-07 `verify:` is good: I read it, it loads the
control, filters `T-08`, asserts exactly **7** lines (I counted 7 in the file myself), requires a
`POSITIVE-CONTROL` section, and emits the `REJECT, do not explain` message. That gate can fail.

## THE MIRROR IS STILL FROZEN

No `start-task`, no `close-task`, for any task, until T-07 lands. `plan.yaml` now records T-03 `done`
and its subcommand is deliberately unrun. Seven control lines still depend on cards reading `Backlog`.

## What landed, verified at my tier

T-03 in its six approved files. **Unit: 160 PASS / 0 FAIL / exit 0**, up from the 139 baseline — my
own run, not relayed. Both mandated mutations proven red on *named* checks and reverted under sha256
verification; the member's first attempt aborted the suite instead of reddening it and it refused to
count that as evidence, which is exactly the distinction that matters. **Send-backs: 0.**
`cycles_used` stays at **3 of 10**. Branch tip `29c3e9d`.

The lead also self-reported writing a premature `BLOCKED` close under stop-hook pressure while T-03
was still in flight, and named it rather than quietly fixing it. One run, one member spawn.

## Still outstanding for me, after A and B clear

qa segment (the blocking `test_matrix` gate — T-03 is `change_type: feature`, so **unit AND
integration**, which is why A must clear first) → SIMPLIFY → re-run suites → pin `review_sha` at the
tip → panel → goal-check.

Budget: GraphQL 6/5000 at the start of this window; my spend this session is 46 points total.
`CLAUDE.md` remains uncommitted and untouched by me.
