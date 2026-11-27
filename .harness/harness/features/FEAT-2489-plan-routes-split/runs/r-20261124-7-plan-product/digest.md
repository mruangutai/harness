# FEAT-2489 — plan apply c4 (r-20261124-7-plan-product)

**The four cycle-4 remedies are applied, and the plan is ready for signature with one residual question.** approval.status is still `pending`. pm reports `plan-merge.py check` gave 0 failures.

## What changed (pm, step `apply`, PASS)
- **SC-02 item 5** (BRIEF.md:32), PF-daf9: the item now covers every site a diagnostic names: path::symbol, path::symbol:line and each traceback frame `File "...", line N, in NAME`. The order of sites and frames, and every byte outside a locator, stay as they are. W1 and W2 are unchanged. The disclosed-departure note (BRIEF.md:61) is rewritten once, for a reader who has not seen the cycles. pm traced the null-rows traceback and found four moved frames where the reader listed three: it adds `_classification_task_files`.
- **T-02 intent**, PF-1300: the leftmost-lookalike rule is gone. The rewrite now touches only the locator field of seven recognized stdout formats (R1 to R7), each traced to its base format function. Line-numbered R7 locators in the moved files FAIL. Every other line is compared exactly, including the echoed plan-read input, stderr and traceback frames, so a moved frame FAILs. The verify is unchanged.
- **T-04 verify** (plan.yaml:535), PF-c01a: the MAP block in the receipt must now equal the live run's MAP lines, in order.
- **T-01 intent** (plan.yaml:278), PF-a4d2: the receipt prose now says neither canonical_reader_audit.py nor structure_audit.py exists.

## How the lead checked it
I wrote the send-back criteria (`sendback-criteria.md`) before dispatching pm. I checked all eight against the files with grep, and every one is met: the T-04 `==` at :535, both modules at :278, traceback frames at BRIEF:32 and :61, `approval: pending`, and the dispositions at :28–155.

## Panel dispositions (all 19)
- **Resolved:** PF-b25f62af28d7aa5f31cd38d635041a54, PF-0e9128df11c14ad97669b28ff451a725, PF-5dbe6b5eecda5efa44c6d9624e826e1a, PF-9bc751c71f94a87fdd29e84578ce6c1e, PF-293c2789a0a14408ae4b9f3ca8df9efb, PF-2f032ea4ded9ab191d46672327dac011, PF-0dad747f115c481968d48fdfed6ec1e1, PF-6efa88c834c89ca43eea0322509703d9, PF-b963b10c2511cecf9ad0f6103be427ea, PF-29a7e86075e97f550fb37781a3eb389f, PF-4405ff64a842f05eadbdbad42e358e73.
- **Resolved in this run:** PF-1dd0f7a1329fa5038cc5e6aa8e0c3ecb (confirmed closed at c4), PF-a4d2a5fd9eb5b8976b8ae883e1c4e624 (form; fixed under the form rule).
- **Open, remedy applied but not re-read:** PF-241126189d3c3d16550a5f09c7532ff3 (high), PF-6159b2359da400c4da7dca8dcaa1415e (high), PF-daf9c8a84d9cf8f0da611c26b91877eb (high), PF-b14b5b45525eb18f63e04849c88d3838 (med), PF-13006fd231e087314c1651e5679503d0 (med), PF-c01acc578f91cbed233d9afea356eea7 (med). A signer who overrules must name these six.

## Residual for the signer
Do you accept SC-02 item 5 as a disclosed departure from grilling Q3's "exactly these, nothing else"? Under it, every place output names check-plan-routes.py source names where that code sits after the split, crash-traceback frames included. The checker FAILs on line numbers and moved frames instead of modelling them, so those parts rest on inspecting SC-01's diff. If you refuse, the plan returns to Plan with SC-02 unsatisfiable by the required move.

