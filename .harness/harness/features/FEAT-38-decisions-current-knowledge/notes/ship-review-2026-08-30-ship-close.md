# Ship review — FEAT-38, DECISIONS.md states current knowledge

**FEAT-38 did not ship, and the reason has nothing to do with the feature.** Every gate it owns is
green, the goal-check reads 17 of 17 live criteria met, and SC-13 — the one thing that ever blocked
this — was answered by you. PR **#996** is open. It **cannot merge**: the branch conflicts with
`origin/main` in three files, because **FEAT-44 shipped while FEAT-38 was in flight** and edited the
same three. Nothing was faked to get past it. No board card was moved, milestone 31 is still open,
and `gh-sync.py ship` was never run — writing `Done` for work that did not merge would corrupt the
record every other part of the factory reads.

**Two decisions are yours: how the conflict gets resolved, and which of three defects become
backlog issues.**

## The blocker, measured

The premise this run was handed — *0 commits behind `main`* — was true and misleading. It was
measured against your **local** `main`, which is itself **2 ahead and 19 behind `origin/main`**.

| Measurement | Result |
|---|---|
| `main...HEAD` | `0 52` — the branch did merge local `main`, at `d04be92` |
| `main...origin/main` | **`2 19`** — local `main` is stale and divergent |
| `origin/main...HEAD` | **`19 55`** — real merge-base is `7ebfc9e`, the feature's original base |

