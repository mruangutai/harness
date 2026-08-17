# Distillation — harness-ui-reviewer — FEAT-22

**Source discipline note (stated up front, per the dispatch's ask):** no observations log exists for
this feature despite seven review rounds on it — this distillation is a cold digest-and-notes skim
only. Cost: I have no mid-run detail beyond what each digest/note chose to record — e.g. any smaller
probe-construction dead-ends on r9 that didn't make it into the final addendum are gone. It did not
cost me the two candidates below; both are fully reconstructable from the r9 note (`plan-r9.md:108-207`)
and the run-10 digest, because both were written as findings with probes shown, not narrated.

## Candidates — decisions, sourced, tagged

**C-1 — accepted, relayed.** Source: run-10 digest (`runs/2026-08-15-10-validator/digest.md`, "What
the panel could not tell us," 4th bullet) + my own r9 addendum
(`notes/review-harness-ui-reviewer-2026-08-15-plan-r9.md:108-207`, probes d/e). Cycle-1 PASS flipped
to cycle-2 FAIL on the same two-line delta because one probe *direction* (false-PASS) was added, not
because more text was read. My r9 probe set (a/b/c) covered total-silence and false-FAIL only; the
finding I was sent back to close lived in the third direction. Checked against existing Patterns:
distinct from P-15 (a narrower, specific failure mode — new-literal-contains-old-literal) — C-1 is
the general testing-methodology lesson that a probe set's *polarity coverage*, not its wording
variety, is what determines whether a coverage claim is earned. **Applied as G-06** (Gotchas had
room; no displacement needed).

**C-2 — accepted, relayed.** Source: run-10 digest, "The finding that gates." The r9 remedy (T-08
clause 4) closed the total-silence shape of the earlier open question (Q3) and left the false-PASS
shape unaddressed — the shape Q3 was actually *ranked* on. Distinct from G-01 (verify a fix's literal
text before marking closed, a *presence* check) — C-2 is about *shape-completeness*: a remedy can be
textually present and still discharge the wrong reading of a multi-shaped finding. **Applied as
G-07** (Gotchas had room).

**C-3 — rejected.** Source: run-7 digest (`runs/2026-08-15-7-validator/digest.md`, "Assessment").
Re-deriving the DEC-189 arithmetic from tracked sources (`harness_boundary.py:89-94`,
`team-config.yaml:117/118/199`) rather than reading it back from the plan's own self-description is
an instance of existing P-02 ("a dispatch's description of a file is a hypothesis, not evidence"),
generalized from "dispatch claim" to "plan's own self-description claim" — same mechanism, same
remedy (direct object check at the source of truth). Not a new rule; a new instance of one already
held. Rejecting per the dispatch's own flagged expectation.

**Not evaluated as candidates** (per dispatch instruction — already covered by held entries, or
routed as harness defects, not craft): the census-before-scope-out lesson (P-01/G-05/O-01), the
run-id collision and squad-boundary drift (harness defects, correctly routed as `open_questions`
in prior runs, not Expertise material).

**No repository-layer candidate identified.** `.harness/harness/expertise/harness-ui-reviewer.md`
does not exist and I hold no grant for it; nothing in this skim turned on a path, decision or
invariant true of only this one repository rather than the craft of the review itself, so I propose
nothing there.

## Section counts

| Section | Before | After |
|---|---|---|
| Patterns | 15/15 | 15/15 (unchanged) |
| Gotchas | 5/15 | 7/15 |
| Outcomes | 3/10 | 3/10 (unchanged) |
| Open | 0/5 | 0/5 (unchanged) |

## Verification

`bash .claude/skills/harness/bin/check-expertise.sh .harness/expertise/harness-ui-reviewer.md` →
`OK   .harness/expertise/harness-ui-reviewer.md`, exit code **0**.
