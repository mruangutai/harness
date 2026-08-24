# STATE

## Current

- feature: FEAT-35-orchestrator-stop-and-wake
- run: VALIDATE COMPLETE at its exit predicate — panel PASS, must_fix EMPTY. Nothing in flight.
  Pin a2a373b1ef351f94b0a4310bea928f1384727a08, base df18fe5. Tree clean.
- squad: none
- status: Review

<!-- SC-01/02/04 RE-CONFIRMED at the new pin and shown to DISCRIMINATE: 9/9 pass at a2a373b,
     9/9 fail at 569d417. SC-06 re-graded PASS (its c0 verdict covered SKILL.md:99-138, the region
     both fix commits edit). SC-07 met. SC-05 partial + post-merge obligation. matrix_ok FALSE,
     accepted. The fix introduced NO regression.
     SC-03 now splits by verifier (BRIEF.md:98-117). Clause A (shape) MET, cited to the c2 run.
     Clause B (subject) rests on the main session's two measurements against a live orchestrator -
     agent-ad292e24ec60c589b.meta.json and current=330,527 peak=330,527 entries=149. NO AGENT CAN
     GRADE CLAUSE B; recording SC-03 met is the main session's act, not a run I can dispatch.
     TWO NEW NON-BLOCKING FINDINGS, both in the calibration text added at a2a373b, both in five
     lines (SKILL.md:103-107), so ONE editing pass fixes both:
       MED - :105-107 "Approaching roughly TWICE the threshold is where handing off stops being
       optional" is a mandate DEC-198 does not license; :102 in the same paragraph says the
       threshold ADVISES and the decision is yours. I READ BOTH LINES MYSELF. Not a gate - nothing
       enforces it - so BRIEF.md:57's "turning it into a gate is out of bounds" is not breached in
       letter, but the paragraph tells an orchestrator two different things.
       LOW - :104-105 embeds a dated operator quote and a token measurement. REQ-07 exists to keep
       measurements in DECISIONS.md; this is the feature's own requirement in tension with the
       feature's own text.
     RE-SIGNATURE STILL OWED: ## Approval reads 2026-08-24, written BEFORE the second SC-03
     amendment. Same date, so the record cannot show it - day granularity hides same-day edits.
     cycles_used 6/10. 12 runs vs informational bound 20. NOT COMMITTED BY ME, NOT SHIPPED,
     PR NOT OPENED. -->

## Open Questions

- BLOCKING, MAIN SESSION ONLY: record SC-03's grade. Clause A is met and in-repo; Clause B rests on
  your own off-repo measurements and no agent can vouch for them. Not a run I can dispatch.
- BLOCKING, OPERATOR: RE-SIGN for the second SC-03 amendment. The signature predates its content
  again, invisibly this time - both carry date 2026-08-24.
- NON-BLOCKING, OPERATOR'S OWN TEXT: soften SKILL.md:105-107's "stops being optional", or amend
  DEC-198 to license a second harder point. One editing pass also moves the dated quote at :104-105
  to DEC-201 per REQ-07.
- NON-BLOCKING: day-granularity approval dates cannot detect a same-day amendment. Backlog.
- FILED, do not re-file: #803, #804, #805, #806, #808, #810.
