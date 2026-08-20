# SIMPLIFICATION angle — FEAT-26 plan surface — receipt

Read: `plan.yaml` (686 lines), `BRIEF.md` (127 lines), `.claude/skills/harness-simplify/SKILL.md`
(charter). Skimmed for cross-reference only, not rewritten: `feature-schema.json`,
`test-gh-sync.py`, `test-validate-feature-json.py`, `test-check-state.py` (not opened in full —
their shape is already pinned verbatim in the task intents, which is what this pass judges).

## The live question — checked, and it comes back clean

The dispatch named the `source_issues` contract as spelled across five places: T-01's schema
`description` (plan.yaml:129-136), T-02's mirror rule (`load_recorded`/`save_recorded`/
`parse_source_issues`, plan.yaml:196-236), T-04's renderer (reads `load_recorded`'s
`github.source_issues`, plan.yaml:366-368), T-07's template comment + SKILL.md row
(plan.yaml:587-606), and DEC-197 (plan.yaml:669-676). All five agree on the same shape and the
same flow: plan.yaml's top-level `source_issues` is the signed truth, `open` mirrors it into
`feature.json`'s `github.source_issues`, `closes` reads the **mirror** (not plan.yaml) so what
it emits is what was recorded at open time, and absent/empty is legal everywhere. No drift
found — not flagged.

## Finding 1 (low) — a decision's rationale sentence is restated near-verbatim in the task intent that implements it, in three places

- **File**: `plan.yaml`
- **Lines**: D-02 (56-58) vs T-03 intent (305-306); D-06 (82-85) vs T-05 intent (445-446); D-07
  (87-92) vs T-02 intent item 3 (220-224). Also BRIEF.md's SC-02 (55-57) states the same
  external fact as D-02.
- **Summary**: three `because:` clauses are copied near-verbatim into the intent of the task
  that implements them, rather than the intent citing the decision id:
  - D-02's "the branch feat/harness-native-foundation really does carry two merged pull
    requests, so a first-match rule would silently record the wrong one" reappears in T-03's
    intent as "the branch feat/harness-native-foundation carries two merged pull requests, 15
    and 4, so a first-match rule records the wrong one" — and a third time in BRIEF SC-02 ("...
    really does carry two").
  - D-06's "INV-21 set the precedent that the GitHub mirror never gates a flow, and PR linkage
    is bookkeeping rather than correctness" reappears in T-05's intent as "the GitHub mirror
    never gates a flow (INV-21's own recorded reason), and pull request linkage is bookkeeping
    rather than correctness".
  - D-07's "_record_status in the same file already refuses for exactly that reason" reappears
    in T-02's intent as "_record_status in this same file already refuses to create a document
    for exactly this reason."
- **Concrete cost**: this draft is about to be revised once more (pm merging four angles'
  findings). If any other angle's finding touches D-02's zero/many wording, or the eleven/four
  backfill split, three independent spellings (BRIEF SC-02, plan D-02, plan T-03 intent) need
  synchronized edits in that revision round, and there is no automated check that would catch
  one left stale — `check-state.sh` does not audit plan prose, only feature.json.
- **Alternative**: the task intent cites the decision id ("see D-02 for why exactly-one, not
  first-match") instead of restating the because-clause; the decision stays the single
  authoritative spelling.
- **Caveat, included so pm can skip with reason rather than re-derive it**: task intents are
  dispatched to an executing engineer who may not carry the full `decisions:` block in context,
  so a self-contained intent is arguably deliberate, not accidental duplication. Rank this last.

## Checked and declined — not flagged

- **The absent/empty `source_issues` rule** appears in six places (D-08, T-01 schema
  description, T-02 items 1+4, T-04 intent, T-07 template comment, BRIEF REQ-06/SC-11) but each
  states the *same invariant scoped to its own component's behavior* (schema legality, load
  default, parse default, render behavior, template guidance, requirement) — not one rule
  spelled six ways that can disagree. This is the normal shape of a cross-cutting invariant
  honored by several components, not drift risk.
- **DEC-174 carve-out restatement** (BRIEF Constraints:115-116, plan.yaml lanes rows:29-34,
  T-05 execution_reason:401-402, T-05 intent close:469-472) — protected by the dispatch's
  explicit "do not flag `execution_mode: main-session-direct` markers" instruction.
- **D-02 as a standalone decision** — considered folding it into D-01 since both concern PR
  derivation, but D-01 fixes *when* (ship time, from the recorded branch) and D-02 fixes a
  separate axis (*how many matches count as resolved*); genuinely two design choices, not one
  restated.
- **T-06's verify block size** (the full 23-feature expected-`pr` dict) — SC-08 explicitly
  requires the per-feature assertion ("A count or a whole-file search does not satisfy this"),
  so the size is the claim, not padding around it.
- **T-01/T-02 vs T-03/T-04 task granularity** — each pair is independently testable and
  independently dependent (T-03 and T-04 both depend only on T-02, not on each other), so
  splitting is correct, not "two tasks that are one."
- **T-07 bundling two files** (template comment + SKILL.md rows) into one task — both resolve
  to the same `main-session-direct` lane for the same reason (`check-domain.sh --resolve`
  returns NOBODY), so one task avoids a second no-op dispatch, not complexity.

## No SIMPLIFICATION findings beyond the one above

Empty-on-everything-else is a real result, not a pre-emptive skip: full file read, cross-checked
against the SKILL's four bullets (duplicated prose, restated D-entries, redundant tasks, dead
references) and the two must-not-flag exclusions.
