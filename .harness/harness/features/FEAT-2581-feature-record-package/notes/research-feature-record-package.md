# Research — FEAT-2581 feature_record/ package (plan-product c1)

**BLUF.** The settled split is feasible as one atomic main-session-direct task plus a DECISIONS task
and a separate pin task. Four settled premises need correcting at signature (below, §2); none
changes the destination. Every figure here was re-measured in the worktree at baseline
`e12381fde910eb05728004476a10d741d6918010`, feature dir untracked, unless marked otherwise.

## 1. Re-measured facts (worktree, e12381fd)

- Line counts unchanged from the grilling: feature-record.py 1149, feature_schema.py 581,
  feature_json_write.py 227, artifact_accessors.py 499, feature-json-merge.py 129 (`wc -l`).
- The 12 below-bar functions are exactly the grilling's list (`code_grade.grade_source`):
  feature-record.py main 1, _close_refused_run.mutate 1, cmd_record_history.mutate 2,
  _run_end_digest 2, _record_run_end.mutate 2, spend_for 2; feature_schema.py
  recovery_command_for 2, verify_evidence_ref 2, run_evidence_problems 2,
  mirror_provenance_problem 2, _runs_agent_problems 3, _problems_for_doc 3. No other function
  in the five files is below 4.
- Live canonical-reader audit: `check-plan-routes.py --canonical-reader-audit` exit 0,
  `0 unresolved reader site(s) across 103 Python file(s)`.
