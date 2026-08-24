# Rulings fix round — what changed, what I measured, what is still the operator's

**Both rulings are applied and all four must-fixes are closed — but ruling 1 forces one edit to
`check-state.sh`, which `SC-10` forbade. That is the one thing the operator must weigh at signature.**

## The consequence neither review round could see

INV-26 (`check-state.sh:1234` `_EXPECT`, compared at `:1303-1315`) maps a task status of `done` to
the board's `done` column. It has always agreed because `close-task` closed the sub-issue at commit
and GitHub's `Item closed` workflow moved the card. Under ruling 1 the sub-issue is deliberately
**open** and stands at `building`/`review` for the whole Review phase, so **every `done` task of
every in-flight feature becomes an INV-26 violation** — in the gate that runs at every `/harness`
door and before every commit, this feature's own validate phase included. Both dodges are worse: a
task status INV-26 does not map is silently skipped (a gate weakened by the back door), and a
standing violation teaches the operator to read violations as noise. So: `D-24` + new `T-22` (a
bounded widening, the operator's own hand under DEC-174 am.4), `SC-10`'s list drops to four files,
new `SC-20` grades the widening's bound, `T-11` now depends on `T-22`.

## The four must-fixes

- **M1 CLOSED, re-derived independently.** I parsed every `test-*.py` in `bin/` with `ast` at
  `46ee87c`: **18 five-key station maps in 9 files**, 19 edits (`test-factory-claim.py`'s
  `repo_board` needs signature + dict). arch-eng's list is right and simplify-eng's is short by
  `test-factory-integration.py:339`. `T-02`'s `files:` already covered all nine; its line anchors
  did not — several moved, and the fixture-site list is now re-derived. Also named: three sites that
  must NOT change (`test-gh-board.py:146,:154`, `test-factory-config.py:157`).
- **M2 CLOSED** — `T-08 depends_on: [T-02, T-07]`, already applied by the dead round; verified.
- **M3 CLOSED** — `T-03` primitive 0 `project_resolve` plus `T-04`'s "no path may call
  `project_create` on any outcome other than `project_resolve` returning None", and the
  not-single-select case exits 2 with zero mutations. Verified against `factory_gh.py:435-457`.
- **M4 CLOSED, remedy = keep `feature`, carry integration in `test-factory-integration.py`**
  (`D-12`). Reason: `integration.detect` is a closed filename list and `harness.json` has three
  concurrent writers, so the detect-list remedy costs a dev-ops task; the change types are honest;
  `test-factory-integration.py` is already in both lists and is the only file that forks a real
  process against a stub `gh`. **Both counts in `D-12` were wrong** — the list is 22 filenames and
  `INTEGRATION_SCRIPTS` is 22 names, not six and fourteen. Corrected in plan and brief.

## Citations re-derived at `46ee87c` — the ones that MOVED

`_EXPECT` `:1184`→`:1234` · `check-state.sh` `load_board` `:1147`→`:1197` ·
`_apply_parent_rule` `gh_board.py:177`→`gh-sync.py:177` · `factory_decompose.py` ready write
`:411`→`:414` · `gh-sync.py` open-skip `:583`→`:584` · integration counts six/fourteen→22/22 ·
`test-factory-{land,decompose,claim}` fixture lines shifted 1–3. **Still resolve:**
`factory_config.py:41,:44,:134` · `factory_gh.py:30,:186,:400,:435-457,:465` ·
`gh-sync.py:177,:187,:520-531,:574,:592,:621,:626-627,:645,:714,:744,:791` · `factory_claim.py:302` ·
`factory_decompose.py:393` · `harness.json:102,105,113,119,121,127,134,141,148` ·
`harness-init/SKILL.md:174,189,200` · `SKILL.md:131,191,192` · `feature-schema.json:32`.
**Falsified by a merge:** FEAT-32 shipped, so SC-16's FEAT-32 shape (`status Review`, `#700` at
`Building`) is no longer live — `#700` is CLOSED/COMPLETED. It stays a written fixture, relabelled.
`#85` and `#98` re-checked live: still OPEN, `feature.json` still `Done`.

## Found here, in neither digest

1. `.claude/skills/harness/templates/harness.json:156` tells a joining repository to declare
   "exactly the five keys" — the scaffold for REQ-01 itself. New **`T-21`** (main-session-direct;
   `--resolve` = NOBODY).
2. `.harness/harness.json` `github.board._note` opens "Four keys" — already wrong at five, inverts
   at six. Folded into `T-02`.
3. `T-14`/`T-19`/`T-20` still carried a "three branches, ruling outstanding" framing for `Ready`
   that the brief's own SETTLED section had superseded; `T-20` would have returned itself unstarted.
   Removed.

## Still the operator's

**Q1 (blocking):** ruling 1 cannot be built without widening INV-26. Accept `T-22`/`SC-20` and the
four-file `SC-10`, or reopen the ruling. I applied the ruling and drafted the remedy; the signature
is yours.

## Gate output at return

`check-plan-routes.py` → `0 violation(s) across 2 plan(s)`, exit 0 (five DEVIATIONs, all declared).
`check-state.sh` → exit 1, one violation: `BRIEF.md is NOT approved`. Finding set **byte-identical**
before and after this round's edits. `approval:` and `## Approval` untouched, both `pending`.

---

# Cycle 2 — the DAG defect was four collisions, not one; ruling 3 attributed; the branch is behind

