# Handoff — FEAT-48-parallel-safe-suite, plan → signature then build — written at 047f6914, seq-6

## Next

Main signs: `plan-merge.py sign-approval` on
`.harness/harness/features/FEAT-48-parallel-safe-suite/plan.yaml`, pre-authorised by the operator
against `fable-advisor`'s `approve: "yes"`. **`BRIEF.md`'s own `## Approval` is also `pending` and
both must read approved before any ship-mission orchestrator will start** (INV-3, and the ship
step-0 gate). Then station the tasks `ready` and run `gh-sync.py open` — the mirror opens only
after the approval gate passes (`references/github-mirror.md:38`), which is why INV-26 is red now.
Build order is the plan's own DAG: T-01 → T-02 → T-03 → T-04 → T-06 → T-05. **T-07 is `abandoned`
and must NOT be dispatched** — its exclusion is prose, not a mechanical guard, so exclude it by
hand when choosing the task set for `eng-lead`.

## Trust

- Plan is signable: `panel:` records cycle 6 `PASS`, `severity_max: med`, 16 findings all open and
  none above med, three readers all `ran` — `plan.yaml` `panel:`; `check-state.sh` INV-32 silent —
  verified-at 047f6914
- Advisor's `approve: "yes"` with nine residual risks —
  `runs/2026-09-01-10-validator/digest.md` `## Advisor recommendation` — verified-at 047f6914
- The derived census is real, not cosmetic: a rebase adding a 60th test file and a 193rd decision
  across 21 plan-relevant files forced zero plan edits — `git diff --stat 38dd3622 a93a1df9` —
  verified-at 047f6914
- Cycle 4's gating high is closed per-FILE, so anchor drift inside an owned file cannot reopen it;
  only a hazard in a file no task owns can — `runs/2026-09-01-10-validator/digest.md` —
  verified-at 047f6914
- T-02's verify fails unless `absorbed` is non-empty, and `absorbed` derives from T-07 being
  present, `abandoned`, and naming T-02. **Editing T-07's `status` or `depends_on` reddens T-02** —
  `plan.yaml:492`, derivation `:464-467` — verified-at 047f6914
- `gh-sync.py:1152` will refuse the review-station write while T-07 stands —
  `check-state.sh`-independent, read at source by the validator lead — UNVERIFIED by me
- The 0/0 satisfiability sweep had ONE sweeper; cycle 5's bare 0 from the same reader missed a case
  the goal-check caught, and the goal-check did not re-run this cycle —
  `runs/2026-09-01-10-validator/digest.md` adequacy note 1 — UNVERIFIED

## Dead ends

- Do NOT dissolve T-07 or grow T-02's `files:`: `amend --yaml-value` replaces a field and cannot
  delete an item, so every variant leaves T-07 in the file and no tool observes a difference —
  `runs/2026-09-01-08-validator/digest.md` Q1 — verified-at 047f6914
- Do NOT re-date the stale numerals (59 files, 192/DEC-209, 117 files) on a rebase: that is the rot
  treadmill D-10 abolished — same digest, Q4 — verified-at 047f6914
- Do NOT add a closure criterion for #1053: SC-05's ten `--kind all` runs already exercise
  `test-gh-sync.py` (`run-unit-tests.sh:31`, `:44`) — same digest, Q2 — verified-at 047f6914
- Do NOT expect a pre-`review_sha` code-reviewer digest to validate: SEC-01 refuses every
  `code_grade` including `n_a`, measured at this tip — `validate-digest.py` — verified-at 047f6914

## Working set

- `.harness/harness/features/FEAT-48-parallel-safe-suite/plan.yaml` (`panel:` and the seven tasks)
- `.harness/harness/features/FEAT-48-parallel-safe-suite/BRIEF.md` (`## Approval` still pending)
- `.harness/harness/features/FEAT-48-parallel-safe-suite/runs/2026-09-01-10-validator/digest.md`
- `.harness/harness/features/FEAT-48-parallel-safe-suite/runs/2026-09-01-08-validator/digest.md`
- `.harness/harness/features/FEAT-48-parallel-safe-suite/STATE.md`
