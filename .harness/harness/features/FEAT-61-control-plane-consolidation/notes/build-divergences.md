# FEAT-61 build record — enumerated divergences and rulings (D-06)

Built main-session-direct under DEC-174 (D-10) on `feat/FEAT-61-control-plane-consolidation`.
Commits: `2967b204` T-01 primitives; `40294807` T-02/03/04/05; `97d344d9` index cap. Panel
findings PF-994f9d45 and PF-2bab6a44 were applied in-run (T-02 verify names
`test-gh-sync-open.py`; T-05 carries the byte receipt) and are recorded `resolved`.

Correctness bar is D-06: byte-identity over the offline fixture corpus EXCEPT the divergences
below, each ruled and carried by a red-first test. Everything not listed here was measured
byte-identical (T-02: 21 plan-merge receipts; T-03: 29 of 41 gate receipts; T-05: 20 lifecycle
receipts in `tests/integration/fixtures/feat61-check-plan-routes-lifecycle.receipt.json`).

## Station predicates (D-03, D-11)

| # | Divergence | Ruling | Red-first test |
|---|---|---|---|
| 1 | `rejected` now completes review (`plan-merge._review_complete` = all `is_finished`) | D-11 | `test-plan-merge.py::case_bug1699_approval_reset_classifies_active_station` |
| 2 | abandoned+rejected alone resume `ready`, not `building` (`_work_started` stays the historical trio) | D-11 | same case, guard at :3363 |
| 3 | explicit empty/unknown task status in plan-merge RAISES FleetError (exit 1, plan untouched) where it was silently classified | D-03 | `test-plan-merge.py::case_feat61_approval_reset_refuses_an_unknown_task_station` |
| 4 | `gh-sync status review` with an out-of-vocabulary task status refuses "unknown station" (exit 2) instead of "not every task is done" | D-03 | `test-gh-sync-record.py` :356-377 |
| 5 | `gh-sync start-task` illegal top-level station: still exit 2 / one line, line now carries the repr'd value | D-03 | `test-gh-sync-start-task.py` (h) |
| 6 | `worktree_terminal` landed station outside the vocabulary → `unresolved` (was silently omitted, i.e. never reclaimed). One-time check: every landed station on origin/main is done/review/abandoned | D-03 | `test-worktree-terminal.py` :125-132, :173-181 |
| 7 | `check-plan-routes._is_shipped` keeps membership over `FINISHED_STATIONS` (never raises; unknown token = checked) — the view, not the predicate, because the function's documented contract is never-raise | T-05 comment at `finished_stations` | lifecycle receipt (byte-identical incl. `Done`) |

## Module loading (T-03)

| # | Divergence | Ruling | Red-first test |
|---|---|---|---|
| 8 | INV-40's observer no longer sees a stale `check_skill_weight` registration after a failed exec | intended (plan) | `test-check-state-feat59.py` 61.b |
| 9 | null module spec: INV-42 CANNOT RUN as `ImportError: cannot load ... no module spec or loader` (was `AttributeError: 'NoneType' ... 'loader'`) | `load_repo_module` contract | 61.c |

## Run-step schema (T-01/T-03)

| # | Divergence | Ruling | Red-first test |
|---|---|---|---|
| 10 | duplicate key / NaN in `run-state-schema.json`: both gates now "CANNOT be checked: ArtifactAccessError ... invalid JSON" instead of silent last-wins acceptance | strict reader | 61.e; `test-check-domain.py::_run_schema_contract_cases` |
| 11 | missing schema file / top-level non-mapping: `ArtifactAccessError` text (was bare `FileNotFoundError` / `TypeError`) at the same absorbing boundary | strict reader (`_load_json_bytes`) | same |
| 12 | `items` that is a non-mapping (e.g. `[]`): navigation's `TypeError: list indices must be integers...` instead of jsonschema's `AttributeError: 'list' object has no attribute 'get'` — the accessor finishes navigation before the caller builds the validator. **Ruled by the operator at validate c1 (VAL-03, 2026-09-20): accepted as an allowed divergence** — the gate still refuses on the same channel with the same verdict; restoring the old text would re-duplicate the navigation or fabricate a message. Build-time note: both are natural exceptions through the same absorbing `except Exception` and the plan's "natural errors at existing catch boundaries" covers the accessor's navigation. Mapping-shaped malformed schemas (`KeyError: 'steps'`, `KeyError: 'properties'`) are byte-identical and pinned | main session | 61.f, 61.g |

## Gate policy (D-04)

| # | Divergence | Ruling | Red-first test |
|---|---|---|---|
| 13 | `load_policy` returns `{"review": ...}` only | D-04 | `test-gate-policy.py` "loader resolves review by name from a review-only fixture" |
| 14 | review-only config loads (was `invalid gate policy for qa_gate: None`) | D-04 | same; `test-validate-digest.py::check_review_policy` |
| 15 | removed keys present with any value are ignored | D-04 | "loader ignores removed gate keys whatever their values" |

`GatePolicyError` wording preserved verbatim: `invalid gate policy for {gate}: {value!r}`.

## Grader

Diff grade: 84/84 changed functions PASS, no reason owed. Whole-tree: 1359 functions
(+17, all grade 4–5); below-bar counts unchanged (30/57/49) — pre-existing debt is not this
wave's ratchet (`harness-code-risk-grading`).

## Lock

`check-plan-routes.py --consolidation-audit` → `0 consolidation finding(s) under bin/`. On the
pre-migration tree it reported 14 (the exact sites the review found); each mutant in
`case_feat61_consolidation_locks` adds exactly its own finding.
