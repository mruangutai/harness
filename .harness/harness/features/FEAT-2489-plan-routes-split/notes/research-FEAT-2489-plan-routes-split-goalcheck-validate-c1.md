# Goal-check — FEAT-2489-plan-routes-split — validate c1 (r-20261124-8-validate-validator)

Pin `be0807b024f5da33adcd034859d62ab9ec59bd8f`, base `261fdf726428bd8325fbd3d4beccad23b67e83cc`. Every read below was a `git show <pin>:…` or a `git diff base pin`. I re-ran no suite.

**BLUF: PASS.** All three perspectives are discharged, SC-01 to SC-05 are met, and no decision disposition is graded: all four `decisions_affected` rows are `keep`, and DECISIONS.md is not in the diff. Of the signoff conditions, C1 to C5 are met. C6 is not_met: no record-panel ticket exists. C7 is partial. Both are outside this diff's gate under the ruling's own words, and both go to Main before close. The two disclosed builder choices are not fail-open.

## Perspectives

| Perspective | Verdict | SCs | Evidence |
|---|---|---|---|
| operator | pass | SC-02 (with SC-01, SC-05) | `notes/equivalence-final.txt` shows 9/9 PASS and `exit=0`. Its trees are bin `d542c641` and tests `3f8731cd`, which equal `rev-parse <pin>:.claude/skills/harness/bin` and `<pin>:tests`. The perturbed canonical run has `mapped=1`: the `_classification_document` blank-reason finding has its path span rewritten to `canonical_reader_audit.py` and is otherwise byte-identical. The summary goes 103→105, which is D=2. `--help` exits 2 on both sides, so the quirk is preserved. `git diff --quiet base pin -- .github` exits 0, so tests.yml is byte-identical. The disclosed gaps (line numbers, traceback frames, location order) are carried by SC-01's move (below), as signed. |
| code maintainer | pass | SC-01, SC-04, SC-05 | Under bin, the .py diff is A `canonical_reader_audit.py`, A `structure_audit.py`, M entry, M `plan_merge/check.py` (comment only); there is no `__init__.py`. The entry imports exactly `LEGAL_MAIN_SESSION_TOKEN, _run_canonical_reader_audit` and `_run_consolidation_audit` (`check-plan-routes.py` lines 44-45). Neither module imports or loads the entry. `structure_audit` imports only `_reader_source_paths` from `canonical_reader_audit`. Five test files import by `AUDIT_DIR` and carry provenance checks. The inventory delta is 2 rows re-pathed in place plus 2 `scanned_files` entries. |
| reader | pass | SC-03 | The default `CASES` unpacks `*CANONICAL_READER_CASES` (test file `CASES` tuple). `red-t01`, `red-t03` and `green-t01` meet the stated shape (below). `green-t04-suites.txt` shows the canonical cases PASS in the default run at the pin's trees. |

## Success criteria

- **SC-01: met (inspection).** I took the base entry from `READER_CALL_CATEGORIES` through `_run_consolidation_audit` and ran a SequenceMatcher on it against the pinned modules. The only non-equal ops are: the module header inserts (docstring and imports), one replaced line (the `T07_TERMINAL_REMEDIES` `_task_files` key, now `canonical_reader_audit.py::_task_files::load_plan#1`), and trailing-blank or section-comment boundary lines. Those comment lines open `structure_audit.py`, inside its insert range.
  - The entry's own non-equal ops are: the docstring paragraph, the moved `LEGAL_MAIN_SESSION_TOKEN` line, the dropped `ast`/`collections`/`json` imports, the comment and two import lines, the `COUPLED` comment, and the removed block (base lines 925-2636).
  - This is my measurement. The code-reviewer's file:symbol citation is the declared carrier.
- **SC-02: met (inspection, sampled receipt plus SC-01).** See the operator row. The map is derived from top-level names (`split-equivalence.py relocation_map`), never from the inventory. It has 164 lines, each same-NAME into one of the two modules.
- **SC-03: met (automated, integration).** In the receipts:
  - `red-t01`: `exit=1`, exactly two FAILs, `canonical_reader_live_inventory_names_no_plan` and `canonical_reader_audit_holds_without_a_feature_corpus`.
  - `red-t03`, test segment: `exit=1` with 9 FAILs, all `canonical_reader_*` (the T-03..T-07 postconditions, `T07_terminal_accepts_exact_live_state`, `audit_holds_on_bin_plus_named_plans`, `live_audit_is_zero`, `live_classification_consistent`). There is no named-plan-resolves FAIL.
  - `red-t03`, audit segment: `exit=2` with five CLASSIFICATION lines. One names the scanned-file manifest, two name `canonical_reader_audit.py::…` (the new module path), and two name `check-plan-routes.py::_classification_document` and `::_task_files` (the moved rows). There is nothing else.
  - `green-t01` is bound. `HEAD c794bffe` is an ancestor of the pin, and its `BLOB 224a0a00` equals `rev-parse c794bffe:tests/integration/test-check-plan-routes.py`. Neither module exists at `c794bffe`. The receipt shows `ALL PASS` and `exit=0`, with no FAIL, and includes both `named_plan_resolves[...]` rows plus the four contract checks.
  - The phrases "names no plan", "no feature plan" and "without a feature corpus" are absent from the pinned test file.
