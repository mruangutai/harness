# Goal-check (validate c1) — FEAT-2581 feature_record package

review_sha `62da450182282b05b25a127528f9223ac90fc6c8`, baseline `e12381fde910eb05728004476a10d741d6918010`,
implementation pin named by the receipt `c91df7a5913a1c45b0c797bd10a3a0a91ed9c9c7`. Run 2026-11-27-01-validate-validator.

**BLUF: PASS.** Both perspectives are discharged; SC-01..SC-10 are all met; the three amend rows
(DEC-259, DEC-220, DEC-150) landed and D-01, D-02 and D-03 landed. Every one of the 631
`divergence:` lines in the generated receipt is `RULED` and has a ruling carrying `by`, `date` and
`reason`; the receipt has 0 `UNRULED` lines. There is no finding. One non-blocking
caveat: qa's validate DIGEST was not available to me (the run's `qa/` folder held only
`manifest-unit.json`). So SC-03 and SC-04 rest on the committed per-file suite records, which I
recomputed through the T-03 verify. I did not use a qa citation for them.

## What I executed vs. reasoned

Executed: I ran the three `verify: |` blocks, read verbatim from
`git show 62da4501:<feature>/plan.yaml`, under `env -u HARNESS_AGENT_TYPE` in the feature worktree.
HEAD there is 13ee3de8. `git diff --quiet 62da4501 HEAD -- .claude .harness/harness/docs` is clean,
and the T-03 verify asserts that no path outside the feature directory changed after the pin.
- T-01: exit 0, 42 s. `T-01 structure and smoke PASS`, test-feature-record.py `Ran 130 tests … OK`,
  test-validate-feature-json.py `ALL PASS`, audit `0 unresolved reader site(s) across 110 Python file(s)`.
- T-02: exit 0. `T-02 decisions PASS`. `gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md`
  was empty.
- T-03: exit 0, 5 s. `verifying at 62da4501… (review_sha)`, `T-03 receipts PASS at 62da4501…`, and
  the audit exited 0. This recomputes every receipt line, every divergence body, every
  test_change record, the gate, replay and audit records, and grade-assert red at the baseline and
  green at the pin, all from the committed `notes/measurements/*.jsonl.gz` and `git show`.

Read at the pin with `git show`: the generated receipt, divergence-rulings.json, the
build-divergences.md head, DECISIONS.md and its index diff, the classification JSON, the D-02
literals, ctx.py, LAYOUT.md, README.md and canonical_reader_audit.py.

Reasoned only, not executed: I did not re-run the full unit or integration corpus. SC-03 and SC-04
rest on the committed suite records. The suites were measured at c91df7a5, which the verify binds
to the review_sha.

## Perspectives

- **operator — pass.** SC-03, SC-04, SC-05, SC-06, SC-08 and SC-10 carry it:
  - Same verbs and paths with ruled divergences only: the receipt reports `cli_identity: PASS` and
    `replay_identity: PASS`.
  - Replay coverage: the receipt has no `replay#` divergence at all, and the verify asserts 9 steps
    for every tracked feature.json except FEAT-2581's own.
  - Gates keep their tests: the receipt has `unit_files`/`integration_files: PASS` and
    `baseline_failing:` names only test-typescript-typecheck.py.
  - Every changed byte was shown with old and new bytes and an account, then ruled: 631 records in
    build-divergences.md, ruled 631 by `Mike Ruangutai` on 2026-11-27 (groups A 21, B 481, C 129).
  - Nothing was exempted in advance: the 7 unreached D-02 items appear as `d02#N:unreached` records
    and are ruled.
- **code maintainer — pass.** SC-01, SC-02, SC-07 and SC-09 carry it:
  - One package behind a thin entry: `bin/feature_record/` holds exactly the 10 files, and
    `__init__.py` is 0 bytes.
  - Grade bar: 155 functions are graded and all reach grade 4 or better.
  - No flat module, merge CLI, re-export or shim remains: the T-01 verify's AST and grep scan of
    bin/ and tests/ is clean.
  - LAYOUT row: `LAYOUT.md:10`.
  - The decision record states this without an exception: DEC-259 at `DECISIONS.md:8788-8791`.

## SC grading

