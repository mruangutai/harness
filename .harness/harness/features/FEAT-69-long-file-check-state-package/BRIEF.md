# BRIEF — FEAT-69 long-file check-state package

## Problem

The operator and code maintainers must currently review and change 5,058 lines of state-checking bootstrap, shared context, 39 active invariant rows, table metadata, and runner logic in one `.claude/skills/harness/bin/check-state.py` file. The file-wide shape obscures input-family ownership, while the existing FEAT-62 lock follows functions only within that one AST and would silently stop enforcing transitive declared reads if invariant bodies were merely moved into imported modules.

## Done when — by perspective

**operator** — I can rely on the hyphenated entry retaining its complete observable contract: normalized baseline-versus-immutable-pin exit status, stdout, and stderr bytes agree for full-table output, `--list`, every owning check-state suite, and both structural-lock clean-tree runs. The proof is reproducible from clean detached checkouts, records raw evidence, and cannot claim receipts existed before the pin they evaluate.

**code maintainer** — I find a thin `check-state.py` entry over an importable `check_state/` package whose context, table, runner, and invariant families have explicit ownership without moving discretion out of the table. Every function on that full surface meets code grade 4 or better, and the package-aware structural lock still follows transitive calls, declared reads, authority, module-body, no-reparse, broad-catch, and reads-family rules rather than going vacuously green at an import boundary.

## Success criteria

- SC-01 (code maintainer): For FEAT-69-long-file-check-state-package at the immutable implementation pin, the code-grade analyzer reports every function in `.claude/skills/harness/bin/check-state.py` and every Python file under `.claude/skills/harness/bin/check_state/**` at grade 4 or better. The set explicitly includes `_inv41_invocation`, `_unquoted_hash_digit`, `_quoted_scalar_closed`, and `inv_49`; moved functions retain grade identity against their baseline pre-images, while every genuinely new lock-walker or table-glue function is graded as new with no exemption. A committed red-first receipt shows this exact file-wide assertion failing against baseline `a726bad8` and passing at the pin.
  verify: automated
  evidence: unit
- SC-02 (operator): Clean detached checkouts of baseline `a726bad8` and the immutable implementation pin produce identical exit status, stdout bytes, and stderr bytes after replacing only each checkout's raw absolute root with one common token for: one full-table run over every feature, `--list`, all nine suites `test-check-state.py`, `test-check-state-entry.py`, `test-check-state-plans.py`, `test-check-state-records.py`, `test-check-state-handoff.py`, `test-check-state-worktrees.py`, `test-check-state-inv26.py`, `test-check-state-feat59.py`, and `test-check-state-table.py`, plus clean-tree `feat62_findings` and `consolidation_findings` runs. Raw bytes and hashes are retained; every non-root byte difference is ledgered as exact old and new bytes and leaves this criterion unmet unless the operator rules otherwise.
  verify: automated
  evidence: integration
  fail-first: the baseline-versus-pin byte comparison is this semantics-preserving refactor's fail-first equivalent; the pin side does not exist before implementation.
- SC-03 (code maintainer): At the immutable pin, automated structural cases prove the entry remains the only forked interface; `table.py` alone imports all families and owns `INVARIANTS` in the baseline's exact order; family functions retain the settled ownership and signatures; `runner.py` alone selects and executes rows; and no family knows the runner. `feat62_findings` parses the entry and every `check_state/*.py` file into one function table, applies the unchanged module-body, no-reparse, transitive declared-reads, and authority rules package-wide, adds the reads-family rule, and applies the broad-catch ceiling of zero to every package file. Mutants demonstrate that cross-module undeclared reads, including a spawn two helpers deep, and rows whose functions do not live in a module named by their reads are rejected.
  verify: automated
  evidence: integration
- SC-04 (operator): Inspection of committed receipts finds that the immutable implementation pin predates every receipt-script and receipt commit, and every receipt names the full baseline and pin SHAs, clean detached checkout identities, exact commands, one execution per measurement, raw and normalized byte hashes, comparison results, the code-grade records, and the complete exact-byte divergence ledger. The receipt scripts reuse the FEAT-68 baseline, clean-pin, and grade-assert structure rather than introducing a second proof system.
  verify: inspection

