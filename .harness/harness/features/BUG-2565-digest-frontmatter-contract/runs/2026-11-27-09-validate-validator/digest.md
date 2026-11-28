# Validate c4: BUG-2565 at dca6017d

**ESCALATE (gate: FAIL, budget spent).** Round 3 closed F-2 exactly as the operator ruled, and this was measured. Both lookalike witnesses fail on b9c98761's generator and pass at the pin. Mutant M2 (guard deleted) and two weaker-guard mutants are now killed.

Two further silent-loss shapes remain, and both were already present at b9c98761. They have the same root as F-1 and F-2: the generator picks the spans it rewrites from physical lines. Rounds 2, 3 and 4 each closed one shape, and each time a reader found another. The authorised rounds (4/4) are used up, so the operator decides whether to ship with a residual or authorise a structural repair.

Reviewed: 104252db..dca6017d59edf5222bbd41de08d2a8a2a0f74c51, focus b9c98761..dca6017d. Members: qa PASS, code FAIL, security FAIL, ui PASS (scoped out), pm PASS. The code reviewer's first dispatch ended without a review: the provider refused it with a `cyber_policy` error. I re-dispatched it once with neutral wording and it completed.

## Closed (measured)

| Item | Evidence |
|---|---|
| F-2 (bare and escaped lookalike inside a multiline description) | QA: witnesses red on the b9c98761 generator, green at the pin. Code and security reproduced exit 2 with bytes unchanged |
| Run 08 coverage gap: M2 survives | QA: M2, M2b (key-set guard) and M2c (value-blind guard) are all killed. M1, M3 and M4 stay killed |
| Suite | unit 69, integration 95, `runner_exit` 0 (receipts in `qa/`). 16/16 parity; `--check` ok |
| Scope | Inside the c3 ruling and T-03's files (pm) |

## Remaining: two gating findings (T-03, substance, med)

**F-3: a merge override is deleted, and an int-to-bool change passes the value guard.** Code and security each measured this independently. Location: `.claude/skills/harness/bin/gen-agent-output.py:87-95`, with the guard at `:126-128`.
- **Trigger:** a nested flow mapping inherits `output: false` through `<<` and overrides it with a column-0 line `output: 0,`.
- **What happens:** the generator treats that line as the root `output` key and deletes it. The value changes from `int 0` to `bool False`. Python reports `0 == False`, so the guard passes, the write exits 0, and `--check` exits 0.
- **Variant:** an explicit `!!int 0` over an inherited `0` loses the line while the parsed value stays equal. No value comparison can see this variant (code).
- **Against the ruling:** this violates the operator ruling's "any difference" letter on the int/bool case, and SC-07's byte letter on both variants.

**F-4: the parse boundary and the rewrite boundary differ.** Only code measured this. Location: `gen-agent-output.py:99-114` and `:126-128`.
- **Trigger:** a VT or NEL character around a false `---` fence.
- **What happens:** the canonical reader stops early, so the guard compares only a prefix. The writer edits the longer LF-delimited slice and deletes a description line, with exit 0 and then `--check` exit 0.
- **Pins:** present at both.

**Severity.** Both readers rate F-3 med, and I agree. Code alone rates F-4 med. Neither finding is a regression of round 4, and no shipped agent triggers either. Both are silent value loss behind a green `--check`, which is the worst failure direction this feature exists to prevent. That is why they gate.

**Repair, converging by construction.** Select the generated spans from `yaml.compose` root-mapping node marks, so the parser defines both what is parsed and what is rewritten. Then refuse when any removed byte falls outside a root-level generated key/value node. This closes F-2, both F-3 variants and F-4 together, with no per-shape patch. As a cheap belt, make the guard compare types as well as values, for example by recursing on `(type(v), v)`. Witnesses, observed red first: the int-to-bool merge override, the `!!int` equal-value override, and the VT/NEL fence. Each must exit 2 with the bytes unchanged. Run 08 called the compose-marks step optional. It is required now, because value comparison alone is shown not to converge.

## Advisory (non-blocking, ranked)

