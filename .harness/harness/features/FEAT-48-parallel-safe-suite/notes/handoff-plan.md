# Handoff — FEAT-48-parallel-safe-suite, plan → build — written at 99dab78a, seq-8

## Next

**Plan phase is COMPLETE. Nothing remains in it.** Plan and BRIEF are signed (Mike Ruangutai,
2026-09-02, `85900e7f`), station is `ready`, the mirror is open, and FEAT-48 carries zero
`check-state.sh` violations.

The build phase begins with `harness-eng-lead` hosting the `build` team, task set **T-01 alone** —
the DAG is a strict chain T-01 → T-02 → T-03 → T-04 → T-06 → T-05, so each dispatch is one task.
**T-07 is `abandoned` and is NEVER in the task set**; `build.yaml`'s `steps_from` has no status
filter, so that exclusion is manual at every dispatch. Per task, in one act: set its station to
`building` with `plan-merge.py set-task-station`, then `gh-sync.py start-task <feature-dir> T-NN` —
plan first, then the subcommand, or the parent write is a silent no-op.

## Trust

- Plan and BRIEF both signed; station `ready`; `panel:` cycle 6 PASS, `severity_max: med` —
  read at source — verified-at 99dab78a
- Mirror open and correct: milestone #40, parent #1191, T-01..T-06 → #1192-#1197 all at `ready`,
  and `gh-sync: T-07 is abandoned — no sub-issue created` — the tool's own output —
  verified-at 99dab78a
- Zero `check-state.sh` violations for FEAT-48 — full run — verified-at 99dab78a
- The rebase onto `d135364e` did NOT change `plan.yaml`: blob `9684cf17` before and after —
  `git rev-parse <sha>:<path>` on both sides — verified-at 99dab78a
- **Two NEW live-tree mutation sites are in the tree**, `test-check-fixture-secrets.py:150` and
  `:198`, writing `.check-fixture-secrets-*mutant-<pid>.sh` into live `bin/`; discovered count is
  now 61 — verified-at 99dab78a. **No plan edit was needed**: the file is under
  `.claude/skills/harness/bin/**`, so T-02's widening clause covers it and T-03's live-tree zero
  backstops it. The doer must NAME the addition in its receipt.
- Editing T-07's `status` or `depends_on` reddens T-02: its verify fails unless `absorbed` is
  non-empty, and `absorbed` derives from T-07 being present, abandoned, and naming T-02 —
  `plan.yaml:492`, derivation `:464-467` — verified-at 047f6914
- SEC-01 blocks every pre-`review_sha` code-reviewer digest for the whole build phase; it clears
  only when `review_sha` is pinned at the Building → Review seam — verified-at 85900e7f
- The 0/0 satisfiability sweep had ONE sweeper, and the same reader's bare 0 in cycle 5 missed a
  case the goal-check caught — `runs/2026-09-01-10-validator/digest.md` note 1 — UNVERIFIED
- Nobody has executed the ~250s census scan; rot ABSORPTION now has three real measurements, rot
  DETECTION is still argued — same digest — UNVERIFIED

## Dead ends

- Do NOT re-plan for the two new hazard sites. Absorbing a moving `main` without a plan edit is the
  design the operator ordered, and this is its third passing test — `plan.yaml` D-10, T-02's
  widening clause — verified-at 99dab78a
- Do NOT dissolve T-07 or grow T-02's `files:`: `amend --yaml-value` replaces a field and cannot
  delete an item, so every variant leaves T-07 in the file and no tool observes a difference —
  `runs/2026-09-01-08-validator/digest.md` Q1 — verified-at 047f6914
- Do NOT re-date the stale numerals (59 files, 192/DEC-209, 117 files) — that is the rot treadmill
  D-10 abolished — same digest, Q4 — verified-at 047f6914
- Do NOT call `gh-sync.py open` again — `feature.json`'s `github` receipts make it a no-op, and
  re-running to "discover" one is what the contract forbids — `github-mirror.md` — at 99dab78a

## Working set

- `.harness/harness/features/FEAT-48-parallel-safe-suite/plan.yaml` (the six live tasks, `panel:`)
- `.harness/harness/features/FEAT-48-parallel-safe-suite/feature.json` (`github` receipts)
- `.harness/harness/features/FEAT-48-parallel-safe-suite/runs/2026-09-01-10-validator/digest.md`
- `.harness/harness/features/FEAT-48-parallel-safe-suite/STATE.md`
- `.agents/skills/harness/references/github-mirror.md`
