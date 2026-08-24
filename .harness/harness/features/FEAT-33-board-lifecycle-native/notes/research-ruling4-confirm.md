# Ruling 4 confirmation at the merged tree — the plan is SIGNABLE

**YES, signable.** `T-22`, `D-24` and `SC-20` hold at `57e18ca` with no substantive change; the two
files they touch were not in either merge. Everything else this round was making the record match
the tree: ruling 4's station/state separation is now written down, DEC-186 am.2 is recorded as
present rather than pending, and two claims the merge falsified are corrected.

## 1. Citations re-derived at `57e18ca`

The merge (`git diff --stat 46ee87c 57e18ca`) touched exactly four files: `feature-worktree.py`,
`test-feature-worktree.py`, `DECISIONS.md`, `DECISIONS-INDEX.md`. **`check-state.sh` and
`test-check-state.py` were not touched**, so every `T-22`/`D-24`/`SC-20` anchor re-derived at
`46ee87c` still resolves.

| Citation | Verdict at `57e18ca` |
|---|---|
| `check-state.sh:1233-1235` `_st26` / `_EXPECT` | HOLDS, as the dispatch read it |
| `check-state.sh:1304` `_want = _EXPECT.get(...)` | HOLDS |
| `:1305-1306` `if _want is None: continue` | HOLDS — the silent skip, correctly refused |
| `:1315-1318` `elif _found != _want:` + append | HOLDS |
| `check-state.sh:1197` `load_board` (T-01's inertness proof) | HOLDS |
| `test-check-state.py:1333` five-key `_board` literal | HOLDS |
| `test-check-state.py:1616` Icebox/Primed/WIP/Shipped map | HOLDS |
| `feature-schema.json:32` status enum | HOLDS (seven values, incl. `Abandoned`) |
| `run-unit-tests.sh:17` `UNIT_SCRIPTS` | HOLDS |
| `factory_config.py:41,:134` · `factory_claim.py:302` · `factory_decompose.py:393` | untouched by the merge |

**Nothing had MOVED.** One citation was imprecise rather than stale and is tightened: the plan and
`D-24` said the comparison sits at `:1303-1315`; it is `:1304-1318`. Corrected in both.

## 2. Ruling 4 written into the surfaces

- `BRIEF.md` lifecycle section now opens with **STATION vs STATE** and ruling 4's four-row table.
  Nothing in either file said a sub-issue closes at commit, and nothing said `Review` is
  parent-only — ruling 1 had already been applied.
- The gate paragraph no longer reads "the operator's to weigh at signature": it is RULED.
- `SC-10` still reads FOUR files, and the drop is now attributed to **ruling 4's acceptance** with
  ruling 1 named as the cause — not presented as pm's choice.
- `T-22`'s intent gains the warrant paragraph (ruling 4, station/state, the `Item closed`
  mechanism) and `D-24` gains the acceptance sentence.

## 3. DEC-186 am.2, and T-09 / T-19

Am.2 is in this tree: `DECISIONS.md` `### DEC-186 amendment 2 (2026-08-23)` and
`DECISIONS-INDEX.md:204` `am.1-am.2 ... bounded to four purposes, am.2's being /harness-init's
workflow read`. **No collision.** `T-09` and `T-19` amend **DEC-196**, both say so explicitly, and
`T-19` already carries "Do not touch DEC-186 ... its bound was already widened by amendment 2".
Both regenerate the index with `gen-decisions-index.py`, whose contract preserves everything right
of ` :: ` verbatim (its docstring, `:12-14`), so regeneration cannot flatten am.2's row.

## 4. Q4 — four calls

- **`T-01`'s harness-first departure — does NOT block.** It is disclosed in `## Constraints` under
  the heading the operator reads at signature; the breakage is latent (a `FleetError` naming
  `github.board.stations`, reachable only if a `factory_*` command runs against kaya-ai between
  the two merges) and loud. Signing ratifies a stated departure; nothing new is needed to decide it.
- **FEAT-31 on `run-unit-tests.sh` — does NOT block, and it is not the operator's.** Settled from
  the tree: FEAT-31 is `Done` and merged, and `run-unit-tests.sh:17` already lists
  `test-context-watch.py`. Among live features only FEAT-33's `T-04` writes that file (FEAT-26's
  eight tasks do not).
- **`SPEC.md:1868` — does NOT block.** It is genuinely falsified: `feature-schema.json:32`
  enumerates seven statuses and two features on disk carry `Abandoned`. But it is pre-existing, in
  a file no task here touches, and this plan already says the right thing (`Abandoned` is a status
  with no station — `T-19`, `SC-08`). Fixing it inside this feature widens the file set for a doc
  defect. **File it as an issue, the way #730 was filed.**
- **FEAT-26 concurrency — does NOT block signature; it is a scheduling call.** Found this round:
  FEAT-26 is `Ready`, `approved 2026-08-23`, **all eight tasks pending**, and its `T-05` writes
  `check-state.sh` and `test-check-state.py` — the same two files as `T-22` — while
  `T-02`/`T-03`/`T-04` write `gh-sync.py` and `T-08` writes `DECISIONS.md`. Neither plan is wrong;
  whichever builds second re-derives by symbol, and `T-22`'s intent now says so.

## 5. Two claims the merge falsified, corrected

- The DEC-186 bullet said "this worktree is one commit BEHIND" — now 0 behind at `57e18ca`.
- The concurrency bullet said "FEAT-31, FEAT-26 and FEAT-32 have all since MERGED". **False for
  FEAT-26**: what merged was its plan's signature (`2c0a33c`); its build has not run.

## 6. Gate output, verbatim

`python3 .claude/skills/harness/bin/check-plan-routes.py` → `0 violation(s) across 2 plan(s)`,
`examined 33 feature dir(s); 31 skipped as shipped`, **exit 0**. Seven DEVIATION lines across the
two plans (FEAT-26 T-05, T-06; FEAT-33 T-11, T-12, T-18, T-22), every one declared
`main-session-direct`.

`bash .claude/skills/harness/bin/check-state.sh` → **exit 1**, 437 lines, **exactly one VIOLATION**:
`.harness/harness/features/FEAT-33-board-lifecycle-native/BRIEF.md is NOT approved — halt that flow
and surface to the user.` Everything else is a `note`. Expected while the signature is pending
(`STATE.md:38-40`, Q6). No INV-26 finding — this feature has no `done` task yet.

`approval:` and `## Approval` are untouched and both read `pending`.
