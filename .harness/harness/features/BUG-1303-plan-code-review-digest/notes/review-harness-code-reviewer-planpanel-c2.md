# Plan panel — BUG-1303, cycle 2 (scope reader) — repair verification

**S-1 (high, cycle-1): CLOSED.** T-01 step 4 (`plan.yaml:147-165`) is now a pure helper
`documented_contract_results(roster, sources, required_by_persona, read_source)` reading no module
global — everything arrives as an argument. Step 7b (`plan.yaml:232-251`) drives it on a wholly
synthetic roster/sources/required-fields/read_source, in ONE call, and asserts all four defensive
branches plus a control inside that one call: unmapped persona, path absent from disk, unlocatable
block, field-present-only-outside-the-block, and a fully-mapped control that reports nothing. That
is stronger than the cycle-1 ask (which wanted the branches merely exercised) — it demonstrates them
together, in one call, inside one suite run, exactly mirroring step 7a's discrimination shape. I
traced the ordering in step 4's prose (sources-missing → read_source None → documented_block None →
gap check over the block) against 7b's five assertions and they line up one-for-one. Verdict stands
on `plan.yaml:113-251` read in full, not on the repair note's account of it.

**VERDICT: PASS.** No must_fix. One new low-severity spec gap noted below (not gating, mirrors the
already-accepted A-3 "latent, not live" pattern).

## Verified closed (all six cycle-1 dispositions)

- **A-1 (dup gate):** case (6) is gone; T-01 renumbers cleanly 1-8 with no orphaned reference —
  grepped every parenthetical step marker in `plan.yaml`, none stray. SC-08 re-declared
  `verify: inspection`, evidence named as T-02's own verify (`--check` + body-compare) plus the
  standing `check-omp-port.py:156-166` wiring (`BRIEF.md` SC-08).
- **Q2 (hand-edit):** T-02 now edits `.omp/agents/harness-code-reviewer.md` only, then
  `sync-agent-adapters.py --apply`; both paths stay in `files:`; recorded as D-07 (`plan.yaml:338-345`
  intent, decisions block).
- **A-2 (artifact fragment unguarded):** T-01 step 6 (`plan.yaml:191-215`) now asserts the literal
  `features/<FEAT>/notes/review-harness-code-reviewer-` for both agent copies, inside the suite.
- **S-2 + A-4 (bare substrings):** step 6 now asserts the composite `"reviewed: " + _PLAN_REVIEW_PREFIX`
  and a field-paired `code_grade:` line carrying `n_a` — both derived from the validator module
  (`_PLAN_REVIEW_PREFIX = "plan:"`, `CODE_GRADE_VALUES` — confirmed present at
  `validate-digest.py:616-617,977`), never retyped.
- **A-3 (whole-file search false-greens 7/16 personas):** `documented_block` now scopes to the fenced
  `DIGEST:` block (SKILL.md sources) or the `## Output` section (agent files) before grading. I
  independently re-ran the premise check myself rather than trust the repair note or the pm's own
  "independent check": grepped `dev` schema's five required field names
  (`tests_added|suite|blocked_on|task|task_verify`) against `harness-digest-dev/SKILL.md` and `lead`
  schema's eight (`team|steps_run|cycles_used|members|must_fix|branch|escalations|sc_status`) against
  `harness-team/SKILL.md`, both restricted to lines outside their fenced blocks (14-33 and 236-255
  respectively, confirmed by fence-line grep) — zero hits outside either block. The premise holds;
  the defect really is latent, not live, and scoping it anyway was the right call.
- **S-3 (spurious depends_on):** `plan.yaml:421-422` — `T-04 depends_on: [T-01]`, with the
  record-integrity reason written into T-04's own intent (the claim "checked mechanically by
  test-validate-digest.py" is true only once T-01 lands). Sound: T-04 consumes no artefact from T-02
  or T-03.

## Fresh-eyes hunt (items 1-4 of the dispatch)

- **Orphan REQs / bad traces:** none. REQ-01→T-02,T-03 · REQ-02→T-01,T-02 · REQ-03→T-03 ·
  REQ-04→T-01 · REQ-05→T-04. Every `traces:` cites a REQ that exists in `BRIEF.md`; every REQ has at
  least one task.
- **`depends_on` topology:** `T-01[] → T-02[T-01] → T-03[T-01,T-02]`, `T-04[T-01]`. Linear, acyclic,
  and consistent with file order — no task depends on one declared after it.
- **Verify vs. intent, character for character:** T-01's two ok-line literals in its `verify:`
  (`plan.yaml:100`) match the strings printed by step 7a/7b in its own `intent:` byte for byte.
  T-02's four verify greps (`code_grade: pass|fail|grade_2|n_a`, `reviewed: plan:`,
  `features/<FEAT>/notes/review-harness-code-reviewer-`, body-compare) each match a literal T-02's own
  intent instructs the author to write, also byte for byte. T-03's verify greps `reviewed: plan:` and
  `DEC-207` directly and checks `code_grade: n_a` only transitively (via the full-suite run, which
  T-01's step 6 grades across all three sources) — T-03's intent says this explicitly ("the verify
  greps for the first" only), so this is a documented asymmetry, not a gap. No stale reference to the
  deleted case (6) anywhere in `plan.yaml` or `BRIEF.md` (grepped both).
- **Traceability after SC re-declarations:** every SC still names a task that produces its evidence.
  SC-01→T-03's full-suite verify · SC-02→T-01 step 7a · SC-03→T-01 step 6, closed by T-02/T-03 ·
  SC-04→structural, no task (unchanged, correctly so) · SC-05→T-01 steps 5+7b · SC-06→T-04 ·
  SC-07→T-03 · SC-08→T-02's verify + standing `check-omp-port.py` gate. No SC lacks a task-produced
  evidence source; no task's verify claims something its SC doesn't ask for.

## New finding (not in cycle 1)

- **[low] `plan.yaml:152-158` (T-01 step 4) — an empty-but-present `CONTRACT_SOURCES` entry is a
  silent no-op, not a named failure.** The spec branches on "sources carries no entry for that
  persona" (→ named failure) vs. "otherwise, for each mapped source" (→ ok/FAIL per source). It does
  not address a persona present in the map with an empty list value: that falls into the "otherwise"
  branch and the `for` loop simply executes zero times, emitting **no line at all** for that persona —
  neither a pass nor a named failure, and invisible to `main()`'s FAIL count. This is exactly the
  "discovery breaks" shape REQ-04 exists to end, just one specific typo away from today's correct
  16-entry map (a maintainer writing `"some-persona": []` instead of omitting the key, or accidentally
  clearing a list while editing). Not gating: today's `CONTRACT_SOURCES` (step 3) maps every persona to
  a non-empty path or pair, so the gap is latent — the same status the panel already accepted for A-3.
  Worth a one-line defense in T-01's intent (treat an empty mapped-list value as an unmapped persona),
  but I would not send this plan back on it alone.

## Assessment

Six-for-six cycle-1 dispositions verified against `plan.yaml` text, not taken on the repair note's
word — I re-derived A-3's premise myself with fresh greps rather than reuse the pm's or the prior
panel's numbers. Traceability, dependency topology, and verify/intent literal identity all hold after
the renumbering. The one new item is low and latent, in the same class the panel already tolerated
once this cycle.

artifact: this file
