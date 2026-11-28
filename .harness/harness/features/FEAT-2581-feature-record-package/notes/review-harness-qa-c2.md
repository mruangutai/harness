# QA test-matrix gate — FEAT-2581 — run 2026-11-27-02-validate-validator (c2)

**BLUF: PASS.** `matrix_ok: true` at review_sha `a03103b0d85128217401dc84157bfa97827f8a96`.
- Both required kinds (`unit` 68/68, `integration` 94/94) ran once each and exited 0. Each has a runner receipt, and both receipts are free of defects under `check-integration-shards.evidence_defects`.
- The T-01, T-02 and T-03 verifies, run verbatim, all exit 0. T-03 is new evidence: it reads the regenerated receipt and reports `T-03 receipts PASS at a03103b0…`.
- I tested the fix-round claims by execution:
  - **CR-1:** confirmed.
  - **CR-2, generator half:** confirmed, with old-blob fail-first.
  - **SEC-1:** confirmed for the four leaf directories. One low, non-gating residual remains on the ledger's parent directory (finding QA-c2-1).

## Matrix floor (policy read at the pin)

- **Policy blob:** `git show a03103b0…:.harness/harness.json`, from repository `mruangutai/harness`. The feature is unbound, so its own repository applies.
- **Pin agreement:** `feature.json` at branch tip `b22e5989` records review_sha `a03103b0…`, which matches the dispatch pin. `b22e5989` changes only the feature dir.
- **Required kinds by change type:**
  - T-01 is `cross_module`, so it always requires `unit` and `integration`.
  - T-02 is `docs`, so it requires none.
  - T-03 is `cross_module`, so it always requires `unit` and `integration`.
  - `cross_module` has no `when:` clauses.
- **Fix-cycle delta:** `62da4501..a03103b0` touches only this feature's `notes/`. Outside the feature dir, `git diff --quiet c91df7a5 a03103b0` gives rc 0.
- **Untouched kinds:** the feature diff touches no `.ts`/`.tsx`, `tests/manual/**`, `evals/**`, spec or e2e paths. So `typecheck`, the `locally_run` probes, `eval`, `component` and `ui` are not required.

| kind | status | state | cmd | runner exit | files | receipt sha256 |
|---|---|---|---|---|---|---|
| unit | active | satisfied | `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest <run>/qa/manifest-unit.json` | 0 | 68/68 exit 0 | `a9f88fbb…eb5a25` |
| integration | active | satisfied | `… --kind integration --shard 1/1 --manifest <run>/qa/manifest-integration.json` | 0 | 94/94 exit 0 | `942cf081…43dd` |

## How I ran

- **Managed checkout:** created with `pinned-checkout.py add --feature FEAT-2581-feature-record-package --run-id 2026-11-27-02-validate-validator --persona harness-qa --sha a03103b0…`.
  - HEAD was `a03103b0…`, and `git status --porcelain` was empty.
  - I ran `bun install --frozen-lockfile` first (repo G-12).
  - Each suite ran once, under `env -u HARNESS_AGENT_TYPE`.
  - I removed the checkout on return (`remove`, rc 0).
- **Receipts:** written by the runner and never edited. They are at `runs/2026-11-27-02-validate-validator/qa/manifest-{unit,integration}.json`.
  - Both carry `tested_commit` `a03103b0…` and `runner_exit` 0.
  - Every `completed_files[].returncode` is 0.
  - Against the installed `check-integration-shards.py`, using validate-digest's call shape: `discover_expected` returns 68/94, and `evidence_defects` returns `[]` for both.
- **Full runner output:**
  - `/tmp/feat2581-qa-c2-unit.log`: 3158 lines, sha256 `f704e4f3…f817`.
  - `/tmp/feat2581-qa-c2-integration.log`: 8558 lines, sha256 `5094a83a…3433`.
  - These are host scratch files, because QA's write grant excludes `runs/` logs. The per-file exits and verdict lines are reproduced below.
