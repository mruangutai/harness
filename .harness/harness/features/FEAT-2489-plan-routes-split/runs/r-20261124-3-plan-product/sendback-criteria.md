# Send-back criteria — apply c2 (written before dispatch, P-05)

Send pm's apply back if any holds:

1. SC-02's delta rule for diagnostics enumerates producers (`_exemption_finding`, `_row_label`, `_unmigrated_row_findings`) as the rule instead of stating the class (any diagnostic, either stream, any mode, formatted from a rewritten field: row `file`/`id`, re-keyed T07 key, scanned_files entry).
2. The class allows anything beyond the rewritten value (text otherwise identical; multiset position and order unchanged).
3. T-02's checker / equivalence-final receipt does not sample a perturbed finding naming a relocated row, or its comparison is a loosened diff instead of a stated old-path→new-path mapping for exactly the relocated identities.
4. BRIEF lacks the disclosed departure (beside complete-install) stating it derives from sanctioned deltas 1–3, for the signer to accept or refuse.
5. T-01 verify still accepts a receipt by prefix alone: must check recorded HEAD is ancestor of HEAD AND `git rev-parse <HEAD>:tests/integration/test-check-plan-routes.py` == recorded BLOB; never compare the live file. Recording must occur after T-01's test change is committed (else blob mismatch by construction).
6. Ruled scope touched: SC numbering, new task, module shape, CLI/tests.yml, approval status, complete-install gap.
7. `plan-merge.py check` failures > 0, or PF dispositions not reported per id.