- Tracked feature.json files: 43 (`git ls-files '.harness/**/feature.json'`).
- `check-domain.py --resolve`: bin/** and tests/** grant backend-dev/dev-ops(/qa);
  DECISIONS.md, DECISIONS-INDEX.md and .harness/README.md grant documentor;
  `schemas/feature.json` answers NOBODY; feature notes answer orchestrator. Every task is
  main-session-direct regardless (DEC-174, operator constraint 8).

## 2. Settled premises that are false or incomplete at source (raised in open_questions)

1. **Classification counts.** The grilling's "rows by source" (5/13/3/9/3) are `grep -c` line
   counts, which also count `remedy` and `file` mentions. Counted by each row's `file` field:
   feature-record.py 2, feature_schema.py 6, feature_json_write.py 1, artifact_accessors.py 4,
   feature-json-merge.py 1.
2. **artifact_accessors rows (Not-yet-specified #1, settled here).** Its 4 rows are
   strict_json_loads, load_frontmatter, load_omp_config and load_harness_json. **None belongs to
   the moving loader**; all 4 stay. The moving loader's only row is the historical
   `feature_json_write.py::load_feature_json::json_string#1` (T-07 relocation identity).
3. **Remedy strings.** 24 rows carry (corrected 2026-11-27, re-counted at e12381fd: 23 rows not
   sourced from moving code plus the moved loader's own `feature_json_write.py` row; first written
   as "24 rows not sourced from moving code")
   `remedy: artifact_accessors.load_feature_json`; `canonical_reader_audit.py` matches a canonical
   row only when a call's resolved callee equals the remedy, and classifies a call as
   `load_feature_json` only via `READER_CALL_CATEGORIES` or an `artifact_accessors.` prefix. After
   the move those 24 remedies, `READER_CATEGORY_REMEDIES["load_feature_json"]`,
   `READER_CALL_CATEGORIES` (its dead `feature_json_write.load_feature_json` key) and the two T07
   dicts must name `feature_record.read.load_feature_json`. Row ids of callers do not change (the
   category is still `load_feature_json`). This exceeds "change only file and id" → D-01. The
   operator accepted the correction at PL-03 (2026-11-27); the moved loader's row changes file,
   id and remedy.
4. **Diagnostic text.** Several gate diagnostics name the module they failed to import:
   check-domain.py (`feature_schema is not importable ... Expected at
   .agents/skills/harness/bin/feature_schema.py`, `feature_schema CRASHED`), check_state board,
   feature_record and run_state (`INV-37/INV-26/INV-23 CANNOT RUN: feature_schema.py did not
   import`), and ctx.py INV-40 (`plan-merge.py did not import`). Byte identity would leave them
   naming a deleted file → D-02 (the only intended text delta outside the 12 graded functions).
   `test-check-state-feat59.py` asserts `"feature_schema" in config[0]`.

## 3. Not-yet-specified #2 — copy_executable_package delegate: **not needed**

No test copies feature-record.py into a temporary bin on its own: test-feature-record.py
copytrees the whole bin; test-validate-digest (`_mx_bin`) and test-check-state-records
(`_anchor_bin`) run the real bin; test-hooks-install discovers `BIN_PACKAGES` by listing
directories. Selective copies that will reach the package through a copied module do need it:
test-check-plan-routes.py's fake_bin module list (feature_corpus.py and canonical_reader_audit.py
will import feature_record) and its case_21 copy of every top-level file (copies files only).
Patch targets that name feature_schema.py move to the owning module: test-check-domain-grant
`_inject_schema_crash`, test-check-domain-post SC-07 mutant, test-check-state-feat59 `_isolated`,
test-merge-gate `_feat65_fire`, test-validate-feature-json mutant, test-harness-config-readers
`_module(...)`, test-feature-record private loads.

## 4. Function placement where the map is silent (reason = what it reads)

| function(s) | module | reason |
|---|---|---|
| `_read_doc`, `_runs` | read | read feature.json bytes / the parsed runs list; `spend_for` (spend) and the run verbs (runs) both need `_runs`, so it sits below both (c1 scope finding 5) |
| `SCHEMA_REFUSAL_CODE` | read | first raised by parse_doc; write imports it |
| `_apply`, `REFUSAL_CODE`, `_refuse`, `_exit_refused`, `FEATURE_JSON_TAIL` | write | the CLI's locked read-modify-write and the refusal protocol `_apply` converts to an exit |
| `JUDGEMENT_KINDS`, `now_iso`, `_judgement`, `_append_judgement`, `_judgements_of`, `_kind_count` | judgements | read/stamp judgements[]; lowest CLI module, so runs/budget/spend import it without a cycle |
| `_find_run`, `_cycle_count`, `_attributed_cycles`, `_open_runs`, `_handoff_seq`, `_owed_*`, `_reconcile_owed`, close-run family | runs | read runs[] and handoff notes |
| `MISSIONS`, `_require_decision_file`, `_commit_id`, `_budgets_for`, `DEFAULT_REWORK_ROUND_MINUTES`, `TASKS_PER_ROUND`, `propose_rework` | budget | read the decision file, git, harness.json budgets, plan task count |
| `VALIDATE_RUN`/`FIX_RUN`/`DISTILL_RUN`, `_parse_iso` … `_regate_rounds`, `spend_for` | spend | read run timestamps and regate stamps |
| `_int_at_least`, verb registrars, `main` | entry | argument parsing only |

Import DAG: read ← schema ← write ← judgements ← runs/budget/spend; binding ← schema
(`recovery_command_line` calls `mirror_provenance_problem`; binding imports no schema name);
evidence imports read/schema. Cross-module edges measured by an AST walk of the baseline sources
against the map (c1): the only edges outside the original statement were spend→runs (`_runs`, now
in read) and schema→binding. No cycle; the artifact_accessors → feature_json_write lazy import
disappears.

## 5. Source traps the intent pins

- `feature_schema.BIN_DIR`/`SCHEMA_PATH` derive from `__file__`; in `feature_record/schema.py`
  `SCHEMA_PATH` must still resolve to `.claude/skills/harness/schemas/feature.json`.
- `_close_run_stages` spawns `__file__` (the entry) and `_HERE/validate-digest.py`,
  `_HERE/plan-merge.py`; moved into runs.py they must still name the entry and bin paths.
- `plan_merge/approval.py` `_feature_record_module` loads feature-record.py by path as module
  `feature_record`, colliding with the package name; it migrates to the budget module import.
- Audit alias collector: `import feature_record.read` (no `as`) resolves calls to
  `feature_record.read.read.load_feature_json`; any `from feature_record import read` /
  `from feature_record.read import load_feature_json` / aliased import resolves correctly.
- `schemas/feature.json` `runs.agent` description names `feature_schema.py's
  _runs_agent_problems`; `.harness/README.md` names `feature_json_write`; LAYOUT.md's table lacks
  the pair; artifact_accessors docstrings name `feature_json_write.parse_doc`.

## 6. Identity-proof adaptation (FEAT-70 structure, receipts under notes/receipt-scripts)

FEAT-70 intercepted calls through `PLAN_MERGE_BIN`; feature-record callers name the real path, so
no env override exists. Adaptation: a recorder loaded through `PYTHONPATH` `sitecustomize` in each
disposable detached checkout records any process whose `argv[0]` is that checkout's
`bin/feature-record.py` (argv, cwd, exit, stdout, stderr, `--file` bytes before/after), freezes the
clock in the tool's modules, and makes test-process `tempfile` names deterministic. The checkout is
never edited. `omp-hooks.test.ts` spawns the entry from bun with random `mkdtempSync` names; the
driver must make those deterministic at creation (bun `--preload`), else they are listed in
build-divergences.md and stay red pending a ruling (open question).

## 7. decisions_affected row identities

DEC-259 amend (the exception clause), DEC-220 amend (two module pointers, one row on the
binding clause), DEC-150 amend (budget holder), keep: DEC-174, DEC-205, DEC-211 (past-tense
incident, still true). Out of scope, left untouched: `docs/invalid-states-audit.html` (dated audit
with line refs already stale), `tests/integration/fixtures/prior-check-domain.fixture` (frozen
prior copy).

## 8. Reader wave c1 — dispositions (apply step, 2026-11-27)

Applied through `plan-merge.py apply` (D-02, T-01 intent/verify, T-03 intent/verify; exit 0, no
`APPROVAL-RESET:` receipt, so no gh-sync call) and `set-key decisions_affected` (exit 0). BRIEF
operator perspective, SC-05, SC-08 and two Constraints bullets edited to match.

| reader · finding | disposition | what changed / why |
|---|---|---|
| scope · T-03 omits the copied-bin CLI call (high) | applied | Recorder acts on every process whose argv[0] basename is `feature-record.py`, wherever it lives; it wraps the real child (exit, stdout, stderr relayed byte for byte). Per-class record counts (checkout bin / copied bin / bun) with a zero-count FAIL. Tracebacks recorded raw; their frame deltas stay red until ruled. |
| scope · T-03 accepts PASS text unbound to the pin (high) | applied within FEAT-70's structure | Verify now: checks inputs unchanged from the pin through HEAD (the review_sha at review), not just through the receipt commit; checks `script_sha256` lines against committed scripts; re-runs `feat2581-grade-assert.py --ref` (green at the pin, red at the baseline with exactly the twelve `below_bar` lines); re-runs the audit; requires every `divergence:` record RULED and present in `divergence-rulings.json` (FEAT-70's own ruling file). |
| scope · INV-40 observer left on the old seam (high) | applied; premise partly overturned | Observer re-targeted to `plan_merge/approval.py`; T-01 verify proves the seam is live (a raising replacement yields `INV-40 CANNOT RUN … plan_merge/approval.py did not import (RuntimeError: feat2581 observer reached)`). **Measured at e12381fd:** the observer already runs at `Ctx.__init__` *before* INV-42 executes (`runner.py` builds `Ctx` once, then `run_table`); a probe in which check-skill-weight.py writes a marker printed `check-skill-weight executed before me: False`. So (61.b) never tested stale registration even at the baseline; the move does not cause it. Repairing it needs a new test seam, outside Settled's imports-and-targets rule → open question. |
| scope · D-02 exemption unauthorized and not exhaustive (high) | applied; carried to the operator | D-02 now authorizes source text only; the T-03 exemption is gone; every measured difference, D-02 included, is red until ruled. Inventory below. |
| scope · `spend_for` → `_runs` edge (med) | applied | `_runs` moves to read.py; import statement adds schema→binding, the second edge the AST walk found. |
| scope · T-01 verify is a smoke check (med, form) | fixed | Verify binds all 13 `set_defaults(func=…)` handlers to `feature_record.*` imports, sweeps bin and tests by AST for `from artifact_accessors import <moved>` and `artifact_accessors.<moved>`, adds the INV-40 seam probe, and prints that it is a smoke gate; the corpus is T-03's per-file receipt. Measured ~21 s for test-feature-record.py. |
| scope · decisions_affected omits governing rules (med, form) | fixed | `keep` rows for DEC-180, DEC-190, DEC-191, DEC-229, DEC-230 with verbatim one-line clauses (checked as substrings of each section). DEC-259 was already `amend`. |
| should-not-exist · drop the bun leg (med, proportionality, scope: task) | **kept** (lead constraint 2) | Settled Q3 (a) says "every feature-record.py CLI call in the test corpus"; `tests/unit/omp-hooks.test.ts` is under `tests/unit/` and matches the unit kind's detect glob `**/*.test.*`. Narrowing a settled ruling is the operator's call, so the leg stays, with its own zero-count FAIL; the reader's trim goes to the operator as a non-blocking question. |
| should-not-exist · second normalization token (low) | applied | Fixtures under one fixed `/tmp/feat2581-fixtures` and replay trees under `/tmp/feat2581-replay`, identical on both sides and cleared per execution; only checkout roots are replaced. |

### D-02 expected output inventory (baseline e12381fd; the build records exact bytes)

Direct literals D-02 repoints:
1. `check-domain.py` `_feature_json_schema_problems`, ImportError branch: `feature_schema is not importable` / `Expected at .agents/skills/harness/bin/feature_schema.py`.
2. Same function, crash branch: `feature_schema CRASHED while checking this file`.
3. `check-domain.py` line-budget fallback `_basis`: `whole file — feature_schema was not importable`. (Not named in the c0 draft.)
4. `check_state/feature_record.py` INV-23: `feature_schema.py did not import`.
5. `check_state/board.py` `_inv37_import` INV-37: `feature_schema.py did not import`. INV-37 reads `recovery_command_line` (schema) as well as binding names, so it loads two modules.
6. `check_state/board.py` INV-26: `feature_schema.py did not import`.
7. `check_state/ctx.py` `_load_hash_module` INV-40: `plan-merge.py did not import`.

Wrapped `RepoModuleError` renderings (unchanged source; `str(error)` embeds `cannot load 'feature_schema' from None: …`):
8. `check_state/feature_record.py` `inv_7`: `INV-7 CANNOT RUN for {feat}: {error}`.
9. `check_state/run_state.py` refusal-evidence check: `{feat} refusal evidence CANNOT be checked: {error}`.
10. `harness_config._jsonschema`: `harness.json cannot be validated: {error}`.

Also changing by themselves: the cause text inside 4–7 when the failure is a missing module
(`No module named …`), and traceback frame file/line coordinates for any uncaught exception that
passes through moved code (expected in the ledger: `test_an_unexpected_defect_stays_loud_and_nonzero`,
whose deliberate traceback runs through `cmd_propose_rework`).
11. `check_state/table.py` `_EVIDENCE_READER` (`path:.claude/skills/harness/bin/feature_schema.py`,
    read by INV-7 and three other rows) is repointed with the move, so `check-state.py --list`
    prints the new path in those rows' reads column (`runner.py` `_list_rows` prints `row.reads`),
    and `--changed` selects those rows when the new owner file changes (`runner.py` `_row_changed`
    matches `row.reads`). Measured since send-back 1 from the captured `--list` runs (§9, GC-02).

Recommendation to the operator: sign D-02 (repoint 1–7); rule 8–11, frame coordinates and each
unreached item per measured record in `divergence-rulings.json`, as FEAT-70's rulings did for
relocated frames.

## 9. Send-back 1 (apply, 2026-11-27) — goal-check gaps GC-01..GC-04

**BLUF:** T-03 now compares case identity per file and measures every D-02 inventory item into
ruled `divergence:` records. Seven findings are marked resolved and two stay open. The (61.b) gap
is carried as a non-blocking question. All writes went through `plan-merge.py`: `apply` T-03
(traces, verify, intent), `set-panel`, and `apply` D-02 choice. Each exited 0 and printed no
`APPROVAL-RESET:` receipt, so no gh-sync call was made.

Census (worktree at e12381fd, feature dir untracked, `xargs -P 8`, HARNESS_AGENT_TYPE unset, 162
Python test files excluding test-omp-hooks.py; raw outputs in /tmp/feat2581-census, not
committed): 161 exit 0. `tests/integration/test-typescript-typecheck.py` exits 1 because there is
no `node_modules/.bin/tsc`. By the marker rule (first token `ok`/`ok:`/`PASS`/`PASS:` on stdout),
131 files print marker lines, 26 are unittest only and 3 use both. Of the 131, three print only
one summary line: test-code-grade.py, test-code-grade-cli.py and test-suite-claim-preservation.py. Three name none:
test-harness-config-fixtures.py, test-factory-claim-mutation.py and test-omp-hooks.py (stdout
checked separately: 0 marker lines). Bun `--reporter=junit` names 247 testcases. Seven files
repeat a marker line, so identity is an ordered list, not a set. Only
test-factory-claim-mutation.py prints FAIL lines at exit 0 (4, its deliberate mutants).

| GC | what changed |
|---|---|
| GC-01 case identity (T-03) | New `Case identity` paragraph, FEAT-70's `b_cases == pre_existing` per file. Each file gets an ordered list: marker lines plus unittest `<outcome> <id>`, which the recorder writes by wrapping the `TestResult.add*` methods, and bun JUnit for omp-hooks.test.ts. One `case_set:` line per file, and `cases#<file>` records that stay red until ruled. **Files no runner names:** the six above, each with fewer than two entries. They are bounded by byte-identical file bytes between baseline and pin (verify asserts `git diff --quiet`) plus identical whole stdout. T-01 edits none of them (grep for moved-module names: none). The baseline FAIL rule is corrected from "no FAIL line" to "same FAIL lines as the baseline", which test-factory-claim-mutation.py needed. Verify now checks `case_set` coverage against `git ls-tree <baseline>` minus `baseline_failing`. BRIEF: SC-03/SC-04 FAIL wording, new SC-10 (operator, inspection), T-03 traces SC-10. |
| GC-02 D-02 measured (T-03, D-02) | The recorder also wraps `subprocess.Popen.communicate` in test processes and captures check-state.py/check-domain.py children; this is the same recorder, not a new framework. Items 1–11 each have a quoted marker, plus a residual class for any other captured line naming a moved module. Each item is `MEASURED` with `d02#` difference records, or `UNREACHED` with one `d02#<n>:unreached` record that carries its source template; no new test is added. `d02_inventory` is PASS only when every record is RULED, captures are non-zero on both sides, and every MEASURED item shows a difference. Static expectation (not gated): reached 2, 10 and 11; unreached 1 and 3–9, because the only feature_schema injection (`case_feat63_inv23_import_boundary`) fails harness.json validation first and the INV-40 observer never raises. D-02's choice is reworded to match. BRIEF SC-08 and the gaps section are updated, and SC-08 is reworded so it no longer names the gate scripts by filename (INV-41 false-matched it). |
| GC-03 panel | `set-panel`: resolved PF-ccd4 (T-03), PF-e7dd (T-03), PF-d91c (T-01, observer re-targeted), PF-aaf4 (T-01), PF-2782 (T-01), PF-dc97 (T-01: the keep rows govern T-01's surfaces; a `resolved_by` must name a task), PF-b3de (T-03). **Left open:** PF-d35d (bun leg, the operator's call) and PF-7999 (high). D-02 is now exhaustive by measurement, but its authorization exists only at the operator's signature and rulings, so `sign-approval` will require an `approval.rulings` entry for it. Severity, kind, summary and reader are unchanged. |
| GC-04 (61.b) | Carried as a non-blocking open question recommending a backlog item. The stale-registration check never ran, even at the baseline (§8), and this plan does not fix it. |

