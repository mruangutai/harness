# FEAT-2489 plan panel c2 — validator-lead digest

**ESCALATE: do not sign as written.** Two of the three cycle-1 substance findings are closed for their class. PF-5dbe is closed only for its instance and leaves a med residual. Broadening SC-02 exposed one new high: as worded, SC-02 cannot be satisfied on some complete trees. Its remedy amends the closed sanctioned-delta list in the operator's Q3 ruling, so the operator has to rule on it. The scope reader's loop is at `max_cycles: 1` (`then: escalate`).

Reader note: `notes/review-harness-code-reviewer-plan-c2.md`. Fan-in: `runs/r-20261124-2-plan-validator/panel-c2.md`. Only `scope` ran. should-not-exist and design were skipped by design, and that is not a clean read by either of them.

## Per-finding verdicts (cycle-1 substance)

| PF id | Verdict | Basis (reader, plan text) |
|---|---|---|
| PF-b25f62af28d7aa5f31cd38d635041a54 (high) | **closed, class** | BRIEF SC-02 now covers every audited tree state and argv: both streams, source errors, finding order, and a closed list of deltas. The receipt samples are explicitly evidence, not scope. |
| PF-0e9128df11c14ad97669b28ff451a725 (high) | **closed, class** | T-02 compares matched archives from one base, overlaying only bin and tests. It checks exits and both streams in full, must be red at the stale checkpoint and green after T-04, and the final receipt is bound to the graded tree IDs. |
| PF-5dbe6b5eecda5efa44c6d9624e826e1a (med) | **not closed, instance only** | T-01's verify is now stage-aware, so the shared-file gate break is fixed. Its historical green receipt is bound by prefix only. |

## Ranked findings

1. **high, substance (new): SC-02 contradicts the verbatim move.** I checked the source myself. `_exemption_finding` (and `_unmigrated_row_findings`, `_canonical_row_findings`) build their diagnostic from the row's `file`/`id`. Delta item 1 requires those fields to be rewritten to `canonical_reader_audit.py`. So the same perturbation, for example blanking the `reason` on the exempt `_classification_document::json_file#1` row, prints a different finding text before and after the split. SC-02's closed list sanctions the rewrite in the inventory, not its echo in diagnostics. The grilling's Q3 says "exactly these", so the defect is inherited from the ruling and is not pm's drafting error. **The class to close:** every diagnostic that echoes a relocated row's `file`, `id` or label. Recommended remedy: add one sanctioned consequence of delta 1, namely that finding text echoing a rewritten row field shows the rewritten value and is otherwise identical. Ideally T-02 should also sample one such perturbed finding (today it samples none, plan.yaml T-02). Severity: I keep the reader's `high`. Left as written, SC-02 forces either a false PASS at review or an unsatisfiable gate.
2. **med, substance (residual of PF-5dbe): T-01's green receipt is not bound to its checkpoint.** I checked this myself. T-01's verify asserts only `rec[0].startswith('HEAD ')` and `rec[1].startswith('BLOB ')`, yet it prints "green receipt bound to its checkpoint". That claim is not enforced. Remedy, which pm can make in T-01's text: verify that the recorded HEAD is an ancestor of the current HEAD, and that `git rev-parse <HEAD>:tests/integration/test-check-plan-routes.py` equals the recorded BLOB. Do not compare against the live file, because T-03 edits it.

Fix order: (1) first, since its wording decides what T-02 must sample. (2) is independent.

## Disclosed gap: complete-install scoping of SC-02

**Acceptable as a disclosed gap, not a finding.** The reader and I agree. Q3's "every tree state" is about what a runnable checker audits. A bin missing a module fails loudly at import (traceback, exit 1). That cannot produce a false audit pass, BRIEF "Verification gaps" discloses it, and case 19b's copy list covers the fixture. The new high above is a different matter: it occurs on a complete install, so this gap does not absorb it.

## Notes

