# Validate c1: BUG-2565 at bb401aae

**ESCALATE.** The pin does not ship. Four in-scope repairs are needed, plus two scope decisions only the operator can make:

- The required integration kind is red (2 files). One of the two can only be repaired in a file that no task owns.
- T-03 fails the mandatory code-grade gate.
- SPEC.md:779 still says a yield proceeds when the validator is unavailable.

The core contract holds and was measured:

- SC-01, SC-02, SC-03, SC-06 and SC-07 have covering tests, and fail-first was reproduced against 104252db.
- Unit is green with 69 tests, and typecheck is green.
- T-03 parity is 16/16 at the pin (QA executed it).
- The port gate and `gen-agent-output.py --check` both exit 0.
- All 7 DEC amend dispositions are met.

Reviewed: 104252db..bb401aaea16b9b36a954daef3cebafb2401efe89. Cycles used: 0. Members: qa FAIL, code FAIL, security FAIL, ui PASS (scoped out), pm FAIL.

## Must-fix (ranked; fix order in brackets)

1. **T-03 code grade (code-reviewer, high, substance).** The pinned `code-grade.py` exits 1 on two functions:
   - `_Loader.project` at `digest_projection.py:121` is grade 1 (49/91/104.2).
   - `render` at `gen-agent-output.py:29` is grade 3 (10/14/18.0).

   **Repair:** separate ref traversal from projection, and span extraction from rendering, then re-grade. The same refactor must also close two med defects (code-reviewer), each with a regression witness:
   - A referenced root `anyOf` is admitted, which breaks SC-07's letter (`:124-133,177-190`).
   - Regeneration does not preserve CRLF, quoted-key and indentationless-sequence frontmatter (`gen-agent-output.py:32-46,62,80`).

   Then regenerate the agents and re-run parity. [1]
2. **Integration red: `test-check-plan-routes.py` (qa).** `tests/integration/canonical-reader-classification.json` has no entries for the new `digest_projection.py` and `gen-agent-output.py` readers. That file is in no task's `files:`, so this needs the scope decision in OQ-1 first.

   **Repair:** add the entries after item 1, because the refactor may rename the classified functions. [2]
3. **Integration red: `test-gen-decisions-index.py` (qa, T-06).** The DEC-100, DEC-127 and DEC-208 rulings are over the 30-word cap: 39, 33 and 33 words at `DECISIONS-INDEX.md:109,132,206`.

   **Repair:** shorten each ruling, still without asserting injection or a passing yield. [independent]
4. **SPEC.md:779 (pm, substance, low, T-06).** The refusal table's Unavailable row still lists the yield among the phases where the call proceeds. That contradicts the hook, SPEC:784-788 and DEC-100, and it leaves the operator perspective `partial`.

   **Repair:** change the row to "proceeds (pre, post, dispatch); a yield is refused, never passed (BUG-2565)". [independent]

## Escalated, not must_fix (operator decision)

- **Exit 0 with an unrecognized answer is allowed (T-02).** Code-reviewer rates this high; security rates it med. Both ratings are transcribed unchanged.

  In `classifyAnswer`, a broad gate that exits 0 with empty, malformed or unknown stdout returns `{blocked:false}` (`harness-hooks.ts:430-439`). I confirmed this at source. My reading:
  - This is not a regression. Base used the same classifier, and silent exit 0 is the validator's success contract.
  - Every class SC-01 enumerates is refused.
  - The only remedy is a positive acknowledgement protocol in `validate-digest.py`, which is outside T-02's files and inside the bin tree that is main-session-direct.

  So this goes up as OQ-2 rather than into must_fix. The verdict already fails on the other items, so neither rating changes the outcome.
- **"The permissive frontmatter removes the strict backstop" (security):** dismissed. D-01 settled it, and SC-05's probe shows OMP rejects off-schema yields.

## Advisory (logged, non-blocking)

