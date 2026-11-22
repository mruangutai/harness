# Red-first evidence — T-02 (FEAT-2229, SC-04/SC-05/SC-07)

Static wiring regressions only: they prove each instruction is present at its owner, not that any
agent obeys it.

## Red
New `tests/integration/test-plan-team.py` (case 10) run against the pre-T-02 tree
(`git archive HEAD` = d22d1860, new test file copied in): exit 1, `30 of 153 FAILING.`

```
FAIL  (10) template: names exactly the five row fields
FAIL  (10) template: instantiates the explicit empty list
FAIL  (10) template: example needs no real decision id
FAIL  (10) template: drafted_at is writer-owned, not user-filled
FAIL  (10) patch-lane: one-task plan still carries the block
FAIL  (10) patch-lane: one-task plan still runs the check, adding no panel
FAIL  (10) plan/draft: every new draft carries the five-field block
FAIL  (10) plan/draft: explicit empty list when nothing is affected
FAIL  (10) plan/draft: verbatim clauses
FAIL  (10) plan/draft: resolvable amend/strike successor
FAIL  (10) plan/draft: a task owns DECISIONS.md
FAIL  (10) plan/scope: searches touched surfaces independently of the plan's list
FAIL  (10) plan/scope: flags omissions
FAIL  (10) plan/scope: flags an unjustified empty list
FAIL  (10) plan/scope: applies DEC-188 strike-vs-amend
FAIL  (10) plan/scope: softer strike needs operator authorization
FAIL  (10) plan/scope: mechanical defects left to the check
FAIL  (10) validate/goalcheck: points at canonical harness-pm Mode 2 at the supplied pin
FAIL  (10) pm Mode 2: third falsifiable unit
FAIL  (10) pm Mode 2: keep rows are not graded
FAIL  (10) pm Mode 2: per-row read pinned at review_sha, never the working tree
FAIL  (10) pm Mode 2: sc_status row: DEC id, verdict, inspection method
FAIL  (10) pm Mode 2: evidence names review_sha, path and pinned line
FAIL  (10) pm Mode 2: amend and strike landing tests
FAIL  (10) pm Mode 2: mention or green suite is insufficient
FAIL  (10) pm Mode 2: failed landing fails the goal-check, routed to the owning task
FAIL  (10) pm Mode 2: missing owner is a plan/scope defect
FAIL  (10) validator gate: failed dispositions become must_fix against the owning task
FAIL  (10) validator gate: clean QA cannot erase a failed landing
FAIL  (10z) template's decisions_affected is the instantiated empty list, not a comment
```

## Green
Same test in the worktree after the T-02 prompt/doc edits: exit 0, `182/182 checks passed.`,
no FAIL lines, ~3.5 s wall.

## Mutation witnesses
1. In-script (case 10m, 30 checks, all ok): for every obligation, its matched text is deleted from
   its own owning slice and that obligation's assertion must report missing.
2. File-level: one line carrying an obligation deleted from the real file in a temp copy of the
   tracked tree, test re-run:

- template: example needs no real decision id — rc=1; FAIL: ['(10) template: example needs no real decision id']
- template: instantiates the explicit empty list — rc=1; FAIL: ['(10) template: instantiates the explicit empty list', "(10z) template's decisions_affected is the instantiated empty list, not a comment"]
- patch-lane: one-task plan still runs the check — rc=1; FAIL: ['(10) patch-lane: one-task plan still runs the check, adding no panel']
- plan/draft: verbatim clauses — rc=1; FAIL: ['(10) plan/draft: resolvable amend/strike successor']
- plan/scope: softer strike — rc=1; FAIL: ['(10) plan/scope: softer strike needs operator authorization', '(10) plan/scope: mechanical defects left to the check']
- plan/scope: searches touched surfaces — rc=1; FAIL: ["(10) plan/scope: searches touched surfaces independently of the plan's list", '(10) plan/scope: flags omissions']
- validate/goalcheck: points at canonical — rc=1; FAIL: ['(10) validate/goalcheck: points at canonical harness-pm Mode 2 at the supplied pin']
- pm Mode 2: keep rows are not graded — rc=1; FAIL: ['(10) pm Mode 2: keep rows are not graded']
- pm Mode 2: missing owner — rc=0; FAIL: []
- validator gate: failed dispositions — rc=1; FAIL: ['(10) validator gate: failed dispositions become must_fix against the owning task', '(10) validator gate: clean QA cannot erase a failed landing']
- pm Mode 2: missing owner — rc=1; FAIL: ['(10) pm Mode 2: missing owner is a plan/scope defect, not success']

   (Line deletion takes neighbouring wrapped obligations with it; every run reddened the owning
   section's assertion. The pm "missing owner" witness first stayed green, which exposed an
   under-specified pattern; the assertion now covers "never a reason to claim success" and reddens.)

## Gates
- `check-instruction-paths.py`: 0 violations (the pinned read names `<repo-relative DECISIONS.md path>`
  inside `git show` instead of an unanchored literal path).
- `check-skill-weight.py`: exit 0.

## Validate c1 F-01 — the strike alternative (test-only fix)

Gap: case 10 checked pm Mode 2's strike test only up to "a strike only when the strike record
exists". The alternative, "or the deletion is justified by its named successor with citations
repointed (DEC-188, DEC-205)", had no assertion.

Mutation: in a temp copy of the tracked tree (HEAD 98305097), the alternative clause was removed
from `.omp/agents/harness-pm.md` by a whitespace-tolerant regex (1 substitution); harness-pm.md
itself is unchanged.

- Old test (HEAD) vs mutated pm: exit 0, `182/182 checks passed.` — the gap is reproduced: the
  deletion went unnoticed.
- New test vs mutated pm: exit 1, `1 of 183 FAILING.` —
  `FAIL  (10) pm Mode 2: strike alternative: successor-justified deletion with repointed citations`.
- New test vs the real worktree: exit 0, `184/184 checks passed.`, no FAIL lines; includes
  `ok    (10m) pm Mode 2: deleting 'strike alternative: successor-justified deletion with repointed
  citations' reddens its assertion`.
