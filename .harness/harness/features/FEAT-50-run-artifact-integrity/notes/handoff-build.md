# Handoff — FEAT-50-run-artifact-integrity, build (partial) → main session — written at 5ae9274, seq-1

## Next

Do not dispatch a squad. The main session implements T-01–T-06 and T-09–T-12 itself; every one
is DEC-174 `main-session-direct` and no governed agent, this orchestrator included, may write
those seven files. Before T-08 can record `done`, pm must amend one token in its `verify:`
(Q1 below) under the operator's signature. T-03, T-09 and T-11 may proceed now: their
`worktree_for_feature` seam is landed and green. T-07 stays last — it depends on all eleven.

## Trust

- T-08's seam and cutover are landed and correct: `harness_boundary.py:185` `AmbiguousWorktree`,
  `:193` `worktree_for_feature`, `inflight_registry.py:263` calls it — grep — verified-at 5ae9274
- `test-harness-boundary.py` 17 PASS / 0 FAIL with all six named cases present; six case names
  read back from the runner's own output — verified-at 5ae9274
- `test-inflight-registry.py` 111/111 and the file is UNMODIFIED in `git status --porcelain` —
  that is SC-16's before-and-after invariance evidence — verified-at 5ae9274
- The hyphen boundary holds in the production function, not only in its test: `FEAT-XY-thing`
  and `FEAT-XY` both return `None` against a lone `FEAT-X` worktree — direct probe — verified-at 5ae9274
- T-08's `verify:` FAILS at its last assertion and only there; the eight before it pass —
  ran the heredoc verbatim from the worktree root — verified-at 5ae9274
- `'OTHER-thing'` satisfies that assertion — `worktree_for_feature` → `None`, `feature_root` → `d`
  — direct probe — verified-at 5ae9274
- `check-domain.sh` hook mode exits 2 for `harness-orchestrator` on all seven main-session-direct
  files; `bash-write-guard.sh` refused `cp` on `validate-digest.py` — ran both — verified-at 5ae9274
- T-01 and T-02 pass their plan `verify:` verbatim at exit 0 and `test-validate-digest.py` is
  ALL PASSED, `empty-red` green, mutant removed — ran all three — verified-at 5ae9274
- The eng lead's `runs/t08-eng/digest.md` satisfies DEC-156 — `validate-digest.py harness-eng-lead`
  exit 0, `digest ok` — verified-at 5ae9274
- HEAD is unmoved at 5ae9274 and NOTHING is committed — `git status --porcelain` — verified-at 5ae9274
- The dirty-file SET is NOT stable: the main session began editing `check-domain.sh` and
  `bash-write-guard.sh` while this note was being written, so re-measure it yourself rather
  than trusting any count — `git status --porcelain`, 2026-08-31 — UNVERIFIED beyond that moment
- **UNVERIFIED**: the full unit and integration matrix after T-08. The only baseline is a
  `run-unit-tests.sh` exit 0 captured while T-01 was mid-apply, so it is not a clean pre-image.
  Re-run both suites once the main session's tasks land.
- **UNVERIFIED**: `check-state.sh` at any point in this phase. SC-11 is ungraded.

## Dead ends

- Do not route the T-08 verify failure to the eng squad as a fix cycle — the code is right and
  the assertion is unsatisfiable under the task's own rule — `runs/t08-eng/digest.md` — verified-at 5ae9274
- Do not mark T-08 `done` before that amendment; `gh-sync.py status Review` refuses unless every
  task reads `done` — `gh-sync.py:955-957` — verified-at 5ae9274
- Do not grant the seven gate paths in `.harness/team-config.yaml` — that changes DEC-174 and the
  main session ruled against it — parent instruction, this run — source
- Do not revert or re-apply T-01/T-02; the main session owns both files now — parent instruction,
  this run — source

## Working set

- .harness/harness/features/FEAT-50-run-artifact-integrity/plan.yaml
- .harness/harness/features/FEAT-50-run-artifact-integrity/STATE.md
- .harness/harness/features/FEAT-50-run-artifact-integrity/runs/t08-eng/digest.md
- .harness/harness/features/FEAT-50-run-artifact-integrity/notes/receipt-harness-backend-dev-t08-eng.md
- .claude/skills/harness/bin/harness_boundary.py