- README:185 and BUILD:62 say "repeated refusals"; the probe measured 3 (code-reviewer and pm, form, T-06).
- harness-team SKILL:146 still says "injected lead schema" (pm, form, T-06).
- The probe receipt says no refused payload reached the parent. The parent's failure text quotes the refused object, so that claim should be narrowed (security, form, T-01/T-06).
- Child-visible validator diagnostics should be bounded and redacted; base forwarded the same detail (security, low, T-02).
- Four grade-2 functions (code-reviewer).
- SPEC §8.3 cites stale line numbers that were already stale at base (pm).

## Adequacy

- SC-08 parity has measured evidence from QA's execution (16/16 at the pin). The code-reviewer was refused the parity command by its read-only guard, so the reviewer lens on SC-08 is reasoning-only.
- QA coverage gaps:
  - There is no symlink-escape fixture, so `digest_projection.py:76` is never exercised alone.
  - The `task.structured` refusal test asserts the key, not the file name.
  - SC-02's contract leg is witnessed by a mutation, not a natural red.
- The integration receipt is an honest red at the host interpreter, not CI.

```yaml
VERDICT: ESCALATE
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2565-digest-frontmatter-contract/.harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-06-validate-validator/digest.md
DIGEST:
  headline: 'bb401aae does not ship yet. The core contract is measured green: SC-01/02/03/06/07
    fail-first reproduced, unit and typecheck green, parity 16/16, 7/7 dispositions
    met. Still failing: integration is red, T-03 fails the code-grade gate, and SPEC.md:779
    contradicts the yield refusal. Two scope amendments need operator decisions.'
  open_questions:
  - id: OQ-1
    question: 'test-check-plan-routes.py is red at the pin because tests/integration/canonical-reader-classification.json
      has no entries for the new digest_projection.py / gen-agent-output.py readers.
      That file is in no task''s files:. Should T-03''s files: be amended to own it,
      so the main session can add the entries after the T-03 refactor? (QA Q-1)'
    blocking: true
  - id: OQ-2
    question: 'A broad-gate validator that exits 0 with empty, malformed or unknown
      stdout is allowed: harness-hooks.ts:430-439, classifyAnswer returns {blocked:false}.
      Code-reviewer rates this high and security rates it med. It is not a regression,
      since base uses the same classifier, and every class SC-01 enumerates is refused.
      The only remedy is a positive-acknowledgement protocol in validate-digest.py,
      which is outside T-02''s files and in the main-session-direct bin tree. Options:
      amend T-02 scope to add the ack and refuse every other exit-0 answer, or accept
      it as a residual and file a follow-up issue. (code Q2, security SEC-01)'
    blocking: true
  - id: OQ-3
    question: SC-08 says 'the reviewer runs T-03's parity command'. The code-reviewer
      was refused the command by its read-only write guard; QA executed it at the
      pin with 16/16 parity ok. Is QA's execution accepted as SC-08's evidence?
    blocking: false
  - id: OQ-4
    question: Should D-03's boundary cover failure prose? The T-01 probe's parent
      task-failure text quotes the entire refused object, while the receipt says no
      refused payload reached the parent. (security SEC-02)
    blocking: false
  - id: OQ-5
    question: 'Harness defect: the validator-lead digest schema forces findings[].scope
      and readers[].reason to none/null/n/a, so a validate lead cannot record a finding''s
      task scope (DEC-228 ''scope: task|mission'') or a reader''s reason. Is the schema
      meant to be this narrow?'
    blocking: false
  files_touched:
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-06-validate-validator/state.yaml
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-06-validate-validator/digest.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-06-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-06-validate-validator/qa/manifest-integration.json
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/observations/harness-qa.md
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: FAIL
    headline: 'Integration is red: test-gen-decisions-index.py and test-check-plan-routes.py
      regressed by the diff. Unit (69) and typecheck are green. Fail-first is reproduced
      for every automated SC. Parity is 16/16 at the pin.'
    files_touched:
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-06-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-06-validate-validator/qa/manifest-integration.json
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Yield still accepts an unchecked exit 0; two T-03 Python functions fail
      the code-grade gate.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: The yield hook accepts exit 0 with empty or malformed validator output;
      permissive frontmatter removes the old strict backstop.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B scoped out: of 83 changed paths only org.html renders, a copy-only
      change with no governing DESIGN.md.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: 'Orchestrator and code maintainer perspectives are met. Operator is
      partial: SPEC.md:779 still says a yield proceeds on an unavailable validator.
      All 7 amend dispositions, SC-09, SC-10 and SC-11 are met.'
    files_touched: []
  must_fix:
  - '[1] T-03 (code-reviewer, high, substance): pinned code-grade.py exits 1. _Loader.project
    at digest_projection.py:121 is grade 1 (49/91/104.2); render at gen-agent-output.py:29
    is grade 3 (10/14/18.0). Separate ref traversal from projection and span extraction
    from rendering, then re-grade. In the same refactor, with regression witnesses:
    refuse a $ref-reached root anyOf (digest_projection.py:124-133,177-190; SC-07),
    and preserve CRLF, quoted-key and indentationless-sequence frontmatter bytes (gen-agent-output.py:32-46,62,80).
    Then regenerate the agents, run gen-agent-output.py --check, and re-run T-03 parity.'
  - '[2] Integration red, test-check-plan-routes.py (qa): add scanned_files and _Loader
    load_json_mapping rows for digest_projection.py and gen-agent-output.py to tests/integration/canonical-reader-classification.json.
    Do this after [1], because the refactor may rename the classified functions. Gated
    on OQ-1, because the file is in no task''s files:.'
  - 'T-06 (qa): test-gen-decisions-index.py is red. The DEC-100, DEC-127 and DEC-208
    rulings are 39, 33 and 33 words at DECISIONS-INDEX.md:109,132,206, over the 30-word
    cap. Shorten them, still without asserting injection or a passing yield.'
  - 'T-06 (pm, substance, low): SPEC.md:779 refusal-table Unavailable row still says
    the call proceeds in the yield phase. Reword to ''proceeds (pre, post, dispatch);
    a yield is refused, never passed (BUG-2565)''. Operator perspective stays partial
    until fixed.'
  branch: feat/BUG-2565-digest-frontmatter-contract
  escalations:
  - id: E-1
    raised_by: harness-qa
    question: 'Amend T-03 files: to own tests/integration/canonical-reader-classification.json,
      so the red integration gate can be repaired'
    domain: plan scope
    routed_to: orchestrator -> operator
    resolution: pending
    decided_by: operator
    recorded_as: open_questions OQ-1
  - id: E-2
    raised_by: harness-code-reviewer, harness-security-reviewer
    question: 'Exit-0 unrecognized validator answer allowed (harness-hooks.ts:430-439):
      amend T-02 to add a positive ack in validate-digest.py, or accept as a residual
      and file a follow-up'
    domain: plan scope / signed D-05 reading
    routed_to: orchestrator -> operator
    resolution: pending
    decided_by: operator
    recorded_as: open_questions OQ-2
  adequacy_notes:
  - SC-08 has measured evidence only from QA's execution (16/16 parity ok at the pin).
    The code-reviewer was refused the command, so that lens is reasoning-only for
    SC-08.
  - QA receipts are host-interpreter results, not CI. The integration receipt is an
    honest red (runner_exit 1, tested_commit bb401aae).
  - SC-02's contract leg is witnessed by a mutation, not by a natural pre-fix red.
  - ui scoped out with a measured 83-path census.
  - Security's 'permissive frontmatter removes strict backstop' half is dismissed
    as settled by D-01; SC-05's probe shows OMP rejects off-schema yields.
  - 'The exit-0 finding keeps both reader ratings, code high and security med. Lead
    reading: not a regression, and SC-01''s enumerated classes are all met. It routes
    to the operator because its remedy is out of task scope; the FAIL already stands
    on the must_fix items.'
  - Every finding is task-scoped (it names its task in the summary). The schema forced
    scope to n/a (OQ-5).
  sc_status:
  - id: SC-01
    verdict: met
    method: automated unit
    evidence: omp-hooks.test.ts:2357,1807,2375; natural red against the 104252db hook
      (QA)
  - id: SC-02
    verdict: met
    method: automated unit
    evidence: omp-hooks.test.ts:2385; contract leg is mutation-witnessed (QA)
  - id: SC-03
    verdict: met
    method: automated unit
    evidence: omp-hooks.test.ts:1737; six witnesses red at base (QA)
  - id: SC-04
    verdict: met
    method: inspection
    evidence: 'pm: 0 outputSchema/schemaMode hits in the hook at the pin; digest-schema.ts
      absent'
  - id: SC-05
    verdict: met
    method: inspection
    evidence: 'pm: binding probe records the three observations; agent_blob 96f4332c
      equals the pin blob'
  - id: SC-06
    verdict: met
    method: automated integration
    evidence: test-check-omp-port.py 39/39 at the pin; 31/39 against the old check
      (QA). The integration kind as a whole is red on two other files.
  - id: SC-07
    verdict: partial
    method: automated unit + review
    evidence: 'Tests pass with 8 refusal mutants discriminating (QA). Code-reviewer:
      a $ref-reached root anyOf is admitted (digest_projection.py:124-133,177-190),
      and the generator does not preserve CRLF and other frontmatter bytes.'
  - id: SC-08
    verdict: met
    method: inspection (QA executed)
    evidence: T-03 parity 16/16 parity ok at bb401aae (review-harness-qa-c1.md:104).
      Reviewer execution was refused (OQ-3).
  - id: SC-09
    verdict: met
    method: inspection
    evidence: 'pm: letter met; SPEC.md:779 contradiction is tracked as must_fix'
  - id: SC-10
    verdict: met
    method: inspection
    evidence: 'pm: 7/7 amend dispositions met and the index regenerates equal. The
      index ruling word cap is red (must_fix).'
  - id: SC-11
    verdict: met
    method: inspection
    evidence: 'pm: probe records the 4 measurements; README:184-187 and BUILD:60-62
      state them (count advisory)'
  - id: PERSPECTIVE-operator
    verdict: partial
    method: inspection
    evidence: SPEC.md:779 (T-06)
  - id: PERSPECTIVE-orchestrator
    verdict: met
    method: inspection
    evidence: pm goal-check
  - id: PERSPECTIVE-code-maintainer
    verdict: met
    method: inspection
    evidence: pm goal-check; T-03 code-grade failure is tracked separately as must_fix
  needs_approval: true
  severity_max: high
  matrix_ok: false
  coverage_gaps:
  - 'Integration kind is red at the pin: test-gen-decisions-index.py and test-check-plan-routes.py
    pass at 104252db and fail at bb401aae.'
  - 'SC-07: no symlink-escape fixture; the inside(real) guard at digest_projection.py:76
    is never exercised alone (T-03).'
  - 'SC-06: test-check-omp-port.py:231-232 asserts ''task.structured'', not the file
    name ''.omp/config.yml''; live stderr does name it (T-04).'
  - SC-02's contract leg has no natural pre-fix red; it rests on a mutation proof.
  findings:
  - kind: substance
    scope: n/a
    severity: high
    reader: code-reviewer
    summary: 'T-03: _Loader.project grade 1 (digest_projection.py:121) and render
      grade 3 (gen-agent-output.py:29), below the production bar 4'
    why: The mandatory code-grade gate fails (pinned code-grade.py exit 1).
  - kind: substance
    scope: n/a
    severity: high
    reader: code-reviewer; harness-security-reviewer (med)
    summary: 'T-02: the yield accepts an unrecognized exit-0 validator answer (harness-hooks.ts:430-439,1857-1867)'
    why: Empty, malformed or unknown stdout at exit 0 is indistinguishable from success.
      Not a regression. The remedy needs validate-digest.py outside T-02's files,
      so it is escalated as OQ-2.
  - kind: substance
    scope: n/a
    severity: med
    reader: code-reviewer
    summary: 'T-03: a $ref-reached root anyOf is projected; SC-07 requires refusal
      (digest_projection.py:124-133,177-190)'
    why: The cycle stack doubles as a depth marker; an in-memory document produced
      an unsupported provider shape.
  - kind: substance
    scope: n/a
    severity: med
    reader: code-reviewer
    summary: 'T-03: regeneration rewrites CRLF bytes, duplicates a quoted structured
      key, and can orphan an indentationless sequence (gen-agent-output.py:32-46,62,80)'
    why: Breaks SC-07's byte-for-byte preservation for non-canonical frontmatter.
  - kind: substance
    scope: n/a
    severity: med
    reader: code-reviewer
    summary: 'T-03: four advisory grade-2 functions (resolve_ref, gen main, test walk,
      case_generator)'
    why: Advisory; does not determine the grade.
  - kind: substance
    scope: n/a
    severity: high
    reader: harness-qa
    summary: 'Integration red: test-check-plan-routes.py; canonical-reader-classification.json
      lacks the new readers'
    why: Regressed by the diff; the file is owned by no task (OQ-1).
  - kind: substance
    scope: n/a
    severity: high
    reader: harness-qa
    summary: 'Integration red: test-gen-decisions-index.py; T-06 rulings exceed the
      30-word cap (DECISIONS-INDEX.md:109,132,206)'
    why: A required kind is red, so matrix_ok is false.
  - kind: substance
    scope: n/a
    severity: low
    reader: harness-pm
    summary: 'T-06: SPEC.md:779 Unavailable row still says the yield proceeds'
    why: Contradicts the hook, SPEC:784-788 and DEC-100; leaves the operator perspective
      partial.
  - kind: form
    scope: n/a
    severity: low
    reader: code-reviewer; harness-pm
    summary: 'T-06: README:185 and BUILD:62 say ''repeated refusals''; the probe measured
      3'
    why: Advisory precision for SC-11.
  - kind: form
    scope: n/a
    severity: low
    reader: harness-pm
    summary: 'T-06: harness-team SKILL.md:146 ''injected lead schema'''
    why: Stale wording; advisory.
  - kind: form
    scope: n/a
    severity: med
    reader: harness-security-reviewer
    summary: 'T-01/T-06: probe receipt claims no refused payload reached the parent,
      but the parent''s failure text quotes it (research-yield-refusal-probe.md:117-129;
      BUILD.md:60-62)'
    why: Narrow the claim; the D-03 boundary question is OQ-4.
  - kind: substance
    scope: n/a
    severity: low
    reader: harness-security-reviewer
    summary: 'T-02: bound and redact child-visible validator diagnostics (harness-hooks.ts:398-404,432-435,880-885)'
    why: Can expose absolute paths or exception text. Base did the same; advisory.
  - kind: form
    scope: n/a
    severity: low
    reader: harness-pm
    summary: "SPEC \xA78.3 cites stale line numbers (harness-hooks.ts:1108, validate-digest.py:2200/:1827)"
    why: Stale at base and owned by no task; backlog candidate.
  readers:
  - reader: qa
    status: ran
    persona: harness-qa
    reason: n/a
  - reader: code
    status: ran
    persona: harness-code-reviewer
    reason: n/a
  - reader: security
    status: ran
    persona: harness-security-reviewer
    reason: n/a
  - reader: ui
    status: ran
    persona: harness-ui-reviewer
    reason: n/a
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: n/a
```
