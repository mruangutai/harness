# Operator rulings before signature — FEAT-1559 — 2026-10-04

Given by mruangutai in the main session after the plan-product run (ESCALATE) and an independent
fable-advisor review (history://AdviseFEAT1559).

1. **PF-5e51b4e6 (repair safety vs merge convergence): classify by content.** `--repair` sorts
   every status entry into three classes:
   - (A) outside the target cone, absent from the working tree, index entry == HEAD → pure sparse
     debt; set skip-worktree, touch no bytes;
   - (B) outside the cone, present, byte-identical to the index → remove;
   - (C) any content divergence (modified, staged index != HEAD, deletion inside the cone, untracked
     files inside hidden feature dirs) → refuse with exit 8, mutate nothing.
   "Dirty" in SC-07 means class C. An unstaged deletion of a hidden feature's file is class A by
   design: the write is forbidden cross-feature anyway, and the bytes remain in index/HEAD.
   Provenance markers are rejected.
2. **Fresh-id ordering: checkout identity.** When no artifact segment holds a record for the id,
   the active id comes from checkout identity (worktree dir id, `feat/<id>` branch, or pin name).
   The cone excludes every `.harness/*/features` and re-adds `.harness/*/features/<id>` in all
   segments. No creator edits (D-10 intact); covers bare `git worktree add`. Ambiguity (id
   claimed by several segments, or identity underivable) keeps the existing refusal. T-01's
   "do not infer from the worktree segment" still governs segment selection for existing records.
3. **Q-01 (FEAT-57 replay prerequisite): superseded.** FEAT-57-review-latency was abandoned (#1655
   closed, label `abandoned`), so there is no receipt to wait for and no T-19 to serialise against.