Verify probe: the new T-03 verify compiles and contains no `>`. Its case_set/d02 block was run
in-process against synthetic receipts. A good receipt passes. Each of these fails as intended: a
dropped case_set, a DIFFERENT case set with no record, an unnamed file with entries, a MEASURED
item with no record, a missing item, zero captures, and an unreached residual.

Observed, not fixed (outside the GCs): `test-omp-hooks.py` runs `bun test` without the preload
in the Python corpus. Its feature-record spawns may therefore carry random mkdtemp paths in the
CLI ledger, so expect ruled divergences there unless the operator drops the bun leg.

## 10. Reader wave c2 — apply (repanel-product, 2026-11-27)

Applied through `plan-merge.py apply`: D-02.choice, T-01.intent, T-03.intent and T-03.verify,
exit 0, with no `APPROVAL-RESET:` receipt, so gh-sync was not called. Then `record-panel
--cycle 2` (exit 0, five findings ADDED) and `set-panel` (exit 0), which reopened PF-e7dd0045
because the scope reader re-read it as not closed. BRIEF SC-02, SC-05 to SC-08 and SC-10 and the
Constraints disclosure were edited to match. **No reader has read any of this text.** Every new
finding stays `open`.

| finding | where | what changed |
|---|---|---|
| PF-e7dd0045 restated (PF-14c27514, high) | T-03 verify and intent; BRIEF SC-02, SC-05 to SC-08, SC-10 | The receipt now commits per-side raw records, `notes/measurements/{baseline,pin}.jsonl.gz`. The verify recomputes every cli, gate, replay and audit difference from those files and requires the receipt's divergence set to equal the recomputed set. It requires a non-zero record count per CLI class, and replay ids equal to tracked feature.json records × 9 steps, derived independently with `git ls-tree` at the pin. The six `script_sha256` paths must be the six named scripts. The grade-assert runs from committed bytes on stdin. Everything is read through `git show` at feature.json `review_sha` when pinned, else HEAD, with base → pin → receipt → ref → HEAD in ancestry and no change outside this feature's directory after the pin. |
| PF-7999938a restated (PF-c36ed89c, high) | T-03 intent and verify; D-02.choice; BRIEF SC-08 and the disclosure | Gate stdout and stderr are captured as raw bytes, before decoding. A calibration record (`gate#calibration#1`, fixed bytes with `\r\n`, `\r` and UTF-8) proves this on each side. Streams are compared whole; the module-substring residual is gone. Inventory items now classify `gate#` records through `d02_item_record` lines, and the residual is a count of the unnamed ones. The canonical-reader audit runs at both checkouts. `audit_scanned_files: <b> <p>` discloses the count, and `audit:stdout` is a red record. **The authorization half stays the operator's; the finding stays open.** |
| T-01 gate vs SC-03 (PF-c82fdafb, high) | T-01 intent, last paragraph | The pass condition is the baseline's own result. In the unit run, exit 0, every run_pool status line is PASS, and the only other FAIL lines are the four preserved mutation lines. In the integration run, only test-typescript-typecheck.py may fail, and only where tsc is absent, exactly as at the baseline. The paragraph separates this gate from T-03's graded clean-checkout comparison. |
| RG-A2 (PF-390fdc3e, med) | T-03 intent and verify; BRIEF SC-10 | A `baseline_failing` file other than test-typescript-typecheck.py needs a ruled `baseline#<file>` divergence. |
| PF-d91cba6c caveat | T-01 intent | Nothing claimed that the probe proves INV-42 cleanup. T-01 now says outright that the probe shows only that the INV-40 seam is live (form). It stays resolved. |
| should-not-exist (PF-502d3541, low) | T-03 intent, case-identity paragraph | Not trimmed. PF-d35d903d is reframed in the text: the operator decides only the CLI ledger's bun-spawned class (its zero-records gate) and `feat2581-bun-preload.js`. The junit run stays for SC-10 either way. Both findings stay open. |

