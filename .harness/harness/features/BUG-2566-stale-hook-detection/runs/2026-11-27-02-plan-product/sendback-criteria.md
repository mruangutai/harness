# Send-back criteria — run 2026-11-27-02-plan-product (written before any return)

## answers (pm)
Send back if any holds:
- D-02, SC-01, SC-02, T-01 or T-02 still fingerprints `schemas/digest` / `DIGEST_SCHEMA_DIR`, or still lists `digest-schema.ts` as a fingerprint entry (Q-02, Q-03).
- `.omp/agents` added to the fingerprint (Q-02 says do not).
- SC-01 still carries cases for digest-schema.ts present/absent/appearing, or for schema-file add/modify/remove.
- D-02 / SC-02 / T-02 still refuse a governed child's `VERDICT: BLOCKED` yield on a stale process (Q-04 carve-out not taken), or the carve-out is broader than a BLOCKED yield.
- `decisions_affected` DEC-204 row still claims the exception is removed; the DEC-204/DEC-100 rows are not re-derived against the carve-out.
- D-04 merge-order and per-file naming fixes from run 01 silently dropped (per-file naming may shrink with the fingerprint set, but must remain for whatever files are fingerprinted).
- Edits not made through plan-merge verbs, or `plan-merge.py check` not exit 0, or `approval:` touched.

## scope (code-reviewer, bounded)
Send back only for an invalid return: reads beyond T-01/T-02 (plus the D-/SC- text they cite) presented as findings, findings without `kind`/severity, or no per-PF verdict on the run-01 findings it was asked to grade.

## apply (pm)
Send back if: a form finding left unfixed; a substance finding edited into the plan instead of carried to the digest; `record-panel --cycle 2` or `check` not exit 0; a c1 finding marked `resolved` without the reader's confirming verdict.
