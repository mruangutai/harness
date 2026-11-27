# FEAT-2537 c1-completion QA re-check — run r-20261125-4-validate-validator — PASS

**Pin** c67ba818977af535508b3a861b5eeead5bd39410 · **base** a24eacee718898c4512379de1fe87b9611a7df43 · prior pin 635b5c15 · scope per `notes/answers-2026-11-25-validate-c1.md` Constraints. QA was the only reader run. Code review, security, UI and goal-check were skipped by the ruling.

## Conclusion

SC-02 is now **met (literal)**. Every re-check the ruling lists holds, so the feature ships at c67ba818 under the ruling's step 4, without going back to the advisor. The code-reviewer's must_fix 1 from r-20261125-3 is **closed** by the ruling together with these QA receipts.

QA's measurements, all from its review-pin checkout (`notes/qa-r-20261125-4-validate-validator.md`):
- `test-inflight-registry.py` passes 200/200 at the pin.
- **Base swap** (full bin/ copy): 12/200 red, all on the ruled case-18 lines, with 0 other reds. Every control stays green, and the one-factor candidate control is 200/200.
- **Default-to-v2 mutant:** 4 reds, so the mutant dies.
- **CRLF writer mutant:** 8 reds, one on each writing byte row. The same mutant gives 200/200 against the 635b5c15 test file. That shows the red comes from the c1-completion edit, which is the witness that case 18 now compares literal file bytes.
- **Inspection:** `rb` reads, distinct `object()` sentinels, encoded-byte expectations, and `err == ""` on silent rows. No decoded comparison remains.
- **Scope:** outside `.harness/`, the 635b5c15..c67ba818 diff touches only `tests/integration/test-inflight-registry.py` (+18/-15), and only its case-18 helpers and state table. `inflight_registry.py` has zero diff.
- **Immutables:** all four are byte-identical to a24eacee (`git diff --quiet` exits 0).
- **Regression floor:** unit 68/68 and integration 95/95 under the DEC-255 runner, with receipts in `qa/`. Typecheck exits 0.

main's receipt table in `notes/fix-c1-receipt.md` § c1 completion matches QA's independent runs row for row.

## Findings

1. **(low, advisory, qa)** The silent-row `err == ""` assertion is discriminated for the empty-file and live-v2 rows by a stderr-noise mutant at `_parse` entry. The missing-file writer path never reaches `_parse`, so that row's assertion is present but no mutant has made it fail. This is hygiene beyond SC-02's literal list (ruling Q1 point 4) and does not gate.

No other findings. The r-3 F2 point, that the record range included feature-dir records, was dismissed by the ruling.

## Adequacy

