# BUG-2171 goal-check — PASS

All four SCs are met by inspected evidence; both declared perspectives pass. No smoke, test, build, lint or formatter was rerun. Read-only computations compared saved schemas/records and immutable source. T-01 is main-session-direct; findings route to Main, not a dev.

Pin: d3792019e74ff266c2414708124512544d1fc9f6. Base: b7af829c0207522b43f978b5275a2ebdc96b3210. F denotes this feature directory.

## Perspective coverage

- **operator — pass:** SC-01 pins the native opt-in and copy-warning; SC-03 establishes fresh main → product lead → PM returns and automatic append, not merely final record presence. Evidence below.
- **code maintainer — pass:** SC-02 and SC-04 have named historical assertion failures and fixed passes, boolean identity enforcement, equivalent object/string validation, invalid-string refusal and held-run coverage. Evidence below.

## SC outcomes

- **SC-01 — met, inspection:** immutable git diff base→pin of .omp/extensions/harness-hooks.ts contains exactly one added concatenated refusal-text source line and the yield-local variable/JSON.parse changes; dispatch, injection, lifecycle and append have no diff. .omp/config.yml adds structured: true while retaining maxRecursionDepth: 3/maxRuntimeMs: 0. check-omp-port.py changes only the boolean-identity predicate and diagnostic. These are the approved T-01 surfaces.
- **SC-02 — met, automated evidence inspection:** tests/integration/test-check-omp-port.py case_task_structured_required; F/notes/receipts/red-port.txt:14-17 shows three actual failed assertions and the true control passing. green-offline.txt:14-17,32 shows fixed acceptance/rejection; :2284-2285 binds the very same named assertions to immutable historical gate b7af829c and fixed gate. Integer 1 is an additional pin assertion, not part of the older 30/30 receipt; QA owns its current gate execution. Production uses is not True, so integer equality cannot grant acceptance.
- **SC-03 — met, inspection:** actual saved sessions, calls, write payloads, runtime persistence mechanism and canonical selection inspected independently, detailed below. Execution was at d1e203d4758ce6d6aed075a8f092af0bb064a45c, not re-executed at the pin. git diff executed SHA→pin across .omp, Harness bin/templates, tests and Harness/team configuration shows only the integration test's added integer-1 row. Hooks, validator, schemas, agents, configuration, bundle projection and probe behavior are unchanged; this supports transfer of the live evidence, not a claim of pin execution.
- **SC-04 — met, automated evidence inspection:** pinned tests/unit/omp-hooks.test.ts real tool_call handler regression “BUG-2171 string-serialized PASS digest is validated as the object it encodes” asserts exactly one validator call, deep-equal digest_object, and object/string verdict equality. Adjacent invalid-string test covers malformed JSON, null, array and string primitive with zero validator calls; original object-data test remains. Held-run test refuses string PASS without validation and validates parsed string BLOCKED. red-hook.txt:9-33 records actual pre-fix refusal assertions. green-offline.txt:2288-2318 replays the immutable historical hook: expected validator count 1, received 0, followed by fixed 1 pass/0 fail. Full handler suite is 140 pass/0 fail (:33-38 and :2259-2265), covering held/invalid branches too.

## SC-03 writer and injection proof

Session directory S = /Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-BUG-2171-task-structured/2026-11-21T15-51-23-264Z_01a1fece-1d80-71ed-bc1b-55ec6796029b.

Main is S.jsonl; lead is S/SmokeProductLead.jsonl; PM is S/SmokeProductLead/SmokeProductLead.SexualRoundworm.jsonl. Session metadata gives distinct fresh IDs/times, assigned worktree cwd and actual parent-session links. Lead/PM session_init declares runtime 19.1.0, strict schema and yield among tools. Real credentialled model turns successfully complete both levels; no missing-auth or timeout substitute is used. Launcher/version/hash are recorded in live-smoke-identity.txt:1-4.

Main task toolu_017jyU7iLFbtk2ADZeDywNWH and lead task call_95da35eeaec947ddbe33db6ffe0c5909 both complete without task refusal. Independently computed deep equality: their persisted outputSchema equals loadDigestSchemaBundle for harness-product-lead/harness-pm respectively, schemaMode strict. This equality alone would NOT establish injection. Installed OMP agent-session.ts:5638-5660 forwards extension input revisions as args; pi-agent-core/src/agent-loop.ts:3155-3163 actually overwrites toolCall.arguments before persistence. Product hook schemaControlRefusal runs before withDigestSchemas/claim at harness-hooks.ts:1219 onward. Thus caller-supplied fields would refuse; successful calls plus actual strict child initialization discriminate hook injection from stripped fields. The narrator's “I explicitly sent fields” in live-smoke.txt:3 misreads revised persisted arguments, not raw provider input.

Actual PM yield call_2c282581bee44fd2bfa49c60e6dd44fa and lead yield call_8a582d7cccc747d6aea21007f8ea45c5 have successful tool results. PM only reads then yields. Lead writes identical fence-free human text to before.md and digest.md, then yields; it issues no shell/validator invocation. Main's full tool sequence contains no manual append/standalone validator. Its later shell reads/checks/closes the run only. These tool payloads distinguish the writer from simply observing a fence later.

Read-only byte comparison found the entire 678-byte before.md preserved as digest.md prefix, with no fence in before.md. canonical digest_record.last_fenced_mapping selects PASS with exactly VERDICT/DIGEST/artifact; its object deep-equals the lead's actual yield data and artifact resolves to this run's digest.md. Existing hook validate-digest.py --hook call with digest_object and unchanged validator-owned append explain the added fence; no agent write contains it.

## Findings and honest limits

- **Form, low, T-01/SC-03:** live-smoke.txt:3 inaccurately concludes this only proves an explicit-schema path. Concrete consequence: a successor trusting the narrator may unnecessarily rerun/overwrite proof despite successful hook injection. Preserve the historical receipt; this independent assessment supersedes that interpretation. Not a product failure.
- No substance or proportionality finding. No personal UAT: BRIEF has none. Null typecheck remains the signed disclosure, not a green claim. Integer-1 execution at the final pin belongs to QA. This goal-check inspects receipts, not substitutes for QA's matrix verdict. Open questions: none.
