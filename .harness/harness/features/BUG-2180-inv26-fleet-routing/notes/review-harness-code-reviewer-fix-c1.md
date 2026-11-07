# BUG-2180 fix-c1 — PASS

**R1 resolved; R2 resolved by source inspection and recorded fail-first evidence. No new findings.** Code-grade passes at the exact pin; independent runtime confirmation belongs to QA. No source/tests authored, tests/build/lint/format executed, or goalcheck performed.

## Stage 1 — spec compliance

Reviewed `4a05030d401593003209f525fd06e00802eccd36..909798ec572ffe6ec484e89fd36f0f58ef113c45`; remediation separately compared `556a23ffea8dafcf5110e80fe25a42ee2542ff2b..909798ec572ffe6ec484e89fd36f0f58ef113c45`. Merge-base matches the supplied base. Full commit census contains only BUG-2180 work; no `[harness:human]` commits. Status contained only untracked `.harness/notes/grilling-inv26-fleet-routing-2026-11-07.md`, no tracked modifications. Pin matches feature.json.

- SC-01: `board.py:632–670,695–705` resolves each binding and groups by repository/board; integration `:747–790` checks parent/task/source numbers, owner-off behavior and overlapping issue 41. Unique bound numbers cannot enter owner groups.
- SC-02: original owner controls `case_v`/`case_w` are unchanged; `board.py:432–444,709–754` retains eligibility and authentication/owner-declaration handling; comparison/projection helpers are unchanged. Mixed owner/bound control remains at integration `:774`.
- SC-03: `board.py:696–703` catches actual GhError and BoardError, attributes original error to every affected feature, and returns to the next group without fabricated empty-map comparison. Integration `:792–804` retains failure text, exit 1, no traceback and healthy-feature comparison.
- SC-04: `board.py:644–648,658–662` reports FleetError without fallback; integration `:807–819` requires broken-feature/error attribution, healthy comparison and exact owner numbers.
- All SCs specify automated integration, not `verify: inspection`; these pointers document source compliance, not substituted runtime evidence. T-01 literal verify remains exactly `python3 tests/integration/test-check-state-inv26.py`.
- Unit file addition implements the signed BRIEF's DEC-217 floor; amendment `notes/amendment-T-01-unit-floor-2026-11-07.md` and amended T-01 own it. Settled scope Q1 is resolved; no scope change requested. Other changed paths are feature lifecycle/evidence records, not unrelated runtime changes.
- PRODUCT `docs/` contains only PRINCIPLES.md and invalid-states-audit.html: assigned `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` remain absent. No contents invented; no unresolved bounded requirement question. Actual adopted DEC-217 and DEC-221 consulted in PRODUCT `.harness/harness/docs/DECISIONS.md:7044–7068,7234–7269`.

## Stage 2 — quality and prior findings

**R1 — resolved (T-01; prior substance/high).** Scenario extraction retains x.1–x.6 fixtures and all behavioral requirements. x.1 now checks the complete repository→number-set map rather than the first call's numbers; x.6 strengthens the complete read map. The six predicates still require real checker output/read routing, not fixture assertions. `case_x` now CC5/cognitive7/ABC9.5, grade4, versus prior CC48/cognitive38/ABC124.9, grade1. Untouched legacy `case_v` is correctly absent from the changed-function gate.

**R2 — resolved (T-01; prior substance/high).** New unit file invokes real public `board.inv_26(ctx)` with real projection/comparison and only I/O/resolver doubles. `:128–172` asserts exact repository/project/numbers, differing station outcomes for shared issue 41, bound checking with owner off, attributed GhError and healthy continuation, and failed-binding no-fallback. An owner-union regression breaks u.1/u.4, an owner-sync early return breaks u.2, and swallowing failed reads breaks u.3. Presence assertions accompany owner-clean/absence assertions; a no-op subject cannot satisfy required reads or concrete diagnostics. `:175–188` also binds offline/no-candidate skips to probe counts. Builder evidence `notes/evidence-fix-c1-unit-base.txt` records seven behavioral failures and exit1; `notes/evidence-fix-c1-unit-after.txt` records nine PASS and exit0. These are read evidence, not reviewer-executed tests; QA owns independent replay. Separate BoardError-only coverage remains the settled nonblocking qualification, not a new requirement.