- **Plan verifies:** I extracted the verifies verbatim from `git show a03103b0:<feat>/plan.yaml` with `yaml.safe_load` and ran each with `bash -e`, which is stricter than plain bash: any failing line fails the run.
  - T-01 and T-02 ran in the pin checkout.
  - T-03 ran from the worktree root. Its binding reads `feature.json`'s review_sha, which is `a03103b0` only at the tip. The tip differs from the pin only inside the feature dir.

## Plan verify blocks

| task | exit | output tail |
|---|---|---|
| T-01 | 0 | `T-01 structure and smoke PASS; …`, then `Ran 130 tests … OK` (test-feature-record), then `ALL PASS` (test-validate-feature-json), then `0 unresolved reader site(s) across 110 Python file(s)` |
| T-02 | 0 | `T-02 decisions PASS`. The `gen-decisions-index.py --stdout \| diff` output was empty. |
| T-03 | 0 | `verifying at a03103b0… (review_sha)`, then `T-03 receipts PASS at a03103b0…`, then `0 unresolved reader site(s) across 110 Python file(s)` |

## SC evidence and fail-first

Only SC-03 and SC-04 are `verify: automated`. SC-01, SC-02 and SC-05 through SC-10 are `inspection`; T-03's verify recomputes them, and it passed.

- **SC-03 (unit):**
  - At the pin, all 68 files exit 0. Their baseline set equals the receipt's set: the baseline's 69 unit records minus `omp-hooks.test.ts`, which `--kind unit` does not run.
  - The only `FAIL`-token lines are the four from `test-factory-claim-mutation.py`, which itself exits 0.
- **SC-04 (integration):**
  - At the pin, all 94 files exit 0, with no `FAIL` line. This includes `test-check-state-feat59.py` (INV-40).
  - `test-feature-json-merge.py` is absent.
  - The 94 files equal the baseline's 94 integration records.
- **Fail-first equivalent:** the BRIEF names this explicitly as the equivalent for a semantics-preserving move, and the operator signed it.
  - The source is the committed baseline-side records in `notes/measurements/baseline.jsonl.gz`, read at `a03103b0`. They are byte-unchanged since `62da4501`. I recomputed them from the raw base64:
    - 163 suite records.
    - The only nonzero exit is `test-typescript-typecheck.py` (1).
    - The only exit-0 file with FAIL lines is `test-factory-claim-mutation.py` (4).
  - The receipt line `baseline_failing: tests/integration/test-typescript-typecheck.py 1 1` agrees.
  - **Tier:** this is identity evidence, not a natural RED. It shows the same files pass with the same FAIL lines on both sides. It shows nothing about how well the tests discriminate, and I am not claiming they fail to.

## Pre-existing failures (baseline-equivalent, not regressions)

- **`test-typescript-typecheck.py`:** the baseline record exits 1 with `FAIL no installed compiler at …`, and the pin record shows the same. In my run it exits 0, because `bun install` supplied `tsc`. It is listed, not compared.
- **`test-factory-claim-mutation.py`:** in my pin run it exits 0 and prints four `FAIL  BUG-1290 5a/5b/5c/5b` lines. These are byte-identical, in order, to the baseline record's four lines, and that record also exits 0. I graded on the runner's exit and on the per-file headers, never on a `^FAIL` count (repo G-09).

## Fix-round claims: executed checks

- **Claimed file set:** `git show --stat a03103b0` touches exactly 7 files, all under `notes/`: five receipt scripts plus the two receipts.
  - `build-divergences.md`, `measurements/` and `divergence-rulings.json` are byte-unchanged between `62da4501` and `a03103b0` (rc 0).
  - The generated receipt diff is exactly the five `script_sha256` lines and the `generated` stamp.
  - The pre-refactor measurement bytes are disclosed in `clean-pin-byte-receipts.md`.
- **CR-1, base-versus-pin probe:**
  - `code-grade.py --base e12381fd --head a03103b0` exits 0, with 279 passing and zero `RESULT: FAIL`.
  - The same command at `--head 62da4501` exits 1 with 12 FAIL results, all in `notes/receipt-scripts`.
  - At `a03103b0`, all 144 receipt-script functions grade at least 4, and each of the twelve is now grade 4.