T-03's verify is 31 lines (48 machine-field lines, under the 50 cap). It parses, and exits 1 on
the unbuilt tree at `receipt commit not found`. I lifted its comparison lines out into a
synthetic harness: it passes clean, and goes red under three mutants, each caught by the
`mv==D` set equality:

- an unruled audit difference;
- calibration bytes whose newlines were translated;
- a dropped bun record.

Not measured: the size of the committed measurement files.

## 11. Reader wave c3 — apply, first pass (repanel2-product, 2026-11-27)

Applied through the control-plane `plan-merge.py apply`, with a partial proposal carrying only
T-03. The receipt was `REPLACED T-03.verify` and `REPLACED T-03.intent`, `APPLIED`, exit 0, with
no `APPROVAL-RESET:` line, so gh-sync was not called. A second, accidental invocation received
an empty proposal because the builder script's anchor had already been consumed. It printed only
`APPLIED` with no REPLACED or ADDED line, exit 0: a no-op. T-01 is untouched.

The BRIEF gained one disclosure sentence (Constraints, the end of the disclosure paragraph). SC
wording is unchanged. SC-05, SC-06 and SC-08 already require the captured fields and the exact
old and new bytes; the gap was in the verify, not in the criterion.

No record-panel was run, and no PF id was resolved or reopened in this pass. `plan-merge.py check`
exits 0 with 0 failures. Worktree HEAD is e12381fd and the feature dir is untracked.

