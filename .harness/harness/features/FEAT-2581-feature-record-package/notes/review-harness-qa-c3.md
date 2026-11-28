# QA test-matrix gate — FEAT-2581 — run 2026-11-27-03-validate-validator (c3)

**BLUF: FAIL. The cause is environmental and in no fix-round code. The matrix itself is green.**

- **The failing gate:** T-03's signed `verify:` block, run verbatim at `c039c32d`, exits 1 (QA-c3-1).
  - Its `test_change` check compares `git diff` output, whose `index` lines carry abbreviated blob hashes, against the committed records in `build-divergences.md`.
  - git sizes the default abbreviation from the object count. The shared object store now holds **65,632 objects, which is past 2^16**, so git prints 9 hex digits where the committed records carry 8. Round 2 measured the same check green.
  - One-factor control: the identical verify with only `core.abbrev=8` injected (`GIT_CONFIG_COUNT`) exits 0 and prints `T-03 receipts PASS at c039c32d…`.
- **The matrix:** both required kinds ran once each and exited 0, and both receipts are free of defects (`unit` 68/68, `integration` 94/94). `matrix_ok: true`.
- **T-01 and T-02 verifies:** both exit 0.
- **P1, P2, P3, P4, P5 and P6:** all confirmed by execution. P1 includes the other-uid case, which was feasible (root-owned `/Library` and `/private/var`), and each of P1's three refusal conditions has its own mutant, each of which turns a row from refused to accepted. P2 has an old-blob fail-first.

## Matrix floor (policy read at the pin)

- **Policy blob:** `git show c039c32dea25d26e3235ee90e1343d7280ddfd4e:.harness/harness.json`, from repository `mruangutai/harness`. The feature is unbound, so its own repository applies.
- **Required kinds:**
  - `test_matrix.cross_module.always` is `[unit, integration]`. T-01 and T-03 are `cross_module`.
  - `docs.always` is `[]`. T-02 is `docs`.
  - Both kinds are `active`.
- **Pin agreement:** at tip `177af2d5`, `feature.json` records review_sha `c039c32d…`. `git diff --quiet c039c32d HEAD -- . ':!<FD>'` gives rc 0.
- **Fix delta:** `a03103b0..c039c32d` touches only `<FD>/` (checked with `git diff --name-only`).
- **Untouched surfaces:** the feature diff touches no `.ts`/`.tsx`, `evals/`, `tests/manual/` or e2e paths, so no further kinds apply. This is unchanged from c2.

| kind | state | cmd (run from the pin, `env -u HARNESS_AGENT_TYPE`) | runner exit | files | receipt sha256 |
|---|---|---|---|---|---|
| unit | satisfied | `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest <run>/qa/manifest-unit.json` | 0 | 68/68 exit 0 | `75f71f3e…5d314d5a` |
| integration | satisfied | `… --kind integration --shard 1/1 --manifest <run>/qa/manifest-integration.json` | 0 | 94/94 exit 0 | `94ae9f83…a83e3bf96` |

- **Checkout:** `pinned-checkout.py add … --sha c039c32dea25d26e3235ee90e1343d7280ddfd4e`.
  - HEAD was `c039c32d…`, and `git status --porcelain` was empty both before and after the run.
  - I ran `bun install --frozen-lockfile` first.
  - I removed the checkout on return (`remove`, rc 0).
- **Receipts:** both have `tested_commit` `c039c32d…`, `runner_exit` 0, and every `completed_files[].returncode` equal to 0. Using the installed `check-integration-shards.py` with validate-digest's own call shape (`validate-digest.py:2807-2811`), `discover_expected` returns 68/94 and `evidence_defects` returns `[]` for each.
- **Full runner output, as host scratch files:**
  - `/tmp/feat2581-qa-c3-unit.log`: 3158 lines, sha256 `8ad31177…6e42c2`.
  - `/tmp/feat2581-qa-c3-integration.log`: 8558 lines, sha256 `2ed13eae…1c3c`.

