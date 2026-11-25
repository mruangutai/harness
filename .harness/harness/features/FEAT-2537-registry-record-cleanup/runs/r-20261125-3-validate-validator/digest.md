# FEAT-2537 targeted re-validate — run r-20261125-3-validate-validator — ESCALATE

**Pin** 635b5c158c00047bab2998dd3349e524bc12d0b7 · **base** a24eacee718898c4512379de1fe87b9611a7df43 · prior pin 8ae96bea · scope per `notes/answers-2026-11-25-validate-c0.md` Constraints. Readers run: qa, code-reviewer, in one turn. Skipped by ruling: security, ui, goal-check. They stand as validated at 8ae96bea.

## Conclusion

Fix c1 is in scope and green, but the ruling's ship condition "SC-02 met" is not reached on the code-reviewer's reading. The ruling forbids a second round, so this goes back to the ruler and does not loop.

Delivered and measured by QA:
- `test-inflight-registry.py` passes 200/200 at the pin.
- With the base module swapped in, all 12 case-18 reds point in the ruled direction: v1 map ×3, `{}` ×2, version-less ×4, schema-1 writer ×3. The controls stay green.
- The default-to-v2 mutant now dies, with 4 reds.
- The T-01 verify block exits 0.
- The four immutables are byte-identical to base.
- Unit 68 and integration 95 pass, with DEC-255 receipts in `qa/`.
- Must-fix 2, the docstring, is closed. The module diff is docstring-only.

The two new inputs, full claim dicts and full `(claim, expired)` returns are all present, and no decoded-JSON comparison remains. Both readers confirm this.

## Ranked findings (deduplicated)

1. **F1: case 18 compares text, not bytes, and uses value sentinels.**
   - *Raised by:* code-reviewer (substance, high, must_fix) and qa F-1 (low, coverage gap plus a non-blocking question). I verified it at source in `tests/integration/test-inflight-registry.py:481-559`.
   - *Text mode:* `_file_bytes` opens files with `"r", encoding="utf-8"`, so universal-newline decoding lets a CRLF writer pass.
   - *Sentinels:* `_ABSENT = "<absent>"` and `_UNREADABLE = "UnreadableRegistry"` are strings, so they can collide with file content or a return value.
   - *Silent rows:* these check only that the phrase `treating as empty` is absent, not that stderr is empty.
   - *My reading: low to med, not high.* The ruling's own clause names `<absent>` as the absence representation. Each counterexample needs a contrived mutant that no plausible code path produces on this platform, such as a CRLF writer on darwin or a strict reader returning a magic string. The ruling's stated intent is met: no decoded JSON, the canonical serialization is pinned, and full returns are checked. SC-02's literal words "file bytes" and "raise or no raise" are not met.
   - *Severity:* the reader's high is transcribed unchanged, so `severity_max` is high and the gate is FAIL.
   - *Remedy fit:* the remedy is about 10 lines in a T-01 file, so it is legal under G-06. Read with `"rb"` and compare against `.encode()`d expectations. Use `object()` sentinels for absence and refusal, and assert `buf.getvalue() == ""` on silent rows. It would close every counterexample the reviewer named.
   - *Why ESCALATE:* the ruling allows exactly one fix round and says "not a second round", so no fix cycle may run it without the ruler.
2. **F2: the literal 8ae96bea..635b5c15 range is wider than the two ruled files.**
   - *Raised by:* code-reviewer (form, low).
   - *Assessed and dismissed as a stop-and-rule trigger.* QA measured that, outside the feature directory, only `inflight_registry.py` and `test-inflight-registry.py` change. The feature-directory paths are station records and records the ruling itself required: the ruling note `answers-2026-11-25-validate-c0.md` and the main session's `fix-c1-receipt.md`, from commits 2a0904e8 and 7d986b71 plus the receipt in 635b5c15.
   - *Why it cannot trigger stop-and-rule:* nothing in it is source or behaviour. I fold the point into Q1 so the ruler can confirm it.

**SC-02, recorded as two findings (G-10):** literal status **partial**, because "file bytes" and "raise or no raise" are not literally asserted. Lead reading: **intent met**. Only the ruler may adopt that reading.

## Options for the ruler (Q1)

- **(a) Accept the intent-met reading.** SC-02 becomes met, and the feature ships at 635b5c15 with F1 in the backlog.
- **(b) Grant one test-only micro-round.** It applies the F1 remedy above, followed by a QA-only re-check: whole file green, base swap red, and a CRLF mutant red.

## Members

- qa PASS: `notes/qa-r-20261125-3-validate-validator.md`, with receipts in `runs/r-20261125-3-validate-validator/qa/`
- code-reviewer ESCALATE: `notes/review-harness-code-reviewer-c2.md`
- security, ui and pm goal-check were skipped by the ruling and stand at 8ae96bea.

