# FEAT-2398 simplify pass (DEC-195)

Scope: `9eb07b4f..8167aab2`, four parallel read-only `reviewer` readers, one angle each. Under
DEC-174 (main-session-direct) the main session is the build side and applied the findings itself.
Suites re-ran green after the apply (full `test-validate-digest.py`, shadows, config readers,
reader audit); no assertion was deleted or weakened.

| Angle | Finding | Disposition |
|---|---|---|
| reuse | `_qa_pins`/`_qa_review_commit` restate `_review_binding`/`_pins_agree` | Skipped: the shared primitives (`resolve_reviewed_commit`, `_placeholder`) are reused; T-01's intent bars reusing `_review_binding` unchanged (different root and diagnostics), and `_pins_agree`'s bool would drop which pin failed to resolve. |
| reuse | the pinned blob read duplicates `code_grade._git_show` | Applied: `_qa_pinned_policy` calls `_git_show` (no change to `code_grade.py`), separating "no such file at that commit" from a git refusal. |
| reuse | the readers-test fixture restates `git_support` | Applied: `init_repo`/`commit_all`. |
| efficiency | identical review_sha and dispatch pin resolve twice | Skipped: one `git rev-parse` (milliseconds) per QA return; a dedupe branch costs more reading than it saves. |
| efficiency | `_hook_registered_feature` runs twice per QA return | Applied: `_hook_validate` resolves it once for the artifact check and QA's policy. |
| altitude | receipt sequencing (`qa_receipts_follow`) leaks into `validate()` | Applied: `validate()` always reports the policy refusal (a `_QaPolicyRefusal`); the hook's `_receipt_owned` leaves it to the #919 receipt check only when it is the sole error on an unconditional PASS. |
| simplification | positional `qa` tuple | Applied: `_QaSeam(feature_dir, review_pin)`. |
| simplification | two diagnostics for one misconfigured-verdict fault | Applied: the pinned-policy error owns a misconfigured-class kind; the generic PASS/FAIL rule fires only when the policy check found nothing. |
| simplification | one-letter fixture pin labels | Applied: pins named for their `always` floor. |
| simplification | `_kp_commit` passes straight through to `_rx_commit` | Applied: removed. |