| SC | verdict | method | evidence (at 62da4501) |
|---|---|---|---|
| SC-01 | met | inspection | The T-01 verify executed exit 0 and asserts every clause. `git ls-tree` shows the 10 files, and `feature_record/__init__.py` is 0 bytes. `plan-merge.py` has no `signed_task_hash`; it is defined only in `plan_merge/approval.py#signed_task_hash`. LAYOUT.md:10 reads `feature-record.py` \| `feature_record/`. README.md:204 reads `feature_record.write`. |
| SC-02 | met | inspection | Receipt `grade_bar: PASS`. The provenance block shows all twelve functions at their package owners: `main` 1→5 in feature-record.py, `spend_for` 2→4 in spend.py, and the rest. It lists 47 new helpers, each grade 4 or better, and `below_bar:` names the twelve at the baseline (exit 1). The T-03 verify re-ran grade-assert from the committed bytes: exit 0 at the pin; at the baseline it exits 1 and names exactly the twelve. |
| SC-03 | met | automated | The committed `suite#tests/unit/*` records were recomputed by the T-03 verify (`ng` assertion, executed): every baseline-passing unit file exits 0 at the pin with identical FAIL lines. That covers the 4 deliberate factory-claim-mutation lines. receipt-main-session-T-01.md records the `run-unit-tests.py --kind unit` exit 0. Test edits are imports, patch targets and label renames. They are listed as `test_change` records, and their output effects are ruled in group A. qa validate DIGEST: not in hand. |
| SC-04 | met | automated | The same recomputation covers `suite#tests/integration/*`: test-feature-json-merge.py is excluded from both sides, and only test-typescript-typecheck.py fails at the baseline (`baseline_failing: … 1 1`). For INV-40 the observer is keyed on `plan_merge/approval.py`, and the T-01 verify executed it (`plan_merge/approval.py did not import (RuntimeError: feat2581 observer reached)`). `ctx.py:364` calls `load_repo_module("plan_merge.approval")`. |
| SC-05 | met | inspection | Receipt `cli_identity: PASS`. The verify asserts at least one cli record per class (checkout, copied, bun) on each side. Its recomputed divergence set equals the receipt's `divergence:` lines and build-divergences.md bodies, and every one is RULED with by, date and reason. The CLI-record divergences are ruled: test-feature-record.py 12, test-omp-hooks.py 14 and test-validate-digest.py 5 records. |
| SC-06 | met | inspection | Receipt `replay_identity: PASS`. No `replay#` record diverges. The verify asserts replay ids equal 9 steps × every tracked feature.json except FEAT-2581's own, on both sides. |
| SC-07 | met | inspection | The T-01 and T-03 audits executed: exit 0 with `0 unresolved … across 110 Python file(s)`. In the classification JSON at the pin: 9 `feature_record/` rows with matching ids; the feature-json-merge row is gone (185→184 rows); the only `load_feature_json` remedy is `feature_record.read.load_feature_json`; the 4 artifact_accessors.py rows equal the baseline's; `scanned_files` has length 110. `audit_scanned_files: 103 110` is ruled as `audit:stdout`. |
| SC-08 | met | inspection | The D-02 literals at the pin name the loaded module: check-domain.py:1831, :1853 and :1804 (`feature_record.schema`); feature_record.py:427 (INV-23, `feature_record/schema.py`); board.py:286 (INV-37, `%s` of `feature_record.binding`/`.schema`) and :386 (INV-26, `feature_record/binding.py`); ctx.py:370 (INV-40, `plan_merge/approval.py`). Receipt `d02_item:` lines: items 2, 7, 10 and 11 MEASURED; items 1, 3, 4, 5, 6, 8 and 9 UNREACHED with source-only records; `residual 576`; `gate_captures: 1538 1559`. Every record is ruled, and the verify recomputes every line and body. |
| SC-09 | met | inspection | DECISIONS.md:8788-8791: DEC-259 has no exception, and `with one exception` and `still re-exports` are absent from the section. :7325 and :7333: DEC-220 reads `feature_record.binding.resolve_binding` and `.effective_recorded_repo`, which both exist at binding.py:18 and :62. :3513: DEC-150 reads `feature_record/schema.py`, which holds `FEATURE_JSON_LINE_BUDGET = 300` at schema.py:256. The `gen-decisions-index.py --stdout` diff was empty (T-02 verify, executed). DEC-211:6932 keeps its past-tense `feature_schema.py`, as planned. |
| SC-10 | met | inspection | Receipt `case_identity: PASS`; 162 `case_set:` lines. Per-side counts are equal for every file, so no case was dropped. 11 are DIFFERENT (label renames such as `feature_schema.py`→`feature_record/schema.py`), each ruled as `cases#<file>`. The six summary-only or unnamed files named in the BRIEF are SAME, and the verify's `ch` assertion holds their bytes unchanged. The only listed baseline-failing file is test-typescript-typecheck.py. |

## Decision dispositions (amend/strike rows; keep rows not graded)

| DEC | verdict | evidence |
|---|---|---|
| DEC-259 amend (clause `with one exception\n  this rule now names as a finding:`, successor D-03) | met | `git show 62da4501:.harness/harness/docs/DECISIONS.md` lines 8788-8791 now read "…in this shape. FEAT-2581 (#2581) moved the `feature.json` domain into `feature_record/` and removed the last re-export, … (#2569)". The clause is gone. |
| DEC-220 amend (clause `treats non-null`, successor D-01) | met | same path, lines 7325 and 7333 name `feature_record.binding.*`; `feature_schema` is absent from the section. |
| DEC-150 amend (clause `300 lines since FEAT-14,`, successor D-01) | met | same path, line 3513 reads `300 lines since FEAT-14, \`feature_record/schema.py\``. |

Settled decisions, graded only on whether they landed:
- **D-01** landed: canonical_reader_audit.py:28, :60 and :77-78/:87 carry the
  `feature_record.read.load_feature_json` keys, and the classification remedies match.
- **D-02** landed: the literals are cited under SC-08.
- **D-03** landed: ctx.py:364 loads `plan_merge.approval` by name through `load_repo_module`, and
  plan-merge.py contains no `signed_task_hash`.

## Findings

None. Info only, no task binding: test-broad-catch-census.py, test-checker-structure-locks.py and
test-harness-yaml.py change file-name keys (receipt-main-session-T-01.md deviation 5). These are path
renames, a reading of "copy/patch targets". They are disclosed as `test_change` records with exact
diffs, and their output effects are ruled. I do not grade them as a breach of SC-03.

## Open

- Non-blocking: qa's validate DIGEST should still be cited against SC-03 and SC-04 when it lands.
