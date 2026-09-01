# Handoff — build phase — FEAT-41-one-station-vocabulary

## Next

Re-review cycle 1 against the NEW `review_sha`, on a branch REBASED onto 9f2a070 (0 behind).
All five of cycle 0's must-fix findings are fixed, each with its own commit and receipt in
`787c7fa..8fa2d04`. Zero gated HIGH code-grade records; six grade-2 records need written reasons,
not refactors. Inputs: `plan.yaml` (16 tasks, D-01..D-16), `BRIEF.md`, and the fix commits.

THE REBASE CHANGED THE ANSWER TO Q2 AND TO T-18 — read D-16 before reviewing either. FEAT-45 had
already fixed Q2 upstream, better, so T-18 is STRUCK and its station is `abandoned`. My duplicate
mechanism is deleted; validate-digest.py is byte-identical to origin/main.

Cycle 0's two verdict items are CLOSED by the operator: T-15's lane deviation is ratified in D-15,
and T-10's verify-line defect is recorded rather than rewritten because the plan format is
add-only. Do not re-open either; check that the records say what happened.

## Trust

- unit exit 0, 505 PASS; integration exit 0, 816 PASS — verified-at 8fa2d04, both kinds run SERIALLY at the new base
- Gated HIGH code-grade records: 0, against merge-base 9f2a070, the same the reviewer will use — verified-at 8fa2d04
- T-14's invariant is INV-33 now, not 32: FEAT-45 shipped its own INV-32 first, so it owns the number; both suites' cases pass side by side — verified-at 8fa2d04
- FEAT-45's records were migrated by THIS feature, not by FEAT-45: it shipped after T-04/T-07 ran, so its plan carried no station and its feature.json still carried `status` — verified-at 8fa2d04
- The 33 INV-32 lines seen mid-rebase were a STALE BASE, not a defect here; BUG-1071's era guard resolves them — verified-at 8fa2d04
- Q2 is fixed UPSTREAM: origin/main's `_hook_feature_dir` resolves the worktree via inflight_registry and SEC-01 bound to fb07ed6 when driven against the real layout — verified-at 8fa2d04
- F-01's fix is cross-file: the test reads the sweep's gate literals OUT of post-merge-sweep.sh rather than retyping them — verified-at 787c7fa
- F-02 had FIVE failures in three classes, not the one reported; `#845 owner` and `yes` PARSE FINE and still corrupt the value, so the check compares values — verified-at 8c2972e
- F-02's two layers are independent: mutating the escaping away leaves the round-trip check refusing with the plan byte-identical — verified-at 8c2972e
- F-03's fix covers the TEXT fallback too; fixing only the token scan moved the evasion one unbalanced quote away — verified-at dee7225
- F-04's realpath half does NOT reproduce: `./`, `..`, doubled slash, absolute and a SYMLINKED feature dir are all already denied — verified-at 6eda94d
- `_commit_terminal_station` was printing a Python LIST at the operator (`['fatal: ...']`); rendered to confirm before fixing — verified-at 9bdbe91
- INV-32 reports THIS feature's own review_sha until the pin moves; that is the invariant working, not a defect — verified-at a1dc932
- T-14's four verify greps need `-F` or escaped parens under `pi-uu-grep 0.2.0`, which reads the pattern as ERE — verified-at a1dc932

## Dead Ends

- Do NOT replace shape-matching WITH realpath in check-domain.sh; shape is stronger for `./`, `..`, doubled slashes, absolute paths and a symlinked feature DIRECTORY. This entry USED to say "do not re-fix F-04's realpath half" full stop, and cycle 1's panel found the hole that wording talked past: a symlinked FILE with an innocent name matched no pattern at all. Closed by ADDING resolved candidates (H-01), not by substituting resolution
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
