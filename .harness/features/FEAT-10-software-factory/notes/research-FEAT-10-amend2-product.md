# Receipt — harness-pm, run amend2-product, step plan-amend2 — FEAT-10

**Path note, first, because it is a known harness contradiction.** `harness-handoff` prescribes
`notes/receipt-<agent>-<runid>.md`. `check-domain.sh --resolve` on that path returns
`harness-orchestrator`, and `harness-pm`'s domain in `.harness/team-config.yaml` grants only
`.harness/features/*/notes/research-*.md` and `.../notes/uat-*.md`. So this receipt is at
`notes/research-FEAT-10-amend2-product.md`. Same recurrence the reviewer hit last run (#199).

## What landed

**A — the deleted criterion.** The `verify: uat` criterion is removed entirely from `BRIEF.md`. Its
id appears zero times in `BRIEF.md` and zero times in `plan.yaml`. The claim mechanism, D-05 and
REQ-03 stand; the residual under D-05 is restated as *unmeasured before ship* rather than as a
criterion's job. No replacement criterion was written and none was proposed.

**B1 — the step-5b skip.** `plan.yaml` T-05 step 5b now requires a distinct stderr reason on every
poll, naming the candidate issue and that `refs/heads/factory/issue-<n>` already exists, poll mode
only (`--issue` stays a lost race at exit 3). It matches `DESIGN.md` C-2 as amended this run. The
assertion sits on SC-13, not SC-22, and on the route-one exhaustion case in T-05's test list.

**B2 — the mixed-blocker case.** One new case in T-05's SC-22 block: the blocked candidate carries
three blockers resolving to three distinct issue numbers, two closed and one open; it is skipped;
the same fixture with the last blocker closed claims it. Case count in that block moved six to
seven. **Buildable** — the gate's only GitHub input is `issue_view(repo, number, fields)`, keyed by
issue number, and `feature.yaml`'s `factory.issues` map gives one number per blocker, so two blocker
states within one candidate need no new fixture capability. The fixture spec now says this in
writing.

**B3 — the false gap note.** The live blocker hop is now stated as unverified before ship, and the
note records that the earlier claim was false even before the deletion.

**Q12** — `plan.yaml` T-05 a-bis: resolvable feature plus unresolvable T-NN is now edge (i) BLOCKED.
The ungated path is scoped to an issue carrying no `feature:` label. **No SC-22 case asserts the new
refusal** — flagged, not silently added.

**Q13** — the cost is corrected to one blocker-state read **per blocker** per candidate in D-01's
`because`, in T-09's instruction, and in SC-09's text. `DESIGN.md:116` carries the same wrong phrase
and is the visual-designer's file, not mine.

**FOURTH RULING** — every REQ-01..REQ-08 and all 20 surviving criteria rewritten in plain English.
Ids, `verify:`, `evidence:`, `traces:` and counts unchanged. `plan.yaml` prose was not touched for
plainness.

## Three criteria changed what they ASSERT, each on a separate instruction — not plainness

Named here so nobody reads them as meaning smuggled in under a prose pass.

- **SC-13** gained "every skip named in clause (a) reports its own reason on stderr…" — that is
  **B1 edit 3**, instructed.
- **SC-09**'s cost clause moved from "per candidate" to "per blocker per candidate" — that is
  **Q13**, instructed. Leaving it would have made SC-09 assert a number the decision no longer says.
- **SC-22** gained "A candidate carrying several blockers is skipped while any one of them is open,
  and becomes claimable only when the last one closes." **B2 asked for a plan case, not this
  sentence — this is my addition.** Reason: without it the new case proves a property no criterion
  asserts, which is the shape of the defect B2 exists to close. Decline it and the case is orphaned.

That makes SC-22 a **four-reason** edit: cross-reference removed, protected literal kept, plainness,
and this new assertion. SC-12 and SC-19 are the two-reason ones the dispatch anticipated.

## Housekeeping check 1, confirmed and not re-derived

Post-deletion every REQ keeps a criterion. REQ-01 → SC-16/17/19/21 · REQ-02 → SC-01/16/17/19 ·
REQ-03 → SC-12/13/19/22 · REQ-04 → SC-04/19 · REQ-05 → SC-05/19. **REQ-06, REQ-07 and REQ-08 were
never at risk and the table's stopping at REQ-05 is not a gap:** the deleted criterion traced only
`[REQ-01, REQ-03, REQ-04, REQ-05]`. Their coverage is REQ-06 → SC-06/08/18/21, REQ-07 →
SC-03/09/20/22, REQ-08 → SC-10/11/14/15.

## Protected literals

`no claimable work` and the `never no work available` negative in SC-13 clause (b): **byte-identical,
untouched.** The two sentences of clause (b) were not rewritten at all — the plainness pass went
around them and the new stderr assertion was appended as a separate sentence after them.

SC-22's second carrier: the cross-reference to the other criterion is **removed**; the literal `no
claimable work` is **kept**, now reading "exits 1 with zero mutating calls and stderr reads `no
claimable work`".

## Numbers, re-derived not recalled

20 criteria (21 before the deletion, not 20 — `feature.yaml counts.scs: 20` was already one behind
after SC-22 was added). By method: 18 automated (15 unit, 3 integration), 2 inspection, **0 uat**.
8 REQs, 12 tasks, 15 decisions. Task `id`, `depends_on`, `files` and `verify` are unchanged — the
sha256 over that projection is `d396fa5…` before and after.

## For the orchestrator

`feature.yaml counts` is stale and is not mine to write: `scs` should read 20, `sc_automated` 18,
`sc_inspection` 2, `sc_uat` **0**. `harness.json` sets `gates.uat` to
`blocking_when_uat_criteria_exist`, so the gate no-ops on its own; the explicit statement lives in
`BRIEF.md ## Verification gaps`, first bullet.
