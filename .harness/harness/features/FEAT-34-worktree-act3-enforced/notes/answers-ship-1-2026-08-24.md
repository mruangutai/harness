# FEAT-34 — operator answers, ship escalation 1, 2026-08-24

Written by the main session. Every ruling here was decided by the user except where it says
otherwise.

## Q1 — the stale signature. CLEARED.

`plan.yaml`'s `approval:` mapping was reset and re-signed. It now carries a `signatures:` list with
both signatures of the day and a comment recording exactly what the second one covers: D-10, the six
edited task intents, the two edited verifies, and the fact that T-01 and T-02 reopen.

**You do not need to check this again.** Verified after writing: `status: approved`, ten decisions,
thirteen tasks.

## Q2 — D-10 stands. Re-run T-01 and T-02. USER RULING.

**The user re-signed with D-10 in it.** `classify_all` goes in `worktree_terminal.py`, not in
`check-state.sh`. Dispatch the rework; `cycles_used` going to 2 of 10 is authorised.

The reasoning was verified independently by the main session before it reached the user, so treat it
as settled rather than re-arguing it:

- `worktree_terminal.py:56` runs `git worktree list` with `cwd=root`. That is ONE repository. A
  served repo's worktrees sit inside a different git repository, which that call can never report.
  So REQ-04's "every repository" clause is genuinely unmet today.
- `test-worktree-terminal.py` is green at **19 of 19, exit 0**, measured directly. Its case (g)
  calls `classify(repo2)` on the second repository's own root — it proves the per-repo predicate and
  proves nothing about one caller covering both.
- `grep -c "def classify_all"` returns **0**. D-10 is a plan change, not something already built.

The cost was named on both sides and accepted: two spawns of real rework now, against test leverage
that would be lost permanently if the logic landed on the main-session-direct lane.

## Q4 — ADD THE CRITERION. Amendment 2. USER RULING.

**The user chose to add it rather than leave it ungraded or defer it to validate.**

The gap, verified at source: `BRIEF.md:179-182` — SC-04 grades only the POSITIVE second-repo case, a
`Done` feature in a second repository producing an `INV-29` finding. `BRIEF.md:62-63` — REQ-04
requires "no per-repository exception to remember or later remove". **D-10's three-way failure
posture is what satisfies that clause, and no success criterion grades any branch of it.** A
repository silently skipped because its checkout could not be enumerated would pass every criterion
in the signed brief.

**pm authors it.** Wording, numbering and `verify:` method are pm's, per DEC-132 — this is a goal
constraint, not a pre-written criterion. What it must grade, stated as an outcome rather than as
text to transcribe:

- `fleet.yaml` failing to load is a blocking violation, not silence.
- A declared repository whose checkout directory does not exist produces no record and no error.
- A declared repository whose checkout exists but cannot be enumerated produces one
  repository-level unresolved record, and it is blocking.

Each branch asserted separately, never by a total count. **This costs no extra fixture work** —
`test-worktree-terminal.py:337-406` already builds the `fleet.yaml` plus real second repository this
needs. It makes evidence that will exist anyway into graded evidence.

**Run it in parallel with the T-01/T-02 rework.** SC-15 grades behaviour D-10 already specifies, so
it does not change what the eng squad builds. Do not serialise the two.

The BRIEF's `## Approval` block will be stale again once Amendment 2 lands. **Return it to me and I
re-sign.** Do not write that block yourself.

## Q3 — the seven main-session-direct tasks. Acknowledged, not started.

T-06..T-12 (#823–#829) are mine. **I have started none of them**, so no work exists against the
pre-correction text of T-06 or T-07.

Your caveat about T-10 is recorded and I am not treating pm's claim as verified either.
**I will close that permanently: `plan.yaml` gets committed once Amendment 2 is signed**, so every
later plan edit is a real diff rather than a claim about one.

## Q5 — task status. Understood.

T-01..T-05 stay `building` until each `[harness:t-NN]` commit lands, and the commit pen is mine.
`gh-sync.py status Review` refusing until every task reads `done` is correct behaviour, not an
obstacle. I will write `done` as each commit lands.

## Standing instruction, unchanged

Every decision, question and option holds the QUALITY, PERFORMANCE and EFFICIENCY of the system as
the highest priority. Never accept a cheap proxy for a check because the real measurement costs
another run.
