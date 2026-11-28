# QA gate — FEAT-2622 validate c1 (run 2026-11-28-02-validate-validator)

**BLUF: PASS.** The matrix floor is unit + integration (T-01 `cross_module`; T-02 `logic` → unit; T-03..T-05 `docs` → none). Both kinds ran once at `d131c231d3e4f278019a8acdffd4706e6f622cee` and were green: unit 74/74 files exit 0, integration 94/94 files exit 0. Both receipts pass `check-integration-shards.evidence_defects` with `[]`. Every `verify: automated` SC has a named test and a pre-fix red I reproduced myself. Adequacy is weaker than the green suite suggests. **Removing validate-digest's per-finding severity ceiling (`_severity_errors`, SC-02's main leg) leaves the whole SC suite green.** Five SC-15 acceptance legs and the severity/PF normalisation legs also have no witness that tells a mutant apart (see the gaps table). I found no relief leak at the pin: every bypass probe was refused or denied, and those are execution-backed.

## Policy and pin
- Policy blob: `git show d131c231d3e4f278019a8acdffd4706e6f622cee:.harness/harness.json` in the harness repo (unbound feature). unit and integration are `active`; typecheck is `active` but no change_type here requires it, and the diff touches no `.ts`.
- Managed checkout: `.claude/worktrees/.pins/FEAT-2622-practicality-rule--2026-11-28-02-validate-validator--harness-qa`. HEAD = `d131c231`, clean. I ran `bun install --frozen-lockfile` first (repo G-12).
- **tsc environment gap closed, not waived.** After the install, `test-typescript-typecheck.py` passed (exit 0, "PASS bun run typecheck passes on the real tree"), so integration is satisfied on the captured run.
- Candidate vs installed: the installed control-plane `.agents/skills/harness/bin/validate-digest.py` (main @ `3e979ae3`, sha256 `c843d51b…`) is the base copy. The candidate at the pin is sha256 `b2100eb0…`. Every candidate claim below comes from tests or probes run in the pin.

## Runner receipts (DEC-255; command: `env -u HARNESS_AGENT_TYPE python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind <k> --shard 1/1 --manifest <run>/qa/manifest-<k>.json`)
|kind|receipt|tested_commit|files|exit|defects|
|---|---|---|---|---|---|
|unit|runs/2026-11-28-02-validate-validator/qa/manifest-unit.json|d131c231…|74/74|0|[]|
|integration|…/qa/manifest-integration.json|d131c231…|94/94|0|[]|
Full runner output: unit log 4409 lines ("74 files … OK", sha256 `6c4d3879…`); integration log 8585 lines ("ALL PASSED.", sha256 `52986025…`). Per-file exit lines: 168 of 168 are `exit 0`. The SC files: test-practicality-rule, test-practicality-record-panel, test-digest-dev-skill, test-digest-schemas and test-validate-digest-plan-rollup (unit); test-validate-digest, test-validate-digest-shadows, test-panel-findings, test-plan-merge, test-check-state-records, test-check-omp-port, test-plan-team and test-typescript-typecheck (integration).

## Fail-first (each reproduced by me, never inherited)
|SC|test|pre-fix red|class|
|---|---|---|---|
|SC-01|tests/unit/test-practicality-rule.py:110-119|pin test over a `git archive 3e979ae3` tree: missing-exposure is "no errors" (base accepts it); the other four are red because base refuses `'exposure' was unexpected`|semantic (missing) / signature-absent (4)|
|SC-02|:132-142|base: all 7 red; errors are additionalProperties only, never `practicality rule`|signature-absent|
|SC-03|:156-159|base: 3 red, same cause|signature-absent|
|SC-04|:163-172|base: 6 red, same cause|signature-absent|
|SC-05|tests/unit/test-practicality-record-panel.py:129-137|base plan-merge: 5 red with exit 0, exposure silently dropped or missing exposure accepted; legacy-row-kept PASS at base, as the verify requires|semantic|
|SC-13|gen-agent-output.py --check; tests/unit/test-digest-dev-skill.py|at T-01 `0daddfc4`: 6× DRIFT, exit 1; 3/12 examples fail with "'exposure' is a required property"; both green at the pin|semantic|
|SC-14|tests/integration/test-plan-merge.py `case_f59_record_panel_writes_from_a_lead_digest`|the base test alone against the pin's plan-merge: `rc=5 … missing exposure`; the control (base test against base bin) is green. The whole base suite aborts its pool on a ValueError, which confirms the receipt's deviation 2|semantic|
|SC-15|test-practicality-rule.py:184-216|base: 5 of 6 red. carveout-plausible-open-denied passes at base, because it is a denial base already makes|signature-absent|
The fail-first-T-01.md claim of "16 of 16" holds: its regex counts only the `-refused/-relieved/-carried` names, and the file has 29 checks. fail-first-T-02.md's deviation holds too. Signature-absent means base refuses every exposure-bearing digest wholesale. Those reds show that the `practicality rule` refusal is new; they cannot show that base accepted the bad digest (O-03).

