# QA gate (integrated upstream) — FEAT-1928, pin 3c1923cf (source = c81a57b6, base origin/main 91e88653) — VERDICT: PASS

**BLUF.** Floor met, nothing new. The pin differs from c81a57b6 only in feature-ledger files, so the c81a57b6 pool and fresh receipts bind to the pin's source. The 83746a42 PASS still stands, now at the integrated pin. I made no test or source edits and did not rerun the suite. I ran only the plan's `--verify-receipt` CLI, as authorized. Two original low findings stay open.

## Phase 1 (from BRIEF + plan.yaml + control-plane harness.json, before source)
Unchanged from `review-harness-qa-final.md`: T-01 `api` → unit. T-02 and T-04 `cross_module` → unit + integration. T-03 and T-05 `docs` → none. Locally-run surfaces: `inflight_claim_lifecycle_live` and `digest_object_contract_live`. Control-plane harness.json is the pre-cutover one and has no `digest_object_contract_live` kind. That kind exists only in the pin's own harness.json (carried over from the prior note).

## Binding to the pin
- `git diff c81a57b6 3c1923cf` = 6 files, all under `.harness/harness/features/FEAT-1928-…` (STATE.md, feature.json, code-risk-current.md, live-digest-object-probe-current.md and its transcript, live-omp-probe.md). Zero bytes differ under `tests/`, `.omp/`, `.claude/`, `.agents/`. Blob ids for `harness-hooks.ts` and the probe are identical at both commits.
- Pool, artifact://710: `run-unit-tests.py` 120 files, 8 workers, 141.82s. 120 `----- … (exit N` headers, 0 non-zero. `git ls-tree 3c1923cf` has 120 `test-*` files outside tests/manual, matching. `test-omp-hooks.py` ran and the bun run reported 134 pass / 0 fail. The prior pin showed 112, and the rise is the incoming BUG1016 tests.
- Native receipt `live-digest-object-probe-current.md`: HEAD c81a57b6, 0 uncommitted paths, OMP `omp/18.6.1`. It runs 18/18 on OpenAI: Main `gpt-5.6-terra`, child `gpt-5.6-sol`. The null yield was rejected by `omp-yield-tool (YieldTool.execute)`, then the same job `DigestObjectProbe` retried and was accepted, with structured output valid. I recomputed sha256 for the transcript (`1c7f6b50…7def`, 43 records) and for all seven under-test files. All equal the receipt, and all equal the pin's files.
- **Executed** `python3 tests/manual/probe-digest-object-contract.py --verify-receipt <notes>/live-digest-object-probe-current.md` from the target. Result: **33/33 PASS, exit 0**. It re-derives from the transcript, the launcher hash, the HEAD commit and the clean tree.
- Lifecycle, `live-omp-probe.md` latest appended run 2026-10-04T22:14:13Z: PASS 28/28 at HEAD c81a57b6. The recorded sha256 for `digest_destination.py` (`e386daf6…`), `validate-digest.py` (`089ec5f2…`), `harness-hooks.ts` (`456c9af7…`) and `probe-inflight-claim-lifecycle.py` (`b968b472…`) all match the pin's bytes. Earlier runs are retained unaltered by the append. The prior Main-run note (bun 112 → 134) is consistent.
- Caveat: the worktree has an uncommitted `feature.json` modification (Main-owned ledger). It is outside every under-test file, so the receipt's clean-tree claim concerns the run-time tree and is unaffected.

## Matrix
| kind | state | evidence |
|---|---|---|
| unit | satisfied | 46 unit files in the 120 pool, exit 0 (test-digest-schemas, test-digest-record, test-digest-dev-skill, test-feature-record, test-omp-hooks.py → bun 134/0) |
| integration | satisfied | 74 files, exit 0 (test-validate-digest incl. 37/37 undeclared-key and 81/81 BUG-1898, -shadows, test-plan-merge, test-check-state-feat59, test-check-domain-artifact, test-check-plan-routes, test-suite-claim-preservation) |
| inflight_claim_lifecycle_live | locally_run, recorded | 28/28 above. This is a live kind, not a CI kind |
| digest_object_contract_live | locally_run, recorded | 18/18 live + 33/33 verify-receipt, executed by me |
| functional, eval | not_applicable | excluded, DEC-187 |

