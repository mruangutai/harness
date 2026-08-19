# BRIEF — FEAT-25 claim feature root

## Problem

The factory cannot take work. `factory_claim.py:43` still builds its feature root as
`<harness_root()>/.harness/features`, the path unit 3 vacated in `d033b9d` when the features tree
moved to `.harness/harness/features`. Every plan read fails, so `_BlockerCache.task()` returns
`None` for every candidate, so `_blocker_gate` returns the edge-(i) blocking reason at
`factory_claim.py:140-142`. Verified by live probe at `ada8e99`: the constant's directory does not
exist, and a real plan (`FEAT-24 T-01`) resolves under the migrated path and nowhere else.

It fails closed — no wrong work is handed out, nothing is claimed twice — so the cost is not a
safety hole but a dead factory. Unit 8, the live kaya proof (#496), takes its work through this
tool and therefore cannot start.

The second cost lands on whoever debugs it. The skip message at `factory_claim.py:162-168` says
the issue's "title yields no matching plan task (edge (i), lost task identity)", pointing the
reader at issue titles and plan files. The cause is a directory that is not there. Nothing in the
diagnostic would lead anyone to the filesystem.

The whole unit suite is green over this, because `FEATURES_ROOT` is deliberately monkeypatchable
and every existing test overrides it (`test-factory-claim.py:342-343`; `test-factory-integration.py`
plants its fixture at the stale path under a redirected root).

## Goal

Make the factory able to claim work again, and make the refusal legible when a root is genuinely
absent. One constant, one diagnostic, and a test that can only pass against the corrected constant.
The correct root is decided on the record, so unit 7 inherits an answer rather than a guess.

## Requirements

- REQ-01: `factory_claim.py` resolves plan and feature-state files at the location where feature
  directories actually live, so a candidate issue whose plan task has no unfinished dependency is
  claimed rather than refused.
- REQ-02: When a candidate is refused because no plan could be read, the diagnostic names the
  absolute path that was tried and says the root or the plan file is missing — distinct from the
  message used when a plan loaded but held no matching task.
- REQ-03: The corrected root is proven by a check that fails against the pre-fix code, so the
  defect cannot recur behind a green suite.
- REQ-04: `factory_claim.py` is judged by the layout-migration detector on the features surface
  instead of being excluded from it.

## Success Criteria

- SC-01: `factory_claim.FEATURES_ROOT`, read as the unpatched module default, equals
  `os.path.join(factory_config.harness_root(), ".harness", "harness", "features")` and that
  directory exists in this checkout.
  verify: automated      evidence: unit
- SC-02: The assertion behind SC-01 is red against the pre-fix constant and green after — proven
  by running it once against the unmodified line before the change lands.
  verify: automated      evidence: unit
- SC-03: An end-to-end claim run whose feature directory sits at the migrated path exits 0 and
  emits its JSON payload, with no fixture and no test monkeypatching the module's root to make it
  so.
  verify: automated      evidence: integration
- SC-04: A candidate whose features root does not exist produces a stderr reason naming the
  absolute path tried and stating that no plan could be read there; a candidate whose plan loads
  but holds no task with the title's id still produces the edge-(i) text. The two messages are not
  interchangeable.
  verify: automated      evidence: unit
- SC-05: Every diagnostic added or changed by this feature goes to stderr; stdout still carries at
  most the single JSON payload.
  verify: automated      evidence: unit
- SC-06: The layout-migration detector reads `factory_claim.py` on the features surface and reports
  it `migrated`, and the features surface verdict for the real repository root stays CLEAN.
  verify: automated      evidence: unit
- SC-07: No existing assertion in `test-factory-claim.py`, `test-factory-integration.py` or
  `test-layout-migration.py` is deleted or weakened, and none is renamed except the single
  authorised rename of the skip-reason-distinctness case from seven reasons to eight; each of the
  three suites passes with a case count no lower than its `d1ffd7f` baseline — 114 for
  `test-factory-claim.py`, 106 for `test-factory-integration.py`, 40 for `test-layout-migration.py`
  (each counted as `ok` lines, re-derived at `d1ffd7f`). These are baselines, not targets: they are
  the floor below which a case was deleted, and the new cases this feature adds are graded by
  SC-01…SC-06, not here.
  verify: automated      evidence: unit
- SC-08: Graded over **what the branch actually changed, not what the plan declared**. The grading
  set is the tracked-file list from `git diff --name-only d1ffd7f...<feature branch head>` — a
  three-dot diff against the base commit `d1ffd7f`, so untracked files (the in-flight
  `FEAT-26-pr-linkage-recorded/` and `FEAT-27-expertise-repository-tier/` directories) are outside
  the comparison by construction and cannot fail it — **minus** the one exclusion R-6 warrants: any
  path under `.harness/harness/features/FEAT-25-claim-feature-root/`, which is this feature's own
  bookkeeping (`STATE.md`, `feature.json`, `plan.yaml`, run directories, notes, observation logs).
  **Both clauses below grade that same remaining set** — the three-dot diff minus the feature
  directory — never the full diff, so prose in this feature's own notes and receipts that names a
  forbidden file or the `load_board` symbol cannot fail either clause. All five forbidden files sit
  outside the feature directory and so stay detectable. Two clauses, graded by reading the path list:
  (a) every remaining path appears in the union of the `files:` lists of T-01, T-02 and T-03 — a
  path that does not, including one inside `.claude/skills/harness/bin/`, fails this
  clause, because a file the plan never declared is exactly what it exists to detect;
  (b) each of the six members of the canonical forbidden set in `## Constraints` is checked
  **individually and named in the finding** — `factory_config.py`, `.harness/factory/fleet.yaml`,
  `.harness/harness.json`, `gh_board.py` and `check-domain.sh` each absent from the diffed path
  list, and `load_board` absent from every added line of the diff. Six separate verdicts, never one
  file-global search, which the conforming five would satisfy alone.
  verify: inspection

## Verification gaps

- None on the surfaces this feature touches. `unit` and `integration` are both `active` in
  `.harness/harness.json` with non-null `cmd`, and both `detect` globs match
  `.claude/skills/harness/bin/test-*.py`, which is where every file this feature tests lives
  (checked at `ada8e99`). The `functional`, `component`, `ui` and `eval` kinds are irrelevant here
  and no criterion rests on one.

## Constraints

- **The forbidden set — canonical, stated once here and referenced everywhere else.** Five files:
  `factory_config.py`, `.harness/factory/fleet.yaml`, `.harness/harness.json`, `gh_board.py`,
  `check-domain.sh`. Plus one symbol: `load_board`, which no call site this feature adds may
  reference. SC-08 grades against this list and adds nothing to it.
- No new `factory_config.py` API. `factory_config.py` is FEAT-24's T-02 surface, and general
  per-repository resolution is unit 7's (#495). The fix consumes an existing function or a literal.
- `factory_claim.py` is not a DEC-174 carve-out script; every task dispatches normally.
- Stream discipline is absolute: stderr for every diagnostic, one JSON payload on stdout
  (`factory_claim.py:12-14`).
- Merge collision, now resolved: FEAT-24 listed
  `.claude/skills/harness/bin/test-factory-claim.py` as a T-03 surface and added one case to it, and
  also edited `test-factory-integration.py`. FEAT-24 **merged at `d1ffd7f`**, so no sequencing is
  left to do — and its added case is why the claim-suite baseline is 114 rather than the 113 counted
  at `ada8e99`. Any later movement on `main` re-opens this: re-derive all three baselines before
  trusting SC-07 or the plan's count clauses.

## Approval
status: approved
approved_by: operator (Mike Ruangutai), via main session
date: 2026-08-19
