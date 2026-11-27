# BRIEF — FEAT-2581 feature_record package

## Problem

The code that reads and writes `feature.json` is spread across four flat `bin/` files and one
unused CLI: the 1,149-line `feature-record.py`, `feature_schema.py` (581), `feature_json_write.py`
(227), the feature.json loader inside `artifact_accessors.py`, and `feature-json-merge.py`, whose
`set-key review_sha` / `set-key max_total_cycles` bypass the commit check and `budget_decisions[]`
record that `pin-review` and `raise-cycles` enforce. `feature_json_write` and `artifact_accessors`
import each other, twelve functions sit below code grade 4, and `plan-merge.py` still re-exports
`signed_task_hash` only so check-state's INV-40 can load the entry by path — the one exception
DEC-259 names (#2569). A maintainer changing feature.json behaviour today has to find it in five
places, and nothing proves a move leaves the CLI's bytes alone.

## Done when — by perspective

**operator** — I keep calling `feature-record.py` at the same path with the same verbs and get the
same exit status, stdout, stderr and feature.json bytes as before, shown from clean baseline and
pin checkouts for every call the tests make and for every tracked feature.json; any difference
stays red until I rule on it. The gates that read feature.json keep passing their own tests, and
every output text that changes — a diagnostic or traceback naming a moved module — is shown to me
with its exact old and new bytes before I rule on it; none is exempted in advance.

**code maintainer** — Everything that reads or writes feature.json lives in one `feature_record/`
package behind the thin entry, laid out per DEC-259 and `bin/LAYOUT.md`, every function at code
grade 4 or better, with no flat feature.json module, no unused merge CLI, no re-export and no
compatibility shim left anywhere; the decision record says so without an exception.

## Success criteria

- SC-01 (code maintainer): Read at the pin with `git show <review_sha>:<path>`, the bin directory holds `feature_record/` with exactly `__init__.py` (empty), `read.py`, `write.py`, `schema.py`, `evidence.py`, `binding.py`, `runs.py`, `judgements.py`, `budget.py` and `spend.py`; `feature_schema.py`, `feature_json_write.py`, `feature-json-merge.py` and `tests/integration/test-feature-json-merge.py` are absent; `artifact_accessors.py` defines none of `load_feature_json`, `FeatureJsonError`, `_feature_json_source`, `_read_feature_json_text`, `_parse_feature_json_text`, `_positive_issue_number`, `_validate_recorded_*`; `feature-record.py` defines no `cmd_` function and imports every one it dispatches from the package; no Python file under `bin/` or `tests/` imports `feature_schema` or `feature_json_write` or calls `artifact_accessors.load_feature_json`/`FeatureJsonError`; `plan-merge.py` contains no `signed_task_hash`; `bin/LAYOUT.md` lists `feature-record.py` with `feature_record/`. The reviewer cites each file and symbol.
  verify: inspection
- SC-02 (code maintainer): A committed grade assertion run against both clean checkouts reports, at the pin, every function in `feature-record.py` and every `feature_record/*.py` at code grade 4 or better — naming the twelve baseline below-bar functions (`main`, `_close_refused_run.mutate`, `cmd_record_history.mutate`, `_run_end_digest`, `_record_run_end.mutate`, `spend_for`, `recovery_command_for`, `verify_evidence_ref`, `run_evidence_problems`, `mirror_provenance_problem`, `_runs_agent_problems`, `_problems_for_doc`) at their package owners and listing each new helper — and reports red at the baseline. The reviewer reads the generated receipt with `git show <review_sha>:<path>`, the receipt being committed after the implementation pin it names.
  verify: inspection
- SC-03 (operator): Every Python file under `tests/unit/` that exits 0 at baseline `e12381fde910eb05728004476a10d741d6918010` also exits 0 at the pin and prints the same `FAIL` lines as at the baseline — none, except `tests/unit/test-factory-claim-mutation.py`, whose deliberate mutation proofs print four at exit 0 (measured at e12381fd) — with only imports and copy/patch targets changed; qa cites the pin's unit run and the committed baseline-side receipt, which is the fail-first equivalent for this semantics-preserving move.
  verify: automated
  evidence: unit
- SC-04 (operator): Every Python file under `tests/integration/` that exits 0 at the baseline also exits 0 at the pin with no `FAIL` line (none prints one at the baseline, measured at e12381fd), excepting only the deleted `test-feature-json-merge.py`; this includes the INV-40 signed-text cases in `test-check-state-feat59.py` running with `signed_task_hash` imported from `plan_merge.approval` and no re-export in `plan-merge.py`. qa cites the pin's integration run and the committed baseline-side receipt.
  verify: automated
  evidence: integration
- SC-05 (operator): A committed driver records every `feature-record.py` process started while the unit and integration corpus and `tests/unit/omp-hooks.test.ts` run — from the checkout's bin, from a bin a test copied, or spawned by a hook — (argv, cwd, the process's real exit status, stdout bytes, stderr bytes, `--file` bytes before and after), aligned by test file and invocation ordinal, with at least one record per spawning class on each side, commits each side's raw records, and finds them identical between the clean baseline and pin checkouts after replacing only each checkout's root path; any difference is listed with its exact old and new bytes in `build-divergences.md` and stays red until `notes/divergence-rulings.json` carries the operator's ruling on that exact record. The receipt's divergence list is exactly the set of differences recomputed from the committed records. The reviewer reads the receipt and records with `git show <review_sha>:<path>`.
  verify: inspection
