# UAT result and the signature at 19 tasks — 2026-08-22

## SC-10: MET. The UAT was run, both invocations, against live orchestrators.

Run by the main session at `bff6e92`. **109 rows.** The live-orchestrator condition is genuinely
satisfied rather than argued: `a9f2ac678e5cd346e` (FEAT-33's planning orchestrator, running at the
time) and `a2c30ace00fc99048` (FEAT-26's) both appear in the no-argument output.

The four questions, answered from output alone:

1. **Which orchestrators, on which feature** — every row carries `feature=FEAT-NN`.
2. **Current and peak** — both columns present on every measured row.
3. **Distance from the threshold with no arithmetic** — `headroom=` or `overage=`, precomputed.
   **Asserted rather than eyeballed: 0 of 109 rows lack one**, so nothing has to be divided,
   subtracted or compared by hand.
4. **What could not be measured, and which file defeated it** — 5 unmeasured rows, each naming its
   own absolute path.

The named-agent invocation works and warns: `a9f2ac678e5cd346e … overage=25,631` plus the advisory.
None of SC-10's stated failure conditions triggered.

## SC-15's behaviour half: DEFERRED to FEAT-32's first relay, with the reason recorded.

**It is not gradeable at this point in this feature's life, and a manufactured pass would be
theatre.** The criterion grades a successor's first dispatch against the predecessor's `## Next`. The
predecessor's `## Next` was read BEFORE anything was spawned, so this is not post-hoc:

> Dispatch T-05 to harness-eng-lead and T-09 to harness-product-lead … then sequence the qa segment,
> then SIMPLIFY, then pin `review_sha`, then the review panel, then pm's goal-check.

**T-05 and T-09 are both `done`, and so are the other 17.** A successor given only the feature
directory would read the plan, see the work complete, and correctly NOT dispatch them. So the
criterion as written rewards obedience to a stale instruction: the only successor that could satisfy
it is one that ignores the tree in front of it. `handoff-plan.md`'s `## Next` is worse — "the next act
is the operator's signature", given on 2026-08-21.

**Two independent confounds, from opposite directions.** The predecessor orchestrator offered its own
relay as evidence and pm REFUSED it — correctly — because it also held a dispatch naming T-05 and
T-09, giving two sufficient causes for one observation. Mine would be confounded by the work already
being finished.

**The operator's ruling: grade it at FEAT-32's build-to-validate seam**, which produces a live
handoff and a real successor. SC-15's gate half is already automated and passing (INV-17 rejects a
handoff whose `## Next` body is empty, with a mutant red proof), so what defers is the behaviour half
alone.

**The real finding underneath: this criterion is testable only MID-feature and nothing enforced that
timing.** It was written to be hand-graded once, and the one moment it could have been graded passed
unnoticed while the build was running. Filed thinking, not a defect in the code.

## The signature covers 19 tasks

Confirmed by the operator, 2026-08-22. `plan.yaml` gained **T-19** after
`notes/signature-reaffirmed-18-tasks.md` recorded the re-affirmation at 18.

`approval:` is byte-identical and was never reset. T-19 closed **SC-09, which was already approved
scope** — the qa gate found that criterion had no implementing task while `plan.yaml`'s D-02 falsely
claimed an earlier run had closed it. So T-19 **fulfils** the signature rather than extending it, and
the operator has confirmed that reading rather than leaving it as an orchestrator's assumption.

## Close-out state

- 21 residual findings filed as #677 through #697. The twenty-second row was the two stray files in
  the main checkout; those were deleted rather than filed.
- `check-state.sh`: one violation, FEAT-26's unapproved BRIEF — a different flow.
