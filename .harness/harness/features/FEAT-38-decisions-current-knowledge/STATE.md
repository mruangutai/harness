# STATE

## Current

- feature: FEAT-38-decisions-current-knowledge
- run: `2026-08-30-ship-close-orchestrator` — the ship closing sequence
- squad: none. Orchestrator-held; no lead was dispatched in this run
- status: **Done**, PR **#996**, merged to `main`

**SC-13 IS ANSWERED AND THE SHIP IS AUTHORISED.** The previous `## Current` recorded SC-13 as the
one blocking item, unrun. It is now `status: passed` in `notes/uat-FEAT-38.md`, answered by the
operator on 2026-08-30 on their own reading of DEC-138, DEC-174 and DEC-181 — each marked
`pass. true today`, and the cross-cutting question answered `pass — nothing considered settled has
disappeared`. The file keeps the verdict history rather than overwriting it: an initial `failed`
instruction was reversed by the operator after reading the entries, and a verdict that changed is a
fact about the review. **The pass is scoped** — it asked only whether each entry reads as current
truth, never whether an entry is a decision at all or is in clause form. FEAT-46 sets that standard
and all three entries are in scope for its triage; this pass must never be cited to exempt them.

**The goal-check is 17 of 17 live criteria met.** Both closable gates were closed before this run
and neither was re-run here: the blocking qa gate PASSES (`matrix_ok: true`, `must_fix: []`, suite
exit 0, all 55 registered scripts run) and the four-reviewer panel PASSES at the pin with
`severity_max: low` and no `must_fix`.

**`review_sha` `635cd3ba` was still valid at the merge and was NOT re-pinned.** Verified by name
rather than assumed: 16 files changed between the pin and the tip `d04be92`, of which 13 are under
this feature's own directory and the other three are `.harness/logs/2026-08-29.md`,
`.harness/logs/2026-08-30.md` and `.harness/notes/grilling-decision-standard-2026-08-30.md`. Zero
source files, so the panel's verdict still describes the code that merged.

**The close, in order.** Branch pushed (it had never been pushed); PR #996 opened with a body
stating what shipped, the pin, the operator's SC-13 answer and the three carried defects; `pr` and
the terminal status recorded through `gh-sync.py record-pr` rather than by hand; this state and the
handoff committed so they land on `main` with the merge; merged; `gh-sync.py ship` for the board.

**Budget at close: cycles 16 of 30; runs 34 of an informational 20.** Neither moved in this run —
no rework, and this orchestrator-held segment is not a squad run, so nothing was added to `runs`.
`len(runs)` passed `max_total_runs` long ago; the count is informational, it stops nothing, and
these runs earn their place: they closed the whole build, both gates, the goal-check and the UAT.

## Open Questions

**Blocking: none.** SC-13 was the last one and it is closed.

**Carried to the operator as proposed backlog** in `notes/ship-review-2026-08-30-ship-close.md`.
Anything not accepted there dies silently, so all three are listed:

- **B-25 — `bash-write-guard.sh` cannot expand shell variables and does not track `cd`.** It
  resolves targets against the session root, so `cd <dir> && sed -i '' … plan.yaml` and
  `sed -i '' … "$P"` were both denied "outside your domain" while the identical command with a
  literal absolute path was allowed — and `check-domain.sh --resolve` grants `plan.yaml` to
  `harness-orchestrator`. Two enforcement surfaces disagree.
- **B-26 — `/usr/bin/grep` is `pi-uu-grep 0.2.0`, in which `^+` matches EVERY line.** Four false
  readings across this feature, including an apparent 83 insertions against a true `--numstat` of
  zero. Every affected measurement was redone in Python.
- **B-39 — a run-directory slug collision destroyed a record.** The T-27 lead wrote into
  `runs/2026-08-29-01-product`, already the panel-revision run's directory, overwriting its
  `digest.md` and `state.yaml`. `runs/` is gitignored, so it was never in git and is unrecoverable.
  Artifacts were relocated to `runs/t27-product/` and a tombstone left. Nothing in the
  run-directory contract stops a lead choosing a slug that already exists.

**Recorded, not proposed as backlog — they belong to work already scoped elsewhere:**

- **Bare relative paths resolve against the OUTER checkout, not the assigned worktree.** Two review
  artifacts were written into the main checkout and are still stray, untracked, there.
  Byte-identical copies were recovered into this tree; removing the originals is the operator's.
- **A stale prose reference SC-18 forbids fixing**: `check-decision-anchors.py`'s docstring still
  calls the snippet problem "the executable-claims checker's job (a different tool)". Pre-existing,
  not introduced, and SC-18 pins that file byte-identical to `99bb52c`.
- **DEC-205 names two refused rot detectors but not what compensates today** — the answer lives only
  in `BRIEF.md`. The remedy would add positive content to DEC-205, which the ruling forbids.
- **The `bin/` argv class is NOT empty**: 11 of 70 scripts build argv from a parsed value, recorded
  as remaining work in two risk groups. Backlog under REQ-10's reconciliation, not this feature.
- **SC-04's pinned baseline `37` for `am.N` does not reproduce** (34 occurrences / 31 lines) while
  its `30` and `24` reproduce exactly. Every pattern is 0 at the pin, so intent is met.
- Non-blocking Q6..Q10 from the plan phase remain open and gate nothing. REQ-08 and SC-09 are
  retired tombstones, graded by nobody.
