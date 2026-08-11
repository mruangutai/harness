# Receipt — harness-pm — FEAT-12 send-back cycle 2 — 2026-08-10-03-product

**Both F-1 and F-2 landed. One cycle-1 edit had to move: F-2's defect also lived in `plan.yaml`
T-02's intent, so `plan.yaml` was touched and the A-2 check was re-run.** Nothing else changed.

Artifacts: `.harness/features/FEAT-12-end-copy-distribution/BRIEF.md` and `plan.yaml`.
Approval blocks untouched — `plan.yaml` `approval: {status: pending, approved_by: none, date: none}`
(`plan.yaml:4-7`); BRIEF `## Approval` / `status: pending` (`BRIEF.md:294`).

## The worktree measurement (F-2) — enumerated, not sampled

Observed 2026-08-10 in `/Users/molchairuangutai/GitHub/kaya-ai`, reads only. Anchor: kaya `master`
at `b6aaab9`; branch tips as named. (This repo's HEAD is `8dedeae`, one commit past cycle-1's
`687fd3e` — `8dedeae FEAT-11 signed`; `687fd3e` confirmed an ancestor. Kaya facts carry kaya shas.)

| worktree | branch | tip | `ls-files '.claude/skills/harness*'` |
|---|---|---|---|
| `333-env-test` | `feat/333-env-test` | `ab92578` | **55** |
| `feat02-statements` | `feat/120-statements-page` | `d09289c` | **48** |
| `feat03-live-review-loop` | `feat/48-live-review-loop` | `c7b2208` | **50** |
| `26-persistence-schema` | `feat/26-persistence-schema-design` | `e3785e2` | 0 (path absent from branch tree) |
| `review-redesign-spec` | `feat/121-spec-family-followup` | `6476d5e` | 0 |
| `transcript-263` | `feat/277-acceptance-transcript` | `4613f13` | 0 |

**Answer: TRACKED, not untracked. Three of six, not six. Deferral is TRANSIENT.**

- 153 files across 56 `.claude/skills/harness*` directories. Cycle-1's "56" was right as a
  *directory* count and wrong in attributing it to six worktrees and in calling it untracked.
- What is ignored is only the container, in the **main** tree: `git check-ignore -v
  .claude/worktrees` → `.gitignore:23:.claude/worktrees/`. That is why the copies never surface in
  kaya's root `git status`. Inside each worktree they are clean tracked content of that branch.
- `git ls-files '.claude/worktrees*'` on `master` → **0**. A factory clone of `master` carries no
  worktrees at all, so the deferral cannot reach SC-06.
- **The factory can never execute against the residue.** After T-05 the two diverged branches hold
  48 and 50 harness skill files with no upstream — a stale fork of the gates, which is the exposure
  worth bounding. Measured: `factory_workspace.py:118` fixes the working branch to
  `factory/issue-<N>`; `:103` cuts it from `origin/<default_branch>`; the only other checkout
  targets are `default_branch` (`:129-130`) and a pre-existing `factory/issue-<N>` ref cut the same
  way. No code path checks out a `feat/*` branch. Stated in the F-2 bullet rather than left implied.
- Branch-side diff of `.claude/skills/harness*` from each merge-base → **0 files, all three**
  (`feat02` and `feat03` differ from `master` only by 38 / 12 master-side changes). T-05's deletion
  commit therefore merges cleanly. **Each of the three loses its copy the next time that branch
  merges or rebases `master`** — no conflict, no follow-up work.
- Working-tree modifications to those paths inside the worktrees: 0 in all three.

Not ambiguous, not raised as an open question: the population was enumerated and is uniform in kind.
Three carrying zero is a different population, not disagreement.

## What changed

**F-1 — `## Goal` (BRIEF:28-40).** Rewritten so it and REQ-03 say the same thing. "kaya-ai's copy of
the tooling is removed" → the copy in kaya-ai's own three tooling directories, committed to
`master`; "never by holding a copy of it" kept as ambition ("not by holding a copy of it") with the
branch-local residue named in one closing clause and pointed at `## Constraints`. Still a goal
paragraph, not a second constraints list.