## Leg adequacy — in-memory mutants (sitecustomize, no source edited; marker reached each time)
|leg|witness|mutant → result|
|---|---|---|
|SC-02 per-finding ceiling in validate-digest|discounted-high-refused :132|`_severity_errors→[]`: **suite green** (severity_max leg masks it). Probe P1 (discounted high, severity_max med): refused at the pin, accepted under the mutant. **GAP**|
|ceiling in panel_findings (shared)|record-panel-discounted-high-refused; test-panel-findings case7d|`practicality_fault→None`: record-panel test red ✓|
|adversary exception|adversary-high-accepted; record-panel-adversary-high-carried|drop the exception: both red ✓|
|trimmed/case-insensitive non-gating set|none|`is_non_gating` without strip/lower: green. Fail-closed direction (P3b ' Med ' is over-refused). **GAP**|
|must_fix summary containment|mustfix-summary-refused :156|summary branch removed: red ✓|
|must_fix PF id, ≥8 hex|mustfix-pfid-refused :157 (exactly 8 hex)|min 9: red ✓. **min 1: green**, so no witness that PF+7 hex is not a tie (P4a). **GAP** (fail-closed)|
|PF id case-insensitivity|none|case-sensitive regex: green. P4b/P4c (uppercase PF) then escape the tie, which is fail-open. **GAP**|
|unrated refused for 4 / accepted for 2 leads|:163-172|both directions red ✓|
|severity_max needs a non-discounted gating finding|severity-max-discounted-only-refused / witnessed-accepted|leg removed: red ✓; always-refuse: red ✓|
|severity_max case-fold|none|no-lower: green. Probably unreachable: severity_max is a schema enum [inference]|
|reviewer FAIL refusal|fail-discounted-only-refused :187|leg removed: red ✓|
|FAIL relief: must_fix present / code_grade fail / non-gating severity_max / all-vs-any / reviewers only|fail-with-mustfix-accepted carries a plausible finding, so `all(discounted)` short-circuits|each mutant green. P5a, P5b, P6 and P9 show the real behaviour. **GAP ×5** (all fail-closed)|
|DEC-123 discounted-open relief|carveout-discounted-open-relieved|resolved-only: red ✓|
|plausible row denies relief|carveout-plausible-open-denied|any-exposure: red ✓|
|relief needs a non-gating severity|none|severity conjunct dropped: green, but equivalent: C2 (discounted high row) is denied anyway as "panel.findings malformed"|
|record-panel malformed exposure|none at the writer level|writer check dropped: still exit 5 via the downstream shape_faults (test-panel-findings case7c)|

## Bypass probes at the pin (execution-backed)
All of these were refused or denied: discounted severity ' HIGH ', 'medium' or 'med\u200b'; a discounted high finding behind a plausible low one; a malformed or missing-control exposure; 'UNRATED'; uppercase PF tokens; adversary, plausible or unrated open rows (relief denied); a discounted high row; record-panel severity ' HIGH ' or 'none'.
Accepted, and not leaks under the shipped rule: a reworded must_fix ("fix the stale cache entry"), ruled under OQ-01; PF+7 hex; a plausible finding with severity 'none' propping up severity_max high, where DEC-31 still gates.

## Principles applied
- Build the Lever: one sitecustomize mutant driver plus one probe script cover 27 mutants across three test files, instead of hand-run swaps.
