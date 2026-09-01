# UI Review — BUG-1080 inv6-plan-phase-runs (operator-message remit)

Reviewed at pinned `review_sha` **a2fb6c0b** (`78519029` is worktree HEAD — a2fb6c0b is
its immediate parent per `git log`, and `git diff 9f2a0702 a2fb6c0b` is the object diffed
below; content is unaffected by the one extra commit ahead). Base `9f2a0702`. Ran from
`.claude/worktrees/harness/BUG-1080-inv6-plan-phase-runs` throughout — confirmed via
`wc -l test-check-state.py` = 3526, matching the worktree figure the dispatch names (the
main checkout's stale 3396-line copy was never read).

## Scope measurement

`git diff --stat 9f2a0702 a2fb6c0b` touches exactly the three files the dispatch names:
`check-state.sh` (+28/-3), `feature-schema.json` (+3/-1), `test-check-state.py`
(+132/-1). Extension census on `git diff --name-only` against
`html|css|scss|tsx|jsx|vue|svelte|less`: **zero matches** — no rendered UI. No
`DESIGN.md` exists anywhere under this feature's directory; `notes/` holds only
`handoff-plan.md` and `handoff-build.md`; no `mockups/` or `prototypes/` directory
exists. Per repo-tier Expertise P-01, scope reduces to the one adjacent surface the
dispatch hands down explicitly: the INV-6 violation message, an operator-facing CLI
diagnostic.

## The candidate message

`check-state.sh:457-460` (verified live in the diffed file):

> `{feat}: a validator run reviewed code but review_sha is not pinned — reviewers would
> diff HEAD (the GAP-7 failure).`

## Finding — MED, non-gating: the message names the fact, not the remedy this bug creates

The message states the trigger (an unpinned `review_sha` on a code-reviewing run) and the
consequence (GAP-7), but names no remedy. For an operator who does not already know this
feature's own vocabulary, the only actionable-sounding clause is "review_sha is not
pinned" — which reads as "go pin it." That is the wrong instruction for exactly the case
BUG-1080 exists to legalize: a plan-phase validator run has no commit to pin (DEC-207),
so the correct fix is setting `code_grade: n_a` on that run entry, not pinning anything.
The message gives no pointer to that key at all.

**This is not a hypothetical gap — it is the identical shape BUG-1071's panel raised
against INV-32's `panel_era_start` message, and this same file now demonstrates the
opposite of what it teaches.** `check-state.sh:286-297` (the INV-32 no-panel-result
message, unchanged by this diff) carries an explicit comment on exactly this point:
*"WITHOUT this sentence its cause is invisible... Naming the key here is what makes the
residual self-diagnosing rather than merely reversible"* — and its message text follows
through: *"...set harness.json `panel_era_start` to the date the panel became available
here instead of recording one."* That is the house convention this file itself states and
follows one invariant away. INV-6's new message does not follow it: it names neither
`code_grade` nor `n_a` anywhere.

**Severity, calibrated against this same feature's own precedent.** BUG-1071's UI review
(`notes/review-harness-ui-reviewer-bug1071.md`) rated an analogous "names the defect, not
the remedy" gap on INV-32's approval-date message at **LOW**, non-gating — that gap had an
obvious, guessable fix ("add a date"). This one rates higher: `code_grade: n_a` is not
guessable prose, it is a schema key introduced by this very diff (`feature-schema.json:61`)
that an operator has no way to discover from the message text, and the message's only
actionable-sounding clause ("pin review_sha") is not available to the exact case (a
plan-phase run) the message is now reachable from. That is closer to cycle 1's **MED**
rating for BUG-1071's F1 remedy ("the file has a documented, consistently-followed
convention for exactly this situation") than to cycle 0's LOW.

**Why non-gating:** the message does not corrupt state, does not misreport which
invariant fired, and the `note`/`bad` framing already signals a hard block rather than a
silent pass — an operator who hits this will investigate and can find `code_grade: n_a`
by reading `feature-schema.json` or this bug's own commit message, just with friction the
sibling INV-32 convention shows is avoidable. Confirmed no test asserts full message text
beyond the fixed substring `"review_sha is not pinned"` (`test-check-state.py:3301`,
`_PIN_MSG`) — adding the remedy clause would not break any of the six new `case_inv6_*`
cases.

## Out of remit, noted only

Reachability of `code_grade` (whether any producer actually writes it into a run entry)
is a code-review/architecture question, not a UI one — `validate-digest.py`'s reviewer
DIGEST already carries a `code_grade` field (`code_grade: n_a` is a legal DIGEST value
per `test-validate-digest.py:1863`), which is the plausible write path, but confirming an
end-to-end producer exists is outside this lens. Flagging for whichever peer covers gate
wiring (per Expertise O-02).

## Verdict rationale

No `must_fix`. One MED, non-gating finding on operator-diagnostic wording.
`severity_max: med` → PASS.

## Open question

None blocking. Adding `— set \`code_grade: n_a\` on this run if it graded a specification,
not code` (or equivalent) to the INV-6 message is a one-line, reversible fix that brings
it into line with this same file's own INV-32 convention — noted as a take-it-or-leave-it
improvement for whoever next touches this block.
