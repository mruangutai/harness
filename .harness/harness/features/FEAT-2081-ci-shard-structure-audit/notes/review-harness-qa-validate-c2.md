# QA gate — FEAT-2081 at review_sha f2791446 (validate c2)

**BLUF: PASS.** One final matrix at a clean exact pin `f2791446c294abb5b26e6bcf663b25ee86b6dcce` (`git rev-parse HEAD` = pin, `git status --porcelain` empty;
managed `pinned-checkout.py`, key `FEAT-2081-ci-shard-structure-audit--validate-c2--harness-qa`, removed on return): unit exit 0, integration exit 0.
No changed-code/spec blocker prevents moving `uat.md` to ready. I authored nothing, mutated nothing; cycle-1 fail-first receipts stand.

## Delta scope
`fc942ec4..f2791446` touches only three bin files (via `.claude/skills/harness/bin/`, same files as `.agents/...`): `check-integration-shards.py` (`_parse` split to
`_missing_options`/`_value_problems`), `run-unit-tests.py` (`_tokens`→`_take_option`; `_parse`→`_check_combinations`; `_load_weights`→`_check_provenance`/`_check_weights`),
`run_pool.py` (`main`→`_record_completed`), plus panel notes and a 3-line `uat.md` wording change. Zero test files changed. Pure extract-helper refactor; diff read: same conditions, messages, order.

## Matrix (harness.json; run with `env -u HARNESS_AGENT_TYPE`, repo G-07)
| kind | state | cmd | discovery | result |
|---|---|---|---|---|
| unit | satisfied | `run-unit-tests.py --kind unit` | **49 files** (= `ls tests/unit/test-*.py`), 8 workers | exit 0 |
| integration | satisfied | `run-unit-tests.py --kind integration` | **76 files** (= `ls tests/integration/test-*.py`), 8 workers | exit 0 |
`matrix_ok: true`. T-01/T-03 cross_module and T-02 feature need unit+integration (both satisfied); T-04 config (shape trigger not tripped, integration satisfied anyway); T-05/T-06 docs none.
Plan verify scripts each printed their own `PASS` inside those runs (exit 0): unit `test-runner-unsharded` (1.11s), `test-integration-shard-validation`, `test-structure-audit-index`;
integration `test-run-unit-tests-shards` (7.14s), `-kinds`, `-layout`, `test-run-pool` (5.29s), `test-integration-shard-aggregation` (2.72s), `test-structure-audit-single-pass`, `test-checker-structure-locks`.
Not re-run individually (the suites execute them). Canonical-reader audit run directly: `0 unresolved reader site(s) across 97 Python file(s)`, rc 0. FAIL-token lines in the unit log are
only `test-factory-claim-mutation.py`'s deliberate BUG-1290 mutation-proof output (repo G-09); the one `ERROR could not resolve scan root` is an expected negative inside a passing test.

## Changed-behavior coverage at the pin
| changed helper | exercising tests (results above) | limit |
|---|---|---|
| `_take_option`/`_tokens`, `_check_combinations`, `_parse` (run-unit-tests) | `test-run-unit-tests-shards.py` BAD_ARGS (14 refusals: missing value, repeated shard/manifest, manifest-without-shard, check-layout+shard/manifest; `--kind` after `--shard`), `-kinds`, `-layout`, `test-runner-unsharded` | unsupported-option diagnostic branch not directly asserted |
| `_check_provenance`/`_check_weights`/`_load_weights` | positive path runs on every shard fixture and the checked-in document; document shape asserted by the shards test | **no test feeds an invalid duration document to the runner** (refusal branches unasserted; unchanged from c0) |
| `_missing_options`/`_value_problems`/`_parse` (check-integration-shards) | aggregation: absent/unrecognized checks/matrix result (exit 2), abbreviated `--commit` ("full hexadecimal object id") | missing `--commit`/`--manifest-dir`, invalid `--shards`, unrecognized argument: no test (unchanged from c0) |
| `_record_completed` (run_pool) | `test-run-pool.py` completed-seam cases (every finished script + rc recorded; default output unchanged) | `completed=None` path covered by every CLI use |