- **SC-04: met (inspection).** No test under `tests/` reaches any of the 164 moved names through a loader. I grepped all nine other files that mention check-plan-routes and found zero hits. The remaining `cpr()` and `spec_from_file_location` uses in `test-check-plan-routes.py` reach only route surface: `_is_shipped`, `_manifest_deviation`, `BUDGETED_FIELDS`, `MACHINE_LINES_PER_TASK`, `finished_stations` and `legal_task_statuses`.
  - The satellite diffs change only imports, loaders, provenance checks and docstrings.
  - `green-t04-suites.txt` shows `run_pool` `exit=0`, and the copied-bin smoke for both unit files shows `exit=0`, each with `PASS audit_modules_load_from_the_bin_under_test`.
- **SC-05: met (inspection).**
  - The JSON diff is exactly the two rows (`file`, `id`) plus the `scanned_files` inserts in sorted position.
  - `T07_RELOCATED_IMPLEMENTATIONS` is unchanged: its keys still name `check-plan-routes.py::process_plan_yaml`.
  - The only line change in `T07_TERMINAL_REMEDIES` is the re-key.
  - In `plan_merge/check.py`, the comment now reads `structure_audit._decisions_index`.

## Decision dispositions

There are none to grade. `decisions_affected` holds DEC-174 ×2, DEC-183 and DEC-179, all `keep`. `git diff base pin` does not touch `.harness/harness/docs/DECISIONS.md`.

## Signoff conditions (answers-2026-11-24-signoff.md)

- **C1: met.** `split-equivalence.py` `apply_map` rewrites only `match.start/end("path")` of R1–R6. There is no `re.sub`, no masking and no wildcard. An R7 locator in the split files is a FAIL reason (`unmodelled_locators`), and stderr is compared exactly (`run_reasons`).
- **C2: met.** The MAP comes from `relocation_map` (top-level names). `verify-T-04.txt` PASS asserts MAP equality with the live run. The checker blob `dc67649b` and the bin/tests trees are identical at `427d3a7e`, `7282afab` and the pin.
- **C3: met.** The `COUPLED` comment is present above `main`'s dispatch, naming `canonical_reader_audit._run_canonical_reader_audit` (entry line 932). tests.yml is unchanged.
- **C4: met.** Case 19b's copy list carries both modules (test file, case 19b copy tuple). `git diff 9a308303 pin -- BRIEF.md` is empty, so the disclosure is verbatim.
- **C5: met.** BRIEF.md is unchanged since the signature commit, so the class wording ships as signed.
- **C6: not_met; not this diff's gate.** There is no record-panel "readers merge-not-replace + reason 'none'" ticket. `gh issue list --search created:>=2026-11-24` shows #2490–#2524, none of them it. The nearest is #1433 (2026-09-07, an older panel-reader repair). feature.json and STATE.md record nothing. The owner is Main, not a plan task.
- **C7: partial; not this diff's gate.**
  - The exit-7 verify-or-drop item is logged for distill: `observations/harness-pm.md` has the 4th bullet, "apply now replaces changed fields … exits 7 CONFLICT … is stale".
  - The record-panel observation is **not** in the pm log at the pin.
  - Distill has not run. The repo-tier P-04/P-08 still assert exit 7.

## Disclosures judged

- **T-02, stderr compared exactly: correct.** SC-02 says the map rewrites "only the locator field of the stdout diagnostic formats" and compares "stderr and traceback frames … line for line". C1 forbids traceback rewriting. `mapped` counts stdout only, and that is consistent with the contract. The unmeasured stderr part of the fifth item is already a signed verification gap. No finding.
- **T-01, `_copy_named_plans` skip: not fail-open.** The skip happens only while building the fixture.
  - `_named_plan_problems` resolves the same `corpus_path(ROOT, plan)` independently, so an unresolvable or missing plan FAILs `canonical_reader_live_inventory_named_plan_resolves[id]`.
  - The audit over the temp root then cannot read the absent plan. `red-t01` shows this producing "plan cannot be read" findings, so `canonical_reader_audit_holds_on_bin_plus_named_plans` FAILs too.
  - An `OSError` from `copyfile` propagates uncaught, which is loud.
  - There is no path on which a missing plan turns a check green.

## Findings

None against any task.

## Advisory notes (no task: the record is not code, so none of these is a scope change)

- **A-1 (form, info, no task).** Issue #2519 (FEAT-2458 B-4, "canonical-reader-self-test has 2 failures and no runner invokes it") is the defect T-01 fixes. Failure scenario: it stays open after merge and invites a duplicate fix. Main should link or close it at ship.
- **A-2 (form, low, no task).** C6 is unfiled (see above). Failure scenario: the record-panel wholesale-replace drops another feature's goalcheck row unnoticed, as happened here (answers-2026-11-24-inv32.md).
- **A-3 (form, info, no task).** The `verify-final-T-0{1,2,3}.txt` and `verify-T-04.txt` receipts are single PASS lines with no commit binding. They bind only through the unchanged tree ids above.

## Open questions

- OQ-1 (non-blocking): Should Main file the C6 record-panel ticket and add the record-panel observation to the pm log (C7) before close?

## Principles applied

- harness-principles rule 7 (verification is the product): each verdict cites a pinned read, not a suite colour.