Production identity is measured: board.py at pin and `554f219e` share blob `90d656896aecf02d524cc3359145644ef37b88ad`; their diff is empty (exit0). `git merge-base --is-ancestor 1e55b30c 909798ec572ffe6ec484e89fd36f0f58ef113c45` succeeds (exit0); included fix commit resolves to `1e55b30c70e0d1577bedec1d46f5c531d4de0fe9`. No new correctness, fail-open, exception-boundary or maintainability finding identified.

### Measured complexity

Command, from PRODUCT: `python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/code-grade.py --base 4a05030d401593003209f525fd06e00802eccd36 --head 909798ec572ffe6ec484e89fd36f0f58ef113c45`. **Exit0; PASSING:39; no high severity, grade2 or ungraded records.** Numbers below are `cyclomatic/cognitive/ABC → grade`; production bar4, test bar3. This is the pinned changed-function gate, not whole-file grading.

- Production: `_inv26_import` 3/2/11.0→4; `_inv26_binding` 4/3/7.1→5; `_inv26_groups` 4/5/11.0→4; `_inv26_group` 4/4/9.1→4; `_inv26_check` 7/4/10.5→4.
- Integration fixtures: `_fleet_root` 2/2/11.7→4; `_fleet_feature` 2/2/9.4→4; `_fleet_fake` 2/2/10.3→4; `_calls` 3/1/5.4→5; `_board` 1/0/1.0→5.
- Integration extraction: `_x_run` 3/0/6.2→5; `_x_has` 3/0/3.0→5; `_x_asked` 2/1/4.6→5; `_x_bound_only` 1/0/10.6→4; `_x1_bound_feature_reads_its_own_repository` 3/1/7.1→5; `_x2_misplaced_bound_card_is_reported` 2/1/6.2→5; `_x3_owner_sync_off_still_checks_bound` 3/1/13.3→4; `_x4_mixed_features_share_a_number` 4/1/16.0→4; `_x5_failed_read_is_cannot_verify` 4/1/13.7→4; `_x6_unresolvable_binding_never_falls_back` 4/1/14.4→4; `case_x` 5/7/9.5→4.
- Unit fixtures: `check` 2/4/3.6→4; `_Ctx.__init__` 3/0/7.8→5; `_Ctx.gh_ok`, `_Ctx.station`, `_Ctx.record` each 1/0/0.0→5; `_feature` 3/1/3.3→5; `_modules` 2/1/7.9→5; `_modules.board_stations_for` 5/3/7.3→4; `_modules.resolve_binding` 2/1/3.0→5; `_run` 2/4/15.3→4; `_has` 3/0/3.0→5.
- Unit cases: `case_bound_and_owner_read_separately` 2/1/10.4→4; `case_owner_sync_off_keeps_bound` 2/1/7.3→5; `case_failed_read_is_cannot_verify` 3/1/10.4→4; `case_unresolvable_binding` 1/0/7.9→5; `case_offline_records_nothing`, `case_nothing_in_flight_probes_nothing` each 3/1/7.1→5; `main` 2/1/8.1→4.

## Principles applied

- Model the Domain: repository/board-keyed groups encode isolation, rather than another synchronized routing flag (`board.py:651`).
- Delete First: obsolete owner-union/silent-read helpers are removed, not retained beside the replacement. Scenario helpers isolate coherent fixtures/assertions rather than adding production layers.

Open questions: none. Prior items open/regressed: none. New findings: none. Source/test files touched: none.
