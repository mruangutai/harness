# STATE

## Current

- feature: FEAT-38-decisions-current-knowledge
- run: `2026-08-29-01-product` — PASS, the adversarial panel's revision applied
- squad: product (`harness-pm`, via `harness-product-lead`)
- status: **Plan**. The panel revision has LANDED. The plan and brief are again
  pending **ONE fresh operator signature**. No build, no PR, no merge, no ship.

**The revision is applied and verified.** An adversarial three-reader panel graded the signed
plan at `73898a3`; the main session withdrew the signature at `753f4cd` and recorded five rulings
in `notes/answers-2026-08-29-panel.md`. All five landed in one product run:

- **F1** — T-24's blast-radius sweep was UNSATISFIABLE at its own completion. `':!.harness/harness.json'`
  added to the pathspec (`plan.yaml:1826`), and T-24's intent corrected: the sweep is no longer
  described as unscoped, and the false claim that it is the only proof no sixth reference site
  exists is replaced by the true owner, **SC-14's third assertion** graded at `review_sha`.
- **F2** — SC-11 now states its re-grade set as the **five** entries it actually reaches
  (DEC-145, 157, 181, 183, 193); SC-16 extended to cover DEC-205's considered-and-refused
  paragraph, content-anchored on `What was considered and refused` rather than on a line number.
- **F3** — REQ-10 reconciled with the grilling note's Destination in one sentence, scope unwidened.
- **F4** — SC-17's inspection routed to a code-reading persona, not the author of the audit table.
- **F5** — `SC-15` added to T-25's `traces`. T-27's `traces` deliberately untouched.

**F1 was verified by MEASUREMENT, not by argument** — the panel's own predecessor accepted a
reasoned argument here and was wrong. In a disposable clone with a real git index, at the exact
mid-state T-24 faces (T-27 landed, T-24 landed, **T-25 still pending**): the signed clause exits
**1** printing `.harness/harness.json` then `references survive`; the landed clause, extracted
from the amended `plan.yaml` via `harness_yaml.load_plan` rather than retyped, exits **0**.
Applying T-25 on top, SC-14's unscoped sweep exits **1** with no matches — the proof F1 moved to
SC-14 genuinely lands there, and `run-unit-tests.sh --check-kinds` exits 0 with both registration
sides agreeing.

**The plan is structurally unchanged.** 28 tasks; ids `T-01…T-25, T-27, T-28, T-29`; no id
renumbered, reused or added; there is still no T-26. T-01…T-23 all `status: done`, the five
remaining `pending`. `harness_yaml.load_plan` parses it. `check-plan-routes.py` exits **0** with
**0 violations** and the same two informational `DEVIATION` lines on the done tasks T-22/T-23 that
predate this amendment — identical to the pre-revision baseline. Remaining build is
T-27 → {T-24, T-28} → {T-25, T-29}: no cycle, longest chain 3.

**NEITHER APPROVAL FRAGMENT WAS WRITTEN**, and both are byte-identical to `753f4cd` — verified by
diff, not asserted. `plan.yaml`'s `approval:` reads `pending`; **`BRIEF.md`'s `## Approval` still
reads `approved`**, because the `753f4cd` withdrawal touched only `plan.yaml`. The two artifacts
therefore disagree, and only the main session may reconcile them (DEC-120). Both fragments also
still say SC-11 re-grades over the **six** entries T-27 touches, which F2a corrects to five.

`review_sha` still reads `48bbe7e` and is **stale** — it pins the superseded validate phase and
must be re-pinned before any future panel. Nothing in this run re-pinned it; no validator ran.

**Budget: cycles 14 of 30; runs 25 of an informational 20.** `cycles_used` is unchanged: the
product run returned PASS on its first pass with zero send-backs, and DEC-157 counts rework only.
`max_total_cycles` reads 30 in `feature.json`, so the earlier "14 of 10" exhaustion is resolved
and the build has headroom. **`len(runs)` has passed `max_total_runs`** and INV-22 will say so:
the count is informational and stops nothing. The runs still earn their place — this one closed a
high-severity defect that would have failed the build at T-24 and a blocking coverage gap at
DEC-205, for one spawn and no cycles. The run's `run_id` slug reads `2026-08-29-01-product` as
`harness-pm` wrote it; it is the 25th run of the feature, and the slug is recorded as-is rather
than rewritten.

GitHub mirror: milestone 31, parent #935 at the Plan station, sub-issues #936–#958. The five new
tasks have no sub-issue yet — `gh-sync.py open` mints them after the signature. **No card was
moved by this run and no GitHub write was made.** `feature.json`'s local `status:` moved
`Ready` → `Plan`, which is the honest local record of a withdrawn signature, not a board write.

## Open Questions

Blocking on the operator before the fresh signature:

- **Reconcile the two approval fragments.** `BRIEF.md`'s `## Approval` reads `approved` while
  `plan.yaml`'s reads `pending`. Both are the main session's alone; no agent in this flow may
  write them, and `check-domain.sh`'s `approval_guard` FAILS OPEN in a worktree, so the rule was
  honoured here by instruction rather than by enforcement.
- **Both approval fragments carry a stale "six entries" claim** that F2a corrects to five. It sits
  inside the fragments, so it survives this revision untouched and must be fixed at re-signature.
- **Numbering.** REQ-08 and SC-09 are retired in place as tombstones, so the live sets are
  non-contiguous. The alternative, renumbering, silently repoints citations in landed artifacts.
- **`traces: []`** on T-20 and T-21 — the honest statement that no LIVE requirement is served by
  work being removed. Accept an empty traces list in a signed plan, or require a tombstone id?

Settled by the panel answers, recorded so they are not reopened: SC-11's re-grade scope (five
entries, F2a); T-24's sweep scoping (F1, and the code lane still waits on T-27 for the DECISIONS.md
markers, which was never the defect); cycle headroom (`max_total_cycles` now 30); T-29 and SC-17
stay in FEAT-38 over pm's droppable call, the disagreement recorded rather than resolved by
silence; build-then-delete accepted with the plan honest about it; the lost semantic-rot detector
accepted as a named cost.

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
