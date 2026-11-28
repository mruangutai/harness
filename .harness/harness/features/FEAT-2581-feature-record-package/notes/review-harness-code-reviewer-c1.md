# Code review — FEAT-2581, cycle 1

**FAIL at `62da4501` (base `e12381fd`).** T-03's receipt scripts fail the canonical complexity gate, and the receipt verifier accepts JSON nulls as operator sign-off. The package-specific SC-02 grade is green; it is not the full-range DEC-209 grade. No source changed in this review. Human commit in scope: `7694fa0f`.

## Stage 1 — pinned inspection

- **SC-01 / T-01:** `.claude/skills/harness/bin/feature_record/__init__.py:1` (empty blob), exactly ten requested package files; `bin/feature_record/read.py:12–115` owns the moved reader, error type and validation helpers, absent from `bin/artifact_accessors.py`. `bin/feature-record.py:77–84,225–235` imports/dispatches all thirteen distinct handlers (fourteen verbs). `bin/plan-merge.py:132–139` has no `signed_task_hash` re-export; `bin/LAYOUT.md:10` lists the pair. Pinned tree and AST sweep of bin/tests found no surviving legacy module, deleted merge test, legacy import, or aliased accessor call.
- **SC-02 / T-03:** `notes/clean-pin-byte-receipts.generated.md:842–854` gives baseline exit 1, pin exit 0, and all twelve new owners/grades; helper grades follow. Implementation pin `c91df7a5` predates the receipt commit `c65ceb81`.
- **SC-05 / T-03:** `notes/clean-pin-byte-receipts.md:6–9` records 210 checkout, 1 copied and 12 bun calls per side and points to the committed raw records. The literal verifier recomputes the disclosed divergence set and exact payloads from those records, including the CLI delta at `notes/build-divergences.md:8686`, rather than treating `cli_identity: PASS` as proof.
- **SC-06 / T-03:** `notes/receipt-scripts/feat2581-replay.py:42` defines the nine steps; `notes/clean-pin-byte-receipts.md:7` records 43 × 9 identical replay steps. The literal verifier checked every tracked record/step ID and compared the committed before/after bytes and process streams.
- **SC-07 / D-01 / T-01:** `tests/integration/canonical-reader-classification.json:983–1077,2359–2372,2458` migrates the nine rows, removes the merge row, and lists the 110 pinned Python source paths exactly. The four accessor rows (`:10–52`) are unchanged; `feature_record.read.load_feature_json` is the only loader remedy. Pinned-source audit exited 0 with zero unresolved sites, matching `notes/receipt-main-session-T-01.md:13`.
- **SC-08 / D-02–D-03 / T-01 + T-03:** `bin/check-domain.py:1804,1831,1853` (budget/import/crash), `bin/check_state/feature_record.py:209,427` (INV-7/23), `board.py:286,386` (INV-37/26), `ctx.py:361–372` (INV-40), `run_state.py:293` (refusal completion), `table.py:75` (reads column), and `bin/harness_config.py:62` (config validation). The committed receipt `notes/clean-pin-byte-receipts.generated.md:175–193` distinguishes measured and source-only cases. Name loads resolve from the checker's bin in its normal process; the `RepoModuleError` paths still report inability to check, not success. INV-37 stops if either module load fails; `--changed` still selects it for all features because of `gh:auth` (`table.py:178–181`, `runner.py:106–119`).
- **SC-09 / T-02:** `DECISIONS.md:3513,7325,7333,8788–8792` points to schema/binding and removes the exception. The generator's pure render on pinned inputs equaled the committed index byte for byte (`DECISIONS-INDEX.md:242`). The exact T-02 command also has the direct-run receipt at `notes/receipt-main-session-T-02.md:5–12`.
- **SC-10 / T-03:** `notes/clean-pin-byte-receipts.generated.md:11,105,134,828` records the baseline test exclusion, bun and Python case counts, and overall case identity verdict. The literal verifier recomputed these from committed suite records, including full stdout and unchanged source for files with fewer than two observed cases.

## Stage 2 — blocking findings

1. **High · substance · T-03 — DEC-209 code grade fails.** Running `code-grade.py --base e12381fd… --head 62da4501…` exited 1: seven newly added production-grade records below the bar, all under `notes/receipt-scripts/`. If the review were marked `code_grade: pass` from SC-02's narrow receipt, the digest gate would refuse that claim. Grader records (cyclomatic / cognitive / ABC; driver):

   | File · line · function | Metrics | Grade · driver |
   |---|---|---|
   | `feat2581-cleanpin.py:213` · `Derived.__init__` | 21 / 10 / 34.1 | 1 · cyclomatic |
   | `feat2581-cleanpin.py:274` · `Derived.hits` | 9 / 4 / 15.9 | 3 · cyclomatic |
   | `feat2581-cleanpin.py:283` · `Derived.d02` | 10 / 14 / 17.4 | 3 · cyclomatic + cognitive |
   | `feat2581-cleanpin.py:352` · `main` | 56 / 18 / 156.6 | 1 · cyclomatic + ABC |
   | `feat2581-grade-assert.py:59` · `main` | 22 / 10 / 49.8 | 1 · cyclomatic + ABC |
   | `feat2581-ledger-driver.py:66` · `suite` | 5 / 10 / 25.5 | 3 · cognitive + ABC |
   | `feat2581-ledger-driver.py:102` · `main` | 11 / 4 / 45.8 | 1 · ABC |

   Also grade 2 (nonblocking in isolation): `Measured.check_shapes` and `Derived.bodies` in cleanpin, replay `main`, and recorder `_intercept_cli` and `_install_subprocess_hooks.communicate`. The seven high records determine `code_grade: fail`.
2. **High · substance · T-03 — an empty operator ruling passes.** `notes/receipt-scripts/feat2581-cleanpin.py:321–323` and its matching signed verify predicate (`plan.yaml:502,514`) coerce metadata via `str(...)`. The literal verification leg still prints `T-03 receipts PASS` if `audit:stdout` keeps its ID but `by`, `date`, and `reason` are all JSON null (`str(None)` is nonempty). That can publish a measured difference without a recorded operator ruling. Require nonblank strings in both predicates; keep the existing rulings. This probe altered only an in-memory view of a Git blob, not any settled ruling or measured artifact.

## Targeted verification

Ran the literal T-03 block: the receipt recomputation selected `review_sha=62da4501…` and passed; the direct audit leg on identical pinned source and classification passed. A new `audit:stderr` measurement was rejected at divergence-set equality, and deleting `audit:stdout`'s ruling was rejected at ruling lookup. AST-extracted pinned bodies matched for 33 argparse help/error cases across all 14 verbs; normal and refused close-run plans matched exact argv for `feature-record.py`, `validate-digest.py`, and `plan-merge.py`, including optional grade, station, judgement, and Unicode digest path. `spend_for` matched overlapping intervals, token filtering and regate fallback preference (20 total minutes, 8 rework, 14 tokens, 1 round); `_problems_for_doc` matched 42 ordered findings on unknown/missing fields and a blank run agent. Those probes did not execute writes or child stages. Did not rerun T-01's smoke/tests, the full corpus, or enforcement through an agent workflow; the committed receipts are their evidence. No open questions.
