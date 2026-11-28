# Send-back criteria — draft step (written before dispatch, P-05)

Send back the draft if any of these holds:
1. Any task lacks `execution_mode: main-session-direct`.
2. Fingerprint scope differs from exactly: `.omp/extensions/harness-hooks.ts`, `.omp/extensions/digest-schema.ts`, the digest schema directory.
3. Any warn-and-continue / opt-out path on mismatch, or the refusal is not one actionable "restart omp" line.
4. No SC pins per-call cost (cheapness) with a verify method.
5. Python gate scripts placed in scope.
6. Plan does not address: (a) which on-disk path is fingerprinted (the path the module was loaded from, not a worktree copy); (b) a session whose own edit changes the fingerprinted files (main-session-direct build of this very feature) — what happens to that session; (c) orthogonality with BUG-2565 (deletes per-call schema injection) — schema dir still fingerprinted regardless.
7. `plan-merge.py check` not run / not exit 0; `panel:` or `approval:` written.