| finding | where | what changed |
|---|---|---|
| scope high, PF-14c27514 not closed (required stream keys) | T-03 verify, the `nz=` line; T-03 intent, the Measurement files paragraph | Each kind has an exact required stream-key set: cli has 7, gate 5, replay 6, audit 3. An empty capture is base64 of zero bytes. JSON null is legal only for cli `file_before`/`file_after`, when there is no `--file` or the file is absent. A failed capture writes no record, and cleanpin exits non-zero. Before the divergence set is recomputed, the verify refuses five cases: a wrong key set, a non-string value, a non-decimal `exit`, a bad or misplaced `class`, and a kind that differs across sides. `streams: {}` and stderr missing on both sides now fail. |
| scope med + design high (one remedy) | T-03 verify, the `mv=` line and the `assert all(len(ki(s,"audit"))` line; T-03 intent, the Audit and Compare paragraphs | `audit_scanned_files` must be the single line equal to the N pair parsed from each side's committed raw `audit:stdout`, and that line must appear exactly once per side. `build-divergences.md` measured entries are `divergence_entry:` … `end_divergence_entry` blocks. Each holds `old:`/`new:` Python bytes reprs after root replacement, or `side:` plus `stream <k>:` lines for unaligned records. The verify recomputes every body and requires the block map to equal it exactly. Unreached D-02 items use distinct `source_only_entry:` … `end_source_only_entry` blocks with file, symbol, old_source and new_source, exactly one per `d02#` record. |
| should-not-exist med (Q3 a exceedance) | BRIEF Constraints, the disclosure paragraph | One disclosure sentence. Settled Q3 (a) is not edited. Amending it is the operator's call and is carried as an open question. Q3 (a)'s wording is still restated in two places: BRIEF Constraints, Identity proof, and the opening sentence of T-03's intent. |
| should-not-exist low (two implementations) | T-03 intent, the end of the Compare paragraph | The paragraph is normative for both cleanpin.py and the verify, together with the stream-key set, the audit derivation and the entry format. A drift is a script bug, fixed and regenerated with `--reuse` from the same measurements. It is never a divergence, a ruling or a new pin. |

