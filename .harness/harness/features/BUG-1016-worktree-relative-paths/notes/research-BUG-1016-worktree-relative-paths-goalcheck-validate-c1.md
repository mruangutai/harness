# Goalcheck — BUG-1016-worktree-relative-paths — validate c1

**PASS: both shipped perspectives are discharged; SC-01..07 are met.** Review pin: `8211687fd442258a4ae1a50d8e5375228a51b540`; diff baseline: `merge-base(main,pin) = af2a958ab06c0d6fc026b363b59fc3147e3982f1`. All implementation/test/doc citations below name files at that pin, inspected through `git show` and the baseline-to-pin diff, not HEAD.

Checkout/citation base: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/`.
Feature-note base: `.harness/harness/features/BUG-1016-worktree-relative-paths/notes/` within that checkout.

## Shipped perspectives — one grade each

- **operator — pass:** SC-01..06 discharge relative file-tool paths, omitted search defaults, multi-section/MV edits, explicit destinations, fail-closed discovery, unchanged main/Bash behavior and silent success; pinned `tests/unit/omp-hooks.test.ts:1320-1548`, retained red-first receipt, and QA's independently executed 123 pass/0 fail substantiate the adapter diff at `.omp/extensions/harness-hooks.ts:352-401,980-1015,1172-1188,1449-1459`.
- **code maintainer — pass:** SC-07 is discharged by the single DEC-251 contract and index row (`.harness/harness/docs/DECISIONS.md:8013-8089`, `DECISIONS-INDEX.md:237`), agreeing with the seven-tool adapter/tests above; discovery delegates to the existing feature-root command, and neither OMP nor Claude Code hosting changes. T-01 traces SC-01..07; T-02 additionally traces SC-07.

## Criterion evidence

Automated evidence: `notes/review-harness-qa-c1.md:18-34` and QA's returned DIGEST. QA established executed files byte-equal to the pin. Retained `notes/t01-receipts-main-session.md` records 14 new failures against the unmodified adapter, 109 passing tests, then 123 pass/0 fail; production/tests have no diff from receipt commit `10f38a42` to the pin. Receipt assurance is preserved, not claimed as my execution.

| SC | Verdict/method | Specific pinned test and retained red evidence |
|---|---|---|
| SC-01 | met / automated | omp-hooks.test.ts:1320,1338,1347: all six path interfaces, preserved fields/list/selector text; receipt :8-10 |
| SC-02 | met / automated | :1400,1505: section/MV rewriting, quoted spaces, untouched rows/endings and pre/post effective targets; receipt :13,20 |
| SC-03 | met / automated | :1357,1369: omitted/null search defaults, required-argument and explicit-blank controls; receipt :11-12 |
| SC-04 | met / automated | :1432-1503: feature-root argv/cache boundaries, no-match, ambiguous/error/unusable output, spoofed prose, siblings and held claims; existing lineage controls :586,646 remain; receipt :14-19 |
| SC-05 | met / automated | :1382,1505,1529 plus :1060-1182: absolute/tilde/URI controls, rooted mixed-file URI and MV policy, named pre/post refusals; receipt :20-21 |
| SC-06 | met / automated | :1382,1545: unchanged main/Bash inputs and silent post; revised-input-only assertions :1320-1379 cover new governed rewrite path failing first; receipt :8-21, with already-green controls honestly labelled :26 |
| SC-07 | met / inspection | DEC-251 :8013-8089; index :237; registerHarnessHooks/rooting helpers and OMP lifecycle tests cited above agree on defaults, predicate, lists, edit/MV, silence, resolver/claim authority, refusals, URI policy and unchanged hosts |

## Findings and boundaries

- No new product finding. Preserve QA **F1**, kind **substance**, original severity **low**, owner **harness-qa**, task **T-01**: no dedicated SC-06 red-first case. SC-06 explicitly requires the new rewrite path red-first, not already-existing silence/main/Bash controls; shared discriminating cases satisfy it. Advisory, not partial delivery.
- Preserve QA **F2**, kind **form**, original severity **low**, owner **main session**, task **T-01**: pasted red-first receipt lacks an adjacent invocation/exit line. Named failures bind to pinned cases; assurance remains receipt-tier.
- `ast_edit` is graded as actual `paths: string[]` (DEC-251 :8020-8027; adapter :380-385; test :1328-1329), not the signed task's inaccurate singular-field prose. Its pre-existing omission from mutation authorization/domain gating is expressly unchanged; simplify F1 fixture reuse remains flag-only.
- BRIEF's approved Verification gaps sanctions no TypeScript typecheck runner and no operator UAT. Neither is invented as a failing SC. No source, tests, fixtures, approvals, BRIEF, plan or scope changed; no builds/tests/linters/formatters run by this reader.
- Tooling observation, **not attributed to the pin**: peer `write agent://Bug1016Build2.FrightenedCoral` was refused as filesystem `agent:/...`; required `write xd://report_issue` likewise refused as `xd:/report_issue`. Owner: Harness host/guard maintainer. This did not prevent evidence collection through read tools.

## Open questions

Q1 (nonblocking; Harness host/guard maintainer): Why does this reader's live Write guard normalize allowed agent:// and xd://report_issue URIs into filesystem paths? Both attempted calls were blocked; inspect outside this feature's unchanged scope.
