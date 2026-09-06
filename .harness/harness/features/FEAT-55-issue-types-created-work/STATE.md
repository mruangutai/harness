# STATE

## Current

- feature: FEAT-55-issue-types-created-work
- run: none — ship acceptance, no squad dispatched and no run appended
- squad: none
- status: awaiting_user — every act permitted to me is DONE; the merge is the one remaining act and
  it is user-gated
- station: review, UNCHANGED in plan.yaml. The feature has NOT reached `done`: the branch is
  unmerged and `gh-sync.py ship` has not run. Writing `done` now would record a station the feature
  has not reached, and that write belongs to the main session's `gh-sync.py ship`.
- mission: ship — operator decision applied.

- operator ship decision `notes/answers-ship-20260906.md`, handed to me by the main session (the
  only path I trust, issue #671): ship FEAT-55; file backlog row **B-1 only**; B-2..B-16 are not
  created in this ship action. Committed to the feature record this session.
- **B-1 FILED — issue #1388**, https://github.com/mruangutai/harness/issues/1388, title "B-1: run
  tests/manual/probe-issue-types.py --create-in against an organization-owned repo with Issue Types
  enabled", labels `harness`+`chore`, state OPEN, verified by `gh issue view 1388`. Written by
  `gh-sync.py backlog <feature-dir> "chore:<title>"`. **That verb is NOT idempotent** — it creates a
  fresh issue per call and records nothing in feature.json, so it must not be re-run for B-1.
- B-2..B-16 NOT created, per the ruling. They survive only in the briefing table
  `notes/ship-review-2026-09-05-02-eng.md`.
- approval gate re-verified on disk this session, both fragments (never one): BRIEF `## Approval`
  reads `status: approved` / molchairuangutai / 2026-09-05, and plan `approval.status: approved`
  with the same signer and date plus two `rulings`. Neither is writable by me; neither was touched.

- **MERGE NOT PERFORMED, and it is not mine to perform.** Measured this session:
  - `git -C /Users/molchairuangutai/GitHub/harness switch main` → `bash-write-guard: BLOCKED — git
    switch moves HEAD, and every harness agent is refused this for the duration of a run`. `merge`
    is in the same `HEAD_MOVERS` set at `.claude/skills/harness/bin/bash-write-guard.sh:176`, so a
    local merge is refused identically. The guard working, not a malfunction. DEC-153 keeps merge,
    PR and deploy user-gated; the commit pen alone is mine.
  - `gh-sync.py ship <this worktree's feature dir>` → exit 1, refused BEFORE any write or network
    call: "resolves inside a worktree which is about to be deleted... Run ship against the main
    checkout's copy." That copy cannot exist until the merge lands, so ship FOLLOWS the merge.
- mirror state, measured not recalled: `feature.json` carries **no `github` key** — `gh-sync.py
  open` never ran for FEAT-55, so there is no milestone, no parent and no sub-issue; `gh api
  repos/mruangutai/harness/issues/1289/sub_issues` returns 0 and #1289 carries no milestone. `ship`
  would `skip("no recorded milestone")` even from the right directory. I did NOT run `open` now: it
  would create a milestone and twelve sub-issues for finished tasks purely to close them seconds
  later, and no harness command can close an issue by hand if that proves wrong. Main session's
  call, before `ship`, with `--parent 1289` if #1289 is to be adopted.
- remaining sequence, all outside an orchestrator's grant: `git push -u origin
  feat/issue-1289-issue-types` → PR and merge → optional `gh-sync.py open <main-checkout feature
  dir> --parent 1289` → `gh-sync.py ship <main-checkout feature dir> --body-file
  <that dir>/notes/ship-review-2026-09-05-02-eng.md` → the `post-merge` hook removes this worktree
  (INV-29 refuses while it stands).
- branch `feat/issue-1289-issue-types`, unpushed (`git ls-remote --heads origin` empty for it).
  `review_sha` stays `76ba5f41`; `git diff 76ba5f41..HEAD -- .claude tests` is EMPTY, so every
  reviewed line is under the pin and the later commits are feature-record only. Tree clean.
- budget: `cycles_used` 13 of 13 and `runs` 40 of 40, both unchanged — this session dispatched
  nobody and reworked nothing. Runs is at the informational INV-22 bound.
- briefing: `notes/ship-review-2026-09-05-02-eng.md` (+ rendered `.html`), sixteen proposed backlog
  rows, of which B-1 alone was accepted.
- handoff: `notes/handoff-validate.md`; `notes/handoff-build.md` superseded.
- intake: .harness/notes/grilling-issue-types-2026-09-04.md (source ticket #1289)

## Open Questions

No blocking questions. One refusal I chose not to work around, harness defects raised rather than
worked around, and one non-gating ratification.

- Q14 (harness defect, why the mirror is behind) — `gh-sync.py status <dir> review` REFUSED: "not
  every task in plan.yaml is done or abandoned". Correct that none reads done — this plan's tasks
  carry no `status:` key and `set-task-station` only SPLICES an existing line (Q5). I did NOT work
  around it: writing plan content outside `plan-merge.py` is what D-04 forbids. Never a gate.
- Q17 (NEW; the concrete instance of the unrepairable-digest defect) — FIVE FEAT-55 run digests fail
  the lead contract and `check-state.sh` reports each as a VIOLATION: `2026-09-04-03-product`,
  `2026-09-04-11-validator`, `2026-09-05-c5-validator`, `2026-09-05-26-validator` (all pre-existing,
  plan phase) and `2026-09-05-30-validator` — the review panel's own run, whose lead emitted a valid
  fenced contract in its RETURN and wrote a file without one. That file's prose record is complete
  and honest; only the machine fence is absent. I did not repair it: a digest cannot be repaired in
  place, the budget is spent, and retyping 6.7 KB of another agent's record to satisfy a parser
  risks corrupting a good one. The runs tree is gitignored, so all five die with this worktree at
  merge, and the panel's verdict is preserved above and in the briefing.
- Q3 (operator, non-blocking) — T-06 §5 specifies the backlog receipt nested under `items`, but
  T-05's red test seeds and reads those keys at the top level and T-06 had to make it green
  unedited, so the on-disk receipt is FLAT. Ratify it or correct the prose; behaviour is unaffected.
- Q4 — `bash-write-guard.sh` blocked `cp` onto a file outside my domain but NOT `python3 -c` writing
  the identical path in the identical call. It reads the command line for write verbs, not syscalls.
- Q5 — `set-task-station` records no station on a status-less plan, and misreports the cause as
  `T-01 is not in <file> — it carries: T-01, T-02`, naming the task it just called absent.
- Q6 — a truncated capture of the unit driver produced a FALSE GREEN. Captured output cannot be read
  for absence of failure.
- Q7 — the documentor's `Edit` resolved a relative path against the process cwd, not the dispatch
  worktree, briefly writing into the MAIN checkout. Detected, reverted, confirmed clean twice.
- Q12 — backend-dev's `Edit` on `tests/integration/test-gh-sync.py` reported success and issued a new
  snapshot tag while never reaching disk; a re-read returned pre-edit content and an identical retry
  was rejected as byte-identical. It landed by another route; I verified the content at source.
- Q13 — TWO agents wrote their checkpoint into `runs/2026-09-05-01-product/`, an older run's
  directory, because the runs tree is gitignored so a `Glob` returns nothing and a live directory
  reads as free. `check-domain` refused the `digest.md` write both times and allowed `state.yaml`
  both times. Unrecoverable; spent archive artifacts only, and both runs' digests survived.
- Q15 — the handoff shape gate resolves a `## Done when` authority pointer's relative path against
  the MAIN checkout root, not the worktree the note is written in, so `brief-sc:` and `plan-task:`
  cannot resolve from inside a worktree and every `finding:`/`approval:` pointer needs a
  `.claude/worktrees/<...>/` prefix duplicating the feature path.
- Q16 (advisory, non-gating) — `probe-issue-types.py:97-101` `_read_back_issue_type` `%`-formats
  owner and name into GraphQL query TEXT rather than passing `-f owner=`/`-f name=` as every other
  call site does. Reachable only behind the operator's `--create-in` flag on a host-only probe, so
  nothing crosses a boundary; unsafe the moment it gets an externally-sourced caller. Backlog B-9,
  NOT filed — the ruling accepted B-1 only.
- Q8, Q10, Q11 (carried from the plan phase) — `validate-digest.py` rejecting `code_grade: n_a` on a
  plan review; the `harness-spec-driven` verb list omitting `amend`; `amend --key` accepting only
  `tasks|decisions`.
</content>
<parameter name="i">Recording ship-acceptance state