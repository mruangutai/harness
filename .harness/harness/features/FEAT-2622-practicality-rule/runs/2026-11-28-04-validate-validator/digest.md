# FEAT-2622 validate c3: ESCALATE. MF-1 to MF-4 are closed and nothing is left for a fix round. One high security finding needs an operator ruling

This run reviewed `3e979ae3..0ce1c841` (review_sha `0ce1c841f4534e3720e95927d61f43a162aa6a13`), run `2026-11-28-04-validate-validator`, cycle 3. This is the last re-review under VAL-OQ-04. Five readers ran in one wave. `severity_max: high`, transcribed from security. `must_fix` is empty.

## Closure of the c2 must-fix items

| c2 item | Status at 0ce1c841 | Measured by |
|---|---|---|
| MF-1: an unmatched open discounted row relieved | **Closed.** | QA: `no-current-finding-denied` is red at edcda5be and green at the pin, and the presence-drop mutant turns it red. Code-reviewer re-ran its omitted-current-high scenario offline and relief was denied. |
| MF-1 per-leg acceptance | **Met.** | QA ran all 5 mutants, and each turns exactly one named case red, as the receipt claims. c2's M10 (the current-exposure leg) is now witnessed by `current-discounted-high-denied`. |
| MF-2: carve-out blind to the team's must_fix | **Closed.** | QA: `team-mustfix-denied` is red at edcda5be. Security executed `_carveout_inputs`/`_plan_reader_carveout`, and a non-empty must_fix is refused over both open and resolved rows. |
| MF-3: DEC-123 vs D-06 | **Closed.** | pm: DEC-123 at L2497-2506, D-06 at L8877-8884 and the code state one rule, and the index matches. Code-reviewer concurs. |
| MF-4: triage reason names the reader's severity | **Closed.** | pm: product-lead L444-452 and `teams/plan.yaml` L227-232. |

## Escalation: SEC-03 (security, high, substance, T-01/T-02)

**Claim.** Both ratings that open-row relief reads are authored by the product lead:
- the panel row, which pm's record-panel transcribes from the lead's fan-in;
- the current team-digest finding.

The security reviewer's note says: "A compromised product lead exercising ordinary plan fan-in authority can mask a genuine reader `FAIL` on a first-seen gating finding by changing that finding's rating in both lead-authored records."

**Security's exposure:** {plausible, regression, adversary}. Security executed the roll-up difference at an in-memory seam: the matching discounted-med open row relieves at the pin and not at base. The provenance path was traced statically, and no live bypass ran. Security asks for an operator ruling, not a third round.

**My rating is lower: med, not gating.** P-04 requires me to state both ratings, so here they are side by side.
- **The trust class was already ruled.** The VAL-OQ-03 ruling accepted that "the lead's must_fix union is trusted the same way on base's resolved-row path and in every other roll-up". The lead-to-roll-up hop is not a cross-trust boundary, so the adversary exception does not reach it. SEC-03 is the same actor and the same boundary, falsifying a different lead-authored field.
- **Base already trusts a lead-authored disposition.** At base, the resolved-row path relieves on a plan.yaml `disposition: resolved` that the plan team itself records (`validate-digest.py` `_open_row_reason`, first clause, unchanged in kind). [INFERENCE: I did not verify whether record-panel requires independent evidence before it writes `resolved`.] On that reading, vs_today is no_worse for a dishonest lead.
- **Lowering is signed design.** Signed D-03 makes the lead the authority that lowers a discounted finding before writing the fan-in. Its predecessor reason says "the lead owns part of the severity it transcribes". The D-03 reason line must name the reader's original severity and exposure, so a falsified rating is left on record and is detectable after the fact, though not prevented.
- **The remedy does not fit a fix round (G-06).** Security's remedy, binding relief to independently attributable reader rating evidence, needs two approval-gated changes:
  - a provenance contract that the reader return does not carry today;
  - an amendment of signed D-03 and D-06.
  No fix cycle may legally apply it, and VAL-OQ-04 leaves no round anyway.

**Recommendation: accept the residual, as for VAL-OQ-03.** Record it as a known limit of DEC-123's open-row relief. If the operator wants it closed, it is a follow-up feature for reader-return provenance, not a rework of this one.

## Advisory (not gating)

- **QA-F4** (qa, low, substance, T-01): a mutant that replaces `all()` with `any()` over current findings sharing one PF id stays green in both test files. QA's executed probes show it would relieve a discounted med plus a plausible high with the same id. The pin is correct: code-reviewer's offline probe of exactly that case was denied. The exposure is contrived/no_worse/harness, so there is no test demand and no round.
- **Advisories carried from c2:** the SC-11 letter gap, QA-F2, mutants M4/M5/M6/M7 and QA-F3. All were ruled earlier and were not re-raised.
- **Environment:** receipts are from this host's interpreter, not CI (G-03). tsc is absent, and the diff touches no TypeScript.

## Assurance bound (P-09)