The 19 upstream commits are **FEAT-44** (the OMP-native context advisory, PRs #982 and #995).
Three files conflict:

- `.claude/skills/harness/bin/run-unit-tests.sh` — both features registered new test scripts
- `.harness/harness.json` — both edited `test_kinds`
- `.harness/harness/docs/DECISIONS-INDEX.md` — **generated**; FEAT-44 regenerated it after amending
  DEC-198, DEC-201 and DEC-159. It should be regenerated, never hand-merged.

**`DECISIONS.md` itself auto-merges cleanly.** The feature's actual subject matter does not conflict
with anything.

**Why an agent did not just fix it.** Resolving needs `origin/main` merged into the branch — a HEAD
move the write guard refuses for every governed agent, correctly, because HEAD is shared state.
And the resolution edits source files that sit under the review pin, so `review_sha` `635cd3ba`
would stop describing the merged tree. That makes it a validate cycle, not a closing step:
re-pin, re-run the blocking qa gate. The four-reviewer panel does not need re-running unless that
qa run finds something — it returned `severity_max: low` with no `must_fix`, and `gates.review` is
advisory.

**One thing to decide deliberately:** because the branch merged your local `main`, PR #996 currently
**carries the two unpushed FEAT-46 commits** (`16f86e3` grill, `7a23d74` hold). Nobody intended
FEAT-46 material to ride this PR.

## What is finished, and stays finished

**How this briefing was assembled.** No report round was spawned; that would buy a re-narration of
files already on disk. I read the run digests directly:
`runs/2026-08-29-qa-ship-validator/digest.md`, `runs/2026-08-29-18-panel-ship-validator/digest.md`,
`runs/goalcheck-ship-product/digest.md`, `runs/2026-08-29-simplify-ship-eng/digest.md`, plus
`notes/uat-FEAT-38.md` and this feature's `STATE.md`.

`DECISIONS.md` recorded what *was* true, in layers — a decision, then amendment blocks correcting
it, sometimes a third correcting the second. Readers had to date-sort the file in their heads.
On this branch it now holds live decisions only, each stating current truth in its own voice:
all `am.N` sub-sections folded in and deleted, 15 entries removed (7 struck with a named successor,
8 superseded; DEC-90 the recorded exception), the append-only mandate and the `SUPERSEDED BY`
markers gone, one mechanical anchor check installed, and the executable-claims mechanism **deleted,
not redesigned**, per your 2026-08-29 ruling. 7414 → 6272 lines; size was never a goal.

| Squad | Result | Digest |
|---|---|---|
| eng — build | 28 of 28 tasks `done`, in `depends_on` order, each verified against the signed plan's own `verify:` | the numbered eng runs |
| eng — SIMPLIFY | PASS. One real find applied: dead 3-tuple/title surface orphaned by T-10. Suite green, generator output byte-identical | `runs/2026-08-29-simplify-ship-eng/digest.md` |
| validator — qa | **PASS, and this is the only blocking gate.** `matrix_ok: true`, `must_fix: []`, suite exit 0, zero `FAIL` lines, 55 of 55 registered scripts actually ran | `runs/2026-08-29-qa-ship-validator/digest.md` |
| validator — panel | PASS at the pin. `severity_max: low`, no `must_fix`. Four reviewers plus an SC-11 seam check | `runs/2026-08-29-18-panel-ship-validator/digest.md` |
| product — goal-check | Graded 15 of 16 met and correctly refused to grade SC-13 met; with SC-13 now answered it is 17 of 17 live criteria | `runs/goalcheck-ship-product/digest.md` |

**The panel's one substantive finding is worth your attention for what it demonstrates.** It was an
instance of the exact defect class this feature accepted losing detection for — a citation that
still resolves and no longer says what the citing code claims — and it was caught by a human reading
a diff, which is the compensating control the brief names. The removal trade working as signed.

## SC-13 — your answer, and its scope

You read DEC-138, DEC-174 and DEC-181 in full and marked each `pass. true today`, and answered the
cross-cutting question `pass — nothing considered settled has disappeared` (`notes/uat-FEAT-38.md`,
2026-08-30). Two things about that record deserve saying plainly:

1. **The verdict history is kept, not overwritten.** You first instructed `failed` before the
   entries had been read through, then reversed it on reading them. A verdict that changed is a fact
   about the review, and flattening it would falsify the record.
2. **The pass is scoped, and the file says so.** It asked one question — does each entry read as
   current truth. It did **not** ask whether an entry is a decision at all, whether it is in clause
   form, or whether it carries one ruling or nine. FEAT-46 sets that standard, and all three entries
   are in scope for its triage: DEC-181 is 100% prose, DEC-138 carries 11 independent rulings and
   DEC-174 carries 7. This pass must never be cited to exempt them.

There was one process failure, and it was mine, recorded rather than smoothed: an earlier `STATE.md`
asserted SC-13 stood and did not return to you. It restated a dispatch premise instead of checking
the file. pm's goal-check caught it at source. This run repeated the shape once more — it wrote
`status: Done` in anticipation of a merge that then proved impossible, and reverted it.

## Proposed backlog — strike any row you do not want filed

**Anything you strike dies silently, so all three are listed.** None gates anything.

| ID | Nature | Finding |
|---|---|---|
| B-25 | bug | `bash-write-guard.sh` cannot expand shell variables and does not track `cd`. It resolves targets against the session root, so `cd <dir> && sed -i '' … plan.yaml` and `sed -i '' … "$P"` are denied "outside your domain" while the identical command with a literal absolute path is allowed — and `check-domain.sh --resolve` grants that same path. Two enforcement surfaces disagree |
| B-26 | bug | `/usr/bin/grep` on this machine is `pi-uu-grep 0.2.0`, in which a line-leading `+` matches every line. Four false readings in this feature, including an apparent 83 insertions against a true `--numstat` of zero. Every affected measurement was redone in Python |
| B-39 | bug | A run-directory slug collision let one lead overwrite another run's `digest.md` and `state.yaml`. `runs/` is gitignored, so the record was unrecoverable. Nothing in the run-directory contract stops a lead choosing a slug that already exists |

A fourth is worth considering and is **not** proposed, because it may be intentional:
`feature-worktree.py behind` exits 2 on this repository because the repository is not declared in
`fleet.yaml`. That exit is a config gap, not a behind-answer — and it is precisely why the
behind-measurement fell back to a hand-run `rev-list` against the wrong ref and missed 19 commits.

## Open, recorded, not proposed as backlog

- **Bare relative paths resolve against the outer checkout, not the assigned worktree.** Measured
  three times in one panel. Two review artifacts are still stray, untracked, in the main checkout;
  byte-identical copies were recovered into the feature tree. Removing the originals is yours.
- **DEC-205 names two refused rot detectors but not what compensates today.** The answer lives only
  in `BRIEF.md`. The remedy would add positive content to DEC-205, which your ruling forbids.
- **A stale prose reference SC-18 forbids fixing**: `check-decision-anchors.py`'s docstring still
  calls the snippet problem "a different tool"'s job. Pre-existing; SC-18 pins that file
  byte-identical to `99bb52c`.
- **The `bin/` argv class is not empty** — 11 of 70 scripts build argv from a parsed value, recorded
  in two risk groups under REQ-10's reconciliation.

## Budget

Cycles **16 of 30** — a hard bound, not crossed. Two rework cycles in the whole feature: the panel's
SC-11 seam send-back and the UAT repoint. Neither moved in this run.

Runs **34 of an informational 20**. That budget notices a long feature; it never stops one, and this
is not an apology. These runs closed the entire build, both gates, the goal-check and the UAT, and
every run but two returned PASS first-pass. The count is a floor anyway — orchestrator-held segments
like this one are not runs and never appear in it.

## What happens next

1. You or the main session resolves the conflict, re-pins `review_sha`, re-runs the qa gate.
2. Merge #996, then the board writes and milestone 31 follow — `gh-sync.py ship` does all of it.
3. **The worktree must stay** until this lands. It is not safe to remove: it holds the only checkout
   of the unmerged branch.
4. FEAT-46 stays held until then, and inherits the SC-13 scope note above.