**BLUF.** M2's shape is generic, and fixing only the pair the operator named would have left three
more standing. I checked the whole property — *for every file, are all its writers totally ordered?*
— and found **20 unordered writer pairs across 8 files**, in four independent families. Four
`depends_on` edges close all 20. The DAG stays acyclic and the property now returns 0.

## 1. Every concurrent-writer collision, measured

Computed over `plan.yaml`'s transitive closure at the pre-fix state:

| File family | Unordered pair(s) | Edge added | Why this direction |
|---|---|---|---|
| `gh-sync.py`, `test-gh-sync.py` | T-07/T-13, T-07/T-16, T-08/T-13, T-08/T-16 | `T-13: +T-08` | Keeps both accepted chains' internal order and yields `T-07 → T-08 → T-13 → T-16`. T-07/T-08 are localized guards inside existing functions; T-13 adds a new subcommand and T-16 edits line 592, which sits ABOVE T-07/T-08's insert points (621, 645, 744), so it survives their drift. Putting T-13's structural change first would move every anchor the other three cite. |
| `board_lifecycle.py`, `test-board-lifecycle.py`, `test-factory-integration.py` | T-17/T-05, T-17/T-06, T-17/T-15 | `T-17: +T-06` | The file grows subcommands: provision (T-04) → audit (T-05) → the audit's STATUS class (T-15) → reconcile (T-06) → retitle (T-17). Retitle is the only subcommand nothing depends on, so it appends last to a finished entry point. |
| `test-factory-integration.py` | T-02/T-03 | `T-03: +T-02` | T-02's fixture inventory was re-derived at `46ee87c`. If T-03 lands first, its new fixtures sit outside that inventory and can reintroduce a five-key station map T-02 already cleared. Costs one link of parallelism on the critical path; correctness outranks it. |
| `DECISIONS.md`, `DECISIONS-INDEX.md` | T-09/T-19 | `T-19: +T-09` | T-19's intent already SAYS "after T-09's amendment". The ordering existed in prose and was absent from the graph — the runner reads the graph. |

Resulting topological order: `T-01 T-02 T-03 T-07 T-09 T-21 T-04 T-08 T-05 T-13 T-10 T-14 T-15 T-16
T-06 T-19 T-22 T-11 T-17 T-20 T-12 T-18`. Writers of `gh-sync.py`: `T-07 T-08 T-13 T-16`. Writers of
`board_lifecycle.py`: `T-04 T-05 T-15 T-06 T-17`. Both total.

Each new edge silently ages the successor's `46ee87c` line anchors, so T-03, T-13, T-16 and T-17 each
gained one `ORDERING:` paragraph telling the doer to re-derive by symbol rather than by number.

## 2. Ruling 3 applied

- `T-09`'s intent gains a bullet naming the operator's 2026-08-23 ruling and `notes/rulings-2026-08-23.md`
  as the warrant, and demotes the parity argument to the ruling's own reasoning rather than the plan's
  inference. `D-01`'s `because` already cited ruling 3 from cycle 1; unchanged.
- `BRIEF.md`'s parity sentence drops the falsified clause and records the withdrawal: re-verified at
  `46ee87c`, `board-station.py:74` takes `station` straight from `argv` and `:153` passes it unchanged
  to `gh_board.set_station`. No task in this plan touches that file. The one call site where declaring
  stations does buy something is `gh-sync.py`'s hardcoded `"Building"`, which `T-07` de-hardcodes.

## 3. The inherited premise, settled by measurement

Amendment 2 is real and merged; **this worktree is one commit behind it.**

- `gh pr view 725` → `state: MERGED`, `mergedAt 2026-08-23T02:15:04Z`, merge commit `e3392fd`.
- `e3392fd` is the tip of `origin/main`.
- `git rev-list --count HEAD..origin/main` → **1**; `origin/main..HEAD` → 8. `HEAD` is `46ee87c`,
  whose last merge from `main` was `2c0a33c` — the commit immediately before `e3392fd`.
- On `origin/main`, `DECISIONS.md:5634` is `### DEC-186 amendment 2` and `DECISIONS-INDEX.md:204`
  already reads `am.1-am.2 ... bounded to four purposes`. Neither exists in this tree.

So the dispatch's "zero commits behind `main`" was the wrong half. Nothing was authored here either
way, and `DECISIONS.md` / `DECISIONS-INDEX.md` were not touched — documentor lane.

**Recommendation, not a decision.** Merging `origin/main` is a precondition of signature, and it
should happen BEFORE the build for two independent reasons: (a) `DECISIONS-INDEX.md:204` in this tree
asserts the three-purpose bound that `REQ-02` contradicts, so a reviewer grading `REQ-02` against this
tree reads a live contradiction; (b) `T-09` and `T-19` both append to `DECISIONS.md` and regenerate the
index, so a merge deferred past the build collides with their output. `:204` needs no owner —
`e3392fd` already corrects it.

## Gate output at return, cycle 2

`check-plan-routes.py` → `0 violation(s) across 2 plan(s)`, exit 0. Six DEVIATION lines across the two
plans (FEAT-28 T-05, T-06; FEAT-33 T-11, T-12, T-18, T-22), every one declared `main-session-direct`.
`check-state.sh` → exit 1, exactly one VIOLATION:
`.harness/harness/features/FEAT-33-board-lifecycle-native/BRIEF.md is NOT approved`. Expected during a
plan phase awaiting signature (`STATE.md:38-40`, Q6). `approval:` and `## Approval` untouched, both
`pending`.
