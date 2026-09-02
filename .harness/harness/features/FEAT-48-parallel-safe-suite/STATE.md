# STATE

## Current

- feature: FEAT-48-parallel-safe-suite
- run: none this phase — ship preparation is orchestrator-direct, no squad was dispatched
- squad: none
- status: **ship prepared — awaiting the main session's PR, merge and backlog filing**

Station **`done`**, written by `plan-merge.py set-feature-station` on the branch. `review_sha`
`27f8105b`, **unmoved**; no source file, `plan.yaml` task, `BRIEF.md` or decision was touched.
Branch `feat/FEAT-48-parallel-safe-suite`: **31 ahead, 0 behind** `origin/main`, tree clean, no PR
open yet.

**Why `done` is written before the merge, deliberately.** `worktree_terminal.classify` reads
`plan.yaml`'s `status:` **from the default branch**, so the `post-merge` hook's sweep — which runs
`gh-sync.py ship` and then removes this checkout — fires only if `done` is already landed. FEAT-50
and FEAT-51 each paid a second closeout PR (#1111, #1158) for landing it afterwards. Landing it
inside this PR collapses the ship to one merge. The station on a branch is invisible to
`check-state.sh` in the main checkout, so nothing reads a premature `done` in the meantime. If the
PR is not merged, revert with one command:
`plan-merge.py set-feature-station --file <plan.yaml> --station review`.

**What this phase produced** — three artifacts, all under `notes/`, plus the station line:

- `notes/pr-body-FEAT-48.md` — the PR body. Carries `Closes #1053` (ruling 4; precedent PR #1105
  closed its source issues the same way) and names milestone 40 / parent #1191 / sub-issues
  #1192–#1197. **No closing keyword for the parent or any sub-issue** — D-23 gives those to
  `gh-sync.py ship`'s done-station write and GitHub's `Auto-close issue` workflow.
- `notes/backlog-items-FEAT-48.txt` — B-1 … B-15 as 15 `nature:title` lines, ready for
  `gh-sync.py backlog`, which is the **main session's** subcommand and not mine. Each title is
  prefixed `[FEAT-48 B-N]` so the returned issue numbers map back to the briefing table without a
  second lookup. B-13 and B-14 are `harness defect` in the briefing and are filed as `bug`, the
  nearest of the three natures the tool accepts.
- `notes/handoff-ship.md` — the exact sequence the main session runs, with its verification points.

**What I did NOT run, and why.** `gh-sync.py open` — milestone 40, parent #1191 and all six
sub-issues are already recorded in `feature.json`, and a re-run to rediscover a receipt is
forbidden; it would also be the one path that could create a sub-issue for the abandoned T-07.
`gh-sync.py status <dir> done` — the board write belongs to `ship`, and moving the card to Done
before the merge would be a false record. `gh-sync.py backlog`, `ship` and `record-pr` — all three
are the main session's by owner (`references/github-mirror.md`). `gh-sync.py ship` additionally
**refuses to run inside a worktree at exit 1**, so it can only run against the main checkout after
the merge.

Budgets unchanged: `cycles_used` **8 of 10** — no rework this phase. `runs` **21 of an
informational 20 — crossed**, gating nothing; no run was added here.

## Open Questions

- **None blocking.** Every question raised at the validate seam is settled in
  `notes/answers-2026-09-02-c9.md`; this phase raised none.
- **Non-blocking, for the main session's awareness:** B-9 is filed as a plain backlog bug by the
  same command as the rest. Ruling 3 asks for its own `BUG-NN` **flow**, which is a later planning
  act seeded by that issue, not something the ship phase can create.