- QA executed both the matrix and the mutants.
- Code-reviewer executed offline probes covering:
  - several current findings sharing a PF id;
  - unattributed findings;
  - must_fix shapes;
  - a resolved row alongside a current high.
- Security executed the carve-out probes. No guard refused a capability.
- SEC-03's provenance chain is static only.
- The post-pin commit check falls to code-reviewer's note. I did not run it.

## Members

| step | persona | verdict | note |
|---|---|---|---|
| qa | harness-qa | PASS | Unit 74/74 and integration 94/94. Receipts are in `qa/`. fail_first covers all 8 automated SCs. 5/5 mutants are red. |
| code | harness-code-reviewer | PASS | MF-1 to MF-4 are closed. There are no findings, and 45 graded functions pass. |
| security | harness-security-reviewer | FAIL | MF-2 is closed. SEC-03 is high and needs an operator ruling. |
| ui | harness-ui-reviewer | PASS | Scoped out: 68 paths, none UI. |
| goalcheck | harness-pm | PASS | All perspectives pass. DEC-206 and DEC-123 are met. |

Notes: `notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c3.md` and `notes/research-FEAT-2622-practicality-rule-goalcheck-validate-c3.md`.

```yaml
VERDICT: ESCALATE
artifact: .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-04-validate-validator/digest.md
DIGEST:
  headline: 'ESCALATE at 0ce1c841. Mutation and execution show MF-1 to MF-4 closed,
    the matrix is green (74/74, 94/94) and all SCs are met. One security finding is
    left: SEC-03 (high) says both ratings that open-row relief reads are authored
    by the product lead. It needs an operator ruling; the lead recommends accepting
    it as in VAL-OQ-03, rated med. No fix round is needed.'
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: 'Matrix green at 0ce1c841: unit 74/74 and integration 94/94. Each of
      the 5 fix-round mutants turns exactly one case red. MF-1 and MF-2 are red at
      edcda5be. M10 is now witnessed.'
    files_touched:
    - .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-04-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-04-validate-validator/qa/manifest-integration.json
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: MF-1 to MF-4 closed at 0ce1c841. Offline probes found no new fail-open
      path, and all 45 graded functions passed.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: MF-2 is closed. Open-row relief still trusts two ratings authored by
      the same lead.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B scoped out: 68 changed paths, none UI.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: All three perspectives pass, and DEC-206 and DEC-123 are met. DEC-123,
      DEC-260 D-06 and validate-digest.py state one relief rule.
    files_touched: []
  must_fix: []
  files_touched:
  - .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-04-validate-validator/state.yaml
  - .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-04-validate-validator/digest.md
  - .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-04-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2622-practicality-rule/runs/2026-11-28-04-validate-validator/qa/manifest-integration.json
  branch: none
  open_questions:
  - id: VAL-OQ-05
    question: 'SEC-03, raised by security-reviewer and rated high: open-row relief
      reads two ratings, the panel row and the current team-digest finding. The product
      lead authors both, and neither is checked against the reader''s original return,
      so a dishonest lead could mask a reader FAIL. Security rates it {plausible,
      regression, adversary} high and asks: require independently attributable reader
      rating evidence, or accept the risk? Validator-lead rates it med and not gating,
      for four reasons. (1) It is the same actor and boundary the operator already
      accepted in VAL-OQ-03 (the lead''s roll-up inputs are trusted). (2) At base,
      the resolved-row path also relieves on a plan-team-recorded disposition, so
      it is no_worse for a dishonest lead [INFERENCE: record-panel''s resolution evidence
      requirement unverified]. (3) Signed D-03 makes the lead the authority that lowers,
      and its reason line names the reader''s original severity, so falsification
      is left on record. (4) The remedy needs a reader-return provenance contract
      plus amending signed D-03/D-06, so no fix round can apply it. Recommendation:
      accept the residual, as for VAL-OQ-03. If it is wanted, open a separate provenance
      feature. Rule: accept, or open a follow-up?'
    blocking: true
  escalations:
  - id: VAL-ESC-01
    raised_by: harness-security-reviewer
    question: 'SEC-03: should DEC-123 open-row relief require rating evidence that
      can be independently attributed to the reader, or does the operator accept the
      same-source (product-lead) rating risk?'
    domain: security / signed decision D-03, D-06, DEC-123
    routed_to: operator via main session
    resolution: pending; validator-lead recommends accepting the residual, as for
      VAL-OQ-03 (rated med, not gating)
    decided_by: pending
    recorded_as: VAL-OQ-05; runs/2026-11-28-04-validate-validator/digest.md
  expertise_update: []
  adequacy_notes:
  - Receipts are from this host's interpreter, not CI. tsc is absent; the diff touches
    no TypeScript.
  - MF-1 and MF-2 are closed by execution, not reading. QA got red at edcda5be and
    green at the pin, plus one red mutant per relief leg (5/5, each exactly one case).
    Code-reviewer re-ran the omitted-current-high scenario. Security executed _carveout_inputs
    over open and resolved rows.
  - Lead and reader ratings of SEC-03 differ. Security transcribes high (plausible/regression/adversary);
    the validator lead rates it med, not gating. Both are carried in VAL-OQ-05 per
    P-04. severity_max reports the reader's high unchanged.
  - 'QA-F4 advisory (low): an any()-for-all() mutant over current findings sharing
    one PF id stays green. The pin is correct, because code-reviewer''s offline probe
    of that case was denied. Exposure is contrived/no_worse/harness, so there is no
    test demand.'
  - The c2 advisories (SC-11 letter gap, QA-F2, M4-M7, QA-F3) were ruled earlier and
    were not re-raised.
  - The claim that post-pin commits touch only feature.json and plan.yaml was handed
    to code-reviewer, whose note holds the command. The validator lead did not measure
    it.
  - Exposure is carried in each finding's why because the live yield schema is still
    the pre-feature schema (ruled c1).
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: test-practicality-rule.py:115; base FAIL in review-harness-qa-c2.md
  - id: SC-02
    verdict: met
    method: automated
    evidence: test-practicality-rule.py:140; base FAIL in review-harness-qa-c2.md
  - id: SC-03
    verdict: met
    method: automated
    evidence: test-practicality-rule.py:167; base FAIL in review-harness-qa-c2.md
  - id: SC-04
    verdict: met
    method: automated
    evidence: test-practicality-rule.py:174; base FAIL in review-harness-qa-c2.md
  - id: SC-05
    verdict: met
    method: automated
    evidence: test-practicality-record-panel.py; base FAIL in review-harness-qa-c2.md
  - id: SC-06
    verdict: met
    method: inspection
    evidence: _open_row_reason uses the shared panel_findings predicates is_discounted/is_non_gating
      (pm, security)
  - id: SC-07
    verdict: met
    method: inspection
    evidence: 'Under VAL-OQ-01 ruling: diff 3e979ae3..0ce1c841 shows no foreign feature
      or runs path; run_state.py unchanged (pm)'
  - id: SC-08
    verdict: met
    method: inspection
    evidence: surface unchanged edcda5be..0ce1c841 (pm)
  - id: SC-09
    verdict: met
    method: inspection
    evidence: product-lead L444-452 and teams/plan.yaml L227-232 name reader severity
      and exposure (pm)
  - id: SC-10
    verdict: met
    method: inspection
    evidence: surface unchanged edcda5be..0ce1c841 (pm)
  - id: SC-11
    verdict: met
    method: inspection
    evidence: surface unchanged edcda5be..0ce1c841 (pm); c2 letter gap advisory
  - id: SC-12
    verdict: met
    method: inspection
    evidence: DEC-260 carries every element; index INDEX-EQUAL (pm)
  - id: SC-13
    verdict: met
    method: automated
    evidence: 'test-digest-dev-skill.py 12/12; agent output: ok; red at 0daddfc4 (review-harness-qa-c1.md)'
  - id: SC-14
    verdict: met
    method: automated
    evidence: integration 94/94 at the pin; base case_f59 red (notes/fail-first-T-02.md)
  - id: SC-15
    verdict: met
    method: automated
    evidence: 'test-practicality-rule.py 36/36 at the pin; carveout-no-current-finding-denied
      and team-mustfix-denied are red at edcda5be (review-harness-qa-c3.md). SEC-03
      concerns input provenance, outside the SC''s cases: VAL-OQ-05'
  - id: DEC-206
    verdict: met
    method: inspection
    evidence: DECISIONS.md L6804-6807, old clause 0 hits (pm)
  - id: DEC-123
    verdict: met
    method: inspection
    evidence: DECISIONS.md L2497-2506 matches _open_row_reason and _carveout_inputs;
      D-06 L8877-8884 agrees (pm, code-reviewer)
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - 'QA-F4: no witness for all() over several current findings sharing one PF id.
    The any() mutant stays green. The pin is correct; advisory.'
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-security-reviewer
    summary: 'SEC-03 (T-01/T-02): the product lead authors both ratings that open-row
      relief reads (the panel row via its fan-in, and the current team-digest finding),
      so a dishonest lead can mask a genuine reader FAIL without resolving it.'
    why: 'exposure {trigger: plausible, vs_today: regression, control: adversary}
      per security. Security executed the in-memory roll-up: an identical discounted-med
      open row relieves at the pin but not at base. The provenance trace is static.
      Validator-lead rates it med, not gating: the trust class is the one ruled in
      VAL-OQ-03, and lowering by the lead is signed D-03. The remedy needs a provenance
      contract plus amending signed D-03/D-06 (G-06), so it is escalated as VAL-OQ-05
      and not put in must_fix.'
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa
    summary: 'QA-F4 (T-01): a mutant replacing all() with any() over current findings
      that share a PF id survives both test files.'
    why: 'exposure {trigger: contrived, vs_today: no_worse, control: harness}. The
      pin is correct: code-reviewer''s offline probe denied relief for discounted
      med plus plausible high under one id. Advisory, so there is no test demand under
      VAL-OQ-04.'
  readers: []
```
