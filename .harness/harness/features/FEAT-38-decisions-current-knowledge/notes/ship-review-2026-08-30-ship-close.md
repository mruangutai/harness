# Ship review — FEAT-38, DECISIONS.md states current knowledge

**FEAT-38 is shipped.** PR #996 merged to `main`. Every gate that can be closed is closed, the
goal-check reads 17 of 17 live criteria met, and SC-13 — the one thing that ever blocked this — was
answered by you, not by an agent. Nothing outstanding gates the merge. What is left for you is one
decision: which of three carried defects become backlog issues.

**How this briefing was assembled.** No report round was spawned; that would buy a re-narration of
files already on disk. I read the run digests directly:
`runs/2026-08-29-qa-ship-validator/digest.md`, `runs/2026-08-29-18-panel-ship-validator/digest.md`,
`runs/goalcheck-ship-product/digest.md`, `runs/2026-08-29-simplify-ship-eng/digest.md`, plus
`notes/uat-FEAT-38.md` and this feature's `STATE.md`. Those are the sources; anything not in them is
not in here.

## What shipped

`DECISIONS.md` recorded what *was* true, in layers — a decision, then amendment blocks correcting
it, sometimes a third correcting the second. Readers had to date-sort the file in their heads.
It now holds live decisions only, each stating current truth in its own voice.

- All `am.N` amendment sub-sections folded in and deleted. A claim that was measured false survives
  as a clause of current truth, so nothing already disproved gets re-proposed. Git holds the history.
- 15 entries deleted: the 7 struck ones with a named successor, and the 8 superseded ones. DEC-90 is
  the recorded exception and keeps its strike record — its successor is a SPEC section.
- The append-only mandate in the file's own front matter is gone, with the `SUPERSEDED BY` markers
  and the index generator's handling of them.
- One mechanical check installed: `check-decision-anchors.py`, which catches a `file:line` anchor
  that no longer resolves. Deliberately the only one.
- The executable-claims mechanism is **deleted, not redesigned**, per your 2026-08-29 ruling.

`DECISIONS.md` 7414 → 6272 lines. Size was never a goal.

## Where each squad landed

| Squad | Result | Digest |
|---|---|---|
| eng — build | 28 of 28 tasks `done`, in `depends_on` order, each verified against the signed plan's own `verify:` | `runs/2026-08-29-t25-eng/digest.md` and the numbered eng runs |
| eng — SIMPLIFY | PASS. One real find applied: dead 3-tuple/title surface orphaned by T-10. Suite green, generator output byte-identical | `runs/2026-08-29-simplify-ship-eng/digest.md` |
| validator — qa | **PASS, and this is the only blocking gate.** `matrix_ok: true`, `must_fix: []`, suite exit 0, zero `FAIL` lines, 55 of 55 registered scripts actually ran | `runs/2026-08-29-qa-ship-validator/digest.md` |
| validator — panel | PASS at the pin. `severity_max: low`, no `must_fix`. Four reviewers plus an SC-11 seam check | `runs/2026-08-29-18-panel-ship-validator/digest.md` |
| product — goal-check | 15 of 16 met at the time; the 16th was SC-13, and pm correctly refused to grade it met | `runs/goalcheck-ship-product/digest.md` |

**The panel's one substantive finding is worth your attention because of what it demonstrates.** It
was an instance of the exact defect class this feature accepted losing detection for — a citation
that still resolves and no longer says what the citing code claims — and it was caught by a human
reading a diff, which is the compensating control the brief names. The removal trade working as
signed, not a hole in it.

## SC-13 — your answer, and its scope

You read DEC-138, DEC-174 and DEC-181 in full and marked each `pass. true today`, and answered the
cross-cutting question `pass — nothing considered settled has disappeared`. Recorded at
`notes/uat-FEAT-38.md`, 2026-08-30.

Two things about that record deserve saying plainly:

1. **The verdict history is kept, not overwritten.** You first instructed `failed` before the
   entries had been read through, then reversed it on reading them. A verdict that changed is a fact
   about the review, and flattening it would falsify the record.
2. **The pass is scoped, and the file says so.** It asked one question — does each entry read as
   current truth. It did **not** ask whether an entry is a decision at all, whether it is in clause
   form, or whether it carries one ruling or nine. FEAT-46 sets that standard, and all three entries
   are in scope for its triage: DEC-181 is 100% prose, DEC-138 carries 11 independent rulings and
   DEC-174 carries 7. This pass must never be cited to exempt them.

There was one process failure here, and it was mine, recorded rather than smoothed: an earlier
`STATE.md` asserted SC-13 stood and did not return to you. It restated a dispatch premise instead of
checking the file. pm's goal-check caught it at source.

## Proposed backlog — strike any row you do not want filed

**Anything you strike dies silently, so all three are listed.** None of them gates anything.

| ID | Nature | Finding |
|---|---|---|
| B-25 | bug | `bash-write-guard.sh` cannot expand shell variables and does not track `cd`. It resolves targets against the session root, so `cd <dir> && sed -i '' … plan.yaml` and `sed -i '' … "$P"` are denied "outside your domain" while the identical command with a literal absolute path is allowed — and `check-domain.sh --resolve` grants that same path. Two enforcement surfaces disagree |
| B-26 | bug | `/usr/bin/grep` on this machine is `pi-uu-grep 0.2.0`, in which a line-leading `+` matches every line. Four false readings in this feature, including an apparent 83 insertions against a true `--numstat` of zero. Every affected measurement was redone in Python |
| B-39 | bug | A run-directory slug collision let one lead overwrite another run's `digest.md` and `state.yaml`. `runs/` is gitignored, so the record was unrecoverable. Nothing in the run-directory contract stops a lead choosing a slug that already exists |

## Open, recorded, and not proposed as backlog

- **Bare relative paths resolve against the outer checkout, not the assigned worktree.** Measured
  three times in one panel. Two review artifacts are still stray, untracked, in the main checkout;
  byte-identical copies were recovered into the feature tree. Removing the originals is yours — an
  agent does not touch that checkout.
- **DEC-205 names two refused rot detectors but not what compensates today.** The answer lives only
  in `BRIEF.md`. The remedy would add positive content to DEC-205, which your ruling forbids. Your
  call, not a squad's.
- **A stale prose reference SC-18 forbids fixing**: `check-decision-anchors.py`'s docstring still
  calls the snippet problem "a different tool"'s job. Pre-existing, and SC-18 pins that file
  byte-identical to `99bb52c`.
- **The `bin/` argv class is not empty** — 11 of 70 scripts build argv from a parsed value, recorded
  in two risk groups under REQ-10's reconciliation. Not this feature's destination.

## Budget, stated because it crossed

Cycles **16 of 30** — a hard bound, not crossed. Two rework cycles in the whole feature: the panel's
SC-11 seam send-back and the UAT repoint.

Runs **34 of an informational 20**. That budget notices a long feature; it never stops one, and I am
not apologising for it. These runs earn their place: they closed the entire build, both gates, the
goal-check and the UAT, and every run but two returned PASS first-pass. The count is a floor anyway —
orchestrator-held segments like this one are not runs and never appear in it.

## What happens next

- The worktree is safe to remove; removal is yours or the post-merge hook's, never an agent's from
  inside it.
- FEAT-46 was held pending this ship and is now unblocked. It inherits the scope note above.
