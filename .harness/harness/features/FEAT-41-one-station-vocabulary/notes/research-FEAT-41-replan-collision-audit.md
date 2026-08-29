# Collision audit — FEAT-41 plan vs the rebased tree (0d4845b)

**The plan survives. One task loses a third of its scope, thirteen carry re-derived anchors, and
three verify lines could never have passed.** No task is dead. Nothing signed changed: approval is
`pending` in both artifacts. `plan.yaml` parses; `check-plan-routes.py` exits 0, 0 violations across
1 plan. Only `plan.yaml` and `BRIEF.md` were modified.

The old pin `e5afc19` → HEAD `0d4845b` moved 187 files. `ee66ae2` is still an ancestor of HEAD, so
every "measured at ee66ae2" citation stays resolvable and is kept as a historical reading beside the
re-derived one.

## Verdicts

`CARRY` T-03 only. `RE-DERIVE` T-01, T-02, T-04–T-09, T-11–T-14. T-10 is `RE-DERIVE` with one
clause `DEAD`. Per-task reasons are in the DIGEST, which is what the orchestrator routes on.

## The four dispatch findings

1. **T-14 — CONFIRMED intact, one justification falsified.** The insertion point survived: the
   per-feature loop opens at `check-state.sh:202` (glob now two levels deep), `val()` at `:227`,
   `runs` at `:237-244`, the INV-6 block at `:246-253` (was circa `:221-229`), the validator
   predicate at `:250`, `subprocess` already imported at `:49`. INV-32 still free — highest is
   INV-31. `CHECK_STATE_BIN` at `test-check-state.py:17`, `case_u` at `:1195`. **What died is the
   REASON, not the instruction:** the task justified computing the plan path relative to the git top
   level "because root is CLAUDE_PROJECT_DIR". Since FEAT-42 T-12, `check-state.sh:38` resolves root
   through `harness_boundary.resolve_root(_selfdir)`. The instruction still stands — the harness root
   need not be the repo top — so the justification was rewritten and the instruction guarded against
   simplification.
2. **T-10 — CONFIRMED dead in part.** FEAT-40 merged; the violation closed itself. Measured here:
   FEAT-40's `feature.json` reads `Done`, `check-plan-routes.py` skips it as shipped, and a full
   `check-state.sh` run emits **zero** `INV-26` lines (its one violation is FEAT-41's unapproved
   BRIEF). Both ship defects remain real — `gh-sync.py` is byte-identical to `e5afc19`. The repair
   was also **redundant**: FEAT-40's `plan.yaml` carries no top-level `status` at all, and T-07's
   migration (already a dependency of T-10) is what writes it. So T-10 dropped the FEAT-40 file, its
   `git diff --quiet` verify line, and the repair paragraph; the `check-state.sh` run survives as a
   regression bound. **SC-09 was re-based** — it would otherwise be true by construction — onto the
   clause that still fails today: FEAT-40's plan carries no `status: done`.
3. **STATE.md is stale — CONFIRMED, reported not edited.** `STATE.md:20` records "0 violations across
   2 plans" (now 1 plan) and `:22` records "INV-26 FEAT-40, which T-10 closes" (now closed).
4. **T-05 — REFUTED as "already present", CONFIRMED as "already contradicted".** The playbook's
   `Writing plan.yaml (D-04)` section exists at `.omp/agents/harness-orchestrator.md:86-103` but
   presents **two routes**, not the three bullets the task named, and route two at `:92` *actively
   instructs* the surgical `Edit` this task closes. Neither agent file names `set-task-station`. Both
   verify clauses were run against both files and both discriminate. Nothing to subtract; the "three
   bullets" description and the `:78` anchor were corrected to `:96`.

**Step-5 claim-schema check, stated explicitly: no task assumes the old claim schema.** No task's
`files:`, `intent:` or `verify:` names `inflight_registry.py`, `dispatch-guard.sh` or
`validate-digest.py`, and the only "claim" hits in the plan are the English word and `factory_claim.py`
(board task claiming, unrelated). Nothing added.

## Three verify lines that could never pass — found by running them

- **T-04**: `grep -rn "^    status: pending" .../*/plan.yaml ; test $? -eq 1`. Nine of forty feature
  dirs carry no `plan.yaml`; this shell expands the glob to its non-existent members, so `grep` exits
  **2** with or without matches. Replaced with a Python assertion, proved discriminating (56 hits, exit 1).
- **T-13**: the exclude grep returns 36 lines, the 36th being gitignored
  `__pycache__/harness_yaml.cpython-314.pyc`, which carries `plan-merge` as a compiled constant and
  is read *before* any test re-imports the module. Added `--exclude-dir=__pycache__` → exactly 35.
- **T-01**: same class — `__pycache__/factory_config.cpython-314.pyc` carries `_STATION_KEYS`. Same fix.

## Measurements that held, and ones that did not

| Held at HEAD | Moved |
|---|---|
| SC-02: 27 lines / 5 files, per-file split identical | Every `check-state.sh` anchor +25; `check-domain.sh` +29 |
| SC-04: ten `set_station` sites | `factory_claim` +5, `board_lifecycle` +2/+3, `check-plan-routes` +6 |
| `_EXPECT\|_st26` = six lines; `_renamed`/`_no_finding` = 4/4 | `factory_config._STATION_KEYS` 41 → **39** |
| feature-schema 11 props / 8 required | plan files 29 → **31**; pending task lines 55 → **56** |
| `gh-sync.py`, `gh_board.py`, `factory_land.py`, `factory_decompose.py`, `feature-schema.json` unchanged | `DECISIONS.md` strike anchors 3228/4436 → **3235/4443** |
| T-13: 13 tracked files / 35 lines | next free DEC 205, not 204; run-unit-tests PREFIX `:101` → **`:115`** |

**Two claims were wrong before the rebase and are corrected:** T-04's "four remaining pending
literals" is **three** (line 1438 at `ee66ae2` carried no such literal), and the BRIEF's
"`test-gh-sync.py` run by two tasks, 298 s" is **three tasks, ~447 s** — T-07's verify has always run it.

**One scope addition, and it is a re-derivation:** `check-state.sh:1061` and `:1599` now carry comments
citing DEC-192 for the case-sensitivity T-07 ends. They spell `Done` in backticks so SC-02's
quoted-literal grep cannot reach them. T-07 was told to rewrite both.

## Not touched, deliberately

Every `.claude/skills/harness/bin/...` spelling (`.agents/skills` is a tracked symlink, mode 120000);
the four template paths; T-03 entire; the dangling commit ids quoted as historical measurements in
T-13/T-14 prose (PRINCIPLES rule 15); D-07's benchmark; D-11's live-board figures (external system,
needs an authenticated run — T-10's verify re-measures them); the Q1/Q2 dependency on T-12's recording
form, still open and still a signature condition.

## Open

- `lanes.resolved_at` is **`plan.yaml:12`**, now `0d4845b` — the sha the lanes were actually
  re-verified against today. One line, one Edit, if the orchestrator re-pins.
- `STATE.md:20` and `:22` need the orchestrator's correction; `review_sha` in `feature.json` is the
  orchestrator's to re-pin.
- The shell's glob expansion is non-POSIX here (a glob expands to non-existent members, making
  `grep ... ; test $? -eq 1` unusable). Raised as a harness defect in the DIGEST, not worked around
  beyond the one verify it broke.
