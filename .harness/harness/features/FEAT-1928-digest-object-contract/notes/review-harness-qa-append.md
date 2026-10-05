# QA gate (append closure) — FEAT-1928, pin f9c9f1e2 (clean source = ee39d887, base 91e88653) — VERDICT: PASS

**BLUF.** Floor met. The SC-07 guard has natural RED→GREEN evidence and the full pool is green at the source bytes the pin carries. All seven recorded hashes equal the pin's bytes. `--verify-receipt` was executed by me: 33/33, exit 0. No suite rerun, no authoring, no bun run. The guard's tests (three `_append_rule_cases`) bind two distinct open-fence forms and the closed-fence control. Advisory gaps carry unchanged. SC-07's "reader" claim is now supported by the unfinished-fence refusal tests. SC-07's tracked parts (idempotent no-duplicate, correction append, historical byte-unchanged) are unchanged and still green in the pool.

## Phase 1 (BRIEF + plan.yaml + control-plane harness.json, before source)
Unchanged: T-01 `api` → unit. T-02, T-04 `cross_module` → unit + integration. T-03, T-05 `docs` → none. Locally-run kinds: `inflight_claim_lifecycle_live`, `digest_object_contract_live`. Phase 1 expectation for this delta, from SC-07 alone: an append whose result the durable reader cannot select must be refused with bytes unchanged. A closed prose fence must still append. An identical object must still not append. Expectations all have a test (below).

## Binding to the pin (my own commands)
- `git diff ee39d887..f9c9f1e2` = 8 files, all `.harness/harness/features/FEAT-1928-…` (feature.json, 2 PNG, browser-guidance-proof.md, code-risk-current.md, probe receipt + transcript, live-omp-probe.md). `git diff --stat … -- tests .omp .claude .agents` is empty.
- `git diff 3c1923cf..f9c9f1e2 -- tests .omp .claude .agents` = exactly three files, 18 ins / 3 del: `validate-digest.py` (`_append_record`, 10 lines), `test-validate-digest.py` (three cases), `harness-handoff/SKILL.md` (four lines). Matches the briefed delta; nothing else.
- `receipt-scripts/` and `validator-parity.md` have zero diff vs 3c1923cf. 291 `parity-fixtures/P*.json` are tracked at the pin (`git ls-tree | grep -c` → 291). The 14-delta/277/zero-unplanned derivation in `review-harness-qa-final.md` carries because fixtures, scripts and the parity doc are untouched. Append-only change does not alter the parity outcomes. I did not regenerate it.
- Working tree: the only modified path is `feature.json` (Main-owned ledger), outside every under-test file. Source at the pin equals source in the tree the pool ran on.
- **Hashes**: I recomputed sha256 for all seven under-test files from `git show f9c9f1e2:<path>`. Each equals the receipt: common.json `004ec08b…`, harness-documentor.json `7917570a…`, digest_schema.py `d44b6b2e…`, validate-digest.py `ee10a77d…`, digest-schema.ts `0ed3f181…`, harness-hooks.ts `456c9af7…`, probe `d5769a3a…`. Transcript sha256 `6babd885…75c5d9`, 43 records, equals the receipt.
- **Executed by me**: `python3 tests/manual/probe-digest-object-contract.py --verify-receipt …/live-digest-object-probe-current.md` → "receipt verification 33/33", exit 0 (clean tree at ee39, files byte-identical to commit, launcher byte-identical, ids/model/frames match transcript). This did not rerun the live probe. The bun half of the T-05 verify was not run by me. The prior accepted evidence (111 pass / 0 fail / 221 expects) tests OMP source I did not touch, and I carry it as prior evidence only.
- Receipt contents: OMP `omp/18.6.1`, launcher sha256 `348d0987…041a`, source `2a2c6dcb…` labeled release-tag metadata. Harness HEAD ee39 + 0 uncommitted. OpenAI Main `gpt-5.6-terra`, child `gpt-5.6-sol`. Null yield `{"data":null,"error":null,"type":"result"}` rejected by `omp-yield-tool (YieldTool.execute)`. Same job `DigestObjectProbe` retried and was accepted, exit 0, structured output valid. 18/18.
- Lifecycle: `live-omp-probe.md:1029` run 2026-10-04T22:55:39Z, PASS 28/28 (earlier run at :829 retained unaltered). Real suite subrun `test-validate-digest.py` returned 0.

## Pool (Main's execution, `artifact://803`; I did not rerun)
Header count in the backing log: 120 `----- … (exit N` lines, 0 non-zero. `git ls-tree f9c9f1e2` shows 120 `test-*` files outside tests/manual, matching. 8 workers, 142.13s. `test-omp-hooks.py` exit 0; `test-validate-digest.py` exit 0 (71.11s) with 24/24 append, 81/81 BUG-1898, 37/37 T-04 undeclared-key, 24/24 SC-07 append lines visible in the log. The three new cases print `ok` in the pool log (lines 7221-7223). Deliberate caveat: Main's pool executed on the working tree before commit; the commit carries the same bytes of source/tests (no diff outside the 3 files and 8 feature paths, tree otherwise clean).

