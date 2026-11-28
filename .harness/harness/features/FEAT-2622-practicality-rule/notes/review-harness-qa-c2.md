# QA gate: FEAT-2622 validate c2 (run 2026-11-28-03-validate-validator)

**BLUF: PASS, `matrix_ok: true`.** The floor is unit + integration: T-01 is `cross_module`, T-02 is `logic` (unit only) and T-03..T-05 are `docs` (no kind). Both kinds ran once at `edcda5be091e5b1aa6dcc7021e410aae56de0222` and both were green: unit 74/74 files, integration 94/94 files. Both receipts return `evidence_defects == []`. Every `verify: automated` SC has a named test and a pre-fix red that I reproduced myself. **MF-1 and MF-2 are closed.** Each mutant turns its witness red, and the MF-1 mutant is live in the fixture.

There is one new advisory gap, and it is fail-open: **M10**. It drops the *discount* half of MF-1's digest-side conjunct and keeps only the severity check. Under M10 both suites stay green, yet 4 probes the pin denies become relieved. The c1 PF-id case-sensitivity gap is still open.

## Probes 1–5 (each measured)
1. `git diff --stat edcda5be..HEAD` lists only `features/FEAT-2622-practicality-rule/feature.json` (+16/-1) and `plan.yaml` (+1/-1). **Confirmed.**
2. **MF-1 closed.**
   - At the pin, `practicality-carveout-stale-row-current-high-denied` (tests/unit/test-practicality-rule.py:235) PASSes.
   - Mutant M1 drops the `_discounted_non_gating(item)` conjunct. It was applied in memory and its reached-marker fired. Under M1 that case alone is red (`FAIL … no errors`, 30/31), and test-validate-digest-plan-rollup stays 34/34.
   - **The mutant is live in the fixture.** The row is DISCOUNTED med and open; the current finding is PLAUSIBLE high with the same PF id. The pin denies relief, and M1 grants it with zero errors.
   - Natural red: the pin's test file over a `git archive d131c231` tree gives `FAIL 1 of 31: practicality-carveout-stale-row-current-high-denied`.
3. **MF-2 closed.**
   - M2 sets `_severity_errors` to `[]`. Three cases turn red: discounted-high-refused, discounted-unrated-severity-refused and discounted-high-medmax-capped (:142).
   - The receipt says four cases turn red. I measure **3** across both unit files. This is a form issue with no effect on closure (O-09).
   - **Acceptance cases now assert a clean digest.** M12 appends one unrelated error (`artifact: injected unrelated defect`) to `validate()`. Under M12, 12 acceptance cases turn red, among them `practicality-discounted-med-accepted` and `practicality-carveout-discounted-open-relieved`. Under c1's `accepted()` predicate, which ignored errors without `exposure`/`practicality rule`, they would have stayed green.
4. **c1 gaps re-measured** (in-memory mutants, marker reached each time, plus a control run at 31/31 and 34/34):

|gap (c1)|mutant|c2 result|status|direction|
|---|---|---|---|---|
|SC-02 per-finding ceiling|M2 `_severity_errors→[]`|3 red|**closed**|—|
|PF-id case-insensitivity|M3b, c1's exact mutant: regex without IGNORECASE|green on both files. Probe: `must_fix ["see PF-F3C4945F"]` and `"pf-f3c4945f"` are refused at the pin and ACCEPTED under M3b|**still open**|fail-open|
|is_non_gating strip/lower|M4|green|still open|fail-closed|
|PF id ≥8 hex|M5 `{1,32}`|green|still open|fail-closed|
|FAIL relief legs ×5 (must_fix, severity_max, code_grade, all-vs-any, reviewers only)|M6-*|all green|still open|fail-closed|
|severity_max case-fold|M7|green|still open; unreachable via the schema enum [inference]|—|
|relief needs a non-gating row severity|M11|green; probe P5l is denied anyway (`panel.findings malformed`)|equivalent|—|
|record-panel writer malformed exposure|not re-run|panel.py and its tests are byte-unchanged d131c231→edcda5be|unchanged|fail-closed (downstream shape_faults)|

5. **The MF-1 relief predicate.** There are 14 execution probes, all correct at the pin (`/tmp` driver, deleted):
   - **Denied:**
     - two current findings sharing one PF id, one discounted med and one plausible high, in either order (P5a/P5a2);
     - current plausible med (P5c), discounted high (P5d), `unrated` (P5e) or adversary med (P5f) over a discounted row;
     - current malformed exposure (P5k);
     - an extra open plausible row (P5j) or a discounted-high row (P5l).
   - **Relieved:**
     - a resolved row under a plausible-high current finding (P5b/P5b2). The resolved-row path is witnessed: M8 drops the resolved branch and turns 8 bug2582 rollup cases red.
     - both rows discounted (P5h);
     - current `' MED '` (P5g);
     - an extra open discounted row not in the digest (P5i).
   - **New fail-open mutant M10.** `_matched_row_reason` keeps `_discounted_non_gating(row) and is_non_gating(item.severity)` and drops `is_discounted(item.exposure)`. Both test files stay green. P5c, P5e, P5f and P5k flip to **relieved**, so a current plausible-med, adversary-med, unrated or malformed-exposure finding hides behind a stale discounted row. Base DEC-123 denies all four.
   - The stale-row test witnesses only the severity half of the item conjunct: its current finding is plausible *high*. M9 drops the item severity check and relieves P5d. The same digest is still refused by the per-finding ceiling, so M9 is net-equivalent.