- SC-06 (operator): A committed replay runs every `feature.json` record tracked at the pin (except this feature's own) through a fixed `feature-record.py` verb sequence and through `validate-feature-json.py` on independent scratch copies, commits each side's raw step records, and finds exit status, stdout, stderr and resulting bytes identical between baseline and pin after root replacement only. The reviewer reads the receipt and records with `git show <review_sha>:<path>`.
  verify: inspection
- SC-07 (code maintainer): At the pin, `check-plan-routes.py --canonical-reader-audit` exits 0 with zero unresolved reader sites; in `tests/integration/canonical-reader-classification.json` every row formerly sourced from `feature-record.py`, `feature_schema.py` or `feature_json_write.py` names its `feature_record/` owner in `file` and `id`, the `feature-json-merge.py` row is gone, every `load_feature_json` remedy reads `feature_record.read.load_feature_json`, the four `artifact_accessors.py` rows are unchanged, and `scanned_files` equals the live tree. The reviewer reads the audit output recorded in the receipt (`git show <review_sha>:<path>`) and the JSON at the pin.
  verify: inspection
- SC-08 (operator): Read at the pin, each diagnostic that named `feature_schema`, `feature_schema.py` or `plan-merge.py` as the module that failed to import or crashed (check-domain, INV-23, INV-26, INV-37, INV-40) names the `feature_record/` module or `plan_merge/approval.py` actually loaded. The committed receipt captures, as raw bytes before any decoding, the whole stdout and stderr of every check-state and check-domain gate subprocess whose output the existing tests capture, plus the canonical-reader audit run at both the baseline and the pin, and compares each stream whole between baseline and pin; every differing stream — the D-02 inventory items (those literals, the `RepoModuleError` renderings in INV-7, the refusal-evidence check and `harness_config`, the reads column of the check-state `--list` output), relocated traceback frames, the audit's scanned Python file count, and any other byte — is written to `build-divergences.md` as a `divergence:` record with its exact old and new bytes and a readable rendering of what changed, both recomputed from the committed records; an inventory item no existing test reaches is recorded as an unreached `divergence:` record carrying its file, symbol and old and new source read from both refs, never given a new test. Each such record stays red until `notes/divergence-rulings.json` carries the operator's own ruling on it, so none is exempted in advance; `build-divergences.md` also lists every test expectation T-01 changed with its old and new bytes, as the baseline-to-pin diff of each changed test path. The reviewer cites each `file` and symbol and the receipt's `d02_item` lines, read with `git show <review_sha>:<path>`.
  verify: inspection
- SC-09 (code maintainer): Read at the pin with `git show <review_sha>:.harness/harness/docs/DECISIONS.md`, DEC-259 no longer names a `plan-merge.py` re-export exception, DEC-220 and DEC-150 name the `feature_record/` modules that now hold the binding predicate and the line budget, and `gen-decisions-index.py --stdout` equals the committed `DECISIONS-INDEX.md`. The reviewer cites the lines.
  verify: inspection
- SC-10 (operator): The committed receipt names, per side, the passing case identities of every Python test file that exits 0 at the baseline (except the deleted `test-feature-json-merge.py`) and of `tests/unit/omp-hooks.test.ts` — `ok`/`PASS` stdout lines in order, unittest test ids with their outcome, bun JUnit testcase names — and finds each file's ordered list identical between the clean baseline and pin checkouts after root replacement only, so a case dropped, renamed or skipped at the pin is a difference that stays red until `notes/divergence-rulings.json` carries the operator's ruling on that file's record. A file whose runner names no case or only a one-line summary is bounded instead by its bytes being unchanged between baseline and pin and its whole stdout being identical; the receipt lists each such file, and each baseline-failing file left out of the comparison — any beyond the measured `tests/integration/test-typescript-typecheck.py` is itself a record that stays red until ruled. The reviewer reads the receipt with `git show <review_sha>:<path>`.
  verify: inspection

## Verification gaps

- none for runners: `unit` and `integration` are active with commands. The baseline-versus-pin
  receipts (SC-02, SC-05, SC-06, SC-07, SC-08's measured bytes, SC-10) live under
  `notes/receipt-scripts/`, which no test kind's `detect` globs match, so they are graded by
  inspection of committed receipts, never as test evidence; DEC-259 rejects a lint, so the grade
  bar is not added to the suite.
- Case identity (SC-10) is not proven for a file whose runner names no case or only a one-line
  summary. Measured at e12381fd: `test-code-grade.py`, `test-code-grade-cli.py`,
  `test-suite-claim-preservation.py` print one summary line, `test-harness-config-fixtures.py`,
  `test-factory-claim-mutation.py` and `test-omp-hooks.py` print no `ok`/`PASS` line and use no
  unittest. These are carried instead by unchanged file bytes and identical whole stdout.
  `test-typescript-typecheck.py` exits 1 at the baseline (no `tsc` installed) and is listed,
  never compared.
- SC-08 measures only D-02 branches that an existing test drives through a captured gate
  subprocess. An item that no existing test reaches carries no measured bytes: the receipt records
  it as unreached, and the operator rules on its source text alone — the named symbol's source at
  the baseline and at the pin, read through `git show`.

## Constraints

- BLOCKS — DEC-174: every task is `main-session-direct`; the enforcement layer, its tests and the
  proof are executed directly, never through a team run (as FEAT-69/70).
- BLOCKS — DEC-259 and `bin/LAYOUT.md`: thin hyphenated entry at its unchanged path that parses
  and dispatches, underscore package with empty `__init__.py`, modules named by their reads, every
  caller migrated in the same change, no re-export or shim.
- BLOCKS — DEC-232: `files:` anchors are `path`, `path#symbol` or `{path, quote}`, never a line.
  SUPPLIES — DEC-182: package-glob ownership keeps one atomic task within the field limit.
- BLOCKS — DEC-205/DEC-188: DECISIONS.md states current truth; pointer rot in DEC-150, DEC-220 and
  DEC-259 is amended in place, and `DECISIONS-INDEX.md` is regenerated with `gen-decisions-index.py`.
- Module map (operator Q2 a): read (loader, `parse_doc`, `opt_int`), write
  (`schema_checked_transform`, `write_feature_json`), schema, evidence, binding, runs (run-start,
  run-end, close-run, history, stamp-tokens), judgements (judgement, overrule-amendment), budget
  (set-rework, propose-rework, raise-cycles, set-mission, pin-review), spend; `read.py` imports
  `strict_json_loads` from `artifact_accessors`, never the reverse. A function placed elsewhere
  carries its reason in `notes/research-feature-record-package.md`.
- Grade bar (Q4 a): the twelve listed functions and every new helper reach grade 4; behaviour of all
  of them is held by the SC-05/SC-06 ledgers, never by a narrowed test.
- Identity proof (Q3 a): a separate pin task reusing FEAT-70's receipt-script structure, including
  its operator-ruled `divergence-rulings.json`; no new proof framework; only checkout-root bytes are
  normalized, because fixture and replay scratch paths are one fixed path on both sides.
- `feature-json-merge.py`, its integration test, its classification row and its durations row are
  deleted; #2569 is folded in and the PR closes #2581 and #2569.
- Test files change only imports and copy/patch targets; `tests/integration/fixtures/
  prior-check-domain.fixture` is a frozen prior copy and is not edited.
- Disclosure for signature: byte identity is required of every output, the twelve regraded
  functions included. D-02 repoints the import-failure diagnostics; signing authorizes that
  source change only, never its output bytes (PL-01). Those diagnostics, the wrapped
  `RepoModuleError` renderings, relocated traceback frames, any other changed byte of a captured
  gate stream and the canonical-reader audit's scanned Python file count are inventoried, never
  exempted — each measured difference stays red until you rule on that record, which you do
  personally, with every measured divergence presented together at the ship review and none
  delegated (PL-05). Each arrives in `build-divergences.md` with its exact bytes and a readable
  rendering of what changed.
  The classification `remedy` of the 24 rows naming `artifact_accessors.load_feature_json`
  (23 caller rows and the moved loader's own row) changes with the loader, as do
  canonical_reader_audit's category, remedy and T07 keys and two test expectations (D-01). You
  accepted this at PL-03; it supersedes the grilling's rule that classification rows change only
  file and id.
  T-03's proof exceeds Settled Q3 (a)'s "reusing FEAT-70's receipt-script structure with no new
  proof framework": its committed raw-measurement store (`notes/measurements/{baseline,pin}.jsonl.gz`),
  its `recorder/sitecustomize.py` interception of every test process and its verify that
  recomputes the divergences from those records have no FEAT-70 counterpart (FEAT-70 committed
  scripts, summary receipts and divergences only, `git ls-tree a98451c5`). They are the price of
  PF-14c27514, measured evidence bound to the pin. You accepted this exceedance as disclosed
  (PL-10) and the gzip measurement files as proposed (PL-09); Q3 (a) is not amended. Since those
  answers, the cycle-4 rewrite adds one record per test file run to the same store (its exit,
  stdout, stderr and case list), so the receipt's case and failure lines are recomputed rather
  than trusted; the measurement files grow by that much beyond what PL-09 accepted.

## Out of scope

- Test-code layout, and harness-qa adopting the pattern — ruled a later feature in the FEAT-2557
  grilling (Q5).
- `feature_corpus.py` — it handles feature directories and worktree layout, not feature.json; only
  its import line migrates.
- The `check_state/feature_record.py` invariants — they belong to the checker's own families; only
  their module-load targets migrate.
- `artifact_accessors.py`'s non-feature.json loaders (harness.json, plan, fleet, manifest,
  frontmatter, OMP config, hook payloads, gh JSON).
- Other long `bin/` files (validate-digest, check-domain, gh-sync and others) — future splits under
  DEC-259.

## Approval

status: approved
approved-by: operator
date: 2026-11-27
