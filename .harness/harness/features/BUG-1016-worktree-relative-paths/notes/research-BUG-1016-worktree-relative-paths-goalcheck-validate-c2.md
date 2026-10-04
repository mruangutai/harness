# BUG-1016 goalcheck — validate c2

**PASS: operator and code maintainer acceptance are met under the operator-approved amended predicate.** R1 is resolved by authority change, not implementation repair. No new must_fix; current c2 test execution remains QA's final validation gate, not a claim of this reader.

## Pin and evidence

Review only `55c99a856321ef9d059b144b6ee2ac2bf1f75096`; canonical range `af2a958ab06c0d6fc026b363b59fc3147e3982f1..55c99a856321ef9d059b144b6ee2ac2bf1f75096` (observed merge-base main/pin). Current feature.json review_sha matches; the pinned record still carries the preceding pin, historical bookkeeping rather than review authority. Pinned BRIEF approval and plan approval are approved. Read pinned notes/brief-amendment-2026-10-04.md.

The adapter, tests, DECISIONS.md and DECISIONS-INDEX.md have **no diff** from prior QA pin `8211687fd442258a4ae1a50d8e5375228a51b540` to this pin. Prior evidence: notes/review-harness-qa-c1.md:18-34 (123 pass/0 fail, task/index/kind verifies), notes/t01-receipts-main-session.md:5-30 (named red-first cases, controls, mutations), runs/validate-validator/digest.md:25-49 (receipt binding and assessed-and-dismissed F1/F2). These are reused receipts, not tests executed in c2 by PM. No builds/tests/linters run here.

## Perspective coverage and amended contract

- **operator: pass**, SC-01..SC-06, all traced by T-01. Pinned revised-input assertions cover six path interfaces and edit, omitted defaults, resolver refusal/authority, guards, explicit destinations, and silent/main/Bash controls.
- **code maintainer: pass**, SC-07, traced by T-01 and T-02. DEC-251 and its index row document the single existing resolver and all seven tools, including actual ast_edit paths-array interface; no second resolver or other-host change in the pinned production diff.

Explicit R1 remeasurement by pinned inspection: rootTarget (.omp/extensions/harness-hooks.ts:354-362) computes `raw.trim().replace(/^"(.*)"$/, "$1")`, classifies the resulting target, and inserts the root into the original raw string, preserving whitespace/quotes. Thus `"~/notes.md"` remains unchanged, ` /abs/x ` remains unchanged, and ` "src/a.ts" ` becomes ` "<root>/src/a.ts" ` [inspection-derived, not executed probes]. Each semicolon entry is independently transformed by rootPathList; blank targets remain verbatim. This now agrees with amended BRIEF Constraints and DEC-251 (.harness/harness/docs/DECISIONS.md:8029-8039), unlike c1's raw-entry authority. Quoted MV regression and padded excluded list entries corroborate the classification/preservation mechanisms. No dedicated quoted-tilde runtime case is claimed.

## SC outcomes

All test line anchors below refer to pinned tests/unit/omp-hooks.test.ts; receipt anchors refer to notes/t01-receipts-main-session.md. Automated evidence is prior QA execution bound to byte-identical pinned surfaces.

| SC | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | met | automated | Tests:1320,1338,1347; receipt:8-10; prior QA:19,27; amended predicate inspection above |
| SC-02 | met | automated | Tests:1400,1505 (multi-section/MV, literal line endings and original/revised pre/post); receipt:13,20; prior QA:28 |
| SC-03 | met | automated | Tests:1357,1369 (omitted/null defaults, required paths not invented, blank/list controls); receipt:11-12; prior QA:29 |
| SC-04 | met | automated | Tests:1432-1495 (cache/run boundaries, no match, refusal/error/unusable output, spoofed prose, siblings, held claim); receipt:14-19; prior QA:30 |
| SC-05 | met | automated | Tests:1338,1382,1505,1529 plus retained BUG-2003 URI controls; receipt:20-21; prior QA:31 |
| SC-06 | met | automated | Tests:1382,1545 controls; shared governed revised-input cases:1320-1495; receipt:8-21,26; prior QA:32. Dedicated control red-first is not required; c1 F1/F2 stay dismissed |
| SC-07 | met | inspection | Pinned DEC-251:8013-8089; index DEC-251 @8013; hook rootTarget/rootedInput:354-399, featureRoot/rootCall:982-1013 and pre/post integration:1174-1184,1451-1458; tests:1320-1549. Predicate, interfaces, authority, outcomes, URI policy, silence and unchanged hosts agree |

## Boundaries and open questions

UI: no scope; the canonical adapter/test/docs diff has no visual or interaction surface. No UAT or typecheck assurance claimed (BRIEF declares the runner gap). Prior Q1 host normalization/refusal of agent:// and xd://report_issue remains **nonblocking and outside this pinned diff**, not an introduced adapter finding. Pre-existing ast_edit mutation-set omission and fixture reuse backlog remain out of scope. Current c2 prescribed execution is owned by QA; this goalcheck does not replace its gate. No source/test/docs/plan changes.