Provider suites (T-05 verify) 111 pass / 0 fail / 221 expects is prior canonical evidence. It tests OMP source, which is unchanged, so it is valid. It is distinct from the current runtime proof, which is OpenAI only. Two Anthropic runs generated the string `"null"` and failed 17/18. They are preserved in `live-digest-object-probe-null-string-fail*.md`. No Anthropic native proof is claimed.

## Fail-first (per automated SC)
Evidence is carried from `review-harness-qa-final.md`. I did not re-run the RED proof. The base→pin source delta since that note is nil, apart from the incoming BUG1016 merge. Tier: natural RED, pre-change source with post-change tests, from my 83746a42 reproduction. The raw output was ephemeral and the quoted lines are the retained evidence. SC-04 also has the retained natural RED `live-digest-object-probe-native-red.md/.json`, 17/18 FAIL.
SC-01: `omp-hooks.test.ts:1227,1259`. SC-02: `test-validate-digest.py:960,962` and `test-digest-dev-skill.py:106,119,155,158`. SC-03: `test-digest-schemas.py:169,181,223`. SC-04: the probe plus the native-red receipt. SC-06: `test-validate-digest.py` and `-shadows`. SC-07: `test-digest-record.py:74-115`, `test-plan-merge.py:2932`, `test-check-state-feat59.py:710,714`.

## SC-06 literal binding (no regeneration)
- 291 `parity-fixtures/P####.json` tracked at the pin (`git ls-tree | grep -c` → 291). `receipt-scripts/` holds `object-results.json` and `baseline.json`. The final-QA derivation (291 rows each side, 14 rows with baseline_accept ≠ new_accept: P0137,158,159,161,162,166,168,169,171,174,178,181,182,188, = the 4+5+3+2 enumerated deltas, 0 unplanned, none null) is retained. Fixture, receipt-script and validator sources are byte-identical, so it carries to the pin. The incoming merge did not touch the receipt-scripts or `validate-digest.py` (`089ec5f2…` unchanged).
- Three historical generator group failures stay disclosed as failures (`run_reviewer_severity_enum_cases`, `run_documented_contract_cases`, `run_t08_revision_proof`), not among the 291, per `parity-group-error-disclosure.md`. They are not relabeled, waived or subsetted. Permanent boundaries are carried by the in-pool suites, all exit 0.

## Findings (original severity/kind preserved)
**F1 — kind: substance · severity: low · raiser: qa · task: T-02** — Still unaddressed at the pin. `harness-hooks.ts:1272` (`digest == null && input.type === "result"` returns undefined so YieldTool rejects) has no CI-resident test. No `type: "result"` input appears in `omp-hooks.test.ts`. The native-null proof lives only in the live probe plus `--verify-receipt`, which is satisfied. Non-blocking.
**F2 — kind: form · severity: low · raiser: qa · task: T-02** — Prose enum legends are still unpinned to the schema enums. The agent examples are schema-validated, but legends such as `severity_max: none|low|med|high|critical` (harness-validator-lead.md:132) have no drift guard. Non-blocking.
Carried advisories (not mine to convert): medium unfinished-fence hiding an appended mapping, real SC07 mismatch; eleven accepted grade2 costs; low UI stale SubagentStop attribution. No prior high remains. I independently demonstrated none of them away.

## Open questions
- Q1 (non-blocking): the `handoff_comprehension` runner_note asks for a live run before a ship that changes the handoff contract. Its detect surface is untouched, so the rule does not require it. Operator's call.
- Q2 (non-blocking): SC-04 native proof is OpenAI only. The Anthropic string-null failures stand.

## Principles applied
- harness-verification-rules: the matrix was read from the control-plane harness.json. The pin binding is by per-file git diff, per-file sha256 and a header-level exit count, not by the suite's summary line. Fail-first is carried with its tier labelled and not re-claimed as freshly executed.
