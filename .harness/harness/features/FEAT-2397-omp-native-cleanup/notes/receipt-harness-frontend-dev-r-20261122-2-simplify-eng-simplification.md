# Receipt — simplify · simplification — FEAT-2397 (plan surface, flag-only)

BLUF: 4 low/info findings, no blockers. Native-extension and probe design (T-01 TS slice, T-04) is lean: no new module or wrapper survives the deletion test, no alias-hidden names. Remaining cost is plan-text duplication and one stale title. Settled items (single-pass `_capped_body`, atomic #10/#11, KEEP rows, ABI labels, panel rulings) not flagged.

## Findings

1. low · T-03 · plan.yaml:431 (title) vs :465 (intent) — dead reference to a shape the revision removed
   - Title says "...and stale bin comments"; intent says T-05 owns bin/template comments and T-01/T-02 own their files' comments; every T-03 file is under tests/.
   - Cost: a reader or reviewer expects bin-comment edits in T-03 and may re-edit files T-05 owns, which the intent forbids.
   - Alternative: retitle "Remove redundant legacy environment setup from standing tests".

2. low · T-05 · plan.yaml:538-542 vs decisions_affected 122-303 and BRIEF SC-08 — same rule stated in two or three places
   - Per-DEC dispositions (DEC-81/218/222 amend-never-strike, DEC-81 cites maxConcurrency default 32, DEC-127/173/199/208 stop_hook_active rewrite, DEC-155/156, DEC-198/201 floor) are restated in T-05 intent prose after already living in `reason:` fields and SC-08.
   - Cost: wording drift. An edit to one row's reason leaves the intent stating the old contract, and Main executes from the intent.
   - Alternative: intent says "apply each decisions_affected row per its reason" and keeps only what the rows lack (DEC-205 in-place rule, <=30-word tails, regenerate index, cumulative-gate ordering).

3. info · T-01..T-06 intents — boilerplate preamble repeated six times
   - Each intent re-opens with product-checkout path, "no separate docs/architecture.md", DEC-174/execution_agent attribution, and (T-01..T-04) the grade >=3/>=4 sentence. T-01 alone adds "split large grade-2 tests", so the copies already differ.
   - Cost: roughly 6x restatement with partial divergence on the grade rule.
   - Alternative: the grade rule once in T-01 or BRIEF SC-12 (the mandatory bar stays, only the repeat goes) and a shared preamble. Optional: restating may be deliberate so each dispatch is self-contained.

4. info · T-05 depends_on (505-508) and T-06 depends_on (553-555) — transitively redundant edges
   - T-05 lists T-01/T-02, but T-03 and T-04 already imply both. T-06 lists T-04, but T-05 implies it.
   - Cost: minor; a later edge edit can leave the redundant edges inconsistent.
   - Alternative: T-05 depends on T-03, T-04; T-06 on T-05. Drop only if the plan convention is not to spell full lists.

Also noted, not flagged: T-05 verify (:533) uses `.agents/skills/harness/bin/check-state.py` while sibling lines use `.claude/skills/...`. `.agents/skills` is a symlink to `../.claude/skills`, so both resolve; the spelling mismatch is cosmetic.

## Principles applied
Only `harness-simplify` angle-simplification and the `harness-codebase-design` deletion test were applied. No craft leaf was read for this receipt, so none is cited.

## Verification
Read-only reading plus an `ls`/`grep` existence check. No builds, tests or edits.

Open questions: none.
