# FEAT-69 — clean-checkout implementation-pin receipts (reviewed record)

The generated file `notes/clean-pin-byte-receipts.generated.md` is the measurement, committed exactly as `receipt-scripts/feat69-cleanpin.py` wrote it. This file is the operator-facing reading of it and adds nothing the generated file does not carry.

## Identity and chronology

- Implementation pin: `db488aa7c78e392c788bd5839a43ebf4ba562ea1` — the last build commit (T-01 `89c7020e`, T-03 `76723e90`, T-02 `3975a8bf`, simplify pass `264f534a`, amendment 1 `cebe2d69`, amendment 1b `db488aa7`).
- Baseline: `a726bad8f74d23e6c1f07409383bb88d1da8fbcf` — `origin/main` when the worktree was cut (amendment 1 corrected the signed plan's `e6f8493b`, which predates INV-49).
- Checkouts: `.claude/worktrees/harness/feat69-cleanpin-db488aa7` and `.claude/worktrees/harness/feat69-base-a726bad8`, both created detached by the script, both asserted at their SHA with `git status --porcelain` empty before any measurement.
- Chronology: the committed generated receipt is T-04's verify execution, measurements 2026-09-28T20:52:45Z–20:55:06Z (a first execution at 20:48:57Z–20:51:18Z over the same pin and baseline is superseded; its one extra difference, D-01, is ledgered); the receipt scripts, the generated receipt, this file, `red-first-receipts.md` and `build-divergences.md` were committed together AFTER the pin, in the commit that follows it. Nothing in the pin references any receipt.

## Reproduction, exactly as run

From the worktree root `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-69-long-file-check-state-package`:

```
python3 .harness/harness/features/FEAT-69-long-file-check-state-package/notes/receipt-scripts/feat69-cleanpin.py db488aa7 a726bad8
```

That one command creates or reuses both detached checkouts, runs `feat69-baseline.py <checkout> /tmp/feat69-<label>-<sha8>.json` once in each (every measurement executed exactly once per checkout; every byte, sha1, diff line and verdict in the generated file derives from those two JSONs), runs `feat69-grade-assert.py` in the pin checkout (green, with the baseline JSON for moved/new classification) and in the baseline checkout (red), and writes the generated receipt.

## What was measured (SC-02), and the result

Thirteen measurements per checkout: the full-table `check-state.py` run over every feature; `check-state.py --list`; the nine owning suites (`test-check-state`, `-entry`, `-plans`, `-records`, `-handoff`, `-worktrees`, `-inv26`, `-feat59`, `-table`); clean-tree `feat62_findings`; clean-tree `consolidation_findings` (`check-plan-routes.py --consolidation-audit`). Comparison after the one normalisation (each checkout's absolute root → `<checkout>`).

- Identical: 12 of 13 — `--list`, all nine suites, both lock runs — exit status, stdout bytes and stderr bytes.
- Not identical: `full_table` (exit 1 → 1). Five differing lines, all quoted verbatim in the generated file and ruled in `build-divergences.md`: D-02 four INV-32 notes for FEAT-69's own resolved panel findings (the record exists only at the pin); D-03 one INV-8 note for FEAT-69's gitignored `plan-product` run directory. (D-01, a foreign worktree's dirty clause, appeared only in the superseded first execution.) None is produced by the split.

## SC-01

Green at the pin: 295 functions over the entry plus twelve package files, 119 at 5 and 176 at 4, none below; the four named functions present and at 4; 287 moved functions with grade kept or raised; 8 new functions at 4–5. Red at the baseline: no package, four functions below 4. Verbatim outputs in `red-first-receipts.md`.
