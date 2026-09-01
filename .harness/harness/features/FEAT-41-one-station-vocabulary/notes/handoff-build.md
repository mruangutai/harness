# Handoff — build phase — FEAT-41-one-station-vocabulary

## Next

Re-review cycle 1 against the NEW `review_sha`. All five of cycle 0's must-fix findings are
fixed, each with its own commit and receipt in `787c7fa..9bdbe91`. Zero gated HIGH code-grade
records remain; six grade-2 records stand and need written reasons, not refactors. Inputs:
`plan.yaml` (15 tasks, D-01..D-15), `BRIEF.md`, and the fix commits.

Cycle 0's two verdict items are CLOSED, both by the operator: T-15's lane deviation is ratified
in D-15, and T-10's verify-line defect is recorded rather than rewritten because the plan format
is add-only. Do not re-open either; check that the records say what happened.

## Trust

- unit exit 0, 493 PASS; integration exit 0, 816 PASS — verified-at 9bdbe91, both kinds run SERIALLY after every fix
- Gated HIGH code-grade records: 0, measured against the same merge-base the reviewer uses — verified-at 9bdbe91
- F-01's fix is cross-file: the test reads the sweep's gate literals OUT of post-merge-sweep.sh rather than retyping them — verified-at 787c7fa
- F-02 had FIVE failures in three classes, not the one reported; `#845 owner` and `yes` PARSE FINE and still corrupt the value, so the check compares values — verified-at 8c2972e
- F-02's two layers are independent: mutating the escaping away leaves the round-trip check refusing with the plan byte-identical — verified-at 8c2972e
- F-03's fix covers the TEXT fallback too; fixing only the token scan moved the evasion one unbalanced quote away — verified-at dee7225
- F-04's realpath half does NOT reproduce: `./`, `..`, doubled slash, absolute and a SYMLINKED feature dir are all already denied — verified-at 6eda94d
- `_commit_terminal_station` was printing a Python LIST at the operator (`['fatal: ...']`); rendered to confirm before fixing — verified-at 9bdbe91
- INV-32 reports THIS feature's own review_sha until the pin moves; that is the invariant working, not a defect — verified-at a1dc932
- T-14's four verify greps need `-F` or escaped parens under `pi-uu-grep 0.2.0`, which reads the pattern as ERE — verified-at a1dc932

## Dead Ends

- Do NOT re-fix F-04's realpath half; the pattern matches path SHAPE, which is stronger than realpath, and the measurement is in the test
- Do NOT reconcile `_record_station` and `_commit_terminal_station` to use the same words: written-nowhere and written-but-uncommitted have OPPOSITE correct answers, both asserted
- Do NOT exempt `--date` from sign-approval's escaping; a type-aware exemption is a hole in the check that closes F-02
- Do NOT add a `required` column to plan-merge.py's VERBS table; if a verb needs an optional argument it gets its own registration
- Do NOT re-run the one-time board pass; it is idempotent but it WRITES, and a run against a moved plan would move cards the panel has not seen
- Do NOT touch `review_sha` in any other feature.json — T-14's intent forbids it, and 19 directories carry honestly-stale-looking pins from layout history
- Do NOT edit `plan.yaml` with Write or Edit; T-09 closed that route for every author including the main session — use `plan-merge.py` verbs
- Do NOT treat `--kind unit` as the suite: it covers 29 of 56 scripts and that gap hid T-01's breakage for four tasks
- Do NOT quote a retired station spelling in a comment — SC-02 greps for it, and this feature tripped that four times

## Working Set

- .harness/harness/features/FEAT-41-one-station-vocabulary/plan.yaml
- .harness/harness/features/FEAT-41-one-station-vocabulary/BRIEF.md
- .harness/logs/2026-08-31.md
- .claude/skills/harness/bin/check-domain.sh
- .claude/skills/harness/bin/check-state.sh
