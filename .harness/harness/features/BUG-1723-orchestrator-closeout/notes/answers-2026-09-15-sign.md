# Operator decision — BUG-1723 signature

Signed by Main on the operator's blanket authorization in session 2026-09-15 ("do all of them from plan (or patch) to ship"; ask answered: "Sign on my authorization"). Rework ruling: propose-rework default. All five panel findings resolved by pm at apply; none overruled. SC-05 is `verify: uat` and is gated at the first post-ship plan mission, not at this ship.

## Re-signature after validate c2 (2026-09-16)

Validate c2 BLOCKED on two questions; both are Main's to answer, not the operator's:

- **Q2 (DEC-159 scope).** The BUG-1723 mechanism clause in DEC-159 was written by Main during T-03 and still said "a note on one at a terminal station" after validate c0 struck that exemption from the code. Reconciling a sentence Main wrote with the contract Main fixed is the cutover, not new scope. T-03's `files` now declares DECISIONS.md and DECISIONS-INDEX.md (amended via `plan-merge.py amend`, which reset approval); re-signed here on the operator's blanket authorization for this session. Nothing about the SCs, the task set, or the decisions changed.
- **Q1 (verifier checkout).** The qa verifier invoked `.agents/skills/harness/bin/run-unit-tests.py` as a shell script from the gitignored symlink path and read exit 2 as a matrix failure. Both matrices pass with `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit|integration` at the pin and at HEAD; the exact-pin contract is unchanged and the caller error is noted in the fix note.
