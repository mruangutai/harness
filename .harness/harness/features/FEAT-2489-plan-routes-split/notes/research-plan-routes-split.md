# Research — FEAT-2489 plan-routes split (pm, 2026-11-24, measured at 261fdf72)

BLUF: the split is mechanically clean. The canonical section (C) and the structure section (S) reference the route section (R) only through stdlib modules, `artifact_accessors`, `feature_corpus` and `LEGAL_MAIN_SESSION_TOKEN`, and S reaches C only through `_reader_source_paths`. So the ruling's shape (two flat modules, token in C, S imports C, entry imports two runners plus the token) needs no other cross-module name. Two couplings the grilling did not name are handled in T-03: case 19b's copy list, and the CHECK_PLAN_ROUTES_BIN module directory.

## Measurements (all at 261fdf72, worktree `feat/FEAT-2489-plan-routes-split`)

- **Cross-section name use**, from an AST walk of `check-plan-routes.py` with sections split at `READER_CALL_CATEGORIES`, the FEAT-61 separator and `def main`:
  - C→R: `LEGAL_MAIN_SESSION_TOKEN`, `artifact_accessors`, `ast`, `feature_corpus`, `glob`, `json`, `os`.
  - S→C: `_reader_source_paths` only.
  - S→R: `ast`, `collections`, `os`, `re`.
  - main→C/S: `_run_canonical_reader_audit`, `_run_consolidation_audit`.
  - R uses nothing from C or S.
  - After the move the entry no longer uses `ast`, `collections` or `json`; it still uses `glob` and `re`.
