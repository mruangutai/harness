# FEAT-70 — red-first receipts (SC-01, SC-02 and SC-03 fail-first)

## SC-03 — record-amendments after a block-scalar splice (the crash)
Red committed first at 937b1242 (`case_feat70_record_amendments_after_a_block_scalar_splice`, a
two-entry digest whose first entry GROWS a `|` body from one line to six; the plan's `decisions: []`
tail gives the scan no same-indent terminator). Against the baseline implementation the case fails
4 of 6 checks with an IndexError traceback from `_item_range`; plan and ledger bytes are unchanged
(the atomicity half already held). At the pin all 6 checks pass: both fields land, the block keeps
its `|` form with the longer body, two `amendment` judgements in digest order, ledger valid.

Cross-run receipts (the PIN's case and fixture against each implementation, `PLAN_MERGE_BIN`
pointed at the checkout) are in `clean-pin-byte-receipts.generated.md` § SC-03: baseline exit 1,
stderr ends `IndexError: list index out of range`, plan sha 63b5807e unchanged, ledger sha a3324d79
unchanged; pin exit 0, plan sha → 208e23b6, ledger sha → 361c43ab.

The fix is the `_render_field` return-shape contract in `plan_merge/text.py` (one element per
physical line, was one joined element); `_proposal_field_lines`' plain-scalar fallback follows the
same contract. This intended behaviour difference does not enter the SC-02 identity ledger (the
case's invocations are dropped from the pin side before alignment).

## SC-01 — the file-wide grade assertion is RED at the baseline and GREEN at the pin
`feat70-grade-assert.py 35b42d2a… 9e531b34… --tree 9e531b34…` → exit 1: no package, twelve functions
below 4, none at their owners. Without `--tree` (the pin) → exit 0. Both transcripts are in the
generated receipt.

## SC-02 — fail-first is the baseline-versus-pin comparison itself
The pin side does not exist before the implementation; the two ledgers and two scratch corpora ARE
the comparison. The recorder was proven to discriminate during development: before the concurrency
case was serialised it reported 40 differing records (the lock race's winner), and before the shim's
clock was frozen it reported `reset_at` differing by the seconds between executions — both are
listed in `build-divergences.md` as superseded executions.
