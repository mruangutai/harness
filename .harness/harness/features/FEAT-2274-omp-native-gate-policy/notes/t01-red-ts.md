# T-01 RED/GREEN evidence — TypeScript adapter slice (C3 + C4)

Owned files: `.omp/extensions/harness-hooks.ts`, `tests/unit/omp-hooks.test.ts`.

## RED — new assertions against the baseline adapter

Baseline: `.omp/extensions/harness-hooks.ts` byte-identical to 1e0b014917125bc9aae1f30a2f6fd53ed239f3bc
(`git diff --stat -- .omp/extensions/harness-hooks.ts` printed nothing); only the test file carried
the new cases. The new exports are read through a namespace import (`import * as hooks`), so a missing
export fails its own cases instead of failing the module link.

Command (from the worktree): `python3 tests/unit/test-omp-hooks.py` → exit 1

```
(fail) OMP task lifecycle adapter > FEAT-2274: an unavailable check-domain lets the write proceed and says so, pre and post [3.01ms]
(fail) OMP task lifecycle adapter > FEAT-2274: every unavailable invocation is reported again; nothing is cached for the session [0.48ms]
(fail) OMP task lifecycle adapter > FEAT-2274: several unavailable invocations on one call each keep their notice [0.27ms]
(fail) OMP task lifecycle adapter > FEAT-2274: an explicit deny stays a refusal and a normal pass stays silent beside an unavailable gate [0.29ms]
(fail) OMP task lifecycle adapter > FEAT-2274: an ast_edit post notice leaves the tool's own content to the host, never an error [0.17ms]
(fail) OMP task lifecycle adapter > FEAT-2274: an unavailable bash-write-guard keeps the HARNESS_AGENT_TYPE env revision beside its notice [0.19ms]
(fail) OMP task lifecycle adapter > FEAT-2274: a governed Bash post sweep that could not run is reported as post [0.14ms]
(fail) OMP task lifecycle adapter > FEAT-2274: BUG-1016 rooting keeps its revised input beside the notice [0.16ms]
(fail) OMP task lifecycle adapter > FEAT-2274: an unavailable dispatch-guard keeps the schema injection and its note, one notice per target [2.39ms]
(fail) OMP task lifecycle adapter > FEAT-2274: an unavailable digest validator lets the yield through and says so; a refusal still blocks [0.44ms]
(fail) OMP task lifecycle adapter > FEAT-2274: before_subagent_spawn refuses a harness target outside task, for Main and governed parents alike [0.84ms]
(fail) classifyPolicyRun > a declared unavailable line is unavailable, naming the gate, and not a block [0.38ms]
(fail) classifyPolicyRun > a broad gate's structured deny and exit 2 stay refusals; a normal pass carries no notice [0.13ms]
(fail) classifyPolicyRun > a broad gate that crashed, was killed, or never started is unavailable, never a block [0.17ms]
(fail) classifyPolicyRun > a narrow gate that could not run refuses a command it guards and allows any other silently [0.24ms]
(fail) classifyPolicyRun > every other script keeps its non-blocking error contract and still throws a spawn error [0.13ms]
(fail) narrowGateApplies > gh-close-gate.py: every protected spelling matches and every unrelated command does not [0.09ms]
(fail) narrowGateApplies > branch-create-gate.py: every protected spelling matches and every unrelated command does not [0.07ms]
(fail) narrowGateApplies > plan-sign-gate.py: every protected spelling matches and every unrelated command does not [0.06ms]
(fail) narrowGateApplies > a script that is not a narrow gate guards nothing [0.06ms]
 159 pass
 20 fail
Ran 179 tests across 1 file. [19.71s]
```

Representative failure bodies:

```
2158 |   test("FEAT-2274: an unavailable check-domain lets the write proceed and says so, pre and post", async () => {
2159 |     const { handlers } = unavailableAt(["check-domain.py"]);
2160 |     await start(handlers);
2161 |     const event = fileCall("write", { path: "/repo/src/a.ts", content: "x" });
2162 |     const pre = await handlers.get("tool_call")?.(event, leadCtx());
2163 |     expect(pre).toEqual({ additionalContext: notice("check-domain", "pre") });
                       ^
error: expect(received).toEqual(expected)

- {
-   "additionalContext": "Harness: check-domain (pre) could not run; nothing was checked. crashed (RuntimeError: boom)",
- }
+ undefined

- Expected  - 3
+ Received  + 1

2312 |     await start(governed.handlers);
2313 |     for (const { handlers } of [unstarted, main, governed]) {
2314 |       const refused = await spawn(handlers, { agent: "harness-backend-dev", invocationKind: "eval" });
2315 |       expect(refused).toEqual({ block: true, reason: expect.stringContaining("task tool") });
                             ^
error: expect(received).toEqual(expected)

- {
-   "block": true,
-   "reason": StringContaining "task tool",
- }
+ undefined

- Expected  - 4
+ Received  + 1

      at <anonymous> (/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2274-omp-native-gate-policy/tests/unit/omp-hooks.test.ts:2315:23)
(fail) OMP task lifecycle adapter > FEAT-2274: before_subagent_spawn refuses a harness target outside task, for Main and governed parents alike [0.84ms]
2352 | 
TypeError: hooks.classifyPolicyRun is not a function. (In 'hooks.classifyPolicyRun(script, payload, proc)', 'hooks.classifyPolicyRun' is undefined)
TypeError: hooks.classifyPolicyRun is not a function. (In 'hooks.classifyPolicyRun(script, payload, proc)', 'hooks.classifyPolicyRun' is undefined)
TypeError: hooks.narrowGateApplies is not a function. (In 'hooks.narrowGateApplies(script, command)', 'hooks.narrowGateApplies' is undefined)
```

Every pre-existing case (159) passed at baseline; all 20 failures are the new FEAT-2274 cases.

## GREEN — after the adapter change

Command (from the worktree): `python3 tests/unit/test-omp-hooks.py` → exit 0

```
 179 pass
 0 fail
Ran 179 tests across 1 file. [14.26s]
```

All 20 cases that failed at baseline pass; the 159 pre-existing cases still pass.

## Classifier agreement (scratch check, not a committed test)

`narrowGateApplies` was run against the baseline Python matchers taken verbatim from
1e0b014 (gh-close-gate `denies`, plan-sign-gate `denies`, branch-create-gate `_branch_name`) over
~90,000 generated commands (quote, operator, substitution, continuation, `${IFS}`, xargs/find,
comment, unlexable and git branch-creation spellings). Mismatches: gh-close 0, plan-sign 0,
branch-create 0. The committed evidence is the spelling table in `omp-hooks.test.ts`
(`narrowGateApplies` describe) and Main's runtime suite over the gates' APPLICABILITY_CORPUS.
