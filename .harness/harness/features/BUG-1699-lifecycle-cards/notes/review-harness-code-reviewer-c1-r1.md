# Final code review — BUG-1699-lifecycle-cards — c1-r1

**PASS.** The complete fix delta `37d846da62bd2e1d88a5406956482398d17bdca5..d7310f865e03534c233085e5f0a768eb9eca4687` is compliant and preserves behavior. The exact-range grader has no gated record: production helpers are grade 4–5 and test helpers are grade 4–5. The signed T-01 command passes at the target SHA. The final commit is receipt-only.

## Stage 1 — spec compliance

- The only shipped-code changes implement CR-01/CR-02: `project` delegates active-phase selection and parent/source placement without changing the projection interface (`.claude/skills/harness/bin/gh_board.py:126-158`), and `_inv26_fixture` delegates fixture construction by concern while retaining its inputs and assembled board/plan/record/fake-gh behavior (`tests/integration/test-check-state-inv26.py:26-137`). These changes serve T-01 and SC-11/SC-15; no unrelated behavior or scope was added.
- SC-15 remains traceable: `project` is still the single projection policy used by the unchanged status, INV-26, and reconciliation callers; the fix delta changes only its internal decomposition and the INV-26 fixture decomposition.
- QA-03 is **resolved**. The corrected receipt records distinct live controlled-red executions for SC-08, SC-12, SC-13, and SC-14, including the named mutant, exact failing assertion/output, direct command, restoration, and fixed-tip counterpart (`notes/receipt-harness-backend-dev-fix-c1-r1.md`). The assertions bind the intended subjects at `tests/integration/test-gh-sync-ship.py:33-55,86-156` and `tests/integration/test-gh-sync-record.py:236-265`. The restored SHA-256 values at the reviewed head exactly match the receipt: `gh-sync.py` `1a3f6c…e62b3`, `gh_board.py` `93dace6…e4921`; their fixed-tip direct counterparts passed within the exact signed T-01 run.
- Commit `d7310f865e03534c233085e5f0a768eb9eca4687` changes only `notes/receipt-harness-backend-dev-fix-c1-r1.md`; `0e1fdc22..d7310f86` contains no shipped source or test delta.
- No scope creep, omission, or mismatch found. No `[harness:human]` commit occurs in the reviewed range.

## Stage 2 — code quality and behavior

- **CR-01 resolved.** Direct target grading reports `project`: cyclomatic **3**, cognitive **1**, ABC **9.4**, grade **4**, production bar **4**. Exact-range grading additionally reports `_active_lifecycle_station` grade 5 (1/2/3.7) and `_place_parent_and_sources` grade 4 (6/6/7.9). The miss path remains fail-closed with respect to parent/source placement: a non-active/non-derived station returns task-only projection rather than inventing a feature phase.
- **CR-02 resolved.** `_inv26_fixture`: cyclomatic **2**, cognitive **3**, ABC **9.8**, grade **4**, test bar **3**. Its replacement helpers all grade 4–5: `_inv26_write_config` 5, `_inv26_write_plan` 4, `_inv26_write_feature` 4, `_inv26_items` 4, `_inv26_gql_node` 5, `_inv26_byissue_entry` 5, `_inv26_responses` 4, `_inv26_write_fake` 5. All original fixture branches and response shapes remain assembled.
- Audit-range grading over `merge-base(origin/main,d7310f86)..d7310f86` reports `PASSING: 54`, no high finding, and one grade-2 reason-required test (`case_lifecycle_checkpoint_order_and_negative_controls`): its ABC-only score reflects one cohesive orchestration contract plus eight explicit mutation controls, not a new or worsened record in this fix delta.
- The signed T-01 command ran exactly and exited 0 at `d7310f865e03534c233085e5f0a768eb9eca4687`; the unit runner ended `all pass` and all six integration runners ended `ALL PASSED`. No regression, new fail-open/silent path, or unowned finding was found.

## Panel dispositions

| ID | Disposition | Evidence |
|---|---|---|
| QA-01 | resolved | Main repair remains outside this fix delta; signed T-01 and the target implementation are green. |
| QA-02 | resolved | Main's T-04 fixture repair is unchanged by this delta; no T-04 shipped-code change occurs here. |
| QA-03 | resolved | Four distinct controlled reds, restoration hashes, and fixed-tip greens verified as above. |
| QA-04 | resolved | Main's execution-bound no-network control is unchanged; this delta does not touch plan mutation/network behavior. |
| CR-01 | resolved | `project` grade 4 at production bar 4. |
| CR-02 | resolved | `_inv26_fixture` grade 4 at test bar 3; replacements grade 4–5. |

No new findings or open questions.