- **Inventory rows on the entry:** 6. The two whose symbol moves are `check-plan-routes.py::_classification_document::json_file#1` and `check-plan-routes.py::_task_files::load_plan#1`. The other four (`_manifest_deviation` ×2, `process_plan_yaml::load_plan#1` with symbol `_load_plan_once`, `_load_plan_once::load_plan#1`) are route-side and stay. No row names a symbol in S.
- **Inventory order:** `scanned_files` is in os.walk order (each directory's files sorted by name, then its subdirectories), not globally sorted. Rows are not sorted, and the audit never checks their order.
- **Opt-in self-test:** `--canonical-reader-self-test` exits 1 in 6 s with the same two FAILs as facts §8. The second FAIL's text is `plan cannot be read: failed to parse YAML in <tmp>/.harness/harness/features/BUG-20261006-…/plan.yaml`.
- **Default test run:** `test-check-plan-routes.py` takes 23 s. Adding the canonical tuple puts it at about 29 s, which is tolerable in the default integration shard (the ruling Q4 asked pm to confirm this).
- **Named plans live in the owner root:** this worktree is sparse (FEAT-1559) and holds only its own feature directory, so a named plan is read through `feature_corpus.corpus_path`. T-01's resolution check and its plan copy therefore go through `corpus_path`, never `ROOT/<plan>`. Both named plans are tracked on `main`.
- **CLI equivalence prototype:**
  - Method: run `git archive $(git merge-base HEAD main)` into a temporary directory. Run the old entry for the route-style argv shapes with `HARNESS_PROJECT_DIR=<worktree>`, and for the two audit singletons with `HARNESS_PROJECT_DIR=<archive>` (old code on the old tree).
  - On the unsplit tree, all six argv shapes (no argument, both audits, `--help`, both flags together, a missing plan path) gave identical exit, stdout and stderr once the archive path was replaced by the worktree path. That took 12 s. T-02 turns this into `notes/split-equivalence.py`.
- **Timings:**

  | Run | Time |
  |---|---|
  | Route mode | 5 s |
  | Canonical audit | 1 s |
  | Consolidation audit | under 1 s |
  | run_pool over the five test files | 24 s |

## Couplings found beyond the grilling

1. **Case 19b**
   - What it does: `test-check-plan-routes.py` case 19b copies the entry plus `harness_boundary.py`, `run_identity.py`, `artifact_accessors.py` and `feature_corpus.py` into a bare fake bin.
   - The coupling: after the split the entry imports both modules at module scope. Without them beside the copy, 19b dies on ImportError (exit 1, not 2) for a reason unrelated to the root-resolution case being tested.
   - Handling: T-03 adds the two module names to that copy list. That is the BUG-285/FEAT-42 precedent written in the case's own comment.
   - Case 21 copies every bin file from SCRIPT's directory, so it needs nothing.
2. **CHECK_PLAN_ROUTES_BIN**
   - What it does: five test files honour this mutation-testing override. Their docstrings record an earlier defect: a case that read the repo copy while the override pointed at a mutant.
   - The coupling: after the split, an ordinary import resolves from the repo bin unless the override's directory comes first, so audit mutants would become unreachable through the documented knob.
   - Decision (cheap, reversible, so a digest note and not a D-NN): each re-pointed file puts the override's directory first on sys.path, imports the module from there, and asserts the module's file lies in that directory.
   - Relation to the ruling: this keeps "CHECK_PLAN_ROUTES_BIN stays for route/main surface" intact for cpr(), and extends the override to name the bin directory under test for the libraries.
3. **The tests.yml comment**
   - The comment above the Canonical-reader audit step says the regex is coupled to `_run_canonical_reader_audit`'s print "in check-plan-routes.py, which carries a comment pointing back here". The ruling freezes tests.yml.
   - Mitigation: keep the runner names `_run_canonical_reader_audit` and `_run_consolidation_audit` rather than making them public. The ruling left the names to pm. Also add a COUPLED pointer comment at the entry's audit dispatch, so the tests.yml sentence stays true of check-plan-routes.py.
   - Raised as a non-blocking open question.
4. **Comments left alone**
   - `harness_yaml.py`'s "the census (check-plan-routes.py) refuses a broad catch here" stays true, because the census is still reached through check-plan-routes.py --consolidation-audit.
   - The FEAT-71 comment in `_ownership_finding` says "the inventory names no plan of its own". That reads as the document level, which is still true. It is audit code, and moved code stays verbatim.
   - The one live symbol naming is `plan_merge/check.py`'s `check-plan-routes._decisions_index`. It is re-pointed in T-03 (ruling Q5).

## Intermediate-state gate table (P-07)

| After | test-check-plan-routes default | satellite 4 tests | CLI route / consolidation | CLI canonical (CI step) |
|---|---|---|---|---|
| T-01 | green; canonical cases now gate | green | unchanged | unchanged (0, 101 files) |
| T-02 | unchanged (notes only) | green | unchanged | unchanged |
| T-03 | red, FAILs only `canonical_reader_*` (stale inventory) | green (re-pointed) | identical to base | exit 2, findings name only the manifest, the moved rows or the new module path |
| T-04 | green | green | identical | exit 0, count base+2 |

## File overlap answered

`tests/integration/test-check-plan-routes.py` is in T-01 and T-03. This is deliberate: ruling Q4 requires the self-test fix to land and gate before the move, and the move must re-point the same file's imports. `depends_on` serialises them. T-01's green is bound to its own checkpoint by `notes/green-t01-default-run.txt`, and its verify is stage-aware: between T-03 and T-04 it accepts the required canonical red, and it demands the whole run green before T-03 and after T-04.

## Panel cycle 1 — how the reader wave was applied (pm, 2026-11-24)

- **Matched trees (code-reviewer high #2).** Probed at 261fdf72: a `git archive` of the base commit runs all six argv shapes with `HARNESS_PROJECT_DIR=<archive>` (route 5.7 s, 14 lines; canonical exit 0, 101 files; consolidation exit 0). The checker now compares OLD = base archive against NEW = base archive with only HEAD's `bin` and `tests` overlaid, so named plans and the owner corpus are identical on both sides; `projection_confined` keeps every other changed path inside this feature's directory, which also covers `tests.yml`.
- **Non-clean state (code-reviewer high #1).** Probed at 261fdf72: two probe files in an archive's bin (`zz_split_probe_a.py` with `json.load`/`json.loads` and two broad catches, `zz_split_probe_b.py` unparseable) make canonical exit 2 with four CLASSIFICATION lines and consolidation exit 1 with three CONSOLIDATION lines, no traceback. That exercises finding text, order and source-error output, so it is the perturbed state in T-02.
- **AST half dropped (fable med).** SC-01 and SC-05 are graded by reading the move-detected diff and the JSON diff; no automated AST, import-shape or inventory check is built. The BRIEF's Verification gaps say inspection carries the structural class.
- **Pre-move red dropped (fable low).** With only CLI comparisons left, a pre-move run of the checker is a green control, not a discrimination proof; the real red is T-03's stale inventory failing the canonical comparisons, recorded in `notes/red-t03-stale-inventory.txt`.
- **Copied-bin smoke (OQ-2).** Probed at 261fdf72: `feature_corpus`, `artifact_accessors` and `harness_yaml` import cleanly from a bin copied to a temp dir, and both unit audit files pass with `CHECK_PLAN_ROUTES_BIN` naming the copy. T-03 adds the transitive provenance assertion; T-04 records the smoke.
- **Commits.** The checker reads commits only (G-15), so T-03 and T-04 each commit `bin` and `tests`; receipts bind to `review_sha` by bin and tests tree ids, not by HEAD.

## Panel cycle 2 — how the two substance findings were applied (pm, 2026-11-24)

- **PF-24112618 (SC-02 satisfiability).** Producers that interpolate a row's `file` at 261fdf72: `_exemption_finding`, `_row_label` (so `_ownership_finding`, `_route_finding`), `_unmigrated_row_findings`, `_migration_row_findings`, the illegal-disposition branch; `_canonical_row_findings` and the T07 messages format the row `id`. SC-02 now states the class (fifth sanctioned item), not this list. Probed at 261fdf72: base archive plus both probes plus the `_classification_document::json_file#1` row's reason blanked (json.dumps indent=2 rewrite) gives canonical exit 2 with five CLASSIFICATION lines, the fifth `.claude/skills/harness/bin/check-plan-routes.py::_classification_document json_file remedy=none: exemption requires a reason. PLAN AMENDMENT REQUIRED`; consolidation unchanged at exit 1, three lines. T-02's checker derives a `MAP` of exactly the relocated identities (rows differing only in `file`/`id`, id = file + identical suffix, new file one of the two modules) and requires exact equality after applying it; the raw diff stays in the receipt.
- **PF-6efa88c8 (T-01 receipt binding).** T-01 now commits its test change before recording; the verify checks `git merge-base --is-ancestor <recorded HEAD> HEAD`, `git rev-parse <recorded HEAD>:tests/integration/test-check-plan-routes.py` equals the recorded BLOB, the recorded HEAD holds `_check_live_inventory_named_plans` and no `canonical_reader_audit.py`, and the receipt carries every named-plan contract PASS for the inventory at that commit. Probed: `git merge-base --is-ancestor deadbeef HEAD` exits 128 and `git rev-parse --verify --quiet 261fdf72:nope.py` exits 1, so a bogus commit or path reddens the verify; the base commit as recorded HEAD fails the content check.

## Panel cycle 3 — how the four open findings were applied (pm, 2026-11-24, read at 261fdf72)

- **PF-24112618 / PF-6159b235 (SC-02 class).** Stated by what a diagnostic prints (its locator), not by producer or rewritten field. Read at 261fdf72 in check-plan-routes.py: line-numbered locators `{relative}::{symbol}:{node.lineno}` in `_feature_station_literal_findings` and `_module_loader_findings` (both run over every census file under bin, so they can site moved code), and in the check-state-only FEAT-62 producers. Three facts beyond the dispatch's wording, each forced by the same invariant: (1) a locator is not always leading — `_row_lookup` prints `duplicate classification row {row_id}`, so the class says "first place the diagnostic names a site"; (2) unmoved sites in check-plan-routes.py also shift line number (SC-01 drops three imports and adds import, comment and docstring lines), so the class covers any site in check-plan-routes.py at base, not only moved code; (3) `_scan_reader_tree` and `consolidation_findings` emit in os.walk/census order and station literals in line order, so a relocated finding can change position (e.g. `check-domain.py` sorts between `canonical_reader_audit.py` and `check-plan-routes.py`); the class admits only the position the producer's own location order gives the new location.
- **PF-b14b5b45 (T-02 comparator).** Map now derived from the move (top-level names in a module at HEAD that were top-level in the entry at BASE and are not at HEAD), never from the inventory, so the c3 counterexample (row removed from both inventories, candidate printed from `candidate['file']`) is covered. Applied to the leftmost `(?<!\S)path.py::symbol(:line)?` match only; probed the regex on the five shapes: the quoted illegal-exemption value is never matched, the duplicate-row id is. Line-number decision: FAIL (`unmodelled line-numbered locator`), never modelled or wildcarded; the measured perturbed outputs locate only probe files, so the sampled states print none.
- **PF-1dd0f7a1 (T-01 guard).** Both `canonical_reader_audit.py` and `structure_audit.py` must be absent at the recorded commit; ancestor and blob binding unchanged.
- **Resolved:** PF-6efa88c8, PF-5dbe6b5e and PF-4405ff64 (confirmed closed by class, notes/review-harness-code-reviewer-plan-c3.md), resolved_by T-01.
