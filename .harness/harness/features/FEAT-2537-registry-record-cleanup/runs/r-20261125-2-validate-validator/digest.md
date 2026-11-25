# FEAT-2537 validate — run r-20261125-2-validate-validator — ESCALATE

**Pin** 8ae96bea9dd8eb0f412c654158cbb3050322cfff · **base** a24eacee718898c4512379de1fe87b9611a7df43 · cycle 1 · readers: qa, code, security, ui, pm (all dispatched in one turn).

## Conclusion

The gates are green, but the signed stop-and-rule constraint is triggered. QA measured unit 68/68 and integration 95/95 with DEC-255 receipts. Typecheck is green, and the T-01 verify block exits 0 verbatim. Every claim the main session reported reproduced on the host interpreter. SC-01 and SC-02 each have natural fail-first reds. SC-03, SC-04 and the DEC-199/204/218 amends are met, and the four immutables are byte-identical.

Three readers independently found a writer-side delta outside the signoff's three in-class items:

- For non-v1, non-v2 shapes that carry recoverable claim rows, the base writer kept those rows and the pin drops them.
- Those shapes are malformed v2 with a list under another key, explicit `schema_version: 1` with a `claims` list, and an unversioned `claims` list.
- The signoff ruled malformed v2 "warning-only, on-disk bytes identical". That premise is false for this sub-case.

The code matches the signed D-01 text literally ("any other non-v2 object … folded to empty with a warning"). The remedy is therefore a ruling, not a code fix. Under the signoff, "any other behaviour delta stops for a ruling", so this needs the signer.

## Ranked findings (deduplicated)

1. **F1 — writer fold drops recoverable rows (substance; code-reviewer high, security med, pm low as F-1, qa low as Q-2 part).**
   - *Trigger:* `{"schema_version":2,"claims":"x","harness-qa":[row]}`. On base, `live_claim` keeps the row in v2. At the pin it warns and writes an empty v2.
   - *Other affected shapes:* `{schema_version:1, claims:[live]}` and unversioned `{"claims":[live]}`.
   - *Counts:* on the same input, `reconcile` and `release_all` drop from 1 to 0.
   - *Reachability:* no writer produces any of these shapes, and every strict reader refuses them at the pin.
   - *Remedy:* a signer ruling. **Accept:** no code change, and case 18 may optionally add a witness. **Reject:** amend D-01, which is signed. Either way it is not must_fix (G-06).
   - *Severity:* transcribed unchanged. My own reading is med: the change is fail-closed on every strict path, and the lost evidence is in a shape no writer produces.
2. **F2 — dispatch fallback widened (substance; security med).**
   - *Mechanism:* when `find_run_claim` finds any unreadable sibling registry it returns `{ok: False, cause: unreadable}`. On that result `dispatch-guard.py` `_dispatcher_feature` (lines 748–759) falls back to the task-declared feature. That can skip the registered distill feature/mission refusal.
   - *Base vs pin:* on base, a corrupt sibling already reached this same fallback, so the fail-open is pre-existing. The patch adds `{}` and unversioned objects to its trigger set. That follows from the ruled `{}` refusal, but the ruling did not name it.
   - *Remedy:* lives in `dispatch-guard.py`, which is not in T-01's files and sits in the main-session-direct bin tree. I verified the site at source. This goes to the operator.
3. **F3 — case 18 does not assert SC-02's "file bytes" or the full return (substance; code-reviewer high; qa F-2 form low).**
   - *What the test does:* `_file_after` compares decoded JSON, and the claim checks project returned claims to their IDs.
   - *Today's behaviour:* QA's probe found base and pin bytes identical, so no behaviour defect exists now.
   - *Why it is still must_fix:* SC-02's signed clause, each state checked by return value, raise or no raise, and file bytes, is not literally exercised. The fix is test-only and inside T-01's files.
4. **F4 — surviving mutant (substance; qa low, F-1).** A mutant that defaults a missing `schema_version` to 2 survives with 183/183 green. Under it, a strict read of `{"claims": []}` returns `[]`, which contradicts D-01. This is advisory. Recommend adding a version-less input to case 18 in the same edit as F3.
5. **F5 — docstring overstates warnings (form; code-reviewer low).** `inflight_registry.py:4-6` says every non-v2 input warns, but a blank file returns empty silently. Fix it in the fix run.
6. **F6 — `case_18_v1_registry_fails_closed` grades 2 on ABC 39.5 (substance; code-reviewer med).** This is a non-blocking grade exception, accepted with the reviewer's reason that the paired directions stay in one witness.