## Known limit (advisory)
Recognizing a format from output alone means a named-plan value crafted to reproduce a whole R3 line would still match R3. No sampled state does this, and the reader's actual example is handled.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-7-plan-product/digest.md
DIGEST:
  headline: 'All four cycle-4 remedies are applied to BRIEF.md and plan.yaml. pm reports
    plan-merge check at 0 failures and approval is still pending. The plan is ready
    for signature with one residual question: does the signer accept SC-02 item 5
    as a departure from Q3? Six substance findings are open with their remedies applied
    but not re-read.'
  open_questions:
  - id: Q-c4-signer
    question: 'Signer: do you accept SC-02''s fifth item as a disclosed departure
      from grilling Q3''s ''exactly these, nothing else''? Under it, every place any
      output names check-plan-routes.py source (file::symbol, file::symbol:line, or
      a Python traceback frame File "...", line N, in NAME) names where that code
      sits after the split. Order and all other bytes stay the same, except W1 (producer-order)
      and W2 (retained-site line shift). The checker FAILs on line numbers and moved
      frames instead of modelling them, so those parts rest on inspecting SC-01''s
      diff. If you refuse, the plan returns to Plan with SC-02 unsatisfiable by the
      required move. If you sign over the open findings, the overrule must name: PF-241126189d3c3d16550a5f09c7532ff3,
      PF-6159b2359da400c4da7dca8dcaa1415e, PF-daf9c8a84d9cf8f0da611c26b91877eb, PF-b14b5b45525eb18f63e04849c88d3838,
      PF-13006fd231e087314c1651e5679503d0, PF-c01acc578f91cbed233d9afea356eea7.'
    blocking: true
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/BRIEF.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/plan.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-7-plan-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-7-plan-product/sendback-criteria.md
  expertise_update: []
  team: plan
  steps_run: 1
  cycles_used: 0
  members:
  - step: apply
    persona: harness-pm
    verdict: PASS
    headline: 'Applied all four remedies. SC-02 item 5 now covers every site, traceback
      frames included, with W1 and W2 kept. T-02 rewrites only the locator field of
      seven recognized formats; all other text is compared exactly and unmodelled
      differences FAIL. T-04 requires MAP equality. T-01 prose names both modules.
      plan-merge check: 0 failures.'
    files_touched:
    - .harness/harness/features/FEAT-2489-plan-routes-split/BRIEF.md
    - .harness/harness/features/FEAT-2489-plan-routes-split/plan.yaml
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - 'The lead wrote send-back criteria before dispatch (runs/r-20261124-7-plan-product/sendback-criteria.md)
    and checked all eight against the files with grep. Each is met: T-04 `[l for l
    in final if l.startswith(''MAP '')] == maps` at plan.yaml:535; both modules named
    at plan.yaml:278; traceback frames in BRIEF.md:32 and :61; approval.status pending;
    dispositions at plan.yaml:28-155.'
  - The plan-merge check count (0 failures) is pm's own report. The lead holds no
    shell and did not re-run it. pm also reports that the existing OVERLAP line for
    tests/integration/test-check-plan-routes.py (T-01, T-03) is unchanged.
  - 'pm traced the null-rows traceback and found four moved frames where the reader
    listed three: it adds _classification_task_files between audit_canonical_readers
    and _named_plans. The worked example in SC-02 uses pm''s count.'
  - 'Known limit: T-02 recognizes formats from output alone, so a named-plan value
    crafted to reproduce a whole R3 line would still match R3. No sampled state does
    this, and the reader''s actual lookalike example is compared exactly.'
  - This run hosted no readers. The remedies for the six open findings have not been
    re-read, and they go to the signer unread, as the dispatch states.
  sc_status: []
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps:
  - SC-02 item 5's line-number and traceback-frame parts are not measured by any sampled
    state. Inspection of SC-01's diff carries them, as disclosed in BRIEF Verification
    gaps.
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: 'PF-daf9c8a84d9cf8f0da611c26b91877eb: SC-02 W3 first-site limit too narrow.
      Remedy applied (every site, traceback frames included); still open pending a
      re-read.'
    why: Cycle-4 scope record; no re-read follows this apply.
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'PF-13006fd231e087314c1651e5679503d0: T-02 lexical matcher rewrote lookalike
      data. Remedy applied (recognized-format locator field only); still open.'
    why: Cycle-4 scope record; no re-read follows this apply.
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'PF-c01acc578f91cbed233d9afea356eea7: T-04 receipt admitted extra MAP
      lines. Remedy applied (ordered equality); still open.'
    why: Cycle-4 scope record; no re-read follows this apply.
  - kind: form
    scope: none
    severity: low
    reader: harness-code-reviewer
    summary: 'PF-a4d2a5fd9eb5b8976b8ae883e1c4e624: T-01 receipt prose named one module.
      Fixed and resolved under the form rule.'
    why: Cycle-4 scope record.
  readers:
  - reader: scope
    status: skipped
    persona: harness-code-reviewer
    reason: 'apply-only run: no reader re-read follows (dispatch). The cycle-4 scope
      reading in r-20261124-6-plan-validator is the last one.'
  - reader: should-not-exist
    status: skipped
    persona: fable-advisor
    reason: 'apply-only run: not dispatched (its cycle-1 findings were trimmed at
      apply; not re-run since).'
  - reader: design
    status: skipped
    persona: harness-ui-reviewer
    reason: 'apply-only run: no UI surface; self-scoped out at cycle 1.'
  - reader: goalcheck
    status: skipped
    persona: harness-pm
    reason: dispatch excluded goal-check for this apply.
```
