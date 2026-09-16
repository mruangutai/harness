# Operator decision — BUG-1723 signature

Signed by Main on the operator's blanket authorization in session 2026-09-15 ("do all of them from plan (or patch) to ship"; ask answered: "Sign on my authorization"). Rework ruling: propose-rework default. All five panel findings resolved by pm at apply; none overruled. SC-05 is `verify: uat` and is gated at the first post-ship plan mission, not at this ship.

## Re-signature after validate c2 (2026-09-16)

Validate c2 BLOCKED on two questions; both are Main's to answer, not the operator's:

- **Q2 (DEC-159 scope).** The BUG-1723 mechanism clause in DEC-159 was written by Main during T-03 and still said "a note on one at a terminal station" after validate c0 struck that exemption from the code. Reconciling a sentence Main wrote with the contract Main fixed is the cutover, not new scope. T-03's `files` now declares DECISIONS.md and DECISIONS-INDEX.md (amended via `plan-merge.py amend`, which reset approval); re-signed here on the operator's blanket authorization for this session. Nothing about the SCs, the task set, or the decisions changed.
- **Q1 (verifier checkout).** The qa verifier invoked `.agents/skills/harness/bin/run-unit-tests.py` as a shell script from the gitignored symlink path and read exit 2 as a matrix failure. Both matrices pass with `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit|integration` at the pin and at HEAD; the exact-pin contract is unchanged and the caller error is noted in the fix note.

## Rework ruling: one further round (2026-09-16)

`spend` reads rework_rounds 2 / 60 min of the 2 / 90 ruling after fix-c2. c2 was BLOCKED on questions, not FAILed on a gate, and both answers were facts already on disk. Main authorizes exactly one more validate round (fix-c3-validator) on the operator's blanket authorization for this session and records it as a `continue` judgement; a FAIL there returns `awaiting_user` for a real ruling.

## Validate c3 ruling: ship (2026-09-16)

At the pin `69992277`: code-reviewer PASS (both stages, full feature range), security-reviewer PASS, ui-reviewer self-scoped out, goal-check PASS (SC-01..SC-04 met; SC-05 is the post-ship measurement by design), qa matrix PASS in a detached checkout at the exact pin (unit 40 files, integration 72 files). The run is recorded BLOCKED for one reason: `validate-digest.py`'s #919 re-verification spawns `bash run-unit-tests.py` — a Python file since #1674 — and reads its exit 2 as a red matrix. That is a defect in the gate hook on `origin/main`, outside this feature's declared surface, filed as #1756 (DEC-174 main-session-direct). The evidence the gate exists to demand is on disk; Main rules the validate outcome PASS on that evidence and ships. The run record stays BLOCKED as the orchestrator wrote it — history stays as recorded (DEC-227).

## Re-signature after the CI corpus gate (2026-09-16)

PR #1757's `integration` check runs `check-state.py` over the whole corpus, and INV-43 — as validated, "a violation at every station" — reddened three landed records (BUG-1723's own first validate, two on BUG-285-canonical-reader), so the feature could not merge under its own invariant. Those records cannot be re-recorded (DEC-227). The fix is BUG-1071's rule for INV-32, applied to INV-43: a per-project `seam_era_start` in harness.json (template null; this project `2026-09-17`, the first day the seam is graded on `main`), before which a retrospective succession is a note saying what it would fail. The boundary is by DATE, never by station — the terminal-note exemption validate c0 struck stays struck. T-02's `files` now declare harness.json, the template, and test-check-state-records.py; re-signed on the operator's blanket authorization for this session. SCs, task set and decisions unchanged.