**Fix order:** the ruling on F1 comes first, because it decides which shapes case 18 must witness. Then do F3 and F4 together in one test edit, with F5 in the same fix run.

## Assessed and dismissed

- **qa Q-2, the v1 persona map holding a live claim is dropped by the writer.** This is in-class: SC-02 and D-01 explicitly require the writer to return no claim for a persona-keyed map holding a claim and to leave an empty v2 file. What the dropped claim contained does not change its class.
- **pm SC-01/SC-02 "partial pending qa".** QA's evidence has now landed, so SC-01 is met. SC-02 stays partial on F3 alone.

## Adequacy

- **Host evidence only.** All runs used host Python 3.15.2 on darwin arm64, not CI. There is no PR, so the CI route has never run. The canonical gates were parsed with the CI regex.
- **Grades.** `_parse` grades 3, below the production bar of 4, though it improved from base's 2; the reviewer did not gate on it. `_known_shape` grades 5, and cases 25 and 29 grade 4.
- **Which check discriminates the deletion.** Rewritten cases 25 and 29 pass on the base module, so they do not tell the old code from the new. The grep and the case-25 mutant do.
- **`check-state.py` at the pin.** It exits 1 because INV-26 compares the live board with the station recorded at pin time. It exits 0 at tip 2a0904e8. This is a station-timing artifact, not a code defect.
- **SC-04 is true at source.** The omp `event-bus.ts` emit does not await its handler, and `safeHandler` logs the error. The agent_start guard returns only when the run is ready, so a held run is re-opened.

## Members

