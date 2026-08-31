# The team-count tripwire — ruling

**Within approved scope. It needed a task, and T-12 is it. No re-signature, and FEAT-06's SC-05 is
not revisited.** What needs correcting is the constant, which generalised a completion snapshot into
a standing invariant it never was.

I agree with the lead, on primary sources rather than on deference — the four readings below are the
ones that settle it, and each is quoted from the file, not from the dispatch prose.

## The evidence

1. **The third file is signed product, not drift.** `plan.yaml` T-02 (`id: T-02` block): `status:
   done`, `traces: [REQ-01, REQ-02, REQ-04, REQ-05, REQ-09, REQ-14]`, and its only `files:` entry is
   `.claude/skills/harness/teams/plan-panel.yaml`. `approval:` is `status: approved`,
   `date: 2026-08-30`, `covers: '11 tasks, REQ-01..REQ-14, SC-01..SC-17, reader pinned
   fable-advisor'`. The operator signed the existence of that file.
2. **FEAT-06's SC-05 is a completion snapshot.** `FEAT-06-team-layer-inv6/BRIEF.md:157-160`: "the
   directory's contents **at completion** are exactly **two** files — `review.yaml` ... and
   `build.yaml`. `gate-probe.yaml` is deleted (T-10), so the count is two, not three." It constrains
   a moment, and that moment passed with the criterion met. It is permanently met and cannot be
   falsified by later work. Nothing to revisit.
3. **The constant is where the over-reach lives.** `test-harness-yaml-corpus.py:169`,
   `TEAMS_EXPECTED = 2`, consumed as a real condition at `:241-242` —
   `counts.get(TEAMS_ROOT) == TEAMS_EXPECTED` — turned "two at FEAT-06's completion" into "two
   forever". That generalisation is the defect. The assertion itself is correct and stays.
4. **The comment's prohibition is against silence, not against the number.** `:167-168` — "If a third
   team is legitimately added, this failing is the intended prompt to revisit SC-05 rather than to
   **silently** widen the number." A `decisions:` entry citing the requirement that forces the file is
   the opposite of silent, so the prohibition is satisfied without the operator's pen.

The rule that decides it: an approved consequence that no task owns needs a task; only a criterion
that **cannot be met as written** needs the operator. Nothing here is unmeetable — the plan's own
signed task produced the file, and no criterion in either feature is contradicted.

Two `SC-05`s exist and they are unrelated: FEAT-06's is the team-directory count; FEAT-45's
(`BRIEF.md:111-114`) is about distinguishing a resolved from an overruled panel finding. The corpus
test's comment refers to FEAT-06's.

## What was added

- **D-15** — the ruling and its reason, in the plan's existing `decisions:` shape.
- **T-12** — raise the constant to 3 and rewrite the stale comment. `traces: [REQ-02]`,
  `change_type: logic`, `execution_mode: team`, `execution_agent: harness-dev-ops`,
  `depends_on: []`, `status: pending`, one file.

**Why `[REQ-02]` alone, not `[REQ-01, REQ-02]`** — the weakest set the evidence supports. REQ-01
requires the panel to read every plan, which the orchestrator sequence could satisfy with no new team
file at all. REQ-02 requires an independent-model reader hosted by a lead; a lead-hosted reader step
is a team-runner step, and DEC-118's single-squad rule forces it into a validator-squad team file of
its own. REQ-02 alone therefore forces a third file into that directory. REQ-04's scope reader rides
in the same file but does not independently force it.

## The verify block, proved in both directions

Two conjuncts: run the corpus test, then inspect the source. Proved 2026-08-31 by loading the block
from the applied `plan.yaml` and running it verbatim through bash:

- on a tree with the fix applied — `16/16 checks passed.` then `OK`, exit 0;
- on the real tree — exit 1, `FAIL  .claude/skills/harness/teams holds exactly 2 team definitions`;
- against a mutant with the condition replaced by a bare literal `3` — fails "no longer asserted
  against the constant", which is the original f-string-label defect the comment records;
- against a mutant with the constant raised and the comment left stale — fails naming
  `plan-panel.yaml` and `D-15`.

So the block cannot green before the work is done, and it cannot green on a fix that re-displays the
count instead of asserting it.

## Open, non-blocking

The `lanes:` block carries no row for `test-harness-yaml-corpus.py`. `plan-merge.py` unions only
`tasks:` and `decisions:` and exits 7 on any differing top-level key, so pm cannot add it. Live
resolution is `harness-backend-dev, harness-dev-ops`; `check-plan-routes.py` reports
`OK T-12 granted to harness-backend-dev, harness-dev-ops`, `0 violation(s)`. A row is the main
session's one-line edit if the lanes block is to stay exhaustive.
