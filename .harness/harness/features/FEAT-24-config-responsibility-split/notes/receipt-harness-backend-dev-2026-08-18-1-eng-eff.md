# EFFICIENCY angle — FEAT-24 plan surface — receipt

Read-only, flag-only pass over `plan.yaml` (decisions D-01–D-10, tasks T-01–T-10) and `BRIEF.md`
(SC-01–SC-13). Two findings, both measured, both applyable by pm without re-deriving the analysis.

## Finding 1 — T-02's per-process memo is unverified, and D-03's wording invites removing it

**file/line:** `plan.yaml:174` (D-03 choice: "no cached value") vs `plan.yaml:403-405` (T-02 item 6:
mandates a module-level memo keyed `(repo_name, ref)` "so that a tool calling board_for twice makes
one network call").

**cost, measured:** `factory_decompose.py` is the one call path that actually calls `board_for`
twice per process — once directly at :329, once indirectly at :399 through `board_station`, which
T-02 item 8 routes through `board_for`. `factory_claim.py:226` and `factory_land.py:85` each call it
once, so they're unaffected either way. I measured one `gh api` contents read at 0.577s wall
(`time gh api "repos/mruangutai/kaya-ai/contents/.harness/harness.json?ref=master" --jq .content`).
If the memo is missing or broken, every `factory_decompose.py` invocation pays that cost twice
(~0.58s extra) — and nothing catches the regression, because T-02's enumerated test list (17 cases,
`plan.yaml:433-450`) and the current `test-factory-config.py` (grepped, no `memo|cache|call_count`
hit) contain no case asserting a second `board_for`/`board_station` call reuses the first fetch. D-03's
own prose — "no cached value" — reads as forbidding exactly the memo T-02 specifies, so an executor
following the decision text alone could legitimately drop it, and no test would catch that either.

**fix:** two small additions, both to T-02 (pm's draft, not mine to touch):
1. One more enumerated case + `has()` clause: monkeypatch `factory_gh.file_at_ref` with a call
   counter, call `board_for` then `board_station` (or `board_for` twice) against the same fixture,
   assert the counter is 1. Ok-line suggestion: `board_for memoizes — a second call in the same
   process makes no second remote read`.
2. One clarifying clause appended to D-03: "no cached value" means no on-disk cache and no stale
   fallback on a failed read — not the per-process memo T-02 specifies, which is a different thing
   and stays.

**rank:** would-cost-a-build-cycle. The ambiguity is real (two decision texts point opposite ways)
and the miss is silent — nothing reddens if the memo regresses or is never implemented.

## Finding 2 — T-04's verify runs `test-gh-sync.py` and `test-board-station.py` twice each

**file/line:** `plan.yaml:562-573`. The loop at :562-567 runs both suites once each and checks for
pass/fail markers; then :568 re-invokes `test-board-station.py` and :571 re-invokes
`test-gh-sync.py`, purely to capture `$out` for two later `has()` string checks each.

**cost, measured:** `time python3 .claude/skills/harness/bin/test-gh-sync.py` → 8.205s wall;
`test-board-station.py` → 1.264s wall (both rc=0, no `FAIL` lines, run just now). The duplicate
invocations add ~9.5s to every run of T-04's verify — not a fraction of a second, and this verify
runs repeatedly during the cutover's dev/review/re-review cycle (T-04 depends on T-02 and T-06 and is
itself depended on by T-05, so it's a natural point of iteration). This is the plan surface's own
named example of waste ("a step that re-runs a whole suite where a targeted case binds equally") —
not a deliberate boundary run; nothing here is asserting a cutover boundary the way T-03's
intentionally-green-at-HEAD run does.

**fix:** capture each suite's output once inside the existing loop (`o` is already computed at
:563) into two named variables, e.g. `out_ghsync` / `out_boardstation`, and feed the later `has()`
checks from those instead of re-invoking. No behavioural change — same assertions, same ordering.

**rank:** cosmetic. ~9.5s per run is real but well under a build-cycle; still worth a one-line
variable-capture fix since it's free to apply.

## Checked and NOT flagged (dispatch asked explicitly)

- **check-state.sh / bash-write-guard.sh (session-entry and every-write paths):** grepped both for
  `product_config|board_for|file_at_ref|load_board` — zero hits. INV-26's `load_board(root)` at
  `check-state.sh:1131` reads the LOCAL project's `.harness/harness.json` off disk, not a fleet
  member's remote config, so T-04/T-05 add no network round-trip to the session-entry gate.
  `resolve_fleet` (`harness_boundary.py:128`, used by the write guard through `check-domain.sh`)
  reads `fleet.yaml` directly and never calls `board_for`/`product_config`, confirming T-07's own
  claim that the guard "reads name and workspace_root only."
- **T-03's own double-run** of `test-factory-land.py` (loop at :477-482, re-run at :483): measured
  0.073s wall total — a fraction of a second, not worth a finding per the dispatch's own "measure
  before flagging" instruction.
- **T-03's five-suite run, T-05/T-07's "run the full suite by hand":** these are the dispatch's own
  named exception — deliberate boundary/cutover evidence, not waste. Not flagged.
- **`gen-decisions-index.py --check`** (T-10 intent, `plan.yaml:1148`): already logged as a must_fix
  per the dispatch; not re-derived here.

## Ranked summary

| # | Finding | Rank |
|---|---|---|
| 1 | T-02 memo unverified + contradicted by D-03 wording | would-cost-a-build-cycle |
| 2 | T-04 verify re-runs two suites (~9.5s) it already captured | cosmetic |
