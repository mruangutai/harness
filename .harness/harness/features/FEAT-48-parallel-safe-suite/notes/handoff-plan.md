# Handoff — FEAT-48-parallel-safe-suite, plan → build — written at 85900e7f, seq-7

## Next

**Plan phase is COMPLETE.** Plan and BRIEF are both signed (Mike Ruangutai, 2026-09-02, commit
`85900e7f`); `plan.yaml` station is `ready` and T-01..T-06 are `ready`. Two acts remain before the
first build dispatch, in this order:

1. **Main lands the `gh-sync.py` `abandoned` fix** (two call sites, one root): a `continue` on an
   abandoned task in `cmd_open`'s creation loop (`gh-sync.py:942`), and `finished_stations()`
   membership instead of `== "done"` at `:1152`. `bin/**` is main-session-direct (DEC-174).
2. **Then the orchestrator runs, in one act:** `gh-sync.py open <feature-dir>` followed by
   `gh-sync.py status <feature-dir> ready`. Both are the orchestrator's own subcommands.

Then the build's first segment is `eng-lead` with the `build` team, task set **T-01 only** —
the DAG is a strict chain T-01 → T-02 → T-03 → T-04 → T-06 → T-05. **T-07 is `abandoned` and is
NEVER in the task set**; `build.yaml`'s `steps_from` has no status filter, so that exclusion is
yours to make by hand at every dispatch.

## Trust

- Both approvals landed: `plan.yaml` `approval.status: approved` and `BRIEF.md:232` `status:
  approved`, same signer and date — read at source — verified-at 85900e7f
- Plan is `panel:` cycle 6 `PASS`, `severity_max: med`, 16 findings all open, none above med —
  `plan.yaml` `panel:`; INV-32 silent — verified-at 85900e7f
- `gh-sync.py open` WOULD create a sub-issue for the abandoned T-07: `parse_tasks` returns all
  seven and `cmd_open:942` has no status filter — measured by importing the module and calling it,
  `recorded issues: {}` so nothing exists yet — verified-at 85900e7f
- A T-07 sub-issue would hold the parent at ship forever: `ship` skips any card with an open child,
  and nothing closes a task sub-issue except `ship`'s own station write —
  `references/github-mirror.md` — verified-at 85900e7f
- Editing T-07's `status` or `depends_on` reddens T-02: its verify fails unless `absorbed` is
  non-empty, and `absorbed` derives from T-07 being present, abandoned, and naming T-02 —
  `plan.yaml:492`, derivation `:464-467` — verified-at 047f6914
- SEC-01 will block every pre-`review_sha` code-reviewer digest for the whole build phase; it clears
  only when `review_sha` is pinned at the Building → Review seam — measured against a probe digest —
  verified-at 85900e7f
- The 0/0 satisfiability sweep had ONE sweeper, and cycle 5's bare 0 from the same reader missed a
  case the goal-check caught — `runs/2026-09-01-10-validator/digest.md` adequacy note 1 — UNVERIFIED
- Nobody has ever executed the ~250s census scan; rot ABSORPTION is measured, rot DETECTION is
  argued — same digest — UNVERIFIED

## Dead ends

- Do NOT dissolve T-07 or grow T-02's `files:`: `amend --yaml-value` replaces a field and cannot
  delete an item, so every variant leaves T-07 in the file and no tool observes a difference —
  `runs/2026-09-01-08-validator/digest.md` Q1 — verified-at 047f6914
- Do NOT re-date the stale numerals (59 files, 192/DEC-209, 117 files) on a rebase: that is the rot
  treadmill D-10 abolished — same digest, Q4 — verified-at 047f6914
- Do NOT add a closure criterion for #1053: SC-05's ten `--kind all` runs already exercise
  `test-gh-sync.py` (`run-unit-tests.sh:31`, `:44`) — same digest, Q2 — verified-at 047f6914
- Do NOT run `gh-sync.py open` before the fix in `## Next` lands — see Trust — verified-at 85900e7f

## Working set

- `.harness/harness/features/FEAT-48-parallel-safe-suite/plan.yaml` (`panel:`, the seven tasks)
- `.harness/harness/features/FEAT-48-parallel-safe-suite/runs/2026-09-01-10-validator/digest.md`
- `.harness/harness/features/FEAT-48-parallel-safe-suite/runs/2026-09-01-08-validator/digest.md`
- `.harness/harness/features/FEAT-48-parallel-safe-suite/STATE.md`
- `.agents/skills/harness/references/github-mirror.md`
