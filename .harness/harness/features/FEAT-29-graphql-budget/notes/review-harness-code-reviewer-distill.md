# Distillation — harness-code-reviewer — FEAT-29-graphql-budget

## Source

No observations log exists for this agent this feature (checked: `.harness/harness/features/FEAT-29-graphql-budget/observations/` has no `harness-code-reviewer.md`). Source is my own two review artifacts
(`notes/review-harness-code-reviewer-sc05-c472a02.md`, its `-c2` twin) plus, to adjudicate candidate
1's factual premise, `runs/2026-08-19-09-validator/digest.md` (read-only, not my domain, not written to).

## Candidate adjudication

**Accepted — Outcomes, added O-08.** Candidate 2 (send-back mechanism). Verified against
`digest.md:96-103`: the validator-lead explicitly said holding at `high` was acceptable and would
route the cycle; I re-graded to `low` on my own sharper trace and wrote it into a new `-c2` file,
leaving `-c472a02.md` (cycle 1) unmodified — confirmed by file listing, both files present and
distinct. Durable, general (true in any repo that separates review cycles into artifacts), not
covered by an existing entry.

**Accepted — Outcomes, added O-09.** Candidate 3 (refuting a proposed mutation). Verified against
`digest.md:27,86-92`: the validator-lead proposed a mutation to `measured()`; my `-c2` artifact
(lines 25-33) found the sharper refutation — the OFF branch is `yield m; return` with no
`try/finally`, so `record()` is never reached on that path regardless of the proposed change,
making the proposed mutant equivalent rather than a live gap. General technique (check reachability
before trusting a mutation's survive/kill result), not duplicated by O-01/O-05 which cover proof
standards for a mutation you originate, not one you're asked to evaluate.

**Rejected — candidate 1** ("cycle-1 `high` rested on a pre-named false premise"). Checked against
both sources and it does not hold as framed. My cycle-1 artifact (`-c472a02.md:56-61`) already cites
`test-gh-cost-log.py:251-259` by name and reasons about its scope correctly — it never claims the
OFF clause is "asserted nowhere." The false "asserted nowhere"/"unpinnable by mutation" premise is
attributed, by the validator-lead's own digest, to "the eng lead and I" (`digest.md:27-28`) — not to
me. My actual cycle-1→cycle-2 movement (`high`→`low`) came from a different, later trace (guard
non-interaction, captured correctly as candidate 2/O-08 and candidate 3/O-09 above), not from
correcting a premise I never held. Accepting candidate 1 as written would misattribute someone
else's error into code-reviewer craft and teach a lesson my own record doesn't support. Not
re-litigated per dispatch terms.

## Entry counts

| File | Section | Before | After |
|---|---|---|---|
| `.harness/expertise/harness-code-reviewer.md` (craft) | Patterns | 15 | 15 |
| | Gotchas | 15 | 15 |
| | Outcomes | 7 | 9 |
| | Open | 0 | 0 |
| `.harness/harness/expertise/harness-code-reviewer.md` (repository) | Gotchas | 3 | 3 |
| | all other sections | 0 | 0 |

Repository file untouched — none of the three candidates turn on a path, decision or invariant
specific to this checkout; all are general review-methodology rules.

## check-expertise.sh

`.claude/skills/harness/bin/check-expertise.sh .harness/expertise/harness-code-reviewer.md` → `OK`
(one round of trimming: O-08 and O-09 were initially 53/52 words, cut to 39/41).