1. **F-5** (code med, security low; T-03; `gen-agent-output.py:127,140-146`): a recursive alias (`extra: &loop [*loop]`) raises `RecursionError` and exits 1, and nothing is written. It fails closed. Generation became unavailable where b9c98761 accepted the input. A clean exit-2 refusal is the fix.
2. **F-6** (code med, pm low as A-1; T-03; `:126-128`): a block scalar `|` or `>` that ends the frontmatter is now refused (exit 2, nothing written). The refusal is correct under the ruling: the parsed trailing newline really changes. No agent is affected (0 block scalars in .omp/agents). It goes to the backlog.
3. **Invalid UTF-8** (code low; `:136-146`): crashes with exit 1 before the refusal handler. It fails closed and is unchanged from c3.
4. **QA form, low**: `refused()` (`tests/unit/test-digest-projection.py:270-281`) checks exit 2, unchanged bytes and "nothing written", but not the refusal cause.
5. Run 08 advisories 2-6 are unchanged: the write is still not all-or-nothing (security re-measured this), and `case_generator_edges` is still grade 2.

## Operator decision (OQ-1)

- **(a)** One structural round: the compose-marks span selection plus the type-aware guard and three witnesses described above. It is larger than round 4, but it removes the cause rather than another shape.
- **(b)** Ship with F-3 and F-4 as named residuals in a follow-up issue (alongside #2593), and record SC-07 as partial. Both shapes predate round 4 and no shipped agent triggers them. The triggers are a column-0 continuation inside a nested flow mapping with merge keys, and VT/NEL control characters in frontmatter.

I recommend **(b) with the follow-up issue carrying repair (a)'s design**. Round 4 did what the ruling asked. Another shape-level round would repeat a pattern that has failed to converge three times. The structural repair is a design change that deserves its own scoped work rather than a fifth unbudgeted round.

## Adequacy

- QA receipts come from the host interpreter, not CI.
- Fail-first evidence for SC-01, SC-02, SC-03 and SC-06 carries over from c1, on subject files that have not changed.
- The SC-07 contradiction is resolved as in run 08. PM graded SC-07 met on an 18-shape probe. Code and security produced measured counterexamples that the probe did not contain, so SC-07 is partial on the letter of BRIEF.md:29.
- F-3 was reproduced independently by two readers. F-4 rests on one reader's repro, on both pins. I could not re-run it without a shell.
- The ui reviewer scoped out on an 18-path delta census.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: 'dca6017d closes F-2 on measured evidence: witnesses are red on b9c98761,
    M2/M2b/M2c are killed, and unit 69 plus integration 95 are green. Two silent-loss
    shapes predate round 4 and remain in T-03: F-3, a merge override where int-to-bool
    passes the value guard, and F-4, a VT/NEL fence that splits the parse and rewrite
    boundaries. SC-07 is partial and the 4/4 budget is spent, so the operator decides.'
  open_questions:
  - id: OQ-1
    question: 'F-3 and F-4 (T-03, med, substance; both present at b9c98761 too). F-3
      is at gen-agent-output.py:87-95,126-128. Trigger: a nested flow mapping that
      inherits output:false via << and overrides it with a column-0 ''output: 0,''
      line. The line is deleted; int 0 becomes bool False, which Python''s == does
      not see; the write exits 0 and --check is ok. A ''!!int 0'' over an inherited
      0 loses the line with no value change at all (code, security). F-4 is at gen-agent-output.py:99-114,126-128.
      Trigger: VT/NEL around a false fence. The reader parses only a prefix while
      the writer edits the longer LF slice, a description line is deleted, and --check
      is ok (code). No shipped agent triggers either, and the 4-round budget is spent.
      Option (a): one structural round. Select generated spans from yaml.compose root-mapping
      node marks, refuse on any removed byte outside a root generated node, compare
      types as well as values, and add three RED-first witnesses. Option (b): ship
      with F-3 and F-4 as named residuals in a follow-up issue carrying (a)''s design,
      and record SC-07 as partial. The lead recommends (b).'
    blocking: true
  files_touched:
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-09-validate-validator/state.yaml
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-09-validate-validator/digest.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-09-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-09-validate-validator/qa/manifest-integration.json
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/observations/harness-qa.md
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Unit 69 and integration 95 are green at dca6017d. The F-2 witnesses
      are red on b9c98761 and green at the pin. M2, M2b and M2c are now killed, and
      M1, M3 and M4 stay killed. 16/16 parity, and --check is ok.
    files_touched:
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-09-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-09-validate-validator/qa/manifest-integration.json
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: The F-2 witnesses, F-1's three cases and all 16 agents pass. T-03 still
      silently loses a typed merge override, and it can write past a delimiter it
      never validated. The first dispatch was refused by the provider's cyber_policy
      and redispatched once.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: Both F-2 cases refuse with bytes unchanged. A nested YAML merge override
      still disappears and can change a non-generated value's type without detection.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B scoped out: the 18-path round-4 delta changes no rendered UI.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: '3/3 perspectives, SC-01..SC-11 and 7/7 dispositions are met, with the
      lookalike shape now included. The round stayed inside the c3 ruling and T-03''s
      files. Advisory A-1: a block-scalar false refusal.'
    files_touched: []
  must_fix:
  - 'F-3 T-03 (code-reviewer med, security-reviewer med; substance). gen-agent-output.py:87-95,126-128
    deletes a column-0 ''output: 0,'' override inside a nested flow mapping that inherits
    output:false via <<. Because 0 == False, the value guard passes: the write exits
    0 and --check is ok. A ''!!int 0'' over an inherited 0 loses bytes with no value
    change. Repair: select generated spans from yaml.compose root-mapping node marks
    and refuse any removed byte outside a root generated node. Also make the guard
    compare types (recurse on (type(v), v)). Add RED-first witnesses for both variants
    (exit 2, bytes unchanged). Routed via OQ-1 because the budget is spent.'
  - 'F-4 T-03 (code-reviewer med; substance). gen-agent-output.py:99-114,126-128:
    with a VT/NEL-flanked false fence, the reader parses a prefix while the writer
    edits the longer LF slice. A description line is deleted, the write exits 0 and
    --check is ok. Repair: parse exactly the slice being rewritten (covered by F-3''s
    compose-marks design). Add a RED-first witness (exit 2, bytes unchanged). Routed
    via OQ-1.'
  branch: feat/BUG-2565-digest-frontmatter-contract
  escalations:
  - id: E-1
    raised_by: harness-code-reviewer, harness-security-reviewer
    question: With 4/4 authorised rounds spent, authorise one structural round (compose-marks
      span selection plus a type-aware guard) or ship with F-3 and F-4 as named residuals
      and SC-07 partial?
    domain: rework budget / SC-07 acceptance
    routed_to: orchestrator -> operator
    resolution: pending
    decided_by: operator
    recorded_as: open_questions OQ-1
  adequacy_notes:
  - 'F-2 closure is measured three ways: QA ran the pin''s tests against b9c98761''s
    generator, and code and security each reproduced it on raw bytes.'
  - Run 08's M2 coverage gap is closed. M2b (key-set guard) and M2c (value-blind guard)
    are also killed, so the value leg is witnessed.
  - SC-07 is ruled partial on the letter of BRIEF.md:29, the same reasoning as run
    08. pm's 18-shape probe did not contain the merge-override or VT/NEL shapes that
    code and security measured.
  - 'Root cause: rounds 2-4 each closed one physical-line shape and each surfaced
    a new one. A value guard alone cannot see the equal-value byte loss (the ''!!int''
    variant), so it does not converge. Span selection from parser node marks does.'
  - F-3 was reproduced independently by two readers. F-4 rests on code's repro alone,
    at both pins. The lead holds no shell to re-run it.
  - 'The code reviewer''s first spawn produced no review: the provider refused it
    (cyber_policy). One redispatch with neutral wording completed.'
  - QA receipts come from the host interpreter, not CI. Fail-first evidence for SC-01,
    SC-02, SC-03 and SC-06 carries over from c1 on unchanged subject files.
  - The ui reviewer scoped out on an 18-path delta census.
  - Every finding is task-scoped to T-03; the reader schemas record scope as none/n/a.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated unit
    evidence: omp-hooks.test.ts:2357; red at base (QA c1); unchanged
  - id: SC-02
    verdict: met
    method: automated unit
    evidence: omp-hooks.test.ts:2385 (QA c1)
  - id: SC-03
    verdict: met
    method: automated unit
    evidence: omp-hooks.test.ts:1737 (QA c1)
  - id: SC-04
    verdict: met
    method: inspection
    evidence: .omp unchanged since b9c98761; symbol census stands (pm)
  - id: SC-05
    verdict: met
    method: inspection
    evidence: notes/research-frontmatter-binding-probe.md (pm)
  - id: SC-06
    verdict: met
    method: automated integration
    evidence: test-check-omp-port.py:205; integration 95 green (QA receipt)
  - id: SC-07
    verdict: partial
    method: automated unit + review
    evidence: F-2 witnesses green at the pin, red on b9c98761, M2 killed (QA). The
      byte-preservation letter is broken by F-3 (gen-agent-output.py:87-95, merge
      override deleted, code+security) and F-4 (:99-114, VT/NEL fence, code)
  - id: SC-08
    verdict: met
    method: inspection (QA executed)
    evidence: 16/16 parity at dca6017d (QA, pm)
  - id: SC-09
    verdict: met
    method: inspection
    evidence: docs unchanged b9c98761..dca6017d (pm)
  - id: SC-10
    verdict: met
    method: inspection
    evidence: 7/7 amend dispositions; index byte-equal (pm)
  - id: SC-11
    verdict: met
    method: inspection
    evidence: probe receipt and README/BUILD unchanged (pm)
  - id: PERSPECTIVE-operator
    verdict: met
    method: inspection
    evidence: pm c4
  - id: PERSPECTIVE-orchestrator
    verdict: met
    method: inspection
    evidence: SC-03, SC-05 (pm)
  - id: PERSPECTIVE-code-maintainer
    verdict: partial
    method: inspection
    evidence: pm graded this met. The lead downgrades it because it rests on SC-07,
      which is partial on F-3 and F-4
  needs_approval: true
  severity_max: med
  matrix_ok: true
  coverage_gaps:
  - F-3 (merge override int->bool and the '!!int' equal-value variant) is caught by
    no test or gate.
  - F-4 (VT/NEL false fence) is caught by no test or gate.
  - tests/unit/test-digest-projection.py:270-281 refused() does not check the refusal
    cause (QA, form, low).
  - 'gen-agent-output.py write phase: the all-or-nothing write is still unwitnessed
    (unchanged from run 07/08).'
  findings:
  - kind: substance
    scope: n/a
    severity: med
    reader: code-reviewer
    summary: 'T-03 F-3: gen-agent-output.py:87-95,126-128 deletes a nested merge override
      line. int 0 becomes bool False and passes the value guard; ''!!int 0'' over
      an inherited 0 loses bytes with no value change. Exit 0, --check ok, at both
      pins.'
    why: Silent non-generated loss against SC-07 and the c3 ruling's 'any difference'.
      Merged with security's report.
  - kind: substance
    scope: n/a
    severity: med
    reader: security-reviewer
    summary: 'T-03: the same merge-override deletion and type change (duplicate of
      F-3).'
    why: Merged into F-3; kept so the second independent rating stays traceable.
  - kind: substance
    scope: n/a
    severity: med
    reader: code-reviewer
    summary: 'T-03 F-4: gen-agent-output.py:99-114,126-128 parses a prefix but rewrites
      a longer LF slice when a VT/NEL flanks a false fence. A description line is
      deleted; exit 0, --check ok, at both pins.'
    why: Silent loss behind the guard. Measured by one reader.
  - kind: substance
    scope: n/a
    severity: med
    reader: code-reviewer
    summary: 'T-03 F-5: gen-agent-output.py:127,140-146 hits RecursionError on a recursive
      alias (exit 1, nothing written); b9c98761 accepted it. Security rates it low.'
    why: 'Advisory: it fails closed. The availability regression wants a clean exit-2
      refusal.'
  - kind: substance
    scope: n/a
    severity: med
    reader: code-reviewer
    summary: 'T-03 F-6: a block scalar | or > that ends the frontmatter is now refused
      (exit 2, nothing written); pm rates it low (A-1).'
    why: 'Advisory: the refusal is correct under the ruling and no agent has a block
      scalar. Backlog.'
  - kind: substance
    scope: n/a
    severity: low
    reader: code-reviewer
    summary: 'T-03: invalid UTF-8 crashes with exit 1 before the refusal handler (gen-agent-output.py:136-146);
      unchanged from c3.'
    why: 'Advisory: it fails closed and the state is unchanged.'
  - kind: form
    scope: n/a
    severity: low
    reader: qa
    summary: 'T-03: refused() at tests/unit/test-digest-projection.py:270-281 does
      not check the refusal cause.'
    why: Advisory test-precision gap.
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
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2565-digest-frontmatter-contract/.harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-09-validate-validator/digest.md
```
