# FEAT-38 — DECISIONS.md states current knowledge

`DECISIONS.md` recorded what *was* true, in layers: a decision, then amendment blocks correcting it,
sometimes a third correcting the second. Every reader had to date-sort the file in their head.
This lands the file as live decisions only, each stating current truth in its own voice.

## What shipped

- **All amendment layering is gone.** The `am.N` sub-sections are folded into their decisions and
  deleted; a claim that was measured false survives as a clause of current truth, in the document's
  own voice, so nothing already disproved gets re-proposed. Git holds the history.
- **15 entries deleted** — the 7 struck entries with a named successor (DEC-103, 104, 137, 140, 186,
  192, 196) and the 8 superseded ones (DEC-19, 20, 37, 67, 82, 88, 92, 102). DEC-90 is the recorded
  exception and keeps its strike record: its successor is a SPEC section, not a decision.
- **The append-only mandate in the file's own front matter is removed**, along with the
  `SUPERSEDED BY` markers and the index generator's handling of them.
- **One mechanical check installed** — `check-decision-anchors.py` (+ its test), which catches a
  `file:line` anchor that no longer resolves. Deliberately the only one.
- **The executable-claims mechanism is deleted, not redesigned**, per the operator's ruling of
  2026-08-29. A non-executing declarative replacement was put to them in full and rejected. The
  accepted cost is recorded rather than hidden: a cited line that still exists but no longer says
  what the entry claims is now caught by a human reading a diff, or not at all.

`DECISIONS.md` 7414 → 6272 lines. Size was never a goal; it is a consequence of stating current
truth. 147 files, +17524 / −2235 against merge-base `7a23d74`.

## Verification

- **`review_sha` = `635cd3baa950e7a48eaad9c3a1990560b61bf7c0`.** The four-reviewer panel graded that
  exact tree: `severity_max: low`, no `must_fix`. Everything committed after the pin is feature
  notes, logs, `STATE.md`, `feature.json` and observation logs — zero source files — so the pin
  still describes the code being merged.
- **qa gate PASS** (the project's only blocking gate): `matrix_ok: true`, `must_fix: []`, suite
  exit 0, zero `FAIL` lines, all 55 registered scripts run.
- **Goal-check: 17 of 17 live criteria met.**
- **SC-13 was answered by the operator**, not by an agent — `notes/uat-FEAT-38.md`, 2026-08-30.
  They read DEC-138, DEC-174 and DEC-181 in full and marked each `pass. true today`, and answered
  the cross-cutting question `pass — nothing considered settled has disappeared`. The file keeps
  the verdict history rather than overwriting it: an initial `failed` instruction was reversed by
  the operator on their own reading. That reversal is a fact about the review and is recorded as one.
  **The pass is scoped:** it asked only whether each entry reads as current truth. It did not ask
  whether an entry is a decision at all, is in clause form, or carries one ruling or nine. FEAT-46
  sets that standard and all three entries are in scope for its triage — this pass must never be
  cited to exempt them.

## Carried forward as backlog, not fixed here

Three platform defects found during this feature. None gates this merge; all three are recorded so
they are not rediscovered.

- **B-25 — write-guard divergence.** `bash-write-guard.sh` cannot expand shell variables and does
  not track `cd`, so it resolves targets against the session root: `cd <dir> && sed -i '' … plan.yaml`
  and `sed -i '' … "$P"` are both denied "outside your domain" while the identical command with a
  literal absolute path is allowed — and `check-domain.sh --resolve` grants that same path. Two
  enforcement surfaces disagreeing.
- **B-26 — `/usr/bin/grep` on this machine is `pi-uu-grep 0.2.0`**, in which a line-leading `+`
  pattern matches every line. It produced four false readings in this feature, including an apparent
  83 insertions against a true `--numstat` of zero. Every affected measurement was redone in Python.
- **B-39 — the digest-contract gap.** A run-directory slug collision let one lead overwrite another
  run's `digest.md` and `state.yaml`; `runs/` is gitignored, so the record was unrecoverable.
  Nothing in the run-directory contract stops a lead choosing a slug that already exists.

## Approval trail

BRIEF `status: approved`; `plan.yaml` `approval.status: approved` on its third signature (the
adversarial panel's revision). 28 planned tasks, all `done`. Cycles 16 of 30.