- Evidence comes from the host interpreter only (Python 3.15.2 on darwin arm64). CI has not run.
- SC-01, SC-03, SC-04, DEC-199/204/218, security, ui and goal-check are carried forward as met from r-2 and r-3, per the ruling. The commit touches none of their surfaces. QA re-measured SC-01's `live_children` grep, which exits 1 at c67ba818.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-4-validate-validator/digest.md
DIGEST:
  headline: FEAT-2537 c1 completion at c67ba818 meets SC-02 literally and is ready
    to ship under the ruling. The test file passes 200/200. The base swap gives 12
    case-18 reds and 0 others. The default-to-v2 mutant dies (4 reds). The CRLF writer
    mutant gives 8 reds, while the prior test file stays green under it. The diff
    touches only test-inflight-registry.py. The four immutables are identical to base.
    Unit (68/68) and integration (95/95) receipts are clean. The code-reviewer's must_fix
    1 is closed.
  open_questions: []
  files_touched:
  - .harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-4-validate-validator/state.yaml
  - .harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-4-validate-validator/digest.md
  - .harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-4-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-4-validate-validator/qa/manifest-integration.json
  - .harness/harness/features/FEAT-2537-registry-record-cleanup/observations/harness-qa.md
  expertise_update: []
  team: validate
  steps_run: 1
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: 'All ruling re-checks hold at c67ba818. Whole file 200/200. Base swap:
      12 ruled case-18 reds, 0 other. Default-to-v2 mutant: 4 reds. CRLF mutant: 8
      reds, but 200/200 against the 635b5c15 test file. Diff is confined to one file.
      Immutables are identical. Unit 68/68 and integration 95/95 with DEC-255 receipts.'
    files_touched:
    - .harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-4-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-4-validate-validator/qa/manifest-integration.json
    - .harness/harness/features/FEAT-2537-registry-record-cleanup/observations/harness-qa.md
  must_fix: []
  branch: feat/FEAT-2537-registry-record-cleanup
  escalations:
  - id: E1
    raised_by: harness-code-reviewer, harness-qa
    question: SC-02 was literally partial at 635b5c15 (text-mode read, string sentinels,
      silent rows). Accept the intent-met reading, or grant a test-only micro-round?
    domain: c0 ruling ship condition / SC-02 / rework budget
    routed_to: harness-orchestrator -> fable-advisor (operator delegation)
    resolution: Option (b) granted as the completion of round c1, not a second round.
      Severity re-rated to med. F2 is not a scope breach. QA-only re-check. All of
      it is satisfied at c67ba818 by QA's receipts.
    decided_by: fable-advisor (AdvisorF6Revalidate) under operator delegation
    recorded_as: notes/answers-2026-11-25-validate-c1.md
  adequacy_notes:
  - 'Readers run: qa only. Skipped per notes/answers-2026-11-25-validate-c1.md: code
    (no code-reviewer round; must_fix 1 closes on QA receipts), security, ui and goalcheck
    (they stand as validated at 8ae96bea).'
  - Receipts come from the host interpreter only (Python 3.15.2 on darwin arm64).
    CI has not run.
  - 'Code-reviewer must_fix 1 from r-20261125-3 is closed by the ruling plus QA''s
    receipts: rb reads, object() sentinels, encoded expectations, and err == ''''
    on silent rows. The CRLF mutant is red at c67ba818 and green at 635b5c15.'
  - 'Advisory (low, qa): the missing-file silent row''s err == '''' assertion is present,
    but no mutant has made it fail. The stderr-noise probe enters at _parse, which
    that writer path never calls. It is hygiene beyond SC-02''s literal list and does
    not gate.'
  - "main's notes/fix-c1-receipt.md \xA7 c1 completion table matches QA's independent\
    \ runs row for row."
  - SC-01, SC-03, SC-04 and DEC-199/204/218 are carried forward as met from r-2 and
    r-3, per the ruling. Commit c67ba818 touches none of their surfaces.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: 'Carried from r-20261125-2. QA re-measured at c67ba818: git grep live_children
      exits 1, and cases 25 and 29 pass.'
  - id: SC-02
    verdict: met
    method: automated
    evidence: Literal. At c67ba818, test-inflight-registry.py:481-562 reads with rb
      against encoded bytes, uses object() sentinels, and asserts empty stderr on
      silent rows. Base swap gives 12 ruled reds; the v2 mutant 4; the CRLF mutant
      8, but 200/200 on the 635b5c15 tests (qa-r-20261125-4 note, steps 2-5).
  - id: SC-03
    verdict: met
    method: inspection
    evidence: Carried from r-20261125-2 and r-3 per the ruling. DECISIONS.md is not
      in the c67ba818 diff.
  - id: SC-04
    verdict: met
    method: inspection
    evidence: Carried from r-20261125-2 and r-3 per the ruling. harness-hooks.ts is
      not in the 635b5c15..c67ba818 diff.
  - id: DEC-199
    verdict: met
    method: inspection
    evidence: Carried from r-20261125-2 and r-3 per the ruling.
  - id: DEC-204
    verdict: met
    method: inspection
    evidence: Carried from r-20261125-2 and r-3 per the ruling.
  - id: DEC-218
    verdict: met
    method: inspection
    evidence: Carried from r-20261125-2 and r-3 per the ruling.
  needs_approval: false
  severity_max: low
  matrix_ok: true
  coverage_gaps:
  - 'The missing-file silent row''s empty-stderr assertion has never been made to
    fail by a mutant: the writer path skips _parse, where the stderr-noise probe injects.
    Advisory only.'
  findings:
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa
    summary: No mutant has made the missing-file silent row's err == '' assertion
      fail. The empty-file and live-v2 silent rows did turn red under a stderr-noise
      mutant.
    why: Advisory hygiene beyond SC-02's literal list (ruling Q1 point 4). It does
      not gate.
  readers:
  - reader: qa
    status: ran
    persona: harness-qa
    reason: none
  - reader: code
    status: skipped
    persona: harness-code-reviewer
    reason: 'answers-2026-11-25-validate-c1.md: no code-reviewer round; must_fix 1
      closes on QA receipts'
  - reader: security
    status: skipped
    persona: harness-security-reviewer
    reason: 'answers-2026-11-25-validate-c1.md: stands as validated at 8ae96bea; test-only
      change'
  - reader: ui
    status: skipped
    persona: harness-ui-reviewer
    reason: 'answers-2026-11-25-validate-c1.md: stands as validated at 8ae96bea; no
      UI surface'
  - reader: goalcheck
    status: skipped
    persona: harness-pm
    reason: 'answers-2026-11-25-validate-c1.md: stands as validated at 8ae96bea'
```
