# STATE

## Current

- feature: FEAT-38-decisions-current-knowledge
- run: .harness/harness/features/FEAT-38-decisions-current-knowledge/runs/2026-08-29-05-product/state.yaml
- squad: product
- status: Building — 7 of 23 tasks done, deletion batch (T-05, T-07) in flight

The operator signed both artifacts and the signature is committed at `1371027`. `base_sha` for this
feature is **`7ebfc9e`** — every "measured at 7ebfc9e" figure in the plan is measured there, and
`DECISIONS.md` was byte-identical from `7ebfc9e` through the build base. GitHub mirror is open:
milestone 31, parent **#935**, sub-issues #936–#958 for T-01..T-23.

**Landed and committed.** Eng segment A at `204b469` (T-06 generator supersession removal + refs
filter, T-17 anchor-rot checker). Product segment B1 at `57a3bf3` (T-01 DEC-188 retention clause
struck, T-02 front-matter mandate rewritten, T-03 **DEC-205** authored, T-04 DEC-140 deleted, T-15
documentor P-01 rewritten). Every verify block was re-run at the orchestrator's own tier, not taken
on the lead's word.

**Squad split, which the plan does not state.** `harness-documentor` is a PRODUCT-squad persona, so
the 12 documentor tasks are product segments and only the 8 backend-dev/dev-ops tasks are eng. A
build team is eng-only by DEC-118. Remaining segments: **B2** T-05, T-07 (deletions, in flight);
**B3** T-08, T-09 (the folds); **C** eng T-20, T-10, T-12, T-13, T-18, T-19; **D** product T-16,
T-21, T-11. Then qa, SIMPLIFY, `review_sha` pin, panel, goal-check.

**Three tasks are `main-session-direct` and cannot be dispatched to any squad**: T-14 (sweeps 13
ungranted surfaces; SC-04 depends on it), T-22 (the per-entry read-back; SC-11's evidence) and T-23
(closes issue 448). They are carved out for the main session and named in the ship briefing.

Cycles used 1 of 10 — unchanged through the build so far; no send-back has been reported. Runs 4 of
an informational 20.

## Open Questions

- **Q1 (blocking the plan's integrity, not the build).** T-15's `verify:` as signed calls
  `check-expertise.sh` with **no argument**. The script requires a path (`check-expertise.sh:23`) and
  exits 2 without one, so the block cannot exit 0 for any file content. Measured at the orchestrator's
  tier: bare → exit 2; `check-expertise.sh "$E"` → exit 0, `OK`. The deliverable is correct; the plan
  text needs a one-token amendment, which is pm's pen and the operator's signature. Scanned the whole
  plan: T-15 is the **only** instance of this defect class. SC-12 is `verify: inspection` and does not
  route through this block, so the goal-check is unaffected.
- **Q2 (non-blocking, for the operator).** A T-06 member ran `git checkout -- <path>` on the MAIN
  checkout for `gen-decisions-index.py` and `test-gen-decisions-index.py`. Both are confirmed back at
  committed content and no stash exists, but uncommitted operator edits held there before the run
  would have been destroyed. Unknowable from inside the worktree.
- **Q3 (non-blocking, recorded so nobody re-reports it).** T-03's verify is order-dependent: its last
  clause forbids any generator error, and T-04 — sequenced after it — orphans DEC-140's index row
  until T-11 regenerates. T-03 passed when it ran; re-running it before T-11 reports that orphan and
  is not a defect.
- **Q4 (non-blocking, harness defect, carried from the plan phase).** `plan-merge.py` exits 8 on a
  brand-new `plan.yaml` whose proposal carries an `approval:` mapping. It is also ADD-ONLY (exit 7 on
  a changed value), so a task `status:` transition has no route through it at all; this run uses a
  surgical id-anchored line editor instead.
- **Q5 (non-blocking, harness defect).** A T-06 member returned an empty structured result `{}` — no
  VERDICT, no DIGEST — and the `SubagentStop` digest validator did not block it. The lead
  reconstructed the verdict from the on-disk receipt, which is exactly the inference the hook exists
  to make unnecessary.
- **Q6 (non-blocking, decided at the lead's tier in the plan phase).** The prototype gate did not fire
  and `harness-visual-designer` was not spawned: the deliverable surface is prose, a generator script
  and its tests, with no end-user interaction surface. Overridable by the operator.
