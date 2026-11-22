# Red-first — T-04 guard slice (bash-write-guard + claim_set_refusal advice)

Command (feature worktree): `python3 tests/integration/test-bash-write-guard.py`

## Red — new tests against the pre-change guard and boundary

Exit 1. Every pre-existing section stayed green (48/48 CASES, 7/7 T-14, 29/29 worktree,
3/3 deep, 20/20 HEAD-move, 6/6 FEAT-50, 6/6 FEAT-61, 4/4 FEAT-65, 2/2 bug895, 8/8 bug1106).
Failing checks:

- `[bug1304] direct expertise merge CLI is refused in favour of expertise_apply` (was exit 0)
- `[bug1304] direct expertise redirect is refused with sanctioned advice` (advice named
  `expertise-merge.py apply`, not `expertise_apply`)
- `feat2225 <persona>: refused <form>`: all 12 mutator forms × harness-eng-lead,
  harness-code-reviewer, harness-dev-ops, harness-backend-dev = 48 failures (each exit 0).
  Forms: direct executable member-ops; `.agents` symlink apply; python3 ops; python3 -u
  absolute replay; env python3 member-ops; /usr/bin/env + assignment apply; bash -c apply;
  sh -c replay; compound after cd; stdin heredoc member-ops; merge-gate merge-distill;
  bash -c merge-distill.
- `feat2225 repository-tier Expertise redirect names expertise_apply with the repository tier`
  (got the generic "write it from a bound worktree" advice)

Summary line: `40/89 FEAT-2225 expertise CLI cases passed.` The 40 that passed are the
reads (7 forms × 4 personas) and the 12 main-session allows — the allow half, as expected.

## Green — after the change

Exit 0. All sections pass, including `89/89 FEAT-2225 expertise CLI cases passed.` and every
`[bug1304]` check.
