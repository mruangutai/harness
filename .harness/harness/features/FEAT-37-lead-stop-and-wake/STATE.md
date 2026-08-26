# STATE

## Current

- feature: FEAT-37-lead-stop-and-wake
- run: .harness/harness/features/FEAT-37-lead-stop-and-wake/runs/2026-08-26-01-product/digest.md
- squad: none — plan phase at its seam, awaiting the operator's signature
- status: awaiting-user

**MISSION: plan. The plan is complete at 6 tasks and both approval blocks read `pending`.**

**THE FORM RULING IS APPLIED.** The operator ruled that `DECISIONS.md` stops being append-only: a
decision SUBSUMES its correction IN PLACE and reads as current knowledge in one voice; git holds the
history. T-05 and T-06 were written before that ruling and both instructed the documentor to ADD an
amendment sub-section. Both are rewritten to subsume in place — no `### DEC-NNN amendment N`
heading, no bold `**Amendment N (date)**` marker, no changelog voice. The content objective is
UNCHANGED: DEC-201 still gains the lead tier, DEC-199 still gets the measured bound and its
falsified once-only clauses corrected. **D-09 records the ruling and its cost** — a citation to a
specific amendment number no longer resolves in the file, and the diff is the only place superseded
wording survives.

**DEC-158 forced a survives-or-cut call on every item**, made in the task intents so the documentor
does not re-judge it. CUT as biography: specimen ids as narrative, sidecar line numbers, microsecond
`started_at` values, cycle counts, durations, "the hook was ruled out", the platform's
consecutive-block cap of eight. SURVIVES: the rule, the consequence, one clause of why, and the
DISCRIMINATING evidence compressed — two refusals named DIFFERENT CHILD SETS, which is what proves a
distinct event rather than replayed context.

**NEITHER `verify:` BLOCK NEEDED CHANGING, and that was measured, not assumed.**
`gen-decisions-index.py` emits an `am.N` span only inside `if amend_span:`, and `compute_amendments`
returns nothing when neither amendment regex matches — absence of the form is SILENT, not an error.
DEC-199 and DEC-201 carry no `am.` token in the index today (DECISIONS-INDEX.md 217, 219), so
removing the form removes nothing that exists. Both verify blocks are byte-identical to the
originals.

**T-01 to T-04 STILL COVER #831 AND ARE UNTOUCHED.** T-01's `coverage` group slices the DEC-201
entry "to the next level-3 heading that introduces a different DEC number" — under the new form that
clause simply never fires and the slice becomes the whole entry, so T-01 needs no change. T-04
remains DELIBERATELY NARROW: it corrects `children_refusal_lines` only. **This feature does NOT fix
issue #866** — see Q6.

**cycles_used stays 0.** The rewrite was triggered by an operator ruling on the form of the record,
not by a FAIL, an unmet SC, or a send-back — none of DEC-157's three rework categories. Flagged, not
silent.

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
