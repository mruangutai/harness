# BUG-2565 build receipt: main-session-direct (DEC-174)

Every task in this plan is `execution_mode: main-session-direct`. The main session built each one in
the product checkout, on branch `feat/BUG-2565-digest-frontmatter-contract`, and dispatched no
engineering lead. Test-first order applied to the `logic`/`bugfix` tasks: the tests were written
first and observed failing (RED) before the production change. `docs` work is exempt.

| Task | Commit(s) | Verify result |
|---|---|---|
| T-01 probe: does a hook-refused yield reach the parent? | `7c8b99a0` | `probe receipt ok` |
| T-02 fail-closed yield, schema-control refusal removed | `c68f4af7`, type fix after it | bun 240 pass / 0 fail; typecheck PASS; greps 0; dispatch-guard 426/426 |
| T-03 Python projection + generator | `5acda291` | all cases PASS; 16/16 `parity ok` against the 104252db TypeScript loader |
| T-04 generate all 16 agents, `task.structured` off, drift gate | `84e3b617` | `OMP port surface: ok`; 39/39 cases; check-skill-weight exit 0 |
| T-05 live probe of the generated frontmatter | `caccc607` | `binding receipt ok` |
| T-06 docs and decision amendments | `5385422f` | `decisions ok`, exit 0 |
| SIMPLIFY apply | `7995f460` | test-digest-projection PASS; test-check-omp-port 39/39; port gate ok; `gen-agent-output.py --check` ok |

## RED evidence

- **T-02.** Before the hook change, the rewritten `tests/unit/omp-hooks.test.ts` failed 9 tests:
  - the six validator-failure classes (one parameterised test), which expected the D-02 refusal and got a passing yield;
  - the data-less `type: result` yield, which the old hook returned `undefined` for;
  - the six SC-03 dispatch witnesses (`flat-output-only` … `batch-both-scout`), which the old hook refused or revised;
  - the unavailable dispatch-guard case, which expected an unrevised input.
- **T-03.** `digest_projection.py` was first written ahead of its test. That draft was deleted, the
  tests in `tests/unit/test-digest-projection.py` were written, and RED showed 42 failures
  (module absent) before the module was written again.
- **T-04.** Before the gate change:
  - `check-omp-port.py` passed the schema-drift fixture (exit 0, `OMP port surface: ok`);
  - it failed the `task.structured`-absent fixture;
  - `python3 -c 'print({"a": False} == {"a": 0})'` printed `True`, which is why `typed_equal` exists.
- **T-01, T-05.** These are probes, with no production code. Their receipts are
  `research-yield-refusal-probe.md` and `research-frontmatter-binding-probe.md`.
- **T-06.** `docs`, exempt.

## SIMPLIFY pass

The skill's four reader dispatches go to the engineering squad. Under DEC-174 the main session may
not dispatch `harness-eng-lead`, so the main session ran the four angles itself, read-only first,
over the code diff `104252db..5385422f`:

- **reuse.** Finding: the root-relative path `.claude/skills/harness/schemas/digest` was spelled at
  `gen-agent-output.py:56` and `check-omp-port.py:178`. The cost: two spellings to move in
  lockstep, and this directory has moved once before. Applied: `digest_projection.SCHEMA_RELPATH`.
- **simplification.** Empty. `typed_equal` closes a measured bool/int equality hole, and
  `--check` is part of the signed T-03 spec.
- **efficiency.** Empty. `check-omp-port.py` measured 0.2 s and is on no hook path.
- **altitude.** Leave. The validator-unavailable refusal sits in the yield phase, the one home D-02
  names, and the projection sits beside `digest_schema.py`.

## Known residual for validation

The dispatching main-session process loaded the pre-change `harness-hooks.ts` and keeps enforcing
it until omp restarts. That stale-process class is BUG-2566's subject.

## Fix round 1 (validate run 2026-11-27-06, ESCALATE)