## Adequacy

- Evidence is host-only (Python on darwin arm64), not CI.
- The base-swap and mutant reds are QA's own runs, and they match the main session's receipt line for line.
- SC-01, SC-03, SC-04 and the DEC rows are carried from r-20261125-2 without being re-measured, by ruling. The c1 code diff does not touch their surfaces (QA diff-stat).

```yaml
VERDICT: ESCALATE
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-3-validate-validator/digest.md
DIGEST:
  headline: 'Fix c1 at 635b5c15 is in scope and green: 200/200, 12 base-swap reds,
    the default-to-v2 mutant dies, verify exit 0, immutables identical, must_fix 2
    closed. But SC-02 is still literally partial: case 18 reads files in text mode
    and uses string sentinels (code-reviewer high, qa low). The ruling allows no second
    round, so the ruler must accept the intent-met reading or grant a test-only micro-round.'
  open_questions:
  - id: Q1
    question: 'Ruler (fable-advisor, under operator delegation): case 18 at 635b5c15
      meets the c0 ruling''s intent, and it carries full returns and both new inputs.
      It still falls short of SC-02''s literal ''file bytes'' and ''raise or no raise'',
      in three ways. (1) _file_bytes reads in text mode with utf-8 and universal newlines,
      so a CRLF writer passes. (2) The absent and refusal markers are the strings
      ''<absent>'' and ''UnreadableRegistry'', which can collide with file content
      or a return value. (3) Silent rows check only that ''treating as empty'' is
      absent, not that stderr is empty. code-reviewer rates this high (must_fix);
      qa rates it low. Lead reading is low to med, since every counterexample needs
      a contrived mutant that cannot occur on this platform. Choose one: (a) accept
      intent-met, so SC-02 is met and the feature ships at 635b5c15 with this item
      in the backlog; or (b) grant one test-only micro-round. That round would read
      with ''rb'' against encoded expectations, use object() sentinels, and assert
      empty stderr on silent rows, then a QA-only re-check: green, base-swap red,
      CRLF mutant red. Please also confirm that the feature-record paths in the 8ae96bea..635b5c15
      range fall outside the ruling''s two-file scope. Those are the ruling note,
      the station records and the fix receipt; qa measured that only the two ruled
      files change outside the feature dir.'
    blocking: true
  files_touched:
  - .harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-3-validate-validator/state.yaml
  - .harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-3-validate-validator/digest.md
  - .harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-3-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-3-validate-validator/qa/manifest-integration.json
  - .harness/harness/features/FEAT-2537-registry-record-cleanup/observations/harness-qa.md
  expertise_update: []
  team: validate
  steps_run: 2
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: 'Whole file 200/200. Base swap shows 12 case-18 reds in the ruled direction.
      The default-to-v2 mutant dies with 4 reds. Verify exits 0, the immutables are
      identical, the code diff is confined to the two ruled files, and the unit and
      integration receipts are clean. Low note: text-mode file read.'
    files_touched:
    - .harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-3-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-3-validate-validator/qa/manifest-integration.json
    - .harness/harness/features/FEAT-2537-registry-record-cleanup/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: ESCALATE
    headline: 'must_fix 2 (docstring) is closed. must_fix 1 stays open: case 18 does
      not literally assert bytes, typed refusal or silence, so SC-02 stays partial.
      The literal prior-pin range also includes feature records.'
    files_touched: []
  must_fix:
  - 'T-01 / SC-02 (substance; code-reviewer high, qa low). This is a legal remedy,
    but it is blocked on Q1 because the ruling allows no second round. In case 18
    of tests/integration/test-inflight-registry.py: read registry files in binary
    mode and compare them with encoded expectations; replace the ''<absent>'' and
    ''UnreadableRegistry'' string sentinels with distinct object() sentinels; and
    assert empty stderr on silent rows.'
  branch: feat/FEAT-2537-registry-record-cleanup
  escalations:
  - id: E1
    raised_by: harness-code-reviewer, harness-qa
    question: The ruling's ship condition requires SC-02 to be met, but case 18 still
      does not literally assert file bytes or raise/no-raise. The ruling also forbids
      a second fix round. Should the ruler accept the intent-met reading, or grant
      a test-only micro-round?
    domain: c0 ruling ship condition / SC-02 / rework budget
    routed_to: harness-orchestrator -> fable-advisor (operator delegation)
    resolution: pending
    decided_by: pending
    recorded_as: open_questions Q1
  adequacy_notes:
  - Receipts are from the host interpreter only (darwin arm64); CI has not run.
  - QA's own base-swap (12 reds) and mutant (4 reds) runs match notes/fix-c1-receipt.md
    line for line. The CLI-subprocess reds are a swap-harness artifact that QA avoided
    with a full bin/ copy.
  - 'Lead reading of F1 is low to med, below code-reviewer''s high: each counterexample
    needs a contrived mutant, and the ruling''s own clause names ''<absent>'' as the
    absence marker. The reader''s severity is transcribed unchanged.'
  - 'Dismissed as a stop-and-rule trigger: the literal 8ae96bea..635b5c15 range includes
    feature-dir records (the ruling note, station records and fix-c1-receipt.md).
    QA measured that, outside the feature dir, only inflight_registry.py (a docstring-only
    change) and test-inflight-registry.py change. No source or behaviour delta is
    outside the ruled scope.'
  - SC-01, SC-03, SC-04, DEC-199/204/218, security, ui and goal-check are carried
    from r-20261125-2 at 8ae96bea without re-measurement, per the ruling. The c1 code
    diff does not touch their surfaces.
  - 'Readers run: qa (targeted re-validation) and code (must_fix closure only), per
    the c0 ruling. Skipped: security, ui and goalcheck, which stand as validated at
    8ae96bea.'
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: Carried from r-20261125-2 at 8ae96bea and not rerun, per the ruling.
      The verify block's live_children grep still exits 1 at 635b5c15 (qa).
  - id: SC-02
    verdict: partial
    method: automated
    evidence: 'Full returns, both new envelopes and the base-swap reds (12) are present.
      ''File bytes'' and ''raise or no raise'' are not literally asserted: a text-mode
      read and string sentinels (test-inflight-registry.py:481-559). The lead''s reading
      is intent met; the ruler decides (Q1).'
  - id: SC-03
    verdict: met
    method: inspection
    evidence: Carried from r-20261125-2 at 8ae96bea and not rerun, per the ruling.
      The verify block's DECISIONS stale-clause check and the index diff exit 0 at
      635b5c15 (qa).
  - id: SC-04
    verdict: met
    method: inspection
    evidence: Carried from r-20261125-2 at 8ae96bea and not rerun, per the ruling.
      harness-hooks.ts is not in the c1 diff.
  - id: DEC-199
    verdict: met
    method: inspection
    evidence: Carried from r-20261125-2 at 8ae96bea; DECISIONS.md is not in the c1
      diff.
  - id: DEC-204
    verdict: met
    method: inspection
    evidence: Carried from r-20261125-2 at 8ae96bea; DECISIONS.md is not in the c1
      diff.
  - id: DEC-218
    verdict: met
    method: inspection
    evidence: Carried from r-20261125-2 at 8ae96bea; DECISIONS.md is not in the c1
      diff.
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - Case 18 compares registry files in text mode (utf-8, universal newlines), so a
    CRLF-emitting writer passes 200/200 (qa F-1, code-reviewer).
  - Case 18's absence and refusal markers are strings, and its silent rows do not
    require empty stderr (code-reviewer).
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: 'T-01 / SC-02: case 18 does not prove exact bytes, absence, typed refusal
      or silence. _file_bytes reads text (a CRLF writer passes); ''<absent>'' and
      ''UnreadableRegistry'' are colliding string sentinels; silent rows check only
      for a missing phrase.'
    why: SC-02 requires 'raise or no raise, and the file bytes'. QA raised the same
      defect as F-1 at low, merged here. Lead reading is low to med because each counterexample
      needs a contrived mutant, but the reader's severity is transcribed. The remedy
      is legal but blocked by the ruling's one-round budget, so it goes to Q1.
  - kind: form
    scope: none
    severity: low
    reader: harness-code-reviewer
    summary: 'Stop-and-rule claim: the literal 8ae96bea..635b5c15 range is not confined
      to the two allowed files.'
    why: Assessed and dismissed as a trigger. QA measured that only the two ruled
      files change outside the feature dir; the extra paths are ruling-mandated records
      (the ruling note, station records, fix-c1-receipt.md). The ruler is asked to
      confirm in Q1.
  readers:
  - reader: qa
    status: ran
    persona: harness-qa
    reason: none
  - reader: code
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: security
    status: skipped
    persona: harness-security-reviewer
    reason: stands as validated at 8ae96bea per answers-2026-11-25-validate-c0.md;
      the c1 diff is test plus docstring only
  - reader: ui
    status: skipped
    persona: harness-ui-reviewer
    reason: stands as validated at 8ae96bea per answers-2026-11-25-validate-c0.md;
      no UI surface
  - reader: goalcheck
    status: skipped
    persona: harness-pm
    reason: stands as validated at 8ae96bea per answers-2026-11-25-validate-c0.md
```