## Plan verify blocks (extracted with `yaml.safe_load` from `git show c039c32d:<FD>/plan.yaml`; run from the worktree root)

| task | `bash -e` exit | plain `bash` exit | tail |
|---|---|---|---|
| T-01 | 0 | 0 | `T-01 structure and smoke PASS`, then the `ALL PASS` output, then `0 unresolved reader site(s) across 110 Python file(s)` |
| T-02 | 0 | 0 | `T-02 decisions PASS`; the index diff is empty |
| T-03 | **1** | 0 | `verifying at c039c32d… (review_sha)`, then an `AssertionError` at `<string>` line 23: "build-divergences.md test_change records are not the baseline-to-pin diff of every changed test path" |
| T-03, control `core.abbrev=8` | 0 | — | `T-03 receipts PASS at c039c32d…` |

## SC evidence and fail-first

Only SC-03 and SC-04 are `verify: automated`. Every other SC is `inspection`.

- **SC-03 (unit):**
  - All 68 files exit 0 at the pin.
  - The only `FAIL` lines are the four `BUG-1290` lines inside the `test-factory-claim-mutation.py` block, which starts at log line 314. That file exits 0.
- **SC-04 (integration):**
  - All 94 files exit 0, with no `FAIL` line.
  - `test-check-state-feat59.py` exits 0 (log line 1906).
  - `test-feature-json-merge.py` is absent.
- **Fail-first equivalent (designated by the BRIEF):** I recomputed `notes/measurements/baseline.jsonl.gz` from `git show c039c32d:` myself. It is byte-unchanged since `a03103b0`.
  - It holds 163 suite records: 68 unit `.py`, 94 integration and 1 bun.
  - The only nonzero exit is `test-typescript-typecheck.py` (1).
  - The only exit-0 file with FAIL lines is `test-factory-claim-mutation.py` (4).
  - **Tier:** identity evidence, not a natural RED.

## Fix-round claims: executed checks (`/tmp/feat2581-qa-c3-probe/probe.py`, output `probe-out.json`, run as uid 501)

- **P1: confirmed.** I extracted `private_parent` from the `c039c32d` blob with `ast` and called it on scratch paths.

  | Case | Result |
  |---|---|
  | absent | accepted, created at 0700 |
  | own 0700 | accepted |
  | own 0750 | accepted |
  | own 0755 | accepted |
  | own 0777 | refused, `sys.exit` |
  | own 0775 | refused, `sys.exit` |
  | own 0702 | refused, `sys.exit` |
  | own 0720 | refused, `sys.exit` |
  | symlink to own 0700 | refused, `sys.exit` |
  | dangling symlink | refused, `sys.exit` |
  | regular file 0600 | refused, `sys.exit` |
  | **other uid:** `/Library` (root, 0755) | refused, `sys.exit` |
  | **other uid:** `/private/var` (root, 0755) | refused, `sys.exit` |
  | **other uid:** `/private/tmp` (root, 1777) | refused, `sys.exit` |

  - **Mutants, one leg dropped at a time:**
    - Without the `S_ISDIR` check, both symlinks and the regular file are accepted.
    - Without the `uid` check, `/Library` and `/private/var` are accepted.
    - Without the `& 0o022` check, 0777, 0775, 0702 and 0720 are accepted.
    - **Old `makedirs(exist_ok=True)`:** accepts every symlink-to-dir, writable and other-uid row.
  - Each check therefore decides at least one row on its own.
  - I never touched `/tmp/feat2581-ledger`.
- **P2: confirmed, with old-blob fail-first.** I wrapped a scratch `feature-record.py` with `PYTHONPATH` set to a copy of the recorder blob.

  | Recorder | Case | Exit | stderr | Child runs | Records |
  |---|---|---|---|---|---|
  | `c039c32d` | kill -9 | -9 | empty | 1 | 1 (`-9`) |
  | `c039c32d` | kill -15 | -15 | empty | 1 | 1 (`-15`) |
  | `c039c32d` | exit 3 | 3 | relayed `e`; stdout `o` | 1 | 1 (`3`) |
  | `a03103b0` | kill -9 | -9 | `Error in sitecustomize … OSError: [Errno 22]` | **2** | 1 |

  - SIGSTOP is not probed. A stopped child never returns from `subprocess.run`'s wait, so that branch is unreachable as written. This is reasoned, not run.