Probe, run by me: I lifted the four changed verify lines (`nz=`, the D loop, `mv=`, audit) into
a synthetic harness (`/tmp/feat2581-c3-probe.py`, not committed). A good receipt PASSes. Eleven
mutants each FAIL at the intended assertion: streams `{}` on both sides, stderr missing on both
sides, null stdout, empty exit, a kind that differs, a cli record with no class, an altered
payload, a missing entry, a dropped source-only entry, `audit_scanned_files: 0 0`, and a
duplicated audit line. The full T-03 verify still compiles and, on the unbuilt tree, exits 1 at
`receipt commit not found`.

## 12. Panel cycle 3 recorded (repanel2-product, 2026-11-27)

Record step only. No task, decision or BRIEF text changed; goal-check not re-run; no addendum.
Input: `runs/repanel2-product/panel-c3.md` (lead fan-in incl. second read).

**Step 1** — `plan-merge.py record-panel --file <FD>/plan.yaml --digest <FD>/runs/repanel2-product/panel-c3.md --cycle 3`, exit 0:

```text
Check-state --changed after <FD>/plan.yaml:
  VIOLATION  .harness/harness/features/FEAT-2581-feature-record-package/BRIEF.md is NOT approved — halt that flow and surface to the user.
  VIOLATION  INV-29: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2557-code-layout-pattern is a standing worktree whose feature FEAT-2557-code-layout-pattern reached a terminal state on the default branch. [... remove command elided; unrelated feature]
  VIOLATION  INV-37 FEAT-2581-feature-record-package: github.sync is enabled but the feature has no usable Build-entry receipt (receipt absent or incomplete) - run python3 .claude/skills/harness/bin/gh-sync.py open <FD>.
  note       .harness/harness/features/FEAT-2581-feature-record-package/plan.yaml approval is pending — awaiting the user.
  note       FEAT-2581-feature-record-package: run repanel2-product has unknown historical cycle attribution.
  note       FEATURE SET: 1 feature director(y/ies) on disk that HEAD does not track: harness/FEAT-2581-feature-record-package (not gating).
ADDED PF-0ab2a54115f601adc844b6ff906f5564
ADDED PF-74107187b30075ff469855f63e753993
ADDED PF-f8e3277e88a9a8d53e8fc85c312ba652
ADDED PF-b045e378e3a26989ec460a400717b923
ADDED PF-2ddbc1410bd086da4924c7a25bf1ab96
ADDED PF-96cdf9f10890ac070da480030c481192
ADDED PF-3882d444d53e5048aab5db3565f24435
ADDED PF-cf9cf710f71b769e92a542d62f352636
ADDED PF-a37e5b4054c542a0b7b80de309c1f9ca
PANEL cycle 3 from <FD>/runs/repanel2-product/panel-c3.md -> <FD>/plan.yaml
APPLIED <FD>/plan.yaml
```

