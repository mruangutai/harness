# STATE

## Current

- feature: FEAT-37-lead-stop-and-wake
- run: .harness/harness/features/FEAT-37-lead-stop-and-wake/runs/2026-08-26-02-product/digest.md
- squad: none — plan phase at its seam, awaiting the operator's signature
- status: awaiting-user

**MISSION: plan (RE-PLAN). Done. Both artifacts are re-anchored at `8fc87f8` and both approval
blocks read `pending`. One pm run, ZERO send-backs. Runs 7 -> 8 of 20, cycles 0/10, twelve runs
left for the whole build.**

**ALL FOUR BLOCKERS CLOSED, and I verified each at disk rather than on the lead's word.**
B1: `.claude/skills/harness/SKILL.md` is REMOVED from T-01's `bound` group, because c5e59aa
deleted the only text it graded and a third case would grade the empty set — the issue-804 shape
D-05 refuses. Every surviving site now carries `case_floor_<site>` (plan.yaml:234), a NAMED FAIL on
zero occurrences, so no occurrence-grading check in this plan can pass on an empty subject again.
B1b: entered as REQ-08 / T-03 / SC-09. T-03 is repurposed from bound-correction to restoring the
orchestrator's never-wait rule and its inoculation; it depends on nothing and nothing depends on it
(plan.yaml:17), so the three items strike together and #831 stays whole.
B2: re-derived at LEVEL TWO. `case_entry_scope` now slices "from its LEVEL-TWO heading to the next
LEVEL-TWO heading beginning with DEC-" (plan.yaml:302-303), and `case_entry_heading` reads the
level-two line. 201 `^## DEC-` vs 28 `^### DEC-`, measured by me and again by pm.
B3: delivered at BOTH ends. T-02 part THREE writes the contradicting clause into the playbook
(plan.yaml:405-408), and T-01 `case7_overrides_tool_text` (plan.yaml:200) requires ONE SENTENCE to
match both the tool's nudge and a denial — a region that quotes the nudge in one place and denies
something unrelated elsewhere FAILS, which is the silent-beside-it state SC-04 exists to catch.

**SC-08 IS DEFERRED ON A MEASUREMENT, NOT AN EVASION (D-13).** I directed the zero-cost option —
grade it from this feature's own build — to be tested FIRST. It genuinely fails: DECISIONS.md:7023
records that a spawned agent loads its skills from the MAIN CHECKOUT while the rewrite sits in a
worktree, so every lead in this build would read the UNEDITED playbook and the evidence would grade
the old text. Deferred to a post-merge operator run. Issue #866 is a second, weaker reason and not
the deciding one.

**ONE DEFECT I FOUND AND DID NOT SPEND A CYCLE ON.** plan.yaml:110 and BRIEF.md:139/219 label
REQ-08/SC-09 "the operator's scope call/addition". THAT ATTRIBUTION IS FALSE. The operator
DELEGATED the decision to me and I made it; my dispatch said "state it as mine in the BRIEF" and pm
rendered it as the operator's. It matters because the operator reads it and may believe they
already approved it. Correcting it costs a run and a cycle for three words, so it is named loudly
in the CEO briefing instead and the operator corrects or accepts at signature.

**SECOND SCOPE CALL HELD: `inflight_registry.py:258`'s #551-vs-#628 citation is NOT corrected
here.** Different function (`refusal_lines`), different code path, its own tests, and it rests on
#866's measurement rather than this feature's. Disclosed as a backlog residual.

**cycles_used STAYS 0.** The withdrawal was an operator ruling on a moved factual base, and the
re-plan run returned PASS with no send-backs — none of DEC-157's three rework categories.

**B1b WAS CORROBORATED LIVE, TWICE, DURING THIS RUN.** The `children_refusal_lines` refusal fired
on my own return with a lead in flight, and again on the product lead's return with pm in flight.
It keys on HAVING CHILDREN, not on `SINGLE_FLIGHT_AGENTS`. By DEC-201 neither instance can serve as
SC-08 evidence — both playbooks came from the main checkout.

## Open Questions

- Q1 (BLOCKING): `plan.yaml` D-02 (line 54) and D-11 (line 82) still read "DEC-201 is AMENDED" and
  "DEC-199 is AMENDED rather than STRUCK", and D-02 further instructs "the amendment restates the
  scope its title narrows to the orchestrator". That is the SUPERSEDED form sitting in the
  `decisions:` block the documentor reads immediately before executing T-05, which now says DO NOT
  ADD AN AMENDMENT — one document, two contradictory instructions. The SUBSTANCE of both decisions
  survives the ruling intact; only the form word is wrong. Reword both, or let D-09 carry the
  supersession? Out of this run's authorized scope (one pm cycle, two tasks).
- Q2 (was: DEC-199 amend or STRIKE) — RESOLVED. Amend, now expressed as subsume-in-place. D-11 and
  T-06 carry the reasoning: DEC-188 governs a decision the tree FLATLY CONTRADICTS, and DEC-199's
  actual ruling still holds; only the frequency clause was false.
- Q3 (was: the #811 split ruling) — RESOLVED by operator ruling of 2026-08-24. The three-task #811
  block was STRUCK WHOLE before approval; D-07 is the strike record. Issue #811 stays OPEN and
  returns to the backlog.
- Q4: `notes/root-cause-*.md` is in no member's domain, so debug reports fall back to receipt paths.
- Q5: engineer DIGESTs carry no `files_touched`, so a member that wrote a receipt reported no files;
  the lead reconstructs it by hand. Schema gap or intended?
- Q6: **this feature does not close issue #866, and the plan never claimed it did.** The deadlock has
  TWO ends — a dispatch refused on a claim, and `validate-digest.py` refusing the RETURN that reads
  the same claim — and a lead holds no Bash (`.claude/agents/harness-*-lead.md` grant Read, Glob,
  Grep, Agent, Write), so it can act on neither. T-04 corrects one sentence of
  `children_refusal_lines`, the RETURN end. The DISPATCH end is untouched: `refusal_lines` still
  prints `RELEASE_ALL_CMD` (`inflight_registry.py:44`), and `release-all` wipes EVERY feature's live
  claims, not the one blocking. Separate work, and the operator's call whether it joins this feature.
- Q7: single-flight is keyed per checkout, so several orchestrators' children can share one registry
  when they run from one cwd.
