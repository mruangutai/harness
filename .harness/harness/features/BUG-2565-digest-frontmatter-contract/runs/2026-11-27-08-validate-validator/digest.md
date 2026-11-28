# Validate c3: BUG-2565 at b9c98761

**ESCALATE (gate: FAIL).** Round 2 closed all three of F-1's named cases, and each was measured: red on ed064577, green at the pin. But the same class of defect survives in a fourth shape, and the operator-mandated guard cannot see it. A column-zero line inside a multiline `description` that looks like a generated key is silently deleted. The key set is unchanged, so the pre-write guard passes, the write exits 0, and `--check` then reports ok. The rework budget (3 rounds) is now spent, so the operator decides: ship with a residual, or authorise one more narrow repair.

Reviewed: 104252db..b9c98761ff82c408a1c58a974cfd10d60eee31b1, focused on ed064577..b9c98761. Members: qa PASS, code FAIL, security FAIL, ui PASS (scoped out, 18-path census), pm PASS.

## Closed (measured)

| Item | Evidence |
|---|---|
| F-1's three c2 cases (dash sibling key, commented sequence, escaped quoted key) | QA (a): the pin's test file, run against ed064577's generator, gives exit 1 with exactly :256, :260 and :264 failing; at the pin it passes. Code's raw-byte CLI table confirms all three are preserved |
| Suite | unit 69, integration 95, runner_exit 0 (receipts in `qa/`) |
| Parity / port / grade | `--check` ok, 16/16 byte-identical, `check-omp-port.py` passes, production `render` grade 4 |
| Scope of the fix | Inside the operator's ruling and T-03's files (pm, code) |

## Remaining: one gating finding

**F-2 · T-03 · substance · code high / security med (both transcribed). Location: `.claude/skills/harness/bin/gen-agent-output.py:91-99` (`kept`), with the guard at `:110-128` (`other_keys`/`render`).**

Example input:
```
description: 'keep
"out\u0070ut": middle
end'
```
followed by stale `structured`/`output` entries. `kept()` treats the middle physical line as the start of the generated key, so the description becomes `keep end`. `other_keys` compares key **sets** only, which are identical before and after, so the write proceeds (exit 0) and the later `--check` is ok.
- The escaped spelling is a **regression from round 2**: ed064577 preserved it (security measured this). Round 2's `harness_yaml.load_str` key decoding is what made the line match.
- The bare `output: middle` lookalike fails the same way (code). Whether it also failed before round 2 was not measured.
- Two readers measured it independently. It is caught by no test and no gate. None of the 16 shipped agents triggers it.

This is the same root as F-1: generated spans are chosen from physical lines, not from parsed YAML. Patching shapes one at a time has now failed to converge twice. The operator's prescribed guard compares key sets, and value loss passes straight through it. SC-07 ("other frontmatter keys byte-for-byte unchanged", BRIEF.md:29) is therefore **partial**. PM graded it met, but pm's 16-shape probe did not include a key lookalike inside a value, while code and security both produced that counterexample. On the letter I side with them.

My severity reading is med. The trigger is a multiline quoted scalar with a column-0 continuation line that spells a generated key. PyYAML accepts it; [INFERENCE] YAML 1.2 requires indentation of at least 1 there. No shipped agent is affected. Code's `high` is transcribed and gates.

**Repair (converges by construction; main-session-direct, T-03 files):**
1. At `gen-agent-output.py:110-117`, have `other_keys` return the parsed mapping minus GENERATED (`{k: v for k, v in parsed.items() if k not in GENERATED}`) instead of its key set. At `:126`, compare the two mappings. Any change to a non-generated value then refuses with nothing written. This closes the class fail-closed, whatever the line shape.
2. Add witnesses in `tests/unit/test-digest-projection.py`: the escaped and bare lookalike-in-description cases expect exit 2 and unchanged bytes, observed RED first. Add one row that kills QA's mutant M2 (guard deleted), for example `output: &o` plus `copy: *o`. Today no test kills M2, so the operator-mandated guard is unwitnessed.
3. Full byte-preserving regeneration of such inputs would require span selection from `yaml.compose` node marks. That is optional, not needed for SC-07 once step 1 refuses.

## Advisory (non-blocking, ranked)

1. QA, med, T-03: mutant M2 survives. Deleting the pre-write guard at `:126-128` keeps the suite green, although QA showed the guard is live (it refuses `? output`, `!!str structured` and alias inputs). This is folded into repair step 2 above.
2. QA (state unchanged from run 07 advisory 1), low, T-03: the all-or-nothing write at `:164-168` has no witness. Security also records that a write-phase I/O failure leaves files inconsistent across personas (tampering, unmitigated). The persona preflight refusal is mitigated.
3. Code, med, T-03: a multiline flow `output: {…}` with a column-zero `}` cannot be regenerated. It fails closed (exit 2, nothing written), so this is not data loss.
4. Code, observed in its table, T-03: with `output: stale`, comment lines between it and the next key are dropped. Comments are not keys, so this is outside SC-07's letter. Low.
5. Code, med (grade record), T-03: `case_generator_edges` (`test-digest-projection.py:245`) is a new grade-2 function with reasons recorded. It does not gate.
6. Run 07 advisories 2–5 are unchanged and outside round 3's authorisation.