Operator rulings: `notes/answers-2026-11-27-validate-c1.md`. OQ-2's residual is now issue #2593.

- **RED first.** Four regression witnesses were added to `tests/unit/test-digest-projection.py` and observed failing before any production edit:
  - a `$ref`-reached root anyOf was not refused ("no ProjectionError");
  - CRLF bytes were lost when stale output was rewritten;
  - a quoted `"structured"` key was duplicated;
  - an indentationless `output:` sequence was orphaned.
  The first CRLF witness passed vacuously, because `read_text` normalises newlines and an up-to-date file is never written. It was sharpened to force a rewrite, and it then failed.
- **T-03 refactor.**
  - `digest_projection.project` became a keyword-handler table (`KEYWORDS`, `_Site`). The `root` flag survives `$ref`. `resolve_ref` was split into `split_ref` and `step`.
  - `gen-agent-output.py` keeps line endings: it splits on `\n` keeping each terminator and reads and writes bytes. It recognises quoted keys (`TOP_KEY`) and treats indentationless sequence items as part of the value. It writes nothing if any persona fails (`Refused`, `report`).
  - `code-grade.py` over both files: no function below its bar. The 16 agents regenerate byte-identical (`agent output: ok`).
- **OQ-1.** `tests/integration/canonical-reader-classification.json` classifies `_Loader.document` and lists both scripts in `scanned_files`. T-03's `files:` was amended to own it.
- **T-06.**
  - The DEC-100, DEC-127 and DEC-208 index rulings are within the 30-word cap.
  - The SPEC refusal-table Unavailable row names the yield refusal.
  - README and BUILD state "three refusals" and narrow D-03 to task data (OQ-4). The probe receipt gained a correction line.
  - The harness-team lead-schema sentence no longer says the schema is injected.
- **Checks after the last edit:**
  - T-01, T-03 (16/16 parity) and T-06 verifies: exit 0.
  - `test-gen-decisions-index.py`: exit 0.
  - `test-check-plan-routes.py`: ALL PASS.
  - `test-check-omp-port.py`: 39/39.
  - Port gate: ok.
- **Advisory test-function grades left as is.** These are med, never blocking: `walk` and `case_generator` in the projection test are at grade 2. Both are flat fixture walkers whose branches are one assertion each, and splitting them would scatter one case's fixture across helpers.

## Fix round 2 (validate run 2026-11-27-07, ESCALATE on F-1)

Operator ruling: `notes/answers-2026-11-27-validate-c2.md`. A third round, narrow to F-1, with the budget at 3 rounds / 135 minutes.

- **RED first.** Three raw-byte witnesses were observed failing before any production edit:
  - a dash-prefixed sibling key (`-mode: keep`) after a stale `output:` was deleted;
  - a commented indentationless sequence left an orphan, or dropped the comment before the next key;
  - an escaped quoted key (`"struc\u0074ured"`) was duplicated.
- **Repair in `gen-agent-output.py`, inside T-03's files:**
  - `SEQUENCE_ITEM` continues a value only for `-` followed by whitespace or end of line.
  - `value_end` absorbs blank and comment lines only between continuation lines, never after the last one.
  - `top_key` decodes a quoted key through `harness_yaml.load_str`.
  - `render` reads the current and regenerated frontmatter through `artifact_accessors.load_frontmatter`, which refuses duplicate keys. It refuses, writing nothing, if either fails to parse or the non-generated key set differs.
- **Reader classification.** The `other_keys` (canonical, `load_frontmatter`) and `top_key` (exempt, in-memory) rows were added.
- **Checks after the last edit:**
  - `test-digest-projection.py`: PASS.
  - T-03 verify (16/16 parity): exit 0.
  - `test-check-plan-routes.py`: ALL PASS.
  - `test-check-omp-port.py`: 39/39.
  - Port gate: ok; `gen-agent-output.py --check`: ok.
  - Code grade: no function below its bar.
