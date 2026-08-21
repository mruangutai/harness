# M-15. T-08's lane: two corrections to the R-4 analysis, and why the answer is the operator's

The architecture review's S-B reader ruled T-08 correctly `team`-laned and said it would sign that.
Its conclusion may well be right, but two of its supporting claims do not survive checking, and both
cut the same way — toward the operator's eye rather than away from it.

## Correction 1. DEC-174 amendment 4 does not mention `run-unit-tests.sh` at all

The receipt states that am.4 "discussed `run-unit-tests.sh` by name and did not add it to the
enumerated five", and recommends an amendment recording that omission as **deliberate**.

Measured: `awk` over the whole of amendment 4 returns **zero** occurrences of `run-unit-tests`. The
three mentions in `DECISIONS.md` are at `:4662`, `:5422` and `:5617`, none of them in am.4.

This matters beyond pedantry. Writing "the omission was deliberate" into `DECISIONS.md` would record
a consideration that never happened — PRINCIPLES rule 15, never falsify the record. The honest
amendment, if one is written, says the question was **not reached** in am.4 and is settled now.

## Correction 2. DEC-174's own evidence paragraph lists it among the gates

`DECISIONS.md:4662`, inside DEC-174's opening evidence: *"Every gate was green —
`run-unit-tests.sh`, `check-docs.sh`, `check-state.sh`, `gen-decisions-index.py --check` — while:"*
and then the three failures self-hosting missed.

So the entry that creates the carve-out names this script as one of the gates whose greenness proved
nothing. The carve-out TABLE's four parenthetical examples exclude it. The text is therefore
genuinely ambiguous, not "genuinely outside on the evidence".

## The claim that actually decides it, and it is false for this repository

The receipt accepts a residual risk on the grounds that it is *"mitigated the same way any
team-laned code is — review, a human reading the diff at merge, same protection every other `team`
task gets."*

`DECISIONS.md:5419-5428` says that protection does not exist here, and says so as a measurement:

- `required_pull_request_reviews` on `main` is **null** — one required context, `enforce_admins` on,
  **zero required reviewers**.
- A CODEOWNERS file covering `/.github/` **and `run-unit-tests.sh`** is committed and **deliberately
  not enforced**, because `require_code_owner_reviews` would make every PR permanently unmergeable:
  sole collaborator, GitHub forbids self-approval, `enforce_admins: true` removes the bypass.
- The repository's own history: **52 reviews, every one COMMENTED, none APPROVED.**

A signed decision has already identified `run-unit-tests.sh` as a surface warranting owner review and
recorded that nothing requires one. So the mitigation the ruling leans on is the one control this
repository provably lacks.

## What follows

Not a `must_fix` and not mine to decide — this is a lane question resting on how much the operator
trusts an unenforced control over the script that runs every gate's test.

- **Keep T-08 `team`** and accept, knowingly, that a team agent edits the test runner and
  `harness.json`'s `test_kinds` with no enforced review. The edit is a two-entry array append plus
  two `detect` entries, and T-08's own verify asserts both new files actually run.
- **Or make T-08 `main-session-direct`**, at the cost the reader named honestly: every future feature
  adding a `bin/test-*.py` loses team execution for a mechanical append, and six shipped features'
  worth of `team`-laned registrations read retroactively as violations.

I recommend keeping it `team`, because T-08's verify is self-discriminating — it requires
`PASS test-feature-worktree.py` and `PASS test-expertise-merge.py` in the runner's own output, so a
registration that silently does nothing fails the task. That is a stronger control than the review
that does not exist. But the operator should choose it knowing the review argument is unavailable.