The three VIOLATION lines are pre-existing state (BRIEF pending by design, an unrelated
FEAT-2557 worktree, no Build-entry receipt before signature), not produced by this write.

Cycle-3 PF ids assigned:

| PF id | reader / sev / kind | summary |
|---|---|---|
| PF-0ab2a541 | scope high substance | PF-14c27514 not closed: missing required measurement streams |
| PF-74107187 | scope med substance | audit-count disclosure disagrees with committed raw audit |
| PF-f8e3277e | design high substance | D-02 operator-facing disclosure not bound to measured output |
| PF-b045e378 | should-not-exist med proportionality | raw-measurement store + recorder + recompute exceed Settled Q3(a), undisclosed |
| PF-2ddbc141 | should-not-exist low proportionality | divergence set computed by two independent implementations |
| PF-96cdf9f1 | scope med substance | invalid base64 accepted as captured stream |
| PF-3882d444 | scope med substance | unrelated source templates accepted for unreached D-02 items |
| PF-cf9cf710 | scope med substance | can pass without SC-08 `divergence:` records in build-divergences.md |
| PF-a37e5b40 | design med substance | disclosure may be only escaped byte literals |

**Step 2** — `plan-merge.py set-panel` (value file generated from the recorded panel, only
`disposition`/`resolved_by` changed on ten findings), exit 0; stdout carried the same
check-state block as step 1, then `PANEL cycle 3 -> <FD>/plan.yaml` and `APPLIED <FD>/plan.yaml`.
Resolution rationale (the finding schema admits no rationale key, so it lives here):