## Matrix (control-plane harness.json)
| kind | state | evidence |
|---|---|---|
| unit | satisfied | unit files in the 120 pool all exit 0 (test-digest-schemas, test-digest-record, test-digest-dev-skill, test-omp-hooks → bun) |
| integration | satisfied | test-validate-digest (incl. 24/24 append, 81/81, 37/37), test-plan-merge, test-check-state-feat59, others, all exit 0 |
| inflight_claim_lifecycle_live | locally_run, recorded | 28/28 at `live-omp-probe.md:1029` |
| digest_object_contract_live | locally_run, recorded | 18/18 live + 33/33 verify-receipt executed by me |
| functional, eval | not_applicable | excluded |

matrix_ok: true. The T-02 change sits in `validate-digest.py`, whose owning test `tests/integration/test-validate-digest.py` is the file with the new cases, and it is in the pool list; P-14 satisfied by header exit 0 for that file.

## Fail-first (per `verify: automated` SC)
Tier labels per O-03. Natural RED outranks constructed proof; none here is a present-state mutation proof except where stated.
- **SC-07 (new, append guard)**: natural RED. `append-visibility-rework.md:7` records `python3 tests/integration/test-validate-digest.py --only run_lead_append_cases` exit 1, 22/24; both unfinished-fence cases returned exit 0 and changed bytes, no production edit preceded. This is Main's actual execution; the raw log was not retained, only the note's lines. I did not rerun it. The cases themselves (`test-validate-digest.py:1586-1592`) assert exit 2 and `None` bytes-written for the open-fence forms, so red against the old `_append_record` is by construction: the old code wrote unconditionally after `last == obj`. GREEN 24/24 at `artifact://803` line 26 of the log.
- SC-07 historical (retained): `test-digest-record.py:74-115`, `test-plan-merge.py:2932`, `test-check-state-feat59.py:710,714` from `review-harness-qa-final.md` (natural RED, carried; source delta since is the append guard only, which is additive to the writer).
- SC-01: `omp-hooks.test.ts:1227,1259`. SC-02: `test-validate-digest.py:960,962`, `test-digest-dev-skill.py:106,119,155,158`. SC-03: `test-digest-schemas.py:169,181,223`. SC-04: `live-digest-object-probe-native-red.md/.json` (17/18 FAIL natural RED) plus current 18/18. SC-06: `test-validate-digest.py` and `-shadows`, with the retained baseline RED from the final note. All carried from `review-harness-qa-final.md`, not re-executed here; the source for those SCs is byte-identical at the pin.

## Adequacy judgement
- The guard's discriminating cases: `…:1586` (fence ```` ```text ```` unfinished, no prior record) and `…:1589` (unfinished ```` ```yaml ```` after an earlier record, the exact "correction hidden" scenario) both expect exit 2 and unchanged bytes. The third, closed prose fence, appends. They pin both open-fence legs (P-06). The mutant "guard removed" reddens both refusal cases, which is the retained RED. The mutant "guard always refuses" reddens the closed-fence case and the existing append cases.
- The guard evaluates the same `_last_record` the readers use over old bytes + the exact suffix, so it cannot diverge from durable-read selection (`validate-digest.py:1865`). I did not mutate the guard in a pin checkout; mutation arguments above are reasoning, not a run (assurance tier: natural RED + reasoning).
- Open quibble, non-blocking: `_last_record` is not a pure historical-reader import under test independence; both writer and guard share it, so a defect in `_last_record` would be self-consistent. The historical-reader tests in test-check-state-feat59 / test-plan-merge cover it independently.