## Findings (advisory; QA's gate is green)
- **QA-F1: M10 is an unwitnessed fail-open mutant on the MF-1 relief predicate.** kind: substance; owner T-01 (`tests/unit/test-practicality-rule.py`); severity med.
  - why: the DEC-123 carve-out is an enforcement gate, and the dispatch puts MF-1 relief mutants at full weight.
  - exposure {trigger: contrived (needs a future edit narrowing the item conjunct), vs_today: no_worse (the pin denies all four probes), control: harness}. On the practicality rule alone this is at most med and never must_fix. Ruling on the full-weight carve-out belongs to the lead.
  - Witness: one `run_carveout` row with `current = finding(…, PLAUSIBLE, "med")` over the DISCOUNTED row, expecting denial.
- **QA-F2: the PF-id case-sensitivity gap from c1 is still open.** kind: substance; owner T-01; severity low.
  - Under the mutant, a discounted finding named in must_fix by an uppercase or lowercase-prefix PF id escapes refusal. The code at the pin is correct.
  - exposure {trigger: contrived, vs_today: no_worse, control: harness}.
- **QA-F3: SC-15's text overstates relief after MF-1.** kind: form; owner BRIEF (pm); severity low.
  - SC-15 still says "a reader FAIL whose only open panel row is discounted at med is relieved". Since MF-1, the code also requires the current finding to be discounted. The code is stricter than the text (fail-closed). DEC-123 was amended in MF-3, and the SC text was not.
  - exposure {trigger: plausible, vs_today: no_worse, control: harness}.

## Policy and pin
- Policy: `git show edcda5be091e5b1aa6dcc7021e410aae56de0222:.harness/harness.json` in the harness repo; the feature is unbound. Kinds:
  - unit: `active`.
  - integration: `active`.
  - typecheck: `active`, but no change_type requires it, and the diff touches no `.ts`.
  - The only `when:` predicates fall under change types that no task uses.
- Managed checkout: `.claude/worktrees/.pins/FEAT-2622-practicality-rule--2026-11-28-03-validate-validator--harness-qa`. HEAD is `edcda5be`, clean. I ran `bun install --frozen-lockfile` first (repo G-12). It was removed on return.
- Candidate vs installed:
  - The installed control-plane `validate-digest.py` (main `3e979ae3`) has sha256 `c843d51be869…`.
  - The candidate at the pin has sha256 `e913fa557fb9…`.
  - Every candidate claim here comes from runs in the pin.

## Runner receipts (DEC-255)
Command, run from the pin: `env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/run-unit-tests.py --kind <k> --shard 1/1 --manifest <run>/qa/manifest-<k>.json`

|kind|receipt|tested_commit|files|runner_exit|evidence_defects|
|---|---|---|---|---|---|
|unit|runs/2026-11-28-03-validate-validator/qa/manifest-unit.json|edcda5be091e5b1aa6dcc7021e410aae56de0222|74 expected/74|0|[]|
|integration|…/qa/manifest-integration.json|edcda5be091e5b1aa6dcc7021e410aae56de0222|94/94|0|[]|

Full output:
- Unit: 4414 lines, sha256 `38fc50b38aa3…`. Tail: `pool: 8 workers, 74 files, 36.98s wall` and `unit exit 0`.
- Integration: 8586 lines, sha256 `099143001ebc…`. Tail: `ALL PASSED.`, `pool: 8 workers, 94 files, 492.15s wall` and `integration exit 0`.
- No `FAIL test-*.py` file line appears.
- The one `ERROR could not resolve scan root` line is a passing self-test's expected stderr, followed by `PASS self-test unresolved root refuses`.
- `test-typescript-typecheck.py` passed after the install.

## Fail-first (`verify: automated` SCs)
|SC|test|pre-fix red|
|---|---|---|
|SC-01|tests/unit/test-practicality-rule.py:115-124|pin test file over `git archive 3e979ae3`: all 5 schema cases plus wellformed-accepted FAIL (c2 run)|
|SC-02|:140-153 (incl. medmax-capped :142)|base: all 8 FAIL (c2 run). medmax-capped is isolated by M2|
|SC-03|:167-170|base: summary, pfid and other-finding cases all FAIL (c2 run)|
|SC-04|:174-185|base: all 6 unrated cases FAIL (c2 run)|
|SC-05|tests/unit/test-practicality-record-panel.py|base tree plus the pin test: 5 FAIL; legacy-row-kept PASS, as verify requires (c2 run)|
|SC-13|gen-agent-output.py --check; tests/unit/test-digest-dev-skill.py|c1 reproduction at `0daddfc4`: 6× DRIFT, 3/12 examples refused (notes/review-harness-qa-c1.md). The subject bytes are unchanged since|
|SC-14|tests/integration/test-plan-merge.py `case_f59_record_panel_writes_from_a_lead_digest`|base test against the pin's plan-merge: rc=5 "missing exposure" (notes/fail-first-T-02.md; reproduced in c1). plan_merge is unchanged since|
|SC-15|test-practicality-rule.py:196-235|base: 6 FAIL; plausible-open-denied and stale-row-denied PASS at base (denials base already makes). **MF-1 natural red:** stale-row-denied FAILs at `d131c231` (c2 run)|

These base reds are mostly signature-absent (base refuses `'exposure' was unexpected`), as c1 graded. The MF-1 red at d131c231 is semantic.

## Principles applied
- Build the Lever: one in-memory mutant driver covers 17 mutants over two test files. One probe script covers 14 relief probes and runs under any mutant. No source was edited.
