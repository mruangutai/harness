# Readable append review — FEAT-1928

**PASS: original T-02 F2 is fixed, preserving its historical med/substance/task classification; SC-07 is now met without weakening its signed requirement. Eleven accepted medium maintainability costs remain.** No ship authorization or new source work is implied.

## Stage 1 — approved specification

Read BRIEF, plan decisions D-01–05, prior validator digest and upstream goalcheck before the diff; then append-visibility-rework.md, simplify-append-eng/digest.md and code-risk-current.md. The three source surfaces in `3c1923cf..f9c9f1e` are exactly validate-digest.py `_append_record`, three integration `_append_rule_cases`, and four harness-handoff guidance lines (18 additions/3 removals). All serve SC-07/D-01/D-03; no omission, scope creep, parser alteration, automatic prose repair or changed approval criterion was found. Simplify's zero applies are not correctness evidence inherited by this review.

**Original T-02 F2 disposition:** unfinished prose fencing previously allowed success with an absent/stale successor mapping. At validate-digest.py:1865–1872 the exact safe-dumped suffix is now checked with the existing canonical reader before the first write. An unreadable prospective record refuses, leaving bytes unchanged; the operator appends only the missing human closing fence and retries. This delivers the signed safely-appended, successor-readable outcome rather than redefining successful append as merely writing bytes. Existing digest_record.py:33–67 and historical extra-key consumers are unchanged. SC-07 owning RED22/24 → GREEN24/24 and Main's separate refusal2/unchanged-bytes → human-fence-only closure → retry0/exact readback are recorded in notes/append-visibility-rework.md; these were Main's executions, not mine. Original mismatch is resolved, not severity-downgraded or waived.

**SC-05 inspection:** notes/live-digest-object-probe-current.md:5–17 binds clean executed ee39d887, OMP18.6.1, launcher hash, separately labelled release provenance, actual native raw-null rejection, same-job retry and exact accepted object/exit0. Independently enumerated ee39→f9: exactly eight feature metadata/evidence paths (feature.json, risk note, native receipt/transcript, lifecycle receipt, browser proof/two images), no source/tests/schema/config/probe delta. Thus execution-source equivalence holds at the review pin. Recorded transcript hash is 6babd8856af0f81c49ed7b9ff1dec2b265e267e6ca47c093cc56b8c9dc75c5d9; no receipt verifier/probe was executed here.

**SC-08 inspection:** validate-digest.py:1843–1875 positively uses durable-only canonical comparison and safe_dump; harness-handoff/SKILL.md:40–45 instructs object retry, not agent-authored machine fencing. The bounded diff changes none of the previously inspected removal surfaces, schema authority, DEC-237 or DEC-208. Prior SC-01–06/08 evidence remains applicable to unchanged subjects; literal SC-06 remains 291 retained rows/exact14 approved deltas, with disclosed historical failures retained, not regenerated. No blanket eight-SC audit or provider-wide native-proof claim is substituted for these bounded inspections.

## Stage 2 — correctness and quality