## Findings (original severity/kind preserved)
- F1 — substance · low · qa · T-02: `harness-hooks.ts:1272` native-null branch has no CI-resident test; guarded only by the live probe + `--verify-receipt`. Unchanged.
- F2 — form · low · qa · T-02: prose enum legends have no drift guard to schema enums. Unchanged.
- Carried advisories, not converted: eleven accepted grade-2 costs (old-grader report: 241 units, 230 meeting bars, zero high; changed writer grade 4, cases grade 3, per Main's `code-risk-current.md`; I did not rerun the grader); low UI stale SubagentStop attribution. The earlier medium "unfinished fence hides appended mapping" is the finding this delta addresses; I record it as addressed by tests, and only my own evidence plus Main's actual execution has examined the fix. Independence of the four quality angles is Main's account, I did not audit it.

coverage_gaps: native-null CI guard (F1); enum legend drift (F2); Anthropic native proof absent (two STRINGnull 17/18 FAIL receipts preserved); `handoff_comprehension` live run (detect surface untouched).

## Open questions
- Q1 (non-blocking): `handoff_comprehension` detect surface is only `tests/manual/probe-handoff-comprehension.py` (`.harness/harness.json:306-311`), unchanged by this delta, so a live comprehension run is not required by detect. The broader `runner_note` advisory (run live before a handoff-contract ship decision) stands as the operator's call.
- Q2 (non-blocking): SC-04 native proof is OpenAI only.
- Q3 (non-blocking): the OLD digest gate rejects `locally_run`/`not_applicable` kind states in the terminal; the terminal carries only unit/integration and the other kinds are in the matrix table above and the `coverage_gaps` qualification.

## Form-only correction
Reconciled to the accepted terminal: terminal `kinds` restricted to unit/integration, other kinds qualified in `coverage_gaps`; SC-01 evidence path corrected to `tests/unit/omp-hooks.test.ts` (file exists there); Q1 resolved factually; Q3 added. No findings, verdict, severities or evidence limits changed; nothing re-executed.

## Principles applied
- harness-verification-rules: matrix from control-plane harness.json; pin binding by diff scoping, per-file sha256 from `git show` at the pin, and header-level exit counts; fail-first tiers labeled and not re-claimed as freshly run.

```yaml
VERDICT: PASS
DIGEST:
  headline: Append-visibility guard has natural RED22/24→GREEN24/24, pool 120/120 with 0 non-zero exits, all seven hashes and 33/33 receipt verified at the pin; floor met, advisories carried
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 tests/run-unit-tests.py --kind unit (Main pool artifact://803, 120 files exit 0)", named_tests: 46 }
    - { kind: integration, state: satisfied, cmd: "python3 tests/run-unit-tests.py --kind integration (Main pool artifact://803; test-validate-digest 24/24 append, 81/81, 37/37)", named_tests: 74 }
  coverage_gaps: [native-null CI guard at harness-hooks.ts:1272 (low), prose enum legend drift guard (low), Anthropic native proof absent, handoff_comprehension live run not required by detect surface, guard mutation proof not run in pin checkout, "locally_run kinds inflight_claim_lifecycle_live (28/28 at live-omp-probe.md:1029) and digest_object_contract_live (18/18 live + 33/33 verify-receipt executed by qa) are recorded, and functional/eval are not_applicable (excluded); all four are carried in the matrix table above, not in terminal kinds, because the OLD gate rejects those states"]
  sc_evidence:
    - { id: SC-01, test: "tests/unit/omp-hooks.test.ts:1227" }
    - { id: SC-02, test: "tests/integration/test-validate-digest.py:960" }
    - { id: SC-03, test: "tests/unit/test-digest-schemas.py:169" }
    - { id: SC-04, test: ".harness/harness/features/FEAT-1928-digest-object-contract/notes/live-digest-object-probe-current.md" }
    - { id: SC-06, test: "tests/integration/test-validate-digest.py" }
    - { id: SC-07, test: "tests/integration/test-validate-digest.py:1586" }
  fail_first:
    - { sc: SC-01, evidence: "omp-hooks.test.ts:1227,1259 natural RED carried from notes/review-harness-qa-final.md" }
    - { sc: SC-02, evidence: "test-validate-digest.py:960,962 and test-digest-dev-skill.py:106,119,155,158 natural RED carried from notes/review-harness-qa-final.md" }
    - { sc: SC-03, evidence: "test-digest-schemas.py:169,181,223 natural RED carried from notes/review-harness-qa-final.md" }
    - { sc: SC-04, evidence: "notes/live-digest-object-probe-native-red.md (17/18 FAIL natural RED)" }
    - { sc: SC-06, evidence: "test-validate-digest.py and -shadows retained baseline RED, notes/review-harness-qa-final.md; 291 fixtures, 14 approved deltas, 0 unplanned, untouched" }
    - { sc: SC-07, evidence: "notes/append-visibility-rework.md:7 actual RED 22/24 before guard (no production edit preceded); historical consumer RED test-digest-record.py:74-115, test-plan-merge.py:2932, test-check-state-feat59.py:710,714" }
  open_questions:
    - { id: Q1, question: "handoff_comprehension detect surface is only tests/manual/probe-handoff-comprehension.py (harness.json:306-311), unchanged by this delta; live comprehension run not required by detect. Broader runner_note advisory (run before a handoff-contract ship decision) stands as operator's call", blocking: false }
    - { id: Q2, question: "SC-04 native proof is OpenAI-only; Anthropic string-null failures 17/18 stand", blocking: false }
    - { id: Q3, question: "OLD digest gate rejects locally_run/not_applicable kind states in this terminal; they are carried in the prose matrix and coverage_gaps qualification only", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-1928-digest-object-contract/notes/review-harness-qa-append.md
```