**Supplementary read-only differential (not a repo test, nothing authored):** an in-memory loader exec'd the `fc942ec4` and pin sources and compared old vs new:
`check-integration-shards._parse` 9 inputs identical (incl. missing, malformed, unrecognized); `run-unit-tests._tokens` and `_parse` **61,882 calls** (every argv up to length 4 over 13 tokens,
exceptions compared by type and message) identical; `_load_weights` 17 documents (missing file, bad JSON, wrong schema, bool/zero/negative/NaN/Infinity, non-dict weights) identical outcomes.
`run_pool.main` is a one-line move behind the same condition. This closes the uncovered branches' regression risk for the delta; it is QA's own probe (tier: differential reproduction), not a gate-owned receipt.

## fail_first mapping (unchanged from cycle 1; retained, not re-derived)
Source: `notes/review-harness-qa-validate-c0.md` § fail_first and `notes/evidence-T-01.md`, `evidence-T-02.md`, `evidence-T-03.md`, `qa-structure-audit-equivalence.md`.
The delta changed no behavior and no tests, so no receipt is invalidated; the c0 pinned tests still name the same asserted behaviors and are green here.
- SC-01 (N): `test-run-unit-tests-shards.py` vs pre-fix runner, exit 1, 25 FAIL / 8 PASS (partition, LPT weighting, tie-break, unknown file, empty shard, 14 malformed args, manifest completed-vs-selected).
- SC-02 (N+M) / SC-03 (N+M): pre-gate `cannot load gate` / `FileNotFoundError`; per-defect mutation tables in evidence-T-02; c0 QA reproduced `cancelled` acceptance and duplicate-threshold mutants at fc942ec4.
- SC-06 (N): old checker via `CHECK_PLAN_ROUTES_BIN` fails `test-structure-audit-single-pass.py` with 9 failures vs post exit 0 (99 trees/202781 visits).
- SC-07 (M): drop-first-file, destroy-attribution, mask-failure mutations (evidence-T-01; c0 QA reproduced M1/M3).
- SC-08 (M+N): integration rows of the same mutations; `run_pool.main(completed=)` TypeError natural red.
Red-first applicability at this pin: all these receipts bound to pre-delta code; the delta is behavior-preserving (differential above), so they carry. Not re-run, per instruction.

## Findings
1. **low / coverage / T-01** — `_load_weights` refusals (invalid/ non-positive / non-finite / wrong-schema duration document) have no discriminating test. Fix (optional, dev/Main): one shards-test case writing a bad document and asserting runner exit nonzero. Pre-existing from c0; refactor proved identical by differential.
2. **low / coverage / T-02** — `check-integration-shards._parse` missing `--commit`/`--manifest-dir`, bad `--shards`, unrecognized-argument branches untested (only abbreviated `--commit` is). Fix (optional): three aggregation CLI cases expecting exit 2. Pre-existing; refactor identical by differential.
3. **info / assurance** — c0 note finding 1 (no unit-index red-first) and 2 (author-run mutation tables, tier M) are unchanged and retained. No new finding introduced by the delta.

## UAT-ready blocker answer
**No changed-code/spec blocker.** Code-risk closure of the five extracted functions is the code reviewer's grading call, not QA's; behavior regression: none. Ordinary ledger items remain for Main: fill `review_sha: f2791446…`, current inspection/readiness columns, Main's own final whole-suite receipt (my run may be cited, not substituted). The `uat.md` wording change makes L-01 mandatory user-executed under SC-10 (read at diff; the user's execution stays pending, not a blocker). SC-09/SC-10 pending USER UAT; not graded here.

## Assurance bounds
Live Actions facts are context, not re-observed. Matrix executed once; no repeated runs. Differential script lived in /tmp only. Edits to bin are refused to harness-qa and none made.