- `_append_record:1857–1864` reads the held descriptor once and preserves identical-last-mapping no-write before serialization. Existing malformed trailing prose does not force duplicate identical records: the canonical reader already exposes the identical object. Changed content must pass prospective equality; None/stale mapping fails closed before write. The checked suffix is precisely the suffix written, not a second rendering.
- `check_artifact_file:1827–1840` still obtains authorized_digest before any read/append. digest_destination.py:90–146 rechecks runtime/parent/feature, checkout, registered run/grant and exact destination, traverses descriptor-relative O_NOFOLLOW directories, opens a regular writable O_APPEND target and closes descriptors on all paths. The new guard cannot mint authorization. Authorization/read/decode/write/flush errors still reject; no success exception suppression or live-text fallback was added. This is static review, not an independent race or I/O-fault execution.
- Tests at test-validate-digest.py:1586–1592 call the real hook through `_append_case:1497–1512`, asserting exit and literal bytes together. Two negative cases bind first-record and stale-correction suppression; removing the guard restores exit0/changed bytes and reddens them (Main's observed RED). The positive closed-text-fence case rejects an indiscriminate fence ban and asserts the exact appended dump. Existing identical/correction/historical-extra-key cases remain. Retry/readback is Main's actual separate CLI evidence, not falsely described as a new permanent retry assertion. No tests, mutants, builds, linters, formatters or probes ran here.
- One additional canonical scan on a non-idempotent return earns the invariant at the existing writer seam; no duplicate parser or shallow wrapper is introduced. There is no measured performance claim.

Independent OLD absolute metadata grader, canonical91e88653→exactf9, exited0 (`artifact://864`): 230 bar passes, eleven grade-2 reason requirements, zero high/ungraded. `_append_record` CC6/COG6/ABC13.2 grade4; `_append_rule_cases` CC1/COG0/ABC25.5 grade3. The eleven reasons remain sufficient, one per function:

| Owner | Function | Accepted reason (med/substance/task, unchanged) |
|---|---|---|
| T-02 | digest_destination.authorized_destination | Keep coupled identity/checkout/run/exact-target proof together; omitting a conjunct authorizes another run. |
| T-02 | object probe _task_dispatch | Ordered authored/executed/error correlation prevents misattributed strict dispatch. |
| T-02 | object probe _yields | Same-child call/result pairing prevents counting rejected null as accepted. |
| T-02 | object probe _native_yield_started | Job/phase/tool/call conjunction distinguishes native execution from hook-only refusal. |
| T-02 | object probe run_live | One RPC lifetime owns session creation, event pump and cleanup. |
| T-02 | object probe verify | Explicit transcript/runtime/Harness/outcome checks prevent unsupported receipts. |
| T-02 | object probe main | Dry/verify/live modes and exit outcomes remain visibly distinct. |
| T-02 | lifecycle probe run_live | Session/claim/run-record mandatory cleanup shares one lifetime. |
| T-02 | lifecycle probe receipt_header | Launcher identity remains distinct from release metadata provenance. |
| T-02 | test-digest-dev-skill.check_refusal | Concrete refusal/schema/receipt-skill ownership bind the same guidance invariant. |
| T-01 | test-digest-schemas._object_shape_violations | Full closed/required/no-null conjunction detects open/nullable contracts. |

Other original advisories remain unchanged: T-02 QA F1 low/substance native-null CI guard gap; T-02 QA F2 low/form prose enum drift guard gap; T-02 F-UI-02 low/form stale SubagentStop attribution. No speculative cleanup requested. Main's browser-guidance-proof.md:3–9 now supplies the previously missing durable managed-Chromium light/dark pointer; no independent browser/full accessibility/UAT execution claimed. Native proof remains OpenAI-only; both Anthropic STRINGnull17/18 failures and separate canonical-provider111 evidence retain their meanings. handoff_comprehension and URI-routing concerns remain outside this source delta.

## Binding and scope

Independent git metadata (`artifact://852`) establishes merge-base91e88653, all nine human commits below, and 28 paths since prior3c: three source surfaces plus25 feature evidence/metadata paths. Full commit list inspected; inherited upstream provenance was not relabelled feature work. Only dirty tracked path was this feature's feature.json (allowed ledger domain); its active review_sha agrees with dispatch f9. Committed feature.json still carries historical3c and is not substituted for the active registration. No source edits or unrelated BUG1016 checkout access. Main owns terminal checks and closure; no additional test run is requested by this bounded review. Open questions: none.

```yaml
VERDICT: PASS
DIGEST:
  headline: "T-02 F2 readable-append mismatch is fixed and SC-07 met; eleven justified medium costs remain."
  severity_max: med
  findings:
    - {kind: substance, scope: task, severity: med, reader: code-reviewer, summary: "T-02 retains ten accepted grade-2 maintainability costs.", why: "Exact-pin OLD grading artifact://864 reproduces authorized_destination, six object-probe functions, two lifecycle functions and check_refusal; individual reasons above remain sufficient."}
    - {kind: substance, scope: task, severity: med, reader: code-reviewer, summary: "T-01 _object_shape_violations retains its accepted grade-2 conjunction cost.", why: "CC12/COG21/ABC24.2; weakening closed/required/no-null conjunction loses contract detection."}
    - {kind: substance, scope: task, severity: low, reader: code-reviewer, summary: "T-02 QA F1 native-null CI guard gap remains.", why: "Actual live proof exists; this unchanged regression-guard advisory is not absent SC-04 evidence."}
    - {kind: form, scope: task, severity: low, reader: code-reviewer, summary: "T-02 QA F2 prose enum drift guard gap remains.", why: "Original low/form classification retained; no current enum mismatch established."}
    - {kind: form, scope: task, severity: low, reader: code-reviewer, summary: "T-02 F-UI-02 stale SubagentStop attribution remains.", why: "Unchanged specialist instruction wording, not a restored enforcement path."}
  must_fix: []
  spec_violations: []
  code_grade: grade_2
  reviewed: 91e8865346a7bf4e2b8a5bf2033b17f01f8d6b14..f9c9f1e21d05ae1d64f3f1fed38465be89059dc1
  human_commits_in_scope: [f9c9f1e21d05ae1d64f3f1fed38465be89059dc1, ee39d8876cde56e06561266ba02dfc174176559f, 3c1923cf2475c1e976b5b941a5b5c7fc445f9e19, c81a57b6c7d62a63b52614e4bcb64a07f7d9fa47, 9e910a4ee31a9c9ce2c3a3e08b2f8ddf4c48e250, 10a9594cae75d241185ecde8745762ec7cd3e5a5, 828b3605d6334b96a6d21bfc8f93140b6b26a9c2, 4379809b1ce7e37e89407b2ade7912abc898fed9, 27ea22063047a4ea1776eef05a64e05d0a6417b1]
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/notes/review-harness-code-reviewer-append.md
```
