# A plan-merge.py proposal, not prose. It carries the .md name because check-domain.sh grants
# harness-pm exactly `.harness/*/features/*/notes/research-*.md` under notes/, and a proposal is
# YAML that plan-merge.py reads by path regardless of extension. Fix cycle 2, send-back 1.
#
# ONLY new ids: D-15, D-16, T-08. No `approval:` mapping and no `lanes:` block, because lanes is
# not a UNION_KEY and any differing value would exit 7 and refuse the whole apply.
schema: plan/1
feature: FEAT-51-claude-code-lifecycle-safety

decisions:
  - id: D-15
    choice: The DEC-209 entry T-06 writes carries BOTH halves of the quarantine boundary, and this decision SUPERSEDES two bullets of T-06's immutable intent, the bullet saying the boundary is refused at the check-domain.sh Write gate on the canonical artifacts and the bullet beginning The four canonical artifacts are plan.yaml BRIEF.md feature.json and STATE.md; the entry must instead state (a) the check-domain.sh Write and Edit half, which bites on BRIEF.md, feature.json and STATE.md, (b) the plan-sign-gate.sh PreToolUse Bash half, which bites on the four mutating plan-merge.py verbs apply, add-tasks, set-task-station and set-feature-station and on quarantine.py adopt and discard per D-16, and (c) explicitly that plan.yaml's only write route is plan-merge.py invoked through Bash, so plan.yaml is covered by the plan-sign-gate.sh half and NOT by FEAT-41's editor route denial, which is a second and independent refusal on a route nobody may use
    because: a documentor following T-06's bullet list verbatim writes an entry that omits the Bash half entirely and leaves a reader believing plan.yaml is covered because the FEAT-41 denial handles it, which is the exact false belief T-07 exists to overturn, and DEC-209 is the entry future readers rely on to know what the boundary covers, so an incomplete entry understates the contract that shipped
    dec: DEC-209
  - id: D-16
    choice: quarantine.py discard IS covered by the Bash quarantine rule, which reverses the deliberately-not-covered comment T-07's immutable intent directs for ADOPT_TOOL, and T-07 is the task that implements it; discard is matched on the value of --dir and not --file, because discard takes --dir, so the rule normalises that value from its last .harness/ segment, matches the result against ^\.harness/[^/]+/features/([^/]+)/quarantine/[^/]+/?$, takes the feature from group 1, refuses when orphan_write is True, and falls OPEN on an unresolvable or absent value exactly as D-13 states for --file; the new case in test-plan-sign-gate.py carries the exact label string "an orphan quarantine.py discard of a quarantine directory is refused", and the refusal text says that discarding a quarantined result is the resumed parent's act and this caller is not it, rather than naming a quarantine path to write instead
    because: this answers Q2 as a choice and not an omission - REQ-05 is untouched since discard makes nothing canonical, but the boundary's whole promise to the operator is a recoverable artifact, and an orphan destroying the only copy of its own result silently undoes REQ-04's remedy with no wake and no operator act, which is the same unsupervised-durable-state harm this feature exists to stop; the cost is one branch in a rule already being written, and a note that discard is uncovered would read to a later reader as an oversight
    dec: DEC-209

