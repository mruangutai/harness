# STATE

## Current

- feature: FEAT-10-software-factory
- mission: ship — phase `ship`. **Every gate is green and the work is committed.** What remains is
  the operator's acceptance, which is the only thing that can close this feature.
- status: awaiting_user. **A1 is fixed, committed and re-pinned.** The four blocking questions the
  last segment raised are all ruled and closed; one non-blocking question survives to the ship call.
- HEAD is `b86565b` — `[harness:t-04] A1 closed`. Not pushed, no PR: both the operator's.

- **THE FOUR RULINGS ARE APPLIED, EACH IN THE FILE THAT OWNS IT.** `max_total_cycles` is 12 in
  `feature.yaml` with the DEC-157 record naming `notes/answers-a1fix-eng.md` as the decision;
  `declared_widening.status` now reads RESOLVED and `plan.yaml` was not touched; the panel2
  worktree-edit disclosure is accepted with nothing filed; `review_sha` is `b86565b` with base
  **deliberately unmoved** at `f9488a2` so every panel2 line citation keeps its range.

- **THE COMMIT IS BY EXPLICIT PATHSPEC, AND ONE FILE WAS LEFT OUT ON PURPOSE.** `b86565b` carries
  `factory_decompose.py`, `test-factory-decompose.py` and the five notes.
  `.harness/logs/2026-08-09.md` is still dirty: its twelve added lines are the main session's own
  record — the bf8f191 measurements, #203 and #204 — and I cannot verify those claims, so signing
  them into my commit would be the wrong trade. It is the operator's to commit.
  `check-state.sh` and `test-check-state.py` were never opened for edit and are in no commit.

- **THREE GATES RE-MEASURED BY ME AT THE SETTLED TREE, BEFORE THE COMMIT, NOT INHERITED.**
  `run-unit-tests.sh` exit 0 — **22 test files PASS, 0 FAIL** (the 22 is FILE-level; a bare
  `grep -c "^PASS"` returns 85 by counting sub-case lines). `check-docs.sh` exit 0 — 62 patterns
  across 317 files. `check-state.sh` exit 0 — **zero violations**, only notes, including the
  expected INV-22. Both checkers were re-run AFTER the last write, not before it.

- **ADVANCING THE PHASE TO `ship` EXPOSED A REAL GAP, AND I CLOSED IT RATHER THAN REVERTING.**
  INV-17 fired two VIOLATIONs: the build and validate seams were each crossed with **no handoff
  note**, so every successor lost its predecessor's working memory. That is true and it happened.
  `notes/handoff-build.md` and `notes/handoff-validate.md` now exist, each labelled RECONSTRUCTED
  AT FEATURE CLOSE in its own opening lines so the loss is recorded permanently instead of erased,
  and each priced claim-by-claim with `verified-at b86565b` or `UNVERIFIED`. Reverting the phase to
  `build` would have hidden it; leaving it red would have left the operator a paperwork failure on
  ship day with no note to show for it.

- **ONE OPEN QUESTION CLOSED BY MEASUREMENT RATHER THAN BY ASKING.** The last segment asked the
  operator to confirm whether panel2's security low was among bf8f191's "four INV-24 defects". It
  is. I read that commit's own diff: the new guard's comment cites **"panel2 C1"** by name and
  describes the exact fail-open — a `repos:` entry with no `name` putting `None` in the allow-list
  so `factory.repo: null` matched it — and adds both an `isinstance` filter and a `factory.repo`
  type check. Closed, not carried.

- **CLOSE-OUT: SHIP-REFRESH SKIPPED ON A MEASUREMENT, DISTILLATION SKIPPED ON A JUDGEMENT.** No
  codebase map exists — `find . -name INDEX.md` returns nothing — so the union of `files_touched`
  intersects no map domain and ship-refresh is zero dispatches. Distillation is deliberately NOT
  run: DEC-145 puts it after ship, and this feature is returning **for** the ship decision with Q5
  still open. Distilling a run the operator may reopen writes Expertise hot, which is the failure
  DEC-145 exists to prevent. The operator can overrule and it costs three lead dispatches.

- **THE BRIEFING WAS ASSEMBLED FROM DISK, NOT FROM A REPORT ROUND.** No lead was spawned to
  re-narrate. All **31** run digests under `runs/*/digest.md` were read directly, including the
  plan and build phases this segment did not run. Paths are cited in the briefing itself.

- budget: **12 of 12 — RAISED BY THE OPERATOR, AND NOW AT ZERO HEADROOM.** Any rework ordered from
  here exhausts a hard bound and the next orchestrator returns BLOCKED rather than working it.
- runs: 31 of 20, informational (INV-22). The last four each found or closed a defect that would
  otherwise have shipped.
- briefing: `notes/ship-review-ship-2026-08-09.md`, with its rendered `.html` sibling.

## Open Questions

- **NON-BLOCKING, AND THE ONE THE SHIP CALL TURNS ON · the A1 fix is verified against the STUB
  ONLY.** The operator's one-character station typo is the only thing that ever reproduced A1
  outside a test, and it has not been re-run against a real board. It needs a throwaway repo and a
  fresh board, which is the operator's to authorize; the last one required a `delete_repo` scope
  refresh to clean up. Carried deliberately (answers-a1fix-eng.md Q5) — recommended before ship,
  required by no signed criterion.
- NON-BLOCKING · `.harness/logs/2026-08-09.md` is dirty and deliberately uncommitted. Reasons above.
- NON-BLOCKING · **deleting `wip-omp-and-feat10-mixed` kills every panel2 line citation** — the old
  pin `8bbb246` survives nowhere else. The new pin's range `f9488a2..b86565b` also sweeps in
  `c5597be` (the wayfinding door), which is not this feature's work; `bf8f191` in the same range
  IS in scope, since T-08 is a FEAT-10 task.
- NON-BLOCKING · eleven panel2 advisory findings survive undispatched, plus panel1's carried F3 and
  F7. Each is a proposed backlog row in the briefing with an id the operator can strike by name.
- NON-BLOCKING · `plan.yaml:1435` still records T-08 `status: pending`. Stale; pm's to fix, and it
  is the only plan-level correction this feature still owes.
- NON-BLOCKING · issue #199, **seventh recurrence**: the receipt path `harness-handoff` prescribes
  is denied to most personas by `check-domain.sh`. Hit again by this feature's a1fix segment.
- NON-BLOCKING · all three commits in the OLD review pin were unattributed (`2a3e91c`, `b89c00a`,
  `8bbb246`). `bf8f191` and `b86565b` both carry trailers, so the gap is historical.
- HARNESS QUESTION, demonstrated twice on this feature: should a review panel — or any segment —
  run against a working checkout another process can move under it? panel2 hit it as a moving HEAD,
  a1fix-eng hit it as `check-state.sh` changing mid-run. A worktree at the pin is free both times.
