# QA gate (final newest-main merge) — FEAT-1928, pin 232685fb — VERDICT: PASS

**BLUF.** Floor met at the pin. `feature.json` `review_sha` = `232685fb…` (pin supplied; I did not infer it from HEAD, though HEAD also equals it). The clean-executed `7e2e6713` → `232685fb` delta is six feature metadata paths and no source, test, config, schema or probe path. The authorized receipt verifier I executed now: **33/33, exit 0**. I ran no suite, no bun, no live probe, no authoring. Pool, native 18/18, lifecycle 28/28, verifier 33/33 (Main) are Main/retained executions, labeled below.

## Phase 1 (BRIEF + plan.yaml + control-plane harness.json; before source)
Unchanged from `review-harness-qa-append.md`. T-01 `api` → unit. T-02, T-04 `cross_module` → unit + integration. T-03, T-05 `docs` → none. Locally-run kinds `inflight_claim_lifecycle_live`, `digest_object_contract_live`; `functional`, `eval` excluded. Expectation for this delta: a merge may not move any under-test byte, the SC-07 writer guard and refusal/closing-retry proof survive, and `digestBinding` stays independent of `featureRootCache` under cold revival. A merge with no source delta needs no new test.

## Current measurements (mine, this run)
- **Pin**: `feature.json:review_sha` = `232685fb902a32795e169895fcf3c9fd154a7991`; `git rev-parse 232685fb` agrees. `ee6898b8` is an ancestor of the pin. Working tree: only `feature.json` modified (Main-owned ledger).
- **Clean 7e2e→pin delta**: `git diff --stat 7e2e671304cd… 232685fb…` = exactly `STATE.md`, `feature.json`, `notes/code-risk-current.md`, `notes/live-digest-object-probe-current.md`, its `.transcript.jsonl`, `notes/live-omp-probe.md`. Six paths, all metadata and evidence. Zero under `tests/ .omp/ .claude/ .agents/`.
- **Writer guard intact**: `git diff 3c1923cf 232685fb` over `validate-digest.py`, `test-validate-digest.py`, `digest_schema.py`, `digest-schemas/`, `digest-schema.ts` and `tests/manual/` lists only `validate-digest.py` and `test-validate-digest.py`, the already-accepted append guard and its three cases. `receipt-scripts/` and `validator-parity.md` have zero diff vs 3c1923cf.
- **Fixtures**: 291 `parity-fixtures/P*.json` tracked at the pin. The 291 / exact-14 approved / 277 unchanged / zero null-or-unplanned derivation stands because fixtures, generator scripts and parity doc are unchanged. Not regenerated, waived or subsetted.
- **Receipt**: `python3 tests/manual/probe-digest-object-contract.py --verify-receipt …/notes/live-digest-object-probe-current.md` (cwd sourceRoot) → every line PASS, "receipt verification 33/33", **exit 0**. It includes: clean tree, every file under test byte-identical to the recorded commit, launcher byte-identical, version matches launcher, ids/model match the transcript.
- **Transcript**: sha256 `ba1fcf4179323573037b1c2e1373f1f090a22dcd1a5387fb70f8defdc6d2fe29`, 43 records. I recomputed it and it equals the receipt.
- **Under-test subjects at the pin** (`git show 232685fb:<path>`): common.json `004ec08b…`, harness-documentor.json `7917570a…`, digest_schema.py `d44b6b2e…`, validate-digest.py `ee10a77d…`, digest-schema.ts `0ed3f181…`, harness-hooks.ts `7dc70535…`, probe `d5769a3a…`. The first six hashes equal the receipt-era values and the verifier confirmed all seven byte-identical. `harness-hooks.ts` changed from the f9 value `456c9af7…` by the upstream cold-revival merge, which the receipt's HEAD `7e2e6713` already contained. The six-path delta cannot move it.
- **Receipt contents**: OMP `omp/18.6.1`, launcher sha256 `348d0987…041a`, source `2a2c6dcb…` labeled release-tag metadata (distinct from binary identity). Harness HEAD `7e2e6713` + 0 uncommitted. OpenAI Main `gpt-5.6-terra`, child `gpt-5.6-sol:medium`. Null yield `{"data":null,"error":null,"type":"result"}` rejected by `omp-yield-tool (YieldTool.execute)`; the same job `DigestObjectProbe` retried, valid object accepted, exit 0, 18/18.
- **Lifecycle**: `live-omp-probe.md` at the pin carries a new run block (`Verdict: PASS (28/28 checks)`, line 1231 at the pin); the earlier block at line 1031 is retained unaltered. The run's suite subrun `test-validate-digest.py` returned 0 (37/37 T-04 line).
- **Pool**: backing log of `artifact://891`: 120 `----- test-… (exit N` header lines, 0 non-zero, 120 `exit 0`; footer `pool: 8 workers, 120 files, 160.70s wall`. `git ls-tree 232685fb` shows 120 `test-*` files outside `tests/manual`, matching. `test-validate-digest.py` exit 0 (61.65s), `test-omp-hooks.py` exit 0, `test-feature-record.py` exit 0, `test-prune-run-evidence.py` exit 0. I counted the log; I did not rerun the pool.