tasks:
  - id: T-08
    title: Guard the DEC-209 entry so an omitted Bash half turns the suite red
    traces: [REQ-04, REQ-05]
    change_type: scaffolding
    execution_mode: team
    execution_agent: harness-dev-ops
    depends_on: [T-06]
    status: ready
    files:
      - .claude/skills/harness/bin/test-gen-decisions-index.py
    verify: |
      grep -q 'def test_dec_209_entry_names_both_enforcement_points' .agents/skills/harness/bin/test-gen-decisions-index.py &&
      grep -q 'def test_dec_209_entry_states_the_bash_write_route_for_plan_yaml' .agents/skills/harness/bin/test-gen-decisions-index.py &&
      python3 .agents/skills/harness/bin/test-gen-decisions-index.py
    intent: |
      SC-09 grades the DEC-209 entry's CONTENT and declares verify automated with evidence
      integration. Nothing in the plan asserts that content today, so an entry that omits
      the plan-sign-gate.sh half would ship graded met. This task is the assertion. It adds
      NO new test file, so neither run-unit-tests.sh INTEGRATION_SCRIPTS nor
      harness.json test_kinds.integration.detect changes, and it does not touch
      DECISIONS.md or DECISIONS-INDEX.md, so no index regeneration is owed here.
      change_type is scaffolding because the deliverable IS the guard - no production
      behaviour changes and the matrix owes this row nothing beyond the guard itself.

      Everything below was measured at ad93d43e1f232ec1ab87e08ccf70a01a08c206b7. Re-read
      each anchor before editing and treat the quoted literals as the anchors.

      Add TWO module-level test functions at the foot of
      .claude/skills/harness/bin/test-gen-decisions-index.py, immediately after
      test_no_amendment_construct_survives_in_the_authority which begins at :829 and ends
      at :869, and BEFORE the TESTS list at :872. Register BOTH in that TESTS list - main()
      at :887 iterates TESTS and nothing else, so an unregistered function never runs.
      Follow that neighbour's shape exactly: it guards the LIVE authority file rather than a
      fixture, it wraps its whole body in try/except printing FAIL - <name> on an exception,
      it prints ok - <name> and returns True on success, and every FAIL message names the
      file and what was missing. Reuse the module constants already present rather than
      restating any path - REPO_ROOT at :22 and gdi.DECISIONS_PATH, the pair that neighbour
      composes at :837 to reach the real DECISIONS.md.

      Add one module-level constant beside them:

        QUARANTINE_DEC = "DEC-209"

      with a comment saying that T-06 takes the next free number if DEC-209 is taken when it
      runs, and that this constant moves with it. Both tests must FAIL LOUDLY, never skip,
      when no heading for QUARANTINE_DEC is present - a skip on an absent heading is a green
      that proves nothing, and after T-06 the heading is present by construction.

      Both tests slice the SAME region and each must compute it the same way, so extract one
      module-level helper beside the constant, _dec_region(text, dec) -> str or None. The
      authority's live headings are ## DEC-N followed by an em dash and a title; harvest them
      with the fence toggle the file already defines at :46,
      fence_guarded_dec_headings(text), so a heading inside a ``` fence is never taken as the
      region start. The region runs from the ## DEC-209 heading line to the next line
      matching ^##\s+DEC-\d+ outside a fence, or to end of file. Return None when the heading
      is absent. Bound the region on BOTH sides - an unbounded tail would let a later entry's
      text satisfy every assertion below.

      test_dec_209_entry_names_both_enforcement_points asserts, on that region, with a
      SEPARATE check and its own FAIL message per clause rather than one combined condition,
      because a combined condition is satisfied by the clauses that hold and blind to the one
      that does not:

        1. the literal check-domain.sh occurs in the region;
        2. the literal plan-sign-gate.sh occurs in the region;
        3. the literal quarantine.py adopt occurs in the region.

      test_dec_209_entry_states_the_bash_write_route_for_plan_yaml asserts, on that same
      region with its newlines collapsed to single spaces so a sentence wrapped across lines
      still matches, again one check per clause:

        1. the literal Bash occurs in the region, case-sensitive, as a whole word;
        2. one sentence of the region - split the collapsed text on the literal period
           followed by a space - carries BOTH plan.yaml and plan-merge.py. A whole-region
           search for the two names is satisfied by two unrelated sentences, which is exactly
           the entry this test exists to reject.

      Do not assert the ABSENCE of the FEAT-41 sentence. FEAT-41's route denial is a true
      second refusal and the entry may legitimately mention it; the defect being guarded is
      an entry that names it INSTEAD OF the Bash half, and clauses 1 to 3 above already turn
      that entry red.

      Change nothing else in the file. Do not touch the eleven existing tests, run_gen at
      :64, make_authority at :83, or the GEN_DECISIONS_INDEX_BIN override at :29.

      Recorded baseline, observed at ad93d43e from the main checkout - the task verify block
      above run verbatim exits 1 with no output, because the first grep fails, while its tail
      conjunct alone, python3 .agents/skills/harness/bin/test-gen-decisions-index.py, exits 0
      today printing eleven ok lines. The two greps are therefore the whole discriminator and
      no earlier conjunct masks them.
