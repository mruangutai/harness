# Receipt — harness-data-engineer — SIMPLIFICATION angle — FEAT-30 plan.yaml

## Verdict: PASS, one low-cost finding

## What was checked
- Read `plan.yaml` in full (1058 lines): `lanes:`, D-01..D-08, T-01..T-09.
- Cross-checked every `line NNN` / `lines NNN to NNN` citation in D-02/T-03/T-04/T-05 against
  `git show eeabc59:<file>` for `harness_boundary.py`, `check-domain.sh`, `bash-write-guard.sh`,
  `test-check-domain.py`, `test-bash-write-guard.py` — all citations landed on the exact code they
  describe (WORKTREE_REL_RE line 37, worktree_owner line 355, resolve-path match line 212, `_norm`
  regex line 644, sweep-glob join line 602, dest legality lines 460-466, prefix-only rule line 545,
  parser `_ops[1]` window lines 405-427, fixture lines 1093/1160/1465-1482, mutation-proof lines
  491-506). No dead reference to a superseded shape found — everything cited still exists as
  described.
- Grepped for orphaned/renumbered ids: task ids (T-01..T-09), decision ids (D-01..D-08), REQ-01..08,
  SC-01..09 — all internally consistent, no stray id from an earlier draft (the apparent `T-30/T-31/
  T-90..93` hits are FEAT/BUG fixture ids inside prose, not task references — false positive, checked
  and dismissed).
- Checked candidate "same rule twice, could drift" pairs: D-02/T-04 on WORKTREE_REL_RE cutover
  (T-04 executes exactly what D-02 mandates, one authority — D-02); D-03/T-04 on the DEC-193
  no-git-subprocess rule (D-03 is the decision, T-04's restatement is the obligation it must satisfy
  — D-03 is authoritative, consistent, not a drift risk); D-04/T-05 on no-orchestrator-exemption
  (T-05 explicitly cites D-04 by name rather than silently duplicating it — this is a citation, not
  drift). None of these earn a finding under the "judge whether they can actually diverge" instruction.
- Confirmed the settled items hold as stated: no `<product>` spelling anywhere; REQ-08 is one
  mechanism for one mechanism in T-04 (no segment-count widening found); DEC-174 am.4 DEVIATION
  lines are present for T-03/T-04/T-05 exactly as expected; four RED-proof `verify:` blocks (T-01,
  T-03, T-04, T-05) each prove a different boundary (CLI absence, WORKTREES_SEGMENT mutation on the
  shape phase, eeabc59-regressed guard, eeabc59-regressed HEAD-move rule) — correctly not one
  finding.

## Finding (briefing row, not a feature cycle)

**`workspace_root`'s definition is spelled out in full twice, once per task intent, and the two
copies use different supporting clauses.**

- File: `plan.yaml`
- Lines: 214 (T-01) and 1028-1029 (T-09)
- T-01 line 214: "owner_root is ONE checkout. workspace_root is the CONTAINER that holds served
  repository checkouts. Never join WORKTREES_SEGMENT to workspace_root: that would put every served
  repository's worktrees in one directory..."
- T-09 lines 1028-1029: "...workspace_root is the container that holds served repository checkouts
  and is never the parent of a worktree."
- Cost: same fact (what workspace_root is) restated with different guardrail clauses (destroys
  per-repo isolation vs. never the parent of a worktree). If either invariant is refined later, an
  editor fixing T-01's copy has no structural signal to also fix T-09's, and the two doc surfaces
  (CLI intent vs. orchestrator-facing instructions) can silently diverge on what workspace_root means.
- Alternative: T-09 states the rule once, in its own voice as the instruction file requires, and
  cross-references T-01/D-01's definition by task id rather than re-deriving the definition inline —
  the same "cross-reference instead of restate" principle T-09's own closing line already applies to
  its three target files, extended one hop further to the source of the fact.
- Weight: briefing row. The two spellings do not contradict each other today and the underlying fact
  (workspace_root is the served-repo container) is simple enough that redundant restatement is low
  risk; not worth a feature cycle at 3 of 10.

## Not flagged (checked, explicitly not findings)
- The four expensive red-state `verify:` proofs (T-01/T-03/T-04/T-05) — each proves a different
  boundary, per the settled list.
- D-02/D-03/D-04 restated inside T-04/T-05 task intents — decision is the authority, task intent is
  the obligation, no divergence risk found.
- SC-06 (BRIEF, inspection-kind) not literally cited by id inside T-09 — T-09 traces REQ-05/REQ-03
  and its acceptance text matches SC-06's wording; BRIEF-level SC/REQ mapping is pm's surface, not
  mine to re-litigate.

Everything else in scope — the 8 decisions, the 9 tasks, the `lanes:` table — read consistent, with
no other double-spelled fact and no other dead reference found.
