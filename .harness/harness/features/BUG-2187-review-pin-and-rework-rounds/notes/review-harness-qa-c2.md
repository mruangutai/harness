# QA correction — BUG-2187 T-01 @ 1b35414b (run 2026-11-21-02-validate-validator, c2)

BLUF: This note corrects `review-harness-qa-c1.md`, which stays unmodified. **Terminal verdict is ESCALATE, not PASS.**
The gate's independent run-unit-tests.py hook exited 1 after my c0 measured exit 0; I could not reconcile it and
no failing test or path is available to me. c0 and c1 are unchanged. No new tests or probes ran.

## Corrections to c1
1. Verdict: c1 reads as PASS with no probes. The terminal yield was ESCALATE, `suite: fail`, `failures: 1`,
   `matrix_ok: true`, because of the contradiction below. Read ESCALATE as authoritative.
2. Kinds: c1 relabelled c0's kinds to test-gap/evidence-form against the preservation instruction. The c0 kinds stand.
   Severities are unchanged from c1.

| # | kind (c0, stands) | severity | location | gate effect |
|---|---|---|---|---|
| 1 | substance | med | tests/integration/test-check-state-records.py inv33 e-g; feature_record.py:84-89 (bytes fallback, M-C/M-L) | advisory |
| 2 | substance | low | inv33.g; feature_record.py:71-72 (task-nested status, M-E) | advisory |
| 3 | substance (pre-existing) | low | feature_record.py:197 (three silences and placeholder have no case) | advisory |
| 4 | substance | med | PinReviewTest; feature-record.py:607-619 (field preservation, shared writer, M-P/M-Q/M-R) | advisory |
| 5a | substance | low | SpendTest; feature-record.py:673 (naive/aware timestamp guard, M-N2) | advisory |
| 5b | form | none | receipts/red-inv33.txt (labels without stderr; remedied by c0 base-red reproduction) | advisory, remedied |

Item 5 in c0 ("form/advisory") was two defects: 5a is substance, 5b is form. must_fix: none (reasoning in c1).

## Unreconciled contradiction (blocking)
- c0 measured at the pin with `env -u HARNESS_AGENT_TYPE`: `run-unit-tests.py --kind unit` exit 0 (61 files) and `--kind integration` exit 0 (87 files, ALL PASSED).
- The gate's independent run of run-unit-tests.py exited 1. The only text I received was its tail: the integration kind, 87 files, `ALL PASSED`, last `PASS test-gh-sync-open.py`.
  It named no failing kind, file or test. I hold no raw output path and do not know the hook's environment (`HARNESS_AGENT_TYPE` set or not: repo G-07; also G-05, G-11).
- I did not rerun anything (dispatch forbids execution), so I cannot attribute the exit-1. Per O-01 it is not graded PASS.
- Successor action: obtain the gate's full raw output and environment, or authorise a rerun with `env -u HARNESS_AGENT_TYPE`, and record which kind/file failed.

## Principles applied
Honest record (rule 15): the c1 artifact is not rewritten; this note corrects it and records the failed gate as failed (O-01, O-09).
