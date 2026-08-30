# STATE

## Current

- feature: FEAT-38-decisions-current-knowledge
- run: none — the replan closed at the operator's signature gate
- squad: none
- status: **Plan**. The amended BRIEF and plan are drafted, reviewed, simplify-flagged and
  pending **ONE fresh operator signature**. No build, no PR, no merge, no ship.

The artifacts to read are `BRIEF.md` and `plan.yaml` themselves, both amended in place on
2026-08-29 for the operator's ruling that the executable-claims mechanism is DELETED, not
redesigned. `notes/handoff-plan.md` is the working memory for whoever picks this up.
`notes/ship-review-2026-08-29-18.md` is still accurate about what was BUILT before the ruling;
its recommendation to ship stays superseded.

Branch `feat/FEAT-38-decisions-current-knowledge`. `review_sha` still reads `48bbe7e` and is
**stale** — it pins the superseded validate phase and must be re-pinned before any future panel.

**Blocking on the main session, two acts and one signature.** (1) Reset both approval fragments
to `pending` — `plan.yaml:6-9` and `BRIEF.md`'s `## Approval`. Both still read `approved` and
that signature covers the PRE-RULING scope. No agent in this flow may write them:
`.harness/team-config.yaml:19-25` grants those fragments to the main session alone (DEC-120).
(2) Take the fresh signature, which covers in one act the deletion scope, REQ-08/SC-09 retired
as tombstones, REQ-10 and SC-14..SC-18, the two-task merge into T-24, and all three previously
signed `verify:` corrections (T-10 at `plan.yaml:877`, T-15 at `:1223`, T-19 at `:1437`).

**Measured harness defect, load-bearing for act 1:** `check-domain.sh`'s `approval_guard` FAILS
OPEN inside a worktree. `_verdict["rel"]` there carries the `.claude/worktrees/…` prefix and does
not `fnmatch` the grant glob `.harness/*/features/*/plan.yaml`, so the denial never fires. The
identical `harness-pm` payload exits **2** in the main checkout and **0** in this worktree. The
rule was honoured here by instruction, not by enforcement.

**The plan.** 23 tasks are `done` and committed at `48bbe7e`; six new tasks were authored and one
of them retired into another during the fix cycle, giving **28 tasks**. The retired number is
never reused; the merge and its measured cause are recorded in T-24's own `intent:`.
`check-plan-routes.py <feature-dir>/plan.yaml` exits 0 with 0 violations; the two `DEVIATION`
lines on T-22/T-23 predate this amendment. The `contains`/`max_lines` redesign is rejected and
appears nowhere (0 occurrences). `check-decision-anchors.py` (T-17) is retained unchanged. The
class audit of the rest of `bin/` is in scope as T-29.

**Budget: cycles 14 of 10; runs 24 of an informational 20.** `max_total_cycles` stays 10 and was
not altered. `cycles_used` moved 11 → 14: one lead-internal send-back in run 20, one fix cycle
routed after runs 21 and 22 both returned FAIL, and one bounded correction cycle in run 24. It is
incremented rather than frozen because DEC-157 counts rework and rule 15 forbids a flattering
record. Each replan run earned its place — run 20 drafted, runs 21 and 22 each found a measured
high-severity defect the draft would otherwise have shipped, run 23 applied all four fixes, and
run 24 removed a stale self-quotation from a task intent the operator reads at signature.

GitHub mirror: milestone 31, parent #935 at the Plan station, sub-issues #936–#958. The five new
tasks have no sub-issue yet — `gh-sync.py open` mints them after the signature. No card was moved
by this run.

## Open Questions

Blocking on the operator before the signature:

- **Numbering.** REQ-08 and SC-09 are retired in place as tombstones, so the live sets are
  non-contiguous. The alternative, renumbering, silently repoints citations in landed artifacts.
- **`traces: []`** on T-20 and T-21 — the honest statement that no LIVE requirement is served by
  work being removed. Accept an empty traces list in a signed plan, or require a tombstone id?
- **SC-11 and SC-13** were graded before the removal was in scope. Re-run the per-entry read-back
  and the UAT over the six entries T-27 touches, or does deleting a marker without touching prose
  leave them standing?
- **Cycle headroom for the build.** `max_total_cycles` is 10 and `cycles_used` is 14, so the
  build phase would start already exhausted. Raising the bound is the operator's act, recorded in
  `feature.json`; I did not presume it.
- **T-24's blast-radius sweep stays unscoped**, so the code lane waits on the documentor lane
  (T-27). Recorded as deliberate in both intents, with the alternative and its cost.

Not blocking, carried up from the squads: whether DEC-205 needs positive guidance on what an
entry does instead of carrying a checkable claim (ruled out of T-28 on weakest-sufficient-
specification); whether the accepted semantic-rot gap is filed as a backlog issue or left unfiled
as the grilling left it; whether T-03's intent should say plainly that its sixth rule survives
naming one check rather than two, which reads correctly but densely; and a harness defect —
`check-plan-routes.py:397` raises an unhandled `IsADirectoryError` when handed a feature directory
rather than the plan file, which reads as a gate failure rather than a bad argument.

**INV-26 now reports 23 cards at Review whose tasks read `done`.** The replan moved the feature
back to Plan while the landed tasks' cards stayed where the validate phase left them. Nothing in
this run moved a card and nothing should have: the Done station is written by `gh-sync.py ship`
and the Plan phase's own station writes belong to the main session.

Backlog rows B-1…B-23 remain in `notes/ship-review-2026-08-29-18.md`. The ruling settles four
without an issue being filed: **B-8 and B-11 MOOT**, **B-10 SUPERSEDED**, and **B-9 absorbed
into the plan as T-29** rather than filed.