Swept the rest of the BRIEF for the same unqualified claim rather than stopping at the cited lines:

- `## Problem` (BRIEF:17) — carried "55 tracked skill files … 16 untracked agents" with no scope
  qualifier. A reader meeting the 153 later would read it as an undercount. Now "tracked on
  `master` … and a further 153 skill files tracked on three of its feature branches". Problem
  describes the present state, so it was not otherwise falsified.
- `REQ-03` (BRIEF:46-53) — "six git worktrees" corrected to three, deferral labelled transient with
  its mechanism.
- `## Verification gaps` — **checked, not edited.** It already says no test kind can observe another
  repository and that every kaya claim rests on inspection or the operator. Still true; the
  worktree finding adds nothing it does not already cover.
- No other unqualified "kaya-ai holds no copy" claim survives (grep of `worktree|untracked|
  gitignor|six|56|copy of` over the whole file).

**F-2 — `## Constraints` (BRIEF:181-203, the bullet opening "Out of scope and DEFERRED").** Bullet rewritten to state the **measured** reason, with
the three worktrees, their branches, tips and file counts named, `.gitignore:23` cited as what
actually hides them, and the correction stated in the artifact itself ("an earlier draft called the
copies untracked and gitignored. That was wrong and was never measured"), per rule 15. Says
explicitly that the deferral is transient and what the operator experiences: those three worktree
sessions lose harness capability on their next `master` sync — the intended end state arriving late
per branch, not a regression.

**F-2 also lived in `plan.yaml`.** `T-02` intent carried the same sentence ("six git worktrees …
They are untracked"). Rewritten to the measured facts, including the `master`-tracks-no-worktree-path
reason the globs cannot reach them. This is the one cycle-1 edit that had to move.

**`## Open questions`** — the deferral summary now carries the measured status of both deferrals
(first inert, second transient). **Q1 / `## Settled rulings` untouched:** the finding adds a
consequence to the push ruling, it does not falsify it, and the consequence is stated where the
deferral is stated.

## Gate results

- `check-plan-routes.py`: **exit 0**, `0 violation(s) across 7 plan(s)`. FEAT-12 lines are the same
  two predicted advisories as cycle 1 and nothing was restructured to chase them:
  - `DEVIATION T-01 .harness/features/FEAT-12-end-copy-distribution/notes/kaya-harness-manifest-before.txt granted to harness-orchestrator but declared main-session-direct`
  - `DEVIATION T-04 .harness/features/FEAT-12-end-copy-distribution/notes/kaya-harness-manifest-after.txt granted to harness-orchestrator but declared main-session-direct`
  - all other FEAT-12 lines `OK`.
- **A-2 re-run** (required — `plan.yaml` was touched). `safe_load` succeeds. Both `#<digits>` tokens
  survive with no reduction in count: raw `['#206','#202','#202','#202']`, loaded identical. All 49
  `because`/`choice`/`intent`/`execution_reason`/`verify` values have their whitespace-normalised
  50-char tail present in the raw text — 0 missing. Every `verify:` in the raw file is `|`
  (styles set = `{'|'}`, 14 of 14); all 14 loaded blocks end in a newline, 2 have multi-line bodies
  (`T-03` 12 lines, `T-14` 9) and 12 are single-line shell pipelines. *Precision note on cycle 1:*
  that receipt's "all 14 retain newlines" was true under the trailing-newline reading and is
  unchanged here; only 2 were ever multi-line.
  - Method note: comparing raw tails literally produces 7 false positives on the `>-` folded
    `because`/`choice` scalars, whose loaded last "line" is a joined paragraph. Whitespace
    normalisation is the correct comparison for folded values.

## Judged wrong

Nothing in the send-back. Both defects were real and both were mine: the Goal narrowing was missed,
and the "untracked and gitignored" sentence was exactly the R-9 shape I had been sent to eliminate —
an unmeasured git-state claim in a signed artifact. It was inherited from a cycle-1 observation
written before anything was measured, and it was wrong in three ways at once (count, trackedness,
permanence).