## Retained evidence vs Main executions (not mine)
- **Main executions**: pool 120/120 (`artifact://891`), native 18/18, verifier 33/33 and lifecycle 28/28 after the merge, prune permanent suite, real canonical CLI `--dry-run`, and the corrected canonical-reader audit/selftest PASS. The initial audit failure on six duplicate classification identities is historical and stays recorded.
- **Retained**: both Anthropic STRINGnull 17/18 FAIL receipts (`live-digest-object-probe-null-string-fail*.md`) and `live-digest-object-probe-native-red.md`. Native proof is OpenAI-only.
- **Not executed anywhere here**: the bun half of the T-05 verify (four OMP provider suites in `/Users/molchairuangutai/GitHub/oh-my-pi`). I did not run it; the prior accepted result (111 pass / 0 fail / 221 expects) is carried as prior evidence and tests OMP source this merge did not touch. I ran only the authorized receipt half of the T-05 verify.
- **Independence/lifetime interactions** (source reads of `simplify-finalmerge-eng/digest.md` against `newest-main-integration.md`; I did not re-read the source and ran nothing). `digestBinding` and `featureRootCache` remain separate caches. Cold revival takes identity from `session_init` and reclaims through `openRun`, while native yield forwards the object plus trusted binding. Upstream's cold-revival `adoptPersistedRun` runs only when the instance has no runtime id and only sets persona/feature/pin/mission, so it does not touch the strict object dispatch or append authorization. Main's all-cold-revival hook groups and the schema-refusal/no-claim groups ran green in the 120/120 pool. These rest on source observation by the simplify angles plus Main's execution; I did not independently run a cold-revival case.
- **Integration conflicts**: Five conflicts resolved (prune refusal/helper + distill retention, stronger same-bug duplicate-key test, schema refusal/no-claim + cold revival groups, regenerated decision index with DEC-237, six duplicate classification identities removed). I did not audit those 61 upstream files; the pool and the canonical audit execution are Main's. My bounded read: the merge changed no under-test file, and no test was removed or weakened in the files the feature owns (`git diff 3c1923cf..232685fb` over the feature's test files = the append guard only).

## Matrix (control-plane harness.json) — full durable matrix
| kind | state | evidence |
|---|---|---|
| unit | satisfied | unit files of the 120 pool exit 0 (Main `artifact://891`): test-digest-schemas, test-digest-record, test-digest-dev-skill, test-omp-hooks → bun |
| integration | satisfied | test-validate-digest (exit 0), test-plan-merge, test-check-state-feat59, test-feature-record, others all exit 0 |
| inflight_claim_lifecycle_live | locally_run, recorded | 28/28 at `live-omp-probe.md` pin line 1231; detect surface untouched by the six-path delta |
| digest_object_contract_live | locally_run, recorded | 18/18 live receipt + 33/33 `--verify-receipt` executed by me now |
| functional, eval | not_applicable | excluded |

`matrix_ok: true`. The legacy terminal below carries only `unit` and `integration`, because the OLD gate rejects `locally_run`/`not_applicable` terminal states (Q3). This is a terminal-form limit; it does not claim that CI ran the locally_run kinds, and it does not claim CI ran at all: unit/integration were executed by Main locally through `run-unit-tests.py`.

## Fail-first (per `verify: automated` SC; original durable evidence, none newly invented)
- SC-01: `omp-hooks.test.ts:1227,1259` natural RED, `review-harness-qa-final.md`.
- SC-02: `test-validate-digest.py:960,962`; `test-digest-dev-skill.py:106,119,155,158` natural RED, `review-harness-qa-final.md`.
- SC-03: `test-digest-schemas.py:169,181,223` natural RED, `review-harness-qa-final.md`.
- SC-04: `live-digest-object-probe-native-red.md` (17/18 FAIL natural RED); the two STRINGnull 17/18 failures also retained.
- SC-06: retained baseline RED in `review-harness-qa-final.md`; 291 fixtures, 14 approved, 0 unplanned, untouched.
- SC-07: `append-visibility-rework.md:7` actual RED 22/24 before the guard (no production edit preceded); GREEN 24/24; historical consumer RED `test-digest-record.py:74-115`, `test-plan-merge.py:2932`, `test-check-state-feat59.py:710,714`.
- Tier label (O-03): natural RED; no present-state mutation proof newly run. The SC-07 raw log was not retained, only the note's lines. Source for these SCs is byte-identical at the pin, so the carry is sound.