- qa PASS: `notes/qa-r-20261125-2-validate-validator.md`, with receipts in `runs/r-20261125-2-validate-validator/qa/`
- code-reviewer ESCALATE: `notes/review-harness-code-reviewer-c1.md`
- security-reviewer FAIL: `notes/review-harness-security-reviewer-c1.md`
- ui-reviewer PASS (out of scope; census showed no UI surface): `notes/review-harness-ui-reviewer-c1.md`
- pm PASS: `notes/research-FEAT-2537-registry-record-cleanup-goalcheck-validate-c1.md`

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: 'FEAT-2537 at 8ae96bea needs a signer ruling. Gates are green: unit 68/68,
    integration 95/95, verify exit 0, fail-first red for SC-01/02, SC-03/04 and the
    DEC amends met, immutables byte-identical. But three readers found a writer delta
    outside the ruled class: non-v1/non-v2 shapes with recoverable rows lose them
    on fold, and reconcile/release counts go 1->0. Case 18 also does not check SC-02''s
    file bytes.'
  open_questions:
  - id: Q1
    question: 'Signer (AdvisorF4Sign): the signoff called malformed-v2 ''warning-only,
      on-disk bytes identical''. That is false when the object carries recoverable
      rows. Examples: {schema_version:2, claims:''x'', <persona>:[row]}; {schema_version:1,
      claims:[live]}; unversioned {claims:[live]}. Base live_claim kept those rows;
      the pin warns and writes an empty v2, and reconcile/release_all drop from 1
      to 0 on the same input. No writer produces these shapes, and every strict reader
      refuses them at the pin, so the change is fail-closed. The code matches signed
      D-01 literally. Accept as in-class (no code change), or reject (amend D-01)?
      Raised by code-reviewer (high), security (med), pm F-1 (low) and qa Q-2 (low).'
    blocking: true
  - id: Q2
    question: 'Operator: dispatch-guard.py _dispatcher_feature (lines 748-759) falls
      back to the task-declared feature whenever find_run_claim reports any unreadable
      sibling registry. That can skip the registered distill feature/mission refusal.
      On base, a corrupt sibling already reached this path. The ruled {} refusal adds
      {} and unversioned objects to its triggers. The remedy edits dispatch-guard.py,
      which is outside T-01''s files and main-session-direct. Accept as backlog, or
      block this ship? Raised by security (med) as blocking.'
    blocking: true
  files_touched:
  - .harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-2-validate-validator/state.yaml
  - .harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-2-validate-validator/digest.md
  - .harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-2-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-2-validate-validator/qa/manifest-integration.json
  - .harness/harness/features/FEAT-2537-registry-record-cleanup/observations/harness-qa.md
  - .harness/harness/features/FEAT-2537-registry-record-cleanup/observations/harness-pm.md
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Unit 68/68 and integration 95/95 with DEC-255 receipts; typecheck green;
      verify exit 0; SC-01 and SC-02 fail-first red reproduced; one surviving mutant
      (version-less claims).
    files_touched:
    - .harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-2-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-2-validate-validator/qa/manifest-integration.json
    - .harness/harness/features/FEAT-2537-registry-record-cleanup/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: ESCALATE
    headline: Malformed-v2 recovery can discard previously retained rows and change
      counts, which needs a signer ruling; case 18 does not verify exact bytes or
      full returns.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: Strict reads refuse the non-v2 shapes, but the dispatch fallback widens
      and locked recovery can erase live claim rows.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Out of scope: the measured census shows no UI surface changed.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Both perspectives delivered; SC-03, SC-04 and DEC-199/204/218 met; one
      unruled low writer delta.
    files_touched:
    - .harness/harness/features/FEAT-2537-registry-record-cleanup/observations/harness-pm.md
  must_fix:
  - 'T-01 (substance, test-only, after the Q1 ruling): case_18_v1_registry_fails_closed
    must assert exact file bytes (or absence) and the complete live_claims/live_claim
    return for each SC-02 state. Today _file_after compares decoded JSON and the claim
    checks project to IDs. Raised by code-reviewer (high) and qa F-2 (low). In the
    same edit, add a version-less {"claims": [...]} input to kill qa''s surviving
    default-to-v2 mutant.'
  - 'T-01 (form): the inflight_registry.py:4-6 module docstring says every non-v2
    input warns, but a blank file returns empty silently. Correct it in the fix run
    (code-reviewer, low).'
  branch: feat/FEAT-2537-registry-record-cleanup
  escalations:
  - id: E1
    raised_by: harness-code-reviewer, harness-security-reviewer, harness-pm, harness-qa
    question: Is the writer-side loss of recoverable rows from non-v1/non-v2 shapes
      (and reconcile/release_all going 1->0) inside the signed class? The signoff
      called malformed-v2 bytes identical, which is false for this sub-case.
    domain: signed decision D-01 / signoff constraint 'any other behaviour delta stops
      for a ruling'
    routed_to: harness-orchestrator -> signer (AdvisorF4Sign under operator delegation)
    resolution: pending
    decided_by: pending
    recorded_as: open_questions Q1
  - id: E2
    raised_by: harness-security-reviewer
    question: When find_run_claim reports an unreadable sibling registry, the dispatch-guard
      _dispatcher_feature fallback is fail-open. The trigger set is now wider ({}
      and unversioned objects). The remedy is outside T-01's files.
    domain: dispatch-guard.py (main-session-direct bin tree)
    routed_to: harness-orchestrator -> operator
    resolution: pending
    decided_by: pending
    recorded_as: open_questions Q2
  adequacy_notes:
  - 'Receipts are host-interpreter only (Python 3.15.2, darwin arm64). With no PR,
    the CI route never ran. The canonical gates were parsed with the CI regex: canonical-reader
    audit 0/103, consolidation audit 0.'
  - 'Every main-session claim reproduced: test-inflight-registry 183/183, test-validate-digest
    ALL PASSED, lead-start-return 60/60, lead-start-preflight 61/61, omp-hooks 247/0,
    typecheck 0. Merge-base is a24eacee.'
  - Rewritten cases 25 and 29 pass on the base module, so they do not discriminate
    the live_children deletion. The grep and the case-25 stranded mutant (3/183 red)
    do.
  - 'Code grade: _parse scores 3, below the production bar of 4. That is up from 2
    on base, and the reviewer did not gate on it. _known_shape scores 5 and cases
    25/29 score 4. Case 18 scores 2 on ABC 39.5, accepted as a non-blocking grade
    exception with the reviewer''s reason.'
  - check-state.py exits 1 at the pin because INV-26 compares the live board with
    the station recorded at pin time. It exits 0 at tip 2a0904e8. This is a timing
    artifact, not a code defect.
  - 'Dismissed as in-class: qa Q-2, the v1 persona map holding a live claim being
    dropped by the writer. SC-02 and D-01 explicitly specify that fold for a persona-keyed
    map holding a claim.'
  - 'The SC-04 comments are true at source: omp 19.1.1 event-bus emit does not await
    its handler and safeHandler logs failures; the agent_start guard re-opens a held
    run.'
  - Lead severity reading on the Q1 delta is med (fail-closed on strict paths, not
    writer-producible). Reader severities are transcribed unchanged, so severity_max
    is high from code-reviewer.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: 'pm: structure checked at the pin. qa: the live_children grep exits
      0 on base (inflight_registry.py:543) and 1 at the pin; positive control matches;
      the case-25 stranded mutant is red 3/183; whole file 183/183.'
  - id: SC-02
    verdict: partial
    method: automated
    evidence: 'With the base module swapped in, exactly the 5 case-18 v1 assertions
      are red and the 20 controls green; the candidate is 183/183. The ''file bytes''
      and full-return clause is not literally asserted (decoded JSON, IDs): must_fix
      1.'
  - id: SC-03
    verdict: met
    method: inspection
    evidence: 'pm: the three old clauses are absent at the pin and successors sit
      at lines 6038, 6615 and 7263, with no amendment paragraph. The index matches
      gen --stdout. Ledger commit d1777a89 precedes code commit 8764b820. The four
      immutables have equal blobs on base and pin.'
  - id: SC-04
    verdict: met
    method: inspection
    evidence: 'pm and security: all 6 changed lines are // comments. agent_start returns
      only when ready, so a held run re-opens. omp event-bus emit does not await.
      The tool_result release awaits releaseClaims, and the yield-side settle is _settle_in.'
  - id: DEC-199
    verdict: met
    method: inspection
    evidence: DECISIONS.md:6038 at the pin names the exact-parent strict live_claims
      read, which writes nothing.
  - id: DEC-204
    verdict: met
    method: inspection
    evidence: 'DECISIONS.md:6615 at the pin: v2 only; strict readers refuse non-v2;
      writers fold with a warning. This matches _parse and _known_shape at the pin.'
  - id: DEC-218
    verdict: met
    method: inspection
    evidence: DECISIONS.md:7263 at the pin names the held-child read (exact-parent
      live_claims).
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - 'A default-to-v2 mutant survives (183/183) while a strict read of {"claims": []}
    returns []. Version-less, {schema_version:1}, v2-without-claims, non-list claims
    and scalar JSON inputs have no case-18 witness (qa F-1).'
  - Case 18 compares decoded JSON and claim IDs, not bytes or full returns (qa F-2,
    code-reviewer).
  - No test witnesses the writer's treatment of non-v1/non-v2 shapes carrying recoverable
    rows (F1).
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: 'T-01: the malformed-v2 writer fold discards a previously retained row
      and changes reconcile/release_all counts from 1 to 0, not only stderr.'
    why: This is a delta beyond the signoff's warning-only characterization, which
      triggers the stop-and-rule constraint. The same finding was raised by security
      (med), pm F-1 (low) and qa Q-2 (low). The remedy is a ruling (Q1), not must_fix.
  - kind: substance
    scope: none
    severity: med
    reader: harness-security-reviewer
    summary: 'T-01: an unreadable sibling registry ({} now included) makes dispatch-guard
      _dispatcher_feature fall back to the task-declared feature, which can skip the
      registered distill preflight.'
    why: The fail-open in dispatch-guard.py is pre-existing (corrupt siblings already
      reached it); the ruled {} refusal widens its trigger set. The remedy is outside
      T-01's files, so it goes to Q2.
  - kind: substance
    scope: none
    severity: med
    reader: harness-security-reviewer
    summary: 'T-01: locked recovery can erase a live claim row from a malformed envelope
      before single-flight admission.'
    why: Duplicate of the code-reviewer high finding, viewed from the admission side;
      merged into Q1.
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: 'T-01/SC-02: case 18 does not verify exact bytes or full API returns.'
    why: SC-02's signed clause requires file bytes and the return value per state.
      qa F-2 rated it form/low after measuring the bytes identical today. Test-only
      fix, must_fix 1.
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa
    summary: 'T-01: a default-to-v2 mutant survives; a strict read of version-less
      {"claims": []} returns [].'
    why: Test adequacy against D-01's 'every non-v2 object refused'. Fold into must_fix
      1.
  - kind: form
    scope: none
    severity: low
    reader: harness-qa
    summary: 'T-01: case 18 compares parsed JSON rather than bytes, and the v1 inputs
      do not assert the file is unchanged after the strict read.'
    why: Duplicate of the code-reviewer bytes finding; merged.
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'T-01: case_18_v1_registry_fails_closed grades 2 (ABC 39.5).'
    why: Non-blocking grade exception, accepted with the reviewer's reason.
  - kind: form
    scope: none
    severity: low
    reader: harness-code-reviewer
    summary: 'T-01: the module docstring overstates writer warnings (a blank file
      is silent).'
    why: inflight_registry.py:4-6 vs :60-62; must_fix 2.
  - kind: substance
    scope: none
    severity: low
    reader: harness-pm
    summary: 'T-01: {schema_version:1, claims:[live]} was kept by the base writer
      and is folded by the pin writer.'
    why: Part of the Q1 delta; merged.
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
    status: ran
    persona: harness-security-reviewer
    reason: none
  - reader: ui
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/runs/r-20261125-2-validate-validator/digest.md
```