- **CR-2, generator half (mutant):**
  - I loaded `feat2581-cleanpin.py` from `a03103b0` in-process, with its `main()` stripped so it writes nothing. It ran against the real measurements and rulings in the pin checkout.
  - Control: `divergence: audit:stdout RULED`, `overall: PASS`, 631 divergences, 0 unruled.
  - Mutants: for each of by, date and reason, I tried `None`, `""`, `"   "` and the int `7`, plus a missing `reason`. Every one gives `divergence: audit:stdout UNRULED`, `overall: FAIL` and 1 unruled.
  - **Fail-first:** the old `Derived.ruled` blob from `62da4501`, executed, returns `True` for a `None` value of by, date or reason. The new blob returns `False`.
  - The verifier half is dispositioned (OQ-V1). I note it and do not gate on it.
- **SEC-1:**
  - I executed `private_dir` from the `a03103b0` blob on scratch paths:
    - A fresh path becomes mode 0700.
    - An existing 0777 directory with contents is replaced at 0700.
    - A symlink in its place raises `OSError`.
    - An unremovable subtree raises `PermissionError`.
  - `build_scratch` in replay has the same shape.

## Findings

- **QA-c2-1. Kind: substance. Severity: low. Non-gating; owned by T-03 `files:` (`notes/**`).**
  - **The gap:** `prepare_scratch` in `feat2581-ledger-driver.py` creates the parent `/tmp/feat2581-ledger` with `os.makedirs(..., mode=0o700, exist_ok=True)`. That call never checks an existing parent's type, owner or mode. Executed: `makedirs(exist_ok=True)` accepted a symlink-to-directory without error.
  - **Failure scenario:** another local user pre-creates `/tmp/feat2581-ledger` as their own directory, or as a symlink. The 0700 leaf `baseline`/`pin` is then created inside a directory that user controls, so they can rename or swap it between the driver's runs.
  - **Impact today:** the committed measurements predate this code, being reused with `--reuse`, so no committed evidence is affected. This only matters on a future re-measure.

No other findings.

## Per-file results at the pin (runner `----- <file> (exit N, …)` headers)

- **unit (68, all exit 0):** answers-provenance, check-state-corpus-rules, broad-catch-census, config-shape-matrix, check-state-inv26-routing, check-state-inv37-local-binding, artifact-accessors, check-state-shipped-ctx, digest-record, digest-dev-skill, decision-disposition-schema, factory-claim-mutation, check-state-inv35, factory-cli, factory-gh, expertise-ops, factory-claim, factory-land, factory-config, digest-schemas, feature-json-budget, feature-json-reader, feature-schema-build-entry, fleet-product-config, gate-policy, factory-workspace, gen-craft-index, gh-board-item-add, feature-corpus-discovery, gh-cost-log, gh-sync-abandon-sources, gh-sync-build-entry, handoff-policy, gh-board, handoff-done-when, feature-corpus-gates, harness-boundary, and the rest. The last line is `pool: 8 workers, 68 files`. Every header reads exit 0; a grep for a non-`exit 0` header was empty.
- **integration (94, all exit 0):** the 94 headers all read exit 0, and a grep for non-zero was empty. The tail is `ALL PASSED.` and `pool: 8 workers, 94 files, 177.06s wall`.

## Executed vs reasoned

- **Executed:**
  - both suites, once each
  - the receipt `evidence_defects` check
  - the three verifies, verbatim
  - the baseline-record recompute
  - the FAIL-line byte comparison
  - code-grade at both pins
  - the CR-2 mutants and the old-blob comparison
  - the SEC-1 `private_dir` probes
  - the file-set and byte-identity diffs
- **Reasoned:**
  - the QA-c2-1 attack path beyond the executed `makedirs` acceptance
  - that T-03 run at the tip is equivalent to the pin. This follows from the tip touching only the feature dir, which T-03 itself asserts.

## Principles applied

- harness-verification-rules (skill): I read the matrix floor from the pin blob, resolved kind states from the runner's exit and its per-file headers, and graded fail-first by tier.
- I re-took the discrimination proofs at the new pin (expertise G-06) because the receipt scripts were rewritten wholesale.
