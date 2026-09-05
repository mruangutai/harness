# Eng findings applied to the BUG-1290 plan draft — fix cycle 1 (2026-09-05)

**All nine findings from run `2026-09-05-02-eng` are disposed; all six gating findings are applied.**
The plan's shape changed in one load-bearing way: D-01 no longer leaves the resolver's home free, and
the thing both callers share is now `segment_of`, **not** a features-root function. That deviates
from the operator's settled grilling wording and is named inside D-01's own text so it is signed
knowingly, not discovered in the diff. `approval.status` stays `pending`; no `panel:` key was written.

## Disposition

| id | gating | disposition | where |
|---|---|---|---|
| AR-01 | yes | applied-differently | D-01 (choice+because), REQ-05, SC-06, T-01 step 1, T-03 steps 1-2. Split into `segment_of` (3 callers) + `features_root` (1 caller), both in `factory_config.py`. Differs from the digest only in also making `workspace_path` call `segment_of` in T-03 step 1 — otherwise the third derivation survives and SC-06 fails at goal-check. |
| SF-01 | yes | applied | D-01, D-03, REQ-05, SC-06, T-01 step 5f, T-03 step 1. Home pinned to `factory_config.py`; the SC-06 scan now reads three files and requires exactly one derivation in `factory_config.py`. |
| AR-02 | yes | applied | D-01 because (3), D-04 because, T-04 step 2. Disarmed structurally: `factory_config.py` holds neither a `READER_TABLE` row nor a `STUB` entry (verified), so the retarget creates no duplicate key. T-04 step 2 states this and forbids the `harness_boundary.py` target explicitly. |
| AR-03 | no (advisory) | applied-differently | D-04 choice+because. Citation corrected — FEAT-42 (`layout_migration.py:98-104`) is a **removal** because no file carried the string afterwards. Shape chosen is **(b) the move**, not (a) removal: here a successor file does carry it, so moving keeps the module that now owns the rule under coupled-reader scrutiny and preserves the surface's five rows. AR-02 is disarmed by the home pin, not by removal. |
| AR-04 | yes | applied | T-03 `verify:` (appended `python3 tests/integration/test-feature-worktree.py`, measured exit 0 in 6.4s at `eb9d044e`), REQ-07, D-03 because. |
| AR-05 | yes | applied | T-02 `verify:` — marker assertion taken verbatim. Verified the idiom: today it exits 1 with 0 `FAIL` lines, so it is discriminating. T-01's verify deliberately unchanged. |
| SF-02 | yes | applied | REQ-04, SC-04, T-01 step 1, T-03 step 2. Bare-`harness` clause dropped from the shared functions' stated contract (it returns early at `feature-worktree.py:67-69`); REQ-04/SC-04 now say explicitly they are about an **owner-qualified** name ending in `harness`, and that the two inputs are different. |
| SF-03 | no (advisory) | applied | T-03 step 4 recites `factory_claim.py:94-157` (verified: `issue_number` ends at `:157`). |
| SF-04 | no (advisory) | applied | T-01 step 2 narrowed to `:58-68` + comment `:54-57` + docstring `:14-16`, with a separate reword of `:7-8`; `:7-12`'s fixture-rig prose stays. The two module-scope tests are still **deleted**, and step 2 now forbids converting them into weaker assertions. T-04's inline `python3 -c` probe dropped; its verify comment names case 22 (`:421-429`). |

**Nothing rejected.**

## The deviation the operator must see (D-01)

> DEVIATION FROM THE SETTLED WORDING: the wording settled in grilling was ONE resolver function
> called by both `factory_claim.py` and `feature-worktree.py:resolve_repo`. Under this shape the
> function both callers share is `segment_of`, NOT a features-root function, and `features_root` is a
> thin single-caller wrapper. The module home is also no longer engineering's free choice: it is
> pinned to `factory_config.py`.

Reason, in one line: `resolve_repo` composes the segment with `workspace_path`'s `workspace_root`,
not with the harness root, so a single features-root function makes it recover the segment from a
path built for a different consumer.

## Judgement calls beyond the findings

- **T-03 step 1 also rewrites `workspace_path` to call `segment_of`.** Without it, SC-06's extended
  scan (which now requires *exactly one* derivation in `factory_config.py`) would find two.
- **T-04 gains `tests/integration/test-layout-migration.py`** to reword case 22's comment
  (`:422-425`), which names `factory_claim.py` as a features reader — false after the row moves. The
  comment only; no assertion changes, and case 22 remains T-04's verify.

## Anchors re-checked at `eb9d044e` — 23, 2 corrected

Verified by reading the file at HEAD (`eb9d044e`, working tree clean for all source):
`factory_config.py:34,37,382-387`; `feature-worktree.py:64-87,67-69,77,86`;
`factory_claim.py:26-29,46-50,94-157,107,127-129,341,343`;
`test-factory-claim.py:7-12,14-16,54-57,58-68,393-394,420,850-867`;
`test-factory-integration.py:26-30,74-81,487,881-883,925`;
`layout_migration.py:83-88,92-94,98-104`; `layout_fixtures.py:45-48,53-56,68-71`;
`test-layout-migration.py:421-429`; `test-no-distribution.py:371-372`;
`check-state.sh:2363-2367`.
Corrected: `factory_claim.py:94-146` -> `:94-157`; `test-factory-claim.py:7-16` -> `:14-16` plus a
separate `:7-8` reword.

## Gates run

- `plan-merge.py amend` x14, all APPLIED; `yaml.safe_load` reloads the file; every value's tail
  survives; `approval: {status: pending}`; no `panel:` key.
- `check-plan-routes.py <plan>` -> `0 violation(s)`, all four tasks granted to `harness-backend-dev`.
- T-02's new verify idiom executed as written: exit 1 today, 0 `FAIL` lines — discriminating.
- `tests/integration/test-feature-worktree.py` -> exit 0, 6.4s at `eb9d044e`.

## Open questions

- **Q1 (operator, blocking signature):** D-01's deviation above. Two functions, not one; home pinned.
- **Q2 (harness defect, non-blocking):** `check-domain.sh` resolves the fleet from the **main
  checkout's** `.claude/skills/harness/bin/factory_gh.py`, which currently imports a module
  (`gh_issue_types`) that exists nowhere in the tree — an unrelated in-flight edit. Every write by
  every agent, including writes to `/tmp`, was denied with `BLOCKED — the fleet declaration does not
  load` for the duration. A guard whose availability depends on another feature's uncommitted
  working tree fails closed across the whole factory.