## Operator decision (OQ-1)
- **(a)** One more narrow round: repair steps 1–2 only. That is a few lines in `other_keys`/`render` plus two or three witnesses. Unlike rounds 2–3, it closes the class rather than one more shape, so it converges.
- **(b)** Ship with F-2 as a named residual and a follow-up issue, recording SC-07 as partial. No shipped agent triggers it, and the trigger shape is one PyYAML accepts but the YAML 1.2 spec arguably forbids.

I recommend (a) if any budget can be found, because a silent value loss behind a green `--check` is the worst failure direction. Otherwise (b) is defensible on the trigger's rarity.

## Adequacy
- QA receipts come from the host interpreter, not CI.
- Fail-first evidence for SC-01, SC-02, SC-03 and SC-06 carries over from round 1. Their subject files are unchanged since bb401aae (pm).
- The PM/code SC-07 contradiction is resolved on measured counterexample evidence, not on judgement.
- The F-2 count covers two shapes, escaped and bare, both reported by code. Security independently measured only the escaped one against ed064577.

```yaml
VERDICT: ESCALATE
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2565-digest-frontmatter-contract/.harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-08-validate-validator/digest.md
DIGEST:
  headline: b9c98761 fixes F-1's three named cases. Each was measured red on ed064577
    and green at the pin, and unit 69 and integration 95 are green. One silent value
    loss remains in T-03 (F-2). The generator deletes a generated-key lookalike line
    that sits inside a multiline description, and --check then reports ok. The key-set
    guard cannot see this. SC-07 is partial, the budget is spent, and the operator
    must choose between one narrow round and shipping with a residual.
  open_questions:
  - id: OQ-1
    question: 'F-2 (T-03, rated high by code and med by security). The site is gen-agent-output.py:91-99
      (kept) and :110-128 (other_keys/render). A column-0 line inside a multiline
      quoted description that spells a generated key, e.g. ''"out\u0070ut": middle''
      or bare ''output: middle'', is deleted. The key set is unchanged, so the guard
      passes, the write exits 0 and --check reports ok. The escaped spelling regressed
      in round 2 (ed064577 preserved it); whether the bare spelling regressed was
      not measured. No shipped agent triggers it. SC-07''s byte-preservation letter
      is partial. The rework budget (3 rounds) is spent. Option (a), one more narrow
      round: other_keys returns the parsed mapping minus GENERATED rather than its
      key set, and render refuses on any change to a non-generated value. Add RED-first
      witnesses for the escaped and bare lookalikes (exit 2, bytes unchanged) and
      one row that kills mutant M2. This closes the class fail-closed and converges.
      Option (b): ship with F-2 as a named residual plus a follow-up issue, and record
      SC-07 as partial. The lead recommends (a) if budget allows; (b) is defensible
      on rarity.'
    blocking: true
  files_touched:
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-08-validate-validator/state.yaml
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/runs/2026-11-27-08-validate-validator/digest.md
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/observations/harness-pm.md
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Unit 69 and integration 95 green at b9c98761 (runner_exit 0). All 3
      F-1 witnesses are red on ed064577 and green at the pin. Mutants M1, M3 and M4
      are killed; M2 (pre-write guard deleted) survives.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: F-1's three cases pass, but T-03 still silently truncates a multiline
      description when it contains a generated-key lookalike line, and --check accepts
      the result.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: T-03 still silently removes text from a valid non-generated YAML value.
      ed064577 preserved the escaped variant.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B scoped out: the 18-path delta changes no rendered or interactive
      UI.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: 3/3 perspectives pass, SC-01..SC-11 met and 7/7 dispositions met. The
      fix stayed inside the operator's ruling and T-03's files. Its 16-shape probe
      did not include a key lookalike inside a value.
    files_touched:
    - .harness/harness/features/BUG-2565-digest-frontmatter-contract/observations/harness-pm.md
  must_fix:
  - 'F-2 T-03 (code-reviewer high, security-reviewer med; substance). gen-agent-output.py:91-99
    kept() selects generated spans from physical lines, so a key-lookalike continuation
    line inside a multiline quoted description is deleted. The guard at :110-128 compares
    key sets only, so the change passes it; the write exits 0 and --check reports
    ok. The escaped variant regressed in round 2. Repair: other_keys returns {k: v
    for k, v in parsed.items() if k not in GENERATED}, and render (:126) compares
    the mappings and refuses with nothing written on any difference. Add RED-first
    witnesses in tests/unit/test-digest-projection.py for the escaped and bare lookalike-in-description
    cases (exit 2, bytes unchanged), plus one row that kills mutant M2 (guard deleted).
    The budget is spent, so this is routed via OQ-1.'
  branch: feat/BUG-2565-digest-frontmatter-contract
  escalations:
  - id: E-1
    raised_by: harness-code-reviewer, harness-security-reviewer
    question: Authorise one more narrow round (value-equality guard plus witnesses)
      beyond the spent 3-round budget, or ship with F-2 as a named residual and SC-07
      partial?
    domain: rework budget / SC-07 acceptance
    routed_to: orchestrator -> operator
    resolution: pending
    decided_by: operator
    recorded_as: open_questions OQ-1
  adequacy_notes:
  - 'F-1''s three c2 cases are closed on measured evidence: QA ran the pin''s tests
    against ed064577''s generator and got exactly :256, :260 and :264 red; code''s
    raw-byte CLI table agrees.'
  - SC-07 contradiction resolved. Pm graded it met on a 16-shape probe. Code and security
    each produced a lookalike-in-value counterexample that pm's probe lacked. The
    lead rules SC-07 partial on the letter of BRIEF.md:29.
  - 'Root-cause note: rounds 2 and 3 each patched line shapes and each surfaced a
    new shape. The proposed repair compares values rather than shapes, so it closes
    the class fail-closed.'
  - 'Lead severity reading for F-2 is med: the trigger is a column-0 continuation
    of a quoted scalar that PyYAML accepts ([INFERENCE] YAML 1.2 forbids it), and
    no shipped agent is affected. Code''s high is transcribed and gates.'
  - 'QA''s mutant M2 survives: the operator-mandated pre-write guard is live but no
    test kills its deletion.'
  - The ui reader scoped out on an 18-path census showing no UI.
  - QA receipts come from the host interpreter, not CI. Fail-first evidence for SC-01,
    SC-02, SC-03 and SC-06 carries from round 1 on unchanged subject files.
  - Every finding is task-scoped to T-03; the schema forces scope to n/a.
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
    evidence: 0 retired symbols; digest-schema.ts absent (pm, code)
  - id: SC-05
    verdict: met
    method: inspection
    evidence: binding probe; documentor blob matches pin (pm, code)
  - id: SC-06
    verdict: met
    method: automated integration
    evidence: test-check-omp-port.py:205; integration 95 green (QA receipt)
  - id: SC-07
    verdict: partial
    method: automated unit + review
    evidence: '3 F-1 witnesses red on ed064577 and green at the pin (QA). Byte-preservation
      clause broken by F-2: gen-agent-output.py:91-99 deletes a lookalike line inside
      a multiline description (code, security)'
  - id: SC-08
    verdict: met
    method: inspection (QA executed, OQ-3)
    evidence: 16/16 parity at b9c98761 (QA, pm)
  - id: SC-09
    verdict: met
    method: inspection
    evidence: docs unchanged since c2 (pm, code)
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
    evidence: SPEC.md:779 (pm)
  - id: PERSPECTIVE-orchestrator
    verdict: met
    method: inspection
    evidence: SC-03, SC-05 (pm)
  - id: PERSPECTIVE-code-maintainer
    verdict: partial
    method: inspection
    evidence: pm graded it met; the lead downgrades it because it rests on SC-07,
      which is partial on F-2
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - 'T-03 gen-agent-output.py:126-128: no test kills mutant M2 (pre-write guard deleted);
    the guard is live but unwitnessed (QA, med).'
  - 'T-03 gen-agent-output.py:164-168: the all-or-nothing write has no witness; state
    unchanged from run 07 (QA, low).'
  - F-2's lookalike-in-value deletion is caught by no test or gate.
  findings:
  - kind: substance
    scope: n/a
    severity: high
    reader: code-reviewer
    summary: 'T-03 F-2: gen-agent-output.py:91-99,110-128 deletes a generated-key
      lookalike line inside a multiline description; the key-set guard passes and
      --check reports ok. SC-07 mismatch.'
    why: Silent non-generated value loss; the escaped variant regressed in round 2.
      Merged with security's report.
  - kind: substance
    scope: n/a
    severity: med
    reader: security-reviewer
    summary: 'T-03: same lookalike deletion (duplicate of F-2); ed064577 preserved
      the escaped variant.'
    why: Merged into F-2; kept so the second rating stays traceable.
  - kind: substance
    scope: n/a
    severity: med
    reader: qa
    summary: 'T-03: mutant M2 (pre-write guard at gen-agent-output.py:126-128 deleted)
      survives the suite.'
    why: The operator-mandated guard is unwitnessed. Folded into F-2's repair step
      2.
  - kind: substance
    scope: n/a
    severity: low
    reader: qa
    summary: 'T-03: no witness for the all-or-nothing write at gen-agent-output.py:164-168;
      security records the write-phase I/O inconsistency as unmitigated.'
    why: Advisory; state unchanged from run 07.
  - kind: substance
    scope: n/a
    severity: med
    reader: code-reviewer
    summary: 'T-03: a multiline flow output with a column-zero closing brace cannot
      be regenerated (gen-agent-output.py:65-84,125-128).'
    why: 'Advisory: it fails closed with exit 2 and nothing written, so no data is
      lost.'
  - kind: substance
    scope: n/a
    severity: med
    reader: code-reviewer
    summary: 'T-03: new grade-2 test function case_generator_edges at tests/unit/test-digest-projection.py:245.'
    why: Advisory grade record with reasons; does not gate.
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