- No edits were made to BRIEF.md or plan.yaml in this run. Overlap: read-only `plan-merge.py check` by the reader found a single advisory OVERLAP (T-01/T-03 on the test file) and no orphan or dangling traces.
- The reader also listed spec_violations (SC-02 mismatch, SC-03 omission). They are the same two findings above, not additional ones.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: 'Plan not signable: PF-b25f and PF-0e91 closed by class, PF-5dbe instance-only
    (med residual), and a new high shows SC-02''s closed delta list (inherited from
    Q3) forbids the diagnostic filename echo the required move produces; operator
    ruling needed'
  open_questions:
  - id: OQ-C2-1
    question: "SC-02 / grilling Q3 'sanctioned delta \u2014 exactly these': diagnostics\
      \ such as _exemption_finding, _unmigrated_row_findings and _canonical_row_findings\
      \ print a relocated row's file/id, which delta 1 rewrites, so a perturbed complete\
      \ tree prints different finding text after the move. Amend the closed list to\
      \ sanction 'finding text echoing a rewritten row field shows the rewritten value,\
      \ otherwise identical' (and have T-02 sample one such finding)? Validator-lead\
      \ and scope reader recommend yes. Without it SC-02 is unsatisfiable or gets\
      \ a false PASS at review."
    blocking: true
  files_touched:
  - .harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-2-plan-validator/state.yaml
  - .harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-2-plan-validator/panel-c2.md
  expertise_update: []
  team: plan
  steps_run: 1
  cycles_used: 1
  members:
  - step: scope
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Two prior findings close by class; T-01 checkpoint proof is still unbound,
      and the broadened SC-02 contradicts a verbatim move on a complete install.
    files_touched:
    - .harness/harness/features/FEAT-2489-plan-routes-split/notes/review-harness-code-reviewer-plan-c2.md
  must_fix:
  - 'SC-02 (BRIEF) and T-02: resolve how diagnostics that echo a relocated row''s
    file/id are compared. Close the class (every row-echoing diagnostic), not one
    instance. The wording amends the operator''s Q3 closed list, so it needs the operator''s
    ruling (OQ-C2-1) before pm applies it.'
  - 'T-01 verify (plan.yaml): bind green-t01-default-run.txt to its checkpoint. The
    recorded HEAD must be an ancestor of HEAD, and git rev-parse <recorded HEAD>:tests/integration/test-check-plan-routes.py
    must equal the recorded BLOB. Never compare against the live file, which T-03
    edits. pm-owned text edit (PF-5dbe residual, med).'
  branch: none
  escalations:
  - id: ESC-C2-1
    raised_by: harness-code-reviewer
    question: 'Scope reader FAIL at cycle 2 with step max_cycles 1 reached (then:
      escalate). Remedy 1 amends the operator''s Q3 sanctioned-delta list; remedy
      2 is a pm text edit.'
    domain: plan scope / operator behaviour contract
    routed_to: harness-orchestrator
    resolution: 'open: operator rules on OQ-C2-1 at signature review (DEC-176); pm
      applies both remedies; a further scope re-read is the orchestrator''s call'
    decided_by: pending
    recorded_as: runs/r-20261124-2-plan-validator/digest.md
  adequacy_notes:
  - Only scope ran. should-not-exist and design were skipped by design (proportionality/form
    and self-scope-out do not re-cycle), and that is not a clean read by either.
  - 'Lead checked both open findings at source: check-plan-routes.py::_exemption_finding
    interpolates row file; T-01 verify checks HEAD/BLOB prefixes only while printing
    ''bound to its checkpoint''.'
  - 'Disclosed gap (SC-02 scoped to a complete install): ruled an acceptable disclosed
    gap, not a finding. An import failure is loud and cannot pass an audit falsely.
    It does not absorb the new high, which occurs on a complete install.'
  - PF-b25f closed (class) and PF-0e91 closed (class) rest on the reader's reading
    of plan text. No code exists yet, so nothing was executed.
  - 'Scope reader result: FAIL, severity_max high; 2 closed (class), 1 not closed
    (med residual), 1 new high substance.'
  sc_status: []
  needs_approval: true
  severity_max: high
  matrix_ok: none
  coverage_gaps:
  - T-02's equivalence receipt samples no perturbed finding that names a relocated
    row (the exact case the new high describes).
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: SC-02 forbids a diagnostic filename change that the required verbatim
      move produces.
    why: Diagnostics interpolate the row's file/id, which delta 1 rewrites. A perturbed
      complete tree (e.g. a blank reason on the exempt _classification_document row)
      prints check-plan-routes.py before and canonical_reader_audit.py after. SC-02's
      closed list does not sanction this, so the criterion is unsatisfiable or will
      get a false PASS.
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: PF-5dbe6b5eecda5efa44c6d9624e826e1a closes the immediate overlap only;
      the historical T-01 green receipt is not bound to its checkpoint.
    why: T-01 verify checks only HEAD/BLOB prefixes, so a receipt naming an unrelated
      commit/blob still passes. Once T-03 makes the live run intentionally red, nothing
      proves T-01 was green before the move.
  - kind: substance
    scope: none
    severity: info
    reader: harness-code-reviewer
    summary: 'PF-b25f62af28d7aa5f31cd38d635041a54 closed for its class: SC-02 now
      states the invariant for every audited tree state and argv, with a closed delta
      list; receipt samples are evidence, not scope.'
    why: 'Cycle-1 disposition: the narrowing to six argv examples is gone (BRIEF SC-02).'
  - kind: substance
    scope: none
    severity: info
    reader: harness-code-reviewer
    summary: 'PF-0e9128df11c14ad97669b28ff451a725 closed for its class: T-02 compares
      matched archive trees from one base, both streams in full, red at the stale
      checkpoint and green after T-04.'
    why: 'Cycle-1 disposition: the inputs are now equal trees, comparison is full-stream
      rather than last-line, and the final receipt is bound to the graded tree IDs
      (plan.yaml T-02, T-04).'
  readers:
  - reader: scope
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: should-not-exist
    status: skipped
    persona: fable-advisor
    reason: 'not re-run at cycle 2: its cycle-1 findings were proportionality plus
      form, trimmed at apply; never re-cycles'
  - reader: design
    status: skipped
    persona: harness-ui-reviewer
    reason: 'not re-run at cycle 2: self-scoped out at cycle 1, and nothing in the
      apply added a UI surface'
artifact: .harness/harness/features/FEAT-2489-plan-routes-split/runs/r-20261124-2-plan-validator/digest.md
```