- **P3: confirmed.** The footer now reads `decompressed jsonl sha256`. Its values `3a8fb085…` and `59e5b9ae…` equal my own `gunzip | shasum -a 256` of the two blobs and are unchanged from `a03103b0`.
- **P4: confirmed.**
  - The generated-receipt diff `a03103b0..c039c32d` is exactly three `script_sha256` lines, the two relabelled footer lines and the `generated` stamp.
  - All three new `script_sha256` values equal the blob hashes.
  - `build-divergences.md`, `divergence-rulings.json` and `measurements/` are byte-identical (`git diff --quiet` rc 0).
  - The recorder change is named in `clean-pin-byte-receipts.md`'s round-2 disclosure, which states that the measurements predate it.
- **P5: split.**
  - **Holds:** `code-grade.py --base e12381fd --head c039c32d` exits 0 with `PASSING: 280` and zero `RESULT: FAIL`. The new or changed functions grade as follows: `private_parent` 4, `_exit_as` 5, `measurement_provenance` 5.
  - **Fails:** T-03's verify does not pass today (QA-c3-1).
- **P6: confirmed.** The reworded F-1 is true: `load_rulings` (`feat2581-cleanpin.py:384-390`) writes only `[]\n`, and only when the file is absent.

## Findings

- **QA-c3-1. Kind: substance. Severity: high, gating. Owner: T-03 (`notes/**` plus the signed verify).**
  - **The defect:** T-03's verify, and its generator `feat2581-cleanpin.py:362`, build the expected `test_change` bytes with `git diff`, and nothing fixes the abbreviation length. The `index <a>..<b>` lines therefore depend on the object count of whichever repository runs the check.
  - **Measured:**
    - `git count-objects -v` reports `in-pack: 65632`.
    - The committed records carry 28 `index` lines with 8-digit hashes; git now prints 9.
    - Every one of the 29 `test_change` records mismatches, and the verify exits 1.
    - With `core.abbrev=8`, it exits 0.
  - **Not caused by `c039c32d`:** the bug was latent since build. It surfaced once the shared store passed 65,536 objects. A fresh clone or CI checkout will pass or fail depending on its own object count.
  - **Repair options, for the lead to route:**
    - (a) Regenerate `build-divergences.md` with `cleanpin --reuse`. This is a T-03 notes change, but it stays fragile.
    - (b) Make both sides independent of repository size, for example `--full-index` or `--abbrev=40` in the generator and the verify. This amends the signed verify, so it is operator-gated (open question QA-c3-OQ1).
- **QA-c3-2. Kind: form. Severity: low, non-gating.** T-03's verify block is several shell lines with no `set -e`. Run under plain `bash`, the block exits 0 even though its main assertion failed, because the last line (the audit) exits 0. Its exit status is honest only under `bash -e`. I found no automated verify executor in `bin/` to show which shell runs it.

## Executed vs reasoned

- **Executed:**
  - both suites, once each, plus the receipt-defect check
  - the three verifies, under both `bash -e` and plain `bash`
  - the T-03 abbrev control
  - the baseline-record recompute
  - the P1 shape and mutant table, including other-uid
  - the P2 current and old-blob probes
  - the P3 hashes
  - the P4 byte diffs
  - `code-grade`
- **Reasoned, not run:**
  - SIGSTOP being unreachable
  - CI and fresh-clone behaviour of QA-c3-1
  - that c2's green T-03 ran below 2^16 objects

## Principles applied

- **harness-verification-rules (skill):** I read the floor from the pin blob, took state from the runner's exit and per-file headers, and graded fail-first by tier. A green matrix did not hide a red task verify.