## Verification gaps

- none; unit and integration runners are active, and immutable-pin chronology and provenance are graded by inspection of committed receipts.

## Constraints

- Preserve the operator-set package split: keep the hyphenated `.claude/skills/harness/bin/check-state.py` path as the thin forked entry and add importable `.claude/skills/harness/bin/check_state/` with `__init__.py`, `ctx.py`, `table.py`, `runner.py`, and the settled input-family modules. Keep `Ctx` whole in `ctx.py`; no additional split is required.
- Preserve exact family ownership by declared reads: `plan.py` owns INV-35/3/4/5/34/32/44; `feature_record.py` owns INV-1/2/6/7/8/12/18/22/23/33 and ledger INV-39/40/43/47 with `collate_feat59`; `run_state.py` owns INV-15/16/36/46; `seams.py` owns INV-17; `brief.py` owns INV-38/41/49 and the INV-38..41 helpers; `worktrees.py` owns INV-25/27/29/31; `board.py` owns INV-13/21/24/26/28/30/37; and `host.py` owns INV-19/42/45/48. The accepted judgment placements are INV-1/2 in `feature_record.py` and INV-27/31 in `worktrees.py`.
- Keep discretion in `table.py`: it imports every family and owns `INVARIANTS` in today's exact order. Families export `inv_NN(ctx[, feat]) -> (bad, warn)`, know nothing of the runner, and have no per-family entry points; `check-state.py` never selects families.
- Preserve every invariant's behavior, message text, severity, table order, runner ordering, exit semantics, and retired-number handling. Comments move byte-for-byte with their code, including all four load-bearing `# INV-32 … BEGIN/END` markers; no rename is permitted beyond the package split.
- Make the FEAT-62 lock package-aware by the settled option (a): one combined function table and one package-wide transitive call walk. Keep the four existing rules unchanged and add the reads-family rule. Per-module option (b) is rejected because it makes the declared-reads rule vacuous across imported helpers.
- Migrate both live `INV-\d+` text scanners to the package glob, adapt all scratch-bin copies and source mutants to copy and patch the package, and re-key by rule every canonical-reader identity whose source moved plus the fixture's `scanned_files` entry. Preserve the ten identifiers supplied by the grilling artifact, including `station_of` and `_handoff_exempt`, as anchored examples rather than the complete live set. Preserve CI and session-entry compatibility at the unchanged entry path, preserve CODEOWNERS' deliberate non-ownership of DEC-174 enforcement scripts, and at most update its existing explanatory comment to name the package. Keep the broad-catch ceiling at zero for every package file.
- Baseline is `a726bad8`. Baseline and pin measurements run once each in clean detached checkouts under `.claude/worktrees/harness/`; checkout-root normalization is the only normalization, and every other byte difference is recorded exactly. Receipts are committed only after the immutable pin and name its full SHA.
- DEC-174 BLOCKS team execution of the enforcement scripts and their owning tests; all implementation and proof collection is main-session-direct. DEC-205 SUPPLIES retired-number non-reuse, DEC-188 SUPPLIES the authority rule, and DEC-156/182/203/231 SUPPLY the invariant-row contracts that must remain unchanged.
- Approval remains pending. At signature, the recommended rework ruling is two rounds and 480 wall-clock minutes, based on the recorded 5–6 hour build estimate and one to two validation cycles.

## Out of scope

- `plan-merge.py`, `validate-digest.py`, `check-domain.py`, `gh-sync.py`, and `check-plan-routes.py` as long-file refactors — they belong to later waves; only the package-aware FEAT-62 lock and scanner changes in `check-plan-routes.py` are in scope.
- The 19 remaining grade-1 functions, comprising 10 CLI dispatchers and 9 light functions — they belong to the dispatcher wave.
- Any file-length ratchet or cap — the operator ruled prose first and will revisit only if evidence shows it does not hold.
- Any change to invariant behavior, message text, severity, order, or any unrelated long file.
- The stringly typed navigation family represented by 918 `.get` sites.

## Approval

status: approved
approved-by: molchairuangutai
date: 2026-09-28