## Adequacy / SC-07 closure
I find no regression. SC-07 stays closed: guard (`_append_record` applying `_last_record` to old bytes + exact suffix before write) is unchanged by the merge; three `_append_rule_cases` bind two open-fence refusal legs and the closed-fence append (P-06); the Main pool ran them. I did not mutate the guard in a pin checkout (assurance: natural RED + reasoning). Shared-`_last_record` self-consistency quibble from the append gate stands as non-blocking.

## Findings (original severity/kind preserved; nothing converted)
- F1 — substance · low · qa · T-02: native-null branch (`harness-hooks.ts`) has no CI-resident test; guarded only by live probe + `--verify-receipt`. Unchanged.
- F2 — form · low · qa · T-02: prose enum legends lack a drift guard to schema enums. Unchanged.
- Carried: eleven accepted grade-2 costs (merge grading: 240 gated functions, 229 meeting bars, zero high; Main's `code-risk-current.md`, I did not rerun the grader); low stale SubagentStop attribution (UI); outside-feature `handoff_comprehension` runner_note and deviceURI routing advisories; prior QA local-kind rerun mismatch outside the feature remains advisory. UI: browser-guidance proof and PNG hashes retained, org source unchanged; no full accessibility/UAT claim.
- Simplify S1 (duplicate `artifact_accessors` import) was fixed by Main per `newest-main-integration.md`; I did not inspect the fix.

## Coverage limits
bun provider suites not run by me; no independent cold-revival execution; no pin-checkout guard mutation; Anthropic native proof absent; no fresh source-pinned audit of the 61 upstream files.

## Open questions
- Q1 (non-blocking): `handoff_comprehension` live run is not required by the detect surface; the runner_note stays with the operator.
- Q2 (non-blocking): SC-04 native proof is OpenAI-only; Anthropic STRINGnull 17/18 FAIL receipts stand.
- Q3 (non-blocking): OLD gate rejects locally_run/not_applicable terminal states; they live in the matrix table and coverage_gaps only.

## Principles applied
- harness-verification-rules: matrix from the control-plane harness.json; delta binding by diffs scoped to under-test paths and clean/pin SHAs; log census by header exit counts; current, retained and Main-executed evidence labeled separately; fail-first tiers not re-claimed as freshly run.

```yaml
VERDICT: PASS
DIGEST:
  headline: Merge to 232685fb moves no source, test, config, schema or probe byte versus the clean 7e2e executed tree; receipt verifier 33/33 exit 0 now, pool 120/120 exit 0 census confirmed, all eight SCs and SC-07 closure stand
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 tests/run-unit-tests.py --kind unit (Main pool artifact://891, 120 files exit 0, local; qa did not rerun)", named_tests: 46 }
    - { kind: integration, state: satisfied, cmd: "python3 tests/run-unit-tests.py --kind integration (Main pool artifact://891; test-validate-digest exit 0; local; qa did not rerun)", named_tests: 74 }
  coverage_gaps: [native-null CI guard at harness-hooks.ts (low), prose enum legend drift guard (low), Anthropic native proof absent, "bun provider suites of T-05 verify not run by qa (retained prior 111/0/221 only)", cold-revival interaction judged from Main's pool and source reads not independently executed, guard mutation proof not run in pin checkout, handoff_comprehension live run not required by detect surface, "locally_run kinds inflight_claim_lifecycle_live (28/28 live-omp-probe.md) and digest_object_contract_live (18/18 live + 33/33 verify-receipt executed by qa now) are recorded and functional/eval are not_applicable (excluded); carried in the matrix table not terminal kinds because the OLD gate rejects those states; no CI execution is claimed"]
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
    - { sc: SC-04, evidence: "notes/live-digest-object-probe-native-red.md (17/18 FAIL natural RED); notes/live-digest-object-probe-null-string-fail.md and -fail2.md retained" }
    - { sc: SC-06, evidence: "retained baseline RED in notes/review-harness-qa-final.md; 291 fixtures, 14 approved, 277 unchanged, 0 unplanned, untouched" }
    - { sc: SC-07, evidence: "notes/append-visibility-rework.md:7 actual RED 22/24 before guard (no production edit preceded); historical consumer RED test-digest-record.py:74-115, test-plan-merge.py:2932, test-check-state-feat59.py:710,714" }
  open_questions:
    - { id: Q1, question: "handoff_comprehension detect surface is only tests/manual/probe-handoff-comprehension.py, unchanged; live comprehension run not required by detect. Broader runner_note advisory stands as operator's call", blocking: false }
    - { id: Q2, question: "SC-04 native proof is OpenAI-only; Anthropic string-null failures 17/18 stand", blocking: false }
    - { id: Q3, question: "OLD digest gate rejects locally_run/not_applicable kind states in this terminal; they are carried in the prose matrix and coverage_gaps qualification only", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/notes/review-harness-qa-finalmerge.md
```