- PF-14c27514 → resolved_by T-03: closed by scope, second read (each kind's exact stream-key set checked before comparison). PF-e7dd0045 → resolved_by T-03: PF-14c27514 restates it, same reader verdict.
- PF-c36ed89c → resolved_by T-03 (D-02.choice): closed by scope, first read. The inventory bounds the delta; authorization was NOT judged. PF-7999938a stays open.
- PF-c82fdafb → resolved_by T-01: closed by scope, first read.
- PF-390fdc3e → resolved_by T-03: closed by scope, first read.
- PF-0ab2a541, PF-74107187, PF-f8e3277e, PF-2ddbc141 → resolved_by T-03: closed by the second read.
- PF-b045e378 → resolved_by T-03: closed by disclosure, BRIEF.md:104-110; amending Q3(a) stays the operator's.

Still open: PF-7999938a, PF-d35d903d, PF-502d3541 (operator's); PF-96cdf9f1, PF-3882d444,
PF-cf9cf710, PF-a37e5b40 (second-read med substance, deliberately not applied).

**Step 3** — `plan-merge.py check --file <FD>/plan.yaml --root <worktree>`, exit 0:

```text
OK T-01 11 anchor(s) resolved
OK T-02 2 anchor(s) resolved
OK T-03 1 anchor(s) resolved
CHECK <FD>/plan.yaml against <worktree>: 3 task(s), 14 anchor(s) resolved, 0 failure(s)
```

**Step 4** — `approval: {status: pending}`; T-01, T-02, T-03 all `execution_mode: main-session-direct`. Nothing signed; `.agents/` untouched.
